"""Exhaustive candidate operations and actual typed monoidal calibration."""
import importlib.util
from itertools import permutations, product
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


oracle, core = load("independent_oracle_v13"), load("optional_v13")
COVERAGE = {}


class OptionalTests(unittest.TestCase):
    def test_actual_reset_category(self):
        functions = oracle.BIT_FUNCTIONS
        self.assertEqual(len(set(functions)), 3)
        equations = associativity = 0
        inverse_pairs = []
        for a, b in product(range(3), repeat=2):
            actual = oracle.compose_functions(functions[a], functions[b])
            self.assertEqual(functions[core.RESET_COMPOSITION[a][b]], actual)
            reverse = oracle.compose_functions(functions[b], functions[a])
            self.assertEqual(core.RESET_COMPOSITION[a][b] == core.RESET_COMPOSITION[b][a], actual == reverse)
            if actual == functions[0] == reverse:
                inverse_pairs.append((a, b))
            equations += 1
        for a, b, c in product(range(3), repeat=3):
            self.assertEqual(oracle.reset_composite(oracle.reset_composite(functions[a], functions[b]), functions[c]),
                             oracle.reset_composite(functions[a], oracle.reset_composite(functions[b], functions[c])))
            associativity += 1
        self.assertTrue(core.associative(core.RESET_COMPOSITION))
        self.assertTrue(core.unit_laws(core.RESET_COMPOSITION, 0))
        self.assertEqual(core.inverses(core.RESET_COMPOSITION, 0), tuple(inverse_pairs))
        self.assertEqual(inverse_pairs, [(0, 0)])
        for a in functions:
            self.assertEqual(oracle.compose_functions(functions[0], a), a)
            self.assertEqual(oracle.compose_functions(a, functions[0]), a)
        self.assertNotEqual(oracle.compose_functions(functions[1], functions[2]),
                            oracle.compose_functions(functions[2], functions[1]))
        COVERAGE.update(actual_compositions=equations, actual_inverse_pair_checks=equations,
                        actual_commutation_checks=equations, actual_associativity_equations=associativity,
                        actual_unit_equations=2 * len(functions))

    def test_all_binary_operations(self):
        count = normalized = associative = equations = failed = relabelings = 0
        records = []
        for candidate in oracle.operations():
            expected_assoc, expected_unit = oracle.candidate_properties(candidate)
            self.assertEqual(core.associative(candidate), expected_assoc)
            self.assertEqual(core.unit_laws(candidate, 0), expected_unit)
            count += 1
            associative += expected_assoc
            if not expected_unit:
                continue
            normalized += 1
            checks = oracle.interchange_equations(candidate)
            failures = [word for word, equal in checks if not equal]
            equations += len(checks)
            failure = core.interchange_failure(core.RESET_COMPOSITION, candidate)
            self.assertTrue(failures)
            self.assertEqual(failure, failures[0])
            records.append((candidate, failure))
            failed += 1
            for permutation in permutations(range(3)):
                seq = oracle.rename(core.RESET_COMPOSITION, permutation)
                tensor = oracle.rename(candidate, permutation)
                self.assertTrue(core.unit_laws(seq, permutation[0]))
                self.assertTrue(core.unit_laws(tensor, permutation[0]))
                expected = min(tuple(permutation[i] for i in word) for word in failures)
                self.assertEqual(core.interchange_failure(seq, tensor), expected)
                relabelings += 1
        self.assertEqual(count, 19683)
        self.assertEqual(normalized, 81)
        self.assertEqual(equations, 6561)
        self.assertEqual(failed, 81)
        self.assertEqual(relabelings, 486)
        self.assertTrue(oracle.verify_obstruction(records))
        COVERAGE.update(binary_operations=count, associative_operations=associative,
                        common_unit_operations=normalized, interchange_equations=equations,
                        actual_failed_candidates=failed, relabeled_candidates=relabelings,
                        complete_obstruction_certificates=1)

    def test_c2_positive_control(self):
        functions = ((0, 1), (1, 0))
        table = tuple(tuple(functions.index(oracle.compose_functions(a, b)) for b in functions) for a in functions)
        self.assertTrue(core.associative(table))
        self.assertTrue(core.unit_laws(table, 0))
        self.assertEqual(core.inverses(table, 0), ((0, 0), (1, 1)))
        self.assertIsNone(core.interchange_failure(table, table))
        checked = 0
        for a, b, c, d in product(functions, repeat=4):
            left = oracle.compose_functions(oracle.compose_functions(a, b), oracle.compose_functions(c, d))
            right = oracle.compose_functions(oracle.compose_functions(a, c), oracle.compose_functions(b, d))
            self.assertEqual(left, right)
            checked += 1
        self.assertEqual(checked, 16)
        COVERAGE["positive_c2_interchange_equations"] = checked

    def test_typed_monoidal_models(self):
        homs = compositions = incompatible = tensors = triples = interchanges = units = identities = blocked = 0
        composition_triples = 0
        for model in ("discrete", "product"):
            actual = oracle.arrows(model == "product")
            arrows = tuple((oracle.BIT_FUNCTIONS.index(obj), bit) for obj, bit in actual)
            decode = lambda arrow: (oracle.BIT_FUNCTIONS[arrow[0]], arrow[1])
            for source, target in product(range(3), repeat=2):
                expected = tuple(a for a in arrows if a[0] == source) if source == target else ()
                self.assertEqual(core.hom(model, source, target), expected)
                homs += 1
                unit_tensor = core.tensor(model, core.identity(model, source), core.identity(model, target))
                self.assertEqual(unit_tensor, core.identity(model, core.RESET_COMPOSITION[source][target]))
                identities += 1
            composable = []
            for a, b in product(arrows, repeat=2):
                self.assertEqual(decode(core.tensor(model, a, b)), oracle.parallel(decode(a), decode(b)))
                tensors += 1
                if a[0] == b[0]:
                    self.assertEqual(decode(core.compose(model, a, b)), oracle.sequential(decode(a), decode(b)))
                    composable.append((a, b))
                    compositions += 1
                else:
                    with self.assertRaises(ValueError):
                        core.compose(model, a, b)
                    incompatible += 1
            for a in arrows:
                self.assertEqual(core.compose(model, core.identity(model, a[0]), a), a)
                self.assertEqual(core.compose(model, a, core.identity(model, a[0])), a)
                self.assertEqual(core.tensor(model, core.identity(model, 0), a), a)
                self.assertEqual(core.tensor(model, a, core.identity(model, 0)), a)
                units += 4
            for a, b, c in product(arrows, repeat=3):
                self.assertEqual(core.tensor(model, core.tensor(model, a, b), c),
                                 core.tensor(model, a, core.tensor(model, b, c)))
                triples += 1
                if a[0] == b[0] == c[0]:
                    composition_triples += 1
                    self.assertEqual(core.compose(model, core.compose(model, a, b), c),
                                     core.compose(model, a, core.compose(model, b, c)))
            for (a, b), (c, d) in product(composable, repeat=2):
                self.assertEqual(core.tensor(model, core.compose(model, a, b), core.compose(model, c, d)),
                                 core.compose(model, core.tensor(model, a, c), core.tensor(model, b, d)))
                interchanges += 1
            forward = core.tensor(model, core.identity(model, 1), core.identity(model, 2))[0]
            backward = core.tensor(model, core.identity(model, 2), core.identity(model, 1))[0]
            self.assertNotEqual(forward, backward)
            self.assertEqual(core.hom(model, forward, backward), ())
            blocked += 1
        self.assertEqual((homs, compositions, incompatible, tensors, triples, interchanges, units, identities, blocked),
                         (18, 15, 30, 45, 243, 153, 36, 18, 2))
        self.assertEqual(composition_triples, 27)
        COVERAGE.update(composition_associativity_equations=composition_triples, typed_hom_sets=homs, typed_compositions=compositions,
                        incompatible_composition_rejections=incompatible, typed_tensors=tensors,
                        tensor_associativity_equations=triples, typed_interchange_equations=interchanges,
                        typed_unit_equations=units, tensor_identity_equations=identities,
                        empty_braiding_hom_sets=blocked)


if __name__ == "__main__":
    unittest.main()
