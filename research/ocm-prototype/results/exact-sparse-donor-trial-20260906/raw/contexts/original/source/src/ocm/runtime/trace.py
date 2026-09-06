"""Trace events and solve traces, ADAPTED from ORION ``src/orion/engine/trace.py``.

Source: SzeChunYiu/ORION commit adb97ecce7d8e1fe6effab456b98e653f401dae0.
What changed (and nothing else):

* the operator vocabulary is ``OCMOperator`` (from ``ocm.runtime.transition``);
* ``MECHANIC_ID_BY_OPERATOR`` maps each operator to its OCM mechanic id,
  ``kso.<operator>`` (lower-case operator name), instead of ORION's
  ``FRAME.v1`` … ``SATURATE_BOUNDED.v3``;
* ``MechanicReceipt`` comes from the byte-vendored ``ocm.operators.receipt``.

Both ``__post_init__`` cross-validations — receipt-against-transition on every
event, and state-hash/epoch chain continuity across a trace — are verbatim.

Provenance: docs/provenance/VENDORED_SOURCE_MANIFEST_V1.json.
"""

from __future__ import annotations

from dataclasses import dataclass

from ocm.operators.receipt import MechanicReceipt
from ocm.runtime.transition import OCMOperator, Transition

MECHANIC_ID_BY_OPERATOR = {
    operator: f"kso.{operator.value.lower()}" for operator in OCMOperator
}


@dataclass(frozen=True)
class TraceEvent:
    operator: OCMOperator
    epoch: int
    summary: str
    transition: Transition
    receipt: MechanicReceipt
    pre_state_hash: str
    post_state_hash: str

    def __post_init__(self) -> None:
        self.transition.validate()
        if self.transition.operator is not self.operator:
            raise ValueError("trace event transition/operator mismatch")
        if self.receipt.mechanic_id != MECHANIC_ID_BY_OPERATOR[self.operator]:
            raise ValueError("trace event receipt/mechanic mismatch")
        if self.epoch != self.transition.output_epoch:
            raise ValueError("trace event epoch/transition mismatch")
        if self.receipt.residual_ids != self.transition.residual_ids:
            raise ValueError("trace event receipt/transition residual mismatch")
        if self.receipt.evidence_ids != self.transition.evidence_ids:
            raise ValueError("trace event receipt/transition evidence mismatch")
        if (
            self.receipt.provenance_ids
            != self.transition.scientific_authority_certificate_ids
        ):
            raise ValueError("trace event receipt/transition provenance mismatch")
        handoff = dict(self.receipt.handoff_values)
        if handoff.get("changed_coordinates") != ",".join(
            self.transition.changed_coordinates
        ):
            raise ValueError("trace event receipt/transition handoff mismatch")
        for digest in (self.pre_state_hash, self.post_state_hash):
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError("trace event state bindings must be SHA-256 hashes")


@dataclass(frozen=True)
class SolveTrace:
    trace_id: str
    events: tuple[TraceEvent, ...]

    def __post_init__(self) -> None:
        if not self.trace_id.strip():
            raise ValueError("solve trace identity is required")
        receipt_ids = [event.receipt.receipt_id for event in self.events]
        if len(set(receipt_ids)) != len(receipt_ids):
            raise ValueError("solve trace receipt ids must be unique")
        for previous, current in zip(self.events, self.events[1:], strict=False):
            if previous.post_state_hash != current.pre_state_hash:
                raise ValueError("solve trace state-hash chain is discontinuous")
            if previous.transition.output_epoch != current.transition.input_epoch:
                raise ValueError("solve trace epoch chain is discontinuous")

    @property
    def operator_sequence(self) -> tuple[OCMOperator, ...]:
        return tuple(event.operator for event in self.events)

    def validate_endpoints(
        self, *, pre_state_hash: str, post_state_hash: str
    ) -> None:
        """Bind a nonempty internal chain to the actual runtime states."""

        if not self.events:
            raise ValueError("solve trace requires an endpoint-bound event")
        if self.events[0].pre_state_hash != pre_state_hash:
            raise ValueError("solve trace pre-state endpoint mismatch")
        if self.events[-1].post_state_hash != post_state_hash:
            raise ValueError("solve trace post-state endpoint mismatch")


__all__ = ["MECHANIC_ID_BY_OPERATOR", "SolveTrace", "TraceEvent"]
