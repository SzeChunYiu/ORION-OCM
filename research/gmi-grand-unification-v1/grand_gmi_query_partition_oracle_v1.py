"""Independent syntax census: generate trees before inspecting any obligation."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product


@lru_cache(None)
def shapes(remaining):
    result = [None]
    for i in remaining:
        children = shapes(tuple(j for j in remaining if j != i))
        result.extend((i, a, b) for a, b in product(children, repeat=2))
    return tuple(result)


@lru_cache(None)
def executed_shapes(n, costs):
    result = []
    for shape in shapes(tuple(range(n))):
        leaves, work = [], []
        for x in range(1 << n):
            tree, path, bill, seen = shape, (), F(0), set()
            while tree is not None:
                i, a, b = tree
                if i in seen:
                    raise AssertionError("syntax generator repeated a coordinate")
                seen.add(i)
                bit = (x >> i) & 1
                path += (bit,)
                bill += costs[i]
                tree = b if bit else a
            leaves.append(path)
            work.append(bill)
        result.append((tuple(leaves), tuple(work), shape))
    return tuple(result)


def oracle(table, costs):
    n = len(table).bit_length()-1
    candidates = executed_shapes(n, tuple(map(F, costs)))
    profiles, admitted = set(), 0
    for leaves, work, _ in candidates:
        required, valid = {}, True
        for x, leaf in enumerate(leaves):
            if leaf in required and required[leaf] != table[x]:
                valid = False
                break
            required[leaf] = table[x]
        if valid:
            profiles.add(work)
            admitted += 1
    frontier = set(profiles)
    for v in profiles:
        for u in profiles:
            if u != v and all(u[i] <= v[i] for i in range(len(table))):
                frontier.discard(v)
                break
    return dict(frontier=frozenset(frontier), shapes=len(candidates), admitted=admitted)


def partitions(size):
    """Restricted-growth strings enumerate every partition exactly once."""
    def extend(prefix):
        if len(prefix) == size:
            yield tuple(prefix)
        else:
            for label in range(max(prefix)+2):
                yield from extend(prefix+[label])
    yield from extend([0])
