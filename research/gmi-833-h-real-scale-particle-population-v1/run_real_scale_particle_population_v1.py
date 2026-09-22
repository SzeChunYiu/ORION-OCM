#!/usr/bin/env python3
"""Real-scale run driver for gmi-833-h-real-scale-particle-population-v1.

Runs on the host of record (FREEZE_V1.md section 4): billy-old, Linux,
CPython 3.14.4. Reads the sha256-bound external source D, builds the F19
stored-particle-population ecology, applies the registered target-independent
Knuth presentation (FREEZE_V1_SLICE_ADDENDUM.md), scores every readout of the
registered language R (63 arms) on the rank stage, the symmetric half-split
regeneration (R2.1), the full-scale held set and the matched source-order
presentation (R2.4), writes the frozen-prediction record (R08) BEFORE any null
or control is computed, and writes the receipts under REAL_RUNS/ that the
stdlib checker replays exactly and the independent oracle re-derives.

Stdlib only: every quantity is an exact integer decision count. No float enters
any count, comparison, loss, or claim.

Usage:  python3 -B run_real_scale_particle_population_v1.py
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
VOTE_K = 3
MIN_POP = 2
LEN_L = tuple(range(6, 13))
CNT_K = (1, 2, 3)
ASSOC_K = (1, 2, 3)
READOUTS = (("C0", "C1")
            + tuple("LEN<=%d" % L for L in LEN_L)
            + tuple("CNT>=%d" % K for K in CNT_K)
            + tuple("ASSOC>=%d" % K for K in ASSOC_K)
            + tuple("LEN<=%d&CNT>=%d" % (L, j) for L in LEN_L for j in CNT_K)
            + tuple("LEN<=%d&ASSOC>=%d" % (L, j) for L in LEN_L for j in ASSOC_K)
            + ("PLUR", "PLUR_W", "PREF_VOTE", "EXT_VOTE",
               "MEM_FALLBACK", "PARTICLE_1"))

# FREEZE_V1_SLICE_ADDENDUM_R2.md
NULL_SEED_LABEL = 20260926
NULL_SEED_DESIGN = 20260927
LADDER_BUDGETS = (1000, 5000, 10000, 30000, 67912, 135824, 271649)
REPLAY_HELD = 1500
REPLAY_RANK = 1500
REPLAY_REGEN = 2000

SIGMA = "SIGMA_H19R"
ROW = "Particle/population inference."
PREDICTED_CLASS = "POPULATION_PLURALITY"
WINNER = "PLUR"

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
CLASSES["PLUR"] = "POPULATION_PLURALITY"
CLASSES["PLUR_W"] = "POPULATION_PLURALITY"
CLASSES["PREF_VOTE"] = "NEIGHBORHOOD_MAJORITY_VOTE"
CLASSES["EXT_VOTE"] = "NEIGHBORHOOD_MAJORITY_VOTE"
CLASSES["MEM_FALLBACK"] = "STORED_TABLE_READ_WITH_FALLBACK"
CLASSES["PARTICLE_1"] = "STORED_SINGLE_PARTICLE_READ_WITH_FALLBACK"

COST = dict((r, 0) for r in READOUTS)
for r in READOUTS:
    if r.startswith("CNT>=") or r.startswith("ASSOC>="):
        COST[r] = 1
    if "&" in r:
        COST[r] = 1
COST["PARTICLE_1"] = 1
COST["MEM_FALLBACK"] = 2    # one membership lookup and one stored-table read

FIT_MAJ = 1


def classify(name):
    return CLASSES[name]


def order_key(i):
    """FREEZE_V1_SLICE_ADDENDUM.md: key(i) = (i * 2654435761) mod 2**32."""
    return (i * ORDER_MULT) % (2 ** 32)


class F19(object):
    """The registered ecology: the stored-particle-population table over the
    sha-bound bytes. A query q is a descriptor (a prefix of length >= 2 of a
    source token) with at least MIN_POP particles: pop(q) = the distinct
    one-letter extensions of q over the FULL source. A particle p votes 1 iff
    its source occurrence count is >= VOTE_K. The protected interface is
    y(q) = 1 iff the STRICT plurality of pop(q) votes 1 (ties -> 0). The
    family is particle / population inference: the answer is the consensus over
    a population of many weak samples, not the value of any single sample."""

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
        uniq = sorted(set(DL))
        self.uniq = uniq
        self.idx = dict((q, i) for i, q in enumerate(uniq))
        self.V = len(uniq)
        # the particle population: the distinct one-letter extensions of q
        children = [[] for _ in range(self.V)]
        for q in uniq:
            i = self.idx[q]
            lo = bisect_left(uniq, q)
            hi = bisect_right(uniq, q + "\x7f")
            for m in range(lo, hi):
                if len(uniq[m]) == len(q) + 1:
                    children[i].append(self.idx[uniq[m]])
        self.children = children
        self.cntU = [cnt[q] for q in uniq]
        # the registered particle vote: source occurrence count >= VOTE_K
        self.vote = bytearray(1 if self.cntU[i] >= VOTE_K else 0
                              for i in range(self.V))
        # the registered protected interface: strict plurality over pop(q)
        ylab = {}
        for q in uniq:
            i = self.idx[q]
            ch = children[i]
            if len(ch) < MIN_POP:
                ylab[q] = 0
                continue
            a = sum(1 for j in ch if self.vote[j])
            ylab[q] = 1 if a * 2 > len(ch) else 0
        self.ylab = ylab
        self.y = [ylab[q] for q in DL]
        self.n_scored_distinct = sum(1 for q in uniq
                                     if len(children[self.idx[q]]) >= MIN_POP)

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

    def scored(self, pos):
        """The registered scored query set restricted to `pos`, in pos order."""
        ch = self.children
        idx = self.idx
        DL = self.DL
        return [i for i in pos if len(ch[idx[DL[i]]]) >= MIN_POP]


class Store(object):
    """The stored particle population table over a set of fit positions."""

    def __init__(self, eco, store_pos):
        self.eco = eco
        self.fc = Counter(eco.DL[i] for i in store_pos)
        self.store_set = set(self.fc)
        self.store_list = sorted(self.store_set)
        # the stored association of a cue q: the distinct letters c such that
        # the descriptor q+c is a STORED descriptor (FREEZE_V1_SLICE_ADDENDUM.md
        # registers this reading; it is the same child-extension relation the
        # particle population uses, without any vote)
        fan = defaultdict(set)
        for q in self.store_set:
            if len(q) >= 3:
                fan[q[:-1]].add(q[-1])
        self.fan = fan
        # the vote the stored table can record for a particle: its STORED
        # occurrence count >= VOTE_K
        self.svote = dict((q, 1 if n >= VOTE_K else 0)
                          for q, n in self.fc.items())
        self.ylab = dict((q, eco.ylab[q]) for q in self.store_set)

    def count_of(self, q):
        return self.fc.get(q, 0)

    def fan_of(self, q):
        """The number of stored children of q: |{ c : q+c is a stored
        descriptor }|. A stored descriptor q+c records c as following q, so
        the fan-out is read over the store's own membership."""
        i = self.eco.idx.get(q)
        if i is None:
            return len(self.fan.get(q, ()))
        n = 0
        for j in self.eco.children[i]:
            if self.eco.uniq[j] in self.store_set:
                n += 1
        return n

    def pref_tally(self, q, ql):
        n1 = n0 = 0
        ss = self.store_set
        yl = self.eco.ylab
        for k in range(2, ql):
            p = q[:k]
            if p in ss:
                if yl[p]:
                    n1 += 1
                else:
                    n0 += 1
        return n1, n0

    def ext_tally(self, q, ql):
        lo = bisect_left(self.store_list, q)
        hi = bisect_right(self.store_list, q + "\x7f")
        n1 = n0 = 0
        yl = self.eco.ylab
        for m in range(lo, hi):
            p = self.store_list[m]
            if len(p) > ql:
                if yl[p]:
                    n1 += 1
                else:
                    n0 += 1
        return n1, n0


def readout_decision(name, ql, c, fa, in_store, p1, p0, e1, e0,
                     n1, n0, nw1, nw0, m1, m0, one_vote):
    """Exact decision of a registered readout from one query's tallies.

    Registered semantics (FREEZE_V1_SLICE_ADDENDUM.md). `n1`/`n0` are the
    stored particles voting 1/0 at their FULL-SOURCE vote, `nw1`/`nw0` the same
    weighted by stored occurrence count, `m1`/`m0` the same at the
    STORED-TABLE vote, `one_vote` one stored particle's full vote
    (-1 when the query has no stored particle). Every empty-population readout
    falls back to the fit majority (1), asserted by the caller before any
    enumeration.
    """
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if "&" in name:
        for part in name.split("&"):
            if readout_decision(part, ql, c, fa, in_store, p1, p0, e1, e0,
                                n1, n0, nw1, nw0, m1, m0, one_vote) == 0:
                return 0
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
    if name.startswith("CNT>="):
        return 1 if c >= int(name.split(">=")[1]) else 0
    if name.startswith("ASSOC>="):
        return 1 if fa >= int(name.split(">=")[1]) else 0
    if name == "PLUR":
        if n1 + n0 == 0:
            return FIT_MAJ
        return 1 if n1 > n0 else 0
    if name == "PLUR_W":
        if nw1 + nw0 == 0:
            return FIT_MAJ
        return 1 if nw1 > nw0 else 0
    if name == "PREF_VOTE":
        if p1 + p0 == 0:
            return FIT_MAJ
        return 1 if p1 > p0 else 0
    if name == "EXT_VOTE":
        if e1 + e0 == 0:
            return FIT_MAJ
        return 1 if e1 > e0 else 0
    if name == "MEM_FALLBACK":
        if not in_store:
            return FIT_MAJ
        if m1 + m0 == 0:
            return FIT_MAJ
        return 1 if m1 > m0 else 0
    if name == "PARTICLE_1":
        if not in_store or one_vote < 0:
            return FIT_MAJ
        return one_vote
    raise ValueError("readout outside the registered language: " + name)


def decide_row(name, row):
    """The registered decision of `name` on one committed tally row."""
    return readout_decision(name, row[0], row[2], row[3], row[4], row[5],
                            row[6], row[7], row[8], row[9], row[10], row[11],
                            row[12], row[13], row[14], row[15])


def tally(eco, store, i, one_particle=False):
    """One query's committed tallies. Row order (16 fields):

        [ql, y, cnt, fanout, in_store, p1, p0, e1, e0,
         n1, n0, nw1, nw0, m1, m0, one_vote]

    one_particle=True collapses the stored particle population to at most one
    particle (the R2.5 single-particle-store control).
    """
    q = eco.DL[i]
    ql = eco.LEN[i]
    ch = eco.children[eco.idx[q]]
    c = store.count_of(q)
    fa = store.fan_of(q)
    in_store = 1 if q in store.store_set else 0
    p1, p0 = store.pref_tally(q, ql)
    e1, e0 = store.ext_tally(q, ql)
    n1 = n0 = nw1 = nw0 = m1 = m0 = 0
    one_vote = -1
    first = None
    for j in ch:
        p = eco.uniq[j]
        if p in store.store_set:
            if first is None:
                first = p
            if one_particle and p != first:
                continue
            v = eco.vote[j]
            if v:
                n1 += 1
                nw1 += store.count_of(p)
            else:
                n0 += 1
                nw0 += store.count_of(p)
            if store.svote[p]:
                m1 += 1
            else:
                m0 += 1
    if first is not None:
        one_vote = eco.vote[eco.idx[first]]
    return [ql, eco.y[i], c, fa, in_store, p1, p0, e1, e0,
            n1, n0, nw1, nw0, m1, m0, one_vote]


def score(eco, store, query_pos, one_particle=False):
    """Score every readout on query_pos. Exact integers only.

    Returns per-readout error counts, per-readout summed charged cost (R2.3),
    the majority rule's errors and the winner of the registered winner rule
    (fewest exact decision errors, then fewer charged-cost units, then readout
    name).
    """
    errs = dict((r, 0) for r in READOUTS)
    costs = dict((r, 0) for r in READOUTS)
    maj = 0
    for i in query_pos:
        row = tally(eco, store, i, one_particle)
        yv = row[1]
        for r in READOUTS:
            if decide_row(r, row) != yv:
                errs[r] += 1
        costs["PLUR"] += row[9] + row[10]
        costs["PLUR_W"] += row[9] + row[10]
        costs["PREF_VOTE"] += row[5] + row[6]
        costs["EXT_VOTE"] += row[7] + row[8]
        if yv != FIT_MAJ:
            maj += 1
    table = sorted((errs[r], costs[r], r) for r in READOUTS)
    winner = table[0][2]
    return {"n": len(query_pos), "per_readout_errors": errs, "costs": costs,
            "majority_errors": maj, "winner": winner,
            "winner_errors": errs[winner], "winner_class": classify(winner),
            "table": table}


def main():
    os.makedirs(RUNS, exist_ok=True)
    t0 = time.time()
    print("loading F19 ecology from %s" % SOURCE, flush=True)
    eco = F19()
    sl = eco.slices()
    n_fit = sl["n_fit"]
    assert n_fit == 679124 and len(sl["held"]) == 97018
    assert len(sl["rank_fit"]) == 475386 and len(sl["rank_score"]) == 203738
    assert sl["half"] == 339562
    print("N=%d T=%d V=%d n_fit=%d n_held=%d"
          % (eco.N, eco.T, eco.V, n_fit, len(sl["held"])), flush=True)

    scored_fit = eco.scored(sl["fit"])
    scored_held = eco.scored(sl["held"])
    scored_rank = eco.scored(sl["rank_score"])
    scored_hi = eco.scored(sl["fit_hi"])
    scored_lo = eco.scored(sl["fit_lo"])
    cont_fit = list(range(n_fit))
    cont_held = list(range(n_fit, eco.T))
    scored_cont = eco.scored(cont_held)
    fit_pos = sum(eco.y[i] for i in scored_fit)
    assert fit_pos * 2 > len(scored_fit), "fit positive fraction not > 1/2"
    assert len(scored_fit) == 373409 and fit_pos == 232779
    assert len(scored_held) == 53230 and len(scored_rank) == 111908
    assert len(scored_hi) == 186725 and len(scored_lo) == 186684
    assert len(scored_cont) == 51783
    print("scored fit=%d (pos %d) held=%d (pos %d) rank=%d hi=%d lo=%d cont=%d"
          % (len(scored_fit), fit_pos, len(scored_held),
             sum(eco.y[i] for i in scored_held), len(scored_rank),
             len(scored_hi), len(scored_lo), len(scored_cont)), flush=True)

    store_fit = Store(eco, sl["fit"])
    store_rank = Store(eco, sl["rank_fit"])
    store_lo = Store(eco, sl["fit_lo"])
    store_hi = Store(eco, sl["fit_hi"])
    store_cont = Store(eco, cont_fit)

    # ---- rank stage (store = rank_fit, score = rank_score) ----
    print("rank stage (store rank_fit, score rank_score)", flush=True)
    rank = score(eco, store_rank, scored_rank)
    assert rank["winner"] == WINNER and rank["winner_errors"] == 5366
    assert rank["majority_errors"] == 42073
    assert rank["per_readout_errors"]["PLUR_W"] == 19169
    assert rank["per_readout_errors"]["MEM_FALLBACK"] == 18310
    assert rank["per_readout_errors"]["PARTICLE_1"] == 25662
    rank_block = [tally(eco, store_rank, i)
                  for i in scored_rank[:REPLAY_RANK]]

    # ---- R09 symmetric half-split regeneration ----
    print("R09 PRIMARY (store fit_lo, score fit_hi)", flush=True)
    prim = score(eco, store_lo, scored_hi)
    assert prim["winner"] == WINNER and prim["winner_errors"] == 16581
    assert prim["majority_errors"] == 70170
    assert prim["per_readout_errors"]["MEM_FALLBACK"] == 49965
    assert prim["per_readout_errors"]["PARTICLE_1"] == 47440
    print("R09 REGEN (store fit_hi, score fit_lo)", flush=True)
    regen = score(eco, store_hi, scored_lo)
    assert regen["winner"] == WINNER and regen["winner_errors"] == 20732
    assert regen["majority_errors"] == 70460
    assert regen["per_readout_errors"]["MEM_FALLBACK"] == 54378
    assert regen["per_readout_errors"]["PARTICLE_1"] == 53136
    regen_block_lo = [tally(eco, store_hi, i) for i in scored_lo[:REPLAY_REGEN]]
    regen_block_hi = [tally(eco, store_lo, i) for i in scored_hi[:REPLAY_REGEN]]

    # ---- final arm (store = full fit, score = held) ----
    print("final arm (store fit, score held)", flush=True)
    final = score(eco, store_fit, scored_held)
    assert final["winner"] == WINNER and final["winner_errors"] == 622
    assert final["majority_errors"] == 20001
    assert final["per_readout_errors"]["PLUR_W"] == 9533
    assert final["per_readout_errors"]["MEM_FALLBACK"] == 2426
    assert final["per_readout_errors"]["PARTICLE_1"] == 12278
    assert final["per_readout_errors"]["CNT>=1"] == 19933
    assert final["per_readout_errors"]["LEN<=9"] == 18338
    assert min(final["per_readout_errors"][r] for r in READOUTS if "&" in r) == 11522
    prototype_agreement = len(scored_held) - final["winner_errors"]
    assert prototype_agreement == 52608
    held_block = [tally(eco, store_fit, i) for i in scored_held[:REPLAY_HELD]]

    # ---- R08: the frozen-prediction record, written BEFORE any null or
    # control is computed. The predictions are the winner's decisions on the
    # scored held queries, in the registered presentation order.
    frozen = {
        "schema": "GMI833HRealScaleParticlePopulationFrozenPredictionsV1",
        "scope": SIGMA, "row": ROW,
        "source_sha256": eco.sha,
        "presentation_key": "(i*%d) mod 2**32" % ORDER_MULT,
        "grammar_digest": grammar_digest(),
        "winner": final["winner"], "winner_class": final["winner_class"],
        "n_scored_held": len(scored_held),
        "positions": [int(i) for i in scored_held],
        "predictions": [decide_row(WINNER, tally(eco, store_fit, i))
                        for i in scored_held],
        "written_before": "any null, control, ladder or crossover of this run",
    }
    frozen_path = os.path.join(RUNS, "FROZEN_PREDICTIONS_R8.json")
    with open(frozen_path, "w") as fh:
        json.dump(frozen, fh, indent=1, sort_keys=True)
        fh.write("\n")
    frozen_sha = hashlib.sha256(open(frozen_path, "rb").read()).hexdigest()
    # the fit is complete before the record is written; assert the record's
    # predictions are exactly the winner's decisions re-derived after writing
    again = [decide_row(WINNER, tally(eco, store_fit, i))
             for i in scored_held]
    assert again == frozen["predictions"]
    assert sum(1 for p, i in zip(again, scored_held) if p != eco.y[i]) == \
        final["winner_errors"]
    print("R08 frozen predictions written (%d rows, sha %s)"
          % (len(again), frozen_sha[:12]), flush=True)

    # ---- nulls (R2.2) ----
    winner_preds = frozen["predictions"]
    held_y = [eco.y[i] for i in scored_held]
    rng = random.Random(NULL_SEED_LABEL)
    sh = held_y[:]
    rng.shuffle(sh)
    label_null = sum(1 for p, v in zip(winner_preds, sh) if p != v)
    assert label_null == 24596
    rng2 = random.Random(NULL_SEED_DESIGN)
    stored_ids = [eco.idx[q] for q in store_fit.store_list]
    vals = [eco.vote[i] for i in stored_ids]
    rng2.shuffle(vals)
    vnull = bytearray(eco.vote)
    for i, v in zip(stored_ids, vals):
        vnull[i] = v
    saved_vote = eco.vote
    eco.vote = vnull
    dn = score(eco, store_fit, scored_held)
    eco.vote = saved_vote
    assert dn["per_readout_errors"]["PLUR"] == 33268
    assert dn["winner"] == "MEM_FALLBACK"
    assert dn["per_readout_errors"]["MEM_FALLBACK"] == 2426
    assert dn["per_readout_errors"]["PARTICLE_1"] == 29697
    assert dn["per_readout_errors"]["CNT>=1"] == 19933
    # the reweighted null's own PLUR predictions, for exact re-derivation
    design_null_preds = []
    eco.vote = vnull
    for i in scored_held:
        design_null_preds.append(decide_row(WINNER, tally(eco, store_fit, i)))
    eco.vote = saved_vote
    assert len(design_null_preds) == len(winner_preds)

    order_held = sorted(range(len(held_y)),
                        key=lambda k: (k * ORDER_MULT) % (2 ** 32))
    keyed = [held_y[k] for k in order_held]
    keyed_label = sum(1 for p, v in zip(winner_preds, keyed) if p != v)
    assert keyed_label == 25010

    # ---- R07 ladder (winner readout PLUR) ----
    ladder = []
    for m in LADDER_BUDGETS:
        st = Store(eco, sl["fit"][:m])
        e = 0
        for i in scored_held:
            row = tally(eco, st, i)
            if decide_row(WINNER, row) != row[1]:
                e += 1
        ladder.append((m, e))
    ladder.append((n_fit, final["winner_errors"]))
    assert [e for _, e in ladder] == [20024, 19914, 19596, 18501, 17014,
                                      14364, 9943, 622]
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
    cont = score(eco, store_cont, scored_cont)
    assert cont["winner"] == "LEN<=6" and cont["winner_errors"] == 15162
    assert cont["majority_errors"] == 21104
    assert cont["per_readout_errors"]["PLUR"] == 21096
    assert cont["per_readout_errors"]["PLUR_W"] == 21100
    assert cont["per_readout_errors"]["MEM_FALLBACK"] == 21160
    assert cont["per_readout_errors"]["PARTICLE_1"] == 21122
    f1_cont = cont["winner_errors"] <= cont["majority_errors"] // 2
    assert not f1_cont  # the control must NOT clear F1

    # ---- R2.5 single-particle-store control ----
    ctrl = score(eco, store_fit, scored_held, one_particle=True)
    assert ctrl["per_readout_errors"]["PLUR"] == 12210
    assert ctrl["per_readout_errors"]["PARTICLE_1"] == 12278
    assert ctrl["per_readout_errors"]["PLUR"] > ctrl["majority_errors"] // 2

    # ---- boundary datum: the store-size-asymmetric complementary split ----
    store_rscore = Store(eco, sl["rank_score"])
    comp = score(eco, store_rscore, eco.scored(sl["rank_fit"]))
    assert comp["per_readout_errors"]["PLUR"] == 46478
    assert comp["majority_errors"] == 98557
    assert comp["winner"] == "LEN<=6&CNT>=3" and comp["winner_errors"] == 38212

    # ---- receipt ----
    rec = {
        "schema": "GMI833HRealScaleParticlePopulationScopeV1",
        "scope": SIGMA, "row": ROW,
        "source": {"path": SOURCE, "sha256": eco.sha, "tokens": eco.N,
                   "descriptors": eco.T, "distinct_descriptors": eco.V},
        "presentation": {"key": "(i*%d) mod 2**32" % ORDER_MULT,
                         "n_fit": n_fit, "n_held": len(sl["held"]),
                         "rank_fit": len(sl["rank_fit"]),
                         "rank_score": len(sl["rank_score"]),
                         "half": sl["half"]},
        "ecology": {
            "vote_k": VOTE_K, "min_pop": MIN_POP,
            "distinct_scored": eco.n_scored_distinct,
            "distinct_vote1": sum(eco.vote),
            "scored_fit": len(scored_fit), "scored_fit_positive": fit_pos,
            "fit_majority": FIT_MAJ,
            "scored_held": len(scored_held),
            "scored_held_positive": sum(eco.y[i] for i in scored_held),
            "scored_rank": len(scored_rank),
            "scored_hi": len(scored_hi), "scored_lo": len(scored_lo),
            "scored_cont": len(scored_cont),
            "classes": sorted(set(CLASSES[r] for r in READOUTS)),
        },
        "grammar": {"digest": grammar_digest(), "readouts": len(READOUTS)},
        "holdout": {"n": len(scored_held), "positive": sum(eco.y[i] for i in scored_held),
                    "negative": len(scored_held) - sum(eco.y[i] for i in scored_held),
                    "majority": FIT_MAJ,
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
                              "majority_errors": prim["majority_errors"],
                              "per_readout_errors": prim["per_readout_errors"]},
                  "regen": {"store": "fit_hi", "score": "fit_lo",
                            "n": regen["n"], "winner": regen["winner"],
                            "winner_errors": regen["winner_errors"],
                            "winner_class": regen["winner_class"],
                            "majority_errors": regen["majority_errors"],
                            "per_readout_errors": regen["per_readout_errors"]},
                  "same_class": regen["winner_class"] == prim["winner_class"] ==
                  rank["winner_class"] == final["winner_class"],
                  "class": prim["winner_class"]},
        "nulls": {"label": {"seed": NULL_SEED_LABEL, "errors": label_null,
                            "gt_majority": label_null > final["majority_errors"],
                            "shuffled_labels": [int(v) for v in sh]},
                  "design": {"seed": NULL_SEED_DESIGN, "errors": dn["per_readout_errors"]["PLUR"],
                             "predictions": [int(v) for v in design_null_preds],
                             "bound_3x_arm": 3 * final["winner_errors"],
                             "gt_3x_arm": dn["per_readout_errors"]["PLUR"] >
                             3 * final["winner_errors"],
                             "per_readout_errors": dn["per_readout_errors"],
                             "winner_under_null": dn["winner"]},
                  "keyed_label_boundary": keyed_label},
        "frozen_predictions": {"path": "FROZEN_PREDICTIONS_R8.json",
                               "sha256": frozen_sha, "rows": len(again),
                               "winner": frozen["winner"],
                               "grammar_digest": frozen["grammar_digest"],
                               "matches_holdout": again == winner_preds},
        "holdout_all": {"rows": len(held_y),
                        "queries": [[int(yv), int(p)] for yv, p in
                                    zip(held_y, winner_preds)]},
        "ladder": {"readout": WINNER,
                   "budgets": [m for m, _ in ladder],
                   "errors": [e for _, e in ladder], "monotone": monotone},
        "crossover": {"V": V, "alphabet_width": ALPHABET_WIDTH,
                      "index_cost": index_cost, "m_star": m_star,
                      "scan_cost_at_m_star": 2 * m_star,
                      "holds": 2 * m_star > index_cost},
        "presentation_control": {"winner": cont["winner"],
                                 "winner_errors": cont["winner_errors"],
                                 "winner_class": cont["winner_class"],
                                 "majority_errors": cont["majority_errors"],
                                 "plur_errors": cont["per_readout_errors"]["PLUR"],
                                 "plur_w_errors": cont["per_readout_errors"]["PLUR_W"],
                                 "memfb_errors": cont["per_readout_errors"]["MEM_FALLBACK"],
                                 "part1_errors": cont["per_readout_errors"]["PARTICLE_1"],
                                 "f1_holds": f1_cont,
                                 "control_fires": not f1_cont},
        "single_particle_store": {
            "plur_errors": ctrl["per_readout_errors"]["PLUR"],
            "part1_errors": ctrl["per_readout_errors"]["PARTICLE_1"],
            "majority_errors": ctrl["majority_errors"],
            "winner": ctrl["winner"],
            "winner_errors": ctrl["winner_errors"],
            "f1_holds": ctrl["per_readout_errors"]["PLUR"] <=
            ctrl["majority_errors"] // 2,
            "control_fires": ctrl["per_readout_errors"]["PLUR"] >
            ctrl["majority_errors"] // 2},
        "complementary_split": {
            "store": "rank_score", "score": "rank_fit", "n": comp["n"],
            "winner": comp["winner"], "winner_errors": comp["winner_errors"],
            "plur_errors": comp["per_readout_errors"]["PLUR"],
            "majority_errors": comp["majority_errors"]},
        "replay": {
            "held_block": {"rows": len(held_block), "queries": held_block,
                           "winner": final["winner"],
                           "winner_errors": block_errors(held_block, final["winner"])},
            "rank_block": {"rows": len(rank_block), "queries": rank_block,
                           "winner": rank["winner"],
                           "winner_errors": block_errors(rank_block, rank["winner"])},
            "regen_lo_block": {"rows": len(regen_block_lo),
                               "queries": regen_block_lo,
                               "winner": regen["winner"],
                               "winner_errors": block_errors(regen_block_lo,
                                                            regen["winner"])},
            "regen_hi_block": {"rows": len(regen_block_hi),
                               "queries": regen_block_hi,
                               "winner": prim["winner"],
                               "winner_errors": block_errors(regen_block_hi,
                                                            prim["winner"])},
        },
    }
    out = os.path.join(RUNS, "scope_SIGMA_H19R.json")
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
    with open(os.path.join(RUNS, "sources.json"), "w") as fh:
        json.dump({"schema": "GMI833HRealScaleSourcesV1",
                   "source": {"path": SOURCE, "sha256": eco.sha,
                              "tokens": eco.N, "descriptors": eco.T}},
                  fh, indent=1, sort_keys=True)
    print("WROTE %s (%.1fs)" % (out, time.time() - t0), flush=True)
    print("winner %s err %d agreement %d" % (final["winner"],
                                             final["winner_errors"],
                                             prototype_agreement), flush=True)
    print("DONE", flush=True)


def block_errors(rows, name):
    e = 0
    for row in rows:
        if decide_row(name, row) != row[1]:
            e += 1
    return e


def grammar_digest():
    h = hashlib.sha256()
    h.update("+".join(READOUTS).encode())
    h.update(("VOTE_K=%d;MIN_POP=%d" % (VOTE_K, MIN_POP)).encode())
    h.update(("key(i)=(i*%d) mod 2**32" % ORDER_MULT).encode())
    return h.hexdigest()


if __name__ == "__main__":
    main()
