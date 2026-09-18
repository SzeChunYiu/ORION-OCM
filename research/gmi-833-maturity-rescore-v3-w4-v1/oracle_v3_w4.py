#!/usr/bin/env python3
"""Route B: an independent oracle for the v3-W4 correction.

Materially independent of route A (`rescore_v3_w4.py`), which it does NOT
import and whose algorithms it deliberately avoids:

  * censuses        - single-pass accumulation into integer counters keyed by
                      a pre-declared fixed key list, instead of route A's
                      dict-growing classifier;
  * the delta       - set algebra over result_id (removed / added / retained)
                      instead of route A's in-place row rewrite;
  * blob identity   - `git hash-object` plumbing, instead of route A's
                      pure-python reconstruction of the blob header;
  * custody order   - `git rev-list --ancestry-path` plus reverse-chronological
                      `git log` position, instead of `merge-base --is-ancestor`;
  * the adverse population - a SCHEMA-AGNOSTIC recursive walk of every register
                      that finds package names and adverse tokens wherever they
                      live, instead of route A's explicit section enumeration.
                      This is the check that justifies any 'zero found' claim:
                      if route A's key enumeration missed a section, route B
                      would find packages route A never considered.

Exact integer arithmetic; stdlib only; Py3.8-safe.
Run:  python3 -I -B oracle_v3_w4.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Sequence, Set, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, os.pardir, os.pardir))

_SCORES = "research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json"
_REGDIR = "research/gmi-833-corpus-passes-v2-v1"
_PARENT = "gmi-novel-intelligence-w4-v1"
_ARRIVAL = "gmi-novel-intelligence-w4-prospective-v1"
_PARENT_ROW = "GMI833_V2_LEGACY_074_W4-C"

_M_KEYS = ("M0", "M1", "M2", "M3", "M4", "M5", "M6", "UNKNOWN")
_EV_KEYS = ("EV0", "EV1", "EV2", "EV3", "EV4", "EV5", "UNKNOWN")

_PKG_RE = re.compile(r"\b(?:gmi|machine)-[a-z0-9]+(?:-[a-z0-9.]+)*-v\d+\b")
_ADVERSE_TOKENS = (
    "POST_HOC_SUSPECT", "OVERSTRONG", "UNAUDITED_COST_DEPENDENT",
    "UNTESTED_SCALARIZATION_DEPENDENT", "CUSTODY_NON_DEMONSTRABLE",
    "NON_DEMONSTRABLE", "custody cannot demonstrate", "DEGENERATE_HELDOUT",
    "TYPED_POST_HOC", "post-freeze heldout registration",
)
_EXCULPATORY = ("screen false positive", "false positive:", "no prospective claim")


def _p(rel_path):
    # type: (str) -> str
    return os.path.join(_ROOT, rel_path)


def _sh(argv):
    # type: (Sequence[str]) -> Tuple[int, str]
    try:
        proc = subprocess.Popen(
            ["git", "-C", _ROOT] + list(argv),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw, _err = proc.communicate()
    except OSError:
        return 127, ""
    return proc.returncode, raw.decode("utf-8", "replace")


def blob_id(rel_path):
    # type: (str) -> Optional[str]
    rc, out = _sh(["hash-object", "--", _p(rel_path)])
    if rc != 0:
        return None
    return out.strip() or None


def jload(rel_path):
    # type: (str) -> object
    handle = open(_p(rel_path), "r")
    try:
        return json.load(handle)
    finally:
        handle.close()


# --------------------------------------------------------------------------
# census by accumulation into a fixed key list
# --------------------------------------------------------------------------
def tally(records, field, keys):
    # type: (Sequence[Dict], str, Sequence[str]) -> Dict[str, int]
    counters = {}
    for key in keys:
        counters[key] = 0
    stray = []
    for rec in records:
        value = rec.get(field, "UNKNOWN")
        if value in counters:
            counters[value] = counters[value] + 1
        else:
            stray.append(value)
    if stray:
        raise AssertionError("values outside the declared key list: %r" % (sorted(set(stray)),))
    return dict((k, v) for k, v in counters.items() if v)


# --------------------------------------------------------------------------
# delta by set algebra over result_id
# --------------------------------------------------------------------------
def apply_delta_by_setalgebra(published, delta_records):
    # type: (Sequence[Dict], Sequence[Dict]) -> Tuple[List[Dict], Dict[str, List[str]]]
    published_ids = []
    for rec in published:
        published_ids.append(rec["result_id"])
    delta_ids = []
    for rec in delta_records:
        delta_ids.append(rec["result_id"])
    replaced = []
    added = []
    for rid in delta_ids:
        if rid in published_ids:
            replaced.append(rid)
        else:
            added.append(rid)
    retained = []
    for rid in published_ids:
        if rid not in delta_ids:
            retained.append(rid)
    index = {}
    for rec in published:
        index[rec["result_id"]] = rec
    for rec in delta_records:
        index[rec["result_id"]] = rec
    out = []
    for rid in retained + sorted(replaced) + sorted(added):
        out.append(index[rid])
    return out, {
        "retained": sorted(retained), "replaced": sorted(replaced), "added": sorted(added),
    }


# --------------------------------------------------------------------------
# custody by ancestry-path and log position (not merge-base)
# --------------------------------------------------------------------------
def first_add(ref, path):
    # type: (str, str) -> Optional[str]
    rc, out = _sh(["log", ref, "--diff-filter=A", "--format=%H", "--", path])
    if rc != 0:
        return None
    rows = []
    for line in out.splitlines():
        if line.strip():
            rows.append(line.strip())
    if not rows:
        return ""
    return rows[0]


def strictly_before(earlier, later, ref):
    # type: (str, str, str) -> Optional[bool]
    """True iff `earlier` is a strict ancestor of `later`, by ancestry-path.

    git rev-list --ancestry-path A..B lists commits on a path from A to B; it is
    non-empty exactly when A is a strict ancestor of B reachable from B.
    """
    if earlier == later:
        return False
    rc, out = _sh(["rev-list", "--ancestry-path", "%s..%s" % (earlier, later)])
    if rc != 0:
        return None
    forward = bool([ln for ln in out.splitlines() if ln.strip()])
    rc2, out2 = _sh(["rev-list", "--ancestry-path", "%s..%s" % (later, earlier)])
    if rc2 != 0:
        return None
    backward = bool([ln for ln in out2.splitlines() if ln.strip()])
    if forward and not backward:
        return True
    if backward and not forward:
        return False
    return None  # unrelated or ambiguous: NOT a pass
    # (None is never read as 'fine' by the caller)


def custody_verdict(ref, pkg_dir, freeze_files, outcome_files):
    # type: (str, str, Sequence[str], Sequence[str]) -> str
    freeze_commits = []
    for name in freeze_files:
        got = first_add(ref, pkg_dir + "/" + name)
        if got is None:
            return "NOT_CHECKED"
        if got:
            freeze_commits.append(got)
    outcome_commits = []
    for name in outcome_files:
        got = first_add(ref, pkg_dir + "/" + name)
        if got is None:
            return "NOT_CHECKED"
        if got:
            outcome_commits.append(got)
    if not freeze_commits or not outcome_commits:
        return "NOT_CHECKED"
    saw_same = False
    for fzc in freeze_commits:
        for occ in outcome_commits:
            if fzc == occ:
                saw_same = True
                continue
            verdict = strictly_before(fzc, occ, ref)
            if verdict is None:
                return "NOT_CHECKED"
            if verdict is False:
                return "OUTCOME_FIRST"
    if saw_same:
        return "SAME_COMMIT"
    return "FREEZE_FIRST"


# --------------------------------------------------------------------------
# schema-agnostic adverse-population discovery
# --------------------------------------------------------------------------
def harvest(node, path, found):
    # type: (object, str, List[Dict]) -> None
    if isinstance(node, dict):
        blob = json.dumps(node, sort_keys=True)
        _consider(blob, path, found)
        for key in sorted(node.keys()):
            harvest(node[key], path + "." + key, found)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            harvest(item, "%s[%d]" % (path, i), found)
    elif isinstance(node, str):
        _consider(node, path, found)


def _consider(text, path, found):
    # type: (str, str, List[Dict]) -> None
    hits = []
    for token in _ADVERSE_TOKENS:
        if token in text:
            hits.append(token)
    if not hits:
        return
    packages = sorted(set(_PKG_RE.findall(text)))
    if not packages:
        return
    exculpated = False
    for phrase in _EXCULPATORY:
        if phrase in text:
            exculpated = True
    for pkg in packages:
        found.append({
            "path": path, "package": pkg, "tokens": sorted(set(hits)),
            "exculpated": exculpated,
        })


def discover_adverse():
    # type: () -> Dict[str, Dict]
    files = []
    for name in sorted(os.listdir(_p(_REGDIR))):
        if name.startswith("VERDICT_REGISTER") and name.endswith(".json"):
            files.append(name)
    found = []  # type: List[Dict]
    for name in files:
        harvest(jload(_REGDIR + "/" + name), name, found)
    # also mine the plain-english gap-state prose for short package fragments
    reg = jload(_REGDIR + "/VERDICT_REGISTER_V1.json")
    prose = reg["L47_post_hoc"]["overclaiming_freeze_texts"]
    # Strip the parenthesised quotations, then take every hyphenated identifier
    # left in the prose.  This is derived from the register text itself, not a
    # hand-written list: if the register names another overclaiming package, it
    # is picked up without editing this oracle.
    stripped = re.sub(r"\([^)]*\)", " ", prose)
    fragments = []
    for frag in re.findall(r"\b[a-z0-9]+(?:-[a-z0-9]+){1,}\b", stripped):
        if len(frag) > 6 and frag not in ("freeze-texts",):
            fragments.append(frag)
    by_pkg = {}  # type: Dict[str, Dict]
    for item in found:
        entry = by_pkg.setdefault(item["package"], {
            "package": item["package"], "paths": [], "tokens": set(),
            "exculpated_everywhere": True, "from_fragment": False,
        })
        entry["paths"].append(item["path"])
        entry["tokens"].update(item["tokens"])
        if not item["exculpated"]:
            entry["exculpated_everywhere"] = False
    for frag in sorted(set(fragments)):
        by_pkg.setdefault("FRAGMENT:" + frag, {
            "package": "FRAGMENT:" + frag, "paths": ["L47_post_hoc.overclaiming_freeze_texts"],
            "tokens": set(["custody cannot demonstrate"]),
            "exculpated_everywhere": False, "from_fragment": True,
        })
    out = {}
    for key in sorted(by_pkg):
        entry = by_pkg[key]
        entry["tokens"] = sorted(entry["tokens"])
        entry["paths"] = sorted(set(entry["paths"]))
        out[key] = entry
    return out


def exposed_rows(rows, package_or_fragment):
    # type: (Sequence[Dict], str) -> List[Dict]
    needle = package_or_fragment
    if needle.startswith("FRAGMENT:"):
        needle = needle[len("FRAGMENT:"):]
    out = []
    for rec in rows:
        if needle not in rec["package"]:
            continue
        if rec.get("maturity_M") in ("M4", "M5", "M6") or rec.get("support_kind") == "FROZEN_HELDOUT":
            out.append(rec)
    return out


def mentions_finding(rec):
    # type: (Dict) -> bool
    parts = [
        str(rec.get("justification", "")), str(rec.get("verification_note", "")),
        str(rec.get("claim_evidence_gap", "")),
    ]
    for item in rec.get("forbidden_extrapolations", []) or []:
        parts.append(str(item))
    blob = " ".join(parts).upper()
    for token in ("POST_HOC", "CUSTODY", "OVERSTRONG", "UNAUDITED", "NON_DEMONSTRABLE", "DEGENERATE"):
        if token in blob:
            return True
    return False


def sweep_b(rows):
    # type: (Sequence[Dict]) -> Dict
    adverse = discover_adverse()
    scored_packages = set()
    for rec in rows:
        scored_packages.add(rec["package"])
    unreflected = {}
    out_of_pop = []
    immaterial = []
    reflected = []
    not_adverse = []
    for key in sorted(adverse):
        entry = adverse[key]
        if entry["exculpated_everywhere"]:
            not_adverse.append(key)
            continue
        exposed = exposed_rows(rows, key)
        needle = key[len("FRAGMENT:"):] if key.startswith("FRAGMENT:") else key
        scored_hit = False
        for pkg in scored_packages:
            if needle in pkg:
                scored_hit = True
        if not scored_hit:
            out_of_pop.append(key)
            continue
        if not exposed:
            immaterial.append(key)
            continue
        bad = []
        for rec in exposed:
            if not mentions_finding(rec):
                bad.append(rec["result_id"])
        if bad:
            unreflected[key] = sorted(bad)
        else:
            reflected.append(key)
    return {
        "discovered": len(adverse),
        "not_adverse": sorted(not_adverse),
        "out_of_scored_population": sorted(out_of_pop),
        "immaterial": sorted(immaterial),
        "reflected": sorted(reflected),
        "unreflected": unreflected,
    }


# --------------------------------------------------------------------------
def main():
    # type: () -> int
    rows = jload(_SCORES)
    delta = jload("research/gmi-833-maturity-rescore-v3-w4-v1/SCORES_V3_DELTA.json")["records"]

    published_m = tally(rows, "maturity_M", _M_KEYS)
    published_ev = tally(rows, "evidence_EV", _EV_KEYS)
    corrected, setalg = apply_delta_by_setalgebra(rows, delta)
    corrected_m = tally(corrected, "maturity_M", _M_KEYS)
    corrected_ev = tally(corrected, "evidence_EV", _EV_KEYS)

    m4_before = set()
    for rec in rows:
        if rec["maturity_M"] == "M4":
            m4_before.add(rec["package"])
    m4_after = set()
    for rec in corrected:
        if rec["maturity_M"] == "M4":
            m4_after.add(rec["package"])

    parent_custody = custody_verdict(
        "HEAD", "research/" + _PARENT, ["FREEZE_V1.md"], ["RESULT_V1.json"])
    arrival_on_main = custody_verdict(
        "HEAD", "research/" + _ARRIVAL,
        ["FREEZE_V2_PROSPECTIVE.md", "FREEZE_V2_PROSPECTIVE.json"],
        ["RESULT_V1.json", "RECEIPT_MULTIHOST_V1.json"])
    arrival_on_branch = custody_verdict(
        "rev-l47-w4-results^{commit}", "research/" + _ARRIVAL,
        ["FREEZE_V2_PROSPECTIVE.md", "FREEZE_V2_PROSPECTIVE.json"],
        ["RESULT_V1.json", "RECEIPT_MULTIHOST_V1.json"])

    blobs = {
        _SCORES: blob_id(_SCORES),
        "research/%s/FREEZE_V2_PROSPECTIVE.md" % _ARRIVAL:
            blob_id("research/%s/FREEZE_V2_PROSPECTIVE.md" % _ARRIVAL),
        "research/%s/FREEZE_V2_PROSPECTIVE.json" % _ARRIVAL:
            blob_id("research/%s/FREEZE_V2_PROSPECTIVE.json" % _ARRIVAL),
    }

    sweep = sweep_b(rows)
    sweep_after = sweep_b(corrected)

    payload = {
        "schema": "GMI_833_MATURITY_RESCORE_V3_W4_ORACLE_V1",
        "route": "B",
        "published_M": published_m, "corrected_M": corrected_m,
        "published_EV": published_ev, "corrected_EV": corrected_ev,
        "published_rows": len(rows), "corrected_rows": len(corrected),
        "set_algebra": setalg,
        "M4_left": sorted(m4_before - m4_after),
        "M4_entered": sorted(m4_after - m4_before),
        "M4_total_before": published_m.get("M4", 0),
        "M4_total_after": corrected_m.get("M4", 0),
        "custody": {
            "parent_on_main": parent_custody,
            "arrival_on_main": arrival_on_main,
            "arrival_on_tagged_branch": arrival_on_branch,
        },
        "blobs": blobs,
        "propagation": sweep,
        "propagation_after_correction": sweep_after,
    }
    handle = open(os.path.join(_HERE, "ORACLE_RESULT_V1.json"), "w")
    try:
        json.dump(payload, handle, indent=1, sort_keys=True)
        handle.write("\n")
    finally:
        handle.close()
    print(json.dumps({
        "published_M": published_m, "corrected_M": corrected_m,
        "M4_left": payload["M4_left"], "M4_entered": payload["M4_entered"],
        "custody": payload["custody"],
        "propagation_unreflected": sorted(sweep["unreflected"].keys()),
        "propagation_discovered": sweep["discovered"],
        "propagation_out_of_pop": len(sweep["out_of_scored_population"]),
    }, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
