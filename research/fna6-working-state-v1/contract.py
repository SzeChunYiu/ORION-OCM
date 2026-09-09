"""FNA-6 working-state contract: counters, exact checker, common arm surface.

Every arm implements the same lifecycle on the same frozen stream:

    open(field, seeds) -> build
    serve(ob, seed, target, ks_now, revoked_now) -> (answer, consulted_atom_ids)
    apply_admission / apply_revocation / apply_drift(event, ks_after, revoked_after)
    resident(ob) -> set of atom/object ids currently held for that obligation
    persistent_state() -> JSON-serialisable working-state footprint (field excluded)
    close()

The exact checker wraps every serve: answer != oracle truth is an event, classified by
what changed since the obligation last served (stale revocation / merge failure) and by
provenance (consulted objects resident in the other obligation's working set -> the event
is also an interference event). Nothing is self-reported: classification uses the oracle
verdict and the arm's own recorded consulted/resident sets.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple

PHASES = ("build", "serve", "merge", "sweep", "drift")


class Counters:
    """Whole-lifecycle charged cost + working-set occupancy + locality touched sets."""

    def __init__(self) -> None:
        self.ops = {p: 0 for p in PHASES}
        self.detail: Dict[str, int] = {}
        self.resident: Dict[str, Set[str]] = {"__all__": set()}
        self.working_set_peak = 0
        self.touched: List[Tuple[str, Set[str]]] = []  # (event_key, atom ids touched)

    def op(self, phase: str, n: int = 1, kind: str = None) -> None:
        self.ops[phase] += n
        if kind:
            self.detail[kind] = self.detail.get(kind, 0) + n

    def resident_sync(self, ob: int, ids: Iterable[str]) -> None:
        """Declare an obligation's current working-set membership (bookkeeping only —
        never charged as ops; the arm's own state mutation is what costs). The process
        working set is the union over obligations; peak occupancy is its high-water."""
        per = self.resident.setdefault(str(ob), set())
        per.clear()
        per.update(ids)
        allset: Set[str] = set()
        for k, s in self.resident.items():
            if k != "__all__":
                allset |= s
        self.resident["__all__"] = allset
        if len(allset) > self.working_set_peak:
            self.working_set_peak = len(allset)

    def touch(self, event_key: str, ids: Iterable[str]) -> None:
        self.touched.append((event_key, set(ids)))

    @property
    def total_ops(self) -> int:
        return sum(self.ops.values())


class ServeVerdict:
    __slots__ = ("serve_idx", "ob", "target", "answer", "truth", "exact",
                 "stale_revocation", "merge_failure", "interference", "consulted_other")

    def __init__(self, serve_idx: int, ob: int, target: str, answer: bool, truth: bool,
                 stale_revocation: bool, merge_failure: bool, interference: bool,
                 consulted_other: bool) -> None:
        self.serve_idx = serve_idx
        self.ob = ob
        self.target = target
        self.answer = answer
        self.truth = truth
        self.exact = answer == truth
        self.stale_revocation = stale_revocation
        self.merge_failure = merge_failure
        self.interference = interference
        self.consulted_other = consulted_other

    def as_dict(self) -> dict:
        return {"idx": self.serve_idx, "ob": self.ob, "target": self.target,
                "answer": self.answer, "truth": self.truth, "exact": self.exact,
                "stale_revocation": self.stale_revocation, "merge_failure": self.merge_failure,
                "interference": self.interference, "consulted_other": self.consulted_other}


class ExactChecker:
    """Classifies wrong answers using stream context, never arm self-reports."""

    def __init__(self) -> None:
        self.since_last: Dict[int, List[str]] = {0: [], 1: []}

    def note_update(self, kind: str) -> None:
        for ob in (0, 1):
            self.since_last[ob].append(kind)

    def check(self, serve_idx: int, ob: int, target: str, answer: bool, truth: bool,
              consulted: Iterable[str], other_resident: Iterable[str]) -> ServeVerdict:
        history = self.since_last[ob]
        self.since_last[ob] = []
        wrong = answer != truth
        overlap = bool(set(consulted) & set(other_resident))
        return ServeVerdict(
            serve_idx, ob, target, answer, truth,
            stale_revocation=bool(wrong and "revocation" in history),
            merge_failure=bool(wrong and ("admission" in history or "drift" in history)),
            interference=bool(wrong and overlap),
            consulted_other=overlap,
        )


class ArmResult:
    def __init__(self, code: str) -> None:
        self.code = code
        self.counters = Counters()
        self.verdicts: List[ServeVerdict] = []

    @property
    def decisions_exact(self) -> int:
        return sum(1 for v in self.verdicts if v.exact)

    def summary(self) -> dict:
        n = len(self.verdicts)
        return {
            "arm": self.code,
            "decisions_exact": self.decisions_exact,
            "decisions_total": n,
            "interference_events": sum(1 for v in self.verdicts if v.interference),
            "stale_revocation_decisions": sum(1 for v in self.verdicts if v.stale_revocation),
            "merge_failures": sum(1 for v in self.verdicts if v.merge_failure),
            "wrong_total": sum(1 for v in self.verdicts if not v.exact),
            "ops": dict(self.counters.ops),
            "total_ops": self.counters.total_ops,
            "ops_detail": dict(sorted(self.counters.detail.items())),
            "working_set_peak": self.counters.working_set_peak,
        }

    def sufficient(self) -> bool:
        return (self.decisions_exact == len(self.verdicts)
                and not any(v.interference or v.stale_revocation or v.merge_failure
                            for v in self.verdicts))
