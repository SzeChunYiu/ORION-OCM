#!/usr/bin/env python3
"""Feasibility region for testing ARRANGEMENT generalisation in a fixed grammar.

Two constraints must hold simultaneously to test whether a developmental prior
generalises to novel ARRANGEMENTS (distance d >= 2) rather than merely interpolating:

  NOVELTY EXISTS.  Targets at edit distance >= 2 from every training arrangement must
  exist. Each training arrangement of k tokens over m motifs covers k*(m-1)+1 arrangements
  within distance 1, so novelty requires

        train_n * (k*(m-1) + 1)  <  A(m,k)

  where A(m,k) is the number of CANONICAL k-token arrangements (those that are the
  first-in-enumeration program for their normal form).

  MECHANISM WORKS.  The guided stream must reach a target's composition before the
  baseline does. A k-token word over the top-ranked motifs sits at roughly

        g(m,k) ~ sum_{i<=k} T^i   restricted to motif ranks, ~ m^k for the k-block

  and the interleave returns at ~2g, so the mechanism needs 2*g <= b, where b is the
  target's baseline index (bounded above by the cumulative grammar size).

The two pull in opposite directions in k: raising k creates arrangement room (good for
novelty) and deepens the guided search (bad for the mechanism). This script maps where
both hold, using the MEASURED canonical fraction rather than an assumed one.
"""
from __future__ import annotations
import argparse, json, sys
from itertools import product
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--recovery-c", type=float, default=5.0,
                    help="measured constant: train_n >= c*m is needed for the learner to "
                         "recover the motif set. E5 used 35 train for 6 motifs (c=5.8), "
                         "E8 66 for 7 (c=9.4); c=5 is the LENIENT end of the observed range.")
    a = ap.parse_args()
    sys.path.insert(0, str(Path(a.repo) / "src"))
    import ocm.learning.methods as M

    canonical = {}
    slot = 0
    cum = {}
    for L in range(9):
        for prog in product(M.PRIMITIVES, repeat=L):
            slot += 1
            nf = M.normal_form(prog)
            if nf not in canonical:
                canonical[nf] = (prog, slot)
        cum[L] = slot

    import random
    rng = random.Random(7)
    rows = []
    for m in (4, 6, 8, 10, 12, 14):
        pool = [p for p in product(M.PRIMITIVES, repeat=2)]
        if m > len(pool):
            continue
        motifs = tuple(sorted(rng.sample(pool, m)))
        for k in (2, 3, 4):
            if 2 * k > 8:
                continue
            A = 0
            for combo in product(range(m), repeat=k):
                prog = tuple(op for i in combo for op in motifs[i])
                if len(prog) > 8:
                    continue
                if canonical.get(M.normal_form(prog), (None,))[0] == prog:
                    A += 1
            if A == 0:
                continue
            # smallest train_n that still leaves distance-2 room, and the largest that
            # still permits it
            cover = k * (m - 1) + 1
            max_train_for_novelty = max(0, (A - 1) // cover)
            # mechanism: guided position for a k-token word over m ranked motifs
            g = sum(min(m, 20) ** i for i in range(1, k + 1))
            b_max = cum[2 * k] if 2 * k <= 8 else cum[8]
            b_min = cum[2 * k - 1] + 1 if 2 * k - 1 >= 0 else 1
            train_needed = a.recovery_c * m          # RECOVERY constraint (measured)
            rows.append({
                "recovery_train_n_needed": round(train_needed, 1),
                "recovery_feasible": max_train_for_novelty >= train_needed,
                "motifs": m, "tokens_k": k, "target_len": 2 * k,
                "canonical_arrangements": A,
                "distance1_cover_per_train_item": cover,
                "max_train_n_leaving_d2_room": max_train_for_novelty,
                "guided_position_estimate": g,
                "interleave_return_2g": 2 * g,
                "baseline_index_range": [b_min, b_max],
                "binding_bound_b_min": b_min,
                "mechanism_feasible": 2 * g <= b_min,
                "novelty_feasible": max_train_for_novelty >= 10,
                "BOTH": bool(2 * g <= b_min and max_train_for_novelty >= 10),
                "ALL_THREE": bool(2 * g <= b_min and max_train_for_novelty >= train_needed),
            })

    both = [r for r in rows if r["BOTH"]]
    allthree = [r for r in rows if r["ALL_THREE"]]
    out = {"schema": "OCM_M2_ARRANGEMENT_FEASIBILITY_V1",
           "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "grammar": {"primitives": list(M.PRIMITIVES), "max_length": 8,
                       "cumulative_index_by_length": cum},
           "rows": rows,
           "feasible_configurations_novelty_and_depth": both,
           "feasible_configurations_ALL_THREE": allthree,
           "third_constraint": ("RECOVERY: the learner must see enough training "
                                "arrangements to mine the motif set, train_n >= c*m. This "
                                "fights NOVELTY, which needs train_n small enough to leave "
                                "distance-2 room. Omitting it is why the m=12,k=3,train_n=18 "
                                "test failed: feasible on novelty and depth, starved on recovery."),
           "verdict": ("ARRANGEMENT_GENERALISATION_TESTABLE" if allthree
                       else "ARRANGEMENT_GENERALISATION_NOT_TESTABLE_IN_THIS_GRAMMAR"),
           "reading": ("novelty needs arrangement room, which grows with k; the mechanism "
                       "needs shallow guided position, which decays with k. Where the two "
                       "windows do not overlap, d>=2 generalisation cannot be tested at all "
                       "-- the claim is bounded by the substrate, not by the experiment")}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print("%-7s %-4s %-8s %-9s %-14s %-10s %-9s %s" % ("motifs", "k", "len", "arrang.",
          "max_train_d2", "2g", "b_max", "BOTH"))
    for r in rows:
        print("%-7s %-4s %-8s %-9s %-14s %-10s %-9s %s" % (
            r["motifs"], r["tokens_k"], r["target_len"], r["canonical_arrangements"],
            r["max_train_n_leaving_d2_room"], r["interleave_return_2g"],
            r["baseline_index_range"][1], r["BOTH"]))
    print()
    print("%-7s %-4s %-9s %-14s %-14s %-8s %s" % ("motifs","k","arrang.","max_train_d2",
          "recovery_need","2g<=b","ALL_THREE"))
    for r in rows:
        print("%-7s %-4s %-9s %-14s %-14s %-8s %s" % (
            r["motifs"], r["tokens_k"], r["canonical_arrangements"],
            r["max_train_n_leaving_d2_room"], r["recovery_train_n_needed"],
            r["mechanism_feasible"], r["ALL_THREE"]))
    print("\nVERDICT:", out["verdict"])
    print("novelty+depth feasible:", len(both), "| ALL THREE feasible:", len(allthree))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
