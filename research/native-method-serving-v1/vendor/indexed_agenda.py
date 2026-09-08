"""Knuth/Nederhof positive weighted deduction over ordered ground action records.

Direct implementation from algorithmic principles; no donor implementation copied.
See DONORS.md for inspected implementations and their representation boundaries.
"""
import heapq
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('_common',Path(__file__).with_name('common.py'))
C=importlib.util.module_from_spec(s);s.loader.exec_module(C)
F=C.load('finite_search')
def count(work,key,n=1):work[key]=work.get(key,0)+n
def search(actions,bank,task,work,max_decisions=8):
    if type(max_decisions) is not int or max_decisions<0:raise ValueError('nonnegative integer cutoff')
    formulas=[['|-']+r['tokens'] for r in bank['wff']];lookup={tuple(t):i for i,t in enumerate(formulas)}
    if tuple(task['query']) not in lookup or any(tuple(p) not in lookup for p in task['premises']):
        raise ValueError('BANK_INCOMPLETE: task')
    target=lookup[tuple(task['query'])];supplied={}
    for slot,premise in enumerate(task['premises']):
        supplied.setdefault(lookup[tuple(premise)],{'kind':'premise','slot':slot,'decision_count':0,'output':premise})
    if target in supplied:return {'terminal':'PROVED','decision_count':0,'derivation':supplied[target]}
    def key(i):count(work,'rank_actions_scanned');return F.order(actions[i],formulas)
    order=sorted(range(len(actions)),key=key);ranks={index:rank for rank,index in enumerate(order)}
    incidence=[[] for _ in formulas];remaining=[];sums=[];queue=[];best={};settled={};serial=0
    def push(head,cost,rank,derivation):
        nonlocal serial
        if cost>max_decisions:count(work,'candidate_bound_rejections');return
        if head in settled:count(work,'candidate_settled_rejections');return
        value=(cost,rank)
        if head in best and best[head]<=value:count(work,'candidate_dominance_rejections');return
        best[head]=value
        heapq.heappush(queue,(cost,tuple(formulas[head]),rank,serial,head,derivation));serial+=1
        count(work,'queue_pushes');work['peak_queue_entries']=max(work.get('peak_queue_entries',0),len(queue))
    for head,derivation in supplied.items():push(head,0,-1,derivation)
    for index,a in enumerate(actions):
        count(work,'index_action_records')
        if type(a['query']) is not int or not 0<=a['query']<len(formulas):raise ValueError('action head outside bank')
        if any(type(p) is not int or not 0<=p<len(formulas) for p in a['premises']):raise ValueError('action premise outside bank')
        remaining.append(len(a['premises']));sums.append(1)
        for premise in a['premises']:
            incidence[premise].append(index);count(work,'index_premise_incidences')
        if not a['premises']:
            count(work,'candidate_actions_ready');count(work,a['kind']+'_candidate_actions')
            push(a['query'],1,ranks[index],{'kind':'action','action':a,'parents':[],'decision_count':1,'output':formulas[a['query']]})
    while queue:
        cost,_,rank,_,head,derivation=heapq.heappop(queue);count(work,'queue_pops')
        if head in settled or best[head]!=(cost,rank):count(work,'stale_queue_entries');continue
        settled[head]=derivation;count(work,'settled_facts')
        if head==target:return {'terminal':'PROVED','decision_count':cost,'derivation':derivation}
        for index in incidence[head]:
            count(work,'visited_premise_incidences');remaining[index]-=1;sums[index]+=cost
            if remaining[index]:continue
            a=actions[index];count(work,'candidate_actions_ready');count(work,a['kind']+'_candidate_actions')
            parents=[settled[p] for p in a['premises']];candidate_cost=sums[index]
            if candidate_cost!=1+sum(p['decision_count'] for p in parents):raise ValueError('ordered multiplicity accounting')
            push(a['query'],candidate_cost,ranks[index],{'kind':'action','action':a,'parents':parents,
                'decision_count':candidate_cost,'output':formulas[a['query']]})
    return {'terminal':'NO_PROOF_WITHIN_BOUND','max_decisions':max_decisions,'reached_facts':len(settled)}
