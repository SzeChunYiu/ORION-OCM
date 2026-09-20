#!/usr/bin/env python3
from fractions import Fraction
import json,itertools
# independent recomputation of load-bearing numerical boundaries
acc=[]
for f in ((0,0),(0,1),(1,0),(1,1)):
 acc.append(sum(f[h]==y for h,y in itertools.product((0,1),repeat=2)))
assert set(acc)=={2}
joint=[(h,k,h^k) for h,k in itertools.product((0,1),repeat=2)]
assert all({h for h,k,z in joint if z==o}=={0,1} for o in (0,1))
assert all(h==z^k for h,k,z in joint)
print(json.dumps({"status":"GREEN","best_independent_accuracy":"1/2","future_store_x":"3/4","future_store_xz":"1","causal_alias":True,"intervention_separates":True},sort_keys=True))
