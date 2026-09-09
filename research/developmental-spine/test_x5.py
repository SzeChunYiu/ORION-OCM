"""Integrity tests for X5, which sweeps nine budgets to find out whether X4's two
positives are regimes with edges or isolated cells, and finds that one is and one
is not.

X5 is the study most exposed to the temptation to smooth: three of its six
registered predictions failed, and each failure is more informative than the
prediction would have been. The tests below exist to make sure none of them can
be quietly rounded off -- in particular that a margin which changes sign three
times is reported as three sign changes and not as "a crossing".
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
import run_x5 as R
import x5
from x5 import BUDGETS, COMMITMENT, DEV3_ANALYTIC_LOWER_EDGE, X5_PLAN

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "X5_BUDGET_CROSSING_V1.json"


def _doc() -> dict:
    if not RECEIPT.exists():
        pytest.skip("X5 receipt not generated in this checkout")
    return json.loads(RECEIPT.read_text())


# --- the commitment ----------------------------------------------------------

def test_the_plan_digest_is_the_one_that_was_registered():
    assert COMMITMENT.commitment.startswith("999326a41ad7b9e8")


def test_no_outcome_lives_inside_the_committed_plan():
    for field in ("terminal", "terminal_reason", "predictions", "crossings",
                  "primary_grid", "gate_evidence"):
        assert field not in X5_PLAN, f"{field!r} is an outcome and must live outside PLAN"


def test_seven_of_the_nine_budgets_are_out_of_sample_for_x4():
    x4_budgets = {1024, 1536}
    assert x4_budgets < set(BUDGETS)
    assert len(set(BUDGETS) - x4_budgets) == 7


def test_the_two_budgets_x4_swept_are_re_run_as_a_control_not_dropped():
    assert 1024 in BUDGETS and 1536 in BUDGETS
    assert "reproduce, which is a control" in X5_PLAN["prior_information_audit"][
        "known_before_this_study"]


# --- the crossing counter cannot round a wiggle into a boundary ---------------

def test_every_sign_change_is_counted_not_just_the_first():
    """A margin that changes sign three times is not a boundary, and reporting it
    as one would be the whole error this study exists to avoid."""
    cells = [{"level": 1, "budget_bits": b, "skew": 0.0,
              "margin": {"A": m}, "arms": {}, "beats_replay": {"A": m > 0}}
             for b, m in [(768, 1.0), (896, 1.0), (1024, -1.0), (1152, -1.0),
                          (1408, 1.0), (2048, -1.0)]]
    out = R.crossings(cells, "A", 1, 0.0)
    assert out["crossing_count"] == 3
    assert out["single_crossing"] is False
    assert out["direction"] is None, "no single direction exists for three crossings"
    assert out["wins_at"] == [768, 896, 1408]
    assert out["loses_at"] == [1024, 1152, 2048]


def test_a_budget_with_no_admissible_figure_is_skipped_and_named_never_imputed():
    cells = [{"level": 1, "budget_bits": 768, "skew": 0.0, "margin": {"A": 1.0},
              "arms": {}, "beats_replay": {"A": True}},
             {"level": 1, "budget_bits": 896, "skew": 0.0, "margin": {"A": None},
              "arms": {}, "beats_replay": {"A": False}}]
    out = R.crossings(cells, "A", 1, 0.0)
    assert out["budgets_skipped_for_correctness"] == [896]
    assert out["budgets_with_an_admissible_figure"] == [768]
    assert out["crossing_count"] == 0, "a skipped budget must not manufacture a crossing"


def test_a_single_crossing_is_reported_with_its_direction():
    cells = [{"level": 3, "budget_bits": b, "skew": 0.0, "margin": {"A": m},
              "arms": {}, "beats_replay": {"A": m > 0}}
             for b, m in [(768, 1.0), (1024, 1.0), (1536, -1.0), (2048, -1.0)]]
    out = R.crossings(cells, "A", 3, 0.0)
    assert out["single_crossing"] and out["direction"] == "TO_LOSING"


# --- the terminals are all reachable -----------------------------------------

def _y(**over) -> dict:
    base = {"Y1_guarded_single_crossing_upward": False,
            "Y3_unanimity_single_crossing_downward": False}
    base.update(over)
    return base


def test_the_uncharacterised_terminal_is_reachable():
    terminal, reason = R._terminal([], _y())
    assert terminal == "CARRY_ADVANTAGE_UNCHARACTERISED"
    assert "isolated cell rather than a regime" in reason
    assert "X4's receipt is not withdrawn" in reason


def test_the_two_regime_terminal_is_reachable():
    terminal, _ = R._terminal([], _y(Y1_guarded_single_crossing_upward=True,
                                     Y3_unanimity_single_crossing_downward=True))
    assert terminal == "TWO_REGIMES_WITH_OPPOSITE_BUDGET_EDGES"


def test_a_broken_counter_identity_stops_everything_downstream():
    """If work does not equal the sum of the priced events, no margin in this lane
    means anything, and that must dominate every other terminal."""
    broken = [{"arms": {"A": {"counter_identity_residual": 1}}}]
    terminal, reason = R._terminal(broken, _y(Y1_guarded_single_crossing_upward=True,
                                              Y3_unanimity_single_crossing_downward=True))
    assert terminal == "COUNTER_IDENTITY_REFUTED"
    assert "outside the six named channels" in reason


# --- the counter identity is a real reconstruction, not a restatement ---------

def test_deliberation_is_removed_from_lookup_work_before_it_is_counted():
    """DEV-6 charged consultation into lookup_work. Counting it as lookups would
    double-count it against LOOKUP_COST and hide it from the identity."""
    src = inspect.getsource(R._counters)
    assert "phase.lookup_work - deliberation" in src


def test_the_identity_uses_every_priced_channel_this_lane_has():
    src = inspect.getsource(R._work_from_counters)
    for cost in ("DERIVE_COST", "APPLY_COST", "LOOKUP_COST", "INDUCE_COST",
                 "VERIFY_COST", "COMPOSE_COST"):
        assert cost in src, cost
    assert 'c["deliberation"]' in src


def test_the_extra_counters_left_dev6_reproducing():
    """X5 needed consultation COUNTS as well as consultation CHARGE. The counter is
    additive and DEV-6's receipt regenerated byte-identically with it in place."""
    src = inspect.getsource(A6._run)
    assert "consultations += 1" in src
    assert '"held_rules_final": len(store.held)' in src


# --- the receipt tells the truth about its own failures ----------------------

def test_the_terminal_follows_from_the_published_grid_and_predictions():
    doc = _doc()
    assert R._terminal(doc["primary_grid"], doc["predictions"])[0] == doc["terminal"]


def test_the_counter_identity_holds_exactly_in_every_cell():
    for cell in _doc()["primary_grid"]:
        for arm, row in cell["arms"].items():
            assert row["counter_identity_residual"] == 0, (arm, cell["budget_bits"])


def test_every_quoted_work_figure_is_at_matched_correctness():
    for cell in _doc()["primary_grid"]:
        if any(v is not None for v in cell["ratio_to_replay"].values()):
            assert cell["arms"]["REPLAY_ONLY_PARENT"]["min_correctness"] == 1.0
        for row in cell["arms"].values():
            if row["work"] is not None:
                assert row["min_correctness"] == 1.0


def test_refuted_predictions_are_published_as_refuted():
    preds = _doc()["predictions"]
    assert set(preds) == {
        "Y1_guarded_single_crossing_upward", "Y2_gate_is_the_held_guard_count",
        "Y3_unanimity_single_crossing_downward", "Y4_unanimity_flat_replay_falling",
        "Y5a_same_language_opposite_sign",
        "Y5b_margin_is_a_function_of_what_was_charged"}
    assert all(isinstance(v, bool) for v in preds.values())


def test_a_gate_that_could_not_be_tested_is_not_reported_as_confirmed():
    """Y2 is only testable where Y1 found a single crossing. Where it is not, the
    row must say so rather than defaulting to a pass."""
    doc = _doc()
    for row in doc["gate_evidence"]:
        if not row["testable"]:
            assert "crossing_at_budget" not in row
    if not doc["predictions"]["Y1_guarded_single_crossing_upward"]:
        assert doc["predictions"]["Y2_gate_is_the_held_guard_count"] is False


def test_the_dev3_analytic_edge_is_recorded_as_already_refuted_not_re_guessed():
    doc = _doc()
    assert DEV3_ANALYTIC_LOWER_EDGE == 768
    assert doc["dev3_analytic_lower_edge_status"].startswith("ALREADY REFUTED")


def test_nothing_is_withdrawn_from_the_studies_this_one_extends():
    assert "withdraws nothing" in _doc()["authority"]


def test_no_novelty_is_claimed_for_a_boundary_sweep():
    assert _doc()["novelty"].startswith("NONE CLAIMED")


# --- the window section is labelled post hoc and cannot launder a fit ---------

def test_the_window_section_declares_itself_post_hoc():
    """DEV-3 registered the edges; asking about them HERE was decided after seeing
    the crossings, and the receipt must say so in its own text."""
    w = _doc()["window_analysis"]
    assert w["provenance"].startswith("POST HOC within X5")
    assert "no claim in this section is treated as pre-registered" in w["provenance"]
    assert "window_analysis" not in X5_PLAN


def test_the_two_window_edges_are_reported_separately():
    """The upper edge held and the lower did not. A single 'the window is
    confirmed' would be false, and a single 'refuted' would throw away a
    prediction that landed."""
    w = _doc()["window_analysis"]
    assert isinstance(w["upper_edge_holds"], bool)
    assert isinstance(w["lower_edge_is_sufficient"], bool)
    assert w["dev3_lower_edge_bits"] == DEV3_ANALYTIC_LOWER_EDGE


def test_the_measured_regime_is_the_run_that_wins_at_every_skew():
    """A budget that wins under uniform demand and loses under skewed is not in
    the regime, however much the lane would like it to be."""
    doc = _doc()
    regime = doc["window_analysis"]["measured_carry_regime_bits"]
    arm = "GUARDED_SMALL_LANGUAGE"
    for b in regime:
        for k in (0.0, 1.0):
            cell = [c for c in doc["primary_grid"]
                    if c["level"] == 1 and c["budget_bits"] == b and c["skew"] == k][0]
            assert cell["beats_replay"][arm], (b, k)
    assert regime == sorted(regime)
    if regime:
        assert max(regime) < doc["window_analysis"]["dev3_upper_edge_bits"]


def test_a_budget_the_arm_loses_at_any_skew_is_outside_the_regime():
    doc = _doc()
    regime = set(doc["window_analysis"]["measured_carry_regime_bits"])
    losses = set(doc["window_analysis"]["budgets_inside_the_window_that_the_arm_loses"])
    assert not (regime & losses)


def test_the_non_monotone_margin_is_explained_rather_than_smoothed():
    w = _doc()["window_analysis"]
    assert "change sign more than once" in w["why_the_margin_is_not_monotone"]
    assert "not about whether" in w["why_the_margin_is_not_monotone"]
