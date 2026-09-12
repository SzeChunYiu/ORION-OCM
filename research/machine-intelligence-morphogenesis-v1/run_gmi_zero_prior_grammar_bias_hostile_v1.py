#!/usr/bin/env python3
import itertools
import json
from collections import defaultdict
from pathlib import Path

Q = 5
DOMAIN = tuple(range(Q))


def add_sem(a, b):
    return tuple((x + y) % Q for x, y in zip(a, b))


def mul_sem(a, b):
    return tuple((x * y) % Q for x, y in zip(a, b))


def eq_sem(a, b):
    return tuple(1 if x == y else 0 for x, y in zip(a, b))


def exhaustive_min_costs(max_cost=25):
    best = {tuple([c] * Q): (1, str(c)) for c in range(Q)}
    best[DOMAIN] = (1, "x")
    by_cost = defaultdict(list)
    for sem, (cost, _) in best.items():
        by_cost[cost].append(sem)

    completed_at = None
    for total_cost in range(3, max_cost + 1):
        staged = {}
        for left_cost in range(1, total_cost - 1):
            right_cost = total_cost - 1 - left_cost
            if left_cost not in by_cost or right_cost not in by_cost:
                continue
            for a in by_cost[left_cost]:
                ea = best[a][1]
                for b in by_cost[right_cost]:
                    eb = best[b][1]
                    candidates = (
                        (add_sem(a, b), f"({ea}+{eb})"),
                        (mul_sem(a, b), f"({ea}*{eb})"),
                        (eq_sem(a, b), f"eq({ea},{eb})"),
                    )
                    for sem, expr in candidates:
                        if sem not in best and sem not in staged:
                            staged[sem] = expr
        for sem, expr in staged.items():
            best[sem] = (total_cost, expr)
            by_cost[total_cost].append(sem)
        if len(best) == Q**Q:
            completed_at = total_cost
            break

    return best, completed_at


def main():
    best, completed_at = exhaustive_min_costs()
    assert len(best) == Q**Q == 3125

    stable = tuple((2 * x + 1) % Q for x in DOMAIN)
    predecessor_twin = (0, 0, 0, 0, 1)
    stable_cost, stable_expr = best[stable]
    twin_cost, twin_expr = best[predecessor_twin]

    max_cost = max(cost for cost, _ in best.values())
    hardest = [(sem, expr) for sem, (cost, expr) in best.items() if cost == max_cost]

    assert stable_cost == 5
    assert twin_cost == 3
    assert twin_expr in ("eq(4,x)", "eq(x,4)")
    assert completed_at == 15
    assert max_cost == 15
    assert len(hardest) == 1
    assert hardest[0][0] == (4, 2, 4, 1, 1)

    histogram = defaultdict(int)
    for cost, _ in best.values():
        histogram[cost] += 1

    receipt = {
        "artifact": "GMI_ZERO_PRIOR_GRAMMAR_BIAS_HOSTILE_RECEIPT_V1",
        "status": "EXECUTED_EXACT_HOSTILE",
        "runner": "run_gmi_zero_prior_grammar_bias_hostile_v1.py",
        "grammar": {
            "domain": "F_5 -> F_5",
            "terminals": ["x", "0", "1", "2", "3", "4"],
            "binary_operators": ["add_mod_5", "multiply_mod_5", "equality_to_0_or_1"],
            "cost": "AST node count"
        },
        "semantic_functions_total": len(best),
        "all_functions_reached_by_cost": completed_at,
        "cost_histogram": {str(k): histogram[k] for k in sorted(histogram)},
        "stable_affine_target": {
            "outputs": list(stable),
            "minimum_ast_cost": stable_cost,
            "one_minimum_expression": stable_expr
        },
        "predecessor_memory_twin": {
            "outputs": list(predecessor_twin),
            "minimum_ast_cost": twin_cost,
            "one_minimum_expression": twin_expr,
            "cross_grammar_incompressibility_claim": "FALSIFIED"
        },
        "successor_hard_target": {
            "outputs": list(hardest[0][0]),
            "minimum_ast_cost": max_cost,
            "one_minimum_expression": hardest[0][1],
            "number_of_functions_at_maximum_cost": len(hardest)
        },
        "checks": {
            "all_3125_semantic_functions_exhausted": True,
            "predecessor_twin_has_three_node_equality_program": True,
            "predecessor_cross_grammar_negative_control_fails": True,
            "successor_hard_target_is_unique_at_cost_15": True
        },
        "claim_ceiling": "Exact hostile against one richer DSL. The successor hard target is grammar-relative, not intrinsically incompressible; multi-grammar protected testing remains required.",
        "terminal": "ZERO_PRIOR_GRAMMAR_BIAS_PREDECESSOR_RED_SUCCESSOR_FROZEN"
    }

    out = Path(__file__).with_name("GMI_ZERO_PRIOR_GRAMMAR_BIAS_HOSTILE_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
