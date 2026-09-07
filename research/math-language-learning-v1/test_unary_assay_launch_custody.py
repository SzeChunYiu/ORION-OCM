"""Actual post-write clock custody and precise authored denial verdict controls."""
import errno,os,subprocess
from pathlib import Path
import pytest
import unary_assay_launch_contract as L
import unary_assay_launch_profile as P
import unary_assay_launch as A
import unary_assay_probe as Q
import unary_method_outer as D
from test_unary_assay_namespace import RUNTIME,restore_resource_registry

def prepared(tmp_path):
    review=L.write(tmp_path/"review.json",{"scope":"AUTHORED_CUSTODY_CONTROL","sources":D.sources()})
    P.prepare(tmp_path/"prepared",RUNTIME,run_id="authored-issuance-control",mode="AUTHORED_PROBE",
        duration_ns=20000000000,cpu=min(os.sched_getaffinity(0)),input_value={"case":"normal"},review=review)
    return tmp_path/"prepared"

@pytest.mark.skipif(not RUNTIME.exists(),reason="Reviewed laptop snapshot required")
@pytest.mark.parametrize("fault",[None,"clock_stamp","directory_fsync"])
def test_known_original_clock_survives_post_write_failure(tmp_path,monkeypatch,fault):
    root=prepared(tmp_path);original=P.resources
    def resources():
        modules,sources=original()
        def run(profile,limits,output,**kw):
            Path(output).mkdir()
            L.write(Path(output)/"build-profile-receipt.json",{"terminal":"COMPLETED"})
            L.write(root/"work/BOOTSTRAP.json",{"terminal":"BOOTSTRAP_COMPLETED"})
            return {"terminal":"COMPLETED"}
        modules["build_profile"].run=run
        return modules,sources
    monkeypatch.setattr(P,"resources",resources)
    failed=[]
    if fault=="clock_stamp":
        stamp=L.stamp
        def fail(p):
            if Path(p)==root/"STARTED.json" and not failed:
                failed.append(True);raise OSError("authored post-write stamp failure")
            return stamp(p)
        monkeypatch.setattr(L,"stamp",fail)
    elif fault=="directory_fsync":
        fsync=os.fsync
        def fail(fd):
            if Path(os.readlink("/proc/self/fd/"+str(fd)))==root and (root/"STARTED.json").exists() and not failed:
                failed.append(True);raise OSError("authored post-write directory fsync failure")
            return fsync(fd)
        monkeypatch.setattr(os,"fsync",fail)
    result=A.launch(L.stamp(root/"PREPARED.json"))
    assert (root/"STARTED.json").is_file()
    assert result["started"]["value"]["deadline_monotonic_ns"]>0
    assert result["started"]["state"]==("ISSUED" if fault is None else "ISSUANCE_UNCERTAIN")
    assert result["terminal"]==("LAUNCH_COMPLETED" if fault is None else "LAUNCH_REFUSED")
    if fault:
        assert result["dispatch"] is None and result["started"]["bytes_written"] is True
        assert "authored post-write" in result["error"]["message"]

@pytest.mark.skipif(not RUNTIME.exists(),reason="Reviewed laptop snapshot required")
def test_preparation_persists_new_root_parent_entry(tmp_path,monkeypatch):
    seen=[];fsync=os.fsync
    def observe(fd):
        seen.append(os.readlink("/proc/self/fd/"+str(fd)));return fsync(fd)
    # The initial external review write is not evidence for the later mkdir.
    review=L.write(tmp_path/"review.json",{"scope":"AUTHORED_PARENT_FSYNC","sources":D.sources()})
    monkeypatch.setattr(os,"fsync",observe)
    P.prepare(tmp_path/"prepared",RUNTIME,run_id="authored-parent-entry",mode="AUTHORED_PROBE",
        duration_ns=20000000000,cpu=min(os.sched_getaffinity(0)),input_value={"case":"normal"},review=review)
    assert str(tmp_path) in seen

@pytest.mark.parametrize("outcome",["denied","executed_nonzero"])
def test_native_exec_denial_is_not_an_executed_nonzero_child(tmp_path,monkeypatch,outcome):
    monkeypatch.setattr(L,"WORK",str(tmp_path));monkeypatch.setattr(Q,"observation",lambda:{"pid":os.getpid()})
    def launch(*args,**kwargs):
        if outcome=="denied":raise PermissionError(errno.EACCES,"authored denial")
        if kwargs.get("check"):raise subprocess.CalledProcessError(7,args[0],output=b"ran",stderr=b"failure")
        return subprocess.CompletedProcess(args[0],7,b"ran",b"failure")
    monkeypatch.setattr(Q.subprocess,"run",launch)
    if outcome=="denied":
        result=Q.run({"case":"native_exec"},__import__("time").monotonic()+5)
        assert result["denied"]["errno"]==errno.EACCES
    else:
        with pytest.raises(ValueError,match="EXECUTED"):Q.run({"case":"native_exec"},__import__("time").monotonic()+5)
        saved=L.read(tmp_path/"probe-native-attempt.json",L.stamp(tmp_path/"probe-native-attempt.json")["sha256"])
        assert saved["returncode"]==7 and saved["stdout"]=="ran" and saved["stderr"]=="failure"


@pytest.mark.parametrize("reason",["failed to map segment from shared object","wrong ELF class"])
def test_native_map_retains_actual_error_and_refuses_unrelated_failure(tmp_path,monkeypatch,reason):
    monkeypatch.setattr(L,"WORK",str(tmp_path));monkeypatch.setattr(Q,"observation",lambda:{"pid":os.getpid()})
    calls=[]
    def load(path):
        calls.append(path)
        if len(calls)>1:raise OSError(reason)
        return object()
    monkeypatch.setattr(Q.ctypes,"CDLL",load)
    if reason.startswith("failed"):
        result=Q.run({"case":"native_map"},__import__("time").monotonic()+5)
        assert result["denied"]["message"]==reason
    else:
        with pytest.raises(ValueError,match="UNCLASSIFIED"):Q.run({"case":"native_map"},__import__("time").monotonic()+5)
    saved=L.read(tmp_path/"probe-native-attempt.json",L.stamp(tmp_path/"probe-native-attempt.json")["sha256"])
    assert saved["mapping_error"]["message"]==reason and len(calls)==2
    assert saved["authorized_libc"]["sha256"]==saved["copied_libc"]["sha256"]
