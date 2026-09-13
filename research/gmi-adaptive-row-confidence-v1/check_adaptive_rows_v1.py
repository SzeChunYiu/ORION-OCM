import hashlib
import json
import sys
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from row_confidence_v1 import radius, tail_upper, registered_radii, require
from visit_oracle_v1 import prefix_failure, full_bitstrings, adaptive_failure, optional_peek


def run():
    alpha, weights = F(1, 4), (F(1, 2), F(1, 2))
    finite, witness = [], []
    for p in (F(1, 4), F(1, 2), F(3, 4)):
        for n in range(1, 65):
            for e in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
                exact = sum(F(comb(n, k))*p**k*(1-p)**(n-k)
                            for k in range(n+1) if abs(F(k, n)-p) > e)
                bound = tail_upper(2, n, e)
                require(exact <= bound, "finite tail upper bound failed")
                finite.append((p, n, e, exact, bound))
        e = {n: radius(2, n, alpha, F(1)) for n in range(1, 65)}
        hit = prefix_failure(p, 64, e)
        require(hit <= alpha, "finite prefix confidence sequence failed")
        witness.append({"p": str(p), "horizon": 64, "first_failure_probability": str(hit)})
    independent = 0
    for p in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
        for h in range(8):
            for e in (F(0), F(1, 3), F(1)):
                eps = {n: e for n in range(1, h+1)}
                require(prefix_failure(p, h, eps) == full_bitstrings(p, h, eps), "path oracle mismatch")
                independent += 1
    adaptive = []
    eps = [{n: radius(2, n, alpha, w) for n in range(1, 33)} for w in weights]
    for laws in product((F(1, 4), F(1, 2), F(3, 4)), repeat=2):
        for rule in ("alternate", "higher_mean", "lower_mean", "stop_on_first_one"):
            failure, states = adaptive_failure(laws, 32, eps, rule)
            require(failure <= alpha, "adaptive allocation confidence failed")
            adaptive.append({"laws": [str(x) for x in laws], "rule": rule,
                             "failure_probability": str(failure), "visited_states": states})
    peek = optional_peek()
    require(peek["optional_failure"] == F(47, 125) > peek["fixed_look_nominal_error"], "peek falsifier")
    require(peek["repair_uniform_union_upper"] < peek["fixed_look_nominal_error"], "peek revival")
    grid = []
    for k in (1, 2, 3):
        for n in (0, 1, 2, 8, 32, 64, 128):
            r = registered_radii((k,), (n,), alpha, (F(1),))[0]
            if n and k > 1:
                require(tail_upper(k, n, r) <= alpha/(n*(n+1)), "radius certificate")
                if r:
                    require(tail_upper(k, n, r-F(1, n)) > alpha/(n*(n+1)), "grid nonminimal")
            grid.append({"alphabet": k, "n": n, "radius": str(r)})
    root = Path(__file__).resolve().parent
    names = ("row_confidence_v1.py", "visit_oracle_v1.py", "check_adaptive_rows_v1.py",
             "ADAPTIVE_ROW_CONFIDENCE_THEOREM_V1.md")
    return {"schema": "gmi-adaptive-row-confidence-v1", "status": "PASS",
            "exact_binomial_tail_checks": len(finite), "independent_prefix_path_checks": independent,
            "fixed_prefix_hitting_controls": witness, "adaptive_allocation_controls": adaptive,
            "rational_radius_grid": grid, "optional_peek": {k: str(v) for k, v in peek.items()},
            "source_sha256": {n: hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names},
            "scope": "Fixed conditional row laws and supplied support, never inferred from these checks",
            "new_confidence_sequence_method": False, "physical_sampling_verified": False,
            "policy_transfer": "Inherited FMT bound applied on the proved simultaneous TV event"}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
