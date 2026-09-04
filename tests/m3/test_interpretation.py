"""M3 §5–§7 and §12 hostiles: constructions, candidate warrants, verdicts, grounding boundary."""
from __future__ import annotations

from ocm.kso.nogoods import NogoodSet
from ocm.kso.types import Authority
from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.language import constructions as C
from ocm.language import interpret as I
from ocm.language import lexicon as L
from ocm.language import meaning as M


def _lexicon():
    lx = L.Lexicon()
    ev = lambda n: WP.of({f"ev:{n}"})  # noqa: E731
    lx.add(L.Lexeme("the", L.Category.DET, ()))
    lx.add(L.Lexeme("robot", L.Category.NOUN, (L.Sense("robot", "robot", "entity", ev("robot")),)))
    lx.add(L.Lexeme("door", L.Category.NOUN, (L.Sense("door", "door", "entity", ev("door")),)))
    lx.add(L.Lexeme("red", L.Category.ADJ, (L.Sense("red", "red", "property", ev("red")),)))
    lx.add(L.Lexeme("open", L.Category.VERB, (L.Sense("open:ev", "open", "event", ev("open")),)))
    lx.add(L.Lexeme("bank", L.Category.NOUN, (L.Sense("bank:fin", "financial_institution", "entity", ev("bank-fin")), L.Sense("bank:river", "river_bank", "entity", ev("bank-river")))))
    lx.add(L.Lexeme("see", L.Category.VERB, (L.Sense("see", "see", "event", ev("see")),)))
    lx.add(L.Lexeme("do", L.Category.AUX, ()))
    lx.add(L.Lexeme("be", L.Category.AUX, ()))
    lx.add(L.Lexeme("not", L.Category.NEG, ()))
    lx.add(L.Lexeme("by", L.Category.PREP, ()))
    lx.add(L.Lexeme("which", L.Category.WH, ()))
    lx.add(L.Lexeme("it", L.Category.PRON, ()))
    lx.add_rule(L.MorphRule("past-ed", L.RuleKind.PRODUCTIVE, L.Category.VERB, (("tense", "past"),), lambda l: l + "ed", lambda s: s[:-2] if s.endswith("ed") else None, ev("rule-ed")))
    lx.add_rule(L.MorphRule("pp-ed", L.RuleKind.PRODUCTIVE, L.Category.VERB, (("participle", "past"),), lambda l: l + "ed", lambda s: s[:-2] if s.endswith("ed") else None, ev("rule-pp")))
    lx.add_rule(L.MorphRule("aux-did", L.RuleKind.EXCEPTION, L.Category.AUX, (("tense", "past"),), lambda l: "did", lambda s: "do" if s == "did" else None, ev("did"), lemmas=frozenset({"do"})))
    lx.add_rule(L.MorphRule("aux-was", L.RuleKind.EXCEPTION, L.Category.AUX, (("tense", "past"),), lambda l: "was", lambda s: "be" if s == "was" else None, ev("was"), lemmas=frozenset({"be"})))
    lx.add_rule(L.MorphRule("saw", L.RuleKind.EXCEPTION, L.Category.VERB, (("tense", "past"),), lambda l: "saw", lambda s: "see" if s == "saw" else None, ev("saw"), lemmas=frozenset({"see"})))
    return lx


CONS = C.seed_constructions()


def test_transitive_declarative_interpreted_with_composed_warrant_and_said_record():
    r = I.interpret("The robot opened the red door.", _lexicon(), CONS, speaker="alice")
    assert r.verdict is I.Verdict.INTERPRETED
    m = r.meaning
    assert M.isomorphic(m, M.example_meanings()["the robot opened the red door"])
    assert {"ev:robot", "ev:open", "ev:door", "ev:red", "ev:rule-ed", "ev:seed:transitive"} <= r.candidates[0].warrant.evidence
    assert r.said is not None and r.said.authority == Authority.of(speaker=1) and r.said.authority.rank("world_truth") == 0


def test_passive_negation_yesno_and_wh_map_to_the_required_meanings():
    lx = _lexicon()
    ex = M.example_meanings()
    p = I.interpret("the door was opened by the robot", lx, CONS)
    assert p.verdict is I.Verdict.INTERPRETED and M.isomorphic(p.meaning, ex["the door was opened by the robot"])
    n = I.interpret("the robot did not open the door", lx, CONS)
    assert n.verdict is I.Verdict.INTERPRETED and M.isomorphic(n.meaning, ex["the robot did not open the door"])
    q = I.interpret("did the robot open the door", lx, CONS)
    assert q.verdict is I.Verdict.INTERPRETED and M.isomorphic(q.meaning, ex["did the robot open the door"])
    w = I.interpret("which door did it open", lx, CONS, context_bindings={"x1": "atom:robot"})
    assert w.verdict is I.Verdict.INTERPRETED and M.isomorphic(w.meaning, ex["which door did it open"])
    w2 = I.interpret("which door did it open", lx, CONS)
    assert w2.verdict is I.Verdict.NEEDS_CONTEXT


def test_ambiguity_is_retained_and_collapses_only_by_evidence():
    lx = _lexicon()
    r = I.interpret("the robot saw the bank", lx, CONS)
    assert r.verdict is I.Verdict.AMBIGUOUS and len(r.candidates) == 2
    assert I.mutant_force_top1(r) is not None                      # the forced collapse the rule forbids
    r2 = I.interpret("the robot saw the bank", lx, CONS, revoked={"ev:bank-river"})
    assert r2.verdict is I.Verdict.INTERPRETED and r2.meaning.node("x2").label == "financial_institution"


def test_unknown_lexeme_and_unknown_construction_are_learn_gaps_not_guesses():
    lx = _lexicon()
    assert I.interpret("the robot opened the portal", lx, CONS).verdict is I.Verdict.UNKNOWN_LEXEME
    assert I.interpret("robot door robot", lx, CONS).verdict is I.Verdict.UNKNOWN_CONSTRUCTION


def test_hostile_mutants_differ_and_are_detectable():
    lx = _lexicon()
    tr = next(c for c in CONS if c.construction_id == "en:transitive")
    swapped = I.interpret("the robot opened the door", lx, [C.mutant_word_order_swap(tr)])
    good = I.interpret("the robot opened the door", lx, [tr])
    assert not M.isomorphic(swapped.meaning, good.meaning)
    neg = next(c for c in CONS if c.construction_id == "en:negation-transitive")
    dropped = I.interpret("the robot did not open the door", lx, [C.mutant_drop_negation(neg)])
    assert not any(e.relation == "NEGATES" for e in dropped.meaning.edges)


def test_contradiction_via_nogood_and_revoked_sense_never_returned():
    lx = _lexicon()
    ng = NogoodSet.of({"ev:robot", "ev:open"})
    r = I.interpret("the robot opened the door", lx, CONS, nogoods=ng)
    assert r.verdict is I.Verdict.CONTRADICTION
    r2 = I.interpret("the robot saw the bank", lx, CONS, revoked={"ev:bank-fin", "ev:bank-river"})
    assert r2.verdict is I.Verdict.UNKNOWN_LEXEME  # both senses dead: no live reading, nothing cached


def test_promotion_never_exceeds_the_bridge_and_speaker_record():
    said = I.SaidRecord("Paris is in Germany", "user", "d", Authority.of(speaker=1), I.Scope.of("conv"))
    assert I.mutant_promote_said_to_world_truth(said).rank("world_truth") == 1
    assert I.promote_authority(said, Authority.of(world_truth=1, speaker=1)).rank("world_truth") == 0  # said has no world_truth → meet is 0
