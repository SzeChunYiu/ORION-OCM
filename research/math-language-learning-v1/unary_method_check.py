"""Conditional request and use binding; independent semantics checks the answer."""
from fractions import Fraction
from ocm.kso.space import Atom,Hyperedge
from unary_contract import InputRefused,validate_task,fields,negate
import unary_method_data as D

def answer_warrant(store,eid=None):
    ids=[store.environment[k] for k in ("semantics","answer_environment")]
    if eid is not None:ids.append(eid)
    return store.rt.state.evidence.citation_warrant(ids)

def request(store,value):
    value=validate_task(D.parse(D.raw(value)))
    body={"task":value,"task_sha256":D.hashed(value),"meaning":"conditional-premise-assumptions.v1"}
    eid=D.admit_evidence(store.rt,"request",body,store.work)
    qid="unary:query:"+D.hashed({"body":body,"sequence":len(store.rt.events)})
    data={"schema":"ocm.unary-method.request.v1",**body,"evidence":eid,"sources_sha256":store.source_sha}
    w=answer_warrant(store,eid)
    anchor=Atom(qid+":input","observation",w,scope=D.SCOPE,quarantined=True)
    atom=Atom(qid,"query_seed",w,scope=D.SCOPE,content_ref=D.hashed(data),meta=(("data",D.raw(data).decode()),))
    edge=Hyperedge(qid+":support",(anchor.atom_id,),(qid,),"SUPPORT",warrant=w,scope=D.SCOPE,head_weights=(Fraction(1),))
    store.rt.admit_batch(((anchor,(),"EXACT_CHECKER"),(atom,(edge,),"EXACT_CHECKER")))
    return qid,data

def read_request(store,qid,expected=None):
    atom=store.rt.state.ks.atom_view.get(qid)
    if atom is None:raise InputRefused("MISSING_REQUEST")
    data=D.atom_data(atom,store.work)
    fields(data,("schema","task","task_sha256","meaning","evidence","sources_sha256"))
    if data["schema"]!="ocm.unary-method.request.v1" or data["sources_sha256"]!=store.source_sha:
        raise InputRefused("REQUEST_SOURCE")
    task=validate_task(data["task"])
    if data["task_sha256"]!=D.hashed(task) or data["meaning"]!="conditional-premise-assumptions.v1":
        raise InputRefused("REQUEST_BINDING")
    if expected is not None and D.raw(data)!=D.raw(expected):raise InputRefused("REQUEST_CHANGED")
    body={k:data[k] for k in ("task","task_sha256","meaning")}
    D.payload(store.rt,data["evidence"],"request",expected=body,work=store.work)
    if atom.warrant!=answer_warrant(store,data["evidence"]) or atom.scope!=D.SCOPE:
        raise InputRefused("REQUEST_WARRANT")
    return data

from unary_method_verify_use import verify_use,verify_answer

def validate_use(store,task,use,*,current=True,work=None):
    return verify_use(task,use,store.read,current=current,work={} if work is None else work)

def check_packet(store,qid,expected,packet,*,current=True,work=None):
    work={} if work is None else work
    packet=D.parse(D.raw(packet));fields(packet,("schema","task_sha256","result","use","execution"))
    data=read_request(store,qid,expected)
    if packet["schema"]!="ocm.unary-method.packet.v1" or packet["task_sha256"]!=data["task_sha256"]:
        raise InputRefused("PACKET_REQUEST_BINDING")
    if current and D.live(store.rt,answer_warrant(store,data["evidence"]))!="LIVE":
        raise InputRefused("ANSWER_CHECKER_UNAVAILABLE")
    if not verify_answer(data["task"],packet["result"],work=work,counter="independent_answer_checks"):raise InputRefused("ANSWER_CERTIFICATE")
    validate_use(store,data["task"],packet["use"],current=current,work=work)
    return True
