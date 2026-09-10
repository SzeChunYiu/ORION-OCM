#!/usr/bin/env python3
"""M2-P1 amortisation vs developmental depth (#323 HDI-14).

The E1/E5/E6 ledgers charge the ENTIRE developmental phase against the prior and come
out negative. Two things were never separated, and they should be:

  1. DEPTH. Acquisition cost grows with the number of developmental tasks solved, but
     the dose-response is non-monotone -- the prior peaks at a modest depth and then
     degrades. So there is an economically optimal depth, and full depth is not it.

  2. WHAT THE COST BUYS. Solving the developmental tasks produced verified solutions --
     real acquired cognition the agent wanted. Charging all of it against the search
     prior is maximally conservative: it treats every developmental solve as pure
     overhead. The MARGINAL ledger charges only what the prior specifically cost --
     mining plus validation -- and is the right question for "does keeping the prior
     pay?" once the developmental work is done anyway.

Both ledgers are reported. Neither is presented as the single truth.
"""
from __future__ import annotations
import argparse, json, statistics
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ecology", required=True)
    ap.add_argument("--dose", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    eco = json.loads(Path(a.ecology).read_text())
    dose = json.loads(Path(a.dose).read_text())
    summ = json.loads(Path(a.summary).read_text())

    train = eco["streams"]["train"]
    reset_B = summ["arms"]["RESET"]["mean_B_slots"]
    n_prot = len(eco["streams"]["protected"])

    # validation cost is paid once per admission attempt, independent of depth
    val_rows = dose["curve"]
    validate_slots = None
    att = Path(a.summary).parent
    for cand in (att / "M2P1_E5_ATTRIBUTION.json", att / "M2P1_E6_ATTRIBUTION.json"):
        if cand.exists():
            at = json.loads(cand.read_text())
            validate_slots = sum(r["baseline_slots"] + r["candidate_slots"] for r in at["all_rows"])
            break

    rows = []
    for depth_s, v in sorted(val_rows.items(), key=lambda kv: int(kv[0])):
        if "work_reduction" not in v:
            continue
        d = int(depth_s)
        solve_slots = sum(r["baseline_first_index"] for r in train[:d])
        saved = reset_B * v["work_reduction"]
        full = solve_slots + (validate_slots or 0)
        marginal = validate_slots or 0
        rows.append({
            "depth": d, "admitted": v["admitted"],
            "work_reduction": v["work_reduction"],
            "developmental_solve_slots": solve_slots,
            "validation_slots": validate_slots,
            "saved_per_target": round(saved, 1),
            "conservative_acquisition": full,
            "conservative_breakeven_targets": round(full / saved, 1) if saved > 0 else None,
            "marginal_acquisition": marginal,
            "marginal_breakeven_targets": round(marginal / saved, 1) if saved > 0 else None,
        })

    admitted = [r for r in rows if r["admitted"]]
    best_cons = min(admitted, key=lambda r: r["conservative_breakeven_targets"]) if admitted else None
    best_marg = min(admitted, key=lambda r: r["marginal_breakeven_targets"]) if admitted else None

    out = {
        "schema": "OCM_M2P1_AMORTISATION_VS_DEPTH_V1",
        "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
        "owner_issue": 165, "hardening_parent": 323,
        "ecology": eco.get("ecology_variant", {}).get("label", "?"),
        "reset_mean_B": reset_B, "protected_targets": n_prot,
        "rows": rows,
        "best_conservative": best_cons, "best_marginal": best_marg,
        "note": ("conservative charges every developmental solve against the prior, which "
                 "treats verified cognition the agent wanted as pure overhead; marginal "
                 "charges only mining plus validation. Both reported; neither is the "
                 "single truth."),
    }
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print("%-7s %-6s %-8s %-12s %-14s %s" % ("depth", "adm", "reduc", "saved/tgt",
                                             "cons.breakeven", "marg.breakeven"))
    for r in rows:
        print("%-7s %-6s %-8s %-12s %-14s %s" % (
            r["depth"], r["admitted"], r["work_reduction"], r["saved_per_target"],
            r["conservative_breakeven_targets"], r["marginal_breakeven_targets"]))
    print("\nprotected targets available:", n_prot)
    if best_marg:
        print("best marginal: depth %s -> %s targets to break even" % (
            best_marg["depth"], best_marg["marginal_breakeven_targets"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
