from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_language_v0.py"


def load():
    name = "kso_language_v0"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_language_l0_end_to_end():
    lang = load()
    r = lang.run_language_l0()
    assert r["terminal"] == "LANGUAGE_KSO_L0_CONTROLLED_GREEN"
    assert r["learning"]["clause_order_initial_hypotheses"] == 6
    assert r["learning"]["clause_order_final_hypotheses"] == 1
    assert r["learning"]["clause_order"] == ["S", "V", "O"]
    assert r["learning"]["np_order"] == ["D", "A", "N"]
    assert r["generation"]["surface"] == "The curious robot opens the red door."
    assert r["generation"]["heldout_surface"] == "The curious robot admires the red painting."
    assert r["generation"]["sentence_sketch"] == ["S", "V", "O"]
    assert r["generation"]["regular_past"] == "walked"
    assert r["generation"]["irregular_past"] == "went"
    assert r["generation"]["instruction_demo_surface_equal"] is True


def test_language_refuses_to_guess_before_construction_learning():
    lang = load()
    m = lang.LanguageKSO()
    lang._teach_demo_lexicon(m)
    r = m.speak(lang._target_frame())
    assert r.status == "GAP_NO_CLAUSE_TRANSITIVE_CONSTRUCTION"
    assert r.surface is None and r.plan is None


def test_empty_demonstration_keeps_all_clause_orders_live():
    lang = load()
    r = lang.induce_clause_order("en", (), 99)
    assert r.status == "GAP_AMBIGUOUS"
    assert r.initial_hypotheses == r.final_hypotheses == 6
    assert r.order == ()


def test_sentence_plan_exists_before_surface_realization_and_contains_only_frame_bindings():
    lang = load()
    m = lang.LanguageKSO()
    lang._teach_demo_lexicon(m)
    m.teach_construction("en", "CLAUSE_TRANSITIVE", ("S", "V", "O"), 5000)
    m.teach_construction("en", "NP", ("D", "A", "N"), 5001)
    m.admit_morph_rule(
        "en",
        "PRES_3SG",
        lang.InductionReceipt("MORPH", 5002, 5, 1, 2, "LEARNED_WARRANTED", transform="ADD_S"),
    )
    m.admit_morph_rule(
        "en",
        "PAST",
        lang.InductionReceipt("MORPH", 5003, 5, 1, 2, "LEARNED_WARRANTED", transform="ADD_ED"),
    )
    plan = m.plan(lang._target_frame())
    assert plan.sketch == ("S", "V", "O")
    assert plan.slots() == {
        "S": ("the", "curious", "robot"),
        "V": ("opens",),
        "O": ("the", "red", "door"),
    }
    assert m.realize(plan) == "The curious robot opens the red door."


def test_revocation_and_language_scope_are_fail_closed():
    lang = load()
    m = lang.LanguageKSO()
    lang._teach_demo_lexicon(m)
    c = m.teach_construction("en", "CLAUSE_TRANSITIVE", ("S", "V", "O"), 6000)
    m.teach_construction("en", "NP", ("D", "A", "N"), 6001)
    m.admit_morph_rule(
        "en",
        "PRES_3SG",
        lang.InductionReceipt("MORPH", 6002, 5, 1, 2, "LEARNED_WARRANTED", transform="ADD_S"),
    )
    m.admit_morph_rule(
        "en",
        "PAST",
        lang.InductionReceipt("MORPH", 6003, 5, 1, 2, "LEARNED_WARRANTED", transform="ADD_ED"),
    )
    assert m.speak(lang._target_frame()).status == "PASS"
    m.revoke(c.evidence_id)
    assert m.speak(lang._target_frame()).status == "GAP_REVOKED_CLAUSE_TRANSITIVE_CONSTRUCTION"
    m.reinstate(c.evidence_id)
    assert m.speak(lang._target_frame()).status == "PASS"

    f = lang._target_frame()
    foreign = lang.SemanticFrame("toy-sov", f.agent, f.predicate_concept, f.patient, f.tense)
    assert m.speak(foreign).status == "GAP_NO_CLAUSE_TRANSITIVE_CONSTRUCTION"


def test_irregular_is_more_specific_than_productive_regular_rule():
    lang = load()
    m = lang.LanguageKSO()
    lang._teach_demo_lexicon(m)
    m.admit_morph_rule(
        "en",
        "PAST",
        lang.InductionReceipt("MORPH", 7000, 5, 1, 2, "LEARNED_WARRANTED", transform="ADD_ED"),
    )
    assert m.verb_form("en", "WALK", lang.Tense.PAST, lang.Number.SINGULAR)[0] == "walked"
    assert m.verb_form("en", "GO", lang.Tense.PAST, lang.Number.SINGULAR) == ("went", "IRREGULAR:PAST")


def test_main_returns_zero_for_controlled_l0():
    lang = load()
    assert lang.main([]) == 0
