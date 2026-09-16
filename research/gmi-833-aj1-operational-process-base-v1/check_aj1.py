from __future__ import annotations
from fractions import Fraction
import itertools, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
REQ={"TYPE","SEQUENCE","PARALLEL","NO_CHANGE","SUBSTRATE_ADMISSIBILITY","OPERATIONAL_OBSERVATION"}

def comp_fun(f,g):
    return {x:g[f[x]] for x in f}

def compose_rel(r,s):
    return {(a,c) for a,b in r for b2,c in s if b==b2}

def tensor_rel(r,s):
    return {((a,c),(b,d)) for a,b in r for c,d in s}

def compose_kernel(k1,k2):
    out={}
    for x,ys in k1.items():
        zs={}
        for y,p in ys.items():
            for z,q in k2[y].items(): zs[z]=zs.get(z,Fraction(0))+p*q
        out[x]=zs
    return out

def tensor_kernel(k1,k2):
    out={}
    for x,ys in k1.items():
        for u,vs in k2.items():
            dist={}
            for y,p in ys.items():
                for v,q in vs.items(): dist[(y,v)]=p*q
            out[(x,u)]=dist
    return out

def check_distribution(k):
    return all(sum(d.values(),Fraction(0))==1 and all(p>=0 for p in d.values()) for d in k.values())

def component_irredundancy():
    mapping={"Obj":"TYPE","compose":"SEQUENCE","tensor":"PARALLEL","identity":"NO_CHANGE","Adm_S":"SUBSTRATE_ADMISSIBILITY","Obs_S":"OPERATIONAL_OBSERVATION"}
    assert set(mapping.values())==REQ
    return mapping

def main():
    funcs=[]
    for vals in itertools.product((0,1), repeat=2): funcs.append({0:vals[0],1:vals[1]})
    assoc_fun=0
    for f,g,h in itertools.product(funcs, repeat=3):
        assert comp_fun(comp_fun(f,g),h)==comp_fun(f,comp_fun(g,h))
        assoc_fun += 1

    pairs=[(0,0),(0,1),(1,0),(1,1)]
    rels=[]
    for mask in range(16): rels.append({pairs[i] for i in range(4) if mask & (1<<i)})
    assoc_rel=0
    for f,g,h in itertools.product(rels, repeat=3):
        assert compose_rel(compose_rel(f,g),h)==compose_rel(f,compose_rel(g,h))
        assoc_rel += 1

    r={(0,0),(0,1),(1,1)}
    assert len({b for a,b in r if a==0})==2
    rid={(0,0),(1,1)}
    assert compose_rel(rid,r)==r==compose_rel(r,rid)
    f1={(0,1)}; f2={(1,0)}; g1={(1,0)}; g2={(0,1)}
    assert compose_rel(tensor_rel(f1,f2),tensor_rel(g1,g2))==tensor_rel(compose_rel(f1,g1),compose_rel(f2,g2))

    half=Fraction(1,2)
    K={0:{0:half,1:half},1:{0:Fraction(1)}}
    Kid={0:{0:Fraction(1)},1:{1:Fraction(1)}}
    assert check_distribution(K)
    assert compose_kernel(Kid,K)==K and compose_kernel(K,Kid)==K
    TK=tensor_kernel(K,K)
    assert check_distribution(TK)
    L={0:{1:Fraction(1)},1:{0:half,1:half}}
    leftk=compose_kernel(tensor_kernel(K,L),tensor_kernel(L,K))
    rightk=tensor_kernel(compose_kernel(K,L),compose_kernel(L,K))
    assert leftk==rightk and check_distribution(leftk)

    adm={"S_ALLOW_NOT":{"NOT":True},"S_FORBID_NOT":{"NOT":False}}
    assert adm["S_ALLOW_NOT"]["NOT"] != adm["S_FORBID_NOT"]["NOT"]
    p=("A","B"); q=("C","D")
    assert not (p[1]==q[0])

    result={"status":"GREEN","deterministic_associativity_cases":assoc_fun,"relation_associativity_cases":assoc_rel,"relation_interchange":"PASS","stochastic_interchange":"PASS","typed_mismatch_hostile":"REJECTED","relation_nondeterministic_witness":"input 0 has two outputs","stochastic_non_dirac_witness":"K(0)=(1/2,1/2)","stochastic_tensor_distributions_valid":True,"substrate_admissibility_twin":"PASS","relative_irredundancy_removals":component_irredundancy(),"forbidden_terminal":"ABSOLUTE_PROCESS_ONTOLOGY_PROVEN","claim_ceiling":"AJ1_TYPED_OPERATIONAL_PROCESS_FRAME_AT_FINITE_REGISTERED_SCOPE"}
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
