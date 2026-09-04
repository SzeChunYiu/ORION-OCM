from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "research" / "orion-machine" / "reference"


def load(name):
    p = REF / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, p)
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def m3():
    return load("kso_m3_learning_v1")


@pytest.fixture(scope="module")
def m4():
    return load("kso_m4_jump_v1")


@pytest.fixture(scope="module")
def m5():
    return load("kso_m5_chat_v1")


def test_m3_all_warranting_channels_learn_and_reuse(m3):
    r = m3.run_m3()
    assert r["terminal"] == "M3_EXACT_GAP_LEARNING_GREEN"
    for c in ("INSTRUCTION", "DEMONSTRATION", "INTERACTION", "EXPERIMENTATION"):
        assert r["channels"][c]["warranted"] is True
        assert r["channels"][c]["heldout_composition_exact"] == 12
        assert r["channels"][c]["heldout_composition_total"] == 12


def test_m3_feedback_cannot_warrant(m3):
    r = m3.run_m3()
    f = r["channels"]["FEEDBACK"]
    assert f["warranted"] is False and f["heldout_composition_exact"] == 0
    assert r["m0_integration"]["FEEDBACK"]["warranted"] is False
    assert r["m0_integration"]["FEEDBACK"]["profile_live"] is False


def test_m3_incomplete_demonstration_remains_ambiguous(m3):
    lesson = m3.Lesson(
        "AND",
        m3.Channel.DEMONSTRATION,
        1,
        examples=tuple(m3.Example(x, m3.table_apply(m3.TARGET_AND, x)) for x in m3.DOMAIN[:3]),
    )
    r = m3.learn_demonstration(lesson)
    assert r.learned is None and r.final_hypotheses == 2 and r.status == "GAP_AMBIGUOUS"


def test_m3_interaction_is_query_only_and_exact(m3):
    t = m3.BlindTeacher(lambda x: m3.table_apply(m3.TARGET_AND, x))
    r = m3.learn_interaction("AND", 12, t)
    assert r.learned and r.learned.table == m3.TARGET_AND
    assert r.observations == len(t.calls) == 4
    assert set(t.calls) == set(m3.DOMAIN)


def test_m3_revocation_and_reinstatement(m3):
    r = m3.learn_instruction(m3.Lesson("AND", m3.Channel.INSTRUCTION, 42, declared_table=m3.TARGET_AND))
    assert r.learned
    assert m3.heldout_composition_score(r.learned, m3.TARGET_AND) == (12, 12)
    assert m3.heldout_composition_score(r.learned, m3.TARGET_AND, {42}) == (0, 12)
    assert m3.heldout_composition_score(r.learned, m3.TARGET_AND) == (12, 12)


def test_m4_exact_expressive_ceiling_and_minimum_jump(m4):
    r = m4.run_m4()
    assert r["terminal"] == "M4_FINITE_GOVERNED_JUMP_GREEN"
    assert r["ceiling"]["exact_matches"] == 0
    assert r["proposals"]["minimum_sufficient"] == "kso-j3-add-conjunction-feature"
    assert r["j3_exact"]["target_exact"] == 4
    assert r["j3_exact"]["old_functions_preserved"] == 8


def test_m4_bad_representation_and_weak_trigger_rejected(m4):
    assert m4.check_bad_jump_rejected()
    j3, _ = m4.proposals()
    weak = m4.jump.JumpTrigger(
        "weak",
        m4.jump.TriggerKind.POOR_SCORE,
        m4.jump.JumpLevel.LOCAL_REPAIR_COMPOSITION,
        ("score",),
        ("retry",),
    )
    assert not weak.is_admissible
    assert (
        m4.jump.assess_jump(j3, lower_level_sufficient=True, donor_product_ties=False)
        is m4.jump.JumpAssessment.NO_JUMP_NEEDED_LOWER_LEVEL_SUFFICIENT
    )


def test_m5_translator_invariance_and_chat_lifecycle(m5):
    r = m5.run_m5()
    assert r["terminal"] == "M5_CONTROLLED_CODEC_CHAT_GREEN"
    assert all(r["translator_invariance"].values())
    assert r["chat"]["prelesson_gap"] == "GAP_UNKNOWN_PROCEDURE"
    assert r["chat"]["learned"] == "LEARNED"
    assert r["chat"]["answer_after_lesson"] == 0
    assert r["chat"]["answer_after_revocation"] == "GAP_REVOKED_PROCEDURE"
    assert r["chat"]["answer_after_reinstatement"] == 0


def test_m5_codec_cannot_supply_answer(m5):
    with pytest.raises(m5.CodecError, match="CODEC_ATTEMPTED_TO_SUPPLY_ANSWER"):
        m5.JsonCodec().parse('{"kind":"solve","name":"AND","combinator":"NOT","input":[1,1],"answer":0}')


def test_m5_feedback_only_does_not_make_chat_solver(m5):
    machine = m5.ChatMachine()
    machine.execute(m5.TextCodec().parse("feedback AND success"))
    r = machine.execute(m5.TextCodec().parse("solve NOT AND on 11"))
    assert r["status"] == "GAP_UNKNOWN_PROCEDURE"


def test_exit_contracts(m3, m4, m5):
    assert m3.main([]) == 0
    assert m4.main([]) == 0
    assert m5.main([]) == 0


def test_runnable_demo_transcript():
    demo = load("kso_demo_v1")
    rows = demo.run_script()
    assert [r["receipt"]["status"] for r in rows] == [
        "GAP_UNKNOWN_PROCEDURE",
        "LEARNED",
        "PASS",
        "REVOKED",
        "GAP_REVOKED_PROCEDURE",
        "REINSTATED",
        "PASS",
    ]
    assert rows[2]["receipt"]["result"] == 0 and rows[-1]["receipt"]["result"] == 0
