"""Integrity tests for the absorption register and the phase-boundary conjecture.

A post-hoc law that reproduces its own training data is the single most seductive
artifact this programme could produce, so these tests are aimed at it: the rule
must have no free parameters, the in-sample agreement must be labelled as
worthless, the out-of-sample prediction must be frozen before the experiment
exists, and every absorption must cite a receipt that is actually on disk.
"""

from __future__ import annotations

import inspect
import json
import pathlib

import pytest

import synthesis as S

HERE = pathlib.Path(__file__).parent
DOC = S.build()


# --- absorption -------------------------------------------------------------

@pytest.mark.parametrize("a", S.ABSORPTIONS, ids=[a["parent"][:24] for a in S.ABSORPTIONS])
def test_every_absorption_is_complete(a):
    assert a["verdict"] in S.VERDICTS, a["parent"]
    for field in ("teaches", "novelty_removed", "mapped_to",
                  "prior_information_charged", "next_experiment"):
        assert a[field], (a["parent"], field)


@pytest.mark.parametrize("a", S.ABSORPTIONS, ids=[a["parent"][:24] for a in S.ABSORPTIONS])
def test_every_absorption_cites_a_receipt_that_exists(a):
    for ref in a["receipt"].split(","):
        ref = ref.strip()
        if ref.startswith("../") or "..." in ref:
            continue   # cross-lane references are checked by the spine, not here
        assert (HERE / ref).is_file(), (a["parent"], ref)


def test_an_absorption_names_what_novelty_it_removes():
    """The doctrine's whole point: a parent kills a claim and strengthens the machine."""
    for a in S.ABSORPTIONS:
        assert a["novelty_removed"].strip().lower().startswith(("any claim", "whether")), (
            a["parent"], "novelty_removed must name the claim being given up")


def test_the_open_verdict_says_what_is_missing():
    for a in S.ABSORPTIONS:
        if a["verdict"] == "OPEN":
            assert "not been run" in a["next_experiment"] or "hole" in a["next_experiment"], (
                a["parent"])


# --- the rule has nowhere to hide -------------------------------------------

def test_the_rule_has_no_free_parameters():
    src = inspect.getsource(S.predict)
    code = src.split('"""')[-1]          # the body, not the prose about the body
    assert "0." not in code, "a rule with a knob fits anything"
    assert "weight" not in code.lower()
    body = [l for l in code.splitlines() if l.strip().startswith("return")]
    assert len(body) == 1


def test_the_rule_is_a_conjunction_and_can_therefore_be_wrong():
    from synthesis import Coordinates as C
    assert S.predict(C(True, True, True)) == "MACHINE"
    for combo in ((False, True, True), (True, False, True), (True, True, False),
                  (False, False, False)):
        assert S.predict(C(*combo)) == "PARENT_SUFFICIENT", combo


def test_in_sample_agreement_is_labelled_as_worthless():
    assert DOC["in_sample_agreement"] == 1.0
    note = DOC["in_sample_is_not_evidence"]
    assert "not about the world" in note
    assert "CONJECTURE, FITTED POST HOC" in DOC["law_status"]


def test_the_row_most_at_risk_of_being_scored_to_fit_is_flagged():
    risky = [r for r in S.OBSERVED if "at risk of being scored to fit" in r["note"]]
    assert len(risky) == 1, "the DEV-1 tight-budget row must carry its own warning"
    assert risky[0]["beta"] is False
    assert "interval reading" in risky[0]["note"]


def test_beta_is_documented_as_an_interval_not_a_threshold():
    assert "NOT a threshold" in S.CONDITIONS["beta"]["measurable_as"]
    assert "upper edge" in S.CONDITIONS["beta"]["measurable_as"]


def test_every_condition_names_the_experiment_that_isolated_it():
    for key, c in S.CONDITIONS.items():
        assert "results/" in c["isolated_by"] or "E" in c["isolated_by"], key
        assert c["absent_reproduces"], key
        assert c["measurable_as"], key


# --- the out-of-sample prediction -------------------------------------------

def test_the_prediction_is_frozen_in_the_commitment():
    assert S.OUT_OF_SAMPLE in S.PLAN.values() or S.PLAN["out_of_sample"] is S.OUT_OF_SAMPLE
    assert S.COMMITMENT.commitment == S.commit(S.PLAN).commitment
    assert S.OUT_OF_SAMPLE["predicted_before_the_experiment_exists"] is True


def test_the_prediction_follows_from_the_rule_and_not_from_taste():
    from synthesis import Coordinates as C
    c = S.OUT_OF_SAMPLE["coordinates"]
    assert S.predict(C(c["rho"], c["beta"], c["phi"])) == S.OUT_OF_SAMPLE["predicted"]


def test_the_prediction_names_what_would_refute_the_law():
    o = S.OUT_OF_SAMPLE
    assert "PARENT_SUFFICIENT" in o["what_refutes_the_law"]
    assert "caching result with an inflated name" in o["what_refutes_the_law"]
    assert "one out-of-sample point, not a validated law" in o["what_confirms_it_weakly"]


def test_the_load_bearing_move_is_declared_rather_than_assumed():
    """beta must mean scarcity of the economized resource, or the law is about caches."""
    j = S.OUT_OF_SAMPLE["coordinate_justification"]
    assert "unbounded" in j
    assert "statement about caches" in j


def test_changing_the_prediction_changes_the_commitment():
    import copy
    altered = copy.deepcopy(dict(S.PLAN))
    altered["out_of_sample"] = dict(S.OUT_OF_SAMPLE, predicted="PARENT_SUFFICIENT")
    assert S.commit(altered).commitment != S.COMMITMENT.commitment


# --- the generated artifact -------------------------------------------------

def test_generated_artifact_matches_the_source():
    assert json.loads((HERE / "SYNTHESIS_V1.json").read_text()) == DOC


def test_the_document_prints_the_disagreements_if_any():
    md = (HERE / "SYNTHESIS_V1.md").read_text()
    for r in DOC["in_sample"]:
        if not r["agrees"]:
            assert "| NO |" in md


def test_the_artifact_produces_no_evidence_and_says_so():
    assert "produces no evidence" in DOC["authority"]
    assert "stands unchanged" in DOC["authority"]
    assert "falsifiable, which is its only current virtue" in DOC["what_this_does_not_establish"]


def test_recording_the_outcome_did_not_rewrite_the_prediction():
    """The frozen text is inside the digest; the outcome must live outside it."""
    assert S.COMMITMENT.commitment == S.commit(S.PLAN).commitment
    assert "OUT_OF_SAMPLE_RESULT" not in json.dumps(S.PLAN)
    assert "SURVIVED" not in S.LAW_STATUS, (
        "LAW_STATUS is inside PLAN and must stay as it was written")
    assert "law_status_after_the_test" in DOC
    assert DOC["law_status_after_the_test"].startswith("CONJECTURE WITH ONE SURVIVING")


def test_the_outcome_records_the_correction_the_run_forced():
    r = DOC["out_of_sample_result"]
    assert r["verdict"] == "SURVIVED_ONE_TEST"
    assert "That is false" in r["the_correction_it_forced"]
    assert "artifact of compression" in r["the_correction_it_forced"]
    assert "One out-of-sample point" in r["how_much_this_is_worth"]


def test_the_adverse_finding_is_carried_in_the_summary_not_only_the_receipt():
    r = DOC["out_of_sample_result"]["adverse_finding_in_the_same_run"]
    assert "AGAINST the" in r
    assert "eager_all_rules_parent" in r
    assert "itself a cost once waiting is charged" in r


def test_a_later_parent_can_revise_a_row_without_rewriting_the_frozen_table():
    assert S.COMMITMENT.commitment == S.commit(S.PLAN).commitment
    assert "OBSERVED_REVISIONS" not in json.dumps(S.PLAN)
    frozen = {r["study"]: r["observed"] for r in S.OBSERVED}
    revised = {r["study"]: r["observed"] for r in DOC["in_sample_after_revision"]}
    changed = [k for k in frozen if frozen[k] != revised[k]]
    assert changed == ["DEV-1 D0 to D1, 1024 bits"]
    assert frozen["DEV-1 D0 to D1, 1024 bits"] == "MACHINE"


def test_the_revised_agreement_is_reported_and_is_below_the_fitted_one():
    assert DOC["in_sample_agreement"] == 1.0
    assert DOC["in_sample_agreement_after_revision"] < 1.0
    md = (HERE / "SYNTHESIS_V1.md").read_text()
    assert "In-sample agreement falls from 100% to 90%" in md


def test_every_revision_names_the_receipt_that_forced_it():
    for r in S.OBSERVED_REVISIONS:
        assert "results/" in r["forced_by"], r["study"]
        assert r["why"] and r["consequence"]
        assert r["study"] in {o["study"] for o in S.OBSERVED}


def test_the_missing_quantity_is_a_candidate_and_not_a_coordinate():
    from synthesis import Coordinates as C
    import inspect
    assert "use" in S.CANDIDATE_MISSING_QUANTITY.lower()
    assert "deliberately NOT added" in S.CANDIDATE_MISSING_QUANTITY or \
        "would mean nothing" in S.CANDIDATE_MISSING_QUANTITY
    params = list(inspect.signature(S.predict).parameters)
    assert params == ["c"]
    assert set(C.__dataclass_fields__) == {"rho", "beta", "phi"}, (
        "the rule must still have exactly three coordinates")


def test_the_continual_learning_absorption_is_no_longer_open():
    entry = [a for a in S.ABSORPTIONS if a["field"] == "continual learning"]
    assert len(entry) == 1
    assert entry[0]["verdict"] == "ADOPT"
    assert "BEATS the lineage" in entry[0]["teaches"]
    assert "withdrawn" in entry[0]["novelty_removed"]
    assert DOC["verdict_counts"]["OPEN"] == 0


def test_acting_on_the_candidate_did_not_turn_it_into_a_coordinate():
    from synthesis import Coordinates as C
    f = DOC["candidate_follow_up"]
    assert f["verdict"].startswith("THE CANDIDATE WAS RIGHT")
    assert "STAYS mispredicted" in f["why_it_is_still_not_a_fourth_coordinate"]
    assert set(C.__dataclass_fields__) == {"rho", "beta", "phi"}
    assert DOC["in_sample_agreement_after_revision"] < 1.0, (
        "the row the candidate explains must remain a recorded failure")


def test_the_follow_up_states_the_new_falsifier():
    f = DOC["candidate_follow_up"]
    assert "the law is wrong rather than incomplete" in f["why_it_is_still_not_a_fourth_coordinate"]
    assert "no representation without a use tax exists" in \
        f["why_it_is_still_not_a_fourth_coordinate"].lower()
