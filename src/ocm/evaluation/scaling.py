"""Scaling / resource baseline (M2 §13) on synthetic typed hypergraphs.

Sizes 10², 10³, 10⁴ (10⁵ when the host budget allows) — *engineering* baselines only, not
cognition benchmarks.  Per size: build time, sparse navigation (iterations, incidences, wall, CPU,
peak memory), one revocation + reopening report, one admission.  Exact solver is run only where
feasible (n ≤ 60) to certify the sparse path.  Results are a resource vector per stage plus wall
and peak-RSS numbers; nothing here is a claim.
"""
from __future__ import annotations

import argparse
import json
import random
import resource
import sys
import time
from fractions import Fraction

from ocm.kso import admission as AD
from ocm.kso import navigation as N
from ocm.kso import navigation_sparse as NS
from ocm.kso import revocation as RV
from ocm.kso import space as S
from ocm.kso.warrant import WarrantProfile


def synthetic_space(n: int, *, seed: int, degree: int = 3, n_evidence: int | None = None) -> S.KnowledgeSpace:
    rng = random.Random(seed)
    n_ev = n_evidence or max(8, n // 4)
    types = ("claim", "procedure", "constraint", "observation")
    rels = ("DEPENDENCE", "SUPPORT", "CONSTRAINT", "RESTRICTION")
    atoms = tuple(S.Atom(f"v{i}", rng.choice(types), WarrantProfile.certified([frozenset({rng.randrange(n_ev)})]) if rng.random() < 0.7 else WarrantProfile.one()) for i in range(n))
    edges = []
    for j in range(n * degree):
        nt = 2 if rng.random() < 0.15 else 1
        tails = tuple(f"v{rng.randrange(n)}" for _ in range(nt))
        if len(set(tails)) != nt:
            continue
        head = f"v{rng.randrange(n)}"
        if head in tails:
            continue
        edges.append(S.Hyperedge(f"e{j}", tails, (head,), rng.choice(rels), Fraction(rng.randint(1, 3))))
    return S.KnowledgeSpace(atoms, tuple(edges))


def _rss_mb() -> float:
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return ru / 1024.0 / (1024.0 if sys.platform == "darwin" else 1.0)


def run_size(n: int, *, seed: int = 20260904, skip_admit_above: int = 1000) -> dict:
    t0 = time.perf_counter()
    c0 = time.process_time()
    ks = synthetic_space(n, seed=seed)
    t_build = time.perf_counter() - t0
    seed_v = [Fraction(0)] * n
    seed_v[0] = Fraction(1)
    t1 = time.perf_counter()
    act, iters, inc = NS.sparse_activation(ks, seed_v, 1 / 3, tol=1e-10)
    t_nav = time.perf_counter() - t1
    exact_agreement = None
    if n <= 60:
        exact_agreement = NS.check_sparse_agrees_with_exact(ks, seed_v, Fraction(1, 3))["max_abs_error"]
    t2 = time.perf_counter()
    rep = RV.reopening_report(ks, (), (0,))
    t_reopen = time.perf_counter() - t2
    t3 = time.perf_counter()
    if n > skip_admit_above:
        return _finish(n, ks, inc, t_build, iters, t_nav, act, exact_agreement, rep, t_reopen, None, "SKIPPED: exceeds configured skip_admit_above", c0)
    try:
        AD.admit(ks, S.Atom("new", "claim", WarrantProfile.of({0})), (S.Hyperedge("newe", (ks.ids[1],), ("new",), "SUPPORT"),), "INSTRUCTION")
        t_admit = time.perf_counter() - t3
        admit_note = "exact positive matrix support (all sizes, KS-T05)"
    except Exception as exc:  # noqa: BLE001
        t_admit = time.perf_counter() - t3
        admit_note = f"{type(exc).__name__}"
    return _finish(n, ks, inc, t_build, iters, t_nav, act, exact_agreement, rep, t_reopen, t_admit, admit_note, c0)


def _finish(n, ks, inc, t_build, iters, t_nav, act, exact_agreement, rep, t_reopen, t_admit, admit_note, c0):
    return {
        "atoms": n,
        "hyperedges": len(ks.hyperedges),
        "incidences": inc,
        "build_s": round(t_build, 4),
        "navigation": {"iterations": iters, "wall_s": round(t_nav, 4), "active_atoms": sum(1 for v in act.values() if v > 0)},
        "sparse_vs_exact_max_error": exact_agreement,
        "reopening": {"wall_s": round(t_reopen, 4), "cone": len(rep.cone), "reopen": len(rep.reopen), "unaffected": len(rep.unaffected)},
        "admission": {"wall_s": None if t_admit is None else round(t_admit, 4), "note": admit_note},
        "cpu_s": round(time.process_time() - c0, 4),
        "peak_rss_mb": round(_rss_mb(), 1),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", default="100,1000,10000")
    p.add_argument("--skip-admit-above", type=int, default=1000)
    p.add_argument("--out", default=None)
    a = p.parse_args(argv)
    rows = []
    for n in [int(x) for x in a.sizes.split(",")]:
        rows.append(run_size(n, skip_admit_above=a.skip_admit_above))
        print(json.dumps(rows[-1]))
    out = {"study": "M2_SCALING_BASELINE_V1", "authority": "engineering baseline on synthetic hypergraphs; not a cognition benchmark; no claim", "rows": rows}
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
