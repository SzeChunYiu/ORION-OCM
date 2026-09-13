#!/usr/bin/env python3
"""RV-377-130 .. RV-377-134 -- GMI channel capability law family harness.

Extends the RV-377-123 / RV-377-124 world (gmi_ti_capability_law.py). Same world family:
W uniform on L bits, drawn AFTER the machine is frozen; development D reveals r distinct
indices; the query is an index (or, for the verifier law, an aligned m-bit block). Every
law below is a statement about a CHANNEL CLASS -- the set of all machines whose only access
to W runs through the named channels -- and bounds the EXPECTATION of accuracy over
independent protected draws of W (the RV-377-123 lesson: predicates are stated over the
expectation across draws, with the standard error taken across draws).

Laws (channel-law index CL-k; the tasking's TI-k labels are aliases, and the acquisition
theorem document already uses "TI-3" for a different statement, so CL-k is the primary id):

  CL-1  one channel           acc <= 1/2 + r/(2L)                          (RV-377-123)
  CL-2  two channels          acc <= 1 - (1 - r/L)(1 - p)/2                (RV-377-124)
  CL-3  noisy development     acc <= (r/L) max(m_k(q), 1 - m_k(q)) + (1 - r/L)/2
  CL-4  bounded state         acc <= (r/L)(1 - d*(r, s)) + (1 - r/L)/2
  CL-5  structured world      E[acc | S] = 1/2 + f_G(S)/2,  f_G(S) = span fraction
  CL-6  verifier channel      acc <= sum_u P_hyp(u) min(1, k / 2^u)         (m-bit blocks)
  CL-7  external store        acc <= 1 - (1 - r/L)(1 - c rho)/2

Each closed form is a pure function here so the boundary-case lattice can be unit-tested.
The pre-registered predicates are coded in adjudicate_* and frozen with the docs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import statistics
import sys
import time
from math import comb

L_DEFAULT = 64
Z_PRIMARY = 4.0  # pre-registered falsifier threshold, in s.e. across independent W draws
Z_DIAG = 3.0     # diagnostic threshold; expected null count reported alongside

# =====================================================================================
# closed forms
# =====================================================================================


def ti1(L: int, r: int) -> float:
    """CL-1 (RV-377-123)."""
    return 0.5 + r / (2.0 * L)


def ti2(L: int, r: int, p: float) -> float:
    """CL-2 (RV-377-124)."""
    return 1.0 - (1.0 - r / L) * (1.0 - p) / 2.0


# ---- CL-3 noisy development -----------------------------------------------------------

def majority_correct(k: int, q: float) -> float:
    """P(majority over k independent copies, each flipped w.p. q, equals the true bit);
    ties count 1/2 (coin)."""
    p = 0.0
    for f in range(k + 1):
        pf = comb(k, f) * (q ** f) * ((1.0 - q) ** (k - f))
        if 2 * f < k:
            p += pf
        elif 2 * f == k:
            p += 0.5 * pf
    return p


def unanimity_correct(k: int, q: float) -> float:
    """success of 'trust only a unanimous set of copies, else coin'."""
    all_ok = (1.0 - q) ** k
    all_bad = q ** k
    return all_ok + 0.5 * (1.0 - all_ok - all_bad)


def ceiling3(L: int, r: int, q: float, k: int = 1) -> float:
    """CL-3 ceiling: a machine that knows q may invert the majority when q > 1/2."""
    m = majority_correct(k, q)
    return (r / L) * max(m, 1.0 - m) + (1.0 - r / L) / 2.0


def naive3(L: int, r: int, q: float, k: int = 1) -> float:
    """the 'trust the (majority of the) revealed copies' line -- the tasking's proposed form
    at k = 1; equals ceiling3 iff q <= 1/2."""
    return (r / L) * majority_correct(k, q) + (1.0 - r / L) / 2.0


def first_copy_line(L: int, r: int, q: float) -> float:
    return (r / L) * (1.0 - q) + (1.0 - r / L) / 2.0


def unanimity_line(L: int, r: int, q: float, k: int) -> float:
    return (r / L) * unanimity_correct(k, q) + (1.0 - r / L) / 2.0


# ---- CL-4 bounded state ---------------------------------------------------------------

def sphere_covering_distortion(r: int, s: int) -> float:
    """Lower bound on the expected per-bit Hamming distortion of ANY code with 2^s words on
    r uniform bits (fill Hamming balls greedily: each codeword owns at most C(r,t) strings at
    distance t). Tight whenever a perfect code exists (repetition s=1 with r odd; Hamming
    r = 2^m - 1, s = r - m; even-weight s = r - 1). Zero for s >= r."""
    if r == 0 or s >= r:
        return 0.0
    n_words = 2 ** s
    remaining = 2 ** r
    total = 0
    t = 0
    while remaining > 0:
        cnt = min(n_words * comb(r, t), remaining)
        total += t * cnt
        remaining -= cnt
        t += 1
    return total / (r * 2 ** r)


def ceiling4(L: int, r: int, s: int) -> float:
    """CL-4 corrected ceiling (rate-distortion converse)."""
    return (r / L) * (1.0 - sphere_covering_distortion(r, s)) + (1.0 - r / L) / 2.0


def naive4(L: int, r: int, s: int) -> float:
    """the tasking's proposed form: keep min(r, s) bits exactly, coin elsewhere.
    A LINE attained by truncation, NOT a ceiling."""
    return 0.5 + min(r, s) / (2.0 * L)


def flip_line(L: int, r: int, s: int) -> float:
    return 0.5 - min(r, s) / (2.0 * L)


def hamming_m(r: int) -> int | None:
    """m with r = 2^m - 1, else None."""
    m = (r + 1).bit_length() - 1
    return m if (2 ** m - 1 == r and m >= 2) else None


# ---- CL-5 structured world ------------------------------------------------------------

def ceiling5_rep_closed(L: int, H: int, r: int) -> float:
    """G_rep = L/H stacked copies of I_H: a direction is covered iff any of its L/H copies is
    revealed, so E[span fraction] = 1 - C(L - L/H, r) / C(L, r)."""
    copies = L // H
    return 0.5 + (1.0 - comb(L - copies, r) / comb(L, r)) / 2.0


# ---- CL-6 verifier channel ------------------------------------------------------------

def p_unrevealed_in_block(L: int, r: int, m: int, u: int) -> float:
    """P(an aligned m-block has exactly u unrevealed bits) -- hypergeometric."""
    rev_in = m - u
    if rev_in < 0 or rev_in > r or r - rev_in > L - m:
        return 0.0
    return comb(m, rev_in) * comb(L - m, r - rev_in) / comb(L, r)


def ceiling6(L: int, r: int, m: int, k: int) -> float:
    return sum(p_unrevealed_in_block(L, r, m, u) * min(1.0, k / 2 ** u) for u in range(m + 1))


def random_k_line(m: int, k: int) -> float:
    return min(1.0, k / 2 ** m)


# ---- CL-7 external store --------------------------------------------------------------

def ceiling7(L: int, r: int, c: float, rho: float) -> float:
    return 1.0 - (1.0 - r / L) * (1.0 - c * rho) / 2.0


def store_only_line(c: float, rho: float) -> float:
    return 0.5 + c * rho / 2.0


def store_first_line(L: int, r: int, c: float, rho: float) -> float:
    return ceiling7(L, r, c, rho) - (r / L) * c * (1.0 - rho) / 2.0


# =====================================================================================
# common machinery
# =====================================================================================


def draw_seed(law: str, cell_key: str, d: int) -> int:
    h = hashlib.sha256(f"{law}|{cell_key}|{d}".encode()).hexdigest()
    return int(h[:16], 16)


def base_world(L: int, r: int, rng: random.Random):
    W = [rng.randrange(2) for _ in range(L)]
    idx = list(range(L))
    rng.shuffle(idx)
    revealed = idx[:r]  # order = order of revelation (matters for truncation)
    return W, revealed


def evaluate(world, machine, rng: random.Random, n_rep: int, queries):
    hit = 0
    n = 0
    for _ in range(n_rep):
        for q in queries:
            if machine(world, q, rng):
                hit += 1
            n += 1
    return hit / n


def summarize(pairs):
    """pairs = [(acc_d, pred_d)] over draws -> stats dict."""
    n = len(pairs)
    accs = [a for a, _ in pairs]
    preds = [p for _, p in pairs]
    diffs = [a - p for a, p in pairs]
    mean_acc = statistics.fmean(accs)
    sd_acc = statistics.stdev(accs) if n > 1 else 0.0
    mean_pred = statistics.fmean(preds)
    sd_pred = statistics.stdev(preds) if n > 1 else 0.0
    mean_diff = statistics.fmean(diffs)
    sd_diff = statistics.stdev(diffs) if n > 1 else 0.0
    se_diff = sd_diff / math.sqrt(n)
    z = (mean_diff / se_diff) if se_diff > 0 else (0.0 if abs(mean_diff) < 1e-12 else float("inf") * (1 if mean_diff > 0 else -1))
    return {
        "n_draws": n,
        "mean_acc": round(mean_acc, 6),
        "sd_acc": round(sd_acc, 6),
        "se_acc": round(sd_acc / math.sqrt(n), 6),
        "mean_pred": round(mean_pred, 6),
        "sd_pred": round(sd_pred, 6),
        "mean_diff": round(mean_diff, 6),
        "se_diff": round(se_diff, 6),
        "z": (round(z, 3) if math.isfinite(z) else str(z)),
        "exceeds_primary": bool(mean_diff > Z_PRIMARY * se_diff + 1e-12),
        "meets_primary": bool(abs(mean_diff) <= Z_PRIMARY * se_diff + 1e-12),
        "exceeds_diag": bool(mean_diff > Z_DIAG * se_diff + 1e-12),
        "below_primary": bool(mean_diff < -Z_PRIMARY * se_diff - 1e-12),
    }


def rel_to(cell_pairs, line_values):
    """re-summarize accs against a different reference line (per-draw list or scalar)."""
    if isinstance(line_values, (int, float)):
        line_values = [line_values] * len(cell_pairs)
    return summarize([(a, lv) for (a, _), lv in zip(cell_pairs, line_values)])


# =====================================================================================
# CL-3 noisy development
# =====================================================================================


def world3(L, r, q, k, rng):
    W, revealed = base_world(L, r, rng)
    dev = {}
    for i in revealed:
        dev[i] = [W[i] ^ (1 if rng.random() < q else 0) for _ in range(k)]
    return {"W": W, "dev": dev, "q": q, "k": k}


def m3_trust(w, i, rng):
    """trust the first copy (k = 1: the naive table)."""
    if i in w["dev"]:
        return w["dev"][i][0] == w["W"][i]
    return rng.randrange(2) == w["W"][i]


def m3_know_noise(w, i, rng):
    """Bayes-optimal: majority of copies, inverted when q > 1/2, coin on ties."""
    if i in w["dev"]:
        copies = w["dev"][i]
        ones = sum(copies)
        if 2 * ones == len(copies):
            guess = rng.randrange(2)
        else:
            guess = 1 if 2 * ones > len(copies) else 0
            if w["q"] > 0.5:
                guess ^= 1
        return guess == w["W"][i]
    return rng.randrange(2) == w["W"][i]


def m3_majority(w, i, rng):
    """plain majority, never inverts (= trust at k = 1)."""
    if i in w["dev"]:
        copies = w["dev"][i]
        ones = sum(copies)
        if 2 * ones == len(copies):
            guess = rng.randrange(2)
        else:
            guess = 1 if 2 * ones > len(copies) else 0
        return guess == w["W"][i]
    return rng.randrange(2) == w["W"][i]


def m3_unanimous(w, i, rng):
    """deliberately wasteful: trusts only a unanimous set of copies, else coin."""
    if i in w["dev"]:
        copies = w["dev"][i]
        if all(c == copies[0] for c in copies):
            return copies[0] == w["W"][i]
        return rng.randrange(2) == w["W"][i]
    return rng.randrange(2) == w["W"][i]


def m3_ignore_dev(w, i, rng):
    return rng.randrange(2) == w["W"][i]


def run_cl3(L, n_draws, n_rep, log):
    law = "CL3"
    cells = []
    single_q = [0.0, 0.1, 0.25, 0.4, 0.5, 0.75, 1.0]
    single_r = [0, 16, 32, 48, 64]
    single_machines = {"trust": m3_trust, "know_noise": m3_know_noise, "ignore_dev": m3_ignore_dev}
    multi_q = [0.1, 0.25, 0.4]
    multi_k = [1, 3, 5]
    multi_r = [16, 32, 48]
    multi_machines = {"majority": m3_majority, "first_copy": m3_trust, "unanimous": m3_unanimous}
    grid = [("single", q, 1, r, single_machines) for q in single_q for r in single_r]
    grid += [("multi", q, k, r, multi_machines) for q in multi_q for k in multi_k for r in multi_r]
    queries = list(range(L))
    for part, q, k, r, machines in grid:
        cell_key = f"{part}|q={q}|k={k}|r={r}"
        worlds = [world3(L, r, q, k, random.Random(draw_seed(law, cell_key, d))) for d in range(n_draws)]
        ceil = ceiling3(L, r, q, k)
        for mname, mfn in machines.items():
            pairs = []
            for d, w in enumerate(worlds):
                rng = random.Random(draw_seed(law, cell_key + "|" + mname, d) ^ 0x5EED)
                pairs.append((evaluate(w, mfn, rng, n_rep, queries), ceil))
            rec = {"part": part, "q": q, "k": k, "r": r, "machine": mname, "ceiling": round(ceil, 6)}
            rec["vs_ceiling"] = summarize(pairs)
            if mname in ("trust", "first_copy"):
                rec["line"] = round(first_copy_line(L, r, q), 6)
                rec["vs_line"] = rel_to(pairs, rec["line"])
            elif mname == "majority":
                rec["line"] = round(naive3(L, r, q, k), 6)
                rec["vs_line"] = rel_to(pairs, rec["line"])
            elif mname == "unanimous":
                rec["line"] = round(unanimity_line(L, r, q, k), 6)
                rec["vs_line"] = rel_to(pairs, rec["line"])
            elif mname == "ignore_dev":
                rec["line"] = 0.5
                rec["vs_line"] = rel_to(pairs, 0.5)
            rec["vs_half"] = rel_to(pairs, 0.5)
            rec["vs_ti1"] = rel_to(pairs, ti1(L, r))
            cells.append(rec)
            log(f"CL3 {cell_key} {mname:11s} acc={rec['vs_ceiling']['mean_acc']:.4f} ceil={ceil:.4f} z={rec['vs_ceiling']['z']}")
    return cells


def adjudicate_cl3(cells):
    out = {}
    single = [c for c in cells if c["part"] == "single"]
    multi = [c for c in cells if c["part"] == "multi"]
    viol = [c for c in cells if c["vs_ceiling"]["exceeds_primary"]]
    out["N1_no_machine_exceeds_ceiling"] = {"status": "CONFIRMED" if not viol else "FALSIFIED",
                                          "violations": [(c["part"], c["q"], c["k"], c["r"], c["machine"]) for c in viol],
                                          "diag_3se_count": sum(c["vs_ceiling"]["exceeds_diag"] for c in cells),
                                          "diag_3se_null_expectation": round(0.00135 * len(cells), 3)}
    kn = [c for c in single if c["machine"] == "know_noise"]
    short = [c for c in kn if not c["vs_ceiling"]["meets_primary"]]
    out["N2_know_noise_tight_at_every_q_incl_above_half"] = {"status": "CONFIRMED" if not short else "FALSIFIED",
                                                            "shortfalls": [(c["q"], c["r"]) for c in short]}
    tr = [c for c in single if c["machine"] == "trust"]
    off = [c for c in tr if not c["vs_line"]["meets_primary"]]
    below = [c for c in tr if c["q"] > 0.5 and c["r"] >= 16]
    not_below = [c for c in below if not c["vs_half"]["below_primary"]]
    out["N3_trust_on_naive_line_and_below_chance_for_q_above_half"] = {
        "status": "CONFIRMED" if (not off and not not_below) else "FALSIFIED",
        "off_line": [(c["q"], c["r"]) for c in off], "not_below_chance": [(c["q"], c["r"]) for c in not_below]}
    half = [c for c in single if c["q"] == 0.5]
    bad = [c for c in half if not c["vs_half"]["meets_primary"]]
    out["N4_q_half_collapses_to_chance_for_all"] = {"status": "CONFIRMED" if not bad else "FALSIFIED",
                                                   "off": [(c["machine"], c["r"]) for c in bad]}
    q0 = [c for c in single if c["q"] == 0.0 and c["machine"] in ("trust", "know_noise")]
    bad0 = [c for c in q0 if not c["vs_ti1"]["meets_primary"]]
    out["N5_q0_reproduces_TI1"] = {"status": "CONFIRMED" if not bad0 else "FALSIFIED", "off": [(c["machine"], c["r"]) for c in bad0]}
    maj = [c for c in multi if c["machine"] == "majority"]
    fc = [c for c in multi if c["machine"] == "first_copy"]
    un = [c for c in multi if c["machine"] == "unanimous"]
    bad_maj = [c for c in maj if not c["vs_ceiling"]["meets_primary"]]
    bad_fc = [c for c in fc if not c["vs_line"]["meets_primary"]]
    bad_un = [c for c in un if not c["vs_line"]["meets_primary"]]
    un_short = [c for c in un if c["k"] >= 3 and not c["vs_ceiling"]["below_primary"]]
    out["N6_majority_tight_first_copy_flat_in_k_unanimity_on_its_line_and_below_ceiling"] = {
        "status": "CONFIRMED" if not (bad_maj or bad_fc or bad_un or un_short) else "FALSIFIED",
        "majority_off": [(c["q"], c["k"], c["r"]) for c in bad_maj],
        "first_copy_off": [(c["q"], c["k"], c["r"]) for c in bad_fc],
        "unanimity_off_line": [(c["q"], c["k"], c["r"]) for c in bad_un],
        "unanimity_not_below_ceiling": [(c["q"], c["k"], c["r"]) for c in un_short]}
    return out


# =====================================================================================
# CL-4 bounded state
# =====================================================================================


def world4(L, r, rng):
    W, revealed = base_world(L, r, rng)
    return {"W": W, "revealed": revealed, "r": r}


def _hamming_quantize(bits, m):
    """nearest codeword of the Hamming(2^m-1, 2^m-1-m) code (syndrome decoding)."""
    r = len(bits)
    syn = 0
    for pos in range(1, r + 1):
        if bits[pos - 1]:
            syn ^= pos
    c = list(bits)
    if syn != 0:
        c[syn - 1] ^= 1
    return c


def make_m4(kind, s):
    """returns machine using at most s bits of world-information state (state built once per
    world and cached on the world dict)."""

    def state(w):
        key = ("state", kind, s)
        if key in w:
            return w[key]
        rev = w["revealed"]
        bits = [w["W"][i] for i in rev]
        r = len(rev)
        if kind == "truncate":
            keep = min(r, s)
            st = {rev[j]: bits[j] for j in range(keep)}                      # keep bits exactly
        elif kind == "truncate_flip":
            keep = min(r, s)
            st = {rev[j]: bits[j] ^ 1 for j in range(keep)}                  # wrong about the world
        elif kind == "repetition":
            ones = sum(bits)
            maj = 1 if 2 * ones > r else (0 if 2 * ones < r else None)
            st = {i: maj for i in rev}                                       # 1 bit of state
        elif kind == "parity_store":
            par = sum(bits) % 2
            st = {"parity": par, "rev": set(rev)}                            # 1 bit, wrong statistic
        elif kind == "even_weight":
            c = list(bits)
            if sum(c) % 2 == 1:
                c[-1] ^= 1
            st = {rev[j]: c[j] for j in range(r)}                            # r-1 bits
        elif kind == "hamming":
            m = hamming_m(r)
            c = _hamming_quantize(bits, m)
            st = {rev[j]: c[j] for j in range(r)}                            # r-m bits
        else:
            raise ValueError(kind)
        w[key] = st
        return st

    def machine(w, i, rng):
        st = state(w)
        if kind == "parity_store":
            if i in st["rev"]:
                return st["parity"] == w["W"][i]                             # parity is not W[i]
            return rng.randrange(2) == w["W"][i]
        if i in st and st[i] is not None:
            return st[i] == w["W"][i]
        return rng.randrange(2) == w["W"][i]

    return machine


def legal4(kind, r, s):
    if kind in ("truncate", "truncate_flip"):
        return True
    if kind in ("repetition", "parity_store"):
        return s >= 1
    if kind == "even_weight":
        return s >= r - 1
    if kind == "hamming":
        m = hamming_m(r)
        return m is not None and s >= r - m
    return False


def bits_used4(kind, r, s):
    return {"truncate": min(r, s), "truncate_flip": min(r, s), "repetition": 1, "parity_store": 1,
            "even_weight": r - 1, "hamming": r - (hamming_m(r) or 0)}[kind]


def run_cl4(L, n_draws, n_rep, log):
    law = "CL4"
    cells = []
    grid = []
    for r in (7, 15, 31, 63):
        m = hamming_m(r)
        for s in sorted({0, 1, r // 4, r - m, r - 1, r}):
            grid.append((r, s))
    kinds = ["truncate", "truncate_flip", "repetition", "parity_store", "even_weight", "hamming"]
    queries = list(range(L))
    for r, s in grid:
        cell_key = f"r={r}|s={s}"
        worlds = [world4(L, r, random.Random(draw_seed(law, cell_key, d))) for d in range(n_draws)]
        ceil = ceiling4(L, r, s)
        nv = naive4(L, r, s)
        for kind in kinds:
            if not legal4(kind, r, s):
                continue
            mfn = make_m4(kind, s)
            pairs = []
            for d, w in enumerate(worlds):
                rng = random.Random(draw_seed(law, cell_key + "|" + kind, d) ^ 0x5EED)
                pairs.append((evaluate(w, mfn, rng, n_rep, queries), ceil))
            rec = {"r": r, "s": s, "machine": kind, "bits_used": bits_used4(kind, r, s),
                   "ceiling": round(ceil, 6), "naive": round(nv, 6),
                   "vs_ceiling": summarize(pairs), "vs_naive": rel_to(pairs, nv), "vs_half": rel_to(pairs, 0.5),
                   "vs_flip": rel_to(pairs, flip_line(L, r, s))}
            cells.append(rec)
            log(f"CL4 {cell_key} {kind:13s} acc={rec['vs_ceiling']['mean_acc']:.4f} ceil={ceil:.4f} naive={nv:.4f} z_ceil={rec['vs_ceiling']['z']} z_naive={rec['vs_naive']['z']}")
    return cells


def adjudicate_cl4(cells):
    out = {}
    viol = [c for c in cells if c["vs_ceiling"]["exceeds_primary"]]
    out["B1_no_legal_machine_exceeds_corrected_ceiling"] = {
        "status": "CONFIRMED" if not viol else "FALSIFIED",
        "violations": [(c["r"], c["s"], c["machine"]) for c in viol],
        "diag_3se_count": sum(c["vs_ceiling"]["exceeds_diag"] for c in cells),
        "diag_3se_null_expectation": round(0.00135 * len(cells), 3)}
    tr = [c for c in cells if c["machine"] == "truncate"]
    off = [c for c in tr if not c["vs_naive"]["meets_primary"]]
    out["B2_truncate_on_naive_line_everywhere"] = {"status": "CONFIRMED" if not off else "FALSIFIED",
                                                  "off": [(c["r"], c["s"]) for c in off]}
    beats = [c for c in cells if (c["machine"] == "repetition" and c["s"] == 1) or
             (c["machine"] == "hamming" and c["s"] == c["r"] - hamming_m(c["r"]))]
    not_beat = [c for c in beats if not c["vs_naive"]["exceeds_primary"]]
    out["B3_naive_law_falsified_by_repetition_at_s1_and_hamming_at_s_r_minus_m"] = {
        "status": "CONFIRMED" if (beats and not not_beat) else "FALSIFIED",
        "cells_tested": [(c["r"], c["s"], c["machine"], c["vs_naive"]["mean_diff"], c["vs_naive"]["z"]) for c in beats],
        "not_beating": [(c["r"], c["s"], c["machine"]) for c in not_beat]}
    tight_expected = []
    for c in cells:
        r, s, k = c["r"], c["s"], c["machine"]
        m = hamming_m(r)
        if (s == 0 and k == "truncate") or (s == 1 and k == "repetition") or (s == r - m and k == "hamming") \
           or (s == r - 1 and k in ("even_weight", "truncate")) or (s == r and k == "truncate"):
            tight_expected.append(c)
    not_tight = [c for c in tight_expected if not c["vs_ceiling"]["meets_primary"]]
    out["B4_ceiling_attained_at_perfect_code_points_and_boundaries"] = {
        "status": "CONFIRMED" if (tight_expected and not not_tight) else "FALSIFIED",
        "n_points": len(tight_expected), "not_tight": [(c["r"], c["s"], c["machine"]) for c in not_tight]}
    ps = [c for c in cells if c["machine"] == "parity_store"]
    fl = [c for c in cells if c["machine"] == "truncate_flip"]
    bad_ps = [c for c in ps if not c["vs_half"]["meets_primary"]]
    bad_fl = [c for c in fl if not c["vs_flip"]["meets_primary"]]
    out["B5_parity_store_at_chance_and_flip_on_mirrored_line"] = {
        "status": "CONFIRMED" if not (bad_ps or bad_fl) else "FALSIFIED",
        "parity_off": [(c["r"], c["s"]) for c in bad_ps], "flip_off": [(c["r"], c["s"]) for c in bad_fl]}
    inter = [c for c in cells if c["s"] == c["r"] // 4 and c["s"] not in (0, 1) and c["s"] != c["r"] - hamming_m(c["r"])]
    out["B6_diag_intermediate_s_ceiling_respected_tightness_not_claimed"] = {
        "status": "DIAGNOSTIC",
        "cells": [(c["r"], c["s"], c["machine"], c["vs_ceiling"]["mean_acc"], c["ceiling"], c["vs_ceiling"]["z"]) for c in inter]}
    return out


# =====================================================================================
# CL-5 structured world
# =====================================================================================


def make_G(L, H, kind, seed):
    if kind == "rep":
        assert L % H == 0
        return [1 << (j % H) for j in range(L)]
    rng = random.Random(seed)
    while True:
        rows = [rng.randrange(1, 1 << H) for _ in range(L)]
        if gf2_rank(rows) == H:
            return rows


def gf2_rank(rows):
    basis = {}
    for v in rows:
        for piv in sorted(basis, reverse=True):
            if v >> piv & 1:
                v ^= basis[piv]
        if v:
            basis[v.bit_length() - 1] = v
    return len(basis)


def span_solve(G, revealed, bits):
    """returns list answer[j] in {0,1,None}: the value of row j determined by the revealed
    rows (linear combination of revealed bits) or None if row j is outside the span."""
    basis = {}  # pivot -> (vec, val)
    for i, b in zip(revealed, bits):
        v, val = G[i], b
        for piv in sorted(basis, reverse=True):
            if v >> piv & 1:
                bv, bval = basis[piv]
                v ^= bv
                val ^= bval
        if v:
            basis[v.bit_length() - 1] = (v, val)
    ans = []
    for j in range(len(G)):
        v, val = G[j], 0
        for piv in sorted(basis, reverse=True):
            if v >> piv & 1:
                bv, bval = basis[piv]
                v ^= bv
                val ^= bval
        ans.append(val if v == 0 else None)
    return ans


def world5(L, H, G, Gwrong, r, rng):
    theta = rng.randrange(0, 1 << H)
    W = [bin(G[j] & theta).count("1") & 1 for j in range(L)]
    idx = list(range(L))
    rng.shuffle(idx)
    revealed = idx[:r]
    bits = [W[i] for i in revealed]
    ans = span_solve(G, revealed, bits)
    ans_wrong = span_solve(Gwrong, revealed, bits)
    frac = sum(1 for a in ans if a is not None) / L
    return {"W": W, "revealed": set(revealed), "dev": dict(zip(revealed, bits)), "ans": ans,
            "ans_wrong": ans_wrong, "span_frac": frac}


def m5_eliminate(w, j, rng):
    a = w["ans"][j]
    if a is None:
        return rng.randrange(2) == w["W"][j]
    return a == w["W"][j]


def m5_table(w, j, rng):
    if j in w["dev"]:
        return w["dev"][j] == w["W"][j]
    return rng.randrange(2) == w["W"][j]


def m5_eliminate_wrong_G(w, j, rng):
    if j in w["dev"]:
        return w["dev"][j] == w["W"][j]
    a = w["ans_wrong"][j]
    if a is None:
        return rng.randrange(2) == w["W"][j]
    return a == w["W"][j]


def run_cl5(L, n_draws, n_rep, log):
    law = "CL5"
    cells = []
    machines = {"eliminate": m5_eliminate, "table": m5_table, "eliminate_wrong_G": m5_eliminate_wrong_G}
    queries = list(range(L))
    for gkind in ("rep", "rand"):
        for H in (16, 32, 64):
            G = make_G(L, H, gkind, seed=0xC1A55 + H)
            Gwrong = make_G(L, H, "rand", seed=0xBAD + H)
            for r in (0, 8, 16, 24, 32, 48, 64):
                cell_key = f"G={gkind}|H={H}|r={r}"
                worlds = [world5(L, H, G, Gwrong, r, random.Random(draw_seed(law, cell_key, d))) for d in range(n_draws)]
                per_draw_ceiling = [0.5 + w["span_frac"] / 2.0 for w in worlds]
                closed = ceiling5_rep_closed(L, H, r) if gkind == "rep" else None
                for mname, mfn in machines.items():
                    pairs = []
                    for d, w in enumerate(worlds):
                        rng = random.Random(draw_seed(law, cell_key + "|" + mname, d) ^ 0x5EED)
                        pairs.append((evaluate(w, mfn, rng, n_rep, queries), per_draw_ceiling[d]))
                    rec = {"G": gkind, "H": H, "r": r, "machine": mname,
                           "mean_ceiling_per_draw": round(statistics.fmean(per_draw_ceiling), 6),
                           "closed_form": (round(closed, 6) if closed is not None else None),
                           "ti1": round(ti1(L, r), 6),
                           "vs_ceiling": summarize(pairs), "vs_ti1": rel_to(pairs, ti1(L, r))}
                    cells.append(rec)
                    log(f"CL5 {cell_key} {mname:17s} acc={rec['vs_ceiling']['mean_acc']:.4f} ceil={rec['mean_ceiling_per_draw']:.4f} z={rec['vs_ceiling']['z']}")
                # closed-form check for G_rep: mean of per-draw span fraction vs hypergeometric form
                if closed is not None:
                    sd = statistics.stdev(per_draw_ceiling) if n_draws > 1 else 0.0
                    se = sd / math.sqrt(n_draws)
                    diff = statistics.fmean(per_draw_ceiling) - closed
                    cells.append({"G": gkind, "H": H, "r": r, "machine": "_closed_form_check",
                                  "mean_ceiling_per_draw": round(statistics.fmean(per_draw_ceiling), 6),
                                  "closed_form": round(closed, 6), "diff": round(diff, 6), "se": round(se, 6),
                                  "meets_primary": bool(abs(diff) <= Z_PRIMARY * se + 1e-12)})
    return cells


def adjudicate_cl5(cells):
    out = {}
    mc = [c for c in cells if not c["machine"].startswith("_")]
    viol = [c for c in mc if c["vs_ceiling"]["exceeds_primary"]]
    out["S1_no_machine_exceeds_per_draw_span_ceiling"] = {
        "status": "CONFIRMED" if not viol else "FALSIFIED",
        "violations": [(c["G"], c["H"], c["r"], c["machine"]) for c in viol],
        "diag_3se_count": sum(c["vs_ceiling"]["exceeds_diag"] for c in mc),
        "diag_3se_null_expectation": round(0.00135 * len(mc), 3)}
    el = [c for c in mc if c["machine"] == "eliminate"]
    off = [c for c in el if not c["vs_ceiling"]["meets_primary"]]
    out["S2_eliminate_tight_everywhere"] = {"status": "CONFIRMED" if not off else "FALSIFIED",
                                           "off": [(c["G"], c["H"], c["r"]) for c in off]}
    tb = [c for c in mc if c["machine"] == "table"]
    offt = [c for c in tb if not c["vs_ti1"]["meets_primary"]]
    out["S3_table_on_TI1_line_ignores_structure"] = {"status": "CONFIRMED" if not offt else "FALSIFIED",
                                                    "off": [(c["G"], c["H"], c["r"]) for c in offt]}
    cf = [c for c in cells if c["machine"] == "_closed_form_check"]
    offc = [c for c in cf if not c["meets_primary"]]
    out["S4_G_rep_closed_form_matches_per_draw_mean"] = {"status": "CONFIRMED" if not offc else "FALSIFIED",
                                                        "off": [(c["H"], c["r"], c["diff"], c["se"]) for c in offc]}
    gain = [c for c in el if c["G"] == "rep" and c["H"] < 64 and 0 < c["r"] < 64]
    nogain = [c for c in gain if not c["vs_ti1"]["exceeds_primary"]]
    out["S5a_G_rep_structure_buys_span_fraction_above_TI1_at_every_0_lt_r_lt_L"] = {
        "status": "CONFIRMED" if (gain and not nogain) else "FALSIFIED",
        "no_gain": [(c["G"], c["H"], c["r"]) for c in nogain],
        "gains": [(c["G"], c["H"], c["r"], c["vs_ti1"]["mean_diff"]) for c in gain]}
    late = [c for c in el if c["G"] == "rand" and c["H"] < 64 and c["r"] >= c["H"] and c["r"] < 64]
    nolate = [c for c in late if not c["vs_ti1"]["exceeds_primary"]]
    early = [c for c in el if c["G"] == "rand" and c["H"] < 64 and 0 < c["r"] <= c["H"] // 2]
    bigearly = [c for c in early if c["vs_ti1"]["mean_diff"] > 0.01]
    out["S5b_G_rand_transition_no_gain_above_0_01_for_r_le_H_over_2_and_gain_above_4se_for_r_ge_H"] = {
        "status": "CONFIRMED" if (late and early and not nolate and not bigearly) else "FALSIFIED",
        "no_gain_at_r_ge_H": [(c["H"], c["r"]) for c in nolate],
        "gain_above_0_01_at_r_le_H_over_2": [(c["H"], c["r"], c["vs_ti1"]["mean_diff"]) for c in bigearly],
        "late": [(c["H"], c["r"], c["vs_ti1"]["mean_diff"]) for c in late],
        "early": [(c["H"], c["r"], c["vs_ti1"]["mean_diff"]) for c in early]}
    h64 = [c for c in el if c["H"] == 64]
    off64 = [c for c in h64 if not c["vs_ti1"]["meets_primary"]]
    out["S6_H_eq_L_reduces_to_TI1_for_both_G_kinds"] = {"status": "CONFIRMED" if not off64 else "FALSIFIED",
                                                       "off": [(c["G"], c["r"]) for c in off64]}
    wg = [c for c in mc if c["machine"] == "eliminate_wrong_G"]
    upw = [c for c in wg if c["vs_ti1"]["exceeds_primary"]]
    out["S7a_wrong_structure_never_exceeds_TI1"] = {"status": "CONFIRMED" if not upw else "FALSIFIED",
                                                   "above": [(c["G"], c["H"], c["r"], c["vs_ti1"]["mean_diff"], c["vs_ti1"]["z"]) for c in upw]}
    offw = [c for c in wg if not c["vs_ti1"]["meets_primary"]]
    out["S7b_wrong_structure_is_exactly_neutral_sits_on_TI1"] = {"status": "CONFIRMED" if not offw else "FALSIFIED",
                                                                "off": [(c["G"], c["H"], c["r"], c["vs_ti1"]["mean_diff"], c["vs_ti1"]["z"]) for c in offw]}
    return out


# =====================================================================================
# CL-6 verifier channel (m-bit block obligation, k proposals to an exact checker)
# =====================================================================================


def world6(L, r, m, rng):
    W, revealed = base_world(L, r, rng)
    rev = set(revealed)
    nb = L // m
    blocks = []
    for b in range(nb):
        pos = list(range(b * m, (b + 1) * m))
        unrev = [p for p in pos if p not in rev]
        truth = tuple(W[p] for p in pos)
        # consistent completions (as tuples)
        cands = []
        for bits in range(1 << len(unrev)):
            word = list(W[p] if p in rev else 0 for p in pos)
            for t, p in enumerate(unrev):
                word[pos.index(p)] = (bits >> t) & 1
            cands.append(tuple(word))
        blocks.append({"truth": truth, "cands": cands, "u": len(unrev)})
    return {"W": W, "blocks": blocks, "m": m}


def make_m6(kind, k):
    def machine(w, b, rng):
        blk = w["blocks"][b]
        truth = blk["truth"]
        if kind == "verifier_search":
            cands = list(blk["cands"])
            rng.shuffle(cands)
            props = cands[:k]
        elif kind == "single_proposal":
            props = [rng.choice(blk["cands"])]
        elif kind == "repeat_proposal":
            c = rng.choice(blk["cands"])
            props = [c] * k
        elif kind == "random_k":
            m = w["m"]
            allw = list(range(1 << m))
            rng.shuffle(allw)
            props = [tuple((x >> t) & 1 for t in range(m)) for x in allw[:k]]
        else:
            raise ValueError(kind)
        return truth in props  # exact checker accepts iff a proposal equals the truth
    return machine


def run_cl6(L, n_draws, n_rep, log):
    law = "CL6"
    cells = []
    kinds = ["verifier_search", "single_proposal", "repeat_proposal", "random_k"]
    for m in (1, 4, 8):
        nb = L // m
        queries = list(range(nb))
        for k in (1, 2, 4, 16):
            for r in (0, 16, 32, 48):
                cell_key = f"m={m}|k={k}|r={r}"
                worlds = [world6(L, r, m, random.Random(draw_seed(law, cell_key, d))) for d in range(n_draws)]
                per_draw = [statistics.fmean(min(1.0, k / 2 ** blk["u"]) for blk in w["blocks"]) for w in worlds]
                per_draw_k1 = [statistics.fmean(1.0 / 2 ** blk["u"] for blk in w["blocks"]) for w in worlds]
                closed = ceiling6(L, r, m, k)
                for kind in kinds:
                    mfn = make_m6(kind, k)
                    pairs = []
                    for d, w in enumerate(worlds):
                        rng = random.Random(draw_seed(law, cell_key + "|" + kind, d) ^ 0x5EED)
                        pairs.append((evaluate(w, mfn, rng, n_rep, queries), per_draw[d]))
                    rec = {"m": m, "k": k, "r": r, "machine": kind, "closed_form": round(closed, 6),
                           "mean_ceiling_per_draw": round(statistics.fmean(per_draw), 6),
                           "vs_ceiling": summarize(pairs),
                           "vs_k1_line": rel_to(pairs, per_draw_k1),
                           "vs_random_line": rel_to(pairs, random_k_line(m, k)),
                           "vs_ti1": rel_to(pairs, ti1(L, r)), "vs_one": rel_to(pairs, 1.0)}
                    cells.append(rec)
                    log(f"CL6 {cell_key} {kind:16s} acc={rec['vs_ceiling']['mean_acc']:.4f} ceil={rec['mean_ceiling_per_draw']:.4f} z={rec['vs_ceiling']['z']}")
                sd = statistics.stdev(per_draw) if n_draws > 1 else 0.0
                se = sd / math.sqrt(n_draws)
                diff = statistics.fmean(per_draw) - closed
                cells.append({"m": m, "k": k, "r": r, "machine": "_closed_form_check", "closed_form": round(closed, 6),
                              "mean_ceiling_per_draw": round(statistics.fmean(per_draw), 6), "diff": round(diff, 6),
                              "se": round(se, 6), "meets_primary": bool(abs(diff) <= Z_PRIMARY * se + 1e-12)})
    return cells


def adjudicate_cl6(cells):
    out = {}
    mc = [c for c in cells if not c["machine"].startswith("_")]
    viol = [c for c in mc if c["vs_ceiling"]["exceeds_primary"]]
    out["V1_no_machine_exceeds_per_draw_ceiling"] = {
        "status": "CONFIRMED" if not viol else "FALSIFIED",
        "violations": [(c["m"], c["k"], c["r"], c["machine"]) for c in viol],
        "diag_3se_count": sum(c["vs_ceiling"]["exceeds_diag"] for c in mc),
        "diag_3se_null_expectation": round(0.00135 * len(mc), 3)}
    vs = [c for c in mc if c["machine"] == "verifier_search"]
    off = [c for c in vs if not c["vs_ceiling"]["meets_primary"]]
    out["V2_verifier_search_tight_everywhere"] = {"status": "CONFIRMED" if not off else "FALSIFIED",
                                                 "off": [(c["m"], c["k"], c["r"]) for c in off]}
    cf = [c for c in cells if c["machine"] == "_closed_form_check"]
    offc = [c for c in cf if not c["meets_primary"]]
    out["V3_hypergeometric_closed_form_matches_per_draw_mean"] = {"status": "CONFIRMED" if not offc else "FALSIFIED",
                                                                 "off": [(c["m"], c["k"], c["r"], c["diff"], c["se"]) for c in offc]}
    b11 = [c for c in vs if c["m"] == 1 and c["k"] == 1]
    off11 = [c for c in b11 if not c["vs_ti1"]["meets_primary"]]
    full = [c for c in vs if c["k"] >= 2 ** c["m"]]
    offfull = [c for c in full if not c["vs_one"]["meets_primary"]]
    out["V4_boundaries_m1k1_is_TI1_and_k_ge_2m_is_one"] = {"status": "CONFIRMED" if not (off11 or offfull) else "FALSIFIED",
                                                          "off_ti1": [c["r"] for c in off11], "off_one": [(c["m"], c["k"], c["r"]) for c in offfull]}
    sp = [c for c in mc if c["machine"] in ("single_proposal", "repeat_proposal")]
    offsp = [c for c in sp if not c["vs_k1_line"]["meets_primary"]]
    out["V5_single_and_repeat_proposal_sit_on_k1_line_independent_of_k"] = {"status": "CONFIRMED" if not offsp else "FALSIFIED",
                                                                           "off": [(c["m"], c["k"], c["r"], c["machine"]) for c in offsp]}
    rk = [c for c in mc if c["machine"] == "random_k"]
    offrk = [c for c in rk if not c["vs_random_line"]["meets_primary"]]
    out["V6_random_k_on_k_over_2m_independent_of_r"] = {"status": "CONFIRMED" if not offrk else "FALSIFIED",
                                                       "off": [(c["m"], c["k"], c["r"]) for c in offrk]}
    return out


# =====================================================================================
# CL-7 external store / retrieval channel
# =====================================================================================


def world7(L, r, c, rho, rng):
    W, revealed = base_world(L, r, rng)
    n_store = round(c * L)
    idx = list(range(L))
    rng.shuffle(idx)
    store = set(idx[:n_store])  # independent of the revealed set
    return {"W": W, "dev": {i: W[i] for i in revealed}, "store": store, "rho": rho}


def _retrieve(w, i, rng):
    return w["W"][i] if rng.random() < w["rho"] else rng.randrange(2)


def m7_rag(w, i, rng):
    if i in w["dev"]:
        return w["dev"][i] == w["W"][i]
    if i in w["store"]:
        return _retrieve(w, i, rng) == w["W"][i]
    return rng.randrange(2) == w["W"][i]


def m7_ignore_store(w, i, rng):
    if i in w["dev"]:
        return w["dev"][i] == w["W"][i]
    return rng.randrange(2) == w["W"][i]


def m7_store_only(w, i, rng):
    if i in w["store"]:
        return _retrieve(w, i, rng) == w["W"][i]
    return rng.randrange(2) == w["W"][i]


def m7_store_first(w, i, rng):
    if i in w["store"]:
        return _retrieve(w, i, rng) == w["W"][i]
    if i in w["dev"]:
        return w["dev"][i] == w["W"][i]
    return rng.randrange(2) == w["W"][i]


def run_cl7(L, n_draws, n_rep, log):
    law = "CL7"
    cells = []
    machines = {"rag": m7_rag, "ignore_store": m7_ignore_store, "store_only": m7_store_only, "store_first": m7_store_first}
    queries = list(range(L))
    for c in (0.0, 0.25, 0.5, 1.0):
        for rho in (0.0, 0.5, 1.0):
            for r in (0, 16, 32, 48):
                cell_key = f"c={c}|rho={rho}|r={r}"
                worlds = [world7(L, r, c, rho, random.Random(draw_seed(law, cell_key, d))) for d in range(n_draws)]
                ceil = ceiling7(L, r, c, rho)
                for mname, mfn in machines.items():
                    pairs = []
                    for d, w in enumerate(worlds):
                        rng = random.Random(draw_seed(law, cell_key + "|" + mname, d) ^ 0x5EED)
                        pairs.append((evaluate(w, mfn, rng, n_rep, queries), ceil))
                    rec = {"c": c, "rho": rho, "r": r, "machine": mname, "ceiling": round(ceil, 6),
                           "ti1": round(ti1(L, r), 6), "ti2_p_eq_c_rho": round(ti2(L, r, c * rho), 6),
                           "vs_ceiling": summarize(pairs), "vs_ti1": rel_to(pairs, ti1(L, r)),
                           "vs_store_only": rel_to(pairs, store_only_line(c, rho)),
                           "vs_store_first": rel_to(pairs, store_first_line(L, r, c, rho))}
                    cells.append(rec)
                    log(f"CL7 {cell_key} {mname:12s} acc={rec['vs_ceiling']['mean_acc']:.4f} ceil={ceil:.4f} z={rec['vs_ceiling']['z']}")
    return cells


def adjudicate_cl7(cells):
    out = {}
    viol = [c for c in cells if c["vs_ceiling"]["exceeds_primary"]]
    out["E1_no_machine_exceeds_ceiling"] = {
        "status": "CONFIRMED" if not viol else "FALSIFIED",
        "violations": [(c["c"], c["rho"], c["r"], c["machine"]) for c in viol],
        "diag_3se_count": sum(c["vs_ceiling"]["exceeds_diag"] for c in cells),
        "diag_3se_null_expectation": round(0.00135 * len(cells), 3)}
    rag = [c for c in cells if c["machine"] == "rag"]
    off = [c for c in rag if not c["vs_ceiling"]["meets_primary"]]
    out["E2_rag_tight_everywhere"] = {"status": "CONFIRMED" if not off else "FALSIFIED", "off": [(c["c"], c["rho"], c["r"]) for c in off]}
    ig = [c for c in cells if c["machine"] == "ignore_store"]
    offi = [c for c in ig if not c["vs_ti1"]["meets_primary"]]
    out["E3_ignore_store_on_TI1_at_every_c_rho"] = {"status": "CONFIRMED" if not offi else "FALSIFIED", "off": [(c["c"], c["rho"], c["r"]) for c in offi]}
    so = [c for c in cells if c["machine"] == "store_only"]
    offs = [c for c in so if not c["vs_store_only"]["meets_primary"]]
    out["E4_store_only_on_half_plus_c_rho_over_2_independent_of_r"] = {"status": "CONFIRMED" if not offs else "FALSIFIED",
                                                                       "off": [(c["c"], c["rho"], c["r"]) for c in offs]}
    sf = [c for c in cells if c["machine"] == "store_first"]
    offf = [c for c in sf if not c["vs_store_first"]["meets_primary"]]
    short_expected = [c for c in sf if c["r"] > 0 and c["c"] > 0 and c["rho"] < 1.0]
    not_short = [c for c in short_expected if not c["vs_ceiling"]["below_primary"]]
    out["E5_store_first_on_its_line_and_below_ceiling_by_r_over_L_c_1_minus_rho_over_2"] = {
        "status": "CONFIRMED" if not (offf or not_short) else "FALSIFIED",
        "off_line": [(c["c"], c["rho"], c["r"]) for c in offf], "not_below": [(c["c"], c["rho"], c["r"]) for c in not_short]}
    # boundary: c=1 reproduces the RV-377-124 TI-2 table with p = rho (compare the rag machine to ti2)
    b = [c for c in rag if c["c"] == 1.0]
    offb = [c for c in b if abs(c["ceiling"] - c["ti2_p_eq_c_rho"]) > 1e-12]
    z0 = [c for c in rag if (c["c"] == 0.0 or c["rho"] == 0.0)]
    offz = [c for c in z0 if not c["vs_ti1"]["meets_primary"]]
    out["E6_boundaries_c1_is_TI2_with_p_eq_rho_and_c_rho_zero_is_TI1"] = {"status": "CONFIRMED" if not (offb or offz) else "FALSIFIED",
                                                                          "ti2_mismatch": [(c["rho"], c["r"]) for c in offb],
                                                                          "ti1_off": [(c["c"], c["rho"], c["r"]) for c in offz]}
    return out


# =====================================================================================
# driver
# =====================================================================================

LAW_DEFAULTS = {"cl4": (100, 64)}  # (n_draws, n_rep); others (60, 32)

LAWS = {
    "cl3": ("RV-377-130", "NOISY_DEVELOPMENT", run_cl3, adjudicate_cl3),
    "cl4": ("RV-377-131", "BOUNDED_STATE", run_cl4, adjudicate_cl4),
    "cl5": ("RV-377-132", "STRUCTURED_WORLD", run_cl5, adjudicate_cl5),
    "cl6": ("RV-377-133", "VERIFIER", run_cl6, adjudicate_cl6),
    "cl7": ("RV-377-134", "EXTERNAL_STORE", run_cl7, adjudicate_cl7),
}


def predict_tables(L=L_DEFAULT):
    """closed-form tables for the freeze documents (no world is drawn here)."""
    out = {}
    out["cl3_single"] = [(q, r, round(ceiling3(L, r, q), 4), round(naive3(L, r, q), 4)) for q in (0.0, 0.1, 0.25, 0.4, 0.5, 0.75, 1.0) for r in (0, 16, 32, 48, 64)]
    out["cl3_multi"] = [(q, k, r, round(ceiling3(L, r, q, k), 4), round(first_copy_line(L, r, q), 4), round(unanimity_line(L, r, q, k), 4)) for q in (0.1, 0.25, 0.4) for k in (1, 3, 5) for r in (16, 32, 48)]
    cl4 = []
    for r in (7, 15, 31, 63):
        m = hamming_m(r)
        for s in sorted({0, 1, r // 4, r - m, r - 1, r}):
            cl4.append((r, s, round(ceiling4(L, r, s), 4), round(naive4(L, r, s), 4), round(sphere_covering_distortion(r, s), 4)))
    out["cl4"] = cl4
    out["cl5_rep_closed"] = [(H, r, round(ceiling5_rep_closed(L, H, r), 4), round(ti1(L, r), 4)) for H in (16, 32, 64) for r in (0, 8, 16, 24, 32, 48, 64)]
    mc = []
    rng = random.Random(0x5A11)
    for H in (16, 32, 64):
        G = make_G(L, H, "rand", seed=0xC1A55 + H)
        for r in (0, 8, 16, 24, 32, 48, 64):
            fr = []
            for _ in range(2000):
                idx = list(range(L))
                rng.shuffle(idx)
                rev = idx[:r]
                ans = span_solve(G, rev, [0] * r)
                fr.append(sum(a is not None for a in ans) / L)
            mc.append((H, r, round(0.5 + statistics.fmean(fr) / 2, 4), round(ti1(L, r), 4)))
    out["cl5_rand_mc_2000_S_draws"] = mc
    out["cl6"] = [(m, k, r, round(ceiling6(L, r, m, k), 4)) for m in (1, 4, 8) for k in (1, 2, 4, 16) for r in (0, 16, 32, 48)]
    out["cl7"] = [(c, rho, r, round(ceiling7(L, r, c, rho), 4), round(store_first_line(L, r, c, rho), 4)) for c in (0.0, 0.25, 0.5, 1.0) for rho in (0.0, 0.5, 1.0) for r in (0, 16, 32, 48)]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", choices=sorted(LAWS) + ["predict"], required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--L", type=int, default=L_DEFAULT)
    ap.add_argument("--draws", type=int, default=None, help="independent protected W draws per cell (default 60; CL-4 100)")
    ap.add_argument("--rep", type=int, default=None, help="full passes over all query positions per draw (default 32; CL-4 64)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.law == "predict":
        print(json.dumps(predict_tables(a.L), indent=1))
        return 0
    rid, name, runner, adj = LAWS[a.law]
    d_def, r_def = LAW_DEFAULTS.get(a.law, (60, 32))
    if a.draws is None:
        a.draws = d_def
    if a.rep is None:
        a.rep = r_def
    log = (lambda s: None) if a.quiet else (lambda s: print(s, flush=True))
    t0 = time.time()
    cells = runner(a.L, a.draws, a.rep, log)
    verdicts = adj(cells)
    with open(__file__, "rb") as fh:
        harness_sha = hashlib.sha256(fh.read()).hexdigest()
    receipt = {
        "revival_id": rid, "law": a.law.upper(), "name": name,
        "config": {"L": a.L, "n_draws": a.draws, "n_rep": a.rep, "z_primary": Z_PRIMARY, "z_diag": Z_DIAG,
                   "predicate_rule": "all predicates are over the EXPECTATION across independent protected W draws; "
                                     "s.e. across draws; primary falsifier at 4 s.e., 3 s.e. counts reported as diagnostics "
                                     "with their null expectation"},
        "harness_sha256": harness_sha, "python": sys.version.split()[0], "wall_seconds": round(time.time() - t0, 1),
        "verdicts": verdicts, "n_cells": len(cells), "cells": cells,
    }
    out = a.out or f"microscopes/results/CHANNEL_LAW_{name}_{rid.replace('-', '_')}.json"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
    print(json.dumps({k: v["status"] for k, v in verdicts.items()}, indent=1))
    print("wrote", out, "cells", len(cells), "wall", receipt["wall_seconds"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
