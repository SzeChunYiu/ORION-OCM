"""Exact finite witnesses and scope guards for #602 F2 capability ceilings."""

from fractions import Fraction
from itertools import product
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
REGISTRY_PATH = HERE / "F2_CEILINGS_V1.json"

EXPECTED_IDS = (
    "F2_STATE_CAPACITY_MEMORY",
    "F2_OBSERVATION_QUOTIENT",
    "F2_COMMUNICATION_BANDWIDTH",
    "F2_PRECISION_BOUNDARY",
    "F2_UPDATE_CHANNEL_PLASTICITY",
    "F2_PROTECTED_RANK_FRONTIER",
)
REQUIRED_ROW_FIELDS = {
    "id", "box", "quantity", "theorem", "bound", "strongest_parent",
    "assumptions", "negative_twin", "falsifier",
}


def load_registry():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def validate_registry(data=None):
    data = load_registry() if data is None else data
    errors = []
    required_top = {
        "schema", "issue", "section", "scope", "assumptions", "evidence_class",
        "claim_ceiling", "strongest_parents", "falsifier", "ceilings", "terminal",
    }
    missing = required_top - set(data)
    if missing:
        errors.append("missing top-level fields: %s" % sorted(missing))
        return errors

    if data["schema"] != "GMICapabilityCeilingsV1":
        errors.append("schema mismatch")
    if data["issue"] != 602:
        errors.append("issue must be 602")
    if data["claim_ceiling"] != "G2":
        errors.append("claim ceiling must be G2")
    if "P1" not in data["evidence_class"] or "P2" not in data["evidence_class"]:
        errors.append("evidence class must register P1 and P2")
    if not isinstance(data["assumptions"], list) or not data["assumptions"]:
        errors.append("top-level assumptions must be non-empty")
    if len(data["strongest_parents"]) < 6:
        errors.append("all six strongest-parent families must be registered")
    if not str(data["falsifier"]).strip():
        errors.append("top-level falsifier must be non-empty")
    if data["terminal"] != "F2_TRANCHE2_SIX_EXACT_CEILINGS_REGISTERED_AT_G2":
        errors.append("terminal mismatch")

    rows = data["ceilings"]
    ids = [row.get("id") for row in rows]
    if tuple(ids) != EXPECTED_IDS:
        errors.append("ceiling id/order mismatch: %r" % ids)
    if len(set(ids)) != len(ids):
        errors.append("duplicate ceiling id")
    for i, row in enumerate(rows):
        missing_row = REQUIRED_ROW_FIELDS - set(row)
        if missing_row:
            errors.append("row %d missing fields: %s" % (i, sorted(missing_row)))
            continue
        if not row["assumptions"]:
            errors.append("%s has empty assumptions" % row["id"])
        for field in ("theorem", "bound", "strongest_parent", "negative_twin", "falsifier"):
            if not str(row[field]).strip():
                errors.append("%s has empty %s" % (row["id"], field))
    return errors


def _positive_int(name, value):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("%s must be a positive integer" % name)


def _nonnegative_int(name, value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("%s must be a nonnegative integer" % name)


def state_capacity_allows(distinctions, states):
    """Necessary/tight delayed-label condition S >= K."""
    _positive_int("distinctions", distinctions)
    _positive_int("states", states)
    return states >= distinctions


def validate_state_scope(instance):
    errors = []
    if instance.get("external_memory", False):
        errors.append("external memory invalidates the state-only ceiling scope")
    if instance.get("hidden_side_channel", False):
        errors.append("hidden side channel invalidates the state-only ceiling scope")
    if instance.get("future_observation_reseparates", False):
        errors.append("future observation re-separates histories; recompute the full quotient")
    if not instance.get("zero_error", False):
        errors.append("theorem is zero-error only")
    return errors


def exhaustive_delayed_label_exists(distinctions, states, max_candidates=2_000_000):
    """Enumerate every encoder K->S and decoder S->K for a tiny delayed-label task."""
    _positive_int("distinctions", distinctions)
    _positive_int("states", states)
    candidates = (states ** distinctions) * (distinctions ** states)
    if candidates > max_candidates:
        raise ValueError("enumeration cap exceeded")
    for encoder in product(range(states), repeat=distinctions):
        for decoder in product(range(distinctions), repeat=states):
            if all(decoder[encoder[label]] == label for label in range(distinctions)):
                return True
    return False


def _same_keys(a, b):
    return set(a) == set(b)


def observation_task_realisable(observation_of, required_action):
    """Exact deterministic fiber criterion."""
    if not observation_of or not required_action:
        raise ValueError("observation and action maps must be non-empty")
    if not _same_keys(observation_of, required_action):
        raise ValueError("observation and required-action domains must match")
    action_by_observation = {}
    for latent, obs in observation_of.items():
        action = required_action[latent]
        if obs in action_by_observation and action_by_observation[obs] != action:
            return False
        action_by_observation[obs] = action
    return True


def validate_observation_scope(instance):
    errors = []
    if instance.get("later_probe", False):
        errors.append("later probe refines the information channel; quotient is incomplete")
    if instance.get("later_intervention_information", False):
        errors.append("later intervention carries information; quotient is incomplete")
    if instance.get("side_information", False):
        errors.append("side information must be included in the observation quotient")
    if not instance.get("zero_error", False):
        errors.append("theorem is zero-error only")
    return errors


def exhaustive_observation_policy_exists(observation_of, required_action, max_candidates=2_000_000):
    if not observation_of or not required_action:
        raise ValueError("observation and action maps must be non-empty")
    if not _same_keys(observation_of, required_action):
        raise ValueError("observation and required-action domains must match")
    observations = tuple(sorted(set(observation_of.values()), key=repr))
    actions = tuple(sorted(set(required_action.values()), key=repr))
    candidates = len(actions) ** len(observations)
    if candidates > max_candidates:
        raise ValueError("enumeration cap exceeded")
    for outputs in product(actions, repeat=len(observations)):
        policy = dict(zip(observations, outputs))
        if all(policy[observation_of[x]] == required_action[x] for x in observation_of):
            return True
    return False


def transcript_capacity(bits):
    _nonnegative_int("bits", bits)
    return 1 << bits


def communication_allows(coordination_classes, bits):
    _positive_int("coordination_classes", coordination_classes)
    _nonnegative_int("bits", bits)
    return coordination_classes <= transcript_capacity(bits)


def minimum_fixed_bits(coordination_classes):
    _positive_int("coordination_classes", coordination_classes)
    bits = 0
    cap = 1
    while cap < coordination_classes:
        bits += 1
        cap <<= 1
    return bits


def validate_communication_scope(instance):
    errors = []
    if instance.get("receiver_side_information", False):
        errors.append("receiver side information can refine sender classes; theorem scope excludes it")
    if instance.get("correlated_shared_state", False):
        errors.append("correlated shared state is an unmetered information channel")
    if not instance.get("deterministic", False):
        errors.append("theorem is deterministic only")
    if not instance.get("noiseless", False):
        errors.append("theorem requires a noiseless registered channel")
    if not instance.get("fixed_length", False):
        errors.append("theorem meters fixed-length bits")
    if not instance.get("one_way", False):
        errors.append("theorem is one-way only")
    if not instance.get("zero_error", False):
        errors.append("theorem is zero-error only")
    return errors


def exhaustive_one_way_protocol_exists(coordination_classes, bits, max_candidates=2_000_000):
    """Enumerate all deterministic encoders/decoders for identity coordination."""
    _positive_int("coordination_classes", coordination_classes)
    _nonnegative_int("bits", bits)
    transcripts = transcript_capacity(bits)
    candidates = (transcripts ** coordination_classes) * (
        coordination_classes ** transcripts
    )
    if candidates > max_candidates:
        raise ValueError("enumeration cap exceeded")
    for encoder in product(range(transcripts), repeat=coordination_classes):
        for decoder in product(range(coordination_classes), repeat=transcripts):
            if all(decoder[encoder[c]] == c for c in range(coordination_classes)):
                return True
    return False


def precision_boundary_capacity(bits, ordered_probe_points):
    """Best-case number of threshold placements represented by a fixed B-bit code."""
    _nonnegative_int("bits", bits)
    _positive_int("ordered_probe_points", ordered_probe_points)
    return min(1 << bits, ordered_probe_points + 1)


def minimum_threshold_bits(ordered_probe_points):
    _positive_int("ordered_probe_points", ordered_probe_points)
    return minimum_fixed_bits(ordered_probe_points + 1)


def exhaustive_threshold_codebook_covers(ordered_probe_points, bits, max_candidates=2_000_000):
    """Enumerate every decoder from B-bit codes to N+1 threshold placements."""
    _positive_int("ordered_probe_points", ordered_probe_points)
    _nonnegative_int("bits", bits)
    placements = ordered_probe_points + 1
    codes = 1 << bits
    candidates = placements ** codes
    if candidates > max_candidates:
        raise ValueError("enumeration cap exceeded")
    required = set(range(placements))
    for decoder in product(range(placements), repeat=codes):
        if set(decoder) == required:
            return True
    return False


def validate_precision_scope(instance):
    errors = []
    if not instance.get("architecture_frozen", False):
        errors.append("architecture must be frozen for the precision ceiling")
    if not instance.get("codebook_frozen", False):
        errors.append("threshold decoder/codebook must be frozen across the target family")
    if instance.get("extra_precision_channel", False):
        errors.append("extra precision-bearing channel invalidates the registered bit ceiling")
    if instance.get("task_specific_decoder_rewrite", False):
        errors.append("task-specific decoder rewrite is an unmetered precision/design channel")
    if not instance.get("zero_error", False):
        errors.append("theorem is zero-error only")
    return errors


def update_transcript_capacity(symbols, steps):
    _positive_int("symbols", symbols)
    _nonnegative_int("steps", steps)
    return symbols ** steps


def update_channel_allows(target_states, symbols, steps):
    _positive_int("target_states", target_states)
    return target_states <= update_transcript_capacity(symbols, steps)


def minimum_update_steps(target_states, symbols):
    _positive_int("target_states", target_states)
    _positive_int("symbols", symbols)
    if target_states == 1:
        return 0
    if symbols == 1:
        raise ValueError("one update symbol cannot select multiple target states")
    steps = 0
    cap = 1
    while cap < target_states:
        steps += 1
        cap *= symbols
    return steps


def exhaustive_update_decoder_covers(target_states, symbols, steps, max_candidates=2_000_000):
    """Enumerate every deterministic transcript->target decoder for tiny cases."""
    _positive_int("target_states", target_states)
    transcript_count = update_transcript_capacity(symbols, steps)
    candidates = target_states ** transcript_count
    if candidates > max_candidates:
        raise ValueError("enumeration cap exceeded")
    required = set(range(target_states))
    for decoder in product(range(target_states), repeat=transcript_count):
        if set(decoder) == required:
            return True
    return False


def validate_update_scope(instance):
    errors = []
    if not instance.get("fixed_initial_state", False):
        errors.append("initial persistent state must be fixed")
    if instance.get("direct_write", False):
        errors.append("direct write bypasses the registered update channel")
    if instance.get("external_memory_mutation", False):
        errors.append("external memory mutation is an additional update channel")
    if instance.get("target_correlated_side_channel", False):
        errors.append("target-correlated side channel must be included in the update alphabet")
    if instance.get("architecture_growth", False):
        errors.append("architecture growth changes the mutable state space")
    if not instance.get("deterministic", False):
        errors.append("theorem is deterministic only")
    if not instance.get("zero_error", False):
        errors.append("theorem is zero-error only")
    return errors


def matrix_rank(matrix, columns=None):
    """Exact Gaussian-elimination rank over rationals."""
    if not matrix:
        if columns is None:
            return 0
        _nonnegative_int("columns", columns)
        return 0
    width = len(matrix[0])
    if width == 0:
        raise ValueError("matrix must have at least one column")
    if columns is not None and width != columns:
        raise ValueError("matrix column count mismatch")
    if any(len(row) != width for row in matrix):
        raise ValueError("matrix must be rectangular")
    a = [[Fraction(value) for value in row] for row in matrix]
    rows = len(a)
    rank = 0
    for col in range(width):
        pivot = next((r for r in range(rank, rows) if a[r][col] != 0), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        pivot_value = a[rank][col]
        a[rank] = [x / pivot_value for x in a[rank]]
        for r in range(rows):
            if r != rank and a[r][col] != 0:
                factor = a[r][col]
                a[r] = [x - factor * y for x, y in zip(a[r], a[rank])]
        rank += 1
        if rank == rows:
            break
    return rank


def protected_nullity(protected_map, parameter_dim):
    _positive_int("parameter_dim", parameter_dim)
    if protected_map and any(len(row) != parameter_dim for row in protected_map):
        raise ValueError("protected map width must equal parameter_dim")
    return parameter_dim - matrix_rank(protected_map, columns=parameter_dim)


def protected_frontier_allows(protected_map, parameter_dim, plastic_rank):
    _nonnegative_int("plastic_rank", plastic_rank)
    return plastic_rank <= protected_nullity(protected_map, parameter_dim)


def validate_protected_rank_scope(instance):
    errors = []
    if not instance.get("linear_protected_map", False):
        errors.append("exact theorem requires a linear protected-output map")
    if not instance.get("fixed_parameter_dim", False):
        errors.append("parameter dimension must be fixed")
    if instance.get("auxiliary_mutable_state", False):
        errors.append("auxiliary mutable state must be included in parameter dimension")
    if instance.get("architecture_growth", False):
        errors.append("architecture growth changes the registered dimension")
    if not instance.get("exact_retention", False):
        errors.append("theorem is for exact zero-forgetting retention")
    return errors


def run():
    registry_errors = validate_registry()
    if registry_errors:
        return {"status": "FAIL", "errors": registry_errors}

    observation_bad = {"x0": "z0", "x1": "z0", "x2": "z1"}
    actions_bad = {"x0": "a0", "x1": "a1", "x2": "a0"}
    observation_good = dict(observation_bad)
    actions_good = {"x0": "a0", "x1": "a0", "x2": "a1"}
    protected = [[1, 0, 0], [0, 1, 0]]

    checks = {
        "state_bound_negative": not state_capacity_allows(3, 2),
        "state_exhaustive_negative": not exhaustive_delayed_label_exists(3, 2),
        "state_tight_positive": exhaustive_delayed_label_exists(3, 3),
        "observation_fiber_negative": not observation_task_realisable(
            observation_bad, actions_bad
        ),
        "observation_exhaustive_negative": not exhaustive_observation_policy_exists(
            observation_bad, actions_bad
        ),
        "observation_twin_positive": exhaustive_observation_policy_exists(
            observation_good, actions_good
        ),
        "communication_bound_negative": not communication_allows(5, 2),
        "communication_exhaustive_negative": not exhaustive_one_way_protocol_exists(3, 1),
        "communication_tight_positive": exhaustive_one_way_protocol_exists(4, 2),
        "communication_bits_exact": minimum_fixed_bits(5) == 3,
        "precision_capacity_negative": precision_boundary_capacity(2, 4) == 4,
        "precision_exhaustive_negative": not exhaustive_threshold_codebook_covers(4, 2),
        "precision_tight_positive": exhaustive_threshold_codebook_covers(3, 2),
        "precision_bits_exact": minimum_threshold_bits(4) == 3,
        "update_capacity_negative": not update_channel_allows(5, 2, 2),
        "update_exhaustive_negative": not exhaustive_update_decoder_covers(5, 2, 2),
        "update_tight_positive": exhaustive_update_decoder_covers(4, 2, 2),
        "update_steps_exact": minimum_update_steps(5, 2) == 3,
        "protected_rank_exact": matrix_rank(protected) == 2,
        "protected_nullity_exact": protected_nullity(protected, 3) == 1,
        "protected_frontier_negative": not protected_frontier_allows(protected, 3, 2),
        "protected_frontier_tight": protected_frontier_allows(protected, 3, 1),
    }
    failed = [name for name, ok in checks.items() if not ok]
    return {
        "status": "PASS" if not failed else "FAIL",
        "failed": failed,
        "ceiling_ids": list(EXPECTED_IDS),
        "claim_ceiling": load_registry()["claim_ceiling"],
        "checks": checks,
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
