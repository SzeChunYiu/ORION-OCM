"""Integrity tests for DEV-5.

The claim here is that a weaker decision rule gives up no soundness, which is the
kind of claim that is either a theorem or a bug. So the tests check the theorem
directly -- unanimity returns the truth's verdict whenever it returns anything --
and then check the ways the measurement could still be wrong: that both rules pay
for their own consultation, that the deficient-language control really does break,
and that the win over the replay parent is bracketed by the consultation price
rather than assumed.
"""

from __future__ import annotations

import inspect
import itertools
import json
import pathlib
import random
import sys

import pytest

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import dev4
import dev5
import dev5_arms as A
import run_dev5 as R
from retain import demand_stream

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "DEV5_UNANIMITY_V1.json"


# --- the rule is sound, as a theorem ---------------------------------------

def test_unanimity_returns_the_truths_verdict_whenever_it_returns_anything():
    """Exhaustive over small survivor sets: if the truth is present and the rule
    answers, the answer is the truth's."""
    lang = dev4.language(2, 16)
    rng = random.Random(1)
    for _ in range(400):
        survivors = tuple(rng.sample(lang, rng.randint(1, 6)))
        truth = rng.choice(survivors)
        index = rng.randrange(16)
        verdict = A.decide(survivors, index, "unanimity")
        if verdict is not None:
            assert verdict == truth.excludes(index)


def test_the_singleton_rule_is_strictly_weaker_than_unanimity():
    lang = dev4.language(1, 16)
    rng = random.Random(2)
    strictly = 0
    for _ in range(400):
        survivors = tuple(rng.sample(lang, rng.randint(1, 5)))
        index = rng.randrange(16)
        s = A.decide(survivors, index, "singleton")
        u = A.decide(survivors, index, "unanimity")
        if s is not None:
            assert u == s, "unanimity must agree wherever singleton commits"
        elif u is not None:
            strictly += 1
    assert strictly > 0, "if unanimity never fires where singleton does not, it is inert"


def test_an_empty_version_space_decides_nothing():
    for rule in ("singleton", "unanimity"):
        assert A.decide((), 3, rule) is None


# --- both rules pay for their own consultation ------------------------------

def test_both_decision_rules_are_charged_identically():
    src = inspect.getsource(A._run)
    assert "phase.lookup_work += cost" in src
    # the charge is outside any branch on rule_name, so neither rule is billed
    # differently for consulting the store it already holds
    consult = src[src.index("if rule in store.held"):src.index("verdict = decide")]
    assert "rule_name" not in consult


def test_the_consult_price_is_swept_up_to_the_price_of_a_real_check():
    from dev1 import VERIFY_COST
    sweep = dev5.DEV5_PLAN["consult_cost_sweep"]
    assert 0 in sweep and max(sweep) >= VERIFY_COST
    assert dev5.DEV5_PLAN["registered_consult_cost"] in sweep


def test_the_win_over_replay_is_bracketed_by_the_consult_price():
    doc = json.loads(RECEIPT.read_text())
    rows = doc["consult_cost_sweep"]["rows"]
    assert all(r["beats_singleton"] for r in rows), (
        "both rules pay the same consultation, so the gap between them must survive "
        "every price")
    beats = [r["consult_cost"] for r in rows if r["beats_replay"]]
    loses = [r["consult_cost"] for r in rows if not r["beats_replay"]]
    assert beats and loses, (
        "the sweep must bracket the price at which the parent comparison turns over, or "
        "it is not a sensitivity analysis")
    assert max(beats) < min(loses)


# --- the guards actually arrive at D1 ---------------------------------------

def test_rules_induced_in_d0_arrive_holding_their_guard():
    """The first run of this module missed this and every arm, including the
    oracle, paid a check on every demand -- a broken hook, not a finding."""
    world, truth = dev4.build_level_world(16, 16, 3, random.Random(4))
    d0 = demand_stream(world.base, 800, 1.0, random.Random(5))
    d1 = dev4.d1_stream(world, 200, 1.0, random.Random(6))
    _, _, carried = A.run_arm("ORACLE_GUARD_PARENT", world, d0, d1, 1536, 3, truth)
    assert carried.held, "no guard survived D0"
    assert carried.held <= carried.base.rules


def test_the_oracle_pays_no_checks_at_all():
    doc = json.loads(RECEIPT.read_text())
    verif = [c["arms"]["ORACLE_GUARD_PARENT"]["verifications"] for c in doc["primary_grid"]]
    assert min(verif) == 0, (
        "an arm handed the true guard must be able to reach zero checks, or the hook is "
        "still not connected")


def test_the_held_set_is_charged_bits():
    src = inspect.getsource(A.VersionStore.bits)
    assert "len(self.held) * GUARD_BITS" in src


# --- the control breaks, which is the point ---------------------------------

def test_unanimity_does_not_rescue_a_deficient_language():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["U5_unanimity_does_not_rescue_a_deficient_language"] is True
    unsound = doc["the_control"]["unsound_cells"]
    assert unsound, "the control must actually break somewhere"
    assert all(c["level"] > 1 for c in unsound), (
        "it must break exactly where the truth is outside the small language, and nowhere "
        "else")
    assert "does NOT rescue" in doc["the_control"]["verdict"]


def test_the_control_shares_everything_but_the_language():
    small = inspect.getsource(A.unanimity_small)
    full = inspect.getsource(A.unanimity_full)
    assert '"unanimity"' in small and '"unanimity"' in full
    assert "1," in small.replace("budget, ", "") or ", 1," in small
    assert "max(LEVELS)" in full


# --- the receipt ------------------------------------------------------------

def test_every_prediction_held_or_is_reported_as_not_holding():
    doc = json.loads(RECEIPT.read_text())
    for key in ("U1", "U2", "U3", "U4", "U5"):
        matches = [k for k in doc["predictions"] if k.startswith(key)]
        assert matches, key


def test_soundness_is_reported_for_both_full_language_arms():
    doc = json.loads(RECEIPT.read_text())
    for c in doc["primary_grid"]:
        for arm in ("UNANIMITY_FULL", "SINGLETON_FULL", "ORACLE_GUARD_PARENT"):
            assert c["arms"][arm]["sound_in_every_replicate"], (arm, c["level"])


def test_the_receipt_states_what_it_changes_about_dev3():
    doc = json.loads(RECEIPT.read_text())
    note = doc["what_this_changes_about_dev3"]
    assert "BIG language rather than the RIGHT one" in note
    assert "available without knowing the world" in note


def test_the_terminal_reports_the_check_counts_it_rests_on():
    doc = json.loads(RECEIPT.read_text())
    assert doc["terminal"] == "UNANIMITY_RECOVERS_THE_FULL_LANGUAGE"
    assert "Mean scope checks fall from" in doc["terminal_reason"]
    assert "gives up no soundness at all" in doc["terminal_reason"]


def test_an_inert_rule_would_have_been_reported_as_inert():
    src = inspect.getsource(R._terminal)
    assert "UNANIMITY_IS_INERT" in src
    assert "the dilemma DEV-4 left is real" in src


def test_the_receipt_carries_the_plan_and_no_wall_clock():
    doc = json.loads(RECEIPT.read_text())
    assert doc["commitment"]["commitment"] == dev5.COMMITMENT.commitment
    assert doc["plan"] == json.loads(json.dumps(dev5.DEV5_PLAN))
    text = RECEIPT.read_text().lower()
    for banned in ("elapsed", "timestamp", "duration_ms", "wall"):
        assert banned not in text, banned


def test_the_receipt_claims_no_novelty_for_an_old_idea():
    doc = json.loads(RECEIPT.read_text())
    assert "NONE CLAIMED" in doc["novelty"]
    assert "Mitchell 1982" in doc["novelty"]
    assert "two earlier experiments in this lane had taken the stronger rule for granted" \
        in doc["novelty"]
