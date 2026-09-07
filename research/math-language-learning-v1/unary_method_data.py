"""Bounded plain data, source observations, and declared evidence identities."""
import hashlib
import json
import math
from pathlib import Path
from ocm.kso.ids import content_hash,evidence_id
from ocm.kso.types import Authority,Scope
from ocm.kso.warrant import Liveness
from unary_contract import InputRefused,fields

CONTEXT="unary-method-runtime.v1"
SCOPE=Scope.of(CONTEXT)
MAX_BYTES=1<<20

def bump(work,key,n=1):work[key]=work.get(key,0)+n

def raw(value):
    nodes=0
    def check(x,depth=0):
        nonlocal nodes
        nodes+=1
        if nodes>100000 or depth>40:raise InputRefused("METHOD_DATA_BOUND")
        if type(x) is dict:
            if any(type(k) is not str for k in x):raise InputRefused("METHOD_DATA_KEY")
            for v in x.values():check(v,depth+1)
        elif type(x) is list:
            for v in x:check(v,depth+1)
        elif type(x) is float:
            if not math.isfinite(x):raise InputRefused("METHOD_DATA_FLOAT")
        elif type(x) not in (str,int,bool,type(None)):raise InputRefused("METHOD_NOT_DATA")
    check(value)
    result=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
    if len(result)>MAX_BYTES:raise InputRefused("METHOD_DATA_BOUND")
    return result

def hashed(value):return hashlib.sha256(raw(value)).hexdigest()

def parse(data):
    if type(data) is not bytes or len(data)>MAX_BYTES:raise InputRefused("METHOD_DATA_BYTES")
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise InputRefused("METHOD_DUPLICATE_KEY")
            result[key]=value
        return result
    try:value=json.loads(data,object_pairs_hook=pairs)
    except (UnicodeError,ValueError,RecursionError) as exc:raise InputRefused("METHOD_JSON") from exc
    if raw(value)!=data:raise InputRefused("METHOD_NONCANONICAL")
    return value

def sources(work=None):
    work={} if work is None else work
    here=Path(__file__).resolve().parent;repo=here.parents[1]
    paths=list((repo/"src/ocm").rglob("*.py"))+list((repo/"src/orion_v2").rglob("*.py"))
    paths+=list(here.glob("unary_rule_*.py"))+list(here.glob("unary_method_*.py"))+list(here.glob("unary_parent_*.py"))
    paths+=list((repo/"docs/plans/unary-adaptive-parent-v2-1").glob("*.md"))
    paths+=[repo/"research/math-language-v1"/n for n in
            ("unary_contract.py","unary_language.py","unary_solver.py","unary_verify.py")]
    out={}
    for p in sorted(paths):
        data=p.read_bytes();bump(work,"source_files_hashed");bump(work,"source_bytes_hashed",len(data))
        out[str(p.relative_to(repo))]=hashlib.sha256(data).hexdigest()
    return out

def payload(rt,eid,role,*,expected=None,derived=None,work=None):
    work={} if work is None else work
    if type(eid) is not str:raise InputRefused("EVIDENCE_ID")
    rec=rt.state.evidence.records.get(eid)
    if rec is None:raise InputRefused("MISSING_EVIDENCE")
    found=None
    for event in rt.events:
        bump(work,"evidence_events_read")
        if event.event_type.value!="EVIDENCE_ADMITTED" or event.status.value!="PASS":continue
        p=event.payload
        if evidence_id(rt.state.evidence.namespace,{"payload":p["payload"],"source":p["source"],
                                                  "channel":p["channel"]})==eid:found=p
    if found is None:raise InputRefused("MISSING_EVIDENCE_PAYLOAD")
    data=parse(raw(found["payload"]));fields(data,("schema","role","body"))
    if data["schema"]!="ocm.unary-method.evidence.v1" or data["role"]!=role:
        raise InputRefused("EVIDENCE_ROLE")
    channel={"proof":"proof","discovery":"demonstration"}.get(role,"instruction")
    if (rec.channel.value!=channel or rec.source!="unary-method.v1:"+role or
        rec.scope!=SCOPE or rec.authority!=Authority() or rec.derived_from!=derived or
        rec.content_hash!=content_hash(data)):raise InputRefused("EVIDENCE_POLICY")
    if expected is not None and raw(data["body"])!=raw(expected):raise InputRefused("EVIDENCE_BODY")
    return data["body"]

def admit_evidence(rt,role,body,work,derived=None):
    channel={"proof":"proof","discovery":"demonstration"}.get(role,"instruction")
    data={"schema":"ocm.unary-method.evidence.v1","role":role,"body":parse(raw(body))}
    _,eid=rt.admit_evidence(data,channel,"unary-method.v1:"+role,scope=SCOPE,derived_from=derived)
    bump(work,"evidence_admissions")
    payload(rt,eid,role,expected=body,derived=derived,work=work)
    return eid

def live(rt,warrant):
    w=rt.state.nogoods.filter_interval(warrant)
    w=rt.state.evidence.nogoods.filter_interval(w)
    return w.liveness(rt.state.revoked|rt.state.evidence.revoked).value

def atom_data(atom,work):
    bump(work,"atoms_read")
    if (type(atom.meta) is not tuple or len(atom.meta)!=1 or type(atom.meta[0]) is not tuple
        or len(atom.meta[0])!=2 or type(atom.meta[0][0]) is not str or atom.meta[0][0]!="data"
        or type(atom.meta[0][1]) is not str or type(atom.content_ref) is not str):
        raise InputRefused("METHOD_ATOM_DATA")
    data=atom.meta[0][1].encode();bump(work,"atom_bytes_decoded",len(data))
    value=parse(data)
    if hashlib.sha256(data).hexdigest()!=atom.content_ref:raise InputRefused("METHOD_ATOM_HASH")
    return value
