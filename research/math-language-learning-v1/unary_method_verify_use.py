"""Independent structural application check shared by both authority adapters."""
from unary_contract import InputRefused,fields,negate
from unary_verify import verify_result
import unary_method_plain as D

def verify_answer(task,result,*,work,counter):
    if type(work) is not dict:raise TypeError("work must be a dict")
    D.bump(work,counter)
    return verify_result(task,result)

def _expr(pattern,binding,work):
    D.bump(work,"binding_expression_nodes")
    if pattern[0]=="pred":return binding[pattern[1]]
    return [pattern[0],*[_expr(x,binding,work) for x in pattern[1:]]]

def _statement(pattern,binding,work):
    return {"kind":pattern["kind"],"left":_expr(pattern["left"],binding,work),
            "right":_expr(pattern["right"],binding,work)}

def verify_use(task,use,lookup,*,work,current=True):
    if type(work) is not dict:raise TypeError("work must be a dict")
    fields(use,("method_id","rule_id","binding","cover","recipes_applied","replaced_branch"))
    if type(use["recipes_applied"]) is not int or use["recipes_applied"] not in (0,1):raise InputRefused("RECIPE_COUNT")
    if not use["recipes_applied"]:
        if use!={"method_id":None,"rule_id":None,"binding":{},"cover":[],"recipes_applied":0,"replaced_branch":None}:
            raise InputRefused("FALSE_METHOD_USE")
        return
    item=lookup(use["method_id"])
    if current and not item["eligible"]:raise InputRefused("METHOD_NOT_ELIGIBLE")
    rule=item["envelope"]["rule"]
    if use["rule_id"]!=rule["rule_id"]:raise InputRefused("RULE_USE_ID")
    fields(use["binding"],tuple(rule["parameters"]))
    cover=use["cover"]
    if (type(cover) is not list or any(type(i) is not int or not 0<=i<len(task["premises"]) for i in cover)
        or cover!=sorted(set(cover)) or len(cover)!=len(rule["premises"])):raise InputRefused("RULE_USE_COVER")
    instantiated=[_statement(p,use["binding"],work) for p in rule["premises"]]
    actual=[task["premises"][i] for i in cover]
    if sorted(map(D.raw,instantiated))!=sorted(map(D.raw,actual)):raise InputRefused("RULE_USE_SUPPORT")
    universal=task["query"]["kind"] in ("every","no")
    target=task["query"] if universal else negate(task["query"])
    if D.raw(_statement(rule["conclusion"],use["binding"],work))!=D.raw(target):raise InputRefused("RULE_USE_TARGET")
    if use["replaced_branch"]!=("no" if universal else "yes"):raise InputRefused("RULE_USE_BRANCH")
