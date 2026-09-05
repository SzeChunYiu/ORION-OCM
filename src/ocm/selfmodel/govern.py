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
import math
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime, RuntimeRefusal
from ocm.store.event import EventStatus, EventType
from ocm.store.evidence import Channel, content_hash

from .proposal import ChangeClass, SelfChangeProposal, touches_protected_target
from . import rollback_data

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
    # Each arm/suite receives its own object and task copies. A runner mutating
    # an input cannot contaminate the frozen suite or the other comparison arm.
    inc = {name: runner(copy.deepcopy(incumbent), copy.deepcopy(tasks)) for name, tasks in suites.items()}
    chal = {name: runner(copy.deepcopy(challenger), copy.deepcopy(tasks)) for name, tasks in suites.items()}
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
        index = prediction_receipt.event_index
        event = runtime.events[index] if type(index) is int and 0 <= index < len(runtime.events) else None
        shadow_index = shadow.events_before
        shadow_head = runtime.events[shadow_index - 1].event_hash if type(shadow_index) is int and 0 < shadow_index <= len(runtime.events) else None
        checks["no_leakage"] = (
            rec is not None and rec.content_hash == expected and rec.source == "self_model"
            and runtime.state.evidence.liveness([prediction_receipt.evidence_id]).value == "LIVE"
            and prediction_receipt.digest == proposal.prediction.digest()
            and event is not None and event.event_type is EventType.EVIDENCE_ADMITTED
            and event.status is EventStatus.PASS and event.payload.get("source") == "self_model"
            and content_hash(event.payload.get("payload")) == expected
            and type(shadow_index) is int and 0 <= index < shadow_index
            and shadow_head == shadow.event_head_before
        )
    else:
        # legacy path (a caller-supplied digest string): weaker, recorded as such
        checks["no_leakage"] = prediction_digest_before_access is not None and proposal.prediction.digest() == prediction_digest_before_access
        checks["legacy_digest_string"] = True
    seen = set(proposal.dev_tasks) & set(held_out_task_ids)
    checks["tasks_unseen_by_proposer"] = not seen
    checks["shadow_non_interference"] = shadow.non_interference
    required = ({proposal.discriminator} | set(proposal.preserved_capabilities)
                | set(proposal.prediction.improve) | set(proposal.prediction.invariants_unchanged)
                | set(proposal.prediction.may_regress))

    def measured(row: Any) -> bool:
        return (isinstance(row, Mapping) and type(row.get("n")) is int and row["n"] > 0
                and type(row.get("success")) is int and 0 <= row["success"] <= row["n"])

    measured_all = all(measured(shadow.incumbent.get(n)) and measured(shadow.challenger.get(n))
                       and shadow.incumbent[n]["n"] == shadow.challenger[n]["n"] for n in required)
    checks["required_suites_measured"] = measured_all
    checks["preserved_capabilities"] = measured_all and all(shadow.challenger[n]["success"] >= shadow.incumbent[n]["success"] for n in proposal.preserved_capabilities)
    checks["reopened_marked"] = all(name in proposal.reopened_capabilities or name in proposal.preserved_capabilities or name == proposal.discriminator for name in shadow.challenger)
    discriminator_row = shadow.challenger.get(proposal.discriminator)
    res = discriminator_row.get("resources", {}) if isinstance(discriminator_row, Mapping) else None
    def nonnegative_number(value: Any) -> bool:
        return (type(value) is int and value >= 0) or (type(value) is float and math.isfinite(value) and value >= 0)

    checks["resource_budget"] = isinstance(res, Mapping) and all(
        nonnegative_number(v) and k in res and nonnegative_number(res[k]) and res[k] <= v
        for k, v in budget.items())
    checks["rollback_artifact"] = rollback_exists
    realised = measured_all and nonnegative_number(proposal.prediction.margin) and proposal.prediction.margin <= 1
    if realised:
        realised = all(shadow.challenger[fam]["success"] > shadow.incumbent[fam]["success"] for fam in proposal.prediction.improve)
        realised = realised and all(shadow.challenger[fam]["success"] >= shadow.incumbent[fam]["success"] - proposal.prediction.margin * shadow.incumbent[fam]["n"] for fam in proposal.prediction.invariants_unchanged)
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
        if type(charge) not in (int, float) or not math.isfinite(charge) or charge <= 0:
            raise ValueError("meter charge must be strictly positive")
        if type(budget) not in (int, float) or not math.isfinite(budget) or budget < 0:
            raise ValueError("meter budget must be finite and nonnegative")
        self._charge = charge
        self._budget = budget
        self.charges: list[float] = []

    @property
    def charge(self) -> float:
        return self._charge

    def raise_charge(self, new: float) -> None:
        if type(new) not in (int, float) or not math.isfinite(new) or new < self._charge:
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
    last_rollback: dict[str, Any] | None = None

    def __post_init__(self):
        charges = []
        for event in self.runtime.events:
            if (event.event_type is EventType.EVIDENCE_ADMITTED and event.status is EventStatus.PASS
                    and event.payload.get("source") == "host-proposal-meter.v1"):
                value = event.payload.get("payload", {}).get("charge")
                if type(value) not in (float, int) or not math.isfinite(value) or value <= 0:
                    raise RuntimeRefusal("CANNOT_CHECK_METER_HISTORY")
                charges.append(value)
        if charges:
            self.meter.charges[:] = charges
            self.meter.raise_charge(max(self.meter.charge, max(charges)))

    def persist(self) -> None:
        """The verified ledger and content-bound rollback files are authoritative."""
        self.runtime.persist()

    @classmethod
    def load(cls, runtime: OCMRuntime, *, meter: Meter | None = None):
        led = cls(runtime, meter=meter or Meter())
        for fp, record in led.adoption_history.items():
            if "decision" in record:
                led.decisions.append(AdoptionDecision(**record["decision"]))
            if not record["rollback_available"] or record["rollback_completed"]:
                continue
            data = rollback_data.read(runtime.root, record)
            led.adopted[fp] = RollbackArtifact(fp, data["previous_artifact"], data["previous_state_hash"],
                record["evidence_id"], data["previous_components"], data["cache_snapshot"], record["previous_components_digest"])
        return led

    @property
    def meter_charges(self) -> list[float]:
        return self.meter.charges

    @property
    def adoption_history(self) -> dict[str, dict[str, Any]]:
        """Durable metadata and verified data-only rollback availability."""
        records = {(r.source, r.content_hash): r for r in self.runtime.state.evidence.records.values()}
        history: dict[str, dict[str, Any]] = {}
        completed = self._completed_rollbacks()
        prepared = self._prepared_rollbacks()
        for ev in self.runtime.events:
            if ev.event_type is not EventType.EVIDENCE_ADMITTED or ev.status is not EventStatus.PASS or ev.payload.get("source") != "external_adopter":
                continue
            payload = ev.payload.get("payload", {})
            fingerprint = payload.get("adopted")
            if fingerprint is None:
                continue
            rec = records.get(("external_adopter", content_hash(payload)))
            if rec is not None:
                available = fingerprint in self.adopted
                if not available and fingerprint not in completed:
                    try:
                        rollback_data.read(self.runtime.root, payload)
                        available = True
                    except (OSError, ValueError, TypeError, KeyError, RecursionError):
                        pass
                history[fingerprint] = {**payload, "evidence_id": rec.evidence_id, "liveness": self.runtime.state.evidence.liveness([rec.evidence_id]).value, "rollback_available": available and fingerprint not in completed, "rollback_prepared": fingerprint in prepared, "rollback_completed": fingerprint in completed}
        return history

    def _rollback_states(self) -> tuple[set[str], set[str]]:
        """Validate ordered preparation and host acknowledgment against adoption."""
        records = {(r.source, r.content_hash): r for r in self.runtime.state.evidence.records.values()}
        adoptions: dict[str, tuple[dict[str, Any], str]] = {}
        revoked: set[str] = set()
        prepared: set[str] = set()
        acknowledged: set[str] = set()
        for ev in self.runtime.events:
            if ev.status is not EventStatus.PASS:
                continue
            if ev.event_type is EventType.EVIDENCE_REVOKED:
                revoked.update(ev.payload.get("evidence", ()))
            elif ev.event_type is EventType.EVIDENCE_REINSTATED:
                revoked.difference_update(ev.payload.get("evidence", ()))
            if ev.event_type is not EventType.EVIDENCE_ADMITTED:
                continue
            payload = ev.payload.get("payload")
            if not isinstance(payload, Mapping):
                continue
            source = ev.payload.get("source")
            rec = records.get((source, content_hash(payload)))
            if source == "external_adopter" and isinstance(payload.get("adopted"), str) and rec is not None:
                adoptions[payload["adopted"]] = (dict(payload), rec.evidence_id)
            if source not in ("external_adopter_rollback", "external_adopter_rollback_ack"):
                continue
            field = "rollback_prepared" if source == "external_adopter_rollback" else "rollback_acknowledged"
            fingerprint = payload.get(field)
            if not isinstance(fingerprint, str) or fingerprint not in adoptions:
                continue
            adoption, eid = adoptions[fingerprint]
            outstanding = [fp for fp in adoptions if fp not in acknowledged]
            if (not outstanding or outstanding[-1] != fingerprint or eid not in revoked
                    or payload.get("adoption_evidence") != eid
                    or payload.get("components_digest") != adoption.get("previous_components_digest")):
                continue
            if source == "external_adopter_rollback":
                prepared.add(fingerprint)
            elif fingerprint in prepared and payload.get("confirmation") == "HOST_REPORTED_INSTALLED":
                acknowledged.add(fingerprint)
        return prepared, acknowledged

    def _completed_rollbacks(self) -> set[str]:
        return self._rollback_states()[1]

    def _prepared_rollbacks(self) -> set[str]:
        return self._rollback_states()[0]

    def propose(self, proposal: SelfChangeProposal) -> None:
        """Every proposal charges the meter (δ > 0); a proposal touching the meter is refused before charging."""
        if touches_protected_target(proposal):
            raise PermissionError("proposal touches a protected target (evaluator / meter / authority)")
        self.meter.pay()
        try:
            self.runtime.admit_evidence({"proposal": proposal.fingerprint(), "charge": self.meter.charge,
                "sequence": len(self.runtime.events)}, Channel.OBSERVATION, "host-proposal-meter.v1")
        except Exception:
            self.meter.charges.pop()
            raise

    def adopt(self, proposal: SelfChangeProposal, decision: AdoptionDecision, incumbent: Any, components: dict[str, Any], *, cache: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any]]:
        if not decision.approved or decision.authority_token == "no-token":
            raise PermissionError("adoption requires an external decision with a token")
        if decision.proposal_fingerprint != proposal.fingerprint():
            raise PermissionError("external decision names another proposal")
        if not proposal.adoptable_through_cognition() or touches_protected_target(proposal):
            raise PermissionError("proposal touches a protected target (evaluator / meter / authority)")
        if components.get(proposal.target_component, {}).get("artifact") != proposal.incumbent_fingerprint:
            raise RuntimeRefusal("INCUMBENT_FINGERPRINT_MISMATCH", proposal.target_component)
        history = self.adoption_history
        if proposal.fingerprint() in history:
            raise RuntimeRefusal("ADOPTION_ALREADY_RECORDED", proposal.fingerprint())
        if any(record["rollback_prepared"] and not record["rollback_completed"] for record in history.values()):
            raise RuntimeRefusal("ADOPTION_BLOCKED_PENDING_ROLLBACK_ACK")
        if sum(record["liveness"] == "LIVE" for record in history.values()) >= self.window_budget:
            raise ValueError("adoption budget for this window exhausted")
        previous_artifact = copy.deepcopy(incumbent)
        previous_components = copy.deepcopy(components)
        previous_cache = copy.deepcopy(cache or {})
        prev_hash = self.runtime.state.kso_state_hash
        before = self.runtime._expectation()
        # Construct first: an exception is not a completed adoption. The callback
        # contract is pure; detect writes to this runtime instead of assuming it.
        challenger = proposal.apply(copy.deepcopy(incumbent))
        after = self.runtime._expectation()
        before.check(log_head=after.log_head, kso_state_hash=after.kso_state_hash, registry_revision=after.registry_revision, evidence_epoch=after.evidence_epoch)
        binding = rollback_data.write(self.runtime.root, {
            "schema": rollback_data.SCHEMA, "proposal_fingerprint": proposal.fingerprint(),
            "target": proposal.target_component, "incumbent": proposal.incumbent_fingerprint,
            "previous_artifact": previous_artifact, "previous_components": previous_components,
            "previous_state_hash": prev_hash, "cache_snapshot": previous_cache,
        })
        _, eid = self.runtime.admit_evidence({"adopted": proposal.fingerprint(), "class": proposal.change_class.value, "target": proposal.target_component, "token": decision.authority_token, "decision": vars(decision), "incumbent": proposal.incumbent_fingerprint, "previous_components_digest": _digest(previous_components), "rollback_data": binding}, Channel.IMPORTED, "external_adopter", scope=Scope.of("self"), authority=Authority.of(self_model=1))
        self.decisions.append(decision)
        new_components = copy.deepcopy(previous_components)
        new_components[proposal.target_component] = {"artifact": proposal.fingerprint(), "stamped": eid, "lineage": components.get(proposal.target_component, {}).get("artifact")}
        self.adopted[proposal.fingerprint()] = RollbackArtifact(proposal.fingerprint(), previous_artifact, prev_hash, eid, previous_components, previous_cache, _digest(previous_components))
        migration = {"preserved": list(proposal.preserved_capabilities), "revalidate": [c for c in new_components if c != proposal.target_component and new_components[c].get("depends_on") == proposal.target_component], "reopen": list(proposal.reopened_capabilities), "lineage": [proposal.incumbent_fingerprint, proposal.fingerprint()]}
        return challenger, {"components": new_components, "migration": migration, "stamped_evidence": eid}

    def rollback(self, fingerprint: str, *, cache: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any], bool]:
        """Prepare/re-deliver exact rollback data and restore a plain dict cache.

        This does not install executable artifacts. The host acknowledges actual
        installation separately; a crash before delivery leaves a retryable result.
        """
        if cache is not None and type(cache) is not dict:
            raise RuntimeRefusal("CANNOT_CHECK_ROLLBACK_CACHE_TYPE", "cache must be an exact built-in dict")
        history = self.adoption_history
        if fingerprint in self._completed_rollbacks():
            raise RuntimeRefusal("ROLLBACK_ALREADY_COMPLETED", fingerprint)
        art = self.adopted.get(fingerprint)
        if art is None:
            if fingerprint not in history:
                raise RuntimeRefusal("UNKNOWN_ADOPTION", fingerprint)
            record = history[fingerprint]
            try:
                data = rollback_data.read(self.runtime.root, record)
                art = RollbackArtifact(fingerprint, data["previous_artifact"], data["previous_state_hash"], record["evidence_id"], data["previous_components"], data["cache_snapshot"], record["previous_components_digest"])
            except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
                raise RuntimeRefusal("CANNOT_CHECK_ROLLBACK_ARTIFACT_UNAVAILABLE", fingerprint) from exc
        # This API restores an entire component table, so even adoptions on
        # different components must unwind in reverse order to preserve them.
        outstanding = [fp for fp, record in history.items() if not record["rollback_completed"]]
        if outstanding and outstanding[-1] != fingerprint:
            raise RuntimeRefusal("ROLLBACK_OUT_OF_ORDER", fingerprint)
        previous_artifact = copy.deepcopy(art.previous_artifact)
        components = copy.deepcopy(art.previous_components)
        restored_cache = copy.deepcopy(art.cache_snapshot) if cache is not None else None
        if _digest(components) != art.components_digest:
            raise RuntimeRefusal("CANNOT_CHECK_ROLLBACK_COMPONENTS_CHANGED", fingerprint)
        if not history[fingerprint]["rollback_prepared"]:
            self.runtime.revoke([art.stamped_evidence])
            # A preparation receipt never claims the caller installed the result.
            self.runtime.admit_evidence({"rollback_prepared": fingerprint, "adoption_evidence": art.stamped_evidence,
                                        "components_digest": art.components_digest}, Channel.IMPORTED,
                                       "external_adopter_rollback", scope=Scope.of("self"), authority=Authority.of(self_model=1))
        if cache is not None:
            cache.clear()
            cache.update(restored_cache)
        exact = _digest(components) == art.components_digest and (cache is None or _digest(cache) == _digest(art.cache_snapshot)) and self.runtime.state.evidence.liveness([art.stamped_evidence]).value == "DEAD"
        return previous_artifact, components, exact

    def acknowledge_rollback_installation(self, fingerprint: str, *, components: dict[str, Any], cache: dict[str, Any] | None = None) -> None:
        """Host-reported installation, bound to the exact prepared data/table.

        This is an explicit host acknowledgment, not a proof of executable code
        identity. It releases the next predecessor restoration in the LIFO order.
        """
        history = self.adoption_history
        record = history.get(fingerprint)
        if record is None or not record["rollback_prepared"]:
            raise RuntimeRefusal("ROLLBACK_NOT_PREPARED", fingerprint)
        if record["rollback_completed"]:
            return
        outstanding = [fp for fp, rec in history.items() if not rec["rollback_completed"]]
        if outstanding[-1] != fingerprint:
            raise RuntimeRefusal("ROLLBACK_OUT_OF_ORDER", fingerprint)
        if type(components) is not dict or _digest(components) != record["previous_components_digest"]:
            raise RuntimeRefusal("ROLLBACK_ACK_COMPONENTS_MISMATCH", fingerprint)
        art = self.adopted.get(fingerprint)
        try:
            expected_cache = art.cache_snapshot if art is not None else rollback_data.read(self.runtime.root, record)["cache_snapshot"]
        except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
            raise RuntimeRefusal("CANNOT_CHECK_ROLLBACK_ARTIFACT_UNAVAILABLE", fingerprint) from exc
        if ((expected_cache or cache is not None) and
                (type(cache) is not dict or _digest(cache) != _digest(expected_cache))):
            raise RuntimeRefusal("ROLLBACK_ACK_CACHE_MISMATCH", fingerprint)
        if self.runtime.state.evidence.liveness([record["evidence_id"]]).value != "DEAD":
            raise RuntimeRefusal("ROLLBACK_ACK_ADOPTION_NOT_REVOKED", fingerprint)
        self.runtime.admit_evidence({"rollback_acknowledged": fingerprint,
                                    "adoption_evidence": record["evidence_id"],
                                    "components_digest": record["previous_components_digest"],
                                    "confirmation": "HOST_REPORTED_INSTALLED"}, Channel.IMPORTED,
                                   "external_adopter_rollback_ack", scope=Scope.of("self"), authority=Authority.of(self_model=1))
        self.adopted.pop(fingerprint, None)


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
