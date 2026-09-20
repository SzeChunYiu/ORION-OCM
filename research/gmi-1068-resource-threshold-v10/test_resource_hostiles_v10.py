"""Boundary models and independently checked certificate corruption controls."""
import unittest
from copy import deepcopy
import independent_oracle_v10 as oracle
import threshold_v10 as core

COVERAGE = {}


class ResourceHostiles(unittest.TestCase):
    def test_resource_semantics(self):
        # A zero-cost cycle cannot invent a mismatch; a separate exit costs five.
        fixtures = [(((0, 0), (((0, 0, 0),), ((0, 0, 1),))), None),
                    (((0, 0), (((0, 0, 0), (0, 5, 0)), ((0, 0, 1), (1, 5, 1)))), 5),
                    (((0, 0), (((0, 3, 1),), ((0, 3, 0),))), None),
                    (((0, 0), ((None,), ((0, 0, 1),))), 0),
                    (((0, 1), ((), ())), 0),
                    (((0, 0), ((), ())), None)]
        for machine, distance in fixtures:
            result = core.solve(machine)
            self.assertTrue(core.verify(machine, result))
            self.assertEqual(result["distances"][0][1], distance)
            for budget in range(7):
                self.assertEqual(tuple(core.classes(result, budget)), oracle.budget_partition(machine, budget))
        singleton = core.solve(((0,), ((),)))
        self.assertEqual(singleton, {"distances": [[None]], "witnesses": [[None]]})
        # Erasing cost loses nesting: both blocked, only cheap edge, both visible.
        hidden = ((0, 0, 0), (((0, 1, 2),), ((0, 2, 2),), (None,)))
        equalities = []
        for budget in range(4):
            part = oracle.budget_partition(hidden, budget, hide_cost=True)
            equalities.append(part[0] == part[1])
            self.assertEqual(part[0] == part[1], core.run(hidden, 0, (0,), budget, True)
                             == core.run(hidden, 1, (0,), budget, True))
        self.assertEqual(equalities, [True, False, True, True])
        # Global label-cost factorization is unnecessary when unequal costs belong to distinct actions.
        per_action = ((0, 0, 0), (((0, 1, 2), (0, 2, 2)),
                                ((0, 1, 2), (0, 2, 2)), (None, None)))
        for budget in range(4):
            part = oracle.budget_partition(per_action, budget, hide_cost=True)
            self.assertEqual(part[0], part[1])
        # Resetting resource at the successor destroys the fixed-budget congruence claim.
        reset = ((0, 0, 0, 0), (((0, 1, 2),), ((0, 1, 3),),
                               ((0, 1, 2),), ((1, 1, 3),)))
        zero, one = oracle.budget_partition(reset, 0), oracle.budget_partition(reset, 1)
        self.assertEqual(one[0], one[1])
        self.assertNotEqual(one[2], one[3])
        self.assertEqual(zero[2], zero[3])
        # Mixed containers denote the same labels and cannot create artificial edge mismatches.
        mixed = ([0, 0], ([([0, 1, 0])], [(0, 1, 1)]))
        self.assertIsNone(core.solve(mixed)["distances"][0][1])
        COVERAGE.update(boundary_models=len(fixtures) + 5, hidden_cost_budget_checks=4)

    def test_certificate_corruption(self):
        machine = ((0, 0), (((0, 1, 0), (0, 3, 0)), ((1, 1, 1), (1, 3, 1))))
        good = core.solve(machine)
        self.assertTrue(core.verify(machine, good))
        mutations = []
        def pair(distance, word):
            bad = deepcopy(good)
            for s, t in ((0, 1), (1, 0)):
                bad["distances"][s][t], bad["witnesses"][s][t] = distance, word
            mutations.append(bad)
        for distance, word in [(0, (0,)), (2, (0,)), (None, None), (1, ()),
                               (1, (2,)), (1, (False,)), (True, (0,)), (-1, (0,)),
                               (1.0, (0,)), (1, None), (None, (0,)), (1, "0")]:
            pair(distance, word)
        # Honest expensive witness passes D/D-1 but misses the cheaper local alternative.
        pair(3, (1,))
        bad = deepcopy(good)
        bad["distances"][0][1] = 2
        mutations.append(bad)
        bad = deepcopy(good)
        bad["distances"][0][0], bad["witnesses"][0][0] = 0, ()
        mutations.append(bad)
        mutations.extend([{}, {**good, "extra": 1}, {"distances": [], "witnesses": []},
                          {"distances": [[None]], "witnesses": good["witnesses"]}])
        for bad in mutations:
            with self.assertRaises(ValueError):
                core.verify(machine, bad)
        zero = ((0, 0), (((0, 0, 0),), ((0, 0, 1),)))
        fake = core.solve(zero)
        self.assertTrue(core.verify(zero, fake))
        for s, t in ((0, 1), (1, 0)):
            fake["distances"][s][t], fake["witnesses"][s][t] = 0, (0,)
        with self.assertRaises(ValueError):
            core.verify(zero, fake)
        # Isolate the successor inequality: direct expensive witness is honest,
        # but an equal-event edge reaches a cheaper distinguishing successor.
        linked = ((0, 0, 0, 0), (((0, 1, 2), (0, 4, 0)), ((0, 1, 3), (1, 4, 1)),
                                  ((0, 1, 2), None), ((1, 1, 3), None)))
        honest = core.solve(linked)
        self.assertTrue(core.verify(linked, honest))
        self.assertEqual(honest["distances"][0][1], 2)
        for distance, word in ((4, (1,)), (None, None)):
            bad = deepcopy(honest)
            for s, t in ((0, 1), (1, 0)):
                bad["distances"][s][t], bad["witnesses"][s][t] = distance, word
            with self.assertRaises(ValueError):
                core.verify(linked, bad)
        self.assertEqual(len(mutations), 19)
        COVERAGE["rejected_certificate_mutations"] = len(mutations) + 3

    def test_malformed_inputs(self):
        invalid = [None, (), ((), ()), ((True,), ((),)), ((-1,), ((),)),
                   ((0,), ()), ((0,), (None,)), ((0, 0), ((), (None,)))]
        for edge in ((0, -1, 0), (True, 0, 0), (0, True, 0), (0, 0, True),
                     (0, 0, 1), (0, 0), (0.0, 0, 0), "000"):
            invalid.append(((0,), ((edge,),)))
        rejections = 0
        for machine in invalid:
            for validator in (core.validate, oracle.validate):
                with self.assertRaises(ValueError):
                    validator(machine)
                rejections += 1
        machine = ((0,), (((0, 0, 0),),))
        for runner in (core.run, oracle.response):
            for state in (True, -1, 1, "0"):
                with self.assertRaises(ValueError):
                    runner(machine, state, ())
                rejections += 1
            for word in ((True,), (-1,), (1,), "0", None):
                with self.assertRaises(ValueError):
                    runner(machine, 0, word)
                rejections += 1
            for budget in (True, -1, 0.5, "0"):
                with self.assertRaises(ValueError):
                    runner(machine, 0, (), budget)
                rejections += 1
        for budget in (True, -1, 0.5, "0"):
            with self.assertRaises(ValueError):
                core.classes(core.solve(machine), budget)
            with self.assertRaises(ValueError):
                oracle.budget_partition(machine, budget)
            rejections += 2
        self.assertEqual(rejections, 66)
        COVERAGE["malformed_input_rejections"] = rejections


if __name__ == "__main__":
    unittest.main()
