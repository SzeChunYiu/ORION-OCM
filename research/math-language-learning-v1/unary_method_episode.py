"""Authored process entry. Isolation flags are not a host containment claim."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ROOTS=(ROOT/"src",ROOT/"research/math-language-v1",ROOT/"research/math-language-learning-v1")
for folder in reversed(ROOTS):sys.path.insert(0,str(folder))
import hashlib,os,sysconfig,time
from ocm.runtime.ocm_runtime import OCMRuntime
from unary_contract import InputRefused,fields
from unary_method_store import MethodStore
from unary_method_runtime import MethodRuntime
import unary_method_data as D
import unary_method_profile as B


def identity(path):
    data=Path(path).read_bytes()
    return {"path":str(Path(path).resolve()),"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}

def imported():
    result={};stdlib=Path(sysconfig.get_path("stdlib")).resolve()
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,"__file__",None)
        if path is None or path.startswith("<"):continue
        p=Path(path).resolve()
        if not any(p.is_relative_to(r) for r in (*ROOTS,stdlib)):raise InputRefused("UNDECLARED_IMPORT_ORIGIN")
        if "site-packages" in p.parts:raise InputRefused("EXTERNAL_PACKAGE_IMPORT")
        cached=getattr(module,"__cached__",None)
        if cached and Path(cached).is_file() and any(p.is_relative_to(r) for r in ROOTS):
            raise InputRefused("CACHED_PROJECT_CODE")
        result[name]=identity(p)
    return result

def run(mode,value):
    fields(value,("store","training") if mode=="acquire" else ("store","task","invoke"))
    if type(value["store"]) is not str:raise InputRefused("STORE_PATH")
    path=Path(value["store"])
    if not path.is_absolute() or path.is_symlink():raise InputRefused("STORE_PATH")
    if mode=="acquire" and path.exists():raise InputRefused("CREATE_ONLY_STORE")
    if mode=="solve" and not (path/"unary-method-journal/ledger.jsonl").is_file():
        raise InputRefused("MISSING_ISSUER_JOURNAL")
    rt=OCMRuntime(path);store=MethodStore(rt,create=mode=="acquire")
    # Restored metadata may contain a refusal stub; explicit host callbacks are counted separately.
    callbacks=len(rt._host_operators)
    prior=len(store.uses)
    outcome=store.acquire(value["training"]) if mode=="acquire" else MethodRuntime(store).solve(value["task"],invoke=value["invoke"])
    begin=time.monotonic();rt.persist();persist=time.monotonic()-begin
    return {"outcome":outcome,"callbacks_on_restore":callbacks,"prior_uses":prior,
            "work":dict(store.work),"persist_wall_s":persist,"core_head":rt.events[-1].event_hash,
            "issuer_head":store.head}

def main():
    start=time.monotonic();result={};out=None
    try:
        if len(sys.argv)!=4 or sys.argv[1] not in ("acquire","solve"):raise InputRefused("ARGV")
        mode=sys.argv[1];out=Path(sys.argv[3])
        if out.exists():raise InputRefused("CREATE_ONLY_RESULT")
        profile=B.validate(D.parse(os.environ["OCM_UNARY_PYTHON_PROFILE"].encode()))
        result["profile"]=profile;python=B.verify(profile,actual=True)
        before=D.sources();origins=imported();input_bytes=Path(sys.argv[2]).read_bytes()
        result={"profile":profile,"mode":mode,"input_sha256":hashlib.sha256(input_bytes).hexdigest(),"source_before":before,
                "python":python,"pid":os.getpid(),"argv":sys.argv,
                "flags":{"isolated":sys.flags.isolated,"no_site":sys.flags.no_site,"dont_write_bytecode":sys.flags.dont_write_bytecode}}
        result.update(run(mode,D.parse(input_bytes)))
        result["imports"]=imported();result["source_after"]=D.sources()
        B.verify(profile,actual=True)
        if before!=result["source_after"]:raise InputRefused("SOURCE_DRIFT")
        result["terminal"]="COMPLETED";result["reason"]="AUTHORED_PROCESS_EXECUTION"
    except Exception as exc:
        result.update(terminal="CANNOT_CHECK",reason=type(exc).__name__+": "+str(exc))
    result["process_wall_s"]=time.monotonic()-start
    raw=D.raw(result)
    if out is not None:
        with out.open("xb") as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    sys.stdout.buffer.write(raw);sys.stdout.buffer.flush()
    return 0 if result["terminal"]=="COMPLETED" else 2

if __name__=="__main__":raise SystemExit(main())
