#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from itertools import combinations, product
import json
from typing import Any, Iterable, Mapping

F = Fraction

CLAIM_CEILING = "GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE"
FREEZE_COMMIT = "b62fd81b5e3b37a4f94f70aaaa54d4b76e36008a"
SOURCE_MAIN = "5db372ef7003253d5846b324ed80a2454613983c"
FORBIDDEN_PROMOTIONS = (
    "UNIVERSAL_UNCERTAINTY_CALIBRATION",
    "INDEPENDENCE_PROVED",
    "ALL_REAL_WORLD_CONFIDENCE_VALID",
    "UNIVERSAL_POSTERIOR_CORRECTNESS",
    "REAL_SCALE_UNCERTAINTY_VALIDATION",
    "COMPLETE_GMI",
)


class UncertaintyKind(str, Enum):
    FEASIBLE_SET = "FEASIBLE_SET"
    CONFIDENCE_SET = "CONFIDENCE_SET"
    PREDICTIVE_LAW = "PREDICTIVE_LAW"
    LATENT_PREDICTIVE_MODEL = "LATENT_PREDICTIVE_MODEL"
    SELECTIVE_PREDICTION = "SELECTIVE_PREDICTION"


class SetKnowledge(str, Enum):
    FEASIBLE = "FEASIBLE"
    UNKNOWN = "UNKNOWN"
    INCONSISTENT_REGISTERED_ASSUMPTIONS = "INCONSISTENT_REGISTERED_ASSUMPTIONS"


class QueryDisposition(str, Enum):
    IDENTIFIED = "IDENTIFIED"
    CANNOT_IDENTIFY = "CANNOT_IDENTIFY"
    CANNOT_CHECK = "CANNOT_CHECK"
    INCONSISTENT_REGISTERED_ASSUMPTIONS = "INCONSISTENT_REGISTERED_ASSUMPTIONS"


class CannotCheckError(ValueError):
    pass


def _fraction(value: Any, name: str) -> F:
    if type(value) is not F:
        raise ValueError(f"{name} must be an exact Fraction")
    return value


def _budget(value: Any, name: str) -> F:
    value = _fraction(value, name)
    if not F(0) <= value <= F(1):
        raise ValueError(f"{name} must lie in [0,1]")
    return value


def _domain(values: Any, name: str) -> tuple[Any, ...]:
    if not isinstance(values, tuple) or not values:
        raise ValueError(f"{name} must be a nonempty tuple")
    try:
        if len(set(values)) != len(values):
            raise ValueError(f"{name} must contain unique hashable values")
    except TypeError as exc:
        raise ValueError(f"{name} values must be hashable") from exc
    return values


def _subset(values: Any, domain: tuple[Any, ...], name: str) -> tuple[Any, ...]:
    if not isinstance(values, tuple):
        raise ValueError(f"{name} must be a tuple")
    try:
        if len(set(values)) != len(values):
            raise ValueError(f"{name} must contain unique values")
        if not set(values).issubset(set(domain)):
            raise ValueError(f"{name} must be a subset of the registered domain")
    except TypeError as exc:
        raise ValueError(f"{name} values must be hashable") from exc
    return tuple(sorted(values, key=repr))


def _provenance(values: Any) -> tuple[str, ...]:
    if not isinstance(values, tuple) or not values:
        raise ValueError("provenance must be a nonempty tuple")
    if any(not isinstance(x, str) or not x.strip() for x in values):
        raise ValueError("provenance entries must be nonempty strings")
    return values


def _version(value: Any) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("version must be a nonnegative integer")
    return value


def _probability_vector(values: Any, size: int, name: str) -> tuple[F, ...]:
    if not isinstance(values, tuple) or len(values) != size:
        raise ValueError(f"{name} must align exactly with its domain")
    out = tuple(_fraction(x, name) for x in values)
    if any(x < 0 for x in out) or sum(out, F(0)) != 1:
        raise ValueError(f"{name} must be nonnegative exact probabilities summing to 1")
    return out


def frac(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


@dataclass(frozen=True)
class FeasibleSet:
    domain: tuple[Any, ...]
    values: tuple[Any, ...]
    version: int
    provenance: tuple[str, ...]
    kind: UncertaintyKind = UncertaintyKind.FEASIBLE_SET

    def __post_init__(self) -> None:
        domain = _domain(self.domain, "domain")
        values = _subset(self.values, domain, "values")
        _version(self.version)
        _provenance(self.provenance)
        object.__setattr__(self, "values", values)

    @property
    def knowledge(self) -> SetKnowledge:
        if not self.values:
            return SetKnowledge.INCONSISTENT_REGISTERED_ASSUMPTIONS
        if set(self.values) == set(self.domain):
            return SetKnowledge.UNKNOWN
        return SetKnowledge.FEASIBLE


@dataclass(frozen=True)
class ConfidenceSet:
    domain: tuple[Any, ...]
    values: tuple[Any, ...]
    alpha: F
    target: str
    version: int
    provenance: tuple[str, ...]
    raw_evidence_count: int = 0
    kind: UncertaintyKind = UncertaintyKind.CONFIDENCE_SET

    def __post_init__(self) -> None:
        domain = _domain(self.domain, "domain")
        values = _subset(self.values, domain, "values")
        _budget(self.alpha, "alpha")
        if not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("target must be a nonempty string")
        _version(self.version)
        _provenance(self.provenance)
        if type(self.raw_evidence_count) is not int or self.raw_evidence_count < 0:
            raise ValueError("raw_evidence_count must be a nonnegative integer")
        object.__setattr__(self, "values", values)

    @property
    def coverage_lower_bound(self) -> F:
        return 1 - self.alpha

    @property
    def knowledge(self) -> SetKnowledge:
        if not self.values:
            return SetKnowledge.INCONSISTENT_REGISTERED_ASSUMPTIONS
        if set(self.values) == set(self.domain):
            return SetKnowledge.UNKNOWN
        return SetKnowledge.FEASIBLE


@dataclass(frozen=True)
class PredictiveLaw:
    outcome_domain: tuple[Any, ...]
    probabilities: tuple[F, ...]
    version: int
    provenance: tuple[str, ...]
    kind: UncertaintyKind = UncertaintyKind.PREDICTIVE_LAW

    def __post_init__(self) -> None:
        domain = _domain(self.outcome_domain, "outcome_domain")
        _probability_vector(self.probabilities, len(domain), "probabilities")
        _version(self.version)
        _provenance(self.provenance)

    def epistemic_aleatoric_decomposition(self) -> None:
        raise CannotCheckError("CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS")


@dataclass(frozen=True)
class LatentPredictiveModel:
    latent_domain: tuple[Any, ...]
    latent_prior: tuple[F, ...]
    outcome_domain: tuple[F, ...]
    kernels: tuple[tuple[F, ...], ...]
    version: int
    provenance: tuple[str, ...]
    kind: UncertaintyKind = UncertaintyKind.LATENT_PREDICTIVE_MODEL

    def __post_init__(self) -> None:
        latent = _domain(self.latent_domain, "latent_domain")
        outcomes = _domain(self.outcome_domain, "outcome_domain")
        for y in outcomes:
            _fraction(y, "outcome value")
        _probability_vector(self.latent_prior, len(latent), "latent_prior")
        if not isinstance(self.kernels, tuple) or len(self.kernels) != len(latent):
            raise ValueError("kernels must align exactly with latent_domain")
        for row in self.kernels:
            _probability_vector(row, len(outcomes), "kernel row")
        _version(self.version)
        _provenance(self.provenance)

    def predictive_law(self) -> PredictiveLaw:
        probs = []
        for j in range(len(self.outcome_domain)):
            probs.append(sum((self.latent_prior[i] * self.kernels[i][j] for i in range(len(self.latent_domain))), F(0)))
        return PredictiveLaw(self.outcome_domain, tuple(probs), self.version, self.provenance + ("marginalized",))

    def variance_decomposition(self) -> Mapping[str, F]:
        means: list[F] = []
        conditional_vars: list[F] = []
        for row in self.kernels:
            mean = sum((p * y for p, y in zip(row, self.outcome_domain)), F(0))
            second = sum((p * y * y for p, y in zip(row, self.outcome_domain)), F(0))
            means.append(mean)
            conditional_vars.append(second - mean * mean)
        mu = sum((p * m for p, m in zip(self.latent_prior, means)), F(0))
        aleatoric = sum((p * v for p, v in zip(self.latent_prior, conditional_vars)), F(0))
        epistemic_mean = sum((p * (m - mu) * (m - mu) for p, m in zip(self.latent_prior, means)), F(0))
        marginal = self.predictive_law()
        total_mean = sum((p * y for p, y in zip(marginal.probabilities, self.outcome_domain)), F(0))
        total_second = sum((p * y * y for p, y in zip(marginal.probabilities, self.outcome_domain)), F(0))
        total = total_second - total_mean * total_mean
        if total != aleatoric + epistemic_mean:
            raise ArithmeticError("law of total variance failed")
        return {"predictive_mean": mu, "aleatoric": aleatoric, "epistemic_mean": epistemic_mean, "total": total}


@dataclass(frozen=True)
class SelectivePrediction:
    value_set: tuple[Any, ...]
    risk_or_error_certificate: F
    coverage: F
    version: int
    provenance: tuple[str, ...]
    kind: UncertaintyKind = UncertaintyKind.SELECTIVE_PREDICTION

    def __post_init__(self) -> None:
        if not isinstance(self.value_set, tuple) or not self.value_set:
            raise ValueError("value_set must be a nonempty tuple")
        try:
            if len(set(self.value_set)) != len(self.value_set):
                raise ValueError("value_set must contain unique values")
        except TypeError as exc:
            raise ValueError("value_set values must be hashable") from exc
        _budget(self.risk_or_error_certificate, "risk_or_error_certificate")
        _budget(self.coverage, "coverage")
        _version(self.version)
        _provenance(self.provenance)


@dataclass(frozen=True)
class QueryResult:
    disposition: QueryDisposition
    candidates: tuple[Any, ...] = ()
    reason: str = ""
    failure_budget: F | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, QueryDisposition):
            raise ValueError("disposition must be a QueryDisposition")
        if not isinstance(self.candidates, tuple):
            raise ValueError("candidates must be a tuple")
        if not isinstance(self.reason, str):
            raise ValueError("reason must be a string")
        if self.failure_budget is not None:
            _budget(self.failure_budget, "failure_budget")

    @property
    def coverage_lower_bound(self) -> F | None:
        return None if self.failure_budget is None else 1 - self.failure_budget


@dataclass(frozen=True)
class CannotCheck:
    reason: str
    disposition: QueryDisposition = QueryDisposition.CANNOT_CHECK

    def __post_init__(self) -> None:
        if not isinstance(self.reason, str) or not self.reason:
            raise ValueError("CANNOT_CHECK reason must be a nonempty string")
        if self.disposition is not QueryDisposition.CANNOT_CHECK:
            raise ValueError("CannotCheck disposition is fixed")


def query_identified_set(obj: FeasibleSet | ConfidenceSet, query: Mapping[Any, Any] | None) -> QueryResult:
    if not isinstance(obj, (FeasibleSet, ConfidenceSet)):
        return QueryResult(QueryDisposition.CANNOT_CHECK, reason="QUERY_REQUIRES_SET_VALUED_STATE")
    if query is None:
        return QueryResult(QueryDisposition.CANNOT_CHECK, reason="QUERY_NOT_REGISTERED")
    if set(query) != set(obj.domain):
        return QueryResult(QueryDisposition.CANNOT_CHECK, reason="QUERY_DOMAIN_MISMATCH")
    if not obj.values:
        return QueryResult(QueryDisposition.INCONSISTENT_REGISTERED_ASSUMPTIONS, reason="EMPTY_FEASIBLE_SET")
    try:
        candidates = tuple(sorted({query[x] for x in obj.values}, key=repr))
    except TypeError:
        return QueryResult(QueryDisposition.CANNOT_CHECK, reason="QUERY_OUTPUT_NOT_FINITE_HASHABLE")
    failure_budget = obj.alpha if isinstance(obj, ConfidenceSet) else None
    if len(candidates) == 1:
        return QueryResult(QueryDisposition.IDENTIFIED, candidates=candidates, failure_budget=failure_budget)
    return QueryResult(QueryDisposition.CANNOT_IDENTIFY, candidates=candidates, failure_budget=failure_budget)


@dataclass(frozen=True)
class FiniteRelation:
    source_domain: tuple[Any, ...]
    target_domain: tuple[Any, ...]
    pairs: tuple[tuple[Any, Any], ...]
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        source = _domain(self.source_domain, "source_domain")
        target = _domain(self.target_domain, "target_domain")
        _provenance(self.provenance)
        if not isinstance(self.pairs, tuple):
            raise ValueError("pairs must be a tuple")
        if len(set(self.pairs)) != len(self.pairs):
            raise ValueError("relation pairs must be unique")
        for pair in self.pairs:
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise ValueError("relation entries must be source/target pairs")
            x, y = pair
            if x not in source or y not in target:
                raise ValueError("relation pair outside registered domains")


def relational_image(values: Iterable[Any], relation: FiniteRelation) -> tuple[Any, ...]:
    value_set = set(values)
    return tuple(sorted({y for x, y in relation.pairs if x in value_set}, key=repr))


def compose_relations(left: FiniteRelation, right: FiniteRelation) -> FiniteRelation:
    if left.target_domain != right.source_domain:
        raise ValueError("relation domains do not compose")
    pairs = tuple(sorted({(x, z) for x, y in left.pairs for y2, z in right.pairs if y == y2}, key=repr))
    return FiniteRelation(left.source_domain, right.target_domain, pairs, left.provenance + right.provenance + ("composed",))


def coverage_lower_bound(source_alpha: F, relation_betas: Iterable[F]) -> F:
    total = _budget(source_alpha, "source_alpha")
    for beta in relation_betas:
        total += _budget(beta, "relation_beta")
    return max(F(0), F(1) - total)


def product_good_probability(failure_budgets: Iterable[F], *, independence_registered: bool = False) -> F:
    budgets = tuple(_budget(x, "failure_budget") for x in failure_budgets)
    if not independence_registered:
        raise CannotCheckError("CANNOT_USE_PRODUCT_WITHOUT_REGISTERED_INDEPENDENCE")
    out = F(1)
    for beta in budgets:
        out *= 1 - beta
    return out


def propagate_feasible(source: FeasibleSet, relation: FiniteRelation | None, *, target_domain: tuple[Any, ...] | None, target_version: int, provenance: tuple[str, ...]) -> FeasibleSet | CannotCheck:
    if not isinstance(source, FeasibleSet):
        raise ValueError("source must be FeasibleSet")
    _version(target_version)
    _provenance(provenance)
    if target_domain is None:
        return CannotCheck("TARGET_DOMAIN_NOT_REGISTERED")
    target_domain = _domain(target_domain, "target_domain")
    if not source.values:
        return FeasibleSet(target_domain, (), target_version, provenance + ("upstream_inconsistency",))
    if relation is None:
        return FeasibleSet(target_domain, target_domain, target_version, provenance + ("missing_relation_full_domain",))
    if relation.source_domain != source.domain or relation.target_domain != target_domain:
        return CannotCheck("RELATION_DOMAIN_MISMATCH")
    return FeasibleSet(target_domain, relational_image(source.values, relation), target_version, provenance + ("relational_image",))


def propagate_confidence(source: ConfidenceSet, relation: FiniteRelation | None, relation_beta: F, *, target_domain: tuple[Any, ...] | None, target_version: int, provenance: tuple[str, ...]) -> ConfidenceSet | FeasibleSet | CannotCheck:
    if not isinstance(source, ConfidenceSet):
        raise ValueError("source must be ConfidenceSet")
    beta = _budget(relation_beta, "relation_beta")
    _version(target_version)
    _provenance(provenance)
    if target_domain is None:
        return CannotCheck("TARGET_DOMAIN_NOT_REGISTERED")
    target_domain = _domain(target_domain, "target_domain")
    if not source.values:
        return FeasibleSet(target_domain, (), target_version, provenance + ("upstream_inconsistency",))
    if relation is None:
        return FeasibleSet(target_domain, target_domain, target_version, provenance + ("missing_relation_full_domain",))
    if relation.source_domain != source.domain or relation.target_domain != target_domain:
        return CannotCheck("RELATION_DOMAIN_MISMATCH")
    image = relational_image(source.values, relation)
    if not image:
        return FeasibleSet(target_domain, (), target_version, provenance + ("registered_empty_image",))
    return ConfidenceSet(target_domain, image, min(F(1), source.alpha + beta), source.target, target_version, provenance + ("confidence_relational_image",), raw_evidence_count=0)


def transport_developmental_confidence(source: ConfidenceSet, relation: FiniteRelation | None, relation_beta: F, *, target_domain: tuple[Any, ...] | None, target_version: int, provenance: tuple[str, ...]) -> ConfidenceSet | FeasibleSet | CannotCheck:
    if type(target_version) is not int or target_version != source.version + 1:
        return CannotCheck("DEVELOPMENTAL_TRANSPORT_REQUIRES_ADJACENT_VERSION")
    return propagate_confidence(source, relation, relation_beta, target_domain=target_domain, target_version=target_version, provenance=provenance)


@dataclass(frozen=True)
class DAGNodeRelation:
    node: str
    parents: tuple[str, ...]
    domain: tuple[Any, ...]
    relation: tuple[tuple[tuple[Any, ...], Any], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.node, str) or not self.node:
            raise ValueError("node must be nonempty")
        if not isinstance(self.parents, tuple) or not self.parents:
            raise ValueError("non-root node must have at least one parent")
        if len(set(self.parents)) != len(self.parents):
            raise ValueError("parents must be unique")
        _domain(self.domain, f"domain[{self.node}]")
        if not isinstance(self.relation, tuple):
            raise ValueError("DAG relation must be a tuple")
        if len(set(self.relation)) != len(self.relation):
            raise ValueError("DAG relation entries must be unique")
        for parent_values, child in self.relation:
            if not isinstance(parent_values, tuple) or len(parent_values) != len(self.parents):
                raise ValueError("DAG parent tuple has wrong arity")
            if child not in self.domain:
                raise ValueError("DAG child outside node domain")


def global_feasible_assignments(roots: tuple[str, ...], root_domains: Mapping[str, tuple[Any, ...]], root_joint: tuple[tuple[Any, ...], ...], nodes: tuple[DAGNodeRelation, ...]) -> tuple[tuple[tuple[str, Any], ...], ...]:
    if not roots or len(set(roots)) != len(roots):
        raise ValueError("roots must be nonempty and unique")
    for root in roots:
        if root not in root_domains:
            raise ValueError("missing root domain")
        _domain(root_domains[root], f"root_domain[{root}]")
    if not isinstance(root_joint, tuple):
        raise ValueError("root_joint must be a tuple")
    assignments: list[dict[str, Any]] = []
    for row in root_joint:
        if not isinstance(row, tuple) or len(row) != len(roots):
            raise ValueError("root joint row has wrong arity")
        if any(row[i] not in root_domains[roots[i]] for i in range(len(roots))):
            raise ValueError("root joint row outside domain")
        assignments.append(dict(zip(roots, row)))
    registered = set(roots)
    registered_domains = {root: root_domains[root] for root in roots}
    for spec in nodes:
        if spec.node in registered or any(p not in registered for p in spec.parents):
            raise ValueError("nodes must be supplied once in topological order")
        for parent_values, _child in spec.relation:
            if any(parent_values[i] not in registered_domains[parent] for i, parent in enumerate(spec.parents)):
                raise ValueError("DAG relation parent tuple outside registered domains")
        relation_map: dict[tuple[Any, ...], list[Any]] = {}
        for parent_values, child in spec.relation:
            relation_map.setdefault(parent_values, []).append(child)
        next_assignments: list[dict[str, Any]] = []
        for assignment in assignments:
            key = tuple(assignment[p] for p in spec.parents)
            for child in relation_map.get(key, []):
                extended = dict(assignment)
                extended[spec.node] = child
                next_assignments.append(extended)
        assignments = next_assignments
        registered.add(spec.node)
        registered_domains[spec.node] = spec.domain
    return tuple(sorted({tuple(sorted(assignment.items())) for assignment in assignments}, key=repr))


def global_projection(assignments: tuple[tuple[tuple[str, Any], ...], ...], outputs: tuple[str, ...]) -> tuple[tuple[Any, ...], ...]:
    if not outputs:
        raise ValueError("outputs must be nonempty")
    projected = set()
    for row in assignments:
        d = dict(row)
        if any(name not in d for name in outputs):
            raise ValueError("output not present in assignment")
        projected.add(tuple(d[name] for name in outputs))
    return tuple(sorted(projected, key=repr))


def local_cartesian_propagation(root_sets: Mapping[str, tuple[Any, ...]], nodes: tuple[DAGNodeRelation, ...]) -> Mapping[str, tuple[Any, ...]]:
    sets: dict[str, tuple[Any, ...]] = {}
    for name, values in root_sets.items():
        if not isinstance(values, tuple) or not values:
            raise ValueError("root marginal sets must be nonempty tuples")
        sets[name] = tuple(sorted(set(values), key=repr))
    for spec in nodes:
        if any(p not in sets for p in spec.parents):
            raise ValueError("nodes must be supplied in topological order")
        legal_parent_tuples = set(product(*(sets[p] for p in spec.parents)))
        out = {child for parent_values, child in spec.relation if parent_values in legal_parent_tuples}
        sets[spec.node] = tuple(sorted(out, key=repr))
    return sets


def all_relations(domain: tuple[Any, ...]) -> tuple[tuple[tuple[Any, Any], ...], ...]:
    pairs = tuple(product(domain, domain))
    return tuple(tuple(pairs[i] for i in range(len(pairs)) if mask & (1 << i)) for mask in range(1 << len(pairs)))


def boole_union_census() -> Mapping[str, int]:
    universe = tuple(range(4))
    events = [{universe[i] for i in range(len(universe)) if mask & (1 << i)} for mask in range(1 << len(universe))]
    cases = failures = equality_cases = 0
    for a in events:
        for b in events:
            for c in events:
                true_good = F(len(universe) - len(a | b | c), len(universe))
                bound = max(F(0), F(1) - F(len(a), 4) - F(len(b), 4) - F(len(c), 4))
                cases += 1
                failures += int(true_good < bound)
                equality_cases += int(true_good == bound)
    return {"cases": cases, "failures": failures, "equality_cases": equality_cases}


def relation_composition_census() -> Mapping[str, int]:
    domain = (0, 1)
    relations = all_relations(domain)
    subsets = ((), (0,), (1,), (0, 1))
    cases = failures = 0
    for subset in subsets:
        for p1 in relations:
            r1 = FiniteRelation(domain, domain, p1, ("census-r1",))
            for p2 in relations:
                r2 = FiniteRelation(domain, domain, p2, ("census-r2",))
                direct = relational_image(relational_image(subset, r1), r2)
                composed = relational_image(subset, compose_relations(r1, r2))
                cases += 1
                failures += int(direct != composed)
    return {"cases": cases, "failures": failures}


def query_identification_census() -> Mapping[str, int]:
    domain = (0, 1, 2)
    query_values = (0, 1)
    cases = failures = empty_cases = singleton_cases = ambiguous_cases = 0
    subsets = []
    for k in range(4):
        subsets.extend(combinations(domain, k))
    for subset in subsets:
        fs = FeasibleSet(domain, tuple(subset), 0, ("query-census",))
        for outputs in product(query_values, repeat=len(domain)):
            query = dict(zip(domain, outputs))
            result = query_identified_set(fs, query)
            image = {query[x] for x in subset}
            expected = QueryDisposition.INCONSISTENT_REGISTERED_ASSUMPTIONS if not subset else QueryDisposition.IDENTIFIED if len(image) == 1 else QueryDisposition.CANNOT_IDENTIFY
            cases += 1
            failures += int(result.disposition != expected)
            empty_cases += int(not subset)
            singleton_cases += int(bool(subset) and len(image) == 1)
            ambiguous_cases += int(len(image) > 1)
    return {"cases": cases, "failures": failures, "empty_cases": empty_cases, "identified_cases": singleton_cases, "cannot_identify_cases": ambiguous_cases}


def shared_ancestor_witness() -> Mapping[str, Any]:
    roots = ("x",)
    root_domains = {"x": (-1, 1)}
    root_joint = ((-1,), (1,))
    a = DAGNodeRelation("a", ("x",), (-1, 1), (((-1,), -1), ((1,), 1)))
    b = DAGNodeRelation("b", ("x",), (-1, 1), (((-1,), -1), ((1,), 1)))
    y = DAGNodeRelation("y", ("a", "b"), (-2, 0, 2), tuple(((av, bv), av - bv) for av in (-1, 1) for bv in (-1, 1)))
    nodes = (a, b, y)
    exact = global_feasible_assignments(roots, root_domains, root_joint, nodes)
    global_y = tuple(row[0] for row in global_projection(exact, ("y",)))
    local = local_cartesian_propagation({"x": (-1, 1)}, nodes)
    return {"global_y": global_y, "local_y": local["y"], "strict_overapproximation": set(global_y) < set(local["y"]), "global_assignment_count": len(exact)}


def dependent_root_witness() -> Mapping[str, Any]:
    roots = ("r1", "r2")
    domains = {"r1": (0, 1), "r2": (0, 1)}
    joint = ((0, 0), (1, 1))
    y = DAGNodeRelation("y", roots, (0, 1), tuple(((a, b), a ^ b) for a in (0, 1) for b in (0, 1)))
    exact = global_feasible_assignments(roots, domains, joint, (y,))
    exact_y = tuple(row[0] for row in global_projection(exact, ("y",)))
    local = local_cartesian_propagation({"r1": (0, 1), "r2": (0, 1)}, (y,))
    return {"global_y": exact_y, "local_y": local["y"], "strict_overapproximation": set(exact_y) < set(local["y"]), "root_joint_size": len(joint), "root_cartesian_size": 4}


def anti_product_witness() -> Mapping[str, F]:
    universe = tuple(range(4))
    failure_a, failure_b = {0}, {1}
    good_both = {u for u in universe if u not in failure_a and u not in failure_b}
    return {"true_joint_good": F(len(good_both), len(universe)), "independence_product": F(3, 4) * F(3, 4), "union_bound_lower": coverage_lower_bound(F(1, 4), (F(1, 4),))}


def latent_nonidentifiability_witness() -> Mapping[str, Any]:
    outcomes = (F(0), F(1))
    latent = ("a", "b")
    prior = (F(1, 2), F(1, 2))
    pure_epistemic = LatentPredictiveModel(latent, prior, outcomes, ((F(1), F(0)), (F(0), F(1))), 0, ("pure-epistemic",))
    pure_aleatoric = LatentPredictiveModel(latent, prior, outcomes, ((F(1, 2), F(1, 2)), (F(1, 2), F(1, 2))), 0, ("pure-aleatoric",))
    law_e, law_a = pure_epistemic.predictive_law(), pure_aleatoric.predictive_law()
    decomp_e, decomp_a = pure_epistemic.variance_decomposition(), pure_aleatoric.variance_decomposition()
    return {
        "same_marginal": law_e.probabilities == law_a.probabilities,
        "marginal": law_e.probabilities,
        "pure_epistemic": decomp_e,
        "pure_aleatoric": decomp_a,
        "opposite_components": decomp_e["aleatoric"] == 0 and decomp_e["epistemic_mean"] == F(1, 4) and decomp_a["aleatoric"] == F(1, 4) and decomp_a["epistemic_mean"] == 0,
    }


def missing_empty_version_witness() -> Mapping[str, Any]:
    source_domain, target_domain = (0, 1), ("u", "v")
    source = ConfidenceSet(source_domain, (0,), F(1, 20), "theta", 3, ("source",), raw_evidence_count=2048)
    missing = propagate_confidence(source, None, F(0), target_domain=target_domain, target_version=4, provenance=("missing",))
    empty_relation = FiniteRelation(source_domain, target_domain, (), ("registered-empty",))
    empty = propagate_confidence(source, empty_relation, F(0), target_domain=target_domain, target_version=4, provenance=("empty",))
    missing_domain = propagate_confidence(source, None, F(0), target_domain=None, target_version=4, provenance=("no-target",))
    exact_relation = FiniteRelation(source_domain, target_domain, ((0, "u"), (1, "v")), ("exact",))
    transported = transport_developmental_confidence(source, exact_relation, F(1, 100), target_domain=target_domain, target_version=4, provenance=("transport",))
    if not isinstance(missing, FeasibleSet) or not isinstance(empty, FeasibleSet):
        raise AssertionError("unexpected missing/empty witness type")
    if not isinstance(missing_domain, CannotCheck) or not isinstance(transported, ConfidenceSet):
        raise AssertionError("unexpected version witness type")
    return {
        "missing_relation_kind": missing.kind.value,
        "missing_relation_knowledge": missing.knowledge.value,
        "missing_relation_values": missing.values,
        "empty_relation_knowledge": empty.knowledge.value,
        "empty_relation_values": empty.values,
        "missing_target_domain": missing_domain.disposition.value,
        "missing_target_reason": missing_domain.reason,
        "transported_alpha": transported.alpha,
        "transported_raw_evidence_count": transported.raw_evidence_count,
        "transported_values": transported.values,
    }


def query_controls() -> Mapping[str, Any]:
    domain = (0, 1)
    unknown = FeasibleSet(domain, domain, 0, ("unknown-control",))
    identity = query_identified_set(unknown, {0: 0, 1: 1})
    constant = query_identified_set(unknown, {0: 7, 1: 7})
    empty = FeasibleSet(domain, (), 0, ("empty-control",))
    inconsistent = query_identified_set(empty, {0: 0, 1: 1})
    cannot_check = query_identified_set(unknown, None)
    return {
        "state_knowledge": unknown.knowledge.value,
        "identity_query": {"disposition": identity.disposition.value, "candidates": identity.candidates},
        "constant_query": {"disposition": constant.disposition.value, "candidates": constant.candidates},
        "empty_query": {"disposition": inconsistent.disposition.value, "reason": inconsistent.reason},
        "missing_query": {"disposition": cannot_check.disposition.value, "reason": cannot_check.reason},
        "machine_distinct": len({SetKnowledge.UNKNOWN.value, identity.disposition.value, inconsistent.disposition.value, cannot_check.disposition.value}) == 4,
    }


def jsonable(obj: Any) -> Any:
    if isinstance(obj, Fraction):
        return frac(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list, set)):
        return [jsonable(v) for v in obj]
    return obj


def build_receipt() -> Mapping[str, Any]:
    relation_census = relation_composition_census()
    boole_census = boole_union_census()
    query_census = query_identification_census()
    shared, roots = shared_ancestor_witness(), dependent_root_witness()
    anti_product, latent = anti_product_witness(), latent_nonidentifiability_witness()
    transport, queries = missing_empty_version_witness(), query_controls()
    bound = coverage_lower_bound(F(1, 20), (F(1, 100), F(1, 200)))
    product_blocked = False
    try:
        product_good_probability((F(1, 4), F(1, 4)))
    except CannotCheckError:
        product_blocked = True
    marginal_blocked = False
    try:
        PredictiveLaw((F(0), F(1)), (F(1, 2), F(1, 2)), 0, ("marginal-only",)).epistemic_aleatoric_decomposition()
    except CannotCheckError:
        marginal_blocked = True
    all_green = all((
        relation_census["failures"] == 0,
        boole_census["cases"] == 4096,
        boole_census["failures"] == 0,
        query_census["failures"] == 0,
        shared["global_y"] == (0,),
        shared["local_y"] == (-2, 0, 2),
        shared["strict_overapproximation"],
        roots["global_y"] == (0,),
        roots["local_y"] == (0, 1),
        roots["strict_overapproximation"],
        anti_product["true_joint_good"] == F(1, 2),
        anti_product["independence_product"] == F(9, 16),
        anti_product["union_bound_lower"] == F(1, 2),
        product_blocked,
        latent["same_marginal"],
        latent["opposite_components"],
        marginal_blocked,
        transport["missing_relation_knowledge"] == SetKnowledge.UNKNOWN.value,
        transport["empty_relation_knowledge"] == SetKnowledge.INCONSISTENT_REGISTERED_ASSUMPTIONS.value,
        transport["missing_target_domain"] == QueryDisposition.CANNOT_CHECK.value,
        transport["transported_raw_evidence_count"] == 0,
        queries["machine_distinct"],
        queries["identity_query"]["disposition"] == QueryDisposition.CANNOT_IDENTIFY.value,
        queries["constant_query"]["disposition"] == QueryDisposition.IDENTIFIED.value,
        bound == F(187, 200),
    ))
    return {
        "schema": "GMI833GlobalUncertaintyReceiptV1",
        "issue": 851,
        "parent_issue": 833,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "typed_kinds": tuple(kind.value for kind in UncertaintyKind),
        "query_dispositions": tuple(kind.value for kind in QueryDisposition),
        "set_knowledge_states": tuple(kind.value for kind in SetKnowledge),
        "relation_composition_census": relation_census,
        "boole_union_census": boole_census,
        "query_identification_census": query_census,
        "dependence_safe_bound": {"source_alpha": F(1, 20), "relation_betas": (F(1, 100), F(1, 200)), "coverage_lower_bound": bound},
        "anti_product_hostile": {**anti_product, "product_without_independence_blocked": product_blocked},
        "shared_ancestor_hostile": shared,
        "dependent_root_hostile": roots,
        "query_controls": queries,
        "missing_empty_version_controls": transport,
        "latent_nonidentifiability": {**latent, "marginal_only_decomposition_blocked": marginal_blocked},
        "parent_ownership": {
            "chain_composition": "#757/#761",
            "dag_composition": "#759/#765",
            "developmental_transport": "#748/#749",
            "epistemic_aleatoric": "#750/#751",
            "selective_calibration": "#766/#767",
        },
        "terminal": "GMI_833_GLOBAL_UNCERTAINTY_V1_ALL_GREEN" if all_green else "GMI_833_GLOBAL_UNCERTAINTY_V1_RED",
    }


if __name__ == "__main__":
    print(json.dumps(jsonable(build_receipt()), indent=2, sort_keys=True))
