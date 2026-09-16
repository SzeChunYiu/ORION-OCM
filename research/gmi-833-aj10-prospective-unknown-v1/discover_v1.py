from __future__ import annotations

import json
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENV = json.loads((HERE / "HELDOUT_ENV_V1.json").read_text())
INPUTS = [tuple(x) for x in ENV["input_order"]]
TARGET = tuple(ENV["protected_outputs"])


def table_route():
    checked = 0
    hits = []
    for mask in range(256):
        truth = tuple((mask >> i) & 1 for i in range(8))
        checked += 1
        if truth == TARGET:
            hits.append(mask)
    assert hits == [232]
    return {
        "route": "complete_response_table_enumeration",
        "checked": checked,
        "candidate_id": "T232",
        "truth": list(TARGET),
        "resource_vector": {"evaluation_operations": 1, "persistent_description_cells": 8},
        "developmental_profile": "FIXED",
    }


def semantic_route():
    terminals = {
        "x0": tuple(r[0] for r in INPUTS),
        "x1": tuple(r[1] for r in INPUTS),
        "x2": tuple(r[2] for r in INPUTS),
        "0": (0,) * 8,
        "1": (1,) * 8,
    }
    best = {sem: (0, name) for name, sem in terminals.items()}
    first_hit = None
    frontier_sizes = [len(best)]
    for cost in range(1, 6):
        snapshot = list(best.items())
        for sem, (c, expr) in snapshot:
            if c == cost - 1:
                out = tuple(1 - v for v in sem)
                if out not in best:
                    best[out] = (cost, f"NOT({expr})")
        snapshot = list(best.items())
        for c1 in range(cost):
            c2 = cost - 1 - c1
            left = [(s, e) for s, (c, e) in snapshot if c == c1]
            right = [(s, e) for s, (c, e) in snapshot if c == c2]
            for s1, e1 in left:
                for s2, e2 in right:
                    for op in ("AND", "OR"):
                        out = tuple((a & b) if op == "AND" else (a | b) for a, b in zip(s1, s2))
                        if out not in best:
                            best[out] = (cost, f"{op}({e1},{e2})")
        frontier_sizes.append(len(best))
        if TARGET in best and first_hit is None:
            first_hit = best[TARGET]
            break
    assert first_hit is not None
    cost, expr = first_hit
    assert cost == 4
    return {
        "route": "semantic_dynamic_closure",
        "semantic_classes_seen": len(best),
        "frontier_sizes": frontier_sizes,
        "candidate_id": "E4",
        "expression": expr,
        "truth": list(TARGET),
        "resource_vector": {"evaluation_operations": cost, "persistent_description_cells": 0},
        "developmental_profile": "FIXED",
    }


def pareto(candidates):
    def dominates(a, b):
        ka = a["resource_vector"]
        kb = b["resource_vector"]
        coords = ("evaluation_operations", "persistent_description_cells")
        return all(ka[c] <= kb[c] for c in coords) and any(ka[c] < kb[c] for c in coords)
    out = []
    for c in candidates:
        if not any(dominates(d, c) for d in candidates if d is not c):
            out.append(c["candidate_id"])
    return out


def main():
    a = table_route()
    b = semantic_route()
    assert a["truth"] == b["truth"] == list(TARGET)
    candidates = [a, b]
    frontier = pareto(candidates)
    assert set(frontier) == {"T232", "E4"}
    result = {
        "schema": "AJ10_PRE_TAXONOMY_EVALUATION_V1",
        "heldout_task_id": ENV["task_id"],
        "taxonomy_visible_to_search": False,
        "capability_evaluated_before_taxonomy": True,
        "capability": {"protected_cases": 8, "correct_cases_each": 8, "exact": True},
        "candidates": candidates,
        "pareto_frontier": frontier,
        "unique_morphology_selected": False,
        "replication": "two materially different representations/search routes reproduce identical protected behavior",
    }
    (HERE / "EVALUATED_CANDIDATES_V1.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
