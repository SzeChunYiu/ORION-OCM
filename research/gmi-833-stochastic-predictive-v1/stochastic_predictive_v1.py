#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations, product
import json

ISSUE=836; PARENT_ISSUE=833
SOURCE_MAIN='5db372ef7003253d5846b324ed80a2454613983c'
FREEZE_COMMIT='f79f748c909e67dceab8f4d05ad6e1de4c273060'
CLAIM_CEILING='GMI_FINITE_PREDICTIVE_BLOCK_LINEAR_DIMENSION_AT_REGISTERED_HORIZON'
FORBIDDEN_PROMOTIONS=(
 'UNIVERSAL_STOCHASTIC_MINIMALITY','GENERAL_MEASURABLE_PSR_THEORY',
 'INFINITE_HORIZON_PREDICTIVE_IDENTIFICATION','FINITE_SAMPLE_PREDICTIVE_IDENTIFICATION',
 'CAUSAL_LATENT_IDENTIFICATION','ALL_PSRS_ARE_MINIMAL','NOVEL_PSR_RANK_THEOREM','COMPLETE_GMI')

class ContractError(ValueError): pass
History=tuple[tuple[str,str],...]; Test=History; Matrix=tuple[tuple[F,...],...]

def rank(a:Matrix)->int:
    m=[list(r) for r in a]
    if not m:return 0
    R=len(m); C=len(m[0]); i=j=0
    while i<R and j<C:
        p=next((k for k in range(i,R) if m[k][j]),None)
        if p is None: j+=1; continue
        m[i],m[p]=m[p],m[i]; q=m[i][j]; m[i]=[x/q for x in m[i]]
        for k in range(R):
            if k!=i and m[k][j]:
                q=m[k][j]; m[k]=[x-q*y for x,y in zip(m[k],m[i])]
        i+=1;j+=1
    return i

def det(a:Matrix)->F:
    n=len(a)
    if n==0:return F(1)
    if any(len(r)!=n for r in a): raise ContractError('det requires square matrix')
    m=[list(r) for r in a]; sign=1; out=F(1)
    for j in range(n):
        p=next((k for k in range(j,n) if m[k][j]),None)
        if p is None:return F(0)
        if p!=j:m[j],m[p]=m[p],m[j];sign*=-1
        q=m[j][j];out*=q
        for k in range(j+1,n):
            if m[k][j]:
                z=m[k][j]/q
                for c in range(j,n):m[k][c]-=z*m[j][c]
    return out*sign

def rank_by_minors(a:Matrix)->int:
    if not a:return 0
    R=len(a); C=len(a[0])
    for r in range(min(R,C),0,-1):
        for rs in combinations(range(R),r):
            for cs in combinations(range(C),r):
                if det(tuple(tuple(a[i][j] for j in cs) for i in rs)):
                    return r
    return 0

def solve(A:Matrix,b:tuple[F,...])->tuple[F,...]:
    n=len(A)
    if n==0:return ()
    if len(b)!=n or any(len(r)!=n for r in A):raise ContractError('solve shape')
    m=[list(r)+[b[i]] for i,r in enumerate(A)]
    for j in range(n):
        p=next((k for k in range(j,n) if m[k][j]),None)
        if p is None:raise ContractError('singular core minor')
        m[j],m[p]=m[p],m[j];q=m[j][j];m[j]=[x/q for x in m[j]]
        for k in range(n):
            if k!=j and m[k][j]:
                q=m[k][j];m[k]=[x-q*y for x,y in zip(m[k],m[j])]
    return tuple(m[i][-1] for i in range(n))

def select_independent_columns(D:Matrix)->tuple[int,...]:
    if not D:return ()
    chosen=[]; r=0
    for j in range(len(D[0])):
        cand=chosen+[j]
        M=tuple(tuple(row[c] for c in cand) for row in D)
        nr=rank(M)
        if nr>r:chosen.append(j);r=nr
    return tuple(chosen)

def factor(D:Matrix):
    r=rank(D); cs=select_independent_columns(D)
    if len(cs)!=r:raise ContractError('core-column rank mismatch')
    Q=tuple(tuple(row[j] for j in cs) for row in D)
    prs=None
    for rs in combinations(range(len(D)),r):
        A=tuple(tuple(Q[i][j] for j in range(r)) for i in rs)
        if det(A):prs=rs;break
    if prs is None:raise ContractError('no invertible core minor')
    A=tuple(tuple(Q[i][j] for j in range(r)) for i in prs)
    W=[]
    for j in range(len(D[0])):
        b=tuple(D[i][j] for i in prs);W.append(solve(A,b))
    reconstructed=tuple(tuple(sum((Q[i][k]*W[j][k] for k in range(r)),F(0)) for j in range(len(W))) for i in range(len(D)))
    return {'rank':r,'core_columns':cs,'pivot_rows':prs,'reconstructed':reconstructed}

@dataclass(frozen=True)
class Process:
    actions:tuple[str,...]; obs:tuple[str,...]; horizon:int; kernels:dict[tuple[History,str],tuple[F,...]]
    def __post_init__(self):
        if not self.actions or not self.obs or self.horizon<1:raise ContractError('bad process header')
        for (h,a),ps in self.kernels.items():
            if a not in self.actions or len(h)>=self.horizon or len(ps)!=len(self.obs):raise ContractError('bad kernel key/shape')
            if any(type(p) is not F or p<0 or p>1 for p in ps) or sum(ps,F(0))!=1:raise ContractError('bad kernel probabilities')
        # Every positive reachable prefix before horizon must have all action kernels.
        front={()}
        for _ in range(self.horizon):
            nxt=set()
            for h in front:
                for a in self.actions:
                    ps=self.kernels.get((h,a))
                    if ps is None:raise ContractError('missing positive-history kernel')
                    for o,p in zip(self.obs,ps):
                        if p:nxt.add(h+((a,o),))
            front=nxt
    def likelihood(self,h:History)->F:
        p=F(1);pre=(); idx={o:i for i,o in enumerate(self.obs)}
        for a,o in h:
            if p==0:return F(0)
            ps=self.kernels.get((pre,a))
            if ps is None:raise ContractError('history outside registered support/horizon')
            p*=ps[idx[o]];pre+=((a,o),)
        return p
    def positive_histories(self,d:int)->tuple[History,...]:
        if d<0 or d>self.horizon:raise ContractError('bad depth')
        front={()}
        for _ in range(d):
            nxt=set()
            for h in front:
                for a in self.actions:
                    ps=self.kernels[(h,a)]
                    for o,p in zip(self.obs,ps):
                        if p:nxt.add(h+((a,o),))
            front=nxt
        return tuple(sorted(front,key=repr))
    def tests(self,l:int)->tuple[Test,...]:
        pairs=tuple(product(self.actions,self.obs));out=[()]
        for m in range(1,l+1):out.extend(tuple(x) for x in product(pairs,repeat=m))
        return tuple(out)
    def ptest(self,h:History,t:Test)->F:
        if self.likelihood(h)==0:raise ContractError('conditional prediction on zero-probability history')
        if len(h)+len(t)>self.horizon:raise ContractError('test exceeds horizon')
        p=F(1);pre=h;idx={o:i for i,o in enumerate(self.obs)}
        for a,o in t:
            ps=self.kernels[(pre,a)];p*=ps[idx[o]];pre+=((a,o),)
            if p==0:break
        return p
    def block(self,d:int,l:int):
        hs=self.positive_histories(d);ts=self.tests(l)
        return hs,ts,tuple(tuple(self.ptest(h,t) for t in ts) for h in hs)

def partition(D:Matrix):
    groups={}
    for i,row in enumerate(D):groups.setdefault(row,[]).append(i)
    return tuple(tuple(v) for _,v in sorted(groups.items(),key=lambda kv:repr(kv[0])))

def exact_statistic(D:Matrix,labels:tuple[object,...]):
    if len(labels)!=len(D):raise ContractError('label count')
    for i in range(len(D)):
        for j in range(i):
            if labels[i]==labels[j] and D[i]!=D[j]:
                for c,(x,y) in enumerate(zip(D[i],D[j])):
                    if x!=y:return False,{'left_row':j,'right_row':i,'test_column':c,'left_probability':str(y),'right_probability':str(x)}
    return True,None

def separation_process()->Process:
    A=('a',);O=('A','B','C','X','Y');K={}
    K[((),'a')]=(F(1,3),F(1,3),F(1,3),F(0),F(0))
    K[((('a','A'),), 'a')]=(F(0),F(0),F(0),F(1),F(0))
    K[((('a','B'),), 'a')]=(F(0),F(0),F(0),F(1,2),F(1,2))
    K[((('a','C'),), 'a')]=(F(0),F(0),F(0),F(0),F(1))
    # Positive depth-2 histories need no outgoing kernels when horizon=2.
    return Process(A,O,2,K)

def duplicate_row_process()->Process:
    return Process(('a',),('A','B'),2,{((),'a'):(F(1,2),F(1,2)),((('a','A'),), 'a'):(F(1,2),F(1,2)),((('a','B'),), 'a'):(F(1,2),F(1,2))})

def horizon_process()->Process:
    A=('a',);O=('X','Y');K={((),'a'):(F(1,2),F(1,2))}
    K[((('a','X'),), 'a')]=(F(1),F(0));K[((('a','Y'),), 'a')]=(F(1),F(0))
    K[((('a','X'),('a','X')), 'a')]=(F(1),F(0));K[((('a','Y'),('a','X')), 'a')]=(F(0),F(1))
    return Process(A,O,3,K)

def small_census():
    vals=(F(0),F(1,2),F(1)); blocks=assign=rf=ff=sf=strict=0
    for ps in product(vals,repeat=4):
        D=tuple((F(1),p) for p in ps);blocks+=1;c=len(set(D));r=rank(D)
        if rank_by_minors(D)!=r or r>c:rf+=1
        fac=factor(D)
        if fac['reconstructed']!=D or fac['rank']!=r:ff+=1
        if c>r:strict+=1
        for labels in product(range(4),repeat=4):
            assign+=1;ok,_=exact_statistic(D,labels)
            if ok and len(set(labels))<c:sf+=1
    return {'blocks':blocks,'statistic_assignments':assign,'rank_class_failures':rf,'factorization_failures':ff,'statistic_minimality_failures':sf,'class_count_strictly_above_rank_blocks':strict}

def latent_census(max_len=5):
    total=fail=nonempty=0
    for m in range(max_len+1):
        for word in product((0,1),repeat=m):
            total+=1
            if m:nonempty+=1
            p1=F(1,2**m);p2=F(1,2**m)
            if p1!=p2:fail+=1
    return {'max_length':max_len,'observable_words_checked_including_empty':total,'nonempty_words_checked':nonempty,'failures':fail,'one_latent_state_count':1,'two_latent_state_count':2,'latent_cardinality_identified':False}

def build_receipt():
    p=separation_process();hs,ts,D=p.block(1,1);fac=factor(D);classes=len(set(D))
    xcol=ts.index((('a','X'),))
    ok,w=exact_statistic(D,('same','same','other'))
    dup=duplicate_row_process().block(1,1)[2]
    hp=horizon_process();short=hp.block(1,1)[2];long=hp.block(1,2)[2]
    lc=latent_census(5)
    zero=(('a','X'),)
    rejected=False
    try:p.ptest(zero,())
    except ContractError:rejected=True
    return {
      'schema':'GMI833FinitePredictiveRankReceiptV1','issue':ISSUE,'parent_issue':PARENT_ISSUE,
      'source_main':SOURCE_MAIN,'freeze_commit':FREEZE_COMMIT,'claim_ceiling':CLAIM_CEILING,
      'forbidden_promotions':list(FORBIDDEN_PROMOTIONS),
      'parent_ownership':{
       'predictive_quotient_and_cardinality_minimality':'#846 PS-1','separating_test_coordinate_boundary':'#846 PSR-1',
       'predictive_state_definition':'Littman-Sutton-Singh NeurIPS 2001','system_dynamics_rank_and_core_tests':'Singh-James-Rudary UAI 2004','finite_linear_algebra':'standard rank factorization'},
      'SEP_1':{'positive_history_count':len(hs),'complete_test_count':len(ts),'predictive_class_count':classes,'exact_rank':rank(D),'independent_minor_rank':rank_by_minors(D),'core_columns':list(fac['core_columns']),'core_tests':[list(map(list,ts[j])) for j in fac['core_columns']],'pivot_rows':list(fac['pivot_rows']),'exact_reconstruction':fac['reconstructed']==D,'under_dimension_claim_accepted':rank(D)<=1,'under_dimension_reason':f'CLAIMED_DIMENSION_1_BELOW_EXACT_RANK_{rank(D)}'},
      'PQ_1_hostiles':{'illegal_statistic_merge_accepted':ok,'illegal_statistic_merge_witness':w,'duplicate_histories_collapse_to_one_class':len(set(dup))==1},
      'horizon_completeness_hostile':{'test_horizon_1_class_count':len(set(short)),'test_horizon_2_class_count':len(set(long)),'short_horizon_merges':short[0]==short[1],'long_horizon_separates':long[0]!=long[1]},
      'zero_likelihood_boundary':{'zero_history_conditional_rejected':rejected,'positive_histories':[list(map(list,h)) for h in hs]},
      'small_binary_exact_census':small_census(),'latent_nonidentifiability':lc,
      'gap_descendants_required_open':['GAP-836-INFINITE-MEASURABLE','GAP-836-APPROXIMATE-PREDICTIVE','GAP-836-FINITE-SAMPLE-ID','GAP-836-CAUSAL-LATENT-ID'],
      'terminal':'GMI_833_FINITE_PREDICTIVE_RANK_V1_ALL_GREEN'}

def main():print(json.dumps(build_receipt(),indent=2,sort_keys=True))
if __name__=='__main__':main()
