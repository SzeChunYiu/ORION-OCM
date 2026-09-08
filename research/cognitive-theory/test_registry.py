"""Tests for the theory registry.

These are integrity tests, not science: they check that no row can quietly lose
its falsifier, its rung, or its evidence, because a registry row without those is
an opinion.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from registry_data import ROUTES, STATUS, THEORIES

HERE = pathlib.Path(__file__).parent


@pytest.mark.parametrize("t", THEORIES, ids=[t["theory_id"] for t in THEORIES])
def test_every_row_is_falsifiable_and_bound_to_a_rung(t):
    assert t["falsifier"], "a row with no falsifier is an opinion"
    assert t["empirical_rung"], "a row that no rung can kill is not a theory row"
    assert t["verification_route"] in ROUTES
    assert t["status"] in STATUS


@pytest.mark.parametrize("t", THEORIES, ids=[t["theory_id"] for t in THEORIES])
def test_a_settled_row_cites_its_evidence(t):
    if t["status"] in ("OPEN", "NOT_YET_TESTABLE"):
        return
    assert t["evidence"], f"{t['theory_id']} is settled but cites nothing"
    assert len(t["evidence"]) > 40, "evidence must say what was measured, not just name a file"


@pytest.mark.parametrize("t", THEORIES, ids=[t["theory_id"] for t in THEORIES])
def test_a_refuted_row_names_its_successor_or_says_it_is_closed(t):
    if t["status"] != "REFUTED":
        return
    assert t["reopen_condition"], "a refuted row must say what would reopen it, or that nothing will"


def test_every_row_names_a_strongest_parent():
    for t in THEORIES:
        assert t["strongest_parent"], t["theory_id"]


def test_theory_ids_are_unique():
    ids = [t["theory_id"] for t in THEORIES]
    assert len(ids) == len(set(ids))


def test_generated_artifacts_match_the_source():
    """CI regenerates these; a hand-edited registry must fail source custody."""
    import registry
    data = json.loads((HERE / "THEORY_EMPIRICAL_REGISTRY_V1.json").read_text())
    assert data["row_count"] == len(THEORIES)
    assert data == registry.build_json()
    assert (HERE / "THEORY_EMPIRICAL_REGISTRY_V1.md").read_text() == registry.build_md()


def test_the_registry_leads_with_what_was_killed():
    """The programme's own discipline, asserted rather than trusted."""
    settled = [t for t in THEORIES if t["status"] not in ("OPEN", "NOT_YET_TESTABLE")]
    killed = [t for t in settled if t["status"] in ("REFUTED", "PARENT_SUFFICIENT", "PARENT_OWNED")]
    assert len(killed) > len(settled) - len(killed), (
        "more settled rows survive than were killed; check that negatives are being recorded"
    )
