"""Structural Boolean substitution and cover assembly; outputs remain proposals."""
from itertools import product
from unary_contract import InputRefused, negate
from unary_rule_contract import count, validate_rule
from unary_rule_check import check_rule

def _key(expr,work):
    count(work,"key_nodes")
    return tuple(expr) if expr[0]=="pred" else (expr[0],*(_key(x,work) for x in expr[1:]))

def _match(pattern,actual,bindings,work):
    count(work,"matching_nodes")
    if pattern[0]=="pred":
        key=_key(actual,work);name=pattern[1]
        count(work,"binding_probes")
        if name in bindings:
            count(work,"binding_comparisons")
            return bindings[name][1]==key
        bindings[name]=(actual,key);count(work,"binding_insertions");return True
    if pattern[0]!=actual[0]:return False
    return all(_match(p,a,bindings,work) for p,a in zip(pattern[1:],actual[1:]))

def _statement(pattern,actual,bindings,work):
    count(work,"matching_statement_tests")
    return (pattern["kind"]==actual["kind"] and
            _match(pattern["left"],actual["left"],bindings,work) and
            _match(pattern["right"],actual["right"],bindings,work))

def apply_rule(value,task,engine,prepared):
    work={"recipes_applied":0,"matching_nodes":0,"key_nodes":0}
    rule=validate_rule(value,work);schema=check_rule(rule,work)
    if not schema["accepted"]:raise InputRefused("UNCHECKED_RULE_SCHEMA")
    task,base=engine.inspect_prepared(prepared,task)
    if base["kind"]=="unsat":return {"terminal":"INCONSISTENT_BASE","counters":work}
    universal=task["query"]["kind"] in ("every","no")
    target=task["query"] if universal else negate(task["query"])
    seed={}
    if not _statement(rule["conclusion"],target,seed,work):
        return {"terminal":"NO_MATCH","counters":work}
    index={"every":[],"no":[]}
    for i,premise in enumerate(task["premises"]):
        count(work,"premise_index_reads")
        if premise["kind"] in index:index[premise["kind"]].append(i)
    choices=[]
    for premise in rule["premises"]:
        count(work,"index_probes");choices.append(index[premise["kind"]])
    for indices in product(*choices):
        count(work,"mapping_attempts");count(work,"distinct_index_reads",len(indices))
        if len(set(indices))!=len(indices):continue
        bindings=dict(seed);count(work,"binding_copy_entries",len(seed))
        if not all(_statement(pattern,task["premises"][i],bindings,work)
                   for pattern,i in zip(rule["premises"],indices)):continue
        count(work,"certificate_index_reads",len(indices))
        cover=sorted(indices)
        unsat={"kind":"unsat","obligation":len(task["premises"]),"cover":cover}
        yes,no=(base,unsat) if universal else (unsat,base)
        result=engine.result_from_certificates(prepared,yes,no)
        count(work,"recipes_applied")
        return {"terminal":"PROPOSED","result":result,"method_id":rule["rule_id"],
                "binding":{name:bindings[name][0] for name in rule["parameters"]},
                "cover":cover,"counters":work,"schema_check":schema}
    return {"terminal":"NO_MATCH","counters":work}
