"""Objective vector + prospectively frozen scalar development score (#221 sec 6).

Objectives (all MINIMIZED except capability which is maximized):
  capability        solved_fraction (maximize)
  acquisition_work  work spent admitting/persisting inputs
  reasoning_work    work spent deriving (expansions, rules, closures)
  verification_work work spent checking (consistency, exact checks)
  persistent_bytes  bytes persisted across the lifetime
  active_bytes      working-set proxy (k/N mass in use)
  maintenance_work  consolidation/maintenance passes
  revision_work     revocation/reopen work
  self_change_work  self-modification work (0 in this tranche)
  robustness        harmful_transfers + stale_answers (minimize)

Scalar (frozen BEFORE scored runs, reported alongside raw vectors, never the
scientific conclusion):
  dev_score = capability - 0.5*normalized_cost
  normalized_cost = (work_total/w_ref + persistent_bytes/b_ref)/2
  w_ref = 500.0, b_ref = 150.0   (frozen 2026-09-09, pre-score)
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

W_REF = 500.0
B_REF = 150.0

# T2 (MZ-D7, FREEZE_V1_AMEND_3) scalar references: MEDIANS of work_total and
# persistent_bytes over the feasible census at tier T2 (CENSUS_P00C truth,
# run 2026-09-09: feasible 28584/56160).  Frozen BEFORE any scored T2 run;
# identical values are recorded in FREEZE_V1_AMEND_3.json and asserted by
# tests.
W2_REF = 484.7
B2_REF = 152.8

OBJECTIVE_NAMES: Tuple[str, ...] = (
    "capability", "acquisition_work", "reasoning_work", "verification_work",
    "persistent_bytes", "active_bytes", "maintenance_work", "revision_work",
    "self_change_work", "robustness",
)

MAXIMIZE = frozenset({"capability"})


def objective_vector(ev: Dict[str, Any]) -> List[float]:
    return [
        ev.get("solved_fraction", 0.0),
        ev.get("acquisition_work", 0.0),
        ev.get("reasoning_work", 0.0),
        ev.get("verification_work", 0.0),
        ev.get("persistent_bytes", 0.0),
        ev.get("active_bytes_proxy", 0.0),
        ev.get("maintenance_work", 0.0),
        ev.get("revision_work", 0.0),
        ev.get("self_change_work", 0.0),
        float(ev.get("harmful_transfers", 0) + ev.get("stale_answers", 0)),
    ]


def dev_score(ev: Dict[str, Any]) -> float:
    """Frozen scalar.  T0: V1 battery formula (W_REF/B_REF).  T2: the same
    formula shape re-referenced to the T2 census medians (W2_REF/B2_REF,
    FREEZE_V1_AMEND_3) so the cost term is ~1 at the feasible median."""
    if ev.get("tier") == "T2":
        assert W2_REF is not None and B2_REF is not None, \
            "T2 scalar refs not frozen (FREEZE_V1_AMEND_3)"
        cost = (ev.get("work_total", 0.0) / W2_REF
                + ev.get("persistent_bytes", 0.0) / B2_REF) / 2.0
    else:
        cost = (ev.get("work_total", 0.0) / W_REF
                + ev.get("persistent_bytes", 0.0) / B_REF) / 2.0
    return round(ev.get("solved_fraction", 0.0) - 0.5 * cost, 6)


def dominates(a: List[float], b: List[float]) -> bool:
    """Pareto dominance over objective vectors (capability maximized, rest minimized)."""
    better = False
    for i, name in enumerate(OBJECTIVE_NAMES):
        if name in MAXIMIZE:
            if a[i] < b[i]:
                return False
            if a[i] > b[i]:
                better = True
        else:
            if a[i] > b[i]:
                return False
            if a[i] < b[i]:
                better = True
    return better


def pareto_front(items: List[Dict[str, Any]], vec_key: str = "objectives") -> List[int]:
    """Indices of non-dominated items (O(n^2); census-sized only)."""
    keep: List[int] = []
    for i, it in enumerate(items):
        dominated = False
        for j, jt in enumerate(items):
            if i != j and dominates(jt[vec_key], it[vec_key]):
                dominated = True
                break
        if not dominated:
            keep.append(i)
    return keep
