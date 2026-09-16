from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import permutations, product
from typing import Iterable, Tuple
import json

SOURCE_MAIN='43102437ebcbf6f818bb58b45470beffaf865029'
FREEZE_COMMIT='e05a2849d3bf71b0130085d880c7607ce0f507fa'
CLAIM_CEILING='GMI_FINITE_EXACT_STOCHASTIC_UPDATE_OPERATOR_AT_REGISTERED_SCOPE'
FORBIDDEN_PROMOTIONS=(
 'GENERAL_MEASURABLE_MARKOV_KERNEL','INFINITE_HORIZON_STOCHASTIC_THEORY',
 'FINITE_SAMPLE_IDENTIFICATION','BAYESIAN_INFERENCE_DERIVED',
 'PROBABILISTIC_PROGRAMMING_DERIVED','LATENT_CAUSAL_IDENTIFICATION',
 'STOCHASTIC_MORPHOLOGY_OPTIMAL','COMPLETE_GMI')
S=(0,1,2)
ZERO=Fraction(0,1); ONE=Fraction(1,1); HALF=Fraction(1,2)

@dataclass(frozen=True)
class DistributionV1:
    mass: Tuple[Fraction,Fraction,Fraction]

@dataclass(frozen=True)
class KernelV1:
    rows: Tuple[Tuple[Fraction,Fraction,Fraction],Tuple[Fraction,Fraction,Fraction],Tuple[Fraction,Fraction,Fraction]]

@dataclass(frozen=True)
class OpResult:
    value: object
    resources: Tuple[int,int,int,int,int]

UPDATE_RESOURCES=(3,9,9,6,3)
COMPOSE_RESOURCES=(0,54,27,18,9)

def _strict_fraction(x):
    if type(x) is not Fraction: raise ValueError('PROBABILITY_NOT_FRACTION')
    if x < 0: raise ValueError('NEGATIVE_PROBABILITY')
    return x

def distribution(values: Iterable[Fraction]) -> DistributionV1:
    vals=tuple(values)
    if len(vals)!=3: raise ValueError('DISTRIBUTION_DIMENSION')
    for x in vals: _strict_fraction(x)
    if sum(vals,ZERO)!=ONE: raise ValueError('DISTRIBUTION_NOT_NORMALIZED')
    return DistributionV1(vals)

def kernel(rows: Iterable[Iterable[Fraction]]) -> KernelV1:
    rows=tuple(tuple(r) for r in rows)
    if len(rows)!=3 or any(len(r)!=3 for r in rows): raise ValueError('KERNEL_DIMENSION')
    return KernelV1(tuple(distribution(r).mass for r in rows))

def update(mu:DistributionV1,K:KernelV1)->OpResult:
    if not isinstance(mu,DistributionV1): raise ValueError('INVALID_DISTRIBUTION_OBJECT')
    if not isinstance(K,KernelV1): raise ValueError('INVALID_KERNEL_OBJECT')
    out=tuple(sum((mu.mass[i]*K.rows[i][j] for i in S),ZERO) for j in S)
    return OpResult(distribution(out),UPDATE_RESOURCES)

def compose(K1:KernelV1,K2:KernelV1)->OpResult:
    if not isinstance(K1,KernelV1) or not isinstance(K2,KernelV1): raise ValueError('INVALID_KERNEL_OBJECT')
    rows=tuple(tuple(sum((K1.rows[i][k]*K2.rows[k][j] for k in S),ZERO) for j in S) for i in S)
    return OpResult(kernel(rows),COMPOSE_RESOURCES)

def identity_kernel()->KernelV1:
    return kernel(tuple(tuple(ONE if i==j else ZERO for j in S) for i in S))

def deterministic_kernel(mapping:Iterable[int])->KernelV1:
    m=tuple(mapping)
    if len(m)!=3 or any(type(x) is not int or x not in S for x in m): raise ValueError('DETERMINISTIC_MAP_DOMAIN')
    return kernel(tuple(tuple(ONE if j==m[i] else ZERO for j in S) for i in S))

def point_mass(i:int)->DistributionV1:
    if type(i) is not int or i not in S: raise ValueError('STATE_OUTSIDE_CARRIER')
    return distribution(tuple(ONE if j==i else ZERO for j in S))

def validate_perm(pi:Iterable[int])->Tuple[int,int,int]:
    p=tuple(pi)
    if len(p)!=3 or set(p)!=set(S): raise ValueError('NON_BIJECTIVE_RELABELING')
    return p

def transport_distribution(mu:DistributionV1,pi:Iterable[int])->DistributionV1:
    p=validate_perm(pi); out=[ZERO,ZERO,ZERO]
    for i in S: out[p[i]]=mu.mass[i]
    return distribution(out)

def transport_kernel(K:KernelV1,pi:Iterable[int])->KernelV1:
    p=validate_perm(pi); rows=[[ZERO]*3 for _ in S]
    for i in S:
        for j in S: rows[p[i]][p[j]]=K.rows[i][j]
    return kernel(tuple(tuple(r) for r in rows))

def row_family()->Tuple[DistributionV1,...]:
    return tuple(distribution(r) for r in ((ONE,ZERO,ZERO),(ZERO,ONE,ZERO),(ZERO,ZERO,ONE),(HALF,HALF,ZERO),(HALF,ZERO,HALF),(ZERO,HALF,HALF)))

@lru_cache(maxsize=1)
def kernel_family()->Tuple[KernelV1,...]:
    rows=row_family()
    return tuple(kernel((a.mass,b.mass,c.mass)) for a,b,c in product(rows,repeat=3))

def predictive_to_confidence(_:object)->str: return 'CANNOT_COERCE_PREDICTIVE_LAW_WITHOUT_CONFIDENCE_PREMISE'
def marginal_latent_decomposition(_:object)->str: return 'CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS'

def _independent_compose(K1:KernelV1,K2:KernelV1)->KernelV1:
    cols=tuple(tuple(K2.rows[i][j] for i in S) for j in S)
    return kernel(tuple(tuple(sum((a*b for a,b in zip(row,col)),ZERO) for col in cols) for row in K1.rows))

@lru_cache(maxsize=1)
def exact_census():
    rows=row_family(); ks=kernel_family(); perms=tuple(permutations(S))
    law_checks=law_fail=0
    for K in ks:
        for mu in rows:
            law_checks+=1
            try: update(mu,K)
            except ValueError: law_fail+=1
    cov_checks=cov_fail=0
    for K in ks:
        for mu in rows:
            base=update(mu,K).value
            for p in perms:
                cov_checks+=1
                if transport_distribution(base,p)!=update(transport_distribution(mu,p),transport_kernel(K,p)).value: cov_fail+=1
    I=identity_kernel(); id_fail=0
    for K in ks:
        if compose(I,K).value!=K or compose(K,I).value!=K: id_fail+=1
    pair_checks=pair_valid_fail=pair_impl_mismatch=seq_checks=seq_fail=cov_comp_fail=0
    transposition=(1,0,2); basis=tuple(point_mass(i) for i in S)
    for K1 in ks:
        t1=transport_kernel(K1,transposition)
        for K2 in ks:
            pair_checks+=1; C=compose(K1,K2).value
            try: kernel(C.rows)
            except ValueError: pair_valid_fail+=1
            if C != _independent_compose(K1,K2): pair_impl_mismatch+=1
            for mu in basis:
                seq_checks+=1
                if update(update(mu,K1).value,K2).value!=update(mu,C).value: seq_fail+=1
            if transport_kernel(C,transposition)!=compose(t1,transport_kernel(K2,transposition)).value: cov_comp_fail+=1
    det_checks=det_fail=0
    for mapping in product(S,repeat=3):
        K=deterministic_kernel(mapping)
        for i in S:
            det_checks+=1
            if update(point_mass(i),K).value != point_mass(mapping[i]): det_fail+=1
    return {'row_family_count':len(rows),'kernel_count':len(ks),'law_preservation_checks':law_checks,'law_preservation_failures':law_fail,'one_step_covariance_checks':cov_checks,'one_step_covariance_failures':cov_fail,'composition_pair_checks':pair_checks,'composition_invalid_failures':pair_valid_fail,'composition_implementation_mismatches':pair_impl_mismatch,'sequential_basis_checks':seq_checks,'sequential_basis_failures':seq_fail,'composition_covariance_transposition_checks':pair_checks,'composition_covariance_failures':cov_comp_fail,'identity_kernel_failures':id_fail,'deterministic_specialization_checks':det_checks,'deterministic_specialization_failures':det_fail}

def positive_controls():
    I=identity_kernel(); absorbing=kernel(((ONE,ZERO,ZERO),(ONE,ZERO,ZERO),(ONE,ZERO,ZERO))); cycle=deterministic_kernel((1,2,0)); stochastic=kernel(((HALF,HALF,ZERO),(ZERO,HALF,HALF),(HALF,ZERO,HALF))); quarter=compose(stochastic,stochastic).value
    return {'identity_point':update(point_mass(2),I).value.mass==point_mass(2).mass,'absorbing':update(point_mass(1),absorbing).value.mass==point_mass(0).mass,'cycle':update(point_mass(2),cycle).value.mass==point_mass(0).mass,'mixture':update(point_mass(0),stochastic).value.mass==(HALF,HALF,ZERO),'genuinely_stochastic':any(any(x not in (ZERO,ONE) for x in row) for row in stochastic.rows),'quarter_after_composition':any(x.denominator==4 for row in quarter.rows for x in row)}

def hostile_results():
    out={}; cases=[('float_distribution',lambda:distribution((0.5,0.5,0.0))),('integer_distribution',lambda:distribution((1,0,0))),('negative',lambda:distribution((Fraction(-1,2),Fraction(3,2),ZERO))),('bad_sum',lambda:distribution((HALF,ZERO,ZERO))),('bad_dim',lambda:distribution((ONE,ZERO))),('kernel_dim',lambda:kernel(((ONE,ZERO,ZERO),))),('kernel_row_sum',lambda:kernel(((ONE,ZERO,ZERO),(ONE,ZERO,ZERO),(HALF,ZERO,ZERO)))),('bad_perm',lambda:validate_perm((0,0,2))),('state_outside',lambda:point_mass(3))]
    for name,fn in cases:
        try: fn(); out[name]='ACCEPTED'
        except ValueError as e: out[name]=str(e)
    out['confidence_boundary']=predictive_to_confidence(kernel_family()[0]); out['latent_boundary']=marginal_latent_decomposition(kernel_family()[0]); return out

def build_receipt():
    c=exact_census(); p=positive_controls(); h=hostile_results()
    green=(c['row_family_count']==6 and c['kernel_count']==216 and c['law_preservation_checks']==1296 and c['law_preservation_failures']==0 and c['one_step_covariance_checks']==7776 and c['one_step_covariance_failures']==0 and c['composition_pair_checks']==46656 and c['composition_invalid_failures']==0 and c['composition_implementation_mismatches']==0 and c['sequential_basis_checks']==139968 and c['sequential_basis_failures']==0 and c['composition_covariance_failures']==0 and c['identity_kernel_failures']==0 and c['deterministic_specialization_checks']==81 and c['deterministic_specialization_failures']==0 and all(p.values()) and 'ACCEPTED' not in h.values() and h['confidence_boundary'].startswith('CANNOT_') and h['latent_boundary'].startswith('CANNOT_'))
    return {'schema':'GMI833FiniteStochasticUpdateReceiptV1','parent_issue':833,'issue':885,'source_main':SOURCE_MAIN,'freeze_commit':FREEZE_COMMIT,'probability_type':'fractions.Fraction','state_count':3,'update_resources':list(UPDATE_RESOURCES),'compose_resources':list(COMPOSE_RESOURCES),'census':c,'positive_controls':p,'hostile_results':h,'claim_ceiling':CLAIM_CEILING,'forbidden_promotions':list(FORBIDDEN_PROMOTIONS),'terminal':'GMI_833_FINITE_STOCHASTIC_UPDATE_V1_ALL_GREEN' if green else 'RED'}
def canonical_json(obj): return json.dumps(obj,indent=2,sort_keys=True,separators=(',',': '))+'\n'
def main(): print(canonical_json(build_receipt()),end='')
if __name__=='__main__': main()
