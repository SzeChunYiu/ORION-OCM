"""Static adequate table reuse; independently executed admission schedules."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
from prefix_v1 import exact


def subsets(items):
    items=tuple(items)
    return (frozenset(s) for k in range(len(items)+1) for s in combinations(items,k))


def partition(rows):
    rows=tuple(tuple(row) for row in rows)
    if not rows or any(len(row)!=len(rows[0]) for row in rows):
        raise ValueError('nonempty equal-width complete response rows')
    if any(type(x) is not int or x not in (0,1) for row in rows for x in row):
        raise ValueError('Boolean response register')
    distinct=[];route=[]
    for row in rows:
        if row not in distinct:distinct.append(row)
        route.append(distinct.index(row))
    return tuple(distinct),tuple(route)


def gain(r,C,S,U):
    if type(r) is not int or r<1:raise ValueError('positive occurrence count')
    C,S,U=map(exact,(C,S,U))
    return (r-1)*(C-U)-S


def execute(rows,stream,selected,C,S,U,route_price=1,delivery_price=1):
    C,S,U,rp,dp=map(exact,(C,S,U,route_price,delivery_price))
    rows=tuple(tuple(row) for row in rows);partition(rows)
    stream=tuple(stream);selected=frozenset(selected)
    if not selected<=set(range(len(rows))) or any(type(i) is not int or i not in range(len(rows)) for i in stream):
        raise ValueError('unknown class')
    cache={};events=[];answers=[];cost=F(0);peak=0;counts=Counter()
    for key in stream:
        counts['route']+=1;cost+=rp
        if key in cache:
            body=cache[key];charge=U;kind='recall'
        else:
            body=tuple(rows[key]);charge=C;kind='materialize'
            if key in selected:
                cache[key]=body;charge+=S;counts['install']+=1
        if body!=rows[key]:raise ValueError('inadequate reuse')
        counts[kind]+=1;counts['delivered_bits']+=len(body)
        peak=max(peak,sum(map(len,cache.values())))
        answers.append(body);cost+=charge+len(body)*dp
        events.append(dict(key=key,kind=kind,body=body,reconstruction=charge,
                           route=rp,delivery=len(body)*dp))
    return dict(cost=cost,events=events,answers=answers,counts=dict(counts),
                peak_retained_row_bits=peak)


def choose(stream,C,S,U,sizes=None,capacity=None):
    counts=Counter(stream);keys=tuple(counts)
    if sizes is None: sizes={k:1 for k in keys}
    if any(type(sizes[k]) is not int or sizes[k]<1 for k in keys):
        raise ValueError('positive retained sizes')
    if capacity is not None and (type(capacity) is not int or capacity<0):
        raise ValueError('nonnegative integer capacity')
    feasible=[s for s in subsets(keys) if capacity is None or sum(sizes[k] for k in s)<=capacity]
    gains={k:gain(counts[k],C,S,U) for k in keys}
    best=max(sum((gains[k] for k in s),F(0)) for s in feasible)
    winners=[s for s in feasible if sum((gains[k] for k in s),F(0))==best]
    return winners,best
