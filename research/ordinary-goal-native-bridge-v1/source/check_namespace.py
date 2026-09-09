"""One affected source-bound namespace control; no search or native invocation."""
from pathlib import Path
import hashlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/"vendor")]
from authored_fixture import bundle,restore,SUFFIX,native_text
started=time.perf_counter();record={"id":"reserved_emitter_namespace","passed":False}
try:
    clean=restore(bundle());assert clean.cohort_labels==["learned-cut"]
    reasons=[]
    for label in ("search-hyp-0","cut-f0"):
        b=bundle(suffix=native_text(SUFFIX.replace("learned-cut",label)))
        try:restore(b)
        except ValueError as exc:
            assert str(exc)=="private proof-label namespace collision";reasons.append(str(exc))
        else:raise AssertionError("collision accepted")
    record.update(passed=True,refusals=reasons,clean_cohort=clean.cohort_labels)
except BaseException as exc:record.update(error=str(exc),traceback=traceback.format_exc())
record["wall_s"]=time.perf_counter()-started
result={"passed":record["passed"],"tests_run":1,"tests":[record["id"]],"records":[record],"native_calls":0,
        "pid":os.getpid(),"parent_pid":os.getppid(),"cwd":os.getcwd(),"python":sys.executable,
        "imported_modules":{n:str(Path(m.__file__).resolve()) for n,m in sorted(sys.modules.items()) if getattr(m,"__file__",None)},
        "scope":"Authored source-index namespace refusal only; no search, native verifier or retained data."}
with Path(sys.argv[1]).open("x") as f:f.write(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
print(json.dumps({"passed":result["passed"]}))
raise SystemExit(0 if result["passed"] else 1)
