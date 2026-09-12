#!/usr/bin/env python3
import itertools
import json
from fractions import Fraction
from pathlib import Path

ETA = Fraction(1, 4)
SAFE = Fraction(4, 5)


def belief(history):
    l1 = Fraction(1, 1)
    l0 = Fraction(1, 1)
    for obs in history:
        if obs == 1:
            l1 *= 1 - ETA
            l0 *= ETA
        else:
            l1 *= ETA
            l0 *= 1 - ETA
    return l1 / (l1 + l0)


def next_one(p):
    return ETA + (1 - 2 * ETA) * p


def values(p):
    return {"guess0": 1 - p, "safe": SAFE, "guess1": p}


def optimal(p):
    v = values(p)
    best = max(v.values())
    return tuple(k for k, x in v.items() if x == best)


def map_state(p):
    if p > Fraction(1, 2):
        return "1"
    if p < Fraction(1, 2):
        return "0"
    return "tie"


def main():
    histories = []
    groups = {}
    for length in range(0, 7):
        for h in itertools.product((0, 1), repeat=length):
            p = belief(h)
            histories.append(h)
            groups.setdefault(p, []).append(h)

    same_belief_pairs = 0
    violations = 0
    for p, hs in groups.items():
        for h1, h2 in itertools.combinations(hs, 2):
            same_belief_pairs += 1
            if belief(h1) != belief(h2):
                violations += 1
            if next_one(belief(h1)) != next_one(belief(h2)):
                violations += 1
            if values(belief(h1)) != values(belief(h2)):
                violations += 1
            if optimal(belief(h1)) != optimal(belief(h2)):
                violations += 1

    map_collisions = 0
    examples = []
    for h1, h2 in itertools.combinations(histories, 2):
        p1, p2 = belief(h1), belief(h2)
        if map_state(p1) == map_state(p2) and optimal(p1) != optimal(p2):
            map_collisions += 1
            if len(examples) < 5:
                examples.append({
                    "h1": list(h1), "p1": str(p1), "opt1": list(optimal(p1)),
                    "h2": list(h2), "p2": str(p2), "opt2": list(optimal(p2)),
                    "map": map_state(p1)
                })

    receipt = {
        "artifact": "GMI_POMDP_BELIEF_EXACT_RECEIPT_V1",
        "status": "EXACT_FINITE_CONTROL_STATE_CALIBRATION",
        "runner": "run_gmi_pomdp_belief_exact_v1.py",
        "history_lengths": [0, 6],
        "histories": len(histories),
        "distinct_beliefs": len(groups),
        "same_belief_pairs": same_belief_pairs,
        "same_belief_violations": violations,
        "same_map_different_optimal_action_pairs": map_collisions,
        "examples": examples,
        "claim_ceiling": "Exact binary known-model POMDP only; no belief learning, exploration, approximation or real control transfer.",
        "terminal": "POMDP_BELIEF_EXACT_GREEN" if violations == 0 and map_collisions > 0 else "POMDP_BELIEF_RED"
    }
    out = Path(__file__).with_name("GMI_POMDP_BELIEF_EXACT_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if receipt["terminal"] != "POMDP_BELIEF_EXACT_GREEN":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
