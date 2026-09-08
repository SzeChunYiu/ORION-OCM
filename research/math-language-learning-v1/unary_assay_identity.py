"""Exact syntax identity and released semantic identity; no answer selection."""
from itertools import permutations
import hashlib
from unary_contract import InputRefused,validate_task
from unary_rule_contract import count,encoded
from unary_rule_identity import semantic_key
from unary_assay_stream import NAMES,SPLITS

def used_names(task,*,work):
    used=set();grouped=False
    def visit(e):
        nonlocal grouped
        count(work,"gate_expression_nodes")
        if type(e) is not list or not e:raise InputRefused("INVALID_EXPRESSION")
        if e[0]=="pred" and len(e)==2:
            if type(e[1]) is not str:raise InputRefused("INVALID_PREDICATE_NAME")
            used.add(e[1])
        elif (e[0]=="not" and len(e)==2) or (e[0] in ("and","or") and len(e)==3):
            grouped=True
            for x in e[1:]:visit(x)
        else:raise InputRefused("INVALID_EXPRESSION")
    for s in [*task["premises"],task["query"]]:
        visit(s["left"]);visit(s["right"])
    return used,grouped

def gate(task,split,*,work):
    if split not in SPLITS:raise InputRefused("SPLIT")
    names,grouped=used_names(task,work=work)
    if names!=set(NAMES):return "MISSING_PREDICATE"
    if split!="train" and not grouped:return "MISSING_BOOLEAN_GROUP"
    validate_task(task)
    return None

def syntax_key(value,*,work):
    task=validate_task(value);names=task["predicates"]
    if len(names)!=3:raise InputRefused("SYNTAX_IDENTITY_BOUND")
    best=None
    for targets in permutations(NAMES):
        count(work,"syntax_renamings");rename=dict(zip(names,targets))
        def walk(e):
            count(work,"syntax_expression_nodes")
            return ["pred",rename[e[1]]] if e[0]=="pred" else [e[0],*[walk(x) for x in e[1:]]]
        def statement(s):return {"kind":s["kind"],"left":walk(s["left"]),"right":walk(s["right"])}
        premises=sorted([statement(s) for s in task["premises"]],key=lambda s:encoded(s,work))
        candidate={"schema":task["schema"],"predicates":list(NAMES),"premises":premises,"query":statement(task["query"])}
        raw=encoded(candidate,work);count(work,"syntax_key_comparisons")
        if best is None or raw<best:best=raw
    count(work,"bytes_hashed",len(best));count(work,"syntax_hash_calls")
    return hashlib.sha256(best).hexdigest()
