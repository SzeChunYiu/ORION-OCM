"""Standalone archive custody and full receipt replay; not copied into grand."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from structural_threshold_analytic_v1 import run
from structural_threshold_countercontrols_v1 import bounded_output_counterexample
from structural_threshold_packet_v1 import HERE, verify_sources


class StructuralThresholdPacketTests(unittest.TestCase):
    def test_original_five_files_match_frozen_source_bindings(self):
        self.assertEqual(verify_sources(), 5)

    def test_archive_mutation_rejects(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            shutil.copytree(HERE / "raw", target / "raw")
            shutil.copyfile(HERE / "SOURCE_PARENTS_V1.json", target / "SOURCE_PARENTS_V1.json")
            path = target / "raw/grand_gmi_structural_neural_bound_checks_v1.py"
            path.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "archived source changed"):
                verify_sources(target)

    def test_bound_old_checker_reproduces_actual_output_omission(self):
        verify_sources()
        name = HERE / "raw/grand_gmi_structural_neural_bound_checks_v1.py"
        namespace = {"__name__": "historical_finite_output_control"}
        exec(compile(name.read_bytes(), str(name), "exec"), namespace)
        _, table = namespace["output_threshold_table"](4)
        evidence = bounded_output_counterexample()
        self.assertEqual(len(table), evidence["bounded_output_functions"])
        self.assertNotIn(evidence["omitted_full_truth_table"], table)

    def test_full_frozen_receipt_matches_every_field(self):
        expected = json.loads((HERE / "STRUCTURAL_THRESHOLD_REPAIR_RECEIPT_V1.json").read_bytes())
        self.assertEqual(run(), expected)

    def test_isolated_relocation_keeps_full_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "copied"
            shutil.copytree(HERE, target)
            command = [sys.executable, "-I", "-B"] + (["-O"] if sys.flags.optimize else [])
            command += [str(target / "check_structural_threshold_repair_v1.py")]
            result = subprocess.run(command, cwd=temporary, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, (HERE / "STRUCTURAL_THRESHOLD_REPAIR_RECEIPT_V1.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
