"""Complete DCR delegation packet/wrapper custody and later-checker mutation controls."""
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
WRAPPER = "grand_gmi_delegation_cost_checks_v1.py"
UNIT = "research/gmi-delegation-cost-repair-v1"
SHA = "24a0b78ce8a7650a0873831c4c39f9794a1589b9f0f76d2c9e0e2386157b5702"


class DelegationCostCapsuleTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repository = Path(tmp.name)
        self.root = self.repository / "research/gmi-grand-unification-v1"
        self.root.mkdir(parents=True)
        shutil.copytree(HERE.parent.parent / UNIT, self.repository / UNIT)
        shutil.copy2(HERE / "external_unit_bindings_v1.py", self.root)
        self.payload = {"terminal": "FIXTURE_GREEN", "witness": [0, 1]}
        source = self.root / WRAPPER
        source.write_text("print(" + repr(json.dumps(self.payload)) + ")\n")
        receipt = self.root / "FIXTURE_RECEIPT_V1.json"
        receipt.write_text(json.dumps(self.payload))
        self.row = {"checker": WRAPPER, "kind": "finite_check",
                    "source_sha256": GATE["sha256"](source),
                    "receipt": receipt.name, "receipt_sha256": GATE["sha256"](receipt),
                    "terminal": self.payload["terminal"], "historical_receipts": []}
        self.inventory = {"schema": GATE["SCHEMA"], "claim_ceiling": GATE["CLAIM_CEILING"],
                          "checkers": [self.row], "inputs": {}, "non_replayed_records": [],
                          "control_sources": {"external_unit_bindings_v1.py":
                                              GATE["sha256"](self.root / "external_unit_bindings_v1.py")},
                          "external_units": {UNIT: {"manifest": "MANIFEST_V1.json", "sha256": SHA}}}
        self.save()

    def save(self):
        (self.root / GATE["INVENTORY"]).write_text(json.dumps(self.inventory))

    def test_actual_wrapper_preserves_the_complete_original_payload(self):
        result = subprocess.run([sys.executable, "-I", "-B", str(HERE / WRAPPER)],
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stderr, b"")
        expected = (HERE / "GRAND_GMI_DELEGATION_COST_RECEIPT_V1.json").read_bytes()
        self.assertEqual(result.stdout, expected)
        original = json.loads((HERE.parent.parent / UNIT / "RECEIPT_V1.json").read_text())
        self.assertEqual(GATE["canonical"](json.loads(result.stdout)["original_payload"]),
                         GATE["canonical"](original))
        self.assertEqual(set(json.loads(result.stdout)["original_payload"]), set(original))

    def test_pass_status_cannot_hide_an_altered_parent_cost(self):
        wrapper = runpy.run_path(str(HERE / WRAPPER))
        original = json.loads((HERE.parent.parent / UNIT / "RECEIPT_V1.json").read_text())
        self.assertEqual(original["status"], "PASS")
        original["rows"]["WRITTEN_SHARED_SUM_NET"]["python_opcodes_per_sweep"] = 1
        fake = SimpleNamespace(returncode=0, stderr="", stdout=json.dumps(original))
        with patch("subprocess.run", return_value=fake):
            with self.assertRaisesRegex(ValueError, "complete original.*differs"):
                wrapper["run"]()

    def test_original_field_projection_is_rejected(self):
        wrapper = runpy.run_path(str(HERE / WRAPPER))
        original = json.loads((HERE.parent.parent / UNIT / "RECEIPT_V1.json").read_text())
        del original["wrapper_refinement"]
        fake = SimpleNamespace(returncode=0, stderr="", stdout=json.dumps(original))
        with patch("subprocess.run", return_value=fake):
            with self.assertRaisesRegex(ValueError, "complete original.*differs"):
                wrapper["run"]()

    def test_complete_real_unit_fixture_has_no_alarm(self):
        self.assertTrue(GATE["replay"](self.root)["all_green"])

    def test_omitted_and_renamed_unit_dependencies_are_rejected(self):
        correct = copy.deepcopy(self.inventory["external_units"])
        for bad in ({}, {"research/unknown": correct[UNIT]}):
            self.inventory["external_units"] = bad
            self.save()
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "missing external research"):
                GATE["load_inventory"](self.root)

    def test_changed_typed_evaluator_is_rejected(self):
        target = self.repository / UNIT / "typed_machine_v1.py"
        target.write_bytes(target.read_bytes() + b"unreviewed trace")
        with self.assertRaisesRegex(ValueError, "content changed"):
            GATE["load_inventory"](self.root)

    def test_missing_historical_parent_is_rejected(self):
        (self.repository / UNIT / "raw/grand_gmi_delegation_invariant_cost_checks_v1.py").unlink()
        with self.assertRaisesRegex(ValueError, "membership changed"):
            GATE["load_inventory"](self.root)

    def test_later_checker_cannot_mutate_an_already_checked_external_parent(self):
        source = self.root / "grand_gmi_z_later_checks_v1.py"
        target = self.repository / UNIT / "independent_oracle_v1.py"
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

    def test_workflow_covers_frozen_tests_in_isolated_processes(self):
        text = (HERE.parent.parent / ".github/workflows/grand-gmi-theorem-capsule.yml").read_text()
        self.assertEqual(text.count("'research/gmi-delegation-cost-repair-v1/**'"), 2)
        for flags in ("-I -B", "-I -O -B"):
            self.assertIn("python " + flags + " -m unittest discover -s " + UNIT + " -p 'test_*v1.py' -v", text)
            self.assertIn("python " + flags + " " + UNIT + "/raw/test_grand_gmi_delegation_invariant_cost_v1.py", text)
        self.assertIn("timeout-minutes: 30", text)


    def test_original_positive_receipt_and_raw_sources_remain_historical(self):
        inventory = GATE["load_inventory"](HERE)
        row = next(x for x in inventory["checkers"] if x["checker"] == WRAPPER)
        name = "GRAND_GMI_DELEGATION_INVARIANT_COST_RECEIPT_V1.json"
        old = next(x for x in row["historical_receipts"] if x["path"] == name)
        self.assertEqual(old["sha256"], "c1510bc8acacb358e5031c3782ee07fe3113b8cd586eb45ea363fb761ea7dd94")
        self.assertEqual((HERE / name).read_bytes(), (HERE.parent.parent / UNIT / "raw" / name).read_bytes())
        for source in ("grand_gmi_delegation_invariant_cost_checks_v1.py",
                       "test_grand_gmi_delegation_invariant_cost_v1.py"):
            self.assertFalse((HERE / source).exists())
            self.assertTrue((HERE.parent.parent / UNIT / "raw" / source).is_file())


if __name__ == "__main__":
    unittest.main()
