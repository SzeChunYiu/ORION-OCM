#!/usr/bin/env python3
"""Real-scale run driver for gmi-833-h-real-scale-associative-memory-v1.

Runs on the host of record (FREEZE_V1.md section 4): billy-old, Linux,
CPython 3.14.4. Reads the sha256-bound external source D, builds the F06
cue-association ecology, applies the registered target-independent Knuth
presentation (FREEZE_V1_SLICE_ADDENDUM.md), scores every readout of the
registered language R (FREEZE_V1_SLICE_ADDENDUM.md section 2, R2 addendum)
on the rank stage, the symmetric half-split regeneration (R2.1), and the
full-scale held set, and writes the receipts under REAL_RUNS/ that the stdlib
checker replays exactly and the independent oracle re-derives.

Stdlib only: every quantity is an exact integer decision count. No float
enters any count, comparison, loss, or claim.

Usage:  python3 -B run_real_scale_associative_memory_v1.py
"""
from bisect import bisect_left, bisect_right
from collections import defaultdict
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
LEN_L = tuple(range(7, 13))
ASSOC_K = (1, 2, 3)
READOUTS = (
    "C0", "C1",
    "LEN<=7", "LEN<=8", "LEN<=9", "LEN<=10", "LEN<=11", "LEN<=12",
    "ASSOC>=1", "ASSOC>=2", "ASSOC>=3",
    "PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK",
)

# FREEZE_V1_SLICE_ADDENDUM_R2.md
NULL_SEED_LABEL = 20260923
NULL_SEED_ASSOC = 20260924
LADDER_BUDGETS = (1000, 5000, 10000, 30000, 67912, 135824, 271649)

REPLAY_HELD = 1500
REPLAY_RANK = 1500
REPLAY_REGEN = 2000

CLASSES = {
    "C0": "CONSTANT_ARM", "C1": "CONSTANT_ARM",
    "LEN<=7": "DESCRIPTOR_LENGTH_THRESHOLD", "LEN<=8": "DESCRIPTOR_LENGTH_THRESHOLD",
    "LEN<=9": "DESCRIPTOR_LENGTH_THRESHOLD", "LEN<=10": "DESCRIPTOR_LENGTH_THRESHOLD",
    "LEN<=11": "DESCRIPTOR_LENGTH_THRESHOLD", "LEN<=12": "DESCRIPTOR_LENGTH_THRESHOLD",
    "ASSOC>=1": "CUE_ASSOCIATION_RETRIEVAL",
    "ASSOC>=2": "CUE_ASSOCIATION_FANOUT",
    "ASSOC>=3": "CUE_ASSOCIATION_SIZE_THRESHOLD",
    "PREF_VOTE": "NEIGHBORHOOD_MAJORITY_VOTE", "EXT_VOTE": "NEIGHBORHOOD_MAJORITY_VOTE",
    "MEM_FALLBACK": "STORED_ASSOCIATION_READ_WITH_FALLBACK",
}


def classify(name):
    return CLASSES[name]


def order_key(i):
    """FREEZE_V1_SLICE_ADDENDUM.md: key(i) = (i * 2654435761) mod 2**32."""
    return (i * ORDER_MULT) % (2 ** 32)


class F06(object):
    """The registered ecology: the cue-association table over the sha-bound
    bytes. A cue q is a descriptor (prefix of length >= 2 of a source token);
    the stored association A(q) is the set of distinct next letters
    immediately following q across all tokens starting with q (the trie
    fan-out at q)."""

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
        fan = defaultdict(set)
        for w in words:
            for k in range(1, len(w)):
                fan[w[:k]].add(w[k])
        self.fan = fan
        DL = []
        for w in words:
            for L in range(2, len(w) + 1):
                DL.append(w[:L])
        self.T = len(DL)
        if self.T != T_EXPECT:
            raise SystemExit("DESCRIPTOR COUNT MISMATCH: %d != %d"
                             % (self.T, T_EXPECT))
        self.DL = DL
        # Protected interface: y(q) = 1 iff |A(q)| >= 2 (the cue retrieves a
        # multi-element association). |A(q)| = 0 for a full-token descriptor
        # (nothing follows a complete word), which is content-at-the-cue.
        self.ylab = {q: (1 if len(fan.get(q, ())) >= 2 else 0) for q in DL}
        self.y = [self.ylab[q] for q in DL]
        self.LEN = [len(q) for q in DL]

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
    """The stored association table over a set of fit positions."""

    def __init__(self, eco, store_pos):
        self.eco = eco
        self.store_set = set(eco.DL[i] for i in store_pos)
        self.store_fan = defaultdict(set)
        for i in store_pos:
            s = eco.DL[i]
            if len(s) >= 3:
                self.store_fan[s[:-1]].add(s[-1])
        self.ext_list = sorted(self.store_set)
        self.ext_ylab = [eco.ylab[s] for s in self.ext_list]

    def fan_of(self, q):
        return len(self.store_fan.get(q, ()))

    def pref_tally(self, q, ql):
        """(n1, n0) over stored proper prefixes of q, labelled by the
        source-wide association label of each prefix."""
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
        labelled by the source-wide association label."""
        lo = bisect_left(self.ext_list, q)
        hi = bisect_right(self.ext_list, q + "\x7f")
        n1 = n0 = 0
        for m in range(lo, hi):
            p = self.ext_list[m]
            if len(p) > ql:
                if self.ext_ylab[m]:
                    n1 += 1
                else:
                    n0 += 1
        return n1, n0


def readout_decision(name, ql, fa, in_store, p1, p0, e1, e0):
    """Exact decision of a readout on one query (registered language R).

    Empty-neighbourhood readouts fall back to the fit majority (1), asserted
    to be 1 by the caller before any enumeration.
    """
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
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
            return 1 if fa >= 2 else 0
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
        fa = store.fan_of(q)
        in_store = 1 if q in store.store_set else 0
        p1, p0 = store.pref_tally(q, ql)
        e1, e0 = store.ext_tally(q, ql)
        for r in READOUTS:
            if readout_decision(r, ql, fa, in_store, p1, p0, e1, e0) != yv:
                errs[r] += 1
        costs["ASSOC>=1"] += 1
        costs["ASSOC>=2"] += 1
        costs["ASSOC>=3"] += 1
        costs["MEM_FALLBACK"] += 2
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
    [len, true_label, assoc_fanout_in_store, in_store, p1, p0, e1, e0]."""
    rows = []
    for i in query_pos:
        q = eco.DL[i]
        ql = eco.LEN[i]
        fa = store.fan_of(q)
        in_store = 1 if q in store.store_set else 0
        p1, p0 = store.pref_tally(q, ql)
        e1, e0 = store.ext_tally(q, ql)
        rows.append([ql, eco.y[i], fa, in_store, p1, p0, e1, e0])
    return rows


def _winner_preds(eco, store, query_pos):
    return [readout_decision("ASSOC>=2", eco.LEN[i], store.fan_of(eco.DL[i]),
                             1 if eco.DL[i] in store.store_set else 0,
                             0, 0, 0, 0)
            for i in query_pos]


def _block_errors(rows, winner):
    e = 0
    for ql, yv, fa, in_store, p1, p0, e1, e0 in rows:
        if readout_decision(winner, ql, fa, in_store, p1, p0, e1, e0) != yv:
            e += 1
    return e


def main():
    os.makedirs(RUNS, exist_ok=True)
    t0 = time.time()
    print("loading F06 ecology from %s" % SOURCE, flush=True)
    eco = F06()
    sl = eco.slices()
    n_fit = sl["n_fit"]
    assert n_fit == 679124 and len(sl["held"]) == 97018
    assert len(sl["rank_fit"]) == 475386 and len(sl["rank_score"]) == 203738
    assert sl["half"] == 339562
    fit_pos = sum(eco.y[i] for i in sl["fit"])
    assert fit_pos * 2 > n_fit, "fit multi-element fraction not > 1/2"
    print("N=%d T=%d n_fit=%d n_held=%d fit_pos=%d"
          % (eco.N, eco.T, n_fit, len(sl["held"]), fit_pos), flush=True)

    held_y = [eco.y[i] for i in sl["held"]]
    held_pos = sum(held_y)
    held_neg = len(held_y) - held_pos
    assert held_pos == 53243 and held_neg == 43775, (held_pos, held_neg)

    store_fit = Store(eco, sl["fit"])
    store_rank = Store(eco, sl["rank_fit"])
    store_lo = Store(eco, sl["fit_lo"])
    store_hi = Store(eco, sl["fit_hi"])

    # ---- rank stage (store = rank_fit, score = rank_score) ----
    print("rank stage (store rank_fit, score rank_score)", flush=True)
    rank = score(eco, store_rank, sl["rank_score"])
    assert rank["winner"] == "ASSOC>=2" and rank["winner_errors"] == 8600
    assert rank["majority_errors"] == 91819
    rank_block = tally_block(eco, store_rank, sl["rank_score"][:REPLAY_RANK])

    # ---- R09 symmetric half-split regeneration ----
    print("R09 PRIMARY (store fit_lo, score fit_hi)", flush=True)
    prim = score(eco, store_lo, sl["fit_hi"])
    assert prim["winner"] == "ASSOC>=2" and prim["winner_errors"] == 25907
    assert prim["majority_errors"] == 152818
    print("R09 REGEN (store fit_hi, score fit_lo)", flush=True)
    regen = score(eco, store_hi, sl["fit_lo"])
    assert regen["winner"] == "ASSOC>=2" and regen["winner_errors"] == 31249
    assert regen["majority_errors"] == 152848
    regen_block_lo = tally_block(eco, store_hi, sl["fit_lo"][:REPLAY_REGEN])
    regen_block_hi = tally_block(eco, store_lo, sl["fit_hi"][:REPLAY_REGEN])

    # ---- final arm (store = full fit, score = held) ----
    print("final arm (store fit, score held)", flush=True)
    final = score(eco, store_fit, sl["held"])
    assert final["winner"] == "ASSOC>=2" and final["winner_errors"] == 1249
    assert final["majority_errors"] == 43775
    held_block = tally_block(eco, store_fit, sl["held"][:REPLAY_HELD])
    prototype_agreement = len(sl["held"]) - final["winner_errors"]
    assert prototype_agreement == 95769

    # ---- nulls (R2.2) ----
    rng = random.Random(NULL_SEED_LABEL)
    sh = held_y[:]
    rng.shuffle(sh)
    winner_preds = _winner_preds(eco, store_fit, sl["held"])
    assert sum(1 for p, v in zip(winner_preds, held_y) if p != v) == \
        final["winner_errors"]
    label_null = sum(1 for p, v in zip(winner_preds, sh) if p != v)
    assert label_null == 48065
    rng2 = random.Random(NULL_SEED_ASSOC)
    cues = [eco.DL[i][:-1] for i in sl["fit"] if len(eco.DL[i]) >= 3]
    nxts = [eco.DL[i][-1] for i in sl["fit"] if len(eco.DL[i]) >= 3]
    rng2.shuffle(nxts)
    sh_fan = defaultdict(set)
    for c, nn in zip(cues, nxts):
        sh_fan[c].add(nn)
    design_preds = [1 if len(sh_fan.get(eco.DL[i], ())) >= 2 else 0
                    for i in sl["held"]]
    design_null = sum(1 for p, v in zip(design_preds, held_y) if p != v)
    assert design_null == 23969

    # ---- R07 ladder (winner readout ASSOC>=2) + vocabulary crossover ----
    ladder = []
    order = sl["fit"]
    for m in LADDER_BUDGETS:
        st = Store(eco, order[:m])
        e = sum(1 for i in sl["held"]
                if (1 if st.fan_of(eco.DL[i]) >= 2 else 0) != eco.y[i])
        ladder.append((m, e))
    ladder.append((n_fit, final["winner_errors"]))
    assert [e for _, e in ladder] == [49200, 41310, 37421, 30716, 25239,
                                      20226, 13755, 1249]
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
    assert cont_final["winner"] == "LEN<=7" and cont_final["winner_errors"] == 31584
    assert cont_final["majority_errors"] == 45231
    assoc2_cont = cont_final["per_readout_errors"]["ASSOC>=2"]
    assert assoc2_cont == 51702
    f1_cont = cont_final["winner_errors"] <= cont_final["majority_errors"] // 2
    assert not f1_cont  # the control must NOT clear F1

    # ---- receipt ----
    rec = {
        "schema": "GMI833HRealScaleAssociativeMemoryScopeV1",
        "scope": "SIGMA_H06R",
        "row": "Associative memory.",
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
                  "design": {"seed": NULL_SEED_ASSOC, "errors": design_null,
                             "predictions": [int(v) for v in design_preds],
                             "bound_3x_arm": 3 * final["winner_errors"],
                             "gt_3x_arm": design_null > 3 * final["winner_errors"]}},
        "holdout_all": {"rows": len(held_y),
                        "queries": [[int(yv), int(p)] for yv, p in
                                    zip(held_y, winner_preds)]},
        "ladder": {"readout": "ASSOC>=2", "budgets": [m for m, _ in ladder],
                   "errors": [e for _, e in ladder], "monotone": monotone},
        "crossover": {"V": V, "alphabet_width": ALPHABET_WIDTH,
                      "index_cost": index_cost, "m_star": m_star,
                      "scan_cost_at_m_star": 2 * m_star,
                      "holds": 2 * m_star > index_cost},
        "presentation_control": {"winner": cont_final["winner"],
                                 "winner_errors": cont_final["winner_errors"],
                                 "winner_class": cont_final["winner_class"],
                                 "majority_errors": cont_final["majority_errors"],
                                 "assoc2_errors": assoc2_cont,
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
    out = os.path.join(RUNS, "scope_SIGMA_H06R.json")
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
