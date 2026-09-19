#!/usr/bin/env python3
"""Route B (black-box): independently reproduce the set-valued emission census.

Reuses the frozen revive-kl package (unmodified, pinned) as the source of the
bridge table and the SIGMA_REAL4 population, and the UNMODIFIED parent F. Route
B installs concrete worlds on the registration surface (value-index worlds
plus seeded random product worlds) and runs the parent's `predict` end to end,
then unions the emitted identified sets and compares to route A's structural
I(x). It imports no route-A logic.
"""
from fractions import Fraction
import hashlib, json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'research' / 'gmi-833-capability-predictor-v1'))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'research' / 'gmi-833-kl-revival-v1'))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'research' / 'gmi-833-capability-predictor-evaluation-v1'))
import heldout_universes_v1 as hu
import heldout_universes_real4_v1 as r4

UNSAT='UNSATISFIED'
def val_key(v): return (1, Fraction(0)) if v==UNSAT else (0,v)
def union_sorted(s): return ','.join(str(v) for v in sorted(s,key=val_key))

def route_a_images(table):
    """Structural I(x) and I_PROTO(x) for every grid input (route A)."""
    parent=hu.load_parent()
    spec=r4.clean_spec(r4.sigma_real4(table))
    hu.install_universe(parent, spec)
    sets={}
    for contract in parent.CONTRACTS:
        verified=hu.VERIFIED[contract]
        sets[contract]=[r4.value_set(hu.MU_REAL,verified,r4.admissible_bits(table,m)) for m in r4.REAL4_MACHINES]
    out={}
    for idx,entry in enumerate(parent.main_grid()):
        k_index,r_value,d_value,b_value,h_value,u_id,u_kind,u_mask,alpha,contract,tau=entry
        survivors=parent.survivor_mask(k_index,d_value,b_value,h_value,u_mask)
        if survivors==0:
            out[idx]={'image':None,'n':0}; continue
        res=parent.RES_MASKS[r_value]
        admissible=survivors&res; refused=survivors&~res
        image=set()
        if refused: image.add(UNSAT)
        for i in parent.bits_of(admissible): image|=sets[contract][i]
        out[idx]={'image':image,'n':len(image)}
    return out

def route_b_emissions(table, rA, samples_per=1, rng=None):
    """Install explicit worlds and run predict end-to-end; union emitted sets."""
    import random
    rng = rng or random.Random(833)
    parent=hu.load_parent()
    base=hu.sigma_1(); fingerprint=hu.code_fingerprint(parent)
    base_spec=r4.clean_spec(r4.sigma_real4(table))
    machines=r4.REAL4_MACHINES; n=len(machines)
    adm=[r4.admissible_bits(table,m) for m in machines]
    mismatches=0; checked=0; sampled=0
    for idx,entry in enumerate(parent.main_grid()):
        k_index,r_value,d_value,b_value,h_value,u_id,u_kind,u_mask,alpha,contract,tau=entry
        survivors=parent.survivor_mask(k_index,d_value,b_value,h_value,u_mask)
        if survivors==0: continue
        expected=rA[idx]['image']
        got=set()
        # value-index worlds: world t gives machine i its (Idx+t) mod |Adm(i)|-th
        # admissible vector, so each admissible vector of each machine appears in
        # some world (Idx is the grid-row index, kept in [0, 32) via the cycle).
        for t in range(n):
            world=[]
            for i in range(n):
                ai=adm[i]
                world.append(ai[(idx + t) % len(ai)])
            spec=r4.spec_with_world(base_spec,machines,world)
            hu.install_universe(parent,spec)
            e=parent.predict(k_index,contract,r_value,h_value,d_value,b_value,u_kind,u_mask,alpha,'REGISTERED')
            if e.disposition=='IDENTIFIED': got.add(e.value)
            elif e.disposition=='CANNOT_IDENTIFY': got.update(e.identified_set)
        # seeded random product worlds: every emitted set must lie inside route A
        for _ in range(samples_per):
            world=[ai[rng.randrange(len(ai))] for ai in adm]
            spec=r4.spec_with_world(base_spec,machines,world)
            hu.install_universe(parent,spec)
            e=parent.predict(k_index,contract,r_value,h_value,d_value,b_value,u_kind,u_mask,alpha,'REGISTERED')
            if e.disposition=='IDENTIFIED':
                if e.value not in expected: mismatches+=1
            elif e.disposition=='CANNOT_IDENTIFY':
                if not set(e.identified_set)<=expected: mismatches+=1
            sampled+=1
        checked+=1
        if got!=expected:
            mismatches+=1
    after=hu.code_fingerprint(parent)
    assert after==fingerprint,'F code changed during route B'
    return checked,sampled,mismatches

def main():
    table,evidence=r4.derive_bridge()
    assert r4.bridge_matches_freeze(table), table
    rA=route_a_images(table)
    checked,sampled,mismatches=route_b_emissions(table,rA,samples_per=3)
    out={'schema':'GMI833KRealTrainedRouteBV1',
         'route_b_inputs_checked':checked,'random_product_worlds':sampled,
         'disagreements':mismatches,'two_routes_agree':mismatches==0,
         'verdict':'GREEN' if mismatches==0 else 'RED'}
    print(json.dumps(out,sort_keys=True,indent=2))
if __name__=='__main__': main()
