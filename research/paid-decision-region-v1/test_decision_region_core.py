from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

import decision_region_core as D


def test_common_action_can_stop_before_identification():
    hypotheses = (0, 1, 2)
    safe = {
        0: {"a", "x"},
        1: {"a", "y"},
        2: {"a", "z"},
    }
    costs = {(h, a): 0.0 for h in hypotheses for a in safe[h]}
    probes = ("p",)
    outcomes = {("p", 0): 0, ("p", 1): 1, ("p", 2): 2}
    probe_cost = {"p": 1.0}

    drd = D.solve_worst_case_drd(hypotheses, safe, costs, probes, outcomes, probe_cost)
    identify = D.solve_worst_case_drd(
        hypotheses, safe, costs, probes, outcomes, probe_cost,
        identification_only=True,
    )
    assert drd["value"] == 0.0
    assert drd["first_decision"] == ("stop", "a")
    assert identify["value"] == 1.0
    assert identify["first_decision"] == ("probe", "p")


def test_safety_sufficiency_does_not_imply_economic_stopping():
    hypotheses = (0, 1)
    safe = {0: {"safe", "cheap0"}, 1: {"safe", "cheap1"}}
    costs = {
        (0, "safe"): 10.0,
        (1, "safe"): 10.0,
        (0, "cheap0"): 0.0,
        (1, "cheap1"): 0.0,
    }
    probes = ("identify",)
    outcomes = {("identify", 0): 0, ("identify", 1): 1}
    probe_cost = {"identify": 1.0}

    assert D.common_actions(hypotheses, safe) == frozenset({"safe"})
    result = D.solve_worst_case_drd(
        hypotheses, safe, costs, probes, outcomes, probe_cost
    )
    assert result["value"] == 1.0
    assert result["first_decision"] == ("probe", "identify")


def test_expensive_probe_makes_common_action_economically_sufficient():
    hypotheses = (0, 1)
    safe = {0: {"safe", "cheap0"}, 1: {"safe", "cheap1"}}
    costs = {
        (0, "safe"): 10.0,
        (1, "safe"): 10.0,
        (0, "cheap0"): 0.0,
        (1, "cheap1"): 0.0,
    }
    probes = ("identify",)
    outcomes = {("identify", 0): 0, ("identify", 1): 1}
    probe_cost = {"identify": 20.0}
    result = D.solve_worst_case_drd(
        hypotheses, safe, costs, probes, outcomes, probe_cost
    )
    assert result["value"] == 10.0
    assert result["first_decision"] == ("stop", "safe")


def test_unanimous_external_verdict_has_zero_in_class_information_value():
    version = (0, 1, 2, 3)
    verdict = {0: False, 1: False, 2: False, 3: False}
    common = D.unanimous_verdict(version, verdict)
    assert common is False
    assert D.condition_on_verdict(version, verdict, common) == version


def test_disagreement_probe_can_shrink_version_space():
    version = (0, 1, 2, 3)
    verdict = {0: False, 1: False, 2: True, 3: True}
    assert D.unanimous_verdict(version, verdict) is None
    assert D.condition_on_verdict(version, verdict, False) == (0, 1)
    assert D.condition_on_verdict(version, verdict, True) == (2, 3)


def test_shortcircuit_is_pointwise_minimal_for_fixed_prefix_order():
    version = (0, 1, 2, 3, 4)
    verdict = {0: False, 1: False, 2: True, 3: False, 4: True}
    cert = D.fixed_order_unanimity_certificate(version, verdict)
    assert cert["result"] is None
    assert cert["examined"] == 3
    assert cert["minimum_for_fixed_prefix_order"] == 3


def test_unanimity_requires_full_scan_when_every_survivor_agrees():
    version = (0, 1, 2, 3, 4)
    verdict = {h: True for h in version}
    cert = D.fixed_order_unanimity_certificate(version, verdict)
    assert cert["result"] is True
    assert cert["examined"] == len(version)
