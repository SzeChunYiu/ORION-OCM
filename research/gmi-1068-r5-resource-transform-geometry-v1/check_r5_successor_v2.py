#!/usr/bin/env python3
import json
import pathlib
import sys
from fractions import Fraction

ROOT=pathlib.Path(__file__).resolve().parent
RESEARCH=ROOT.parent

NODES=("A","B","C")
EDGES={
    ("A","B"):[(1,0)],
    ("B","C"):[(0,2)],
    ("A","C"):[(2,1)],
}

def need(cond,msg):
    if not cond:
        raise RuntimeError(msg)

def add(a,b):
    return (a[0]+b[0],a[1]+b[1])

def paths(start,target,edges=EDGES):
    out=[]
    if start==target:
        out.append(((),(0,0)))
    def dfs(node,seen,names,cost):
        if len(seen)>len(NODES):
            return
        for (src,dst),costs in edges.items():
            if src!=node or dst in seen:
                continue
            for c in costs:
                nc=add(cost,c)
                nn=names+((src,dst,c),)
                if dst==target:
                    out.append((nn,nc))
                dfs(dst,seen|{dst},nn,nc)
    dfs(start,{start},(),(0,0))
    return out

def cost_set(a,b,edges=EDGES):
    return sorted({c for _,c in paths(a,b,edges)})

def dominates(a,b):
    return a[0]<=b[0] and a[1]<=b[1] and a!=b

def pareto(vs):
    vals=set(vs)
    return sorted(v for v in vals if not any(dominates(u,v) for u in vals if u!=v))

def score(w,c):
    return w[0]*c[0]+w[1]*c[1]

def distance(a,b,w,edges=EDGES):
    cs=cost_set(a,b,edges)
    if not cs:
        return None
    return min(score(w,c) for c in cs)

def ball(a,r,w,edges=EDGES):
    return sorted(n for n in NODES if distance(a,n,w,edges) is not None and distance(a,n,w,edges)<=r)

def rename_graph(rename,edges=EDGES,mutate_direct=False):
    out={}
    for (a,b),costs in edges.items():
        vals=list(costs)
        if mutate_direct and (a,b)==("A","C"):
            vals=[(0,0)]
        out[(rename[a],rename[b])]=vals
    return out

def named_cost_set(a,b,edges,nodes):
    # Same independent path logic but accepts relabeled node set.
    out=[]
    if a==b: out.append((0,0))
    def dfs(node,seen,cost):
        for (src,dst),costs in edges.items():
            if src!=node or dst in seen: continue
            for c in costs:
                nc=add(cost,c)
                if dst==b: out.append(nc)
                dfs(dst,seen|{dst},nc)
    dfs(a,{a},(0,0))
    return sorted(set(out))

def main():
    r4=json.loads((RESEARCH/"gmi-1068-r4-equivalence-state-quotient-v1"/"RESULT_V2.json").read_text())
    need(r4["status"]=="GREEN_AT_REGISTERED_THREE_WAY_RESPONSE_QUOTIENT_SCOPE","R4_S1_PARENT_NOT_GREEN")

    cs=cost_set("A","C")
    p=pareto(cs)
    need(cs==[(1,2),(2,1)],f"COST_SET:{cs}")
    need(p==[(1,2),(2,1)],f"PARETO:{p}")
    need(cost_set("C","A")==[],"UNREACHABLE")

    weights=((1,3),(3,1))
    ds={}
    for w in weights:
        ds[str(w)]={
            "AA":distance("A","A",w),
            "AB":distance("A","B",w),
            "BC":distance("B","C",w),
            "AC":distance("A","C",w),
        }
        d=ds[str(w)]
        need(d["AA"]==0,"IDENTITY_ZERO")
        need(d["AC"]<=d["AB"]+d["BC"],f"TRIANGLE:{w}:{d}")
    need(ds[str((1,3))]["AC"]==5 and ds[str((3,1))]["AC"]==5,"DISTANCES")

    b1=ball("A",1,(1,3))
    b5=ball("A",5,(1,3))
    need(b1==["A","B"] and b5==["A","B","C"],f"BALLS:{b1}:{b5}")

    rename={"A":"X","B":"Y","C":"Z"}
    rg=rename_graph(rename)
    rcs=named_cost_set("X","Z",rg,("X","Y","Z"))
    rp=pareto(rcs)
    need(rcs==cs and rp==p,"RELABEL_TRANSPORT")

    badg=rename_graph(rename,mutate_direct=True)
    badcs=named_cost_set("X","Z",badg,("X","Y","Z"))
    badp=pareto(badcs)
    need(badcs!=cs and badp!=p and badp==[(0,0)],f"RELABEL_NEGATIVE:{badcs}:{badp}")

    descending=[Fraction(1,n) for n in range(1,65)]
    need(all(descending[i+1] < descending[i] for i in range(len(descending)-1)),"DESCENDING_PREFIX")
    # Analytic boundary is stated in THEORY_V2: for every n, 1/(n+1)<1/n.
    # This finite prefix only guards the executable arithmetic route.

    hostiles=[
        cost_set("C","A")==[],
        len(p)==2,
        ds[str((1,3))]["AA"]==0,
        all(ds[str(w)]["AC"]<=ds[str(w)]["AB"]+ds[str(w)]["BC"] for w in weights),
        b1!=b5,
        rcs==cs,
        rp==p,
        badcs!=cs,
        badp!=p,
        all(descending[i+1] < descending[i] for i in range(len(descending)-1)),
    ]
    need(all(hostiles),f"HOSTILES:{hostiles}")

    res=json.loads((ROOT/"RESULT_V2.json").read_text())
    expected={
        "paths_A_C":2,
        "cost_set_A_C":[[1,2],[2,1]],
        "pareto_A_C":[[1,2],[2,1]],
        "unreachable_pair":"C->A",
        "hostiles_caught":10,
    }
    for k,v in expected.items():
        need(res.get(k)==v,f"RESULT_DRIFT:{k}")

    print(json.dumps({
        "status":"GREEN",
        "cost_set_A_C":[list(x) for x in cs],
        "pareto_A_C":[list(x) for x in p],
        "unreachable_C_A":True,
        "distances":ds,
        "ball_r1":b1,
        "ball_r5":b5,
        "relabel_cost_set":[list(x) for x in rcs],
        "relabel_pareto":[list(x) for x in rp],
        "bad_relabel_cost_set":[list(x) for x in badcs],
        "bad_relabel_pareto":[list(x) for x in badp],
        "descending_prefix":len(descending),
        "hostiles_caught":10,
    },sort_keys=True))

if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print("R5_S1_RED:"+repr(exc),file=sys.stderr)
        sys.exit(1)
