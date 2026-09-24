#!/usr/bin/env python3
import json
from itertools import product

edges={
    "A":[("B",(1,0)),("C",(2,1))],
    "B":[("C",(0,2))],
    "C":[],
}
def add(x,y): return (x[0]+y[0],x[1]+y[1])
def costs(a,b):
    out={(0,0)} if a==b else set()
    frontier=[(a,{a},(0,0))]
    while frontier:
        n,seen,c=frontier.pop()
        for m,ec in edges[n]:
            if m in seen: continue
            nc=add(c,ec)
            if m==b: out.add(nc)
            frontier.append((m,seen|{m},nc))
    return sorted(out)
def pareto(vs):
    return sorted(v for v in vs if not any(u!=v and u[0]<=v[0] and u[1]<=v[1] for u in vs))
def d(a,b,w):
    cs=costs(a,b)
    return None if not cs else min(w[0]*x+w[1]*y for x,y in cs)
cs=costs("A","C")
print(json.dumps({
  "status":"GREEN",
  "cost_set_A_C":[list(x) for x in cs],
  "pareto_A_C":[list(x) for x in pareto(cs)],
  "unreachable_C_A":costs("C","A")==[],
  "distances":{
    str((1,3)):{"AA":d("A","A",(1,3)),"AB":d("A","B",(1,3)),"BC":d("B","C",(1,3)),"AC":d("A","C",(1,3))},
    str((3,1)):{"AA":d("A","A",(3,1)),"AB":d("A","B",(3,1)),"BC":d("B","C",(3,1)),"AC":d("A","C",(3,1))}
  }
},sort_keys=True))
