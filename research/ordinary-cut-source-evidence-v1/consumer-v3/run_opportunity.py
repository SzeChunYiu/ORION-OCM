"""Prospective training-only driver. Requires a released, hash-bound trace packet."""
import hashlib,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def byte_identity(raw):return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def identity(path):return byte_identity(path.read_bytes())
def read_bound(row):
    raw=Path(row["path"]).read_bytes()
    if byte_identity(raw)!={k:row[k] for k in ("bytes","sha256")}:raise ValueError("input identity")
    return json.loads(raw)
def write(p,obj):
    with p.open("x") as f:json.dump(obj,f,sort_keys=True,indent=2,allow_nan=False);f.write("\n")
class Work(dict):
    def __init__(self,maximum):super().__init__();self.maximum=maximum;self.exhausted=False
    def __setitem__(self,key,value):
        if key=="token_states" and value>self.maximum:
            self.exhausted=True;raise ValueError("REGISTERED_TOKEN_STATE_BOUND")
        super().__setitem__(key,value)

def main(request_path,output):
    start=time.perf_counter();request_bytes=request_path.read_bytes();request_identity=byte_identity(request_bytes);request=json.loads(request_bytes)
    gate_path=Path(request["gate_path"]);gate_bytes=gate_path.read_bytes();gate_identity=byte_identity(gate_bytes)
    gate=json.loads(gate_bytes)
    if gate.get("authorization")!="ROOT_TRAINING_OPPORTUNITY_GATE" or gate["request"]!=request_identity:
        raise ValueError("root training-only authorization")
    if request.get("schema")!="ordinary.training-opportunity-request.v3":raise ValueError("opportunity request schema")
    source=request["sources"]
    for name,pin in source.items():
        if identity(ROOT/name)!=pin:raise ValueError("source freeze")
    if output.exists():raise ValueError("output already exists")
    output.mkdir()
    result={"schema":"ordinary.training-only-opportunity.v3","roots":[],"native_calls":0,"pid":os.getpid(),
            "terminal":"RUNNING","request":request_identity,"training_outcome_is_not_native_admission":True}
    work=Work(request["max_token_states"])
    try:
        sys.path[:0]=[str(ROOT),str(ROOT/"donor")]
        import boundary as cuts
        import alias_screen as alias
        import teaching_packet as teaching
        import registry_scope
        base=read_bound(request["P0_contracts"]);packet=read_bound(request["training_packet"])
        release=read_bound(request["release_receipt"]);inventory=read_bound(request["P1_inventory"])
        authority=read_bound(request["qualified_native_trace_authority"])
        registry_scope.read_declared(read_bound(request["registry_scope"]),request["corpus"])
        p1=teaching.validate(base,packet,inventory,release,request,authority)
        roots=packet["roots"]
        result["qualified_native_trace_authority"]=request["qualified_native_trace_authority"]
        result["P1_inventory"]=request["P1_inventory"]
        result["authority_scope"]="Exact external qualification supplied by root gate; this audit does not replay native verification."
        write(output/"P1-CONTRACTS.json",p1)
        result["P1_contracts"]=identity(output/"P1-CONTRACTS.json")
        for row in roots:
            record={"ordinal":row["ordinal"],"label":row["label"]}
            if row["source_disposition"]!="RELEASED":
                record["status"]=row["source_disposition"];result["roots"].append(record);continue
            if row["trace_disposition"]=="TRACE_UNUSABLE":
                record.update(status="TRACE_UNUSABLE",whole_contract=row["whole_contract"],
                              P1_retained=True,opportunity_coverage="UNKNOWN_INTERFACE")
                result["roots"].append(record)
                write(output/("ROOT-"+str(row["ordinal"])+".json"),record)
                continue
            if work.exhausted or time.perf_counter()-start>request["max_wall_s"]:
                record["status"]="NOT_REACHED_RESOURCE";result["roots"].append(record);continue
            try:
                trace=row["trace"];contracts=row["contracts"]
                if trace["source"]["label"]!=row["label"]:raise ValueError("training identity")
                mined=cuts.enumerate_two(trace,contracts,work)
                record.update(status="ENUMERATED",cuts=mined["rows"])
                for candidate in record["cuts"]:
                    if candidate["status"]!="CUT_PROPOSAL":continue
                    if work.exhausted or time.perf_counter()-start>request["max_wall_s"]:
                        candidate["screen"]={"status":"UNKNOWN_RESOURCE","coverage_complete":False};continue
                    candidate["screen"]=alias.screen(candidate["body"],p1,work)
            except (ValueError,KeyError,TypeError,IndexError,RecursionError) as exc:
                record.update(status="UNKNOWN_INTERFACE",error=type(exc).__name__+": "+str(exc))
            result["roots"].append(record)
            write(output/("ROOT-"+str(row["ordinal"])+".json"),record)
        result["terminal"]="TRAINING_ONLY_OPPORTUNITY_RECORDED"
        result["new_native_admissions"]=0
    except BaseException as exc:
        result.update(terminal="AUDIT_FAILED",error={"type":type(exc).__name__,"message":str(exc)})
    result.update(work=dict(work),token_bound_reached=work.exhausted,wall_s=time.perf_counter()-start)
    try:
        result["inputs_unchanged"]=all(identity(Path(request[k]["path"]))=={x:request[k][x] for x in ("bytes","sha256")}
                                       for k in ("P0_contracts","training_packet","release_receipt","P1_inventory","qualified_native_trace_authority","registry_scope"))
        result["sources_unchanged"]=all(identity(ROOT/name)==pin for name,pin in source.items())
        result["request_unchanged"]=identity(request_path)==request_identity and identity(gate_path)==gate_identity
    except BaseException as exc:
        result.update(inputs_unchanged=False,sources_unchanged=False,request_unchanged=False,
                      custody_error=type(exc).__name__+": "+str(exc))
    write(output/"RESULT.json",result)
    return 0 if result["terminal"]!="AUDIT_FAILED" and result["inputs_unchanged"] and result["sources_unchanged"] and result["request_unchanged"] else 1
if __name__=="__main__":raise SystemExit(main(Path(sys.argv[1]),Path(sys.argv[2])))
