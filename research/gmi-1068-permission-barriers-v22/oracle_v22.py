"""Independent literal traversal and complete intervention enumeration; no core imports."""
from itertools import combinations, product


def subsets(items):
    items=tuple(items)
    return tuple(c for size in range(len(items)+1) for c in combinations(items,size))


def execute(observations,rows,requirements,start,word,enabled=None):
    state=start; required=set(); trace=[('OBS',observations[state])]
    for action in word:
        edge=rows[state][action]
        if edge is None or (enabled is not None and any(x not in enabled for x in requirements[state][action])):
            return tuple(trace+[('ILLEGAL',)]),None
        required.update(requirements[state][action])
        output,cost,state=edge
        trace.extend((('EDGE',output,cost),('OBS',observations[state])))
    return tuple(trace),(state,tuple(sorted(required)))


def survivors(records,enabled):
    return tuple(sorted(i for i,support in records if all(x in enabled for x in support)))


def additions(records,baseline,available):
    candidates=[d for d in subsets(x for x in available if x not in baseline)
                if survivors(records,baseline+d)]
    return tuple(sorted(d for d in candidates if not any(set(c)<set(d) for c in candidates)))


def blockers(records,available):
    candidates=[b for b in subsets(available) if not survivors(records,tuple(x for x in available if x not in b))]
    return tuple(sorted(b for b in candidates if not any(set(c)<set(b) for c in candidates)))


def certificate(records,available,blocked):
    if blocked not in blockers(records,available):return None
    return tuple((b,min(i for i,s in records if set(s)<=set(available) and set(s)&set(blocked)=={b})) for b in sorted(blocked))


def minimal_supports(records):
    supports={tuple(sorted(s)) for _,s in records}
    return tuple((s,tuple(sorted(i for i,t in records if set(t)==set(s)))) for s in sorted(supports)
                 if not any(set(t)<set(s) for t in supports))


def families(q):
    options=subsets(range(q))
    for chosen in subsets(range(len(options))):
        yield tuple((i,options[i]) for i in chosen)


def machines(states,actions,q):
    options=(None,)+tuple((target,support) for target in range(states) for support in subsets(range(q)))
    for chosen in product(options,repeat=states*actions):
        rows=[];requirements=[]
        for s in range(states):
            cells=chosen[s*actions:(s+1)*actions]
            rows.append(tuple(None if x is None else (0,0,x[0]) for x in cells))
            requirements.append(tuple(None if x is None else x[1] for x in cells))
        yield tuple(rows),tuple(requirements)


def context_expected(observations,rows,requirements,histories,p,values,selected,enabled):
    admitted=[];tags=[];image=set()
    for i,(s,w) in enumerate(histories):
        success=execute(observations,rows,requirements,s,w,enabled)[1] is not None
        active=p[i] and i in selected and success
        admitted.append(active)
        tag=('ILLEGAL',None) if not active else ('UNDEFINED',None) if values[i] is None else ('VALUE',values[i])
        tags.append(tag)
        if active and values[i] is not None:image.add(values[i])
    return tuple(admitted),tuple(tags),tuple(sorted(image))


def witnesses(observations,rows,requirements,histories,p,values,selected,target):
    result=[]
    for i,(s,w) in enumerate(histories):
        run=execute(observations,rows,requirements,s,w)[1]
        if run is not None and p[i] and i in selected and values[i] is not None and values[i] in target:
            result.append((i,run[1]))
    return tuple(result)
