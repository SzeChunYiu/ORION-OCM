from __future__ import annotations
import itertools, json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def requirement(task, history, x):
    if task=="TEMPORAL_A":
        return history[-1] if history else 0
    if task=="CURRENT_B":
        return x
    raise ValueError(task)


def response_signature(task, history, alphabet):
    return tuple(requirement(task, history, x) for x in alphabet)


def signature_quotient_synthesis(task, m):
    alphabet=tuple(range(m))
    probes=[()] + [(x,) for x in alphabet]
    sig_to_rep={}
    for h in probes:
        sig=response_signature(task,h,alphabet)
        sig_to_rep.setdefault(sig,h)
    signatures=sorted(sig_to_rep)
    index={sig:i for i,sig in enumerate(signatures)}
    table={}
    for sig in signatures:
        s=index[sig]; h=sig_to_rep[sig]
        for x in alphabet:
            y=requirement(task,h,x)
            next_sig=response_signature(task,h+(x,),alphabet)
            if next_sig not in index:
                return {"terminal":"NOT_RECOVERED_AT_SCOPE","reason":"successor signature outside probe quotient"}
            table[(s,x)]=(index[next_sig],y)
    return {"terminal":"RECOVERED","q":len(signatures),"initial":index[response_signature(task,(),alphabet)],"table":table,"method":"SIGNATURE_QUOTIENT"}


def _histories(alphabet, depth=2):
    out=[()]
    for n in range(1,depth+1): out.extend(itertools.product(alphabet,repeat=n))
    return out


def constraint_synthesis(task, m, qmax):
    alphabet=tuple(range(m)); hs=_histories(alphabet,2)
    rows={h:response_signature(task,h,alphabet) for h in hs}
    total_visited=0
    for q in range(1,qmax+1):
        assignment={():0}; outrows={0:rows[()]}; transitions={}; used=1; visited=0
        ordered=hs[1:]

        def dfs(i, used):
            nonlocal visited
            visited += 1
            if i==len(ordered):
                if len(outrows)>q: return None
                return dict(assignment),dict(outrows),dict(transitions)
            h=ordered[i]; row=rows[h]
            pred=h[:-1]; symbol=h[-1]; ps=assignment[pred]
            options=[s for s,r in outrows.items() if r==row]
            if used<q: options.append(used)
            for s in options:
                created=s not in outrows
                oldt=transitions.get((ps,symbol),None)
                if oldt is not None and oldt!=s: continue
                assignment[h]=s
                if created: outrows[s]=row
                transitions[(ps,symbol)]=s
                ans=dfs(i+1,max(used,s+1))
                if ans is not None: return ans
                assignment.pop(h,None)
                if oldt is None: transitions.pop((ps,symbol),None)
                else: transitions[(ps,symbol)]=oldt
                if created: outrows.pop(s,None)
            return None

        sol=dfs(0,used); total_visited += visited
        if sol is not None:
            assignment,outrows,transitions=sol
            table={}
            for s,row in outrows.items():
                for x in alphabet:
                    ns=transitions.get((s,x))
                    if ns is None:
                        return {"terminal":"NOT_RECOVERED_AT_SCOPE","reason":"incomplete transition table","visited":total_visited}
                    table[(s,x)]=(ns,row[x])
            return {"terminal":"RECOVERED","q":len(outrows),"initial":0,"table":table,"method":"INCREMENTAL_CONSTRAINTS","visited":total_visited}
    return {"terminal":"NOT_RECOVERED_AT_SCOPE","reason":"no model within registered state bound","visited":total_visited}


def run_machine(model, word):
    s=model["initial"]; out=[]
    for x in word:
        s,y=model["table"][(s,x)]; out.append(y)
    return tuple(out)


def expected(task, word):
    h=(); out=[]
    for x in word:
        out.append(requirement(task,h,x)); h=h+(x,)
    return tuple(out)


def exact_protected(model, task, m, horizon):
    alphabet=tuple(range(m)); checked=0
    for n in range(horizon+1):
        for w in itertools.product(alphabet,repeat=n):
            if run_machine(model,w)!=expected(task,w): return False,checked,w
            checked += 1
    return True,checked,None


def canonical_table(model,m):
    return tuple(model["table"][(s,x)] for s in range(model["q"]) for x in range(m))


def raw_space_bits(q,m):
    # (q*m) choices for each of q*m rows; here q*m is a power of two.
    choices=q*m
    assert choices>0 and choices & (choices-1)==0
    return q*m*(choices.bit_length()-1)


def run_all():
    m=8; horizon=4
    result={"schema":"AJ15_BLIND_LARGE_OUTCOME_V1","m":m,"horizon":horizon,"tasks":{}}
    for task in ("TEMPORAL_A","CURRENT_B"):
        a=signature_quotient_synthesis(task,m)
        b=constraint_synthesis(task,m,m)
        if a["terminal"]!="RECOVERED" or b["terminal"]!="RECOVERED":
            result["tasks"][task]={"terminal":"NOT_RECOVERED_AT_SCOPE","route_a":a["terminal"],"route_b":b["terminal"]}
            continue
        oka,ca,wa=exact_protected(a,task,m,horizon)
        okb,cb,wb=exact_protected(b,task,m,horizon)
        result["tasks"][task]={
            "terminal":"RECOVERED" if oka and okb else "NOT_RECOVERED_AT_SCOPE",
            "route_a_states":a["q"],"route_b_states":b["q"],
            "route_a_protected_checks":ca,"route_b_protected_checks":cb,
            "behavioral_agreement":all(run_machine(a,w)==run_machine(b,w) for n in range(horizon+1) for w in itertools.product(range(m),repeat=n)),
            "constraint_nodes_visited":b.get("visited",0),
            "route_a_method":a["method"],"route_b_method":b["method"],
        }
        if task=="TEMPORAL_A":
            result["tasks"][task]["raw_registered_transducer_space_bits"]=raw_space_bits(8,8)
            result["tasks"][task]["raw_registered_transducer_space_exact"]="64^64"
    return result


if __name__=="__main__":
    r=run_all()
    (HERE/"BLIND_LARGE_OUTCOME_V1.json").write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,sort_keys=True))
