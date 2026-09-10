"""Exhaustive G5.3 v3 protocol: ZDD vs ROBDD vs support DAG vs antichain oracle."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "research" / "g5-bdd-warrant-v2"))
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

from bdd_warrant import BDDWarrant, ROBDD
from factored_warrant import FactoredWarrant, SupportDAG
from zdd_warrant import (
    ZDD,
    ZDDWarrant,
    mutant_collapse_bounds,
    mutant_eval_lower_only,
    mutant_join_as_xor,
)


def legal_intervals(n: int):
    profiles = all_profiles(n)
    for lower in profiles:
        for upper in profiles:
            if leq(lower, upper):
                yield WarrantProfile(lower, upper)


class TestZDDWarrantProtocol(unittest.TestCase):
    def test_stdlib_only_no_zdd_package(self):
        text = (HERE / "zdd_warrant.py").read_text()
        for banned in ("import dd", "from dd", "import cudd", "import pyeda", "from pyeda"):
            self.assertNotIn(banned, text)
        self.assertNotIn("bdd_warrant", text)
        self.assertNotIn("factored_warrant", text)
        spec = importlib.util.spec_from_file_location("zdd_warrant_iso", HERE / "zdd_warrant.py")
        self.assertIsNotNone(spec)

    def test_zero_suppression_drops_hi_false(self):
        mgr = ZDD((0, 1, 2))
        kept = mgr.var(0)
        self.assertEqual(mgr.node(kept).hi, mgr.TRUE.ident)
        suppressed = mgr.mk(1, mgr.TRUE.ident, mgr.FALSE.ident)
        self.assertEqual(suppressed, mgr.TRUE.ident)
        lo_eq_hi = mgr.mk(2, kept, kept)
        self.assertNotEqual(lo_eq_hi, kept)
        self.assertEqual(mgr.node(lo_eq_hi).lo, kept)
        self.assertEqual(mgr.node(lo_eq_hi).hi, kept)

    def test_lower_and_upper_remain_distinct(self):
        mgr = ZDD((0, 1, 2))
        wp = WarrantProfile.partial([{0}])
        zw = ZDDWarrant.from_profile(wp, mgr)
        self.assertNotEqual(zw.lower, zw.upper)
        self.assertEqual(zw.upper_only_evidence(), frozenset())
        expanded = zw.expand()
        self.assertEqual(expanded.lower, wp.lower)
        self.assertEqual(expanded.upper, wp.upper)
        self.assertFalse(expanded.complete)

    def test_upper_only_evidence_is_tracked(self):
        mgr = ZDD((0, 1, 2))
        lower = (frozenset({0}),)
        upper = join(lower, (frozenset({1}),))
        wp = WarrantProfile(lower, upper)
        zw = ZDDWarrant.from_profile(wp, mgr)
        self.assertEqual(zw.upper_only_evidence(), frozenset({1}))
        self.assertEqual(zw.liveness(()), Liveness.LIVE)
        self.assertEqual(zw.liveness((0,)), Liveness.UNKNOWN)
        self.assertEqual(zw.liveness((0, 1)), Liveness.DEAD)

    def test_alternate_and_conjunctive_exact_on_expand(self):
        mgr = ZDD((0, 1, 2))
        a = ZDDWarrant.from_profile(WarrantProfile.of({0}), mgr)
        b = ZDDWarrant.from_profile(WarrantProfile.of({1}), mgr)
        self.assertEqual(a.join(b).expand().lower, join((frozenset({0}),), (frozenset({1}),)))
        self.assertEqual(a.meet(b).expand().lower, meet((frozenset({0}),), (frozenset({1}),)))

    def test_xor_is_not_warrant_join(self):
        mgr = ZDD((0, 1))
        a = ZDDWarrant.from_profile(WarrantProfile.of({0}), mgr)
        same = ZDDWarrant.from_profile(WarrantProfile.of({0}), mgr)
        joined = a.join(same).expand().lower
        xored = mutant_join_as_xor(a, same).expand().lower
        self.assertEqual(joined, (frozenset({0}),))
        self.assertEqual(xored, ())
        other = ZDDWarrant.from_profile(WarrantProfile.of({1}), mgr)
        self.assertEqual(a.join(other).expand().lower, mutant_join_as_xor(a, other).expand().lower)

    def test_n3_four_way_revocation_parity(self):
        universe = tuple(range(3))
        revocations = powerset(universe)
        mismatches = 0
        checked = 0
        expand_ok = 0
        for wp in legal_intervals(3):
            dag = SupportDAG()
            fw = FactoredWarrant.from_profile(wp, dag)
            bdd = ROBDD(universe)
            bw = BDDWarrant.from_profile(wp, bdd)
            zdd = ZDD(universe)
            zw = ZDDWarrant.from_profile(wp, zdd)
            expanded = zw.expand(cap=64)
            self.assertEqual(expanded.lower, wp.lower)
            self.assertEqual(expanded.upper, wp.upper)
            self.assertEqual(bw.expand(cap=64).lower, wp.lower)
            self.assertEqual(fw.expand(cap=64).lower, wp.lower)
            expand_ok += 1
            for revoked in revocations:
                checked += 1
                anti = wp.liveness(revoked)
                if (
                    fw.liveness(revoked) is not anti
                    or bw.liveness(revoked) is not anti
                    or zw.liveness(revoked) is not anti
                ):
                    mismatches += 1
        self.assertEqual(mismatches, 0)
        self.assertGreater(checked, 100)
        self.assertEqual(expand_ok, 168)

    def test_enumeration_cap_is_cannot_check_not_approx(self):
        mgr = ZDD()
        node = mgr.FALSE.ident
        for i in range(6):
            node = mgr.zdd_or(node, mgr.var(i))
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
        zw = ZDDWarrant.from_profile(wp, ZDD((0, 1)))
        self.assertFalse(live(wp.lower, (0,)))
        self.assertEqual(mutant_eval_lower_only(zw, (0,)), Liveness.DEAD)
        self.assertIs(wp.liveness((0,)), Liveness.UNKNOWN)
        self.assertIs(zw.liveness((0,)), Liveness.UNKNOWN)

    def test_predecessor_result_files_untouched(self):
        v1 = (REPO / "research" / "g5-factored-warrant-v1" / "RESULT.json").read_text()
        v2 = (REPO / "research" / "g5-bdd-warrant-v2" / "RESULT.json").read_text()
        self.assertIn("FACTORED_WARRANT_VALUE_SUPPORTED", v1)
        self.assertIn("BDD_PARENT_N3_PARITY_SUPPORTED", v2)
        self.assertIn('"zdd_parent": "OPEN"', v2)

    def test_production_warrant_unchanged_and_not_switched(self):
        from ocm.kso import warrant as W

        self.assertTrue(hasattr(W, "WarrantProfile"))
        self.assertNotEqual(Path(W.__file__).resolve(), Path(__file__).resolve())
        text = Path(W.__file__).read_text()
        self.assertNotIn("zdd_warrant", text)
        self.assertNotIn("bdd_warrant", text)
        self.assertIn("antichain", W.__doc__.lower())


if __name__ == "__main__":
    unittest.main()
