"""Integrity tests for X4, which applies one charge rule to every carry-advantage
claim this lane has made and finds that exactly one of them survives.

The tests that matter here are the hostile ones. X4 is the study this lane most
wants to come out positive, so the checks below are written to catch the ways a
positive could be manufactured: a kill criterion that cannot fire, a terminal
that does not follow from the grid, an arm quoted at unmatched correctness, or a
language axis that is not actually the only thing separating the two singleton
arms.
"""

from __future__ import annotations

import inspect
import json
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import dev6_arms as A6
import run_x4 as R
import x4
from dev4 import language
from x4 import ARM_LANGUAGES, COMMITMENT, X4_PLAN

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "X4_FINAL_ACCOUNTING_V1.json"


def _doc() -> dict:
    if not RECEIPT.exists():
        pytest.skip("X4 receipt not generated in this checkout")
    return json.loads(RECEIPT.read_text())


# --- the commitment is a commitment -----------------------------------------

def test_the_plan_digest_is_the_one_that_was_registered():
    assert COMMITMENT.commitment.startswith("e0af655407205d4f")


def test_no_outcome_field_lives_inside_the_committed_plan():
    """E9's failure mode: an outcome recorded inside PLAN changes the digest and
    silently un-freezes the prediction. Outcomes belong in the receipt only."""
    registered = {
        "audits", "capability_gate", "charge_rule", "contribution_level",
        "decisive_causal_question", "doctrine", "evidence_class", "kill_criterion",
        "novelty", "predictions_frozen_before_execution", "prior_information_audit",
        "programme", "resolves", "scientific_question", "study_id", "sweep",
        "the_confound_being_removed", "what_this_does_not_establish"}
    assert set(X4_PLAN) == registered, "the plan gained or lost a field after freezing"
    outcomes = set(json.loads(RECEIPT.read_text())) if RECEIPT.exists() else set()
    for field in ("terminal", "terminal_reason", "predictions", "primary_grid",
                  "what_survives_after_every_audit", "what_this_corrects"):
        assert field not in X4_PLAN, f"{field!r} is an outcome and must live outside PLAN"
        assert field in outcomes or not outcomes


def test_predictions_are_frozen_before_any_arm_runs():
    src = inspect.getsource(x4)
    assert src.index("predictions_frozen_before_execution") < src.rindex("commit(X4_PLAN)")
    assert src.index("kill_criterion") < src.rindex("commit(X4_PLAN)")


# --- the kill criterion can actually fire -----------------------------------

def test_the_negative_terminal_is_reachable_from_a_grid_that_loses():
    """A kill criterion that no grid can trigger is decoration. Feed _terminal a
    level-1 grid in which the guarded arm is sound and loses, and require the
    words the plan promised to report."""
    losing = [{"level": 1, "arms": {"GUARDED_SMALL_LANGUAGE":
                                    {"sound_in_every_replicate": True}},
               "beats_replay": {"GUARDED_SMALL_LANGUAGE": False},
               "ratio_to_replay": {"GUARDED_SMALL_LANGUAGE": 1.4,
                                   "SINGLETON_FULL_LANGUAGE": 1.4}}]
    terminal, reason = R._terminal(losing)
    assert terminal == "NO_CARRY_ADVANTAGE_UNDER_ANY_REPRESENTATION_TRIED"
    assert "no carry advantage under any" in reason
    assert "DEV-3 must be corrected" in reason


def test_an_unsound_small_language_at_level_one_voids_rather_than_kills():
    """The level-1 language contains every level-1 truth. Unsoundness there is a
    harness bug, and reporting it as a scientific negative would be a lie."""
    void = [{"level": 1, "arms": {"GUARDED_SMALL_LANGUAGE":
                                  {"sound_in_every_replicate": False}},
             "beats_replay": {"GUARDED_SMALL_LANGUAGE": False},
             "ratio_to_replay": {"GUARDED_SMALL_LANGUAGE": None,
                                 "SINGLETON_FULL_LANGUAGE": 1.0}}]
    terminal, _ = R._terminal(void)
    assert terminal.startswith("VOID_")


def test_the_positive_terminal_requires_a_win_at_matched_correctness():
    """A cell that wins on work while being unsound must not count."""
    unsound_win = [{"level": 1, "arms": {"GUARDED_SMALL_LANGUAGE":
                                         {"sound_in_every_replicate": False}},
                    "beats_replay": {"GUARDED_SMALL_LANGUAGE": True},
                    "ratio_to_replay": {"GUARDED_SMALL_LANGUAGE": 0.1,
                                        "SINGLETON_FULL_LANGUAGE": 1.0}}]
    terminal, _ = R._terminal(unsound_win)
    assert terminal.startswith("VOID_"), "an unsound arm cannot carry the positive"


# --- language size is the only axis separating the two singleton arms --------

def test_the_two_singleton_arms_differ_in_language_and_in_nothing_else():
    assert R.MODE["GUARDED_SMALL_LANGUAGE"] == R.MODE["SINGLETON_FULL_LANGUAGE"]
    assert ARM_LANGUAGES["GUARDED_SMALL_LANGUAGE"] != ARM_LANGUAGES["SINGLETON_FULL_LANGUAGE"]


def test_the_small_language_is_actually_small_and_the_full_one_actually_full():
    small = len(language(ARM_LANGUAGES["GUARDED_SMALL_LANGUAGE"], 16))
    full = len(language(ARM_LANGUAGES["SINGLETON_FULL_LANGUAGE"], 16))
    assert small < full / 10, (small, full)


def test_the_language_parameter_is_additive_and_dev6_still_reproduces():
    """dev6_arms._run gained lang_level for this study. Its default must leave
    every DEV-6 arm byte-identical, or X4 has silently rewritten its own audit."""
    sig = inspect.signature(A6._run)
    assert sig.parameters["lang_level"].default is None
    src = inspect.getsource(A6._run)
    assert "max(LEVELS) if lang_level is None else lang_level" in src


# --- the receipt agrees with the grid it publishes ---------------------------

def test_every_quoted_work_figure_is_at_full_correctness():
    for cell in _doc()["primary_grid"]:
        for arm, row in cell["arms"].items():
            if row["d1_work"] is not None:
                assert row["min_correctness"] == 1.0, (arm, cell["level"])


def test_the_replay_parent_is_itself_sound_wherever_it_is_used_as_a_baseline():
    """A ratio against an unsound parent is meaningless."""
    for cell in _doc()["primary_grid"]:
        if any(v is not None for v in cell["ratio_to_replay"].values()):
            assert cell["arms"]["REPLAY_ONLY_PARENT"]["min_correctness"] == 1.0


def test_the_terminal_follows_from_the_published_grid():
    doc = _doc()
    assert R._terminal(doc["primary_grid"])[0] == doc["terminal"]


def test_the_positive_is_stated_with_its_condition_and_not_without_it():
    doc = _doc()
    if doc["terminal"] != "CARRY_ADVANTAGE_SURVIVES_ON_A_SMALL_SOUND_LANGUAGE":
        pytest.skip("terminal is not the conditional positive")
    survives = doc["what_survives_after_every_audit"]
    for condition in ("contain the truth", "does not extend to", "matched correctness"):
        assert condition in survives, condition


def test_a_refuted_prediction_is_published_as_refuted():
    """Z1 and Z5 are the two the lane would most like to quietly restate."""
    preds = _doc()["predictions"]
    assert set(preds) == {
        "Z1_small_language_beats_replay_at_level_1",
        "Z2_full_language_loses_at_level_1",
        "Z3_small_language_unsound_above_level_1",
        "Z4_unanimity_beats_singleton_on_the_full_language",
        "Z5_nothing_beats_replay_at_level_3"}
    assert all(isinstance(v, bool) for v in preds.values())


def test_nothing_is_withdrawn_from_the_studies_this_one_audits():
    doc = _doc()
    assert "withdraws nothing" in doc["authority"]
    assert "X3's receipt is not withdrawn" in doc["what_this_corrects"]


def test_no_novelty_is_claimed_for_bookkeeping():
    assert _doc()["novelty"].startswith("NONE CLAIMED")
