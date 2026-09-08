"""R0-D3: candidate/work instrumentation on the actual runtime path. No ML.

This wraps ``ocm.runtime.solve.compose_stage`` and ``check_stage`` for the
duration of a context manager and records, per solve, what the incumbent policy
actually did.  It adds no operator, changes no order, executes no backend, and
re-runs no candidate.  Everything it needs is already computed by the incumbent,
which is the finding as much as the method:

    ``compose_stage`` composes EVERY structurally applicable live candidate --
    there is no ``break`` -- and ``check_stage`` checks every composed candidate.
    ``decide`` then returns ``passed[0]``.

So the outcome of every admissible candidate is observed on every query, at the
incumbent's own expense, and the counterfactual question "what would the other
candidates have done" is answered by the incumbent trace itself rather than by
off-policy inference. That is identification route 3 of #152 -- an exact finite
reference -- and it costs nothing extra.

The per-candidate work is derived from the same arithmetic the runtime uses:
composing candidate ``i`` costs ``len(op.input_atoms)`` composition work and one
verification call, and checking it costs one more verification call. Those are
read off the operator specs, not re-measured, so the instrument cannot perturb
what it measures.
"""
from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from typing import Any, Iterator

from ocm.runtime import solve as S


@dataclass(frozen=True)
class CandidateRecord:
    operator_id: str
    input_atoms: int
    verdict: str
    #: work the runtime spends on this candidate, by the runtime's own arithmetic
    composition_work: int
    verification_calls: int


@dataclass
class SolveRecord:
    """One selection point on one real query."""

    source: str = ""
    catalogue_operators: int = 0
    selection_mode: str = ""
    structural_candidates: int = 0
    admissible_candidates: int = 0
    candidates: tuple[CandidateRecord, ...] = ()
    first_passing_index: int | None = None
    passing_count: int = 0
    chosen_operator_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "N_total": self.catalogue_operators,
            "selection_mode": self.selection_mode,
            "A_structural_count": self.structural_candidates,
            "A_admissible_count": self.admissible_candidates,
            "incumbent_order_and_choice": {
                "order": [c.operator_id for c in self.candidates],
                "verdicts": [c.verdict for c in self.candidates],
                "first_passing_index": self.first_passing_index,
                "chosen": self.chosen_operator_id,
            },
            "passing_candidate_count": self.passing_count,
            "incumbent_work_vector": self.incumbent_work(),
            "work_after_first_pass": self.work_after_first_pass(),
            # per-candidate work makes the BEFORE / CHOSEN / AFTER split exact
            # instead of leaving BEFORE+CHOSEN as one bound
            "per_candidate_work": [
                {"operator_id": c.operator_id,
                 "composition_work": c.composition_work,
                 "verification_calls": c.verification_calls}
                for c in self.candidates],
        }

    def incumbent_work(self) -> dict[str, int]:
        return {
            "composition_work": sum(c.composition_work for c in self.candidates),
            "verification_calls": sum(c.verification_calls for c in self.candidates),
        }

    def work_after_first_pass(self) -> dict[str, int]:
        """Work the incumbent spends on candidates strictly after its own answer.

        This is exactly what an early-exit policy would not spend. It is a
        property of the incumbent, computed from the incumbent's own trace, and
        it involves no alternative execution.
        """
        if self.first_passing_index is None:
            return {"composition_work": 0, "verification_calls": 0}
        tail = self.candidates[self.first_passing_index + 1:]
        return {
            "composition_work": sum(c.composition_work for c in tail),
            "verification_calls": sum(c.verification_calls for c in tail),
        }


class Capture:
    def __init__(self) -> None:
        self.records: list[SolveRecord] = []
        self._pending: SolveRecord | None = None
        self.source = ""

    def compose(self, ks, ops, g, revoked, **kw):
        result, candidates = self._compose(ks, ops, g, revoked, **kw)
        sel = result.payload.get("operator_selection", {}) if result.payload else {}
        rec = SolveRecord(
            source=self.source,
            catalogue_operators=int(sel.get("catalogue_operators", 0) or 0),
            selection_mode=str(sel.get("mode", "")),
            structural_candidates=int(sel.get("structural_candidates",
                                              sel.get("operators_considered", 0)) or 0),
            admissible_candidates=len(candidates),
        )
        rec.candidates = tuple(
            CandidateRecord(op.operator_id, len(op.input_atoms), "PENDING",
                            len(op.input_atoms), 1)
            for op, _out, _w in candidates)
        self._pending = rec
        return result, candidates

    def check(self, candidates, revoked, **kw):
        result, checked = self._check(candidates, revoked, **kw)
        rec = self._pending
        if rec is not None:
            verdicts = [v.value for _op, _o, _w, v in checked]
            rec.candidates = tuple(
                CandidateRecord(c.operator_id, c.input_atoms, verdicts[i],
                                c.composition_work, c.verification_calls + 1)
                if i < len(verdicts) else c
                for i, c in enumerate(rec.candidates))
            passing = [i for i, v in enumerate(verdicts) if v == "PASS"]
            rec.passing_count = len(passing)
            rec.first_passing_index = passing[0] if passing else None
            rec.chosen_operator_id = (
                rec.candidates[passing[0]].operator_id if passing else None)
            self.records.append(rec)
            self._pending = None
        return result, checked

    def flush_uncchecked(self) -> None:
        """A compose that never reached check is still a selection point."""
        if self._pending is not None:
            self.records.append(self._pending)
            self._pending = None


@contextlib.contextmanager
def capture(source: str = "") -> Iterator[Capture]:
    cap = Capture()
    cap.source = source
    cap._compose, cap._check = S.compose_stage, S.check_stage
    S.compose_stage, S.check_stage = cap.compose, cap.check
    try:
        yield cap
    finally:
        S.compose_stage, S.check_stage = cap._compose, cap._check
        cap.flush_uncchecked()
