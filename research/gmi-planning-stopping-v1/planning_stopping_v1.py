"""Exact finite witnesses for planning, goals and the EVC stop rule (I4).

Reuses the 6-world fixture from META-1..4 (WORLD6 0..5, actions {0,1,2},
Gamma6, tests t0/t1 costs 1/2) and composes META-3 EVC as the planning
expansion rule. All values exact Fractions, CPython 3.8 safe.
"""

from fractions import Fraction as F
from itertools import combinations

WORLD6 = tuple(range(6))

GAMMA6 = {
    0: frozenset((0, 1)),
    1: frozenset((0, 1)),
    2: frozenset((0, 2)),
    3: frozenset((0,)),
    4: frozenset((1, 2)),
    5: frozenset((1,)),
}


def _check_set(s):
    s = frozenset(s)
    if not s or not s <= frozenset(WORLD6):
        raise ValueError("nonempty subset of WORLD6 required")
    return s


def outcome_t0(w):
    if type(w) is not int or w not in WORLD6:
        raise ValueError("world must be 0..5")
    return w % 2


def outcome_t1(w):
    if type(w) is not int or w not in WORLD6:
        raise ValueError("world must be 0..5")
    return 0 if w < 4 else 1


TESTS = {"t0": (outcome_t0, F(1)), "t1": (outcome_t1, F(2))}


def common_actions(s):
    s = _check_set(s)
    out = frozenset((0, 1, 2))
    for w in s:
        out &= GAMMA6[w]
    return out


def confidence(a, s):
    if type(a) is not int or a not in (0, 1, 2):
        raise ValueError("action must be 0/1/2")
    s = _check_set(s)
    return F(len([w for w in s if a in GAMMA6[w]]), len(s))


def loss_of(a, w):
    if type(a) is not int or a not in (0, 1, 2):
        raise ValueError("action must be 0/1/2")
    if type(w) is not int or w not in WORLD6:
        raise ValueError("world must be 0..5")
    return F(0) if a in GAMMA6[w] else F(1)


def error_cost(a, s):
    if type(a) is not int or a not in (0, 1, 2):
        raise ValueError("action must be 0/1/2")
    s = _check_set(s)
    return sum(loss_of(a, w) for w in s) / len(s)


def cells(s, test):
    s = _check_set(s)
    if test not in TESTS:
        raise ValueError("unknown test")
    fn, _ = TESTS[test]
    groups = {}
    for w in s:
        groups.setdefault(fn(w), set()).add(w)
    return [frozenset(v) for v in groups.values()]


def evc_worst(a, s, test):
    s = _check_set(s)
    if test not in TESTS:
        raise ValueError("unknown test")
    _, cost = TESTS[test]
    return error_cost(a, s) - (cost + max(error_cost(a, c) for c in cells(s, test)))


def evc_mean(a, s, test):
    s = _check_set(s)
    if test not in TESTS:
        raise ValueError("unknown test")
    _, cost = TESTS[test]
    cs = cells(s, test)
    mean = sum(error_cost(a, c) * len(c) for c in cs) / len(s)
    return error_cost(a, s) - (cost + mean)


def tda_value(s):
    s = _check_set(s)
    if common_actions(s):
        return F(0)
    best = None
    for name, (fn, cost) in TESTS.items():
        groups = {}
        for w in s:
            groups.setdefault(fn(w), set()).add(w)
        if len(groups) < 2:
            continue
        val = cost + max(tda_value(c) for c in groups.values())
        if best is None or val < best[0]:
            best = (val, name)
    if best is None:
        raise ValueError("no splitting test")
    return best[0]


def tda_minimizers(s):
    s = _check_set(s)
    if common_actions(s):
        return []
    opt = tda_value(s)
    out = []
    for name, (fn, cost) in TESTS.items():
        groups = {}
        for w in s:
            groups.setdefault(fn(w), set()).add(w)
        if len(groups) < 2:
            continue
        if cost + max(tda_value(c) for c in groups.values()) == opt:
            out.append(name)
    return out


def max_evc_tests(a, s):
    s = _check_set(s)
    scored = [(evc_worst(a, s, t), t) for t in TESTS]
    top = max(v for v, _ in scored)
    return [t for v, t in scored if v == top]


# --- planning wrappers ---
def formed_goal(s):
    """Max-confidence action(s) and their Omega at S."""
    s = _check_set(s)
    best_conf = max(confidence(a, s) for a in (0, 1, 2))
    leaders = [a for a in (0, 1, 2) if confidence(a, s) == best_conf]
    # Omega_a = worlds where a is adequate
    omegas = {a: frozenset(w for w in WORLD6 if a in GAMMA6[w]) for a in leaders}
    return leaders, omegas, best_conf


def should_expand(a, s, test):
    """META-3 stop rule as planning expansion rule: continue iff EVC>0."""
    return evc_worst(a, s, test) > F(0)


def stop_rule_holds(s):
    """True iff no expansion has positive EVC for the max-conf action."""
    s = _check_set(s)
    leaders, _, _ = formed_goal(s)
    a = leaders[0]
    return all(evc_worst(a, s, t) <= F(0) for t in TESTS)


def is_subgoal(candidate, root=None):
    """Strictly between: 0 < V(candidate) < V(root). If root None, use WORLD6 full set."""
    candidate = _check_set(candidate)
    if root is None:
        root = frozenset(WORLD6)
    else:
        root = _check_set(root)
    vc = tda_value(candidate)
    vr = tda_value(root)
    return F(0) < vc < vr


def all_subsets():
    out = []
    for r in range(1, len(WORLD6) + 1):
        out.extend(frozenset(c) for c in combinations(WORLD6, r))
    return out
