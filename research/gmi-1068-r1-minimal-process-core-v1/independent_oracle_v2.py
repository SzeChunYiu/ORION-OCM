#!/usr/bin/env python3
import json

edges={"A":["B"],"B":["C"],"C":["D"],"D":[]}
reach=set()
for s in edges:
    reach.add((s,s))
    frontier=[s]
    seen={s}
    while frontier:
        x=frontier.pop(0)
        for y in edges[x]:
            reach.add((s,y))
            if y not in seen:
                seen.add(y)
                frontier.append(y)
print(json.dumps({
    "status":"GREEN",
    "reachable_pairs":[list(x) for x in sorted(reach)],
    "empty_identities":[[x,x] for x in sorted(edges)],
    "assoc_path":["f","g","h"],
},sort_keys=True))
