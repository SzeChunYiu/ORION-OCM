#!/usr/bin/env python3
"""M2-P1 three-ledger amortisation (#323 HDI-14).

Charging acquisition correctly requires saying WHAT THE COST BUYS. Three ledgers,
increasingly precise about attribution. All three are reported; none is "the" answer.

  CONSERVATIVE   developmental solving + full validation.
                 Treats every developmental solve as pure overhead, even though each
                 produced a verified solution the agent wanted. Maximally hostile to
                 the history arm.

  MARGINAL       full validation only.
                 Grants that developmental solving was work the agent was doing anyway,
                 but still charges the whole validation phase to the prior.

  INCREMENTAL    the DUPLICATE search inside validation only.
                 validate_generator solves each held-out task TWICE -- once baseline,
                 once candidate -- but the agent needs only one solution per task and
                 would have paid the baseline regardless. The prior's genuine extra cost
                 is therefore the second search, i.e. sum(candidate_slots).

The incremental ledger is the honest answer to "what does keeping this prior cost me
that I would not otherwise have spent?". It is not a reinterpretation of the benefit --
the benefit column is identical in all three.
"""
from __future__ import annotations
import argparse, json, statistics
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--ecology", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--attribution", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    eco = json.loads(Path(a.ecology).read_text())
    summ = json.loads(Path(a.summary).read_text())
    att = json.loads(Path(a.attribution).read_text())
    arms = summ["arms"]

    if not (arms.get("CONTINUED", {}).get("mean_B_slots") and arms.get("RESET", {}).get("mean_B_slots")):
        raise SystemExit("missing arms")
    cont, reset = arms["CONTINUED"]["mean_B_slots"], arms["RESET"]["mean_B_slots"]
    saved_per_target = reset - cont
    n_future = len(eco["streams"]["protected"])

    rows = att["all_rows"]
    dev_solve = sum(r["baseline_first_index"] for r in eco["streams"]["train"])
    validation_full = sum(r["baseline_slots"] + r["candidate_slots"] for r in rows)
    validation_incremental = sum(r["candidate_slots"] for r in rows)

    ledgers = {}
    for name, cost in (("conservative", dev_solve + validation_full),
                       ("marginal", validation_full),
                       ("incremental", validation_incremental)):
        be = cost / saved_per_target if saved_per_target > 0 else None
        ledgers[name] = {
            "acquisition_slots": cost,
            "breakeven_targets": round(be, 1) if be else None,
            "future_targets_available": n_future,
            "net_slots_over_available_horizon": round(saved_per_target * n_future - cost, 1),
            "pays_for_itself": bool(be is not None and be <= n_future),
        }

    out = {"schema": "OCM_M2P1_THREE_LEDGER_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "owner_issue": 165, "hardening_parent": 323, "ecology": a.label,
           "admitted": summ["arms"]["CONTINUED"]["fragments_served"] > 0,
           "terminal": summ["terminal"],
           "benefit": {"mean_B_RESET": reset, "mean_B_CONTINUED": cont,
                       "saved_slots_per_target": round(saved_per_target, 1),
                       "work_reduction": round(1 - cont / reset, 4)},
           "components": {"developmental_solve_slots": dev_solve,
                          "validation_full_slots": validation_full,
                          "validation_incremental_slots": validation_incremental},
           "ledgers": ledgers,
           "definitions": {
               "conservative": "developmental solving + full validation; every dev solve treated as overhead",
               "marginal": "full validation only; dev solving granted as work already being done",
               "incremental": ("the duplicate search inside validation only; the agent needs one "
                               "solution per held-out task and would have paid the baseline anyway, "
                               "so the prior's genuine extra cost is the second search")}}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print("%s  admitted=%s  saved/target=%.0f  future=%d" % (
        a.label, out["admitted"], saved_per_target, n_future))
    for k, v in ledgers.items():
        print("  %-13s cost=%-10s breakeven=%-8s pays=%-6s net=%s" % (
            k, v["acquisition_slots"], v["breakeven_targets"], v["pays_for_itself"],
            v["net_slots_over_available_horizon"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
