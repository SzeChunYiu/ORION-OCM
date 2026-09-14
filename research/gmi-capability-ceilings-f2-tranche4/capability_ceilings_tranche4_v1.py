"""Exact finite witnesses for #602 F2 tranche 4: acquisition and social identifiability."""

from itertools import product
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
REGISTRY_PATH = HERE / "F2_TRANCHE4_CEILINGS_V1.json"

EXPECTED_IDS = (
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
        return ["missing top-level fields: %s" % sorted(missing)]
    if data["schema"] != "GMICapabilityCeilingsF2Tranche4V1":
        errors.append("schema mismatch")
    if data["issue"] != 602:
        errors.append("issue must be 602")
    if data["claim_ceiling"] != "G2":
        errors.append("claim ceiling must be G2")
    if "P1" not in data["evidence_class"] or "P2" not in data["evidence_class"]:
        errors.append("evidence class must register P1 and P2")
    if len(data["strongest_parents"]) != 2:
        errors.append("exactly two strongest-parent families required")
    if data["terminal"] != "F2_ALL_ELEVEN_BOUNDED_CEILINGS_REGISTERED_AT_G2":
        errors.append("terminal mismatch")
    ids = [row.get("id") for row in data["ceilings"]]
    if tuple(ids) != EXPECTED_IDS:
        errors.append("ceiling id/order mismatch: %r" % ids)
    if len(ids) != len(set(ids)):
        errors.append("duplicate ceiling id")
    for i, row in enumerate(data["ceilings"]):
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
    errors = validate_registry()
    if errors:
        return {"status": "FAIL", "errors": errors}
    base, heldout, diagnostic = social_witness()
    checks = {
        "acquisition_5_not_two_binary": not acquisition_allows(5, 2, 2),
        "acquisition_4_two_binary": acquisition_allows(4, 2, 2),
        "acquisition_min_queries": minimum_queries(5, 2) == 3,
        "acquisition_exhaustive_negative": not exhaustive_separating_code_exists(5, 2, 2),
        "acquisition_exhaustive_tight": exhaustive_separating_code_exists(4, 2, 2),
        "acquisition_budget": acquisition_budget_capacity(2, 5, 2) == 4,
        "social_base_not_identifiable": not social_response_identifiable(base, heldout),
        "social_base_decoder_absent": not exhaustive_social_decoder_exists(base, heldout),
        "social_diagnostic_restores": social_response_identifiable(diagnostic, heldout),
        "social_diagnostic_full_models": social_model_identifiable(diagnostic),
        "social_base_classes": social_transcript_class_count(base) == 2,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "claim_ceiling": "G2",
        "ceiling_ids": list(EXPECTED_IDS),
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
