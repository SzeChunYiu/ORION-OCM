"""ResponsePlan.v1 and the response planner (M6 §2–§3, §7).

A `ResponsePlan` is produced *above* sentence generation: dialogue act, intended content
(propositions with their warrant layer), warrant/uncertainty requirement, content selection and
ordering (rhetorical relation), reference strategy, style constraints, length target, clause
obligations, open checks.  Refinement: plan → clause structure → sentence plans (`realize`) →
surface; when a lower level exposes a missing referent, an unsupported comparative/causal wording
or a missing intermediate premise, the planner raises a `FeedbackEvent` and reopens the higher
level (M6 §7 protected cases) instead of rendering.

Content selection draws only on (a) the bounded knowledge world (source claims vs verified facts,
by liveness) and (b) the dialogue workspace (speaker commitments).  Nothing is invented: an
unknown yields REPORT_UNKNOWN with the gap named; an unverified source claim is REPORTED with its
source; a contradiction is REPORT_UNCERTAIN citing both.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Sequence

from ocm.kso.warrant import Liveness

from ocm.knowledge.world import Fact, KnowledgeWorld
from ocm.language.meaning import MeaningGraph, canonical

from .gate import Act, Assertion, FeedbackEvent, FeedbackKind, Marker, REOPENS, ResponsePlan as GatePlan
from .workspace import DialogueWorkspace


FUNCTIONAL_RELATIONS = frozenset({"CAPITAL_OF", "BOILS_AT", "FREEZES_AT", "HAS_COUNT", "EQUALS", "HAPPENED_IN"})   # registry data: one object per subject


class Rhetorical(str, Enum):
    ANSWER = "ANSWER"
    ELABORATION = "ELABORATION"       # explanation chain
    CONTRAST = "CONTRAST"             # compare/contrast
    LIST = "LIST"                     # summary
    TEACH_BACK = "TEACH_BACK"
    NONE = "NONE"


@dataclass(frozen=True)
class ContentItem:
    digest: str
    meaning: MeaningGraph
    layer: str                        # machine | source | speaker
    evidence: tuple[str, ...]
    marker: Marker
    gloss: str
    source: str | None = None
    negated: bool = False


@dataclass(frozen=True)
class ResponsePlan:
    act: Act
    goal: str
    content: tuple[ContentItem, ...]
    rhetorical: Rhetorical
    required_marker: Marker
    reference_strategy: str            # full | pronoun_safe
    register: str                      # neutral | brief | detailed | formal | casual
    length_target: int                 # max clauses
    clause_obligations: tuple[str, ...]
    open_checks: tuple[str, ...]
    referents: tuple[str, ...] = ()
    events: tuple[FeedbackEvent, ...] = ()

    def gate_plan(self) -> GatePlan:
        assertions = tuple(Assertion(c.digest, c.evidence, c.layer if c.layer in ("speaker", "source") else "machine") for c in self.content)
        meaning = self.content[0].meaning if self.content else None
        return GatePlan(self.act, meaning, assertions, self.required_marker, self.referents, source_name=self.content[0].source if self.content else None, reported_negative=self.content[0].negated if self.content else False)


def _item(world: KnowledgeWorld, f: Fact) -> ContentItem:
    lv = world.liveness(f.fact_id)
    verified = world.authority(f.fact_id).rank("verified") == 1
    ev = tuple(f.assertion_evidence + f.verification_evidence)
    if lv is not Liveness.LIVE:
        return ContentItem(f.digest, f.meaning, "machine", ev, Marker.DENIED if lv is Liveness.DEAD else Marker.UNCERTAIN, f.gloss)
    if verified:
        return ContentItem(f.digest, f.meaning, "machine", ev, Marker.ASSERTED, f.gloss)
    return ContentItem(f.digest, f.meaning, "source", ev, Marker.REPORTED, f.gloss, source=f.sources[0] if f.sources else None)


def plan_answer(world: KnowledgeWorld, ws: DialogueWorkspace, asked: MeaningGraph, *, register: str = "neutral") -> ResponsePlan:
    """Yes/no over the bounded world and the discourse record: verified fact → ASSERTED; live
    source claim → REPORTED with its source; contradicted → UNCERTAIN citing both; absent → UNKNOWN."""
    f, lv = world.lookup(asked)
    pos, neg = ws.commitments_on(asked)
    items: list[ContentItem] = []
    if f is not None and lv is Liveness.LIVE:
        items.append(_item(world, f))
    # a contradicting live fact: only for *registered functional* relations (one value per subject),
    # same subject, different object; IS_A / LOCATED_IN admit several true objects (ledger S23)
    subj = asked.node(asked.root).label if asked.root else None
    rel = asked.edges[0].relation if asked.edges else None
    contra = [g for g in world.about(subj) if rel in FUNCTIONAL_RELATIONS and g.fact_id != (f.fact_id if f else None) and any(e.relation == rel and g.meaning.node(e.tails[0]).label == subj and g.meaning.node(e.heads[0]).label != asked.node(asked.edges[0].heads[0]).label for e in g.meaning.edges)] if asked.edges else []
    verified_contra = [g for g in contra if world.authority(g.fact_id).rank("verified") == 1]
    if items and items[0].marker is Marker.ASSERTED and not verified_contra:
        return ResponsePlan(Act.ANSWER, "answer yes/no", tuple(items), Rhetorical.ANSWER, Marker.ASSERTED, "full", register, 1, ("cite evidence",), ())
    if items and items[0].marker is Marker.REPORTED:
        return ResponsePlan(Act.ANSWER, "report source claim", tuple(items), Rhetorical.ANSWER, Marker.REPORTED, "full", register, 1, ("name the source",), ("verification absent",))
    if pos or neg:
        ev = tuple(c.evidence_id for c in pos + neg)
        it = ContentItem(canonical(asked)[1], asked, "speaker", ev, Marker.REPORTED if not (pos and neg) else Marker.UNCERTAIN, "", (pos or neg)[0].speaker, bool(neg and not pos))
        return ResponsePlan(Act.ANSWER if not (pos and neg) else Act.REPORT_UNCERTAIN, "report speaker commitment", (it,), Rhetorical.ANSWER, it.marker, "full", register, 1, ("name the speaker",), ())
    if f is not None and lv is Liveness.DEAD:
        return ResponsePlan(Act.REPORT_UNKNOWN, "fact revoked", (), Rhetorical.NONE, Marker.UNCERTAIN, "full", register, 1, ("say the support was revoked",), ("revoked",))
    return ResponsePlan(Act.REPORT_UNKNOWN, "unknown", (), Rhetorical.NONE, Marker.UNCERTAIN, "full", register, 1, ("say what is not known",), ("outside bounded world",))


def plan_explain(world: KnowledgeWorld, label: str, *, depth: int = 2, register: str = "neutral") -> ResponsePlan:
    """Explanation = the live facts about the label, then one hop along IS_A/PART_OF/LOCATED_IN
    (ELABORATION).  A missing intermediate premise (a hop whose target has no live facts) is a
    feedback event naming the gap (M6 §7 case 3)."""
    items: list[ContentItem] = []
    events: list[FeedbackEvent] = []
    seen: set[str] = set()
    frontier = [label]
    for _ in range(depth):
        nxt = []
        for lab in frontier:
            facts = world.about(lab)
            if not facts and lab != label:
                events.append(FeedbackEvent(FeedbackKind.MISSING_PREMISE, f"no live facts about {lab}", REOPENS[FeedbackKind.MISSING_PREMISE]))
            for f in facts:
                if f.digest in seen:
                    continue
                seen.add(f.digest)
                items.append(_item(world, f))
                for e in f.meaning.edges:
                    if e.relation in ("IS_A", "PART_OF", "LOCATED_IN", "ORBITS") and f.meaning.node(e.tails[0]).label == lab:
                        nxt.append(f.meaning.node(e.heads[0]).label)
        frontier = nxt
    if not items:
        return ResponsePlan(Act.REPORT_UNKNOWN, f"explain {label}", (), Rhetorical.NONE, Marker.UNCERTAIN, "full", register, 1, ("say what is not known",), ("outside bounded world",))
    marker = Marker.ASSERTED if all(i.marker is Marker.ASSERTED for i in items) else Marker.REPORTED
    n = {"brief": 2, "neutral": 4, "detailed": 8}.get(register, 4)
    return ResponsePlan(Act.ASSERT, f"explain {label}", tuple(items[:n]), Rhetorical.ELABORATION, marker, "pronoun_safe", register, n, ("order: about the topic first, then one hop",), tuple(e.detail for e in events), events=tuple(events))


def plan_compare(world: KnowledgeWorld, a: str, b: str, *, register: str = "neutral") -> ResponsePlan:
    """Compare/contrast = shared relations (same object) vs differing; only live facts; an
    unsupported comparative ('bigger') is never minted (no size facts ⇒ not expressible)."""
    fmt = lambda pair: f"{pair[0]}={pair[1]}" if pair[1] else str(pair[0])  # noqa: E731
    ra, rb = world.relations_of(a), world.relations_of(b)
    shared, diff = [], []
    for rel in sorted(set(ra) | set(rb)):
        oa, ob = {fmt(x) for x in ra.get(rel, [])}, {fmt(x) for x in rb.get(rel, [])}
        if oa & ob:
            shared.append((rel, sorted(oa & ob)))
        if oa ^ ob:
            diff.append((rel, sorted(oa - ob), sorted(ob - oa)))
    items: list[ContentItem] = []
    for f in world.about(a) + world.about(b):
        items.append(_item(world, f))
    if not items:
        return ResponsePlan(Act.REPORT_UNKNOWN, f"compare {a} {b}", (), Rhetorical.NONE, Marker.UNCERTAIN, "full", register, 1, (), ("outside bounded world",))
    marker = Marker.ASSERTED if all(i.marker is Marker.ASSERTED for i in items) else Marker.REPORTED
    obligations = tuple([f"shared:{rel}={','.join(o)}" for rel, o in shared] + [f"differs:{rel}:{a}={','.join(x)}|{b}={','.join(y)}" for rel, x, y in diff])
    return ResponsePlan(Act.ASSERT, f"compare {a} and {b}", tuple(items), Rhetorical.CONTRAST, marker, "full", register, len(items), obligations, ())


def plan_summary(world: KnowledgeWorld, ws: DialogueWorkspace, *, register: str = "neutral") -> ResponsePlan:
    """Summary of the conversation: the active speaker commitments, as REPORTED content."""
    items = []
    for c in ws.active_commitments():
        m = MeaningGraph.from_dict(c.meaning) if hasattr(MeaningGraph, "from_dict") else None
        if m is None:
            continue
        items.append(ContentItem(c.digest, m, "speaker", (c.evidence_id,), Marker.REPORTED, "", c.speaker))
    if not items:
        return ResponsePlan(Act.REPORT_UNKNOWN, "summary", (), Rhetorical.NONE, Marker.UNCERTAIN, "full", register, 1, (), ("nothing on record",))
    return ResponsePlan(Act.ASSERT, "summarise the conversation", tuple(items), Rhetorical.LIST, Marker.REPORTED, "pronoun_safe", register, len(items), ("attribute each item to its speaker",), ())


def plan_teach_back(lexeme: str, concept: str, evidence: Iterable[str], *, construction: str | None = None) -> ResponsePlan:
    ev = tuple(evidence)
    gloss = f"'{lexeme}' means {concept}" + (f"; the {construction} construction" if construction else "")
    it = ContentItem(f"teach:{lexeme}", MeaningGraph((), (), None), "machine", ev, Marker.ASSERTED, gloss)
    return ResponsePlan(Act.ASSERT, "teach back", (it,), Rhetorical.TEACH_BACK, Marker.ASSERTED, "full", "neutral", 1, ("cite the lesson evidence",), ())


def check_plan(plan: ResponsePlan, resolved: Iterable[str]) -> tuple[FeedbackEvent, ...]:
    """Thought→language checks before realisation (M6 §7): missing referent, unsupported
    comparative wording, missing premise already recorded in plan.events."""
    ev = list(plan.events)
    res = set(resolved)
    for r in plan.referents:
        if r not in res:
            ev.append(FeedbackEvent(FeedbackKind.MISSING_REFERENT, r, REOPENS[FeedbackKind.MISSING_REFERENT]))
    for ob in plan.clause_obligations:
        if ob.startswith("comparative:") and not any(c.marker is Marker.ASSERTED for c in plan.content):
            ev.append(FeedbackEvent(FeedbackKind.UNSUPPORTED_ASSERTION, ob, REOPENS[FeedbackKind.UNSUPPORTED_ASSERTION]))
    return tuple(ev)


def mutant_invent_premise(plan: ResponsePlan, digest: str, gloss: str) -> ResponsePlan:
    """Planted (M6 §13 'response planner invents intermediate premise')."""
    it = ContentItem(digest, MeaningGraph((), (), None), "machine", (), Marker.ASSERTED, gloss)
    return ResponsePlan(plan.act, plan.goal, plan.content + (it,), plan.rhetorical, plan.required_marker, plan.reference_strategy, plan.register, plan.length_target + 1, plan.clause_obligations, plan.open_checks, plan.referents, plan.events)
