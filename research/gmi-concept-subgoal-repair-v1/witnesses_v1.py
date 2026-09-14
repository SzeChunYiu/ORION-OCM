"""Independent complete-parse/subset census and decisive finite controls."""
from fractions import Fraction as F
from itertools import product
from collections import Counter
from prefix_v1 import solve,complete_parses
from concept_v1 import partition,gain,choose,execute,subsets


def prefix_checks(original):
    cases=paths=positions=0
    for n in range(1,4):
        for letters in product('ab',repeat=n):
            target=''.join(letters)
            for values in product((None,0,1,3),repeat=4):
                skills={s:p for s,p in zip(('a','b','ab','ba'),values) if p is not None}
                for c,d in product((0,1),(0,2)):
                    row=solve(target,skills,c,d);cases+=1
                    for i in range(n+1):
                        costs=complete_parses(target,skills,c,d,i);paths+=len(costs);positions+=1
                        if row['values'][i]!=min(costs):raise ValueError('complete parse optimum')
                    if not set(row['local'])<=set(row['entries']):raise ValueError('entry implication')
    negatives={t:solve(t,s) for t,s in [('abc',{'ab':1,'bc':1}),('abcd',{'ab':1,'bcd':1})]}
    if negatives['abc']['entries']!=[0,1] or negatives['abc']['local']!=[1]:raise ValueError('overlap control')
    positive=solve('abcabc',{'abc':1})
    if positive['entries']!=positive['local'] or positive['local']!=[0,3]:raise ValueError('strict positive')
    old=original['records']['STAGE_SUBGOAL_WITNESS_V1.json'];rows=[];local=[];entries=[];disc=[]
    for t in old['targets']:
        answer=solve(t,{s:1 for s in old['skills']})
        for i in range(len(t)):
            rows.append(dict(target=t,pos=i,prefix=t[:i],suffix=t[i:],ctg_bare=answer['bare'][i],
                             ctg_with_skills=answer['values'][i],drop=answer['delta'][i]))
            if i in answer['local']:local.append([t,i])
            if i in answer['entries']:entries.append([t,i])
            if answer['delta'][i]>0:disc.append([t,i])
    if rows!=old['states']:raise ValueError('old complete row reconstruction')
    loc=original['records']['STAGE_SUBGOAL_LOCAL_V1.json']
    actual=dict(schema=loc['schema'],n_disc=len(disc),n_entry=len(entries),n_local=len(local),
                entry_not_local=sorted(x for x in entries if x not in local),
                local_not_entry=sorted(x for x in local if x not in entries),local_equals_entry=local==entries)
    if actual!=loc:raise ValueError('old local record reconstruction')
    return dict(cases=cases,complete_parse_executions=paths,suffixes=positions,
                overlap_counterexamples=negatives,positive=positive,original_local_reconstruction=actual,
                all_emitted_targets_equal=True)


def concept_checks():
    cases=schedules=0
    for n in range(1,5):
        for stream in product((0,1),repeat=n):
            for C,S,U in product((0,1,3),repeat=3):
                for capacity in (0,1,2):
                    winners,g=choose(stream,C,S,U,capacity=capacity);costs={}
                    for chosen in subsets(set(stream)):
                        if len(chosen)>capacity:continue
                        row=execute(((0,1),(1,0)),stream,chosen,C,S,U)
                        if row['answers']!=[(0,1) if k==0 else (1,0) for k in stream]:raise ValueError('adequacy')
                        costs[chosen]=row['cost'];schedules+=1
                    best=min(costs.values());exact_winners={s for s,v in costs.items() if v==best}
                    if set(winners)!=exact_winners:raise ValueError('independent subset schedule')
                    cases+=1
    functions=[lambda h:h&1,lambda h:(h>>1)&1,lambda h:(h&1)^((h>>1)&1),
               lambda h:(h>>2)&1,lambda h:(h>>3)&1,lambda h:((h>>2)&1)&((h>>3)&1)]
    raw_rows=[tuple(f(h) for h in range(16)) for f in functions]
    # The exact source occurrence order, supplied as an explicit finite register.
    stream=(0,1,2,0,2,0,1,2,0,2,2,0,3,4,5)
    rows,route=partition([raw_rows[i] for i in stream]);selected=frozenset(i for i,r in Counter(route).items() if gain(r,5,3,1)>0)
    runs={name:execute(rows,route,s,5,3,1) for name,s in
          [('flat',frozenset()),('triggered',selected),('all',frozenset(range(len(rows))))]}
    work={name:sum(e['reconstruction'] for e in r['events']) for name,r in runs.items()}
    if work!={'flat':75,'triggered':48,'all':57}:raise ValueError('retained original costs')
    bad=execute(((0,),),(0,0),{0},1,1,2,0,0)
    if bad['cost']!=4 or gain(2,1,1,2)!=-2:raise ValueError('unguarded sign countercontrol')
    # Same charged acquired past; present artifact may be installed or discarded.
    futures=[dict(further=k,keep=F(3)+k,discard=F(5)*k) for k in (0,2)]
    return dict(cases=cases,complete_subset_executions=schedules,source_runs=runs,
                original_reconstruction=work,unguarded_negative=bad,same_past_futures=futures,
                supplied_response_bits=len(raw_rows)*16,registered_occurrences=len(stream),
                source_class_count=len(rows),derived_concepts_or_meanings=False)


def future_control():
    # Present answers coincide, but a registered update changes only state0.
    outputs=(0,0,1);update=(2,1,2)
    before=[outputs[i] for i in (0,1)];after=[outputs[update[i]] for i in (0,1)]
    if before!=[0,0] or after!=[1,0]:raise ValueError('future interface witness')
    return dict(current=before,after_update_query=after,full_future_merge_legal=False)
