"""Fixed retained execution obligations and original-store restart lineage."""
from pathlib import Path
from unary_assay_phase import ARMS,ROLES
from unary_assay_auth import CustodyFailure

def key(e,phase,arm):return f"e{e}--{phase}--{arm}"

def accepted(call):
    return (call is not None and call.get("error") is None and type(call.get("facts")) is dict
            and call["facts"].get("terminal")=="CHECKED")

def failure_at(abort,e):
    if abort is None:return False
    return any(c["kind"]=="SEMANTIC_CONTROL_FAILED" and c.get("episode")==e
               for c in abort.get("causes",[abort]))

def completion(e,states,calls,known):
    by={c["slot"]:c for c in calls};missing=[]
    required=[key(e,"A",arm) for arm in ("ADAPTIVE_PARENT","OCM_ENABLED")]
    required += [key(e,p,arm) for p in ("B","C") for arm in ARMS]
    reference_known=known.get("C_complete") is True and "role_reference" in known
    for role in ROLES:
        for arm in ARMS:
            for action in ("withdraw","withdrawn","reinstate","restored"):
                slot=key(e,role+"-"+action,arm)
                na=(reference_known and known["role_reference"] is None) or (
                    reference_known and arm=="EXACT_PARENT" and action in ("withdraw","reinstate"))
                if na:
                    if states[slot]["state"]!="NOT_APPLICABLE" or slot in by:missing.append(slot+":N_A_NOT_ESTABLISHED")
                else:required.append(slot)
    for slot in required:
        if states[slot]["state"]!="COMPLETED" or not accepted(by.get(slot)):missing.append(slot+":CALL_UNAVAILABLE")
    return missing

def predecessor(e,phase,arm):
    origin=key(e,"A","ADAPTIVE_PARENT" if arm=="ADAPTIVE_PARENT" else "OCM_ENABLED")
    if phase in ("B","C"):return origin
    for role in ROLES:
        actions=("withdraw","withdrawn","reinstate","restored")
        for i,action in enumerate(actions):
            if phase==role+"-"+action:return origin if i==0 else key(e,role+"-"+actions[i-1],arm)
    raise CustodyFailure("COPY_PHASE")

def lineage(root,calls,copies):
    root=Path(root);by={c["slot"]:c for c in calls};mapped={}
    if len(by)!=len(calls):raise CustodyFailure("RESTART_DUPLICATE_CALL")
    for cp in copies:
        target=Path(cp["target"]);slot=target.name
        if str(root/"stores"/slot)!=cp["target"] or slot in mapped:raise CustodyFailure("COPY_TARGET")
        try:ep,phase,arm=slot.split("--");e=int(ep[1:])
        except (ValueError,TypeError):raise CustodyFailure("COPY_SLOT")
        if ep!=f"e{e}" or e not in range(4) or arm not in ARMS or arm=="EXACT_PARENT" or phase=="A":
            raise CustodyFailure("COPY_SLOT")
        prev=by.get(predecessor(e,phase,arm))
        if not accepted(prev) or prev.get("store_after_audit") is None:raise CustodyFailure("RESTART_PREDECESSOR")
        if cp["source"]!=prev["request"]["store"]:raise CustodyFailure("COPY_ORIGINAL_SOURCE")
        if any(cp[k]!=prev["store_after_audit"] for k in ("before","after","copied")):
            raise CustodyFailure("COPY_PREDECESSOR_IDENTITY")
        mapped[slot]=cp
    for slot,call in by.items():
        ep,phase,arm=slot.split("--");e=int(ep[1:]);request=call["request"]
        if arm=="EXACT_PARENT":
            if request.get("store") is not None:raise CustodyFailure("RESTART_EXACT_STORE")
            continue
        if request.get("store")!=str(root/"stores"/slot):raise CustodyFailure("RESTART_STORE")
        facts=call.get("facts")
        if phase=="A":
            if call.get("store_before_dispatch") is not None:raise CustodyFailure("RESTART_ACQUISITION_NOT_EMPTY")
            if accepted(call) and (facts["prior_uses"]!=0 or facts["use_count"]!=0):
                raise CustodyFailure("RESTART_ACQUISITION_HISTORY")
            continue
        cp=mapped.get(slot)
        if cp is None:raise CustodyFailure("RESTART_COPY_MISSING")
        before=call.get("store_before_dispatch")
        if (before is not None or accepted(call)) and before!=cp["copied"]:
            raise CustodyFailure("COPY_DISPATCH_IDENTITY")
        if facts is not None and facts.get("terminal")=="CHECKED":
            prev=by[predecessor(e,phase,arm)]["facts"]
            if facts["prior_uses"]!=prev["use_count"]:raise CustodyFailure("RESTART_INITIAL_HISTORY")
