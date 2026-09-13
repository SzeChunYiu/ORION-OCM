#!/usr/bin/env python3
"""Exact finite evidence, with inherited general decidability explicitly unexecuted."""
from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from classical_parent_v1 import classical_optimum
from finite_witnesses_v1 import (assistance_control, factor_orientation_control,
    mixed_support_controls, nonprojective_control, random_access_controls, relation_census,
    shared_seed_control)
from hostile_controls_v1 import run_hostile_controls
from quantum_parent_v1 import HERE, quantum_parent, verify_sources
from quantum_witness_v1 import task_fingerprint, verify_registered
from rational_matrix_v1 import encode, require

ASSUMPTIONS_SHA = "33733ae343018de7780ff49e12542d55a0988c84b3f396d8e6d76753e72f373d"


def assumptions(base=HERE):
    raw = (base / "ASSUMPTIONS_V1.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == ASSUMPTIONS_SHA, "assumption register drift")
    return json.loads(raw)


def decisive_relation():
    task = {"actions": 3, "allowed": ((frozenset((0, 1)),),
            (frozenset((0, 2)),), (frozenset((1, 2)),))}
    register = task_fingerprint(task)
    parent = classical_optimum(task)
    result = verify_registered(task, parent["rays"], parent["factors"], register)
    require(result["dimension"] == 2, "higher-order obstruction lost")
    return {"registered_task_sha256": register, "allowed": [[[0, 1]], [[0, 2]], [[1, 2]]],
            "pairwise_compatible": True, "common_action_exists": False,
            "exact_quantum_lower_dimension": 2, "rays": parent["rays"],
            "factors": parent["factors"], **result}


def run():
    scope = assumptions()
    parents = verify_sources()
    result = {
        "schema": "GMI_FINITE_QUANTUM_COVER_RECEIPT_V1",
        "status": "EXACT_FINITE_WITNESSES_AND_LOWER_CERTIFICATES_PASS",
        "assumptions_sha256": ASSUMPTIONS_SHA,
        "source_parents_sha256": hashlib.sha256((HERE / "SOURCE_PARENTS_V1.json").read_bytes()).hexdigest(),
        "implementation_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(HERE.glob("*.py"))},
        "analytic_theorem_sha256": hashlib.sha256(
            (HERE / "FINITE_QUANTUM_COVER_THEOREM_V1.md").read_bytes()).hexdigest(),
        "general_quantifier_eliminator_executed": False,
        "general_complex_algebraic_witness_solver_implemented": False,
        "hardware_or_ecology_measurements": False,
        "relation_census": relation_census(),
        "decisive_relation": decisive_relation(),
        "mixed_support_controls": mixed_support_controls(),
        "random_access_controls": random_access_controls(),
        "factor_orientation_control": factor_orientation_control(),
        "nonprojective_control": nonprojective_control(),
        "assistance_control": assistance_control(),
        "shared_seed_control": shared_seed_control(),
        "mature_quantum_parent": quantum_parent(),
        "hostile_controls_rejected": run_hostile_controls(),
    }
    require(scope["general_quantifier_eliminator_executed"] is False and len(parents["files"]) == 4,
            "scope or parent coverage drift")
    return encode(result)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))
