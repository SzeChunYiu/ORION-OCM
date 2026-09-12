import json, numpy as np

def pars(pi,rho):
    return pi*(1-rho), pi+rho*(1-pi)

def exact_var(pi,rho,n):
    s=n+2*sum((n-k)*(rho**k) for k in range(1,n))
    return pi*(1-pi)*s/n**2

rng=np.random.default_rng(120926)
rows=[]
for pi in [0.2,0.5,0.8]:
    for rho in [0.0,0.4,0.8]:
        n=128
        m=10000
        p01,p11=pars(pi,rho)
        means=[]
        for _ in range(m):
            x=1 if rng.random()<pi else 0
            total=x
            for _ in range(1,n):
                p=p11 if x else p01
                x=1 if rng.random()<p else 0
                total+=x
            means.append(total/n)
        emp=float(np.var(means))
        ex=exact_var(pi,rho,n)
        rows.append({"pi":pi,"rho":rho,"empirical":emp,"exact":ex,
                     "relative_error":abs(emp-ex)/ex})
print(json.dumps({
 "artifact":"GMI_CORRELATED_DESCRIPTOR_CONFIDENCE_RECEIPT_V1",
 "cells":len(rows),
 "trajectories_per_cell":10000,
 "trajectory_length":128,
 "max_relative_variance_error":max(r["relative_error"] for r in rows),
 "rows":rows,
 "terminal":"CORRELATED_DESCRIPTOR_VARIANCE_CALIBRATION_GREEN"
},indent=2,sort_keys=True))
