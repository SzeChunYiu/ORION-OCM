#!/usr/bin/env python3
"""IMB-v1 Route B -- materially independent oracle (GMI #833 Section Z / Z11).

Written from FREEZE_V1.md and FREEZE_V1_AMENDMENT_1.md alone; imports nothing
from Route A (imb_benchmark_v1.py).  Where Route A enumerates next-state
tables by address signature with per-address majority outputs and scores with
a tally object, this file

  * rebuilds every case from the generation rules of FREEZE section 2 with its
    own spec builder and its own composition/stream/law code, reveals the
    hidden seed from CASES_V1.json and checks it against the sha256 commitment,
  * recomputes every hidden truth by FULL enumeration of explicit
    (output table, next-state table) machines at b <= 1 (probability-weighted
    simulation, exact Fractions), and proves every b = 2 floor by a constructive
    shift-register witness that attains 0 (a floor is >= 0, so 0 is exact),
  * derives the resource frontier from half-line feasibility of the strict
    argmin condition instead of sampling prices,
  * re-reads PREDICTIONS_V1.json and re-scores every registered theory with its
    own scorer written from FREEZE section 4, recomputes the scrambled-truth
    control (literal and informative-cell forms), and draws its OWN null family
    of 200 theories from an independent seed stream.

Agreement with Route A is by exact equality of every score of every registered
theory, every truth field of every case, and the case-set sha256.

Run from the repository root:
    python3 -I -B research/gmi-833-z-z11-morphology-benchmark-v1/independent_imb_oracle_v1.py

Stdlib only; fractions.Fraction / int; Python 3.8 compatible.
"""
import hashlib
import io
import json
import os
import random
import sys
from fractions import Fraction as F
from itertools import product
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

COMMITMENT = "b7adc75b3ec9b7f3c4fd9f7a9130198a21f01a341d4167bf7ef9abf4a0c9271f"
STREAMS = [
    ("README.md", "d7519609d064a4c478696ec6378f23c771a3db20", 8110),
    ("LICENSE", "d645695673349e3947e8e5ae42332d0ac3164cd7", 11358),
    ("research/gmi-833-z-z12-prediction-scoring-v1/z12_prediction_scoring_v1.py",
     "2825c19583aa7ca0dc3f9f475553fd9ea419ed3c", 23113),
]
GAMMAS = (F(1), F(3, 4), F(1, 2))
PRICES = [F(j, 16) for j in range(25)]
N_NULL = 200
NULL_SEED_BASE = 500000  # disjoint from Route A's 1000 + k


def fs(x) -> str:
    return str(F(x))


def die(msg: str) -> None:
    print("ORACLE FAIL: " + msg)
    sys.exit(2)


# ---------------------------------------------------------------- streams
STREAM_BITS = []  # type: List[List[int]]


def blob_sha1(data: bytes) -> str:
    return hashlib.sha1(("blob %d\0" % len(data)).encode("ascii") + data).hexdigest()


def load_streams() -> bool:
    ok = True
    for path, sha, nbytes in STREAMS:
        with io.open(os.path.join(REPO, path), "rb") as fh:
            data = fh.read()
        if blob_sha1(data) != sha or len(data) != nbytes:
            ok = False
        bits = []
        for byte in data:
            for k in range(8):
                bits.append((byte >> (7 - k)) & 1)
        STREAM_BITS.append(bits)
    return ok


# ---------------------------------------------------------------- laws as probability maps over 4-bit words
SEQS = list(product((0, 1), repeat=4))


def law_probs(law: dict) -> Dict[tuple, F]:
    kind = law["kind"]
    if kind == "UNIFORM":
        return dict((w, F(1, 16)) for w in SEQS)
    if kind == "IID":
        q = F(law["q"])
        out = {}
        for w in SEQS:
            pr = F(1)
            for x in w:
                pr *= q if x == 1 else (1 - q)
            out[w] = pr
        return out
    if kind == "PERIOD2":
        return dict((w, F(1, 4) if (w[2] == w[0] and w[3] == w[1]) else F(0)) for w in SEQS)
    if kind == "EMPIRICAL":
        bits = STREAM_BITS[int(law["stream"])]
        off = int(law["offset"])
        counts = dict((w, 0) for w in SEQS)
        n = 0
        for i in range(off, len(bits) - 3):
            counts[(bits[i], bits[i + 1], bits[i + 2], bits[i + 3])] += 1
            n += 1
        return dict((w, F(c, n)) for w, c in counts.items())
    die("unknown law %r" % kind)
    return {}


# ---------------------------------------------------------------- explicit machines
def machine_error(prob: Dict[tuple, F], nstates: int, nxt: tuple, out: tuple, m: int) -> F:
    """Error rate of an explicit Mealy machine (start state 0) on target
    x_{t-m}, scored at t in {2, 3}, weight 1/2 each."""
    err = F(0)
    for w, pr in prob.items():
        if pr == 0:
            continue
        s = 0
        e = 0
        for t in range(4):
            a = s * 2 + w[t]
            if t >= 2 and out[a] != w[t - m]:
                e += 1
            s = nxt[a]
        err += pr * e
    return err / 2


def ladder_floor_full(prob: Dict[tuple, F], b: int, m: int) -> F:
    ns = 2 ** b
    na = 2 * ns
    best = None
    for nxt in product(range(ns), repeat=na):
        for out in product((0, 1), repeat=na):
            e = machine_error(prob, ns, nxt, out, m)
            if best is None or e < best:
                best = e
    return best


def shift_register_witness(m: int) -> Tuple[tuple, tuple]:
    """Four states s = 2*x_{t-1} + x_{t-2}; address a = s*2 + cur."""
    nxt = tuple(2 * (a % 2) + ((a // 2) // 2) for a in range(8))
    if m == 0:
        out = tuple(a % 2 for a in range(8))
    elif m == 1:
        out = tuple((a // 2) // 2 for a in range(8))
    else:
        out = tuple((a // 2) % 2 for a in range(8))
    return nxt, out


def ladder_floors(prob: Dict[tuple, F]) -> Dict[Tuple[int, int], F]:
    fl = {}
    for b in (0, 1):
        for m in (0, 1, 2):
            fl[(b, m)] = ladder_floor_full(prob, b, m)
    for m in (0, 1, 2):
        nxt, out = shift_register_witness(m)
        e = machine_error(prob, 4, nxt, out, m)
        if e != 0:
            die("b=2 witness for mode %d attains %s, not 0" % (m, e))
        fl[(2, m)] = F(0)
    return fl


def two_level_floors(prob: Dict[tuple, F]) -> Dict[Tuple[int, int], F]:
    r0 = ladder_floor_full(prob, 0, 1)
    # level 1: one bit stores x_{t-1}; witness nxt(a) = cur, out(a) = state
    e = machine_error(prob, 2, (0, 1, 0, 1), (0, 0, 1, 1), 1)
    if e != 0:
        die("two-level delay-1 witness attains %s" % e)
    return {(0, 0): F(0), (0, 1): r0, (1, 0): F(0), (1, 1): F(0)}


def alphabet_floor(A: int) -> F:
    """Stateless table cur -> guess of the previous symbol, length-3 uniform
    A-ary sequences scored at t in {1, 2}."""
    seqs = list(product(range(A), repeat=3))
    best = None
    for tab in product(range(A), repeat=A):
        e = 0
        for s in seqs:
            for t in (1, 2):
                if tab[s[t]] != s[t - 1]:
                    e += 1
        if best is None or e < best:
            best = e
    return F(best, 2 * len(seqs))


def alphabet_floors(A: int) -> Dict[Tuple[int, int], F]:
    return {(0, 0): F(0), (0, 1): alphabet_floor(A), (1, 0): F(0), (1, 1): F(0)}


# ---------------------------------------------------------------- verdicts
def argmin_set(E: Dict[int, F], lam: F) -> frozenset:
    costs = dict((k, E[k] + lam * k) for k in E)
    mn = min(costs.values())
    return frozenset(k for k in E if costs[k] == mn)


def frontier_by_halflines(E: Dict[int, F]) -> frozenset:
    """k is on the frontier iff some lam >= 0 makes it the STRICT argmin:
    for every j != k, lam*(k - j) < E(j) - E(k).  Each j gives an open
    half-line (an upper bound when k > j, a lower bound when k < j); the
    feasible set is the open interval (lo, hi) intersected with [0, inf)."""
    out = set()
    for k in E:
        lo = None
        hi = None
        for j in E:
            if j == k:
                continue
            bound = (E[j] - E[k]) / (k - j)
            if k > j:
                hi = bound if hi is None else min(hi, bound)
            else:
                lo = bound if lo is None else max(lo, bound)
        if lo is None or lo < 0:
            feasible = (hi is None) or (hi > 0)          # lam = 0 or any small lam
        else:
            feasible = (hi is None) or (hi > lo)         # an open, non-empty (lo, hi)
        if feasible:
            out.add(k)
    return frozenset(out)


def truth_of(spec: dict, fl: Dict[Tuple[int, int], F]) -> dict:
    eta = F(spec["accounting"]["eta"])
    p = [F(x) for x in spec["accounting"]["p"]]
    levels = list(spec["universe"]["levels"])
    modes = list(spec["universe"]["modes"])
    E = dict((k, eta * sum((p[m] * fl[(k, m)] for m in modes), F(0))) for k in levels)
    prices = [F(x) for x in spec["prices"]]
    return {
        "floors": fl,
        "profile": E,
        "thresholds": dict((k, E[k - 1] - E[k]) for k in levels[1:]),
        "frontier": frontier_by_halflines(E),
        "selection_by_price": dict((lam, argmin_set(E, lam)) for lam in prices),
        "failure_modes": dict((k, frozenset(m for m in modes if p[m] > 0 and fl[(k, m)] > 0)) for k in levels),
    }


# ---------------------------------------------------------------- case generation (FREEZE section 2)
def comps(total: int, parts: int) -> List[tuple]:
    if parts == 1:
        return [(total,)]
    out = []
    for a in range(total + 1):
        for rest in comps(total - a, parts - 1):
            out.append((a,) + rest)
    return out


def spec(cls: str, utype: str, A: int, eta: int, p: List[F], law: dict, prices: List[F]) -> dict:
    ladder = utype == "LADDER"
    return {
        "class": cls,
        "universe": {"type": utype, "alphabet": A,
                     "levels": [0, 1, 2] if ladder else [0, 1],
                     "modes": [0, 1, 2] if ladder else [0, 1],
                     "L": 4 if ladder else 3, "window": [2, 3] if ladder else [1, 2]},
        "accounting": {"eta": fs(eta), "p": [fs(x) for x in p], "rho": "1"},
        "law": law,
        "prices": [fs(x) for x in prices],
    }


def L_uniform() -> dict:
    return {"kind": "UNIFORM"}


def L_iid(q: F) -> dict:
    return {"kind": "IID", "q": fs(q)}


def L_period2() -> dict:
    return {"kind": "PERIOD2"}


def L_emp(stream: int, offset: int) -> dict:
    path, sha, _n = STREAMS[stream]
    return {"kind": "EMPIRICAL", "stream": stream, "path": path, "blob_sha1": sha, "offset": offset}


def build_cases(preimage: str, c1_prices: Optional[List[F]] = None) -> List[dict]:
    if c1_prices is None:
        c1_prices = PRICES
    cases = []
    for eta in (1, 2, 3):
        for c in comps(8, 3):
            cases.append(spec("C1_LADDER", "LADDER", 2, eta, [F(x, 8) for x in c], L_uniform(), c1_prices))
    for k8 in range(1, 8):
        for eta in (1, 2, 3):
            for k in range(9):
                cases.append(spec("C2_TWO_LEVEL_IID", "TWO_LEVEL", 2, eta, [1 - F(k, 8), F(k, 8)], L_iid(F(k8, 8)), PRICES))
    for A in (2, 3, 4):
        for eta in (1, 2, 3):
            for k in range(9):
                cases.append(spec("C3_ALPHABET", "TWO_LEVEL", A, eta, [1 - F(k, 8), F(k, 8)], L_uniform(), PRICES))
    for stream in range(3):
        for c in comps(4, 3):
            cases.append(spec("C4_EMPIRICAL_STREAM", "LADDER", 2, 1, [F(x, 4) for x in c], L_emp(stream, 0), PRICES))
    # C5: the draw protocol of the published executor, replayed here from the
    # revealed preimage; the sha256 comparison below is what checks it.
    rng = random.Random(preimage)
    c16 = comps(16, 3)
    for _ in range(60):
        utype = "LADDER" if rng.randrange(2) == 0 else "TWO_LEVEL"
        eta = rng.randrange(1, 5)
        if utype == "LADDER":
            c = c16[rng.randrange(len(c16))]
            p = [F(x, 16) for x in c]
        else:
            k = rng.randrange(17)
            p = [1 - F(k, 16), F(k, 16)]
        kind = rng.randrange(4)
        if kind == 0:
            law = L_uniform()
        elif kind == 1:
            law = L_iid(F(rng.randrange(1, 10), 10))
        elif kind == 2:
            law = L_period2()
        else:
            st = rng.randrange(3)
            off = rng.randrange(4096)
            law = L_emp(st, off)
        lam = F(rng.randrange(49), 32)
        cases.append(spec("C5_HIDDEN", utype, 2, eta, p, law, [lam]))
    for eta in (1, 2, 3):
        for law in (L_uniform(), L_iid(F(1, 4)), L_period2()):
            cases.append(spec("C6_NEGATIVE_CONTROL", "LADDER", 2, eta, [F(1), F(0), F(0)], law, PRICES))
    return cases


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def sha256_of(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- record parsing (PREDICTIONS_V1.json)
def parse_cell(c: Optional[dict]):
    if c is None:
        return None
    kind = c["kind"]
    if kind == "ABSTAIN":
        return ("ABSTAIN",)
    if kind == "POINT":
        return ("POINT", F(c["value"]))
    if kind == "INTERVAL":
        return ("INTERVAL", F(c["lo"]), F(c["hi"]), F(c["gamma"]))
    if kind == "SET":
        return ("SET", frozenset(int(v) for v in c["values"]))
    die("bad cell kind %r" % kind)
    return None


REQUIRED = ("profile", "frontier", "thresholds", "selection_by_price", "failure_modes")


def valid(rec: Optional[dict], sp: dict) -> bool:
    """Row-2 schema of FREEZE section 1, checked independently: all five
    fields present, keyed exactly by the case's levels / prices."""
    if not isinstance(rec, dict) or any(f not in rec for f in REQUIRED):
        return False
    levels = list(sp["universe"]["levels"])
    prices = set(F(x) for x in sp["prices"])
    return (set(rec["profile"]) == set(levels) and set(rec["thresholds"]) == set(levels[1:])
            and set(rec["selection_by_price"]) == prices and set(rec["failure_modes"]) == set(levels)
            and all(c is not None for c in rec["profile"].values())
            and all(c is not None for c in rec["thresholds"].values())
            and all(c is not None for c in rec["selection_by_price"].values())
            and all(c is not None for c in rec["failure_modes"].values())
            and rec["frontier"] is not None)


def parse_record(r: Optional[dict]) -> Optional[dict]:
    if r is None:
        return None
    return {
        "profile": dict((int(k), parse_cell(v)) for k, v in r["profile"].items()),
        "thresholds": dict((int(k), parse_cell(v)) for k, v in r["thresholds"].items()),
        "frontier": parse_cell(r["frontier"]),
        "selection_by_price": dict((F(k), parse_cell(v)) for k, v in r["selection_by_price"].items()),
        "failure_modes": dict((int(k), parse_cell(v)) for k, v in r["failure_modes"].items()),
    }


# ---------------------------------------------------------------- scorer (FREEZE section 4), written independently
class Acc(object):
    def __init__(self):
        self.n = {}

    def add(self, key: str, v=1):
        self.n[key] = self.n.get(key, 0) + v

    def get(self, key: str):
        return self.n.get(key, 0)


def score_value(cell, truth: F, eta: F, acc: Acc, pre: str, cal: Dict[F, List[int]], vac_covers: bool):
    """Returns True (covered), False (not covered) or None (abstain)."""
    acc.add(pre + "cells")
    if cell[0] == "ABSTAIN":
        acc.add(pre + "abstains")
        return None
    if cell[0] == "POINT":
        acc.add(pre + "sharp", F(1))
        acc.add(pre + "sharp_n")
        cal[F(1)][0] += 1
        hit = cell[1] == truth
        if hit:
            cal[F(1)][1] += 1
        return hit
    lo, hi, g = cell[1], cell[2], cell[3]
    sh = 1 - (hi - lo) / eta
    if sh < 0:
        sh = F(0)
    acc.add(pre + "sharp", sh)
    acc.add(pre + "sharp_n")
    inside = lo <= truth <= hi
    if lo <= 0 and hi >= eta:
        acc.add(pre + "vacuous")
        return inside if vac_covers else False
    cal[g][0] += 1
    if inside:
        cal[g][1] += 1
    return inside


def score_theory(recs: List[Optional[dict]], truths: List[dict], specs: List[dict], idx: Optional[List[int]] = None,
                 abstain_hits: bool = False, vac_covers: bool = False) -> dict:
    if idx is None:
        idx = list(range(len(specs)))
    acc = Acc()
    cal = dict((g, [0, 0]) for g in GAMMAS)
    rejected = 0
    for i in idx:
        sp, tr, rec = specs[i], truths[i], recs[i]
        eta = F(sp["accounting"]["eta"])
        levels = list(sp["universe"]["levels"])
        prices = [F(x) for x in sp["prices"]]
        if rec is None:
            rejected += 1
            acc.add("cc_misses", len(prices))
            acc.add("cc_cells", len(prices))
            acc.add("pr_cells", len(levels))
            acc.add("th_misses", len(levels) - 1)
            acc.add("th_cells", len(levels) - 1)
            acc.add("fr_misses")
            acc.add("fr_cells")
            acc.add("fm_misses", len(levels))
            acc.add("fm_cells", len(levels))
            continue
        for lam in prices:
            c = rec["selection_by_price"][lam]
            acc.add("cc_cells")
            if c[0] == "ABSTAIN":
                acc.add("cc_hits" if abstain_hits else "cc_abstains")
            elif c[1] == tr["selection_by_price"][lam]:
                acc.add("cc_hits")
            else:
                acc.add("cc_misses")
        for k in levels:
            r = score_value(rec["profile"][k], tr["profile"][k], eta, acc, "pr_", cal, vac_covers)
            if r is None and abstain_hits:
                r = True
            if r:
                acc.add("pr_covered")
        for k in levels[1:]:
            r = score_value(rec["thresholds"][k], tr["thresholds"][k], eta, acc, "th_", cal, vac_covers)
            if r is None:
                if abstain_hits:
                    acc.add("th_hits")
            elif r:
                acc.add("th_hits")
            else:
                acc.add("th_misses")
        c = rec["frontier"]
        acc.add("fr_cells")
        if c[0] == "ABSTAIN":
            acc.add("fr_hits" if abstain_hits else "fr_abstains")
        elif c[1] == tr["frontier"]:
            acc.add("fr_hits")
        else:
            acc.add("fr_misses")
        for k in levels:
            c = rec["failure_modes"][k]
            acc.add("fm_cells")
            if c[0] == "ABSTAIN":
                acc.add("fm_hits" if abstain_hits else "fm_abstains")
            elif c[1] == tr["failure_modes"][k]:
                acc.add("fm_hits")
            else:
                acc.add("fm_misses")

    def rat(a, b):
        return None if b == 0 else F(a) / b

    def hm(pre):
        h, m, a, c = acc.get(pre + "hits"), acc.get(pre + "misses"), acc.get(pre + "abstains"), acc.get(pre + "cells")
        return {"hits": h, "misses": m, "abstains": a, "cells": c, "score": rat(h, h + m)}

    per_gamma = {}
    max_err = F(0)
    calibrated = True
    for g in GAMMAS:
        d, c = cal[g]
        if d == 0:
            continue
        cov = F(c, d)
        per_gamma[g] = {"declared": d, "covered": c, "coverage": cov}
        if abs(cov - g) > max_err:
            max_err = abs(cov - g)
        if cov < g:
            calibrated = False
    th = hm("th_")
    th["vacuous"] = acc.get("th_vacuous")
    th["mean_sharpness"] = rat(acc.get("th_sharp"), acc.get("th_sharp_n"))
    return {
        "class_choice": hm("cc_"),
        "profile": {"covered": acc.get("pr_covered"), "cells": acc.get("pr_cells"), "vacuous": acc.get("pr_vacuous"),
                    "abstains": acc.get("pr_abstains"),
                    "mean_sharpness": rat(acc.get("pr_sharp"), acc.get("pr_sharp_n")),
                    "score": rat(acc.get("pr_covered"), acc.get("pr_cells") - acc.get("pr_abstains"))},
        "thresholds": th,
        "frontier": hm("fr_"),
        "failure_modes": hm("fm_"),
        "calibration": {"per_gamma": per_gamma, "max_error": max_err, "calibrated": calibrated},
        "rejected_records": rejected,
    }


def restricted_cc(recs: List[Optional[dict]], truths: List[dict], cells: List[tuple]) -> Optional[F]:
    h = m = 0
    for (i, lam) in cells:
        r = recs[i]
        if r is None:
            m += 1
            continue
        c = r["selection_by_price"][lam]
        if c[0] == "ABSTAIN":
            continue
        if c[1] == truths[i]["selection_by_price"][lam]:
            h += 1
        else:
            m += 1
    return None if h + m == 0 else F(h, h + m)


def to_plain(v):
    """Route A's serialisation: Fractions -> exact strings, Fraction keys -> strings."""
    if isinstance(v, bool) or v is None or isinstance(v, int):
        return v
    if isinstance(v, F):
        return fs(v)
    if isinstance(v, dict):
        return dict(((fs(k) if isinstance(k, F) else str(k)), to_plain(x)) for k, x in v.items())
    if isinstance(v, (list, tuple)):
        return [to_plain(x) for x in v]
    return str(v)


def truth_plain(t: dict) -> dict:
    return {
        "floors": dict(("%d,%d" % bm, fs(v)) for bm, v in sorted(t["floors"].items())),
        "profile": dict((str(k), fs(v)) for k, v in t["profile"].items()),
        "thresholds": dict((str(k), fs(v)) for k, v in t["thresholds"].items()),
        "frontier": sorted(t["frontier"]),
        "selection_by_price": dict((fs(l), sorted(s)) for l, s in t["selection_by_price"].items()),
        "failure_modes": dict((str(k), sorted(s)) for k, s in t["failure_modes"].items()),
    }


# ---------------------------------------------------------------- own null family
def own_null(k: int, specs: List[dict]) -> List[dict]:
    rng = random.Random(NULL_SEED_BASE + k)
    recs = []
    for sp in specs:
        eta = F(sp["accounting"]["eta"])
        levels = list(sp["universe"]["levels"])
        modes = list(sp["universe"]["modes"])
        nl, nm = len(levels), len(modes)

        def subset(items, nonempty):
            while True:
                chosen = [x for x in items if rng.randrange(2) == 1]
                if chosen or not nonempty:
                    return frozenset(chosen)

        rec = {"profile": dict((k2, ("POINT", eta * F(rng.randrange(33), 32))) for k2 in levels),
               "thresholds": dict((k2, ("POINT", eta * F(rng.randrange(33), 32))) for k2 in levels[1:]),
               "frontier": ("SET", subset(levels, True)),
               "selection_by_price": dict((F(l), ("SET", subset(levels, True))) for l in sp["prices"]),
               "failure_modes": dict((k2, ("SET", subset(modes, False))) for k2 in levels)}
        recs.append(rec)
    return recs


def gt(a: Optional[F], b: Optional[F]) -> bool:
    if a is None:
        return False
    if b is None:
        return True
    return a > b


# ---------------------------------------------------------------- main
def main() -> int:
    res = {"schema": "GMI_833_Z11_IMB_ORACLE_V1", "route": "B", "imports_route_A": False}
    with io.open(os.path.join(HERE, "CASES_V1.json"), encoding="utf-8") as fh:
        cases_doc = json.load(fh)
    with io.open(os.path.join(HERE, "PREDICTIONS_V1.json"), encoding="utf-8") as fh:
        pred_doc = json.load(fh)
    with io.open(os.path.join(HERE, "RESULT_V1.json"), encoding="utf-8") as fh:
        route_a = json.load(fh)

    preimage = cases_doc["hidden_seed_preimage"]
    commit_ok = hashlib.sha256(preimage.encode("utf-8")).hexdigest() == COMMITMENT
    pins_ok = load_streams()
    if not commit_ok or not pins_ok:
        die("commitment %s pins %s" % (commit_ok, pins_ok))

    # ---- cases ----
    mine = build_cases(preimage)
    theirs = [c["spec"] for c in cases_doc["cases"]]
    specs_equal = mine == theirs
    my_sha = sha256_of(mine)
    sha_equal = my_sha == cases_doc["case_set_sha256"] == route_a["case_set_sha256"]
    census = {}
    for c in mine:
        census[c["class"]] = census.get(c["class"], 0) + 1
    # C5 range rules of FREEZE section 2
    c5_rules_ok = True
    for c in mine:
        if c["class"] != "C5_HIDDEN":
            continue
        eta = int(F(c["accounting"]["eta"]))
        p = [F(x) for x in c["accounting"]["p"]]
        lam = F(c["prices"][0])
        if not (1 <= eta <= 4) or any(x.denominator not in (1, 2, 4, 8, 16) for x in p) or sum(p) != 1:
            c5_rules_ok = False
        if not (lam.denominator in (1, 2, 4, 8, 16, 32) and 0 <= lam <= F(48, 32)):
            c5_rules_ok = False
        law = c["law"]
        if law["kind"] == "IID" and F(law["q"]).denominator not in (1, 2, 5, 10):
            c5_rules_ok = False
        if law["kind"] == "EMPIRICAL" and not (0 <= int(law["offset"]) < 4096):
            c5_rules_ok = False
    specs = mine
    n = len(specs)

    # ---- truths by full enumeration ----
    floor_cache = {}
    truths = []
    for sp in specs:
        u = sp["universe"]
        law = sp["law"]
        lk = canon(law)
        if u["type"] == "LADDER":
            key = ("LADDER", lk)
            if key not in floor_cache:
                floor_cache[key] = ladder_floors(law_probs(law))
        elif int(u["alphabet"]) == 2:
            key = ("TWO_LEVEL", lk)
            if key not in floor_cache:
                floor_cache[key] = two_level_floors(law_probs(law))
        else:
            key = ("ALPHABET", int(u["alphabet"]))
            if key not in floor_cache:
                floor_cache[key] = alphabet_floors(int(u["alphabet"]))
        truths.append(truth_of(sp, floor_cache[key]))
    truth_equal = sum(1 for i in range(n) if truth_plain(truths[i]) == cases_doc["cases"][i]["truth"])
    base = floor_cache[("LADDER", canon(L_uniform()))]
    base_ok = dict((k, fs(v)) for k, v in base.items()) == {
        (0, 0): "0", (0, 1): "1/2", (0, 2): "1/2", (1, 0): "0", (1, 1): "0", (1, 2): "5/16",
        (2, 0): "0", (2, 1): "0", (2, 2): "0"}

    # ---- records ----
    records = {}
    own_rejections = {}
    for tid, recs in pred_doc["theories"].items():
        if len(recs) != n:
            die("theory %s has %d records" % (tid, len(recs)))
        parsed = [parse_record(r) for r in recs]
        own_rejections[tid] = 0
        for i in range(n):
            if parsed[i] is not None and not valid(parsed[i], specs[i]):
                parsed[i] = None
                own_rejections[tid] += 1
        records[tid] = parsed

    # ---- scores and agreement ----
    scores = dict((tid, score_theory(records[tid], truths, specs)) for tid in records)
    mismatches = []
    for tid in sorted(scores):
        mine_p = to_plain(scores[tid])
        theirs_p = route_a["scores"].get(tid)
        if mine_p != theirs_p:
            mismatches.append(tid)
    by_class = {}
    cls_idx = {}
    for i, sp in enumerate(specs):
        cls_idx.setdefault(sp["class"], []).append(i)
    class_mismatch = []
    for cls, idx in cls_idx.items():
        by_class[cls] = to_plain(score_theory(records["T_GMI_IC1"], truths, specs, idx))
        if by_class[cls] != route_a["scores_by_class"].get(cls):
            class_mismatch.append(cls)

    # ---- scrambled control, both forms (FREEZE C6(b), AMENDMENT 1) ----
    groups = {}
    for i, sp in enumerate(specs):
        groups.setdefault((sp["class"], sp["universe"]["type"]), []).append(i)
    scr = [None] * n
    for key in sorted(groups):
        idx = groups[key]
        if len(idx) < 2:
            die("scramble group of size 1")
        for j, i in enumerate(idx):
            partner = truths[idx[(j + 1) % len(idx)]]
            prices = [F(x) for x in specs[i]["prices"]]
            scr[i] = dict(partner)
            scr[i]["selection_by_price"] = dict((lam, argmin_set(partner["profile"], lam)) for lam in prices)
    informative = [(i, lam) for i in range(n) for lam in scr[i]["selection_by_price"]
                   if scr[i]["selection_by_price"][lam] != truths[i]["selection_by_price"][lam]]
    scr_literal = dict((tid, score_theory(records[tid], scr, specs)["class_choice"]["score"]) for tid in records)
    scr_info = dict((tid, restricted_cc(records[tid], scr, informative)) for tid in records)
    a_ctrl = route_a["scrambled_truth_control"]
    scr_literal_agree = to_plain(scr_literal) == a_ctrl["literal_all_cells"]["class_choice"]
    scr_info_agree = (to_plain(scr_info) == a_ctrl["informative_cells"]["class_choice"]
                      and len(informative) == a_ctrl["informative_cells"]["cells"])
    # sanity on the informative-cell control: a truth reader of the scrambled
    # truth scores exactly 1 there and a perfect real-truth predictor scores 0
    reader = [dict(records["T_GMI_IC1"][i], selection_by_price=dict((lam, ("SET", s)) for lam, s in scr[i]["selection_by_price"].items()))
              for i in range(n)]
    reader_info = restricted_cc(reader, scr, informative)

    # ---- own null family ----
    fields = ("class_choice", "thresholds", "frontier", "failure_modes")
    best = dict((f, None) for f in fields)
    best_info = None
    for k in range(N_NULL):
        recs = own_null(k, specs)
        s = score_theory(recs, truths, specs)
        for f in fields:
            v = s[f]["score"]
            if best[f] is None or gt(v, best[f]):
                best[f] = v
        vi = restricted_cc(recs, scr, informative)
        if best_info is None or gt(vi, best_info):
            best_info = vi
    gmi = dict((f, scores["T_GMI_IC1"][f]["score"]) for f in fields)
    own_null_beaten = all(gt(gmi[f], best[f]) for f in fields)
    gmi_info_le_null = not gt(scr_info["T_GMI_IC1"], best_info)

    # ---- frozen predictions re-derived where the quantity is Route B's ----
    b2 = {"stateless_equal": 0, "b1_covered": 0}
    for stream in range(3):
        law = L_emp(stream, 0)
        prob = law_probs(law)
        fl = floor_cache[("LADDER", canon(law))]
        for m in (1, 2):
            # pair-Bayes error of x_{t-m} given x_t pooled over t in {2,3}
            joint = {}
            for w, pr in prob.items():
                for t in (2, 3):
                    key2 = (w[t], w[t - m])
                    joint[key2] = joint.get(key2, F(0)) + pr / 2
            pb = sum(min(joint.get((c, 0), F(0)), joint.get((c, 1), F(0))) for c in (0, 1))
            if pb == fl[(0, m)]:
                b2["stateless_equal"] += 1
        if fl[(0, 0)] == 0:
            b2["stateless_equal"] += 1
        r2 = fl[(0, 2)]
        if F(0) <= fl[(1, 2)] <= r2:
            b2["b1_covered"] += 1
    b4 = pred_doc["theories"]["T_DECLARED"] == pred_doc["theories"]["T_GMI_IC1"]

    def thr_miss(tid, idx):
        cnt = 0
        for i in idx:
            r = records[tid][i]
            miss = False
            for k, c in r["thresholds"].items():
                tv = truths[i]["thresholds"][k]
                if (c[0] == "POINT" and c[1] != tv) or (c[0] == "INTERVAL" and not (c[1] <= tv <= c[2])):
                    miss = True
            cnt += 1 if miss else 0
        return cnt

    c2q = [i for i in cls_idx["C2_TWO_LEVEL_IID"] if F(specs[i]["law"]["q"]) != F(1, 2)]
    c3a = [i for i in cls_idx["C3_ALPHABET"] if int(specs[i]["universe"]["alphabet"]) != 2]
    c2q_pos = [i for i in c2q if F(specs[i]["accounting"]["p"][1]) > 0]
    c3a_pos = [i for i in c3a if F(specs[i]["accounting"]["p"][1]) > 0]
    b3 = {"T_HALF_C2_q_ne_half_cases": len(c2q), "T_HALF_C2_miss_cases": thr_miss("T_HALF", c2q),
          "T_HALF_C2_p_pos_cases": len(c2q_pos), "T_HALF_C2_p_pos_miss_cases": thr_miss("T_HALF", c2q_pos),
          "T_HALF_C3_A_ne_2_cases": len(c3a), "T_HALF_C3_miss_cases": thr_miss("T_HALF", c3a),
          "T_HALF_C3_p_pos_cases": len(c3a_pos), "T_HALF_C3_p_pos_miss_cases": thr_miss("T_HALF", c3a_pos),
          "T_LEVEL_calibrated": scores["T_LEVEL"]["calibration"]["calibrated"]}
    a_b3 = route_a["frozen_predictions"]["B3"]["evidence"]
    b3_agree = (b3["T_HALF_C2_miss_cases"] == a_b3["T_HALF_C2_q_ne_half"]["threshold_miss_cases"]
                and b3["T_HALF_C3_miss_cases"] == a_b3["T_HALF_C3_A_ne_2"]["threshold_miss_cases"])
    c12 = cls_idx["C1_LADDER"] + cls_idx["C2_TWO_LEVEL_IID"]
    b5 = {}
    for tid in ("T_MDL", "T_SRM", "T_SATISFICE", "T_OCCAM_HARD"):
        s12 = score_theory(records[tid], truths, specs, c12)["class_choice"]
        b5[tid] = {"C1_C2_misses": s12["misses"], "beaten": gt(gmi["class_choice"], scores[tid]["class_choice"]["score"])}
    b5_agree = all(b5[t]["C1_C2_misses"] == route_a["frozen_predictions"]["B5"]["evidence"][t]["C1_C2_misses"] for t in b5)

    # ---- hostiles re-checked with the independent instruments ----
    hz3 = score_theory(records["T_ABSTAIN"], truths, specs, abstain_hits=True)["class_choice"]
    honest = scores["T_ABSTAIN"]["class_choice"]
    vac = []
    for i in range(n):
        eta = F(specs[i]["accounting"]["eta"])
        levels = list(specs[i]["universe"]["levels"])
        r = dict(records["T_GMI_IC1"][i])
        r["profile"] = dict((k, ("INTERVAL", F(0), eta, F(1))) for k in levels)
        r["thresholds"] = dict((k, ("INTERVAL", F(0), eta, F(1))) for k in levels[1:])
        vac.append(r)
    vac_h = score_theory(vac, truths, specs)
    vac_t = score_theory(vac, truths, specs, vac_covers=True)
    tampered_sha = sha256_of(build_cases(preimage, PRICES[:-1]))
    wrong_sha = hashlib.sha256((preimage + ":wrong").encode("utf-8")).hexdigest()
    hz2 = [dict((k, v) for k, v in records["T_GMI_IC1"][i].items() if k != "frontier") for i in range(n)]
    hz2_rej = sum(1 for i in range(n) if not valid(hz2[i], specs[i]))
    hz2_scored = score_theory([None if not valid(hz2[i], specs[i]) else hz2[i] for i in range(n)], truths, specs)
    hostiles = {
        "HZ2_missing_field_rejected": {"applicable": hz2_rej > 0 and all(own_rejections[t] == 0 for t in records),
                                       "detected": hz2_rej == n and hz2_scored["rejected_records"] == n
                                       and hz2_scored["class_choice"]["abstains"] == 0
                                       and hz2_scored["class_choice"]["misses"] == hz2_scored["class_choice"]["cells"]},
        "HZ3_abstain_as_hit": {"applicable": hz3["hits"] != honest["hits"],
                               "detected": gt(hz3["score"], F(0)) and honest["hits"] == 0 and honest["misses"] == 0},
        "HZ4_vacuous_as_covered": {"applicable": vac_t["profile"]["covered"] != vac_h["profile"]["covered"],
                                   "detected": vac_h["profile"]["vacuous"] == vac_h["profile"]["cells"] and vac_h["profile"]["covered"] == 0},
        "HZ5_tampered_rule": {"applicable": tampered_sha != my_sha, "detected": tampered_sha != cases_doc["case_set_sha256"]},
        "HZ6_wrong_preimage": {"applicable": True, "detected": wrong_sha != COMMITMENT},
        "HZ1_truth_reader_on_informative_cells": {"applicable": reader_info != scr_info["T_GMI_IC1"],
                                                  "detected": reader_info == 1 and gt(reader_info, best_info)},
    }
    hostiles_ok = all(v["applicable"] and v["detected"] for v in hostiles.values())

    checks = {
        "commitment_ok": commit_ok,
        "pins_ok": pins_ok,
        "base_floors_reproduced_by_full_enumeration": base_ok,
        "specs_equal_to_route_A": specs_equal,
        "case_set_sha256_equal": sha_equal,
        "census_519": census == {"C1_LADDER": 135, "C2_TWO_LEVEL_IID": 189, "C3_ALPHABET": 81,
                                 "C4_EMPIRICAL_STREAM": 45, "C5_HIDDEN": 60, "C6_NEGATIVE_CONTROL": 9},
        "C5_draws_obey_section_2_ranges": c5_rules_ok,
        "truths_equal_all_cases": truth_equal == n,
        "every_registered_score_equal": mismatches == [],
        "every_class_score_equal": class_mismatch == [],
        "scrambled_literal_equal": scr_literal_agree,
        "scrambled_informative_equal": scr_info_agree,
        "truth_reader_scores_1_on_informative_cells": reader_info == 1,
        "T_GMI_IC1_scores_0_on_informative_cells": scr_info["T_GMI_IC1"] == 0,
        "own_null_beaten_on_four_fields": own_null_beaten,
        "T_GMI_IC1_le_own_null_on_informative_cells": gmi_info_le_null,
        "B2_stateless_9_of_9_and_b1_covered_3_of_3": b2 == {"stateless_equal": 9, "b1_covered": 3},
        "B3_counts_equal_route_A": b3_agree,
        "B4_T_DECLARED_identical_records": b4,
        "B5_counts_equal_route_A": b5_agree,
        "hostiles_all_applicable_and_detected": hostiles_ok,
    }
    res.update({
        "case_set_sha256": my_sha,
        "census": census,
        "truths_equal": truth_equal,
        "n_cases": n,
        "distinct_laws_enumerated": sum(1 for k in floor_cache if k[0] != "ALPHABET"),
        "alphabet_populations_enumerated": sum(1 for k in floor_cache if k[0] == "ALPHABET"),
        "b1_machines_enumerated_per_law_and_mode": 256,
        "b2_method": "constructive shift-register witness attains 0 for every mode under every law; a floor is >= 0, so 0 is exact",
        "score_mismatches": mismatches,
        "class_score_mismatches": class_mismatch,
        "scores": dict((tid, to_plain(scores[tid])) for tid in sorted(scores)),
        "scrambled": {"informative_cells": len(informative), "literal": to_plain(scr_literal), "informative": to_plain(scr_info),
                      "truth_reader_informative": fs(reader_info) if reader_info is not None else None},
        "own_null": {"n": N_NULL, "seed_base": NULL_SEED_BASE, "best": to_plain(best), "best_informative": fs(best_info) if best_info is not None else None,
                     "T_GMI_IC1": to_plain(gmi)},
        "B2": b2, "B3": to_plain(b3), "B5": to_plain(b5),
        "hostiles": hostiles,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    })
    with io.open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    print("IMB-v1 Route B  verdict=%s  truths equal %d/%d  score mismatches %s" % (res["verdict"], truth_equal, n, mismatches))
    print("  checks: %s" % checks)
    print("  own null best: %s  informative best: %s" % (to_plain(best), fs(best_info) if best_info is not None else None))
    print("  B3: %s" % to_plain(b3))
    return 0 if res["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
