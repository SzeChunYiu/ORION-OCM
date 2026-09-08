"""Pinned local I/O and imports; no proof, bridge or learning at import time."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys,time
HERE=Path(__file__).resolve().parent
IO={"read_operations":0,"bytes_read":0,"write_operations":0,"bytes_written":0}
ACTIVE_WORK={}
AUDIT_READS=None


def require(ok,why):
    if not ok:raise ValueError(why)


def raw(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()


def digest(value):return hashlib.sha256(raw(value)).hexdigest()


def bytes_read(path):
    body=Path(path).read_bytes();IO["read_operations"]+=1;IO["bytes_read"]+=len(body)
    return body


def identity(path):
    body=bytes_read(path)
    return {"bytes":len(body),"sha256":hashlib.sha256(body).hexdigest()}


def read(path):return json.loads(bytes_read(path))


def checked(path,pin):
    require(identity(path)==pin,"FILE_BINDING_CHANGED")
    value=read(path)
    require(identity(path)==pin,"FILE_CHANGED_DURING_READ")
    return value


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("xb") as stream:
        body=raw(value)+b"\n";stream.write(body);stream.flush();os.fsync(stream.fileno())
        IO["write_operations"]+=1;IO["bytes_written"]+=len(body)
    return identity(path)


def bump(work,key,value=1):work[key]=work.get(key,0)+value


def freeze():
    return read(HERE/"SOURCE-FREEZE.json")


def check_sources(role="supervisor",expected_freeze=None):
    if expected_freeze is not None:require(identity(HERE/"SOURCE-FREEZE.json")==expected_freeze,"FREEZE_CHANGED")
    frozen=freeze()
    for relative,pin in frozen["sources"].items():
        require(identity(HERE/relative)==pin,"SOURCE_CHANGED:"+relative)
    for relative,pin in frozen["inputs"].items():
        if role=="B" and relative not in frozen["b_inputs"]:continue
        require(identity(HERE/relative)==pin,"INPUT_CHANGED:"+relative)
    if expected_freeze is not None:require(identity(HERE/"SOURCE-FREEZE.json")==expected_freeze,"FREEZE_CHANGED_DURING_CHECK")
    return frozen


def gate(role="supervisor"):
    entry=read(HERE/"EXECUTION-GATE.json")
    require(entry["authorization"]=="ROOT_GATE_OPEN","EXECUTION_GATE_CLOSED")
    request=checked(HERE/"RUN-REQUEST.json",entry["request"])
    require(identity(HERE/"SOURCE-FREEZE.json")==request["source_freeze"],"FREEZE_CHANGED")
    require(Path(sys.executable).resolve()==Path(request["python"]).resolve() and
            identity(sys.executable)==request["python_identity"],"PYTHON_IDENTITY")
    require(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,"PYTHON_FLAGS")
    check_sources(role,request["source_freeze"])
    return request


def load(name,relative):
    path=HERE/relative
    require(identity(path)==freeze()["sources"][relative],"IMPORT_SOURCE_CHANGED")
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module


def engine():
    location=str(HERE/"engine")
    if location not in sys.path:sys.path.insert(0,location)
    return {name:load(name,"engine/"+name+".py") for name in
            ["typed_context","typed_constructor","typed_extract","typed_emit","typed_grammar","typed_alias"]}


def native_configuration():
    inputs=read(HERE/"SOURCE-INPUTS-01.json")
    files={row["destination"]:row for row in inputs["files"]}
    bindings={}
    for key,name in [("index","trace_source.py"),("adapter","trace_adapter.py"),("verifier","mmverify.py")]:
        row=files["authority/"+name]
        bindings[key]={"path":str(HERE/row["destination"]),**{k:row[k] for k in ("bytes","sha256")}}
    prefix={k:files["inputs/PREFIX.mm"][k] for k in ("bytes","sha256")}
    authority={"prefix":prefix,"trusted_assertions_sha256":inputs["trusted_assertions_sha256"],
               "trusted_assertion_count":inputs["trusted_assertion_count"],
               "prefix_proof_count":inputs["expected_prefix_proofs"]}
    return bindings,authority


def native(claims,archive,work,suffix=None):
    checker=load("life_native","life_native.py");bindings,authority=native_configuration()
    start=time.monotonic();bump(work,"native_wrapper_invocations")
    try:
        result=checker.verify(HERE/"inputs/PREFIX.mm",claims,archive,bindings,authority,suffix)
    except Exception:
        bump(work,"native_wrapper_unreturned")
        bump(work,"native_calls_unresolved_invocations")
        raise
    finally:bump(work,"native_wrapper_wall_s",time.monotonic()-start)
    bump(work,"native_calls",result["native_calls"])
    require(result["claims_sha256"]==digest(claims),"NATIVE_REQUEST_BINDING")
    return result


def parameters(source):
    return [{"type":h["statement"][0],"variable":h["statement"][1],"floating_label":h["label"]}
            for h in source["floating"]]


def claim(label,target,holes,proof,context):
    return {"label":label,"premises":[h["statement"] for h in holes],"query":target,
            "holes":[h["label"] for h in holes],"proof":proof,"parameters":context}


def invocation(main,role="A"):
    output=Path(sys.argv[1]);created=False
    try:
        output.mkdir(exist_ok=False);created=True
        opening_request=gate(role)
        result=main(output)
        result["pid"]=os.getpid();result["parent_pid"]=os.getppid()
        check_sources(role,opening_request["source_freeze"])
        if role=="B":write(output/"OPEN-AUDIT.json",{
            "status":"COMPLETED_MAIN_AND_SOURCE_CUSTODY","open_attempts":AUDIT_READS})
        result["common_io"]=dict(IO)
        result["common_io_scope"]="explicit common helpers only; Python import I/O uncounted here but included in process wall; native wrapper I/O in native receipts; final result write excluded"
        write(output/"RESULT.json",result)
    except Exception as error:
        if created:
            audit=None
            if role=="B":
                audit=write(output/"OPEN-AUDIT-FAILURE.json",{
                    "status":"UNINITIALIZED" if AUDIT_READS is None else "INITIALIZED_AT_FAILURE",
                    "open_attempts":AUDIT_READS})
            write(output/"FAILURE.json",{"type":type(error).__name__,"message":str(error),
                "pid":os.getpid(),"parent_pid":os.getppid(),"work":dict(ACTIVE_WORK),
                "common_io":dict(IO),"audit":audit,"scope":"through failure; final failure receipt write excluded"})
        raise
