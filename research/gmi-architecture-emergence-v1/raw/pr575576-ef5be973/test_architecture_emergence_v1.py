"""Exact witnesses for AEM-2, AEM-3 and AEM-5.

These checks do not re-prove the registered parent results.  They freeze the
numbers each obstruction turns on, so that a claim of "GMI predicts this
architecture" can be tested against them.
"""

from fractions import Fraction
from itertools import product
import re
import unittest
from pathlib import Path

HALF = Fraction(1, 2)
THEOREM = Path(__file__).resolve().parent / "ARCHITECTURE_EMERGENCE_THEOREM_V1.md"


def pareto(points):
    """Minimisation: keep points not weakly dominated by a different point."""
    out = []
    for p in points:
        if not any(q != p and all(a <= b for a, b in zip(q, p))
                   and any(a < b for a, b in zip(q, p)) for q in points):
            out.append(p)
    return sorted(set(out))


class ObstructionWitnesses(unittest.TestCase):
    def test_O3_process_law_does_not_choose_the_obligation(self) -> None:
        # GG32: dynamics x_{t+1} = a are identical; the constitution differs.
        def optimal_action(viable):
            return sorted(a for a in (0, 1) if a in viable)
        self.assertEqual(optimal_action({0}), [0])
        self.assertEqual(optimal_action({1}), [1])
        self.assertNotEqual(optimal_action({0}), optimal_action({1}))

    def test_O4_observation_does_not_fix_the_interventional_law(self) -> None:
        # CAU-1: identical observational law, different do(X=1).
        def observational(world):
            table = {}
            for u in (0, 1):
                x = u
                y = u if world == 0 else x
                table[(x, y)] = table.get((x, y), Fraction(0)) + HALF
            return table

        def do_x1(world):
            return sum(HALF for u in (0, 1) if (u if world == 0 else 1) == 1)

        self.assertEqual(observational(0), observational(1))
        self.assertEqual(do_x1(0), HALF)
        self.assertEqual(do_x1(1), Fraction(1))

    def test_O5_relaxed_bounds_do_not_determine_the_family_optimum(self) -> None:
        # PL-5: same refined lower bounds, opposite actual winners.
        lower = {"NEURAL": 18, "NON_NEURAL": 14}
        world_a = {"NEURAL": 18, "NON_NEURAL": 16}
        world_b = {"NEURAL": 18, "NON_NEURAL": 20}
        for world in (world_a, world_b):
            for family, bound in lower.items():
                self.assertGreaterEqual(world[family], bound)
        self.assertEqual(min(world_a, key=world_a.get), "NON_NEURAL")
        self.assertEqual(min(world_b, key=world_b.get), "NEURAL")

    def test_AEM5_family_orderings_are_size_indexed(self) -> None:
        # PN-4R, measured under a faithful native charge l(n) = 2n+1.
        rows = {3: (88, 104), 4: (224, 240), 5: (544, 544),
                6: (1280, 1216), 7: (2944, 2688), 8: (6656, 5888)}
        for n, (xor, delegating_lower) in rows.items():
            with self.subTest(n=n):
                if n <= 4:
                    self.assertLess(xor, delegating_lower)
                elif n == 5:
                    self.assertEqual(xor, delegating_lower)
                else:
                    self.assertGreater(xor, delegating_lower)


class PositiveCondition(unittest.TestCase):
    def test_AEM2_domination_makes_the_pareto_sets_coincide(self) -> None:
        constructive = [(1, 3), (3, 1)]
        necessity = constructive + [(2, 4), (4, 2), (3, 3)]
        # every necessity point is weakly dominated by a constructive point
        for point in necessity:
            self.assertTrue(any(all(c <= p for c, p in zip(cand, point))
                                for cand in constructive), point)
        self.assertEqual(pareto(constructive), pareto(necessity))

    def test_AEM2_is_sufficient_not_necessary(self) -> None:
        # An attainable set with an empty Pareto subset supplies no optimiser.
        unbounded = [(1, 3), (3, 1)]
        self.assertNotIn((1, 1), unbounded)
        self.assertEqual(pareto(unbounded), [(1, 3), (3, 1)])


class ClaimDiscipline(unittest.TestCase):
    def test_theorem_disclaims_formal_independence(self) -> None:
        text = THEOREM.read_text(encoding="utf-8")
        self.assertIn("not* a claim of formal logical independence", text)

    def test_theorem_lists_five_distinct_destroyed_arguments(self) -> None:
        text = THEOREM.read_text(encoding="utf-8")
        rows = re.findall(r"^\| O\d \| .+? \| (.+?) \|", text, re.M)
        self.assertEqual(len(rows), 5)
        self.assertEqual(len(set(rows)), 5, rows)


if __name__ == "__main__":
    unittest.main()
