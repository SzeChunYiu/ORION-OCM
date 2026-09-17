#!/usr/bin/env python3
"""REV-L47 re-run batch runner (phase 1) + section-d replica stages.

Executed ON REMOTE HOSTS at the pushed branch commit containing
REV_FREEZE_V1.md. Runs, per package:
  - MECHANICAL self-tests (content legs of the custody-repair receipts);
  - SUBSTANTIVE single-stage re-runs under the pre-registered decision
    rules (REV_FREEZE_V1.md);
  - section-d replica stage A (acquisition + training only) and stage B
    (holdout execution + comparisons) — stage B refuses to run unless the
    stage-2 freeze file exists in the tree (commit B precedes it).

Writes one receipt per package to --out plus a batch manifest. Nothing on
the Mac ever executes corpus code.

Usage:
  python3 run_batch_v1.py --repo <clone> --out <receipts-dir> [--only pkg,...]
  python3 run_batch_v1.py --repo <clone> --out <receipts-dir> --section-d-stage-a
  python3 run_batch_v1.py --repo <clone> --out <receipts-dir> --section-d-stage-b
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO = None  # set from --repo
PKG = "research/gmi-833-rev-l47-custody-gaps-v1"

MECHANICAL_TESTS = [
    ("gmi-833-aj9a-known-family-benchmark-v1", "check_aj9a.py"),
    ("gmi-833-transform-geometry-v1", "test_transform_geometry_v1.py"),
    ("gmi-833-remint-equivariance-v1", "test_remint_equivariance_v1.py"),
    ("gmi-833-pareto-topology-v1", "test_pareto_topology_v1.py"),
    ("gmi-capability-held-freeze-v1", "test_held_freeze_v1.py"),
    ("gmi-capability-transfer-freeze-v1", "test_transfer_freeze_v1.py"),
    ("gmi-capability-held-score-v1", "test_held_score_v1.py"),  # consumer leg
]

# package -> (executor, committed artifact, test file or None, equality mode)
SUBSTANTIVE = [
    ("gmi-833-aj9b-k01-blind-recovery-v1", "check_aj9b.py", None, "checker"),
    ("gmi-833-aj9c-k02-blind-recovery-v1", "check_aj9c.py", None, "checker"),
    ("gmi-833-aj9d-k03-blind-recovery-v1", "check_aj9d.py", None, "checker"),
    ("gmi-833-aj9e-k04-blind-recovery-v1", "check_aj9e.py", None, "checker"),
    ("gmi-833-aj9f-k05-blind-recovery-v1", "check_aj9f.py", None, "checker"),
    ("gmi-833-aj9h-k07-k11-blind-recovery-v1", "check_aj9h.py", None, "checker"),
    ("gmi-833-developmental-naturality-v1", "developmental_naturality_v1.py",
     "test_developmental_naturality_v1.py", "stdout_json"),
    ("gmi-833-real-transition-protocol-v1", "real_transition_protocol_v1.py",
     "test_real_transition_protocol_v1.py", "stdout_json"),
    ("gmi-history-morphology-discovery-v1", "history_morphology_discovery_v1.py",
     "test_history_morphology_discovery_v1.py", "stdout_json"),
    ("gmi-heldout-long-sequence-v1", "heldout_long_sequence_v1.py",
     "test_heldout_long_sequence_v1.py", "stdout_json"),
    ("gmi-833-heldout-20-transitions-v1", "heldout_transition_v1.py",
     None, "stdout_json"),
]


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True,
                          check=True).stdout


def run_cmd(cmd: list[str], cwd: Path, timeout: int = 900) -> dict:
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          timeout=timeout)
    return {"cmd": " ".join(cmd), "cwd": str(cwd), "exit": proc.returncode,
            "wall_s": round(time.time() - t0, 3),
            "stdout_sha256": hashlib.sha256(
                proc.stdout.encode()).hexdigest(),
            "stdout_len": len(proc.stdout),
            "stderr_tail": proc.stderr[-400:]}


def pkg_clean(pkg: str) -> bool:
    st = git("status", "--porcelain", "--", f"research/{pkg}")
    return st.strip() == ""


def base_receipt(kind: str) -> dict:
    run_commit = git("rev-parse", "HEAD").strip()
    freeze_adds = git("log", "--diff-filter=A", "--format=%H", "--",
                      f"{PKG}/REV_FREEZE_V1.md").splitlines()
    freeze_commit = freeze_adds[-1] if freeze_adds else None
    ancestor = None
    if freeze_commit:
        ancestor = subprocess.run(
            ["git", "-C", str(REPO), "merge-base", "--is-ancestor",
             freeze_commit, run_commit],
            capture_output=True).returncode == 0
    return {
        "schema": "REV_L47_RERUN_RECEIPT_V1",
        "kind": kind,
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "run_commit": run_commit,
        "rev_freeze_first_add_commit": freeze_commit,
        "freeze_ancestor_of_run": ancestor,
        "freeze_note": "pre-registered decision rule in "
                       f"{PKG}/REV_FREEZE_V1.md (first-add commit must be an "
                       "ancestor of run_commit - verified above; after any "
                       "squash merge resolve these SHAs via refs/pull/<N>/head, "
                       "the #980 custody-pin pattern)",
        "utc_epoch": int(time.time()),
    }


def mechanical_pass(out: Path, only: set[str] | None) -> None:
    for pkg, script in MECHANICAL_TESTS:
        if only and pkg not in only:
            continue
        cwd = REPO / "research" / pkg
        clean_before = pkg_clean(pkg)
        r = run_cmd([sys.executable, script], cwd)
        rec = base_receipt("MECHANICAL_SELFTEST")
        rec.update({"package": pkg, "script": script,
                    "clean_tree_before": clean_before,
                    "clean_tree_after": pkg_clean(pkg),
                    "run": r})
        if r["exit"] == 0 and rec["clean_tree_after"]:
            rec["verdict"] = "CONTENT_LEG_GREEN"
        elif pkg == "gmi-833-aj9a-known-family-benchmark-v1" and \
                "hostile_results" in r["stderr_tail"]:
            rec["verdict"] = "CONTENT_LEG_FAIL__AUDIT_WALKER_LIST_ELEMENT_EVASION"
            rec["root_cause"] = (
                "check_aj9a.audit_config.walk() yields dict values but never "
                "string LIST elements, so denylisted tokens inside lists (e.g. "
                '{"ops":["dense_layer"]}) evade the MACRO_DENY scan; the '
                "checker's own 11-hostile battery catches exactly this "
                "(assert all(hostile_results) fails on 4 ops-hostiles: "
                "dense_layer, self_attention, bayes_update, "
                "genetic_algorithm). Single-commit file (6a6ef5ca6) - the "
                "defect is present since landing, version-independent (pure "
                "dict/list logic). aj-lane package: not editable here; "
                "routed to the owning lane with lever = make walk() yield "
                "string leaf values from lists.")
        else:
            rec["verdict"] = "CONTENT_LEG_FAIL"
        (out / f"{pkg}__selftest.json").write_text(json.dumps(rec, indent=2))
        print(f"[{rec['verdict']}] {pkg} ({r['exit']}, {r['wall_s']}s)")


def claim_subset(committed, live) -> tuple[bool, list]:
    """every outcome claim in `committed` present+equal in `live` (recursive;
    missing keys are failures). Prose-only extra keys in committed are the
    caller's responsibility to exclude."""
    misses = []

    def walk(c, l, path):
        if isinstance(c, dict):
            if not isinstance(l, dict):
                misses.append(f"{path}: committed dict vs live {type(l).__name__}")
                return
            for k, v in c.items():
                if k not in l:
                    misses.append(f"{path}.{k}: missing in live")
                else:
                    walk(v, l[k], f"{path}.{k}")
        elif isinstance(c, list):
            if not isinstance(l, list) or len(l) != len(c):
                misses.append(f"{path}: list shape mismatch")
                return
            for i, (cv, lv) in enumerate(zip(c, l)):
                walk(cv, lv, f"{path}[{i}]")
        else:
            if c != l:
                misses.append(f"{path}: {c!r} != {l!r}")

    walk(committed, live, "$")
    return not misses, misses


def substantive_pass(out: Path, only: set[str] | None) -> None:
    for pkg, executor, test, mode in SUBSTANTIVE:
        if only and pkg not in only:
            continue
        cwd = REPO / "research" / pkg
        clean_before = pkg_clean(pkg)
        rec = base_receipt("SUBSTANTIVE_RERUN")
        rec.update({"package": pkg, "executor": executor,
                    "clean_tree_before": clean_before})
        r = run_cmd([sys.executable, executor], cwd)
        rec["run"] = r
        equality = {"mode": mode}
        if mode == "checker":
            # checker rewrites RESULT_V1.json from the live run; equality =
            # PARSED content vs the committed HEAD blob (byte-level drift is
            # a serialization artifact of the original landing: committed
            # files were written with different separators than the checker
            # line produces - evidence in receipts). Tree restored after.
            head_result = git("show", f"HEAD:research/{pkg}/RESULT_V1.json")
            live_result = (cwd / "RESULT_V1.json").read_text()
            try:
                eq = json.loads(live_result) == json.loads(head_result)
            except Exception:
                eq = False
            equality["parsed_json_equal_committed_RESULT"] = eq
            equality["byte_equal"] = live_result == head_result
            equality["serialization_artifact_only"] = (
                eq and live_result != head_result)
            diffstat = git("diff", "--stat", "--", f"research/{pkg}")
            equality["worktree_diffstat"] = diffstat.strip()
            subprocess.run(["git", "-C", str(REPO), "checkout", "--",
                            f"research/{pkg}"], capture_output=True)
            equality["tree_restored"] = pkg_clean(pkg)
            green = r["exit"] == 0 and eq
        else:
            second = subprocess.run([sys.executable, executor],
                                    cwd=str(cwd), capture_output=True,
                                    text=True)
            committed = (cwd / "RESULT_V1.json").read_text()
            try:
                eq = json.loads(second.stdout) == json.loads(committed)
            except Exception:
                eq = False
            equality["parsed_json_equal_committed_RESULT"] = eq
            equality["byte_equal"] = second.stdout == committed
            equality["within_host_deterministic"] = "compared via sha256 of both runs"
            equality["second_run_stdout_sha256"] = hashlib.sha256(
                second.stdout.encode()).hexdigest()
            green = second.returncode == 0 and eq
            if not eq and pkg in (
                    "gmi-history-morphology-discovery-v1",
                    "gmi-heldout-long-sequence-v1"):
                # committed RESULT is a curated receipt (single-commit
                # executors; committed file adds `interpretation` prose /
                # flattened rows). Equality at claim level: every committed
                # OUTCOME field present+equal in the raw live output.
                live = json.loads(second.stdout)
                com = json.loads(committed)
                cur = {k: v for k, v in com.items() if k != "interpretation"}
                if pkg == "gmi-heldout-long-sequence-v1":
                    # rows matched by n; committed row fields checked against
                    # the richer live row fields only where present by name
                    rows_ok, misses = True, []
                    for section in ("calibration", "heldout"):
                        for crow in com[section]:
                            lrows = [x for x in live[section]
                                     if x.get("n") == crow["n"]]
                            if not lrows:
                                rows_ok = False
                                misses.append(f"{section} n={crow['n']}: no live row")
                                continue
                            lrow = lrows[0]
                            for k, v in crow.items():
                                if k in lrow and lrow[k] != v:
                                    rows_ok = False
                                    misses.append(
                                        f"{section} n={crow['n']}.{k}: "
                                        f"{v!r} != {lrow[k]!r}")
                            if live is not None and lrow.get(
                                    "exact_candidate_count") != crow.get(
                                    "exact_candidate_count"):
                                rows_ok = False
                                misses.append(
                                    f"{section} n={crow['n']}: exact count")
                    ok, misses2 = rows_ok, misses
                else:
                    ok, misses2 = claim_subset(cur, live)
                equality["claim_level_equality"] = {
                    "ok": ok, "misses": misses2[:20]}
                green = second.returncode == 0 and ok
        if test:
            tr = run_cmd([sys.executable, test, "-v"], cwd)
            rec["test"] = tr
            green = green and tr["exit"] == 0
        rec["clean_tree_after"] = pkg_clean(pkg)
        rec["equality"] = equality
        rec["verdict"] = "CLEARED_GREEN" if green else "REPLICA_FAIL"
        (out / f"{pkg}__rerun.json").write_text(json.dumps(rec, indent=2))
        print(f"[{rec['verdict']}] {pkg} ({r['exit']}, {r['wall_s']}s)")


def section_d_stage_a(out: Path) -> None:
    sys.path.insert(0, str(REPO / "research" /
                           "gmi-section-d-uncertainty-extrapolation-v5"))
    import secrets
    from fractions import Fraction
    import training_measure_v5 as tm

    freeze_commit = git("log", "--diff-filter=A", "--format=%H", "--",
                        f"{PKG}/REV_FREEZE_V1.md").splitlines()[-1]
    raw = secrets.token_bytes(16384)
    bits = [1 if b < 224 else 0 for b in raw]
    ones = sum(bits)
    packed = bytearray()
    for i in range(0, 16384, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        packed.append(byte)
    packed_hex = packed.hex()
    packed_sha = hashlib.sha256(bytes(packed)).hexdigest()
    sample = {"n": 16384, "packed_bytes": 2048, "packing": "MSB_FIRST_8",
              "threshold": 224, "packed_bits_hex": packed_hex,
              "ones_count": ones, "first_64_ones_count": sum(bits[:64]),
              "packed_sha256": packed_sha,
              "authority_freeze_commit": freeze_commit,
              "acquisition": "secrets.token_bytes(16384) on "
                             f"{platform.node()} at run after stage-1 freeze "
                             f"{freeze_commit[:9]}; single draw, no reroll",
              "raw_sha256": hashlib.sha256(raw).hexdigest()}

    train = tm.build()
    rows = {r["n"]: r for r in train["rows"]}
    coords = ("persistent_cells_single_orientation", "migration_ops",
              "key_block_ops", "value_block_ops")
    fits, residuals = {}, {}
    for coord in coords:
        y2, y3 = rows[2][coord], rows[3][coord]
        a, b = y3 - y2, y2 - 2 * (y3 - y2)
        fits[coord] = {"a": a, "b": b}
        residuals[coord] = {"n4": rows[4][coord] - (a * 4 + b),
                            "n5": rows[5][coord] - (a * 5 + b)}
    # stage-2 freeze draft: predictions + crossover derived ONLY from fitted
    # coordinates (v5 FREEZE_V5.md sec 11; construction mirrors
    # crossover_from_observation applied to predicted coordinates)
    def fj(x):
        return {"numerator": x.numerator, "denominator": x.denominator}
    predictions = {}
    for n in (17, 31):
        p = {c: fits[c]["a"] * n + fits[c]["b"] for c in coords}
        advantage = p["key_block_ops"] - p["value_block_ops"]
        q = Fraction(p["migration_ops"], advantage)
        predictions[str(n)] = {
            **{c: p[c] for c in coords},
            "continuous_crossover": fj(q),
            "first_strict_migration_horizon": q.numerator // q.denominator + 1,
            "m2_stay_key": 2 * p["key_block_ops"],
            "m2_migrate_value": p["migration_ops"] + 2 * p["value_block_ops"],
            "m3_stay_key": 3 * p["key_block_ops"],
            "m3_migrate_value": p["migration_ops"] + 3 * p["value_block_ops"],
        }
    draft = {
        "schema": "REV_L47_SECTION_D_REPLICA_FIT_FREEZE_V1",
        "stage1_freeze": f"{PKG}/REV_FREEZE_V1.md",
        "training_receipt_sha256": train["numeric_receipt_sha256"],
        "affine_fits": fits, "validation_residuals": residuals,
        "holdout_predictions": predictions,
        "note": "commit BEFORE any n=17/31 execution (v5 sec 11 discipline)",
    }
    rec = base_receipt("SECTION_D_STAGE_A")
    rec.update({"sample": {k: v for k, v in sample.items()
                           if k != "packed_bits_hex"},
                "stage1_freeze_commit": freeze_commit,
                "train_rows": train["rows"],
                "training_receipt_sha256": train["numeric_receipt_sha256"],
                "affine_fits": fits, "validation_residuals": residuals,
                "holdout_executed": False,
                "note": "stage-2 freeze (commit B) must land before stage B"})
    (out / "section_d_stage_a.json").write_text(json.dumps(rec, indent=2))
    (out / "REPLICA_SAMPLE_V1.json").write_text(json.dumps(sample, indent=2))
    (out / "REPLICA_TRAIN_V1.json").write_text(json.dumps(train, indent=2))
    (out / "REPLICA_FIT_FREEZE_DRAFT_V1.json").write_text(
        json.dumps(draft, indent=2))
    print(f"[STAGE_A] freeze={freeze_commit[:9]} ones={ones} "
          f"sha={packed_sha[:16]} fits="
          f"{ {k: (v['a'], v['b']) for k, v in fits.items()} }")
    print(f"residuals (must all be zero): {residuals}")


def section_d_stage_b(out: Path) -> None:
    sys.path.insert(0, str(REPO / "research" /
                           "gmi-section-d-uncertainty-extrapolation-v5"))
    from fractions import Fraction
    import section_d_uncertainty_extrapolation_witness as wit

    pkg_dir = REPO / PKG

    def first_add_commit(path: str) -> str:
        return git("log", "--diff-filter=A", "--format=%H", "--",
                   path).splitlines()[-1]

    def is_ancestor(a: str, b: str) -> bool:
        return subprocess.run(
            ["git", "-C", str(REPO), "merge-base", "--is-ancestor", a, b],
            capture_output=True).returncode == 0

    stage2 = json.loads((pkg_dir / "REPLICA_FIT_FREEZE_V1.json").read_text())
    sample = json.loads((pkg_dir / "REPLICA_SAMPLE_V1.json").read_text())

    run_commit = git("rev-parse", "HEAD").strip()
    fit_commit = first_add_commit(f"{PKG}/REPLICA_FIT_FREEZE_V1.json")
    sample_commit = first_add_commit(f"{PKG}/REPLICA_SAMPLE_V1.json")
    freeze_commit = first_add_commit(f"{PKG}/REV_FREEZE_V1.md")
    custody = {
        "freeze_ancestor_of_sample": is_ancestor(freeze_commit, sample_commit),
        "sample_ancestor_of_fit_freeze": is_ancestor(sample_commit, fit_commit),
        "fit_freeze_ancestor_of_run": is_ancestor(fit_commit, run_commit),
        "sample_authority_matches_stage1_freeze":
            sample.get("authority_freeze_commit") == freeze_commit,
        "fit_freeze_train_sha_matches_stage_a":
            stage2.get("training_receipt_sha256")
            == json.loads((pkg_dir / "REPLICA_TRAIN_V1.json").read_text())
            ["numeric_receipt_sha256"],
    }

    packed = bytes.fromhex(sample["packed_bits_hex"])
    u7 = (hashlib.sha256(packed).hexdigest() == sample["packed_sha256"]
          and len(packed) == 2048 and sum(
              (byte >> shift) & 1 for byte in packed
              for shift in range(7, -1, -1)) == sample["ones_count"])
    bits = [(byte >> shift) & 1 for byte in packed for shift in range(7, -1, -1)]
    full = wit.hoeffding_boundary(bits, 16384, Fraction(1, 64))
    small = wit.hoeffding_boundary(bits[:64], 64, Fraction(1, 4))
    TRUE_P, TRUE_Q = Fraction(7, 8), Fraction(32, 9)

    def iv_f(iv: dict) -> tuple:
        lo = iv["lo"]
        hi = iv["hi"]
        if lo is None or hi is None:
            return None
        return (Fraction(lo["numerator"], lo["denominator"]),
                Fraction(hi["numerator"], hi["denominator"]))

    p_iv = iv_f(full["p_interval"])
    q_iv = iv_f(full["q_interval"])
    sq_iv = iv_f(small["q_interval"])
    u = {
        "U1_p_in_interval": p_iv is not None and p_iv[0] <= TRUE_P <= p_iv[1],
        "U2_q_in_interval": q_iv is not None and q_iv[0] <= TRUE_Q <= q_iv[1],
        "U3_q_strictly_in_3_4": q_iv is not None and q_iv[0] > 3 and q_iv[1] < 4,
        "U4_unique_switch_set": full["possible_first_strict_integer_switches"] == [4],
        "U5_bound_reported": full["failure_bound_symbolic"],
        "U6_small_control_not_localizing": not (
            sq_iv is not None and sq_iv[0] > 3 and sq_iv[1] < 4),
        "U7_sample_reproduces": bool(u7),
    }

    def to_fraction(fj_: dict) -> Fraction:
        return Fraction(fj_["numerator"], fj_["denominator"])

    frozen = {}
    for n in (17, 31):
        pred = stage2["holdout_predictions"][str(n)]
        frozen[n] = {
            "persistent_cells_single_orientation":
                pred["persistent_cells_single_orientation"],
            "migration_ops": pred["migration_ops"],
            "key_block_ops": pred["key_block_ops"],
            "value_block_ops": pred["value_block_ops"],
            "continuous_crossover": to_fraction(pred["continuous_crossover"]),
            "first_strict_migration_horizon":
                pred["first_strict_migration_horizon"],
            "m2_stay_key": pred["m2_stay_key"],
            "m2_migrate_value": pred["m2_migrate_value"],
            "m3_stay_key": pred["m3_stay_key"],
            "m3_migrate_value": pred["m3_migrate_value"],
        }
    x = {}
    for n in (17, 31):
        for remint in (False, True):
            obs = wit.measure_holdout(n, remint=remint)
            x[f"X8_exact_n{n}_remint{int(remint)}"] = bool(
                obs["key_exact"] and obs["value_exact"]
                and obs["migration_exact"])
            x[f"X4X5_n{n}_remint{int(remint)}_match"] = bool(
                wit.compare_observation_to_frozen(obs, n, frozen=frozen[n]))
    obs17 = wit.measure_holdout(17, remint=False)
    bad = dict(frozen[17])
    bad["migration_ops"] = bad["migration_ops"] + 1
    x["X10_hostile_detected"] = not wit.compare_observation_to_frozen(
        obs17, 17, frozen=bad)
    for n in (17, 31):
        cross = wit.crossover_from_observation(wit.measure_holdout(n))
        pred = stage2["holdout_predictions"][str(n)]
        x[f"X6X7_crossover_n{n}"] = bool(
            cross["continuous_crossover"]
            == wit.frac_json(to_fraction(pred["continuous_crossover"]))
            and cross["first_strict_migration_horizon"]
            == pred["first_strict_migration_horizon"])
    x["X9_remint_invariance"] = all(
        x[f"X4X5_n{n}_remint1_match"] and x[f"X8_exact_n{n}_remint1"]
        for n in (17, 31))

    custody_ok = all(custody.values())
    mechanical_u = (u["U3_q_strictly_in_3_4"] and u["U4_unique_switch_set"]
                    and u["U6_small_control_not_localizing"]
                    and u["U7_sample_reproduces"])
    statistical_u = u["U1_p_in_interval"] and u["U2_q_in_interval"]
    x_ok = all(x.values())
    if not (custody_ok and mechanical_u and x_ok):
        verdict = "REPLICA_FAIL"
    elif statistical_u:
        verdict = "CLEARED_GREEN"
    else:
        verdict = "CLEARED_GREEN_WITH_STATISTICAL_MISS_RECORDED"
    rec = base_receipt("SECTION_D_STAGE_B")
    rec.update({
        "custody_chain": custody,
        "stage2_freeze_commit": fit_commit,
        "sample_first_add_commit": sample_commit,
        "run_commit": run_commit,
        "full_sample_boundary": {
            k: (str(v) if isinstance(v, Fraction)
                else (json.loads(json.dumps(v)) if isinstance(v, list) else v))
            for k, v in full.items()},
        "small_sample_control": {k: str(v) if isinstance(v, Fraction) else v
                                 for k, v in small.items()},
        "U": u, "X": x,
        "verdict": verdict,
        "decision_rule": "REV_FREEZE_V1.md section-d: custody chain + "
                         "mechanical U + all X => green; U1/U2 statistical "
                         "miss retained honestly",
    })
    (out / "section_d_stage_b.json").write_text(json.dumps(rec, indent=2))
    print(json.dumps({"custody": custody, "U": u, "X": x,
                      "verdict": verdict}, indent=2))


def main() -> int:
    global REPO
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--section-d-stage-a", action="store_true")
    ap.add_argument("--section-d-stage-b", action="store_true")
    args = ap.parse_args()
    REPO = Path(args.repo).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    only = set(filter(None, args.only.split(",")))
    if args.section_d_stage_a:
        section_d_stage_a(out)
        return 0
    if args.section_d_stage_b:
        section_d_stage_b(out)
        return 0
    mechanical_pass(out, only)
    substantive_pass(out, only)
    manifest = base_receipt("BATCH_MANIFEST")
    manifest["tasks"] = [p.name for p in sorted(out.glob("*.json"))]
    (out / "BATCH_MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
