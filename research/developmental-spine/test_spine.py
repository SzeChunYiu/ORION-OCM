"""Tests for the developmental spine.

The failure mode guarded against here is a spine that reports transitions as
complete because the fields have names rather than because evidence exists.
"""

from __future__ import annotations

import json
import pathlib

import pytest

import spine

DOC = spine.build()
HERE = pathlib.Path(__file__).parent


def test_lineage_detects_a_break():
    """A swapped machine must not pass as the same lineage."""
    lin = spine.LineageIdentity("L", "g0").extend("D0", "d1").extend("D1", "d2")
    assert lin.continuous
    broken = spine.LineageIdentity("L", "g0", (("D0", "g0", "d1"), ("D1", "WRONG", "d2")))
    assert not broken.continuous


def test_lineage_chain_digest_changes_when_history_changes():
    a = spine.LineageIdentity("L", "g0").extend("D0", "d1")
    b = spine.LineageIdentity("L", "g0").extend("D0", "d1").extend("D1", "d2")
    assert a.chain_digest() != b.chain_digest()


def test_every_transition_requires_all_four_arms():
    for t in DOC["transitions"]:
        if t["complete"]:
            assert not t["arms_missing"]


def test_the_reset_arm_is_required_everywhere():
    """Without it, cheaper cannot be distinguished from easier."""
    assert "RESET_OCM" in spine.REQUIRED_ARMS
    for t in DOC["transitions"]:
        assert "RESET_OCM" in t["arms_missing"] or "RESET_OCM" in t["arms_present"]


def test_no_transition_is_reported_complete_without_evidence():
    """The load-bearing test: naming a field is not having measured it."""
    for t in DOC["transitions"]:
        if t["complete"]:
            assert t["supporting_receipts"], (
                f"{t['source_stage']}->{t['target_stage']} claims complete with no receipts"
            )


def test_exactly_the_measured_transitions_are_complete_and_the_rest_say_why():
    """This assertion used to read ``== 0`` and it was the honest answer then.

    DEV-1 supplied the D0-to-D1 transition, so it reads 1 now. Five remain, and
    the test still requires each of those to name what blocks it -- which is the
    part that was doing the work all along. It also requires that the one
    complete transition is the one that was actually measured, so that a future
    receipt cannot quietly mark a transition complete without a transition
    receipt behind it.
    """
    complete = [(t["source_stage"], t["target_stage"]) for t in DOC["transitions"]
                if t["complete"]]
    assert complete == [("D0", "D1")]
    assert DOC["complete_transitions"] == 1
    for t in DOC["transitions"]:
        if not t["complete"]:
            assert t["blocking_reason"], "an incomplete transition must say what blocks it"


def test_a_complete_transition_is_backed_by_a_transition_receipt():
    """Stage receipts can never complete a transition, however many there are."""
    for t in DOC["transitions"]:
        if not t["complete"]:
            continue
        backing = [n for n in t["supporting_receipts"]
                   if "transition" in spine.EVIDENCE_MAP[n]]
        assert backing, (t["source_stage"], t["target_stage"])
        for n in backing:
            assert tuple(spine.EVIDENCE_MAP[n]["transition"]) == (
                t["source_stage"], t["target_stage"])


def test_causal_attribution_is_a_required_field():
    """#151 section 3's decisive question must be answerable from the receipt."""
    assert "cheaper_because" in spine.TRANSITION_FIELDS
    assert "cheaper_because" in DOC["field_added_beyond_151"]


@pytest.mark.parametrize("name", sorted(spine.EVIDENCE_MAP))
def test_every_mapped_receipt_exists_and_supplies_named_fields(name):
    assert spine._receipt(name) is not None, f"{name} is mapped but does not exist"
    for f in spine.EVIDENCE_MAP[name]["supplies"]:
        assert f in spine.TRANSITION_FIELDS, (name, f)


@pytest.mark.parametrize("name", sorted(spine.EVIDENCE_MAP))
def test_every_mapped_receipt_states_its_limitation(name):
    assert len(spine.EVIDENCE_MAP[name]["note"]) > 50


def test_identity_and_reuse_fields_are_never_claimed_by_stage_receipts():
    """These exist only if a machine crossed a boundary carrying state."""
    supplied = set()
    for m in spine.EVIDENCE_MAP.values():
        if "transition" in m:
            continue   # a transition receipt is exactly the thing that may claim these
        supplied.update(m["supplies"])
    for f in ("reuse_execution_witnesses", "reused_object_identities",
              "source_machine_identity", "target_machine_identity", "cheaper_because"):
        assert f not in supplied, f"{f} cannot be supplied by a single-stage receipt"


def test_generated_artifact_matches_the_source():
    assert json.loads((HERE / "DEVELOPMENTAL_SPINE_V1.json").read_text()) == DOC


def test_complete_is_never_presented_as_a_score():
    """#151 section 6's failure mode: a count of completions read as a win rate."""
    assert "complete_does_not_mean_succeeded" in DOC
    note = DOC["complete_does_not_mean_succeeded"]
    assert "never 'succeeded'" in note or "never alone" in note
    assert "CONDITIONAL" in DOC["headline"], (
        "the headline must carry the one measured transition's actual terminal")


def test_the_complete_transition_records_that_a_parent_beat_it():
    """A spine that counts a transition complete must not hide that it lost."""
    assert "the_one_complete_transition_lost_to_a_parent" in DOC
    note = DOC["the_one_complete_transition_lost_to_a_parent"]
    assert "PARENT_SUFFICIENT" in note
    assert "opposite shape" in note
    assert "DEV-1's comparison against RESET_OCM stands" in note
    entry = spine.EVIDENCE_MAP["DEV1_D0_TO_D1_V1.json"]["note"]
    assert "SUPERSEDED ON THE CARRY CLAIM" in entry


def test_the_recovery_is_recorded_with_its_condition_not_as_a_clean_win():
    note = DOC["the_one_complete_transition_lost_to_a_parent"]
    assert "RECOVERED by DEV3_GUARDED_RULES_V1" in note
    assert "conditional on a representation with no use tax" in note
    assert "The control holds" in note
    assert "PARENT_SUFFICIENT" in note, (
        "the loss that preceded the recovery must stay in the same sentence")
