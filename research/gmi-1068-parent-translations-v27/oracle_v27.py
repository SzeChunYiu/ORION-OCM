"""Independent finite sets, walks, and trajectory products; no production imports."""
from fractions import Fraction as F
from itertools import product
from functools import lru_cache
from math import prod


def certify(actual, expected):
    if type(actual) is not type(expected):
        raise ValueError("representation type differs")
    if isinstance(expected, tuple):
        if len(actual) != len(expected):
            raise ValueError("representation length differs")
        for a, e in zip(actual, expected):
            certify(a, e)
    elif actual != expected:
        raise ValueError("semantic value differs")


@lru_cache(None)
def systems(n, labels=1):
    edges = tuple(product(range(n), range(labels), range(n)))
    return tuple((n, labels, tuple(e for i, e in enumerate(edges) if mask >> i & 1))
                 for mask in range(1 << len(edges)))


def clauses(source, target, mapping):
    left = [{(a, mapping[t]) for s, a, t in source[2] if s == x}
            for x in range(source[0])]
    right = [{(a, t) for s, a, t in target[2] if s == mapping[x]}
             for x in range(source[0])]
    return (all(a <= b for a, b in zip(left, right)),
            all(b <= a for a, b in zip(left, right)))


@lru_cache(None)
def paths(system, limit=3):
    n, labels, edges = system
    result = []
    for length in range(limit + 1):
        for start in range(n):
            for suffix in product(range(n), repeat=length):
                states = (start,) + suffix
                for word in product(range(labels), repeat=length):
                    triples = tuple((states[i], a, states[i + 1]) for i, a in enumerate(word))
                    if all(e in edges for e in triples):
                        result.append((start, tuple(edges.index(e) for e in triples)))
    return tuple(result)


def endpoint(system, path):
    return system[2][path[1][-1]][2] if path[1] else path[0]


def path_labels(system, path):
    return tuple(system[2][e][1] for e in path[1])


def mapped(source, target, mapping, path):
    edges = tuple(target[2].index((mapping[source[2][e][0]], source[2][e][1],
                                  mapping[source[2][e][2]])) for e in path[1])
    return mapping[path[0]], edges


def lifts(source, target, mapping, start, target_path):
    return tuple(sorted((p for p in paths(source, len(target_path[1]))
                         if p[0] == start and len(p[1]) == len(target_path[1])
                         and mapped(source, target, mapping, p) == target_path), key=lambda p: p[1]))


def bisimilar(left, right, first=0, second=0):
    relation = set(product(range(left[0]), range(right[0])))
    while True:
        nxt = {(s, t) for s, t in relation
               if all(any(v == t and b == a and (u, w) in relation for v, b, w in right[2])
                      for x, a, u in left[2] if x == s)
               and all(any(v == s and b == a and (w, u) in relation for v, b, w in left[2])
                       for x, a, u in right[2] if x == t)}
        if nxt == relation:
            return (first, second) in relation
        relation = nxt


@lru_cache(None)
def events():
    values = (F(0), F(1, 2), F(1))
    out = []
    for n, m in product(range(3), repeat=2):
        for flat in product(values, repeat=n * m):
            rows = tuple(tuple(flat[i * m:(i + 1) * m]) for i in range(n))
            if all(sum(row) <= 1 for row in rows):
                out.append((n, m, rows))
    return tuple(out)


def trajectory(chain):
    n, m = chain[0][0], chain[-1][1]
    intermediates = tuple(x[1] for x in chain[:-1])
    return tuple(tuple(sum((prod((e[2][states[k]][states[k + 1]]
                                     for k, e in enumerate(chain)), start=F(1))
                           for middle in product(*(range(d) for d in intermediates))
                           for states in ((i,) + middle + (j,),)), F(0))
                       for j in range(m)) for i in range(n))


@lru_cache(None)
def tests():
    values = (F(0), F(1, 2), F(1))
    out = []
    for n, m in product(range(3), repeat=2):
        for flat in product(values, repeat=2 * n * m):
            rows = tuple(tuple(tuple(flat[o * n * m + i * m:o * n * m + (i + 1) * m])
                               for i in range(n)) for o in range(2))
            if all(sum(rows[0][i]) + sum(rows[1][i]) == 1 for i in range(n)):
                out.append((n, m, tuple((o, (n, m, rows[o])) for o in range(2))))
    return tuple(out)


def aggregate(test):
    return tuple(tuple(sum((e[2][i][j] for _, e in test[2]), F(0))
                       for j in range(test[1])) for i in range(test[0]))


def relation_product(first, second):
    return tuple(sorted({(x, z) for x, y in first for yy, z in second if y == yy}))


def domain(relation):
    return tuple(sorted({a for a, _ in relation}))


def image(relation):
    return tuple(sorted({b for _, b in relation}))


def relations():
    cells = tuple(product(range(2), repeat=2))
    return tuple(tuple(c for i, c in enumerate(cells) if mask >> i & 1) for mask in range(16))
