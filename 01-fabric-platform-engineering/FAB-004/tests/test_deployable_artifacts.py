import json
import re
import unittest
from pathlib import Path


FAB004_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = FAB004_ROOT / "workspace"


class DeployableArtifactTests(unittest.TestCase):
    def notebook(self, name):
        root = WORKSPACE_ROOT / f"{name}.Notebook"
        platform = json.loads((root / ".platform").read_text(encoding="utf-8"))
        content = (root / "notebook-content.py").read_text(encoding="utf-8")
        return platform, content

    def test_notebooks_are_deployable_fabric_items(self):
        for name in (
            "NB_FAB004_BenchmarkWorker",
            "NB_FAB004_BenchmarkOrchestrator",
        ):
            platform, content = self.notebook(name)
            self.assertEqual("Notebook", platform["metadata"]["type"])
            self.assertEqual(name, platform["metadata"]["displayName"])
            self.assertEqual("2.0", platform["config"]["version"])
            self.assertTrue(platform["config"]["logicalId"])
            self.assertIn("# Fabric notebook source", content)
            self.assertIn("# PARAMETERS CELL", content)

    def test_worker_enforces_synthetic_scale_and_replay_contract(self):
        _, content = self.notebook("NB_FAB004_BenchmarkWorker")
        self.assertIn("spark.range(0, rows_per_object", content)
        self.assertIn("rows_per_object <= 10_000_000", content)
        self.assertIn("Replay requires a seeded target.", content)
        self.assertIn("target.encounter_id = source.encounter_id", content)
        self.assertIn('"queue_seconds"', content)
        self.assertIn('"elapsed_seconds"', content)
        self.assertIn('"correctness_status"', content)

    def test_orchestrator_enforces_approved_alternatives_and_tiers(self):
        _, content = self.notebook("NB_FAB004_BenchmarkOrchestrator")
        self.assertIn('ALLOWED_ALTERNATIVES = {"SEQ1": 1, "PAR4": 4}', content)
        self.assertIn('"smoke": (1, 10_000)', content)
        self.assertIn('"standard": (4, 1_000_000)', content)
        self.assertIn('"large": (8, 10_000_000)', content)
        self.assertIn("notebookutils.notebook.runMultiple", content)
        self.assertIn('"capacity_sku": "F256"', content)

    def test_artifacts_do_not_embed_physical_identifiers(self):
        forbidden_patterns = (
            r"https://onelake\.dfs\.fabric\.microsoft\.com",
            r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}@",
            r"password\s*=",
            r"token\s*=",
        )
        for path in WORKSPACE_ROOT.rglob("*"):
            if path.is_file():
                content = path.read_text(encoding="utf-8").lower()
                for pattern in forbidden_patterns:
                    self.assertIsNone(re.search(pattern, content), f"{pattern} in {path}")


if __name__ == "__main__":
    unittest.main()
