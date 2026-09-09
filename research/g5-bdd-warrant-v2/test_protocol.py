"""Exhaustive G5.3 v2 protocol: ROBDD vs support DAG vs antichain oracle."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "research" / "g5-factored-warrant-v1"))

from ocm.kso.warrant import (
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

from bdd_warrant import BDDWarrant, ROBDD, mutant_collapse_bounds, mutant_eval_lower_only
from factored_warrant import FactoredWarrant, SupportDAG


def legal_intervals(n: int):
    profiles = all_profiles(n)
    for lower in profiles:
        for upper in profiles:
            if leq(lower, upper):
                yield WarrantProfile(lower, upper)


class TestBDDWarrantProtocol(unittest.TestCase):
    def test_stdlib_only_no_bdd_package(self):
        text = (Path(__file__).resolve().parent / "bdd_warrant.py").read_text()
        for banned in ("import dd", "from dd", "import cudd", "import pyeda", "from pyeda"):
            self.assertNotIn(banned, text)
        self.assertNotIn("factored_warrant", text)
        spec = importlib.util.spec_from_file_location(
            "bdd_warrant_iso", Path(__file__).resolve().parent / "bdd_warrant.py"
        )
        self.assertIsNotNone(spec)

    def test_lower_and_upper_remain_distinct(self):
        mgr = ROBDD((0, 1, 2))
        wp = WarrantProfile.partial([{0}])
        bw = BDDWarrant.from_profile(wp, mgr)
        self.assertNotEqual(bw.lower, bw.upper)
        self.assertEqual(bw.upper_only_evidence(), frozenset())
        expanded = bw.expand()
        self.assertEqual(expanded.lower, wp.lower)
        self.assertEqual(expanded.upper, wp.upper)
        self.assertFalse(expanded.complete)

    def test_upper_only_evidence_is_tracked(self):
        mgr = ROBDD((0, 1, 2))
        lower = (frozenset({0}),)
        upper = join(lower, (frozenset({1}),))
        wp = WarrantProfile(lower, upper)
        bw = BDDWarrant.from_profile(wp, mgr)
        self.assertEqual(bw.upper_only_evidence(), frozenset({1}))
        self.assertEqual(bw.liveness(()), Liveness.LIVE)
        self.assertEqual(bw.liveness((0,)), Liveness.UNKNOWN)
        self.assertEqual(bw.liveness((0, 1)), Liveness.DEAD)

    def test_alternate_and_conjunctive_exact_on_expand(self):
        mgr = ROBDD((0, 1, 2))
        a = BDDWarrant.from_profile(WarrantProfile.of({0}), mgr)
        b = BDDWarrant.from_profile(WarrantProfile.of({1}), mgr)
        self.assertEqual(a.join(b).expand().lower, join((frozenset({0}),), (frozenset({1}),)))
        self.assertEqual(a.meet(b).expand().lower, meet((frozenset({0}),), (frozenset({1}),)))

    def test_n3_three_way_revocation_parity(self):
        universe = tuple(range(3))
        revocations = powerset(universe)
        mismatches = 0
        checked = 0
        expand_ok = 0
        for wp in legal_intervals(3):
            dag = SupportDAG()
            fw = FactoredWarrant.from_profile(wp, dag)
            mgr = ROBDD(universe)
            bw = BDDWarrant.from_profile(wp, mgr)
            expanded = bw.expand(cap=64)
            self.assertEqual(expanded.lower, wp.lower)
            self.assertEqual(expanded.upper, wp.upper)
            self.assertEqual(fw.expand(cap=64).lower, wp.lower)
            expand_ok += 1
            for revoked in revocations:
                checked += 1
                anti = wp.liveness(revoked)
                if fw.liveness(revoked) is not anti or bw.liveness(revoked) is not anti:
                    mismatches += 1
        self.assertEqual(mismatches, 0)
        self.assertGreater(checked, 100)
        self.assertEqual(expand_ok, 168)

    def test_enumeration_cap_is_cannot_check_not_approx(self):
        mgr = ROBDD()
        node = mgr.FALSE.ident
        for i in range(6):
            node = mgr.bdd_or(node, mgr.var(i))
        with self.assertRaises(CannotCheck) as ctx:
            mgr.expand(node, cap=2)
        self.assertIn("OUTPUT_SIZE", str(ctx.exception))

    def test_collapse_bounds_mutant_is_wrong_on_partial(self):
        wp = WarrantProfile.partial([{0}])
        collapsed = mutant_collapse_bounds(wp)
        self.assertEqual(wp.liveness((0,)), Liveness.UNKNOWN)
        self.assertEqual(collapsed.liveness((0,)), Liveness.LIVE)

    def test_lower_only_eval_mutant_is_wrong(self):
        wp = WarrantProfile((frozenset({0}),), join((frozenset({0}),), (frozenset({1}),)))
        bw = BDDWarrant.from_profile(wp, ROBDD((0, 1)))
        self.assertFalse(live(wp.lower, (0,)))
        self.assertEqual(mutant_eval_lower_only(bw, (0,)), Liveness.DEAD)
        self.assertIs(wp.liveness((0,)), Liveness.UNKNOWN)
        self.assertIs(bw.liveness((0,)), Liveness.UNKNOWN)

    def test_production_warrant_unchanged_and_not_switched(self):
        from ocm.kso import warrant as W
        self.assertTrue(hasattr(W, "WarrantProfile"))
        self.assertNotEqual(Path(W.__file__).resolve(), Path(__file__).resolve())
        self.assertNotIn("bdd_warrant", Path(W.__file__).read_text())
        self.assertIn("antichain", W.__doc__.lower())


if __name__ == "__main__":
    unittest.main()
