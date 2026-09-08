"""Create-only registered caller entry. No prefix is opened before a root gate."""
from pathlib import Path
import hashlib,json,os,resource,sys,time,traceback
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/"vendor")]
from caller_bindings import raw_identity
from caller_flow import execute,write
from hole_match import require
import life_native as N

def load(path):
    return json.loads(Path(path).read_bytes())
def pin(path):
    p=Path(path);return {"path":str(p),**raw_identity(p.read_bytes())}
def exact(binding):
    require(pin(binding["path"])==binding,"file identity: "+binding["path"])
def main():
    started=time.perf_counter();before=resource.getrusage(resource.RUSAGE_SELF)
    request_path=Path(sys.argv[1]).resolve();request=load(request_path)
    gate_path=Path(request["gate"]);gate=load(gate_path)
    require(gate["schema"]=="ordinary.hole-native-gate.v1" and gate["authorized"] is True,"root gate")
    require(gate["request"]==pin(request_path),"root-bound request")
    require(gate["scope"]=="ONE_AUTHORED_TWO_NATIVE_CALLS_NO_RETRY","root gate scope")
    require(gate["source_freeze"]==request["source_freeze"],"root-bound source freeze")
    exact(request["source_freeze"]);freeze=load(request["source_freeze"]["path"])
    for row in freeze["files"]:exact(row)
    require(pin(sys.executable)==request["python"] and sys.flags.isolated and sys.flags.no_site
            and sys.flags.dont_write_bytecode and not sys.flags.optimize,"isolated pinned runtime")
    require(os.getcwd()==request["cwd"],"registered cwd")
    opening_request=pin(request_path);opening_gate=pin(gate_path);opening_freeze=pin(request["source_freeze"]["path"])
    output=Path(request["output"]);output.mkdir(exist_ok=False)
    outcome={"terminal":"CANNOT_CHECK","native_calls":0}
    try:
        exact(request["definition"]);definition=load(request["definition"]["path"])
        require(definition["schema"]=="ordinary.hole-native-definition.v1"
                and definition["eligible_method_ids"]==[],"noneligible authored definition")
        exact(request["old_prefix"]);exact(request["admission_suffix"])
        raw=Path(request["old_prefix"]["path"]).read_bytes()+b"\n"+Path(request["admission_suffix"]["path"]).read_bytes()
        require(raw_identity(raw)==request["authority"]["prefix"],"exact published extended prefix")
        prefix_path=output/"EXTENDED-PREFIX.mm";N.store(prefix_path,raw)
        write(output/"INPUT-BINDINGS.json",{"request":opening_request,"gate":opening_gate,"freeze":opening_freeze})
        outcome=execute(definition,raw,prefix_path,request["authority"],request["native_sources"],output)
    except Exception as exc:
        outcome["error"]={"type":type(exc).__name__,"message":str(exc)}
        (output/"caller-error.txt").write_text(traceback.format_exc())
    finally:
        try:
            require(pin(request_path)==opening_request and pin(gate_path)==opening_gate
                    and pin(request["source_freeze"]["path"])==opening_freeze,"opening custody retained")
            for row in freeze["files"]:exact(row)
            exact(request["old_prefix"]);exact(request["admission_suffix"])
            if (output/"EXTENDED-PREFIX.mm").exists():
                require(raw_identity((output/"EXTENDED-PREFIX.mm").read_bytes())==request["authority"]["prefix"],"extended prefix retained")
            outcome["custody_unchanged"]=True
        except Exception as exc:
            outcome.update(terminal="CANNOT_CHECK",custody_unchanged=False,custody_error=str(exc))
        after=resource.getrusage(resource.RUSAGE_SELF)
        outcome["process"]={"pid":os.getpid(),"parent_pid":os.getppid(),"cwd":os.getcwd(),"python":sys.executable,
           "imported_modules":{k:str(Path(v.__file__).resolve()) for k,v in sys.modules.items() if getattr(v,"__file__",None)},
           "wall_s":time.perf_counter()-started,"user_cpu_s":after.ru_utime-before.ru_utime,
           "system_cpu_s":after.ru_stime-before.ru_stime,"process_highwater_rss_kib":after.ru_maxrss,
           "scope":"Entry main through post-custody; imports and final RESULT serialization excluded; nested flow/native windows not additive"}
        write(output/"RESULT.json",outcome)
    return 0 if outcome["terminal"]=="AUTHORED_ALIAS_REPLACEMENT_NATIVE_CHECKED" else 2
if __name__=="__main__":raise SystemExit(main())
