"""Executable structural checks for #602 A2 EcologyContractV2.

The checker establishes registration and finite remint/isomorphism properties only.
It does not establish a morphology phase law, reachability, or empirical validity.
"""

from pathlib import Path
import copy
import json
import re


def _here():
    try:
        return Path(__file__).resolve().parent
    except NameError:
        for cand in [Path.cwd() / "research/gmi-ecology-contract-v2", Path.cwd()]:
            if (cand / "ECOLOGY_CONTRACT_V2.json").exists():
                return cand
        return Path.cwd()


HERE = _here()
CONTRACT = HERE / "ECOLOGY_CONTRACT_V2.json"

EXPECTED_COORDINATES = (
    "adaptive_agents",
    "observation_structure",
    "action_intervention_structure",
    "feedback_verifier_structure",
    "task_distribution_horizon",
    "drift_regime_change",
    "recurrence_reuse",
    "noise_partial_observability",
    "compositional_symmetry_relational_structure",
    "social_topology",
    "embodiment_sensor_actuator",
    "resource_prices_hard_budgets",
    "verification_latency_cost_false_adoption",
    "information_acquisition_cost",
    "protected_train_development_heldout_splits",
    "ecology_equivalence_remint",
)

REQUIRED_META = {
    "schema", "issue", "scope", "assumptions", "evidence_class",
    "strongest_parent", "falsifier", "claim_ceiling", "ecology_object",
    "required_coordinates", "anti_leakage", "terminal",
}

FORBIDDEN_VISIBLE_DEFAULT = {
    "ecology_id", "remint_id", "protected_split_membership",
    "protected_outcome", "architecture_or_family_label",
}


def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def claim_rank(value):
    m = re.fullmatch(r"G(\d+)", value if isinstance(value, str) else "")
    if not m:
        raise ValueError("invalid claim ceiling %r" % (value,))
    return int(m.group(1))


def validate_contract(data=None):
    if data is None:
        data = load_contract()
    errors = []
    if not isinstance(data, dict):
        return ["contract must be an object"]
    missing = REQUIRED_META - set(data)
    if missing:
        errors.append("missing metadata %r" % sorted(missing))
        return errors
    if data.get("schema") != "GMIEcologyContractV2":
        errors.append("wrong schema")
    if data.get("issue") != 602:
        errors.append("issue must be 602")
    try:
        if claim_rank(data.get("claim_ceiling")) != 1:
            errors.append("A2 registration ceiling must be G1")
    except ValueError as exc:
        errors.append(str(exc))
    assumptions = data.get("assumptions")
    if not isinstance(assumptions, list) or not assumptions:
        errors.append("assumptions must be nonempty")
    for field in ("scope", "evidence_class", "strongest_parent", "falsifier", "ecology_object", "terminal"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append("%s must be nonempty text" % field)
    coords = data.get("required_coordinates")
    if not isinstance(coords, dict):
        errors.append("required_coordinates must be an object")
    else:
        actual = set(coords)
        expected = set(EXPECTED_COORDINATES)
        if actual != expected:
            errors.append(
                "coordinate set mismatch: missing=%r extra=%r"
                % (sorted(expected - actual), sorted(actual - expected))
            )
        for name, row in coords.items():
            if not isinstance(row, dict):
                errors.append("%s must be an object" % name)
                continue
            required = row.get("required")
            if not isinstance(required, list) or not required or len(required) != len(set(required)):
                errors.append("%s required fields must be a nonempty unique list" % name)
            if not isinstance(row.get("rule"), str) or not row["rule"].strip():
                errors.append("%s must state a rule" % name)
    anti = data.get("anti_leakage")
    if not isinstance(anti, dict):
        errors.append("anti_leakage must be an object")
    else:
        visible = set(anti.get("forbidden_agent_visible_fields_by_default", []))
        if visible != FORBIDDEN_VISIBLE_DEFAULT:
            errors.append("anti-leakage forbidden-field set mismatch")
        if not isinstance(anti.get("exception_rule"), str) or not anti["exception_rule"].strip():
            errors.append("anti-leakage exception rule missing")
    return errors


def validate_instance(instance):
    """Validate a compact finite ecology instance used by executable witnesses."""
    errors = []
    required = {
        "agents", "focal_agent", "states", "observations", "actions",
        "interventions", "transition_rows", "feedback", "verifier", "tasks",
        "horizon", "drift", "recurrence", "structure", "social_edges",
        "embodiment", "resource_coordinates", "hard_budget", "price_vector",
        "information_acquisition", "split", "agent_visible_fields",
    }
    missing = required - set(instance)
    if missing:
        return ["instance missing %r" % sorted(missing)]
    agent_ids = [a.get("id") for a in instance["agents"] if isinstance(a, dict)]
    if len(agent_ids) != len(instance["agents"]) or len(agent_ids) != len(set(agent_ids)):
        errors.append("agent IDs must be unique")
    if instance["focal_agent"] not in set(agent_ids):
        errors.append("focal agent must be registered")
    for agent in instance["agents"]:
        if agent.get("adaptive") and not agent.get("adaptation_contract"):
            errors.append("adaptive agent %s lacks adaptation_contract" % agent.get("id"))
    for edge in instance["social_edges"]:
        if len(edge) != 2 or edge[0] not in agent_ids or edge[1] not in agent_ids:
            errors.append("social edge references unknown agent")
    coords = instance["resource_coordinates"]
    if not isinstance(coords, list) or not coords or len(coords) != len(set(coords)):
        errors.append("resource coordinates must be a nonempty unique list")
    for field in ("hard_budget", "price_vector"):
        vector = instance[field]
        if set(vector) != set(coords):
            errors.append("%s coordinates mismatch" % field)
        for value in vector.values():
            if not isinstance(value, (int, float)) or value < 0:
                errors.append("%s must be nonnegative" % field)
    verifier = instance["verifier"]
    for field in ("latency", "resource_cost", "false_adoption_loss", "false_rejection_loss"):
        if field not in verifier or not isinstance(verifier[field], (int, float)) or verifier[field] < 0:
            errors.append("verifier %s must be a nonnegative number" % field)
    acquisition = instance["information_acquisition"]
    if not isinstance(acquisition, dict) or "channels" not in acquisition or "query_budget" not in acquisition:
        errors.append("information acquisition contract incomplete")
    split = instance["split"]
    split_sets = []
    for field in ("train", "development", "heldout"):
        values = split.get(field)
        if not isinstance(values, list):
            errors.append("split %s must be a list" % field)
            values = []
        split_sets.append(set(values))
    if any(split_sets[i] & split_sets[j] for i in range(3) for j in range(i + 1, 3)):
        errors.append("train/development/heldout splits must be disjoint")
    leaked = FORBIDDEN_VISIBLE_DEFAULT & set(instance["agent_visible_fields"])
    if leaked:
        errors.append("protected fields visible to agent: %r" % sorted(leaked))
    return errors


def componentwise_feasible(resource_vector, hard_budget):
    if set(resource_vector) != set(hard_budget):
        raise ValueError("resource and budget coordinates must match")
    return all(resource_vector[k] <= hard_budget[k] for k in resource_vector)


def scalar_price(resource_vector, price_vector):
    if set(resource_vector) != set(price_vector):
        raise ValueError("resource and price coordinates must match")
    if any(v < 0 for v in price_vector.values()):
        raise ValueError("prices must be nonnegative")
    return sum(resource_vector[k] * price_vector[k] for k in resource_vector)


def _replace_tokens(value, token_map):
    if isinstance(value, str):
        return token_map.get(value, value)
    if isinstance(value, list):
        return [_replace_tokens(v, token_map) for v in value]
    if isinstance(value, dict):
        return {
            token_map.get(k, k): _replace_tokens(v, token_map)
            for k, v in value.items()
        }
    return value


def validate_bijection(token_map):
    if not isinstance(token_map, dict):
        return False
    return len(token_map) == len(set(token_map.values()))


def remint(instance, token_map):
    if not validate_bijection(token_map):
        raise ValueError("remint map must be bijective on its declared nominal tokens")
    return _replace_tokens(copy.deepcopy(instance), token_map)


def remint_equivalent(left, right, token_map):
    """Finite declared-isomorphism check: applying the bijection must give exact equality."""
    if not validate_bijection(token_map):
        return False
    return remint(left, token_map) == right


def inverse_map(token_map):
    if not validate_bijection(token_map):
        raise ValueError("map is not bijective")
    return {v: k for k, v in token_map.items()}


def compose_maps(first, second):
    """Return second∘first on the declared domain, retaining unchanged tokens."""
    if not validate_bijection(first) or not validate_bijection(second):
        raise ValueError("maps must be bijective")
    result = {k: second.get(v, v) for k, v in first.items()}
    if len(result) != len(set(result.values())):
        raise ValueError("composition is not bijective on declared domain")
    return result


def witness_instance():
    """Small finite ecology covering all A2 coordinate families."""
    return {
        "agents": [
            {"id": "learner", "adaptive": True, "adaptation_contract": "history_to_policy_state"},
            {"id": "peer", "adaptive": True, "adaptation_contract": "history_to_policy_state"},
        ],
        "focal_agent": "learner",
        "states": ["cold", "hot"],
        "observations": {
            "learner": {"alphabet": ["blue", "red"], "kernel": [["cold", "blue", 1.0], ["hot", "red", 1.0]], "timing": "after_transition"},
            "peer": {"alphabet": ["blue", "red"], "kernel": [["cold", "blue", 1.0], ["hot", "red", 1.0]], "timing": "after_transition"},
        },
        "actions": {"learner": ["stay", "toggle"], "peer": ["stay", "toggle"]},
        "interventions": [{"id": "force_cold", "target": "state", "value": "cold", "preserves": ["verifier", "costs"]}],
        "transition_rows": [
            ["cold", "stay", "stay", "cold", 1.0],
            ["cold", "toggle", "stay", "hot", 1.0],
            ["hot", "stay", "stay", "hot", 1.0],
            ["hot", "toggle", "stay", "cold", 1.0]
        ],
        "feedback": {"channels": ["reward", "counterexample"], "timing": "post_action"},
        "verifier": {"rule": "target_state_match", "authority": "external", "latency": 1, "resource_cost": 2, "false_adoption_loss": 7, "false_rejection_loss": 1},
        "tasks": [{"id": "warm_task", "target": "hot"}, {"id": "cool_task", "target": "cold"}, {"id": "held_task", "target": "hot"}],
        "horizon": {"episode": 4, "evaluation": 12},
        "drift": {"regimes": ["stable"], "schedule": [[0, "stable"]], "mutable_components": []},
        "recurrence": {"identity_rule": "same_target", "reuse_count": 3, "reuse_horizon": 12},
        "structure": {"composition_grammar": "two_step", "symmetry_group": ["identity"], "relation_schema": "agent_state_bipartite"},
        "social_edges": [["learner", "peer"], ["peer", "learner"]],
        "embodiment": {"sensor_ports": ["thermometer"], "sensor_latency": 1, "actuator_ports": ["switch"], "actuator_latency": 1, "workspace": "single_cell"},
        "resource_coordinates": ["exec", "memory", "communication"],
        "hard_budget": {"exec": 8, "memory": 4, "communication": 2},
        "price_vector": {"exec": 1, "memory": 2, "communication": 3},
        "information_acquisition": {"channels": {"active_probe": {"cost": {"exec": 1, "memory": 0, "communication": 0}, "latency": 1}}, "query_budget": 2},
        "split": {"train": ["warm_task"], "development": ["cool_task"], "heldout": ["held_task"], "freeze_point": "before_heldout"},
        "agent_visible_fields": ["observations", "actions", "feedback"]
    }


def run():
    contract_errors = validate_contract()
    fixture = witness_instance()
    instance_errors = validate_instance(fixture)
    if contract_errors or instance_errors:
        raise ValueError("; ".join(contract_errors + instance_errors))
    return {
        "status": "PASS",
        "a2_coordinates": len(EXPECTED_COORDINATES),
        "claim_ceiling": "G1",
        "adaptive_agents": sum(1 for a in fixture["agents"] if a["adaptive"]),
        "protected_fields_hidden": True,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
