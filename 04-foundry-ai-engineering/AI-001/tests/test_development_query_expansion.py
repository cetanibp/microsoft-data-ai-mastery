"""Contracts for the frozen development query-expansion comparison."""
import copy
from contextlib import contextmanager
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(ROOT / "evaluation/run_development_query_expansion.py"))
SPEC = json.loads((ROOT / "evaluation/development-query-expansion-01.json").read_text(encoding="utf-8"))
SPEC02 = json.loads((ROOT / "evaluation/development-query-expansion-02.json").read_text(encoding="utf-8"))
SPEC03 = json.loads((ROOT / "evaluation/development-query-expansion-03.json").read_text(encoding="utf-8"))
SUPPLEMENT = json.loads((ROOT / "evaluation/development-cases-02.json").read_text(encoding="utf-8"))
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


@contextmanager
def supplemental_fixture(registry):
    """Simulate review only in temporary files; never approve the real packet."""
    spec = copy.deepcopy(SPEC03)
    spec["supplemental_development_cases"]["canonical_sha256"] = API["sha"](API["canonical"](registry))
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        (folder / "dataset.json").write_text(json.dumps(DATASET), encoding="utf-8")
        (folder / "development-cases-02.json").write_text(json.dumps(registry), encoding="utf-8")
        with mock.patch.dict(API["validate_spec"].__globals__, {"HERE": folder}):
            yield spec, folder


class DevelopmentQueryExpansionTests(unittest.TestCase):
    def test_pending_supplement_previews_locally_but_cannot_call_service(self):
        self.assertTrue(API["validate_spec"](SPEC03, allow_pending_review=True))
        class ForbiddenReader:
            calls = []

            def call(self, *args, **kwargs):
                raise AssertionError("Pending review must not reach Azure")

        with tempfile.TemporaryDirectory() as temp:
            result = API["execute"](SPEC03, ForbiddenReader(), Path(temp))
        self.assertEqual(result["status"], "blocked")
        self.assertIn("review is pending", result["error"])
        self.assertEqual(result["calls"], [])
        self.assertEqual(len(API["build_requests"](SPEC03)), 22)
        self.assertEqual(SPEC03["bounds"]["total_requests"], 30)

    def test_review_must_bind_cases_and_name_a_distinct_reviewer(self):
        registry = copy.deepcopy(SUPPLEMENT)
        registry["independent_review"].update(
            status="approved", reviewer="synthetic-reviewer-fixture", reviewed_on="2026-10-01",
            reviewed_cases_canonical_sha256=API["sha"](API["canonical"](registry["cases"])),
        )
        with supplemental_fixture(registry) as (spec, _):
            spec["status"] = "frozen_before_live_execution"
            self.assertFalse(API["validate_spec"](spec))
        variants = [copy.deepcopy(registry) for _ in range(3)]
        variants[0]["independent_review"]["reviewer"] = registry["authorship"]["author"]
        variants[1]["independent_review"]["reviewed_cases_canonical_sha256"] = "0" * 64
        variants[2]["cases"][0]["required_assertions"].append("Unreviewed new assertion")
        for changed in variants:
            with supplemental_fixture(changed) as (spec, _):
                spec["status"] = "frozen_before_live_execution"
                with self.assertRaisesRegex(ValueError, "Independent review"):
                    API["validate_spec"](spec)

    def test_supplement_hash_and_copied_evidence_cannot_drift(self):
        spec = copy.deepcopy(SPEC03)
        spec["supplemental_development_cases"]["canonical_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "declared hash"):
            API["validate_spec"](spec, allow_pending_review=True)
        spec = copy.deepcopy(SPEC03)
        spec["cases"][0]["required_evidence"][0]["text_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Supplemental evidence"):
            API["validate_spec"](spec, allow_pending_review=True)
        spec = copy.deepcopy(SPEC03)
        spec["supplemental_development_cases"]["path"] = "../outside.json"
        with self.assertRaisesRegex(ValueError, "declared local"):
            API["validate_spec"](spec, allow_pending_review=True)

    def test_supplement_cannot_replace_existing_cases_and_review_metadata_stays_local(self):
        registry = copy.deepcopy(SUPPLEMENT)
        registry["cases"][0]["case_id"] = DATASET["cases"][0]["case_id"]
        with supplemental_fixture(registry) as (spec, _):
            with self.assertRaisesRegex(ValueError, "replace existing or reserved"):
                API["validate_spec"](spec, allow_pending_review=True)
        for job in API["build_requests"](SPEC03):
            body = json.dumps(job["body"])
            for key in ("reviewer", "required_assertions", "independent_review", "cohort"):
                self.assertNotIn(key, body)
            for case in SUPPLEMENT["cases"]:
                for target in case["required_evidence"]:
                    for key in ("document_id", "heading_h2", "source_commit", "text_sha256"):
                        self.assertNotIn(target[key], body)

    def test_fusion_loss_against_expansion_is_visible_without_original_regression(self):
        first = ranked(1, "first", heading="Pattern")
        shared = ranked(2, "shared", heading="Objective")
        hit = ranked(5, "hit", heading="Needed", text="expected")
        expanded = [first] + [ranked(i, "other" + str(i), heading="Other" + str(i)) for i in range(2, 5)] + [hit]
        expanded += [ranked(i, "other" + str(i), heading="Other" + str(i)) for i in range(6, 9)]
        expanded.append(dict(shared, position=9))
        case = {"case_id": "fixture", "category": "supported", "cohort": "new_development",
                "required_evidence": [{"document_id": "doc", "heading_h2": "Needed",
                                       "source_commit": "a" * 40, "text_sha256": API["sha"](b"expected")}]}
        result = API["evaluate_case"](case, {"original": [first, shared], "expanded": expanded}, SPEC03)
        self.assertEqual(result["cohort"], "new_development")
        self.assertTrue(result["views"]["expanded"]["all_required_evidence"])
        self.assertFalse(result["views"]["fused"]["all_required_evidence"])
        self.assertTrue(result["views"]["fused_loss_vs_expanded"])
        self.assertFalse(result["views"]["fused_regression"])
        self.assertEqual(result["fused_candidates"]["required_evidence"][0]["position"], 6)

    def test_fixed_rule_preserves_arbitrary_question_without_case_inputs(self):
        question = "Can I repeat an unfamiliar task?\nWhich conditions apply? \u03bb"
        expanded = API["generate_expanded_query"](question, SPEC02["query_generation"])
        self.assertEqual(expanded, question + SPEC02["query_generation"]["suffix"])
        self.assertEqual(expanded[:len(question)], question)
        changed = copy.deepcopy(SPEC02)
        for case in changed["cases"]:
            case["category"] = "unused-fixture"
            case["required_evidence"] = [{"heading_h2": "Do not leak this target"}]
        self.assertEqual(API["build_requests"](changed), API["build_requests"](SPEC02))

    def test_both_comparison_specs_validate_and_preserve_baseline(self):
        API["validate_spec"](SPEC)
        API["validate_spec"](SPEC02)
        self.assertEqual(SPEC02["bounds"], SPEC["bounds"])
        for original, new in zip(SPEC["cases"], SPEC02["cases"]):
            self.assertEqual({k: v for k, v in original.items() if k != "expanded"},
                             {k: v for k, v in new.items() if k != "expanded"})
        for key in ("api_version", "index", "knowledge_base", "knowledge_source",
                    "semantic_configuration", "historical_corpus_fingerprint", "fusion"):
            self.assertEqual(SPEC02[key], SPEC[key])
        for job in API["build_requests"](SPEC02):
            for case in SPEC02["cases"]:
                for target in case["required_evidence"]:
                    for key in ("document_id", "heading_h2", "source_commit", "text_sha256"):
                        self.assertNotIn(target[key], json.dumps(job["body"]))

    def test_spec_drift_is_rejected_before_service_access(self):
        variants = []
        spec = copy.deepcopy(SPEC02)
        spec["cases"][0]["expanded"] += " special target"
        variants.append(spec)
        spec = copy.deepcopy(SPEC02)
        spec["query_generation"]["suffix"] += " changed rule"
        variants.append(spec)
        spec = copy.deepcopy(SPEC02)
        del spec["query_generation"]
        variants.append(spec)
        spec = copy.deepcopy(SPEC02)
        spec["bounds"]["total_requests"] += 1
        variants.append(spec)
        spec = copy.deepcopy(SPEC02)
        spec["final_context_limit"] = 6
        variants.append(spec)
        spec = copy.deepcopy(SPEC02)
        spec["cases"][0]["case_id"] = next(
            c["case_id"] for c in DATASET["cases"] if c["split"] == "reserved")
        variants.append(spec)
        class ForbiddenReader:
            def __init__(self):
                self.calls = []

            def call(self, *args, **kwargs):
                raise AssertionError("Invalid spec must not reach a service call")

        for spec in variants:
            with self.subTest(spec=spec["experiment_id"]), tempfile.TemporaryDirectory() as temp:
                reader = ForbiddenReader()
                result = API["execute"](spec, reader, Path(temp))
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["calls"], [])
                self.assertFalse((Path(temp) / "spec.json").exists())

    def test_candidate_pool_hit_beyond_five_does_not_pass_context(self):
        hit = ranked(6, "hit", document="doc", heading="Needed", text="expected")
        ranking = [ranked(i, "other" + str(i), heading="Other" + str(i)) for i in range(1, 6)] + [hit]
        case = {"case_id": "fixture", "category": "supported", "required_evidence": [{
            "document_id": "doc", "heading_h2": "Needed", "source_commit": "a" * 40,
            "text_sha256": API["sha"](b"expected"),
        }]}
        result = API["evaluate_case"](case, {"original": ranking, "expanded": ranking}, SPEC02)
        self.assertEqual(result["candidate_pool"], {
            "original_count": 6, "expanded_count": 6, "union_count": 6})
        self.assertTrue(result["fused_candidates"]["all_required_evidence"])
        self.assertEqual(result["fused_candidates"]["required_evidence"][0]["position"], 6)
        self.assertFalse(result["views"]["fused"]["all_required_evidence"])
        self.assertEqual(len(result["views"]["fused"]["ranking"]), 5)

    def test_validation_cli_needs_no_endpoint_or_output_directory(self):
        env = dict(os.environ)
        env.pop("SEARCH_ENDPOINT", None)
        proc = subprocess.run([
            sys.executable, "-B", str(ROOT / "evaluation/run_development_query_expansion.py"),
            "--spec", str(ROOT / "evaluation/development-query-expansion-02.json"),
            "--validate-only",
        ], capture_output=True, text=True, env=env, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "validated_locally")
        self.assertEqual(result["azure_requests_attempted"], 0)
        self.assertEqual(result["query_requests"], 10)
        self.assertEqual(result["spec_sha256"], API["sha"](API["canonical"](SPEC02)))

    def test_first_request_failure_stops_fixed_rule_batch_without_retry(self):
        class FailingReader:
            def __init__(self):
                self.calls = []

            def call(self, label, *args, **kwargs):
                self.calls.append({"id": label, "status": "failed"})
                raise API["RequestFailure"]("Authentication required")

        with tempfile.TemporaryDirectory() as temp:
            reader = FailingReader()
            result = API["execute"](SPEC02, reader, Path(temp))
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(len(reader.calls), 1)
            self.assertEqual(result["results"], [])

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
        self.assertTrue(result["views"]["expanded_regression"])
        self.assertFalse(result["views"]["fused_regression"])
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
