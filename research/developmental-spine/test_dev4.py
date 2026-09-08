"""Integrity tests for DEV-4, which withdraws DEV-3's declared gift.

The result here turns on CORRECTNESS rather than cost, so the tests are aimed at
the correctness machinery: that an arm can actually be wrong, that the arm which
cannot be wrong really cannot, that a wrong arm's work figure is withheld rather
than quoted, and that the levels are disjoint so an arm starting small is not
handed an easy truth by accident.
"""

from __future__ import annotations

import inspect
import json
import pathlib
import random
import sys

import pytest

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import dev4
import dev4_arms as A
import run_dev4 as R
from retain import demand_stream

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "DEV4_LANGUAGE_EXPANSION_V1.json"


# --- the ladder ------------------------------------------------------------

def test_the_levels_are_nested_and_grow():
    sizes = [len(dev4.language(l, 16)) for l in dev4.LEVELS]
    assert sizes == sorted(sizes) and len(set(sizes)) == len(sizes)
    for lo, hi in zip(dev4.LEVELS, dev4.LEVELS[1:]):
        assert set(dev4.language(lo, 16)) < set(dev4.language(hi, 16))


def test_a_worlds_truth_is_never_expressible_at_a_lower_level():
    """Otherwise an arm starting small looks sound by luck."""
    for level in (2, 3):
        rng = random.Random(level)
        for _ in range(40):
            pred = dev4.draw_truth(level, 16, rng)
            assert pred not in dev4.language(level - 1, 16), (level, pred)
            assert pred in dev4.language(level, 16)


def test_the_disjointness_is_stated_in_the_plan():
    assert "NOT in level k-1" in dev4.DEV4_PLAN["levels_are_disjoint"]


# --- an arm can be wrong, and one cannot ------------------------------------

def test_the_serve_path_can_return_an_incorrect_answer():
    src = inspect.getsource(A._run)
    assert "return world.generated_by_rule(answer)" in src, (
        "applying under a guard must be able to be wrong, or nothing is being tested")
    assert "phase.correct += 1 if ok else 0" in src


def test_the_full_language_parent_cannot_produce_a_false_guard():
    """Its language contains every truth, so a singleton provably contains it."""
    for level in (1, 2, 3):
        world, truth = dev4.build_level_world(16, 16, level, random.Random(level + 5))
        d0 = demand_stream(world.base, 300, 1.0, random.Random(level + 6))
        d1 = dev4.d1_stream(world, 400, 1.0, random.Random(level + 7))
        _, p1, carried = A.run_arm("FIXED_FULL_PARENT", world, d0, d1, 1024, level)
        assert p1.correctness() == 1.0, level
        for rule, guard in carried.guards.items():
            for index in range(world.base.extension):
                answer = world.base.members[rule][index]
                assert guard.excludes(index) == (not world.generated_by_rule(answer))


def test_a_small_language_really_does_go_wrong_somewhere():
    """If it never did, the whole experiment would be measuring nothing."""
    worst = 1.0
    for seed in range(8):
        world, _ = dev4.build_level_world(16, 16, 3, random.Random(100 + seed))
        d0 = demand_stream(world.base, 60, 1.0, random.Random(200 + seed))
        d1 = dev4.d1_stream(world, 600, 1.0, random.Random(300 + seed))
        _, p1, _ = A.run_arm("FIXED_SMALL_PARENT", world, d0, d1, 1024, 3)
        worst = min(worst, p1.correctness())
    assert worst < 1.0


def test_no_arm_is_told_the_world_level_except_the_declared_ceiling():
    for arm in ("expanding_arm", "fixed_full_parent", "fixed_small_parent"):
        src = inspect.getsource(getattr(A, arm))
        assert "oracle_level" not in src, arm
    assert "oracle_level=world_level" in inspect.getsource(A.oracle_level_parent)
    assert A.ARM_ROLES["ORACLE_LEVEL_PARENT"] == "CEILING"


# --- the gate withholds a number rather than quoting it --------------------

def test_an_unsound_arm_has_no_admissible_work_figure():
    doc = json.loads(RECEIPT.read_text())
    found = False
    for c in doc["primary_grid"]:
        for arm, v in c["arms"].items():
            if not v["sound_in_every_replicate"]:
                found = True
                assert v["d1_work"] is None, (arm, c["level"])
                assert v["d1_work_if_it_were_admissible"] is not None
    assert found, "no unsound cell in the receipt; this test would be vacuous"


def test_the_receipt_says_the_withheld_number_is_the_speed_of_a_wrong_answer():
    """Whenever ANY cell is unsound -- not only when a whole level is."""
    doc = json.loads(RECEIPT.read_text())
    unsound = [c for c in doc["primary_grid"]
               if not c["arms"]["EXPANDING_ARM"]["sound_in_every_replicate"]]
    assert unsound, "no unsound cell; this test would be vacuous"
    assert "speed of a wrong answer" in doc["terminal_reason"]
    assert f"In {len(unsound)} of {len(doc['primary_grid'])} cells" in doc["terminal_reason"]


# --- the registered predictions ---------------------------------------------

def test_e5_is_reported_false_and_in_the_machines_favour():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["E5_advantage_only_where_the_mechanism_is_unnecessary"] is False
    v = doc["predictions"]["E5_verdict"]
    assert v.startswith("FALSE, and in the machine's favour")
    assert "least flattering to self-expansion" in v


def test_the_terminal_is_computed_from_the_grid_not_asserted():
    """Every branch of the terminal is reachable and none is hard-coded prose."""
    src = inspect.getsource(R._terminal)
    for token in ("always_unsound", "sometimes", "always_sound", "len(unsound)"):
        assert token in src, token
    doc = json.loads(RECEIPT.read_text())
    grid = doc["primary_grid"]
    levels = sorted({c["level"] for c in grid})
    sound_levels = sorted({
        l for l in levels
        if any(c["arms"]["EXPANDING_ARM"]["sound_in_every_replicate"]
               for c in grid if c["level"] == l)
        and all(c["arms"]["EXPANDING_ARM"]["sound_in_every_replicate"]
                for c in grid if c["level"] == l)})
    assert f"level(s) {sound_levels}" in doc["terminal_reason"]


def test_the_earned_soundness_threshold_matches_the_grid():
    doc = json.loads(RECEIPT.read_text())
    grid = doc["primary_grid"]
    for level in sorted({c["level"] for c in grid}):
        rows = [c for c in grid if c["level"] == level]
        sound = [c["d0_length"] for c in rows
                 if c["arms"]["EXPANDING_ARM"]["sound_in_every_replicate"]]
        unsound = [c["d0_length"] for c in rows
                   if not c["arms"]["EXPANDING_ARM"]["sound_in_every_replicate"]]
        if sound and unsound:
            claim = (f"level {level} becomes sound only at D0 length {min(sound)} "
                     "and above")
            assert claim in doc["terminal_reason"], claim


def test_expansion_is_shown_to_be_inert_against_the_failure_that_matters():
    doc = json.loads(RECEIPT.read_text())
    rows = doc["correctness_by_level_and_evidence"]
    assert all(r["expanding"] == r["fixed_small"] for r in rows) or \
        "expansion is doing something on its own" in doc["terminal_reason"]
    if all(r["expanding"] == r["fixed_small"] for r in rows):
        assert "never fires against the failure that matters" in doc["terminal_reason"]
        assert "a wrong SINGLETON, which never empties" in doc["terminal_reason"]


def test_the_evidence_note_matches_what_the_grid_shows():
    doc = json.loads(RECEIPT.read_text())
    note = doc["does_more_evidence_rescue_it"]
    rows = doc["correctness_by_level_and_evidence"]
    longest = max(r["d0_length"] for r in rows)
    grid = doc["primary_grid"]
    still_wrong = [{"level": c["level"], "skew": c["skew"]} for c in grid
                   if c["d0_length"] == longest
                   and not c["arms"]["EXPANDING_ARM"]["sound_in_every_replicate"]]
    if still_wrong:
        assert "It is not enough everywhere" in note
        for r in still_wrong:
            assert f"level {r['level']} at skew {r['skew']}" in note, r
        assert "does rescue it" not in note
    else:
        assert "every cell is sound" in note and "does rescue it" in note, (
            "if the longest evidence reaches correctness 1.0 everywhere, the receipt must "
            "not still claim that more evidence does not rescue it")
        assert "not a general soundness argument" in note


# --- what the gift was worth ------------------------------------------------

def test_dev3s_gift_is_characterised_as_a_precondition():
    doc = json.loads(RECEIPT.read_text())
    note = doc["what_the_gift_was_worth"]
    assert "PRECONDITION" in note
    assert "not a convenience" in note
    assert "DEV-3's numbers stand" in note


def test_this_receipt_withdraws_nothing():
    doc = json.loads(RECEIPT.read_text())
    assert "withdraws no negative and no positive" in doc["authority"]


def test_the_pilot_and_its_misleading_single_seed_are_disclosed():
    d = dev4.DEV4_PLAN["pilot_disclosure"]
    assert "looked like a refutation" in d
    assert "extensionally equal" in d
    assert "the pilot's single seed was the misleading observation" in d


def test_the_receipt_carries_the_plan_and_no_wall_clock():
    doc = json.loads(RECEIPT.read_text())
    assert doc["commitment"]["commitment"] == dev4.COMMITMENT.commitment
    assert doc["plan"] == json.loads(json.dumps(dev4.DEV4_PLAN))
    text = RECEIPT.read_text().lower()
    for banned in ("elapsed", "timestamp", "duration_ms", "wall"):
        assert banned not in text, banned


def test_the_receipt_admits_it_cannot_invent_a_language():
    doc = json.loads(RECEIPT.read_text())
    assert "inventing the ladder" in doc["what_this_does_not_establish"]
    assert "NONE CLAIMED" in doc["novelty"]
