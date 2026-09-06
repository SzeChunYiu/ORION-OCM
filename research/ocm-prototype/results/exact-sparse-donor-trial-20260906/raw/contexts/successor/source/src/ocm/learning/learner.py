"""Learner interface (M2 §6) — one lifecycle for every acquisition channel.

    Learner.observe(experience)           → records an Experience (channel-typed, evidence-bound)
    Learner.propose_updates(state)        → UpdateProposals (never admitted by the learner itself)
    Runtime.evaluate_update(proposal)     → EvaluatedUpdate with status PASS | FAIL | CANNOT_CHECK
    Runtime.admit_or_quarantine(...)      → admission through ``kso.admission`` only

Invariants (registry KS-T18, KS-S1, MEG-13 finite-class half):
  * feedback alone never mints warrant: a FEEDBACK experience yields a *behaviour* proposal
    (weights/relevance/routing) and never an object proposal with a non-zero interval — unless a
    registered task contract (``FeedbackContract``) declares feedback as valid evidence for that
    exact target, in which case it enters as an OBSERVATION about the registered outcome function
    (MEG-15), never as the skill's own warrant;
  * ambiguous experiences stay unresolved (``GAP_AMBIGUOUS``), contradictory ones keep the
    conflict (``CONTRADICTION`` + nogood), insufficient ones never promote;
  * a promoted object's warrant is the exhibited demonstration/instruction evidence (⊗), so
    revoking an essential lesson reopens it (KS-T22) while unrelated skills stay live;
  * relearning admits new support under a new evidence id with a LINEAGE link (history kept).

The version-space learner over a *finite registered hypothesis class* is the M2 reference learner
(inherited M3 calibration generalised: agreement on the registered query family, not global
uniqueness).  Parents: Mitchell 1982 version spaces; KWIK (Li, Littman & Walsh 2008); Angluin 1988.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Hashable, Iterable, Mapping, Protocol, Sequence

from ocm.kso.admission import CertificateKind, WARRANTING_KINDS
from ocm.kso.ids import content_hash
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import WarrantProfile, meet_all_profiles


class ExperienceKind(str, Enum):
    INSTRUCTION = "INSTRUCTION"       # "the rule is …" with source identity
    DEMONSTRATION = "DEMONSTRATION"   # (input, output) pairs
    INTERACTION = "INTERACTION"       # answered queries (membership / equivalence)
    EXPERIMENTATION = "EXPERIMENTATION"  # closure over a registered domain
    FEEDBACK = "FEEDBACK"             # endpoint reward / preference: behaviour only


@dataclass(frozen=True)
class Experience:
    experience_id: str
    kind: ExperienceKind
    evidence_id: str                  # the evidence record backing this experience
    target: str                       # the skill/object the experience is about
    content: Mapping[str, Any]        # e.g. {"input": x, "output": y} or {"rule": ...}
    source: str = ""


class UpdateKind(str, Enum):
    OBJECT = "OBJECT"                 # a new warranted atom (skill/claim/construction)
    BEHAVIOUR = "BEHAVIOUR"           # weights/relevance/routing — no warrant change
    QUARANTINE = "QUARANTINE"         # candidate stored without warrant


class UpdateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"
    GAP_AMBIGUOUS = "GAP_AMBIGUOUS"
    GAP_INSUFFICIENT = "GAP_INSUFFICIENT"
    CONTRADICTION = "CONTRADICTION"


@dataclass(frozen=True)
class UpdateProposal:
    proposal_id: str
    kind: UpdateKind
    target: str
    payload: Mapping[str, Any]
    warrant: WarrantProfile           # ⊗ of the experiences' evidence for OBJECT; zero for BEHAVIOUR
    certificate: CertificateKind
    supporting_experience_ids: tuple[str, ...]
    status: UpdateStatus
    detail: str = ""
    scope: Scope = field(default_factory=Scope.universal)
    authority: Authority = field(default_factory=Authority)
    lineage: tuple[str, ...] = ()     # previous object ids this relearns


@dataclass(frozen=True)
class FeedbackContract:
    """A registered task contract that licenses feedback as evidence for ONE target via a
    registered outcome function (MEG-15)."""

    target: str
    outcome_function_id: str
    evidence_channel: CertificateKind = CertificateKind.OBSERVATION

    def __post_init__(self) -> None:
        if self.evidence_channel not in WARRANTING_KINDS:
            raise ValueError("a feedback contract must route to a warranting channel")


class Learner(Protocol):
    def observe(self, experience: Experience) -> None: ...
    def propose_updates(self) -> list[UpdateProposal]: ...


Hypothesis = Callable[[Any], Any]


@dataclass
class VersionSpaceLearner:
    """Reference learner over a finite registered hypothesis class.

    ``hypotheses``: name → callable.  ``query_family``: the registered inputs on which agreement
    is required for promotion (MEG-13 agreement-region rule).  Demonstrations/interactions
    eliminate hypotheses; instructions name a hypothesis directly (still checked against the
    demonstrations); experimentation supplies the closure over the whole domain.
    """

    target: str
    hypotheses: Mapping[str, Hypothesis]
    query_family: tuple[Any, ...]
    contracts: tuple[FeedbackContract, ...] = ()
    experiences: list[Experience] = field(default_factory=list)

    def observe(self, experience: Experience) -> None:
        if experience.target != self.target:
            raise ValueError("experience addressed to another target")
        self.experiences.append(experience)

    # --- version space ------------------------------------------------------------------
    def _examples(self) -> list[tuple[Any, Any, Experience]]:
        out = []
        for e in self.experiences:
            if e.kind in (ExperienceKind.DEMONSTRATION, ExperienceKind.INTERACTION, ExperienceKind.EXPERIMENTATION):
                for x, y in e.content.get("pairs", ()):
                    out.append((x, y, e))
            elif e.kind is ExperienceKind.FEEDBACK:
                c = next((c for c in self.contracts if c.target == self.target and c.outcome_function_id == e.content.get("outcome_function_id")), None)
                if c is not None:  # licensed feedback = an observation of the registered outcome
                    for x, y in e.content.get("pairs", ()):
                        out.append((x, y, e))
        return out

    def consistent(self) -> dict[str, list[Experience]]:
        """Hypotheses consistent with every example, with the examples that pinned them."""
        examples = self._examples()
        out = {}
        for name, h in self.hypotheses.items():
            if all(h(x) == y for x, y, _ in examples):
                out[name] = [e for _, _, e in examples]
        return out

    def contradictions(self) -> list[tuple[Experience, Experience]]:
        seen: dict[Any, tuple[Any, Experience]] = {}
        out = []
        for x, y, e in self._examples():
            if x in seen and seen[x][0] != y:
                out.append((seen[x][1], e))
            seen.setdefault(x, (y, e))
        return out

    def agreement_on_query_family(self, names: Iterable[str]) -> bool:
        names = list(names)
        if not names:
            return False
        return all(len({self.hypotheses[n](q) for n in names}) == 1 for q in self.query_family)

    def propose_updates(self) -> list[UpdateProposal]:
        pid = f"upd:{self.target}:{content_hash([e.experience_id for e in self.experiences])[:12]}"
        feedback = [e for e in self.experiences if e.kind is ExperienceKind.FEEDBACK]
        proposals: list[UpdateProposal] = []
        licensed = {e.experience_id for x, y, e in self._examples() if e.kind is ExperienceKind.FEEDBACK}
        for e in feedback:
            if e.experience_id not in licensed:
                proposals.append(UpdateProposal(pid + ":fb", UpdateKind.BEHAVIOUR, self.target, {"reward": e.content.get("reward")}, WarrantProfile.zero(), CertificateKind.FEEDBACK, (e.experience_id,), UpdateStatus.PASS, "feedback updates behaviour only (KS-T18)"))
        conflicts = self.contradictions()
        if conflicts:
            proposals.append(UpdateProposal(pid, UpdateKind.QUARANTINE, self.target, {"conflicts": [(a.experience_id, b.experience_id) for a, b in conflicts]}, WarrantProfile.zero(), CertificateKind.DEMONSTRATION, tuple(e.experience_id for e in self.experiences), UpdateStatus.CONTRADICTION, "contradictory examples are preserved as a conflict, never averaged"))
            return proposals
        consistent = self.consistent()
        if not consistent:
            proposals.append(UpdateProposal(pid, UpdateKind.QUARANTINE, self.target, {}, WarrantProfile.zero(), CertificateKind.DEMONSTRATION, (), UpdateStatus.FAIL, "no registered hypothesis is consistent with the examples"))
            return proposals
        instructed = [e for e in self.experiences if e.kind is ExperienceKind.INSTRUCTION and e.content.get("hypothesis") in consistent]
        chosen: list[str]
        if instructed:
            chosen = [instructed[-1].content["hypothesis"]]
        else:
            chosen = sorted(consistent)
        if not self.agreement_on_query_family(chosen):
            proposals.append(UpdateProposal(pid, UpdateKind.QUARANTINE, self.target, {"candidates": chosen}, WarrantProfile.zero(), CertificateKind.DEMONSTRATION, tuple(e.experience_id for e in self.experiences), UpdateStatus.GAP_AMBIGUOUS if len(chosen) > 1 else UpdateStatus.GAP_INSUFFICIENT, "version space disagrees on the registered query family"))
            return proposals
        pins = {e.evidence_id for name in chosen for e in consistent[name]} | {e.evidence_id for e in instructed}
        if not pins:
            proposals.append(UpdateProposal(pid, UpdateKind.QUARANTINE, self.target, {"candidates": chosen}, WarrantProfile.zero(), CertificateKind.DEMONSTRATION, (), UpdateStatus.GAP_INSUFFICIENT, "no warranting evidence pins the hypothesis"))
            return proposals
        warrant = WarrantProfile.certified([frozenset(pins)])
        cert = CertificateKind.INSTRUCTION if instructed else (CertificateKind.EXPERIMENTATION if any(e.kind is ExperienceKind.EXPERIMENTATION for e in self.experiences) else CertificateKind.DEMONSTRATION)
        proposals.append(UpdateProposal(pid, UpdateKind.OBJECT, self.target, {"hypothesis": chosen[0], "table": [(q, self.hypotheses[chosen[0]](q)) for q in self.query_family]}, warrant, cert, tuple(e.experience_id for e in self.experiences), UpdateStatus.PASS, f"agreement on {len(self.query_family)} registered queries"))
        return proposals


def mutant_feedback_mints_warrant(learner: VersionSpaceLearner) -> UpdateProposal:
    """Planted: an unlicensed FEEDBACK experience is turned into an OBJECT proposal with warrant."""
    fb = [e for e in learner.experiences if e.kind is ExperienceKind.FEEDBACK]
    e = fb[-1]
    return UpdateProposal("mutant", UpdateKind.OBJECT, learner.target, {"reward": e.content.get("reward")}, WarrantProfile.certified([frozenset({e.evidence_id})]), CertificateKind.DEMONSTRATION, (e.experience_id,), UpdateStatus.PASS, "MUTANT")


def mutant_average_contradiction(learner: VersionSpaceLearner) -> UpdateProposal:
    """Planted: contradictory examples are majority-voted into one hypothesis."""
    votes: dict[str, int] = {}
    for x, y, _ in learner._examples():
        for name, h in learner.hypotheses.items():
            if h(x) == y:
                votes[name] = votes.get(name, 0) + 1
    best = max(votes, key=votes.get)
    return UpdateProposal("mutant", UpdateKind.OBJECT, learner.target, {"hypothesis": best}, WarrantProfile.one(), CertificateKind.DEMONSTRATION, (), UpdateStatus.PASS, "MUTANT")
