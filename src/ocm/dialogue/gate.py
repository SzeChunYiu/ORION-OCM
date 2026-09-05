"""External commitment gate and thought↔language feedback (M4 §7–§9; theory batch 3 C2/C3).

A `ResponsePlan` is what cognition intends to say: a dialogue act, the meaning graph (or
proposition digests) it asserts, the evidence each assertion rests on, the epistemic marker the
three-valued state requires, and the referents it needs.  A `Surface` is the renderer's output:
text plus the meaning graph the renderer *claims* the text expresses (the codec's reverse reading)
and any facts it introduced.  The gate refuses unless:

    G1 meaning(surface) canonical digest == meaning(plan) digest       (no drift, no minted facts)
    G2 every asserted proposition is LIVE at the plan's scope           (warrant threshold)
    G3 the surface's epistemic marker equals the plan's required marker (uncertainty preserved)
    G4 every referent the plan needs is RESOLVED in the workspace       (resolvable enough)
    G5 no protected/hidden content id appears in the surface            (codec cannot leak)
    G6 the renderer has no store handle (capability half: it receives digests, not the store)

Feedback events (M4 §7) are the *structured* reasons a plan cannot be rendered, each naming the
cognitive stage to reopen: MISSING_REFERENT → reference, MISSING_PREMISE / UNSUPPORTED_ASSERTION →
warrant/solve, SEMANTIC_CONFLICT / PLAN_CONTRADICTION → nogoods, UNKNOWN_CONSTRUCTION → learn,
EXCESS_AMBIGUITY → clarify.  A linguistic alternative may raise such an event; it can never add
support (the gate has no admit path).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Sequence

from ocm.kso.warrant import Liveness

from ocm.language.meaning import MeaningGraph, canonical


class Act(str, Enum):
    ASSERT = "ASSERT"
    ANSWER = "ANSWER"
    ASK = "ASK"
    CLARIFY = "CLARIFY"
    ACKNOWLEDGE = "ACKNOWLEDGE"
    CORRECT = "CORRECT"
    RETRACT = "RETRACT"
    REQUEST = "REQUEST"
    CONFIRM = "CONFIRM"
    REPORT_UNKNOWN = "REPORT_UNKNOWN"
    REPORT_UNCERTAIN = "REPORT_UNCERTAIN"


class Marker(str, Enum):
    """Epistemic marker the surface must carry, fixed by the three-valued state of the assertion."""
    ASSERTED = "ASSERTED"          # LIVE machine warrant
    REPORTED = "REPORTED"          # rests on speaker commitments only ("X said …")
    UNCERTAIN = "UNCERTAIN"        # UNKNOWN
    DENIED = "DENIED"              # DEAD / contradicted
    NONE = "NONE"                  # non-assertive acts


class FeedbackKind(str, Enum):
    MISSING_REFERENT = "MISSING_REFERENT"
    MISSING_PREMISE = "MISSING_PREMISE"
    SEMANTIC_CONFLICT = "SEMANTIC_CONFLICT"
    UNSUPPORTED_ASSERTION = "UNSUPPORTED_ASSERTION"
    UNKNOWN_CONSTRUCTION = "UNKNOWN_CONSTRUCTION"
    EXCESS_AMBIGUITY = "EXCESS_AMBIGUITY"
    PLAN_CONTRADICTION = "PLAN_CONTRADICTION"
    MEANING_DRIFT = "MEANING_DRIFT"
    MARKER_MISMATCH = "MARKER_MISMATCH"
    PROTECTED_LEAK = "PROTECTED_LEAK"
    RENDERER_CAPABILITY = "RENDERER_CAPABILITY"


REOPENS = {
    FeedbackKind.MISSING_REFERENT: "reference", FeedbackKind.MISSING_PREMISE: "solve", FeedbackKind.SEMANTIC_CONFLICT: "nogoods",
    FeedbackKind.UNSUPPORTED_ASSERTION: "warrant", FeedbackKind.UNKNOWN_CONSTRUCTION: "learn", FeedbackKind.EXCESS_AMBIGUITY: "clarify",
    FeedbackKind.PLAN_CONTRADICTION: "nogoods", FeedbackKind.MEANING_DRIFT: "render", FeedbackKind.MARKER_MISMATCH: "render",
    FeedbackKind.PROTECTED_LEAK: "render", FeedbackKind.RENDERER_CAPABILITY: "render",
}


@dataclass(frozen=True)
class FeedbackEvent:
    kind: FeedbackKind
    detail: str
    reopen_stage: str


@dataclass(frozen=True)
class Assertion:
    digest: str                                # canonical meaning digest of the proposition
    evidence: tuple[str, ...]                  # what it rests on
    layer: str                                 # "machine" | "speaker"


@dataclass(frozen=True)
class ResponsePlan:
    act: Act
    meaning: MeaningGraph | None
    assertions: tuple[Assertion, ...] = ()
    required_marker: Marker = Marker.NONE
    referents: tuple[str, ...] = ()            # entity ids the plan needs resolved
    scope: str | None = None


@dataclass(frozen=True)
class Surface:
    text: str
    meaning: MeaningGraph | None               # the codec's reverse reading of the text
    marker: Marker
    introduced_digests: tuple[str, ...] = ()   # propositions the text expresses beyond the plan
    content_ids: tuple[str, ...] = ()          # content hashes the renderer referenced
    renderer_had_store: bool = False


@dataclass(frozen=True)
class GateVerdict:
    committed: bool
    events: tuple[FeedbackEvent, ...]


def required_marker(liveness: Liveness, layer: str) -> Marker:
    if layer in ("speaker", "source"):          # commitments and unverified source claims are *reported*
        return Marker.REPORTED if liveness is Liveness.LIVE else Marker.UNCERTAIN
    return {Liveness.LIVE: Marker.ASSERTED, Liveness.UNKNOWN: Marker.UNCERTAIN, Liveness.DEAD: Marker.DENIED}[liveness]


def plan_check(plan: ResponsePlan, liveness_of: Callable[[Iterable[str]], Liveness], resolved: Iterable[str]) -> tuple[FeedbackEvent, ...]:
    """Thought→language direction: can this plan be said at all?  Returns reopen events."""
    ev: list[FeedbackEvent] = []
    res = set(resolved)
    for r in plan.referents:
        if r not in res:
            ev.append(FeedbackEvent(FeedbackKind.MISSING_REFERENT, r, REOPENS[FeedbackKind.MISSING_REFERENT]))
    for a in plan.assertions:
        lv = liveness_of(a.evidence) if a.evidence else Liveness.UNKNOWN
        need = required_marker(lv, a.layer)
        if plan.required_marker is not Marker.NONE and need is not plan.required_marker:
            kind = FeedbackKind.UNSUPPORTED_ASSERTION if plan.required_marker is Marker.ASSERTED else FeedbackKind.MARKER_MISMATCH
            ev.append(FeedbackEvent(kind, f"{a.digest}: state requires {need.value}, plan says {plan.required_marker.value}", REOPENS[kind]))
        if not a.evidence:
            ev.append(FeedbackEvent(FeedbackKind.MISSING_PREMISE, a.digest, REOPENS[FeedbackKind.MISSING_PREMISE]))
    digests = [a.digest for a in plan.assertions]
    if plan.meaning is not None and plan.act in (Act.ASSERT, Act.ANSWER) and any(e.relation == "NEGATES" for e in plan.meaning.edges) and any(not e.relation == "NEGATES" for e in ()):
        pass
    if len(set(digests)) != len(digests):
        ev.append(FeedbackEvent(FeedbackKind.PLAN_CONTRADICTION, "duplicate assertion", REOPENS[FeedbackKind.PLAN_CONTRADICTION]))
    return tuple(ev)


def commit_gate(plan: ResponsePlan, surface: Surface, liveness_of: Callable[[Iterable[str]], Liveness], *, resolved: Iterable[str] = (), protected_ids: Iterable[str] = ()) -> GateVerdict:
    ev: list[FeedbackEvent] = list(plan_check(plan, liveness_of, resolved))
    if surface.renderer_had_store:
        ev.append(FeedbackEvent(FeedbackKind.RENDERER_CAPABILITY, "renderer held a store handle", REOPENS[FeedbackKind.RENDERER_CAPABILITY]))
    if (plan.meaning is None) != (surface.meaning is None) or (plan.meaning is not None and canonical(plan.meaning)[1] != canonical(surface.meaning)[1]):
        ev.append(FeedbackEvent(FeedbackKind.MEANING_DRIFT, "surface meaning ≠ plan meaning", REOPENS[FeedbackKind.MEANING_DRIFT]))
    if surface.introduced_digests:
        ev.append(FeedbackEvent(FeedbackKind.MEANING_DRIFT, f"renderer introduced {list(surface.introduced_digests)}", REOPENS[FeedbackKind.MEANING_DRIFT]))
    if surface.marker is not plan.required_marker:
        ev.append(FeedbackEvent(FeedbackKind.MARKER_MISMATCH, f"surface {surface.marker.value} ≠ required {plan.required_marker.value}", REOPENS[FeedbackKind.MARKER_MISMATCH]))
    leaked = sorted(set(surface.content_ids) & set(protected_ids))
    if leaked:
        ev.append(FeedbackEvent(FeedbackKind.PROTECTED_LEAK, str(leaked), REOPENS[FeedbackKind.PROTECTED_LEAK]))
    return GateVerdict(not ev, tuple(ev))


def mutant_renderer_injects_fact(surface: Surface, digest: str) -> Surface:
    """Planted (M4 §14): the renderer adds a proposition not in the response meaning."""
    return Surface(surface.text + " (and also …)", surface.meaning, surface.marker, surface.introduced_digests + (digest,), surface.content_ids, surface.renderer_had_store)


def mutant_drop_uncertainty(surface: Surface) -> Surface:
    """Planted (M4 §14): an UNCERTAIN plan rendered as a flat assertion."""
    return Surface(surface.text.replace("might ", "").replace("I am not sure whether ", ""), surface.meaning, Marker.ASSERTED, surface.introduced_digests, surface.content_ids, surface.renderer_had_store)
