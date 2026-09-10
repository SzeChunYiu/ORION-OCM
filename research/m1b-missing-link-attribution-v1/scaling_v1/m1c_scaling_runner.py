"""M1C amortisation-scaling lifecycle runner (machinery only; no scored run).

Executes the frozen protocol M1C_SCALING_FREEZE_V1.json (PR #360, merge c5e93805).
Every constant this runner obeys (ladder rungs, serving budget, frozen dev cost and
fingerprint) is READ FROM THE FREEZE FILE at import -- the machinery is bound to
its own freeze, never to hand-copied numbers.

Reuses the M1B machinery verbatim by import (m1b_runner binds m1_runner and the
registered learner src/ocm/learning/methods.py AS-IS): frozen-worlds verification,
phase_dev / phase_checkpoint (dev mining + STRONG_ADAPTIVE_PARENT fit), arm_solve
for the four registered arms, checker-C external verification, sealed logs, and
per-arm fresh-OS-process restart evidence.

Serve model (freeze): one serve = one acquisition of one target-list entry at the
registered serving budget; the target list is the frozen protected stream cyclically
repeated; T-rungs are PREFIXES of that one list.  The analysis phase computes the
crossing curve net(T) = sum_{i<=T}(B_RESET,i - B_GATE,i) - DEV, the Holm rung family
(target-clustered sign-flip + equal-n label-shuffle nulls at every rung), the
DEV-CAL-4 secondary (N_FROZEN read from the cited frozen semantics file), the
tertiary work readouts, the M1C invariants, and the frozen terminal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE.parent))            # the M1B lane (m1b_runner, m1b_stats)
sys.path.insert(0, str(HERE.parent.parent / "m1-native-acquisition"))

import m1_runner as R1                            # noqa: E402  proven M1 scaffold
import m1b_runner as B1                           # noqa: E402  M1B machinery, reused
from ocm.learning import methods as M             # noqa: E402  registered learner, AS-IS

# ----------------------------------------------------------------- freeze binding
FREEZE_PATH = HERE / "M1C_SCALING_FREEZE_V1.json"
FREEZE = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
FREEZE_SHA256 = hashlib.sha256(FREEZE_PATH.read_bytes()).hexdigest()
RUNGS = tuple(FREEZE["design"]["ladder"]["rungs"])
SERVE_BUDGET = int(str(FREEZE["design"]["serving_unit"]).split("budget ")[1].split(" ")[0])
DEV_COST_FROZEN = int(FREEZE["design"]["dev_charge_ledger_entry"].split("number ")[1].split(" ")[0].replace(",", ""))
DEV_FINGERPRINT = B1.FROZEN_M1_DEV_FINGERPRINT
GATE_ARM = "STRONG_ADAPTIVE_PARENT"
SCALING_ARMS = tuple(FREEZE["arms"]["set"])
OBLIGATION_SLICE = (8, 40)   # freeze: protected rows 8..39 served once, never in the ladder
DEVCAL4_PATH = REPO / "research/hsg-semantic-execution-v1/exact/DEV_CAL_4_ACQUISITION_CHARGING_FREEZE_V1.json"
DEVCAL4 = json.loads(DEVCAL4_PATH.read_text(encoding="utf-8"))
DEVCAL4_SHA256 = hashlib.sha256(DEVCAL4_PATH.read_bytes()).hexdigest()
N_FROZEN = int(DEVCAL4["N_derivation_rule"]["n_frozen"])
MARGIN = 0.20
FROZEN_SEED = 20260910

# SELFTEST ONLY relaxation switch, identical in spirit to M1B's: with toy worlds the
# frozen-hash and frozen-cost gates RECORD instead of ENFORCE, and every artifact is
# stamped toy_selftest_only_NOT_SCORED_EVIDENCE.  The scored run never passes the flag.
WORLDS_MODE = {"toy": False}


class AssayDefect(Exception):
    """The M1C assay itself is broken (drift, fake restart, binding mismatch)."""

assert DEV_COST_FROZEN == 14427131, "freeze dev-cost binding drifted"
assert SERVE_BUDGET == 200000, "freeze serving-budget binding drifted"
assert RUNGS == (8, 32, 128, 512), "freeze ladder binding drifted"
assert SCALING_ARMS == ("RESET", "STRONG_ADAPTIVE_PARENT", "APPL_ORACLE",
                        "KNOWN_STRUCTURE_ORACLE"), "freeze arm-set binding drifted"


def run_files(run_dir: Path):
    return {**B1.run_files(run_dir), "serves": run_dir / "serves",
            "m1c_dir": HERE}


def serve_list(partitions: dict, t_max: int) -> list:
    """The frozen target list: the protected stream in stream order, cyclically
    repeated to t_max (freeze design.target_list).  Deterministic pure function."""
    rows = partitions["streams"]["protected"]
    if not rows:
        raise AssayDefect("EMPTY_PROTECTED_STREAM")
    return [rows[i % len(rows)] for i in range(t_max)]


def verify_frozen_worlds(run_dir: Path) -> dict:
    """M1B verification reused verbatim (byte-identical partitions + protected set);
    toy worlds are RECORDED, never enforced, and stamped as such."""
    return B1.verify_frozen_worlds(run_dir)


# --------------------------------------------------------------------- phases

def phase_dev_scaling(run_dir: Path, slots: int) -> None:
    """M1B dev phase reused verbatim (fingerprint gate included) PLUS the M1C dev
    COST gate: the re-executed dev enumeration must equal the frozen 14,427,131.
    A mismatch on either identity is RECEIPT_BINDING_DEFECT: worlds or learner
    drifted, the run halts before any serve."""
    B1.phase_dev(run_dir, slots, DEV_FINGERPRINT)
    ledger = R1.load_json(run_files(run_dir)["ledger"])
    dev_cost = ledger.get("candidate_enumerations_dev", 0)
    if not WORLDS_MODE["toy"] and dev_cost != DEV_COST_FROZEN:
        raise SystemExit(f"RECEIPT_BINDING_DEFECT: re-executed dev cost {dev_cost} != "
                         f"frozen {DEV_COST_FROZEN}; worlds or learner drifted")
    R1.events_append(run_dir, "dev", "M1C_DEV_COST_GATE",
                     {"candidate_enumerations_dev": dev_cost,
                      "frozen": DEV_COST_FROZEN,
                      "enforced": not WORLDS_MODE["toy"]})


def phase_checkpoint_scaling(run_dir: Path) -> dict:
    """M1B checkpoint reused verbatim (STRONG_ADAPTIVE_PARENT fit from DEV data
    only, persisted to its own store, sealed).  The fit is byte-identical to M1B's
    because the dev state and features are byte-identical."""
    return B1.phase_checkpoint(run_dir)


def phase_serve(run_dir: Path, arm: str, t_max: int, serve_budget: int) -> dict:
    """Serve the frozen cyclic target list for ONE arm in a FRESH OS process:
    t_max serves at the registered budget, plus the frozen obligation slice
    (protected rows 8..39) served once -- never part of the T-ladder.  Every serve
    goes through the M1B arm_solve dispatch (registered M.solve path for RESET /
    STRONG_ADAPTIVE_PARENT; declared-info channels for the two calibration riders)
    with checker-C external verification, M1B row shape, and the M1B HDI-14 ledger
    (the frozen dev cost enters ONCE as the fixed entry for every arm that uses
    dev history; RESET carries zero)."""
    started = time.perf_counter()
    verify_frozen_worlds(run_dir)
    paths = run_files(run_dir)
    checkpoint = R1.load_json(paths["checkpoint"])
    if checkpoint["pre_restart_pid"] == os.getpid():
        raise AssayDefect("SAME_PROCESS_FAKE_RESTART: serve must run in a fresh OS process")
    partitions = R1.load_json(paths["partitions"])
    dev_state = R1.load_json(paths["dev_state"])
    strong_store = R1.load_json(paths["strong_parent"])
    targets = serve_list(partitions, t_max)
    library = tuple(tuple(f) for f in (dev_state.get("candidates") or {}).get("fragments", []))
    ctx = {"library": library, "strong_store": strong_store,
           "method": None, "refusal_reason": None}
    if arm == "RESET":
        R1.clone_ocm_root(run_dir, arm)   # pristine ocm root, M1B arm behaviour verbatim
    budget = R1.budget_of(partitions, serve_budget)
    rows, obligations = [], []
    verification_calls = external_spawns = adaptation_events = 0
    p_star_cache: dict[str, tuple | None] = {}

    def p_star_for(row):
        key = row["normal_form_digest"]
        if key not in p_star_cache:
            p_star_cache[key] = B1.minimal_solution(row)
        return p_star_cache[key]

    oracle_arms = ("STRONG_ADAPTIVE_PARENT", "APPL_ORACLE")  # p_star used: observation / declared set
    for serve_index, row in enumerate(targets):
        task = M.PolynomialTask(row["task_id"], row["coefficients"])
        ctx["p_star"] = p_star_for(row) if arm in oracle_arms else None
        if arm in oracle_arms:
            adaptation_events += 1
        result, instr, note = B1.arm_solve(arm, task, budget, row, ctx)
        verification_calls += 1
        verdict = None
        if result.program is not None:
            verdict = R1.checker_C(row["coefficients"], result.program)
            external_spawns += 1
            verification_calls += 1
        instr = dict(instr)
        if not instr.get("retrieval_cost_slots") and instr.get("retrieval_events"):
            instr["retrieval_cost_slots"] = instr["retrieval_events"]
        rows.append({"arm": arm, "serve_index": serve_index,
                     "target": row["normal_form_digest"],
                     "semantic_class": row["semantic_class"],
                     "min_primitive_length": row["min_primitive_length"],
                     "budget_slots": serve_budget, "B_slots": result.slots,
                     "B_candidates_checked": result.candidates_checked,
                     "status": result.status,
                     "checker_verdict": verdict["verdict"] if verdict else None,
                     "verified_external": bool(verdict and verdict["verdict"] == "IDENTICAL"),
                     "note": note, "search_behavior": instr})
    prot_rows = partitions["streams"]["protected"]
    for row in prot_rows[OBLIGATION_SLICE[0]:OBLIGATION_SLICE[1]]:
        task = M.PolynomialTask(row["task_id"], row["coefficients"])
        ctx["p_star"] = p_star_for(row) if arm in oracle_arms else None
        result, instr, _note = B1.arm_solve(arm, task, budget, row, ctx)
        verification_calls += 1
        verdict = R1.checker_C(row["coefficients"], result.program) if result.program is not None else None
        external_spawns += 1 if verdict else 0
        obligations.append({"arm": arm, "target": row["normal_form_digest"],
                            "B_slots": result.slots, "status": result.status,
                            "verified_external": bool(verdict and verdict["verdict"] == "IDENTICAL")})
    uses_dev_history = arm != "RESET"

    def total(field):
        return sum((r["search_behavior"] or {}).get(field, 0) for r in rows)

    run_ledger = R1.load_json(paths["ledger"])
    dev_entry = (run_ledger.get("candidate_enumerations_dev") or 0) if uses_dev_history else 0
    hdi14 = {
        "acquisition_slots": sum(r["B_slots"] for r in rows),
        "dev_enumeration_slots": dev_entry,
        "obligation_slots": sum(r["B_slots"] for r in obligations),
        "retrieval_events": total("retrieval_events") + total("retrieval_signal_events"),
        "retrieval_cost_slots": total("retrieval_cost_slots"),
        "max_penalty_tax_slots": total("max_penalty_tax_slots"),
        "rejected_candidates": total("candidates_rejected"),
        "verification_calls": verification_calls,
        "external_checker_spawns": external_spawns,
        "storage_bytes": B1._arm_state_bytes(arm, run_dir, dev_state),
        "adapter_storage_bytes": B1._arm_adapter_bytes(arm),
        "adaptation_events": adaptation_events + total("retrieval_signal_events"),
        "interpreter_restarts": 1,
        "wall_seconds": round(time.perf_counter() - started, 6),
    }
    missing = [f for f in B1.HDI14_FAMILIES if f not in hdi14]
    if missing:
        raise AssayDefect(f"HDI14_INCOMPLETE: {missing}")
    report = {"schema": "OCM_M1C_ARM_SERVE_REPORT", "arm": arm,
              "calibration_only": arm in B1.CALIBRATION_ONLY_ARMS,
              "declared_info_advantage": B1.DECLARED_INFO_ADVANTAGES.get(arm),
              "process": {"pid": os.getpid(),
                          "pre_restart_pid": checkpoint["pre_restart_pid"],
                          "pid_changed": os.getpid() != checkpoint["pre_restart_pid"],
                          "boot_token_inherited": checkpoint["boot_token"]},
              "serve_model": {"t_max": t_max, "serve_budget": serve_budget,
                              "distinct_targets": len({r["target"] for r in rows}),
                              "protected_stream_len": len(prot_rows)},
              "dev_charge_entry": dev_entry,
              "serve_rows": rows, "obligation_rows": obligations,
              "cost_ledger_hdi14": hdi14}
    R1.write_json(paths["arms"] / f"{arm}.json", report)
    R1.events_append(run_dir, f"serve_{arm}", "ARM_SERVE_REPORT",
                     {"arm": arm, "serves": len(rows), "obligations": len(obligations),
                      "dev_charge_entry": dev_entry})
    R1.seal_phase(run_dir, f"serve_{arm}")
    R1.ledger_update(run_dir, phase=f"serve_{arm}", phase_wall_seconds=hdi14["wall_seconds"],
                     interpreter_restarts=1,
                     candidate_enumerations=sum(r["B_candidates_checked"] for r in rows + obligations),
                     verification_calls=verification_calls)
    return report


def phase_restart_and_serve(run_dir: Path, arm: str, t_max: int, serve_budget: int,
                            timeout: int = 14400) -> dict:
    """REAL OS-PROCESS RESTART per arm (M1/M1B pattern verbatim): a fresh
    interpreter loads persisted state and serves; the child's own report carries
    its pid; the receipt cross-checks pids and fails closed."""
    child_args = [sys.executable, str(Path(__file__).resolve()), "--run-dir", str(run_dir),
                  "--phase", "serve", "--arm", arm, "--t-max", str(t_max),
                  "--serve-budget", str(serve_budget)]
    if WORLDS_MODE["toy"]:
        child_args.append("--selftest-toy-worlds")
    child = subprocess.run(child_args, capture_output=True, text=True, timeout=timeout)
    receipt = {"arm": arm, "parent_pid": os.getpid(), "child_pid": None,
               "child_returncode": child.returncode, "child_stderr_tail": child.stderr[-400:]}
    report_path = run_files(run_dir)["arms"] / f"{arm}.json"
    if child.returncode != 0 or not report_path.exists():
        R1.write_json(report_path,
                      {"schema": "OCM_M1C_ARM_SERVE_REPORT", "arm": arm,
                       "censored_whole_arm": True, "restart_receipt": receipt,
                       "serve_rows": [], "obligation_rows": [],
                       "cost_ledger_hdi14": {}, "censor_reason": f"child exited {child.returncode}"})
        R1.events_append(run_dir, f"serve_{arm}", "ARM_CENSORED",
                         {"arm": arm, "returncode": child.returncode})
        R1.seal_phase(run_dir, f"serve_{arm}")
        raise SystemExit(f"ARM_CENSORED: {arm} child exit {child.returncode}: {child.stderr[-300:]}")
    report = R1.load_json(report_path)
    report["restart_receipt"] = {**receipt, "child_pid": report["process"]["pid"]}
    R1.write_json(report_path, report)
    if report["process"]["pid"] == os.getpid():
        raise AssayDefect("RESTART_EVIDENCE_FAILED: child pid equals parent pid")
    if report["process"]["pid"] == report["process"]["pre_restart_pid"]:
        raise AssayDefect("RESTART_EVIDENCE_FAILED: child pid equals checkpoint pre-restart pid")
    return report


# ------------------------------------------------------------------- analysis

import random  # noqa: E402  (analysis-phase statistics; frozen seed only)

import m1b_stats as S1  # noqa: E402  frozen M1B statistics, reused


def _cluster_arrays(reports: dict) -> dict:
    """Per-arm serve arrays + the target-cluster structure (freeze null discipline:
    every statistical construct operates at equal n over the DISTINCT protected
    targets -- serves of one target are perfectly correlated, so they are one
    cluster, never independent samples)."""
    t_max = max(len(r.get("serve_rows", [])) for r in reports.values())
    arrays = {}
    for arm, report in reports.items():
        rows = sorted(report.get("serve_rows", []), key=lambda r: r["serve_index"])
        arrays[arm] = [r["B_slots"] for r in rows]
    clusters = []           # cluster j = list of serve indices serving target j
    seen: dict[str, int] = {}
    for arm in (GATE_ARM,):
        for row in sorted(reports[arm].get("serve_rows", []),
                          key=lambda r: r["serve_index"]):
            dig = row["target"]
            if dig not in seen:
                seen[dig] = len(clusters)
                clusters.append({"digest": dig, "serve_indices": []})
            clusters[seen[dig]]["serve_indices"].append(row["serve_index"])
    return {"t_max": t_max, "arrays": arrays, "clusters": clusters}


def _cumulative_net(arrays: dict, t_max: int, dev: int, gate=GATE_ARM,
                    charge_profile=None) -> list:
    """net(T) for T = 1..t_max: sum of per-serve RESET-minus-gate diffs minus the
    charged dev cost.  charge_profile=None -> the PRIMARY full-charge-once reading
    (DEV subtracted at every T); 'devcal4' -> the DEV-CAL-4 frozen semantics
    (min(T, N_FROZEN) * DEV / N_FROZEN charged)."""
    net = []
    running = 0
    for i in range(t_max):
        running += arrays["RESET"][i] - arrays[gate][i]
        if charge_profile is None:
            charge = float(dev)
        elif charge_profile == "devcal4":
            charge = min(i + 1, N_FROZEN) * dev / N_FROZEN
        else:
            raise ValueError(f"unknown charge profile {charge_profile}")
        net.append(running - charge)
    return net


def _cluster_diffs(clusters: list, arrays: dict, gate=GATE_ARM) -> list:
    """One value per DISTINCT target: the per-serve RESET-minus-gate diff (identical
    across that target's serves by the determinism control)."""
    out = []
    for cluster in clusters:
        i = cluster["serve_indices"][0]
        out.append(arrays["RESET"][i] - arrays[gate][i])
    return out


def _cluster_signflip_p(values: list, shift: float, seed=FROZEN_SEED) -> float:
    """Paired sign-flip null on target-clustered net contributions d_j = diff_j -
    shift, PERM_N from the frozen M1B statistics."""
    d = [v - shift for v in values]
    return S1.signflip_p(d, seed=seed)


def _equal_n_label_shuffle_p(clusters: list, arrays: dict, t: int, gate=GATE_ARM,
                             seed=FROZEN_SEED, perm_n=S1.PERM_N):
    """Equal-n label-shuffle null (freeze null_discipline (2)): the two arms'
    per-DISTINCT-target serve burdens over the rung-t prefix are pooled and arm
    labels shuffled at equal n; the null distribution of the mean difference under
    label exchangeability (deterministic re-serves collapse to the target's value)."""
    r_vals, a_vals = [], []
    for cluster in clusters:
        idx = next((i for i in cluster["serve_indices"] if i < t), None)
        if idx is None:
            continue
        r_vals.append(arrays["RESET"][idx])
        a_vals.append(arrays[gate][idx])
    if not r_vals:
        return None
    obs = sum(r - a for r, a in zip(r_vals, a_vals)) / len(r_vals)
    pooled = r_vals + a_vals
    rng = random.Random(seed)
    n = len(r_vals)
    ge = 0
    for _ in range(perm_n):
        rng.shuffle(pooled)
        null = sum(pooled[:n]) / n - sum(pooled[n:]) / n
        if abs(null) >= abs(obs) - 1e-12:
            ge += 1
    return ge / perm_n


def _bootstrap_net_curve(clusters: list, arrays: dict, rungs: tuple, dev: int,
                         charge_profile=None, boot_n=S1.BOOT_N, seed=FROZEN_SEED):
    """Percentile bootstrap over the DISTINCT targets (equal n): resample target
    clusters with replacement, recompute the mean per-serve diff, and report CI of
    net(T_r) = T_r * mean_boot - charge(T_r) per rung, plus the T* distribution
    (first T with net > 0; None per resample if the resampled mean never pays the
    charge within t_max)."""
    diffs = _cluster_diffs(clusters, arrays)
    n = len(diffs)
    rng = random.Random(seed)
    t_max = rungs[-1]
    means = []
    for _ in range(boot_n):
        means.append(sum(diffs[rng.randrange(n)] for _ in range(n)) / n)
    out = {}
    for t in rungs:
        if charge_profile is None:
            charge = float(dev)
        else:
            charge = min(t, N_FROZEN) * dev / N_FROZEN
        nets = sorted(t * m - charge for m in means)
        out[t] = [nets[max(0, int(0.025 * len(nets)) - 1)],
                  nets[min(len(nets) - 1, int(0.975 * len(nets)))]]
    t_stars = []
    for m in means:
        if charge_profile is None:
            t_stars.append(dev / m if m > 0 else None)
        else:
            # DEV-CAL-4: crossing = first T with T*m > min(T,30)*dev/30; for T>=30
            # this is T* = dev/m when m > 0; for T<30 charge is partial so also
            # check the early region exactly.
            star = None
            running_charge = 0.0
            cum = 0.0
            for i in range(t_max):
                cum += m
                running_charge = min(i + 1, N_FROZEN) * dev / N_FROZEN
                if cum - running_charge > 0:
                    star = i + 1
                    break
            t_stars.append(star)
    present = sorted(t for t in t_stars if t is not None)
    ci = ([present[max(0, int(0.025 * len(present)) - 1)],
           present[min(len(present) - 1, int(0.975 * len(present)))]] if present else None)
    return {"rung_cis": out, "t_star_ci": ci,
            "crossing_rate": len(present) / len(t_stars) if t_stars else None}


def phase_analyze(run_dir: Path, rungs: tuple = None) -> dict:
    """Deterministic M1C analysis: fail-closed guards (seals, worlds, leakage,
    serve determinism, cyclic binding, restart evidence), the PRIMARY crossing
    curve with the Holm rung family, the DEV-CAL-4 SECONDARY, the tertiary work
    readouts, the M1C invariants, and the frozen terminal.  Nothing random beyond
    the frozen-seed constructs."""
    started = time.perf_counter()
    rungs = tuple(rungs or RUNGS)
    paths = run_files(run_dir)
    seals = R1.verify_seals(run_dir)
    worlds = verify_frozen_worlds(run_dir)
    partitions = R1.load_json(paths["partitions"])
    dev_state = R1.load_json(paths["dev_state"])
    reports = {}
    for arm_file in sorted(paths["arms"].glob("*.json")):
        report = json.loads(arm_file.read_text(encoding="utf-8"))
        reports[report["arm"]] = report
    missing_arms = sorted(set(SCALING_ARMS) - set(reports))
    censored_arms = [a for a, r in reports.items() if r.get("censored_whole_arm")]
    struct = _cluster_arrays(reports)
    arrays, clusters = struct["arrays"], struct["clusters"]
    t_max = struct["t_max"]

    # ---- fail-closed guards
    history_digests = {row["normal_form_digest"] for stream in ("train", "validation", "test")
                       for row in partitions["streams"][stream]}
    history_digests |= {t["task"] for t in dev_state.get("traces", [])}
    serve_digests = {c["digest"] for c in clusters}
    leakage = sorted(history_digests & serve_digests)
    prot_rows = partitions["streams"]["protected"]
    expected_list = serve_list(partitions, t_max)
    cyclic_ok = ([r["target"] for r in sorted(reports[GATE_ARM]["serve_rows"],
                                              key=lambda r: r["serve_index"])]
                 == [r["normal_form_digest"] for r in expected_list])
    determinism_violations = []
    for arm, report in reports.items():
        per_target: dict[str, set] = {}
        for row in report.get("serve_rows", []):
            per_target.setdefault(row["target"], set()).add(row["B_slots"])
        determinism_violations += [f"{arm}:{d}" for d, vals in per_target.items()
                                   if len(vals) > 1]
    restart_ok = all(r.get("restart_receipt", {}).get("child_pid") not in (None, os.getpid())
                     for r in reports.values())
    dev_entries = {a: r.get("cost_ledger_hdi14", {}).get("dev_enumeration_slots")
                   for a, r in reports.items()}
    receipt_binding_defects = []
    ledger_dev = R1.load_json(paths["ledger"]).get("candidate_enumerations_dev")
    # EVERY mode: each arm's dev entry must be self-consistent (0 for RESET, exactly
    # the run ledger's own dev cost for every dev-using arm).  Real mode adds the
    # frozen identity (that ledger value IS the frozen 14,427,131).
    for arm in reports:
        expected = 0 if arm == "RESET" else ledger_dev
        if dev_entries.get(arm) != expected:
            receipt_binding_defects.append(
                f"{arm}: dev entry {dev_entries.get(arm)} != {expected}")
    if not WORLDS_MODE["toy"] and ledger_dev != DEV_COST_FROZEN:
        receipt_binding_defects.append(
            f"run ledger dev cost {ledger_dev} != frozen {DEV_COST_FROZEN}")
    assay_defects = []
    if leakage:
        assay_defects.append(f"LEAKAGE:{leakage[:5]}")
    if not cyclic_ok:
        assay_defects.append("CYCLIC_TARGET_BINDING")
    if determinism_violations:
        assay_defects.append(f"SERVE_DETERMINISM:{determinism_violations[:5]}")
    if not restart_ok:
        assay_defects.append("RESTART_EVIDENCE")
    if censored_arms:
        assay_defects.append(f"CENSORED_ARMS:{censored_arms}")
    if missing_arms:
        assay_defects.append(f"MISSING_ARMS:{missing_arms}")
    hdi14_missing = {a: [f for f in B1.HDI14_FAMILIES
                         if f not in r.get("cost_ledger_hdi14", {})]
                     for a, r in reports.items()}
    if any(hdi14_missing.values()):
        assay_defects.append(f"HDI14_INCOMPLETE:{hdi14_missing}")
    dev = dev_entries.get(GATE_ARM) or DEV_COST_FROZEN

    # ---- PRIMARY: crossing curve + Holm rung family (freeze readouts.primary)
    net_curve = _cumulative_net(arrays, t_max, dev, charge_profile=None)
    boot = _bootstrap_net_curve(clusters, arrays, rungs, dev, charge_profile=None)
    t_star_cont = next((i + 1 for i, v in enumerate(net_curve) if v > 0), None)
    rung_table = []
    pvals = {}
    for t in rungs:
        # sign-flip on the FULL serve prefix (paired per serve; exact re-serves collapse)
        serve_diffs = [arrays["RESET"][i] - arrays[GATE_ARM][i] - dev / t
                       for i in range(t)]
        p_sf = S1.signflip_p(serve_diffs, seed=FROZEN_SEED)
        p_sh = _equal_n_label_shuffle_p(clusters, arrays, t)
        pvals[f"T{t}"] = max(p_sf, p_sh)
        net_t = net_curve[t - 1]
        rung_table.append({"T": t, "net": net_t, "boot_ci": boot["rung_cis"][t],
                           "p_signflip": p_sf, "p_label_shuffle": p_sh,
                           "mean_B_reset": sum(arrays["RESET"][:t]) / t,
                           "mean_B_gate": sum(arrays[GATE_ARM][:t]) / t,
                           "verified_reset": sum(1 for r in reports["RESET"]["serve_rows"][:t]
                                                 if r["verified_external"]),
                           "verified_gate": sum(1 for r in reports[GATE_ARM]["serve_rows"][:t]
                                                if r["verified_external"])})
    holm = S1.holm(pvals)
    for row in rung_table:
        h = holm[f"T{row['T']}"]
        row["p_max"] = max(row["p_signflip"] or 0.0, row["p_label_shuffle"] or 0.0)
        row["holm_p"] = h["p_holm"]
        row["rejected"] = bool(h["reject"])
    crossing_rung = next((row["T"] for row in rung_table
                          if row["net"] > 0 and all(r["rejected"] and r["net"] > 0
                                                    for r in rung_table if r["T"] >= row["T"])), None)

    # ---- SECONDARY: DEV-CAL-4 frozen corrected charging (labelled, never primary)
    net_devcal4 = _cumulative_net(arrays, t_max, dev, charge_profile="devcal4")
    boot_d4 = _bootstrap_net_curve(clusters, arrays, rungs, dev, charge_profile="devcal4")
    t_star_d4 = next((i + 1 for i, v in enumerate(net_devcal4) if v > 0), None)
    secondary = {"label": "SECONDARY", "semantics": "MARGINAL_COST_ONLY_AT_FROZEN_N",
                 "n_frozen": N_FROZEN, "cited_file": str(DEVCAL4_PATH.relative_to(REPO)),
                 "cited_sha256": DEVCAL4_SHA256,
                 "net_at_rungs": {str(t): net_devcal4[t - 1] for t in rungs},
                 "t_star_continuous": t_star_d4, "t_star_boot_ci": boot_d4["t_star_ci"],
                 "agrees_with_primary_at_T_ge_30": (t_star_d4 is not None and t_star_cont is not None
                                                    and abs(t_star_d4 - t_star_cont) <= 0) or None}

    # ---- TERTIARY: work readouts per rung (never the primary); recovery_i is the
    # REGISTERED M1B statistic (m1b_stats.recovery_share at matched keys), uncharged.
    tertiary = {"label": "TERTIARY_WORK", "recovery_i_at_rungs": {}, "rule_distribution": {}}
    recovery_vs_ks = {}
    for t in rungs:
        keyed = {}
        for arm in SCALING_ARMS:
            if arm not in arrays:
                continue
            keyed[arm] = {c["digest"]: arrays[arm][next(i for i in c["serve_indices"] if i < t)]
                          for c in clusters if any(i < t for i in c["serve_indices"])}
        rec = {}
        for arm in ("STRONG_ADAPTIVE_PARENT", "APPL_ORACLE"):
            rec[arm] = S1.recovery_share(keyed, arm)   # dev_slots=0: UNCHARGED work readout
        tertiary["recovery_i_at_rungs"][str(t)] = rec
        if t == rungs[-1]:
            recovery_vs_ks = {arm: S1.recovery_share(keyed, arm)
                              for arm in ("STRONG_ADAPTIVE_PARENT", "APPL_ORACLE")}
    for row in reports[GATE_ARM]["serve_rows"]:
        rule = (row.get("note") or "?")
        tertiary["rule_distribution"][rule] = tertiary["rule_distribution"].get(rule, 0) + 1

    # ---- merged M1B invariants stay in the loop (freeze entry gate 4): the three
    # checkers whose inputs the M1C summary carries run; the two that read M1B-only
    # arm schemas (mirror arms / CONTINUED) are recorded NOT_APPLICABLE, never passed.
    import m1b_invariants as IV
    inv = {"observation_horizon": IV.observation_horizon_consistency(run_dir),
           "amortisation_divisor": IV.amortisation_divisor_consistency(run_dir),
           "retrieval_no_fire_no_effect":
               {"invariant": "retrieval_no_fire_no_effect", "status": "NOT_APPLICABLE",
                "detail": "M1C arm set has no RETR_ORACLE mirror arm"},
           "typed_failure_cross_path":
               {"invariant": "typed_failure_cross_path_consistency", "status": "NOT_APPLICABLE",
                "detail": "M1C arm set has no mirror-path arms"}}

    # ---- frozen terminal (precedence + halting idiom)
    if receipt_binding_defects:
        terminal = "RECEIPT_BINDING_DEFECT"
    elif assay_defects:
        terminal = "ASSAY_DEFECT"
    elif missing_arms or censored_arms:
        terminal = "CANNOT_CHECK_MISSING_OR_CENSORED_ARM"
    elif crossing_rung is not None:
        terminal = "CROSSING_OBSERVED__AT_REGISTERED_SCOPE"
    elif net_curve[-1] <= 0:
        terminal = "NO_CROSSING_AT_MAX_T"
    else:
        terminal = "NO_CROSSING_AT_MAX_T"   # net>0 at 512 but family not rejected
    summary = {"schema": "OCM_M1C_SCALING_SUMMARY",
               "toy_selftest_only_NOT_SCORED_EVIDENCE": WORLDS_MODE["toy"],
               "freeze": {"path": str(FREEZE_PATH.relative_to(REPO)), "sha256": FREEZE_SHA256},
               "worlds": worlds, "seals_verified": seals,
               "ladder": list(rungs), "t_max_served": t_max,
               "guards": {"leakage_digests": leakage, "cyclic_target_binding_ok": cyclic_ok,
                          "serve_determinism_violations": determinism_violations[:20],
                          "restart_evidence_ok": restart_ok,
                          "dev_charge_entries": dev_entries,
                          "receipt_binding_defects": receipt_binding_defects,
                          "assay_defects": assay_defects},
               "primary": {"net_curve_head": net_curve[:8],
                           "net_at_rungs": {str(r["T"]): r["net"] for r in rung_table},
                           "rung_table": rung_table, "holm_family": holm,
                           "t_star_continuous": t_star_cont,
                           "t_star_boot_ci": boot["t_star_ci"],
                           "crossing_rate_boot": boot["crossing_rate"],
                           "crossing_rung": crossing_rung},
               "secondary": secondary, "tertiary": tertiary,
               "cost_ledger_hdi14": {a: r.get("cost_ledger_hdi14", {})
                                     for a, r in reports.items()},
               "recovery_share_vs_known_structure_oracle": recovery_vs_ks,
               "m1b_invariants": inv,
               "terminal": terminal,
               "wall_seconds": round(time.perf_counter() - started, 6)}
    inv["recovery_over_unit"] = IV.recovery_over_unit_flag(summary)
    R1.write_json(paths["summary"], summary)
    R1.events_append(run_dir, "analyze", "M1C_SUMMARY",
                     {"terminal": terminal, "crossing_rung": crossing_rung,
                      "t_star_continuous": t_star_cont})
    R1.seal_phase(run_dir, "analyze")
    R1.ledger_update(run_dir, phase="analyze",
                     phase_wall_seconds=summary["wall_seconds"])
    print(json.dumps({"terminal": terminal, "crossing_rung": crossing_rung,
                      "t_star_continuous": t_star_cont,
                      "net_at_rungs": summary["primary"]["net_at_rungs"],
                      "holm_rejected": [r["T"] for r in rung_table if r["rejected"]]},
                     indent=1))
    return summary


def _enter_toy_worlds() -> None:
    """SELFTEST ONLY: both the M1B machinery and this runner record-not-enforce."""
    WORLDS_MODE["toy"] = True
    B1.WORLDS_MODE["toy"] = True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="M1C amortisation-scaling runner (frozen protocol)")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--phase", required=True,
                    choices=["dev", "checkpoint", "serve", "restart-and-serve",
                             "analyze", "all"])
    ap.add_argument("--arm")
    ap.add_argument("--t-max", type=int, default=max(RUNGS))
    ap.add_argument("--serve-budget", type=int, default=SERVE_BUDGET)
    ap.add_argument("--slots", type=int, default=SERVE_BUDGET,
                    help="dev-phase budget (frozen: the M1B dev budget 200000)")
    ap.add_argument("--selftest-toy-worlds", action="store_true",
                    help="SELFTEST ONLY: toy worlds, recorded not enforced, never scored")
    args = ap.parse_args(argv)
    run_dir = Path(args.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_files(run_dir)["serves"]).mkdir(exist_ok=True)
    if args.selftest_toy_worlds:
        _enter_toy_worlds()
    if args.phase == "dev":
        phase_dev_scaling(run_dir, args.slots)
    elif args.phase == "checkpoint":
        phase_checkpoint_scaling(run_dir)
    elif args.phase == "serve":
        if args.arm not in SCALING_ARMS:
            raise SystemExit(f"UNKNOWN_ARM: {args.arm}")
        phase_serve(run_dir, args.arm, args.t_max, args.serve_budget)
    elif args.phase == "restart-and-serve":
        if args.arm not in SCALING_ARMS:
            raise SystemExit(f"UNKNOWN_ARM: {args.arm}")
        phase_restart_and_serve(run_dir, args.arm, args.t_max, args.serve_budget)
    elif args.phase == "analyze":
        phase_analyze(run_dir)
    elif args.phase == "all":
        phase_dev_scaling(run_dir, args.slots)
        phase_checkpoint_scaling(run_dir)
        for arm in SCALING_ARMS:
            phase_restart_and_serve(run_dir, arm, args.t_max, args.serve_budget)
        phase_analyze(run_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
