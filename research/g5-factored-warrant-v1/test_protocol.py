"""Exhaustive G5.3 protocol: factored DAG vs antichain oracle."""
from __future__ import annotations

import itertools
import unittest

from ocm.kso.warrant import (
    ONE,
    ZERO,
    CannotCheck,
    Liveness,
    WarrantProfile,
    all_profiles,
    join,
    leq,
    live,
    meet,
    powerset,
)

from factored_warrant import (
    FactoredWarrant,
    SupportDAG,
    mutant_collapse_bounds,
    mutant_upper_only_as_live,
)


def legal_intervals(n: int):
    profiles = all_profiles(n)
    for lower in profiles:
        for upper in profiles:
            if leq(lower, upper):
                yield WarrantProfile(lower, upper)


class TestFactoredWarrantProtocol(unittest.TestCase):
    def test_lower_and_upper_remain_distinct(self):
        dag = SupportDAG()
        wp = WarrantProfile.partial([{0}])
        fw = FactoredWarrant.from_profile(wp, dag)
        self.assertNotEqual(fw.lower.ident, fw.upper.ident)
        self.assertEqual(fw.upper_only_evidence(), frozenset())  # upper is ONE, no leaves
        expanded = fw.expand()
        self.assertEqual(expanded.lower, wp.lower)
        self.assertEqual(expanded.upper, wp.upper)
        self.assertFalse(expanded.complete)

    def test_upper_only_evidence_is_tracked(self):
        dag = SupportDAG()
        lower = (frozenset({0}),)
        upper = join(lower, (frozenset({1}),))
        wp = WarrantProfile(lower, upper)
        fw = FactoredWarrant.from_profile(wp, dag)
        self.assertEqual(fw.upper_only_evidence(), frozenset({1}))
        self.assertEqual(fw.liveness(()), Liveness.LIVE)
        self.assertEqual(fw.liveness((0,)), Liveness.UNKNOWN)
        self.assertEqual(fw.liveness((0, 1)), Liveness.DEAD)

    def test_alternate_and_conjunctive_exact_on_expand(self):
        dag = SupportDAG()
        a = FactoredWarrant.from_profile(WarrantProfile.of({0}), dag)
        b = FactoredWarrant.from_profile(WarrantProfile.of({1}), dag)
        self.assertEqual(a.join(b).expand().lower, join((frozenset({0}),), (frozenset({1}),)))
        self.assertEqual(a.meet(b).expand().lower, meet((frozenset({0}),), (frozenset({1}),)))

    def test_n3_revocation_parity_against_antichain_oracle(self):
        universe = tuple(range(3))
        revocations = powerset(universe)
        mismatches = 0
        checked = 0
        for wp in legal_intervals(3):
            dag = SupportDAG()
            fw = FactoredWarrant.from_profile(wp, dag)
            expanded = fw.expand(cap=64)
            self.assertEqual(expanded.lower, wp.lower)
            self.assertEqual(expanded.upper, wp.upper)
            for revoked in revocations:
                checked += 1
                if fw.liveness(revoked) is not wp.liveness(revoked):
                    mismatches += 1
        self.assertEqual(mismatches, 0)
        self.assertGreater(checked, 100)

    def test_enumeration_cap_is_cannot_check_not_approx(self):
        dag = SupportDAG()
        node = dag.zero
        for i in range(6):
            node = dag.join(node, dag.leaf(i))
        with self.assertRaises(CannotCheck) as ctx:
            dag.expand(node, cap=2)
        self.assertIn("OUTPUT_SIZE", str(ctx.exception))

    def test_collapse_bounds_mutant_is_wrong_on_partial(self):
        wp = WarrantProfile.partial([{0}])
        collapsed = mutant_collapse_bounds(wp)
        self.assertEqual(wp.liveness((0,)), Liveness.UNKNOWN)
        self.assertEqual(collapsed.liveness((0,)), Liveness.LIVE)

    def test_upper_only_as_live_mutant_is_wrong(self):
        wp = WarrantProfile((frozenset({0}),), join((frozenset({0}),), (frozenset({1}),)))
        self.assertFalse(live(wp.lower, (0,)))
        self.assertTrue(mutant_upper_only_as_live(wp, (0,)))
        self.assertIs(wp.liveness((0,)), Liveness.UNKNOWN)

    def test_production_adoption_not_claimed(self):
        # Default warrant module still exports antichain constructors.
        from ocm.kso import warrant as W
        self.assertTrue(hasattr(W, "WarrantProfile"))
        self.assertNotEqual(W.__file__, __file__)


if __name__ == "__main__":
    unittest.main()
