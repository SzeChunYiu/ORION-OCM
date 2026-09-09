"""Single-organism evaluation wrapper: tiers, caching, hard gates (MZ-D1)."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from morphology.compile import CompiledOrganism, InvariantViolation, compile_genome
from morphology.schema import OCMMorphologyGenomeV1
from evaluation.invariants import hard_gate_report
from evaluation.lifetime import run_lifetime
from evaluation.lifetime2 import run_lifetime2

_TIERS = ("T0", "T1", "T2")

_cache: Dict[str, Dict[str, Any]] = {}


def evaluate_genome(genome: OCMMorphologyGenomeV1, tier: Optional[str] = None,
                    use_cache: bool = True) -> Dict[str, Any]:
    """Evaluate one genome.  Deterministic; cached by (phenotype, tier).

    T0 = compile + invariants + V1 exact micro-world battery (frozen).
    T2 = MZ-D7 developmental lifetime (LIFETIME_ECOLOGY_V2, FREEZE_V1_AMEND_3):
    long battery + RESET control run; the reset evaluation is returned under
    evaluation["reset_control"].  An explicit tier argument wins; otherwise
    the ZOO_TIER environment variable decides (default T0) so the search
    arms run unmodified at either tier.
    """
    tier = tier or os.environ.get("ZOO_TIER", "T0")
    if tier not in _TIERS:
        raise ValueError("unknown tier %s" % tier)
    org = compile_genome(genome)
    key = org.phenotype_digest + "|" + tier
    if use_cache and key in _cache:
        return _cache[key]
    if tier == "T1":
        raise NotImplementedError(
            "CANNOT_CHECK_T1_NOT_IMPLEMENTED (cross-family microscopes, "
            "not in MZ-D7 scope)")
    ev = run_lifetime(org) if tier == "T0" else run_lifetime2(org)
    if tier == "T2":
        ev["reset_control"] = run_lifetime2(org, reset=True)
    gates = hard_gate_report(org, ev)
    out = {
        "genotype_digest": org.genotype_digest,
        "phenotype_digest": org.phenotype_digest,
        "active_unit_types": list(org.active_unit_types),
        "active_operators": list(org.active_operators),
        "dead_units": list(org.dead_units),
        "n_units": len(genome.U),
        "gates": gates,
        "feasible": gates["feasible"],
        "evaluation": ev,
        "tier": tier,
    }
    if use_cache:
        _cache[key] = out
    if len(_cache) > 200000:  # bound memory in long array jobs
        _cache.clear()
    return out


def evaluate_many(genomes, tier: str = "T0") -> Dict[str, Any]:
    """Batch helper used by census/search runners (no cache across batches)."""
    results = []
    for g in genomes:
        try:
            results.append(evaluate_genome(g, tier=tier))
        except InvariantViolation as iv:
            results.append({"feasible": False, "invariant_violation": iv.code})
    return {"results": results}


def clear_cache() -> None:
    _cache.clear()
