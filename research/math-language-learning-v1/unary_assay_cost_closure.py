"""Data-only physical observations; never promotes semantic or lifetime economics."""
import re
from pathlib import Path
import unary_assay_launch_contract as L

SCHEMA="ocm.unary-phase-process-cost.v1"
FIELDS={"schema","phase","argv","cwd","wrapper","sources_before","sources_after",
        "returncode","error","child_reaped","started_monotonic_ns","ended_monotonic_ns",
        "gnu_time","stdout","stderr","products"}
TIME_FORMAT="wall_s=%e\\nuser_s=%U\\nsystem_s=%S"
SCOPE="GNU time around the phase command, including its product persistence and exit; excludes observer receipt persistence."

def bound(binding,limit=None):
    if type(binding) is not dict or set(binding)!={"path","sha256","bytes"}:raise ValueError("COST_BINDING")
    if type(binding["bytes"]) is not int or binding["bytes"]<0:raise ValueError("COST_BINDING_BYTES")
    if limit is not None and (binding["bytes"]>limit or Path(binding["path"]).lstat().st_size>limit):raise ValueError("COST_INPUT_BOUND")
    if L.stamp(binding["path"])!=binding:raise ValueError("COST_BYTES")
    return binding

def json_binding(path):
    if Path(path).lstat().st_size>L.D.MAX_BYTES:raise ValueError("COST_INPUT_BOUND")
    return L.stamp(path)

def data(binding,*,resource_newline=False):
    bound(binding,L.D.MAX_BYTES)
    if not resource_newline:return L.read(binding["path"],binding["sha256"])
    if binding["bytes"]>L.D.MAX_BYTES:raise ValueError("COST_DATA_BOUND")
    with Path(binding["path"]).open("rb") as f:raw=f.read(L.D.MAX_BYTES+1)
    import hashlib
    if len(raw)!=binding["bytes"] or hashlib.sha256(raw).hexdigest()!=binding["sha256"]:raise ValueError("COST_DATA_CONSUMED")
    if not raw.endswith(b"\n"):raise ValueError("COST_RESOURCE_NEWLINE")
    return L.D.parse(raw[:-1])

def measurement(binding):
    bound(binding,256);p=Path(binding["path"])
    if binding["bytes"]>256:raise ValueError("COST_TIME_BOUND")
    with p.open("rb") as f:raw=f.read(257)
    import hashlib
    if len(raw)!=binding["bytes"] or hashlib.sha256(raw).hexdigest()!=binding["sha256"]:raise ValueError("COST_TIME_CONSUMED")
    match=re.fullmatch(rb"wall_s=([0-9]+\.[0-9]{2})\nuser_s=([0-9]+\.[0-9]{2})\nsystem_s=([0-9]+\.[0-9]{2})\n",raw)
    if match is None:raise ValueError("COST_TIME_FORMAT")
    return {"wall_s":float(match[1]),"reported_user_s":float(match[2]),
            "reported_system_s":float(match[3]),"resolution_s":.01,"raw":binding,
            "cpu_scope":"GNU time waited-process observation; not aggregate namespace CPU."}

def phase(binding,kind,*,sources,wrapper,products):
    value=data(binding)
    if type(value) is not dict or set(value)!=FIELDS or value["schema"]!=SCHEMA or value["phase"]!=kind:raise ValueError("COST_PHASE_SCHEMA")
    if value["wrapper"]!=wrapper:raise ValueError("COST_WRAPPER_AUTHORITY")
    bound(wrapper)
    if value["sources_before"]!=sources or value["sources_after"]!=sources:raise ValueError("COST_SOURCE_BINDING")
    if type(value["argv"]) is not list or not value["argv"] or any(type(x) is not str for x in value["argv"]):raise ValueError("COST_ARGV")
    if not Path(value["argv"][0]).is_absolute() or type(value["cwd"]) is not str or not Path(value["cwd"]).is_absolute():raise ValueError("COST_COMMAND")
    a=value["started_monotonic_ns"];b=value["ended_monotonic_ns"]
    if type(a) is not int or type(b) is not int or not 0<a<=b:raise ValueError("COST_CLOCK")
    if value["products"]!=products:raise ValueError("COST_PRODUCTS")
    for item in products.values():bound(item)
    for key in ("stdout","stderr"):bound(value[key])
    measured=measurement(value["gnu_time"])
    if measured["wall_s"]>(b-a)/1e9+measured["resolution_s"]:raise ValueError("COST_WALL_EXCEEDS_ENCLOSING_SPAN")
    if type(value["returncode"]) is not int or type(value["child_reaped"]) is not bool:raise ValueError("COST_EXIT")
    return {"receipt":binding,"measurement":measured,"clock":[a,b],"returncode":value["returncode"],
            "error":value["error"],"child_reaped":value["child_reaped"],
            "complete":value["returncode"]==0 and value["error"] is None and value["child_reaped"],
            "scope":SCOPE}

def close(prepared,receipts,*,wrapper):
    """Trusted fixed observer binding is supplied before the run, never inferred here."""
    out={"schema":"ocm.unary-outer-cost-closure.v1","terminal":"ECONOMICS_CANNOT_CHECK",
         "wall_terminal":"UNAVAILABLE","phases":{},"earliest_crossing":"UNAVAILABLE",
         "full_cpu_s":None,"full_lifetime_cost":None,
         "reason":"AGGREGATE_AND_OUTSIDE_CPU_OVERLAP_OR_UNOBSERVED_HELPER_CPU",
         "semantic_analysis":"Retained unchanged; no reanalysis or promotion.",
         "scope":"Each physical PREPARATION/LAUNCH observation counted once; nested costs are separate."}
    try:
        ready=data(prepared);root=Path(prepared["path"]).parent
        plan=L.plan(data(ready["plan"]));outer_binding=json_binding(root/"OUTER.json");outer=data(outer_binding)
        if outer["seal"]!=prepared:raise ValueError("COST_PREPARED_AUTHORITY")
        if outer["started"]["state"]!="ISSUED":raise ValueError("COST_STARTED_UNAVAILABLE")
        started=outer["started"]["binding"]["record"];bound(started)
        if outer["started"]["binding"]["launch_seal_sha256"]!=prepared["sha256"]:raise ValueError("COST_STARTED_SEAL")
        bootstrap_binding=outer["bootstrap"];bootstrap=data(bootstrap_binding)
        if bootstrap["seal_sha256"]!=prepared["sha256"]:raise ValueError("COST_BOOTSTRAP_SEAL")
        profile_binding=outer["dispatch"]["receipt"];profile=data(profile_binding,resource_newline=True)
        analysis=bootstrap["analysis"];host_analysis=json_binding(root/"work/coordinator/ANALYSIS.json")
        if analysis!={**host_analysis,"path":L.WORK+"/coordinator/ANALYSIS.json"}:raise ValueError("COST_ANALYSIS_BINDING")
        out["retained_analysis"]=host_analysis
        expected={"PREPARATION":{"PREPARED":prepared},
                  "LAUNCH":{"OUTER":outer_binding,"STARTED":started,"BOOTSTRAP":bootstrap_binding,
                            "BUILD_PROFILE":profile_binding,"ANALYSIS":host_analysis}}
        if type(receipts) is not dict or set(receipts)!=set(expected):raise ValueError("COST_REQUIRED_PHASES")
        for kind in expected:
            out["phases"][kind]=phase(receipts[kind],kind,sources=plan["sources"],wrapper=wrapper,products=expected[kind])
        prep=out["phases"]["PREPARATION"];launch=out["phases"]["LAUNCH"]
        if prep["clock"][1]>launch["clock"][0]:raise ValueError("COST_PHASE_OVERLAP")
        dispatch=profile["dispatch"]
        out["separate_cpu_observations"]={"cgroup_cpuacct_usage_ns":dispatch["final_resources"].get("cpuacct.usage"),
            "outside_usage_before":outer["usage_before"],"outside_usage_after":outer["usage_after"],
            "evaluation_recheck":bootstrap.get("evaluation_recheck")}
        out["observer_retention_and_between_phase_work"]="UNAVAILABLE; not silently included in the measured phase sum."
        if all(x["complete"] for x in out["phases"].values()):
            out["wall_terminal"]="OBSERVED_PHASE_PROCESS_WALL"
            out["phase_process_wall_sum_s"]=sum(x["measurement"]["wall_s"] for x in out["phases"].values())
            out["wall_resolution_s_per_phase"]=.01
    except (OSError,ValueError,KeyError,TypeError) as exc:
        out["observation_error"]={"class":type(exc).__name__,"message":str(exc)}
    return out
