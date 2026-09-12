import json, math
import numpy as np

rows=violations=better=0
max_abs_error=0.0
for mu in range(1,9):
    for L in range(mu,17):
        sm,sL=math.sqrt(mu),math.sqrt(L)
        eta=4/(sL+sm)**2
        beta=((sL-sm)/(sL+sm))**2
        q=(sL-sm)/(sL+sm) if L>mu else 0.0
        worst=0.0
        for lam in np.linspace(mu,L,101):
            a=1+beta-eta*lam
            roots=np.roots([1,-a,beta])
            worst=max(worst,max(abs(r) for r in roots))
        gd=(L-mu)/(L+mu) if L>mu else 0.0
        rows+=1
        max_abs_error=max(max_abs_error,abs(worst-q))
        if worst>q+5e-8:
            violations+=1
        if L>mu and q<gd:
            better+=1

print(json.dumps({
 "artifact":"GMI_OPTIMIZER_STATE_QUADRATIC_RECEIPT_V1",
 "spectral_intervals":rows,
 "root_radius_violations":violations,
 "nontrivial_intervals_hb_faster_than_gd":better,
 "max_root_radius_abs_error":max_abs_error,
 "terminal":"OPTIMIZER_STATE_QUADRATIC_EXACT_LAYER_GREEN" if violations==0 else "RED"
},indent=2,sort_keys=True))
