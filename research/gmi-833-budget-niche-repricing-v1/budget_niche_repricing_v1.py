from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations, product, combinations
import json
from typing import Mapping, Sequence

CLAIM_CEILING='GMI_FINITE_BUDGET_NICHE_AND_REPRICING_SELECTION_LAWS_AT_REGISTERED_SCOPE'
class LawError(ValueError): pass
def F(x): return x if isinstance(x,Fraction) else Fraction(x)

@dataclass(frozen=True)
class SearchCandidate:
    cid:str
    objective:Fraction
    discovery:int

def make_search(cid,obj,discovery):
    o=F(obj)
    if not cid or o<0 or int(discovery)!=discovery or discovery<0: raise LawError('MALFORMED_SEARCH_CANDIDATE')
    return SearchCandidate(cid,o,int(discovery))

def budget_winners(cands:Sequence[SearchCandidate], budget:int):
    if len({c.cid for c in cands})!=len(cands): raise LawError('DUPLICATE_CANDIDATE_ID')
    if budget<0: raise LawError('NEGATIVE_BUDGET')
    avail=[c for c in cands if c.discovery<=budget]
    if not avail: return ()
    best=min(c.objective for c in avail)
    return tuple(sorted(c.cid for c in avail if c.objective==best))

def budget_best_value(cands,budget):
    w=budget_winners(cands,budget)
    if not w: return None
    by={c.cid:c for c in cands}
    return by[w[0]].objective

def stabilization_budget(cands):
    if not cands: raise LawError('EMPTY_CANDIDATES')
    best=min(c.objective for c in cands)
    winners=[c for c in cands if c.objective==best]
    if len(winners)!=1: return None
    return winners[0].discovery

@dataclass(frozen=True)
class Regime:
    rid:str
    weight:Fraction

def niche_summary(candidates:Sequence[str], regimes:Sequence[Regime], costs:Mapping[tuple[str,str],object]):
    if not candidates or len(set(candidates))!=len(candidates): raise LawError('MALFORMED_CANDIDATES')
    if not regimes or len({r.rid for r in regimes})!=len(regimes): raise LawError('MALFORMED_REGIMES')
    if any(r.weight<0 for r in regimes) or sum((r.weight for r in regimes),F(0))!=1: raise LawError('REGIME_WEIGHTS_NOT_PROBABILITY')
    req={(r.rid,c) for r in regimes for c in candidates}
    if set(costs)!=req: raise LawError('COST_DOMAIN_MISMATCH')
    vals={k:F(v) for k,v in costs.items()}
    if any(v<0 for v in vals.values()): raise LawError('NEGATIVE_COST')
    winners={}
    lower={c:F(0) for c in candidates}; upper={c:F(0) for c in candidates}
    for r in regimes:
        best=min(vals[(r.rid,c)] for c in candidates)
        ws=tuple(sorted(c for c in candidates if vals[(r.rid,c)]==best))
        winners[r.rid]=ws
        for c in ws: upper[c]+=r.weight
        if len(ws)==1: lower[ws[0]]+=r.weight
    robust=tuple(sorted(c for c in candidates if lower[c]>0))
    possible=tuple(sorted(c for c in candidates if upper[c]>0))
    return {'winners':winners,'lower':lower,'upper':upper,
            'robust_coexistence':len(robust)>=2,'possible_coexistence':len(possible)>=2,
            'robust_forms':robust,'possible_forms':possible}

@dataclass(frozen=True)
class ResourceCandidate:
    cid:str
    resources:tuple[Fraction,...]

def make_resource(cid,resources):
    rr=tuple(F(x) for x in resources)
    if not cid or not rr or any(x<0 for x in rr): raise LawError('MALFORMED_RESOURCE_CANDIDATE')
    return ResourceCandidate(cid,rr)

def price_vector(w0,v,theta):
    w=tuple(F(a)+F(theta)*F(b) for a,b in zip(w0,v,strict=True))
    if any(x<=0 for x in w): raise LawError('NONPOSITIVE_PRICE')
    return w

def price_winners(cands,w0,v,theta):
    if not cands or len({c.cid for c in cands})!=len(cands): raise LawError('MALFORMED_RESOURCE_CANDIDATES')
    d=len(cands[0].resources)
    if any(len(c.resources)!=d for c in cands) or len(w0)!=d or len(v)!=d: raise LawError('DIMENSION_MISMATCH')
    w=price_vector(w0,v,theta)
    scores={c.cid:sum((wi*ri for wi,ri in zip(w,c.resources,strict=True)),F(0)) for c in cands}
    best=min(scores.values())
    return tuple(sorted(k for k,z in scores.items() if z==best))

def repricing_boundaries(cands,w0,v,lo,hi):
    L,U=F(lo),F(hi)
    if L>U: raise LawError('INVALID_INTERVAL')
    price_vector(w0,v,L); price_vector(w0,v,U)
    out=set()
    for a,b in combinations(cands,2):
        da=sum((F(w0[i])*(a.resources[i]-b.resources[i]) for i in range(len(w0))),F(0))
        db=sum((F(v[i])*(a.resources[i]-b.resources[i]) for i in range(len(v))),F(0))
        if db==0: continue
        t=-da/db
        if L<=t<=U: out.add(t)
    return tuple(sorted(out))

def repricing_cells(cands,w0,v,lo,hi):
    L,U=F(lo),F(hi)
    pts=[L]+[t for t in repricing_boundaries(cands,w0,v,L,U) if L<t<U]+[U]
    pts=sorted(set(pts))
    return tuple((a,b,price_winners(cands,w0,v,(a+b)/2)) for a,b in zip(pts,pts[1:]) if a<b)

def finite_certificate():
    checks={}
    budget_systems=budget_points=unique_stabilizations=0
    for objs in product(range(3),repeat=3):
        for order in permutations(range(3)):
            tau={idx:i+1 for i,idx in enumerate(order)}
            cs=tuple(make_search(f'm{i}',objs[i],tau[i]) for i in range(3))
            vals=[]
            for B in (1,2,3):
                val=budget_best_value(cs,B); assert val is not None; vals.append(val); budget_points+=1
            if not (vals[0]>=vals[1]>=vals[2]): raise AssertionError('budget value worsened')
            sb=stabilization_budget(cs)
            if sb is not None:
                unique_stabilizations+=1
                g=budget_winners(cs,sb)
                for B in range(sb,4):
                    if budget_winners(cs,B)!=g: raise AssertionError('unique optimum failed to stabilize')
            budget_systems+=1
    checks['finite_budget_monotonicity_and_stabilization']=budget_systems==162 and budget_points==486 and unique_stabilizations>0
    hostile=(make_search('early',1,1),make_search('late',0,2))
    checks['finite_budget_hostile']=budget_winners(hostile,1)==('early',) and budget_winners(hostile,2)==('late',)

    regs=(Regime('e1',F('1/3')),Regime('e2',F('1/3')),Regime('e3',F('1/3')))
    cids=('A','B','C')
    niche_costs={('e1','A'):0,('e1','B'):2,('e1','C'):2,
                 ('e2','A'):2,('e2','B'):0,('e2','C'):2,
                 ('e3','A'):2,('e3','B'):2,('e3','C'):0}
    ns=niche_summary(cids,regs,niche_costs)
    checks['exact_niche_partition_coexistence']=ns['robust_coexistence'] and ns['robust_forms']==('A','B','C') and all(ns['lower'][c]==F('1/3') for c in cids)
    tie_costs={('e1','A'):0,('e1','B'):0,('e1','C'):2,
               ('e2','A'):2,('e2','B'):0,('e2','C'):2,
               ('e3','A'):2,('e3','B'):2,('e3','C'):0}
    nts=niche_summary(cids,regs,tie_costs)
    checks['tie_preserves_share_bounds']=nts['lower']['A']==0 and nts['upper']['A']==F('1/3') and nts['lower']['B']==F('1/3') and nts['upper']['B']==F('2/3')
    niche_census=0
    for bits in product((0,1),repeat=9):
        costs={(r.rid,cids[j]):bits[3*i+j] for i,r in enumerate(regs) for j in range(3)}
        x=niche_summary(cids,regs,costs)
        for c in cids:
            if not (F(0)<=x['lower'][c]<=x['upper'][c]<=F(1)): raise AssertionError('share bound violation')
        niche_census+=1
    checks['niche_share_bound_census']=niche_census==512

    rc=(make_resource('A',(1,4)),make_resource('B',(4,1)),make_resource('C',(2,2)))
    w0=(0,1); v=(1,-1); lo=F('1/5'); hi=F('4/5')
    bounds=repricing_boundaries(rc,w0,v,lo,hi)
    cells=repricing_cells(rc,w0,v,lo,hi)
    checks['repricing_boundaries_exact']=bounds==(F('1/3'),F('1/2'),F('2/3'))
    checks['repricing_lower_envelope']=tuple(w for _,_,w in cells)==(('B',),('C',),('C',),('A',))
    checks['non_envelope_crossing_preserved']=price_winners(rc,w0,v,F('1/2'))==('C',)
    repricing_checks=0
    for a,b,w in cells:
        for q in (F('1/4'),F('1/2'),F('3/4')):
            if price_winners(rc,w0,v,a+(b-a)*q)!=w: raise AssertionError('repricing changed inside cell')
            repricing_checks+=1
    checks['repricing_cell_checks']=repricing_checks==12

    if not all(checks.values()): raise AssertionError(checks)
    return {'schema':'GMI_833_BUDGET_NICHE_REPRICING_RESULT_V1','claim_ceiling':CLAIM_CEILING,'verdict':'GREEN','checks':checks,
            'counts':{'budget_systems':budget_systems,'budget_points':budget_points,'unique_stabilizations':unique_stabilizations,'niche_cost_census':niche_census,'repricing_cell_checks':repricing_checks},
            'witnesses':{'finite_budget_B1':['early'],'finite_budget_B2':['late'],'niche_lower':{k:str(v) for k,v in ns['lower'].items()},'repricing_boundaries':[str(x) for x in bounds]},
            'forbidden_promotions':['PROSPECTIVE_TRANSITIONS_VALIDATED','INDEPENDENT_REAL_SYSTEM_REPLICATION','STOCHASTIC_ECOLOGY_DYNAMICS_CLOSED','REAL_SCALE_VALIDATION','COMPLETE_GMI']}

def main(): print(json.dumps(finite_certificate(),sort_keys=True,separators=(',',':')))
if __name__=='__main__': main()
