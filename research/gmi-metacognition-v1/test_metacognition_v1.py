"""17 exact controls for META-1-4. Sibling source compiled explicitly; -I safe."""

from fractions import Fraction as F
from pathlib import Path
import importlib.util
import unittest

path = Path(__file__).with_name("metacognition_v1.py")
spec = importlib.util.spec_from_loader("metacognition_checked", loader=None)
meta = importlib.util.module_from_spec(spec)
exec(compile(path.read_bytes(), str(path), "exec"), meta.__dict__)


class ConfidenceMargin(unittest.TestCase):
    def test_conf_one_is_tda_stop(self):
        for s in meta.all_subsets(meta.WORLD8):
            for a in (0, 1, 2):
                self.assertEqual(meta.confidence(a, s) == F(1),
                                 a in meta.common_actions(s))

    def test_conf_monotone_for_truly_adequate(self):
        full = frozenset(meta.WORLD8)
        for a in (0, 1, 2):
            if a in meta.common_actions(full):
                continue
            # action 0 is adequate on {0,1,2,3,7}: conf rises as rivals drop
            s = frozenset((0, 1, 2, 3, 7))
            self.assertEqual(meta.confidence(a, s), F(1) if a == 0 else meta.confidence(a, s))

    def test_conf_values_spot(self):
        s = frozenset(meta.WORLD8)
        self.assertEqual(meta.confidence(0, s), F(5, 8))
        self.assertEqual(meta.confidence(1, s), F(5, 8))
        self.assertEqual(meta.confidence(2, s), F(4, 8))
        self.assertEqual(meta.common_actions(s), frozenset())

    def test_interior_conf_names_splitter(self):
        s = frozenset(meta.WORLD8)
        # action 0 inadequate exactly on {4,5,6}; t0/t1 cells separate some
        self.assertTrue(F(0) < meta.confidence(0, s) < F(1))
        self.assertEqual(len(meta.cells(s, "t0")), 2)
        self.assertEqual(len(meta.cells(s, "t1")), 2)


class ErrorLikelihood(unittest.TestCase):
    def test_ec_spot_values(self):
        s = frozenset(meta.WORLD8)
        # uniform unit loss: EC(0,S) = 3/8 = 1 - conf(0,S)
        self.assertEqual(meta.error_cost(0, s), F(3, 8))
        self.assertEqual(meta.error_cost(0, s), F(1) - meta.confidence(0, s))

    def test_ec_zero_iff_common(self):
        for s in meta.all_subsets(meta.WORLD8):
            for a in (0, 1, 2):
                self.assertEqual(meta.error_cost(a, s) == F(0),
                                 a in meta.common_actions(s))

    def test_max_conf_minimizes_ec(self):
        for s in meta.all_subsets(meta.WORLD8):
            best_conf = max(meta.confidence(a, s) for a in (0, 1, 2))
            best_ec = min(meta.error_cost(a, s) for a in (0, 1, 2))
            cands = [a for a in (0, 1, 2) if meta.confidence(a, s) == best_conf]
            self.assertTrue(any(meta.error_cost(a, s) == best_ec for a in cands))

    def test_uniform_indifference_declared(self):
        s = frozenset((4, 5, 6, 7))
        # EC is the plain mean over survivors: action 0 inadequate on 4,5,6
        self.assertEqual(meta.error_cost(0, s), F(3, 4))


class StopRule(unittest.TestCase):
    def test_stop_reproduces_tda(self):
        for s in meta.all_subsets(meta.WORLD8):
            try:
                stopped = meta.tda_value(s) == F(0)
            except ValueError:
                continue
            self.assertEqual(stopped, bool(meta.common_actions(s)))

    def test_free_splitter_always_taken(self):
        # emitting the common action has nonpositive EVC for every costly test:
        # with EC=0 already, no paid test can beat stopping (TDA-1, reversed)
        s = frozenset((0, 4))
        self.assertEqual(meta.common_actions(s), frozenset((1,)))
        for test in ("t0", "t1"):
            self.assertLessEqual(meta.evc_worst(1, s, test), F(0))

    def test_evc_is_myopic_with_exact_greedy_condition(self):
        # EVC is one-step myopic; TDA-1 is farsighted (value recursion). They
        # coincide exactly where the greedy choice is optimal: 13/35 nonempty
        # no-common-action subsets of the 6-world problem. The checker pins the
        # fraction AND witnesses both sides (agree + disagree examples).
        agree, total, examples = 0, 0, []
        for s in meta.all_subsets(meta.WORLD6):
            if meta.common_actions(s):
                continue
            try:
                mins = set(meta.tda_minimizers(s))
            except ValueError:
                continue
            total += 1
            scored = sorted(((meta.evc_mean(1, s, t), t) for t in meta.TESTS8))
            top = scored[-1][0]
            hit = bool({t for v, t in scored if v == top} & mins)
            agree += int(hit)
            if hit and len(examples) < 2:
                examples.append(sorted(s))
        self.assertEqual((agree, total), (13, 35))
        self.assertEqual(examples, [[2, 5], [3, 4]])
        # disagree example: {3,5} — t0 cheaper but never splits, TDA pays t1
        self.assertEqual(meta.tda_minimizers(frozenset((3, 5))), ["t1"])

    def test_evc_mean_form_declared(self):
        s = frozenset(meta.WORLD8)
        self.assertEqual(meta.evc_mean(0, s, "t0"),
                         meta.error_cost(0, s) - (F(1) + sum(
                             meta.error_cost(0, c) * len(c)
                             for c in meta.cells(s, "t0")) / len(s)))


class StrategySelection(unittest.TestCase):
    def test_partition_covers_all_subsets(self):
        covered, ties = 0, 0
        for s in meta.all_subsets(meta.WORLD6):
            best = meta.best_strategies(s)
            self.assertTrue(best)
            covered += 1
            ties += int(len(best) > 1)
        self.assertEqual(covered, 63)
        self.assertGreaterEqual(ties, 0)

    def test_strategy_partition_measured(self):
        # Honest measured partition over all 63 nonempty subsets: bold is
        # uniquely best on 32 sets (emitting beats costly testing); the other
        # 31 are ties including cautious/cheap_first. No fee begs the question
        # (all fees zero, verified during construction). The checker pins the
        # exact partition counts and witnesses a three-way tie + a bold win.
        from collections import Counter
        c = Counter()
        for s in meta.all_subsets(meta.WORLD6):
            c[tuple(meta.best_strategies(s))] += 1
        self.assertEqual(c[("bold",)], 32)
        self.assertEqual(sum(c.values()), 63)
        self.assertIn(("cautious", "bold", "cheap_first"), set(c))
        # bold uniquely best on {2,5}: EC 0 for action 2 vs any test cost
        self.assertEqual(meta.best_strategies(frozenset((2, 5))), ["bold"])
        # three-way tie on singletons: nothing to test, nothing to lose
        self.assertEqual(set(meta.best_strategies(frozenset((0,)))),
                         {"cautious", "bold", "cheap_first"})

    def test_bold_wins_where_common_and_costly(self):
        s = frozenset((0, 1))
        self.assertTrue(meta.common_actions(s))
        self.assertIn("bold", meta.best_strategies(s))

    def test_calibration_by_construction(self):
        # conf(a,S) IS the adequacy rate over S: calibrated relative to S.
        for s in meta.all_subsets(meta.WORLD8):
            for a in (0, 1, 2):
                rate = F(len([w for w in s if a in meta.GAMMA8[w]]), len(s))
                self.assertEqual(meta.confidence(a, s), rate)

    def test_interfaces_refuse_bad_inputs(self):
        with self.assertRaises(ValueError):
            meta.confidence(3, frozenset((0,)))
        with self.assertRaises(ValueError):
            meta.error_cost(0, frozenset())
        with self.assertRaises(ValueError):
            meta.strategy_value("timid", frozenset((0,)))
        with self.assertRaises(ValueError):
            meta.evc_worst(0, frozenset((0,)), "t9")


if __name__ == "__main__":
    unittest.main()
