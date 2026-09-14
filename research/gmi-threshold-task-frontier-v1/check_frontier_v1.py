#!/usr/bin/env python3
"""Complete finite payload for the threshold-task frontier theorem TT-1..TT-7.

Emits one JSON object on stdout. Every number is produced here: the candidate
costs come from DCR's typed machine, the minimality statements come from the
exhaustive enumeration in `minimal_renderings_v1`, and the frontiers are
computed from those two sources under the two declared cost readings.
"""

import json
import platform
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
DCR = HERE.parent / "gmi-delegation-cost-repair-v1"
for _path in (str(DCR), str(HERE)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import frontier_registers_v1 as reg                        # noqa: E402
import minimal_renderings_v1 as enumeration                # noqa: E402
from cost_contracts_v1 import additive_bounds              # noqa: E402
from typed_machine_v1 import execute                       # noqa: E402
from typed_program_v1 import Program                       # noqa: E402

TERMINAL = "GRAND_GMI_THRESHOLD_TASK_FRONTIER_GREEN_AT_FINITE_SCOPE"
CLAIM_CEILING = (
    "one task family, one code grammar, one interpreter opcode layout and one "
    "declared constant-cell count; no timing, no physical memory and no coverage "
    "of the realizations nobody has written"
)
SCOPE = (3, 4, 5, 6, 7, 8)
CONSTANTS = tuple(range(-6, 7))
WIDE_CONSTANTS = tuple(range(-12, 13))


class CheckError(ValueError):
    """A registered check did not hold."""


def require(condition, message):
    if not condition:
        raise CheckError(message)


def layout_contract():
    """Validate the per-construct opcode layout this payload is stated against.

    The contract is the one the parity-n registration used: reading an n-tuple
    through UNPACK_SEQUENCE costs n + 2, each further input read costs 1, each
    binary operation and each comparison costs 1, each constant load costs 1, and
    RETURN_VALUE costs 1. If an interpreter emits a different layout this raises
    rather than silently restating different numbers as the same theorem.
    """
    probes = {
        "unpack_and_return_3": ("def f(x):\n    a, b, c = x\n    return a\n", 3 + 2 + 1 + 1),
        "xor_chain_3": ("def f(x):\n    a, b, c = x\n    return a ^ b ^ c\n", 11),
        "threshold_compare_3": ("def f(x):\n    a, b, c = x\n    return (a + b + c) >= 2\n", 13),
        "store_then_compare_3": ("def f(x):\n    a, b, c = x\n    s = a + b + c\n"
                                 "    return s >= 2\n", 15),
        "native_int_call": ("def f(x):\n    a, b, c = x\n    return int(a + b + c)\n", 13),
        # Each admitted unary operation costs exactly one opcode, which is why
        # 3n+3 is a reachable budget. TT-2's first version denied that.
        "unary_negate_3": ("def f(x):\n    a, b, c = x\n    return -(a ^ b ^ c)\n", 12),
        "unary_invert_3": ("def f(x):\n    a, b, c = x\n    return ~(a ^ b ^ c)\n", 12),
        "unary_not_3": ("def f(x):\n    a, b, c = x\n    return not (a ^ b ^ c)\n", 12),
        "two_unary_3": ("def f(x):\n    a, b, c = x\n    return - -(a ^ b ^ c)\n", 13),
    }
    measured = {}
    for name, (source, expected) in sorted(probes.items()):
        result = execute(Program({"f": source}), "f", (1, 0, 1))
        measured[name] = result.python_opcodes
        require(result.python_opcodes == expected,
                "opcode layout differs from the registered contract at %s: %d != %d"
                % (name, result.python_opcodes, expected))
    registered_parity3 = {
        "WRITTEN_XOR_CHAIN": (11, 0),
        "WRITTEN_SHARED_SUM_NET": (39, 4),
        "DELEGATING_SUM_AND_MASK": (6, 1),
    }
    sources = {
        "WRITTEN_XOR_CHAIN": "def f(x):\n    a, b, c = x\n    return a ^ b ^ c\n",
        "WRITTEN_SHARED_SUM_NET":
            "def f(x):\n    a, b, c = x\n    s = a - b - c\n    h0 = int(s >= 1)\n"
            "    h1 = int(s >= 0)\n    h2 = int(s >= -1)\n"
            "    return int((h0 - h1 + h2) >= 1)\n",
        "DELEGATING_SUM_AND_MASK": "def f(x):\n    return sum(x) & 1\n",
    }
    replayed = {}
    for name, (opcodes, natives) in sorted(registered_parity3.items()):
        program = Program({"f": sources[name]})
        seen = set()
        for bits in reg.points(3):
            result = execute(program, "f", bits)
            require(result.value == reg.parity(bits), "parity witness failed: " + name)
            seen.add((result.python_opcodes,
                      sum(not e.startswith("py:") for e in result.events)))
        require(seen == {(opcodes, natives)},
                "registered parity-3 fact not reproduced: %s %s" % (name, sorted(seen)))
        replayed[name] = [opcodes, natives]
    # Unary `+` is refused rather than costed: CPython 3.12 compiles it to
    # CALL_INTRINSIC_1, which the typed machine does not account. The
    # enumeration's unary set therefore omits it.
    refused = "def f(x):\n    a, b, c = x\n    return +(a ^ b ^ c)\n"
    try:
        execute(Program({"f": refused}), "f", (1, 0, 1))
    except Exception as exc:                      # noqa: BLE001 - recorded, not handled
        unary_plus = type(exc).__name__ + ": " + str(exc)
    else:
        raise CheckError("unary + is no longer refused by the typed register")
    return {"probe_opcode_counts": measured,
            "unary_plus_refusal": unary_plus,
            "registered_parity3_facts_reproduced": replayed,
            "interpreter": "%s %d.%d" % (platform.python_implementation(),
                                         sys.version_info[0], sys.version_info[1])}


def interval(row, reading):
    """(lower, upper) total cost; upper is None when it is not finite."""
    events = ["py:X"] * row["python_opcodes_per_call"]
    events += ["native:call:%d" % i for i in range(row["native_obligations_per_call"])]
    if reading == "python_projection":
        contracts = {name: (1, 1) if name.startswith("py:") else (0, 0) for name in events}
    elif reading == "honest_unknown":
        contracts = {name: (1, 1) for name in events if name.startswith("py:")}
    else:
        raise CheckError("unknown reading: " + str(reading))
    lower, upper = additive_bounds(tuple(events), contracts)
    return lower, upper


def certified(a, b):
    """DCR's rule: a strict claim needs a's finite upper below b's lower."""
    al, au = a
    bl, bu = b
    if au is not None and au < bl:
        return "CERTIFIED_STRICTLY_LOWER"
    if bu is not None and bu < al:
        return "CERTIFIED_STRICTLY_HIGHER"
    if au is not None and bu is not None and al == au == bl == bu:
        return "EXACT_TIE"
    return "UNVERIFIABLE"


def scalar_frontier(rows, reading):
    """Names no other candidate is certified strictly below, plus the matrix."""
    bounds = {name: interval(row, reading) for name, row in rows.items()}
    relations, undominated = {}, []
    for name in sorted(rows):
        beaten_by = sorted(other for other in rows if other != name
                           and certified(bounds[other], bounds[name])
                           == "CERTIFIED_STRICTLY_LOWER")
        relations[name] = beaten_by
        if not beaten_by:
            undominated.append(name)
    return {"reading": reading,
            "bounds": {name: [str(lo), None if hi is None else str(hi)]
                       for name, (lo, hi) in sorted(bounds.items())},
            "certified_strictly_below": relations,
            "undominated": undominated}


def product_frontier(rows, require_exact_int=False):
    """Product order on (python_opcodes, constant_cells) over native-free members.

    A candidate carrying a native obligation is excluded and listed separately:
    its total cost has no finite upper endpoint, so it takes no place in an
    ordering of exact costs.
    """
    eligible = {name: row for name, row in rows.items()
                if row["native_obligations_per_call"] == 0
                and row["exact_on_whole_domain"]
                and (not require_exact_int or row["return_type"] == ["int"])}
    excluded = sorted(set(rows) - set(eligible))

    def point(row):
        return (row["python_opcodes_per_call"], row["constant_cells"])

    dominated = {}
    for name, row in eligible.items():
        a = point(row)
        beaten_by = []
        for other, orow in eligible.items():
            if other == name:
                continue
            b = point(orow)
            if b[0] <= a[0] and b[1] <= a[1] and b != a:
                beaten_by.append(other)
        dominated[name] = sorted(beaten_by)
    return {"points": {name: list(point(row)) for name, row in sorted(eligible.items())},
            "strictly_dominated_by": {k: v for k, v in sorted(dominated.items())},
            "undominated": sorted(n for n in eligible if not dominated[n]),
            "excluded_for_unbounded_or_inexact_cost": excluded,
            "int_typed_obligation": require_exact_int}


def formula(rows_by_n, name, field):
    """Exact affine fit a*n+b over the whole scope, or None when not affine."""
    present = [n for n in SCOPE if name in rows_by_n[n] and rows_by_n[n][name]["exact_on_whole_domain"]]
    if len(present) < 2:
        return None
    n0, n1 = present[0], present[1]
    y0, y1 = rows_by_n[n0][name][field], rows_by_n[n1][name][field]
    if (n1 - n0) == 0 or (y1 - y0) % (n1 - n0):
        return None
    a = (y1 - y0) // (n1 - n0)
    b = y0 - a * n0
    if all(rows_by_n[n][name][field] == a * n + b for n in present):
        return {"a": a, "b": b, "holds_for_n": present}
    return None


def run():
    layout = layout_contract()
    rows_by_n = {n: reg.measure(n) for n in SCOPE}

    exact = {n: {name: row for name, row in rows_by_n[n].items()
                 if row["exact_on_whole_domain"]} for n in SCOPE}

    # TT-1: the nested constant table is exactly 3n+4 with 2**n cells, on every n.
    for n in SCOPE:
        table = rows_by_n[n]["NESTED_CONSTANT_TABLE"]
        require(table["python_opcodes_per_call"] == 3 * n + 4,
                "nested table is not 3n+4 at n=%d" % n)
        require(table["constant_cells"] == 2 ** n, "nested table cells not 2**n at n=%d" % n)
        require(table["native_obligations_per_call"] == 0, "nested table delegates at n=%d" % n)
        flat = rows_by_n[n]["FLAT_INDEX_TABLE"]
        require(flat["python_opcodes_per_call"] == 5 * n + 4,
                "flat-index table is not 5n+4 at n=%d" % n)

    # TT-5: the threshold comparison ties the table in the opcode coordinate and
    # is two dearer once the obligation is int-typed.
    for n in SCOPE:
        table = rows_by_n[n]["NESTED_CONSTANT_TABLE"]["python_opcodes_per_call"]
        bool_form = rows_by_n[n]["THRESHOLD_COMPARISON_BOOL"]
        int_form = rows_by_n[n]["THRESHOLD_COMPARISON_INT"]
        require(bool_form["python_opcodes_per_call"] == table,
                "the Boolean threshold form does not tie the table at n=%d" % n)
        require(int_form["python_opcodes_per_call"] == table + 2,
                "the int-typed threshold form is not table+2 at n=%d" % n)
        require(rows_by_n[n]["THRESHOLD_SHIFT_INT"]["exact_on_whole_domain"] == (n == 3),
                "the shift rendering's exactness changed at n=%d" % n)
        require(rows_by_n[n]["NONAFFINE_SHIFT_BOOL"]["exact_on_whole_domain"] == (n in (3, 4)),
                "the non-affine rendering's exactness changed at n=%d" % n)

    formulas = {}
    for name in sorted(rows_by_n[SCOPE[0]]):
        formulas[name] = {"python_opcodes_per_call": formula(rows_by_n, name, "python_opcodes_per_call"),
                          "constant_cells": formula(rows_by_n, name, "constant_cells")}

    surveys = {}
    for cap in (32, 64, 256):
        surveys["n3_cap%d" % cap] = enumeration.survey(3, enumeration.majority(3), cap, CONSTANTS)
    surveys["n3_cap32_wide_constants"] = enumeration.survey(
        3, enumeration.majority(3), 32, WIDE_CONSTANTS)
    # n=4 at cap 32 here; the cap-64 saturation and the n=4 one-constant
    # arithmetic search live in the unit test, which has no 60-second allowance.
    surveys["n4_cap32_comparison_shape"] = enumeration.survey(
        4, enumeration.majority(4), 32, CONSTANTS, include_arithmetic=False)

    # TT-3: majority needs a constant, so nothing reaches 3n+2, 3n+3 or the
    # two-unary 3n+4 shape. The unary budgets are the repair: the first version
    # of this enumeration searched binary operations only.
    for key, survey in sorted(surveys.items()):
        free = survey["constant_free_by_unary_count"]
        require(sorted(free) == ["3n+2", "3n+3", "3n+4"],
                "the constant-free budget layers changed in " + key)
        for budget, hits in sorted(free.items()):
            require(hits == [], "a constant-free %s rendering of majority appeared in %s: %s"
                    % (budget, key, hits))

    # TT-4: the 3n+4 optimum is attained by a threshold form and by a non-affine
    # form, so minimal cost does not force the threshold structure.
    saturation = {}
    for key, survey in sorted(surveys.items()):
        affine = sorted(row["rendering"] for row in survey["comparison_3n_plus_4"]
                        if row["affine_operand"])
        other = sorted(row["rendering"] for row in survey["comparison_3n_plus_4"]
                       if not row["affine_operand"])
        require(affine, "no affine minimal rendering in " + key)
        require(other, "no non-affine minimal rendering in " + key)
        saturation[key] = {
            "affine": affine, "non_affine": other,
            "arithmetic": survey["arithmetic_3n_plus_4"],
            "constant_free_by_unary_count": survey["constant_free_by_unary_count"],
            "distinct_value_vectors_by_unary_count":
                survey["distinct_value_vectors_by_unary_count"]}
    base = saturation["n3_cap32"]
    for key in ("n3_cap64", "n3_cap256", "n3_cap32_wide_constants"):
        require(saturation[key] == base,
                "the n=3 enumeration is not saturated: " + key + " differs from n3_cap32")
    n4 = saturation["n4_cap32_comparison_shape"]
    require(len(n4["affine"]) == 2 and len(n4["non_affine"]) == 8,
            "the n=4 minimal set changed: %d affine, %d non-affine"
            % (len(n4["affine"]), len(n4["non_affine"])))

    opcode_frontier = {n: scalar_frontier(exact[n], "python_projection") for n in SCOPE}
    honest_frontier = {n: scalar_frontier(exact[n], "honest_unknown") for n in SCOPE}
    priced = {n: product_frontier(rows_by_n[n]) for n in SCOPE}
    priced_int = {n: product_frontier(rows_by_n[n], require_exact_int=True) for n in SCOPE}

    # TT-6: once a constant cell costs anything, the 2**n table is strictly
    # dominated by the threshold rendering, at every n in scope.
    for n in SCOPE:
        beaten = priced[n]["strictly_dominated_by"]["NESTED_CONSTANT_TABLE"]
        require("THRESHOLD_COMPARISON_BOOL" in beaten,
                "the table is not dominated by the threshold form at n=%d" % n)
        require("THRESHOLD_COMPARISON_BOOL" in priced[n]["undominated"],
                "the threshold form is not on the priced frontier at n=%d" % n)
        require("NESTED_CONSTANT_TABLE" not in priced[n]["undominated"],
                "the table is still undominated at n=%d" % n)

    # TT-7: under DCR's sound reading, where an unbounded native obligation makes
    # a total cost have no finite upper endpoint, the threshold form is
    # undominated in the opcode coordinate and nothing is certified below the
    # table -- so the threshold family can tie but never strictly win there.
    for n in SCOPE:
        require("THRESHOLD_COMPARISON_BOOL" in honest_frontier[n]["undominated"],
                "the threshold form is dominated in the sound reading at n=%d" % n)
        require(honest_frontier[n]["certified_strictly_below"]["NESTED_CONSTANT_TABLE"] == [],
                "something is certified below the table at n=%d" % n)
        require(honest_frontier[n]["certified_strictly_below"]["THRESHOLD_COMPARISON_BOOL"] == [],
                "something is certified below the threshold form at n=%d" % n)

    # Control, and it is the PN-4 artifact reproduced: under DCR-3's implemented
    # projection, where a native obligation is priced at zero Python opcodes, the
    # delegating realization is certified below every written one.
    for n in SCOPE:
        beaten = opcode_frontier[n]["certified_strictly_below"]
        require(beaten["NESTED_CONSTANT_TABLE"] == ["DELEGATING_SUM_COMPARISON"],
                "the zero-priced-native artifact changed at the table, n=%d" % n)
        require(beaten["THRESHOLD_COMPARISON_BOOL"] == ["DELEGATING_SUM_COMPARISON"],
                "the zero-priced-native artifact changed at the threshold form, n=%d" % n)
        require(opcode_frontier[n]["undominated"] == ["DELEGATING_SUM_COMPARISON"],
                "the zero-priced projection no longer singles out delegation, n=%d" % n)

    return {
        "terminal": TERMINAL,
        "claim_ceiling": CLAIM_CEILING,
        "scope_n": list(SCOPE),
        "task": "majority-n: 1 exactly when at least half of n binary inputs are 1",
        "layout_contract": layout,
        "candidates": {str(n): rows_by_n[n] for n in SCOPE},
        "cost_formulas": formulas,
        "exhaustive_minimal_renderings": saturation,
        "enumeration_scope": {
            "binary_operations": sorted(enumeration.BINARY),
            "unary_operations": sorted(enumeration.UNARY),
            "unary_operations_refused_by_the_register": ["+"],
            "unary_budget": enumeration.UNARY_BUDGET,
            "comparisons": sorted(enumeration.COMPARE),
            "constants": list(CONSTANTS),
            "wide_constants": list(WIDE_CONSTANTS),
            "left_shift_limit": enumeration.SHIFT_LIMIT,
            "arithmetic_shape_enumerated_at": ["n=3"],
            "arithmetic_shape_open_at": ["n>=4 inside this checker; the unit test "
                                         "enumerates n=4 at a declared cap"],
            "constant_free_shapes_enumerated_at": ["n=3 at caps 32/64/256",
                                                   "n=4 at cap 32 here, cap 64 in the unit test"],
            "shapes_covered_by_measurement_not_enumeration":
                ["realizations that read a registered data binding, that is the "
                 "constant tables; the enumeration covers expression trees over "
                 "the n unpacked inputs"],
        },
        "frontier_opcode_projection": {str(n): opcode_frontier[n] for n in SCOPE},
        "frontier_honest_unknown_native_cost": {str(n): honest_frontier[n] for n in SCOPE},
        "frontier_priced_constant_cells": {str(n): priced[n] for n in SCOPE},
        "frontier_priced_constant_cells_int_typed": {str(n): priced_int[n] for n in SCOPE},
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2, allow_nan=False))
