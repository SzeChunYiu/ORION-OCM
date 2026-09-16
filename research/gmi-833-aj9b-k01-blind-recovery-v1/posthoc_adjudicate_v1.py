from __future__ import annotations
import hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BENCH=ROOT/"gmi-833-aj9a-known-family-benchmark-v1"/"KNOWN_FAMILY_BENCHMARK_V1.json"
OUTCOME=HERE/"BLIND_OUTCOME_V1.json"
EXPECTED_BLOB="6b9ac3095c90d74e2717671a70ad7cc18955310c"
CASES=((0,0),(0,1),(1,0),(1,1))


def git_blob_sha(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def tup(x):
    return tuple(tup(y) for y in x) if isinstance(x,list) else x


def rpn_to_ast(tokens):
    st=[]
    for t in tokens:
        if t=="X0": st.append(("x",0))
        elif t=="X1": st.append(("x",1))
        elif t=="C-1": st.append(("c",-1))
        elif t=="C0": st.append(("c",0))
        elif t=="C1": st.append(("c",1))
        elif t=="NEG": st.append(("neg",st.pop()))
        elif t=="POS": st.append(("pos",st.pop()))
        elif t=="ADD":
            b,a=st.pop(),st.pop(); st.append(("add",a,b))
        else: raise ValueError(t)
    if len(st)!=1: raise ValueError("malformed postfix")
    return st[0]


def eval_ast(e,row):
    op=e[0]
    if op=="x": return row[e[1]]
    if op=="c": return e[1]
    if op=="add": return eval_ast(e[1],row)+eval_ast(e[2],row)
    if op=="neg": return -eval_ast(e[1],row)
    if op=="pos": return int(eval_ast(e[1],row)>0)
    raise ValueError(op)


def affine_form(e):
    op=e[0]
    if op=="x": return (1,0,0) if e[1]==0 else (0,1,0)
    if op=="c": return (0,0,e[1])
    if op=="neg":
        f=affine_form(e[1]); return None if f is None else tuple(-z for z in f)
    if op=="add":
        a,b=affine_form(e[1]),affine_form(e[2])
        return None if a is None or b is None else tuple(x+y for x,y in zip(a,b))
    return None


def pos_affine_sites(e,out=None):
    if out is None: out=[]
    if e[0]=="pos":
        f=affine_form(e[1])
        if f is not None: out.append((f,e))
    for child in e[1:]:
        if isinstance(child,tuple): pos_affine_sites(child,out)
    return out


def depth(e):
    kids=[child for child in e[1:] if isinstance(child,tuple)]
    return 0 if not kids else 1+max(depth(k) for k in kids)


def affine_on_binary(values):
    f00,f01,f10,f11=values
    a=f10-f00; b=f01-f00; c=f00
    return f11==a+b+c


def inspect_candidate(e,required):
    output=tuple(eval_ast(e,row) for row in CASES)
    sites=pos_affine_sites(e,[])
    forms=[f for f,_ in sites]
    two_signal=[f for f in forms if f[0]!=0 and f[1]!=0]
    nonlinear=[]
    for _,node in sites:
        vals=tuple(eval_ast(node,row) for row in CASES)
        if not affine_on_binary(vals): nonlinear.append(vals)
    checks={
      "protected_io": output==tuple(required),
      "acyclic_multistage": depth(e)>=3,
      "multiple_numeric_mixing_sites": len(forms)>=2,
      "non_affine_internal_response": len(nonlinear)>=1,
      "reused_mix_test_construction": len(set(forms))>=2,
      "two_incoming_signal_intervention_ready": len(two_signal)>=2
    }
    return {"pass":all(checks.values()),"checks":checks,"mixing_forms":forms,"non_affine_witnesses":nonlinear,"depth":depth(e),"output":output}


def main():
    data=BENCH.read_bytes()
    assert git_blob_sha(data)==EXPECTED_BLOB
    bench=json.loads(data)
    family=next(f for f in bench["families"] if f["family_id"]=="K01")
    outcome=json.loads(OUTCOME.read_text())
    a=tup(outcome["search_1"]["expression"])
    b=rpn_to_ast(outcome["search_2"]["postfix"])
    ia=inspect_candidate(a,outcome["required_outputs"])
    ib=inspect_candidate(b,outcome["required_outputs"])
    required_clauses=family["posthoc_fingerprint"]["required"]
    assert len(required_clauses)==4
    observation_tests=family["minimum_observation_tests"]
    assert len(observation_tests)>=3
    result={
      "schema":"AJ9B_POSTHOC_ADJUDICATION_V1",
      "benchmark_blob":EXPECTED_BLOB,
      "family_id":"K01",
      "paper_name":family["paper_name"],
      "adjudication_started_after_blind_outcome":True,
      "search_1":ia,
      "search_2":ib,
      "frozen_required_clause_count":len(required_clauses),
      "frozen_observation_test_count":len(observation_tests),
      "learning_extension_claimed":False,
      "terminal":"RECOVERED" if ia["pass"] and ib["pass"] else "NOT_RECOVERED_AT_SCOPE"
    }
    (HERE/"POSTHOC_RESULT_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__": main()
