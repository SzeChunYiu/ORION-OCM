#!/usr/bin/env python3
"""Exact prospective witness for Section D developmental-history phase law V4."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple
import json

FREEZE_COMMIT = "06828d7dbf2cf86072efc3ec59db6216e5bf3bd7"
KEYS = ("k0", "k1", "k2", "k3")
VALUES = ("v0", "v1", "v2", "v3")
HELDOUT = {"k0": "v1", "k1": "v3", "k2": "v0", "k3": "v2"}
MAIN_BLOCK = (
    ("F", "k0"), ("F", "k1"), ("F", "k3"),
    ("R", "v0"), ("R", "v1"), ("R", "v2"), ("R", "v3"), ("R", "v1"),
)
MIRROR_BLOCK = (
    ("F", "k0"), ("F", "k1"), ("F", "k2"), ("F", "k3"), ("F", "k0"),
    ("R", "v0"), ("R", "v2"), ("R", "v3"),
)
CANDIDATES = ("key_index", "value_index", "dual_index", "pair_list")
KEY_REMINT = {"k0": "amber", "k1": "cedar", "k2": "delta", "k3": "birch"}
VALUE_REMINT = {"v0": "quartz", "v1": "onyx", "v2": "jade", "v3": "opal"}
VERIFY_UNITS = 8
CAP = 4


@dataclass(frozen=True)
class Vector:
    valid: bool
    persistent: int
    ops: int
    over_cap: bool


def dominates(a: Vector, b: Vector) -> bool:
    if not a.valid or a.over_cap or not b.valid or b.over_cap:
        return False
    return a.persistent <= b.persistent and a.ops <= b.ops and (
        a.persistent < b.persistent or a.ops < b.ops
    )


def pareto_all_pairs(vectors: Sequence[Vector]) -> Tuple[int, ...]:
    eligible = [i for i, v in enumerate(vectors) if v.valid and not v.over_cap]
    return tuple(i for i in eligible if not any(j != i and dominates(vectors[j], vectors[i]) for j in eligible))


def pareto_incremental(vectors: Sequence[Vector]) -> Tuple[int, ...]:
    front: List[int] = []
    for i in reversed(range(len(vectors))):
        vi = vectors[i]
        if not vi.valid or vi.over_cap:
            continue
        if any(dominates(vectors[j], vi) for j in front):
            continue
        front = [j for j in front if not dominates(vi, vectors[j])]
        front.append(i)
    return tuple(sorted(front))


def build_key_index(relation: Mapping[str, str]) -> Dict[str, str]:
    return dict(relation)


def build_value_index(relation: Mapping[str, str]) -> Dict[str, str]:
    return {v: k for k, v in relation.items()}


def reindex_key_to_value(key_index: Mapping[str, str]) -> Tuple[Dict[str, str], int]:
    out: Dict[str, str] = {}
    ops = 0
    for key, value in key_index.items():
        ops += 1
        out[value] = key
        ops += 1
    return out, ops


def reindex_value_to_key(value_index: Mapping[str, str]) -> Tuple[Dict[str, str], int]:
    out: Dict[str, str] = {}
    ops = 0
    for value, key in value_index.items():
        ops += 1
        out[key] = value
        ops += 1
    return out, ops


def serve_key(index: Mapping[str, str], direction: str, token: str) -> Tuple[str, int]:
    if direction == "F":
        return index[token], 1
    found = None
    ops = 0
    for key, value in index.items():
        ops += 1
        if value == token:
            found = key
    assert found is not None
    return found, ops


def serve_value(index: Mapping[str, str], direction: str, token: str) -> Tuple[str, int]:
    if direction == "R":
        return index[token], 1
    found = None
    ops = 0
    for value, key in index.items():
        ops += 1
        if key == token:
            found = value
    assert found is not None
    return found, ops


def serve_dual(rep: Tuple[Mapping[str, str], Mapping[str, str]], direction: str, token: str) -> Tuple[str, int]:
    key_index, value_index = rep
    return (key_index[token], 1) if direction == "F" else (value_index[token], 1)


def serve_pairs(pairs: Sequence[Tuple[str, str]], direction: str, token: str) -> Tuple[str, int]:
    found = None
    ops = 0
    for key, value in pairs:
        ops += 1
        if direction == "F" and key == token:
            found = value
        if direction == "R" and value == token:
            found = key
    assert found is not None
    return found, ops


def representations(relation: Mapping[str, str]) -> dict:
    key = build_key_index(relation)
    value = build_value_index(relation)
    return {
        "key_index": key,
        "value_index": value,
        "dual_index": (key, value),
        "pair_list": tuple(relation.items()),
    }


def serve(name: str, rep, direction: str, token: str) -> Tuple[str, int]:
    if name == "key_index":
        return serve_key(rep, direction, token)
    if name == "value_index":
        return serve_value(rep, direction, token)
    if name == "dual_index":
        return serve_dual(rep, direction, token)
    if name == "pair_list":
        return serve_pairs(rep, direction, token)
    raise KeyError(name)


def expected(relation: Mapping[str, str], direction: str, token: str) -> str:
    if direction == "F":
        return relation[token]
    return build_value_index(relation)[token]


def exactness_receipt() -> dict:
    checks = {name: 0 for name in CANDIDATES}
    failures = {name: [] for name in CANDIDATES}
    for perm in permutations(VALUES):
        relation = dict(zip(KEYS, perm))
        reps = representations(relation)
        for direction, tokens in (("F", KEYS), ("R", VALUES)):
            for token in tokens:
                target = expected(relation, direction, token)
                for name in CANDIDATES:
                    got, _ = serve(name, reps[name], direction, token)
                    checks[name] += 1
                    if got != target:
                        failures[name].append([list(perm), direction, token, got, target])
    return {
        "bijections": 24,
        "obligations_per_bijection": 8,
        "checks_per_candidate": checks,
        "all_exact": {name: not failures[name] for name in CANDIDATES},
        "failures": failures,
    }


def migration_receipt() -> dict:
    failures = []
    ops_seen = set()
    for perm in permutations(VALUES):
        relation = dict(zip(KEYS, perm))
        value, ops1 = reindex_key_to_value(build_key_index(relation))
        key, ops2 = reindex_value_to_key(build_value_index(relation))
        ops_seen.update((ops1, ops2))
        if value != build_value_index(relation) or key != build_key_index(relation):
            failures.append(list(perm))
    return {
        "bijections_checked": 24,
        "future_ops_seen": sorted(ops_seen),
        "all_exact": not failures,
        "failures": failures,
    }


def block_cost(name: str, relation: Mapping[str, str], block: Sequence[Tuple[str, str]]) -> Tuple[List[str], int]:
    rep = representations(relation)[name]
    outputs = []
    ops = 0
    for direction, token in block:
        out, cost = serve(name, rep, direction, token)
        assert out == expected(relation, direction, token)
        outputs.append(out)
        ops += cost
    return outputs, ops


def serve_cost_from_counts(name: str, forward: int, reverse: int) -> int:
    if name == "key_index":
        return forward + 4 * reverse
    if name == "value_index":
        return 4 * forward + reverse
    if name == "dual_index":
        return forward + reverse
    if name == "pair_list":
        return 4 * (forward + reverse)
    raise KeyError(name)


def migration_cost(history: str, name: str, k: int) -> int:
    if name not in ("key_index", "value_index"):
        return 0
    if history == "cold":
        return 8
    installed = "key_index" if history == "key" else "value_index"
    return 0 if name == installed else k


def vectors(history: str, m: int, k: int = 8, forward: int = 3, reverse: int = 5) -> List[Vector]:
    persistent = {"key_index": 4, "value_index": 4, "dual_index": 8, "pair_list": 8}
    out = []
    for name in CANDIDATES:
        p = persistent[name]
        ops = VERIFY_UNITS + migration_cost(history, name, k) + m * serve_cost_from_counts(name, forward, reverse)
        out.append(Vector(True, p, ops, p > CAP))
    return out


def names(indices: Sequence[int]) -> List[str]:
    return [CANDIDATES[i] for i in indices]


def phase_table(history: str, k: int = 8, forward: int = 3, reverse: int = 5) -> dict:
    table = {}
    for m in range(1, 9):
        vec = vectors(history, m, k, forward, reverse)
        a = pareto_all_pairs(vec)
        b = pareto_incremental(vec)
        table[str(m)] = {
            "all_pairs": names(a),
            "incremental": names(b),
            "agree": a == b,
            "key_ops": vec[0].ops,
            "value_ops": vec[1].ops,
        }
    return table


def theorem_grid_receipt() -> dict:
    checked = 0
    failures = []
    outcomes = {"A": 0, "tie": 0, "B": 0}
    for base_b in range(1, 6):
        for d in range(1, 9):
            for k in range(0, 13):
                for m in range(1, 9):
                    checked += 1
                    a_cost = (base_b + d) * m
                    b_from_a = k + base_b * m
                    if a_cost < b_from_a:
                        observed = "A"
                    elif a_cost == b_from_a:
                        observed = "tie"
                    else:
                        observed = "B"
                    dm = d * m
                    expected_from_a = "A" if dm < k else "tie" if dm == k else "B"
                    outcomes[observed] += 1
                    b_stay = base_b * m
                    a_from_b = k + (base_b + d) * m
                    if observed != expected_from_a or not (b_stay < a_from_b):
                        failures.append([base_b, d, k, m, observed, expected_from_a, b_stay, a_from_b])
    return {
        "tuples_checked": checked,
        "from_H_A_outcomes": outcomes,
        "all_pass": not failures,
        "failures": failures,
    }


def remint_relation(relation: Mapping[str, str]) -> Dict[str, str]:
    return {KEY_REMINT[k]: VALUE_REMINT[v] for k, v in relation.items()}


def remint_block(block: Sequence[Tuple[str, str]]) -> Tuple[Tuple[str, str], ...]:
    return tuple((direction, KEY_REMINT[token] if direction == "F" else VALUE_REMINT[token]) for direction, token in block)


def remint_receipt() -> dict:
    relation = remint_relation(HELDOUT)
    block = remint_block(MAIN_BLOCK)
    costs = {}
    for name in CANDIDATES:
        rep = representations(relation)[name]
        cost = 0
        for direction, token in block:
            out, op = serve(name, rep, direction, token)
            if out != expected(relation, direction, token):
                return {"all_exact": False, "bad_candidate": name}
            cost += op
        costs[name] = cost
    base_key = block_cost("key_index", HELDOUT, MAIN_BLOCK)[1]
    base_value = block_cost("value_index", HELDOUT, MAIN_BLOCK)[1]
    return {
        "all_exact": True,
        "key_block_ops": costs["key_index"],
        "value_block_ops": costs["value_index"],
        "costs_preserved": costs["key_index"] == base_key and costs["value_index"] == base_value,
        "heldout_history_collision_preserved": (
            names(pareto_all_pairs(vectors("key", 1))) == ["key_index"]
            and names(pareto_all_pairs(vectors("value", 1))) == ["value_index"]
        ),
        "reminted_relation": relation,
    }


def vector_json(v: Vector) -> dict:
    return {"valid": v.valid, "persistent_cells": v.persistent, "lifecycle_ops": v.ops, "over_cap": v.over_cap}


def build_results() -> dict:
    exact = exactness_receipt()
    migration = migration_receipt()
    main_key_outputs, main_key_cost = block_cost("key_index", HELDOUT, MAIN_BLOCK)
    main_value_outputs, main_value_cost = block_cost("value_index", HELDOUT, MAIN_BLOCK)
    mirror_key_outputs, mirror_key_cost = block_cost("key_index", HELDOUT, MIRROR_BLOCK)
    mirror_value_outputs, mirror_value_cost = block_cost("value_index", HELDOUT, MIRROR_BLOCK)

    key_phase = phase_table("key")
    value_phase = phase_table("value")
    zero_key = phase_table("key", k=0)
    zero_value = phase_table("value", k=0)
    cold = phase_table("cold")
    mirror_key = phase_table("key", forward=5, reverse=3)
    mirror_value = phase_table("value", forward=5, reverse=3)

    held_key = vectors("key", 1)
    held_value = vectors("value", 1)
    theorem = theorem_grid_receipt()
    remint = remint_receipt()

    assertions = {
        "H1_all_candidates_exact_24x8": all(exact["all_exact"].values()),
        "H2_reindex_exact_all24_and_cost8": migration["all_exact"] and migration["future_ops_seen"] == [8],
        "H3_dual_pair_over_cap": held_key[2].over_cap and held_key[3].over_cap,
        "H4_Hkey_m1_key_unique": key_phase["1"]["all_pairs"] == ["key_index"],
        "H5_Hvalue_m1_value_unique": value_phase["1"]["all_pairs"] == ["value_index"],
        "H6_Hkey_m2_8_value": all(key_phase[str(m)]["all_pairs"] == ["value_index"] for m in range(2, 9)),
        "H7_Hvalue_m1_8_value": all(value_phase[str(m)]["all_pairs"] == ["value_index"] for m in range(1, 9)),
        "H8_zeroK_history_erased": all(
            zero_key[str(m)]["all_pairs"] == ["value_index"] and zero_value[str(m)]["all_pairs"] == ["value_index"]
            for m in range(1, 9)
        ),
        "H9_cold_value": all(cold[str(m)]["all_pairs"] == ["value_index"] for m in range(1, 9)),
        "H10_mirrored_symmetric": (
            mirror_value["1"]["all_pairs"] == ["value_index"]
            and all(mirror_value[str(m)]["all_pairs"] == ["key_index"] for m in range(2, 9))
            and all(mirror_key[str(m)]["all_pairs"] == ["key_index"] for m in range(1, 9))
        ),
        "H11_general_theorem_grid": theorem["all_pass"],
        "H12_remint": all(remint.get(x, False) for x in ("all_exact", "costs_preserved", "heldout_history_collision_preserved")),
        "H13_selectors_agree": all(
            table[str(m)]["agree"]
            for table in (key_phase, value_phase, zero_key, zero_value, cold, mirror_key, mirror_value)
            for m in range(1, 9)
        ),
    }

    return {
        "authority": {
            "freeze_commit": FREEZE_COMMIT,
            "claim_ceiling": [
                "FINITE_EXACT_PROSPECTIVE_DEVELOPMENTAL_HISTORY_PHASE_LAW",
                "PARENT_OWNED_SWITCHING_COST_PATH_DEPENDENCE_WARMSTART",
                "NO_UNIVERSAL_HYSTERESIS_OR_REAL_SCALE_CLAIM",
            ],
        },
        "relation_family_exactness": exact,
        "migration": migration,
        "registered_blocks": {
            "main_3F_5R": {"key_index_ops": main_key_cost, "value_index_ops": main_value_cost, "key_outputs": main_key_outputs, "value_outputs": main_value_outputs},
            "mirror_5F_3R": {"key_index_ops": mirror_key_cost, "value_index_ops": mirror_value_cost, "key_outputs": mirror_key_outputs, "value_outputs": mirror_value_outputs},
        },
        "heldout_m1": {
            "H_key_vectors": {name: vector_json(v) for name, v in zip(CANDIDATES, held_key)},
            "H_key_pareto": names(pareto_all_pairs(held_key)),
            "H_value_vectors": {name: vector_json(v) for name, v in zip(CANDIDATES, held_value)},
            "H_value_pareto": names(pareto_all_pairs(held_value)),
            "same_present_scalar_occupancy": 4,
            "only_registered_difference": "semantic installed orientation",
        },
        "phase_main": {"H_key": key_phase, "H_value": value_phase},
        "controls": {
            "zero_K": {"H_key": zero_key, "H_value": zero_value},
            "cold_start": cold,
            "mirrored_ecology": {"H_key": mirror_key, "H_value": mirror_value},
        },
        "general_theorem_grid": theorem,
        "remint": remint,
        "assertions": assertions,
        "all_frozen_predictions_pass": all(assertions.values()),
    }


def main() -> None:
    result = build_results()
    out = Path(__file__).with_name("RESULT_V4.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_frozen_predictions_pass": result["all_frozen_predictions_pass"],
        "heldout_H_key": result["heldout_m1"]["H_key_pareto"],
        "heldout_H_value": result["heldout_m1"]["H_value_pareto"],
        "theorem_tuples": result["general_theorem_grid"]["tuples_checked"],
        "theorem_outcomes": result["general_theorem_grid"]["from_H_A_outcomes"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
