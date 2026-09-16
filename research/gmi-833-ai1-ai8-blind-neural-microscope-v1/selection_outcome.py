from __future__ import annotations
import json
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load_protocol(): return json.loads((HERE/'BLIND_PROTOCOL_V1.json').read_text())
def frac(x): return Fraction(x) if not isinstance(x,str) else Fraction(x)
def resources():
    p=load_protocol(); return {k:tuple(frac(v) for v in vals) for k,vals in p['raw_resources'].items()}
def pareto_front(rs):
    names=list(rs); out=[]
    for a in names:
        va=rs[a]
        dominated=False
        for b in names:
            if a==b: continue
            vb=rs[b]
            if all(x<=y for x,y in zip(vb,va)) and any(x<y for x,y in zip(vb,va)):
                dominated=True;break
        if not dominated: out.append(a)
    return tuple(sorted(out))
def scalar_cost(name,H,rs=None):
    rs=rs or resources(); build,use,_=rs[name]; return build+Fraction(H)*use
def winners(H,rs=None):
    rs=rs or resources(); costs={n:scalar_cost(n,H,rs) for n in rs}; m=min(costs.values())
    return tuple(sorted(n for n,c in costs.items() if c==m)),costs
def switched_winner(previous,H,k=Fraction(4)):
    rs=resources(); candidates=('RULE','COMPOSITION')
    costs={n:scalar_cost(n,H,rs)+(Fraction(0) if n==previous else k) for n in candidates}; m=min(costs.values())
    return tuple(sorted(n for n,c in costs.items() if c==m)),costs
def certificate():
    p=load_protocol(); rs=resources(); assert pareto_front(rs)==('COMPOSITION','RULE','TABLE')
    held=[]
    for H,pred in zip(p['heldout_horizons'],p['predicted_winners']):
        got,c=winners(H,rs); assert got==tuple(sorted(pred)); held.append({'H':H,'winners':list(got),'costs':{k:str(v) for k,v in c.items()}})
    # Full exact scalar regime through 200.
    full={H:winners(H,rs)[0] for H in range(0,201)}
    assert all(full[H]==('RULE',) for H in range(0,9)); assert full[9]==('COMPOSITION','RULE')
    assert all(full[H]==('COMPOSITION',) for H in range(10,160)); assert full[160]==('COMPOSITION','TABLE')
    assert all(full[H]==('TABLE',) for H in range(161,201))
    hist={}
    for prev in ('RULE','COMPOSITION'):
        hist[prev]={H:switched_winner(prev,H)[0] for H in range(0,20)}
    assert all(hist['RULE'][H]==('RULE',) for H in range(0,11)); assert hist['RULE'][11]==('COMPOSITION','RULE'); assert hist['RULE'][12]==('COMPOSITION',)
    assert all(hist['COMPOSITION'][H]==('RULE',) for H in range(0,7)); assert hist['COMPOSITION'][7]==('COMPOSITION','RULE')
    assert all('COMPOSITION' in hist['COMPOSITION'][H] for H in range(7,20))
    # Matched scalar-price hostile: changing registered build cost can remove the composition region; raw Pareto remains primary.
    hostile=dict(rs); hostile['COMPOSITION']=(Fraction(200),Fraction(1),Fraction(4))
    hostile_comp_wins=[H for H in range(0,201) if 'COMPOSITION' in winners(H,hostile)[0]]
    assert not hostile_comp_wins
    return {'pareto_front':list(pareto_front(rs)),'heldout':held,'full_regime_counts':{str(k):sum(1 for v in full.values() if v==k) for k in set(full.values())},'history_switching_rule_at_11':list(hist['RULE'][11]),'history_switching_rule_at_12':list(hist['RULE'][12]),'history_switching_composition_at_7':list(hist['COMPOSITION'][7]),'price_hostile_composition_wins':0,'raw_vectors_primary':True}
