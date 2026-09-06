"""The Alpha chat session (M6 §1–§3, §7–§8): one persistent machine over the bounded world.

    user utterance → M3 interpretation → M4 workspace → knowledge/cognition → ResponsePlan.v1
    ↔ feedback (reopen) → realisation (checked codec) → commitment gate → committed response

Every committed response is a machine turn in the workspace with its evidence; the diagnostic
trace is assembled from the runtime's actual events (the ledger sequence numbers emitted during
the turn), the interpretation candidates, the workspace state, the plan and the gate verdict —
never from an after-the-fact explanation.  Learning in chat: `teach word`, `teach construction`
(through M5 lifecycles), `revoke <evidence>` / `reinstate <evidence>` (diagnostic commands), all
persisted through the runtime ledger + workspace file so a restart retains them.
The mechanism arm calls no external model; external IO is zero.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

from ocm.dialogue import gate as G
from ocm.dialogue import planner as P
from ocm.dialogue import surface_text as ST
from ocm.dialogue.session import DialogueRuntime, _describe, _is_question, _strip
from ocm.knowledge.world import KnowledgeWorld, triple
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.language import acquisition as AQ
from ocm.language import constructions as C
from ocm.language import lexicon as L
from ocm.language import realize as RZ
from ocm.language.interpret import Verdict, tokenize
from ocm.language.meaning import MEdge, MNode, MeaningGraph, canonical
from ocm.learning.language import lexical as LX
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel
from ocm.kso.types import Scope
from ocm.data import default_manifest_path
from ocm.language.chat_frontend import seed_frontend, world_query, add_lexical_lesson, parse_lexical_lesson

DEFAULT_MANIFEST = default_manifest_path()

# relation words the bounded world's question forms use ("is X in Y", "is X a Y", "does X orbit Y", "what is X")
RELATION_WORDS = {"in": "LOCATED_IN", "a": "IS_A", "an": "IS_A", "orbit": "ORBITS", "orbits": "ORBITS", "part": "PART_OF", "contain": "CONTAINS", "contains": "CONTAINS", "before": "BEFORE", "capital": "CAPITAL_OF"}


@dataclass
class TurnTrace:
    turn_id: int
    utterance: str
    interpretation: dict[str, Any]
    dialogue_state: dict[str, Any]
    kso_objects: list[str]
    operators: list[str]
    checks: list[str]
    response_plan: dict[str, Any]
    sentence_plan: dict[str, Any]
    warrant_ids: list[str]
    resources: dict[str, Any]
    committed_response: str
    ledger_events: list[int]


def _load_lexicon_and_constructions(state_dir: Path, manifest: Path = DEFAULT_MANIFEST) -> tuple[L.Lexicon, list[C.Construction]]:
    """Compatibility export retaining this entry point's default custody check."""
    if Path(manifest).resolve() == DEFAULT_MANIFEST.resolve():
        manifest = default_manifest_path()
    return seed_frontend(manifest)


@dataclass
class ChatSession:
    root: Path
    conversation_id: str = "alpha"
    manifest: Path = DEFAULT_MANIFEST
    diagnostic: bool = False
    runtime: OCMRuntime = field(init=False)
    world: KnowledgeWorld = field(init=False)
    dialogue: DialogueRuntime = field(init=False)
    traces: list[TurnTrace] = field(default_factory=list)
    style: RZ.Style = field(default_factory=RZ.Style)
    register: str = "neutral"
    learned_state_path: Path = field(init=False)
    pending_spelling: tuple[str, ...] = field(default=(), init=False)
    input_guess: dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.runtime = OCMRuntime(self.root / "ledger")
        lx, cons = _load_lexicon_and_constructions(self.root, self.manifest)
        self.dialogue = DialogueRuntime(self.runtime, lx, cons, self.conversation_id)
        self.world = KnowledgeWorld(self.runtime)
        self.learned_state_path = self.root / "learned.json"
        marker = self.root / "world_loaded.json"
        if not marker.exists():
            rep = self.world.load_manifest(self.manifest)
            marker.write_text(json.dumps(rep) + "\n", encoding="utf-8")
            self._save_world_index()
        else:
            self._restore_world_index()
        self._restore_learned()

    # ------------------------------------------------------------------ persistence of indexes
    def _save_world_index(self) -> None:
        idx = {fid: {"digest": f.digest, "topic": f.topic, "sources": f.sources, "assertion": f.assertion_evidence, "verification": f.verification_evidence, "verified_by": f.verified_by, "gloss": f.gloss, "meaning": f.meaning.as_dict()} for fid, f in self.world.facts.items()}
        (self.root / "world_index.json").write_text(json.dumps({"documents": {k: vars(v) for k, v in self.world.documents.items()}, "facts": idx}, sort_keys=True), encoding="utf-8")

    def _restore_world_index(self) -> None:
        from ocm.knowledge.world import Fact, SourceDocument

        d = json.loads((self.root / "world_index.json").read_text(encoding="utf-8"))
        for k, v in d["documents"].items():
            self.world.documents[k] = SourceDocument(**v)
        known = set(self.runtime.state.evidence.records)
        for fid, v in d["facts"].items():
            missing = [e for e in v["assertion"] + v["verification"] if e not in known]
            if missing:
                raise RuntimeError(f"CANNOT_CHECK: world index references evidence absent from the ledger: {missing}")
            m = MeaningGraph.from_dict(v["meaning"])
            self.world.facts[fid] = Fact(fid, m, v["digest"], v["topic"], v["sources"], v["assertion"], v["verification"], v["verified_by"], v["gloss"])
            self.world.by_digest[v["digest"]] = fid

    def _save_learned(self) -> None:
        lx = self.dialogue.lexicon
        known = set(self.runtime.state.evidence.records)          # learned-in-chat senses cite ledger evidence
        words = [{"lemma": x.lemma, "category": x.category.value, "senses": [{"sense_id": s.sense_id, "concept": s.concept, "node_type": s.node_type, "evidence": sorted(s.warrant.evidence)} for s in x.senses if s.warrant.evidence & known], "features": list(x.features)} for k, x in lx.lexemes.items() if any(e in known for s in x.senses for e in s.warrant.evidence)]
        cons = [{"construction_id": c.construction_id, "family": c.family, "hypothesis": getattr(c, "lineage", ()), "evidence": sorted(c.warrant.evidence), "pattern": [(s.name, s.category.value, s.phrase, list(s.requires)) for s in c.pattern]} for c in self.dialogue.constructions if c.construction_id.endswith(":learned")]
        self.learned_state_path.write_text(json.dumps({"words": words, "constructions": cons}, sort_keys=True), encoding="utf-8")

    def _restore_learned(self) -> None:
        if not self.learned_state_path.exists():
            return
        d = json.loads(self.learned_state_path.read_text(encoding="utf-8"))
        lx = self.dialogue.lexicon
        for w in d["words"]:
            senses = tuple(L.Sense(s["sense_id"], s["concept"], s["node_type"], WarrantProfile.of(set(s["evidence"]))) for s in w["senses"])
            key = f"{w['lemma']}|{w['category']}"
            if key in lx.lexemes:                                  # keep the built-in senses, add the learned ones
                old = lx.lexemes[key]
                senses = old.senses + tuple(s for s in senses if s.sense_id not in {o.sense_id for o in old.senses})
            lx.add(L.Lexeme(w["lemma"], L.Category(w["category"]), senses, tuple(tuple(f) for f in w["features"])))
        seed = {c.construction_id: c for c in C.seed_constructions()}
        for c in d["constructions"]:
            pattern = tuple(C.Slot(n, L.Category(cat), phrase=ph, requires=tuple(req)) for n, cat, ph, req in c["pattern"])
            self.dialogue.constructions.append(C.Construction(c["construction_id"], c["family"], pattern, seed["en:transitive"].template, WarrantProfile.of(set(c["evidence"])), language="en"))

    # ------------------------------------------------------------------ the loop
    def say(self, text: str, speaker: str = "user") -> str:
        from . import spelling

        if not isinstance(text, str):
            raise TypeError("chat input must be text")
        self.input_guess = {}
        original = text
        low = text.strip().lower().rstrip(".!?")
        if self.pending_spelling:
            pending = self.pending_spelling
            self.pending_spelling = ()
            chosen = pending[0] if low in ("yes", "yes please") and len(pending) == 1 else next(
                (c for c in pending if c.lower().rstrip(".!?") == low), None)
            if chosen:
                self.input_guess = {"original": original, "interpreted": chosen, "status": "USER_CONFIRMED"}
                return self._say(chosen, speaker)
        proposal = spelling.propose(text, self.dialogue.lexicon, self.runtime.state.revoked)
        if proposal.candidates:
            candidate = proposal.candidates[0]
            # Automatic guesses only answer read-only world queries. Statements,
            # lessons, commands and ambiguous alternatives require clarification.
            read_only = (self._world_question(candidate.lower()) is not None or
                         candidate.lower().startswith(("what is ", "explain ", "compare ")))
            if len(proposal.candidates) == 1 and read_only:
                self.input_guess = {"original": original, "interpreted": candidate, "status": "SPELLING_GUESS"}
                try:
                    return self._say(candidate, speaker)
                finally:
                    self.input_guess = {}
            self.pending_spelling = proposal.candidates
            options = " or ".join(repr(c) for c in proposal.candidates[:4])
            reply = f"Did you mean {options}? " + ("Reply yes or write the intended sentence." if len(proposal.candidates) == 1 else "Please write the intended sentence.")
            return self._commit(original, reply, G.Act.REQUEST, {"interpretation": {"status": proposal.status,
                "candidates": proposal.candidates}}, time.perf_counter(), len(self.runtime.events))
        return self._say(text, speaker)

    def _say(self, text: str, speaker: str = "user") -> str:
        t0 = time.perf_counter()
        seq0 = len(self.runtime.events)
        low = text.strip().lower()
        from .learning import handle
        learned = handle(self, text)
        if learned is not None:
            reply, evidence = learned
            return self._commit(text, reply, G.Act.ACKNOWLEDGE, {"learning_interface": True}, t0, seq0, evidence=evidence)
        social = low.rstrip(".!?")
        if social in ("hi", "hello", "hey", "good morning"):
            return self._commit(text, "Hello! What would you like to discuss or teach me?", G.Act.ACKNOWLEDGE, {}, t0, seq0)
        if social in ("thanks", "thank you"):
            return self._commit(text, "You're welcome.", G.Act.ACKNOWLEDGE, {}, t0, seq0)
        if social in ("what can you do", "can you learn", "what can you learn", "help"):
            reply = ("I can discuss my bounded knowledge, remember your reports, learn words and grammar, "
                "and learn or find checked arithmetic methods. Try 'remember: mira is a botanist', "
                "'teach: crate = shipping container', 'learn method next-square: inc square', "
                "'run next-square on 3', or 'find method: 1,2,1'. I ask when spelling is ambiguous. "
                "I do not yet support unrestricted conversation or unsolved mathematics.")
            return self._commit(text, reply, G.Act.ACKNOWLEDGE, {}, t0, seq0)
        for prefix in ("tell me about ", "can you explain ", "please explain "):
            if low.startswith(prefix):
                return self._explain(text, low[len(prefix):].strip("?. "), t0, seq0)
        if low.startswith(("what's ", "what’s ")):
            return self._explain(text, low[7:].strip("?. "), t0, seq0)
        # style requests (no factual change)
        for reg in ("brief", "detailed", "formal", "casual"):
            if low in (f"be {reg}", f"please be {reg}", f"{reg} please", f"answer {reg}ly"):
                self.register = reg
                self.style = RZ.Style(register=reg, contractions=(reg == "casual"))
                return self._commit(text, f"Understood — I will keep answers {reg}.", G.Act.ACKNOWLEDGE, {}, t0, seq0)
        # Invalid lesson syntax is a typed conversational refusal, before durable admission.
        if low.startswith("teach:"):
            body = text.strip()[6:].strip()
            aligned = "=>" in body or body.lower().startswith("construction ")
            if aligned:
                utterance, sep, target = body.partition("=>")
                valid = bool(sep and utterance.strip() and len(target.split()) == 3)
            else:
                word, sep, concept = body.partition("=")
                valid = bool(sep and word.strip() and concept.strip())
            if not valid or any(ch in body for ch in ("\n", "\r")):
                return self._commit(text, "I cannot learn that format. Use teach: word = concept, or teach: construction sentence => agent verb patient.", G.Act.REQUEST, {}, t0, seq0)
        # diagnostic commands
        if low.startswith("revoke "):
            return self._revoke(text, low.split(" ", 1)[1].strip(), t0, seq0)
        if low.startswith("reinstate "):
            self.runtime.reinstate([low.split(" ", 1)[1].strip()])
            return self._commit(text, "Reinstated.", G.Act.ACKNOWLEDGE, {}, t0, seq0)
        if low.startswith("teach:"):
            return self._teach(text, t0, seq0)
        if low.startswith("what is ") or low.startswith("what is a ") or low.startswith("explain "):
            label = low.replace("what is a ", "").replace("what is an ", "").replace("what is the ", "").replace("what is ", "").replace("explain the ", "").replace("explain ", "").strip("?. ")
            return self._explain(text, label, t0, seq0)
        if low.startswith("compare "):
            body = low[len("compare "):].strip("?. ")
            parts = [p.strip() for p in body.replace(" with ", " and ").split(" and ")]
            if len(parts) == 2:
                return self._compare(text, parts[0].replace("the ", ""), parts[1].replace("the ", ""), t0, seq0)
        if low in ("summarize", "summarise", "summarize the conversation", "what did we say"):
            return self._summary(text, t0, seq0)
        # bounded-world yes/no questions: "is X in Y" / "is X a Y" / "does X orbit Y" / "is X the capital of Y"
        q = self._world_question(low)
        if q is not None:
            return self._answer_world(text, q, t0, seq0)
        # everything else: the M4 dialogue loop (statements, questions over the record, clarification, learning)
        mt = self.dialogue.hear(text, speaker, original_utterance=self.input_guess.get("original"))
        trace_bits = {"interpretation": self._interp_dict(mt.interpretation), "act": mt.act.value, "events": [e.kind.value for e in mt.events]}
        reply = mt.text
        if mt.act is G.Act.REQUEST and "cannot interpret" in mt.text:
            reply = mt.text + " (say: teach: <word> = <concept>, or teach: construction <utterance> => <agent> <verb> <patient>)"
        return self._commit(text, reply, mt.act, trace_bits, t0, seq0, committed=mt.committed, evidence=mt.evidence, machine_turn_recorded=True)

    # ------------------------------------------------------------------ bounded-world questions
    def _world_question(self, low: str) -> MeaningGraph | None:
        query = world_query(low)
        return triple(*query) if query is not None else None

    def _answer_world(self, text: str, asked: MeaningGraph, t0: float, seq0: int) -> str:
        plan = P.plan_answer(self.world, self.dialogue.workspace, asked, register=self.register)
        subj = asked.node("s").label; rel = asked.edges[0].relation; obj = asked.node("o").label
        gloss = f"{subj} {rel.lower().replace('_', ' ')} {obj}"
        checkpoint = self.runtime._expectation()
        rendered = None
        if plan.content and plan.content[0].layer != "speaker":
            try:
                rendered = self._render_item(plan.content[0])
            except Exception as exc:
                return self._commit(text, f"I cannot render that meaning yet ({type(exc).__name__}).", G.Act.REPORT_UNCERTAIN, {"gate": ["UNKNOWN_CONSTRUCTION"]}, t0, seq0, committed=False)
        if plan.act is G.Act.ANSWER and plan.required_marker is G.Marker.ASSERTED:
            reply = f"Yes. {rendered} That is a verified fact in my knowledge ({plan.content[0].evidence[-1]})."
        elif plan.act is G.Act.ANSWER and plan.required_marker is G.Marker.REPORTED and plan.content and plan.content[0].layer == "source":
            reply = f"A source ({plan.content[0].source}) says so, but I have not verified it: {rendered}"
        elif plan.act is G.Act.ANSWER and plan.content and plan.content[0].layer == "speaker":
            item = plan.content[0]
            polarity = "it did not" if item.negated else "so"
            reply = f"{item.source} said {polarity} ({item.evidence[0]}); I have no independent warrant."
        elif plan.act is G.Act.REPORT_UNCERTAIN:
            reply = "I have contradictory statements on record about that; I cannot say."
        elif "revoked" in plan.open_checks:
            reply = f"I used to have support for '{gloss}', but it was revoked; I do not assert it now."
        else:
            reply = f"I do not know whether {gloss}; it is outside what I have verified."
        gp = plan.gate_plan()
        surface = G.Surface(reply, gp.meaning, plan.required_marker)
        verdict = G.commit_gate(gp, surface, self.dialogue._liveness, resolved=[e.entity_id for e in self.dialogue.workspace.entities.values()])
        if checkpoint != self.runtime._expectation():
            verdict = G.GateVerdict(False, verdict.events+(G.FeedbackEvent(G.FeedbackKind.RENDERER_CAPABILITY,"runtime changed during codec execution","render"),))
        if not verdict.committed:
            reply = "I cannot say that yet: " + "; ".join(f"{e.kind.value} ({e.reopen_stage})" for e in verdict.events)
        return self._commit(text, reply, plan.act, {"plan": self._plan_dict(plan), "gate": [e.kind.value for e in verdict.events]}, t0, seq0, committed=verdict.committed, evidence=tuple(e for c in plan.content for e in c.evidence))

    def _render_item(self, c: P.ContentItem) -> str:
        # A free-form source gloss is not a semantic certificate.
        return ST.world_clause(c.meaning)

    def _checked_items(self, items):
        checkpoint = self.runtime._expectation()
        try:
            rendered = [(c, self._render_item(c)) for c in items]
        except Exception as exc:
            return None, (G.FeedbackEvent(G.FeedbackKind.UNKNOWN_CONSTRUCTION, f"renderer unavailable: {type(exc).__name__}", "render"),)
        # Recheck every warrant after all renderer callbacks, including cross-item revocation.
        for c, text in rendered:
            gp = G.ResponsePlan(G.Act.ASSERT, c.meaning,
                (G.Assertion(c.digest, c.evidence, c.layer),), c.marker,
                source_name=c.source, reported_negative=c.negated)
            spoken = f"{c.source} said {text}" if c.marker is G.Marker.REPORTED else text
            verdict = G.commit_gate(gp, G.Surface(spoken, c.meaning, c.marker), self.dialogue._liveness)
            if not verdict.committed:
                return None, verdict.events
        if checkpoint != self.runtime._expectation():
            return None, (G.FeedbackEvent(G.FeedbackKind.RENDERER_CAPABILITY, "runtime changed during rendering", "render"),)
        return [f"{c.source} said {text}" if c.marker is G.Marker.REPORTED else text for c,text in rendered], ()

    def _explain(self, text: str, label: str, t0: float, seq0: int) -> str:
        plan = P.plan_explain(self.world, label, register=self.register)
        if plan.act is G.Act.REPORT_UNKNOWN:
            reply = f"I do not have anything verified about '{label}'."
        else:
            n = {"brief": 1, "neutral": 3, "detailed": 6}.get(self.register, 3)
            parts, failures = self._checked_items(plan.content[:n])
            if failures:
                return self._commit(text, "I cannot say that yet: actual text or warrant failed verification.", G.Act.REPORT_UNCERTAIN, {"plan": self._plan_dict(plan), "gate": [e.kind.value for e in failures]}, t0, seq0, committed=False)
            lead = "" if self.register == "casual" else ""
            reply = " ".join(parts)
            if plan.events:
                reply += " (I lack facts about: " + ", ".join(e.detail.replace("no live facts about ", "") for e in plan.events) + ".)"
            if any(c.marker is G.Marker.REPORTED for c in plan.content[:n]):
                reply += " Some of this is source-reported, not verified."
        return self._commit(text, reply, plan.act, {"plan": self._plan_dict(plan)}, t0, seq0, evidence=tuple(e for c in plan.content for e in c.evidence))

    def _compare(self, text: str, a: str, b: str, t0: float, seq0: int) -> str:
        plan = P.plan_compare(self.world, a, b, register=self.register)
        if plan.act is G.Act.REPORT_UNKNOWN:
            reply = f"I do not have verified facts to compare {a} and {b}."
        else:
            shared = [o.split(":", 1)[1] for o in plan.clause_obligations if o.startswith("shared:")]
            diff = [o.split(":", 1)[1] for o in plan.clause_obligations if o.startswith("differs:")]
            reply = f"Comparing {a} and {b}: " + ("they share " + "; ".join(shared) + ". " if shared else "they share nothing I have on record. ") + ("They differ in " + "; ".join(diff) + "." if diff else "")
        return self._commit(text, reply, plan.act, {"plan": self._plan_dict(plan)}, t0, seq0, evidence=tuple(e for c in plan.content for e in c.evidence))

    def _summary(self, text: str, t0: float, seq0: int) -> str:
        ws = self.dialogue.workspace
        items = ws.active_commitments()
        if not items:
            return self._commit(text, "Nothing has been said on record yet.", G.Act.REPORT_UNKNOWN, {}, t0, seq0)
        parts = [f"{c.speaker} said {'not ' if c.negated else ''}{_describe(MeaningGraph.from_dict(c.meaning))}" for c in items]
        return self._commit(text, "So far: " + "; ".join(parts) + ".", G.Act.ASSERT, {}, t0, seq0, evidence=tuple(c.evidence_id for c in items))

    # ------------------------------------------------------------------ learning in chat
    def _teach(self, text: str, t0: float, seq0: int) -> str:
        body = text.strip()[len("teach:"):].strip()
        low = body.lower()
        if low.startswith("construction "):
            # teach: construction <utterance> => <agent> <verb> <patient>
            utt, _, gold = body[len("construction "):].partition("=>")
            a, v, p = [x.strip() for x in gold.strip().split()]
            m = MeaningGraph((MNode("x1", "entity", a, (("definite", "yes"),)), MNode("e", "event", v), MNode("x2", "entity", p, (("definite", "yes"),))), (MEdge("ROLE:agent", ("e",), ("x1",)), MEdge("ROLE:patient", ("e",), ("x2",)), MEdge("TENSE", ("e",), ("e",), "past")), root="e")
            if "transitive" not in self.dialogue.families:
                seed = {c.construction_id: c for c in C.seed_constructions()}
                N, V = L.Category.NOUN, L.Category.VERB
                hyps = AQ.order_hypotheses([("S", C.Slot("subj", N, phrase="NP")), ("V", C.Slot("verb", V, requires=("tense",))), ("O", C.Slot("obj", N, phrase="NP"))])
                self.dialogue.register_family(AQ.ConstructionFamily("transitive", hyps, seed["en:transitive"].template, query_family=(utt.strip(),), helpers=(seed["en:np"],)))
            mt = self.dialogue.demonstrate("transitive", utt.strip(), m, speaker="user")
            self._save_learned()
            return self._commit(text, mt.text, G.Act.ACKNOWLEDGE, {"learning": "construction", "evidence": list(mt.evidence)}, t0, seq0, evidence=mt.evidence)
        # teach: <word> = <concept> [as noun|verb]   or   teach: <utterance> => <agent> <verb> <patient> (aligned example)
        if "=>" in body:
            utt, _, gold = body.partition("=>")
            a, v, p = [x.strip() for x in gold.strip().split()]
            m = MeaningGraph((MNode("x1", "entity", a, (("definite", "yes"),)), MNode("e", "event", v), MNode("x2", "entity", p, (("definite", "yes"),))), (MEdge("ROLE:agent", ("e",), ("x1",)), MEdge("ROLE:patient", ("e",), ("x2",)), MEdge("TENSE", ("e",), ("e",), "past")), root="e")
            _, eid = self.runtime.admit_evidence({"aligned": utt.strip(), "meaning": m.as_dict()}, Channel.DEMONSTRATION, "user", scope=Scope.of(self.conversation_id))
            eid_chat = eid
            u = LX.learn_word(self.dialogue.lexicon, utt.strip(), m, eid_chat, source="user")
            self._save_learned()
            reply = f"Learned '{u.lemma}' ↦ {u.detail.split('↦')[-1].strip()} from your example ({eid})." if u.kind in ("NEW_LEXEME", "NEW_SENSE") else f"I could not learn from that example: {u.detail}"
            return self._commit(text, reply, G.Act.ACKNOWLEDGE, {"learning": u.kind, "evidence": [eid]}, t0, seq0, evidence=(eid,))
        try:
            word, concept, cat = parse_lexical_lesson(body)
        except ValueError:
            return self._commit(text, "I cannot learn that format. Give a word and its meaning.", G.Act.REQUEST, {}, t0, seq0)
        # each giving of a lesson is a distinct observation (turn-stamped): relearning after a
        # revocation must not collapse onto the revoked record's bytes (ledger S24)
        _, eid = self.runtime.admit_evidence({"lesson": f"{word} = {concept}", "turn": len(self.dialogue.workspace.turns) + 1}, Channel.INSTRUCTION, "user", scope=Scope.of(self.conversation_id))
        add_lexical_lesson(self.dialogue.lexicon, word, concept, eid, cat)
        self._save_learned()
        return self._commit(text, f"Noted: '{word}' means {concept} ({eid}). I will use it.", G.Act.ACKNOWLEDGE, {"learning": "lesson", "evidence": [eid]}, t0, seq0, evidence=(eid,))

    def _revoke(self, text: str, eid: str, t0: float, seq0: int) -> str:
        if eid not in self.runtime.state.evidence.records:
            return self._commit(text, f"{eid} is not on my ledger.", G.Act.REPORT_UNKNOWN, {}, t0, seq0)
        affected = [lex for lex in self.dialogue.lexicon.lexemes.values()
                    if eid in lex.warrant.evidence or any(eid in sense.warrant.evidence for sense in lex.senses)]
        rep = self.runtime.revoke([eid])
        revoked = self.runtime.state.evidence.revoked
        remainder = []
        for lex in affected:
            for sense in lex.live_senses(revoked):
                profile = lex.warrant.meet(sense.warrant)
                if not profile.is_live(revoked):
                    continue
                supports = [sorted(map(str, w)) for w in profile.lower if not (w & revoked)]
                row = {"word": lex.lemma, "concept": sense.concept, "supports": supports}
                if row not in remainder:
                    remainder.append(row)
        reply = f"Revoked {eid}; reopened {sorted(rep.reopen)}, rechecked {sorted(rep.recheck)}."
        if remainder:
            descriptions = [f"'{r['word']}' as '{r['concept']}' still supported by {r['supports']}" for r in remainder]
            reply += " Other lexical support remains: " + "; ".join(descriptions) + "."
        return self._commit(text, reply, G.Act.ACKNOWLEDGE, {"reopen": sorted(rep.reopen), "revocation_remainder": remainder}, t0, seq0)

    # ------------------------------------------------------------------ commit + trace
    def _commit(self, utterance: str, reply: str, act: G.Act, bits: dict, t0: float, seq0: int, *, committed: bool = True, evidence: Sequence[str] = (), machine_turn_recorded: bool = False) -> str:
        ws = self.dialogue.workspace
        if self.input_guess:
            bits = {**bits, "interpretation": {**bits.get("interpretation", {}), "input": dict(self.input_guess)}}
            utterance = self.input_guess["original"]
            if self.input_guess["status"] == "SPELLING_GUESS":
                reply = f"Assuming you meant '{self.input_guess['interpreted']}': " + reply
        if not machine_turn_recorded:
            ws.record_turn("user", utterance, "ASSERT", "INPUT")
            ws.record_turn("machine", reply, act.value, "COMMITTED" if committed else "GATE_REFUSED", evidence=evidence)
        evs = self.runtime.events[seq0:]
        tr = TurnTrace(len(ws.turns), utterance, bits.get("interpretation", {}), {"entities": len(ws.entities), "active_commitments": len(ws.active_commitments()), "topic": ws.current_topic, "open_items": len(ws.unresolved())}, sorted({e for e in evidence}), sorted({getattr(e, "operator", "") or "" for e in evs}), bits.get("gate", []) + bits.get("events", []), bits.get("plan", {}), {"register": self.register, "contractions": self.style.contractions}, list(evidence), {"wall_s": round(time.perf_counter() - t0, 4), "ledger_events": len(evs), "kso_atoms": len(self.runtime.state.ks.atoms) if hasattr(self.runtime.state, "ks") else None}, reply, [getattr(e, "sequence", -1) for e in evs])
        self.traces.append(tr)
        self.runtime.persist()
        return reply

    def _interp_dict(self, r) -> dict[str, Any]:
        if r is None:
            return {}
        return {"verdict": r.verdict.value, "reason": r.reason, "candidates": [{"construction": c.construction_id, "digest": canonical(c.meaning)[1][:12], "evidence": sorted(c.warrant.evidence)} for c in r.candidates]}

    def _plan_dict(self, plan: P.ResponsePlan) -> dict[str, Any]:
        return {"act": plan.act.value, "goal": plan.goal, "rhetorical": plan.rhetorical.value, "marker": plan.required_marker.value, "content": [{"digest": c.digest[:12], "layer": c.layer, "marker": c.marker.value, "evidence": list(c.evidence)} for c in plan.content], "obligations": list(plan.clause_obligations), "open_checks": list(plan.open_checks), "events": [e.kind.value for e in plan.events]}

    def last_trace(self) -> dict[str, Any]:
        t = self.traces[-1]
        return {k: getattr(t, k) for k in ("turn_id", "utterance", "interpretation", "dialogue_state", "kso_objects", "operators", "checks", "response_plan", "sentence_plan", "warrant_ids", "resources", "committed_response", "ledger_events")}
