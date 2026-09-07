"""OCM admission adapter for internally executed, measured library selection."""
from unary_contract import InputRefused,fields
from unary_rule_check import check_rule
from unary_method_selection import acquire_selected as select,SCHEMA
from unary_method_selection_check import validate_receipt
import unary_method_data as D

def utility_body(store,rule_id):
    receipt=store.selection["receipt"]
    return {"policy":SCHEMA,"rule_id":rule_id,"selection_receipt_sha256":receipt["receipt_sha256"],
            "library_sha256":receipt["library_sha256"],"ranking_sha256":receipt["ranking_sha256"],
            "selection_contract":receipt["contract"]}

def validate_selection(store):
    body=store.selection
    if body is None:return
    fields(body,("schema","receipt","discovery"))
    if body["schema"]!="ocm.unary-method.selected.v1":raise InputRefused("SELECTED_SCHEMA")
    r=validate_receipt(body["receipt"],sources_sha256=store.source_sha,work=store.work)
    D.payload(store.rt,body["discovery"],"discovery",expected={"selection":r},work=store.work)
    if set(store.records)!={"unary:method:"+x["rule_id"] for x in r["selected"]}:
        raise InputRefused("INCOMPLETE_SELECTED_ISSUANCE")
    for mid in store.method_ids:
        env=store.records[mid]["envelope"]
        if env["discovery"]!=body["discovery"]:raise InputRefused("SELECTED_DISCOVERY")
        rule=next(x for x in r["selected"] if mid=="unary:method:"+x["rule_id"])
        if D.raw(rule)!=D.raw(env["rule"]):raise InputRefused("SELECTED_RULE_BINDING")

def acquire_selected(store,training,development,contract,*,observation=None):
    store._check_environment()
    if store.records or store.selection is not None:raise InputRefused("SELECTED_ALREADY_ACQUIRED")
    if D.live(store.rt,store._proof_warrant())!="LIVE":raise InputRefused("RULE_CHECKER_UNAVAILABLE")
    r=select(training,development,contract,work=store.work,observation=observation,sources_sha256=store.source_sha)
    validate_receipt(r,sources_sha256=store.source_sha,work=store.work)
    discovery=D.admit_evidence(store.rt,"discovery",{"selection":r},store.work)
    selected={"schema":"ocm.unary-method.selected.v1","receipt":r,"discovery":discovery}
    store._append("SELECTION",selected);store.selection=D.parse(D.raw(selected))
    for rule in r["selected"]:
        mid="unary:method:"+rule["rule_id"];checked=check_rule(rule);D.bump(store.work,"schema_checks")
        utility=D.admit_evidence(store.rt,"utility",utility_body(store,rule["rule_id"]),store.work)
        proof_body={"rule":rule,"certificate":checked,"sources_sha256":store.source_sha}
        proof=D.admit_evidence(store.rt,"proof",proof_body,store.work,store._proof_warrant())
        envelope={"schema":"ocm.unary-method.data.v1","rule":rule,"schema_certificate":checked,
                  "proof":proof,"discovery":discovery,"utility":utility,**store.environment,"sources_sha256":store.source_sha}
        if len(D.raw(envelope))>65536:raise InputRefused("METHOD_ENVELOPE_BOUND")
        plan={"method_id":mid,"anchor_id":mid+":proof","edge_id":mid+":support","envelope":envelope,"proof_body":proof_body}
        store._append("PREPARE",plan);anchor,method,edge=store._items(plan)
        store.rt.admit_batch(((anchor,(),"EXACT_CHECKER"),(method,(edge,),"EXACT_CHECKER")))
        D.bump(store.work,"atomic_kso_batches");store._append("ISSUE",{"method_id":mid,"plan_sha256":D.hashed(plan)})
        store.records[mid]=D.parse(D.raw(plan));store.read(mid)
    validate_selection(store)
    return r
