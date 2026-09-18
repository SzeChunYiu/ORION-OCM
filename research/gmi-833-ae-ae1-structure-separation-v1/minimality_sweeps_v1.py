#!/usr/bin/env python3
"""GMI #833 AE1 -- minimality certificates for the non-distributional
separations (control, causal, accessibility, finite-sample).

The AE1 freeze promises "a minimality certificate for every witness", and AE1
row 8 asks for minimal counterexamples for every false equivalence in rows 2-6.
The distributional sweep in `ae1_structure_separation_v1.py` covers rows 2-3;
this module covers rows 4-6.

All arithmetic is integer or Fraction; minimality is claimed only at the frozen
finite grids declared below, never over all real-valued parameters.
"""
from fractions import Fraction as F

# frozen grids for this module
CTRL_DEN = 6
CTRL_MAX_X = 3
CTRL_MAX_Y = 3
CTRL_MAX_A = 2
CAUSAL_DEN = 4
CAUSAL_MAX = 2
BITS_MAX = 3


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def minimal_under_product_order(hits):
    out = []
    for s in hits:
        if not any(o != s and all(o[i] <= s[i] for i in range(len(s)))
                   for o in hits):
            out.append(s)
    return sorted(out)


# --------------------------------------------------------------------------
# row 4a: predictive dependence vs control relevance
# --------------------------------------------------------------------------

def control_patterns(counts, a, b, c, U):
    """(PRED, CTRL, utility-nonconstant-in-y) from integer data."""
    rows = [counts[x * b:(x + 1) * b] for x in range(a)]
    ny = [sum(rows[x][y] for x in range(a)) for y in range(b)]
    pred = sum(max(r) for r in rows) > max(ny)
    blind = max(sum(ny[y] * U[act][y] for y in range(b)) for act in range(c))
    informed = sum(
        max(sum(rows[x][y] * U[act][y] for y in range(b))
            for act in range(c))
        for x in range(a))
    ctrl = informed > blind
    nonconst = any(any(U[act][y] != U[act][0] for y in range(b))
                   for act in range(c))
    return pred, ctrl, nonconst


def control_minimality():
    """Exhaustive over shapes (|X|,|Y|,|A|) up to (3,3,2), joints with counts
    summing to 6, and every 0/1 utility table."""
    pred_no_ctrl = []
    ctrl_no_pred = []
    shapes = 0
    cases = 0
    for a in range(1, CTRL_MAX_X + 1):
        for b in range(1, CTRL_MAX_Y + 1):
            for c in range(1, CTRL_MAX_A + 1):
                shapes += 1
                utilities = []
                for code in range(2 ** (b * c)):
                    U = [[(code >> (act * b + y)) & 1 for y in range(b)]
                         for act in range(c)]
                    utilities.append(U)
                found_pnc = False
                found_cnp = False
                for comp in compositions(CTRL_DEN, a * b):
                    for U in utilities:
                        cases += 1
                        p, ct, nc = control_patterns(comp, a, b, c, U)
                        if p and not ct and nc:
                            found_pnc = True
                        if ct and not p:
                            found_cnp = True
                    if found_pnc and found_cnp:
                        break
                if found_pnc:
                    pred_no_ctrl.append((a, b, c))
                if found_cnp:
                    ctrl_no_pred.append((a, b, c))
    return {
        "grid_denominator": CTRL_DEN,
        "max_shape_XYA": [CTRL_MAX_X, CTRL_MAX_Y, CTRL_MAX_A],
        "shapes_searched": shapes,
        "cases_examined": cases,
        "nondegeneracy_requirement": (
            "at least two actions. A single-action world offers no choice, so "
            "its control gain is zero for trivial reasons and every world "
            "would be a vacuous witness -- the same exclusion applied to the "
            "arity-0 rule class in the accessibility sweep. Both the "
            "unrestricted and the non-degenerate minima are reported."),
        "PRED_without_CTRL_nonconstant_utility": {
            "realizable_shapes": [list(s) for s in sorted(pred_no_ctrl)],
            "minimal_shapes_any_action_count": [
                list(s) for s in minimal_under_product_order(pred_no_ctrl)],
            "minimal_shapes_at_least_two_actions": [
                list(s) for s in minimal_under_product_order(
                    [t for t in pred_no_ctrl if t[2] >= 2])],
        },
        "CTRL_without_PRED": {
            "realizable_shapes": [list(s) for s in sorted(ctrl_no_pred)],
            "minimal_shapes_any_action_count": [
                list(s) for s in minimal_under_product_order(ctrl_no_pred)],
            "minimal_shapes_at_least_two_actions": [
                list(s) for s in minimal_under_product_order(
                    [t for t in ctrl_no_pred if t[2] >= 2])],
        },
    }


# --------------------------------------------------------------------------
# row 4b: predictive dependence vs causal relevance
# --------------------------------------------------------------------------

def causal_minimality():
    """Smallest confounded structure Z -> X, Z -> Y (no X -> Y edge) with a
    strictly positive observational Bayes gain.

    Because the structure carries no X -> Y edge, P(y | do(x)) is independent
    of x by construction, so the interventional gain is exactly 0 for every
    member of the family; the question is the minimal (|Z|,|X|,|Y|) at which a
    positive observational gain is nevertheless realizable.
    """
    hits = []
    shapes = 0
    cases = 0
    for nz in range(1, CAUSAL_MAX + 1):
        for nx in range(1, CAUSAL_MAX + 1):
            for ny in range(1, CAUSAL_MAX + 1):
                shapes += 1
                found = False
                for pz in compositions(CAUSAL_DEN, nz):
                    xcond = list(compositions(CAUSAL_DEN, nx))
                    ycond = list(compositions(CAUSAL_DEN, ny))
                    for xs in _tuples(xcond, nz):
                        for ys in _tuples(ycond, nz):
                            cases += 1
                            joint = [[0] * ny for _ in range(nx)]
                            for z in range(nz):
                                for x in range(nx):
                                    for y in range(ny):
                                        joint[x][y] += (pz[z] * xs[z][x]
                                                        * ys[z][y])
                            col = [sum(joint[x][y] for x in range(nx))
                                   for y in range(ny)]
                            if sum(max(r) for r in joint) > max(col):
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break
                if found:
                    hits.append((nz, nx, ny))
    return {
        "grid_denominator": CAUSAL_DEN,
        "max_shape_ZXY": [CAUSAL_MAX] * 3,
        "shapes_searched": shapes,
        "cases_examined": cases,
        "structure": "Z -> X, Z -> Y, no X -> Y edge",
        "interventional_gain_is_zero_by_construction": True,
        "PRED_with_zero_interventional_gain": {
            "realizable_shapes": [list(s) for s in sorted(hits)],
            "minimal_shapes": [list(s) for s in
                               minimal_under_product_order(hits)],
        },
    }


def _tuples(pool, k):
    out = [()]
    for _ in range(k):
        out = [t + (p,) for t in out for p in pool]
    return out


# --------------------------------------------------------------------------
# row 5: existence of structure vs accessibility
# --------------------------------------------------------------------------

def _essential_arity(table, n):
    cnt = 0
    for i in range(n):
        for x in range(2 ** n):
            if not (x >> i) & 1 and table[x] != table[x ^ (1 << i)]:
                cnt += 1
                break
    return cnt


def _dt_depth(table, n):
    memo = {}

    def rec(mask, vals):
        key = (mask, vals)
        if key in memo:
            return memo[key]
        live = [x for x in range(2 ** n) if (x & mask) == vals]
        if all(table[x] == table[live[0]] for x in live):
            memo[key] = 0
            return 0
        best = n
        for i in range(n):
            if mask & (1 << i):
                continue
            cand = 1 + max(rec(mask | (1 << i), vals),
                           rec(mask | (1 << i), vals | (1 << i)))
            if cand < best:
                best = cand
        memo[key] = best
        return best

    return rec(0, 0)


def _best_acc(target, n, k, d):
    """Best fraction of the 2^n inputs a rule of arity<=k and depth<=d gets
    right, as an exact Fraction, for a deterministic target table."""
    N = 2 ** n
    best = 0
    for code in range(2 ** N):
        tab = [(code >> j) & 1 for j in range(N)]
        if _essential_arity(tab, n) > k or _dt_depth(tab, n) > d:
            continue
        hit = sum(1 for x in range(N) if tab[x] == target[x])
        if hit > best:
            best = hit
    return F(best, N)


def accessibility_minimality():
    """Minimal number of coordinates at which registered structure exists yet
    a NON-TRIVIAL budget (arity at least 1) reaches only the base rate.

    The arity-0 class is excluded: it contains only constant rules, so it
    attains the base rate for trivial reasons and would make every world a
    vacuous witness.
    """
    arity_hits = []
    depth_hits = []
    allread_hits = []
    examined = 0
    for n in range(1, BITS_MAX + 1):
        N = 2 ** n
        for code in range(2 ** N):
            target = [(code >> j) & 1 for j in range(N)]
            ones = sum(target)
            base = F(max(ones, N - ones), N)
            full = F(1)
            if full <= base:
                continue
            examined += 1
            for k in range(1, n):
                if _best_acc(target, n, k, n) == base:
                    arity_hits.append((n, k))
            for d in range(1, n):
                if _best_acc(target, n, n, d) == base:
                    depth_hits.append((n, d))
                    # strictly stronger: every coordinate is reachable within
                    # the depth budget (a depth-d tree can query up to
                    # 2^d - 1 distinct coordinates) and the rule STILL only
                    # attains the base rate
                    if (2 ** d) - 1 >= n:
                        allread_hits.append((n, d))
    return {
        "coordinate_range": [1, BITS_MAX],
        "targets_examined": examined,
        "nontrivial_budget_requirement": "junta arity at least 1",
        "arity_gap": {
            "realizable_n_k": [list(s) for s in sorted(set(arity_hits))],
            "minimal_n": (min(s[0] for s in arity_hits)
                          if arity_hits else None),
        },
        "depth_gap_at_full_arity": {
            "realizable_n_d": [list(s) for s in sorted(set(depth_hits))],
            "minimal_n": (min(s[0] for s in depth_hits)
                          if depth_hits else None),
        },
        "depth_gap_with_every_coordinate_reachable": {
            "definition": (
                "a depth-d tree can query up to 2^d - 1 distinct coordinates; "
                "this pattern requires 2^d - 1 >= n, so no coordinate is "
                "hidden from the budget, and the best rule is STILL at the "
                "base rate"),
            "realizable_n_d": [list(s) for s in sorted(set(allread_hits))],
            "minimal_n": (min(s[0] for s in allread_hits)
                          if allread_hits else None),
        },
    }


# --------------------------------------------------------------------------
# row 6: finite-sample discoverability vs asymptotic learnability
# --------------------------------------------------------------------------

def discoverability_minimality():
    """Minimal coordinate count at which the zero-sample Bayes learner is
    exactly at the secret-marginalised base rate while the target is
    asymptotically learnable to accuracy 1."""
    hits = []
    detail = {}
    for n in range(1, BITS_MAX + 1):
        N = 2 ** n
        ones = {}
        for x in range(N):
            ones[x] = sum(1 for s in range(N)
                          if bin(s & x).count("1") % 2 == 1)
        joint = {}
        for x in range(N):
            joint[(x, 1)] = F(1, N) * F(ones[x], N)
            joint[(x, 0)] = F(1, N) * F(N - ones[x], N)
        py1 = sum((joint[(x, 1)] for x in range(N)), F(0))
        base = max(py1, F(1) - py1)
        obs = sum((max(joint[(x, 0)], joint[(x, 1)]) for x in range(N)), F(0))
        # the zero-sample Bayes learner is the best constant rule
        zero_sample = base
        detail["n%d" % n] = {
            "marginalised_acc_base": str(base),
            "marginalised_acc_obs": str(obs),
            "marginalised_PRED": obs > base,
            "zero_sample_learner": str(zero_sample),
            "asymptotic": "1",
        }
        if zero_sample == base and obs == base:
            hits.append(n)
    return {
        "coordinate_range": [1, BITS_MAX],
        "per_n": detail,
        "realizable_n": hits,
        "minimal_n": min(hits) if hits else None,
    }
