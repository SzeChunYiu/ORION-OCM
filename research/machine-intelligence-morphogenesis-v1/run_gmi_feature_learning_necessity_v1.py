import itertools, json
import numpy as np

vals=(-1,0,1)
total=reachable=irreducible=violations=0
max_residual=0.0

for entries in itertools.product(vals, repeat=6):
    Phi=np.array(entries,dtype=float).reshape(3,2)
    P=Phi @ np.linalg.pinv(Phi)
    for yv in itertools.product(vals, repeat=3):
        y=np.array(yv,dtype=float)
        a=np.linalg.pinv(Phi) @ y
        direct=float(np.sum((y-Phi@a)**2))
        projected=float(np.sum(((np.eye(3)-P)@y)**2))
        total += 1
        if abs(direct-projected)>1e-9:
            violations += 1
        if projected < 1e-10:
            reachable += 1
        else:
            irreducible += 1
        max_residual=max(max_residual,projected)

receipt={
 "artifact":"GMI_FEATURE_LEARNING_NECESSITY_RECEIPT_V1",
 "cells":total,
 "fixed_feature_exact_reachable":reachable,
 "tangent_orthogonal_positive":irreducible,
 "projection_identity_violations":violations,
 "max_squared_residual":max_residual,
 "terminal":"FEATURE_LEARNING_NECESSITY_EXACT_MICROSCOPE_GREEN" if violations==0 else "RED"
}
print(json.dumps(receipt,indent=2,sort_keys=True))
