"""Recorder failures retain actual child output and conservative cleanup evidence."""
import json,subprocess
import pytest
import unary_method_process as P
import unary_method_profile as B

def test_spawn_failure_retains_request_and_empty_raw_streams(tmp_path,monkeypatch):
    def fail(*a,**k):raise OSError("authored spawn refusal")
    monkeypatch.setattr(P.subprocess,"Popen",fail)
    out=P.launch(tmp_path/"spawn","solve",{},profile=B.observe())
    assert out["terminal"]=="PROCESS_REFUSED" and out["pid"] is None
    assert not out["reaped"] and not out["group_absent"]
    assert "authored spawn refusal" in out["error"]
    assert (tmp_path/"spawn/stdout.bin").read_bytes()==b""
    assert json.loads((tmp_path/"spawn/PROCESS.json").read_bytes())==out

@pytest.mark.parametrize("mode",["timeout","nonzero"])
def test_actual_harmless_failure_child_is_reaped_and_preserved(tmp_path,monkeypatch,mode):
    actual=subprocess.Popen
    code="import sys,time; print('authored-child',flush=True); "
    code+="time.sleep(10)" if mode=="timeout" else "sys.stderr.write('authored-error');sys.exit(7)"
    def child(argv,**kwargs):
        return actual([B.observe()["executable"],"-I","-S","-B","-c",code],**kwargs)
    monkeypatch.setattr(P.subprocess,"Popen",child)
    out=P.launch(tmp_path/mode,"solve",{},timeout=0.3,profile=B.observe())
    assert out["terminal"]=="PROCESS_REFUSED"
    assert out["reaped"] and out["group_absent"] and out["pid"]>0
    assert (tmp_path/mode/"stdout.bin").read_bytes()==b"authored-child\n"
    if mode=="timeout":assert "TimeoutExpired" in out["error"] and out["returncode"]<0
    else:
        assert out["returncode"]==7 and out["error"] is None
        assert (tmp_path/mode/"stderr.bin").read_bytes()==b"authored-error"

@pytest.mark.parametrize("fault",[False,True])
def test_post_child_source_failure_preserves_observed_exit(tmp_path,monkeypatch,fault):
    actual=subprocess.Popen;sources=P.D.sources;calls=0
    def child(argv,**kwargs):
        return actual([B.observe()["executable"],"-I","-S","-B","-c","import sys;print('finished',flush=True);sys.exit(7)"],**kwargs)
    def inventory(work=None):
        nonlocal calls
        calls+=1
        if calls==2 and fault:raise OSError("authored post-child source disappearance")
        return sources(work)
    monkeypatch.setattr(P.subprocess,"Popen",child);monkeypatch.setattr(P.D,"sources",inventory)
    out=P.launch(tmp_path/"post-source","solve",{},profile=B.observe())
    assert out["returncode"]==7 and out["reaped"] and out["group_absent"]
    assert out["terminal"]=="PROCESS_REFUSED"
    assert (tmp_path/"post-source/PROCESS.json").is_file()
    if fault:
        assert out["source_after"] is None and "source disappearance" in out["postcheck_error"]
