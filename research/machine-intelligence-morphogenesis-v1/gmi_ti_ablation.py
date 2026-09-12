"""RV-377-122 -- experimental verification of theorem TI-1 by channel ablation.

TI-1 states a capability ceiling on ANY machine, not on any named architecture:

    Y = F(P, D, Q, A, R)  with  I(W;P) = 0  and  R independent of W

    => a realization with no development, no informative query and no informative
       authority has success probability at most 1/M on a uniform M-world
       exact-identification obligation.

That is a prediction about UNSEEN forms: it bounds machines nobody has built, because it
constrains the information channels rather than the mechanism.  It has been verified
combinatorially (GMI_TARGET_INFORMATION_EXACT_RECEIPT_V1.json) but never against real
machines on real worlds.  This module does that.

METHOD.  A generic exemplar machine -- the most capable thing available to a learner that
has only D and Q -- is run on each K4-D world under channel ablations:

    FULL      development from THIS world
    NO_DEV    development reminted from an INDEPENDENT world (same shape, different W)
    NO_QUERY  queries shuffled against their answers, destroying Q's instance content
    NEITHER   both ablations

The machine is unchanged across arms.  Only the channels change.  TI-1 predicts NO_DEV and
NEITHER collapse to the chance floor; a world where they do NOT collapse is LEAKING the
protected variable through a channel its declaration does not name -- so this experiment is
simultaneously a capability test and a leak detector.
"""
from __future__ import annotations
import json, math, random
import gmi_k4d_worlds as W


def _flat(o):
    """order-stable flattening of heterogeneous world items to a comparable token list."""
    if isinstance(o, dict): return [x for k in sorted(o) for x in _flat(o[k])]
    if isinstance(o, (list, tuple)): return [x for v in o for x in _flat(v)]
    return [o]


def _dist(a, b):
    fa, fb = _flat(a), _flat(b)
    n = min(len(fa), len(fb))
    d = sum(1 for i in range(n) if fa[i] != fb[i]) + abs(len(fa) - len(fb))
    return d


def exemplar_machine(development, query):
    """nearest development exemplar by token mismatch; returns its recorded answer.

    This is a genuine learner: with real development it generalizes from stored cases.
    It is deliberately the STRONGEST generic D+Q machine, so a collapse under ablation
    cannot be blamed on a weak mechanism.
    """
    if not development: return None
    best, bd = None, None
    for item in development:
        d = _dist(item, query)
        if bd is None or d < bd: bd, best = d, item
    if isinstance(best, dict):
        for k in ("y", "answer", "expected", "out", "label", "x"):
            if k in best: return best[k]
        vals = [v for k, v in sorted(best.items()) if k not in ("z", "q", "query")]
        return vals[-1] if vals else None
    return best


def score(world, development, queries):
    exp = world["expected"]
    n = min(len(queries), len(exp))
    if n == 0: return 0.0
    hit = sum(1 for i in range(n) if exemplar_machine(development, queries[i]) == exp[i])
    return hit / n


def run_family(fid, seed=12345, scale=1, alt_seed=999983):
    w = W.generate(fid, seed, scale)
    alt = W.generate(fid, alt_seed, scale)              # same shape, independent W
    dev, qs = w["development"], w["queries"]
    shuffled = list(qs); random.Random(7).shuffle(shuffled)
    M = 2 ** w["entropy_bits_lower_bound"]
    return {"family_id": fid,
            "entropy_bits": round(w["entropy_bits_lower_bound"], 3),
            "M": M, "chance_floor_1_over_M": 1.0 / M,
            "declared_source": w["target_information_source"],
            "n_queries": len(qs), "n_development": len(dev),
            "FULL":    round(score(w, dev, qs), 4),
            "NO_DEV":  round(score(w, alt["development"], qs), 4),
            "NO_QUERY": round(score(w, dev, shuffled), 4),
            "NEITHER": round(score(w, alt["development"], shuffled), 4)}
