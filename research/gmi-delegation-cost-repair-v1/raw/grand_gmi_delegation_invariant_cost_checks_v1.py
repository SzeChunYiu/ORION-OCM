#!/usr/bin/env python3
"""Delegation-invariant static cost coordinate for the registered flat grammar.

SN-7 recorded that `python_opcode_count_per_full_domain_sweep` counts opcodes
executed in the candidate's own frame only, so work exported into a C builtin
leaves the measure. This checker registers a two-component coordinate over the
same straight-line grammar and the same static opcode contract. Work exported
into a statically resolvable Python callee is accounted by recursion, so it does
not leave the measure; work exported into a callee with no Python code object
cannot be accounted at all and is charged to a separate component. Neither
export can produce a dominating realization.

No timing, no tracing, no physical cost. Explicit `raise` only: the suite also
runs under `python -O`, which strips `assert`.
"""

import dis
import json
from functools import partial
from itertools import product

INPUTS = tuple(product((0, 1), repeat=3))
PARITY = tuple(sum(x) % 2 for x in INPUTS)
SWEEP = len(INPUTS)

# Opcodes this instrument can account for exactly. Anything else is refused
# rather than guessed: an unaccounted opcode could hide a call.
PUSH1 = ("LOAD_CONST", "LOAD_FAST", "LOAD_NAME", "LOAD_FAST_CHECK")
UNARY = ("UNARY_NEGATIVE", "UNARY_NOT", "UNARY_INVERT")
BINARY = ("BINARY_OP", "BINARY_SUBSCR", "COMPARE_OP", "IS_OP", "CONTAINS_OP")
IGNORED = ("RESUME", "CACHE", "NOP", "PRECALL")

NULL = ("null",)
VALUE = ("value",)


class CoordinateRefusal(ValueError):
    """The instrument cannot account for this realization and refuses to score it."""


def require(condition, message):
    if not condition:
        raise CoordinateRefusal(message)


def compile_candidate(source, environment=None):
    """Compile one registered straight-line realization."""
    namespace = {} if environment is None else dict(environment)
    exec(compile(source, "<delegation-invariant>", "exec"), namespace)
    require("f" in namespace, "registered source must define f")
    fn = namespace["f"]
    instructions = tuple(dis.get_instructions(fn, adaptive=False, show_caches=False))
    require(not any(i.opcode in dis.hasjabs or i.opcode in dis.hasjrel
                    or i.opname in ("YIELD_VALUE", "RETURN_GENERATOR")
                    for i in instructions),
            "outside the straight-line coordinate")
    return fn, instructions, namespace


def _resolve(name, namespace):
    if name in namespace:
        return namespace[name], True
    builtins = __builtins__ if isinstance(__builtins__, dict) else vars(__builtins__)
    if name in builtins:
        return builtins[name], True
    return None, False


def account(source, environment=None):
    """Exact (accounted opcodes, unaccounted calls) per call, or a refusal."""
    fn, instructions, namespace = compile_candidate(source, environment)
    return _account_instructions(instructions, namespace, fn, ())


def _callee_instructions(target):
    """Straight-line instruction sequence of a Python-coded callee."""
    instructions = tuple(dis.get_instructions(target, adaptive=False, show_caches=False))
    require(not any(i.opcode in dis.hasjabs or i.opcode in dis.hasjrel
                    or i.opname in ("YIELD_VALUE", "RETURN_GENERATOR")
                    for i in instructions),
            "callee is outside the straight-line coordinate")
    return instructions


def _account_instructions(instructions, namespace, fn, chain):
    """Account one straight-line frame, recursing into Python-coded callees.

    A call whose callee carries a Python code object is not an escape: its work
    is statically visible, so its own accounted opcodes are added here. Only a
    callee whose work cannot be accounted at all is charged to the second
    component. That is what makes the coordinate invariant to delegation rather
    than merely to delegation-into-a-builtin.
    """
    require(len(chain) <= 8, "callee nesting deeper than the registered limit")
    stack = []
    opcodes = 0
    unaccounted = 0
    resolved_calls = []
    for instruction in instructions:
        name = instruction.opname
        if name not in IGNORED:
            opcodes += 1
        if name in ("RESUME", "CACHE", "NOP"):
            continue
        if name in PUSH1:
            stack.append(VALUE)
        elif name == "LOAD_GLOBAL":
            if instruction.argrepr.startswith("NULL + "):
                stack.append(NULL)
            stack.append(("global", instruction.argval))
        elif name == "PUSH_NULL":
            stack.append(NULL)
        elif name in ("STORE_FAST", "STORE_NAME", "POP_TOP"):
            require(stack, "stack underflow")
            stack.pop()
        elif name == "UNPACK_SEQUENCE":
            require(stack, "stack underflow")
            stack.pop()
            stack.extend(VALUE for _ in range(instruction.arg))
        elif name in UNARY:
            require(stack, "stack underflow")
            stack.pop()
            stack.append(VALUE)
        elif name in BINARY:
            require(len(stack) >= 2, "stack underflow")
            del stack[-2:]
            stack.append(VALUE)
        elif name == "CALL":
            count = instruction.arg
            require(len(stack) >= count + 2, "stack underflow at call")
            frame = stack[-(count + 2):]
            del stack[-(count + 2):]
            first, second = frame[0], frame[1]
            if first == NULL:
                callee = second
            elif second == NULL:
                callee = first
            else:
                raise CoordinateRefusal("unresolvable bound-method call")
            require(callee != NULL and callee[0] == "global",
                    "unresolvable callee: not a statically named global")
            target, found = _resolve(callee[1], namespace)
            require(found, "unresolvable callee: name not bound at compile time")
            resolved_calls.append(callee[1])
            if hasattr(target, "__code__"):
                code = target.__code__
                require(code not in chain, "recursive callee: not straight-line")
                inner = _account_instructions(_callee_instructions(target),
                                              getattr(target, "__globals__", {}),
                                              target, chain + (code,))
                opcodes += inner["opcodes_per_call"]
                unaccounted += inner["unaccounted_calls_per_call"]
                resolved_calls.extend(inner["resolved_callees"])
            else:
                unaccounted += 1
            stack.append(VALUE)
        elif name in ("RETURN_VALUE",):
            require(stack, "stack underflow")
            stack.pop()
        elif name == "RETURN_CONST":
            pass
        elif name == "COPY":
            require(len(stack) >= instruction.arg, "stack underflow")
            stack.append(stack[-instruction.arg])
        elif name == "SWAP":
            require(len(stack) >= instruction.arg, "stack underflow")
            index = -instruction.arg
            stack[index], stack[-1] = stack[-1], stack[index]
        else:
            raise CoordinateRefusal("unaccounted opcode: " + name)
    return {"opcodes_per_call": opcodes, "unaccounted_calls_per_call": unaccounted,
            "resolved_callees": resolved_calls, "fn": fn}


def vector(source, environment=None):
    """The registered coordinate: both components over one full domain sweep."""
    row = account(source, environment)
    values = tuple(row["fn"](x) for x in INPUTS)
    return {"opcodes": SWEEP * row["opcodes_per_call"],
            "unaccounted_calls": SWEEP * row["unaccounted_calls_per_call"],
            "opcodes_per_call": row["opcodes_per_call"],
            "unaccounted_calls_per_call": row["unaccounted_calls_per_call"],
            "callees": row["resolved_callees"],
            "exact_parity_on_all_eight_inputs": values == PARITY}


def dominates(left, right):
    """Product order written as minimization: <= in both, < in at least one."""
    weak = (left["opcodes"] <= right["opcodes"]
            and left["unaccounted_calls"] <= right["unaccounted_calls"])
    strict = (left["opcodes"] < right["opcodes"]
              or left["unaccounted_calls"] < right["unaccounted_calls"])
    return weak and strict


def relation(left, right):
    if dominates(left, right):
        return "DOMINATES"
    if dominates(right, left):
        return "IS_DOMINATED_BY"
    if (left["opcodes"], left["unaccounted_calls"]) == (right["opcodes"], right["unaccounted_calls"]):
        return "EQUAL"
    return "INCOMPARABLE"


HEAD = "def f(x):\n    a,b,c=x\n"

REGISTERED = {
    # The two faithful flat-linear threshold shapes and their non-neural rivals,
    # byte-compatible with the STR repair unit's registered witnesses.
    "WRITTEN_SHARED_SUM_NET": HEAD + ("    s=a+b+c\n    h0=int(s>=1)\n    h1=int(s>=2)\n"
                                      "    h2=int(s>=3)\n    return int(h0-h1+h2>=1)\n"),
    "WRITTEN_THRESHOLD_DNF4": HEAD + ("    h001=int((-a-b+c)>=1)\n    h010=int((-a+b-c)>=1)\n"
                                      "    h100=int((a-b-c)>=1)\n    h111=int((a+b+c)>=3)\n"
                                      "    return int((h001+h010+h100+h111)>=1)\n"),
    "WRITTEN_XOR": HEAD + "    return (a^b)^c\n",
    "WRITTEN_LOOKUP8": HEAD + "    return (0,1,1,0,1,0,0,1)[(a<<2)|(b<<1)|c]\n",
    # SN-7's two gaming realizations: work moved out of the candidate frame.
    "DELEGATING_SUM_AND_MASK": "def f(x):\n    return sum(x)&1\n",
    "NET_DELEGATING_THE_SUM": ("def f(x):\n    s=sum(x)\n    h0=int(s>=1)\n    h1=int(s>=2)\n"
                               "    h2=int(s>=3)\n    return int(h0-h1+h2>=1)\n"),
}

# Exports of the written shared-sum net: each moves one written form into a
# callee with no Python code object. These are the anti-gaming witnesses.
EXPORTS = {
    "EXPORT_THE_SUM": ("def f(x):\n    s=sum(x)\n    h0=int(s>=1)\n    h1=int(s>=2)\n"
                       "    h2=int(s>=3)\n    return int(h0-h1+h2>=1)\n"),
    "EXPORT_THE_WHOLE_FUNCTION": "def f(x):\n    return delegate(x)\n",
}


def opcode_contract():
    """The static layout this coordinate inherits from the STR repair unit."""
    base = account(HEAD + "    return 0\n")["opcodes_per_call"]
    require(base == 6, "UNVERIFIABLE: opcode layout differs from registered BASE6")
    own, shared = {}, {}
    for degree in range(1, 4):
        expression = "+".join(("a", "b", "c")[:degree])
        own[degree] = account(HEAD + "    h=int(" + expression + ">=1)\n"
                              "    return 0\n")["opcodes_per_call"] - base
        shared[degree] = account(HEAD + "    s=" + expression + "\n"
                                 "    return 0\n")["opcodes_per_call"] - base
        require(own[degree] == 4 + 2 * degree and shared[degree] == 2 * degree,
                "UNVERIFIABLE: hidden/form opcode layout differs")
    return {"base": base, "own_hidden": {str(d): c for d, c in own.items()},
            "shared_form": {str(d): c for d, c in shared.items()},
            "inherited_from": "STRUCTURAL_THRESHOLD_ANALYTIC_CORRECTION_V1 opcode contract"}


def certified_lower(shape, active_gates, total_support=6):
    """STR's proved per-call opcode lower bounds, unchanged by this repair."""
    require(type(active_gates) is int and active_gates >= 3, "need proved active-gate bound")
    if shape == "A":
        require(type(total_support) is int
                and max(6, active_gates) <= total_support <= 3 * active_gates,
                "need proved support-incidence bound")
        return 9 + 6 * active_gates + 2 * total_support
    require(shape == "B", "unknown registered shape")
    return 15 + 8 * active_gates


def scalar_weight_rejection(rows):
    """Why a single scalar charge per unaccounted call is not registered.

    A scalar coordinate opcodes + w * unaccounted_calls restores both SN-7
    orderings only above a threshold fitted from the very comparison it is
    meant to decide. The threshold is reported as a negative witness.
    """
    xor, delegating = rows["WRITTEN_XOR"], rows["DELEGATING_SUM_AND_MASK"]
    written_net, delegating_net = rows["WRITTEN_SHARED_SUM_NET"], rows["NET_DELEGATING_THE_SUM"]
    smallest = None
    for weight in range(0, 65):
        restored_pair = (delegating["opcodes"] + weight * delegating["unaccounted_calls"]
                         > xor["opcodes"] + weight * xor["unaccounted_calls"])
        restored_net = (delegating_net["opcodes"] + weight * delegating_net["unaccounted_calls"]
                        > written_net["opcodes"] + weight * written_net["unaccounted_calls"])
        if restored_pair and restored_net:
            smallest = weight
            break
    require(type(smallest) is int and smallest > 0, "scalar rejection witness unavailable")
    return {"smallest_weight_restoring_both_orderings": smallest,
            "weight_is_fitted_to_the_decided_comparison": True,
            "registered_as_the_coordinate": False,
            "reason": "an outcome-fitted constant is not a derived accounting rule"}


def written_shared_sum_net(x):
    """Python-coded descendant: its work is statically accountable."""
    a, b, c = x
    s = a + b + c
    h0 = int(s >= 1)
    h1 = int(s >= 2)
    h2 = int(s >= 3)
    return int(h0 - h1 + h2 >= 1)


def written_xor_net(x):
    """Python-coded non-neural descendant."""
    return x[0] ^ x[1] ^ x[2]


def main():
    rows = {name: vector(source) for name, source in REGISTERED.items()}
    for name, row in rows.items():
        require(row["exact_parity_on_all_eight_inputs"],
                "registered realization does not compute parity: " + name)

    # A. The recorded SN-7 defect, reproduced in the single-component coordinate.
    single = {name: row["opcodes"] for name, row in rows.items()}
    require(single["DELEGATING_SUM_AND_MASK"] < single["WRITTEN_XOR"],
            "SN-7 opcode gaming witness lost")
    require(single["NET_DELEGATING_THE_SUM"] < single["WRITTEN_SHARED_SUM_NET"],
            "SN-7 class-member gaming witness lost")

    # B. The same comparisons under the registered product order.
    pairs = {
        "DELEGATING_SUM_AND_MASK_vs_WRITTEN_XOR":
            relation(rows["DELEGATING_SUM_AND_MASK"], rows["WRITTEN_XOR"]),
        "NET_DELEGATING_THE_SUM_vs_WRITTEN_SHARED_SUM_NET":
            relation(rows["NET_DELEGATING_THE_SUM"], rows["WRITTEN_SHARED_SUM_NET"]),
        "WRITTEN_XOR_vs_WRITTEN_SHARED_SUM_NET":
            relation(rows["WRITTEN_XOR"], rows["WRITTEN_SHARED_SUM_NET"]),
        "WRITTEN_XOR_vs_WRITTEN_THRESHOLD_DNF4":
            relation(rows["WRITTEN_XOR"], rows["WRITTEN_THRESHOLD_DNF4"]),
        "WRITTEN_LOOKUP8_vs_WRITTEN_SHARED_SUM_NET":
            relation(rows["WRITTEN_LOOKUP8"], rows["WRITTEN_SHARED_SUM_NET"]),
    }
    require(pairs["DELEGATING_SUM_AND_MASK_vs_WRITTEN_XOR"] == "INCOMPARABLE",
            "delegation must not win under the product order")
    require(pairs["NET_DELEGATING_THE_SUM_vs_WRITTEN_SHARED_SUM_NET"] == "INCOMPARABLE",
            "a delegating class member must not fall below the written bound")
    require(pairs["WRITTEN_XOR_vs_WRITTEN_SHARED_SUM_NET"] == "DOMINATES",
            "written-against-written exclusion lost")
    require(pairs["WRITTEN_XOR_vs_WRITTEN_THRESHOLD_DNF4"] == "DOMINATES",
            "written-against-written exclusion lost")

    # C. Anti-gaming, both export routes out of the candidate frame.
    parent = rows["WRITTEN_SHARED_SUM_NET"]
    wrapper = "def f(x):\n    return delegate(x)\n"

    # C1. Export into a callee with no Python code object: the work cannot be
    #     accounted, so the second component strictly rises.
    opaque_export = rows["NET_DELEGATING_THE_SUM"]
    require(opaque_export["unaccounted_calls"] > parent["unaccounted_calls"],
            "opaque export did not raise the unaccounted-call component")
    opaque_relation = relation(opaque_export, parent)

    # C2. Export into a Python-coded callee: the work stays accounted by
    #     recursion, so the wrapper pays the parent's opcodes plus its own.
    accounted_export = vector(wrapper, {"delegate": written_shared_sum_net})
    require(accounted_export["opcodes"] > parent["opcodes"],
            "an accounted export must not be cheaper than the work it wraps")
    require(accounted_export["unaccounted_calls"] == parent["unaccounted_calls"],
            "an accounted export must inherit its callee's unaccounted calls")
    accounted_relation = relation(accounted_export, parent)
    require(accounted_relation == "IS_DOMINATED_BY",
            "an accounted export must not dominate the work it wraps")

    # C3. Neither route dominates the realization it was derived from.
    require(opaque_relation != "DOMINATES" and accounted_relation != "DOMINATES",
            "an export dominated its parent: the coordinate is gameable")

    # D. The STR opaque-wrapper control: a C-implemented outer callable with a
    #    Python descendant. Both families score identically, so this coordinate
    #    abstains rather than separating them.
    neural_wrapper = vector(wrapper, {"delegate": partial(written_shared_sum_net)})
    non_neural_wrapper = vector(wrapper, {"delegate": partial(written_xor_net)})
    require(not hasattr(partial(written_shared_sum_net), "__code__"),
            "opaque-wrapper control changed: partial exposes a code object")
    require(relation(neural_wrapper, non_neural_wrapper) == "EQUAL",
            "opaque wrappers must remain indistinguishable in this coordinate")
    require(neural_wrapper["unaccounted_calls"] > 0,
            "an opaque wrapper must record an unaccounted call")

    # E. The opcode component's proved lower bound is unchanged by the repair.
    contract = opcode_contract()
    require(parent["opcodes_per_call"] == certified_lower("A", 3, 6)
            == certified_lower("B", 3) == 39,
            "opcode component lower bound moved")
    require(parent["opcodes"] == 312, "per-sweep opcode bound moved")

    receipt = {
        "terminal": "GRAND_GMI_DELEGATION_INVARIANT_COST_GREEN_AT_FINITE_SCOPE",
        "schema": "GMI_DELEGATION_INVARIANT_COST_RECEIPT_V1",
        "coordinate": {
            "name": "python_static_cost_vector_per_full_domain_sweep",
            "components": ["opcodes", "unaccounted_calls"],
            "order": "componentwise minimisation; domination is <= in both and < in one",
            "accounted_call": "a statically resolved Python-coded callee, charged by recursion",
            "unaccounted_call": "a statically resolved callee with no Python code object",
            "resolution": "abstract straight-line stack accounting over dis instructions",
            "timing_used": False,
            "tracing_used": False,
            "refuses_rather_than_guesses": True,
            "nesting_limit": 8,
        },
        "opcode_contract": contract,
        "registered_realizations": {
            name: {"opcodes": row["opcodes"], "unaccounted_calls": row["unaccounted_calls"],
                   "opcodes_per_call": row["opcodes_per_call"],
                   "unaccounted_calls_per_call": row["unaccounted_calls_per_call"],
                   "callees": row["callees"]}
            for name, row in sorted(rows.items())
        },
        "single_component_defect_reproduced": {
            "coordinate": "python_opcode_count_per_full_domain_sweep",
            "delegating_beats_written_xor": True,
            "delegating_class_member_below_derived_bound": True,
            "observed": {name: single[name] for name in sorted(single)},
        },
        "product_order_relations": pairs,
        "anti_gaming": {
            "statement": "an export out of the candidate frame either leaves its work "
                         "accountable, in which case recursion charges it here, or leaves it "
                         "unaccountable, in which case the second component strictly rises; "
                         "neither route yields a dominating realization",
            "opaque_export": {"opcodes": opaque_export["opcodes"],
                              "unaccounted_calls": opaque_export["unaccounted_calls"],
                              "relation_to_written_parent": opaque_relation},
            "accounted_export": {"opcodes": accounted_export["opcodes"],
                                 "unaccounted_calls": accounted_export["unaccounted_calls"],
                                 "relation_to_written_parent": accounted_relation},
            "python_coded_callee_is_accounted_by_recursion": True,
            "no_export_dominates_its_parent": True,
        },
        "opaque_wrapper_control": {
            "neural_wrapper": {"opcodes": neural_wrapper["opcodes"],
                               "unaccounted_calls": neural_wrapper["unaccounted_calls"]},
            "non_neural_wrapper": {"opcodes": non_neural_wrapper["opcodes"],
                                   "unaccounted_calls": non_neural_wrapper["unaccounted_calls"]},
            "coordinate_separates_them": False,
            "inherited_from": "STR delegation_counterexample",
        },
        "rejected_alternative_scalar_charge": scalar_weight_rejection(rows),
        "sn3_bound_in_the_repaired_coordinate": {
            "opcode_component_minimum_per_call": 39,
            "opcode_component_minimum_per_sweep": 312,
            "bound_changed_by_the_repair": False,
            "reason": "certified_lower is a static syntactic count; the repair adds a second "
                      "component rather than altering the first",
            "class_bound_is_now_a_frontier": True,
            "written_attaining_witness_unaccounted_calls_per_sweep":
                parent["unaccounted_calls"],
        },
        "explicitly_not_established": {
            "universal_delegated_family_exclusion": False,
            "callee_work_measured_dynamically": False,
            "timing_or_physical_cost_ordering": False,
            "coverage_of_realizations_outside_the_straight_line_grammar": False,
            "independent_replication": False,
        },
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
