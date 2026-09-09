"""Synthetic stack fixtures only: their marker is not native acceptance."""
from copy import deepcopy


def substitute(tokens,mapping):
    return [part for token in tokens for part in mapping.get(token,[token])]


def fixture(kind="wff", names=("ph","ps","ch"), float_labels=("wph","wps","wch")):
    p,q,z=names
    implies=lambda a,b:["|-","(",a,"->",b,")"] if kind=="wff" else ["|-",a,"C_",b]
    h0,h1,out=implies(p,q),implies(q,z),implies(p,z)
    joined=(["|-","(",p,"->","(",q,"/\\",z,")",")"] if kind=="wff"
            else ["|-","("]+h0[1:]+["/\\"]+out[1:]+[")"])
    floats=[{"label":label,"statement":[kind,var]} for label,var in zip(float_labels,names)]
    holes=[{"label":"h0","statement":h0},{"label":"h1","statement":h1}]
    rows={h["label"]:{"label":h["label"],"kind":"$f","statement":h["statement"],"span":[0,1]} for h in floats}
    rows.update({h["label"]:{"label":h["label"],"kind":"$e","statement":h["statement"],"span":[0,1]} for h in holes})
    for label,ess,target in [("compose",[h0,h1],out),("pair",[h0,out],joined),("wrap",[joined],joined)]:
        rows[label]={"label":label,"kind":"$a","floating":deepcopy(floats),
                     "essential":[{"label":label+"."+str(i),"statement":s} for i,s in enumerate(ess)],
                     "statement":target,"dv":[],"span":[1,2]}
    inner=list(float_labels)+["h0"]+list(float_labels)+["h0","h1","compose","pair"]
    proof=list(float_labels)+inner+["wrap"]
    source={"label":"synthetic-root","kind":"$p","floating":floats,"essential":holes,
            "statement":joined,"dv":[],"active_dv":[],"span":[100,101]}
    return trace_from_proof(source,rows,proof),rows,inner


def trace_from_proof(source,rows,proof):
    stack=[];nodes=[];events=[]
    for label in proof:
        row=rows[label];i=len(nodes)
        if row["kind"] in ("$f","$e"):
            node={"id":i,"kind":"floating_hypothesis" if row["kind"]=="$f" else "essential_hypothesis",
                  "label":label,"inputs":[],"output":deepcopy(row["statement"])}
        else:
            hs=row["floating"]+row["essential"];inputs=stack[-len(hs):];del stack[-len(hs):]
            m={h["statement"][1]:nodes[j]["output"][1:] for h,j in zip(row["floating"],inputs)}
            node={"id":i,"kind":"semantic_application" if row["statement"][0]=="|-" else "syntax_application",
                  "label":label,"assertion_kind":row["kind"],"inputs":inputs,
                  "output":substitute(row["statement"],m),"substitution":m,
                  "obligations":[{"kind":"floating" if k<len(row["floating"]) else "essential",
                                  "hypothesis":h["label"],"from":j,"expected":substitute(h["statement"],m)}
                                 for k,(h,j) in enumerate(zip(hs,inputs))],
                  "distinct_variable_obligations":[]}
        nodes.append(node);events.append({"kind":"step","node":i});stack.append(i)
    assert stack==[len(nodes)-1]
    return {"terminal":"NATIVE_VERIFIED","label":source["label"],"source":source,"nodes":nodes,
            "events":events,"root":len(nodes)-1,"external_logical_hypotheses":deepcopy(source["essential"])}
