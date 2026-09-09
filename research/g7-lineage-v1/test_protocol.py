"""Hostile protocol tests for the G7 persistent lineage microscope."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC_L = importlib.util.spec_from_file_location("g7_lineage", HERE / "lineage.py")
L = importlib.util.module_from_spec(SPEC_L)
SPEC_L.loader.exec_module(L)
SPEC_E = importlib.util.spec_from_file_location("g7_experiment", HERE / "experiment.py")
E = importlib.util.module_from_spec(SPEC_E)
SPEC_E.loader.exec_module(E)


class TestG7LineageProtocol(unittest.TestCase):
    def test_schema_requires_every_transition_field(self):
        schema = L.load_schema()
        required = set(schema["required"])
        expected = {
            "schema", "lineage_id", "source_stage", "target_stage",
            "source_machine_identity", "target_machine_identity",
            "persistent_state_digest", "imported_donor_identities",
            "prior_information_manifest", "new_information_supplied",
            "new_methods_schemas", "reused_method_identities",
            "actual_execution_witnesses", "primitive_operators_added",
            "composition_depth", "acquisition_cost", "reasoning_cost",
            "verification_cost", "revision_cost", "self_change_cost",
            "maintenance_cost", "persistent_bytes", "active_k_n",
            "kappa", "omega", "chi", "retention", "negative_transfer",
            "ablation", "strongest_parent_result", "terminal",
        }
        self.assertEqual(required, expected)
        parent_required = set(schema["properties"]["strongest_parent_result"]["required"])
        self.assertEqual(
            parent_required,
            {
                "CONTINUED_OCM", "RESET_OCM", "TASK_SPECIFIC_OCM",
                "STRONG_ADAPTIVE_PARENT", "reset_costs_more_or_fails_reuse",
                "parent_ties_continued_mechanism", "winner", "notes",
            },
        )

    def test_empty_bundle_has_all_persist_slots_and_taught_donors(self):
        bundle = L.empty_bundle()
        for slot in L.PERSIST_SLOTS:
            self.assertIn(slot, bundle)
        donors = bundle["imported_donors"]
        self.assertEqual(len(donors), 4)
        self.assertTrue(all(d["origin_category"] == L.ORIGIN_TAUGHT for d in donors))
        self.assertEqual(bundle["lineage_id"], L.LINEAGE_ID)
        self.assertEqual(bundle["stage"], "EMPTY")

    def test_tampered_digest_fails_closed(self):
        bundle = L.empty_bundle()
        with tempfile.TemporaryDirectory() as temp:
            store = L.LineageStore(Path(temp) / "continued", "CONTINUED_OCM")
            store.persist(bundle)
            path = store.root / L.BUNDLE_FILE
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["bundle"]["field_state"]["notes"] = "tampered"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(L.DigestTamperError):
                store.load()
            payload["digest"] = "0" * 64
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(L.DigestTamperError):
                store.load()

    def test_reset_store_cannot_see_continued_files(self):
        bundle = L.empty_bundle()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            continued = L.LineageStore(root / "continued", "CONTINUED_OCM")
            reset = L.LineageStore(root / "reset", "RESET_OCM")
            continued.persist(bundle)
            L.assert_disjoint_stores(continued, reset)
            with self.assertRaises(FileNotFoundError):
                reset.load()
            with self.assertRaises(L.IsolationError):
                reset._inside(continued.root / L.BUNDLE_FILE)
            nested = L.LineageStore(root / "reset-ok", "RESET_OCM")
            with self.assertRaises(L.IsolationError):
                L.assert_disjoint_stores(continued, L.LineageStore(continued.root / "nested", "RESET_OCM"))
            self.assertIsNotNone(nested)

    def test_failure_record_is_degree_scope_not_task_blacklist(self):
        macro = ("square", "inc")
        method = L.method_record(macro, L.ORIGIN_COMPOSITION)
        rec = L.failure_record(method["identity"], macro, [{"fingerprint": "must-not-be-stored"}])
        self.assertEqual(rec["task_ids"], [])
        self.assertTrue(rec["scope"]["not_task_id_blacklist"])
        self.assertEqual(rec["origin_category"], L.ORIGIN_APPLICABILITY)
        self.assertEqual(rec["outcome"], "METHOD_FAILURE")
        high = L.normal_form(("square", "inc", "double"))
        low = L.normal_form(("inc", "inc", "double"))
        bundle = L.empty_bundle()
        bundle, _method = L.admit_macro(bundle, macro, L.ORIGIN_COMPOSITION, "OCM_0", "admit")
        bundle = L.admit_failure(bundle, rec, "OCM_1")
        self.assertTrue(L.failure_records_for_task(bundle, low))
        self.assertFalse(L.failure_records_for_task(bundle, high))

    def test_origin_categories_are_the_four_registered_ones(self):
        schema = L.load_schema()
        origin = schema["$defs"]["origin_category"]["enum"]
        self.assertEqual(
            origin,
            [
                "TAUGHT_IMPORTED",
                "LEARNED_APPLICABILITY",
                "LEARNED_COMPOSITION",
                "INDEPENDENT_REDISCOVERY",
            ],
        )

    def test_unrun_stages_include_d2_through_d6_and_not_d0_d1(self):
        self.assertEqual(L.UNRUN_STAGES, ("OCM_2", "OCM_3", "OCM_4", "OCM_5", "OCM_6"))
        self.assertNotIn("OCM_0", L.UNRUN_STAGES)
        self.assertNotIn("OCM_1", L.UNRUN_STAGES)


class TestG7Experiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = E.run(out=None, transitions_dir=None)

    def test_one_lineage_id_and_two_earned_transitions(self):
        result = self.result
        self.assertEqual(result["lineage_id"], L.LINEAGE_ID)
        self.assertEqual(result["earned_transitions"], 2)
        t0, t1 = result["transitions"]
        self.assertEqual(t0["lineage_id"], t1["lineage_id"])
        self.assertEqual(t0["source_stage"], "EMPTY")
        self.assertEqual(t0["target_stage"], "OCM_0")
        self.assertEqual(t1["source_stage"], "OCM_0")
        self.assertEqual(t1["target_stage"], "OCM_1")
        self.assertEqual(t0["target_machine_identity"], t1["source_machine_identity"])

    def test_both_transitions_validate(self):
        for record in self.result["transitions"]:
            L.validate_transition(record)
            for arm in ("CONTINUED_OCM", "RESET_OCM", "TASK_SPECIFIC_OCM", "STRONG_ADAPTIVE_PARENT"):
                self.assertIn(arm, record["strongest_parent_result"])

    def test_t0_macro_is_learned_composition_and_actually_used(self):
        t0 = self.result["t0"]
        self.assertEqual(t0["origin_category"], L.ORIGIN_COMPOSITION)
        self.assertGreater(t0["macro_wins"], 0)
        self.assertLess(t0["test_attempts"], t0["primitive_attempts"])
        self.assertTrue(self.result["transitions"][0]["actual_execution_witnesses"])

    def test_t1_reuses_t0_method_and_reset_costs_more(self):
        t1 = self.result["t1"]
        t0_method = self.result["transitions"][0]["new_methods_schemas"][0]["identity"]
        self.assertIn(t0_method, t1["reused_method_identities"])
        self.assertGreater(t1["reset_work_units"], t1["continued_work_units"])
        self.assertTrue(t1["failure_reduces_trap"])
        self.assertTrue(t1["retention_preserved"])
        self.assertEqual(t1["reset_origin_category"], L.ORIGIN_REDISCOVERY)
        self.assertTrue(self.result["transitions"][1]["strongest_parent_result"]["reset_costs_more_or_fails_reuse"])
        self.assertFalse(self.result["transitions"][1]["strongest_parent_result"]["RESET_OCM"]["reused_prior_methods"])
        self.assertTrue(self.result["transitions"][1]["strongest_parent_result"]["CONTINUED_OCM"]["reused_prior_methods"])
        self.assertFalse(self.result["transitions"][1]["strongest_parent_result"]["RESET_OCM"]["loaded_foreign_store"])

    def test_honest_unrun_boundary_and_terminal(self):
        result = self.result
        self.assertEqual(result["unrun_stages"], list(L.UNRUN_STAGES))
        self.assertFalse(result["d3_formal_mathematics_happened"])
        self.assertFalse(result["six_transitions_complete"])
        self.assertEqual(result["terminal"], "PHASED_COGNITIVE_DEVELOPMENT")
        self.assertNotEqual(
            result["terminal"],
            "CANNOT_CHECK_ONE_OF_SIX_TRANSITIONS_COMPLETE_AND_THAT_ONE_PARENT_SUFFICIENT",
        )

    def test_all_thirteen_persist_slots_present(self):
        self.assertEqual(len(self.result["persist_slots_present"]), 13)


if __name__ == "__main__":
    unittest.main()
