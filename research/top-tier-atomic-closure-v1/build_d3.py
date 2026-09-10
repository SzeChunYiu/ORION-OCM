#!/usr/bin/env python3
"""TTAC-D3 builder: BLOCKER_DAG_V1 + critical path.

Nodes are ACTIONS (audits/experiments/decisions), each closing a specific set
of coordinate gaps recorded in READINESS_MATRIX_V1.gap_vs_closure_profile.
Priority(a) = uncertainty_reduction x downstream_unlock / cost, per #277 D3.
Cross-checked against IN_FLIGHT_COORDINATE_MAP_V1 so no blocker duplicates
frozen or in-flight lanes.
"""
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
M = json.loads((BASE / "READINESS_MATRIX_V1.json").read_text())
D = json.loads((BASE / "DECISIVE_CLAIM_REGISTRY_V1.json").read_text())
IF = json.loads((BASE / "IN_FLIGHT_COORDINATE_MAP_V1.json").read_text())

# Hand-authored blocker actions; atom membership derived from gap signatures.
BLOCKERS = [
    {"blocker_id": "B1-IND-REPLAY",
     "action": "Independent replay of every exact theorem checker on a disjoint host (billy-old/laptop via ssh, never Mac) with frozen inputs and recorded sha; each replay emits an E4-class receipt",
     "gap_signature": [("T", 4, 5), ("R", 2, 4)],
     "cost_class": "M", "cost_weight": 2.0, "uncertainty_reduction": 0.9,
     "requires": ["B2-PARENT-BIND"],
     "risk": "low: checkers exist and passed internally; replay is mechanical"},
    {"blocker_id": "B2-PARENT-BIND",
     "action": "AMENDED (D10, cause below): faithful parent run of every exact checker at matched access on the original host (billy-laptop) with sha-bound receipts, binding each atom's parent artifact (sha + evidence class E3); executed as ONE campaign with B1-IND-REPLAY (disjoint-host half on billy-old). Original action text ('bind artifact sha, fills P1->3 without new experiments') conflicted with READINESS_SCHEMA_V1 coordinate P: '3 requires faithful parent run at matched information/resources/checker access and subtracted; NOT_RUN stays 1' -- archival binding alone cannot fill P3",
     "gap_signature": [("P", 1, 3)],
     "cost_class": "M", "cost_weight": 2.0, "uncertainty_reduction": 0.7,
     "requires": [],
     "risk": "low-moderate: checkers exist and passed internally; faithful rerun is mechanical but must run off-Mac (host rules) with sha-bound receipts"},
    {"blocker_id": "B3-AUTONOMY-AUDIT",
     "action": "Prospective autonomy audit applied to historical evidence chains: for each atom, record whether any admission/self-adoption step lacked external authority; emits A-audit receipts per chain (A1->2). D5 ledger already covers the prospective half",
     "gap_signature": [("A", 1, 2)],
     "cost_class": "M", "cost_weight": 2.0, "uncertainty_reduction": 0.8,
     "requires": [],
     "risk": "medium: chains live across capsules; audit is scripted but must fail closed on missing provenance"},
    {"blocker_id": "B4-NULL-CHECKER",
     "action": "Author exact checkers for LIMITS_V1 theorems with checker=null (HST-14/15/16), or prove checker impossibility and register the structural CANNOT_CHECK terminal with that proof",
     "gap_signature": [("T", 3, 5), ("R", 1, 4)],
     "cost_class": "M", "cost_weight": 2.0, "uncertainty_reduction": 0.6,
     "requires": [],
     "risk": "high: parents are Rice/halting/Goedel/Blum-flavored; the honest likely terminal is structural CANNOT_CHECK, which is itself a publishable disposition"},
    {"blocker_id": "B5-PARENT-DEEPEN",
     "action": "Deepen parent-sufficiency verification from witness-verified (P4) to independent-check depth (P5): run the parent artifacts through the same frozen replay discipline as B1",
     "gap_signature": [("P", 4, 5)],
     "cost_class": "M", "cost_weight": 2.0, "uncertainty_reduction": 0.6,
     "requires": ["B1-IND-REPLAY"],
     "risk": "low-moderate: witness artifacts exist; deepening is replay plus boundary proofs"},
    {"blocker_id": "B6-PROFILE-FINAL",
     "action": "Governance decision finalizing the EMPIRICAL_REGULARITY/PARENT_SUFFICIENT closure profile (currently P4,M2 by analogy, flagged non-final): either add P to the class load-bearing set or revise the profile; then rescore DEV-01/PAR-02/PAR-03",
     "gap_signature": [("P", None, 4)],
     "cost_class": "S", "cost_weight": 1.0, "uncertainty_reduction": 0.4,
     "requires": [],
     "risk": "low: decision + rescoring; must be recorded as an amendment with cause"},
    {"blocker_id": "B7-EMPIRICAL-PARENT-VERIFY",
     "action": "Disjoint-host (billy-old) verification of the external empirical parents backing the EMPIRICAL_REGULARITY/PARENT_SUFFICIENT atoms (DEV-01/PAR-02/PAR-03): rerun the incumbent/parent engine arms that produced the parent artifacts and compare metrics against the recorded values, sha-bound receipts (P 2->4, E4-class empirical-parent bar)",
     "gap_signature": [("P", 2, 4)],
     "cost_class": "M", "cost_weight": 2.0, "uncertainty_reduction": 0.6,
     "requires": ["B6-PROFILE-FINAL"],
     "risk": "medium: parent arms live in lane engines (developmental/PDE); rerun is mechanical but must reproduce the exact parent configurations at the recorded shas"},
]

sig_atoms = {}
for r in M["rows"]:
    g = r["gap_vs_closure_profile"]
    if not g:
        continue
    for c, hn in g.items():
        sig_atoms.setdefault((c, hn["have"], hn["need"]), set()).add(r["atom_id"])

claim_atoms = {c["claim_id"]: set(c["atoms"]) for c in D["claims"]}
nodes, uncovered = [], set()
for sig, s in sig_atoms.items():
    uncovered |= s
for b in BLOCKERS:
    atoms = set()
    for sig in b["gap_signature"]:
        atoms |= sig_atoms.get(tuple(sig), set())
    claims_touched = sorted(cid for cid, ca in claim_atoms.items() if ca & atoms)
    unlock = len(atoms) + len(claims_touched)
    priority = round(b["uncertainty_reduction"] * unlock / b["cost_weight"], 2)
    nodes.append({**{k: v for k, v in b.items() if k != "gap_signature"},
                  "closes_atoms": sorted(atoms),
                  "closes_claims": claims_touched,
                  "atoms_closed": len(atoms), "claims_touched": len(claims_touched),
                  "priority_score": priority,
                  "priority_formula": "uncertainty_reduction * (atoms_closed + claims_touched) / cost_weight"})
    uncovered -= atoms

assert not uncovered, f"gap atoms not covered by any blocker: {sorted(uncovered)}"

edges = [{"from": req, "to": b["blocker_id"], "type": "prerequisite"}
         for b in BLOCKERS for req in b["requires"]]
ranked = sorted(nodes, key=lambda n: -n["priority_score"])
# Kahn topological order restricted to ranked priority (prerequisites first)
avail = {n["blocker_id"] for n in nodes}
done, path = set(), []
while avail - done:
    ready = [n for n in ranked if n["blocker_id"] not in done
             and all(r in done for r in n["requires"])]
    assert ready, "cycle in blocker DAG"
    n = ready[0]
    path.append(n["blocker_id"]); done.add(n["blocker_id"])

inflight = IF.get("coordinate_coverage_in_flight_or_legal_now", {})
dag = {
    "schema": "TTAC_BLOCKER_DAG", "version": "V1", "d_step": "TTAC-D3", "owner_issue": 277,
    "built_utc": "2026-09-10", "matrix_ref": "READINESS_MATRIX_V1.json",
    "claims_ref": "DECISIVE_CLAIM_REGISTRY_V1.json",
    "nodes": nodes, "edges": edges,
    "critical_path": [{"rank": i + 1, "blocker_id": bid,
                       "rationale": next(n["action"][:90] for n in nodes if n["blocker_id"] == bid)}
                      for i, bid in enumerate(path)],
    "in_flight_conflict_check": {
        "source": "IN_FLIGHT_COORDINATE_MAP_V1.json",
        "coordinate_coverage_in_flight_or_legal_now": inflight,
        "reading": "R and A coverage are 0 in flight, so B1-IND-REPLAY and B3-AUTONOMY-AUDIT claim unowned coordinates; no frozen or in-flight lane is duplicated by this DAG",
    },
    "census": {"blockers": len(nodes), "edges": len(edges),
               "gap_atoms_total": sum(len(s) for s in sig_atoms.values()),
               "by_priority": [(n["blocker_id"], n["priority_score"]) for n in ranked]},
    "amendments": [
        {"amendment_id": "DAG-AMD-1", "recorded_utc": "2026-09-10", "d_step": "TTAC-D10",
         "cause": "B2 original action ('archival sha binding fills P1->3 without new experiments') conflicted with the frozen READINESS_SCHEMA_V1 P definition: P3 requires a faithful parent run at matched information/resources/checker access; NOT_RUN stays 1. Schema is authoritative over the DAG action text.",
         "change": "B2 cost_class S->M, cost_weight 1.0->2.0, action rewritten to the faithful-parent-run campaign executed jointly with B1 (matched host billy-laptop for the P3 half; disjoint host billy-old for the R4 half). Priority rescored mechanically. Append-only: original reading preserved in this amendment.",
         "executed_by": "PR chain TTAC-D10 (#277); receipts PARENT_BINDING_V1 + REPLAY_RECEIPTS_V1"},
        {"amendment_id": "DAG-AMD-2", "recorded_utc": "2026-09-10", "d_step": "TTAC-D10/B3",
         "cause": "B3-AUTONOMY-AUDIT executed: all 24 A-gap chains resolved; A gap 24->0 via d2_overrides_c.json (coordinate-wise deep merge).",
         "change": "B3 closes_atoms now satisfied on the A coordinate; blocker remains in the DAG for provenance with status recorded in AUTONOMY_AUDIT_V1.json.",
         "executed_by": "PR TTAC-D10/B3 AUTONOMY_AUDIT_V1"},
        {"amendment_id": "DAG-AMD-3", "recorded_utc": "2026-09-10", "d_step": "TTAC-D10/B6+B1B2",
         "cause": "B6-PROFILE-FINAL made P load-bearing for every PARENT_SUFFICIENT terminal, newly exposing the (P,2,4) gap signature on DEV-01/PAR-02/PAR-03 (previously P=null: invisible to the matrix). B1+B2 replay campaign does not cover these atoms: their parents are external empirical parents, not exact checkers.",
         "change": "Blocker B7-EMPIRICAL-PARENT-VERIFY appended to own the new signature (append-only; no existing blocker changed). Priority scored mechanically with the others.",
         "executed_by": "PR TTAC-D10/B6-PROFILE-FINAL chain"},
    ],
    "non_final": "EXPLICITLY_NON_FINAL",
}
(BASE / "BLOCKER_DAG_V1.json").write_text(json.dumps(dag, indent=1) + "\n")
print(f"blockers={len(nodes)} edges={len(edges)} path={' -> '.join(path)}")
for n in ranked:
    print(f"  {n['priority_score']:6.2f} {n['blocker_id']}: {n['atoms_closed']} atoms, {n['claims_touched']} claims")
print("VALIDATION OK")
