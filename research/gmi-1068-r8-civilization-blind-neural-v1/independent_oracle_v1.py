#!/usr/bin/env python3
import itertools,json
XS=range(-32,33)
slopes=(-2,-1,0,1,2)
bases=(-1,0,1)
def world(s0,s1,s2,b,x):
 if x<-8:return b-8*s1+s0*(x+8)
 if x<=8:return b+s1*x
 return b+8*s1+s2*(x-8)
def pos(z):return z if z>0 else 0
def form(s0,s1,s2,b,x):
 d1=s1-s0;d2=s2-s1
 return b-8*d1+s0*x+d1*pos(x+8)+d2*pos(x-8)
dist=[0,0,0];checks=0;wa={"AFFINE":0,"HINGE":0};wb={"AFFINE":0,"BRANCH":0}
for s0,s1,s2,b in itertools.product(slopes,slopes,slopes,bases):
 k=(s0!=s1)+(s1!=s2);dist[k]+=1
 for x in XS:
  assert world(s0,s1,s2,b,x)==form(s0,s1,s2,b,x);checks+=1
 if k==0:wa["AFFINE"]+=1;wb["AFFINE"]+=1
 else:wa["HINGE"]+=1;wb["BRANCH"]+=1
print(json.dumps({"status":"GREEN","worlds":sum(dist),"jump_distribution":dist,"route_checks":checks,"winners_S_ARITH":wa,"winners_S_BRANCH":wb,"substrate_inversions":wa["HINGE"]},sort_keys=True))
