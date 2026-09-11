"""Independent cross-check of RV8_ANALYSIS.json.

Not part of the frozen analysis and not a source of any reported number. Its only job
is to recompute a few rows of the surface from the raw cell files by a DIFFERENT route
-- reading the gzipped cells directly, re-deriving the family sequence from the frozen
generator, and summing by hand -- and to disagree loudly if the frozen analysis and this
route do not land on the same figures.

A checker is not trusted until it has been run against real data including the case
where it must NOT fire, so this also runs a deliberate control that must report a
mismatch.

    python3 rv8_verify.py <out_dir>
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rv8_horizon import (COMPOSITIONS, FAMILY_ORDER, MIX_GRID,  # noqa: E402
                         STREAM_SEEDS, cell_inventory, family_sequence)

TOL = 1e-9


def read_cell(out, idx):
    p = out / "cells" / ("cell_%05d.json.gz" % idx)
    if not p.exists():
        return None
    with gzip.open(str(p), "rt") as fh:
        return json.load(fh)


def index_cells(out):
    idx = {}
    for i, spec in enumerate(cell_inventory()):
        c = read_cell(out, i)
        if c is None:
            continue
        idx[(c["arm"], c["mix_idx"], c["composition"], c["seed"],
             c["null_seed"])] = c
    return idx


def recompute(cells, arm, mi, comp, null_seed=None,
              seeds=STREAM_SEEDS):
    """Paired saving and per-family attribution, computed by hand."""
    tot, n = 0, 0
    fam = dict((f, [0, 0]) for f in FAMILY_ORDER)      # family -> [sum, count]
    acq_m = acq_f = None
    for s in seeds:
        base = cells.get(("NO_LIBRARY", mi, comp, s, None))
        a = cells.get((arm, mi, comp, s, null_seed))
        if base is None or a is None:
            continue
        bu = base["per_task"]["units"]
        au = a["per_task"]["units"]
        acq_m = a["acquisition_marginal_units"]
        acq_f = a["acquisition_full_units"]
        k = min(len(bu), len(au))
        fseq = family_sequence(MIX_GRID[mi], comp, k)
        for i in range(k):
            d = bu[i] - au[i]
            tot += d
            n += 1
            fam[fseq[i]][0] += d
            fam[fseq[i]][1] += 1
    if not n:
        return None
    return {"saving_per_task": tot / float(n), "n": n,
            "saving_total": tot, "acq_marginal": acq_m, "acq_full": acq_f,
            "per_family": dict((f, {"n": v[1],
                                    "saving_per_task": v[0] / float(v[1])})
                               for f, v in fam.items() if v[1])}


def main(out):
    cells = index_cells(out)
    ana = json.loads((out / "RV8_ANALYSIS.json").read_text())
    rows = {}
    for r in ana["surface"]:
        rows[(r["arm"], r["mix_idx"], r["composition"], r["null_seed"])] = r

    checked, mismatched, skipped = 0, [], 0
    for (arm, mi, comp, ns), r in sorted(rows.items()):
        seeds = (STREAM_SEEDS[0],) if ns is not None else STREAM_SEEDS
        mine = recompute(cells, arm, mi, comp, ns, seeds)
        if mine is None:
            skipped += 1
            continue
        checked += 1
        theirs = r["marginal"]["saving_per_task"]
        bad = []
        if abs(mine["saving_per_task"] - theirs) > max(TOL, abs(theirs) * 1e-12):
            bad.append(("saving_per_task", mine["saving_per_task"], theirs))
        if mine["n"] != r["tasks_total"]:
            bad.append(("tasks_total", mine["n"], r["tasks_total"]))
        for f, v in mine["per_family"].items():
            t = r.get("per_family_saving", {}).get(f)
            if t is None:
                bad.append(("per_family_missing:" + f, v, None))
            elif abs(v["saving_per_task"] - t["saving_per_task"]) > \
                    max(TOL, abs(t["saving_per_task"]) * 1e-12):
                bad.append(("per_family:" + f, v["saving_per_task"],
                            t["saving_per_task"]))
        if bad:
            mismatched.append({"arm": arm, "mix_idx": mi, "composition": comp,
                               "null_seed": ns, "diffs": bad})

    # CONTROLS: agreement is not evidence unless the comparison can FAIL. Two of them,
    # the first of which always runs so thin grid coverage cannot leave the checker
    # unfired and silently inert.
    #
    # (1) synthetic: perturb a recomputed value by a known amount and require the same
    #     comparison that produced "agree" to flag it.
    # (2) cross-mix: compare a row against a DIFFERENT mix's recomputation, when the
    #     loaded cells hold two mixes for one arm.
    control_synthetic = None
    control_cross_mix = None
    keys = sorted(rows)
    for (arm, mi, comp, ns) in keys:
        seeds = (STREAM_SEEDS[0],) if ns is not None else STREAM_SEEDS
        mine = recompute(cells, arm, mi, comp, ns, seeds)
        if mine is None:
            continue
        theirs = rows[(arm, mi, comp, ns)]["marginal"]["saving_per_task"]
        control_synthetic = abs((mine["saving_per_task"] + 1.0) - theirs) > max(
            TOL, abs(theirs) * 1e-12)
        break
    for k1 in keys:
        arm, mi, comp, ns = k1
        if ns is not None:
            continue
        other = [k for k in keys if k[0] == arm and k[3] is None and k[1] != mi]
        if not other:
            continue
        mine = recompute(cells, arm, other[0][1], comp, None, STREAM_SEEDS)
        if mine is None:
            continue
        control_cross_mix = abs(mine["saving_per_task"] -
                                rows[k1]["marginal"]["saving_per_task"]) > TOL
        break
    control_fired = bool(control_synthetic) and (control_cross_mix is not False)

    print(json.dumps({"rows_checked": checked, "rows_skipped": skipped,
                      "mismatched": mismatched,
                      "agree": not mismatched and checked > 0,
                      "control_can_fire": control_fired,
                      "control_synthetic": control_synthetic,
                      "control_cross_mix": control_cross_mix,
                      "NOTE": "run against a SNAPSHOT of out/cells, never the live "
                              "directory: cells are rewritten every 4,096 tasks, so a "
                              "live read gives the analysis and this verifier different "
                              "bytes and they will disagree for that reason alone"},
                     indent=1, default=str))
    return 0 if (not mismatched and checked > 0 and control_fired) else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]).resolve()))
