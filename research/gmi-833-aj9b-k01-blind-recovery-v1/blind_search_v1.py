from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = ((0,0),(0,1),(1,0),(1,1))
REQUIRED = (0,1,1,0)
ATOMS = (("x",0),("x",1),("c",-1),("c",0),("c",1))
MAX_OPS = 7


def eval_ast(e):
    op=e[0]
    if op=="x": return tuple(row[e[1]] for row in CASES)
    if op=="c": return (e[1],)*len(CASES)
    if op=="add":
        a,b=eval_ast(e[1]),eval_ast(e[2]); return tuple(x+y for x,y in zip(a,b))
    if op=="neg":
        a=eval_ast(e[1]); return tuple(-x for x in a)
    if op=="pos":
        a=eval_ast(e[1]); return tuple(1 if x>0 else 0 for x in a)
    raise ValueError(op)


def valid_values(v): return all(-3 <= x <= 3 for x in v)

def ast_key(e): return repr(e)


def ast_resources(e):
    if e[0] in ("x","c"):
        return {"operation_nodes":0,"positive_tests":0,"depth":0,"constant_uses":int(e[0]=="c")}
    if e[0]=="add":
        a,b=ast_resources(e[1]),ast_resources(e[2])
        return {
            "operation_nodes":1+a["operation_nodes"]+b["operation_nodes"],
            "positive_tests":a["positive_tests"]+b["positive_tests"],
            "depth":1+max(a["depth"],b["depth"]),
            "constant_uses":a["constant_uses"]+b["constant_uses"]}
    a=ast_resources(e[1])
    return {
        "operation_nodes":1+a["operation_nodes"],
        "positive_tests":a["positive_tests"]+int(e[0]=="pos"),
        "depth":1+a["depth"],
        "constant_uses":a["constant_uses"]}


def size_layered_search():
    by=[{} for _ in range(MAX_OPS+1)]
    for e in ATOMS: by[0].setdefault(eval_ast(e),e)
    seen=set(by[0]); counts=[len(by[0])]
    for size in range(1,MAX_OPS+1):
        cand={}
        for e in by[size-1].values():
            for ne in (("neg",e),("pos",e)):
                v=eval_ast(ne)
                if valid_values(v):
                    old=cand.get(v)
                    if old is None or ast_key(ne)<ast_key(old): cand[v]=ne
        for left_size in range(size):
            right_size=size-1-left_size
            for a in by[left_size].values():
                for b in by[right_size].values():
                    if ast_key(a)>ast_key(b): continue
                    ne=("add",a,b); v=eval_ast(ne)
                    if valid_values(v):
                        old=cand.get(v)
                        if old is None or ast_key(ne)<ast_key(old): cand[v]=ne
        cand={v:e for v,e in cand.items() if v not in seen}
        by[size]=cand; seen |= set(cand); counts.append(len(cand))
        if REQUIRED in cand:
            e=cand[REQUIRED]
            return {"first_exact_cost":size,"expression":e,"semantics":REQUIRED,
                    "raw_resources":ast_resources(e),"new_semantics_by_cost":counts}
    return None


def eval_postfix(tokens):
    stack=[]
    for t in tokens:
        if t=="X0": stack.append(tuple(row[0] for row in CASES))
        elif t=="X1": stack.append(tuple(row[1] for row in CASES))
        elif t=="C-1": stack.append((-1,)*4)
        elif t=="C0": stack.append((0,)*4)
        elif t=="C1": stack.append((1,)*4)
        elif t=="NEG":
            a=stack.pop(); stack.append(tuple(-x for x in a))
        elif t=="POS":
            a=stack.pop(); stack.append(tuple(1 if x>0 else 0 for x in a))
        elif t=="ADD":
            b,a=stack.pop(),stack.pop(); stack.append(tuple(x+y for x,y in zip(a,b)))
        else: raise ValueError(t)
    if len(stack)!=1: raise ValueError("bad postfix program")
    return stack[0]


def postfix_resources(tokens):
    op_nodes=sum(t in {"NEG","POS","ADD"} for t in tokens)
    pos_tests=tokens.count("POS")
    constant_uses=sum(t.startswith("C") for t in tokens)
    depths=[]
    for t in tokens:
        if t in {"X0","X1","C-1","C0","C1"}: depths.append(0)
        elif t in {"NEG","POS"}: depths.append(depths.pop()+1)
        elif t=="ADD":
            b,a=depths.pop(),depths.pop(); depths.append(1+max(a,b))
    return {"operation_nodes":op_nodes,"positive_tests":pos_tests,"depth":depths[0],"constant_uses":constant_uses}


def semantic_cost_closure():
    atoms=(("X0",),("X1",),("C-1",),("C0",),("C1",))
    by=[{} for _ in range(MAX_OPS+1)]
    for p in atoms: by[0].setdefault(eval_postfix(p),p)
    seen=set(by[0]); counts=[len(by[0])]
    for cost in range(1,MAX_OPS+1):
        programs=[]
        for left_cost in range(cost-1,-1,-1):
            right_cost=cost-1-left_cost
            for a in sorted(by[left_cost].values(),reverse=True):
                for b in sorted(by[right_cost].values()):
                    programs.append(a+b+("ADD",))
        for p in sorted(by[cost-1].values(),reverse=True):
            programs.append(p+("POS",)); programs.append(p+("NEG",))
        current={}
        for p in programs:
            v=eval_postfix(p)
            if not valid_values(v) or v in seen: continue
            current[v]=p
        by[cost]=current; seen |= set(current); counts.append(len(current))
        if REQUIRED in current:
            p=current[REQUIRED]
            return {"first_exact_cost":cost,"postfix":p,"semantics":REQUIRED,
                    "raw_resources":postfix_resources(p),"new_semantics_by_cost":counts}
    return None


def jsonable(x):
    if isinstance(x,tuple): return [jsonable(y) for y in x]
    if isinstance(x,dict): return {k:jsonable(v) for k,v in x.items()}
    return x


def main():
    a=size_layered_search(); b=semantic_cost_closure()
    assert a is not None and b is not None
    assert a["first_exact_cost"]==7 and b["first_exact_cost"]==7
    assert tuple(a["semantics"])==REQUIRED and tuple(b["semantics"])==REQUIRED
    assert a["raw_resources"]["positive_tests"]>=2 and b["raw_resources"]["positive_tests"]>=2
    result={
      "schema":"AJ9B_BLIND_OUTCOME_V1",
      "status":"SEARCH_COMPLETE",
      "task_inputs":CASES,
      "required_outputs":REQUIRED,
      "search_1":{"id":"SIZE_LAYERED_SYNTAX_ENUMERATION","presentation":"TREE_AST",**a},
      "search_2":{"id":"SEMANTIC_COST_CLOSURE","presentation":"POSTFIX_STACK_ENCODING",**b},
      "no_exact_candidate_below_operation_cost":7,
      "benchmark_or_family_data_used":False
    }
    result=jsonable(result)
    (HERE/"BLIND_OUTCOME_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__": main()
