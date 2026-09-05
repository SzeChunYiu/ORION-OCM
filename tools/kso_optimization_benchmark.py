#!/usr/bin/env python3
"""Measure structural KSO operations without changing historical milestone receipts.

Run this command on each checkout to compare source revisions on the same host:
  python tools/kso_optimization_benchmark.py --out /tmp/kso-measurement.json
The digest/receipt fields are semantic controls; timings are host observations.
"""
from __future__ import annotations

import argparse
import cProfile
import hashlib
import io
import json
import platform
import pstats
import statistics
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ocm.evaluation.scaling import synthetic_space
from ocm.kso.admission import admit
from ocm.kso.navigation import gated_closure, ungated_closure
from ocm.kso.navigation_sparse import sparse_activation
from ocm.kso.revocation import reopening_report
from ocm.kso.space import Atom, Hyperedge


def measured(fn, repeats):
    samples = []
    result = None
    for _ in range(repeats):
        begin = time.perf_counter()
        result = fn()
        samples.append(time.perf_counter() - begin)
    return result, {"median_s": statistics.median(samples), "samples_s": samples}


def run_size(n, repeats):
    ks, construction = measured(lambda: synthetic_space(n, seed=20260904), repeats)
    queries = tuple(f"v{i * (n - 1) // 127}" for i in range(128))
    _, lookup = measured(lambda: tuple(ks.atom(x).atom_id for x in queries), repeats)
    _, incident = measured(lambda: tuple(len(ks.incident_edges(x)) for x in queries), repeats)
    closure, walk = measured(lambda: ungated_closure(ks, ("v0",)), repeats)
    live_closure, gated = measured(lambda: gated_closure(ks, ("v0",), (0,)), repeats)
    report, reopening = measured(lambda: reopening_report(ks, (), (0,)), repeats)
    seed = [Fraction(0)] * n
    seed[0] = Fraction(1)
    nav, navigation = measured(lambda: sparse_activation(ks, seed, 1 / 3), repeats)
    result, admission = measured(
        lambda: admit(ks, Atom("new", "claim"),
                      (Hyperedge("newe", ("v1",), ("new",), "SUPPORT"),), "INSTRUCTION"),
        repeats,
    )
    new, receipt = result
    def digest(value):
        return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
    return {
        "atoms": n, "edges": len(ks.hyperedges), "construction": construction,
        "atom_lookup_128": lookup, "incident_lookup_128": incident,
        "ungated_closure": walk, "gated_closure": gated,
        "reopening": reopening, "sparse_navigation": navigation, "admission": admission,
        "semantic_controls": {
            "space_digest": ks.digest(), "admitted_digest": new.digest(),
            "closure_digest": digest(sorted(closure)), "gated_closure_digest": digest(sorted(live_closure)),
            "reopening": report.as_dict(), "navigation_digest": digest(nav[0]),
            "navigation_iterations": nav[1], "navigation_incidences": nav[2],
            "admission_resources": receipt.resources.as_dict(),
            "admission_reachable": receipt.reachable_by_navigation,
        },
        "materialized_indexes": ks.index_resources().as_dict() if hasattr(ks, "index_resources") else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", default="256,1024,4096")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--profile", action="store_true")
    args = parser.parse_args()
    if args.repeats < 1 or any(int(n) < 2 for n in args.sizes.split(",")):
        parser.error("positive repeats and sizes >= 2 are required")
    rows = []
    for n in map(int, args.sizes.split(",")):
        rows.append(run_size(n, args.repeats))
        print(json.dumps({"atoms": n, "admission_median_s": rows[-1]["admission"]["median_s"]}), flush=True)
    profile = None
    if args.profile:
        ks = synthetic_space(max(map(int, args.sizes.split(","))), seed=20260904)
        pr = cProfile.Profile()
        pr.runcall(admit, ks, Atom("new", "claim"),
                   (Hyperedge("newe", ("v1",), ("new",), "SUPPORT"),), "INSTRUCTION")
        output = io.StringIO()
        pstats.Stats(pr, stream=output).sort_stats("cumulative").print_stats(16)
        profile = output.getvalue()
    data = {
        "study": "KSO_STRUCTURAL_OPTIMIZATION_V1", "authority": "same-host engineering measurements; no cognition or novelty claim",
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": sys.version, "platform": platform.platform(),
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted((ROOT / "src/ocm/kso").glob("*.py"))},
        "rows": rows, "admission_profile": profile,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
