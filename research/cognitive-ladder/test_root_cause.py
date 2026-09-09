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


def test_deep_root_chain_counts_are_derived_not_asserted():
    """A hand-typed count is the easiest place to inflate an explanation's support."""
    counts = {k: v["chains_supporting"] for k, v in DOC["first_order_roots"].items()}
    for name, r in DOC["deep_roots"].items():
        assert r["chains_supporting"] == sum(counts[s] for s in r["subsumes"]), name
    assert "chains_supporting" not in RC.DEEP_ROOTS["COMPARISON_WAS_CONSTRUCTED_FROM_THE_ARM"], (
        "deep roots must not carry a literal count in the source")


def test_the_headline_count_tracks_the_observations():
    eco = DOC["deep_roots"]["ECOLOGY_HAS_NO_ACCUMULATION_STRUCTURE"]
    assert DOC["headline"].startswith(f"{eco['chains_supporting']} of {len(RC.OBSERVATIONS)} ")


def test_a_fired_falsifier_is_recorded_where_it_fired():
    """A root whose falsifier has been run may not keep presenting it as untested."""
    fired = {"PARENT_SHARES_THE_MECHANISM_UNDER_TEST": DOC["first_order_roots"],
             "COMPARISON_WAS_CONSTRUCTED_FROM_THE_ARM": DOC["deep_roots"]}
    for name, table in fired.items():
        status = table[name].get("falsifier_status", "")
        assert status.startswith("HALF_FIRED"), name
        assert "INDEP_E8_V1.json" in status or "E8" in status, name
        assert "N12" in status, f"{name} must say where the root still stands"


def test_a_superseding_observation_names_what_it_supersedes():
    ids = {o["observation_id"] for o in RC.OBSERVATIONS}
    for o in RC.OBSERVATIONS:
        if "supersedes" in o:
            assert o["supersedes"] in ids, o["observation_id"]
            assert o["observation_id"] != o["supersedes"]
    superseded = {o["supersedes"] for o in RC.OBSERVATIONS if "supersedes" in o}
    for o in RC.OBSERVATIONS:
        if o["observation_id"] in superseded:
            assert o["preserved"] is True, "superseding may not withdraw the original"


def test_the_eager_acquisition_root_records_that_its_falsifier_fired():
    """The programme's central negative explanation is now scoped; it must say so."""
    root = DOC["deep_roots"]["EAGER_ACQUISITION_IS_DOMINATED_BY_DEFERRED_ACQUISITION"]
    status = root["falsifier_status"]
    assert status.startswith("FIRED, AND THE ROOT IS NARROWED")
    assert "RETAIN_E10_V1.json" in status
    assert "scoped, not refuted" in status
    second = root["falsifier_status_second_half"]
    assert second.startswith("FIRED AGAINST THE MACHINE"), (
        "the second half of the falsifier went against the machine and must say so first")
    assert "PERISH_E12_V1.json" in second
    assert "narrowed on BOTH sides" in second
    assert "scoped, not withdrawn" in second


def test_every_recorded_falsifier_status_reaches_the_generated_document():
    md = (HERE / "ROOT_CAUSE_ANALYSIS_V1.md").read_text()
    for table in (RC.ROOTS, RC.DEEP_ROOTS):
        for name, r in table.items():
            for field in ("falsifier_status", "falsifier_status_second_half"):
                if r.get(field):
                    assert r[field] in md, (name, field)
