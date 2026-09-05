"""M11 §13–§15: the controlled benchmark (with the no-fault control), the recorded replay and the
ORION-V2 intake audit."""
from __future__ import annotations

from ocm.selfmodel import benchmark as B
from ocm.selfmodel import intake as I
from ocm.selfmodel import replay as R


def test_benchmark_scenarios_diagnose_repair_and_refuse_broad_rewrites(tmp_path):
    rows = {sc.scenario_id: B.run_scenario(sc, tmp_path) for sc in B.scenarios()}
    ctl = rows["S0_no_fault_control"]
    assert ctl["no_failure"] and ctl["proposal_class"] is None and not ctl["adopted"]           # no alarm when nothing failed
    for sid, r in rows.items():
        if sid == "S0_no_fault_control":
            continue
        assert r["diagnosis_correct"] and r["minimum_class_correct"], (sid, r["diagnosed"], r["proposal_class"])
        assert r["adopted"] and r["target_after"] == "6/6" and r["rollback_exact"], sid
        assert int(r["preservation_after"][0]) >= int(r["preservation_before"][0]), sid
        assert not r["false_jump"] and not r["missed_jump"], sid
    assert rows["S3_representation_ceiling"]["escalation_allowed"] and rows["S3_representation_ceiling"]["architecture_alarm"]
    s6 = rows["S6_harmful_jump"]["broad_rewrite"]
    assert s6["preservation"] == "0/6" and not s6["assurance"] and "preserved_capabilities" in s6["reasons"] and s6["refused"]   # harmful Jump refused on preservation, not only on class
    s5 = rows["S5_false_structural_alarm"]["broad_rewrite"]
    assert s5["assurance"] and not s5["minimum_sufficient"] and s5["refused"]                        # benign-but-excessive rewrite refused as not minimum
    assert rows["S5_false_structural_alarm"]["diagnosed"] == "D2" and not rows["S5_false_structural_alarm"]["architecture_alarm"]
    # the parents: configuration search reaches only router/revocation faults; retry reaches only the router fault
    t, p = B.suites_for(1)
    by = {sc.scenario_id: sc for sc in B.scenarios()}
    assert B.parent_parameter_search(by["S2_operator_fault"], t, p)["target"] == "0/6" and B.parent_parameter_search(by["S1_router_fault"], t, p)["solves"]
    assert not B.parent_reflection_retry(by["S2_operator_fault"], t, p)["solves"]


def test_recorded_replay_and_intake_are_descriptive():
    rep = R.replay_all()
    assert rep["summary"]["rows"] == 18 and rep["summary"]["narrow"] == 18 and rep["summary"]["escalated_cannot_check"] == 0
    assert "RECORDED_REPLAY" in rep["summary"]["kind"]
    a = I.audit()
    assert a["intakes"] == len(I.INTAKES) and a["defects_with_fix_ref"] == a["by_status"]["DEFECT_FOUND"]
