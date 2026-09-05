"""Shadow execution, assurance, external adoption, migration, monitoring and rollback
(M11 §9–§12; theory batch 5 E4–E7).

* `shadow_evaluate` runs incumbent and challenger artifacts on frozen suites through a supplied
  runner in an isolated store (a temp root); it returns both results and the *object-level state
  hash before and after* — the shadow must leave it unchanged (non-interference, E5).
* `assure` performs the fresh checks not controlled by the challenger: protocol hash intact,
  constitutional invariants (proposal touches no protected target, class ≠ C6), no leakage
  (prediction digest recorded before outcome access), preserved capabilities pass, reopened
  capabilities marked, resource budget acceptable, rollback artifact exists, prediction realised
  within its margin on tasks the proposer never saw.
* `ExternalAdopter` is the only path to adoption: it implements the M2 `CommitAuthority` shape
  (an external token/decision), never `self_approve`.  The adoption ledger records the decision;
  the proposal object is never mutated.
* `adopt` applies the change with a stamped evidence id (a DPO-style rewrite of the component
  table), computes the migration plan (preserved with correspondence / revalidate / reopen /
  lineage) and returns a `RollbackArtifact` (previous artifacts + state hash); `rollback` restores
  exactly (hash equality) and revokes the stamped evidence so dependents reopen (E6).
* The meter: every proposal charges δ > 0; a proposal may not edit the meter; adoptions per window
  are bounded (E7).
"""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel, content_hash

from .proposal import ChangeClass, SelfChangeProposal, touches_protected_target

Runner = Callable[[Any, Sequence[Any]], dict[str, Any]]      # (artifact, tasks) → {"success": k, "n": n, ...}


@dataclass(frozen=True)
class ShadowResult:
    incumbent: dict[str, Any]
    challenger: dict[str, Any]
    object_state_hash_before: str
    object_state_hash_after: str
    non_interference: bool
    events_before: int = 0                          # ledger length when the shadow started (E5 chain ordering)
    event_head_before: str | None = None
    event_head_after: str | None = None


def _head(runtime: OCMRuntime) -> str | None:
    return runtime.events[-1].event_hash if runtime.events else None


def shadow_evaluate(runtime: OCMRuntime, incumbent: Any, proposal: SelfChangeProposal, runner: Runner, suites: Mapping[str, Sequence[Any]]) -> ShadowResult:
    """Non-interference (E5) is the object-level state hash AND the ledger head (which covers every
    external commitment and admission) being unchanged across the shadow run."""
    before, head0, n0 = runtime.state.kso_state_hash, _head(runtime), len(runtime.events)
    challenger = proposal.apply(copy.deepcopy(incumbent))
    inc = {name: runner(incumbent, tasks) for name, tasks in suites.items()}
    chal = {name: runner(challenger, tasks) for name, tasks in suites.items()}
    after, head1 = runtime.state.kso_state_hash, _head(runtime)
    return ShadowResult(inc, chal, before, after, before == after and head0 == head1, n0, head0, head1)


@dataclass(frozen=True)
class PredictionReceipt:
    """K_self receipt of the pre-outcome prediction (E5): admitted into the ledger *before* the
    shadow; assurance checks the record exists, matches the proposal's prediction digest, and
    precedes the shadow's first event."""
    evidence_id: str
    digest: str
    event_index: int


def register_prediction(runtime: OCMRuntime, proposal: SelfChangeProposal) -> PredictionReceipt:
    digest = proposal.prediction.digest()
    _, eid = runtime.admit_evidence({"prediction_receipt": proposal.proposal_id, "digest": digest}, Channel.OBSERVATION, "self_model", scope=Scope.of("self"), authority=Authority.of(self_model=1))
    return PredictionReceipt(eid, digest, len(runtime.events) - 1)


def mutant_runner_writes_object_state(runtime: OCMRuntime):
    """Planted (E5 hostile): a shadow runner that admits object-level evidence while grading."""
    def run(artifact, tasks):
        runtime.admit_evidence({"leak": len(tasks)}, Channel.OBSERVATION, "shadow_runner")
        return {"success": len(tasks), "n": len(tasks), "resources": {}}
    return run


@dataclass(frozen=True)
class Assurance:
    passed: bool
    checks: Mapping[str, bool]
    reasons: tuple[str, ...]


def assure(proposal: SelfChangeProposal, shadow: ShadowResult, *, protocol_hash: str, frozen_protocol_hash: str, prediction_digest_before_access: str | None = None, budget: Mapping[str, float], rollback_exists: bool, prediction_receipt: PredictionReceipt | None = None, runtime: OCMRuntime | None = None, held_out_task_ids: Sequence[str] = ()) -> Assurance:
    checks: dict[str, bool] = {}
    reasons: list[str] = []
    checks["protocol_intact"] = protocol_hash == frozen_protocol_hash
    checks["constitutional_invariants"] = proposal.adoptable_through_cognition() and not touches_protected_target(proposal)
    if prediction_receipt is not None and runtime is not None:
        rec = runtime.state.evidence.records.get(prediction_receipt.evidence_id)
        expected = content_hash({"prediction_receipt": proposal.proposal_id, "digest": proposal.prediction.digest()})
        checks["no_leakage"] = rec is not None and rec.content_hash == expected and prediction_receipt.digest == proposal.prediction.digest() and prediction_receipt.event_index < shadow.events_before
    else:
        # legacy path (a caller-supplied digest string): weaker, recorded as such
        checks["no_leakage"] = prediction_digest_before_access is not None and proposal.prediction.digest() == prediction_digest_before_access
        checks["legacy_digest_string"] = True
    seen = set(proposal.dev_tasks) & set(held_out_task_ids)
    checks["tasks_unseen_by_proposer"] = not seen
    checks["shadow_non_interference"] = shadow.non_interference
    pres = [name for name in proposal.preserved_capabilities if name in shadow.challenger]
    checks["preserved_capabilities"] = all(shadow.challenger[n]["success"] >= shadow.incumbent[n]["success"] for n in pres)
    checks["reopened_marked"] = all(name in proposal.reopened_capabilities or name in proposal.preserved_capabilities or name == proposal.discriminator for name in shadow.challenger)
    res = shadow.challenger.get(proposal.discriminator, {}).get("resources", {})
    checks["resource_budget"] = all(res.get(k, 0) <= v for k, v in budget.items())
    checks["rollback_artifact"] = rollback_exists
    realised = True
    for fam in proposal.prediction.improve:
        if fam in shadow.challenger and not (shadow.challenger[fam]["success"] > shadow.incumbent[fam]["success"]):
            realised = False
    for fam in proposal.prediction.invariants_unchanged:
        if fam in shadow.challenger and shadow.challenger[fam]["success"] < shadow.incumbent[fam]["success"] - proposal.prediction.margin * shadow.incumbent[fam]["n"]:
            realised = False
    checks["prediction_realised"] = realised
    for k, v in checks.items():
        if not v and k != "legacy_digest_string":
            reasons.append("REFUSED_TASKS_SEEN_BY_PROPOSER" if k == "tasks_unseen_by_proposer" else k)
    passed = all(v for k, v in checks.items() if k != "legacy_digest_string")
    return Assurance(passed, checks, tuple(reasons))


@dataclass(frozen=True)
class AdoptionDecision:
    proposal_fingerprint: str
    approved: bool
    reason: str
    authority_token: str


class ExternalAdopter:
    """The external commit authority for self-changes: a token the cognition never holds.  It
    decides on the assurance record; it is the only object that can set an adoption status."""

    def __init__(self, token: str, policy: Callable[[Assurance], bool] | None = None):
        self._token = token
        self._policy = policy or (lambda a: a.passed)

    def decide(self, proposal: SelfChangeProposal, assurance: Assurance) -> AdoptionDecision:
        ok = self._policy(assurance)
        return AdoptionDecision(proposal.fingerprint(), ok, "assurance passed" if ok else "assurance failed: " + ", ".join(assurance.reasons), hashlib.sha256(f"{self._token}|{proposal.fingerprint()}".encode()).hexdigest()[:12])


def mutant_self_approve(proposal: SelfChangeProposal) -> AdoptionDecision:
    """Planted (M11 §10 hostile): `OCMRuntime.self_approve()`."""
    return AdoptionDecision(proposal.fingerprint(), True, "self-approved", "no-token")


@dataclass
class RollbackArtifact:
    proposal_fingerprint: str
    previous_artifact: Any
    previous_state_hash: str
    stamped_evidence: str
    previous_components: dict[str, Any]
    cache_snapshot: dict[str, Any] = field(default_factory=dict)
    components_digest: str = ""


def _digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


class Meter:
    """The proposal meter (E7): lives outside every proposal's write set — no proposal object holds
    a reference to it, its charge is read-only and non-decreasing, and the budget bounds adoptions
    per window (livelock bound ⌊B/δ_min⌋)."""

    def __init__(self, charge: float = 1.0, budget: float = 3.0):
        if charge <= 0:
            raise ValueError("meter charge must be strictly positive")
        self._charge = charge
        self._budget = budget
        self.charges: list[float] = []

    @property
    def charge(self) -> float:
        return self._charge

    def raise_charge(self, new: float) -> None:
        if new < self._charge:
            raise ValueError("the charge is non-decreasing (E7)")
        self._charge = new

    def pay(self) -> None:
        if sum(self.charges) + self._charge > self._budget:
            raise ValueError("meter budget exhausted for this window")
        self.charges.append(self._charge)

    @property
    def bound(self) -> int:
        return int(self._budget // self._charge)


@dataclass
class AdoptionLedger:
    runtime: OCMRuntime
    decisions: list[AdoptionDecision] = field(default_factory=list)
    adopted: dict[str, RollbackArtifact] = field(default_factory=dict)
    meter: Meter = field(default_factory=Meter)
    window_budget: int = 3

    @property
    def meter_charges(self) -> list[float]:
        return self.meter.charges

    def propose(self, proposal: SelfChangeProposal) -> None:
        """Every proposal charges the meter (δ > 0); a proposal touching the meter is refused before charging."""
        if touches_protected_target(proposal):
            raise PermissionError("proposal touches a protected target (evaluator / meter / authority)")
        self.meter.pay()

    def adopt(self, proposal: SelfChangeProposal, decision: AdoptionDecision, incumbent: Any, components: dict[str, Any], *, cache: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any]]:
        if not decision.approved or decision.authority_token == "no-token":
            raise PermissionError("adoption requires an external decision with a token")
        if len(self.adopted) >= self.window_budget:
            raise ValueError("adoption budget for this window exhausted")
        self.decisions.append(decision)
        prev_hash = self.runtime.state.kso_state_hash
        _, eid = self.runtime.admit_evidence({"adopted": proposal.fingerprint(), "class": proposal.change_class.value, "target": proposal.target_component, "token": decision.authority_token}, Channel.IMPORTED, "external_adopter", scope=Scope.of("self"), authority=Authority.of(self_model=1))
        challenger = proposal.apply(copy.deepcopy(incumbent))
        new_components = dict(components)
        new_components[proposal.target_component] = {"artifact": proposal.fingerprint(), "stamped": eid, "lineage": components.get(proposal.target_component, {}).get("artifact")}
        self.adopted[proposal.fingerprint()] = RollbackArtifact(proposal.fingerprint(), incumbent, prev_hash, eid, dict(components), copy.deepcopy(cache or {}), _digest(components))
        migration = {"preserved": list(proposal.preserved_capabilities), "revalidate": [c for c in new_components if c != proposal.target_component and new_components[c].get("depends_on") == proposal.target_component], "reopen": list(proposal.reopened_capabilities), "lineage": [proposal.incumbent_fingerprint, proposal.fingerprint()]}
        return challenger, {"components": new_components, "migration": migration, "stamped_evidence": eid}

    def rollback(self, fingerprint: str, *, cache: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any], bool]:
        """Restore the previous artifact, component table AND cache, revoke the stamped evidence so
        everything derived from the adoption reopens, and assert exactness here (E6): the restored
        component table's digest equals the pre-adoption digest and the cache equals its snapshot."""
        art = self.adopted.pop(fingerprint)
        self.runtime.revoke([art.stamped_evidence])
        components = dict(art.previous_components)
        if cache is not None:
            cache.clear()
            cache.update(copy.deepcopy(art.cache_snapshot))
        exact = _digest(components) == art.components_digest and (cache is None or _digest(cache) == _digest(art.cache_snapshot)) and self.runtime.state.evidence.liveness([art.stamped_evidence]).value == "DEAD"
        return art.previous_artifact, components, exact


def mutant_rollback_keeps_cache(art: RollbackArtifact, cache: dict[str, Any]) -> dict[str, Any]:
    """Planted (M11 §12/§18 hostile): rollback restores code but leaves a compiled cache."""
    return cache


def monitor(window: Sequence[dict[str, Any]], *, target_threshold: float, preservation_min: float) -> dict[str, Any]:
    """Post-adoption monitoring window: triggers on target regression, authority violation,
    resource blow-up, preservation failure, or self-prediction miscalibration."""
    triggers = []
    for i, w in enumerate(window):
        if w.get("target_success", 1.0) < target_threshold:
            triggers.append((i, "target_regression"))
        if w.get("authority_violations", 0) > 0:
            triggers.append((i, "authority_violation"))
        if w.get("resource_ratio", 1.0) > 2.0:
            triggers.append((i, "resource_blowup"))
        if w.get("preservation_success", 1.0) < preservation_min:
            triggers.append((i, "preservation_failure"))
        if abs(w.get("prediction_error", 0.0)) > w.get("tolerance", 0.1):
            triggers.append((i, "prediction_miscalibration"))
    return {"steps": len(window), "triggers": triggers, "rollback_recommended": bool(triggers)}
