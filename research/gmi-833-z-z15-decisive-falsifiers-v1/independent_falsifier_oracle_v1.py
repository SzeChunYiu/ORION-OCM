"""Route B -- source-separated oracle for the Z15 decisive falsifiers.

Imports nothing from route A and nothing from the Z12 package. It rebuilds the
candidate universe by a different decomposition (explicit truth-table lists
rather than bit shifts), reduces it to a multiplicity histogram over
(state_bits, e_now, e_delay), and decides every falsifier with **integer**
objective arithmetic obtained by clearing denominators -- not with Fraction
comparisons. Agreement with route A on every verdict and count is required.

Run:  python3 -I -B independent_falsifier_oracle_v1.py
"""
import json
import os
import random
import sys
from fractions import Fraction

_H = os.path.dirname(os.path.abspath(__file__))
_R = os.path.dirname(_H)
SL, PS = "STATELESS", "PERSISTENT_STATE"
SCALES = ("1/7", "1/2", "2/1", "3/1", "11/5", "100/1")


def _load(path):
    with open(path) as fh:
        return json.load(fh)


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _lcm(a, b):
    return a // _gcd(a, b) * b


# ------------------------------------------- universe by table-list expansion
def _bits(value, width):
    return [(value >> i) & 1 for i in range(width)]


def _frames():
    out = []
    for s in range(8):
        out.append(_bits(s, 3))
    return out


FRAMES = _frames()


def _score_stateless(out_bits):
    """out_bits indexed by 2*mode + current."""
    en = ed = 0
    for frame in FRAMES:
        for pos in (1, 2):
            cur = frame[pos]
            prev = frame[pos - 1]
            if out_bits[0 * 2 + cur] != cur:
                en += 1
            if out_bits[1 * 2 + cur] != prev:
                ed += 1
    return en, ed


def _score_stateful(nxt_bits, out_bits):
    """bits indexed by 4*state + 2*mode + current."""
    errs = [0, 0]
    for mode in (0, 1):
        for frame in FRAMES:
            state = 0
            for pos in range(3):
                cur = frame[pos]
                i = 4 * state + 2 * mode + cur
                emitted = out_bits[i]
                if pos > 0:
                    want = cur if mode == 0 else frame[pos - 1]
                    if emitted != want:
                        errs[mode] += 1
                state = nxt_bits[i]
    return errs[0], errs[1]


def build_histogram():
    hist = {}
    for table in range(16):
        k = (0,) + _score_stateless(_bits(table, 4))
        hist[k] = hist.get(k, 0) + 1
    for nxt in range(256):
        nb = _bits(nxt, 8)
        for table in range(256):
            k = (1,) + _score_stateful(nb, _bits(table, 8))
            hist[k] = hist.get(k, 0) + 1
    return hist


# --------------------------------------------------- integer-coefficient argmin
def _coeffs(p, eta, lam):
    a = eta * (1 - p) / 16
    b = eta * p / 16
    c = lam
    scale = _lcm(_lcm(a.denominator, b.denominator), c.denominator)
    return int(a * scale), int(b * scale), int(c * scale)


def winner_classes(hist, p, eta, lam):
    a, b, c = _coeffs(p, eta, lam)
    best = None
    cls = set()
    for (bits, en, ed) in hist:
        v = a * en + b * ed + c * bits
        if best is None or v < best:
            best = v
            cls = set([SL if bits == 0 else PS])
        elif v == best:
            cls.add(SL if bits == 0 else PS)
    return frozenset(cls)


def predicted(p, eta, lam, mult=Fraction(1)):
    star = mult * eta * p / 2
    if lam < star:
        return frozenset([PS])
    if lam > star:
        return frozenset([SL])
    return frozenset([PS, SL])


def worlds():
    doc = _load(os.path.join(_R, "gmi-833-heldout-20-transitions-v1", "RESULT_V1.json"))
    out = []
    for case in doc["cases"]:
        p = Fraction(case["p"])
        eta = Fraction(case["eta"])
        star = eta * p / 2
        out.append((case["case"], "low", p, eta, Fraction(case["lambda_low"]), star))
        out.append((case["case"], "high", p, eta, Fraction(case["lambda_high"]), star))
        out.append((case["case"], "boundary", p, eta, star, star))
    return out, doc


# ---------------------------------------------------------------- falsifiers
def f1(hist, ws, mult=Fraction(1), include_boundary=False):
    n = 0
    bad = 0
    for (_cid, tag, p, eta, lam, _star) in ws:
        if tag == "boundary" and not include_boundary:
            continue
        n += 1
        if predicted(p, eta, lam, mult) != winner_classes(hist, p, eta, lam):
            bad += 1
    return n, bad


def f2(hist, ws, narrow=False):
    bad = 0
    for (_cid, _tag, p, eta, lam, star) in ws:
        pred = predicted(p, eta, lam)
        if narrow and lam < star:
            pred = frozenset([SL])
        if not winner_classes(hist, p, eta, lam) <= pred:
            bad += 1
    return len(ws), bad


def f3(damage=False):
    ev = os.path.join(_R, "gmi-833-capability-predictor-evaluation-v1")
    res = _load(os.path.join(ev, "RESULT_V1.json"))
    truth = {}
    for c in res["curves"]:
        for case in c["detail"]:
            for pt in case["points"]:
                truth[(c["universe"], case["case_index"], tuple(pt["budget"]))] = pt["external_values"]
    rows = []
    for name in ("FROZEN_PREDICTIONS_V1.json", "FROZEN_PREDICTIONS_V4.json"):
        doc = _load(os.path.join(ev, name))
        for uni in doc["universes"]:
            u = uni["universe"]
            buf = []
            ok = True
            for ci, curve in enumerate(uni["curves"]):
                for pt in curve["points"]:
                    key = (u, ci, tuple(pt["budget"]))
                    if key not in truth:
                        ok = False
                        break
                    buf.append((set(pt["identified_set"]), set(truth[key])))
                if not ok:
                    break
            if ok:
                rows.extend(buf)
    if damage:
        for i, (S, T) in enumerate(rows):
            if T and T <= S and len(S) > 1:
                S2 = set(S)
                S2.discard(sorted(T)[0])
                rows[i] = (S2, T)
                break
    return len(rows), sum(1 for S, T in rows if not T <= S)


def f4a(hist, ws, semantic_break=False):
    """Relabelling cannot change a multiset; a semantics-permuting pseudo-remint can."""
    flat = []
    for k, m in hist.items():
        flat.extend([k] * m)
    base = dict(((c, t), winner_classes(hist, p, e, l)) for (c, t, p, e, l, _s) in ws)
    changes = 0
    cache = {}
    for seed in range(7000, 7200):
        rng = random.Random(seed)
        perm = list(range(len(flat)))
        rng.shuffle(perm)
        if semantic_break:
            remade = [(flat[i][0], flat[perm[i]][1], flat[perm[i]][2]) for i in range(len(flat))]
        else:
            remade = [flat[perm[i]] for i in range(len(flat))]
        h2 = {}
        for k in remade:
            h2[k] = h2.get(k, 0) + 1
        key = tuple(sorted(h2.items()))
        if key not in cache:
            cache[key] = dict(((c, t), winner_classes(h2, p, e, l)) for (c, t, p, e, l, _s) in ws)
        got = cache[key]
        for (c, t, _p, _e, _l, _s) in ws:
            if got[(c, t)] != base[(c, t)]:
                changes += 1
    return changes, len(cache)


def f4b(hist, ws, eta_only=False):
    changes = 0
    checks = 0
    for (_c, _t, p, eta, lam, _s) in ws:
        base = winner_classes(hist, p, eta, lam)
        for text in SCALES:
            k = Fraction(text)
            checks += 1
            lam2 = lam if eta_only else k * lam
            if winner_classes(hist, p, k * eta, lam2) != base:
                changes += 1
    return checks, changes


def main():
    hist = build_histogram()
    ws, parent = worlds()
    n1, b1 = f1(hist, ws)
    n1p, b1p = f1(hist, ws, mult=Fraction(2))
    n2, b2 = f1(hist, ws, include_boundary=True)
    n2p, b2p = f1(hist, ws, mult=Fraction(6, 7), include_boundary=True)
    ce_n, ce_b = f1(hist, ws, mult=Fraction(6, 7))
    caught = 0
    caught_plus = 0
    ladder = [Fraction(n, d) for n in range(1, 8) for d in range(1, 8) if Fraction(n, d) != 1]
    for seed in range(8000, 8200):
        r = random.Random(seed).choice(ladder)
        if f1(hist, ws, mult=r)[1] > 0:
            caught += 1
        if f1(hist, ws, mult=r, include_boundary=True)[1] > 0:
            caught_plus += 1
    out = {
        "schema": "GMI_833_Z15_FALSIFIER_ORACLE_V1",
        "route": "B",
        "candidate_census": sum(hist.values()),
        "distinct_risk_summaries": len(hist),
        "F1": {"checked": n1, "mismatches": b1},
        "F1_planted_double_boundary": {"checked": n1p, "mismatches": b1p},
        "F1_counterexample_6_7": {"checked": ce_n, "mismatches": ce_b},
        "F1PLUS": {"checked": n2, "mismatches": b2},
        "F1PLUS_planted_6_7": {"checked": n2p, "mismatches": b2p},
        "F2": dict(zip(("checked", "outside"), f2(hist, ws))),
        "F2_planted": dict(zip(("checked", "outside"), f2(hist, ws, narrow=True))),
        "F3": dict(zip(("checked", "misses"), f3())),
        "F3_planted": dict(zip(("checked", "misses"), f3(damage=True))),
        "F4a": dict(zip(("changes", "distinct_multisets"), f4a(hist, ws))),
        "F4a_planted": dict(zip(("changes", "distinct_multisets"), f4a(hist, ws, semantic_break=True))),
        "F4b": dict(zip(("checks", "changes"), f4b(hist, ws))),
        "F4b_planted": dict(zip(("checks", "changes"), f4b(hist, ws, eta_only=True))),
        "null": {"seeds": 200, "F1_caught": caught, "F1PLUS_caught": caught_plus},
        "parent_controls": {"raw_candidates": parent["counts"]["raw_candidates"],
                            "risk_points": parent["counts"]["risk_points"],
                            "endpoint_predictions": parent["counts"]["endpoint_predictions"],
                            "boundary_ties": parent["counts"]["boundary_ties"],
                            "shifted_threshold_failures": parent["counts"]["shifted_threshold_failures"]},
    }
    with open(os.path.join(_H, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    sys.stdout.write("Z15 route B census=%d summaries=%d F1=%d/%d F1+=%d/%d null=%d/%d\n"
                     % (out["candidate_census"], len(hist), b1, n1, b2, n2, caught, caught_plus))
    return 0


if __name__ == "__main__":
    sys.exit(main())
