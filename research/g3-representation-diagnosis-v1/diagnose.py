"""G3.4 diagnosis from legal pre-outcome features only.

Independent recovery (scorer) may inspect hidden polynomials. The classifier
may not. Timeout / hard-wall never yields JUMP.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import product
from fractions import Fraction
from typing import Any

from ocm.learning import methods as M


class Diagnosis(str, Enum):
    SEARCH_MORE = "SEARCH_MORE"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    LOCAL_REPAIR = "LOCAL_REPAIR"
    MISSING_OPERATOR = "MISSING_OPERATOR"
    REPRESENTATION_INSUFFICIENT = "REPRESENTATION_INSUFFICIENT"
    OBSERVATION_CHANNEL_INSUFFICIENT = "OBSERVATION_CHANNEL_INSUFFICIENT"
    RESOURCE_BOUND = "RESOURCE_BOUND"
    CANNOT_CHECK = "CANNOT_CHECK"
    JUMP = "JUMP"


@dataclass(frozen=True)
class Features:
    checker_identity: bool
    grammar_exhausted: bool
    remaining_legal_work: bool
    neighborhood_hit: bool
    extra_budget_finds: bool
    extra_operator_finds: bool
    extra_same_channel_splits: bool
    observation_collision: bool
    legal_full_coefficients: bool
    hard_wall: bool


def classify(feat: Features) -> Diagnosis:
    if not feat.checker_identity:
        return Diagnosis.CANNOT_CHECK
    if feat.observation_collision and not feat.legal_full_coefficients:
        return Diagnosis.OBSERVATION_CHANNEL_INSUFFICIENT
    if feat.observation_collision and feat.legal_full_coefficients and feat.extra_same_channel_splits:
        return Diagnosis.MISSING_EVIDENCE
    if feat.observation_collision and feat.legal_full_coefficients and not feat.extra_same_channel_splits:
        return Diagnosis.REPRESENTATION_INSUFFICIENT
    if feat.neighborhood_hit:
        return Diagnosis.LOCAL_REPAIR
    if feat.grammar_exhausted and feat.extra_operator_finds:
        return Diagnosis.MISSING_OPERATOR
    if feat.hard_wall and feat.remaining_legal_work:
        return Diagnosis.RESOURCE_BOUND
    if feat.extra_budget_finds:
        return Diagnosis.SEARCH_MORE
    return Diagnosis.CANNOT_CHECK


def compact_key(coefficients, kind: str) -> tuple:
    coef = tuple(coefficients)
    while len(coef) > 1 and coef[-1] == 0:
        coef = coef[:-1]
    if kind == "degree_leading":
        return (len(coef) - 1, coef[-1] if coef else 0)
    if kind == "eval":
        raise ValueError("eval keys are built from points")
    return coef


def eval_key(coefficients, points: tuple[int, ...]) -> tuple:
    return tuple(M.evaluate_polynomial(coefficients, x) for x in points)


def _iter_grammar(primitives, max_len):
    for length in range(max_len + 1):
        yield from product(primitives, repeat=length)


def _solve(primitives, max_len, target, budget: int):
    checked = 0
    n = sum(len(primitives) ** k for k in range(max_len + 1))
    for program in _iter_grammar(primitives, max_len):
        if checked >= budget:
            return None, checked, False, n
        checked += 1
        if M.normal_form(program) == target:
            return program, checked, checked >= n, n
    return None, checked, True, n


def neighborhood(program, primitives):
    program = list(program)
    for i, op in enumerate(program):
        for alt in primitives:
            if alt != op:
                yield tuple(program[:i] + [alt] + program[i + 1:])
    for alt in primitives:
        yield tuple(program) + (alt,)
        if program:
            yield tuple(program[:-1])


def features_for(case: dict[str, Any]) -> Features:
    primitives = tuple(case["primitives"])
    max_len = int(case["max_len"])
    budget = int(case["budget"])
    target = tuple(Fraction(str(x)) for x in case["target"])
    found, checked, exhausted, n_legal = _solve(primitives, max_len, target, budget)
    extra_budget_finds = False
    if found is None:
        found2, _, _, _ = _solve(primitives, max_len, target, int(case["raised_budget"]))
        extra_budget_finds = found2 is not None
    extra_operator_finds = False
    extra_ops = tuple(case.get("extra_primitives") or ())
    if extra_ops and found is None:
        f3, _, _, _ = _solve(primitives + extra_ops, max_len, target, int(case["raised_budget"]))
        extra_operator_finds = f3 is not None
    seed = tuple(case.get("seed_program") or ())
    neighborhood_hit = False
    if seed:
        neighborhood_hit = any(M.normal_form(cand) == target for cand in neighborhood(seed, primitives))
    collision = False
    extra_same = False
    collider = case.get("collider_program")
    channel = case.get("channel", "eval")
    points = tuple(case.get("obs_points") or (0,))
    extra_points = tuple(case.get("extra_points") or (1, 2, 3))
    if collider:
        other = M.normal_form(tuple(collider))
        if channel == "eval":
            collision = eval_key(other, points) == eval_key(target, points) and other != target
            extra_same = eval_key(other, extra_points) != eval_key(target, extra_points)
        elif channel == "degree_leading":
            collision = compact_key(other, "degree_leading") == compact_key(target, "degree_leading") and other != target
            extra_same = False  # same compact channel has no further coordinate
        elif channel == "empty":
            collision = True
            extra_same = False
    remaining = found is None and checked < n_legal
    return Features(
        checker_identity=bool(case.get("checker_identity", True)),
        grammar_exhausted=bool(exhausted and found is None),
        remaining_legal_work=remaining,
        neighborhood_hit=neighborhood_hit,
        extra_budget_finds=extra_budget_finds,
        extra_operator_finds=extra_operator_finds,
        extra_same_channel_splits=extra_same,
        observation_collision=collision,
        legal_full_coefficients=bool(case.get("legal_full_coefficients", True)),
        hard_wall=bool(case.get("hard_wall", False)),
    )


def frozen_cases() -> list[dict[str, Any]]:
    nf = lambda prog: [str(c) for c in M.normal_form(prog)]
    return [
        {
            "id": "search-more",
            "primitives": ("inc", "dec"),
            "max_len": 2,
            "budget": 1,
            "raised_budget": 16,
            "target": nf(("inc", "inc")),
            "truth_reserved": "SEARCH_MORE",
        },
        {
            "id": "missing-evidence",
            "primitives": ("inc", "dec", "double", "square"),
            "max_len": 1,
            "budget": 16,
            "raised_budget": 16,
            "target": nf(("double",)),
            "collider_program": ("square",),
            "channel": "eval",
            "obs_points": (0,),
            "extra_points": (1, 2),
            "truth_reserved": "MISSING_EVIDENCE",
        },
        {
            "id": "local-repair",
            "primitives": ("inc", "dec", "double"),
            "max_len": 2,
            "budget": 2,
            "raised_budget": 2,
            "target": nf(("double",)),
            "seed_program": ("inc",),
            "truth_reserved": "LOCAL_REPAIR",
        },
        {
            "id": "missing-operator",
            "primitives": ("inc", "dec"),
            "extra_primitives": ("square",),
            "max_len": 1,
            "budget": 16,
            "raised_budget": 16,
            "target": nf(("square",)),
            "truth_reserved": "MISSING_OPERATOR",
        },
        {
            "id": "representation-insufficient",
            "primitives": ("inc", "dec", "double", "square"),
            "max_len": 2,
            "budget": 64,
            "raised_budget": 64,
            "target": nf(("double",)),
            "collider_program": ("inc", "double"),
            "channel": "degree_leading",
            "truth_reserved": "REPRESENTATION_INSUFFICIENT",
        },
        {
            "id": "observation-channel",
            "primitives": ("inc", "dec", "double"),
            "max_len": 1,
            "budget": 16,
            "raised_budget": 16,
            "target": nf(("double",)),
            "collider_program": ("inc",),
            "channel": "empty",
            "legal_full_coefficients": False,
            "truth_reserved": "OBSERVATION_CHANNEL_INSUFFICIENT",
        },
        {
            "id": "resource-bound",
            "primitives": ("inc", "dec", "double", "square"),
            "max_len": 3,
            "budget": 2,
            "raised_budget": 2,
            "target": nf(("inc", "inc", "inc")),
            "hard_wall": True,
            "truth_reserved": "RESOURCE_BOUND",
        },
        {
            "id": "cannot-check",
            "primitives": ("inc",),
            "max_len": 1,
            "budget": 4,
            "raised_budget": 4,
            "target": ["0", "1"],
            "checker_identity": False,
            "truth_reserved": "CANNOT_CHECK",
        },
        {
            "id": "timeout-only",
            "primitives": ("inc", "dec", "double", "square"),
            "max_len": 3,
            "budget": 2,
            "raised_budget": 2,
            "target": nf(("square", "inc")),
            "hard_wall": True,
            "truth_reserved": "RESOURCE_BOUND",
        },
    ]


def parent_search_more(_feat: Features) -> Diagnosis:
    return Diagnosis.SEARCH_MORE


def parent_always_representation(_feat: Features) -> Diagnosis:
    return Diagnosis.REPRESENTATION_INSUFFICIENT


def parent_timeout_jump(feat: Features) -> Diagnosis:
    if feat.hard_wall:
        return Diagnosis.JUMP
    return classify(feat)
