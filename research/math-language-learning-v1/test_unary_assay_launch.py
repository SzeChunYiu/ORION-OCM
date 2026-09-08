"""Authored deadline enforcement at actual fixed-launch boundaries."""
import json,time
import pytest
import unary_method_process as P
import unary_method_profile as B
from assay_test_support import authored_only

@pytest.mark.parametrize("where",["already","sources","profile"])
def test_expiry_during_preflight_never_launches(tmp_path,monkeypatch,where):
    deadline=time.monotonic()+(0 if where=="already" else .05)
    if where=="sources":
        original=P.D.sources
        def slow(*a,**k):time.sleep(.06);return original(*a,**k)
        monkeypatch.setattr(P.D,"sources",slow)
    if where=="profile":
        original=B.verify
        def slow(*a,**k):time.sleep(.06);return original(*a,**k)
        monkeypatch.setattr(B,"verify",slow)
    monkeypatch.setattr(P.subprocess,"Popen",lambda *a,**k:pytest.fail("late launch"))
    out=P.launch(tmp_path/"expired","solve",{},profile=B.observe(),deadline=deadline)
    assert out["terminal"]=="PROCESS_REFUSED" and out["pid"] is None
    assert "DEADLINE" in out["error"] and out["deadline_monotonic"]==deadline
    assert not out["reaped"] and not out["group_absent"]
    assert json.loads((tmp_path/"expired/PROCESS.json").read_bytes())==out

def test_wait_uses_current_remaining_after_slow_dispatch(tmp_path,monkeypatch):
    actual=P.subprocess.Popen;seen=[]
    def slow(argv,**kwargs):
        child=actual([B.observe()["executable"],"-I","-S","-B","-c",
                      "import time;print('started',flush=True);time.sleep(5)"],**kwargs)
        original=child.wait
        def wait(timeout=None):
            if timeout is not None:seen.append(timeout)
            return original(timeout=timeout)
        child.wait=wait;time.sleep(.12);return child
    monkeypatch.setattr(P.subprocess,"Popen",slow)
    out=P.launch(tmp_path/"wait","solve",{},profile=B.observe(),deadline=time.monotonic()+.5)
    assert out["terminal"]=="PROCESS_REFUSED" and out["reaped"] and out["group_absent"]
    assert seen and 0<seen[0]<.38 and out["returncode"]<0
    assert (tmp_path/"wait/stdout.bin").read_bytes()==b"started\n"
