"""Bounded, read-only retrieval diagnostic using Azure CLI authentication.

No model endpoint, configuration mutation, automatic retry, or raw credential
output. Public evidence contains request bodies, hashes and selected metadata.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone


FIELDS = [
    "chunk_id", "document_id", "heading_h1", "heading_h2", "text",
    "source_url", "source_commit", "runtime_eligible",
    "heading_h1_search_v1", "heading_h2_search_v1",
]
SEARCH_FIELDS = ["heading_h1_search_v1", "heading_h2_search_v1", "text"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def write(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def corpus_fingerprint(response):
    rows = []
    for record in response["value"]:
        row = {field: record[field] for field in FIELDS}
        row["chunk_id"] = sha(row["chunk_id"].encode("utf-8"))
        rows.append(row)
    rows.sort(key=lambda row: row["chunk_id"])
    if len({row["chunk_id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate corpus identity")
    return sha(canonical(rows))


def build_requests(spec):
    jobs = []
    for query in spec["queries"]:
        for arm in spec["arms"]:
            if arm["kind"] == "search":
                body = {
                    "search": query["text"], "queryType": arm["query_type"],
                    "searchMode": "any", "searchFields": ",".join(SEARCH_FIELDS),
                    "count": True, "top": arm["limit"], "select": ",".join(FIELDS),
                }
                if arm["query_type"] == "semantic":
                    body["semanticConfiguration"] = spec["semantic_configuration"]
                route = "indexes/" + spec["index"] + "/docs/search"
            else:
                body = {
                    "intents": [{"type": "semantic", "search": query["text"]}],
                    "includeActivity": True, "maxOutputDocuments": arm["limit"],
                    "knowledgeSourceParams": [{
                        "knowledgeSourceName": spec["knowledge_source"], "kind": "searchIndex",
                        "includeReferences": True, "includeReferenceSourceData": True,
                    }],
                }
                for option in ("rerankerThreshold", "resultsProcessing"):
                    if option in arm:
                        body["knowledgeSourceParams"][0][option] = arm[option]
                if arm.get("resultsProcessing") == "none" and "rerankerThreshold" in arm:
                    raise ValueError("Threshold cannot be combined with disabled reranking")
                route = "knowledgebases/" + spec["knowledge_base"] + "/retrieve"
            jobs.append({"id": query["id"] + "." + arm["id"], "query_id": query["id"],
                         "arm": arm, "route": route, "body": body})
    return jobs


def summarize(response, job, target):
    kb = job["arm"]["kind"] == "knowledge_base"
    raw_rows = response["references"] if kb else response["value"]
    ranking = []
    for position, raw in enumerate(raw_rows, 1):
        row = raw["sourceData"] if kb else raw
        if row["runtime_eligible"] is not False:
            raise ValueError("Unexpected eligibility")
        ranking.append({
            "position": position, "chunk_id_sha256": sha(row["chunk_id"].encode("utf-8")),
            "document_id": row["document_id"], "heading_h2": row["heading_h2"],
            "text_sha256": sha(row["text"].encode("utf-8")), "source_commit": row["source_commit"],
            "runtime_eligible": row["runtime_eligible"],
            "search_score": None if kb else raw.get("@search.score"),
            "reranker_score": raw.get("rerankerScore") if kb else raw.get("@search.rerankerScore"),
        })
    if len(ranking) > job["arm"]["limit"]:
        raise ValueError("Response exceeds declared output limit")
    matches = [r for r in ranking if r["document_id"] == target["document_id"] and r["heading_h2"] == target["heading_h2"]]
    if len(matches) > 1:
        raise ValueError("Ambiguous target identity")
    match = matches[0] if matches else None
    exact = bool(match and match["text_sha256"] == target["text_sha256"] and match["source_commit"] == target["source_commit"])
    activity = [{
        "type": a.get("type"), "count": a.get("count"),
        "search": a.get("searchIndexArguments", {}).get("search"),
        "search_fields": a.get("searchIndexArguments", {}).get("searchFields"),
        "semantic_configuration": a.get("searchIndexArguments", {}).get("semanticConfigurationName"),
        "filter": a.get("searchIndexArguments", {}).get("filter"),
        "knowledge_source": a.get("knowledgeSourceName"),
    } for a in response.get("activity", [])]
    return {
        "id": job["id"], "returned": len(ranking), "match_count": response.get("@odata.count"),
        "target_position": match["position"] if match else None,
        "target_exact_text_and_revision": exact,
        "target_in_top5": bool(exact and match["position"] <= 5),
        "ranking": ranking, "activity": activity,
        "semantic_partial_response_reason": response.get("@search.semanticPartialResponseReason"),
        "semantic_partial_response_type": response.get("@search.semanticPartialResponseType"),
    }


def validate_controls(spec, index, kb, source, corpus):
    if len(corpus["value"]) != spec["expected_corpus_count"] or corpus.get("@odata.count") != spec["expected_corpus_count"]:
        raise ValueError("Corpus size changed or incomplete snapshot")
    if any(d["runtime_eligible"] is not False for d in corpus["value"]):
        raise ValueError("Corpus eligibility changed")
    if corpus_fingerprint(corpus) != spec["historical_corpus_fingerprint"]:
        raise ValueError("Corpus differs from frozen historical baseline")
    if kb.get("models") or kb.get("outputMode") != "extractiveData" or kb.get("retrievalReasoningEffort", {}).get("kind") != "minimal":
        raise ValueError("Knowledge base no longer uses model-free minimal extraction")
    if [s["name"] for s in kb["knowledgeSources"]] != [spec["knowledge_source"]]:
        raise ValueError("Knowledge source set changed")
    if kb.get("retrieveDefaults"):
        raise ValueError("New knowledge-base retrieval defaults require review")
    params = source["searchIndexParameters"]
    if source.get("kind") != "searchIndex" or params["searchIndexName"] != spec["index"]:
        raise ValueError("Knowledge source index changed")
    if [f["name"] for f in params["searchFields"]] != SEARCH_FIELDS or params["semanticConfigurationName"] != spec["semantic_configuration"]:
        raise ValueError("Knowledge source search settings changed")
    if source.get("resultsProcessing") not in (None, "rerank"):
        raise ValueError("Knowledge source no longer reranks")
    if index.get("scoringProfiles") or index.get("defaultScoringProfile"):
        raise ValueError("Scoring profiles prevent controlled comparison")
    if any(f.get("dimensions") or f.get("vectorSearchDimensions") for f in index["fields"]):
        raise ValueError("Vector fields require a different experiment")
    configs = index.get("semantic", {}).get("configurations", [])
    if not any(c["name"] == spec["semantic_configuration"] for c in configs):
        raise ValueError("Expected semantic configuration missing")


class RequestFailure(Exception):
    pass


class AzureReader:
    def __init__(self, endpoint, spec, out):
        self.endpoint, self.spec, self.out = endpoint, spec, out
        self.az = shutil.which("az")
        if not self.az:
            raise ValueError("Azure CLI not found")
        self.calls = []

    def call(self, label, method, route, body=None):
        if len(self.calls) >= self.spec["bounds"]["total_requests"]:
            raise ValueError("Request budget exhausted")
        if method not in ("GET", "POST") or (method == "POST" and not route.endswith(("/docs/search", "/retrieve"))):
            raise ValueError("Only configuration reads and retrieval requests are permitted")
        url = self.endpoint + "/" + route + "?api-version=" + self.spec["api_version"]
        args = [self.az, "rest", "--method", method, "--url", url,
                "--resource", "https://search.azure.com", "--output", "json", "--only-show-errors"]
        if body is not None:
            request_file = self.out / (label + ".request.json")
            write(request_file, body)
            args += ["--headers", "Content-Type=application/json", "--body", "@" + str(request_file.resolve())]
        meta = {"id": label, "method": method, "route": route, "attempts": 1,
                "started_at_utc": datetime.now(timezone.utc).isoformat()}
        self.calls.append(meta)
        start = time.perf_counter()
        try:
            proc = subprocess.run(args, capture_output=True, timeout=55)
            if proc.returncode:
                err = proc.stderr.decode("utf-8", errors="replace")
                meta.update(status="failed", cli_exit_code=proc.returncode,
                            auth_codes=sorted(set(re.findall(r"AADSTS\d+", err))),
                            requires_login=bool(re.search(r"(?i)(az login|interactive authentication|MFA)", err)))
                raise RequestFailure("Azure CLI request failed; raw diagnostics withheld")
            raw = proc.stdout
            try:
                decoded = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                decoded = raw.decode("cp1252")
            response = json.loads(decoded)
            meta.update(status="succeeded", response_sha256=sha(raw))
            return response
        except subprocess.TimeoutExpired:
            meta["status"] = "timed_out"
            raise RequestFailure("Azure CLI request timed out; no retry") from None
        finally:
            meta["elapsed_seconds"] = round(time.perf_counter() - start, 4)
            write(self.out / (label + ".metrics.json"), meta)


def execute(spec, reader, out):
    def controls(suffix):
        values = [reader.call(label + suffix, "GET", route) for label, route in (
            ("index", "indexes/" + spec["index"]),
            ("knowledge-base", "knowledgebases/" + spec["knowledge_base"]),
            ("knowledge-source", "knowledgesources/" + spec["knowledge_source"]),
        )]
        values.append(reader.call("corpus" + suffix, "POST", "indexes/" + spec["index"] + "/docs/search",
                                  {"search": "*", "count": True, "top": 100, "select": ",".join(FIELDS)}))
        return values

    result = {"status": "in_progress", "results": [], "model_generation_calls": 0,
              "configuration_mutations": 0, "reserved_cases_run": False,
              "spec_sha256": sha(canonical(spec))}
    try:
        before = controls("-before")
        validate_controls(spec, *before)
        result["preflight_passed"] = True
        result["corpus_fingerprint"] = corpus_fingerprint(before[3])
        result["semantic_configuration"] = before[0].get("semantic")
        result["config_before_sha256"] = [sha(canonical(v)) for v in before[:3]]
        for job in build_requests(spec):
            raw = reader.call(job["id"], "POST", job["route"], job["body"])
            row = summarize(raw, job, spec["target"])
            result["results"].append(row)
            write(out / (job["id"] + ".ranking.json"), row)
            print(json.dumps({k: row[k] for k in ("id", "returned", "target_position", "target_exact_text_and_revision")}), flush=True)
        after = controls("-after")
        validate_controls(spec, *after)
        result["config_after_sha256"] = [sha(canonical(v)) for v in after[:3]]
        result["configuration_unchanged"] = result["config_before_sha256"] == result["config_after_sha256"]
        result["corpus_unchanged"] = corpus_fingerprint(before[3]) == corpus_fingerprint(after[3])
        result["status"] = "completed" if result["configuration_unchanged"] and result["corpus_unchanged"] else "invalidated_by_drift"
    except (RequestFailure, ValueError, KeyError) as error:
        result.update(status="blocked", error_type=type(error).__name__, error=str(error))
    finally:
        result["calls"] = reader.calls
        result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        write(out / "summary.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=Path(__file__).with_name("force-commit-diagnostic-01.json"))
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
    print(json.dumps({"status": result["status"], "requests_attempted": len(reader.calls), "results_directory": str(out)}))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
