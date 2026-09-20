"""Independent flat finite experiments; these books are not universal machines."""
from fractions import Fraction
from itertools import combinations, product


def words(depth):
    return tuple(''.join(bits) for n in range(depth+1) for bits in product('01', repeat=n))


def prefix_domains(depth):
    candidates = words(depth)
    for mask in range(1 << len(candidates)):
        domain = tuple(w for i,w in enumerate(candidates) if mask & (1 << i))
        if all(not a.startswith(b) and not b.startswith(a) for a,b in combinations(domain,2)):
            yield domain


def books(depth):
    for domain in prefix_domains(depth):
        for values in product((0,1),repeat=len(domain)):
            yield tuple(zip(domain,values))


def decode(book,program):
    for word,value in book:
        if program == word:
            return value
    return None


def wrapper_decode(book,target,padding,program):
    if program == '0':
        return target
    consumed = 0
    for symbol in program:
        if consumed == padding:
            break
        if symbol != '1':
            return None
        consumed += 1
    if consumed != padding:
        return None
    return decode(book,program[consumed:])


def lengths(book):
    found = {}
    for program,value in book:
        found[value] = min(found.get(value,len(program)),len(program))
    return found


def output_weights(book):
    return {value:Fraction(1,2**size) for value,size in lengths(book).items()}


def inner(weights,profile):
    return sum((w*x for w,x in zip(weights,profile)),Fraction(0))


def simplex(n,denominator=4):
    return tuple(tuple(Fraction(x,denominator) for x in counts)
                 for counts in product(range(denominator+1),repeat=n) if sum(counts)==denominator)


def profiles(n):
    return tuple(product((Fraction(0),Fraction(1,2),Fraction(1)),repeat=n))


def families(weights):
    return tuple(tuple(w for i,w in enumerate(weights) if mask & (1<<i))
                 for mask in range(1,1<<len(weights)))


def lower(family,profile):
    return min(inner(weight,profile) for weight in family)


def conditional(weight,indices):
    mass = sum((weight[i] for i in indices),Fraction(0))
    return tuple(weight[i]/mass for i in indices)


def preorders(n):
    for bits in product((False,True),repeat=n*n):
        relation = tuple(tuple(bits[i*n+j] for j in range(n)) for i in range(n))
        if all(relation[i][i] for i in range(n)) and all(
                not(relation[i][j] and relation[j][k]) or relation[i][k]
                for i in range(n) for j in range(n) for k in range(n)):
            yield relation


def resource_signature(relation,state):
    return tuple(int(relation[state][target]) for target in range(len(relation)))
