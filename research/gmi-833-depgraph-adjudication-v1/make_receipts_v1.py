#!/usr/bin/env python3
"""Receipts for the gmi-833-depgraph-adjudication-v1 tranche.

Reruns every generator, records the command, the worktree head SHA, each
artifact's sha256, and every headline count RE-READ from the written file
(not from the generator's stdout).  Deterministic output."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]

GENERATORS = [
    "depgraph_miner_v1.py",
    "cycle_check_v1.py",
    "duplicate_adjudication_v1.py",
    "overstrong_adjudication_v1.py",
    "master_rag_v1.py",
]
ARTIFACTS = [
    "DEPENDENCY_GRAPH_V2.json",
    "CYCLE_REPORT_V1.json",
    "DUPLICATE_ADJUDICATION_V1.json",
    "OVERSTRONG_ADJUDICATION_V1.json",
    "MASTER_RAG_TABLE_V1.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    runs = []
    for g in GENERATORS:
        r = subprocess.run([sys.executable, str(HERE / g)],
                           capture_output=True, text=True)
        runs.append({"command": f"python3 research/gmi-833-depgraph-adjudication-v1/{g}",
                     "exit": r.returncode,
                     "stdout_tail": r.stdout.strip().splitlines()[-6:]})
        if r.returncode != 0:
            print(r.stdout, r.stderr)
            return 1

    t = subprocess.run([sys.executable, str(HERE / "test_depgraph_miner_v1.py")],
                       capture_output=True, text=True)
    test_line = t.stdout.strip().splitlines()[-1]

    head = subprocess.run(["/usr/bin/git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()

    # counts re-read from the written artifacts
    dg = json.loads((HERE / "DEPENDENCY_GRAPH_V2.json").read_text())
    cy = json.loads((HERE / "CYCLE_REPORT_V1.json").read_text())
    du = json.loads((HERE / "DUPLICATE_ADJUDICATION_V1.json").read_text())
    ov = json.loads((HERE / "OVERSTRONG_ADJUDICATION_V1.json").read_text())
    mt = json.loads((HERE / "MASTER_RAG_TABLE_V1.json").read_text())

    edges = {k: len(v) for k, v in dg["edges"].items() if isinstance(v, list)}
    reread = {
        "dependency_edges_by_layer": edges,
        "dependency_edges_total": sum(edges.values()),
        "review_excluded_edges": len(dg["review"]["excluded_edges"]),
        "review_retyped_edges": len(dg["review"]["retyped_edges"]),
        "cycles": cy["union"]["cycle_count"],
        "self_loops": len(cy["union"]["self_loops"]),
        "duplicate_groups": du["candidate_groups"]["count"],
        "duplicate_group_verdicts": du["candidate_groups"]["verdict_distribution"],
        "dupid_verdicts": du["dupid_gaps"]["verdict_distribution"],
        "content_collapse": du["content_collapse"],
        "fin2univ_population": ov["population"],
        "fin2univ_verdicts": ov["verdict_distribution"],
        "downgrade_list_entries": len(ov["downgrade_list"]),
        "rag_strata": len(mt["strata"]),
        "rag_objects": mt["summary"]["census_objects"],
        "rag_content_collapsed": mt["summary"]["content_collapsed_objects"],
        "rag_corpus_instances": len(mt["corpus_instances"]),
    }
    receipts = {
        "schema": "GMI_833_DEPGRAPH_ADJUDICATION_RECEIPTS_V1",
        "worktree_head_at_generation": head,
        "census_frozen_source_sha": dg["census_frozen_source_sha"],
        "mined_at_sha": dg["mined_at_sha"],
        "generator_runs": runs,
        "validation": {
            "command": "python3 research/gmi-833-depgraph-adjudication-v1/test_depgraph_miner_v1.py",
            "exit": t.returncode,
            "final_line": test_line,
        },
        "artifact_sha256": {a: sha256(HERE / a) for a in ARTIFACTS},
        "counts_reread_from_written_files": reread,
    }
    out = HERE / "RECEIPTS_V1.json"
    out.write_text(json.dumps(receipts, indent=1, sort_keys=False,
                              ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"head: {head}")
    print(f"validation: {test_line}")
    for a, d in receipts["artifact_sha256"].items():
        print(f"  {d[:16]}  {a}")
    for k, v in reread.items():
        print(f"  {k}: {v}")
    print(f"sha256 RECEIPTS_V1.json: {sha256(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
