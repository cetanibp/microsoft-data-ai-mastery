"""Run a frozen, read-only development query-expansion comparison."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
from datetime import datetime, timezone


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_force_commit_diagnostic import (  # noqa: E402
    AzureReader, FIELDS, SEARCH_FIELDS, RequestFailure, canonical,
    corpus_fingerprint, sha, validate_controls, write,
)


def build_requests(spec):
    jobs = []
    for case in spec["cases"]:
        for variant in ("original", "expanded"):
            body = {
                "search": case[variant],
                "queryType": "semantic",
                "searchMode": "any",
                "searchFields": ",".join(SEARCH_FIELDS),
                "semanticConfiguration": spec["semantic_configuration"],
                "count": True,
                "top": spec["candidate_limit_per_query"],
                "select": ",".join(FIELDS),
            }
            jobs.append({
                "id": case["case_id"] + "." + variant,
                "case_id": case["case_id"],
                "variant": variant,
                "route": "indexes/" + spec["index"] + "/docs/search",
                "body": body,
            })
    return jobs


def summarize_ranking(response, job, limit):
    if response.get("@search.semanticPartialResponseReason") or response.get("@search.semanticPartialResponseType"):
        raise ValueError("Partial semantic response prevents comparison")
    rows = response["value"]
    if len(rows) > limit:
        raise ValueError("Response exceeds declared candidate limit")
    ranking = []
    seen = set()
    for position, row in enumerate(rows, 1):
        if row["runtime_eligible"] is not False:
            raise ValueError("Unexpected eligibility")
        chunk_hash = sha(row["chunk_id"].encode("utf-8"))
        if chunk_hash in seen:
            raise ValueError("Duplicate result identity")
        seen.add(chunk_hash)
        ranking.append({
            "position": position,
            "chunk_id_sha256": chunk_hash,
            "document_id": row["document_id"],
            "heading_h2": row["heading_h2"],
            "text_sha256": sha(row["text"].encode("utf-8")),
            "source_commit": row["source_commit"],
            "runtime_eligible": row["runtime_eligible"],
            "search_score": row.get("@search.score"),
            "reranker_score": row.get("@search.rerankerScore"),
        })
    return {
        "id": job["id"],
        "case_id": job["case_id"],
        "variant": job["variant"],
        "returned": len(ranking),
        "match_count": response.get("@odata.count"),
        "ranking": ranking,
    }


def fuse_rankings(rankings, rank_constant, limit):
    combined = {}
    for variant in ("original", "expanded"):
        for row in rankings[variant]:
            key = row["chunk_id_sha256"]
            entry = combined.setdefault(key, {
                **{k: row[k] for k in (
                    "chunk_id_sha256", "document_id", "heading_h2",
                    "text_sha256", "source_commit", "runtime_eligible",
                )},
                "rrf_score": 0.0,
                "source_ranks": {},
            })
            identity = (entry["document_id"], entry["heading_h2"],
                        entry["text_sha256"], entry["source_commit"])
            observed = (row["document_id"], row["heading_h2"],
                        row["text_sha256"], row["source_commit"])
            if identity != observed:
                raise ValueError("Conflicting result identity")
            entry["source_ranks"][variant] = row["position"]
            entry["rrf_score"] += 1.0 / (rank_constant + row["position"])
    ordered = sorted(
        combined.values(),
        key=lambda row: (
            -row["rrf_score"], min(row["source_ranks"].values()),
            row["chunk_id_sha256"],
        ),
    )[:limit]
    return [dict(row, position=position) for position, row in enumerate(ordered, 1)]


def assess_evidence(ranking, required):
    observations = []
    for target in required:
        heading_matches = [
            row for row in ranking
            if row["document_id"] == target["document_id"]
            and row["heading_h2"] == target["heading_h2"]
        ]
        exact_matches = [
            row for row in heading_matches
            if row["source_commit"] == target["source_commit"]
            and row["text_sha256"] == target["text_sha256"]
        ]
        if len(heading_matches) > 1 or len(exact_matches) > 1:
            raise ValueError("Ambiguous evidence identity")
        observations.append({
            "document_id": target["document_id"],
            "heading_h2": target["heading_h2"],
            "position": exact_matches[0]["position"] if exact_matches else None,
            "heading_match_position": heading_matches[0]["position"] if heading_matches else None,
            "exact_text_and_revision": bool(exact_matches),
        })
    return {
        "all_required_evidence": all(row["exact_text_and_revision"] for row in observations),
        "required_evidence": observations,
    }


def evaluate_case(case, rankings, spec):
    limit = spec["final_context_limit"]
    original = rankings["original"][:limit]
    expanded = rankings["expanded"][:limit]
    fused = fuse_rankings(rankings, spec["fusion"]["rank_constant"], limit)
    views = {"original": original, "expanded": expanded, "fused": fused}
    assessed = {}
    for name, ranking in views.items():
        assessed[name] = {
            "ranking": ranking,
            **assess_evidence(ranking, case["required_evidence"]),
        }
    assessed["regression"] = bool(
        assessed["original"]["all_required_evidence"]
        and (not assessed["expanded"]["all_required_evidence"]
             or not assessed["fused"]["all_required_evidence"])
    )
    return {"case_id": case["case_id"], "category": case["category"], "views": assessed}


def execute(spec, reader, out):
    def controls(suffix):
        values = [reader.call(label + suffix, "GET", route) for label, route in (
            ("index", "indexes/" + spec["index"]),
            ("knowledge-base", "knowledgebases/" + spec["knowledge_base"]),
            ("knowledge-source", "knowledgesources/" + spec["knowledge_source"]),
        )]
        values.append(reader.call(
            "corpus" + suffix, "POST", "indexes/" + spec["index"] + "/docs/search",
            {"search": "*", "count": True, "top": 100, "select": ",".join(FIELDS)},
        ))
        return values

    result = {
        "status": "in_progress",
        "results": [],
        "model_generation_calls": 0,
        "configuration_mutations": 0,
        "reserved_cases_run": False,
        "spec_sha256": sha(canonical(spec)),
        "candidate_limit_per_query": spec["candidate_limit_per_query"],
        "final_context_limit": spec["final_context_limit"],
    }
    try:
        before = controls("-before")
        validate_controls(spec, *before)
        result["preflight_passed"] = True
        result["corpus_fingerprint"] = corpus_fingerprint(before[3])
        result["config_before_sha256"] = [sha(canonical(value)) for value in before[:3]]
        rankings = {}
        for job in build_requests(spec):
            response = reader.call(job["id"], "POST", job["route"], job["body"])
            row = summarize_ranking(response, job, spec["candidate_limit_per_query"])
            rankings.setdefault(job["case_id"], {})[job["variant"]] = row["ranking"]
            write(out / (job["id"] + ".ranking.json"), row)
            print(json.dumps({"id": row["id"], "returned": row["returned"]}), flush=True)
        for case in spec["cases"]:
            result["results"].append(evaluate_case(case, rankings[case["case_id"]], spec))
        after = controls("-after")
        validate_controls(spec, *after)
        result["config_after_sha256"] = [sha(canonical(value)) for value in after[:3]]
        result["configuration_unchanged"] = result["config_before_sha256"] == result["config_after_sha256"]
        result["corpus_unchanged"] = corpus_fingerprint(before[3]) == corpus_fingerprint(after[3])
        result["status"] = (
            "completed" if result["configuration_unchanged"] and result["corpus_unchanged"]
            else "invalidated_by_drift"
        )
    except (RequestFailure, ValueError, KeyError) as error:
        result.update(status="blocked", error_type=type(error).__name__, error=str(error))
    finally:
        result["calls"] = reader.calls
        result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        write(out / "summary.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec", type=Path,
        default=HERE / "development-query-expansion-01.json",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    endpoint = os.environ.get("SEARCH_ENDPOINT", "").rstrip("/")
    if not re.fullmatch(r"https://[a-z0-9-]+\.search\.windows\.net", endpoint):
        parser.error("Set SEARCH_ENDPOINT to the existing Azure Search service HTTPS origin")
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    write(out / "spec.json", spec)
    shutil.copyfile(__file__, out / "runner-snapshot.py")
    reader = AzureReader(endpoint, spec, out)
    result = execute(spec, reader, out)
    print(json.dumps({
        "status": result["status"],
        "requests_attempted": len(reader.calls),
        "results_directory": str(out),
    }))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
