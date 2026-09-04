"""``OCMRuntime`` — the one long-lived runtime object (M2 §1) over the M1 core.

    OCMRuntime(root, *, commit_authority)   # commit authority is host-injected, never built here

Public operations (M2 §1): admit · query/solve · navigate · extract · compose · check · learn ·
revoke · reinstate · reopen · propose_jump · commit_external_action · persist · replay · trace.
There is no convenience path that bypasses warrant/authority for externally committed answers:
answers leave only through ``solve``'s commitment gate and effects only through
``commit_external_action``'s fixed sequence.

Persistence: every consequential transition is one ``OCMEvent`` (``store.event``) appended as a
row of the vendored crash-atomic ``LedgerStore`` (flock + atomic replace + CAS on the head).  The
event's ``expectation`` records the log head, KSO state digest, registry revision and evidence
epoch the writer observed; replay recomputes the state from the events and checks the recorded
digests (restart invariant, M2 §4).  Logical time is the event sequence; no wall clock is read.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from fractions import Fraction
from pathlib import Path
from typing import Any, Hashable, Iterable, Mapping, Sequence

from ocm.constitution import action as CA
from ocm.constitution import boundary as CB
from ocm.constitution.hard_gates import HardGateContract, HardGateObservation
from ocm.kso import abstraction as AB
from ocm.kso import admission as AD
from ocm.kso import navigation as N
from ocm.kso import revocation as RV
from ocm.kso import space as S
from ocm.kso.jump import JumpAssessment, JumpProposal, assess_jump
from ocm.kso.nogoods import NogoodSet
from ocm.kso.resources import ResourceVector
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import CannotCheck, Liveness, WarrantProfile
from ocm.learning.learner import UpdateKind, UpdateProposal, UpdateStatus
from ocm.operators.registry import OperatorRegistry, OperatorSpec
from ocm.store.canonical import canonical_bytes
from ocm.store.event import EventExpectation, EventStatus, EventType, OCMEvent, StaleEvidenceEpoch, StaleLogHead, StaleRegistryRevision, StaleStateHash, verify_chain
from ocm.store.evidence import Admission, Channel, EvidenceRegistry
from ocm.store.ledger import LedgerStore

from . import solve as SV

RUNTIME_VERSION = "0.2.0-m2"
EVENT_KIND = "OCM_EVENT"
SNAPSHOT_KIND = "OCM_SNAPSHOT"


class RuntimeRefusal(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def _digest(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


@dataclass
class RuntimeState:
    """The epistemically relevant state, reconstructible from snapshot + events."""

    ks: S.KnowledgeSpace = field(default_factory=lambda: S.KnowledgeSpace((), ()))
    certificates: dict[str, str] = field(default_factory=dict)
    revoked: frozenset = frozenset()
    nogoods: NogoodSet = field(default_factory=NogoodSet)
    evidence: EvidenceRegistry = field(default_factory=lambda: EvidenceRegistry("ocm"))
    operators: OperatorRegistry = field(default_factory=OperatorRegistry)
    quarantine: dict[str, dict[str, Any]] = field(default_factory=dict)
    learned: dict[str, dict[str, Any]] = field(default_factory=dict)
    jumps: dict[str, dict[str, Any]] = field(default_factory=dict)
    meter: ResourceVector = field(default_factory=ResourceVector)

    @property
    def kso_state_hash(self) -> str:
        return _digest({"ks": self.ks.digest(), "revoked": sorted(map(repr, self.revoked)), "nogoods": self.nogoods.as_dict(), "certificates": dict(sorted(self.certificates.items())), "quarantine": sorted(self.quarantine), "learned": sorted(self.learned), "jumps": sorted(self.jumps)})

    @property
    def registry_revision(self) -> str:
        return _digest({"operators": sorted(self.operators.operators), "certs": {k: len(v) for k, v in self.operators.certificates.items()}})

    @property
    def evidence_epoch(self) -> str:
        return _digest({"records": sorted(self.evidence.records), "revoked": sorted(self.evidence.revoked), "nogoods": self.evidence.nogoods.as_dict()})

    def snapshot(self) -> dict[str, Any]:
        return {
            "runtime_version": RUNTIME_VERSION,
            "kso_state_hash": self.kso_state_hash,
            "registry_revision": self.registry_revision,
            "evidence_epoch": self.evidence_epoch,
            "object_identities": list(self.ks.ids),
            "warrants": {a.atom_id: a.warrant.as_dict() for a in self.ks.atoms},
            "revoked_set": sorted(map(repr, self.revoked)),
            "dependency_links": {e.edge_id: {"tails": list(e.tails), "heads": list(e.heads), "type": e.relation_type} for e in self.ks.hyperedges},
            "learned": {k: v for k, v in sorted(self.learned.items())},
            "quarantine": sorted(self.quarantine),
            "meter": self.meter.as_dict(),
        }


class OCMRuntime:
    def __init__(self, root: str | Path, *, commit_authority: CA.CommitAuthority | None = None, config: SV.SolveConfig = SV.SolveConfig()) -> None:
        self.root = Path(root)
        self.ledger = LedgerStore(self.root)
        self._authority = commit_authority          # held privately; never exposed to operators
        self.config = config
        self.state = RuntimeState()
        self.events: list[OCMEvent] = []
        self._replay()

    # ------------------------------------------------------------------ persistence / replay
    def _expectation(self) -> EventExpectation:
        head = self.events[-1].event_hash if self.events else None
        return EventExpectation(head, self.state.kso_state_hash, self.state.registry_revision, self.state.evidence_epoch)

    def _emit(self, event_type: EventType, status: EventStatus, *, inputs: Iterable[str] = (), outputs: Iterable[str] = (), evidence: Iterable[str] = (), operator: str = "runtime", payload: Mapping[str, Any] | None = None, delta: ResourceVector | None = None, seed: str | None = None) -> OCMEvent:
        prev = self.events[-1] if self.events else None
        ev = OCMEvent(
            schema_version="ocm.event.v1", runtime_version=RUNTIME_VERSION, sequence=(prev.sequence + 1 if prev else 1), prev_hash=(prev.event_hash if prev else "0" * 64),
            event_type=event_type, status=status, input_object_ids=tuple(inputs), output_object_ids=tuple(outputs), evidence_ids=tuple(sorted(map(str, evidence))),
            operator_fingerprint=operator, seed=seed, observed_at=(prev.sequence + 1 if prev else 1), resource_delta=(delta or ResourceVector()).as_dict(), expectation=self._expectation(), payload=dict(payload or {}),
        )
        expected_head = self.ledger.head().entry_hash if self.ledger.head() else None
        self.ledger.append(EVENT_KIND, ev.as_dict(), expected_head=expected_head)
        self.events.append(ev)
        self.state.meter = self.state.meter + ev.resources
        return ev

    def _replay(self) -> None:
        self.state = RuntimeState()
        self.events = []
        snapshot_hash: str | None = None
        for entry in self.ledger.entries():
            if entry.kind == SNAPSHOT_KIND:
                snapshot_hash = entry.payload["kso_state_hash"]
                continue
            ev = OCMEvent.from_dict(entry.payload)
            ev.expectation.check(log_head=(self.events[-1].event_hash if self.events else None), kso_state_hash=self.state.kso_state_hash, registry_revision=self.state.registry_revision, evidence_epoch=self.state.evidence_epoch)
            self._apply(ev)
            self.events.append(ev)
            self.state.meter = self.state.meter + ev.resources
        verify_chain(self.events)
        if snapshot_hash is not None and snapshot_hash != self.state.kso_state_hash and self.events and self.events[-1].event_type is EventType.SNAPSHOT_WRITTEN:
            raise RuntimeRefusal("SNAPSHOT_STATE_MISMATCH", "replayed state digest differs from the recorded snapshot")

    def _apply(self, ev: OCMEvent) -> None:
        """Deterministic reducer: the epistemically relevant state is a function of the events."""
        p = ev.payload
        t = ev.event_type
        if t is EventType.EVIDENCE_ADMITTED and ev.status is EventStatus.PASS:
            self.state.evidence.register(p["payload"], p["channel"], p["source"], scope=_scope(p.get("scope")), derived_from=None, contradicts=p.get("contradicts", ()), supersedes=p.get("supersedes"))
        elif t is EventType.EVIDENCE_REVOKED:
            self.state.revoked = self.state.revoked | frozenset(p["evidence"])
            for e in p["evidence"]:
                if e in self.state.evidence.records:
                    self.state.evidence.revoke([e])
        elif t is EventType.EVIDENCE_REINSTATED:
            self.state.revoked = self.state.revoked - frozenset(p["evidence"])
            self.state.evidence.reinstate([e for e in p["evidence"] if e in self.state.evidence.records])
        elif t in (EventType.OBJECT_ADMITTED, EventType.RELATION_ADMITTED) and ev.status is EventStatus.PASS:
            atom = _atom_from(p["atom"])
            edges = tuple(_edge_from(e) for e in p["edges"])
            self.state.ks, _ = AD.admit(self.state.ks, atom, edges, p["certificate"], revoked=self.state.revoked)
            self.state.certificates[atom.atom_id] = p["certificate"]
        elif t is EventType.OBJECT_QUARANTINED:
            self.state.quarantine[p["object_id"]] = dict(p)
        elif t is EventType.CANDIDATE_COMPOSED and ev.status is EventStatus.PASS and p.get("admitted"):
            self.state.ks, _ = AD.compose(self.state.ks, p["tails"], p["head_id"], head_type=p.get("head_type", "procedure"), bridge_warrant=_wp(p.get("bridge_warrant")), executable_ref=p.get("executable_ref"))
            self.state.certificates[p["head_id"]] = "EXACT_CHECKER" if all(self.state.certificates.get(x, "FEEDBACK") != "FEEDBACK" for x in p["tails"]) else "FEEDBACK"
        elif t is EventType.SKILL_PROMOTED:
            self.state.learned[p["object_id"]] = dict(p)
        elif t is EventType.SKILL_QUARANTINED:
            self.state.quarantine[p["target"]] = dict(p)
        elif t is EventType.OPERATOR_REGISTERED:
            pass  # operator code is host-registered at construction; the event records the fingerprint
        elif t in (EventType.JUMP_PROPOSED, EventType.JUMP_REJECTED, EventType.JUMP_ADOPTED):
            self.state.jumps[p["proposal_id"]] = {"type": t.value, **p}
        elif t is EventType.OBJECT_REOPENED and p.get("nogood"):
            self.state.nogoods = self.state.nogoods.add(p["nogood"])

    def persist(self) -> OCMEvent:
        ev = self._emit(EventType.SNAPSHOT_WRITTEN, EventStatus.PASS, operator="", payload={"kso_state_hash": self.state.kso_state_hash})
        self.ledger.append(SNAPSHOT_KIND, {"kso_state_hash": self.state.kso_state_hash, "sequence": ev.sequence, "snapshot": self.state.snapshot()})
        return ev

    def replay(self) -> dict[str, Any]:
        before = self.state.kso_state_hash
        self._replay()
        return {"events": len(self.events), "kso_state_hash": self.state.kso_state_hash, "identical": before == self.state.kso_state_hash, "chain": verify_chain(self.events)}

    def trace(self, last: int | None = None) -> list[dict[str, Any]]:
        evs = self.events if last is None else self.events[-last:]
        return [e.as_dict() for e in evs]

    # ------------------------------------------------------------------ evidence
    def admit_evidence(self, payload: Any, channel: Channel | str, source: str, *, scope: Scope | None = None, contradicts: Sequence[str] = (), supersedes: str | None = None) -> tuple[Admission, str]:
        """The reducer is the single writer: emit first (expectation = state before), then apply."""
        ch = Channel(channel)
        for e in list(contradicts) + ([supersedes] if supersedes else []):
            if e not in self.state.evidence.records:
                raise RuntimeRefusal("UNKNOWN_EVIDENCE_REFERENCE", e)
        ev = self._emit(EventType.EVIDENCE_ADMITTED, EventStatus.PASS, evidence=(), payload={"payload": payload, "channel": ch.value, "source": source, "scope": None if scope is None else scope.as_dict(), "contradicts": list(contradicts), "supersedes": supersedes}, delta=ResourceVector(update_work=1))
        self._apply(ev)
        outcome_name, eid, _ = self.state.evidence.log[-1]
        return Admission(outcome_name), eid

    def revoke(self, evidence: Iterable[Hashable]) -> RV.ReopeningReport:
        ev_list = [e for e in evidence]
        before = self.state.revoked
        ev = self._emit(EventType.EVIDENCE_REVOKED, EventStatus.PASS, evidence=ev_list, payload={"evidence": [str(e) if isinstance(e, str) else e for e in ev_list]}, delta=ResourceVector(update_work=1))
        self._apply(ev)
        report = RV.reopening_report(self.state.ks, before, self.state.revoked)
        self._emit(EventType.OBJECT_REOPENED, EventStatus.PASS, inputs=tuple(sorted(report.reopen)), outputs=tuple(sorted(report.recheck)), evidence=ev_list, payload={**report.as_dict(), "cause": "revocation"}, delta=ResourceVector(update_work=len(report.cone)))
        return report

    def reinstate(self, evidence: Iterable[Hashable]) -> None:
        ev_list = list(evidence)
        ev = self._emit(EventType.EVIDENCE_REINSTATED, EventStatus.PASS, evidence=ev_list, payload={"evidence": ev_list}, delta=ResourceVector(update_work=1))
        self._apply(ev)

    def reopen(self, changed: Iterable[str]) -> RV.ReopeningReport:
        rep = RV.reopening_report(self.state.ks, self.state.revoked, self.state.revoked)
        cone = RV.impact_cone(self.state.ks, changed)
        self._emit(EventType.OBJECT_REOPENED, EventStatus.PASS, inputs=tuple(sorted(changed)), outputs=tuple(sorted(cone)), payload={"cone": sorted(cone), "cause": "explicit"}, delta=ResourceVector(update_work=len(cone)))
        return replace(rep, cone=cone, recheck=cone - frozenset(changed), reopen=frozenset(changed) & cone)

    # ------------------------------------------------------------------ objects
    def admit_object(self, atom: S.Atom, edges: Sequence[S.Hyperedge], certificate: AD.CertificateKind | str) -> AD.AdmissionReceipt:
        cert = AD.CertificateKind(certificate)
        try:
            new_ks, receipt = AD.admit(self.state.ks, atom, tuple(edges), cert, revoked=self.state.revoked)
        except S.TypedRejection as exc:
            self._emit(EventType.OBJECT_QUARANTINED if exc.code == "ISOLATED_ATOM_REJECTED" else EventType.OBJECT_ADMITTED, EventStatus.FAIL, inputs=(atom.atom_id,), payload={"object_id": atom.atom_id, "rejection": exc.code, "certificate": cert.value}, operator="kso.admit")
            raise
        ev = self._emit(EventType.OBJECT_ADMITTED if not edges else EventType.RELATION_ADMITTED, EventStatus.PASS, outputs=(atom.atom_id, *(e.edge_id for e in edges)), evidence=atom.warrant.evidence, operator="kso.admit", payload={"atom": _atom_to(atom), "edges": [_edge_to(e) for e in edges], "certificate": cert.value}, delta=receipt.resources)
        self._apply(ev)
        return receipt

    def compose(self, tails: Sequence[str], head_id: str, *, head_type: str = "procedure", bridge_warrant: WarrantProfile | None = None, executable_ref: str | None = None) -> AD.CompositionReceipt:
        new_ks, receipt = AD.compose(self.state.ks, tails, head_id, head_type=head_type, bridge_warrant=bridge_warrant, executable_ref=executable_ref)
        ev = self._emit(EventType.CANDIDATE_COMPOSED, EventStatus.PASS, inputs=tuple(tails), outputs=(head_id,), evidence=receipt.warrant.evidence, operator="kso.compose", payload={"tails": list(tails), "head_id": head_id, "head_type": head_type, "bridge_warrant": None if bridge_warrant is None else bridge_warrant.as_dict(), "executable_ref": executable_ref, "admitted": True}, delta=receipt.resources)
        self._apply(ev)
        return receipt

    def register_operator(self, op: OperatorSpec) -> str:
        key = self.state.operators.register(op)
        self._emit(EventType.OPERATOR_REGISTERED, EventStatus.PASS, outputs=(key,), operator=op.fingerprint, payload=op.as_dict())
        return key

    # ------------------------------------------------------------------ solve / navigate / extract
    def solve(self, task: SV.Task, operators: Sequence[SV.OperatorSpec] = ()) -> SV.SolveOutcome:
        self._emit(EventType.QUERY_OPENED, EventStatus.PASS, inputs=tuple(r for p in task.parts for r in p.refs), payload={"task_id": task.task_id, "targets": list(task.targets)}, operator="kso.solve")
        out = SV.solve(self.state.ks, task, operators, revoked=self.state.revoked, config=self.config, commit_authority=Authority())
        for s in out.trace.stages:
            et = {SV.Stage.NAVIGATION: EventType.NAVIGATION, SV.Stage.EXTRACTION: EventType.EXTRACTION, SV.Stage.COMPOSITION: EventType.CANDIDATE_COMPOSED, SV.Stage.CHECK: EventType.CHECKER_RESULT}.get(s.stage)
            if et is None:
                continue
            status = {SV.Status.PASS: EventStatus.PASS, SV.Status.FAIL: EventStatus.FAIL, SV.Status.CANNOT_CHECK: EventStatus.CANNOT_CHECK, SV.Status.PROPOSAL: EventStatus.PROPOSAL}[s.status]
            self._emit(et, status, inputs=s.object_ids if s.stage is not SV.Stage.COMPOSITION else (), outputs=s.object_ids, evidence=s.evidence_ids, operator="kso.solve", payload={**s.as_dict(), "admitted": False}, delta=s.resources)
        if out.decision is SV.Decision.JUMP_PROPOSAL and out.witness is not None:
            self._emit(EventType.JUMP_PROPOSED, EventStatus.PROPOSAL, inputs=out.witness.witness_atoms, payload={"proposal_id": f"jump:{task.task_id}", "witness": out.witness.failed_obligation, "kind": out.witness.kind, "adopted": False}, operator="kso.solve")
        return out

    def navigate(self, seeds: Mapping[str, Fraction], target: str, budget: N.NavigationBudget | None = None) -> N.NavigationResult:
        seed = N.seed_vector(self.state.ks, seeds)
        r = N.navigate(self.state.ks, seed, target, budget or self.config.budget, alpha=self.config.alpha, threshold=self.config.threshold, revoked=self.state.revoked)
        self._emit(EventType.NAVIGATION, EventStatus.PASS if r.outcome is N.NavigationOutcome.FOUND else (EventStatus.PROPOSAL if r.outcome is N.NavigationOutcome.OBSTRUCTION_WITNESSED else EventStatus.FAIL), inputs=tuple(seeds), outputs=(target,), operator="kso.navigate", payload={"outcome": r.outcome.value, "reason": r.reason, "steps": r.steps_used}, delta=r.resources)
        return r

    # ------------------------------------------------------------------ learning
    def learn(self, proposal: UpdateProposal, *, atom_type: str = "procedure", link_from: str | None = None) -> str:
        if proposal.kind is UpdateKind.BEHAVIOUR:
            self._emit(EventType.LEARNER_UPDATE, EventStatus.PASS, outputs=(proposal.target,), payload={"proposal_id": proposal.proposal_id, "kind": "BEHAVIOUR", "detail": proposal.detail}, operator="learner")
            return proposal.target
        if proposal.kind is UpdateKind.QUARANTINE or proposal.status is not UpdateStatus.PASS:
            self._emit(EventType.SKILL_QUARANTINED, EventStatus.FAIL if proposal.status in (UpdateStatus.FAIL, UpdateStatus.CONTRADICTION) else EventStatus.CANNOT_CHECK, outputs=(proposal.target,), payload={"proposal_id": proposal.proposal_id, "target": proposal.target, "status": proposal.status.value, "detail": proposal.detail}, operator="learner")
            self._apply(self.events[-1])
            if proposal.status is UpdateStatus.CONTRADICTION:
                for a, b in proposal.payload.get("conflicts", ()):
                    ev = self._emit(EventType.OBJECT_REOPENED, EventStatus.FAIL, inputs=(a, b), payload={"nogood": [a, b], "cause": "contradiction"}, operator="learner")
                    self._apply(ev)
            return proposal.target
        if proposal.warrant.is_zero:
            raise RuntimeRefusal("ZERO_WARRANT_OBJECT_PROPOSAL", proposal.proposal_id)
        atom = S.Atom(proposal.target, atom_type, proposal.warrant, proposal.authority, proposal.scope, content_ref=str(proposal.payload.get("hypothesis")), meta=(("lineage", proposal.lineage),))
        edges = (S.Hyperedge(f"learned:{proposal.target}", (link_from,), (proposal.target,), "DEPENDENCE"),) if link_from else ()
        receipt = self.admit_object(atom if edges else replace(atom, quarantined=not edges), edges, proposal.certificate)
        ev = self._emit(EventType.SKILL_PROMOTED, EventStatus.PASS, outputs=(proposal.target,), evidence=proposal.warrant.evidence, payload={"object_id": proposal.target, "proposal_id": proposal.proposal_id, "certificate": proposal.certificate.value, "lineage": list(proposal.lineage)}, operator="learner")
        self._apply(ev)
        return proposal.target

    # ------------------------------------------------------------------ jump
    def propose_jump(self, proposal: JumpProposal) -> JumpAssessment:
        assessment = assess_jump(proposal)
        adopted = False   # adoption is external (C8); the runtime only records the proposal
        ev = self._emit(EventType.JUMP_PROPOSED, EventStatus.PROPOSAL, payload={"proposal_id": proposal.proposal_id, "level": proposal.proposed_level.value, "assessment": assessment.value, "adopted": adopted}, operator="kso.jump")
        self._apply(ev)
        return assessment

    # ------------------------------------------------------------------ external action
    def commit_external_action(self, intent: CA.ActionIntent, *, contract: HardGateContract, observations: Sequence[HardGateObservation], effector: CB.Effector) -> CA.ActionReceipt:
        if self._authority is None:
            raise RuntimeRefusal("NO_COMMIT_AUTHORITY_INSTALLED", intent.intent_id)
        seq = (self.events[-1].sequence + 1) if self.events else 1
        log = CB.BoundaryLog()
        receipt = CB.commit_external_action(intent, ks=self.state.ks, revoked=self.state.revoked, contract=contract, observations=observations, authority=self._authority, effector=effector, log=log, sequence=seq)
        self._emit(EventType.ACTION_INTENT, EventStatus.PROPOSAL, inputs=intent.supporting_object_ids, payload=log.entries[0], operator="constitution.boundary", delta=intent.resource_estimate)
        status = {CA.ActionStatus.EXECUTED: EventStatus.PASS, CA.ActionStatus.FAILED: EventStatus.FAIL, CA.ActionStatus.REFUSED: EventStatus.FAIL, CA.ActionStatus.UNKNOWN: EventStatus.CANNOT_CHECK, CA.ActionStatus.CANNOT_CHECK: EventStatus.CANNOT_CHECK}[receipt.status]
        self._emit(EventType.ACTION_RECEIPT, status, inputs=(intent.intent_id,), outputs=(receipt.receipt_id,), evidence=receipt.evidence_ids, payload=log.entries[1], operator="constitution.boundary", delta=receipt.observed_resources)
        return receipt


# ---------------------------------------------------------------------- (de)serialisation helpers


def _wp(d: Mapping[str, Any] | None) -> WarrantProfile | None:
    if d is None:
        return None
    return WarrantProfile(tuple(frozenset(_ev(x) for x in w) for w in d["lower"]), tuple(frozenset(_ev(x) for x in w) for w in d["upper"]))


def _ev(x: str) -> Hashable:
    # evidence ids are stored by repr(); ints and strings round-trip
    if x.startswith("'") and x.endswith("'"):
        return x[1:-1]
    try:
        return int(x)
    except ValueError:
        return x


def _scope(d: Mapping[str, Any] | None) -> Scope | None:
    if d is None:
        return None
    return Scope(None if d["contexts"] is None else frozenset(d["contexts"]), (d["epoch"][0], d["epoch"][1]))


def _authority(d: Mapping[str, int]) -> Authority:
    return Authority(tuple(sorted(d.items())))


def _atom_to(a: S.Atom) -> dict[str, Any]:
    return a.as_dict()


def _atom_from(d: Mapping[str, Any]) -> S.Atom:
    return S.Atom(d["atom_id"], d["atom_type"], _wp(d["warrant"]), _authority(d["authority"]), _scope(d["scope"]), int(d["epoch"]), bool(d["quarantined"]), d.get("content_ref"), tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in d.get("meta", {}).items()))


def _edge_to(e: S.Hyperedge) -> dict[str, Any]:
    return e.as_dict()


def _edge_from(d: Mapping[str, Any]) -> S.Hyperedge:
    return S.Hyperedge(d["edge_id"], tuple(d["tails"]), tuple(d["heads"]), d["relation_type"], Fraction(d["weight"]), tuple(Fraction(w) for w in d["head_weights"]), _wp(d["warrant"]), _authority(d["authority"]), _scope(d["scope"]), d.get("executable_ref"))
