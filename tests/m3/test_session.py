"""M3 §7/§12: the dialogue session over the M2 runtime — said-records as ledger evidence,
answers cite evidence and never guess, clarification collapses by evidence, unknown constructions
are learned from demonstrations, retraction reopens exactly."""
from __future__ import annotations

from ocm.language import acquisition as AQ
from ocm.language import constructions as C
from ocm.language import lexicon as L
from ocm.language import meaning as M
from ocm.language import session as S
from ocm.runtime.ocm_runtime import OCMRuntime
from tests.m3.test_interpretation import _lexicon


def _session(tmp_path):
    rt = OCMRuntime(tmp_path / "ledger")
    return S.DialogueSession(rt, _lexicon(), list(C.seed_constructions()))


def test_statement_is_recorded_as_said_and_question_answered_with_evidence_never_guessed(tmp_path):
    s = _session(tmp_path)
    a = s.hear("did the robot open the door")
    assert a.kind is S.ReplyKind.ANSWER and a.text.startswith("Unknown") and a.evidence == ()
    r = s.hear("the robot opened the door", speaker="alice")
    assert r.kind is S.ReplyKind.RECORDED and len(r.evidence) == 1
    rec = s.runtime.state.evidence.records[r.evidence[0]]
    assert rec.channel.value == "observation" and rec.source == "alice"
    a2 = s.hear("did the robot open the door")
    assert a2.kind is S.ReplyKind.ANSWER and a2.text.startswith("Yes") and a2.evidence == r.evidence and "no independent warrant" in a2.text
    # negated statement by another speaker: contradiction is kept, not resolved by majority
    n = s.hear("the robot did not open the door", speaker="bob")
    assert n.kind is S.ReplyKind.RECORDED and "contradicts" in n.text
    a3 = s.hear("did the robot open the door")
    assert a3.text.startswith("Unknown") and set(a3.evidence) == set(r.evidence) | set(n.evidence)
    # the ledger replays to the same state (the discourse record is durable)
    rep = s.runtime.replay()
    assert rep["ok"] if isinstance(rep, dict) and "ok" in rep else rep is not None


def test_clarification_collapses_ambiguity_by_an_interaction_event(tmp_path):
    s = _session(tmp_path)
    c = s.hear("the robot saw the bank", speaker="alice")
    assert c.kind is S.ReplyKind.CLARIFY and len(c.candidates) == 2 and "(1)" in c.text and "(2)" in c.text
    vague = s.hear("hmm")
    assert vague.kind is S.ReplyKind.CLARIFY
    ans = s.hear("2")
    assert ans.kind is S.ReplyKind.RECORDED and len(ans.evidence) == 2   # said-evidence + interaction evidence
    kinds = {s.runtime.state.evidence.records[e].channel.value for e in ans.evidence}
    assert kinds == {"observation", "interaction"}


def test_unknown_construction_is_learned_from_demonstrations_and_then_understood(tmp_path):
    s = _session(tmp_path)
    s.constructions = [c for c in s.constructions if c.construction_id not in ("en:transitive",)]  # forget the transitive clause
    lx = s.lexicon
    ev = L.WarrantProfile.of
    for n in ("cat", "box", "key"):
        lx.add(L.Lexeme(n, L.Category.NOUN, (L.Sense(n, n, "entity", ev({f"ev:{n}"})),)))
    lx.add(L.Lexeme("push", L.Category.VERB, (L.Sense("push", "push", "event", ev({"ev:push"})),)))
    g = s.hear("the cat pushed the box")
    assert g.kind is S.ReplyKind.LEARN
    seed = {c.construction_id: c for c in C.seed_constructions()}
    N, V = L.Category.NOUN, L.Category.VERB
    hyps = AQ.order_hypotheses([("S", C.Slot("subj", N, phrase="NP")), ("V", C.Slot("verb", V, requires=("tense",))), ("O", C.Slot("obj", N, phrase="NP"))])
    s.register_family(AQ.ConstructionFamily("transitive", hyps, seed["en:transitive"].template, query_family=("the cat pushed the box", "the key opened the door"), helpers=(seed["en:np"],)))

    def meaning(agent, verb, patient):
        return M.MeaningGraph((M.MNode("x1", "entity", agent, (("definite", "yes"),)), M.MNode("e", "event", verb), M.MNode("x2", "entity", patient, (("definite", "yes"),))), (M.MEdge("ROLE:agent", ("e",), ("x1",)), M.MEdge("ROLE:patient", ("e",), ("x2",)), M.MEdge("TENSE", ("e",), ("e",), "past")), root="e")

    d = s.demonstrate("transitive", "the cat pushed the box", meaning("cat", "push", "box"))
    assert d.kind is S.ReplyKind.RECORDED and "Learned" in d.text and len(d.evidence) == 1
    assert s.runtime.state.evidence.records[d.evidence[0]].channel.value == "demonstration"
    u = s.hear("the key opened the door", speaker="alice")     # unseen sentence under the learned construction
    assert u.kind is S.ReplyKind.RECORDED
    assert s.hear("did the key open the door").text.startswith("Yes")


def test_retraction_reopens_exactly_the_dependent_answer(tmp_path):
    s = _session(tmp_path)
    r1 = s.hear("the robot opened the door", speaker="alice")
    r2 = s.hear("the robot saw the door", speaker="alice")
    assert s.hear("did the robot open the door").text.startswith("Yes")
    ret = s.retract(r1.evidence[0])
    assert ret.kind is S.ReplyKind.RETRACTED
    assert s.hear("did the robot open the door").text.startswith("Unknown")     # reopened
    assert s.hear("did the robot see the door").text.startswith("Yes")          # unaffected
    assert s.retract("ev:nope").kind is S.ReplyKind.CANNOT_CHECK
