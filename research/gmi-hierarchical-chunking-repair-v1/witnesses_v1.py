"""Decisive exact controls, not empirical hierarchy measurements."""
from fractions import Fraction as F
from itertools import product
from hierarchy_v1 import Register,solve
from policy_oracle_v1 import enumerate_executions
from parsing_v1 import parse,all_parses
from event_executor_v1 import replay_events


def hierarchy_witness():
    r=Register(('a',),(101,), (('a',),(0,)*10),(1,1),(100,100),(0,0),(1,))
    runs={name:solve(r,(1,1,1),allowed) for name,allowed in
          (('fresh',()),('lower_only',(0,)),('both',(0,1)))}
    if [runs[x]['cost'] for x in runs] != [3060,3032,1233]:
        raise ValueError('complete lifecycle countermodel failed')
    if len({x['output'] for x in runs.values()})!=1:raise ValueError('trace mismatch')
    counts={name:{kind:sum(e[0]==kind for e in run['events'])
                  for kind in ('primitive','expand','invoke','retain')} for name,run in runs.items()}
    if counts['both']['retain']!=2 or counts['both']['primitive']!=1:
        raise ValueError('first acquisition missing')
    # Exactly nine retained-child calls before the upper artifact is admitted.
    events=runs['both']['events'];end=next(i for i,e in enumerate(events) if e[:2]==('retain',1))
    if sum(e[:2]==('invoke',0) for e in events[:end])!=9:raise ValueError('no actual child calls')
    executed={name:replay_events(r,(1,1,1),allowed,runs[name]['events'])
              for name,allowed in (('fresh',()),('lower_only',(0,)),('both',(0,1)))}
    if any(executed[name]['total']!=run['cost'] for name,run in runs.items()):
        raise ValueError('independent materialized executor disagrees')
    return dict(runs=runs,materialized_execution=executed,events_by_category=counts,first_gain=28,second_gain=1799,
                invocation_contract='self-contained compiled trace; all call work included',
                admission_price_per_artifact=dict(compile=F(1,3),check=F(1,3),index_store=F(1,3)),
                primitive_delivery_price=1,common_delivery=30,native_calls=0)


def parsing_controls():
    p={x:1 for x in 'abcde'};chunks={'abc':1,'ab':1,'cde':1}
    exact=parse('abcde',p,chunks);all_choices=all_parses('abcde',p,chunks)
    if exact['cost']!=2 or min(c for c,_ in all_choices)!=2:raise ValueError('parse revival')
    overlap=all_parses('aaa',{'a':1},{'aa':1})
    maxcalls=max(tokens.count('aa') for _,tokens in overlap)
    if maxcalls!=1:raise ValueError('overlap double-counted')
    return dict(greedy_countermodel=exact,complete_parses=len(all_choices),
                overlapping_raw_count=2,maximum_realized_calls=maxcalls)


def policy_census():
    cases=executions=0
    for width in (1,2):
        for c,u0,u1,s0,s1 in product((1,3),(0,2),(0,2),(0,2),(0,2)):
            reg=Register(('a',),(c,), (('a',),(0,)*width),(s0,s1),(u0,u1),(0,0),(2,))
            for h in (1,2):
                for allowed in ((),(0,),(0,1)):
                    all_runs=enumerate_executions(reg,(1,)*h,allowed)
                    oracle={}
                    for cost,mask,out,_ in all_runs:
                        if out!='a'*(width*h):raise ValueError('independent output failed')
                        oracle[mask]=min(cost,oracle.get(mask,cost))
                    got=solve(reg,(1,)*h,allowed)
                    if got['final_costs']!=oracle:raise ValueError('full mask/profile mismatch')
                    executions+=len(all_runs);cases+=1
    return dict(complete_register_class_cases=cases,complete_executions=executions,
                allowed_classes=[[],[0],[0,1]],widths=[1,2],horizons=[1,2],primitive_delivery_price=2)


def parsing_census():
    cases=executions=0
    for n in range(6):
        for bits in product('ab',repeat=n):
            text=''.join(bits)
            for mask in range(16):
                chunks={p:1 for i,p in enumerate(('aa','ab','ba','bb')) if mask & (1<<i)}
                all_choices=all_parses(text,{'a':1,'b':2},chunks)
                got=parse(text,{'a':1,'b':2},chunks)
                if got['cost']!=min(c for c,_ in all_choices):raise ValueError('parse oracle mismatch')
                cases+=1;executions+=len(all_choices)
    return dict(word_dictionary_cases=cases,complete_parses=executions)
