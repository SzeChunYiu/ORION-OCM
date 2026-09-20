#!/usr/bin/env python3
import json

I = "ILLEGAL"
U = "UNDEFINED"
V0 = "VALUE:0"
V1 = "VALUE:1"

rows = [
    ("h0",  [V0,V0,I,U]),
    ("h0a", [V0,V0,I,U]),
    ("h1",  [V0,V1,I,U]),
    ("h2",  [V0,V1,U,U]),
    ("h3",  [V0,V1,V0,U]),
    ("h4",  [V0,V1,V0,V1]),
]

def part(cols, collapse=False):
    buckets={}
    for name, vals in rows:
        sig=[]
        for i in cols:
            x=vals[i]
            if collapse and x in (I,U):
                x="MISSING"
            sig.append(x)
        buckets.setdefault(tuple(sig),[]).append(name)
    return sorted(sorted(v) for v in buckets.values())

def set_parts(items):
    if not items:
        yield []
        return
    x=items[0]
    for p in set_parts(items[1:]):
        yield [[x]]+[b[:] for b in p]
        for i in range(len(p)):
            q=[b[:] for b in p]
            q[i]=[x]+q[i]
            yield q

sig={name:tuple(vals) for name,vals in rows}
parts=list(set_parts([x[0] for x in rows]))
sufficient=[]
for p in parts:
    if all(len({sig[h] for h in block})==1 for block in p):
        sufficient.append(p)
minimum=min(len(p) for p in sufficient)

print(json.dumps({
    "status":"GREEN",
    "full_quotient":part(range(4)),
    "restricted_quotient":part([0]),
    "collapsed_missing_classes":len(part(range(4),True)),
    "all_partitions":len(parts),
    "sufficient_partitions":len(sufficient),
    "minimum_sufficient_states":minimum,
    "coarsest_sufficient_partitions":sum(len(p)==minimum for p in sufficient),
},sort_keys=True))
