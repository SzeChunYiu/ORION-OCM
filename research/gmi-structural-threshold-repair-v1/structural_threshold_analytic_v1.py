"""Portable full analytic receipt, conditional on the explicit opcode contract."""
from itertools import product
import json
from structural_threshold_costs_v1 import (INPUTS, PARITY, SHARED_WITNESS, XOR_WITNESS,
    certified_lower, compiled, native_cost_contract, require, syntax_stress_controls)
from structural_threshold_geometry_v1 import (midpoint_certificates, nonunate_controls,
    two_input_threshold_certificate)
from structural_threshold_countercontrols_v1 import (bounded_output_counterexample,
    delegation_counterexample, rendering_counterexample)


def run():
    contract = native_cost_contract()
    native_count, witness, _ = compiled(SHARED_WITNESS)
    xor_count, xor, _ = compiled(XOR_WITNESS)
    values = tuple(witness(x) for x in INPUTS)
    require(values == PARITY == tuple(xor(x) for x in INPUTS), "attainment/task mismatch")
    require(native_count == certified_lower("A", 3, 6) == certified_lower("B", 3) == 39,
            "analytic lower and constructed upper differ")
    require(xor_count == 11, "UNVERIFIABLE: XOR coordinate layout")
    degree_cases = 0
    for active in range(3, 8):
        for degrees in product((1, 2, 3), repeat=active):
            if sum(degrees) < 6:
                continue
            atom_sum = 6 + sum(4 + 2 * d for d in degrees) + 3 + 2 * active
            require(atom_sum == certified_lower("A", active, sum(degrees)) >= 39,
                    "finite independent support accounting mismatch")
            degree_cases += 1
    result = {"schema": "GMI_STRUCTURAL_THRESHOLD_ANALYTIC_RECEIPT_V1",
            "terminal": "ANALYTIC_FLAT_THRESHOLD_OPTIMUM_39_AT_OPCODE_CONTRACT",
            "cost_contract": contract, "runtime_patch_identity_claim": False,
            "midpoint_certificates": midpoint_certificates(),
            "two_input_output_certificate": two_input_threshold_certificate(),
            "dependency_boundary": nonunate_controls(),
            "arbitrary_coefficient_lower_bound": {
                "active_hidden_gates_at_least": 3, "active_input_incidence_at_least": 6,
                "shape_A": "9+6*r+2*s >=39", "shape_B": "15+8*r >=39",
                "all_unit_counts_covered_analytically": True,
                "coefficient_saturation_argument_used": False,
                "independent_finite_degree_cases": degree_cases},
            "attainment": {"source": SHARED_WITNESS, "all8_outputs": values,
                          "minimum_per_call": native_count, "minimum_per_sweep": 8 * native_count,
                          "xor_per_sweep": 8 * xor_count, "exclusion_in_registered_flat_class": True},
            "syntax_stress_controls": syntax_stress_controls(),
            "omitted_output_counterexample": bounded_output_counterexample(),
            "rendering_counterexample": rendering_counterexample(),
            "delegation_counterexample": delegation_counterexample(),
            "timing_or_ecology_measurements": False,
            "general_neural_or_delegating_family_exclusion": False,
            "scope": "two faithful flat-linear shapes; hidden-only output; ideal opcode contract"}

    return json.loads(json.dumps(result, sort_keys=True))
