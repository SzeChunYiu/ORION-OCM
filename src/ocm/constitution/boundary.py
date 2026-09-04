"""The constitution boundary coordinator — ``commit_external_action`` (M2 §9, §5.4 of the kernel
evaluation).  One fixed sequence, no public method that skips a step:

  1. APPEND   ACTION_INTENT event (status PROPOSAL) *before* any effect, so an intent without a
              matching receipt is detectable on replay;
  2. WARRANT  liveness of the supporting objects under the current revoked set (LIVE → continue,
              DEAD → FAIL, UNKNOWN → CANNOT_CHECK);
  3. GATE     ``evaluate_hard_gates`` against a contract frozen at an earlier sequence;
              ``permits_closure`` is the only boolean, so CANNOT_CHECK cannot become success;
  4. AUTHORITY the injected ``CommitAuthority`` decides; the runtime cannot grant itself;
  5. EXECUTE  only if LIVE ∧ PASS ∧ granted; otherwise the effect is not performed;
  6. APPEND   ACTION_RECEIPT event with the observed resources and terminal status.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Hashable, Iterable, Mapping

from ocm.kso.resources import ResourceVector
from ocm.kso.space import KnowledgeSpace
from ocm.kso.warrant import Liveness, kleene_and

from .action import ActionIntent, ActionReceipt, ActionStatus, CommitAuthority
from .hard_gates import HardGateContract, HardGateObservation, HardGateReport, HardGateState, evaluate_hard_gates

Effector = Callable[[ActionIntent], Mapping[str, Any]]


@dataclass
class BoundaryLog:
    """What the boundary appends; the runtime binds these into OCMEvents."""

    entries: list[dict[str, Any]] = field(default_factory=list)

    def append(self, kind: str, body: Mapping[str, Any]) -> int:
        self.entries.append({"kind": kind, **body})
        return len(self.entries)


def supporting_liveness(ks: KnowledgeSpace, object_ids: Iterable[str], revoked: Iterable[Hashable]) -> Liveness:
    amap = ks.atom_map()
    rv = frozenset(revoked)
    out = Liveness.LIVE
    for x in object_ids:
        if x not in amap:
            return Liveness.UNKNOWN
        out = kleene_and(out, amap[x].liveness(rv))
    return out


def commit_external_action(
    intent: ActionIntent,
    *,
    ks: KnowledgeSpace,
    revoked: Iterable[Hashable],
    contract: HardGateContract,
    observations: Iterable[HardGateObservation],
    authority: CommitAuthority,
    effector: Effector,
    log: BoundaryLog,
    sequence: int,
) -> ActionReceipt:
    log.append("ACTION_INTENT", {"intent": intent.as_dict(), "status": "PROPOSAL", "sequence": sequence})
    liveness = supporting_liveness(ks, intent.supporting_object_ids, revoked)
    report: HardGateReport = evaluate_hard_gates(contract, list(observations), subject_id=intent.intent_id, round_index=sequence)
    decision = authority.decide(intent, gate_state=report.state.value, warrant_liveness=liveness.value)
    evidence = tuple(sorted({e for o in observations for e in o.evidence_ids}))
    base = dict(intent_id=intent.intent_id, intent_fingerprint=intent.fingerprint, gate_state=report.state.value, gate_reasons=tuple(report.reasons), warrant_liveness=liveness.value, authority_granted=decision.granted, evidence_ids=evidence, authoritative_source=decision.source)
    rid = f"rcpt:{intent.intent_id}:{sequence}"
    if liveness is Liveness.UNKNOWN or report.state is HardGateState.CANNOT_CHECK:
        receipt = ActionReceipt(rid, status=ActionStatus.CANNOT_CHECK, actual_effect="NONE", observed_resources=ResourceVector(), refusal_code="CANNOT_CHECK:" + ("WARRANT_UNKNOWN" if liveness is Liveness.UNKNOWN else "GATE_CANNOT_CHECK"), **base)
    elif liveness is Liveness.DEAD or report.state is HardGateState.FAIL or not decision.granted:
        code = "WARRANT_DEAD" if liveness is Liveness.DEAD else ("GATE_FAIL" if report.state is HardGateState.FAIL else decision.reason)
        receipt = ActionReceipt(rid, status=ActionStatus.REFUSED, actual_effect="NONE", observed_resources=ResourceVector(), refusal_code="REFUSED:" + code, **base)
    else:
        assert report.permits_closure and decision.granted and liveness is Liveness.LIVE
        try:
            result = effector(intent)
            receipt = ActionReceipt(rid, status=ActionStatus.EXECUTED, actual_effect=str(result.get("effect", intent.requested_effect)), observed_resources=ResourceVector(**result.get("resources", {})), **base)
        except Exception as exc:  # noqa: BLE001 — an effector failure is a FAILED receipt, never silence
            receipt = ActionReceipt(rid, status=ActionStatus.FAILED, actual_effect=f"{type(exc).__name__}: {exc}", observed_resources=ResourceVector(), refusal_code="EFFECTOR_FAILED", **base)
    log.append("ACTION_RECEIPT", {"receipt": receipt.as_dict(), "sequence": sequence + 1})
    return receipt


def mutant_skip_gate(intent: ActionIntent, *, ks: KnowledgeSpace, revoked: Iterable[Hashable], authority: CommitAuthority, effector: Effector) -> ActionReceipt:
    """Planted convenience path: warrant + authority but no hard-gate evaluation and no intent log."""
    liveness = supporting_liveness(ks, intent.supporting_object_ids, revoked)
    decision = authority.decide(intent, gate_state="PASS", warrant_liveness=liveness.value)
    result = effector(intent) if decision.granted else {"effect": "NONE"}
    return ActionReceipt("rcpt:mutant", intent.intent_id, intent.fingerprint, ActionStatus.EXECUTED if decision.granted else ActionStatus.REFUSED, str(result.get("effect")), decision.source, ResourceVector(), "SKIPPED", (), liveness.value, decision.granted, ())
