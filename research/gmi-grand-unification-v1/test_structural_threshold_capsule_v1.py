"""STR capsule integration, including mutation after the first entry succeeds."""
from pathlib import Path
import copy
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
GATE = runpy.run_path(str(HERE / "replay_theorem_capsule_v1.py"))
WRAPPER = "grand_gmi_structural_neural_bound_checks_v1.py"
UNIT = "research/gmi-structural-threshold-repair-v1"
SHA = "e55db0c72cb0d57c918727a4f252f39ade18e8716c4db8e31861f25371a1e8ad"


class StructuralThresholdCapsuleTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repository = Path(tmp.name)
        self.root = self.repository / "research/gmi-grand-unification-v1"
        self.root.mkdir(parents=True)
        shutil.copytree(HERE.parent.parent / UNIT, self.repository / UNIT)
        shutil.copy2(HERE / "external_unit_bindings_v1.py", self.root)
        self.payload = {"terminal": "FIXTURE_GREEN", "witness": [0, 1]}
        self.source = self.root / WRAPPER
        self.source.write_text("print(" + repr(json.dumps(self.payload)) + ")\n")
        self.receipt = self.root / "FIXTURE_RECEIPT_V1.json"
        self.receipt.write_text(json.dumps(self.payload))
        self.row = {"checker": WRAPPER, "kind": "finite_check",
                    "source_sha256": GATE["sha256"](self.source),
                    "receipt": self.receipt.name, "receipt_sha256": GATE["sha256"](self.receipt),
                    "terminal": self.payload["terminal"], "historical_receipts": []}
        self.inventory = {"schema": GATE["SCHEMA"], "claim_ceiling": GATE["CLAIM_CEILING"],
                          "checkers": [self.row], "inputs": {}, "non_replayed_records": [],
                          "control_sources": {"external_unit_bindings_v1.py":
                                              GATE["sha256"](self.root / "external_unit_bindings_v1.py")},
                          "external_units": {UNIT: {"manifest": "MANIFEST.json", "sha256": SHA}}}
        self.save()

    def save(self):
        (self.root / GATE["INVENTORY"]).write_text(json.dumps(self.inventory))

    def test_actual_adapter_preserves_complete_sn_v2_and_standalone_receipt(self):
        result = subprocess.run([sys.executable, "-I", "-B", str(HERE / WRAPPER)],
                                capture_output=True, check=True, timeout=60)
        self.assertEqual(result.stderr, b"")
        frozen = (HERE / "GRAND_GMI_STRUCTURAL_NEURAL_BOUND_RECEIPT_V2.json").read_bytes()
        standalone = (HERE.parent.parent / UNIT / "STRUCTURAL_THRESHOLD_REPAIR_RECEIPT_V1.json").read_bytes()
        self.assertEqual(result.stdout, frozen)
        self.assertEqual(result.stdout, standalone)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["runtime_patch_identity_claim"])
        self.assertFalse(payload["general_neural_or_delegating_family_exclusion"])
        self.assertEqual(payload["attainment"]["minimum_per_sweep"], 312)

    def test_capsule_rejects_projection_of_full_checker_payload(self):
        self.source.write_text("print(" + repr(json.dumps({"terminal": self.payload["terminal"]})) + ")\n")
        self.inventory["checkers"][0]["source_sha256"] = GATE["sha256"](self.source)
        self.save()
        with self.assertRaisesRegex(ValueError, "full receipt differs"):
            GATE["replay"](self.root)

    def test_complete_external_unit_fixture_has_no_alarm(self):
        self.assertTrue(GATE["replay"](self.root)["all_green"])

    def test_missing_unknown_and_renamed_dependencies_are_rejected(self):
        correct = copy.deepcopy(self.inventory["external_units"])
        for bad in ({}, {"research/unknown": correct[UNIT]}, {**correct, "extra": correct[UNIT]}):
            self.inventory["external_units"] = bad
            self.save()
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "missing external research"):
                GATE["load_inventory"](self.root)

    def test_required_helper_must_be_registered_and_source_bound(self):
        helper = self.root / "external_unit_bindings_v1.py"
        helper.write_text(helper.read_text() + "\n# unreviewed edit\n")
        with self.assertRaisesRegex(ValueError, "evidence changed"):
            GATE["load_inventory"](self.root)
        helper.unlink()
        self.inventory["control_sources"] = {}
        self.save()
        with self.assertRaisesRegex(ValueError, "bad digest"):
            GATE["load_inventory"](self.root)

    def test_cached_module_cannot_bypass_fresh_complete_unit_check(self):
        GATE["load_inventory"](self.root)
        target = self.repository / UNIT / "raw/validation/tests-normal.log"
        target.write_bytes(target.read_bytes() + b"unreviewed")
        fake = SimpleNamespace(verify_unit=lambda *args: {})
        with patch.dict(sys.modules, {"external_unit_bindings_v1": fake}):
            with self.assertRaisesRegex(ValueError, "external research unit invalid"):
                GATE["load_inventory"](self.root)

    def test_later_checker_cannot_mutate_already_verified_external_input(self):
        source = self.root / "grand_gmi_z_later_checks_v1.py"
        target = self.repository / UNIT / "raw/STRUCTURAL_NEURAL_BOUND_THEOREM_V1.md"
        source.write_text("from pathlib import Path\n"
                          + "p = Path(" + repr(str(target)) + ")\n"
                          + "p.write_bytes(p.read_bytes() + b'changed later')\n"
                          + "print(" + repr(json.dumps(self.payload)) + ")\n")
        receipt = self.root / "LATER_RECEIPT_V1.json"
        receipt.write_text(json.dumps(self.payload))
        self.inventory["checkers"].append({**self.row, "checker": source.name,
                                          "source_sha256": GATE["sha256"](source),
                                          "receipt": receipt.name,
                                          "receipt_sha256": GATE["sha256"](receipt)})
        self.save()
        with self.assertRaisesRegex(ValueError, "external research unit invalid"):
            GATE["replay"](self.root)

    def test_workflow_triggers_cover_frozen_unit_and_its_tests(self):
        text = (HERE.parent.parent / ".github/workflows/grand-gmi-theorem-capsule.yml").read_text()
        self.assertEqual(text.count("'research/gmi-structural-threshold-repair-v1/**'"), 2)
        self.assertIn("python -I -B -m unittest discover -s research/gmi-structural-threshold-repair-v1 -p 'test_structural_threshold*_v1.py'", text)
        self.assertIn("python -I -O -B -m unittest discover -s research/gmi-structural-threshold-repair-v1 -p 'test_structural_threshold*_v1.py'", text)


if __name__ == "__main__":
    unittest.main()
