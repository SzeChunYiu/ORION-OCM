"""M4 target loop end-to-end: statements, questions with evidence, pronouns through the workspace,
clarification only when it matters, correction as supersession that reopens, restart, gate."""
from __future__ import annotations

from ocm.dialogue import gate as G
from ocm.dialogue import session as S
from ocm.dialogue import workspace as WS
from ocm.language import constructions as C
from ocm.language import lexicon as L
from ocm.language import meaning as M
from ocm.kso.warrant import WarrantProfile as WP
from ocm.runtime.ocm_runtime import OCMRuntime
from tests.m3.test_interpretation import _lexicon


def _lex():
    lx = _lexicon()
    ev = lambda n: WP.of({f"ev:{n}"})  # noqa: E731
    for n in ("key", "box", "cat"):
        lx.add(L.Lexeme(n, L.Category.NOUN, (L.Sense(n, n, "entity", ev(n)),)))
    lx.add(L.Lexeme("push", L.Category.VERB, (L.Sense("push", "push", "event", ev("push")),)))
    return lx


def _dr(tmp_path, conv="c1"):
    return S.DialogueRuntime(OCMRuntime(tmp_path / "rt"), _lex(), list(C.seed_constructions()), conv)


def test_conversation_loop_with_evidence_pronoun_and_restart(tmp_path):
    d = _dr(tmp_path)
    t = d.hear("the robot opened the door", "alice")
    assert t.act is G.Act.ACKNOWLEDGE and t.committed and len(t.evidence) == 1
    assert {e.descriptions[0] for e in d.workspace.entities.values()} == {"the robot", "the door"}
    a = d.hear("did the robot open the door", "bob")
    assert a.act is G.Act.ANSWER and a.committed and "alice said so" in a.text and a.evidence == t.evidence
    # a pronoun with two inanimate candidates matters (it changes what is asserted) → clarification
    p = d.hear("which door did it open", "bob")
    assert p.act is G.Act.CLARIFY and "Which do you mean by 'it'" in p.text
    # restart from disk: same workspace hash, same answer
    h = d.workspace.state_hash()
    d2 = S.DialogueRuntime.resume(tmp_path / "rt", _lex(), C.seed_constructions(), "c1")
    assert d2.workspace.state_hash() == h
    a2 = d2.hear("did the robot open the door", "carol")
    assert a2.committed and a2.evidence == t.evidence


def test_clarification_only_when_it_matters_and_collapse_is_interaction_evidence(tmp_path):
    d = _dr(tmp_path)
    c = d.hear("the robot saw the bank", "alice")
    assert c.act is G.Act.CLARIFY and len(c.candidates) == 2       # the readings assert different things
    ans = d.hear("2", "alice")
    assert ans.act is G.Act.ACKNOWLEDGE and ans.committed
    kinds = [r.channel.value for r in d.runtime.state.evidence.records.values()]
    assert "interaction" in kinds and "observation" in kinds
    assert d.workspace.unresolved("reference") == []


def test_correction_supersedes_and_the_answer_reopens_while_unrelated_state_stays(tmp_path):
    d = _dr(tmp_path)
    d.workspace.push_topic("doors")
    t1 = d.hear("the robot opened the door", "alice")
    d.hear("the cat pushed the box", "alice")
    assert "alice said so" in d.hear("did the robot open the door", "bob").text
    corr = d.hear("correction, the robot did not open the door", "alice")
    assert corr.committed and "supersedes" in corr.text
    old = [c for c in d.workspace.commitments.values() if c.evidence_id == t1.evidence[0]][0]
    assert old.status is WS.CommitmentStatus.SUPERSEDED and old.evidence_id in d.runtime.state.revoked
    assert "said it did not" in d.hear("did the robot open the door", "bob").text          # reopened conclusion
    assert "alice said so" in d.hear("did the cat push the box", "bob").text               # unrelated commitment intact
    assert len(d.workspace.turns) >= 7                                                     # history immutable, nothing deleted


def test_unknown_construction_becomes_an_obligation_learned_by_demonstration(tmp_path):
    from ocm.language import acquisition as AQ
    d = _dr(tmp_path)
    d.constructions = [c for c in d.constructions if c.construction_id != "en:transitive"]
    g = d.hear("the cat pushed the box", "alice")
    assert g.act is G.Act.REQUEST and d.workspace.unresolved("obligation")
    seed = {c.construction_id: c for c in C.seed_constructions()}
    N, V = L.Category.NOUN, L.Category.VERB
    hyps = AQ.order_hypotheses([("S", C.Slot("subj", N, phrase="NP")), ("V", C.Slot("verb", V, requires=("tense",))), ("O", C.Slot("obj", N, phrase="NP"))])
    d.register_family(AQ.ConstructionFamily("transitive", hyps, seed["en:transitive"].template, query_family=("the cat pushed the box", "the key opened the door"), helpers=(seed["en:np"],)))
    m = M.MeaningGraph((M.MNode("x1", "entity", "cat", (("definite", "yes"),)), M.MNode("e", "event", "push"), M.MNode("x2", "entity", "box", (("definite", "yes"),))), (M.MEdge("ROLE:agent", ("e",), ("x1",)), M.MEdge("ROLE:patient", ("e",), ("x2",)), M.MEdge("TENSE", ("e",), ("e",), "past")), root="e")
    l = d.demonstrate("transitive", "the cat pushed the box", m)
    assert "Learned" in l.text and d.workspace.unresolved("obligation") == []
    assert d.hear("the key opened the door", "alice").committed


def test_gate_refuses_a_plan_the_state_cannot_support(tmp_path):
    d = _dr(tmp_path)
    m = M.example_meanings()["the robot did not open the door"]
    dg = M.canonical(m)[1]
    plan = G.ResponsePlan(G.Act.ANSWER, m, (G.Assertion(dg, ("ev:none",), "machine"),), G.Marker.ASSERTED)
    t = d._reply(G.Act.ANSWER, "The robot did not open the door.", plan=plan)
    assert not t.committed and any(e.kind is G.FeedbackKind.UNSUPPORTED_ASSERTION for e in t.events)
    assert d.workspace.turns[-1].verdict == "GATE_REFUSED"
