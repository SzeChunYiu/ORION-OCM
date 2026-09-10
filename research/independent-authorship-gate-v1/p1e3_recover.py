#!/usr/bin/env python3
"""P1-E3 independent exact truth recovery over the frozen formal core.

Implements the public Implication-System semantics of
p1e3_author_spec.md (frozen by P1E3_AUTHORSHIP_FREEZE_V1.json):

  closure(base, implications)      monotone forward-chaining fixpoint
  reachable goals                  goals ∩ closure(base)
  minimum seed                     minimum-cost set S of addable elements
                                   (elements - closure(base) - excluded) whose
                                   joint closure contains every goal and no
                                   excluded element; lexicographic tie-break;
                                   IMPOSSIBLE when no S exists

This module is the independent checker. It reads ONLY the frozen interface
keys ("elements", "implications", "base", "excluded", "weights", "goals").
It imports nothing from src/ocm, nothing from the mechanism, and nothing
from the authored generators. Generator/author intent never reaches it.

Fail-closed: instances outside the frozen size bounds or over the
enumeration caps return CANNOT_CHECK with a reason. No fallback.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent

# Frozen bounds (P1E3_AUTHORSHIP_FREEZE_V1.json neutral_interface_spec).
BOUNDS = {
    "elements_max": 24,
    "implications_max": 64,
    "base_max": 24,
    "excluded_max": 12,
    "goals_max": 8,
    "seedable_elements_max": 16,
    "weights_min": 1,
    "weights_max": 99,
}
CORE_KEYS = ("elements", "implications", "base", "excluded", "weights", "goals")
MAX_EVALS_PER_INSTANCE = 70_000  # frozen enumeration cap (2^16 = 65,536 + slack)


def _cannot(reason: str) -> dict[str, Any]:
    return {"status": "CANNOT_CHECK", "reason": reason, "truth": None}


def _validate_core(core: Mapping[str, Any]) -> dict[str, Any]:
    """Structural + bounds validation of the formal core. No intent fields."""
    try:
        elements = list(core["elements"])
        implications = list(core["implications"])
        base = list(core["base"])
        excluded = list(core["excluded"]) if "excluded" in core else []
        weights = dict(core["weights"]) if "weights" in core else {}
        goals = list(core["goals"])
    except (KeyError, TypeError) as exc:
        return {"ok": False, "reason": f"malformed core: {exc}"}
    if len(set(elements)) != len(elements):
        return {"ok": False, "reason": "duplicate elements"}
    eset = set(elements)
    for lit in list(base) + list(excluded) + list(goals) + list(weights):
        if lit not in eset:
            return {"ok": False, "reason": f"unknown element referenced: {lit!r}"}
    for rule in implications:
        if not isinstance(rule, Mapping) or "if" not in rule or "then" not in rule:
            return {"ok": False, "reason": "malformed implication"}
        for lit in list(rule["if"]) + list(rule["then"]):
            if lit not in eset:
                return {"ok": False, "reason": f"unknown element in implication: {lit!r}"}
    for w in weights.values():
        if not isinstance(w, int) or not (BOUNDS["weights_min"] <= w <= BOUNDS["weights_max"]):
            return {"ok": False, "reason": f"weight out of range: {w!r}"}
    if len(elements) > BOUNDS["elements_max"]:
        return {"ok": False, "reason": f"|elements|={len(elements)} > {BOUNDS['elements_max']}"}
    if len(implications) > BOUNDS["implications_max"]:
        return {"ok": False, "reason": f"|implications|={len(implications)} > {BOUNDS['implications_max']}"}
    if len(base) > BOUNDS["base_max"]:
        return {"ok": False, "reason": f"|base|={len(base)} > {BOUNDS['base_max']}"}
    if len(excluded) > BOUNDS["excluded_max"]:
        return {"ok": False, "reason": f"|excluded|={len(excluded)} > {BOUNDS['excluded_max']}"}
    if len(goals) > BOUNDS["goals_max"]:
        return {"ok": False, "reason": f"|goals|={len(goals)} > {BOUNDS['goals_max']}"}
    return {
        "ok": True,
        "elements": elements,
        "implications": [dict(r) for r in implications],
        "base": list(dict.fromkeys(base)),
        "excluded": list(dict.fromkeys(excluded)),
        "weights": weights,
        "goals": list(dict.fromkeys(goals)),
    }


def closure(holding: frozenset[str], implications) -> frozenset[str]:
    """Monotone forward-chaining fixpoint. Unique by construction."""
    current = set(holding)
    changed = True
    while changed:
        changed = False
        for rule in implications:
            if all(a in current for a in rule["if"]):
                for b in rule["then"]:
                    if b not in current:
                        current.add(b)
                        changed = True
    return frozenset(current)


def recover_core(core: Mapping[str, Any]) -> dict[str, Any]:
    """Recover the three truths from the formal core alone. Fail-closed."""
    v = _validate_core(core)
    if not v["ok"]:
        return _cannot(v["reason"])
    elements, implications, base = v["elements"], v["implications"], v["base"]
    excluded, weights, goals = v["excluded"], v["weights"], v["goals"]

    base_closure = closure(frozenset(base), implications)

    # Minimum seed: candidates are elements not already derivable and not excluded.
    addable = sorted(set(elements) - base_closure - set(excluded))
    if len(addable) > BOUNDS["seedable_elements_max"]:
        return _cannot(
            f"addable elements {len(addable)} > {BOUNDS['seedable_elements_max']} "
            "(exact enumeration outside frozen bounds)"
        )
    goal_set = set(goals)
    excl_set = set(excluded)
    cost_of = {e: weights.get(e, 1) for e in elements}

    best = None  # (cost, tuple(seed)) — lexicographic on tuple within equal cost
    evals = 0
    # Every successful seed dominates its supersets (weights are >= 1, so any
    # superset costs at least as much and cannot beat it on the lex tie-break).
    known_success_seeds: list[frozenset[str]] = []

    # Sizes beyond the incumbent cost cannot win (every weight >= 1).
    max_k = len(addable)
    for k in range(0, min(len(addable), max(max_k, 0)) + 1):
        if best is not None and k > best[0] - 1:
            break
        for combo in itertools.combinations(addable, k):
            if best is not None:
                cost = sum(cost_of[e] for e in combo)
                if cost > best[0]:
                    continue
                combo_set = frozenset(combo)
                if any(s <= combo_set for s in known_success_seeds):
                    continue  # dominated by a cheaper-or-equal successful seed
            evals += 1
            if evals > MAX_EVALS_PER_INSTANCE:
                return _cannot(f"enumeration cap exceeded ({MAX_EVALS_PER_INSTANCE} closure evaluations)")
            joint = closure(frozenset(base) | frozenset(combo), implications)
            if excl_set_local := (joint & excl_set):
                continue
            if not goal_set <= joint:
                continue
            cost = sum(cost_of[e] for e in combo)
            key = (cost, tuple(sorted(combo)))
            if best is None or key < best:
                best = key
                known_success_seeds.append(frozenset(combo))

    if best is None:
        min_seed = {"possible": False, "seed": [], "cost": None, "status": "IMPOSSIBLE"}
    else:
        min_seed = {
            "possible": True,
            "seed": list(best[1]),
            "cost": best[0],
            "status": "MIN_SEED_RECOVERED",
            "tie_break": "minimum cost, then lexicographically smallest seed",
        }

    truth = {
        "closure": sorted(base_closure),
        "closure_size": len(base_closure),
        "reachable_goals": sorted(g for g in goals if g in base_closure),
        "unreachable_goals": sorted(g for g in goals if g not in base_closure),
        "addable_elements": addable,
        "min_seed": min_seed,
        "closure_evaluations": evals,
    }
    return {"status": "RECOVERED", "reason": None, "truth": truth}


def recover_instance(instance: Mapping[str, Any]) -> dict[str, Any]:
    """Recover truth for one authored instance, reading ONLY instance['core'].

    Code-level guarantee: the intent/surface fields are stripped before the
    core is even looked at; recover_core can never see them.
    """
    if not isinstance(instance, Mapping):
        return _cannot("instance is not an object")
    core = instance.get("core")
    if not isinstance(core, Mapping):
        return _cannot("instance has no formal core")
    if any(k not in core for k in ("elements", "implications", "base", "goals")):
        return _cannot("core missing required frozen keys")
    return recover_core({k: core.get(k) for k in CORE_KEYS})


# --------------------------------------------------------------------------
# Known-answer control (hand-computed; P1E3_AUTHORSHIP_FREEZE hostile
# H-P1E3-3). Every expected value below was derived by hand from the public
# semantics, not by running this module's search paths first.
# --------------------------------------------------------------------------

def _hand_case_a() -> dict:
    core = {
        "elements": ["a", "b", "c"],
        "implications": [{"if": ["a"], "then": ["b"]}],
        "base": ["a"],
        "excluded": [],
        "weights": {},
        "goals": ["b"],
    }
    expected = {
        "closure": ["a", "b"],
        "reachable_goals": ["b"],
        "min_seed": {"possible": True, "seed": [], "cost": 0},
    }
    return {"case_id": "hand-A-trivial-chain", "core": core, "expected": expected}


def _hand_case_b() -> dict:
    # Hand computation: closure(base={}) = {}. goals={d}.
    # addable = elements - closure - excluded = {a, c, d}.
    #   {d}: closure={d} ⊇ goals, no excluded -> cost 1 (d absent from weights).
    #   {c}: closure={c,d} -> cost 2.
    #   {a}: closure={a,b} hits excluded b -> disqualified.
    # min seed = {d}, cost 1.
    core = {
        "elements": ["a", "b", "c", "d"],
        "implications": [
            {"if": ["a"], "then": ["b"]},
            {"if": ["c"], "then": ["d"]},
        ],
        "base": [],
        "excluded": ["b"],
        "weights": {"a": 1, "c": 2},
        "goals": ["d"],
    }
    expected = {
        "closure": [],
        "reachable_goals": [],
        "addable_contains": ["a", "c", "d"],
        "min_seed": {"possible": True, "seed": ["d"], "cost": 1},
    }
    return {"case_id": "hand-B-default-weight-wins", "core": core, "expected": expected}


def _hand_case_c() -> dict:
    # goals contains z; z is excluded, so it can never be added and no rule
    # derives it -> IMPOSSIBLE.
    core = {
        "elements": ["x", "y", "z"],
        "implications": [{"if": ["x"], "then": ["y"]}],
        "base": ["x"],
        "excluded": ["z"],
        "weights": {},
        "goals": ["z"],
    }
    expected = {
        "closure": ["x", "y"],
        "reachable_goals": [],
        "min_seed": {"possible": False, "status": "IMPOSSIBLE"},
    }
    return {"case_id": "hand-C-impossible-goal", "core": core, "expected": expected}


def _hand_case_d() -> dict:
    # Hand computation: direct add of g costs 5; {m} and {n} both cost 1 and
    # both derive g. Minimum cost is 1, and between the two equal-cost single
    # seeds the lexicographically smaller ({m}) must win. (First draft of this
    # fixture priced g at 1 and wrongly expected {m}: with g addable at cost 1
    # the true min seed is {g} — the checker caught the hand error, which is
    # exactly what a known-answer control is for.)
    core = {
        "elements": ["m", "n", "g"],
        "implications": [
            {"if": ["n"], "then": ["g"]},
            {"if": ["m"], "then": ["g"]},
        ],
        "base": [],
        "excluded": [],
        "weights": {"m": 1, "n": 1, "g": 5},
        "goals": ["g"],
    }
    expected = {
        "closure": [],
        "min_seed": {"possible": True, "seed": ["m"], "cost": 1},
    }
    return {"case_id": "hand-D-lex-tiebreak", "core": core, "expected": expected}


def known_answer_cases() -> list[dict]:
    return [_hand_case_a(), _hand_case_b(), _hand_case_c(), _hand_case_d()]


def run_known_answer_control() -> dict:
    rows = []
    all_ok = True
    for case in known_answer_cases():
        rec = recover_core(case["core"])
        exp = case["expected"]
        ok = rec["status"] == "RECOVERED"
        detail: dict[str, Any] = {}
        if ok:
            t = rec["truth"]
            if "closure" in exp:
                detail["closure_ok"] = t["closure"] == exp["closure"]
            if "reachable_goals" in exp:
                detail["reachable_goals_ok"] = t["reachable_goals"] == exp["reachable_goals"]
            if "addable_contains" in exp:
                detail["addable_ok"] = all(e in t["addable_elements"] for e in exp["addable_contains"])
            ms = t["min_seed"]
            ems = exp["min_seed"]
            detail["min_seed_possible_ok"] = ms["possible"] == ems["possible"]
            if ems["possible"]:
                detail["min_seed_seed_ok"] = ms["seed"] == ems["seed"]
                detail["min_seed_cost_ok"] = ms["cost"] == ems["cost"]
            else:
                detail["min_seed_status_ok"] = ms.get("status") == ems.get("status")
            case_ok = ok and all(detail.values())
        else:
            case_ok = False
        all_ok = all_ok and case_ok
        rows.append({
            "case_id": case["case_id"],
            "recovery_status": rec["status"],
            "checks": detail,
            "all_match": case_ok,
        })
    return {"all_match": all_ok, "n_cases": len(rows), "rows": rows}


def main() -> int:
    ctrl = run_known_answer_control()
    print(json.dumps({k: ctrl[k] for k in ("all_match", "n_cases")}, indent=2))
    for r in ctrl["rows"]:
        print(r["case_id"], "OK" if r["all_match"] else f"MISMATCH {r['checks']}")
    return 0 if ctrl["all_match"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
