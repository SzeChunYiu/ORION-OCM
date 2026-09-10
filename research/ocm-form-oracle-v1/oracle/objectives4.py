"""Form Oracle objective vector (FO-V1) — k-objective Pareto.

The frozen OBJECTIVE_REGISTRY_V1 names ten objectives and
evaluation/objectives.py:dominates() is hardwired to that tuple.  The Form
Oracle needs a FOUR-objective front whose second component is an aggregate
that does not exist upstream (full lifetime burden including rejected-
candidate work) and whose fourth does not exist at all (evolvability).
Reuse is therefore impossible for the dominance relation itself; this module
is the recorded build-over-reuse residual.  Nothing else about the frozen
registry is changed and dev_score is never used as a scientific conclusion.

SEARCH-TIME vs REPORT-TIME
--------------------------
T3 generalization is HELD OUT.  If it entered the admission rule it would no
longer be held out.  So:

  SEARCH_OBJECTIVES = (capability, burden, evolvability)   3-vector, drives admission
  REPORT_OBJECTIVES = (capability, burden, t3_gen, evolvability)  4-vector, post-hoc only

Both are frozen here before any scored run.
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

# ---------------------------------------------------------------- frozen names

SEARCH_OBJECTIVES: Tuple[str, ...] = ("capability", "burden", "evolvability")
SEARCH_MAXIMIZE: Tuple[bool, ...] = (True, False, True)

REPORT_OBJECTIVES: Tuple[str, ...] = ("capability", "burden", "t3_gen",
                                      "evolvability")
REPORT_MAXIMIZE: Tuple[bool, ...] = (True, False, True, True)

# Sentinel used when an objective could not be computed.  It is NEVER coerced
# to a number: a record carrying it is excluded from the front and counted in
# a distinct CANNOT_CHECK bucket (see partition_checkable).
CANNOT_CHECK = "CANNOT_CHECK"


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def dominates_k(a: Sequence[float], b: Sequence[float],
                maximize: Sequence[bool]) -> bool:
    """Pareto dominance for an arbitrary objective vector.

    a dominates b iff a is no worse on every objective and strictly better on
    at least one, with per-objective sense given by `maximize`.
    """
    if len(a) != len(b) or len(a) != len(maximize):
        raise ValueError("objective/mask length mismatch: %d/%d/%d"
                         % (len(a), len(b), len(maximize)))
    better = False
    for ai, bi, mx in zip(a, b, maximize):
        if not (_is_number(ai) and _is_number(bi)):
            raise ValueError("non-numeric objective in dominance test")
        if mx:
            if ai < bi:
                return False
            if ai > bi:
                better = True
        else:
            if ai > bi:
                return False
            if ai < bi:
                better = True
    return better


def partition_checkable(items: List[Dict[str, Any]], vec_key: str,
                        n_obj: int) -> Tuple[List[int], List[int]]:
    """Split indices into (checkable, cannot_check).

    'could not check' is kept structurally distinct from 'checked and fine':
    a record whose vector holds a non-numeric entry never enters the front and
    is reported under its own count.
    """
    ok: List[int] = []
    bad: List[int] = []
    for i, it in enumerate(items):
        v = it.get(vec_key)
        if (isinstance(v, (list, tuple)) and len(v) == n_obj
                and all(_is_number(x) for x in v)):
            ok.append(i)
        else:
            bad.append(i)
    return ok, bad


def pareto_front_k(items: List[Dict[str, Any]], vec_key: str,
                   maximize: Sequence[bool]) -> Dict[str, Any]:
    """Indices of the non-dominated set over `vec_key`.

    Returns both the front and the cannot-check bucket so a caller can never
    silently read an incomplete front as a complete one.
    """
    ok, bad = partition_checkable(items, vec_key, len(maximize))
    front: List[int] = []
    for i in ok:
        vi = items[i][vec_key]
        dominated = False
        for j in ok:
            if i == j:
                continue
            if dominates_k(items[j][vec_key], vi, maximize):
                dominated = True
                break
        if not dominated:
            front.append(i)
    return {
        "front_indices": front,
        "n_front": len(front),
        "n_checked": len(ok),
        "n_cannot_check": len(bad),
        "cannot_check_indices": bad,
        "objectives": list(maximize),
    }


def search_vector(rec: Dict[str, Any]) -> Any:
    """(capability, burden, evolvability) or CANNOT_CHECK."""
    vals = [rec.get("capability"), rec.get("burden"), rec.get("evolvability")]
    if all(_is_number(v) for v in vals):
        return [float(v) for v in vals]
    return CANNOT_CHECK


def report_vector(rec: Dict[str, Any]) -> Any:
    """(capability, burden, t3_gen, evolvability) or CANNOT_CHECK."""
    vals = [rec.get("capability"), rec.get("burden"), rec.get("t3_gen"),
            rec.get("evolvability")]
    if all(_is_number(v) for v in vals):
        return [float(v) for v in vals]
    return CANNOT_CHECK
