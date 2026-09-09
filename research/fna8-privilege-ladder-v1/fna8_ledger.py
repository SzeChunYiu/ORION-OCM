"""FNA-8/D9 instruments: the 7-axis whole-lifetime cost ledger + the OCM recorder.

The 7 axes are exactly the #214 §4 FNA-8 enumeration:
  1. capability_source  — which mechanism supplied the decisive committed step
  2. model_usage        — calls / parse failures / tokens / wall
  3. state_growth       — persistent explicit state the rung had to add
  4. acquisition_work   — one-time build: index build, guard derivation,
                          authored-prior bytes (#214 §6 prior accounting)
  5. reasoning_work     — per-query execution + selection work (logical counters)
  6. verifier_work      — exact-certificate + commitment-gate work
  7. maintenance_and_revision — drift rebuild/recompute + revocation recompute,
                          including model re-asks where a rung needs them

Axes are reported per rung per arm and NEVER summed across incommensurable
units: logical work counters are summed among themselves; tokens and wall
seconds stay separate lines. The OCM recorder is the "OCM records" half of
Rung 1: every call, decision, check and commit is an append-only row; its size
is charged as Rung-1 state growth.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional


def _row_digest(row: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(row, sort_keys=True, default=str)
                          .encode("utf-8")).hexdigest()[:16]


class Recorder:
    """Append-only OCM-side event log (Rung 1's recording instrument)."""

    def __init__(self) -> None:
        self.rows: List[Dict[str, Any]] = []

    def add(self, kind: str, **payload: Any) -> Dict[str, Any]:
        row = {"seq": len(self.rows), "kind": kind}
        row.update(payload)
        row["digest"] = _row_digest(row)
        self.rows.append(row)
        return row

    def bytes(self) -> int:
        return sum(len(json.dumps(r, sort_keys=True, default=str)) for r in self.rows)

    def state_growth(self) -> Dict[str, int]:
        return {"event_rows": len(self.rows), "event_bytes": self.bytes()}


class CostLedger:
    """One ledger per (rung, arm). All counters are ints/floats, never None."""

    def __init__(self, rung: str, arm: str) -> None:
        self.rung = rung
        self.arm = arm
        self.capability_source: Dict[str, int] = {}
        self.model_usage = {"calls": 0, "calls_ok": 0, "parse_failures": 0,
                            "tokens": 0, "wall_s": 0.0}
        self.state_growth = {"event_rows": 0, "event_bytes": 0,
                             "index_entries": 0, "learned_bytes": 0}
        self.acquisition_work = {"index_build_work": 0, "guard_derivation_work": 0,
                                 "authored_prior_bytes": 0}
        self.reasoning_work = {"exec_work": 0, "select_work": 0, "queries": 0}
        self.verifier_work = {"check_work": 0, "commit_gate_work": 0}
        self.maintenance_and_revision = {
            "drift_index_rebuild_work": 0, "drift_recompute_work": 0,
            "drift_model_reasks": 0, "revision_recompute_work": 0,
            "revision_model_reasks": 0, "revoked_atoms": 0}
        self.capability = {"n": 0, "first_pass": 0, "delivered_correct": 0,
                           "fallbacks": 0}
        self.per_query: List[Dict[str, Any]] = []

    # -- accumulators ------------------------------------------------------------------

    def record_source(self, source: str) -> None:
        self.capability_source[source] = self.capability_source.get(source, 0) + 1

    def record_query(self, qid: str, first_pass: bool, delivered: bool, fallback: bool,
                     exec_work: int, select_work: int, check_work: int,
                     source: str, model_call: Optional[Dict] = None) -> None:
        self.capability["n"] += 1
        self.capability["first_pass"] += int(first_pass)
        self.capability["delivered_correct"] += int(delivered)
        self.capability["fallbacks"] += int(fallback)
        self.reasoning_work["exec_work"] += exec_work
        self.reasoning_work["select_work"] += select_work
        self.reasoning_work["queries"] += 1
        self.verifier_work["check_work"] += check_work
        self.record_source(source)
        row = {"qid": qid, "first_pass": first_pass, "delivered": delivered,
               "fallback": fallback, "exec_work": exec_work, "select_work": select_work,
               "check_work": check_work, "source": source}
        if model_call is not None:
            self.model_usage["calls"] += 1
            if model_call.get("ok"):
                self.model_usage["calls_ok"] += 1
            if model_call.get("parse_failure") or not model_call.get("ok"):
                self.model_usage["parse_failures"] += 1
            self.model_usage["tokens"] += int(model_call.get("tokens") or 0)
            self.model_usage["wall_s"] += float(model_call.get("wall_s") or 0.0)
            row["model"] = {"tokens": model_call.get("tokens"),
                            "parse_failure": model_call.get("parse_failure"),
                            "wall_s": model_call.get("wall_s"),
                            "returncode": model_call.get("returncode")}
        self.per_query.append(row)

    # -- composites --------------------------------------------------------------------

    def lifetime_logical_work(self) -> int:
        """Commensurable composite: acquisition + reasoning + verification +
        maintenance/revision logical counters. Tokens/wall are NEVER in here."""
        return (sum(self.acquisition_work.values())
                + self.reasoning_work["exec_work"] + self.reasoning_work["select_work"]
                + self.verifier_work["check_work"]
                + sum(self.maintenance_and_revision.values()))

    def delivered_correct_rate(self) -> Optional[float]:
        n = self.capability["n"]
        return None if n == 0 else self.capability["delivered_correct"] / n

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rung": self.rung, "arm": self.arm,
            "capability": dict(self.capability),
            "delivered_correct_rate": self.delivered_correct_rate(),
            "capability_source": dict(self.capability_source),
            "model_usage": dict(self.model_usage),
            "state_growth": dict(self.state_growth),
            "acquisition_work": dict(self.acquisition_work),
            "reasoning_work": dict(self.reasoning_work),
            "verifier_work": dict(self.verifier_work),
            "maintenance_and_revision": dict(self.maintenance_and_revision),
            "lifetime_logical_work": self.lifetime_logical_work(),
            "per_query": list(self.per_query),
        }
