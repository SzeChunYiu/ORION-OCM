"""Tests for the #149 incident intake binding.

These are integrity tests. Their job is to make it impossible to hand another
lane a number that is not backed by a receipt, because that is precisely what
#149 warns against.
"""

from __future__ import annotations

import hashlib
import json
import pathlib

import pytest

import incident_intake as II

DOC = II.build()
BINDINGS = DOC["bindings"]
SUPPLIED = {k: v for k, v in BINDINGS.items()
            if str(v["status"]).startswith("EXECUTABLE_INTAKE_SUPPLIED")}


@pytest.mark.parametrize("fid", sorted(SUPPLIED))
def test_a_supplied_incident_is_backed_by_a_receipt_that_exists(fid):
    b = SUPPLIED[fid]
    path = pathlib.Path(II.HERE.parent.parent) / b["receipt"]
    assert path.is_file(), f"{fid} names a receipt that does not exist"
    assert b["receipt_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("fid", sorted(SUPPLIED))
def test_a_supplied_incident_says_what_it_does_not_certify(fid):
    """Supplying a trace is not certifying a diagnosis, and must not read as one."""
    assert len(SUPPLIED[fid]["does_not_certify"]) > 60


@pytest.mark.parametrize("fid", sorted(SUPPLIED))
def test_a_supplied_incident_is_reproducible_by_a_named_command(fid):
    assert SUPPLIED[fid]["reproduce"].startswith("python run_")


def test_numbers_are_read_from_receipts_not_typed_into_the_module():
    """The F6 drop must equal what the receipt says, not what anyone remembers."""
    receipt = json.loads((II.RESULTS / "ESCALATION_INDEPENDENT_E4_V1.json").read_text())
    assert BINDINGS["F6"]["accuracy_drop"] == receipt["generator_artifact_verdict"]["accuracy_drop"]
    assert BINDINGS["F6"]["independent_accuracy"] == (
        receipt["generator_artifact_verdict"]["independent_accuracy"])


def test_f2_and_f3_declare_their_shared_receipt():
    """#149 is right that these are not two independent observations."""
    assert BINDINGS["F2"]["receipt"] == BINDINGS["F3"]["receipt"]
    assert BINDINGS["F3"]["shared_receipt_with"] == "F2"
    assert "not two independent observations" in BINDINGS["F3"]["shared_receipt_note"]


def test_f1_is_not_claimed_by_this_lane():
    """The cancelled experiment must not leave a phantom binding behind."""
    assert BINDINGS["F1"]["status"] == "NOT_SUPPLIED_BY_THIS_LANE"
    assert "receipt" not in BINDINGS["F1"]
    assert BINDINGS["F1"]["why_not_supplied"]


def test_f1_records_the_bottleneck_moving_from_discovery_to_opportunity():
    note = BINDINGS["F1"]["what_the_clause_revival_changes"]
    assert "tautolog" in note.lower(), "the opportunity finding must be carried forward"


def test_the_two_incidents_149_lists_as_lacking_intake_carry_an_explicit_correction():
    for fid in ("F5", "F6"):
        assert BINDINGS[fid].get("supersedes_149_note"), fid


def test_generated_artifacts_match_the_source():
    doc = json.loads((II.HERE / "INCIDENT_INTAKE_V1.json").read_text())
    assert doc == DOC


def test_supplied_count_is_honest():
    assert DOC["incidents_supplied"] == len(SUPPLIED)
    assert DOC["incidents_supplied"] < DOC["incidents_total"], (
        "if this ever equals the total, check that F1 was genuinely earned and not assumed"
    )
