"""Exact finite witnesses for TOM-1-3 (checklist item 16).

TOM-1: copycat vs contrarian opponents, identical round 1, opposite optimal
round-2 replies; no joint optimum without an opponent-type bit.
TOM-2: finite beauty-contest belief ladder with exact closure depth.
TOM-3: stag-hunt team, regret-insufficiency, exact reliability-probe value.

All values are exact Fractions. No sampling, no estimation. CPython 3.8 safe.
"""

from fractions import Fraction as F

C, D = 0, 1


# --- TOM-1: opponent-type forcing -------------------------------------------

def opponent_first_move(opponent):
    """Round-1 move of each opponent type: both open D by construction."""
    if opponent not in ("copycat", "contrarian"):
        raise ValueError("admitted opponents are copycat/contrarian")
    return D

def tom1_payoff(a1, f, opponent):
    """Two-round match game. f maps own round-1 action to round-2 action."""
    if a1 not in (0, 1) or opponent not in ("copycat", "contrarian"):
        raise ValueError("admitted actions are 0/1, opponents copycat/contrarian")
    if len(f) != 2 or any(v not in (0, 1) for v in f):
        raise ValueError("reply function must map {0,1} to {0,1}")
    o1 = D
    o2 = a1 if opponent == "copycat" else 1 - a1
    return (1 if a1 == o1 else 0) + (1 if f[a1] == o2 else 0)


def tom1_all_policies():
    """All 8 effective deterministic policies (a1, reply pair)."""
    return [(a1, (f0, f1))
            for a1 in (0, 1) for f0 in (0, 1) for f1 in (0, 1)]


def tom1_best_vs(opponent):
    return max(tom1_payoff(a1, f, opponent) for a1, f in tom1_all_policies())


def tom1_best_joint():
    """Best worst-opponent payoff of one fixed policy."""
    return max(min(tom1_payoff(a1, f, "copycat"),
                   tom1_payoff(a1, f, "contrarian"))
               for a1, f in tom1_all_policies())


# --- TOM-2: recursive belief ladder ------------------------------------------

def beauty_br(m):
    """Best reply to opponent pick m on {0..5} under -|n - 2m/3|, ties down."""
    if type(m) is not int or not 0 <= m <= 5:
        raise ValueError("pick must be in 0..5")
    target = F(2 * m, 3)
    return min(range(6), key=lambda n: (abs(F(n) - target), n))


def beauty_score(n, m):
    beauty_br(m)
    beauty_br(n)
    return -abs(F(n) - F(2 * m, 3))


def beauty_ladder(anchor=5, depth=5):
    if type(anchor) is not int or not 0 <= anchor <= 5:
        raise ValueError("pick must be in 0..5")
    level = [anchor]
    for _ in range(depth):
        level.append(beauty_br(level[-1]))
    return level


# --- TOM-3: partner reliability ----------------------------------------------

TEAM_LOSS = {(0, 0): F(0), (0, 1): F(3), (1, 0): F(1), (1, 1): F(2)}


def _check_action(a, name="action"):
    if type(a) is not int or a not in (0, 1):
        raise ValueError(name + " must be 0 (C) or 1 (D)")


def unilateral_regret(profile, player):
    """Loss(profile) - loss(unilateral deviation), agent-1 loss matrix view.

    Symmetric team game: agent-2 losses mirror agent-1's across the diagonal.
    """
    a1, a2 = profile
    _check_action(a1)
    _check_action(a2)
    if player == 1:
        base = TEAM_LOSS[(a1, a2)]
        return base - TEAM_LOSS[(1 - a1, a2)]
    if player == 2:
        base = TEAM_LOSS[(a2, a1)]
        return base - TEAM_LOSS[(1 - a2, a1)]
    raise ValueError("player must be 1 or 2")


def is_nash(profile):
    return unilateral_regret(profile, 1) <= 0 and unilateral_regret(profile, 2) <= 0


def minimax_without_signal():
    """Worst-case team loss per own action; returns (action, worst loss)."""
    options = [(a, max(TEAM_LOSS[(a, t)] for t in (0, 1))) for a in (0, 1)]
    return min(options, key=lambda kv: (kv[1], kv[0]))


def signal_branch_loss(reliable):
    """Team loss playing C iff the probe says reliable (before probe cost)."""
    if type(reliable) is not bool:
        raise ValueError("reliability flag required")
    return TEAM_LOSS[(0, 0)] if reliable else TEAM_LOSS[(1, 1)]
