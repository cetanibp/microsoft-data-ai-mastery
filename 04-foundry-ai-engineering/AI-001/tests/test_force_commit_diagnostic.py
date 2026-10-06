"""Diagnostic contracts using synthetic development fixtures; no Azure calls."""
import copy
import json
from pathlib import Path
import runpy
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(ROOT / "evaluation/run_force_commit_diagnostic.py"))
SPEC = json.loads((ROOT / "evaluation/force-commit-diagnostic-01.json").read_text(encoding="utf-8"))


def document(number=0):
    row = {field: "fixture" for field in API["FIELDS"]}
    row.update(chunk_id="fixture-" + str(number), runtime_eligible=False,
               document_id="northstar-recovery", heading_h2="Corrective state action",
               text="Synthetic evidence.", source_commit="a" * 40)
    return row


class ForceCommitDiagnosticTests(unittest.TestCase):
    def test_frozen_matrix_and_target_not_in_requests(self):
        jobs = API["build_requests"](SPEC)
        self.assertEqual(len(jobs), 12)
        self.assertEqual(len({j["id"] for j in jobs}), 12)
        self.assertEqual(SPEC["bounds"]["total_requests"], 20)
        for job in jobs:
            body = job["body"]
            self.assertNotIn("Corrective state action", json.dumps(body))
            self.assertNotIn(SPEC["target"]["text_sha256"], json.dumps(body))
            self.assertNotIn("filter", body)
            self.assertNotIn("scoringProfile", body)
            self.assertNotIn("vectorQueries", body)
            if job["arm"]["kind"] == "search":
                self.assertEqual(body["top"], 18)
                self.assertEqual(body["searchFields"], ",".join(API["SEARCH_FIELDS"]))

    def test_fingerprint_ignores_order_but_detects_content_change(self):
        corpus = {"value": [document(0), document(1)]}
        before = API["corpus_fingerprint"](corpus)
        corpus["value"].reverse()
        self.assertEqual(before, API["corpus_fingerprint"](corpus))
        corpus["value"][0]["text"] += " changed"
        self.assertNotEqual(before, API["corpus_fingerprint"](corpus))
        corpus["value"][0] = corpus["value"][1]
        with self.assertRaisesRegex(ValueError, "Duplicate corpus identity"):
            API["corpus_fingerprint"](corpus)

    def test_followup_changes_only_declared_request_options(self):
        spec = json.loads((ROOT / "evaluation/force-commit-diagnostic-02.json").read_text(encoding="utf-8"))
        jobs = API["build_requests"](spec)
        self.assertEqual(len(jobs), 3)
        self.assertEqual(spec["queries"], SPEC["queries"][:1])
        baseline = jobs[0]["body"]
        for job, option, value in zip(jobs[1:], ("rerankerThreshold", "resultsProcessing"), (0, "none")):
            expected = copy.deepcopy(baseline)
            expected["knowledgeSourceParams"][0][option] = value
            self.assertEqual(job["body"], expected)
        spec["arms"][-1]["rerankerThreshold"] = 0
        with self.assertRaisesRegex(ValueError, "disabled reranking"):
            API["build_requests"](spec)

    def test_rank_and_exact_evidence_are_separate(self):
        row = document()
        target = {key: row[key] for key in ("document_id", "heading_h2", "source_commit")}
        target["text_sha256"] = API["sha"](row["text"].encode())
        distractors = [dict(document(i + 1), heading_h2="Different") for i in range(5)]
        job = API["build_requests"](SPEC)[0]
        response = {"value": distractors + [row], "@odata.count": 6}
        summary = API["summarize"](response, job, target)
        self.assertEqual(summary["target_position"], 6)
        self.assertTrue(summary["target_exact_text_and_revision"])
        self.assertFalse(summary["target_in_top5"])
        row["text"] = ""
        self.assertFalse(API["summarize"](response, job, target)["target_exact_text_and_revision"])
        response["value"] = distractors
        self.assertIsNone(API["summarize"](response, job, target)["target_position"])

    def test_kb_limit_and_eligibility_guards(self):
        job = API["build_requests"](SPEC)[2]
        row = document()
        response = {"references": [{"sourceData": row, "rerankerScore": 1.0}] * 6}
        with self.assertRaisesRegex(ValueError, "output limit"):
            API["summarize"](response, job, SPEC["target"])
        response["references"] = response["references"][:1]
        row["runtime_eligible"] = True
        with self.assertRaisesRegex(ValueError, "eligibility"):
            API["summarize"](response, job, SPEC["target"])

    def test_preflight_rejects_drift_and_generation(self):
        spec = copy.deepcopy(SPEC)
        corpus = {"@odata.count": 18, "value": [document(i) for i in range(18)]}
        spec["historical_corpus_fingerprint"] = API["corpus_fingerprint"](corpus)
        index = {"fields": [], "semantic": {"configurations": [{"name": spec["semantic_configuration"]}]}}
        kb = {"models": [], "outputMode": "extractiveData", "retrievalReasoningEffort": {"kind": "minimal"},
              "knowledgeSources": [{"name": spec["knowledge_source"]}]}
        source = {"kind": "searchIndex", "searchIndexParameters": {
            "searchIndexName": spec["index"], "searchFields": [{"name": f} for f in API["SEARCH_FIELDS"]],
            "semanticConfigurationName": spec["semantic_configuration"]}}
        API["validate_controls"](spec, index, kb, source, corpus)
        corpus["value"][0]["text"] += " changed"
        with self.assertRaisesRegex(ValueError, "historical baseline"):
            API["validate_controls"](spec, index, kb, source, corpus)
        corpus["value"][0] = document(0)
        kb["models"] = [{"kind": "unexpected-model"}]
        with self.assertRaisesRegex(ValueError, "model-free"):
            API["validate_controls"](spec, index, kb, source, corpus)

    def test_first_request_failure_stops_without_retry(self):
        class FailingReader:
            calls = []

            def call(self, label, *args, **kwargs):
                self.calls.append({"id": label, "status": "failed", "requires_login": True})
                raise API["RequestFailure"]("Authentication required")

        with tempfile.TemporaryDirectory() as temp:
            reader = FailingReader()
            result = API["execute"](SPEC, reader, Path(temp))
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(len(reader.calls), 1)
            self.assertEqual(result["results"], [])
            self.assertEqual(json.loads((Path(temp) / "summary.json").read_text())["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
