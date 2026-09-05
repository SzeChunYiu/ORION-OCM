"""M3 §3–§4: lexemes with sense ambiguity sets, productive morphology with warranted exceptions."""
from __future__ import annotations

from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.language import lexicon as L


def _lexicon():
    lx = L.Lexicon()
    lx.add(L.Lexeme("bank", L.Category.NOUN, (L.Sense("bank:fin", "financial_institution", "entity", WP.of({"ev:bank-fin"})), L.Sense("bank:river", "river_bank", "entity", WP.of({"ev:bank-river"})))))
    lx.add(L.Lexeme("open", L.Category.VERB, (L.Sense("open:ev", "open", "event", WP.of({"ev:open"})),)))
    lx.add(L.Lexeme("go", L.Category.VERB, (L.Sense("go:ev", "go", "event", WP.of({"ev:go"})),)))
    lx.add_rule(L.MorphRule("past-ed", L.RuleKind.PRODUCTIVE, L.Category.VERB, (("tense", "past"),), lambda l: l + "ed", lambda s: s[:-2] if s.endswith("ed") else None, WP.of({"ev:rule-ed"})))
    lx.add_rule(L.MorphRule("past-go", L.RuleKind.EXCEPTION, L.Category.VERB, (("tense", "past"),), lambda l: "went", lambda s: "go" if s == "went" else None, WP.of({"ev:went"}), lemmas=frozenset({"go"})))
    lx.add_rule(L.MorphRule("past-go-regularised", L.RuleKind.PRODUCTIVE, L.Category.VERB, (("tense", "past"),), lambda l: l + "ed", lambda s: "go" if s == "goed" else None, WP.of({"ev:rule-ed"})))
    return lx


def test_polysemy_is_an_ambiguity_set_and_collapse_is_evidence_driven():
    lx = _lexicon()
    a = lx.analyse("bank")
    assert a.status is L.AnalysisStatus.AMBIGUOUS and {r.sense.sense_id for r in a.readings} == {"bank:fin", "bank:river"}
    b = lx.analyse("bank", revoked={"ev:bank-river"})
    assert b.status is L.AnalysisStatus.READINGS and b.readings[0].sense.sense_id == "bank:fin"
    merged = L.mutant_merge_senses(lx.lexemes["bank|N"])
    assert merged.liveness({"ev:bank-river"}) is Liveness.LIVE and merged.liveness({"ev:bank-fin", "ev:bank-river"}) is Liveness.DEAD


def test_unseen_inflected_form_is_recognised_through_morphology_with_a_composed_warrant():
    lx = _lexicon()
    a = lx.analyse("opened")
    assert a.status is L.AnalysisStatus.READINGS
    r = a.readings[0]
    assert r.lemma == "open" and dict(r.features)["tense"] == "past" and r.via == ("past-ed",)
    assert r.warrant.evidence == {"ev:open", "ev:rule-ed"}
    assert lx.analyse("opened", revoked={"ev:rule-ed"}).status is L.AnalysisStatus.NO_LIVE_READING


def test_irregular_exception_overrides_the_productive_rule_and_revocation_is_local():
    lx = _lexicon()
    went = lx.analyse("went")
    assert went.status is L.AnalysisStatus.READINGS and went.readings[0].via == ("past-go",)
    goed = lx.analyse("goed")
    assert goed.status is L.AnalysisStatus.NO_LIVE_READING or goed.readings == ()  # blocked while the exception is live
    # revoke the exception's evidence: the regularised form becomes available, 'opened' untouched
    goed2 = lx.analyse("goed", revoked={"ev:went"})
    assert goed2.status is L.AnalysisStatus.READINGS and "past-go-regularised" in goed2.readings[0].via
    assert lx.analyse("opened", revoked={"ev:went"}).status is L.AnalysisStatus.READINGS


def test_unknown_word_is_unknown_not_hallucinated():
    lx = _lexicon()
    assert lx.analyse("bnak").status is L.AnalysisStatus.UNKNOWN_LEXEME
    m = L.mutant_nearest_spelling(lx, "bnak")
    assert m is not None and m.lemma == "bank" and m.via == ("SPELLING",)   # the hallucination the rule forbids
