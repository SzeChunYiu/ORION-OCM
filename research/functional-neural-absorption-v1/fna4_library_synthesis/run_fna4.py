"""FNA-4 scored suite driver (FNA4_PROTOCOL.md). Execute on an off-Mac host:

    python3 run_fna4.py <output_dir>

Phases, in order: harness validation -> main comparison (8 arms; the per_op -> per_batch
nogood-granularity revival pair is measured inside it) -> ablation -> revocation cone ->
repeat-rate sweep -> determinism. Output is written progressively
(FNA4_RESULTS_PARTIAL.json) so a crash preserves the defect run; the final artifact is
FNA4_RUN_RECEIPTS.json. All salts live here and are frozen by FNA4_FREEZE.json (and its
addenda) before any scored run.

Acquisition solves run collect_all=True: the paid search runs to its bound and records
every checker-passing chain -- experience is everything the incumbent actually ran, the
identical information surface for every arm. Test solves keep the early exit (fresh-task
cost = time-to-first-solution).
"""
from __future__ import annotations

import itertools
import json
import random
import sys
import traceback
from pathlib import Path

from fna4 import Work, FORBIDDEN_CLAIMS, gen_task, run_chain, make_macro, Misfire
from fna4_solver import MisfireRegistry, solve_task, validate_selection_mirror
import fna4_learners as L

SALT_ACQ = 620001
SALT_TEST = 630001
SALT_SWEEP = 640001
SALT_DETERMINISM = 650001
REVOKED_EV = "ev:fam:filter"
STREAM_LEN = 24          # repeat-rate sweep stream: 12 F1 + 12 F2
R_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
OUT = None


def _dump(results, name="FNA4_RESULTS_PARTIAL.json"):
    if OUT is not None:
        (OUT / name).write_text(json.dumps(results, indent=1, sort_keys=True,
                                           default=str) + "\n")


def acquisition_stream():
    rng = random.Random(SALT_ACQ)
    return [gen_task(rng, "F1", "ACQ-F1-%d" % i) for i in range(4)] + \
           [gen_task(rng, "F2", "ACQ-F2-%d" % i) for i in range(4)]


def test_stream():
    rng = random.Random(SALT_TEST)
    return [gen_task(rng, "F1", "T-F1-%d" % i) for i in range(8)] + \
           [gen_task(rng, "F2", "T-F2-%d" % i) for i in range(4)] + \
           [gen_task(rng, "F3", "T-F3-%d" % i) for i in range(4)]


def run_arm(name, learner=None, registry_gran=None, use_cegis=False):
    """Acquire (first exposure, charged) then solve the test stream. Returns the arm row."""
    acq_tasks = acquisition_stream()
    work_acq = Work()
    registry = MisfireRegistry(registry_gran) if registry_gran else None
    acq_receipts = [solve_task(t, macros=(), registry=registry, work=work_acq,
                               collect_all=True)
                    for t in acq_tasks]
    macros = learner(acq_receipts, work_acq) if learner is not None else []
    acq_work = work_acq.as_dict()
    lib = list(macros)
    test_receipts = []
    for t in test_stream():
        w = Work()
        r = solve_task(t, macros=lib, registry=registry, work=w)
        if use_cegis:
            r["cegis_refinements"] = []
            for att in r["macro_attempts"]:
                if att["misfires"] > 0 and not att["hit"] \
                        and att["first_failed_assignment"] is not None:
                    m = next((m for m in lib if m.macro_id == att["macro_id"]), None)
                    if m is not None:
                        m2, ok = L.specialize(m, tuple(att["first_failed_assignment"]), w)
                        if ok:
                            lib[lib.index(m)] = m2
                            r["cegis_refinements"].append(m2.macro_id)
            r["work"] = w.as_dict()  # CEGIS refinement charged into this task's cost
        test_receipts.append(r)
    return {"arm": name, "acquisition_work": acq_work,
            "library": [m.as_dict() for m in macros],
            "library_size_final": len(lib),
            "acq_solved": sum(1 for r in acq_receipts if r["solved"]),
            "acq_experience_chains": sum(len(r["all_solution_chains"])
                                         for r in acq_receipts),
            "test_receipts": test_receipts,
            "test_solved": sum(1 for r in test_receipts if r["solved"]),
            "test_work_total": sum(r["work"]["total_units"] for r in test_receipts),
            "macro_hits_fresh": sum(r["macro_hits"] for r in test_receipts),
            "misfires_test": sum(r["misfires"] for r in test_receipts)}


def arm_totals(row):
    return row["acquisition_work"]["total_units"] + row["test_work_total"]


def main():
    results = {"schema": "ocm.fna.fna4-library-synthesis.v1", "phases": {},
               "defects": []}
    try:
        # ---- phase 0: harness validation (protocol-mandatory) -------------------
        mirror = validate_selection_mirror(__import__("fna4").INDEX)
        acq_solved = all(solve_task(t).get("solved") for t in acquisition_stream()[:2])
        test_ok = all(solve_task(t).get("solved") for t in test_stream()[:2])
        results["phases"]["harness"] = {"selection_mirror_ok": mirror,
                                        "smoke_solves": acq_solved and test_ok}
        if not (mirror and acq_solved and test_ok):
            results["phases"]["harness"]["terminal"] = \
                "CANNOT_CHECK_SELECTION_MIRROR_DISAGREES_WITH_PRODUCTION_INDEX"
            _dump(results)
            return results
        _dump(results)

        # ---- phase 1: main comparison ------------------------------------------
        arms = [run_arm("NO_LIBRARY"),
                run_arm("CHUNK", learner=L.learn_chunk),
                run_arm("AU_PAIR", learner=L.learn_au),
                run_arm("STITCH", learner=L.learn_stitch),
                run_arm("EGGRAPH", learner=L.learn_egraph),
                run_arm("NOGOOD_ONLY_per_op", registry_gran="per_op"),
                run_arm("NOGOOD_ONLY_per_batch", registry_gran="per_batch"),
                run_arm("STITCH_NOGOOD_CEGIS", learner=L.learn_stitch,
                        registry_gran="per_batch", use_cegis=True)]
        by = {a["arm"]: a for a in arms}
        no = by["NO_LIBRARY"]

        oracle = []
        for t in test_stream():
            sigs = [L.step_sig(n) for n in t.true_chain]
            m = make_macro(tuple(sigs), [sigs], label="ORACLE")
            w = Work()
            r = solve_task(t, macros=[m], work=w)
            r["work"] = w.as_dict()
            oracle.append(r)
        results["phases"]["main"] = {
            "arms": arms,
            "oracle_teleport_LABELLED_UPPER_BOUND": {
                "test_work_total": sum(r["work"]["total_units"] for r in oracle),
                "solved": sum(1 for r in oracle if r["solved"]),
                "macro_hits": sum(r["macro_hits"] for r in oracle)},
            "no_library_test_work_total": no["test_work_total"]}
        _dump(results)

        # ---- phase 2: ablation (library removed mid-stream) --------------------
        macros = L.learn_stitch([solve_task(t, collect_all=True)
                                 for t in acquisition_stream()], Work())
        half1 = test_stream()[:8]
        half2 = test_stream()[8:]
        abl = {"with_library": [], "revoked_mid_stream": []}
        for t in half1:
            abl["with_library"].append(solve_task(t, macros=macros))
        for t in half2:
            abl["revoked_mid_stream"].append(solve_task(t, macros=()))
        no_half1 = [solve_task(t) for t in half1]
        no_half2 = [solve_task(t) for t in half2]
        abl["regression_to_no_library_exact"] = all(
            a["work"] == b["work"] for a, b in zip(abl["revoked_mid_stream"], no_half2))
        # same-mix references: with/without totals are computed over the SAME tasks
        abl["with_library_work_half1"] = sum(r["work"]["total_units"]
                                             for r in abl["with_library"])
        abl["no_library_work_half1"] = sum(r["work"]["total_units"] for r in no_half1)
        abl["revoked_work_half2"] = sum(r["work"]["total_units"]
                                        for r in abl["revoked_mid_stream"])
        abl["no_library_work_half2"] = sum(r["work"]["total_units"] for r in no_half2)
        results["phases"]["ablation"] = abl
        _dump(results)

        # ---- phase 3: revocation cone (H-EC3) -----------------------------------
        cone = {"revoked_evidence": REVOKED_EV, "macros": [], "f2_f3_after": [],
                "f1_tasks_after": []}
        for m in macros:
            expected_live = REVOKED_EV.split("ev:fam:")[1] not in m.families()
            cone["macros"].append({"macro_id": m.macro_id, "families": list(m.families()),
                                   "expected_live": expected_live,
                                   "actual_live": m.warrant.is_live({REVOKED_EV})})
        cone["cone_exact"] = all(r["expected_live"] == r["actual_live"]
                                 for r in cone["macros"])
        cone["stale_survivors"] = sum(1 for r in cone["macros"]
                                      if r["actual_live"] and not r["expected_live"])
        cone["collateral_dead"] = sum(1 for r in cone["macros"]
                                      if r["expected_live"] and not r["actual_live"])
        for t in [t for t in test_stream() if t.family in ("F2", "F3")]:
            w = Work()
            r = solve_task(t, macros=macros, work=w, revoked={REVOKED_EV})
            r["work"] = w.as_dict()
            cone["f2_f3_after"].append(r)
        for t in [t for t in test_stream() if t.family == "F1"][:4]:
            w = Work()
            r = solve_task(t, macros=macros, work=w, revoked={REVOKED_EV})
            r["work"] = w.as_dict()
            cone["f1_tasks_after"].append(r)
        cone["survivors_still_hit"] = sum(r["macro_hits"]
                                          for r in cone["f2_f3_after"])
        cone["f1_capability_lost_by_construction"] = sum(
            1 for r in cone["f1_tasks_after"] if not r["solved"])
        results["phases"]["revocation"] = cone
        _dump(results)

        # ---- phase 4: repeat-rate sweep (critical rate r*) ----------------------
        sweep = {"r_grid": list(R_GRID), "points": []}
        for ri, r in enumerate(R_GRID):
            streams = build_sweep_streams(macros, r, ri)
            if streams is None:
                sweep["points"].append({"r": r, "constructible": False})
                continue
            tasks = streams
            no_w, arm_w = 0, 0
            hits = 0
            for t in tasks:
                no_w += solve_task(t)["work"]["total_units"]
                rr = solve_task(t, macros=macros)
                arm_w += rr["work"]["total_units"]
                hits += rr["macro_hits"]
            acq_units = by["STITCH"]["acquisition_work"]["total_units"]
            sweep["points"].append({
                "r": r, "constructible": True, "actual_covered": streams and
                sum(1 for t in tasks if covered_by(macros, t)),
                "no_library_total": no_w, "stitch_acquisition": acq_units,
                "stitch_with_library_total": arm_w + acq_units,
                "payback": no_w - (arm_w + acq_units), "macro_hits": hits})
        results["phases"]["repeat_rate_sweep"] = sweep
        _dump(results)

        # ---- phase 5: determinism ----------------------------------------------
        rng = random.Random(SALT_DETERMINISM)
        dets = [gen_task(rng, "F1", "D-%d" % i) for i in range(3)]
        r1 = [solve_task(t) for t in dets]
        r2 = [solve_task(t) for t in dets]
        results["phases"]["determinism"] = {
            "identical": all(a["work"] == b["work"] and
                             a["solution_chain"] == b["solution_chain"]
                             for a, b in zip(r1, r2))}
        _dump(results)
        (OUT / "FNA4_RUN_RECEIPTS.json").write_text(
            json.dumps(results, indent=1, sort_keys=True, default=str) + "\n")
        return results
    except Exception as exc:  # defect run preserved, never edited
        results["defects"].append({"phase": "crash", "error": repr(exc),
                                   "traceback": traceback.format_exc()})
        _dump(results)
        raise


def covered_by(macros, task):
    """A task is covered iff some macro assignment (within the enumeration cap)
    reproduces the goal when its body runs on the task's initial atoms. Stream
    construction only -- no arm ever sees task.true_chain or goal shortcuts."""
    for m in macros:
        for a in m.assignments():
            try:
                if run_chain(m.body_names(a), task.initial) == task.goal:
                    return True
            except (Misfire, KeyError, ValueError, IndexError):
                continue
    return False


def _f1_param_space():
    fmts = ("csv", "jsonl")
    for fmt, fk, sd, sk, af, ak, k in itertools.product(
            fmts, ("f0", "f1", "f2"), ("asc", "desc"), ("f0", "f1", "f2"),
            ("sum", "mean", "count"), ("f0", "f1", "f2"), ("2", "3")):
        yield {"fmt": fmt, "fk": fk, "sd": sd, "sk": sk, "af": af, "ak": ak, "k": k}


def _f2_param_space():
    for (fa, fb), af, ak in itertools.product(
            (("csv", "jsonl"), ("jsonl", "csv")), ("sum", "mean"),
            ("f0", "f1", "f2")):
        yield {"fmt_pair": (fa, fb), "af": af, "ak": ak}


def build_sweep_streams(macros, r, ri):
    """Construct a 12 F1 + 12 F2 stream with round(r*24) covered tasks, fresh payloads.
    Covered tasks draw parameters until a covered draw appears; uncovered tasks take the
    next parameter tuple that no macro covers. Returns None if the quota is not
    constructible (coverage is total)."""
    need_cov = int(round(r * STREAM_LEN))
    per_family = STREAM_LEN // 2
    need_cov_f = need_cov // 2 + (1 if need_cov % 2 and r > 0 else 0)
    rng = random.Random(SALT_SWEEP + 1000 * ri)
    tasks = []

    def want(family, force, uid):
        t = gen_task(rng, family, uid, force=force)
        return t

    for family, space in (("F1", _f1_param_space()), ("F2", _f2_param_space())):
        ncov = need_cov_f if family == "F1" else need_cov - need_cov_f
        ncov = max(0, min(per_family, ncov))
        nun = per_family - ncov
        got_cov = got_un = 0
        # covered draws: rejection-sample draws from the sweep salt
        tries = 0
        while got_cov < ncov and tries < 4000:
            tries += 1
            t = gen_task(rng, family, "S-%s-%d-%d" % (family, ri, got_cov + got_un))
            if covered_by(macros, t):
                tasks.append(t)
                got_cov += 1
        # uncovered draws: forced parameter tuples outside every macro's cover
        for force in space:
            if got_un >= nun:
                break
            t = want(family, force, "S-%s-%d-u%d" % (family, ri, got_un))
            if not covered_by(macros, t):
                tasks.append(t)
                got_un += 1
        if got_cov < ncov or got_un < nun:
            return None
    return tasks


if __name__ == "__main__":
    OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    res = main()
    txt = json.dumps(res, default=str)
    bad = [c for c in FORBIDDEN_CLAIMS if c in txt]
    print("forbidden_claims_present:", bad)
    print("phases:", sorted(res.get("phases", {})))
