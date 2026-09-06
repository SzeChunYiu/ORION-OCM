"""Transition validation, ADAPTED from ORION ``src/orion/engine/cycle.py``.

Source: SzeChunYiu/ORION commit adb97ecce7d8e1fe6effab456b98e653f401dae0.
What changed (and nothing else):

* ``CycleOperator`` (FRAME, SEARCH, ABSORB, ...) is replaced by ``OCMOperator``,
  the M2 operator vocabulary. The non-authority set is *every* operator except
  ``COMMIT_ACTION`` — the one operator that crosses the constitution boundary —
  where ORION exempted only ``ABSORB``.
* ``Residual``/``ResidualKind``/``Responsibility`` are imported from the
  byte-vendored ``ocm.runtime.residuals``.
* The product name in one error message ("ORION transitions" → "OCM
  transitions"). The ``Transition.validate`` body, ``revision_allowed`` and
  ``local_reframe_allowed`` are otherwise verbatim, including the rule that an
  authority increase requires certificate-producing evidence.

Provenance: docs/provenance/VENDORED_SOURCE_MANIFEST_V1.json.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ocm.runtime.residuals import Residual, ResidualKind, Responsibility


class OCMOperator(str, Enum):
    ADMIT = "ADMIT"
    QUERY = "QUERY"
    NAVIGATE = "NAVIGATE"
    EXTRACT = "EXTRACT"
    COMPOSE = "COMPOSE"
    CHECK = "CHECK"
    LEARN = "LEARN"
    REVOKE = "REVOKE"
    REINSTATE = "REINSTATE"
    REOPEN = "REOPEN"
    PROPOSE_JUMP = "PROPOSE_JUMP"
    COMMIT_ACTION = "COMMIT_ACTION"
    PERSIST = "PERSIST"


# Every operator except COMMIT_ACTION is non-authority: no epistemic operator
# can mint authority on its own, and COMMIT_ACTION can only do so with
# certificate-producing evidence (checked below).
_NON_AUTHORITY_OPERATORS = frozenset(
    operator for operator in OCMOperator if operator is not OCMOperator.COMMIT_ACTION
)

# Responsibilities whose local repair is genuinely a formulation/search-space
# revision. METHOD/EVALUATOR changes are separately protected by Self-ORION;
# EVIDENCE and EXECUTION call for acquisition/retry/implementation repair rather
# than rewriting the research formulation.
_LOCAL_REFRAME_RESPONSIBILITIES = frozenset(
    {
        Responsibility.QUESTION,
        Responsibility.REPRESENTATION,
        Responsibility.SEARCH,
        Responsibility.ROUTING,
        Responsibility.DECOMPOSITION,
        Responsibility.INTERFACE,
        Responsibility.MEASUREMENT,
    }
)


@dataclass(frozen=True)
class Transition:
    operator: OCMOperator
    input_epoch: int
    output_epoch: int
    evidence_ids: tuple[str, ...] = ()
    residual_ids: tuple[str, ...] = ()
    authority_increase: bool = False
    scientific_authority_certificate_ids: tuple[str, ...] = ()
    changed_coordinates: tuple[str, ...] = ()

    def validate(self) -> None:
        if self.output_epoch < self.input_epoch:
            raise ValueError("OCM transitions cannot move backward in epoch")
        if self.operator in _NON_AUTHORITY_OPERATORS and self.authority_increase:
            raise ValueError(f"{self.operator.value} cannot directly increase scientific authority")
        if self.authority_increase and not self.scientific_authority_certificate_ids:
            raise ValueError("authority increase requires certificate-producing evidence")


def revision_allowed(responsibilities: tuple[Responsibility, ...]) -> bool:
    """High-impact revision is blocked while responsibility remains ambiguous."""

    return len(set(responsibilities)) == 1 and bool(responsibilities)


def local_reframe_allowed(responsibility: Responsibility) -> bool:
    """Whether the diagnosed responsibility is licensed for local REFRAME.

    This is deliberately narrower than `revision_allowed`: a singular diagnosis
    can still point to an acquisition/execution problem whose correct next action
    is not a formulation rewrite.
    """

    return responsibility in _LOCAL_REFRAME_RESPONSIBILITIES


__all__ = [
    "OCMOperator",
    "Residual",
    "ResidualKind",
    "Responsibility",
    "Transition",
    "local_reframe_allowed",
    "revision_allowed",
]
