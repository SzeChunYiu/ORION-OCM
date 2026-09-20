"""Independent finite reconstruction of recoverability and typed countermodels."""
import unittest
from itertools import permutations, product

import independent_semantic_v9 as oracle
import semantic_v9 as core

MAPS = tuple(product(range(3), repeat=3))
TARGETS = tuple(product(range(2), repeat=3))
OBJECTIVES = tuple(product(range(2), repeat=4))
COVERAGE = {}


class SemanticTests(unittest.TestCase):
    def record(self, name, actual, expected):
        self.assertEqual(actual, expected)
        COVERAGE[name] = actual

    def test_every_map_against_all_decoder_assignments(self):
        problems = assignments = collisions = recoverable = 0
        for reduct, target in product(MAPS, TARGETS):
            witnesses = oracle.decoders(reduct, target, (0, 1))
            self.assertLessEqual(len(witnesses), 1)
            actual = core.decoder(reduct, target)
            self.assertEqual(actual, witnesses[0] if witnesses else None)
            for candidate in oracle.candidates(reduct, (0, 1)):
                self.assertEqual(core.verify_decoder(reduct, target, candidate), candidate in witnesses)
                assignments += 1
            collision = core.collision(reduct, target)
            self.assertEqual(collision is None, bool(witnesses))
            if collision is not None:
                first, second = collision
                self.assertNotEqual(first, second)
                self.assertEqual(reduct[first], reduct[second])
                self.assertNotEqual(target[first], target[second])
                collisions += 1
            recoverable += int(bool(witnesses))
            problems += 1
        self.record("map_problems", problems, 216)
        self.record("candidate_decoder_assignments", assignments, 1008)
        self.record("recoverable_maps", recoverable, 126)
        self.record("executed_collision_witnesses", collisions, 90)

    def test_all_presentation_permutations(self):
        checked = 0
        for reduct, target in product(MAPS, TARGETS):
            process_names = {p: 3 * p + 7 for p in set(reduct)}
            objective_names = {o: 5 * o + 11 for o in set(target)}
            original = core.decoder(reduct, target)
            for ordering in permutations(range(3)):
                renamed_p, renamed_o = core.presentation(reduct, target, ordering,
                                                         process_names, objective_names)
                expected_p = tuple(process_names[reduct[i]] for i in ordering)
                expected_o = tuple(objective_names[target[i]] for i in ordering)
                self.assertEqual((renamed_p, renamed_o), (expected_p, expected_o))
                candidates = oracle.decoders(renamed_p, renamed_o, tuple(objective_names.values()))
                self.assertEqual(core.decoder(renamed_p, renamed_o), candidates[0] if candidates else None)
                if original is not None:
                    self.assertEqual(candidates[0], {process_names[p]: objective_names[o]
                                                    for p, o in original.items()})
                checked += 1
        self.record("presentation_cases", checked, 1296)

    def test_ambient_category_and_every_admission_objective_history(self):
        compositions = histories = attainable = 0
        for first, second in product(range(4), repeat=2):
            try:
                expected = oracle.composition(first, second)
            except ValueError:
                with self.assertRaises(ValueError):
                    core.compose(first, second)
            else:
                self.assertEqual(core.compose(first, second), expected)
            compositions += 1
        for mask in range(4):
            admitted = oracle.admitted_arrows(mask)
            self.assertTrue({0, 1} <= admitted)
            self.assertEqual(admitted, frozenset(a for a in range(4) if core.admitted(mask, a)))
            for first, second in product(admitted, repeat=2):
                try:
                    composite = oracle.composition(first, second)
                except ValueError:
                    continue
                self.assertIn(composite, admitted)
            for objective, start in product(OBJECTIVES, range(2)):
                for path in oracle.paths(4):
                    try:
                        expected = oracle.history(mask, objective, start, path)
                    except ValueError:
                        with self.assertRaises(ValueError):
                            core.evaluate_history(mask, objective, start, path)
                    else:
                        self.assertEqual(core.evaluate_history(mask, objective, start, path), expected)
                    histories += 1
                self.assertEqual(core.attainable(mask, objective, start),
                                 oracle.attainable_by_paths(mask, objective, start))
                attainable += 1
        self.record("ambient_composition_cases", compositions, 16)
        self.record("history_cases", histories, 43648)
        self.record("attainable_set_cases", attainable, 128)

    def test_typed_countermodels_and_actual_ranking_reversal(self):
        first, second = (0, 0, 0, 1), (0, 0, 1, 0)
        # Same process/admission; different total evaluators on the SAME 4 arrows.
        self.assertEqual(len(first), len(second))
        self.assertNotEqual(core.attainable(1, first, 0), core.attainable(1, second, 0))
        # Same total evaluator; admission alone changes legal histories and values.
        self.assertIsNone(core.evaluate_history(0, second, 0, (2,)))
        self.assertEqual(core.evaluate_history(1, second, 0, (2,)), 1)
        self.assertNotEqual(core.attainable(0, second, 0), core.attainable(1, second, 0))
        ranks = [tuple(core.evaluate_history(3, objective, 0, (arrow,)) for arrow in (2, 3))
                 for objective in (first, second)]
        self.assertLess(ranks[0][0], ranks[0][1])
        self.assertGreater(ranks[1][0], ranks[1][1])
        self.assertIsNone(core.decoder((1, 1), tuple(ranks[i][0] for i in range(2))))
        admission_results = tuple(int(core.evaluate_history(mask, second, 0, (2,)) is not None)
                                  for mask in (0, 1))
        self.assertIsNone(core.decoder((0, 0), admission_results))

    def test_empty_image_and_corrupted_decoder_controls(self):
        self.assertEqual(core.decoder((), ()), {})
        self.assertTrue(core.verify_decoder((), (), {}))
        self.assertEqual(oracle.decoders((), (), (), domain=()), ({},))
        self.assertEqual(oracle.decoders((), (), (), domain=(0,)), ())
        self.assertEqual(oracle.decoders((), (), (1,), domain=(0,)), ({0: 1},))
        reduct, target = (0, 1, 0), (1, 0, 1)
        self.assertFalse(core.verify_decoder(reduct, target, {0: 0, 1: 0}))
        for candidate in ({0: 1}, {0: 1, 1: 0, 2: 0}, {False: 1, 1: 0}, {0: True, 1: 0}):
            with self.assertRaises(ValueError):
                core.verify_decoder(reduct, target, candidate)

    def test_all_binary_operations_and_unique_units(self):
        operations = associations = 0
        for entries in product(range(2), repeat=4):
            table = (entries[:2], entries[2:])
            self.assertEqual(core.binary_units(table), oracle.units(table))
            self.assertLessEqual(len(oracle.units(table)), 1)
            agreements = []
            for word in product(range(2), repeat=3):
                agreements.append(oracle.left_fold(table, word) == oracle.right_fold(table, word))
                associations += 1
            self.assertEqual(core.associative(table), all(agreements))
            operations += 1
        no_unit = ((0, 0), (1, 1))
        self.assertTrue(core.associative(no_unit))
        self.assertEqual(core.binary_units(no_unit), ())
        self.record("binary_operations", operations, 16)
        self.record("associativity_equations", associations, 128)

    def test_malformed_tables_histories_presentations_and_operations(self):
        for reduct, target in (([0], (0,)), ((0,), ()), ((False, 0), (0, 0)), ((0,), (-1,))):
            for operation in (core.decoder, core.collision):
                with self.assertRaises(ValueError):
                    operation(reduct, target)
        for args in ((True, (0, 0, 0, 0), 0, ()), (0, (0, 0), 0, ()),
                     (0, (False, 0, 0, 0), 0, ()), (0, (0, 0, 0, 0), True, ()),
                     (0, (0, 0, 0, 0), 0, (True,)), (0, (0, 0, 0, 0), 0, (1,))):
            with self.assertRaises(ValueError):
                core.evaluate_history(*args)
        for ordering, names in (((0, 0), {0: 0, 1: 1}), ((False, 1), {0: 0, 1: 1}),
                               ((0, 1), {0: 3, 1: 3}), ((0, 1), {False: 0, 1: 1})):
            with self.assertRaises(ValueError):
                core.presentation((0, 1), (0, 1), ordering, names, {0: 0, 1: 1})
        for table in ((), ((0,), (1,)), ((False, 1), (1, 0)), ((0, 2), (1, 0))):
            with self.assertRaises(ValueError):
                core.binary_units(table)


if __name__ == "__main__":
    unittest.main()
