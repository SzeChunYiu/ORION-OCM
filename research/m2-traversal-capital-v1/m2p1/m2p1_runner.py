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
        "SHUFFLED_HISTORY", "ORACLE_FAMILY", "ORDINARY_ADAPTIVE_PARENT",
        "PARENT_WITH_MDL", "CONTINUED_OCM", "CONTINUAL_OCM")
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


# ------------------------------------------------ integrated developmental controller
def _tile_tokens(prog, lib):
    n = len(prog); best = [None] * (n + 1); best[0] = 0
    for i in range(n):
        if best[i] is None:
            continue
        for f in lib:
            j = i + len(f)
            if j <= n and tuple(prog[i:j]) == tuple(f) and (best[j] is None or best[i] + 1 < best[j]):
                best[j] = best[i] + 1
    return best[n]


def _obs_feats(nf, lib):
    deg = len(nf) - 1
    sup = sum(1 for c in nf if c != 0)
    mag = max(max(abs(c.numerator).bit_length(), abs(c.denominator).bit_length()) for c in nf)
    return [min(deg, 8), min(sup, 6), min(mag // 4, 6), min(len(lib), 16) // 4]


def _probe(M, nf, lib, depth, beta):
    """guided stream ALONE, words of <= depth tokens, every word one charged slot"""
    from itertools import product as _prod
    tokens = tuple(lib) + tuple((op,) for op in M.PRIMITIVES)
    used = 0
    for L in range(1, depth + 1):
        for word in _prod(tokens, repeat=L):
            used += 1
            if used > beta:
                return None, beta
            prog = tuple(op for tok in word for op in tok)
            if len(prog) > 8:
                continue
            if M.normal_form(prog) == nf:
                return prog, used
    return None, used


# ------------------------------------------------ continual development (CONTINUAL_OCM)
CONTINUAL = {"mine_n": 32, "val_n": 8, "min_new": 16, "min_corpus": 12, "standdown_misses": 3, "min_new_after_fail": 8, "value_window": 8, "version": "continual_v5.2"}
# v5: VALUE-BASED liveness. s604: a 16-fragment learned library (beta 8 420) kept hitting one
# A-prime target in three and was therefore never stood down by the consecutive-miss rule,
# paying beta + baseline on every miss for 17 targets. A library stays live while the realised
# delta over the last value_window targets (hit: expected baseline - position; miss: -probe cost)
# is non-negative; a hit that does not pay for its misses stands the library down.
# v4.2: a FAILED validation is evidence the corpus was too small, not a reason to wait for 16 more
# solutions; the next attempt comes at the next re-probe with >= 8 new solutions (s603: the
# attempt at 72 failed on a 17-program corpus and the deployment waited until 88).
# v4: min_corpus 8 -> 12. On SHIFT45 the v3 attempt on an 8-program corpus failed validation and
# charged 9 556 slots; the 13- and 24-program attempts (v2, v3) both deployed. Registered on
# SHIFT45 and on a fresh shift world before the run.


def _fit_controller(M, lib, val_rows):
    """Fit depth / rule / fallback for `lib` on a held-out slice of the organism's OWN
    solved history: val_rows = [(task, program, baseline_B)]. Same rules as the dev-phase
    controller_v2 (expected-cost depth, per-cell rule), but the candidate cost of each
    validation task is measured by a CHARGED guided-only probe, never by a second full solve."""
    T = len(lib) + len(M.PRIMITIVES)
    hist = []
    for _t, prog, bs in val_rows:
        d = _tile_tokens(tuple(prog), lib) if prog else None
        hist.append((d if d is not None else 99, bs))
    depth, bc = 3, float("inf")
    for D in range(1, 5):
        bD = sum(T ** i for i in range(1, D + 1))
        c = statistics.fmean((sum(T ** j for j in range(1, d_)) + T ** d_ / 2) if d_ <= D else bD + b_
                             for d_, b_ in hist) if hist else float("inf")
        if c < bc:
            depth, bc = D, c
    beta = sum(T ** i for i in range(1, depth + 1))
    charged, deltas, cells, detail = 0, [], {}, []
    # v5.2: validation probes buy INFORMATION, not savings. The deployment criterion is
    # "strictly better on more than half of the slice", and a task that does not tile in
    # <= depth tokens cannot be a strict win, so (a) a candidate with tilable tasks <= n/2 is
    # rejected before any probe is charged, and (b) probing stops as soon as the majority is
    # out of reach. FV8: two attempts charged 65 k each on candidates with 1/8 tilable tasks.
    n_val = len(val_rows); tilable = sum(1 for d_t, _ in hist if d_t <= depth)
    if tilable * 2 <= n_val:
        return {"lib": [list(f) for f in lib], "probe_depth": depth, "beta": beta, "rule": {},
                "expected_baseline": round(statistics.fmean(bs for _, _, bs in val_rows), 1) if val_rows else None,
                "fallback": False, "val_mean_delta": 0.0, "val_better": 0, "val_n": n_val,
                "fit_detail": [], "tiling_probe_violations": 0, "tilable_at_depth": tilable,
                "skipped_probes": "cannot reach majority (%d/%d tilable)" % (tilable, n_val)}, 0
    order = sorted(range(n_val), key=lambda i: hist[i][0])          # tilable tasks first
    hits_so_far, remaining_tilable = 0, tilable
    for i in order:
        (task, prog, bs), (d_t, _) = val_rows[i], hist[i]
        if d_t <= depth:
            remaining_tilable -= 1
        if (hits_so_far + remaining_tilable + (1 if d_t <= depth else 0)) * 2 <= n_val:
            # the majority is already out of reach: stop paying for information
            deltas.append(-1); cells.setdefault(str(_obs_feats(task.coefficients, lib)), []).append(-1)
            detail.append({"tiling": d_t, "hit": False, "used": 0, "baseline": bs, "unprobed": True})
            continue
        pr, used = _probe(M, task.coefficients, lib, depth, beta)
        charged += used
        if pr is not None:
            hits_so_far += 1
        cand = used if pr is not None else used + bs       # miss: probe + the baseline it would then pay
        deltas.append(bs - cand)
        cells.setdefault(str(_obs_feats(task.coefficients, lib)), []).append(bs - cand)
        detail.append({"tiling": d_t, "hit": pr is not None, "used": used, "baseline": bs})
    # INVARIANT (assay): a validation program that tiles in <= depth tokens must be reachable by
    # the probe at <= beta words. A violation means the depth rule and the probe disagree about
    # the library and the fit is untrustworthy; it is recorded, never smoothed.
    violations = [x for x in detail if x["tiling"] <= depth and not x["hit"]]
    rule = {z: (statistics.fmean(v) > 0) for z, v in cells.items()}
    better = sum(1 for d in deltas if d > 0)
    return {"lib": [list(f) for f in lib], "probe_depth": depth, "beta": beta, "rule": rule,
            "fit_detail": detail, "tiling_probe_violations": len(violations),
            "expected_baseline": round(statistics.fmean(bs for _, _, bs in val_rows), 1) if val_rows else None,
            "fallback": (statistics.fmean(deltas) > 0) if deltas else False,
            "val_mean_delta": round(statistics.fmean(deltas), 1) if deltas else 0.0,
            "val_better": better, "val_n": len(deltas)}, charged


def _remine(M, solved):
    """Mine candidate libraries from the organism's own verified acquisitions and validate
    them on the most recent held-out slice. solved = [(task, SearchResult, B)] in order,
    RESTRICTED by the caller to the current regime (solutions since the last stand-down):
    continual_v1 mined a window that straddled the shift, so its first attempt learned
    the old regime and its second came too late to pay. Returns
    (controller_record or None, charged_slots, event)."""
    if len(solved) < CONTINUAL["val_n"] + CONTINUAL["min_corpus"]:
        return None, 0, {"skipped": "too few solutions in this regime", "regime_solved": len(solved)}
    val = solved[-CONTINUAL["val_n"]:]
    corpus = solved[-(CONTINUAL["mine_n"] + CONTINUAL["val_n"]):-CONTINUAL["val_n"]]
    if len(corpus) < CONTINUAL["min_corpus"]:
        return None, 0, {"skipped": "corpus too small", "corpus": len(corpus)}
    val_rows = [(t, r.program, b) for t, r, b in val]
    cands = {}
    try:
        cands["frequency"] = tuple(M.learn_generator([(t, r) for t, r, _ in corpus]).fragments)
    except Exception:
        cands["frequency"] = ()
    try:
        import m2_mdl_selection as _mdl
        picked = [f for f in _mdl.mdl_select([r.program for _, r, _ in corpus], cap=16) if 2 <= len(f) <= 8][:16]
        cands["mdl"] = tuple(tuple(f) for f in picked)
    except Exception:
        cands["mdl"] = ()
    charged, fitted = 0, {}
    for name, lib in cands.items():
        if not lib:
            continue
        rec, c = _fit_controller(M, list(lib), val_rows)
        charged += c; rec["library"] = name; fitted[name] = rec
    if not fitted:
        return None, charged, {"skipped": "no candidate library", "charged": charged}
    best = max(fitted.values(), key=lambda r: (r["val_better"], r["val_mean_delta"]))
    ok = best["val_mean_delta"] > 0 and best["val_better"] * 2 > best["val_n"]
    ev = {"corpus": len(corpus), "validated_on": len(val_rows), "charged": charged,
          "candidates": {k: {"n": len(v["lib"]), "val_better": v["val_better"], "val_mean_delta": v["val_mean_delta"],
                             "depth": v["probe_depth"], "beta": v["beta"],
                             "tilable_at_depth": sum(1 for x in v["fit_detail"] if x["tiling"] <= v["probe_depth"]),
                             "hits": sum(1 for x in v["fit_detail"] if x["hit"]),
                             "tiling_probe_violations": v["tiling_probe_violations"]} for k, v in fitted.items()},
          "chosen": best["library"], "deployed": bool(ok)}
    return (best if ok else None), charged, ev


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

    ocm_ctl = None
    try:
        # controller_v2: (a) LIBRARY CHOSEN BY VALIDATION -- frequency vs MDL, whichever
        # has the better held-out strictly-better count (both already computed above);
        # (b) miss rate for the depth rule estimated on the VALIDATION stream, not on
        # training, because the library was mined FROM training and tiles it optimistically.
        _freq_better = sum(1 for r in report["held_out"]
                           if r["candidate"]["slots"] < r["baseline"]["slots"])
        _mdl_better = (sum(1 for r in mdl_report["held_out"]
                           if r["candidate"]["slots"] < r["baseline"]["slots"])
                       if isinstance(mdl_report, dict) and "held_out" in mdl_report else -1)
        # controller_v3: SELECT THE LIBRARY THE WAY IT IS DEPLOYED. validate_generator scores
        # each candidate by the INTERLEAVE; the controller deploys through the PROBE, whose
        # cost scales with (|lib| + P)^depth. On the authored world hc08 the interleave
        # validation picked the 16-fragment frequency library and the probe then lost to the
        # same-library parent (beta 8 420); the compact MDL library would have paid. Each
        # candidate is therefore costed by the expected PROBE cost on the held-out validation
        # tilings (the same rule that sets the depth), from the rows already recorded -- no
        # extra search. Both scores are reported; the interleave choice is kept as
        # `validated_better_interleave` for the record.
        def _probe_cost(_frags, _rep):
            _lib = [tuple(f) for f in _frags]; _T = len(_lib) + len(M.PRIMITIVES); _h = []
            for _r in _rep["held_out"]:
                _bp = _r["baseline"].get("program"); _bs = _r["baseline"]["slots"]
                _d = _tile_tokens(tuple(_bp), _lib) if _bp else None
                _h.append((_d if _d is not None else 99, _bs))
            _best = (float("inf"), 3)
            for _D in range(1, 5):
                _bD = sum(_T ** i for i in range(1, _D + 1))
                _c = statistics.fmean((sum(_T ** j for j in range(1, d_)) + _T ** d_ / 2) if d_ <= _D else _bD + b_ for d_, b_ in _h) if _h else float("inf")
                _best = min(_best, (_c, _D))
            return _best[0]
        _freq_frags = [list(f) for f in method.fragments]
        _pc_freq = _probe_cost(_freq_frags, report) if _freq_frags else float("inf")
        _pc_mdl = _probe_cost(mdl_frags, mdl_report) if (mdl_frags and isinstance(mdl_report, dict) and "held_out" in mdl_report) else float("inf")
        _use_mdl = bool(mdl_frags) and _pc_mdl <= _pc_freq
        _chosen_report = mdl_report if _use_mdl else report
        _chosen_frags = mdl_frags if _use_mdl else _freq_frags
        if _chosen_frags and isinstance(_chosen_report, dict) and "held_out" in _chosen_report:
            _lib = [tuple(f) for f in _chosen_frags]
            mdl_report = _chosen_report          # the rule below is fitted on the chosen library
            _T = len(_lib) + len(M.PRIMITIVES)
            # controller_v4: the rule is only ever consulted on a PROBE MISS, so it must be
            # fitted on the validation tasks the probe would miss (tiling deeper than the
            # chosen depth) -- fitting it on all tasks credits the interleave with the easy
            # hits it never gets to serve (hc08: 16 misses routed to an interleave at 1.4x
            # RESET because the unconditional rule said the interleave paid). The depth is
            # chosen first (below), then the rule is fitted on the miss-conditional rows.
            _rows_all = list(zip(mdl_report["held_out"], held))
            # expected-cost depth on solved history: hits cost their guided position,
            # misses cost beta_D plus the baseline index the organism actually paid (r_.slots)
            # depth rule on HELD-OUT validation: tiling of each validation task's canonical
            # (baseline) solution against the chosen library; a None tiling is a miss at
            # every depth and costs beta_D + its baseline index
            _hist = []
            for _r in mdl_report["held_out"]:
                _bp = _r["baseline"].get("program")
                _bs = _r["baseline"]["slots"]
                _d = _tile_tokens(tuple(_bp), _lib) if _bp else None
                _hist.append((_d if _d is not None else 99, _bs))
            _depth, _bc = 3, float("inf")
            for _D in range(1, 5):
                _bD = sum(_T ** i for i in range(1, _D + 1))
                _c = statistics.fmean((sum(_T ** j for j in range(1, d_)) + _T ** d_ / 2) if d_ <= _D else _bD + b_
                                      for d_, b_ in _hist) if _hist else float("inf")
                if _c < _bc:
                    _depth, _bc = _D, _c
            _rule, _cond = {}, []
            for _r, _h in _rows_all:
                _bp = _r["baseline"].get("program")
                _dt = _tile_tokens(tuple(_bp), _lib) if _bp else None
                if _dt is not None and _dt <= _depth:
                    continue                                  # the probe would hit: the rule is never asked
                _cond.append(_r["baseline"]["slots"] - _r["candidate"]["slots"])
                _rule.setdefault(str(_obs_feats(_h.coefficients, _lib)), []).append(_cond[-1])
            _rule = {z: (statistics.fmean(v) > 0) for z, v in _rule.items()}
            _fallback = (statistics.fmean(_cond) > 0) if _cond else False
            ocm_ctl = {"rule": _rule, "fallback": _fallback, "probe_depth": _depth,
                       "rule_fit": "controller_v4: miss-conditional (validation tasks tiling deeper than the probe depth); %d of %d rows" % (len(_cond), len(_rows_all)),
                       "beta": sum(_T ** i for i in range(1, _depth + 1)),
                       "liveness_window": 8, "liveness_min_hit_rate": 0.25,
                       "depth_rule": "expected-cost on held-out validation (controller_v2)",
                       "liveness": "v2: counter advances every target; stood-down => RESET until re-probe hits",
                       "library": "mdl" if _use_mdl else "frequency",
                       "library_rule": "controller_v3: expected probe cost on held-out validation tilings",
                       "expected_probe_cost": {"frequency": round(_pc_freq, 1) if _pc_freq != float("inf") else None,
                                               "mdl": round(_pc_mdl, 1) if _pc_mdl != float("inf") else None},
                       "validated_better_interleave": {"frequency": _freq_better, "mdl": _mdl_better}}
    except Exception as _e:
        ocm_ctl = {"error": str(_e)[:200]}

    state = {
        "schema": "M2P1_DEV_STATE", "eu_admission": eu,
        "ocm_controller": ocm_ctl,
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
    if arm in ("CONTINUED_OCM", "CONTINUAL_OCM"):
        # INTEGRATED DEVELOPMENTAL CONTROLLER: MDL selection -> probe with history-learned
        # depth -> task-statement rule on a miss -> liveness on the probe hit-rate.
        # Reads only the task statement, solved history and charged-action outcomes.
        ctl = dev.get("ocm_controller")
        if not ctl or "error" in ctl:
            return M.GeneratorMethod(), "no controller (%s)" % ((ctl or {}).get("error", "none"))
        mdl = dev.get("mdl_fragments") if ctl.get("library", "mdl") == "mdl" else dev.get("fragments")
        if not mdl:
            return M.GeneratorMethod(), "no library"
        return M.GeneratorMethod(tuple(tuple(f) for f in mdl), tuple(dev["training_task_ids"])), \
            ("integrated controller: probe depth %d beta %d, rule cells %d" % (
                ctl["probe_depth"], ctl["beta"], len(ctl["rule"]))
             + ("; CONTINUAL: re-mines from its own verified acquisitions while stood down "
                "(corpus %d, held-out %d, min new %d), retains every library"
                % (CONTINUAL["mine_n"], CONTINUAL["val_n"], CONTINUAL["min_new"]) if arm == "CONTINUAL_OCM" else ""))
    if arm == "PARENT_WITH_MDL":
        # FAIRNESS CONTROL. CONTINUED_MDL beating ORDINARY_ADAPTIVE_PARENT conflates two
        # things: the selection RULE (MDL vs frequency) and the OCM/parent distinction.
        # This arm gives the ungated parent the SAME MDL library, isolating the rule. If
        # it matches CONTINUED_MDL, the win belongs to compression, not to OCM.
        mdl = dev.get("mdl_fragments")
        if not mdl:
            return M.GeneratorMethod(), "no mdl library recorded"
        return M.GeneratorMethod(tuple(tuple(f) for f in mdl), tuple(dev["training_task_ids"])), \
            "ungated parent serving the MDL library: isolates selection rule from OCM"
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
            if arm == "CONTINUAL_OCM" and method.fragments:
                # CONTINUAL DEVELOPMENT: the v3 controller, plus re-mining from the organism's
                # own verified acquisitions while stood down. Reads only the task statement,
                # its own solved history and charged-action outcomes; every probe, every
                # validation probe and every interleave excess is charged to the target.
                P = phase_acquire
                if not hasattr(P, "_c"):
                    c0 = dev["ocm_controller"]
                    P._c = {"libs": [{"lib": [list(f) for f in method.fragments], "probe_depth": c0["probe_depth"],
                                      "beta": c0["beta"], "rule": c0["rule"], "fallback": c0["fallback"],
                                      "expected_baseline": dev.get("held_out_mean_baseline"),
                                      "library": "dev:" + c0.get("library", "mdl")}],
                            "active": None, "hits": [], "vals": [], "solved": [], "since_mine": 0, "events": [], "regime_start": 0}
                C = P._c
                prog, used = None, 0
                if C["active"] is not None:
                    L = C["libs"][C["active"]]
                    prog, used = _probe(M, task.coefficients, [tuple(f) for f in L["lib"]], L["probe_depth"], min(L["beta"], q))
                    C["hits"].append(prog is not None)
                    # v5: realised value of keeping this library live on this target
                    C["vals"].append((L.get("expected_baseline") or 0) - used if prog is not None else -used)
                    W = CONTINUAL["value_window"]; k = CONTINUAL["standdown_misses"]
                    # v5.1: EITHER signal stands the library down -- k consecutive misses (fast at a
                    # regime change, where the value window still carries the old regime's hits)
                    # or a negative realised value over the window (an expensive library whose
                    # sporadic hits never pay for its misses, s604).
                    if (len(C["hits"]) >= k and not any(C["hits"][-k:])) or \
                       (len(C["vals"]) >= k and sum(C["vals"][-W:]) < 0):
                        # v3: stand down after k consecutive misses (v2's 8-window hit-rate rule
                        # paid ~7 targets of probe + interleave at every regime change), and
                        # try the OTHER retained libraries at once -- a return to a known
                        # regime should cost one probe each, not a cadence wait.
                        prev = C["active"]; C["active"] = None
                        C["regime_start"] = len(C["solved"]); C["since_mine"] = 0
                        for kk, L2 in enumerate(C["libs"]):
                            if kk == prev:
                                continue
                            pr, u = _probe(M, task.coefficients, [tuple(f) for f in L2["lib"]], L2["probe_depth"], min(L2["beta"], q))
                            used += u
                            if pr is not None:
                                prog, C["active"] = pr, kk
                                C["hits"] = [True]; C["vals"] = []
                                break
                else:
                    C["hits"].append(False)
                    if (len(C["hits"]) - 1) % 8 == 0:           # re-probe every retained library
                        for k, L in enumerate(C["libs"]):
                            pr, u = _probe(M, task.coefficients, [tuple(f) for f in L["lib"]], L["probe_depth"], min(L["beta"], q))
                            used += u
                            if pr is not None:
                                prog, C["active"] = pr, k
                                C["hits"] = [True]; C["vals"] = []   # v2: a fresh window for the reactivated library
                                break
                        if prog is None and C["since_mine"] >= CONTINUAL["min_new"]:
                            rec, charged, ev = _remine(M, C["solved"][C.get("regime_start", 0):])
                            used += charged
                            if "skipped" not in ev:
                                # v4.1: a SKIPPED attempt (corpus too small) mined nothing and must not
                                # consume the counter; v4.2: a FAILED attempt retries after min_new_after_fail
                                C["since_mine"] = 0 if rec is not None else CONTINUAL["min_new"] - CONTINUAL["min_new_after_fail"]
                            ev["target_index"] = i; C["events"].append(ev)
                            if rec is not None:
                                C["libs"].append(rec); C["active"] = len(C["libs"]) - 1
                                pr, u = _probe(M, task.coefficients, [tuple(f) for f in rec["lib"]], rec["probe_depth"], min(rec["beta"], q))
                                used += u
                                C["hits"] = [pr is not None]; C["vals"] = []   # v2: a fresh window for the new library
                                if pr is not None:
                                    prog = pr
                if prog is not None:
                    res = M.SearchResult(task.fingerprint, method.fingerprint, "VERIFIED_POLYNOMIAL_IDENTITY",
                                         prog, used, used, (0,), 8)
                else:
                    L = C["libs"][C["active"]] if C["active"] is not None else None
                    # v3: only the dev-fitted rule (fitted on interleave-vs-baseline deltas) may
                    # route to the interleave; a learned library's rule was fitted on probe
                    # deltas, which say where the probe hits, not where the interleave pays.
                    use_inter = bool(L) and str(L.get("library", "")).startswith("dev:") and \
                        L["rule"].get(str(_obs_feats(task.coefficients, [tuple(f) for f in L["lib"]])), L["fallback"])
                    rest = M.SearchBudget(slots=max(1, q - used), max_length=8)
                    meth = M.GeneratorMethod(tuple(tuple(f) for f in L["lib"]), method.training_tasks) if use_inter else None
                    r2 = M.solve(task, rest, meth) if meth else M.solve(task, rest)
                    res = M.SearchResult(task.fingerprint, method.fingerprint, r2.status, r2.program,
                                         used + r2.slots, r2.candidates_checked, r2.counterexamples, 8)
                if M.verify_solution(task, res):
                    C["solved"].append((task, res, res.slots)); C["since_mine"] += 1
            elif arm == "CONTINUED_OCM" and method.fragments:
                ctl = dev["ocm_controller"]; lib = list(method.fragments)
                if not hasattr(phase_acquire, "_live"):
                    # liveness_v3: COLD START STOOD DOWN. Liveness is earned by a probe hit,
                    # never assumed -- v2 booted live, so its first window consulted the
                    # task-statement rule before any probe evidence existed; on a world the
                    # library never fits (FV8) those rule-routed interleaves were the whole
                    # -0.56 % overhead. The first target probes immediately (below), so a
                    # working library loses nothing.
                    phase_acquire._live, phase_acquire._hits = False, []
                if phase_acquire._live:
                    prog, used = _probe(M, task.coefficients, lib, ctl["probe_depth"], min(ctl["beta"], q))
                    phase_acquire._hits.append(prog is not None)
                    if len(phase_acquire._hits) >= ctl["liveness_window"]:
                        recent = phase_acquire._hits[-ctl["liveness_window"]:]
                        if sum(recent) / len(recent) < ctl["liveness_min_hit_rate"]:
                            phase_acquire._live = False          # stand the probe down
                else:
                    # stood down: the counter must ADVANCE every target (liveness_v2 -- the
                    # first port only appended on a re-probe, so reactivation could fire
                    # once and never again), and a periodic re-probe restores the library.
                    prog, used = (None, 0)
                    phase_acquire._hits.append(False)
                    # probe on the FIRST target and every liveness_window thereafter
                    if (len(phase_acquire._hits) - 1) % ctl["liveness_window"] == 0:
                        prog, used = _probe(M, task.coefficients, lib, ctl["probe_depth"], min(ctl["beta"], q))
                        phase_acquire._hits[-1] = prog is not None
                        if prog is not None:
                            phase_acquire._live = True           # reactivate
                if prog is not None:
                    res = M.SearchResult(task.fingerprint, method.fingerprint, "VERIFIED_POLYNOMIAL_IDENTITY",
                                         prog, used, used, (0,), 8)
                else:
                    # liveness_v2: while stood down the LIBRARY is presumed stale, so the
                    # rule (fitted on the old ecology) may not route to the interleave
                    use_inter = (phase_acquire._live and
                                 ctl["rule"].get(str(_obs_feats(task.coefficients, lib)), ctl["fallback"]))
                    rest = M.SearchBudget(slots=max(1, q - used), max_length=8)
                    r2 = M.solve(task, rest, method) if use_inter else M.solve(task, rest)
                    res = M.SearchResult(task.fingerprint, method.fingerprint, r2.status, r2.program,
                                         used + r2.slots, r2.candidates_checked, r2.counterexamples, 8)
            else:
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
    if arm == "CONTINUAL_OCM" and hasattr(phase_acquire, "_c"):
        C = phase_acquire._c
        rep["continual"] = {"libraries_retained": len(C["libs"]),
                            "libraries": [{k: v for k, v in L.items() if k != "rule"} for L in C["libs"]],
                            "remine_events": C["events"], "params": CONTINUAL}
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
