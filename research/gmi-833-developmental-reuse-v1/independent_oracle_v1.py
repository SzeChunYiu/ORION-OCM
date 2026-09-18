#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Route B oracle for gmi-833-developmental-reuse-v1 (#833 Section L).

Materially independent recomputation.  This file MUST NOT import
`developmental_reuse_v1`; it re-derives every claimed integer by a different
method:

  * discovery burdens by LITERAL breadth-by-length enumeration of programs and
    expansion, never by the segmentation DP + rank closed form;
  * Phi by the closed geometric form n*(n**ell - 1)//(n - 1), never by the
    accumulating loop;
  * REP-1 bands verified against the EXTREME rank assignments directly;
  * NOV-1 by explicit construction of the expansion set;
  * SD-2b and SD-2c by EXHAUSTIVE sweeps over all 3**ell start points rather
    than by the 200-seed sample Route A uses.

Run:
    python3 -I -B independent_oracle_v1.py     # stdout == ORACLE_RESULT_V1.json
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(HERE, "FROZEN_FIXTURES_V1.json")


# ---------------------------------------------------------------- primitives

def phi_closed(n, ell):
    """Geometric closed form; deliberately not the accumulating loop."""
    if ell <= 0:
        return 0
    return (n * (n ** ell - 1)) // (n - 1)


def macro_order(lib):
    return sorted(lib.keys(), key=lambda s: (len(s), s))


def build_expansions(base, lib):
    """Symbol -> base tuple; raises on a dependency cycle."""
    exp = dict((t, (t,)) for t in base)
    pending = list(macro_order(lib))
    guard = 0
    while pending:
        guard += 1
        if guard > len(lib) * len(lib) + len(lib) + 2:
            raise ValueError("RECURSIVE_LIBRARY_CYCLE")
        nxt = []
        for name in pending:
            body = lib[name]
            if all(sym in exp for sym in body):
                acc = []
                for sym in body:
                    acc.extend(exp[sym])
                exp[name] = tuple(acc)
            else:
                nxt.append(name)
        if len(nxt) == len(pending):
            raise ValueError("RECURSIVE_LIBRARY_CYCLE")
        pending = nxt
    return exp


def alphabet_of(base, lib):
    return list(base) + macro_order(lib)


def burden_by_enumeration(word, base, lib, cap=None):
    """Literal enumeration: count programs until the first whose expansion is `word`.

    Programs are generated breadth by length, lexicographically within a length,
    under the canonical order a < b < c < m1 < m2 < ...  Returns the 1-based
    count, or None if `cap` is reached first.
    """
    exp = build_expansions(base, lib)
    alpha = alphabet_of(base, lib)
    n = len(alpha)
    target = tuple(word)
    m = len(target)
    pieces = [exp[s] for s in alpha]
    count = 0
    ell = 1
    while True:
        if ell > m:                      # the identity program has length <= m
            return None
        # every program of length `ell` in lexicographic (n-ary) order
        total = n ** ell
        idx = 0
        while idx < total:
            k = idx
            digits = [0] * ell
            for j in range(ell - 1, -1, -1):
                digits[j] = k % n
                k //= n
            out = []
            ok = True
            for dgt in digits:
                piece = pieces[dgt]
                if len(out) + len(piece) > m:
                    ok = False
                    break
                out.extend(piece)
            count += 1
            if cap is not None and count > cap:
                return None
            if ok and len(out) == m and tuple(out) == target:
                return count
            idx += 1
        ell += 1


def min_len_by_search(word, base, lib):
    """Least program length, by breadth-first search over expansions."""
    exp = build_expansions(base, lib)
    alpha = alphabet_of(base, lib)
    target = tuple(word)
    m = len(target)
    INF = m + 2
    best = [INF] * (m + 1)
    best[0] = 0
    for i in range(m):
        if best[i] >= INF:
            continue
        for s in alpha:
            e = exp[s]
            le = len(e)
            if i + le <= m and target[i:i + le] == e:
                if best[i] + 1 < best[i + le]:
                    best[i + le] = best[i] + 1
    return best[m]


def all_words(base, lmax):
    out = []
    cur = [()]
    for _ in range(lmax):
        nxt = [p + (t,) for p in cur for t in base]
        out.extend(nxt)
        cur = nxt
    return out


# ------------------------------------------------------------------- REP 1/3

def rep1_band_oracle(n, np_, l0, l1):
    if phi_closed(np_, l1) <= phi_closed(n, l0 - 1):
        return "GUARANTEED_REDUCTION"
    if phi_closed(np_, l1 - 1) >= phi_closed(n, l0):
        return "GUARANTEED_INCREASE"
    return "RANK_DECIDED"


def rep1_extreme_rank_check(fx):
    """Verify the bands against the EXTREME rank assignments directly.

    B lies in [Phi(n, ell-1) + 1, Phi(n, ell)].  A band is sound iff the sign it
    asserts holds for the worst possible pair of ranks.
    """
    spec = fx["rep1_census"]
    bad = []
    weak = []
    counts = {"GUARANTEED_REDUCTION": 0, "GUARANTEED_INCREASE": 0, "RANK_DECIDED": 0}
    rank_decided_both_signs = 0
    for n in spec["n_values"]:
        for off in spec["n_prime_offsets"]:
            np_ = n + off
            for l0 in range(1, spec["ell0_max"] + 1):
                for l1 in range(1, l0 + 1):
                    band = rep1_band_oracle(n, np_, l0, l1)
                    counts[band] += 1
                    b1_lo = phi_closed(np_, l1 - 1) + 1
                    b1_hi = phi_closed(np_, l1)
                    b0_lo = phi_closed(n, l0 - 1) + 1
                    b0_hi = phi_closed(n, l0)
                    if band == "GUARANTEED_REDUCTION" and not (b1_hi < b0_lo):
                        bad.append(["REDUCTION", n, np_, l0, l1])
                    if band == "GUARANTEED_INCREASE" and not (b1_lo > b0_hi):
                        bad.append(["INCREASE", n, np_, l0, l1])
                    if band == "RANK_DECIDED":
                        if (b1_lo < b0_hi) and (b1_hi > b0_lo):
                            rank_decided_both_signs += 1
                        elif b1_hi <= b0_lo:
                            weak.append(["WEAK_REDUCTION_OR_EQUALITY", n, np_, l0, l1])
                        elif b1_lo >= b0_hi:
                            weak.append(["WEAK_INCREASE_OR_EQUALITY", n, np_, l0, l1])
                        else:  # pragma: no cover - the four cases are exhaustive
                            bad.append(["UNCLASSIFIABLE", n, np_, l0, l1])
    return {
        "counts": counts,
        "extreme_rank_violations": bad,
        "rank_decided_cells_with_both_signs_realisable": rank_decided_both_signs,
        "weak_boundary_cells_frozen_rule_leaves_in_RANK_DECIDED": weak,
        "frozen_guaranteed_bands_never_assert_a_wrong_strict_sign": not bad,
        "sound": not bad,
        "note": "the weak-boundary cells are sound under the frozen rule (it merely "
                "declines to decide them); REP-1b classifies them exactly.",
    }


def rep3_by_enumeration(fx):
    base = fx["base_tokens"]
    lib = dict((k, tuple(v)) for k, v in fx["rep3"]["library"].items())
    out = {}
    for key in ("primary", "near_miss_hostile"):
        spec = fx["rep3"][key]
        w = tuple(spec["word"])
        b0 = burden_by_enumeration(w, base, {})
        b1 = burden_by_enumeration(w, base, lib)
        l0 = min_len_by_search(w, base, {})
        l1 = min_len_by_search(w, base, lib)
        n = len(base)
        np_ = len(base) + len(lib)
        out[key] = {
            "word": spec["word"],
            "ell0": l0, "ell1": l1,
            "B_G0_enumerated": b0,
            "B_G1_enumerated": b1,
            "delta": b1 - b0,
            "band": rep1_band_oracle(n, np_, l0, l1),
            "burden_increases": b1 > b0,
            "rank_free_floor_G1": phi_closed(np_, l1 - 1) + 1,
            "rank_free_ceiling_G0": phi_closed(n, l0),
        }
    return out


# ------------------------------------------------------------------- REP 2

def rep2_by_enumeration(fx):
    base = fx["base_tokens"]
    lib = dict((k, tuple(v)) for k, v in fx["rep2"]["library"].items())
    kappa = fx["kappa_primary"]
    kt = sum(len(b) + kappa for b in lib.values())
    out = {}
    for key in ("heldout_reuse_positive", "heldout_unrelated_control"):
        b0 = 0
        b1 = 0
        for t in fx["rep2"][key]:
            w = tuple(t)
            b0 += burden_by_enumeration(w, base, {})
            b1 += burden_by_enumeration(w, base, lib)
        out[key] = {
            "burden_G0_total": b0, "burden_G1_total": b1,
            "K_total": kt, "dNet": (b1 - b0) + kt,
        }
    exp = fx["rep2"]["parent_published_integers_to_reproduce"]
    hp = out["heldout_reuse_positive"]
    hm = out["heldout_unrelated_control"]
    out["parent_integers_reproduced_by_enumeration"] = (
        hp["burden_G0_total"] == exp["hplus_burden_g0"]
        and hp["burden_G1_total"] == exp["hplus_burden_g1"]
        and hp["dNet"] == exp["hplus_net"]
        and hm["burden_G0_total"] == exp["hminus_burden_g0"]
        and hm["burden_G1_total"] == exp["hminus_burden_g1"]
        and hm["dNet"] == exp["hminus_net"])
    return out


# ------------------------------------------------------------------ NOV 1/2

def nov1_by_construction(fx):
    base = fx["base_tokens"]
    lmax = fx["nov1"]["expressibility_check_lmax"]
    sigma = set("".join(w) for w in all_words(base, lmax))
    libs = []
    for libd in fx["nov1"]["libraries_checked"]:
        lib = dict((k, tuple(v)) for k, v in libd.items())
        exp = build_expansions(base, lib)
        # expansion set of all programs, truncated at length lmax
        reachable = set()
        alpha = alphabet_of(base, lib)
        frontier = [()]
        for _ in range(lmax):
            nxt = []
            for p in frontier:
                for s in alpha:
                    q = p + (s,)
                    word = []
                    for sym in q:
                        word.extend(exp[sym])
                    if len(word) <= lmax:
                        reachable.add("".join(word))
                        nxt.append(q)
            frontier = nxt
        libs.append({
            "library": dict((k, list(v)) for k, v in lib.items()),
            "expansion_set_equals_sigma_plus": reachable == sigma,
            "only_base_tokens_in_expansions": all(
                all(t in base for t in e) for e in exp.values()),
        })
    cycles = []
    for libd in fx["nov1"]["cycle_hostiles"]:
        lib = dict((k, tuple(v)) for k, v in libd.items())
        try:
            build_expansions(base, lib)
            code = "NO_ERROR_RAISED"
        except ValueError as exc:
            code = str(exc)
        cycles.append({"library": dict((k, list(v)) for k, v in lib.items()),
                       "code": code,
                       "detected": code == "RECURSIVE_LIBRARY_CYCLE"})
    return {
        "sigma_plus_size": len(sigma),
        "libraries": libs,
        "all_add_zero_expressive_power": all(
            L["expansion_set_equals_sigma_plus"] and L["only_base_tokens_in_expansions"]
            for L in libs),
        "cycle_hostiles": cycles,
        "all_cycle_hostiles_detected": all(c["detected"] for c in cycles),
    }


def nov2_by_enumeration(fx):
    base = fx["base_tokens"]
    lib = dict((k, tuple(v)) for k, v in fx["nov2"]["library"].items())
    lmax = fx["nov2"]["lmax"]
    rows = []
    table = []
    for w in all_words(base, lmax):
        table.append(("".join(w),
                      burden_by_enumeration(w, base, {}),
                      burden_by_enumeration(w, base, lib)))
    any_added = False
    any_removed = False
    for B in fx["nov2"]["budget_grid"]:
        added = [s for (s, b0, b1) in table if b1 <= B < b0]
        removed = [s for (s, b0, b1) in table if b0 <= B < b1]
        any_added = any_added or bool(added)
        any_removed = any_removed or bool(removed)
        rows.append({"budget": B,
                     "reach_G0": sum(1 for (_s, b0, _b1) in table if b0 <= B),
                     "reach_G1": sum(1 for (_s, _b0, b1) in table if b1 <= B),
                     "added_count": len(added), "removed_count": len(removed),
                     "added_examples": sorted(added)[:6],
                     "removed_examples": sorted(removed)[:6]})
    return {"rows": rows,
            "ADDED_nonempty_at_some_budget": any_added,
            "REMOVED_nonempty_at_some_budget": any_removed,
            "reachability_non_monotone_under_growth": any_added and any_removed}


# -------------------------------------------------------- SD, exhaustive route

def _idx_to_word(idx, base, ell):
    out = []
    n = len(base)
    for _ in range(ell):
        out.append(base[idx % n])
        idx //= n
    out.reverse()
    return tuple(out)


def sd2a_exact(fx):
    """ENUM's expected evaluations under OPAQUE, by explicit summation."""
    base = fx["base_tokens"]
    ell = fx["sd_frame"]["ell_primary"]
    X = len(base) ** ell
    total = 0
    for k in range(X):            # target at enumeration index k is hit at k+1
        total += k + 1
    return {"X": X, "sum_over_all_targets": total,
            "mean_num": total, "mean_den": X,
            "closed_form_num": X + 1, "closed_form_den": 2,
            "agrees_with_closed_form": total * 2 == (X + 1) * X}


def sd2b_exhaustive_at(fx, ell):
    """Coordinate descent under GRADED, over ALL 3**ell start points.

    Exhaustive, so this is a proof at scope rather than a 200-sample estimate.
    """
    base = fx["base_tokens"]
    n = len(base)
    X = n ** ell
    bound = 1 + ell * (n - 1)
    target = _idx_to_word((X - 1) // 2, base, ell)
    worst = 0
    misses = 0
    for start in range(X):
        x = list(_idx_to_word(start, base, ell))
        evals = 1                                   # the initial evaluation
        hit = (tuple(x) == target)
        if not hit:
            for i in range(ell):
                for s in base:
                    if s == x[i]:
                        continue
                    y = list(x)
                    y[i] = s
                    evals += 1
                    if tuple(y) == target:
                        hit = True
                        break
                    if y[i] == target[i]:
                        pass
                # greedy: adopt the target's symbol at this position
                if hit:
                    break
                x[i] = target[i]
            # after a full sweep every position matches, so a hit must have occurred
        if hit:
            if evals > worst:
                worst = evals
        else:
            misses += 1
    return {"ell": ell, "start_points_swept": X, "derived_bound": bound,
            "worst_observed": worst, "misses": misses,
            "bound_respected": misses == 0 and worst <= bound}


def sd2b_exhaustive(fx):
    """Exhaustive verification at every registered scaling ell that is tractable."""
    rows = []
    for ell in fx["sd_frame"]["ell_scaling"]:
        if len(fx["base_tokens"]) ** ell > 10000:
            rows.append({"ell": ell, "skipped": "start-point sweep beyond the "
                                                "registered exhaustive budget",
                         "derived_bound": 1 + ell * (len(fx["base_tokens"]) - 1)})
            continue
        rows.append(sd2b_exhaustive_at(fx, ell))
    primary = [r for r in rows if r.get("ell") == fx["sd_frame"]["ell_primary"]][0]
    return {"rows": rows,
            "primary": primary,
            "all_swept_bounds_respected": all(
                r["bound_respected"] for r in rows if "bound_respected" in r)}


def sd2c_exhaustive(fx):
    """DECEPTIVE: which restart points let coordinate descent evaluate w?

    Exhaustive over all 3**ell start points.  The derived characterisation is
    `x0` agrees with the target on every position except possibly position 0.
    """
    base = fx["base_tokens"]
    n = len(base)
    ell = fx["sd_frame"]["ell_primary"]
    X = n ** ell
    succ = dict((base[i], base[(i + 1) % n]) for i in range(n))
    target = _idx_to_word((X - 1) // 2, base, ell)
    decoy = tuple(succ[t] for t in target)
    hits = []
    predicted = []
    for start in range(X):
        x0 = _idx_to_word(start, base, ell)
        if x0[1:] == target[1:]:
            predicted.append(start)
        x = list(x0)
        found = (tuple(x) == target)
        for i in range(ell):
            if found:
                break
            for s in base:
                if s == x[i]:
                    continue
                y = list(x)
                y[i] = s
                if tuple(y) == target:
                    found = True
                    break
            if found:
                break
            x[i] = decoy[i]            # the deceptive objective's unique improver
        if found:
            hits.append(start)
    return {"start_points_swept": X,
            "hit_start_points": len(hits),
            "predicted_start_points": len(predicted),
            "predicted_window_size": n,
            "characterisation_exact": sorted(hits) == sorted(predicted),
            "hit_fraction_num": len(hits), "hit_fraction_den": X}


# ------------------------------------------------------------------------ main

def main():
    with open(FIXTURES_PATH, "r") as fh:
        fx = json.load(fh)
    rep1 = rep1_extreme_rank_check(fx)
    rep3 = rep3_by_enumeration(fx)
    rep2 = rep2_by_enumeration(fx)
    nov1 = nov1_by_construction(fx)
    nov2 = nov2_by_enumeration(fx)
    a = sd2a_exact(fx)
    b = sd2b_exhaustive(fx)
    c = sd2c_exhaustive(fx)

    ok = (rep1["sound"]
          and rep3["primary"]["band"] == "GUARANTEED_INCREASE"
          and rep3["primary"]["burden_increases"]
          and rep3["near_miss_hostile"]["band"] == "RANK_DECIDED"
          and rep2["parent_integers_reproduced_by_enumeration"]
          and nov1["all_add_zero_expressive_power"]
          and nov1["all_cycle_hostiles_detected"]
          and nov2["reachability_non_monotone_under_growth"]
          and a["agrees_with_closed_form"]
          and b["all_swept_bounds_respected"]
          and c["characterisation_exact"])

    out = {
        "schema": "GMI833DevelopmentalReuseOracleV1",
        "issue": 833,
        "section": "L",
        "package": "gmi-833-developmental-reuse-v1",
        "route": "B_literal_enumeration_and_exhaustive_sweep",
        "source_main": fx["source_main"],
        "REP_1_extreme_rank_check": rep1,
        "REP_3_by_enumeration": rep3,
        "REP_2_by_enumeration": rep2,
        "NOV_1_by_construction": nov1,
        "NOV_2_by_enumeration": nov2,
        "SD_2a_exact": a,
        "SD_2b_exhaustive": b,
        "SD_2c_exhaustive": c,
        "verdict": "ORACLE_AGREES" if ok else "ORACLE_DISAGREES",
    }
    sys.stdout.write(json.dumps(out, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
