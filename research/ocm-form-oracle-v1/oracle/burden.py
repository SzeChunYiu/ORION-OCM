"""Full lifetime burden (FO-V1 objective 2).

Contract (frozen before any scored run):

    B_own(x)  = B_acquire + B_exec + B_verify + B_revise + B_self + B_maintain
                + LAMBDA_BYTES * persistent_bytes

    B_full(x, arm) = B_own(x) + B_reject_share(arm)

Component map onto the frozen evaluator's charged buckets:

    B_acquire   <- acquisition_work    (index BUILD cost is charged here by
                                        lifetime.Sim._charge(..., "acquisition");
                                        index_built is reported separately so
                                        the inclusion is auditable, not assumed)
    B_exec      <- reasoning_work
    B_verify    <- verification_work
    B_revise    <- revision_work
    B_self      <- self_change_work
    B_maintain  <- maintenance_work

LAMBDA_BYTES converts persisted bytes into work-equivalent units.  It is NOT a
new free constant: it is the ratio of the two ALREADY-FROZEN T2 census medians
recorded in FREEZE_V1_AMEND_3 and in evaluation/objectives.py (W2_REF/B2_REF),
so one median byte costs exactly one median work unit.  Computed, never typed.

B_reject_share is the honesty term the directive requires.  A burden number
that omits work spent on rejected candidates is a defect, so every candidate an
arm evaluated at every rung -- feasible, infeasible, gate-failed and crashed --
contributes its charged work to the arm total, which is then amortised over the
archive the arm actually retained:

    B_reject_share(arm) = charged_work_all_candidates(arm) / max(1, |archive|)

A crashed candidate has no charged vector; it is charged CRASH_WORK_FLOOR = the
arm's running mean charged work per attempted candidate at that rung, so a
crash cannot be cheaper than an evaluation.  If no candidate has completed at
that rung yet, the crash is deferred and settled at arm end.

Memoisation note: evaluate_genome caches on (phenotype_digest, tier).  A cache
hit saves WALL CLOCK, not burden -- the charged work of a phenotype is a
deterministic modelled quantity, so every evaluation ATTEMPT is charged whether
or not the cache served it.  Wall clock is reported separately and never enters
an objective.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

WORK_BUCKETS = ("acquisition_work", "reasoning_work", "verification_work",
                "revision_work", "self_change_work", "maintenance_work")

BURDEN_COMPONENT_NAMES = ("B_acquire", "B_exec", "B_verify", "B_revise",
                          "B_self", "B_maintain", "B_bytes")


def lambda_bytes() -> float:
    """Work-units per persisted byte, derived from the frozen T2 medians."""
    from evaluation.objectives import W2_REF, B2_REF
    if not W2_REF or not B2_REF:
        raise RuntimeError("CANNOT_CHECK_T2_REFS_NOT_FROZEN")
    return float(W2_REF) / float(B2_REF)


def work_charged(ev: Dict[str, Any]) -> float:
    """Total charged WORK for one evaluation, byte rent excluded.

    `work_total` is authoritative when present: it is the evaluator's own
    running total, and on T2 it equals the six-bucket sum exactly (asserted by
    assert_work_identity below on real data, not assumed). The per-bucket
    fields exist on the T0/T2 batteries but NOT on the T3/future battery, which
    reports only work_total -- so a bucket-sum-only implementation silently
    returns 0.0 there. That failure mode is why this function exists and why
    absence of both raises instead of returning zero.
    """
    if "work_total" in ev:
        return float(ev["work_total"])
    if any(b in ev for b in WORK_BUCKETS):
        return float(sum(float(ev.get(b, 0.0)) for b in WORK_BUCKETS))
    raise RuntimeError("CANNOT_CHECK_NO_WORK_ACCOUNTING")


def assert_work_identity(ev: Dict[str, Any], tol: float = 1e-6) -> Dict[str, Any]:
    """Executed check that work_total == sum(buckets) where both exist."""
    if "work_total" not in ev or not any(b in ev for b in WORK_BUCKETS):
        return {"status": "CANNOT_CHECK_PARTIAL_ACCOUNTING"}
    bs = float(sum(float(ev.get(b, 0.0)) for b in WORK_BUCKETS))
    wt = float(ev["work_total"])
    if abs(bs - wt) > tol:
        raise RuntimeError("WORK_ACCOUNTING_DISAGREES: buckets=%r work_total=%r"
                           % (bs, wt))
    return {"status": "OK", "work_total": wt, "bucket_sum": bs}


def burden_components(ev: Dict[str, Any]) -> Dict[str, float]:
    """Charged components of one organism's lifetime.

    On batteries that expose per-bucket fields the six work components are
    itemised. On batteries that expose only work_total (T3/future) the buckets
    are absent and the whole charged work appears under B_work_unattributed,
    so the total is never understated and the missing attribution is visible
    rather than silently folded into B_exec.
    """
    lam = lambda_bytes()
    out: Dict[str, float] = {"B_bytes": lam * float(ev.get("persistent_bytes", 0.0))}
    if any(b in ev for b in WORK_BUCKETS):
        out.update({
            "B_acquire": float(ev.get("acquisition_work", 0.0)),
            "B_exec": float(ev.get("reasoning_work", 0.0)),
            "B_verify": float(ev.get("verification_work", 0.0)),
            "B_revise": float(ev.get("revision_work", 0.0)),
            "B_self": float(ev.get("self_change_work", 0.0)),
            "B_maintain": float(ev.get("maintenance_work", 0.0)),
        })
    else:
        out["B_work_unattributed"] = work_charged(ev)
    return out


def b_own(ev: Dict[str, Any]) -> float:
    """Full own-lifetime burden: all charged work plus the byte rent."""
    lam = lambda_bytes()
    return round(work_charged(ev)
                 + lam * float(ev.get("persistent_bytes", 0.0)), 6)


def b_work_only(ev: Dict[str, Any]) -> float:
    """Charged work without the persisted-byte rent.

    Used for B_future_cognition. Including the byte term there would make
    "development makes future cognition cheaper" structurally impossible: more
    development means more carried bytes means a larger number, whatever
    happens to the work actually done. The byte term is already charged in
    objective 2 and is reported beside this figure, so the split hides nothing.
    """
    return round(work_charged(ev), 6)


def charged_work(ev: Dict[str, Any]) -> float:
    """Charged work of one evaluation attempt (no byte term).

    Prefers the evaluator's own work_total when present so this function can
    never disagree with the frozen accounting; falls back to the bucket sum.
    """
    if "work_total" in ev:
        return float(ev["work_total"])
    return float(sum(float(ev.get(b, 0.0)) for b in WORK_BUCKETS))


class RejectLedger:
    """Charges every evaluation attempt an arm makes, at every rung.

    Feasible, infeasible, gate-failed and crashed candidates all land here.
    Nothing is netted off: the ledger only ever grows.
    """

    def __init__(self) -> None:
        self.n_attempts = 0
        self.n_crashes = 0
        self.n_retained = 0
        self.total_charged = 0.0
        self.per_rung: Dict[str, Dict[str, float]] = {}
        self._pending_crashes: List[str] = []

    def _rung(self, tier: str) -> Dict[str, float]:
        return self.per_rung.setdefault(
            tier, {"n": 0.0, "work": 0.0, "crashes": 0.0})

    def charge_eval(self, tier: str, ev: Optional[Dict[str, Any]]) -> float:
        w = charged_work(ev) if ev else 0.0
        r = self._rung(tier)
        r["n"] += 1.0
        r["work"] += w
        self.n_attempts += 1
        self.total_charged += w
        return w

    def charge_crash(self, tier: str) -> None:
        """A crash cannot be cheaper than an evaluation at the same rung."""
        r = self._rung(tier)
        r["crashes"] += 1.0
        self.n_crashes += 1
        self.n_attempts += 1
        if r["n"] > 0:
            floor = r["work"] / r["n"]
            r["work"] += floor
            self.total_charged += floor
        else:
            self._pending_crashes.append(tier)

    def settle(self) -> Dict[str, Any]:
        """Settle crashes that preceded any completed evaluation at their rung.

        Returns a distinct status so an unsettleable crash is never silently
        read as zero-cost.
        """
        unsettled = []
        for tier in self._pending_crashes:
            r = self._rung(tier)
            if r["n"] > 0:
                floor = r["work"] / r["n"]
                r["work"] += floor
                self.total_charged += floor
            else:
                unsettled.append(tier)
        self._pending_crashes = []
        return {
            "settled": True,
            "unsettled_crash_rungs": unsettled,
            "status": ("CANNOT_CHECK_CRASH_FLOOR_NO_BASELINE"
                       if unsettled else "OK"),
        }

    # Rungs that are SEARCH work (they produced the archive) versus rungs that
    # are MEASUREMENT work (they scored an archive member after the fact).
    # Only search work is amortised into the burden objective: charging the
    # cost of measuring evolvability into burden would entangle objective 2
    # with objective 4 through the ledger, so measurement is reported apart.
    SEARCH_RUNGS = ("T0", "T1", "T2")

    def search_charged(self) -> float:
        return sum(v["work"] for k, v in self.per_rung.items()
                   if k in self.SEARCH_RUNGS)

    def measurement_charged(self) -> float:
        return sum(v["work"] for k, v in self.per_rung.items()
                   if k not in self.SEARCH_RUNGS)

    def reject_share(self, n_retained: Optional[int] = None) -> float:
        """Search work spent per retained archive member.

        Every candidate the arm evaluated at a search rung is in the numerator
        -- feasible, infeasible, gate-failed and crashed -- so an arm that
        wasted a thousand rejects to keep one elite pays for all thousand.
        """
        n = self.n_retained if n_retained is None else n_retained
        return round(self.search_charged() / max(1, n), 6)

    def report(self) -> Dict[str, Any]:
        return {
            "n_attempts": self.n_attempts,
            "n_crashes": self.n_crashes,
            "n_retained": self.n_retained,
            "total_charged_work": round(self.total_charged, 6),
            "search_charged_work": round(self.search_charged(), 6),
            "measurement_charged_work": round(self.measurement_charged(), 6),
            "search_rungs": list(self.SEARCH_RUNGS),
            "reject_share_per_retained": self.reject_share(),
            "per_rung": {k: {kk: round(vv, 6) for kk, vv in v.items()}
                         for k, v in sorted(self.per_rung.items())},
        }


def b_full(ev: Dict[str, Any], reject_share: float) -> float:
    return round(b_own(ev) + float(reject_share), 6)
