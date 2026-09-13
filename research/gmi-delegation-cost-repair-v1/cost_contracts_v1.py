"""Additive event semantics: external bounds remain explicit premises."""
from collections import Counter
from fractions import Fraction
from typed_program_v1 import require

def ledger(events):
    return dict(sorted(Counter(events).items()))

def preserved_subsequence(parent, child):
    position = 0
    for event in child:
        if position < len(parent) and event == parent[position]: position += 1
    return position == len(parent)

def refinement(parent, child):
    require(preserved_subsequence(parent, child), 'old events were not preserved in order')
    delta = Counter(child)
    delta.subtract(Counter(parent))
    require(all(v >= 0 for v in delta.values()), 'negative residual event count')
    return dict(sorted((k, v) for k, v in delta.items() if v))

def rational(value):
    require(type(value) in (int, Fraction) and type(value) is not bool, 'exact rational bound required')
    return Fraction(value)

def additive_bounds(events, contracts):
    """Each row is a supplied sound per-label interval, NOT automatically certified.

    Absence means [0,infinity). Soundness relative to a real resource requires
    an independent uniform contract proof on the complete declared input domain.
    """
    lower, upper = Fraction(0), Fraction(0)
    for name, count in Counter(events).items():
        lo, hi = contracts.get(name, (0, None))
        lo = rational(lo)
        hi = None if hi is None else rational(hi)
        require(lo >= 0 and (hi is None or hi >= lo), 'invalid nonnegative contract')
        lower += count * lo
        upper = None if upper is None or hi is None else upper + count * hi
    return lower, upper

def python_contract(events):
    """Definitional Python-opcode projection; native work is outside this metric."""
    return {name: ((1, 1) if name.startswith('py:') else (0, 0)) for name in events}

def separation(candidate, comparator, contracts):
    """Strict scalar comparison under supplied uniform sound interval contracts."""
    ca, cb = additive_bounds(candidate, contracts), additive_bounds(comparator, contracts)
    return 'CERTIFIED_STRICTLY_LOWER' if ca[1] is not None and ca[1] < cb[0] else 'UNVERIFIABLE'
