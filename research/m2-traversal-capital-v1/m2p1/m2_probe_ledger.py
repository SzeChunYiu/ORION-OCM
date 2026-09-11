#!/usr/bin/env python3
"""Recompute the three ledgers for PROBE-mode gates with fit cost = 0.

m2_applicability fits a rule on the validation stream in every mode, and its ledger
charged that fit to the probe gate too. The probe gate uses no rule: its acquisition
cost is beta per target, already inside its B. So for probe mode:
    conservative = developmental solving only      (validation solves belong to the
                                                    admission machinery, not the gate)
    marginal     = 0
    incremental  = 0
Pure arithmetic on the saved JSON; nothing is re-run.
"""
import json, sys
from pathlib import Path
for f in sys.argv[1:]:
    d = json.loads(Path(f).read_text())
    if d.get("feature_mode") != "probe":
        print(f, "not probe mode; skipped"); continue
    n = d["targets"]; a = d["arms"]
    saved = a["RESET"]["total_B"] - a["APPLICABILITY"]["total_B"]; per = saved / n
    dev = d["dev_solve_slots"]
    be = round(dev / per, 1) if per > 0 else None
    d["ledger_probe_corrected"] = {
        "saved_slots_per_target": round(per, 1), "total_saved": round(saved, 1),
        "conservative": {"cost": dev, "breakeven": be, "pays": bool(per > 0 and dev / per <= n), "net": round(saved - dev, 1)},
        "marginal": {"cost": 0, "breakeven": 0.0, "pays": per > 0, "net": round(saved, 1)},
        "incremental": {"cost": 0, "breakeven": 0.0, "pays": per > 0, "net": round(saved, 1)},
        "note": "probe gate fits nothing; beta is charged inside B; fit cost from the rule path removed",
    }
    Path(f).write_text(json.dumps(d, indent=1, sort_keys=True))
    L = d["ledger_probe_corrected"]
    print("%-12s horizon=%-4d saved/target=%-8.1f | conservative cost=%-9d breakeven=%-6s pays=%-5s net=%+.0f | marginal/incremental pay=%s" % (
        d["label"], n, per, dev, be, L["conservative"]["pays"], L["conservative"]["net"], L["marginal"]["pays"]))
