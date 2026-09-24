#!/usr/bin/env python3
"""Tests for `gmi-833-aa-ledger-gate-v1` (issue #833, AA02-AA06).

Runnable as `python3 -I -B  test_ledger_gate_v1.py`
       and  `python3 -I -O -B test_ledger_gate_v1.py`.

Nothing load-bearing is expressed with `assert`.
"""
from __future__ import annotations

import json
import os
import subprocess
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


def test_immutable_amendment_fails_closed():
    """Issue #1049 item 2: a hash-pinned result may be carried as identified
    debt only while its pin verifiably holds; every way of breaking the pin
    must re-enforce the result. Kept out of gate_demo() so the pinned receipt
    section `gate_failure_demonstration` is unchanged."""
    import hashlib
    tmp = tempfile.mkdtemp(prefix="gmi833-amend-")
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
        note = root / "research" / "fixture-pkg" / "FIXTURE_THEOREMS_V1.md"
        note.write_text(CLEAN + NEW_BAD, encoding="utf-8")
        rel = "research/fixture-pkg/FIXTURE_THEOREMS_V1.md"
        sha = hashlib.sha256(note.read_bytes()).hexdigest()
        other = root / "research" / "other-pkg"
        other.mkdir(parents=True, exist_ok=True)
        (other / "MANIFEST_V1.json").write_text(
            json.dumps({"parent_pins": [{"path": rel, "sha256": sha}]}), encoding="utf-8")
        own_rec = root / "research" / "fixture-pkg" / "RESULT_V1.json"
        own_rec.write_text(json.dumps({"sha256": sha}), encoding="utf-8")
        result = "CLN-2 - a new result that omits two ledgers"
        amend = Path(tmp) / "amend.json"

        def run(entries_):
            amend.write_text(json.dumps({
                "schema": "GMI_833_LEDGER_BASELINE_AMENDMENT_V1",
                "entries": entries_}), encoding="utf-8")
            return A.gate(None, root, base_path, amend)

        good = {"path": rel, "result": result,
                "pinned_by": "research/other-pkg/MANIFEST_V1.json", "pin_sha256": sha}
        code, rep = run([good])
        check("amendment_valid_pin_passes", code == 0 and rep["violations"] == []
              and rep["immutable_custody_amended_results"] == 1,
              json.dumps(rep["violations"]))

        code, rep = run([])
        check("amendment_absent_fails", code != 0 and "NEW_RESULT_MISSING_LEDGER"
              in {v["kind"] for v in rep["violations"]}, json.dumps(rep["violations"]))

        same_pkg = dict(good, pinned_by="research/fixture-pkg/RESULT_V1.json")
        code, rep = run([same_pkg])
        check("amendment_same_package_record_rejected", code != 0
              and rep["immutable_custody_dropped_entries"], json.dumps(rep["violations"]))

        forged = dict(good, pin_sha256="0" * 64)
        code, rep = run([forged])
        check("amendment_forged_sha_rejected", code != 0
              and rep["immutable_custody_dropped_entries"], json.dumps(rep["violations"]))

        wrong_result = dict(good, result="CLN-1 - a compliant named result")
        code, rep = run([good, wrong_result])
        check("amendment_complete_result_not_counted",
              code == 0 and rep["immutable_custody_amended_results"] == 1
              and len(rep["immutable_custody_dropped_entries"]) == 1,
              json.dumps(rep["immutable_custody_dropped_entries"]))

        # Editing the pinned note (e.g. adding one ledger) breaks the pin, so
        # the entry drops and the still-incomplete result is enforced again.
        note.write_text(CLEAN + NEW_BAD + "\n**Assumptions.** One.\n", encoding="utf-8")
        code, rep = run([good])
        check("amendment_edit_breaks_pin_and_reenforces", code != 0
              and rep["immutable_custody_dropped_entries"]
              and "NEW_RESULT_MISSING_LEDGER" in {v["kind"] for v in rep["violations"]},
              json.dumps(rep["violations"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_real_amendment_entries_all_verify():
    """Every entry of the committed amendment must verify on the live repo;
    a dropped entry means a pin moved and the amendment must be revisited."""
    c = A.census()
    valid, dropped = A.load_amendment(c)
    check("real_amendment_no_dropped_entries", dropped == [], json.dumps(dropped))
    doc = json.loads(A.AMENDMENT.read_text(encoding="utf-8"))
    check("real_amendment_every_entry_valid", len(valid) == len(doc["entries"]),
          "%d of %d" % (len(valid), len(doc["entries"])))


def _owned_paths():
    """Theorem notes this change actually added or changed, or None off-PR.

    `gate(owned=None)` enforces over the whole repository. That is right on push
    to main and wrong in a unit test: it fails this branch for theorem notes
    another lane merged. It already did -- a documentation-only PR was failed
    for five AG5 results it never touched. The gate's own code says why this
    matters: "A gate that fires on work you did not do is a gate that gets
    switched off."

    The scope rule lives in ONE place, `A.owned_paths_from_git`, and the
    workflow reads the same rule through `--print-owned`. This test used to
    compute `PR_BASE_SHA..HEAD` on its own while the workflow computed
    `origin/<base>...HEAD`; the two disagreed, and the two-dot form attributed
    every file main gained after the PR's last push to the PR (a ledger-mirror
    fix was failed for a Z2 theorem note another lane merged). The mechanism
    test below rebuilds that topology in a scratch repository and keeps the
    stale rule's wrong answer as the regression witness.
    """
    return A.owned_paths_from_git()


# ---------------------------------------------------------------------------
# The scope rule, on a scratch repository with the exact topology that failed.
# ---------------------------------------------------------------------------
GIT = "/usr/bin/git" if os.path.exists("/usr/bin/git") else "git"

NEW_NOTE_BAD = """# X theorem note

## XN-1 - a new result that omits every ledger

**Statement.** Something.
"""


def _git(repo, *args):
    env = dict(os.environ)
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x",
                "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@x",
                "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(repo)})
    proc = subprocess.run([GIT, "-C", str(repo)] + list(args),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if proc.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (args, proc.stderr.decode("utf-8", "replace")))
    return proc.stdout.decode("utf-8", "replace")


def _scratch_repo(tmp, branch_adds):
    """base --(main)--> +Y.md
         `--(branch)--> +<branch_adds>   then merge(main, branch) = HEAD.

    Returns (repo, base_sha). `base_sha` plays the part of
    `github.event.pull_request.base.sha`: the base tip when the branch was
    cut, which is STALE once main advances.
    """
    repo = Path(tmp) / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-q", "-m", "base")
    base_sha = _git(repo, "rev-parse", "HEAD").strip()
    _git(repo, "checkout", "-q", "-b", "branch")
    for rel, body in branch_adds.items():
        f = repo / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(body, encoding="utf-8")
        _git(repo, "add", rel)
    if branch_adds:
        _git(repo, "commit", "-q", "-m", "branch work")
    else:
        _git(repo, "commit", "-q", "--allow-empty", "-m", "branch work (adds nothing)")
    _git(repo, "checkout", "-q", "main")
    y = repo / "research" / "other-pkg" / "Y_THEOREMS_V1.md"
    y.parent.mkdir(parents=True, exist_ok=True)
    y.write_text(NEW_NOTE_BAD.replace("XN-1", "YN-1"), encoding="utf-8")
    _git(repo, "add", str(y.relative_to(repo)))
    _git(repo, "commit", "-q", "-m", "main advances: +Y.md")
    # GitHub's pull_request checkout: merge of the PR head into the CURRENT base.
    _git(repo, "merge", "-q", "--no-ff", "--no-edit", "branch")
    return repo, base_sha


def _empty_baseline(tmp):
    base_path = Path(tmp) / "baseline.json"
    base_path.write_text(json.dumps({
        "schema": "GMI_833_LEDGER_BASELINE_V1",
        "named_results": 0, "non_compliant_named_results": 0,
        "identified_non_compliant": 0, "entries": {},
    }), encoding="utf-8")
    return base_path


def test_owned_paths_rule():
    x_rel = "research/x-pkg/X.md"
    y_rel = "research/other-pkg/Y_THEOREMS_V1.md"
    tmp = tempfile.mkdtemp(prefix="gmi833-scope-")
    try:
        repo, base_sha = _scratch_repo(tmp, {x_rel: "# X\n\nprose only\n"})
        parents = _git(repo, "rev-list", "--parents", "-n", "1", "HEAD").split()
        check("scratch_head_is_a_merge", len(parents) == 3, str(parents))

        # (1) merge checkout: the shared rule owns exactly the branch's file.
        owned = A.owned_paths_from_git(repo, base_sha, GIT)
        check("merge_checkout_owns_branch_file_only", owned == [x_rel], str(owned))
        # The stale two-dot rule reports main's file as well: regression witness.
        stale = A.stale_two_dot_paths(repo, base_sha, GIT)
        check("stale_two_dot_rule_misattributes_mains_file",
              y_rel in stale and x_rel in stale, str(stale))
        check("shared_rule_differs_from_stale_rule", set(stale) != set(owned),
              "the witness does not witness: both rules agree")

        # (2) non-merge checkout with a base sha: merge-base(base, HEAD)..HEAD.
        _git(repo, "checkout", "-q", "branch")
        owned2 = A.owned_paths_from_git(repo, base_sha, GIT)
        check("linear_checkout_uses_merge_base", owned2 == [x_rel], str(owned2))
        # (3) no merge, no base sha: no PR scope -> repo-wide.
        owned3 = A.owned_paths_from_git(repo, "", GIT)
        check("no_scope_means_repo_wide", owned3 is None, str(owned3))
        # (4) markdown filter is applied only when asked.
        (repo / "research" / "x-pkg" / "x.py").write_text("x = 1\n", encoding="utf-8")
        _git(repo, "add", "research/x-pkg/x.py")
        _git(repo, "commit", "-q", "-m", "+py")
        with_py = A.owned_paths_from_git(repo, base_sha, GIT, only_markdown=False)
        md_only = A.owned_paths_from_git(repo, base_sha, GIT)
        check("markdown_filter_drops_non_markdown",
              "research/x-pkg/x.py" in with_py and md_only == [x_rel],
              "%s / %s" % (with_py, md_only))
        # (5) the CLI surface the workflow calls prints the same list.
        env = dict(os.environ)
        env["PR_BASE_SHA"] = base_sha
        env.pop("PYTHONPATH", None)
        proc = subprocess.run([sys.executable, "-I", "-B", str(HERE / "ledger_gate_v1.py"),
                               "--print-owned"], cwd=str(repo), env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # The CLI runs in the PACKAGE repo, not the scratch one (REPO is fixed
        # at import), so it exercises the real checkout: it must either print
        # a list (PR scope) or exit 3 (no scope) -- never crash.
        check("print_owned_cli_exit_is_0_or_3", proc.returncode in (0, 3),
              proc.stderr.decode("utf-8", "replace"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_scoped_gate_no_alarm_and_alarm():
    """The scope rule feeding the gate: a branch that adds nothing is silent
    even though main gained a non-compliant note; a branch that adds a
    non-compliant note fires."""
    tmp = tempfile.mkdtemp(prefix="gmi833-scope-gate-")
    try:
        # no-alarm: branch adds nothing, main gained a bad note.
        repo, base_sha = _scratch_repo(tmp, {})
        owned = A.owned_paths_from_git(repo, base_sha, GIT)
        check("empty_branch_owns_nothing", owned == [], str(owned))
        code, rep = A.gate(owned, repo, _empty_baseline(tmp))
        check("scoped_gate_silent_when_branch_adds_nothing",
              code == 0 and rep["violations"] == [] and rep["scope"] == "owned-files",
              json.dumps(rep["violations"]))
        # ... and the same repo enforced repo-wide DOES see main's debt, so the
        # silence above is scope, not blindness.
        code_w, rep_w = A.gate(None, repo, _empty_baseline(tmp))
        check("repo_wide_gate_sees_mains_note", code_w != 0
              and any(v["path"].endswith("Y_THEOREMS_V1.md") for v in rep_w["violations"]),
              json.dumps(rep_w["violations"]))
        shutil.rmtree(str(repo), ignore_errors=True)

        # alarm: branch adds a non-compliant theorem note.
        bad_rel = "research/x-pkg/X_THEOREMS_V1.md"
        repo, base_sha = _scratch_repo(tmp, {bad_rel: NEW_NOTE_BAD})
        owned = A.owned_paths_from_git(repo, base_sha, GIT)
        check("bad_branch_owns_its_note", owned == [bad_rel], str(owned))
        code, rep = A.gate(owned, repo, _empty_baseline(tmp))
        kinds = sorted({v["kind"] for v in rep["violations"]})
        paths = sorted({v["path"] for v in rep["violations"]})
        check("scoped_gate_fires_on_branch_note",
              code != 0 and kinds == ["NEW_RESULT_MISSING_LEDGER"] and paths == [bad_rel],
              json.dumps(rep["violations"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_is_green_on_the_real_repo():
    owned = _owned_paths()
    # gate(owned, root, baseline_path) -- owned is the FIRST parameter.
    # Passing it third put a list into baseline_path and crashed the harness
    # with "'list' object has no attribute 'exists'". The original call was
    # gate(None, None, None), which is why the position error was invisible:
    # every argument was None, so no argument was in the wrong place yet.
    code, rep = A.gate(owned)
    check("real_repo_gate_green", code == 0,
          json.dumps({"owned_scope": "PR diff" if owned is not None else "repo-wide",
                      "violations": rep["violations"][:5]}))
    check("real_repo_gate_reports_debt",
          rep["live_non_compliant"] >= rep["baseline_non_compliant"] - 0
          and rep["baseline_non_compliant"] > 0, json.dumps(
              {k: rep[k] for k in ("baseline_non_compliant", "live_non_compliant")}))
    # Non-vacuity, stated per scope. Repo-wide the scan must see new results or
    # it is inspecting nothing. PR-scoped, a branch that adds no theorem note
    # correctly yields zero, so requiring new results there would fail every
    # such branch -- the same repo-wide-assertion-in-a-per-PR-gate mistake this
    # gate has already made twice.
    if owned is None:
        check("real_repo_gate_saw_new_results", rep["new_named_results"] > 0,
              "repo-wide scan sees no new named results; it is inspecting nothing")
    else:
        check("real_repo_gate_scope_is_the_pr_diff",
              isinstance(owned, list),
              "PR scope did not resolve to a list of owned paths")
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
    # NOT a ratchet on the corpus-wide total. That number rises whenever any
    # other lane merges a package -- it went 2345 -> 2372 the moment the AG5
    # tranche landed -- so asserting on it fails every open branch for debt the
    # branch did not create, including documentation-only ones. The identical
    # defect was already found and removed from the terminology ratchet; the
    # enforcement that survives is per-file and PR-scoped (real_repo_gate_green
    # over owned paths), and the total is recorded as a measurement.
    check("receipt_debt_measured",
          isinstance(a["non_compliant_named_results"], int)
          and a["non_compliant_named_results"] >= 0,
          "non-integer debt: %r" % (a["non_compliant_named_results"],))
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
    test_immutable_amendment_fails_closed()
    test_real_amendment_entries_all_verify()
    test_owned_paths_rule()
    test_scoped_gate_no_alarm_and_alarm()
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
