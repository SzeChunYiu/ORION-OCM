#!/usr/bin/env python3
"""Check solver equality against a Git source revision and measure traced allocations.

This executes the named, locally available repository source as the baseline. Only
use a trusted revision. It does not fetch or modify any Git object or receipt.
"""
import argparse
import importlib.util
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ocm.evaluation.scaling import synthetic_space
from ocm.kso.navigation_sparse import SparseMatrix, sparse_fixed_point_certified, sparse_navigation_matrix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", default="479e781")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    baseline_commit = subprocess.check_output(["git", "rev-parse", "--verify", f"{args.baseline_ref}^{{commit}}"], cwd=ROOT, text=True).strip()
    source = subprocess.check_output(["git", "show", f"{baseline_commit}:src/ocm/kso/navigation_sparse.py"], cwd=ROOT, text=True)
    spec = importlib.util.spec_from_loader("ocm.kso._previous_sparse", loader=None)
    old = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = old
    exec(compile(source, f"{baseline_commit}/navigation_sparse.py", "exec"), old.__dict__)
    rng = random.Random(20260905)
    for case in range(256):
        n = rng.randint(1, 9)
        incoming = [[] for _ in range(n)]
        for i in range(n):
            for _ in range(4):
                incoming[rng.randrange(n)].append((i, rng.choice((0., .025, .1, .125))))
        matrix = SparseMatrix(tuple(map(str, range(n))), tuple(tuple(row) for row in incoming), 4 * n)
        seed = [rng.random() / n for _ in range(n)]
        alpha = rng.choice((.01, .07, 1 / 3, .75, 1.))
        current = sparse_fixed_point_certified(matrix, seed, alpha)
        previous = old.sparse_fixed_point_certified(matrix, seed, alpha)
        for field in ("activation", "iterations", "residual_l1", "contraction", "error_bound_l1"):
            if getattr(current, field) != getattr(previous, field):
                raise RuntimeError(f"case {case} changed {field}")
    ks = synthetic_space(4096, seed=20260904)
    matrix = sparse_navigation_matrix(ks)
    seed = [1.0] + [0.0] * 4095
    peak = {}
    for name, function in (("before", old.sparse_fixed_point_certified), ("after", sparse_fixed_point_certified)):
        tracemalloc.start()
        function(matrix, seed, 1 / 3)
        _, peak[name] = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    data = {"study": "REPRESENTED_SPARSE_SOLVER_EQUALITY_V2", "baseline_commit": baseline_commit,
            "random_seed": 20260905, "cases": 256, "all_fields_exactly_equal": True,
            "current_solver_sha256": hashlib.sha256((ROOT / "src/ocm/kso/navigation_sparse.py").read_bytes()).hexdigest(),
            "python": sys.version,
            "solver_peak_traced_bytes_4096_sparse": peak,
            "memory_scope": "Python tracemalloc allocations within solver only; matrix and graph pre-exist; not process RSS"}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(data))


if __name__ == "__main__":
    main()
