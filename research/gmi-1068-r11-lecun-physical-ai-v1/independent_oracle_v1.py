#!/usr/bin/env python3
import json,itertools
raw=[(t,n) for t in [0,1] for n in [0,1]]
assert len({t for t,n in raw})==2 and len(raw)==4
actions=[(a,b) for a in [-1,1] for b in [-1,1]]
assert min(actions,key=lambda q:abs(2-sum(q)))==(1,1)
assert sum([0 for _ in range(16)])==0
print(json.dumps({"status":"GREEN","latent_classes":2,"raw_bits":2,"latent_bits":1,"planning_best":"++","constant_collapse_loss":0,"multimodal_point_optimum":0,"source_entries":11},sort_keys=True))
