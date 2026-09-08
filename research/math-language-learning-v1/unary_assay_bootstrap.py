"""Fixed Python/affinity entry; original STARTED authority is always external."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ROOTS=(ROOT/"src",ROOT/"research/math-language-v1",ROOT/"research/math-language-learning-v1")
for folder in reversed(ROOTS):sys.path.insert(0,str(folder))
import hashlib,os,time,types
import unary_assay_launch_contract as L
import unary_method_outer as D
import unary_method_profile as B

def clock(binding,sources):
    modules={}
    for name in ("resource_contract","resource_deadline"):
        path=ROOT/"research/proof-corpus-coverage-v1"/(name+".py")
        data=path.read_bytes();rel=str(path.relative_to(ROOT))
        if hashlib.sha256(data).hexdigest()!=sources[rel]:raise ValueError("BOOTSTRAP_DEADLINE_SOURCE")
        m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
        exec(compile(data,str(path),"exec"),m.__dict__);modules[name]=m
    return modules["resource_deadline"].Started(binding,[L.WORK])

def observe():
    from unary_assay_probe import observation
    import sysconfig
    roots=(*ROOTS,ROOT/"research/proof-corpus-coverage-v1",Path(sysconfig.get_path("stdlib")).resolve())
    imports={}
    for name,module in sorted(sys.modules.items()):
        source=getattr(module,"__file__",None)
        if not source or source.startswith("<"):continue
        p=Path(source).resolve()
        if not any(p.is_relative_to(r) for r in roots) or "site-packages" in p.parts:raise ValueError("BOOTSTRAP_IMPORT_ORIGIN")
        if p.suffix!=".py":raise ValueError("BOOTSTRAP_NON_SOURCE_IMPORT")
        cached=getattr(module,"__cached__",None)
        if cached and Path(cached).exists():raise ValueError("BOOTSTRAP_CACHED_IMPORT")
        imports[name]=L.stamp(p)
    return {"environment":observation(),"imports":imports}

def main():
    start=time.monotonic();cpu=time.process_time();out={"terminal":"BOOTSTRAP_REFUSED","stage":"ENTRY"};watch=None
    try:
        if ROOT!=Path(L.PROJECT) or len(sys.argv)!=3:raise ValueError("FIXED_BOOTSTRAP_ENTRY")
        seal=L.read(L.SEAL,sys.argv[1]);plan=L.plan(L.read(L.PLAN,seal["plan"]["sha256"]));binding=L.read(L.BINDING,sys.argv[2])
        out["seal_sha256"]=sys.argv[1];out["plan_sha256"]=seal["plan"]["sha256"];out["binding_sha256"]=sys.argv[2]
        if binding["run_id"]!=plan["run_id"] or binding["launch_seal_sha256"]!=sys.argv[1] or binding["duration_ns"]!=plan["duration_ns"]:
            raise ValueError("BOOTSTRAP_CLOCK_AUTHORITY")
        if binding["record"]["path"]!=L.STARTED:raise ValueError("BOOTSTRAP_CLOCK_PATH")
        watch=clock(binding,plan["sources"]);out["external_started"]=watch.receipt
        watch.check("BOOTSTRAP_START");B.verify(plan["python"],actual=True)
        before=D.sources()
        if before!=plan["sources"]:raise ValueError("BOOTSTRAP_SOURCE_BINDING")
        allowed=sorted(os.sched_getaffinity(0));out["allowed_before"]=allowed
        if not allowed or plan["cpu"]!=allowed[0]:raise ValueError("BOOTSTRAP_LOWEST_CPU")
        os.sched_setaffinity(0,{plan["cpu"]})
        if os.sched_getaffinity(0)!={plan["cpu"]}:raise ValueError("BOOTSTRAP_AFFINITY")
        out["before"]=observe();out["stage"]="DISPATCH"
        initial=watch.check("BOOTSTRAP_PREDISPATCH");deadline=initial["deadline_monotonic_ns"]/1e9
        value=None
        if plan["input"] is not None:
            if L.stamp(L.INPUT)["bytes"]!=plan["input"]["bytes"]:raise ValueError("BOOTSTRAP_INPUT_BYTES")
            value=L.read(L.INPUT,plan["input"]["sha256"])
        watch.check("BOOTSTRAP_INPUT_READY")
        if plan["mode"]=="AUTHORED_PROBE":
            from unary_assay_probe import run
            result=run(value,deadline)
        else:
            from unary_assay_coordinator import run,run_authored
            result=(run(L.WORK+"/coordinator",deadline=deadline,profile=B.DEFAULT) if plan["mode"]=="REGISTERED" else
                    run_authored(L.WORK+"/coordinator",value,deadline=deadline,profile=B.DEFAULT))
        if plan["mode"]=="AUTHORED_PROBE":out["outcome"]=result
        else:
            folder=Path(L.WORK)/"coordinator"
            out["outcome"]={"coordinator":L.stamp(folder/"COORDINATOR.json"),
                            "abort":result["abort"],"call_count":len(result["calls"])}
            watch.check("EVALUATOR_RECHECK_START");out["stage"]="EVALUATOR_RECHECK"
            from unary_assay_analysis import analyze
            begin=time.monotonic();used=time.process_time();work={}
            try:
                analysis=analyze(folder,expected_sources=plan["sources"],work=work)
                out["analysis"]=L.write(folder/"ANALYSIS.json",analysis)
            finally:
                out["evaluation_recheck"]={"wall_s":time.monotonic()-begin,
                                          "own_cpu_s":time.process_time()-used,"work":work}
            watch.check("EVALUATOR_RECHECK_END")
        out["stage"]="POST_CUSTODY";out["after"]=observe()
        if D.sources()!=before:raise ValueError("BOOTSTRAP_SOURCE_DRIFT")
        B.verify(plan["python"],actual=True);watch.check("BOOTSTRAP_FINAL")
        out["terminal"]="BOOTSTRAP_COMPLETED"
    except BaseException as exc:
        out["error"]={"class":type(exc).__name__,"message":str(exc)}
    out["wall_before_retention_s"]=time.monotonic()-start;out["own_cpu_before_retention_s"]=time.process_time()-cpu
    L.write(Path(L.WORK)/"BOOTSTRAP.json",out)
    print(D.raw({"terminal":out["terminal"],"stage":out["stage"]}).decode())
    return 0 if out["terminal"]=="BOOTSTRAP_COMPLETED" else 2

if __name__=="__main__":raise SystemExit(main())
