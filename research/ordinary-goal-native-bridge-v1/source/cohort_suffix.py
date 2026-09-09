"""Deterministic scoped essential-label transport; no native admission."""
import copy
import life_native as N
import trace_source as S
from goal_library import identity,raw_identity,require
def construct(base_raw,base_pin,members,members_pin):
    require(raw_identity(base_raw)==base_pin,"base source pin")
    require(identity(members)==members_pin,"ordered member packet pin")
    require(type(members) is list and members,"nonempty ordered members")
    base,_=S.index(base_raw);claims=[];bindings=[];seen=set(base)
    theorem_labels=[m["contract"]["label"] for m in members]
    require(len(set(theorem_labels))==len(theorem_labels) and not set(theorem_labels)&set(base),"cohort theorem collision")
    reserved=set(theorem_labels)|seen
    for i,m in enumerate(members):
        require(set(m)=={"contract","proof","origin"},"member fields")
        row=copy.deepcopy(m["contract"]);proof=copy.deepcopy(m["proof"])
        require(set(row)=={"label","kind","statement","floating","essential","dv"} and
                row["kind"]=="$p" and row["dv"]==[],"ordinary no-DV theorem contract")
        old=[h["label"] for h in row["essential"]]
        require(len(set(old))==len(old) and not set(old)&set(base) and not set(old)&set(theorem_labels),"original essential-label collision")
        new=["cohort-e-"+str(i)+"-"+str(j) for j in range(len(old))]
        require(not set(new)&reserved,"new essential-label collision")
        mapping=dict(zip(old,new));reserved.update(new)
        require(set(proof)<={k for k,r in base.items() if r["kind"] in {"$a","$p","$f"}}|set(old),
                "proof outside base and own scoped essentials")
        parameters=[{"type":h["statement"][0],"variable":h["statement"][1],"floating_label":h["label"]} for h in row["floating"]]
        claim={"label":row["label"],"premises":[h["statement"] for h in row["essential"]],
               "query":row["statement"],"holes":new,"parameters":parameters,
               "proof":[mapping.get(t,t) for t in proof]}
        N.validate_claims([claim]);claims.append(claim)
        bindings.append({"index":i,"theorem_label":row["label"],"origin":copy.deepcopy(m["origin"]),
                         "original_member":identity(m),"original_contract":identity(row),"original_proof":identity(proof),
                         "essential_label_renaming":[{"old":a,"new":b,"statement":h["statement"]}
                                                     for a,b,h in zip(old,new,row["essential"])],
                         "transported_proof":identity(claim["proof"])})
    suffix=N.serialize(claims);joined=base_raw+b"\n"+suffix;rows,_=S.index(joined)
    expected_new=set(theorem_labels)|{h for c in claims for h in c["holes"]}
    require(set(rows)-set(base)==expected_new,"transported label population")
    for m,c,binding in zip(members,claims,bindings):
        expected=copy.deepcopy(m["contract"])
        expected["essential"]=[{"label":h,"statement":s} for h,s in zip(c["holes"],c["premises"])]
        actual=rows[c["label"]]
        require(S.contract(actual)==expected and actual["proof"]==c["proof"] and actual["active_dv"]==[],
                "exact transported statement/types/DV/proof/context")
        binding.update(transported_contract=identity(expected),transported_source=actual["raw"])
    require([r["raw"] for r in rows.values() if r["kind"]=="$a"]==
            [r["raw"] for r in base.values() if r["kind"]=="$a"],"axiom authority changed")
    return {"schema":"ordinary.scoped-cohort-transport.v1","native_acceptance":False,"base":base_pin,
            "members":members_pin,"suffix":raw_identity(suffix),"joined_prefix":raw_identity(joined),
            "bindings":bindings},suffix
