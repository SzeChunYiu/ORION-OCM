import itertools, json, random, numpy as np

A=[a for a in itertools.product(range(2), repeat=4)
   if all(a.count(k)<=2 for k in range(2))]
rng=random.Random(240912)
viol=max_regret=0
cases=50000

for _ in range(cases):
    c=np.array([rng.randint(0,5) for _ in range(8)],dtype=float).reshape(4,2)
    d=np.array([rng.choice([-1,0,1]) for _ in range(8)],dtype=float).reshape(4,2)
    chat=c+d
    def cost(M,a): return sum(M[i,a[i]] for i in range(4))
    a0=min(A,key=lambda a:cost(c,a))
    a1=min(A,key=lambda a:cost(chat,a))
    regret=cost(c,a1)-cost(c,a0)
    max_regret=max(max_regret,regret)
    if regret>8+1e-9: violations+=1

print(json.dumps({
 "artifact":"GMI_ROUTER_ESTIMATION_REGRET_RECEIPT_V2",
 "cases":cases,
 "bound":8,
 "max_observed_regret":max_regret,
 "violations":viol,
 "terminal":"ROUTER_ESTIMATION_REGRET_BOUND_GREEN" if viol==0 else "RED"
},indent=2,sort_keys=True))
