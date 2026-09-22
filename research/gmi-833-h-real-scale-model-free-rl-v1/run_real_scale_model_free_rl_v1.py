#!/usr/bin/env python3
"""Real-scale run driver for gmi-833-h-real-scale-model-free-rl-v1 (issue
#833, section H, row `Model-free RL-like learning.`, scope SIGMA_HMLR).

Runs on the host of record (FREEZE_V1.md section 4): billy-old, Linux, CPython
3.14.4. Reads the sha256-bound external source D, builds the F_ML experience
table with received outcomes, applies the registered target-independent Knuth
presentation (FREEZE_V1_SLICE_ADDENDUM.md section 1), scores every readout of
the registered language R on the rank stage, the symmetric half-split
regeneration (R2.1), the source-order matched presentation, the matched
negative control (R2.3) and the full-scale held set, and writes the receipts
under REAL_RUNS/ that the stdlib checker replays exactly and the independent
oracle re-derives.

Stdlib only: every quantity is an exact integer decision count. No float enters
any count, comparison, loss, or claim.

Usage:  python3 -B run_real_scale_model_free_rl_v1.py
"""
from bisect import bisect_left, bisect_right
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
T_EXPECT = 671860
REWARD_SET = frozenset("aeiou")
LABEL_DENOM = 2

# FREEZE_V1_SLICE_ADDENDUM.md section 1
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27
LEN_L = tuple(range(6, 13))
CNT_K = (1, 2, 3)
ASSOC_K = (1, 2, 3)
VOTE_J = tuple(range(1, 10))
READOUTS = (("C0", "C1")
            + tuple("LEN<=%d" % L for L in LEN_L)
            + tuple("CNT>=%d" % K for K in CNT_K)
            + tuple("ASSOC>=%d" % K for K in ASSOC_K)
            + tuple("LEN<=%d&CNT>=%d" % (L, K) for L in LEN_L for K in CNT_K)
            + tuple("LEN<=%d&ASSOC>=%d" % (L, K) for L in LEN_L for K in ASSOC_K)
            + ("PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK", "RECENCY_LAST")
            + tuple("VOTE>=%d/10" % j for j in VOTE_J))

# FREEZE_V1_SLICE_ADDENDUM_R2.md
SEED_LABEL = 20260931
SEED_DESIGN = 20260932
SEED_CONTROL = 20260933
CONTROL_MULT = 7919
CONTROL_PER_MILLE = 322
CONTROL_BAND = (300, 340)
LADDER_BUDGETS = (1000, 5000, 10000, 30000, 67912, 135824, 271649)
REPLAY_HELD = 1500
REPLAY_OTHER = 1500

CLASSES = {}
for r in READOUTS:
    if r in ("C0", "C1"):
        CLASSES[r] = "CONSTANT_ARM"
    elif "&" in r:
        CLASSES[r] = "THRESHOLD_CONJUNCTION"
    elif r.startswith("LEN<="):
        CLASSES[r] = "DESCRIPTOR_LENGTH_THRESHOLD"
    elif r.startswith("CNT>="):
        CLASSES[r] = "STORED_EXEMPLAR_COUNT_THRESHOLD"
    elif r.startswith("ASSOC>="):
        CLASSES[r] = "CUE_ASSOCIATION_FANOUT"
    elif r.startswith("VOTE>="):
        CLASSES[r] = "REWARD_PROPENSITY_ACCUMULATION"
    elif r in ("PREF_VOTE", "EXT_VOTE"):
        CLASSES[r] = "NEIGHBORHOOD_MAJORITY_VOTE"
    elif r == "MEM_FALLBACK":
        CLASSES[r] = "STORED_OUTCOME_READ_WITH_FALLBACK"
    else:
        CLASSES[r] = "STORED_LAST_OUTCOME_READ_WITH_FALLBACK"

# Registered design statistics the run must reproduce (FREEZE_V1_SLICE_ADDENDUM
# _R2.md R2.1-R2.4). A mismatch fails the run closed before any receipt exists.
EXPECT = {
    "T": 671860,
    "n_fit": 587877,
    "n_held": 83983,
    "rank_fit": 411513,
    "rank_score": 176364,
    "fit_lo": 293938,
    "fit_hi": 293939,
    "distinct_states": 1805,
    "fit_distinct_contexts": 159259,
    "all_distinct_contexts": 168834,
    "label_positives": 216614,
    "fit_positives": 189392,
    "rank_fit_positives": 132705,
    "fit_lo_positives": 94668,
    "fit_hi_positives": 94724,
    "src_fit_positives": 192062,
    "held_positives": 27222,
    "rank_score_positives": 56687,
    "src_held_positives": 24552,
    "rank_majority_errors": 56687,
    "rank_winner": "VOTE>=5/10",
    "rank_winner_errors": 1303,
    "rank_winner_cost": 221841397,
    "rank_fallback_used": 67,
    "held_majority_errors": 27222,
    "held_winner": "VOTE>=5/10",
    "held_winner_errors": 931,
    "held_winner_cost": 150604945,
    "held_fallback_used": 11,
    "primary_majority_errors": 94724,
    "primary_winner_errors": 5457,
    "primary_winner_cost": 263883983,
    "primary_fallback_used": 182,
    "regen_majority_errors": 94668,
    "regen_winner_errors": 6923,
    "regen_winner_cost": 263883983,
    "regen_fallback_used": 213,
    "src_majority_errors": 24552,
    "src_winner": "VOTE>=5/10",
    "src_winner_errors": 23237,
    "src_winner_cost": 14624750,
    "src_fallback_used": 79244,
    "label_null": 36939,
    "design_null": 27222,
    "control_mass": 189016,
    "control_mass_all": 216073,
    "control_winner": "MEM_FALLBACK",
    "control_winner_errors": 18132,
    "control_best_value_arm": "VOTE>=4/10",
    "control_best_value_errors": 27215,
    "control_zero_winner": "MEM_FALLBACK",
    "control_zero_winner_errors": 18132,
    "ladder": [19952, 10601, 8062, 6064, 4389, 2905, 1761, 931],
    "V": 159259,
    "m_star": 79644,
    "mem_stored_one": 40149,
    "mem_stored_zero": 119110,
    "mem_rank": 38261,
    "mem_held": 18132,
    "mem_primary": 64437,
    "mem_regen": 64524,
    "recency_rank": 42446,
    "recency_held": 21020,
    "cnt1_held": 49503,
    "assoc2_held": 39241,
    "len9_held": 53651,
    "conj_held": 48217,
    "asym_winner_errors": 10499,
    "asym_majority_errors": 132705,
    "asym_covered": 54014,
    "asym_score_contexts": 79684,
}


def order_key(i):
    """FREEZE_V1_SLICE_ADDENDUM.md section 1."""
    return (i * ORDER_MULT) % (2 ** 32)


class FML(object):
    """The registered ecology: the experience table over the sha-bound bytes.

    An experience is (context q = w[:k], received outcome rho(w[k])) for every
    token w and every 2 <= k <= len(w) - 1. The state of an experience is
    sigma(q) = (q[:1], q[-1:]); the protected label is the accumulated-feedback
    threshold 2 * P(sigma(q)) >= N(sigma(q)) over the whole table.
    """

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
        ctx = []
        rho = []
        for w in words:
            for k in range(2, len(w)):
                ctx.append(w[:k])
                rho.append(1 if w[k] in REWARD_SET else 0)
        self.T = len(ctx)
        if self.T != T_EXPECT:
            raise SystemExit("EXPERIENCE COUNT MISMATCH: %d != %d"
                             % (self.T, T_EXPECT))
        self.CTX = ctx
        self.RHO = rho
        self.LEN = [len(q) for q in ctx]
        self.ST = [(q[0], q[-1]) for q in ctx]
        fn = Counter(self.ST)
        fp = Counter()
        for i in range(self.T):
            fp[self.ST[i]] += rho[i]
        self.FN = fn
        self.FP = fp
        self.LAB = dict((c, 1 if LABEL_DENOM * fp[c] >= fn[c] else 0)
                        for c in fn)
        self.Y = [self.LAB[self.ST[i]] for i in range(self.T)]
        # stored outcome the table records for a context (the run says what it
        # means: a context is a prefix of one or more tokens, and the stored
        # outcome it records is READ from the descriptor's own observed action,
        # which is the same for every token sharing the context up to that
        # length; where a context occurs under more than one action the stored
        # outcome is the registered majority of its stored occurrences).
        sn = Counter()
        sp = Counter()
        for i in range(self.T):
            sn[ctx[i]] += 1
            sp[ctx[i]] += rho[i]
        self.OBS = dict((q, 1 if LABEL_DENOM * sp[q] >= sn[q] else 0) for q in sn)

    def slices(self):
        order = sorted(range(self.T), key=order_key)
        n_fit = (self.T * 7) // 8
        fit = order[:n_fit]
        held = order[n_fit:]
        rank_fit = fit[:(7 * n_fit) // 10]
        rank_score = fit[(7 * n_fit) // 10:]
        half = n_fit // 2
        return {"order": order, "n_fit": n_fit, "fit": fit, "held": held,
                "rank_fit": rank_fit, "rank_score": rank_score,
                "fit_lo": fit[:half], "fit_hi": fit[half:], "half": half}


class Store(object):
    """The stored experience table over a set of fit positions."""

    def __init__(self, eco, store_pos, rho=None):
        if rho is None:
            rho = eco.RHO
        self.eco = eco
        self.fc = Counter(eco.CTX[i] for i in store_pos)
        self.sset = set(self.fc)
        self.slist = sorted(self.sset)
        self.fan = defaultdict(set)
        for q in self.sset:
            if len(q) >= 2:
                self.fan[q[:-1]].add(q[-1])
        self.sn = Counter()
        self.sp = Counter()
        self.last = {}
        for i in store_pos:
            self.sn[eco.ST[i]] += 1
            self.sp[eco.ST[i]] += rho[i]
            self.last[eco.CTX[i]] = rho[i]
        self.cell_n = sum(self.sn.values())
        self.cell_p = sum(self.sp.values())
        self.maj = 1 if LABEL_DENOM * self.cell_p >= self.cell_n else 0

    def cnt_of(self, q):
        return self.fc.get(q, 0)

    def fan_of(self, q):
        return len(self.fan.get(q, ()))

    def cell_of(self, i):
        s = self.eco.ST[i]
        return self.sn.get(s, 0), self.sp.get(s, 0)

    def pref_tally(self, q, ql):
        n1 = n0 = 0
        for k in range(2, ql):
            p = q[:k]
            if p in self.sset:
                if self.eco.OBS[p]:
                    n1 += 1
                else:
                    n0 += 1
        return n1, n0

    def ext_tally(self, q, ql):
        lo = bisect_left(self.slist, q)
        hi = bisect_right(self.slist, q + "\x7f")
        n1 = n0 = 0
        for m in range(lo, hi):
            p = self.slist[m]
            if len(p) > ql:
                if self.eco.OBS[p]:
                    n1 += 1
                else:
                    n0 += 1
        return n1, n0


def readout_decision(name, ql, cnt, fan, in_store, stored, last, n_cell, p_cell, maj,
                     p1, p0, e1, e0):
    """The registered readout semantics (FREEZE_V1_SLICE_ADDENDUM.md section 2)."""
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if "&" in name:
        for part in name.split("&"):
            if readout_decision(part, ql, cnt, fan, in_store, stored, last,
                                n_cell, p_cell, maj, p1, p0, e1, e0) == 0:
                return 0
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
    if name.startswith("CNT>="):
        return 1 if cnt >= int(name.split(">=")[1]) else 0
    if name.startswith("ASSOC>="):
        return 1 if fan >= int(name.split(">=")[1]) else 0
    if name == "PREF_VOTE":
        if p1 + p0 == 0:
            return maj
        return 1 if p1 > p0 else 0
    if name == "EXT_VOTE":
        if e1 + e0 == 0:
            return maj
        return 1 if e1 > e0 else 0
    if name == "MEM_FALLBACK":
        return stored if in_store else maj
    if name == "RECENCY_LAST":
        return last if in_store else maj
    if name.startswith("VOTE>="):
        j = int(name.split(">=")[1].split("/")[0])
        if n_cell == 0:
            return maj
        return 1 if 10 * p_cell >= j * n_cell else 0
    raise ValueError("readout outside the registered language: " + name)


def row_decision(name, row, maj):
    """A readout's decision on one committed replay row."""
    ql, yv, cnt, fan, ins, stored, last, p1, p0, e1, e0, n_cell, p_cell, _st = row
    return readout_decision(name, ql, cnt, fan, ins, stored, last, n_cell,
                            p_cell, maj, p1, p0, e1, e0)


def charged_cost(name, n_cell, p1, p0, e1, e0):
    if name in ("C0", "C1") or (name.startswith("LEN<=") and "&" not in name):
        return 0
    if name.startswith("VOTE>="):
        return n_cell
    if name == "MEM_FALLBACK":
        return 2
    if name == "RECENCY_LAST":
        return 1
    if name == "PREF_VOTE":
        return p1 + p0
    if name == "EXT_VOTE":
        return e1 + e0
    return 1


def tally_row(eco, store, i, cell_n=None, cell_p=None):
    """One committed replay row. The row carries everything a second route
    needs to recompute every arm's decision: the length, the registered label,
    the store tallies, the state key and the store's cell mass at that state.
    A route that scores a DIFFERENT store (the matched negative control, the
    design null) substitutes its own cell mass via the state key."""
    q = eco.CTX[i]
    ql = eco.LEN[i]
    cnt = store.cnt_of(q)
    fan = store.fan_of(q)
    ins = 1 if q in store.sset else 0
    stored = eco.OBS.get(q, store.maj)
    last = store.last.get(q, store.maj)
    p1, p0 = store.pref_tally(q, ql)
    e1, e0 = store.ext_tally(q, ql)
    if cell_n is None:
        n_cell, p_cell = store.cell_of(i)
    else:
        key = "%s%s" % eco.ST[i]
        n_cell = cell_n.get(key, 0)
        p_cell = cell_p.get(key, 0)
    return [ql, eco.Y[i], cnt, fan, ins, stored, last, p1, p0, e1, e0,
            n_cell, p_cell, "%s%s" % eco.ST[i]]


def score(eco, store, query_pos, cell_n=None, cell_p=None):
    """Score every readout of R on query_pos. Exact integers only.

    Returns the per-readout error counts, the per-readout summed charged cost,
    the fallback rule's error count, the registered winner (fewest exact
    decision errors, then fewer charged-cost units, then arm name) and the set
    of arms attaining the minimum error count.
    """
    errs = dict((r, 0) for r in READOUTS)
    costs = dict((r, 0) for r in READOUTS)
    maj = store.maj
    maj_err = 0
    fallback = 0
    for i in query_pos:
        q = eco.CTX[i]
        ql = eco.LEN[i]
        yv = eco.Y[i]
        if yv != maj:
            maj_err += 1
        cnt = store.cnt_of(q)
        fan = store.fan_of(q)
        ins = 1 if q in store.sset else 0
        stored = eco.OBS.get(q, maj)
        last = store.last.get(q, maj)
        p1, p0 = store.pref_tally(q, ql)
        e1, e0 = store.ext_tally(q, ql)
        if cell_n is None:
            n_cell = store.sn.get(eco.ST[i], 0)
            p_cell = store.sp.get(eco.ST[i], 0)
        else:
            k = "%s%s" % eco.ST[i]
            n_cell = cell_n.get(k, 0)
            p_cell = cell_p.get(k, 0)
        if n_cell == 0:
            fallback += 1
        for r in READOUTS:
            if readout_decision(r, ql, cnt, fan, ins, stored, last,
                                n_cell, p_cell, maj, p1, p0, e1, e0) != yv:
                errs[r] += 1
            costs[r] += charged_cost(r, n_cell, p1, p0, e1, e0)
    tab = sorted(READOUTS, key=lambda r: (errs[r], costs[r], r))
    winner = tab[0]
    min_set = sorted(r for r in READOUTS if errs[r] == errs[winner])
    return {"n": len(query_pos), "maj": maj, "maj_err": maj_err,
            "fallback_used": fallback, "errs": errs, "costs": costs,
            "winner": winner, "winner_errors": errs[winner],
            "winner_cost": costs[winner], "winner_class": CLASSES[winner],
            "minimum_error_set": min_set}


def control_masses(eco, store_pos):
    """The matched negative control of FREEZE_V1_SLICE_ADDENDUM_R2.md R2.3: a
    per-experience Bernoulli received outcome with the registered marginal,
    whose cell masses carry no information about the outcomes their own
    experiences received."""
    masses = {}
    ones = 0
    for i in store_pos:
        s = "%s%s" % eco.ST[i]
        if s not in masses:
            masses[s] = [0, 0]
        r = 1 if random.Random(SEED_CONTROL * CONTROL_MULT + i).randrange(1000) \
            < CONTROL_PER_MILLE else 0
        masses[s][0] += 1
        masses[s][1] += r
        ones += r
    return masses, ones


def main():
    os.makedirs(RUNS, exist_ok=True)
    t0 = time.time()
    print("loading F_ML from %s" % SOURCE, flush=True)
    eco = FML()
    sl = eco.slices()
    n_fit = sl["n_fit"]
    assert eco.T == EXPECT["T"]
    assert n_fit == EXPECT["n_fit"] and len(sl["held"]) == EXPECT["n_held"]
    assert len(sl["rank_fit"]) == EXPECT["rank_fit"]
    assert len(sl["rank_score"]) == EXPECT["rank_score"]
    assert len(sl["fit_lo"]) == EXPECT["fit_lo"] and len(sl["fit_hi"]) == EXPECT["fit_hi"]
    assert len(eco.FN) == EXPECT["distinct_states"]
    assert len(set(eco.CTX[i] for i in sl["fit"])) == EXPECT["fit_distinct_contexts"]
    assert len(set(eco.CTX)) == EXPECT["all_distinct_contexts"]
    assert sum(eco.Y) == EXPECT["label_positives"]
    print("N=%d T=%d n_fit=%d n_held=%d states=%d label_positives=%d"
          % (eco.N, eco.T, n_fit, len(sl["held"]), len(eco.FN), sum(eco.Y)), flush=True)

    stores = {
        "rank": Store(eco, sl["rank_fit"]),
        "held": Store(eco, sl["fit"]),
        "primary": Store(eco, sl["fit_lo"]),
        "regen": Store(eco, sl["fit_hi"]),
        "source_order": Store(eco, list(range(n_fit))),
    }
    # the registered fallback constant of every registered stream is 0
    for name in sorted(stores):
        assert stores[name].maj == 0, (name, stores[name].maj)
    stage_pos = {
        "rank": sum(1 for i in sl["rank_score"] if eco.Y[i]),
        "held": sum(1 for i in sl["held"] if eco.Y[i]),
        "primary": sum(1 for i in sl["fit_hi"] if eco.Y[i]),
        "regen": sum(1 for i in sl["fit_lo"] if eco.Y[i]),
        "source_order": sum(1 for i in range(n_fit, eco.T) if eco.Y[i]),
        "rank_fit": sum(1 for i in sl["rank_fit"] if eco.Y[i]),
        "fit": sum(1 for i in sl["fit"] if eco.Y[i]),
        "fit_lo": sum(1 for i in sl["fit_lo"] if eco.Y[i]),
        "fit_hi": sum(1 for i in sl["fit_hi"] if eco.Y[i]),
        "src_fit": sum(1 for i in range(n_fit) if eco.Y[i]),
    }
    assert stage_pos["rank"] == EXPECT["rank_score_positives"]
    assert stage_pos["held"] == EXPECT["held_positives"]
    assert stage_pos["fit"] == EXPECT["fit_positives"]
    assert stage_pos["rank_fit"] == EXPECT["rank_fit_positives"]
    assert stage_pos["fit_lo"] == EXPECT["fit_lo_positives"]
    assert stage_pos["fit_hi"] == EXPECT["fit_hi_positives"]
    assert stage_pos["src_fit"] == EXPECT["src_fit_positives"]
    assert stage_pos["source_order"] == EXPECT["src_held_positives"]

    # ---- registered stages ----
    plan = (("rank", "rank_score"), ("held", "held"), ("primary", "fit_hi"),
            ("regen", "fit_lo"), ("source_order", None))
    stages = {}
    for tag, score_key in plan:
        if score_key is None:
            pos = list(range(n_fit, eco.T))
        else:
            pos = sl[score_key]
        print("stage %s" % tag, flush=True)
        res = score(eco, stores[tag], pos)
        stages[tag] = res

    want = {"rank": (EXPECT["rank_winner"], EXPECT["rank_winner_errors"],
                     EXPECT["rank_winner_cost"], EXPECT["rank_majority_errors"],
                     EXPECT["rank_fallback_used"]),
            "held": (EXPECT["held_winner"], EXPECT["held_winner_errors"],
                     EXPECT["held_winner_cost"], EXPECT["held_majority_errors"],
                     EXPECT["held_fallback_used"]),
            "primary": (EXPECT["held_winner"], EXPECT["primary_winner_errors"],
                        EXPECT["primary_winner_cost"], EXPECT["primary_majority_errors"],
                        EXPECT["primary_fallback_used"]),
            "regen": (EXPECT["held_winner"], EXPECT["regen_winner_errors"],
                      EXPECT["regen_winner_cost"], EXPECT["regen_majority_errors"],
                      EXPECT["regen_fallback_used"]),
            "source_order": (EXPECT["src_winner"], EXPECT["src_winner_errors"],
                             EXPECT["src_winner_cost"], EXPECT["src_majority_errors"],
                             EXPECT["src_fallback_used"])}
    for tag in sorted(want):
        w, we, wc, me, fb = want[tag]
        r = stages[tag]
        assert r["winner_errors"] == we and r["maj_err"] == me, (tag, r["winner_errors"], r["maj_err"])
        assert r["winner"] == w and r["winner_cost"] == wc, (tag, r["winner"], r["winner_cost"])
        assert r["fallback_used"] == fb, (tag, r["fallback_used"])
        assert r["minimum_error_set"] == [w], (tag, r["minimum_error_set"])
        assert r["winner_class"] == "REWARD_PROPENSITY_ACCUMULATION"
    assert stages["held"]["errs"]["CNT>=1"] == EXPECT["cnt1_held"]
    assert stages["held"]["errs"]["ASSOC>=2"] == EXPECT["assoc2_held"]
    assert stages["held"]["errs"]["LEN<=9"] == EXPECT["len9_held"]
    assert stages["held"]["errs"]["LEN<=9&CNT>=1"] == EXPECT["conj_held"]
    assert stages["held"]["errs"]["RECENCY_LAST"] == EXPECT["recency_held"]
    assert stages["rank"]["errs"]["RECENCY_LAST"] == EXPECT["recency_rank"]
    assert stages["held"]["errs"]["MEM_FALLBACK"] == EXPECT["mem_held"]
    assert stages["rank"]["errs"]["MEM_FALLBACK"] == EXPECT["mem_rank"]
    assert stages["primary"]["errs"]["MEM_FALLBACK"] == EXPECT["mem_primary"]
    assert stages["regen"]["errs"]["MEM_FALLBACK"] == EXPECT["mem_regen"]
    # R09: the regeneration recovers the same structural class
    assert stages["primary"]["winner_class"] == stages["regen"]["winner_class"]
    assert stages["primary"]["winner_class"] == stages["held"]["winner_class"]

    # ---- explicit falsifiers ----
    held = stages["held"]
    f1 = held["winner_errors"] <= held["maj_err"] // 2
    assert f1, "F1 violated"
    src = stages["source_order"]
    assert not (src["winner_errors"] <= src["maj_err"] // 2), \
        "the source-order matched presentation must NOT clear F1"

    # ---- MEM admission statistic (the constant-branch exclusion rule) ----
    fit_ctx = set(eco.CTX[i] for i in sl["fit"])
    mem_one = sum(1 for q in fit_ctx if eco.OBS[q] == 1)
    mem_zero = sum(1 for q in fit_ctx if eco.OBS[q] == 0)
    assert mem_one == EXPECT["mem_stored_one"] and mem_zero == EXPECT["mem_stored_zero"]
    assert mem_one > 0 and mem_zero > 0

    # ---- R06 lower bound: no strictly cheaper arm attains the winner ----
    strictly_cheaper = [r for r in READOUTS
                        if held["costs"][r] < held["costs"][held["winner"]]]
    assert strictly_cheaper
    best_cheaper = min(strictly_cheaper, key=lambda r: (held["errs"][r], r))
    assert held["errs"][best_cheaper] > held["winner_errors"]
    non_value = [r for r in READOUTS if not r.startswith("VOTE>=")]
    best_non_value = min(non_value, key=lambda r: (held["errs"][r], r))
    assert held["errs"][best_non_value] >= 6 * held["winner_errors"]

    # ---- R07 ladder and crossover ----
    ladder = []
    for m in LADDER_BUDGETS:
        st = Store(eco, sl["fit"][:m])
        e = 0
        for i in sl["held"]:
            n_cell, p_cell = st.cell_of(i)
            if readout_decision("VOTE>=5/10", eco.LEN[i], st.cnt_of(eco.CTX[i]),
                                st.fan_of(eco.CTX[i]),
                                1 if eco.CTX[i] in st.sset else 0,
                                eco.OBS.get(eco.CTX[i], st.maj),
                                st.last.get(eco.CTX[i], st.maj),
                                n_cell, p_cell, st.maj, 0, 0, 0, 0) != eco.Y[i]:
                e += 1
        ladder.append(e)
    ladder.append(held["winner_errors"])
    assert ladder == EXPECT["ladder"], ladder
    assert all(a >= b for a, b in zip(ladder, ladder[1:]))
    V = len(stores["held"].sset)
    assert V == EXPECT["V"]
    index_cost = V + ALPHABET_WIDTH
    m_star = (index_cost // 2) + 1
    assert m_star == EXPECT["m_star"]
    assert 2 * m_star > index_cost and 2 * (m_star - 1) <= index_cost

    # ---- nulls ----
    winner = held["winner"]
    held_ids = list(sl["held"])
    labvec = [eco.Y[i] for i in held_ids]
    preds = []
    for i in held_ids:
        n_cell, p_cell = stores["held"].cell_of(i)
        preds.append(readout_decision(winner, eco.LEN[i],
                                      stores["held"].cnt_of(eco.CTX[i]),
                                      stores["held"].fan_of(eco.CTX[i]),
                                      1 if eco.CTX[i] in stores["held"].sset else 0,
                                      eco.OBS.get(eco.CTX[i], held["maj"]),
                                      stores["held"].last.get(eco.CTX[i], held["maj"]),
                                      n_cell, p_cell, held["maj"], 0, 0, 0, 0))
    assert sum(1 for p, v in zip(preds, labvec) if p != v) == held["winner_errors"]
    sh = labvec[:]
    random.Random(SEED_LABEL).shuffle(sh)
    label_null = sum(1 for p, v in zip(preds, sh) if p != v)
    assert label_null == EXPECT["label_null"], label_null
    assert label_null > held["maj_err"]            # F2
    fit_rho = [eco.RHO[i] for i in sl["fit"]]
    shf = fit_rho[:]
    random.Random(SEED_DESIGN).shuffle(shf)
    dn = Counter()
    dp = Counter()
    for k, i in enumerate(sl["fit"]):
        dn[eco.ST[i]] += 1
        dp[eco.ST[i]] += shf[k]
    design_preds = []
    for i in held_ids:
        s_ = eco.ST[i]
        n_ = dn.get(s_, 0)
        design_preds.append(held["maj"] if n_ == 0
                            else (1 if 10 * dp[s_] >= 5 * n_ else 0))
    design_null = sum(1 for p, v in zip(design_preds, labvec) if p != v)
    assert design_null == EXPECT["design_null"], design_null
    assert design_null > 3 * held["winner_errors"]     # F3

    # ---- matched negative control (R05) and its degenerate boundary ----
    ctl_masses, ctl_ones = control_masses(eco, sl["fit"])
    assert ctl_ones == EXPECT["control_mass"], ctl_ones
    assert CONTROL_BAND[0] * len(sl["fit"]) <= 1000 * ctl_ones <= CONTROL_BAND[1] * len(sl["fit"])
    ctl_all = sum(1 for i in range(eco.T)
                  if random.Random(SEED_CONTROL * CONTROL_MULT + i).randrange(1000)
                  < CONTROL_PER_MILLE)
    assert ctl_all == EXPECT["control_mass_all"], ctl_all
    ctl_n = dict((k, v[0]) for k, v in ctl_masses.items())
    ctl_p = dict((k, v[1]) for k, v in ctl_masses.items())
    ctl = score(eco, stores["held"], held_ids, cell_n=ctl_n, cell_p=ctl_p)
    zc = score(eco, stores["held"], held_ids,
               cell_n=dict((k, 0) for k in ctl_masses),
               cell_p=dict((k, 0) for k in ctl_masses))
    for tag, rr in (("control", ctl), ("control_zero", zc)):
        assert rr["maj_err"] == held["maj_err"]
        assert rr["winner"] == EXPECT["%s_winner" % tag]
        assert rr["winner_errors"] == EXPECT["%s_winner_errors" % tag]
        assert not [r for r in READOUTS if rr["errs"][r] <= rr["maj_err"] // 2], \
            "%s: an arm cleared F1" % tag
        for raw in ("CNT>=1", "ASSOC>=2", "LEN<=9", "LEN<=9&CNT>=1"):
            assert rr["errs"][raw] == held["errs"][raw], (tag, raw)
    assert ctl["errs"][EXPECT["control_best_value_arm"]] == EXPECT["control_best_value_errors"]
    assert ctl["errs"]["VOTE>=5/10"] != 0

    # ---- boundary datum: the store-size-asymmetric complementary split ----
    asym = score(eco, Store(eco, sl["rank_score"]), sl["rank_fit"])
    assert asym["winner"] == "VOTE>=5/10"
    assert asym["winner_errors"] == EXPECT["asym_winner_errors"]
    assert asym["maj_err"] == EXPECT["asym_majority_errors"]
    asym_cov = len(set(eco.CTX[i] for i in sl["rank_score"])
                   & set(eco.CTX[i] for i in sl["rank_fit"]))
    assert asym_cov == EXPECT["asym_covered"]
    assert len(set(eco.CTX[i] for i in sl["rank_score"])) == EXPECT["asym_score_contexts"]

    # ---- replay blocks and the receipt ----
    # Every block carries the per-query tallies a second route needs to
    # recompute EVERY arm's decision, together with the cell masses of the
    # store the block was scored against: the block's own store, the matched
    # negative control's masses, the design null's masses, or the degenerate
    # zero masses. The committed `winner_errors` is the registered stage
    # winner's error count on exactly those rows.
    zero_n = dict((k, 0) for k in ctl_masses)
    zero_p = dict((k, 0) for k in ctl_masses)
    blocks = {
        "rank_block": (stores["rank"], sl["rank_score"][:REPLAY_OTHER], None, None, "rank"),
        "held_block": (stores["held"], sl["held"][:REPLAY_HELD], None, None, "held"),
        "primary_block": (stores["primary"], sl["fit_hi"][:REPLAY_OTHER], None, None, "primary"),
        "regen_block": (stores["regen"], sl["fit_lo"][:REPLAY_OTHER], None, None, "regen"),
        "source_order_block": (stores["source_order"],
                               list(range(n_fit, eco.T))[:REPLAY_OTHER], None, None,
                               "source_order"),
        "control_block": (stores["held"], sl["held"][:REPLAY_HELD], ctl_n, ctl_p,
                          "matched_negative_control"),
        "design_block": (stores["held"], sl["held"][:REPLAY_HELD], dn, dp,
                         "design_null"),
        "zero_block": (stores["held"], sl["held"][:REPLAY_HELD], zero_n, zero_p,
                       "zero_boundary"),
    }
    replay = {}
    for key in sorted(blocks):
        st, pos, cn, cp, tag = blocks[key]
        rows = [tally_row(eco, st, i, cn, cp) for i in pos]
        if tag in stages:
            wname = stages[tag]["winner"]
            bmaj = stages[tag]["maj"]
        elif tag == "matched_negative_control":
            wname, bmaj = ctl["winner"], ctl["maj"]
        elif tag == "design_null":
            wname, bmaj = winner, held["maj"]
        else:
            wname, bmaj = zc["winner"], zc["maj"]
        labels = [eco.Y[i] for i in pos]
        werr = sum(1 for r_, v in zip(rows, labels)
                   if row_decision(wname, r_, bmaj) != v)
        replay[key] = {"stage": tag, "cell_source": ("store" if cn is None
                                                      else "substituted_masses"),
                       "rows": len(rows), "winner": wname,
                       "local_majority": int(1 if 2 * sum(labels) >= len(labels) else 0),
                       "local_majority_errors": int(sum(
                           1 for v in labels
                           if v != (1 if 2 * sum(labels) >= len(labels) else 0))),
                       "winner_errors": int(werr), "queries": rows}
    # the design null's cell masses, committed so a second route can recompute
    # the design-null predictions without the source
    design_masses = dict((("%s%s" % (k[0], k[1])), [dn[k], dp[k]]) for k in dn)

    rec = {
        "schema": "GMI833HRealScaleModelFreeRLScopeV1",
        "scope": "SIGMA_HMLR",
        "row": "Model-free RL-like learning.",
        "source": {"path": SOURCE, "sha256": eco.sha, "tokens": eco.N,
                   "experiences": eco.T, "tokens_below_three": len([w for w in eco.words if len(w) < 3]),
                   "reward_set": sorted(REWARD_SET)},
        "ecology": {"tokens": eco.N, "experiences": eco.T,
                    "distinct_contexts_all": len(set(eco.CTX)),
                    "distinct_contexts_fit": len(fit_ctx),
                    "distinct_states": len(eco.FN),
                    "stored_outcome_one_fit": mem_one,
                    "stored_outcome_zero_fit": mem_zero},
        "label": {"positive": sum(eco.Y), "n": eco.T,
                  "majority_constant": 1 if 2 * sum(eco.Y) >= eco.T else 0,
                  "stage_positives": stage_pos},
        "presentation": {"key": "(i*%d) mod 2**32" % ORDER_MULT,
                         "n_fit": n_fit, "n_held": len(sl["held"]),
                         "rank_fit": len(sl["rank_fit"]),
                         "rank_score": len(sl["rank_score"]),
                         "fit_lo": len(sl["fit_lo"]), "fit_hi": len(sl["fit_hi"])},
        "readout_language": {"count": len(READOUTS), "arms": list(READOUTS),
                             "grammar_digest": hashlib.sha256(
                                 ("+".join(READOUTS) + "key(i)=(i*%d) mod 2**32"
                                  % ORDER_MULT).encode()).hexdigest()},
        "stages": {},
        "nulls": {"label": {"seed": SEED_LABEL, "errors": label_null,
                            "shuffled_labels": [int(v) for v in sh],
                            "gt_majority": bool(label_null > held["maj_err"])},
                  "design": {"seed": SEED_DESIGN, "errors": design_null,
                             "bound_3x_arm": 3 * held["winner_errors"],
                             "gt_3x_arm": bool(design_null > 3 * held["winner_errors"]),
                             "cell_masses": design_masses,
                             "predictions": [int(v) for v in design_preds]}},
        "ladder": {"readout": winner, "budgets": list(LADDER_BUDGETS) + [n_fit],
                   "errors": ladder, "monotone": True},
        "crossover": {"V": V, "alphabet_width": ALPHABET_WIDTH,
                      "index_cost": index_cost, "m_star": m_star,
                      "scan_cost_at_m_star": 2 * m_star,
                      "holds": bool(2 * m_star > index_cost)},
        "matched_negative_control": {
            "seed": SEED_CONTROL, "per_mille": CONTROL_PER_MILLE,
            "band_per_mille": list(CONTROL_BAND), "mass": ctl_ones,
            "cell_masses": dict((k, [v[0], v[1]]) for k, v in ctl_masses.items()),
            "n": ctl["n"], "majority": ctl["maj"],
            "majority_errors": ctl["maj_err"],
            "per_readout_errors": ctl["errs"],
            "per_readout_costs": ctl["costs"],
            "winner": ctl["winner"], "winner_errors": ctl["winner_errors"],
            "arms_clearing_f1": [],
            "raw_arm_errors": dict((r, ctl["errs"][r])
                                   for r in ("CNT>=1", "ASSOC>=2", "LEN<=9",
                                             "LEN<=9&CNT>=1")),
            "boundary_zero_control": {
                "per_readout_errors": zc["errs"], "winner": zc["winner"],
                "winner_errors": zc["winner_errors"], "arms_clearing_f1": [],
                "majority_errors": zc["maj_err"]}},
        "asymmetric_boundary": {"store": "rank_score", "score": "rank_fit",
                                "n": asym["n"], "majority": asym["maj"],
                                "fallback_used": asym["fallback_used"],
                                "per_readout_errors": asym["errs"],
                                "per_readout_costs": asym["costs"],
                                "minimum_error_set": asym["minimum_error_set"],
                                "winner": asym["winner"],
                                "winner_errors": asym["winner_errors"],
                                "majority_errors": asym["maj_err"],
                                "covered_contexts": asym_cov,
                                "score_contexts": len(set(eco.CTX[i] for i in sl["rank_score"])),
                                "note": "boundary datum, not the registered R09"},
        "falsifiers": {
            "F1_arm_le_half_majority": {"bound": held["maj_err"] // 2,
                                        "arm": held["winner_errors"],
                                        "holds": bool(f1)},
            "F2_label_null_gt_majority": {"null": label_null,
                                          "majority": held["maj_err"],
                                          "holds": bool(label_null > held["maj_err"])},
            "F3_design_null_gt_3x_arm": {"null": design_null,
                                         "bound": 3 * held["winner_errors"],
                                         "holds": bool(design_null > 3 * held["winner_errors"])},
            "F4_no_arm_clears_F1_under_the_control": {"arms_clearing": [],
                                                      "holds": True},
        },
        "holdout_all": {"n": len(held_ids),
                        "queries": [[int(eco.Y[i]), int(p)]
                                    for i, p in zip(held_ids, preds)]},
        "replay": replay,
    }
    for tag, res in sorted(stages.items()):
        rec["stages"][tag] = {
            "store": {"rank": "rank_fit", "held": "fit", "primary": "fit_lo",
                      "regen": "fit_hi", "source_order": "source order [0:n_fit)"}[tag],
            "score": {"rank": "rank_score", "held": "held", "primary": "fit_hi",
                      "regen": "fit_lo", "source_order": "source order [n_fit:T)"}[tag],
            "n": res["n"], "majority": res["maj"], "majority_errors": res["maj_err"],
            "fallback_used": res["fallback_used"],
            "per_readout_errors": res["errs"], "per_readout_costs": res["costs"],
            "winner": res["winner"], "winner_errors": res["winner_errors"],
            "winner_cost": res["winner_cost"], "winner_class": res["winner_class"],
            "minimum_error_set": res["minimum_error_set"],
        }
    out = os.path.join(RUNS, "scope_SIGMA_HMLR.json")
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
    with open(os.path.join(RUNS, "sources.json"), "w") as fh:
        json.dump({"schema": "GMI833HRealScaleSourcesV1",
                   "source": {"path": SOURCE, "sha256": eco.sha,
                              "tokens": eco.N, "experiences": eco.T}},
                  fh, indent=1, sort_keys=True)
    print("WROTE %s (%.1fs)" % (out, time.time() - t0), flush=True)
    print("held winner %s errors %d prototype_agreement %d"
          % (winner, held["winner_errors"], held["n"] - held["winner_errors"]),
          flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
