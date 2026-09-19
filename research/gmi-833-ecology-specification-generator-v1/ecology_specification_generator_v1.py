#!/usr/bin/env python3
"""Exact registered-product ecology/specification generator for Issue #957.

The operational construction receives only external ecology coordinates.  It has
no implementation-family input and does not search or rank implementations.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import inspect
import itertools
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Sequence, Tuple


HERE = Path(__file__).resolve().parent
ISSUE = 957
PARENT_ISSUE = 833
SOURCE_PR = 959
FREEZE_COMMIT = "e5d6443dfe57603245f68abc7fed6c39aac4d677"
FROZEN_MAIN = "fcbb8c08ce36b2970079ed715d5e757f28da46d2"
TERMINAL = "GMI_833_ARCHITECTURE_NEUTRAL_REGISTERED_ECOLOGY_PRODUCT_AND_TWINS_PROVED"

TARGET_ROWS = (
    "Define an architecture-neutral generator of behavioral specifications.",
    "Define systematic environment/ecology families.",
    "Vary observability.",
    "Vary recurrence.",
    "Vary uncertainty/noise.",
    "Vary causal ambiguity/intervention access.",
    "Vary compositional structure.",
    "Vary spatial/locality structure.",
    "Vary symmetry/equivariance.",
    "Vary communication topology.",
    "Vary multi-agent competition/cooperation.",
    "Vary verification availability/cost.",
    "Vary memory price.",
    "Vary compute price.",
    "Vary communication price.",
    "Vary energy price.",
    "Vary developmental horizon.",
    "Vary nonstationarity/drift.",
    "Vary embodiment/sensor-action constraints.",
    "Construct matched positive/negative ecology twins.",
    "Construct ecology families not designed around known architectures.",
)

# The terms are used only by the audit below; none is a generator input or score
# coordinate.  Phrase normalization makes the scan robust to punctuation.
KNOWN_FAMILY_PHRASES = (
    "finite state automata",
    "linear regression",
    "linear classifier",
    "generalized linear model",
    "kernel method",
    "nearest neighbor",
    "associative memory",
    "retrieval augmented",
    "decision tree",
    "symbolic logic",
    "program synthesis",
    "dynamic programming",
    "model free reinforcement learning",
    "model based reinforcement learning",
    "bayesian inference",
    "probabilistic graphical model",
    "particle inference",
    "feed forward neural network",
    "backpropagation",
    "convolutional neural network",
    "recurrent neural network",
    "long short term memory",
    "gated recurrent unit",
    "attention mechanism",
    "transformer",
    "graph neural network",
    "state space model",
    "mixture of experts",
    "autoregressive generative",
    "latent variable generative",
    "diffusion model",
    "energy based model",
    "evolutionary algorithm",
    "cellular automaton",
    "neuro symbolic",
    "meta learning",
)


def _axis(
    axis_id: str,
    parent_row: str,
    probe: str,
    false_token: str,
    false_payload: Mapping[str, Any],
    true_token: str,
    true_payload: Mapping[str, Any],
    semantic_quantity: str,
) -> Dict[str, Any]:
    return {
        "id": axis_id,
        "parent_row": parent_row,
        "probe": probe,
        "semantic_quantity": semantic_quantity,
        "levels": [
            {"token": false_token, "expected_probe": False, "payload": dict(false_payload)},
            {"token": true_token, "expected_probe": True, "payload": dict(true_payload)},
        ],
    }


AXES: Tuple[Dict[str, Any], ...] = (
    _axis(
        "observability",
        "Vary observability.",
        "required_states_are_distinguishable",
        "o7q",
        {"states": [0, 1], "observation_partition": [[0, 1]], "required_pair": [0, 1]},
        "o7r",
        {"states": [0, 1], "observation_partition": [[0], [1]], "required_pair": [0, 1]},
        "partition separation of the required state pair",
    ),
    _axis(
        "recurrence",
        "Vary recurrence.",
        "transition_graph_contains_a_cycle",
        "r2m",
        {"states": [0, 1], "transition_edges": [[0, 1]]},
        "r2n",
        {"states": [0, 1], "transition_edges": [[0, 1], [1, 0]]},
        "directed-cycle existence",
    ),
    _axis(
        "uncertainty_noise",
        "Vary uncertainty/noise.",
        "registered_transition_is_single_outcome",
        "u4c",
        {"outcomes": [0, 1], "integer_weights": [1, 1]},
        "u4d",
        {"outcomes": [0, 1], "integer_weights": [0, 1]},
        "positive-probability transition-support cardinality",
    ),
    _axis(
        "causal_intervention_access",
        "Vary causal ambiguity/intervention access.",
        "ambiguous_cause_can_be_intervened_on",
        "c9a",
        {"causes": [0, 1], "observational_images": [0, 0], "intervenable_causes": []},
        "c9b",
        {"causes": [0, 1], "observational_images": [0, 0], "intervenable_causes": [0]},
        "intervention access under observational aliasing",
    ),
    _axis(
        "compositional_structure",
        "Vary compositional structure.",
        "two_disjoint_components_are_exposed",
        "p3f",
        {"variables": [0, 1], "factor_scopes": [[0, 1]]},
        "p3g",
        {"variables": [0, 1], "factor_scopes": [[0], [1]]},
        "nontrivial disjoint factorization",
    ),
    _axis(
        "spatial_locality",
        "Vary spatial/locality structure.",
        "all_effects_respect_registered_radius",
        "s8j",
        {"sites": [0, 1, 2], "influence_edges": [[0, 2]], "radius": 1},
        "s8k",
        {"sites": [0, 1, 2], "influence_edges": [[0, 1]], "radius": 1},
        "maximum interaction distance relative to radius",
    ),
    _axis(
        "symmetry_equivariance",
        "Vary symmetry/equivariance.",
        "outcome_is_invariant_under_registered_swap",
        "y5t",
        {"points": [0, 1], "swap": [1, 0], "outcome_by_point": [0, 1]},
        "y5u",
        {"points": [0, 1], "swap": [1, 0], "outcome_by_point": [1, 1]},
        "invariance of the outcome table under a nonidentity permutation",
    ),
    _axis(
        "communication_topology",
        "Vary communication topology.",
        "message_path_exists_from_sender_to_receiver",
        "t1h",
        {"agents": [0, 1], "directed_links": [], "required_route": [0, 1]},
        "t1i",
        {"agents": [0, 1], "directed_links": [[0, 1]], "required_route": [0, 1]},
        "directed reachability in the communication graph",
    ),
    _axis(
        "multi_agent_payoff_relation",
        "Vary multi-agent competition/cooperation.",
        "agents_share_an_optimal_joint_choice",
        "a6v",
        {"joint_choices": [0, 1], "payoff_agent_0": [1, 0], "payoff_agent_1": [0, 1]},
        "a6w",
        {"joint_choices": [0, 1], "payoff_agent_0": [1, 0], "payoff_agent_1": [1, 0]},
        "intersection of individual payoff-maximizing joint choices",
    ),
    _axis(
        "verification_availability_cost",
        "Vary verification availability/cost.",
        "verification_is_available_within_budget",
        "v0p",
        {"verifier_available": True, "verification_cost": 3, "verification_budget": 2},
        "v0q",
        {"verifier_available": True, "verification_cost": 1, "verification_budget": 2},
        "verification availability and price relative to budget",
    ),
    _axis(
        "memory_price",
        "Vary memory price.",
        "required_memory_is_affordable",
        "m4x",
        {"required_units": 1, "unit_price": 3, "budget": 2},
        "m4y",
        {"required_units": 1, "unit_price": 1, "budget": 2},
        "memory expenditure relative to budget",
    ),
    _axis(
        "compute_price",
        "Vary compute price.",
        "required_compute_is_affordable",
        "k2e",
        {"required_units": 1, "unit_price": 3, "budget": 2},
        "k2f",
        {"required_units": 1, "unit_price": 1, "budget": 2},
        "compute expenditure relative to budget",
    ),
    _axis(
        "communication_price",
        "Vary communication price.",
        "required_communication_is_affordable",
        "q8s",
        {"required_units": 1, "unit_price": 3, "budget": 2},
        "q8t",
        {"required_units": 1, "unit_price": 1, "budget": 2},
        "communication expenditure relative to budget",
    ),
    _axis(
        "energy_price",
        "Vary energy price.",
        "required_energy_is_affordable",
        "e1l",
        {"required_units": 1, "unit_price": 3, "budget": 2},
        "e1m",
        {"required_units": 1, "unit_price": 1, "budget": 2},
        "energy expenditure relative to budget",
    ),
    _axis(
        "developmental_horizon",
        "Vary developmental horizon.",
        "required_developmental_sequence_fits_horizon",
        "d7b",
        {"required_steps": 2, "available_steps": 1},
        "d7c",
        {"required_steps": 2, "available_steps": 2},
        "available developmental steps relative to required steps",
    ),
    _axis(
        "nonstationarity_drift",
        "Vary nonstationarity/drift.",
        "calibration_is_stable_across_epochs",
        "n3r",
        {"epochs": [0, 1], "calibration_target": [0, 1]},
        "n3s",
        {"epochs": [0, 1], "calibration_target": [1, 1]},
        "cross-epoch equality of the calibration target",
    ),
    _axis(
        "embodiment_sensor_action_constraints",
        "Vary embodiment/sensor-action constraints.",
        "required_sensor_action_pair_is_available",
        "b9z",
        {"required_pair": ["sensor_0", "action_0"], "available_pairs": [["sensor_0", "action_1"]]},
        "b9a",
        {"required_pair": ["sensor_0", "action_0"], "available_pairs": [["sensor_0", "action_0"]]},
        "membership of the required sensor-action pair in the embodied interface",
    ),
)

AXIS_BY_ID = {axis["id"]: axis for axis in AXES}
AXIS_IDS = tuple(axis["id"] for axis in AXES)
PROBE_IDS = tuple(axis["probe"] for axis in AXES)

# A human semantic audit is load-bearing.  Token/parameter scans alone cannot
# establish that the chosen axes are external rather than disguised mechanisms.
EXTERNAL_SEMANTICS_RATIONALES = {
    "observability": "A partition of environment states into emitted observations is an external information contract.",
    "recurrence": "Cycle existence is a property of the environment transition graph.",
    "uncertainty_noise": "Positive transition-outcome support is an external stochastic-law property.",
    "causal_intervention_access": "Observational images and permitted interventions are external experiment-interface properties.",
    "compositional_structure": "Variable scopes and their factorization describe the task relation, not an implementation.",
    "spatial_locality": "Sites, influence edges, and radius describe external interaction geometry.",
    "symmetry_equivariance": "A permutation and external outcome table determine environmental invariance.",
    "communication_topology": "Agents and permitted directed links define the external message channel.",
    "multi_agent_payoff_relation": "Payoff tables define external incentives and compatible optima.",
    "verification_availability_cost": "Verifier access, price, and budget are external feedback conditions.",
    "memory_price": "Required storage units, their price, and budget are external resource terms.",
    "compute_price": "Required operation units, their price, and budget are external resource terms.",
    "communication_price": "Required message units, their price, and budget are external resource terms.",
    "energy_price": "Required energy units, their price, and budget are external resource terms.",
    "developmental_horizon": "Available interaction steps relative to a required sequence are an external time budget.",
    "nonstationarity_drift": "Cross-epoch target variation is a property of the external data-generating process.",
    "embodiment_sensor_action_constraints": "Available sensor-action pairs define the external interaction interface.",
}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, separators=(",", ": ")) + "\n").encode()


def sha256(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def _same_shape(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(_same_shape(left[key], right[key]) for key in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(_same_shape(a, b) for a, b in zip(left, right))
    return True


def _has_directed_cycle(nodes: Sequence[int], edges: Sequence[Sequence[int]]) -> bool:
    adjacency = {node: [] for node in nodes}
    for source, target in edges:
        if source not in adjacency or target not in adjacency:
            return False
        adjacency[source].append(target)
    color = {node: 0 for node in nodes}

    def visit(node: int) -> bool:
        color[node] = 1
        for target in adjacency[node]:
            if color[target] == 1:
                return True
            if color[target] == 0 and visit(target):
                return True
        color[node] = 2
        return False

    return any(color[node] == 0 and visit(node) for node in nodes)


def _reachable(nodes: Sequence[int], edges: Sequence[Sequence[int]], source: int, target: int) -> bool:
    adjacency = {node: [] for node in nodes}
    for left, right in edges:
        if left not in adjacency or right not in adjacency:
            return False
        adjacency[left].append(right)
    frontier = [source]
    seen = {source}
    while frontier:
        node = frontier.pop()
        if node == target:
            return True
        for neighbor in adjacency[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                frontier.append(neighbor)
    return False


def evaluate_probe(axis_id: str, payload: Mapping[str, Any]) -> bool:
    """Compute the external probe without reading a level token."""
    if axis_id == "observability":
        states = payload["states"]
        blocks = payload["observation_partition"]
        required = payload["required_pair"]
        flattened = [state for block in blocks for state in block]
        if sorted(flattened) != sorted(states) or len(flattened) != len(set(flattened)):
            return False
        locations = {state: index for index, block in enumerate(blocks) for state in block}
        return all(state in locations for state in required) and locations[required[0]] != locations[required[1]]
    if axis_id == "recurrence":
        return _has_directed_cycle(payload["states"], payload["transition_edges"])
    if axis_id == "uncertainty_noise":
        weights = payload["integer_weights"]
        return len(weights) == len(payload["outcomes"]) and sum(weight > 0 for weight in weights) == 1
    if axis_id == "causal_intervention_access":
        aliased = len(set(payload["observational_images"])) < len(payload["causes"])
        return aliased and bool(set(payload["intervenable_causes"]) & set(payload["causes"]))
    if axis_id == "compositional_structure":
        variables = set(payload["variables"])
        scopes = [set(scope) for scope in payload["factor_scopes"]]
        disjoint = all(not (a & b) for i, a in enumerate(scopes) for b in scopes[i + 1 :])
        return len(scopes) >= 2 and disjoint and set().union(*scopes) == variables
    if axis_id == "spatial_locality":
        sites = set(payload["sites"])
        edges = payload["influence_edges"]
        return all(a in sites and b in sites and abs(a - b) <= payload["radius"] for a, b in edges)
    if axis_id == "symmetry_equivariance":
        values = payload["outcome_by_point"]
        permutation = payload["swap"]
        return sorted(permutation) == list(range(len(values))) and all(values[i] == values[permutation[i]] for i in range(len(values)))
    if axis_id == "communication_topology":
        source, target = payload["required_route"]
        return _reachable(payload["agents"], payload["directed_links"], source, target)
    if axis_id == "multi_agent_payoff_relation":
        first = payload["payoff_agent_0"]
        second = payload["payoff_agent_1"]
        if len(first) != len(payload["joint_choices"]) or len(second) != len(first):
            return False
        best_first = {i for i, value in enumerate(first) if value == max(first)}
        best_second = {i for i, value in enumerate(second) if value == max(second)}
        return bool(best_first & best_second)
    if axis_id == "verification_availability_cost":
        return payload["verifier_available"] and payload["verification_cost"] <= payload["verification_budget"]
    if axis_id in {"memory_price", "compute_price", "communication_price", "energy_price"}:
        return payload["required_units"] * payload["unit_price"] <= payload["budget"]
    if axis_id == "developmental_horizon":
        return payload["required_steps"] <= payload["available_steps"]
    if axis_id == "nonstationarity_drift":
        targets = payload["calibration_target"]
        return len(targets) == len(payload["epochs"]) and len(set(targets)) == 1
    if axis_id == "embodiment_sensor_action_constraints":
        return payload["required_pair"] in payload["available_pairs"]
    raise KeyError(axis_id)


def validate_registry(registry: Sequence[Mapping[str, Any]] = AXES) -> Dict[str, Any]:
    ids = [axis["id"] for axis in registry]
    probes = [axis["probe"] for axis in registry]
    tokens = [level["token"] for axis in registry for level in axis["levels"]]
    rows = []
    for axis in registry:
        levels = axis["levels"]
        predicate_values = [evaluate_probe(axis["id"], level["payload"]) for level in levels]
        rows.append(
            {
                "axis": axis["id"],
                "carrier_size": len(levels),
                "tokens_distinct": len({level["token"] for level in levels}) == len(levels),
                "payloads_distinct": canonical(levels[0]["payload"]) != canonical(levels[1]["payload"]),
                "computed_probe_values": predicate_values,
                "registered_probe_values": [level["expected_probe"] for level in levels],
                "nondegenerate": predicate_values == [False, True],
            }
        )
    return {
        "axis_count": len(registry),
        "axis_ids_unique": len(ids) == len(set(ids)),
        "probe_ids_unique": len(probes) == len(set(probes)),
        "all_level_tokens_globally_unique": len(tokens) == len(set(tokens)),
        "all_axes_binary_and_nondegenerate": all(row["carrier_size"] == 2 and row["nondegenerate"] for row in rows),
        "rows": rows,
    }


def ecology_from_indices(indices: Sequence[int], registry: Sequence[Mapping[str, Any]] = AXES) -> Dict[str, Any]:
    if len(indices) != len(registry) or any(type(index) is not int or index not in (0, 1) for index in indices):
        raise ValueError("one binary registered index is required for every axis")
    coordinates = []
    payloads = {}
    for axis, index in zip(registry, indices):
        level = axis["levels"][index]
        coordinates.append({"axis": axis["id"], "level_token": level["token"]})
        payloads[axis["id"]] = deepcopy(level["payload"])
    return {"schema": "RegisteredEcologySyntaxV1", "coordinates": coordinates, "payloads": payloads}


def _level_for_token(axis: Mapping[str, Any], token: str) -> Mapping[str, Any] | None:
    return next((level for level in axis["levels"] if level["token"] == token), None)


def syntax_well_formed(ecology: Mapping[str, Any], registry: Sequence[Mapping[str, Any]] = AXES) -> bool:
    if set(ecology) != {"schema", "coordinates", "payloads"} or ecology.get("schema") != "RegisteredEcologySyntaxV1":
        return False
    coordinates = ecology.get("coordinates")
    payloads = ecology.get("payloads")
    if not isinstance(coordinates, list) or not isinstance(payloads, dict):
        return False
    if [row.get("axis") for row in coordinates if isinstance(row, dict)] != [axis["id"] for axis in registry]:
        return False
    if len(coordinates) != len(registry) or set(payloads) != {axis["id"] for axis in registry}:
        return False
    for axis, coordinate in zip(registry, coordinates):
        if not isinstance(coordinate, dict) or set(coordinate) != {"axis", "level_token"}:
            return False
        level = _level_for_token(axis, coordinate["level_token"])
        if level is None or not _same_shape(payloads[axis["id"]], level["payload"]):
            return False
    return True


def semantic_well_formed(ecology: Mapping[str, Any], registry: Sequence[Mapping[str, Any]] = AXES) -> bool:
    if not syntax_well_formed(ecology, registry):
        return False
    for axis, coordinate in zip(registry, ecology["coordinates"]):
        level = _level_for_token(axis, coordinate["level_token"])
        if level is None:
            return False
        payload = ecology["payloads"][axis["id"]]
        if canonical(payload) != canonical(level["payload"]):
            return False
        try:
            if evaluate_probe(axis["id"], payload) is not level["expected_probe"]:
                return False
        except (KeyError, TypeError, ValueError, IndexError):
            return False
    return True


def build_behavioral_specification(
    ecology: Mapping[str, Any], registry: Sequence[Mapping[str, Any]] = AXES
) -> Dict[str, Any]:
    """Map a valid external ecology to a finite input/response contract."""
    if not semantic_well_formed(ecology, registry):
        raise ValueError("ecology is not semantically well formed")
    targets = []
    for axis in registry:
        targets.append(
            {
                "probe": axis["probe"],
                "required_response": int(evaluate_probe(axis["id"], ecology["payloads"][axis["id"]])),
            }
        )
    return {
        "schema": "ExternalBehavioralSpecificationV1",
        "input_carrier": [axis["probe"] for axis in registry],
        "response_carrier": [0, 1],
        "required_relation": targets,
        "score_rule": "exact_fraction_of_registered_probe_responses",
        "resource_terms": {
            "verification": deepcopy(ecology["payloads"]["verification_availability_cost"]),
            "memory": deepcopy(ecology["payloads"]["memory_price"]),
            "compute": deepcopy(ecology["payloads"]["compute_price"]),
            "communication": deepcopy(ecology["payloads"]["communication_price"]),
            "energy": deepcopy(ecology["payloads"]["energy_price"]),
            "developmental_horizon": deepcopy(ecology["payloads"]["developmental_horizon"]),
        },
    }


def behavioral_specification_well_formed(specification: Mapping[str, Any]) -> bool:
    expected_keys = {
        "schema",
        "input_carrier",
        "response_carrier",
        "required_relation",
        "score_rule",
        "resource_terms",
    }
    if set(specification) != expected_keys:
        return False
    if specification.get("schema") != "ExternalBehavioralSpecificationV1":
        return False
    if specification.get("input_carrier") != list(PROBE_IDS) or specification.get("response_carrier") != [0, 1]:
        return False
    relation = specification.get("required_relation")
    if not isinstance(relation, list) or len(relation) != len(PROBE_IDS):
        return False
    for probe, row in zip(PROBE_IDS, relation):
        if not isinstance(row, dict) or set(row) != {"probe", "required_response"}:
            return False
        if row["probe"] != probe or type(row["required_response"]) is not int or row["required_response"] not in (0, 1):
            return False
    if specification.get("score_rule") != "exact_fraction_of_registered_probe_responses":
        return False
    resources = specification.get("resource_terms")
    return isinstance(resources, dict) and set(resources) == {
        "verification",
        "memory",
        "compute",
        "communication",
        "energy",
        "developmental_horizon",
    }


def score_behavior(specification: Mapping[str, Any], responses: Mapping[str, int]) -> Dict[str, Any]:
    if not behavioral_specification_well_formed(specification):
        raise ValueError("behavioral specification is not well formed")
    expected = {row["probe"]: row["required_response"] for row in specification["required_relation"]}
    if set(responses) != set(expected) or any(type(value) is not int or value not in (0, 1) for value in responses.values()):
        raise ValueError("responses must assign one binary response to every registered probe")
    correct = sum(responses[probe] == target for probe, target in expected.items())
    total = len(expected)
    return {
        "correct": correct,
        "total": total,
        "exact_score": f"{correct}/{total}",
        "accepted": correct == total,
    }


def iter_family_coordinates(registry: Sequence[Mapping[str, Any]] = AXES) -> Iterator[Tuple[int, ...]]:
    """Systematic full product iterator; materialization is deliberately separate."""
    sizes = tuple(len(axis["levels"]) for axis in registry)
    yield from itertools.product(*(range(size) for size in sizes))


def _recursive_product_count(sizes: Sequence[int]) -> int:
    if not sizes:
        return 1
    return sizes[0] * _recursive_product_count(sizes[1:])


def mixed_radix_code(indices: Sequence[int], sizes: Sequence[int]) -> int:
    if len(indices) != len(sizes):
        raise ValueError("rank arity mismatch")
    code = 0
    for index, size in zip(indices, sizes):
        if type(size) is not int or size <= 0:
            raise ValueError("radix must be a positive exact integer")
        if type(index) is not int or index < 0 or index >= size:
            raise ValueError("rank digit out of carrier")
        code = code * size + index
    return code


def family_census(registry: Sequence[Mapping[str, Any]] = AXES) -> Dict[str, Any]:
    sizes = tuple(len(axis["levels"]) for axis in registry)
    arithmetic = math.prod(sizes)
    recursive = _recursive_product_count(sizes)
    count = 0
    codes = set()
    for indices in iter_family_coordinates(registry):
        count += 1
        codes.add(mixed_radix_code(indices, sizes))
    return {
        "carrier_sizes": list(sizes),
        "arithmetic_product": arithmetic,
        "recursive_product": recursive,
        "iterator_count": count,
        "unique_mixed_radix_codes": len(codes),
        "complete_integer_interval": codes == set(range(arithmetic)),
    }


def matched_twins(registry: Sequence[Mapping[str, Any]] = AXES) -> List[Dict[str, Any]]:
    baseline_indices = [0] * len(registry)
    negative = ecology_from_indices(baseline_indices, registry)
    negative_spec = build_behavioral_specification(negative, registry)
    negative_targets = {row["probe"]: row["required_response"] for row in negative_spec["required_relation"]}
    rows = []
    for position, axis in enumerate(registry):
        positive_indices = list(baseline_indices)
        positive_indices[position] = 1
        positive = ecology_from_indices(positive_indices, registry)
        positive_spec = build_behavioral_specification(positive, registry)
        positive_targets = {row["probe"]: row["required_response"] for row in positive_spec["required_relation"]}
        coordinate_differences = [
            left["axis"]
            for left, right in zip(negative["coordinates"], positive["coordinates"])
            if left != right
        ]
        payload_differences = [axis_id for axis_id in AXIS_IDS if negative["payloads"][axis_id] != positive["payloads"][axis_id]]
        target_differences = [probe for probe in PROBE_IDS if negative_targets[probe] != positive_targets[probe]]
        rows.append(
            {
                "axis": axis["id"],
                "probe": axis["probe"],
                "negative_ecology_sha256": sha256(negative),
                "positive_ecology_sha256": sha256(positive),
                "coordinate_differences": coordinate_differences,
                "payload_differences": payload_differences,
                "target_differences": target_differences,
                "negative_probe_value": negative_targets[axis["probe"]],
                "positive_probe_value": positive_targets[axis["probe"]],
                "same_input_carrier": negative_spec["input_carrier"] == positive_spec["input_carrier"],
                "same_response_carrier": negative_spec["response_carrier"] == positive_spec["response_carrier"],
                "same_score_rule": negative_spec["score_rule"] == positive_spec["score_rule"],
                "isolated": coordinate_differences == [axis["id"]]
                and payload_differences == [axis["id"]]
                and target_differences == [axis["probe"]]
                and negative_targets[axis["probe"]] == 0
                and positive_targets[axis["probe"]] == 1,
            }
        )
    return rows


def remint_registry(registry: Sequence[Mapping[str, Any]] = AXES) -> Tuple[Dict[str, Any], ...]:
    reminted = deepcopy(tuple(registry))
    for axis_number, axis in enumerate(reminted):
        for level_number, level in enumerate(axis["levels"]):
            level["token"] = f"opaque_{(axis_number * 7 + level_number * 19 + 11) % 101:03d}_{axis_number:02d}_{level_number}"
    return tuple(reminted)


def erase_tokens(ecology: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "schema": ecology["schema"],
        "coordinate_axes": [row["axis"] for row in ecology["coordinates"]],
        "payloads": deepcopy(ecology["payloads"]),
    }


def remint_census() -> Dict[str, Any]:
    reminted = remint_registry()
    original_tokens = {level["token"] for axis in AXES for level in axis["levels"]}
    reminted_tokens = {level["token"] for axis in reminted for level in axis["levels"]}
    witnesses = []
    witness_indices = (
        tuple(0 for _ in AXES),
        tuple(1 for _ in AXES),
        tuple(index % 2 for index in range(len(AXES))),
    )
    for indices in witness_indices:
        original = ecology_from_indices(indices, AXES)
        remint = ecology_from_indices(indices, reminted)
        original_spec = build_behavioral_specification(original, AXES)
        # Semantic validation and specification generation use the reminted
        # incidence relation; probes and scoring remain token-blind.
        if not semantic_well_formed(remint, reminted):
            raise RuntimeError("reminted ecology failed its registered semantics")
        remint_spec = build_behavioral_specification(remint, reminted)
        responses = {row["probe"]: row["required_response"] for row in original_spec["required_relation"]}
        witnesses.append(
            {
                "indices": list(indices),
                "token_erased_ecology_equal": erase_tokens(original) == erase_tokens(remint),
                "behavioral_specification_equal": original_spec == remint_spec,
                "score_equal": score_behavior(original_spec, responses) == score_behavior(remint_spec, responses),
            }
        )
    original_twins = matched_twins(AXES)
    # Twin semantics do not depend on token spelling; compare the invariant fields.
    reminted_twins = matched_twins(reminted)
    invariant_keys = (
        "axis",
        "probe",
        "coordinate_differences",
        "payload_differences",
        "target_differences",
        "negative_probe_value",
        "positive_probe_value",
        "same_input_carrier",
        "same_response_carrier",
        "same_score_rule",
        "isolated",
    )
    return {
        "original_token_count": len(original_tokens),
        "reminted_token_count": len(reminted_tokens),
        "token_sets_disjoint": original_tokens.isdisjoint(reminted_tokens),
        "remint_bijective": len(reminted_tokens) == len(original_tokens),
        "carrier_sizes_preserved": [len(axis["levels"]) for axis in AXES] == [len(axis["levels"]) for axis in reminted],
        "witnesses": witnesses,
        "twin_invariants_preserved": all(
            all(left[key] == right[key] for key in invariant_keys)
            for left, right in zip(original_twins, reminted_twins)
        ),
    }


def _normalized_text(value: Any) -> str:
    text = json.dumps(value, sort_keys=True).lower()
    return " ".join("".join(character if character.isalnum() else " " for character in text).split())


def architecture_neutrality_audit() -> Dict[str, Any]:
    baseline = ecology_from_indices([0] * len(AXES))
    specification = build_behavioral_specification(baseline)
    operational = {"axis_registry": AXES, "generated_ecology": baseline, "behavioral_specification": specification}
    normalized = _normalized_text(operational)
    phrase_hits = [phrase for phrase in KNOWN_FAMILY_PHRASES if phrase in normalized]
    generator_parameters = list(inspect.signature(ecology_from_indices).parameters)
    specification_parameters = list(inspect.signature(build_behavioral_specification).parameters)
    score_parameters = list(inspect.signature(score_behavior).parameters)
    forbidden_parameter_fragments = ("architecture", "implementation", "family", "model_class", "algorithm")
    all_parameters = generator_parameters + specification_parameters + score_parameters
    parameter_hits = [name for name in all_parameters if any(fragment in name.lower() for fragment in forbidden_parameter_fragments)]
    semantic_rows = [
        {
            "axis": axis_id,
            "external_semantics_rationale": EXTERNAL_SEMANTICS_RATIONALES.get(axis_id, ""),
            "probe_uses_only_axis_payload": True,
        }
        for axis_id in AXIS_IDS
    ]
    return {
        "known_family_phrase_hits_in_operational_contract": phrase_hits,
        "forbidden_parameter_hits": parameter_hits,
        "generator_parameters": generator_parameters,
        "specification_parameters": specification_parameters,
        "score_parameters": score_parameters,
        "external_semantics_audit": semantic_rows,
        "passes": not phrase_hits
        and not parameter_hits
        and set(EXTERNAL_SEMANTICS_RATIONALES) == set(AXIS_IDS)
        and all(row["external_semantics_rationale"] for row in semantic_rows),
    }


def syntax_semantics_control() -> Dict[str, Any]:
    valid = ecology_from_indices([0] * len(AXES))
    hostile = deepcopy(valid)
    hostile["payloads"]["observability"]["states"][1] = 2
    return {
        "valid_syntax": syntax_well_formed(valid),
        "valid_semantics": semantic_well_formed(valid),
        "hostile_syntax": syntax_well_formed(hostile),
        "hostile_semantics": semantic_well_formed(hostile),
        "hostile_reason": "registered token claims the original two-state payload but the same-shaped payload remints one state without updating the partition",
    }


def registry_document() -> Dict[str, Any]:
    return {
        "schema": "GMI833EcologyAxisRegistryV1",
        "issue": ISSUE,
        "parent_issue": PARENT_ISSUE,
        "source_pr": SOURCE_PR,
        "axis_count": len(AXES),
        "axes": list(AXES),
        "forbidden_operational_family_phrases": list(KNOWN_FAMILY_PHRASES),
        "claim_boundary": "A complete finite product over the registered carriers, not a sample or a complete universe of ecologies.",
    }


def build_ledger() -> Dict[str, Any]:
    validation = validate_registry()
    family = family_census()
    twins = matched_twins()
    remint = remint_census()
    syntax_control = syntax_semantics_control()
    neutrality = architecture_neutrality_audit()
    return {
        "schema": "GMI833EcologySpecificationGeneratorLedgerV1",
        "issue": ISSUE,
        "parent_issue": PARENT_ISSUE,
        "source_pr": SOURCE_PR,
        "freeze_commit": FREEZE_COMMIT,
        "frozen_main": FROZEN_MAIN,
        "theorems": [
            {
                "id": "G17_REGISTERED_PRODUCT_COMPLETENESS",
                "statement": "For finite carriers L_i, the iterator over their Cartesian product emits every registered coordinate tuple exactly once and has cardinality product_i |L_i|.",
                "proof_basis": "Induction on carrier count plus injectivity of mixed-radix rank on the bounded digit tuple.",
                "scope": "exactly the seventeen registered carriers",
            },
            {
                "id": "G17_EXTERNAL_BEHAVIORAL_SPECIFICATION",
                "statement": "Every semantically well-formed registered ecology maps deterministically to a finite external probe/response relation and exact score rule without an implementation-family argument.",
                "proof_basis": "Each registered payload has one total external probe; collecting the seventeen probe values defines the relation, and exact matching defines the score.",
                "scope": "registered semantics only",
            },
            {
                "id": "G17_MATCHED_TWIN_ISOLATION",
                "statement": "For every axis there is a negative/positive pair differing in one coordinate whose induced relation differs on exactly the corresponding probe.",
                "proof_basis": "Hold the sixteen other indices at zero and change only the selected index; registry nondegeneracy gives the single target flip.",
                "scope": "seventeen registered one-axis probes",
            },
            {
                "id": "G17_TOKEN_REMINT_INVARIANCE",
                "statement": "Every bijective remint of level tokens preserves token-erased semantics, behavioral targets, scores, cardinality, and twin isolation.",
                "proof_basis": "Tokens select levels but do not enter payload probes or scoring; a bijection commutes with selection and leaves carrier sizes fixed.",
                "scope": "bijective token remints preserving the registry incidence relation",
            },
            {
                "id": "G17_ARCHITECTURE_PRIOR_NONINTERFERENCE",
                "statement": "Generated ecologies and specifications are functions only of external registered coordinates, so implementation-family labels cannot affect generation or scoring.",
                "proof_basis": "The function domains expose no architecture/family argument and the operational registry contains no known-family phrase.",
                "scope": "the frozen vocabulary audit and public operational interfaces",
            },
        ],
        "axis_validation": validation,
        "product_census": family,
        "matched_twins": twins,
        "remint_census": remint,
        "syntax_semantics_control": syntax_control,
        "architecture_neutrality_audit": neutrality,
        "claim_boundary": {
            "proved": [
                "registered finite-product completeness and uniqueness",
                "seventeen nondegenerate semantic axis witnesses",
                "seventeen one-coordinate matched twins",
                "external behavioral-specification generation and exact scoring",
                "bijective opaque-token remint invariance",
                "absence of known-family inputs and phrases from operational generation/scoring",
            ],
            "not_claimed": [
                "sufficient ecology-space sampling",
                "unbiased sampling or quantified sampling uncertainty",
                "coverage of unregistered or infinite ecology universes",
                "empirical representativeness or real-world transfer",
                "recovery, ranking, or superiority of any implementation family",
            ],
        },
    }


def validate_package_contracts() -> Dict[str, Any]:
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text())
    reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_ECOLOGY_GENERATOR_V1.json").read_text())
    expected_artifacts = {
        "FREEZE_V1.md",
        "CORE.md",
        "ECOLOGY_GENERATOR_THEOREMS_V1.md",
        "ECOLOGY_AXIS_REGISTRY_V1.json",
        "SCIENTIFIC_LEDGER_V1.json",
        "RESULT_V1.json",
        "ecology_specification_generator_v1.py",
        "test_ecology_specification_generator_v1.py",
        "ISSUE_833_RECONCILIATION_ECOLOGY_GENERATOR_V1.json",
    }
    if manifest.get("schema") != "GMI833EcologySpecificationGeneratorManifestV1":
        raise ValueError("wrong manifest schema")
    if manifest.get("issue") != ISSUE or manifest.get("source_pr") != SOURCE_PR:
        raise ValueError("manifest issue/PR mismatch")
    if manifest.get("freeze_commit") != FREEZE_COMMIT or manifest.get("frozen_main") != FROZEN_MAIN:
        raise ValueError("manifest freeze mismatch")
    if set(manifest.get("artifacts", [])) != expected_artifacts:
        raise ValueError("manifest artifact inventory mismatch")
    missing = sorted(name for name in expected_artifacts if not (HERE / name).is_file())
    if missing:
        raise ValueError(f"missing artifacts: {missing}")
    if manifest.get("target_rows") != len(TARGET_ROWS) or manifest.get("axis_count") != len(AXES):
        raise ValueError("manifest count mismatch")
    if reconciliation.get("schema") != "GMI_ISSUE_RECONCILIATION_V2":
        raise ValueError("wrong reconciliation schema")
    if reconciliation.get("issue") != PARENT_ISSUE or reconciliation.get("source_issue") != ISSUE or reconciliation.get("source_pr") != SOURCE_PR:
        raise ValueError("reconciliation issue/PR mismatch")
    replacements = reconciliation.get("replacements", [])
    if len(replacements) != len(TARGET_ROWS):
        raise ValueError("reconciliation row count mismatch")
    if {row.get("old") for row in replacements} != {f"- [ ] {row}" for row in TARGET_ROWS}:
        raise ValueError("reconciliation does not target exactly the frozen rows")
    if any("Sample enough ecology space" in row.get("old", "") or "Quantify ecology sampling" in row.get("old", "") for row in replacements):
        raise ValueError("sampling rows are out of scope")
    return {"manifest_rows": manifest["target_rows"], "reconciliation_rows": len(replacements), "artifacts": len(expected_artifacts)}


def run() -> Dict[str, Any]:
    registry = validate_registry()
    family = family_census()
    twins = matched_twins()
    remint = remint_census()
    syntax_control = syntax_semantics_control()
    neutrality = architecture_neutrality_audit()
    ledger = build_ledger()
    package = validate_package_contracts()
    checks = {
        "registry_has_exactly_seventeen_unique_binary_axes": registry["axis_count"] == 17
        and registry["axis_ids_unique"]
        and registry["probe_ids_unique"]
        and registry["all_level_tokens_globally_unique"],
        "every_axis_has_nondegenerate_semantic_probe": registry["all_axes_binary_and_nondegenerate"],
        "syntax_is_distinct_from_semantic_well_formedness": syntax_control
        == {
            "valid_syntax": True,
            "valid_semantics": True,
            "hostile_syntax": True,
            "hostile_semantics": False,
            "hostile_reason": "registered token claims the original two-state payload but the same-shaped payload remints one state without updating the partition",
        },
        "registered_product_is_complete_unique_and_independently_counted": family["arithmetic_product"]
        == family["recursive_product"]
        == family["iterator_count"]
        == family["unique_mixed_radix_codes"]
        == 2**17
        and family["complete_integer_interval"],
        "all_seventeen_matched_twins_are_one_coordinate_isolated": len(twins) == 17 and all(row["isolated"] for row in twins),
        "matched_twins_preserve_carriers_and_scoring": all(
            row["same_input_carrier"] and row["same_response_carrier"] and row["same_score_rule"] for row in twins
        ),
        "opaque_token_remint_preserves_semantics_specs_scores_and_twins": remint["token_sets_disjoint"]
        and remint["remint_bijective"]
        and remint["carrier_sizes_preserved"]
        and remint["twin_invariants_preserved"]
        and all(
            row["token_erased_ecology_equal"] and row["behavioral_specification_equal"] and row["score_equal"]
            for row in remint["witnesses"]
        ),
        "generation_and_scoring_are_architecture_neutral_at_registered_scope": neutrality["passes"],
        "registry_file_is_canonical": canonical(registry_document()) == (HERE / "ECOLOGY_AXIS_REGISTRY_V1.json").read_bytes(),
        "ledger_file_is_canonical": canonical(ledger) == (HERE / "SCIENTIFIC_LEDGER_V1.json").read_bytes(),
        "package_and_exact_twenty_one_row_reconciliation_are_valid": package["manifest_rows"] == 21
        and package["reconciliation_rows"] == 21,
    }
    status = "GREEN" if all(checks.values()) else "RED"
    return {
        "schema": "GMI833EcologySpecificationGeneratorResultV1",
        "issue": ISSUE,
        "parent_issue": PARENT_ISSUE,
        "source_pr": SOURCE_PR,
        "freeze_commit": FREEZE_COMMIT,
        "frozen_main": FROZEN_MAIN,
        "status": status,
        "terminal": TERMINAL if status == "GREEN" else None,
        "checks": checks,
        "counts": {
            "target_rows": len(TARGET_ROWS),
            "axes": len(AXES),
            "levels": sum(len(axis["levels"]) for axis in AXES),
            "registered_product_cardinality": family["iterator_count"],
            "matched_twins": len(twins),
            "remint_witnesses": len(remint["witnesses"]),
        },
        "registry_sha256": sha256(registry_document()),
        "ledger_sha256": sha256(ledger),
        "package_contracts": package,
        "claim_boundary": "Exact architecture-neutral generation, product completeness, semantic variation, matched twins, and remint invariance for seventeen registered finite carriers. No sampling-adequacy, sampling-bias, unregistered-universe, empirical-transfer, or architecture-recovery claim.",
    }


if __name__ == "__main__":
    print(canonical(run()).decode(), end="")
