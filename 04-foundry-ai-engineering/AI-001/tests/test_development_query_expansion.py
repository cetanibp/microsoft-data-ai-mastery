"""Contracts for the frozen development query-expansion comparison."""
import copy
import json
from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(ROOT / "evaluation/run_development_query_expansion.py"))
SPEC = json.loads((ROOT / "evaluation/development-query-expansion-01.json").read_text(encoding="utf-8"))
DATASET = json.loads((ROOT / "evaluation/dataset.json").read_text(encoding="utf-8"))


def ranked(position, identity, document="doc", heading="heading", text="text", commit="a" * 40):
    return {
        "position": position,
        "chunk_id_sha256": identity,
        "document_id": document,
        "heading_h2": heading,
        "text_sha256": API["sha"](text.encode()),
        "source_commit": commit,
        "runtime_eligible": False,
        "search_score": 1.0,
        "reranker_score": 1.0,
    }


class DevelopmentQueryExpansionTests(unittest.TestCase):
    def test_case_scope_and_original_questions_are_frozen(self):
        dataset = {case["case_id"]: case for case in DATASET["cases"]}
        expected_ids = ["AI001-001", "AI001-011", "AI001-012", "AI001-013", "AI001-025"]
        self.assertEqual([case["case_id"] for case in SPEC["cases"]], expected_ids)
        for case in SPEC["cases"]:
            source = dataset[case["case_id"]]
            self.assertEqual(source["split"], "development")
            self.assertEqual(case["original"], source["question"])
            self.assertEqual(case["category"], source["category"])
            self.assertNotEqual(case["expanded"], case["original"])

    def test_request_matrix_is_bounded_and_targets_are_evaluator_only(self):
        jobs = API["build_requests"](SPEC)
        self.assertEqual(len(jobs), 10)
        self.assertEqual(len({job["id"] for job in jobs}), 10)
        self.assertEqual(SPEC["bounds"]["total_requests"], 18)
        targets = json.dumps([case["required_evidence"] for case in SPEC["cases"]])
        for job in jobs:
            body = job["body"]
            self.assertEqual(body["top"], 10)
            self.assertEqual(body["queryType"], "semantic")
            self.assertEqual(body["searchFields"], ",".join(API["SEARCH_FIELDS"]))
            self.assertNotIn("filter", body)
            self.assertNotIn("vectorQueries", body)
            self.assertNotIn("scoringProfile", body)
            for case in SPEC["cases"]:
                for target in case["required_evidence"]:
                    self.assertNotIn(target["text_sha256"], json.dumps(body))
                    self.assertNotIn(target["heading_h2"], json.dumps(body))
            self.assertNotIn("text_sha256", json.dumps(body))
        self.assertIn("Corrective state action", targets)

    def test_rrf_is_deterministic_and_capped(self):
        rankings = {
            "original": [ranked(i, "o" + str(i)) for i in range(1, 11)],
            "expanded": [ranked(i, "e" + str(i)) for i in range(1, 11)],
        }
        rankings["expanded"][1] = copy.deepcopy(rankings["original"][0])
        rankings["expanded"][1]["position"] = 2
        first = API["fuse_rankings"](rankings, 60, 5)
        second = API["fuse_rankings"](rankings, 60, 5)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 5)
        self.assertEqual(first[0]["chunk_id_sha256"], "o1")
        self.assertEqual(first[0]["source_ranks"], {"original": 1, "expanded": 2})

    def test_exact_evidence_and_heading_match_are_separate(self):
        row = ranked(1, "one", document="doc", heading="Needed", text="expected")
        target = {
            "document_id": "doc", "heading_h2": "Needed",
            "source_commit": "a" * 40,
            "text_sha256": API["sha"](b"expected"),
        }
        result = API["assess_evidence"]([row], [target])
        self.assertTrue(result["all_required_evidence"])
        row["text_sha256"] = API["sha"](b"changed")
        result = API["assess_evidence"]([row], [target])
        self.assertFalse(result["all_required_evidence"])
        self.assertEqual(result["required_evidence"][0]["heading_match_position"], 1)
        self.assertIsNone(result["required_evidence"][0]["position"])

    def test_regression_requires_complete_original(self):
        case = {
            "case_id": "fixture", "category": "supported",
            "required_evidence": [{
                "document_id": "doc", "heading_h2": "Needed",
                "source_commit": "a" * 40, "text_sha256": API["sha"](b"expected"),
            }],
        }
        hit = ranked(1, "hit", document="doc", heading="Needed", text="expected")
        miss = ranked(1, "miss")
        rankings = {"original": [hit], "expanded": [miss]}
        result = API["evaluate_case"](case, rankings, SPEC)
        self.assertTrue(result["views"]["regression"])
        rankings["original"] = [miss]
        result = API["evaluate_case"](case, rankings, SPEC)
        self.assertFalse(result["views"]["regression"])

    def test_partial_semantic_response_and_eligibility_are_rejected(self):
        job = API["build_requests"](SPEC)[0]
        row = {field: "fixture" for field in API["FIELDS"]}
        row.update(chunk_id="fixture", runtime_eligible=False, source_commit="a" * 40)
        response = {"value": [row], "@search.semanticPartialResponseReason": "CapacityOverloaded"}
        with self.assertRaisesRegex(ValueError, "Partial semantic"):
            API["summarize_ranking"](response, job, 10)
        response.pop("@search.semanticPartialResponseReason")
        row["runtime_eligible"] = True
        with self.assertRaisesRegex(ValueError, "eligibility"):
            API["summarize_ranking"](response, job, 10)


if __name__ == "__main__":
    unittest.main()
