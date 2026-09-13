import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_candidate_coverage_checks_v1",
    HERE / "grand_gmi_candidate_coverage_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class CandidateCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aggregate = MOD.run()

    def test_terminal_and_ceiling(self):
        self.assertEqual(
            self.aggregate["terminal"],
            "GRAND_GMI_CANDIDATE_UNIVERSE_COVERAGE_GREEN_AT_FINITE_SCOPE",
        )
        self.assertFalse(self.aggregate["physical_machine_enumeration_claimed"])

    def test_cu1_finite_coverage_is_decidable(self):
        r = self.aggregate["finite_coverage_decision"]
        self.assertEqual(r["admitted_allocations"], 1344)
        self.assertFalse(r["registered_classes_cover"])
        self.assertEqual(r["uncovered_admitted_allocations"], 1105)
        self.assertTrue(r["completed_classes_cover"])
        self.assertTrue(r["complement_cover_is_a_valid_dichotomy"])

    def test_finite_prefix_cannot_certify_universal_coverage(self):
        r = self.aggregate["finite_prefix_boundary"]
        self.assertEqual(r["bounded_controls"], 8)
        self.assertEqual(r["first_uncovered_indices"], list(range(1, 9)))
        self.assertFalse(r["unrestricted_coverage_decidability_claimed"])
        self.assertTrue(r["finite_prefix_never_used_as_infinite_certificate"])

    def test_finite_decision_exact_positive_negative_empty_and_overlap(self):
        even = {"even": lambda x: x % 2 == 0}
        self.assertEqual(MOD.covers(even, (0, 2, 4)), (True, []))
        self.assertEqual(MOD.covers(even, (0, 1, 2)), (False, [1]))
        self.assertEqual(MOD.covers({}, ()), (True, []))
        self.assertEqual(MOD.covers({}, (0,)), (False, [0]))
        both = {**even, "odd": lambda x: x % 2 == 1, "all": lambda x: True}
        self.assertEqual(MOD.covers(both, range(7)), (True, []))

    def test_missing_boolean_predicate_evidence_is_rejected(self):
        for value in (None, 1, "yes"):
            with self.assertRaises(ValueError):
                MOD.covers({"unknown": lambda x: value}, (0,))

    def test_cu3_residue_withdraws_the_verdict(self):
        r = self.aggregate["uncovered_residue_defeats_a_verdict"]
        self.assertEqual(r["verdict_over_registered_classes"], "NON_NEURAL")
        self.assertEqual(
            r["verdict_over_completed_classes"], "UNDECIDED_FROM_CURRENT_EVIDENCE"
        )
        self.assertEqual(r["bounds_over_completed_classes"]["RESIDUE"], 12)
        self.assertEqual(r["admitted_residue_allocations_beating_the_construction"], 19)
        self.assertEqual(r["cheapest_admitted_residue_scalar"], 12)

    def test_cu2_complete_cover_is_universal_at_the_instance(self):
        r = self.aggregate["complete_cover_gives_a_universal_verdict"]
        self.assertEqual(r["verdict"], "RESIDUE")
        self.assertEqual(r["residue_construction_upper_bound"], 12)
        self.assertEqual(r["admitted_allocations_outside_the_selected_class"], 239)
        self.assertTrue(r["no_admitted_allocation_beats_the_witness"])
        self.assertTrue(r["universal_at_registered_instance_only"])

    def test_cu3b_verdict_cannot_be_upgraded(self):
        r = self.aggregate["non_upgradability_without_coverage"]
        self.assertEqual(r["verdict_under_expensive_extension"], "NON_NEURAL")
        self.assertEqual(
            r["verdict_under_cheap_extension"], "UNDECIDED_FROM_CURRENT_EVIDENCE"
        )
        self.assertEqual(
            r["required_report"], "ROBUST_WITHIN_COVERED_CLASSES_WITH_OPEN_RESIDUE"
        )

    def test_cu4_component_cover_does_not_lift(self):
        r = self.aggregate["component_cover_does_not_lift"]
        self.assertTrue(r["single_site_predicates_cover_every_site_cost"])
        self.assertFalse(r["lifted_conjunction_covers_composites"])
        self.assertEqual(r["uncovered_composite_allocations"], 896)
        self.assertEqual(r["mixed_witness"], {"w1": 2, "w2": 1, "t1": 0, "t2": 1})

    def test_cu5_overlap_takes_the_stronger_bound(self):
        r = self.aggregate["overlapping_classes_take_the_stronger_bound"]
        self.assertEqual(r["strongest_applicable_bound"], 18)
        self.assertEqual(r["admitted_allocations_in_both_classes"], 119)
        self.assertTrue(r["overlap_weakens_nothing"])


if __name__ == "__main__":
    unittest.main()
