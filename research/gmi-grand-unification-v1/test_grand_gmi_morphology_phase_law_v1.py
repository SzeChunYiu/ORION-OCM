import importlib.util
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
            "GRAND_GMI_MORPHOLOGY_PHASE_LAW_DERIVATION_GREEN_AT_FINITE_SCOPE",
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
        self.assertEqual(r["undercharged_accounting_scalar"], 10)
        self.assertTrue(r["undercharged_accounting_breaks_the_bound"])

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

    def test_pl5_derivation_cannot_select(self):
        r = self.aggregate["derivation_is_one_sided"]
        self.assertEqual(r["shared_derived_lower_bounds"], {"NEURAL": 18, "NON_NEURAL": 14})
        self.assertEqual(r["world_a_verdict"], "NON_NEURAL")
        self.assertEqual(r["world_b_verdict"], "UNDECIDED_FROM_CURRENT_EVIDENCE")
        self.assertTrue(r["relaxation_yields_lower_bounds_only"])


if __name__ == "__main__":
    unittest.main()
