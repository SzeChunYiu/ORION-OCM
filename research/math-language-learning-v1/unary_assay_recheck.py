"""Derive expected presentations/interventions from retained generation and use."""
from unary_contract import InputRefused
from unary_assay_identity import semantic_key
from unary_assay_present import final_pair,presentation_rows,support_variants
from unary_assay_schedule import request_rows,key
from unary_assay_phase import ARMS,ROLES,order
from unary_assay_controls import agreement,role_transition
from unary_assay_auth import ControlFailure,CustodyFailure
from unary_assay_obligations import accepted
import unary_method_plain as D

def compare_rows(call,expected):
    if D.raw(call["request"]["rows"])!=D.raw(expected):raise ControlFailure("SCHEDULE_INPUT_SUBSTITUTION")

def episode(e,generated,calls,*,work):
    by={c["slot"]:c for c in calls};g=generated["partitions"];a={}
    for arm in ("ADAPTIVE_PARENT","OCM_ENABLED"):
        call=by.get(key(e,"A",arm))
        if call is None:continue
        r=call["request"]
        if (D.raw(r["training"])!=D.raw([x["task"] for x in g["train"]])
            or D.raw(r["development"])!=D.raw([x["task"] for x in g["development"]])):
            raise ControlFailure("ACQUISITION_INPUT_SUBSTITUTION")
        if accepted(call):a[arm]=call["facts"]
    if len(a)!=2:return {}
    for name in ("pool_sha256","ranking_sha256","library_sha256"):
        if a["ADAPTIVE_PARENT"]["selection"][name]!=a["OCM_ENABLED"]["selection"][name]:
            raise ControlFailure("A_IDENTITY_MISMATCH")
    pairs=[];keys={}
    for i,row in enumerate(g["final"]):
        if row["row_id"]!=f"e{e}/final/{i}" or semantic_key(row["task"],work)!=row["semantic_key"]:
            raise CustodyFailure("FINAL_IDENTITY")
        pairs.append(final_pair(row["task"],e,i,work=work));keys[row["row_id"]]=row["semantic_key"]
    b_rows=presentation_rows(pairs,e,work=work);b={}
    for arm in ARMS:
        call=by.get(key(e,"B",arm))
        if call is None:continue
        compare_rows(call,b_rows)
        if accepted(call):b[arm]=call["facts"]
    result={"selection":a["OCM_ENABLED"]["selection"]["terminal"],"selected":a["OCM_ENABLED"]["selected_rule_ids"],
            "semantic_keys":keys,"B":b}
    if len(b)!=4:return result
    agreement(list(b.values()))
    formal={r["row_id"]:r for r in b["OCM_ENABLED"]["rows"] if r["presentation"]=="ast"}
    groups=[support_variants(pair["formal"],used_cover=(formal[pair["row_id"]]["use"]["cover"]
            if formal[pair["row_id"]]["use"]["recipes_applied"] else None),work=work) for pair in pairs]
    c_rows,cslots=request_rows(pairs,groups,work);c={}
    for arm in ARMS:
        call=by.get(key(e,"C",arm))
        if call is None:continue
        compare_rows(call,c_rows)
        if accepted(call):c[arm]=call["facts"]
    result["C_slots"]=cslots
    if len(c)!=4:return result
    result["C_complete"]=True
    agreement(list(c.values()))
    reference=next((p for p in pairs if formal[p["row_id"]]["use"]["recipes_applied"]),None)
    result["role_reference"]=None if reference is None else reference["row_id"]
    if reference is None:return result
    mid=formal[reference["row_id"]]["use"]["method_id"]
    for role in ROLES:
        for arm in order(e):
            for action in ("withdraw","withdrawn","reinstate","restored"):
                phase=role+"-"+action;call=by.get(key(e,phase,arm))
                if call is None:continue
                r=call["request"]
                if action in ("withdraw","reinstate"):
                    if (r["method_id"]!=mid or r["role"]!=role or r["state"]!=("REVOKED" if action=="withdraw" else "LIVE")):
                        raise ControlFailure("ROLE_REFERENCE_SUBSTITUTION")
                else:
                    row={"observation_id":reference["row_id"]+"/"+phase,"row_id":reference["row_id"],
                         "presentation":"ast","payload":reference["formal"],"task_sha256":reference["task_sha256"]}
                    compare_rows(call,[row])
                if accepted(call):
                    role_transition(call["facts"],role,action,arm,mid)
    return result
