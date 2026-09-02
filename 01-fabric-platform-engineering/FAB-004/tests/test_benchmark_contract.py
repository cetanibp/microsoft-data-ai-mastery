import importlib.util
import copy
import unittest
from pathlib import Path


FAB004_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = FAB004_ROOT / "runtime" / "benchmark_contract.py"
SPEC = importlib.util.spec_from_file_location("benchmark_contract", MODULE_PATH)
benchmark_contract = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(benchmark_contract)


class BenchmarkContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = benchmark_contract.load_manifest(
            FAB004_ROOT / "config" / "workloads.json"
        )

    def test_manifest_is_valid(self):
        self.assertEqual([], benchmark_contract.validate_manifest(self.manifest))

    def test_declared_totals_are_representative(self):
        self.assertEqual(10_000, benchmark_contract.tier_total_rows(self.manifest, "smoke"))
        self.assertEqual(
            4_000_000,
            benchmark_contract.tier_total_rows(self.manifest, "standard"),
        )
        self.assertEqual(
            80_000_000,
            benchmark_contract.tier_total_rows(self.manifest, "large"),
        )

    def test_cost_allocation_uses_f256_denominator(self):
        self.assertAlmostEqual(
            10.0,
            benchmark_contract.allocated_cost_usd(256 * 3600, 10.0),
        )

    def test_cost_inputs_cannot_be_negative(self):
        with self.assertRaises(ValueError):
            benchmark_contract.allocated_cost_usd(-1, 10.0)

    def test_threshold_drift_is_rejected(self):
        changed = copy.deepcopy(self.manifest)
        changed["decision_thresholds"]["minimum_elapsed_improvement_pct"] = 0
        errors = benchmark_contract.validate_manifest(changed)
        self.assertIn(
            "decision threshold minimum_elapsed_improvement_pct must equal 15",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
