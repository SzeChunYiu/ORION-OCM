"""Hostile protocol tests for the G7 D6 lineage successor."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
V1 = HERE.parent / "g7-lineage-v1"
V2 = HERE.parent / "g7-lineage-d2-v2"
V3 = HERE.parent / "g7-lineage-d3-v3"
V4 = HERE.parent / "g7-lineage-d4-v4"
V5 = HERE.parent / "g7-lineage-d5-v5"
MATH_V2 = HERE.parent / "math-n4-subgoal-v2"
MATH_V1 = HERE.parent / "math-n4-lemma-reuse-v1"
SPEC_L = importlib.util.spec_from_file_location("g7_lineage_d6", HERE / "lineage.py")
L = importlib.util.module_from_spec(SPEC_L)
SPEC_L.loader.exec_module(L)
SPEC_E = importlib.util.spec_from_file_location("g7_experiment_d6", HERE / "experiment.py")
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

    def test_unrun_stages_are_empty_after_d6(self):
        self.assertEqual(L.UNRUN_STAGES, ())
        self.assertNotIn("OCM_0", L.UNRUN_STAGES)
        self.assertNotIn("OCM_6", L.UNRUN_STAGES)

    def test_same_lineage_id_and_prior_results_untouched(self):
        self.assertEqual(L.LINEAGE_ID, "orion-ocm-g7-lineage-v1:microscope-d0-d1")
        v1_result = json.loads((V1 / "RESULT.json").read_text(encoding="utf-8"))
        self.assertEqual(v1_result["lineage_id"], L.LINEAGE_ID)
        self.assertEqual(v1_result["earned_transitions"], 2)
        self.assertEqual(v1_result["terminal"], "PHASED_COGNITIVE_DEVELOPMENT")
        self.assertEqual(v1_result["final_stage"], "OCM_1")
        v2_result = json.loads((V2 / "RESULT.json").read_text(encoding="utf-8"))
        self.assertEqual(v2_result["lineage_id"], L.LINEAGE_ID)
        self.assertEqual(v2_result["earned_transitions"], 3)
        self.assertEqual(v2_result["terminal"], "PHASED_COGNITIVE_DEVELOPMENT")
        self.assertEqual(v2_result["final_stage"], "OCM_2")
        self.assertFalse(v2_result["d3_formal_mathematics_happened"])
        v3_result = json.loads((V3 / "RESULT.json").read_text(encoding="utf-8"))
        self.assertEqual(v3_result["lineage_id"], L.LINEAGE_ID)
        self.assertEqual(v3_result["earned_transitions"], 4)
        self.assertEqual(v3_result["terminal"], "PHASED_COGNITIVE_DEVELOPMENT")
        self.assertEqual(v3_result["final_stage"], "OCM_3")
        self.assertTrue(v3_result["d3_formal_mathematics_happened"])
        self.assertFalse(v3_result["d4_coding_happened"])
        if (V4 / "RESULT.json").is_file():
            v4_result = json.loads((V4 / "RESULT.json").read_text(encoding="utf-8"))
            self.assertEqual(v4_result["lineage_id"], L.LINEAGE_ID)
            self.assertEqual(v4_result["earned_transitions"], 5)
            self.assertEqual(v4_result["terminal"], "PHASED_COGNITIVE_DEVELOPMENT")
            self.assertEqual(v4_result["final_stage"], "OCM_4")
            self.assertTrue(v4_result["d4_coding_happened"])
            self.assertFalse(v4_result["d5_metacognition_happened"])
        if (V5 / "RESULT.json").is_file():
            v5_result = json.loads((V5 / "RESULT.json").read_text(encoding="utf-8"))
            self.assertEqual(v5_result["lineage_id"], L.LINEAGE_ID)
            self.assertEqual(v5_result["earned_transitions"], 6)
            self.assertEqual(v5_result["terminal"], "PHASED_COGNITIVE_DEVELOPMENT")
            self.assertEqual(v5_result["final_stage"], "OCM_5")
            self.assertTrue(v5_result["d5_metacognition_happened"])
            self.assertFalse(v5_result["d6_self_evolution_happened"])

    def test_d6_family_is_disjoint_and_not_frozen_m11_or_mutate_c(self):
        self.assertNotEqual(L.D6_GRAMMAR_ID, L.GRAMMAR_ID)
        self.assertNotEqual(L.D6_GRAMMAR_ID, L.D2_GRAMMAR_ID)
        self.assertNotEqual(L.D6_GRAMMAR_ID, L.D3_GRAMMAR_ID)
        self.assertNotEqual(L.D6_GRAMMAR_ID, L.D4_GRAMMAR_ID)
        self.assertNotEqual(L.D6_GRAMMAR_ID, L.D5_GRAMMAR_ID)
        poly = L.task_id(L.normal_form(("inc", "double")))
        diag = L.diagnosis_task_id((0, 3))
        hilbert = L.hilbert_task_id({"A": "e", "B": "f", "C": "g", "D": "h"})
        rewrite = L.rewrite_task_id(("P", "Q", "R", "S", "P", "Q"), ("Q", "P", "R", "S", "Q", "P"))
        meta = L.meta_task_id("L", ("W", "X", "Y"))
        plant = L.plant_task_id((0, 3))
        self.assertEqual(len({poly, diag, hilbert, rewrite, meta, plant}), 6)
        population = L.plant_population()
        self.assertGreaterEqual(len(population), 28)
        self.assertTrue(all(task["domain"] == L.D6_GRAMMAR_ID for task in population))
        self.assertEqual(
            L.D6_FROZEN_POLICY_NAMES,
            frozenset({"M11", "JUMP", "MUTATE_C", "G0", "G1", "G2", "AUTOML", "NEURAL"}),
        )
        syndromes = {task["syndrome"] for task in population}
        self.assertEqual(len(syndromes), len(population))

    def test_shadow_eval_and_external_c_gate(self):
        stuck = (0, 3)
        clean = L.shadow_eval_repair(stuck, (0, 3))
        self.assertEqual(clean["quality"], 1)
        dirty = L.shadow_eval_repair(stuck, (0,))
        self.assertEqual(dirty["quality"], 0)
        self.assertTrue(L.constitution_adopt((0, 3), 1, L.CONSTITUTION))
        self.assertFalse(L.constitution_adopt((0, 3), 0, L.CONSTITUTION))
        with self.assertRaises(L.ConstitutionMutationError):
            L.constitution_adopt((0, 3), 1, ("check",))
        with self.assertRaises(L.ConstitutionMutationError):
            L.shadow_eval_repair(stuck, (99,))
        truth = L.independent_truth(stuck)
        self.assertEqual(truth, frozenset({0, 3}))

    def test_propose_without_c_does_not_repair(self):
        population = L.plant_population()
        task = population[0]
        discovered = L.discover_evolution_policy((task,), L.ORIGIN_COMPOSITION)
        refused = L.table_evolution_policy(
            discovered["table"], discovered["policy_id"],
            c_may_adopt=False, width=discovered["width"],
        )
        result = L.serve_plant(task, refused)
        self.assertFalse(result["verified"])
        self.assertFalse(result["c_adopted"])
        self.assertEqual(result["status"], "NOT_FOUND")
        adopted = L.serve_plant(task, discovered["policy"])
        self.assertTrue(adopted["verified"])
        self.assertTrue(adopted["c_adopted"])
        self.assertIn("C_ADOPT", adopted["token_word"])
        self.assertIn("RESTART", adopted["token_word"])
        self.assertIn("SHADOW", adopted["token_word"])


class TestG7Experiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = E.run(out=None, transitions_dir=None)

    def test_one_lineage_id_and_seven_earned_transitions(self):
        result = self.result
        self.assertEqual(result["lineage_id"], L.LINEAGE_ID)
        self.assertEqual(result["earned_transitions"], 7)
        t0, t1, t2, t3, t4, t5, t6 = result["transitions"]
        self.assertEqual(t0["lineage_id"], t6["lineage_id"])
        self.assertEqual(t0["source_stage"], "EMPTY")
        self.assertEqual(t0["target_stage"], "OCM_0")
        self.assertEqual(t1["source_stage"], "OCM_0")
        self.assertEqual(t1["target_stage"], "OCM_1")
        self.assertEqual(t2["source_stage"], "OCM_1")
        self.assertEqual(t2["target_stage"], "OCM_2")
        self.assertEqual(t3["source_stage"], "OCM_2")
        self.assertEqual(t3["target_stage"], "OCM_3")
        self.assertEqual(t4["source_stage"], "OCM_3")
        self.assertEqual(t4["target_stage"], "OCM_4")
        self.assertEqual(t5["source_stage"], "OCM_4")
        self.assertEqual(t5["target_stage"], "OCM_5")
        self.assertEqual(t6["source_stage"], "OCM_5")
        self.assertEqual(t6["target_stage"], "OCM_6")
        self.assertEqual(t0["target_machine_identity"], t1["source_machine_identity"])
        self.assertEqual(t1["target_machine_identity"], t2["source_machine_identity"])
        self.assertEqual(t2["target_machine_identity"], t3["source_machine_identity"])
        self.assertEqual(t3["target_machine_identity"], t4["source_machine_identity"])
        self.assertEqual(t4["target_machine_identity"], t5["source_machine_identity"])
        self.assertEqual(t5["target_machine_identity"], t6["source_machine_identity"])

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

    def test_t5_is_utility_table_metacognition_not_neural(self):
        t5 = self.result["t5"]
        self.assertIsNotNone(t5)
        self.assertTrue(t5["policy_id"].startswith("SEL_"))
        self.assertFalse(t5["neural"])
        self.assertGreater(t5["reset_work_units"], t5["continued_work_units"])
        self.assertTrue(t5["d4_retained"])

    def test_t6_is_governed_self_evolution_not_m11_or_mutate_c(self):
        t6 = self.result["t6"]
        self.assertIsNotNone(t6)
        self.assertTrue(t6["policy_id"].startswith("EVOL_"))
        self.assertFalse(t6["policy_id"].startswith("SEL_"))
        self.assertFalse(t6["policy_id"].startswith("RW_"))
        self.assertFalse(t6["policy_id"].startswith("CUT_"))
        self.assertNotIn(t6["policy_id"], ("M11", "JUMP", "MUTATE_C", "G0", "G1", "G2", "AUTOML", "NEURAL"))
        self.assertFalse(t6["frozen_name"])
        self.assertFalse(t6["neural"])
        self.assertFalse(t6["constitution_mutated"])
        self.assertFalse(t6["metamath_claimed"])
        self.assertFalse(t6["flt_expanded"])
        self.assertFalse(t6["historical_m11_relabeled"])
        self.assertFalse(self.result["historical_m11_relabeled"])
        self.assertGreater(t6["reset_work_units"], t6["continued_work_units"])
        self.assertTrue(t6["d0_retained"])
        self.assertTrue(t6["d1_retained"])
        self.assertTrue(t6["d2_retained"])
        self.assertTrue(t6["d3_retained"])
        self.assertTrue(t6["d4_retained"])
        self.assertTrue(t6["d5_retained"])
        self.assertTrue(t6["families_disjoint"])
        self.assertEqual(t6["constitution"], list(L.CONSTITUTION))
        self.assertLess(t6["test_cost"], t6["replace_all_cost"])
        self.assertEqual(t6["table_uses"], t6["c_adoptions"])
        self.assertEqual(t6["c_adoptions"], t6["identified"])
        self.assertGreater(t6["c_adoptions"], 0)
        t0_method = self.result["transitions"][0]["new_methods_schemas"][0]["identity"]
        t1_failure = self.result["transitions"][1]["new_methods_schemas"][0]["identity"]
        t2_policy = self.result["transitions"][2]["new_methods_schemas"][0]["identity"]
        t3_cut = self.result["transitions"][3]["new_methods_schemas"][0]["identity"]
        t4_rewrite = self.result["transitions"][4]["new_methods_schemas"][0]["identity"]
        t5_sel = self.result["transitions"][5]["new_methods_schemas"][0]["identity"]
        self.assertIn(t0_method, t6["reused_method_identities"])
        self.assertIn(t1_failure, t6["reused_method_identities"])
        self.assertIn(t2_policy, t6["reused_method_identities"])
        self.assertIn(t3_cut, t6["reused_method_identities"])
        self.assertIn(t4_rewrite, t6["reused_method_identities"])
        self.assertIn(t5_sel, t6["reused_method_identities"])
        self.assertTrue(self.result["transitions"][6]["actual_execution_witnesses"])
        self.assertTrue(self.result["transitions"][6]["ablation"]["effect_disappears"])
        self.assertTrue(self.result["transitions"][6]["strongest_parent_result"]["reset_costs_more_or_fails_reuse"])
        self.assertFalse(self.result["transitions"][6]["strongest_parent_result"]["RESET_OCM"]["reused_prior_methods"])
        self.assertTrue(self.result["transitions"][6]["strongest_parent_result"]["CONTINUED_OCM"]["reused_prior_methods"])
        train_ids = set(self.result["transitions"][6]["new_information_supplied"]["training_task_ids"])
        earlier = set()
        for record in self.result["transitions"][:6]:
            earlier |= set(record["new_information_supplied"]["training_task_ids"])
        self.assertFalse(train_ids & earlier)
        payload = self.result["transitions"][6]["new_methods_schemas"][0]["payload"]
        self.assertTrue(payload["not_m11_relabel"])
        self.assertTrue(payload["not_constitution_mutation"])
        self.assertTrue(payload["external_c_required"])
        self.assertTrue(payload["not_neural"])
        self.assertTrue(payload["not_metamath"])
        self.assertTrue(payload["not_flt"])
        self.assertEqual(payload["policy_id"], t6["policy_id"])
        self.assertEqual(t6["continued_work_units"], t6["task_specific_work_units"])
        for witness in self.result["transitions"][6]["actual_execution_witnesses"]:
            self.assertIn("SHADOW", witness["token_word"])
            self.assertIn("C_ADOPT", witness["token_word"])
            self.assertIn("RESTART", witness["token_word"])
            self.assertTrue(any(token.startswith("PROPOSE:") for token in witness["token_word"]))

    def test_honest_terminal_and_d6_earned(self):
        result = self.result
        self.assertEqual(result["unrun_stages"], list(L.UNRUN_STAGES))
        self.assertTrue(result["d3_formal_mathematics_happened"])
        self.assertTrue(result["d4_coding_happened"])
        self.assertTrue(result["d5_metacognition_happened"])
        self.assertTrue(result["d6_self_evolution_happened"])
        self.assertTrue(result["six_transitions_complete"])
        self.assertTrue(result["seven_transitions_complete"])
        self.assertEqual(result["terminal"], "PHASED_COGNITIVE_DEVELOPMENT")
        self.assertEqual(result["final_stage"], "OCM_6")
        self.assertNotEqual(result["terminal"], "CANNOT_CHECK_D6_SELF_EVOLUTION_NOT_EARNED")
        self.assertIn("not M11 relabel", result["d6_scope"])
        self.assertIn("not constitution mutation", result["d6_scope"])
        self.assertEqual(result["constitution"], list(L.CONSTITUTION))

    def test_all_thirteen_persist_slots_present(self):
        self.assertEqual(len(self.result["persist_slots_present"]), 13)

    def test_no_production_src_import(self):
        text = (HERE / "lineage.py").read_text(encoding="utf-8") + (HERE / "experiment.py").read_text(encoding="utf-8")
        self.assertNotIn("from ocm", text)
        self.assertNotIn("import ocm", text)
        self.assertNotIn("src/ocm", text)
        self.assertNotIn("OperatorSpec", text)
        self.assertNotIn("import torch", text)
        self.assertNotIn("from torch", text)

    def test_prior_result_files_not_overwritten(self):
        v1 = hashlib.sha256((V1 / "RESULT.json").read_bytes()).hexdigest()
        v2 = hashlib.sha256((V2 / "RESULT.json").read_bytes()).hexdigest()
        v3 = hashlib.sha256((V3 / "RESULT.json").read_bytes()).hexdigest()
        math_v2 = hashlib.sha256((MATH_V2 / "RESULT.json").read_bytes()).hexdigest()
        math_v1 = hashlib.sha256((MATH_V1 / "RESULT.json").read_bytes()).hexdigest()
        self.assertEqual(v1, hashlib.sha256((V1 / "RESULT.json").read_bytes()).hexdigest())
        self.assertEqual(json.loads((V1 / "RESULT.json").read_text())["earned_transitions"], 2)
        self.assertEqual(json.loads((V2 / "RESULT.json").read_text())["earned_transitions"], 3)
        self.assertEqual(json.loads((V3 / "RESULT.json").read_text())["earned_transitions"], 4)
        self.assertFalse(json.loads((V3 / "RESULT.json").read_text())["d4_coding_happened"])
        if (V4 / "RESULT.json").is_file():
            self.assertEqual(json.loads((V4 / "RESULT.json").read_text())["earned_transitions"], 5)
        if (V5 / "RESULT.json").is_file():
            self.assertEqual(json.loads((V5 / "RESULT.json").read_text())["earned_transitions"], 6)
            self.assertFalse(json.loads((V5 / "RESULT.json").read_text())["d6_self_evolution_happened"])
        self.assertEqual(
            json.loads((MATH_V2 / "RESULT.json").read_text())["terminal"],
            "CAUSAL_SUBGOAL_LEMMA_INTRODUCTION_SUPPORTED_AT_MINIATURE_SCOPE",
        )
        self.assertTrue(v1 and v2 and v3 and math_v2 and math_v1)


if __name__ == "__main__":
    unittest.main()
