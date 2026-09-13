"""PCA exact census: independent policy execution and latent-mode controls."""
from fractions import Fraction as F
from itertools import product, combinations
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from grand_gmi_probabilistic_acquisition_model_v1 import (
    bellman_certificate, finite_horizon, persistent_probe, stationary, validate)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def execute_table(model, table, start):
    """Enumerate actual positive-probability paths; no Bellman value recursion."""
    goal, horizon = len(model)-1, len(table)
    stack, success, expected, worst = [(start, 0, F(1), F(0))], F(0), F(0), F(0)
    while stack:
        state, time, mass, cost = stack.pop()
        if state == goal or time == horizon:
            success += mass * (state == goal)
            expected += mass * cost
            worst = max(worst, cost)
            continue
        charged, probs = model[state][table[time][state]]
        for nxt, chance in enumerate(probs):
            if chance:
                stack.append((nxt, time+1, mass*chance, cost+charged))
    return success, expected, worst


def policy_oracle(model, horizon, start=0):
    widths = [len(row) for row in model[:-1]]
    best_success, best_sure, count = F(0), None, 0
    for flat in product(*(range(width) for _ in range(horizon) for width in widths)):
        table = tuple(flat[t*len(widths):(t+1)*len(widths)] for t in range(horizon))
        success, cost, _ = execute_table(model, table, start)
        best_success = max(best_success, success)
        if success == 1:
            best_sure = cost if best_sure is None else min(cost, best_sure)
        count += 1
    return best_success, best_sure, count


def graph_oracle(model, start):
    """All bounded support paths plus all closed nonglobal-goal subsets."""
    goal, n = len(model)-1, len(model)
    paths, reach = [(start,)], {start}
    for _ in range(n):
        extended = []
        for path in paths:
            if path[-1] == goal:
                continue
            for nxt, p in enumerate(model[path[-1]][0][1]):
                if p:
                    reach.add(nxt)
                    extended.append(path+(nxt,))
        paths = extended
    sure = all(path[-1] == goal for path in paths)
    nong = sorted(reach-{goal})
    closed = False
    for size in range(1, len(nong)+1):
        for subset in combinations(nong, size):
            closed |= all(all(not p or j in subset for j, p in enumerate(model[s][0][1]))
                          for s in subset)
    return sure, not closed


def latent_execution(bits, horizon, recovery=False, cutoff=None):
    """Hidden mode persists between resets; only observed failure changes belief."""
    mode, draw, state, failures, cost = bits[0], 0, "M", 0, 0
    for _ in range(horizon):
        if state == "G":
            break
        if cutoff is not None and failures >= cutoff:
            cost += 5
            state = "G"
        elif state == "B" and recovery:
            cost += 1
            draw += 1
            mode, state = bits[draw], "M"
        else:
            cost += 1
            if mode:
                state = "G"
            else:
                failures += 1
                state = "B"
    return state == "G", cost


def latent_average(horizon, recovery=False, cutoff=None):
    # A reset uses an action, so at most floor(H/2)+1 mode draws are needed.
    outcomes = [latent_execution(bits, horizon, recovery, cutoff)
                for bits in product((0, 1), repeat=horizon//2+1)]
    return (sum(F(success) for success, _ in outcomes)/len(outcomes),
            sum(F(cost) for _, cost in outcomes)/len(outcomes),
            max(cost for _, cost in outcomes))


def run():
    distributions = tuple(tuple(F(x, 2) for x in row)
                          for row in product(range(3), repeat=3) if sum(row) == 2)
    census, policies = 0, 0
    for rows in product(distributions, repeat=4):
        model = validate((((1, rows[0]), (2, rows[1])),
                          ((1, rows[2]), (2, rows[3])), ()))
        success, cost = finite_horizon(model, 2)
        for start in range(2):
            p, c, count = policy_oracle(model, 2, start)
            require((p, c) == (success[start], cost[start]), "finite policy census mismatch")
            policies += count
        census += 1
    supports = tuple(subset for k in range(1, 4) for subset in combinations(range(3), k))
    graphs = 0
    for first, second in product(supports, repeat=2):
        model = tuple(((1, tuple(F(j in subset, len(subset)) for j in range(3))),)
                      for subset in (first, second))+((),)
        for start in range(3):
            actual = stationary(model, (0, 0), start)
            require((actual["sure"], actual["almost_sure"]) == graph_oracle(model, start),
                    "support graph census mismatch")
            require((actual["success"] == 1) == actual["almost_sure"], "absorption probability mismatch")
            graphs += 1
    baseline, retry, full = persistent_probe(), persistent_probe(True), persistent_probe(True, True)
    lost, restored = stationary(baseline, (0, 0)), stationary(retry, (0, 1))
    require(lost["success"] == F(1, 2) and lost["expected_cost"] is None, "correlation obstruction lost")
    require(restored == {"sure": False, "almost_sure": True, "success": F(1), "expected_cost": F(3)},
            "reset revival failed")
    require(bellman_certificate(full, (F(3), F(4), F(0)), (0, 1)), "SSP certificate failed")
    require(not bellman_certificate(full, (F(2), F(3), F(0)), (0, 1)), "optimistic certificate accepted")
    deadlines = []
    for horizon in range(1, 9):
        value, _ = finite_horizon(retry, horizon)
        p, _, _ = latent_average(horizon, recovery=True)
        require(p == value[0] == 1-F(1, 2**((horizon+1)//2)), "retry deadline control failed")
        require(latent_average(horizon)[0] == F(1, 2), "persistent failure became iid")
        deadlines.append(str(p))
    fallback = []
    for k in range(1, 7):
        p, cost, worst = latent_average(2*k, recovery=True, cutoff=k)
        _, optimal = finite_horizon(full, 2*k)
        require(p == 1 and cost == optimal[0] == 3+F(1, 2**k) and worst == 2*k+4,
                "bounded retry/certification law failed")
        fallback.append({"attempts": k, "expected": str(cost), "worst": worst})
    for horizon in range(5):
        success, cost = finite_horizon(full, horizon)
        for start in range(2):
            p, c, count = policy_oracle(full, horizon, start)
            require((p, c) == (success[start], cost[start]), "adaptive fallback oracle mismatch")
            policies += count
    for depth in range(1, 9):
        waits = 0
        for bits in product((0, 1), repeat=depth):
            for i, bit in enumerate(bits, 1):
                if bit:
                    break
                for _ in range(2**i):
                    waits += 1
        require(F(waits, 2**depth) == depth, "history-controller infinite-expectation control failed")
    return {"schema": "probabilistic-controlled-acquisition-v1", "all_checks_green": True,
            "terminal": "PCA_FINITE_KNOWN_KERNEL_REVIVAL_GREEN",
            "horizon_two_kernels": census, "independently_executed_policy_tables": policies,
            "stationary_support_graph_start_cases": graphs, "baseline_success": "1/2",
            "baseline_expected_work": "infinity", "retry_success": "1", "retry_expected_work": "3",
            "retry_sure": False, "retry_success_by_horizon_1_to_8": deadlines,
            "sure_fallback_witnesses": fallback, "infinite_history_expected_wait_prefixes": 8,
            "unknown_kernel_solved": False, "controller_and_physical_costs_measured": False}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
