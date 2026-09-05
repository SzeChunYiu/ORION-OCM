"""Independent dense Fraction reconstruction of the sparse dyadic certificate.

Run from the repo: PYTHONPATH=src python tools/kso_sparse_independent_review_v2.py
This is an internal post-implementation reference check, not protected evaluation.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import random
import sys

from ocm.kso.navigation_sparse import SparseMatrix, _DyadicSystem


def review():
    rng = random.Random(76549)
    cells = 0
    for n in range(1, 9):
        for case in range(80):
            incoming = tuple(tuple((i, float(F(rng.randrange(0, 13), 2 ** rng.randrange(0, 20))))
                                   for i in range(n) if rng.randrange(3)) for j in range(n))
            seed = tuple(float(F(rng.randrange(0, 13), 2 ** rng.randrange(0, 20))) for _ in range(n))
            activation = tuple(float(F(rng.randrange(0, 13), 2 ** rng.randrange(0, 20))) for _ in range(n))
            alpha = float(F(rng.randrange(1, 32), 32))
            matrix = SparseMatrix(tuple(map(str, range(n))), incoming, sum(map(len, incoming)))
            system = _DyadicSystem(matrix, seed, alpha)
            dense = [[F(0) for j in range(n)] for i in range(n)]
            for j, row in enumerate(incoming):
                for i, weight in row:
                    dense[i][j] += F(weight)
            output = [F(alpha) * F(seed[j]) + (1 - F(alpha)) *
                      sum((F(activation[i]) * dense[i][j] for i in range(n)), F(0))
                      for j in range(n)]
            residual = sum((abs(output[j] - F(activation[j])) for j in range(n)), F(0))
            contraction = (1 - F(alpha)) * max(map(sum, dense))
            if residual != system.residual(activation) or contraction != system.contraction:
                raise AssertionError(f"exact dense reconstruction mismatch at n={n}, case={case}")
            cells += 1
    root = Path(__file__).resolve().parents[1]
    sources = (root / "src/ocm/kso/navigation_sparse.py", Path(__file__).resolve())
    return {
        "schema": "KSO_SPARSE_INDEPENDENT_REVIEW_V2",
        "status": "PASS",
        "review_kind": "INTERNAL_POST_IMPLEMENTATION_INDEPENDENT_ORACLE_RECONSTRUCTION",
        "random_seed": 76549,
        "matrix_dimensions": [1, 8],
        "cases_per_dimension": 80,
        "exact_comparisons": cells,
        "checked": ["residual_l1", "contraction"],
        "method": "Construct dense Fraction matrix from incoming incidences; evaluate alpha*seed+(1-alpha)*activation*P entrywise and compare exact L1 residual and outgoing-row-sum contraction",
        "excluded": ["original rational-to-float conversion error", "external scientific validation", "universal proof by random tests"],
        "source_sha256": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    }


if __name__ == "__main__":
    try:
        print(json.dumps(review(), indent=2, sort_keys=True))
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        sys.exit(1)
