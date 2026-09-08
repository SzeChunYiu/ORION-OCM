"""Real authored row writer/readback and strict output-tamper controls."""
import copy,os,time
from pathlib import Path
import pytest
from unary_contract import InputRefused
import unary_assay_rows as R
import unary_assay_service as S
from unary_assay_exact import ExactRuntime
from test_unary_assay_service import rows
from assay_test_support import authored_only

def bundle(tmp_path):
    request={"rows":rows()};writer=R.Writer(tmp_path)
    outcome=S.run(ExactRuntime(),request["rows"],deadline=time.monotonic()+30,sink=writer)
    return {"pid":os.getpid(),"outcome":outcome},request

def audit(tmp_path,data,request):
    return R.audit(tmp_path,data,request,pid=os.getpid(),work={})

def test_actual_per_row_durable_no_alarm(tmp_path):
    data,request=bundle(tmp_path);work={}
    out=R.audit(tmp_path,data,request,pid=os.getpid(),work=work)
    assert out["terminal"]=="ROW_CUSTODY_PASS" and out["rows"]==2
    assert work["row_files_read"]==work["row_records_decoded"]==2
    assert work["row_bytes_read"]==sum(x["bytes"] for x in data["outcome"]["rows"])
    assert data["outcome"]["sink"]["rows"]==2 and data["outcome"]["sink"]["write_wall_s"]>0
    assert {p.name for p in (tmp_path/"rows").iterdir()}=={"00000.json","00001.json"}

@pytest.mark.parametrize("fault,reason",[("bytes","ROW_HASH"),("size","ROW_BYTES"),("missing","ROW_FILE_SET"),
    ("extra","ROW_FILE_SET"),("path","ROW_PATH"),("index","ROW_ORDER"),
    ("identity","ROW_REQUEST_IDENTITY"),("pid","ROW_PROCESS_BINDING"),
    ("unreached","UNREACHED_ROWS"),("symlink","ROW_NOT_REGULAR"),("hardlink","ROW_NOT_REGULAR")])
def test_real_output_tamper_refused(tmp_path,fault,reason):
    data,request=bundle(tmp_path);first=tmp_path/"rows/00000.json"
    if fault=="bytes":
        raw=first.read_bytes();first.write_bytes(bytes([raw[0]^1])+raw[1:])
    elif fault=="size":first.write_bytes(first.read_bytes()+b" ")
    elif fault=="missing":first.unlink()
    elif fault=="extra":(tmp_path/"rows/extra").write_bytes(b"x")
    elif fault=="path":data["outcome"]["rows"][0]["path"]="../00000.json"
    elif fault=="index":data["outcome"]["rows"][0]["index"]=1
    elif fault=="identity":request["rows"][0]["observation_id"]="changed"
    elif fault=="pid":data["pid"]+=1
    elif fault=="unreached":data["outcome"]["unreached_rows"]=[1]
    elif fault=="symlink":
        saved=tmp_path/"saved";first.rename(saved);first.symlink_to(saved)
    elif fault=="hardlink":os.link(first,tmp_path/"alias")
    with pytest.raises((InputRefused,OSError),match=reason):audit(tmp_path,data,request)

def test_failed_durable_write_keeps_known_row_without_reference(tmp_path,monkeypatch):
    writer=R.Writer(tmp_path)
    def fail(*a):raise OSError("authored row directory fsync failure")
    monkeypatch.setattr(R,"sync_dir",fail)
    out=S.run(ExactRuntime(),rows(),deadline=time.monotonic()+30,sink=writer)
    assert out["terminal"]=="CANNOT_CHECK" and out["unreached_rows"]==[1]
    assert "fsync failure" in out["reason"]
    assert out["rows"][0]["result"]["terminal"]=="CHECKED"
    assert "path" not in out["rows"][0] and writer.next==0
    assert (tmp_path/"rows/00000.json").is_file()

@pytest.mark.parametrize("late",[False,True])
def test_deadline_after_durable_write_keeps_exact_reference(tmp_path,monkeypatch,late):
    original=S.remaining;calls=0
    def remaining(d):
        nonlocal calls
        calls+=1
        if late and calls==4:raise InputRefused("DEADLINE_EXPIRED")
        return original(d)
    monkeypatch.setattr(S,"remaining",remaining)
    request={"rows":rows()};out=S.run(ExactRuntime(),request["rows"],
                                    deadline=time.monotonic()+30,sink=R.Writer(tmp_path))
    data={"pid":os.getpid(),"outcome":out}
    assert audit(tmp_path,data,request)["terminal"]=="ROW_CUSTODY_PASS"
    if late:
        assert out["terminal"]=="CANNOT_CHECK" and out["unreached_rows"]==[1]
        assert out["rows"][0]["terminal"]=="CHECKED"
    else:assert out["terminal"]=="CHECKED"


@pytest.mark.parametrize("fault",["reference","index","row_payload"])
def test_malformed_bound_record_refuses_as_data(tmp_path,fault):
    data,request=bundle(tmp_path)
    if fault=="reference":data["outcome"]["rows"][0]=None
    elif fault=="index":data["outcome"]["rows"][0]["index"]=False
    else:
        raw=b"[]";ref=data["outcome"]["rows"][0]
        (tmp_path/ref["path"]).write_bytes(raw);ref["bytes"]=len(raw);ref["sha256"]=R.digest(raw)
    with pytest.raises(InputRefused):audit(tmp_path,data,request)

def test_oversized_actual_row_is_refused_before_unbounded_read(tmp_path,monkeypatch):
    data,request=bundle(tmp_path);p=tmp_path/"rows/00000.json"
    with p.open("r+b") as f:f.truncate(R.D.MAX_BYTES+17)
    original=Path.read_bytes
    def read(path):
        if path==p:pytest.fail("unbounded actual row read")
        return original(path)
    monkeypatch.setattr(Path,"read_bytes",read)
    with pytest.raises(InputRefused,match="ROW_BYTES"):audit(tmp_path,data,request)

@pytest.mark.parametrize("raw",["null","[]"])
def test_malformed_actual_child_summary_retains_process_receipt(tmp_path,monkeypatch,raw):
    import unary_method_process as P
    from unary_method_profile import observe
    actual=P.subprocess.Popen
    def child(argv,**kwargs):
        code="from pathlib import Path;import sys;p=Path(sys.argv[1]);(p.parent/'rows').mkdir();p.write_text(sys.argv[2]);sys.stdout.write(sys.argv[2])"
        return actual([observe()["executable"],"-I","-S","-B","-c",code,argv[-1],raw],**kwargs)
    monkeypatch.setattr(P.subprocess,"Popen",child)
    deadline=time.monotonic()+10
    out=P.launch(tmp_path/"child","presented_batch",{"rows":rows(),"deadline_monotonic":deadline},
                 arm="exact",profile=observe(),deadline=deadline)
    assert out["terminal"]=="PROCESS_REFUSED" and out["returncode"]==0
    assert out["reaped"] and out["group_absent"]
    assert "ROW_SUMMARY" in out["result_refusal"]
    assert (tmp_path/"child/PROCESS.json").is_file()
