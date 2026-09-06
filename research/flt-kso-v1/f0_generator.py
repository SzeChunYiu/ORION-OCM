#!/usr/bin/env python3
"""Isolated, model-free typed proof-AST generator for the preregistered F0 gate.

Input and output are JSON only.  This process receives no Lean source and emits no Lean source.
It performs structural unification/backward search over registered local hypotheses and lemma
signatures.  A separate trusted host validates and renders the returned AST.
"""
from __future__ import annotations

import copy
import json
import sys
from dataclasses import dataclass
from typing import Any

Expr = Any
Subst = dict[str, Expr]


class BudgetExceeded(RuntimeError):
    pass


def _is_meta(x: Expr) -> bool:
    return isinstance(x, list) and len(x) == 2 and x[0] == "?" and isinstance(x[1], str)


def _walk(x: Expr, subst: Subst) -> Expr:
    seen: set[str] = set()
    while _is_meta(x) and x[1] in subst:
        name = x[1]
        if name in seen:
            raise ValueError("cyclic substitution")
        seen.add(name)
        x = subst[name]
    if isinstance(x, list):
        return [_walk(v, subst) for v in x]
    return x


def _occurs(name: str, x: Expr, subst: Subst) -> bool:
    x = _walk(x, subst)
    if _is_meta(x):
        return x[1] == name
    return isinstance(x, list) and any(_occurs(name, v, subst) for v in x)


def unify(a: Expr, b: Expr, subst: Subst) -> Subst | None:
    out = copy.deepcopy(subst)

    def go(x: Expr, y: Expr) -> bool:
        x, y = _walk(x, out), _walk(y, out)
        if x == y:
            return True
        if _is_meta(x):
            if _occurs(x[1], y, out):
                return False
            out[x[1]] = y
            return True
        if _is_meta(y):
            if _occurs(y[1], x, out):
                return False
            out[y[1]] = x
            return True
        if isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
            return all(go(xi, yi) for xi, yi in zip(x, y))
        return False

    return out if go(a, b) else None


def _rename_metas(x: Expr, suffix: str, mapping: dict[str, str]) -> Expr:
    if _is_meta(x):
        old = x[1]
        mapping.setdefault(old, f"{old}@{suffix}")
        return ["?", mapping[old]]
    if isinstance(x, list):
        return [_rename_metas(v, suffix, mapping) for v in x]
    return x


def _fresh_rule(rule: dict[str, Any], serial: int) -> tuple[dict[str, Any], dict[str, str]]:
    mapping: dict[str, str] = {}
    fresh = copy.deepcopy(rule)
    fresh["conclusion"] = _rename_metas(fresh["conclusion"], str(serial), mapping)
    fresh["premises"] = [_rename_metas(p, str(serial), mapping) for p in fresh["premises"]]
    return fresh, mapping


def _canonical(x: Expr, subst: Subst) -> str:
    return json.dumps(_walk(x, subst), sort_keys=True, separators=(",", ":"))


@dataclass
class Counters:
    expansions: int = 0
    candidates: int = 0
    duplicate_states: int = 0
    rule_serial: int = 0


def solve(request: dict[str, Any]) -> dict[str, Any]:
    target = request["target"]
    context = list(request["context"])
    rules = list(request["rules"])
    max_expansions = int(request["budget"]["max_expansions"])
    max_candidates = int(request["budget"]["max_candidates"])
    counters = Counters()
    events: list[dict[str, Any]] = []
    active: set[str] = set()
    failed: set[str] = set()

    def charge_candidate() -> None:
        counters.candidates += 1
        if counters.candidates > max_candidates:
            raise BudgetExceeded("candidate budget exceeded")

    def prove(goal: Expr, subst: Subst) -> tuple[dict[str, Any], Subst] | None:
        normalized = _walk(goal, subst)
        state_id = _canonical(normalized, {})
        if state_id in active or state_id in failed:
            counters.duplicate_states += 1
            events.append({"op": "DEDUP", "goal": normalized, "outcome": "SKIP"})
            return None
        if counters.expansions >= max_expansions:
            raise BudgetExceeded("proof-state budget exceeded")
        counters.expansions += 1
        active.add(state_id)

        for hyp in context:
            charge_candidate()
            unified = unify(hyp["type"], normalized, subst)
            if unified is not None:
                active.remove(state_id)
                events.append({"op": "LOCAL_HYPOTHESIS", "id": hyp["id"], "goal": normalized, "outcome": "CLOSED"})
                return {"op": "LOCAL_HYPOTHESIS", "id": hyp["id"]}, unified
            events.append({"op": "LOCAL_HYPOTHESIS", "id": hyp["id"], "goal": normalized, "outcome": "REJECTED"})

        for rule in rules:
            charge_candidate()
            counters.rule_serial += 1
            fresh, mapping = _fresh_rule(rule, counters.rule_serial)
            unified = unify(fresh["conclusion"], normalized, subst)
            if unified is None:
                events.append({"op": "APPLY_LEMMA", "id": rule["id"], "goal": normalized, "outcome": "REJECTED"})
                continue
            children: list[dict[str, Any]] = []
            running = unified
            ok = True
            for premise in fresh["premises"]:
                subgoal = _walk(premise, running)
                answer = prove(subgoal, running)
                if answer is None:
                    ok = False
                    break
                child, running = answer
                children.append(child)
            if ok:
                bindings: dict[str, Expr] = {}
                for original in rule.get("render_metas", []):
                    fresh_name = mapping.get(original)
                    if fresh_name is None:
                        raise ValueError(f"render meta {original} absent from rule")
                    value = _walk(["?", fresh_name], running)
                    if _is_meta(value):
                        raise ValueError(f"unresolved render meta: {original}")
                    bindings[original] = value
                active.remove(state_id)
                events.append({"op": "APPLY_LEMMA", "id": rule["id"], "goal": normalized, "outcome": "CLOSED"})
                return {
                    "op": "APPLY_LEMMA",
                    "id": rule["id"],
                    "bindings": bindings,
                    "premises": children,
                }, running
            events.append({"op": "APPLY_LEMMA", "id": rule["id"], "goal": normalized, "outcome": "FAILED_PREMISE"})

        active.remove(state_id)
        failed.add(state_id)
        return None

    try:
        answer = prove(target, {})
    except BudgetExceeded as exc:
        return {
            "schema": "flt-kso-v1.f0-generator-result.v1",
            "terminal": "FAILED_UNDER_BUDGET",
            "reason": str(exc),
            "proof_state_expansions": counters.expansions,
            "operator_candidates_considered": counters.candidates,
            "duplicate_states_avoided": counters.duplicate_states,
            "events": events,
            "llm_calls": 0,
            "llm_tokens": 0,
            "foundation_model_calls": 0,
        }
    if answer is None:
        terminal, ast = "NO_PROOF_FOUND_UNDER_GRAMMAR", None
    else:
        ast, _ = answer
        terminal = "CANDIDATE_AST_CONSTRUCTED"
    return {
        "schema": "flt-kso-v1.f0-generator-result.v1",
        "terminal": terminal,
        "proof_ast": ast,
        "proof_state_expansions": counters.expansions,
        "operator_candidates_considered": counters.candidates,
        "duplicate_states_avoided": counters.duplicate_states,
        "events": events,
        "llm_calls": 0,
        "llm_tokens": 0,
        "foundation_model_calls": 0,
    }


def main() -> int:
    request = json.load(sys.stdin)
    result = solve(request)
    json.dump(result, sys.stdout, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
