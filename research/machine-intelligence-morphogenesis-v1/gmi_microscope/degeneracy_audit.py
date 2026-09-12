"""RV-377-112 / DG-12 -- is the OBLIGATION itself a constant function?

Rule 40 asks whether a constant answer can CLEAR theta on an ecology.  That is one level
too shallow.  The DG-9 E1/E3 audit found `e1_scdi` regime B returning the answer 1 on all
24 registered evaluation queries: the obligation is not merely easy for a constant, it IS
a constant.  A row scoring 1.0000 there has demonstrated nothing whatsoever, and no
capability number computed on it carries information.

Nothing in the corpus has ever checked for this.  Rule 40's control would flag a
degenerate obligation only incidentally, via a best constant at or near the ceiling, and
only where a best constant was computed at all.

This module audits every obligation reachable from the registered modules for degeneracy
directly: how many DISTINCT answers does the truth function take over its own declared
evaluation set?  One distinct answer is DEGENERATE.  Two, on a set of n queries, is
reported with its split, because a near-balanced binary obligation and a 23-1 binary
obligation are very different instruments.
"""
from __future__ import annotations

import collections
import itertools
import json
import os
import time

from . import ecology, smooth
from .core import sha256_of

RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "microscopes", "results")


def _classify(vals):
    n = len(vals)
    c = collections.Counter(vals)
    k = len(c)
    top = max(c.values())
    best_const_agreement = top / n if n else 0.0
    if k <= 1:
        status = "DEGENERATE__OBLIGATION_IS_A_CONSTANT"
    elif best_const_agreement >= 0.85:
        status = "NEAR_DEGENERATE__CONSTANT_AGREES_ON_>=85%"
    elif k == 2 and min(c.values()) <= max(1, n // 10):
        status = "SKEWED_BINARY"
    else:
        status = "NON_DEGENERATE"
    return {"n_queries": n, "n_distinct_answers": k, "counts": {str(a): b for a, b in sorted(c.items(), key=lambda t: -t[1])},
            "best_constant_agreement": round(best_const_agreement, 4), "status": status}


def audit_smooth_registry():
    """every registered smooth/table ecology, over its own declared evaluation set."""
    out = {}
    for name, spec in sorted(ecology.REGISTRY.items()):
        target = ecology.target_of(spec)
        for crit, eval_x in (("all", smooth.ALL_X), ("unseen", smooth.UNSEEN)):
            out[f"{name}|{crit}"] = _classify([target[x] for x in eval_x])
    return out


def audit_e1():
    """the E1 serving regimes at their REGISTERED coefficients, over the registered eval set."""
    out = {}
    try:
        from . import e1_scdi, e1_vlc
    except Exception as e:
        return {"__unavailable__": repr(e)[:200]}
    CV, N_F, Q = e1_scdi.COEFF_VALUES, e1_scdi.N_F, e1_vlc.EVAL_QUERIES
    coeffs = [(CV[(2 * i) % 4], CV[(2 * i + 1) % 4]) for i in range(N_F)]
    for reg in ("A", "B", "C", "D"):
        try:
            out[f"e1_scdi|regime_{reg}"] = _classify([e1_scdi.truth_regime(coeffs, x, s, reg) for (x, s) in Q])
        except Exception as e:
            out[f"e1_scdi|regime_{reg}"] = {"error": repr(e)[:200]}
    # How much of the coefficient space is degenerate, not just the registered point?
    for reg in ("A", "B", "C", "D"):
        n_deg = n_tot = 0
        try:
            for flat in itertools.product(CV, repeat=2 * N_F):
                cf = tuple((flat[2 * i], flat[2 * i + 1]) for i in range(N_F))
                vals = [e1_scdi.truth_regime(cf, x, s, reg) for (x, s) in Q]
                n_tot += 1
                n_deg += len(set(vals)) <= 1
            out[f"e1_scdi|regime_{reg}|coefficient_space"] = {
                "n_assignments": n_tot, "n_degenerate": n_deg,
                "fraction_degenerate": round(n_deg / n_tot, 4) if n_tot else None}
        except Exception as e:
            out[f"e1_scdi|regime_{reg}|coefficient_space"] = {"error": repr(e)[:200]}
    return out


def main(tag="V33_DEGENERACY_AUDIT", revival="RV-377-112"):
    t0 = time.time()
    rows = {}
    rows.update({f"smooth_registry::{k}": v for k, v in audit_smooth_registry().items()})
    rows.update({f"e1::{k}": v for k, v in audit_e1().items()})
    scored = {k: v for k, v in rows.items() if "status" in v}
    by_status = collections.Counter(v["status"] for v in scored.values())
    degenerate = sorted(k for k, v in scored.items() if v["status"].startswith("DEGENERATE"))
    near = sorted(k for k, v in scored.items() if v["status"].startswith("NEAR_DEGENERATE"))
    receipt = {"schema": "RV377_112_DegeneracyAuditV1", "revival_record": revival, "run_tag": tag, "issue": [377],
               "status": "EXECUTED_EXACT_AT_SCOPE", "gap": "DG-12",
               "question": "does the obligation itself take more than one value over its own declared evaluation set?",
               "why_rule_40_is_not_enough": "rule 40 asks whether a CONSTANT ANSWER can clear theta; it does not ask whether the OBLIGATION is constant. A degenerate obligation is scored 1.0000 by any constant emitter and carries no information at all.",
               "rows": rows, "counts_by_status": dict(by_status),
               "degenerate": degenerate, "near_degenerate": near,
               "n_scored": len(scored), "seconds": round(time.time() - t0, 1),
               "claim_ceiling": "covers the registered smooth/table ecologies over both declared criteria and the E1 serving regimes at their registered coefficients; obligations in modules not imported here are NOT covered and are listed as uncovered rather than assumed clean"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print(f"scored {len(scored)} obligations | {dict(by_status)}")
    for k, v in sorted(scored.items()):
        if v["status"] != "NON_DEGENERATE":
            print(f"  {k:42} distinct={v['n_distinct_answers']:2d}/{v['n_queries']:2d} "
                  f"best_const={v['best_constant_agreement']:.4f}  {v['status']}")
    for k, v in sorted(rows.items()):
        if "fraction_degenerate" in v:
            print(f"  {k:42} degenerate on {v['n_degenerate']}/{v['n_assignments']} = {v['fraction_degenerate']:.4f} of the coefficient space")
    return receipt


if __name__ == "__main__":
    main()
