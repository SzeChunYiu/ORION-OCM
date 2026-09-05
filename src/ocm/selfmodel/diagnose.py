"""Diagnosis as a distribution with evidence, and the obstruction certificate (M11 §3–§4;
theory batch 5 E2/E3).

The diagnosis is a *set* of layers with evidence weights, never an oracle label: the weight of a
layer is the number of counterfactual/ablation records that succeeded when that layer was
changed, divided by the records that touched it; a layer with no ablation evidence stays UNKNOWN.
The *minimum-sufficient* level is the lowest layer whose ablation restored the task.  Escalation
beyond local repair (D3+) requires an `ObstructionCertificate`: the registered lower-level
alternatives were tried with LIVE warrants and failed, with a ceiling witness; low confidence,
repeated failure or novelty alone is never an obstruction.  Hostiles: a disabled local operator
proposing a representation rewrite when restoring the operator solves the task; a dead-warrant
failure presented as an obstruction; a single low score treated as an architecture alarm.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

from ocm.kso.warrant import Liveness, WarrantProfile

from .model import AblationEvidence, FailureRecord, Layer

ORDER = [Layer.D0_PARAMETER, Layer.D1_ROUTING, Layer.D2_OPERATOR, Layer.D5_VOCABULARY, Layer.D6_LEARNING_POLICY, Layer.D3_REPRESENTATION, Layer.D4_TASK_FORMULATION, Layer.D7_ORGANISATION, Layer.D8_CONSTITUTION]
LOCAL = {Layer.D0_PARAMETER, Layer.D1_ROUTING, Layer.D2_OPERATOR, Layer.D5_VOCABULARY, Layer.D6_LEARNING_POLICY}


@dataclass(frozen=True)
class Diagnosis:
    weights: Mapping[str, float]               # layer → fraction of ablations at that layer that restored the task
    unknown: tuple[str, ...]                   # candidate layers with no ablation evidence
    minimum_sufficient: str | None             # lowest layer whose ablation restored the task
    architecture_alarm: bool
    evidence: tuple[str, ...]


def diagnose(f: FailureRecord, *, certificate: "ObstructionCertificate | None" = None, registry: "Mapping[Layer, Sequence[str]] | None" = None) -> Diagnosis:
    touched: dict[Layer, list[bool]] = {}
    for a in f.ablations:
        touched.setdefault(a.layer, []).append(a.task_succeeded)
    weights = {l.value: sum(v) / len(v) for l, v in touched.items()}
    unknown = tuple(l.value for l in f.candidate_layers if l not in touched)
    restoring = [l for l in ORDER if l in touched and any(touched[l])]
    minimum = restoring[0].value if restoring else None
    # E2: repeated failure never contributes; the alarm is the certificate's, never the symptom count's
    alarm = minimum is not None and Layer(minimum) not in LOCAL and certificate is not None and certificate.valid(registry)
    return Diagnosis(weights, unknown, minimum, alarm, tuple(a.evidence_id for a in f.ablations))


@dataclass(frozen=True)
class Attempt:
    alternative_id: str
    layer: Layer
    warrant: WarrantProfile
    succeeded: bool


@dataclass(frozen=True)
class ObstructionCertificate:
    """Escalation record (M11 §4): incumbent layer, failed obligation, registered lower-level
    alternatives with their attempts, resource envelope, ceiling evidence, why narrower repair is
    insufficient.  Valid iff every registered lower-level alternative was tried with a LIVE warrant
    and failed, and a ceiling witness is present."""
    incumbent_layer: Layer
    failed_obligation: str
    registered_alternatives: tuple[str, ...]
    attempts: tuple[Attempt, ...]
    resource_envelope: Mapping[str, Any]
    ceiling_evidence: tuple[str, ...]
    narrower_insufficient_because: str
    revoked: frozenset = frozenset()

    def valid(self, registry: "Mapping[Layer, Sequence[str]] | None" = None) -> bool:
        """E3(iii): when a component registry is supplied, the alternatives that must have been tried
        are the registry's closure for the incumbent layer, not the certificate's own list."""
        required = tuple(registry.get(self.incumbent_layer, ())) if registry is not None else self.registered_alternatives
        if registry is not None and set(required) - set(self.registered_alternatives):
            return False                        # the certificate omitted a registered alternative
        tried = {a.alternative_id: a for a in self.attempts}
        if any(alt not in tried for alt in required):
            return False
        if any(a.succeeded for a in tried.values()):
            return False
        if any(a.warrant.liveness(self.revoked) is not Liveness.LIVE for a in tried.values()):
            return False                        # a dead-warrant failure is not an obstruction (E3)
        return bool(self.ceiling_evidence)

    def reasons(self) -> list[str]:
        out = []
        tried = {a.alternative_id: a for a in self.attempts}
        for alt in self.registered_alternatives:
            if alt not in tried:
                out.append(f"untried alternative {alt}")
        for a in tried.values():
            if a.succeeded:
                out.append(f"alternative {a.alternative_id} succeeded: narrower repair suffices")
            if a.warrant.liveness(self.revoked) is not Liveness.LIVE:
                out.append(f"alternative {a.alternative_id} failed with a {a.warrant.liveness(self.revoked).value} warrant: reinstate before escalating")
        if not self.ceiling_evidence:
            out.append("no ceiling witness")
        return out


def escalation_allowed(d: Diagnosis, certificate: ObstructionCertificate | None, registry: "Mapping[Layer, Sequence[str]] | None" = None) -> tuple[bool, str]:
    if d.minimum_sufficient is None:
        return False, "no ablation restored the task: gather more evidence (UNKNOWN), do not escalate"
    if Layer(d.minimum_sufficient) in LOCAL:
        return False, f"minimum-sufficient layer {d.minimum_sufficient} is local: repair there"
    if certificate is None or not certificate.valid(registry):
        return False, "no valid obstruction certificate: " + ("; ".join(certificate.reasons()) if certificate else "none supplied") + ("" if registry is None or certificate is None else "; registry closure required")
    return True, f"escalate to {d.minimum_sufficient} under certificate"


def mutant_repeated_failure_is_architecture(f: FailureRecord) -> bool:
    """Planted (E2 hostile): frequency ≥ 3 raises the architecture alarm without a certificate."""
    return f.frequency >= 3


def mutant_certificate_lists_its_own_alternatives(cert: ObstructionCertificate) -> bool:
    """Planted (E3(iii) hostile): validity judged against the certificate's own list, ignoring the registry."""
    return cert.valid(None)


def mutant_low_score_is_architecture(f: FailureRecord) -> bool:
    """Planted (M11 §2 hostile): infer an architecture problem from a single low score."""
    return True


def mutant_dead_warrant_obstruction(cert: ObstructionCertificate) -> bool:
    """Planted (E3 hostile): certificate accepted without the LIVE-warrant clause."""
    tried = {a.alternative_id for a in cert.attempts}
    return all(alt in tried for alt in cert.registered_alternatives) and not any(a.succeeded for a in cert.attempts) and bool(cert.ceiling_evidence)


@dataclass(frozen=True)
class LocalCandidate:
    """A repair below the diagnosed layer that the F4 lemma licenses before any escalation."""
    kind: str                       # "reinstate" | "reroute"
    layer: Layer
    target: str
    why: str


def local_candidates(dead_on_path: Iterable[str], alternatives: Iterable[str] = ()) -> tuple[LocalCandidate, ...]:
    """Batch 6 F4: a failure explained by a DEAD warrant on the execution path has minimum-sufficient
    layer ≤ D2 — reinstatement (D2) and rerouting to a registered alternative (D1) are emitted as
    candidates that must be tried (and fail with LIVE warrants) before the layer can be read as higher."""
    out = [LocalCandidate("reinstate", Layer.D2_OPERATOR, e, "DEAD warrant on the path: reinstate or replace before escalating (F4)") for e in dead_on_path]
    out += [LocalCandidate("reroute", Layer.D1_ROUTING, a, "registered alternative not yet tried (F4 converse)") for a in alternatives]
    return tuple(out)


def diagnose_with_path(f: FailureRecord, *, dead_on_path: Iterable[str], certificate: "ObstructionCertificate | None" = None, registry: "Mapping[Layer, Sequence[str]] | None" = None) -> tuple[Diagnosis, tuple[LocalCandidate, ...]]:
    """`diagnose` plus the F4 bound: with a DEAD warrant on the path and no LIVE-warrant ablation
    evidence above D2, the minimum-sufficient layer is capped at D2 and the local candidates are
    returned; an escalation is refused until they were tried."""
    dead = tuple(dead_on_path)
    base = diagnose(f, certificate=certificate, registry=registry)
    cands = local_candidates(dead, registry.get(Layer.D1_ROUTING, ()) if registry else ())
    if dead and (base.minimum_sufficient is None or Layer(base.minimum_sufficient) not in LOCAL):
        return Diagnosis(base.weights, base.unknown, Layer.D2_OPERATOR.value, False, base.evidence + ("F4:dead-warrant-on-path",)), cands
    return base, cands


def mutant_escalate_over_dead_path(f: FailureRecord, dead_on_path: Iterable[str]) -> str | None:
    """Planted (F4 hostile): reads the layer from the ablations alone, ignoring the DEAD warrant on the path."""
    return diagnose(f).minimum_sufficient

