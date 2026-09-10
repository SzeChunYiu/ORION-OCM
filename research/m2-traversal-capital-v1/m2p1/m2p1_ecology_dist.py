#!/usr/bin/env python3
"""Distance-graded ecology: the decisive test P3 from THEORY_GAPS.md.

The hostile review found that 96 of 100 protected targets in E5/E6/E8 are ONE motif
substitution from a training target, with part coverage 1.00. So every prior claim is a
point estimate at d = 1, the easiest non-trivial transfer.

This generator controls that distance explicitly. Targets are k-motif compositions over a
shared motif alphabet; the protected stream is filtered so that every target's motif
sequence is at Levenshtein distance >= D_MIN from EVERY training sequence.

  d = 1  interpolation: one part swapped from something already solved
  d = 2  novel arrangement of known parts, two positions from anything seen
  d = 3  strongly novel arrangement

Part coverage is held at 1.0 by construction in every grade -- the SAME motifs are
available -- so the only thing varying is the ARRANGEMENT distance. That isolates
"reuse of parts" from "generalisation over arrangements", which is exactly the
distinction the hostile review said was untested.

Registered prediction (P3): a mechanism that only interpolates shows benefit collapsing
at d = 2. A developmental mechanism shows benefit decaying gracefully but staying
positive.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, random, sys, time
from collections import Counter
from itertools import product
from pathlib import Path


def seq_edit(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--motifs", type=int, default=12)
    ap.add_argument("--tokens", type=int, default=3, help="motifs per target (fixed)")
    ap.add_argument("--d-min", type=int, required=True, help="min arrangement distance train->protected")
    ap.add_argument("--train-n", type=int, default=120)
    ap.add_argument("--val-n", type=int, default=30)
    ap.add_argument("--prot-n", type=int, default=60)
    a = ap.parse_args()
    t0 = time.perf_counter()
    repo = Path(a.repo)
    sys.path.insert(0, str(repo / "src"))
    import ocm.learning.methods as M

    canonical, first_index = {}, {}
    slot = 0
    for L in range(9):
        for prog in product(M.PRIMITIVES, repeat=L):
            slot += 1
            nf = M.normal_form(prog)
            if nf not in canonical:
                canonical[nf], first_index[nf] = prog, slot

    rng = random.Random(a.seed)
    # length-2 motifs are substring-disjoint by construction (no proper substring >= 2)
    pool = [p for p in product(M.PRIMITIVES, repeat=2)]
    motifs = tuple(sorted(rng.sample(pool, a.motifs)))

    # every k-token arrangement whose concatenation is the CANONICAL program of its NF
    arrangements = {}
    for combo in product(range(len(motifs)), repeat=a.tokens):
        prog = tuple(op for i in combo for op in motifs[i])
        if len(prog) > 8:
            continue
        nf = M.normal_form(prog)
        if canonical.get(nf) != prog:
            continue                      # not the canonical route to this normal form
        arrangements.setdefault(nf, combo)

    items = [(nf, c) for nf, c in arrangements.items()]
    items.sort(key=lambda x: hashlib.sha256(str(x[0]).encode()).hexdigest())
    if len(items) < a.train_n + a.val_n + a.prot_n:
        raise SystemExit(f"ECOLOGY_TOO_SMALL: {len(items)} arrangements available")

    train = items[: a.train_n]
    rest = items[a.train_n:]
    train_seqs = [c for _, c in train]

    graded, val = [], []
    for nf, c in rest:
        d = min(seq_edit(c, ts) for ts in train_seqs)
        if d >= a.d_min:
            graded.append((nf, c, d))
    if len(graded) < a.prot_n + a.val_n:
        raise SystemExit(f"INSUFFICIENT_AT_DISTANCE d>={a.d_min}: {len(graded)} found")
    val = graded[: a.val_n]
    prot = graded[a.val_n: a.val_n + a.prot_n]

    def row(nf, c, d=None):
        prog = canonical[nf]
        return {"coefficients": [str(x) for x in nf],
                "canonical_program": list(prog), "canonical_length": len(prog),
                "motif_tokens": len(c), "arrangement": list(c),
                "arrangement_distance_to_train": d,
                "baseline_first_index": first_index[nf],
                "normal_form_digest": hashlib.sha256(
                    json.dumps([str(x) for x in nf]).encode()).hexdigest()}

    streams = {"train": [row(nf, c) for nf, c in train],
               "validation": [row(nf, c, d) for nf, c, d in val],
               "protected": [row(nf, c, d) for nf, c, d in prot]}
    digs = {k: {r["normal_form_digest"] for r in v} for k, v in streams.items()}
    shared = (digs["train"] & digs["protected"]) | (digs["train"] & digs["validation"]) | \
             (digs["validation"] & digs["protected"])
    train_motifs = {i for _, c in train for i in c}
    prot_cov = sum(1 for _, c, _ in prot if all(i in train_motifs for i in c)) / len(prot)

    out = {"schema": "OCM_M2_DISTANCE_GRADED_ECOLOGY_V1",
           "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "ecology_variant": {"label": f"D{a.d_min}", "d_min": a.d_min,
                               "tokens_per_target": a.tokens},
           "host": {"hostname": platform.node(), "python": platform.python_version()},
           "frozen_seed": a.seed,
           "hidden_motifs": [list(m) for m in motifs],
           "grammar": {"primitives": list(M.PRIMITIVES), "max_length": 8},
           "registered_prediction_P3": (
               "part coverage is 1.0 by construction at every grade, so only ARRANGEMENT "
               "distance varies; interpolation-only mechanisms lose their benefit at d>=2"),
           "distance_distribution": dict(Counter(d for _, _, d in prot)),
           "protected_part_coverage": round(prot_cov, 3),
           "streams": streams,
           "stream_sizes": {k: len(v) for k, v in streams.items()},
           "entry_gates": {"G2_shared_normal_forms": len(shared),
                           "G2_verdict": "PASS" if not shared else "FAIL",
                           "G_DIST_min_observed": min(d for _, _, d in prot),
                           "G_DIST_verdict": "PASS" if min(d for _, _, d in prot) >= a.d_min else "FAIL",
                           "G_COVERAGE_all_parts_seen": prot_cov == 1.0},
           "timing_seconds": round(time.perf_counter() - t0, 2)}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"label": out["ecology_variant"]["label"],
                      "arrangements_available": len(items),
                      "sizes": out["stream_sizes"],
                      "distance_distribution": out["distance_distribution"],
                      "part_coverage": prot_cov,
                      "gates": {k: v for k, v in out["entry_gates"].items() if "verdict" in k or "COVERAGE" in k}},
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
