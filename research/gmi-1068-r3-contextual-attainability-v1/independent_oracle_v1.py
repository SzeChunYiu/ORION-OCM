#!/usr/bin/env python3
import json,itertools
V=[("h0",0,0),("h1",1,2),("h2",2,5),("h3",2,3)]
def f(rows):
 out=[]
 for name,p,c in rows:
  dominated=False
  for n2,p2,c2 in rows:
   if n2==name: continue
   if p2>=p and c2<=c and (p2>p or c2<c): dominated=True
  if not dominated: out.append(name)
 return sorted(out)
full=V
budget=[r for r in V if r[0] in {"h0","h1"}]
def win(l):
 ss=[(l*p-c,n) for n,p,c in full]; m=max(x[0] for x in ss); return sorted(n for s,n in ss if s==m)
print(json.dumps({"status":"GREEN","full_frontier":f(full),"budget_frontier":f(budget),"phase_low":win(1),"phase_high":win(3)},sort_keys=True))
