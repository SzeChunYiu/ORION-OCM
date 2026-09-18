#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GMI #833 -- Route B: a materially independent enumeration oracle.

This module does NOT import derivation_v1 and does NOT use the closed form
Phi(n,l) = sum_{j=1..l} n**j anywhere.  Every quantity below is obtained by
walking the breadth-by-length enumeration of ACTUAL words one word at a time
with an explicit odometer, and by expanding ACTUAL macro programs under an
explicit macro-expansion semantics.  Burden endpoints are the positions of the
first and last enumerated word of a given length; minimal program lengths are
found by brute-force search over enumerated programs.

Agreement with Route A is measured only on the registered overlap scope that
enumeration actually reaches; the reachable scope is recorded per check.

Exact integers only.  No float.  Python 3.8, stdlib only.  Run:

    python3 -I -B oracle_derivation_v1.py [outpath]
    python3 -I -O -B oracle_derivation_v1.py [outpath]
"""

import json
import os
import sys

PACKAGE = "gmi-833-real-developmental-validation-v1"
ROUTE = "B_EXPLICIT_ENUMERATION"
ROUTE_A_RESULT_BASENAME = "DERIVATION_RESULT_V1.json"

# Registered enumeration budget: a single scan may enumerate at most this many
# words.  A check whose scan would exceed it is reported OUT_OF_BUDGET and is
# NOT silently computed by any closed form.
WORD_BUDGET_PER_SCAN = 1000000

# Registered overlap scope (must match Route A's route_b_overlap registration).
OVR_N_RANGE = (2, 4)
OVR_K_RANGE = (2, 3)
OVR_LMAX = 5
OVR_OI2_L_RANGE = (2, 6)
OVR_MSTAR_N_RANGE = (2, 2)


# ------------------------------------------------------------- enumeration


def enumerate_words(sigma, length):
    """Yield every word of `length` over symbols 0..sigma-1 in lexicographic
    order, as a list of symbol indices.  Explicit odometer; no formula."""
    if length == 0:
        yield []
        return
    w = [0] * length
    while True:
        yield list(w)
        i = length - 1
        while i >= 0:
            w[i] = w[i] + 1
            if w[i] < sigma:
                break
            w[i] = 0
            i = i - 1
        if i < 0:
            return


def scan(sigma, maxlen):
    """Walk the breadth-by-length enumeration counting ONE WORD AT A TIME.

    Returns {"first": {l: pos}, "last": {l: pos}, "count": {l: k},
             "total": total_words}.  `first[l]` / `last[l]` are the 1-based
    positions of the first and last word of length l in the global
    breadth-by-length order -- i.e. the two T3 burden endpoints for a target
    whose minimal program length is exactly l.
    """
    first = {}
    last = {}
    count = {}
    pos = 0
    l = 1
    while l <= maxlen:
        k = 0
        f = None
        for _w in enumerate_words(sigma, l):
            pos = pos + 1
            k = k + 1
            if f is None:
                f = pos
        first[l] = f
        last[l] = pos
        count[l] = k
        l = l + 1
    return {"first": first, "last": last, "count": count, "total": pos}


def scan_size(sigma, maxlen):
    """Number of words a scan(sigma, maxlen) would enumerate (budget check).

    Computed by repeated multiplication/addition of the per-length counts the
    enumerator would produce; it is a budget guard, never a source of any
    reported verdict.
    """
    total = 0
    p = 1
    l = 1
    while l <= maxlen:
        p = p * sigma
        total = total + p
        l = l + 1
    return total


_SCANS = {}


def get_scan(sigma, maxlen):
    key = "%d|%d" % (sigma, maxlen)
    have = _SCANS.get(key, None)
    if have is not None:
        return have
    # reuse a deeper scan over the same alphabet if one exists
    for k in sorted(_SCANS.keys()):
        s_, m_ = k.split("|")
        if int(s_) == sigma and int(m_) >= maxlen:
            return _SCANS[k]
    sc = scan(sigma, maxlen)
    _SCANS[key] = sc
    return sc


def endpoints(sigma, l):
    """(min_burden, max_burden) for a target of minimal program length l."""
    sc = get_scan(sigma, l)
    return (sc["first"][l], sc["last"][l])


def band_enum(sigma_old, l0, sigma_new, l1):
    """Three-way verdict from ENUMERATED burden endpoints."""
    o_lo, o_hi = endpoints(sigma_old, l0)
    n_lo, n_hi = endpoints(sigma_new, l1)
    if n_hi <= o_lo - 1:
        return "GUARANTEED_REDUCTION"
    if n_lo >= o_hi + 1:
        return "GUARANTEED_INCREASE"
    return "RANK_DECIDED"


# --------------------------------------------------- macro-expansion semantics


def expand(program, n_base, bodies):
    """Expand a program (list of symbol indices) to a list of base symbols.

    Symbols 0..n_base-1 are base; symbol n_base+i has body bodies[i] (a list of
    symbol indices, which may itself reference earlier macros).  Returns None on
    a cyclic dependency rather than recursing forever.
    """
    out = []
    stack = list(reversed(program))
    steps = 0
    limit = 100000
    while stack:
        steps = steps + 1
        if steps > limit:
            return None
        s = stack.pop()
        if s < n_base:
            out.append(s)
        else:
            body = bodies[s - n_base]
            i = len(body) - 1
            while i >= 0:
                stack.append(body[i])
                i = i - 1
    return out


def min_length_and_burden(n_base, bodies, target, maxlen):
    """Brute force: walk the breadth-by-length enumeration of PROGRAMS over the
    grammar's full symbol set and return (l*, burden) for the first program
    whose expansion equals `target`.  Returns (None, None) if unreached."""
    sigma = n_base + len(bodies)
    pos = 0
    l = 1
    while l <= maxlen:
        for prog in enumerate_words(sigma, l):
            pos = pos + 1
            if expand(prog, n_base, bodies) == target:
                return (l, pos)
        l = l + 1
    return (None, None)


def rank_to_word(sigma, l, rank):
    """The word at 0-based `rank` among the length-l words, by odometer walk."""
    i = 0
    for w in enumerate_words(sigma, l):
        if i == rank:
            return w
        i = i + 1
    return None


def burden_by_enumeration(sigma, word):
    """1-based position of `word` in the global breadth-by-length order,
    found by walking the enumeration and counting."""
    pos = 0
    l = 1
    while l <= len(word):
        for w in enumerate_words(sigma, l):
            pos = pos + 1
            if w == word:
                return pos
        l = l + 1
    return None


# ----------------------------------------------------------------- checks


def check_t3(route_a):
    """Independent verification of #897's T3 burden identity by enumeration."""
    reg = route_a.get("T3_burden_positions", {}) if route_a else {}
    rows = []
    agree = 0
    total = 0
    for key in sorted(reg.keys()):
        parts = key.split("|")
        sig = int(parts[0].split("=")[1])
        l = int(parts[1].split("=")[1])
        rank = int(parts[2].split("=")[1])
        if scan_size(sig, l) > WORD_BUDGET_PER_SCAN:
            rows.append({"cell": key, "status": "OUT_OF_BUDGET"})
            continue
        total = total + 1
        word = rank_to_word(sig, l, rank)
        pos = burden_by_enumeration(sig, word)
        lo, hi = endpoints(sig, l)
        ok = (pos == reg[key]) and (lo <= pos) and (pos <= hi)
        if ok:
            agree = agree + 1
        rows.append({"cell": key, "status": "CHECKED", "word": word,
                     "enumerated_burden": pos, "route_a_burden": reg[key],
                     "enumerated_length_endpoints": [lo, hi],
                     "agree": ok,
                     "rank_recovered": pos - lo})
    return {"check": "T3_BURDEN_IDENTITY",
            "note": ("burden = (number of enumerated words strictly shorter "
                     "than l*) + rank + 1, verified by counting words, not by "
                     "any closed form"),
            "cells_checked": total, "cells_agreeing": agree, "rows": rows}


def check_oi2(route_a):
    reg = route_a.get("OI-2_gamma1_verdicts", {}) if route_a else {}
    rows = []
    agree = 0
    total = 0
    reduction_cells = 0
    n = OVR_N_RANGE[0]
    while n <= OVR_N_RANGE[1]:
        l0 = OVR_OI2_L_RANGE[0]
        while l0 <= OVR_OI2_L_RANGE[1]:
            key = "n=%d|l0=%d" % (n, l0)
            if (scan_size(n, l0) > WORD_BUDGET_PER_SCAN
                    or scan_size(n + 1, l0 - 1) > WORD_BUDGET_PER_SCAN):
                rows.append({"cell": key, "status": "OUT_OF_BUDGET"})
                l0 = l0 + 1
                continue
            v = band_enum(n, l0, n + 1, l0 - 1)
            if v == "GUARANTEED_REDUCTION":
                reduction_cells = reduction_cells + 1
            total = total + 1
            ok = (key in reg) and (reg[key] == v)
            if ok:
                agree = agree + 1
            rows.append({"cell": key, "status": "CHECKED",
                         "enumerated_verdict": v,
                         "route_a_verdict": reg.get(key, None), "agree": ok,
                         "endpoints_G0": list(endpoints(n, l0)),
                         "endpoints_G1": list(endpoints(n + 1, l0 - 1))})
            l0 = l0 + 1
        n = n + 1
    return {"check": "OI-2_GAMMA1_NEVER_GUARANTEED_REDUCTION",
            "cells_checked": total, "cells_agreeing": agree,
            "guaranteed_reduction_cells_found": reduction_cells,
            "claim_upheld_by_enumeration": reduction_cells == 0,
            "rows": rows}


def lstar_enum(n, cap):
    """Least l with band_enum(n,l -> n+1,l) == GUARANTEED_INCREASE, or None."""
    l = 1
    while l <= cap:
        if (scan_size(n, l) > WORD_BUDGET_PER_SCAN
                or scan_size(n + 1, l) > WORD_BUDGET_PER_SCAN):
            return None
        if band_enum(n, l, n + 1, l) == "GUARANTEED_INCREASE":
            return l
        l = l + 1
    return None


def mstar_enum(n, cap):
    """Least l>=2 with band_enum(n,l -> n+1,l-1) == GUARANTEED_INCREASE."""
    l = 2
    while l <= cap:
        if (scan_size(n, l) > WORD_BUDGET_PER_SCAN
                or scan_size(n + 1, l - 1) > WORD_BUDGET_PER_SCAN):
            return None
        if band_enum(n, l, n + 1, l - 1) == "GUARANTEED_INCREASE":
            return l
        l = l + 1
    return None


def check_oi3(route_a):
    regL = route_a.get("OI-3_Lstar", {}) if route_a else {}
    regM = route_a.get("OI-3_Mstar", {}) if route_a else {}
    rowsL = []
    rowsM = []
    agree = 0
    total = 0
    n = OVR_N_RANGE[0]
    while n <= OVR_N_RANGE[1]:
        key = "n=%d" % n
        v = lstar_enum(n, 24)
        if v is None:
            rowsL.append({"cell": key, "status": "OUT_OF_BUDGET_OR_UNREACHED"})
        else:
            total = total + 1
            ok = (key in regL) and (regL[key] == v)
            if ok:
                agree = agree + 1
            rowsL.append({"cell": key, "status": "CHECKED",
                          "enumerated_Lstar": v,
                          "route_a_Lstar": regL.get(key, None), "agree": ok,
                          "gamma0_verdict_at_Lstar":
                              band_enum(n, v, n + 1, v),
                          "gamma0_verdict_at_Lstar_minus_1":
                              band_enum(n, v - 1, n + 1, v - 1) if v >= 2 else None,
                          "gamma1_verdict_at_Lstar":
                              band_enum(n, v, n + 1, v - 1) if v >= 2 else None})
        n = n + 1
    n = OVR_MSTAR_N_RANGE[0]
    while n <= OVR_MSTAR_N_RANGE[1]:
        key = "n=%d" % n
        v = mstar_enum(n, 24)
        if v is None:
            rowsM.append({"cell": key, "status": "OUT_OF_BUDGET_OR_UNREACHED"})
        else:
            total = total + 1
            ok = (key in regM) and (regM[key] == v)
            if ok:
                agree = agree + 1
            rowsM.append({"cell": key, "status": "CHECKED",
                          "enumerated_Mstar": v,
                          "route_a_Mstar": regM.get(key, None), "agree": ok,
                          "gamma1_verdict_at_Mstar":
                              band_enum(n, v, n + 1, v - 1),
                          "gamma1_verdict_at_Mstar_minus_1":
                              band_enum(n, v - 1, n + 1, v - 2) if v >= 3 else None})
        n = n + 1
    return {"check": "OI-3_LSTAR_AND_MSTAR",
            "reachable_scope_note": (
                "Lstar is enumerated for n in %d..%d. Mstar is enumerated only "
                "for n in %d..%d: Mstar(3)=11 would need sum_{j<=11} 4**j = "
                "5592404 enumerated words, above the registered budget of %d. "
                "No out-of-budget cell is filled in by any closed form."
                % (OVR_N_RANGE[0], OVR_N_RANGE[1], OVR_MSTAR_N_RANGE[0],
                   OVR_MSTAR_N_RANGE[1], WORD_BUDGET_PER_SCAN)),
            "cells_checked": total, "cells_agreeing": agree,
            "Lstar_rows": rowsL, "Mstar_rows": rowsM}


def check_lf1(route_a):
    reg = route_a.get("LF-1_verdicts", {}) if route_a else {}
    counts = {"LIBRARY_GUARANTEED_BETTER": 0, "LIBRARY_GUARANTEED_WORSE": 0,
              "RANK_DECIDED": 0, "BAND_COLLISION": 0}
    agree = 0
    total = 0
    skipped = 0
    collisions = 0
    gamma0 = {"LIBRARY_GUARANTEED_BETTER": 0, "LIBRARY_GUARANTEED_WORSE": 0,
              "RANK_DECIDED": 0, "BAND_COLLISION": 0}
    disagreements = []
    n = OVR_N_RANGE[0]
    while n <= OVR_N_RANGE[1]:
        k = OVR_K_RANGE[0]
        while k <= OVR_K_RANGE[1]:
            lj = 1
            while lj <= OVR_LMAX:
                lL = 1
                while lL <= lj:
                    key = "n=%d|k=%d|lL=%d|lj=%d" % (n, k, lL, lj)
                    if (scan_size(n + 1, lj) > WORD_BUDGET_PER_SCAN
                            or scan_size(n + k, lL) > WORD_BUDGET_PER_SCAN):
                        skipped = skipped + 1
                        lL = lL + 1
                        continue
                    sep_lo, sep_hi = endpoints(n + 1, lj)
                    lib_lo, lib_hi = endpoints(n + k, lL)
                    better = lib_hi <= sep_lo - 1
                    worse = lib_lo >= sep_hi + 1
                    if better and worse:
                        v = "BAND_COLLISION"
                        collisions = collisions + 1
                    elif better:
                        v = "LIBRARY_GUARANTEED_BETTER"
                    elif worse:
                        v = "LIBRARY_GUARANTEED_WORSE"
                    else:
                        v = "RANK_DECIDED"
                    counts[v] += 1
                    if lL == lj:
                        gamma0[v] += 1
                    total = total + 1
                    if key in reg and reg[key] == v:
                        agree = agree + 1
                    else:
                        disagreements.append({"cell": key,
                                              "enumerated": v,
                                              "route_a": reg.get(key, None)})
                    lL = lL + 1
                lj = lj + 1
            k = k + 1
        n = n + 1
    return {"check": "LF-1_THREE_WAY_BAND",
            "cells_checked": total, "cells_agreeing": agree,
            "cells_out_of_budget": skipped,
            "enumerated_counts": counts,
            "band_collisions": collisions,
            "mutual_exclusivity_upheld": collisions == 0,
            "gamma0_subcensus_counts": gamma0,
            "disagreements": disagreements}


def check_lf4(route_a):
    reg = route_a.get("LF-4_gammastar", {}) if route_a else {}
    agree = 0
    total = 0
    rows = {}
    below_two = []
    n = OVR_N_RANGE[0]
    while n <= OVR_N_RANGE[1]:
        k = OVR_K_RANGE[0]
        while k <= OVR_K_RANGE[1]:
            lj = 2
            while lj <= OVR_LMAX:
                key = "n=%d|k=%d|lj=%d" % (n, k, lj)
                sep_lo, _sep_hi = endpoints(n + 1, lj)
                gs = None
                g = 0
                while g <= lj - 1:
                    lib_hi = endpoints(n + k, lj - g)[1]
                    if lib_hi <= sep_lo - 1:
                        gs = g
                        break
                    g = g + 1
                rows[key] = gs
                if gs is not None and gs < 2:
                    below_two.append(key)
                total = total + 1
                if key in reg and reg[key] == gs:
                    agree = agree + 1
                lj = lj + 1
            k = k + 1
        n = n + 1
    undefined = []
    for key in sorted(rows.keys()):
        if rows[key] is None:
            undefined.append(key)
    return {"check": "LF-4_GAMMASTAR",
            "cells_checked": total, "cells_agreeing": agree,
            "enumerated_table": rows,
            "undefined_cells": undefined,
            "undefined_count": len(undefined),
            "gammastar_below_two_cells": below_two,
            "gammastar_below_two_count": len(below_two)}


def check_oi1(route_a):
    """Re-derive W1's Theta_inv from ACTUAL macro expansion + enumeration."""
    reg = route_a.get("OI-1_W1", None) if route_a else None
    n_base = 2                       # base alphabet {a, b} = {0, 1}
    macro_body = [0, 1, 0, 1]        # m -> abab
    target = [0, 1, 0, 1, 0, 1, 0, 1]   # abababab
    l0, b0 = min_length_and_burden(n_base, [], target, 9)
    l1, b1 = min_length_and_burden(n_base, [macro_body], target, 9)
    theta = None
    saving = None
    ok_l = False
    if l0 is not None and l1 is not None:
        old_lo, _old_hi = endpoints(n_base, l0)
        _new_lo, new_hi = endpoints(n_base + 1, l1)
        saving = old_lo - new_hi
        theta = saving                # single target, weight 1, no tax term
        ok_l = True
    charge = None
    pays = None
    if reg is not None and theta is not None:
        charge = reg["D"] + reg["body_len"] + reg["kappa"]
        pays = bool(charge < theta)
    agree_l0 = (reg is not None and l0 == reg["l0"])
    agree_l1 = (reg is not None and l1 == reg["l1"])
    agree_theta = (reg is not None and theta is not None
                   and ("%d/1" % theta) == reg["Theta_inv"])
    agree_pays = (reg is not None and pays == reg["strictly_pays"])
    n_agree = 0
    for x in (agree_l0, agree_l1, agree_theta, agree_pays):
        if x:
            n_agree = n_agree + 1
    return {"check": "OI-1_THETA_INV_ON_W1",
            "base_alphabet_size": n_base,
            "macro_body": macro_body, "target": target,
            "enumerated_l0_under_G0": l0,
            "enumerated_burden_of_target_under_G0": b0,
            "enumerated_l1_under_G0_plus_m": l1,
            "enumerated_burden_of_target_under_G0_plus_m": b1,
            "enumerated_min_burden_at_l0": endpoints(n_base, l0)[0] if ok_l else None,
            "enumerated_max_burden_at_l1": endpoints(n_base + 1, l1)[1] if ok_l else None,
            "enumerated_Saving": saving,
            "enumerated_Theta_inv": theta,
            "total_charge": charge,
            "enumerated_strictly_pays": pays,
            "route_a": reg,
            "cells_checked": 4, "cells_agreeing": n_agree,
            "agreements": {"l0": agree_l0, "l1": agree_l1,
                           "Theta_inv": agree_theta, "strictly_pays": agree_pays}}


def check_oi4(route_a):
    reg = route_a.get("OI-4_witness_verdicts", []) if route_a else []
    rows = []
    agree = 0
    total = 0
    for w in reg:
        n = w["n"]
        l0 = w["l0"]
        l1 = w["l1"]
        if (scan_size(n, l0) > WORD_BUDGET_PER_SCAN
                or scan_size(n + 1, l1) > WORD_BUDGET_PER_SCAN):
            rows.append({"label": w["label"], "status": "OUT_OF_BUDGET"})
            continue
        v = band_enum(n, l0, n + 1, l1)
        total = total + 1
        ok = (v == w["verdict"])
        if ok:
            agree = agree + 1
        rows.append({"label": w["label"], "status": "CHECKED", "n": n,
                     "l0": l0, "l1": l1,
                     "endpoints_G0": list(endpoints(n, l0)),
                     "endpoints_G0_plus_o": list(endpoints(n + 1, l1)),
                     "enumerated_verdict": v, "route_a_verdict": w["verdict"],
                     "agree": ok})
    return {"check": "OI-4_WITNESS_VERDICTS",
            "cells_checked": total, "cells_agreeing": agree, "rows": rows}


def check_hostiles():
    """Independent enumeration evidence for the gamma=0 hostiles H1 and H2."""
    h1_rows = []
    h1_bad = 0
    n = OVR_N_RANGE[0]
    while n <= OVR_N_RANGE[1]:
        l0 = 1
        while l0 <= OVR_LMAX:
            lo, hi = endpoints(n, l0)
            nlo, nhi = endpoints(n + 1, l0)
            # a gamma = 0 operator can never strictly reduce the worst case
            saving = lo - nhi
            if saving > 0:
                h1_bad = h1_bad + 1
            h1_rows.append({"n": n, "l0": l0, "endpoints_G0": [lo, hi],
                            "endpoints_G0_plus_o": [nlo, nhi],
                            "rank_free_saving": saving})
            l0 = l0 + 1
        n = n + 1
    h2_bad = 0
    h2_cells = 0
    n = OVR_N_RANGE[0]
    while n <= OVR_N_RANGE[1]:
        k = OVR_K_RANGE[0]
        while k <= OVR_K_RANGE[1]:
            lj = 1
            while lj <= OVR_LMAX:
                sep_lo, _ = endpoints(n + 1, lj)
                _, lib_hi = endpoints(n + k, lj)
                h2_cells = h2_cells + 1
                if lib_hi <= sep_lo - 1:
                    h2_bad = h2_bad + 1
                lj = lj + 1
            k = k + 1
        n = n + 1
    return {"check": "HOSTILE_GAMMA0_FACTS_BY_ENUMERATION",
            "H1_cells": len(h1_rows),
            "H1_cells_with_positive_rank_free_saving": h1_bad,
            "H1_claim_upheld": h1_bad == 0,
            "H1_rows": h1_rows,
            "H2_gamma0_cells": h2_cells,
            "H2_gamma0_cells_guaranteed_better": h2_bad,
            "H2_claim_upheld": h2_bad == 0}


# --------------------------------------------------------------------- main


def load_route_a(here):
    path = os.path.join(here, ROUTE_A_RESULT_BASENAME)
    if not os.path.exists(path):
        return (None, "ROUTE_A_RESULT_ABSENT")
    fh = open(path, "r")
    obj = json.load(fh)
    fh.close()
    return (obj.get("route_b_overlap", None), "ROUTE_A_RESULT_LOADED")


def build(here):
    route_a, status = load_route_a(here)
    checks = [check_t3(route_a), check_oi1(route_a), check_oi2(route_a),
              check_oi3(route_a), check_oi4(route_a), check_lf1(route_a),
              check_lf4(route_a), check_hostiles()]
    per_check = {}
    tot_checked = 0
    tot_agree = 0
    for c in checks:
        name = c["check"]
        ck = c.get("cells_checked", None)
        ag = c.get("cells_agreeing", None)
        per_check[name] = {"cells_checked": ck, "cells_agreeing": ag}
        if ck is not None and ag is not None:
            tot_checked = tot_checked + ck
            tot_agree = tot_agree + ag
    results = {}
    for c in checks:
        results[c["check"]] = c
    return {
        "package": PACKAGE,
        "route": ROUTE,
        "independence": (
            "This module does not import derivation_v1 and never evaluates "
            "Phi(n,l). Burden endpoints are the positions of the first and "
            "last ENUMERATED word of each length; minimal program lengths come "
            "from brute-force search over enumerated macro programs."),
        "route_a_status": status,
        "word_budget_per_scan": WORD_BUDGET_PER_SCAN,
        "registered_overlap_scope": {
            "n_range": list(OVR_N_RANGE), "k_range": list(OVR_K_RANGE),
            "lmax": OVR_LMAX, "oi2_l_range": list(OVR_OI2_L_RANGE),
            "mstar_n_range": list(OVR_MSTAR_N_RANGE)},
        "two_route_agreement_per_check": per_check,
        "two_route_cells_checked": tot_checked,
        "two_route_cells_agreeing": tot_agree,
        "two_route_full_agreement": tot_checked == tot_agree and tot_checked > 0,
        "results": results,
        "arithmetic": "EXACT_INT_ONLY__NO_FLOAT",
    }


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    if len(argv) > 1:
        outpath = argv[1]
    else:
        outpath = os.path.join(here, "ORACLE_DERIVATION_RESULT_V1.json")
    obj = build(here)
    text = json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=True)
    fh = open(outpath, "w")
    fh.write(text)
    fh.write("\n")
    fh.close()
    sys.stdout.write("WROTE %s bytes=%d\n" % (outpath, len(text) + 1))
    sys.stdout.write("two_route %d/%d full=%s\n"
                     % (obj["two_route_cells_agreeing"],
                        obj["two_route_cells_checked"],
                        obj["two_route_full_agreement"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
