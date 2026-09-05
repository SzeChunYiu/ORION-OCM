#!/usr/bin/env python3
"""Same-host engineering benchmark; represented solver equality is checked separately.

Synthetic sparse and three-tail/two-head conjunction graphs model structural workloads,
not cognition. Run at each revision, preserving both output files.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ocm.evaluation.scaling import synthetic_space
from ocm.kso.navigation_sparse import sparse_navigation_matrix, sparse_fixed_point_certified
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace


def measure(call, repeats):
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        result = call()
        samples.append(time.perf_counter() - started)
    return result, {"median_s": statistics.median(samples), "samples_s": samples}


def conjunctive_space(n):
    return KnowledgeSpace(tuple(Atom(f"v{i}", "claim") for i in range(n)), tuple(
        Hyperedge(f"e{i}", (f"v{i}", f"v{(i+1)%n}", f"v{(i+7)%n}"),
                  (f"v{(i+17)%n}", f"v{(i+101)%n}"), "SUPPORT",
                  head_weights=(Fraction(1), Fraction(3))) for i in range(n)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sizes", default="4096,16384")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("repeats must be positive")
    rows = []
    for n in map(int, args.sizes.split(",")):
        if n < 128:
            parser.error("sizes must be at least 128")
        for kind, construct in (("sparse", lambda: synthetic_space(n, seed=20260904)),
                                ("conjunctive", lambda: conjunctive_space(n))):
            ks = construct()
            matrix, build = measure(lambda: sparse_navigation_matrix(ks), args.repeats)
            seed = [1.0 if i == 0 else 0.0 for i in range(n)]
            result, solve = measure(lambda: sparse_fixed_point_certified(matrix, seed, 1 / 3), args.repeats)
            ks.atom_map(); ks.edge_map(); ks.incident_edges("v0"); ks.outgoing_edges("v0")
            def digest(value):
                return hashlib.sha256(json.dumps(value, default=str, sort_keys=True).encode()).hexdigest()
            row = {"kind": kind, "atoms": n, "edges": len(ks.hyperedges),
                   "incidences": matrix.incidences, "matrix_build": build, "certified_solve": solve,
                   "index_storage": ks.index_resources().as_dict(),
                   "semantic_controls": {"graph_digest": ks.digest(), "matrix_digest": digest(asdict(matrix)),
                       "activation_digest": digest(result.activation), "iterations": result.iterations,
                       "residual_l1": str(result.residual_l1), "contraction": str(result.contraction),
                       "error_bound_l1": str(result.error_bound_l1)}}
            rows.append(row)
            print(json.dumps({"kind": kind, "atoms": n, "solve_median_s": solve["median_s"]}), flush=True)
    data = {"study": "KSO_SPARSE_CERTIFICATE_CONTINUATION_V2", "authority": "engineering reference workload only",
            "python": sys.version, "platform": platform.platform(),
            "parent_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in (ROOT / "src/ocm/kso").glob("*.py")}, "rows": rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
