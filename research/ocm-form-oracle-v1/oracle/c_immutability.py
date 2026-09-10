"""GATE_C_IMMUTABLE — the external constitution C is not a search dimension.

The directive: C is outside the system's control and must not be searchable.
If any legal configuration can alter C, that is a bug in the space and finding
one is itself a reportable result.

This is a HARD GATE.  It EXECUTES on every candidate and raises; it does not
log and continue.  `CImmutabilityViolation` carrying the drifted constant is
the reportable result if it ever fires.

What C is, concretely, in this stack
------------------------------------
morphology/schema.py declares the genome as
    G = (F_arch, U, T, O_basis, Pi_arch, L, R, K, theta)
with "C is NOT part of G" stated in the module docstring.  C is therefore
realised as the frozen constants the evaluator charges and gates against:

    COST_MODEL_V1, FIELD_MULT, TOPOLOGY_MULT, EXEC_MULT   (physics of charging)
    CAPABILITY_FLOOR_V1, REVOCATION_REQUIRED              (gate floors)
    UNIT_TYPES[*].charged_prior                           (priors charged)

Structural exclusion is necessary but NOT sufficient evidence: a genome could
still reach these through shared mutable module state (dicts are mutable and
lifetime.Sim takes `dict(COST_MODEL_V1)` by copy, but a mutation to the module
global would still leak).  So the gate takes a digest of the live constants
before compiling a candidate and re-checks it after evaluating, and separately
asserts no genome field name collides with a C-owned name.

The no-alarm case is asserted too: `selftest()` must show the gate PASSES on
legal configurations and FIRES on a deliberately tampered one.  A gate that has
only ever been seen not firing has not been validated.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Tuple


class CImmutabilityViolation(Exception):
    """C drifted during evaluation. Reportable result, not a warning."""


# Names owned by C.  A genome field may never carry one of these.
C_OWNED_NAMES: Tuple[str, ...] = (
    "COST_MODEL_V1", "FIELD_MULT", "TOPOLOGY_MULT", "EXEC_MULT",
    "CAPABILITY_FLOOR_V1", "REVOCATION_REQUIRED", "charged_prior",
)

GENOME_FIELDS: Tuple[str, ...] = (
    "F_arch", "U", "T", "O_basis", "Pi_arch", "L", "R", "K", "theta",
)


def _canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def constitution_snapshot() -> Dict[str, Any]:
    """Digest of every live C-owned constant."""
    from evaluation import lifetime as _lt
    from evaluation import invariants as _inv
    from morphology import schema as _sch
    parts = {
        "COST_MODEL_V1": _canon(_lt.COST_MODEL_V1),
        "FIELD_MULT": _canon(_lt.FIELD_MULT),
        "TOPOLOGY_MULT": _canon(_lt.TOPOLOGY_MULT),
        "EXEC_MULT": _canon(_lt.EXEC_MULT),
        "CAPABILITY_FLOOR_V1": _canon(_inv.CAPABILITY_FLOOR_V1),
        "REVOCATION_REQUIRED": _canon(_inv.REVOCATION_REQUIRED),
        "charged_priors": _canon({k: v.get("charged_prior")
                                  for k, v in sorted(_sch.UNIT_TYPES.items())}),
    }
    digests = {k: hashlib.sha256(v.encode()).hexdigest()[:16]
               for k, v in parts.items()}
    digests["_all"] = hashlib.sha256(_canon(digests).encode()).hexdigest()
    return digests


def genome_touches_c(genome: Any) -> List[str]:
    """Any way this genome names or carries a C-owned constant."""
    hits: List[str] = []
    for name in C_OWNED_NAMES:
        if hasattr(genome, name):
            hits.append("attr:%s" % name)
    theta = getattr(genome, "theta", {}) or {}
    if isinstance(theta, dict):
        for k in theta:
            if k in C_OWNED_NAMES:
                hits.append("theta:%s" % k)
    for f in GENOME_FIELDS:
        v = getattr(genome, f, None)
        if isinstance(v, str) and v in C_OWNED_NAMES:
            hits.append("field:%s" % f)
    return hits


def check_c_immutable(genome: Any, before: Dict[str, Any],
                      after: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the gate.  Raises on violation; returns the pass record."""
    touched = genome_touches_c(genome)
    if touched:
        raise CImmutabilityViolation(
            "GENOME_NAMES_C_OWNED_CONSTANT: %s" % ",".join(sorted(touched)))
    drift = [k for k in before if before[k] != after.get(k)]
    if drift:
        raise CImmutabilityViolation(
            "C_DRIFTED_DURING_EVALUATION: %s (before=%s after=%s)"
            % (",".join(sorted(drift)),
               {k: before[k] for k in drift},
               {k: after.get(k) for k in drift}))
    return {"GATE_C_IMMUTABLE": True, "c_digest": before["_all"]}


def selftest() -> Dict[str, Any]:
    """Validate the gate against real data BEFORE trusting any of its verdicts.

    Asserts BOTH directions:
      * no-alarm: a legal genome and an undisturbed constitution PASS;
      * alarm:    a tampered constitution and a C-naming genome FIRE.

    Exit codes are distinct: a selftest that cannot run returns
    status=CANNOT_CHECK, never status=OK.
    """
    out: Dict[str, Any] = {"schema": "GateCImmutableSelftestV1"}
    try:
        from morphology.gs_bound import gs_uniform_sample
        import random
        from evaluation import lifetime as _lt
    except Exception as e:  # noqa: BLE001
        return {**out, "status": "CANNOT_CHECK",
                "reason": "import_failed:%s" % repr(e)[:120]}

    rng = random.Random(20260910)
    g = gs_uniform_sample(rng)

    # --- no-alarm case
    snap = constitution_snapshot()
    try:
        rec = check_c_immutable(g, snap, constitution_snapshot())
        out["no_alarm_pass"] = bool(rec["GATE_C_IMMUTABLE"])
    except CImmutabilityViolation as e:
        return {**out, "status": "FAIL",
                "reason": "false_positive_on_legal_genome:%s" % str(e)[:160]}

    # --- alarm case 1: constitution tampered between snapshots
    before = constitution_snapshot()
    saved = _lt.COST_MODEL_V1.get("rule_fire_work")
    fired = False
    try:
        _lt.COST_MODEL_V1["rule_fire_work"] = (float(saved) + 1.0
                                               if saved is not None else 1.0)
        try:
            check_c_immutable(g, before, constitution_snapshot())
        except CImmutabilityViolation:
            fired = True
    finally:
        if saved is None:
            _lt.COST_MODEL_V1.pop("rule_fire_work", None)
        else:
            _lt.COST_MODEL_V1["rule_fire_work"] = saved
    out["alarm_on_tampered_constitution"] = fired

    # --- alarm case 2: genome carrying a C-owned name in theta
    class _Tampered:
        F_arch = getattr(g, "F_arch", None)
        U = getattr(g, "U", None)
        T = getattr(g, "T", None)
        O_basis = getattr(g, "O_basis", None)
        Pi_arch = getattr(g, "Pi_arch", None)
        L = getattr(g, "L", None)
        R = getattr(g, "R", None)
        K = getattr(g, "K", None)
        theta = {"CAPABILITY_FLOOR_V1": 0.0}

    fired2 = False
    snap2 = constitution_snapshot()
    try:
        check_c_immutable(_Tampered(), snap2, snap2)
    except CImmutabilityViolation:
        fired2 = True
    out["alarm_on_c_naming_genome"] = fired2

    # --- restoration check: the constitution must be exactly as we found it
    out["constitution_restored"] = (constitution_snapshot()["_all"]
                                    == snap["_all"])
    ok = (out.get("no_alarm_pass") and out.get("alarm_on_tampered_constitution")
          and out.get("alarm_on_c_naming_genome")
          and out.get("constitution_restored"))
    out["status"] = "OK" if ok else "FAIL"
    return out
