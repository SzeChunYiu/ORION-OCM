"""An observed exit remains recorded if the first cleanup snapshot fails."""
import pytest
import resource_runner as runner
from dispatch_test_support import controlled,command
from test_resource_contract import limits

@pytest.mark.parametrize("exit_code",[0,7])
def test_observed_exit_survives_first_cleanup_snapshot(tmp_path,monkeypatch,exit_code):
    marker,children,calls=controlled(runner,tmp_path,monkeypatch)
    original=runner.Controller.snapshot
    failures=[]
    def snapshot(self):
        # The loop just observed termination; fail its first cleanup read.
        if children and children[0].returncode is not None and not failures:
            failures.append(children[0].returncode)
            raise OSError("authored first cleanup snapshot")
        return original(self)
    monkeypatch.setattr(runner.Controller,"snapshot",snapshot)
    argv=command(marker);argv[-1]+=";raise SystemExit("+str(exit_code)+")"
    result=runner.run(argv,{},limits(),tmp_path/"out",[])
    assert marker.read_text()=="started" and failures==[exit_code]
    assert all(child.poll() is not None for child in children)
    assert result["returncode"]==exit_code
    assert result["dispatch"]["state"]=="STARTED"
    assert result["terminal"]=="CLEANUP_INCOMPLETE"
    assert result["primary_outcome"]["terminal"]==("COMPLETED" if exit_code==0 else "COMMAND_FAILED")
    assert result["cleanup"]["reaped"] is False and result["cleanup"]["members_empty"] is False
    assert "authored first cleanup snapshot" in result["cleanup"]["error"]
    assert not result["cleanup"].get("controllers_removed") and "removed" not in calls


def test_stop_preserves_exit_observed_by_cleanup_poll(tmp_path,monkeypatch):
    marker,children,calls=controlled(runner,tmp_path,monkeypatch)
    observed=[]
    def snapshot(self):
        # Keep membership until the supervisor's own cleanup poll observes exit.
        if children and children[0].returncode is not None and not observed:
            observed.append(children[0].returncode)
            raise OSError("authored snapshot after cleanup poll")
        return {"members":[p.pid for p in children if p.returncode is None],
                "memory.failcnt":0,"memory.memsw.failcnt":0,"pids.events":{}}
    monkeypatch.setattr(runner.Controller,"snapshot",snapshot)
    monkeypatch.setattr(runner,"reason",lambda *args:"WALL_DEADLINE")
    argv=command(marker);argv[-1]=argv[-1].replace("time.sleep(.10)","time.sleep(3)")
    result=runner.run(argv,{},limits(),tmp_path/"out",[])
    assert marker.read_text()=="started" and len(observed)==1
    assert result["returncode"]==observed[0]
    assert children[0].poll()==observed[0]
    assert result["primary_outcome"]["terminal"]=="RESOURCE_STOP"
    assert result["terminal"]=="CLEANUP_INCOMPLETE"
    assert result["cleanup"]["reaped"] is False and not result["cleanup"].get("controllers_removed")
    assert "removed" not in calls
