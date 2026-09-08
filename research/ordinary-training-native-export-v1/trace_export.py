"""Future gated isolated entry; missing pins refuse before reading any prefix."""
import hashlib,json,os,resource,sys,time,types
from pathlib import Path
HERE=Path(__file__).resolve().parent
NAMES=("trace_export.py","bound_io.py","request_contract.py","population.py","native_export.py",
       "packet_export.py","trace_transport.py","donor/trace_source.py","donor/trace_adapter.py")
def ident(raw):return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def bootstrap(name,expected):
    path=HERE/name;raw=path.read_bytes()
    if ident(raw)!=expected:raise ValueError("bootstrap binding")
    module=types.ModuleType(name[:-3]);module.__file__=str(path)
    exec(compile(raw,str(path),"exec"),module.__dict__);return module

def main(request_path,output):
    started=time.monotonic();created=False;B=None;req=None;journal=None;opened={}
    result={"schema":"ordinary.training-trace-export-process.v2","terminal":"STARTING",
        "pid":os.getpid(),"ppid":os.getppid(),"cwd":os.getcwd(),"entry_file":str(Path(__file__).resolve()),
        "python_executable":sys.executable,"argv":sys.argv,"native_calls":0,"prefix_read":False,
        "native_module_loaded":False,"gate_read":False,"roots":[],"opportunity_calls":0,"learner_calls":0}
    try:
        output.mkdir();created=True
        request_raw=request_path.read_bytes();early=json.loads(request_raw)
        before={n:ident((HERE/n).read_bytes()) for n in NAMES}
        result.update(request=ident(request_raw),sources_before=before)
        if early.get("sources")!=before:raise ValueError("exact source population/freeze required")
        B=bootstrap("bound_io.py",before["bound_io.py"])
        C=B.load(HERE/"request_contract.py",before["request_contract.py"],"export_request_contract")
        result["imported_helpers"]={"bound_io":B.__file__,"request_contract":C.__file__}
        req=B.loads(request_raw);C.validate_request(req)
        gate_raw=Path(req["gate_path"]).read_bytes();result["gate_read"]=True
        gate=B.loads(gate_raw)
        if gate.get("authorization")!="ROOT_TRAINING_NATIVE_EXPORT_GATE" or gate.get("request")!=ident(request_raw):
            raise ValueError("native export gate absent or unbound")
        if gate.get("observer_contract")!=req["observer_contract"]:raise ValueError("separate observer contract")
        if sys.executable!=req["python"]["path"] or not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
            raise ValueError("requires bound interpreter -I -S without optimization")
        for key in ("python","verifier","release","registry_scope","authority_contract","observer_contract","P0_contracts"):
            opened[key]=B.read_bound(req[key])
        release=B.loads(opened["release"]);C.validate_release(release,req)
        registry=B.loads(opened["registry_scope"])
        if registry.get("schema")!="ordinary.registry-scope.v2" or registry.get("coverage")!="DECLARED_REGISTRY_UNIVERSE_ONLY":
            raise ValueError("declared registry scope required; no universal clearance")
        C.validate_authority(B.loads(opened["authority_contract"]),req,release)
        result["roots"]=[{k:r[k] for k in ("ordinal","label","source_disposition")} for r in release["roots"]]
        B.write(output/"REQUEST.json",req)
        raw=B.read_bound(req["prefix"]);opened["prefix"]=raw;result["prefix_read"]=True
        S=B.load(HERE/"donor/trace_source.py",before["donor/trace_source.py"],"export_trace_source")
        T=B.load(HERE/"donor/trace_adapter.py",before["donor/trace_adapter.py"],"export_trace_adapter")
        P=B.load(HERE/"population.py",before["population.py"],"export_population")
        rows,proofs=P.bind_population(raw,release,S,T)
        base=B.loads(opened["P0_contracts"]);P.validate_base(base,rows,proofs,S)
        native=B.load(Path(req["verifier"]["path"]),ident(opened["verifier"]),"ocm_bound_mmverify")
        result["native_module_loaded"]=True;native.verbosity=2;native.logfile=sys.stderr
        E=B.load(HERE/"native_export.py",before["native_export.py"],"export_native_session")
        journal=(output/"CUSTODIAN-PROGRESS.jsonl").open("xb")
        def progress(value):journal.write(B.canonical(value));journal.flush()
        released={r["label"] for r in release["roots"] if r["source_disposition"]=="RELEASED"}
        verified,error=E.verify_prefix(native,T,rows,raw,req["prefix"]["path"],released,progress)
        result.update(native_calls=verified.native_calls,verified_count=len(verified.verified),native_error=error)
        if error is not None:raise ValueError("fresh full-prefix verification failed")
        observed,trace_error=E.observe_traces(native,T,rows,raw,req["prefix"]["path"],released,progress)
        result.update(native_calls=verified.native_calls+observed.native_calls,trace_error=trace_error,
                      trace_unusable=observed.unusable,trace_ready_labels=sorted(observed.traces))
        K=B.load(HERE/"packet_export.py",before["packet_export.py"],"export_packet")
        U=B.load(HERE/"trace_transport.py",before["trace_transport.py"],"export_transport")
        artifacts=K.assemble(req,release,rows,proofs,base,verified,observed,trace_error,S,P,B,U)
        if request_path.read_bytes()!=request_raw or Path(req["gate_path"]).read_bytes()!=gate_raw:raise ValueError("request/gate drift")
        if B.snapshot(HERE,NAMES)!=before or any(B.read_bound(req[k])!=v for k,v in opened.items()):raise ValueError("source/input drift")
        result["artifacts"]=K.emit(output,*artifacts,base,B)
        result["trace_ready_labels"]=[r["label"] for r in artifacts[2]["roots"] if r["trace_disposition"]=="TRACE_READY"]
        result["roots"]=[{k:r[k] for k in ("ordinal","label","source_disposition","trace_disposition")} for r in artifacts[2]["roots"]]
        result["terminal"]="FRESH_NATIVE_EXPORT_CANDIDATE_REQUIRES_ROOT_QUALIFICATION"
    except BaseException as exc:
        result.update(terminal="EXPORT_REFUSED_OR_FAILED",error={"type":type(exc).__name__,"message":str(exc)})
        for row in result["roots"]:row.setdefault("trace_disposition","NOT_EXPORTED_FAILURE")
    finally:
        if journal is not None:journal.close()
        result.update(wall_s=time.monotonic()-started,cpu_user_s=resource.getrusage(resource.RUSAGE_SELF).ru_utime,
                      cpu_system_s=resource.getrusage(resource.RUSAGE_SELF).ru_stime,
                      maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        try:result["sources_after"]={n:ident((HERE/n).read_bytes()) for n in NAMES}
        except BaseException as exc:result["custody_error"]=str(exc)
        if created:
            with (output/"RESULT.json").open("xb") as stream:
                stream.write((json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n").encode())
        print(json.dumps({k:result[k] for k in ("terminal","pid","native_calls","prefix_read","native_module_loaded")}))
    return 0 if result["terminal"]=="FRESH_NATIVE_EXPORT_CANDIDATE_REQUIRES_ROOT_QUALIFICATION" else 1

if __name__=="__main__":raise SystemExit(main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve()))
