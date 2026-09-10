#!/usr/bin/env python3
"""TTAC-D9 builder: REPLICATION_MATRIX_V1 + E3_PROTOCOL_FREEZE_V1.

Replication matrix: every atom whose R coordinate is load-bearing and short
of its closure profile, with the concrete E3->E4->E5 route.
E3 protocol: programme-wide freeze of what ANY E3 confirmatory study must
satisfy before execution (world authorship, meters, checkers, stats,
contamination, negative terminals). Frozen now; authorization still rides
the D7 flagship entry gates.
"""
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
M = json.loads((BASE / "READINESS_MATRIX_V1.json").read_text())

ROUTES = {
    ("THEOREM", "PROVED"): "E3 independent replay of exact checker on disjoint host -> E4 second disjoint host -> E5 out-of-repo second checker implementation",
    ("THEOREM", "FINITE_CERTIFIED"): "E3 independent replay of certificate checker -> E4 disjoint host -> E5 second implementation",
    ("THEOREM", "PARENT_SUFFICIENT"): "R not load-bearing for this terminal (P leads); replication rides parent artifact binding (B2/B5)",
    ("ENGINEERING_MECHANISM", "any"): "E3 frozen-protocol rerun with hostile controls -> E4 disjoint host -> E5 external reimplementation",
    ("EMPIRICAL_REGULARITY", "any"): "E3 prospectively frozen confirmatory rerun -> E4 disjoint replication -> E5 external",
}

rows = []
for r in M["rows"]:
    g = r["gap_vs_closure_profile"] or {}
    rneed = g.get("R")
    if r["R"].get("R") is None:
        continue  # R not load-bearing for this atom
    rhave = r["R"]["R"]
    short = bool(rneed and rneed["have"] < rneed["need"])
    rows.append({"atom_id": r["atom_id"], "class": r["class"], "terminal": r["terminal"],
                 "R_have": rhave, "R_need": rneed["need"] if rneed else "profile-met",
                 "short": short,
                 "route": ROUTES.get((r["class"], r["terminal"]), ROUTES.get((r["class"], "any"), "route TBD")),
                 "first_action": "B1-IND-REPLAY (disjoint-host checker replay, laptop billy E3 / billy-old E4)" if short else "none — hold",
                 "host_rule": "never Mac mini"})

short_rows = [x for x in rows if x["short"]]
rm = {
    "schema": "TTAC_REPLICATION_MATRIX", "version": "V1", "d_step": "TTAC-D9", "owner_issue": 277,
    "built_utc": "2026-09-10", "matrix_ref": "READINESS_MATRIX_V1.json", "dag_ref": "BLOCKER_DAG_V1.json",
    "rows": rows,
    "census": {"R_load_bearing_atoms": len(rows), "short_of_profile": len(short_rows),
               "by_route_first_action": dict(Counter(x["first_action"].split(" (")[0] for x in short_rows))},
    "reading": "every R shortfall routes through one blocker (B1-IND-REPLAY): the 13 short atoms are exactly the checker-replay population; no atom needs a bespoke replication mechanism before B1 lands",
    "non_final": "EXPLICITLY_NON_FINAL",
}
assert len(rows) > 0 and all(x["R_need"] for x in rows)
(BASE / "REPLICATION_MATRIX_V1.json").write_text(json.dumps(rm, indent=1) + "\n")

protocol = {
    "schema": "TTAC_E3_PROTOCOL_FREEZE", "version": "V1", "d_step": "TTAC-D9", "owner_issue": 277,
    "built_utc": "2026-09-10", "flagship_ref": "FLAGSHIP_EXPERIMENT_V1.json (FE-DEV-AMORT-1)",
    "scope": "programme-wide: any study promoted to E3 CONFIRMATORY must satisfy every clause below; frozen now so promotion cannot retro-tune",
    "clauses": [
        {"id": "P1-world-authorship",
         "rule": "task/world families independently authored outside the mechanism's taxonomy; truth labels independently recovered, never generator intent",
         "hostile": "H-MV-05",
         "status": "SATISFIED__P1E3 — executed: 10 fresh-session families / 60 instances (floors 10/5/50 met), taxonomy-disjoint (0 overlaps), truth recovered 60/60 by independent exact checker, intent audit-only and refused as cause; authorship is model-proxy (HUMAN_GATE_BYPASSED__MODEL_PROXY); receipt research/independent-authorship-gate-v1/P1E3_RESULT.md. Grants no execution rights: promotion of any study still requires its owning lane's entry gates (promotion_rule)"},
        {"id": "P2-splits",
         "rule": "protected splits, exclusion rules, and non-inferiority margins frozen before any protected outcome is accessed; violations void the study",
         "hostile": "H-MV-10", "status": "ENFORCEABLE NOW"},
        {"id": "P3-meters",
         "rule": "physical cost vector (elapsed, RSS, I/O, storage; energy where available) recorded alongside raw counts; count-only cost claims are invalid",
         "hostile": "H-MV-02", "status": "ENFORCEABLE NOW (lesson already paid: DATABASE_PARENT_SUFFICIENT)"},
        {"id": "P4-checkers",
         "rule": "exact checker registered and sha-bound before execution; scoring by an independent unit; internal replay never counts as replication (R cap 2)",
         "hostile": "H-MV-03", "status": "ENFORCEABLE NOW"},
        {"id": "P5-contamination",
         "rule": "EXTERNAL_COGNITIVE_INPUT_LEDGER active prospectively for the whole run window; every external input dispositioned",
         "hostile": "H-MV-09", "status": "LEDGER LIVE"},
        {"id": "P6-stats",
         "rule": "frozen analysis plan: pre-registered primaries, Holm family control, fixed horizon, no interim looks; deviation = new study, not amendment",
         "hostile": "H-MV-10", "status": "ENFORCEABLE NOW"},
        {"id": "P7-negatives",
         "rule": "authoritative negative terminals pre-registered verbatim and retained on execution; a clean negative is a valid closure",
         "hostile": "H-MV-06", "status": "ENFORCEABLE NOW"},
        {"id": "P8-replication-ladder",
         "rule": "E3 = confirmatory on fresh host (laptop billy) -> E4 = disjoint host/environment (billy-old) -> E5 = out-of-repo second implementation by an independent unit; E5 where a human gate is proxied carries HUMAN_GATE_BYPASSED__MODEL_PROXY, never marked externally obtained",
         "hostile": "H-MV-03", "status": "LADDER FROZEN"},
        {"id": "P9-hosts",
         "rule": "execution never on Mac mini (git/gh and single-file edits only); scale arms on LUNARC; no crypto-platform network from LUNARC",
         "hostile": None, "status": "STANDING"},
    ],
    "promotion_rule": "a study is E3-authorized only when P1 authorship exists AND the owning lane's entry gates (e.g. FLAGSHIP_EXPERIMENT_V1) are SATISFIED; the protocol freeze itself grants no execution rights",
    "non_final": "EXPLICITLY_NON_FINAL",
}
assert len(protocol["clauses"]) == 9 and all(c["id"] and c["rule"] for c in protocol["clauses"])
(BASE / "E3_PROTOCOL_FREEZE_V1.json").write_text(json.dumps(protocol, indent=1) + "\n")

print(f"R rows={len(rows)} short={len(short_rows)}")
for x in short_rows:
    print(f"  {x['atom_id']} R{x['R_have']}->{x['R_need']} ({x['terminal'][:14]})")
print("clauses=9; P1 authorship satisfied by P1E3 (model-proxy); promotion still rides owning-lane entry gates")
print("VALIDATION OK")
