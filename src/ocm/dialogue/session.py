"""M4 dialogue session: the loop utterance → meaning(s) → workspace → cognition ↔ language planning
→ gate → external commitment → new dialogue evidence (M4 target loop).

Built on the M3 interpreter and the M4 workspace; every reply passes the commitment gate and is
recorded as a machine turn with its evidence.  Dialogue acts (M4 §9) are the plan's `Act`.
Reference: entities are introduced from interpreted meanings (one discourse entity per meaning
node with a label, keyed by canonical description) and pronouns/descriptions are resolved through
`reference.resolve` — NEEDS_CLARIFICATION only when the clarification policy says the ambiguity
matters to the pending question.  Correction ("correction, …" / "no, …") supersedes the speaker's
latest commitment on the same topic; retraction revokes.  Long-horizon: nothing is clipped; the
workspace file plus the runtime ledger reconstruct the session after restart (`DialogueRuntime.resume`).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Iterable, Sequence

from ocm.kso.warrant import Liveness
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel
from ocm.kso.types import Scope

from ocm.language import acquisition as AQ
from ocm.language.constructions import CandidateMeaning, Construction
from ocm.language.interpret import Interpretation, Verdict, interpret, tokenize
from ocm.language.lexicon import Lexicon
from ocm.language.meaning import MeaningGraph, canonical
from ocm.language.chat_frontend import _is_question, _strip, _is_negated, _describe, correction_body, CORRECTION_PREFIXES, clarification_choice

from . import clarify as CL
from . import gate as G
from . import reference as R
from .workspace import Commitment, DialogueWorkspace, WorkspaceRefusal

PRONOUN_NODE_LABELS = {None}


@dataclass(frozen=True)
class MachineTurn:
    act: G.Act
    text: str
    committed: bool
    evidence: tuple[str, ...] = ()
    events: tuple[G.FeedbackEvent, ...] = ()
    candidates: tuple[CandidateMeaning, ...] = ()
    interpretation: Interpretation | None = None




@dataclass
class DialogueRuntime:
    runtime: OCMRuntime
    lexicon: Lexicon
    constructions: list[Construction]
    conversation_id: str = "conv"
    workspace: DialogueWorkspace | None = None
    pending: dict[str, Any] = field(default_factory=dict)      # pending clarification / learn state
    asked: list[str] = field(default_factory=list)              # question ids asked (repeat penalty)
    families: dict[str, AQ.ConstructionFamily] = field(default_factory=dict)
    demonstrations: dict[str, list[AQ.Demonstration]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.workspace is None:
            self.workspace = DialogueWorkspace.load(self.runtime, self.conversation_id)

    @classmethod
    def resume(cls, root, lexicon: Lexicon, constructions: Sequence[Construction], conversation_id: str) -> "DialogueRuntime":
        rt = OCMRuntime(root)
        return cls(rt, lexicon, list(constructions), conversation_id)

    # ------------------------------------------------------------------ helpers
    def _revoked(self) -> frozenset:
        return frozenset(self.runtime.state.revoked)

    def _liveness(self, ev: Iterable[str]) -> Liveness:
        """Liveness of cited evidence; an id the ledger does not know is UNKNOWN (never LIVE)."""
        ev = list(ev)
        if not ev:
            return Liveness.UNKNOWN
        try:
            return self.runtime.state.evidence.liveness(ev)
        except KeyError:
            return Liveness.UNKNOWN

    def _entities_from(self, m: MeaningGraph, turn_id: int) -> list[str]:
        """Introduce or re-mention one discourse entity per labelled entity node."""
        ws = self.workspace
        ids = []
        for n in m.nodes:
            if n.node_type != "entity" or not n.label:
                continue
            desc = f"the {n.label}"
            hit = [e for e in ws.entities.values() if desc in e.descriptions or n.label in e.aliases]
            if hit:
                ws.mention(hit[0].entity_id, turn_id=turn_id)
                ids.append(hit[0].entity_id)
            else:
                feats = {k: v for k, v in n.features}
                e = ws.introduce("entity", desc, features={**feats, "animate": "no"}, turn_id=turn_id)
                ids.append(e.entity_id)
        return ids

    def _reply(self, act: G.Act, text: str, *, plan: G.ResponsePlan | None = None, surface: G.Surface | None = None, evidence: Iterable[str] = (), candidates: Iterable[CandidateMeaning] = (), interp: Interpretation | None = None) -> MachineTurn:
        """Every machine turn passes the gate; a refused plan is reported as the feedback events."""
        ws = self.workspace
        resolved = [e.entity_id for e in ws.entities.values()]
        if plan is None:
            plan = G.ResponsePlan(act, None, (), G.Marker.NONE)
        if surface is None:
            surface = G.Surface(text, plan.meaning, plan.required_marker)
        checkpoint = self.runtime._expectation()
        surface = replace(surface, text=text)
        verdict = G.commit_gate(plan, surface, self._liveness, resolved=resolved, lexicon=self.lexicon, constructions=self.constructions, revoked=self._revoked())
        if checkpoint != self.runtime._expectation():
            verdict = G.GateVerdict(False, verdict.events+(G.FeedbackEvent(G.FeedbackKind.RENDERER_CAPABILITY,"runtime changed during codec execution","render"),))
        if not verdict.committed:
            ws.record_turn("machine", f"[reopen {sorted({e.reopen_stage for e in verdict.events})}]", "REPORT_UNCERTAIN", "GATE_REFUSED")
            return MachineTurn(act, "I cannot say that yet: " + "; ".join(f"{e.kind.value} ({e.reopen_stage})" for e in verdict.events), False, tuple(evidence), verdict.events, tuple(candidates), interp)
        ws.record_turn("machine", text, act.value, "COMMITTED", evidence=evidence)
        return MachineTurn(act, text, True, tuple(evidence), (), tuple(candidates), interp)

    # ------------------------------------------------------------------ main entry
    def hear(self, utterance: str, speaker: str = "user", *, original_utterance: str | None = None) -> MachineTurn:
        ws = self.workspace
        if self.pending.get("clarify") is not None:
            return self._resolve_clarification(utterance, speaker)
        body, correction = correction_body(utterance)
        r = interpret(body, self.lexicon, self.constructions, speaker=speaker, conversation=self.conversation_id, revoked=self._revoked())
        turn = ws.record_turn(speaker, original_utterance if original_utterance is not None else utterance, "CORRECT" if correction else ("ASK" if r.verdict is Verdict.INTERPRETED and _is_question(r.meaning) else "ASSERT"), r.verdict.value, meaning_digest=None if r.meaning is None else canonical(r.meaning)[1])
        if r.verdict is Verdict.INTERPRETED:
            m = r.meaning
            self._entities_from(m, turn.turn_id)
            if _is_question(m):
                return self._answer(_strip(m, "ASKS", "question_variable"), r)
            return self._record(speaker, m, r, utterance, correction)
        if r.verdict is Verdict.AMBIGUOUS:
            return self._maybe_clarify(r, speaker)
        if r.verdict is Verdict.NEEDS_CONTEXT:
            return self._bind_context(r, speaker, body)
        if r.verdict in (Verdict.UNKNOWN_LEXEME, Verdict.UNKNOWN_CONSTRUCTION):
            self.pending["learn"] = body
            ws.open("obligation", {"learn": body, "verdict": r.verdict.value}, turn.turn_id)
            return self._reply(G.Act.REQUEST, f"I cannot interpret this yet ({r.verdict.value}). Show me what it means.", interp=r)
        if r.verdict is Verdict.CONTRADICTION:
            return self._reply(G.Act.REPORT_UNKNOWN, f"Every reading contradicts what is registered: {r.reason}", interp=r)
        return self._reply(G.Act.REPORT_UNKNOWN, r.reason, interp=r)

    # ------------------------------------------------------------------ statements / corrections
    def _record(self, speaker: str, m: MeaningGraph, r: Interpretation, utterance: str, correction: bool) -> MachineTurn:
        ws = self.workspace
        neg = _is_negated(m)
        base = _strip(m, "NEGATES") if neg else m
        supersedes = None
        if correction:
            # a correction supersedes the speaker's latest active commitment on the *same proposition*
            # (either polarity); failing that, the latest one on the current topic
            same = [c for c in ws.active_commitments(speaker) if c.digest == canonical(base)[1]]
            prev = same or [c for c in ws.active_commitments(speaker) if c.topic == ws.current_topic]
            if prev:
                supersedes = prev[-1].commitment_id
        try:
            c = ws.commit(speaker, base, negated=neg, supersedes=supersedes, utterance=utterance)
        except WorkspaceRefusal as exc:
            return self._reply(G.Act.REPORT_UNKNOWN, str(exc), interp=r)
        pos, negs = ws.commitments_on(base)
        conflicting = [x for x in (negs if not neg else pos) if x.commitment_id != c.commitment_id]
        text = f"Noted: {speaker} says {'not ' if neg else ''}{_describe(base)}."
        if supersedes:
            text += f" This supersedes {supersedes}; dependents reopened."
        if conflicting:
            text += f" It contradicts {', '.join(x.commitment_id for x in conflicting)}; both are kept as commitments, neither is my knowledge."
        plan = G.ResponsePlan(G.Act.ACKNOWLEDGE, None, (), G.Marker.NONE)
        return self._reply(G.Act.ACKNOWLEDGE, text, plan=plan, evidence=(c.evidence_id,), interp=r)

    # ------------------------------------------------------------------ questions
    def _answer(self, asked: MeaningGraph, r: Interpretation) -> MachineTurn:
        ws = self.workspace
        pos, neg = ws.commitments_on(asked)
        dg = canonical(asked)[1]
        machine = [mc for mc in ws.machine_commitments if mc["digest"] == dg and mc["evidence_id"] not in self.runtime.state.revoked]
        if machine:
            ev = tuple(mc["evidence_id"] for mc in machine)
            plan = G.ResponsePlan(G.Act.ANSWER, asked, (G.Assertion(dg, ev, "machine"),), G.Marker.ASSERTED)
            from ocm.language.realize import best, realize
            rendered = best(realize(asked, self.lexicon, self.constructions, revoked=self._revoked()))
            clause = rendered.text.removesuffix(".") if rendered else "CANNOT_CHECK"
            return self._reply(G.Act.ANSWER, f"Yes — {clause} ({', '.join(ev)}).", plan=plan, surface=G.Surface("Yes.", asked, G.Marker.ASSERTED), evidence=ev, interp=r)
        if pos and not neg:
            ev = tuple(c.evidence_id for c in pos)
            plan = G.ResponsePlan(G.Act.ANSWER, asked, (G.Assertion(dg, ev, "speaker"),), G.Marker.REPORTED, source_name=pos[0].speaker)
            return self._reply(G.Act.ANSWER, f"{pos[0].speaker} said so ({ev[0]}); I have no independent warrant.", plan=plan, surface=G.Surface("reported", asked, G.Marker.REPORTED), evidence=ev, interp=r)
        if neg and not pos:
            ev = tuple(c.evidence_id for c in neg)
            plan = G.ResponsePlan(G.Act.ANSWER, asked, (G.Assertion(dg, ev, "speaker"),), G.Marker.REPORTED, source_name=neg[0].speaker, reported_negative=True)
            return self._reply(G.Act.ANSWER, f"{neg[0].speaker} said it did not ({ev[0]}); I have no independent warrant.", plan=plan, surface=G.Surface("reported-negative", asked, G.Marker.REPORTED), evidence=ev, interp=r)
        if pos and neg:
            ev = tuple(c.evidence_id for c in pos + neg)
            plan = G.ResponsePlan(G.Act.REPORT_UNCERTAIN, asked, (G.Assertion(dg, ev, "speaker"),), G.Marker.UNCERTAIN)
            return self._reply(G.Act.REPORT_UNCERTAIN, "Contradictory statements are on record: " + ", ".join(ev), plan=plan, surface=G.Surface("contradictory", asked, G.Marker.UNCERTAIN), evidence=ev, interp=r)
        plan = G.ResponsePlan(G.Act.REPORT_UNKNOWN, asked, (), G.Marker.UNCERTAIN)
        return self._reply(G.Act.REPORT_UNKNOWN, "Unknown — nothing on record supports or denies it.", plan=plan, surface=G.Surface("unknown", asked, G.Marker.UNCERTAIN), interp=r)

    # ------------------------------------------------------------------ clarification
    def _maybe_clarify(self, r: Interpretation, speaker: str) -> MachineTurn:
        ws = self.workspace
        cands = list(range(len(r.candidates)))
        pending_q = ws.unresolved("question")
        # query family: the pending questions' answers under each candidate (does the candidate settle them?)
        queries = {}
        for i, q in enumerate(pending_q):
            asked_digest = q.detail.get("digest")
            queries[f"q{i}"] = lambda c, d=asked_digest: canonical(_strip(r.candidates[c].meaning, "NEGATES"))[1] == d
        # a statement whose readings differ in *what is asserted* always matters for the record
        queries["asserted"] = lambda c: canonical(r.candidates[c].meaning)[1]
        qs = CL.binary_questions(cands, lambda c: _describe(r.candidates[c].meaning) + " [" + ", ".join(sorted({n.label for n in r.candidates[c].meaning.nodes if n.label})) + "]")
        d = CL.decide(cands, queries, qs, asked_before=self.asked)
        if not d.ask:
            ws.open("ambiguity", {"utterance": r.utterance, "candidates": len(r.candidates), "reason": d.reason})
            return self._reply(G.Act.ACKNOWLEDGE, f"Noted ({len(r.candidates)} readings retained; {d.reason}).", candidates=r.candidates, interp=r)
        self.pending["clarify"] = (r, speaker, d.question)
        self.asked.append(d.question.question_id)
        item = ws.open("reference", {"utterance": r.utterance, "question": d.question.text, "value": d.value})
        self.pending["clarify_item"] = item.item_id
        return self._reply(G.Act.CLARIFY, d.question.text, candidates=r.candidates, interp=r)

    def _resolve_clarification(self, utterance: str, speaker: str) -> MachineTurn:
        ws = self.workspace
        r, sp, q = self.pending.pop("clarify")
        item = self.pending.pop("clarify_item", None)
        ws.record_turn(speaker, utterance, "CONFIRM", "CLARIFICATION_ANSWER")
        chosen = clarification_choice(utterance, r.candidates, q.question_id)
        if chosen is None:
            # not an answer to the question: the speaker moved on.  The ambiguity stays *open* in the
            # workspace (never forced) and the new utterance is processed on its own (ledger S22)
            if item:
                ws.open("ambiguity", {"utterance": r.utterance, "candidates": len(r.candidates), "abandoned_after": utterance})
            return self.hear(utterance, speaker)
        _, eid = self.runtime.admit_evidence({"clarification": r.utterance, "chosen": canonical(chosen.meaning)[1]}, Channel.INTERACTION, speaker, scope=Scope.of(self.conversation_id))
        if item:
            ws.resolve(item)
        m = chosen.meaning
        self._entities_from(m, len(ws.turns))
        if _is_question(m):
            return self._answer(_strip(m, "ASKS", "question_variable"), r)
        return self._record(sp, m, r, r.utterance, False)

    # ------------------------------------------------------------------ context binding (pronouns)
    def _bind_context(self, r: Interpretation, speaker: str, body: str) -> MachineTurn:
        ws = self.workspace
        m = r.candidates[0].meaning
        unresolved = [n for n in m.nodes if n.underspecified and n.node_type == "entity"]
        toks = tokenize(body)
        pron = next((t for t in toks if t in R.PRONOUNS), "it")
        res = R.resolve(ws, R.Mention(pron), matters=True)
        if res.status is R.ReferenceStatus.RESOLVED:
            ent = ws.entities[res.candidates[0]]
            label = ent.descriptions[0].split(" ", 1)[-1] if ent.descriptions else (ent.aliases[0] if ent.aliases else ent.entity_id)
            bound = m.relabel({}) if False else MeaningGraph(tuple(n if n.node_id not in {u.node_id for u in unresolved} else type(n)(n.node_id, n.node_type, label, n.features, False) for n in m.nodes), m.edges, m.root)
            ws.mention(ent.entity_id)
            if _is_question(bound):
                return self._answer(_strip(bound, "ASKS", "question_variable"), r)
            return self._record(speaker, bound, r, body, False)
        if res.status is R.ReferenceStatus.UNKNOWN_REFERENT:
            ws.open("reference", {"pronoun": pron, "status": res.status.value})
            return self._reply(G.Act.REQUEST, f"I do not know what '{pron}' refers to.", interp=r)
        opts = "; ".join(f"({i + 1}) {o['description']}" for i, o in enumerate(res.question_plan["options"]))
        self.pending["bind"] = (r, speaker, body, res)
        return self._reply(G.Act.CLARIFY, f"Which do you mean by '{pron}': {opts}?", interp=r)

    # ------------------------------------------------------------------ learning / retraction
    def register_family(self, family: AQ.ConstructionFamily) -> None:
        self.families[family.family] = family

    def demonstrate(self, family: str, utterance: str, meaning: MeaningGraph, speaker: str = "teacher") -> MachineTurn:
        fam = self.families[family]
        _, eid = self.runtime.admit_evidence({"demonstration": utterance, "meaning": meaning.as_dict(), "family": family}, Channel.DEMONSTRATION, speaker, scope=Scope.of(self.conversation_id))
        self.demonstrations.setdefault(family, []).append(AQ.Demonstration(utterance, meaning, eid, speaker))
        p = AQ.acquire(fam, self.lexicon, self.demonstrations[family])
        if p.status.value != "PASS":
            return self._reply(G.Act.ACKNOWLEDGE, f"Demonstration recorded ({eid}); {family} is still {p.status.value}.", evidence=(eid,))
        cid = f"{fam.language}:{family}:learned"
        self.constructions = [c for c in self.constructions if c.construction_id != cid] + [AQ.construction_from_proposal(fam, p, cid)]
        for it in self.workspace.unresolved("obligation"):
            if "learn" in it.detail:
                self.workspace.resolve(it.item_id)
        self.pending.pop("learn", None)
        return self._reply(G.Act.ACKNOWLEDGE, f"Learned the {family} construction ({p.payload['hypothesis']}).", evidence=tuple(sorted(p.warrant.evidence)))

    def retract(self, commitment_id: str) -> MachineTurn:
        try:
            c = self.workspace.retract(commitment_id)
        except WorkspaceRefusal as exc:
            return self._reply(G.Act.REPORT_UNKNOWN, str(exc))
        return self._reply(G.Act.ACKNOWLEDGE, f"Retracted {commitment_id}; its evidence {c.evidence_id} is revoked and dependents reopened.", evidence=(c.evidence_id,))
