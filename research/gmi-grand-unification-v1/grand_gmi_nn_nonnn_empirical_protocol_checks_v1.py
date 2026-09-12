#!/usr/bin/env python3
"""Structural and synthetic logic checks for the NN/non-NN empirical protocol.

No hardware or deployment measurements are generated here. Synthetic intervals only
verify that the preregistered adjudication semantics refuse overclaiming.
"""

import json
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


def adjudicate_scalar(candidates, prerequisites_complete=True):
    """Adjudicate a frozen scalar-cost packet from certified [lo, hi] intervals."""
    if not prerequisites_complete:
        return "UNDECIDED_FROM_CURRENT_EVIDENCE"

    feasible = [
        c for c in candidates
        if c["hard_gate_pass"]
        and c["development_reached"]
        and c["deployment_evidence_present"]
    ]
    if not feasible:
        return "INFEASIBLE_AT_REGISTERED_SCOPE"

    winners = []
    for c in feasible:
        if all(c["hi"] < d["lo"] for d in feasible if d["candidate_id"] != c["candidate_id"]):
            winners.append(c)

    if len(winners) == 1:
        fam = winners[0]["family"]
        return DERIVED.get(fam, "FAMILY_COEXISTENCE_AT_REGISTERED_SCOPE")

    families = {c["family"] for c in feasible}
    if len(feasible) == 1 and len(families) == 1:
        # One feasible candidate does not prove its family necessary against a missing
        # registered competitor; the packet is candidate-scope underidentified.
        return "UNDECIDED_FROM_CURRENT_EVIDENCE"
    return "UNDECIDED_FROM_CURRENT_EVIDENCE"


def c(cid, family, lo, hi, hard=True, reached=True, deploy=True):
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
    assert adjudicate_scalar(missing_deployment) == "INFEASIBLE_AT_REGISTERED_SCOPE"
    # If the packet as a whole has not discharged deployment prerequisites, abstain
    # rather than reinterpret missing evidence as physical infeasibility.
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
        "hard_gate_precedes_cost_selection": True,
        "missing_packet_prerequisites_force_abstention": True,
        "single_family_registry_cannot_prove_family_necessity": True,
        "real_empirical_measurements_executed": False,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
