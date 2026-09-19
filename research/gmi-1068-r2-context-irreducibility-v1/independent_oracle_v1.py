#!/usr/bin/env python3
import json
pairs=[(x,y) for x in (0,1,2) for y in (0,1,2)]
sets=[("a0" if x>y else "a1" if y>x else "tie") for x,y in pairs]
out={k:sets.count(k) for k in ("a0","a1","tie")}
p=(1,0); q=(0,1)
seps=[2*p[0]+p[1] > 2*q[0]+q[1], q[0]+2*q[1] > p[0]+2*p[1]]
print(json.dumps({"status":"GREEN","reward_worlds":len(pairs),"optimal_sets":out,"scalarization_separators":sum(seps)},sort_keys=True))
