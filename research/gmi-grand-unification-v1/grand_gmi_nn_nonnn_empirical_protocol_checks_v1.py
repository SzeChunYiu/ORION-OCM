#!/usr/bin/env python3
"""Structural and synthetic logic checks for the NN/non-NN empirical protocol.

No hardware or deployment measurements are generated here. Synthetic intervals only
verify that the preregistered adjudication semantics refuse overclaiming.
"""

import json
import math
from decimal import Decimal
from numbers import Rational, Real
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "NN_NONNN_EMPIRICAL_PROTOCOL_SCHEMA_V1.json"

EXPECTED_SECTIONS = {
    "problem_registration",
    "family_definitions",
    "candidate_universe",
    "development_reachability",
    "resource_accounting",
    "deployment_generalization",
    "replication_uncertainty",
    "hard_feasibility_gates",
    "selection_rule",
    "prospective_predictions",
    "provenance_receipts",
}

DERIVED = {
    "NEURAL": "DERIVED_NEURAL_AT_REGISTERED_SCOPE",
    "NON_NEURAL": "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE",
    "HYBRID": "DERIVED_HYBRID_AT_REGISTERED_SCOPE",
}
UNDECIDED = "UNDECIDED_FROM_CURRENT_EVIDENCE"
EVIDENCE_FIELDS = ("hard_gate_pass", "development_reached", "deployment_evidence_present")


def finite_real(value):
    if isinstance(value, bool):
        return False
    if isinstance(value, Rational):
        return True
    if isinstance(value, Decimal):
        return value.is_finite()
    return isinstance(value, Real) and math.isfinite(value)


def adjudicate_scalar(candidates, prerequisites_complete=True):
    """Adjudicate certified intervals for one frozen, common scalar cost.

    Interval coverage/calibration and scalar registration remain externally
    certified prerequisites; ordered numeric bounds alone cannot prove them.
    Missing deployment evidence is unknown adequacy, not a failed deployment gate.
    An explicit hard/development gate failure can independently exclude a candidate.
    """
    if prerequisites_complete is not True or not isinstance(candidates, (list, tuple)):
        return UNDECIDED

    identities = set()
    for c in candidates:
        if (not isinstance(c, dict)
                or not isinstance(c.get("candidate_id"), str) or not c["candidate_id"].strip()
                or c["candidate_id"] in identities
                or not isinstance(c.get("family"), str) or c["family"] not in DERIVED
                or any(type(c.get(field)) is not bool for field in EVIDENCE_FIELDS)
                or not finite_real(c.get("lo")) or not finite_real(c.get("hi"))
                or c["lo"] > c["hi"]):
            return UNDECIDED
        identities.add(c["candidate_id"])

    eligible = [c for c in candidates if c["hard_gate_pass"] and c["development_reached"]]
    if any(not c["deployment_evidence_present"] for c in eligible):
        return UNDECIDED

    feasible = eligible
    if not feasible:
        return "INFEASIBLE_AT_REGISTERED_SCOPE"

    # A family-comparison packet containing only one feasible/represented family cannot
    # prove that family necessary against an unrepresented competitor. A separate
    # candidate-completeness/exclusion theorem would be needed to override this guard.
    registered_families = {c["family"] for c in candidates}
    if len(registered_families) < 2:
        return "UNDECIDED_FROM_CURRENT_EVIDENCE"

    winners = []
    for candidate in feasible:
        if all(
            candidate["hi"] < other["lo"]
            for other in feasible
            if other["candidate_id"] != candidate["candidate_id"]
        ):
            winners.append(candidate)

    if len(winners) == 1:
        fam = winners[0]["family"]
        return DERIVED[fam]

    return "UNDECIDED_FROM_CURRENT_EVIDENCE"


def c(cid, family, lo, hi, hard=True, reached=True, deploy=True):
    """Build synthetic logic fixtures, without manufacturing real certificates."""
    return {
        "candidate_id": cid,
        "family": family,
        "lo": lo,
        "hi": hi,
        "hard_gate_pass": hard,
        "development_reached": reached,
        "deployment_evidence_present": deploy,
    }


def main():
    schema = json.loads(SCHEMA.read_text())
    assert schema["status"] == "PROTOCOL_SCHEMA_NOT_AN_EXECUTED_EXPERIMENT"
    assert set(schema["required_sections"]) == EXPECTED_SECTIONS
    assert set(schema["allowed_selection_modes"]) == {"PARETO", "SCALAR_PREREGISTERED"}
    assert "DERIVED_NEURAL_AT_REGISTERED_SCOPE" in schema["allowed_canonical_terminals"]
    assert "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE" in schema["allowed_canonical_terminals"]
    assert "DERIVED_HYBRID_AT_REGISTERED_SCOPE" in schema["allowed_canonical_terminals"]
    assert "UNDECIDED_FROM_CURRENT_EVIDENCE" in schema["allowed_canonical_terminals"]
    assert len(schema["forbidden_shortcuts"]) == 7

    neural_unique = [
        c("n1", "NEURAL", 8, 9),
        c("x1", "NON_NEURAL", 11, 13),
    ]
    assert adjudicate_scalar(neural_unique) == "DERIVED_NEURAL_AT_REGISTERED_SCOPE"

    overlap = [
        c("n1", "NEURAL", 8, 11),
        c("x1", "NON_NEURAL", 10, 12),
    ]
    assert adjudicate_scalar(overlap) == "UNDECIDED_FROM_CURRENT_EVIDENCE"

    expanded = neural_unique + [c("h1", "HYBRID", 6, 7)]
    assert adjudicate_scalar(expanded) == "DERIVED_HYBRID_AT_REGISTERED_SCOPE"

    cheap_but_inadequate = [
        c("bad", "NON_NEURAL", 1, 2, hard=False),
        c("n1", "NEURAL", 8, 9),
        c("x1", "NON_NEURAL", 11, 13),
    ]
    assert adjudicate_scalar(cheap_but_inadequate) == "DERIVED_NEURAL_AT_REGISTERED_SCOPE"

    missing_deployment = [
        c("n1", "NEURAL", 8, 9, deploy=False),
        c("x1", "NON_NEURAL", 11, 13, deploy=False),
    ]
    assert adjudicate_scalar(missing_deployment) == "UNDECIDED_FROM_CURRENT_EVIDENCE"
    # Absence of evidence is unresolved both at candidate level and packet level.
    assert adjudicate_scalar(neural_unique, prerequisites_complete=False) == "UNDECIDED_FROM_CURRENT_EVIDENCE"

    single_family_only = [c("n1", "NEURAL", 8, 9)]
    assert adjudicate_scalar(single_family_only) == "UNDECIDED_FROM_CURRENT_EVIDENCE"

    receipt = {
        "terminal": "GRAND_GMI_NN_NONNN_EMPIRICAL_PROTOCOL_SELF_TEST_ALL_GREEN",
        "required_sections_checked": len(EXPECTED_SECTIONS),
        "forbidden_shortcuts_registered": len(schema["forbidden_shortcuts"]),
        "synthetic_neural_unique_verdict": adjudicate_scalar(neural_unique),
        "synthetic_overlap_verdict": adjudicate_scalar(overlap),
        "synthetic_candidate_expansion_verdict": adjudicate_scalar(expanded),
        "synthetic_missing_deployment_verdict": adjudicate_scalar(missing_deployment),
        "hard_gate_precedes_cost_selection": True,
        "missing_packet_prerequisites_force_abstention": True,
        "single_family_registry_cannot_prove_family_necessity": True,
        "real_empirical_measurements_executed": False,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
