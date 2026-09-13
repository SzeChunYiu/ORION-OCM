"""Exact finite REP/REAL/ARCH witnesses; run on billy-laptop only.

Tests check constructions and failure witnesses, not universal proofs.
The reference interpreter, partition refinement and neural block use different
mechanisms. Exhaustive coverage includes all 256 two-state binary Mealy tables.
"""

import itertools
import unittest
from fractions import Fraction


def words(alphabet_size, max_length):
    for length in range(max_length + 1):
        yield from itertools.product(range(alphabet_size), repeat=length)


def tables(state_count, input_count=2, output_count=2):
    entries = tuple(itertools.product(range(state_count), range(output_count)))
    yield from itertools.product(entries, repeat=state_count * input_count)


def trace(table, state, word, input_count=2):
    outputs = []
    for symbol in word:
        state, output = table[state * input_count + symbol]
        outputs.append(output)
    return state, tuple(outputs)


def residual_classes(table, state_count, input_count=2):
    """Fixed-point partition refinement, without a bounded-word cutoff."""
    labels = (0,) * state_count
    while True:
        signatures = []
        for state in range(state_count):
            signatures.append(
                tuple(
                    (table[state * input_count + symbol][1],
                     labels[table[state * input_count + symbol][0]])
                    for symbol in range(input_count)
                )
            )
        unique = []
        next_labels = []
        for signature in signatures:
            if signature not in unique:
                unique.append(signature)
            next_labels.append(unique.index(signature))
        next_labels = tuple(next_labels)
        if next_labels == labels:
            return labels
        labels = next_labels


def compiled_block(table, one_hot_state, one_hot_input, output_count=2,
                   threshold=False):
    """Explicit indicator layer and sparse readout, independently from trace."""
    state_count = len(one_hot_state)
    input_count = len(one_hot_input)
    indicators = [
        [int(s + x >= Fraction(3, 2)) if threshold else max(0, s + x - 1)
         for x in one_hot_input]
        for s in one_hot_state
    ]
    next_state = [0] * state_count
    output = [0] * output_count
    for state in range(state_count):
        for symbol in range(input_count):
            destination, emitted = table[state * input_count + symbol]
            indicator = indicators[state][symbol]
            next_state[destination] += indicator
            output[emitted] += indicator
    return tuple(next_state), tuple(output)


def one_hot(index, size):
    return tuple(int(position == index) for position in range(size))


class RepresentationTests(unittest.TestCase):
    def test_all_two_state_tables_compile_exactly_for_every_short_stream(self):
        count = 0
        for table in tables(2):
            count += 1
            for initial_state in range(2):
                for word in words(2, 4):
                    reference_state, reference_outputs = trace(
                        table, initial_state, word
                    )
                    for threshold in (False, True):
                        state = one_hot(initial_state, 2)
                        emitted = []
                        for symbol in word:
                            state, output = compiled_block(
                                table, state, one_hot(symbol, 2),
                                threshold=threshold,
                            )
                            self.assertEqual(sum(state), 1)
                            self.assertEqual(sum(output), 1)
                            self.assertTrue(set(state).issubset({0, 1}))
                            emitted.append(output.index(1))
                        self.assertEqual(state, one_hot(reference_state, 2))
                        self.assertEqual(tuple(emitted), reference_outputs)
        self.assertEqual(count, 256)

    def test_singleton_state_input_output_embedding(self):
        state, output = compiled_block(((0, 0),), (1,), (1,), output_count=1)
        self.assertEqual((state, output), ((1,), (1,)))

    def test_wrong_gate_negative_control_breaks_one_hot_invariant(self):
        state, symbol = (1, 0), (1, 0)
        wrong = tuple(int(s + x >= 1) for s in state for x in symbol)
        self.assertEqual(sum(wrong), 3)
        self.assertNotEqual(sum(wrong), 1)

    def test_partition_agrees_with_independent_exhaustive_profiles(self):
        for table in tables(2):
            labels = residual_classes(table, 2)
            profiles = [
                tuple(trace(table, state, word)[1] for word in words(2, 4))
                for state in range(2)
            ]
            for left in range(2):
                for right in range(2):
                    equivalent = labels[left] == labels[right]
                    self.assertEqual(equivalent, profiles[left] == profiles[right])
                    if equivalent:
                        for symbol in range(2):
                            ls, lo = table[2 * left + symbol]
                            rs, ro = table[2 * right + symbol]
                            self.assertEqual(lo, ro)
                            self.assertEqual(labels[ls], labels[rs])

    def test_finite_horizon_equality_is_not_right_congruence(self):
        # q0 emits zero forever; q1 emits 0 then 1, then reaches q0.
        table = ((0, 0), (2, 0), (0, 1))
        self.assertEqual(trace(table, 0, (0,), 1)[1], (0,))
        self.assertEqual(trace(table, 1, (0,), 1)[1], (0,))
        left = trace(table, 0, (0,), 1)[0]
        right = trace(table, 1, (0,), 1)[0]
        self.assertNotEqual(
            trace(table, left, (0,), 1)[1], trace(table, right, (0,), 1)[1]
        )
        self.assertNotEqual(
            residual_classes(table, 3, 1)[0], residual_classes(table, 3, 1)[1]
        )

    def test_minimal_two_state_behavior_has_no_one_state_realizer(self):
        parity = ((0, 0), (1, 1), (1, 1), (0, 0))
        self.assertEqual(len(set(residual_classes(parity, 2))), 2)
        for candidate in tables(1):
            witnesses = [
                word for word in words(2, 2)
                if trace(candidate, 0, word)[1] != trace(parity, 0, word)[1]
            ]
            self.assertTrue(witnesses)

    def test_equal_observed_policy_does_not_identify_controlled_law(self):
        first = ((0, 0), (0, 0))
        second = ((0, 0), (0, 1))
        for length in range(6):
            self.assertEqual(
                trace(first, 0, (0,) * length)[1],
                trace(second, 0, (0,) * length)[1],
            )
        self.assertNotEqual(trace(first, 0, (1,))[1], trace(second, 0, (1,))[1])

if __name__ == "__main__":
    unittest.main()
