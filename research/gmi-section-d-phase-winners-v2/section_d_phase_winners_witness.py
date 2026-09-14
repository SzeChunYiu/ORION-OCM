#!/usr/bin/env python3
"""Exact finite witness for Section D phase winners V2 + neural replication V3.

Stdlib only. No randomness outside the explicitly frozen 32-bit LCG.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from collections import deque
import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

CLAIM_CEILING = [
    "FINITE_EXACT_PROSPECTIVE_SECTION_D_PHASE_LAW_V2_WITH_RECORDED_V2_N_FAILURE",
    "FINITE_EXACT_PROSPECTIVE_NEURAL_LIKE_PHASE_REPLICATION_V3",
    "PARENT_OWNED_BAYES_THRESHOLD_SEARCH",
    "NO_UNIVERSAL_NEURAL_PROBABILISTIC_PLANNING_OR_REAL_SCALE_CLAIM",
]

V2_FREEZE_COMMIT = "b8c407428cfb76dda736d9867e50c1c8a365eabb"
V3_FREEZE_COMMIT = "e08f9ddcc53516fafc685f8da5bd182c0c9df7d0"


@dataclass(frozen=True)
class EvalVector:
    valid: bool
    persistent: int
    working: int
    ops: int
    over_cap: bool = False


def dominates(a: EvalVector, b: EvalVector) -> bool:
    if not a.valid or a.over_cap or not b.valid or b.over_cap:
        return False
    av = (a.persistent, a.working, a.ops)
    bv = (b.persistent, b.working, b.ops)
    return all(x <= y for x, y in zip(av, bv)) and any(x < y for x, y in zip(av, bv))


def pareto_indices(vectors: Sequence[EvalVector]) -> Tuple[int, ...]:
    eligible = [i for i, v in enumerate(vectors) if v.valid and not v.over_cap]
    out = []
    for i in eligible:
        if not any(j != i and dominates(vectors[j], vectors[i]) for j in eligible):
            out.append(i)
    return tuple(out)


def stochastic_retained(vectors: Sequence[EvalVector], seed: int, proposals: int = 64) -> Tuple[int, ...]:
    """Frozen Search B. Candidate names are intentionally absent from this API."""
    state = seed + 1
    sampled: List[int] = []
    k = len(vectors)
    for _ in range(proposals):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        sampled.append(state % k)
    unique = sorted(set(sampled))
    sampled_vectors = [vectors[i] for i in unique]
    local_front = pareto_indices(sampled_vectors)
    return tuple(unique[i] for i in local_front)


P_CONTEXTS = ((3, 1), (4, 1), (5, 1), (5, 2), (6, 1), (7, 2), (8, 3), (9, 4))
P_NAMES = ("point_only", "raw_history_replay", "count_replay", "belief_weights")


def p_weights(n1: int, t: int = 12) -> Tuple[int, int]:
    n0 = t - n1
    return (2 ** n0, 2 ** n1)


def p_bayes_action(n1: int, W: int, S: int, t: int = 12, priority: Sequence[str] = ("guess_0", "safe", "guess_1")) -> str:
    w0, w1 = p_weights(n1, t)
    losses = {
        "guess_0": W * w1,
        "safe": S * (w0 + w1),
        "guess_1": W * w0,
    }
    rank = {name: i for i, name in enumerate(priority)}
    return min(losses, key=lambda name: (losses[name], rank[name]))


def p_point_label(n1: int, t: int = 12) -> int:
    return 1 if n1 >= t - n1 else 0


def p_point_valid(t: int = 12) -> Tuple[bool, List[dict]]:
    conflicts = []
    for W, S in P_CONTEXTS:
        groups: Dict[int, Dict[str, List[int]]] = {0: {}, 1: {}}
        for n1 in range(t + 1):
            label = p_point_label(n1, t)
            action = p_bayes_action(n1, W, S, t)
            groups[label].setdefault(action, []).append(n1)
        for label, by_action in groups.items():
            if len(by_action) > 1:
                conflicts.append({
                    "context": [W, S],
                    "point_label": label,
                    "actions": {k: v for k, v in sorted(by_action.items())},
                })
    return (not conflicts, conflicts)


def p_map_sufficient_01(t: int = 12) -> bool:
    for n1 in range(t + 1):
        target = "guess_1" if n1 >= t - n1 else "guess_0"
        point_action = "guess_1" if p_point_label(n1, t) == 1 else "guess_0"
        if target != point_action:
            return False
    return True


def p_vectors(q: int, t: int = 12) -> List[EvalVector]:
    point_ok, _ = p_point_valid(t)
    return [
        EvalVector(point_ok, 1, 1, t + q, False),
        EvalVector(True, t, 2, t + q * (2 * t + 4), False),
        EvalVector(True, 2, 2, t + q * (t + 4), False),
        EvalVector(True, 2, 2, 2 * t + 4 * q, False),
    ]


def p_remint_ok(t: int = 12) -> bool:
    swap_action = {"guess_0": "guess_1", "guess_1": "guess_0", "safe": "safe"}
    for n1 in range(t + 1):
        for W, S in P_CONTEXTS:
            base = p_bayes_action(n1, W, S, t)
            reminted = p_bayes_action(t - n1, W, S, t, priority=("guess_1", "safe", "guess_0"))
            if reminted != swap_action[base]:
                return False
    return True


N_V2_NAMES = (
    "full_map", "default_exceptions", "affine_fold", "one_cutoff",
    "cutoff_plus_exceptions", "weighted_local_composition",
)
N_V3_NAMES = N_V2_NAMES


def shell_value(bits: Sequence[int], k: int) -> int:
    return int(sum(bits) == k)


def cutoff_value(bits: Sequence[int], threshold: int, polarity: int) -> int:
    v = int(sum(bits) >= threshold)
    return v if polarity == 1 else 1 - v


def best_cutoff_residual(n: int, k: int) -> dict:
    best = None
    all_rows = []
    for threshold in range(0, n + 2):
        for polarity in (0, 1):
            errors = sum(
                cutoff_value(bits, threshold, polarity) != shell_value(bits, k)
                for bits in product((0, 1), repeat=n)
            )
            row = {"errors": errors, "threshold": threshold, "polarity": polarity}
            all_rows.append(row)
            key = (errors, threshold, polarity)
            if best is None or key < (best["errors"], best["threshold"], best["polarity"]):
                best = row
    assert best is not None
    return {"best": best, "all": all_rows}


def affine_exact_exists(n: int, k: int) -> bool:
    inputs = list(product((0, 1), repeat=n))
    targets = [shell_value(x, k) for x in inputs]
    for mask in range(1 << n):
        for bias in (0, 1):
            ok = True
            for x, y in zip(inputs, targets):
                acc = bias
                for i, bit in enumerate(x):
                    if (mask >> i) & 1:
                        acc ^= bit
                if acc != y:
                    ok = False
                    break
            if ok:
                return True
    return False


def one_cutoff_exact_exists(n: int, k: int) -> bool:
    for t in range(0, n + 2):
        for p in (0, 1):
            if all(cutoff_value(x, t, p) == shell_value(x, k) for x in product((0, 1), repeat=n)):
                return True
    return False


def weighted_shell_value(bits: Sequence[int], k: int) -> int:
    s = sum(bits)
    h_lo = int(s >= k)
    h_hi = int(s >= k + 1)
    return int(h_lo - h_hi >= 1)


def weighted_shell_exact(n: int, k: int) -> bool:
    return all(weighted_shell_value(x, k) == shell_value(x, k) for x in product((0, 1), repeat=n))


def shell_remint_ok(n: int, k: int, perm: Sequence[int]) -> bool:
    for x in product((0, 1), repeat=n):
        xr = tuple(x[i] for i in perm)
        if shell_value(x, k) != shell_value(xr, k):
            return False
        if weighted_shell_value(x, k) != weighted_shell_value(xr, k):
            return False
    return True


def n_v3_vectors(q: int = 16, cap: int = 32) -> List[EvalVector]:
    n, k = 9, 4
    residual = best_cutoff_residual(n, k)["best"]["errors"]
    shell_count = sum(shell_value(x, k) for x in product((0, 1), repeat=n))
    affine_ok = affine_exact_exists(n, k)
    cutoff_ok = one_cutoff_exact_exists(n, k)
    weighted_ok = weighted_shell_exact(n, k)
    verify = 1 << n
    return [
        EvalVector(True, 1 << n, 1, (1 << n) + verify + q, (1 << n) > cap),
        EvalVector(True, 1 + shell_count, 2, (1 + shell_count) + verify + 2 * q, (1 + shell_count) > cap),
        EvalVector(affine_ok, n + 1, 1, (n + 1) + verify + n * q, (n + 1) > cap),
        EvalVector(cutoff_ok, 2, 1, 2 + verify + n * q, 2 > cap),
        EvalVector(True, 2 + residual, 2, (2 + residual) + verify + (n + 1) * q, (2 + residual) > cap),
        EvalVector(weighted_ok, 23, 3, 23 + verify + 20 * q, 23 > cap),
    ]


def n_twin_vectors(q: int = 16) -> Tuple[EvalVector, EvalVector]:
    verify = 512
    cutoff = EvalVector(True, 2, 1, 2 + verify + 9 * q, False)
    weighted = EvalVector(True, 23, 3, 23 + verify + 20 * q, False)
    return cutoff, weighted


S_NAMES = ("token_greedy", "online_bfs", "compiled_all_pairs")
S_BASE_EDGES = (
    (0, 1), (0, 2), (1, 3), (3, 7), (2, 4),
    (4, 5), (5, 6), (6, 7), (1, 4), (2, 5),
)
S_PERM = (6, 2, 7, 0, 5, 1, 4, 3)


def make_adj(edges: Iterable[Tuple[int, int]]) -> Dict[int, Tuple[int, ...]]:
    tmp = {i: set() for i in range(8)}
    for a, b in edges:
        tmp[a].add(b)
        tmp[b].add(a)
    return {i: tuple(sorted(tmp[i])) for i in range(8)}


def shortest_distance(adj: Dict[int, Tuple[int, ...]], s: int, g: int) -> int:
    q = deque([(s, 0)])
    seen = {s}
    while q:
        u, d = q.popleft()
        if u == g:
            return d
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append((v, d + 1))
    raise AssertionError("graph disconnected")


def bfs_first_hop(adj: Dict[int, Tuple[int, ...]], s: int, g: int) -> int:
    q = deque([s])
    pred = {s: None}
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in pred:
                pred[v] = u
                q.append(v)
    assert g in pred
    cur = g
    while pred[cur] != s:
        cur = pred[cur]
        assert cur is not None
    return cur


def token_greedy_first(adj: Dict[int, Tuple[int, ...]], s: int, g: int) -> int | None:
    cur = s
    seen = {s}
    first = None
    while cur != g:
        opts = [v for v in adj[cur] if v not in seen]
        if not opts:
            return None
        nxt = min(opts, key=lambda v: (abs(v - g), v))
        if first is None:
            first = nxt
        seen.add(nxt)
        cur = nxt
    return first


def first_hop_is_shortest(adj: Dict[int, Tuple[int, ...]], s: int, g: int, hop: int | None) -> bool:
    return hop is not None and hop in adj[s] and 1 + shortest_distance(adj, hop, g) == shortest_distance(adj, s, g)


def s_validity(edges: Iterable[Tuple[int, int]]) -> dict:
    adj = make_adj(edges)
    greedy_failures = []
    bfs_failures = []
    compiled_failures = []
    compiled = {}
    for s in range(8):
        for g in range(8):
            if s == g:
                continue
            bh = bfs_first_hop(adj, s, g)
            compiled[(s, g)] = bh
            if not first_hop_is_shortest(adj, s, g, bh):
                bfs_failures.append([s, g, bh])
            gh = token_greedy_first(adj, s, g)
            if not first_hop_is_shortest(adj, s, g, gh):
                greedy_failures.append([s, g, gh])
    for (s, g), hop in compiled.items():
        if not first_hop_is_shortest(adj, s, g, hop):
            compiled_failures.append([s, g, hop])
    return {
        "greedy_failures": greedy_failures,
        "bfs_failures": bfs_failures,
        "compiled_failures": compiled_failures,
        "ordered_pairs_checked": 56,
    }


def s_vectors(q: int) -> List[EvalVector]:
    validity = s_validity(S_BASE_EDGES)
    return [
        EvalVector(not validity["greedy_failures"], 1, 1, q, False),
        EvalVector(not validity["bfs_failures"], 1, 8, 28 * q, False),
        EvalVector(not validity["compiled_failures"], 57, 8, 224 + q, False),
    ]


def remint_edges(edges: Iterable[Tuple[int, int]], perm: Sequence[int]) -> Tuple[Tuple[int, int], ...]:
    return tuple((perm[a], perm[b]) for a, b in edges)


def s_remint_ok() -> bool:
    base = s_validity(S_BASE_EDGES)
    rem = s_validity(remint_edges(S_BASE_EDGES, S_PERM))
    if base["bfs_failures"] or base["compiled_failures"]:
        return False
    if rem["bfs_failures"] or rem["compiled_failures"]:
        return False
    return pareto_indices(s_vectors(4)) == (1,)


def stochastic_success(vectors: Sequence[EvalVector], winner: int) -> dict:
    successes = []
    for seed in range(100):
        front = stochastic_retained(vectors, seed, 64)
        if winner in front:
            successes.append(seed)
    return {
        "seeds": 100,
        "proposals_per_seed": 64,
        "success_count": len(successes),
        "failure_seeds": [s for s in range(100) if s not in successes],
        "criterion_at_least_95": len(successes) >= 95,
    }


def vector_json(v: EvalVector) -> dict:
    return {
        "valid": v.valid,
        "persistent_cells": v.persistent,
        "working_cells": v.working,
        "lifecycle_ops": v.ops,
        "over_cap": v.over_cap,
    }


def build_results() -> dict:
    p_ok, p_conflicts = p_point_valid(12)
    p_phase = {}
    for q in range(1, 13):
        vecs = p_vectors(q)
        p_phase[str(q)] = [P_NAMES[i] for i in pareto_indices(vecs)]

    v2_residual = best_cutoff_residual(8, 4)["best"]
    v3_residual = best_cutoff_residual(9, 4)["best"]
    v3_vectors = n_v3_vectors()
    v3_front = pareto_indices(v3_vectors)
    twin_cutoff, twin_weighted = n_twin_vectors()

    s_phase = {}
    for q in range(1, 17):
        s_phase[str(q)] = [S_NAMES[i] for i in pareto_indices(s_vectors(q))]
    s_val = s_validity(S_BASE_EDGES)

    p_held = p_vectors(8)
    s_held = s_vectors(4)

    return {
        "authority": {
            "v2_freeze_commit": V2_FREEZE_COMMIT,
            "v3_freeze_commit": V3_FREEZE_COMMIT,
            "v2_overall_status": "FAILED_PREREGISTRATION",
            "v2_failed_prediction": "N3 cutoff+exceptions residual predicted 56, observed 70",
            "claim_ceiling": CLAIM_CEILING,
        },
        "P_probabilistic": {
            "point_only_valid": p_ok,
            "point_conflict_count": len(p_conflicts),
            "registered_exhibit": {
                "n1_6": p_bayes_action(6, 3, 1, 12),
                "n1_7": p_bayes_action(7, 3, 1, 12),
                "same_point_label": p_point_label(6, 12) == p_point_label(7, 12) == 1,
            },
            "heldout_T": 12,
            "heldout_Q": 8,
            "heldout_vectors": {name: vector_json(v) for name, v in zip(P_NAMES, p_held)},
            "heldout_pareto": [P_NAMES[i] for i in pareto_indices(p_held)],
            "phase_Q_1_to_12": p_phase,
            "q1_count_belief_tie": (
                p_vectors(1)[2].persistent == p_vectors(1)[3].persistent
                and p_vectors(1)[2].working == p_vectors(1)[3].working
                and p_vectors(1)[2].ops == p_vectors(1)[3].ops
            ),
            "belief_strictly_dominates_count_q2_to_12": all(dominates(p_vectors(q)[3], p_vectors(q)[2]) for q in range(2, 13)),
            "negative_twin_MAP_sufficient": p_map_sufficient_01(12),
            "remint_ok": p_remint_ok(12),
        },
        "N_v2_failure": {
            "frozen_predicted_best_residual": 56,
            "observed_best_residual": v2_residual["errors"],
            "observed_best_threshold": v2_residual["threshold"],
            "observed_best_polarity": v2_residual["polarity"],
            "prediction_passed": v2_residual["errors"] == 56,
            "qualitative_cap32_winner_not_claimed_from_v2": "weighted_local_composition",
        },
        "N_v3_neural_replication": {
            "n": 9,
            "target_weight": 4,
            "inputs_checked": 512,
            "shell_size": 126,
            "full_map_cells": 512,
            "default_exceptions_cells": 127,
            "best_cutoff_residual": v3_residual["errors"],
            "best_cutoff_threshold": v3_residual["threshold"],
            "best_cutoff_polarity": v3_residual["polarity"],
            "cutoff_plus_exceptions_cells": 2 + v3_residual["errors"],
            "affine_exact_exists": affine_exact_exists(9, 4),
            "one_cutoff_exact_exists": one_cutoff_exact_exists(9, 4),
            "weighted_local_composition_exact": weighted_shell_exact(9, 4),
            "weighted_local_composition_cells": 23,
            "memory_cap": 32,
            "heldout_vectors": {name: vector_json(v) for name, v in zip(N_V3_NAMES, v3_vectors)},
            "heldout_pareto": [N_V3_NAMES[i] for i in v3_front],
            "negative_twin_cutoff_dominates_weighted": dominates(twin_cutoff, twin_weighted),
            "remint_ok": shell_remint_ok(9, 4, (8, 3, 0, 6, 1, 7, 4, 2, 5)),
        },
        "S_online_planning": {
            "nodes": 8,
            "edges": 10,
            "ordered_pairs_checked": s_val["ordered_pairs_checked"],
            "token_greedy_failure_count": len(s_val["greedy_failures"]),
            "token_greedy_failure_examples": s_val["greedy_failures"][:5],
            "bfs_failure_count": len(s_val["bfs_failures"]),
            "compiled_failure_count": len(s_val["compiled_failures"]),
            "heldout_Q": 4,
            "heldout_vectors": {name: vector_json(v) for name, v in zip(S_NAMES, s_held)},
            "heldout_pareto": [S_NAMES[i] for i in pareto_indices(s_held)],
            "phase_Q_1_to_16": s_phase,
            "online_dominates_compiled_Q_1_to_8": all(dominates(s_vectors(q)[1], s_vectors(q)[2]) for q in range(1, 9)),
            "q9_to_16_tradeoff": all(
                not dominates(s_vectors(q)[1], s_vectors(q)[2]) and not dominates(s_vectors(q)[2], s_vectors(q)[1])
                for q in range(9, 17)
            ),
            "remint_ok": s_remint_ok(),
        },
        "stochastic_search_replication": {
            "algorithm": "seeded_LCG_uniform_sampling_with_replacement_plus_sampled_pareto",
            "candidate_labels_visible_to_search": False,
            "P": stochastic_success(p_held, 3),
            "N_v3": stochastic_success(v3_vectors, 5),
            "S": stochastic_success(s_held, 1),
        },
    }


def main() -> None:
    result = build_results()
    out = Path(__file__).with_name("RESULT_V2_V3.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "v2_status": result["authority"]["v2_overall_status"],
        "P_winner": result["P_probabilistic"]["heldout_pareto"],
        "N_v2_residual_observed": result["N_v2_failure"]["observed_best_residual"],
        "N_v3_winner": result["N_v3_neural_replication"]["heldout_pareto"],
        "S_winner": result["S_online_planning"]["heldout_pareto"],
        "stochastic_successes": {
            k: v["success_count"] for k, v in result["stochastic_search_replication"].items() if isinstance(v, dict)
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
