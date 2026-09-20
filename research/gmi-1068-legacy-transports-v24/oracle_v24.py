"""Independent literal multigraph paths, raw profiles, preferences and common plans."""
from fractions import Fraction as F
from itertools import combinations
import json

POLICIES={'C0':(0,0),'C1':(1,1),'ID':(0,1),'NOT':(1,0)}
INITIAL='INITIAL_OR_INHERITED_ORGANIZATION'
OBS='EXTERNAL_OBSERVATION'
ORACLE='ORACLE_ADVICE_OR_TOOL'
COMPUTE='ENDOGENOUS_COMPUTE'


def require(condition,message):
    if not condition:raise ValueError(message)


def subsets(values):
    values=tuple(values)
    return tuple(c for n in range(len(values)+1) for c in combinations(values,n))


def paths(vertices,rows,start,horizon):
    """Every prefix is a history; original absent slot positions are never compressed."""
    result=[]
    def visit(state,edges,actions):
        result.append((state,edges,actions))
        if len(edges)==horizon:return
        for slot,edge in enumerate(rows[vertices.index(state)]):
            if edge is not None:
                action,destination=edge
                visit(destination,edges+((state,slot),),actions+(action,))
    visit(start,(),())
    return tuple(result)


def selected(full):
    best={}
    for terminal,edges,actions in full:
        rank=(len(edges),tuple(slot for _,slot in edges))
        if terminal not in best or rank<best[terminal][0]:best[terminal]=(rank,actions)
    return {terminal:best[terminal][1] for terminal in sorted(best)}


def profile(terminal,actions,provenance,target):
    tags={INITIAL}
    for action in actions:tags.update(provenance[action])
    correct=sum(POLICIES[terminal][i]==POLICIES[target][i] for i in (0,1))
    capability='1/2' if correct==1 else str(correct//2)
    return {'machine':terminal,'capability':{target+'_TASK':capability},
            'resources':{'development_steps':len(actions),'external_observations':int(OBS in tags),
                         'oracle_queries':int(ORACLE in tags)},
            'provenance':sorted(tags),'history':list(actions)}


def profiles(full,provenance,target):
    return tuple((edges,profile(terminal,actions,provenance,target)) for terminal,edges,actions in full)


def strict_json(value):
    if type(value) is dict:
        require(all(type(k) is str for k in value),'JSON keys')
        for item in value.values():strict_json(item)
    elif type(value) is list:
        for item in value:strict_json(item)
    else:require(type(value) in (str,int,bool,type(None)),'raw legacy JSON type')
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def verify_raw(actual,expected):
    require(strict_json(actual)==strict_json(expected),'raw profile field drift')
    return True


def validate_path(vertices,rows,start,edges,terminal,actions):
    state=start;word=[]
    for source,slot in edges:
        require(source==state and type(slot) is int and 0<=slot<len(rows[vertices.index(source)]),'path source/slot')
        edge=rows[vertices.index(source)][slot]
        require(edge is not None,'absent slot')
        action,state=edge;word.append(action)
    require((state,tuple(word))==(terminal,actions),'path erasure')
    return True


def preference(candidates,weights,reachable_only):
    active=tuple((label,vector) for label,vector,viable,reachable in candidates if viable and (reachable or not reachable_only))
    front=tuple(sorted(label for label,v in active if not any(all(x<=y for x,y in zip(w,v)) and any(x<y for x,y in zip(w,v)) for _,w in active)))
    scores={label:sum((x*w for x,w in zip(v,weights)),F(0)) for label,v in active}
    winners=tuple(sorted(label for label,value in scores.items() if all(value<=other for other in scores.values())))
    return {'terminal':'SELECTION_DEFINED' if active else 'NO_VIABLE_MORPHOLOGY','pareto_front':list(front),'scalar_argmin':list(winners)}


def feasible(plan_ids,admitted,defined,losses,threshold):
    return tuple(sorted(label for i,label in enumerate(plan_ids) if admitted[i] and defined[i] and losses[i]<=threshold))


def common(plan_ids,sets,selected):
    return tuple(sorted(label for label in plan_ids if all(label in sets[h] for h in selected)))


def verify_plan_ids(actual,expected):
    require(type(actual) is tuple and all(type(x) is str for x in actual) and actual==expected,'plan identity drift')
    return True


def exact_equal(left,right):
    if type(left) is not type(right):return False
    if type(left) in (tuple,list):return len(left)==len(right) and all(exact_equal(a,b) for a,b in zip(left,right))
    if type(left) is dict:return left.keys()==right.keys() and all(exact_equal(left[k],right[k]) for k in left)
    return left==right


def verify_context(context,decoder,admitted,defined,relation,expected_decoder):
    n=len(admitted)
    expected=(n,len(relation),admitted,defined,tuple(i if e else None for i,e in enumerate(defined)),relation)
    actual=tuple(getattr(context,key) for key in ('n','m','admitted','defined','values','order'))
    require(exact_equal(actual,expected),'context semantic or type drift')
    require(exact_equal(decoder,expected_decoder),'decoder identity/value drift')
    return True
