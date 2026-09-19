#!/usr/bin/env python3
import json
rows=[("h0",[0,0,0]),("h1",[0,1,0]),("h2",[0,1,0])]
def partition(cols):
 buckets={}
 for n,v in rows:buckets.setdefault(tuple(v[i] for i in cols),[]).append(n)
 return sorted(sorted(x) for x in buckets.values())
print(json.dumps({"status":"GREEN","full_quotient":partition([0,1,2]),"restricted_quotient":partition([0])},sort_keys=True))
