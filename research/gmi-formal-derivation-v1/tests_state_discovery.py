"""Exact bounded transducer learning versus independent product exploration."""
from collections import deque
from fractions import Fraction as F
from itertools import product
import unittest


def machines(n):
    entries = tuple(product(range(n), range(2)))
    return [(n, table) for table in product(entries, repeat=2*n)]


def output(machine, word):
    _, table = machine
    state, result = 0, []
    for symbol in word:
        state, emitted = table[2*state+symbol]
        result.append(emitted)
    return tuple(result)


def product_disagreement(left, right):
    """All reachable pair states, without imposing a word length cutoff."""
    queue, seen = deque([(0, 0, ())]), {(0, 0)}
    while queue:
        u, v, prefix = queue.popleft()
        for symbol in range(2):
            nu, ou = left[1][2*u+symbol]
            nv, ov = right[1][2*v+symbol]
            word = prefix + (symbol,)
            if ou != ov:
                return word
            if (nu, nv) not in seen:
                seen.add((nu, nv))
                queue.append((nu, nv, word))
    return None


class StateAcquisitionWitnesses(unittest.TestCase):
    def test_all_bounded_tables_have_complete_query_certificate(self):
        universe = machines(1) + machines(2)
        self.assertEqual(len(universe), 260)
        queries = list(product(range(2), repeat=3))
        self.assertEqual(len(queries), 8)
        self.assertEqual(sum(map(len, queries)), 24)
        signatures = [tuple(output(m, w) for w in queries) for m in universe]
        old_queries = [w for length in range(1, 5)
                       for w in product(range(2), repeat=length)]
        old_signatures = [tuple(output(m, w) for w in old_queries) for m in universe]
        comparisons = 0
        for i, left in enumerate(universe):
            for j, right in enumerate(universe):
                witness = product_disagreement(left, right)
                self.assertEqual(signatures[i] == signatures[j], witness is None)
                self.assertEqual(old_signatures[i] == old_signatures[j], witness is None)
                if witness is not None:
                    self.assertLessEqual(len(witness), left[0]*right[0])
                    self.assertLessEqual(len(witness), left[0]+right[0]-1)
                    self.assertNotEqual(output(left, witness), output(right, witness))
                comparisons += 1
        self.assertEqual(comparisons, 67600)
        # Learn from the actual complete query answers, not hidden state IDs.
        for i, target in enumerate(universe):
            retained = min((m for m, sig in zip(universe, signatures)
                            if sig == signatures[i]), key=lambda m: m[0])
            self.assertIsNone(product_disagreement(target, retained))

    def test_short_queries_and_absent_bound_are_insufficient(self):
        constant = (1, ((0, 0), (0, 0)))
        delayed = (2, ((1, 0), (1, 0), (1, 1), (1, 1)))
        for symbol in range(2):
            self.assertEqual(output(constant, (symbol,)), output(delayed, (symbol,)))
        self.assertNotEqual(output(constant, (0, 0)), output(delayed, (0, 0)))
        for observed_length in range(1, 8):
            table = tuple((min(s+1, observed_length), int(s == observed_length))
                          for s in range(observed_length+1) for _ in range(2))
            hidden_chain = (observed_length+1, table)
            self.assertEqual(output(hidden_chain, (0,)*observed_length),
                             output(constant, (0,)*observed_length))
            self.assertNotEqual(output(hidden_chain, (0,)*(observed_length+1)),
                                output(constant, (0,)*(observed_length+1)))

    def test_positive_mass_floor_support_recovery_and_countercontrol(self):
        n, floor, alpha = 32, F(1, 4), F(1, 20)
        bound = 2 * (1-floor)**n
        self.assertLess(bound, alpha)
        for p in (F(0), floor, F(1, 2), 1-floor, F(1)):
            missing_probability = p**n + (1-p)**n if 0 < p < 1 else F(0)
            self.assertLessEqual(missing_probability, bound)
        # Same fixed n cannot exclude an arbitrarily small nonzero probability.
        rare = F(1, 10000)
        self.assertGreater((1-rare)**n, F(99, 100))

    def test_acquisition_end_state_requires_transport_or_reset(self):
        parity = (2, ((1, 1), (1, 1), (0, 0), (0, 0)))
        # A valid overestimate m=3 leads to a final word of length 2m-1=5.
        prefix = (0,)*5
        from_physical_current = output(parity, prefix+(0,))[-1]
        from_learned_root = output(parity, (0,))[-1]
        self.assertNotEqual(from_physical_current, from_learned_root)
        # An equivalent learned table uses swapped state IDs (root is now1).
        learned_table = ((1, 0), (1, 0), (0, 1), (0, 1))
        learned_state = 1
        for symbol in prefix:
            learned_state, _ = learned_table[2*learned_state+symbol]
        _, transported = learned_table[2*learned_state]
        self.assertEqual(transported, from_physical_current)


if __name__ == "__main__":
    unittest.main()
