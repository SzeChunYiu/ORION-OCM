#!/usr/bin/env python3
"""What substrate makes d>=2 arrangement generalisation testable at all?

ARRANGEMENT_OBSTRUCTION established 0/18 feasible configurations in the registered
grammar (P=4 primitives, max length 8). MDL selection removes ONE of the causes -- it no
longer requires substring-disjointness, so the alphabet is no longer capped at
m(l-1) <= P^2 -- but that does not automatically make d>=2 testable. This derives the
condition in closed form and solves it for P.

DEPTH. A library covering m motifs needs ~m fragments, so the guided token set is
T ~ m + P and a k-token word sits at g ~ (m+P)^k. The interleave returns at 2g, and
admission needs 2g <= b_min, the SMALLEST baseline index in the target-length band. For
targets of length 2k, b_min is the cumulative grammar size through length 2k-1:

        b_min(2k) = (P^(2k) - 1)/(P - 1)  ~  P^(2k)/(P-1)

    depth:      2 (m+P)^k  <=  P^(2k)/(P-1)
                (m+P)      <=  P^2 / (2(P-1))^(1/k)

NOVELTY + RECOVERY. Novelty needs train_n*(k(m-1)+1) < A(m,k) ~ f*m^k with f the measured
canonical fraction; recovery needs train_n >= c*m. Eliminating train_n:

        recovery+novelty:   m^(k-2)  >=  c*k / f

Both must hold. The first caps m from above and tightens as P falls; the second bounds m
from below and tightens as k falls. The registered grammar has P=4.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--c", type=float, default=3.6,
                    help="recovery constant train_n >= c*m. MDL measured c=3.6 on E7 "
                         "(25 train, 7/7 recovered); frequency needed 5-9.")
    ap.add_argument("--f", type=float, default=0.22,
                    help="canonical-arrangement fraction, measured A(12,4)=4642/20736")
    a = ap.parse_args()

    rows = []
    for P in (4, 5, 6, 8, 10):
        for k in (3, 4):
            if 2 * k > 8 and P == 4:
                pass
            m_max = P ** 2 / (2 * (P - 1)) ** (1.0 / k) - P       # depth
            m_min = (a.c * k / a.f) ** (1.0 / (k - 2)) if k > 2 else float("inf")
            rows.append({
                "primitives_P": P, "tokens_k": k, "target_length": 2 * k,
                "m_max_from_depth": round(m_max, 2),
                "m_min_from_recovery_and_novelty": round(m_min, 2),
                "feasible": bool(m_max >= m_min),
                "window": round(m_max - m_min, 2),
            })

    feas = [r for r in rows if r["feasible"]]
    smallest_P = min((r["primitives_P"] for r in feas), default=None)
    out = {
        "schema": "OCM_M2_SUBSTRATE_REQUIREMENT_V1",
        "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
        "constants": {"recovery_c": a.c, "canonical_fraction_f": a.f},
        "conditions": {
            "depth": "(m+P) <= P^2 / (2(P-1))^(1/k)",
            "recovery_and_novelty": "m^(k-2) >= c*k/f",
        },
        "rows": rows,
        "feasible": feas,
        "smallest_feasible_P": smallest_P,
        "registered_grammar_P": 4,
        "verdict": ("REGISTERED_GRAMMAR_SUFFICIENT" if any(r["primitives_P"] == 4 for r in feas)
                    else "REGISTERED_GRAMMAR_INSUFFICIENT__NEEDS_P_GE_%s" % smallest_P),
        "reading": ("the obstruction survives the MDL fix: removing substring-disjointness "
                    "lifts the alphabet cap but not the DEPTH cap, which depends only on P. "
                    "d>=2 testability is a property of the SUBSTRATE, and the requirement is "
                    "a specific number of primitives, not more compute."),
    }
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print("%-4s %-4s %-8s %-14s %-14s %-9s %s" % ("P", "k", "len", "m_max(depth)",
          "m_min(rec+nov)", "window", "feasible"))
    for r in rows:
        print("%-4s %-4s %-8s %-14s %-14s %-9s %s" % (
            r["primitives_P"], r["tokens_k"], r["target_length"],
            r["m_max_from_depth"], r["m_min_from_recovery_and_novelty"],
            r["window"], r["feasible"]))
    print("\nVERDICT:", out["verdict"])
    print("smallest feasible P:", smallest_P, "| registered P = 4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
