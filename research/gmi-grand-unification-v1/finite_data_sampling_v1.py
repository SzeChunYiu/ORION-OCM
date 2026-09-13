"""Fixed-size finite-alphabet confidence; no floating-point confidence claims."""
from fractions import Fraction as F
from itertools import product
from math import factorial
from finite_data_model_v1 import rational, tv


def row_confidence_upper(alphabets, samples, epsilon, terms=40):
    alphabets = tuple(alphabets)
    if any(type(x) is not int for x in (*alphabets, samples, terms)):
        raise ValueError("integer register required")
    if any(k < 1 for k in alphabets) or samples < 1 or terms < 0:
        raise ValueError("invalid sampling register")
    epsilon = rational(epsilon, upper=1)
    prefactor = sum((1 << k)-2 for k in alphabets)
    if not prefactor or epsilon == 1:
        return F(0)
    x = 2*samples*epsilon*epsilon
    term = total = F(1)
    for j in range(1, terms+1):
        term *= x/j
        total += term
    return min(F(1), prefactor/total)


def confidence_upper(rows, alphabet, samples, epsilon, terms=40):
    if type(rows) is not int or rows < 0 or type(alphabet) is not int or alphabet < 1:
        raise ValueError("invalid row or alphabet count")
    return row_confidence_upper((alphabet,)*rows, samples, epsilon, terms)


def empirical_register(action_counts, supports, known_rows, records, samples):
    """Validate finite call custody, not physical iidness, support truth or row access."""
    n = len(action_counts)
    if n < 1 or type(samples) is not int or samples < 1:
        raise ValueError("positive fixed N and finite state register required")
    if any(type(a) is not int or a < 0 for a in action_counts):
        raise ValueError("invalid action counts")
    legal = {(s, a) for s, count in enumerate(action_counts) for a in range(count)}
    if set(supports) & set(known_rows) or set(supports) | set(known_rows) != legal:
        raise ValueError("every row must be sampled or independently known")
    for support in supports.values():
        if not support or len(set(support)) != len(support) or any(z not in range(n) for z in support):
            raise ValueError("invalid supplied support alphabet")
    counts = {row: [0]*n for row in supports}
    seen = set()
    for s, a, draw, outcome in records:
        key = (s, a)
        if key not in supports or type(draw) is not int or draw not in range(samples):
            raise ValueError("unregistered row or draw")
        if (s, a, draw) in seen or outcome not in supports[key]:
            raise ValueError("reused draw or outcome outside supplied support")
        seen.add((s, a, draw))
        counts[key][outcome] += 1
    if len(seen) != samples*len(supports):
        raise ValueError("incomplete fixed sampling register")
    rows = []
    for s, size in enumerate(action_counts):
        row = []
        for a in range(size):
            p = tuple(F(c, samples) for c in counts[(s, a)]) if (s, a) in supports else tuple(
                rational(v, upper=1) for v in known_rows[(s, a)])
            if len(p) != n or sum(p) != 1:
                raise ValueError("invalid known probability row")
            row.append(p)
        rows.append(tuple(row))
    return tuple(rows), dict(recorded_draws=len(seen), estimated_count_entries=n*len(supports))


def compositions(total, width):
    if width == 1:
        yield (total,)
    else:
        for first in range(total+1):
            for rest in compositions(total-first, width-1):
                yield (first,)+rest


def count_law(distribution, samples):
    distribution = tuple(rational(p, upper=1) for p in distribution)
    if sum(distribution) != 1 or samples < 1:
        raise ValueError("iid row and positive fixed N required")
    answer = {}
    for counts in compositions(samples, len(distribution)):
        weight = F(factorial(samples))
        for count, probability in zip(counts, distribution):
            weight *= probability**count/factorial(count)
        answer[counts] = weight
    return answer


def simultaneous_failure(distributions, samples, epsilon):
    laws = [count_law(row, samples) for row in distributions]
    answer = F(0)
    for outcome in product(*(tuple(law.items()) for law in laws)):
        weight = F(1)
        for _, probability in outcome:
            weight *= probability
        if any(tv(row, tuple(F(c, samples) for c in outcome[i][0])) > epsilon
               for i, row in enumerate(distributions)):
            answer += weight
    return answer
