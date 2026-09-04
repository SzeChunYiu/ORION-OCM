from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_language_corpus_v0.py"


def load():
    name = "kso_language_corpus_v0"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_raw_corpus_discovers_form_but_not_semantic_roles():
    mod = load()
    r = mod.run_corpus_l1c_preflight()
    assert r["terminal"] == "LANGUAGE_CORPUS_L1C_FORM_PREFLIGHT_GREEN"
    assert r["raw"]["pattern"] == [
        "the",
        "<SLOT:1>",
        "<SLOT:2>",
        "<SLOT:3>",
        "the",
        "<SLOT:4>",
        "<SLOT:5>",
    ]
    assert r["raw"]["semantic_status"] == "UNGROUNDED_FORM_ONLY"
    assert r["raw"]["raw_pattern_has_semantic_roles"] is False
    assert r["aligned"]["status"] == "ALIGNED_ROLE_BINDING_IDENTIFIED"
    assert r["aligned"]["inconsistent_alignment_refused"] == "GAP_INCONSISTENT_ROLE_BINDING"


def test_anti_unification_requires_more_than_one_equal_length_sentence():
    mod = load()
    doc = mod.RawDocument("d", 1, "The cat sleeps.")
    sent = mod.tokenize_sentences(doc)
    try:
        mod.anti_unify(sent)
    except ValueError as exc:
        assert "at least two" in str(exc)
    else:
        raise AssertionError("one sentence was accepted as a recurring corpus pattern")

    d2 = mod.RawDocument("e", 2, "Dogs run quickly today.")
    rows = sent + mod.tokenize_sentences(d2)
    try:
        mod.anti_unify(rows)
    except ValueError as exc:
        assert "equal-length" in str(exc)
    else:
        raise AssertionError("unequal sentences were forced into one V0 pattern")


def test_raw_surface_pattern_cannot_supply_missing_semantics():
    mod = load()
    docs = (
        mod.RawDocument("a", 1, "The RED ROBOT OPEN the BLUE DOOR."),
        mod.RawDocument("b", 2, "The OLD CHILD LIKE the NEW TOY."),
    )
    pattern = mod.mine_surface_patterns(docs)[0]
    assert pattern.semantic_status == "UNGROUNDED_FORM_ONLY"
    assert not hasattr(pattern, "semantic_roles")
    assert pattern.render(("quiet", "student", "read", "good", "book")) == "The quiet student read the good book."


def test_inconsistent_alignment_is_not_majority_voted_into_a_binding():
    mod = load()
    docs = (
        mod.RawDocument("a", 1, "The CURIOUS ROBOT OPEN the RED DOOR."),
        mod.RawDocument("b", 2, "The SMALL CHILD ADMIRE the BLUE PAINTING."),
    )
    pattern = mod.mine_surface_patterns(docs)[0]
    frame = mod.lang.SemanticFrame(
        "en",
        mod.lang.NPConcept("robot", "the", ("curious",), mod.lang.Number.SINGULAR),
        "open",
        mod.lang.NPConcept("door", "the", ("red",), mod.lang.Number.SINGULAR),
    )
    rec = mod.bind_roles_from_aligned_examples(
        pattern,
        (
            (frame, "the curious robot open the red door"),
            (frame, "the curious door open the red robot"),
        ),
        3,
    )
    assert rec.status == "GAP_INCONSISTENT_ROLE_BINDING"
    assert rec.role_by_position == ()


def test_main_returns_zero():
    mod = load()
    assert mod.main([]) == 0
