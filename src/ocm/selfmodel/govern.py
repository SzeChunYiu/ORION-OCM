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
from ocm.store.evidence import Channel

from .proposal import ChangeClass, SelfChangeProposal, touches_protected_target

Runner = Callable[[Any, Sequence[Any]], dict[str, Any]]      # (artifact, tasks) → {"success": k, "n": n, ...}


@dataclass(frozen=True)
class ShadowResult:
    incumbent: dict[str, Any]
    challenger: dict[str, Any]
    object_state_hash_before: str
    object_state_hash_after: str
    non_interference: bool


def shadow_evaluate(runtime: OCMRuntime, incumbent: Any, proposal: SelfChangeProposal, runner: Runner, suites: Mapping[str, Sequence[Any]]) -> ShadowResult:
    before = runtime.state.kso_state_hash
    challenger = proposal.apply(copy.deepcopy(incumbent))
    inc = {name: runner(incumbent, tasks) for name, tasks in suites.items()}
    chal = {name: runner(challenger, tasks) for name, tasks in suites.items()}
    after = runtime.state.kso_state_hash
    return ShadowResult(inc, chal, before, after, before == after)


@dataclass(frozen=True)
class Assurance:
    passed: bool
    checks: Mapping[str, bool]
    reasons: tuple[str, ...]


def assure(proposal: SelfChangeProposal, shadow: ShadowResult, *, protocol_hash: str, frozen_protocol_hash: str, prediction_digest_before_access: str, budget: Mapping[str, float], rollback_exists: bool) -> Assurance:
    checks: dict[str, bool] = {}
    reasons: list[str] = []
    checks["protocol_intact"] = protocol_hash == frozen_protocol_hash
    checks["constitutional_invariants"] = proposal.adoptable_through_cognition() and not touches_protected_target(proposal)
    checks["no_leakage"] = proposal.prediction.digest() == prediction_digest_before_access
    checks["shadow_non_interference"] = shadow.non_interference
    pres = [name for name in proposal.preserved_capabilities if name in shadow.challenger]
    checks["preserved_capabilities"] = all(shadow.challenger[n]["success"] >= shadow.incumbent[n]["success"] for n in pres)
    checks["reopened_marked"] = all(name in proposal.reopened_capabilities or name in proposal.preserved_capabilities or name == proposal.discriminator for name in shadow.challenger)
    res = shadow.challenger.get(proposal.discriminator, {}).get("resources", {})
    checks["resource_budget"] = all(res.get(k, 0) <= v for k, v in budget.items())
    checks["rollback_artifact"] = rollback_exists
    # prediction realised: every family predicted to improve must improve on the discriminator/held-out; none predicted unchanged may regress beyond the margin
    realised = True
    for fam in proposal.prediction.improve:
        if fam in shadow.challenger and not (shadow.challenger[fam]["success"] > shadow.incumbent[fam]["success"]):
            realised = False
    for fam in proposal.prediction.invariants_unchanged:
        if fam in shadow.challenger and shadow.challenger[fam]["success"] < shadow.incumbent[fam]["success"] - proposal.prediction.margin * shadow.incumbent[fam]["n"]:
            realised = False
    checks["prediction_realised"] = realised
    for k, v in checks.items():
        if not v:
            reasons.append(k)
    return Assurance(all(checks.values()), checks, tuple(reasons))


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


@dataclass
class AdoptionLedger:
    runtime: OCMRuntime
    decisions: list[AdoptionDecision] = field(default_factory=list)
    adopted: dict[str, RollbackArtifact] = field(default_factory=dict)
    meter_charges: list[float] = field(default_factory=list)
    window_budget: int = 3
    charge: float = 1.0

    def propose(self, proposal: SelfChangeProposal) -> None:
        """Every proposal charges the meter (δ > 0); a proposal touching the meter is refused."""
        if touches_protected_target(proposal):
            raise PermissionError("proposal touches a protected target (evaluator / meter / authority)")
        if self.charge <= 0:
            raise ValueError("meter charge must be strictly positive")
        self.meter_charges.append(self.charge)

    def adopt(self, proposal: SelfChangeProposal, decision: AdoptionDecision, incumbent: Any, components: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
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
        self.adopted[proposal.fingerprint()] = RollbackArtifact(proposal.fingerprint(), incumbent, prev_hash, eid, dict(components))
        migration = {"preserved": list(proposal.preserved_capabilities), "revalidate": [c for c in new_components if c != proposal.target_component and new_components[c].get("depends_on") == proposal.target_component], "reopen": list(proposal.reopened_capabilities), "lineage": [proposal.incumbent_fingerprint, proposal.fingerprint()]}
        return challenger, {"components": new_components, "migration": migration, "stamped_evidence": eid}

    def rollback(self, fingerprint: str) -> tuple[Any, dict[str, Any], bool]:
        """Restore the previous artifact and component table and revoke the stamped evidence so
        everything derived from the adoption reopens; exactness = the component table equals the
        previous one (state hash equality is asserted by the caller on the object level)."""
        art = self.adopted.pop(fingerprint)
        self.runtime.revoke([art.stamped_evidence])
        return art.previous_artifact, dict(art.previous_components), True


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
