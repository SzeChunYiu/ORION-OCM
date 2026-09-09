"""Single-organism evaluation wrapper: tiers, caching, hard gates (MZ-D1)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from morphology.compile import CompiledOrganism, InvariantViolation, compile_genome
from morphology.schema import OCMMorphologyGenomeV1
from evaluation.invariants import hard_gate_report
from evaluation.lifetime import run_lifetime

_TIERS = ("T0", "T1", "T2")

_cache: Dict[str, Dict[str, Any]] = {}


def evaluate_genome(genome: OCMMorphologyGenomeV1, tier: str = "T0",
                    use_cache: bool = True) -> Dict[str, Any]:
    """Evaluate one genome.  Deterministic; cached by (phenotype, tier).

    T0 = compile + invariants + exact micro-world battery (this tranche).
    T1/T2 lifetime extensions are MZ-D7; requesting them now is an explicit
    NOT_YET_IMPLEMENTED error, never a silent T0 answer.
    """
    if tier not in _TIERS:
        raise ValueError("unknown tier %s" % tier)
    org = compile_genome(genome)
    key = org.phenotype_digest + "|" + tier
    if use_cache and key in _cache:
        return _cache[key]
    if tier in ("T1", "T2"):
        raise NotImplementedError(
            "CANNOT_CHECK_T1_T2_NOT_IMPLEMENTED (MZ-D7 scope, not scored yet)")
    ev = run_lifetime(org)
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
