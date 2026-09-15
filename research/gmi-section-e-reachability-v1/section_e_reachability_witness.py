#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
from collections import deque
from fractions import Fraction
from pathlib import Path

N = 5
TARGET = (1 << 0) | (1 << 2) | (1 << 4)
BIT_PERM = (2, 4, 1, 0, 3)
VERIFY_COST = 32
PROPOSAL_COST = 1
BUDGET_VERIFICATIONS = 20

NEGATIVE_TERMINAL = "SEARCH_NEGATIVE_TARGET_REPRESENTABLE_BUT_OPERATOR_UNREACHABLE"
PLATEAU_TERMINAL = "REACHABLE_BUT_LOCAL_STRICT_IMPROVEMENT_BLOCKED_BY_PLATEAU"


def all_inputs():
    return tuple(itertools.product((0, 1), repeat=N))


def eval_mask(mask: int, x: tuple[int, ...]) -> int:
    out = 0
    for i in range(N):
        if mask & (1 << i):
            out ^= x[i]
    return out


def semantic_error(mask: int, target: int = TARGET) -> int:
    return sum(eval_mask(mask, x) != eval_mask(target, x) for x in all_inputs())


def all_error_profile(target: int = TARGET) -> dict[int, int]:
    return {mask: semantic_error(mask, target) for mask in range(1 << N)}


def single_neighbors(mask: int):
    for i in range(N):
        yield mask ^ (1 << i)


def pair_neighbors(mask: int):
    for i in range(N):
        for j in range(i + 1, N):
            yield mask ^ (1 << i) ^ (1 << j)


def bfs(target: int, neighbor_fn, stop_on_target: bool = True):
    queue = deque([0])
    seen = {0}
    evaluated = []
    proposals = 0
    while queue:
        cur = queue.popleft()
        evaluated.append(cur)
        if stop_on_target and cur == target:
            return {
                "found": True,
                "evaluated": evaluated,
                "verifications": len(evaluated),
                "proposals": proposals,
                "burden": len(evaluated) * VERIFY_COST + proposals * PROPOSAL_COST,
            }
        for nxt in neighbor_fn(cur):
            proposals += 1
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return {
        "found": target in seen,
        "evaluated": evaluated,
        "verifications": len(evaluated),
        "proposals": proposals,
        "burden": len(evaluated) * VERIFY_COST + proposals * PROPOSAL_COST,
    }


def strict_local_search(target: int):
    current = 0
    verified = {current}
    proposals = 0
    while True:
        current_error = semantic_error(current, target)
        best = None
        best_error = current_error
        for nxt in single_neighbors(current):
            proposals += 1
            verified.add(nxt)
            err = semantic_error(nxt, target)
            if err < best_error:
                best = nxt
                best_error = err
        if best is None:
            return {
                "found": current == target,
                "terminal": None if current == target else PLATEAU_TERMINAL,
                "current": current,
                "current_error": current_error,
                "verifications": len(verified),
                "proposals": proposals,
                "burden": len(verified) * VERIFY_COST + proposals * PROPOSAL_COST,
            }
        current = best
        if current == target:
            return {
                "found": True,
                "terminal": None,
                "current": current,
                "current_error": 0,
                "verifications": len(verified),
                "proposals": proposals,
                "burden": len(verified) * VERIFY_COST + proposals * PROPOSAL_COST,
            }


def prefix_lengths():
    return tuple(rank + 1 if rank <= 29 else 31 for rank in range(32))


def prefix_kraft_sum():
    return sum(Fraction(1, 1 << length) for length in prefix_lengths())


def encoding_order(target: int, mode: str):
    others = [m for m in range(32) if m != target]
    if mode == "ENC_SHORT":
        return [target] + others
    if mode == "ENC_LONG":
        return others + [target]
    raise ValueError(mode)


def levin_best_first(target: int, mode: str, budget: int | None = None):
    order = encoding_order(target, mode)
    lengths = prefix_lengths()
    ranked = [
        (1 << lengths[rank], rank, mask, lengths[rank])
        for rank, mask in enumerate(order)
    ]
    ranked.sort()
    tested = []
    proposals = 0
    for _, rank, mask, length in ranked:
        if budget is not None and len(tested) >= budget:
            break
        proposals += 1
        tested.append(mask)
        if mask == target:
            return {
                "found": True,
                "rank": rank,
                "code_length": length,
                "verifications": len(tested),
                "proposals": proposals,
                "burden": len(tested) * VERIFY_COST + proposals * PROPOSAL_COST,
                "tested": tested,
            }
    return {
        "found": False,
        "rank": None,
        "code_length": None,
        "verifications": len(tested),
        "proposals": proposals,
        "burden": len(tested) * VERIFY_COST + proposals * PROPOSAL_COST,
        "tested": tested,
    }


def remint_target(target: int = TARGET):
    inv = {old: new for new, old in enumerate(BIT_PERM)}
    support = [i for i in range(N) if target & (1 << i)]
    new_support = sorted(inv[i] for i in support)
    new_mask = sum(1 << i for i in new_support)
    return new_mask, new_support


def build_results():
    profile = all_error_profile(TARGET)
    pair = bfs(TARGET, pair_neighbors, stop_on_target=False)
    single = bfs(TARGET, single_neighbors, stop_on_target=True)
    local = strict_local_search(TARGET)

    short_full = levin_best_first(TARGET, "ENC_SHORT")
    long_full = levin_best_first(TARGET, "ENC_LONG")
    short_budget = levin_best_first(TARGET, "ENC_SHORT", BUDGET_VERIFICATIONS)
    long_budget = levin_best_first(TARGET, "ENC_LONG", BUDGET_VERIFICATIONS)

    remint, remint_support = remint_target()
    remint_profile = all_error_profile(remint)
    remint_pair = bfs(remint, pair_neighbors, stop_on_target=False)
    remint_single = bfs(remint, single_neighbors, stop_on_target=True)
    remint_local = strict_local_search(remint)

    pair_terminal = NEGATIVE_TERMINAL if (TARGET not in pair["evaluated"] and TARGET in range(32)) else "UNEXPECTED"
    budget_results = {
        "levin_short": short_budget["found"],
        "single_bfs": single["verifications"] <= BUDGET_VERIFICATIONS,
        "levin_long": long_budget["found"],
        "strict_local": local["found"],
    }

    assertions = {
        "E1_01_target_unique_exact": profile[TARGET] == 0 and all(err == 16 for m, err in profile.items() if m != TARGET),
        "E1_02_pair_parity_component": pair["verifications"] == 16 and all(mask.bit_count() % 2 == 0 for mask in pair["evaluated"]),
        "E1_03_pair_target_unreachable": not pair["found"] and TARGET not in pair["evaluated"] and pair_terminal == NEGATIVE_TERMINAL,
        "E1_04_pair_exact_burden": pair["proposals"] == 160 and pair["burden"] == 672,
        "E1_05_single_restores": single["found"] and single["verifications"] == 21 and single["proposals"] == 100 and single["burden"] == 772,
        "E1_06_constructive_path": all(b in tuple(single_neighbors(a)) for a, b in zip((0,1,5),(1,5,21))),
        "E1_07_local_plateau": local["terminal"] == PLATEAU_TERMINAL and not local["found"] and local["verifications"] == 6 and local["proposals"] == 5 and local["burden"] == 197,
        "E1_08_prefix_complete": prefix_kraft_sum() == 1,
        "E1_09_levin_short": short_full["found"] and short_full["verifications"] == 1 and short_full["code_length"] == 1 and short_full["burden"] == 33,
        "E1_10_levin_long": long_full["found"] and long_full["verifications"] == 32 and long_full["code_length"] == 31 and long_full["burden"] == 1056,
        "E1_11_prior_ratio": (1 << (long_full["code_length"] - short_full["code_length"])) == (1 << 30),
        "E1_12_budget_search_dependence": budget_results == {"levin_short": True, "single_bfs": False, "levin_long": False, "strict_local": False},
        "E1_13_complete_cross_search_recovery": single["found"] and short_full["found"] and long_full["found"] and single["evaluated"][-1] == TARGET and short_full["tested"][-1] == TARGET and long_full["tested"][-1] == TARGET,
        "E1_14_remint_target": remint == 11 and remint_support == [0,1,3],
        "E1_15_remint_semantic_profile": remint_profile[remint] == 0 and all(err == 16 for m, err in remint_profile.items() if m != remint),
        "E1_16_remint_reachability_class": not remint_pair["found"] and remint_pair["verifications"] == 16 and remint_local["terminal"] == PLATEAU_TERMINAL,
        "E1_17_remint_bfs_burden_changes": remint_single["found"] and remint_single["verifications"] == 18 and remint_single["proposals"] == 85,
    }

    return {
        "authority": {
            "issue": 710,
            "freeze_commit": "0329ea74f6d2475ed47e3e8e65c29f4105ea77fd",
            "claim_ceiling": [
                "FINITE_EXACT_PROSPECTIVE_SECTION_E_REACHABILITY_AND_SEARCH_BURDEN_V1",
                "PARENT_OWNED_LEVIN_OOPS_GRAPH_LOCAL_SEARCH_AND_ENCODING_BIAS",
                "NO_NOVEL_SEARCH_ALGORITHM_OR_REAL_SCALE_MORPHOGENESIS_CLAIM",
            ],
        },
        "world": {
            "n": N,
            "target_mask": TARGET,
            "target_support": [0,2,4],
            "non_target_error": 16,
            "candidate_count": 32,
            "verify_cost": VERIFY_COST,
            "proposal_cost": PROPOSAL_COST,
        },
        "pair_flip": {**pair, "terminal": pair_terminal},
        "single_bfs": single,
        "strict_local": local,
        "prefix": {
            "kraft_sum": str(prefix_kraft_sum()),
            "lengths": list(prefix_lengths()),
            "short": short_full,
            "long": long_full,
            "prior_mass_ratio": 1 << 30,
        },
        "budget20": budget_results,
        "remint": {
            "permutation": list(BIT_PERM),
            "target_mask": remint,
            "target_support": remint_support,
            "pair_flip": remint_pair,
            "single_bfs": remint_single,
            "strict_local": remint_local,
        },
        "assertions": assertions,
        "all_frozen_predictions_pass": all(assertions.values()),
    }


def receipt(r):
    return {
        "authority": r["authority"],
        "world": r["world"],
        "pair_flip": {k: r["pair_flip"][k] for k in ("found","verifications","proposals","burden","terminal")},
        "single_bfs": {k: r["single_bfs"][k] for k in ("found","verifications","proposals","burden")},
        "strict_local": {k: r["strict_local"][k] for k in ("found","terminal","verifications","proposals","burden","current_error")},
        "prefix": {
            "kraft_sum": r["prefix"]["kraft_sum"],
            "lengths": r["prefix"]["lengths"],
            "short": {k: r["prefix"]["short"][k] for k in ("found","rank","code_length","verifications","proposals","burden")},
            "long": {k: r["prefix"]["long"][k] for k in ("found","rank","code_length","verifications","proposals","burden")},
            "prior_mass_ratio": r["prefix"]["prior_mass_ratio"],
        },
        "budget20": r["budget20"],
        "remint": {
            "permutation": r["remint"]["permutation"],
            "target_mask": r["remint"]["target_mask"],
            "target_support": r["remint"]["target_support"],
            "pair_flip": {k: r["remint"]["pair_flip"][k] for k in ("found","verifications","proposals","burden")},
            "single_bfs": {k: r["remint"]["single_bfs"][k] for k in ("found","verifications","proposals","burden")},
            "strict_local": {k: r["remint"]["strict_local"][k] for k in ("found","terminal","verifications","proposals","burden","current_error")},
        },
        "assertions": r["assertions"],
        "all_frozen_predictions_pass": r["all_frozen_predictions_pass"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=Path(__file__).with_name("RESULT_E1.json"))
    args = ap.parse_args()
    result = build_results()
    args.output.write_text(json.dumps(receipt(result), indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "pass": result["all_frozen_predictions_pass"],
        "pair_flip": receipt(result)["pair_flip"],
        "single_bfs": receipt(result)["single_bfs"],
        "strict_local": receipt(result)["strict_local"],
        "budget20": result["budget20"],
        "remint_single_bfs": receipt(result)["remint"]["single_bfs"],
        "assertions": result["assertions"],
    }, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_frozen_predictions_pass"] else 1)


if __name__ == "__main__":
    main()
