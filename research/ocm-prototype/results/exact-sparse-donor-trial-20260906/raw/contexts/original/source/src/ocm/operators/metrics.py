"""Metric vocabulary vendored BYTE-for-byte (EXTRACT) from ORION.

Source: SzeChunYiu/ORION ``src/orion/mechanics/model.py`` at commit
adb97ecce7d8e1fe6effab456b98e653f401dae0, lines 39-97: the ``MetricKind``,
``MetricDirection``, ``MetricSpec`` and ``MetricObservation`` definitions with
their docstrings and validation bodies, in source order. Nothing else from that
module (``MechanicDimension``, ``HandoffField``, ``DimensionWaiver``,
``MechanicCell``) is vendored: those are ORION mechanics types. The import
header below is the module's original header (lines 1-4).

Provenance: docs/provenance/VENDORED_SOURCE_MANIFEST_V1.json.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MetricKind(str, Enum):
    QUALITY = "QUALITY"
    COVERAGE = "COVERAGE"
    COST = "COST"
    LATENCY = "LATENCY"
    RELIABILITY = "RELIABILITY"
    UNCERTAINTY = "UNCERTAINTY"
    RESOURCE = "RESOURCE"
    SAFETY = "SAFETY"
    DIAGNOSTIC = "DIAGNOSTIC"


class MetricDirection(str, Enum):
    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"
    TARGET = "TARGET"
    NON_COMPENSATORY_GATE = "NON_COMPENSATORY_GATE"
    OBSERVE_ONLY = "OBSERVE_ONLY"


@dataclass(frozen=True)
class MetricSpec:
    metric_id: str
    description: str
    kind: MetricKind
    direction: MetricDirection
    unit: str
    required_for_handoff: bool = False
    threshold_semantics: str = ""
    uncertainty_semantics: str = ""

    def __post_init__(self) -> None:
        if (
            not self.metric_id.strip()
            or not self.description.strip()
            or not self.unit.strip()
        ):
            raise ValueError("metric identity, description and unit are required")
        if (
            self.direction
            in {MetricDirection.TARGET, MetricDirection.NON_COMPENSATORY_GATE}
            and not self.threshold_semantics.strip()
        ):
            raise ValueError("target/gate metrics require threshold semantics")


@dataclass(frozen=True)
class MetricObservation:
    metric_id: str
    value: float | int | str
    unit: str
    evidence_ids: tuple[str, ...] = ()
    uncertainty: float | None = None

    def __post_init__(self) -> None:
        if not self.metric_id.strip() or not self.unit.strip():
            raise ValueError("metric observation identity and unit are required")
        if self.uncertainty is not None and self.uncertainty < 0:
            raise ValueError("metric uncertainty cannot be negative")
