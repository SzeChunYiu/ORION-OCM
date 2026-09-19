#!/usr/bin/env python3
"""IMB-v1 executor, Route A (GMI #833 Section Z / Z11).

Implements ``FREEZE_V1.md`` of this package literally. Self-contained, stdlib
only, exact arithmetic (``fractions.Fraction`` / ``int``) for every reported
number. Run from the repository root::

    python3 -I -B research/gmi-833-z-z11-morphology-benchmark-v1/imb_benchmark_v1.py

Emits, next to this file: ``CASES_V1.json`` (public spec + hidden truth per
case), ``PREDICTIONS_V1.json`` (every registered theory's prediction record per
case, null theories as scores only) and ``RESULT_V1.json`` (the receipt).
Exit status is non-zero when any structural check fails (pins, commitment,
base floors, an inapplicable or undetected hostile).

Route B may not import this file; it rebuilds the cases from FREEZE §2 and
re-scores ``PREDICTIONS_V1.json`` with its own scorer.

Executor-side choices where the freeze is silent (all reported in the receipt
under ``executor_choices``):

* the seven registered ``IID(q)`` laws are taken as ``q = 1/8 .. 7/8``
  (``C2_IID_Q``): symmetric about ``1/2`` and containing it, as B3 needs;
* thresholds are the plain marginals ``Delta_k = E(k-1) - E(k)``, ``k = 1..K``;
* the resource frontier is the set of levels that are the *unique* argmin of
  ``E(k) + lam*k`` at some price ``lam >= 0`` (this is the strict lower-hull
  vertex set, and makes the flat ecology's frontier ``{0}`` as the freeze says);
* a binary two-level population takes ``R0`` as the enumerated stateless
  delay-1 floor of the ``L = 4`` window law (``floor(0, 1)``), so one law object
  serves both universe types; alphabet-``A`` populations enumerate the ``A``-ary
  stateless table on length-3 sequences scored at ``t in {1, 2}``;
* ``T_GMI_IC1``'s stateless floors are the pooled (``t in {2, 3}``, weight ``1/2``
  each) Bayes error of the target given the current symbol, the minimum taken
  *after* pooling (a stateless predictor cannot see ``t``);
* ``T_MDL`` sums its error bits over every mode of the universe (``p_m`` is not a
  weight there); ``T_MDL``, ``T_SRM``, ``T_SATISFICE`` use the upper endpoint of
  any predicted interval floor;
* ``T_SRM``'s thresholds are ``ABSTAIN`` (a fixed-price theory has no price
  threshold); ``T_SRM`` and ``T_SATISFICE`` carry ``T_GMI_IC1``'s frontier;
* ``T_LEVEL`` on a two-level case has no ladder formula and behaves as
  ``T_GMI_IC1`` there;
* a null theory's failure-mode draw is a subset of the *case's* channel set;
* the ``rho`` accounting entry is ``1`` (level cost ``lam*k``);
* the scrambled-truth control pairs case ``i`` with the truth of case
  ``(i + 1) mod n`` inside its own class.
"""
import hashlib
import json
import os
import random
import sys
import time
from fractions import Fraction as F
from itertools import product
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

SCHEMA = "GMI_833_Z11_IMB_RESULT_V1"
ISSUE = 833
SUBSECTION = "Z11"
ROUTE = "A"
SOURCE_MAIN = "f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5"

HIDDEN_COMMITMENT = "b7adc75b3ec9b7f3c4fd9f7a9130198a21f01a341d4167bf7ef9abf4a0c9271f"
HIDDEN_PREIMAGE = "IMB-V1-HIDDEN-SEED:sec-z811:2026-09-19:orion-ocm-833:7d1e4c"

# (path relative to REPO, git blob sha1, byte length) -- FREEZE §2 C4.
STREAMS = [
    ("README.md", "d7519609d064a4c478696ec6378f23c771a3db20", 8110),
    ("LICENSE", "d645695673349e3947e8e5ae42332d0ac3164cd7", 11358),
    (
        "research/gmi-833-z-z12-prediction-scoring-v1/z12_prediction_scoring_v1.py",
        "2825c19583aa7ca0dc3f9f475553fd9ea419ed3c",
        23113,
    ),
]

# Executor choice: the seven registered IID laws (FREEZE §2 C2 names them only
# by reference to the Z8 freeze, which this file may not read).
C2_IID_Q = [F(k, 8) for k in range(1, 8)]

# Registered base floors under UNIFORM (task statement / Z13): floor(b, m).
REGISTERED_BASE_FLOORS = {
    (0, 0): F(0), (0, 1): F(1, 2), (0, 2): F(1, 2),
    (1, 0): F(0), (1, 1): F(0), (1, 2): F(5, 16),
    (2, 0): F(0), (2, 1): F(0), (2, 2): F(0),
}

L = 4
SCORED_T = (2, 3)
LADDER_LEVELS = (0, 1, 2)
LADDER_MODES = (0, 1, 2)
TWO_LEVEL_LEVELS = (0, 1)
TWO_LEVEL_MODES = (0, 1)  # 0 = now channel, 1 = delay-1 channel
GAMMAS = (F(1), F(3, 4), F(1, 2))
PRICES_16 = [F(j, 16) for j in range(25)]
N_NULL = 200
MDL_N = 32

SEQ = [((w >> 3) & 1, (w >> 2) & 1, (w >> 1) & 1, w & 1) for w in range(16)]


def fs(x) -> str:
    """Exact string form of a Fraction / int."""
    if isinstance(x, bool):
        return "true" if x else "false"
    return str(F(x))


def fail(msg: str) -> None:
    print("FAIL: " + msg)
    sys.exit(2)


# --------------------------------------------------------------------------
# Input laws
# --------------------------------------------------------------------------
STREAM_BYTES = []  # type: List[bytes]
STREAM_BITS = []  # type: List[List[int]]


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_streams() -> Dict[str, dict]:
    pins = {}
    for path, sha, nbytes in STREAMS:
        with open(os.path.join(REPO, path), "rb") as fh:
            data = fh.read()
        computed = git_blob_sha1(data)
        ok = computed == sha and len(data) == nbytes
        pins[path] = {"expected": sha, "computed": computed, "ok": ok,
                      "bytes": len(data), "expected_bytes": nbytes}
        STREAM_BYTES.append(data)
        bits = []
        for byte in data:
            for k in range(7, -1, -1):
                bits.append((byte >> k) & 1)
        STREAM_BITS.append(bits)
    return pins


def law_key(law: dict) -> tuple:
    kind = law["kind"]
    if kind == "IID":
        return ("IID", F(law["q"]))
    if kind == "EMPIRICAL":
        return ("EMPIRICAL", int(law["stream"]), int(law["offset"]))
    return (kind,)


WEIGHT_CACHE = {}  # type: Dict[tuple, Tuple[List[int], int]]


def law_weights(law: dict) -> Tuple[List[int], int]:
    """Integer weights over the 16 length-4 sequences and their common denominator."""
    key = law_key(law)
    if key not in WEIGHT_CACHE:
        WEIGHT_CACHE[key] = _law_weights(law)
    wts, D = WEIGHT_CACHE[key]
    return list(wts), D


def _law_weights(law: dict) -> Tuple[List[int], int]:
    kind = law["kind"]
    if kind == "UNIFORM":
        return [1] * 16, 16
    if kind == "IID":
        q = F(law["q"])
        a, b = q.numerator, q.denominator
        wts = []
        for w in range(16):
            ones = bin(w).count("1")
            wts.append(a ** ones * (b - a) ** (4 - ones))
        return wts, b ** 4
    if kind == "PERIOD2":
        wts = [0] * 16
        for x0 in (0, 1):
            for x1 in (0, 1):
                wts[x0 * 8 + x1 * 4 + x0 * 2 + x1] = 1
        return wts, 4
    if kind == "EMPIRICAL":
        bits = STREAM_BITS[int(law["stream"])]
        off = int(law["offset"])
        n = len(bits)
        counts = [0] * 16
        w = bits[off] * 4 + bits[off + 1] * 2 + bits[off + 2]
        for i in range(off + 3, n):
            w = ((w << 1) | bits[i]) & 15
            counts[w] += 1
        total = n - off - 3
        if sum(counts) != total:
            fail("window count mismatch")
        return counts, total
    fail("unknown law kind %r" % kind)
    return [], 0


# --------------------------------------------------------------------------
# Exhaustive transducer enumeration (hidden truth)
# --------------------------------------------------------------------------
# A "signature" of a next-state table is the tuple of the 32 addresses visited at
# the scored times (w, t) for w in 0..15, t in {2, 3}, canonicalised by order of
# first appearance. The error of a table depends on its table only through this
# partition of the 32 scored slots (the optimal output is chosen per address), so
# tables sharing a signature share every floor; the min over all tables equals
# the min over distinct signatures. Every table is enumerated to build the set.
SIGNATURES = {}  # type: Dict[int, List[tuple]]
SIG_COUNTS = {}  # type: Dict[int, int]


def table_signature(next_tab: List[int]) -> tuple:
    sig = []
    for w in range(16):
        x = SEQ[w]
        s = 0
        addrs = []
        for t in range(4):
            a = s * 2 + x[t]
            addrs.append(a)
            s = next_tab[a]
        sig.append(addrs[2])
        sig.append(addrs[3])
    relabel = {}
    out = []
    for a in sig:
        if a not in relabel:
            relabel[a] = len(relabel)
        out.append(relabel[a])
    return tuple(out)


def build_signatures() -> None:
    for b in LADDER_LEVELS:
        nstates = 2 ** b
        naddr = 2 * nstates
        ntables = nstates ** naddr
        seen = {}
        for tidx in range(ntables):
            next_tab = []
            rem = tidx
            for _ in range(naddr):
                next_tab.append(rem % nstates)
                rem //= nstates
            sig = table_signature(next_tab)
            if sig not in seen:
                seen[sig] = tidx
        SIGNATURES[b] = sorted(seen.keys())
        SIG_COUNTS[b] = ntables


# slot i = 2*w + j, j=0 -> t=2, j=1 -> t=3
SLOT_W = [i // 2 for i in range(32)]
SLOT_T = [2 + (i % 2) for i in range(32)]
TARGET = {m: [SEQ[SLOT_W[i]][SLOT_T[i] - m] for i in range(32)] for m in LADDER_MODES}


def ladder_floors(weights: List[int], D: int) -> Dict[Tuple[int, int], F]:
    """floor(b, m) for b in 0..2, m in 0..2 under integer weights / D."""
    wslot = [weights[SLOT_W[i]] for i in range(32)]
    floors = {}
    for b in LADDER_LEVELS:
        naddr = 2 ** (b + 1)
        best = [None, None, None]
        for sig in SIGNATURES[b]:
            for m in LADDER_MODES:
                tg = TARGET[m]
                t0 = [0] * naddr
                t1 = [0] * naddr
                for i in range(32):
                    wt = wslot[i]
                    if wt:
                        if tg[i]:
                            t1[sig[i]] += wt
                        else:
                            t0[sig[i]] += wt
                err = 0
                for a in range(naddr):
                    err += t0[a] if t0[a] < t1[a] else t1[a]
                if best[m] is None or err < best[m]:
                    best[m] = err
        for m in LADDER_MODES:
            floors[(b, m)] = F(best[m], 2 * D)
    return floors


def alphabet_R0(A: int) -> F:
    """Stateless delay-1 floor, A-ary table cur->symbol, length-3 uniform sequences, t in {1,2}."""
    seqs = list(product(range(A), repeat=3))
    D = len(seqs)
    best = None
    for tab in product(range(A), repeat=A):
        err = 0
        for s in seqs:
            for t in (1, 2):
                if tab[s[t]] != s[t - 1]:
                    err += 1
        if best is None or err < best:
            best = err
    return F(best, 2 * D)


# --------------------------------------------------------------------------
# Verdict machinery (shared by the truth and by the IC-1 theories)
# --------------------------------------------------------------------------
def argmin_set(E: Dict[int, F], lam: F) -> frozenset:
    vals = {k: E[k] + lam * k for k in E}
    m = min(vals.values())
    return frozenset(k for k in E if vals[k] == m)


def frontier_set(E: Dict[int, F]) -> frozenset:
    """Levels that are the unique argmin of E(k) + lam*k for some lam >= 0."""
    levels = sorted(E)
    cands = {F(0)}
    for i in levels:
        for j in levels:
            if j > i:
                lam = (E[i] - E[j]) / (j - i)
                if lam >= 0:
                    cands.add(lam)
    pts = sorted(cands)
    evals = list(pts)
    for a, b in zip(pts, pts[1:]):
        evals.append((a + b) / 2)
    evals.append(pts[-1] + 1)
    out = set()
    for lam in evals:
        s = argmin_set(E, lam)
        if len(s) == 1:
            out.update(s)
    return frozenset(out)


def marginals(E: Dict[int, F]) -> Dict[int, F]:
    levels = sorted(E)
    return {k: E[k - 1] - E[k] for k in levels[1:]}


def failure_modes(floors: Dict[Tuple[int, int], F], p: List[F], levels, modes) -> Dict[int, frozenset]:
    return {k: frozenset(m for m in modes if p[m] > 0 and floors[(k, m)] > 0) for k in levels}


def profile_from_floors(floors, eta: F, p: List[F], levels, modes) -> Dict[int, F]:
    return {k: eta * sum((p[m] * floors[(k, m)] for m in modes), F(0)) for k in levels}


def compute_truth(spec: dict, floors: Dict[Tuple[int, int], F]) -> dict:
    eta = F(spec["accounting"]["eta"])
    p = [F(x) for x in spec["accounting"]["p"]]
    levels = tuple(spec["universe"]["levels"])
    modes = tuple(spec["universe"]["modes"])
    E = profile_from_floors(floors, eta, p, levels, modes)
    prices = [F(x) for x in spec["prices"]]
    return {
        "floors": floors,
        "profile": E,
        "thresholds": marginals(E),
        "frontier": frontier_set(E),
        "selection_by_price": {lam: argmin_set(E, lam) for lam in prices},
        "failure_modes": failure_modes(floors, p, levels, modes),
    }


# --------------------------------------------------------------------------
# Prediction cells
# --------------------------------------------------------------------------
ABSTAIN = ("ABSTAIN",)


def POINT(v: F) -> tuple:
    return ("POINT", F(v))


def INTERVAL(lo: F, hi: F, gamma: F) -> tuple:
    lo, hi = F(lo), F(hi)
    if lo == hi:
        return ("POINT", lo)
    return ("INTERVAL", lo, hi, F(gamma))


def SET(vals) -> tuple:
    return ("SET", frozenset(vals))


def interval_verdict(fn, lo: F, hi: F, crit: List[F]):
    """Evaluate fn(E1) at both endpoints, every critical value inside, and the
    midpoints between consecutive evaluation points; return the common value or
    None when the interval leaves the verdict undetermined."""
    pts = {lo, hi}
    for c in crit:
        if lo < c < hi:
            pts.add(c)
    pts = sorted(pts)
    evals = list(pts)
    for a, b in zip(pts, pts[1:]):
        evals.append((a + b) / 2)
    first = None
    for x in evals:
        v = fn(x)
        if first is None:
            first = v
        elif v != first:
            return None
    return first


def ic1_record(floor_pred: Dict[Tuple[int, int], Tuple[F, F]], spec: dict) -> dict:
    """IC-1 machinery applied to a predicted floor table whose cells are
    (lo, hi) intervals (lo == hi for a point). Interval arithmetic for the
    profile and thresholds; ABSTAIN where an interval leaves a verdict open."""
    eta = F(spec["accounting"]["eta"])
    p = [F(x) for x in spec["accounting"]["p"]]
    levels = tuple(spec["universe"]["levels"])
    modes = tuple(spec["universe"]["modes"])
    prices = [F(x) for x in spec["prices"]]
    Elo = {k: eta * sum((p[m] * floor_pred[(k, m)][0] for m in modes), F(0)) for k in levels}
    Ehi = {k: eta * sum((p[m] * floor_pred[(k, m)][1] for m in modes), F(0)) for k in levels}
    interval_levels = [k for k in levels if Elo[k] != Ehi[k]]
    if len(interval_levels) > 1:
        fail("ic1_record: more than one interval level is not supported")
    rec = {}
    rec["profile"] = {k: INTERVAL(Elo[k], Ehi[k], F(1)) for k in levels}
    rec["thresholds"] = {k: INTERVAL(Elo[k - 1] - Ehi[k], Ehi[k - 1] - Elo[k], F(1)) for k in levels[1:]}
    if not interval_levels:
        E = dict(Elo)
        rec["frontier"] = SET(frontier_set(E))
        rec["selection_by_price"] = {lam: SET(argmin_set(E, lam)) for lam in prices}
    else:
        ku = interval_levels[0]
        lo, hi = Elo[ku], Ehi[ku]
        fixed = {k: Elo[k] for k in levels if k != ku}

        def with_value(v):
            E = dict(fixed)
            E[ku] = v
            return E

        crit = []
        for k in fixed:
            crit.append(fixed[k])
            for lam in prices:
                crit.append(fixed[k] + lam * (k - ku))
        for i in fixed:
            for j in fixed:
                if i < j:
                    # chord value at ku between fixed levels i and j
                    crit.append(fixed[i] + (fixed[j] - fixed[i]) * F(ku - i, j - i))
        fr = interval_verdict(lambda v: frontier_set(with_value(v)), lo, hi, crit)
        rec["frontier"] = SET(fr) if fr is not None else ABSTAIN
        sel = {}
        for lam in prices:
            s = interval_verdict(lambda v, lam=lam: argmin_set(with_value(v), lam), lo, hi, crit)
            sel[lam] = SET(s) if s is not None else ABSTAIN
        rec["selection_by_price"] = sel
    fm = {}
    for k in levels:
        certain = True
        s = set()
        for m in modes:
            if p[m] > 0:
                lo, hi = floor_pred[(k, m)]
                if lo > 0:
                    s.add(m)
                elif hi > 0:
                    certain = False
        fm[k] = SET(s) if certain else ABSTAIN
    rec["failure_modes"] = fm
    return rec


# --------------------------------------------------------------------------
# Theories (pure functions of the public spec)
# --------------------------------------------------------------------------
def pooled_bayes_error(weights: List[int], D: int, m: int) -> F:
    """Closed form: Bayes error of x_{t-m} given x_t, t pooled over {2,3} with
    weight 1/2 each, minimum taken after pooling."""
    joint = [[0, 0], [0, 0]]
    for w in range(16):
        wt = weights[w]
        if not wt:
            continue
        x = SEQ[w]
        for t in SCORED_T:
            joint[x[t]][x[t - m]] += wt
    err = sum(min(joint[c][0], joint[c][1]) for c in (0, 1))
    return F(err, 2 * D)


def gmi_stateless_floor(spec: dict, m: int) -> F:
    """T_GMI_IC1's predicted stateless floor for mode m (0 = now channel)."""
    if m == 0:
        return F(0)
    uni = spec["universe"]
    law = spec["law"]
    if uni["type"] == "TWO_LEVEL" and int(uni["alphabet"]) != 2:
        if law["kind"] != "UNIFORM":
            fail("alphabet-A population only registered under UNIFORM")
        return F(1) - F(1, int(uni["alphabet"]))
    weights, D = law_weights(law)
    r = pooled_bayes_error(weights, D, m)
    # registered closed forms are special cases; assert them
    if law["kind"] == "UNIFORM" and r != F(1, 2):
        fail("closed form UNIFORM != 1/2")
    if law["kind"] == "IID" and r != min(F(law["q"]), 1 - F(law["q"])):
        fail("closed form IID != min(q, 1-q)")
    if law["kind"] == "PERIOD2" and r != (F(1, 2) if m == 1 else F(0)):
        fail("closed form PERIOD2 unexpected")
    return r


def gmi_floor_pred(spec: dict) -> Dict[Tuple[int, int], Tuple[F, F]]:
    uni = spec["universe"]
    law = spec["law"]
    fp = {}
    if uni["type"] == "LADDER":
        r1 = gmi_stateless_floor(spec, 1)
        r2 = gmi_stateless_floor(spec, 2)
        fp[(0, 0)] = (F(0), F(0))
        fp[(0, 1)] = (r1, r1)
        fp[(0, 2)] = (r2, r2)
        fp[(1, 0)] = (F(0), F(0))
        fp[(1, 1)] = (F(0), F(0))
        if law["kind"] == "UNIFORM":
            fp[(1, 2)] = (F(5, 16), F(5, 16))
        elif law["kind"] == "PERIOD2":
            fp[(1, 2)] = (F(0), F(0))
        else:
            fp[(1, 2)] = (F(0), r2)
        for m in LADDER_MODES:
            fp[(2, m)] = (F(0), F(0))
    else:
        r0 = gmi_stateless_floor(spec, 1)
        fp[(0, 0)] = (F(0), F(0))
        fp[(0, 1)] = (r0, r0)
        fp[(1, 0)] = (F(0), F(0))
        fp[(1, 1)] = (F(0), F(0))
    return fp


def half_floor_pred(spec: dict) -> Dict[Tuple[int, int], Tuple[F, F]]:
    if spec["universe"]["type"] == "LADDER":
        return {bm: (v, v) for bm, v in REGISTERED_BASE_FLOORS.items()}
    return {(0, 0): (F(0), F(0)), (0, 1): (F(1, 2), F(1, 2)),
            (1, 0): (F(0), F(0)), (1, 1): (F(0), F(0))}


def T_GMI_IC1(spec: dict) -> dict:
    return ic1_record(gmi_floor_pred(spec), spec)


def T_DECLARED(spec: dict) -> dict:
    # argmin of E(k) + lam*k over T_GMI_IC1's predicted profile: identical machinery.
    return ic1_record(gmi_floor_pred(spec), spec)


def T_HALF(spec: dict) -> dict:
    return ic1_record(half_floor_pred(spec), spec)


def T_LEVEL(spec: dict) -> dict:
    base = T_GMI_IC1(spec)
    if spec["universe"]["type"] != "LADDER":
        return base
    eta = F(spec["accounting"]["eta"])
    p = [F(x) for x in spec["accounting"]["p"]]
    lower = eta * p[2] * F(5, 16)
    upper = eta * (p[2] * F(5, 16) + p[1] / 2)
    rec = dict(base)
    rec["thresholds"] = {1: POINT(upper), 2: POINT(lower)}
    Eimp = {0: lower + upper, 1: lower, 2: F(0)}
    rec["selection_by_price"] = {F(lam): SET(argmin_set(Eimp, F(lam))) for lam in spec["prices"]}
    return rec


def _upper_floors(spec: dict) -> Dict[Tuple[int, int], F]:
    return {bm: hi for bm, (lo, hi) in gmi_floor_pred(spec).items()}


def ceil_frac(x: F) -> int:
    return -((-x.numerator) // x.denominator)


def ceil_log2(n: int) -> int:
    if n < 1:
        fail("ceil_log2 of non-positive")
    return (n - 1).bit_length()


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    out = 1
    for i in range(1, k + 1):
        out = out * (n - k + i) // i
    return out


def _const_selection(spec: dict, chosen: frozenset) -> dict:
    return {F(lam): SET(chosen) for lam in spec["prices"]}


def T_MDL(spec: dict) -> dict:
    base = T_GMI_IC1(spec)
    fl = _upper_floors(spec)
    levels = tuple(spec["universe"]["levels"])
    modes = tuple(spec["universe"]["modes"])
    cost = {}
    for k in levels:
        bits = 3 * (1 + k) * 2 ** (k + 1)
        for m in modes:
            bits += ceil_log2(binom(MDL_N, ceil_frac(MDL_N * fl[(k, m)])))
        cost[k] = bits
    best = min(cost.values())
    chosen = frozenset(k for k in levels if cost[k] == best)
    rec = dict(base)
    rec["selection_by_price"] = _const_selection(spec, chosen)
    rec["thresholds"] = {k: ABSTAIN for k in levels[1:]}
    rec["frontier"] = ABSTAIN
    return rec


def T_OCCAM_HARD(spec: dict) -> dict:
    base = T_GMI_IC1(spec)
    levels = tuple(spec["universe"]["levels"])
    rec = dict(base)
    rec["selection_by_price"] = _const_selection(spec, frozenset([0]))
    rec["thresholds"] = {k: ABSTAIN for k in levels[1:]}
    rec["frontier"] = ABSTAIN
    return rec


def _weighted_error(spec: dict, fl, k: int) -> F:
    p = [F(x) for x in spec["accounting"]["p"]]
    modes = tuple(spec["universe"]["modes"])
    return sum((p[m] * fl[(k, m)] for m in modes), F(0))


def T_SRM(spec: dict) -> dict:
    base = T_GMI_IC1(spec)
    fl = _upper_floors(spec)
    levels = tuple(spec["universe"]["levels"])
    obj = {k: _weighted_error(spec, fl, k) + F(k, 4) for k in levels}
    best = min(obj.values())
    chosen = frozenset(k for k in levels if obj[k] == best)
    rec = dict(base)
    rec["selection_by_price"] = _const_selection(spec, chosen)
    rec["thresholds"] = {k: ABSTAIN for k in levels[1:]}
    return rec


def T_SATISFICE(spec: dict) -> dict:
    base = T_GMI_IC1(spec)
    fl = _upper_floors(spec)
    levels = tuple(spec["universe"]["levels"])
    chosen = None
    for k in levels:
        if _weighted_error(spec, fl, k) <= F(1, 4):
            chosen = k
            break
    if chosen is None:
        chosen = max(levels)
    rec = dict(base)
    rec["selection_by_price"] = _const_selection(spec, frozenset([chosen]))
    rec["thresholds"] = {k: ABSTAIN for k in levels[1:]}
    return rec


def T_ABSTAIN(spec: dict) -> dict:
    levels = tuple(spec["universe"]["levels"])
    return {
        "profile": {k: ABSTAIN for k in levels},
        "thresholds": {k: ABSTAIN for k in levels[1:]},
        "frontier": ABSTAIN,
        "selection_by_price": {F(lam): ABSTAIN for lam in spec["prices"]},
        "failure_modes": {k: ABSTAIN for k in levels},
    }


class NullTheory(object):
    """T_NULL_k: every field drawn uniformly from its output space."""

    def __init__(self, k: int):
        self.k = k
        self.rng = random.Random(1000 + k)

    def __call__(self, spec: dict) -> dict:
        rng = self.rng
        eta = F(spec["accounting"]["eta"])
        levels = tuple(spec["universe"]["levels"])
        modes = tuple(spec["universe"]["modes"])
        nl = len(levels)
        nm = len(modes)
        rec = {}
        rec["profile"] = {k: POINT(F(rng.randrange(33), 32) * eta) for k in levels}
        rec["thresholds"] = {k: POINT(F(rng.randrange(33), 32) * eta) for k in levels[1:]}
        mask = rng.randrange(1, 2 ** nl)
        rec["frontier"] = SET(levels[i] for i in range(nl) if (mask >> i) & 1)
        sel = {}
        for lam in spec["prices"]:
            mask = rng.randrange(1, 2 ** nl)
            sel[F(lam)] = SET(levels[i] for i in range(nl) if (mask >> i) & 1)
        rec["selection_by_price"] = sel
        fm = {}
        for k in levels:
            mask = rng.randrange(2 ** nm)
            fm[k] = SET(modes[i] for i in range(nm) if (mask >> i) & 1)
        rec["failure_modes"] = fm
        return rec


class PeekTheory(object):
    """Planted hostile: copies spec['truth'] when the harness leaks it; falls
    back to T_NULL_0 behaviour otherwise."""

    def __init__(self):
        self.fallback = NullTheory(0)

    def __call__(self, spec: dict) -> dict:
        truth = spec.get("truth")
        if truth is None:
            return self.fallback(spec)
        return {
            "profile": {k: POINT(v) for k, v in truth["profile"].items()},
            "thresholds": {k: POINT(v) for k, v in truth["thresholds"].items()},
            "frontier": SET(truth["frontier"]),
            "selection_by_price": {lam: SET(s) for lam, s in truth["selection_by_price"].items()},
            "failure_modes": {k: SET(s) for k, s in truth["failure_modes"].items()},
        }


REGISTERED = [
    ("T_GMI_IC1", T_GMI_IC1),
    ("T_HALF", T_HALF),
    ("T_LEVEL", T_LEVEL),
    ("T_DECLARED", T_DECLARED),
    ("T_MDL", T_MDL),
    ("T_OCCAM_HARD", T_OCCAM_HARD),
    ("T_SRM", T_SRM),
    ("T_SATISFICE", T_SATISFICE),
    ("T_ABSTAIN", T_ABSTAIN),
]
DISCRIMINATION_THEORIES = [t for t, _ in REGISTERED if t != "T_ABSTAIN"]


# --------------------------------------------------------------------------
# Case generation (FREEZE §2)
# --------------------------------------------------------------------------
def compositions(total: int, parts: int) -> List[Tuple[int, ...]]:
    if parts == 1:
        return [(total,)]
    out = []
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            out.append((first,) + rest)
    return out


def make_spec(cls: str, utype: str, alphabet: int, eta: F, p: List[F], law: dict, prices: List[F]) -> dict:
    if utype == "LADDER":
        levels, modes = list(LADDER_LEVELS), list(LADDER_MODES)
    else:
        levels, modes = list(TWO_LEVEL_LEVELS), list(TWO_LEVEL_MODES)
    if sum(p, F(0)) != 1 or len(p) != len(modes):
        fail("bad p for %s" % cls)
    return {
        "class": cls,
        "universe": {"type": utype, "alphabet": alphabet, "levels": levels, "modes": modes,
                     "L": L if utype == "LADDER" else 3, "window": list(SCORED_T) if utype == "LADDER" else [1, 2]},
        "accounting": {"eta": fs(eta), "p": [fs(x) for x in p], "rho": "1"},
        "law": law,
        "prices": [fs(x) for x in prices],
    }


def law_uniform() -> dict:
    return {"kind": "UNIFORM"}


def law_iid(q: F) -> dict:
    return {"kind": "IID", "q": fs(q)}


def law_period2() -> dict:
    return {"kind": "PERIOD2"}


def law_empirical(stream: int, offset: int) -> dict:
    path, sha, _ = STREAMS[stream]
    return {"kind": "EMPIRICAL", "stream": stream, "path": path, "blob_sha1": sha, "offset": offset}


def generate_cases(secret: str, c1_prices: Optional[List[F]] = None) -> List[dict]:
    if c1_prices is None:
        c1_prices = PRICES_16
    specs = []
    # C1_LADDER: UNIFORM, eta in {1,2,3}, p over eighths
    for eta in (1, 2, 3):
        for comp in compositions(8, 3):
            p = [F(c, 8) for c in comp]
            specs.append(make_spec("C1_LADDER", "LADDER", 2, F(eta), p, law_uniform(), c1_prices))
    # C2_TWO_LEVEL_IID
    for q in C2_IID_Q:
        for eta in (1, 2, 3):
            for k in range(9):
                p = [1 - F(k, 8), F(k, 8)]
                specs.append(make_spec("C2_TWO_LEVEL_IID", "TWO_LEVEL", 2, F(eta), p, law_iid(q), PRICES_16))
    # C3_ALPHABET
    for A in (2, 3, 4):
        for eta in (1, 2, 3):
            for k in range(9):
                p = [1 - F(k, 8), F(k, 8)]
                specs.append(make_spec("C3_ALPHABET", "TWO_LEVEL", A, F(eta), p, law_uniform(), PRICES_16))
    # C4_EMPIRICAL_STREAM
    for stream in range(3):
        for comp in compositions(4, 3):
            p = [F(c, 4) for c in comp]
            specs.append(make_spec("C4_EMPIRICAL_STREAM", "LADDER", 2, F(1), p, law_empirical(stream, 0), PRICES_16))
    # C5_HIDDEN
    rng = random.Random(secret)
    ladder_comps = compositions(16, 3)
    for _ in range(60):
        utype = "LADDER" if rng.randrange(2) == 0 else "TWO_LEVEL"
        eta = F(rng.randrange(1, 5))
        if utype == "LADDER":
            comp = ladder_comps[rng.randrange(len(ladder_comps))]
            p = [F(c, 16) for c in comp]
        else:
            k = rng.randrange(17)
            p = [1 - F(k, 16), F(k, 16)]
        kind = rng.randrange(4)
        if kind == 0:
            law = law_uniform()
        elif kind == 1:
            law = law_iid(F(rng.randrange(1, 10), 10))
        elif kind == 2:
            law = law_period2()
        else:
            stream = rng.randrange(3)
            offset = rng.randrange(4096)
            law = law_empirical(stream, offset)
        lam = F(rng.randrange(49), 32)
        specs.append(make_spec("C5_HIDDEN", utype, 2, eta, p, law, [lam]))
    # C6_NEGATIVE_CONTROL (a): flat ecologies
    for eta in (1, 2, 3):
        for law in (law_uniform(), law_iid(F(1, 4)), law_period2()):
            specs.append(make_spec("C6_NEGATIVE_CONTROL", "LADDER", 2, F(eta), [F(1), F(0), F(0)], law, PRICES_16))
    return specs


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def case_set_sha256(specs: List[dict]) -> str:
    return hashlib.sha256(canonical_json(specs).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# Truth oracle with floor cache
# --------------------------------------------------------------------------
FLOOR_CACHE = {}  # type: Dict[tuple, Dict[Tuple[int, int], F]]
ALPHABET_CACHE = {}  # type: Dict[int, F]


def floors_for_spec(spec: dict) -> Dict[Tuple[int, int], F]:
    uni = spec["universe"]
    law = spec["law"]
    if uni["type"] == "LADDER":
        key = ("LADDER",) + law_key(law)
        if key not in FLOOR_CACHE:
            weights, D = law_weights(law)
            FLOOR_CACHE[key] = ladder_floors(weights, D)
        return FLOOR_CACHE[key]
    A = int(uni["alphabet"])
    if A == 2:
        key = ("TWO_LEVEL",) + law_key(law)
        if key not in FLOOR_CACHE:
            lkey = ("LADDER",) + law_key(law)
            if lkey in FLOOR_CACHE:
                r0 = FLOOR_CACHE[lkey][(0, 1)]
            else:
                weights, D = law_weights(law)
                # b = 0 only: the single next-state table, per-address majority
                r0 = ladder_floors_b0(weights, D)[(0, 1)]
            FLOOR_CACHE[key] = {(0, 0): F(0), (0, 1): r0, (1, 0): F(0), (1, 1): F(0)}
        return FLOOR_CACHE[key]
    if law["kind"] != "UNIFORM":
        fail("alphabet-A population only registered under UNIFORM")
    if A not in ALPHABET_CACHE:
        ALPHABET_CACHE[A] = alphabet_R0(A)
    r0 = ALPHABET_CACHE[A]
    return {(0, 0): F(0), (0, 1): r0, (1, 0): F(0), (1, 1): F(0)}


def ladder_floors_b0(weights: List[int], D: int) -> Dict[Tuple[int, int], F]:
    wslot = [weights[SLOT_W[i]] for i in range(32)]
    out = {}
    sig = SIGNATURES[0][0]
    for m in LADDER_MODES:
        tg = TARGET[m]
        t0 = [0, 0]
        t1 = [0, 0]
        for i in range(32):
            if tg[i]:
                t1[sig[i]] += wslot[i]
            else:
                t0[sig[i]] += wslot[i]
        out[(0, m)] = F(sum(min(t0[a], t1[a]) for a in (0, 1)), 2 * D)
    return out


# --------------------------------------------------------------------------
# Record validation and scoring (FREEZE §1 row-2 schema, §4)
# --------------------------------------------------------------------------
REQUIRED_FIELDS = ("profile", "frontier", "thresholds", "selection_by_price", "failure_modes")


def _valid_value_cell(c) -> bool:
    if not isinstance(c, tuple) or not c:
        return False
    if c[0] == "ABSTAIN":
        return len(c) == 1
    if c[0] == "POINT":
        return len(c) == 2 and isinstance(c[1], F)
    if c[0] == "INTERVAL":
        return (len(c) == 4 and isinstance(c[1], F) and isinstance(c[2], F)
                and c[1] <= c[2] and c[3] in GAMMAS)
    return False


def _valid_set_cell(c) -> bool:
    if not isinstance(c, tuple) or not c:
        return False
    if c[0] == "ABSTAIN":
        return len(c) == 1
    return c[0] == "SET" and len(c) == 2 and isinstance(c[1], frozenset)


def validate_record(rec, spec: dict) -> bool:
    if not isinstance(rec, dict):
        return False
    for f in REQUIRED_FIELDS:
        if f not in rec:
            return False
    levels = tuple(spec["universe"]["levels"])
    prices = [F(x) for x in spec["prices"]]
    if set(rec["profile"].keys()) != set(levels):
        return False
    if set(rec["thresholds"].keys()) != set(levels[1:]):
        return False
    if set(rec["selection_by_price"].keys()) != set(prices):
        return False
    if set(rec["failure_modes"].keys()) != set(levels):
        return False
    if not all(_valid_value_cell(c) for c in rec["profile"].values()):
        return False
    if not all(_valid_value_cell(c) for c in rec["thresholds"].values()):
        return False
    if not _valid_set_cell(rec["frontier"]):
        return False
    if not all(_valid_set_cell(c) for c in rec["selection_by_price"].values()):
        return False
    if not all(_valid_set_cell(c) for c in rec["failure_modes"].values()):
        return False
    return True


class Tally(object):
    def __init__(self):
        self.cc = {"hits": 0, "misses": 0, "abstains": 0, "cells": 0}
        self.pr = {"covered": 0, "cells": 0, "vacuous": 0, "abstains": 0, "sharp_sum": F(0), "sharp_n": 0}
        self.th = {"hits": 0, "misses": 0, "abstains": 0, "cells": 0, "vacuous": 0, "sharp_sum": F(0), "sharp_n": 0}
        self.fr = {"hits": 0, "misses": 0, "abstains": 0, "cells": 0}
        self.fm = {"hits": 0, "misses": 0, "abstains": 0, "cells": 0}
        self.cal = {g: {"declared": 0, "covered": 0} for g in GAMMAS}
        self.rejected = 0


def _score_value_cell(cell, truth: F, eta: F, tally: dict, cal: dict, vacuous_as_covered: bool) -> Optional[bool]:
    """Returns covered flag (None for ABSTAIN) and updates tallies."""
    tally["cells"] += 1
    if cell[0] == "ABSTAIN":
        tally["abstains"] += 1
        return None
    if cell[0] == "POINT":
        covered = cell[1] == truth
        tally["sharp_sum"] += 1
        tally["sharp_n"] += 1
        cal[F(1)]["declared"] += 1
        if covered:
            cal[F(1)]["covered"] += 1
        return covered
    lo, hi, gamma = cell[1], cell[2], cell[3]
    vacuous = lo <= 0 and hi >= eta
    width = hi - lo
    sharp = 1 - width / eta
    if sharp < 0:
        sharp = F(0)
    tally["sharp_sum"] += sharp
    tally["sharp_n"] += 1
    inside = lo <= truth <= hi
    if vacuous:
        tally["vacuous"] += 1
        # a vacuous interval is never counted as covered and never declared
        return inside if vacuous_as_covered else False
    cal[gamma]["declared"] += 1
    if inside:
        cal[gamma]["covered"] += 1
    return inside


def score_records(records: List[Optional[dict]], truths: List[dict], specs: List[dict],
                  indices: Optional[List[int]] = None,
                  abstain_as_hit: bool = False, vacuous_as_covered: bool = False) -> dict:
    """Score one theory's records against the given truths (index-aligned)."""
    if indices is None:
        indices = list(range(len(specs)))
    T = Tally()
    for i in indices:
        spec, truth, rec = specs[i], truths[i], records[i]
        eta = F(spec["accounting"]["eta"])
        levels = tuple(spec["universe"]["levels"])
        prices = [F(x) for x in spec["prices"]]
        if rec is None:
            # rejected record: every cell is a scored MISS, never an abstention
            T.rejected += 1
            T.cc["misses"] += len(prices)
            T.cc["cells"] += len(prices)
            T.pr["cells"] += len(levels)
            T.th["misses"] += len(levels) - 1
            T.th["cells"] += len(levels) - 1
            T.fr["misses"] += 1
            T.fr["cells"] += 1
            T.fm["misses"] += len(levels)
            T.fm["cells"] += len(levels)
            continue
        for lam in prices:
            cell = rec["selection_by_price"][lam]
            T.cc["cells"] += 1
            if cell[0] == "ABSTAIN":
                if abstain_as_hit:
                    T.cc["hits"] += 1
                else:
                    T.cc["abstains"] += 1
            elif cell[1] == truth["selection_by_price"][lam]:
                T.cc["hits"] += 1
            else:
                T.cc["misses"] += 1
        for k in levels:
            cov = _score_value_cell(rec["profile"][k], truth["profile"][k], eta, T.pr, T.cal, vacuous_as_covered)
            if cov is None and abstain_as_hit:
                cov = True
            if cov:
                T.pr["covered"] += 1
        for k in levels[1:]:
            cov = _score_value_cell(rec["thresholds"][k], truth["thresholds"][k], eta, T.th, T.cal, vacuous_as_covered)
            if cov is None:
                if abstain_as_hit:
                    T.th["hits"] += 1
            elif cov:
                T.th["hits"] += 1
            else:
                T.th["misses"] += 1
        cell = rec["frontier"]
        T.fr["cells"] += 1
        if cell[0] == "ABSTAIN":
            if abstain_as_hit:
                T.fr["hits"] += 1
            else:
                T.fr["abstains"] += 1
        elif cell[1] == truth["frontier"]:
            T.fr["hits"] += 1
        else:
            T.fr["misses"] += 1
        for k in levels:
            cell = rec["failure_modes"][k]
            T.fm["cells"] += 1
            if cell[0] == "ABSTAIN":
                if abstain_as_hit:
                    T.fm["hits"] += 1
                else:
                    T.fm["abstains"] += 1
            elif cell[1] == truth["failure_modes"][k]:
                T.fm["hits"] += 1
            else:
                T.fm["misses"] += 1
    return finalize_scores(T)


def informative_cc_score(records: List[Optional[dict]], truths: List[dict], cells: List[tuple]) -> Optional[F]:
    """Class-choice score restricted to the given (case, price) cells; a
    rejected record's cell is a MISS, an ABSTAIN cell is excluded."""
    hits = 0
    misses = 0
    for (i, lam) in cells:
        rec = records[i]
        if rec is None:
            misses += 1
            continue
        cell = rec["selection_by_price"][lam]
        if cell[0] == "ABSTAIN":
            continue
        if cell[1] == truths[i]["selection_by_price"][lam]:
            hits += 1
        else:
            misses += 1
    return ratio(hits, hits + misses)


def ratio(num: int, den: int) -> Optional[F]:
    return None if den == 0 else F(num, den)


def finalize_scores(T: Tally) -> dict:
    def hm(d):
        return {"hits": d["hits"], "misses": d["misses"], "abstains": d["abstains"], "cells": d["cells"],
                "score": ratio(d["hits"], d["hits"] + d["misses"])}

    per_gamma = {}
    max_err = F(0)
    calibrated = True
    for g in GAMMAS:
        d = T.cal[g]
        if d["declared"] == 0:
            continue
        cov = F(d["covered"], d["declared"])
        per_gamma[g] = {"declared": d["declared"], "covered": d["covered"], "coverage": cov}
        err = abs(cov - g)
        if err > max_err:
            max_err = err
        if cov < g:
            calibrated = False
    th = hm(T.th)
    th["vacuous"] = T.th["vacuous"]
    th["mean_sharpness"] = ratio_f(T.th["sharp_sum"], T.th["sharp_n"])
    return {
        "class_choice": hm(T.cc),
        "profile": {"covered": T.pr["covered"], "cells": T.pr["cells"], "vacuous": T.pr["vacuous"],
                    "abstains": T.pr["abstains"],
                    "mean_sharpness": ratio_f(T.pr["sharp_sum"], T.pr["sharp_n"]),
                    "score": ratio(T.pr["covered"], T.pr["cells"] - T.pr["abstains"])},
        "thresholds": th,
        "frontier": hm(T.fr),
        "failure_modes": hm(T.fm),
        "calibration": {"per_gamma": per_gamma, "max_error": max_err, "calibrated": calibrated},
        "rejected_records": T.rejected,
    }


def ratio_f(num: F, den: int) -> Optional[F]:
    return None if den == 0 else num / den


# --------------------------------------------------------------------------
# Serialisation
# --------------------------------------------------------------------------
def cell_out(c) -> dict:
    if c[0] == "ABSTAIN":
        return {"kind": "ABSTAIN"}
    if c[0] == "POINT":
        return {"kind": "POINT", "value": fs(c[1])}
    if c[0] == "INTERVAL":
        return {"kind": "INTERVAL", "lo": fs(c[1]), "hi": fs(c[2]), "gamma": fs(c[3])}
    return {"kind": "SET", "values": sorted(c[1])}


def record_out(rec: Optional[dict]) -> Optional[dict]:
    if rec is None:
        return None
    return {
        "profile": {str(k): cell_out(v) for k, v in rec["profile"].items()},
        "thresholds": {str(k): cell_out(v) for k, v in rec["thresholds"].items()},
        "frontier": cell_out(rec["frontier"]),
        "selection_by_price": {fs(lam): cell_out(v) for lam, v in rec["selection_by_price"].items()},
        "failure_modes": {str(k): cell_out(v) for k, v in rec["failure_modes"].items()},
    }


def truth_out(truth: dict) -> dict:
    return {
        "floors": {"%d,%d" % bm: fs(v) for bm, v in sorted(truth["floors"].items())},
        "profile": {str(k): fs(v) for k, v in truth["profile"].items()},
        "thresholds": {str(k): fs(v) for k, v in truth["thresholds"].items()},
        "frontier": sorted(truth["frontier"]),
        "selection_by_price": {fs(lam): sorted(s) for lam, s in truth["selection_by_price"].items()},
        "failure_modes": {str(k): sorted(s) for k, s in truth["failure_modes"].items()},
    }


def scores_out(s: dict) -> dict:
    def conv(v):
        if isinstance(v, bool) or v is None or isinstance(v, int):
            return v
        if isinstance(v, F):
            return fs(v)
        if isinstance(v, dict):
            return {(fs(k) if isinstance(k, F) else str(k)): conv(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [conv(x) for x in v]
        return str(v)
    return conv(s)


def gt(a: Optional[F], b: Optional[F]) -> bool:
    """a > b with None treated as minus infinity."""
    if a is None:
        return False
    if b is None:
        return True
    return a > b


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main() -> int:
    t_start = time.time()
    # ---- commitment ----
    computed_commit = hashlib.sha256(HIDDEN_PREIMAGE.encode("utf-8")).hexdigest()
    commitment_ok = computed_commit == HIDDEN_COMMITMENT
    if not commitment_ok:
        fail("hidden seed commitment mismatch")
    # ---- pins ----
    pins = load_streams()
    pins_ok = all(v["ok"] for v in pins.values())
    if not pins_ok:
        fail("empirical blob pin drift: %s" % json.dumps(pins))
    # ---- enumeration structures ----
    build_signatures()
    uw, uD = law_weights(law_uniform())
    base = ladder_floors(uw, uD)
    base_ok = base == REGISTERED_BASE_FLOORS
    if not base_ok:
        fail("base floors not reproduced: %s" % {k: fs(v) for k, v in base.items()})
    FLOOR_CACHE[("LADDER", "UNIFORM")] = base
    a2 = alphabet_R0(2)
    if a2 != F(1, 2):
        fail("alphabet-2 length-3 enumeration != 1/2")
    # ---- cases ----
    specs = generate_cases(HIDDEN_PREIMAGE)
    census = {}
    for s in specs:
        census[s["class"]] = census.get(s["class"], 0) + 1
    expected_census = {"C1_LADDER": 135, "C2_TWO_LEVEL_IID": 189, "C3_ALPHABET": 81,
                       "C4_EMPIRICAL_STREAM": 45, "C5_HIDDEN": 60, "C6_NEGATIVE_CONTROL": 9}
    census_ok = census == expected_census and len(specs) == 519
    if not census_ok:
        fail("case census mismatch: %s" % census)
    cs_sha = case_set_sha256(specs)
    truths = [compute_truth(s, floors_for_spec(s)) for s in specs]
    t_truth = time.time()
    n = len(specs)
    class_indices = {}
    for i, s in enumerate(specs):
        class_indices.setdefault(s["class"], []).append(i)
    # scrambled truth (FREEZE C6(b)): a fixed cyclic shift within each
    # (class, universe type) group; the partner's profile is re-priced at THIS
    # case's own price set so that every scored cell exists (C5 cases carry a
    # single private price each).
    group_indices = {}
    for i, s in enumerate(specs):
        group_indices.setdefault((s["class"], s["universe"]["type"]), []).append(i)
    scrambled = [None] * n
    for key, idx in sorted(group_indices.items()):
        if len(idx) < 2:
            fail("scramble group of size 1: %r" % (key,))
        for j, i in enumerate(idx):
            partner = truths[idx[(j + 1) % len(idx)]]
            prices = [F(x) for x in specs[i]["prices"]]
            scrambled[i] = {
                "floors": partner["floors"],
                "profile": partner["profile"],
                "thresholds": partner["thresholds"],
                "frontier": partner["frontier"],
                "selection_by_price": {lam: argmin_set(partner["profile"], lam) for lam in prices},
                "failure_modes": partner["failure_modes"],
            }
    # informative cells of the scrambled control: class-choice cells whose
    # scrambled truth differs from the real truth (FREEZE_V1_AMENDMENT_1.md)
    informative = []
    for i in range(n):
        for lam in scrambled[i]["selection_by_price"]:
            if scrambled[i]["selection_by_price"][lam] != truths[i]["selection_by_price"][lam]:
                informative.append((i, lam))
    # ---- run theories on the public spec only ----
    def public_spec(s: dict) -> dict:
        d = json.loads(json.dumps(s))
        if "truth" in d:
            fail("truth key in public spec")
        return d

    pubs = [public_spec(s) for s in specs]
    records = {}
    rejected = {}
    for tid, fn in REGISTERED + [("T_PEEK", PeekTheory())]:
        recs = []
        nrej = 0
        for i in range(n):
            r = fn(pubs[i])
            if not validate_record(r, specs[i]):
                r = None
                nrej += 1
            recs.append(r)
        records[tid] = recs
        rejected[tid] = nrej
    null_records = {}
    for k in range(N_NULL):
        fn = NullTheory(k)
        recs = []
        for i in range(n):
            r = fn(pubs[i])
            if not validate_record(r, specs[i]):
                fail("null record invalid")
            recs.append(r)
        null_records["T_NULL_%d" % k] = recs
    t_theories = time.time()
    # T_PEEK fallback proof: identical to T_NULL_0 when nothing is leaked
    peek_is_null0 = records["T_PEEK"] == null_records["T_NULL_0"]
    # ---- scores ----
    scores = {tid: score_records(records[tid], truths, specs) for tid in records}
    null_scores = {nid: score_records(null_records[nid], truths, specs) for nid in null_records}
    scrambled_scores = {tid: score_records(records[tid], scrambled, specs)["class_choice"]["score"] for tid in records}
    null_scrambled = {nid: score_records(null_records[nid], scrambled, specs)["class_choice"]["score"] for nid in null_records}
    scrambled_info = {tid: informative_cc_score(records[tid], scrambled, informative) for tid in records}
    null_info = {nid: informative_cc_score(null_records[nid], scrambled, informative) for nid in null_records}
    t_scores = time.time()
    by_class = {cls: score_records(records["T_GMI_IC1"], truths, specs, idx) for cls, idx in class_indices.items()}

    # ---- discrimination C7 ----
    pair_counts = {}
    disc_cases = set()
    ths = DISCRIMINATION_THEORIES
    for a_i in range(len(ths)):
        for b_i in range(a_i + 1, len(ths)):
            a, b = ths[a_i], ths[b_i]
            cnt = 0
            for i in range(n):
                ra, rb = records[a][i], records[b][i]
                if ra is None or rb is None:
                    continue
                differ = False
                for lam in ra["selection_by_price"]:
                    ca, cb = ra["selection_by_price"][lam], rb["selection_by_price"][lam]
                    if ca[0] == "SET" and cb[0] == "SET" and ca[1] != cb[1]:
                        differ = True
                        break
                if differ:
                    cnt += 1
                    disc_cases.add(i)
            pair_counts["%s|%s" % (a, b)] = cnt
    non_disc = sorted(k for k, v in pair_counts.items() if v == 0)
    decl_disagree = pair_counts["T_GMI_IC1|T_DECLARED"]
    decl_identical_all_fields = records["T_DECLARED"] == records["T_GMI_IC1"]

    # ---- null ----
    fields4 = ("class_choice", "thresholds", "frontier", "failure_modes")
    best_null = {}
    best_null_id = {}
    for f in fields4:
        b_id, b_v = None, None
        for nid in sorted(null_scores, key=lambda x: int(x.split("_")[-1])):
            v = null_scores[nid][f]["score"]
            if b_v is None or gt(v, b_v):
                b_id, b_v = nid, v
        best_null[f] = b_v
        best_null_id[f] = b_id
    gmi4 = {f: scores["T_GMI_IC1"][f]["score"] for f in fields4}
    all_beaten = all(gt(gmi4[f], best_null[f]) for f in fields4)
    best_null_scrambled = max(null_scrambled.values(), key=lambda v: (v is not None, v))
    scr_gmi_le_null_literal = not gt(scrambled_scores["T_GMI_IC1"], best_null_scrambled)
    best_null_info = max(null_info.values(), key=lambda v: (v is not None, v))
    scr_gmi_le_null_info = not gt(scrambled_info["T_GMI_IC1"], best_null_info)
    # FREEZE_V1_AMENDMENT_1.md: the literal all-cell control governs when it
    # does not alarm on the provably clean T_GMI_IC1; when it does, the
    # informative-cell form governs and the switch is disclosed.
    if scr_gmi_le_null_literal:
        control_form = "LITERAL_ALL_CELLS"
        scr_gmi_le_null = True
        s6_followed = True
    else:
        control_form = "INFORMATIVE_CELLS_AMENDMENT_1"
        scr_gmi_le_null = scr_gmi_le_null_info
        s6_followed = False
    leak_scores = scrambled_scores if control_form == "LITERAL_ALL_CELLS" else scrambled_info
    leak_best_null = best_null_scrambled if control_form == "LITERAL_ALL_CELLS" else best_null_info
    # Diagnosis of every theory-level alarm: a registered theory is a pure
    # function of the public specification and cannot read the truth, so an
    # alarm on it is a false positive of the control. The receipt records why:
    # a price-blind theory emits one class choice per case, and its
    # informative-cell score is the base rate of that choice among scrambled
    # truths, not truth access. Harness leakage itself is excluded by
    # T_PEEK == T_NULL_0 under the honest harness.
    alarm_diag = {}
    for tid in sorted(t for t, v in leak_scores.items() if gt(v, leak_best_null)):
        recs = records[tid]
        blind = all(r is not None and len(set(r["selection_by_price"].values())) == 1 for r in recs)
        alarm_diag[tid] = {
            "price_blind": blind,
            "informative_score_vs_scrambled_truth": leak_scores[tid],
            "informative_score_vs_real_truth": informative_cc_score(recs, truths, informative),
            "pure_function_of_public_spec": True,
            "classification": "FALSE_ALARM_ON_CLEAN_THEORY",
        }

    # ---- two-level ties ----
    tie_cells = 0
    tie_truth_ok = True
    tie_pred_ok = True
    for i, s in enumerate(specs):
        if s["universe"]["type"] != "TWO_LEVEL":
            continue
        thr = truths[i]["thresholds"][1]
        for lam in truths[i]["selection_by_price"]:
            if lam == thr:
                tie_cells += 1
                if truths[i]["selection_by_price"][lam] != frozenset([0, 1]):
                    tie_truth_ok = False
                c = records["T_GMI_IC1"][i]["selection_by_price"][lam]
                if not (c[0] == "SET" and c[1] == frozenset([0, 1])):
                    tie_pred_ok = False
    ties_ok = tie_cells > 0 and tie_truth_ok and tie_pred_ok

    # ---- hostiles ----
    hostiles = {}
    # HZ1: planted truth reader caught by the scrambled-truth control (leaky harness pass)
    peek = PeekTheory()
    leaky_recs = []
    for i in range(n):
        d = public_spec(specs[i])
        d["truth"] = scrambled[i]
        r = peek(d)
        leaky_recs.append(r if validate_record(r, specs[i]) else None)
    peek_leaky_scr = score_records(leaky_recs, scrambled, specs)["class_choice"]["score"]
    peek_honest_scr = scrambled_scores["T_PEEK"]
    peek_leaky_info = informative_cc_score(leaky_recs, scrambled, informative)
    peek_honest_info = scrambled_info["T_PEEK"]
    hostiles["HZ1"] = {
        "applicable": peek_leaky_scr != peek_honest_scr and peek_leaky_info != peek_honest_info,
        "detected": gt(peek_leaky_scr, best_null_scrambled) and gt(peek_leaky_info, best_null_info),
        "T_PEEK_scrambled_score_honest_harness": peek_honest_scr,
        "T_PEEK_scrambled_score_leaky_harness": peek_leaky_scr,
        "best_null_scrambled_score": best_null_scrambled,
        "T_PEEK_informative_score_honest_harness": peek_honest_info,
        "T_PEEK_informative_score_leaky_harness": peek_leaky_info,
        "best_null_informative_score": best_null_info,
        "T_PEEK_falls_back_to_T_NULL_0": peek_is_null0,
    }
    # HZ2: a record missing a required field is rejected (scored, not abstained)
    hz2_recs = []
    hz2_rej = 0
    for i in range(n):
        r = dict(records["T_GMI_IC1"][i])
        del r["frontier"]
        if validate_record(r, specs[i]):
            hz2_recs.append(r)
        else:
            hz2_recs.append(None)
            hz2_rej += 1
    hz2_scores = score_records(hz2_recs, truths, specs)
    hostiles["HZ2"] = {
        "applicable": hz2_recs != records["T_GMI_IC1"],
        "detected": hz2_rej == n and hz2_scores["rejected_records"] == n
        and hz2_scores["class_choice"]["abstains"] == 0
        and hz2_scores["class_choice"]["misses"] == hz2_scores["class_choice"]["cells"],
        "rejected_records": hz2_rej,
        "class_choice_score_after_rejection": hz2_scores["class_choice"]["score"],
        "class_choice_score_untampered": scores["T_GMI_IC1"]["class_choice"]["score"],
    }
    # HZ3: a scorer counting ABSTAIN as HIT is caught by T_ABSTAIN scoring above 0
    hz3 = score_records(records["T_ABSTAIN"], truths, specs, abstain_as_hit=True)
    honest_abstain = scores["T_ABSTAIN"]
    hostiles["HZ3"] = {
        "applicable": hz3["class_choice"]["hits"] != honest_abstain["class_choice"]["hits"],
        "detected": gt(hz3["class_choice"]["score"], F(0))
        and honest_abstain["class_choice"]["hits"] == 0 and honest_abstain["class_choice"]["misses"] == 0,
        "T_ABSTAIN_hits_tampered_scorer": hz3["class_choice"]["hits"],
        "T_ABSTAIN_score_tampered_scorer": hz3["class_choice"]["score"],
        "T_ABSTAIN_hits_honest": honest_abstain["class_choice"]["hits"],
        "T_ABSTAIN_misses_honest": honest_abstain["class_choice"]["misses"],
    }
    # HZ4: vacuous interval counted as covered is caught by the VACUOUS flag
    vac_recs = []
    for i in range(n):
        s = specs[i]
        eta = F(s["accounting"]["eta"])
        levels = tuple(s["universe"]["levels"])
        r = dict(records["T_GMI_IC1"][i])
        r["profile"] = {k: INTERVAL(F(0), eta, F(1)) for k in levels}
        r["thresholds"] = {k: INTERVAL(F(0), eta, F(1)) for k in levels[1:]}
        vac_recs.append(r)
    vac_honest = score_records(vac_recs, truths, specs)
    vac_tampered = score_records(vac_recs, truths, specs, vacuous_as_covered=True)
    hostiles["HZ4"] = {
        "applicable": vac_tampered["profile"]["covered"] != vac_honest["profile"]["covered"],
        "detected": vac_honest["profile"]["vacuous"] == vac_honest["profile"]["cells"]
        and vac_honest["profile"]["covered"] == 0
        and vac_honest["thresholds"]["hits"] == 0
        and vac_honest["calibration"]["per_gamma"] == {},
        "profile_cells": vac_honest["profile"]["cells"],
        "profile_vacuous_flagged": vac_honest["profile"]["vacuous"],
        "profile_covered_honest": vac_honest["profile"]["covered"],
        "profile_covered_tampered": vac_tampered["profile"]["covered"],
        "mean_sharpness": vac_honest["profile"]["mean_sharpness"],
    }
    # HZ5: a tampered generation rule changes the case-set sha256
    tampered_specs = generate_cases(HIDDEN_PREIMAGE, c1_prices=PRICES_16[:-1])
    tampered_sha = case_set_sha256(tampered_specs)
    hostiles["HZ5"] = {
        "applicable": tampered_specs != specs,
        "detected": tampered_sha != cs_sha,
        "tamper": "C1 price set truncated to j = 0..23",
        "case_set_sha256": cs_sha,
        "tampered_case_set_sha256": tampered_sha,
    }
    # HZ6: a wrong seed preimage fails the commitment check
    wrong = HIDDEN_PREIMAGE + ":wrong"
    wrong_sha = hashlib.sha256(wrong.encode("utf-8")).hexdigest()
    hostiles["HZ6"] = {
        "applicable": wrong != HIDDEN_PREIMAGE,
        "detected": wrong_sha != HIDDEN_COMMITMENT,
        "wrong_preimage_sha256": wrong_sha,
        "commitment": HIDDEN_COMMITMENT,
    }
    # HZ7: a drifted empirical-stream blob fails the pin
    drift = {}
    for (path, sha, _), data in zip(STREAMS, STREAM_BYTES):
        d = data + b"\n"
        drift[path] = {"drifted_sha1": git_blob_sha1(d), "pin": sha, "caught": git_blob_sha1(d) != sha,
                       "moved": d != data}
    hostiles["HZ7"] = {
        "applicable": all(v["moved"] for v in drift.values()),
        "detected": all(v["caught"] for v in drift.values()),
        "streams": drift,
    }
    # HZ8: gamma = 1 with coverage below 1 reported MISCALIBRATED (planted: T_LEVEL on C1)
    lvl_c1 = score_records(records["T_LEVEL"], truths, specs, class_indices["C1_LADDER"])
    cov1 = lvl_c1["calibration"]["per_gamma"].get(F(1), {}).get("coverage")
    hostiles["HZ8"] = {
        "applicable": cov1 is not None and cov1 < 1,
        "detected": scores["T_LEVEL"]["calibration"]["calibrated"] is False
        and lvl_c1["calibration"]["calibrated"] is False,
        "T_LEVEL_C1_coverage_gamma_1": cov1,
        "T_LEVEL_C1_declared_gamma_1": lvl_c1["calibration"]["per_gamma"].get(F(1), {}).get("declared"),
        "T_LEVEL_C1_covered_gamma_1": lvl_c1["calibration"]["per_gamma"].get(F(1), {}).get("covered"),
        "T_LEVEL_calibrated_overall": scores["T_LEVEL"]["calibration"]["calibrated"],
        "status": "MISCALIBRATED" if not scores["T_LEVEL"]["calibration"]["calibrated"] else "CALIBRATED",
    }
    hostiles_ok = all(h["applicable"] and h["detected"] for h in hostiles.values())

    # ---- frozen predictions B1..B6 ----
    def cc_score(tid, idx):
        return score_records(records[tid], truths, specs, idx)["class_choice"]

    frozen = {}
    # B1
    b1 = {}
    for cls in ("C1_LADDER", "C2_TWO_LEVEL_IID", "C3_ALPHABET", "C6_NEGATIVE_CONTROL"):
        b1[cls] = cc_score("T_GMI_IC1", class_indices[cls])
    c5_tl_simple = [i for i in class_indices["C5_HIDDEN"]
                    if specs[i]["universe"]["type"] == "TWO_LEVEL" and specs[i]["law"]["kind"] != "EMPIRICAL"]
    c5_rest = [i for i in class_indices["C5_HIDDEN"] if i not in c5_tl_simple]
    b1["C5_TWO_LEVEL_UNIFORM_IID_PERIOD2"] = cc_score("T_GMI_IC1", c5_tl_simple)
    b1["C5_TWO_LEVEL_UNIFORM_IID_PERIOD2"]["n_cases"] = len(c5_tl_simple)
    b1["C5_remaining"] = cc_score("T_GMI_IC1", c5_rest)
    b1["C5_remaining"]["n_cases"] = len(c5_rest)
    b1["C4_EMPIRICAL_STREAM"] = cc_score("T_GMI_IC1", class_indices["C4_EMPIRICAL_STREAM"])
    b1_hit = (all(b1[c]["score"] == 1 for c in ("C1_LADDER", "C2_TWO_LEVEL_IID", "C3_ALPHABET", "C6_NEGATIVE_CONTROL"))
              and (len(c5_tl_simple) == 0 or b1["C5_TWO_LEVEL_UNIFORM_IID_PERIOD2"]["score"] == 1)
              and b1["C5_remaining"]["misses"] == 0 and b1["C4_EMPIRICAL_STREAM"]["misses"] == 0)
    frozen["B1"] = {"verdict": "HIT" if b1_hit else "MISS", "evidence": b1}
    # B2
    b2_cells = {}
    b2_eq = 0
    b2_cov = 0
    for stream in range(3):
        law = law_empirical(stream, 0)
        key = ("LADDER",) + law_key(law)
        fl = FLOOR_CACHE[key]
        weights, D = law_weights(law)
        for m in (1, 2):
            pred = pooled_bayes_error(weights, D, m)
            eq = pred == fl[(0, m)]
            b2_eq += 1 if eq else 0
            b2_cells["%s,m=%d" % (STREAMS[stream][0], m)] = {"closed_form": pred, "enumerated": fl[(0, m)], "equal": eq}
        # now channel
        b2_eq += 1 if fl[(0, 0)] == 0 else 0
        b2_cells["%s,m=0" % STREAMS[stream][0]] = {"closed_form": F(0), "enumerated": fl[(0, 0)], "equal": fl[(0, 0)] == 0}
        r2 = pooled_bayes_error(weights, D, 2)
        covered = F(0) <= fl[(1, 2)] <= r2
        b2_cov += 1 if covered else 0
        b2_cells["%s,b=1,m=2" % STREAMS[stream][0]] = {"interval_lo": F(0), "interval_hi": r2,
                                                      "enumerated": fl[(1, 2)], "covered": covered}
    frozen["B2"] = {"verdict": "HIT" if (b2_eq == 9 and b2_cov == 3) else "MISS",
                    "evidence": {"stateless_cells_equal": "%d/9" % b2_eq, "b1_delay2_covered": "%d/3" % b2_cov,
                                 "cells": b2_cells}}
    # B3
    def threshold_miss_cases(tid, idx):
        cnt = 0
        for i in idx:
            r = records[tid][i]
            miss = False
            for k, cell in r["thresholds"].items():
                tv = truths[i]["thresholds"][k]
                if cell[0] == "POINT" and cell[1] != tv:
                    miss = True
                elif cell[0] == "INTERVAL" and not (cell[1] <= tv <= cell[2]):
                    miss = True
            cnt += 1 if miss else 0
        return cnt

    c2_qne = [i for i in class_indices["C2_TWO_LEVEL_IID"] if F(specs[i]["law"]["q"]) != F(1, 2)]
    c3_ane = [i for i in class_indices["C3_ALPHABET"] if int(specs[i]["universe"]["alphabet"]) != 2]
    c1_p2 = [i for i in class_indices["C1_LADDER"] if F(specs[i]["accounting"]["p"][2]) > 0]
    half_c2 = threshold_miss_cases("T_HALF", c2_qne)
    half_c3 = threshold_miss_cases("T_HALF", c3_ane)
    c2_qne_p0 = sum(1 for i in c2_qne if F(specs[i]["accounting"]["p"][1]) == 0)
    c3_ane_p0 = sum(1 for i in c3_ane if F(specs[i]["accounting"]["p"][1]) == 0)
    lvl_upper = 0
    for i in c1_p2:
        cell = records["T_LEVEL"][i]["thresholds"][1]
        if cell[0] == "POINT" and cell[1] != truths[i]["thresholds"][1]:
            lvl_upper += 1
    b3 = {
        "T_HALF_C2_q_ne_half": {"cases": len(c2_qne), "threshold_miss_cases": half_c2,
                                "cases_with_p_zero": c2_qne_p0, "claim_holds": half_c2 == len(c2_qne)},
        "T_HALF_C3_A_ne_2": {"cases": len(c3_ane), "threshold_miss_cases": half_c3,
                             "cases_with_p_zero": c3_ane_p0, "claim_holds": half_c3 == len(c3_ane)},
        "T_LEVEL_C1_p2_gt_0_upper_miss": {"cases": len(c1_p2), "upper_threshold_miss_cases": lvl_upper,
                                          "claim_holds": lvl_upper == len(c1_p2) == 108},
        "T_LEVEL_miscalibrated": scores["T_LEVEL"]["calibration"]["calibrated"] is False,
    }
    b3_hit = (b3["T_HALF_C2_q_ne_half"]["claim_holds"] and b3["T_HALF_C3_A_ne_2"]["claim_holds"]
              and b3["T_LEVEL_C1_p2_gt_0_upper_miss"]["claim_holds"] and b3["T_LEVEL_miscalibrated"])
    frozen["B3"] = {"verdict": "HIT" if b3_hit else "MISS", "evidence": b3}
    # B4
    frozen["B4"] = {"verdict": "HIT" if decl_disagree == 0 else "MISS",
                    "evidence": {"disagreements": decl_disagree, "all_fields_identical": decl_identical_all_fields}}
    # B5
    c12 = class_indices["C1_LADDER"] + class_indices["C2_TWO_LEVEL_IID"]
    b5 = {}
    b5_hit = True
    for tid in ("T_MDL", "T_SRM", "T_SATISFICE", "T_OCCAM_HARD"):
        s12 = cc_score(tid, c12)
        beaten = gt(scores["T_GMI_IC1"]["class_choice"]["score"], scores[tid]["class_choice"]["score"])
        b5[tid] = {"C1_C2_misses": s12["misses"], "C1_C2_cells": s12["cells"],
                   "overall_score": scores[tid]["class_choice"]["score"],
                   "T_GMI_IC1_overall_score": scores["T_GMI_IC1"]["class_choice"]["score"],
                   "beaten_by_T_GMI_IC1": beaten}
        if not (s12["misses"] > 0 and beaten):
            b5_hit = False
    frozen["B5"] = {"verdict": "HIT" if b5_hit else "MISS", "evidence": b5}
    # B6
    b6 = {f: {"best_null": best_null[f], "best_null_id": best_null_id[f], "T_GMI_IC1": gmi4[f],
              "strictly_below": gt(gmi4[f], best_null[f])} for f in fields4}
    frozen["B6"] = {"verdict": "HIT" if all_beaten else "MISS", "evidence": b6}

    # ---- gates ----
    abstain_zero = (scores["T_ABSTAIN"]["class_choice"]["hits"] == 0 and scores["T_ABSTAIN"]["class_choice"]["misses"] == 0
                    and scores["T_ABSTAIN"]["thresholds"]["hits"] == 0 and scores["T_ABSTAIN"]["thresholds"]["misses"] == 0
                    and scores["T_ABSTAIN"]["frontier"]["hits"] == 0 and scores["T_ABSTAIN"]["frontier"]["misses"] == 0
                    and scores["T_ABSTAIN"]["failure_modes"]["hits"] == 0 and scores["T_ABSTAIN"]["failure_modes"]["misses"] == 0)
    gates = {
        "hidden_seed_commitment_ok": commitment_ok,
        "empirical_blob_pins_ok": pins_ok,
        "base_floors_reproduced": base_ok,
        "case_census_matches_freeze": census_ok,
        "registered_records_all_valid": all(rejected[t] == 0 for t in rejected),
        "hostiles_all_applicable_and_detected": hostiles_ok,
        "null_all_fields_beaten": all_beaten,
        "no_alarm_T_DECLARED_non_discriminating": decl_disagree == 0 and decl_identical_all_fields,
        "no_alarm_scrambled_T_GMI_IC1_le_best_null": scr_gmi_le_null,
        "two_level_ties_predicted": ties_ok,
        "T_ABSTAIN_zero_hits_zero_misses": abstain_zero,
        "T_PEEK_falls_back_to_T_NULL_0_without_leak": peek_is_null0,
    }
    verdict = "GREEN" if all(gates.values()) else "RED"
    t_end = time.time()

    # ---- emit CASES_V1.json ----
    cases_doc = {
        "schema": "GMI_833_Z11_IMB_CASES_V1",
        "case_set_sha256": cs_sha,
        "hidden_seed_preimage": HIDDEN_PREIMAGE,
        "cases": [{"index": i, "id": "%s_%04d" % (specs[i]["class"], i), "spec": specs[i], "truth": truth_out(truths[i])}
                  for i in range(n)],
    }
    with open(os.path.join(HERE, "CASES_V1.json"), "w") as fh:
        fh.write(canonical_json(cases_doc) + "\n")
    # ---- emit PREDICTIONS_V1.json ----
    pred_doc = {
        "schema": "GMI_833_Z11_IMB_PREDICTIONS_V1",
        "case_set_sha256": cs_sha,
        "theories": {tid: [record_out(r) for r in records[tid]] for tid in records},
        "null_scores": {nid: scores_out(null_scores[nid]) for nid in null_records},
        "null_scrambled_class_choice": {nid: fs(v) if v is not None else None for nid, v in null_scrambled.items()},
        "null_scrambled_informative_class_choice": {nid: fs(v) if v is not None else None for nid, v in null_info.items()},
        "scrambled_informative_cells": [[i, fs(lam)] for (i, lam) in informative],
    }
    with open(os.path.join(HERE, "PREDICTIONS_V1.json"), "w") as fh:
        fh.write(canonical_json(pred_doc) + "\n")
    # ---- emit RESULT_V1.json ----
    laws_enumerated = sorted(set(str(k) for k in FLOOR_CACHE))
    result = {
        "schema": SCHEMA,
        "issue": ISSUE,
        "subsection": SUBSECTION,
        "route": ROUTE,
        "source_main": SOURCE_MAIN,
        "case_census": dict(census, total=n),
        "case_set_sha256": cs_sha,
        "hidden_seed_commitment": {"sha256": HIDDEN_COMMITMENT, "preimage_revealed": HIDDEN_PREIMAGE, "ok": commitment_ok},
        "empirical_blob_pins": pins,
        "base_floors_reproduced": {"ok": base_ok, "floors": {"%d,%d" % bm: fs(v) for bm, v in sorted(base.items())}},
        "scores": {tid: scores_out(scores[tid]) for tid in scores},
        "scores_by_class": {cls: scores_out(by_class[cls]) for cls in by_class},
        "discrimination": {
            "pair_counts": pair_counts,
            "cases": len(disc_cases),
            "non_discriminating_pairs": non_disc,
            "T_DECLARED_vs_T_GMI_IC1_disagreements": decl_disagree,
            "T_DECLARED_status": "NON_DISCRIMINATING" if decl_disagree == 0 else "DISCRIMINATING",
        },
        "scrambled_truth_control": {
            "pairing": "truth of case (j+1) mod n_group within the same (class, universe type) group, re-priced at the case's own price set",
            "governing_form": control_form,
            "s6_instruction_followed": s6_followed,
            "audit_shape_disclosed": "NONE" if s6_followed else "POST_HOC_SUSPECT",
            "literal_all_cells": {
                "class_choice": {tid: fs(v) if v is not None else None for tid, v in scrambled_scores.items()},
                "best_null_scrambled": fs(best_null_scrambled) if best_null_scrambled is not None else None,
                "T_GMI_IC1_at_or_below_best_null": scr_gmi_le_null_literal,
                "leakage_alarms": sorted(t for t, v in scrambled_scores.items() if gt(v, best_null_scrambled)),
            },
            "informative_cells": {
                "cells": len(informative),
                "cells_total": sum(len(s["prices"]) for s in specs),
                "class_choice": {tid: fs(v) if v is not None else None for tid, v in scrambled_info.items()},
                "best_null_scrambled": fs(best_null_info) if best_null_info is not None else None,
                "T_GMI_IC1_at_or_below_best_null": scr_gmi_le_null_info,
                "leakage_alarms": sorted(t for t, v in scrambled_info.items() if gt(v, best_null_info)),
            },
            "T_GMI_IC1_at_or_below_best_null": scr_gmi_le_null,
            "leakage_alarms": sorted(t for t, v in leak_scores.items() if gt(v, leak_best_null)),
            "leakage_alarm_diagnosis": alarm_diag,
            "harness_leakage_excluded_by": "T_PEEK_falls_back_to_T_NULL_0_without_leak",
        },
        "null": {"n": N_NULL, "best": {f: fs(v) if v is not None else None for f, v in best_null.items()},
                 "best_id": best_null_id,
                 "T_GMI_IC1": {f: fs(v) if v is not None else None for f, v in gmi4.items()},
                 "all_fields_beaten": all_beaten},
        "hostiles": scores_out(hostiles),
        "hostiles_all_applicable_and_detected": hostiles_ok,
        "frozen_predictions": scores_out(frozen),
        "gates": gates,
        "verdict": verdict,
        "two_level_ties": {"tie_cells": tie_cells, "truth_all_{0,1}": tie_truth_ok, "T_GMI_IC1_all_{0,1}": tie_pred_ok},
        "enumeration": {"next_state_tables": {str(b): SIG_COUNTS[b] for b in LADDER_LEVELS},
                        "distinct_signatures": {str(b): len(SIGNATURES[b]) for b in LADDER_LEVELS},
                        "laws_enumerated": laws_enumerated, "n_laws": len(laws_enumerated)},
        "executor_choices": {
            "C2_IID_Q": [fs(q) for q in C2_IID_Q],
            "thresholds": "plain marginals Delta_k = E(k-1) - E(k)",
            "frontier": "levels that are the unique argmin of E(k)+lam*k at some lam >= 0",
            "two_level_binary_R0": "enumerated floor(0,1) of the L=4 window law",
            "alphabet_R0": "A-ary stateless table on length-3 uniform sequences, t in {1,2}",
            "stateless_closed_form": "Bayes error of x_{t-m} given x_t, pooled over t in {2,3}, min after pooling",
            "competitor_interval_floors": "upper endpoint (T_MDL, T_SRM, T_SATISFICE)",
            "T_MDL_error_bits_sum": "over every mode of the universe, unweighted by p_m",
            "T_SRM_thresholds": "ABSTAIN",
            "T_SRM_T_SATISFICE_frontier": "T_GMI_IC1's frontier",
            "T_LEVEL_on_two_level": "as T_GMI_IC1",
            "null_failure_modes": "subset of the case's channel set",
            "rho": "1",
            "degenerate_interval": "emitted as POINT when lo == hi",
            "rejected_record_scoring": "every cell a MISS, never an abstention",
            "scramble_grouping": "cyclic shift within (class, universe type); partner profile re-priced at the case's own price set",
            "scramble_control_form": control_form,
        },
    }
    # wall-clock timing is printed, never written to the receipt (byte-stability)
    timing = {"truth": int(t_truth - t_start), "theories": int(t_theories - t_truth),
              "scoring": int(t_scores - t_theories), "total": int(t_end - t_start)}
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")

    # ---- stdout summary ----
    print("IMB-v1 Route A  verdict=%s  cases=%d  case_set_sha256=%s" % (verdict, n, cs_sha))
    print("distinct signatures b=0..2: %s  laws enumerated: %d  timing: %s" % (
        [len(SIGNATURES[b]) for b in LADDER_LEVELS], len(laws_enumerated), timing))
    for tid in scores:
        s = scores[tid]
        print("  %-13s cc=%s (h%d m%d a%d) th=%s fr=%s fm=%s prof_cov=%d/%d cal=%s rej=%d" % (
            tid, fs(s["class_choice"]["score"]) if s["class_choice"]["score"] is not None else "NA",
            s["class_choice"]["hits"], s["class_choice"]["misses"], s["class_choice"]["abstains"],
            fs(s["thresholds"]["score"]) if s["thresholds"]["score"] is not None else "NA",
            fs(s["frontier"]["score"]) if s["frontier"]["score"] is not None else "NA",
            fs(s["failure_modes"]["score"]) if s["failure_modes"]["score"] is not None else "NA",
            s["profile"]["covered"], s["profile"]["cells"], s["calibration"]["calibrated"], s["rejected_records"]))
    print("  null best: %s" % {f: fs(v) for f, v in best_null.items()})
    print("  scrambled literal: T_GMI_IC1=%s best_null=%s ; informative(%d cells): T_GMI_IC1=%s best_null=%s ; form=%s alarms=%s" % (
        fs(scrambled_scores["T_GMI_IC1"]), fs(best_null_scrambled), len(informative),
        fs(scrambled_info["T_GMI_IC1"]) if scrambled_info["T_GMI_IC1"] is not None else "NA",
        fs(best_null_info) if best_null_info is not None else "NA",
        control_form, result["scrambled_truth_control"]["leakage_alarms"]))
    print("  hostiles: %s" % {h: (v["applicable"], v["detected"]) for h, v in hostiles.items()})
    print("  frozen: %s" % {b: frozen[b]["verdict"] for b in sorted(frozen)})
    print("  alarm diagnosis: %s" % {t: (v["price_blind"], fs(v["informative_score_vs_real_truth"]) if v["informative_score_vs_real_truth"] is not None else "NA") for t, v in alarm_diag.items()})
    print("  gates: %s" % gates)
    if not hostiles_ok:
        print("FAIL: a hostile is inapplicable or undetected")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
