"""Freeze-custody and verification checker v2.

Mirrors the v1 custody discipline, hardened:

  1. FREEZE custody: at FREEZE_COMMIT (recorded below) the battery, basis
     grid, and prior disclosure existed, and NO implementation, outcome,
     adjudication, or screen file existed (asserted via git cat-file).
  2. Battery blob: NEUTRAL_BATTERY_FREEZE_V1.json matches the recorded blob.
  3. Regeneration: battery_generate_v1.py regenerates the battery
     byte-identically (determinism of the frozen generation rules).
  4. Outcome integrity: every BLIND_OUTCOME_V2_*.json present; search-side
     sources contain no benchmark reads (lexical) — the semantic screen
     covers the rest.
  5. Screen verdict CLEAN with controls; adjudication present with the
     self-test passing.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = "research/gmi-833-blind-recovery-v2-v1/"
FREEZE_COMMIT = "f7378c8e0a36d1206b99080f8f7b4ddde518e92d"  # post-rebase hash of the original freeze 3ee0c4452
BATTERY_BLOB = "b7b358b55435ac0932e7e72318e189b59e10e5cf"  # amended (see erratum)
FREEZE_FILES = ["README.md", "battery_generate_v1.py",
                "NEUTRAL_BATTERY_FREEZE_V1.json", "BASIS_GRID_V1.json",
                "PRIOR_DISCLOSURE_V1.md"]
ABSENT_AT_FREEZE = ["neutral_search_v2.py", "run_v2_tranches.py",
                    "v1_counterfactual_or_task.py", "posthoc_adjudicate_v2.py",
                    "screen_v2.py", "check_v2.py",
                    "MOTIVATION_RECEIPT_V1.json",
                    "BLIND_OUTCOME_V2_T1.json", "BLIND_OUTCOME_V2_T2.json",
                    "BLIND_OUTCOME_V2_T3.json", "BLIND_OUTCOME_V2_T4.json",
                    "POSTHOC_RESULT_V2.json", "SCREEN_RESULT_V1.json"]


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def git(*args, check=True):
    return subprocess.run(["/usr/bin/git", "-C", str(HERE.parents[1]), *args],
                          capture_output=True, text=True, check=check)


def main():
    results = {}

    # 1. freeze custody
    if FREEZE_COMMIT != "FILLED_AT_OUTCOME_COMMIT":
        git("merge-base", "--is-ancestor", FREEZE_COMMIT, "HEAD")
        missing_at_freeze = []
        for f in FREEZE_FILES:
            git("cat-file", "-e", f"{FREEZE_COMMIT}:{PKG}{f}")
        for f in ABSENT_AT_FREEZE:
            p = git("cat-file", "-e", f"{FREEZE_COMMIT}:{PKG}{f}", check=False)
            if p.returncode == 0:
                missing_at_freeze.append(f)
        results["freeze_custody"] = {
            "freeze_commit": FREEZE_COMMIT,
            "freeze_files_present": True,
            "implementation_absent_at_freeze": not missing_at_freeze,
            "violations": missing_at_freeze}
    else:
        results["freeze_custody"] = {"status": "FREEZE_COMMIT_PLACEHOLDER"}

    # 2. battery blob
    bat = (HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_bytes()
    results["battery_blob_ok"] = git_blob_sha(bat) == BATTERY_BLOB

    # 3. regeneration determinism (runs the frozen generator to temp)
    regen = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {str(HERE)!r});"
         "import battery_generate_v1 as g; g.main()"],
        capture_output=True, text=True, cwd=str(HERE))
    # battery_generate writes NEUTRAL_BATTERY_FREEZE_V1.json in place; the
    # write must be byte-identical to the committed file.
    bat2 = (HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_bytes()
    results["battery_regeneration_deterministic"] = bat2 == bat

    # 4. outcome presence + no benchmark reads in search-side sources
    outcomes = {}
    for t in ("T1", "T2", "T3", "T4"):
        p = HERE / f"BLIND_OUTCOME_V2_{t}.json"
        outcomes[t] = p.exists()
        if p.exists():
            json.loads(p.read_text())  # structural validity
    results["outcomes_present"] = outcomes
    search_src = "".join(
        (HERE / f).read_text() for f in
        ("battery_generate_v1.py", "neutral_search_v2.py", "run_v2_tranches.py"))
    results["search_side_no_benchmark_reference"] = (
        "KNOWN_FAMILY_BENCHMARK" not in search_src
        and "6b9ac3095c90d74e2717671a70ad7cc18955310c" not in search_src
        and "posthoc_fingerprint" not in search_src)

    # 5. screen + adjudication artifacts
    screen = HERE / "SCREEN_RESULT_V1.json"
    posthoc = HERE / "POSTHOC_RESULT_V2.json"
    receipt = HERE / "MOTIVATION_RECEIPT_V1.json"
    if screen.exists():
        s = json.loads(screen.read_text())
        results["screen"] = {"verdict": s["screen_verdict"],
                             "clean": s["screen_verdict"] == "CLEAN"}
    if posthoc.exists():
        p = json.loads(posthoc.read_text())
        results["posthoc"] = {
            "selftest_pass": p["no_hardcoded_solution_selftest"]["pass"],
            "terminals": {k: v["terminal"] for k, v in
                          p["adjudications"].items()}}
    if receipt.exists():
        r = json.loads(receipt.read_text())
        results["motivation_receipt"] = {
            "or_counterfactual_terminal":
                r["rows"]["OR_COUNTERFACTUAL"]["v1_terminal_would_be"],
            "xor_v1_terminal":
                r["rows"]["XOR_V1_ACTUAL"]["v1_terminal_would_be"]}

    # 6. recomputation bindings (light, CI-safe): recompute T1 per-task costs
    #    (U_ORD), T2 guard-3 machines, and T4 cost summary from code+battery
    #    and assert equality with the committed outcomes.
    import sys as _sys
    _sys.path.insert(0, str(HERE))
    battery = json.loads((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
    from battery_generate_v1 import delay_battery as _delay
    from neutral_search_v2 import (Basis as _Basis, FastBasis as _FBasis,
                                   rows_to_atom_semantics as _ras,
                                   semantic_cost_layered_dp as _dp,
                                   semantic_cost_layered_dp_fast as _dpf)
    from run_v2_tranches import simulate_state_machine as _sim
    recompute = {}
    t1 = json.loads((HERE / "BLIND_OUTCOME_V2_T1.json").read_text())
    b2 = battery["batteries"]["B_BOOL2"]
    atom_sem = _ras(b2["per_task_tasks"][0]["inputs"], ["x0", "x1"])
    targets = [tuple(t["required_outputs"]) for t in b2["per_task_tasks"]]
    r = _dp(atom_sem, _Basis("U_ORD", 3), targets)
    recompute["t1_per_task_costs_match"] = (
        [x["cost"] for x in r["targets"]] ==
        t1["runs"]["U_ORD_g3"]["per_task_costs"])
    t2 = json.loads((HERE / "BLIND_OUTCOME_V2_T2.json").read_text())
    basis3 = _FBasis("U_ORD", 3)
    rows3 = [(s, x) for s in range(-3, 4) for x in (0, 1)]
    asem = {"S": tuple(s for s, x in rows3), "X": tuple(x for s, x in rows3)}
    dpk = _dpf(asem, _FBasis("U_ORD", 3), [], layer_cap=12, return_known=True)
    by_cost = {}
    for k in dpk["known"]:
        by_cost.setdefault(k["cost"], []).append(k)
    ok_t2 = True
    for run in t2["runs"]:
        if run["guard"] != 3 or not run["machine"]:
            continue
        bat_lag = next(t for t in battery["batteries"]["B_DELAY"]["tasks"]
                       if t["lag"] == run["lag"])
        found_cost = None
        for total in range(0, run["machine"]["total_cost"] + 1):
            for cs in range(0, total + 1):
                done = False
                for es in by_cost.get(cs, []):
                    for ey in by_cost.get(total - cs, []):
                        ok, _ = _sim(es["expr"], ey["expr"], basis3,
                                     bat_lag["machine_inputs"],
                                     bat_lag["required_outputs"])
                        if ok:
                            found_cost = total
                            done = True
                            break
                    if done:
                        break
                if done:
                    break
            if found_cost is not None:
                break
        ok_t2 = ok_t2 and found_cost == run["machine"]["total_cost"]
    recompute["t2_guard3_minimal_costs_match"] = ok_t2
    t4 = json.loads((HERE / "BLIND_OUTCOME_V2_T4.json").read_text())
    b3 = battery["batteries"]["B_BOOL3"]
    asem3 = _ras(b3["per_task_tasks"][0]["inputs"], ["i0", "i1", "i2"])
    tg = [tuple(t["required_outputs"]) for t in b3["per_task_tasks"]]
    r4 = _dp(asem3, _Basis("U_ORD", 3), tg)
    recompute["t4_per_task_costs_match"] = (
        [x["cost"] for x in r4["targets"]] ==
        [t["cost"] for t in t4["runs"]["per_task"]["tasks"]])
    results["recomputation_bindings"] = recompute

    (HERE / "RESULT_V2.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
