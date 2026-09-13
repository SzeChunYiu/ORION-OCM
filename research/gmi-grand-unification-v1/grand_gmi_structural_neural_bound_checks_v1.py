#!/usr/bin/env python3
"""Exact checks for STRUCTURAL_NEURAL_BOUND_THEOREM_V1.

The parity-3 evidence line has only ever produced a point verdict over
registered candidates. CU-3b proves such a verdict cannot be upgraded by
adding candidates. What upgrades it is a derived lower bound over a structural
class, in the sense of PL-1 and PL-2, because such a bound covers members
nobody has written.

These checks derive that bound for the single-hidden-layer threshold class on
parity-3, in the registered CPython opcode coordinate, by exhaustive
enumeration. Everything here is static: nothing is timed, and no wall or
process measurement is used or produced.
"""

from __future__ import annotations

import dis
import functools
import itertools
import json
import sys

INPUTS = tuple((a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1))
PARITY = tuple(a ^ b ^ c for a, b, c in INPUTS)
NAMES = ("a", "b", "c")

# Registered coefficient range for the enumerated grammar. SN-2 proves the
# hidden behaviour set is already saturated over a strictly wider range, so
# this bound is not what limits feasibility.
COEF = (-2, -1, 0, 1, 2)
WIDE_COEF = (-4, -3, -2, -1, 0, 1, 2, 3, 4)
# Threshold functions of three binary variables, i.e. linearly separable
# Boolean functions on three inputs. Enumerated independently in SN-2.
KNOWN_THRESHOLD_FUNCTION_COUNT_3 = 104


class StructuralBoundError(ValueError):
    """The enumeration cannot support a derived bound as it stands."""


def require(condition, message):
    if not condition:
        raise StructuralBoundError(message)


# --- Canonical minimal rendering ------------------------------------------


def term_text(coef, name):
    if coef == 1:
        return name
    if coef == -1:
        return "-" + name
    return f"{coef}*{name}"


def linear_text(coefs, names):
    """Cheapest faithful Python rendering of an integer linear form.

    A zero coefficient omits its term, a unit coefficient omits its multiply,
    and a subtraction is written as such rather than as adding a negation.
    Rendering any term more expensively would only raise the derived bound.
    """
    parts = [(c, n) for c, n in zip(coefs, names) if c != 0]
    if not parts:
        return "0"
    out = term_text(parts[0][0], parts[0][1])
    for c, n in parts[1:]:
        out += f" + {term_text(c, n)}" if c > 0 else f" - {term_text(-c, n)}"
    return out


def opcode_count(source, name="f"):
    """Exact straight-line opcode count, in the registered coordinate."""
    namespace = {}
    exec(compile(source, "<structural-grammar>", "exec"), namespace)
    fn = namespace[name]
    instructions = list(dis.get_instructions(fn, adaptive=False))
    require(not any(i.opcode in dis.hasjabs or i.opcode in dis.hasjrel
                    or i.opname in ("RETURN_GENERATOR", "YIELD_VALUE")
                    for i in instructions),
            "the grammar must stay straight-line")
    return len([i for i in instructions if i.opname not in ("RESUME", "CACHE")]), fn


# --- Line costs, measured once per syntactic shape -------------------------

BASE, _ = opcode_count("def f(x):\n    a, b, c = x\n    return 0\n")
_LINE_CACHE: dict = {}


def unit_own_form_cost(coefs):
    key = ("unitA", coefs)
    if key not in _LINE_CACHE:
        text = linear_text(coefs, NAMES)
        total, _ = opcode_count(
            f"def f(x):\n    a, b, c = x\n    h0 = int(({text}) >= 1)\n    return 0\n")
        _LINE_CACHE[key] = total - BASE
    return _LINE_CACHE[key]


def shared_form_cost(coefs):
    key = ("shared", coefs)
    if key not in _LINE_CACHE:
        text = linear_text(coefs, NAMES)
        total, _ = opcode_count(f"def f(x):\n    a, b, c = x\n    s = {text}\n    return 0\n")
        _LINE_CACHE[key] = total - BASE
    return _LINE_CACHE[key]


def unit_shared_cost():
    key = ("unitB",)
    if key not in _LINE_CACHE:
        with_unit, _ = opcode_count(
            "def f(x):\n    a, b, c = x\n    s = a\n    h0 = int(s >= 1)\n    return 0\n")
        without, _ = opcode_count("def f(x):\n    a, b, c = x\n    s = a\n    return 0\n")
        _LINE_CACHE[key] = with_unit - without
    return _LINE_CACHE[key]


def output_cost(coefs):
    key = ("out", coefs)
    if key not in _LINE_CACHE:
        names = tuple(f"h{i}" for i in range(len(coefs)))
        head = "def f(x):\n    a, b, c = x\n" + "".join(f"    {n} = 0\n" for n in names)
        text = linear_text(coefs, names)
        with_return, _ = opcode_count(head + f"    return int(({text}) >= 1)\n")
        without, _ = opcode_count(head + "    return 0\n")
        _LINE_CACHE[key] = with_return - without
    return _LINE_CACHE[key]


# --- SN-2: the hidden behaviour set is saturated ---------------------------


@functools.lru_cache(maxsize=None)
def threshold_behaviours(coefs_range, threshold_span):
    """behaviour -> (cheapest own-form line cost, representative spec)."""
    best = {}
    for w in itertools.product(coefs_range, repeat=3):
        values = [w[0] * a + w[1] * b + w[2] * c for a, b, c in INPUTS]
        cost = unit_own_form_cost(w)
        for t in range(-threshold_span, threshold_span + 2):
            behaviour = tuple(int(v >= t) for v in values)
            if behaviour not in best or cost < best[behaviour][0]:
                best[behaviour] = (cost, (w, t))
    return best


def check_behaviour_saturation():
    """SN-2. Widening the coefficient range adds no hidden behaviour.

    A hidden unit's behaviour is a linearly separable Boolean function of the
    three inputs. There are finitely many such functions, so the enumerated
    set can be complete. Enumerating over a strictly wider coefficient range
    yields the same set, and its size matches the known count of threshold
    functions on three variables. A wider range therefore cannot lower the
    derived bound, because it adds no behaviour and every rendering of a
    larger coefficient costs at least as much.
    """
    narrow = threshold_behaviours(COEF, 6)
    wide = threshold_behaviours(WIDE_COEF, 12)
    require(set(narrow) == set(wide), "a wider coefficient range added a behaviour")
    require(len(narrow) == KNOWN_THRESHOLD_FUNCTION_COUNT_3,
            f"enumerated {len(narrow)} behaviours, expected "
            f"{KNOWN_THRESHOLD_FUNCTION_COUNT_3}")
    cheaper = {b for b in narrow if wide[b][0] < narrow[b][0]}
    require(not cheaper, "a wider coefficient range rendered a behaviour more cheaply")
    return {
        "registered_coefficient_range": list(COEF),
        "wider_coefficient_range": list(WIDE_COEF),
        "behaviours_registered_range": len(narrow),
        "behaviours_wider_range": len(wide),
        "behaviour_sets_identical": True,
        "known_threshold_function_count_on_three_inputs": KNOWN_THRESHOLD_FUNCTION_COUNT_3,
        "wider_range_never_cheaper": True,
        "coefficient_bound_is_not_binding": True,
    }


# --- Output layer ----------------------------------------------------------


@functools.lru_cache(maxsize=None)
def output_threshold_table(k):
    """Every Boolean function on k hidden bits realizable by one threshold
    output line, with the cheapest line cost realizing it."""
    patterns = list(itertools.product((0, 1), repeat=k))
    best = {}
    for v in itertools.product(COEF, repeat=k):
        values = [sum(vi * pi for vi, pi in zip(v, p)) for p in patterns]
        cost = output_cost(v)
        for t in range(-2 * k, 2 * k + 2):
            function = tuple(int(x >= t) for x in values)
            if function not in best or cost < best[function][0]:
                best[function] = (cost, v, t)
    return patterns, best


def hidden_requirement(hidden):
    """Parity as a partial function of the hidden pattern, or None if the
    hidden layer maps two inputs of different parity to the same pattern."""
    need = {}
    for pattern, parity in zip(hidden, PARITY):
        if need.setdefault(pattern, parity) != parity:
            return None
    return need


def cheapest_output(patterns, table, need):
    """Cheapest threshold output agreeing with `need` on its domain.

    Hidden patterns that no input reaches are genuine don't-cares, so every
    realizable threshold function must be tested rather than a guessed
    completion.
    """
    index = {p: i for i, p in enumerate(patterns)}
    constraints = [(index[p], value) for p, value in need.items()]
    best = None
    for function, row in table.items():
        if all(function[i] == value for i, value in constraints):
            if best is None or row[0] < best[0]:
                best = row
    return best


# --- SN-3: exhaustive minimum over the registered grammar ------------------


@functools.lru_cache(maxsize=None)
def grammar_minimum(max_units=4):
    """Exhaustive minimum opcode count per call over the grammar.

    Shape A gives every hidden unit its own linear form. Shape B computes one
    shared linear form and thresholds it repeatedly, which is how a competent
    implementer writes a network whose units share a weight vector. Both are
    enumerated; the cheaper wins.
    """
    behaviours = threshold_behaviours(COEF, 6)
    ordered = sorted(behaviours)
    shared_forms = {}
    for w in itertools.product(COEF, repeat=3):
        values = [w[0] * a + w[1] * b + w[2] * c for a, b, c in INPUTS]
        rows = {}
        for t in range(-6, 8):
            rows.setdefault(tuple(int(v >= t) for v in values), t)
        shared_forms[w] = rows

    per_k, best = {}, None
    unit_b = unit_shared_cost()
    for k in range(1, max_units + 1):
        patterns, table = output_threshold_table(k)
        floor_output = min(row[0] for row in table.values())
        local = None

        for combo in itertools.combinations_with_replacement(range(len(ordered)), k):
            units = [ordered[i] for i in combo]
            unit_sum = sum(behaviours[u][0] for u in units)
            if local is not None and BASE + unit_sum + floor_output >= local[0]:
                continue
            need = hidden_requirement([tuple(u[j] for u in units) for j in range(8)])
            if need is None:
                continue
            got = cheapest_output(patterns, table, need)
            if got is None:
                continue
            total = BASE + unit_sum + got[0]
            if local is None or total < local[0]:
                local = (total, "A", [behaviours[u][1] for u in units], got)

        for w, rows in shared_forms.items():
            base = BASE + shared_form_cost(w) + k * unit_b
            if local is not None and base + floor_output >= local[0]:
                continue
            for combo in itertools.combinations_with_replacement(sorted(rows), k):
                need = hidden_requirement([tuple(u[j] for u in combo) for j in range(8)])
                if need is None:
                    continue
                got = cheapest_output(patterns, table, need)
                if got is None:
                    continue
                total = base + got[0]
                if local is None or total < local[0]:
                    local = (total, "B", (w, [rows[u] for u in combo]), got)

        per_k[k] = local
        if local is not None and (best is None or local[0] < best[0]):
            best = local
    return behaviours, tuple(sorted(per_k.items())), best


def build_source(kind, spec, out):
    _, v, t = out
    if kind == "B":
        w, thresholds = spec
        lines = ["def f(x):", "    a, b, c = x",
                 f"    s = {linear_text(w, NAMES)}"]
        lines += [f"    h{i} = int(s >= {th})" for i, th in enumerate(thresholds)]
    else:
        lines = ["def f(x):", "    a, b, c = x"]
        lines += [f"    h{i} = int(({linear_text(w, NAMES)}) >= {th})"
                  for i, (w, th) in enumerate(spec)]
    names = tuple(f"h{i}" for i in range(len(v)))
    lines.append(f"    return int(({linear_text(v, names)}) >= {t})")
    return "\n".join(lines)


def check_grammar_minimum():
    """SN-3. The minimum is attained, and few-unit networks are infeasible."""
    behaviours, per_k_pairs, best = grammar_minimum()
    per_k = dict(per_k_pairs)
    require(best is not None, "no grammar member computes parity")
    require(per_k[1] is None and per_k[2] is None,
            "a one- or two-unit threshold network computed parity")
    require(per_k[3] is not None, "no three-unit network computed parity")

    total, kind, spec, out = best
    source = build_source(kind, spec, out)
    actual, fn = opcode_count(source)
    require(actual == total, f"line costs are not additive: {actual} against {total}")
    require(tuple(fn(x) for x in INPUTS) == PARITY, "the minimizer does not compute parity")

    # The optimum is not unique, so only properties common to all minimizers
    # are derived (MS-3). Count the distinct minimizing specifications found.
    return {
        "hidden_behaviours_enumerated": len(behaviours),
        "per_unit_count": {str(k): (None if v is None else v[0]) for k, v in per_k.items()},
        "one_and_two_unit_networks_infeasible": True,
        "derived_minimum_per_call": total,
        "derived_minimum_per_full_domain_sweep": total * 8,
        "minimizing_shape": kind,
        "minimizer_source": source,
        "minimizer_predicted_equals_compiled": True,
        "minimizer_computes_parity": True,
    }


def check_unbounded_unit_count_excluded():
    """SN-4. Every unit count above the enumerated range is more expensive.

    Each hidden unit contributes a positive line cost, so a network with more
    units than were enumerated costs at least the overhead plus that many
    minimum unit lines plus the cheapest possible output line. Once that floor
    exceeds the enumerated minimum, no larger network can beat it, and the
    enumeration is complete over all unit counts.
    """
    best = grammar_minimum()[2]
    minimum = best[0]
    behaviours = threshold_behaviours(COEF, 6)
    min_unit_a = min(cost for cost, _ in behaviours.values())
    min_unit_b = unit_shared_cost()
    min_shared = min(shared_form_cost(w) for w in itertools.product(COEF, repeat=3))
    min_unit = min(min_unit_a, min_unit_b)
    floor_output = min(
        min(row[0] for row in output_threshold_table(k)[1].values()) for k in (1, 2, 3, 4))
    require(min_unit > 0, "a hidden unit line costs nothing")

    first_excluded = None
    for k in range(5, 64):
        floor = BASE + min(0, min_shared) + k * min_unit + floor_output
        if floor >= minimum:
            first_excluded = k
            break
    require(first_excluded == 5,
            f"unit counts from 5 upward are not immediately excluded: {first_excluded}")
    return {
        "enumerated_minimum_per_call": minimum,
        "minimum_hidden_unit_line_cost": min_unit,
        "minimum_shared_form_line_cost": min_shared,
        "minimum_output_line_cost": floor_output,
        "floor_at_five_units": BASE + min(0, min_shared) + 5 * min_unit + floor_output,
        "all_unit_counts_from_five_upward_excluded": True,
        "enumeration_complete_over_unit_count": True,
    }


# --- SN-5: the structural exclusion ---------------------------------------


def xor_reference():
    source = "def f(x):\n    a, b, c = x\n    return (a ^ b) ^ c\n"
    total, fn = opcode_count(source)
    require(tuple(fn(x) for x in INPUTS) == PARITY, "the reference is not parity")
    return total, source


def check_structural_exclusion():
    """SN-5. A non-neural witness excludes the whole structural class.

    The derived bound holds of every member of the class, so a construction
    strictly below it is not beaten by any member, including members nobody
    has written. This is PL-2 supplying the bound and CU-2 transferring the
    verdict, on a real instance rather than a synthetic grid.
    """
    best = grammar_minimum()[2]
    neural_sweep = best[0] * 8
    per_call, source = xor_reference()
    witness_sweep = per_call * 8
    require(witness_sweep < neural_sweep, "the witness does not beat the derived bound")
    return {
        "derived_class_lower_bound_per_sweep": neural_sweep,
        "non_neural_witness_per_sweep": witness_sweep,
        "witness_source": source,
        "margin_per_sweep": neural_sweep - witness_sweep,
        "ratio": f"{neural_sweep}/{witness_sweep}",
        "structural_exclusion_holds": True,
        "covers_unwritten_members_of_the_class": True,
        "coordinate": "python_opcode_count_per_full_domain_sweep",
        "timing_used": False,
    }


def check_registered_candidates_are_grammar_optimal():
    """The registered neural candidate already attains the derived bound.

    That makes the bound tight in the PL-3b sense, and it means the registered
    candidate register was not understating the neural family: no member of the
    enumerated class is cheaper.
    """
    best = grammar_minimum()[2]
    shared_sum = build_source("B", ((1, 1, 1), [1, 2, 3]), (0, (1, -1, 1), 1))
    dnf4 = build_source("A", [((-1, -1, 1), 1), ((-1, 1, -1), 1),
                              ((1, -1, -1), 1), ((1, 1, 1), 3)],
                        (0, (1, 1, 1, 1), 1))
    shared_total, shared_fn = opcode_count(shared_sum)
    dnf_total, dnf_fn = opcode_count(dnf4)
    require(tuple(shared_fn(x) for x in INPUTS) == PARITY, "rebuilt shared-sum net is wrong")
    require(tuple(dnf_fn(x) for x in INPUTS) == PARITY, "rebuilt DNF net is wrong")
    require(shared_total == best[0],
            f"the registered shared-sum net {shared_total} does not attain {best[0]}")
    require(dnf_total > best[0], "the registered DNF net unexpectedly attains the bound")
    return {
        "registered_shared_sum_net_per_call": shared_total,
        "registered_shared_sum_net_per_sweep": shared_total * 8,
        "registered_dnf_net_per_call": dnf_total,
        "registered_dnf_net_per_sweep": dnf_total * 8,
        "derived_minimum_per_call": best[0],
        "registered_candidate_attains_the_bound": True,
        "bound_is_tight_in_the_pl3b_sense": True,
        "minimizer_differs_from_registered_candidate": build_source(*best[1:]) != shared_sum,
    }


# --- SN-7: the coordinate is not delegation invariant ---------------------

DELEGATION_WITNESSES = {
    "class_member_written_arithmetic": (
        "def f(x):\n    a, b, c = x\n    s = a + b + c\n"
        "    h0 = int(s >= 1)\n    h1 = int(s >= 2)\n    h2 = int(s >= 3)\n"
        "    return int((h0 - h1 + h2) >= 1)\n"),
    "threshold_net_delegating_the_sum": (
        "def f(x):\n    s = sum(x)\n"
        "    h0 = int(s >= 1)\n    h1 = int(s >= 2)\n    h2 = int(s >= 3)\n"
        "    return int((h0 - h1 + h2) >= 1)\n"),
    "non_neural_written_xor": "def f(x):\n    a, b, c = x\n    return (a ^ b) ^ c\n",
    "non_neural_delegating": "def f(x):\n    return sum(x) & 1\n",
}


def check_delegation_is_outside_the_coordinate():
    """SN-7. The coordinate counts candidate-frame opcodes only.

    Moving work into a callee with no Python code object removes it from the
    coordinate entirely. This is shown statically, without timing: `sum` and
    `int` are C builtins, so their work executes no candidate-frame opcode.

    Two consequences are recorded. First, the SN-3 numeric bound is relative to
    the non-delegating rendering the grammar registers: a threshold network
    that delegates its weighted sum scores below that bound. Second, the
    exclusion survives anyway, and the bias runs toward the excluded class:
    every class member already delegates its `int` conversions while the
    written XOR realization delegates nothing, so correcting for invisible work
    would only widen the margin.
    """
    counts, calls = {}, {}
    for name, source in DELEGATION_WITNESSES.items():
        total, fn = opcode_count(source)
        require(tuple(fn(x) for x in INPUTS) == PARITY, f"{name} is not parity")
        counts[name] = total * 8
        instructions = dis.get_instructions(fn, adaptive=False)
        calls[name] = sum(1 for i in instructions if i.opname.startswith("CALL"))

    require(not hasattr(sum, "__code__") and not hasattr(int, "__code__"),
            "the delegation witnesses are not C builtins on this interpreter")

    member = counts["class_member_written_arithmetic"]
    delegating_member = counts["threshold_net_delegating_the_sum"]
    written_witness = counts["non_neural_written_xor"]
    delegating_witness = counts["non_neural_delegating"]

    require(delegating_member < member,
            "delegation did not lower the class member's count, so this witness is vacuous")
    require(written_witness < member, "the written exclusion failed")
    require(delegating_witness < delegating_member,
            "the like-for-like delegating exclusion failed")
    require(calls["non_neural_written_xor"] == 0 and calls["class_member_written_arithmetic"] > 0,
            "the delegation asymmetry between the compared realizations changed")
    return {
        "per_sweep_counts": counts,
        "candidate_frame_calls": calls,
        "callees_have_no_python_code_object": True,
        "delegation_lowers_a_class_member_below_the_derived_bound": True,
        "derived_bound_is_relative_to_the_non_delegating_rendering": True,
        "exclusion_holds_written_against_written": True,
        "exclusion_holds_delegating_against_delegating": True,
        "coordinate_bias_favours_the_excluded_class": True,
        "exclusion_is_conservative_under_delegation": True,
        "timing_used": False,
    }


RESIDUE = {
    "closed_within_this_class": [
        "any number of hidden units, by enumeration to four and the cost floor above",
        "any integer coefficient magnitude, because the behaviour set is saturated",
        "both registered code shapes, independent forms and one shared form",
        "the non-delegating rendering, which SN-7 shows is what the numeric bound is "
        "relative to",
        "all threshold placements, by exhaustive enumeration of separable behaviours",
    ],
    "open_residue": [
        "more than one hidden layer",
        "activations other than an integer-threshold comparison",
        "realizations that delegate arithmetic into a C builtin, which SN-7 measures: they "
        "score below the derived bound while still being excluded",
        "vectorized or array-based realizations whose opcode accounting differs",
        "realizations that precompute their outputs, which the structural predicate "
        "excludes by definition rather than by discovery; that is the lookup family",
        "any substrate or language other than the registered CPython opcode coordinate",
        "wall and process time, which this derivation never uses",
    ],
    "predicate_is_a_scope_choice": (
        "Defining the neural class as single-hidden-layer integer-threshold units is a "
        "registered scope decision. A different predicate is a different theorem, and by "
        "PL-4b weakening the predicate can only lower the bound."
    ),
}


def run():
    return {
        "terminal": "GRAND_GMI_STRUCTURAL_NEURAL_BOUND_GREEN_AT_FINITE_SCOPE",
        "interpreter": list(sys.version_info[:3]),
        "behaviour_saturation": check_behaviour_saturation(),
        "grammar_minimum": check_grammar_minimum(),
        "unbounded_unit_count_excluded": check_unbounded_unit_count_excluded(),
        "registered_candidates_are_grammar_optimal":
            check_registered_candidates_are_grammar_optimal(),
        "structural_exclusion": check_structural_exclusion(),
        "delegation_outside_the_coordinate": check_delegation_is_outside_the_coordinate(),
        "residue": RESIDUE,
        "timing_measurement_used": False,
        "claim_ceiling": "one structural class, one task, one exact coordinate, one interpreter",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
