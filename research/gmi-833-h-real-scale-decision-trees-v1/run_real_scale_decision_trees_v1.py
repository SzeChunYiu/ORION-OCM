#!/usr/bin/env python3
"""Real-scale run driver for gmi-833-h-real-scale-decision-trees-v1.

Runs on the host of record (FREEZE_V1.md section 4): billy-old, Linux,
CPython 3.14.4. Reads the sha256-bound external source D, builds the F08
stored-context rule-table ecology, applies the registered target-independent
Knuth presentation (FREEZE_V1_SLICE_ADDENDUM.md), scores every readout of the
registered language R (FREEZE_V1_SLICE_ADDENDUM.md section 2, R2 addendum)
on the rank stage, the symmetric half-split regeneration (R2.1), and the
full-scale held set, and writes the receipts under REAL_RUNS/ that the stdlib
checker replays exactly and the independent oracle re-derives.

Stdlib only: every quantity is an exact integer decision count. No float
enters any count, comparison, loss, or claim.

Usage:  python3 -B run_real_scale_decision_trees_v1.py
"""
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
import hashlib
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

# FREEZE_V1.md section 4
SOURCE = "/usr/share/dict/american-english"
SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
N_EXPECT = 104334
T_EXPECT = 776142

# FREEZE_V1_SLICE_ADDENDUM.md
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27
LABEL_L0 = 9
LEN_L = tuple(range(6, 13))
CNT_K = (1, 2, 3)
ASSOC_K = (1, 2, 3)
READOUTS = (("C0", "C1")
            + tuple("LEN<=%d" % L for L in LEN_L)
            + tuple("CNT>=%d" % K for K in CNT_K)
            + tuple("ASSOC>=%d" % K for K in ASSOC_K)
            + tuple("LEN<=%d&CNT>=%d" % (L, j) for L in LEN_L for j in CNT_K)
            + tuple("LEN<=%d&ASSOC>=%d" % (L, j) for L in LEN_L for j in ASSOC_K)
            + ("PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK"))

# FREEZE_V1_SLICE_ADDENDUM_R2.md
NULL_SEED_LABEL = 20260926
NULL_SEED_DESIGN = 20260927
LADDER_BUDGETS = (1000, 5000, 10000, 30000, 67912, 135824, 271649)

REPLAY_HELD = 1500
REPLAY_RANK = 1500
REPLAY_REGEN = 2000

CLASSES = dict((r, "THRESHOLD_CONJUNCTION") for r in READOUTS)
for r in ("C0", "C1"):
    CLASSES[r] = "CONSTANT_ARM"
for L in LEN_L:
    CLASSES["LEN<=%d" % L] = "DESCRIPTOR_LENGTH_THRESHOLD"
CLASSES["CNT>=1"] = "STORED_EXEMPLAR_MEMBERSHIP"
CLASSES["CNT>=2"] = "STORED_EXEMPLAR_COUNT_THRESHOLD"
CLASSES["CNT>=3"] = "STORED_EXEMPLAR_COUNT_THRESHOLD"
CLASSES["ASSOC>=1"] = "CUE_ASSOCIATION_RETRIEVAL"
CLASSES["ASSOC>=2"] = "CUE_ASSOCIATION_FANOUT"
CLASSES["ASSOC>=3"] = "CUE_ASSOCIATION_SIZE_THRESHOLD"
CLASSES["PREF_VOTE"] = "NEIGHBORHOOD_MAJORITY_VOTE"
CLASSES["EXT_VOTE"] = "NEIGHBORHOOD_MAJORITY_VOTE"
CLASSES["MEM_FALLBACK"] = "STORED_LABEL_READ_WITH_FALLBACK"

COST = dict((r, 0) for r in READOUTS)
for r in READOUTS:
    if r.startswith("CNT>=") or r.startswith("ASSOC>="):
        COST[r] = 1
    if "&" in r:
        COST[r] = 1
    if r == "MEM_FALLBACK":
        COST[r] = 2


def classify(name):
    return CLASSES[name]


def order_key(i):
    """FREEZE_V1_SLICE_ADDENDUM.md: key(i) = (i * 2654435761) mod 2**32."""
    return (i * ORDER_MULT) % (2 ** 32)


class F08(object):
    """The registered ecology: the stored-context rule table over the
    sha-bound bytes. A query q is a descriptor (prefix of length >= 2 of a
    source token); the stored context of q is its membership count among the
    stored descriptors (cnt(q)) and the set A(q) of distinct letters stored
    immediately after q among stored descriptors of length >= 3 (the trie
    fan-out). The family is decision trees / rule systems: a query is
    classified by testing threshold conditions against its own properties
    (length) and against its stored context (membership count, association
    fan-out), and a decision rule is a conjunction of such tests."""

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
        for w in words:
            for L in range(2, len(w) + 1):
                DL.append(w[:L])
        self.T = len(DL)
        if self.T != T_EXPECT:
            raise SystemExit("DESCRIPTOR COUNT MISMATCH: %d != %d"
                             % (self.T, T_EXPECT))
        self.DL = DL
        cnt = Counter(DL)
        self.cnt_full = cnt
        self.LEN = [len(q) for q in DL]
        # Protected interface: y(q) = 1 iff len(q) <= 9 AND
        # source-count(q) >= 2 -- the short shared descriptor, a threshold
        # conjunction over the source (the property a decision rule over the
        # stored context would express as LEN<=9 AND count>=2).
        self.ylab = {q: (1 if (len(q) <= LABEL_L0 and cnt[q] >= 2) else 0)
                     for q in DL}
        self.y = [self.ylab[q] for q in DL]

    def slices(self):
        order = sorted(range(self.T), key=order_key)
        n_fit = (self.T * 7) // 8
        fit = order[:n_fit]
        held = order[n_fit:]
        rank_fit = fit[:(7 * n_fit) // 10]
        rank_score = fit[(7 * n_fit) // 10:]
        half = n_fit // 2
        return {"order": order, "n_fit": n_fit, "held": held,
                "rank_fit": rank_fit, "rank_score": rank_score,
                "fit_lo": fit[:half], "fit_hi": fit[half:], "half": half,
                "fit": fit}


class Store(object):
    """The stored-context rule table over a set of fit positions."""

    def __init__(self, eco, store_pos):
        self.eco = eco
        self.fc = Counter(eco.DL[i] for i in store_pos)
        self.store_set = set(self.fc)
        self.store_list = sorted(self.store_set)
        self.fan = defaultdict(set)
        for q in self.store_set:
            if len(q) >= 3:
                self.fan[q[:-1]].add(q[-1])
        self.ylab = {q: eco.ylab[q] for q in self.store_set}

    def count_of(self, q):
        return self.fc.get(q, 0)

    def fan_of(self, q):
        return len(self.fan.get(q, ()))

    def pref_tally(self, q, ql):
        """(n1, n0) over stored proper prefixes of q, labelled by the
        source-wide label of each prefix."""
        n1 = n0 = 0
        for k in range(2, ql):
            p = q[:k]
            if p in self.store_set:
                if self.eco.ylab[p]:
                    n1 += 1
                else:
                    n0 += 1
        return n1, n0

    def ext_tally(self, q, ql):
        """(n1, n0) over stored descriptors extending q (distinct strings),
        labelled by the source-wide label."""
        lo = bisect_left(self.store_list, q)
        hi = bisect_right(self.store_list, q + "\x7f")
        n1 = n0 = 0
        for m in range(lo, hi):
            p = self.store_list[m]
            if len(p) > ql:
                if self.eco.ylab[p]:
                    n1 += 1
                else:
                    n0 += 1
        return n1, n0


def readout_decision(name, ql, c, fa, in_store, yl, p1, p0, e1, e0):
    """Exact decision of a readout on one query (registered language R).

    Empty-neighbourhood readouts fall back to the fit majority (1), asserted
    to be 1 by the caller before any enumeration.
    """
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if "&" in name:
        for part in name.split("&"):
            if readout_decision(part, ql, c, fa, in_store, yl,
                                p1, p0, e1, e0) == 0:
                return 0
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
    if name.startswith("CNT>="):
        return 1 if c >= int(name.split(">=")[1]) else 0
    if name.startswith("ASSOC>="):
        return 1 if fa >= int(name.split(">=")[1]) else 0
    if name == "PREF_VOTE":
        if p1 + p0 == 0:
            return 1
        return 1 if p1 > p0 else 0
    if name == "EXT_VOTE":
        if e1 + e0 == 0:
            return 1
        return 1 if e1 > e0 else 0
    if name == "MEM_FALLBACK":
        if in_store:
            return yl
        return 1
    raise ValueError("readout outside the registered language: " + name)


FIT_MAJ = 1  # asserted > 1/2 by the caller before any enumeration


def score(eco, store, query_pos):
    """Score every readout on query_pos. Exact integers only.

    Returns per-readout error counts, per-readout summed charged cost
    (R2.3), the majority rule's errors, and the winner of the registered
    winner rule (fewest exact decision errors, then fewer charged-cost
    units, then readout name).
    """
    errs = {r: 0 for r in READOUTS}
    costs = {r: 0 for r in READOUTS}
    qy = [eco.y[i] for i in query_pos]
    n = len(query_pos)
    for i in query_pos:
        q = eco.DL[i]
        ql = eco.LEN[i]
        yv = eco.y[i]
        c = store.count_of(q)
        fa = store.fan_of(q)
        in_store = 1 if q in store.store_set else 0
        yl = eco.ylab[q]
        p1, p0 = store.pref_tally(q, ql)
        e1, e0 = store.ext_tally(q, ql)
        for r in READOUTS:
            if readout_decision(r, ql, c, fa, in_store, yl,
                                p1, p0, e1, e0) != yv:
                errs[r] += 1
        for r in READOUTS:
            costs[r] += COST[r]
        costs["PREF_VOTE"] += p1 + p0
        costs["EXT_VOTE"] += e1 + e0
    maj_err = sum(1 for v in qy if v != FIT_MAJ)
    table = sorted((errs[r], costs[r], r) for r in READOUTS)
    winner = table[0][2]
    return {"n": n, "per_readout_errors": errs, "costs": costs,
            "majority_errors": maj_err, "winner": winner,
            "winner_errors": errs[winner], "winner_class": classify(winner),
            "table": table}


def tally_block(eco, store, query_pos):
    """Committed per-query tallies for exact replay by route A /
    re-derivation by route B. Each row:
    [len, true_label, count_in_store, assoc_fanout_in_store, in_store,
     stored_label, p1, p0, e1, e0]."""
    rows = []
    for i in query_pos:
        q = eco.DL[i]
        ql = eco.LEN[i]
        c = store.count_of(q)
        fa = store.fan_of(q)
        in_store = 1 if q in store.store_set else 0
        yl = eco.ylab[q]
        p1, p0 = store.pref_tally(q, ql)
        e1, e0 = store.ext_tally(q, ql)
        rows.append([ql, eco.y[i], c, fa, in_store, yl, p1, p0, e1, e0])
    return rows


def _winner_preds(eco, store, query_pos, winner):
    return [readout_decision(winner, eco.LEN[i], store.count_of(eco.DL[i]),
                             store.fan_of(eco.DL[i]),
                             1 if eco.DL[i] in store.store_set else 0,
                             eco.ylab[eco.DL[i]], 0, 0, 0, 0)
            for i in query_pos]


def _block_errors(rows, winner):
    e = 0
    for ql, yv, c, fa, in_store, yl, p1, p0, e1, e0 in rows:
        if readout_decision(winner, ql, c, fa, in_store, yl,
                            p1, p0, e1, e0) != yv:
            e += 1
    return e


def main():
    os.makedirs(RUNS, exist_ok=True)
    t0 = time.time()
    print("loading F08 ecology from %s" % SOURCE, flush=True)
    eco = F08()
    sl = eco.slices()
    n_fit = sl["n_fit"]
    assert n_fit == 679124 and len(sl["held"]) == 97018
    assert len(sl["rank_fit"]) == 475386 and len(sl["rank_score"]) == 203738
    assert sl["half"] == 339562
    fit_pos = sum(eco.y[i] for i in sl["fit"])
    assert fit_pos == 535946
    assert fit_pos * 2 > n_fit, "fit positive fraction not > 1/2"
    print("N=%d T=%d n_fit=%d n_held=%d fit_pos=%d"
          % (eco.N, eco.T, n_fit, len(sl["held"]), fit_pos), flush=True)

    held_y = [eco.y[i] for i in sl["held"]]
    held_pos = sum(held_y)
    held_neg = len(held_y) - held_pos
    assert held_pos == 76572 and held_neg == 20446, (held_pos, held_neg)

    store_fit = Store(eco, sl["fit"])
    store_rank = Store(eco, sl["rank_fit"])
    store_lo = Store(eco, sl["fit_lo"])
    store_hi = Store(eco, sl["fit_hi"])

    # ---- rank stage (store = rank_fit, score = rank_score) ----
    print("rank stage (store rank_fit, score rank_score)", flush=True)
    rank = score(eco, store_rank, sl["rank_score"])
    assert rank["winner"] == "LEN<=9&CNT>=1" and rank["winner_errors"] == 11947
    assert rank["majority_errors"] == 42936
    # R2.6: the admitted membership-with-fallback arm must be rejected by the
    # winner rule at every stage (design statistics re-derived by the run).
    assert rank["per_readout_errors"]["MEM_FALLBACK"] == 34750
    rank_block = tally_block(eco, store_rank, sl["rank_score"][:REPLAY_RANK])

    # ---- R09 symmetric half-split regeneration ----
    print("R09 PRIMARY (store fit_lo, score fit_hi)", flush=True)
    prim = score(eco, store_lo, sl["fit_hi"])
    assert prim["winner"] == "LEN<=9&ASSOC>=1" and prim["winner_errors"] == 23239
    assert prim["majority_errors"] == 71453
    assert prim["per_readout_errors"]["MEM_FALLBACK"] == 59873
    print("R09 REGEN (store fit_hi, score fit_lo)", flush=True)
    regen = score(eco, store_hi, sl["fit_lo"])
    assert regen["winner"] == "LEN<=9&ASSOC>=1" and regen["winner_errors"] == 29226
    assert regen["majority_errors"] == 71725
    assert regen["per_readout_errors"]["MEM_FALLBACK"] == 60056
    regen_block_lo = tally_block(eco, store_hi, sl["fit_lo"][:REPLAY_REGEN])
    regen_block_hi = tally_block(eco, store_lo, sl["fit_hi"][:REPLAY_REGEN])

    # ---- final arm (store = full fit, score = held) ----
    print("final arm (store fit, score held)", flush=True)
    final = score(eco, store_fit, sl["held"])
    assert final["winner"] == "LEN<=9&CNT>=1" and final["winner_errors"] == 1391
    assert final["majority_errors"] == 20446
    assert final["per_readout_errors"]["MEM_FALLBACK"] == 15759
    held_block = tally_block(eco, store_fit, sl["held"][:REPLAY_HELD])
    prototype_agreement = len(sl["held"]) - final["winner_errors"]
    assert prototype_agreement == 95627

    # ---- nulls (R2.2) ----
    winner = final["winner"]
    winner_preds = _winner_preds(eco, store_fit, sl["held"], winner)
    assert sum(1 for p, v in zip(winner_preds, held_y) if p != v) == \
        final["winner_errors"]
    rng = random.Random(NULL_SEED_LABEL)
    sh = held_y[:]
    rng.shuffle(sh)
    label_null = sum(1 for p, v in zip(winner_preds, sh) if p != v)
    assert label_null == 33079
    rng2 = random.Random(NULL_SEED_DESIGN)
    idx2 = list(range(eco.T))
    rng2.shuffle(idx2)
    sh_store = set(eco.DL[i] for i in idx2[:n_fit])
    design_preds = [1 if (eco.LEN[i] <= LABEL_L0 and eco.DL[i] in sh_store)
                    else 0 for i in sl["held"]]
    design_null = sum(1 for p, v in zip(design_preds, held_y) if p != v)
    assert design_null == 9358

    # ---- R07 ladder (winner readout LEN<=9&CNT>=1) + vocabulary crossover ----
    ladder = []
    order = sl["fit"]
    for m in LADDER_BUDGETS:
        st = Store(eco, order[:m])
        e = sum(1 for i in sl["held"]
                if (1 if (eco.LEN[i] <= LABEL_L0 and
                          st.count_of(eco.DL[i]) >= 1) else 0) != eco.y[i])
        ladder.append((m, e))
    ladder.append((n_fit, final["winner_errors"]))
    assert [e for _, e in ladder] == [67348, 56488, 51064, 40557, 31103,
                                      22904, 11946, 1391]
    monotone = all(ladder[k][1] <= ladder[k - 1][1]
                   for k in range(1, len(ladder)))
    assert monotone
    V = len(store_fit.store_set)
    assert V == 221569
    index_cost = V + ALPHABET_WIDTH
    assert index_cost == 221596
    m_star = None
    for m in range(1, n_fit + 1):
        if 2 * m > index_cost:
            m_star = m
            break
    assert m_star == 110799

    # ---- R05 matched-presentation control (R2.4) ----
    cont_fit = list(range(n_fit))
    cont_held = list(range(n_fit, eco.T))
    cont_store = Store(eco, cont_fit)
    cont_final = score(eco, cont_store, cont_held)
    # registered control facts
    assert cont_final["winner"] == "LEN<=9" and cont_final["winner_errors"] == 12319
    assert cont_final["majority_errors"] == 21571
    conj1_cont = cont_final["per_readout_errors"]["LEN<=9&CNT>=1"]
    assert conj1_cont == 75318
    f1_cont = cont_final["winner_errors"] <= cont_final["majority_errors"] // 2
    assert not f1_cont  # the control must NOT clear F1

    # ---- receipt ----
    rec = {
        "schema": "GMI833HRealScaleDecisionTreesScopeV1",
        "scope": "SIGMA_H08R",
        "row": "Decision trees/rule systems.",
        "source": {"path": SOURCE, "sha256": eco.sha, "tokens": eco.N,
                   "descriptors": eco.T},
        "presentation": {"key": "(i*%d) mod 2**32" % ORDER_MULT,
                         "n_fit": n_fit, "n_held": len(sl["held"]),
                         "rank_fit": len(sl["rank_fit"]),
                         "rank_score": len(sl["rank_score"]),
                         "half": sl["half"]},
        "holdout": {"n": len(sl["held"]), "shared": held_pos,
                    "unique": held_neg, "majority": FIT_MAJ,
                    "majority_errors": final["majority_errors"],
                    "winner": final["winner"],
                    "winner_errors": final["winner_errors"],
                    "winner_class": final["winner_class"],
                    "prototype_agreement": prototype_agreement,
                    "per_readout_errors": final["per_readout_errors"],
                    "falsifier1_half_majority": final["majority_errors"] // 2,
                    "falsifier1_holds": final["winner_errors"] <=
                    final["majority_errors"] // 2},
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
                  "same_class": regen["winner_class"] == prim["winner_class"],
                  "class": prim["winner_class"]},
        "nulls": {"label": {"seed": NULL_SEED_LABEL, "errors": label_null,
                            "gt_majority": label_null > final["majority_errors"],
                            "shuffled_labels": [int(v) for v in sh]},
                  "design": {"seed": NULL_SEED_DESIGN, "errors": design_null,
                             "predictions": [int(v) for v in design_preds],
                             "bound_3x_arm": 3 * final["winner_errors"],
                             "gt_3x_arm": design_null > 3 * final["winner_errors"]}},
        "holdout_all": {"rows": len(held_y),
                        "queries": [[int(yv), int(p)] for yv, p in
                                    zip(held_y, winner_preds)]},
        "ladder": {"readout": "LEN<=9&CNT>=1",
                   "budgets": [m for m, _ in ladder],
                   "errors": [e for _, e in ladder], "monotone": monotone},
        "crossover": {"V": V, "alphabet_width": ALPHABET_WIDTH,
                      "index_cost": index_cost, "m_star": m_star,
                      "scan_cost_at_m_star": 2 * m_star,
                      "holds": 2 * m_star > index_cost},
        "presentation_control": {"winner": cont_final["winner"],
                                 "winner_errors": cont_final["winner_errors"],
                                 "winner_class": cont_final["winner_class"],
                                 "majority_errors": cont_final["majority_errors"],
                                 "conj1_errors": conj1_cont,
                                 "f1_holds": f1_cont,
                                 "control_fires": not f1_cont},
        "replay": {
            "held_block": {"rows": len(held_block),
                           "queries": held_block,
                           "winner_errors": _block_errors(held_block,
                                                          final["winner"])},
            "rank_block": {"rows": len(rank_block),
                           "queries": rank_block,
                           "winner_errors": _block_errors(rank_block,
                                                          rank["winner"])},
            "regen_lo_block": {"rows": len(regen_block_lo),
                               "queries": regen_block_lo,
                               "winner_errors": _block_errors(regen_block_lo,
                                                              regen["winner"])},
            "regen_hi_block": {"rows": len(regen_block_hi),
                               "queries": regen_block_hi,
                               "winner_errors": _block_errors(regen_block_hi,
                                                              prim["winner"])}},
    }
    out = os.path.join(RUNS, "scope_SIGMA_H08R.json")
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
    with open(os.path.join(RUNS, "sources.json"), "w") as fh:
        json.dump({"schema": "GMI833HRealScaleSourcesV1",
                   "source": {"path": SOURCE, "sha256": eco.sha,
                              "tokens": eco.N, "descriptors": eco.T}},
                  fh, indent=1, sort_keys=True)
    print("WROTE %s (%.1fs)" % (out, time.time() - t0), flush=True)
    print("winner %s held_errors %d prototype_agreement %d"
          % (final["winner"], final["winner_errors"], prototype_agreement),
          flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
