#!/usr/bin/env python3
import json
from fractions import Fraction

rows = [
    ("h0", 0, 0, True),
    ("h1", 1, 2, True),
    ("h2", 2, 5, True),
    ("h3", 2, 3, True),
    ("h4", 2, 3, True),
    ("hU", 0, 0, False),
]


def image(names):
    return sorted({(p, c) for n, p, c, defined in rows if defined and n in names})


def dominates(a, b):
    return (
        a[0] >= b[0]
        and a[1] <= b[1]
        and (a[0] > b[0] or a[1] < b[1])
    )


def front(values):
    return [v for v in values if not any(u != v and dominates(u, v) for u in values)]


def win(values, lam):
    scores = [(lam * p - c, (p, c)) for p, c in values]
    top = max(score for score, _ in scores)
    return [v for score, v in scores if score == top]


all_names = {r[0] for r in rows}
budget_names = {"h0", "h1"}
full = image(all_names)
budget = image(budget_names)
relief = []
for name in sorted(all_names - budget_names):
    if any(p >= 2 for p, _ in image(budget_names | {name})):
        relief.append(name)

print(
    json.dumps(
        {
            "status": "GREEN",
            "full_frontier": [list(v) for v in front(full)],
            "budget_frontier": [list(v) for v in front(budget)],
            "phase_low": [list(v) for v in win(full, Fraction(1, 1))],
            "phase_tie": [list(v) for v in win(full, Fraction(3, 2))],
            "phase_high": [list(v) for v in win(full, Fraction(3, 1))],
            "relief_witnesses": relief,
        },
        sort_keys=True,
    )
)
