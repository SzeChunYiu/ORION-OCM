"""Exact finite witnesses for CAU-5 (checklist item 13).

W4a/W4b: the P(Y|X) vs P(Y|do(X)) separator has no universal sign.
W5A/W5B: identical rung-1 (observational) and rung-2 (interventional) laws,
yet different rung-3 (counterfactual PN) values.
W1 pair: identical observational law with different do-targets, so any
observational-law-only discovery procedure returns identical output.

All probabilities are exact Fractions. No sampling, no estimation.
CPython 3.8 compatible (runs the off-Mac witness hosts).
"""

from fractions import Fraction as F

HALF = F(1, 2)


def _check_bit(v, name):
    if type(v) is not int or v not in (0, 1):
        raise ValueError(name + " must be 0 or 1")


def w4a():
    """Confounded exaggeration: P(Y=1|X=1)=3/4, P(Y=1|do(X=1))=1/2."""
    obs = {}
    for u, pu in ((0, HALF), (1, HALF)):
        for b, pb in ((0, F(3, 4)), (1, F(1, 4))):
            key = (u ^ b, u)
            obs[key] = obs.get(key, F(0)) + pu * pb
    cond = obs[(1, 1)] / (obs[(1, 0)] + obs[(1, 1)])
    return obs, cond, HALF


def w4b():
    """Confounded prevention: P(Y=1|X=1)=0, P(Y=1|do(X=1))=1/2."""
    return {(0, 1): HALF, (1, 0): HALF}, F(0), HALF


UNITS = (0, 1, 2, 3, 4, 5)
UPROB = F(1, 6)

RA = {0: (0, 0), 1: (0, 0), 2: (1, 1), 3: (0, 1), 4: (0, 0), 5: (0, 0)}
RB = {0: (0, 0), 1: (0, 0), 2: (0, 1), 3: (0, 1), 4: (1, 0), 5: (0, 0)}


def _x_of(u):
    return 1 if u >= 2 else 0


def _check_table(r):
    if set(r) != set(UNITS):
        raise ValueError("response table must cover units 0..5")
    for pair in r.values():
        if (len(pair) != 2
                or any(type(v) is not int or v not in (0, 1) for v in pair)):
            raise ValueError("binary response pair required")


def observed_w5(r):
    """Rung-1 law: only (X(u), r_u(X(u))) pairs occur."""
    _check_table(r)
    obs = {}
    for u in UNITS:
        key = (_x_of(u), r[u][_x_of(u)])
        obs[key] = obs.get(key, F(0)) + UPROB
    return obs


def do_w5(r, x):
    """Rung-2 law: surgery on X keeps the uniform root law."""
    _check_bit(x, "assignment")
    _check_table(r)
    return sum(UPROB for u in UNITS if r[u][x] == 1)


def pn_w5(r):
    """Rung-3 PN: P(Y_0 = 0 | X = 1, Y = 1)."""
    _check_table(r)
    cond = [u for u in UNITS if _x_of(u) == 1 and r[u][1] == 1]
    mass = len(cond) * UPROB
    if not mass:
        raise ValueError("conditioning event has zero mass")
    return sum(UPROB for u in cond if r[u][0] == 0) / mass


def rung2_blind_midpoint(do0, do1):
    """Sample rung-2-blind estimator: midpoint of the two do-laws."""
    return (do0 + do1) / 2


def w1(world):
    """CAU-1 pair, structurally evaluated: same obs law, do-targets 1/2 vs 1."""
    if type(world) is not int or world not in (0, 1):
        raise ValueError("unknown witness")
    obs = {}
    for u, pu in ((0, HALF), (1, HALF)):
        x = u
        y = u if world == 0 else x
        obs[(x, y)] = obs.get((x, y), F(0)) + pu
    return obs, (HALF if world == 0 else F(1))


def skeleton_w1(obs):
    """Toy discovery skeleton: keep X--Y iff dependent under the obs law."""
    px = sum(p for (x, _y), p in obs.items() if x == 1)
    py = sum(p for (_x, y), p in obs.items() if y == 1)
    p11 = obs.get((1, 1), F(0))
    if p11 != px * py:
        return frozenset((("X", "Y"),))
    return frozenset()
