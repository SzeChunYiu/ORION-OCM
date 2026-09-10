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
            rows.append({
                "motifs": m, "tokens_k": k, "target_len": 2 * k,
                "canonical_arrangements": A,
                "distance1_cover_per_train_item": cover,
                "max_train_n_leaving_d2_room": max_train_for_novelty,
                "guided_position_estimate": g,
                "interleave_return_2g": 2 * g,
                "baseline_index_range": [b_min, b_max],
                "mechanism_feasible": 2 * g <= b_max,
                "novelty_feasible": max_train_for_novelty >= 10,
                "BOTH": bool(2 * g <= b_max and max_train_for_novelty >= 10),
            })

    both = [r for r in rows if r["BOTH"]]
    out = {"schema": "OCM_M2_ARRANGEMENT_FEASIBILITY_V1",
           "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "grammar": {"primitives": list(M.PRIMITIVES), "max_length": 8,
                       "cumulative_index_by_length": cum},
           "rows": rows,
           "feasible_configurations": both,
           "verdict": ("ARRANGEMENT_GENERALISATION_TESTABLE" if both
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
    print("\nVERDICT:", out["verdict"], "| feasible configs:", len(both))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
