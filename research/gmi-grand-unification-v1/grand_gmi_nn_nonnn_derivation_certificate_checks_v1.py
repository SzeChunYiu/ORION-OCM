#!/usr/bin/env python3
"""Finite synthesis checks for the Grand GMI NN/non-NN derivation certificate."""

import json


VERDICT_BY_SINGLE_FAMILY = {
    "NEURAL": "DERIVED_NEURAL",
    "NON_NEURAL": "DERIVED_NON_NEURAL",
    "HYBRID": "DERIVED_HYBRID",
}


def dominates(a, b):
    pa = a["profile"]
    pb = b["profile"]
    return all(x <= y for x, y in zip(pa, pb)) and any(x < y for x, y in zip(pa, pb))


def derive(candidates, evidence_complete=True, evidence_ambiguous=False, receipt_consistent=True):
    if not receipt_consistent:
        return "UNDECIDED_FROM_CURRENT_EVIDENCE", [], []
    if not evidence_complete or evidence_ambiguous:
        return "UNDECIDED_FROM_CURRENT_EVIDENCE", [], []

    survivors = [
        c for c in candidates
        if c.get("realization_valid", False)
        and c.get("adequate", False)
        and c.get("substrate_legal", False)
        and c.get("reachable", False)
        and c.get("hard_feasible", False)
    ]
    if not survivors:
        return "INFEASIBLE_AT_REGISTERED_SCOPE", [], []

    selected = [
        c for c in survivors
        if not any(dominates(other, c) for other in survivors if other["name"] != c["name"])
    ]
    families = sorted({c["family"] for c in selected})
    if len(families) == 1:
        verdict = VERDICT_BY_SINGLE_FAMILY.get(families[0], "FAMILY_COEXISTENCE")
    else:
        verdict = "FAMILY_COEXISTENCE"
    return verdict, sorted(c["name"] for c in selected), families


def candidate(name, family, profile, **overrides):
    c = {
        "name": name,
        "family": family,
        "profile": tuple(profile),
        "realization_valid": True,
        "adequate": True,
        "substrate_legal": True,
        "reachable": True,
        "hard_feasible": True,
    }
    c.update(overrides)
    return c


def main():
    # 1. Unique neural.
    neural_case = [
        candidate("N", "NEURAL", (1, 1)),
        candidate("P", "NON_NEURAL", (2, 2)),
    ]
    vn, sn, fn = derive(neural_case)
    assert (vn, sn, fn) == ("DERIVED_NEURAL", ["N"], ["NEURAL"])

    # 2. Unique non-neural.
    nonneural_case = [
        candidate("N", "NEURAL", (3, 3)),
        candidate("P", "NON_NEURAL", (1, 1)),
    ]
    vp, sp, fp = derive(nonneural_case)
    assert (vp, sp, fp) == ("DERIVED_NON_NEURAL", ["P"], ["NON_NEURAL"])

    # 3. Unique hybrid.
    hybrid_case = [
        candidate("N", "NEURAL", (3, 3)),
        candidate("P", "NON_NEURAL", (2, 4)),
        candidate("H", "HYBRID", (1, 1)),
    ]
    vh, sh, fh = derive(hybrid_case)
    assert (vh, sh, fh) == ("DERIVED_HYBRID", ["H"], ["HYBRID"])

    # 4. Cross-family coexistence.
    coexist_case = [
        candidate("N", "NEURAL", (1, 2)),
        candidate("P", "NON_NEURAL", (2, 1)),
    ]
    vc, sc, fc = derive(coexist_case)
    assert vc == "FAMILY_COEXISTENCE"
    assert sc == ["N", "P"]
    assert fc == ["NEURAL", "NON_NEURAL"]

    # 5. Infeasible registered scope.
    infeasible_case = [
        candidate("N", "NEURAL", (1, 1), adequate=False),
        candidate("P", "NON_NEURAL", (1, 1), reachable=False),
    ]
    vi, si, fi = derive(infeasible_case)
    assert (vi, si, fi) == ("INFEASIBLE_AT_REGISTERED_SCOPE", [], [])

    # 6. Missing or ambiguous evidence forces abstention.
    vu1, _, _ = derive(neural_case, evidence_complete=False)
    vu2, _, _ = derive(neural_case, evidence_ambiguous=True)
    vu3, _, _ = derive(neural_case, receipt_consistent=False)
    assert vu1 == vu2 == vu3 == "UNDECIDED_FROM_CURRENT_EVIDENCE"

    # 7. Candidate-universe sensitivity: a scope-relative verdict can reverse.
    v_small, _, _ = derive([candidate("N", "NEURAL", (2, 2))])
    v_large, _, _ = derive([
        candidate("N", "NEURAL", (2, 2)),
        candidate("P", "NON_NEURAL", (1, 1)),
    ])
    assert v_small == "DERIVED_NEURAL"
    assert v_large == "DERIVED_NON_NEURAL"

    receipt = {
        "terminal": "GRAND_GMI_NN_NONNN_DERIVATION_CERTIFICATE_ALL_GREEN",
        "canonical_verdicts": {
            "neural": vn,
            "non_neural": vp,
            "hybrid": vh,
            "coexistence": vc,
            "infeasible": vi,
            "missing_evidence": vu1,
            "ambiguous_evidence": vu2,
            "receipt_mismatch": vu3,
        },
        "candidate_universe_sensitivity": {
            "restricted_universe": v_small,
            "expanded_universe": v_large,
            "global_uniqueness_from_registered_uniqueness_claimed": False,
        },
        "load_bearing_certificate_fields": 10,
        "formal_scope": "finite registered candidate set with decidable certificate fields",
        "unrestricted_global_optimizer_claimed": False,
        "empirical_inputs_manufactured_by_theory": False,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
