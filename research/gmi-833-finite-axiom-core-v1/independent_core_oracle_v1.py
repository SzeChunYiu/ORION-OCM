from __future__ import annotations
from fractions import Fraction as F
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def frac(x): return F(x)

def main():
    m=json.loads((ROOT/'FINITE_MODEL_V1.json').read_text())
    states=tuple(m['states']); actions=tuple(m['actions']); outputs=set(m['outputs']); interventions=tuple(m['interventions']); iouts=set(m['intervention_outputs'])
    trans={(r['state'],r['action']):r['next'] for r in m['transition']}
    out={r['state']:r['value'] for r in m['output']}
    iresp={(r['state'],r['intervention']):r['value'] for r in m['intervention_response']}
    checks={}
    checks['typed_unique']=len(states)==len(set(states)) and bool(states) and len(actions)==len(set(actions)) and bool(actions)
    checks['transition_total']=set(trans)=={(s,a) for s in states for a in actions} and set(trans.values())<=set(states)
    checks['output_total']=set(out)==set(states) and set(out.values())<=outputs
    checks['intervention_total']=set(iresp)=={(s,j) for s in states for j in interventions} and set(iresp.values())<=iouts
    checks['development_typed']=all(a in states and b in states for a,b in m['development_edges'])
    checks['resources_nonnegative']=bool(m['resources']) and all(frac(x)>=0 for x in m['resources'])
    tags={o['tag'] for o in m['uncertainty_objects']}
    checks['uncertainty_tags']=tags=={'FeasibleSet','ConfidenceSet','PredictiveLaw','LatentPredictiveModel','SelectivePrediction'}
    confidence=next(o for o in m['uncertainty_objects'] if o['tag']=='ConfidenceSet')
    domain=set(confidence['domain']); vals=set(confidence['values']); truth={k:frac(v) for k,v in confidence['truth_law'].items()}; alpha=frac(confidence['alpha'])
    checks['confidence_valid']=vals<=domain and set(truth)==domain and sum(truth.values(),F(0))==1 and sum((truth[x] for x in vals),F(0))>=1-alpha
    allowed={('FINITE_MODEL_WITNESS','FINITE_EXISTENTIAL'),('FINITE_EXHAUSTIVE','BOUNDED_FINITE'),('ANALYTIC_FINITE','REGISTERED_FINITE'),('UNIVERSAL_PROOF','UNIVERSAL')}
    checks['scope_monotone']=all((c['evidence_scope'],c['claim_scope']) in allowed for c in m['scope_claims'])

    blocks=[set(states)]
    while True:
        cls={s:i for i,b in enumerate(blocks) for s in b}
        groups={}
        for s in states:
            sig=(out[s],)+tuple(cls[trans[(s,a)]] for a in actions)
            groups.setdefault(sig,set()).add(s)
        new=list(groups.values())
        if {frozenset(x) for x in new}=={frozenset(x) for x in blocks}: break
        blocks=new
    quotient=sorted([sorted(x) for x in blocks])
    checks['behavioral_quotient']=quotient==[['s0','s1'],['s2']]

    def run(word):
        s=m['initial']
        for a in word:s=trans[(s,a)]
        return out[s]
    caps={}
    res=tuple(frac(x) for x in m['resources'])
    for c in m['capability_contracts']:
        budget=tuple(frac(x) for x in c['budget'])
        if any(r>b for r,b in zip(res,budget)): val=None
        else:
            den=sum((frac(t['weight']) for t in c['tasks']),F(0)); num=sum((frac(t['weight']) for t in c['tasks'] if run(t['word'])==t['target']),F(0)); val=num/den
        caps[c['id']]=None if val is None else str(val)
    checks['capability_certificates']=all(caps[k]==v for k,v in m['capability_certificates'].items())
    result={'schema':'GMI833IndependentFiniteCoreOracleV1','checks':checks,'behavioral_quotient':quotient,'capability_values':caps,'terminal':'GREEN' if all(checks.values()) else 'RED'}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
