"""Fixed episode-major A/B/C/role schedule; no configurable workflow policy."""
from unary_contract import InputRefused
from unary_method_selection import contract
from unary_assay_present import final_pair,presentation_rows,support_variants
from unary_assay_phase import ARMS,ROLES,order
from unary_assay_service import remaining
import unary_method_plain as D

def key(e,phase,arm):return f"e{e}--{phase}--{arm}"

def expected(session,e,n):
    for arm in ("ADAPTIVE_PARENT","OCM_ENABLED"):session.expect(key(e,"A",arm),{"episode":e,"phase":"A","arm":arm})
    for phase in ("B","C"):
        for arm in ARMS:session.expect(key(e,phase,arm),{"episode":e,"phase":phase,"arm":arm,"base_rows":n})
    for role in ROLES:
        for arm in ARMS:
            for action in ("withdraw","withdrawn","reinstate","restored"):
                phase=role+"-"+action
                session.expect(key(e,phase,arm),{"episode":e,"phase":phase,"arm":arm})

def completed(session,slot):return session.slots[slot]["state"]=="COMPLETED"

def request_rows(pairs,variants,work):
    rows=[];slots=[]
    for pair,group in zip(pairs,variants):
        for v in group:
            oid=pair["row_id"]+"/C/"+v["kind"]
            slots.append({"observation_id":oid,"row_id":pair["row_id"],**v})
            if v["terminal"]=="READY":rows.append({"observation_id":oid,"row_id":pair["row_id"],"presentation":"ast",
                "payload":v["task"],"task_sha256":v["task_sha256"]})
    return rows,slots

def solve(session,e,phase,arm,rows,source):
    slot=key(e,phase,arm);request={"rows":rows}
    if arm!="EXACT_PARENT":
        try:store=session.snapshot(source,slot)
        except Exception:return None
        request.update(store=str(store),invoke=arm!="OCM_KNOCKOUT")
    return session.call(slot,arm,"presented_batch",request)

def roles(session,e,pair,mid,origins):
    from unary_assay_controls import role_transition
    outcomes={}
    for role in ROLES:
        for arm in order(e):
            previous=origins.get(arm);chain=[];stopped=False
            for action in ("withdraw","withdrawn","reinstate","restored"):
                phase=role+"-"+action;slot=key(e,phase,arm)
                if stopped or session.abort:
                    session.mark(slot,"UNAVAILABLE","ROLE_DEPENDENCY");continue
                mutation=action in ("withdraw","reinstate")
                if arm=="EXACT_PARENT" and mutation:
                    session.mark(slot,"NOT_APPLICABLE","EXACT_NO_ROLE_RECORD");continue
                if mutation:
                    try:store=session.snapshot(previous,slot)
                    except Exception:stopped=True;continue
                    record=session.call(slot,arm,"revise",{"store":str(store),"role":role,
                        "state":"REVOKED" if action=="withdraw" else "LIVE","method_id":mid})
                else:
                    row={"observation_id":pair["row_id"]+"/"+phase,"row_id":pair["row_id"],
                         "presentation":"ast","payload":pair["formal"],"task_sha256":pair["task_sha256"]}
                    record=solve(session,e,phase,arm,[row],previous)
                chain.append(record)
                if record is None or not completed(session,slot):stopped=True;continue
                previous=record["request"].get("store")
                try:role_transition(record["facts"],role,action,arm,mid)
                except Exception as exc:session.fail("SEMANTIC_CONTROL_FAILED",str(exc),slot=slot)
            outcomes[role+"/"+arm]=[r["slot"] for r in chain if r is not None]
    return outcomes

def episode(session,e,generation,*,authored=False):
    session.current_episode=e
    parts=generation["partitions"];n=len(parts.get("final",[]))
    out={"episode":e,"generation_terminal":generation["terminal"],"base_rows":n,"phases":{}}
    if generation["terminal"]!="GENERATED":
        out["reason"]="GENERATION_INCOMPLETE";return out
    training=[x["task"] for x in parts["train"]];development=[x["task"] for x in parts["development"]]
    policy=contract(len(training),len(development),authored=authored);a={}
    for arm in (("ADAPTIVE_PARENT","OCM_ENABLED") if e%2==0 else ("OCM_ENABLED","ADAPTIVE_PARENT")):
        slot=key(e,"A",arm);store=session.root/"stores"/slot
        a[arm]=session.call(slot,arm,"acquire_selected",{"store":str(store),"training":training,
                           "development":development,"contract":policy})
    if not all(completed(session,key(e,"A",arm)) for arm in a):
        out["reason"]="A_INCOMPLETE";return out
    fields=("pool_sha256","ranking_sha256","library_sha256")
    if any(a["ADAPTIVE_PARENT"]["facts"]["selection"][k]!=a["OCM_ENABLED"]["facts"]["selection"][k] for k in fields):
        session.fail("SEMANTIC_CONTROL_FAILED","A_IDENTITY_MISMATCH");return out
    origins={arm:a["ADAPTIVE_PARENT" if arm=="ADAPTIVE_PARENT" else "OCM_ENABLED"]["request"]["store"] for arm in ARMS if arm!="EXACT_PARENT"}
    work={};pairs=[final_pair(x["task"],e,i,work=work) for i,x in enumerate(parts["final"])]
    session.ledger.append("PAIRS",{"episode":e,"pairs":pairs,"semantic_keys":[x["semantic_key"] for x in parts["final"]],"work":work})
    rows=presentation_rows(pairs,e,work=work);b={}
    for arm in order(e):
        b[arm]=solve(session,e,"B",arm,rows,origins.get(arm))
        if session.abort:break
    out["phases"]["B"]={arm:None if r is None else r["slot"] for arm,r in b.items()}
    if not all(completed(session,key(e,"B",arm)) for arm in ARMS):
        out["reason"]="B_INCOMPLETE";return out
    from unary_assay_controls import agreement
    try:agreement([b[arm]["facts"] for arm in ARMS])
    except Exception as exc:
        session.fail("SEMANTIC_CONTROL_FAILED",str(exc));return out
    formal={x["row_id"]:x for x in b["OCM_ENABLED"]["facts"]["rows"] if x["presentation"]=="ast"}
    variants=[]
    for pair in pairs:
        use=formal[pair["row_id"]]["use"]
        variants.append(support_variants(pair["formal"],used_cover=use["cover"] if use["recipes_applied"] else None,work=work))
    crows,cslots=request_rows(pairs,variants,work)
    session.ledger.append("SUPPORT",{"episode":e,"slots":cslots,"reference":"OCM_ENABLED/B/ast","work":work})
    c={}
    for arm in order(e):
        c[arm]=solve(session,e,"C",arm,crows,origins.get(arm))
        if session.abort:break
    out["phases"]["C"]={arm:None if r is None else r["slot"] for arm,r in c.items()}
    if not all(completed(session,key(e,"C",arm)) for arm in ARMS):
        out["reason"]="C_INCOMPLETE";return out
    try:agreement([c[arm]["facts"] for arm in ARMS])
    except Exception as exc:
        session.fail("SEMANTIC_CONTROL_FAILED",str(exc));return out
    reference=next((pair for pair in pairs if formal[pair["row_id"]]["use"]["recipes_applied"]),None)
    if reference is None:
        for role in ROLES:
            for arm in ARMS:
                for action in ("withdraw","withdrawn","reinstate","restored"):
                    session.mark(key(e,role+"-"+action,arm),"NOT_APPLICABLE","NO_USE_REFERENCE")
        out["role_reference"]=None
    else:
        mid=formal[reference["row_id"]]["use"]["method_id"];out["role_reference"]={"row_id":reference["row_id"],"method_id":mid}
        out["phases"]["roles"]=roles(session,e,reference,mid,origins)
    return out
