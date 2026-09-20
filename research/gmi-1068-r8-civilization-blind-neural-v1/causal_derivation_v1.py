#!/usr/bin/env python3
# Causal lane: generic arithmetic/order/process only. No family taxonomy.
from fractions import Fraction

XS=tuple(range(-32,33))
SLOPES=(-2,-1,0,1,2)
BASE=(-1,0,1)
H=16

def world_value(s0,s1,s2,b,x):
    if x < -8:
        return b - 8*s1 + s0*(x+8)
    if x <= 8:
        return b + s1*x
    return b + 8*s1 + s2*(x-8)

def pos_abs(z):
    return (z + abs(z))//2

def pos_select(z):
    return z if z>0 else 0

def slope_jump_value(s0,s1,s2,b,x,use_abs=True):
    d1=s1-s0; d2=s2-s1
    a=b-8*d1
    pos=pos_abs if use_abs else pos_select
    return a+s0*x+d1*pos(x+8)+d2*pos(x-8)

def branch_value(s0,s1,s2,b,x):
    return world_value(s0,s1,s2,b,x)

def jumps(s0,s1,s2):
    return int(s1!=s0)+int(s2!=s1)

def candidates(k,substrate):
    out=[]
    out.append(("TABLE",65,H*(15 if substrate=="S_ARITH" else 4)+65))
    out.append(("BRANCH",8,H*(18 if substrate=="S_ARITH" else 6)+8))
    if k==0:
        out.append(("AFFINE",3,H*(2 if substrate=="S_ARITH" else 4)+3))
    else:
        per=(2+7*k) if substrate=="S_ARITH" else (4+15*k)
        out.append(("HINGE",2+2*k,H*per+2+2*k))
    return out

def select(k,substrate):
    cs=candidates(k,substrate)
    m=min(c[2] for c in cs)
    return tuple(sorted(c[0] for c in cs if c[2]==m))

def all_worlds():
    for s0 in SLOPES:
      for s1 in SLOPES:
       for s2 in SLOPES:
        for b in BASE:
         yield s0,s1,s2,b

def run():
    counts={"worlds":0,"k0":0,"k1":0,"k2":0,"routeA_checks":0,"routeB_checks":0,"remint_checks":0}
    winners={"S_ARITH":{},"S_BRANCH":{}}
    for s0,s1,s2,b in all_worlds():
        counts["worlds"]+=1;k=jumps(s0,s1,s2);counts[f"k{k}"]+=1
        for x in XS:
            y=world_value(s0,s1,s2,b,x)
            if slope_jump_value(s0,s1,s2,b,x,True)!=y: raise RuntimeError("routeA")
            if branch_value(s0,s1,s2,b,x)!=y: raise RuntimeError("routeB")
            if slope_jump_value(s0,s1,s2,b,x,False)!=slope_jump_value(s0,s1,s2,b,x,True): raise RuntimeError("remint")
            counts["routeA_checks"]+=1;counts["routeB_checks"]+=1;counts["remint_checks"]+=1
        for sub in winners:
            w=select(k,sub)
            winners[sub][w]=winners[sub].get(w,0)+1
    return counts,winners

if __name__=="__main__":
 import json
 c,w=run();print(json.dumps({"counts":c,"winners":{s:{"|".join(k):v for k,v in d.items()} for s,d in w.items()}},sort_keys=True))
