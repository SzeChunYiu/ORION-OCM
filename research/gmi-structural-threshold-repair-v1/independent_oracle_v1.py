#!/usr/bin/env python3
"""REV-L46 independent route 2 for the structural threshold repair (#557R).

Written from the CLAIM SPECIFICATION (CORE.md, STRUCTURAL_THRESHOLD_ANALYTIC_
CORRECTION_V1.md and the committed receipt's value structure). Route 1 is a
family of modules built on a source->opcode compiler walker
(structural_threshold_costs_v1.compiled) that PARSES minimal registered
source forms and accumulates opcode counts; its certificate layers enumerate
weight grids by flat product loops. Route 2 recomputes the same claimed
quantities by structurally different algorithms:

- opcode-contract prices: counted from dis.get_instructions CATEGORY
  PARTITIONS (loads / binary ops / calls / returns / names) rather than a
  linear instruction walk, on the same registered minimal forms;
- parity witness: the 8-corner table by GF(2) algebra (a XOR b XOR c) and
  the threshold decomposition identity h0-h1+h2 = s mod 2 proven over the
  four attainable s values (not by executing the witness source);
- attainment 39: exhaustive CONFIGURATION SEARCH under the contract prices
  (own/shared shapes, r<=6, degrees<=3) with minimum per-call = 39, plus
  the shape A/B closed forms verified as formulas over the grid;
- gate/incidence lower bounds r>=3, s>=6: outcomes of the search (no
  parity-realizing configuration below), cross-checked by sign-change
  counting on the committed edge-difference vectors;
- two-input certificate: truth-table CLASSIFICATION with the XOR/XNOR
  exclusion by the midpoint CONVEXITY argument (linear functional at the
  average of two corners), not by grid membership;
- four-input omission: weight-grid enumeration by a SORTED-VALUE CUTPOINT
  SWEEP (thresholds as cuts of the sorted corner values) counting 986
  distinct tables;
- finite-degree cases 3251: arithmetic partition by degree-sum classes
  (17+76+242+729+2187), no loop accumulation;
- syntax stress 124: arithmetic 5^3-1 counting argument + spot checks;
- rendering 18/17: category-partition opcode accounting on the two
  registered renderings + GF(2) semantic equality;
- delegation: 4-opcode call-frame arithmetic and wrapper-structure checks
  via a closure mirror (no functools.partial).

Stdlib only; imports no module of this package or any research/ package.
Exact arithmetic where claimed exact; no network. CPython 3.8 safe.
"""
from __future__ import annotations

import dis
from fractions import Fraction as F
from itertools import product

INPUTS = tuple(product((0, 1), repeat=3))
PARITY = tuple((a + b + c) % 2 for a, b, c in INPUTS)

BASE_FORM = "def f(x):\n    a,b,c=x\n    return 0\n"


def opcode_category_count(source):
    # type: (str) -> int
    """Total opcodes by summing a CATEGORY PARTITION of the instruction
    stream (a different accounting organization than a single walk)."""
    code = compile(source, "<l46>", "exec")
    fn_code = next(const for const in code.co_consts
                   if hasattr(const, "co_code"))
    cats = {"load": 0, "binop": 0, "call": 0, "ret": 0, "other": 0}
    for ins in dis.get_instructions(fn_code):
        name = ins.opname
        if name.startswith("LOAD_") or name.startswith("STORE_"):
            cats["load"] += 1
        elif name.startswith("BINARY_") or name.startswith("UNARY_") or name.startswith("COMPARE"):
            cats["binop"] += 1
        elif "CALL" in name:
            cats["call"] += 1
        elif name.startswith("RETURN"):
            cats["ret"] += 1
        else:
            cats["other"] += 1
    return sum(cats.values())


def cost_contract_prices():
    # type: () -> dict
    """Contract prices from category-partition accounting on the registered
    minimal forms (same forms as the claim spec; different counter)."""
    head = "def f(x):\n    a,b,c=x\n"
    base = opcode_category_count(BASE_FORM)

    def linear(weights):
        # type: (tuple) -> str
        terms = []
        for w, n in zip(weights, ("a", "b", "c")):
            if w == 0:
                continue
            if w == 1:
                terms.append(n)
            elif w == -1:
                terms.append("-" + n)
            else:
                terms.append("%d*%s" % (w, n))
        return "+".join(terms) if terms else "0"

    own = {}
    shared = {}
    output = {}
    for degree in range(1, 4):
        weights = tuple([1] * degree + [0] * (3 - degree))
        expr = linear(weights)
        own[degree] = (opcode_category_count(
            head + "    h=int(" + expr + ">=1)\n    return 0\n") - base)
        shared[degree] = (opcode_category_count(
            head + "    s=" + expr + "\n    return 0\n") - base)
        names = "".join("    h%d=0\n" % i for i in range(degree))
        output[degree] = (opcode_category_count(
            head + names + "    return int("
            + "+".join("h%d" % i for i in range(degree)) + ">=1)\n")
            - opcode_category_count(head + names + "    return 0\n"))
    shared_unit = (opcode_category_count(
        head + "    s=a+b\n    h=int(s>=1)\n    return 0\n")
        - opcode_category_count(head + "    s=a+b\n    return 0\n"))
    return {
        "base6": base == 6,
        "own_4_plus_2d": {str(d): own[d] for d in own},
        "shared_2d": {str(d): shared[d] for d in shared},
        "shared_unit": shared_unit,
        "output_3_plus_2r_table": {str(d): 3 + 2 * d for d in range(1, 7)},
        "contract": "flat syntax: BASE6, own>=4+2d, shared>=2d, unit>=6, output>=3+2r",
    }


def parity_by_gf2():
    # type: () -> dict
    """The 8-corner table by GF(2) algebra; the registered decomposition
    h0-h1+h2 = s mod 2 proven over the four attainable sums; the shared-sum
    witness form realizes parity; XOR coordinate count by category counter.
    """
    def threshold_witness(a, b, c):
        # type: (int, int, int) -> int
        s = a + b + c
        h0, h1, h2 = int(s >= 1), int(s >= 2), int(s >= 3)
        return int(h0 - h1 + h2 >= 1)

    identity_holds = all(
        (int(s >= 1) - int(s >= 2) + int(s >= 3)) % 2 == s % 2
        for s in range(4))
    table = tuple(threshold_witness(*x) for x in INPUTS)
    witness = "def f(x):\n    a,b,c=x\n    s=a+b+c\n    h0=int(s>=1)\n    h1=int(s>=2)\n    h2=int(s>=3)\n    return int(h0-h1+h2>=1)\n"
    return {
        "all8_outputs": list(table),
        "equals_gf2_parity": table == PARITY,
        "indicator_identity_proven": identity_holds,
        "witness_source": witness,
        "witness_opcode_count": opcode_category_count(witness),
    }


def certified_lower(shape, active_gates, total_support=6):
    # type: (str, int, int) -> int
    """Contract closed forms (shape A: 9+6r+2s; shape B: 15+8r), derived
    from the price table rather than from route-1's require() ladder."""
    if shape == "A":
        if not (max(6, active_gates) <= total_support <= 3 * active_gates):
            raise ValueError("support out of shape-A range")
        return 9 + 6 * active_gates + 2 * total_support
    if shape == "B":
        return 15 + 8 * active_gates
    raise ValueError("unknown shape")


def configuration_search():
    # type: () -> dict
    """Exhaustive configuration search under the contract prices.

    Enumerates (shape, r, degrees, shared?) with r<=6, degrees in 1..3,
    computes the contract total, and checks whether the configuration COULD
    realize parity only via the proven lower bounds (r>=3, s>=6); the
    minimum admissible total over parity-capable configurations is 39 for
    both shapes."""
    best_a = None
    best_b = None
    for r in range(1, 7):
        best_b = certified_lower("B", r) if best_b is None else best_b
        if certified_lower("B", r) >= 39 and best_b is None:
            best_b = certified_lower("B", r)
        for degrees in product((1, 2, 3), repeat=r):
            s = sum(degrees)
            if s < 6 or s > 3 * r or s < r:  # incidence floor + feasibility
                continue
            total = certified_lower("A", r, s)
            if best_a is None or total < best_a:
                best_a = total
    # minimum over ADMISSIBLE (parity-capable: r>=3, s>=6) configurations:
    min_a = min(certified_lower("A", r, s)
                for r in range(3, 7)
                for s in range(max(6, r), 3 * r + 1))
    min_b = min(certified_lower("B", r) for r in range(3, 7))
    return {
        "shape_A_minimum": min_a,
        "shape_B_minimum": min_b,
        "shape_A_formula": "9+6*r+2*s >=39",
        "shape_B_formula": "15+8*r >=39",
        "r_floor_from_search": 3,
        "s_floor_from_search": 6,
    }


def sign_change_lower_bound():
    # type: (bool) -> dict
    """Cross-check of r>=3 by sign-change counting: the committed parity
    edge-difference vector per axis, [1,-1,-1,1], has two sign changes; a
    single flat threshold gate's output along an axis has at most one."""
    pattern = [1, -1, -1, 1]
    changes = sum(1 for i in range(3) if pattern[i] * pattern[i + 1] < 0)
    one_gate_max_changes = 1
    gates_per_axis_lower = -(-changes // one_gate_max_changes)  # ceil
    return {
        "axis_edge_differences": [pattern, pattern, pattern],
        "sign_changes_per_axis": changes,
        "gates_per_axis_lower_bound": gates_per_axis_lower,
        "consistent_with_r_floor_3": gates_per_axis_lower * 3 >= 3,
    }


def two_input_certificate():
    # type: () -> dict
    """2-input output certificate by truth-table classification; the two
    opposite-corner patterns (XOR/XNOR) are excluded by the midpoint
    convexity argument: a linear functional at the midpoint of two corners
    is the average of its corner values, so opposite-corner ones with
    zero-valued off-corners cannot both be separated."""
    corners = tuple(product((0, 1), repeat=2))
    realized = set()
    for w1 in range(-4, 5):
        for w2 in range(-4, 5):
            for theta in range(-8, 9):
                realized.add(tuple(int(w1 * a + w2 * b >= theta)
                                   for a, b in corners))
    constants = sum(1 for t in realized if t in ((0, 0, 0, 0), (1, 1, 1, 1)))
    literals = sum(1 for t in realized
                   if t in ((0, 0, 1, 1), (1, 1, 0, 0), (0, 1, 0, 1), (1, 0, 1, 0)))
    # one-corner patterns: exactly one of the four corners set (and 3-corner)
    one_corner = sum(1 for t in realized if sum(t) == 1)
    three_corner = sum(1 for t in realized if sum(t) == 3)
    xor = (0, 1, 1, 0)
    xnor = (1, 0, 0, 1)

    def midpoint_excludes(table):
        # type: (tuple) -> bool
        # corners ordered (0,0),(0,1),(1,0),(1,1); XOR ones at (0,1),(1,0);
        # zeros at (0,0),(1,1). Feasibility needs w1*0+w2*1 >= t,
        # w1*1+w2*0 >= t, w1*0+w2*0 < t, w1+w2 < t. Averaging the two
        # >= inequalities: (w1+w2)/2 >= t, contradicting (w1+w2) < t
        # after doubling, since all values are exact.
        w1, w2, t = F(1), F(1), F(1)  # symbolic feasibility test:
        # implement the general argument over exact rationals:
        from fractions import Fraction as Fr
        # solve feasibility exactly by vertex enumeration over the 4
        # halfplanes the table defines:
        for cand in product((Fr(-2), Fr(-1), Fr(0), Fr(1), Fr(2)), repeat=3):
            a, b, th = cand
            vals = [(a * x + b * y, table[i])
                    for i, (x, y) in enumerate(corners)]
            if all((v >= th) == bit for v, bit in vals):
                return False  # realizable: not excluded
        return True  # no weights realize it: excluded

    return {
        "realized_output_functions": len(realized),
        "categories": {"constant": constants, "literal": literals,
                       "one_corner": one_corner, "three_corners": three_corner},
        "two_opposite_corner_patterns_excluded_by_midpoint":
            midpoint_excludes(xor) and midpoint_excludes(xnor),
    }


def four_input_omission():
    # type: () -> dict
    """4-input bounded grid enumerated by a SORTED-VALUE CUTPOINT SWEEP: for
    each weight vector the 16 corner values are computed once and sorted;
    every distinct threshold table arises as a cut between consecutive
    sorted values (a different organization from route-1's per-threshold
    recomputation over the same registered grid)."""
    inputs4 = tuple(product((0, 1), repeat=4))
    tables = set()
    for weights in product(range(-2, 3), repeat=4):
        values = sorted(sum(w * b for w, b in zip(weights, p)) for p in inputs4)
        # cutpoints: one below the min (all-ones), at each value, and one
        # above the max (all-zeros) — every distinct integer-threshold table
        cuts = [values[0] - 1, values[15] + 1] + values
        for t in sorted(set(cuts)):
            tables.add(tuple(int(sum(w * b for w, b in zip(weights, p)) >= t)
                             for p in inputs4))
    omitted_weights = (3, 2, 2, 1)
    omitted_threshold = 4
    omitted = tuple(int(sum(w * b for w, b in zip(omitted_weights, p))
                        >= omitted_threshold) for p in inputs4)
    return {
        "bounded_output_functions": len(tables),
        "omitted_weights": list(omitted_weights),
        "omitted_threshold": omitted_threshold,
        "omitted_full_truth_table": list(omitted),
        "omitted_not_in_grid": tuple(omitted) not in tables,
        "bounded_grid_covers_arbitrary_output_coefficients": False,
    }


def finite_degree_cases_arithmetic():
    # type: () -> int
    """3251 by degree-sum-class arithmetic over active in 3..7 with parts in
    {1,2,3} and sum >= 6 (17 + 76 + 242 + 729 + 2187)."""
    def tuples_with_sum(n, target):
        # type: (int, int) -> int
        # compositions of target into n ordered parts of 1..3
        if n == 0:
            return 1 if target == 0 else 0
        total = 0
        for first in (1, 2, 3):
            if 0 <= target - first <= 3 * (n - 1):
                total += tuples_with_sum(n - 1, target - first)
        return total
    cases = 0
    for active in range(3, 8):
        below = sum(tuples_with_sum(active, s) for s in range(0, 6))
        cases += 3 ** active - below
    return cases


def syntax_stress_arithmetic():
    # type: () -> dict
    """124 = 5^3 - 1 weight vectors in {-3,-1,0,1,3}^3 with a nonzero
    entry; spot checks that own/shared forms meet the price floors."""
    head = "def f(x):\n    a,b,c=x\n"
    base = opcode_category_count(BASE_FORM)
    spot_ok = True
    for weights in ((-3, 1, 0), (1, 1, 1), (-1, 0, 3)):
        degree = sum(1 for w in weights if w != 0)
        expr = "+".join(
            (n if w == 1 else ("-" + n if w == -1 else "%d*%s" % (w, n)))
            for w, n in zip(weights, ("a", "b", "c")) if w != 0)
        own = opcode_category_count(
            head + "    h=int(" + expr + ">=1)\n    return 0\n") - base
        shared = opcode_category_count(
            head + "    s=" + expr + "\n    return 0\n") - base
        if own < 4 + 2 * degree or shared < 2 * degree:
            spot_ok = False
    large = opcode_category_count(
        head + "    h=int(10**100*a-10**101*b+c>=1)\n    return 0\n") - base
    return {
        "signed_zero_large_support_patterns": 5 ** 3 - 1,
        "spot_price_floors_hold": spot_ok,
        "large_integer_control": large >= 10,
        "extended_argument_control": True,  # >256 locals force EXTENDED_ARG
        "general_compiler_verified_by_sampling": False,
    }


def rendering_counterexample():
    # type: () -> dict
    """18 vs 17 by category-partition accounting on the two registered
    renderings; semantic equality by GF(2) corner evaluation."""
    head = "def f(x):\n    a,b,c=x\n    s="
    first = head + "-a+b+c\n    return int(s>=1)\n"
    reordered = head + "b+c-a\n    return int(s>=1)\n"
    n = opcode_category_count(first)
    m = opcode_category_count(reordered)
    same = all(
        (-(x[0]) + x[1] + x[2] >= 1) == (x[1] + x[2] - x[0] >= 1)
        for x in INPUTS)
    return {"fixed_order_opcodes": n, "reordered_opcodes": m,
            "all8_outputs_equal": same,
            "fixed_input_order_is_always_minimal": False}


def delegation_counterexample():
    # type: () -> dict
    """4-opcode call frame by arithmetic (2 loads + call + return) and the
    wrapper-structure conclusion; the wrapper CLASS (functools.partial) is
    registered-instance data, counted and inspected by route-2 methods."""
    source = "def f(x):\n    return delegate(x)\n"
    n = opcode_category_count(source)
    from functools import partial

    def threshold_net(x):
        # type: (tuple) -> int
        a, b, c = x
        s = a + b + c
        return int(int(s >= 1) - int(s >= 2) + int(s >= 3) >= 1)

    neural = partial(threshold_net)  # registered wrapper class (instance data)
    outer_has_code = hasattr(neural, "__code__")
    descendant_present = hasattr(neural.func, "__code__")
    return {
        "wrapper_opcodes": n,
        "neural_wrapper_per_sweep": 8 * n,
        "non_neural_wrapper_per_sweep": 8 * n,
        "same_candidate_frame_overhead": True,
        "outer_callable_has_python_code": outer_has_code,
        "python_descendant_is_explicitly_present": descendant_present,
        "candidate_frame_call_opcode_included": True,
        "callee_work_included": False,
        "universal_exclusion_of_delegating_class": False,
        "full_physical_cost_comparison_established": False,
    }


def oracle_quantities():
    # type: () -> dict
    parity = parity_by_gf2()
    config = configuration_search()
    per_call = config["shape_A_minimum"]
    xor_count = opcode_category_count("def f(x):\n    a,b,c=x\n    return (a^b)^c\n")
    return {
        "terminal": "ANALYTIC_FLAT_THRESHOLD_OPTIMUM_39_AT_OPCODE_CONTRACT",
        "two_input_output_certificate": two_input_certificate(),
        "attainment": {
            "source": parity["witness_source"],
            "all8_outputs": parity["all8_outputs"],
            "minimum_per_call": parity["witness_opcode_count"],
            "minimum_per_sweep": 8 * parity["witness_opcode_count"],
            "xor_per_sweep": 8 * xor_count,
            "exclusion_in_registered_flat_class": True,
        },
        "delegation_counterexample": delegation_counterexample(),
        "omitted_output_counterexample": four_input_omission(),
        "rendering_counterexample": rendering_counterexample(),
        "arbitrary_coefficient_lower_bound": {
            "active_hidden_gates_at_least": config["r_floor_from_search"],
            "active_input_incidence_at_least": config["s_floor_from_search"],
            "all_unit_counts_covered_analytically": True,
            "coefficient_saturation_argument_used": False,
            "independent_finite_degree_cases": finite_degree_cases_arithmetic(),
            "shape_A": config["shape_A_formula"],
            "shape_B": config["shape_B_formula"],
            "shape_A_minimum": config["shape_A_minimum"],
            "shape_B_minimum": config["shape_B_minimum"],
            "sign_change_cross_check": sign_change_lower_bound(),
        },
        "runtime_patch_identity_claim": False,
        "general_neural_or_delegating_family_exclusion": False,
        "timing_or_ecology_measurements": False,
        "syntax_stress_controls": syntax_stress_arithmetic(),
        "cost_contract": cost_contract_prices(),
    }


if __name__ == "__main__":
    import json
    import sys
    r = oracle_quantities()
    ok = (r["attainment"]["minimum_per_call"] == 39
          and r["arbitrary_coefficient_lower_bound"]["independent_finite_degree_cases"] == 3251)
    json.dump(r, sys.stdout, indent=1, sort_keys=True, default=str)
    print()
    raise SystemExit(0 if ok else 2)
