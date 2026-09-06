from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Iterable


class CriticalFailure(str, Enum):
    FALSE_COMPLETION = "FALSE_COMPLETION"
    UNSAFE_TRANSPORT = "UNSAFE_TRANSPORT"
    AUTHORITY_VIOLATION = "AUTHORITY_VIOLATION"
    EVIDENCE_CORRUPTION = "EVIDENCE_CORRUPTION"
    CRITERION_DRIFT = "CRITERION_DRIFT"
    PROTECTED_CAPABILITY_LOSS = "PROTECTED_CAPABILITY_LOSS"


@dataclass(frozen=True, slots=True)
class CostVector:
    latency: float = 0.0
    compute: float = 0.0
    memory: float = 0.0
    annotation: float = 0.0
    implementation: float = 0.0

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            value = getattr(self, name)
            if not isfinite(value) or value < 0:
                raise ValueError("cost coordinates must be finite and non-negative")

    def no_worse_than(self, other: CostVector, tolerance: float = 0.0) -> bool:
        if tolerance < 0:
            raise ValueError("tolerance must be non-negative")
        return all(
            getattr(self, name) <= getattr(other, name) + tolerance
            for name in self.__dataclass_fields__
        )

    def strictly_better_than(
        self, other: CostVector, tolerance: float = 0.0
    ) -> bool:
        return self.no_worse_than(other, tolerance) and any(
            getattr(self, name) < getattr(other, name) - tolerance
            for name in self.__dataclass_fields__
        )


@dataclass(frozen=True, slots=True)
class ConfigurationCaseResult:
    case_id: str
    configuration_id: str
    enabled_components: frozenset[str]
    protected_success: bool
    quality: float
    critical_failures: frozenset[CriticalFailure] = frozenset()
    costs: CostVector = CostVector()

    def __post_init__(self) -> None:
        if not self.case_id.strip() or not self.configuration_id.strip():
            raise ValueError("case and configuration identities are required")
        if not isfinite(self.quality) or not 0 <= self.quality <= 1:
            raise ValueError("quality must be finite and within [0, 1]")
        object.__setattr__(
            self,
            "critical_failures",
            frozenset(CriticalFailure(item) for item in self.critical_failures),
        )
        if self.protected_success and self.critical_failures:
            raise ValueError(
                "a configuration with a critical failure cannot be a protected success"
            )


def result_dominates(
    left: ConfigurationCaseResult,
    right: ConfigurationCaseResult,
    *,
    quality_tolerance: float = 0.0,
    cost_tolerance: float = 0.0,
) -> bool:
    """Return whether ``left`` Pareto-dominates ``right`` on one frozen case.

    Critical failures and protected success are non-compensatory. Quality and
    each cost coordinate are then compared without collapsing them to a single
    scalar.
    """
    if left.case_id != right.case_id:
        raise ValueError("dominance requires the same frozen case")
    if quality_tolerance < 0 or cost_tolerance < 0:
        raise ValueError("tolerances must be non-negative")
    hard_no_worse = (
        left.critical_failures <= right.critical_failures
        and (left.protected_success or not right.protected_success)
    )
    hard_strictly_better = (
        left.critical_failures < right.critical_failures
        or (left.protected_success and not right.protected_success)
    )
    if not hard_no_worse:
        return False
    if hard_strictly_better:
        return True
    quality_no_worse = left.quality + quality_tolerance >= right.quality
    cost_no_worse = left.costs.no_worse_than(right.costs, cost_tolerance)
    strict = (
        left.quality > right.quality + quality_tolerance
        or left.costs.strictly_better_than(right.costs, cost_tolerance)
    )
    return quality_no_worse and cost_no_worse and strict


def pareto_frontier(
    results: Iterable[ConfigurationCaseResult],
    *,
    quality_tolerance: float = 0.0,
    cost_tolerance: float = 0.0,
) -> tuple[str, ...]:
    """Return non-dominated configuration IDs for a single frozen case."""
    frozen = tuple(results)
    if not frozen:
        return ()
    case_ids = {result.case_id for result in frozen}
    if len(case_ids) != 1:
        raise ValueError("a Pareto frontier is computed for one frozen case")
    configuration_ids = [result.configuration_id for result in frozen]
    if len(configuration_ids) != len(set(configuration_ids)):
        raise ValueError("configuration identities must be unique within a case")
    non_dominated = []
    for candidate in frozen:
        if not any(
            other.configuration_id != candidate.configuration_id
            and result_dominates(
                other,
                candidate,
                quality_tolerance=quality_tolerance,
                cost_tolerance=cost_tolerance,
            )
            for other in frozen
        ):
            non_dominated.append(candidate.configuration_id)
    return tuple(sorted(non_dominated))


class ComponentValueStatus(str, Enum):
    NECESSARY = "NECESSARY"
    PARENT_REPLACEABLE = "PARENT_REPLACEABLE"
    CONTEXTUAL = "CONTEXTUAL"
    EFFICIENCY_IMPROVING = "EFFICIENCY_IMPROVING"
    REDUNDANT_DRAG = "REDUNDANT_DRAG"
    HARMFUL = "HARMFUL"
    NO_MEASURABLE_VALUE = "NO_MEASURABLE_VALUE"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True, slots=True)
class ComponentValueAssessment:
    component_id: str
    status: ComponentValueStatus
    matched_case_ids: tuple[str, ...]
    protected_regression_case_ids: tuple[str, ...]
    protected_improvement_case_ids: tuple[str, ...]
    quality_gain_case_ids: tuple[str, ...]
    quality_harm_case_ids: tuple[str, ...]
    ablation_dominates_case_ids: tuple[str, ...]
    full_dominates_case_ids: tuple[str, ...]
    parent_replacement_case_ids: tuple[str, ...]
    authority_granted: bool = False

    def __post_init__(self) -> None:
        if self.authority_granted:
            raise ValueError("component attribution cannot grant architecture authority")


def _index_by_case(
    results: Iterable[ConfigurationCaseResult],
) -> dict[str, ConfigurationCaseResult]:
    indexed: dict[str, ConfigurationCaseResult] = {}
    for result in results:
        if result.case_id in indexed:
            raise ValueError("each configuration arm may contain one result per case")
        indexed[result.case_id] = result
    return indexed


def _noninferior_to(
    candidate: ConfigurationCaseResult,
    reference: ConfigurationCaseResult,
    *,
    quality_tolerance: float,
    cost_tolerance: float,
) -> bool:
    return (
        candidate.critical_failures <= reference.critical_failures
        and (candidate.protected_success or not reference.protected_success)
        and candidate.quality + quality_tolerance >= reference.quality
        and candidate.costs.no_worse_than(reference.costs, cost_tolerance)
    )


def assess_component_value(
    component_id: str,
    full_results: Iterable[ConfigurationCaseResult],
    ablated_results: Iterable[ConfigurationCaseResult],
    *,
    parent_replacement_results: Iterable[ConfigurationCaseResult] = (),
    quality_tolerance: float = 0.01,
    cost_tolerance: float = 0.0,
) -> ComponentValueAssessment:
    """Assess one component from matched full/ablation/reference arms.

    This is a transparent decision rule for frozen protected cases, not a
    statistical estimator and not proof that the tested cases exhaust future
    contexts.
    """
    if not component_id.strip():
        raise ValueError("component identity is required")
    if quality_tolerance < 0 or cost_tolerance < 0:
        raise ValueError("tolerances must be non-negative")
    full = _index_by_case(full_results)
    ablated = _index_by_case(ablated_results)
    parents = _index_by_case(parent_replacement_results)
    matched = tuple(sorted(full.keys() & ablated.keys()))
    if not matched:
        return ComponentValueAssessment(
            component_id,
            ComponentValueStatus.CANNOT_CHECK,
            (),
            (),
            (),
            (),
            (),
            (),
            (),
            (),
        )

    protected_regressions: list[str] = []
    protected_improvements: list[str] = []
    quality_gains: list[str] = []
    quality_harms: list[str] = []
    ablation_dominates: list[str] = []
    full_dominates: list[str] = []
    parent_replacements: list[str] = []

    for case_id in matched:
        full_result = full[case_id]
        ablated_result = ablated[case_id]
        if component_id not in full_result.enabled_components:
            raise ValueError("full arm must contain the assessed component")
        if component_id in ablated_result.enabled_components:
            raise ValueError("ablation arm must remove the assessed component")

        if (
            full_result.protected_success
            and not ablated_result.protected_success
        ) or not (
            ablated_result.critical_failures
            <= full_result.critical_failures
        ):
            protected_regressions.append(case_id)

        if (
            ablated_result.protected_success
            and not full_result.protected_success
        ) or not (
            full_result.critical_failures
            <= ablated_result.critical_failures
        ):
            protected_improvements.append(case_id)

        if full_result.quality > ablated_result.quality + quality_tolerance:
            quality_gains.append(case_id)
        if ablated_result.quality > full_result.quality + quality_tolerance:
            quality_harms.append(case_id)

        if result_dominates(
            ablated_result,
            full_result,
            quality_tolerance=quality_tolerance,
            cost_tolerance=cost_tolerance,
        ):
            ablation_dominates.append(case_id)
        if result_dominates(
            full_result,
            ablated_result,
            quality_tolerance=quality_tolerance,
            cost_tolerance=cost_tolerance,
        ):
            full_dominates.append(case_id)

        parent_result = parents.get(case_id)
        if parent_result is not None:
            if component_id in parent_result.enabled_components:
                raise ValueError(
                    "a parent-replacement arm must not retain the assessed component"
                )
            if _noninferior_to(
                parent_result,
                full_result,
                quality_tolerance=quality_tolerance,
                cost_tolerance=cost_tolerance,
            ):
                parent_replacements.append(case_id)

    scientific_benefit_cases = set(protected_regressions) | set(quality_gains)
    scientific_harm_cases = set(protected_improvements) | set(quality_harms)
    ablation_cost_savings = {
        case_id
        for case_id in matched
        if ablated[case_id].costs.strictly_better_than(
            full[case_id].costs, cost_tolerance
        )
    }
    full_cost_savings = {
        case_id
        for case_id in matched
        if full[case_id].costs.strictly_better_than(
            ablated[case_id].costs, cost_tolerance
        )
    }

    if scientific_benefit_cases and scientific_harm_cases:
        status = ComponentValueStatus.CONTEXTUAL
    elif scientific_benefit_cases:
        if scientific_benefit_cases <= set(parent_replacements):
            status = ComponentValueStatus.PARENT_REPLACEABLE
        else:
            status = ComponentValueStatus.NECESSARY
    elif scientific_harm_cases:
        status = ComponentValueStatus.HARMFUL
    elif ablation_cost_savings and full_cost_savings:
        status = ComponentValueStatus.CONTEXTUAL
    elif ablation_cost_savings:
        status = ComponentValueStatus.REDUNDANT_DRAG
    elif full_cost_savings:
        status = ComponentValueStatus.EFFICIENCY_IMPROVING
    else:
        status = ComponentValueStatus.NO_MEASURABLE_VALUE

    return ComponentValueAssessment(
        component_id,
        status,
        matched,
        tuple(sorted(protected_regressions)),
        tuple(sorted(protected_improvements)),
        tuple(sorted(quality_gains)),
        tuple(sorted(quality_harms)),
        tuple(sorted(ablation_dominates)),
        tuple(sorted(full_dominates)),
        tuple(sorted(parent_replacements)),
    )


class PairInteractionStatus(str, Enum):
    SYNERGISTIC = "SYNERGISTIC"
    SUBSTITUTABLE = "SUBSTITUTABLE"
    ADDITIVE = "ADDITIVE"
    CONTEXTUAL_INTERACTION = "CONTEXTUAL_INTERACTION"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True, slots=True)
class PairInteractionAssessment:
    component_a: str
    component_b: str
    status: PairInteractionStatus
    matched_case_ids: tuple[str, ...]
    interaction_by_case: tuple[tuple[str, float], ...]
    excluded_case_ids: tuple[str, ...]
    authority_granted: bool = False

    def __post_init__(self) -> None:
        if self.authority_granted:
            raise ValueError("interaction attribution cannot grant architecture authority")


def _bounded_scientific_utility(result: ConfigurationCaseResult) -> float:
    if result.critical_failures or not result.protected_success:
        return 0.0
    return result.quality


def assess_pair_interaction(
    component_a: str,
    component_b: str,
    full_results: Iterable[ConfigurationCaseResult],
    minus_a_results: Iterable[ConfigurationCaseResult],
    minus_b_results: Iterable[ConfigurationCaseResult],
    minus_both_results: Iterable[ConfigurationCaseResult],
    *,
    interaction_tolerance: float = 0.05,
) -> PairInteractionAssessment:
    """Diagnose complementarity/substitutability from a 2x2 intervention.

    The interaction score for a case is
    ``u(AB) - u(A) - u(B) + u(empty)`` where invalid configurations receive
    zero bounded scientific utility. Positive values indicate complementarity;
    negative values indicate substitutability. Cases whose full configuration
    is not a protected success are excluded because component value is not
    identifiable from an already-invalid reference.
    """
    if not component_a.strip() or not component_b.strip():
        raise ValueError("component identities are required")
    if component_a == component_b:
        raise ValueError("pair interaction requires distinct components")
    if interaction_tolerance < 0:
        raise ValueError("interaction tolerance must be non-negative")

    full = _index_by_case(full_results)
    minus_a = _index_by_case(minus_a_results)
    minus_b = _index_by_case(minus_b_results)
    minus_both = _index_by_case(minus_both_results)
    matched = tuple(
        sorted(full.keys() & minus_a.keys() & minus_b.keys() & minus_both.keys())
    )
    if not matched:
        return PairInteractionAssessment(
            component_a,
            component_b,
            PairInteractionStatus.CANNOT_CHECK,
            (),
            (),
            (),
        )

    interactions: list[tuple[str, float]] = []
    excluded: list[str] = []
    per_case_statuses: list[PairInteractionStatus] = []

    for case_id in matched:
        full_result = full[case_id]
        a_removed = minus_a[case_id]
        b_removed = minus_b[case_id]
        both_removed = minus_both[case_id]

        if not {component_a, component_b} <= full_result.enabled_components:
            raise ValueError("full arm must contain both assessed components")
        if (
            component_a in a_removed.enabled_components
            or component_b not in a_removed.enabled_components
        ):
            raise ValueError("minus-a arm must remove only component A of the pair")
        if (
            component_b in b_removed.enabled_components
            or component_a not in b_removed.enabled_components
        ):
            raise ValueError("minus-b arm must remove only component B of the pair")
        if (
            component_a in both_removed.enabled_components
            or component_b in both_removed.enabled_components
        ):
            raise ValueError("minus-both arm must remove both assessed components")

        if not full_result.protected_success or full_result.critical_failures:
            excluded.append(case_id)
            continue

        u_full = _bounded_scientific_utility(full_result)
        u_without_a = _bounded_scientific_utility(a_removed)
        u_without_b = _bounded_scientific_utility(b_removed)
        u_without_both = _bounded_scientific_utility(both_removed)
        interaction = u_full - u_without_a - u_without_b + u_without_both
        interactions.append((case_id, interaction))

        if interaction > interaction_tolerance:
            per_case_statuses.append(PairInteractionStatus.SYNERGISTIC)
        elif interaction < -interaction_tolerance:
            per_case_statuses.append(PairInteractionStatus.SUBSTITUTABLE)
        else:
            per_case_statuses.append(PairInteractionStatus.ADDITIVE)

    if not per_case_statuses:
        status = PairInteractionStatus.CANNOT_CHECK
    elif len(set(per_case_statuses)) == 1:
        status = per_case_statuses[0]
    else:
        status = PairInteractionStatus.CONTEXTUAL_INTERACTION

    return PairInteractionAssessment(
        component_a,
        component_b,
        status,
        matched,
        tuple(interactions),
        tuple(sorted(excluded)),
    )
