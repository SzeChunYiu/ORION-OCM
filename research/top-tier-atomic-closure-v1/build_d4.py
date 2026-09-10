#!/usr/bin/env python3
"""TTAC-D4 builder: MEASUREMENT_VALIDITY_V1 — hostile suite against the
programme's own load-bearing measurements.

Every hostile targets a measurement family that READINESS_MATRIX_V1 /
DECISIVE_CLAIM_REGISTRY_V1 scores depend on. Statuses are honest:
EXECUTED hostiles cite artifacts on origin/main; DESIGNED_PENDING ones
name their blocker. A suite that passes everything is theater: H-MV-02
records a real measurement failure (raw counts did not survive the
physical denominator).
"""
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent

HOSTILES = [
    {"hostile_id": "H-MV-01", "target": "any headline comparative positive (DC-02/DC-06/DC-07 family)",
     "attack": "re-run the headline measurement under outcome-label shuffle (shuffle-equal-n null); a real edge collapses to null, a fabricated selectivity edge survives",
     "pass_condition": "headline either collapses under shuffle or is retracted",
     "status": "EXECUTED", "outcome": "CONTROL CAUGHT A REAL FALSE POSITIVE",
     "receipt": "research/quantum-structural-ocm-v1/ORION_QUANTUM_SOURCE_LEDGER.md FQ-2: headline retracted, null-reproducible under shuffle (ATOM-PAR-03)"},
    {"hostile_id": "H-MV-02", "target": "cost claims measured as raw search/verification counts",
     "attack": "substitute the physical denominator (elapsed time, RSS, I/O, storage) for the count metric",
     "pass_condition": "cost ranking survives substitution",
     "status": "EXECUTED", "outcome": "MEASUREMENT FAILED (retained as result)",
     "receipt": "research/g5-physical-denominator-v1 SUMMARY.json DATABASE_PARENT_SUFFICIENT: 1024x JSONL-vs-SQLite gap, 66us measured; raw counts are not elapsed time, RSS, energy, or whole-lifetime cost"},
    {"hostile_id": "H-MV-03", "target": "R (replication) coordinate claims",
     "attack": "promote an internal replay to replication evidence",
     "pass_condition": "refused by schema",
     "status": "EXECUTED", "outcome": "REFUSED (governance control held)",
     "receipt": "READINESS_SCHEMA_V1.json: internal replay caps R at 2; READINESS_MATRIX_V1 rows carry R=2 for all internal-replay atoms"},
    {"hostile_id": "H-MV-04", "target": "exploratory positives (morphology, GS-R2, E1-CGP)",
     "attack": "attempt confirmatory promotion without a fresh prospective freeze",
     "pass_condition": "refused; exploratory cap permanent",
     "status": "EXECUTED", "outcome": "REFUSED (cap enforced at 2 permanently)",
     "receipt": "research/ocm-morphology-zoo-v1/results/GS_R2_AGGREGATE.json + ATOM-MOR-01/02 rows: EXPLORATORY_ADAPTIVE caps at 2"},
    {"hostile_id": "H-MV-05", "target": "benchmark truth labels for E3+ studies",
     "attack": "independently recover the minimum sufficient cause and compare against the generator's planted cause",
     "pass_condition": "no E3+ study ships with generator-intent labels where intent is the target",
     "status": "EXECUTED", "outcome": "GATE PASSED (P1E3: 60/60 truth labels independently recovered on fresh-session taxonomy-disjoint families; generator intent audit-only and refused as cause)",
     "receipt": "issue #165 section 16: independent-authorship/benchmark-circularity gate; EXECUTED 2026-09-10 by P1E3: research/independent-authorship-gate-v1/P1E3_RESULT.md + P1E3_RECOVERY.json + P1E3_FAMILY_TABLE_V1.json (P1E3_AUTHORSHIP_FREEZE_V1, issue #277)"},
    {"hostile_id": "H-MV-06", "target": "gate/filter claims (adaptive refinement family)",
     "attack": "test the gate against a CLEAN baseline plus shuffle-equal-n null, never a degraded baseline",
     "pass_condition": "gate either shows edge over clean baseline or is rejected",
     "status": "EXECUTED", "outcome": "GATE REJECTED AT SCOPE (negative retained)",
     "receipt": "research/hsg-semantic-execution-v1/exact/results/D20_RESULTS.json: adaptive refinement loses to direct concrete search everywhere in pre-registered grid (ATOM-SEM-07, PR #283)"},
    {"hostile_id": "H-MV-07", "target": "evidence scores >=3 on any coordinate",
     "attack": "score an atom above 2 without a sha-bound artifact with declared evidence class",
     "pass_condition": "refused by scoring",
     "status": "EXECUTED", "outcome": "REFUSED (21 theorem atoms held at P=1 pending binding)",
     "receipt": "READINESS_MATRIX_V1.json: P gap 1->3 on 21 atoms; READINESS_SCHEMA_V1 sha+class rule; blocker B2-PARENT-BIND (BLOCKER_DAG_V1)"},
    {"hostile_id": "H-MV-08", "target": "absence claims (NO RESULT EXISTS atoms)",
     "attack": "re-verify each absence with a scope-justified search plus a control pattern that must match",
     "pass_condition": "absence claim survives control-verified search",
     "status": "EXECUTED", "outcome": "HELD (all NO-RESULT atoms carry control-verified search notes)",
     "receipt": "ATOM-MAQ-03/04, ATOM-SPX-01, ATOM-COD-01, ATOM-LNG-02 rows: filename sweeps with matching controls recorded in ATOM_REGISTRY_V1"},
    {"hostile_id": "H-MV-09", "target": "frozen-run contamination",
     "attack": "require prospective logging of every external cognitive input during frozen execution",
     "pass_condition": "ledger exists prospectively and every event is dispositioned",
     "status": "EXECUTED", "outcome": "LEDGER LIVE (own verdict negative and retained)",
     "receipt": "research/top-tier-atomic-closure-v1/EXTERNAL_COGNITIVE_INPUT_LEDGER.jsonl (TTAC-D5, prospective)"},
    {"hostile_id": "H-MV-10", "target": "prose exceeding evidence level",
     "attack": "read every shipped claim against its registered ceiling",
     "pass_condition": "no claim sentence exceeds member-atom ceilings",
     "status": "EXECUTED", "outcome": "ENFORCED (composition rule = min over load-bearing coordinates)",
     "receipt": "DECISIVE_CLAIM_REGISTRY_V1.json composition_rule + READINESS_SCHEMA_V1 claim_ceiling_rules"},
    {"hostile_id": "H-MV-11", "target": "finite theorem certificates (DC-04/DC-05 family)",
     "attack": "registered hostile worlds: block-merge/split refinements (H-T78a), reduct-image targets, negation-present population OW4N",
     "pass_condition": "certificate survives its registered hostiles or is bounded explicitly",
     "status": "EXECUTED", "outcome": "HELD WITH ONE MEASURED BOUNDARY (negation boundary empirical, CANNOT_CHECK_NEGATION_PRESENT)",
     "receipt": "research/hsg-semantic-execution-v1/exact/results/D17_RESULTS.json + D19_RESULTS.json (PR #275/#282)"},
    {"hostile_id": "H-MV-12", "target": "sparse relevant cognition k/N (DC-12)",
     "attack": "measure k(q,K_t) and N_t physically with index costs charged",
     "pass_condition": "a measured k/N artifact exists with full cost vector",
     "status": "DESIGNED_PENDING", "outcome": "NO MEASUREMENT EXISTS (the suite records its own unexecuted member)",
     "receipt": "ATOM-SPX-01: k/N unbound, zero measured artifacts, control-verified absence; also blocks DC-12 at current_min=1"},
]

for h in HOSTILES:
    assert set(h) >= {"hostile_id", "target", "attack", "pass_condition", "status", "outcome", "receipt"}, h["hostile_id"]

verdicts = Counter(h["outcome"].split(" ")[0] + "|" + h["status"] for h in HOSTILES)
suite = {
    "schema": "TTAC_MEASUREMENT_VALIDITY", "version": "V1", "d_step": "TTAC-D4", "owner_issue": 277,
    "built_utc": "2026-09-10",
    "matrix_ref": "READINESS_MATRIX_V1.json", "dag_ref": "BLOCKER_DAG_V1.json",
    "purpose": "hostile probes against the programme's own load-bearing measurements; a suite that passes everything is theater",
    "hostiles": HOSTILES,
    "self_test": {
        "at_least_one_real_failure_required": True,
        "real_failures_recorded": ["H-MV-02 (raw counts did not survive physical denominator)",
                                    "H-MV-01 (shuffle-null retracted a shipped headline)"],
        "unexecuted_members_admitted": ["H-MV-12 (k/N unbound)"],
        "since_executed": ["H-MV-05 (admitted pending at freeze; executed 2026-09-10 by P1E3, see hostiles[4])"],
    },
    "census": {"hostiles": len(HOSTILES),
               "executed": sum(1 for h in HOSTILES if h["status"] == "EXECUTED"),
               "designed_pending": sum(1 for h in HOSTILES if h["status"] == "DESIGNED_PENDING"),
               "by_outcome": dict(verdicts)},
    "non_final": "EXPLICITLY_NON_FINAL",
}
(BASE / "MEASUREMENT_VALIDITY_V1.json").write_text(json.dumps(suite, indent=1) + "\n")
print(f"hostiles={len(HOSTILES)} executed={suite['census']['executed']} pending={suite['census']['designed_pending']}")
for k, v in verdicts.items():
    print(f"  {k}: {v}")
print("VALIDATION OK")
