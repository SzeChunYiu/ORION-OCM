# -*- coding: utf-8 -*-
"""AJ9 route B -- an independent oracle for the holdout blind-source audit.

Route B imports nothing from route A.  It reads the same frozen registry but scans by a
different mechanism:

  * Python files are tokenized with the standard `tokenize` module, so comments and string
    literals are identified structurally rather than by a line prefix;
  * JSON files are parsed and walked as a tree, so the declaration exemption is decided by the
    key a value hangs under rather than by a line pattern;
  * matching is set intersection over extracted word tokens and over whole parsed strings,
    rather than line-by-line regular expressions.

Counts that depend on how a line is split are not in the agreement set; the distinct
`(package, file, pattern)` triples are.

    python3 -I -B  independent_oracle_v1.py
"""

import io
import json
import os
import re
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RESEARCH = os.path.join(REPO, "research")

BENCHMARK_PKG = "gmi-833-aj9a-known-family-benchmark-v1"
BENCHMARK_FILE = "KNOWN_FAMILY_BENCHMARK_V1.json"
BENCHMARK_BLOB = "6b9ac3095c90d74e2717671a70ad7cc18955310c"

HOLDOUTS = ("gmi-833-aj9b-k01-blind-recovery-v1",
            "gmi-833-aj9c-k02-blind-recovery-v1",
            "gmi-833-aj9d-k03-blind-recovery-v1",
            "gmi-833-aj9e-k04-blind-recovery-v1",
            "gmi-833-aj9f-k05-blind-recovery-v1",
            "gmi-833-aj9g-k06-blind-recovery-v1",
            "gmi-833-aj9h-k07-k11-blind-recovery-v1")

DECLARATION_KEYS = ("forbidden", "hidden_from_generator", "hidden_from_search",
                    "hidden_from_evaluator", "no_family_score",
                    "meaning_hidden_from_search",
                    "benchmark_blob_required_after_generation_only")

GENERIC_TOKENS = frozenset((
    "control", "memory", "search", "population", "planning", "local", "shared",
    "transform", "stateful", "probabilistic", "developmental", "rewrite", "routing",
    "dynamic", "program", "synthesis", "forward", "feed", "self", "modifying"))


def vocabulary():
    reg = json.load(open(os.path.join(RESEARCH, BENCHMARK_PKG, BENCHMARK_FILE)))
    ids = set()
    names = set()
    toks = set()
    clauses = set()
    anchors = set()
    for fam in reg["families"]:
        ids.add(fam["family_id"])
        names.add(fam["paper_name"])
        for t in re.split(r"[^A-Za-z]+", fam["paper_name"]):
            if len(t) >= 4:
                toks.add(t.lower())
        fp = fam.get("posthoc_fingerprint", {})
        for c in fp.get("required", ()):
            clauses.add(c)
        if fp.get("learning_extension"):
            clauses.add(fp["learning_extension"])
        for c in fam.get("exclusions_near_neighbors", ()):
            clauses.add(c)
        for c in fam.get("minimum_observation_tests", ()):
            clauses.add(c)
        for a in fam.get("parent_anchors", ()):
            anchors.add(a)
    return {"ids": ids, "names": names, "tokens": toks, "clauses": clauses,
            "anchors": anchors,
            "multiword": set(n for n in names if re.search(r"[ /-]", n))}


def word_tokens(text):
    return set(t.lower() for t in re.split(r"[^A-Za-z0-9]+", text) if t)


def hits_in_string(s, vocab):
    """Every vocabulary element present in one string, as `(class, pattern)` pairs."""
    out = set()
    low = s.lower()
    words = word_tokens(s)
    for fid in vocab["ids"]:
        if fid.lower() in words:
            out.add(("FAMILY_ID", fid))
    for nm in vocab["multiword"]:
        if nm.lower() in low:
            out.add(("PAPER_NAME", nm))
    for t in vocab["tokens"]:
        if t in words:
            out.add(("NAME_TOKEN", t))
    for c in vocab["clauses"]:
        if c.lower()[:30] in low:
            out.add(("CLAUSE", c[:60]))
    for a in vocab["anchors"]:
        if a.lower() in low:
            out.add(("PARENT_ANCHOR", a))
    if BENCHMARK_BLOB in s or BENCHMARK_FILE in s:
        out.add(("BENCHMARK_REFERENCE", BENCHMARK_FILE))
    return out


def walk_json(node, vocab, exempt_key=False):
    """Returns `(violations, review, exemptions)` as sets of `(class, pattern)`."""
    v, r, e = set(), set(), set()
    if isinstance(node, dict):
        for k, val in node.items():
            sub_exempt = exempt_key or (k in DECLARATION_KEYS)
            kv, kr, ke = walk_json(k, vocab, sub_exempt)
            v |= kv
            r |= kr
            e |= ke
            vv, rr, ee = walk_json(val, vocab, sub_exempt)
            v |= vv
            r |= rr
            e |= ee
    elif isinstance(node, list):
        for item in node:
            vv, rr, ee = walk_json(item, vocab, exempt_key)
            v |= vv
            r |= rr
            e |= ee
    elif isinstance(node, str):
        for cls, pat in hits_in_string(node, vocab):
            if exempt_key:
                e.add((cls, pat))
            elif cls == "NAME_TOKEN" and pat in GENERIC_TOKENS:
                r.add((cls, pat))
            else:
                v.add((cls, pat))
    return v, r, e


def scan_python(text, vocab):
    v, r, e = set(), set(), set()
    pieces = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            kind = tok[0]
            val = tok[1]
            is_prose = kind in (tokenize.COMMENT, tokenize.STRING)
            pieces.append((val, is_prose))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pieces = [(text, False)]
    for val, is_prose in pieces:
        declaring = False
        if is_prose:
            low = val.lower()
            declaring = ("forbid" in low or "hidden" in low or "must not" in low
                         or "never" in low or "no family" in low)
        for cls, pat in hits_in_string(val, vocab):
            if declaring:
                e.add((cls, pat))
            elif cls == "NAME_TOKEN" and pat in GENERIC_TOKENS:
                r.add((cls, pat))
            else:
                v.add((cls, pat))
    return v, r, e


def is_blind(n):
    return n.startswith("blind_") or n in ("SEARCH_CONFIG_V1.json", "BLIND_OUTCOME_V1.json")


def is_posthoc(n):
    return (n.startswith("posthoc_") or n.startswith("check_aj9")
            or n == "POSTHOC_RESULT_V1.json")


def scan_file(path, name, vocab):
    text = open(path, "rb").read().decode("utf-8", "replace")
    if name.endswith(".json"):
        try:
            return walk_json(json.loads(text), vocab)
        except ValueError:
            return scan_python(text, vocab)
    return scan_python(text, vocab)


def audit(vocab):
    violations = set()
    review = set()
    exemptions = set()
    control = 0
    blind_files = 0
    posthoc_files = 0
    gaps = []
    for pkg in HOLDOUTS:
        d = os.path.join(RESEARCH, pkg)
        if not os.path.isdir(d):
            gaps.append({"package": pkg, "gap": "PACKAGE_MISSING"})
            continue
        names = sorted(os.listdir(d))
        if not any(is_blind(n) for n in names):
            gaps.append({"package": pkg, "gap": "NO_BLIND_ARTIFACT_MATCHED"})
        if not any(n.startswith("blind_") for n in names):
            gaps.append({"package": pkg, "gap": "NO_BLIND_SOURCE_FILE"})
        if "FREEZE_V1.md" not in names:
            gaps.append({"package": pkg, "gap": "NO_FREEZE_FILE"})
        if not any(is_posthoc(n) for n in names):
            gaps.append({"package": pkg, "gap": "NO_POSTHOC_ARTIFACT"})
        for n in names:
            p = os.path.join(d, n)
            if not os.path.isfile(p):
                continue
            if is_blind(n):
                blind_files += 1
                v, r, e = scan_file(p, n, vocab)
                violations |= set((pkg, n, c, pat) for c, pat in v)
                review |= set((pkg, n, c, pat) for c, pat in r)
                exemptions |= set((pkg, n, c, pat) for c, pat in e)
            elif is_posthoc(n):
                posthoc_files += 1
                v, r, e = scan_file(p, n, vocab)
                control += len(v) + len(r) + len(e)
    return {"violations": sorted(violations), "review": sorted(review),
            "exemptions": sorted(exemptions), "control_family_hits_in_posthoc": control,
            "blind_files_scanned": blind_files, "posthoc_files_scanned": posthoc_files,
            "coverage_gaps": gaps}


def planted(vocab):
    clause = sorted(vocab["clauses"])[0]
    anchor = sorted(vocab["anchors"])[0]
    plants = [
        ("benchmark_contents", "config = json.load(open('%s'))" % BENCHMARK_FILE),
        ("family_id", "TARGET_FAMILY = 'K01'"),
        ("paper_name", "MODE = 'neural/feed-forward'"),
        ("fingerprint_clause", "# require " + clause[:60]),
        ("target_property_vector", "TARGET_PROPERTIES = ['" + clause[:40] + "']"),
        ("family_specific_macro", "def attention_macro(x): return x"),
        ("family_cost_bonus", "COST_BONUS = {'K03': -2, 'K04': -1}"),
        ("parent_anchor_in_search", "# after " + anchor),
    ]
    out = []
    for name, line in plants:
        v, _r, _e = scan_python(line + "\n", vocab)
        out.append({"class": name, "detected": len(v) > 0})
    return out


def canonical_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True, separators=(",", ": "))


def main():
    vocab = vocabulary()
    res = audit(vocab)
    rec = planted(vocab)
    return {"schema": "GMI833AJ9HoldoutSourceAuditOracleV1",
            "route": "B",
            "imports_route_a": False,
            "violation_count": len(res["violations"]),
            "violations": res["violations"],
            "review_triples": sorted(set((p, f, pat) for p, f, _c, pat in res["review"])),
            "review_triple_count": len(set((p, f, pat) for p, f, _c, pat in res["review"])),
            "exemption_triples": sorted(set((p, f, pat) for p, f, _c, pat in res["exemptions"])),
            "control_family_hits_in_posthoc": res["control_family_hits_in_posthoc"],
            "blind_files_scanned": res["blind_files_scanned"],
            "posthoc_files_scanned": res["posthoc_files_scanned"],
            "coverage_gaps": res["coverage_gaps"],
            "planted_positive_recall": rec,
            "planted_positives_detected": sum(1 for p in rec if p["detected"])}


if __name__ == "__main__":
    r = main()
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        fh.write(canonical_json(r) + "\n")
    print(canonical_json({"route": "B", "violation_count": r["violation_count"],
                          "review_triple_count": r["review_triple_count"],
                          "control_family_hits_in_posthoc":
                              r["control_family_hits_in_posthoc"],
                          "planted_positives_detected": r["planted_positives_detected"],
                          "coverage_gaps": r["coverage_gaps"]}))
