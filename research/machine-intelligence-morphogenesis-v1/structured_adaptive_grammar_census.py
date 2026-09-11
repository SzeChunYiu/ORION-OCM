#!/usr/bin/env python3
"""Exact Stage C-v1 calibration for a small structured adaptive morphology grammar.

This is deliberately NOT a universal/intelligence claim. It asks whether state
adaptation and topology adaptation create different developmental phenotype
classes under a fixed tiny two-node architecture budget, while retaining the
finite-state-transducer parent as the algebraic upper bound.
"""

from itertools import product
import json

COMPUTE_OPS = (
    "INPUT", "STATE", "NEIGHBOR", "NOT_INPUT",
    "XOR_INPUT_STATE", "XOR_INPUT_NEIGHBOR",
    "AND_INPUT_STATE", "AND_INPUT_NEIGHBOR",
)
UPDATE_OPS = (
    "HOLD", "WRITE_LABEL", "WRITE_ERROR", "XOR_ERROR",
    "COPY_OUTPUT", "COPY_NEIGHBOR",
)
EDGE_MODES = ("FIXED_OFF", "FIXED_ON", "TOGGLE_ON_ERROR", "SET_ON_ERROR")
EVENTS = tuple(product((0, 1), (0, 1)))
HISTORIES = ((),) + tuple(product(EVENTS, repeat=1)) + tuple(product(EVENTS, repeat=2))
INITIAL_LOCAL_STATES = ((0, 0), (0, 1))


def compute(op, x, state, neighbor):
    if op == "INPUT": return x
    if op == "STATE": return state
    if op == "NEIGHBOR": return neighbor
    if op == "NOT_INPUT": return 1 - x
    if op == "XOR_INPUT_STATE": return x ^ state
    if op == "XOR_INPUT_NEIGHBOR": return x ^ neighbor
    if op == "AND_INPUT_STATE": return x & state
    if op == "AND_INPUT_NEIGHBOR": return x & neighbor
    raise ValueError(op)


def update(op, state, label, error, neighbor, output):
    if op == "HOLD": return state
    if op == "WRITE_LABEL": return label
    if op == "WRITE_ERROR": return error
    if op == "XOR_ERROR": return state ^ error
    if op == "COPY_OUTPUT": return output
    if op == "COPY_NEIGHBOR": return neighbor
    raise ValueError(op)


def infer(morphology, machine_state, x):
    a, b, edge = machine_state
    f0, f1, _u0, _u1, _emode = morphology
    n0 = b if edge else 0
    n1 = a if edge else 0
    return compute(f0, x, a, n0), compute(f1, x, b, n1)


def learn(morphology, machine_state, x, label):
    a, b, edge = machine_state
    h0, h1 = infer(morphology, machine_state, x)
    error = h0 ^ label
    n0 = b if edge else 0
    n1 = a if edge else 0
    f0, f1, u0, u1, emode = morphology
    del f0, f1
    a2 = update(u0, a, label, error, n0, h0)
    b2 = update(u1, b, label, error, n1, h1)
    if emode == "FIXED_OFF":
        edge2 = 0
    elif emode == "FIXED_ON":
        edge2 = 1
    elif emode == "TOGGLE_ON_ERROR":
        edge2 = edge ^ error
    elif emode == "SET_ON_ERROR":
        edge2 = 1 if error else edge
    else:
        raise ValueError(emode)
    return a2, b2, edge2


def initial_state(local_pair, edge_mode):
    a, b = local_pair
    return a, b, 1 if edge_mode == "FIXED_ON" else 0


def developmental_phenotype(morphology):
    """Outputs for x=0,1 after every registered history and initial seed."""
    out = []
    for local_pair in INITIAL_LOCAL_STATES:
        for history in HISTORIES:
            state = initial_state(local_pair, morphology[4])
            for x, label in history:
                state = learn(morphology, state, x, label)
            out.extend(infer(morphology, state, x)[0] for x in (0, 1))
    return tuple(out)


def all_morphologies():
    return product(COMPUTE_OPS, COMPUTE_OPS, UPDATE_OPS, UPDATE_OPS, EDGE_MODES)


def family_predicates():
    return {
        "STATIC": lambda m: m[2] == "HOLD" and m[3] == "HOLD" and m[4] in ("FIXED_OFF", "FIXED_ON"),
        "STATE_ADAPTIVE": lambda m: m[4] in ("FIXED_OFF", "FIXED_ON"),
        "TOPOLOGY_ADAPTIVE": lambda m: m[2] == "HOLD" and m[3] == "HOLD",
        "FULL_ADAPTIVE": lambda m: True,
    }


def census():
    morphologies = tuple(all_morphologies())
    phenotype_sets = {}
    morphology_counts = {}
    for name, pred in family_predicates().items():
        selected = [m for m in morphologies if pred(m)]
        morphology_counts[name] = len(selected)
        phenotype_sets[name] = {developmental_phenotype(m) for m in selected}

    union_single = phenotype_sets["STATE_ADAPTIVE"] | phenotype_sets["TOPOLOGY_ADAPTIVE"]
    result = {
        "schema": "StructuredAdaptiveGrammarCensusV1",
        "registered_histories": len(HISTORIES),
        "initial_local_state_seeds": [list(x) for x in INITIAL_LOCAL_STATES],
        "morphology_counts": morphology_counts,
        "developmental_class_counts": {k: len(v) for k, v in phenotype_sets.items()},
        "state_unique_beyond_static": len(phenotype_sets["STATE_ADAPTIVE"] - phenotype_sets["STATIC"]),
        "topology_unique_beyond_static": len(phenotype_sets["TOPOLOGY_ADAPTIVE"] - phenotype_sets["STATIC"]),
        "topology_unique_beyond_state_adaptive": len(phenotype_sets["TOPOLOGY_ADAPTIVE"] - phenotype_sets["STATE_ADAPTIVE"]),
        "state_unique_beyond_topology_adaptive": len(phenotype_sets["STATE_ADAPTIVE"] - phenotype_sets["TOPOLOGY_ADAPTIVE"]),
        "full_unique_beyond_union_of_single_channels": len(phenotype_sets["FULL_ADAPTIVE"] - union_single),
        "terminal": "STRUCTURED_ADAPTATION_INTERACTION_EXACT__FINITE_STATE_PARENT_SUFFICIENT_FOR_EXPRESSIVITY",
    }
    return result


if __name__ == "__main__":
    print(json.dumps(census(), indent=2, sort_keys=True))
