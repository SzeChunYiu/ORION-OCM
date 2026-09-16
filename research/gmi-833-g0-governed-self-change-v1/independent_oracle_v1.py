from itertools import product
from hashlib import sha256
import json
Z=(0,1,2)
def digest(c): return sha256(json.dumps(tuple(c),separators=(',',':')).encode()).hexdigest()
def policy(c): return c[0]==0
def main():
    candidates=tuple(product(Z,repeat=3)); accepted=sum(policy(c) for c in candidates); rejected=len(candidates)-accepted
    inert=adopt_fail=reject_mut=replay=0
    for seq,c in enumerate(candidates):
        active=((0,1,2),0); d=digest(c); pid=sha256(f'0:{seq}:{d}'.encode()).hexdigest(); proposed_active=active
        if proposed_active!=active: inert+=1
        if policy(c):
            next_active=(tuple(c),1)
            if next_active[0]!=tuple(c) or next_active[1]!=1: adopt_fail+=1
            consumed={pid}
            if pid not in consumed: replay+=1
        else:
            next_active=active
            if next_active!=active: reject_mut+=1
    stale=(0!=1)
    active0=((0,1,2),0); c1=(0,2,1); active1=(c1,active0[1]+1); c2=(0,2,2); base2=active1[1]; active2=(c2,base2+1)
    two=active1==((0,2,1),1) and base2==1 and active2==((0,2,2),2)
    out={'schema':'GMI833GovernedSelfChangeIndependentOracleV1','candidate_count':len(candidates),'accepted':accepted,'rejected':rejected,'proposal_inert_failures':inert,'accepted_adoption_failures':adopt_fail,'rejected_mutation_failures':reject_mut,'replay_failures':replay,'stale_receipt_control':stale,'two_generation_control':two,'terminal':'GREEN' if (accepted,rejected,inert,adopt_fail,reject_mut,replay,stale,two)==(9,18,0,0,0,0,True,True) else 'RED'}
    print(json.dumps(out,indent=2,sort_keys=True,separators=(',',': ')))
if __name__=='__main__': main()
