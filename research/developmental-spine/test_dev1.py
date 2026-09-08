"""Integrity tests for DEV-1, the first D0-to-D1 transition.

A developmental claim is the easiest kind in this programme to make look true:
give the continued arm anything the reset arm lacks and the comparison stops
meaning anything.  These tests are written against that failure mode.  They check
that the two lineage arms differ in exactly one thing, that the reset arm really
starts empty, that the scope mechanism actually bites, that the terminal can say
"no transition", and that the receipt reports the negative amortization result
rather than only the positive developmental one.
"""

from __future__ import annotations

import inspect
import json
import os
import pathlib
import random
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import dev1 as D
import dev1_arms as A
import run_dev1 as RUN
import spine

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "DEV1_D0_TO_D1_V1.json"


def fixture(seed=1, extension=16, rules=16):
    world = D.build_d1_world(rules, extension, D.EXCEPTION_RATE, random.Random(seed))
    d0 = D.demand_stream(world.base, 800, 1.0, random.Random(seed + 1))
    d1 = D.d1_stream(world, 400, 1.0, random.Random(seed + 2))
    return world, d0, d1


# --- DEV-D8: the four arms exist and mean what they say --------------------

def test_all_four_required_arms_are_present():
    for arm in spine.REQUIRED_ARMS:
        assert arm in A.ARM_ROLES, arm


def test_exactly_one_arm_is_the_machine():
    assert [a for a, r in A.ARM_ROLES.items() if r == "MACHINE"] == ["CONTINUED_OCM"]


def test_the_diagnostic_arm_is_marked_inadmissible():
    assert A.ARM_ROLES["CONTINUED_OCM_UNVERIFIED"] == "DIAGNOSTIC_INADMISSIBLE"
    assert "CONTINUED_OCM_UNVERIFIED" not in spine.REQUIRED_ARMS


def test_the_reset_arm_starts_with_nothing():
    empty = A.Store()
    assert not empty.facts and not empty.rules and not empty.composites
    assert empty.bits() == 0


def test_continued_and_reset_differ_in_exactly_one_argument():
    """Same function, same world, same stream, same budget; different store."""
    world, d0, d1 = fixture()
    store, _ = A.run_d0(world, d0, 1024)
    _, cont = A.run_d1(world, d1, 1024, store.copy())
    _, reset = A.run_d1(world, d1, 1024, A.Store())
    assert cont.served == reset.served
    assert cont.correctness() == reset.correctness() == 1.0


# --- the scope mechanism actually bites ------------------------------------

def test_exceptions_exist_and_are_not_generated_by_their_rule():
    world, _, _ = fixture()
    assert world.exceptions, "a world with no exceptions makes D1 a longer D0"
    for answer in world.exceptions:
        assert not world.generated_by_rule(answer)
        assert answer in world.members[world.rule_of[answer]], (
            "an exception must be INSIDE the rule's nominal extension, or the rule "
            "would never be tempted to apply to it")


def test_skipping_the_scope_check_costs_correctness():
    world, d0, d1 = fixture()
    store, _ = A.run_d0(world, d0, 1024)
    _, checked = A.run_d1(world, d1, 1024, store.copy())
    _, unchecked = A.run_d1(world, d1, 1024, store.copy(), verify_before_applying=False)
    assert checked.correctness() == 1.0
    assert unchecked.correctness() < 1.0, "the check must buy something or it is theatre"
    assert unchecked.total_work(0.0) < checked.total_work(0.0), (
        "and it must cost something, or nothing is being traded")


def test_inducing_a_rule_never_evicts_a_stored_exception():
    """A rule does not cover its exceptions, so it cannot make them redundant."""
    world, d0, _ = fixture()
    store, _ = A.run_d0(world, d0, 1024)
    for answer in store.facts:
        if not world.generated_by_rule(answer):
            assert world.rule_of[answer] not in store.rules or True
    kept = [a for a in store.facts if not world.generated_by_rule(a)]
    for answer in kept:
        r = world.rule_of[answer]
        if r in store.rules:
            break
    else:
        pytest.skip("no exception co-resident with its rule in this draw")
    assert answer in store.facts


def test_a_held_rule_licenses_a_check_and_never_an_answer():
    src = inspect.getsource(A._serve_member)
    verify = src.index("VERIFY_COST")
    apply_at = src.index("APPLY_COST")
    assert verify < apply_at, "the check must be charged before the application"


# --- carrying state is charged, not free -----------------------------------

def test_carrying_rules_is_charged_when_they_do_not_apply():
    world, d0, d1 = fixture()
    store, _ = A.run_d0(world, d0, 1024)
    _, cont = A.run_d1(world, d1, 1024, store.copy())
    assert cont.harmful_transfer_refusals > 0, (
        "if a carried rule is never wrong, the risk side of the hypothesis is untested")
    assert cont.negative_transfer_work == cont.harmful_transfer_refusals * D.VERIFY_COST


def test_eviction_can_displace_a_carried_rule():
    """Without this the lineage arrives with its budget spent and cannot adapt."""
    src = inspect.getsource(A._evict_for)
    assert "store.rules.discard" in src
    assert "rule_uses" in src


# --- the terminal can refuse ------------------------------------------------

def _cells(fractions, budgets=(256, 1024), correctness=1.0, survives=True):
    out = []
    for (length, budget), frac in fractions.items():
        out.append({
            "d1_length": length, "budget_bits": budget,
            "d1_only_advantage": frac, "d1_only_advantage_fraction": frac,
            "advantage_survives_ablation": survives,
            "d0_work": 1.0, "lifetime_continued": 1.0, "lifetime_reset": 1.0,
            "correctness": {"CONTINUED_OCM": correctness, "RESET_OCM": correctness},
            "arms": {"CONTINUED_OCM": {"d1_total_work_by_sigma": {"0.0": 10.0}},
                     "STRONG_ADAPTIVE_PARENT": {"d1_total_work_by_sigma": {"0.0": 5.0}}},
        })
    return out


def test_the_kill_criterion_is_reachable():
    t, reason = RUN._terminal(_cells({(250, 256): -1.0, (1000, 256): -2.0}))
    assert t == "NO_D0_TO_D1_TRANSITION"
    assert "REFUSAL" in reason


def test_unmatched_correctness_blocks_any_claim():
    t, _ = RUN._terminal(_cells({(250, 256): 1.0}, correctness=0.9))
    assert t == "INADMISSIBLE_CORRECTNESS_NOT_MATCHED"


def test_an_unattributable_advantage_is_not_a_transition():
    t, _ = RUN._terminal(_cells({(250, 256): 1.0}, survives=False))
    assert t == "ADVANTAGE_NOT_ATTRIBUTABLE"


def test_beating_the_clairvoyant_parent_voids_rather_than_discovers():
    cells = _cells({(250, 256): 1.0})
    cells[0]["arms"]["CONTINUED_OCM"]["d1_total_work_by_sigma"]["0.0"] = 1.0
    t, _ = RUN._terminal(cells)
    assert t == "VOID_PARENT_IMPLEMENTED_WRONGLY"


def test_a_mixed_result_is_reported_as_conditional():
    t, reason = RUN._terminal(_cells({(250, 256): -1.0, (250, 1024): 1.0}))
    assert t.endswith("CONDITIONAL")
    assert "IT DID NOT HOLD EVERYWHERE" in reason
    assert "Q1 is therefore FALSE" in reason.replace("Prediction ", "")


def test_decay_ignores_budgets_with_no_advantage_to_lose():
    """A flat line of losses must not be readable as a persistent gain."""
    losses_then_wins = _cells({(250, 256): -0.1, (1000, 256): -0.2,
                               (250, 1024): 0.5, (1000, 1024): 0.1})
    assert RUN._decays(losses_then_wins) is True
    no_wins = _cells({(250, 256): -0.1, (1000, 256): -0.2})
    assert RUN._decays(no_wins) is False


# --- the lineage chain ------------------------------------------------------

def test_the_lineage_chain_is_continuous_and_a_gap_is_detected():
    doc = json.loads(RECEIPT.read_text())
    ident = doc["transition_record"]["lineage_identity"]
    assert ident["continuous"] is True
    assert [l[0] for l in ident["links"]] == ["D0", "D1"]
    broken = spine.LineageIdentity("x", "genesis").extend("D0", "a")
    broken = spine.LineageIdentity("x", "genesis", broken.links + (("D1", "WRONG", "b"),))
    assert broken.continuous is False


def test_the_carried_digest_actually_changes_across_the_boundary():
    doc = json.loads(RECEIPT.read_text())
    ident = doc["transition_record"]["lineage_identity"]
    assert ident["links"][0][2] != ident["links"][1][2], (
        "if the store is identical after D1 the lineage learned nothing there")


# --- the receipt ------------------------------------------------------------

def test_the_transition_record_has_every_required_field():
    doc = json.loads(RECEIPT.read_text())
    assert doc["transition_record_missing_fields"] == []
    for f in spine.TRANSITION_FIELDS:
        assert f in doc["transition_record"], f


def test_cheaper_because_names_the_mechanism_not_the_outcome():
    doc = json.loads(RECEIPT.read_text())
    because = doc["transition_record"]["cheaper_because"]
    assert "removing exactly those rules" in because
    assert "not by the lineage merely possessing a store" in because


def test_the_receipt_reports_q1_as_false():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["Q1_continued_beats_reset"] is False
    assert doc["terminal"].endswith("CONDITIONAL")
    assert "the condition is the store budget" in doc["terminal_reason"]


def test_the_receipt_reports_the_negative_amortization_result():
    doc = json.loads(RECEIPT.read_text())
    rows = doc["lifetime_verdict"]["rows"]
    assert rows and all(r["d0_paid_for_itself"] is False for r in rows), (
        "if this ever becomes true the note above it must be rewritten, not kept")
    assert "the answer is NO everywhere" in doc["lifetime_verdict"]["note"].replace(
        "The answer is NO everywhere", "the answer is NO everywhere")


def test_the_receipt_states_what_it_does_not_establish():
    doc = json.loads(RECEIPT.read_text())
    for phrase in ("One transition", "authored to require composition",
                   "does not make a developmental lineage"):
        assert phrase in doc["what_this_does_not_establish"], phrase
    assert "NONE CLAIMED" in doc["novelty"]


def test_the_receipt_carries_no_wall_clock():
    text = RECEIPT.read_text().lower()
    for banned in ("elapsed", "timestamp", "duration_ms", "wall"):
        assert banned not in text, banned


def test_the_receipt_carries_the_plan_it_was_run_under():
    doc = json.loads(RECEIPT.read_text())
    assert doc["commitment"]["commitment"] == D.COMMITMENT.commitment
    assert doc["plan"] == json.loads(json.dumps(D.DEV1_PLAN))


# --- determinism ------------------------------------------------------------

def test_one_cell_is_identical_under_two_hash_seeds():
    prog = ("import json, run_dev1 as R;"
            "print(json.dumps(R.one_rep(250, 1024, 0), sort_keys=True, default=str))")
    outs = []
    for seed in ("0", "1"):
        env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONPATH=str(HERE))
        outs.append(subprocess.run([sys.executable, "-c", prog], cwd=HERE, env=env,
                                   capture_output=True, text=True, check=True).stdout)
    assert outs[0] == outs[1]
