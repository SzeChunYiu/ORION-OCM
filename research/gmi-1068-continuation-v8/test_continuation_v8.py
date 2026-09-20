"""Exhaustive operational quotient checks against independent pair BFS."""
import unittest
from itertools import combinations

import continuation_v8 as core
import independent_oracle_v8 as oracle

COVERAGE = {}


class ContinuationTests(unittest.TestCase):
    def record(self, name, count, expected):
        self.assertEqual(count, expected)
        COVERAGE[name] = count

    def test_exhaustive_two_state_machines(self):
        machines = pairs = responses = witnesses = 0
        words = oracle.words(2, 2)
        for observations, transitions in oracle.exhaustive_two_state():
            machine = core.Machine(observations, transitions)
            partition = core.coarsest_partition(machine)
            witness = oracle.distinguish(observations, transitions, 0, 1)
            self.assertEqual(partition[0] == partition[1], witness is None)
            pairs += 1
            if witness is not None:
                self.assertNotEqual(core.run(machine, 0, witness), core.run(machine, 1, witness))
                for shorter in oracle.words(2, len(witness) - 1):
                    self.assertEqual(core.run(machine, 0, shorter), core.run(machine, 1, shorter))
                witnesses += 1
            reduced, mapping = core.quotient(machine, partition)
            for state in range(2):
                for word in words:
                    expected = oracle.response(observations, transitions, state, word)
                    self.assertEqual(core.run(machine, state, word), expected)
                    self.assertEqual(core.run(reduced, mapping[state], word), expected)
                    responses += 1
            machines += 1
        self.record("exhaustive_machines", machines, 59049)
        self.record("exhaustive_pair_comparisons", pairs, machines)
        self.record("exhaustive_response_comparisons", responses, machines * 14)
        # Outcome count is measured, not a presumed count of distinct machines.
        self.assertLessEqual(witnesses, pairs)
        self.assertGreater(witnesses, 0)
        COVERAGE["executed_exhaustive_distinguishers"] = witnesses

    def test_larger_generated_machines_relabeling_and_corrupt_quotients(self):
        machines = pairs = responses = corruptions = 0
        for observations, transitions in oracle.generated_larger():
            machine = core.Machine(observations, transitions)
            partition = core.coarsest_partition(machine)
            self.assertEqual(partition, oracle.partition(observations, transitions))
            reduced, mapping = core.quotient(machine, partition)
            identity, identity_map = core.quotient(machine, tuple(range(len(observations))))
            size = len(observations)
            relabeled = core.Machine(observations[::-1], tuple(
                tuple(None if edge is None else (edge[0], edge[1], size - 1 - edge[2])
                      for edge in row[::-1]) for row in transitions[::-1]))
            for left, right in combinations(range(size), 2):
                witness = oracle.distinguish(observations, transitions, left, right)
                self.assertEqual(partition[left] == partition[right], witness is None)
                if witness is not None:
                    self.assertNotEqual(core.run(machine, left, witness), core.run(machine, right, witness))
                    for shorter in oracle.words(2, len(witness) - 1):
                        self.assertEqual(core.run(machine, left, shorter), core.run(machine, right, shorter))
                pairs += 1
            for state in range(size):
                for word in oracle.words(2, 2):
                    expected = oracle.response(observations, transitions, state, word)
                    self.assertEqual(core.run(reduced, mapping[state], word), expected)
                    self.assertEqual(core.run(identity, identity_map[state], word), expected)
                    self.assertEqual(core.run(relabeled, size - 1 - state, tuple(1 - a for a in word)), expected)
                    responses += 1
            if len(set(partition)) > 1:
                with self.assertRaises(ValueError):
                    core.quotient(machine, (0,) * size)
                corruptions += 1
            machines += 1
        self.record("larger_machines", machines, 64)
        self.record("larger_pair_comparisons", pairs, 544)
        self.record("larger_response_relabel_cases", responses, 2016)
        self.assertGreater(corruptions, 0)
        COVERAGE["rejected_generated_quotient_corruptions"] = corruptions

    def test_budget_product_matches_guarded_execution(self):
        cases = products = 0
        for observations, transitions in oracle.generated_larger():
            machine = core.Machine(observations, transitions)
            for maximum in range(3):
                lifted = core.budget_lift(machine, maximum)
                transported = core.transport_partition_to_budget(core.coarsest_partition(machine), maximum)
                reduced, mapping = core.quotient(lifted, transported)
                products += 1
                for state in range(len(observations)):
                    for remaining in range(maximum + 1):
                        for word in oracle.words(2, 2):
                            expected = oracle.response(observations, transitions, state, word, remaining)
                            self.assertEqual(core.run(machine, state, word, budget=remaining), expected)
                            self.assertEqual(core.run(lifted, state * (maximum + 1) + remaining, word), expected)
                            self.assertEqual(core.run(reduced, mapping[state * (maximum + 1) + remaining], word), expected)
                            cases += 1
        self.record("budget_products", products, 192)
        self.record("budget_execution_comparisons", cases, 12096)

    def test_long_chains_and_incomplete_continuation_tests(self):
        chains = 0
        for size in range(3, 11):
            observations = (0,) * size
            transitions = tuple(((int(i == size - 1), 0, min(i + 1, size - 1)),) for i in range(size))
            machine = core.Machine(observations, transitions)
            witness = oracle.distinguish(observations, transitions, 0, 1)
            self.assertEqual(witness, (0,) * (size - 1))
            for word in oracle.words(1, size - 2):
                self.assertEqual(core.run(machine, 0, word), core.run(machine, 1, word))
            self.assertNotEqual(core.run(machine, 0, witness), core.run(machine, 1, witness))
            self.assertEqual(core.coarsest_partition(machine), tuple(range(size)))
            with self.assertRaises(ValueError):
                core.quotient(machine, (0, 0) + tuple(range(1, size - 1)))
            chains += 1
        self.record("long_distinguishing_chains", chains, 8)
        # Pending successor observation mismatch must beat a deeper edge mismatch.
        observations = (0, 0, 0, 0, 0, 1)
        transitions = (((0, 0, 2), (0, 0, 4)), ((0, 0, 3), (0, 0, 5)),
                       ((0, 0, 2), (0, 0, 2)), ((1, 0, 3), (0, 0, 3)),
                       ((0, 0, 4), (0, 0, 4)), ((0, 0, 5), (0, 0, 5)))
        self.assertEqual(oracle.distinguish(observations, transitions, 0, 1), (1,))

    def test_undefined_cost_and_residual_budget_boundaries(self):
        undefined = core.Machine((None, None), ((None,), ((0, 0, 1),)))
        self.assertEqual(core.run(undefined, 0, ()), core.run(undefined, 1, ()))
        self.assertNotEqual(core.run(undefined, 0, (0,)), core.run(undefined, 1, (0,)))
        # An empty observation-context product erases values, not legality:
        # its quotient is not the vacuous universal intersection of relations.
        self.assertEqual(oracle.partition(undefined.observations, undefined.transitions), (0, 1))
        costly = core.Machine((0, 0), (((0, 0, 0),), ((0, 1, 1),)))
        self.assertEqual(core.coarsest_partition(costly), (0, 1))
        for word in oracle.words(1, 4):
            a, b = (core.run(costly, state, word) for state in (0, 1))
            erase_cost = lambda trace: tuple(token[:2] if token[0] == "EDGE" else token for token in trace)
            self.assertEqual(erase_cost(a), erase_cost(b))
        # A spent budget hides later output distinctions; resetting it is unsound.
        machine = core.Machine((0, 0, 0, 0), (((0, 1, 2),), ((0, 1, 3),),
                                           ((0, 1, 2),), ((1, 1, 3),)))
        for word in oracle.words(1, 4):
            self.assertEqual(core.run(machine, 0, word, budget=1), core.run(machine, 1, word, budget=1))
        self.assertNotEqual(core.run(machine, 2, (0,), budget=1), core.run(machine, 3, (0,), budget=1))
        self.assertEqual(core.run(machine, 2, (0,), budget=0), core.run(machine, 3, (0,), budget=0))
        self.assertEqual(core.run(costly, 0, (0,) * 4, budget=0), core.run(costly, 0, (0,) * 4))

    def test_total_cost_only_and_noncongruent_exact_representation(self):
        machine = core.Machine((0,) * 5, (((0, 1, 2),), ((0, 0, 3),),
                                       ((0, 0, 4),), ((0, 1, 4),), (None,)))
        traces = [core.run(machine, state, (0, 0)) for state in (0, 1)]
        self.assertEqual([sum(t[2] for t in trace if t[0] == "EDGE") for trace in traces], [1, 1])
        self.assertEqual(traces[0][-1], traces[1][-1])
        self.assertNotEqual(traces[0], traces[1])
        redundant = core.Machine((0,) * 4, (((0, 0, 2),), ((0, 0, 3),),
                                          ((0, 0, 2),), ((0, 0, 3),)))
        self.assertEqual(core.coarsest_partition(redundant), (0, 0, 0, 0))
        with self.assertRaises(ValueError):
            core.quotient(redundant, (0, 0, 1, 2))

    def test_nondeterministic_trace_equality_is_not_bisimulation(self):
        observations = (0,) * 6
        transitions = ((((0, 0, 2),),), (((0, 0, 3), (0, 0, 4)),),
                       (((0, 0, 5), (1, 0, 5)),), (((0, 0, 5),),),
                       (((1, 0, 5),),), (((0, 0, 5),),))
        for word in oracle.words(1, 8):
            self.assertEqual(oracle.nondeterministic_responses(observations, transitions, 0, word),
                             oracle.nondeterministic_responses(observations, transitions, 1, word))
        self.assertNotIn((0, 1), oracle.nondeterministic_bisimulation(observations, transitions))

    def test_malformed_inputs_and_quotient_certificates(self):
        malformed = [((), ()), ((0,), ((),)), ((True,), ((None,),)), ((-1,), ((None,),)),
                     ((0, 1), ((None,),)), ((0,), (((0, -1, 0),),)),
                     ((0,), (((0, True, 0),),)), ((0,), (((0, 0, 1),),)),
                     ((0,), (((False, 0, 0),),)), ((0,), (((0, 0),),))]
        for observations, transitions in malformed:
            with self.assertRaises(ValueError):
                core.coarsest_partition(core.Machine(observations, transitions))
        machine = core.Machine((0, 1), ((None,), (None,)))
        for bad in ((), (0,), (False, 1), (0, -1), (0, 0)):
            with self.assertRaises(ValueError):
                core.quotient(machine, bad)
        for bad in (-1, True, 1.0):
            with self.assertRaises(ValueError):
                core.budget_lift(machine, bad)
            with self.assertRaises(ValueError):
                core.run(machine, 0, (), budget=bad)
        for state, word in ((True, ()), (-1, ()), (2, ()), (0, (True,)), (0, (1,)), (0, (-1,))):
            with self.assertRaises(ValueError):
                core.run(machine, state, word)


if __name__ == "__main__":
    unittest.main()
