#!/usr/bin/env python3
"""Fail-closed reconciliation of the B14 and existing I5 formal evidence."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROUTING_RECEIPT = ROOT / "research/machine-intelligence-morphogenesis-v1/microscopes/results/STAGE_TOOL_ROUTING_V1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ISSUE_602_FORMAL_RECONCILIATION_FAIL: {message}")


def prose(text: str) -> str:
    """Normalize Markdown wrapping without weakening exact phrase checks."""
    return " ".join(text.split())


def main() -> None:
    ledger = json.loads((HERE / "SELECTOR_DERIVATION_LEDGER_V1.json").read_text(encoding="utf-8"))
    theorem = (HERE / "SYMBOLIC_SELECTOR_DERIVATION_THEOREM_V1.md").read_text(encoding="utf-8")
    reconciliation = (HERE / "ISSUE_602_FORMAL_RECONCILIATION_V1.md").read_text(encoding="utf-8")
    causal_boundary = (
        ROOT / "research/gmi-causal-identifiability-v1/CAUSAL_IDENTIFIABILITY_BOUNDARY_THEOREM_V1.md"
    ).read_text(encoding="utf-8")
    causal_parents = (
        ROOT / "research/gmi-causal-rung-repair-v1/PARENTS_AND_SCOPE_V1.md"
    ).read_text(encoding="utf-8")
    acquisition_parents = (
        ROOT / "research/gmi-grand-unification-v1/EPISTEMIC_ACQUISITION_PARENT_SUBTRACTION_V1.md"
    ).read_text(encoding="utf-8")
    routing = json.loads(ROUTING_RECEIPT.read_text(encoding="utf-8"))

    require(ledger["status"] == "GREEN_AT_REGISTERED_FINITE_AND_FORMAL_SCOPE", "B14 status not green")
    require({"P1", "P2"} == set(ledger["evidence_classes"]), "B14 evidence classes drifted")
    require("sound-cover characterization" in theorem, "B14 theorem missing")
    require("UNIVERSAL_BEST_SELECTOR_LANGUAGE" in theorem, "B14 universal-claim guard missing")

    # I5 aliasing is exactly the non-constancy-on-observational-fiber theorem.
    normalized_boundary = prose(causal_boundary)
    normalized_parents = prose(causal_parents)
    require("theta is point-identified at P **iff** theta(M) is constant on C(P)" in normalized_boundary, "I5 fiber criterion missing")
    require("identical observational laws but different exact interventional targets" in normalized_boundary, "I5 alias witness missing")

    # I5 parent subtraction must name all three tracker parents and deny novelty.
    require("Pearl" in normalized_parents, "Pearl/SCM parent missing")
    require("identification/estimation distinction" in normalized_parents, "causal identification parent missing")
    require("not a new causal calculus" in normalized_parents, "parent-ownership boundary missing")
    require("finite procedure is exhaustive elimination" in normalized_parents, "finite-procedure disposition missing")
    normalized_acquisition = prose(acquisition_parents)
    require("Bayesian experimental design" in normalized_acquisition, "Bayesian experimental-design parent missing")
    require("active causal discovery" in normalized_acquisition, "active-causal-learning parent missing")
    require("parent theory" in normalized_acquisition, "active-acquisition ownership disposition missing")

    # Existing B20 finite evidence closes dominance and routing/verification
    # cost, but deliberately not the recovery/admission/domain rows.
    shapes = [row["shape"] for row in routing["recovery"]]
    require(len(shapes) == 70, "B20 recovery world count drifted")
    require(shapes.count("mixed") == 40, "B20 mixed winner count drifted")
    require(shapes.count("all held") == 30, "B20 monolith winner count drifted")
    relational = [row for row in routing["verification"] if row["obligation"] == "relational"]
    functional = [row for row in routing["verification"] if row["obligation"] == "functional"]
    require(relational and all(row["check_probes"] < row["solve_probes"] for row in relational), "B20 relational verification result drifted")
    require(functional and all(row["check_probes"] == row["solve_probes"] for row in functional), "B20 functional verification equality drifted")
    collapse = routing["collapse_control"]
    require(collapse["map_nodes"] > collapse["hold_covered"], "B20 routing-cost collapse control no longer fires")

    verified = ledger["issue_602_reconciliation"]["verified_rows"]
    require(len(verified) == ledger["issue_602_reconciliation"]["verified_row_count"] == 6, "verification count drifted")
    require(ledger["issue_602_reconciliation"]["existing_checked_rows_crossvalidated"] == 5, "live-state cross-validation count drifted")
    require(ledger["issue_602_reconciliation"]["new_live_checkbox_authorized_after_merge_and_ci"] == "P0 finish causal cognition", "live checkbox authorization drifted")
    require(ledger["issue_602_reconciliation"]["adjacent_open_rows_preserved"] is True, "adjacent open-row guard missing")
    require("Rows deliberately left open" in reconciliation, "open-row boundary missing")
    for token in (
        "COMPLETE_THEORY_OF_MACHINE_INTELLIGENCE",
        "UNIVERSAL_BEST_TOOL_ROUTER",
        "CAUSAL_DISCOVERY_COMPLETE",
    ):
        require(token in reconciliation, f"forbidden promotion missing: {token}")

    print("ISSUE_602_FORMAL_RECONCILIATION_V1_VALID")
    print("B14_SELECTOR_PLUS_EMITTER=GREEN")
    print("I5_OBSERVATIONAL_ALIAS_CONDITION=GREEN_EXISTING_EVIDENCE")
    print("I5_PARENT_SUBTRACTION=GREEN_EXISTING_EVIDENCE")
    print("P0_CAUSAL_COGNITION_FORMAL_ROWS=GREEN")
    print("B20_HETEROGENEOUS_DOMINANCE=GREEN_EXISTING_EVIDENCE")
    print("B20_ROUTING_AND_VERIFICATION_COST=GREEN_EXISTING_EVIDENCE")
    print("ISSUE_602_VERIFIED_ROWS=6")
    print("ISSUE_602_NEW_LIVE_CHECKBOX_AFTER_MERGE=P0_CAUSAL_COGNITION")


if __name__ == "__main__":
    main()
