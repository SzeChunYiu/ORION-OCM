"""Exact finite witnesses for META-1-4 (item 14 / 602-I6).

8-world priced problem: worlds 0..7, actions {0,1,2}, adequate-action sets
Gamma, unit failure losses, two tests with exact costs. 6-world subproblem (worlds 0..5) for the EVC/TDA coincidence sweep.

All values are exact Fractions. No sampling, no estimation. CPython 3.8 safe.
"""

from fractions import Fraction as F
from itertools import combinations

WORLD8 = tuple(range(8))
WORLD6 = tuple(range(6))

GAMMA8 = {
    0: frozenset((0, 1)),
    1: frozenset((0, 1)),
    2: frozenset((0, 2)),
    3: frozenset((0,)),
    4: frozenset((1, 2)),
    5: frozenset((1,)),
    6: frozenset((2,)),
    7: frozenset((0, 1, 2)),
}

# Unit failure loss: 1 per inadequate emission, uniformly over actions/worlds.
# Then EC(a,S) = 1 - conf(a,S) exactly. This is a declared indifference premise
# (uniform loss), stated openly; a priced-loss variant would weight by LOSS, but
# the uniform case makes the confidence/error duality exact, which is the point.
def loss_of(a, w):
    if type(a) is not int or a not in (0, 1, 2):
        raise ValueError("action must be 0/1/2")
    if type(w) is not int or w not in WORLD8:
        raise ValueError("world must be 0..7")
    return F(0) if a in GAMMA8[w] else F(1)

# Two tests: t0 splits even/odd worlds, t1 splits low/high worlds.
def outcome_t0(w):
    if type(w) is not int or w not in WORLD8:
        raise ValueError("world must be 0..7")
    return w % 2


def outcome_t1(w):
    if type(w) is not int or w not in WORLD8:
        raise ValueError("world must be 0..7")
    return 0 if w < 4 else 1


TESTS8 = {"t0": (outcome_t0, F(1)), "t1": (outcome_t1, F(2))}


def _check_set(s, universe=WORLD8):
    s = frozenset(s)
    if not s or not s <= frozenset(universe):
        raise ValueError("nonempty candidate subset required")
    return s


def common_actions(s):
    """C(S): actions adequate in every surviving world."""
    s = _check_set(s)
    out = frozenset((0, 1, 2))
    for w in s:
        out &= GAMMA8[w]
    return out


def confidence(a, s):
    """conf(a,S): fraction of surviving worlds where a is adequate."""
    if type(a) is not int or a not in (0, 1, 2):
        raise ValueError("action must be 0/1/2")
    s = _check_set(s)
    return F(len([w for w in s if a in GAMMA8[w]]), len(s))


def error_cost(a, s):
    """EC(a,S): uniform-mean failure loss of emitting a now (= 1 - conf)."""
    if type(a) is not int or a not in (0, 1, 2):
        raise ValueError("action must be 0/1/2")
    s = _check_set(s)
    return sum(loss_of(a, w) for w in s) / len(s)


def cells(s, test):
    """Outcome cells of a test on S."""
    s = _check_set(s)
    if test not in TESTS8:
        raise ValueError("unknown test")
    fn, _ = TESTS8[test]
    groups = {}
    for w in s:
        groups.setdefault(fn(w), set()).add(w)
    return [frozenset(v) for v in groups.values()]


def evc_worst(a, s, test):
    """Worst-case expected value of cognition for test before emitting a."""
    s = _check_set(s)
    if test not in TESTS8:
        raise ValueError("unknown test")
    _, cost = TESTS8[test]
    return error_cost(a, s) - (cost + max(error_cost(a, c) for c in cells(s, test)))


def evc_mean(a, s, test):
    """Mean-form EVC under declared indifference over outcome cells."""
    s = _check_set(s)
    if test not in TESTS8:
        raise ValueError("unknown test")
    _, cost = TESTS8[test]
    cs = cells(s, test)
    mean = sum(error_cost(a, c) * len(c) for c in cs) / len(s)
    return error_cost(a, s) - (cost + mean)


def tda_value(s):
    """TDA-1 optimal worst-case remaining test cost (uniform test costs apply)."""
    s = _check_set(s)
    if common_actions(s):
        return F(0)
    best = None
    for name, (fn, cost) in TESTS8.items():
        groups = {}
        for w in s:
            groups.setdefault(fn(w), set()).add(w)
        if len(groups) < 2:
            continue
        val = cost + max(tda_value(c) for c in groups.values())
        if best is None or val < best[0]:
            best = (val, name)
    if best is None:
        raise ValueError("no splitting test: TDA value is infinite")
    return best[0]


def tda_minimizers(s):
    """Names of tests attaining the TDA-1 optimum on S."""
    s = _check_set(s)
    if common_actions(s):
        return []
    opt = tda_value(s)
    out = []
    for name, (fn, cost) in TESTS8.items():
        groups = {}
        for w in s:
            groups.setdefault(fn(w), set()).add(w)
        if len(groups) < 2:
            continue
        if cost + max(tda_value(c) for c in groups.values()) == opt:
            out.append(name)
    return out


def max_evc_tests(a, s):
    """Tests attaining the max worst-case EVC on S (empty C(S) scope)."""
    s = _check_set(s)
    scored = [(evc_worst(a, s, t), t) for t in TESTS8]
    top = max(v for v, _ in scored)
    return [t for v, t in scored if v == top]


# --- META-4: finite strategy register ---
def _worst_leaf_ec(s):
    """Worst-leaf min-EC under a TDA-optimal policy tree from S."""
    s = _check_set(s, WORLD6)
    if common_actions(s):
        return F(0)
    name = tda_minimizers(s)[0]
    fn, _ = TESTS8[name]
    groups = {}
    for w in s:
        groups.setdefault(fn(w), set()).add(w)
    out = F(0)
    for g in groups.values():
        g = frozenset(g)
        leaf = min(error_cost(a, g) for a in (0, 1, 2)) if common_actions(g) else _worst_leaf_ec(g)
        out = max(out, leaf)
    return out


def strategy_value(name, s):
    """Worst-case total (tests + execution + terminal EC) of a strategy on S.

    cautious: run TDA-optimal tests to termination (cost V(S)), then emit best.
    bold: emit max-confidence action now (cost EC only).
    cheap_first: take t0 iff it splits, else emit; then finish TDA-optimally.
    Execution fees are zero (declared): the tradeoff is test cost vs error
    cost structurally, not via fees (nonzero fees beg the question — verified
    during construction: any fee above the EC gap makes bold win everywhere).
    """
    s = _check_set(s, WORLD6)
    if name not in ("cautious", "bold", "cheap_first"):
        raise ValueError("unknown strategy")
    exec_fee = {"cautious": F(0), "bold": F(0), "cheap_first": F(0)}[name]
    best_ec = min(error_cost(a, s) for a in (0, 1, 2))
    if name == "bold":
        return best_ec
    if name == "cautious":
        # testing ends at leaves; terminal EC = worst-leaf min-EC, via the
        # TDA-optimal tree (leaves of the minimizing test, recursed).
        return tda_value(s) + exec_fee + _worst_leaf_ec(s)
    groups = {}
    for w in s:
        groups.setdefault(outcome_t0(w), set()).add(w)
    if len(groups) < 2:
        return exec_fee + best_ec
    _, t0cost = TESTS8["t0"]
    return t0cost + max(tda_value(frozenset(g)) for g in groups.values()) + exec_fee


def best_strategies(s):
    """Strategies attaining the minimum strategy value on S."""
    s = _check_set(s, WORLD6)
    scored = [(strategy_value(k, s), k)
              for k in ("cautious", "bold", "cheap_first")]
    top = min(v for v, _ in scored)
    return [k for v, k in scored if v == top]


def all_subsets(universe):
    out = []
    for r in range(1, len(universe) + 1):
        out.extend(frozenset(c) for c in combinations(universe, r))
    return out
