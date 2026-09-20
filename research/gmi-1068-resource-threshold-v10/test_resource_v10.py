"""Exhaustive threshold checks against independent complete budget products."""
import unittest
from itertools import product
import independent_oracle_v10 as oracle
import threshold_v10 as core

COVERAGE = {}


class ResourceTests(unittest.TestCase):
    def check_pair(self, machine, result, s, t):
        distance = result["distances"][s][t]
        word = result["witnesses"][s][t]
        self.assertEqual(distance, result["distances"][t][s])
        if distance is None:
            self.assertIsNone(word)
            return 0
        self.assertLessEqual(distance, oracle.finite_bound(machine))
        n = len(machine[0])
        self.assertLessEqual(len(word), n * (n - 1) // 2)
        self.assertNotEqual(oracle.response(machine, s, word, distance),
                            oracle.response(machine, t, word, distance))
        if distance:
            self.assertEqual(oracle.response(machine, s, word, distance - 1),
                             oracle.response(machine, t, word, distance - 1))
        return 1

    def test_primary_corpus(self):
        machines = slices = relations = witnesses = 0
        for machine in oracle.primary_machines():
            machines += 1
            result = core.solve(machine)
            self.assertTrue(core.verify(machine, result))
            self.assertIsNone(result["distances"][0][0])
            self.assertIsNone(result["distances"][1][1])
            witnesses += self.check_pair(machine, result, 0, 1)
            previous = None
            for budget in range(oracle.finite_bound(machine) + 1):
                actual = tuple(core.classes(result, budget))
                expected = oracle.budget_partition(machine, budget)
                self.assertEqual(actual, expected)
                for s, t in product(range(2), repeat=2):
                    equal = expected[s] == expected[t]
                    d = result["distances"][s][t]
                    self.assertEqual(equal, d is None or budget < d)
                    if previous is not None and equal:
                        self.assertEqual(previous[s], previous[t])
                    relations += 1
                previous = expected
                slices += 1
        self.assertEqual(machines, 114244)
        self.assertEqual(slices, 214116)
        self.assertEqual(relations, 856464)
        self.assertGreater(witnesses, 0)
        COVERAGE.update(primary_machines=machines, primary_budget_products=slices,
                        primary_ordered_pair_checks=relations, primary_finite_witnesses=witnesses)

    def test_seeded_larger(self):
        machines = slices = witnesses = triangles = relabels = executions = 0
        for machine in oracle.larger_machines():
            machines += 1
            n = len(machine[0])
            result = core.solve(machine)
            self.assertTrue(core.verify(machine, result))
            for s in range(n):
                for t in range(s + 1, n):
                    witnesses += self.check_pair(machine, result, s, t)
            previous, initial_count, changes = None, None, 0
            for budget in range(oracle.finite_bound(machine) + 1):
                expected = oracle.budget_partition(machine, budget)
                self.assertEqual(tuple(core.classes(result, budget)), expected)
                if previous is None:
                    initial_count = len(set(expected))
                else:
                    changes += expected != previous
                    for s, t in product(range(n), repeat=2):
                        if expected[s] == expected[t]:
                            self.assertEqual(previous[s], previous[t])
                previous = expected
                slices += 1
            self.assertLessEqual(changes, n - initial_count)
            for s, t, u in product(range(n), repeat=3):
                d = result["distances"]
                real = lambda value: float("inf") if value is None else value
                self.assertGreaterEqual(real(d[s][u]), min(real(d[s][t]), real(d[t][u])))
                triangles += 1
            obs, rows = machine
            relabeled = (obs[::-1], tuple(tuple(None if e is None else (e[0], e[1], n-1-e[2])
                                                for e in row[::-1]) for row in rows[::-1]))
            moved = core.solve(relabeled)
            for s, t in product(range(n), repeat=2):
                self.assertEqual(result["distances"][s][t], moved["distances"][n-1-s][n-1-t])
                relabels += 1
                for word in ((), (0,), (1,), (0, 1), (1, 0, 1)):
                    for budget in (0, oracle.finite_bound(machine)):
                        self.assertEqual(core.run(machine, s, word, budget) == core.run(machine, t, word, budget),
                                         oracle.response(machine, s, word, budget) == oracle.response(machine, t, word, budget))
                        executions += 1
        self.assertEqual(machines, 40)
        self.assertEqual(triangles, 6200)
        self.assertEqual(relabels, 1080)
        self.assertEqual(executions, 10800)
        COVERAGE.update(larger_machines=machines, larger_budget_products=slices,
                        larger_finite_witnesses=witnesses, triangle_checks=triangles,
                        relabeled_pair_checks=relabels, execution_relation_checks=executions)

    def test_bound_attaining_chains(self):
        chains = 0
        for size in range(2, 9):
            for terminal in (None, (1, 2, size - 1)):
                rows = tuple(((0, 2, i + 1),) if i < size - 1 else (terminal,)
                             for i in range(size))
                machine = (tuple(0 for _ in range(size)), rows)
                result = core.solve(machine)
                self.assertTrue(core.verify(machine, result))
                self.assertEqual(result["distances"][0][1], 2 * (size - 1))
                self.assertEqual(result["distances"][0][1], oracle.finite_bound(machine))
                self.assertEqual(len(result["witnesses"][0][1]), size - 1)
                self.check_pair(machine, result, 0, 1)
                chains += 1
        self.assertEqual(chains, 14)
        COVERAGE["bound_attaining_chains"] = chains


if __name__ == "__main__":
    unittest.main()
