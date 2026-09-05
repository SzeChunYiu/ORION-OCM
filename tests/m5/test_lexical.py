"""M5 §3 curriculum: new word from one aligned example → unseen contexts → second sense →
context disambiguation → revoke first sense (locality) → relearn from a new source."""
from __future__ import annotations

from ocm.kso.warrant import Liveness
from ocm.language import constructions as C
from ocm.language import interpret as I
from ocm.language import lexicon as L
from ocm.language import meaning as M
from ocm.learning.language import lexical as LX
from tests.m3.test_interpretation import _lexicon

CONS = C.seed_constructions()


def tr(agent, verb, patient, adj=None):
    nodes = [M.MNode("x1", "entity", agent, (("definite", "yes"),)), M.MNode("e", "event", verb), M.MNode("x2", "entity", patient, (("definite", "yes"),))]
    edges = [M.MEdge("ROLE:agent", ("e",), ("x1",)), M.MEdge("ROLE:patient", ("e",), ("x2",)), M.MEdge("TENSE", ("e",), ("e",), "past")]
    if adj:
        nodes.append(M.MNode("p", "property", adj))
        edges.append(M.MEdge("MODIFIES", ("p",), ("x2",)))
    return M.MeaningGraph(tuple(nodes), tuple(edges), root="e")


def test_word_lifecycle_one_example_reuse_second_sense_revocation_locality_relearn():
    lx = _lexicon()
    assert I.interpret("the robot opened the crate", lx, CONS).verdict is I.Verdict.UNKNOWN_LEXEME
    # 1. one aligned example teaches the noun
    u = LX.learn_word(lx, "the robot opened the crate", tr("robot", "open", "crate"), "ev:demo1")
    assert u.kind == "NEW_LEXEME" and u.lemma == "crate" and u.evidence == ("ev:demo1",)
    # 2. unseen grammatical contexts (passive, negation, adjective, question)
    for utt, gold in [("the crate was opened by the robot", tr("robot", "open", "crate")), ("the robot did not open the red crate", None), ("did the robot open the crate", None)]:
        r = I.interpret(utt, lx, CONS)
        assert r.verdict is I.Verdict.INTERPRETED, (utt, r.reason)
        if gold is not None:
            assert M.isomorphic(r.meaning, gold)
    assert "ev:demo1" in I.interpret("the crate was opened by the robot", lx, CONS).candidates[0].warrant.evidence
    # 3. second sense of the same surface word ('crate' as a box-shaped event? no: a second concept)
    u2 = LX.learn_word(lx, "the robot opened the crate", tr("robot", "open", "shipping_container"), "ev:demo2", source="warehouse")
    assert u2.kind == "NEW_SENSE" and u2.lemma == "crate"
    # 4. context-sensitive disambiguation: without context the readings are retained as an ambiguity set
    r = I.interpret("the robot opened the crate", lx, CONS)
    assert r.verdict is I.Verdict.AMBIGUOUS and len(r.candidates) == 2
    # 5–6. revoke the first sense's evidence: the second sense remains; unrelated vocabulary untouched
    r5 = I.interpret("the robot opened the crate", lx, CONS, revoked={"ev:demo1"})
    assert r5.verdict is I.Verdict.INTERPRETED and r5.meaning.node("x2").label == "shipping_container"
    assert I.interpret("the robot opened the door", lx, CONS, revoked={"ev:demo1"}).verdict is I.Verdict.INTERPRETED
    # 7. relearn the first sense from a new source: new record with lineage, old stays dead
    u7 = LX.relearn_sense(lx, "crate", L.Category.NOUN, "crate", "entity", "ev:demo3", replaces="crate:crate")
    assert u7.lineage == ("crate:crate",)
    senses = {s.sense_id: s for s in lx.lexemes["crate|N"].senses}
    assert senses["crate:crate"].liveness({"ev:demo1"}) is Liveness.DEAD and senses["crate:crate#2"].liveness({"ev:demo1"}) is Liveness.LIVE


def test_alignment_refuses_when_it_cannot_be_exact():
    lx = _lexicon()
    a = LX.align(lx, "the zorb glipped the door", tr("zorb", "glip", "door"))
    assert a.status is LX.AlignmentStatus.TOO_MANY_UNKNOWN
    a2 = LX.align(lx, "the robot opened the crate", tr("robot", "open", "door"))
    assert a2.status is LX.AlignmentStatus.NO_UNACCOUNTED_NODE
    assert LX.learn_word(lx, "the zorb glipped the door", tr("zorb", "glip", "door"), "ev:x").kind == "REFUSED"
    assert "crate" not in {k.split("|")[0] for k in lx.lexemes}


def test_cooccurrence_never_grounds_and_the_mutant_does():
    lx = _lexicon()
    # a word the raw corpus miner saw next to 'door' 100 times is still UNKNOWN to the interpreter
    assert I.interpret("the robot opened the portal", lx, CONS).verdict is I.Verdict.UNKNOWN_LEXEME
    m = LX.mutant_learn_from_cooccurrence(lx, "portal", "door", "ev:corpus-cooc")
    assert m.kind == "NEW_LEXEME" and I.interpret("the robot opened the portal", lx, CONS).verdict is I.Verdict.INTERPRETED   # the laundering the rule forbids


def test_competence_curve_point():
    lx = _lexicon()
    probes = [("the robot opened the door", tr("robot", "open", "door")), ("the robot opened the crate", tr("robot", "open", "crate"))]
    before = LX.competence(lx, CONS, probes)
    LX.learn_word(lx, "the robot opened the crate", tr("robot", "open", "crate"), "ev:demo1")
    after = LX.competence(lx, CONS, probes)
    assert (before["exact"], after["exact"]) == (1, 2) and after["n"] == 2
