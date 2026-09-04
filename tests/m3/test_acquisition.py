"""M3 §5/§8: construction acquisition from aligned demonstrations via the version-space learner."""
from __future__ import annotations

from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.language import acquisition as AQ
from ocm.language import constructions as C
from ocm.language import interpret as I
from ocm.language import lexicon as L
from ocm.language import meaning as M
from ocm.learning.learner import UpdateKind, UpdateStatus


def _lexicon():
    lx = L.Lexicon()
    ev = lambda n: WP.of({f"ev:{n}"})  # noqa: E731
    for n in ("robot", "door", "cat", "box", "key"):
        lx.add(L.Lexeme(n, L.Category.NOUN, (L.Sense(n, n, "entity", ev(n)),)))
    for v in ("open", "push", "see"):
        lx.add(L.Lexeme(v, L.Category.VERB, (L.Sense(v, v, "event", ev(v)),)))
    lx.add_rule(L.MorphRule("past-ed", L.RuleKind.PRODUCTIVE, L.Category.VERB, (("tense", "past"),), lambda l: l + "ed", lambda s: s[:-2] if s.endswith("ed") else None, ev("rule-ed")))
    lx.add_rule(L.MorphRule("saw", L.RuleKind.EXCEPTION, L.Category.VERB, (("tense", "past"),), lambda l: "saw", lambda s: "see" if s == "saw" else None, ev("saw"), lemmas=frozenset({"see"})))
    return lx


def _family():
    def template(b):
        s, v, o = b["S"], b["V"], b["O"]
        return M.MeaningGraph((M.MNode("x1", "entity", s.lemma), M.MNode("e", "event", v.lemma), M.MNode("x2", "entity", o.lemma)), (M.MEdge("ROLE:agent", ("e",), ("x1",)), M.MEdge("ROLE:patient", ("e",), ("x2",)), M.MEdge("TENSE", ("e",), ("e",), "past")), root="e")

    hyps = AQ.order_hypotheses([("S", C.Slot("S", L.Category.NOUN)), ("V", C.Slot("V", L.Category.VERB, requires=("tense",))), ("O", C.Slot("O", L.Category.NOUN))])
    assert len(hyps) == 6
    return AQ.ConstructionFamily("transitive-order", hyps, template, query_family=("cat pushed box", "box opened key", "key saw cat"))


def _meaning(agent, verb, patient):
    return M.MeaningGraph((M.MNode("a", "entity", agent), M.MNode("e", "event", verb), M.MNode("p", "entity", patient)), (M.MEdge("ROLE:agent", ("e",), ("a",)), M.MEdge("ROLE:patient", ("e",), ("p",)), M.MEdge("TENSE", ("e",), ("e",), "past")), root="e")


def test_before_lesson_gap_then_ambiguity_then_learned_construction_generalises():
    lx, fam = _lexicon(), _family()
    p0 = AQ.acquire(fam, lx, [])
    assert p0.status in (UpdateStatus.GAP_AMBIGUOUS, UpdateStatus.GAP_INSUFFICIENT) and p0.kind is UpdateKind.QUARANTINE
    # one demonstration with a symmetric predicate still leaves SVO vs OVS undecided
    p1 = AQ.acquire(fam, lx, [AQ.Demonstration("robot opened door", _meaning("robot", "open", "door"), "ev:d1")])
    assert p1.status is UpdateStatus.PASS or p1.status is UpdateStatus.GAP_AMBIGUOUS
    demos = [AQ.Demonstration("robot opened door", _meaning("robot", "open", "door"), "ev:d1"), AQ.Demonstration("cat saw key", _meaning("cat", "see", "key"), "ev:d2")]
    p2 = AQ.acquire(fam, lx, demos)
    assert p2.status is UpdateStatus.PASS and p2.payload["hypothesis"] == "SVO"
    assert p2.warrant.evidence <= {"ev:d1", "ev:d2"} and p2.warrant.evidence
    c = AQ.construction_from_proposal(fam, p2)
    r = I.interpret("box pushed cat", lx, [c])           # unseen lexical combination
    assert r.verdict is I.Verdict.INTERPRETED and M.isomorphic(r.meaning, _meaning("box", "push", "cat"))
    # revoke the pinning demonstration → construction dead → generation gap; reinstate → recovers exactly
    revoked = tuple(p2.warrant.evidence)
    assert c.liveness(revoked) is Liveness.DEAD and I.interpret("box pushed cat", lx, [c], revoked=revoked).verdict is I.Verdict.UNKNOWN_CONSTRUCTION
    assert I.interpret("box pushed cat", lx, [c]).verdict is I.Verdict.INTERPRETED


def test_contradictory_demonstrations_are_preserved_not_averaged():
    lx, fam = _lexicon(), _family()
    demos = [AQ.Demonstration("robot opened door", _meaning("robot", "open", "door"), "ev:d1"), AQ.Demonstration("robot opened door", _meaning("door", "open", "robot"), "ev:d2")]
    p = AQ.acquire(fam, lx, demos)
    assert p.status is UpdateStatus.CONTRADICTION and p.kind is UpdateKind.QUARANTINE


def test_instruction_names_the_hypothesis_but_demonstrations_check_it():
    lx, fam = _lexicon(), _family()
    p = AQ.acquire(fam, lx, [AQ.Demonstration("cat saw key", _meaning("cat", "see", "key"), "ev:d2")], instruction=("OVS", "ev:book"))
    assert p.payload.get("hypothesis") != "OVS"            # refuted by the demonstration
    p2 = AQ.acquire(fam, lx, [AQ.Demonstration("cat saw key", _meaning("cat", "see", "key"), "ev:d2")], instruction=("SVO", "ev:book"))
    assert p2.status is UpdateStatus.PASS and p2.payload["hypothesis"] == "SVO" and "ev:book" in p2.warrant.evidence


def test_wrong_language_transfer_is_refused_by_scope():
    lx, fam = _lexicon(), _family()
    p = AQ.acquire(fam, lx, [AQ.Demonstration("robot opened door", _meaning("robot", "open", "door"), "ev:d1"), AQ.Demonstration("cat saw key", _meaning("cat", "see", "key"), "ev:d2")])
    c = AQ.construction_from_proposal(fam, p)
    bad = AQ.mutant_transfer_to_other_language(c, "sov-lang")
    assert not AQ.scope_check(c, "sov-lang") and AQ.scope_check(bad, "sov-lang")   # the relabel is what the scope rule forbids
