"""Hostile receipt tests: a green string alone must never satisfy replay."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("capsule_replay", HERE / "replay_theorem_capsule_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class TheoremCapsuleReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payload = {"terminal": "FINITE_GREEN", "count": 2, "witness": [0, 1]}
        self.source = self.root / "grand_gmi_fixture_checks_v1.py"
        self.receipt = self.root / "FIXTURE_RECEIPT_V1.json"
        self.source.write_text("print(" + repr(json.dumps(self.payload)) + ")\n")
        self.receipt.write_text(json.dumps(self.payload))
        self.row = {
            "checker": self.source.name,
            "kind": "finite_check",
            "source_sha256": MOD.sha256(self.source),
            "receipt": self.receipt.name,
            "receipt_sha256": MOD.sha256(self.receipt),
            "terminal": self.payload["terminal"],
            "historical_receipts": [],
        }
        self.inventory = {
            "schema": MOD.SCHEMA,
            "claim_ceiling": MOD.CLAIM_CEILING,
            "checkers": [self.row],
            "control_sources": {},
            "inputs": {},
            "non_replayed_records": [],
        }
        self.save_inventory()

    def save_inventory(self):
        (self.root / MOD.INVENTORY).write_text(json.dumps(self.inventory))

    def replace_receipt(self, payload, update_hash=True):
        self.receipt.write_text(json.dumps(payload))
        if update_hash:
            self.row["receipt_sha256"] = MOD.sha256(self.receipt)
            self.save_inventory()

    def replace_source(self, text):
        self.source.write_text(text)
        self.row["source_sha256"] = MOD.sha256(self.source)
        self.save_inventory()

    def test_complete_fresh_payload_passes(self):
        result = MOD.replay(self.root)
        self.assertEqual(result["receipts"], 1)
        self.assertTrue(result["all_green"])
        self.assertEqual(len(result["fresh_payload_sha256"][self.source.name]), 64)

    def test_green_terminal_with_missing_changed_or_extra_witness_fails(self):
        for mutation in ({"terminal": "FINITE_GREEN"},
                         {**self.payload, "count": 999},
                         {**self.payload, "unproved_claim": True}):
            with self.subTest(mutation=mutation):
                self.replace_receipt(mutation)
                with self.assertRaisesRegex(MOD.ReplayError, "full receipt differs"):
                    MOD.replay(self.root)

    def test_unregistered_receipt_mutation_fails_before_replay(self):
        self.replace_receipt({**self.payload, "count": 999}, update_hash=False)
        with self.assertRaisesRegex(MOD.ReplayError, "evidence changed"):
            MOD.replay(self.root)

    def test_boolean_and_integer_are_not_equivalent_receipts(self):
        self.replace_receipt({**self.payload, "count": True})
        self.replace_source("print(" + repr(json.dumps({**self.payload, "count": 1})) + ")\n")
        with self.assertRaisesRegex(MOD.ReplayError, "full receipt differs"):
            MOD.replay(self.root)

    def test_changed_source_fails_even_when_stdout_would_match(self):
        self.source.write_text(self.source.read_text() + "# unreviewed source change\n")
        with self.assertRaisesRegex(MOD.ReplayError, "evidence changed"):
            MOD.replay(self.root)

    def test_ambient_stale_bytecode_cannot_replace_pinned_source(self):
        dependency = self.root / "dependency.py"
        dependency.write_text("VALUE = 2\n")
        original_stat = dependency.stat()
        py_compile.compile(str(dependency), doraise=True)
        # Preserve timestamp and size so Python's normal cache validation would
        # accept the old VALUE=2 bytecode despite the hash-bound VALUE=9 source.
        dependency.write_text("VALUE = 9\n")
        os.utime(dependency, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
        self.inventory["control_sources"][dependency.name] = MOD.sha256(dependency)
        self.replace_source(
            "from pathlib import Path\n"
            "from importlib.util import spec_from_file_location, module_from_spec\n"
            "spec = spec_from_file_location('dependency', Path(__file__).parent / 'dependency.py')\n"
            "module = module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
            "assert module.VALUE == 2, 'pinned source must execute'\n"
            "print(" + repr(json.dumps(self.payload)) + ")\n"
        )
        with self.assertRaisesRegex(MOD.ReplayError, "checker failed"):
            MOD.replay(self.root)

    def test_changed_registered_input_fails(self):
        dependency = self.root / "INPUT.json"
        dependency.write_text('{"bound": 1}')
        self.inventory["inputs"][dependency.name] = MOD.sha256(dependency)
        self.save_inventory()
        dependency.write_text('{"bound": 2}')
        with self.assertRaisesRegex(MOD.ReplayError, "evidence changed"):
            MOD.replay(self.root)

    def test_later_checker_cannot_mutate_an_already_verified_receipt(self):
        second_source = self.root / "grand_gmi_second_checks_v1.py"
        second_receipt = self.root / "SECOND_RECEIPT_V1.json"
        second_source.write_text(
            "from pathlib import Path\n"
            "Path('FIXTURE_RECEIPT_V1.json').write_text('{}')\n"
            "print(" + repr(json.dumps(self.payload)) + ")\n"
        )
        second_receipt.write_text(json.dumps(self.payload))
        second_row = copy.deepcopy(self.row)
        second_row.update(checker=second_source.name,
                          source_sha256=MOD.sha256(second_source),
                          receipt=second_receipt.name,
                          receipt_sha256=MOD.sha256(second_receipt))
        self.inventory["checkers"].append(second_row)
        self.save_inventory()
        with self.assertRaisesRegex(MOD.ReplayError, "evidence changed"):
            MOD.replay(self.root)

    def test_checker_inventory_cannot_silently_omit_or_duplicate_a_checker(self):
        self.inventory["checkers"].append(copy.deepcopy(self.row))
        self.save_inventory()
        with self.assertRaisesRegex(MOD.ReplayError, "duplicate checker"):
            MOD.replay(self.root)
        self.inventory["checkers"].pop()
        self.save_inventory()
        (self.root / "grand_gmi_unregistered_checks_v1.py").write_text("raise RuntimeError\n")
        with self.assertRaisesRegex(MOD.ReplayError, "checker coverage changed"):
            MOD.replay(self.root)

    def test_leaf_cannot_be_laundered_as_skipped_aggregate(self):
        self.row["kind"] = "aggregate"
        self.save_inventory()
        with self.assertRaisesRegex(MOD.ReplayError, "only the master"):
            MOD.replay(self.root, include_aggregate=False)

    def test_unclassified_receipt_and_input_are_rejected(self):
        extra = self.root / "EXTRA_RECEIPT_V1.json"
        extra.write_text("{}")
        with self.assertRaisesRegex(MOD.ReplayError, "unclassified or missing frozen receipt"):
            MOD.replay(self.root)
        extra.unlink()
        (self.root / "UNREGISTERED_INPUT.json").write_text("{}")
        with self.assertRaisesRegex(MOD.ReplayError, "unclassified or missing local document/JSON input"):
            MOD.replay(self.root)

    def test_theorem_document_change_fails_even_when_stdout_is_unchanged(self):
        document = self.root / "THEOREM.md"
        document.write_text("The finite bound is 2.\n")
        self.inventory["inputs"][document.name] = MOD.sha256(document)
        self.save_inventory()
        self.assertTrue(MOD.replay(self.root)["all_green"])
        document.write_text("The finite bound is 999.\n")
        with self.assertRaisesRegex(MOD.ReplayError, "evidence changed"):
            MOD.replay(self.root)

    def test_external_normative_dependency_must_be_registered_and_unchanged(self):
        repository = self.root / "repository"
        capsule = repository / "research/gmi-grand-unification-v1"
        capsule.mkdir(parents=True)
        checker = "grand_gmi_operational_reachability_checks_v1.py"
        (capsule / checker).write_bytes(self.source.read_bytes())
        (capsule / self.receipt.name).write_bytes(self.receipt.read_bytes())
        inventory = copy.deepcopy(self.inventory)
        inventory["checkers"][0]["checker"] = checker
        dependency = MOD.EXTERNAL_DOCUMENT_DEPENDENCIES[checker][0]
        document = repository / dependency
        document.parent.mkdir(parents=True)
        document.write_text("The reachable frontier is conditional.\n")
        inventory_path = capsule / MOD.INVENTORY
        inventory_path.write_text(json.dumps(inventory))
        with self.assertRaisesRegex(MOD.ReplayError, "missing external normative"):
            MOD.replay(capsule)
        inventory["external_documents"] = {dependency: MOD.sha256(document)}
        inventory_path.write_text(json.dumps(inventory))
        self.assertTrue(MOD.replay(capsule)["all_green"])
        document.write_text("Every frontier point is always reachable.\n")
        with self.assertRaisesRegex(MOD.ReplayError, "evidence changed"):
            MOD.replay(capsule)

    def test_external_workflow_must_be_registered_and_unchanged(self):
        repository = self.root / "repository"
        capsule = repository / "research/gmi-grand-unification-v1"
        capsule.mkdir(parents=True)
        (capsule / self.source.name).write_bytes(self.source.read_bytes())
        (capsule / self.receipt.name).write_bytes(self.receipt.read_bytes())
        control = capsule / "nn_nonnn_point_parity3_experiment_v1.py"
        control.write_text("# Registered historical experiment control.\n")
        inventory = copy.deepcopy(self.inventory)
        inventory["control_sources"][control.name] = MOD.sha256(control)
        workflow_name = MOD.EXTERNAL_CONTROL_DEPENDENCIES[control.name][0]
        workflow = repository / workflow_name
        workflow.parent.mkdir(parents=True)
        workflow.write_text("name: historical experiment\non: workflow_dispatch\n")
        inventory_path = capsule / MOD.INVENTORY
        inventory_path.write_text(json.dumps(inventory))
        with self.assertRaisesRegex(MOD.ReplayError, "missing external control workflow"):
            MOD.replay(capsule)
        inventory["external_controls"] = {workflow_name: MOD.sha256(workflow)}
        inventory_path.write_text(json.dumps(inventory))
        self.assertTrue(MOD.replay(capsule)["all_green"])
        workflow.write_text("name: silently changed experiment\non: push\n")
        with self.assertRaisesRegex(MOD.ReplayError, "evidence changed"):
            MOD.replay(capsule)

    def test_duplicate_keys_and_nonfinite_json_are_rejected(self):
        for text in ('{"terminal":"BAD","terminal":"FINITE_GREEN"}',
                     '{"value":NaN}', '{"value":Infinity}', '{"value":1e999}'):
            with self.subTest(text=text), self.assertRaises(MOD.ReplayError):
                MOD.strict_json(text)

    def test_duplicate_key_stdout_is_rejected_even_if_last_key_is_green(self):
        self.replace_source('print(\'{"terminal":"BAD","terminal":"FINITE_GREEN"}\')\n')
        with self.assertRaisesRegex(MOD.ReplayError, "duplicate key"):
            MOD.replay(self.root)

    def test_nonzero_exit_cannot_launder_green_stdout(self):
        self.replace_source(self.source.read_text() + "raise SystemExit(7)\n")
        with self.assertRaisesRegex(MOD.ReplayError, "exit 7"):
            MOD.replay(self.root)

    def test_optimized_environment_does_not_disable_checker_assertions(self):
        self.replace_source("assert False, 'must execute'\n" + self.source.read_text())
        with patch.dict(os.environ, {"PYTHONOPTIMIZE": "2"}):
            with self.assertRaisesRegex(MOD.ReplayError, "checker failed"):
                MOD.replay(self.root)

    def test_timeout_is_failure(self):
        self.replace_source("import time\ntime.sleep(1)\n" + self.source.read_text())
        with self.assertRaisesRegex(MOD.ReplayError, "did not complete"):
            MOD.execute_checker(self.root, self.row, timeout=0.03)

    def test_superseded_receipt_is_explicit_and_still_immutable(self):
        old = self.root / "OLD_RECEIPT_V1.json"
        old.write_text('{"terminal":"FINITE_GREEN","count":999}')
        self.row["historical_receipts"].append({
            "path": old.name, "sha256": MOD.sha256(old),
            "status": "HISTORICAL_SUPERSEDED_FOR_REPLAY",
            "reason": "Historical count differs from current executable witness.",
        })
        self.save_inventory()
        self.assertTrue(MOD.replay(self.root)["all_green"])
        old.write_text("{}")
        with self.assertRaisesRegex(MOD.ReplayError, "evidence changed"):
            MOD.replay(self.root)

    def test_missing_historical_classification_is_rejected(self):
        self.row["historical_receipts"] = [{"path": "old.json"}]
        self.save_inventory()
        with self.assertRaisesRegex(MOD.ReplayError, "supersession reason"):
            MOD.replay(self.root)

    def test_preregistration_classification_describes_record_not_execution_history(self):
        receipt = self.root / "PREREG_RECEIPT_V1.json"
        payload = {
            "terminal": "GRAND_GMI_NN_NONNN_POINT_PARITY3_PREREGISTRATION_FROZEN",
            "protected_resource_measurement_executed_in_frozen_receipt": False,
        }
        receipt.write_text(json.dumps(payload))
        row = {"path": receipt.name, "sha256": MOD.sha256(receipt),
               "status": "PREREGISTRATION_ONLY_NOT_MEASUREMENT",
               "reason": "This registration record is separate from historical executed packets."}
        self.inventory["non_replayed_records"].append(row)
        self.save_inventory()
        self.assertTrue(MOD.replay(self.root)["all_green"])
        payload["protected_resource_measurement_executed"] = True
        receipt.write_text(json.dumps(payload))
        row["sha256"] = MOD.sha256(receipt)
        self.save_inventory()
        with self.assertRaisesRegex(MOD.ReplayError, "not a preregistration-only receipt"):
            MOD.replay(self.root)

    def test_path_escape_is_rejected(self):
        for name in ("../outside.py", "/tmp/outside.py", "./inside.py"):
            with self.subTest(name=name), self.assertRaises(MOD.ReplayError):
                MOD.file_path(self.root, name)


if __name__ == "__main__":
    unittest.main()
