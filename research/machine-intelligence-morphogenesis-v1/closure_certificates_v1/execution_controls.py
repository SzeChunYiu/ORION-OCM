"""Same-author DEVELOPMENT calibration: enumerate and execute arithmetic programs.

No family/shape/capability label participates in execution or scoring.
This small finite grammar is a parent-owned synthesis control, not K4 recovery.
It is intentionally NOT a substitute for the repository's 22-family generator.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Iterable

LEAVES = ("x", "-1", "0", "1")
OPS = ("+", "*")

@dataclass(frozen=True)
class Expr:
    op: str
    args: tuple["Expr", ...] = ()
    def __post_init__(self):
        if type(self.op) is not str or type(self.args) is not tuple or any(type(a) is not Expr for a in self.args):
            raise TypeError("immutable Expr children and a string opcode required")
        if self.op not in LEAVES + OPS:
            raise ValueError("operation outside frozen grammar")
        if len(self.args) != (2 if self.op in OPS else 0):
            raise ValueError("invalid operation arity")
    def tokens(self) -> tuple[str, ...]:
        return tuple(t for a in self.args for t in a.tokens()) + (self.op,)


def enumerate_programs(max_binary_ops: int = 2) -> tuple[Expr, ...]:
    if type(max_binary_ops) is not int or not 0 <= max_binary_ops <= 3:
        raise ValueError("development enumeration cap must be between zero and three")
    levels = [tuple(Expr(v) for v in LEAVES)]
    for n in range(1, max_binary_ops + 1):
        row = []
        for left_n in range(n):
            for a, b, op in product(levels[left_n], levels[n-1-left_n], OPS):
                row.append(Expr(op, (a, b)))
        levels.append(tuple(row))
    return tuple(e for level in levels for e in level)


def execute(program: Expr, x: int) -> dict:
    if type(x) is not int:
        raise TypeError("this exact microscope uses integer inputs only")
    stack: list[int] = []
    trace = []
    peak = 0
    for token in program.tokens():
        if token in OPS:
            b, a = stack.pop(), stack.pop()
            stack.append(a + b if token == "+" else a * b)
        else:
            stack.append(x if token == "x" else int(token))
        trace.append({"token": token, "stack_words": len(stack)})
        peak = max(peak, len(stack))
    assert len(stack) == 1
    return {"output": stack[0], "executed_steps": len(trace), "trace": trace,
            "temporary_peak_words": peak, "retained_parameter_words": 0,
            "description_tokens": len(program.tokens())}


def certificate(program: Expr) -> dict:
    # In a straight-line postfix language every token executes exactly once.
    # This is a structural statement, not an exponent fit on a finite size sweep.
    height = peak = 0
    for token in program.tokens():
        height += -1 if token in OPS else 1
        peak = max(peak, height)
    return {"executed_steps": len(program.tokens()), "temporary_peak_words": peak,
            "retained_parameter_words": 0, "description_tokens": len(program.tokens()),
            "cost_model": "ONE_PER_POSTFIX_TOKEN__INTEGER_BIT_COMPLEXITY_EXCLUDED",
            "scope": "EXACT_STRAIGHT_LINE_CONTROL_ONLY"}


def search(examples: Iterable[tuple[int, int]], *, max_binary_ops: int = 2,
           budget: int | None = None) -> dict:
    data = tuple(examples)
    if not data or any(type(x) is not int or type(y) is not int for x, y in data):
        raise ValueError("nonempty integer examples required")
    space = enumerate_programs(max_binary_ops)
    if budget is None:
        budget = len(space)
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be nonnegative integer")
    admissible = []
    execution_work = 0
    for candidate in space[:budget]:
        rows = [execute(candidate, x) for x, _ in data]
        execution_work += sum(r["executed_steps"] for r in rows)
        if all(r["output"] == y for r, (_, y) in zip(rows, data)):
            admissible.append(candidate)
    winner = min(admissible, key=lambda p: (len(p.tokens()), p.tokens())) if admissible else None
    return {"status": "FINITE_CONTROL_WITNESS" if winner else "NO_CONTROL_WITNESS",
            "exhaustive": budget >= len(space), "space_size": len(space),
            "examined": min(budget, len(space)), "candidate_execution_work": execution_work,
            "winner_tokens": None if winner is None else winner.tokens(),
            "winner_certificate": None if winner is None else certificate(winner),
            "claim_ceiling": "SAME_AUTHOR_DEVELOPMENT_CONTROL_NOT_PROTECTED_K4",
            "meter_exclusions": ["host interpreter overhead", "enumeration construction work",
                                 "integer bit complexity", "physical energy", "external review"]}


def certify_finite_frontier(examples: Iterable[tuple[int, int]], *,
                            target_uses_multiplication: bool,
                            max_binary_ops: int = 2) -> dict:
    """Exact class comparison ONLY in this complete, declared finite language.

    Every candidate is executed on every registered example. The objective is
    description tokens plus total serving token steps on those examples; search
    work is reported separately. This is not a bit/energy/full-lifecycle bound.
    Target membership is inspected only after generation, execution and ranking.
    There is no caller-supplied completeness flag or class lower bound.
    """
    import hashlib
    import json
    data = tuple(examples)
    if type(target_uses_multiplication) is not bool:
        raise ValueError("target_uses_multiplication must be boolean")
    if not data or any(type(x) is not int or type(y) is not int for x, y in data):
        raise ValueError("nonempty integer examples required")
    space = enumerate_programs(max_binary_ops)
    evaluated = []
    search_work = 0
    for program in space:
        rows = [execute(program, x) for x, _ in data]
        search_work += sum(row["executed_steps"] for row in rows)
        if all(row["output"] == y for row, (_, y) in zip(rows, data)):
            cost = len(program.tokens()) + sum(row["executed_steps"] for row in rows)
            evaluated.append((cost, program.tokens()))
    evaluated.sort()
    body = {"grammar": [LEAVES, OPS, max_binary_ops], "examples": data,
            "ordered_programs": [p.tokens() for p in space], "admissible": evaluated}
    digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    # Only now is the declared target morphology consulted.
    targets = [row for row in evaluated if ("*" in row[1]) == target_uses_multiplication]
    rivals = [row for row in evaluated if ("*" in row[1]) != target_uses_multiplication]
    lower = min((row[0] for row in targets), default=None)
    rival = min((row[0] for row in rivals), default=None)
    status = ("FINITE_TARGET_CLASS_EMPTY" if lower is None else
              "FINITE_RIVAL_STRICTLY_BEATS_CLASS" if rival is not None and rival < lower else
              "FINITE_TARGET_CLASS_OPTIMAL_OR_TIED")
    return {"schema": "GMIExecutedFiniteClassFrontierV1", "status": status,
            "domain_and_evaluation_sha256": digest, "target_uses_multiplication": target_uses_multiplication,
            "exhaustive_by_construction": True, "domain_size": len(space),
            "admissible_target_count": len(targets), "admissible_rival_count": len(rivals),
            "exact_target_minimum": lower, "exact_rival_minimum": rival,
            "global_winner_tokens": None if not evaluated else evaluated[0][1],
            "candidate_execution_work": search_work,
            "objective": "DESCRIPTION_TOKENS_PLUS_REGISTERED_SERVING_TOKEN_STEPS",
            "claim_ceiling": "EXACT_FINITE_LANGUAGE_AND_EXAMPLES_ONLY_NOT_K4_OR_FULL_GMI"}
