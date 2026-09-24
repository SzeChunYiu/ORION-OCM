#!/usr/bin/env python3
"""Route A - ledger emission census and ratcheting gate (issue #833, AA02-AA06).

The four theorem-side ledgers (assumptions / dependency / falsifier /
strongest-parent) and the five experiment-side ledgers (leakage / search space /
cost model / evaluation / sampling bias) are made machine-checkable here, the
corpus state is measured exactly, and a ratchet stops the debt growing.

Usage:
  ledger_gate_v1.py                      census over the whole corpus (JSON)
  ledger_gate_v1.py --gate               ratchet against LEDGER_BASELINE_V1.json
  ledger_gate_v1.py --gate --owned-files FILE
                                         ratchet, restricted to the paths in FILE
  ledger_gate_v1.py --write-baseline     freeze the current state as the baseline
  ledger_gate_v1.py --scan-root DIR      scan DIR instead of the repo (fixtures)
  ledger_gate_v1.py --print-owned        the PR-owned markdown paths (shared scope rule)

stdlib only; exact integer arithmetic; python3.8-compatible.

Span extraction (route A) walks the file once, cutting it at level-2 ATX
headings and collecting block-leading bold labels per span.  Route B
(`independent_ledger_oracle_v1.py`) uses a line state machine and shares no
code with this module; they are compared by set equality per named result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BASELINE = HERE / "LEDGER_BASELINE_V1.json"

# ---------------------------------------------------------------------------
# The emission predicate, declared in FREEZE_V1.md section 5 before it was run.
# ---------------------------------------------------------------------------
THEOREM_ARTIFACT = re.compile(r"THEOREM", re.IGNORECASE)
EXPERIMENT_ARTIFACT = re.compile(r"EXPERIMENT.*LEDGER", re.IGNORECASE)
EXPERIMENT_SCHEMA = "GMI_EXPERIMENT_LEDGER_V1"

THEOREM_LEDGERS = (
    ("assumptions", "AA02", ("assumptions", "assumption")),
    ("dependency", "AA03", ("dependencies", "dependency", "depends on")),
    ("falsifier", "AA04", ("falsifiers", "falsifier", "counterexamples", "counterexample")),
    ("strongest_parent", "AA05",
     ("strongest parents", "strongest parent", "parents", "parent")),
)
EXPERIMENT_LEDGERS = (
    ("leakage", ("leakage",)),
    ("search_space", ("search space",)),
    ("cost_model", ("cost model",)),
    ("evaluation", ("evaluation",)),
    ("sampling_bias", ("sampling bias",)),
)

# A ledger is emitted only as a BLOCK-LEADING bold label. A prose sentence
# mentioning the word is not an emission; that decoy class is named in the
# freeze and is asserted to be rejected.
BLOCK_LABEL = re.compile(r"^\*\*([^*]+?)\*\*")
H2 = re.compile(r"^##\s+(?!#)(.*\S)\s*$")
DEFINITION_HEADING = re.compile(r"^(definition|definitions)\b", re.IGNORECASE)

# A DISCLOSED SUB-CLASSIFICATION, not a change to the declared predicate.
# FREEZE_V1.md section 5 defines a named result as any level-2 ATX heading that
# is not a bare definition marker. Over the real corpus that predicate
# OVER-approximates: section headings such as "Scope" or "Claim ceiling" are
# counted as results. Over-approximation can only OVERSTATE the ledger debt and
# can only make the gate STRICTER on new work, so the declared predicate stays
# primary. The conservative subset below - headings that carry a result
# identifier (`AAG-1`, `NS-2`, `RLG-T1`) or open with a result word - is
# reported alongside it so the reader can see both bounds.
RESULT_ID = re.compile(r"\b[A-Z][A-Z0-9]{0,7}-[A-Z0-9]{1,5}\b")
# `claim` and `result` are deliberately NOT here: `## Claim ceiling` and
# `## Results` are ordinary section headings in this corpus, and a fixture
# built to test the false-positive class caught them being typed as named
# results. A checker that cries wolf on its first real run gets switched off.
RESULT_WORD = re.compile(
    r"^\s*(?:\d+\.\s*)?(theorem|lemma|proposition|corollary)\b",
    re.IGNORECASE,
)


def has_result_identifier(title: str) -> bool:
    return bool(RESULT_ID.search(title) or RESULT_WORD.match(title))


class GateError(RuntimeError):
    pass


def normalize_label(raw: str) -> str:
    return raw.strip().rstrip(".:").strip().lower()


def tracked_files(root: Optional[Path] = None) -> List[str]:
    if root is not None:
        out = []
        for p in sorted(root.rglob("*.md")):
            out.append(str(p.relative_to(root)))
        return out
    # git ls-files sees only TRACKED files, so a package that has been written
    # but not yet committed is invisible: the gate then reports passed with
    # new_named_results 0, having scanned nothing it was asked about. Three
    # lanes hit that independently and each had to verify their ledgers by
    # calling theorem_report directly, because the gate said nothing was there.
    #
    # Include untracked-but-not-ignored markdown as well, so the gate reads the
    # working tree it is actually being run against. Ignored files stay out.
    proc = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard",
         "research/*.md", "research/**/*.md"],
        cwd=str(REPO), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise GateError("git ls-files failed: %s" % proc.stderr.decode("utf-8", "replace"))
    return sorted(set(proc.stdout.decode("utf-8").split()))


# ---------------------------------------------------------------------------
# PR scope: which files does THIS change own?  One rule, shared by the test
# (`test_ledger_gate_v1.py::_owned_paths`) and the workflow (`--print-owned`).
# ---------------------------------------------------------------------------
GIT = "/usr/bin/git" if os.path.exists("/usr/bin/git") else (shutil.which("git") or "git")


def _git(args: Sequence[str], cwd: Path, git: str) -> Optional[str]:
    """stdout of a git command, or None when it fails. Never raises."""
    try:
        proc = subprocess.run([git] + list(args), cwd=str(cwd),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", "replace")


def owned_paths_from_git(repo: Optional[Path] = None,
                         base_sha: Optional[str] = None,
                         git: Optional[str] = None,
                         only_markdown: bool = True) -> Optional[List[str]]:
    """Files this change added or modified, or None when there is no PR scope.

    The rule, in priority order:

      1. HEAD has two parents (a `pull_request` checkout is GitHub's merge of
         the PR head into the CURRENT base tip) -> `HEAD^1..HEAD`.  The first
         parent IS the base the PR is being merged into, so this is exactly
         the PR's own contribution, however far the base has moved since.
      2. otherwise a base sha is known (`PR_BASE_SHA`, i.e.
         `github.event.pull_request.base.sha`) -> `merge-base(base, HEAD)..HEAD`.
      3. otherwise None: the caller enforces repo-wide (push to main).

    Why not `base.sha..HEAD` (two-dot)?  `base.sha` is the base at the PR's
    LAST synchronize event, while a merge checkout's HEAD contains the base
    as it is NOW.  Every file main gained in between is then attributed to
    the PR: a ledger-mirror fix was failed for a theorem note another lane
    merged (NEW_RESULT_MISSING_LEDGER on a file the PR never touched).  Why
    not `origin/<base>...HEAD` (three-dot)?  It is a second, different rule
    for the same question, it needs the remote ref to be present, and the
    test and the workflow disagreed about which one was in force.
    """
    cwd = repo if repo is not None else REPO
    tool = git or GIT
    if base_sha is None:
        base_sha = os.environ.get("PR_BASE_SHA") or ""
    if _git(["rev-parse", "--verify", "--quiet", "HEAD^2"], cwd, tool) is not None:
        span = ["HEAD^1", "HEAD"]
    elif base_sha:
        mb = _git(["merge-base", base_sha, "HEAD"], cwd, tool)
        if mb is None or not mb.strip():
            return None
        span = [mb.strip(), "HEAD"]
    else:
        return None
    out = _git(["diff", "--name-only", "--diff-filter=ACMR"] + span, cwd, tool)
    if out is None:
        return None
    paths = [p for p in out.split("\n") if p.strip()]
    if only_markdown:
        paths = [p for p in paths if p.endswith(".md")]
    return paths


def stale_two_dot_paths(repo: Optional[Path], base_sha: str,
                        git: Optional[str] = None) -> List[str]:
    """The rule this package USED to apply (`base_sha..HEAD`), kept only as a
    regression witness for the test: on a merge checkout whose base moved it
    reports files the change never authored."""
    out = _git(["diff", "--name-only", "--diff-filter=ACMR", base_sha, "HEAD"],
               repo if repo is not None else REPO, git or GIT)
    return [p for p in (out or "").split("\n") if p.strip()]


def is_theorem_artifact(path: str) -> bool:
    return path.endswith(".md") and bool(THEOREM_ARTIFACT.search(Path(path).name))


def is_experiment_artifact(path: str, text: str) -> bool:
    if not (path.endswith(".md") and EXPERIMENT_ARTIFACT.search(Path(path).name)):
        return False
    return EXPERIMENT_SCHEMA in text


def named_results(text: str) -> List[Tuple[str, str]]:
    """Cut the file at level-2 ATX headings. Bare definition headings are not
    named results (a definition has nothing to falsify)."""
    lines = text.split("\n")
    spans = []  # type: List[Tuple[str, List[str]]]
    current = None  # type: Optional[Tuple[str, List[str]]]
    fenced = False
    for line in lines:
        if line.startswith("```"):
            fenced = not fenced
        if not fenced:
            hit = H2.match(line)
            if hit:
                if current is not None:
                    spans.append(current)
                current = (hit.group(1).strip(), [])
                continue
        if current is not None:
            current[1].append(line)
    if current is not None:
        spans.append(current)
    return [(title, "\n".join(body)) for title, body in spans
            if not DEFINITION_HEADING.match(title)]


def emitted_labels(body: str) -> Set[str]:
    out = set()
    fenced = False
    for line in body.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        hit = BLOCK_LABEL.match(line)
        if hit:
            out.add(normalize_label(hit.group(1)))
    return out


def theorem_report(path: str, text: str) -> Dict[str, object]:
    results = []
    for title, body in named_results(text):
        labels = emitted_labels(body)
        emits = {}
        for key, row, accepted in THEOREM_LEDGERS:
            emits[key] = any(a in labels for a in accepted)
        results.append({
            "result": title,
            "emits": emits,
            "complete": all(emits.values()),
            "identified": has_result_identifier(title),
            "labels": sorted(labels),
        })
    return {"path": path, "named_results": results,
            "count": len(results),
            "vendored": "/raw/" in path,
            "complete": sum(1 for r in results if r["complete"])}


def experiment_report(path: str, text: str) -> Dict[str, object]:
    labels = emitted_labels(text)
    emits = {}
    for key, accepted in EXPERIMENT_LEDGERS:
        emits[key] = any(a in labels for a in accepted)
    return {"path": path, "emits": emits, "complete": all(emits.values()),
            "labels": sorted(labels)}


def census(root: Optional[Path] = None,
           exclude_prefixes: Sequence[str] = ()) -> Dict[str, object]:
    base = root if root is not None else REPO
    theorem_files = []
    experiment_files = []
    for rel in tracked_files(root):
        if any(rel.startswith(pref) for pref in exclude_prefixes):
            continue
        p = base / rel
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if is_theorem_artifact(rel):
            theorem_files.append(theorem_report(rel, text))
        elif is_experiment_artifact(rel, text):
            experiment_files.append(experiment_report(rel, text))

    totals = {key: 0 for key, _, _ in THEOREM_LEDGERS}
    n_results = 0
    n_complete = 0
    n_identified = 0
    n_identified_complete = 0
    for f in theorem_files:
        for r in f["named_results"]:
            n_results += 1
            n_complete += int(r["complete"])
            if r["identified"]:
                n_identified += 1
                n_identified_complete += int(r["complete"])
            for key in totals:
                totals[key] += int(r["emits"][key])
    unparsed = sorted(f["path"] for f in theorem_files if f["count"] == 0)
    identified_non_compliant = n_identified - n_identified_complete
    vendored = [f for f in theorem_files if f["vendored"]]

    exp_totals = {key: 0 for key, _ in EXPERIMENT_LEDGERS}
    for f in experiment_files:
        for key in exp_totals:
            exp_totals[key] += int(f["emits"][key])

    return {
        "schema": "GMI_833_LEDGER_CENSUS_V1",
        "route": "A",
        "theorem_files": len(theorem_files),
        "named_results": n_results,
        "complete_named_results": n_complete,
        "non_compliant_named_results": n_results - n_complete,
        "identified_named_results": n_identified,
        "identified_complete": n_identified_complete,
        "identified_non_compliant": identified_non_compliant,
        "excluded_prefixes": list(exclude_prefixes),
        "unparsed_theorem_artifacts": len(unparsed),
        "unparsed_theorem_artifact_paths": unparsed,
        "vendored_theorem_artifacts": len(vendored),
        "vendored_named_results": sum(f["count"] for f in vendored),
        "emission_by_ledger": {key: totals[key] for key, _, _ in THEOREM_LEDGERS},
        "row_for_ledger": {key: row for key, row, _ in THEOREM_LEDGERS},
        "experiment_files": len(experiment_files),
        "experiment_complete": sum(1 for f in experiment_files if f["complete"]),
        "experiment_emission_by_ledger": exp_totals,
        "per_file": theorem_files,
        "per_experiment": experiment_files,
    }


# ---------------------------------------------------------------------------
# The ratchet.
# ---------------------------------------------------------------------------
def baseline_key(path: str, result: str) -> str:
    return path + "::" + result


def write_baseline(exclude_prefixes: Sequence[str] = ()) -> Dict[str, object]:
    c = census(None, exclude_prefixes)
    entries = {}
    for f in c["per_file"]:
        for r in f["named_results"]:
            entries[baseline_key(f["path"], r["result"])] = bool(r["complete"])
    payload = {
        "schema": "GMI_833_LEDGER_BASELINE_V1",
        "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
        "excluded_prefixes": list(exclude_prefixes),
        "exclusion_reason": (
            "the four packages this tranche adds did not exist at source_main; "
            "excluding them keeps the baseline a faithful picture of main"
        ),
        "identified_named_results": c["identified_named_results"],
        "identified_complete": c["identified_complete"],
        "unparsed_theorem_artifacts": c["unparsed_theorem_artifacts"],
        "theorem_files": c["theorem_files"],
        "named_results": c["named_results"],
        "complete_named_results": c["complete_named_results"],
        "non_compliant_named_results": c["non_compliant_named_results"],
        "identified_non_compliant": c["identified_non_compliant"],
        "emission_by_ledger": c["emission_by_ledger"],
        "experiment_files": c["experiment_files"],
        "entries": dict(sorted(entries.items())),
    }
    BASELINE.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return payload


# ---------------------------------------------------------------------------
# Immutable-custody amendment (issue #1049 item 2).
#
# A theorem note whose CURRENT bytes are sha256-pinned by ANOTHER package's
# record cannot be repaired in place: adding the missing ledgers changes its
# bytes and breaks that package's custody check (e.g. gmi-833-kl-revival-v1
# verifies the live sha256 of every parent pin). Such results are debt that is
# identified but not editable. They are listed one by one, by (path, result),
# in LEDGER_BASELINE_AMENDMENT_V1.json -- never by blanket re-baselining -- and
# every entry is re-verified on each run:
#   * the file's live sha256 equals the entry's pin_sha256, AND
#   * the named record exists, lies in a DIFFERENT package, and contains that
#     sha256 verbatim, AND
#   * the (path, result) is a live named result that is identified and
#     non-compliant.
# An entry that fails any check is DROPPED and reported, so the result is
# enforced again (fail closed). Editing the pinned file breaks its pin, which
# drops its entries: the exemption cannot outlive the custody it rests on.
# The frozen LEDGER_BASELINE_V1.json is not touched.
# ---------------------------------------------------------------------------
AMENDMENT = HERE / "LEDGER_BASELINE_AMENDMENT_V1.json"


def _package_of(rel: str) -> str:
    parts = rel.split("/")
    return "/".join(parts[:2]) if len(parts) >= 3 and parts[0] == "research" else os.path.dirname(rel)


def load_amendment(c: Dict[str, object], root: Optional[Path] = None,
                   path: Optional[Path] = None) -> Tuple[Dict[str, bool], List[Dict[str, str]]]:
    """Return ({baseline_key: False} for every verified entry, [dropped entries])."""
    apath = path if path is not None else AMENDMENT
    if not apath.exists():
        return {}, []
    doc = json.loads(apath.read_text(encoding="utf-8"))
    if doc.get("schema") != "GMI_833_LEDGER_BASELINE_AMENDMENT_V1":
        raise GateError("amendment schema mismatch at %s" % apath)
    base = root if root is not None else REPO
    live = {}
    for f in c["per_file"]:
        for r in f["named_results"]:
            live[baseline_key(f["path"], r["result"])] = r
    valid = {}  # type: Dict[str, bool]
    dropped = []  # type: List[Dict[str, str]]
    for e in doc.get("entries", []):
        key = baseline_key(e["path"], e["result"])
        target = base / e["path"]
        record = base / e["pinned_by"]
        why = None
        if _package_of(e["pinned_by"]) == _package_of(e["path"]):
            why = "pin record is inside the pinned file's own package"
        elif not target.exists() or not record.exists():
            why = "pinned file or pin record missing"
        elif hashlib.sha256(target.read_bytes()).hexdigest() != e["pin_sha256"]:
            why = "pinned file bytes changed since the pin"
        elif e["pin_sha256"] not in record.read_text(encoding="utf-8", errors="replace"):
            why = "pin record no longer carries the sha256"
        elif key not in live:
            why = "no such live named result"
        elif not live[key]["identified"] or live[key]["complete"]:
            why = "result is not identified debt (unidentified or already complete)"
        if why is None:
            valid[key] = False
        else:
            dropped.append({"path": e["path"], "result": e["result"], "reason": why})
    return valid, dropped


def gate(owned: Optional[Sequence[str]] = None,
         root: Optional[Path] = None,
         baseline_path: Optional[Path] = None,
         amendment_path: Optional[Path] = None) -> Tuple[int, Dict[str, object]]:
    """Return (exit_code, report). Non-zero exit means the gate FAILED."""
    bpath = baseline_path or BASELINE
    if not bpath.exists():
        raise GateError("no frozen baseline at %s" % bpath)
    base = json.loads(bpath.read_text(encoding="utf-8"))

    c = census(root)
    # A custom baseline (fixtures) never inherits the real repo's amendment.
    if amendment_path is None and (baseline_path is not None or root is not None):
        amended, dropped = {}, []
    else:
        amended, dropped = load_amendment(c, root, amendment_path)
    known = dict(base["entries"])
    for key, was in amended.items():
        known.setdefault(key, was)
    violations = []  # type: List[Dict[str, str]]
    new_results = 0
    regressions = 0
    owned_set = set(owned) if owned is not None else None

    # ENFORCEMENT SCOPE vs MEASUREMENT SCOPE.
    # The census above uses the declared over-approximating predicate, which is
    # right for the debt number: it can only overstate. Enforcement uses the
    # conservative `identified` subset, because a lane that writes `## Scope`
    # as a section heading in a new theorem note must not be failed for a
    # reason that has nothing to do with ledger discipline. A gate that fires
    # on work you did not do is a gate that gets switched off.
    unidentified_new = 0
    for f in c["per_file"]:
        if owned_set is not None and f["path"] not in owned_set:
            continue
        for r in f["named_results"]:
            key = baseline_key(f["path"], r["result"])
            was = known.get(key)
            if was is None and not r["identified"]:
                unidentified_new += 1
                continue
            if was is None:
                new_results += 1
                if not r["complete"]:
                    missing = sorted(k for k, v in r["emits"].items() if not v)
                    violations.append({
                        "kind": "NEW_RESULT_MISSING_LEDGER",
                        "path": f["path"], "result": r["result"],
                        "missing": ",".join(missing),
                    })
            elif was and not r["complete"] and r["identified"]:
                regressions += 1
                missing = sorted(k for k, v in r["emits"].items() if not v)
                violations.append({
                    "kind": "COMPLIANT_RESULT_REGRESSED",
                    "path": f["path"], "result": r["result"],
                    "missing": ",".join(missing),
                })

    # Monotone corpus ratchet: the debt may never grow. Only meaningful when
    # the whole corpus was scanned.
    debt_grew = False
    if owned_set is None:
        # The ratchet binds the ENFORCED population. Binding it to the
        # over-approximating measurement would fail any lane that adds a
        # theorem note using `##` for section headings, which is the same
        # false-positive class the enforcement scope above avoids.
        # The allowance grows only by verified immutable-custody entries that
        # are not already in the frozen baseline, one per named result.
        allowed = base["identified_non_compliant"] + sum(
            1 for key in amended if key not in base["entries"])
        debt_grew = c["identified_non_compliant"] > allowed
        if debt_grew:
            violations.append({
                "kind": "CORPUS_DEBT_GREW",
                "path": "(corpus)",
                "result": "identified_non_compliant",
                "missing": "%d > %d" % (c["identified_non_compliant"], allowed),
            })

    report = {
        "schema": "GMI_833_LEDGER_GATE_V1",
        "scope": "owned-files" if owned_set is not None else "repo-wide",
        "baseline_non_compliant": base["non_compliant_named_results"],
        "live_non_compliant": c["non_compliant_named_results"],
        "baseline_identified_non_compliant": base["identified_non_compliant"],
        "live_identified_non_compliant": c["identified_non_compliant"],
        "baseline_named_results": base["named_results"],
        "live_named_results": c["named_results"],
        "new_named_results": new_results,
        "new_headings_outside_enforcement_scope": unidentified_new,
        "enforcement_scope": ("named results carrying a result identifier or a "
                              "result word; section headings are measured but "
                              "not enforced"),
        "regressions": regressions,
        "corpus_debt_grew": debt_grew,
        "immutable_custody_amended_results": len(amended),
        "immutable_custody_dropped_entries": dropped,
        "violations": violations,
        "passed": not violations,
    }
    return (0 if not violations else 1), report


# ---------------------------------------------------------------------------
# Null: is the accepted label vocabulary an arbitrary choice of four groups?
# ---------------------------------------------------------------------------
NULL_TRIALS = 200
NULL_SEED = 8330206  # 833 / AA02-AA06

# The five AA rows this package reconciles, verbatim from comment 5684607872 at
# source_main. The accepted canonical labels are DERIVED from these strings;
# they are not invented here, and the guard below proves it.
ROWS = {
    "AA02": "- [ ] Require every theorem/proof/experiment to emit an explicit assumptions ledger.",
    "AA03": "- [ ] Require every theorem to emit a dependency ledger.",
    "AA04": "- [ ] Require every theorem to emit a falsifier/counterexample ledger.",
    "AA05": "- [ ] Require every theorem to emit a strongest-parent/subsumption ledger.",
    "AA06": ("- [ ] Require every experiment to emit leakage, search-space, cost-model, "
             "evaluation and sampling-bias ledgers."),
}
# canonical label per ledger; the accepted tuples above are widenings of these.
CANONICAL = {
    "assumptions": ("AA02", "assumptions"),
    "dependency": ("AA03", "dependency"),
    "falsifier": ("AA04", "falsifier"),
    "strongest_parent": ("AA05", "strongest parent"),
    "leakage": ("AA06", "leakage"),
    "search_space": ("AA06", "search space"),
    "cost_model": ("AA06", "cost model"),
    "evaluation": ("AA06", "evaluation"),
    "sampling_bias": ("AA06", "sampling bias"),
}


def normalize_row(text: str) -> str:
    """Declared normalization: lowercase, markdown emphasis dropped, hyphens and
    slashes read as spaces, whitespace collapsed."""
    low = text.lower().replace("*", "").replace("`", "")
    for ch in "-/,":
        low = low.replace(ch, " ")
    return " ".join(low.split())


def anti_invention_guard() -> Dict[str, object]:
    """Every canonical ledger label must occur literally in the verbatim text of
    the AA row that demands it. A requirement cannot be invented to make a row
    pass, and a row-named ledger cannot be quietly dropped."""
    normalized = dict((rid, normalize_row(txt)) for rid, txt in ROWS.items())
    per_label = {}
    for key, (row_id, label) in sorted(CANONICAL.items()):
        per_label[key] = {
            "row": row_id,
            "canonical_label": label,
            "occurs_in_row_text": label in normalized[row_id],
        }
    # And no row named ledger may be missing: AA06 names exactly five.
    aa06 = [k for k, (r, _) in CANONICAL.items() if r == "AA06"]
    return {
        "labels_checked": len(per_label),
        "labels_occurring_in_their_row": sum(
            1 for v in per_label.values() if v["occurs_in_row_text"]),
        "aa06_ledger_count": len(aa06),
        "per_label": per_label,
        "passed": all(v["occurs_in_row_text"] for v in per_label.values()),
    }


def row_binding_null() -> Dict[str, object]:
    """Null for the guard: shuffle which canonical label is bound to which row.

    The true binding satisfies the guard for every label. A random binding
    should not. This is the null that tests whether the label vocabulary was
    read off the rows or chosen to fit."""
    import random
    normalized = dict((rid, normalize_row(txt)) for rid, txt in ROWS.items())
    labels = [label for _, label in sorted(CANONICAL.values())]
    rows = [row for row, _ in sorted(CANONICAL.values())]
    rng = random.Random(NULL_SEED)
    full = 0
    sat = []
    for _ in range(NULL_TRIALS):
        shuffled = rows[:]
        rng.shuffle(shuffled)
        hits = sum(1 for lab, row in zip(labels, shuffled) if lab in normalized[row])
        sat.append(hits)
        if hits == len(labels):
            full += 1
    return {
        "trials": NULL_TRIALS,
        "seed": NULL_SEED,
        "labels": len(labels),
        "true_binding_satisfied": len(labels),
        "random_bindings_fully_satisfied": full,
        "max_random_satisfied": max(sat),
        "mean_random_satisfied_exact": str(__import__("fractions").Fraction(sum(sat), NULL_TRIALS)),
    }


def label_pool(c: Dict[str, object], top: int = 60) -> List[str]:
    from collections import Counter
    counter = Counter()  # type: Counter
    for f in c["per_file"]:
        for r in f["named_results"]:
            for lab in r["labels"]:
                counter[lab] += 1
    return [lab for lab, _ in counter.most_common(top)]


def null_study(c: Dict[str, object]) -> Dict[str, object]:
    """Draw four disjoint random label groups of the declared sizes from the
    corpus' own most common block labels and recompute compliance."""
    import random
    cached = []  # type: List[Set[str]]
    for f in c["per_file"]:
        for r in f["named_results"]:
            cached.append(set(r["labels"]))
    sizes = [len(accepted) for _, _, accepted in THEOREM_LEDGERS]
    true_complete = sum(1 for labs in cached
                        if all(any(a in labs for a in accepted)
                               for _, _, accepted in THEOREM_LEDGERS))
    pool = label_pool(c)
    rng = random.Random(NULL_SEED)
    beat = 0
    best = 0
    for _ in range(NULL_TRIALS):
        draw = rng.sample(pool, sum(sizes))
        groups = []
        at = 0
        for n in sizes:
            groups.append(tuple(draw[at:at + n]))
            at += n
        hits = sum(1 for labs in cached
                   if all(any(a in labs for a in g) for g in groups))
        best = max(best, hits)
        if hits >= true_complete and true_complete > 0:
            beat += 1
    return {
        "trials": NULL_TRIALS,
        "seed": NULL_SEED,
        "pool_size": len(pool),
        "group_sizes": sizes,
        "true_complete_named_results": true_complete,
        "random_vocabularies_matching_or_beating_truth": beat,
        "best_random_complete": best,
    }


# ---------------------------------------------------------------------------
def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--owned-files")
    ap.add_argument("--write-baseline", action="store_true")
    ap.add_argument("--scan-root")
    ap.add_argument("--baseline")
    ap.add_argument("--exclude-prefix", action="append", default=[])
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--full", action="store_true",
                    help="include the per-file detail in the census output")
    ap.add_argument("--print-owned", action="store_true",
                    help="print the PR-owned markdown paths (one per line) under "
                         "the shared scope rule; exit 3 when there is no PR scope")
    args = ap.parse_args(list(argv))

    root = Path(args.scan_root).resolve() if args.scan_root else None

    if args.print_owned:
        owned = owned_paths_from_git()
        if owned is None:
            print("no PR scope: HEAD is not a merge and PR_BASE_SHA is unset",
                  file=sys.stderr)
            return 3
        for p in owned:
            print(p)
        return 0

    if args.write_baseline:
        payload = write_baseline(tuple(args.exclude_prefix))
        print(json.dumps({k: v for k, v in payload.items() if k != "entries"},
                         indent=2, sort_keys=True))
        return 0

    if args.gate:
        owned = None
        if args.owned_files:
            raw = Path(args.owned_files).read_text(encoding="utf-8").split()
            owned = [r for r in raw if r.strip()]
        code, report = gate(owned, root,
                            Path(args.baseline).resolve() if args.baseline else None)
        print(json.dumps(report, indent=2, sort_keys=True))
        if code:
            print("LEDGER GATE FAILED: %d violation(s)" % len(report["violations"]),
                  file=sys.stderr)
        return code

    c = census(root, tuple(args.exclude_prefix))
    if args.null:
        print(json.dumps({
            "guard": anti_invention_guard(),
            "row_binding_null": row_binding_null(),
            "vocabulary_null_diagnostic": null_study(c),
        }, indent=2, sort_keys=True))
        return 0
    if not args.full:
        c = {k: v for k, v in c.items() if k not in ("per_file", "per_experiment")}
    print(json.dumps(c, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
