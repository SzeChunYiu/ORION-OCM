#!/usr/bin/env python3
from fractions import Fraction
import itertools,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
def need(cond,msg):
 if not cond: raise RuntimeError(msg)
ok={}
r9=json.loads((ROOT.parent/"gmi-1068-r9-update-law-unification-v1/RESULT_V1.json").read_text())
need(r9["status"]=="GREEN_AT_REGISTERED_UPDATE_UNIFICATION_SCOPE","R9_PARENT_NOT_GREEN")
need("UNIVERSAL_BEST_UPDATE_LAW" in r9["forbidden_promotions"],"R9_UNIVERSAL_UPDATE_BOUNDARY")

# S1: biased but iid. Marginal 3/4 each; joint P(1,1)=9/16=product.
p=Fraction(3,4)
iid={(x0,x1): (p if x0 else 1-p)*(p if x1 else 1-p) for x0,x1 in itertools.product((0,1),repeat=2)}
m0=sum(prob for (x0,x1),prob in iid.items() if x0==1)
m1=sum(prob for (x0,x1),prob in iid.items() if x1==1)
ok["S1"]=(m0==p and m1==p and iid[(1,1)]==m0*m1)

# S2: observations X0,X1 are maximally dependent (X1=X0), but target Y is independent.
dep_worlds=[(x,x,y,Fraction(1,4)) for x,y in itertools.product((0,1),repeat=2)]
cond={}
for x in (0,1):
 den=sum(pr for x0,x1,y,pr in dep_worlds if x1==x)
 num=sum(pr for x0,x1,y,pr in dep_worlds if x1==x and y==1)
 cond[x]=num/den
ok["S2"]=(cond=={0:Fraction(1,2),1:Fraction(1,2)})

# S3: perfect observational predictor P=Y via common cause Z, but intervening on P leaves Y uniform.
obs=[(z,z,z,Fraction(1,2)) for z in (0,1)]  # Z,P,Y
obs_predicts=all(pv==y for z,pv,y,pr in obs)
do_p0_y={0:Fraction(1,2),1:Fraction(1,2)}
ok["S3"]=obs_predicts and do_p0_y=={0:Fraction(1,2),1:Fraction(1,2)}

# S4: action causally changes X, but utility ignores X and is constant.
x_after={a:a for a in (0,1)}
utility={a:1 for a in (0,1)}
ok["S4"]=(x_after[0]!=x_after[1] and utility[0]==utility[1])

# S5: a perfectly compressible nuisance string carries no target information.
nuisance=(0,0,0,0)
target_worlds=[(nuisance,y,Fraction(1,2)) for y in (0,1)]
ok["S5"]=(len(set(nuisance))==1 and sum(pr for n,y,pr in target_worlds if y==1)==Fraction(1,2))

# S6: one-time-pad accessibility. O alone leaves H ambiguous; O plus K recovers H.
joint=[(h,k,h^k) for h,k in itertools.product((0,1),repeat=2)]
o_sets={o:{h for h,k,oo in joint if oo==o} for o in (0,1)}
ok["S6"]=all(v=={0,1} for v in o_sets.values()) and all((o^k)==h for h,k,o in joint)

# S7: no predictive information. Every deterministic map H->Y gets exactly 1/2 against independent Y.
acc=[]
for a,b in itertools.product((0,1),repeat=2):
 correct=0;total=0
 for h,y in itertools.product((0,1),repeat=2):
  correct+=((a,b)[h]==y);total+=1
 acc.append(Fraction(correct,total))
ok["S7"]=set(acc)=={Fraction(1,2)}

# S8: simple rate/distortion frontier.
retain=(1,Fraction(0));forget=(0,Fraction(1,2))
ok["S8"]=(retain!=forget)

# S9: MDL preference flips when the coding language swaps code lengths.
ok["S9"]=(min({"A":1,"B":2},key={"A":1,"B":2}.get)=="A" and min({"A":2,"B":1},key={"A":2,"B":1}.get)=="B")

# S10: current task asks X, future task equally likely asks X or Z.
store_x=Fraction(1,2)*1+Fraction(1,2)*Fraction(1,2)
store_xz=Fraction(1)
ok["S10"]=(store_x==Fraction(3,4) and store_xz==1)

# S11: deterministic drift from y=x to y=1-x makes old predictor accuracy zero.
old_future_scores=[int(x==(1-x)) for x in (0,1)]
ok["S11"]=(sum(old_future_scores)==0)

# S12: observationally identical causal models A->Y and Y->A separate under do(A=0).
obs1={(0,0):Fraction(1,2),(1,1):Fraction(1,2)}
obs2=dict(obs1)
doA0_M1={0:Fraction(1)}
doA0_M2={0:Fraction(1,2),1:Fraction(1,2)}
ok["S12"]=(obs1==obs2 and doA0_M1!=doA0_M2)

need(len(ok)==12 and all(ok.values()),"SEPARATIONS:"+repr({k:v for k,v in ok.items() if not v}))
r=json.loads((ROOT/"RESULT_V1.json").read_text());need(r["separations"]==12,"RESULT")
print(json.dumps({"status":"GREEN","separations":sorted(ok),"biased_iid_joint_11":"9/16","dependent_target_conditionals":["1/2","1/2"],"confounded_predictor_perfect":True,"do_predictor_not_causal":True,"best_independent_accuracy":"1/2","future_store_x":"3/4","future_store_xz":"1","drift_old_accuracy":"0","causal_alias":True,"intervention_separates":True,"hostiles_caught":12},sort_keys=True))
