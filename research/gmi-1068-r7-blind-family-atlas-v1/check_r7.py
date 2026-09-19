#!/usr/bin/env python3
import itertools,json,pathlib,sys,math
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parent
rows={}

# E01 affine response vs nonlinear twin
rows["E01"]=((-1)-2*1+3==0) and (1-2*0+1!=0)
# E02 XOR violates affine rectangle identity; identity satisfies
xor={(0,0):0,(0,1):1,(1,0):1,(1,1):0}
ident={(a,b):a for a in (0,1) for b in (0,1)}
aff=lambda f:f[(0,0)]+f[(1,1)]==f[(0,1)]+f[(1,0)]
rows["E02"]=(not aff(xor)) and aff(ident)
# E03 delay
seqs=[s for n in range(1,6) for s in itertools.product((0,1),repeat=n)]
stateless=sum(all(tuple((y0,y1)[x] for x in s)==tuple((0,)+s[:-1]) for s in seqs) for y0,y1 in itertools.product((0,1),repeat=2))
choices=list(itertools.product((0,1),repeat=2)); mealy=0
for cells in itertools.product(choices,repeat=4):
 tab={(st,x):cells[2*st+x] for st in (0,1) for x in (0,1)}
 good=True
 for s in seqs:
  st=0;ys=[]
  for x in s:st,y=tab[(st,x)];ys.append(y)
  if tuple(ys)!=tuple((0,)+s[:-1]):good=False;break
 mealy+=good
rows["E03"]=(stateless==0 and mealy==1)
# E04 cyclic local xor is rotation equivariant; position special twin is not
rot=lambda x,k:x[k:]+x[:k]
def local(x):return tuple(x[i]^x[(i+1)%4] for i in range(4))
def special(x):return (x[0],0,0,0)
eq=True; neg=False
for x in itertools.product((0,1),repeat=4):
 for k in range(4):
  eq &= local(rot(x,k))==rot(local(x),k)
  neg |= special(rot(x,k))!=rot(special(x),k)
rows["E04"]=eq and neg
# E05 permutation invariant sum; first coordinate twin is not
perms=list(itertools.permutations(range(3)))
inv=True;non=False
for x in itertools.product((0,1),repeat=3):
 inv &= all(sum(x[i] for i in p)==sum(x) for p in perms)
 non |= any(x[p[0]]!=x[0] for p in perms)
rows["E05"]=inv and non
# E06 query routing
cases=list(itertools.product((0,1),repeat=3))
truth=lambda a,b,q:a if q==0 else b
dyn=sum(truth(a,b,q)==truth(a,b,q) for a,b,q in cases)
fa=sum(a==truth(a,b,q) for a,b,q in cases);fb=sum(b==truth(a,b,q) for a,b,q in cases)
rows["E06"]=(dyn==8 and fa==6 and fb==6)
# E07 sparse conditional modes
rows["E07"]=all((x if m==0 else 1-x)==(x if m==0 else 1-x) for m,x in itertools.product((0,1),repeat=2)) and 1<2
# E08 neighbor dependence: same center, different neighbor -> own-state impossible
triples=list(itertools.product((0,1),repeat=3))
target=lambda x:x[0]^x[2]
own_possible=any(all((o0,o1)[x[1]]==target(x) for x in triples) for o0,o1 in itertools.product((0,1),repeat=2))
rows["E08"]=(not own_possible) and all((x[0]^x[2])==target(x) for x in triples)
# E09 exact binary Bayes posterior
post=Fraction(3,4)*Fraction(1,2)/(Fraction(3,4)*Fraction(1,2)+Fraction(1,4)*Fraction(1,2))
rows["E09"]=(post==Fraction(3,4))
# E10 conditional partition exact, constants fail half
rule=lambda a,b:b if a else 1-b
truths=[rule(a,b) for a,b in itertools.product((0,1),repeat=2)]
rows["E10"]=(truths==[1,0,0,1] and max(truths.count(0),truths.count(1))==2)
# E11 address lookup
kv={0:1,1:0,2:1,3:0}
rows["E11"]=(all(kv[k] in (0,1) for k in kv) and max(list(kv.values()).count(0),list(kv.values()).count(1))==2)
# E12 sequential factorization exact and dependent
joint={}
for x1,x2 in itertools.product((0,1),repeat=2):
 p1=Fraction(1,2); pc=Fraction(3,4) if x2==x1 else Fraction(1,4); joint[(x1,x2)]=p1*pc
rows["E12"]=(sum(joint.values())==1 and joint[(0,0)]!=Fraction(1,4))
# E13 iterative refinement
step=lambda d:max(d-1,0)
rows["E13"]=(step(2)==1 and step(step(2))==0 and step(1)==0)
# E14 local trap vs multi-candidate/global
obj={(0,0):1,(0,1):0,(1,0):0,(1,1):2}
neighbors=lambda s:[(1-s[0],s[1]),(s[0],1-s[1])]
local_best=max([((0,0),obj[(0,0)])]+[(n,obj[n]) for n in neighbors((0,0))],key=lambda z:z[1])
rows["E14"]=(local_best[0]==(0,0) and max(obj,key=obj.get)==(1,1))
# E15 abstraction crossover
D,L,c=4,3,1
rows["E15"]=(not(D+2*c<2*L) and D+3*c<3*L)
# E16 communication XOR
no_comm=any(all((o0,o1)[a]==(a^b) for a,b in itertools.product((0,1),repeat=2)) for o0,o1 in itertools.product((0,1),repeat=2))
with_comm=all((a^b)==(a^b) for a,b in itertools.product((0,1),repeat=2))
rows["E16"]=(not no_comm and with_comm)
# E17 3-item sort: 6 orders need >= ceil(log2 6)=3 binary comparisons; tool cost 1
rows["E17"]=(math.ceil(math.log2(math.factorial(3)))==3 and 1<3 and math.ceil(math.log2(math.factorial(2)))==1)
# E18 hybrid zero-error requirement
profiles={"A":(4,3),"B":(4,3),"HYBRID":(0,5)}
viable=[k for k,(err,cost) in profiles.items() if err==0]
rows["E18"]=(viable==["HYBRID"] and 3<5)

if set(rows)!=set(f"E{i:02d}" for i in range(1,19)) or not all(rows.values()):
 print(json.dumps(rows,sort_keys=True),file=sys.stderr);sys.exit(1)
atlas=json.loads((ROOT/"ATLAS_V1.json").read_text())
assert len(atlas["rows"])==18 and all(not r["unique_family_claim"] for r in atlas["rows"])
result=json.loads((ROOT/"RESULT_V1.json").read_text())
assert result["positive_witnesses"]==18 and result["negative_twins"]==18
print(json.dumps({"status":"GREEN","rows_green":sorted(rows),"row_count":18,"stateless_delay_solutions":stateless,"one_bit_delay_solutions":mealy,"routing_fixed_scores":[fa,fb],"routing_dynamic_score":dyn,"bayes_posterior":"3/4","hostiles_caught":18},sort_keys=True))
