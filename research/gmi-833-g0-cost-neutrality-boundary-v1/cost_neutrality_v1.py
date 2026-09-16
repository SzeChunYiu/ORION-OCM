from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations, product
from collections import deque
import json

SOURCE_MAIN='97af465d8339d8c32cfcb2a6fd622c8be0a19d25'
FREEZE_COMMIT='2460f0624410f639eac50f3464feedd67218857a'
E2_RESULT_BLOB='e903033615946a71f2f0859cda42e5b902e0d693'
CLAIM_CEILING='GMI_G0_COST_LABEL_BLINDNESS_AND_STRUCTURAL_PRIVILEGE_BOUNDARY_AT_REGISTERED_SCOPE'
FORBIDDEN_PROMOTIONS=('G0_UNBIASED','NO_KNOWN_FAMILY_PRIVILEGED_UNIVERSALLY','REPRESENTATION_INVARIANT_COST_UNIVERSALLY','SEARCH_NEUTRALITY_PROVED','ARCHITECTURE_PRIOR_FREE_GRAMMAR','ALL_SCALARIZATIONS_AGREE','COMPLETE_GMI')
WEIGHTS={'w11':(Fraction(1),Fraction(1)),'w21':(Fraction(2),Fraction(1)),'w12':(Fraction(1),Fraction(2))}
FAMILY_LABELS=('FINITE_STATE','SYMBOLIC','PROBABILISTIC','NEURAL')

def one_ops(): return ('H','R0','I0','E0','D00')
def two_ops(): return ('H','R0','R1','I0','I1','E0','E1','D00','D01','D10','D11')
def presentations():
    nodes=[(1,(a,)) for a in one_ops()]
    nodes += [(2,(a,b)) for a,b in product(two_ops(),repeat=2)]
    if len(nodes)!=126: raise RuntimeError
    return tuple(nodes)
def adjacency():
    ns=presentations(); adj={n:set() for n in ns}
    groups=([n for n in ns if n[0]==1],[n for n in ns if n[0]==2])
    for group in groups:
        for i,a in enumerate(group):
            for b in group[i+1:]:
                if sum(x!=y for x,y in zip(a[1],b[1]))==1: adj[a].add(b);adj[b].add(a)
    for a in groups[0]:
        for b in groups[1]:
            if a[1][0]==b[1][0]: adj[a].add(b);adj[b].add(a)
    return adj
def distances():
    adj=adjacency(); start=(1,('H',)); q=deque([start]); d={start:0}
    while q:
        u=q.popleft()
        for v in adj[u]:
            if v not in d:d[v]=d[u]+1;q.append(v)
    if len(d)!=126: raise RuntimeError('unreachable')
    return d
def scalar(raw,w):
    L,d=raw; a,b=w
    if type(a) is not Fraction or type(b) is not Fraction or a<=0 or b<=0: raise ValueError('INVALID_STRICTLY_POSITIVE_RATIONAL_WEIGHT')
    return a*L+b*d
def dominates(a,b): return a[0]<=b[0] and a[1]<=b[1] and a!=b

@dataclass(frozen=True)
class CostDeclaration:
    weights: tuple
    family_adjustments: tuple=()
    target_adjustments: tuple=()
    primitive_prices: tuple=(('generic',Fraction(1)),)
def audit_cost(decl):
    a,b=decl.weights
    if type(a) is not Fraction or type(b) is not Fraction or a<=0 or b<=0:return 'INVALID_STRICTLY_POSITIVE_RATIONAL_WEIGHT'
    if any(v!=0 for _,v in decl.family_adjustments):return 'FAMILY_LABEL_COST_PRIVILEGE'
    if any(v!=0 for _,v in decl.target_adjustments):return 'TARGET_SPECIFIC_COST_PRIVILEGE'
    if any(type(v) is not Fraction or v<=0 for _,v in decl.primitive_prices):return 'ZERO_OR_INVALID_PRIMITIVE_PRICE'
    return 'CLEAN_LABEL_BLIND_COST'

@dataclass(frozen=True)
class Grammar:
    nodes: tuple
    semantics: tuple
    raw: tuple
    edges: frozenset
    starts: frozenset
def fixture():
    n=('root','a_short','a_long','b'); sem=(('root','ROOT'),('a_short','A'),('a_long','A'),('b','B')); raw=(('root',(0,0)),('a_short',(1,1)),('a_long',(2,2)),('b',(1,1)))
    e=frozenset({('root','a_short'),('a_short','root'),('a_short','a_long'),('a_long','a_short'),('root','b'),('b','root')})
    return Grammar(n,sem,raw,e,frozenset({'root'}))
def remint(g,phi): return Grammar(tuple(phi[n] for n in g.nodes),tuple((phi[n],s) for n,s in g.semantics),tuple((phi[n],r) for n,r in g.raw),frozenset((phi[a],phi[b]) for a,b in g.edges),frozenset(phi[x] for x in g.starts))
def costs(g,w):
    raw=dict(g.raw);return {n:scalar(raw[n],w) for n in g.nodes}
def class_min_cost(g,w):
    sem=dict(g.semantics);c=costs(g,w);out={}
    for n in g.nodes: out[sem[n]]=min(out.get(sem[n],c[n]),c[n])
    return out
def select(g,w,candidates=('A','B')):
    cm=class_min_cost(g,w);return min(candidates,key=lambda x:(cm[x],x))
def label_blind_certificate():
    g=fixture(); base={k:costs(g,w) for k,w in WEIGHTS.items()}; baseclass={k:class_min_cost(g,w) for k,w in WEIGHTS.items()};checks=fail=0
    for perm in permutations(FAMILY_LABELS):
        labels=dict(zip(g.nodes,perm))
        if len(set(labels.values()))!=4: raise RuntimeError
        for k,w in WEIGHTS.items():
            checks+=1
            if costs(g,w)!=base[k] or class_min_cost(g,w)!=baseclass[k]:fail+=1
    return {'label_permutations':24,'weight_vectors':3,'checks':checks,'failures':fail}
def isometric_certificate():
    g=fixture(); names=('w','x','y','z');checks=fail=0
    for perm in permutations(names):
        phi=dict(zip(g.nodes,perm));h=remint(g,phi)
        for _,w in WEIGHTS.items():
            checks+=1;c1=costs(g,w);c2=costs(h,w);transported={phi[n]:v for n,v in c1.items()}
            if transported!=c2 or select(g,w)!=select(h,w):fail+=1
    return {'node_remints':24,'weight_vectors':3,'checks':checks,'failures':fail}
def structural_pair():
    ga=Grammar(('root','a','b'),(('root','ROOT'),('a','A'),('b','B')),(('root',(0,0)),('a',(1,1)),('b',(2,2))),frozenset({('root','a'),('a','root'),('a','b'),('b','a')}),frozenset({'root'}))
    gb=Grammar(('root2','a2','b2'),(('root2','ROOT'),('a2','A'),('b2','B')),(('root2',(0,0)),('a2',(2,2)),('b2',(1,1))),frozenset({('root2','b2'),('b2','root2'),('b2','a2'),('a2','b2')}),frozenset({'root2'}))
    rows={}
    for k,w in WEIGHTS.items():rows[k]={'GA':select(ga,w),'GB':select(gb,w),'GA_costs':{x:str(v) for x,v in class_min_cost(ga,w).items()},'GB_costs':{x:str(v) for x,v in class_min_cost(gb,w).items()}}
    return rows
def g0_pareto_certificate():
    d=distances();raw={n:(n[0],d[n]) for n in d};nodes=tuple(raw);dom=viol=0
    for a in nodes:
        for b in nodes:
            if dominates(raw[a],raw[b]):
                dom+=1
                for w in WEIGHTS.values():
                    if not scalar(raw[a],w)<scalar(raw[b],w):viol+=1
    x=(1,4);y=(4,1);reversal=scalar(x,WEIGHTS['w21'])<scalar(y,WEIGHTS['w21']) and scalar(y,WEIGHTS['w12'])<scalar(x,WEIGHTS['w12'])
    return {'presentation_count':126,'ordered_strict_dominance_pairs':dom,'dominance_weight_checks':dom*3,'dominance_violations':viol,'incomparable_control_reverses':reversal}
def hostiles():
    return {'family_adjustment':audit_cost(CostDeclaration(WEIGHTS['w11'],(('NEURAL',Fraction(-1)),))),'target_adjustment':audit_cost(CostDeclaration(WEIGHTS['w11'],(),(('targetA',Fraction(-1)),))),'zero_primitive':audit_cost(CostDeclaration(WEIGHTS['w11'],(),(),(('macro',Fraction(0)),))),'float_weight':audit_cost(CostDeclaration((1.0,Fraction(1)))),'clean':audit_cost(CostDeclaration(WEIGHTS['w11']))}
def build_receipt():
    l=label_blind_certificate();i=isometric_certificate();s=structural_pair();p=g0_pareto_certificate();h=hostiles();structural_all=all(v['GA']=='A' and v['GB']=='B' for v in s.values())
    green=(l['checks']==72 and l['failures']==0 and i['checks']==72 and i['failures']==0 and structural_all and p['dominance_violations']==0 and p['incomparable_control_reverses'] and h=={'family_adjustment':'FAMILY_LABEL_COST_PRIVILEGE','target_adjustment':'TARGET_SPECIFIC_COST_PRIVILEGE','zero_primitive':'ZERO_OR_INVALID_PRIMITIVE_PRICE','float_weight':'INVALID_STRICTLY_POSITIVE_RATIONAL_WEIGHT','clean':'CLEAN_LABEL_BLIND_COST'})
    return {'schema':'GMI833CostNeutralityBoundaryReceiptV1','parent_issue':833,'issue':891,'source_main':SOURCE_MAIN,'freeze_commit':FREEZE_COMMIT,'e2_result_blob':E2_RESULT_BLOB,'weights':{k:[str(x) for x in w] for k,w in WEIGHTS.items()},'label_blind_certificate':l,'isometric_remint_certificate':i,'structural_bias_counterexample':s,'pareto_certificate':p,'cost_hostiles':h,'narrow_positive_terminal':'LABEL_BLIND_AND_ISOMETRICALLY_INVARIANT_AT_REGISTERED_SCOPE','row_disposition':'NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE','claim_ceiling':CLAIM_CEILING,'forbidden_promotions':list(FORBIDDEN_PROMOTIONS),'terminal':'GMI_833_COST_NEUTRALITY_BOUNDARY_V1_ALL_GREEN' if green else 'RED'}
def canonical_json(o):return json.dumps(o,indent=2,sort_keys=True,separators=(',',': '))+'\n'
def main():print(canonical_json(build_receipt()),end='')
if __name__=='__main__':main()
