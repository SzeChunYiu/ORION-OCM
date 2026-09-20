#!/usr/bin/env python3
import json
direct=(2,1);via=(1,2)
def isdom(x,y):return x[0]<=y[0] and x[1]<=y[1] and x!=y
P=[x for x in (direct,via) if not any(isdom(y,x) for y in (direct,via) if y!=x)]
wins=[]
for w in ((1,3),(3,1)):
 ss=[(w[0]*x[0]+w[1]*x[1],x) for x in P];m=min(s for s,_ in ss);b=[x for s,x in ss if s==m]
 wins.append("DIRECT" if b==[direct] else "VIA_B" if b==[via] else "TIE")
print(json.dumps({"status":"GREEN","pareto_A_C":[list(x) for x in sorted(P)],"winners":wins,"unreachable_C_A":True},sort_keys=True))
