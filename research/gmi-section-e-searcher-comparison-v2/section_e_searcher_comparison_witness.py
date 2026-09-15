#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path

N=5
TARGET=21
BIT_PERM=(2,4,1,0,3)
TRUTH_TOUCH_CAP=320
VERIFY_EXAMPLES=32
STRICT_TERMINAL='STRICT_ELITIST_PLATEAU'
MISSPEC_TERMINAL='REPRESENTATION_MISSPECIFIED_NO_EXACT_AFFINE_TARGET'


def all_inputs(): return tuple(itertools.product((0,1), repeat=N))

def eval_mask(mask,x):
    y=0
    for i in range(N):
        if mask&(1<<i): y ^= x[i]
    return y

def target_y(mask=TARGET): return tuple(eval_mask(mask,x) for x in all_inputs())
def singleton_y(): return tuple(int(x==(1,0,1,0,1)) for x in all_inputs())

def discrete_error(mask, ys): return sum(eval_mask(mask,x)!=y for x,y in zip(all_inputs(),ys))

def random_parent():
    ranks=tuple(range(1,33))
    return {
      'target_rank_support':[1,32],
      'success_prob_at_10':str(Fraction(10,32)),
      'expected_rank':str(sum(Fraction(r,32) for r in ranks)),
      'expected_truth_example_touches':str(VERIFY_EXAMPLES*sum(Fraction(r,32) for r in ranks)),
      'reporting_at_cap':{
        'truth_example_touches':320,
        'proposal_or_mutation_attempts':10,
        'unique_discrete_candidates_verified':10,
        'arithmetic_update_ops':0,
        'success_probability_or_exact_success':str(Fraction(5,16)),
        'terminal':'BUDGETED_RANDOM_SEARCH_DISTRIBUTION'
      }
    }

def one_neighbors(mask):
    for i in range(N): yield mask^(1<<i)

def strict_evolution(target=TARGET, proposals=10):
    ys=target_y(target); current=0; cache={current:discrete_error(current,ys)}
    attempts=0
    for i in range(proposals):
        bit=i%N
        cand=current^(1<<bit); attempts+=1
        if cand not in cache: cache[cand]=discrete_error(cand,ys)
        if cache[cand] < cache[current]: current=cand
        if current==target: break
    return {
      'truth_example_touches':VERIFY_EXAMPLES*len(cache),
      'proposal_or_mutation_attempts':attempts,
      'unique_discrete_candidates_verified':len(cache),
      'arithmetic_update_ops':0,
      'success_probability_or_exact_success': current==target,
      'terminal':None if current==target else STRICT_TERMINAL,
      'current':current,
      'cache_errors':{str(k):v for k,v in sorted(cache.items())},
    }

def neutral_drift_exact(target=TARGET,T=5):
    total=N**T; hits=0; unique_sum=0; proposal_sum=0
    for choices in itertools.product(range(N), repeat=T):
        state=0; visited={0}; props=0; hit=False
        for bit in choices:
            props+=1; state ^= 1<<bit; visited.add(state)
            if state==target: hit=True; break
        hits += int(hit); unique_sum += len(visited); proposal_sum += props
    return {
      'horizon':T,
      'success_probability':str(Fraction(hits,total)),
      'expected_unique_discrete_candidates_verified':str(Fraction(unique_sum,total)),
      'expected_truth_example_touches':str(Fraction(VERIFY_EXAMPLES*unique_sum,total)),
      'expected_proposal_or_mutation_attempts':str(Fraction(proposal_sum,total)),
      'arithmetic_update_ops':0,
      'terminal':'STOCHASTIC_NEUTRAL_DRIFT_DISTRIBUTION',
      'paths_enumerated':total,
    }

def neutral_hit_dp(target=TARGET,T=10):
    dist={0:Fraction(1)}; hit=Fraction(0)
    for _ in range(T):
        nd={}
        for state,p in dist.items():
            for bit in range(N):
                nxt=state^(1<<bit); q=p/Fraction(N)
                if nxt==target: hit+=q
                else: nd[nxt]=nd.get(nxt,Fraction(0))+q
        dist=nd
    return hit

class Counter:
    def __init__(self): self.ops=0
    def add(self,a,b): self.ops+=1; return a+b
    def sub(self,a,b): self.ops+=1; return a-b
    def mul(self,a,b): self.ops+=1; return a*b
    def div(self,a,b): self.ops+=1; return a/b

def relaxed_loss(z, ys, count_ops=True):
    c=Counter(); total=Fraction(0)
    for x,y in zip(all_inputs(),ys):
        terms=[]
        for i in range(N):
            a=c.mul(Fraction(2),z[i]); b=c.mul(a,Fraction(x[i])); terms.append(c.sub(Fraction(1),b))
        prod=Fraction(1)
        for t in terms: prod=c.mul(prod,t)
        p=c.div(c.sub(Fraction(1),prod),Fraction(2))
        e=c.sub(p,Fraction(y)); sq=c.mul(e,e); contrib=c.div(sq,Fraction(32)); total=c.add(total,contrib)
    if count_ops: return total,c.ops
    return total

def relaxed_loss_grad(z, ys):
    c=Counter(); total=Fraction(0); g=[Fraction(0)]*N
    for x,y in zip(all_inputs(),ys):
        terms=[]
        for i in range(N):
            a=c.mul(Fraction(2),z[i]); b=c.mul(a,Fraction(x[i])); terms.append(c.sub(Fraction(1),b))
        prod=Fraction(1)
        for t in terms: prod=c.mul(prod,t)
        p=c.div(c.sub(Fraction(1),prod),Fraction(2))
        e=c.sub(p,Fraction(y)); sq=c.mul(e,e); contrib=c.div(sq,Fraction(32)); total=c.add(total,contrib)
        for i in range(N):
            q=Fraction(x[i])
            for j in range(N):
                if j!=i: q=c.mul(q,terms[j])
            u=c.mul(Fraction(2),e); u=c.mul(u,q); u=c.div(u,Fraction(32)); g[i]=c.add(g[i],u)
    return total,g,c.ops

def rounded_mask(z): return sum((1<<i) for i,v in enumerate(z) if v>=Fraction(1,2))

def ablation_nas(target=TARGET):
    ys=target_y(target); z=[Fraction(1,2)]*N; selected=[]; losses={}; arithmetic=0
    for i in range(N):
        z0=z.copy(); z1=z.copy(); z0[i]=0; z1[i]=1
        l0,o0=relaxed_loss(z0,ys); l1,o1=relaxed_loss(z1,ys); arithmetic += o0+o1
        selected.append(0 if l0<l1 else 1)
        losses[str(i)]={'z0':str(l0),'z1':str(l1),'selected':selected[-1]}
    mask=sum((1<<i) for i,v in enumerate(selected) if v)
    err=discrete_error(mask,ys)
    return {
      'endpoint_losses':losses,'hard_mask':mask,'exact_error':err,
      'truth_example_touches':352,'proposal_or_mutation_attempts':10,
      'unique_discrete_candidates_verified':1,'arithmetic_update_ops':arithmetic,
      'success_probability_or_exact_success':err==0,'within_primary_touch_cap':352<=TRUTH_TOUCH_CAP,
      'terminal':None if err==0 else 'HARD_EXACT_VERIFIER_REJECTED'
    }

def darts(target=TARGET, singleton=False):
    ys=singleton_y() if singleton else target_y(target); z=[Fraction(1,2)]*N
    L,g,ops=relaxed_loss_grad(z,ys)
    zp=[]
    c=Counter()
    for zi,gi in zip(z,g): zp.append(c.sub(zi,c.mul(Fraction(8),gi)))
    ops += c.ops
    mask=rounded_mask(zp); err=discrete_error(mask,ys)
    exact_representable=any(discrete_error(m,ys)==0 for m in range(32))
    terminal=None if err==0 else (MISSPEC_TERMINAL if not exact_representable else 'HARD_EXACT_VERIFIER_REJECTED')
    return {
      'initial_loss':str(L),'gradient':[str(x) for x in g],'post_step':[str(x) for x in zp],
      'hard_mask':mask,'exact_error':err,'grammar_has_exact_target':exact_representable,
      'truth_example_touches':64,'proposal_or_mutation_attempts':5,'unique_discrete_candidates_verified':1,
      'arithmetic_update_ops':ops,'success_probability_or_exact_success':err==0,
      'within_primary_touch_cap':64<=TRUTH_TOUCH_CAP,'terminal':terminal
    }

def remint_target(mask=TARGET):
    inv={old:new for new,old in enumerate(BIT_PERM)}
    support=[i for i in range(N) if mask&(1<<i)]; ns=sorted(inv[i] for i in support)
    return sum(1<<i for i in ns),ns

def build_results():
    ys=target_y(); profile={m:discrete_error(m,ys) for m in range(32)}
    rand=random_parent(); strict=strict_evolution(); neutral5=neutral_drift_exact(T=5); neutral10=neutral_hit_dp(T=10)
    nas=ablation_nas(); grad=darts(); neg=darts(singleton=True)
    rem,rs=remint_target(); rem_profile={m:discrete_error(m,target_y(rem)) for m in range(32)}
    rem_strict=strict_evolution(rem); rem_neutral5=neutral_drift_exact(rem,5); rem_neutral10=neutral_hit_dp(rem,10); rem_nas=ablation_nas(rem); rem_grad=darts(rem)
    assertions={
      'E2_01_discrete_plateau':profile[TARGET]==0 and all(v==16 for m,v in profile.items() if m!=TARGET),
      'E2_02_random_exact_distribution':rand['success_prob_at_10']=='5/16' and rand['expected_rank']=='33/2' and rand['expected_truth_example_touches']=='528',
      'E2_03_strict_evolution_plateau':strict['terminal']==STRICT_TERMINAL and strict['success_probability_or_exact_success'] is False and strict['truth_example_touches']==192,
      'E2_04_neutral5_probability':neutral5['success_probability']=='12/125' and neutral5['paths_enumerated']==3125,
      'E2_05_neutral10_probability':neutral10==Fraction(72696,390625),
      'E2_06_nas_endpoint_losses':all((row['z1']=='15/64' and row['z0']=='17/64') if int(i) in (0,2,4) else (row['z0']=='15/64' and row['z1']=='17/64') for i,row in nas['endpoint_losses'].items()),
      'E2_07_nas_recovers_over_budget':nas['hard_mask']==21 and nas['exact_error']==0 and nas['arithmetic_update_ops']==8320 and not nas['within_primary_touch_cap'],
      'E2_08_darts_exact_gradient':grad['initial_loss']=='31/128' and grad['gradient']==['-1/32','1/32','-1/32','1/32','-1/32'],
      'E2_09_darts_recovers_and_charged':grad['post_step']==['3/4','1/4','3/4','1/4','3/4'] and grad['hard_mask']==21 and grad['exact_error']==0 and grad['truth_example_touches']==64 and grad['arithmetic_update_ops']==2122,
      'E2_10_common_budget_ordering':rand['reporting_at_cap']['success_probability_or_exact_success']=='5/16' and strict['success_probability_or_exact_success'] is False and nas['within_primary_touch_cap'] is False and grad['within_primary_touch_cap'] is True,
      'E2_11_singleton_negative':not neg['grammar_has_exact_target'] and neg['terminal']==MISSPEC_TERMINAL and neg['success_probability_or_exact_success'] is False,
      'E2_12_remint_target':rem==11 and rs==[0,1,3],
      'E2_13_remint_plateau':rem_profile[rem]==0 and all(v==16 for m,v in rem_profile.items() if m!=rem),
      'E2_14_remint_search_classes':rem_strict['terminal']==STRICT_TERMINAL and rem_neutral5['success_probability']=='12/125' and rem_neutral10==Fraction(72696,390625),
      'E2_15_remint_nas_darts':rem_nas['hard_mask']==11 and rem_nas['exact_error']==0 and rem_grad['hard_mask']==11 and rem_grad['exact_error']==0,
    }
    return {
      'authority':{'issue':715,'freeze_commit':'773bebb5b7851c72a0a80e4ff22381406d9cac99','accounting_freeze_commit':'d437442367b7314a8ef453c0c1d4630e86b579c4','claim_ceiling':['FINITE_EXACT_SAME_WORLD_PARENT_SEARCHER_COMPARISON_E2','PARENT_OWNED_RANDOM_EVOLUTION_CGP_NAS_DARTS_SEARCH','NO_UNIVERSAL_SEARCHER_DOMINANCE_OR_REAL_SCALE_NAS_CLAIM']},
      'world':{'target_mask':TARGET,'target_support':[0,2,4],'touch_cap':TRUTH_TOUCH_CAP,'non_target_error':16},
      'random':rand,'strict_evolution':strict,'neutral_drift_5':neutral5,'neutral_drift_10_hit_probability':str(neutral10),
      'nas_ablation':nas,'darts':grad,'singleton_negative':neg,
      'remint':{'permutation':list(BIT_PERM),'target_mask':rem,'target_support':rs,'strict_evolution':rem_strict,'neutral_drift_5':rem_neutral5,'neutral_drift_10_hit_probability':str(rem_neutral10),'nas_ablation':rem_nas,'darts':rem_grad},
      'assertions':assertions,'all_frozen_predictions_pass':all(assertions.values())
    }

def receipt(r): return r

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=Path(__file__).with_name('RESULT_E2.json')); a=ap.parse_args()
    r=build_results(); a.output.write_text(json.dumps(receipt(r),indent=2,sort_keys=True)+'\n')
    print(json.dumps({'pass':r['all_frozen_predictions_pass'],'random':r['random']['reporting_at_cap'],'strict':{k:r['strict_evolution'][k] for k in ('truth_example_touches','proposal_or_mutation_attempts','success_probability_or_exact_success','terminal')},'neutral5':r['neutral_drift_5'],'nas':{k:r['nas_ablation'][k] for k in ('truth_example_touches','arithmetic_update_ops','hard_mask','within_primary_touch_cap')},'darts':{k:r['darts'][k] for k in ('truth_example_touches','arithmetic_update_ops','hard_mask','within_primary_touch_cap')},'negative':{k:r['singleton_negative'][k] for k in ('hard_mask','exact_error','grammar_has_exact_target','terminal')},'assertions':r['assertions']},indent=2,sort_keys=True))
    raise SystemExit(0 if r['all_frozen_predictions_pass'] else 1)
if __name__=='__main__': main()
