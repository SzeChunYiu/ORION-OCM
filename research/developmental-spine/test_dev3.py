"""Integrity tests for DEV-3, the first result in this lane where carried
structure beats the parent that had been beating it.

That is exactly the situation in which a lane fools itself, so these tests are
aimed at the specific ways this could be false: the arm could be skipping checks
it has not earned (unsound guards), the two regimes could differ in something
other than exception structure, the budget window could have been searched rather
than derived, and the win could be a coverage effect that has nothing to do with
guards -- which is what the RANDOM control exists to detect and what the
out-of-window rows show really does happen below the window.
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

import dev1_arms as A
import dev3
import dev3_arms as G
import run_dev3 as R
from retain import FACT_BITS, RULE_BITS, demand_stream

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "DEV3_GUARDED_RULES_V1.json"


def worlds(seed=5, extension=16, rules=16):
    structured, truth = dev3.build_structured_world(rules, extension, random.Random(seed))
    randomw, _ = dev3.build_random_world(rules, extension, len(structured.exceptions),
                                         random.Random(seed + 1))
    return structured, randomw, truth


# --- soundness: the arm may never skip a check it has not earned ------------

def test_a_guard_is_used_only_when_the_version_space_is_a_singleton():
    src = inspect.getsource(G._observe)
    assert "if len(survivors) == 1:" in src
    assert "store.guards.pop(rule, None)" in src, (
        "a version space that grows back above one must retract the guard")


def test_every_usable_guard_is_the_true_guard():
    """A singleton version space provably contains the truth; check it does."""
    structured, _, truth = worlds()
    d0 = demand_stream(structured.base, 2000, 1.0, random.Random(9))
    d1 = dev3.d1_stream(structured, 500, 1.0, random.Random(10))
    _, _, carried = G.guarded_lineage(structured, d0, d1, 1024)
    assert carried.guards, "no guards learned; the test would be vacuous"
    for rule, guard in carried.guards.items():
        for index in range(structured.base.extension):
            answer = structured.base.members[rule][index]
            assert guard.excludes(index) == (not structured.generated_by_rule(answer)), (
                rule, index)


def test_the_version_space_empties_under_unstructured_exceptions():
    _, randomw, _ = worlds()
    d0 = demand_stream(randomw.base, 2000, 1.0, random.Random(9))
    d1 = dev3.d1_stream(randomw, 500, 1.0, random.Random(10))
    _, _, carried = G.guarded_lineage(randomw, d0, d1, 1024)
    assert len(carried.guards) <= 2, (
        "unstructured exceptions must leave almost no rule with a sound guard")


def test_correctness_is_one_in_both_regimes():
    for world in worlds()[:2]:
        d0 = demand_stream(world.base, 1200, 1.0, random.Random(9))
        d1 = dev3.d1_stream(world, 400, 1.0, random.Random(10))
        _, p1, _ = G.guarded_lineage(world, d0, d1, 1024)
        assert p1.correctness() == 1.0


# --- the regimes differ in structure and nothing else ----------------------

def test_the_two_regimes_have_the_same_number_of_exceptions():
    structured, randomw, _ = worlds()
    assert len(structured.exceptions) == len(randomw.exceptions)
    assert structured.exceptions != randomw.exceptions


def test_matching_the_count_matters_because_the_rates_differ_a_lot():
    """An unmatched control would have let a rate difference look like structure."""
    structured, _, _ = worlds()
    rate = len(structured.exceptions) / structured.base.answers
    assert rate > 0.25, (
        "the structured draw is exception-HEAVY; a 10 per cent independent rate would have "
        "been a much easier world and the comparison would have been confounded")


def _arm_code() -> str:
    """The arm's executable body, with the module's prose about itself removed.

    An earlier version of these two tests scanned the whole module and failed on
    the docstring that EXPLAINS the regimes -- which is documentation, not a
    channel. What must be leak-free is the code.
    """
    out = []
    for fn in (G._observe, G._index_of, G.run_guarded_d1, G.guarded_lineage):
        src = inspect.getsource(fn)
        parts = src.split('"""')
        out.append(parts[0] + "".join(parts[2::2]) if len(parts) > 2 else src)
    return "\n".join(out)


def test_no_arm_is_told_which_regime_it_is_in():
    code = _arm_code()
    for banned in ("STRUCTURED", "RANDOM_REGIME", "build_structured_world",
                   "build_random_world"):
        assert banned not in code, banned


def test_the_arm_never_reads_the_true_guard_or_the_exception_set():
    """It may ask about ONE answer at a time and pay for it; it may not read the
    world's exception set or any guard the world holds.

    ``known_exceptions`` is the arm's own record of exceptions it derived and is
    not a channel; the distinction is the point of this test rather than an
    exemption from it."""
    code = _arm_code()
    for banned in ("world.exceptions", ".semantics", "truth[", "_truth"):
        assert banned not in code, banned
    assert "world.generated_by_rule(" in code, (
        "the one legitimate channel is the per-answer observation the arm pays to derive")
    assert code.count("known_exceptions") >= 1


# --- the window is derived, not searched ------------------------------------

def test_the_window_bounds_are_computed_from_the_registered_constants():
    sw = dev3.DEV3_PLAN["sweep"]
    assert R.WINDOW_LO == sw["rule_count"] * (RULE_BITS + dev3.GUARD_BITS)
    assert R.WINDOW_HI == sw["rule_count"] * sw["extension"] * FACT_BITS
    src = inspect.getsource(R)
    assert "WINDOW_LO = SW[" in src and "WINDOW_HI = SW[" in src


def test_the_grid_spans_both_sides_of_the_window():
    budgets = dev3.DEV3_PLAN["sweep"]["budget_bits"]
    assert any(b < R.WINDOW_LO for b in budgets), "the degenerate low region must be shown"
    assert any(b >= R.WINDOW_HI for b in budgets), "the degenerate high region must be shown"
    assert any(R.WINDOW_LO <= b < R.WINDOW_HI for b in budgets)


def test_above_the_window_the_parent_holds_the_whole_answer_space():
    doc = json.loads(RECEIPT.read_text())
    high = [c for c in doc["primary_grid"] if c["budget_bits"] >= R.WINDOW_HI]
    assert high and all(not c["guarded_beats_replay"] for c in high), (
        "at or above the high bound memoization wins by arithmetic and must be seen to")


# --- the win is the guard, not coverage -------------------------------------

def test_the_control_is_clean_inside_the_window():
    doc = json.loads(RECEIPT.read_text())
    assert doc["control_exceptions"] == [], (
        "a random-regime win inside the window would mean the result is coverage, not guards")
    rand = [c for c in doc["primary_grid"]
            if c["regime"] == "RANDOM" and c["in_analytic_window"]]
    assert rand and all(not c["guarded_beats_replay"] for c in rand)


def test_the_coverage_effect_is_real_and_is_shown_outside_the_window():
    """Below the window the arm can beat replay in BOTH regimes; that is coverage,
    it has nothing to do with guards, and it is why the window is stated."""
    doc = json.loads(RECEIPT.read_text())
    below = [c for c in doc["primary_grid"] if c["budget_bits"] < R.WINDOW_LO]
    wins = [c for c in below if c["guarded_beats_replay"]]
    assert any(c["regime"] == "RANDOM" for c in wins), (
        "the receipt's claim that sub-window wins are coverage rests on them appearing in "
        "the regime where no guard is learnable")


def test_the_guarded_and_unguarded_arms_apply_rules_equally_often():
    """The guard changes the price of a rule application, not the number of them.
    If applications moved too, the arm would be a different policy and not a
    different representation."""
    doc = json.loads(RECEIPT.read_text())
    apps = doc["why_the_pilot_lost"]["applications_by_arm_in_window"]
    assert abs(apps["GUARDED_LINEAGE"] - apps["UNGUARDED_LINEAGE"]) < 5
    verif = doc["why_the_pilot_lost"]["verifications_by_arm_in_window"]
    assert verif["GUARDED_LINEAGE"] * 20 < verif["UNGUARDED_LINEAGE"]


def test_guarded_ties_unguarded_where_no_guard_is_learnable():
    doc = json.loads(RECEIPT.read_text())
    rand = [c for c in doc["primary_grid"]
            if c["regime"] == "RANDOM" and c["in_analytic_window"]]
    for c in rand:
        assert abs(c["ratio_to_unguarded"] - 1.0) < 0.05, c


# --- the arm defect the pilot exposed ---------------------------------------

def test_a_guard_is_never_evicted_to_make_room_for_a_fact():
    src = inspect.getsource(G.run_guarded_d1)
    assert "not in base.rules" in src, (
        "guards may be dropped only when their rule is")
    assert "discarded only when its rule is" in src


def test_a_rule_is_admitted_only_with_room_for_its_guard():
    src = inspect.getsource(G.run_guarded_d1)
    assert "RULE_BITS + (GUARD_BITS" in src


def test_the_pilot_defect_is_disclosed_with_its_number():
    d = dev3.DEV3_PLAN["pilot_disclosure"]
    assert "1958 of" in d
    assert "holding sixteen sound guards and using none" in d
    assert "DEGENERATE" in d


# --- terminals --------------------------------------------------------------

def _cells(rows, correctness=1.0):
    out = []
    for (regime, budget), ratio in rows.items():
        out.append({
            "regime": regime, "d1_length": 1000, "budget_bits": budget, "skew": 1.0,
            "in_analytic_window": R.in_window(budget),
            "ratio_to_replay": ratio, "ratio_to_unguarded": 0.5,
            "guarded_beats_replay": ratio < 1.0,
            "mean_exception_count": 80.0,
            "arms": {a: {"correctness": correctness, "d1_work": 1.0, "verifications": 1,
                         "applications": 1, "guards_carried": 1}
                     for a in ("GUARDED_LINEAGE", "UNGUARDED_LINEAGE",
                               "REPLAY_ONLY_PARENT")}})
    return out


def test_the_kill_criterion_is_reachable():
    t, reason = R._terminal(_cells({("STRUCTURED", 1024): 2.0, ("RANDOM", 1024): 2.0}))
    assert t == "NO_CARRY_ADVANTAGE_UNDER_ANY_REPRESENTATION_TRIED"
    assert "no carry advantage under any representation it has tried" in reason


def test_an_unsound_guard_blocks_every_claim():
    t, _ = R._terminal(_cells({("STRUCTURED", 1024): 0.5}, correctness=0.99))
    assert t == "INADMISSIBLE_CORRECTNESS_NOT_MATCHED"


def test_a_dirty_control_narrows_the_headline_in_the_receipt_text():
    t, reason = R._terminal(_cells({("STRUCTURED", 1024): 0.5, ("RANDOM", 1024): 0.5}))
    assert t == "GUARDED_CARRY_ADVANTAGE_INSIDE_THE_ANALYTIC_WINDOW"
    assert "THE CONTROL IS NOT CLEAN" in reason
    assert "wins for coverage rather than for guards" in reason


# --- the receipt ------------------------------------------------------------

def test_all_registered_predictions_are_reported():
    doc = json.loads(RECEIPT.read_text())
    for key in ("G0", "G1", "G2", "G3", "G4", "G5", "G6"):
        assert any(k.startswith(key) for k in doc["predictions"]), key


def test_the_advantage_is_larger_under_uniform_demand():
    doc = json.loads(RECEIPT.read_text())
    by_skew = doc["mean_ratio_to_replay_by_skew_in_window"]
    assert by_skew["0.0"] < by_skew["1.0"], (
        "uniform demand is the hardest setting for a cache; the result must not need a "
        "skewed stream")


def test_the_receipt_names_the_parent_that_had_beaten_us():
    doc = json.loads(RECEIPT.read_text())
    assert doc["arm_roles"]["REPLAY_ONLY_PARENT"] == "PARENT_THAT_BEAT_US_IN_DEV2"
    assert "DEV2_CONTINUAL_PARENTS_V1" in doc["authority"]


def test_the_receipt_carries_the_plan_and_no_wall_clock():
    doc = json.loads(RECEIPT.read_text())
    assert doc["commitment"]["commitment"] == dev3.COMMITMENT.commitment
    assert doc["plan"] == json.loads(json.dumps(dev3.DEV3_PLAN))
    text = RECEIPT.read_text().lower()
    for banned in ("elapsed", "timestamp", "duration_ms", "wall"):
        assert banned not in text, banned


def test_the_receipt_states_what_it_does_not_establish():
    doc = json.loads(RECEIPT.read_text())
    text = doc["what_this_does_not_establish"]
    for phrase in ("guard language is given", "partial structure", "One stage pair"):
        assert phrase in text, phrase
    assert "NONE CLAIMED" in doc["novelty"]
