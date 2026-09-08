"""Integrity tests for the recursive root-cause analysis.

The analysis reinterprets evidence, which is exactly the operation most likely to
quietly launder a negative into an excuse. These tests exist to make that hard.
"""

from __future__ import annotations

import json
import pathlib

import pytest

import root_cause as RC

DOC = RC.build()
HERE = pathlib.Path(__file__).parent


@pytest.mark.parametrize("o", RC.OBSERVATIONS, ids=[o["observation_id"] for o in RC.OBSERVATIONS])
def test_every_observation_cites_a_source_and_terminates(o):
    assert o["source"], o["observation_id"]
    assert len(o["why"]) >= 3, "a chain of fewer than three steps is not a recursion"
    assert o["terminates_at"] in RC.ROOTS
    assert o["preserved"] is True, "no negative may be withdrawn by this analysis"


def test_a_root_needs_two_independent_chains():
    for name, r in DOC["first_order_roots"].items():
        if r["chains_supporting"] < 2:
            assert r["status"] == "CONJECTURE_SINGLE_CHAIN", name
        else:
            assert r["status"] == "ROOT", name


def test_every_root_has_a_falsifier():
    for name, r in DOC["first_order_roots"].items():
        assert len(r["falsifier"]) > 40, name
    for name, r in DOC["deep_roots"].items():
        assert len(r["falsifier"]) > 40, name


def test_deep_roots_subsume_only_declared_first_order_roots():
    for name, r in DOC["deep_roots"].items():
        for s in r["subsumes"]:
            assert s in DOC["first_order_roots"], (name, s)


def test_the_deep_root_states_what_it_does_not_excuse():
    """An explanation that excuses everything explains nothing."""
    for name, r in DOC["deep_roots"].items():
        assert len(r["what_it_does_not_excuse"]) > 60, name
    eco = DOC["deep_roots"]["ECOLOGY_HAS_NO_ACCUMULATION_STRUCTURE"]
    assert "does not rehabilitate" in eco["what_it_does_not_excuse"]


def test_the_decisive_experiment_cannot_be_rigged_by_choosing_rho():
    d = DOC["decisive_experiment"]
    assert "rho = 0 is in the sweep" in d["anti_rigging_controls"]
    assert "REPRODUCE the existing negatives" in d["anti_rigging_controls"]
    assert "every parent runs at every rho" in d["anti_rigging_controls"]
    assert "never a single favourable rho" in d["anti_rigging_controls"]


def test_essential_requirement_is_certified_not_assumed():
    d = DOC["decisive_experiment"]
    assert "strictly increase the minimal solution cost" in d["essential_requirement"]


def test_the_analysis_claims_unmeasurable_not_refuted():
    """The distinction the whole analysis turns on, asserted rather than trusted."""
    eco = DOC["deep_roots"]["ECOLOGY_HAS_NO_ACCUMULATION_STRUCTURE"]
    assert "UNMEASURABLE rather than refuted" in eco["consequence"]
    assert "without withdrawing any of them" in eco["consequence"]


def test_generated_artifact_matches_the_source():
    assert json.loads((HERE / "ROOT_CAUSE_ANALYSIS_V1.json").read_text()) == DOC


def test_no_root_claims_more_chains_than_exist():
    total = sum(r["chains_supporting"] for r in DOC["first_order_roots"].values())
    assert total == len(RC.OBSERVATIONS)
