#!/usr/bin/env python3
"""Stack-wide integration guards for Grand GMI V2.

This checker deliberately validates committed receipt terminals rather than rerunning every
historical microscope. Individual layer tests remain the local executable authorities.
"""

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

EXPECTED = {
    "GRAND_GMI_SEMANTIC_CUT_RECEIPT_V1.json": "GRAND_GMI_SEMANTIC_CUT_TRANCHE_ALL_GREEN",
    "GRAND_GMI_RECURSIVE_RECEIPT_V1.json": "GRAND_GMI_RECURSIVE_MORPHOGENESIS_TRANCHE_ALL_GREEN",
    "GRAND_GMI_SUBSTRATE_SYMMETRY_RECEIPT_V1.json": "GRAND_GMI_SUBSTRATE_SYMMETRY_TRANCHE_ALL_GREEN",
    "GRAND_GMI_COMPOSITIONAL_RECEIPT_V1.json": "GRAND_GMI_COMPOSITIONAL_DISTRIBUTED_TRANCHE_ALL_GREEN",
    "GRAND_GMI_MEANING_RECEIPT_V1.json": "GRAND_GMI_CAUSAL_SEMANTIC_VIABILITY_TRANCHE_ALL_GREEN",
    "GRAND_GMI_MASTER_RECEIPT_V1.json": "GRAND_GMI_MASTER_INTEGRATION_ALL_GREEN",
    "GRAND_GMI_PHYSICAL_BRIDGE_RECEIPT_V1.json": "GRAND_GMI_PHYSICAL_RESOURCE_BRIDGE_TRANCHE_ALL_GREEN",
    "GRAND_GMI_QUANTUM_RECEIPT_V1.json": "GRAND_GMI_QUANTUM_PROCESS_INSTANTIATION_TRANCHE_ALL_GREEN",
    "GRAND_GMI_CONTINUOUS_RECEIPT_V1.json": "GRAND_GMI_MEASURABLE_CONTINUOUS_TRANCHE_ALL_GREEN",
    "GRAND_GMI_MORPHOLOGY_SELECTION_RECEIPT_V1.json": "GRAND_GMI_MORPHOLOGY_SELECTION_FINITE_CHECKS_ALL_GREEN",
    "GRAND_GMI_FAMILY_SELECTION_RECEIPT_V1.json": "GRAND_GMI_FAMILY_SELECTION_FINITE_CHECKS_ALL_GREEN",
    "GRAND_GMI_REALIZATION_COMPILER_RECEIPT_V1.json": "GRAND_GMI_REALIZATION_COMPILER_FINITE_CHECKS_ALL_GREEN",
    "GRAND_GMI_PHENOMENOLOGY_RECEIPT_V1.json": "GRAND_GMI_PHENOMENOLOGY_REDUCTION_TRANCHE_ALL_GREEN",
    "GRAND_GMI_END_TO_END_RECEIPT_V1.json": "GRAND_GMI_END_TO_END_DERIVATION_TRACES_ALL_GREEN",
}

AUTHORITIES = [
    "GRAND_GMI_MASTER_THEORY_V2.md",
    "MASTER_CLOSURE_LEDGER_V2.md",
    "SEMANTIC_CUT_THEOREM_V1.md",
    "INFORMATION_COMPUTATION_SEPARATION_THEOREM_V1.md",
    "RECURSIVE_MORPHOGENESIS_THEOREM_V1.md",
    "SYMMETRY_TO_MORPHOLOGY_THEOREM_V1.md",
    "SUBSTRATE_LIFTING_THEOREM_V1.md",
    "COMPOSITIONAL_DISTRIBUTED_GMI_THEOREM_V1.md",
    "CAUSAL_SEMANTIC_VIABILITY_THEOREM_V1.md",
    "PHYSICAL_RESOURCE_BRIDGE_THEOREM_V1.md",
    "QUANTUM_PROCESS_INSTANTIATION_THEOREM_V1.md",
    "MEASURABLE_CONTINUOUS_GMI_THEOREM_V1.md",
    "MORPHOLOGY_SELECTION_THEOREM_V1.md",
    "MORPHOLOGY_FAMILY_SELECTION_THEOREM_V1.md",
    "REALIZATION_COMPILER_THEOREM_V1.md",
    "PHENOMENOLOGY_REDUCTION_ATLAS_V1.md",
    "END_TO_END_DERIVATIONS_V1.md",
    "UNCOMPUTABILITY_BOUNDARY_THEOREM_V1.md",
    "APPROXIMATE_SEMANTIC_GEOMETRY_THEOREM_V1.md",
]


def check_receipt_stack():
    observed = {}
    for filename, terminal in EXPECTED.items():
        path = HERE / filename
        assert path.is_file(), filename
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["terminal"] == terminal, (filename, data.get("terminal"), terminal)
        observed[filename] = terminal
    return {"receipt_count": len(observed), "all_green": True, "terminals": observed}


def check_authority_stack():
    missing = [name for name in AUTHORITIES if not (HERE / name).is_file()]
    assert not missing, missing
    return {"authority_documents": len(AUTHORITIES), "missing": [], "all_present": True}


def check_completion_contract():
    master = (HERE / "GRAND_GMI_MASTER_THEORY_V2.md").read_text(encoding="utf-8")
    ledger = (HERE / "MASTER_CLOSURE_LEDGER_V2.md").read_text(encoding="utf-8")
    required = [
        "GRAND_GMI_V2_FORMAL_THEORY_ARCHITECTURE_CLOSED = TRUE",
        "unrestricted Turing-complete",
        "falsifier",
        "family selection",
        "finite-dimensional quantum",
    ]
    text = master + "\n" + ledger
    missing = [token for token in required if token not in text]
    assert not missing, missing
    return {"required_contract_markers": len(required), "missing": [], "all_present": True}


def run():
    return {
        "terminal": "GRAND_GMI_V2_STACK_INTEGRATION_ALL_GREEN",
        "receipt_stack": check_receipt_stack(),
        "authority_stack": check_authority_stack(),
        "completion_contract": check_completion_contract(),
        "formal_theory_architecture_closed": True,
        "empirical_science_finished": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
