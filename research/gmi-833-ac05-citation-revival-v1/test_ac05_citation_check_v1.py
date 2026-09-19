#!/usr/bin/env python3
"""Tests for gmi-833-ac05-citation-revival-v1. Stdlib only, no network.

    python3 -I -B research/gmi-833-ac05-citation-revival-v1/test_ac05_citation_check_v1.py
    python3 -I -O -B research/gmi-833-ac05-citation-revival-v1/test_ac05_citation_check_v1.py

Asserts (never via `assert`, so -O cannot silence them):
  * the freeze quotes the AC05 row byte-exactly and names the eight rows;
  * route A and route B agree on n/48, the failing set, the Harel verdict,
    and every row's identifier set;
  * 48/48 rows pass the four clauses;
  * every hostile is applicable AND detected; the null's primary deletions
    are all caught (0 missed) and the true result beats the null;
  * the register has one primary anchor per row, every passage <= 15 words,
    every primary resolution status in the accepted set, and no float;
  * the addendum's eight rows now carry an in-place identifier;
  * RESULT_V1.json matches the live two-route run.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FAILURES = []
RUN = []


def check(name, cond, detail=""):
    RUN.append(name)
    if not cond:
        FAILURES.append("%s :: %s" % (name, detail))


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


A = load("ac05_citation_check_v1")
B = load("independent_ac05_oracle_v1")
EIGHT = [16, 19, 21, 23, 34, 41, 47, 48]
AC05_ROW = "- [ ] Maintain citation-backed definitions rather than model-generated definitions."


def test_freeze():
    fz = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
    check("freeze_quotes_ac05_row", AC05_ROW in fz, "row text missing")
    check("freeze_names_eight_rows", all(("%d" % n) in fz for n in EIGHT), "")
    check("freeze_no_neighbor", "No neighboring row is earned here" in fz, "")
    check("freeze_rule_15_words", "15 words" in fz, "")


def test_route_b_independent():
    src = (HERE / "independent_ac05_oracle_v1.py").read_text(encoding="utf-8")
    imports = [l for l in src.splitlines() if l.startswith(("import ", "from "))]
    check("oracle_does_not_import_route_a", not any("ac05_citation_check_v1" in l for l in imports), str(imports))
    check("oracle_imports_stdlib_only", all(l.split()[1].split(".")[0] in ("json", "re", "pathlib", "__future__") for l in imports), str(imports))


def test_routes_agree(a, b):
    check("routes_rows_48", a["crosswalk_rows"] == 48 and b["rows"] == 48, "%s %s" % (a["crosswalk_rows"], b["rows"]))
    check("routes_passing_equal", a["passing_rows"] == b["passing"], "%s vs %s" % (a["passing_rows"], b["passing"]))
    check("routes_failing_equal", a["failing_rows"] == b["failing_rows"], "%s vs %s" % (a["failing_rows"], b["failing_rows"]))
    check("routes_harel_equal", a["harel_row1"]["ok"] == b["harel_ok"], "")
    pa = {p["row"]: p for p in a["per_row"]}
    bad = [n for n in range(1, 49)
           if pa[n]["identifiers_in_cell"] != b["per_row"][str(n)]["identifiers"]
           or pa[n]["passes"] != b["per_row"][str(n)]["passes"]]
    check("routes_per_row_identifier_sets_equal", not bad, "rows %s" % bad)


def test_closure(a):
    check("ac05_48_of_48", a["passing_rows"] == 48 and a["failing_rows"] == [], json.dumps(a["failing_rows"]))
    check("harel_venue_fixed", a["harel_row1"]["ok"] is True, json.dumps(a["harel_row1"]))
    pa = {p["row"]: p for p in a["per_row"]}
    for n in EIGHT:
        check("row_%d_in_place" % n, pa[n]["c4_in_place"] and pa[n]["c1_identifier"], json.dumps(pa[n]))


def test_hostiles_and_null(a):
    check("hostile_count_7", len(a["hostiles"]) == 7, str(len(a["hostiles"])))
    for h in a["hostiles"]:
        check("hostile_applicable_%s" % h["name"], h["applicable"] is True, json.dumps(h))
        check("hostile_detected_%s" % h["name"], h["detected"] is True, json.dumps(h))
    n = a["null"]
    check("null_200_draws", n["draws"] == 200, "")
    check("null_primary_deletions_all_caught", n["primary_deletions_missed"] == 0 and n["draws_hitting_primary"] == n["draws_reducing_count"], json.dumps(n))
    check("null_true_result_beats_null", n["base_passing"] == 48 and n["draws_hitting_primary"] > 0, json.dumps(n))


def test_register():
    reg = json.loads((HERE / "CITATION_VERIFICATION_V1.json").read_text(encoding="utf-8"))
    check("register_48_rows", len(reg["rows"]) == 48, str(len(reg["rows"])))
    for n, r in reg["rows"].items():
        prim = [x for x in r["anchors"] if x["role"] == "primary"]
        check("register_row_%s_one_primary" % n, len(prim) == 1, str(len(prim)))
        for x in r["anchors"]:
            if x.get("passage"):
                check("register_row_%s_passage_len" % n, len(x["passage"].split()) <= 15, x["passage"])
        if prim:
            p = prim[0]
            ok = p["identifier_kind"] == "internal" or p["resolution"]["http"] in (200, 301, 302, 303)
            check("register_row_%s_primary_resolved" % n, ok, json.dumps(p["resolution"]))
            check("register_row_%s_primary_has_locator" % n, bool(p.get("locator")), "")
            check("register_row_%s_primary_route_named" % n, p.get("passage_route") in
                  ("PRIMARY_TEXT", "ABSTRACT", "PUBLISHER_DESCRIPTION", "SECONDARY_QUOTATION", "TITLE"), str(p.get("passage_route")))

    def walk(node, path="$"):
        if isinstance(node, float):
            FAILURES.append("no_float_in_register :: %s" % path)
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, path + "." + k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, "%s[%d]" % (path, i))
    RUN.append("no_float_in_register")
    walk(reg)
    # the retired row-48 rescue is recorded as retired, never as primary
    r48 = reg["rows"]["48"]
    retired = [x for x in r48["anchors"] if x["role"] == "retired"]
    check("row48_hempel_retired", any("10.1086/286983" in (x.get("identifier") or "") for x in retired), "")
    check("row48_primary_internal", [x for x in r48["anchors"] if x["role"] == "primary"][0]["identifier_kind"] == "internal", "")


def test_crosswalk_only_citations_changed():
    """The tranche may change citations cells and the header note only:
    every other cell of every row must be byte-identical to the frozen blob."""
    import subprocess
    fz = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
    m = re.search(r"GMI_TERMINOLOGY_CROSSWALK_V2\.md` = `([0-9a-f]{40})`", fz)
    check("freeze_pins_crosswalk_blob", bool(m), "")
    if not m:
        return
    proc = subprocess.run(["git", "-C", str(REPO), "cat-file", "-p", m.group(1)], capture_output=True)
    if proc.returncode != 0:
        RUN.append("frozen_crosswalk_blob_reachable")
        FAILURES.append("frozen_crosswalk_blob_reachable :: UNREACHABLE (%s) - degrade, not pass" % m.group(1))
        return
    old = A.crosswalk_rows(proc.stdout.decode("utf-8"))
    new = A.crosswalk_rows()
    check("crosswalk_row_count_unchanged", len(old) == len(new) == 48, "%d %d" % (len(old), len(new)))
    changed = []
    for o, n in zip(old, new):
        for col in A.COLS:
            if col != "citations" and o[col] != n[col]:
                changed.append((o["n"], col))
    check("crosswalk_non_citation_cells_unchanged", not changed, str(changed[:5]))


def test_receipt(a, b):
    path = HERE / "RESULT_V1.json"
    if not path.exists():
        RUN.append("receipt_present")
        FAILURES.append("receipt_present :: RESULT_V1.json missing")
        return
    stored = json.loads(path.read_text(encoding="utf-8"))
    for key in ("passing_rows", "failing_rows", "harel_row1", "hostiles", "null", "register", "per_row"):
        check("receipt_%s" % key, stored.get(key) == a[key], "%s drifted" % key)
    check("receipt_route_b", stored.get("route_b") == b, "route_b drifted")


def main():
    test_freeze()
    test_route_b_independent()
    a = A.main()
    b = B.derive()
    test_routes_agree(a, b)
    test_closure(a)
    test_hostiles_and_null(a)
    test_register()
    test_crosswalk_only_citations_changed()
    test_receipt(a, b)
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
