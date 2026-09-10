"""Behavioural dedup signature (FO-V1).

Dedup is on BEHAVIOUR, not genotype and not phenotype structure.  Two forms
that solve the identical item set with the identical expansion and reuse
profile are one behaviour however differently they are built.

Signature = sha256 over canonical JSON of
  1. the per-family (solved, total) profile over the frozen T2 families
     -- this is the solved-item profile, the primary behavioural content;
  2. the two frozen behavioural descriptor dims (B_behavior_2d:
     expansions_per_solved, method_reuse_fraction) quantised to QUANT;
  3. the boolean hard-gate vector (a form that fails a different gate is a
     different behaviour even at equal solve profile).

Structural fields (unit types, topology, field family) are deliberately
EXCLUDED: including them would make this genotype dedup wearing a behavioural
name, which is the exact failure the directive names.

Cost is instrumented: `SigCost` counts signature computations and accumulates
wall-clock, so the dedup lever's price is reported separately from its yield
(GS-R2 showed the distinct-yield lever costs roughly double cpu-seconds per
seed: GSA6_DP 190,527 vs GSA2_hetero 354,046 morphologies/cpu-hour).
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple

QUANT = 1000  # quantisation denominator for the two continuous dims
SIG_SCHEMA = "FOBehaviourSigV1"


def _q(x: Any) -> int:
    try:
        return int(round(float(x) * QUANT))
    except (TypeError, ValueError):
        return -(2 ** 62)  # non-numeric marks its own bucket, never 0


def behaviour_payload(ev: Dict[str, Any], gates: Dict[str, Any],
                      descriptors: Optional[Tuple[float, ...]] = None
                      ) -> Dict[str, Any]:
    per_family = ev.get("per_family", {}) or {}
    profile = [[k, int(v.get("solved", 0)), int(v.get("total", 0))]
               for k, v in sorted(per_family.items())]
    if descriptors is None:
        # Frozen B_behavior_2d dims, read from the evaluator's own summary
        # fields (lifetime._summarize): expansions/solved and the already
        # computed method_reuse_fraction.  -1.0 marks "undefined", which is a
        # distinct bucket from 0.0 ("defined and zero").
        solved = float(ev.get("solved", 0) or 0)
        exp_per_solved = (float(ev.get("expansions", 0.0)) / solved
                          if solved > 0 else -1.0)
        reuse = float(ev.get("method_reuse_fraction", -1.0))
        descriptors = (exp_per_solved, reuse)
    return {
        "schema": SIG_SCHEMA,
        "profile": profile,
        "dims": [_q(d) for d in descriptors],
        "gates": [[k, bool(v)] for k, v in sorted(gates.items())
                  if isinstance(v, bool)],
    }


def behaviour_signature(ev: Dict[str, Any], gates: Dict[str, Any],
                        descriptors: Optional[Tuple[float, ...]] = None) -> str:
    payload = behaviour_payload(ev, gates, descriptors)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


class SigCost:
    """Instrumented behavioural-dedup archive.

    Reports yield (distinct behaviours) and price (signature seconds) apart,
    so the lever can never be credited with a gain whose cost is hidden.
    """

    def __init__(self) -> None:
        self.n_calls = 0
        self.seconds = 0.0
        self.seen: Dict[str, int] = {}
        self.n_duplicates = 0

    def admit(self, ev: Dict[str, Any], gates: Dict[str, Any],
              descriptors: Optional[Tuple[float, ...]] = None) -> Tuple[str, bool]:
        t0 = time.perf_counter()
        sig = behaviour_signature(ev, gates, descriptors)
        self.seconds += time.perf_counter() - t0
        self.n_calls += 1
        if sig in self.seen:
            self.seen[sig] += 1
            self.n_duplicates += 1
            return sig, False
        self.seen[sig] = 1
        return sig, True

    def report(self) -> Dict[str, Any]:
        return {
            "schema": SIG_SCHEMA,
            "quantisation": QUANT,
            "n_signature_calls": self.n_calls,
            "n_distinct_behaviours": len(self.seen),
            "n_duplicates_suppressed": self.n_duplicates,
            "dedup_seconds": round(self.seconds, 6),
            "dedup_seconds_per_call": (round(self.seconds / self.n_calls, 9)
                                       if self.n_calls else None),
        }
