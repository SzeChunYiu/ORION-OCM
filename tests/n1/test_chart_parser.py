"""N1: the packed-forest chart parser agrees with the M3 matcher on the bounded world and counts ambiguity exactly."""
from __future__ import annotations

from ocm.language import chart as CH
from ocm.language import constructions as C
from ocm.language import interpret as I
from ocm.language.meaning import canonical
from tests.m3.test_microworld import _lexicon_for


def _lexicon():
    lx = _lexicon_for(())
    from ocm.kso.warrant import WarrantProfile as WP
    from ocm.language import lexicon as L
    lx.add(L.Lexeme("bank", L.Category.NOUN, (L.Sense("bank:fin", "financial_institution", "entity", WP.of({"e1"})), L.Sense("bank:river", "river_bank", "entity", WP.of({"e2"})))))
    return lx


def test_chart_agrees_with_matcher_on_the_bounded_world_and_counts_ambiguity():
    lx = _lexicon()
    cons = list(C.seed_constructions())
    for utt in ("the girl lifted the cup", "the robot opened the door", "the big dog kicked the ball", "the door was opened by the robot", "did the robot open the door", "the robot did not open the door"):
        m = I.interpret(utt, lx, cons)
        r = CH.parse(I.tokenize(utt), lx, cons)
        assert r["verdict"] == "INTERPRETED" == m.verdict.value, (utt, r["verdict"], m.verdict)
        assert canonical(r["meanings"][0]["meaning"])[1] == canonical(m.candidates[0].meaning)[1], utt
    # polysemy: two readings of 'bank' → exactly two derivations, matcher says AMBIGUOUS too
    m = I.interpret("the bank saw the robot", lx, cons)
    r = CH.parse(I.tokenize("the bank saw the robot"), lx, cons)
    assert m.verdict is I.Verdict.AMBIGUOUS and r["verdict"] == "AMBIGUOUS" and r["count"] == 2
    assert {canonical(x["meaning"])[1] for x in r["meanings"]} == {canonical(c.meaning)[1] for c in m.candidates}
    assert CH.mutant_first_derivation_only(r)["verdict"] == "INTERPRETED"        # the hostile hides the ambiguity
    # unknown word / unknown construction
    assert CH.parse(I.tokenize("the zorb lifted the cup"), lx, cons)["verdict"] == "UNKNOWN_LEXEME"
    assert CH.parse(I.tokenize("girl cup lifted"), lx, cons)["verdict"] == "UNKNOWN_CONSTRUCTION"
