"""Exact controls only; no task, candidate, training or timing experiment."""
from fractions import Fraction as F
from itertools import product
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stopping_model_v1 import Model, action
from proper_policy_v1 import construct, evaluate, bellman_slacks, certify
from occupancy_oracle_v1 import independent_viable, flow_vertices


def witnesses():
    wait = Model(((action(0, 1, 0), action(1, 0, 1)),))
    w = construct(wait)
    if (w["cost"], w["steps"], w["policy"]) != ((F(1),), (F(1),), (1,)):
        raise RuntimeError("zero-cycle revival failed")
    if set(bellman_slacks(wait, w).values()) != {0}:
        raise RuntimeError("scalar greedy countercontrol not tied")
    if evaluate(wait, (0,), (0,)) is not None:
        raise RuntimeError("improper zero loop accepted")
    geom = construct(Model(((action(1, F(1,2), F(1,2)),),)))
    free = construct(Model(((action(0, F(1,2), F(1,2)),),)))
    trap = Model(((action(0, 0, F(1,2), F(1,2)),), ()))
    revived = Model(((action(0, 0, F(1,2), F(1,2)), action(3, 0, 0, 1)), ()))
    if construct(trap)["viable"] or construct(revived)["cost"] != (3, None):
        raise RuntimeError("trap viability control failed")
    cheap = Model(((action(0, F(1,2), F(1,2)), action(F(1,4), 0, 1)),))
    delta = Model((tuple(action(a.cost+1, *a.probability) for a in cheap.rows[0]),))
    c, d = construct(cheap), construct(delta)
    if c["policy"] != (0,) or d["policy"] != (1,):
        raise RuntimeError("finite perturbation countercontrol failed")
    if geom["cost"] != (2,) or geom["steps"] != (2,) or free["cost"] != (0,):
        raise RuntimeError("geometric exact-value control failed")
    return {
        "zero_loop_rejected": True, "zero_loop_revival": w,
        "positive_geometric": geom, "free_geometric": free,
        "geometric_tail_first_eight": [F(1, 2**k) for k in range(1, 9)],
        "geometric_extended_infinite_fixed_point_excluded": True,
        "naive_goal_path_trap_rejected": True,
        "terminal_revival": construct(revived),
        "lexical_cheap_trial": c, "delta_one_higher_original_cost": d,
        "history_delay_survival_first_eight": [F(1, n) for n in range(1, 9)],
        "history_delay_mean": "infinite harmonic tail; almost sure finite delay",
    }


def census():
    kernels = tuple(tuple(F(x, 2) for x in row)
                    for row in product(range(3), repeat=3) if sum(row) == 2)
    regimes = ((0, 0, 0, 0), (0, 1, 0, 1), (1, 0, 0, 1), (1, 1, 1, 1))
    stats = {"kernels": 0, "models": 0, "flow_comparisons": 0,
             "accepted_flow_bases": 0, "proper_policy_evaluations": 0}
    digest = hashlib.sha256()
    for rows in product(kernels, repeat=4):
        unc = Model(tuple(tuple(action(0, *rows[2*s+a]) for a in range(2))
                          for s in range(2)))
        domain = independent_viable(unc)
        stats["kernels"] += 1
        for charges in regimes:
            model = Model(tuple(tuple(action(charges[2*s+a], *rows[2*s+a])
                                      for a in range(2)) for s in range(2)))
            result = construct(model)
            certify(model, result)
            if result["viable"] != domain:
                raise RuntimeError("independent closed-subset viability mismatch")
            if any(slack < 0 for slack in bellman_slacks(model, result).values()):
                raise RuntimeError("Bellman certificate inequality failed")
            policy = tuple(result["policy"][s] for s in domain)
            if domain and evaluate(model, domain, policy) != (
                    tuple(result["cost"][s] for s in domain),
                    tuple(result["steps"][s] for s in domain)):
                raise RuntimeError("returned common policy has different values")
            injections = ((1, 1), (1, 2)) if len(domain) == 2 else ((1,)*len(domain),)
            for alpha in injections:
                pair, bases = flow_vertices(model, domain, alpha)
                expected = tuple(sum(F(a)*result[key][s] for a, s in zip(alpha, domain))
                                 for key in ("cost", "steps"))
                if pair != expected:
                    raise RuntimeError("independent occupancy optimum mismatch")
                stats["flow_comparisons"] += 1
                stats["accepted_flow_bases"] += bases
            stats["models"] += 1
            stats["proper_policy_evaluations"] += result["proper_tables"]
            digest.update(json.dumps(result, default=str, sort_keys=True).encode())
    return {**stats, "full_result_sha256": digest.hexdigest()}


def run_checks():
    return {"status": "EXACT_FINITE_PROPER_STOPPING_PASS", "witnesses": witnesses(),
            "census": census(), "scope": "known finite rational model; expected scalar cost",
            "new_empirical_measurements": False}


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2, sort_keys=True, default=str))
