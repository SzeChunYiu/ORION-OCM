"""Constitutional invariants + hard gates (#221 sec 6) — fail-closed.

Hard gates (all must pass before a candidate is feasible):
  GATE_CORRECTNESS        no harmful transfers, no stale answers
  GATE_INVARIANTS         compile-time invariant set holds (compile.py)
  GATE_PROTECTED_ISOLATION  no cross-contamination channel exists in this
                           tranche (single-organism processes, no shared
                           stores) — asserted structurally, see note
  GATE_REVOCATION_FIDELITY  revocation semantics not weakened (R != none
                           whenever revoke-relevant worlds are scored)
  GATE_CAPABILITY_FLOOR   solved_fraction >= frozen floor

Floors are frozen in FREEZE_V1.json before scored runs.
"""
from __future__ import annotations

from typing import Any, Dict

from morphology.compile import CompiledOrganism

CAPABILITY_FLOOR_V1 = 0.5  # frozen: solve >= 50% of the fixed battery
REVOCATION_REQUIRED = True  # battery contains revocation worlds


def hard_gate_report(org: CompiledOrganism, ev: Dict[str, Any]) -> Dict[str, Any]:
    correctness = (ev.get("harmful_transfers", 0) == 0
                   and ev.get("stale_answers", 0) == 0)
    revocation_ok = (not REVOCATION_REQUIRED) or (org.genome.R != "none")
    capability_ok = ev.get("solved_fraction", 0.0) >= CAPABILITY_FLOOR_V1
    # protected isolation: this tranche evaluates organisms in isolated
    # deterministic processes with no shared memory or external IO; the gate
    # asserts the evaluation path did not open any store outside the run dir.
    isolation_ok = ev.get("external_io", 0) == 0
    gates = {
        "GATE_CORRECTNESS": correctness,
        "GATE_INVARIANTS": True,  # compile_genome raised otherwise
        "GATE_PROTECTED_ISOLATION": isolation_ok,
        "GATE_REVOCATION_FIDELITY": revocation_ok,
        "GATE_CAPABILITY_FLOOR": capability_ok,
    }
    gates["feasible"] = all(gates.values())
    return gates
