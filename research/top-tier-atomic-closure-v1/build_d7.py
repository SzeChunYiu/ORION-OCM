#!/usr/bin/env python3
"""TTAC-D7 builder: FLAGSHIP_EXPERIMENT_V1 — binds #151 DevelopmentTransitionV1
as the programme flagship E3 route.

The design is frozen NOW (no retroactive tuning), but authorization to run is
explicitly withheld until every entry gate in issue #165 section 9 holds.
That is the honest D7 deliverable: a frozen route, not a premature run.
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent

ENTRY_GATES = [
    {"gate": "G2 causal reuse complete in at least one domain",
     "status": "PARTIAL", "evidence": "#165 evidence-sync 2026-09-09: G2.4 SUPPORTED AT REGISTERED POLYNOMIAL SCOPE (#192/#193) — explicitly 'Not G2.4 complete'"},
    {"gate": "G3 composition/failure evidence",
     "status": "PARTIAL", "evidence": "G3.1 composition supported at registered polynomial scope; G3.2 scoped failure memory open; G3.3/G3.4 roadmap items"},
    {"gate": "G4 exact metareasoning disposition",
     "status": "SATISFIED", "evidence": "EXACT_POLICY_SUFFICIENT current compose-stage terminal; #71 LEARNED_ROUTER_NOT_YET_AUTHORIZED"},
    {"gate": "Physical denominator acceptable",
     "status": "SATISFIED_AT_SCOPE", "evidence": "research/g5-physical-denominator-v1 DATABASE_PARENT_SUFFICIENT, 14 parity/restart tests, 66us measured"},
    {"gate": "At least two materially different domains use the same core",
     "status": "PARTIAL", "evidence": "language/mathematics/procedural types registered per #165 section 8; heterogeneous lifetime study not executed (LIF-02 synthetic calibration only)"},
    {"gate": "Strongest comparator configurations frozen",
     "status": "SATISFIED", "evidence": "COMPARATOR_LADDER_FREEZE_V1.json (TTAC-D7a, merged by this PR chain; sha recorded in the #165 evidence-sync comment) freezes every rung B0-B8+OCM for the developmental arm: registered machine configurations, budgets (200k serving / 200k dev / sealed dev charge ledger rule), seed 20260910, capability gate delta 0.20 before protected outcomes, HDI-14 + P3 physical meters; rungs anchored to sealed receipts (M1B arms, FNA-3 tournament winners, M7/M12 matched+semantic parents); Transformer gap routed to E5 with in-estate scope declared"},
]

DESIGN = {
    "flagship_id": "FE-DEV-AMORT-1",
    "owner_issue": 151,
    "decisive_claim_binding": "DC-10 'Developmental-lineage amortization across generations' (DECISIVE_CLAIM_REGISTRY_V1; atoms ATOM-DEV-01, ATOM-DEV-02; current_min 2)",
    "scientific_question": "Does earlier verified experience in ONE persistent lineage make later related cognition and later machine modification cheaper at matched capability and complete lifetime cost — measured on prospectively frozen related-task families with the full cost vector charged?",
    "record_schema": "DevelopmentTransitionV1 (#165 section G7): every transition records lineage id, source/target stage, machine identities, persistent-state digest, donor identities, prior-information manifest, new information, new methods/schemas, reused method identities, actual execution witnesses, primitive operators added, composition depth, acquisition/reasoning/verification/revision/self-change/maintenance cost, persistent bytes, active k/N, kappa/Omega/chi, retention, negative transfer, ablation, strongest-parent result, terminal",
    "arms": [
        {"arm": "CONTINUED_OCM", "role": "principal", "rule": "no reset across stages; full learned state persists where earned"},
        {"arm": "RESET_OCM", "role": "primary control", "rule": "same machine, state reset at each stage boundary"},
        {"arm": "STRONG_ADAPTIVE_PARENT", "role": "parent control", "rule": "comparators evolve too; no frozen-parent strawman (#165 G7)"},
    ],
    "primary_endpoints": [
        "C_acquire(next related competence | K_t) vs C_acquire(next related competence | K_0)",
        "C_reason(next related task) delta at matched capability",
        "complete lifetime cost vector per DevelopmentTransitionV1",
    ],
    "secondary_endpoints": ["k/N vs N growth", "revision cone / collateral invalidations", "kappa/Omega/chi developmental variables", "harmful-transfer refusal"],
    "capability_gate": "Performance_OCM >= Performance_parent - delta frozen BEFORE protected outcomes (#165 section 9); no efficiency claim if capability materially worse",
    "stats_plan_frozen": {
        "design": "paired across task-order permutations; fresh family identities; scale axis 1x/3x/10x/30x/100x where feasible (#165 section 10)",
        "primary_test": "pre-registered related-family acquisition-cost contrast, one-sided, frozen n, fixed horizon",
        "multiplicity": "Holm across the three primary endpoints",
        "non_inferiority": "capability margin delta frozen before protected splits",
        "stopping_exclusion": "no interim looks; exclusions only by pre-registered rules with reasons retained",
        "independent_units": "task families (not episodes); benchmark labels independently recovered, never generator intent (H-MV-05)",
    },
    "authoritative_negative_terminals": [
        "RESET_PARENT_EQUIVALENT", "CURRICULUM_ORDER_DOMINATES", "HARMFUL_DEVELOPMENTAL_TRANSFER",
        "MAINTENANCE_COST_DOMINATES", "PARENT_SUFFICIENT", "CANNOT_CHECK_<reason>",
    ],
    "execution_hosts": {"e3_confirmatory": "laptop billy (ssh billy-laptop)", "e4_disjoint_replication": "billy-old (ssh billy-old)", "scale_arms": "LUNARC (ssh cosmos, batch)", "forbidden": "Mac mini — git/gh and single-file edits only"},
    "authorization": {
        "status": "FROZEN_DESIGN_NOT_AUTHORIZED",
        "blocking_gates": [g["gate"] for g in ENTRY_GATES if g["status"] not in ("SATISFIED", "SATISFIED_AT_SCOPE")],
        "rule": "authorization flips only when every entry gate reads SATISFIED on an updated #165 evidence sync AND independently authored world families exist for E3 (H-MV-05); no partial-run waiver",
    },
}

suite = {
    "schema": "TTAC_FLAGSHIP_EXPERIMENT", "version": "V1", "d_step": "TTAC-D7", "owner_issue": 277,
    "built_utc": "2026-09-10",
    "binds_issue": 151, "matrix_ref": "READINESS_MATRIX_V1.json",
    "claims_ref": "DECISIVE_CLAIM_REGISTRY_V1.json", "dag_ref": "BLOCKER_DAG_V1.json",
    "design": DESIGN,
    "entry_gates": ENTRY_GATES,
    "census": {"gates": len(ENTRY_GATES),
               "satisfied": sum(1 for g in ENTRY_GATES if g["status"] == "SATISFIED"),
               "partial": sum(1 for g in ENTRY_GATES if g["status"] == "PARTIAL"),
               "pending": sum(1 for g in ENTRY_GATES if g["status"] == "PENDING"),
               "authorization": DESIGN["authorization"]["status"]},
    "non_final": "EXPLICITLY_NON_FINAL",
}

assert all(g["status"] in ("SATISFIED", "PARTIAL", "PENDING", "SATISFIED_AT_SCOPE") for g in ENTRY_GATES)
assert DESIGN["authorization"]["blocking_gates"], "authorization must not be granted at freeze time"
assert len(DESIGN["arms"]) == 3 and {a["arm"] for a in DESIGN["arms"]} == {"CONTINUED_OCM", "RESET_OCM", "STRONG_ADAPTIVE_PARENT"}

(BASE / "FLAGSHIP_EXPERIMENT_V1.json").write_text(json.dumps(suite, indent=1) + "\n")
print(f"gates={len(ENTRY_GATES)} satisfied={suite['census']['satisfied']} partial={suite['census']['partial']} pending={suite['census']['pending']}")
print("authorization:", DESIGN["authorization"]["status"])
print("blocking:", "; ".join(DESIGN["authorization"]["blocking_gates"]))
print("VALIDATION OK")
