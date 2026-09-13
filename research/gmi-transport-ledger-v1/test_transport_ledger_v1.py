"""TL-1..TL-5: what transports to arbitrary scale and what does not."""
from fractions import Fraction as F
import unittest
from pathlib import Path

import transport_model_v1 as T

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
GMI = REPO / "research" / "gmi-grand-unification-v1"


class TL1_LowerBoundsTransport(unittest.TestCase):
    def test_transport_holds_and_does_not_use_cardinality(self):
        """Same order argument at every size; cardinality is never consulted."""
        for n in (1, 2, 5, 50, 500, 5000):
            alloc = [F(k, n + 1) for k in range(1, n + 1)]
            a_qM = max(alloc)
            r = T.transport(alloc, a_qM, a_qM + F(1))
            self.assertEqual(r["terminal"], "TRANSPORTS")
            self.assertEqual(r["bound"], min(alloc))
            self.assertLessEqual(r["bound"], a_qM + F(1))

    def test_bound_is_independent_of_how_many_allocations_exist(self):
        small = [F(1, 2), F(3, 4)]
        # F(3,4) must actually be in the set it is declared a member of.
        large = [F(1, 2), F(3, 4)] + [F(3, 4) + F(1, k) for k in range(2, 200)]
        self.assertEqual(T.transport(small, F(3, 4), F(1))["bound"],
                         T.transport(large, F(3, 4), F(1))["bound"])


class TL2_ThePremisesAreLoadBearing(unittest.TestCase):
    def test_unsound_accounting_refuses_transport(self):
        alloc = [F(1), F(2)]
        r = T.transport(alloc, F(2), F(1))          # a(q_M) > c(M)
        self.assertEqual(r["terminal"], "UNSOUND_ACCOUNTING")
        self.assertIsNone(r["bound"])

    def test_missing_membership_refuses_transport(self):
        alloc = [F(1), F(2)]
        r = T.transport(alloc, F(2), F(5), membership=False)
        self.assertEqual(r["terminal"], "NO_MEMBERSHIP")

    def test_declared_membership_contradicted_by_the_set_raises(self):
        with self.assertRaises(ValueError):
            T.transport([F(1), F(2)], F(7), F(9))

    def test_inexact_values_are_refused(self):
        with self.assertRaises(ValueError):
            T.transport([F(1)], 1.0, F(2))


class TL3_ExclusionsDoNotTransport(unittest.TestCase):
    """The half that fails: a lower bound never orders two machines."""

    def test_shared_bound_leaves_the_ordering_open(self):
        L = F(1)
        self.assertFalse(T.exclusion_is_determined(L, [F(3), F(2)]))
        self.assertFalse(T.exclusion_is_determined(L, [F(2), F(3)]))

    def test_the_order_can_flip_while_the_bound_is_unchanged(self):
        L = F(1)
        a, b = F(2), F(3)
        self.assertTrue(a < b)
        self.assertTrue(T.transport([L, a], a, a)["bound"] == L)
        self.assertTrue(T.transport([L, b], b, b)["bound"] == L)
        # same transported bound, opposite orderings available
        self.assertFalse(T.exclusion_is_determined(L, [a, b]))

    def test_only_a_single_machine_above_the_bound_is_determined(self):
        self.assertTrue(T.exclusion_is_determined(F(1), [F(1), F(2)]))


class TL4_TheParentClausesAreCitedCorrectly(unittest.TestCase):
    def test_clb_states_the_two_premises_and_the_non_requirements(self):
        text = (GMI / "CONTINUOUS_LIFT_BOUNDARY_THEOREM_V1.md").read_text(encoding="utf-8")
        self.assertIn("neither finite cardinality, compactness, measurability nor", text)
        self.assertIn("allocation membership and sound accounting", text)
        self.assertIn("retained comparator", text)

    def test_the_atlas_records_the_open_scale_tier(self):
        text = (GMI / "PHENOMENOLOGY_REDUCTION_ATLAS_V1.md").read_text(encoding="utf-8")
        self.assertIn("quantitatively open at modern scale", text)
        self.assertIn("should not convert unmeasured constants into theorems", text)

    def test_control_a_false_citation_would_fail(self):
        text = (GMI / "CONTINUOUS_LIFT_BOUNDARY_THEOREM_V1.md").read_text(encoding="utf-8")
        self.assertNotIn("compactness is required for transport", text)


if __name__ == "__main__":
    unittest.main()


class TL6_ExclusionsTransportUnderATwoSidedCertificate(unittest.TestCase):
    """The positive form of TL-3, reusing DCR's registered separation rule."""

    def test_finite_upper_below_comparator_lower_certifies_at_any_scale(self):
        self.assertEqual(T.exclusion_transports((F(1), F(2)), (F(3), None)),
                         "CERTIFIED_STRICTLY_LOWER")
        # scale the whole problem: the certificate is order-based, so it survives
        for k in (1, 10, 1000, 10 ** 6):
            self.assertEqual(
                T.exclusion_transports((F(1 * k), F(2 * k)), (F(3 * k), None)),
                "CERTIFIED_STRICTLY_LOWER")

    def test_lower_bounds_alone_never_certify(self):
        """TL-3 restated: this is the degenerate case, candidate upper is None."""
        self.assertEqual(T.exclusion_transports((F(1), None), (F(1), None)),
                         "UNVERIFIABLE")
        self.assertEqual(T.exclusion_transports((F(1), None), (F(5), None)),
                         "UNVERIFIABLE")

    def test_overlap_is_unverifiable_not_false(self):
        self.assertEqual(T.exclusion_transports((F(1), F(4)), (F(3), F(9))),
                         "UNVERIFIABLE")

    def test_touching_intervals_do_not_certify(self):
        self.assertEqual(T.exclusion_transports((F(1), F(3)), (F(3), None)),
                         "UNVERIFIABLE")

    def test_malformed_intervals_are_refused(self):
        with self.assertRaises(ValueError):
            T.exclusion_transports((F(2), F(1)), (F(3), None))
        with self.assertRaises(ValueError):
            T.exclusion_transports((F(-1), F(1)), (F(3), None))
        with self.assertRaises(ValueError):
            T.exclusion_transports((1.0, F(2)), (F(3), None))

    def test_every_verdict_is_a_registered_terminal(self):
        cases = [((F(1), F(2)), (F(3), None)), ((F(1), None), (F(2), None)),
                 ((F(1), F(4)), (F(3), F(9)))]
        for c, m in cases:
            self.assertIn(T.exclusion_transports(c, m), T.EXCLUSION_TERMINALS)


class TL7_TheCertificateIsNecessaryAndSufficient(unittest.TestCase):
    """Unconditional characterisation, with constructive counter-witnesses."""

    def test_certification_is_exactly_for_all_completions(self):
        """Exhaustive over a rational grid: the rule never disagrees."""
        grid = [F(k, 2) for k in range(0, 9)]
        checked = 0
        for a_lo in grid:
            for a_hi in [x for x in grid if x >= a_lo] + [None]:
                for b_lo in grid:
                    for b_hi in [x for x in grid if x >= b_lo] + [None]:
                        A, B = (a_lo, a_hi), (b_lo, b_hi)
                        can_lt, can_gt, can_eq = T.realizable_orders(A, B)
                        forall_lt = (not can_gt) and (not can_eq)
                        certified = T.compare(A, B) == "CERTIFIED_STRICTLY_LOWER"
                        self.assertEqual(certified, forall_lt, "%s vs %s" % (A, B))
                        checked += 1
        self.assertGreater(checked, 1000)

    def test_non_certifying_pairs_have_both_orders_realizable(self):
        A, B = (F(1), F(4)), (F(3), F(9))
        self.assertEqual(T.compare(A, B), "UNVERIFIABLE")
        can_lt, can_gt, _ = T.realizable_orders(A, B)
        self.assertTrue(can_lt and can_gt)

    def test_the_boundary_case_realizes_a_tie(self):
        A, B = (F(1), F(3)), (F(3), None)
        self.assertEqual(T.compare(A, B), "UNVERIFIABLE")
        _, _, can_eq = T.realizable_orders(A, B)
        self.assertTrue(can_eq)

    def test_the_mirror_certificate_TL6_omitted(self):
        """b_hi < a_lo certifies the comparator cheaper; TL-6 returned UNVERIFIABLE."""
        A, B = (F(10), None), (F(1), F(4))
        self.assertEqual(T.compare(A, B), "CERTIFIED_STRICTLY_HIGHER")
        self.assertEqual(T.exclusion_transports(A, B), "UNVERIFIABLE")

    def test_compare_agrees_with_exclusion_transports_on_its_own_direction(self):
        for A, B in [((F(1), F(2)), (F(3), None)), ((F(1), None), (F(2), None)),
                     ((F(1), F(4)), (F(3), F(9)))]:
            if T.exclusion_transports(A, B) == "CERTIFIED_STRICTLY_LOWER":
                self.assertEqual(T.compare(A, B), "CERTIFIED_STRICTLY_LOWER")

    def test_every_compare_verdict_is_registered(self):
        for A, B in [((F(1), F(2)), (F(9), None)), ((F(9), None), (F(1), F(2))),
                     ((F(1), None), (F(1), None))]:
            self.assertIn(T.compare(A, B), T.COMPARE_TERMINALS)


class TL8_CompareValidatesLikeItsSibling(unittest.TestCase):
    """Corrects a defect: compare() certified empty and negative intervals."""

    def test_empty_candidate_interval_is_refused(self):
        with self.assertRaises(ValueError):
            T.compare((F(2), F(1)), (F(3), F(4)))

    def test_negative_lower_bound_is_refused(self):
        with self.assertRaises(ValueError):
            T.compare((F(-1), F(2)), (F(3), F(4)))

    def test_inexact_endpoint_is_refused(self):
        with self.assertRaises(ValueError):
            T.compare((1.0, F(2)), (F(3), F(4)))

    def test_the_no_alarm_case_still_certifies(self):
        self.assertEqual(T.compare((F(1), F(2)), (F(3), F(4))),
                         "CERTIFIED_STRICTLY_LOWER")
        self.assertEqual(T.compare((F(10), None), (F(1), F(4))),
                         "CERTIFIED_STRICTLY_HIGHER")

    def test_compare_and_exclusion_transports_now_agree_on_validation(self):
        for bad in [((F(2), F(1)), (F(3), F(4))), ((F(-1), F(2)), (F(3), F(4)))]:
            for fn in (T.compare, T.exclusion_transports):
                with self.assertRaises(ValueError):
                    fn(*bad)
