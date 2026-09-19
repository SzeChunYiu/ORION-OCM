#!/usr/bin/env python3
import json
# Source-separated finite oracle: enumerate composition tables directly.

def preorder():
  arr=[(a,b) for a in range(3) for b in range(3) if a<=b]
  triples=[]
  for f in arr:
    for g in arr:
      if f[1]!=g[0]: continue
      fg=(f[0],g[1])
      for h in arr:
        if g[1]!=h[0]: continue
        gh=(g[0],h[1])
        if (fg[0],h[1]) != (f[0],gh[1]): raise SystemExit(1)
        triples.append((f,g,h))
  return len(arr),len(triples)

def c2():
  table={(0,0):0,(0,1):1,(1,0):1,(1,1):0}
  n=0
  for a in (0,1):
   for b in (0,1):
    for c in (0,1):
     if table[(table[(a,b)],c)] != table[(a,table[(b,c)])]: raise SystemExit(1)
     n+=1
  if any(table[(0,a)]!=a or table[(a,0)]!=a for a in (0,1)): raise SystemExit(1)
  return n

pa,pt=preorder()
print(json.dumps({"status":"GREEN","preorder_arrows":pa,"preorder_assoc_triples":pt,"c2_assoc_triples":c2()},sort_keys=True))
