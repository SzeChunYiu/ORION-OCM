#!/usr/bin/env python3
"""Tests for `gmi-833-ab-residual-definitions-v1` (issue #833, AB08 + AB25).

Runnable as `python3 -I -B  test_residual_definitions_v1.py`
       and  `python3 -I -O -B test_residual_definitions_v1.py`.
Nothing load-bearing is expressed with `assert`.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import residual_definitions_v1 as A            # noqa: E402
import independent_definitions_oracle_v1 as B  # noqa: E402

FAILURES = []
RUN = []


def check(name, cond, detail=""):
    RUN.append(name)
    if not cond:
        FAILURES.append("%s :: %s" % (name, detail))


def test_freeze_governs():
    freeze = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
    check("freeze_quotes_ab08", A.AB08_ROW in freeze, "")
    check("freeze_quotes_ab25", A.AB25_ROW in freeze, "")
    check("freeze_quotes_the_antecedent", A.AB25_ANTECEDENT in freeze,
          "the AB25 antecedent must be declared in the freeze, not chosen later")
    check("freeze_no_neighbour", "No neighboring row is earned here." in freeze, "")
    check("freeze_pins_source_main",
          "5e57d4292266bccf435136e1f7d72caa32e920a0" in freeze, "")
    for forbidden in ("GMI_IS_NOVEL_WRT_RICE", "RICE_SUBSUMED", "LADDER_APPLIED",
                      "CLAIM_IS_AT_LEVEL_N", "CITATIONS_VERIFIED"):
        check("freeze_forbids_%s" % forbidden, forbidden in freeze, "")
    # Route B recovers the same three strings from the freeze independently.
    ab08, ab25, ante = B.rows_from_freeze()
    check("routes_share_no_row_constant",
          (ab08, ab25, ante) == (A.AB08_ROW, A.AB25_ROW, A.AB25_ANTECEDENT),
          "route B recovered different row text")


def test_anti_invention_guard():
    guard = A.anti_invention_guard()
    check("guard_passed", guard["passed"],
          json.dumps([c for c in guard["detail"] if not c["occurs"]]))
    check("guard_size", guard["checked"] == 5 + 6 + 6 + 1, str(guard["checked"]))
    # The AB25 exception must stay exactly as declared: the levels are NOT in
    # AB25's own text, which is why the antecedent was declared in advance. If
    # they ever were, the exception would be unnecessary and must be removed.
    for level in A.ab25_levels():
        check("level_absent_from_ab25_itself_%s" % level.replace(" ", "_"),
              level not in A.AB25_ROW, "")
        check("level_present_in_antecedent_%s" % level.replace(" ", "_"),
              level in A.AB25_ANTECEDENT, "")
    for comp in A.ab08_components():
        check("component_in_ab08_itself_%s" % comp.replace(" ", "_"),
              comp in A.AB08_ROW, "AB08 needs no antecedent exception")


def test_route_b_is_independent():
    src = (HERE / "independent_definitions_oracle_v1.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    check("oracle_does_not_import_route_a",
          not any("residual_definitions" in m for m in imported), str(imported))
    check("oracle_uses_no_regex", "re" not in imported, str(imported))


def test_routes_agree():
    a = A.main()
    b = B.derive()
    r = a["AB08_rice_subtraction"]
    l = a["AB25_novelty_ladder"]
    pairs = [
        ("ab08 components", r["row_component_count"], len(b["ab08_row_components"])),
        ("ab08 sections", r["sections_found"], b["ab08_sections"]),
        ("ab08 present", r["components_present"], b["ab08_present"]),
        ("ab08 complete", r["components_complete"], b["ab08_complete"]),
        ("ab25 levels", l["row_level_count"], len(b["ab25_row_levels"])),
        ("ab25 found", l["levels_found"], b["ab25_levels_found"]),
        ("ab25 complete", l["levels_complete"], b["ab25_complete"]),
        ("ab25 witness", l["levels_naming_a_witness"], b["ab25_naming_a_witness"]),
        ("ab25 down", l["levels_found"], b["ab25_demotions_pointing_down"]),
    ]
    for label, x, y in pairs:
        check("agree_%s" % label.replace(" ", "_"), x == y, "A=%s B=%s" % (x, y))
    check("agree_verdicts", r["verdict_counts"] == b["ab08_verdicts"],
          "A=%s B=%s" % (r["verdict_counts"], b["ab08_verdicts"]))
    check("agree_component_lists",
          r["row_components"] == b["ab08_row_components"], "")
    check("agree_level_lists", l["row_levels"] == b["ab25_row_levels"], "")
    check("agree_level_zero",
          l["declares_level_zero"] == b["ab25_declares_level_zero"], "")
    check("agree_distinct_criteria",
          l["criteria_pairwise_distinct"] == b["ab25_criteria_pairwise_distinct"], "")
    return a, b


def test_ab08(a):
    r = a["AB08_rice_subtraction"]
    check("ab08_five_components", r["row_component_count"] == 5, str(r))
    check("ab08_all_present", r["components_present"] == 5, str(r))
    check("ab08_all_complete", r["components_complete"] == 5, str(r))
    check("ab08_verdicts_total_five", sum(r["verdict_counts"].values()) == 5,
          json.dumps(r["verdict_counts"]))
    check("ab08_declares_what_is_not_claimed",
          r["declares_what_is_not_claimed_novel"], "")
    check("ab08_cites_rice_doi", r["cites_rice_doi"], "")
    # A subtraction that absorbed nothing would be a novelty claim in disguise.
    check("ab08_absorbs_something", r["verdict_counts"]["ABSORBED"] > 0,
          json.dumps(r["verdict_counts"]))


def test_ab25(a):
    l = a["AB25_novelty_ladder"]
    check("ab25_six_levels", l["row_level_count"] == 6, str(l["row_level_count"]))
    check("ab25_all_found", l["levels_found"] == 6, str(l["levels_found"]))
    check("ab25_order_matches", l["order_matches_the_antecedent_row"], "")
    check("ab25_all_complete", l["levels_complete"] == 6, str(l["levels_complete"]))
    check("ab25_all_name_a_witness", l["levels_naming_a_witness"] == 6,
          str(l["levels_naming_a_witness"]))
    check("ab25_demotions_point_down", l["all_demotions_point_down"], "")
    check("ab25_chain_terminates", l["demotion_chain_terminates_at_zero"], "")
    check("ab25_criteria_distinct", l["criteria_pairwise_distinct"], "")
    check("ab25_level_zero_declared", l["declares_level_zero"], "")
    check("ab25_places_no_claim", l["declares_no_claim_is_placed"], "")


def test_citation_firewall():
    for name in ("RICE_PARENT_SUBTRACTION_V1.md", "NOVELTY_LADDER_V1.md"):
        text = (HERE / name).read_text(encoding="utf-8")
        check("%s_marks_cite_tf" % name, "CITE-TF" in text,
              "%s must disclose that its citations are unverified" % name)
        check("%s_disclaims_ac05" % name, "AC05 is not earned" in text, "")


def test_hostiles_and_null(a):
    for h in a["hostiles"]:
        check("hostile_detected_%s" % h["name"], bool(h["detected"]), json.dumps(h))
        check("hostile_moved_%s" % h["name"], h["before"] != h["after"], json.dumps(h))
    check("hostile_count", a["hostiles_total"] >= 6, str(a["hostiles_total"]))
    n = a["null"]
    check("null_trials", n["trials"] == 200, str(n["trials"]))
    check("null_never_full", n["random_bindings_fully_matching"] == 0, json.dumps(n))
    check("null_non_vacuous", n["max_random_matches"] > 0, json.dumps(n))
    check("null_true_total", n["true_binding_matches"] == n["bindings"], json.dumps(n))


def test_no_float(a):
    def walk(node, path="$"):
        if isinstance(node, float):
            FAILURES.append("float_in_receipt :: %s" % path)
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, path + "." + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + "[%d]" % i)
    RUN.append("no_float_in_receipt")
    walk(a)


def test_receipt_matches(a):
    path = HERE / "RESULT_V1.json"
    if not path.exists():
        RUN.append("receipt_present")
        FAILURES.append("receipt_present :: RESULT_V1.json missing")
        return
    stored = json.loads(path.read_text(encoding="utf-8"))
    for key in ("AB08_rice_subtraction", "AB25_novelty_ladder", "guard", "null",
                "hostiles"):
        check("receipt_%s" % key, stored[key] == a[key], "%s drifted" % key)


def main():
    test_freeze_governs()
    test_anti_invention_guard()
    test_route_b_is_independent()
    a, b = test_routes_agree()
    test_ab08(a)
    test_ab25(a)
    test_citation_firewall()
    test_hostiles_and_null(a)
    test_no_float(a)
    test_receipt_matches(a)
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
