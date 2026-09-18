#!/usr/bin/env python3
"""Tests for `gmi-833-aa-ledger-gate-v1` (issue #833, AA02-AA06).

Runnable as `python3 -I -B  test_ledger_gate_v1.py`
       and  `python3 -I -O -B test_ledger_gate_v1.py`.

Nothing load-bearing is expressed with `assert`.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ledger_gate_v1 as A              # noqa: E402
import independent_ledger_oracle_v1 as B  # noqa: E402

FAILURES = []
RUN = []


def check(name, cond, detail=""):
    RUN.append(name)
    if not cond:
        FAILURES.append("%s :: %s" % (name, detail))


# ---------------------------------------------------------------------------
# Anti-invention guard.
# ---------------------------------------------------------------------------
def test_every_required_label_occurs_in_its_row_text():
    guard = A.anti_invention_guard()
    check("guard_passed", guard["passed"], json.dumps(guard["per_label"]))
    check("guard_covers_nine_labels", guard["labels_checked"] == 9,
          str(guard["labels_checked"]))
    check("aa06_names_five_ledgers", guard["aa06_ledger_count"] == 5,
          str(guard["aa06_ledger_count"]))
    # The guard must be able to fail, or it is decoration.
    bad = A.normalize_row(A.ROWS["AA03"])
    check("guard_is_falsifiable", "sampling bias" not in bad,
          "a foreign label already occurs in AA03's text")


def test_rows_match_the_freeze_verbatim():
    freeze = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
    for rid, row in sorted(A.ROWS.items()):
        check("freeze_quotes_%s" % rid, row in freeze,
              "%s row text is not quoted verbatim in the freeze" % rid)
    check("freeze_no_neighbour", "No neighboring row is earned here." in freeze, "")
    check("freeze_pins_source_main",
          "5e57d4292266bccf435136e1f7d72caa32e920a0" in freeze, "")
    for forbidden in ("CORPUS_LEDGERS_COMPLETE", "LEDGER_CONTENTS_VERIFIED",
                      "ALL_THEOREMS_COMPLIANT", "ANALYTIC_PROOF"):
        check("freeze_forbids_%s" % forbidden, forbidden in freeze, "")
    check("freeze_declares_planted_positives",
          "planted positives" in freeze.lower(), "")


# ---------------------------------------------------------------------------
# Two materially independent routes.
# ---------------------------------------------------------------------------
def test_routes_agree_per_result():
    a = A.census()
    b = B.derive()
    for key in ("theorem_files", "named_results", "complete_named_results",
                "non_compliant_named_results", "unparsed_theorem_artifacts",
                "experiment_files", "experiment_complete"):
        check("agree_%s" % key, a[key] == b[key],
              "%s: A=%s B=%s" % (key, a[key], b[key]))
    check("agree_emission_by_ledger",
          a["emission_by_ledger"] == b["emission_by_ledger"],
          "A=%s B=%s" % (a["emission_by_ledger"], b["emission_by_ledger"]))
    check("agree_experiment_emission",
          a["experiment_emission_by_ledger"] == b["experiment_emission_by_ledger"],
          "A=%s B=%s" % (a["experiment_emission_by_ledger"],
                         b["experiment_emission_by_ledger"]))
    # Load-bearing: the same RESULTS, not just the same count.
    a_map = {}
    for f in a["per_file"]:
        for r in f["named_results"]:
            a_map[f["path"] + "::" + r["result"]] = bool(r["complete"])
    check("per_result_maps_identical", a_map == b["per_result"],
          "%d keys differ" % len(set(a_map.items()) ^ set(b["per_result"].items())))
    return a, b


def test_route_b_is_independent():
    import ast
    src = (HERE / "independent_ledger_oracle_v1.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    check("oracle_does_not_import_route_a",
          not any("ledger_gate" in m for m in imported), str(imported))
    check("oracle_uses_no_regex", "re" not in imported and "import re" not in src,
          "route B imports re; a shared regex bug could make both routes agree")


# ---------------------------------------------------------------------------
# The decoy class: a prose mention is not an emission.
# ---------------------------------------------------------------------------
DECOY = """# Decoy theorem note

## DEC-1 - a result that talks about ledgers without emitting any

This result depends on several assumptions and one could falsify it by
exhibiting a counterexample; its strongest parent is well known, and the
dependency on that parent is acknowledged in the prose above.
"""

SECTION_HEADING_NOTE = """# A note that uses ## for sections as well as results

## Scope

Every tracked artifact at the pinned sha.

## Claim ceiling

Something modest.

## XY-1 - a compliant named result

**Statement.** Exact.

**Assumptions.** One.

**Dependencies.** One.

**Falsifiers.** One.

**Strongest parents.** One.
"""

SECTION_HEADING_NOTE_BAD = SECTION_HEADING_NOTE.replace(
    "**Dependencies.** One.\n\n", "")

CLEAN = """# Clean theorem note

## CLN-1 - a compliant named result

**Statement.** Something exact.

**Assumptions.** One assumption.

**Dependencies.** One dependency.

**Falsifiers.** One falsifier.

**Strongest parents.** One parent.
"""

NEW_BAD = """
## CLN-2 - a new result that omits two ledgers

**Statement.** Something else.

**Falsifiers.** One falsifier.
"""


def test_decoy_is_rejected():
    results = A.named_results(DECOY)
    check("decoy_has_one_result", len(results) == 1, str(len(results)))
    emits = {}
    for key, _, accepted in A.THEOREM_LEDGERS:
        emits[key] = any(x in A.emitted_labels(results[0][1]) for x in accepted)
    check("decoy_emits_nothing", not any(emits.values()), str(emits))
    # Route B must reject it too, by its own parser.
    b_scan = B.scan_theorem_file(DECOY)
    check("decoy_rejected_by_route_b",
          len(b_scan) == 1 and not any(b_scan[0][1].values()), str(b_scan))


# ---------------------------------------------------------------------------
# The gate can actually fail. This is the check the predecessor gate lacked.
# ---------------------------------------------------------------------------
def _fixture(tmp, body):
    root = Path(tmp)
    pkg = root / "research" / "fixture-pkg"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "FIXTURE_THEOREMS_V1.md").write_text(body, encoding="utf-8")
    return root


def gate_demo():
    out = {}
    tmp = tempfile.mkdtemp(prefix="gmi833-ledger-")
    try:
        root = _fixture(tmp, CLEAN)
        base_path = Path(tmp) / "baseline.json"
        c = A.census(root)
        entries = {}
        for f in c["per_file"]:
            for r in f["named_results"]:
                entries[A.baseline_key(f["path"], r["result"])] = bool(r["complete"])
        base_path.write_text(json.dumps({
            "schema": "GMI_833_LEDGER_BASELINE_V1",
            "named_results": c["named_results"],
            "non_compliant_named_results": c["non_compliant_named_results"],
            "identified_non_compliant": c["identified_non_compliant"],
            "entries": entries,
        }), encoding="utf-8")

        code, rep = A.gate(None, root, base_path)
        out["clean"] = {"exit": code, "violations": len(rep["violations"])}

        # (2) a NEW non-compliant result appears
        p = root / "research" / "fixture-pkg" / "FIXTURE_THEOREMS_V1.md"
        p.write_text(CLEAN + NEW_BAD, encoding="utf-8")
        code, rep = A.gate(None, root, base_path)
        out["new_bad"] = {"exit": code, "violations": len(rep["violations"]),
                          "kinds": sorted({v["kind"] for v in rep["violations"]})}

        # (3) an existing compliant result REGRESSES
        p.write_text(CLEAN.replace("**Dependencies.** One dependency.\n\n", ""),
                     encoding="utf-8")
        code, rep = A.gate(None, root, base_path)
        out["regression"] = {"exit": code, "violations": len(rep["violations"]),
                             "kinds": sorted({v["kind"] for v in rep["violations"]})}

        # (4) the prose decoy must not pass as compliant
        p.write_text(CLEAN + "\n" + DECOY.split("\n", 1)[1], encoding="utf-8")
        code, rep = A.gate(None, root, base_path)
        out["decoy"] = {"exit": code, "violations": len(rep["violations"]),
                        "kinds": sorted({v["kind"] for v in rep["violations"]})}

        # (5) a new note that uses `##` for SECTION headings as well as for its
        # one compliant named result must PASS: section headings are measured
        # but not enforced. This is the false-positive class that would
        # otherwise fail every other lane's theorem note.
        q = root / "research" / "fixture-pkg" / "OTHER_THEOREMS_V1.md"
        p.write_text(CLEAN, encoding="utf-8")
        q.write_text(SECTION_HEADING_NOTE, encoding="utf-8")
        code, rep = A.gate(None, root, base_path)
        out["section_headings_pass"] = {
            "exit": code, "violations": len(rep["violations"]),
            "outside_enforcement": rep["new_headings_outside_enforcement_scope"]}

        # (6) ... and the same note with its NAMED RESULT non-compliant fails.
        q.write_text(SECTION_HEADING_NOTE_BAD, encoding="utf-8")
        code, rep = A.gate(None, root, base_path)
        out["section_headings_bad_result_fails"] = {
            "exit": code, "violations": len(rep["violations"]),
            "kinds": sorted({v["kind"] for v in rep["violations"]})}
        q.unlink()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return out


def test_gate_can_fail():
    demo = gate_demo()
    check("gate_passes_clean", demo["clean"]["exit"] == 0
          and demo["clean"]["violations"] == 0, json.dumps(demo["clean"]))
    for case in ("new_bad", "regression", "decoy"):
        check("gate_fails_%s" % case, demo[case]["exit"] != 0
              and demo[case]["violations"] > 0, json.dumps(demo[case]))
    check("gate_names_new_result_violation",
          "NEW_RESULT_MISSING_LEDGER" in demo["new_bad"]["kinds"],
          json.dumps(demo["new_bad"]))
    check("gate_names_regression_violation",
          "COMPLIANT_RESULT_REGRESSED" in demo["regression"]["kinds"],
          json.dumps(demo["regression"]))
    # The false-positive class: section headings are measured, never enforced.
    sp = demo["section_headings_pass"]
    check("gate_does_not_fire_on_section_headings",
          sp["exit"] == 0 and sp["violations"] == 0, json.dumps(sp))
    check("section_headings_were_actually_seen",
          sp["outside_enforcement"] >= 2, json.dumps(sp))
    sb = demo["section_headings_bad_result_fails"]
    check("gate_still_fires_on_the_named_result_in_that_note",
          sb["exit"] != 0 and "NEW_RESULT_MISSING_LEDGER" in sb["kinds"],
          json.dumps(sb))
    return demo


def test_gate_is_green_on_the_real_repo():
    code, rep = A.gate(None, None, None)
    check("real_repo_gate_green", code == 0,
          json.dumps(rep["violations"][:5]))
    check("real_repo_gate_reports_debt",
          rep["live_non_compliant"] >= rep["baseline_non_compliant"] - 0
          and rep["baseline_non_compliant"] > 0, json.dumps(
              {k: rep[k] for k in ("baseline_non_compliant", "live_non_compliant")}))
    check("real_repo_gate_saw_new_results", rep["new_named_results"] > 0,
          "the tranche's own theorem notes are not being seen as new")
    return rep


# ---------------------------------------------------------------------------
# Planted positives and the baseline.
# ---------------------------------------------------------------------------
def test_planted_positives_are_detected(a):
    per = {f["path"]: f for f in a["per_file"]}
    planted = [p for p in per
               if p.startswith("research/gmi-833-aa-finite-universal-harness-v1/")
               or p.startswith("research/gmi-833-aa-ledger-gate-v1/")]
    check("planted_theorem_files_present", len(planted) >= 1, str(planted))
    total = 0
    complete = 0
    for p in planted:
        total += per[p]["count"]
        complete += per[p]["complete"]
    check("planted_recall_total", total > 0 and complete == total,
          "%d/%d planted results complete" % (complete, total))

    exp = a["per_experiment"]
    check("experiment_ledgers_planted", len(exp) >= 2, str(len(exp)))
    check("experiment_ledger_recall",
          all(f["complete"] for f in exp),
          json.dumps([{"p": f["path"], "e": f["emits"]} for f in exp]))
    return total, complete, len(exp)


def test_baseline_is_a_picture_of_main():
    base = json.loads((HERE / "LEDGER_BASELINE_V1.json").read_text(encoding="utf-8"))
    check("baseline_pins_source_main",
          base["source_main"] == "5e57d4292266bccf435136e1f7d72caa32e920a0", "")
    check("baseline_excludes_this_tranche",
          len(base["excluded_prefixes"]) == 4, str(base["excluded_prefixes"]))
    for pref in base["excluded_prefixes"]:
        check("baseline_has_no_entry_under_%s" % pref.split("/")[1],
              not any(k.startswith(pref) for k in base["entries"]), pref)
    check("baseline_dependency_ledger_absent",
          base["emission_by_ledger"]["dependency"] == 0,
          "the batching plan's claim that two notes on main emit all four "
          "ledgers no longer reproduces: %s" % base["emission_by_ledger"])
    check("baseline_zero_complete", base["complete_named_results"] == 0,
          str(base["complete_named_results"]))
    return base


def test_null_and_no_float(a):
    guard = A.anti_invention_guard()
    null = A.row_binding_null()
    check("null_trials", null["trials"] == 200, str(null["trials"]))
    check("null_never_fully_satisfied", null["random_bindings_fully_satisfied"] == 0,
          json.dumps(null))
    check("null_non_vacuous", null["max_random_satisfied"] > 0, json.dumps(null))
    check("true_binding_total", null["true_binding_satisfied"] == guard["labels_checked"],
          "")

    def walk(node, path="$"):
        if isinstance(node, float):
            FAILURES.append("float_in_receipt :: %s" % path)
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, path + "." + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + "[%d]" % i)
    RUN.append("no_float_in_census")
    walk({k: v for k, v in a.items() if k not in ("per_file", "per_experiment")})
    return null


def test_receipt_matches(a, base):
    path = HERE / "RESULT_V1.json"
    if not path.exists():
        RUN.append("receipt_present")
        FAILURES.append("receipt_present :: RESULT_V1.json missing")
        return
    stored = json.loads(path.read_text(encoding="utf-8"))
    # The live corpus is a shared surface other lanes extend, so the receipt
    # binds it by non-vacuous inequality, not by equality. The baseline below
    # is pinned and IS bound by equality.
    for key in ("theorem_files", "named_results", "complete_named_results",
                "experiment_files"):
        check("receipt_live_%s_not_below" % key, a[key] >= stored["live_census"][key],
              "%s: receipt %s live %s" % (key, stored["live_census"][key], a[key]))
    check("receipt_debt_never_grew",
          a["non_compliant_named_results"] <= stored["baseline"]["non_compliant_named_results"],
          "%s > %s" % (a["non_compliant_named_results"],
                       stored["baseline"]["non_compliant_named_results"]))
    for key in ("named_results", "non_compliant_named_results",
                "complete_named_results", "theorem_files"):
        check("receipt_baseline_%s" % key, stored["baseline"][key] == base[key],
              "%s: receipt %s baseline %s" % (key, stored["baseline"][key], base[key]))


def main():
    test_every_required_label_occurs_in_its_row_text()
    test_rows_match_the_freeze_verbatim()
    test_route_b_is_independent()
    a, b = test_routes_agree_per_result()
    test_decoy_is_rejected()
    test_gate_can_fail()
    test_gate_is_green_on_the_real_repo()
    test_planted_positives_are_detected(a)
    base = test_baseline_is_a_picture_of_main()
    test_null_and_no_float(a)
    test_receipt_matches(a, base)

    print("checks run: %d" % len(RUN))
    if FAILURES:
        print("FAILURES (%d):" % len(FAILURES))
        for f in FAILURES:
            print("  - %s" % f)
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
