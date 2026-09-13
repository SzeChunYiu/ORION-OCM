"""Whole NAR/delta custody, exact live exports and later-checker controls."""
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
WRAPPER = "grand_gmi_native_adjoint_checks_v1.py"
CODE = runpy.run_path(str(HERE / WRAPPER))
UNIT, DELTA = CODE["UNIT"], CODE["DELTA"]
RECEIPT = "GRAND_GMI_NATIVE_ADJOINT_RECEIPT_V1.json"


class NativeAdjointCapsuleTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repository = Path(tmp.name)
        self.root = self.repository / "research/gmi-grand-unification-v1"
        self.root.mkdir(parents=True)
        for name in (UNIT, DELTA):
            shutil.copytree(HERE.parent.parent / name, self.repository / name)
        mapping = json.loads((self.repository / UNIT / "ACTIVE_RUNTIME_BINDING_V1.json").read_text())["files"]
        for name in mapping:
            target = self.repository / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(HERE.parent.parent / name, target)
        self.vm = next(name for name in mapping if name.endswith("/vm.py"))
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
                          "external_controls": {name: row["sha256"] for name, row in mapping.items()},
                          "external_units": {name: {"manifest": "MANIFEST_V1.json",
                            "sha256": GATE["sha256"](self.repository / name / "MANIFEST_V1.json")}
                            for name in (UNIT, DELTA)}}
        self.save()

    def save(self):
        (self.root / GATE["INVENTORY"]).write_text(json.dumps(self.inventory))

    def test_actual_wrapper_preserves_complete_payload_and_live_mapping(self):
        run = subprocess.run([sys.executable, "-I", "-B", str(HERE / WRAPPER)], capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr.decode(errors="replace"))
        self.assertEqual(run.stderr, b"")
        self.assertEqual(run.stdout, (HERE / RECEIPT).read_bytes())
        actual = json.loads(run.stdout)
        original = json.loads((HERE.parent.parent / UNIT / "RECEIPT_V1.json").read_text())
        self.assertEqual(GATE["canonical"](actual["original_payload"]), GATE["canonical"](original))
        self.assertEqual(len(actual["active_runtime"]), 9)
        self.assertEqual(set(actual["external_units"]), {UNIT, DELTA})

    def test_pass_status_does_not_hide_changed_adjoint(self):
        original = json.loads((HERE.parent.parent / UNIT / "RECEIPT_V1.json").read_text())
        self.assertEqual(original["status"], "PASS")
        original["boundary_controls"]["saturation"]["registered_adjoint_fx"] = 0
        fake = SimpleNamespace(returncode=0, stderr="", stdout=json.dumps(original))
        with patch("subprocess.run", return_value=fake), self.assertRaisesRegex(ValueError, "complete original.*differs"):
            CODE["run"]()

    def test_original_field_projection_is_rejected(self):
        original = json.loads((HERE.parent.parent / UNIT / "RECEIPT_V1.json").read_text())
        del original["complete_historical_controls"]
        fake = SimpleNamespace(returncode=0, stderr="", stdout=json.dumps(original))
        with patch("subprocess.run", return_value=fake), self.assertRaisesRegex(ValueError, "complete original.*differs"):
            CODE["run"]()

    def test_complete_real_two_unit_and_live_fixture_has_no_alarm(self):
        self.assertEqual(len(CODE["live_bindings"](self.root, GATE, self.inventory)), 9)
        self.assertTrue(GATE["replay"](self.root)["all_green"])

    def test_missing_or_renamed_unit_is_rejected(self):
        good = copy.deepcopy(self.inventory["external_units"])
        for bad in ({UNIT: good[UNIT]}, {**good, "research/unknown": good[DELTA]}):
            self.inventory["external_units"] = bad
            self.save()
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "missing external research"):
                GATE["load_inventory"](self.root)

    def test_missing_live_mapping_entry_is_rejected(self):
        del self.inventory["external_controls"][self.vm]
        self.save()
        with self.assertRaisesRegex(ValueError, "missing external control"):
            GATE["load_inventory"](self.root)

    def test_changed_actual_live_vm_with_untouched_snapshot_is_rejected(self):
        path = self.repository / self.vm
        path.write_bytes(path.read_bytes() + b"unreviewed live change")
        with self.assertRaisesRegex(ValueError, "source or evidence changed"):
            GATE["load_inventory"](self.root)

    def test_rehashing_live_vm_cannot_replace_the_frozen_source_contract(self):
        path = self.repository / self.vm
        path.write_bytes(path.read_bytes() + b"unreviewed live change")
        self.inventory["external_controls"][self.vm] = GATE["sha256"](path)
        self.save()
        GATE["load_inventory"](self.root)
        with self.assertRaisesRegex(ValueError, "live runtime differs"):
            CODE["live_bindings"](self.root, GATE, self.inventory)

    def test_missing_and_symlink_live_source_are_rejected(self):
        path = self.repository / self.vm
        path.unlink()
        with self.assertRaisesRegex(ValueError, "missing file"):
            GATE["load_inventory"](self.root)
        path.symlink_to(HERE.parent.parent / self.vm)
        with self.assertRaisesRegex(ValueError, "symlink"):
            GATE["load_inventory"](self.root)

    def test_changed_delta_and_missing_original_audit_are_rejected(self):
        target = self.repository / DELTA / "PR551_DELTA_CORRECTION_08821A0A_V1.md"
        original = target.read_bytes()
        target.write_bytes(original + b"changed claim")
        with self.assertRaisesRegex(ValueError, "content changed"):
            GATE["load_inventory"](self.root)
        target.write_bytes(original)
        (self.repository / UNIT / "raw/pr551-grad-audit-20260913/GRAD_SIDE_EFFECT_CONTROL_V1.json").unlink()
        with self.assertRaisesRegex(ValueError, "membership changed"):
            GATE["load_inventory"](self.root)

    def test_later_checker_cannot_mutate_an_already_checked_live_vm(self):
        source = self.root / "grand_gmi_z_later_checks_v1.py"
        source.write_text("from pathlib import Path\np = Path(" + repr(str(self.repository / self.vm)) +
                          ")\np.write_bytes(p.read_bytes() + b'changed later')\nprint(" +
                          repr(json.dumps(self.payload)) + ")\n")
        receipt = self.root / "LATER_RECEIPT_V1.json"
        receipt.write_text(json.dumps(self.payload))
        self.inventory["checkers"].append({**self.row, "checker": source.name,
            "source_sha256": GATE["sha256"](source), "receipt": receipt.name,
            "receipt_sha256": GATE["sha256"](receipt)})
        self.save()
        with self.assertRaisesRegex(ValueError, "source or evidence changed"):
            GATE["replay"](self.root)

    def test_workflow_covers_both_units_and_all_nine_live_dependencies(self):
        text = (HERE.parent.parent / ".github/workflows/grand-gmi-theorem-capsule.yml").read_text()
        for name in (UNIT + "/**", DELTA + "/**", *self.inventory["external_controls"]):
            self.assertEqual(text.count("'" + name + "'"), 2)
        for flags in ("-I -B", "-I -O -B"):
            self.assertIn("python " + flags + " -m unittest discover -s " + UNIT + " -p 'test_*v1.py' -v", text)
            self.assertIn("python " + flags + " " + CODE["PREFIX"] + "test_gmi_vm_parameter_adjoint_v1.py", text)
        self.assertIn("timeout-minutes: 30", text)


if __name__ == "__main__":
    unittest.main()
