"""Research-only local-to-global epistemic atlas semantics.

This module hardens the Epistemic Locality programme without claiming that a
finite machine can enumerate a total space of possible epistemic mechanisms.
It provides exact finite reference objects for:

* local epistemic contexts/charts and typed context maps;
* overlap compatibility versus witnessed global gluing;
* probe-induced observational equivalence and strict partition refinement;
* explicit epistemic-horizon / outside-current-atlas states; and
* scoped globality claims that stop short of an empirical absolute-universal
  level.

The construction is deliberately presheaf/fibration-like rather than declaring
that every ORION domain forms a sheaf. Sheaf, cohomological or other stronger
mathematics may be used only when their domain assumptions are actually bound.
Nothing in this module grants scientific truth, novelty, field status,
architecture authority, or publication authority, and it is intentionally not
re-exported from :mod:`orion_v2.kernel`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from .epistemic_architecture import CapabilityContext


def _ids(values: Iterable[str], *, name: str, allow_empty: bool = False) -> tuple[str, ...]:
    result = tuple(values)
    if not allow_empty and not result:
        raise ValueError(f"{name} must not be empty")
    if any(not value.strip() for value in result):
        raise ValueError(f"{name} may not contain blank identities")
    if len(result) != len(set(result)):
        raise ValueError(f"{name} identities must be unique")
    return result


class UnknownKind(StrEnum):
    """Operational unknown classes inside an explicitly bounded atlas.

    ``OUTSIDE_CURRENT_ATLAS`` is a sentinel for a witnessed residual that cannot
    yet be represented by the other classes. It is not an enumeration of the
    complement of an unknown total epistemic space.
    """

    KNOWN_UNCERTAINTY = "KNOWN_UNCERTAINTY"
    OPEN_WORLD_NOVELTY = "OPEN_WORLD_NOVELTY"
    MODEL_FAMILY_INSUFFICIENCY = "MODEL_FAMILY_INSUFFICIENCY"
    REPRESENTATION_INSUFFICIENCY = "REPRESENTATION_INSUFFICIENCY"
    PROBE_OR_ACTION_INSUFFICIENCY = "PROBE_OR_ACTION_INSUFFICIENCY"
    CONTEXT_SCALE_BOUNDARY_INSUFFICIENCY = "CONTEXT_SCALE_BOUNDARY_INSUFFICIENCY"
    FORMALISM_OR_OPERATOR_INSUFFICIENCY = "FORMALISM_OR_OPERATOR_INSUFFICIENCY"
    OUTSIDE_CURRENT_ATLAS = "OUTSIDE_CURRENT_ATLAS"


@dataclass(frozen=True, slots=True)
class UnknownRecord:
    unknown_id: str
    kind: UnknownKind
    witness_ids: tuple[str, ...]
    current_representation_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.unknown_id.strip():
            raise ValueError("unknown records require an identity")
        object.__setattr__(self, "kind", UnknownKind(self.kind))
        object.__setattr__(self, "witness_ids", _ids(self.witness_ids, name="witness_ids"))
        object.__setattr__(
            self,
            "current_representation_ids",
            _ids(self.current_representation_ids, name="current_representation_ids", allow_empty=True),
        )
        if self.kind is UnknownKind.OUTSIDE_CURRENT_ATLAS and not self.witness_ids:
            raise ValueError("outside-current-atlas state requires a residual/obstruction witness")


@dataclass(frozen=True, slots=True)
class EpistemicContext:
    context_id: str
    capability_context: CapabilityContext
    authority_context_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.context_id.strip():
            raise ValueError("epistemic contexts require an identity")
        object.__setattr__(
            self,
            "authority_context_ids",
            _ids(self.authority_context_ids, name="authority_context_ids"),
        )


class ContextMapKind(StrEnum):
    RESTRICTION = "RESTRICTION"
    EMBEDDING = "EMBEDDING"
    SCALE_CHANGE = "SCALE_CHANGE"
    BOUNDARY_CHANGE = "BOUNDARY_CHANGE"
    REPRESENTATION_TRANSPORT = "REPRESENTATION_TRANSPORT"
    DECISION_TRANSPORT = "DECISION_TRANSPORT"


@dataclass(frozen=True, slots=True)
class ContextMap:
    map_id: str
    source_context_id: str
    target_context_id: str
    kind: ContextMapKind
    witness_ids: tuple[str, ...]
    loss_or_scope_ids: tuple[str, ...] = ()
    transport_authorized: bool = False

    def __post_init__(self) -> None:
        for value in (self.map_id, self.source_context_id, self.target_context_id):
            if not value.strip():
                raise ValueError("context maps require identities")
        if self.source_context_id == self.target_context_id:
            raise ValueError("context maps must connect distinct registered contexts")
        object.__setattr__(self, "kind", ContextMapKind(self.kind))
        object.__setattr__(self, "witness_ids", _ids(self.witness_ids, name="witness_ids"))
        object.__setattr__(
            self,
            "loss_or_scope_ids",
            _ids(self.loss_or_scope_ids, name="loss_or_scope_ids", allow_empty=True),
        )
        if self.transport_authorized:
            raise ValueError("context-map receipts are non-authorizing")


@dataclass(frozen=True, slots=True)
class LocalEpistemicChart:
    chart_id: str
    context_id: str
    local_state_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.chart_id.strip() or not self.context_id.strip():
            raise ValueError("local charts require identities")
        object.__setattr__(self, "local_state_ids", _ids(self.local_state_ids, name="local_state_ids"))


@dataclass(frozen=True, slots=True)
class OverlapAssessment:
    overlap_id: str
    left_chart_id: str
    right_chart_id: str
    compatible: bool | None
    witness_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value in (self.overlap_id, self.left_chart_id, self.right_chart_id):
            if not value.strip():
                raise ValueError("overlap assessments require identities")
        if self.left_chart_id == self.right_chart_id:
            raise ValueError("an overlap must compare distinct charts")
        object.__setattr__(
            self,
            "witness_ids",
            _ids(self.witness_ids, name="witness_ids", allow_empty=True),
        )
        if self.compatible is not None and not self.witness_ids:
            raise ValueError("a compatibility verdict requires a witness")


class GluingStatus(StrEnum):
    GLOBAL_SECTION_WITNESSED = "GLOBAL_SECTION_WITNESSED"
    MATCHING_FAMILY_ONLY = "MATCHING_FAMILY_ONLY"
    GLOBAL_SECTION_OBSTRUCTED = "GLOBAL_SECTION_OBSTRUCTED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True, slots=True)
class AtlasGluingReceipt:
    status: GluingStatus
    chart_ids: tuple[str, ...]
    overlap_ids: tuple[str, ...]
    reasons: tuple[str, ...]
    global_section_witness_id: str = ""
    scientific_truth_authorized: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", GluingStatus(self.status))
        object.__setattr__(self, "chart_ids", _ids(self.chart_ids, name="chart_ids"))
        object.__setattr__(self, "overlap_ids", _ids(self.overlap_ids, name="overlap_ids", allow_empty=True))
        if not self.reasons or any(not reason.strip() for reason in self.reasons):
            raise ValueError("gluing receipts require reasons")
        if self.scientific_truth_authorized:
            raise ValueError("atlas gluing receipts are non-authorizing")
        if self.status is GluingStatus.GLOBAL_SECTION_WITNESSED and not self.global_section_witness_id.strip():
            raise ValueError("a witnessed global section requires a witness identity")


def assess_atlas_gluing(
    charts: tuple[LocalEpistemicChart, ...],
    overlaps: tuple[OverlapAssessment, ...],
    *,
    global_section_witness_id: str = "",
) -> AtlasGluingReceipt:
    """Assess finite exact local compatibility without overclaiming gluing.

    Pairwise/overlap compatibility produces only ``MATCHING_FAMILY_ONLY`` unless
    a separate global-section witness is supplied. This prevents a local
    consistency check from silently becoming a global ontology claim.
    """

    if not charts:
        raise ValueError("an epistemic atlas requires at least one local chart")
    chart_ids = tuple(chart.chart_id for chart in charts)
    if len(chart_ids) != len(set(chart_ids)):
        raise ValueError("chart identities must be unique")
    known = set(chart_ids)
    for overlap in overlaps:
        if overlap.left_chart_id not in known or overlap.right_chart_id not in known:
            raise ValueError("overlap references an unknown chart")

    if any(overlap.compatible is False for overlap in overlaps):
        failed = tuple(overlap.overlap_id for overlap in overlaps if overlap.compatible is False)
        return AtlasGluingReceipt(
            GluingStatus.GLOBAL_SECTION_OBSTRUCTED,
            chart_ids,
            tuple(overlap.overlap_id for overlap in overlaps),
            tuple(f"incompatible overlap {item}" for item in failed),
        )
    if any(overlap.compatible is None for overlap in overlaps):
        unresolved = tuple(overlap.overlap_id for overlap in overlaps if overlap.compatible is None)
        return AtlasGluingReceipt(
            GluingStatus.CANNOT_CHECK,
            chart_ids,
            tuple(overlap.overlap_id for overlap in overlaps),
            tuple(f"unresolved overlap {item}" for item in unresolved),
        )
    if len(charts) > 1 and not overlaps:
        return AtlasGluingReceipt(
            GluingStatus.CANNOT_CHECK,
            chart_ids,
            (),
            ("multiple local charts have no registered overlap/correspondence checks",),
        )
    if global_section_witness_id.strip():
        return AtlasGluingReceipt(
            GluingStatus.GLOBAL_SECTION_WITNESSED,
            chart_ids,
            tuple(overlap.overlap_id for overlap in overlaps),
            ("local compatibility and a separate global-section witness are registered",),
            global_section_witness_id.strip(),
        )
    return AtlasGluingReceipt(
        GluingStatus.MATCHING_FAMILY_ONLY,
        chart_ids,
        tuple(overlap.overlap_id for overlap in overlaps),
        ("registered local/overlap compatibility does not by itself establish a global section",),
    )


@dataclass(frozen=True, slots=True)
class ProbeOutcome:
    probe_id: str
    candidate_id: str
    outcome_class_id: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.probe_id, self.candidate_id, self.outcome_class_id)):
            raise ValueError("probe outcomes require non-blank identities")


def observational_partition(outcomes: tuple[ProbeOutcome, ...]) -> tuple[tuple[str, ...], ...]:
    """Return exact finite observational-equivalence classes.

    ``outcome_class_id`` is evaluator-relative: two outputs should share it only
    when the bound evaluator treats them as observationally indistinguishable.
    Every candidate must have an outcome for every registered probe.
    """

    if not outcomes:
        raise ValueError("at least one probe outcome is required")
    probe_ids = tuple(sorted({item.probe_id for item in outcomes}))
    candidate_ids = tuple(sorted({item.candidate_id for item in outcomes}))
    lookup: dict[tuple[str, str], str] = {}
    for item in outcomes:
        key = (item.candidate_id, item.probe_id)
        if key in lookup:
            raise ValueError("duplicate candidate/probe outcome")
        lookup[key] = item.outcome_class_id
    expected = {(candidate, probe) for candidate in candidate_ids for probe in probe_ids}
    if set(lookup) != expected:
        raise ValueError("probe table must contain the full candidate-by-probe grid")

    signatures: dict[tuple[str, ...], list[str]] = {}
    for candidate in candidate_ids:
        signature = tuple(lookup[(candidate, probe)] for probe in probe_ids)
        signatures.setdefault(signature, []).append(candidate)
    blocks = [tuple(sorted(members)) for members in signatures.values()]
    return tuple(sorted(blocks, key=lambda block: (block[0], len(block), block)))


def is_strict_partition_refinement(
    new_partition: tuple[tuple[str, ...], ...],
    old_partition: tuple[tuple[str, ...], ...],
) -> bool:
    """Return True when ``new_partition`` strictly refines ``old_partition``."""

    def _universe(partition: tuple[tuple[str, ...], ...]) -> set[str]:
        flattened = [item for block in partition for item in block]
        if len(flattened) != len(set(flattened)):
            raise ValueError("partition blocks must be disjoint")
        return set(flattened)

    if _universe(new_partition) != _universe(old_partition):
        return False
    old_sets = tuple(set(block) for block in old_partition)
    new_sets = tuple(set(block) for block in new_partition)
    if new_sets == old_sets:
        return False
    return all(any(new_block <= old_block for old_block in old_sets) for new_block in new_sets)


class HorizonStatus(StrEnum):
    PROBE_REFINES_HORIZON = "PROBE_REFINES_HORIZON"
    NO_DISTINGUISHABILITY_GAIN = "NO_DISTINGUISHABILITY_GAIN"
    BROKEN_CANDIDATE_UNIVERSE = "BROKEN_CANDIDATE_UNIVERSE"
    OUTSIDE_CURRENT_ATLAS = "OUTSIDE_CURRENT_ATLAS"


@dataclass(frozen=True, slots=True)
class HorizonReceipt:
    status: HorizonStatus
    before_partition: tuple[tuple[str, ...], ...]
    after_partition: tuple[tuple[str, ...], ...]
    reason: str
    scientific_truth_authorized: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", HorizonStatus(self.status))
        if not self.reason.strip():
            raise ValueError("horizon receipts require a reason")
        if self.scientific_truth_authorized:
            raise ValueError("horizon receipts are non-authorizing")


def assess_probe_expansion(
    before: tuple[ProbeOutcome, ...],
    after: tuple[ProbeOutcome, ...],
) -> HorizonReceipt:
    before_partition = observational_partition(before)
    after_partition = observational_partition(after)
    before_universe = {item for block in before_partition for item in block}
    after_universe = {item for block in after_partition for item in block}
    if before_universe != after_universe:
        return HorizonReceipt(
            HorizonStatus.BROKEN_CANDIDATE_UNIVERSE,
            before_partition,
            after_partition,
            "candidate identity changed, so distinguishability refinement is not comparable",
        )
    if is_strict_partition_refinement(after_partition, before_partition):
        return HorizonReceipt(
            HorizonStatus.PROBE_REFINES_HORIZON,
            before_partition,
            after_partition,
            "the added probe strictly refines at least one observational-equivalence class",
        )
    return HorizonReceipt(
        HorizonStatus.NO_DISTINGUISHABILITY_GAIN,
        before_partition,
        after_partition,
        "the probe set does not strictly refine the current observational partition",
    )


class GlobalityLevel(StrEnum):
    LOCAL = "G0_LOCAL"
    COVER_COMPATIBLE = "G1_COVER_COMPATIBLE"
    TRANSPORT_STABLE = "G2_TRANSPORT_STABLE"
    ATLAS_ROBUST = "G3_ATLAS_ROBUST"
    FORMAL_UNIVERSE_THEOREM = "G4_FORMAL_UNIVERSE_THEOREM"


@dataclass(frozen=True, slots=True)
class GlobalityClaim:
    claim_id: str
    level: GlobalityLevel
    context_ids: tuple[str, ...]
    transport_relation_ids: tuple[str, ...] = ()
    hostile_chart_or_probe_ids: tuple[str, ...] = ()
    formal_universe_id: str = ""
    theorem_witness_id: str = ""

    def __post_init__(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("globality claims require an identity")
        object.__setattr__(self, "level", GlobalityLevel(self.level))
        object.__setattr__(self, "context_ids", _ids(self.context_ids, name="context_ids"))
        object.__setattr__(
            self,
            "transport_relation_ids",
            _ids(self.transport_relation_ids, name="transport_relation_ids", allow_empty=True),
        )
        object.__setattr__(
            self,
            "hostile_chart_or_probe_ids",
            _ids(self.hostile_chart_or_probe_ids, name="hostile_chart_or_probe_ids", allow_empty=True),
        )
        if self.level is GlobalityLevel.LOCAL and len(self.context_ids) != 1:
            raise ValueError("G0 local claims bind exactly one context")
        if self.level is GlobalityLevel.COVER_COMPATIBLE and len(self.context_ids) < 2:
            raise ValueError("G1 cover-compatible claims require multiple contexts")
        if self.level in {GlobalityLevel.TRANSPORT_STABLE, GlobalityLevel.ATLAS_ROBUST}:
            if len(self.context_ids) < 2 or not self.transport_relation_ids:
                raise ValueError("G2/G3 claims require multiple contexts and transport witnesses")
        if self.level is GlobalityLevel.ATLAS_ROBUST and not self.hostile_chart_or_probe_ids:
            raise ValueError("G3 atlas-robust claims require independent hostile chart/probe challenges")
        if self.level is GlobalityLevel.FORMAL_UNIVERSE_THEOREM:
            if not self.formal_universe_id.strip() or not self.theorem_witness_id.strip():
                raise ValueError("G4 requires an explicit formal universe and theorem witness")


def globality_levels() -> tuple[GlobalityLevel, ...]:
    """Return the only admissible globality levels.

    There is intentionally no empirical ``ABSOLUTE_GLOBAL`` member. A theorem
    may be universal only relative to its explicitly axiomatized formal universe.
    """

    return tuple(GlobalityLevel)
