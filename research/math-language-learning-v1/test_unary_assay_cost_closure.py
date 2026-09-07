"""Authored physical observations; no study inputs or launcher execution."""
from pathlib import Path
import pytest
import unary_assay_cost_closure as C
import unary_assay_launch_contract as L
from test_unary_assay_namespace import sample

def fixture(root):
    def put(name,value):return L.write(root/name,value)
    wrapper=put("wrapper.py",{"authored":"fixed observer placeholder"})
    plan=put("PLAN.json",sample());prepared=put("PREPARED.json",{"plan":plan})
    started=put("STARTED.json",{"authored":"issued"})
    (root/"work/coordinator").mkdir(parents=True)
    analysis=put("work/coordinator/ANALYSIS.json",{"apparatus":{"terminal":"CANNOT_CHECK"}})
    bootstrap=put("work/BOOTSTRAP.json",{"seal_sha256":prepared["sha256"],
        "analysis":{**analysis,"path":L.WORK+"/coordinator/ANALYSIS.json"},"evaluation_recheck":{"own_cpu_s":.4}})
    profile_path=root/"profile.json"
    profile_path.write_bytes(L.D.raw({"dispatch":{"final_resources":{"cpuacct.usage":5000000000}}})+b"\n")
    profile=L.stamp(profile_path)
    outer=put("OUTER.json",{"seal":prepared,"started":{"state":"ISSUED","binding":{"record":started,
        "launch_seal_sha256":prepared["sha256"]}},"bootstrap":bootstrap,"dispatch":{"receipt":profile},
        "usage_before":{"own_user_s":1,"child_user_s":2},"usage_after":{"own_user_s":3,"child_user_s":4}})
    products={"PREPARATION":{"PREPARED":prepared},"LAUNCH":{"OUTER":outer,"STARTED":started,
        "BOOTSTRAP":bootstrap,"BUILD_PROFILE":profile,"ANALYSIS":analysis}}
    values={};receipts={}
    for i,kind in enumerate(products):
        p=root/(kind+".time");p.write_bytes(b"wall_s=12.34\nuser_s=1.23\nsystem_s=0.45\n")
        stdout=put(kind+".out",{});stderr=put(kind+".err",{})
        value={"schema":C.SCHEMA,"phase":kind,"argv":["/authored/python","fixed.py"],"cwd":str(root),
            "wrapper":wrapper,"sources_before":sample()["sources"],"sources_after":sample()["sources"],
            "returncode":0,"error":None,"child_reaped":True,"started_monotonic_ns":1+i*14000000000,"ended_monotonic_ns":13000000000+i*14000000000,
            "gnu_time":L.stamp(p),"stdout":stdout,"stderr":stderr,"products":products[kind]}
        values[kind]=value;receipts[kind]=put(kind+".json",value)
    return prepared,receipts,wrapper,values

def test_bound_resource_newline_and_clean_scope(tmp_path):
    prepared,receipts,wrapper,_=fixture(tmp_path)
    out=C.close(prepared,receipts,wrapper=wrapper)
    assert "observation_error" not in out
    assert out["wall_terminal"]=="OBSERVED_PHASE_PROCESS_WALL"
    assert out["phase_process_wall_sum_s"]==24.68
    assert out["terminal"]=="ECONOMICS_CANNOT_CHECK" and out["full_cpu_s"] is None
    assert out["earliest_crossing"]=="UNAVAILABLE"
    assert out["separate_cpu_observations"]["cgroup_cpuacct_usage_ns"]==5000000000
    assert C.data(out["retained_analysis"])=={"apparatus":{"terminal":"CANNOT_CHECK"}}

@pytest.mark.parametrize("fault",["source","wrapper","products","phase","clock","exit","cleanup","missing","time","stdout"])
def test_exact_observer_bindings_and_partial_failure(tmp_path,fault):
    prepared,receipts,wrapper,values=fixture(tmp_path);value=values["LAUNCH"]
    if fault=="source":value["sources_after"]={}
    elif fault=="wrapper":value["wrapper"]=L.write(tmp_path/"other",{})
    elif fault=="products":value["products"]={}
    elif fault=="phase":value["phase"]="PREPARATION"
    elif fault=="clock":value["started_monotonic_ns"]=50
    elif fault=="exit":value["returncode"]=7
    elif fault=="cleanup":value["child_reaped"]=False
    elif fault=="missing":receipts.pop("LAUNCH")
    elif fault=="time":
        p=tmp_path/"bad-time";p.write_bytes(b"wall_s=NaN\nuser_s=1.23\nsystem_s=0.45\n");value["gnu_time"]=L.stamp(p)
    else:Path(value["stdout"]["path"]).write_bytes(b"changed")
    if fault!="missing":receipts["LAUNCH"]=L.write(tmp_path/"changed.json",value)
    out=C.close(prepared,receipts,wrapper=wrapper)
    assert out["wall_terminal"]=="UNAVAILABLE" and out["terminal"]=="ECONOMICS_CANNOT_CHECK"
    if fault in ("exit","cleanup"):
        assert out["phases"]["LAUNCH"]["measurement"]["wall_s"]==12.34
        assert not out["phases"]["LAUNCH"]["complete"]

def test_original_analysis_drift_refuses_without_reanalysis(tmp_path):
    prepared,receipts,wrapper,_=fixture(tmp_path)
    Path(tmp_path/"work/coordinator/ANALYSIS.json").write_bytes(b'{"apparatus":{"terminal":"PASS"}}')
    out=C.close(prepared,receipts,wrapper=wrapper)
    assert out["observation_error"]["message"]=="COST_ANALYSIS_BINDING"
    assert out["terminal"]=="ECONOMICS_CANNOT_CHECK"

@pytest.mark.parametrize("fault",["impossible_span","malformed_profile"])
def test_wall_positive_requires_all_retained_obligations(tmp_path,fault):
    prepared,receipts,wrapper,values=fixture(tmp_path)
    launch=values["LAUNCH"]
    if fault=="impossible_span":launch["ended_monotonic_ns"]=launch["started_monotonic_ns"]+98
    else:
        path=tmp_path/"profile.json";path.write_bytes(b"{}\n");profile=L.stamp(path)
        outer=C.data(launch["products"]["OUTER"]);outer["dispatch"]["receipt"]=profile
        path=tmp_path/"OUTER.json";path.write_bytes(L.D.raw(outer))
        launch["products"].update(OUTER=L.stamp(path),BUILD_PROFILE=profile)
    receipts["LAUNCH"]=L.write(tmp_path/"changed.json",launch)
    result=C.close(prepared,receipts,wrapper=wrapper)
    assert result["wall_terminal"]=="UNAVAILABLE"
    assert "observation_error" in result

@pytest.mark.parametrize("kind",["data","time"])
def test_oversized_cost_input_refused_before_open(tmp_path,monkeypatch,kind):
    path=tmp_path/"large";path.write_bytes(b"x"*((L.D.MAX_BYTES+1) if kind=="data" else 257))
    binding=L.stamp(path);original=Path.open
    def opened(p,*args,**kwargs):
        if p==path:raise AssertionError("cost reader opened oversized input")
        return original(p,*args,**kwargs)
    monkeypatch.setattr(Path,"open",opened)
    with pytest.raises(ValueError,match="BOUND"):
        (C.data if kind=="data" else C.measurement)(binding)

@pytest.mark.parametrize("name",["OUTER.json","work/coordinator/ANALYSIS.json"])
def test_close_bounds_dynamic_json_before_open(tmp_path,monkeypatch,name):
    prepared,receipts,wrapper,_=fixture(tmp_path)
    path=tmp_path/name;path.write_bytes(b"x"*(L.D.MAX_BYTES+1));original=Path.open
    def opened(p,*args,**kwargs):
        if p==path:raise AssertionError("dynamic cost JSON opened before bound")
        return original(p,*args,**kwargs)
    monkeypatch.setattr(Path,"open",opened)
    result=C.close(prepared,receipts,wrapper=wrapper)
    assert result["observation_error"]["message"]=="COST_INPUT_BOUND"
    assert result["wall_terminal"]=="UNAVAILABLE"
