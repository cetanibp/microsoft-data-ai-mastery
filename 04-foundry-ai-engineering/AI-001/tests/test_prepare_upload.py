"""Local upload projection checks; no Azure access."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

AI_ROOT = Path(__file__).resolve().parents[1]
REPO = AI_ROOT.parents[1]
spec = importlib.util.spec_from_file_location("prepare_upload", AI_ROOT / "azure-search/prepare_upload.py")
upload = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upload)


class UploadProjectionTests(unittest.TestCase):
    def test_round_trip_and_determinism(self):
        chunks, _ = upload.prepare(REPO, True)
        payloads, summary = upload.build(REPO, True)
        self.assertEqual(payloads, upload.build(REPO, True)[0])
        for label, strategy in upload.STRATEGIES.items():
            records = json.loads(payloads[label + ".upload.json"])["value"]
            self.assertEqual(len(records), len(chunks[strategy]))
            for original, record in zip(chunks[strategy], records):
                self.assertEqual(record["@search.action"], "upload")
                for key, value in original.items():
                    if key not in ("chunking", "source_sections"):
                        self.assertEqual(record[key], value)
                self.assertEqual(json.loads(record["chunking_json"]), original["chunking"])
                self.assertEqual(json.loads(record["source_sections_json"]), original["source_sections"])
        self.assertFalse(summary["cloud_upload_performed"])

    def test_explicit_draft_flag_required(self):
        with self.assertRaises(upload.CorpusError):
            upload.build(REPO)

    def test_rejects_promoted_flags_and_wrong_strategy(self):
        chunks, _ = upload.prepare(REPO, True)
        fields = json.loads((AI_ROOT / "azure-search/sections.index.json").read_text())["fields"]
        for flag in upload.FLAGS:
            chunk = copy.deepcopy(chunks["markdown_section"][0])
            chunk[flag] = True
            with self.assertRaises(upload.CorpusError):
                upload.project(chunk, fields, "markdown_section")
        with self.assertRaises(upload.CorpusError):
            upload.project(chunks["markdown_section"][0], fields, "fixed_window")

    def test_rejects_schema_drift(self):
        chunks, _ = upload.prepare(REPO, True)
        fields = json.loads((AI_ROOT / "azure-search/sections.index.json").read_text())["fields"]
        with self.assertRaises(upload.CorpusError):
            upload.project(chunks["markdown_section"][0], fields[1:], "markdown_section")
        fields = copy.deepcopy(fields)
        fields[0]["type"] = "Edm.Boolean"
        with self.assertRaises(upload.CorpusError):
            upload.project(chunks["markdown_section"][0], fields, "markdown_section")


if __name__ == "__main__":
    unittest.main()
