from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json
from itertools import product
from typing import Any, Callable, Iterable, Sequence, Tuple

F = Fraction

FREEZE_COMMIT = "417db4581fb66903eeba5c6bfb6e60a02719716d"
CLAIM_CEILING = "SOUND_FINITE_UNCERTAINTY_COMPOSITION_FOR_REGISTERED_RELATIONS"

IDENTIFIED_TRUE = "IDENTIFIED_TRUE"
IDENTIFIED_FALSE = "IDENTIFIED_FALSE"
CANNOT_IDENTIFY = "CANNOT_IDENTIFY"
INCONSISTENT_EMPTY_IMAGE = "INCONSISTENT_EMPTY_IMAGE"
MISSING_RELATION_FULL_DOMAIN = "MISSING_RELATION_FULL_DOMAIN"


def _fraction(value: Any, name: str) -> F:
    if type(value) is not F:
        raise ValueError(f"{name} must be an exact Fraction")
    return value


def _probability(value: Any, name: str) -> F:
    value = _fraction(value, name)
    if not F(0) <= value <= F(1):
        raise ValueError(f"{name} must lie in [0,1]")
    return value


def _canonical_key(value: Any) -> tuple[int, Any]:
    if isinstance(value, bool):
        return (0, int(value))
    if isinstance(value, int):
        return (1, value)
    if type(value) is F:
        return (2, value)
    if isinstance(value, str):
        return (3, value)
    return (99, repr(value))


def canonical_values(values: Iterable[Any]) -> Tuple[Any, ...]:
    return tuple(sorted(set(values), key=_canonical_key))


def _domain(values: Sequence[Any], name: str) -> Tuple[Any, ...]:
    if not isinstance(values, tuple) or not values:
        raise ValueError(f"{name} must be a nonempty tuple")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} contains duplicates")
    return canonical_values(values)


def _subset(values: Sequence[Any], domain: Sequence[Any], name: str) -> Tuple[Any, ...]:
    if not isinstance(values, tuple):
        raise ValueError(f"{name} must be a tuple")
    d = set(_domain(tuple(domain), f"{name} domain"))
    if len(set(values)) != len(values):
        raise ValueError(f"{name} contains duplicates")
    if not set(values).issubset(d):
        raise ValueError(f"{name} contains a value outside its domain")
    return canonical_values(values)


def _relation(
    source_domain: Sequence[Any],
    target_domain: Sequence[Any],
    relation: Sequence[tuple[Any, Any]],
    name: str = "relation",
) -> Tuple[tuple[Any, Any], ...]:
    src = set(_domain(tuple(source_domain), f"{name} source domain"))
    dst = set(_domain(tuple(target_domain), f"{name} target domain"))
    if not isinstance(relation, tuple):
        raise ValueError(f"{name} must be a tuple")
    seen = set()
    out = []
    for pair in relation:
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError(f"{name} entries must be pairs")
        x, y = pair
        if x not in src or y not in dst:
            raise ValueError(f"{name} endpoint lies outside its registered domain")
        if pair in seen:
            raise ValueError(f"{name} contains duplicate pairs")
        seen.add(pair)
        out.append(pair)
    return tuple(sorted(out, key=lambda p: (_canonical_key(p[0]), _canonical_key(p[1]))))


def relational_image(
    source_domain: Sequence[Any],
    target_domain: Sequence[Any],
    relation: Sequence[tuple[Any, Any]],
    source_set: Sequence[Any],
) -> Tuple[Any, ...]:
    src = _domain(tuple(source_domain), "source domain")
    dst = _domain(tuple(target_domain), "target domain")
    rel = _relation(src, dst, tuple(relation))
    s = set(_subset(tuple(source_set), src, "source set"))
    return canonical_values(y for x, y in rel if x in s)


def compose_relations(
    domain_x: Sequence[Any],
    domain_y: Sequence[Any],
    domain_z: Sequence[Any],
    relation_xy: Sequence[tuple[Any, Any]],
    relation_yz: Sequence[tuple[Any, Any]],
) -> Tuple[tuple[Any, Any], ...]:
    x = _domain(tuple(domain_x), "domain X")
    y = _domain(tuple(domain_y), "domain Y")
    z = _domain(tuple(domain_z), "domain Z")
    r = _relation(x, y, tuple(relation_xy), "R")
    q = _relation(y, z, tuple(relation_yz), "Q")
    pairs = {
        (a, c)
        for a, b1 in r
        for b2, c in q
        if b1 == b2
    }
    return tuple(sorted(pairs, key=lambda p: (_canonical_key(p[0]), _canonical_key(p[1]))))


def complete_relation(
    source_domain: Sequence[Any], target_domain: Sequence[Any]
) -> Tuple[tuple[Any, Any], ...]:
    src = _domain(tuple(source_domain), "source domain")
    dst = _domain(tuple(target_domain), "target domain")
    return tuple((x, y) for x in src for y in dst)


def coverage_lower_bound(alpha: F, betas: Sequence[F]) -> F:
    alpha = _probability(alpha, "alpha")
    if not isinstance(betas, tuple):
        raise ValueError("betas must be a tuple")
    total = alpha
    for index, beta in enumerate(betas):
        total += _probability(beta, f"beta[{index}]")
    return max(F(0), F(1) - total)


def identify_boolean_query(
    target_set: Sequence[Any], query: Callable[[Any], bool]
) -> str:
    if not isinstance(target_set, tuple):
        raise ValueError("target_set must be a tuple")
    if not callable(query):
        raise ValueError("query must be callable")
    if not target_set:
        return INCONSISTENT_EMPTY_IMAGE
    values = {bool(query(x)) for x in target_set}
    if values == {True}:
        return IDENTIFIED_TRUE
    if values == {False}:
        return IDENTIFIED_FALSE
    return CANNOT_IDENTIFY


@dataclass(frozen=True)
class Stage:
    name: str
    source_domain: Tuple[Any, ...]
    target_domain: Tuple[Any, ...]
    relation: Tuple[tuple[Any, Any], ...] | None
    beta: F

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("stage name must be a nonempty string")
        src = _domain(self.source_domain, f"{self.name} source domain")
        dst = _domain(self.target_domain, f"{self.name} target domain")
        _probability(self.beta, f"{self.name} beta")
        if self.relation is None:
            if self.beta != 0:
                raise ValueError("missing relation cannot claim a relation-failure budget")
        else:
            _relation(src, dst, self.relation, self.name)


@dataclass(frozen=True)
class Propagation:
    target_set: Tuple[Any, ...]
    markers: Tuple[str, ...]
    lower_coverage: F


class CompositionCampaign:
    def __init__(self, source_domain: Tuple[Any, ...], alpha: F):
        self._source_domain = _domain(source_domain, "campaign source domain")
        self._alpha = _probability(alpha, "alpha")
        self._stages: list[Stage] = []
        self._active = False

    @property
    def stages(self) -> Tuple[Stage, ...]:
        return tuple(self._stages)

    def register(self, stage: Stage) -> None:
        if self._active:
            raise RuntimeError("campaign is frozen after activation")
        if not isinstance(stage, Stage):
            raise ValueError("stage must be Stage")
        expected_source = self._source_domain if not self._stages else self._stages[-1].target_domain
        if canonical_values(stage.source_domain) != canonical_values(expected_source):
            raise ValueError("stage source domain is incompatible with the registered chain")
        self._stages.append(stage)

    def activate(self) -> None:
        self._active = True

    def propagate(self, source_set: Tuple[Any, ...]) -> Propagation:
        if not self._active:
            raise RuntimeError("campaign must be activated before propagation")
        current_domain = self._source_domain
        current = _subset(source_set, current_domain, "source set")
        markers: list[str] = []
        betas: list[F] = []
        for stage in self._stages:
            if canonical_values(stage.source_domain) != canonical_values(current_domain):
                raise ValueError("registered stage chain is inconsistent")
            if stage.relation is None:
                relation = complete_relation(stage.source_domain, stage.target_domain)
                markers.append(MISSING_RELATION_FULL_DOMAIN)
            else:
                relation = stage.relation
                betas.append(stage.beta)
            current = relational_image(
                stage.source_domain, stage.target_domain, relation, current
            )
            current_domain = stage.target_domain
        return Propagation(
            target_set=canonical_values(current),
            markers=tuple(markers),
            lower_coverage=coverage_lower_bound(self._alpha, tuple(betas)),
        )


def _powerset(values: Tuple[Any, ...]) -> Tuple[Tuple[Any, ...], ...]:
    values = canonical_values(values)
    return tuple(
        tuple(values[i] for i, include in enumerate(mask) if include)
        for mask in product((False, True), repeat=len(values))
    )


def _all_relations(
    source_domain: Tuple[Any, ...], target_domain: Tuple[Any, ...]
) -> Tuple[Tuple[tuple[Any, Any], ...], ...]:
    pairs = tuple((x, y) for x in source_domain for y in target_domain)
    return tuple(
        tuple(pairs[i] for i, include in enumerate(mask) if include)
        for mask in product((False, True), repeat=len(pairs))
    )


def exhaustive_uc1_certificate() -> dict[str, Any]:
    x = (0, 1)
    y = (0, 1)
    z = (0, 1)
    failures = 0
    cases = 0
    for s in _powerset(x):
        for r in _all_relations(x, y):
            first = relational_image(x, y, r, s)
            for q in _all_relations(y, z):
                sequential = relational_image(y, z, q, first)
                composed = compose_relations(x, y, z, r, q)
                direct = relational_image(x, z, composed, s)
                cases += 1
                if sequential != direct:
                    failures += 1
    return {
        "domain_cardinalities": [2, 2, 2],
        "cases": cases,
        "failures": failures,
        "all_hold": failures == 0,
    }


def _frac(value: F) -> str:
    if type(value) is not F:
        raise ValueError("_frac requires Fraction")
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _json_atom(value: Any) -> dict[str, Any]:
    if isinstance(value, bool):
        return {"type": "bool", "value": value}
    if isinstance(value, int):
        return {"type": "int", "value": value}
    if isinstance(value, str):
        return {"type": "str", "value": value}
    if type(value) is F:
        return {"type": "fraction", "value": _frac(value)}
    raise ValueError(f"unsupported receipt atom type: {type(value).__name__}")


def _json_set(values: Sequence[Any]) -> list[dict[str, Any]]:
    return [_json_atom(v) for v in canonical_values(values)]


def hostile_dependence_receipt() -> dict[str, Any]:
    omega = ("a", "b", "c", "d")
    f1 = {"a"}
    f2 = {"b"}
    good1 = set(omega) - f1
    good2 = set(omega) - f2
    true_joint = F(len(good1 & good2), len(omega))
    product_good = F(len(good1), len(omega)) * F(len(good2), len(omega))
    union_lower = F(1) - F(len(f1), len(omega)) - F(len(f2), len(omega))

    overlap_f1 = {"a"}
    overlap_f2 = {"a"}
    overlap_good = (set(omega) - overlap_f1) & (set(omega) - overlap_f2)
    overlap_true_joint = F(len(overlap_good), len(omega))
    overlap_union_lower = F(1) - F(1, 4) - F(1, 4)

    return {
        "disjoint_failures": {
            "failure_1": "1/4",
            "failure_2": "1/4",
            "marginal_good_1": "3/4",
            "marginal_good_2": "3/4",
            "true_joint_good": _frac(true_joint),
            "independence_product": _frac(product_good),
            "union_bound_lower": _frac(union_lower),
            "product_is_unsound_lower_bound": product_good > true_joint,
            "union_bound_is_attained": union_lower == true_joint,
        },
        "overlapping_failures": {
            "failure_1": "1/4",
            "failure_2": "1/4",
            "true_joint_good": _frac(overlap_true_joint),
            "union_bound_lower": _frac(overlap_union_lower),
            "union_bound_is_conservative": overlap_true_joint > overlap_union_lower,
        },
    }


def frozen_chain() -> tuple[
    Tuple[int, ...],
    Tuple[str, ...],
    Tuple[int, ...],
    Tuple[int, ...],
    Tuple[tuple[int, str], ...],
    Tuple[tuple[str, int], ...],
]:
    x0 = (0, 1, 2)
    x1 = ("a", "b")
    x2 = (10, 20, 30, 40)
    s0 = (0, 2)
    r0 = ((0, "a"), (1, "a"), (2, "b"))
    r1 = (("a", 10), ("a", 20), ("b", 30), ("b", 40))
    return x0, x1, x2, s0, r0, r1


def build_receipt() -> dict[str, Any]:
    x0, x1, x2, s0, r0, r1 = frozen_chain()
    s1 = relational_image(x0, x1, r0, s0)
    s2 = relational_image(x1, x2, r1, s1)
    composed = compose_relations(x0, x1, x2, r0, r1)
    direct = relational_image(x0, x2, composed, s0)

    alpha = F(1, 20)
    betas = (F(1, 100), F(1, 200))
    lower = coverage_lower_bound(alpha, betas)

    q_even = identify_boolean_query(s2, lambda x: x % 2 == 0)
    q_gt_25 = identify_boolean_query(s2, lambda x: x > 25)
    q_le_40 = identify_boolean_query(s2, lambda x: x <= 40)

    missing = CompositionCampaign(x0, alpha)
    missing.register(Stage("missing", x0, x2, None, F(0)))
    missing.activate()
    missing_result = missing.propagate(s0)

    receipt = {
        "schema": "FiniteUncertaintyCompositionReceiptV1",
        "issue": 757,
        "parent_issue": 602,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "proof_classes": {
            "UC-1": ["P1", "P2"],
            "UC-2": ["P1", "P2"],
            "UC-3": ["P1", "P2"],
            "UC-4": ["P1", "P2"],
            "UC-H1": ["P2"],
        },
        "exhaustive_uc1": exhaustive_uc1_certificate(),
        "concrete_chain": {
            "source_set": _json_set(s0),
            "stage_1_image": _json_set(s1),
            "stage_2_image": _json_set(s2),
            "direct_composed_image": _json_set(direct),
            "sequential_equals_direct": s2 == direct,
            "alpha": _frac(alpha),
            "betas": [_frac(b) for b in betas],
            "coverage_lower_bound": _frac(lower),
            "query_outcomes": {
                "q_even": q_even,
                "q_gt_25": q_gt_25,
                "q_le_40": q_le_40,
            },
        },
        "missing_relation": {
            "target_set": _json_set(missing_result.target_set),
            "markers": list(missing_result.markers),
            "coverage_lower_bound": _frac(missing_result.lower_coverage),
            "query_outcomes": {
                "q_even": identify_boolean_query(missing_result.target_set, lambda x: x % 2 == 0),
                "q_gt_25": identify_boolean_query(missing_result.target_set, lambda x: x > 25),
                "q_le_40": identify_boolean_query(missing_result.target_set, lambda x: x <= 40),
            },
        },
        "dependence_hostiles": hostile_dependence_receipt(),
        "empty_image_query_terminal": identify_boolean_query((), lambda _: True),
        "forbidden_claims": [
            "INDEPENDENT_STAGE_ERRORS",
            "UNIVERSAL_UNCERTAINTY_CALIBRATION",
            "REAL_WORLD_COVERAGE_PROVED",
            "G6",
            "G7",
            "COMPLETE_GMI",
        ],
    }
    return receipt


def canonical_receipt_bytes() -> bytes:
    return (json.dumps(build_receipt(), indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    print(canonical_receipt_bytes().decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
