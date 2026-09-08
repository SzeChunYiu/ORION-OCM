"""Bounded ordinary P1 screen; no native acceptance or useful-learning claim."""
import typed_alias as A
import typed_context as TC
import typed_grammar as G
import typed_boolean as B
from vendor import legacy_class_terms as L

def substitute(ts,m):return [x for t in ts for x in m.get(t,[t])]
def syntax_proof(kind,tokens,parameters,catalogue):
    """Reuse registered parsers; emit exact existing syntax contracts only."""
    G.checker(parameters)(kind,tokens)
    declared=parameters[0]["type"];leaves={k:"cut-f"+str(i) for i,k in enumerate(TC.IDS)}
    if declared=="class":
        raw=L.syntax(kind,[dict(zip(TC.IDS,L.ATOMS)).get(t,t) for t in tokens])
        proof=[dict(zip(["c"+a for a in L.ATOMS],leaves.values())).get(t,t) for t in raw]
    else:
        tree=B.parse_expression(["|-"]+tokens,dict.fromkeys(TC.IDS,declared))["body"]
        def visit(n):
            if n["op"]=="variable":return [leaves[n["name"]]]
            if n["op"]=="not":return visit(n["argument"])+["wn"]
            return visit(n["left"])+visit(n["right"])+[{"implies":"wi","and":"wa","or":"wo","iff":"wb"}[n["op"]]]
        proof=visit(tree)
    stack=[];floats={label:[declared,var] for var,label in leaves.items()}
    for label in proof:
        if label in floats:stack.append(floats[label]);continue
        row=catalogue[label]
        if row["kind"] not in ("$a","$p") or row["essential"] or row["dv"]:raise ValueError("syntax contract scope")
        fs=row["floating"];n=len(fs)
        if not n or len(stack)<n:raise ValueError("syntax stack")
        supplied=stack[-n:];del stack[-n:]
        if any(x[0]!=h["statement"][0] for x,h in zip(supplied,fs)):raise ValueError("syntax type")
        mapping={h["statement"][1]:x[1:] for x,h in zip(supplied,fs)}
        stack.append(substitute(row["statement"],mapping))
    if stack!=[[kind]+tokens]:raise ValueError("syntax conclusion")
    return proof

def screen(body,contracts,work):
    syntax=G.checker(body["parameters"])
    try:A.ground_guard(body["query"],body["premises"],syntax)
    except (ValueError,KeyError,TypeError,IndexError,RecursionError) as exc:
        return {"status":"UNKNOWN","coverage_complete":False,"reasons":[str(exc)],"aliases":[],"native_acceptance":False}
    catalogue={row["label"]:row for row in contracts};unknown=[];answers=[]
    if len(catalogue)!=len(contracts):raise ValueError("duplicate P1 labels")
    for i,p in enumerate(body["premises"]):
        if p==body["query"]:
            answers.append({"kind":"hypothesis_return","premise_indices":[i],"proof":["cut-h"+str(i)]})
    for row in contracts:
        A.count(work,"P1_assertions_visited")
        try:
            if any(h["statement"][0] not in ("wff","class","setvar") for h in row["floating"]):
                raise ValueError("unsupported floating type")
            for witness in A.applications(row,body["query"],body["premises"],work,syntax):
                proof=[]
                for h in row["floating"]:
                    A.count(work,"syntax_proof_requests")
                    proof+=syntax_proof(h["statement"][0],witness["substitution"][h["statement"][1]],body["parameters"],catalogue)
                proof+=["cut-h"+str(i) for i in witness["premise_indices"]]+[row["label"]]
                answers.append({"kind":"one_logical_assertion",**witness,"proof":proof})
        except (ValueError,KeyError,TypeError,IndexError,RecursionError) as exc:
            unknown.append({"label":row.get("label"),"reason":type(exc).__name__+": "+str(exc)})
    return {"status":"ALIAS_FOUND_PROOF_READY" if answers else "UNKNOWN" if unknown else "SCREENED_NEGATIVE_IN_DOMAIN",
            "coverage_complete":not unknown,"reasons":unknown,"aliases":answers,"native_acceptance":False,
            "scope":"Direct hypothesis return or one P1 logical assertion, arbitrary allowed hypothesis reuse/omission/order, exact registered typed ground grammar; syntax proof proposals replayed structurally, not through the native verifier."}
