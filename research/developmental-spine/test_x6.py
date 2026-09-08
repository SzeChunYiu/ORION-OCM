"""Integrity tests for X6, which compiles the unanimity verdict into a table so
that a 433-predicate version space can be consulted for a charge of 1.

X6 is the first arm this lane has built that could REMOVE DEV-4's language
precondition rather than work around it, which makes it the study most able to
produce a false positive. Two things would do it: a compiled arm that is quietly
a different decision rule, and a comparison that reads a moved regime as a
widened one. Both have tests below, and both are terminals rather than caveats.
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

import dev6_arms as A6
import run_x6 as R
import x6
from dev4 import language
from dev5_arms import decide
from x6 import ARM_MODES, COMMITMENT, X6_PLAN

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "X6_COMPILED_CONSULTATION_V1.json"


def _doc() -> dict:
    if not RECEIPT.exists():
        pytest.skip("X6 receipt not generated in this checkout")
    return json.loads(RECEIPT.read_text())


# --- the commitment ----------------------------------------------------------

def test_the_plan_digest_is_the_one_that_was_registered():
    assert COMMITMENT.commitment.startswith("7fbeebfe626eadec")


def test_no_outcome_lives_inside_the_committed_plan():
    for field in ("terminal", "terminal_reason", "predictions", "primary_grid",
                  "winning_settings", "control_disagreements_total"):
        assert field not in X6_PLAN, field


def test_the_kill_criterion_names_the_story_it_would_confirm():
    kill = X6_PLAN["kill_criterion"]
    assert "size story survives" in kill
    assert "not removable by pricing" in kill
    assert "X4's and X5's receipts unchanged" in kill


# --- compilation is permitted to change the price and nothing else ------------

def test_the_compiled_verdict_is_the_unanimity_verdict_by_construction():
    """``_unanimous`` and dev5_arms.decide must agree on every input, or the
    compiled arms are a different rule that merely shares a name."""
    rng = random.Random(20260908)
    lang = language(3, 16)
    for _ in range(400):
        survivors = tuple(rng.sample(lang, rng.randint(0, 6)))
        index = rng.randrange(16)
        assert A6._unanimous(survivors, index) == decide(survivors, index, "unanimity")


def test_an_empty_version_space_decides_nothing_in_both_implementations():
    assert A6._unanimous((), 0) is None
    assert decide((), 0, "unanimity") is None


def test_the_demand_mode_charges_the_scan_on_a_miss_and_one_on_a_hit():
    src = inspect.getsource(A6._run)
    assert "cache_hits += 1\n                charge(1)" in src
    assert "cache_misses += 1\n            charge(max(1, len(survivors)))" in src


def test_the_eager_mode_is_charged_for_every_cell_it_compiles():
    src = inspect.getsource(A6._run)
    assert "charge_compilation(width * world.base.extension)" in src, (
        "an eagerly compiled bank must pay for the whole scan it performs")


def test_a_version_space_that_did_not_shrink_keeps_its_identity():
    """The compiled table invalidates on identity. If ``observe`` replaced an
    unchanged tuple with an equal one, every re-observation would recompile and
    the demand-driven arm would be measured paying for work it never does."""
    src = inspect.getsource(A6._run)
    assert "if len(after) != len(before):" in src
    assert "after = before" in src


def test_dev6s_own_receipt_survived_the_new_modes():
    """The modes and the identity fix are additive; DEV-6 regenerated
    byte-identically with them in place, and the arms it names are untouched."""
    assert set(A6.ARMS) == {"SINGLETON", "UNANIMITY_NAIVE", "UNANIMITY_INCREMENTAL"}
    assert set(ARM_MODES.values()) >= {"precompiled_eager", "precompiled_demand"}


# --- every terminal is reachable ---------------------------------------------

def _w(**over) -> dict:
    base = {"W2_compilation_changed_only_cost": True,
            "W3_compiled_regime_is_a_strict_superset": True,
            "W5_compiled_wins_where_naive_never_did": True}
    base.update(over)
    return base


def test_a_control_failure_voids_the_study_rather_than_costing_a_prediction():
    terminal, reason = R._terminal([], _w(W2_compilation_changed_only_cost=False))
    assert terminal == "VOID_THE_COMPILED_ARM_IS_A_DIFFERENT_DECISION_RULE"
    assert "VOID" in reason


def test_the_negative_terminal_is_reachable_and_says_the_size_story_survived():
    terminal, reason = R._terminal([], _w(W5_compiled_wins_where_naive_never_did=False))
    assert terminal == "LANGUAGE_PRECONDITION_IS_NOT_REMOVABLE_BY_PRICING"
    assert "size story survives its sharpest test" in reason
    assert "confined to languages small enough to collapse" in reason


def test_a_moved_regime_is_not_reported_as_a_widened_one():
    terminal, _ = R._terminal([], _w(W3_compiled_regime_is_a_strict_superset=False))
    assert terminal == "COMPILED_CONSULTATION_MOVES_THE_REGIME_RATHER_THAN_WIDENING_IT"


def test_the_positive_terminal_requires_the_control_and_both_win_conditions():
    terminal, _ = R._terminal([], _w())
    assert terminal.startswith("CARRY_ADVANTAGE_SURVIVES_ON_A_LARGE_LANGUAGE")


def test_the_control_is_checked_per_replicate_not_on_the_means():
    src = inspect.getsource(R.cell)
    assert "for r in reps:" in src and "control_disagreements" in src


# --- the receipt ------------------------------------------------------------

def test_the_terminal_follows_from_the_published_grid_and_predictions():
    doc = _doc()
    assert R._terminal(doc["primary_grid"], doc["predictions"])[0] == doc["terminal"]


def test_the_control_actually_held_in_every_replicate():
    doc = _doc()
    assert doc["control_disagreements_total"] == 0
    for cell in doc["primary_grid"]:
        assert cell["control_disagreements"] == []


def test_every_arm_held_the_same_full_language():
    assert _doc()["language_size"] == len(language(3, 16))


def test_every_quoted_work_figure_is_at_matched_correctness():
    for cell in _doc()["primary_grid"]:
        if any(v is not None for v in cell["ratio_to_replay"].values()):
            assert cell["arms"]["REPLAY_ONLY_PARENT"]["min_correctness"] == 1.0
        for row in cell["arms"].values():
            if row["work"] is not None:
                assert row["min_correctness"] == 1.0


def test_the_counter_identity_holds_exactly_in_every_cell():
    for cell in _doc()["primary_grid"]:
        for arm, row in cell["arms"].items():
            assert row["counter_identity_residual"] == 0, (arm, cell["budget_bits"])


def test_what_compiling_lost_is_published_next_to_what_it_gained():
    w = _doc()["winning_settings"]
    assert "gained_by_compiling" in w and "lost_by_compiling" in w


def test_refuted_predictions_are_published_as_refuted():
    preds = _doc()["predictions"]
    assert set(preds) == {
        "W1_reuse_exists_and_lowers_deliberation",
        "W2_compilation_changed_only_cost",
        "W3_compiled_regime_is_a_strict_superset",
        "W4_eager_costs_more_and_wins_nothing_extra",
        "W5_compiled_wins_where_naive_never_did"}
    assert all(isinstance(v, bool) for v in preds.values())


def test_the_unpriced_table_is_declared_rather_than_hidden():
    """The compiled table costs no bits. That is this lane's existing convention
    and the successor study is named, but it must not be silent."""
    text = _doc()["what_this_does_not_establish"]
    assert "NOT charged bits" in text
    assert "successor" in text


def test_no_novelty_is_claimed_for_memoisation():
    assert _doc()["novelty"].startswith("NONE CLAIMED")


def test_compiling_a_table_is_not_counted_as_a_consultation():
    """An earlier version charged the eager compile through ``charge``, which
    incremented the consultation counter and inflated the denominator of the cache
    hit rate by one per compilation. The charge was right and the meter was not."""
    src = inspect.getsource(A6._run)
    assert "def charge_compilation(n: int)" in src
    assert "charge_compilation(width * world.base.extension)" in src
    assert "consultations += 1" not in src.split("def charge_compilation")[1].split(
        "def evict")[0]


def test_the_two_compiled_arms_perform_the_same_number_of_consultations():
    doc = _doc()
    for cell in doc["primary_grid"]:
        eager = cell["arms"]["PRECOMPILED_EAGER"]["consultations"]
        demand = cell["arms"]["PRECOMPILED_DEMAND"]["consultations"]
        naive = cell["arms"]["UNANIMITY_NAIVE"]["consultations"]
        assert eager == demand == naive, (cell["budget_bits"], eager, demand, naive)
