"""Outer custody errors retain known or uncertain dispatch state."""
import pytest
from pathlib import Path
from test_build_profile import fixture,subject
from test_resource_contract import limits
from dispatch_test_support import controlled,command

@pytest.mark.parametrize("fault",["custody","returned_failure","unreturned","precommand",None])
def test_profile_retains_actual_dispatch_or_explicit_uncertainty(tmp_path,monkeypatch,fault):
    m=subject();p=fixture(tmp_path);calls=[]
    marker,children,_=controlled(m.resource_runner,tmp_path,monkeypatch)
    monkeypatch.setattr(m,"helper",lambda mode,*args:calls.append(mode) or {})
    original_command=m.command
    def prepare_command(*args):
        if fault=="precommand":raise OSError("authored command construction")
        return command(marker)
    monkeypatch.setattr(m,"command",prepare_command)
    original_run=m.resource_runner.run
    def dispatch(*args,**kw):
        result=original_run(*args,**kw)
        if fault=="unreturned":raise OSError("authored lost returned receipt")
        if fault=="custody":(tmp_path/"source/x").write_text("changed")
        if fault=="returned_failure":result["terminal"]="MONITOR_FAILED"
        return result
    monkeypatch.setattr(m.resource_runner,"run",dispatch)
    receipt=m.run(p,limits(),tmp_path/"out")
    expected={"custody":"POST_DISPATCH_CUSTODY_FAILED","returned_failure":"MONITOR_FAILED","unreturned":"DISPATCH_UNCERTAIN","precommand":"PROFILE_REFUSED",None:"COMPLETED"}[fault]
    assert receipt["terminal"]==expected
    assert all(child.poll() is not None for child in children)
    if fault=="precommand":
        assert not marker.exists() and receipt["dispatch_state"]=="NOT_ATTEMPTED"
        assert receipt["terminal"]=="PROFILE_REFUSED"
        assert calls==["policy-add","policy-remove"]
    else:
        assert marker.read_text()=="started"
        if fault=="unreturned":
            assert receipt["dispatch_state"]=="ATTEMPTED_UNKNOWN"
            assert receipt["primary_outcome"]["terminal"]=="DISPATCH_UNCERTAIN"
            assert receipt["terminal"]=="DISPATCH_UNCERTAIN"
            assert receipt["policy_retained_until_empty"] is True
            assert calls==["policy-add"]
        else:
            assert receipt["dispatch_state"]=="STARTED"
            assert receipt["dispatch"]["dispatch"]["state"]=="STARTED"
            expected={"custody":"POST_DISPATCH_CUSTODY_FAILED","returned_failure":"MONITOR_FAILED",None:"COMPLETED"}[fault]
            assert receipt["terminal"]==expected
            assert calls==["policy-add","policy-remove"]
            if fault=="custody":
                assert receipt["failure_phase"]=="POST_DISPATCH_CUSTODY"
                assert receipt["dispatch"]["terminal"]=="COMPLETED"
    assert (tmp_path/"out/build-profile-receipt.json").is_file()

def test_cleanup_override_keeps_custody_failure(tmp_path,monkeypatch):
    m=subject();p=fixture(tmp_path)
    def helper(mode,*args):
        if mode=="policy-remove":raise OSError("authored policy cleanup")
        return {}
    monkeypatch.setattr(m,"helper",helper)
    def dispatch(*args,**kw):
        (tmp_path/"source/x").write_text("changed")
        return {"terminal":"COMPLETED","dispatch":{"state":"STARTED","attempted":True,"pid":123},
                "cleanup":{"members_empty":True,"reaped":True,"controllers_removed":True}}
    monkeypatch.setattr(m.resource_runner,"run",dispatch)
    receipt=m.run(p,limits(),tmp_path/"out")
    assert receipt["terminal"]=="CLEANUP_INCOMPLETE"
    assert receipt["primary_outcome"]["terminal"]=="POST_DISPATCH_CUSTODY_FAILED"
    assert receipt["primary_outcome"]["phase"]=="POST_DISPATCH_CUSTODY"
    assert receipt["error"]["class"]=="ValueError"
