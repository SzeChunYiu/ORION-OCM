"""Independent exact synthesis, certificate and compiler falsification checks."""
import copy
import unittest
from itertools import product

from independent_oracle_v6 import (
    ASSIGNMENTS, certificate_is_valid, cost_layers, measured_cost, pack, source,
    stack_execute,
)
from machine_v6 import compile_ast, execute, run_program
from synthesis_v6 import ast_cost, eval_ast, swap_inputs, synthesize, truth_table, validate_certificate

COVERAGE = {"functions": 16, "witness_cases": 64, "composition_inequalities": 256,
            "compiled_prefix_cases": 448, "machine_transition_cases": 10192,
            "mutated_certificates": 71, "input_relabel_cases": 64}
STACKS = tuple(s for length in range(3) for s in product((0, 1), repeat=length))


class SynthesisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = synthesize()
        cls.oracle = cost_layers(31)

    def test_independent_exact_costs_and_lower_bound_certificates(self):
        self.assertEqual(len(self.records), COVERAGE["functions"])
        self.assertEqual({k: v["cost"] for k, v in self.records.items()},
                         {k: v["cost"] for k, v in self.oracle.items()})
        for records in (self.records, self.oracle):
            self.assertTrue(certificate_is_valid(records))
            self.assertEqual(validate_certificate(records),
                             {k: COVERAGE[k] for k in
                              ("functions", "witness_cases", "composition_inequalities")})

    def test_actual_source_and_compiled_execution_with_stack_prefixes(self):
        witnesses = prefixes = 0
        for semantic, record in self.records.items():
            ast, code = record["ast"], compile_ast(record["ast"])
            self.assertEqual(ast_cost(ast), measured_cost(ast))
            self.assertEqual(len(code), record["cost"])
            self.assertEqual(truth_table(ast), semantic)
            for x, y in ASSIGNMENTS:
                expected = source(ast, x, y)
                self.assertEqual(eval_ast(ast, x, y), expected)
                self.assertEqual(run_program(code, x, y), expected)
                witnesses += 1
                for prefix in STACKS:
                    self.assertEqual(execute(code, x, y, stack=prefix), prefix + (expected,))
                    self.assertEqual(execute(code, x, y, stack=prefix),
                                     stack_execute(code, x, y, prefix))
                    prefixes += 1
        self.assertEqual(witnesses, COVERAGE["witness_cases"])
        self.assertEqual(prefixes, COVERAGE["compiled_prefix_cases"])

    def test_all_short_instruction_streams_against_separate_interpreter(self):
        checked = 0
        for length in range(6):
            for code in product(("PUSH_X", "PUSH_Y", "NAND"), repeat=length):
                for x, y in ASSIGNMENTS:
                    for prefix in STACKS:
                        try:
                            expected = stack_execute(code, x, y, prefix)
                        except ValueError:
                            with self.assertRaises(ValueError):
                                execute(code, x, y, stack=prefix)
                        else:
                            self.assertEqual(execute(code, x, y, stack=prefix), expected)
                        checked += 1
        self.assertEqual(checked, COVERAGE["machine_transition_cases"])

    def test_mutated_certificates_fail_both_checkers(self):
        mutations = []
        for semantic in self.records:
            missing = copy.deepcopy(self.records)
            del missing[semantic]
            mutations.append(missing)
            bad_cost = copy.deepcopy(self.records)
            bad_cost[semantic]["cost"] += 1
            mutations.append(bad_cost)
            wrong_witness = copy.deepcopy(self.records)
            replacement = "y" if semantic == truth_table("x") else "x"
            wrong_witness[semantic] = {"ast": replacement, "cost": 1}
            mutations.append(wrong_witness)
            # Same semantics, honest measured cost: isolates lower-bound checks.
            inflated = copy.deepcopy(self.records)
            ast = self.records[semantic]["ast"]
            negated = ("nand", ast, ast)
            twice_negated = ("nand", negated, negated)
            self.assertEqual(pack(source(twice_negated, x, y) for x, y in ASSIGNMENTS), semantic)
            inflated[semantic] = {"ast": twice_negated, "cost": measured_cost(twice_negated)}
            mutations.append(inflated)
        for record in ({"ast": "x", "cost": False}, {"ast": "bad", "cost": 1},
                       {"cost": 1}, {"ast": "x"}, None):
            damaged = copy.deepcopy(self.records)
            damaged[0] = record
            mutations.append(damaged)
        bool_key = copy.deepcopy(self.records)
        bool_key[False] = bool_key.pop(0)
        mutations += [bool_key, {**self.records, 16: {"ast": "x", "cost": 1}}]
        self.assertEqual(len(mutations), COVERAGE["mutated_certificates"])
        for index, records in enumerate(mutations):
            with self.subTest(index=index):
                self.assertFalse(certificate_is_valid(records))
                with self.assertRaises(ValueError):
                    validate_certificate(records)

    def test_changed_costs_and_premature_stopping_are_not_certified(self):
        changed = cost_layers(31, nand_cost=2)
        self.assertEqual(set(changed), set(self.records))
        self.assertNotEqual({k: v["cost"] for k, v in changed.items()},
                            {k: v["cost"] for k, v in self.records.items()})
        premature = cost_layers(3)
        self.assertLess(len(premature), len(self.records))
        for records in (changed, premature):
            self.assertFalse(certificate_is_valid(records))
            with self.assertRaises(ValueError):
                validate_certificate(records)

    def test_negative_grammars_and_relabeling(self):
        for core_args, oracle_args in (({"terminal_order": ("x",)}, {"terminals": ("x",)}),
                                       ({"allow_nand": False}, {"allow_nand": False})):
            actual, expected = synthesize(**core_args), cost_layers(31, **oracle_args)
            self.assertEqual({k: v["cost"] for k, v in actual.items()},
                             {k: v["cost"] for k, v in expected.items()})
            self.assertLess(len(actual), len(self.records))
            with self.assertRaises(ValueError):
                validate_certificate(actual)
        reordered = synthesize(terminal_order=("y", "x"))
        self.assertEqual({k: v["cost"] for k, v in reordered.items()},
                         {k: v["cost"] for k, v in self.records.items()})
        checked = 0
        for record in self.records.values():
            swapped = swap_inputs(record["ast"])
            self.assertEqual(ast_cost(swapped), record["cost"])
            for x, y in ASSIGNMENTS:
                self.assertEqual(eval_ast(swapped, x, y), source(record["ast"], y, x))
                checked += 1
        self.assertEqual(checked, COVERAGE["input_relabel_cases"])

    def test_malformed_asts_bits_and_programs(self):
        bad_asts = (None, True, 0, "z", ("nand", "x"), ("and", "x", "y"),
                    ["nand", "x", "y"], ("nand", "x", "z"))
        for ast in bad_asts:
            for operation in (ast_cost, truth_table, compile_ast, swap_inputs):
                with self.subTest(ast=ast, operation=operation.__name__), self.assertRaises(ValueError):
                    operation(ast)
        for bad in (True, False, 2, -1, 0.0, "0", None):
            for x, y in ((bad, 0), (0, bad)):
                with self.assertRaises(ValueError):
                    eval_ast("x", x, y)
                with self.assertRaises(ValueError):
                    execute(("PUSH_X",), x, y)
            with self.assertRaises(ValueError):
                execute((), 0, 0, stack=(bad,))
        for code in (("BAD",), ("NAND",), ("PUSH_X", "NAND"), (1,), (True,)):
            with self.assertRaises(ValueError):
                execute(code, 0, 0)
        for code in ((), ("PUSH_X", "PUSH_Y")):
            with self.assertRaises(ValueError):
                run_program(code, 0, 0)
        for record in self.records.values():
            with self.assertRaises(ValueError):
                run_program(compile_ast(record["ast"])[:-1], 0, 0)
        for terminals in ((), ("z",), ("x", "x")):
            with self.assertRaises(ValueError):
                synthesize(terminal_order=terminals)


    def test_malformed_outer_contracts_and_no_partial_stack_mutation(self):
        for invalid in (None, True, 1, "x", []):
            with self.assertRaises(ValueError):
                validate_certificate(invalid)
        for invalid in (None, True, 1, "PUSH_X", {"PUSH_X": 1}):
            with self.assertRaises(ValueError):
                execute(invalid, 0, 0)
            with self.assertRaises(ValueError):
                execute((), 0, 0, stack=invalid)
        for args in ({"allow_nand": 1}, {"stats": []}, {"terminal_order": "xy"}):
            with self.assertRaises(ValueError):
                synthesize(**args)
        prefix = [0]
        with self.assertRaises(ValueError):
            execute(("PUSH_X", "NAND", "NAND"), 1, 0, stack=prefix)
        self.assertEqual(prefix, [0])


if __name__ == "__main__":
    unittest.main()
