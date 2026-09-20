"""Third route: residual-pair exploration, plus coherent certificate corruptions."""
import collections
import copy
import json
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import threshold_v10 as T
import certificate_v10 as C
import coverage_v10 as G

COVERAGE = {}


def equivalent(machine, s, t, resource):
    """Explore actual paired executions, without constructing threshold edges."""
    observations, rows = machine
    todo = collections.deque([(s, resource, t, resource)])
    seen = set()
    while todo:
        current = todo.popleft()
        if current in seen:
            continue
        seen.add(current)
        s, left_resource, t, right_resource = current
        if observations[s] != observations[t]:
            return False
        for action in range(len(rows[0])):
            left, right = rows[s][action], rows[t][action]
            left_ok = left is not None and left[1] <= left_resource
            right_ok = right is not None and right[1] <= right_resource
            if left_ok != right_ok:
                return False
            if left_ok:
                if tuple(left[:2]) != tuple(right[:2]):
                    return False
                todo.append((left[2], left_resource - left[1],
                             right[2], right_resource - right[1]))
    return True


def cases():
    rng = random.Random(106810)
    for _ in range(200):
        n, width = rng.randrange(1, 6), rng.randrange(4)
        observations = [rng.randrange(2) for _ in range(n)]
        rows = [[None if rng.randrange(4) == 0 else
                 [rng.randrange(2), rng.randrange(4), rng.randrange(n)]
                 for _ in range(width)] for _ in range(n)]
        if rng.randrange(2):
            rows = tuple(tuple(row) for row in rows)
        yield observations, rows


class IndependentReview(unittest.TestCase):
    def test_seeded_mixed_models_and_corruptions(self):
        count = comparisons = mutants = infinite_mutants = 0
        for machine in cases():
            count += 1
            result = T.solve(machine)
            self.assertTrue(C.verify(machine, result))
            n = len(machine[0])
            maximum = max((e[1] for row in machine[1] for e in row if e is not None), default=0)
            bound = (n - len(set(machine[0]))) * maximum
            for s in range(n):
                for t in range(s + 1, n):
                    distance = result['distances'][s][t]
                    for resource in range(bound + 3):
                        self.assertEqual(equivalent(machine, s, t, resource),
                                         distance is None or resource < distance)
                        comparisons += 1
                    bad_values = [None, 0, 1, False, -1, 0.5, '0', []]
                    if distance is not None:
                        bad_values.append(distance + 1)
                    for bad in bad_values:
                        if type(bad) is type(distance) and bad == distance:
                            continue
                        damaged = copy.deepcopy(result)
                        damaged['distances'][s][t] = damaged['distances'][t][s] = bad
                        with self.assertRaises(ValueError):
                            C.verify(machine, damaged)
                        mutants += 1
                    if distance is not None:
                        damaged = copy.deepcopy(result)
                        damaged['distances'][s][t] = damaged['distances'][t][s] = None
                        damaged['witnesses'][s][t] = damaged['witnesses'][t][s] = None
                        with self.assertRaises(ValueError):
                            C.verify(machine, damaged)
                        infinite_mutants += 1
        COVERAGE.update(seed=106810, machines=count, residual_pair_comparisons=comparisons,
                        distance_mutants=mutants, coherent_infinity_mutants=infinite_mutants)

    def test_coverage_guards(self):
        baseline = copy.deepcopy(G.REQUIRED)
        positive = ("primary_finite_witnesses", "larger_finite_witnesses", "larger_budget_products")
        baseline["test_resource_v10"].update({key: 1 for key in positive})
        self.assertTrue(G.validate_coverage(baseline))
        rejected = 0
        for module, required in G.REQUIRED.items():
            absent = copy.deepcopy(baseline)
            del absent[module]
            with self.assertRaises(ValueError):
                G.validate_coverage(absent)
            rejected += 1
            for key, value in required.items():
                for bad in (value + 1, True, None):
                    damaged = copy.deepcopy(baseline)
                    damaged[module][key] = bad
                    with self.assertRaises(ValueError):
                        G.validate_coverage(damaged)
                    rejected += 1
                damaged = copy.deepcopy(baseline)
                del damaged[module][key]
                with self.assertRaises(ValueError):
                    G.validate_coverage(damaged)
                rejected += 1
        for key in positive:
            for bad in (0, None, True):
                damaged = copy.deepcopy(baseline)
                damaged["test_resource_v10"][key] = bad
                with self.assertRaises(ValueError):
                    G.validate_coverage(damaged)
                rejected += 1
        COVERAGE["coverage_guard_rejections"] = rejected

    def test_zero_cycles_and_delayed_witness(self):
        zero = ([0, 0], [[[0, 0, 0]], [[0, 0, 1]]])
        self.assertIsNone(T.solve(zero)['distances'][0][1])
        five = ([0, 0], [[[0, 0, 0], [0, 5, 0]], [[0, 0, 1], None]])
        result = T.solve(five)
        self.assertEqual(result['distances'][0][1], 5)
        self.assertTrue(C.verify(five, result))
        delayed = ([0, 0], [[[0, 1, 0], [0, 1, 0]], [[0, 1, 1], [1, 1, 1]]])
        result = T.solve(delayed)
        result['distances'][0][1] = result['distances'][1][0] = 2
        result['witnesses'][0][1] = result['witnesses'][1][0] = (0, 1)
        self.assertNotEqual(T.run(delayed, 0, (0, 1), 2), T.run(delayed, 1, (0, 1), 2))
        self.assertEqual(T.run(delayed, 0, (0, 1), 1), T.run(delayed, 1, (0, 1), 1))
        with self.assertRaisesRegex(ValueError, 'local sink'):
            C.verify(delayed, result)
        COVERAGE.update(zero_cycle_controls=2, delayed_nonminimal_witness_rejected=1)

    def test_malformed_models_and_certificate_structure(self):
        malformed = [([], []), ([0], []), ([False], [[]]), ([0], [[[0, False, 0]]]),
                     ([0], [[[0, -1, 0]]]), ([0], [[[0, 1, 1]]]),
                     ([0, 0], [[], [None]]), ([0], [[[0, 1]]])]
        for machine in malformed:
            with self.assertRaises(ValueError):
                T.solve(machine)
        machine = ([0, 1], [[], []])
        good = T.solve(machine)
        bad = [None, {}, {**good, 'certified': True}, {**good, 'distances': []},
               {**good, 'witnesses': [[], []]}, {**good, 'distances': [[None, 0], [None, None]]},
               {**good, 'witnesses': [[None, (False,)], [(False,), None]]},
               {**good, 'distances': [[0, 0], [0, None]]}]
        for result in bad:
            with self.assertRaises(ValueError):
                C.verify(machine, result)
        COVERAGE.update(malformed_models=len(malformed), malformed_certificates=len(bad))


if __name__ == '__main__':
    program = unittest.main(exit=False)
    print(json.dumps(COVERAGE, sort_keys=True))
    raise SystemExit(0 if program.result.wasSuccessful() else 1)
