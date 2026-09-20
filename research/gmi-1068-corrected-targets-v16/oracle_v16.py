"""Independent typed-path, bit-count and exact linear calibration semantics."""
from fractions import Fraction as Q
from itertools import product

COEFFICIENTS = tuple(map(Q, (-1,0))) + (Q(1,3),Q(1,2),Q(2,3),Q(1),Q(2))
PROFILE_VALUES = tuple(map(Q,(-1,0,1,2)))


def graph_cases():
    universe = tuple(product(range(2), repeat=2))
    for present in product((False,True), repeat=4):
        edges = tuple(e for e,keep in zip(universe,present) if keep)
        for mask in product((False,True),repeat=len(edges)):
            yield (2,edges),mask


def paths(graph, maximum):
    n,edges = graph
    for start in range(n):
        pending = [(start,())]
        while pending:
            endpoint,word = pending.pop()
            yield (start,word),endpoint
            if len(word)<maximum:
                pending.extend((target,word+(i,)) for i,(source,target) in enumerate(edges)
                               if source==endpoint)


def path_allowed(mask,history):
    return all(mask[i] for i in history[1])


def words(maximum):
    for length in range(maximum+1):
        yield from product(range(4),repeat=length)


def c4_product(word):
    return sum(word) % 4


def v4_product(word):
    low = sum(label % 2 for label in word) % 2
    high = sum(label // 2 for label in word) % 2
    return 2*high+low


def parity(word):
    return sum(label % 2 for label in word) % 2


def coefficients():
    for n in range(4):
        yield from product(COEFFICIENTS,repeat=n)


def profiles(n):
    return tuple(product(PROFILE_VALUES,repeat=n))


def score(coefficients,profile):
    answer = Q(0)
    for index in range(len(profile)):
        answer += coefficients[index]*profile[index]
    return answer


def ordered_pairs(n):
    choices = tuple((a,b) for a,b in product(PROFILE_VALUES,repeat=2) if a<=b)
    for coordinates in product(choices,repeat=n):
        yield tuple(a for a,_ in coordinates),tuple(b for _,b in coordinates)
