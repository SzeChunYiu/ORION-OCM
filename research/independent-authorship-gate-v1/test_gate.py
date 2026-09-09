#!/usr/bin/env python3
"""Local controls for the independent-authorship gate. Not a publication result."""
from __future__ import annotations

from policy import PolicyViolation, label_truth, refuse_generator_intent_as_cause
from recover_mex1 import compare_to_planted, load_mex1, recover_world


def test_policy_refuses_planted_cause():
    try:
        refuse_generator_intent_as_cause({
            "target": "cause",
            "source": "GENERATOR_INTENT",
            "truth": {"planted_family": "X1-B_MEASUREMENT_CALIBRATION"},
        })
    except PolicyViolation:
        return
    raise AssertionError("planted cause must fail closed")


def test_e3_requires_independent_authorship():
    lab = label_truth(target="decision", recovered=None, planted={"family": "X"}, independently_authored=False, evidence_class="E3")
    assert lab["source"] == "CANNOT_CHECK"


def test_mex1_recovery_ignores_family_and_can_disagree():
    gen, model, oracle = load_mex1()
    inst, exp = gen.generate_instance("dev", "ME-X1-DEV-20260902", model.FAMILIES[1], 1)  # B NEGATIVE
    recovered = recover_world(model, oracle, inst.world_v0, inst.events, inst.request)
    assert recovered["status"] == "RECOVERED"
    assert recovered["truth"]["action"] == exp.action
    assert "planted_family" not in recovered["truth"]
    labelled = label_truth(
        target="minimum_sufficient_cause",
        recovered=recovered,
        planted={"family": inst.family},
        evidence_class="E2",
    )
    refuse_generator_intent_as_cause(labelled)
    assert labelled["source"] == "INDEPENDENT_RECOVERY"
    assert labelled["truth"]["action"] == exp.action
    cmp = compare_to_planted(inst.family, inst.variant, recovered)
    assert inst.variant == "NEGATIVE"
    assert cmp["reason"] == "PLANTED_FAMILY_BUT_NO_INVALID_ATOM"
    assert cmp["agreement"] == "DISAGREE"


if __name__ == "__main__":
    test_policy_refuses_planted_cause()
    test_e3_requires_independent_authorship()
    test_mex1_recovery_ignores_family_and_can_disagree()
    print("ok")
