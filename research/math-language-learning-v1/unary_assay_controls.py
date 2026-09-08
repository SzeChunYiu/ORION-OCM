"""Predeclared semantic/control decisions over independently authenticated facts."""
from unary_assay_auth import ControlFailure
from unary_assay_phase import ARMS

PRECEDENCE=("SEMANTIC_CONTROL_FAILED","CANNOT_CHECK","NO_METHOD_ACQUIRED",
            "NO_DEVELOPMENT_BENEFIT","NO_CAUSAL_USE","CHECKED_CAUSAL_REUSE_APPARATUS")

def agreement(batches):
    if not batches or any(b["terminal"]!="CHECKED" for b in batches):raise ValueError("INCOMPLETE_AGREEMENT")
    reference=[(r["observation_id"],r["task_sha256"],r["status"]) for r in batches[0]["rows"]]
    for b in batches:
        if [(r["observation_id"],r["task_sha256"],r["status"]) for r in b["rows"]]!=reference:
            raise ControlFailure("PAIRED_ANSWER_DISAGREEMENT")
        seen={}
        for row in b["rows"]:
            digest=row["task_sha256"]
            if digest in seen and seen[digest]!=row["status"]:raise ControlFailure("PRESENTATION_OR_RESTORATION_DISAGREEMENT")
            seen[digest]=row["status"]

def role_transition(facts,role,action,arm,mid):
    if facts["terminal"]!="CHECKED":raise ValueError("INCOMPLETE_ROLE")
    if arm=="EXACT_PARENT":return
    item=facts["methods"][mid]
    withdrawn=action in ("withdraw","withdrawn")
    dead="REVOKED" if arm=="ADAPTIVE_PARENT" else "DEAD"
    if role=="schema_environment":
        expected=(dead,"LIVE",False) if withdrawn else ("LIVE","LIVE",True)
    elif role=="utility":
        expected=("LIVE",dead,False) if withdrawn else ("LIVE","LIVE",True)
    else:expected=("LIVE","LIVE",True)
    if tuple(item[k] for k in ("correctness","selection","eligible"))!=expected:
        raise ControlFailure("ROLE_WARRANT_TRANSITION")
    for row in facts["rows"]:
        use=row["use"]
        if arm=="OCM_KNOCKOUT" and use["recipes_applied"]:raise ControlFailure("KNOCKOUT_ROLE_USE")
        if withdrawn and role=="schema_environment" and use["recipes_applied"]:
            raise ControlFailure("WITHDRAWN_SCHEMA_USE")
        if withdrawn and role=="utility" and use["method_id"]==mid:
            raise ControlFailure("WITHDRAWN_UTILITY_USE")

def causal(rows,semantic_keys,selected):
    groups={}
    for row in rows:
        use=row["use"]
        if row.get("terminal","CHECKED")!="CHECKED" or row["presentation"]!="ast" or not use or not use["recipes_applied"]:continue
        rule=use["rule_id"]
        if rule not in selected:raise ControlFailure("UNSELECTED_CAUSAL_USE")
        groups.setdefault(rule,{})[row["row_id"]]=semantic_keys[row["row_id"]]
    return {rule:{"row_ids":sorted(ids),"semantic_keys":sorted(set(ids.values())),
                  "qualifies":len(ids)>=2 and len(set(ids.values()))>=2} for rule,ids in sorted(groups.items())}

def decide(*,unavailable,selection,ocm_rows,parent_rows,knockout_rows,semantic_keys,selected,control_failure=False):
    ocm=causal(ocm_rows,semantic_keys,selected);parent=causal(parent_rows,semantic_keys,selected)
    bad_knockout=any(r["use"] and r["use"]["recipes_applied"] for r in knockout_rows)
    if control_failure or bad_knockout:terminal=PRECEDENCE[0]
    elif unavailable:terminal=PRECEDENCE[1]
    elif selection=="NO_METHOD_ACQUIRED":terminal=PRECEDENCE[2]
    elif selection=="NO_DEVELOPMENT_BENEFIT":terminal=PRECEDENCE[3]
    elif not any(v["qualifies"] for v in ocm.values()):terminal=PRECEDENCE[4]
    else:terminal=PRECEDENCE[5]
    return {"terminal":terminal,"ocm_causal":ocm,"parent_causal":parent,
            "comparison":"PARENT_SUFFICIENT" if not unavailable and not control_failure and not bad_knockout and any(v["qualifies"] for v in parent.values()) else "PARENT_REUSE_NOT_ESTABLISHED",
            "knockout_invocations":sum(r["use"]["recipes_applied"] for r in knockout_rows if r["use"])}

def overall(episodes,*,expected=4):
    terminal=min((e["terminal"] for e in episodes),key=PRECEDENCE.index) if episodes else "CANNOT_CHECK"
    if len(episodes)!=expected and PRECEDENCE.index(terminal)>1:terminal="CANNOT_CHECK"
    return {"terminal":terminal,"episodes":episodes,"expected_episodes":expected,
            "complete_count":sum(e["terminal"]=="CHECKED_CAUSAL_REUSE_APPARATUS" for e in episodes),
            "scope":"Checked apparatus only; economics and novelty are separate."}
