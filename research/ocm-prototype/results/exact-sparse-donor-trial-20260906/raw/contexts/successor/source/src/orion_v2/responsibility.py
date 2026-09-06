from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from typing import Hashable, Mapping


class ResponsibilityTopology(str, Enum):
    SINGLE = "SINGLE"
    SERIAL_UPSTREAM = "SERIAL_UPSTREAM"
    MULTIPLE_INDEPENDENT = "MULTIPLE_INDEPENDENT"
    DISTRIBUTED = "DISTRIBUTED"
    INTERACTION_ONLY = "INTERACTION_ONLY"
    UNRESOLVED = "UNRESOLVED"


class DiagnosisStatus(str, Enum):
    IDENTIFIED = "IDENTIFIED"
    MULTIPLE_DISCRIMINABLE = "MULTIPLE_DISCRIMINABLE"
    STRUCTURALLY_NONIDENTIFIABLE = "STRUCTURALLY_NONIDENTIFIABLE"
    CONTRADICTION = "CONTRADICTION"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True, slots=True)
class ResponsibilityHypothesis:
    hypothesis_id: str
    causes: frozenset[str]
    topology: ResponsibilityTopology
    predicted_observations: frozenset[str]
    preference_rank: int = 0

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip() or not self.causes:
            raise ValueError("responsibility hypotheses require identity and causes")
        object.__setattr__(self, "topology", ResponsibilityTopology(self.topology))
        if self.preference_rank < 0:
            raise ValueError("preference rank must be non-negative")
        if self.topology is ResponsibilityTopology.INTERACTION_ONLY and len(self.causes) < 2:
            raise ValueError("interaction-only hypotheses require at least two causes")


@dataclass(frozen=True, slots=True)
class DiagnosticProbe:
    probe_id: str
    outcome_by_hypothesis: Mapping[str, Hashable]
    cost: float = 0.0

    def __post_init__(self) -> None:
        if not self.probe_id.strip() or not self.outcome_by_hypothesis:
            raise ValueError("diagnostic probes require identity and outcomes")
        if self.cost < 0:
            raise ValueError("probe cost must be non-negative")


@dataclass(frozen=True, slots=True)
class ResponsibilityAssessment:
    status: DiagnosisStatus
    candidate_hypothesis_ids: tuple[str, ...]
    minimal_hypothesis_ids: tuple[str, ...]
    minimum_probe_ids: tuple[str, ...]
    authority_granted: bool = False

    def __post_init__(self) -> None:
        if self.authority_granted:
            raise ValueError("responsibility diagnosis does not grant blame or authority")


def _minimal_hypotheses(
    hypotheses: tuple[ResponsibilityHypothesis, ...],
) -> tuple[ResponsibilityHypothesis, ...]:
    preferred_rank = min(hypothesis.preference_rank for hypothesis in hypotheses)
    preferred = tuple(
        hypothesis
        for hypothesis in hypotheses
        if hypothesis.preference_rank == preferred_rank
    )
    return tuple(
        hypothesis
        for hypothesis in preferred
        if not any(
            other.causes < hypothesis.causes
            for other in preferred
            if other.hypothesis_id != hypothesis.hypothesis_id
        )
    )


def _separates_all(
    hypothesis_ids: tuple[str, ...],
    probes: tuple[DiagnosticProbe, ...],
) -> bool:
    for left_index, left in enumerate(hypothesis_ids):
        for right in hypothesis_ids[left_index + 1 :]:
            if all(
                probe.outcome_by_hypothesis.get(left)
                == probe.outcome_by_hypothesis.get(right)
                for probe in probes
            ):
                return False
    return True


def minimum_diagnostic_probe_set(
    hypothesis_ids: tuple[str, ...],
    probes: tuple[DiagnosticProbe, ...],
) -> tuple[str, ...]:
    if len(hypothesis_ids) <= 1:
        return ()
    for probe in probes:
        if set(hypothesis_ids) - set(probe.outcome_by_hypothesis):
            raise ValueError(
                "every probe must define an outcome for every candidate hypothesis"
            )
    ordered = tuple(sorted(probes, key=lambda probe: (probe.cost, probe.probe_id)))
    for size in range(1, len(ordered) + 1):
        candidates = [
            combo
            for combo in combinations(ordered, size)
            if _separates_all(hypothesis_ids, combo)
        ]
        if candidates:
            best = min(
                candidates,
                key=lambda combo: (
                    sum(probe.cost for probe in combo),
                    tuple(probe.probe_id for probe in combo),
                ),
            )
            return tuple(probe.probe_id for probe in best)
    return ()


def assess_responsibility(
    observed: frozenset[str],
    hypotheses: tuple[ResponsibilityHypothesis, ...],
    probes: tuple[DiagnosticProbe, ...] = (),
) -> ResponsibilityAssessment:
    if not observed or not hypotheses:
        return ResponsibilityAssessment(DiagnosisStatus.CANNOT_CHECK, (), (), ())
    ids = [hypothesis.hypothesis_id for hypothesis in hypotheses]
    if len(ids) != len(set(ids)):
        raise ValueError("hypothesis identities must be unique")
    candidates = tuple(
        hypothesis
        for hypothesis in hypotheses
        if observed <= hypothesis.predicted_observations
    )
    if not candidates:
        return ResponsibilityAssessment(DiagnosisStatus.CONTRADICTION, (), (), ())
    minimal = _minimal_hypotheses(candidates)
    candidate_ids = tuple(sorted(hypothesis.hypothesis_id for hypothesis in candidates))
    minimal_ids = tuple(sorted(hypothesis.hypothesis_id for hypothesis in minimal))
    if len(minimal_ids) == 1:
        return ResponsibilityAssessment(
            DiagnosisStatus.IDENTIFIED,
            candidate_ids,
            minimal_ids,
            (),
        )
    probe_ids = minimum_diagnostic_probe_set(minimal_ids, probes) if probes else ()
    status = (
        DiagnosisStatus.MULTIPLE_DISCRIMINABLE
        if probe_ids
        else DiagnosisStatus.STRUCTURALLY_NONIDENTIFIABLE
    )
    return ResponsibilityAssessment(status, candidate_ids, minimal_ids, probe_ids)
