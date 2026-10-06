"""Portable saved-case contracts. No model, network, or operator lab needed."""
import copy
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest


PACKAGE = Path(__file__).resolve().parents[1] / "offline-reference"
API = runpy.run_path(str(PACKAGE / "reference.py"))
CASES = {
    "AI001-012": "clarify",
    "AI001-012-C1": "evidence_only",
    "AI001-013": "clarify",
    "AI001-013-C1": "evidence_only",
    "AI001-025": "decline",
}


class OfflineReferenceTests(unittest.TestCase):
    def copy_inputs(self, parent):
        root = Path(parent) / "standalone"
        root.mkdir()
        shutil.copytree(PACKAGE / "inputs", root / "inputs")
        return root

    def replace_input(self, root, case, data):
        """Update hash too, so scope tests reach validation beyond the hash gate."""
        index_path = root / "inputs/index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        raw = json.dumps(data).encode("utf-8")
        (root / index["cases"][case]["file"]).write_bytes(raw)
        index["cases"][case]["sha256"] = hashlib.sha256(raw).hexdigest()
        index_path.write_text(json.dumps(index), encoding="utf-8")

    def test_import_hashes_and_sanitized_ids(self):
        manifest = json.loads((PACKAGE / "import-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["files"]), 18)
        for entry in manifest["files"]:
            with self.subTest(file=entry["file"]):
                self.assertEqual(
                    hashlib.sha256((PACKAGE / entry["file"]).read_bytes()).hexdigest(),
                    entry["repository_sha256"],
                )
        for case in CASES:
            for passage in API["load"](PACKAGE, case)["passages"]:
                self.assertRegex(passage["chunk_id"], r"^sha256:[0-9a-f]{64}$")
                self.assertRegex(
                    passage["source_url"],
                    r"^https://github\.com/cetanibp/microsoft-data-ai-mastery/blob/[0-9a-f]{40}/",
                )

    def test_saved_outputs_preserve_passages_and_navigation(self):
        for case, mode in CASES.items():
            with self.subTest(case=case):
                data = API["load"](PACKAGE, case)
                response = API["response"](data)
                self.assertEqual(response["mode"], mode)
                self.assertFalse(response["generated_procedural_claims"])
                self.assertEqual(response, json.loads((PACKAGE / "views" / (case + ".json")).read_text(encoding="utf-8")))
                rendered = API["markdown"](data)
                self.assertEqual(rendered, (PACKAGE / "views" / (case + ".md")).read_text(encoding="utf-8"))
                anchors = re.findall(r'<a id="([^"]+)"></a>', rendered)
                targets = re.findall(r"\]\(#([^)]+)\)", rendered)
                self.assertEqual(len(anchors), len(set(anchors)))
                self.assertLessEqual(set(targets), set(anchors))
                if mode == "evidence_only":
                    self.assertEqual(response["passages"], data["passages"])
                    self.assertEqual(len(response["passages"]), 5)
                    for passage in response["passages"]:
                        quoted = "\n".join("> " + line for line in passage["text"].splitlines())
                        self.assertEqual(rendered.count(quoted), 1)
                else:
                    self.assertEqual(response["passages"], [])

    def test_required_evidence_and_known_gap_remain_visible(self):
        required = {
            "AI001-012-C1": {("northstar-triage", "Procedure"), ("northstar-recovery", "Select a pattern")},
            "AI001-013-C1": {("northstar-triage", "Procedure"), ("northstar-recovery", "Recovery verification")},
        }
        for case, expected in required.items():
            data = API["load"](PACKAGE, case)
            self.assertLessEqual(expected, {(p["document_id"], p["heading_h2"]) for p in data["passages"]})
        control = API["load"](PACKAGE, "AI001-025")
        self.assertNotIn("Corrective state action", {p["heading_h2"] for p in control["passages"]})
        self.assertEqual(API["response"](control)["mode"], "decline")
        self.assertIn("No corrective procedure is supplied", API["response"](control)["message"])

    def test_relocated_cli_with_only_script_and_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.copy_inputs(temp)
            shutil.copyfile(PACKAGE / "reference.py", root / "reference.py")
            for case in CASES:
                for fmt in ("json", "markdown"):
                    with self.subTest(case=case, format=fmt):
                        result = subprocess.run(
                            [sys.executable, "-I", "-B", "-X", "utf8", str(root / "reference.py"), "--case", case, "--format", fmt],
                            cwd=temp, capture_output=True, text=True, encoding="utf-8", timeout=15,
                        )
                        self.assertEqual(result.returncode, 0, result.stderr)
                        expected = (PACKAGE / "views" / (case + (".json" if fmt == "json" else ".md"))).read_text(encoding="utf-8")
                        if fmt == "json":
                            self.assertEqual(json.loads(result.stdout), json.loads(expected))
                        else:
                            self.assertEqual(result.stdout.rstrip("\n"), expected.rstrip("\n"))

    def test_unavailable_case_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown or unavailable case"):
            API["load"](PACKAGE, "UNPACKAGED-CASE")

    def test_changed_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.copy_inputs(temp)
            path = root / "inputs/AI001-012.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "Input hash mismatch"):
                API["load"](root, "AI001-012")

    def test_input_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.copy_inputs(temp)
            outside = root / "outside.json"
            outside.write_bytes((root / "inputs/AI001-012.json").read_bytes())
            index_path = root / "inputs/index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            index["cases"]["AI001-012"]["file"] = "inputs/../outside.json"
            index_path.write_text(json.dumps(index), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Input path outside package"):
                API["load"](root, "AI001-012")

    def test_saved_scope_guards_even_with_updated_hash(self):
        original = API["load"](PACKAGE, "AI001-012-C1")
        mutations = [
            ("case_id", "DIFFERENT-CASE", "Case identity or split mismatch"),
            ("split", "not_development", "Case identity or split mismatch"),
            ("passages", original["passages"] * 2, "Saved retrieval limit exceeded"),
        ]
        promoted = copy.deepcopy(original["passages"])
        promoted[0]["runtime_eligible"] = True
        mutations.append(("passages", promoted, "false-eligibility"))
        for key, value, error in mutations:
            with self.subTest(field=key, error=error), tempfile.TemporaryDirectory() as temp:
                root = self.copy_inputs(temp)
                data = copy.deepcopy(original)
                data[key] = value
                self.replace_input(root, "AI001-012-C1", data)
                with self.assertRaisesRegex(ValueError, error):
                    API["load"](root, "AI001-012-C1")


if __name__ == "__main__":
    unittest.main()
