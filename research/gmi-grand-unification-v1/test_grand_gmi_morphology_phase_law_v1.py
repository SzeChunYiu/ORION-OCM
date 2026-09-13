import importlib.util
import hashlib
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_morphology_phase_law_checks_v1",
    HERE / "grand_gmi_morphology_phase_law_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class MorphologyPhaseLawTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aggregate = MOD.run()

    def test_terminal_and_ceiling(self):
        self.assertEqual(
            self.aggregate["terminal"],
            "GRAND_GMI_MORPHOLOGY_PHASE_LAW_SCOPE_REPAIRED_V2_GREEN",
        )
        self.assertFalse(self.aggregate["real_substrate_bound_measured"])

    def test_bounds_are_derived_not_registered(self):
        r = self.aggregate["derived_bounds"]
        self.assertEqual(r["allocation_grid_size"], 4096)
        self.assertEqual(r["states"]["without_coupling"]["NEURAL"]["derived_lower_bound"], 15)
        self.assertEqual(r["states"]["without_coupling"]["NON_NEURAL"]["derived_lower_bound"], 11)
        self.assertEqual(r["states"]["with_coupling"]["NEURAL"]["derived_lower_bound"], 18)
        self.assertEqual(r["states"]["with_coupling"]["NON_NEURAL"]["derived_lower_bound"], 14)

    def test_pl2_transports_to_machines_and_needs_sound_accounting(self):
        r = self.aggregate["transport_to_real_machines"]
        self.assertEqual(r["sound_machines_checked"], 4)
        self.assertTrue(r["every_sound_machine_respects_its_derived_bound"])
        self.assertEqual(r["actual_scalar_cost"], 10)
        self.assertEqual(r["overcharging_accounting_scalar"], 18)
        self.assertEqual(r["accounted_resources"], {"memory": 6, "compute": 6})
        self.assertEqual(r["actual_resources"], {"memory": 2, "compute": 4})
        self.assertTrue(r["overcharging_accounting_breaks_the_bound"])

    def test_pl2_covers_an_unregistered_member_of_the_class(self):
        # PL-2 quantifies over the structural predicate, so a machine that
        # appears in no registered candidate list is still bounded.
        bound, _ = MOD.derived_lower_bound(MOD.sigma_neural, True)
        exotic = {"w1": 6, "w2": 6, "t1": 4, "t2": 4}
        self.assertTrue(MOD.sigma_neural(exotic))
        self.assertTrue(MOD.satisfies_necessities(exotic, True))
        self.assertGreaterEqual(MOD.scalar(MOD.accounted(exotic)), bound)

    def test_pl3_looseness_is_epistemic(self):
        r = self.aggregate["relaxation_looseness_is_epistemic"]
        self.assertEqual(r["relaxed_neural_lower_bound"], 15)
        self.assertEqual(r["refined_neural_lower_bound"], 18)
        self.assertEqual(r["verdict_from_relaxed_bound"], "UNDECIDED_FROM_CURRENT_EVIDENCE")
        self.assertEqual(r["verdict_from_refined_bound"], "NON_NEURAL")

    def test_pl3b_tight_bounds_are_physical(self):
        r = self.aggregate["tight_bounds_make_abstention_physical"]
        self.assertEqual(r["interval_verdict"], r["true_optimum_verdict"])
        self.assertEqual(r["interval_verdict"], "UNDECIDED_FROM_CURRENT_EVIDENCE")

    def test_pl4_evidence_is_safe_and_candidates_are_not(self):
        r = self.aggregate["evidence_monotonicity_and_candidate_sensitivity"]
        self.assertTrue(r["valid_necessities_never_lower_a_derived_bound"])
        self.assertEqual(r["restricted_neural_lower_bound"], 18)
        self.assertEqual(r["enlarged_neural_lower_bound"], 12)
        self.assertEqual(r["verdict_under_registered_class"], "NON_NEURAL")
        self.assertEqual(r["verdict_after_class_enlargement"], "UNDECIDED_FROM_CURRENT_EVIDENCE")

    def test_pl5_identical_bounds_can_have_opposite_actual_optima(self):
        r = self.aggregate["derivation_is_one_sided"]
        self.assertEqual(r["shared_derived_lower_bounds"], {"NEURAL": 18, "NON_NEURAL": 14})
        self.assertEqual(r["world_a_verdict"], "NON_NEURAL")
        self.assertEqual(r["world_b_verdict"], "UNDECIDED_FROM_CURRENT_EVIDENCE")
        self.assertTrue(r["relaxation_yields_lower_bounds_only"])
        self.assertEqual(r["complete_world_candidate_costs"], {
            "world_a": {"NEURAL": 18, "NON_NEURAL": 16},
            "world_b": {"NEURAL": 18, "NON_NEURAL": 20}})
        self.assertEqual(r["true_optimal_families"], {
            "world_a": "NON_NEURAL", "world_b": "NEURAL"})

    def test_empty_rival_plus_attained_existence_can_select(self):
        r = self.aggregate["derivation_is_one_sided"]
        self.assertEqual(r["empty_rival_relaxation"], {"A": [1], "B": []})
        self.assertEqual(r["selected_existence_supplied"], {
            "family": "A", "selected_families": ["A"], "status": "SELECTED"})
        self.assertFalse(r["numeric_upper_bound_needed_for_empty_rival_exclusion"])
        self.assertEqual(MOD.derived_lower_bound(lambda _: False, True), (None, 0))

    def test_same_relaxation_does_not_supply_actual_existence(self):
        actual = MOD.survivor_from_empty_rivals({"A": {1}, "B": set()}, [])
        self.assertEqual(actual, {
            "family": None, "selected_families": [], "status": "NO_SELECTED_REALIZATION"})

    def test_uncovered_competitor_and_bad_relaxation_are_refused(self):
        relaxed = {"A": {1}, "B": set()}
        with self.assertRaisesRegex(ValueError, "coverage"):
            MOD.survivor_from_empty_rivals(relaxed, [{"family": "C", "allocation": 0, "cost": 0}])
        with self.assertRaisesRegex(ValueError, "allocation"):
            MOD.survivor_from_empty_rivals(relaxed, [{"family": "B", "allocation": 0, "cost": 0}])
        with self.assertRaisesRegex(ValueError, "integer"):
            MOD.survivor_from_empty_rivals(relaxed, [{"family": "A", "allocation": 1, "cost": float("inf")}])

    def test_v2_payload_and_historical_v1_custody(self):
        v2 = json.loads((HERE / "GRAND_GMI_MORPHOLOGY_PHASE_LAW_RECEIPT_V2.json").read_text())
        self.assertEqual(self.aggregate, v2)
        old_bytes = (HERE / "GRAND_GMI_MORPHOLOGY_PHASE_LAW_RECEIPT_V1.json").read_bytes()
        self.assertEqual(hashlib.sha256(old_bytes).hexdigest(),
            "b5fe1962e4505b52a702b032ffee39dd557984653a2d14ac2b942acc5b5792d1")


if __name__ == "__main__":
    unittest.main()
