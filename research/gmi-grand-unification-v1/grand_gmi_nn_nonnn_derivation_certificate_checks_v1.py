#!/usr/bin/env python3
"""Finite synthesis checks for the Grand GMI NN/non-NN derivation certificate."""

import json
import math
from decimal import Decimal
from numbers import Rational, Real


VERDICT_BY_SINGLE_FAMILY = {
    "NEURAL": "DERIVED_NEURAL",
    "NON_NEURAL": "DERIVED_NON_NEURAL",
    "HYBRID": "DERIVED_HYBRID",
}
HARD_FIELDS = ("realization_valid", "adequate", "substrate_legal", "reachable", "hard_feasible")
UNDECIDED = "UNDECIDED_FROM_CURRENT_EVIDENCE"


def finite_real(value):
    """Accept exact rationals and finite real measurements, never booleans."""
    if isinstance(value, bool):
        return False
    if isinstance(value, Rational):
        return True
    if isinstance(value, Decimal):
        return value.is_finite()
    return isinstance(value, Real) and math.isfinite(value)


def valid_profile(profile, dimension):
    return (isinstance(profile, (list, tuple))
            and len(profile) == dimension
            and all(finite_real(value) for value in profile))


def dominates(a, b):
    pa = a["profile"]
    pb = b["profile"]
    if (not isinstance(pa, (list, tuple)) or not pa
            or not valid_profile(pa, len(pa)) or not valid_profile(pb, len(pa))):
        raise ValueError("Dominance requires matching nonempty finite real profiles")
    return all(x <= y for x, y in zip(pa, pb)) and any(x < y for x, y in zip(pa, pb))


def derive(candidates, evidence_complete=True, evidence_ambiguous=False, receipt_consistent=True,
           *, profile_dimension=None):
    """Select a finite typed certificate under its registered resource dimension.

    The dimension must come from the frozen resource-coordinate registration, not
    be inferred from candidate vectors: all candidates could omit the same suffix.
    Boolean fields report certified facts; None/missing/malformed evidence is not
    a proved failed gate. This checks structure, not the truth of those certificates.
    """
    flags = (evidence_complete, evidence_ambiguous, receipt_consistent)
    if (any(type(flag) is not bool for flag in flags)
            or not evidence_complete or evidence_ambiguous or not receipt_consistent):
        return UNDECIDED, [], []
    if (type(profile_dimension) is not int or profile_dimension < 1
            or not isinstance(candidates, (list, tuple))):
        return UNDECIDED, [], []

    names = set()
    for c in candidates:
        if (not isinstance(c, dict)
                or not isinstance(c.get("name"), str) or not c["name"].strip()
                or c["name"] in names
                or not isinstance(c.get("family"), str)
                or c["family"] not in VERDICT_BY_SINGLE_FAMILY
                or any(type(c.get(field)) is not bool for field in HARD_FIELDS)
                or not valid_profile(c.get("profile"), profile_dimension)):
            return UNDECIDED, [], []
        names.add(c["name"])

    survivors = [
        c for c in candidates
        if all(c[field] for field in HARD_FIELDS)
    ]
    if not survivors:
        return "INFEASIBLE_AT_REGISTERED_SCOPE", [], []

    selected = [
        c for c in survivors
        if not any(dominates(other, c) for other in survivors if other["name"] != c["name"])
    ]
    families = sorted({c["family"] for c in selected})
    if len(families) == 1:
        verdict = VERDICT_BY_SINGLE_FAMILY[families[0]]
    else:
        verdict = "FAMILY_COEXISTENCE"
    return verdict, sorted(c["name"] for c in selected), families


def candidate(name, family, profile, **overrides):
    """Build synthetic examples; default True flags are not empirical evidence."""
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
    vn, sn, fn = derive(neural_case, profile_dimension=2)
    assert (vn, sn, fn) == ("DERIVED_NEURAL", ["N"], ["NEURAL"])

    # 2. Unique non-neural.
    nonneural_case = [
        candidate("N", "NEURAL", (3, 3)),
        candidate("P", "NON_NEURAL", (1, 1)),
    ]
    vp, sp, fp = derive(nonneural_case, profile_dimension=2)
    assert (vp, sp, fp) == ("DERIVED_NON_NEURAL", ["P"], ["NON_NEURAL"])

    # 3. Unique hybrid.
    hybrid_case = [
        candidate("N", "NEURAL", (3, 3)),
        candidate("P", "NON_NEURAL", (2, 4)),
        candidate("H", "HYBRID", (1, 1)),
    ]
    vh, sh, fh = derive(hybrid_case, profile_dimension=2)
    assert (vh, sh, fh) == ("DERIVED_HYBRID", ["H"], ["HYBRID"])

    # 4. Cross-family coexistence.
    coexist_case = [
        candidate("N", "NEURAL", (1, 2)),
        candidate("P", "NON_NEURAL", (2, 1)),
    ]
    vc, sc, fc = derive(coexist_case, profile_dimension=2)
    assert vc == "FAMILY_COEXISTENCE"
    assert sc == ["N", "P"]
    assert fc == ["NEURAL", "NON_NEURAL"]

    # 5. Infeasible registered scope.
    infeasible_case = [
        candidate("N", "NEURAL", (1, 1), adequate=False),
        candidate("P", "NON_NEURAL", (1, 1), reachable=False),
    ]
    vi, si, fi = derive(infeasible_case, profile_dimension=2)
    assert (vi, si, fi) == ("INFEASIBLE_AT_REGISTERED_SCOPE", [], [])

    # 6. Missing or ambiguous evidence forces abstention.
    vu1, _, _ = derive(neural_case, evidence_complete=False, profile_dimension=2)
    vu2, _, _ = derive(neural_case, evidence_ambiguous=True, profile_dimension=2)
    vu3, _, _ = derive(neural_case, receipt_consistent=False, profile_dimension=2)
    assert vu1 == vu2 == vu3 == "UNDECIDED_FROM_CURRENT_EVIDENCE"

    # 7. Candidate-universe sensitivity: a scope-relative verdict can reverse.
    v_small, _, _ = derive([candidate("N", "NEURAL", (2, 2))], profile_dimension=2)
    v_large, _, _ = derive([
        candidate("N", "NEURAL", (2, 2)),
        candidate("P", "NON_NEURAL", (1, 1)),
    ], profile_dimension=2)
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
