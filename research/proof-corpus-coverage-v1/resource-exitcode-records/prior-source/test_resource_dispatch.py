"""Truthful post-launch failure attribution; no privileged controller needed."""
import pytest
import resource_runner as runner
from test_resource_contract import limits
from dispatch_test_support import controlled,command

@pytest.mark.parametrize("fault",[None,"disk","controller","sample","cleanup","raw","missing_raw"])
def test_actual_started_child_keeps_dispatch_and_primary_cause(tmp_path,monkeypatch,fault):
    marker,children,calls=controlled(runner,tmp_path,monkeypatch,fault)
    receipt=runner.run(command(marker),{},limits(),tmp_path/"out",[])
    assert marker.read_text()=="started" and all(p.poll() is not None for p in children)
    expected={"disk":"MONITOR_FAILED","controller":"MONITOR_FAILED","sample":"MONITOR_FAILED","cleanup":"CLEANUP_INCOMPLETE","raw":"EVIDENCE_FAILED","missing_raw":"EVIDENCE_FAILED",None:"COMPLETED"}[fault]
    assert receipt["terminal"]==expected
    assert receipt["dispatch"]["state"]=="STARTED" and receipt["dispatch"]["attempted"] is True
    assert receipt["dispatch"]["pid"]==children[0].pid
    if fault is None:
        assert receipt["terminal"]=="COMPLETED" and receipt["primary_outcome"]["terminal"]=="COMPLETED"
    elif fault in ("raw","missing_raw"):
        assert receipt["terminal"]=="EVIDENCE_FAILED"
        assert receipt["evidence_errors"][0]["phase"]=="RAW_CUSTODY"
    else:
        assert receipt["primary_outcome"]["terminal"]=="MONITOR_FAILED"
        assert receipt["primary_outcome"]["phase"]=="MONITOR"
        assert receipt["error"]["message"].startswith("authored ")
        assert receipt["terminal"]==("CLEANUP_INCOMPLETE" if fault=="cleanup" else "MONITOR_FAILED")
    assert receipt["cleanup"]["reaped"] and receipt["cleanup"]["members_empty"]
    assert (tmp_path/"out/resource-receipt.json").is_file()

def test_launch_exception_does_not_claim_not_attempted_or_reaped(tmp_path,monkeypatch):
    marker,children,calls=controlled(runner,tmp_path,monkeypatch,"launch")
    receipt=runner.run(command(marker),{},limits(),tmp_path/"out",[])
    assert not marker.exists() and not children
    assert receipt["dispatch"]=={"state":"ATTEMPTED_UNKNOWN","attempted":True,"pid":None}
    assert receipt["primary_outcome"]["terminal"]=="DISPATCH_UNCERTAIN"
    assert receipt["primary_outcome"]["phase"]=="LAUNCH"
    assert receipt["terminal"]=="CLEANUP_INCOMPLETE"
    assert receipt["cleanup"]["reaped"] is False and "removed" not in calls

def test_initial_scan_failure_is_truthfully_no_dispatch(tmp_path,monkeypatch):
    monkeypatch.setattr(runner,"disk_snapshot",lambda _:(_ for _ in ()).throw(OSError("prelaunch scan")))
    receipt=runner.run(["must-not-dispatch"],{},limits(),tmp_path/"out",[])
    assert receipt["terminal"]=="SETUP_REFUSED"
    assert receipt["dispatch"]=={"state":"NOT_ATTEMPTED","attempted":False,"pid":None}
    assert receipt["primary_outcome"]["phase"]=="SETUP"
    assert receipt["cleanup"]["no_dispatch"] is True

def test_existing_clean_no_alarm(tmp_path,monkeypatch):
    marker,children,_=controlled(runner,tmp_path,monkeypatch)
    result=runner.run(command(marker),{},limits(),tmp_path/"out",[])
    assert result["terminal"]=="COMPLETED" and result["returncode"]==0
    assert marker.read_text()=="started" and result["cleanup"]["reaped"] and result["cleanup"]["members_empty"]

@pytest.mark.parametrize("fault",[None,"raw","late_cleanup"])
def test_nonzero_primary_survives_late_custody_failure(tmp_path,monkeypatch,fault):
    marker,children,_=controlled(runner,tmp_path,monkeypatch,fault)
    argv=command(marker);argv[-1]+=";raise SystemExit(7)"
    result=runner.run(argv,{},limits(),tmp_path/"out",[])
    assert marker.read_text()=="started" and result["returncode"]==7
    assert result["primary_outcome"]["terminal"]=="COMMAND_FAILED"
    assert result["terminal"]=={None:"COMMAND_FAILED","raw":"EVIDENCE_FAILED","late_cleanup":"CLEANUP_INCOMPLETE"}[fault]

def test_final_disk_failure_retains_completed_child(tmp_path,monkeypatch):
    marker,children,calls=controlled(runner,tmp_path,monkeypatch)
    original=runner.disk_snapshot
    def disk(roots):
        if "removed" in calls:raise OSError("authored final disk")
        return original(roots)
    monkeypatch.setattr(runner,"disk_snapshot",disk)
    result=runner.run(command(marker),{},limits(),tmp_path/"out",[])
    assert marker.read_text()=="started" and result["returncode"]==0
    assert result["terminal"]=="EVIDENCE_FAILED" and result["evidence_complete"] is False
    assert result["primary_outcome"]["terminal"]=="COMPLETED"
    assert result["evidence_errors"][0]["phase"]=="FINAL_DISK_ACCOUNTING"
