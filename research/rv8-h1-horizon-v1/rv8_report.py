"""Render RV8_ANALYSIS.json as the RV-8 report. Formatting only: every number comes
from the analysis receipt, none is computed here.

    python3 rv8_report.py <out_dir> > RV8_REPORT.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rv8_horizon import MIX_GRID, N_FULL, N_REDUCED, REDUCED_ARMS  # noqa: E402


def f(v, nd=0):
    if v is None:
        return "--"
    if isinstance(v, float) and nd == 0:
        return "{:,.0f}".format(v)
    if isinstance(v, float):
        return ("{:,.%df}" % nd).format(v)
    return "{:,}".format(v)


def nstar(row):
    """N* with its CI, or an explicit statement that no horizon pays."""
    m = row["marginal"]
    if m["saving_per_task"] is None or m["saving_per_task"] <= 0:
        return "no horizon pays"
    p = m["n_star_point"]
    reached = row["horizon_reached_max"]
    s = f(p)
    if m["n_star_lo"] and m["n_star_hi"]:
        s += " [{}, {}]".format(f(m["n_star_lo"]), f(m["n_star_hi"]))
    if p and p > reached:
        s += " (> horizon reached {})".format(f(reached))
    return s


def main(out):
    a = json.loads((out / "RV8_ANALYSIS.json").read_text())
    rep = json.loads((out / "RV8_REPLICATION.json").read_text())
    pre = json.loads((out / "RV8_PREFLIGHT.json").read_text())
    L = []
    w = L.append

    w("# RV-8 results — the H1 library-acquisition horizon\n")
    w("Cells: {} of {} loaded.\n".format(a["cells_loaded"], a["cells_expected"]))

    w("\n## Gates\n")
    w("| gate | result |")
    w("|---|---|")
    w("| production selection mirror | {} |".format(pre.get("selection_mirror_ok")))
    w("| smoke solves | {} |".format(pre.get("smoke_solves")))
    w("| acquisition reproduces FNA-4 run 3 exactly | {} |".format(
        pre.get("acquisition_gate_all_ok")))
    w("| reduced-arm rule agrees with its derivation | {} |".format(
        pre.get("reduced_arms_derivation_agrees")))
    w("| frozen sweep r=0 receipt replicated exactly | {} |".format(rep.get("exact")))

    w("\n### The projection's stream construction\n")
    nat = rep["natural_draw_same_mix_n24"]
    w("Same STITCH library, same 12 F1 + 12 F2 mix, same 24-task length.\n")
    w("| stream | incumbent | with library | saving | per task |")
    w("|---|---|---|---|---|")
    w("| FNA-4 constructed (product-order forced tuples) | {} | {} | {} | {} |".format(
        f(rep["observed"]["no_library_total"]),
        f(rep["observed"]["with_library_test_work"]),
        f(rep["observed"]["saving"]), f(rep["observed"]["saving"] / 24.0)))
    w("| RV-8 natural draws | {} | {} | {} | {} |".format(
        f(nat["no_library_total"]), f(nat["with_library_test_work"]),
        f(nat["saving"]), f(nat["saving_per_task"])))

    w("\n## Surface — present cost and future reuse, reported separately\n")
    for comp in ("balanced", "f1_only"):
        w("\n### composition: {}\n".format(comp))
        w("| arm | mix | horizon reached | present cost (marginal) | present cost "
          "(full) | future reuse (cum. saving) | saving/task [95% CI] | N* [95% CI] |")
        w("|---|---|---|---|---|---|---|---|")
        rows = [r for r in a["surface"] if r["composition"] == comp
                and r["null_seed"] is None]
        for r in sorted(rows, key=lambda x: (x["arm"], x["mix"])):
            m = r["marginal"]
            ci = "--"
            if m["saving_per_task_ci95"][0] is not None:
                ci = "{} [{}, {}]".format(f(m["saving_per_task"]),
                                          f(m["saving_per_task_ci95"][0]),
                                          f(m["saving_per_task_ci95"][1]))
            w("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
                r["arm"], r["mix"], f(r["horizon_reached_max"]),
                f(r["present_cost_acquisition_marginal"]),
                f(r["present_cost_acquisition_full"]),
                f(r["future_reuse_cumulative_saving"]), ci, nstar(r)))

    w("\n## Per-family attribution (saving/task, positive = library wins)\n")
    w("| arm | composition | mix | F1 | F2 | F3 |")
    w("|---|---|---|---|---|---|")
    for r in sorted(a["surface"], key=lambda x: (x["arm"], x["composition"],
                                                 x["mix"])):
        if r["null_seed"] is not None:
            continue
        pf = r.get("per_family_saving", {})
        w("| {} | {} | {} | {} | {} | {} |".format(
            r["arm"], r["composition"], r["mix"],
            f(pf.get("F1", {}).get("saving_per_task")),
            f(pf.get("F2", {}).get("saving_per_task")),
            f(pf.get("F3", {}).get("saving_per_task"))))

    w("\n## Critical mix (zero-crossing of saving/task)\n")
    w("| arm | composition | critical mix | 95% CI |")
    w("|---|---|---|---|")
    for c in a["critical_mix"]:
        lo, hi = c["critical_mix_ci95"]
        w("| {} | {} | {} | [{}, {}] |".format(
            c["arm"], c["composition"],
            "--" if c["critical_mix"] is None else "{:.4f}".format(c["critical_mix"]),
            "--" if lo is None else "{:.4f}".format(lo),
            "--" if hi is None else "{:.4f}".format(hi)))

    w("\n## Shuffle-equal-n null\n")
    w("Both columns are computed on the SAME prefix, `n compared` — the shorter of the "
      "two cells. Two null cells at mix 1.0 project past the 7-day ceiling, so their "
      "prefix is shorter than the learned arm's full horizon. The learned arm's "
      "saving/task here is therefore recomputed on that prefix and is NOT the "
      "full-horizon figure in the surface table above.\n")
    w("| learned arm | null | composition | mix | n compared | learned saving/task "
      "(on n compared) | null saving/task (mean, on n compared) | learned exceeds "
      "every null |")
    w("|---|---|---|---|---|---|---|---|")
    for n in sorted(a["null"], key=lambda x: (x["learned_arm"], x["composition"],
                                              x["mix"])):
        w("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
            n["learned_arm"], n["null_arm"], n["composition"], n["mix"],
            f(n["n_compared"]),
            f(n["learned_saving_per_task"]), f(n["null_saving_per_task_mean"]),
            n["learned_exceeds_every_null"]))

    w("\n## Windowed saving/task (stationary vs transient)\n")
    w("| arm | composition | mix | windows (early to late) |")
    w("|---|---|---|---|")
    for x in sorted(a["windows"], key=lambda y: (y["arm"], y["composition"],
                                                 y["mix"])):
        w("| {} | {} | {} | {} |".format(
            x["arm"], x["composition"], x["mix"],
            " ".join(f(v["saving_per_task"]) for v in x["windows"])))

    w("\n## Internal replicate check at mix 1.0\n")
    w("| arm | family sequences identical | saving/task balanced | "
      "saving/task f1_only | CI overlap |")
    w("|---|---|---|---|---|")
    for r in a.get("mix1_replicate_check", []):
        w("| {} | {} | {} | {} | {} |".format(
            r["arm"], r["family_sequences_identical"],
            f(r["saving_per_task_balanced"]), f(r["saving_per_task_f1_only"]),
            r["ci95_overlap"]))

    w("\n## Capped tasks\n")
    w("| arm | composition | mix | capped (arm) | capped (baseline) | "
      "saving/task excluding capped |")
    w("|---|---|---|---|---|---|")
    for r in sorted(a["surface"], key=lambda x: (x["arm"], x["composition"],
                                                 x["mix"])):
        if r["null_seed"] is not None:
            continue
        s = r["sensitivity_excluding_capped"]
        v = s["marginal"]["saving_per_task"] if s and s.get("marginal") else None
        w("| {} | {} | {} | {} | {} | {} |".format(
            r["arm"], r["composition"], r["mix"], f(r["capped_tasks_arm"]),
            f(r["capped_tasks_baseline"]), f(v)))

    w("\n---\n")
    w("Full horizon N={:,}; reduced horizon N={:,} for {}.".format(
        N_FULL, N_REDUCED, ", ".join(REDUCED_ARMS)))
    print("\n".join(L))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
