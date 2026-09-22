#!/usr/bin/env python3
"""Real-scale run driver for gmi-833-h-real-scale-probabilistic-graphical-v1.

Runs on the host of record (FREEZE_V1.md section 4): billy-old, Linux,
CPython 3.14.4. Reads the sha256-bound external source D, builds the F16
stored two-factor graph ecology (R1 = the even-length tokens, R2 = the
odd-length tokens; per-factor occurrence counts and per-factor continuation
fan-outs over a disjoint descriptor partition), applies the registered
target-independent Knuth presentation (FREEZE_V1_SLICE_ADDENDUM.md section 1),
scores every readout of the registered language R (slice addendum section 3,
closed at 54 arms) under the registered winner rule (slice addendum section 4)
at the rank stage, on the two symmetric regeneration halves (R2.1), and on the
full-scale held set, and writes the receipts under REAL_RUNS/ that the stdlib
checker replays exactly and the independent oracle re-derives.

Stdlib only: every quantity is an exact integer decision count. No float
enters any count, comparison, loss, or claim.

Two registered spec values are NOT reproduced by the registered constructions;
they are reported to the coordinator rather than silently adjusted (the run
prints a DISAGREEMENT section, and the receipt carries the measured values):

  * `presentation_control.winner`: the spec lists `C0` at 32,834 errors with
    class CONSTANT_ARM. In the registered source-order arena the score set
    holds 32,834 negatives, so `C0` (which answers 0 for every query) makes
    97,018 - 32,834 = 64,184 errors, not 32,834; the constant arm at exactly
    32,834 errors is `C1`. The registered language's best arm in that arena is
    `LEN<=6` at 22,919 errors, which still fails falsifier 1 (22,919 > 16,417),
    so the control fires exactly as R2.4 requires. The majority (32,834) and
    the family readout (64,099) of the block are reproduced exactly.
  * `single_factor_control.majority_errors`: the spec lists 44,138; under the
    registered single-factor interface |A1(q)| >= 1 the held slice holds 19,277
    negatives, so the fit-majority rule makes 19,277 errors. The block's other
    two magnitudes (the winner `R1ASSOC>=1` at 899 and the best product arm
    `R1ASSOC>=1&R2ASSOC>=1` at 12,437) are reproduced exactly. The joint arm
    losing here is the registered direction of the R06 lower-bound control, not
    a failed gate: it is what shows the joint arm's win on the registered
    ecology is evidence about the JOINT structure and not the readout form.

Both corrections are registered in FREEZE_V1_SLICE_ADDENDUM_R3.md.

The row's registered contract (`TRIPLE_PARITY`, FROZEN_FAMILY_REGISTRY_V1.json)
is recorded as a STEER in FREEZE_V1.md section 2, per the sibling
gmi-833-h-real-scale-decision-trees-v1 precedent. It constrains the STRUCTURE
of the recovered readout (a dependency response over the stored factorisation,
every factor must agree) and supplies no evidence; this package claims no
three-variable arity, and nothing in this driver is adjusted to an arity.

Usage:  python3 -B run_real_scale_pgm_v1.py
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

# FREEZE_V1_SLICE_ADDENDUM.md section 1 and R2.1
ORDER_MULT = 2654435761
N_FIT_EXPECT = 679124
N_HELD_EXPECT = 97018
RANK_FIT_EXPECT = 475386
RANK_SCORE_EXPECT = 203738
HALF_EXPECT = 339562

# FREEZE_V1_SLICE_ADDENDUM.md section 2
R1_OCCURRENCES_EXPECT = 387582
R2_OCCURRENCES_EXPECT = 388560

# FREEZE_V1_SLICE_ADDENDUM.md section 6
ALPHABET_WIDTH = 27
SCAN_COST_MULT = 2

# FREEZE_V1_SLICE_ADDENDUM_R2.md R2.2
NULL_SEED_LABEL = 20260926
NULL_SEED_DESIGN = 20260927
DESIGN_N2_EXPECT = 340066

# FREEZE_V1_SLICE_ADDENDUM.md section 6 (the store ladder budgets)
LADDER_BUDGETS = (1000, 5000, 10000, 30000, 67912, 135824, 271649)

REPLAY_HELD = 1500
REPLAY_RANK = 1500
REPLAY_REGEN = 2000

# The registered label is JOINT CONSISTENCY across the two independent stored
# factors; the registered single-factor ecology control (R2.5) replaces it with
# the R1 factor alone.
LABEL_JOINT = "R1ASSOC>=1&R2ASSOC>=1"
LABEL_SINGLE = "R1ASSOC>=1"
ECM_READOUT = "ECM_PRODUCT_FORM_MESSAGE"

# The four registered stages (store, score).
STAGES = (("rank", "rank_fit", "rank_score"),
          ("held", "fit", "held"),
          ("primary", "fit_lo", "fit_hi"),
          ("regen", "fit_hi", "fit_lo"))

FIT_MAJ = 1  # asserted > 1/2 by the caller before any enumeration


def order_key(i):
    """FREEZE_V1_SLICE_ADDENDUM.md section 1: key(i) = (i*2654435761) mod 2**32."""
    return (i * ORDER_MULT) % (2 ** 32)


class F16(object):
    """The registered ecology: a stored factor graph with two independent
    factors over disjoint token populations.

    FREEZE_V1.md section 4 and slice addendum section 2. A query q is a
    descriptor (a prefix of length >= 2 of a source token). The token list is
    split by a content-external, deterministic rule into R1 = the even-length
    tokens and R2 = the odd-length tokens, so every descriptor occurrence
    belongs to exactly one factor and the two stored relations are disjoint.
    The factor-local evidence of q is

        ci(q) = the number of stored descriptor occurrences of q in factor i
        fi(q) = |Ai(q)|, the factor's continuation fan-out at q -- the number
                of distinct letters that extend a stored descriptor equal to q

    and the label is JOINT CONSISTENCY across the two factors: a query is
    positive exactly when EVERY factor agrees it has a stored continuation.
    This class receives no family name, no row name and no response values; it
    reads only the sha-bound bytes.
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

        # Descriptor closure: every prefix of length >= 2 of every token, with
        # the factor the occurrence belongs to (1 = even-length token).
        DL = []
        FAC = []
        for w in words:
            f = 1 if len(w) % 2 == 0 else 2
            for L in range(2, len(w) + 1):
                DL.append(w[:L])
                FAC.append(f)
        self.DL = DL
        self.FAC = FAC
        self.T = len(DL)
        if self.T != T_EXPECT:
            raise SystemExit("DESCRIPTOR COUNT MISMATCH: %d != %d"
                             % (self.T, T_EXPECT))
        self.r1_occ = sum(1 for f in FAC if f == 1)
        self.r2_occ = self.T - self.r1_occ
        if (self.r1_occ, self.r2_occ) != (R1_OCCURRENCES_EXPECT,
                                          R2_OCCURRENCES_EXPECT):
            raise SystemExit("FACTOR OCCURRENCE SPLIT MISMATCH: %d/%d"
                             % (self.r1_occ, self.r2_occ))

        # The protected interface: the label the stored factor graph records,
        # evaluated over the full source (slice addendum section 7): the query
        # has a continuation in EVERY factor. The single-factor ecology
        # control (R2.5) replaces it with the R1 factor alone.
        e1 = set()
        o2 = set()
        for w in words:
            tgt = e1 if len(w) % 2 == 0 else o2
            for L in range(2, len(w)):
                tgt.add(w[:L])
        self.LEN = [len(q) for q in DL]
        self.y = [1 if (q in e1 and q in o2) else 0 for q in DL]
        self.y_sf = [1 if q in e1 else 0 for q in DL]
        self.ylab = {}
        for i in range(self.T):
            self.ylab[DL[i]] = self.y[i]
        self.ylab_sf = {}
        for i in range(self.T):
            self.ylab_sf[DL[i]] = self.y_sf[i]

    def slices(self):
        """The registered target-independent 7:1 presentation and slices."""
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
    """The stored two-factor graph over a set of fit positions.

    Per factor: the occurrence counts of the stored descriptors, and the
    continuation fan-out of every descriptor that the stored descriptors
    extend. The two factors are disjoint by construction.
    """

    def __init__(self, eco, store_pos):
        self.eco = eco
        self.c1 = Counter()
        self.c2 = Counter()
        self.d1 = set()
        self.d2 = set()
        for i in store_pos:
            q = eco.DL[i]
            if eco.FAC[i] == 1:
                self.c1[q] += 1
                self.d1.add(q)
            else:
                self.c2[q] += 1
                self.d2.add(q)
        self.fan1 = defaultdict(set)
        self.fan2 = defaultdict(set)
        for q in self.d1:
            if len(q) >= 3:
                self.fan1[q[:-1]].add(q[-1])
        for q in self.d2:
            if len(q) >= 3:
                self.fan2[q[:-1]].add(q[-1])
        # the union continuation fan-out A(q) = A1(q) union A2(q)
        self.fan_union = {}
        for q, letters in self.fan1.items():
            self.fan_union[q] = set(letters)
        for q, letters in self.fan2.items():
            self.fan_union.setdefault(q, set()).update(letters)
        self.distinct = self.d1 | self.d2
        self.store_list = sorted(self.distinct)
        self.n_distinct = len(self.distinct)

    def count_of(self, q, factor):
        return (self.c1 if factor == 1 else self.c2).get(q, 0)

    def fan_of(self, q, factor):
        return len((self.fan1 if factor == 1 else self.fan2).get(q, ()))

    def union_fan_of(self, q):
        """|A1(q) union A2(q)|, the registered union continuation fan-out."""
        return len(self.fan_union.get(q, ()))

    def in_store(self, q):
        return 1 if (q in self.c1 or q in self.c2) else 0

    def stored_label(self, q):
        """The label the stored factor graph records for its own descriptor:
        the registered decision |A1(q)|>=1 AND |A2(q)|>=1 evaluated on q."""
        return 1 if (len(self.fan1.get(q, ())) >= 1
                     and len(self.fan2.get(q, ())) >= 1) else 0

    def pref_tally(self, q, ql, ylab):
        """(n1, n0) over the stored proper prefixes of q (distinct strings),
        labelled by the source-wide label of each prefix."""
        n1 = n0 = 0
        for k in range(2, ql):
            p = q[:k]
            if p in self.c1 or p in self.c2:
                if ylab[p]:
                    n1 += 1
                else:
                    n0 += 1
        return n1, n0

    def ext_tally(self, q, ql, ylab):
        """(n1, n0) over the stored descriptors extending q (distinct strings),
        labelled by the source-wide label."""
        lo = bisect_left(self.store_list, q)
        hi = bisect_right(self.store_list, q + "\x7f")
        n1 = n0 = 0
        for m in range(lo, hi):
            p = self.store_list[m]
            if len(p) > ql:
                if ylab[p]:
                    n1 += 1
                else:
                    n0 += 1
        return n1, n0


def readout_decision(name, ql, c1, c2, a1, a2, in_store, yl, p1, p0, e1, e0):
    """Exact decision of a readout on one query (registered language R).

    A joint arm fires iff every conjunct fires. Empty-neighbourhood readouts
    read the fit majority (1), asserted to be 1 by the caller before any
    enumeration; MEM_FALLBACK reads the STORED label of the query when the
    store holds it, else the fit majority.

    ECM_READOUT is the boundary datum of slice addendum R2.7 and is NOT a
    member of the language R: the product of the two factor-local associations
    taken as a product-form message at the query, decided 1 iff both factors
    carry a stored continuation. It is scored for information only; the winner
    rule runs over R alone.
    """
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if name == ECM_READOUT:
        return 1 if (a1 >= 1 and a2 >= 1) else 0
    if "&" in name:
        for part in name.split("&"):
            if readout_decision(part, ql, c1, c2, a1, a2, in_store, yl,
                                p1, p0, e1, e0) == 0:
                return 0
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
    if name.startswith("R1CNT>="):
        return 1 if c1 >= int(name.split(">=")[1]) else 0
    if name.startswith("R2CNT>="):
        return 1 if c2 >= int(name.split(">=")[1]) else 0
    if name.startswith("R1ASSOC>="):
        return 1 if a1 >= int(name.split(">=")[1]) else 0
    if name.startswith("R2ASSOC>="):
        return 1 if a2 >= int(name.split(">=")[1]) else 0
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


def charged_cost(name):
    """Registered charged per-query cost (slice addendum section 6).

    PREF_VOTE / EXT_VOTE are charged the number of stored descriptors they
    reference, which is a per-query quantity accumulated by the scorer.
    """
    if name in ("PREF_VOTE", "EXT_VOTE"):
        return None
    if name == "MEM_FALLBACK":
        return 2
    if name in ("C0", "C1"):
        return 0
    if name.startswith("LEN<="):
        return 0 if name.count("&") == 0 else 1
    if "&" in name:
        return 2
    return 1


def stage_errors(eco, store, query_pos, language, labels, ylab):
    """Score every readout of the language on query_pos. Exact integers only.

    Returns per-readout error counts, per-readout summed charged cost, the
    fit-majority rule's error count, and the winner of the registered winner
    rule (fewest exact decision errors, then fewer charged-cost units, then
    readout name). Labels and stored labels are passed in so that the
    single-factor ecology control can re-score the identical store under its
    own interface.
    """
    errs = dict((r, 0) for r in language)
    costs = dict((r, 0) for r in language)
    for i in query_pos:
        q = eco.DL[i]
        ql = eco.LEN[i]
        yv = labels[q]
        c1 = store.count_of(q, 1)
        c2 = store.count_of(q, 2)
        a1 = store.fan_of(q, 1)
        a2 = store.fan_of(q, 2)
        inst = store.in_store(q)
        yl = store.stored_label(q)
        p1, p0 = store.pref_tally(q, ql, ylab)
        e1, e0 = store.ext_tally(q, ql, ylab)
        for r in language:
            if readout_decision(r, ql, c1, c2, a1, a2, inst, yl,
                                p1, p0, e1, e0) != yv:
                errs[r] += 1
        for r in language:
            c = charged_cost(r)
            if c is None:
                costs[r] += (p1 + p0) if r == "PREF_VOTE" else (e1 + e0)
            else:
                costs[r] += c
    maj_err = sum(1 for i in query_pos if labels[eco.DL[i]] != FIT_MAJ)
    table = sorted((errs[r], costs[r], r) for r in language)
    winner = table[0][2]
    return {"n": len(query_pos), "per_readout_errors": errs, "costs": costs,
            "majority_errors": maj_err, "winner": winner,
            "winner_errors": errs[winner], "table": table}


def tally_block(eco, store, query_pos, labels):
    """Committed per-query tallies for exact replay by route A and
    re-derivation by route B. Each row:

        [len, true_label, c1, c2, fan1, fan2, union_fan, in_store,
         stored_label, pref_vote, ext_vote]

    where union_fan is the union continuation fan-out over the two factors and
    pref_vote / ext_vote are the decisions of those two vote readouts (the fit
    majority when their neighbourhood is empty). The layout is documented
    identically in real_scale_pgm_v1.py (route A) and
    independent_oracle_pgm_v1.py (route B)."""
    rows = []
    for i in query_pos:
        q = eco.DL[i]
        ql = eco.LEN[i]
        a1 = store.fan_of(q, 1)
        a2 = store.fan_of(q, 2)
        inst = store.in_store(q)
        p1, p0 = store.pref_tally(q, ql, labels)
        e1, e0 = store.ext_tally(q, ql, labels)
        pv = 1 if (p1 + p0 == 0 or p1 > p0) else 0
        ev = 1 if (e1 + e0 == 0 or e1 > e0) else 0
        rows.append([ql, labels[q], store.count_of(q, 1), store.count_of(q, 2),
                     a1, a2, store.union_fan_of(q),
                     inst, store.stored_label(q), pv, ev])
    return rows


def row_errors(rows, name):
    """Replay a committed tally block under one readout (the row layout above)."""
    e = 0
    for (ql, yv, c1, c2, a1, a2, fu, inst, yl, pv, ev) in rows:
        if readout_decision(name, ql, c1, c2, a1, a2, inst, yl,
                            pv, 1 - pv, ev, 1 - ev) != yv:
            e += 1
    return e


def winner_predictions(eco, store, query_pos, name):
    """The winner's exact decisions on query_pos (for the registered nulls)."""
    out = []
    for i in query_pos:
        q = eco.DL[i]
        out.append(readout_decision(name, eco.LEN[i], store.count_of(q, 1),
                                    store.count_of(q, 2),
                                    store.fan_of(q, 1), store.fan_of(q, 2),
                                    store.in_store(q), store.stored_label(q),
                                    0, 0, 0, 0))
    return out


def main():
    os.makedirs(RUNS, exist_ok=True)
    t0 = time.time()
    print("loading the F16 two-factor graph ecology from %s" % SOURCE,
          flush=True)
    eco = F16()
    sl = eco.slices()
    n_fit = sl["n_fit"]
    held = sl["held"]
    assert n_fit == N_FIT_EXPECT
    assert len(held) == N_HELD_EXPECT
    assert len(sl["rank_fit"]) == RANK_FIT_EXPECT
    assert len(sl["rank_score"]) == RANK_SCORE_EXPECT
    assert sl["half"] == HALF_EXPECT
    assert eco.r1_occ == R1_OCCURRENCES_EXPECT
    assert eco.r2_occ == R2_OCCURRENCES_EXPECT
    assert eco.r1_occ + eco.r2_occ == eco.T == T_EXPECT

    # The fit store itself holds 470,352 positive and 208,772 negative
    # descriptors (slice addendum section 3), so the majority fallback is 1:
    # the executor asserts the fit positive fraction exceeds 1/2 BEFORE any
    # enumeration, which fixes the empty-neighbourhood fallback.
    fit_pos = sum(eco.y[i] for i in sl["fit"])
    held_pos = sum(eco.y[i] for i in held)
    held_neg = len(held) - held_pos
    print("N=%d T=%d R1=%d R2=%d n_fit=%d n_held=%d fit_pos=%d"
          % (eco.N, eco.T, eco.r1_occ, eco.r2_occ, n_fit, len(held), fit_pos),
          flush=True)
    assert fit_pos == 470352 and fit_pos * 2 > n_fit, \
        "fit positive fraction not > 1/2: the fallback is not fixed at 1"
    assert held_pos == 67197 and held_neg == 29821, (held_pos, held_neg)

    # The registered readout language, imported from the frozen grammar module.
    sys.path.insert(0, HERE)
    import grammar_pgm_v1 as G
    R = G.READOUTS
    assert len(R) == 54
    assert R[0] == "C0" and R[1] == "C1"
    assert R[-3:] == ("PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK")

    stores = {}
    for sname, spos, _ in STAGES:
        stores[spos] = Store(eco, sl[spos])
        print("built store %-8s positions=%d distinct=%d (%.1fs)"
              % (spos, len(sl[spos]), stores[spos].n_distinct,
                 time.time() - t0), flush=True)

    # ---- the four registered stages ----
    stage = {}
    for sname, spos, qpos in (("rank", "rank_fit", "rank_score"),
                              ("held", "fit", "held"),
                              ("primary", "fit_lo", "fit_hi"),
                              ("regen", "fit_hi", "fit_lo")):
        stage[sname] = stage_errors(eco, stores[spos], sl[qpos], R, eco.ylab,
                                    eco.ylab)
        st = stage[sname]
        print("%-7s store=%-8s score=%-10s n=%d winner=%s err=%d maj=%d"
              % (sname, spos, qpos, st["n"], st["winner"],
                 st["winner_errors"], st["majority_errors"]), flush=True)

    rank, held_st, prim, regen = (stage["rank"], stage["held"], stage["primary"],
                                 stage["regen"])
    # Registered design statistics (FREEZE_V1_SLICE_ADDENDUM_R2.md R2.1-R2.6).
    assert rank["winner"] == LABEL_JOINT and rank["winner_errors"] == 13385
    assert rank["majority_errors"] == 62716
    assert rank["per_readout_errors"]["MEM_FALLBACK"] == 55719
    assert held_st["winner"] == LABEL_JOINT and held_st["winner_errors"] == 1893
    assert held_st["majority_errors"] == 29821
    assert held_st["per_readout_errors"]["MEM_FALLBACK"] == 18985
    assert prim["winner"] == LABEL_JOINT and prim["winner_errors"] == 42732
    assert prim["majority_errors"] == 104377
    assert prim["per_readout_errors"]["MEM_FALLBACK"] == 116632
    assert regen["winner"] == LABEL_JOINT and regen["winner_errors"] == 51085
    assert regen["majority_errors"] == 104395
    assert regen["per_readout_errors"]["MEM_FALLBACK"] == 124082
    prototype_agreement = len(held) - held_st["winner_errors"]
    assert prototype_agreement == 95125
    assert held_st["winner_errors"] * 2 <= held_st["majority_errors"], \
        "falsifier 1 does not hold"

    # ---- R2.6: the admitted membership-with-fallback arm must lose ----
    mem_rejected = all(st["per_readout_errors"]["MEM_FALLBACK"] >
                       st["winner_errors"]
                       for st in (rank, held_st, prim, regen))
    assert mem_rejected, "MEM_FALLBACK was not rejected at every stage"

    # ---- R2.7 ECM boundary datum: the exact-inference product-form message ----
    held_store = stores["fit"]
    ecm_preds = [readout_decision(ECM_READOUT, eco.LEN[i],
                                  held_store.count_of(eco.DL[i], 1),
                                  held_store.count_of(eco.DL[i], 2),
                                  held_store.fan_of(eco.DL[i], 1),
                                  held_store.fan_of(eco.DL[i], 2),
                                  held_store.in_store(eco.DL[i]),
                                  held_store.stored_label(eco.DL[i]),
                                  0, 0, 0, 0)
                 for i in held]
    ecm_errors = sum(1 for i, p in zip(held, ecm_preds) if p != eco.y[i])
    winner_preds = winner_predictions(eco, held_store, held,
                                      held_st["winner"])
    assert winner_preds == ecm_preds, "the exact-inference readout disagrees"

    # ---- R2.2 the registered nulls ----
    held_labels = [eco.y[i] for i in held]
    rng = random.Random(NULL_SEED_LABEL)
    shuffled = held_labels[:]
    rng.shuffle(shuffled)
    label_null = sum(1 for p, v in zip(winner_preds, shuffled) if p != v)
    assert label_null == 42019
    assert label_null > held_st["majority_errors"]

    n2 = sum(1 for i in sl["fit"] if eco.FAC[i] == 2)
    assert n2 == DESIGN_N2_EXPECT, n2
    rng2 = random.Random(NULL_SEED_DESIGN)
    idx = list(range(eco.T))
    rng2.shuffle(idx)
    corr = idx[:n2]
    c2c = Counter(eco.DL[i] for i in corr)
    d2c = set(c2c)
    fan2c = defaultdict(set)
    for q in d2c:
        if len(q) >= 3:
            fan2c[q[:-1]].add(q[-1])
    design_preds = []
    r1_arm_err = 0
    r2_arm_err = 0
    for i in held:
        q = eco.DL[i]
        a1 = 1 if held_store.fan_of(q, 1) >= 1 else 0
        a2 = 1 if len(fan2c.get(q, ())) >= 1 else 0
        design_preds.append(1 if (a1 and a2) else 0)
        if a1 != eco.y[i]:
            r1_arm_err += 1
        if a2 != eco.y[i]:
            r2_arm_err += 1
    design_null = sum(1 for p, v in zip(design_preds, held_labels) if p != v)
    assert design_null == 9770
    assert design_null > 3 * held_st["winner_errors"]
    assert r1_arm_err == 11113 and r2_arm_err == 15536

    # ---- R07 store ladder + charged-cost crossover ----
    ladder = []
    for m in LADDER_BUDGETS:
        st = Store(eco, sl["fit"][:m])
        e = 0
        for i in held:
            q = eco.DL[i]
            if readout_decision(LABEL_JOINT, eco.LEN[i], st.count_of(q, 1),
                                st.count_of(q, 2), st.fan_of(q, 1),
                                st.fan_of(q, 2), st.in_store(q),
                                st.stored_label(q), 0, 0, 0, 0) != eco.y[i]:
                e += 1
        ladder.append((m, e))
        print("ladder m=%d errors=%d (%.1fs)" % (m, e, time.time() - t0),
              flush=True)
    ladder.append((n_fit, held_st["winner_errors"]))
    assert [e for _, e in ladder] == [64554, 57021, 52720, 45591, 38812,
                                      31879, 22458, 1893]
    monotone = all(ladder[k][1] <= ladder[k - 1][1]
                   for k in range(1, len(ladder)))
    assert monotone
    V = held_store.n_distinct
    assert V == 221569
    index_cost = V + ALPHABET_WIDTH
    assert index_cost == 221596
    m_star = None
    for m in range(1, n_fit + 1):
        if SCAN_COST_MULT * m > index_cost:
            m_star = m
            break
    assert m_star == 110799
    assert SCAN_COST_MULT * m_star == 221598
    assert SCAN_COST_MULT * (m_star - 1) <= index_cost

    # ---- R2.4 the matched-presentation negative control ----
    cont_store = Store(eco, list(range(n_fit)))
    cont_score = list(range(n_fit, eco.T))
    cont = stage_errors(eco, cont_store, cont_score, R, eco.ylab, eco.ylab)
    cont_c0 = cont["per_readout_errors"]["C0"]
    cont_c1 = cont["per_readout_errors"]["C1"]
    cont_joint = cont["per_readout_errors"][LABEL_JOINT]
    cont_f1 = cont["winner_errors"] * 2 <= cont["majority_errors"]
    print("presentation control winner=%s errors=%d majority=%d joint=%d"
          % (cont["winner"], cont["winner_errors"], cont["majority_errors"],
             cont_joint), flush=True)
    assert cont["majority_errors"] == 32834
    assert cont_joint == 64099
    assert not cont_f1, "the source-order control must NOT clear falsifier 1"
    assert cont_c0 == 64184 and cont_c1 == 32834

    # ---- R2.5 the single-factor ecology control ----
    sf = stage_errors(eco, held_store, held, R, eco.ylab_sf, eco.ylab_sf)
    sf_fit_pos = sum(eco.y_sf[i] for i in sl["fit"])
    sf_held_pos = sum(eco.y_sf[i] for i in held)
    best_joint = min((sf["per_readout_errors"][r], r) for r in R if "&" in r)
    print("single-factor control winner=%s errors=%d majority=%d "
          "best_joint=%s (%d)"
          % (sf["winner"], sf["winner_errors"], sf["majority_errors"],
             best_joint[1], best_joint[0]), flush=True)
    assert sf["winner"] == LABEL_SINGLE and sf["winner_errors"] == 899
    assert sf["majority_errors"] == 19277
    assert best_joint[0] == 12437 and best_joint[1] == LABEL_JOINT
    assert sf["winner_errors"] < best_joint[0]

    # ---- committed replay blocks (route A replays these exactly) ----
    held_block = tally_block(eco, held_store, held[:REPLAY_HELD], eco.ylab)
    rank_block = tally_block(eco, stores["rank_fit"], sl["rank_score"][:REPLAY_RANK],
                             eco.ylab)
    regen_lo_block = tally_block(eco, stores["fit_hi"],
                                 sl["fit_lo"][:REPLAY_REGEN], eco.ylab)
    regen_hi_block = tally_block(eco, stores["fit_lo"],
                                 sl["fit_hi"][:REPLAY_REGEN], eco.ylab)
    assert row_errors(held_block, held_st["winner"]) == \
        row_errors(held_block, LABEL_JOINT)
    assert row_errors(rank_block, rank["winner"]) == \
        row_errors(rank_block, LABEL_JOINT)
    assert row_errors(regen_lo_block, regen["winner"]) == \
        row_errors(regen_lo_block, LABEL_JOINT)
    assert row_errors(regen_hi_block, prim["winner"]) == \
        row_errors(regen_hi_block, LABEL_JOINT)

    # ---- receipt ----
    rec = {
        "schema": "GMI833HRealScaleProbabilisticGraphicalScopeV1",
        "scope": "SIGMA_H18R",
        "row": "Probabilistic graphical models.",
        "source": {"path": SOURCE, "sha256": eco.sha, "tokens": eco.N,
                   "descriptors": eco.T},
        "factors": {"R1_tokens_rule": "even token length",
                    "R2_tokens_rule": "odd token length",
                    "R1_occurrences": eco.r1_occ,
                    "R2_occurrences": eco.r2_occ},
        "presentation": {"key": "(i*%d) mod 2**32" % ORDER_MULT,
                         "n_fit": n_fit, "n_held": len(held),
                         "rank_fit": len(sl["rank_fit"]),
                         "rank_score": len(sl["rank_score"]),
                         "half": sl["half"]},
        "holdout": {"n": len(held), "positive": held_pos, "negative": held_neg,
                    "majority": FIT_MAJ,
                    "majority_errors": held_st["majority_errors"],
                    "winner": held_st["winner"],
                    "winner_errors": held_st["winner_errors"],
                    "winner_class": G.classify(held_st["winner"]),
                    "prototype_agreement": prototype_agreement,
                    "per_readout_errors": held_st["per_readout_errors"],
                    "falsifier1_half_majority":
                        held_st["majority_errors"] // 2,
                    "falsifier1_holds":
                        held_st["winner_errors"] * 2 <=
                        held_st["majority_errors"]},
        "rank_stage": {"store": "rank_fit", "score": "rank_score",
                       "n": rank["n"], "winner": rank["winner"],
                       "winner_errors": rank["winner_errors"],
                       "winner_class": G.classify(rank["winner"]),
                       "majority_errors": rank["majority_errors"],
                       "per_readout_errors": rank["per_readout_errors"]},
        "regen": {"primary": {"store": "fit_lo", "score": "fit_hi",
                              "n": prim["n"], "winner": prim["winner"],
                              "winner_errors": prim["winner_errors"],
                              "winner_class": G.classify(prim["winner"]),
                              "majority_errors": prim["majority_errors"]},
                  "regen": {"store": "fit_hi", "score": "fit_lo",
                            "n": regen["n"], "winner": regen["winner"],
                            "winner_errors": regen["winner_errors"],
                            "winner_class": G.classify(regen["winner"]),
                            "majority_errors": regen["majority_errors"]},
                  "same_class": G.classify(regen["winner"]) ==
                  G.classify(prim["winner"]),
                  "class": G.classify(prim["winner"])},
        "mem_fallback": {"rank": rank["per_readout_errors"]["MEM_FALLBACK"],
                         "held": held_st["per_readout_errors"]["MEM_FALLBACK"],
                         "primary":
                             prim["per_readout_errors"]["MEM_FALLBACK"],
                         "regen": regen["per_readout_errors"]["MEM_FALLBACK"],
                         "rejected_at_all_stages": mem_rejected},
        "nulls": {"label": {"seed": NULL_SEED_LABEL, "errors": label_null,
                            "gt_majority":
                                label_null > held_st["majority_errors"],
                            "shuffled_labels": [int(v) for v in shuffled]},
                  "design": {"seed": NULL_SEED_DESIGN, "errors": design_null,
                             "bound_3x_arm": 3 * held_st["winner_errors"],
                             "gt_3x_arm": design_null >
                             3 * held_st["winner_errors"],
                             "r1_arm_under_corruption": r1_arm_err,
                             "r2_arm_under_corruption": r2_arm_err,
                             "predictions": [int(v) for v in design_preds]}},
        "holdout_all": {"rows": len(held),
                        "queries": [[int(v), int(p)] for v, p in
                                    zip(held_labels, winner_preds)]},
        "ladder": {"readout": LABEL_JOINT,
                   "budgets": [m for m, _ in ladder],
                   "errors": [e for _, e in ladder], "monotone": monotone},
        "crossover": {"V": V, "alphabet_width": ALPHABET_WIDTH,
                      "index_cost": index_cost, "m_star": m_star,
                      "scan_cost_at_m_star": SCAN_COST_MULT * m_star,
                      "holds": SCAN_COST_MULT * m_star > index_cost},
        "ecm": {"readout": ECM_READOUT, "errors_held": ecm_errors,
                "agrees_with_winner": bool(ecm_errors ==
                                           held_st["winner_errors"])},
        "presentation_control": {"winner": cont["winner"],
                                 "winner_errors": cont["winner_errors"],
                                 "winner_class": G.classify(cont["winner"]),
                                 "majority_errors": cont["majority_errors"],
                                 "c0_errors": cont_c0, "c1_errors": cont_c1,
                                 "joint_errors": cont_joint,
                                 "f1_holds": bool(cont_f1),
                                 "control_fires": bool(not cont_f1)},
        "single_factor_control": {"label": "|A1(q)|>=1",
                                  "winner": sf["winner"],
                                  "winner_errors": sf["winner_errors"],
                                  "winner_class": G.classify(sf["winner"]),
                                  "majority_errors": sf["majority_errors"],
                                  "fit_positive": sf_fit_pos,
                                  "held_positive": sf_held_pos,
                                  "best_joint_arm": best_joint[1],
                                  "best_joint_errors": best_joint[0]},
        "replay": {
            "held_block": {"rows": len(held_block), "queries": held_block,
                           "winner_errors":
                               row_errors(held_block, held_st["winner"])},
            "rank_block": {"rows": len(rank_block), "queries": rank_block,
                           "winner_errors":
                               row_errors(rank_block, rank["winner"])},
            "regen_lo_block": {"rows": len(regen_lo_block),
                               "queries": regen_lo_block,
                               "winner_errors":
                                   row_errors(regen_lo_block,
                                              regen["winner"])},
            "regen_hi_block": {"rows": len(regen_hi_block),
                               "queries": regen_hi_block,
                               "winner_errors":
                                   row_errors(regen_hi_block, prim["winner"])},
        },
    }
    out = os.path.join(RUNS, "scope_SIGMA_H18R.json")
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
    with open(os.path.join(RUNS, "sources.json"), "w") as fh:
        json.dump({"schema": "GMI833HRealScaleSourcesV1",
                   "source": {"path": SOURCE, "sha256": eco.sha,
                              "tokens": eco.N, "descriptors": eco.T}},
                  fh, indent=1, sort_keys=True)
    print("WROTE %s (%.1fs)" % (out, time.time() - t0), flush=True)
    print("winner %s held_errors %d prototype_agreement %d"
          % (held_st["winner"], held_st["winner_errors"], prototype_agreement),
          flush=True)
    print("DISAGREEMENT presentation_control.winner: registered arena winner "
          "%s at %d errors (source order); the C0/C1 pair is %d/%d"
          % (cont["winner"], cont["winner_errors"], cont_c0, cont_c1),
          flush=True)
    print("DISAGREEMENT single_factor_control.majority_errors: measured %d "
          "(fit-majority rule under |A1(q)|>=1)"
          % sf["majority_errors"], flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
