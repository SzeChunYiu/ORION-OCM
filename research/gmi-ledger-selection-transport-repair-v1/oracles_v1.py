"""Independent finite path/table/assignment oracles; no certificate calls."""
from itertools import product
from fractions import Fraction as F

def terminal_paths(values,edges,start):
    result=[]
    def visit(path):
        i=path[-1]
        nexts=[j for j in edges[i] if values[i]>values[j]]
        if not nexts:
            result.append(tuple(path))
        for j in nexts:
            if j in path:
                raise ValueError("a strict path cannot cycle")
            visit(path+[j])
    visit([start])
    return tuple(result)

def assignment_cover(source,target,epsilon):
    """Enumerate actual target->source witness functions."""
    sk=tuple(source); tk=tuple(target)
    witnesses=[]
    for chosen in product(sk,repeat=len(tk)):
        if all(source[i]-target[j]<=epsilon for i,j in zip(chosen,tk)):
            witnesses.append(tuple(zip(chosen,tk)))
    return tuple(witnesses)

def table_winners(task,tables,costs):
    possible=[]
    for i in tables:
        violations=[(x,tables[i][x]) for x in task if tables[i][x] not in task[x]]
        if not violations:
            possible.append((F(costs[i]),i))
    if not possible:
        return ()
    possible.sort()
    return tuple(i for c,i in possible if c==possible[0][0])

def threshold_worlds(passes,failures,unknown):
    n=passes+failures+unknown
    decisions=[]
    for outcomes in product((False,True),repeat=unknown):
        decisions.append(F(passes+sum(outcomes),n)>=F(2,3))
    return ("GUARANTEED_FRACTION_PASS" if all(decisions) else
            "FRACTION_FAIL" if not any(decisions) else "UNRESOLVED")
