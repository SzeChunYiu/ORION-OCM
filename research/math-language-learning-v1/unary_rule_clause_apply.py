"""Normalized matching after the original structural route; no query solve."""
from itertools import permutations,product
from unary_rule_contract import count
from unary_rule_clauses import clause,normal,neg,ordered,substituted,subset

LINK="ocm.unary-clause-link.v1"

def match(rule,premises,target,work):
    patterns=[clause(p,work) for p in rule["premises"]]
    actual=[clause(p,work) for p in premises];goal=clause(target,work)
    for order in permutations(range(len(actual))):
        count(work,"mapping_attempts")
        choices=[list(product(actual[i],repeat=len(p))) for p,i in zip(patterns,order)]
        for values in product(*choices):
            count(work,"clause_binding_combinations")
            binding={};valid=True
            for pattern,terms in zip(patterns,values):
                for p,a in zip(pattern,terms):
                    count(work,"matching_nodes");count(work,"binding_probes")
                    if p[0]=="pred":name=p[1];value=a
                    elif p[0]=="not" and p[1][0]=="pred":name=p[1][1];value=neg(a,work)
                    else:valid=False;break
                    value=normal(value,work)
                    if name in binding:
                        count(work,"binding_comparisons")
                        if binding[name]!=value:valid=False;break
                    else:binding[name]=value;count(work,"binding_insertions")
                if not valid:break
            if not valid or set(binding)!=set(rule["parameters"]):continue
            instantiated=[clause(substituted(p,binding,work),work) for p in rule["premises"]]
            count(work,"clause_equivalence_comparisons",len(actual))
            if any(p!=actual[i] for p,i in zip(instantiated,order)):continue
            conclusion=clause(substituted(rule["conclusion"],binding,work),work)
            if subset(conclusion,goal,work):
                return binding,{"schema":LINK,"premises":actual,"conclusion":conclusion,"target":goal}
    return None

def apply(rule,task,engine,prepared,base,target,universal,work):
    from itertools import combinations
    indices=[]
    for i,p in enumerate(task["premises"]):
        count(work,"premise_index_reads")
        if p["kind"] in ("every","no"):indices.append(i)
    count(work,"index_probes")
    for cover in combinations(indices,len(rule["premises"])):
        count(work,"mapping_attempts");count(work,"certificate_index_reads",len(cover))
        found=match(rule,[task["premises"][i] for i in cover],target,work)
        if found is None:continue
        binding,link=found
        from unary_rule_dependency_check import verify_link
        verify_link(rule,task,list(cover),binding,link,work)
        unsat={"kind":"unsat","obligation":len(task["premises"]),"cover":list(cover)}
        yes,no=(base,unsat) if universal else (unsat,base)
        result=engine.result_from_certificates(prepared,yes,no);count(work,"recipes_applied")
        return {"terminal":"PROPOSED","result":result,"method_id":rule["rule_id"],
                "binding":binding,"cover":list(cover),"counters":work,"dependency":link}
    return {"terminal":"NO_MATCH","counters":work}
