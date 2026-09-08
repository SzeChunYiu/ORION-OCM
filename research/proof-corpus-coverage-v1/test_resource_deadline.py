"""Original-deadline input refusal, sampled stopping and actual child cleanup."""
import copy,time
from pathlib import Path
import pytest
from resource_contract import canonical,record
from test_resource_contract import limits
from deadline_test_support import started
from dispatch_test_support import controlled,command

@pytest.fixture(autouse=True)
def current_raw_module_closure():
    import resource_boot
    resource_boot.load()

def watcher(binding,forbidden=()):
    from resource_deadline import Started
    return Started(binding,forbidden)

def test_bound_original_record_and_repeated_consumed_bytes(tmp_path):
    b=started(tmp_path);w=watcher(b)
    a=w.check("FIRST");c=w.check("SECOND")
    assert a["deadline_monotonic_ns"]==c["deadline_monotonic_ns"]
    assert c["remaining_ns"]<a["remaining_ns"] and w.receipt["checks"]==2
    assert w.receipt["bytes_read"]==2*b["record"]["bytes"]
    assert w.receipt["binding"]==b

@pytest.mark.parametrize("fault",["missing","symlink","hardlink","directory","bytes","hash","noncanonical",
 "wrong_boot","future","expired","bool_start","bool_duration","too_long","nan","run","seal"])
def test_invalid_external_record_never_means_unbound(tmp_path,fault):
    from resource_deadline import DeadlineFailure
    b=started(tmp_path);p=Path(b["record"]["path"])
    if fault=="missing":p.unlink()
    elif fault=="symlink":
        target=tmp_path/"original";p.rename(target);p.symlink_to(target)
    elif fault=="hardlink":(tmp_path/"alias").hardlink_to(p)
    elif fault=="directory":p.unlink();p.mkdir()
    elif fault=="bytes":b["record"]["bytes"]+=1
    elif fault=="hash":b["record"]["sha256"]="b"*64
    elif fault=="bool_duration":b["duration_ns"]=True
    elif fault=="too_long":b["duration_ns"]=1200000000001
    elif fault=="run":b["run_id"]="authored-other"
    elif fault=="seal":b["launch_seal_sha256"]="b"*64
    else:
        import json
        v=json.loads(p.read_bytes())
        if fault=="noncanonical":p.write_bytes(b" "+canonical(v))
        else:
            if fault=="wrong_boot":v["boot_id"]="00000000-0000-0000-0000-000000000000"
            if fault=="future":
                v["started_monotonic_ns"]=time.monotonic_ns()+1000000000
                v["deadline_monotonic_ns"]=v["started_monotonic_ns"]+b["duration_ns"]
            if fault=="expired":
                v["started_monotonic_ns"]=time.monotonic_ns()-6000000000
                v["deadline_monotonic_ns"]=v["started_monotonic_ns"]+b["duration_ns"]
            if fault=="bool_start":v["started_monotonic_ns"]=True
            if fault=="nan":
                p.write_text('{"schema":NaN}');b["record"]=record(p)
                with pytest.raises(DeadlineFailure):watcher(b).check("INVALID")
                return
            p.write_bytes(canonical(v))
        b["record"]=record(p)
    w=watcher(b)
    with pytest.raises(DeadlineFailure):w.check("INVALID")
    assert w.receipt["first_failure"]["reason"].startswith("EXTERNAL_")

def test_owned_overlap_and_replaced_identical_record_refuse(tmp_path):
    from resource_deadline import DeadlineFailure
    b=started(tmp_path)
    with pytest.raises(DeadlineFailure,match="WRITABLE"):watcher(b,[tmp_path]).check("OVERLAP")
    w=watcher(b);w.check("CLEAN");p=Path(b["record"]["path"]);raw=p.read_bytes()
    p.rename(tmp_path/"preserved-original");p.write_bytes(raw)
    with pytest.raises(DeadlineFailure,match="IDENTITY"):w.check("REPLACED")

@pytest.mark.parametrize("fault",["expire","drift","delete","boot"])
def test_started_child_retains_original_clock_cleanup_and_failure(tmp_path,monkeypatch,fault):
    import resource_runner as r
    import resource_deadline as d
    marker,children,calls=controlled(r,tmp_path,monkeypatch);b=started(tmp_path)
    original=r.disk_snapshot;done=[]
    def disk(roots):
        value=original(roots)
        if children and not done:
            done.append(True)
            if fault=="expire":monkeypatch.setattr(d.time,"monotonic_ns",lambda:b["duration_ns"]+10**18)
            elif fault=="drift":Path(b["record"]["path"]).write_bytes(b"{}")
            elif fault=="delete":Path(b["record"]["path"]).unlink()
            else:monkeypatch.setattr(d,"boot_id",lambda:"00000000-0000-0000-0000-000000000000")
        return value
    monkeypatch.setattr(r,"disk_snapshot",disk)
    argv=command(marker);argv[-1]=argv[-1].replace("time.sleep(.10)","time.sleep(3)")
    result=r.run(argv,{},limits(),tmp_path/"out",[],external_started=b)
    assert result["dispatch"]["state"]=="STARTED" and result["dispatch"]["pid"]==children[0].pid
    assert result["terminal"]==("RESOURCE_STOP" if fault=="expire" else "EVIDENCE_FAILED")
    assert result["external_started"]["binding"]==b
    assert result["external_started"]["first_failure"]["phase"]=="MONITOR_AFTER"
    assert result["returncode"] is not None and result["cleanup"]["reaped"] and result["cleanup"]["members_empty"]

def test_setup_expiry_never_attempts_Popen(tmp_path,monkeypatch):
    import resource_runner as r
    import resource_deadline as d
    marker,children,calls=controlled(r,tmp_path,monkeypatch);b=started(tmp_path)
    original=r.Controller.create
    def create(*a):
        value=original(*a);monkeypatch.setattr(d.time,"monotonic_ns",lambda:10**18);return value
    monkeypatch.setattr(r.Controller,"create",create)
    result=r.run(command(marker),{},limits(),tmp_path/"out",[],external_started=b)
    assert result["dispatch"]["state"]=="NOT_ATTEMPTED" and not children
    assert result["terminal"]=="SETUP_REFUSED" and "EXTERNAL_DEADLINE_EXPIRED" in result["reason"]

def test_final_hash_expiry_retains_observed_zero_exit(tmp_path,monkeypatch):
    import resource_runner as r
    import resource_deadline as d
    marker,children,calls=controlled(r,tmp_path,monkeypatch);b=started(tmp_path);original=r.record
    def stamp(p):
        value=original(p)
        if Path(p).name=="samples.jsonl":monkeypatch.setattr(d.time,"monotonic_ns",lambda:10**18)
        return value
    monkeypatch.setattr(r,"record",stamp)
    result=r.run(command(marker),{},limits(),tmp_path/"out",[],external_started=b)
    assert result["returncode"]==0 and result["primary_outcome"]["terminal"]=="COMPLETED"
    assert result["terminal"]=="RESOURCE_STOP" and result["external_started"]["first_failure"]["phase"]=="FINAL_CUSTODY"
    assert result["cleanup"]["reaped"] and result["cleanup"]["members_empty"]

def test_present_and_omitted_optional_binding_both_complete(tmp_path,monkeypatch):
    import resource_runner as r
    for name in ("legacy","external"):
        root=tmp_path/name;root.mkdir();marker,children,calls=controlled(r,root,monkeypatch)
        kw={} if name=="legacy" else {"external_started":started(root)}
        result=r.run(command(marker),{},limits(),root/"out",[],**kw)
        assert result["terminal"]=="COMPLETED" and result["returncode"]==0
        assert ("external_started" in result)==bool(kw)

def test_final_observation_time_cannot_report_late_validity(tmp_path,monkeypatch):
    import resource_deadline as d
    b=started(tmp_path);w=watcher(b);deadline=__import__("json").loads(Path(b["record"]["path"]).read_bytes())["deadline_monotonic_ns"]
    times=iter((deadline-1,deadline+1));monkeypatch.setattr(d.time,"monotonic_ns",lambda:next(times))
    with pytest.raises(d.DeadlineFailure,match="EXTERNAL_DEADLINE_EXPIRED"):w.check("LATE_OBSERVATION")
    assert w.receipt["latest"]["lateness_ns"]==1

def test_known_parsed_original_time_survives_boot_refusal(tmp_path):
    import resource_deadline as d
    b=started(tmp_path,changes={"boot_id":"00000000-0000-0000-0000-000000000000"});w=watcher(b)
    with pytest.raises(d.DeadlineFailure,match="BOOT"):w.check("BOOT_REFUSAL")
    assert w.receipt["first_failure"]["deadline_monotonic_ns"]>0


@pytest.mark.parametrize("fault",["nested_record","unexpected_exception"])
def test_failed_validation_cannot_record_valid_observation(tmp_path,monkeypatch,fault):
    import resource_deadline as d
    b=started(tmp_path);clean=watcher(b);assert clean.check("CLEAN")["terminal"]=="VALID"
    if fault=="nested_record":
        p=Path(b["record"]["path"]);p.write_bytes(b'{"schema":'+b'['*1200+b'0'+b']'*1200+b'}')
        b["record"]=record(p);w=watcher(b)
        expected=d.DeadlineFailure;cause="RecursionError"
    else:
        w=watcher(b)
        def fail():raise RuntimeError("authored validation exception")
        monkeypatch.setattr(w,"_read",fail);expected=RuntimeError;cause="RuntimeError"
    with pytest.raises(expected):w.check("FAILED_VALIDATION")
    assert w.receipt["latest"]["terminal"]=="REFUSED"
    assert w.receipt["first_failure"]["validation_error"]["class"]==cause
