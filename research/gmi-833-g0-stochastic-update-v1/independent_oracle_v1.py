from __future__ import annotations
from fractions import Fraction as F
from itertools import permutations, product
import json
S=(0,1,2); Z=F(0,1); O=F(1,1); H=F(1,2)
ROWS=((O,Z,Z),(Z,O,Z),(Z,Z,O),(H,H,Z),(H,Z,H),(Z,H,H))
def mul_vec(mu,K): return tuple(sum((mu[i]*K[i][j] for i in S),Z) for j in S)
def mul_mat(A,B):
    cols=tuple(tuple(B[i][j] for i in S) for j in S)
    return tuple(tuple(sum((a*b for a,b in zip(row,col)),Z) for col in cols) for row in A)
def tvec(mu,p):
    out=[Z,Z,Z]
    for i in S: out[p[i]]=mu[i]
    return tuple(out)
def tmat(K,p):
    out=[[Z]*3 for _ in S]
    for i in S:
        for j in S: out[p[i]][p[j]]=K[i][j]
    return tuple(tuple(r) for r in out)
def valid_dist(x): return len(x)==3 and all(type(v) is F and v>=0 for v in x) and sum(x,Z)==O
def valid_kernel(K): return len(K)==3 and all(valid_dist(r) for r in K)
def main():
    kernels=tuple(product(ROWS,repeat=3)); perms=tuple(permutations(S)); basis=ROWS[:3]
    law=lawbad=cov=covbad=0
    for K in kernels:
      for mu in ROWS:
        law+=1
        if not valid_dist(mul_vec(mu,K)): lawbad+=1
        base=mul_vec(mu,K)
        for p in perms:
          cov+=1
          if tvec(base,p)!=mul_vec(tvec(mu,p),tmat(K,p)): covbad+=1
    pair=invalid=seq=seqbad=compcovbad=0; p=(1,0,2); I=ROWS[:3]; idbad=0
    for K in kernels:
      if mul_mat(I,K)!=K or mul_mat(K,I)!=K: idbad+=1
    for A in kernels:
      tA=tmat(A,p)
      for B in kernels:
        pair+=1; C=mul_mat(A,B)
        if not valid_kernel(C): invalid+=1
        for mu in basis:
          seq+=1
          if mul_vec(mul_vec(mu,A),B)!=mul_vec(mu,C): seqbad+=1
        if tmat(C,p)!=mul_mat(tA,tmat(B,p)): compcovbad+=1
    det=detbad=0
    for f in product(S,repeat=3):
      K=tuple(tuple(O if j==f[i] else Z for j in S) for i in S)
      for i in S:
        det+=1
        if mul_vec(basis[i],K)!=basis[f[i]]: detbad+=1
    out={'schema':'GMI833FiniteStochasticUpdateIndependentOracleV1','row_family_count':6,'kernel_count':216,'law_preservation_checks':law,'law_preservation_failures':lawbad,'one_step_covariance_checks':cov,'one_step_covariance_failures':covbad,'composition_pair_checks':pair,'composition_invalid_failures':invalid,'sequential_basis_checks':seq,'sequential_basis_failures':seqbad,'composition_covariance_failures':compcovbad,'identity_kernel_failures':idbad,'deterministic_specialization_checks':det,'deterministic_specialization_failures':detbad,'terminal':'GREEN' if not any((lawbad,covbad,invalid,seqbad,compcovbad,idbad,detbad)) else 'RED'}
    print(json.dumps(out,indent=2,sort_keys=True,separators=(',',': ')))
if __name__=='__main__': main()
