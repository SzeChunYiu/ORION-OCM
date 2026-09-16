from __future__ import annotations
import itertools, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
BITS=(0,1)
CASES=tuple(itertools.product(BITS,repeat=3))
REQUIRED=tuple(a if c==0 else b for c,a,b in CASES)
ATOMS=(("v",0),("v",1),("v",2),("k",0),("k",1))
MAX_OPS=5


def eval_ast(e):
    op=e[0]
    if op=="v": return tuple(s[e[1]] for s in CASES)
    if op=="k": return (e[1],)*len(CASES)
    if op=="not": return tuple(1-x for x in eval_ast(e[1]))
    a=eval_ast(e[1]); b=eval_ast(e[2])
    if op=="and": return tuple(x & y for x,y in zip(a,b))
    if op=="or": return tuple(x | y for x,y in zip(a,b))
    raise ValueError(op)


def resources(e):
    if e[0] in ("v","k"): return {"operation_nodes":0,"depth":0}
    if e[0]=="not":
        r=resources(e[1]); return {"operation_nodes":r["operation_nodes"]+1,"depth":r["depth"]+1}
    a,b=resources(e[1]),resources(e[2])
    return {"operation_nodes":1+a["operation_nodes"]+b["operation_nodes"],"depth":1+max(a["depth"],b["depth"])}


def size_layered_expression_search():
    by=[{} for _ in range(MAX_OPS+1)]
    for e in ATOMS: by[0].setdefault(eval_ast(e),e)
    seen=set(by[0]); counts=[len(by[0])]
    for size in range(1,MAX_OPS+1):
        cand={}
        for e in by[size-1].values():
            ne=("not",e); v=eval_ast(ne)
            if v not in cand: cand[v]=ne
        for l in range(size):
            r=size-1-l
            for a in by[l].values():
                for b in by[r].values():
                    if repr(a)>repr(b): continue
                    for op in ("or","and"):
                        ne=(op,a,b); v=eval_ast(ne)
                        if v not in cand: cand[v]=ne
        cand={v:e for v,e in cand.items() if v not in seen}
        by[size]=cand; seen |= set(cand); counts.append(len(cand))
        if REQUIRED in cand:
            e=cand[REQUIRED]
            return {"first_exact_cost":size,"expression":e,"semantics":REQUIRED,
                    "new_semantics_by_cost":counts,"raw_resources":resources(e)}
    return None


def cube_matches(cube,state):
    return all(v==-1 or state[i]==v for i,v in enumerate(cube))


def exact_dnf_cube_cover():
    positives={i for i,y in enumerate(REQUIRED) if y}
    implicants=[]
    for cube in itertools.product((-1,0,1),repeat=3):
        covered={i for i,s in enumerate(CASES) if cube_matches(cube,s)}
        if covered and covered <= positives:
            implicants.append((cube,covered,sum(v!=-1 for v in cube)))
    checked=0; covers=[]
    for n in range(1,4):
        for combo in itertools.combinations(implicants,n):
            checked+=1
            union=set().union(*(x[1] for x in combo))
            if union==positives: covers.append(combo)
        if covers: break
    min_literals=min(sum(x[2] for x in cover) for cover in covers)
    covers=[c for c in covers if sum(x[2] for x in c)==min_literals]
    assert len(covers)==1
    cubes=tuple(x[0] for x in covers[0])
    return {"valid_implicants":len(implicants),"cover_candidates_checked":checked,
            "cube_count":len(cubes),"literal_count":min_literals,"cubes":cubes}


def main():
    a=size_layered_expression_search(); b=exact_dnf_cube_cover()
    assert a is not None and a["first_exact_cost"]==4
    assert a["new_semantics_by_cost"]==[5,9,26,44,37]
    assert tuple(a["semantics"])==REQUIRED
    expected=("or",("and",("not",("v",0)),("v",1)),("and",("v",0),("v",2)))
    assert a["expression"]==expected
    assert b["valid_implicants"]==7 and b["cover_candidates_checked"]==28
    assert b["cube_count"]==2 and b["literal_count"]==4
    assert set(b["cubes"])=={(0,1,-1),(1,-1,1)}
    result={
      "schema":"AJ9E_BLIND_BOOLEAN_OUTCOME_V1","status":"SEARCH_COMPLETE",
      "required_semantics":REQUIRED,
      "search_1":{"id":"SIZE_LAYERED_BOOLEAN_EXPRESSION","presentation":"BOOLEAN_AST",**a},
      "search_2":{"id":"EXACT_DNF_CUBE_COVER","presentation":"DNF_CUBE_SET",**b},
      "raw_resource_vector":{"operation_nodes":4,"cube_count":2,"literal_count":4,"depth":3},
      "registry_data_used":False
    }
    (HERE/"BLIND_OUTCOME_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
