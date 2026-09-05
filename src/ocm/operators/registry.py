"""Operator / skill registry (M2 §7) and the warrant rule for statistical operators (MEG-02).

An operator is an executable object with a contract: inputs, output type, preconditions, backend,
expected effects, warrant/dependencies, resource model, checker, known failures, lineage.  Backends
need not be symbolic.  What the epistemic contract fixes is *only* the interface: how a backend's
output enters the store.

MEG-02 (definitional half, adopted here):
  * A STATISTICAL/NEURAL backend's candidate enters with the interval ``⟦0, ONE⟧`` — UNKNOWN under
    every revocation — and a **score outside the lattice** (``Candidate.score``); a score is never
    a warrant (KS-T24 at the operator level).
  * A candidate becomes LIVE only through (a) an EXACT_CHECKER / OBSERVATION certificate on the
    candidate itself, or (b) a **scoped coverage certificate** — an EXPERIMENTATION-channel claim
    *about the operator* ("coverage ≥ 1−δ under the registered exchangeability assumption on scope
    S") whose warrant becomes the bridge ``P_b`` of the composition, with ``S`` recorded as the
    candidate's scope.  Outside ``S`` the certificate does not apply and the candidate stays UNKNOWN.
  * Corollary of KS-T21: no composition whose components are all UNKNOWN is LIVE.
  Parents: selective classification (Chow 1970, verified), conformal prediction (Vovk et al.,
  candidate parent, unverified), PCC admission (Necula 1997, verified).  The graded-semiring half
  (exact-share retraction for graded gates) stays OPEN and is not used: gates remain {0,1}.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

from ocm.kso.admission import CertificateKind, WARRANTING_KINDS
from ocm.kso.ids import content_hash
from ocm.kso.resources import ResourceVector
from ocm.kso.space import KnowledgeSpace, TypedRejection
from ocm.kso.types import Authority, Scope, internal_authority
from ocm.kso.warrant import Liveness, WarrantProfile, meet_all_profiles


class BackendKind(str, Enum):
    PROGRAMMATIC = "PROGRAMMATIC"       # deterministic code; output warranted by inputs ⊗ operator warrant
    SEARCH = "SEARCH"                   # exhaustive/bounded search with an exact verifier
    STATISTICAL = "STATISTICAL"         # probabilistic / neural / LLM-derived: candidates enter UNKNOWN
    PROOF = "PROOF"                     # external proof kernel: EXACT_CHECKER certificate on success
    EXTERNAL_TOOL = "EXTERNAL_TOOL"     # effects outside the store: only through ActionIntent/Receipt


Backend = Callable[[KnowledgeSpace, Mapping[str, Any]], Mapping[str, Any]]
Checker = Callable[[Mapping[str, Any]], str]   # returns "PASS" | "FAIL" | "CANNOT_CHECK"


@dataclass(frozen=True)
class OperatorSpec:
    operator_id: str
    version: str
    kind: BackendKind
    backend: Backend
    input_atoms: tuple[str, ...]
    output_type: str = "procedure"
    preconditions: tuple[str, ...] = ()          # atom ids that must be LIVE
    expected_effects: tuple[str, ...] = ()
    warrant: WarrantProfile = field(default_factory=WarrantProfile.one)
    authority: Authority = field(default_factory=Authority)
    scope: Scope = field(default_factory=Scope.universal)
    checker: Checker | None = None
    known_failures: tuple[str, ...] = ()
    lineage: tuple[str, ...] = ()
    resource_model: ResourceVector = field(default_factory=ResourceVector)

    @property
    def fingerprint(self) -> str:
        return content_hash({"id": self.operator_id, "version": self.version, "kind": self.kind.value, "inputs": list(self.input_atoms), "output": self.output_type})

    def as_dict(self) -> dict[str, Any]:
        return {"operator_id": self.operator_id, "version": self.version, "kind": self.kind.value, "fingerprint": self.fingerprint, "inputs": list(self.input_atoms), "output_type": self.output_type, "preconditions": list(self.preconditions), "scope": self.scope.as_dict(), "authority": self.authority.as_dict(), "known_failures": list(self.known_failures), "lineage": list(self.lineage)}


@dataclass(frozen=True)
class CoverageCertificate:
    """An EXPERIMENTATION-channel claim about an operator: coverage ≥ 1 − delta on `scope` under a
    registered assumption; its evidence id is the bridge warrant of every candidate it licenses."""

    operator_fingerprint: str
    scope: Scope
    delta: Fraction
    assumption: str                  # e.g. "exchangeability of calibration and deployment draws"
    evidence_id: str                 # the EXPERIMENTATION record (calibration run) that warrants it
    channel: CertificateKind = CertificateKind.EXPERIMENTATION

    def __post_init__(self) -> None:
        if not (Fraction(0) <= self.delta < Fraction(1)):
            raise ValueError("delta must be in [0,1)")
        if self.channel not in WARRANTING_KINDS:
            raise TypedRejection("COVERAGE_CERTIFICATE_FROM_NON_WARRANTING_CHANNEL", self.channel.value)

    @property
    def bridge_warrant(self) -> WarrantProfile:
        return WarrantProfile.certified([frozenset({self.evidence_id})])


@dataclass(frozen=True)
class Candidate:
    """A backend output as it may enter the store."""

    operator: OperatorSpec
    output: Mapping[str, Any]
    warrant: WarrantProfile
    scope: Scope
    authority: Authority
    score: float | None = None      # OUTSIDE the lattice; ranking only, never warrant
    certificate: str | None = None  # how it became LIVE, if it did

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        return self.warrant.liveness(revoked)


def compose_candidate(
    ks: KnowledgeSpace,
    op: OperatorSpec,
    output: Mapping[str, Any],
    *,
    score: float | None = None,
    coverage: CoverageCertificate | None = None,
    exact_certificate_evidence: str | None = None,
    context: str | None = None,
) -> Candidate:
    """Apply the MEG-02 rule to a backend output."""
    amap = ks.atom_map()
    for x in op.input_atoms:
        if x not in amap:
            raise TypedRejection("UNKNOWN_ATOM", x)
    inputs_warrant = meet_all_profiles([op.warrant, *(amap[x].warrant for x in op.input_atoms)])
    authority = internal_authority([op.authority, *(amap[x].authority for x in op.input_atoms)])  # MEG-04
    scope = op.scope
    for x in op.input_atoms:
        scope = scope.intersect(amap[x].scope)
    if op.kind in (BackendKind.PROGRAMMATIC, BackendKind.SEARCH):
        return Candidate(op, output, inputs_warrant, scope, authority, score)
    if op.kind is BackendKind.PROOF:
        if exact_certificate_evidence is None:
            return Candidate(op, output, WarrantProfile((), inputs_warrant.upper), scope, authority, score)  # no kernel verdict: UNKNOWN
        w = inputs_warrant.meet(WarrantProfile.certified([frozenset({exact_certificate_evidence})]))
        return Candidate(op, output, w, scope, authority, score, certificate="EXACT_CHECKER")
    if op.kind is BackendKind.EXTERNAL_TOOL:
        raise TypedRejection("EXTERNAL_TOOL_REQUIRES_ACTION_INTENT", op.operator_id)
    # STATISTICAL: UNKNOWN by default — lower bound empty, upper bound whatever the inputs allow
    unknown = WarrantProfile((), inputs_warrant.upper)
    if exact_certificate_evidence is not None:
        w = inputs_warrant.meet(WarrantProfile.certified([frozenset({exact_certificate_evidence})]))
        return Candidate(op, output, w, scope, authority, score, certificate="EXACT_CHECKER")
    if coverage is not None:
        if coverage.operator_fingerprint != op.fingerprint:
            raise TypedRejection("COVERAGE_CERTIFICATE_FOR_ANOTHER_OPERATOR", op.operator_id)
        licensed_scope = scope.intersect(coverage.scope)
        if licensed_scope.is_empty or (context is not None and not coverage.scope.covers(context)):
            return Candidate(op, output, unknown, scope, authority, score)   # outside S: stays UNKNOWN
        w = inputs_warrant.meet(coverage.bridge_warrant)
        return Candidate(op, output, w, licensed_scope, authority, score, certificate=f"COVERAGE(delta={coverage.delta})")
    return Candidate(op, output, unknown, scope, authority, score)


def mutant_score_promoted_to_warrant(ks: KnowledgeSpace, op: OperatorSpec, output: Mapping[str, Any], score: float, threshold: float = 0.9) -> Candidate:
    """Planted: a high score makes the candidate LIVE (authority laundering by ranking)."""
    amap = ks.atom_map()
    w = meet_all_profiles([op.warrant, *(amap[x].warrant for x in op.input_atoms)])
    return Candidate(op, output, w if score >= threshold else WarrantProfile((), w.upper), op.scope, op.authority, score, certificate="SCORE")


@dataclass
class OperatorRegistry:
    operators: dict[str, OperatorSpec] = field(default_factory=dict)
    certificates: dict[str, list[CoverageCertificate]] = field(default_factory=dict)

    def register(self, op: OperatorSpec) -> str:
        key = f"{op.operator_id}@{op.version}"
        if key in self.operators and self.operators[key].fingerprint != op.fingerprint:
            raise TypedRejection("OPERATOR_VERSION_COLLISION", key)
        self.operators[key] = op
        return key

    def add_coverage(self, cert: CoverageCertificate) -> None:
        self.certificates.setdefault(cert.operator_fingerprint, []).append(cert)

    def coverage_for(self, op: OperatorSpec, context: str | None) -> CoverageCertificate | None:
        for c in self.certificates.get(op.fingerprint, []):
            if context is None or c.scope.covers(context):
                return c
        return None

    def applicable(self, ks: KnowledgeSpace, atoms: Iterable[str], revoked: Iterable[Hashable] = ()) -> list[OperatorSpec]:
        rv = frozenset(revoked)
        amap = ks.atom_map()
        pool = set(atoms)
        out = []
        for op in self.operators.values():
            if not set(op.input_atoms) <= pool:
                continue
            if not op.warrant.is_live(rv) or any(not amap[x].is_live(rv) for x in op.input_atoms):
                continue
            if any(p not in amap or not amap[p].is_live(rv) for p in op.preconditions):
                continue
            out.append(op)
        return sorted(out, key=lambda o: (o.operator_id, o.version))

    def as_dict(self) -> dict[str, Any]:
        return {"operators": {k: v.as_dict() for k, v in sorted(self.operators.items())}, "coverage_certificates": {k: [{"scope": c.scope.as_dict(), "delta": str(c.delta), "evidence_id": c.evidence_id} for c in v] for k, v in self.certificates.items()}}
