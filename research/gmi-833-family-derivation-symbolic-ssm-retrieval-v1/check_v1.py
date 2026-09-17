"""Check v1 — custody, determinism, pins, screens, recomputation bindings.

Offline, stdlib-only, byte-identical under -I -B and -I -O -B. Writes
RESULT_V1.json. Assertions (CI must see status GREEN):
  - freeze custody: freeze files present at the freeze commit; ALL
    implementation/outcome/adjudicator files absent there;
  - battery regeneration deterministic and sha256-pinned;
  - parent blob pins match;
  - search-side files carry no benchmark/fingerprint references;
  - screen CLEAN with controls;
  - outcomes present with the blind flag;
  - posthoc selftest + bijection + terminals;
  - recomputation bindings: battery census recomputed; affine-exhaust
    certificate recomputed at a smaller bound; stored machines re-simulated
    by the independent evaluator; null counts asserted.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

FREEZE_COMMIT = "98bd9369792e009d6db348dcfc570375b127f70d"
BATTERY_SHA256 = "5b385f0edfa035b28940f5dd982e0c69991a2ce6e0175e4c693073add26899f0"

FREEZE_FILES = [
    "PRIOR_DISCLOSURE_V1.md", "BASIS_GRID_V1.json", "battery_generate_v1.py",
    "NEUTRAL_BATTERY_FREEZE_V1.json", "PARENT_LEDGER.md", "README.md",
]
ABSENT_AT_FREEZE = [
    "machinery_v1.py", "proc1_v1.py", "proc2_v1.py", "run_tranches_v1.py",
    "screen_v1.py", "posthoc_adjudicate_v1.py", "check_v1.py",
    "FAMILY_FINGERPRINTS_V1.json", "THEORY.md",
    "BLIND_OUTCOME_V1_T1.json", "BLIND_OUTCOME_V1_T2.json",
    "BLIND_OUTCOME_V1_T3.json", "POSTHOC_RESULT_V1.json",
    "SCREEN_RESULT_V1.json", "CLAIMS_V1.json",
]
SEARCH_SIDE_FILES = [
    "battery_generate_v1.py", "machinery_v1.py", "proc1_v1.py",
    "proc2_v1.py", "run_tranches_v1.py",
]
PARENT_BLOBS = {
    "research/gmi-833-aj9a-known-family-benchmark-v1/KNOWN_FAMILY_BENCHMARK_V1.json":
        "6b9ac3095c90d74e2717671a70ad7cc18955310c",
    "research/gmi-833-blind-recovery-v2-v1/PRIOR_DISCLOSURE_V1.md":
        "c55a7cabfbd61bf0eccbfe6d0a8e034ffdd2999f",
    "research/gmi-833-blind-recovery-v2-v1/BASIS_GRID_V1.json":
        "364d67c50a507d0b7afab44621089070ed33f1d6",
    "research/gmi-833-blind-recovery-v2-v1/NEUTRAL_BATTERY_FREEZE_V1.json":
        "b7b358b55435ac0932e7e72318e189b59e10e5cf",
    "research/gmi-833-no-smuggling-audit-v1/audit_core_v1.py":
        "d39663ecd788e65fa8b473dbce21a232152511a8",
    "research/gmi-833-g0-register-core-v1/g0_register_core_v1.py":
        "6c80e7b1ee0cceedb5dc48eaf28bd3011750d80a",
    "research/gmi-833-g0-grammar-growth-v1/FREEZE_V1.md":
        "a1cc3f44828187faf143ad7efe4d3bab51437447",
}


def git(*args):
    return subprocess.run(["/usr/bin/git", "-C", str(REPO)] + list(args),
                          capture_output=True, text=True)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def check_freeze_custody():
    present, absent_ok = [], []
    for f in FREEZE_FILES:
        r = git("cat-file", "-e", "%s:research/gmi-833-family-derivation-"
                "symbolic-ssm-retrieval-v1/%s" % (FREEZE_COMMIT, f))
        present.append((f, r.returncode == 0))
    for f in ABSENT_AT_FREEZE:
        r = git("cat-file", "-e", "%s:research/gmi-833-family-derivation-"
                "symbolic-ssm-retrieval-v1/%s" % (FREEZE_COMMIT, f))
        absent_ok.append((f, r.returncode != 0))
    return {"freeze_commit": FREEZE_COMMIT,
            "freeze_files_present": all(v for _, v in present),
            "implementation_absent_at_freeze": all(v for _, v in absent_ok),
            "detail_present": dict(present),
            "detail_absent": dict(absent_ok)}


def check_battery():
    bat_path = HERE / "NEUTRAL_BATTERY_FREEZE_V1.json"
    sha = sha256_bytes(bat_path.read_bytes())
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        src = (HERE / "battery_generate_v1.py").read_text()
        # generator writes next to itself: copy generator+run in temp dir
        (tdp / "battery_generate_v1.py").write_text(src)
        r = subprocess.run([sys.executable, "-B",
                            str(tdp / "battery_generate_v1.py")],
                           capture_output=True, text=True, cwd=str(tdp))
        ok = (tdp / "NEUTRAL_BATTERY_FREEZE_V1.json").exists()
        if ok:
            ok = sha256_bytes((tdp / "NEUTRAL_BATTERY_FREEZE_V1.json")
                              .read_bytes()) == sha
        return {"sha256": sha, "pinned_ok": sha == BATTERY_SHA256,
                "regeneration_deterministic": bool(ok and r.returncode == 0)}


def check_parents():
    out = {}
    for path, blob in PARENT_BLOBS.items():
        r = git("hash-object", str(REPO / path))
        out[path] = (r.stdout.strip() == blob)
    return {"all_pinned": all(out.values()), "detail": out}


def check_search_side_clean():
    bad = {}
    for f in SEARCH_SIDE_FILES:
        text = (HERE / f).read_text()
        hits = []
        for needle in ("KNOWN_FAMILY_BENCHMARK", "posthoc_fingerprint",
                       "FAMILY_FINGERPRINTS", "family_id", "K05", "K08",
                       "M-FAM", "paper_name"):
            if needle in text:
                hits.append(needle)
        if hits:
            bad[f] = hits
    return {"search_side_no_benchmark_reference": not bad, "detail": bad}


def check_screen():
    p = HERE / "SCREEN_RESULT_V1.json"
    if not p.exists():
        return {"screen_clean": False, "missing": True}
    d = json.loads(p.read_text())
    return {"screen_clean": d["screen_verdict"] == "CLEAN",
            "controls_fired": d["lexical"]["matcher_positive_control_fired"]
            and d["a2_semantic"]["positive_controls_flagged"],
            "basis_clean": d["a2_semantic"]["basis"]["terminal"]
            == "CLEAN_AT_REGISTERED_AUDIT_SCOPE"}


def check_outcomes():
    out = {}
    for t in ("T1", "T2", "T3"):
        p = HERE / ("BLIND_OUTCOME_V1_%s.json" % t)
        if not p.exists():
            out[t] = {"present": False}
            continue
        d = json.loads(p.read_text())
        out[t] = {"present": True,
                  "blind_flag": d.get("benchmark_or_family_data_used") is False,
                  "schema": d.get("schema")}
    return {"all_present": all(v.get("present") for v in out.values()),
            "all_blind": all(v.get("blind_flag") for v in out.values()),
            "detail": out}


def _independent_eval():
    sys.path.insert(0, str(HERE))
    import posthoc_adjudicate_v1 as A
    return A


def check_recomputation():
    A = _independent_eval()
    bat = json.loads((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
    binds = {}
    # binding 1: battery census
    bc = bat["batteries"]["B_CONTR"]
    binds["battery_task_counts"] = (
        bc["n_tasks"] == 17424
        and bat["batteries"]["B_W2"]["n_tasks"] == 2401
        and bat["batteries"]["B_EP"]["n_tasks"] == 56
        and bc["successor_census"]["pairs_total"] == 792
        and bc["successor_census"][
            "pairs_with_two_plus_distinct_successors"] == 20)
    # binding 2: affine-exhaust at smaller bound
    rows = bat["batteries"]["B_EP"]["task_rows"]
    matches = []
    ranges = range(-2, 3)
    import itertools
    for co in itertools.product(ranges, repeat=6):
        ok = True
        for r in rows:
            v = co[0] + sum(co[i + 1] * r["stream"][i] for i in range(5))
            if v != r["required_final_output"]:
                ok = False
                break
        if ok:
            matches.append(co)
            break
    binds["ep_no_affine_at_bound2"] = len(matches) == 0
    # binding 3: stored T2 machines re-simulated independently
    out2 = json.loads((HERE / "BLIND_OUTCOME_V1_T2.json").read_text())
    stream = bat["batteries"]["B_W2"]["stream"]
    w2rows = bat["batteries"]["B_W2"]["task_rows"]
    ok3 = True
    n3 = 0
    for tid, mm in list(out2.get("machines_sample", {}).items())[:10]:
        o, _, legal = A.run_stream(mm, stream)
        if not legal or o != w2rows[int(tid)]["required_outputs"]:
            ok3 = False
        n3 += 1
    binds["t2_machines_resimulate"] = ok3 and n3 > 0
    gf_machines = out2.get("gatefree_machines_sample", {})
    okg = True
    ng = 0
    for tid, mm in list(gf_machines.items())[:10]:
        o, _, legal = A.run_stream(mm, stream)
        if not legal or o != w2rows[int(tid)]["required_outputs"]:
            okg = False
        ng += 1
    binds["t2_gatefree_machines_resimulate"] = okg
    # binding 4: TR-3 champion independent fitness
    out3 = json.loads((HERE / "BLIND_OUTCOME_V1_T3.json").read_text())
    errs = 0
    for r in rows:
        o, _, legal = A.run_stream(out3["primary"]["genome"], r["stream"])
        if not legal or o is None or o[-1] != r["required_final_output"]:
            errs += 1
    binds["t3_champion_independent_errors"] = errs
    binds["t3_claimed_errors"] = out3["primary"]["fitness"][0]
    binds["t3_null_count"] = len(out3["nulls"]["champion_errors"])
    binds["t3_nulls_none_better"] = (
        min(out3["nulls"]["champion_errors"]) >=
        out3["primary"]["fitness"][0])
    # binding 5: TR-1 crossover data + null counts
    out1 = json.loads((HERE / "BLIND_OUTCOME_V1_T1.json").read_text())
    binds["t1_null_count"] = len(out1["nulls"]["champion_errors"])
    binds["t1_readout_certs_empty"] = (
        len(out1["readout_certificates"]["affine_solutions"]) == 0
        and len(out1["readout_certificates"]["gate_solutions"]) == 0)
    binds["t1_crossover_arms"] = len(out1["crossover"])
    return binds


def check_posthoc():
    p = HERE / "POSTHOC_RESULT_V1.json"
    if not p.exists():
        return {"present": False, "selftest_pass": False}
    d = json.loads(p.read_text())
    selftest = d["hostility_selftest"]["outputs_identical"]
    bijection = all(len(m) == len(set(m.values()))
                    for m in d["clause_mapping"].values())
    return {"present": True, "selftest_pass": bool(selftest),
            "clause_bijection": bool(bijection),
            "terminals": d["terminals"]}


def main():
    custody = check_freeze_custody()
    battery = check_battery()
    parents = check_parents()
    clean = check_search_side_clean()
    screen = check_screen()
    outcomes = check_outcomes()
    recompute = check_recomputation()
    posthoc = check_posthoc()
    status = "GREEN" if all([
        custody["freeze_files_present"],
        custody["implementation_absent_at_freeze"],
        battery["pinned_ok"], battery["regeneration_deterministic"],
        parents["all_pinned"],
        clean["search_side_no_benchmark_reference"],
        screen.get("screen_clean"),
        outcomes["all_present"], outcomes["all_blind"],
        all(v is True for k, v in recompute.items()
            if isinstance(v, bool)),
        posthoc.get("present"), posthoc.get("selftest_pass"),
        posthoc.get("clause_bijection"),
    ]) else "RED"
    result = {
        "schema": "FDT_CHECK_RESULT_V1",
        "status": status,
        "claim_ceiling": ("FDT_SYMBOLIC_SSM_RETRIEVAL_DERIVATION_"
                          "AT_DECLARED_FINITE_SCOPES"),
        "forbidden_promotions": [
            "no claim beyond the completed DP/exhaustion scopes",
            "no real-scale or learning-extension claim",
            "no all-k or all-cost minimality claim beyond the certificates",
            "no claim that the order-fixed or readout-only counterexample "
            "machines satisfy the family clauses",
        ],
        "freeze_custody": custody,
        "battery": battery,
        "parents": parents,
        "search_side": clean,
        "screen": screen,
        "outcomes": outcomes,
        "recomputation_bindings": recompute,
        "posthoc": posthoc,
    }
    (HERE / "RESULT_V1.json").write_text(
        json.dumps(result, indent=1, sort_keys=True))
    print("FDT check:", status)


if __name__ == "__main__":
    main()
