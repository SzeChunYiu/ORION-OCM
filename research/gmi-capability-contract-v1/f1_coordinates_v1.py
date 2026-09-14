"""Executable structural verifier for issue #602 F1 capability coordinates.

This module validates the exact 17-coordinate architecture-independent registry
and implements the common bounded independent-unit assay.  It proves only
properties of the registered specification; it does not establish empirical
capability possession or a G6 morphology-to-capability map.
"""

from pathlib import Path
import json
import math
import re


def _here():
    try:
        return Path(__file__).resolve().parent
    except NameError:
        for cand in [Path.cwd() / "research/gmi-capability-contract-v1", Path.cwd()]:
            if (cand / "CAPABILITY_COORDINATES_V1.json").exists():
                return cand
        return Path.cwd()


HERE = _here()
COORDINATES = HERE / "CAPABILITY_COORDINATES_V1.json"
ASSAY = HERE / "F1_ASSAY_V1.json"

EXPECTED_COORDINATES = (
    "memory_capacity_retention",
    "retrieval_efficiency",
    "abstraction_compression_ability",
    "transfer_generalization",
    "compositional_depth",
    "planning_horizon",
    "exploration_information_gain_efficiency",
    "causal_identifiability_intervention",
    "robustness_invariance",
    "continual_learning_plasticity",
    "catastrophic_forgetting_susceptibility",
    "tool_use_solver_routing",
    "social_model_depth",
    "communication_capacity",
    "verification_reliability",
    "self_model_accuracy",
    "meta_learning_evolvability",
)

REQUIRED_FIELDS = {
    "id", "label", "definition", "reporting_contract", "scope", "assumptions",
    "strongest_parent", "falsifier", "evidence_class", "claim_ceiling",
}


def load_coordinates():
    return json.loads(COORDINATES.read_text(encoding="utf-8"))


def load_assay():
    return json.loads(ASSAY.read_text(encoding="utf-8"))


def claim_rank(value):
    match = re.fullmatch(r"G(\d+)", value if isinstance(value, str) else "")
    if not match:
        raise ValueError("invalid claim ceiling %r" % (value,))
    return int(match.group(1))


def hoeffding_radius(n, alpha):
    """Radius for each of three simultaneous one-sided Hoeffding events.

    Paired differences lie in [-1, 1], so their range width is 2.  Allocating
    alpha/3 to one positive lower-tail and two twin tails gives
    sqrt(2*ln(3/alpha)/n).
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")
    if not isinstance(alpha, (int, float)) or not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0,1)")
    return math.sqrt(2.0 * math.log(3.0 / alpha) / n)


def assay_pass(positive_diffs, twin_diffs, tau_parent, tau_twin, alpha=0.05):
    """Evaluate S0 for independent paired differences bounded in [-1, 1]."""
    if not positive_diffs or not twin_diffs:
        raise ValueError("both paired-difference samples must be nonempty")
    for value in list(positive_diffs) + list(twin_diffs):
        if not isinstance(value, (int, float)) or not -1 <= value <= 1:
            raise ValueError("paired differences must lie in [-1,1]")
    if not isinstance(tau_parent, (int, float)) or not isinstance(tau_twin, (int, float)):
        raise ValueError("thresholds must be numeric")
    mean_positive = sum(positive_diffs) / len(positive_diffs)
    mean_twin = sum(twin_diffs) / len(twin_diffs)
    eps_positive = hoeffding_radius(len(positive_diffs), alpha)
    eps_twin = hoeffding_radius(len(twin_diffs), alpha)
    return (
        mean_positive - eps_positive > tau_parent
        and abs(mean_twin) + eps_twin <= tau_twin
    )


def validate_assay(data=None):
    if data is None:
        data = load_assay()
    errors = []
    if not isinstance(data, dict):
        return ["assay must be an object"]
    if data.get("schema") != "F1CapabilityAssayV1":
        errors.append("wrong assay schema")
    if data.get("issue") != 602:
        errors.append("assay issue must be 602")
    try:
        ceiling = claim_rank(data.get("claim_ceiling"))
        if ceiling != 1:
            errors.append("F1 registration ceiling must be G1")
    except ValueError as exc:
        errors.append(str(exc))
    definitions = data.get("definitions")
    if not isinstance(definitions, dict):
        errors.append("definitions must be an object")
    else:
        for key in ("A0", "S0", "N0", "P0"):
            if not isinstance(definitions.get(key), str) or not definitions[key].strip():
                errors.append("missing common definition %s" % key)
    stats = data.get("statistics")
    if not isinstance(stats, dict):
        errors.append("statistics must be an object")
    else:
        alpha = stats.get("alpha_default")
        if not isinstance(alpha, (int, float)) or not 0 < alpha < 1:
            errors.append("alpha_default must lie in (0,1)")
        if stats.get("simultaneous_events") != 3:
            errors.append("common assay must register exactly three one-sided events")
        if stats.get("requires_independent_units") is not True:
            errors.append("common Hoeffding assay must require independent units")
        if "3/alpha" not in stats.get("bound", ""):
            errors.append("common assay must encode alpha/3 Bonferroni radius")
    order = data.get("resource_order")
    if not isinstance(order, dict) or "frozen before protected scoring" not in order.get("scalarization_rule", ""):
        errors.append("resource scalarization rule must require frozen prices")
    return errors


def validate_coordinates(rows=None, assay=None):
    if rows is None:
        rows = load_coordinates()
    if assay is None:
        assay = load_assay()
    errors = list(validate_assay(assay))
    if not isinstance(rows, list):
        return errors + ["coordinates must be a list"]
    ids = [row.get("id") for row in rows if isinstance(row, dict)]
    if len(ids) != len(rows):
        errors.append("every coordinate row must be an object")
    if len(ids) != len(set(ids)):
        errors.append("coordinate IDs must be unique")
    expected = set(EXPECTED_COORDINATES)
    actual = set(ids)
    if actual != expected:
        errors.append(
            "coordinate ID set mismatch: missing=%r extra=%r"
            % (sorted(expected - actual), sorted(actual - expected))
        )
    try:
        ceiling = claim_rank(assay.get("claim_ceiling"))
    except ValueError:
        ceiling = -1
    for row in rows:
        if not isinstance(row, dict):
            continue
        row_id = row.get("id", "<missing>")
        missing = REQUIRED_FIELDS - set(row)
        if missing:
            errors.append("%s: missing fields %r" % (row_id, sorted(missing)))
            continue
        for field in (
            "label", "definition", "reporting_contract", "scope",
            "strongest_parent", "falsifier", "evidence_class",
        ):
            if not isinstance(row[field], str) or not row[field].strip():
                errors.append("%s: %s must be nonempty text" % (row_id, field))
        if not isinstance(row["assumptions"], list) or not row["assumptions"]:
            errors.append("%s: assumptions must be nonempty" % row_id)
        try:
            if claim_rank(row["claim_ceiling"]) > ceiling:
                errors.append("%s: claim ceiling exceeds assay ceiling" % row_id)
        except ValueError as exc:
            errors.append("%s: %s" % (row_id, exc))
    return errors


def run():
    rows = load_coordinates()
    assay = load_assay()
    errors = validate_coordinates(rows, assay)
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "status": "PASS",
        "coordinates": len(rows),
        "claim_ceiling": assay["claim_ceiling"],
        "independent_unit_gate": True,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
