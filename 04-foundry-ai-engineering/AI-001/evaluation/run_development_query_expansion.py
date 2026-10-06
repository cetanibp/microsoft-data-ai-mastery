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


QUESTION_ONLY_RULE = {
    "rule_id": "question-only-v1",
    "method": "append_fixed_suffix",
    "suffix": "\nDocumented prerequisites, decision conditions, restrictions, and verification.",
}


def generate_expanded_query(question, rule):
    """Expand only the question; no case, category or evidence input is accepted."""
    if rule != QUESTION_ONLY_RULE:
        raise ValueError("Unsupported query-generation rule; declare a new comparison")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Original question must be nonempty text")
    return question + rule["suffix"]


def load_supplemental_cases(spec, dataset, allow_pending_review):
    """Load a hash-pinned development supplement with recorded human review."""
    reference = spec["supplemental_development_cases"]
    path = (HERE / reference["path"]).resolve()
    if path.parent != HERE.resolve() or path.name != "development-cases-02.json":
        raise ValueError("Supplement must be the declared local development case registry")
    registry = json.loads(path.read_text(encoding="utf-8"))
    if sha(canonical(registry)) != reference["canonical_sha256"]:
        raise ValueError("Supplemental case registry differs from the declared hash")
    cases = registry["cases"]
    existing = {case["case_id"] for case in dataset["cases"]}
    if not cases or len({case["case_id"] for case in cases}) != len(cases):
        raise ValueError("Supplemental cases must be nonempty and unique")
    for case in cases:
        if case["case_id"] in existing or case["split"] != "development":
            raise ValueError("Supplement cannot replace existing or reserved cases")
        if (case["category"] not in ("supported", "ambiguous", "unanswerable")
                or case["expected_behavior"] not in ("answer", "clarify", "decline")
                or not case["question"].strip() or not case["required_assertions"]
                or not case["required_evidence"] or not case["forbidden_behavior"]):
            raise ValueError("Supplemental behavior and evidence declarations are incomplete")
    review = registry["independent_review"]
    pending = review["status"] != "approved"
    if not pending:
        reviewer = review["reviewer"]
        if (not isinstance(reviewer, str) or not reviewer.strip()
                or reviewer == registry["authorship"]["author"]
                or not review["reviewed_on"]
                or review["reviewed_cases_canonical_sha256"] != sha(canonical(cases))):
            raise ValueError("Independent review must identify the reviewer and cover unchanged cases")
    if pending and not allow_pending_review:
        raise ValueError("Independent case review is pending; no service requests are allowed")
    return {case["case_id"]: case for case in cases}, pending


def validate_spec(spec, allow_pending_review=False):
    """Reject scope, budget and generated-query drift before any service call."""
    dataset = json.loads((HERE / "dataset.json").read_text(encoding="utf-8"))
    development = {case["case_id"]: case for case in dataset["cases"]
                   if case["split"] == "development"}
    supplemental = {}
    pending_review = False
    if "supplemental_development_cases" in spec:
        supplemental, pending_review = load_supplemental_cases(spec, dataset, allow_pending_review)
    if spec["status"] != "frozen_before_live_execution":
        if not (allow_pending_review and pending_review
                and spec["status"] == "draft_pending_independent_review"):
            raise ValueError("Comparison must be frozen before live execution")
    if spec["scope"] != "retrieval_only_development_comparison":
        raise ValueError("Only retrieval-only development comparisons are supported")
    if (spec["candidate_limit_per_query"] != 10 or spec["final_context_limit"] != 5
            or spec["fusion"] != {"method": "reciprocal_rank_fusion",
                                  "rank_constant": 60, "inputs": ["original", "expanded"]}):
        raise ValueError("Candidate, context or fusion settings differ from declared comparison")
    cases = spec["cases"]
    if not cases or len({case["case_id"] for case in cases}) != len(cases):
        raise ValueError("Cases must be nonempty and unique")
    expected_bounds = {
        "query_requests": 2 * len(cases), "configuration_reads": 6,
        "corpus_reads": 2, "total_requests": 2 * len(cases) + 8,
        "attempts_per_request": 1, "model_generation_calls": 0,
    }
    if spec["bounds"] != expected_bounds:
        raise ValueError("Request bounds do not match the comparison matrix")
    rule = spec.get("query_generation")
    if spec["experiment_id"] in ("development-query-expansion-02", "development-query-expansion-03") and rule is None:
        raise ValueError("Fixed-rule comparison requires its declared query-generation rule")
    if spec["experiment_id"] == "development-query-expansion-03" and not supplemental:
        raise ValueError("Comparison 03 requires the supplemental development cases")
    for case in cases:
        source = supplemental.get(case["case_id"], development.get(case["case_id"]))
        if source is None:
            raise ValueError("Case must be an existing development question")
        if case["original"] != source["question"] or case["category"] != source["category"]:
            raise ValueError("Original question or category differs from the dataset")
        if not case["required_evidence"]:
            raise ValueError("Evidence-bearing comparison requires evaluator targets")
        if case["case_id"] in supplemental:
            if (case["required_evidence"] != source["required_evidence"]
                    or case.get("cohort") != "new_development"):
                raise ValueError("Supplemental evidence or cohort differs from reviewed cases")
        elif supplemental and case.get("cohort") != "historical_control":
            raise ValueError("Existing questions must remain historical controls")
        if rule is not None and case["expanded"] != generate_expanded_query(case["original"], rule):
            raise ValueError("Expanded query differs from the frozen question-only rule")
    if supplemental and not set(supplemental).issubset({case["case_id"] for case in cases}):
        raise ValueError("Comparison must include every declared supplemental case")
    return pending_review


def build_requests(spec):
    jobs = []
    for case in spec["cases"]:
        for variant in ("original", "expanded"):
            body = {
                "search": (generate_expanded_query(case["original"], spec["query_generation"])
                           if variant == "expanded" and "query_generation" in spec
                           else case[variant]),
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
    pool_count = len({row["chunk_id_sha256"] for ranking in rankings.values() for row in ranking})
    fused_candidates = fuse_rankings(rankings, spec["fusion"]["rank_constant"], pool_count)
    fused = fused_candidates[:limit]
    views = {"original": original, "expanded": expanded, "fused": fused}
    assessed = {}
    for name, ranking in views.items():
        assessed[name] = {
            "ranking": ranking,
            **assess_evidence(ranking, case["required_evidence"]),
        }
    for variant in ("expanded", "fused"):
        assessed[variant + "_regression"] = bool(
            assessed["original"]["all_required_evidence"]
            and not assessed[variant]["all_required_evidence"]
        )
    assessed["regression"] = assessed["expanded_regression"] or assessed["fused_regression"]
    assessed["fused_loss_vs_expanded"] = bool(
        assessed["expanded"]["all_required_evidence"]
        and not assessed["fused"]["all_required_evidence"]
    )
    result = {
        "case_id": case["case_id"], "category": case["category"], "views": assessed,
        "candidate_pool": {
            "original_count": len(rankings["original"]),
            "expanded_count": len(rankings["expanded"]), "union_count": pool_count,
        },
        "fused_candidates": {
            "ranking": fused_candidates,
            **assess_evidence(fused_candidates, case["required_evidence"]),
        },
    }
    if "cohort" in case:
        result["cohort"] = case["cohort"]
    return result


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
        validate_spec(spec)
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
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--validate-only", action="store_true",
                        help="Validate locally, allowing a draft pending review; no Azure calls or output files")
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    try:
        pending_review = validate_spec(spec, allow_pending_review=args.validate_only)
    except (ValueError, KeyError) as error:
        parser.error(str(error))
    if args.validate_only:
        print(json.dumps({
            "status": "structurally_valid_pending_review" if pending_review else "validated_locally",
            "experiment_id": spec["experiment_id"],
            "spec_sha256": sha(canonical(spec)), "query_requests": len(build_requests(spec)),
            "total_request_budget": spec["bounds"]["total_requests"],
            "azure_requests_attempted": 0,
            "live_execution_ready": not pending_review,
        }))
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required for a live run")
    endpoint = os.environ.get("SEARCH_ENDPOINT", "").rstrip("/")
    if not re.fullmatch(r"https://[a-z0-9-]+\.search\.windows\.net", endpoint):
        parser.error("Set SEARCH_ENDPOINT to the existing Azure Search service HTTPS origin")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    write(out / "spec.json", spec)
    shutil.copyfile(__file__, out / "runner-snapshot.py")
    shutil.copyfile(HERE / "run_force_commit_diagnostic.py", out / "reader-snapshot.py")
    if "supplemental_development_cases" in spec:
        shutil.copyfile(HERE / spec["supplemental_development_cases"]["path"],
                        out / "supplemental-cases-snapshot.json")
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
