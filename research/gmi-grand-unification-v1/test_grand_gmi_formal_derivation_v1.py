"""Complete formal supplement, preserved source audit and live-theorem custody."""
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
WRAPPER = "grand_gmi_formal_derivation_checks_v1.py"
CODE = runpy.run_path(str(HERE / WRAPPER))
UNIT, AUDIT, LIVE = CODE["UNIT"], CODE["AUDIT"], CODE["LIVE_THEOREM"]
RECEIPT = "GRAND_GMI_FORMAL_DERIVATION_RECEIPT_V1.json"


class FormalDerivationCapsuleTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repository = Path(tmp.name)
        self.root = self.repository / "research/gmi-grand-unification-v1"
        self.root.mkdir(parents=True)
        for name in (UNIT, AUDIT):
            shutil.copytree(HERE.parent.parent / name, self.repository / name)
        self.documents = GATE["EXTERNAL_DOCUMENT_DEPENDENCIES"][WRAPPER]
        self.controls = GATE["EXTERNAL_CONTROL_DEPENDENCIES"][WRAPPER]
        for name in (*self.documents, *self.controls):
            target = self.repository / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(HERE.parent.parent / name, target)
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
                          "external_documents": {n: GATE["sha256"](self.repository/n) for n in self.documents},
                          "external_controls": {n: GATE["sha256"](self.repository/n) for n in self.controls},
                          "external_units": {name: {"manifest": "MANIFEST_V1.json",
                            "sha256": GATE["sha256"](self.repository/name/"MANIFEST_V1.json")}
                            for name in (UNIT, AUDIT)}}
        self.save()

    def save(self):
        (self.root / GATE["INVENTORY"]).write_text(json.dumps(self.inventory))

    def test_actual_wrapper_preserves_every_original_field(self):
        run = subprocess.run([sys.executable, "-I", "-B", str(HERE / WRAPPER)], capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr.decode(errors="replace"))
        self.assertEqual(run.stderr, b"")
        self.assertEqual(run.stdout, (HERE / RECEIPT).read_bytes())
        actual = json.loads(run.stdout)
        original = json.loads((HERE.parent.parent / UNIT / "RECEIPT_V1.json").read_text())
        self.assertEqual(GATE["canonical"](actual["original_payload"]), GATE["canonical"](original))
        self.assertEqual(set(actual["external_units"]), {UNIT, AUDIT})
        self.assertEqual(actual["corrected_live_theorem"][LIVE], GATE["sha256"](HERE.parent.parent / LIVE))

    def test_checked_status_cannot_hide_changed_witness_count(self):
        original = json.loads((HERE.parent.parent / UNIT / "RECEIPT_V1.json").read_text())
        self.assertEqual(original["status"], "CHECKED")
        original["tests_run"] -= 1
        fake = SimpleNamespace(returncode=0, stderr="", stdout=json.dumps(original))
        with patch("subprocess.run", return_value=fake), self.assertRaisesRegex(ValueError, "complete original.*differs"):
            CODE["run"]()

    def test_original_test_identity_projection_is_rejected(self):
        original = json.loads((HERE.parent.parent / UNIT / "RECEIPT_V1.json").read_text())
        del original["tests"]
        fake = SimpleNamespace(returncode=0, stderr="", stdout=json.dumps(original))
        with patch("subprocess.run", return_value=fake), self.assertRaisesRegex(ValueError, "complete original.*differs"):
            CODE["run"]()

    def test_complete_real_units_and_live_fixture_have_no_alarm(self):
        self.assertTrue(GATE["replay"](self.root)["all_green"])

    def test_omitted_or_renamed_unit_dependencies_are_rejected(self):
        correct = copy.deepcopy(self.inventory["external_units"])
        for bad in ({UNIT: correct[UNIT]}, {**correct, "research/unknown": correct[AUDIT]}):
            self.inventory["external_units"] = bad
            self.save()
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "missing external research"):
                GATE["load_inventory"](self.root)

    def test_changed_formal_proof_and_missing_freeze_are_rejected(self):
        target = self.repository / UNIT / "AXIOMS.md"
        original = target.read_bytes()
        target.write_bytes(original + b"changed axiom")
        with self.assertRaisesRegex(ValueError, "content changed"):
            GATE["load_inventory"](self.root)
        target.write_bytes(original)
        (self.repository / UNIT / "FREEZE.json").unlink()
        with self.assertRaisesRegex(ValueError, "membership changed"):
            GATE["load_inventory"](self.root)

    def test_changed_original_upstream_theorem_is_rejected(self):
        target = self.repository / AUDIT / "raw/main/GLOBAL_ADAPTIVE_COMPOSITION_THEOREM_V1.md"
        target.write_bytes(target.read_bytes() + b"rewritten history")
        with self.assertRaisesRegex(ValueError, "content changed"):
            GATE["load_inventory"](self.root)

    def test_omitted_or_changed_corrected_live_theorem_is_rejected(self):
        original = self.inventory["external_documents"].pop(LIVE)
        self.save()
        with self.assertRaisesRegex(ValueError, "missing external normative"):
            GATE["load_inventory"](self.root)
        self.inventory["external_documents"][LIVE] = original
        self.save()
        target = self.repository / LIVE
        target.write_bytes(target.read_bytes() + b"changed induction premise")
        with self.assertRaisesRegex(ValueError, "source or evidence changed"):
            GATE["load_inventory"](self.root)

    def test_later_checker_cannot_mutate_the_bound_live_theorem(self):
        source = self.root / "grand_gmi_z_later_checks_v1.py"
        source.write_text("from pathlib import Path\np = Path(" + repr(str(self.repository / LIVE)) +
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

    def test_learning_memory_sources_match_the_actual_validation_receipt(self):
        prefix = "research/gmi-recursive-theory-closure-v1/"
        receipt = json.loads((self.repository / prefix / "LEARNING_MEMORY_REPAIR_RECEIPT_V1.json").read_text())
        for name, row in receipt["source_files"].items():
            path = self.repository / prefix / name
            self.assertEqual(GATE["sha256"](path), row["sha256"])
            self.assertEqual(path.stat().st_size, row["bytes"])
            self.assertIn(prefix + name, (*self.documents, *self.controls))
        for name, row in receipt["historical_source_files"].items():
            path = self.repository / AUDIT / "raw/open568" / name
            self.assertEqual(GATE["sha256"](path), row["sha256"])

    def test_changed_learning_memory_helper_is_rejected(self):
        target = self.repository / "research/gmi-recursive-theory-closure-v1/learning_memory_models_v1.py"
        target.write_bytes(target.read_bytes() + b"changed decoder contract")
        with self.assertRaisesRegex(ValueError, "source or evidence changed"):
            GATE["load_inventory"](self.root)

    def test_workflow_executes_both_modes_and_all_new_paths(self):
        text = (HERE.parent.parent / ".github/workflows/grand-gmi-theorem-capsule.yml").read_text()
        for name in (UNIT + "/**", AUDIT + "/**", "research/gmi-recursive-theory-closure-v1/**"):
            self.assertEqual(text.count("'" + name + "'"), 2)
        for flags in ("-I -B", "-I -O -B"):
            for source in ("verify_unit.py", "verify_controls.py"):
                self.assertIn("python " + flags + " " + UNIT + "/" + source, text)
            self.assertIn("python " + flags + " research/gmi-recursive-theory-closure-v1/test_global_adaptive_composition_v1.py", text)
            self.assertIn("python " + flags + " -m unittest discover -s research/gmi-recursive-theory-closure-v1 -p 'test_learning_memory*.py' -v", text)
        self.assertIn("timeout-minutes: 30", text)


if __name__ == "__main__":
    unittest.main()
