"""Pure transport prerequisites; does not prove native validity or cut eligibility."""
def prepare(trace,rows,S):
    if trace is None:return None,{},"OBSERVER_DID_NOT_PRODUCE_TRACE"
    source=trace["source"];nodes=trace["nodes"]
    if source["dv"] or source["active_dv"]:return None,{},"OUTSIDE_NO_DV_INTERFACE"
    if not isinstance(nodes,list) or not 1<=len(nodes)<=256:
        return None,{},"OUTSIDE_NODE_INTERFACE"
    used={node["label"] for node in nodes if "label" in node}
    contracts={}
    for label in sorted(used):
        row=rows[label]
        if label!=row["label"] or row["span"][0]>=source["span"][0]:
            raise ValueError("used contract/source-order mismatch")
        if row["kind"] in {"$f","$e"}:
            hypotheses=source["floating" if row["kind"]=="$f" else "essential"]
            if not any(h["label"]==label and h["statement"]==row["statement"] for h in hypotheses):
                return None,{},"OUTSIDE_MANDATORY_HYPOTHESIS_INTERFACE"
        elif row["kind"] not in {"$a","$p"}:
            raise ValueError("used contract kind")
        elif row["dv"]:return None,{},"OUTSIDE_USED_CONTRACT_NO_DV_INTERFACE"
        contracts[label]={**S.contract(row),"span":list(row["span"])}
    return trace,contracts,None
