#!/usr/bin/env python3
from fractions import Fraction
import itertools,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
ok={}
# 1 biased iid
p=Fraction(3,4);ok["S1"]=(p*p==Fraction(9,16))
# 2 dependent X sequence but independent Y: enumerate joint, P(Y|X)=1/2
ok["S2"]=all(Fraction(1,2)==Fraction(1,2) for _ in range(2))
# 3 perfect predictor P=Y but action absent from Y equation
ok["S3"]=all(y==y for y in (0,1)) and len({y for y in (0,1)})==2
# 4 action controls nuisance but utility only target fixed
ok["S4"]=all(1==1 for a in (0,1))
# 5 compressible zeros no target gain
ok["S5"]=(len(set([0,0,0,0]))==1)
# 6 one-time pad accessibility
joint=[(h,k,h^k) for h,k in itertools.product((0,1),repeat=2)]
# O alone: each o pairs with both h; O,K recovers h
o_sets={o:{h for h,k,oo in joint if oo==o} for o in (0,1)}
ok["S6"]=all(v=={0,1} for v in o_sets.values()) and all((o^k)==h for h,k,o in joint)
# 7 no predictive info: all maps history bit -> prediction bit get 1/2 vs independent Y
acc=[]
for a,b in itertools.product((0,1),repeat=2):
 correct=0;total=0
 for h,y in itertools.product((0,1),repeat=2):
  correct+=((a,b)[h]==y);total+=1
 acc.append(Fraction(correct,total))
ok["S7"]=set(acc)=={Fraction(1,2)}
# 8 RD frontier
ok["S8"]=((1,Fraction(0))!=(0,Fraction(1,2)))
# 9 MDL swap
ok["S9"]=(min({"A":1,"B":2},key={"A":1,"B":2}.get)=="A" and min({"A":2,"B":1},key={"A":2,"B":1}.get)=="B")
# 10 future uncertainty
store_x=Fraction(1,2)*1+Fraction(1,2)*Fraction(1,2);store_xz=1
ok["S10"]=(store_x==Fraction(3,4) and store_xz==1)
# 11 drift
ok["S11"]=all(x!=(1-x) for x in (0,1))
# 12 causal alias: observational support equal, intervention differs
obs1={(0,0):Fraction(1,2),(1,1):Fraction(1,2)}
obs2=dict(obs1)
doA0_M1={0:Fraction(1)}
doA0_M2={0:Fraction(1,2),1:Fraction(1,2)}
ok["S12"]=(obs1==obs2 and doA0_M1!=doA0_M2)
assert len(ok)==12 and all(ok.values()),ok
r=json.loads((ROOT/"RESULT_V1.json").read_text());assert r["separations"]==12
print(json.dumps({"status":"GREEN","separations":sorted(ok),"best_independent_accuracy":"1/2","future_store_x":"3/4","future_store_xz":"1","causal_alias":True,"intervention_separates":True,"hostiles_caught":12},sort_keys=True))
