"""Assurance needs measured, ordered evidence for every declared obligation."""
from dataclasses import replace

import pytest

from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.selfmodel import govern as GV
from ocm.selfmodel import proposal as PR
from ocm.store.evidence import Channel


def proposal():
    return PR.SelfChangeProposal(
        "p", "1", (), "operator.x", "D2", "inc", PR.ChangeClass.C2_OPERATOR,
        {"replace": "v2"}, lambda a: {**a, "op": "v2"},
        PR.Prediction(("target",), (), {}, ("preservation",), (), (), 0.1),
        ("preservation",), (), "target", "restore", "scope", "window", PR.Origin.HUMAN,
    )


def setup(root):
    rt = OCMRuntime(root)
    p = proposal()
    receipt = GV.register_prediction(rt, p)
    runner = lambda art, tasks: {"success": len(tasks) if art["op"] == "v2" else 0,
                                 "n": len(tasks), "resources": {"steps": len(tasks)}}
    shadow = GV.shadow_evaluate(rt, {"op": "v1"}, p, runner, {"target": [1], "preservation": [2]})
    return rt, p, receipt, shadow


def assure(rt, p, receipt, shadow):
    return GV.assure(p, shadow, protocol_hash="h", frozen_protocol_hash="h",
                     budget={"steps": 3}, rollback_exists=True,
                     prediction_receipt=receipt, runtime=rt)


@pytest.mark.parametrize("side,family", [("incumbent", "target"), ("challenger", "target"),
                                         ("incumbent", "preservation"), ("challenger", "preservation")])
def test_missing_required_suite_never_passes_or_raises(tmp_path, side, family):
    rt, p, receipt, shadow = setup(tmp_path)
    data = dict(getattr(shadow, side))
    del data[family]
    result = assure(rt, p, receipt, replace(shadow, **{side: data}))
    assert not result.passed and "required_suites_measured" in result.reasons


@pytest.mark.parametrize("row", [
    None,
    "unmeasured",
    {"success": 1, "n": 1, "resources": {}},
    {"success": 1, "n": 0, "resources": {"steps": 1}},
    {"success": True, "n": 1, "resources": {"steps": 1}},
    {"success": 2, "n": 1, "resources": {"steps": 1}},
    {"success": 1, "n": 1, "resources": {"steps": -1}},
    {"success": 1, "n": 1, "resources": {"steps": 10 ** 1000}},
    {"success": 1, "n": 2, "resources": {"steps": 1}},
])
def test_missing_or_invalid_measurement_never_passes(tmp_path, row):
    rt, p, receipt, shadow = setup(tmp_path)
    challenger = {**shadow.challenger, "target": row}
    assert not assure(rt, p, receipt, replace(shadow, challenger=challenger)).passed


def test_late_receipt_cannot_claim_an_earlier_event_index(tmp_path):
    rt, p, _, shadow = setup(tmp_path)
    late = replace(p, proposal_id="late")
    late_receipt = GV.register_prediction(rt, late)
    forged = replace(late_receipt, event_index=0)
    result = assure(rt, late, forged, shadow)
    assert not result.passed and "no_leakage" in result.reasons


def test_revoked_prediction_receipt_is_not_live_assurance(tmp_path):
    rt, p, receipt, shadow = setup(tmp_path)
    rt.revoke([receipt.evidence_id])
    result = assure(rt, p, receipt, shadow)
    assert not result.passed and "no_leakage" in result.reasons


def test_valid_receipt_and_measurements_survive_restart(tmp_path):
    rt, p, receipt, shadow = setup(tmp_path)
    assert assure(OCMRuntime(tmp_path), p, receipt, shadow).passed


def test_shadow_runner_cannot_mutate_incumbent_or_other_arm_tasks(tmp_path):
    rt = OCMRuntime(tmp_path)
    incumbent = {"op": "v1", "nested": [1]}
    suites = {"target": [1, 2], "preservation": [3, 4]}
    seen = []

    def runner(artifact, tasks):
        seen.append((artifact["op"], tuple(tasks), tuple(artifact["nested"])))
        artifact["nested"].append(99)
        tasks.clear()
        return {"success": 0, "n": 2, "resources": {"steps": 2}}

    GV.shadow_evaluate(rt, incumbent, proposal(), runner, suites)
    assert incumbent == {"op": "v1", "nested": [1]}
    assert suites == {"target": [1, 2], "preservation": [3, 4]}
    assert seen == [("v1", (1, 2), (1,)), ("v1", (3, 4), (1,)),
                    ("v2", (1, 2), (1,)), ("v2", (3, 4), (1,))]


@pytest.mark.parametrize("field,value", [("scope", "other"), ("expiry", "other"),
    ("preserved_capabilities", ()), ("dev_tasks", ("protected-task",)),
    ("rollback_plan", "different"), ("target_layer", "D7")])
def test_external_decision_binds_complete_declarative_proposal(field, value):
    p = proposal()
    assert replace(p, **{field: value}).fingerprint() != p.fingerprint()
