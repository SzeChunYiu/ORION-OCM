"""Integrity tests for the negative-disposition ledger.

The failure mode this guards against is a programme that quietly relabels a
correct finding as a fixable defect so it can go on attacking it.
"""

from __future__ import annotations

import json
import pathlib

import pytest

import disposition as D

DOC = D.build()
HERE = pathlib.Path(__file__).parent


@pytest.mark.parametrize("n", D.NEGATIVES, ids=[n["negative_id"] for n in D.NEGATIVES])
def test_every_negative_is_fully_dispositioned(n):
    assert n["disposition"] in D.DISPOSITIONS
    assert n["fix_status"] in D.FIX_STATUS
    assert n["root"], n["negative_id"]
    assert len(n["why"]) > 60
    assert len(n["what_solved_would_mean"]) > 60
    assert n["preserved"] is True, "no negative may be withdrawn by a disposition"


@pytest.mark.parametrize("n", D.NEGATIVES, ids=[n["negative_id"] for n in D.NEGATIVES])
def test_a_correct_finding_is_not_given_a_fix(n):
    """The guard: a true result must not acquire a work item."""
    if n["disposition"] == "CORRECT_FINDING":
        assert n["fix_status"] in ("NONE_POSSIBLE", "NOT_STARTED")
        if n["fix_status"] == "NONE_POSSIBLE":
            assert "none" in n["fix"].lower()


@pytest.mark.parametrize("n", D.NEGATIVES, ids=[n["negative_id"] for n in D.NEGATIVES])
def test_a_correctable_negative_names_a_real_fix(n):
    if n["disposition"] == "CORRECTABLE":
        assert n["fix"], n["negative_id"]
        assert n["fix_status"] in ("RUNNING", "NOT_STARTED", "DONE")


@pytest.mark.parametrize("n", D.NEGATIVES, ids=[n["negative_id"] for n in D.NEGATIVES])
def test_a_superseded_negative_names_what_superseded_it(n):
    if n["disposition"] == "SUPERSEDED":
        assert n["fix_status"] == "DONE"
        assert n["fix"] and n["fix"] != "none"


def test_the_supplied_key_result_is_not_treated_as_solvable():
    """The single most important guard in this file."""
    n = next(x for x in D.NEGATIVES if x["negative_id"] == "N1-SUPPLIED-KEY-LOOKUP")
    assert n["disposition"] == "CORRECT_FINDING"
    assert n["fix_status"] == "NONE_POSSIBLE"
    assert "There is no version of this experiment" in n["what_solved_would_mean"]


def test_the_diagnosis_ordering_proof_is_not_treated_as_solvable():
    n = next(x for x in D.NEGATIVES if x["negative_id"] == "N8-DIAGNOSIS-RESIDUAL")
    assert n["disposition"] == "CORRECT_FINDING"
    assert "proof, not a measurement" in n["why"]


def test_counts_are_arithmetic_not_assertion():
    c = DOC["counts_by_disposition"]
    assert sum(c.values()) == len(D.NEGATIVES)
    assert DOC["solvable"] == c.get("CORRECTABLE", 0)
    assert DOC["not_solvable"] == c.get("CORRECT_FINDING", 0) + c.get("NARROW", 0)


def test_every_root_in_the_ledger_exists_in_the_root_cause_analysis():
    import root_cause as RC
    for n in D.NEGATIVES:
        assert n["root"] in RC.ROOTS, n["negative_id"]


def test_generated_artifact_matches_the_source():
    assert json.loads((HERE / "NEGATIVE_DISPOSITION_V1.json").read_text()) == DOC


def test_not_everything_is_correctable():
    """If this ever fails, the ledger has become an excuse generator."""
    c = DOC["counts_by_disposition"]
    assert c.get("CORRECT_FINDING", 0) + c.get("NARROW", 0) >= 2
