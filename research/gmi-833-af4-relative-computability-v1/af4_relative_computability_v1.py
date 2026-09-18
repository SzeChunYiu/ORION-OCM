from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Tuple

HERE = Path(__file__).resolve().parent
CLAIM_CEILING = "GMI_AF4_RELATIVE_COMPUTABILITY_AND_NONTERMINAL_ORACLE_FRONTIER_AT_REGISTERED_STANDARD_ORACLE_MODEL_SCOPE"
PROVENANCE = "ORACLE_ADVICE_OR_TOOL"
FORBIDDEN = {
    "HALTING_PROBLEM_SOLVED_UNIVERSALLY",
    "ALL_UNDECIDABILITY_BARRIERS_REMOVED",
    "PHYSICAL_HYPERCOMPUTATION_ESTABLISHED",
    "PHYSICAL_CHURCH_TURING_FALSIFIED",
    "NO_FINAL_COMPUTABILITY_BARRIER_IN_ALL_PHYSICS",
    "GODEL_INCOMPLETENESS_ESCAPED",
    "GODEL_MACHINE_PROVES_UNIVERSAL_SELF_IMPROVEMENT",
    "ORACLE_POWER_FREE",
    "COMPLETE_GMI",
}

@dataclass(frozen=True)
class OracleSubstrate:
    level: int
    oracle_id: str
    model: str = "STANDARD_ORACLE_TURING_MACHINE"
    provenance: str = PROVENANCE
    access_charge_per_query: int = 1
    finite_advice_bits: Optional[int] = None

@dataclass(frozen=True)
class Displacement:
    source_level: int
    target_level: int
    query_id: str
    source_status: str
    target_status: str
    changed_axes: Tuple[str, ...]
    provenance: str
    target_oracle_id: str
    direct_oracle_queries: int
    oracle_access_charge: int
    finite_advice_bits: Optional[int]
    nearest_residual: str
    classification: Tuple[str, ...]
    evidence_role: str
    terminal: str

@dataclass(frozen=True)
class ProofContext:
    formal_system_id: str
    axioms_id: str
    proof_rules_id: str
    utility_theorem: str
    consistency_or_soundness_assumptions: Tuple[str, ...]
    proof_search_contract: str


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def substrate(level: int) -> OracleSubstrate:
    require(type(level) is int and level >= 0, "INVALID_JUMP_LEVEL")
    return OracleSubstrate(level=level, oracle_id=f"A^({level})")


def query_id(level: int) -> str:
    require(type(level) is int and level >= 0, "INVALID_QUERY_LEVEL")
    return f"Q_{level}=MEMBERSHIP_IN_A^({level+1})"


def parent_status(substrate_level: int, q_level: int) -> str:
    """Parent-theorem-derived registry status, not a decision procedure."""
    require(substrate_level >= 0 and q_level >= 0, "INVALID_LEVEL")
    return "DECIDABLE" if substrate_level >= q_level + 1 else "UNDECIDABLE_RELATIVE_TO_S"


def validate_displacement(d: Displacement) -> None:
    require(d.target_level == d.source_level + 1, "NON_ADJACENT_JUMP_DISPLACEMENT")
    require(d.query_id == query_id(d.source_level), "QUERY_LEVEL_MISMATCH")
    require(d.source_status == "UNDECIDABLE_RELATIVE_TO_S", "SOURCE_STATUS_MISMATCH")
    require(d.target_status == "DECIDABLE", "TARGET_STATUS_MISMATCH")
    require(d.changed_axes == ("S", "Pi", "R"), "CHANGED_AXES_MISMATCH")
    require(d.provenance == PROVENANCE, "MISSING_ORACLE_PROVENANCE")
    require(d.target_oracle_id == substrate(d.target_level).oracle_id, "TARGET_ORACLE_ID_MISMATCH")
    require(d.direct_oracle_queries == 1, "DIRECT_QUERY_COUNT_MUST_BE_ONE")
    require(d.oracle_access_charge >= 1, "ORACLE_ACCESS_MUST_BE_CHARGED")
    require(d.finite_advice_bits is None, "INFINITE_ORACLE_MUST_NOT_HAVE_FINITE_INFORMATION_BITS")
    require(d.nearest_residual == f"{query_id(d.target_level)} remains UNDECIDABLE_RELATIVE_TO_S_{d.target_level}", "MISSING_OR_WRONG_RESIDUAL")
    require(d.classification == ("RELATIVIZATION", "ORACLE_OR_ADVICE", "SUBSTRATE_EXPANSION"), "CLASSIFICATION_MISMATCH")
    require(d.evidence_role == "PARENT_THEOREM_DERIVED_COROLLARY_TABLE_NOT_PARENT_PROOF", "EVIDENCE_ROLE_OVERCLAIM")
    require(d.terminal != "HALTING_PROBLEM_SOLVED_UNIVERSALLY", "UNIVERSAL_HALTING_FORBIDDEN")
    require(d.terminal == "BASE_QUERY_DECIDABILITY_DISPLACED_BY_IMPORTED_ORACLE_POWER", "TERMINAL_MISMATCH")


def adjacent_displacement(level: int) -> Displacement:
    target = substrate(level + 1)
    d = Displacement(
        source_level=level,
        target_level=level + 1,
        query_id=query_id(level),
        source_status=parent_status(level, level),
        target_status=parent_status(level + 1, level),
        changed_axes=("S", "Pi", "R"),
        provenance=PROVENANCE,
        target_oracle_id=target.oracle_id,
        direct_oracle_queries=1,
        oracle_access_charge=target.access_charge_per_query,
        finite_advice_bits=target.finite_advice_bits,
        nearest_residual=f"{query_id(level+1)} remains UNDECIDABLE_RELATIVE_TO_S_{level+1}",
        classification=("RELATIVIZATION", "ORACLE_OR_ADVICE", "SUBSTRATE_EXPANSION"),
        evidence_role="PARENT_THEOREM_DERIVED_COROLLARY_TABLE_NOT_PARENT_PROOF",
        terminal="BASE_QUERY_DECIDABILITY_DISPLACED_BY_IMPORTED_ORACLE_POWER",
    )
    validate_displacement(d)
    return d


def validate_claim_terminal(terminal: str, *, physical_evidence: bool = False) -> None:
    require(terminal not in FORBIDDEN, f"FORBIDDEN_PROMOTION:{terminal}")
    if terminal.startswith("PHYSICAL_"):
        require(physical_evidence, "PHYSICAL_CLAIM_WITHOUT_PHYSICAL_EVIDENCE")


def validate_proof_context(ctx: ProofContext) -> None:
    fields = asdict(ctx)
    for k, v in fields.items():
        if isinstance(v, tuple):
            require(bool(v) and all(str(x).strip() for x in v), f"MISSING_PROOF_CONTEXT:{k}")
        else:
            require(bool(str(v).strip()), f"MISSING_PROOF_CONTEXT:{k}")


def audit_godel_machine_claim(ctx: Optional[ProofContext], terminal: str, *, axioms_changed: bool = False) -> str:
    require(ctx is not None, "CANNOT_AUDIT_PROOF_SYSTEM")
    validate_proof_context(ctx)
    require(terminal != "GODEL_INCOMPLETENESS_ESCAPED", "INCOMPLETENESS_ESCAPE_FORBIDDEN")
    require(terminal != "GODEL_MACHINE_PROVES_UNIVERSAL_SELF_IMPROVEMENT", "UNIVERSAL_SELF_IMPROVEMENT_FORBIDDEN")
    if axioms_changed:
        return "PROOF_SYSTEM_CONTEXT_CHANGED_NOT_INCOMPLETENESS_ESCAPE"
    return "PROOF_SYSTEM_RELATIVE_SELF_IMPROVEMENT_CLAIM_ONLY"


def interpret_unprovable(status: str) -> str:
    require(status == "UNPROVABLE_IN_T", "UNKNOWN_PROVABILITY_STATUS")
    return "NOT_DERIVABLE_IN_REGISTERED_T__TRUTH_NOT_INFERRED"


def finite_proof_context_witness() -> dict:
    t0_axioms = {"P"}
    t1_axioms = {"P", "R"}
    proposition = "R"
    return {
        "status": "FINITE_SYNTACTIC_CONTEXT_DEPENDENCE_ONLY",
        "proposition": proposition,
        "provable_in_T0": proposition in t0_axioms,
        "provable_in_T1": proposition in t1_axioms,
        "axioms_changed": True,
        "evidence_role": "TOY_CONTEXT_DEPENDENCE_NOT_GODEL_PROOF",
    }


def certificate() -> dict:
    rows = [asdict(adjacent_displacement(n)) for n in range(6)]
    chain = [
        {
            "level": n,
            "substrate": asdict(substrate(n)),
            "degree_label": f"deg_T(A^({n}))",
            "parent_relation_to_next": "STRICTLY_BELOW_BY_TURING_JUMP_PARENT" if n < 6 else None,
        }
        for n in range(7)
    ]
    require(parent_status(0, 0) == "UNDECIDABLE_RELATIVE_TO_S", "BASE_HALTING_STATUS_DRIFT")
    require(parent_status(1, 0) == "DECIDABLE", "BASE_HALTING_ORACLE_DISPLACEMENT_DRIFT")
    require(parent_status(1, 1) == "UNDECIDABLE_RELATIVE_TO_S", "RELATIVE_HALTING_RESIDUAL_DRIFT")
    ctx = ProofContext(
        formal_system_id="T_GM_V1",
        axioms_id="AXIOMS_GM_V1",
        proof_rules_id="RULES_GM_V1",
        utility_theorem="REWRITE_IMPROVES_EXPECTED_UTILITY_UNDER_REGISTERED_OBJECTIVE",
        consistency_or_soundness_assumptions=("REGISTERED_FORMAL_SYSTEM_ASSUMPTIONS",),
        proof_search_contract="PROOF_SEARCHER_V1",
    )
    result = {
        "status": "GREEN",
        "scope": "standard oracle Turing model; finite registered jump levels 0..6",
        "parent_theorem": {
            "id": "TURING_JUMP_STRICTNESS",
            "ownership": "PARENT_OWNED_NOT_PROVED_BY_EXECUTOR",
            "statement_used": "for every oracle A, A' is c.e. in A but not computable in A; deg_T(A) < deg_T(A')",
            "source": "SEP Recursive Functions, Proposition 3.7",
        },
        "comp_object": "Comp(S[A]) := deg_T(A) at registered standard-oracle scope only",
        "jump_chain": chain,
        "adjacent_displacements": rows,
        "base_halting_hostile": {
            "S0_Q0": "UNDECIDABLE_RELATIVE_TO_S",
            "S1_Q0": "DECIDABLE_BY_ONE_IMPORTED_ORACLE_QUERY",
            "S1_Q1": "UNDECIDABLE_RELATIVE_TO_S",
            "universal_terminal_allowed": False,
            "residual_preserved": True,
        },
        "nonterminal_frontier_terminal": "NO_TERMINAL_EFFECTIVE_FRONTIER_AT_REGISTERED_ORACLE_MODEL_SCOPE",
        "physical_scope": "NO_PHYSICAL_HYPERCOMPUTATION_CLAIM",
        "godel_machine_audit": {
            "proof_context": asdict(ctx),
            "registered_reading": audit_godel_machine_claim(ctx, "SCOPED_PROOF_GUIDED_REWRITE"),
            "changed_axioms_reading": audit_godel_machine_claim(ctx, "SCOPED_PROOF_GUIDED_REWRITE", axioms_changed=True),
            "unprovable_reading": interpret_unprovable("UNPROVABLE_IN_T"),
            "toy": finite_proof_context_witness(),
            "parent_scope": "INCOMPLETENESS_AND_GODEL_MACHINE_RESULTS_REMAIN_PROOF_SYSTEM_RELATIVE",
        },
        "evidence_role": "REGISTRY_COROLLARY_AND_HOSTILE_VALIDATION_NOT_PARENT_THEOREM_PROOF",
        "hostiles_required": 12,
        "forbidden_promotions": sorted(FORBIDDEN),
        "claim_ceiling": CLAIM_CEILING,
    }
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(HERE / "RESULT_V1.json"))
    args = ap.parse_args()
    result = certificate()
    text = json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
    Path(args.output).write_text(text)
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
