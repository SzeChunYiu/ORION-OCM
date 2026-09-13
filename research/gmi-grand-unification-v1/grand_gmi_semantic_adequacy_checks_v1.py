#!/usr/bin/env python3
"""Finite response preservation, relational adequacy and update witnesses."""
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location("cut_parent", HERE / "grand_gmi_checks_v1.py")
CUT = module_from_spec(SPEC)
SPEC.loader.exec_module(CUT)


def exact_protocol(acceptable):
    """Independent encoder/decoder enumeration, without intersection tests."""
    actions = tuple(sorted(set().union(*acceptable)))
    for m in range(1, len(acceptable) + 1):
        for encoder in product(range(m), repeat=len(acceptable)):
            for decoder in product(actions, repeat=m):
                if all(decoder[encoder[h]] in allowed for h, allowed in enumerate(acceptable)):
                    return m
    raise AssertionError("nonempty finite obligations have an identity protocol")


def profile_count(acceptable):
    return len(set(acceptable))


def hypergraph_messages(acceptable):
    states, actions = tuple(range(len(acceptable))), (0, 1, 2)
    gamma = {(h, 0): choices for h, choices in enumerate(acceptable)}
    edges = CUT.conflict_hyperedges(gamma, states, (0,), actions)
    return CUT.hypergraph_chromatic_number(edges, states)


def overlap_witnesses():
    pair = (frozenset((0, 1)), frozenset((0, 2)))
    triple = (frozenset((0, 1)), frozenset((1, 2)), frozenset((0, 2)))
    assert profile_count(pair) == 2 and exact_protocol(pair) == 1
    assert profile_count(triple) == 3 and exact_protocol(triple) == 2
    assert all(a & b for i, a in enumerate(triple) for b in triple[i + 1:])
    assert not set.intersection(*(set(x) for x in triple))
    return {"common_action": {"full_response_classes": 2, "task_messages": 1},
            "three_way_conflict": {"full_response_classes": 3, "task_messages": 2,
                                   "all_pairs_compatible": True}}


def exhaustive_relational_check():
    subsets = CUT.nonempty_subsets((0, 1, 2))
    total = strict = functions = 0
    for choices in product(subsets, repeat=3):
        messages = exact_protocol(choices)
        assert messages == hypergraph_messages(choices)
        classes = profile_count(choices)
        assert messages <= classes
        total += 1
        strict += messages < classes
        if all(len(x) == 1 for x in choices):
            assert messages == classes
            functions += 1
    return {"three_state_three_action_instances": total,
            "strict_response_vs_task_gaps": strict,
            "singleton_function_equalities": functions}


def growth_witness():
    rows = []
    for horizon in range(1, 7):
        worlds = tuple(product((0, 1), repeat=horizon))
        action_traces = tuple(product((0, 1), repeat=horizon))  # 0 safe; 1 probe
        signatures = {tuple(tuple(1 if action == 0 else bit for action, bit in zip(trace, word))
                            for trace in action_traces) for word in worlds}
        assert len(signatures) == 2 ** horizon
        assert all(all(1 if action == 0 else bit for action, bit in zip((0,) * horizon, word))
                   for word in worlds)
        rows.append({"horizon": horizon, "full_response_classes": len(signatures),
                     "adequate_safe_controller_states": 1})
    return rows


def signature(outputs, transition, state, horizon):
    result = []
    for _ in range(horizon + 1):
        result.append(outputs[state])
        state = transition[state]
    return tuple(result)


def congruent(labels, transition):
    return all(labels[s] != labels[t] or labels[transition[s]] == labels[transition[t]]
               for s in range(len(labels)) for t in range(len(labels)))


def continuation_checks():
    # A positive-horizon quotient can fail to update into that same horizon.
    delayed_outputs, delayed_transition = (0, 0, 0, 1), (0, 2, 3, 3)
    delayed = tuple(signature(delayed_outputs, delayed_transition, s, 1) for s in range(4))
    assert delayed[0] == delayed[1]
    assert delayed[delayed_transition[0]] != delayed[delayed_transition[1]]
    systems = countdown = stationary_failures = 0
    for outputs in product((0, 1), repeat=3):
        for transition in product(range(3), repeat=3):
            for horizon in (1, 2):
                current = tuple(signature(outputs, transition, s, horizon) for s in range(3))
                previous = tuple(signature(outputs, transition, s, horizon - 1) for s in range(3))
                assert all(current[s] != current[t] or previous[transition[s]] == previous[transition[t]]
                           for s in range(3) for t in range(3))
                countdown += 1
            # Current outputs alone need not permit a recursive update.
            stationary_failures += not congruent(outputs, transition)
            # Finite partition refinement adds successor distinctions to a fixed point.
            labels = outputs
            for _ in range(3):
                keys = tuple((labels[s], labels[transition[s]]) for s in range(3))
                ids = {key: i for i, key in enumerate(dict.fromkeys(keys))}
                refined = tuple(ids[key] for key in keys)
                same_partition = all((labels[s] == labels[t]) == (refined[s] == refined[t])
                                     for s in range(3) for t in range(3))
                labels = refined
                if same_partition:
                    break
            assert congruent(labels, transition)
            systems += 1
    return {"finite_systems": systems, "countdown_update_checks": countdown,
            "positive_horizon_stationary_update_counterexample": True,
            "current_output_quotients_not_right_congruent": stationary_failures,
            "stable_quotients_right_congruent": systems}


def null_history_versions():
    # Same joint law, two versions of P(Y=1|H=h) differing only where P(H=h)=0.
    history_mass = (Fraction(1), Fraction(0))
    versions = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(1)))
    joint = tuple(tuple((history_mass[h] * (1 - row[h]), history_mass[h] * row[h])
                        for h in range(2)) for row in versions)
    assert joint[0] == joint[1]
    assert [len(set(row)) for row in versions] == [1, 2]
    return {"same_joint_law": True, "all_history_response_class_counts": [1, 2],
            "null_history_extension_must_be_declared": True}


def run():
    return {"terminal": "GRAND_GMI_SEMANTIC_ADEQUACY_CORRECTION_GREEN_AT_FINITE_SCOPE",
            "determinism": "exhaustive/no-rng/exact-integer-and-rational",
            "overlap_witnesses": overlap_witnesses(),
            "relational_enumeration": exhaustive_relational_check(),
            "response_growth_without_task_memory_growth": growth_witness(),
            "continuation": continuation_checks(), "null_history": null_history_versions(),
            "boundary": "response preservation is not relational task necessity; no empirical closure"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
