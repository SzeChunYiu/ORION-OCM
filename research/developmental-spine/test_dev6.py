"""Integrity tests for DEV-6, which audits this lane's own DEV-5 result.

A self-audit is the easiest place to be generous, so these tests check that the
audit is charged honestly in both directions: that the arm being audited is not
under-billed, that the arm proposed to replace it is not exempted from the
bookkeeping it adds, and that the comparison against DEV-5's published numbers is
read from DEV-5's receipt rather than typed from memory.
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
import dev6
import dev6_arms as A
import run_dev6 as R
from retain import demand_stream

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "DEV6_HONEST_CONSULTATION_PRICE_V1.json"
DEV5 = HERE.parent / "cognitive-ladder" / "results" / "DEV5_UNANIMITY_V1.json"


# --- the bill matches the work ---------------------------------------------

def test_each_mode_is_charged_what_its_test_actually_costs():
    src = inspect.getsource(A._run)
    body = src[src.index("def consult("):src.index("def serve(")]
    assert 'if mode == "singleton":' in body and "charge(1)" in body
    assert "charge(max(1, len(survivors)))" in body, (
        "the naive scan must be charged in proportion to what it scans")
    # One charge per query per mode. X6 added two compiled modes, which share one
    # consult branch with two exits -- a cache hit charged 1 and a miss charged the
    # scan -- so five charge sites cover the five modes. A compiled TABLE build is
    # not a query and goes through charge_compilation, which is counted separately
    # below so that it can never be mistaken for a per-query charge.
    assert body.count("charge(") == 5, "every mode must be charged exactly once per query"
    assert body.count("charge_compilation(") == 1


def test_the_incremental_arm_pays_for_its_own_bookkeeping():
    src = inspect.getsource(A.VoteBook)
    assert "self.maintenance += self.extension * len(survivors)" in src, "seeding"
    assert "self.maintenance += self.extension" in src, "each elimination"
    run = inspect.getsource(A._run)
    assert "phase.lookup_work += maintenance" in run, (
        "maintenance must reach total work, not just a side meter")


def test_maintenance_actually_lands_in_the_reported_work():
    world, _ = dev4.build_level_world(16, 16, 3, random.Random(7))
    d0 = demand_stream(world.base, 400, 1.0, random.Random(8))
    d1 = dev4.d1_stream(world, 60, 1.0, random.Random(9))
    _, p1, _, meters = A.run_arm("UNANIMITY_INCREMENTAL", world, d0, d1, 1536)
    assert meters["maintenance"] > 0
    assert p1.total_work(0.0) > meters["maintenance"]
    _, q1, _, qm = A.run_arm("SINGLETON", world, d0, d1, 1536)
    assert qm["maintenance"] == 0


def test_the_three_arms_differ_only_in_pricing_and_decision():
    """One serve loop; the mode is the only branch."""
    src = inspect.getsource(A._run)
    assert src.count("def serve(") == 1
    assert set(A.ARMS) == set(dev6.PRICING_MODES) or len(A.ARMS) == 3


# --- the comparison is read, not remembered --------------------------------

def test_dev5s_numbers_are_read_from_dev5s_receipt():
    src = inspect.getsource(R.dev5_ratio_range)
    assert "DEV5_RECEIPT" in src and "json.loads" in src
    lo, hi = R.dev5_ratio_range()
    published = [c["ratio_to"]["SINGLETON_FULL"] for c in json.loads(DEV5.read_text())["primary_grid"]]
    assert lo == min(published) and hi == max(published)


def test_the_earlier_hardcoding_error_is_recorded():
    doc = inspect.getdoc(R.dev5_ratio_range)
    assert "hard-coded" in doc
    assert "0.837" in doc and "was not" in doc


def test_the_correction_states_both_ranges_and_they_differ():
    doc = json.loads(RECEIPT.read_text())
    c = doc["correction_to_dev5"]
    assert c["dev5_reported_ratio_range"] != c["honest_price_ratio_range"]
    assert min(c["honest_price_ratio_range"]) > min(c["dev5_reported_ratio_range"]), (
        "the honest price can only make the audited arm look worse, never better")
    assert "its factor of up to 5.1 does not" in c["note"]


def test_the_erosion_is_reported_per_level():
    doc = json.loads(RECEIPT.read_text())
    by_level = doc["correction_to_dev5"]["mean_ratio_by_level"]
    assert set(by_level) == {"1", "2", "3"}
    assert all(0.0 < v <= 1.0 for v in by_level.values())


# --- the lane's own proposal is reported as refuted ------------------------

def test_the_proposed_fix_is_reported_as_refuted():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["P2_incremental_keeps_an_advantage"] is False
    v = doc["predictions"]["P2_verdict"]
    assert v.startswith("REFUTED, and this lane proposed the arm")
    assert "the only reason that is visible here is that the bookkeeping was charged" in v


def test_p5_the_reason_the_fix_was_proposed_is_also_reported_false():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["P5_naive_deliberation_exceeds_incremental_at_long_d1"] is False
    assert "never amortizes" in doc["predictions"]["P5_verdict"]


def test_the_failure_of_the_fix_is_explained_by_its_own_numbers():
    doc = json.loads(RECEIPT.read_text())
    w = doc["why_the_fix_failed"]
    assert w["mean_maintenance"] > w["mean_naive_consultation"], (
        "the receipt claims the bookkeeping outweighs the scanning; check it does")
    assert "bounded by the language rather than by the workload" in w["note"]


# --- the audit could have overturned the result ----------------------------

def test_the_kill_criterion_would_have_withdrawn_the_carry_advantage():
    src = inspect.getsource(R._terminal)
    assert "DEV5_FACTOR_WAS_A_PRICING_ARTIFACT" in src
    assert "resting on the language gift" in src
    kill = dev6.DEV6_PLAN["kill_criterion"]
    assert "DEV-5's receipt annotated accordingly" in kill


def test_correctness_cannot_move_and_did_not():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["P4_correctness_unchanged"] is True
    for c in doc["primary_grid"]:
        for arm in c["arms"].values():
            assert arm["min_correctness"] == 1.0


def test_the_receipt_corrects_rather_than_withdraws():
    doc = json.loads(RECEIPT.read_text())
    assert "its magnitude is corrected" in doc["authority"]
    assert "AUDIT OF THIS LANE'S OWN RESULT" in doc["authority"]
    assert doc["terminal"] == "DEV5_SURVIVES_A_SMALLER_RESULT"


def test_the_receipt_admits_pricing_has_no_ground_truth():
    doc = json.loads(RECEIPT.read_text())
    note = doc["what_this_does_not_establish"]
    assert "no fact of the matter" in note
    assert "a lane that wanted a particular answer could get it by choosing a scheme" in note
    assert "NONE CLAIMED" in doc["novelty"]


def test_the_receipt_carries_the_plan_and_no_wall_clock():
    doc = json.loads(RECEIPT.read_text())
    assert doc["commitment"]["commitment"] == dev6.COMMITMENT.commitment
    assert doc["plan"] == json.loads(json.dumps(dev6.DEV6_PLAN))
    text = RECEIPT.read_text().lower()
    for banned in ("elapsed", "timestamp", "duration_ms", "wall"):
        assert banned not in text, banned
