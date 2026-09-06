"""Local contract tests; no model, cloud service, or reserved evaluation cases."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE.parents[1] / "runtime"))
import prepare_corpus as pc


class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.manifest = json.loads((REPO / pc.MANIFEST).read_text())
        for d in self.manifest["documents"]:
            target = self.root / d["source_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / d["source_path"], target)
        self.write_manifest()

    def write_manifest(self):
        target = self.root / pc.MANIFEST
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.manifest), encoding="utf-8")

    def test_draft_requires_explicit_local_mode(self):
        with self.assertRaises(pc.CorpusError):
            pc.prepare(self.root)

    def test_live_readiness_is_not_accepted(self):
        self.manifest["runtime_ready"] = True
        self.write_manifest()
        with self.assertRaises(pc.CorpusError):
            pc.prepare(self.root, True)

    def test_changed_source_rejected(self):
        path = self.root / self.manifest["documents"][0]["source_path"]
        path.write_bytes(path.read_bytes() + b"\nchanged\n")
        with self.assertRaisesRegex(pc.CorpusError, "hash mismatch"):
            pc.prepare(self.root, True)

    def test_missing_source_rejected(self):
        (self.root / self.manifest["documents"][0]["source_path"]).unlink()
        with self.assertRaises(OSError):
            pc.prepare(self.root, True)

    def test_duplicate_identity_rejected(self):
        self.manifest["documents"].append(copy.deepcopy(self.manifest["documents"][0]))
        self.write_manifest()
        with self.assertRaisesRegex(pc.CorpusError, "duplicate"):
            pc.prepare(self.root, True)

    def test_path_escape_rejected(self):
        for value in ("../outside.md", "/outside.md", "folder\\outside.md"):
            with self.subTest(value=value), self.assertRaises(pc.CorpusError):
                pc.contained(self.root, value)

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            (self.root / "outside").symlink_to(elsewhere, target_is_directory=True)
            with self.assertRaises(pc.CorpusError):
                pc.contained(self.root, "outside/file.md")

    def test_unpinned_citation_rejected(self):
        self.manifest["documents"][0]["source_url"] = "https://github.com/example/blob/main/file.md"
        self.write_manifest()
        with self.assertRaisesRegex(pc.CorpusError, "Citation"):
            pc.prepare(self.root, True)

    def test_complete_text_and_lineage_in_both_strategies(self):
        outputs, summary = pc.prepare(self.root, True)
        self.assertEqual(summary["document_count"], 3)
        for chunks in outputs.values():
            for doc in self.manifest["documents"]:
                raw = (self.root / doc["source_path"]).read_bytes().decode("utf-8")
                selected = [c for c in chunks if c["document_id"] == doc["document_id"]]
                covered = [False] * len(raw)
                for c in selected:
                    start, end = c["start_char"], c["end_char"]
                    self.assertEqual(c["text"], raw[start:end])
                    self.assertEqual(c["source_blob_sha"], doc["source_blob_sha"])
                    self.assertEqual(c["source_url"], doc["source_url"])
                    self.assertFalse(c["runtime_eligible"])
                    self.assertFalse(c["authorization_verified"])
                    self.assertTrue(c["source_sections"])
                    covered[start:end] = [True] * (end - start)
                self.assertTrue(all(covered))
                if selected[0]["chunking"]["strategy"] == "markdown_section":
                    self.assertEqual("".join(c["text"] for c in selected), raw)

    def test_ids_reproducible_and_strategy_specific(self):
        first, _ = pc.prepare(self.root, True)
        second, _ = pc.prepare(self.root, True)
        self.assertEqual(first, second)
        ids = [c["chunk_id"] for group in first.values() for c in group]
        self.assertEqual(len(ids), len(set(ids)))
        modified, _ = pc.prepare(self.root, True, 900, 100)
        self.assertNotEqual(first["fixed_window"][0]["chunk_id"], modified["fixed_window"][0]["chunk_id"])

    def test_fixed_overlap_edges_and_unicode(self):
        text = "é水" * 47
        ranges = list(pc.fixed_ranges(text, 20, 5))
        self.assertEqual(ranges[0], (0, 20))
        self.assertEqual(ranges[-1][1], len(text))
        for a, b in zip(ranges, ranges[1:]):
            self.assertEqual(a[1] - b[0], 5)
        for size, overlap in ((0, 0), (20, 20), (20, -1)):
            with self.assertRaises(pc.CorpusError):
                list(pc.fixed_ranges(text, size, overlap))

    def test_code_fences_do_not_create_sections(self):
        for delimiter in ("~~~", chr(96) * 3):
            text = "# Real\n\n" + delimiter + "\n# Fake\n\nx\n" + delimiter + "\n\n## Next\nBody\n"
            sections = pc.markdown_sections(text)
            self.assertEqual([s["path"][-1] for s in sections], ["Real", "Next"])
            self.assertEqual("".join(text[s["start"]:s["end"]] for s in sections), text)

    def test_recovery_table_and_state_preserved(self):
        outputs, _ = pc.prepare(self.root, True)
        recovery = [c for c in outputs["markdown_section"] if c["document_id"] == "northstar-recovery"]
        table = next(c for c in recovery if c["source_sections"][0]["section"] == "Select a pattern")
        self.assertIn("| Quality BLOCK |", table["text"])
        self.assertIn("| Quality-enforcement integrity breach |", table["text"])
        state = next(c for c in recovery if c["source_sections"][0]["section"] == "State")
        self.assertIn("candidate is committed only after acceptance", state["text"])
        self.assertEqual(state["source_sections"][0]["section_path"][-2:], ["Recovery verification", "State"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
