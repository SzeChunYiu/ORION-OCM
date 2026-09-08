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


def test_the_current_answer_is_zero_and_says_why():
    assert DOC["complete_transitions"] == 0
    for t in DOC["transitions"]:
        assert t["blocking_reason"], "an incomplete transition must say what blocks it"


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
        supplied.update(m["supplies"])
    for f in ("reuse_execution_witnesses", "reused_object_identities",
              "source_machine_identity", "target_machine_identity", "cheaper_because"):
        assert f not in supplied, f"{f} cannot be supplied by a single-stage receipt"


def test_generated_artifact_matches_the_source():
    assert json.loads((HERE / "DEVELOPMENTAL_SPINE_V1.json").read_text()) == DOC
