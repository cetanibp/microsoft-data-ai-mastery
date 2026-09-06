"""Offline Northstar corpus loading and chunk preparation. Python stdlib only."""
import argparse
import hashlib
import json
import re
from pathlib import Path

VERSION = "0.1.0"
MANIFEST = "06-ai-ready-data/DATA-001/corpus-manifest.json"
HEX40 = re.compile(r"[0-9a-f]{40}")


class CorpusError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def contained(root, relative):
    if not isinstance(relative, str) or "\\" in relative:
        raise CorpusError("Invalid relative source path")
    p = Path(relative)
    if p.is_absolute() or ".." in p.parts:
        raise CorpusError("Source path escapes repository")
    resolved = (root / p).resolve()
    if not resolved.is_relative_to(root):
        raise CorpusError("Source symlink escapes repository")
    return resolved


def load_documents(repo_root, allow_draft_local=False):
    root = Path(repo_root).resolve()
    raw = contained(root, MANIFEST).read_bytes()
    manifest = json.loads(raw)
    if manifest.get("schema_version") != VERSION:
        raise CorpusError("Unsupported manifest schema")
    # This program deliberately has no production-serving or approval mode.
    if manifest.get("status") != "draft" or not allow_draft_local:
        raise CorpusError("This loader requires a draft manifest and --allow-draft-local")
    if manifest.get("runtime_ready") is not False:
        raise CorpusError("Local study requires runtime_ready=false")
    policy = manifest["default_policy"]
    if policy["classification"] != "synthetic_lab_documentation":
        raise CorpusError("Local study accepts synthetic lab documentation only")
    docs = manifest["documents"]
    if not docs:
        raise CorpusError("Empty document selection")
    seen = set()
    loaded = []
    for doc in docs:
        key = doc["document_id"]
        if not isinstance(key, str) or not key or key in seen:
            raise CorpusError("Invalid or duplicate document ID")
        seen.add(key)
        if doc["inherits_policy"] != "default_policy":
            raise CorpusError("Unknown inherited policy")
        if doc["content_type"] != "text/markdown":
            raise CorpusError("Unsupported content type")
        if not HEX40.fullmatch(doc["source_commit"]) or not HEX40.fullmatch(doc["source_blob_sha"]):
            raise CorpusError("Invalid source revision")
        expected_url = (
            "https://github.com/" + manifest["repository"] + "/blob/"
            + doc["source_commit"] + "/" + doc["source_path"]
        )
        if doc["source_url"] != expected_url:
            raise CorpusError("Citation URL does not match pinned source")
        data = contained(root, doc["source_path"]).read_bytes()
        if git_blob_sha(data) != doc["source_blob_sha"]:
            raise CorpusError("Source hash mismatch: " + key)
        text = data.decode("utf-8")
        if not text.strip():
            raise CorpusError("Empty source")
        loaded.append((doc, text))
    return manifest, hashlib.sha256(raw).hexdigest(), loaded


def markdown_sections(text):
    """ATX headings outside fenced code; offsets are Unicode character positions."""
    sections = []
    stack = []
    start = 0
    offset = 0
    fence_char, fence_len = None, 0
    for line in text.splitlines(keepends=True):
        if fence_char:
            closing = re.match(r"^ {0,3}(" + re.escape(fence_char) + r"+)\s*$", line)
            if closing and len(closing.group(1)) >= fence_len:
                fence_char = None
            offset += len(line)
            continue
        opening = re.match(r"^ {0,3}(" + chr(96) + r"{3,}|~{3,})(.*)$", line)
        if opening:
            fence_char, fence_len = opening.group(1)[0], len(opening.group(1))
            offset += len(line)
            continue
        heading = re.match(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*\r?\n?$", line)
        if heading:
            if offset > start:
                sections.append({"start": start, "end": offset, "path": [v for _, v in stack]})
            level = len(heading.group(1))
            title = re.sub(r"[ \t]+#+[ \t]*$", "", heading.group(2)).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            start = offset
        offset += len(line)
    if len(text) > start:
        sections.append({"start": start, "end": len(text), "path": [v for _, v in stack]})
    return sections


def fixed_ranges(text, size=800, overlap=120):
    if size <= 0 or overlap < 0 or overlap >= size:
        raise CorpusError("Require size > 0 and 0 <= overlap < size")
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        yield start, end
        if end == len(text):
            break
        start = end - overlap


def make_chunks(manifest, manifest_hash, loaded, strategy, size=800, overlap=120):
    if strategy not in ("markdown_section", "fixed_window"):
        raise CorpusError("Unknown strategy")
    if size <= 0 or overlap < 0 or overlap >= size:
        raise CorpusError("Invalid size/overlap")
    chunks = []
    config = {"version": VERSION, "strategy": strategy}
    if strategy == "fixed_window":
        config.update(size_characters=size, overlap_characters=overlap)
    for doc, text in loaded:
        sections = markdown_sections(text)
        ranges = (
            [(s["start"], s["end"]) for s in sections]
            if strategy == "markdown_section" else list(fixed_ranges(text, size, overlap))
        )
        for start, end in ranges:
            spans = [
                {"section": s["path"][-1] if s["path"] else "(preamble)",
                 "section_path": s["path"], "start": max(start, s["start"]),
                 "end": min(end, s["end"])}
                for s in sections if s["start"] < end and s["end"] > start
            ]
            identity = [manifest_hash, doc["document_id"], doc["source_commit"],
                        doc["source_blob_sha"], config, start, end]
            chunks.append({
                "chunk_id": hashlib.sha256(canonical(identity).encode()).hexdigest(),
                "corpus_id": manifest["corpus_id"],
                "corpus_version": manifest["corpus_version"],
                "manifest_sha256": manifest_hash,
                "document_id": doc["document_id"], "title": doc["title"],
                "source_path": doc["source_path"], "source_url": doc["source_url"],
                "source_commit": doc["source_commit"], "source_blob_sha": doc["source_blob_sha"],
                "chunking": config, "start_char": start, "end_char": end,
                "source_sections": spans, "text": text[start:end],
                "classification": manifest["default_policy"]["classification"],
                "policy_id": manifest["default_policy"]["access"]["policy_id"],
                "declared_reader_roles": manifest["default_policy"]["access"]["allowed_reader_roles"],
                "mode": "offline_draft_study", "runtime_eligible": False,
                "authorization_verified": False, "current_freshness_verified": False,
            })
    return chunks


def prepare(repo_root, allow_draft_local=False, size=800, overlap=120):
    manifest, mh, loaded = load_documents(repo_root, allow_draft_local)
    outputs = {s: make_chunks(manifest, mh, loaded, s, size, overlap)
               for s in ("markdown_section", "fixed_window")}
    summary = {
        "loader_version": VERSION, "mode": "offline_draft_study",
        "corpus_id": manifest["corpus_id"], "corpus_version": manifest["corpus_version"],
        "manifest_sha256": mh, "document_count": len(loaded),
        "source_characters": sum(len(t) for _, t in loaded),
        "source_blob_verification": "PASS",
        "runtime_eligible": False, "current_access_and_freshness": "not_verified",
        "strategies": {},
    }
    for name, chunks in outputs.items():
        lengths = [len(c["text"]) for c in chunks]
        summary["strategies"][name] = {
            "chunk_count": len(chunks), "min_characters": min(lengths),
            "max_characters": max(lengths), "total_chunk_characters": sum(lengths),
            "chunks_over_800_characters": sum(n > 800 for n in lengths),
            "per_document": {doc["document_id"]: sum(c["document_id"] == doc["document_id"]
                                                    for c in chunks) for doc, _ in loaded},
        }
    return outputs, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--allow-draft-local", action="store_true")
    parser.add_argument("--size", type=int, default=800)
    parser.add_argument("--overlap", type=int, default=120)
    args = parser.parse_args()
    try:
        outputs, summary = prepare(args.repo_root, args.allow_draft_local, args.size, args.overlap)
        root = Path(args.repo_root).resolve()
        target = contained(root, "04-foundry-ai-engineering/AI-001/generated")
        target.mkdir(parents=True, exist_ok=True)
        destinations = [target / (name + ".jsonl") for name in outputs] + [target / "summary.json"]
        if any(p.exists() or p.is_symlink() for p in destinations):
            raise CorpusError("Output already exists; use a clean generated directory")
        for name, chunks in outputs.items():
            with (target / (name + ".jsonl")).open("x", encoding="utf-8", newline="\n") as handle:
                for chunk in chunks:
                    handle.write(canonical(chunk) + "\n")
        with (target / "summary.json").open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(summary, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print(json.dumps(summary, indent=2))
    except (CorpusError, OSError, UnicodeError, KeyError, TypeError, ValueError):
        parser.exit(2, "Local corpus preparation failed; check manifest, source hashes, parameters and output directory.\n")


if __name__ == "__main__":
    main()
