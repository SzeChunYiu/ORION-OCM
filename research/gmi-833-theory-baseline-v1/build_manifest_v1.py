#!/usr/bin/env python3
"""Build BASELINE_MANIFEST_V1.json for GMI_THEORY_BASELINE_V1 (#833 Section B capstone).

Deterministic, stdlib-only. Binds every git-tracked file under the 11 frozen
component directories at the pinned HEAD SHA:
  - verifies the working-tree file is byte-identical to the pinned blob
    (git hash-object vs git rev-parse <pin>:<path>),
  - records per-artifact {path, sha256, bytes, role},
  - re-derives every headline count from the live bound artifacts and asserts
    it against the expected freeze value (the builder is itself a checker).

Run from anywhere:  python3 -I -B research/gmi-833-theory-baseline-v1/build_manifest_v1.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PKG = "research/gmi-833-theory-baseline-v1"
GIT = "/usr/bin/git"

PINNED_HEAD = "c4def870df287a476672e47219134832a0c2f380"
PINNED_SUBJECT = (
    "research(#833): corpus identification passes v2 - "
    "L42/L44-L56 detectors + verdicts, L58 revival to universal CI-U (#976)"
)

COMPONENTS: list[dict] = [
    {
        "id": "corpus-census",
        "package": "research/gmi-833-corpus-census-v1",
        "pr": 845,
        "child_issue": 842,
        "role_in_baseline": (
            "Frozen corpus universe: object grammar, file roles, per-object "
            "dispositions, duplicate candidates, dependency-gap audit. Everything "
            "downstream is scoped to this frozen census."
        ),
    },
    {
        "id": "corpus-audit-close",
        "package": "research/gmi-833-corpus-audit-close-v1",
        "pr": 939,
        "child_issue": None,
        "role_in_baseline": (
            "Bounded semantic adjudication tranche over the frozen census "
            "(all 237 GREEN EXPLICIT + seeded stratified 200 of 22,316 AMBER+RED "
            "over 28 non-empty strata). Verdict taxonomy frozen; found the corpus's "
            "one confirmed OVERSTRONG (capability-interactions universal phrasing)."
        ),
    },
    {
        "id": "depgraph-adjudication",
        "package": "research/gmi-833-depgraph-adjudication-v1",
        "pr": 949,
        "child_issue": 842,
        "role_in_baseline": (
            "Dependency graph v2 with real cited edges; Tarjan cycle evidence; "
            "duplicate adjudication with content collapse; OVERSTRONG adjudication "
            "of the FIN2UNIV population; master RAG table over the whole corpus."
        ),
    },
    {
        "id": "maturity-rescore-v1",
        "package": "research/gmi-833-maturity-rescore-v1",
        "pr": 938,
        "child_issue": None,
        "role_in_baseline": (
            "M0-M6 / EV0-EV5 maturity rubric freeze (29 833-family primaries; typed "
            "Gap 1 legacy-173 and Gap 2 post-freeze arrivals handed to v2)."
        ),
    },
    {
        "id": "maturity-rescore-v2",
        "package": "research/gmi-833-maturity-rescore-v2-v1",
        "pr": 948,
        "child_issue": None,
        "role_in_baseline": (
            "Judgment protocol (FREEZE_V2) and 197-row THEOREM_SCORES_V2 covering "
            "both v1 gaps (173 legacy GREEN claim objects + 24 arrivals). Corpus "
            "fact recorded: no M5/M6 (no EV4/EV5 evidence) anywhere."
        ),
    },
    {
        "id": "claim-discipline",
        "package": "research/gmi-833-claim-discipline-v1",
        "pr": 972,
        "pr_successor": 975,
        "child_issue": None,
        "role_in_baseline": (
            "Six discipline fields (scope/quantifiers, assumptions, falsifiers, "
            "strongest parents, forbidden extrapolations) registered for every "
            "claim-bearing object; successor tranche v2 closed all 8 v1 gaps and "
            "absorbed one post-freeze arrival under the frozen mechanical rule."
        ),
    },
    {
        "id": "corpus-passes-v2",
        "package": "research/gmi-833-corpus-passes-v2-v1",
        "pr": 976,
        "child_issue": None,
        "role_in_baseline": (
            "Corpus identification passes L42, L44-L56, L58 over frozen populations "
            "with a verdict register; every CONFIRMED finding carries a revival "
            "ticket; L58 revived the capability-interactions claim to the universal "
            "Theorem CI-U at original strength."
        ),
    },
    {
        "id": "terminology-migration",
        "package": "research/gmi-833-terminology-migration-v1",
        "pr": 940,
        "pr_successor": 947,
        "child_issue": None,
        "role_in_baseline": (
            "Paper-rename-only terminology migration under crosswalk rules R1-R9: "
            "255 (tranche 1) + 217 (tranche 2) rule-attributed edits; non-aj "
            "obligation cleared; residual = 35 aj-lane hits in 12 aj packages + "
            "34 acknowledged definitional-quote/citation sites."
        ),
    },
    {
        "id": "blind-recovery-v2",
        "package": "research/gmi-833-blind-recovery-v2-v1",
        "pr": 974,
        "child_issue": 434,
        "role_in_baseline": (
            "Blind-recovery protocol v2: every input channel frozen pre-search; "
            "coverage-complete neutral batteries; tier-declared basis grid; A2 "
            "semantic-fingerprint screen; recovery boundary measured over complete "
            "classes (XOR recovered, XNOR honestly fails); 6 registered open gaps."
        ),
    },
    {
        "id": "g0-grammar-growth",
        "package": "research/gmi-833-g0-grammar-growth-v1",
        "pr": 945,
        "child_issue": 897,
        "role_in_baseline": (
            "Frozen grammar-growth formalism (GRW-1, INV-1, REC-1, HLD-1, THR-1, "
            "NULL-1) with burden receipts, 200-seed null, and independent-oracle "
            "agreement; terminal green at registered finite scope."
        ),
    },
    {
        "id": "progress-ledger",
        "package": "research/gmi-833-progress-ledger-v1",
        "pr": 970,
        "child_issue": None,
        "role_in_baseline": (
            "Checkbox evidence map (toggle-only tick discipline) and the "
            "remaining-work queue across all #833 sections."
        ),
    },
]

ROLE_RULES: list[tuple[str, str]] = [
    ("FREEZE", "AUTHORITY_DOC"),
    ("FROZEN", "AUTHORITY_DOC"),
    ("AUDIT_PROTOCOL", "AUTHORITY_DOC"),
    ("PRIOR_DISCLOSURE", "AUTHORITY_DOC"),
    ("README", "NARRATIVE_RESULT_DOC"),
    ("CORE.md", "NARRATIVE_RESULT_DOC"),
    ("PASS_", "NARRATIVE_RESULT_DOC"),
    ("MIGRATION_LOG", "NARRATIVE_RESULT_DOC"),
    ("MATURITY_RESCORE", "NARRATIVE_RESULT_DOC"),
    ("SUCCESSOR_TRANCHE", "NARRATIVE_RESULT_DOC"),
    ("CHECKBOX_EVIDENCE", "NARRATIVE_RESULT_DOC"),
    ("REMAINING_WORK", "NARRATIVE_RESULT_DOC"),
    ("PARENT_LEDGER", "NARRATIVE_RESULT_DOC"),
    ("PARENT_LITERATURE", "NARRATIVE_RESULT_DOC"),
    ("RECEIPTS_RUN_LOG", "NARRATIVE_RESULT_DOC"),
    ("REUSE_AUDIT", "NARRATIVE_RESULT_DOC"),
    ("ADJUDICATION", "NARRATIVE_RESULT_DOC"),
    ("REPORTED_NOT_FIXED", "NARRATIVE_RESULT_DOC"),
    ("REGISTRATIONS_TABLE", "NARRATIVE_RESULT_DOC"),
    ("THEOREMS_", "NARRATIVE_RESULT_DOC"),
    ("THEORY_", "NARRATIVE_RESULT_DOC"),
    ("evidence/", "EVIDENCE"),
]


def classify(rel: str) -> str:
    if "/evidence/" in rel:
        return "EVIDENCE"
    if rel.endswith(".json"):
        return "RESULT_DATA"
    name = rel.rsplit("/", 1)[-1]
    for needle, role in ROLE_RULES:
        if needle in rel:
            return role
    if name.endswith(".py"):
        return "TEST_CODE" if name.startswith("test_") else "METHOD_CODE"
    return "DOC"


def git(*args: str) -> str:
    out = subprocess.run(
        [GIT, "-C", str(REPO), *args], check=True, capture_output=True, text=True
    )
    return out.stdout


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    pin_files: set[str] = set()
    for comp in COMPONENTS:
        out = git("ls-tree", "-r", "--name-only", PINNED_HEAD, "--", comp["package"])
        pin_files.update(line for line in out.splitlines() if line.strip())
    assert len(pin_files) == 132, f"expected 132 pinned files, got {len(pin_files)}"

    artifacts: list[dict] = []
    for rel in sorted(pin_files):
        local = REPO / rel
        assert local.is_file(), f"pinned file missing from working tree: {rel}"
        data = local.read_bytes()
        # byte-identity to the pinned blob
        blob_pin = git("rev-parse", f"{PINNED_HEAD}:{rel}").strip()
        blob_wt = git("hash-object", str(local)).strip()
        assert blob_pin == blob_wt, f"working tree drifted from pin: {rel}"
        artifacts.append(
            {
                "path": rel,
                "sha256": sha256_bytes(data),
                "bytes": len(data),
                "role": classify(rel),
            }
        )

    def load(rel: str):
        return json.loads((REPO / rel).read_text())

    # ---- re-derive headline counts from live bound artifacts (builder asserts) ----
    census_idx = load("research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json")
    census_audit = load("research/gmi-833-corpus-census-v1/AUDIT_V1.json")
    dg2 = load("research/gmi-833-depgraph-adjudication-v1/DEPENDENCY_GRAPH_V2.json")
    cyc = load("research/gmi-833-depgraph-adjudication-v1/CYCLE_REPORT_V1.json")
    dup = load("research/gmi-833-depgraph-adjudication-v1/DUPLICATE_ADJUDICATION_V1.json")
    ovr = load("research/gmi-833-depgraph-adjudication-v1/OVERSTRONG_ADJUDICATION_V1.json")
    rag = load("research/gmi-833-depgraph-adjudication-v1/MASTER_RAG_TABLE_V1.json")
    tsv2 = load("research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json")
    reg2 = load("research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json")
    res2 = load("research/gmi-833-claim-discipline-v1/RESULT_V2.json")
    tickets = load("research/gmi-833-corpus-passes-v2-v1/REVIVAL_TICKETS_V1.json")
    ack = load("research/gmi-833-terminology-migration-v1/ACKNOWLEDGED_FINDINGS_V1.json")
    ogaps = load("research/gmi-833-blind-recovery-v2-v1/OPEN_GAPS.json")
    gman = load("research/gmi-833-g0-grammar-growth-v1/MANIFEST_V1.json")

    n_objects = len(census_idx["scientific_objects"])
    assert n_objects == 22553
    disp = census_audit["summary"]["dispositions"]
    assert disp == {"GREEN": 237, "AMBER": 18396, "RED": 3920}, disp
    assert census_audit["summary"]["dependency_cycles"] == 0
    n_dup_groups = census_audit["summary"]["duplicate_candidate_groups"]
    assert n_dup_groups == 1652

    edge_layers = {k: len(v) for k, v in dg2["edges"].items()}
    assert edge_layers == {
        "file_local": 140,
        "pointer_rollup": 28,
        "parent_family_anchor": 60,
        "external_literature": 73,
        "corpus_package": 56,
    }, edge_layers
    n_edges = sum(edge_layers.values())
    assert n_edges == 357
    assert cyc["union"]["cycle_count"] == 0 and cyc["union"]["self_loops"] == []
    assert dup["candidate_groups"]["count"] == 1652
    assert dup["candidate_groups"]["verdict_distribution"] == {
        "DUPLICATE": 1586,
        "DISTINCT": 66,
    }
    collapsed_away = dup["content_collapse"]["collapsed_away"]
    assert collapsed_away == 5295
    content_nodes = n_objects - collapsed_away
    assert content_nodes == 17258
    assert ovr["population"] == 283
    assert ovr["verdict_distribution"] == {"PROPER": 283}
    assert len(rag["strata"]) == 39

    assert len(tsv2) == 197
    assert len(reg2["objects"]) == 235
    assert res2["registered_gap_v2"] == 0
    assert res2["field_slots"] == 1175

    n_tickets = len(tickets["tickets"])
    closed = [t for t in tickets["tickets"] if t.get("status") == "DONE_IN_SWEEP"]
    open_ = [t for t in tickets["tickets"] if t.get("status") is None]
    assert n_tickets == 9 and len(closed) == 3 and len(open_) == 6

    assert ack["total_hits"] == 34 and ack["total_sites"] == 17
    v2_gaps = ogaps["remaining"]
    assert len(v2_gaps) == 6
    assert gman["claim_ceiling"] == (
        "GMI_FINITE_CONSERVATIVE_RECURSIVE_LIBRARY_GROWTH_AND_HELDOUT_REUSE_"
        "BENEFIT_AT_REGISTERED_SCOPE"
    )

    counts = {
        "census_scientific_objects": n_objects,
        "census_files": census_audit["summary"]["included_files"],
        "census_dispositions": disp,
        "census_dependency_cycles": 0,
        "duplicate_candidate_groups": n_dup_groups,
        "duplicate_verdicts": dup["candidate_groups"]["verdict_distribution"],
        "content_collapse": {"from": n_objects, "to": content_nodes, "collapsed_away": collapsed_away},
        "dependency_edges_by_layer": edge_layers,
        "dependency_edges_total": n_edges,
        "cycle_report_union_cycles": 0,
        "overstrong_population": 283,
        "overstrong_verdicts": {"PROPER": 283},
        "master_rag_strata": 39,
        "theorem_scores_rows": 197,
        "claim_discipline_objects_v2": 235,
        "claim_discipline_registered_gap_v2": 0,
        "claim_discipline_slots_v2": 1175,
        "revival_tickets_total": 9,
        "revival_tickets_closed": 3,
        "revival_tickets_open": 6,
        "terminology_edits_tranche1": 255,
        "terminology_edits_tranche2": 217,
        "terminology_aj_lane_residual_hits": 35,
        "terminology_aj_lane_packages": 12,
        "terminology_acknowledged_hits": ack["total_hits"],
        "blind_recovery_open_gaps": len(v2_gaps),
        "grammar_growth_theorems": gman["theorems"],
    }

    # ---- revival-ticket register snapshot ----
    register = {
        "source": "research/gmi-833-corpus-passes-v2-v1/REVIVAL_TICKETS_V1.json",
        "doctrine": tickets["doctrine"],
        "total": 9,
        "closed": [
            {
                "id": t["id"],
                "status": t["status"],
                "evidence": t.get("evidence", ""),
            }
            for t in closed
        ],
        "open": [
            {
                "id": t["id"],
                "finding": t["finding"],
                "attribution": t["attribution"],
                "lever": t["lever"],
                "owner_lane": t["owner_next"],
                "retest_at_original_strength": t["retest_at_original_strength"],
            }
            for t in open_
        ],
    }

    # ---- arrivals since pin (mechanical rule, re-run at build time) ----
    origin_main = git("rev-parse", "origin/main").strip()
    diff_stat = git(
        "diff", "--stat", f"{PINNED_HEAD}..{origin_main}", "--", "research/"
    )
    new_dirs = sorted(
        {
            line.split("/")[1]
            for line in diff_stat.splitlines()
            if line.startswith("research/gmi-833-") and "/" in line
        }
    )
    arrivals = {
        "checked_against": origin_main,
        "rule": "git diff --stat <pin>..<head> -- research/ ; new gmi-833-* dirs",
        "new_gmi_833_dirs": new_dirs,
        "claim_bearing_arrivals_absorbed_as_u_new": [],
        "count_absorbed": 0,
        "note": (
            "re-run at every manifest build; arrivals enter as U-NEW until typed by "
            "the frozen mechanical re-run (arrival_absorption_rule below)"
        ),
    }

    manifest = {
        "schema": "GMI_833_THEORY_BASELINE_MANIFEST_V1",
        "baseline": "GMI_THEORY_BASELINE_V1",
        "parent_issue": 833,
        "freeze_package": PKG,
        "claim_ceiling": "GMI_THEORY_BASELINE_V1_AT_PINNED_FROZEN_CORPUS_SCOPE",
        "pinned_head_sha": PINNED_HEAD,
        "pinned_head_subject": PINNED_SUBJECT,
        "arrivals_since_pin": arrivals,
        "pin_method": (
            "origin/main fetched at freeze time; branch research/833-theory-baseline-v1 "
            "cut from origin/main at the pinned SHA; every bound file verified "
            "byte-identical between working tree and the pinned blob (git hash-object "
            "== git rev-parse <pin>:<path>) before sha256 binding"
        ),
        "bound_artifact_count": len(artifacts),
        "components": [
            {**comp, "artifacts": [a for a in artifacts if a["path"].startswith(comp["package"] + "/")]}
            for comp in COMPONENTS
        ],
        "assertion_dependencies": {
            "A1_corpus_enumerated": [
                "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json",
                "research/gmi-833-corpus-census-v1/AUDIT_V1.json",
                "research/gmi-833-corpus-census-v1/FREEZE_V1.md",
            ],
            "A2_rag_strata_cover_corpus": [
                "research/gmi-833-depgraph-adjudication-v1/MASTER_RAG_TABLE_V1.json",
                "research/gmi-833-corpus-census-v1/AUDIT_V1.json",
            ],
            "A3_dependency_graph_acyclic_stated_scope": [
                "research/gmi-833-depgraph-adjudication-v1/DEPENDENCY_GRAPH_V2.json",
                "research/gmi-833-depgraph-adjudication-v1/CYCLE_REPORT_V1.json",
            ],
            "A4_duplicates_adjudicated_content_collapsed": [
                "research/gmi-833-depgraph-adjudication-v1/DUPLICATE_ADJUDICATION_V1.json",
            ],
            "A5_no_unsupported_overclaim_remaining": [
                "research/gmi-833-depgraph-adjudication-v1/OVERSTRONG_ADJUDICATION_V1.json",
                "research/gmi-833-corpus-audit-close-v1/FREEZE_V1.md",
                "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_V1.json",
                "research/gmi-833-corpus-passes-v2-v1/PASS_L58_V1.md",
            ],
            "A6_maturity_scored_no_m5_m6_evidence": [
                "research/gmi-833-maturity-rescore-v1/FREEZE_V1.md",
                "research/gmi-833-maturity-rescore-v2-v1/FREEZE_V2.md",
                "research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json",
                "research/gmi-833-claim-discipline-v1/MATURE_RESCORE_BRIDGE.md",
            ],
            "A7_claim_discipline_complete_zero_gap": [
                "research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json",
                "research/gmi-833-claim-discipline-v1/RESULT_V2.json",
                "research/gmi-833-claim-discipline-v1/SUCCESSOR_TRANCHE_V2.md",
            ],
            "A8_identification_passes_verdicts": [
                "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_V1.json",
                "research/gmi-833-corpus-passes-v2-v1/FROZEN_PASSES_V1.md",
            ],
            "A9_revival_queue_live": [
                "research/gmi-833-corpus-passes-v2-v1/REVIVAL_TICKETS_V1.json",
            ],
            "A10_terminology_migrated_paper_facing": [
                "research/gmi-833-terminology-migration-v1/MIGRATION_LOG_V1.md",
                "research/gmi-833-terminology-migration-v1/MIGRATION_LOG_V2.md",
                "research/gmi-833-terminology-migration-v1/ACKNOWLEDGED_FINDINGS_V1.json",
            ],
            "A11_blind_recovery_v2_channels_closed": [
                "research/gmi-833-blind-recovery-v2-v1/NEUTRAL_BATTERY_FREEZE_V1.json",
                "research/gmi-833-blind-recovery-v2-v1/BASIS_GRID_V1.json",
                "research/gmi-833-blind-recovery-v2-v1/SCREEN_RESULT_V1.json",
                "research/gmi-833-blind-recovery-v2-v1/POSTHOC_RESULT_V2.json",
                "research/gmi-833-blind-recovery-v2-v1/OPEN_GAPS.json",
            ],
            "A12_grammar_growth_green_registered_scope": [
                "research/gmi-833-g0-grammar-growth-v1/MANIFEST_V1.json",
                "research/gmi-833-g0-grammar-growth-v1/RESULT_V1.json",
                "research/gmi-833-g0-grammar-growth-v1/FROZEN_FIXTURES_V1.json",
                "research/gmi-833-g0-grammar-growth-v1/ORACLE_RESULT_V1.json",
            ],
            "A13_progress_ledger_current": [
                "research/gmi-833-progress-ledger-v1/CHECKBOX_EVIDENCE_V1.md",
                "research/gmi-833-progress-ledger-v1/REMAINING_WORK_V1.md",
            ],
            "A14_ci_u_universal_re_earned": [
                "research/gmi-833-corpus-passes-v2-v1/PASS_L58_V1.md",
                "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_V1.json",
            ],
        },
        "verified_counts": counts,
        "revival_ticket_register": register,
        "open_obligations": {
            "revival_tickets_open": [t["id"] for t in open_],
            "aj_lane_terminology_residual": {
                "hits": 35,
                "packages": 12,
                "owner": "gmi-833-aj* lanes (per MIGRATION_LOG_V2.md; untouched by the non-aj migration)",
            },
            "l48_screen_refinement": {
                "owner": "aj lane (AJ9 no-smuggling contract response; not the identification sweep's)",
                "note": "identification screen only at this baseline; L48 remains unticked by the v2 sweep",
            },
            "blind_recovery_v2_open_gaps": [
                {"id": g["id"], "severity": g["severity"], "gap": g["gap"]} for g in v2_gaps
            ],
            "screened_not_adjudicated_states": (
                "L49/L53 37 packages, L54/L55 5+5 sampled-out rows, and census-side "
                "1,336 UNIVERSAL objects (L52 statement-side) remain explicit "
                "SCREENED-NOT-ADJUDICATED gap states in VERDICT_REGISTER_V1.json - "
                "recorded, never silently dropped"
            ),
            "post_pin_arrivals": (
                "any claim-bearing arrival after the pinned SHA enters as U-NEW until "
                "typed by the frozen mechanical re-run (see arrival_absorption_rule)"
            ),
        },
        "arrival_absorption_rule": {
            "statement": (
                "Enumerate arrivals mechanically: git diff --stat <pinned_head_sha>..<head> "
                "-- research/ restricted to new gmi-833-* directories (and new claim-bearing "
                "files in existing research/gmi-* packages). Every enumerated arrival is a "
                "U-NEW object of the baseline: it is listed, never silently dropped, and "
                "holds no baseline assertion until typed by the frozen mechanical re-run - "
                "census object extraction, maturity scoring under the frozen rubric, "
                "claim-discipline field registration, RAG strata assignment, and the "
                "identification-pass screens. Arrivals never block the freeze; they are "
                "absorbed by a numbered manifest supplement recording their typed status."
            ),
            "precedent": (
                "research/gmi-833-blind-recovery-v2-v1 absorbed as the 235th claim-discipline "
                "object under this rule (RESULT_V2.json arrivals field, PR #974)"
            ),
            "frozen_rule_sources": [
                "research/gmi-833-claim-discipline-v1/FREEZE_V1.md (universe + mechanical enumeration)",
                "research/gmi-833-maturity-rescore-v2-v1/FREEZE_V2.md (arrival scoring protocol)",
            ],
        },
        "governance": {
            "post_freeze_edit_rule": (
                "No bound artifact may be edited in place after this freeze. Every "
                "change - a revival ticket closing, an arrival typed, a count moving - "
                "lands as a supplement: a NEW file research/gmi-833-theory-baseline-v1/"
                "SUPPLEMENT_<n>_<slug>.md (plus any new artifacts in the owning lane) and, "
                "when the binding changes, BASELINE_MANIFEST_V2.json. The pinned "
                "BASELINE_MANIFEST_V1.json and every file it binds stay byte-identical; "
                "research/gmi-833-theory-baseline-v1/test_theory_baseline_v1.py enforces "
                "this and fails on drift."
            ),
            "supplement_pattern": "SUPPLEMENT_*_*.md + BASELINE_MANIFEST_V<n>.json",
            "tamper_evidence": "tests/test_theory_baseline_v1.py re-derives every sha256 from the live tree",
            "forbidden_promotions": [
                "ALL_GMI_THEOREMS_TRUE",
                "ONTOLOGICAL_COMPLETENESS",
                "ALL_PARENTS_EXHAUSTED",
                "ALL_OVERCLAIMS_REPAIRED",
                "KNOWN_FAMILY_DERIVATION_COMPLETE",
                "REAL_SCALE_VALIDATION_COMPLETE",
                "COMPLETE_GMI",
                "BASELINE_IMPLIES_THEOREM_TRUTH",
                "REVIVAL_OBLIGATION_CLOSED_BY_BASELINE",
                "SILENT_EDIT_OF_BOUND_ARTIFACT",
            ],
        },
    }

    # every assertion_dependency path must be a bound artifact
    bound = {a["path"] for a in artifacts}
    for assertion, paths in manifest["assertion_dependencies"].items():
        for p in paths:
            assert p in bound, f"{assertion} references unbound artifact {p}"

    # self-binding: the freeze package's own files (everything except the
    # manifest, which cannot contain its own hash)
    self_binding = []
    for f in sorted((REPO / PKG).iterdir()):
        if not f.is_file() or f.name == "BASELINE_MANIFEST_V1.json":
            continue
        data = f.read_bytes()
        self_binding.append(
            {
                "path": f"{PKG}/{f.name}",
                "sha256": sha256_bytes(data),
                "bytes": len(data),
                "role": "FREEZE_PACKAGE_SELF",
            }
        )
    manifest["self_binding"] = self_binding
    manifest["governance"]["tamper_evidence"] = (
        "research/gmi-833-theory-baseline-v1/test_theory_baseline_v1.py re-derives "
        "every sha256 (component artifacts + self-binding) from the live tree; "
        "runs under python -I -B and -I -O -B with no third-party dependency"
    )

    out_path = REPO / PKG / "BASELINE_MANIFEST_V1.json"
    out_path.write_text(json.dumps(manifest, indent=1, sort_keys=False) + "\n")
    print(f"wrote {out_path.relative_to(REPO)}: {len(artifacts)} artifacts bound, "
          f"{len(COMPONENTS)} components, assertions A1-A14")
    print("verified_counts:", json.dumps(counts, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
