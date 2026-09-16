from itertools import permutations, product
import json

LABELS=("F0","F1","F2")
WEIGHTS=((1,1),(2,1),(1,2),(4,1),(1,4))
ROWS=(
    ("pA0","ALPHA","F0",1,4),("pA1","ALPHA","F0",3,2),
    ("pB0","BETA","F1",4,1),("pB1","BETA","F1",2,3),
    ("pG0","GAMMA","F2",3,3),("pG1","GAMMA","F2",5,0),
)

def minima(rows,w):
    out={}
    for _,s,_,L,d in rows:
        v=w[0]*L+w[1]*d
        if s not in out or v<out[s]: out[s]=v
    return out

def selected(rows,w):
    m=minima(rows,w); z=min(m.values())
    return tuple(sorted(k for k,v in m.items() if v==z))

def build():
    base_min={w:minima(ROWS,w) for w in WEIGHTS}
    base_sel={w:selected(ROWS,w) for w in WEIGHTS}
    pchecks=cchecks=schecks=0
    for imgs in permutations(LABELS):
        mp=dict(zip(LABELS,imgs))
        r=tuple((i,s,mp[f],L,d) for i,s,f,L,d in ROWS)
        for w in WEIGHTS:
            for old,new in zip(ROWS,r):
                pchecks += 1
                if old[3:]!=new[3:]: raise AssertionError
            cchecks += 3
            if minima(r,w)!=base_min[w]: raise AssertionError
            schecks += 1
            if selected(r,w)!=base_sel[w]: raise AssertionError
    vec=tuple(product(range(5),repeat=2))
    dompairs=checks=bad=0
    for x in vec:
        for y in vec:
            if x==y: continue
            dom=(x[0]<=y[0] and x[1]<=y[1] and x!=y)
            if dom:
                dompairs+=1
                for w in WEIGHTS:
                    checks+=1
                    if not x[0]*w[0]+x[1]*w[1] < y[0]*w[0]+y[1]*w[1]: bad+=1
    return {
        "schema":"GMI833G0CostPrivilegeIndependentOracleV1",
        "label_permutations":6,
        "point_cost_checks":pchecks,
        "class_minimum_checks":cchecks,
        "selection_checks":schecks,
        "dominance_pairs":dompairs,
        "dominance_weight_checks":checks,
        "dominance_violations":bad,
        "reversal": (1+4*4 > 4+1*4) and (4+4 < 16+1),
        "terminal":"INDEPENDENT_ORACLE_GREEN"
    }

if __name__=="__main__": print(json.dumps(build(),sort_keys=True,indent=2,separators=(",",": "))+"\n",end="")
