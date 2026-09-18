#!/usr/bin/env python3
"""Route B oracle for AE5.

Independently written.  It imports nothing from ``ae5_causal_state_audit_v1``:
the joint is built by walking the tree once per word rather than by forward
propagation, dyadic exponents are read off with ``bit_length``, the rank is
computed by fraction-free Bareiss elimination over the integers rather than by
rational Gauss-Jordan, and the description length is counted by a queue walk.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product

LEN = 3
RULES = ("F", 0, 1)


def slots():
    out = [()]
    for n in range(1, LEN):
        for t in product((0, 1), repeat=n):
            out.append(t)
    order = []
    for n in range(LEN):
        for t in product((0, 1), repeat=n):
            order.append(t)
    return tuple(order)


SLOTS = slots()
SLOT_AT = dict((SLOTS[i], i) for i in range(len(SLOTS)))


def word_probability(proc, word):
    """Probability of one full word, by walking the tree for that word alone."""
    p = Fraction(1)
    for i in range(LEN):
        rule = proc[SLOT_AT[tuple(word[:i])]]
        if rule == "F":
            p = p * Fraction(1, 2)
        elif rule != word[i]:
            return Fraction(0)
    return p


def joint(proc):
    out = {}
    for word in product((0, 1), repeat=LEN):
        p = word_probability(proc, word)
        if p:
            out[word] = p
    return out


def prefix_mass(jt, n):
    out = {}
    for w in jt:
        out[w[:n]] = out.get(w[:n], Fraction(0)) + jt[w]
    return out


def future_signature(jt, prefix, horizon):
    n = len(prefix)
    acc = {}
    tot = Fraction(0)
    for w in jt:
        if w[:n] != prefix:
            continue
        acc.setdefault(w[n:n + horizon], Fraction(0))
        acc[w[n:n + horizon]] += jt[w]
        tot += jt[w]
    if tot == 0:
        return None
    return tuple(sorted((k, acc[k] / tot) for k in acc))


def classes(jt, prefix_len, horizon):
    out = {}
    for prefix in sorted(prefix_mass(jt, prefix_len)):
        sig = future_signature(jt, prefix, horizon)
        if sig is None:
            continue
        out.setdefault(sig, []).append(prefix)
    return out


def state_masses(jt, prefix_len, horizon):
    pm = prefix_mass(jt, prefix_len)
    cls = classes(jt, prefix_len, horizon)
    return [sum(pm[p] for p in cls[s]) for s in sorted(cls)]


def dyadic_exp(p):
    """a with p = 2^-a, read off with bit_length; None if not such a power."""
    if p <= 0:
        return None
    if p.numerator != 1:
        return None
    d = p.denominator
    if d & (d - 1):
        return None
    return d.bit_length() - 1


def entropy(masses):
    tot = Fraction(0)
    for m in masses:
        if m == 0:
            continue
        a = dyadic_exp(m)
        if a is None:
            raise ValueError("non-dyadic")
        tot += m * a
    return tot


def block(jt, start, length):
    acc = {}
    for w in jt:
        acc.setdefault(w[start:start + length], Fraction(0))
        acc[w[start:start + length]] += jt[w]
    return list(acc.values())


def excess_entropy(jt, split):
    return (
        entropy(block(jt, 0, split))
        + entropy(block(jt, split, LEN - split))
        - entropy(list(jt.values()))
    )


def bareiss_rank(int_rows):
    """Fraction-free Bareiss elimination; returns the rank over Q."""
    m = [list(r) for r in int_rows]
    rows = len(m)
    cols = len(m[0]) if rows else 0
    prev = 1
    r = 0
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if m[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        for i in range(r + 1, rows):
            for j in range(c + 1, cols):
                m[i][j] = (m[i][j] * m[r][c] - m[i][c] * m[r][j]) // prev
            m[i][c] = 0
        prev = m[r][c]
        r += 1
    return r


def hankel_rank(jt, split):
    prefixes = sorted(set(w[:split] for w in jt))
    suffixes = sorted(set(w[split:] for w in jt))
    den = 1
    for w in jt:
        den = den * jt[w].denominator // _gcd(den, jt[w].denominator)
    rows = []
    for u in prefixes:
        rows.append(
            [int(jt.get(u + v, Fraction(0)) * den) for v in suffixes]
        )
    return bareiss_rank(rows)


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def description_length(proc):
    total = 0
    queue = [()]
    while queue:
        w = queue.pop(0)
        if len(w) >= LEN:
            continue
        rule = proc[SLOT_AT[tuple(w)]]
        total += 1
        if rule == "F":
            queue.append(tuple(w) + (0,))
            queue.append(tuple(w) + (1,))
        else:
            total += 1
            queue.append(tuple(w) + (rule,))
    return total


def epsilon_machine_states(jt):
    out = {}
    for ln in range(LEN):
        pm = prefix_mass(jt, ln)
        for prefix in sorted(pm):
            if pm[prefix] == 0:
                continue
            sig = future_signature(jt, prefix, LEN - ln)
            if sig is None:
                continue
            out.setdefault((LEN - ln, sig), []).append((ln, prefix))
    return out
