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


def test_gap_readings_interpret_with_declared_gaps_and_never_live():
    from ocm.kso.warrant import Liveness
    lx = _lexicon()
    cons = list(C.seed_constructions())
    r = CH.parse(I.tokenize("the zorb lifted the cup"), lx, cons, gaps=True)
    assert r["verdict"] == "INTERPRETED_WITH_GAPS" and r["gaps"] == ["zorb"] and r["count"] == 1
    m = r["meanings"][0]
    assert m["warrant"].liveness(()) is Liveness.UNKNOWN                            # a gap never yields a LIVE meaning
    gap_nodes = [n for n in m["meaning"].nodes if ("gap", "yes") in n.features]
    assert len(gap_nodes) == 1 and gap_nodes[0].node_type == "entity"
    assert CH.parse(I.tokenize("the zorb lifted the cup"), lx, cons)["verdict"] == "UNKNOWN_LEXEME"   # gaps are opt-in


def test_evidence_ranking_reports_the_best_supported_reading_without_licensing_it():
    """N1 phase E: two clause constructions with different demonstration counts yield the same meaning →
    AMBIGUOUS (count 2) stays AMBIGUOUS; the ranking puts the better-evidenced construction first and
    says so as a report ('not a unique parse'); constructions without counts are unranked."""
    import dataclasses
    lx = _lexicon()
    cons = list(C.seed_constructions())
    clause = [c for c in cons if c.produces is None and any(s.phrase == "NP" for s in c.pattern)]
    base = clause[0]
    weak = dataclasses.replace(base, construction_id=base.construction_id + ":weak", lineage=("count:2",))
    strong = dataclasses.replace(base, construction_id=base.construction_id + ":strong", lineage=("count:9",))
    others = [c for c in cons if c is not base]
    utt = "the girl lifted the cup"
    r0 = CH.parse(I.tokenize(utt), lx, others + [base])
    assert r0["verdict"] == "INTERPRETED" and r0["ranking"]["scored"] is False       # no counts → unranked, unchanged verdict
    r = CH.parse(I.tokenize(utt), lx, others + [weak, strong])
    assert r["verdict"] == "AMBIGUOUS" and r["count"] == 2                            # ranking never turns AMBIGUOUS into INTERPRETED
    assert r["ranking"]["scored"] and r["ranking"]["top_score"] == 9 and r["ranking"]["top_items"] == 1 and r["ranking"]["top_unique_derivation"]
    assert r["meanings"][0]["construction_id"].endswith(":strong") and r["meanings"][0]["evidence_score"] == 9
    assert r["meanings"][1]["evidence_score"] == 2
    assert "not a unique parse" in r["ranking"]["licence"]
    # a derivation is scored by its weakest construction: the strong clause over a weak NP scores 2
    np_cons = [c for c in others if c.produces == "NP"]
    weak_nps = [dataclasses.replace(c, lineage=("count:2",)) for c in np_cons]
    rest = [c for c in others if c.produces != "NP"]
    r2 = CH.parse(I.tokenize(utt), lx, rest + weak_nps + [strong])
    assert r2["verdict"] == "INTERPRETED" and r2["meanings"][0]["evidence_score"] == 2


def test_exact_derivation_counts_follow_the_catalan_numbers():
    """Batch 11 K1 (ix): with NP → N and NP → NP NP the string of k+1 nouns has Cat(k) derivations
    (1, 2, 5, 14, 42); the packed forest must return the exact count (the pre-phase-F chart undercounted
    once a packed node's count grew after its first use)."""
    from ocm.kso.warrant import WarrantProfile as WP
    from ocm.language import constructions as C
    from ocm.language import lexicon as L
    from ocm.language.meaning import MeaningGraph, MNode, MEdge
    lx = L.Lexicon()
    for w in ("a", "b", "c", "d", "e", "f"):
        lx.add(L.Lexeme(w, L.Category.NOUN, (L.Sense(f"{w}:1", w, "entity", WP.of({"e"})),)))
    def leaf(b):
        r = b["h"]; return MeaningGraph((MNode("x", "entity", r.lemma, ()),), (), root="x")
    def compound(b):
        l, r = b["l"].meaning, b["r"].meaning
        lm = l.relabel({n.node_id: "l." + n.node_id for n in l.nodes}); rm = r.relabel({n.node_id: "r." + n.node_id for n in r.nodes})
        return MeaningGraph((MNode("x", "entity", None, ()), *lm.nodes, *rm.nodes), (*lm.edges, *rm.edges, MEdge("MODIFIES", ("x",), ("l." + l.root,)), MEdge("MODIFIES", ("x",), ("r." + r.root,))), root="x")
    def clause(b):
        return b["np"].meaning
    cons = [C.Construction("t:leaf", "leaf", (C.Slot("h", L.Category.NOUN),), leaf, WP.of({"e"}), produces="NP", head_slot="h"),
            C.Construction("t:compound", "compound", (C.Slot("l", L.Category.NOUN, phrase="NP"), C.Slot("r", L.Category.NOUN, phrase="NP")), compound, WP.of({"e"}), produces="NP", head_slot="l"),
            C.Construction("t:clause", "clause", (C.Slot("np", L.Category.NOUN, phrase="NP"),), clause, WP.of({"e"}))]
    expected = {1: 1, 2: 1, 3: 2, 4: 5, 5: 14, 6: 42}
    for k, cat in expected.items():
        r = CH.parse(list("abcdef")[:k], lx, cons)
        assert r["count"] == cat, (k, r["count"])
        assert r["verdict"] == ("INTERPRETED" if cat == 1 else "AMBIGUOUS")


def test_admit_gate_refutes_completions_instead_of_ranking_them():
    """N1 phase G: an evidence gate refuses a completion; refused derivations are not counted, so an
    AMBIGUOUS sentence whose alternatives lack evidence becomes INTERPRETED — by refutation, not by score."""
    import dataclasses
    lx = _lexicon()
    cons = list(C.seed_constructions())
    clause = [c for c in cons if c.produces is None and any(s.phrase == "NP" for s in c.pattern)]
    base = clause[0]
    alt = dataclasses.replace(base, construction_id=base.construction_id + ":unattested")
    others = [c for c in cons if c is not base]
    utt = "the girl lifted the cup"
    r = CH.parse(I.tokenize(utt), lx, others + [base, alt])
    assert r["verdict"] == "AMBIGUOUS" and r["count"] == 2
    gate = lambda c, b: not c.construction_id.endswith(":unattested")   # noqa: E731
    r2 = CH.parse(I.tokenize(utt), lx, others + [base, alt], admit=gate)
    assert r2["verdict"] == "INTERPRETED" and r2["count"] == 1 and r2["meanings"][0]["construction_id"] == base.construction_id
    assert CH.parse(I.tokenize(utt), lx, others + [base, alt], admit=lambda c, b: False)["verdict"] == "UNKNOWN_CONSTRUCTION"
