"""B2.12 -- KV cache: exact equality plus the measured compute/memory crossover as a function of prefix reuse.

Stage B2 row B2.12 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md:
    "Vary prefix reuse and continuation length. Confirm exact same outputs and predicted compute-memory crossover."

This is a SYNTHETIC EXACT MICROSCOPE at laptop scope, executed in exact rational arithmetic with no randomness anywhere.
It is NOT evidence about a trained neural network: it measures a cost/equality law of the caching MECHANISM on a declared
finite decoder. Registered against theorem TMT-6 (exact cache substitution, receipt check X-TMT6), TMT-13 (cache element
scaling, X-TMT13) and TMT-14 (fixed-window / cache distinction, X-TMT14), and registry entry TF-047.

Declared instrument
-------------------
Decoder: L layers, H heads per layer, head width d = 2, dyadic-kernel exact attention (scores are integers, weights 2^s),
residual stack x^{l+1}_t = x^l_t + sum_h attn_h(Q = x^l, K = Wk_{l,h} x^l, V = Wv_{l,h} x^l)_t, causal mask.
Token embedding embed(tok, t) = [tok, t mod 2]. All weights are declared rationals; no RNG is used.

Arms
----
RECOMPUTE : at every decode step, run the full forward pass over the whole prefix + generated tokens.
CACHE     : run the prefix once (prefill), store every (K, V) exactly, then extend one token per step.
STALE     : the negative twin -- caches (K, V) and does NOT invalidate when the prefix is MUTATED. It isolates TMT-6's
            immutability assumption from the caching mechanism itself.

Metered
-------
mults        : every scalar multiplication, split into projection mults and attention mults. The two arms perform the
               SAME attention read per emitted token; the cache saves prefix work, not the attention over the prefix.
cache_elems  : key/value elements RETAINED BETWEEN decode steps (the serving-memory quantity of TMT-13).
price        : declared total cost = mults + mu * cache_elems. The crossover mu* = delta_mults / delta_cache_elems is the
               memory price above which recomputation is cheaper. mu* is predicted to be independent of L and H.

Run: python3 -m gmi_microscope.b2_kv
"""
from __future__ import annotations

import json
import os
from fractions import Fraction as Fr

from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = "SYNTHETIC_EXACT_MICROSCOPE__LAPTOP_SCOPE__NOT_EMPIRICAL_NEURAL_EVIDENCE"
D = 2  # head width

# declared rational weights, indexed by (layer, head); deterministic, no RNG
def Wk(l, h):
    return [[Fr(1 + ((l + h) % 2)), Fr(-1)], [Fr(2), Fr(1 + (l % 3) - 1)]]


def Wv(l, h):
    return [[Fr(1), Fr(1 + (h % 2))], [Fr((l % 2)), Fr(-1)]]


def embed(tok, t):
    return [Fr(tok), Fr(t % 2)]


def token(stream, i):
    """Declared deterministic token stream: no RNG. stream selects prefix (0) or continuation r (r+1)."""
    return ((i * 7 + stream * 5 + 3) % 5) - 2


class Meter:
    def __init__(self):
        self.proj = 0
        self.attn = 0

    def total(self):
        return self.proj + self.attn


def _proj(W, x, m):
    m.proj += D * D
    return [sum(W[a][b] * x[b] for b in range(D)) for a in range(D)]


def _attn_at(i, Q, K, V, m):
    """Exact dyadic-kernel causal attention output at query position i over sources 0..i."""
    s = [sum(Q[i][a] * K[j][a] for a in range(D)) for j in range(i + 1)]
    m.attn += D * (i + 1)
    w = [Fr(2) ** int(x) for x in s]
    Z = sum(w)
    out = [sum(w[j] * V[j][a] for j in range(i + 1)) / Z for a in range(D)]
    m.attn += D * (i + 1)
    return out


def forward_full(toks, L, H, m):
    """RECOMPUTE: full forward over all positions. Returns the residual stream after the last layer."""
    x = [embed(t, i) for i, t in enumerate(toks)]
    n = len(toks)
    for l in range(L):
        acc = [[Fr(0)] * D for _ in range(n)]
        for h in range(H):
            K = [_proj(Wk(l, h), x[t], m) for t in range(n)]
            V = [_proj(Wv(l, h), x[t], m) for t in range(n)]
            for i in range(n):
                o = _attn_at(i, x, K, V, m)
                acc[i] = [acc[i][a] + o[a] for a in range(D)]
        x = [[x[i][a] + acc[i][a] for a in range(D)] for i in range(n)]
    return x


class Cached:
    """CACHE: per-layer, per-head stores of K, V and of the per-layer residual, extended one token at a time."""

    def __init__(self, L, H):
        self.L, self.H = L, H
        self.K = [[[] for _ in range(H)] for _ in range(L)]
        self.V = [[[] for _ in range(H)] for _ in range(L)]
        self.X = [[] for _ in range(L + 1)]   # X[l][t] = residual at layer l, position t

    def elems(self):
        """Key/value elements retained between decode steps (TMT-13's 2 L n d H_kv)."""
        return sum(len(self.K[l][h]) + len(self.V[l][h]) for l in range(self.L) for h in range(self.H)) * D

    def snapshot(self):
        return ([[list(r) for r in self.K[l]] for l in range(self.L)],
                [[list(r) for r in self.V[l]] for l in range(self.L)],
                [list(r) for r in self.X])

    def restore(self, snap):
        K, V, X = snap
        self.K = [[list(r) for r in K[l]] for l in range(self.L)]
        self.V = [[list(r) for r in V[l]] for l in range(self.L)]
        self.X = [list(r) for r in X]

    def append(self, tok, m):
        """Append one token; returns the final-layer residual at the new position."""
        t = len(self.X[0])
        self.X[0].append(embed(tok, t))
        for l in range(self.L):
            acc = [Fr(0)] * D
            for h in range(self.H):
                self.K[l][h].append(_proj(Wk(l, h), self.X[l][t], m))
                self.V[l][h].append(_proj(Wv(l, h), self.X[l][t], m))
                o = _attn_at(t, self.X[l], self.K[l][h], self.V[l][h], m)
                acc = [acc[a] + o[a] for a in range(D)]
            nxt = [self.X[l][t][a] + acc[a] for a in range(D)]
            if len(self.X[l + 1]) == t:
                self.X[l + 1].append(nxt)
            else:
                self.X[l + 1][t] = nxt
        return self.X[self.L][t]


# ----------------------------------------------------------------------------------------------------------------------
# closed forms (per layer per head), used as the FROZEN prediction and checked against the meters
def cf_full(n):
    """mults of one full forward over n tokens, per layer per head."""
    proj = 2 * n * D * D
    attn = sum(2 * D * (i + 1) for i in range(n))
    return proj, attn


def cf_step(n_prev):
    """mults of appending one token to a cache already holding n_prev tokens, per layer per head."""
    return 2 * D * D, 2 * D * (n_prev + 1)


def closed_form(P, C, R, L, H):
    """Predicted totals for R continuations of length C from a shared prefix of length P."""
    rec = 0
    for _ in range(R):
        for s in range(C):
            a, b = cf_full(P + s + 1)
            rec += a + b
    a, b = cf_full(P)
    cac = a + b
    for _ in range(R):
        n = P
        for s in range(C):
            a, b = cf_step(n)
            cac += a + b
            n += 1
        n = P  # each continuation restarts from the shared prefix cache
    rec *= L * H
    cac *= L * H
    mem_cache = 2 * L * H * D * (P + C)
    mem_rec = 0
    mu_star = Fr(rec - cac, mem_cache - mem_rec) if mem_cache != mem_rec else None
    return {"mults_recompute": rec, "mults_cache": cac, "cache_elems_peak": mem_cache,
            "recompute_elems_retained": mem_rec, "mu_star": mu_star}


CELLS = [  # (P, C, R, L, H)
    ("P4_C1_R1", 4, 1, 1, 4, 2),
    ("P4_C4_R1", 4, 4, 1, 4, 2),
    ("P4_C4_R8", 4, 4, 8, 4, 2),
    ("P16_C4_R1", 16, 4, 1, 4, 2),
    ("P16_C8_R4", 16, 8, 4, 4, 2),
    ("P16_C1_R8", 16, 1, 8, 4, 2),
    ("P32_C8_R16", 32, 8, 16, 4, 2),
    ("P16_C8_R4__L2H4", 16, 8, 4, 2, 4),
    ("P16_C8_R4__L8H1", 16, 8, 4, 8, 1),
]


def run_cell(P, C, R, L, H):
    prefix = [token(0, i) for i in range(P)]
    conts = [[token(r + 1, s) for s in range(C)] for r in range(R)]

    # --- RECOMPUTE arm: no state kept between steps
    m_rec = Meter()
    outs_rec = []
    for r in range(R):
        seq = list(prefix)
        row = []
        for s in range(C):
            seq.append(conts[r][s])
            x = forward_full(seq, L, H, m_rec)
            row.append(x[-1])
        outs_rec.append(row)

    # --- CACHE arm: prefill once, then extend; the prefix cache is REUSED by every continuation
    m_cac = Meter()
    cache = Cached(L, H)
    for i, t in enumerate(prefix):
        cache.append(t, m_cac)
    prefix_snap = cache.snapshot()
    peak = cache.elems()
    outs_cac = []
    for r in range(R):
        cache.restore(prefix_snap)
        row = []
        for s in range(C):
            row.append(list(cache.append(conts[r][s], m_cac)))
        peak = max(peak, cache.elems())
        outs_cac.append(row)

    # --- STALE negative twin: mutate the prefix, then continue from a cache built on the OLD prefix
    mutated = list(prefix)
    mutated[0] = mutated[0] + 1
    m_stale = Meter()
    stale = Cached(L, H)
    for i, t in enumerate(prefix):          # cache built on the ORIGINAL prefix
        stale.append(t, m_stale)
    stale_snap = stale.snapshot()
    m_ref = Meter()
    refresh = Cached(L, H)
    for i, t in enumerate(mutated):         # correctly invalidated cache, built on the MUTATED prefix
        refresh.append(t, m_ref)
    refresh_snap = refresh.snapshot()
    stale_out, fresh_out, truth_out = [], [], []
    for r in range(R):
        stale.restore(stale_snap)
        refresh.restore(refresh_snap)
        srow, frow, trow = [], [], []
        for s in range(C):
            srow.append(list(stale.append(conts[r][s], Meter())))
            frow.append(list(refresh.append(conts[r][s], Meter())))
        seq = list(mutated)
        for s in range(C):
            seq.append(conts[r][s])
            trow.append(forward_full(seq, L, H, Meter())[-1])
        stale_out.append(srow); fresh_out.append(frow); truth_out.append(trow)

    equal = outs_rec == outs_cac
    stale_equals_truth = stale_out == truth_out
    fresh_equals_truth = fresh_out == truth_out
    cf = closed_form(P, C, R, L, H)
    mu_star = Fr(m_rec.total() - m_cac.total(), peak)
    return {
        "P": P, "C": C, "R": R, "L": L, "H": H,
        "outputs_identical_recompute_vs_cache": equal,
        "mults_recompute": m_rec.total(), "mults_cache": m_cac.total(),
        "proj_mults_recompute": m_rec.proj, "proj_mults_cache": m_cac.proj,
        "attn_mults_recompute": m_rec.attn, "attn_mults_cache": m_cac.attn,
        "mults_ratio": str(Fr(m_rec.total(), m_cac.total())),
        "cache_elems_peak": peak, "cache_elems_formula_2LndHkv": 2 * L * H * D * (P + C),
        "cache_elems_matches_TMT13_formula": peak == 2 * L * H * D * (P + C),
        "mu_star_measured": str(mu_star), "mu_star_measured_float": round(float(mu_star), 6),
        "mu_star_closed_form": str(cf["mu_star"]),
        "meters_match_closed_form": (m_rec.total() == cf["mults_recompute"] and m_cac.total() == cf["mults_cache"]),
        "negative_twin_stale_cache_differs_from_truth": not stale_equals_truth,
        "negative_twin_invalidated_cache_equals_truth": fresh_equals_truth,
    }


def main(path=None):
    cells = {}
    for name, P, C, R, L, H in CELLS:
        cells[name] = run_cell(P, C, R, L, H)
    mu = {k: Fr(v["mu_star_measured"]) for k, v in cells.items()}
    claims = {
        "C1_outputs_identical_in_every_cell": all(v["outputs_identical_recompute_vs_cache"] for v in cells.values()),
        "C2_meters_match_closed_form_in_every_cell": all(v["meters_match_closed_form"] for v in cells.values()),
        "C3_cache_elems_match_TMT13_formula": all(v["cache_elems_matches_TMT13_formula"] for v in cells.values()),
        "C4_mu_star_independent_of_L_and_H": mu["P16_C8_R4"] == mu["P16_C8_R4__L2H4"] == mu["P16_C8_R4__L8H1"],
        "C5_mu_star_zero_at_single_one_token_continuation": mu["P4_C1_R1"] == 0,
        "C6_mu_star_increases_with_reuse": mu["P4_C4_R8"] > mu["P4_C4_R1"] and mu["P16_C1_R8"] > 0,
        "C7_stale_twin_differs_and_invalidated_twin_agrees": all(
            v["negative_twin_stale_cache_differs_from_truth"] and v["negative_twin_invalidated_cache_equals_truth"]
            for v in cells.values()),
    }
    receipt = {
        "schema": "GMI_B2_KV_CACHE_V1", "issue": [377, 422], "row": "B2.12 KV cache",
        "revival_id": "RV-377-055",
        "evidence_kind": KIND,
        "theorems": ["TMT-6 (X-TMT6 exact cache substitution)", "TMT-13 (X-TMT13 cache element scaling)",
                     "TMT-14 (X-TMT14 fixed-window / cache distinction)"],
        "registry_entries": ["TF-047 KV cache", "TF-044 context window W", "TF-018 MHA/GQA/MQA", "TF-076 activation checkpointing"],
        "declared_instrument": {
            "head_width_d": D, "attention": "dyadic-kernel exact causal attention (weights 2^s, exact rationals)",
            "metered_mults": "projection mults (d^2 per K or V per head per token) + attention mults (2 d per (query, source) pair)",
            "metered_memory": "key/value elements RETAINED BETWEEN decode steps",
            "price": "total = mults + mu * cache_elems; mu* = delta_mults / delta_cache_elems",
            "randomness": "none: tokens and weights are declared deterministic functions of their indices",
        },
        "cells": cells, "claims": claims,
        "n_claims_hold": sum(bool(v) for v in claims.values()), "n_claims": len(claims),
        "status": "GREEN" if all(claims.values()) else "RED",
        "claim_ceiling": "a cost and equality law of the caching mechanism on a declared finite exact decoder. It establishes "
                         "nothing about a trained neural network and nothing about any real serving system's constants.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_12_KV_CACHE_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    for k, v in r["cells"].items():
        print("%-22s eq=%s  mults %8d -> %6d (x%s)  elems=%5d  mu*=%s" % (
            k, v["outputs_identical_recompute_vs_cache"], v["mults_recompute"], v["mults_cache"],
            v["mults_ratio"], v["cache_elems_peak"], v["mu_star_measured"]))
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])
