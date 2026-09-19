# -*- coding: utf-8 -*-
"""Build ISSUE_833_COMMENT_RECONCILIATION_V1.json -- the package's ONLY issue-facing artifact.

Schema GMI_ISSUE_RECONCILIATION_V2.  One replacement per frozen row AJ15_R1..R7 (the seven
unchecked rows of comment 5693954852 under the AJ15 anchor, byte-exact from
FREEZE_ROWS_V1.json and re-verified against the comment fetch in comment_fetches/).  Every
number in a `new` line is read from RESULT_V1.json, and each replacement carries citations
(receipt path + git blob sha + pinned field values) that ra1_citation_audit_v1.py verifies.

THIS PACKAGE NEVER EDITS THE ISSUE OR ITS COMMENTS; the orchestrator applies this file.

    python3 -I -B build_reconciliation_v1.py            # write
    python3 -I -B build_reconciliation_v1.py --check    # require byte equality with the committed file
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PKG = "gmi-833-aj15-flagship-experiment-v1"
COMMENT = 5693954852
ANCHOR = "### AJ15 — Flagship end-to-end falsification experiment — OPEN"


def _read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def blob_sha(path):
    data = _read_bytes(path)
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\x00")
    h.update(data)
    return h.hexdigest()


def pin(doc, paths):
    out = {}
    for p in paths:
        cur = doc
        for seg in p.split("."):
            cur = cur[int(seg)] if isinstance(cur, list) else cur[seg]
        out[p] = json.dumps(cur, sort_keys=True)
    return out


def build():
    rows = _load_json(os.path.join(HERE, "FREEZE_ROWS_V1.json"))
    result = _load_json(os.path.join(HERE, "RESULT_V1.json"))
    fetch_path = os.path.join(HERE, "comment_fetches", "%d.txt" % COMMENT)
    fetch = _read_bytes(fetch_path)
    fetch_sha = hashlib.sha256(fetch).hexdigest()
    pinned = rows["comment_fetches"][0]
    if fetch_sha != pinned["sha256"] or len(fetch) != pinned["bytes"]:
        raise SystemExit("comment fetch drifted from the freeze pin: %s/%d vs %s/%d" % (
            fetch_sha, len(fetch), pinned["sha256"], pinned["bytes"]))
    text = fetch.decode("utf-8")
    R = result["results"]
    fx1, fx2, fx3, fx4, fx6 = R["FX-1"], R["FX-2"], R["FX-3"], R["FX-4"], R["FX-6"]
    reg = fx1["regimes"]
    b2 = fx3["regimes"]
    d3 = b2["delay3"]
    rp = os.path.join(HERE, "RESULT_V1.json")
    rblob = blob_sha(rp)

    def cite(fields):
        return [{"package": PKG, "receipt_path": "research/%s/RESULT_V1.json" % PKG,
                 "blob_sha": rblob, "fields": pin(result, fields)}]

    ev = {
        "AJ15_R1": ("FX-1", "BOUNDED_UNIVERSE_ENUMERATED_END_TO_END",
                    "all %d presentations of B1 (%d operational classes, %s pair checks, atlas SHA-256 `%s…`) enumerated, every exact solver of each of the 5 regimes listed, and the frozen regime predictions `%s` on route A and `%s` on route B (`identity`/`not`/`const0` %d/%d, %d/%d, %d/%d exact solvers with a reachable-state-dependent output; `delay1`/`toggle` %d/%d, %d/%d)." % (
                        fx1["universe_B1_presentations"], fx1["operational_classes"], "{:,}".format(fx1["pair_checks"]), fx1["atlas_sha256"][:16],
                        fx1["regime_prediction_verdict_route_A"], fx1["regime_prediction_verdict_route_B"],
                        reg["identity"]["with_state_dependent_output"], reg["identity"]["exact_solvers"],
                        reg["not"]["with_state_dependent_output"], reg["not"]["exact_solvers"],
                        reg["const0"]["with_state_dependent_output"], reg["const0"]["exact_solvers"],
                        reg["delay1"]["with_state_dependent_output"], reg["delay1"]["exact_solvers"],
                        reg["toggle"]["with_state_dependent_output"], reg["toggle"]["exact_solvers"]),
                    ["results.FX-1.universe_B1_presentations", "results.FX-1.operational_classes", "results.FX-1.pair_checks",
                     "results.FX-1.atlas_sha256", "results.FX-1.regime_prediction_verdict_route_A",
                     "results.FX-1.regime_prediction_verdict_route_B", "results.FX-1.regimes"]),
        "AJ15_R2": ("FX-1 FX-6", "REGISTRY_HIDDEN_FROM_GENERATION_SEARCH_EVALUATION",
                    "the whole 11-family registry (blob `%s`) was hidden from generation, search and evaluation on both routes (`registry_read_in_blind_stage: %s`); the blind-source audit finds %d violations with planted recall %s and %d control hits where the vocabulary is permitted; the registry is read only by the post-hoc stage after `BLIND_OUTCOME_V1.json` exists (its SHA-256 `%s…` pinned); B1 was constructed at `%s` (%s), before the registry freeze `%s` (%s)." % (
                        fx6["registry_blob"], str(fx6["registry_read_in_blind_stage"]).lower(), fx6["source_audit_violations"],
                        fx6["source_audit_planted_recall"], sum(fx6["source_audit_control_hits"].values()),
                        fx6["blind_outcome_sha256_recorded_by_posthoc"][:16],
                        fx1["universe_constructed_before_registry_freeze"]["B1_construction_commit"][:8],
                        fx1["universe_constructed_before_registry_freeze"]["B1_construction_time"],
                        fx1["universe_constructed_before_registry_freeze"]["registry_freeze_commit"][:8],
                        fx1["universe_constructed_before_registry_freeze"]["registry_freeze_time"]),
                    ["results.FX-6.registry_blob", "results.FX-6.registry_read_in_blind_stage", "results.FX-6.source_audit_violations",
                     "results.FX-6.source_audit_planted_recall", "results.FX-6.source_audit_control_hits",
                     "results.FX-6.blind_outcome_sha256_recorded_by_posthoc", "results.FX-1.universe_constructed_before_registry_freeze"]),
        "AJ15_R3": ("FX-3 FX-4", "BLIND_RECOVERY_OR_HONEST_FAILURE_TERMINAL_LIVE",
                    "at B2 both implementations return `RECOVERED` for `identity`/`delay1`/`delay2` (S1 after %d/%d/%d evaluations, S2 with %d/%d/%d residual classes, every S1 solver certified on all words by route B) and `NOT_RECOVERED_AT_SCOPE` for `delay3` (S1: %s evaluations exhausted; S2: %d residual classes > 4 states) — the honest failure terminal exercised on a live regime; hostile H4 (budget 1) reports failure, never a fake success." % (
                        b2["identity"]["S1_evaluations"], b2["delay1"]["S1_evaluations"], b2["delay2"]["S1_evaluations"],
                        b2["identity"]["S2_residual_classes"], b2["delay1"]["S2_residual_classes"], b2["delay2"]["S2_residual_classes"],
                        "{:,}".format(d3["S1_evaluations"]), d3["S2_residual_classes"]),
                    ["results.FX-3.regimes", "results.FX-3.honest_failure_terminal_exercised_on", "results.FX-4.hostiles.H4"]),
        "AJ15_R4": ("FX-1 FX-4", "PREDICTED_ABSENT_REGIMES_REGISTERED_AND_OBSERVED_ABSENT",
                    "three memoryless-realizable regimes (`identity`, `not`, `const0`) were frozen as predicted-absent before the run and observed %d/%d, %d/%d, %d/%d exact solvers with a reachable-state-dependent output and %d/%d, %d/%d, %d/%d post-hoc fingerprint passes, against %d/%d and %d/%d in the two predicted-present regimes; null N1 fires the same test on %s random tables, so the zeros are regime properties and not a stuck test." % (
                        reg["identity"]["with_state_dependent_output"], reg["identity"]["exact_solvers"],
                        reg["not"]["with_state_dependent_output"], reg["not"]["exact_solvers"],
                        reg["const0"]["with_state_dependent_output"], reg["const0"]["exact_solvers"],
                        reg["identity"]["K02_fingerprint_passes_posthoc"], reg["identity"]["exact_solvers"],
                        reg["not"]["K02_fingerprint_passes_posthoc"], reg["not"]["exact_solvers"],
                        reg["const0"]["K02_fingerprint_passes_posthoc"], reg["const0"]["exact_solvers"],
                        reg["delay1"]["K02_fingerprint_passes_posthoc"], reg["delay1"]["exact_solvers"],
                        reg["toggle"]["K02_fingerprint_passes_posthoc"], reg["toggle"]["exact_solvers"],
                        fx4["N1_state_dependence_rate_random_B1"]),
                    ["results.FX-1.regimes", "results.FX-1.posthoc_agrees_with_frozen_prediction", "results.FX-4.N1_state_dependence_rate_random_B1"]),
        "AJ15_R5": ("FX-3", "REPEATED_AT_NON_ENUMERATED_SCALE_WITH_INDEPENDENT_IMPLEMENTATIONS",
                    "after the bounded `CONFIRMED`, the protocol was repeated at B2 (`8^8 = %s` presentations, `enumerated: %s`) with two independent implementations — S1 random-restart hill-climb (route A) and S2 residual right-congruence construction (route B) — agreeing on all four terminals with every S1 solver certified on all words by route B; scoped to independent implementations within one programme (`independent_team_replication_claimed: %s`)." % (
                        "{:,}".format(fx3["universe_B2_presentations"]), str(fx3["enumerated"]).lower(),
                        str(fx3["independent_team_replication_claimed"]).lower()),
                    ["results.FX-3.universe_B2_presentations", "results.FX-3.enumerated", "results.FX-3.independent_search_implementations",
                     "results.FX-3.independent_team_replication_claimed", "results.FX-3.regimes"]),
        "AJ15_R6": ("FX-2", "SAME_RUN_YIELDS_REGISTERED_RECOVERY_AND_UNKNOWN_CHANNEL_OUTPUTS",
                    "one run yields %d registered-fingerprint recoveries at B1 (plus `delay1`/`delay2` at B2) and %d exact solvers that match no registered fingerprint, placed in the UNKNOWN channel with `registered_family: null` and all %d parent-reduced (`PARENT_REDUCED_KNOWN`); `novel_form_claimed: %s`, replication gate `%s`." % (
                        fx2["registered_fingerprint_recoveries_B1"], fx2["unknown_channel_solvers_total"], fx2["unknown_parent_reduced_total"],
                        str(fx2["novel_form_claimed"]).lower(), fx2["novel_replication_gate"]),
                    ["results.FX-2.registered_fingerprint_recoveries_B1", "results.FX-2.unknown_channel_solvers_total",
                     "results.FX-2.unknown_parent_reduced_total", "results.FX-2.novel_form_claimed", "results.FX-2.novel_replication_gate"]),
        "AJ15_R7": ("FX-4", "FAILURE_WIRED_AS_DIRECT_FALSIFIER",
                    "the registered claim `%s` is wired so that any regime-prediction failure emits `verdict: FALSIFIED` and a non-zero exit; hostile H3 (inverted `identity` prediction) flips `CONFIRMED → FALSIFIED` (`falsifier_live: %s`), %d/%d hostiles are applicable and detected, and the exact chance of the observed outcome vector under null N2 is %s · %s = %s." % (
                        fx4["falsified_claim_under_H3"], str(fx4["falsifier_live"]).lower(),
                        fx4["hostiles_applicable_and_detected"], fx4["hostiles_total"],
                        fx4["N2_chance_B1"], fx4["N2_chance_B2"], fx4["N2_joint_chance"]),
                    ["results.FX-4.falsified_claim_under_H3", "results.FX-4.falsifier_live", "results.FX-4.hostiles_applicable_and_detected",
                     "results.FX-4.hostiles_total", "results.FX-4.N2_chance_B1", "results.FX-4.N2_chance_B2", "results.FX-4.N2_joint_chance"]),
    }
    reps = []
    for row in rows["rows"]:
        rid = row["id"]
        ids, token, sentence, fields = ev[rid]
        old = row["old"]
        if hashlib.sha256(old.encode("utf-8")).hexdigest() != row["old_sha256"]:
            raise SystemExit("row %s text does not match its frozen sha256" % rid)
        if text.count(old) != 1:
            raise SystemExit("row %s does not occur exactly once in the comment fetch (%d)" % (rid, text.count(old)))
        new = "- [x] " + old[len("- [ ] "):] + " — ✅ %s %s: %s" % (PKG, ids, sentence)
        reps.append({"id": rid, "comment_id": COMMENT, "anchor": ANCHOR, "old": old, "old_sha256": row["old_sha256"],
                     "new": new, "named_results": ids.split(), "row_meaning_token": token, "citations": cite(fields)})
    return {
        "schema": "GMI_ISSUE_RECONCILIATION_V2",
        "issue": 833,
        "package": PKG,
        "branch": "research/833-sec-aj15",
        "source_main": "f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5",
        "freeze_commit": "793e3548db7b06ee998b374ace49043c14070f67",
        "comment_id": COMMENT,
        "comment_fetch": {"path": "research/%s/comment_fetches/%d.txt" % (PKG, COMMENT), "bytes": len(fetch), "sha256": fetch_sha,
                          "note": "byte-exact gh api body fetch pinned in FREEZE_ROWS_V1.json; re-fetch immediately before applying"},
        "claim_ceiling": result["claim_ceiling"],
        "forbidden_promotions": result["forbidden_promotions"],
        "issue_body_edited_by_this_package": False,
        "comments_edited_by_this_package": False,
        "rows_deliberately_left_open": [],
        "neighboring_rows_earned": [],
        "replacements": reps,
    }


def main(argv=None):
    doc = build()
    text = json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    path = os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json")
    if "--check" in (argv or sys.argv[1:]):
        if _read_text(path) != text:
            sys.stderr.write("ISSUE_833_COMMENT_RECONCILIATION_V1.json differs from a live rebuild\n")
            return 1
        print("reconciliation matches a live rebuild (%d replacements)" % len(doc["replacements"]))
        return 0
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("wrote %d replacements" % len(doc["replacements"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
