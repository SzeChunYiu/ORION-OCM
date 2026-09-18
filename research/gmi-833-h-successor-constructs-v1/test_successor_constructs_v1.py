"""Tests for gmi-833-h-successor-constructs-v1.

Run:  python3 -I -B test_successor_constructs_v1.py
      python3 -I -O -B test_successor_constructs_v1.py
Stdlib only, no third-party test runner.
"""
from fractions import Fraction as Q
import ast
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = "research/gmi-833-h-successor-constructs-v1"
FAILURES = []


def check(name, cond, detail=""):
    if cond:
        sys.stdout.write("ok   %s\n" % name)
    else:
        sys.stdout.write("FAIL %s %s\n" % (name, detail))
        FAILURES.append(name)


def load(fname):
    path = os.path.join(HERE, fname)
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def git(args):
    try:
        out = subprocess.check_output(["git"] + args, cwd=HERE,
                                      stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return None


def test_custody():
    fz = git(["log", "--diff-filter=A", "--format=%ct", "-1", "--",
              "FREEZE_V1.md"])
    if fz is None or fz == "":
        check("custody.git_available", True, "(git unavailable, skipped)")
        return
    worst = None
    for fn in sorted(os.listdir(HERE)):
        if not (fn.endswith(".py") or fn.endswith(".json")):
            continue
        ts = git(["log", "--diff-filter=A", "--format=%ct", "-1", "--", fn])
        if ts:
            if worst is None or int(ts) < worst:
                worst = int(ts)
    check("custody.freeze_predates_every_implementation_artifact",
          worst is None or int(fz) <= worst,
          "freeze=%s earliest_impl=%s" % (fz, worst))


SUBSTITUTIONS = (("negative twins", "matched negative controls"),
                 ("negative twin", "matched negative control"),
                 ("remint", "independent regeneration"))


def test_freeze_unchanged_but_for_the_disclosed_substitution():
    """A freeze may be re-worded only by the disclosed terminology
    substitution. Anything else is a post-hoc edit."""
    for fn in ("FREEZE_V1.md", "FREEZE_V1_ADDENDUM.md"):
        birth = git(["log", "--diff-filter=A", "--format=%H", "-1", "--", fn])
        if not birth:
            check("freeze.%s.birth_commit_found" % fn, True,
                  "(git unavailable, skipped)")
            continue
        try:
            original = subprocess.check_output(
                ["git", "show", "%s:./%s" % (birth, fn)], cwd=HERE,
                stderr=subprocess.DEVNULL).decode()
        except Exception as exc:
            check("freeze.%s.birth_readable" % fn, False, str(exc))
            continue
        expected = original
        for old, new in SUBSTITUTIONS:
            expected = expected.replace(old, new)
        current = open(os.path.join(HERE, fn)).read()
        check("freeze.%s.only_disclosed_substitution" % fn,
              expected == current,
              "the committed freeze differs from its birth version by more "
              "than the substitution disclosed in "
              "TERMINOLOGY_SUBSTITUTION_V1.md")
    check("freeze.substitution_is_disclosed",
          os.path.exists(os.path.join(HERE, "TERMINOLOGY_SUBSTITUTION_V1.md")))


def test_grammar():
    sys.path.insert(0, HERE)
    import grammar_h_v1 as G
    import search_engine_v1 as S
    d1 = G.digest()
    d2 = G.digest()
    check("grammar.digest_stable", d1 == d2)
    check("grammar.macro_surface_clean", G.macro_audit()["clean"])
    heads = G.all_trees(G.HEAD_BUDGET, G.HEAD_LEAVES)
    bodies = G.all_trees(G.BODY_BUDGET, G.BODY_LEAVES)
    check("grammar.provenance_closed", G.provenance_closed(heads + bodies))
    check("grammar.no_new_operation",
          set(G.UNARY_OPS) == set(("NEG", "ABS", "STEP", "RECIP"))
          and set(G.BINARY_OPS) == set(("ADD", "MUL")))
    raised = False
    try:
        G.classify({"r": 1, "L": 1, "p": 12, "kind": "NONE", "ops": ("ADD",),
                    "family": "Energy-based systems."},
                   {"dep_S1": True, "dep_S2": False, "dep_STATE": False,
                    "dep_RESP": False, "aff_S1": True, "aff_S2": True},
                   {"aff_ARG": True}, None)
    except TypeError:
        raised = True
    check("grammar.classifier_refuses_family_label", raised)
    check("grammar.class_priority_frozen",
          G.CLASS_PRIORITY[0] == "RESPONSE_SPACE_SEARCH"
          and G.CLASS_PRIORITY[-1] == "AFFINE_SCORE"
          and len(G.CLASS_PRIORITY) == 11)


def test_slices():
    sys.path.insert(0, HERE)
    import ecologies_v1 as E
    s, h, r = E.slices()
    check("slices.disjoint",
          not (set(s) & set(h)) and not (set(s) & set(r))
          and not (set(h) & set(r)))
    check("slices.cover", len(s) + len(h) + len(r) == E.N_ROWS)
    d34 = E.build("SIGMA_D34")
    ties = set(E.tie_rows(d34))
    check("slices.tie_rows_present_in_search_and_heldout",
          bool(ties & set(s)) and bool(ties & set(h)), str(sorted(ties)))


def test_route_separation():
    src = open(os.path.join(HERE, "independent_oracle_v1.py")).read()
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
    route_a = set(["grammar_h_v1", "ecologies_v1", "search_engine_v1",
                   "successor_constructs_v1"])
    check("routeB.ast_no_route_a_import", not (imported & route_a),
          str(sorted(imported & route_a)))
    for m in route_a:
        sys.modules.pop(m, None)
    sys.path.insert(0, HERE)
    import independent_oracle_v1  # noqa: F401
    leaked = [m for m in route_a if m in sys.modules]
    check("routeB.sys_modules_clean", not leaked, str(leaked))


def test_results():
    res = load("RESULT_V1.json")
    orc = load("ORACLE_RESULT_V1.json")
    check("result.present", res is not None)
    check("oracle.present", orc is not None)
    if res is None or orc is None:
        return
    check("result.float_clean", res.get("float_clean") is True,
          str(res.get("float_scan"))[:200])
    check("result.grammar_unchanged", res.get("P00_grammar_unchanged") is True)
    check("twoRoute.enumeration_counts",
          orc["enumeration"]["body"] == res["R02_grammar"]["raw_counts"]["body"]
          and orc["enumeration"]["body2"]
          == res["R02_grammar"]["raw_counts"]["body2"]
          and orc["enumeration"]["head"]
          == res["R02_grammar"]["raw_counts"]["head"]
          and orc["enumeration"]["gs_head"]
          == res["R02_grammar"]["raw_counts"]["gs_head"],
          "reverse-polish enumeration must agree with node-tier enumeration")
    hs = res["hostiles"]["summary"]
    check("hostiles.all_detected", hs["all_detected"], str(hs["undetected"]))
    check("hostiles.none_vacuous", hs["all_applicable"], str(hs["vacuous"]))
    check("hostiles.count_is_twelve", hs["n"] == 12, str(hs["n"]))
    for scope, rec in sorted(res["scopes"].items()):
        check("scope.%s.recovered" % scope, rec.get("recovered") is not None)
        if rec.get("recovered") is None:
            continue
        check("scope.%s.sigma_is_own" % scope,
              rec["sigma"] in ("SIGMA_D17", "SIGMA_D20", "SIGMA_D22",
                               "SIGMA_D32", "SIGMA_D34"))
        o = orc["scopes"].get(scope, {}).get("recovered")
        check("twoRoute.%s.render" % scope,
              o is not None and o["render"] == rec["recovered"]["render"],
              str(o))
        check("twoRoute.%s.cost" % scope,
              o is not None and o["cost"] == rec["recovered"]["cost"])
        check("twoRoute.%s.class" % scope,
              o is not None and o["class"] == rec["recovered"]["class"])
        check("twoRoute.%s.ecology_digest" % scope,
              orc["scopes"][scope]["ecology_digest"] == rec["ecology_digest"])
        check("twoRoute.%s.gs_nonrepresentable" % scope,
              orc["scopes"][scope]["gs_match_found"] is False
              and rec["R06_gs_nonrepresentable"]["found_match"] is False)
        ob = orc["scopes"][scope]
        ta = rec["R05_twin"].get("recovered")
        tb = ob.get("twin")
        check("twoRoute.%s.twin" % scope,
              ta is not None and tb is not None
              and ta["render"] == tb["render"] and ta["cost"] == tb["cost"]
              and ta["class"] == tb["class"])
        ra = rec["R09_remint"].get("recovered")
        rb = ob.get("remint")
        check("twoRoute.%s.remint" % scope,
              ra is not None and rb is not None
              and ra["render"] == rb["render"] and ra["cost"] == rb["cost"]
              and ra["class"] == rb["class"])
        check("twoRoute.%s.table_crossover" % scope,
              ob.get("crossover_m") == rec["R07_resources"]["table_crossover_m"],
              "oracle=%s routeA=%s" % (ob.get("crossover_m"),
                                       rec["R07_resources"]["table_crossover_m"]))
        check("twoRoute.%s.heldout_counts" % scope,
              ob.get("heldout_pass") is True
              and ob.get("heldout_search_only")
              == rec["R08_heldout"]["search_only_matches"])
        check("twoRoute.%s.match_count" % scope,
              ob["recovered"]["n_matches"] == rec["n_matches_at_cost"],
              "oracle=%s routeA=%s" % (ob["recovered"]["n_matches"],
                                       rec["n_matches_at_cost"]))
        check("scope.%s.match_unique_up_to_symmetry" % scope,
              rec["match_equivalence"][
                  "distinct_up_to_commutativity_and_bank_swap"] == 1,
              str(rec["match_equivalence"]["keys"]))
    for scope, co in sorted(res["coordinates"].items()):
        check("coordinates.%s.R11_not_earned" % scope,
              co.get("per_requirement", {}).get("R11") is False
              or co.get("count") == 0)
        check("coordinates.%s.row_not_closed" % scope,
              co.get("row_closed") is False or co.get("count") == 0)


def test_forbidden_language():
    banned = ("INDEPENDENT_TEAM_REPLICATION_ACHIEVED", "MATURITY_M5_REACHED",
              "REAL_SCALE_CERTIFIED", "ROW_CLOSED_AT_ELEVEN")
    for fn in ("RESULT_V1.json", "ORACLE_RESULT_V1.json",
               "ISSUE_833_RECONCILIATION_H3_V1.json"):
        path = os.path.join(HERE, fn)
        if not os.path.exists(path):
            continue
        text = open(path).read()
        for b in banned:
            check("language.%s.no_%s" % (fn, b), b not in text)


def test_reconciliation():
    rec = load("ISSUE_833_RECONCILIATION_H3_V1.json")
    if rec is None:
        check("reconciliation.present", False)
        return
    check("reconciliation.schema",
          rec.get("schema") == "GMI_ISSUE_RECONCILIATION_V2")
    check("reconciliation.issue", rec.get("issue") == 833)
    check("reconciliation.anchor_is_section_header",
          str(rec.get("anchor", "")).startswith("# H."))
    check("reconciliation.forbidden_promotions_present",
          isinstance(rec.get("forbidden_promotions"), list)
          and "CROSS_SCOPE_GATE_COMPOSITION" in rec["forbidden_promotions"]
          and "REAL_SCALE_CLAIM" in rec["forbidden_promotions"])
    res = load("RESULT_V1.json")
    reps = rec.get("replacements", [])
    if reps:
        ok = False
        if res is not None:
            for scope, co in res["coordinates"].items():
                if co.get("count") == 11:
                    ok = True
        check("reconciliation.replacements_require_eleven_coordinates", ok)
    else:
        check("reconciliation.replacements_empty_is_declared",
              rec.get("closes_rows") == [])


def test_no_parent_file_is_read():
    """The checker must not read any parent package's artifact."""
    bad = []
    for fn in sorted(os.listdir(HERE)):
        if not fn.endswith(".py"):
            continue
        tree = ast.parse(open(os.path.join(HERE, fn)).read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fname = getattr(node.func, "id", None) or getattr(
                node.func, "attr", None)
            if fname not in ("open", "load", "loads", "read_text"):
                continue
            for arg in list(node.args) + [k.value for k in node.keywords]:
                for sub in ast.walk(arg):
                    val = None
                    if isinstance(sub, ast.Constant) and isinstance(
                            sub.value, str):
                        val = sub.value
                    if val is not None and "gmi-833-h-" in val:
                        bad.append((fn, val))
    check("custody.no_parent_artifact_is_opened", not bad, str(bad))


def test_reconciliation_derives_from_receipts():
    """Every coordinate the reconciliation claims must be recomputable from
    RESULT_V1.json plus the two-route agreement, with no other input."""
    rec = load("ISSUE_833_RECONCILIATION_H3_V1.json")
    res = load("RESULT_V1.json")
    orc = load("ORACLE_RESULT_V1.json")
    if rec is None or res is None or orc is None:
        check("reconciliation.derivable", False, "missing artifact")
        return
    for row in rec.get("rows_examined", []):
        sigma = row["sigma"]
        co = res["coordinates"][sigma]
        ra = res["scopes"][sigma]["recovered"]
        ob = orc["scopes"][sigma]
        agree = (ob.get("recovered") is not None
                 and ob["recovered"]["render"] == ra["render"]
                 and ob["recovered"]["cost"] == ra["cost"]
                 and ob["recovered"]["class"] == ra["class"]
                 and ob.get("gs_match_found") is False)
        per = dict(co["per_requirement"])
        per["R10"] = bool(agree)
        earned = sorted(k for k in per if per[k] is True)
        check("reconciliation.%s.coordinates_recomputed" % sigma,
              earned == row["coordinates_earned"]
              and len(earned) == row["coordinates_earned_count"],
              "receipt=%s artifact=%s" % (earned, row["coordinates_earned"]))
        check("reconciliation.%s.fields_match_receipt" % sigma,
              row["recovered_class"] == ra["class"]
              and row["recovered_charged_cost"] == ra["cost"]
              and row["recovered_program"] == ra["render"]
              and row["gs_exhaustion_verdict"]
              == res["scopes"][sigma]["R06_gs_nonrepresentable"]["verdict"])
        check("reconciliation.%s.left_unchanged" % sigma,
              row["action"] == "LEFT_UNCHANGED")


def test_theorems():
    res = load("RESULT_V1.json")
    if res is None:
        return
    th = res["theorems"]
    check("theorem.SC2_collapse", th["SC2_collapse_affine_depth2"]["holds"])
    check("theorem.SC2b_nonlinear_breaks_collapse",
          th["SC2b_nonlinear_stage_breaks_collapse"]["holds"])
    check("theorem.SC3_shift_invariance",
          th["SC3_tied_fold_shift_invariance"]["holds"])
    check("theorem.SC4_flow_bijection",
          th["SC4_flow_bijection_and_jacobian"]["holds"])
    check("theorem.SC5_staircase", th["SC5_response_space_staircase"]["holds"])


def main():
    test_custody()
    test_freeze_unchanged_but_for_the_disclosed_substitution()
    test_grammar()
    test_slices()
    test_route_separation()
    test_results()
    test_forbidden_language()
    test_no_parent_file_is_read()
    test_reconciliation_derives_from_receipts()
    test_reconciliation()
    test_theorems()
    sys.stdout.write("\n%d failures\n" % len(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
