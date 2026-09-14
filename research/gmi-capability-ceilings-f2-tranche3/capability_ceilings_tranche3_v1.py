"""Exact finite witnesses for #602 F2 tranche 3: planning, search, verification."""

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
REGISTRY_PATH = HERE / "F2_TRANCHE3_CEILINGS_V1.json"

EXPECTED_IDS = (
    "F2_PLANNING_RESOURCE_HORIZON",
    "F2_SEARCH_BUDGET_VERIFIED_CLASS",
    "F2_VERIFICATION_BUDGET_FALSE_ADOPTION",
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
    if data["schema"] != "GMICapabilityCeilingsF2Tranche3V1":
        errors.append("schema mismatch")
    if data["issue"] != 602:
        errors.append("issue must be 602")
    if data["claim_ceiling"] != "G2":
        errors.append("claim ceiling must be G2")
    if "P1" not in data["evidence_class"] or "P2" not in data["evidence_class"]:
        errors.append("evidence class must register P1 and P2")
    if len(data["strongest_parents"]) != 3:
        errors.append("exactly three strongest-parent families required")
    if data["terminal"] != "F2_TRANCHE3_PLANNING_SEARCH_VERIFICATION_CEILINGS_REGISTERED_AT_G2":
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


def run():
    errors = validate_registry()
    if errors:
        return {"status": "FAIL", "errors": errors}
    checks = {
        "planning_14_not_depth3": not planning_budget_allows(2, 3, 14),
        "planning_15_depth3": planning_budget_allows(2, 3, 15),
        "planning_horizon_boundary": max_exhaustive_horizon(2, 14) == 2 and max_exhaustive_horizon(2, 15) == 3,
        "planning_adversary": planning_uninspected_adversary(2, 3, 14),
        "search_4_not_5": not search_budget_allows(5, 4),
        "search_5_covers_5": search_budget_allows(5, 5),
        "search_adversary": unstructured_search_adversary(5, [0, 1, 2, 3]) == 4,
        "verification_single_defect": hypergeom_false_adoption(10, 1, 8) == Fraction(1, 5),
        "verification_two_defects": hypergeom_false_adoption(6, 2, 2) == Fraction(2, 5),
        "verification_exhaustive_matches_formula": exhaustive_uniform_defect_miss(6, 2, [0, 1]) == Fraction(2, 5),
        "verification_full_zero": hypergeom_false_adoption(10, 1, 10) == 0,
        "verification_adversarial_requires_full": not adversarial_zero_false_adoption_possible(10, 9) and adversarial_zero_false_adoption_possible(10, 10),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    return {
        "status": status,
        "claim_ceiling": "G2",
        "ceiling_ids": list(EXPECTED_IDS),
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
