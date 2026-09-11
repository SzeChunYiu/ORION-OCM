"""Exact H1a coding-K1 causal-fault localization metrics.

The evaluator supplies canonical repository-relative planted-fault files after the
run.  Solving agents never receive them.  The metric is frozen before protected
execution and does not use the reference/gold repair as a localization oracle.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import log2
from pathlib import PurePosixPath
from typing import Iterable, Sequence


@dataclass(frozen=True)
class LocalizationMetrics:
    event_rank: int
    localization_censored: bool
    observed_events: int
    event_budget: int
    fault_file_count: int
    fault_files_seen: int
    irrelevant_inspection_events_before_cover: int
    irrelevant_unique_files_before_cover: int
    repeated_inspection_events_before_cover: int

    def as_dict(self) -> dict:
        return asdict(self)


def canonical_repo_path(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("repository path must be a nonempty string")
    raw = value.replace("\\", "/")
    path = PurePosixPath(raw)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"path must be repository-relative without '..': {value!r}")
    parts = tuple(part for part in path.parts if part not in {"", "."})
    if not parts:
        raise ValueError("repository path must name a file")
    return str(PurePosixPath(*parts))


def _canonical_many(values: Iterable[str], *, unique: bool) -> list[str]:
    out = [canonical_repo_path(value) for value in values]
    if unique and len(set(out)) != len(out):
        raise ValueError("fault file list must not contain duplicates after canonicalization")
    return out


def localization_metrics(
    inspected_files: Sequence[str],
    fault_files: Sequence[str],
    *,
    event_budget: int | None = None,
) -> LocalizationMetrics:
    """Measure how early all planted causal-fault files were inspected.

    `event_rank` is 1-based and counts inspection events, including repeated file
    inspections.  If the full fault-file set is not covered, the frozen censor
    convention is `event_budget + 1`.

    `event_budget` must be at least the number of observed inspection events.  If
    omitted it equals the observed event count; a censored trace then receives
    `len(observed)+1`.
    """

    inspected = _canonical_many(inspected_files, unique=False)
    faults = _canonical_many(fault_files, unique=True)
    if not faults:
        raise ValueError("fault_files must contain at least one evaluator-frozen causal file")

    if event_budget is None:
        event_budget = len(inspected)
    if not isinstance(event_budget, int) or event_budget < 0:
        raise ValueError("event_budget must be a nonnegative integer")
    if event_budget < len(inspected):
        raise ValueError("event_budget cannot be smaller than observed inspection events")

    fault_set = set(faults)
    seen_faults: set[str] = set()
    seen_all: set[str] = set()
    irrelevant_events = 0
    irrelevant_unique: set[str] = set()
    repeated_events = 0
    cover_rank: int | None = None

    for idx, path in enumerate(inspected, start=1):
        if path in seen_all:
            repeated_events += 1
        seen_all.add(path)

        if path in fault_set:
            seen_faults.add(path)
        else:
            irrelevant_events += 1
            irrelevant_unique.add(path)

        if seen_faults == fault_set:
            cover_rank = idx
            break

    if cover_rank is None:
        rank = event_budget + 1
        censored = True
    else:
        rank = cover_rank
        censored = False

    return LocalizationMetrics(
        event_rank=rank,
        localization_censored=censored,
        observed_events=len(inspected),
        event_budget=event_budget,
        fault_file_count=len(fault_set),
        fault_files_seen=len(seen_faults),
        irrelevant_inspection_events_before_cover=irrelevant_events,
        irrelevant_unique_files_before_cover=len(irrelevant_unique),
        repeated_inspection_events_before_cover=repeated_events,
    )


def localization_rank_shift(reset_rank: int, treatment_rank: int) -> float:
    """Frozen H1a shift: log2((L_reset + 1)/(L_treatment + 1))."""

    if not isinstance(reset_rank, int) or not isinstance(treatment_rank, int):
        raise ValueError("localization ranks must be integers")
    if reset_rank < 1 or treatment_rank < 1:
        raise ValueError("localization ranks must be >= 1")
    return log2((reset_rank + 1) / (treatment_rank + 1))


def paired_localization_rows(
    reset_rows: Sequence[LocalizationMetrics],
    treatment_rows: Sequence[LocalizationMetrics],
) -> list[dict]:
    if len(reset_rows) != len(treatment_rows):
        raise ValueError("reset and treatment rows must have equal length")
    rows = []
    for idx, (reset, treatment) in enumerate(zip(reset_rows, treatment_rows)):
        rows.append(
            {
                "pair_index": idx,
                "reset_event_rank": reset.event_rank,
                "treatment_event_rank": treatment.event_rank,
                "reset_censored": reset.localization_censored,
                "treatment_censored": treatment.localization_censored,
                "delta_I_loc_bits": localization_rank_shift(
                    reset.event_rank, treatment.event_rank
                ),
            }
        )
    return rows
