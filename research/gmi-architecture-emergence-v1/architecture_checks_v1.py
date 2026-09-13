"""Exact finite completion and full-fiber census; no physical or native execution."""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import json
import types

ROOT = Path(__file__).resolve().parent
model = types.ModuleType("aem_model")
exec(compile((ROOT/"architecture_selection_v1.py").read_bytes(),
             str(ROOT/"architecture_selection_v1.py"), "exec"), model.__dict__)


def oracle_frontier(rows):
    """Find the unique antichain covering all profiles, by subset enumeration."""
    points = tuple(set(row[2] for row in rows))
    accepted = []
    for mask in range(1 << len(points)):
        subset = tuple(p for i, p in enumerate(points) if mask & (1 << i))
        if any(all(a <= b for a, b in zip(p, q)) for p, q in combinations(subset, 2)):
            continue
        if any(all(a <= b for a, b in zip(q, p)) for p, q in combinations(subset, 2)):
            continue
        if all(any(all(a <= b for a, b in zip(q, p)) for q in subset) for p in points):
            accepted.append(set(subset))
    if len(accepted) != 1:
        raise ValueError("independent finite antichain oracle failed")
    return frozenset(row[0] for row in rows if row[2] in accepted[0])


def run_checks():
    grid = tuple((F(x), F(y)) for x, y in product((0, 1), repeat=2))
    worlds, expected = [], []
    for assigned in product((None,) + grid, repeat=3):
        rows = tuple((str(i), "A" if i != 1 else "B", p)
                     for i, p in enumerate(assigned) if p is not None)
        worlds.append(rows)
        expected.append(oracle_frontier(rows))
        if frozenset(r[0] for r in model.frontier(rows)) != expected[-1]:
            raise ValueError("frontier mismatch")
    comparisons = 0
    for i, left in enumerate(worlds):
        for j, right in enumerate(worlds):
            report = model.completion_report((left, right))
            ls = frozenset(row[1] for row in left if row[0] in expected[i])
            rs = frozenset(row[1] for row in right if row[0] in expected[j])
            if report["label_set_identified"] != (ls == rs):
                raise ValueError("label-set mismatch")
            unique = next(iter(ls)) if ls == rs and len(ls) == 1 else None
            if report["robust_unique_label"] != unique:
                raise ValueError("unique-family mismatch")
            if report["common_optimal_candidates"] != expected[i] & expected[j]:
                raise ValueError("common candidate mismatch")
            if report["selection_exists_in_every_world"] != bool(ls and rs):
                raise ValueError("nonemptiness mismatch")
            comparisons += 1
    accepted, rejected = 0, 0
    for rows in worlds:
        for mask in range(1 << len(rows)):
            ids = {row[0] for i, row in enumerate(rows) if mask & (1 << i)}
            # Independent finite N oracle: its minimal profile(0,0) must occur in C.
            expected_acceptance = any(row[0] in ids and row[2] == (F(0), F(0)) for row in rows)
            try:
                selected = model.constructive_closure(rows, ids, grid)
            except ValueError:
                if expected_acceptance:
                    raise
                rejected += 1
            else:
                if not expected_acceptance or frozenset(row[0] for row in selected) != oracle_frontier(rows):
                    raise ValueError("constructive full-fiber mismatch")
                accepted += 1
    return {"status": "EXACT_FINITE_SELECTION_CHECKED",
            "finite_worlds": len(worlds), "world_pairs": comparisons,
            "coverage_certificates_accepted": accepted,
            "coverage_certificates_rejected": rejected,
            "scope": "supplied rational finite completions only; no universe discovery"}


if __name__ == "__main__":
    print(json.dumps(run_checks(), sort_keys=True, indent=2))
