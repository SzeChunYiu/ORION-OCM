"""M5 §5: morphology induction strategies on protected novel stems and irregulars; exception
accumulation → split recommendation; the override hostile."""
from __future__ import annotations

from ocm.kso.warrant import Liveness
from ocm.language import lexicon as L
from ocm.language.lexicon import AnalysisStatus, Category
from ocm.learning.language import morphology as MO


PAIRS = [MO.Pair("open", "opened", "ev:p1"), MO.Pair("push", "pushed", "ev:p2"), MO.Pair("lift", "lifted", "ev:p3"), MO.Pair("kick", "kicked", "ev:p4"), MO.Pair("go", "went", "ev:p5"), MO.Pair("see", "saw", "ev:p6")]


def test_rule_alone_is_contradicted_hybrid_keeps_exceptions_and_generalises_to_novel_stems():
    rule = MO.induce(PAIRS, MO.Strategy.RULE)
    assert rule.rule.name == "-∅+ed" and len(rule.covered) == 4 and "CONTRADICTION" in rule.detail
    hyb = MO.induce(PAIRS, MO.Strategy.HYBRID)
    assert hyb.rule.name == "-∅+ed" and {p.lemma for p in hyb.exceptions} == {"go", "see"} and not hyb.split_recommended
    assert hyb.warrant.evidence == {"ev:p1", "ev:p2", "ev:p3", "ev:p4"}
    assert hyb.rule.apply("blick") == "blicked" and hyb.rule.analyse("blicked") == "blick"      # protected novel stem
    # analogy: nearest paradigm; 'flee' patterns after 'see' (…ee) → 'flaw'? no: after 'see' → 'flaw' is what analogy does
    assert MO.analogy_form(PAIRS, "blick") == "blicked" and MO.analogy_form(PAIRS, "flee") == "flaw"


def test_installed_rules_use_the_override_law_and_the_hostile_breaks_it():
    lx = L.Lexicon()
    for v in ("open", "go", "see", "blick"):
        lx.add(L.Lexeme(v, Category.VERB, (L.Sense(v, v, "event", L.WarrantProfile.of({f"ev:{v}"})),)))
    hyb = MO.induce(PAIRS, MO.Strategy.HYBRID)
    ids = MO.install(lx, hyb, Category.VERB, (("tense", "past"),), "past")
    assert len(ids) == 3
    assert lx.analyse("blicked").status is AnalysisStatus.READINGS
    assert lx.analyse("went").readings[0].via == ("past:exc:go",)
    assert lx.analyse("goed").status is AnalysisStatus.UNKNOWN_LEXEME               # blocked while the exception is live
    assert lx.analyse("goed", revoked={"ev:p5"}).status is AnalysisStatus.READINGS   # local reopening of exactly that form
    assert lx.analyse("saw", revoked={"ev:p5"}).readings[0].via == ("past:exc:see",)  # other exception untouched
    MO.mutant_rule_overrides_exception(lx, "past")
    assert lx.analyse("goed").status is AnalysisStatus.READINGS                      # the hostile: rule competes with the exception


def test_exception_accumulation_recommends_a_split():
    pairs = PAIRS + [MO.Pair("sing", "sang", "ev:p7"), MO.Pair("ring", "rang", "ev:p8"), MO.Pair("drink", "drank", "ev:p9")]
    hyb = MO.induce(pairs, MO.Strategy.HYBRID)
    assert len(hyb.exceptions) == 5 and hyb.split_recommended
    # the split: induce on the -ing→-ang paradigm alone yields its own productive rule (the registered
    # class is suffix rewriting; the ablaut 'drink→drank' is outside it and stays an exception — a
    # recorded class limit, not a silent fit)
    sub = MO.induce([p for p in pairs if p.form.endswith("ang")], MO.Strategy.HYBRID)
    assert sub.rule is not None and sub.exceptions == () and sub.rule.apply("spring") == "sprang"
    sub2 = MO.induce([p for p in pairs if p.form.endswith("ang") or p.form.endswith("ank")], MO.Strategy.HYBRID)
    assert {p.lemma for p in sub2.exceptions} == {"drink"}
