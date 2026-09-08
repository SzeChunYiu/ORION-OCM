import os,pytest
pytestmark=pytest.mark.skipif(os.environ.get("OCM_RESOURCE_HOST_QUALIFICATION")!="1",reason="explicit scoped laptop controller qualification required")
import importlib.util,sys,json
from test_resource_contract import limits

def run(tmp_path,code,**changes):
    assert importlib.util.find_spec("resource_runner") is not None,"aggregate supervisor missing"
    import resource_runner as r
    return r.run([sys.executable,"-I","-S","-c",code],{},limits(**changes),tmp_path/"out",[])

def test_clean_spool_and_descendant_controller_membership(tmp_path):
    r=run(tmp_path,"import pathlib; print(pathlib.Path('/proc/self/cgroup').read_text())")
    assert r["terminal"]=="COMPLETED" and r["returncode"]==0
    text=(tmp_path/"out/stdout.bin").read_text()
    assert text.count("/ocm-f1-coverage-v1/")==3
    assert r["cleanup"]["members_empty"] and r["cleanup"]["reaped"]

def test_cpu_group_throttles_aggregate_workers(tmp_path):
    r=run(tmp_path,"import time; end=time.monotonic()+.5\nwhile time.monotonic()<end: pass")
    assert r["terminal"]=="COMPLETED"
    assert r["final_resources"]["cpu.stat"]["nr_throttled"]>0

def test_timeout_retains_partial_output_and_reaps(tmp_path):
    r=run(tmp_path,"import time;print('before',flush=True);time.sleep(10)",wall_s=.2)
    assert r["terminal"]=="RESOURCE_STOP" and r["reason"]=="WALL_DEADLINE"
    assert (tmp_path/"out/stdout.bin").read_text()=="before\n"
    assert r["cleanup"]["members_empty"] and r["cleanup"]["reaped"]

def test_disk_threshold_is_monitor_stop_not_quota(tmp_path):
    r=run(tmp_path,"import os,time\nf=open('data','wb');f.write(b'x'*200000);f.flush();time.sleep(2)",max_owned_bytes=100000)
    assert r["terminal"]=="RESOURCE_STOP" and r["reason"]=="OWNED_BYTES"
    assert r["overshoot_bytes"]>=100000
    assert r["disk_enforcement"]=="SAMPLED_STOP_NOT_HARD_QUOTA"

def test_host_sigterm_preserves_receipt_and_cleans_descendants(tmp_path):
    import os,signal,subprocess,time
    from resource_pidfd import open_pid,send
    from pathlib import Path
    code="import sys;sys.path.insert(0,"+repr(str(Path(__file__).parent.resolve()))+");from resource_runner import run;run("+repr([sys.executable,"-I","-S","-c","import time;print('ready',flush=True);time.sleep(20)"])+",{},"+repr(limits(wall_s=10))+","+repr(str(tmp_path/"out"))+",[])"
    host=subprocess.Popen([sys.executable,"-I","-S","-c",code])
    fd=open_pid(host.pid)
    try:
        deadline=time.monotonic()+5
        stdout=tmp_path/"out/stdout.bin"
        while time.monotonic()<deadline and (not stdout.exists() or "ready" not in stdout.read_text()):
            assert host.poll() is None
            time.sleep(.02)
        assert stdout.read_text()=="ready\n"
        send(fd,signal.SIGTERM);assert host.wait(timeout=5)==0
        r=json.loads((tmp_path/"out/resource-receipt.json").read_bytes())
        assert r["terminal"]=="INTERRUPTED"
        assert r["cleanup"]["members_empty"] and r["cleanup"]["reaped"] and r["cleanup"]["controllers_removed"]
    finally:
        if host.poll() is None:send(fd,signal.SIGKILL);host.wait(timeout=5)
        os.close(fd)
