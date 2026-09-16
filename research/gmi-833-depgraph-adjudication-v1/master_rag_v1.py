#!/usr/bin/env python3
"""GMI #833 — corpus master RED/AMBER/GREEN table v1.

Builds on the frozen 28-stratum census (2fffb144) plus this tranche's
adjudications.  Census dispositions are NEVER overwritten; adjudication
results are annotations.  Rows:

  per stratum (audit_disposition x object_class, the 28 non-empty census
  strata): census object count, objects in DUPLICATE-adjudicated groups
  (content-collapsible), FIN2UNIV flags in the stratum (all adjudicated
  PROPER at wording level in OVERSTRONG_ADJUDICATION_V1 - the flag is a
  detector false-positive class, the census RED stands until a census
  refresh applies the finding).

  corpus instances (issue-level rows, not object rows):
    INSTANCE-1 AJ9 no-smuggling contract scope gap (PRs #931-#934 audit
               comments; inherited by K04-K06 aj9e/f/g): the prospective
               contract governs label/fingerprint channels but leaves task
               provenance and primitive-basis provenance ungoverned.
               Severity HIGH.  Status RED (open; minimal fix = contract V2).
    INSTANCE-2 config->freeze separation is commit-ordering, not time
               separation (12 s / 10 s / 13 s gaps, PRs #932/#933/#934):
               prospective-ness non-demonstrable from custody metadata
               alone.  Severity MEDIUM.  Status AMBER (real custody checks
               exist; the separation claim overreaches what metadata shows).
    plus tranche-discovered census/tooling defects (see freeze doc).

Claim ceiling: GMI_833_MASTER_RAG_AT_FROZEN_CENSUS_PLUS_TRANCHE_ANNOTATIONS.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
CENSUS_DIR = REPO_ROOT / "research" / "gmi-833-corpus-census-v1"

SCHEMA = "GMI_833_MASTER_RAG_TABLE_V1"
CLAIM_CEILING = "GMI_833_MASTER_RAG_AT_FROZEN_CENSUS_PLUS_TRANCHE_ANNOTATIONS"


def main():
    idx = json.loads((CENSUS_DIR / "CORPUS_INDEX_V1.json").read_text(encoding="utf-8"))
    aud = json.loads((CENSUS_DIR / "AUDIT_V1.json").read_text(encoding="utf-8"))
    gg = json.loads((CENSUS_DIR / "GMI_GAP_GRAPH_V1.json").read_text(encoding="utf-8"))
    dup = json.loads((HERE / "DUPLICATE_ADJUDICATION_V1.json").read_text(encoding="utf-8"))
    ov = json.loads((HERE / "OVERSTRONG_ADJUDICATION_V1.json").read_text(encoding="utf-8"))
    dg = json.loads((HERE / "DEPENDENCY_GRAPH_V2.json").read_text(encoding="utf-8"))
    cy = json.loads((HERE / "CYCLE_REPORT_V1.json").read_text(encoding="utf-8"))

    objs = idx["scientific_objects"]
    byid = defaultdict(list)
    for o in objs:
        byid[o["object_id"]].append(o)

    # duplicate overlay: objects in DUPLICATE-verdict groups
    dup_obj_ids = set()
    for a in dup["candidate_groups"]["adjudications"]:
        if a["verdict"] == "DUPLICATE":
            dup_obj_ids.update(a["object_ids"])
    fin_claim_ids = {a["claim_id"] for a in ov["adjudications"]}

    strata = {}
    for o in objs:
        k = (o["audit_disposition"], o["object_class"])
        s = strata.setdefault(k, {"objects": 0, "in_duplicate_groups": 0,
                                  "fin2univ_flags": 0})
        s["objects"] += 1
        if o["object_id"] in dup_obj_ids:
            s["in_duplicate_groups"] += 1
        if o["object_id"] in fin_claim_ids:
            s["fin2univ_flags"] += 1

    strata_rows = [
        {"disposition": d, "object_class": c, **vals}
        for (d, c), vals in sorted(strata.items())
    ]
    grouped = dup["content_collapse"]["grouped_objects"]
    nodes = dup["content_collapse"]["content_nodes_after_collapse"]
    total = len(objs)
    content_total = total - grouped + nodes

    dup_gaps = dup["dupid_gaps"]["verdict_distribution"]
    ov_dist = ov["verdict_distribution"]
    edge_total = sum(len(v) for v in dg["edges"].values() if isinstance(v, list))

    table = {
        "schema": SCHEMA,
        "claim_ceiling": CLAIM_CEILING,
        "census_frozen_source_sha": idx["frozen_source_sha"],
        "rules": {
            "stratum_disposition": "frozen census disposition; never overwritten by this tranche",
            "in_duplicate_groups": "objects in groups adjudicated DUPLICATE (content-collapsible); collapse counting is by content, not by name/PR",
            "fin2univ_flags": "GAP-FIN2UNIV flags whose claim object sits in this stratum; every flag was adjudicated PROPER at wording level (detector false-positive classes) - census RED stands until a census refresh applies the finding",
        },
        "summary": {
            "census_objects": total,
            "census_dispositions": aud["summary"]["dispositions"],
            "content_collapsed_objects": content_total,
            "duplicate_groups": dup["candidate_groups"]["count"],
            "duplicate_group_verdicts": dup["candidate_groups"]["verdict_distribution"],
            "dupid_gap_verdicts": dup_gaps,
            "fin2univ_flags": ov["population"],
            "fin2univ_verdicts": ov_dist,
            "dependency_edges_total": edge_total,
            "dependency_cycles": cy["union"]["cycle_count"],
            "dependency_self_loops": len(cy["union"]["self_loops"]),
        },
        "strata_framing": "39 non-empty strata = the census/#939 28 AMBER+RED sample strata plus 11 GREEN strata; object counts sum to 22,553",
        "strata": strata_rows,
        "corpus_instances": [
            {
                "id": "INSTANCE-AJ9-NOSMUGGLING-SCOPE",
                "disposition": "RED",
                "severity": "HIGH",
                "statement": "AJ9 blind-recovery prospective no-smuggling contract leaves task provenance and primitive-basis provenance ungoverned (governs only label/fingerprint channels); inherited by K04-K06 (gmi-833-aj9e/f/g)",
                "evidence": "science-audit comments on PRs #931-#934 (2026-09-16), finding E1/A1/C1/D1; holdout contract research/gmi-833-aj9a-known-family-benchmark-v1/HOLDOUT_CONTRACT_V1.json",
                "open_action": "contract V2: freeze per-family task batteries and primitive bases inside the benchmark blob pre-tranche; run the #855 A2 semantic-fingerprint screen; require task/basis prior-disclosure rows in OPEN_GAPS.json",
            },
            {
                "id": "INSTANCE-CONFIG-FREEZE-SEPARATION",
                "disposition": "AMBER",
                "severity": "MEDIUM",
                "statement": "config-to-freeze separation in AJ9b/c/d is commit-ordering (12 s / 10 s / 13 s gaps), not demonstrable time separation; a config authored after a local outcome run is indistinguishable from a prospective one in the custody metadata",
                "evidence": "science-audit comment on PR #931 finding E2 (commit metadata 2026-09-16: 42fb250c 10:21:45Z -> 5324b806 10:21:57Z; PRs #932/#933/#934)",
                "open_action": "require an external timestamp anchor (e.g. dispatch receipt on a second host) between config freeze and search execution for prospective claims",
            },
            {
                "id": "INSTANCE-CENSUS-FIN2UNIV-DETECTOR",
                "disposition": "AMBER",
                "severity": "MEDIUM",
                "statement": "all 283 GAP-FIN2UNIV RED flags are wording-level false positives (bounded/negated/protocol universals); the detector parses universal words without boundedness/negation scope",
                "evidence": "OVERSTRONG_ADJUDICATION_V1.json (145 individual reads, 138 rule-classified rows validated on samples)",
                "open_action": "census v2: extend negation window and bounded-domain parsing before re-flagging; re-disposition affected objects at refresh",
            },
            {
                "id": "INSTANCE-CENSUS-DUPID-COLLISIONS",
                "disposition": "AMBER",
                "severity": "MEDIUM",
                "statement": "703 of 857 duplicate-ID gaps are genuine id collisions between different statement records (437 same-file restatements, 117 same-package, 149 cross-package); 154 are benign redeclarations",
                "evidence": "DUPLICATE_ADJUDICATION_V1.json dupid_gaps section",
                "open_action": "id-namespace tranche: unique ids or registered aliases; cross-package collisions (149) first",
            },
            {
                "id": "INSTANCE-CENSUS-EMPTY-DEPENDENCY-FIELDS",
                "disposition": "AMBER",
                "severity": "MEDIUM",
                "statement": "census index shipped strongest_parents and claim_dependencies unpopulated for all 22,553 objects; DEPENDENCY_GRAPH_V1 shipped edges:{}",
                "evidence": "CORPUS_INDEX_V1.json (0 objects with strongest_parents); DEPENDENCY_GRAPH_V1.json; repaired by DEPENDENCY_GRAPH_V2.json (357 cited edges, this tranche)",
                "open_action": "census v2 populates the fields from V2 edges; dependency registration becomes a package-formation requirement",
            },
            {
                "id": "INSTANCE-AUDIT-CLOSE-TOOLING-UNCOMMITTED",
                "disposition": "AMBER",
                "severity": "LOW",
                "statement": "#939 freeze referenced audit_close_v1.py and verdicts_v1.py (determinism contract, 164 verdicts) but never committed them; found untracked in the shared worktree",
                "evidence": "FREEZE_V1.md section 6 vs git ls-tree of the merge; restored in this tranche's first commit",
                "open_action": "closed by this PR (files restored); worktree-hygiene check added to the freeze checklist",
            },
        ],
        "section_b_checkbox_status": {
            "inventory": "SATISFIED at frozen scope (census v1, 22,553 objects)",
            "dependency_graph": "REPAIRED at mined scope: V2 registers 357 cited edges (was edges:{})",
            "circular_dependencies": "ANSWERED for the stated-dependency graph: 0 cycles, 0 self-loops across all layers and the 239-node union (absence of cycles is over STATED relations; absence of an edge is not independence)",
            "duplicates": "ADJUDICATED at frozen scope: 1,652 groups + 857 gaps verdicted; content-collapsed counting 22,553 -> 17,258 objects",
            "overstrong_names": "ADJUDICATED for the 283 RED flags: all PROPER (detector false-positive classes); the corpus's 1 confirmed OVERSTRONG sits in the GREEN mainline (#939)",
        },
    }
    path = HERE / "MASTER_RAG_TABLE_V1.json"
    path.write_text(json.dumps(table, indent=1, sort_keys=False,
                               ensure_ascii=False) + "\n", encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"strata rows: {len(strata_rows)}")
    print(f"census objects {total} -> content-collapsed {content_total}")
    print(f"summary dispositions: {aud['summary']['dispositions']}")
    print(f"corpus instances: {len(table['corpus_instances'])}")
    for inst in table["corpus_instances"]:
        print(f"   [{inst['disposition']}] {inst['id']}")
    print(f"sha256 {path.name}: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
