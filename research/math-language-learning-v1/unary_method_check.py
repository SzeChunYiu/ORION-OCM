"""Conditional request and use binding; independent semantics checks the answer."""
from fractions import Fraction
from ocm.kso.space import Atom,Hyperedge
from unary_contract import InputRefused,validate_task,fields,negate
from unary_verify import verify_result
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

def _expr(pattern,binding,work):
    D.bump(work,"binding_expression_nodes")
    if pattern[0]=="pred":return binding[pattern[1]]
    return [pattern[0],*[_expr(x,binding,work) for x in pattern[1:]]]

def _statement(pattern,binding,work):
    return {"kind":pattern["kind"],"left":_expr(pattern["left"],binding,work),
            "right":_expr(pattern["right"],binding,work)}

def validate_use(store,task,use,*,current=True,work=None):
    work={} if work is None else work
    fields(use,("method_id","rule_id","binding","cover","recipes_applied","replaced_branch"))
    if type(use["recipes_applied"]) is not int or use["recipes_applied"] not in (0,1):raise InputRefused("RECIPE_COUNT")
    if not use["recipes_applied"]:
        if use!={"method_id":None,"rule_id":None,"binding":{},"cover":[],"recipes_applied":0,"replaced_branch":None}:
            raise InputRefused("FALSE_METHOD_USE")
        return
    item=store.read(use["method_id"])
    if current and not item["eligible"]:raise InputRefused("METHOD_NOT_ELIGIBLE")
    rule=item["envelope"]["rule"]
    if use["rule_id"]!=rule["rule_id"]:raise InputRefused("RULE_USE_ID")
    fields(use["binding"],tuple(rule["parameters"]))
    cover=use["cover"]
    if (type(cover) is not list or any(type(i) is not int or not 0<=i<len(task["premises"]) for i in cover)
        or cover!=sorted(set(cover)) or len(cover)!=len(rule["premises"])):raise InputRefused("RULE_USE_COVER")
    instantiated=[_statement(p,use["binding"],work) for p in rule["premises"]]
    actual=[task["premises"][i] for i in cover]
    if sorted(map(D.raw,instantiated))!=sorted(map(D.raw,actual)):raise InputRefused("RULE_USE_SUPPORT")
    universal=task["query"]["kind"] in ("every","no")
    target=task["query"] if universal else negate(task["query"])
    if D.raw(_statement(rule["conclusion"],use["binding"],work))!=D.raw(target):raise InputRefused("RULE_USE_TARGET")
    if use["replaced_branch"]!=("no" if universal else "yes"):raise InputRefused("RULE_USE_BRANCH")

def check_packet(store,qid,expected,packet,*,current=True,work=None):
    work={} if work is None else work
    packet=D.parse(D.raw(packet));fields(packet,("schema","task_sha256","result","use","execution"))
    data=read_request(store,qid,expected)
    if packet["schema"]!="ocm.unary-method.packet.v1" or packet["task_sha256"]!=data["task_sha256"]:
        raise InputRefused("PACKET_REQUEST_BINDING")
    if current and D.live(store.rt,answer_warrant(store,data["evidence"]))!="LIVE":
        raise InputRefused("ANSWER_CHECKER_UNAVAILABLE")
    D.bump(work,"independent_answer_checks")
    if not verify_result(data["task"],packet["result"]):raise InputRefused("ANSWER_CERTIFICATE")
    validate_use(store,data["task"],packet["use"],current=current,work=work)
    return True
