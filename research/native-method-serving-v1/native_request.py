"""Actual KSO query and exact shared-engine request identity."""
from fractions import Fraction
from ocm.kso.space import Atom,Hyperedge
from native_contract import fields,require
import native_data as D
def request(store,task,requested,*,scheduler="layered",invoke=True,request_id=None):
    base=store.engine.request(task,[],scheduler=scheduler,invoke=invoke,request_id=request_id)
    eid=D.admit_evidence(store.rt,"request",base,store.work)
    eligible=store.eligible(requested,eid)
    engine_request=store.engine.request(task,eligible,scheduler=scheduler,invoke=invoke,request_id=base["request_id"])
    qid="native:query:"+D.hashed({"id":base["request_id"],"sequence":len(store.rt.events)})
    data={"engine_request":engine_request,"evidence":eid,"requested_ids":requested,"base":base}
    w=store.warrant([eid]);anchor=Atom(qid+":input","observation",w,scope=D.SCOPE,quarantined=True)
    atom=Atom(qid,"query_seed",w,scope=D.SCOPE,content_ref=D.hashed(data),meta=(("data",D.raw(data).decode()),))
    edge=Hyperedge(qid+":support",(anchor.atom_id,),(qid,),"SUPPORT",warrant=w,scope=D.SCOPE,head_weights=(Fraction(1),))
    store.rt.admit_batch(((anchor,(),"EXACT_CHECKER"),(atom,(edge,),"EXACT_CHECKER")))
    return qid,data

def read_request(store,qid,expected,*,current=True):
    atom=store.rt.state.ks.atom_view.get(qid);require(atom is not None,"MISSING_REQUEST")
    data=D.atom_data(atom,store.work);fields(data,("engine_request","evidence","requested_ids","base"))
    require(D.raw(data)==D.raw(expected),"REQUEST_CHANGED");store.engine.validate_request(data["engine_request"])
    D.payload(store.rt,data["evidence"],"request",expected=data["base"],work=store.work)
    require(atom.warrant==store.warrant([data["evidence"]]) and atom.scope==D.SCOPE,"REQUEST_WARRANT")
    require({**data["engine_request"],"eligible_ids":[]}==data["base"],"REQUEST_BASE")
    if current:
        require(D.live(store.rt,store.warrant([data["evidence"]]))=="LIVE","ENVIRONMENT_UNAVAILABLE")
        require(store.eligible(data["requested_ids"],data["evidence"])==data["engine_request"]["eligible_ids"],"STALE_ELIGIBILITY")
    return data

def check_packet(store,qid,expected,packet,*,current=True):
    data=read_request(store,qid,expected,current=current)
    if current:store.require_selected_live(packet["selected_proof_method_ids"],data["evidence"])
    return store.engine.check(data["engine_request"],packet)
