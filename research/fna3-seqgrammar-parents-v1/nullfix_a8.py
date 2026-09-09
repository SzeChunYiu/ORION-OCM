#!/usr/bin/env python3
"""Post-run correction A8 driver (declared post-run, NOT in the pre-run set).

Defect found when reading FNA3_RESULTS_V1.json: the UD shuffle-null controls
scored an EMPTY window (bits_per_symbol = 0.0 exactly for every arm) because
run_shuffle_null sliced `stream[n:n+T]` while the real-corpus fit streams are
truncated to exactly n symbols. The synthetic-world nulls sliced full streams
and are unaffected. This driver re-runs ONLY the UD shuffle nulls with the
corrected run_shuffle_null(score_stream=...) signature (same seeds, same
arms, same n), for transparent merge into the results as post_run_corrections.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fna3  # noqa: E402

HERE = Path(__file__).resolve().parent


def main():
    t0 = time.time()
    out = {
        "id": "A8_ud_shuffle_null_empty_window_fix",
        "declared": "post-run correction (defect found reading V1 results)",
        "defect": ("run_shuffle_null scored stream[n:n+T] which is EMPTY for the "
                   "UD worlds (fit streams truncated to exactly n); all seven "
                   "UD null entries in V1 recorded bits_per_symbol = 0.0 and "
                   "the R5 cases derived from them are invalid"),
        "fix": "run_shuffle_null(..., score_stream=protected scored stream); "
               "UD nulls recomputed with identical arms/seeds/n",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "nulls": {"W4_UD_CHAR": {}, "W5_UD_POS": {}},
    }
    # W4
    stream4, scored4, alpha4 = fna3.w4_loader()
    aset4 = set(alpha4)
    if any(c not in aset4 for c in scored4):
        scored4 = "".join(c if c in aset4 else "\x00" for c in scored4)
        alpha4 = list(alpha4) + ["\x00"]
    for key in ("P1", "P2", "P3", "P7"):
        t1 = time.time()
        nr = fna3.run_shuffle_null(key, alpha4, stream4, 1000000, len(scored4),
                                   score_stream=scored4)
        out["nulls"]["W4_UD_CHAR"][key] = {
            "shuffled_bits": nr.get("bits_per_symbol"),
            "positions_scored": nr.get("positions_scored"),
            "shuffled_fit_wall_s": nr.get("fit_wall_s")}
        print("[%6.1fs] W4 %s done (%.1fs)" % (time.time() - t0, key, time.time() - t1), flush=True)
    # W5
    stream5, scored5, alpha5 = fna3.w5_loader()
    for key in ("P1", "P2", "P3", "P7"):
        t1 = time.time()
        nr = fna3.run_shuffle_null(key, alpha5, stream5, 254000, len(scored5),
                                   score_stream=scored5)
        out["nulls"]["W5_UD_POS"][key] = {
            "shuffled_bits": nr.get("bits_per_symbol"),
            "positions_scored": nr.get("positions_scored"),
            "shuffled_fit_wall_s": nr.get("fit_wall_s")}
        print("[%6.1fs] W5 %s done (%.1fs)" % (time.time() - t0, key, time.time() - t1), flush=True)
    out["wall_seconds"] = round(time.time() - t0, 1)
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    p = HERE / "NULLFIX_A8.json"
    p.write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    print("written %s (%d bytes)" % (p, p.stat().st_size), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
