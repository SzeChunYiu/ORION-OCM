"""Integrity tests for DEV-2, which withdraws this lane's own positive result.

A lane that has just lost a result has every incentive to lose it quietly, so the
tests here are aimed at the ways that could happen: the parents could be given
less than the lineage, the failed predictions could be smoothed over, the
mechanism sweep could be summarised with a statistic that flatters the
explanation, and DEV-1's numbers could drift while the code around them changed.
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

import dev1
import dev1_arms as A
import dev2_parents as D2
import run_dev2 as R

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "DEV2_CONTINUAL_PARENTS_V1.json"
DEV1_RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "DEV1_D0_TO_D1_V1.json"


def fixture(budget=1024, seed=11):
    world = dev1.build_d1_world(16, 16, dev1.EXCEPTION_RATE, random.Random(seed))
    from retain import demand_stream
    d0 = demand_stream(world.base, 600, 1.0, random.Random(seed + 1))
    d1 = dev1.d1_stream(world, 300, 1.0, random.Random(seed + 2))
    return world, d0, d1, budget


# --- DEV-1 must not have moved ---------------------------------------------

def test_adding_the_ewc_hook_did_not_change_dev1():
    """The protection parameters default to empty; DEV-1's receipt must reproduce."""
    import subprocess
    before = json.loads(DEV1_RECEIPT.read_text())
    subprocess.run([sys.executable, "run_dev1.py"], cwd=HERE, check=True,
                   capture_output=True)
    assert json.loads(DEV1_RECEIPT.read_text()) == before


def test_protection_defaults_are_empty():
    sig = inspect.signature(A._evict_for)
    assert sig.parameters["protected_rules"].default == frozenset()
    assert sig.parameters["protected_facts"].default == frozenset()
    assert inspect.signature(A.run_d1).parameters["protect"].default == (
        frozenset(), frozenset())


def test_protection_is_dropped_rather_than_deadlocking():
    src = inspect.getsource(A._evict_for)
    assert "free_facts" in src and "free_rules" in src
    assert src.count("if store.facts:") >= 1, (
        "there must be a fallback that evicts protected objects when nothing else is left")


# --- the parents are not handicapped ---------------------------------------

@pytest.mark.parametrize("name", sorted(D2.PARENTS))
def test_every_parent_answers_every_demand(name):
    world, d0, d1, budget = fixture()
    p0, p1, carried = D2.PARENTS[name](world, d0, d1, budget)
    assert p1.served == len(d1)
    assert p1.correctness() == 1.0


@pytest.mark.parametrize("name", sorted(D2.PARENTS))
def test_every_parent_runs_the_same_streams_and_budget(name):
    src = inspect.getsource(D2.PARENTS[name])
    assert "run_d0(world, d0, budget" in src
    assert "run_d1(world, d1, budget" in src


def test_replay_only_never_induces_anything():
    world, d0, d1, budget = fixture()
    p0, p1, carried = D2.replay_only(world, d0, d1, budget)
    assert p0.inductions == 0 and p1.inductions == 0
    assert not carried.rules


def test_consolidation_reads_only_the_bounded_buffer():
    """It must not be handed the lineage's uncharged record of everything seen."""
    src = inspect.getsource(D2.consolidate)
    assert "store.facts" in src
    assert "store.seen" not in src, (
        "consolidating from `seen` would give the parent memory it never paid for")


def test_consolidation_respects_the_budget():
    world, d0, d1, budget = fixture(budget=256)
    store, phase = A.run_d0(world, d0, budget, induce_base=False)
    D2.consolidate(store, world, budget, phase)
    assert store.bits() <= budget


def test_ewc_protects_a_declared_fraction_and_not_all_of_it():
    assert 0.0 < D2.EWC_PROTECTED_QUANTILE < 1.0, (
        "1.0 is DEV-1's saturation failure and 0.0 is CONTINUED_OCM; the parameter is "
        "only interesting strictly inside")


def test_ewc_importance_comes_from_d0_usage_only():
    src = inspect.getsource(D2.d0_importance)
    assert "d0" in src and "d1" not in src.replace("d1World", "")


# --- the mechanism sweep is summarised honestly -----------------------------

def test_the_flip_point_is_where_abstraction_loses_not_the_cheapest_swept_cost():
    doc = json.loads(RECEIPT.read_text())
    block = doc["why_replay_wins"]
    rows = {r["verify_cost"]: r for r in block["verify_cost_sweep"]}
    flip = block["flip_point"]
    assert flip is not None and flip > 0
    assert rows[flip]["continued_wins"] is False
    below = [c for c in rows if c < flip]
    assert below and all(rows[c]["continued_wins"] for c in below), (
        "every price below the flip must be one where abstraction still pays")
    assert block["highest_verify_cost_where_abstraction_still_pays"] == max(below)


def test_the_sweep_brackets_the_flip_on_both_sides():
    doc = json.loads(RECEIPT.read_text())
    rows = doc["why_replay_wins"]["verify_cost_sweep"]
    assert any(r["continued_wins"] for r in rows)
    assert any(not r["continued_wins"] for r in rows)


def test_a_zero_flip_point_would_declare_the_explanation_wrong():
    """The receipt must be able to say its own explanation failed."""
    src = inspect.getsource(R.build)
    assert "the explanation offered here is WRONG" in src
    assert 'flip_point == 0' in src


def test_the_registered_verify_cost_row_matches_the_primary_grid():
    doc = json.loads(RECEIPT.read_text())
    registered = doc["plan"]["registered_verify_cost"]
    row = next(r for r in doc["why_replay_wins"]["verify_cost_sweep"]
               if r["verify_cost"] == registered)
    cell = next(c for c in doc["primary_grid"]
                if c["d1_length"] == 1000 and c["budget_bits"] == 1024)
    assert row["ratio_continued_over_replay"] == pytest.approx(
        cell["ratio_to"]["REPLAY_ONLY_PARENT"])


# --- the failed predictions are reported as failed --------------------------

def test_the_two_false_predictions_are_stated_as_false():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["Q2_the_parent_is_replay_only"] is False
    assert doc["predictions"]["Q3_ewc_loses_to_the_lineage"] is False
    c = doc["predictions_commentary"]
    assert c["Q2_verdict"].startswith("FALSE")
    assert c["Q3_verdict"].startswith("FALSE")
    assert "EWC_PARENT" in c["Q2_verdict"], "the exception must be named, not summarised"


def test_the_damaging_shape_is_reported_not_only_the_headline():
    doc = json.loads(RECEIPT.read_text())
    note = doc["the_advantage_grows_rather_than_decaying"]
    assert "opposite shape" in note
    assert "more damaging of the two facts" in note
    grid = {(c["d1_length"], c["budget_bits"]): c["ratio_to"]["REPLAY_ONLY_PARENT"]
            for c in doc["primary_grid"]}
    at_1024 = [grid[(n, 1024)] for n in (250, 1000, 4000)]
    assert at_1024 == sorted(at_1024), "the receipt claims it grows; check it does"


# --- terminals --------------------------------------------------------------

def _cells(ratios, correctness=1.0):
    out = []
    for (n, b), r in ratios.items():
        arms = {a: {"correctness": correctness, "d1_work": 1.0, "d0_work": 1.0}
                for a in list(D2.PARENTS) + ["CONTINUED_OCM", "RESET_OCM"]}
        out.append({"d1_length": n, "budget_bits": b, "arms": arms,
                    "ratio_to": {a: v for a, v in r.items()},
                    "continued_is_beaten_by": sorted(a for a, v in r.items()
                                                     if v > 1.0 and a in D2.PARENTS)})
    return out


def test_the_lineage_can_still_survive():
    cells = _cells({(250, 1024): {a: 0.5 for a in D2.PARENTS}})
    t, reason = R._terminal(cells)
    assert t == "LINEAGE_SURVIVES_ITS_CONTINUAL_LEARNING_PARENTS"
    assert "closes in the lineage's favour" in reason


def test_unmatched_correctness_blocks_the_comparison():
    cells = _cells({(250, 1024): {a: 2.0 for a in D2.PARENTS}}, correctness=0.9)
    t, _ = R._terminal(cells)
    assert t == "INADMISSIBLE_CORRECTNESS_NOT_MATCHED"


def test_the_receipt_withdraws_a_positive_and_says_which_direction_that_is():
    doc = json.loads(RECEIPT.read_text())
    assert doc["terminal"] == "CARRY_ADVANTAGE_IS_PARENT_SUFFICIENT"
    assert "withdraws a POSITIVE" in doc["authority"]
    assert "reclassified from a result into an absorption" in doc["terminal_reason"]
    assert "DEV-1's comparison against RESET_OCM stands" in doc["terminal_reason"], (
        "withdrawing the carry claim must not also withdraw the control it did run")


def test_the_consequence_for_the_law_is_recorded_not_patched():
    doc = json.loads(RECEIPT.read_text())
    c = doc["consequence_for_the_synthesis_law"]
    assert "MISPREDICTS" in c
    assert "NOT patched in as a fourth coordinate" in c
    assert "is not a law" in c


def test_the_receipt_carries_no_wall_clock_and_names_its_analogy_risk():
    doc = json.loads(RECEIPT.read_text())
    assert "entitled to that objection" in doc["what_this_does_not_establish"]
    assert "NONE CLAIMED" in doc["novelty"]
    text = RECEIPT.read_text().lower()
    for banned in ("elapsed", "timestamp", "duration_ms", "wall"):
        assert banned not in text, banned


def test_only_the_lineage_moves_across_the_verify_sweep():
    """Replay holds no rules, so it never verifies; if its work moves, the sweep
    is varying something other than the price and proves nothing about it."""
    doc = json.loads(RECEIPT.read_text())
    block = doc["why_replay_wins"]
    assert block["replay_work_is_constant_across_the_sweep"] is True
    works = {r["replay_only_d1_work"] for r in block["verify_cost_sweep"]}
    assert len(works) == 1, works
    lineage = [r["continued_d1_work"] for r in block["verify_cost_sweep"]]
    assert lineage == sorted(lineage) and lineage[0] < lineage[-1]
