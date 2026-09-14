#!/usr/bin/env python3
"""Controls for TT-1..TT-7, including the enumeration the capsule checker skips.

These raise explicitly rather than using `assert`, because the capsule runs the
suite under -O as well.
"""

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
DCR = HERE.parent / "gmi-delegation-cost-repair-v1"
for _path in (str(DCR), str(HERE)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import check_frontier_v1 as frontier                        # noqa: E402
import frontier_registers_v1 as reg                        # noqa: E402
import minimal_renderings_v1 as enumeration                # noqa: E402
from typed_machine_v1 import execute                       # noqa: E402
from typed_program_v1 import Program, Refusal              # noqa: E402

N4_ARITHMETIC_CAP = 8


def check(condition, message):
    if not condition:
        raise AssertionError(message)


class LayoutContract(unittest.TestCase):
    def test_layout_and_registered_parity3_facts(self):
        layout = frontier.layout_contract()
        check(layout["registered_parity3_facts_reproduced"]["WRITTEN_XOR_CHAIN"] == [11, 0],
              "the registered XOR fact was not reproduced")
        check(layout["registered_parity3_facts_reproduced"]["WRITTEN_SHARED_SUM_NET"] == [39, 4],
              "the registered shared-sum net fact was not reproduced")

    def test_constructs_outside_the_grammar_are_refused_at_parse(self):
        for source in ("def f(x):\n    a, b, c = x\n    return 0 <= a <= 1\n",
                       "def f(x):\n    a, b, c = x\n    return a if b else c\n",
                       "def f(x):\n    a, b, c = x\n    return [a, b, c]\n"):
            with self.assertRaises(Refusal):
                Program({"f": source})

    def test_an_unregistered_callee_is_refused_at_execution_not_costed(self):
        program = Program({"f": "def f(x):\n    a, b, c = x\n    return len(x)\n"})
        with self.assertRaises(Refusal):
            execute(program, "f", (1, 0, 1))


class BudgetFloor(unittest.TestCase):
    def test_registered_written_costs_sit_at_the_budget_floor(self):
        """Every registered written candidate is at or above the 3n+4 floor."""
        for n in (3, 4, 5):
            costs = set()
            for name, row in reg.measure(n).items():
                if row["native_obligations_per_call"] == 0:
                    costs.add(row["python_opcodes_per_call"])
            check(min(costs) == 3 * n + 4, "the floor moved at n=%d: %s" % (n, sorted(costs)))

    def test_three_n_plus_three_is_reachable_in_the_register(self):
        """The repair of TT-2's first version, kept as a standing control.

        TT-2 originally claimed no written realization costs 3n+3. That is false:
        each admitted unary operation costs exactly one opcode, so a unary
        applied to a constant-free binary expression lands on 3n+3. Cursor Bugbot
        raised this on PR #619 and it reproduced. The claim is now that majority
        is not *realizable* there, which the enumeration checks.
        """
        for source, expected in (
                ("def f(x):\n    a, b, c = x\n    return -(a ^ b ^ c)\n", 12),
                ("def f(x):\n    a, b, c = x\n    return ~(a ^ b ^ c)\n", 12),
                ("def f(x):\n    a, b, c = x\n    return not (a ^ b ^ c)\n", 12),
                ("def f(x):\n    a, b, c = x\n    return a ^ (-b) ^ c\n", 12),
                ("def f(x):\n    a, b, c = x\n    return - -(a ^ b ^ c)\n", 13)):
            result = execute(Program({"f": source}), "f", (1, 0, 1))
            check(result.python_opcodes == expected,
                  "unary cost changed: %r gave %d, expected %d"
                  % (source, result.python_opcodes, expected))

    def test_unary_plus_is_refused_not_costed(self):
        """Bugbot's example used unary `+`, which this register does not admit."""
        program = Program({"f": "def f(x):\n    a, b, c = x\n    return +(a ^ b ^ c)\n"})
        with self.assertRaises(Refusal):
            execute(program, "f", (1, 0, 1))
        check("+" not in enumeration.UNARY, "the enumeration admits an op the register refuses")

    def test_parity_reaches_the_constant_free_floor(self):
        source = "def f(x):\n    a, b, c = x\n    return a ^ b ^ c\n"
        result = execute(Program({"f": source}), "f", (1, 1, 0))
        check(result.python_opcodes == 3 * 3 + 2, "the XOR chain is not at the 3n+2 floor")


class ExhaustiveEnumeration(unittest.TestCase):
    def test_majority3_minimum_is_attained_by_both_structures(self):
        survey = enumeration.survey(3, enumeration.majority(3), 32, range(-6, 7))
        check(all(v == [] for v in survey["constant_free_by_unary_count"].values()),
              "majority-3 reached a constant-free budget: %s"
              % (survey["constant_free_by_unary_count"],))
        affine = [r["rendering"] for r in survey["comparison_3n_plus_4"] if r["affine_operand"]]
        other = [r["rendering"] for r in survey["comparison_3n_plus_4"] if not r["affine_operand"]]
        check(len(affine) == 2 and len(other) == 6,
              "the majority-3 minimal set changed: %d affine, %d other" % (len(affine), len(other)))
        check(survey["arithmetic_3n_plus_4"] == ["(((v0 + v1) + v2) >> 1)"],
              "the arithmetic-form minimum changed: %s" % (survey["arithmetic_3n_plus_4"],))

    def test_majority4_has_no_arithmetic_form_minimum(self):
        """The slow half of TT-4, run here rather than inside the capsule checker."""
        survey = enumeration.survey(4, enumeration.majority(4), N4_ARITHMETIC_CAP, range(-6, 7))
        check(survey["arithmetic_3n_plus_4"] == [],
              "an arithmetic-form majority-4 minimum appeared: %s"
              % (survey["arithmetic_3n_plus_4"],))
        check(all(v == [] for v in survey["constant_free_by_unary_count"].values()),
              "majority-4 reached a constant-free budget: %s"
              % (survey["constant_free_by_unary_count"],))

    def test_majority4_constant_free_search_is_saturated_at_cap_64(self):
        """The cap-64 half of the n=4 saturation, moved out of the checker."""
        wide = enumeration.survey(4, enumeration.majority(4), 64, range(-6, 7),
                                  include_arithmetic=False)
        check(all(v == [] for v in wide["constant_free_by_unary_count"].values()),
              "a constant-free majority-4 rendering appeared at cap 64: %s"
              % (wide["constant_free_by_unary_count"],))
        affine = [r["rendering"] for r in wide["comparison_3n_plus_4"] if r["affine_operand"]]
        other = [r["rendering"] for r in wide["comparison_3n_plus_4"] if not r["affine_operand"]]
        check(len(affine) == 2 and len(other) == 8,
              "the n=4 minimal set changed at cap 64: %d affine, %d other"
              % (len(affine), len(other)))

    def test_parity3_is_reachable_without_a_constant(self):
        """A control: the enumeration does find a 3n+2 solution when one exists."""
        survey = enumeration.survey(3, enumeration.parity(3), 32, range(-6, 7))
        check(survey["constant_free_by_unary_count"]["3n+2"],
              "the enumeration missed the XOR chain")

    def test_the_non_affine_rendering_really_computes_majority(self):
        for n in (3, 4):
            rows = reg.measure(n)
            row = rows["NONAFFINE_SHIFT_BOOL"]
            check(row["exact_on_whole_domain"], "the non-affine rendering is wrong at n=%d" % n)
            check(row["python_opcodes_per_call"] == 3 * n + 4,
                  "the non-affine rendering is not at the minimum at n=%d" % n)
        check(not reg.measure(5)["NONAFFINE_SHIFT_BOOL"]["exact_on_whole_domain"],
              "the non-affine rendering unexpectedly extends to n=5")

    def test_affine_classification_rejects_a_non_affine_vector(self):
        check(enumeration.affine_form((0, 0, 0, 1), 2) is None, "AND was classified as affine")
        check(enumeration.affine_form((0, 1, 1, 2), 2) is not None, "a sum was rejected as non-affine")

    def test_enumeration_refuses_outside_its_scope(self):
        with self.assertRaises(enumeration.EnumerationError):
            enumeration.points(7)
        with self.assertRaises(enumeration.EnumerationError):
            enumeration.reachable(3, 0)
        with self.assertRaises(enumeration.EnumerationError):
            enumeration.reachable(3, 32, unary_budget=enumeration.UNARY_BUDGET + 1)
        with self.assertRaises(enumeration.EnumerationError):
            enumeration.survey(3, (0, 1), 32, range(-1, 2))


class Frontiers(unittest.TestCase):
    payload = None

    @classmethod
    def setUpClass(cls):
        cls.payload = frontier.run()

    def test_table_is_task_independent_and_dominated_once_cells_are_charged(self):
        for n in frontier.SCOPE:
            row = self.payload["candidates"][str(n)]["NESTED_CONSTANT_TABLE"]
            check(row["python_opcodes_per_call"] == 3 * n + 4, "TT-1 opcodes changed at n=%d" % n)
            check(row["constant_cells"] == 2 ** n, "TT-1 cells changed at n=%d" % n)
            priced = self.payload["frontier_priced_constant_cells"][str(n)]
            check("THRESHOLD_COMPARISON_BOOL"
                  in priced["strictly_dominated_by"]["NESTED_CONSTANT_TABLE"],
                  "TT-6 domination lost at n=%d" % n)

    def test_no_strict_win_in_the_opcode_coordinate(self):
        for n in frontier.SCOPE:
            sound = self.payload["frontier_honest_unknown_native_cost"][str(n)]
            check(sound["certified_strictly_below"]["NESTED_CONSTANT_TABLE"] == [],
                  "TT-5 was broken at n=%d" % n)
            check("THRESHOLD_COMPARISON_BOOL" in sound["undominated"],
                  "the threshold form left the sound frontier at n=%d" % n)

    def test_flat_index_table_corrects_pn3(self):
        for n in frontier.SCOPE:
            row = self.payload["candidates"][str(n)]["FLAT_INDEX_TABLE"]
            check(row["python_opcodes_per_call"] == 5 * n + 4,
                  "the flat-index rendering is not 5n+4 at n=%d" % n)
            check(row["python_opcodes_per_call"] != 5 * n + 2,
                  "the superseded 5n+2 figure reappeared at n=%d" % n)

    def test_zero_priced_native_artifact_is_recorded_not_used(self):
        for n in frontier.SCOPE:
            projection = self.payload["frontier_opcode_projection"][str(n)]
            check(projection["undominated"] == ["DELEGATING_SUM_COMPARISON"],
                  "the recorded artifact changed at n=%d" % n)

    def test_terminal_and_ceiling(self):
        check(self.payload["terminal"] == frontier.TERMINAL, "terminal changed")
        check("no timing" in self.payload["claim_ceiling"], "the claim ceiling lost its limits")


if __name__ == "__main__":
    unittest.main(verbosity=2)
