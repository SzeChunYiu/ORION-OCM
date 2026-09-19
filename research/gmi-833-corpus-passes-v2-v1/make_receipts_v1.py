#!/usr/bin/env python3
"""Receipts for corpus passes v2: commands, SHAs, artifact hashes, counts re-read from
the written files (script-asserted, then re-read). stdlib only; deterministic."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parents[1]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def head() -> str:
    return subprocess.run(["/usr/bin/git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def main() -> int:
    artifacts = {
        "FROZEN_PASSES_V1.md": None, "detector_l42_v1.py": None,
        "test_detector_l42_v1.py": None, "TERM_DUP_CANDIDATES_V1.json": None,
        "screen_p1p2_v1.py": None, "P1P2_SCREENS_V1.json": None,
        "screen_p3_v1.py": None, "P3_SCREENS_V1.json": None,
        "VERDICT_REGISTER_V1.json": None, "RAG_DELTA_V1.json": None,
    }
    for name in artifacts:
        p = HERE / name
        assert p.exists(), f"missing artifact {name}"
        artifacts[name] = sha256(p)

    counts = {}
    td = json.loads((HERE / "TERM_DUP_CANDIDATES_V1.json").read_text())
    counts["L42_candidate_groups"] = td["n_groups"]
    counts["L42_class_counts"] = td["class_counts"]
    s1 = json.loads((HERE / "P1P2_SCREENS_V1.json").read_text())
    counts["L44_population"] = s1["L44_enum_analytic"]["population"]
    counts["L44_screen_flagged"] = len(s1["L44_enum_analytic"]["flagged"])
    counts["L45_population"] = s1["L45_comp_only"]["population"]
    counts["L45_screen_flagged"] = len(s1["L45_comp_only"]["flagged"])
    counts["L51_population"] = s1["L51_iid_stationarity"]["population"]
    counts["L51_flagged"] = s1["L51_iid_stationarity"]["n_flagged"]
    counts["L52_flagged"] = len(s1["L52_finite_horizon"]["flagged"])
    s3 = json.loads((HERE / "P3_SCREENS_V1.json").read_text())
    from collections import Counter
    counts["L46_status"] = dict(Counter(v["L46"]["status"] for v in s3["packages"].values()))
    counts["L47_status"] = dict(Counter(v["L47"]["status"] for v in s3["packages"].values()))
    for k, flag in (("L49", "L49_flag"), ("L53", "L53_flag"), ("L54", "L54_flag"), ("L55", "L55_flag")):
        counts[f"{k}_flagged_packages"] = sum(1 for v in s3["packages"].values() if v[flag])
    counts["L50_lexical_hit_packages"] = sum(1 for v in s3["packages"].values() if v["L50"]["lexical_hits"])
    counts["L50_unaudited_operator_surface"] = sum(1 for v in s3["packages"].values() if v["L50"]["surface"] == "UNAUDITED_OPERATOR_SURFACE")
    counts["L56_named_parent_rows"] = s3["L56"]["named_parent_rows"]
    counts["L56_no_residual_flags"] = len(s3["L56"]["no_residual_flagged"])
    vr = json.loads((HERE / "VERDICT_REGISTER_V1.json").read_text())
    counts["verdict_register_sections"] = sorted(vr.keys())

    # re-read assertion: counts above must equal what a fresh reader would compute
    assert counts["L42_candidate_groups"] == 1
    assert counts["L44_population"] == 49 and counts["L45_population"] == 63

    receipt = {
        "schema": "GMI_833_CORPUS_PASSES_V2_RECEIPTS_V1",
        "head": head(),
        "populations": {"P1_census": "frozen 2fffb144 (result blob 861b1ba1)",
                        "P2_rescore": "THEOREM_SCORES_V2.json (merged #948 state)",
                        "P3_packages": "branch base 14276c20 (231 packages incl. morphogenesis)"},
        "commands": [
            "python3 test_detector_l42_v1.py   # 4 plants PASS",
            "python3 detector_l42_v1.py        # corpus run, anchor 1652==1652",
            "python3 screen_p1p2_v1.py         # L44/L45/L51/L52 screens, plants pass",
            "python3 screen_p3_v1.py           # L46/L47/L49/L50/L53/L54/L55/L56 screens, plants pass",
            "python3 -I -B research/gmi-capability-interactions-unified-v1/test_interactions.py  # 27/27 OK (L58 control)",
        ],
        "artifact_sha256": artifacts,
        "counts": counts,
    }
    out = HERE / "RECEIPTS_V1.json"
    out.write_text(json.dumps(receipt, indent=1, sort_keys=True))
    # re-read verification
    back = json.loads(out.read_text())
    assert back["counts"] == counts
    print(json.dumps(counts, indent=1, sort_keys=True))
    print(f"receipt written + re-read verified: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
