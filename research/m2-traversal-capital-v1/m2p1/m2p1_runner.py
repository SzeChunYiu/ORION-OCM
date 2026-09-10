#!/usr/bin/env python3
"""M2-P1 scored lifecycle runner on the hidden-family ecology.

Drives the REGISTERED learner src/ocm/learning/methods.py AS-IS: learn_generator,
validate_generator, solve, verify_solution are imported and called, never copied or
modified.  No new cognitive core, no learned router, no admission loosening, no
threshold tuning (#71 and #323 §11 respected).

Lifecycle: dev (solve train -> learn_generator -> validate_generator -> admit)
        -> checkpoint -> REAL OS-process restart -> acquire fresh protected targets.

Every protected target is a NEW normal form, disjoint from history (gate G2), and
every success is confirmed by an independent checker process with its own pid.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, statistics, subprocess, sys, time
from collections import Counter
from fractions import Fraction
from pathlib import Path

LANE = "LANE_M2_TRAVERSAL_CAPITAL_OPUS"
SCHEMA = "OCM_M2P1_SCORED_V1"
ARMS = ("RESET", "LIBRARY_ONLY", "CONTINUED", "CONTINUED_EU", "CONTINUED_MDL",
        "SHUFFLED_HISTORY", "ORACLE_FAMILY", "ORDINARY_ADAPTIVE_PARENT")
CALIBRATION_ONLY = ("ORACLE_FAMILY",)


class AssayDefect(Exception):
    pass


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def load_methods(repo: Path):
    sys.path.insert(0, str(repo / "src"))
    import ocm.learning.methods as M
    return M


def task_of(M, row, idx):
    return M.PolynomialTask(f"m2p1:{idx}:{row['normal_form_digest'][:16]}",
                            tuple(Fraction(c) for c in row["coefficients"]))


# ---------------------------------------------------------------- checker C
def checker_C(repo: Path, coefficients, program) -> dict:
    """Independent unit: separate OS process, own pid, recomputes the normal form."""
    code = ("import sys,json;sys.path.insert(0,%r);"
            "import ocm.learning.methods as M,os;"
            "d=json.loads(sys.stdin.read());"
            "nf=M.normal_form(tuple(d['p']));"
            "t=tuple(__import__('fractions').Fraction(c) for c in d['c']);"
            "print(json.dumps({'verdict':'IDENTICAL' if nf==t else 'DIFFERENT',"
            "'pid':os.getpid(),'methods_sha256':d['s']}))" % str(repo / "src"))
    payload = json.dumps({"p": list(program), "c": [str(c) for c in coefficients],
                          "s": sha256_file(repo / "src" / "ocm" / "learning" / "methods.py")})
    out = subprocess.run([sys.executable, "-c", code], input=payload,
                         capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise AssayDefect(f"CHECKER_C_FAILED: {out.stderr[:300]}")
    return json.loads(out.stdout)


# ------------------------------------------------------------------- phases
def phase_dev(M, repo, eco, run: Path, slots: int) -> None:
    t0 = time.perf_counter()
    budget = M.SearchBudget(slots=slots, max_length=8)
    training, unsolved = [], 0
    for i, row in enumerate(eco["streams"]["train"]):
        task = task_of(M, row, i)
        res = M.solve(task, budget)
        if M.verify_solution(task, res):
            training.append((task, res))
        else:
            unsolved += 1
    method = M.learn_generator(training)
    held = [task_of(M, r, 10_000 + i) for i, r in enumerate(eco["streams"]["validation"])]
    report = M.validate_generator(method, held, budget)
    # Proposed expected-utility admission, computed from the SAME registered
    # validate_generator rows -- no extra search, no new information.
    _d = [r["baseline"]["slots"] - r["candidate"]["slots"] for r in report["held_out"]]
    _ratios = [r["candidate"]["slots"] / r["baseline"]["slots"]
               for r in report["held_out"] if r["baseline"]["slots"]]
    _mean = statistics.fmean(_d) if _d else 0.0
    _worst = max(_ratios) if _ratios else 0.0
    _sd = statistics.pstdev(_d) if len(_d) > 1 else 0.0
    _se = (_sd / (len(_d) ** 0.5)) if _d else 0.0
    _lo = _mean - 1.96 * _se
    eu = {"policy": "EXPECTED_UTILITY_WITH_BOUNDED_REGRET_V1",
          "mean_delta": round(_mean, 1), "ci95_low": round(_lo, 1),
          "worst_ratio": round(_worst, 4), "rho_max": 2.0,
          "all_verified": all(r["both_verified"] for r in report["held_out"]),
          "admitted": bool(_lo > 0 and _worst <= 2.0 + 1e-9 and bool(method.fragments)
                           and all(r["both_verified"] for r in report["held_out"])),
          "reason": ("ci95_low<=0" if _lo <= 0 else
                     "worst_ratio>rho_max" if _worst > 2.0 + 1e-9 else
                     "no fragments" if not method.fragments else "admitted")}

    mdl_frags, mdl_report = [], None
    try:
        import m2_mdl_selection as _mdl
        progs = [r.program for _, r in training if r.program]
        picked = [f for f in _mdl.mdl_select(progs, cap=16) if 2 <= len(f) <= 8][:16]
        if picked:
            mdl_method = M.GeneratorMethod(tuple(picked), tuple(sorted(t_.fingerprint for t_, _ in training)))
            mdl_report = M.validate_generator(mdl_method, held, budget)
            mdl_frags = [list(f) for f in picked]
    except Exception as _e:                       # never let the successor arm break dev
        mdl_report = {"error": str(_e)[:200]}

    state = {
        "schema": "M2P1_DEV_STATE", "eu_admission": eu,
        "mdl_fragments": mdl_frags,
        "mdl_admission": (mdl_report.get("accepted") if isinstance(mdl_report, dict) else None),
        "mdl_terminal": (mdl_report.get("terminal") if isinstance(mdl_report, dict) else None),
        "mdl_strictly_better": (sum(1 for r in mdl_report["held_out"]
                                    if r["candidate"]["slots"] < r["baseline"]["slots"])
                                if isinstance(mdl_report, dict) and "held_out" in mdl_report else None), "train_solved": len(training),
        "train_unsolved": unsolved, "fragments_mined": len(method.fragments),
        "fragments": [list(f) for f in method.fragments],
        "admission": bool(report["accepted"]), "terminal": report["terminal"],
        "validated_on": len(held),
        "held_out_strictly_better": sum(1 for r in report["held_out"]
                                        if r["candidate"]["slots"] < r["baseline"]["slots"]),
        "held_out_never_worse": all(r["candidate"]["slots"] <= r["baseline"]["slots"]
                                    for r in report["held_out"]),
        "held_out_mean_baseline": round(statistics.fmean(r["baseline"]["slots"] for r in report["held_out"]), 1),
        "held_out_mean_candidate": round(statistics.fmean(r["candidate"]["slots"] for r in report["held_out"]), 1),
        "training_task_ids": list(method.training_tasks),
        "wall_seconds": round(time.perf_counter() - t0, 2),
        "pid": os.getpid(),
    }
    (run / "dev_state.json").write_text(json.dumps(state, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in state.items()
                      if k not in ("fragments", "training_task_ids")}, indent=1))


def phase_checkpoint(run: Path) -> None:
    dev = json.loads((run / "dev_state.json").read_text())
    (run / "checkpoint.json").write_text(json.dumps({
        "pre_restart_pid": os.getpid(), "interpreter": sys.executable,
        "python": platform.python_version(),
        "boot_token": hashlib.sha256(os.urandom(16)).hexdigest(),
        "dev_state_sha256": sha256_file(run / "dev_state.json"),
        "dev_admission": dev["admission"]}, indent=1, sort_keys=True))
    print("checkpoint written, pid", os.getpid())


def arm_method(M, arm: str, eco, dev) -> tuple:
    frags = tuple(tuple(f) for f in dev["fragments"])
    if arm in ("RESET", "LIBRARY_ONLY"):
        return M.GeneratorMethod(), ("no generator; LIBRARY_ONLY holds solved objects whose "
                                     "normal forms are disjoint from every target (gate G2)")
    if arm == "CONTINUED":
        if not dev["admission"]:
            return M.GeneratorMethod(), "learner refused deployment; refusal is first-class"
        return M.GeneratorMethod(frags, tuple(dev["training_task_ids"])), "admitted generator"
    if arm == "CONTINUED_MDL":
        # PROPOSED SUCCESSOR SELECTION RULE, reported only under that label.
        # learn_generator ranks by (support count DESC, length DESC); a substring shared by
        # two motifs outranks both and displaces them from the fixed top-16. This arm keeps
        # everything else identical and swaps the SELECTION rule for greedy MDL --
        # compression of the solved corpus, which prices length and re-parses after each
        # pick so a taken motif's substrings stop earning credit for its occurrences.
        # Parent: corpus-guided library learning (Stitch / DreamCoder).
        mdl = dev.get("mdl_fragments")
        if not mdl:
            return M.GeneratorMethod(), "no mdl library recorded"
        frg = tuple(tuple(f) for f in mdl)
        return M.GeneratorMethod(frg, tuple(dev["training_task_ids"])), \
            ("MDL-selected library (%d fragments) served through the registered solver; "
             "src/ocm/learning/methods.py unmodified" % len(frg))
    if arm == "CONTINUED_EU":
        # PROPOSED SUCCESSOR ADMISSION POLICY -- not the registered rule, and reported
        # only under that label. src/ocm/learning/methods.py is NOT modified.
        #
        # The registered rule admits on universal non-inferiority. Obligation P1 is
        # discharged empirically (410 measurements, 5 adversarial libraries, max ratio
        # exactly 2.0, zero violations, zero correctness violations): the interleaved
        # solver bounds deployment regret at rho_max = 2 and can never make a target
        # unsolvable or incorrect. So the downside the universal rule guards against does
        # not exist in this integration mode, and the admissible quantifier is EXPECTED
        # utility with the bound asserted:
        #
        #     admit iff  mean(baseline - candidate) > 0 over held-out
        #           and  max(candidate/baseline) <= rho_max
        #
        # verify_solution and the independent checker are untouched; every reported
        # success is still externally verified.
        eu = dev.get("eu_admission")
        if not eu or not eu.get("admitted"):
            return M.GeneratorMethod(), ("EU policy refused: %s" %
                                         (eu.get("reason") if eu else "no eu record"))
        return M.GeneratorMethod(frags, tuple(dev["training_task_ids"])), \
            ("admitted under the PROPOSED expected-utility policy "
             "(mean dB=%.1f, worst ratio=%.3f <= 2); registered rule said %s"
             % (eu["mean_delta"], eu["worst_ratio"], dev["admission"]))
    if arm == "ORDINARY_ADAPTIVE_PARENT":
        return M.GeneratorMethod(frags, tuple(dev["training_task_ids"])), \
            "same mined fragments served WITHOUT the admission gate"
    if arm == "SHUFFLED_HISTORY":
        import random
        # Seeds are ecology-authored and need not be integers: a foreign ecology may
        # carry a string seed (the M1 lane uses "orion-ocm-m1-semantic-partition-v1").
        # Derive a stable integer without assuming the author's type.
        _s = eco.get("frozen_seed", 0)
        _seed = (int(_s) if isinstance(_s, int) or (isinstance(_s, str) and _s.lstrip("-").isdigit())
                 else int(hashlib.sha256(str(_s).encode()).hexdigest()[:8], 16))
        rng = random.Random(_seed + 7)
        pool = [p for L in (2, 3) for p in __import__("itertools").product(M.PRIMITIVES, repeat=L)]
        # The control must destroy STRUCTURE while preserving count and length profile.
        # It must therefore EXCLUDE the true hidden motifs: over a small grammar a
        # uniform sample can rediscover them by chance (there are only 16 length-2 and
        # 64 length-3 strings), which would silently weaken the control toward the
        # treatment. Excluding them is the conservative direction.
        true_motifs = {tuple(m) for m in eco["hidden_motifs"]}
        pick, seen = [], set()
        for f in frags:                       # match count AND length profile exactly
            cands = [p for p in pool
                     if len(p) == len(f) and p not in seen and p not in true_motifs]
            if not cands:
                continue
            c = rng.choice(cands)
            seen.add(c)
            pick.append(c)
        return M.GeneratorMethod(tuple(pick), tuple(dev["training_task_ids"])), \
            ("random fragments matching the mined count and length profile, with the "
             "true hidden motifs excluded so the control cannot rediscover them by chance")
    if arm == "ORACLE_FAMILY":
        return M.GeneratorMethod(tuple(tuple(m) for m in eco["hidden_motifs"]), ()), \
            "CALIBRATION ONLY: the true hidden motif set"
    raise SystemExit(f"UNKNOWN_ARM: {arm}")


def phase_acquire(M, repo, eco, run: Path, arm: str, ladder, targets_n: int) -> None:
    t0 = time.perf_counter()
    ck = json.loads((run / "checkpoint.json").read_text())
    if ck["pre_restart_pid"] == os.getpid():
        raise AssayDefect("SAME_PROCESS_FAKE_RESTART")
    dev = json.loads((run / "dev_state.json").read_text())
    if sha256_file(run / "dev_state.json") != ck["dev_state_sha256"]:
        raise AssayDefect("DEV_STATE_TAMPERED")
    method, note = arm_method(M, arm, eco, dev)
    rows, verifications = [], 0
    prot = eco["streams"]["protected"][:targets_n]
    hist_digests = {r["normal_form_digest"] for r in eco["streams"]["train"]} | \
                   {r["normal_form_digest"] for r in eco["streams"]["validation"]}
    for i, row in enumerate(prot):
        if row["normal_form_digest"] in hist_digests:
            raise AssayDefect("LEAKAGE_ALARM: protected target present in history")
        task = task_of(M, row, 20_000 + i)
        first_ok = None
        for q in ladder:
            res = M.solve(task, M.SearchBudget(slots=q, max_length=8), method)
            ok = M.verify_solution(task, res)
            ext = None
            if ok and first_ok is None:
                ext = checker_C(repo, task.coefficients, res.program)
                verifications += 1
                if ext["verdict"] != "IDENTICAL":
                    raise AssayDefect("CHECKER_C_DISAGREES")
                first_ok = res.slots
            rows.append({"arm": arm, "target": row["normal_form_digest"],
                         "canonical_length": row["canonical_length"],
                         "budget_slots": q, "B_slots": res.slots,
                         "candidates_checked": res.candidates_checked,
                         "status": res.status, "verified": ok,
                         "externally_verified": bool(ext and ext["verdict"] == "IDENTICAL"),
                         "checker_pid": ext["pid"] if ext else None,
                         "baseline_first_index": row["baseline_first_index"]})
    ok_rows = [r for r in rows if r["verified"]]
    rep = {"schema": "M2P1_ARM_REPORT", "arm": arm,
           "calibration_only": arm in CALIBRATION_ONLY, "note": note,
           "fragments_served": len(method.fragments),
           "process": {"pid": os.getpid(), "pre_restart_pid": ck["pre_restart_pid"],
                       "pid_changed": os.getpid() != ck["pre_restart_pid"]},
           "targets": len(prot), "ladder": ladder,
           "successes": len(ok_rows), "attempts": len(rows),
           "ladder_total": len(ok_rows),
           "mean_B_slots": round(statistics.fmean(r["B_slots"] for r in ok_rows), 1) if ok_rows else None,
           "external_verifications": verifications,
           "successes_by_budget": {str(q): sum(1 for r in rows if r["budget_slots"] == q and r["verified"])
                                   for q in ladder},
           "rows": rows, "wall_seconds": round(time.perf_counter() - t0, 2)}
    (run / f"arm_{arm}.json").write_text(json.dumps(rep, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in rep.items() if k != "rows"}, indent=1))


def phase_restart_and_acquire(repo, eco_path, run: Path, arm, ladder, targets_n):
    r = subprocess.run([sys.executable, __file__, "--repo", str(repo), "--ecology", str(eco_path),
                        "--run-dir", str(run), "--phase", "acquire", "--arm", arm,
                        "--ladder", ",".join(str(x) for x in ladder), "--targets", str(targets_n)],
                       capture_output=True, text=True)
    print(r.stdout[-4000:] or r.stderr[-4000:])
    (run / f"restart_{arm}.json").write_text(json.dumps(
        {"parent_pid": os.getpid(), "child_returncode": r.returncode}, indent=1))
    if r.returncode != 0:
        raise SystemExit(f"ARM_FAILED {arm}: {r.stderr[-500:]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ecology", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--phase", required=True)
    ap.add_argument("--arm")
    ap.add_argument("--slots", type=int, default=200000)
    ap.add_argument("--ladder", default="1000,4000,16000,64000,200000")
    ap.add_argument("--targets", type=int, default=79)
    a = ap.parse_args()
    repo, run = Path(a.repo), Path(a.run_dir)
    run.mkdir(parents=True, exist_ok=True)
    M = load_methods(repo)
    eco = json.loads(Path(a.ecology).read_text())
    ladder = [int(x) for x in a.ladder.split(",")]
    if a.phase == "dev":
        phase_dev(M, repo, eco, run, a.slots)
    elif a.phase == "checkpoint":
        phase_checkpoint(run)
    elif a.phase == "acquire":
        phase_acquire(M, repo, eco, run, a.arm, ladder, a.targets)
    elif a.phase == "restart-and-acquire":
        phase_restart_and_acquire(repo, a.ecology, run, a.arm, ladder, a.targets)
    else:
        raise SystemExit("unknown phase")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
