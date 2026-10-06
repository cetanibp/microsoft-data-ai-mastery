"""Prepare Azure Search request bodies locally; never connects to Azure."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from prepare_corpus import CorpusError, canonical, contained, prepare

VERSION = "0.1.0"
AI_ROOT = "04-foundry-ai-engineering/AI-001"
STRATEGIES = {"sections": "markdown_section", "windows": "fixed_window"}
FLAGS = ("runtime_eligible", "authorization_verified", "current_freshness_verified")


def project(chunk, fields, strategy):
    if chunk["chunking"]["strategy"] != strategy:
        raise CorpusError("Strategy mismatch")
    if chunk["classification"] != "synthetic_lab_documentation":
        raise CorpusError("Synthetic lab content required")
    if chunk["mode"] != "offline_draft_study" or any(chunk[f] is not False for f in FLAGS):
        raise CorpusError("Draft flags must remain false")
    record = {k: v for k, v in chunk.items() if k not in ("chunking", "source_sections")}
    record.update(
        chunk_strategy=strategy,
        chunking_json=canonical(chunk["chunking"]),
        source_sections_json=canonical(chunk["source_sections"]),
        section_names=list(dict.fromkeys(s["section"] for s in chunk["source_sections"])),
    )
    if set(record) != {f["name"] for f in fields}:
        raise CorpusError("Projection does not match schema fields")
    for field in fields:
        value = record[field["name"]]
        kind = field["type"]
        valid = (
            (kind == "Edm.String" and isinstance(value, str))
            or (kind == "Edm.Boolean" and type(value) is bool)
            or (kind == "Edm.Int64" and type(value) is int and -(2**63) <= value < 2**63)
            or (kind == "Collection(Edm.String)" and isinstance(value, list)
                and all(isinstance(item, str) for item in value))
        )
        if not valid:
            raise CorpusError("Field type mismatch")
    return {"@search.action": "upload", **record}


def build(repo_root, allow_draft_local=False):
    root = Path(repo_root).resolve()
    # Regenerate from hash-verified sources rather than trusting editable JSONL.
    chunks, corpus_summary = prepare(root, allow_draft_local)
    payloads = {}
    summary = {
        "projection_version": VERSION, "evidence_level": "local_only",
        "network_requests": 0, "cloud_upload_performed": False,
        "manifest_sha256": corpus_summary["manifest_sha256"],
        "source_blob_verification": corpus_summary["source_blob_verification"],
        "runtime_eligible": False, "indexes": {},
    }
    for label, strategy in STRATEGIES.items():
        schema_raw = contained(root, AI_ROOT + "/azure-search/" + label + ".index.json").read_bytes()
        schema = json.loads(schema_raw)
        if schema["name"] != "northstar-ops-" + label + "-v1":
            raise CorpusError("Unexpected lab index name")
        records = [project(c, schema["fields"], strategy) for c in chunks[strategy]]
        keys = [r["chunk_id"] for r in records]
        if len(set(keys)) != len(keys) or not records or len(records) > 1000:
            raise CorpusError("Invalid batch count or duplicate keys")
        body = canonical({"value": records}) + "\n"
        data = body.encode("utf-8")
        if len(data) >= 16 * 1024 * 1024:
            raise CorpusError("Batch too large")
        payloads[label + ".upload.json"] = body
        summary["indexes"][schema["name"]] = {
            "document_count": len(records), "payload_bytes": len(data),
            "payload_sha256": hashlib.sha256(data).hexdigest(),
            "schema_sha256": hashlib.sha256(schema_raw).hexdigest(),
            "strategy": strategy,
        }
    return payloads, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--allow-draft-local", action="store_true")
    args = parser.parse_args()
    try:
        payloads, summary = build(args.repo_root, args.allow_draft_local)
        target = contained(Path(args.repo_root).resolve(), AI_ROOT + "/generated/azure-search")
        # Exclusive directory creation avoids overwriting an earlier batch or following a symlink.
        target.mkdir(parents=True, exist_ok=False)
        for name, body in payloads.items():
            (target / name).write_text(body, encoding="utf-8", newline="\n")
        (target / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2))
    except (CorpusError, OSError, UnicodeError, KeyError, TypeError, ValueError):
        parser.exit(2, "Upload preparation failed; check source hashes, draft flag, schemas and output directory.\n")


if __name__ == "__main__":
    main()
