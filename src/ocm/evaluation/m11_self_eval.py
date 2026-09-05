"""M11 self-reorganisation evaluation: the controlled benchmark S1–S7 vs the two parents, the
historical failure replay (ledger rows S11–S28 with their human minimal fixes) and the
adoption-governance hostiles.  Writes research/ocm-m11/M11_SELF_EVAL_V1.json.

Every number is bound to the frozen scenario list; the terminal per claim is decided in the
report (docs/M11_SELF_REORGANISATION_REPORT.md), not here.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from ocm.selfmodel import benchmark as B
from ocm.selfmodel import replay as R

OUT = Path("research/ocm-m11/M11_SELF_EVAL_V1.json")


def main() -> int:
    out_path = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else OUT
    rows = []
    parents = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for sc in B.scenarios():
            rows.append(B.run_scenario(sc, root))
            target, preservation = B.suites_for(sc.build().env_version)
            parents.append({"scenario": sc.scenario_id, "parameter_search": B.parent_parameter_search(sc, target, preservation), "reflection_retry": B.parent_reflection_retry(sc, target, preservation)})
    control = [r for r in rows if r.get("no_failure")]
    rows_f = [r for r in rows if not r.get("no_failure")]
    n = len(rows_f)
    summary = {
        "scenarios": n,
        "control_no_fault": {"count": len(control), "no_proposal_raised": all(not r["adopted"] and r["proposal_class"] is None for r in control)},
        "diagnosis_correct": sum(r["diagnosis_correct"] for r in rows_f),
        "minimum_class_correct": sum(r["minimum_class_correct"] for r in rows_f),
        "false_jumps": sum(r["false_jump"] for r in rows_f),
        "missed_jumps": sum(r["missed_jump"] for r in rows_f),
        "assurance_passed": sum(r["assurance"] for r in rows_f),
        "adopted": sum(r["adopted"] for r in rows_f),
        "target_restored": sum(r["target_after"].split("/")[0] == r["target_after"].split("/")[1] for r in rows_f),
        "preservation_kept": sum(int(r["preservation_after"].split("/")[0]) >= int(r["preservation_before"].split("/")[0]) for r in rows_f),
        "rollback_exact": sum(bool(r["rollback_exact"]) for r in rows_f),
        "broad_rewrites_refused": sum(1 for r in rows_f if r["broad_rewrite"] and r["broad_rewrite"]["refused"]),
        "broad_rewrites_offered": sum(1 for r in rows_f if r["broad_rewrite"]),
        "prediction_realised": sum(bool(r["prediction_realised"]) for r in rows_f),
        "parent_parameter_search_solves": sum(p["parameter_search"]["solves"] for p in parents if not p["scenario"].startswith("S0")),
        "parent_reflection_retry_solves": sum(p["reflection_retry"]["solves"] for p in parents if not p["scenario"].startswith("S0")),
        "ocm_solves": sum(r["target_after"].split("/")[0] == r["target_after"].split("/")[1] and r["adopted"] for r in rows_f),
    }
    replay = R.replay_all()
    out = {"version": "M11_SELF_EVAL_V1", "summary": summary, "scenarios": rows, "parents": parents, "historical_replay": replay,
           "notes": ["target = outage cases, preservation = non-outage cases (oracle-built from protected hidden state; the machine never reads it)",
                     "the ablation channel is available to the self-model only; parents search configurations or retry skills",
                     "n = 7 scenarios: any rate is descriptive; SUPPORTED/REFUTED terminals need the pre-registered n (see report)"]}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(summary, indent=1))
    print(json.dumps(replay["summary"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
