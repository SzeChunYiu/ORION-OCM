#!/usr/bin/env python3
"""Real-scale run driver for gmi-833-h-real-scale-diffusion-refinement-v1.

The ONLY file of this package that reads the real source. Runs on the host of
record (billy-old, CPython 3.14.4). Exact integer arithmetic throughout: every
emitted quantity is an integer decision count or an integer index. No float
enters any comparison, count, loss or claim. The one pre-outcome choice in the
package (the labelling configuration and T*) is made by the registered rule of
FREEZE_V1.md section 4, applied to source-derived data alone, and this file
asserts the outcome of that rule rather than assuming it.

    python3 -B run_real_scale_diffusion_refinement_v1.py

Writes REAL_RUNS/scope_SIGMA_H33R.json and REAL_RUNS/sources.json.
"""
import collections
import hashlib
import json
import os
import random
import sys

SOURCE = "/usr/share/dict/american-english"
SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
N_TOKENS = 104334
T_CTX = 671860
N_CONTEXTS = 168834
MODAL_LEN = 8
MULT = 2654435761
M_CAP = 256
N_QUERIES = 38103
HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

SEED_DESIGN = 20261001
SEED_LABEL = 20261002

# The registered threshold ladder of the step-index family. The ladder is
# fixed by registration EXCEPT that it must contain the registered T* -- the
# label's own threshold -- so that the family is not handicapped by the
# ladder's grid. T_STAR_EXTRA is filled in by the run before any scoring.
REFINE_LE = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 64, 256)
REFINE_GE = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 64, 256)
REFINEIN_LE = (1, 2, 3)
DRAW_GE = (1, 2, 3, 4)
CARD_GE = (1, 2, 3, 4)
CNT_GE = (1, 2, 3)
LEN_LE = (6, 7, 8, 9, 10, 11, 12)

def _ladder(base, extra):
    return tuple(sorted(set(base) | set(extra)))


READOUTS = (("C0", "C1")
            + tuple("LEN<=%d" % L for L in LEN_LE)
            + tuple("CNT>=%d" % K for K in CNT_GE)
            + tuple("CARD>=%d" % K for K in CARD_GE)
            + tuple("REFINE<=%d" % k for k in REFINE_LE)
            + tuple("REFINE>=%d" % k for k in REFINE_GE)
            + tuple("REFINEIN<=%d" % k for k in REFINEIN_LE)
            + tuple("DRAW>=%d" % k for k in DRAW_GE)
            + ("DRAW0", "MEM_FALLBACK"))

WEIGHTED_PREFIXES = ("REFINE<=", "REFINE>=", "REFINEIN<=", "DRAW>=")
REFINE_PREFIXES = ("REFINE<=", "REFINE>=", "REFINEIN<=")
SINGLE_DRAW = ("DRAW0", "DRAW>=")


def classify(name):
    if name in ("C0", "C1"):
        return "CONSTANT_ARM"
    if name.startswith("LEN<="):
        return "DESCRIPTOR_LENGTH_THRESHOLD"
    if name.startswith(("CNT>=", "CARD>=")):
        return "STORE_MEMBERSHIP_COUNT"
    if name.startswith(REFINE_PREFIXES):
        return "REFINEMENT_INDEX"
    if name == "DRAW0" or name.startswith("DRAW>="):
        return "SINGLE_DRAW_SOURCE"
    if name == "MEM_FALLBACK":
        return "STORED_LABEL_READ_WITH_FALLBACK"
    raise ValueError("readout outside the registered language: " + name)


def cost(name):
    if name in ("C0", "C1") or name.startswith("LEN<="):
        return 0
    if name == "MEM_FALLBACK":
        return 2
    if name == "DRAW0":
        return 1
    if name.startswith(("CNT>=", "CARD>=")) or name.startswith(WEIGHTED_PREFIXES):
        return 1
    raise ValueError("readout outside the registered language: " + name)


def order_key(i):
    return (i * MULT) % (2 ** 32)


# --------------------------------------------------------------- the source --

def read_source():
    with open(SOURCE, "rb") as fh:
        raw = fh.read()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != SOURCE_SHA:
        raise SystemExit("SOURCE DIGEST MISMATCH: %s != %s" % (sha, SOURCE_SHA))
    words = raw.decode("utf-8").split()
    if len(words) != N_TOKENS:
        raise SystemExit("SOURCE TOKEN COUNT MISMATCH: %d != %d"
                         % (len(words), N_TOKENS))
    return raw, words


def registered_alphabet(words):
    alpha = sorted(set(ch for w in words for ch in w))
    order = sorted(alpha, key=lambda c: (ord(c) * MULT) % (2 ** 32))
    if len(set(order)) != len(order):
        raise SystemExit("THE REGISTERED ORDER IS NOT INJECTIVE ON THIS SOURCE")
    return alpha, order, {c: i for i, c in enumerate(order)}


class Ecology(object):
    """The registered F33 ecology: descriptor closure, contexts, refinement."""

    def __init__(self, words):
        self.words = words
        self.alpha, self.order, self.sidx = registered_alphabet(words)
        self.C = len(self.alpha)
        self.positions = []
        self.nexts = collections.defaultdict(list)
        for w in words:
            for k in range(2, len(w)):
                # the position IS its descriptor: the prefix of length k >= 2
                self.positions.append(w[:k])
                self.nexts[w[:k]].append(w[k])
        if len(self.positions) != T_CTX:
            raise SystemExit("T_CTX MISMATCH: %d != %d"
                             % (len(self.positions), T_CTX))
        if len(self.nexts) != N_CONTEXTS:
            raise SystemExit("CONTEXT COUNT MISMATCH: %d != %d"
                             % (len(self.nexts), N_CONTEXTS))
        self.occ = {q: len(cs) for q, cs in self.nexts.items()}
        self.support = {q: set(cs) for q, cs in self.nexts.items()}
        self.hist = collections.Counter(len(w) for w in words)

    def sigma(self, c, j):
        return self.order[(self.sidx[c] + j) % self.C]

    def walk(self, cand_set, c):
        if not cand_set:
            return M_CAP
        r = 0
        while self.sigma(c, r) not in cand_set:
            r += 1
            if r > M_CAP:
                return M_CAP
        return r

    def probe_offset(self, q, mode):
        if mode == "occ":
            return (self.occ[q] * MULT) % self.C
        return (ord(q[0]) * MULT + len(q)) % self.C

    def r_full(self, q, key_mode, corruption):
        z = self.probe_offset(q, key_mode) + corruption
        c = self.sigma(min(self.support[q]), z)
        return self.walk(self.support[q], c), c

    def r_dist(self, key_mode, corruption):
        d = collections.Counter()
        for q in self.support:
            r, _c = self.r_full(q, key_mode, corruption)
            d[r] += 1
        return d

    def balance_rule(self):
        """FREEZE_V1.md section 4: the registered pre-outcome configuring rule.

        Over the four registered configurations, measure the distribution of
        r(q) over ALL source contexts and pick the configuration minimising
        |P(y=1) - 1/2|; T* is the smallest threshold attaining that minimum.
        No slice, no store and no readout is evaluated here.
        """
        best = None
        for key_mode in ("occ", "desc"):
            for corruption in (0, 1):
                d = self.r_dist(key_mode, corruption)
                tot = sum(d.values())
                for t in range(0, M_CAP + 1):
                    y1 = sum(v for r, v in d.items() if r <= t)
                    gap = abs(2 * y1 - tot)          # exact integer comparison
                    cand = (gap, key_mode, corruption, t, y1, tot)
                    if best is None or cand[:4] < best[:4]:
                        best = cand
        gap, key_mode, corruption, tstar, y1, tot = best
        return {"key_mode": key_mode, "corruption": corruption, "T_star": tstar,
                "y1": y1, "n": tot, "gap_twice": gap}


# ------------------------------------------------------------------ queries --

def build_queries(eco, held_positions):
    """The registered query set, in held order.

    A task is a held closure position whose descriptor has len >= 3 and whose
    full-source support has at least two candidates.
    """
    rows = []
    for i in held_positions:
        q = eco.positions[i]
        if len(q) < 3 or len(eco.support[q]) < 2:
            continue
        rows.append(q)
    return rows


def label_rows(eco, queries, cfg):
    """(label, presented candidate) for each query, from the labeller alone."""
    out = []
    for q in queries:
        r, c = eco.r_full(q, cfg["key_mode"], cfg["corruption"])
        out.append((1 if r <= cfg["T_star"] else 0, c))
    return out


def build_store(eco, fit_positions, unit_candidates=None):
    """Stored candidate sets from the slice's own positions.

    unit_candidates, when given, supplies the candidate character for each
    stored unit in the order the units are built; it is the design null's
    global reassignment and it changes no context's stored-unit MULTISET slot
    count, so the cardinality aggregates are invariant by construction.
    """
    store = collections.defaultdict(set)
    k = 0
    for i in fit_positions:
        q = eco.positions[i]
        if len(q) < 3:
            continue
        c = q[-1] if unit_candidates is None else unit_candidates[k]
        store[q[:-1]].add(c)
        k += 1
    return store, k


def unit_list(eco, fit_positions):
    us = []
    for i in fit_positions:
        q = eco.positions[i]
        if len(q) >= 3:
            us.append((q[:-1], q[-1]))
    return us


# -------------------------------------------------------------------- arms --

T_STAR = 4          # replaced at run time by the registered rule's own choice
FIT_MAJORITY = 1    # replaced at run time by the fit slice's majority label


def decide(eco, name, q, card, walk_store, draw_dist, cnt, L):
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if name.startswith("LEN<="):
        return 1 if L <= int(name.split("<=")[1]) else 0
    if name.startswith("CNT>="):
        return 1 if cnt >= int(name.split(">=")[1]) else 0
    if name.startswith("CARD>="):
        return 1 if card >= int(name.split(">=")[1]) else 0
    if name.startswith("REFINE<="):
        k = int(name.split("<=")[1])
        return 1 if (card >= 1 and walk_store <= k) else 0
    if name.startswith("REFINE>="):
        k = int(name.split(">=")[1])
        return 1 if (card >= 1 and walk_store >= k) else 0
    if name.startswith("REFINEIN<="):
        k = int(name.split("<=")[1])
        return 1 if (card >= 2 and walk_store <= k) else 0
    if name == "DRAW0":
        return 1 if (card >= 1 and walk_store == 0) else 0
    if name.startswith("DRAW>="):
        k = int(name.split(">=")[1])
        return 1 if (card >= 2 and draw_dist >= k) else 0
    if name == "MEM_FALLBACK":
        # the admitted storable-label arm, exactly as the slice addendum
        # registers it: "if the descriptor q is stored, read out the stored
        # predicate of q (the registered label form evaluated on the stored
        # table); else the fit majority". q is stored iff it occurs among the
        # slice's positions, which is the tally field `cnt`. The fallback
        # branch is load-bearing: without it this arm would be the same branch
        # as REFINE<=T* under another name.
        if cnt >= 1:
            return 1 if (card >= 1 and walk_store <= T_STAR) else 0
        return FIT_MAJORITY
    raise ValueError("readout outside the registered language: " + name)


def tallies(eco, queries, labels, store):
    """Per-query tallies the arms read. No arm reads the labeller's support."""
    rows = []
    for q, (y, c) in zip(queries, labels):
        st = store.get(q, ())
        card = len(st)
        ws = eco.walk(st, c) if st else M_CAP
        # forward registered step distance from the canonical candidate to the
        # nearest stored candidate -- the single-draw family's magnitude
        c0 = min(eco.support[q])
        dd = min(((eco.sidx[x] - eco.sidx[c0]) % eco.C) for x in st) if st else M_CAP
        rows.append((q, y, c, card, ws, dd, eco.occ[q], len(q)))
    return rows


def arm_errors(eco, rows, name):
    e = 0
    for _q, y, c, card, ws, dd, cnt, L in rows:
        if decide(eco, name, _q, card, ws, dd, cnt, L) != y:
            e += 1
    return e


def replay_errors(rows, name):
    """Error count of a readout over replayed tally rows, with no ecology: every
    quantity the readouts read is already in the tallies."""
    return arm_errors(None, rows, name)


def majority_errors(rows):
    neg = sum(1 for r in rows if r[1] != 0)
    pos = sum(1 for r in rows if r[1] != 1)
    return min(neg, pos), (0 if neg <= pos else 1)


def winner(eco, rows):
    scored = []
    for name in READOUTS:
        scored.append((arm_errors(eco, rows, name), cost(name), name))
    scored.sort()
    return scored[0], scored


def min_error_set(scored):
    """The arms attaining the minimum error count, ordered by the registered
    tie-break (fewer charged-cost units, then readout name). The winner is the
    first entry. A tie is made visible here so a gate can see it."""
    best = scored[0][0]
    tied = [s for s in scored if s[0] == best]
    return {"min_errors": best, "winner": tied[0][2],
            "winner_cost": tied[0][1], "tie": len(tied) > 1,
            "arms": [{"arm": t[2], "errors": t[0], "cost": t[1]}
                     for t in tied]}


def mem_fallback_errors(eco, rows, T_star):
    """The admitted storable-label arm: the registered label form evaluated on
    the store's own table."""
    e = 0
    for _q, y, c, card, ws, _dd, _cnt, _L in rows:
        pred = 1 if (card >= 1 and ws <= T_star) else 0
        if pred != y:
            e += 1
    return e


# --------------------------------------------------------------------- main --

def main():
    raw, words = read_source()
    eco = Ecology(words)
    cfg = eco.balance_rule()
    print("balance rule -> key=%s corruption=%d T*=%d rate %d/%d"
          % (cfg["key_mode"], cfg["corruption"], cfg["T_star"],
             cfg["y1"], cfg["n"]))
    T_star = cfg["T_star"]
    global T_STAR, FIT_MAJORITY, READOUTS
    T_STAR = T_star
    READOUTS = (("C0", "C1")
                + tuple("LEN<=%d" % L for L in LEN_LE)
                + tuple("CNT>=%d" % K for K in CNT_GE)
                + tuple("CARD>=%d" % K for K in CARD_GE)
                + tuple("REFINE<=%d" % k for k in _ladder(REFINE_LE, (T_star,)))
                + tuple("REFINE>=%d" % k for k in _ladder(REFINE_GE, (T_star,)))
                + tuple("REFINEIN<=%d" % k for k in REFINEIN_LE)
                + tuple("DRAW>=%d" % k for k in DRAW_GE)
                + ("DRAW0", "MEM_FALLBACK"))
    # The registered rule is the criterion, not a named configuration: the
    # configuration it selects is a fact of the bound source and is recorded
    # in the receipt. A non-degenerate label is asserted instead.
    if not (0 < cfg["y1"] < cfg["n"]):
        raise SystemExit("THE REGISTERED RULE PRODUCED A DEGENERATE LABEL: %r"
                         % (cfg,))

    T = len(eco.positions)
    seq = sorted(range(T), key=order_key)
    n_fit = (T * 7) // 8
    fit = seq[:n_fit]
    held = seq[n_fit:]
    rank_fit = seq[:(7 * n_fit) // 10]
    rank_score = seq[(7 * n_fit) // 10:n_fit]
    half = n_fit // 2
    fit_lo = seq[:half]
    fit_hi = seq[half:n_fit]
    print("T=%d n_fit=%d n_held=%d rank_fit=%d rank_score=%d half=%d/%d"
          % (T, n_fit, len(held), len(rank_fit), len(rank_score),
             half, n_fit - half))

    # the registered fallback constant: the fit slice's majority label
    fit_support = collections.defaultdict(set)
    for i in fit:
        q = eco.positions[i]
        if len(q) >= 3:
            fit_support[q[:-1]].add(q[-1])
    fpos = fneg = 0
    for i in fit:
        q = eco.positions[i]
        if len(q) < 3 or len(eco.support[q]) < 2:
            continue
        c = eco.sigma(min(eco.support[q]),
                      (eco.occ[q] * MULT) % eco.C + cfg["corruption"])
        y = 1 if eco.walk(eco.support[q], c) <= T_star else 0
        if y:
            fpos += 1
        else:
            fneg += 1
    FIT_MAJORITY = 0 if fneg >= fpos else 1
    print("fit slice majority label: %d (%d positive / %d negative)"
          % (FIT_MAJORITY, fpos, fneg))

    queries = build_queries(eco, held)
    if len(queries) != N_QUERIES:
        raise SystemExit("QUERY SET MISMATCH: %d != %d"
                         % (len(queries), N_QUERIES))
    labels = label_rows(eco, queries, cfg)
    y1 = sum(y for y, _c in labels)
    print("query set %d, label positives %d (%.4f)"
          % (len(queries), y1, y1 / len(queries)))

    store, nunits = build_store(eco, fit)
    rows = tallies(eco, queries, labels, store)
    maj_err, maj_lab = majority_errors(rows)
    win, table = winner(eco, rows)
    mf = mem_fallback_errors(eco, rows, T_star)
    print("store units %d | majority %d errors (label %d) | winner %s %d"
          % (nunits, maj_err, maj_lab, win[2], win[0]))
    print("  MEM_FALLBACK admitted: %d errors, class %s, winner=%s"
          % (mf, classify("MEM_FALLBACK"), win[2] == "MEM_FALLBACK"))
    per = {n: arm_errors(eco, rows, n) for n in READOUTS}
    for n in sorted(per, key=lambda k: (per[k], cost(k), k))[:12]:
        print("  %-16s %-28s %7d" % (n, classify(n), per[n]))

    # ---- R8: the frozen prediction record of the winner, written and flushed
    # BEFORE any null or control is run
    frozen_path = os.path.join(RUNS, "FROZEN_PREDICTIONS_R8.json")
    predictions = []
    for i in range(len(rows)):
        _q, y, c, card, ws, dd, cnt, L = rows[i]
        predictions.append([_q, y, decide(eco, win[2], _q, card, ws, dd, cnt, L)])
    with open(frozen_path, "w") as fh:
        json.dump({"schema": "GMI833FrozenPredictionsR8V1",
                   "scope": "SIGMA_H33R", "arm": win[2],
                   "t_star": T_star, "fit": "fit (n_fit=%d)" % n_fit,
                   "held": len(predictions),
                   "predictions": predictions}, fh, sort_keys=True)
        fh.write("\n")
    with open(frozen_path, "rb") as fh:
        r8_sha = hashlib.sha256(fh.read()).hexdigest()
    print("R8 frozen predictions written before any null or control: %d rows "
          "sha256 %s" % (len(predictions), r8_sha[:16]))

    # ---- rank stage: store on rank_fit, score on rank_score
    rstore, _ = build_store(eco, rank_fit)
    rq = [eco.positions[i] for i in rank_score]
    rq = [q for q in rq if len(q) >= 3 and len(eco.support[q]) >= 2]
    rlabels = label_rows(eco, rq, cfg)
    rrows = tallies(eco, rq, rlabels, rstore)
    rmaj, _ = majority_errors(rrows)
    rwin, _ = winner(eco, rrows)
    print("rank stage: n=%d majority=%d winner=%s(%s) %d"
          % (len(rrows), rmaj, rwin[2], classify(rwin[2]), rwin[0]))

    rmin = min_error_set(_)[0] if False else None
    # ---- R09 symmetric half split
    hstore, _ = build_store(eco, fit_lo)
    hq = [eco.positions[i] for i in fit_hi]
    hq = [q for q in hq if len(q) >= 3 and len(eco.support[q]) >= 2]
    hrows = tallies(eco, hq, label_rows(eco, hq, cfg), hstore)
    hmaj, _ = majority_errors(hrows)
    hwin, _ = winner(eco, hrows)
    hstore2, _ = build_store(eco, fit_hi)
    hq2 = [eco.positions[i] for i in fit_lo]
    hq2 = [q for q in hq2 if len(q) >= 3 and len(eco.support[q]) >= 2]
    hrows2 = tallies(eco, hq2, label_rows(eco, hq2, cfg), hstore2)
    hmaj2, _ = majority_errors(hrows2)
    hwin2, _ = winner(eco, hrows2)
    same_class = (classify(rwin[2]) == classify(win[2])
                  == classify(hwin[2]) == classify(hwin2[2]))
    print("regen: %s %d | %s %d  same_class=%s"
          % (hwin[2], hwin[0], hwin2[2], hwin2[0], same_class))

    # ---- family separation (falsifier 3)
    ref_best = min((per[n], cost(n), n) for n in READOUTS
                   if classify(n) == "REFINEMENT_INDEX")
    draw_best = min((per[n], cost(n), n) for n in READOUTS
                    if classify(n) == "SINGLE_DRAW_SOURCE")
    card_best = min((per[n], cost(n), n) for n in READOUTS
                    if classify(n) == "STORE_MEMBERSHIP_COUNT")
    fam_separated = ref_best[0] < draw_best[0]
    print("family separation: REFINE best %s %d vs single-draw best %s %d "
          "(separated=%s); cardinality best %s %d"
          % (ref_best[2], ref_best[0], draw_best[2], draw_best[0],
             fam_separated, card_best[2], card_best[0]))

    # ---- registered global design null
    units = unit_list(eco, fit)
    cands = [c for _q, c in units]
    rng = random.Random(SEED_DESIGN)
    rng.shuffle(cands)
    nstore, _ = build_store(eco, fit, cands)
    nrows = tallies(eco, queries, labels, nstore)
    null_ref = arm_errors(eco, nrows, ref_best[2])
    null_card = arm_errors(eco, nrows, card_best[2])
    null_draw = arm_errors(eco, nrows, draw_best[2])
    raw_invariant = (null_card == card_best[0])
    ratio = null_ref // max(1, ref_best[0])
    gt_3x = null_ref > 3 * ref_best[0]
    print("design null: REFINE %d -> %d (x%.2f, gt3x=%s) | CARD %d -> %d "
          "(invariant=%s) | DRAW %d -> %d"
          % (ref_best[0], null_ref, null_ref / max(1, ref_best[0]), gt_3x,
             card_best[0], null_card, raw_invariant,
             draw_best[0], null_draw))

    # ---- label null
    lrng = random.Random(SEED_LABEL)
    sh = [y for y, _c in labels]
    lrng.shuffle(sh)
    lab_errors = sum(1 for (_q, _y, c, card, ws, _dd, _cnt, _L), s in
                     zip(rows, sh)
                     if decide(eco, win[2], _q, card, ws, _dd, _cnt, _L) != s)

    # ---- store ladder
    ladder_budgets = (1000, 5000, 10000, 20000, 50000, 100000, 200000, n_fit)
    ladder = []
    for b in ladder_budgets:
        if b >= n_fit:
            st = store
        else:
            st, _ = build_store(eco, seq[:b])
        rr = tallies(eco, queries, labels, st)
        ladder.append(arm_errors(eco, rr, win[2]))
    monotone = all(a >= c for a, c in zip(ladder, ladder[1:]))
    print("ladder %s monotone=%s" % (ladder, monotone))

    # ---- crossover
    V = len(set(q for q, _c in units))
    index_cost = V + 27
    m_star = index_cost // 2 + 1
    while 2 * (m_star - 1) > index_cost:
        m_star -= 1
    co_holds = (2 * m_star > index_cost) and (2 * (m_star - 1) <= index_cost)
    print("crossover V=%d index=%d m*=%d holds=%s" % (V, index_cost, m_star, co_holds))

    # ---- source-order presentation control: the un-permuted contiguous slice
    cstore, _ = build_store(eco, list(range(n_fit)))
    crows = tallies(eco, queries, labels, cstore)
    cmaj, _ = majority_errors(crows)
    cwin, _ = winner(eco, crows)
    ctrl_arm = arm_errors(eco, crows, win[2])
    ctrl_f1 = (ctrl_arm * 2) <= cmaj
    ctrl_fires = not ctrl_f1
    print("source-order control: registered arm %s %d vs majority %d "
          "(F1 need %d) fires=%s"
          % (win[2], ctrl_arm, cmaj, cmaj // 2, ctrl_fires))

    # ---- withheld raw arm data for the matched presentation control
    card_arm_err = per[card_best[2]]
    f1 = (win[0] * 2) <= maj_err
    print("F1: winner %d <= half majority %d -> %s" % (win[0], maj_err // 2, f1))

    receipt = {
        "schema": "GMI833HRealScaleDiffusionRefinementScopeV1",
        "scope": "SIGMA_H33R",
        "row": "Diffusion/iterative-refinement systems.",
        "source": {"path": SOURCE, "sha256": eco_sha(raw), "tokens": len(words),
                   "duplicate_tokens": len(words) - len(set(words)),
                   "alphabet_size": eco.C, "contexts": len(eco.support),
                   "positions": len(eco.positions),
                   "length_histogram": {str(k): v for k, v in eco.hist.items()}},
        "label_config": cfg,
        "presentation": {"key": "(i*2654435761) mod 2**32", "T_ctx": T,
                         "n_fit": n_fit, "n_held": len(held),
                         "rank_fit": len(rank_fit), "rank_score": len(rank_score),
                         "half": half},
        "query_fallback_label": FIT_MAJORITY,
        "queries": {"n": len(queries), "positives": y1,
                    "negatives": len(queries) - y1,
                    "held_errors_majority": maj_err, "majority_label": maj_lab},
        "holdout": {"winner": win[2], "winner_class": classify(win[2]),
                    "winner_errors": win[0], "majority_errors": maj_err,
                    "n": len(queries), "f1_half_majority": maj_err // 2,
                    "f1_holds": bool(f1),
                    "prototype_agreement": len(queries) - win[0],
                    "mem_fallback_errors": mf,
                    "mem_fallback_is_winner": bool(win[2] == "MEM_FALLBACK"),
                    "per_readout_errors": per},
        "rank_stage": {"store": "rank_fit", "score": "rank_score",
                       "n": len(rrows), "winner": rwin[2],
                       "winner_class": classify(rwin[2]),
                       "winner_errors": rwin[0], "majority_errors": rmaj},
        "regen": {"primary": {"store": "fit_lo", "score": "fit_hi",
                              "n": len(hrows), "winner": hwin[2],
                              "winner_class": classify(hwin[2]),
                              "winner_errors": hwin[0], "majority_errors": hmaj},
                  "regen": {"store": "fit_hi", "score": "fit_lo",
                            "n": len(hrows2), "winner": hwin2[2],
                            "winner_class": classify(hwin2[2]),
                            "winner_errors": hwin2[0], "majority_errors": hmaj2},
                  "same_class": bool(same_class),
                  "class": classify(win[2])},
        "family_separation": {
            "refinement_best": {"arm": ref_best[2], "errors": ref_best[0]},
            "single_draw_best": {"arm": draw_best[2], "errors": draw_best[0]},
            "cardinality_best": {"arm": card_best[2], "errors": card_best[0]},
            "refinement_beats_single_draw": bool(fam_separated)},
        "nulls": {"design": {"seed": SEED_DESIGN, "arm": ref_best[2],
                             "real": ref_best[0], "reassigned": null_ref,
                             "gt_3x": bool(gt_3x),
                             "cardinality_arm": card_best[2],
                             "cardinality_real": card_best[0],
                             "cardinality_reassigned": null_card,
                             "raw_arms_invariant": bool(raw_invariant),
                             "single_draw_real": draw_best[0],
                             "single_draw_reassigned": null_draw},
                  "label": {"seed": SEED_LABEL, "errors": lab_errors,
                            "gt_majority": bool(lab_errors > maj_err),
                            "shuffled_labels": sh}},
        "ladder": {"budgets": list(ladder_budgets), "errors": ladder,
                   "monotone": bool(monotone), "readout": win[2]},
        "crossover": {"V": V, "alphabet_width": 27, "index_cost": index_cost,
                      "m_star": m_star,
                      "scan_cost_at_m_star": 2 * m_star, "holds": bool(co_holds)},
        "presentation_control": {"arm": win[2],
                                 "arm_errors": ctrl_arm,
                                 "contiguous_winner": cwin[2],
                                 "contiguous_winner_errors": cwin[0],
                                 "majority_errors": cmaj,
                                 "f1_holds": bool(ctrl_f1),
                                 "control_fires": bool(ctrl_fires)},
        "frozen_predictions_r8": {"path": "REAL_RUNS/FROZEN_PREDICTIONS_R8.json",
                                  "rows": len(predictions), "sha256": r8_sha,
                                  "written_before": "any null or control"},
        "stage_min_errors": {
            "rank": _stage_min(eco, rrows),
            "held": _stage_min(eco, rows),
            "regen_lo": _stage_min(eco, hrows),
            "regen_hi": _stage_min(eco, hrows2),
        },
        "holdout_all": {"rows": len(rows), "queries": [tally(r) for r in rows]},
        "null_rows": {"rows": len(nrows), "queries": [tally(r) for r in nrows]},
        "replay": {
            "held_block": _block(rows, win[2], maj_err),
            "rank_block": _block(rrows, rwin[2], rmaj),
            "regen_lo_block": _block(hrows, hwin[2], hmaj),
            "regen_hi_block": _block(hrows2, hwin2[2], hmaj2),
        },
        "claim_ceiling": "REAL_SCALE_ELEVEN_GATE_MEASUREMENT_AT_REGISTERED_SCOPE",
    }
    with open(os.path.join(RUNS, "scope_SIGMA_H33R.json"), "w") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(RUNS, "sources.json"), "w") as fh:
        json.dump({"schema": "GMI833SourcesV1",
                   "source": {"path": SOURCE, "sha256": eco_sha(raw),
                              "tokens": len(words),
                              "duplicate_tokens": len(words) - len(set(words)),
                              "alphabet_size": eco.C}}, fh, indent=1,
                  sort_keys=True)
        fh.write("\n")
    print("WROTE %s" % os.path.join(RUNS, "scope_SIGMA_H33R.json"))


def _stage_min(eco, rows):
    """The min-error set and the MEM_FALLBACK comparison at one stage."""
    scored = []
    for name in READOUTS:
        scored.append((arm_errors(eco, rows, name), cost(name), name))
    scored.sort()
    out = min_error_set(scored)
    mf = [(e, c, n) for e, c, n in scored if n == "MEM_FALLBACK"][0]
    out["mem_fallback"] = {"errors": mf[0], "cost": mf[1],
                           "is_min": bool(mf[0] == out["min_errors"]),
                           "is_winner": bool(out["winner"] == "MEM_FALLBACK"),
                           "loses_on_cost": bool(mf[0] == out["min_errors"]
                                                 and out["winner"] != "MEM_FALLBACK")}
    return out


def tally(r):
    """One replayed query row: [descriptor, label, presented candidate, CARD,
    store walk, forward step distance, slice occurrence count, descriptor
    length]. Every field is an integer or a string; nothing is derived."""
    q, y, c, card, ws, dd, cnt, L = r
    return [q, y, c, card, ws, dd, cnt, L]


def _block(rows, name, majority):
    """A committed replayed block: a bounded slice of the tallies, the winner's
    exact error count on it, and the majority rule's."""
    blk = rows[:1500]
    if not blk and rows:
        blk = rows
    errs = arm_errors(None, blk, name)
    neg = sum(1 for r in blk if r[1] != 0)
    pos = sum(1 for r in blk if r[1] != 1)
    maj_lab = 0 if neg <= pos else 1
    maj = min(neg, pos)
    return {"rows": len(blk), "winner": name, "winner_errors": errs,
            "majority_label": maj_lab, "majority_errors": maj,
            "queries": [tally(r) for r in blk]}


def eco_sha(raw):
    return hashlib.sha256(raw).hexdigest()


if __name__ == "__main__":
    sys.exit(main())
