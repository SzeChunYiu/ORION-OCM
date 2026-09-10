#!/usr/bin/env python3
"""M2-P1 behavioural reuse receipt (#323 HDI-15 / section 4).

"Require direct evidence that history altered search BEFORE the target answer was
found."  This ecology admits an exact receipt rather than an inference.

In methods.solve the stream is chosen by slot parity:

    stream = guided if guided is not None and slots % 2 == 1 else baseline

so for any arm carrying fragments, a success returned at an ODD slot was produced by
the GUIDED stream -- i.e. by a candidate the history-derived library proposed. An
even-slot success came from the primitive baseline. The parity of the returned slot
is therefore a direct behavioural receipt of which stream found the answer, recorded
per target, and it is unavailable to any arm without fragments (RESET/LIBRARY_ONLY
never construct a guided stream at all).
"""
from __future__ import annotations
import argparse, json, statistics
from collections import defaultdict
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    run = Path(a.run_dir)

    arms = {}
    for f in sorted(run.glob("arm_*.json")):
        d = json.loads(f.read_text())
        arms[d["arm"]] = d

    out_arms = {}
    for name, d in arms.items():
        frags = d["fragments_served"]
        # first verified success per target (lowest budget rung that verified)
        first = {}
        for r in d["rows"]:
            if r["verified"] and r["target"] not in first:
                first[r["target"]] = r
        odd = sum(1 for r in first.values() if r["B_slots"] % 2 == 1)
        n = len(first)
        base_first = {r["target"]: r["baseline_first_index"] for r in first.values()}
        out_arms[name] = {
            "fragments_served": frags,
            "targets_with_verified_success": n,
            "guided_stream_successes_odd_slot": odd if frags else None,
            "baseline_stream_successes_even_slot": (n - odd) if frags else None,
            "guided_share": round(odd / n, 4) if (frags and n) else None,
            "mean_B_first_success": round(statistics.fmean(r["B_slots"] for r in first.values()), 1) if n else None,
            "mean_candidates_checked": round(statistics.fmean(r["candidates_checked"] for r in first.values()), 1) if n else None,
            "receipt_available": bool(frags),
            "note": ("odd-slot successes are produced by the guided (history-derived) stream; "
                     "arms without fragments never build a guided stream, so no receipt exists "
                     "for them and the field is null rather than zero"),
        }

    ref = out_arms.get("RESET", {}).get("mean_B_first_success")
    for name, v in out_arms.items():
        v["work_vs_RESET"] = (None if (ref is None or v["mean_B_first_success"] is None)
                              else round(1 - v["mean_B_first_success"] / ref, 4))

    out = {"schema": "OCM_M2P1_BEHAVIOURAL_RECEIPT_V1",
           "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "owner_issue": 165, "hardening_parent": 323,
           "mechanism": ("methods.solve selects the guided stream exactly when the slot "
                         "counter is odd; the returned slot's parity therefore identifies "
                         "which stream produced the verified answer"),
           "arms": out_arms}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    for name, v in out_arms.items():
        print("%-30s frags=%-3s n=%-3s guided_share=%-8s meanB=%-9s vsRESET=%s"
              % (name, v["fragments_served"], v["targets_with_verified_success"],
                 v["guided_share"], v["mean_B_first_success"], v["work_vs_RESET"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
