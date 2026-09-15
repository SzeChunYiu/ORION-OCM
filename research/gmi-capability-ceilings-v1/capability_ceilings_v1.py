"""Exact finite witnesses and scope guards for #602 F2 capability ceilings (all eleven rows)."""

from fractions import Fraction
from itertools import combinations, product
from math import comb
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
    "F2_PLANNING_RESOURCE_HORIZON",
    "F2_SEARCH_BUDGET_VERIFIED_CLASS",
    "F2_VERIFICATION_BUDGET_FALSE_ADOPTION",
    "F2_INFORMATION_ACQUISITION_BUDGET",
    "F2_SOCIAL_OBSERVATION_IDENTIFIABILITY",
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
    if len(data["strongest_parents"]) < 11:
        errors.append("all eleven strongest-parent families must be registered")
    if not str(data["falsifier"]).strip():
        errors.append("top-level falsifier must be non-empty")
    if data["terminal"] != "F2_ALL_ELEVEN_BOUNDED_CEILINGS_REGISTERED_AT_G2":
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


def complete_tree_nodes(branching, horizon):
    """Number of nodes from depth 0 through horizon in a full b-ary tree."""
    _positive_int("branching", branching)
    _nonnegative_int("horizon", horizon)
    if branching == 1:
        return horizon + 1
    return (branching ** (horizon + 1) - 1) // (branching - 1)


def planning_budget_allows(branching, horizon, node_budget):
    _positive_int("node_budget", node_budget)
    return complete_tree_nodes(branching, horizon) <= node_budget


def max_exhaustive_horizon(branching, node_budget):
    _positive_int("branching", branching)
    _positive_int("node_budget", node_budget)
    h = 0
    if complete_tree_nodes(branching, h) > node_budget:
        return -1
    while complete_tree_nodes(branching, h + 1) <= node_budget:
        h += 1
    return h


def validate_planning_scope(instance):
    errors = []
    if not instance.get("full_tree", False):
        errors.append("planning ceiling requires a full registered branching tree")
    for key, phrase in (
        ("heuristic_oracle", "heuristic oracle"),
        ("pruning_certificate", "pruning certificate"),
        ("transposition_merging", "transposition merging"),
        ("structural_dominance", "structural dominance"),
    ):
        if instance.get(key, False):
            errors.append("%s changes the exhaustive-tree ceiling" % phrase)
    if not instance.get("worst_case_complete", False):
        errors.append("theorem is a worst-case complete-coverage ceiling")
    return errors


def planning_uninspected_adversary(branching, horizon, inspected_nodes):
    """True exactly when an uninspected node can still hide the only decisive event."""
    _positive_int("branching", branching)
    _nonnegative_int("horizon", horizon)
    _nonnegative_int("inspected_nodes", inspected_nodes)
    return inspected_nodes < complete_tree_nodes(branching, horizon)


def search_budget_allows(candidate_count, queries):
    _positive_int("candidate_count", candidate_count)
    _nonnegative_int("queries", queries)
    return queries >= candidate_count


def max_guaranteed_unstructured_candidates(queries):
    _nonnegative_int("queries", queries)
    return queries


def unstructured_search_adversary(candidate_count, queried_indices):
    """Return an unqueried index where an adversary can place the unique valid candidate."""
    _positive_int("candidate_count", candidate_count)
    queried = tuple(queried_indices)
    if any(isinstance(i, bool) or not isinstance(i, int) or i < 0 or i >= candidate_count for i in queried):
        raise ValueError("queried index outside candidate domain")
    if len(set(queried)) != len(queried):
        raise ValueError("duplicate query does not enlarge searched class")
    queried_set = set(queried)
    for i in range(candidate_count):
        if i not in queried_set:
            return i
    return None


def validate_search_scope(instance):
    errors = []
    if not instance.get("unstructured_candidates", False):
        errors.append("candidate structure can reduce deterministic query complexity")
    if instance.get("ordering_promise", False):
        errors.append("ordering promise is a search shortcut outside the unstructured theorem")
    if instance.get("heuristic_oracle", False):
        errors.append("heuristic oracle is an additional information channel")
    if instance.get("side_information", False):
        errors.append("side information must be charged before applying the search ceiling")
    if not instance.get("perfect_membership_verifier", False):
        errors.append("search theorem assumes an exact membership verifier")
    if not instance.get("worst_case_zero_error", False):
        errors.append("search theorem is worst-case zero-error only")
    return errors


def hypergeom_false_adoption(total_coordinates, defects, checks):
    """Exact miss probability under a uniform r-defect subset and q checks."""
    _positive_int("total_coordinates", total_coordinates)
    _positive_int("defects", defects)
    _nonnegative_int("checks", checks)
    if defects > total_coordinates:
        raise ValueError("defects cannot exceed total coordinates")
    if checks > total_coordinates:
        raise ValueError("checks cannot exceed total coordinates")
    if total_coordinates - checks < defects:
        return Fraction(0, 1)
    return Fraction(comb(total_coordinates - checks, defects), comb(total_coordinates, defects))


def minimum_checks_for_false_adoption(total_coordinates, defects, max_probability):
    _positive_int("total_coordinates", total_coordinates)
    _positive_int("defects", defects)
    if defects > total_coordinates:
        raise ValueError("defects cannot exceed total coordinates")
    if not isinstance(max_probability, Fraction):
        max_probability = Fraction(max_probability)
    if max_probability < 0 or max_probability > 1:
        raise ValueError("max_probability must lie in [0,1]")
    for checks in range(total_coordinates + 1):
        if hypergeom_false_adoption(total_coordinates, defects, checks) <= max_probability:
            return checks
    raise AssertionError("full verification must reach zero false adoption")


def exhaustive_uniform_defect_miss(total_coordinates, defects, checked_indices):
    """Enumerate every equally likely defect subset and return the exact miss fraction."""
    _positive_int("total_coordinates", total_coordinates)
    _positive_int("defects", defects)
    if defects > total_coordinates:
        raise ValueError("defects cannot exceed total coordinates")
    checked = tuple(checked_indices)
    if len(set(checked)) != len(checked):
        raise ValueError("checks must be distinct")
    if any(isinstance(i, bool) or not isinstance(i, int) or i < 0 or i >= total_coordinates for i in checked):
        raise ValueError("checked index outside coordinate domain")
    cases = list(combinations(range(total_coordinates), defects))
    misses = sum(1 for bad in cases if set(bad).isdisjoint(checked))
    return Fraction(misses, len(cases))


def adversarial_zero_false_adoption_possible(total_coordinates, checks):
    """Zero worst-case FA against one arbitrary defect is possible iff every coordinate is checked."""
    _positive_int("total_coordinates", total_coordinates)
    _nonnegative_int("checks", checks)
    if checks > total_coordinates:
        raise ValueError("checks cannot exceed total coordinates")
    return checks == total_coordinates


def validate_verification_scope(instance):
    errors = []
    if not instance.get("exchangeable_defects", False):
        errors.append("probabilistic floor requires exchangeable registered defect locations")
    if instance.get("defect_location_side_info", False):
        errors.append("defect-location side information changes the sampling law")
    if not instance.get("distinct_checks_without_replacement", False):
        errors.append("theorem meters distinct checks without replacement")
    if not instance.get("perfect_check_detection", False):
        errors.append("exact formula assumes every checked defect is detected")
    if not instance.get("adopt_iff_all_checked_pass", False):
        errors.append("adoption rule must be fixed as all checked coordinates passing")
    return errors


def acquisition_transcript_capacity(outcomes_per_query, queries):
    _positive_int("outcomes_per_query", outcomes_per_query)
    _nonnegative_int("queries", queries)
    return outcomes_per_query ** queries


def acquisition_allows(hypotheses, outcomes_per_query, queries):
    _positive_int("hypotheses", hypotheses)
    return hypotheses <= acquisition_transcript_capacity(outcomes_per_query, queries)


def minimum_queries(hypotheses, outcomes_per_query):
    _positive_int("hypotheses", hypotheses)
    _positive_int("outcomes_per_query", outcomes_per_query)
    if hypotheses == 1:
        return 0
    if outcomes_per_query == 1:
        raise ValueError("one-outcome queries cannot separate multiple hypotheses")
    q = 0
    cap = 1
    while cap < hypotheses:
        q += 1
        cap *= outcomes_per_query
    return q


def max_queries_from_budget(total_budget, per_query_cost):
    _nonnegative_int("total_budget", total_budget)
    _positive_int("per_query_cost", per_query_cost)
    return total_budget // per_query_cost


def acquisition_budget_capacity(outcomes_per_query, total_budget, per_query_cost):
    return acquisition_transcript_capacity(
        outcomes_per_query,
        max_queries_from_budget(total_budget, per_query_cost),
    )


def exhaustive_separating_code_exists(hypotheses, outcomes_per_query, queries, max_candidates=2_000_000):
    """Enumerate hypothesis->transcript codes for tiny rich-query witnesses."""
    _positive_int("hypotheses", hypotheses)
    transcripts = acquisition_transcript_capacity(outcomes_per_query, queries)
    candidates = transcripts ** hypotheses
    if candidates > max_candidates:
        raise ValueError("enumeration cap exceeded")
    for code in product(range(transcripts), repeat=hypotheses):
        if len(set(code)) == hypotheses:
            return True
    return False


def validate_acquisition_scope(instance):
    errors = []
    if not instance.get("deterministic", False):
        errors.append("acquisition ceiling is deterministic at this scope")
    if not instance.get("noiseless", False):
        errors.append("acquisition ceiling uses noiseless registered outcomes")
    if not instance.get("bounded_outcome_alphabet", False):
        errors.append("query outcome alphabet must be prospectively bounded")
    if instance.get("free_side_information", False):
        errors.append("free side information is an additional information channel")
    if instance.get("passive_target_information", False):
        errors.append("passive target information must be included before applying the ceiling")
    if not instance.get("zero_error", False):
        errors.append("acquisition theorem is zero-error only")
    return errors


def _validate_same_nonempty_domain(a, b):
    if not a or not b:
        raise ValueError("maps must be non-empty")
    if set(a) != set(b):
        raise ValueError("map domains must match")


def social_response_identifiable(transcript_of_model, required_response):
    """Exact fiber criterion: response must be constant on every transcript fiber."""
    _validate_same_nonempty_domain(transcript_of_model, required_response)
    response_by_transcript = {}
    for model, transcript in transcript_of_model.items():
        response = required_response[model]
        if transcript in response_by_transcript and response_by_transcript[transcript] != response:
            return False
        response_by_transcript[transcript] = response
    return True


def social_model_identifiable(transcript_of_model):
    if not transcript_of_model:
        raise ValueError("transcript map must be non-empty")
    return len(set(transcript_of_model.values())) == len(transcript_of_model)


def social_transcript_class_count(transcript_of_model):
    if not transcript_of_model:
        raise ValueError("transcript map must be non-empty")
    return len(set(transcript_of_model.values()))


def exhaustive_social_decoder_exists(transcript_of_model, required_response, max_candidates=2_000_000):
    _validate_same_nonempty_domain(transcript_of_model, required_response)
    transcripts = tuple(sorted(set(transcript_of_model.values()), key=repr))
    responses = tuple(sorted(set(required_response.values()), key=repr))
    candidates = len(responses) ** len(transcripts)
    if candidates > max_candidates:
        raise ValueError("enumeration cap exceeded")
    for outputs in product(responses, repeat=len(transcripts)):
        decoder = dict(zip(transcripts, outputs))
        if all(decoder[transcript_of_model[m]] == required_response[m] for m in transcript_of_model):
            return True
    return False


def social_witness():
    base = {
        "goal_left": "context0:wait",
        "belief_blocked": "context0:wait",
        "goal_stay": "context0:go",
    }
    heldout = {
        "goal_left": "predict:left",
        "belief_blocked": "predict:right",
        "goal_stay": "predict:stay",
    }
    diagnostic = {
        "goal_left": "context0:wait|probe:left",
        "belief_blocked": "context0:wait|probe:right",
        "goal_stay": "context0:go|probe:stay",
    }
    return base, heldout, diagnostic


def validate_social_scope(instance):
    errors = []
    if instance.get("hidden_model_label_visible", False):
        errors.append("hidden model label is a direct answer side channel")
    if instance.get("private_state_access", False):
        errors.append("private-state access changes the social observation interface")
    if instance.get("unregistered_later_probe", False):
        errors.append("later diagnostic interaction must be included in the registered transcript")
    if not instance.get("deterministic_behavior", False):
        errors.append("this exact theorem uses deterministic model-to-transcript behavior")
    if not instance.get("zero_error", False):
        errors.append("this exact theorem is zero-error only")
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
    social_base, social_heldout, social_diagnostic = social_witness()

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
        "planning_14_not_depth3": not planning_budget_allows(2, 3, 14),
        "planning_15_depth3": planning_budget_allows(2, 3, 15),
        "planning_horizon_boundary": (
            max_exhaustive_horizon(2, 14) == 2 and max_exhaustive_horizon(2, 15) == 3
        ),
        "planning_adversary": planning_uninspected_adversary(2, 3, 14),
        "search_4_not_5": not search_budget_allows(5, 4),
        "search_5_covers_5": search_budget_allows(5, 5),
        "search_adversary": unstructured_search_adversary(5, [0, 1, 2, 3]) == 4,
        "verification_single_defect": hypergeom_false_adoption(10, 1, 8) == Fraction(1, 5),
        "verification_two_defects": hypergeom_false_adoption(6, 2, 2) == Fraction(2, 5),
        "verification_exhaustive_matches_formula": (
            exhaustive_uniform_defect_miss(6, 2, [0, 1]) == Fraction(2, 5)
        ),
        "verification_full_zero": hypergeom_false_adoption(10, 1, 10) == 0,
        "verification_adversarial_requires_full": (
            not adversarial_zero_false_adoption_possible(10, 9)
            and adversarial_zero_false_adoption_possible(10, 10)
        ),
        "acquisition_5_not_two_binary": not acquisition_allows(5, 2, 2),
        "acquisition_4_two_binary": acquisition_allows(4, 2, 2),
        "acquisition_min_queries": minimum_queries(5, 2) == 3,
        "acquisition_exhaustive_negative": not exhaustive_separating_code_exists(5, 2, 2),
        "acquisition_exhaustive_tight": exhaustive_separating_code_exists(4, 2, 2),
        "acquisition_budget": acquisition_budget_capacity(2, 5, 2) == 4,
        "social_base_not_identifiable": not social_response_identifiable(
            social_base, social_heldout
        ),
        "social_base_decoder_absent": not exhaustive_social_decoder_exists(
            social_base, social_heldout
        ),
        "social_diagnostic_restores": social_response_identifiable(
            social_diagnostic, social_heldout
        ),
        "social_diagnostic_full_models": social_model_identifiable(social_diagnostic),
        "social_base_classes": social_transcript_class_count(social_base) == 2,
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
