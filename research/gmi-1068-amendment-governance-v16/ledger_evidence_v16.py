"""Evidence checks use independently replayed inputs, never submitted totals."""
import hashlib
import json
from ledger_structure_v16 import validate_structure


def validate_evidence(ledger, target_contract, replayed_science_receipt, review_sha,
                      trusted_predecessor=None):
    state = validate_structure(ledger, trusted_predecessor, target_contract)
    encoded = json.dumps(replayed_science_receipt, indent=2, sort_keys=True) + "\n"
    expected = hashlib.sha256(encoded.encode()).hexdigest()
    statements = replayed_science_receipt["statements"]
    active = set(state["leaves"].values())
    for aid, attestation in state["attestations"].items():
        if (aid in state["retracted"] or attestation["verdict"] != "VERIFIED"
                or attestation["revision_id"] not in active):
            continue
        if (attestation["science_sha256"] != expected
                or attestation["review_sha256"] != review_sha):
            raise ValueError("attestation does not bind independently replayed evidence")
        for sid in attestation["statement_ids"]:
            spec = next(x for x in target_contract["statements"] if x["id"] == sid)
            if statements.get(sid) != {"status": "VERIFIED_AT_REGISTERED_SCOPE", "contract": spec}:
                raise ValueError("statement receipt mismatch")
    return derive_accounting(ledger, target_contract, trusted_predecessor)


def derive_accounting(ledger, target_contract, trusted_predecessor=None):
    """Structural current authority only; call validate_evidence for verified use."""
    state = validate_structure(ledger, trusted_predecessor, target_contract)
    active = set(state["leaves"].values())
    supported = {att["revision_id"] for aid, att in state["attestations"].items()
                 if aid not in state["retracted"] and att["verdict"] == "VERIFIED"}
    qualified = set()
    changed = True
    while changed:
        changed = False
        for rid in active & supported:
            deps = state["revisions"][rid]["dependency_revision_ids"]
            if rid not in qualified and all(dep in active and dep in qualified for dep in deps):
                qualified.add(rid)
                changed = True
    count = len(qualified)
    baseline = target_contract["accounting"]
    return {"original_total": baseline["original_total"],
            "original_fulfilled": baseline["original_fulfilled"],
            "original_unresolved": baseline["original_unresolved"],
            "refuted_reading_with_verified_active_replacement": count,
            "active_unresolved": baseline["original_unresolved"] - count,
            "active_revision_ids": sorted(active), "qualified_revision_ids": sorted(qualified),
            "overall_closure": "OPEN", "scientific_truth_certified": False}
