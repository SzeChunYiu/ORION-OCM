from __future__ import annotations
from itertools import permutations, product
import json

V=(0,1,2); Z3=(0,1,2); EDGES=((0,1),(0,2),(1,2))

def canon_graph(bits): return tuple(e for e,b in zip(EDGES,bits) if b)
def degs(g): return tuple(sum(v in e for e in g) for v in V)
def neighbors(g,v):
    out=[]
    for a,b in g:
        if a==v: out.append(b)
        elif b==v: out.append(a)
    return tuple(sorted(out))
def pwise(s): return tuple((x+1)%3 for x in s)
def glob(s):
    a=sum(s)%3
    return tuple((x+a)%3 for x in s)
def neigh(s,g): return tuple((s[v]+sum(s[u] for u in neighbors(g,v)))%3 for v in V)
def tstate(s,p):
    out=[0,0,0]
    for old,new in enumerate(p): out[new]=s[old]
    return tuple(out)
def tgraph(g,p): return tuple(sorted((min(p[a],p[b]),max(p[a],p[b])) for a,b in g))
def rsrc(name,g):
    if name=='POINTWISE': return (3,3,0,0)
    if name=='GLOBAL_BROADCAST': return (6,3,0,2)
    d=degs(g); e2=sum(d)
    return (3+e2,3,e2,sum(max(x-1,0) for x in d))
def main():
    funcs={'POINTWISE':lambda s,g:pwise(s),'GLOBAL_BROADCAST':lambda s,g:glob(s),'NEIGHBOR_UPDATE':neigh}
    comp={k:0 for k in funcs}; mism={k:0 for k in funcs}; rm={k:0 for k in funcs}; hist={}
    for bits in product((0,1),repeat=3):
        g=canon_graph(bits); hist.setdefault(str(len(g)),set()).add(rsrc('NEIGHBOR_UPDATE',g))
        for s in product(Z3,repeat=3):
            for p in permutations(V):
                ts=tstate(s,p); tg=tgraph(g,p)
                for name,fn in funcs.items():
                    a=fn(s,g); b=fn(ts,tg); comp[name]+=1
                    if tstate(a,p)!=b: mism[name]+=1
                    if rsrc(name,g)!=rsrc(name,tg): rm[name]+=1
    out={'schema':'GMI833LocalGlobalGraphOpsIndependentOracleV1','comparisons':comp,'equivariance_mismatches':mism,'resource_mismatches':rm,'neighbor_resource_histogram':{k:[list(x) for x in sorted(v)] for k,v in sorted(hist.items())},'terminal':'GREEN' if all(x==1296 for x in comp.values()) and not any(mism.values()) and not any(rm.values()) else 'RED'}
    print(json.dumps(out,indent=2,sort_keys=True,separators=(',', ': ')))
if __name__=='__main__': main()
