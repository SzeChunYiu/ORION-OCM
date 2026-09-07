"""Mechanical proper-subcover discovery from checked training answers only."""
from itertools import combinations
from unary_contract import InputRefused, SCHEMA, fields, negate, task_digest, validate_task
from unary_verify import verify_result
from unary_rule_contract import count
from unary_rule_check import check_rule
from unary_rule_identity import canonical_rule, semantic_key

def _fragment(task,indices,conclusion,work):
    premises=[task["premises"][i] for i in indices];names=set()
    def walk(e):
        count(work,"fragment_nodes")
        if e[0]=="pred":names.add(e[1])
        else:
            for x in e[1:]:walk(x)
    for s in [*premises,conclusion]:walk(s["left"]);walk(s["right"])
    return {"schema":SCHEMA,"predicates":sorted(names),"premises":premises,"query":conclusion}

def acquire(episodes):
    if type(episodes) is not list or not 1<=len(episodes)<=32:raise InputRefused("TRAINING_BOUND")
    work={"subset_candidates":0,"nonessential_rejections":0};attempts=[];groups={}
    for episode_index,episode in enumerate(episodes):
        fields(episode,("task","result"));task=validate_task(episode["task"])
        count(work,"training_verifications")
        if not verify_result(task,episode["result"]):raise InputRefused("UNCHECKED_TRAINING_RESULT")
        semantic=semantic_key(task,work);identity=task_digest(task)
        count(work,"training_task_digests")
        result=episode["result"]
        if result["premises"]["kind"]!="model":continue
        for branch in ("query_true","query_false"):
            cert=result[branch]
            if cert["kind"]!="unsat" or type(cert["obligation"]) is not int or cert["obligation"]!=len(task["premises"]):
                continue
            conclusion=task["query"] if branch=="query_false" else negate(task["query"])
            if conclusion["kind"] not in ("every","no"):continue
            for size in (2,3):
                if size>=len(task["premises"]):continue
                for indices in combinations(cert["cover"],size):
                    count(work,"subset_candidates");count(work,"subset_index_reads",size)
                    fragment=_fragment(task,indices,conclusion,work)
                    rule=canonical_rule(fragment,work);checked=check_rule(rule,work)
                    accepted=checked["accepted"]
                    attempts.append({"episode":episode_index,"branch":branch,"indices":list(indices),
                                     "rule_id":rule["rule_id"],"accepted":accepted,"reason":checked["reason"]})
                    if not accepted:
                        count(work,"schema_rejections")
                        if checked["reason"]=="NON_ESSENTIAL_PREMISE":count(work,"nonessential_rejections")
                        continue
                    group=groups.setdefault(rule["rule_id"],{"rule":rule,"schema_certificate":checked,"supports":{}})
                    group["supports"].setdefault(semantic,{"semantic_key":semantic,"task_sha256":identity,
                                               "episode":episode_index,"branch":branch,"cover":list(indices)})
    selected=[]
    for key in sorted(groups):
        item=groups[key]
        if len(item["supports"])>=2:
            selected.append(dict(item,supports=[item["supports"][k] for k in sorted(item["supports"])]))
        else:count(work,"insufficient_semantic_support")
    return {"terminal":"RULES_ACQUIRED" if selected else "NO_REPEATED_RULE",
            "rules":selected,"attempts":attempts,"counters":work}
