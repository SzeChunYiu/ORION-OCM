"""Gated chronological source release only; no verification, cuts or ranking."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/"donor")]
import trace_source as S
import trace_adapter as T
import registry_scope as R
def ident(raw):return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def write(p,value):
    with p.open("x") as f:json.dump(value,f,sort_keys=True,indent=2);f.write("\n")
def release(raw,exclusions):
    depth=0;ordinal=0;pending=None;previous=None;end=None;selected=[]
    for token,start,finish in S.lex(raw):
        if token=="$"+"{":depth+=1
        elif token=="$}":depth-=1
        elif token=="$p":
            ordinal+=1;pending=(ordinal,previous)
        elif token=="$." and pending:
            if pending[0]>4095:selected.append({"ordinal":pending[0],"label":pending[1]})
            pending=None
            if ordinal==4223:end=finish;break
        previous=token
    if end is None or len(selected)!=128 or depth<0:raise ValueError("fixed source range unavailable")
    closed=raw[:end]+b"\n"+b"$}\n"*depth
    records,index_end=S.index(closed)
    p_rows=[x for x in records.values() if x["kind"]=="$p"]
    if len(p_rows)!=4223:raise ValueError("source ordinal population")
    protected=set(exclusions["protected_labels"])
    base={x["label"] for x in p_rows[:4095]}
    if protected & base:raise ValueError("protected theorem conflicts with unchanged P0")
    excluded=set(protected);rows=[]
    for ordinal,row in enumerate(p_rows[4095:],4096):
        direct=sorted({op["label"] for op in T.operations(row) if "label" in op and op["label"] in records
                       and records[op["label"]]["kind"]=="$p"})
        forbidden=sorted(set(direct)&excluded)
        status="EXCLUDED_PRIOR_PROTECTED" if row["label"] in protected else "EXCLUDED_DEPENDS_PRIOR_PROTECTED" if forbidden else "RELEASED"
        if status!="RELEASED":excluded.add(row["label"])
        rows.append({"ordinal":ordinal,"label":row["label"],"source_disposition":status,
                     "statement":row["statement"],"proof_raw":row["proof_raw"],"source_raw":row["raw"],
                     "direct_theorem_dependencies":direct,"forbidden_dependencies":forbidden})
    return closed,{"ordinals":list(range(4096,4224)),"roots":rows,"source_end_exclusive":end,
                   "synthetic_scope_closures":depth,"closed_source":ident(closed),
                   "axiom_identities":[{"label":x["label"],"raw":x["raw"]} for x in records.values() if x["kind"]=="$a"],
                   "native_calls":0,"opportunity_or_semantic_outcomes":False,
                   "closed_prefix_access":"custodian/native trace qualifier only; may contain excluded proofs, never learner input"}
def main(request_path,output):
    request_bytes=request_path.read_bytes();request=json.loads(request_bytes)
    if request.get("schema")!="ordinary.training-release-request.v2":raise ValueError("release request schema")
    gate_path=Path(request["gate_path"]);gate_bytes=gate_path.read_bytes();gate=json.loads(gate_bytes)
    if gate.get("authorization")!="ROOT_TRAINING_RELEASE_GATE" or gate["request"]!=ident(request_bytes):
        raise ValueError("release not authorized")
    for name,pin in request["sources"].items():
        if ident((ROOT/name).read_bytes())!=pin:raise ValueError("source binding")
    source=Path(request["corpus"]["path"]);raw=source.read_bytes()
    if ident(raw)!={k:request["corpus"][k] for k in ("bytes","sha256")}:raise ValueError("corpus binding")
    ep=Path(request["registry_scope"]["path"]);eraw=ep.read_bytes()
    if ident(eraw)!={k:request["registry_scope"][k] for k in ("bytes","sha256")}:raise ValueError("registry scope binding")
    ex=json.loads(eraw)
    R.read_declared(ex,request["corpus"])
    closed,result=release(raw,ex)
    output.mkdir()
    with (output/"CUSTODIAN-PREFIX.mm").open("xb") as f:f.write(closed)
    result.update(schema="ordinary.training-release.v2",corpus=request["corpus"],registry_scope=request["registry_scope"],
                  request=ident(request_bytes),native_qualification="PENDING",
                  scope="Only chronological source release and dependency metadata. Eight exposed anchors remain apparatus controls; later proof bodies stay sealed.")
    if ident(source.read_bytes())!=ident(raw) or ident(ep.read_bytes())!=ident(eraw):raise ValueError("input drift")
    if request_path.read_bytes()!=request_bytes or gate_path.read_bytes()!=gate_bytes:raise ValueError("request or gate drift")
    for name,pin in request["sources"].items():
        if ident((ROOT/name).read_bytes())!=pin:raise ValueError("source drift")
    R.read_declared(ex,request["corpus"])
    write(output/"RELEASE.json",result)
if __name__=="__main__":main(Path(sys.argv[1]),Path(sys.argv[2]))
