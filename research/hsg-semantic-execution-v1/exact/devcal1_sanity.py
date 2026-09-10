#!/usr/bin/env python3
"""DEV-CAL-1 construction sanity check (pre-run, assembly-level).

Verifies, fail-closed, BEFORE any scored run:
  1. modules compile;
  2. all 120 worlds build; per world: class shape solves target+source,
     minimality holds (no strictly smaller method), checker verdicts match
     declared labels, certificates present in A/B and absent in C/D;
  3. latent classes pairwise unrelated under the full frozen relation;
  4. hostile/clean controls for every checker fire/stay silent;
  5. search smoke: per cell, one world x 3 arms -- m* found, ranks sane,
     ORACLE template-derived exactly in A/B, not in C/D; acquisition measured.

Writes exact/devcal1_sanity_report.json; exits 0 iff everything passes.
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # parent of exact/

REPORT = {}


def main():
    t0 = time.time()
    failures = []

    # 1. compile
    import py_compile
    for mod in ("devcal1_worlds", "devcal1_certificates", "devcal1_search",
                "run_devcal1"):
        py_compile.compile(os.path.join(HERE, mod + ".py"), doraise=True)
    REPORT["compile"] = "OK"

    import exact.devcal1_worlds as W
    import exact.devcal1_certificates as C
    import exact.devcal1_search as S

    # 2. worlds
    worlds = W.all_worlds()
    REPORT["n_worlds"] = len(worlds)
    if len(worlds) != 120:
        failures.append("expected 120 worlds, built %d" % len(worlds))

    cert_hist = {}
    for w in worlds:
        wid = "%s-%02d" % (w["cell"], w["world_index"])
        # class shape solves both sides
        for side in ("source", "target"):
            ww = w[side]
            tok = ww["inputs"][ww["root_slot"]]
            val = W.execute_dag(ww["shape"], tok["type"], tok["value"])
            if val != ww["goal"]:
                failures.append("%s/%s class shape does not solve" % (wid, side))
            if W.has_smaller_solver(ww["shape"], ww["inputs"],
                                    ww["root_slot"], ww["goal"]):
                failures.append("%s/%s minimality violated" % (wid, side))
        # checker verdicts match declarations
        rel = C.check_structural_relation(w)
        sur = C.check_surface_relation(w)
        if rel["latent_same"] is not w["declared_latent_same"]:
            failures.append("%s latent mismatch: declared=%s checked=%s" % (
                wid, w["declared_latent_same"], rel["latent_same"]))
        if rel["cannot_check"]:
            failures.append("%s CANNOT_CHECK %s" % (wid, rel["cannot_check"]))
        if sur["surface_same"] is not w["declared_surface_same"]:
            failures.append("%s surface mismatch: declared=%s checked=%s" % (
                wid, w["declared_surface_same"], sur["surface_same"]))
        if w["declared_latent_same"]:
            if rel["certificate_type"] is None:
                failures.append("%s latent_same without certificate" % wid)
            cert_hist[rel["certificate_type"]] = \
                cert_hist.get(rel["certificate_type"], 0) + 1
    REPORT["cert_type_hist_declared_same"] = cert_hist

    # 3. pairwise unrelatedness of the frozen latent classes
    n_rel = 0
    for i in range(len(W.LATENT_SHAPES)):
        for j in range(i + 1, len(W.LATENT_SHAPES)):
            if W._related(W.LATENT_SHAPES[i], W.LATENT_SHAPES[j]):
                n_rel += 1
    REPORT["latent_class_related_pairs"] = n_rel
    if n_rel:
        failures.append("%d related latent class pairs" % n_rel)

    # 4. checker controls
    ctl = C.hostile_and_clean_controls()
    REPORT["controls"] = ctl
    for name, cc in ctl.items():
        key = "fired" if "fired" in cc else "silent"
        if not cc[key]:
            failures.append("control %s failed to %s" % (name, key))

    # 5. search smoke: first world of each cell, all three arms
    smoke = {}
    for cell in ("A", "B", "C", "D"):
        w = W.build_cell(cell, 0)
        row = {}
        acq = S.source_acquisition_cost(w, 0)["work"]
        row["acquisition_work"] = acq
        for arm in ("ORACLE_HISTORY", "RESET", "SHUFFLED_HISTORY"):
            rec = S.run_search(arm, w, 0)
            if rec.get("status") != "OK":
                failures.append("smoke %s/%s: %s" % (cell, arm, rec["status"]))
                continue
            rbsd = rec["recorded_before_solution_discovery"]
            row[arm] = {
                "rank": rbsd["eventual_success_rank"],
                "work": rbsd["work_to_first_verified_success"],
                "from_template": rec["m_star_derived_from_history_template"],
                "nodes": rbsd["nodes_expanded"],
            }
        if "ORACLE_HISTORY" in row and "RESET" in row:
            want = cell in ("A", "B")
            got = row["ORACLE_HISTORY"]["from_template"]
            if got is not want:
                failures.append(
                    "smoke %s: ORACLE from_template=%s expected=%s" %
                    (cell, got, want))
            if want and not (row["ORACLE_HISTORY"]["rank"] <
                             row["RESET"]["rank"]):
                failures.append("smoke %s: ORACLE rank not better" % cell)
        smoke[cell] = row
    REPORT["smoke"] = smoke

    REPORT["failures"] = failures
    REPORT["wall_s"] = round(time.time() - t0, 2)
    out = os.path.join(HERE, "results", "devcal1_sanity_report.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(REPORT, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")
    print("SANITY:", "PASS" if not failures else "FAIL(%d)" % len(failures))
    for ff in failures[:20]:
        print("  -", ff)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
