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

DEFAULT_MANIFEST = Path(__file__).resolve().parents[3] / "research" / "ocm-m6" / "KNOWLEDGE_MANIFEST_V1.json"

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


def _load_lexicon_and_constructions(state_dir: Path) -> tuple[L.Lexicon, list[C.Construction]]:
    from tests.m3.test_microworld import _lexicon_for

    lx = _lexicon_for(())
    ev = lambda n: WarrantProfile.of({f"ev:lex:{n}"})  # noqa: E731
    # bounded-world vocabulary (nouns from the manifest labels) + question words
    for w in ("which", "what", "who"):
        lx.add(L.Lexeme(w, L.Category.WH, ()))
    lx.add(L.Lexeme("it", L.Category.PRON, ()))
    lx.add(L.Lexeme("is", L.Category.AUX, (), (("tense", "present"),)))
    lx.add(L.Lexeme("a", L.Category.DET, ()))
    lx.add(L.Lexeme("an", L.Category.DET, ()))
    lx.add(L.Lexeme("in", L.Category.PREP, ()))
    lx.add(L.Lexeme("of", L.Category.PREP, ()))
    # a registered polysemous noun (ambiguity set) for the clarification scenario
    lx.add(L.Lexeme("bank", L.Category.NOUN, (L.Sense("bank:fin", "financial_institution", "entity", ev("bank-fin")), L.Sense("bank:river", "river_bank", "entity", ev("bank-river")))))
    try:
        man = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        labels = {f["subject"] for f in man["facts"]} | {f["object"] for f in man["facts"]}
        for lab in sorted(labels):
            if "_" in lab or f"{lab}|N" in lx.lexemes:
                continue
            lx.add(L.Lexeme(lab, L.Category.NOUN, (L.Sense(lab, lab, "entity", ev(lab)),)))
    except FileNotFoundError:
        pass
    return lx, list(C.seed_constructions())


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

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.runtime = OCMRuntime(self.root / "ledger")
        lx, cons = _load_lexicon_and_constructions(self.root)
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
        t0 = time.perf_counter()
        seq0 = len(self.runtime.events)
        low = text.strip().lower()
        # style requests (no factual change)
        for reg in ("brief", "detailed", "formal", "casual"):
            if low in (f"be {reg}", f"please be {reg}", f"{reg} please", f"answer {reg}ly"):
                self.register = reg
                self.style = RZ.Style(register=reg, contractions=(reg == "casual"))
                return self._commit(text, f"Understood — I will keep answers {reg}.", G.Act.ACKNOWLEDGE, {}, t0, seq0)
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
        mt = self.dialogue.hear(text, speaker)
        trace_bits = {"interpretation": self._interp_dict(mt.interpretation), "act": mt.act.value, "events": [e.kind.value for e in mt.events]}
        reply = mt.text
        if mt.act is G.Act.REQUEST and "cannot interpret" in mt.text:
            reply = mt.text + " (say: teach: <word> = <concept>, or teach: construction <utterance> => <agent> <verb> <patient>)"
        return self._commit(text, reply, mt.act, trace_bits, t0, seq0, committed=mt.committed, evidence=mt.evidence, machine_turn_recorded=True)

    # ------------------------------------------------------------------ bounded-world questions
    def _world_question(self, low: str) -> MeaningGraph | None:
        toks = tokenize(low)
        if not toks:
            return None
        if toks[0] in ("is", "does", "do") and len(toks) >= 4:
            body = [t for t in toks[1:] if t not in ("the", "a", "an")]
            if toks[0] == "is" and "capital" in body:
                i = body.index("capital")
                subj = " ".join(body[:i]); obj = " ".join(body[i + 1:]).replace("of ", "")
                return triple(subj, "CAPITAL_OF", obj)
            if toks[0] == "is" and "in" in toks:
                i = toks.index("in")
                subj = " ".join(t for t in toks[1:i] if t not in ("the",)); obj = " ".join(t for t in toks[i + 1:] if t not in ("the",))
                return triple(subj, "LOCATED_IN", obj)
            if toks[0] == "is" and any(t in ("a", "an") for t in toks[2:]):
                start = 2 if toks[1] in ("a", "an", "the") else 1          # "is a whale a mammal" / "is the moon a planet"
                i = next(k for k, t in enumerate(toks) if k >= start + 1 and t in ("a", "an"))
                subj = " ".join(t for t in toks[start:i] if t != "the"); obj = " ".join(toks[i + 1:])
                return triple(subj, "IS_A", obj)
            if toks[0] == "does" and len(body) >= 3 and body[1] in RELATION_WORDS:
                return triple(body[0], RELATION_WORDS[body[1]], " ".join(body[2:]))
        return None

    def _answer_world(self, text: str, asked: MeaningGraph, t0: float, seq0: int) -> str:
        plan = P.plan_answer(self.world, self.dialogue.workspace, asked, register=self.register)
        subj = asked.node("s").label; rel = asked.edges[0].relation; obj = asked.node("o").label
        gloss = f"{subj} {rel.lower().replace('_', ' ')} {obj}"
        if plan.act is G.Act.ANSWER and plan.required_marker is G.Marker.ASSERTED:
            reply = f"Yes. {self._render_item(plan.content[0])} That is a verified fact in my knowledge ({plan.content[0].evidence[-1]})."
        elif plan.act is G.Act.ANSWER and plan.required_marker is G.Marker.REPORTED and plan.content and plan.content[0].layer == "source":
            reply = f"A source ({plan.content[0].source}) says so, but I have not verified it: {self._render_item(plan.content[0])}"
        elif plan.act is G.Act.ANSWER and plan.content and plan.content[0].layer == "speaker":
            reply = f"Someone in this conversation said so ({plan.content[0].evidence[0]}); I have no independent warrant."
        elif plan.act is G.Act.REPORT_UNCERTAIN:
            reply = "I have contradictory statements on record about that; I cannot say."
        elif "revoked" in plan.open_checks:
            reply = f"I used to have support for '{gloss}', but it was revoked; I do not assert it now."
        else:
            reply = f"I do not know whether {gloss}; it is outside what I have verified."
        gp = plan.gate_plan()
        surface = G.Surface(reply, gp.meaning, plan.required_marker)
        verdict = G.commit_gate(gp, surface, self.dialogue._liveness, resolved=[e.entity_id for e in self.dialogue.workspace.entities.values()])
        if not verdict.committed:
            reply = "I cannot say that yet: " + "; ".join(f"{e.kind.value} ({e.reopen_stage})" for e in verdict.events)
        return self._commit(text, reply, plan.act, {"plan": self._plan_dict(plan), "gate": [e.kind.value for e in verdict.events]}, t0, seq0, committed=verdict.committed, evidence=tuple(e for c in plan.content for e in c.evidence))

    def _render_item(self, c: P.ContentItem) -> str:
        if c.gloss:
            g = c.gloss[0].upper() + c.gloss[1:] + "."
            return g
        return _describe(c.meaning)

    def _explain(self, text: str, label: str, t0: float, seq0: int) -> str:
        plan = P.plan_explain(self.world, label, register=self.register)
        if plan.act is G.Act.REPORT_UNKNOWN:
            reply = f"I do not have anything verified about '{label}'."
        else:
            n = {"brief": 1, "neutral": 3, "detailed": 6}.get(self.register, 3)
            parts = [self._render_item(c) for c in plan.content[:n]]
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
        word, _, concept = body.partition("=")
        word, concept = word.strip().lower(), concept.strip().lower()
        cat = L.Category.NOUN
        if concept.endswith(" as verb"):
            concept, cat = concept[: -len(" as verb")].strip(), L.Category.VERB
        _, eid = self.runtime.admit_evidence({"lesson": f"{word} = {concept}"}, Channel.INSTRUCTION, "user", scope=Scope.of(self.conversation_id))
        ntype = "event" if cat is L.Category.VERB else "entity"
        lx = self.dialogue.lexicon
        key = f"{word}|{cat.value}"
        sense = L.Sense(f"{word}:{concept}", concept, ntype, WarrantProfile.of({eid}))
        if key in lx.lexemes:
            old = lx.lexemes[key]
            lx.add(L.Lexeme(old.lemma, old.category, old.senses + (sense,), old.features, old.warrant, old.scope))
        else:
            lx.add(L.Lexeme(word, cat, (sense,)))
        self._save_learned()
        return self._commit(text, f"Noted: '{word}' means {concept} ({eid}). I will use it.", G.Act.ACKNOWLEDGE, {"learning": "lesson", "evidence": [eid]}, t0, seq0, evidence=(eid,))

    def _revoke(self, text: str, eid: str, t0: float, seq0: int) -> str:
        if eid not in self.runtime.state.evidence.records:
            return self._commit(text, f"{eid} is not on my ledger.", G.Act.REPORT_UNKNOWN, {}, t0, seq0)
        rep = self.runtime.revoke([eid])
        return self._commit(text, f"Revoked {eid}; reopened {sorted(rep.reopen)}, rechecked {sorted(rep.recheck)}.", G.Act.ACKNOWLEDGE, {"reopen": sorted(rep.reopen)}, t0, seq0)

    # ------------------------------------------------------------------ commit + trace
    def _commit(self, utterance: str, reply: str, act: G.Act, bits: dict, t0: float, seq0: int, *, committed: bool = True, evidence: Sequence[str] = (), machine_turn_recorded: bool = False) -> str:
        ws = self.dialogue.workspace
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
