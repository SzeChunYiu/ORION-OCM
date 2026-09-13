"""Finite mathematical countermodels and constructive revivals."""
from fractions import Fraction as F
from pathlib import Path
import types
import unittest

HERE = Path(__file__).resolve().parent
m = types.ModuleType("aem_model")
exec(compile((HERE/"architecture_selection_v1.py").read_bytes(),
             str(HERE/"architecture_selection_v1.py"), "exec"), m.__dict__)


def row(name, label, *cost):
    return name, label, tuple(F(c) for c in cost)


class ArchitectureSelectionControls(unittest.TestCase):
    def test_profile_closure_does_not_erase_other_label_fibers(self):
        actual = (row("a", "A", 1, 1), row("b", "B", 1, 1))
        selected = m.constructive_closure(actual, {"a"}, ((F(1), F(1)),))
        self.assertEqual({r[0] for r in selected}, {"a", "b"})
        self.assertIsNone(m.completion_report((selected,))["robust_unique_label"])

    def test_full_fibers_can_certify_one_label(self):
        actual = (row("a", "A", 1, 1), row("b", "A", 1, 1), row("c", "B", 2, 2))
        selected = m.constructive_closure(actual, {"a"}, tuple(r[2] for r in actual))
        self.assertEqual(m.completion_report((selected,))["robust_unique_label"], "A")

    def test_relaxed_costs_preserve_opposite_winners(self):
        a = (row("neural", "N", 18), row("program", "P", 16))
        b = (row("neural", "N", 18), row("program", "P", 20))
        report = m.completion_report((a, b))
        self.assertFalse(report["label_set_identified"])
        self.assertEqual(report["selected_label_sets"], (frozenset({"P"}), frozenset({"N"})))

    def test_unknown_rival_cost_can_be_irrelevant(self):
        worlds = tuple((row("a", "A", 0), row("b", "B", cost)) for cost in (2, 3))
        report = m.completion_report(worlds)
        self.assertEqual(report["robust_unique_label"], "A")
        self.assertEqual(report["common_optimal_candidates"], frozenset({"a"}))

    def test_unknown_coverage_and_development_of_dominated_member(self):
        base = (row("a", "A", 0),)
        extension = base + (row("b", "B", 4),)
        self.assertEqual(m.completion_report((base, extension))["robust_unique_label"], "A")

    def test_same_family_per_world_need_not_supply_common_machine(self):
        worlds = ((row("a", "A", 0), row("b", "A", 1)),
                  (row("a", "A", 1), row("b", "A", 0)))
        result = m.completion_report(worlds)
        self.assertEqual(result["robust_unique_label"], "A")
        self.assertEqual(result["common_optimal_candidates"], frozenset())

    def test_empty_feasibility_is_not_a_vacuous_family(self):
        report = m.completion_report(((), ()))
        self.assertTrue(report["label_set_identified"])
        self.assertFalse(report["selection_exists_in_every_world"])
        self.assertIsNone(report["robust_unique_label"])
        with self.assertRaises(ValueError):
            m.completion_report(())

    def test_assembly_does_not_imply_adequacy_and_edge_can_revive(self):
        universe = (row("seed", "S", 0), row("bad", "A", 2), row("good", "A", 3))
        first = (("seed", "bad"),)
        self.assertEqual(m.feasible_rows(universe, first, {"seed"}, {"good"}), ())
        repaired = first + (("bad", "good"),)
        adequate = m.feasible_rows(universe, repaired, {"seed"}, {"good"})
        self.assertEqual(tuple(r[0] for r in adequate), ("good",))
        self.assertEqual(m.frontier(adequate), adequate)

    def test_finite_failed_sample_does_not_bound_unseen_family(self):
        failed = {"saved0": F(1, 2), "saved1": F(3, 4)}
        extension = dict(failed, unseen=F(1))
        threshold = F(17, 20)
        self.assertFalse(any(score >= threshold for score in failed.values()))
        self.assertTrue(any(score >= threshold for score in extension.values()))

    def test_approximate_sequence_witness_has_positive_residual(self):
        # The infinite nonattainment claim is analytic; each finite n is improvable.
        for denominator in range(1, 17):
            eta = F(1, denominator)
            n = denominator
            self.assertLessEqual(F(1, n), eta)
            self.assertGreater(F(1, n), 0)
            self.assertLess(F(1, n+1), F(1, n))

    def test_dimension_and_identity_errors_cannot_certify(self):
        for rows in ((row("a", "A", 1), row("b", "B", 1, 2)),
                     (row("a", "A", 1), row("a", "A", 2))):
            with self.assertRaises(ValueError):
                m.frontier(rows)
        with self.assertRaises(ValueError):
            m.completion_report(((row("a", "A", 1),), (row("a", "B", 1),)))

    def test_false_relaxation_or_constructive_coverage_is_rejected(self):
        actual = (row("a", "A", 1), row("b", "B", 0))
        for necessary in (((F(1),),), ((F(0),), (F(1),))):
            with self.assertRaises(ValueError):
                m.constructive_closure(actual, {"a"}, necessary)

    def test_scalar_winner_does_not_exclude_other_pareto_labels(self):
        rows = (row("a", "A", 0, 2), row("b", "B", 2, 0))
        self.assertEqual({r[1] for r in m.frontier(rows)}, {"A", "B"})
        values = {name: 2*p[0]+p[1] for name, _label, p in rows}
        self.assertEqual(values, {"a": F(2), "b": F(4)})

    def test_common_witness_gap_bounds_regret_within_covered_worlds(self):
        for better_same_family in (F(1), F(3, 2), F(2)):
            costs = {"common": F(2), "same": better_same_family, "rival": F(3)}
            optimum = min(costs.values())
            self.assertLessEqual(costs["common"] - optimum, F(2)-F(1))
            self.assertLess(costs["common"], costs["rival"])
        # An unregistered cost0 competitor defeats the supposed global lower bound1.
        self.assertGreater(F(2)-F(0), F(2)-F(1))


if __name__ == "__main__":
    unittest.main()
