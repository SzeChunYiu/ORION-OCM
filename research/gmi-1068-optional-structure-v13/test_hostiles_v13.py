"""Complete obstruction evidence, weak-unit naturality, and malformed controls."""
from copy import deepcopy
import importlib.util
from itertools import product
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


class OptionalHostiles(unittest.TestCase):
    def test_obstruction_corruptions(self):
        records = [(table, core.interchange_failure(core.RESET_COMPOSITION, table))
                   for table in oracle.normalized_operations()]
        self.assertTrue(oracle.verify_obstruction(records))
        bad_records = [[], records[:1], records[:-1], records[:-1] + [records[0]]]
        for bad_failure in (None, (0, 0, 0, 0), (True, 0, 0, 0), (0.0, 0, 0, 0), (0, 1), "PASS"):
            bad = deepcopy(records)
            bad[0] = bad[0][0], bad_failure
            bad_records.append(bad)
        bad = deepcopy(records)
        bad[0] = ((0, 0, 0),) * 3, bad[0][1]
        bad_records.append(bad)
        # Erasing noncommutativity changes the actual process under examination.
        commutative = tuple(tuple(max(a, b) for b in range(3)) for a in range(3))
        self.assertIsNone(core.interchange_failure(commutative, commutative))
        bad = deepcopy(records)
        bad[0] = commutative, None
        bad_records.append(bad)
        rejected = 0
        for bad in bad_records:
            with self.assertRaises(ValueError):
                oracle.verify_obstruction(bad)
            rejected += 1
        self.assertEqual(rejected, 12)
        COVERAGE["obstruction_certificate_rejections"] = rejected

    def test_weak_unitors_and_one_sided_inverse(self):
        reset = core.RESET_COMPOSITION
        checks = naturality = 0
        # Actual bit functions have no invertibles beyond identity.
        functions = oracle.BIT_FUNCTIONS
        invertible = tuple(i for i, a in enumerate(functions) if any(
            oracle.compose_functions(a, b) == functions[0] == oracle.compose_functions(b, a)
            for b in functions))
        self.assertEqual(invertible, (0,))
        for candidate in oracle.normalized_operations():
            for left, right in product(range(3), repeat=2):
                self.assertFalse(core.weak_tensor_necessary(reset, 0, candidate, left, right))
                checks += 1
        c2 = ((0, 1), (1, 0))
        c2_functions = ((0, 1), (1, 0))
        # Mixed unitors test necessary conditions only, not full monoidal sufficiency.
        for left, right in product(range(2), repeat=2):
            self.assertTrue(core.weak_tensor_necessary(c2, 0, c2, left, right))
            checks += 1
            for a in range(2):
                for unit_arrow in (left, right):
                    self.assertEqual(oracle.compose_functions(c2_functions[a], c2_functions[unit_arrow]),
                                     oracle.compose_functions(c2_functions[unit_arrow], c2_functions[a]))
                    naturality += 1
        # Identity preservation and interchange alone do not imply naturality.
        constant = ((0, 0, 0),) * 3
        self.assertIsNone(core.interchange_failure(reset, constant))
        self.assertFalse(core.weak_tensor_necessary(reset, 0, constant, 0, 0))
        checks += 1
        self.assertNotEqual(oracle.reset_composite(oracle.actual_operation(constant, functions[0], functions[1]), functions[0]),
                            oracle.reset_composite(functions[0], functions[1]))
        # A lawful finite-function retraction is only one-sided across unequal objects.
        inclusion, retraction = (0, 1), (0, 1, 1)
        self.assertEqual(oracle.compose_functions(inclusion, retraction), (0, 1))
        self.assertNotEqual(oracle.compose_functions(retraction, inclusion), (0, 1, 2))
        self.assertEqual((checks, naturality), (734, 16))
        COVERAGE.update(weak_unitor_necessity_checks=checks, actual_unitor_naturality_equations=naturality,
                        one_sided_inverse_controls=1, actual_naturality_failure_controls=1)

    def test_malformed_inputs(self):
        count = 0
        for table in (None, (), [], ((0,), (0,)), ((False,),), ((0.0,),), ((-1,),), ((1,),), "0"):
            for validator in (core.validate_table, oracle.table):
                with self.assertRaises(ValueError):
                    validator(table)
                count += 1
        for unit in (True, 0.0, -1, 3, "0"):
            for operation in (core.unit_laws, core.inverses):
                with self.assertRaises(ValueError):
                    operation(core.RESET_COMPOSITION, unit)
                count += 1
        nonassociative = next(t for t in oracle.normalized_operations() if not oracle.candidate_properties(t)[0])
        with self.assertRaises(ValueError):
            core.inverses(nonassociative, 0)
        count += 1
        for unit in (1, 2):
            with self.assertRaises(ValueError):
                core.inverses(core.RESET_COMPOSITION, unit)
            count += 1
        with self.assertRaises(ValueError):
            core.interchange_failure(((0,),), core.RESET_COMPOSITION)
        count += 1
        for model in (None, "unknown", True):
            with self.assertRaises(ValueError):
                core.hom(model, 0, 0)
            count += 1
        for obj in (True, 0.0, -1, 3):
            with self.assertRaises(ValueError):
                core.identity("product", obj)
            count += 1
        for arrow in (None, (), (True, 0), (0.0, 0), (0, True), (0, 0.0), (3, 0), (0, 2)):
            for operation in (core.compose, core.tensor):
                with self.assertRaises(ValueError):
                    operation("product", arrow, (0, 0))
                count += 1
        for operation in (core.compose, core.tensor):
            with self.assertRaises(ValueError):
                operation("discrete", (0, 1), (0, 0))
            count += 1
        for value in (True, 0.0, -1, 3):
            for left, right in ((value, 0), (0, value)):
                with self.assertRaises(ValueError):
                    core.weak_tensor_necessary(core.RESET_COMPOSITION, 0, core.RESET_COMPOSITION, left, right)
                count += 1
        self.assertEqual(core.validate_table([[0, 1], [1, 0]]), ((0, 1), (1, 0)))
        self.assertEqual(core.compose("product", [0, 1], [0, 1]), (0, 0))
        self.assertEqual(count, 65)
        COVERAGE["malformed_input_rejections"] = count


if __name__ == "__main__":
    unittest.main()
