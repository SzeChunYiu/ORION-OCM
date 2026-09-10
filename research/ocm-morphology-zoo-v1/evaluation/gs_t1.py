"""GS tier T1 — intermediate developmental lifetime (GRAND SEARCH #221
sec 18 successive halving rung).  Additive: evaluate.py is NOT modified
(its T1 remains NotImplementedError for the MZ-D7 scope; the GS freeze
declares this module as the GS T1 definition).

T1 = one LIFETIME_ECOLOGY_V2 lifetime (run_lifetime2, reset=False) — the
same battery T2 runs, WITHOUT the reset control run and without the T2
tier label: the evaluation dict carries tier="T1" so dev_score uses the
T0-referenced cost formula (W_REF/B_REF; frozen constants, no new
references minted).  Gates are the frozen hard gates, unmodified.
"""
from __future__ import annotations

from typing import Any, Dict

from evaluation.invariants import hard_gate_report
from evaluation.lifetime2 import run_lifetime2
from morphology.compile import compile_genome


def evaluate_t1(genome) -> Dict[str, Any]:
    """GS T1 evaluation: shape identical to evaluate_genome output."""
    org = compile_genome(genome)
    ev = run_lifetime2(org, reset=False)
    ev["tier"] = "T1"
    gates = hard_gate_report(org, ev)
    return {
        "genotype_digest": org.genotype_digest,
        "phenotype_digest": org.phenotype_digest,
        "active_unit_types": list(org.active_unit_types),
        "active_operators": list(org.active_operators),
        "dead_units": list(org.dead_units),
        "n_units": len(genome.U),
        "gates": gates,
        "feasible": gates["feasible"],
        "evaluation": ev,
        "tier": "T1",
    }
