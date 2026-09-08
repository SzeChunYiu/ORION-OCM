"""One fixed external issuance/dispatch path around the existing resource controller."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for folder in reversed((ROOT/"src",ROOT/"research/math-language-v1",ROOT/"research/math-language-learning-v1")):sys.path.insert(0,str(folder))
import hashlib,os,resource,time
import unary_assay_launch_contract as L
import unary_assay_launch_profile as P
import unary_method_outer as D

def usage():
    own=resource.getrusage(resource.RUSAGE_SELF);child=resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"own_user_s":own.ru_utime,"own_system_s":own.ru_stime,
            "child_user_s":child.ru_utime,"child_system_s":child.ru_stime,
            "own_peak_rss_kib":own.ru_maxrss,"child_peak_rss_kib":child.ru_maxrss}

def launch(prepared_binding):
    start=time.monotonic();initial=usage();root=Path(prepared_binding["path"]).parent
    out={"schema":"ocm.unary-launch-observation.v1","terminal":"LAUNCH_REFUSED","stage":"PREFLIGHT",
         "started":None,"dispatch":None,"usage_before":initial,"seal":prepared_binding}
    try:
        ready=L.read(prepared_binding["path"],prepared_binding["sha256"])
        if L.stamp(Path(prepared_binding["path"]))!=prepared_binding:raise ValueError("PREPARED_RECORD")
        if set(ready)!={"schema","plan","template","driver_sources","review","limits","stdlib_copy","preparation_wall_s","preparation_own_cpu_s"}:
            raise ValueError("PREPARED_FIELDS")
        if ready["schema"]!="ocm.unary-launch-prepared.v1" or ready["limits"]!=L.LIMITS:raise ValueError("FIXED_LAUNCH_LIMITS")
        plan=L.plan(L.read(ready["plan"]["path"],ready["plan"]["sha256"]))
        modules,sources=P.resources()
        if sources!=ready["driver_sources"] or D.sources()!=plan["sources"]:raise ValueError("LAUNCH_SOURCE_DRIFT")
        if plan["cpu"]!=min(os.sched_getaffinity(0)):raise ValueError("LAUNCH_LOWEST_CPU")
        L.read(ready["review"]["path"],ready["review"]["sha256"])
        profile=D.parse(D.raw(ready["template"]))
        modules["build_profile_policy"].verify_inventory(profile["materials"][0]["path"],
            L.read(profile["materials"][0]["inventory"]["path"],profile["materials"][0]["inventory"]["sha256"]))
        # Inputs and copied executable/runtime material are checked before clock issuance.
        for f in profile["files"]:modules["resource_contract"].verify(f["source"])
        for d in profile["materials"]:
            modules["build_profile_policy"].verify_inventory(d["path"],L.read(d["inventory"]["path"],d["inventory"]["sha256"]))
        for k in ("bwrap","aa_exec"):modules["resource_contract"].verify(profile[k])
        if root.resolve(strict=True)!=root or (root/"STARTED.json").exists() or (root/"OUTER.json").exists():
            raise ValueError("CREATE_ONLY_LAUNCH")
        boot=modules["resource_deadline"].boot_id();now=time.monotonic_ns();out["stage"]="STARTED_ISSUANCE"
        value={"schema":"ocm.unary-started.v1","run_id":plan["run_id"],"boot_id":boot,
               "started_monotonic_ns":now,"deadline_monotonic_ns":now+plan["duration_ns"],
               "launch_seal_sha256":prepared_binding["sha256"]}
        # resource_deadline's canonical record includes a trailing newline.
        out["started"]={"state":"ISSUANCE_ATTEMPTED","value":value,"bytes_written":False,"directory_fsynced":False}
        raw=modules["resource_contract"].canonical(value);p=root/"STARTED.json"
        with p.open("xb") as f:f.write(raw);f.flush();os.fsync(f.fileno())
        out["started"]["bytes_written"]=True
        L.sync_dir(root);out["started"]["directory_fsynced"]=True
        binding={"schema":"ocm.unary-external-deadline.v1","record":L.stamp(p),"run_id":plan["run_id"],
                 "launch_seal_sha256":prepared_binding["sha256"],"duration_ns":plan["duration_ns"]}
        out["started"].update(state="ISSUED",binding=binding);out["stage"]="PROFILE_PREPARATION"
        bound=L.write(root/"BINDING.json",L.guest_binding(binding))
        profile["argv"][-2:]=[prepared_binding["sha256"],bound["sha256"]]
        profile["files"] += [{"source":binding["record"],"guest":L.STARTED,"access":"read"},
            {"source":bound,"guest":L.BINDING,"access":"read"},{"source":prepared_binding,"guest":L.SEAL,"access":"read"}]
        audit={"schema":"ocm.f1.build-code-audit.v1","profile_payload_sha256":hashlib.sha256(modules["resource_contract"].canonical(profile)).hexdigest(),
          "non_neural_code_reviewed":True,"dynamic_code_scope":"REGISTERED_EXEC_AND_FILE_MAPPING_ONLY",
          "evidence":[ready["review"],prepared_binding],
          "limitations":"Fixed reviewed source/Python namespace only; explicit external review binding. No whole-host or empirical learning claim."}
        profile["code_audit"]=L.write(root/"CODE-AUDIT.json",audit)
        out["profile"]=L.write(root/"PROFILE.json",profile);out["stage"]="CONTROLLER"
        result=modules["build_profile"].run(profile,L.LIMITS,root/"controller",external_started=binding)
        out["dispatch"]={"terminal":result["terminal"],"receipt":L.stamp(root/"controller/build-profile-receipt.json")}
        out["stage"]="POST_CUSTODY"
        if D.sources()!=plan["sources"] or P.resources()[1]!=sources:raise ValueError("LAUNCH_FINAL_SOURCE_DRIFT")
        if L.stamp(p)!=binding["record"]:raise ValueError("LAUNCH_FINAL_STARTED_DRIFT")
        if result["terminal"]!="COMPLETED":raise ValueError("CONTROLLER_"+result["terminal"])
        out["bootstrap"]=L.stamp(root/"work/BOOTSTRAP.json")
        child=L.read(out["bootstrap"]["path"],out["bootstrap"]["sha256"])
        if child.get("terminal")!="BOOTSTRAP_COMPLETED":raise ValueError("BOOTSTRAP_RESULT")
        out["terminal"]="LAUNCH_COMPLETED"
    except BaseException as exc:
        if out["started"] is not None and out["started"]["state"]=="ISSUANCE_ATTEMPTED":
            out["started"]["state"]="ISSUANCE_UNCERTAIN"
        out["error"]={"class":type(exc).__name__,"message":str(exc)}
    out["usage_after"]=usage();out["wall_before_outer_retention_s"]=time.monotonic()-start
    out["cost_scope"]="Invocation through this observation; excludes its own final retention and caller return. External process receipt closes lifetime."
    L.write(root/"OUTER.json",out)
    return out

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit(2)
    path=Path(sys.argv[1]);binding=L.stamp(path)
    if binding["sha256"]!=sys.argv[2]:raise SystemExit("PREPARED_HASH")
    result=launch(binding);print(D.raw({"terminal":result["terminal"],"stage":result["stage"]}).decode())
    raise SystemExit(0 if result["terminal"]=="LAUNCH_COMPLETED" else 2)
