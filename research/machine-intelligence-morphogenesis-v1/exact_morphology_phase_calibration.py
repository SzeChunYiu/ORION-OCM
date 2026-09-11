#!/usr/bin/env python3
"""Exact tiny morphology-frontier calibration.

Ecology: one supervised example teaches a binary constant label, then the machine
must output that label for both binary probe inputs. Labels 0/1 are equally
weighted. Candidate morphologies come from structured_adaptive_grammar_census.

This is a resource-rational / algorithm-selection calibration, NOT a novelty
claim for GMI.
"""

from structured_adaptive_grammar_census import (
    all_morphologies, initial_state, learn, infer,
)
import json

# Primitive description costs, deliberately simple and frozen for this calibration.
COMPUTE_DESC = {
    "INPUT": 1, "STATE": 1, "NEIGHBOR": 1, "NOT_INPUT": 2,
    "XOR_INPUT_STATE": 3, "XOR_INPUT_NEIGHBOR": 3,
    "AND_INPUT_STATE": 3, "AND_INPUT_NEIGHBOR": 3,
}
UPDATE_DESC = {
    "HOLD": 0, "WRITE_LABEL": 1, "WRITE_ERROR": 2,
    "XOR_ERROR": 3, "COPY_OUTPUT": 1, "COPY_NEIGHBOR": 1,
}
EDGE_DESC = {
    "FIXED_OFF": 0, "FIXED_ON": 0,
    "TOGGLE_ON_ERROR": 2, "SET_ON_ERROR": 2,
}


def description_cost(m):
    f0, f1, u0, u1, edge_mode = m
    return (
        COMPUTE_DESC[f0] + COMPUTE_DESC[f1]
        + UPDATE_DESC[u0] + UPDATE_DESC[u1]
        + EDGE_DESC[edge_mode]
    )


def uses_neighbor(op):
    return "NEIGHBOR" in op


def perfect_on_ecology(m):
    for label in (0, 1):
        state = initial_state((0, 1), m[4])
        state = learn(m, state, 0, label)
        if [infer(m, state, x)[0] for x in (0, 1)] != [label, label]:
            return False
    return True


def resource_vector(m):
    """Expected raw resource vector over equally likely labels.

    Coordinates:
      description_tokens
      changed_local_state_bits_during_training
      changed_edge_bits_during_training
      neighbor_messages_per_future_query
      output_compute_units_per_future_query
    """
    desc = description_cost(m)
    state_writes = 0.0
    edge_writes = 0.0
    messages_per_query = 0.0

    for label in (0, 1):
        before = initial_state((0, 1), m[4])
        after = learn(m, before, 0, label)
        state_writes += ((before[0] != after[0]) + (before[1] != after[1])) / 2.0
        edge_writes += (before[2] != after[2]) / 2.0
        # Output-node neighbor use is charged only when the learned edge is live.
        messages_per_query += (1.0 if uses_neighbor(m[0]) and after[2] else 0.0) / 2.0

    query_compute = COMPUTE_DESC[m[0]]
    return (desc, state_writes, edge_writes, messages_per_query, query_compute)


def dominates(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def census():
    perfect = []
    for m in all_morphologies():
        if perfect_on_ecology(m):
            perfect.append((resource_vector(m), m))

    pareto = []
    for r, m in perfect:
        if not any(dominates(r2, r) for r2, _m2 in perfect if r2 != r):
            pareto.append((r, m))

    vectors = sorted({r for r, _m in pareto})
    return {
        "schema": "ExactMorphologyPhaseCalibrationV1",
        "perfect_morphologies": len(perfect),
        "pareto_morphologies": len(pareto),
        "pareto_resource_vectors": [list(v) for v in vectors],
        "state_storage_vector": [3, 0.5, 0.0, 0.0, 1],
        "topology_storage_vector": [4, 0.0, 0.5, 0.5, 1],
        "scalar_boundary": "topology wins iff w_state > 2*w_desc + w_edge + H*w_message",
        "terminal": "EXACT_MORPHOLOGY_PHASE_BOUNDARY_CALIBRATED__RESOURCE_RATIONAL_PARENT_OWNED",
    }


if __name__ == "__main__":
    print(json.dumps(census(), indent=2, sort_keys=True))
