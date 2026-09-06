"""Fixed role-contract transfer checker, independent of OCM execution.

Compatibility exports remain in science.lifecycle. Role agreement is checked;
this does not prove a transferred program's semantic correctness.
"""
from typing import Mapping
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.work import contracts as WC

SCIENCE_ROLE_MAP = {"gather": "inspect_evidence", "classify": "diagnose", "check_policy": "check_assumptions", "act_smallest": "discriminating_experiment", "verify": "validate", "document": "report"}


def science_transfer_map(source: WC.Skill, science_ops: Mapping[str, WC.Operator], correspondence_evidence: str) -> WC.TransferMap:
    """Work roles → science roles; every science operator is registered under the *science* role,
    so the M9 transfer refuses a work-role operator masquerading (e.g. a work verifier bound as a
    statistical validation)."""
    mapping = {}
    for role in source.skeleton:
        target_role = SCIENCE_ROLE_MAP.get(role)
        op = next((o for o in science_ops if science_ops[o].role == target_role), None)
        if op:
            mapping[role] = op
    return WC.TransferMap(f"tm:{source.skill_id}->science", source.skill_id, "science", mapping, ("roles registered",), tuple(r for r in source.skeleton if r in mapping), tuple(r for r in source.skeleton if r not in mapping), dict(SCIENCE_ROLE_MAP), 0.4, ("withheld",), WarrantProfile.of({correspondence_evidence}))


def transported_science_skill(source: WC.Skill, tm: WC.TransferMap, science_ops: Mapping[str, WC.Operator]) -> tuple[WC.TransferVerdict, WC.Skill | None, str]:
    """Like M9 `transported_skill` but the role agreement is checked through the science role map."""
    if tm.correspondence_warrant.liveness(()) is Liveness.DEAD:
        return WC.TransferVerdict.REFUSE_TRANSFER, None, "correspondence dead"
    bindings = {}
    for role in source.skeleton:
        tgt = tm.role_mapping.get(role)
        if tgt is None or tgt not in science_ops:
            return WC.TransferVerdict.ADAPTER_REQUIRED, None, f"no science binding for {role}"
        if science_ops[tgt].role != SCIENCE_ROLE_MAP.get(role):
            return WC.TransferVerdict.REFUSE_TRANSFER, None, f"{tgt} is {science_ops[tgt].role}, not {SCIENCE_ROLE_MAP.get(role)}"
        bindings[role] = tgt
    return WC.TransferVerdict.TRANSFER, WC.Skill(f"{source.skill_id}->science", source.skeleton, bindings, "science", tm.warrant(source), dict(tm.adapter), source.known_failures, source.lineage + (tm.transfer_id,)), "ok"


