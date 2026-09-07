"""Authored process entry. Isolation flags are not a host containment claim."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ROOTS=(ROOT/"src",ROOT/"research/math-language-v1",ROOT/"research/math-language-learning-v1")
for folder in reversed(ROOTS):sys.path.insert(0,str(folder))
import hashlib,os,sysconfig,time
from unary_contract import InputRefused,fields
import unary_method_outer as D
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

def run(mode,value,*,arm="ocm",observation=None,row_sink=None):
    from unary_method_arm import run as dispatch
    return dispatch(arm,mode,value,observation=observation,row_sink=row_sink)


def main():
    start=time.monotonic();result={};out=None
    try:
        from unary_method_arm import MODES
        if len(sys.argv)!=4 or sys.argv[1] not in MODES:raise InputRefused("ARGV")
        mode=sys.argv[1];out=Path(sys.argv[3]);arm=os.environ.get("OCM_UNARY_ARM","ocm")
        if arm not in ("ocm","conventional","exact"):raise InputRefused("PROCESS_ARM")
        if out.exists():raise InputRefused("CREATE_ONLY_RESULT")
        profile=B.validate(D.parse(os.environ["OCM_UNARY_PYTHON_PROFILE"].encode()))
        result["profile"]=profile;python=B.verify(profile,actual=True)
        before=D.sources();origins=imported();input_bytes=Path(sys.argv[2]).read_bytes()
        result={"arm":arm,"profile":profile,"mode":mode,"input_sha256":hashlib.sha256(input_bytes).hexdigest(),"source_before":before,
                "python":python,"pid":os.getpid(),"argv":sys.argv,
                "flags":{"isolated":sys.flags.isolated,"no_site":sys.flags.no_site,"dont_write_bytecode":sys.flags.dont_write_bytecode}}
        value=D.parse(input_bytes)
        if mode=="presented_batch":
            from unary_assay_service import remaining
            deadline=D.parse(os.environ["OCM_UNARY_DEADLINE"].encode());remaining(deadline)
            if value.get("deadline_monotonic")!=deadline:raise InputRefused("PRESENTED_CHILD_DEADLINE")
            result["deadline_monotonic"]=deadline
        sink=None
        if mode=="presented_batch":
            from unary_assay_rows import Writer
            sink=Writer(out.parent)
        result["active_observation"]={}
        result.update(run(mode,value,arm=arm,observation=result["active_observation"],row_sink=sink))
        if mode=="presented_batch":
            result["active_observation"]={"detail_location":"outcome","stage":result["outcome"]["stage"],
                                          "rows_recorded":len(result["outcome"]["rows"])}
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
