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
