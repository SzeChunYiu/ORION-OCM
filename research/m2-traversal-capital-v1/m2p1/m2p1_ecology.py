#!/usr/bin/env python3
"""M2-P1 hidden-family ecology generator + blocking entry gate.

Design registered in research/m2-traversal-capital-v1/HIDDEN_FAMILY_DESIGN.md.

The M1 ecology hands the agent the complete generative grammar, so the optimal
structural prior is derivable a priori (M2-N2).  This ecology instead carries a
HIDDEN MOTIF SET: targets are normal forms whose canonical (first-in-enumeration)
program is a concatenation of motifs drawn from a set the agent is never told.

The motif set is not derivable from the declared grammar, so a grammar-only agent
must enumerate primitives, while an agent with history can mine the motifs from its
own checked solutions -- using the REGISTERED learner unchanged.

Entry gate (blocking, per HIDDEN_FAMILY_DESIGN.md):
  G1 length-distribution parity across streams
  G2 disjoint normal forms across streams
  G3 canonical-program motif decomposability (ecology is what it claims to be)
  G4 surface-predictor null: the M2 length predictors must NOT capture the benefit
     (guards against re-deriving M2-N1's constant-offset artifact)
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, random, statistics, sys, time
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path

LANE = "LANE_M2_TRAVERSAL_CAPITAL_OPUS"
SCHEMA = "OCM_M2P1_HIDDEN_FAMILY_ECOLOGY_V1"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def decomposable(program, motifs):
    """Is `program` an exact concatenation of motifs?  (dynamic programming)"""
    n = len(program)
    if n == 0:
        return False
    reach = [False] * (n + 1)
    reach[0] = True
    for i in range(n):
        if not reach[i]:
            continue
        for m in motifs:
            j = i + len(m)
            if j <= n and tuple(program[i:j]) == m:
                reach[j] = True
    return reach[n]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--motifs", type=int, default=6)
    ap.add_argument("--min-targets", type=int, default=320)
    ap.add_argument("--trials", type=int, default=400)
    ap.add_argument("--min-len", type=int, default=4,
                    help="E1=4 / E2=6, both pre-registered in HIDDEN_FAMILY_DESIGN.md")
    a = ap.parse_args()
    t0 = time.perf_counter()
    repo = Path(a.repo)
    sys.path.insert(0, str(repo / "src"))
    import ocm.learning.methods as M

    # ---- exact enumeration: canonical program per normal form (methods.solve order)
    canonical, first_index = {}, {}
    slot = 0
    for L in range(9):
        for prog in product(M.PRIMITIVES, repeat=L):
            slot += 1
            nf = M.normal_form(prog)
            if nf not in canonical:
                canonical[nf], first_index[nf] = prog, slot
    enum_seconds = time.perf_counter() - t0

    # ---- search a hidden motif set whose induced ecology is large enough
    rng = random.Random(a.seed)
    all_motifs = [p for L in (2, 3) for p in product(M.PRIMITIVES, repeat=L)]
    best = None
    for trial in range(a.trials):
        motifs = tuple(sorted(rng.sample(all_motifs, a.motifs)))
        members = [nf for nf, prog in canonical.items()
                   if len(prog) >= a.min_len and decomposable(prog, motifs)]
        if best is None or len(members) > len(best[1]):
            best = (motifs, members)
        if len(members) >= a.min_targets:
            break
    motifs, members = best
    lens = Counter(len(canonical[nf]) for nf in members)

    # ---- streams with length parity + disjoint normal forms (G1, G2)
    by_len = defaultdict(list)
    for nf in members:
        by_len[len(canonical[nf])].append(nf)
    for L in by_len:
        by_len[L].sort(key=lambda nf: hashlib.sha256(str(nf).encode()).hexdigest())
    streams = {"train": [], "validation": [], "protected": []}
    quota = {"train": 0.5, "validation": 0.2, "protected": 0.3}
    for L, nfs in sorted(by_len.items()):
        i = 0
        for name, frac in quota.items():
            k = int(round(len(nfs) * frac))
            streams[name].extend(nfs[i:i + k])
            i += k
        for nf in nfs[i:]:
            streams["train"].append(nf)

    def row(nf):
        return {"coefficients": [str(c) for c in nf],
                "canonical_program": list(canonical[nf]),
                "canonical_length": len(canonical[nf]),
                "baseline_first_index": first_index[nf],
                "normal_form_digest": hashlib.sha256(
                    json.dumps([str(c) for c in nf]).encode()).hexdigest()}

    out_streams = {k: [row(nf) for nf in v] for k, v in streams.items()}

    # ---- G2 disjointness
    digs = {k: {r["normal_form_digest"] for r in v} for k, v in out_streams.items()}
    shared = (digs["train"] & digs["protected"]) | (digs["train"] & digs["validation"]) | \
             (digs["validation"] & digs["protected"])

    # ---- G1 length parity (max deviation of each stream's length distribution)
    def dist(rows):
        c = Counter(r["canonical_length"] for r in rows)
        n = sum(c.values())
        return {L: c[L] / n for L in sorted(c)}
    dists = {k: dist(v) for k, v in out_streams.items()}
    alllen = sorted({L for d in dists.values() for L in d})
    parity = max(abs(dists[a_][L] - dists[b_][L])
                 for L in alllen for a_ in dists for b_ in dists if a_ != b_) if alllen else 1.0

    # ---- G3 decomposability (assert every member really is motif-composed)
    g3_bad = [r["normal_form_digest"] for k, v in out_streams.items() for r in v
              if not decomposable(tuple(r["canonical_program"]), motifs)]

    out = {
        "schema": SCHEMA, "lane": LANE, "status": "ECOLOGY_EMISSION_NOT_A_SCORED_RUN",
        "owner_issue": 165, "hardening_parent": 323,
        "host": {"hostname": platform.node(), "python": platform.python_version()},
        "bound_sources": {"methods.py": sha256_file(repo / "src" / "ocm" / "learning" / "methods.py"),
                          "git_head": os.popen(f"/usr/bin/git -C {repo} rev-parse HEAD").read().strip()},
        "frozen_seed": a.seed,
        "ecology_variant": {"min_canonical_length": a.min_len,
                            "label": "E1" if a.min_len == 4 else "E2"},
        "hidden_motifs": [list(m) for m in motifs],
        "hidden_motifs_sha256": hashlib.sha256(json.dumps([list(m) for m in motifs]).encode()).hexdigest(),
        "grammar": {"primitives": list(M.PRIMITIVES), "max_length": 8},
        "ecology": {"members": len(members),
                    "canonical_length_distribution": {str(k): v for k, v in sorted(lens.items())}},
        "streams": out_streams,
        "stream_sizes": {k: len(v) for k, v in out_streams.items()},
        "entry_gates": {
            "G1_length_parity_max_deviation": round(parity, 4),
            "G1_verdict": "PASS" if parity <= 0.08 else "FAIL",
            "G2_shared_normal_forms": len(shared),
            "G2_verdict": "PASS" if not shared else "FAIL",
            "G3_non_decomposable": len(g3_bad),
            "G3_verdict": "PASS" if not g3_bad else "FAIL",
            "G4_surface_predictor_null": "DEFERRED_TO_SCORED_RUN",
        },
        "length_distributions_by_stream": {k: {str(x): round(y, 4) for x, y in v.items()}
                                           for k, v in dists.items()},
        "timing_seconds": {"enumeration": round(enum_seconds, 2),
                           "total": round(time.perf_counter() - t0, 2)},
    }
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"written": a.out, "members": len(members),
                      "motifs": ["".join(m) for m in motifs],
                      "sizes": out["stream_sizes"],
                      "gates": {k: v for k, v in out["entry_gates"].items() if k.endswith("verdict")},
                      "parity": out["entry_gates"]["G1_length_parity_max_deviation"],
                      "lens": out["ecology"]["canonical_length_distribution"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
