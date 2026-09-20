"""Independent subset covers and pair-BFS semantics, never production refinement."""
from collections import deque
from functools import lru_cache
from itertools import product


@lru_cache(None)
def preorders(n):
    result=[]
    for flat in product((False,True),repeat=n*n):
        r=tuple(tuple(flat[i*n+j] for j in range(n)) for i in range(n))
        if all(r[i][i] for i in range(n)) and all(not(r[i][j] and r[j][k]) or r[i][k]
                for i,j,k in product(range(n),repeat=3)):
            result.append(r)
    return tuple(result)


def subsets(values):
    return tuple(tuple(x for i,x in enumerate(values) if mask & (1<<i)) for mask in range(1<<len(values)))


def cofinal(r,a,c):
    return set(c)<=set(a) and all(any(r[x][y] for y in c) for x in a)


def downset(r,a):
    return tuple(x for x in range(len(r)) if any(r[x][y] for y in a))


@lru_cache(None)
def minimum_covers(r,a):
    candidates=tuple(c for c in subsets(a) if cofinal(r,a,c))
    size=min(map(len,candidates))
    return tuple(c for c in candidates if len(c)==size)


def image(mapping,a):
    return tuple(sorted({mapping[x] for x in a if mapping[x] is not None}))


def guarded(source,target,mapping):
    return all(not source[x][y] or mapping[x] is None or
               (mapping[y] is not None and target[mapping[x]][mapping[y]])
               for x,y in product(range(len(source)),repeat=2))


def assignments(n,m):
    return product((None,)+tuple(range(m)),repeat=n)


def contexts():
    for n,m in product(range(4),repeat=2):
        for r in preorders(m):
            for p in product((False,True),repeat=n):
                for values in assignments(n,m):
                    yield n,m,r,p,values


def observation(p,values,h):
    if not p[h]:return ('ILLEGAL',None)
    if values[h] is None:return ('UNDEFINED',None)
    return ('VALUE',values[h])


def attained(p,values,histories):
    return tuple(sorted({values[h] for h in histories if p[h] and values[h] is not None}))


def witness(base,transitions,x,y):
    if not base[x][y]:return ()
    pending=deque([(x,y,())]);seen={(x,y)}
    while pending:
        left,right,word=pending.popleft()
        for action,u in enumerate(transitions[left]):
            if u is None:continue
            v=transitions[right][action]
            extension=word+(action,)
            if v is None or not base[u][v]:return extension
            if (u,v) not in seen:
                seen.add((u,v));pending.append((u,v,extension))
    return None


def run(transitions,state,word):
    for action in word:
        state=transitions[state][action]
        if state is None:return None
    return state


def nondeterministic_language(transitions,start,depth):
    frontier={(start,())};language={()}
    for _ in range(depth):
        next_frontier=set()
        for state,word in frontier:
            for action,destinations in enumerate(transitions[state]):
                for destination in destinations:
                    next_frontier.add((destination,word+(action,)))
                    language.add(word+(action,))
        frontier=next_frontier
    return language
