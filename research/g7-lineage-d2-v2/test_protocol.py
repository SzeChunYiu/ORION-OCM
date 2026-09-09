"""Hostile protocol tests for the G7 D2 lineage successor."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
V1 = HERE.parent / "g7-lineage-v1"
SPEC_L = importlib.util.spec_from_file_location("g7_lineage_d2", HERE / "lineage.py")
L = importlib.util.module_from_spec(SPEC_L)
SPEC_L.loader.exec_module(L)
SPEC_E = importlib.util.spec_from_file_location("g7_experiment_d2", HERE / "experiment.py")
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

    def test_empty_bundle_has_all_persist_slots_taught_donors_and_frozen_c(self):
        bundle = L.empty_bundle()
        for slot in L.PERSIST_SLOTS:
            self.assertIn(slot, bundle)
        donors = bundle["imported_donors"]
        self.assertEqual(len(donors), 4)
        self.assertTrue(all(d["origin_category"] == L.ORIGIN_TAUGHT for d in donors))
        self.assertEqual(bundle["lineage_id"], L.LINEAGE_ID)
        self.assertEqual(bundle["stage"], "EMPTY")
        self.assertEqual(L.constitution_of(bundle), L.CONSTITUTION)
        L.assert_constitution_frozen(bundle)

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
            with self.assertRaises(L.IsolationError):
                L.assert_disjoint_stores(continued, L.LineageStore(continued.root / "nested", "RESET_OCM"))

    def test_continued_persist_rejects_foreign_lineage_id(self):
        missing = L.empty_bundle()
        missing["lineage_id"] = ""
        foreign = L.empty_bundle()
        foreign["lineage_id"] = "foreign-lineage"
        with tempfile.TemporaryDirectory() as temp:
            continued = L.LineageStore(Path(temp) / "continued", "CONTINUED_OCM")
            reset = L.LineageStore(Path(temp) / "reset", "RESET_OCM")
            with self.assertRaises(L.IsolationError):
                continued.persist(missing)
            with self.assertRaises(L.IsolationError):
                continued.persist(foreign)
            reset.persist(foreign)
            continued.persist(L.empty_bundle())

    def test_constitution_mutation_is_refused(self):
        bundle = L.empty_bundle()
        with self.assertRaises(L.ConstitutionMutationError):
            L.mutate_constitution(bundle, ["check"])
        mutated = json.loads(L.canonical_json(bundle))
        mutated["executive_metareasoning_policy"]["payload"]["constitution"] = ["check"]
        with tempfile.TemporaryDirectory() as temp:
            store = L.LineageStore(Path(temp) / "continued", "CONTINUED_OCM")
            with self.assertRaises(L.ConstitutionMutationError):
                store.persist(mutated)

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

    def test_unrun_stages_are_d3_through_d6(self):
        self.assertEqual(L.UNRUN_STAGES, ("OCM_3", "OCM_4", "OCM_5", "OCM_6"))
        self.assertNotIn("OCM_0", L.UNRUN_STAGES)
        self.assertNotIn("OCM_1", L.UNRUN_STAGES)
        self.assertNotIn("OCM_2", L.UNRUN_STAGES)

    def test_same_lineage_id_as_v1_and_v1_result_untouched(self):
        self.assertEqual(L.LINEAGE_ID, "orion-ocm-g7-lineage-v1:microscope-d0-d1")
        v1_result = json.loads((V1 / "RESULT.json").read_text(encoding="utf-8"))
        self.assertEqual(v1_result["lineage_id"], L.LINEAGE_ID)
        self.assertEqual(v1_result["earned_transitions"], 2)
        self.assertEqual(v1_result["terminal"], "PHASED_COGNITIVE_DEVELOPMENT")
        self.assertEqual(v1_result["final_stage"], "OCM_1")

    def test_d2_family_is_disjoint_from_polynomial_grammar(self):
        self.assertNotEqual(L.D2_GRAMMAR_ID, L.GRAMMAR_ID)
        poly = L.task_id(L.normal_form(("inc", "double")))
        diag = L.diagnosis_task_id((0, 3))
        self.assertNotEqual(poly, diag)
        population = L.diagnosis_population()
        self.assertEqual(len(population), 35)
        self.assertTrue(all(task["domain"] == L.D2_GRAMMAR_ID for task in population))


class TestG7Experiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = E.run(out=None, transitions_dir=None)

    def test_one_lineage_id_and_three_earned_transitions(self):
        result = self.result
        self.assertEqual(result["lineage_id"], L.LINEAGE_ID)
        self.assertEqual(result["earned_transitions"], 3)
        t0, t1, t2 = result["transitions"]
        self.assertEqual(t0["lineage_id"], t1["lineage_id"])
        self.assertEqual(t1["lineage_id"], t2["lineage_id"])
        self.assertEqual(t0["source_stage"], "EMPTY")
        self.assertEqual(t0["target_stage"], "OCM_0")
        self.assertEqual(t1["source_stage"], "OCM_0")
        self.assertEqual(t1["target_stage"], "OCM_1")
        self.assertEqual(t2["source_stage"], "OCM_1")
        self.assertEqual(t2["target_stage"], "OCM_2")
        self.assertEqual(t0["target_machine_identity"], t1["source_machine_identity"])
        self.assertEqual(t1["target_machine_identity"], t2["source_machine_identity"])

    def test_all_transitions_validate(self):
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

    def test_t2_is_new_diagnosis_competence_not_relabeled_history(self):
        t2 = self.result["t2"]
        self.assertIsNotNone(t2)
        self.assertEqual(t2["policy_name"], L.D2_POLICY_GREEDY)
        self.assertLess(t2["test_probes"], t2["round_robin_probes"])
        self.assertGreater(t2["reset_work_units"], t2["continued_work_units"])
        self.assertTrue(t2["d0_retained"])
        self.assertTrue(t2["d1_retained"])
        self.assertTrue(t2["families_disjoint"])
        self.assertFalse(t2["historical_m11_relabeled"])
        self.assertFalse(self.result["historical_m11_relabeled"])
        self.assertEqual(t2["constitution"], list(L.CONSTITUTION))
        t0_method = self.result["transitions"][0]["new_methods_schemas"][0]["identity"]
        t1_failure = self.result["transitions"][1]["new_methods_schemas"][0]["identity"]
        self.assertIn(t0_method, t2["reused_method_identities"])
        self.assertIn(t1_failure, t2["reused_method_identities"])
        self.assertTrue(self.result["transitions"][2]["actual_execution_witnesses"])
        self.assertTrue(self.result["transitions"][2]["ablation"]["effect_disappears"])
        self.assertTrue(self.result["transitions"][2]["strongest_parent_result"]["reset_costs_more_or_fails_reuse"])
        self.assertFalse(self.result["transitions"][2]["strongest_parent_result"]["RESET_OCM"]["reused_prior_methods"])
        self.assertTrue(self.result["transitions"][2]["strongest_parent_result"]["CONTINUED_OCM"]["reused_prior_methods"])
        train_ids = set(self.result["transitions"][2]["new_information_supplied"]["training_task_ids"])
        poly_ids = set(self.result["transitions"][0]["new_information_supplied"]["training_task_ids"])
        poly_ids |= set(self.result["transitions"][1]["new_information_supplied"]["training_task_ids"])
        self.assertFalse(train_ids & poly_ids)
        self.assertFalse(self.result["historical_m11_relabeled"])

    def test_honest_unrun_boundary_and_terminal(self):
        result = self.result
        self.assertEqual(result["unrun_stages"], list(L.UNRUN_STAGES))
        self.assertFalse(result["d3_formal_mathematics_happened"])
        self.assertFalse(result["six_transitions_complete"])
        self.assertEqual(result["terminal"], "PHASED_COGNITIVE_DEVELOPMENT")
        self.assertEqual(result["final_stage"], "OCM_2")
        self.assertNotEqual(
            result["terminal"],
            "CANNOT_CHECK_ONE_OF_SIX_TRANSITIONS_COMPLETE_AND_THAT_ONE_PARENT_SUFFICIENT",
        )
        self.assertNotEqual(result["terminal"], "CANNOT_CHECK_D2_PROBE_POLICY_NOT_EARNED")

    def test_all_thirteen_persist_slots_present(self):
        self.assertEqual(len(self.result["persist_slots_present"]), 13)

    def test_no_production_src_import(self):
        text = (HERE / "lineage.py").read_text(encoding="utf-8") + (HERE / "experiment.py").read_text(encoding="utf-8")
        self.assertNotIn("from ocm", text)
        self.assertNotIn("import ocm", text)
        self.assertNotIn("src/ocm", text)


if __name__ == "__main__":
    unittest.main()
