#!/usr/bin/env python3
"""Real-scale run driver for gmi-833-h-real-scale-belief-state-v1 (issue #833,
section H, row `Bayesian inference/belief-state systems.`).

Runs on the host of record (FREEZE_V1.md section 4): billy-old, Linux,
CPython 3.14.4. Reads the sha256-bound external source D, builds the F17
set-valued word-hypothesis table over the descriptor-closure positions
(FREEZE_V1.md section 4), applies the registered target-independent Knuth
presentation (FREEZE_V1_SLICE_ADDENDUM_H17_V1.md), scores every readout of the
registered language R on the rank stage, the symmetric half-split regeneration
and the full-scale held set, and writes the receipts under REAL_RUNS/ that the
stdlib checker replays exactly and the independent oracle re-derives.

This package measures a BOUNDARY and an adjacent scoped positive; it closes no
checkbox. Every quantity is an exact integer decision count. No float enters
any count, comparison, loss, or claim.

Usage:  python3 -B run_real_scale_belief_state_v1.py
"""
from collections import Counter, defaultdict
import hashlib
import json
import os
import random
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

# FREEZE_V1.md section 4
SOURCE = "/usr/share/dict/american-english"
SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
N_EXPECT = 104334
T_EXPECT = 776142
LABEL_T_STAR = 8

# FREEZE_V1_SLICE_ADDENDUM_H17_V1.md
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27
NULL_SEED_LABEL = 20260930
NULL_SEED_DESIGN = 20260931
LADDER_BUDGETS = (1000, 5000, 10000, 30000, 67912, 135824, 271649)

REPLAY_HELD = 1500
REPLAY_RANK = 1500
REPLAY_REGEN = 2000


def readouts():
    """The registered readout language, rebuilt from the freeze text."""
    LEN_L = tuple(range(6, 13))
    out = ("C0", "C1")
    out += tuple("LEN<=%d" % L for L in LEN_L)
    out += tuple("CNT>=%d" % K for K in (1, 2, 3))
    out += tuple("EXT>=%d" % K for K in (1, 2, 3, 4))
    out += tuple("WSUM>=%d" % T for T in (8, 12, 16, 20, 24, 32, 48, 64))
    out += tuple("WMAX>=%d" % T for T in (7, 8, 9, 10, 11, 12, 14, 16))
    out += tuple("WAVG>=%d" % T for T in (6, 7, 8, 9, 10, 12))
    out += tuple("WDOM>=%d" % a for a in (3, 4, 5, 6, 8, 10, 12))
    out += tuple("WPAIR>=%d_%d" % (a, t) for a in (3, 4, 5, 6, 8, 10, 12)
                 for t in (6, 7, 8, 9, 10, 12))
    out += ("MEM_FALLBACK",)
    return out


READOUTS = readouts()
WEIGHTED_PREFIXES = ("WSUM>=", "WMAX>=", "WAVG>=", "WDOM>=", "WPAIR>=")


def is_weighted(name):
    return name.startswith(WEIGHTED_PREFIXES)


def classify(name):
    if name in ("C0", "C1"):
        return "CONSTANT_ARM"
    if name.startswith("LEN<="):
        return "DESCRIPTOR_LENGTH_THRESHOLD"
    if name.startswith("CNT>="):
        return "STORE_MEMBERSHIP_COUNT"
    if name.startswith("EXT>="):
        return "EXTENSION_COUNT"
    if is_weighted(name):
        return "WEIGHTED_EVIDENCE_BELIEF"
    if name == "MEM_FALLBACK":
        return "STORED_LABEL_READ_WITH_FALLBACK"
    raise ValueError(name)


def order_key(i):
    return (i * ORDER_MULT) % (2 ** 32)


class F17(object):
    """The registered amended ecology: the set-valued word-hypothesis table
    over the descriptor-closure positions of the sha-bound source."""

    def __init__(self, source=SOURCE):
        data = open(source, "rb").read()
        self.sha = hashlib.sha256(data).hexdigest()
        if self.sha != SOURCE_SHA:
            raise SystemExit("SOURCE DIGEST MISMATCH: %s != %s"
                             % (self.sha, SOURCE_SHA))
        words = data.decode("utf-8").split()
        self.N = len(words)
        if self.N != N_EXPECT:
            raise SystemExit("SOURCE TOKEN COUNT MISMATCH: %d != %d"
                             % (self.N, N_EXPECT))
        self.words = words
        DL = []
        fullpos = {}
        j = 0
        for w in words:
            for L in range(2, len(w) + 1):
                if L == len(w):
                    fullpos[w] = j
                DL.append(w[:L])
                j += 1
        self.DL = DL
        self.fullpos = fullpos
        self.T = len(DL)
        if self.T != T_EXPECT:
            raise SystemExit("DESCRIPTOR COUNT MISMATCH: %d != %d"
                             % (self.T, T_EXPECT))
        # full-source completion table per distinct prefix
        comp = defaultdict(list)
        for w in words:
            Lw = len(w)
            for k in range(2, Lw):
                comp[w[:k]].append(Lw)
        self.comp = comp
        lh = Counter(len(w) for w in words)
        self.length_histogram = dict(lh)
        self.label_t_star = LABEL_T_STAR
        # registered label
        ylab = {}
        for q, v in comp.items():
            ylab[q] = 1 if (len(v) >= 2 and 2 * max(v) > sum(v)
                            and max(v) >= LABEL_T_STAR) else 0
        self.ylab = ylab

    def y(self, q):
        return self.ylab.get(q, 0)

    def slices(self):
        order = sorted(range(self.T), key=order_key)
        n_fit = (self.T * 7) // 8
        fit = order[:n_fit]
        held = order[n_fit:]
        rank_fit = fit[:(7 * n_fit) // 10]
        rank_score = fit[(7 * n_fit) // 10:]
        half = n_fit // 2
        return {"order": order, "n_fit": n_fit, "held": held, "fit": fit,
                "rank_fit": rank_fit, "rank_score": rank_score,
                "fit_lo": fit[:half], "fit_hi": fit[half:], "half": half}


class Store(object):
    """The set-valued stored word-hypothesis table over a slice of positions."""

    def __init__(self, eco, store_pos, mode="real", rng=None):
        pset = set(store_pos)
        self.eco = eco
        self.fc = Counter(eco.DL[i] for i in store_pos)
        self.store_set = set(self.fc)
        self.words = set()
        for w in eco.words:
            fp = eco.fullpos.get(w)
            if fp is not None and fp in pset:
                self.words.add(w)
        entries = []
        for w in sorted(self.words):
            Lw = len(w)
            for k in range(2, Lw):
                entries.append((w[:k], Lw))
        wts = [e[1] for e in entries]
        self.weight_vector = tuple(wts)
        if mode == "equal":
            wts = [1] * len(entries)
        elif mode == "shuffle":
            rng.shuffle(wts)
        self.weight_vector_used = tuple(wts)
        agg = defaultdict(list)
        for (q, _), wp in zip(entries, wts):
            agg[q].append(wp)
        self.tab = dict((q, (len(v), sum(v), max(v))) for q, v in agg.items())

    def feat(self, q):
        return self.tab.get(q, (0, 0, 0))

    def count_of(self, q):
        return self.fc.get(q, 0)

    def in_store(self, q):
        return 1 if q in self.store_set else 0


def readout_decision(name, ql, c, ext, in_store, stored_label, wsum, wmax,
                     wavg, maj):
    """Exact decision of a readout on one query (registered language R)."""
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
    if name.startswith("CNT>="):
        return 1 if c >= int(name.split(">=")[1]) else 0
    if name.startswith("EXT>="):
        return 1 if ext >= int(name.split(">=")[1]) else 0
    if name.startswith("WSUM>="):
        return 1 if wsum >= int(name.split(">=")[1]) else 0
    if name.startswith("WMAX>="):
        return 1 if (ext >= 1 and wmax >= int(name.split(">=")[1])) else 0
    if name.startswith("WAVG>="):
        return 1 if (ext >= 1 and wsum >= int(name.split(">=")[1]) * ext) else 0
    if name.startswith("WDOM>="):
        a = int(name.split(">=")[1])
        return 1 if (ext >= 2 and a * wmax >= wsum) else 0
    if name.startswith("WPAIR>="):
        a, t = name.split(">=")[1].split("_")
        return 1 if (ext >= 2 and int(a) * wmax >= wsum
                     and wmax >= int(t)) else 0
    if name == "MEM_FALLBACK":
        return stored_label if in_store else maj
    raise ValueError("readout outside the registered language: " + name)


def score(eco, store, query_pos, maj):
    """Score every readout on query_pos. Exact integers only."""
    errs = {r: 0 for r in READOUTS}
    costs = {r: 0 for r in READOUTS}
    qy = [eco.y(eco.DL[i]) for i in query_pos]
    n = len(query_pos)
    for i in query_pos:
        q = eco.DL[i]
        ql = len(q)
        yv = eco.y(q)
        c = store.count_of(q)
        ext, wsum, wmax = store.feat(q)
        wavg = (wsum // ext) if ext else 0
        ins = store.in_store(q)
        yl = yv
        for r in READOUTS:
            if readout_decision(r, ql, c, ext, ins, yl, wsum, wmax, wavg,
                                maj) != yv:
                errs[r] += 1
        for r in READOUTS:
            costs[r] += (2 if r == "MEM_FALLBACK" else
                         (0 if (r in ("C0", "C1") or r.startswith("LEN<="))
                          else 1))
    maj_err = sum(1 for v in qy if v != maj)
    table = sorted((errs[r], costs[r], r) for r in READOUTS)
    winner = table[0][2]
    return {"n": n, "per_readout_errors": errs, "costs": costs,
            "majority_errors": maj_err, "winner": winner,
            "winner_errors": errs[winner], "winner_class": classify(winner),
            "winner_is_weighted": is_weighted(winner), "table": table}


def tally_block(eco, store, query_pos, maj):
    """Committed per-query tallies for exact replay by route A and
    re-derivation by route B. Each row:
    [len, true_label, count_in_store, ext, in_store, wsum, wmax, majority]."""
    rows = []
    for i in query_pos:
        q = eco.DL[i]
        ext, wsum, wmax = store.feat(q)
        rows.append([len(q), eco.y(q), store.count_of(q), ext,
                     store.in_store(q), wsum, wmax, maj])
    return rows


def _block(rows, winner, maj):
    """A committed replay block: the rows, the majority label, the majority
    rule's exact error count on those rows, and the winner's exact count."""
    return {"rows": len(rows), "queries": rows, "majority_label": maj,
            "majority_errors": sum(1 for r in rows if r[1] != maj),
            "winner": winner, "winner_errors": _block_errors(rows, winner)}


def _block_errors(rows, winner):
    e = 0
    for ql, yv, c, ext, ins, wsum, wmax, maj in rows:
        wavg = (wsum // ext) if ext else 0
        if readout_decision(winner, ql, c, ext, ins, yv, wsum, wmax, wavg,
                            maj) != yv:
            e += 1
    return e


def main():
    os.makedirs(RUNS, exist_ok=True)
    t0 = time.time()
    print("loading F17 ecology from %s" % SOURCE, flush=True)
    eco = F17()
    sl = eco.slices()
    n_fit = sl["n_fit"]
    assert n_fit == 679124 and len(sl["held"]) == 97018
    assert len(sl["rank_fit"]) == 475386 and len(sl["rank_score"]) == 203738
    assert sl["half"] == 339562
    # degenerate-channel screen (FREEZE_V1.md section 4): no duplicate lines
    dup = sum(1 for _c, n in Counter(eco.words).items() if n > 1)
    assert dup == 0, "the source has duplicate tokens; the frequency screen fails"
    assert max(eco.length_histogram.values()) == eco.length_histogram[LABEL_T_STAR]
    print("N=%d T=%d n_fit=%d n_held=%d duplicate-tokens=%d T*=%d"
          % (eco.N, eco.T, n_fit, len(sl["held"]), dup, eco.label_t_star),
          flush=True)

    fit_pos = sum(eco.y(eco.DL[i]) for i in sl["fit"])
    held_pos = sum(eco.y(eco.DL[i]) for i in sl["held"])
    print("fit positives %d/%d | held positives %d/%d (%d negatives)"
          % (fit_pos, n_fit, held_pos, len(sl["held"]),
             len(sl["held"]) - held_pos), flush=True)
    # the registered majority fallback, asserted before any enumeration
    MAJ = 1 if fit_pos * 2 >= n_fit else 0
    print("registered fit majority label = %d (fit base %.4f)"
          % (MAJ, fit_pos / n_fit), flush=True)

    store_fit = Store(eco, sl["fit"])
    store_rank = Store(eco, sl["rank_fit"])
    store_lo = Store(eco, sl["fit_lo"])
    store_hi = Store(eco, sl["fit_hi"])

    rank = score(eco, store_rank, sl["rank_score"], MAJ)
    print("rank stage: winner %s [%s] %d errors vs majority %d"
          % (rank["winner"], rank["winner_class"], rank["winner_errors"],
             rank["majority_errors"]), flush=True)
    rank_block = tally_block(eco, store_rank, sl["rank_score"][:REPLAY_RANK], MAJ)

    prim = score(eco, store_lo, sl["fit_hi"], MAJ)
    print("R09 PRIMARY (store fit_lo, score fit_hi): winner %s [%s] %d errors"
          % (prim["winner"], prim["winner_class"], prim["winner_errors"]),
          flush=True)
    regen = score(eco, store_hi, sl["fit_lo"], MAJ)
    print("R09 REGEN (store fit_hi, score fit_lo): winner %s [%s] %d errors"
          % (regen["winner"], regen["winner_class"], regen["winner_errors"]),
          flush=True)
    regen_block_lo = tally_block(eco, store_hi, sl["fit_lo"][:REPLAY_REGEN], MAJ)
    regen_block_hi = tally_block(eco, store_lo, sl["fit_hi"][:REPLAY_REGEN], MAJ)
    same_class = (rank["winner_class"] == prim["winner_class"]
                  == regen["winner_class"])

    final = score(eco, store_fit, sl["held"], MAJ)
    print("final arm (store fit, score held): winner %s [%s] %d errors vs "
          "majority %d" % (final["winner"], final["winner_class"],
                           final["winner_errors"], final["majority_errors"]),
          flush=True)
    held_block = tally_block(eco, store_fit, sl["held"][:REPLAY_HELD], MAJ)

    # raw-count vs weighted separation: the boundary datum
    raw_candidates = [r for r in READOUTS if r.startswith("EXT>=")]
    wtd_candidates = [r for r in READOUTS if is_weighted(r)]
    best_raw = min(raw_candidates, key=lambda r: final["per_readout_errors"][r])
    best_wtd = min(wtd_candidates, key=lambda r: final["per_readout_errors"][r])
    print("best raw count arm %s %d | best weighted arm %s %d"
          % (best_raw, final["per_readout_errors"][best_raw],
             best_wtd, final["per_readout_errors"][best_wtd]), flush=True)

    # the label's full-source optimum: the best achievable decision error over
    # the registered label when the store is the whole source (a boundary
    # datum, never a fitted configuration)
    full_store = Store(eco, list(range(eco.T)))
    full = score(eco, full_store, sl["held"], MAJ)
    full_best = full["table"][0]
    print("full-source optimum: winner %s %d errors (majority %d, F1 need %d)"
          % (full_best[2], full_best[0], full["majority_errors"],
             full["majority_errors"] // 2), flush=True)

    # ---- registered nulls ----
    rng = random.Random(NULL_SEED_DESIGN)
    shuffled = Store(eco, sl["fit"], "shuffle", rng)
    sh = score(eco, shuffled, sl["held"], MAJ)
    print("design null (global weight reassignment, seed %d): winner %s %d"
          % (NULL_SEED_DESIGN, sh["winner"], sh["winner_errors"]), flush=True)
    raw_moved = {r: (final["per_readout_errors"][r], sh["per_readout_errors"][r])
                 for r in raw_candidates}
    raw_invariant = all(a == b for a, b in raw_moved.values())
    print("raw count arms invariant under the reassignment: %s %s"
          % (raw_invariant, raw_moved), flush=True)
    wt_best = best_wtd
    print("weighted arm %s: real %d -> reassigned %d (gt3x=%s)"
          % (wt_best, final["per_readout_errors"][wt_best],
             sh["per_readout_errors"][wt_best],
             sh["per_readout_errors"][wt_best] > 3 * max(1, final["per_readout_errors"][wt_best])),
          flush=True)

    winner = final["winner"]
    held_y = [eco.y(eco.DL[i]) for i in sl["held"]]
    winner_preds = []
    for i in sl["held"]:
        q = eco.DL[i]
        ext, wsum, wmax = store_fit.feat(q)
        winner_preds.append(readout_decision(winner, len(q),
                                             store_fit.count_of(q), ext,
                                             store_fit.in_store(q), eco.y(q),
                                             wsum, wmax,
                                             (wsum // ext) if ext else 0, MAJ))
    assert sum(1 for p, v in zip(winner_preds, held_y) if p != v) == \
        final["winner_errors"]
    rngl = random.Random(NULL_SEED_LABEL)
    sh_lab = held_y[:]
    rngl.shuffle(sh_lab)
    label_null = sum(1 for p, v in zip(winner_preds, sh_lab) if p != v)
    print("label null (seed %d): %d errors vs majority %d"
          % (NULL_SEED_LABEL, label_null, final["majority_errors"]), flush=True)

    # ---- equal-weight control (R05) ----
    equal = Store(eco, sl["fit"], "equal")
    eq = score(eco, equal, sl["held"], MAJ)
    print("equal-weight control: winner %s [%s] %d errors"
          % (eq["winner"], eq["winner_class"], eq["winner_errors"]), flush=True)

    # ---- adjacent scoped positive: the two-evidence subpopulation ----
    held_scoped = [i for i in sl["held"] if store_fit.feat(eco.DL[i])[0] >= 2]
    sc = score(eco, store_fit, held_scoped, MAJ)
    rank_scoped = [i for i in sl["rank_score"]
                   if store_rank.feat(eco.DL[i])[0] >= 2]
    sc_rank = score(eco, store_rank, rank_scoped, MAJ)
    lo_scoped = [i for i in sl["fit_lo"] if store_hi.feat(eco.DL[i])[0] >= 2]
    hi_scoped = [i for i in sl["fit_hi"] if store_lo.feat(eco.DL[i])[0] >= 2]
    sc_lo = score(eco, store_hi, lo_scoped, MAJ)
    sc_hi = score(eco, store_lo, hi_scoped, MAJ)
    sc_same = len(set([sc_rank["winner_class"], sc["winner_class"],
                       sc_lo["winner_class"], sc_hi["winner_class"]])) == 1
    print("scoped positive: n_held %d/%d winner %s [%s] %d vs majority %d "
          "(need %d) class-sharing=%s"
          % (len(held_scoped), len(sl["held"]), sc["winner"],
             sc["winner_class"], sc["winner_errors"], sc["majority_errors"],
             sc["majority_errors"] // 2, sc_same), flush=True)

    # ---- R07 ladder + crossover ----
    ladder = []
    for m in LADDER_BUDGETS:
        st = Store(eco, sl["order"][:m])
        e = sum(1 for i in sl["held"]
                if readout_decision(winner, len(eco.DL[i]), st.count_of(eco.DL[i]),
                                    st.feat(eco.DL[i])[0], st.in_store(eco.DL[i]),
                                    eco.y(eco.DL[i]), st.feat(eco.DL[i])[1],
                                    st.feat(eco.DL[i])[2],
                                    (st.feat(eco.DL[i])[1] // st.feat(eco.DL[i])[0])
                                    if st.feat(eco.DL[i])[0] else 0,
                                    MAJ) != eco.y(eco.DL[i]))
        ladder.append((m, e))
    ladder.append((n_fit, final["winner_errors"]))
    monotone = all(ladder[k][1] <= ladder[k - 1][1]
                   for k in range(1, len(ladder)))
    V = len(store_fit.store_set)
    index_cost = V + ALPHABET_WIDTH
    m_star = None
    for m in range(1, n_fit + 1):
        if 2 * m > index_cost:
            m_star = m
            break
    print("ladder %s monotone=%s | V=%d index_cost=%d m*=%s"
          % ([e for _, e in ladder], monotone, V, index_cost, m_star), flush=True)

    # ---- matched-presentation control (source order) ----
    cont_store = Store(eco, list(range(n_fit)))
    cont = score(eco, cont_store, list(range(n_fit, eco.T)), MAJ)
    cont_f1 = cont["winner_errors"] <= cont["majority_errors"] // 2
    print("source-order control: winner %s %d vs majority %d F1=%s"
          % (cont["winner"], cont["winner_errors"], cont["majority_errors"],
             cont_f1), flush=True)

    rec = {
        "schema": "GMI833HRealScaleBeliefStateScopeV1",
        "scope": "SIGMA_H17R",
        "row": "Bayesian inference/belief-state systems.",
        "claim_ceiling":
            "EARNED_MEASUREMENT_BOUNDARY_AT_ORIGINAL_CLAIM_STRENGTH__ROW_LEFT_OPEN",
        "label": "TWO_EVIDENCE_POSTERIOR(EXT>=2, 2*MAX>SUM, MAX>=T*)",
        "label_t_star": eco.label_t_star,
        "source": {"path": SOURCE, "sha256": eco.sha, "tokens": eco.N,
                   "descriptors": eco.T,
                   "duplicate_tokens": dup,
                   "length_histogram": dict(sorted(eco.length_histogram.items()))},
        "presentation": {"key": "(i*%d) mod 2**32" % ORDER_MULT,
                         "n_fit": n_fit, "n_held": len(sl["held"]),
                         "rank_fit": len(sl["rank_fit"]),
                         "rank_score": len(sl["rank_score"]),
                         "half": sl["half"]},
        "holdout": {"n": len(sl["held"]), "positives": held_pos,
                    "negatives": len(sl["held"]) - held_pos,
                    "majority": MAJ,
                    "majority_errors": final["majority_errors"],
                    "winner": final["winner"],
                    "winner_errors": final["winner_errors"],
                    "winner_class": final["winner_class"],
                    "prototype_agreement": len(sl["held"]) - final["winner_errors"],
                    "f1_half_majority": final["majority_errors"] // 2,
                    "f1_holds": final["winner_errors"] <= final["majority_errors"] // 2,
                    "per_readout_errors": final["per_readout_errors"]},
        "rank_stage": {"store": "rank_fit", "score": "rank_score",
                       "n": rank["n"], "winner": rank["winner"],
                       "winner_errors": rank["winner_errors"],
                       "winner_class": rank["winner_class"],
                       "majority_errors": rank["majority_errors"],
                       "per_readout_errors": rank["per_readout_errors"]},
        "regen": {"primary": {"store": "fit_lo", "score": "fit_hi",
                              "n": prim["n"], "winner": prim["winner"],
                              "winner_errors": prim["winner_errors"],
                              "winner_class": prim["winner_class"],
                              "majority_errors": prim["majority_errors"]},
                  "regen": {"store": "fit_hi", "score": "fit_lo",
                            "n": regen["n"], "winner": regen["winner"],
                            "winner_errors": regen["winner_errors"],
                            "winner_class": regen["winner_class"],
                            "majority_errors": regen["majority_errors"]},
                  "same_class": bool(same_class),
                  "class": rank["winner_class"]},
        "boundary": {
            "best_raw_count_arm": best_raw,
            "best_raw_count_errors": final["per_readout_errors"][best_raw],
            "best_weighted_arm": best_wtd,
            "best_weighted_errors": final["per_readout_errors"][best_wtd],
            "raw_beats_weighted": bool(final["per_readout_errors"][best_raw]
                                       < final["per_readout_errors"][best_wtd]),
            "full_source_optimum_winner": full_best[2],
            "full_source_optimum_class": classify(full_best[2]),
            "full_source_optimum_errors": full_best[0],
            "full_source_majority_errors": full["majority_errors"],
            "full_source_f1_half_majority": full["majority_errors"] // 2,
            "f1_unattainable": bool(full_best[0] > full["majority_errors"] // 2),
            "f15_boundary_doc": "F15_EARNED_BOUNDARY_V1.md"},
        "nulls": {"design": {"seed": NULL_SEED_DESIGN,
                             "winner": sh["winner"],
                             "winner_errors": sh["winner_errors"],
                             "weighted_arm": wt_best,
                             "weighted_real": final["per_readout_errors"][wt_best],
                             "weighted_reassigned": sh["per_readout_errors"][wt_best],
                             "gt_3x": sh["per_readout_errors"][wt_best]
                                     > 3 * max(1, final["per_readout_errors"][wt_best]),
                             "raw_arms_invariant": bool(raw_invariant),
                             "raw_arms": {k: list(v) for k, v in raw_moved.items()}},
                  "label": {"seed": NULL_SEED_LABEL, "errors": label_null,
                            "gt_majority": label_null > final["majority_errors"],
                            "shuffled_labels": [int(v) for v in sh_lab]}},
        "equal_weight_control": {"winner": eq["winner"],
                                 "winner_class": eq["winner_class"],
                                 "winner_errors": eq["winner_errors"],
                                 "majority_errors": eq["majority_errors"],
                                 "weighted_in_top6": [r for _e, _c, r in eq["table"][:6]
                                                      if is_weighted(r)],
                                 "no_weighted_arm_wins":
                                     not any(is_weighted(r) for _e, _c, r in eq["table"][:6])},
        "adjacent_scoped_positive": {
            "scope": "held queries whose stored table presents >= 2 hypotheses",
            "n_held": len(held_scoped),
            "n_held_full": len(sl["held"]),
            "rank": {"n": sc_rank["n"], "winner": sc_rank["winner"],
                     "winner_class": sc_rank["winner_class"],
                     "winner_errors": sc_rank["winner_errors"],
                     "majority_errors": sc_rank["majority_errors"]},
            "held": {"n": sc["n"], "winner": sc["winner"],
                     "winner_class": sc["winner_class"],
                     "winner_errors": sc["winner_errors"],
                     "majority_errors": sc["majority_errors"],
                     "f1_holds": sc["winner_errors"] <= sc["majority_errors"] // 2},
            "regen_lo": {"n": sc_lo["n"], "winner": sc_lo["winner"],
                         "winner_class": sc_lo["winner_class"],
                         "winner_errors": sc_lo["winner_errors"],
                         "majority_errors": sc_lo["majority_errors"]},
            "regen_hi": {"n": sc_hi["n"], "winner": sc_hi["winner"],
                         "winner_class": sc_hi["winner_class"],
                         "winner_errors": sc_hi["winner_errors"],
                         "majority_errors": sc_hi["majority_errors"]},
            "class_sharing": bool(sc_same),
            "class": sc["winner_class"],
            "claimed_for_this_row": False,
            "note": ("the recovered class is the sibling stored-label read; it "
                     "is recorded as the adjacent scoped positive the boundary "
                     "requires and is NOT claimed as this row's recovery")},
        "holdout_all": {"rows": len(held_y),
                        "queries": [[int(yv), int(p)]
                                    for yv, p in zip(held_y, winner_preds)]},
        "ladder": {"readout": winner, "budgets": [m for m, _ in ladder],
                   "errors": [e for _, e in ladder], "monotone": bool(monotone)},
        "crossover": {"V": V, "alphabet_width": ALPHABET_WIDTH,
                      "index_cost": index_cost, "m_star": m_star,
                      "scan_cost_at_m_star": 2 * m_star,
                      "holds": 2 * m_star > index_cost},
        "presentation_control": {"winner": cont["winner"],
                                 "winner_errors": cont["winner_errors"],
                                 "winner_class": cont["winner_class"],
                                 "majority_errors": cont["majority_errors"],
                                 "f1_holds": bool(cont_f1),
                                 "control_fires": bool(not cont_f1)},
        "replay": {
            "held_block": _block(held_block, final["winner"], MAJ),
            "rank_block": _block(rank_block, rank["winner"], MAJ),
            "regen_lo_block": _block(regen_block_lo, regen["winner"], MAJ),
            "regen_hi_block": _block(regen_block_hi, prim["winner"], MAJ)},
    }
    out = os.path.join(RUNS, "scope_SIGMA_H17R.json")
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(RUNS, "sources.json"), "w") as fh:
        json.dump({"schema": "GMI833HRealScaleSourcesV1",
                   "source": {"path": SOURCE, "sha256": eco.sha,
                              "tokens": eco.N, "descriptors": eco.T,
                              "duplicate_tokens": dup,
                              "length_histogram": dict(sorted(eco.length_histogram.items()))}},
                  fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("WROTE %s (%.1fs)" % (out, time.time() - t0), flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
