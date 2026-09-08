"""Compile observed complementary-pivot dependencies, never a supplied target rule."""
from itertools import permutations
from unary_rule_contract import count
from unary_rule_clauses import clause,neg,ordered,statement,subset
from unary_rule_identity import canonical_rule
from unary_rule_clause_apply import matches
from unary_contract import InputRefused
from unary_rule_dependency_check import verify_support

def derive(task,result,support,work):
    cover=support["cover"]
    if len(cover)!=2:
        count(work,"dependency_arity_rejections");return []
    clauses=[clause(task["premises"][i],work) for i in cover]
    if any(len(c)!=2 for c in clauses):
        count(work,"dependency_nonbinary_rejections");return []
    from unary_contract import negate,SCHEMA
    query=task["query"] if support["branch"]=="query_false" else negate(task["query"])
    target=clause(query,work);out=[];seen=set()
    for left,right in permutations(range(2)):
        for pi,pivot in enumerate(clauses[left]):
            count(work,"dependency_pivot_probes")
            if pivot[0]!="pred":continue
            opposite=neg(pivot,work)
            for qi,value in enumerate(clauses[right]):
                count(work,"dependency_complement_tests")
                if value!=opposite:continue
                residuals=[clauses[left][1-pi],clauses[right][1-qi]]
                resolvent=ordered(residuals,work)
                if not subset(resolvent,target,work):
                    count(work,"dependency_link_rejections");continue
                # Assign variables to observed occurrence roles, including equal residuals.
                names=["P0","P1","P2"]
                roles={(left,pi):["pred",names[1]],(right,qi):["not",["pred",names[1]]],
                       (left,1-pi):["pred",names[0]],(right,1-qi):["pred",names[2]]}
                lifted=[[roles[(i,j)] for j in range(2)] for i in range(2)]
                conclusion=[roles[(left,1-pi)],roles[(right,1-qi)]]
                raw={"schema":SCHEMA,"predicates":names,
                     "premises":[statement(ordered(c,work),work) for c in lifted],"query":statement(ordered(conclusion,work),work)}
                rule=canonical_rule(raw,work)
                if rule["rule_id"] in seen:continue
                for binding,_ in matches(rule,[task["premises"][i] for i in cover],statement(resolvent,work),work):
                    count(work,"dependency_binding_candidates")
                    step={"schema":"ocm.unary-pivot-step.v1","order":[cover[left],cover[right]],
                          "pivot":pivot,"residuals":residuals,"resolvent":resolvent,
                          "target":target,"binding":binding}
                    evidence=dict(support,dependency=step)
                    try:checked=verify_support(task,result,evidence,rule,work)
                    except InputRefused as exc:
                        if str(exc)!="DEPENDENCY_ROLE_BINDING":raise
                        count(work,"dependency_role_binding_rejections");continue
                    break
                else:raise RuntimeError("COMPILED_DEPENDENCY_BINDING")
                seen.add(rule["rule_id"]);count(work,"dependency_steps")
                if residuals[0]==residuals[1]:count(work,"dependency_role_splits")
                out.append({"rule":rule,"schema_certificate":checked,"support":evidence})
    return out
