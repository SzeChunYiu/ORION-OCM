"""Independent finite relations, semantic orders and positive-length reachability."""
from itertools import product


def preorders(n):
    for bits in product((False,True),repeat=n*n):
        order=tuple(tuple(bits[i*n+j] for j in range(n)) for i in range(n))
        if all(order[i][i] for i in range(n)) and all(
                not(order[i][j] and order[j][k]) or order[i][k]
                for i,j,k in product(range(n),repeat=3)):
            yield order


def properties(source,target,mapping):
    pairs=tuple(product(range(len(source)),repeat=2))
    monotone=all(not source[i][j] or target[mapping[i]][mapping[j]] for i,j in pairs)
    reflecting=all(not target[mapping[i]][mapping[j]] or source[i][j] for i,j in pairs)
    return monotone,reflecting,len(set(mapping))==len(mapping)


def assignments(carrier,n):
    for statuses in product(range(len(carrier)+2),repeat=n):
        p=tuple(s!=0 for s in statuses)
        values=tuple(None if s<2 else carrier[s-2] for s in statuses)
        yield p,values


def observe(p,values,h):
    return ('ILLEGAL',None) if not p[h] else (('UNDEFINED',None) if values[h] is None else ('VALUE',values[h]))


def powerset(n):
    for bits in product((False,True),repeat=n):
        yield frozenset(i for i,keep in enumerate(bits) if keep)


def viability_cases():
    for n in range(4):
        for bits in product((False,True),repeat=n*n):
            relation=tuple(tuple(bits[i*n+j] for j in range(n)) for i in range(n))
            for safe in powerset(n):
                yield relation,safe


def cycle_survivors(relation,safe):
    """Positive-length transitive closure, then reachability to an actual cycle."""
    n=len(relation)
    reach=[[i in safe and j in safe and relation[i][j] for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j]=reach[i][j] or (reach[i][k] and reach[k][j])
    cyclic={i for i in safe if reach[i][i]}
    return frozenset(i for i in safe if i in cyclic or any(reach[i][j] for j in cyclic))


def postfixed(relation,safe,candidate):
    return candidate<=safe and all(any(relation[i][j] for j in candidate) for i in candidate)


def safe_candidates(safe):
    ordered=tuple(sorted(safe))
    for bits in product((False,True),repeat=len(ordered)):
        yield frozenset(i for i,keep in zip(ordered,bits) if keep)


def product_order(left,right,reverse=False):
    return all(a>=b if reverse else a<=b for a,b in zip(left,right))
