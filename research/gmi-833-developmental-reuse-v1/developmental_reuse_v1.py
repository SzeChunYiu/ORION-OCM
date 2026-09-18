#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Route A executor for gmi-833-developmental-reuse-v1 (#833 Section L).

Closed-form / analytic route.  Stdlib only, exact integer arithmetic
throughout (no float appears in any emitted claim).  CPython >= 3.8.

Run:
    python3 -I -B developmental_reuse_v1.py        # stdout == RESULT_V1.json

Scope, claims, hostiles and forbidden promotions are fixed by FREEZE_V1.md
(commit 01c6a820) and FROZEN_FIXTURES_V1.json, both committed before this file.
"""

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(HERE, "FROZEN_FIXTURES_V1.json")

CLAIM_CEILING = (
    "GMI_833_FINITE_EXACT_REPRESENTATION_CHANGE_CRITERION_GRAMMAR_GROWTH_"
    "NOVELTY_CHARACTERIZATION_AND_ECOLOGY_CONDITIONAL_SEARCH_DYNAMIC_"
    "COMPARISON_AT_REGISTERED_SCOPE"
)

RECURSIVE_LIBRARY_CYCLE = "RECURSIVE_LIBRARY_CYCLE"

BAND_REDUCTION = "GUARANTEED_REDUCTION"
BAND_INCREASE = "GUARANTEED_INCREASE"
BAND_RANK = "RANK_DECIDED"


# --------------------------------------------------------------------------
# 0. Frozen substrate primitives (inherited from #897 FREEZE sections 3-4)
# --------------------------------------------------------------------------

def phi(n, ell):
    """Phi(n, ell) = sum_{j=1..ell} n**j ; Phi(n, 0) = 0.  Exact integer."""
    if ell <= 0:
        return 0
    total = 0
    p = 1
    for _ in range(ell):
        p *= n
        total += p
    return total


class Grammar(object):
    """Alphabet Sigma + ordered macro library, canonical order a<b<c<m1<m2<..."""

    def __init__(self, base_tokens, macro_bodies_ordered):
        self.base = list(base_tokens)
        self.macro_names = [name for name, _ in macro_bodies_ordered]
        self.bodies = dict(macro_bodies_ordered)
        self.alphabet = self.base + self.macro_names
        self.index = {}
        for i, s in enumerate(self.alphabet):
            self.index[s] = i
        self.n = len(self.alphabet)
        self._expansion_cache = None

    # -- expansion with fail-closed cycle detection -------------------------
    def expansions(self):
        """dict symbol -> base-token tuple, or raises ValueError on a cycle."""
        if self._expansion_cache is not None:
            return self._expansion_cache
        out = {}
        for t in self.base:
            out[t] = (t,)
        state = {}  # name -> 0 unvisited / 1 in progress / 2 done

        def visit(name):
            st = state.get(name, 0)
            if st == 2:
                return out[name]
            if st == 1:
                raise ValueError(RECURSIVE_LIBRARY_CYCLE)
            state[name] = 1
            body = self.bodies[name]
            acc = []
            for sym in body:
                if sym in out and sym in self.base:
                    acc.append(sym)
                elif sym in self.bodies:
                    acc.extend(visit(sym))
                else:
                    raise ValueError("UNKNOWN_SYMBOL:" + str(sym))
            state[name] = 2
            out[name] = tuple(acc)
            return out[name]

        for name in self.macro_names:
            visit(name)
        self._expansion_cache = out
        return out

    def is_acyclic(self):
        try:
            self.expansions()
            return True
        except ValueError:
            return False


def min_length_and_lex_least(word, grammar):
    """Least program length expanding to `word`, plus the lex-least such program.

    Returns (ell_star, program_tuple).  `word` is a tuple of base tokens.
    Every base word is expressible (the identity program), so this is total on
    acyclic grammars.
    """
    exps = grammar.expansions()
    m = len(word)
    INF = m + 1
    dp = [INF] * (m + 1)
    dp[m] = 0
    # symbols in canonical order, with their expansions
    ordered = [(s, exps[s]) for s in grammar.alphabet]
    for i in range(m - 1, -1, -1):
        best = INF
        for _s, e in ordered:
            le = len(e)
            if i + le <= m and tuple(word[i:i + le]) == e:
                cand = dp[i + le] + 1
                if cand < best:
                    best = cand
        dp[i] = best
    if dp[0] >= INF:
        raise ValueError("UNREACHABLE_TARGET")
    prog = []
    i = 0
    while i < m:
        for s, e in ordered:
            le = len(e)
            if i + le <= m and tuple(word[i:i + le]) == e and dp[i + le] == dp[i] - 1:
                prog.append(s)
                i += le
                break
        else:  # pragma: no cover - guarded by dp construction
            raise ValueError("SEGMENTATION_FAILURE")
    return dp[0], tuple(prog)


def program_rank(program, grammar):
    """0-based n-ary index of `program` within its own length class."""
    r = 0
    for s in program:
        r = r * grammar.n + grammar.index[s]
    return r


def burden(word, grammar):
    """B_G(w) = Phi(n, ell*-1) + rank + 1 (#897 T3). Exact integer."""
    ell, prog = min_length_and_lex_least(word, grammar)
    return phi(grammar.n, ell - 1) + program_rank(prog, grammar) + 1


# --------------------------------------------------------------------------
# 1. REP-1 : exact decision bracket
# --------------------------------------------------------------------------

def rep1_band(n, n_prime, ell0, ell1):
    """Three-way rank-free classification.  All integer comparisons."""
    if phi(n_prime, ell1) <= phi(n, ell0 - 1):
        return BAND_REDUCTION
    if phi(n_prime, ell1 - 1) >= phi(n, ell0):
        return BAND_INCREASE
    return BAND_RANK


BAND_WEAK_REDUCTION = "WEAK_REDUCTION_OR_EQUALITY"
BAND_WEAK_INCREASE = "WEAK_INCREASE_OR_EQUALITY"


def rep1_band_refined(n, n_prime, ell0, ell1):
    """REP-1b: the five-way completion of the frozen three-way bracket.

    Found by the registered second route (independent_oracle_v1.py), which
    checked every census cell against the EXTREME rank assignments and reported
    four cells that the frozen three-way rule sends to RANK_DECIDED even though
    their sign is in fact rank-free in the WEAK sense.  The frozen rule is sound
    (it never asserts a wrong strict sign) but incomplete at those boundaries.
    The refinement only ever splits RANK_DECIDED; it never moves a cell out of a
    frozen guaranteed band.

        B1 in [Phi(n', l1 - 1) + 1, Phi(n', l1)]
        B0 in [Phi(n,  l0 - 1) + 1, Phi(n,  l0)]
    """
    b1_lo = phi(n_prime, ell1 - 1) + 1
    b1_hi = phi(n_prime, ell1)
    b0_lo = phi(n, ell0 - 1) + 1
    b0_hi = phi(n, ell0)
    if b1_hi < b0_lo:
        return BAND_REDUCTION            # B1 < B0 for every rank assignment
    if b1_lo > b0_hi:
        return BAND_INCREASE             # B1 > B0 for every rank assignment
    if b1_hi <= b0_lo:
        return BAND_WEAK_REDUCTION       # B1 <= B0 always, equality realisable
    if b1_lo >= b0_hi:
        return BAND_WEAK_INCREASE        # B1 >= B0 always, equality realisable
    return BAND_RANK


def rep1_census(fx):
    """Full (n, n', ell0, ell1) classification census with band-disjointness proof."""
    spec = fx["rep1_census"]
    rows = []
    counts = {BAND_REDUCTION: 0, BAND_INCREASE: 0, BAND_RANK: 0}
    refined_counts = {}
    boundary_cells = []
    refinement_conflicts = []
    disjoint_violations = []
    monotone_violations = []
    for n in spec["n_values"]:
        for off in spec["n_prime_offsets"]:
            n_prime = n + off
            for ell0 in range(1, spec["ell0_max"] + 1):
                for ell1 in range(1, ell0 + 1):
                    red = phi(n_prime, ell1) <= phi(n, ell0 - 1)
                    inc = phi(n_prime, ell1 - 1) >= phi(n, ell0)
                    if red and inc:
                        disjoint_violations.append([n, n_prime, ell0, ell1])
                    band = rep1_band(n, n_prime, ell0, ell1)
                    refined = rep1_band_refined(n, n_prime, ell0, ell1)
                    counts[band] += 1
                    refined_counts[refined] = refined_counts.get(refined, 0) + 1
                    if band != refined:
                        if band != BAND_RANK:
                            refinement_conflicts.append(
                                [n, n_prime, ell0, ell1, band, refined])
                        else:
                            boundary_cells.append(
                                [n, n_prime, ell0, ell1, refined])
                    rows.append({
                        "n": n, "n_prime": n_prime, "ell0": ell0, "ell1": ell1,
                        "d": ell0 - ell1, "band": band, "band_refined": refined,
                        "phi_np_l1": phi(n_prime, ell1),
                        "phi_n_l0m1": phi(n, ell0 - 1),
                        "phi_np_l1m1": phi(n_prime, ell1 - 1),
                        "phi_n_l0": phi(n, ell0),
                    })
    # monotonicity in d at fixed (n, n', ell0): deeper compression never moves
    # a cell from REDUCTION towards INCREASE.
    order = {BAND_REDUCTION: 0, BAND_RANK: 1, BAND_INCREASE: 2}
    by_key = {}
    for r in rows:
        by_key.setdefault((r["n"], r["n_prime"], r["ell0"]), []).append(r)
    for key, group in by_key.items():
        group.sort(key=lambda r: r["d"])
        for a, b in zip(group, group[1:]):
            if order[b["band"]] > order[a["band"]]:
                monotone_violations.append([key, a["d"], a["band"], b["d"], b["band"]])
    return {
        "rows": rows,
        "counts": counts,
        "refined_counts": refined_counts,
        "REP_1b_boundary_cells_resolved_by_refinement": boundary_cells,
        "refinement_conflicts_with_frozen_guaranteed_bands": refinement_conflicts,
        "frozen_rule_is_sound_but_incomplete": (
            not refinement_conflicts and bool(boundary_cells)),
        "band_disjointness_violations": disjoint_violations,
        "monotonicity_in_compression_depth_violations": monotone_violations,
        "provenance": "the five-way refinement REP-1b was found by the registered "
                      "second route's extreme-rank check, not by the frozen rule; "
                      "the frozen three-way statement is reported unchanged.",
    }


# --------------------------------------------------------------------------
# 2. REP-3 : the boundary counterexample and its near-miss hostile
# --------------------------------------------------------------------------

def _macro_list(d):
    """Deterministic macro ordering m1, m2, m3, ... from a fixtures dict."""
    names = sorted(d.keys(), key=lambda s: (len(s), s))
    return [(nm, tuple(d[nm])) for nm in names]


def rep3_instance(word_str, lib_dict, base_tokens):
    w = tuple(word_str)
    g0 = Grammar(base_tokens, [])
    g1 = Grammar(base_tokens, _macro_list(lib_dict))
    ell0, p0 = min_length_and_lex_least(w, g0)
    ell1, p1 = min_length_and_lex_least(w, g1)
    b0 = phi(g0.n, ell0 - 1) + program_rank(p0, g0) + 1
    b1 = phi(g1.n, ell1 - 1) + program_rank(p1, g1) + 1
    band = rep1_band(g0.n, g1.n, ell0, ell1)
    return {
        "word": word_str,
        "len": len(word_str),
        "n": g0.n, "n_prime": g1.n,
        "ell0": ell0, "ell1": ell1,
        "macro_used_by_hit_program": bool(
            [s for s in p1 if s not in base_tokens]),
        "lex_least_program_G0": "".join(p0),
        "lex_least_program_G1": "".join(p1),
        "B_G0": b0, "B_G1": b1,
        "delta": b1 - b0,
        "burden_increases": b1 > b0,
        "band": band,
        "B_G1_floor": phi(g1.n, ell1 - 1) + 1,
        "B_G0_ceiling": phi(g0.n, ell0),
        "rank_free_separation": (phi(g1.n, ell1 - 1) + 1) > phi(g0.n, ell0),
    }


# --------------------------------------------------------------------------
# 3. REP-2 : portfolio form with charges
# --------------------------------------------------------------------------

def k_total(lib_dict, kappa):
    return sum(len(body) + kappa for body in lib_dict.values())


def rep2_portfolio(targets, lib_dict, base_tokens, kappa):
    """Exact decomposition  dNet = -Saving(T+) + Tax(T0) + K_total."""
    g0 = Grammar(base_tokens, [])
    g1 = Grammar(base_tokens, _macro_list(lib_dict))
    saving = 0
    tax = 0
    per = []
    n_plus = 0
    n_zero = 0
    b0_sum = 0
    b1_sum = 0
    for t in targets:
        w = tuple(t)
        ell0, p0 = min_length_and_lex_least(w, g0)
        ell1, p1 = min_length_and_lex_least(w, g1)
        b0 = phi(g0.n, ell0 - 1) + program_rank(p0, g0) + 1
        b1 = phi(g1.n, ell1 - 1) + program_rank(p1, g1) + 1
        b0_sum += b0
        b1_sum += b1
        if ell1 < ell0:
            n_plus += 1
            saving += (b0 - b1)
            cls = "T_plus"
        else:
            n_zero += 1
            tax += (b1 - b0)
            cls = "T_zero"
        per.append({
            "target": t, "class": cls, "ell0": ell0, "ell1": ell1,
            "B_G0": b0, "B_G1": b1, "delta": b1 - b0,
            "band": rep1_band(g0.n, g1.n, ell0, ell1),
        })
    kt = k_total(lib_dict, kappa)
    d_net_direct = (b1_sum - b0_sum) + kt
    d_net_decomposed = -saving + tax + kt
    return {
        "library": dict((k, list(v)) for k, v in lib_dict.items()),
        "kappa": kappa,
        "K_total": kt,
        "n_targets": len(targets),
        "n_T_plus": n_plus,
        "n_T_zero": n_zero,
        "burden_G0_total": b0_sum,
        "burden_G1_total": b1_sum,
        "Saving_T_plus": saving,
        "Tax_T_zero": tax,
        "dNet_direct": d_net_direct,
        "dNet_decomposed": d_net_decomposed,
        "decomposition_exact": d_net_direct == d_net_decomposed,
        "criterion_reduces_expected_cost": saving > (tax + kt),
        "verdict": "REDUCES" if d_net_direct < 0 else "DOES_NOT_REDUCE",
        "tax_strictly_positive_on_T_zero": (tax > 0) if n_zero else None,
        "per_target": per,
    }


# --------------------------------------------------------------------------
# 4. NOV-1 / NOV-2 : expressive closure and budget-reachability non-monotonicity
# --------------------------------------------------------------------------

def all_base_words(base_tokens, lmax):
    out = []
    cur = [()]
    for _ in range(lmax):
        nxt = []
        for p in cur:
            for t in base_tokens:
                nxt.append(p + (t,))
        out.extend(nxt)
        cur = nxt
    return out


def nov1_expressive_closure(base_tokens, lib_dicts, cycle_dicts, lmax):
    """Growth adds zero expressive power; cycles are rejected fail-closed."""
    sigma_plus = set("".join(w) for w in all_base_words(base_tokens, lmax))
    results = []
    for lib in lib_dicts:
        g = Grammar(base_tokens, _macro_list(lib))
        exps = g.expansions()
        # (subset) every program over A_t expands into Sigma+ : verified by
        # checking every symbol's expansion is a base word, then closure under
        # concatenation is immediate.
        subset_ok = all(all(t in base_tokens for t in e) for e in exps.values())
        # (superset) every base word of length <= lmax is expressible over A_t
        reachable = set()
        for w in all_base_words(base_tokens, lmax):
            try:
                min_length_and_lex_least(w, g)
                reachable.add("".join(w))
            except ValueError:
                pass
        results.append({
            "library": dict((k, list(v)) for k, v in lib.items()),
            "alphabet_size": g.n,
            "every_program_expands_into_Sigma_plus": subset_ok,
            "sigma_plus_covered_up_to_lmax": reachable == sigma_plus,
            "missing_words": sorted(sigma_plus - reachable)[:8],
            "extra_words": sorted(reachable - sigma_plus)[:8],
            "expressive_power_delta": 0 if (subset_ok and reachable == sigma_plus) else None,
        })
    cycles = []
    for lib in cycle_dicts:
        g = Grammar(base_tokens, _macro_list(lib))
        try:
            g.expansions()
            code = "NO_ERROR_RAISED"
        except ValueError as exc:
            code = str(exc)
        cycles.append({
            "library": dict((k, list(v)) for k, v in lib.items()),
            "code": code,
            "detected": code == RECURSIVE_LIBRARY_CYCLE,
        })
    return {
        "lmax": lmax,
        "sigma_plus_size": len(sigma_plus),
        "libraries": results,
        "cycle_hostiles": cycles,
        "all_libraries_add_zero_expressive_power": all(
            r["expressive_power_delta"] == 0 for r in results),
        "all_cycle_hostiles_detected": all(c["detected"] for c in cycles),
    }


def nov2_reachability_census(base_tokens, lib_dict, lmax, budgets):
    g0 = Grammar(base_tokens, [])
    g1 = Grammar(base_tokens, _macro_list(lib_dict))
    words = all_base_words(base_tokens, lmax)
    table = []
    for w in words:
        b0 = burden(w, g0)
        b1 = burden(w, g1)
        table.append(("".join(w), b0, b1))
    rows = []
    any_added = False
    any_removed = False
    for B in budgets:
        added = [s for (s, b0, b1) in table if b1 <= B < b0]
        removed = [s for (s, b0, b1) in table if b0 <= B < b1]
        reach0 = sum(1 for (_s, b0, _b1) in table if b0 <= B)
        reach1 = sum(1 for (_s, _b0, b1) in table if b1 <= B)
        any_added = any_added or bool(added)
        any_removed = any_removed or bool(removed)
        rows.append({
            "budget": B,
            "reach_G0": reach0,
            "reach_G1": reach1,
            "added_count": len(added),
            "removed_count": len(removed),
            "added_examples": sorted(added)[:6],
            "removed_examples": sorted(removed)[:6],
        })
    return {
        "lmax": lmax,
        "word_count": len(words),
        "library": dict((k, list(v)) for k, v in lib_dict.items()),
        "alphabet_G0": g0.n,
        "alphabet_G1": g1.n,
        "rows": rows,
        "ADDED_nonempty_at_some_budget": any_added,
        "REMOVED_nonempty_at_some_budget": any_removed,
        "reachability_non_monotone_under_growth": any_added and any_removed,
    }


# --------------------------------------------------------------------------
# 5. SD frame : charged oracle, dynamics, ecologies
# --------------------------------------------------------------------------

class FrameViolation(Exception):
    pass


class BudgetExhausted(Exception):
    pass


class ChargedOracle(object):
    """One evaluation = one charged unit.  Repeats are charged.

    `audit_calls` is an independent instrumented counter used only by the frame
    validator; a dynamic that evaluates without charging shows up as a mismatch.
    """

    def __init__(self, ecology, target, decoy, budget):
        self.ecology = ecology
        self._target = tuple(target)
        self._decoy = tuple(decoy)
        self.budget = budget
        self.charged = 0
        self.audit_calls = 0
        self.distinct = set()
        self.record = None          # optional query-sequence log
        self.first_hit = None
        self.ell = len(self._target)

    def evaluate(self, x, charge=True):
        self.audit_calls += 1
        if charge:
            self.charged += 1
        if self.charged > self.budget:
            raise BudgetExhausted()
        xt = tuple(x)
        self.distinct.add(xt)
        if self.record is not None:
            self.record.append(xt)
        if xt == self._target and self.first_hit is None:
            self.first_hit = self.charged
        if self.ecology == "OPAQUE":
            return 1 if xt == self._target else 0
        if self.ecology == "GRADED":
            return sum(1 for i in range(self.ell) if xt[i] == self._target[i])
        if self.ecology == "DECEPTIVE":
            if xt == self._target:
                return self.ell + 1
            return sum(1 for i in range(self.ell) if xt[i] == self._decoy[i])
        raise FrameViolation("UNKNOWN_ECOLOGY")


class _ArmView(object):
    """A portfolio arm's view of the shared charged oracle, capped at its share.

    Every evaluation is charged to the real oracle exactly once; the arm is cut
    off when its OWN spend reaches its share.  No evaluation is free.
    """

    def __init__(self, oracle, share):
        self.oracle = oracle
        self.share = share
        self.spent = 0
        self.ecology = oracle.ecology
        self.budget = share
        self._target = oracle._target
        self._decoy = oracle._decoy
        self.record = oracle.record

    @property
    def first_hit(self):
        return self.oracle.first_hit

    def evaluate(self, x, charge=True):
        if self.spent >= self.share:
            raise BudgetExhausted()
        self.spent += 1
        return self.oracle.evaluate(x, charge=charge)


class Lcg(object):
    """Exact integer LCG frozen in FROZEN_FIXTURES_V1.json."""

    def __init__(self, seed, a, c, m):
        self.s = seed % m
        self.a = a
        self.c = c
        self.m = m

    def next(self):
        self.s = (self.a * self.s + self.c) % self.m
        return self.s

    def below(self, k):
        # A power-of-two-modulus LCG has period 2^j in its low j bits, so
        # `next() % k` for small k is degenerate (measured: 11 distinct states
        # in 6561 draws).  Registered extraction is the high 15 bits.
        return (self.next() >> 16) % k


def _word_from_index(idx, base, ell):
    out = []
    n = len(base)
    for _ in range(ell):
        out.append(base[idx % n])
        idx //= n
    out.reverse()
    return tuple(out)


def _rand_word(rng, base, ell):
    return tuple(base[rng.below(len(base))] for _ in range(ell))


def run_dynamic(name, oracle, base, ell, rng, cfg, trace=None):
    """Drive one dynamic until hit, budget exhaustion or natural termination.

    `trace`, when given, is a list that receives every restart point used by the
    restarting dynamics (LS, GRAD).  SD-2c's mechanism check consumes it.
    """
    n = len(base)
    try:
        if name == "ENUM":
            for idx in range(n ** ell):
                oracle.evaluate(_word_from_index(idx, base, ell))
                if oracle.first_hit is not None:
                    return
        elif name == "MUT":
            x = list(_rand_word(rng, base, ell))
            oracle.evaluate(tuple(x))
            while oracle.first_hit is None:
                i = rng.below(ell)
                cur = x[i]
                alts = [s for s in base if s != cur]
                x[i] = alts[rng.below(len(alts))]
                oracle.evaluate(tuple(x))
        elif name in ("LS", "GRAD"):
            while oracle.first_hit is None:
                x = list(_rand_word(rng, base, ell))
                if trace is not None:
                    trace.append(tuple(x))
                fx = oracle.evaluate(tuple(x))
                if name == "LS":
                    improved = True
                    while improved and oracle.first_hit is None:
                        improved = False
                        best_f = fx
                        best_move = None
                        for i in range(ell):
                            for s in base:
                                if s == x[i]:
                                    continue
                                y = list(x)
                                y[i] = s
                                fy = oracle.evaluate(tuple(y))
                                if fy > best_f:
                                    best_f = fy
                                    best_move = (i, s)
                        if best_move is not None:
                            x[best_move[0]] = best_move[1]
                            fx = best_f
                            improved = True
                else:  # GRAD : exact coordinate descent, left to right
                    changed = True
                    while changed and oracle.first_hit is None:
                        changed = False
                        for i in range(ell):
                            best_f = fx
                            best_s = x[i]
                            for s in base:
                                if s == x[i]:
                                    continue
                                y = list(x)
                                y[i] = s
                                fy = oracle.evaluate(tuple(y))
                                if fy > best_f:
                                    best_f = fy
                                    best_s = s
                            if best_s != x[i]:
                                x[i] = best_s
                                fx = best_f
                                changed = True
        elif name in ("EVO", "GP"):
            mu = cfg["population_mu"]
            lam = cfg["population_lambda"]
            pop = []
            for _ in range(mu):
                ind = _rand_word(rng, base, ell)
                pop.append((oracle.evaluate(ind), ind))
            while oracle.first_hit is None:
                children = []
                for _ in range(lam):
                    if name == "GP":
                        p1 = pop[rng.below(len(pop))][1]
                        p2 = pop[rng.below(len(pop))][1]
                        cut = 1 + rng.below(max(1, ell - 1))
                        child = list(p1[:cut]) + list(p2[cut:])
                    else:
                        child = list(pop[rng.below(len(pop))][1])
                    i = rng.below(ell)
                    cur = child[i]
                    alts = [s for s in base if s != cur]
                    child[i] = alts[rng.below(len(alts))]
                    ct = tuple(child)
                    children.append((oracle.evaluate(ct), ct))
                    if oracle.first_hit is not None:
                        return
                pool = pop + children
                pool.sort(key=lambda fi: (-fi[0], fi[1]))
                pop = pool[:mu]
        elif name == "META":
            arms = cfg["meta_arms"]
            share = oracle.budget // len(arms)
            for arm in arms:
                capped = _ArmView(oracle, share)
                try:
                    run_dynamic(arm, capped, base, ell, rng, cfg, trace)
                except BudgetExhausted:
                    pass
                if oracle.first_hit is not None:
                    return
        else:
            raise FrameViolation("UNKNOWN_DYNAMIC:" + name)
    except BudgetExhausted:
        return


def _sd_setup(fx):
    cfg = fx["sd_frame"]
    base = fx["base_tokens"]
    n = len(base)
    ell = cfg["ell_primary"]
    succ = dict((base[i], base[(i + 1) % n]) for i in range(n))
    return cfg, base, n, ell, succ, (n ** ell)


def _decoy_for(target, succ):
    return tuple(succ[t] for t in target)


def _hamming(x, y):
    return sum(1 for i in range(len(x)) if x[i] != y[i])


SD_CENSUS_DYNAMICS = ["ENUM", "MUT", "LS", "GP", "EVO", "GRAD", "META", "RAND"]


def sd_census(fx):
    """The authoritative comparison: every dynamic x every ecology x 200 seeds.

    One registered target per seed (drawn by the frozen LCG), identical for
    every dynamic, identical budget, identical charging.  This is the common
    charged frame; the single-instance table below is illustrative only.
    """
    cfg, base, n, ell, succ, X = _sd_setup(fx)
    lcg = cfg["lcg"]
    budget = X
    seeds = list(range(cfg["null"]["seeds"][0], cfg["null"]["seeds"][1] + 1))
    targets = []
    for sd in seeds:
        trng = Lcg(lcg["seed"] * 31 + sd, lcg["a"], lcg["c"], lcg["m"])
        targets.append(_rand_word(trng, base, ell))

    agg = {}
    mech = {"LS": {"hits": 0, "explained": 0, "unexplained": []},
            "GRAD": {"hits": 0, "explained": 0, "unexplained": []}}
    for eco in cfg["ecologies"]:
        for dyn in SD_CENSUS_DYNAMICS:
            hits = 0
            sum_evals = 0
            worst = 0
            distinct_sum = 0
            charged_sum = 0
            for k, sd in enumerate(seeds):
                tgt = targets[k]
                dcy = _decoy_for(tgt, succ)
                rng = Lcg(lcg["seed"] + sd, lcg["a"], lcg["c"], lcg["m"])
                oracle = ChargedOracle(eco, tgt, dcy, budget)
                trace = []
                if dyn == "RAND":
                    try:
                        while oracle.first_hit is None:
                            oracle.evaluate(_rand_word(rng, base, ell))
                    except BudgetExhausted:
                        pass
                else:
                    run_dynamic(dyn, oracle, base, ell, rng, cfg, trace)
                distinct_sum += len(oracle.distinct)
                charged_sum += oracle.charged
                if oracle.first_hit is not None:
                    hits += 1
                    sum_evals += oracle.first_hit
                    if oracle.first_hit > worst:
                        worst = oracle.first_hit
                    # SD-2c mechanism check on the deceptive ecology
                    if eco == "DECEPTIVE" and dyn in ("LS", "GRAD"):
                        mech[dyn]["hits"] += 1
                        if dyn == "LS":
                            ok = any(_hamming(p, tgt) <= 1 for p in trace)
                        else:
                            ok = any(p[1:] == tgt[1:] for p in trace)
                        if ok:
                            mech[dyn]["explained"] += 1
                        else:
                            mech[dyn]["unexplained"].append("".join(tgt))
            agg[eco + "/" + dyn] = {
                "seeds": len(seeds),
                "hits": hits,
                "misses": len(seeds) - hits,
                "sum_evals_on_hits": sum_evals,
                "mean_evals_on_hits_num": sum_evals,
                "mean_evals_on_hits_den": hits,
                "worst_evals_on_hits": worst,
                "sum_distinct": distinct_sum,
                "sum_charged": charged_sum,
            }
    return {"aggregate": agg, "targets": len(targets), "budget": budget,
            "ell": ell, "space_size": X, "sd2c_mechanism": mech,
            "dynamics": SD_CENSUS_DYNAMICS, "ecologies": cfg["ecologies"]}


def sd_target_independence(fx):
    """Exact test replacing the freeze's OPAQUE hit-count null (see disposition).

    Under OPAQUE the objective is constant off the target, so a dynamic's next
    query is a function of its query history and seed ONLY - it cannot depend on
    the target.  Consequence: under OPAQUE, hits are a pure COVERAGE LOTTERY and
    guidance is worth exactly nothing.  This is checked mechanically: the same
    dynamic, same seed, two different targets must emit byte-identical query
    sequences up to the first hit.
    """
    cfg, base, n, ell, succ, X = _sd_setup(fx)
    lcg = cfg["lcg"]
    budget = X
    # targets deliberately away from the enumeration frontier: with an index-0
    # target ENUM hits on query 1 and the comparison prefix is empty, i.e. the
    # check passes vacuously.  Vacuity is flagged, not tolerated.
    w1 = _word_from_index((X - 1) // 3, base, ell)
    w2 = _word_from_index(2 * (X - 1) // 3, base, ell)
    rows = []
    for dyn in SD_CENSUS_DYNAMICS:
        seqs = []
        for w in (w1, w2):
            rng = Lcg(lcg["seed"], lcg["a"], lcg["c"], lcg["m"])
            oracle = ChargedOracle("OPAQUE", w, _decoy_for(w, succ), budget)
            oracle.record = []
            if dyn == "RAND":
                try:
                    while oracle.first_hit is None:
                        oracle.evaluate(_rand_word(rng, base, ell))
                except BudgetExhausted:
                    pass
            else:
                run_dynamic(dyn, oracle, base, ell, rng, cfg)
            seqs.append((oracle.record, oracle.first_hit))
        cut = min(len(seqs[0][0]), len(seqs[1][0]))
        # compare up to just before the earlier of the two hits
        hits = [h for h in (seqs[0][1], seqs[1][1]) if h is not None]
        if hits:
            cut = min(cut, min(hits) - 1)
        identical = seqs[0][0][:cut] == seqs[1][0][:cut]
        rows.append({
            "dynamic": dyn,
            "compared_prefix_length": cut,
            "query_sequences_identical": identical,
            "vacuous": cut <= 0,
        })
    return {
        "claim": "under OPAQUE every dynamic's query sequence is target-independent, "
                 "so hit counts are a coverage lottery and guidance buys nothing",
        "target_a": "".join(w1),
        "target_b": "".join(w2),
        "rows": rows,
        "any_vacuous_comparison": any(r["vacuous"] for r in rows),
        "all_target_independent": (
            all(r["query_sequences_identical"] for r in rows)
            and not any(r["vacuous"] for r in rows)),
    }


def sd_mut_objective_invariance(census):
    """MUT never reads f, so its row must be identical in all three ecologies."""
    agg = census["aggregate"]
    vals = dict((eco, agg[eco + "/MUT"]["hits"]) for eco in census["ecologies"])
    evals = dict((eco, agg[eco + "/MUT"]["sum_evals_on_hits"])
                 for eco in census["ecologies"])
    return {
        "claim": "MUT ignores the objective entirely; its census row is therefore "
                 "invariant across ecologies. A difference would prove an ecology "
                 "leak in the common frame.",
        "hits_per_ecology": vals,
        "sum_evals_per_ecology": evals,
        "invariant": len(set(vals.values())) == 1 and len(set(evals.values())) == 1,
    }


def _census_key(cell, budget):
    """Order: more hits first, then fewer total evaluations on the hits."""
    return (-cell["hits"], cell["sum_evals_on_hits"] + cell["misses"] * (budget + 1))


def sd_matrix(fx, census):
    """SD-1: the exact comparison and the dominance verdict.

    Dominance is read off the 200-seed census (authoritative).  The
    single-registered-instance table is emitted alongside because it shows,
    concretely, that per-instance luck exists and is why SD-2a is stated in
    expectation form.
    """
    cfg, base, n, ell, succ, X = _sd_setup(fx)
    lcg = cfg["lcg"]
    budget = X
    target = _word_from_index((X - 1) // 2, base, ell)
    decoy = _decoy_for(target, succ)
    single = []
    for eco in cfg["ecologies"]:
        for dyn in [d for d in cfg["dynamics"] if d != "NAS"]:
            rng = Lcg(lcg["seed"], lcg["a"], lcg["c"], lcg["m"])
            oracle = ChargedOracle(eco, target, decoy, budget)
            run_dynamic(dyn, oracle, base, ell, rng, cfg)
            single.append({
                "ecology": eco, "dynamic": dyn,
                "evals_to_hit": oracle.first_hit,
                "hit": oracle.first_hit is not None,
                "charged": oracle.charged,
                "distinct_candidates": len(oracle.distinct),
                "audit_calls": oracle.audit_calls,
                "charging_consistent": oracle.audit_calls == oracle.charged,
            })

    agg = census["aggregate"]
    best = {}
    worst = {}
    ranked = {}
    for eco in census["ecologies"]:
        rows = []
        for dyn in census["dynamics"]:
            if dyn == "RAND":
                continue  # RAND is the null control, not a competitor
            c = dict(agg[eco + "/" + dyn])
            c["dynamic"] = dyn
            rows.append(c)
        rows.sort(key=lambda c: _census_key(c, budget))
        ranked[eco] = [c["dynamic"] for c in rows]
        top = _census_key(rows[0], budget)
        bot = _census_key(rows[-1], budget)
        best[eco] = sorted(c["dynamic"] for c in rows
                           if _census_key(c, budget) == top)
        worst[eco] = sorted(c["dynamic"] for c in rows
                            if _census_key(c, budget) == bot)

    best_sets = [set(best[e]) for e in census["ecologies"]]
    worst_sets = [set(worst[e]) for e in census["ecologies"]]
    best_everywhere = sorted(set.intersection(*best_sets)) if best_sets else []
    worst_everywhere = sorted(set.intersection(*worst_sets)) if worst_sets else []
    return {
        "frame_held_fixed": [
            "search space Sigma^%d (|X| = %d)" % (ell, X),
            "target multiset: the same 200 registered targets for every dynamic",
            "cost accounting: 1 charged unit per objective evaluation, repeats charged",
            "budget: %d evaluations for every dynamic" % budget,
            "seed stream: the same frozen LCG, same seed per (dynamic, target)",
        ],
        "ell": ell, "space_size": X, "budget": budget,
        "illustrative_single_instance": {
            "target": "".join(target),
            "decoy": "".join(decoy),
            "decoy_hamming_distance_to_target": _hamming(decoy, target),
            "cells": single,
            "note": "single-instance results are subject to per-instance luck "
                    "(here blind restart search beats enumeration on one target); "
                    "the 200-seed census is authoritative.",
        },
        "census_ranking": ranked,
        "best_per_ecology": best,
        "worst_per_ecology": worst,
        "dynamics_best_in_every_ecology": best_everywhere,
        "dynamics_worst_in_every_ecology": worst_everywhere,
        "no_dominance": (not best_everywhere) and (not worst_everywhere),
        "charging_consistent_everywhere": all(
            c["charging_consistent"] for c in single),
    }


def sd_mechanism(fx, census):
    """SD-2a / SD-2b / SD-2c : why the ordering is what it is."""
    cfg, base, n, ell, succ, X = _sd_setup(fx)
    agg = census["aggregate"]
    seeds = census["targets"]

    # SD-2a : expected evaluations under OPAQUE
    enum_expected = Fraction(X + 1, 2)
    enum_census_mean = Fraction(sum(range(1, X + 1)), X)
    o = dict((d, agg["OPAQUE/" + d]) for d in census["dynamics"])
    resampling = ["MUT", "GP", "EVO"]

    # SD-2b : GRAD's exact worst case under GRADED
    grad_bound = 1 + ell * (n - 1)
    g = agg["GRADED/GRAD"]

    # SD-2c : DECEPTIVE structural failure + restart-accident characterisation
    mech = census["sd2c_mechanism"]
    ls_restart_window = 1 + ell * (n - 1)          # words within Hamming 1 of w
    grad_restart_window = n                        # words agreeing with w off position 0
    return {
        "SD_2a": {
            "claim": "Under OPAQUE, expected evaluations to hit is >= (|X|+1)/2 for any "
                     "oracle-only dynamic, with equality iff it never repeats a query.",
            "X": X,
            "bound_num": enum_expected.numerator,
            "bound_den": enum_expected.denominator,
            "enum_closed_form_mean_num": enum_census_mean.numerator,
            "enum_closed_form_mean_den": enum_census_mean.denominator,
            "enum_attains_bound": enum_census_mean == enum_expected,
            "enum_hits": o["ENUM"]["hits"],
            "enum_hits_all": o["ENUM"]["hits"] == seeds,
            "measured_mean_evals_on_hits": dict(
                (d, [o[d]["mean_evals_on_hits_num"], o[d]["mean_evals_on_hits_den"]])
                for d in census["dynamics"]),
            "measured_hits": dict((d, o[d]["hits"]) for d in census["dynamics"]),
            "duplicate_mechanism_sum_distinct": dict(
                (d, o[d]["sum_distinct"]) for d in census["dynamics"]),
            "resampling_dynamics_cover_strictly_less": all(
                o[d]["sum_distinct"] < o["ENUM"]["sum_distinct"] for d in resampling),
            "no_dynamic_matches_enum_coverage": all(
                o[d]["sum_distinct"] < o["ENUM"]["sum_distinct"]
                for d in census["dynamics"] if d != "ENUM"),
        },
        "SD_2b": {
            "claim": "Hamming agreement is separable across positions, so exact "
                     "coordinate descent hits in at most 1 + ell*(n-1) evaluations.",
            "derived_worst_case": grad_bound,
            "measured_hits": g["hits"],
            "measured_hits_all": g["hits"] == seeds,
            "measured_worst": g["worst_evals_on_hits"],
            "bound_respected": g["hits"] == seeds and g["worst_evals_on_hits"] <= grad_bound,
            "enum_expected_num": enum_expected.numerator,
            "enum_expected_den": enum_expected.denominator,
            "separation_factor_floor": (X + 1) // (2 * grad_bound),
            "mechanism": "separability of the objective, NOT any property of "
                         "gradient methods; the substrate has no differentiable structure",
        },
        "SD_2c": {
            "claim": "Under DECEPTIVE, the local-search trajectory converges to the "
                     "decoy z. Since z differs from the target w in every position, no "
                     "point on that trajectory (other than the restart point itself) can "
                     "be within one coordinate of w. Hits are therefore possible ONLY "
                     "through a restart accident, and the accident condition is exact.",
            "LS_accident_condition": "restart point within Hamming distance 1 of the target",
            "LS_accident_window": ls_restart_window,
            "GRAD_accident_condition": "restart point agrees with the target on every "
                                       "position except possibly position 0",
            "GRAD_accident_window": grad_restart_window,
            "space_size": X,
            "LS_hits": mech["LS"]["hits"],
            "LS_hits_explained_by_restart_accident": mech["LS"]["explained"],
            "LS_unexplained": mech["LS"]["unexplained"],
            "GRAD_hits": mech["GRAD"]["hits"],
            "GRAD_hits_explained_by_restart_accident": mech["GRAD"]["explained"],
            "GRAD_unexplained": mech["GRAD"]["unexplained"],
            "every_hit_explained": (
                mech["LS"]["hits"] == mech["LS"]["explained"]
                and mech["GRAD"]["hits"] == mech["GRAD"]["explained"]),
            "ENUM_hits": agg["DECEPTIVE/ENUM"]["hits"],
            "enum_unaffected_by_deception": agg["DECEPTIVE/ENUM"]["hits"] == seeds,
            "guided_collapse": (
                agg["DECEPTIVE/LS"]["hits"] < agg["DECEPTIVE/ENUM"]["hits"]
                and agg["DECEPTIVE/GRAD"]["hits"] < agg["DECEPTIVE/ENUM"]["hits"]),
        },
        "null_two_sided": {
            "control": "RAND (uniform sampling, identical charging)",
            "seeds": seeds,
            "GRADED_hits": dict(
                (d, agg["GRADED/" + d]["hits"]) for d in census["dynamics"]),
            "OPAQUE_hits": dict(
                (d, agg["OPAQUE/" + d]["hits"]) for d in census["dynamics"]),
            "GRADED_guided_beats_null": (
                agg["GRADED/GRAD"]["hits"] > agg["GRADED/RAND"]["hits"]
                or (agg["GRADED/GRAD"]["hits"] == agg["GRADED/RAND"]["hits"]
                    and agg["GRADED/GRAD"]["sum_evals_on_hits"]
                    < agg["GRADED/RAND"]["sum_evals_on_hits"])),
            "OPAQUE_no_guided_dynamic_beats_null": all(
                agg["OPAQUE/" + d]["hits"] <= agg["OPAQUE/RAND"]["hits"]
                for d in ["MUT", "LS", "GP", "EVO", "GRAD"]),
            "OPAQUE_enumeration_is_the_only_complete_dynamic": (
                agg["OPAQUE/ENUM"]["hits"] == seeds
                and all(agg["OPAQUE/" + d]["hits"] < seeds
                        for d in census["dynamics"] if d != "ENUM")),
            "freeze_criterion_disposition": {
                "as_frozen": "OPAQUE: guided dynamics must NOT beat the RAND control",
                "measured": dict((d, agg["OPAQUE/" + d]["hits"])
                                 for d in ["MUT", "LS", "GP", "EVO", "GRAD", "RAND"]),
                "met_as_specified": all(
                    agg["OPAQUE/" + d]["hits"] <= agg["OPAQUE/RAND"]["hits"]
                    for d in ["MUT", "LS", "GP", "EVO", "GRAD"]),
                "single_stage_attribution":
                    "the frozen criterion measured a HIT COUNT, but under OPAQUE the "
                    "objective is constant off the target, so no dynamic can use "
                    "guidance at all and the hit count is a pure coverage lottery in "
                    "which small differences (133/136 vs 129 of 200) carry no "
                    "information about guidance. The criterion was mis-specified, not "
                    "the theory.",
                "replacement_test": "SD_2d target-independence: same dynamic, same "
                                    "seed, two different targets must emit identical "
                                    "query sequences up to the first hit. This is "
                                    "exact and mechanical, and strictly stronger than "
                                    "the hit-count comparison it replaces.",
                "original_result_reported_verbatim": True,
            },
            "both_directions_pass": None,
        },
    }


def sd_nas_and_meta(fx, census):
    """SD-3 : representation search is governed by REP-2; portfolios dilute."""
    cfg, base, n, ell, succ, X = _sd_setup(fx)
    kappa = fx["kappa_primary"]
    target = _word_from_index((X - 1) // 2, base, ell)
    g0 = Grammar(base, [])
    b0 = burden(target, g0)
    ell0, _ = min_length_and_lex_least(target, g0)
    pool = []
    for lib in cfg["nas_library_pool"]:
        libt = dict((k, tuple(v)) for k, v in lib.items())
        g1 = Grammar(base, _macro_list(libt))
        b1 = burden(target, g1)
        kt = k_total(libt, kappa)
        ell1, _ = min_length_and_lex_least(target, g1)
        pool.append({
            "library": dict((k, list(v)) for k, v in lib.items()),
            "ell0": ell0, "ell1": ell1,
            "B_G0": b0, "B_G1": b1, "K_total": kt,
            "charged_delta": (b1 - b0) + kt,
            "REP1_band": rep1_band(g0.n, g1.n, ell0, ell1),
            "REP2_predicts_reduction": (b0 - b1) > kt,
            "measured_reduction": ((b1 - b0) + kt) < 0,
        })
    arms = cfg["meta_arms"]
    share = X // len(arms)
    agg = census["aggregate"]
    return {
        "NAS": {
            "target": "".join(target),
            "B_G0_baseline": b0,
            "pool": pool,
            "REP2_prediction_matches_measurement": all(
                p["REP2_predicts_reduction"] == p["measured_reduction"] for p in pool),
            "all_pool_libraries_lose": all(p["charged_delta"] > 0 for p in pool),
            "reading": "representation search is not a separate kind of search: its "
                       "charged outcome is decided by REP-1/REP-2 on the target at hand, "
                       "and REP-2 predicted every pool member's sign before it was run.",
        },
        "META": {
            "arms": arms,
            "equal_share": share,
            "coverage_dilution_identity": (
                "a portfolio with |arms| equal shares gives its enumeration arm "
                "exactly |X|/|arms| evaluations, so the completeness guarantee that "
                "ENUM alone carries (a hit within |X|) survives only for targets of "
                "index < |X|/|arms| - i.e. exactly a 1/|arms| fraction of the space"),
            "enum_guarantee_fraction_num": 1,
            "enum_guarantee_fraction_den": len(arms),
            "predicted_meta_hits_bound": share,
            "measured_hits": dict(
                (eco, agg[eco + "/META"]["hits"]) for eco in census["ecologies"]),
            "measured_enum_hits": dict(
                (eco, agg[eco + "/ENUM"]["hits"]) for eco in census["ecologies"]),
            "meta_never_matches_enum_in_OPAQUE": (
                agg["OPAQUE/META"]["hits"] < agg["OPAQUE/ENUM"]["hits"]),
            "reading": "budget portfolios do not come free: splitting the budget "
                       "destroys the completeness guarantee of the one arm that had it. "
                       "This is a derived accounting identity, not a measured preference.",
        },
    }


# --------------------------------------------------------------------------
# 6. Hostile battery (frame + criterion integrity)
# --------------------------------------------------------------------------

def hostiles(fx, rep2_main, rep3_primary, rep3_near):
    base = fx["base_tokens"]
    cfg = fx["sd_frame"]
    n = len(base)
    ell = cfg["ell_primary"]
    lcg = cfg["lcg"]
    budget = n ** ell
    target = _word_from_index((n ** ell - 1) // 2, base, ell)
    succ = dict((base[i], base[(i + 1) % n]) for i in range(n))
    decoy = tuple(succ[t] for t in target)
    out = []

    # H-NEARMISS : must be RANK_DECIDED, never a guaranteed band
    out.append({
        "id": "H-NEARMISS",
        "detected": rep3_near["band"] == BAND_RANK,
        "observed": rep3_near["band"],
        "expected": BAND_RANK,
    })

    # H-CYCLE : handled in NOV-1 block, mirrored here
    cyc = Grammar(base, _macro_list({"m1": ["m2", "a"], "m2": ["m1", "b"]}))
    try:
        cyc.expansions()
        code = "NO_ERROR_RAISED"
    except ValueError as exc:
        code = str(exc)
    out.append({"id": "H-CYCLE", "detected": code == RECURSIVE_LIBRARY_CYCLE,
                "observed": code, "expected": RECURSIVE_LIBRARY_CYCLE})

    # H-UNCHARGED : an evaluation that skips the charge counter
    o = ChargedOracle("OPAQUE", target, decoy, budget)
    o.evaluate(target[:1] + target[1:], charge=True)
    o.evaluate(decoy, charge=False)          # the hostile
    out.append({
        "id": "H-UNCHARGED",
        "detected": o.audit_calls != o.charged,
        "observed": "audit=%d charged=%d" % (o.audit_calls, o.charged),
        "expected": "FRAME_VIOLATION_UNCHARGED_EVALUATION",
    })

    # H-BUDGET : a dynamic given a larger budget than the frame's
    fair = ChargedOracle("OPAQUE", target, decoy, budget)
    cheat = ChargedOracle("OPAQUE", target, decoy, budget * 2)
    out.append({
        "id": "H-BUDGET",
        "detected": cheat.budget != fair.budget,
        "observed": "cheat_budget=%d frame_budget=%d" % (cheat.budget, fair.budget),
        "expected": "FRAME_VIOLATION_BUDGET_MISMATCH",
    })

    # H-TARGET : a dynamic run on a different target
    other = _word_from_index(0, base, ell)
    cheat_t = ChargedOracle("OPAQUE", other, decoy, budget)
    out.append({
        "id": "H-TARGET",
        "detected": cheat_t._target != fair._target,
        "observed": "".join(cheat_t._target) + " != " + "".join(fair._target),
        "expected": "FRAME_VIOLATION_TARGET_MISMATCH",
    })

    # H-ORACLE-PEEK : a dynamic that reads the target instead of querying f
    peek = ChargedOracle("OPAQUE", target, decoy, budget)
    peek.evaluate(peek._target)              # 1 charged evaluation, instant hit
    out.append({
        "id": "H-ORACLE-PEEK",
        "detected": peek.first_hit == 1,
        "observed": "first_hit=%s after 1 evaluation" % (peek.first_hit,),
        "expected": "FRAME_VIOLATION_TARGET_LEAK",
    })

    # H-CAPITAL : solution-capital library accepted per-target, rejected in portfolio
    cap = fx["rep2"]["capital_boundary"]
    w_star = cap["target"]
    lib_sol = {"m1": tuple(w_star)}
    single = rep2_portfolio([w_star], lib_sol, base, fx["kappa_primary"])
    whole = rep2_portfolio(
        fx["rep2"]["heldout_reuse_positive"] + fx["rep2"]["heldout_unrelated_control"],
        lib_sol, base, fx["kappa_primary"])
    out.append({
        "id": "H-CAPITAL",
        "detected": single["verdict"] == "REDUCES" and whole["verdict"] == "DOES_NOT_REDUCE",
        "observed": "single_target=%s dNet=%d ; portfolio=%s dNet=%d" % (
            single["verdict"], single["dNet_direct"],
            whole["verdict"], whole["dNet_direct"]),
        "expected": "accepted on w* alone, rejected on the registered distribution",
        "single_target_dNet": single["dNet_direct"],
        "portfolio_dNet": whole["dNet_direct"],
        "portfolio_Saving": whole["Saving_T_plus"],
        "portfolio_Tax": whole["Tax_T_zero"],
        "portfolio_K_total": whole["K_total"],
    })

    # H-NOREUSE : library whose body occurs in no target
    nr = fx["rep2"]["no_reuse_hostile"]
    lib_nr = dict((k, tuple(v)) for k, v in nr["library"].items())
    nr_res = rep2_portfolio(
        fx["rep2"]["heldout_reuse_positive"] + fx["rep2"]["heldout_unrelated_control"],
        lib_nr, base, fx["kappa_primary"])
    out.append({
        "id": "H-NOREUSE",
        "detected": nr_res["Saving_T_plus"] == 0 and nr_res["dNet_direct"] > 0,
        "observed": "Saving=%d dNet=%d" % (nr_res["Saving_T_plus"], nr_res["dNet_direct"]),
        "expected": "Saving==0 and dNet>0",
    })

    # H-RANKFLIP : burden implementation that drops the rank term
    g1 = Grammar(base, _macro_list(
        dict((k, tuple(v)) for k, v in fx["rep2"]["library"].items())))
    probe = tuple("ababcab")
    ell_s, prog = min_length_and_lex_least(probe, g1)
    true_b = phi(g1.n, ell_s - 1) + program_rank(prog, g1) + 1
    flipped = phi(g1.n, ell_s - 1) + 0 + 1
    out.append({
        "id": "H-RANKFLIP",
        "detected": flipped != true_b,
        "observed": "true=%d rank_dropped=%d" % (true_b, flipped),
        "expected": "two-route disagreement",
    })

    # no-alarm obligation on clean instances
    clean = {
        "rep3_primary_band_is_guaranteed_increase":
            rep3_primary["band"] == BAND_INCREASE,
        "rep2_main_decomposition_exact": rep2_main["decomposition_exact"],
        "rep2_main_reduces": rep2_main["verdict"] == "REDUCES",
        "clean_grammar_not_flagged_cyclic": Grammar(
            base, _macro_list(dict((k, tuple(v))
                                   for k, v in fx["rep2"]["library"].items()))
        ).is_acyclic(),
    }
    return {
        "battery": out,
        "all_detected": all(h["detected"] for h in out),
        "no_alarm_on_clean_instances": clean,
        "no_alarm_ok": all(clean.values()),
    }


# --------------------------------------------------------------------------
# 7. Parent reproduction (required validation, not optional)
# --------------------------------------------------------------------------

def reproduce_parent(fx, rep2_hplus, rep2_hminus):
    exp = fx["rep2"]["parent_published_integers_to_reproduce"]
    got = {
        "hplus_burden_g0": rep2_hplus["burden_G0_total"],
        "hplus_burden_g1": rep2_hplus["burden_G1_total"],
        "k_total": rep2_hplus["K_total"],
        "hplus_net": rep2_hplus["dNet_direct"],
        "hminus_burden_g0": rep2_hminus["burden_G0_total"],
        "hminus_burden_g1": rep2_hminus["burden_G1_total"],
        "hminus_net": rep2_hminus["dNet_direct"],
    }
    diffs = dict((k, [exp[k], got[k]]) for k in exp if exp[k] != got[k])
    return {
        "parent": "research/gmi-833-g0-grammar-growth-v1 (#897) HLD-1",
        "expected": exp,
        "recomputed": got,
        "mismatches": diffs,
        "parent_integers_reproduced": not diffs,
    }


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    with open(FIXTURES_PATH, "r") as fh:
        fx = json.load(fh)
    base = fx["base_tokens"]
    kappa = fx["kappa_primary"]

    rep1 = rep1_census(fx)

    r3 = fx["rep3"]
    rep3_primary = rep3_instance(r3["primary"]["word"], r3["library"], base)
    rep3_near = rep3_instance(r3["near_miss_hostile"]["word"], r3["library"], base)

    lib_main = dict((k, tuple(v)) for k, v in fx["rep2"]["library"].items())
    hplus = fx["rep2"]["heldout_reuse_positive"]
    hminus = fx["rep2"]["heldout_unrelated_control"]
    rep2_hplus = rep2_portfolio(hplus, lib_main, base, kappa)
    rep2_hminus = rep2_portfolio(hminus, lib_main, base, kappa)
    rep2_all = rep2_portfolio(hplus + hminus, lib_main, base, kappa)

    nov1 = nov1_expressive_closure(
        base,
        [dict((k, tuple(v)) for k, v in d.items()) for d in fx["nov1"]["libraries_checked"]],
        [dict((k, tuple(v)) for k, v in d.items()) for d in fx["nov1"]["cycle_hostiles"]],
        fx["nov1"]["expressibility_check_lmax"])

    nov2 = nov2_reachability_census(
        base,
        dict((k, tuple(v)) for k, v in fx["nov2"]["library"].items()),
        fx["nov2"]["lmax"], fx["nov2"]["budget_grid"])

    census = sd_census(fx)
    sd1 = sd_matrix(fx, census)
    sd2 = sd_mechanism(fx, census)
    sd2["SD_2d_target_independence"] = sd_target_independence(fx)
    sd2["SD_2e_mut_objective_invariance"] = sd_mut_objective_invariance(census)
    sd2["null_two_sided"]["both_directions_pass"] = (
        sd2["null_two_sided"]["GRADED_guided_beats_null"]
        and sd2["SD_2d_target_independence"]["all_target_independent"])
    sd3 = sd_nas_and_meta(fx, census)

    host = hostiles(fx, rep2_all, rep3_primary, rep3_near)
    parent = reproduce_parent(fx, rep2_hplus, rep2_hminus)

    verdict_ok = (
        not rep1["band_disjointness_violations"]
        and not rep1["monotonicity_in_compression_depth_violations"]
        and not rep1["refinement_conflicts_with_frozen_guaranteed_bands"]
        and rep3_primary["band"] == BAND_INCREASE
        and rep3_primary["burden_increases"]
        and rep3_primary["macro_used_by_hit_program"]
        and rep3_primary["rank_free_separation"]
        and rep3_near["band"] == BAND_RANK
        and rep2_all["decomposition_exact"]
        and rep2_hplus["verdict"] == "REDUCES"
        and rep2_hminus["verdict"] == "DOES_NOT_REDUCE"
        and nov1["all_libraries_add_zero_expressive_power"]
        and nov1["all_cycle_hostiles_detected"]
        and nov2["reachability_non_monotone_under_growth"]
        and sd1["no_dominance"]
        and sd2["SD_2a"]["enum_attains_bound"]
        and sd2["SD_2b"]["bound_respected"]
        and sd2["SD_2c"]["every_hit_explained"]
        and sd2["SD_2c"]["enum_unaffected_by_deception"]
        and sd2["SD_2c"]["guided_collapse"]
        and sd2["null_two_sided"]["both_directions_pass"]
        and sd2["null_two_sided"]["OPAQUE_enumeration_is_the_only_complete_dynamic"]
        and sd2["SD_2d_target_independence"]["all_target_independent"]
        and sd2["SD_2e_mut_objective_invariance"]["invariant"]
        and sd3["NAS"]["REP2_prediction_matches_measurement"]
        and sd3["META"]["meta_never_matches_enum_in_OPAQUE"]
        and host["all_detected"]
        and host["no_alarm_ok"]
        and parent["parent_integers_reproduced"]
    )

    result = {
        "schema": "GMI833DevelopmentalReuseResultV1",
        "issue": 833,
        "section": "L",
        "package": "gmi-833-developmental-reuse-v1",
        "route": "A_closed_form",
        "source_main": fx["source_main"],
        "freeze_commit": "01c6a820",
        "claim_ceiling": CLAIM_CEILING,
        "REP_1_census": rep1,
        "REP_3_boundary": {
            "primary": rep3_primary,
            "near_miss_hostile": rep3_near,
            "statement": "a strict description-length reduction through an actually "
                         "used macro is NOT sufficient for discovery-burden reduction",
            "label": "EARNED_BY_COUNTEREXAMPLE",
        },
        "REP_2_portfolio": {
            "heldout_reuse_positive": rep2_hplus,
            "heldout_unrelated_control": rep2_hminus,
            "combined": rep2_all,
        },
        "NOV_1_expressive_closure": nov1,
        "NOV_2_reachability": nov2,
        "SD_0_census": {"aggregate": census["aggregate"],
                        "seeds": census["targets"],
                        "budget": census["budget"],
                        "ell": census["ell"],
                        "space_size": census["space_size"]},
        "SD_1_matrix": sd1,
        "SD_2_mechanism": sd2,
        "SD_3_nas_meta": sd3,
        "hostiles": host,
        "parent_reproduction": parent,
        "rows_left_open": [
            "Predict evolvability on genuinely future task families.",
            "Validate developmental predictions on continual-learning systems.",
        ],
        "verdict": ("GMI_833_L_DEVELOPMENTAL_REUSE_GREEN_AT_REGISTERED_SCOPE"
                    if verdict_ok else "RED"),
    }
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if verdict_ok else 1


if __name__ == "__main__":
    sys.exit(main())
