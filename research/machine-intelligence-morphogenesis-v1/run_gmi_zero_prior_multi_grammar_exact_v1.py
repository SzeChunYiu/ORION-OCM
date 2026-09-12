#!/usr/bin/env python3
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

Q = 5
DOMAIN = tuple(range(Q))


def add_sem(a, b):
    return tuple((x + y) % Q for x, y in zip(a, b))


def mul_sem(a, b):
    return tuple((x * y) % Q for x, y in zip(a, b))


def eq_sem(a, b):
    return tuple(1 if x == y else 0 for x, y in zip(a, b))


def expression_min_nodes():
    best = {tuple([c] * Q): (1, str(c)) for c in range(Q)}
    best[DOMAIN] = (1, "x")
    by_cost = defaultdict(list)
    for sem, (cost, _) in best.items():
        by_cost[cost].append(sem)

    for total in range(3, 31, 2):
        staged = {}
        for left_cost in range(1, total - 1, 2):
            right_cost = total - 1 - left_cost
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
            best[sem] = (total, expr)
            by_cost[total].append(sem)
        if len(best) == Q ** Q:
            break

    assert len(best) == Q ** Q
    return best


def eval_poly(coeffs, x):
    y = 0
    for c in reversed(coeffs):
        y = (y * x + c) % Q
    return y


def polynomial_min_degree():
    best = {}
    for degree in range(Q):
        for coeffs in itertools.product(range(Q), repeat=degree + 1):
            if degree > 0 and coeffs[-1] == 0:
                continue
            sem = tuple(eval_poly(coeffs, x) for x in DOMAIN)
            if sem not in best:
                best[sem] = (degree, coeffs)
    assert len(best) == Q ** Q
    return best


def main():
    expr = expression_min_nodes()
    poly = polynomial_min_degree()

    cost_hist = Counter()
    strict_winner = Counter()
    winner_set_hist = Counter()
    compressed = 0

    examples = {}

    for sem in itertools.product(range(Q), repeat=Q):
        degree, coeffs = poly[sem]
        nodes, expression = expr[sem]

        table_cost = 17
        poly_cost = 8 + 3 * degree
        expr_cost = 2 + 4 * nodes

        minimum = min(table_cost, poly_cost, expr_cost)
        cost_hist[minimum] += 1
        if minimum < table_cost:
            compressed += 1

        winners = tuple(
            name
            for name, cost in (
                ("table", table_cost),
                ("polynomial", poly_cost),
                ("expression", expr_cost),
            )
            if cost == minimum
        )
        winner_set_hist[winners] += 1
        if len(winners) == 1:
            strict_winner[winners[0]] += 1

        key = tuple(sem)
        if key in {
            (1, 3, 0, 2, 4),
            (0, 0, 0, 0, 1),
            (4, 2, 4, 1, 1),
        }:
            examples[str(list(key))] = {
                "table_bits": table_cost,
                "polynomial_degree": degree,
                "polynomial_bits": poly_cost,
                "polynomial_coefficients": list(coeffs),
                "expression_nodes": nodes,
                "expression_bits": expr_cost,
                "one_minimum_expression": expression,
                "portfolio_bits": minimum,
                "winners": list(winners),
            }

    assert sum(cost_hist.values()) == 3125
    assert cost_hist == Counter({17: 2995, 14: 105, 11: 19, 6: 6})
    assert compressed == 130
    assert winner_set_hist[("table", "polynomial")] == 500
    assert strict_winner["table"] == 2495

    receipt = {
        "artifact": "GMI_ZERO_PRIOR_MULTI_GRAMMAR_EXACT_RECEIPT_V1",
        "status": "EXECUTED_EXACT_ENUMERATION",
        "runner": "run_gmi_zero_prior_multi_grammar_exact_v1.py",
        "target_space": {
            "domain": "F_5 -> F_5",
            "functions": 3125,
        },
        "grammars": {
            "table": "2-bit tag + five 3-bit output symbols",
            "polynomial": "2-bit tag + 3-bit coefficient count + 3 bits per F_5 coefficient",
            "expression": "2-bit tag + 4 bits per prefix AST token over x, constants, add, multiply, equality",
        },
        "minimum_cost_histogram_bits": {str(k): cost_hist[k] for k in sorted(cost_hist)},
        "compressed_below_table_count": compressed,
        "compressed_below_table_fraction": compressed / 3125,
        "no_saving_count": cost_hist[17],
        "no_saving_fraction": cost_hist[17] / 3125,
        "strict_winners": dict(strict_winner),
        "winner_sets": {"|".join(k): v for k, v in winner_set_hist.items()},
        "examples": examples,
        "checks": {
            "all_3125_functions_exhausted": True,
            "minimum_cost_histogram_matches_theorem": True,
            "130_functions_compress_below_table": True,
            "2995_functions_have_no_registered_saving": True,
            "500_degree3_targets_tie_table_and_polynomial": True,
            "2495_targets_are_strict_table_winners": True,
        },
        "claim_ceiling": "Exact finite comparison across three frozen grammars only. Does not establish language-independent incompressibility or broad learning-scale K4 closure.",
        "terminal": "ZERO_PRIOR_COMPRESSION_MULTI_GRAMMAR_EXACT_GREEN",
    }

    out = Path(__file__).with_name("GMI_ZERO_PRIOR_MULTI_GRAMMAR_EXACT_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
