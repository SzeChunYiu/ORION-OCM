from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from fractions import Fraction

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "morphology_selection_schema_v1", ROOT / "morphology_selection_schema_v1.py"
)
m = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)
F = Fraction


class TestSelectionSchema(unittest.TestCase):
    def test_certificate_green(self):
        r = m.finite_certificate()
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))

    def test_scalar_winner_is_pareto(self):
        c = m._selection_fixture()
        front = set(m.pareto_front(c))
        for w in ((1, 1), (4, 1), (1, 4)):
            self.assertLessEqual(set(m.scalar_argmin(c, w)), front)

    def test_no_viable_fails_closed(self):
        c = (m.make_candidate("x", (1, 1), viable=False),)
        self.assertEqual(m.selection_record(c, (1, 1))["terminal"], "NO_VIABLE_MORPHOLOGY")

    def test_universal_componentwise_winner(self):
        c = (
            m.make_candidate("p", (1, 1)),
            m.make_candidate("q", (1, 2)),
            m.make_candidate("r", (2, 1)),
        )
        self.assertEqual(m.componentwise_universal_winner(c), "p")
        self.assertEqual(m.pareto_front(c), ("p",))
        self.assertEqual(m.scalar_argmin(c, (7, 3)), ("p",))

    def test_coordinatewise_minimum_can_be_unattainable(self):
        c = (m.make_candidate("a", (1, 4)), m.make_candidate("b", (4, 1)))
        q = m.coordinatewise_infimum(c)
        self.assertEqual(q, (F(1), F(1)))
        self.assertNotIn(q, {x.resources for x in c})

    def test_phase_boundaries(self):
        c = m._phase_fixture()
        self.assertEqual(m.pairwise_crossings(c, 0, 1), (F(2, 5), F(1, 2), F(3, 5)))
        self.assertEqual(m.affine_argmin(c, F(2, 5)), ("A", "C"))
        self.assertEqual(m.affine_argmin(c, F(3, 5)), ("B", "C"))

    def test_phase_cells_constant(self):
        c = m._phase_fixture()
        for a, b, w in m.phase_cells(c, 0, 1):
            for q in (F(1, 5), F(2, 5), F(4, 5)):
                self.assertEqual(m.affine_argmin(c, a + (b - a) * q), w)

    def test_uncertainty(self):
        c = m._phase_fixture()
        self.assertEqual(
            m.uncertainty_terminal(c, F(9, 20), F(11, 20)),
            {"terminal": "ROBUST_UNIQUE", "possible_winners": ["C"]},
        )
        self.assertEqual(
            m.uncertainty_terminal(c, F(1, 3), F(2, 3))["terminal"], "AMBIGUOUS"
        )

    def test_midpoint_hostile(self):
        c = (m.make_affine("M", 0, 0), m.make_affine("N", "-3/4", 1))
        self.assertEqual(m.affine_argmin(c, F(1, 2)), ("N",))
        self.assertEqual(m.possible_winners(c, 0, 1), ("M", "N"))

    def test_malformed_rejected(self):
        with self.assertRaises(m.SelectionError):
            m.make_candidate("x", (-1, 1))
        with self.assertRaises(m.SelectionError):
            m.scalar_argmin((m.make_candidate("x", (1, 1)),), (1, 0))
        with self.assertRaises(m.SelectionError):
            m.phase_cells((m.make_affine("x", 0, 1),), 1, 0)


if __name__ == "__main__":
    unittest.main()
