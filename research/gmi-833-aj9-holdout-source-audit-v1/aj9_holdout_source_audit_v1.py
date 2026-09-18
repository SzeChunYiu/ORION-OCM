# -*- coding: utf-8 -*-
"""AJ9 route A -- audit every holdout's blind artifacts against the frozen forbidden list.

The eight forbidden classes and the whole search vocabulary are derived from the merged
`gmi-833-aj9a-known-family-benchmark-v1` registry, pinned by blob.  Nothing about which words
count as a family name is authored here.

The scan is validated before any absence is reported: a control pass must find family
vocabulary in the post-hoc artifacts, where it is allowed to be, and a planted positive for
each of the eight classes must be detected.

    python3 -I -B  aj9_holdout_source_audit_v1.py
"""

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RESEARCH = os.path.join(REPO, "research")

SOURCE_MAIN = "5e57d4292266bccf435136e1f7d72caa32e920a0"
CLAIM_CEILING = "AJ9_HOLDOUT_BLIND_SOURCE_AUDITED_AGAINST_THE_FROZEN_FORBIDDEN_INPUT_LIST"
FORBIDDEN_PROMOTIONS = ("ALL_HOLDOUTS_PROVEN_BLIND", "BLIND_SEARCH_IS_UNBIASED",
                        "NO_LEAKAGE_OF_ANY_KIND", "RECOVERY_IS_CONFIRMED_BY_THIS_AUDIT",
                        "COMPLETE_GMI")

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

# A word that also occurs in ordinary technical prose.  Reported, never gated on.
GENERIC_TOKENS = frozenset((
    "control", "memory", "search", "population", "planning", "local", "shared",
    "transform", "stateful", "probabilistic", "developmental", "rewrite", "routing",
    "dynamic", "program", "synthesis", "forward", "feed", "self", "modifying"))


def blob_sha(path):
    with open(path, "rb") as fh:
        data = fh.read()
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\x00")
    h.update(data)
    return h.hexdigest()


# --------------------------------------------------------------------------------------
# 1.  Vocabulary, derived from the frozen registry.
# --------------------------------------------------------------------------------------

def build_vocabulary():
    path = os.path.join(RESEARCH, BENCHMARK_PKG, BENCHMARK_FILE)
    sha = blob_sha(path)
    reg = json.load(open(path))
    ids = []
    names = []
    name_tokens = set()
    fingerprints = []
    exclusions = []
    observations = []
    anchors = []
    for fam in reg["families"]:
        ids.append(fam["family_id"])
        names.append(fam["paper_name"])
        for tok in re.split(r"[^A-Za-z]+", fam["paper_name"]):
            if len(tok) >= 4:
                name_tokens.add(tok.lower())
        fp = fam.get("posthoc_fingerprint", {})
        for clause in fp.get("required", ()):
            fingerprints.append(clause)
        if fp.get("learning_extension"):
            fingerprints.append(fp["learning_extension"])
        exclusions.extend(fam.get("exclusions_near_neighbors", ()))
        observations.extend(fam.get("minimum_observation_tests", ()))
        anchors.extend(fam.get("parent_anchors", ()))
    multiword = sorted(set(n for n in names if re.search(r"[ /-]", n)))
    return {"benchmark_blob": sha, "benchmark_blob_pinned": BENCHMARK_BLOB,
            "blob_matches_pin": sha == BENCHMARK_BLOB,
            "family_ids": sorted(set(ids)),
            "paper_names": sorted(set(names)),
            "multiword_names": multiword,
            "name_tokens": sorted(name_tokens),
            "fingerprint_clauses": sorted(set(fingerprints)),
            "exclusion_clauses": sorted(set(exclusions)),
            "observation_clauses": sorted(set(observations)),
            "parent_anchors": sorted(set(anchors))}


# --------------------------------------------------------------------------------------
# 2.  Declaration exemption.
# --------------------------------------------------------------------------------------

def declaration_spans(name, text):
    """Line numbers whose content is a holdout's own statement of what it forbids."""
    spans = set()
    lines = text.split("\n")
    if name.endswith(".json"):
        key_re = re.compile(r'"(' + "|".join(DECLARATION_KEYS) + r')"\s*:')
        depth_start = None
        for k, line in enumerate(lines, 1):
            if key_re.search(line):
                spans.add(k)
                if "[" in line and "]" not in line:
                    depth_start = k
            elif depth_start is not None:
                spans.add(k)
                if "]" in line:
                    depth_start = None
    else:
        for k, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith("#") or s.startswith('"""') or s.startswith("'''"):
                low = s.lower()
                if ("forbid" in low or "hidden" in low or "must not" in low
                        or "never" in low or "no family" in low):
                    spans.add(k)
    return spans


# --------------------------------------------------------------------------------------
# 3.  The scan.
# --------------------------------------------------------------------------------------

def scan_text(name, text, vocab):
    exempt = declaration_spans(name, text)
    lines = text.split("\n")
    violations = []
    review = []
    exemptions = []

    def add(kind, pattern, k, line, generic=False):
        rec = {"class": kind, "pattern": pattern, "line": k,
               "text": line.strip()[:160]}
        if k in exempt:
            exemptions.append(rec)
        elif generic:
            review.append(rec)
        else:
            violations.append(rec)

    for k, line in enumerate(lines, 1):
        low = line.lower()
        for fid in vocab["family_ids"]:
            # `_` is a word character, so \b would miss `attention_macro`.  Alphabetic
            # boundaries are used instead; the planted-positive test caught this.
            if re.search(r"(?<![A-Za-z0-9])" + re.escape(fid) + r"(?![A-Za-z0-9])", line):
                add("FAMILY_ID", fid, k, line)
        for nm in vocab["multiword_names"]:
            if nm.lower() in low:
                add("PAPER_NAME", nm, k, line)
        for tok in vocab["name_tokens"]:
            if re.search(r"(?<![a-z0-9])" + re.escape(tok) + r"(?![a-z0-9])", low):
                add("NAME_TOKEN", tok, k, line, generic=(tok in GENERIC_TOKENS))
        for clause in vocab["fingerprint_clauses"]:
            if clause.lower()[:40] in low:
                add("FINGERPRINT_CLAUSE", clause[:60], k, line)
        for clause in vocab["exclusion_clauses"]:
            if clause.lower()[:30] in low:
                add("EXCLUSION_CLAUSE", clause[:60], k, line)
        for clause in vocab["observation_clauses"]:
            if clause.lower()[:30] in low:
                add("OBSERVATION_CLAUSE", clause[:60], k, line)
        for anchor in vocab["parent_anchors"]:
            if anchor.lower() in low:
                add("PARENT_ANCHOR", anchor, k, line)
        if BENCHMARK_BLOB in line or BENCHMARK_FILE in line:
            add("BENCHMARK_REFERENCE", BENCHMARK_FILE, k, line)
    return violations, review, exemptions


def is_blind(name):
    return (name.startswith("blind_") or name == "SEARCH_CONFIG_V1.json"
            or name == "BLIND_OUTCOME_V1.json")


def is_posthoc(name):
    return (name.startswith("posthoc_") or name.startswith("check_aj9")
            or name == "POSTHOC_RESULT_V1.json")


def audit(vocab):
    per_holdout = {}
    total_violations = 0
    total_review = 0
    control_hits = 0
    coverage_gaps = []
    blind_files = 0
    posthoc_files = 0
    for pkg in HOLDOUTS:
        d = os.path.join(RESEARCH, pkg)
        if not os.path.isdir(d):
            coverage_gaps.append({"package": pkg, "gap": "PACKAGE_MISSING"})
            continue
        names = sorted(os.listdir(d))
        blind = [n for n in names if is_blind(n)]
        posthoc = [n for n in names if is_posthoc(n)]
        if not blind:
            coverage_gaps.append({"package": pkg, "gap": "NO_BLIND_ARTIFACT_MATCHED"})
        if not any(n.startswith("blind_") for n in names):
            coverage_gaps.append({"package": pkg, "gap": "NO_BLIND_SOURCE_FILE"})
        if "FREEZE_V1.md" not in names:
            coverage_gaps.append({"package": pkg, "gap": "NO_FREEZE_FILE"})
        if not posthoc:
            coverage_gaps.append({"package": pkg, "gap": "NO_POSTHOC_ARTIFACT"})
        entry = {"blind_artifacts": blind, "posthoc_artifacts": posthoc,
                 "violations": [], "review": [], "exemptions": [],
                 "control_family_hits_in_posthoc": 0}
        for n in blind:
            blind_files += 1
            text = open(os.path.join(d, n), "rb").read().decode("utf-8", "replace")
            v, r, e = scan_text(n, text, vocab)
            for rec in v:
                rec["file"] = n
            for rec in r:
                rec["file"] = n
            for rec in e:
                rec["file"] = n
            entry["violations"].extend(v)
            entry["review"].extend(r)
            entry["exemptions"].extend(e)
        for n in posthoc:
            posthoc_files += 1
            text = open(os.path.join(d, n), "rb").read().decode("utf-8", "replace")
            v, r, e = scan_text(n, text, vocab)
            entry["control_family_hits_in_posthoc"] += len(v) + len(r) + len(e)
        control_hits += entry["control_family_hits_in_posthoc"]
        total_violations += len(entry["violations"])
        total_review += len(entry["review"])
        per_holdout[pkg] = entry
    return {"per_holdout": per_holdout, "violations": total_violations,
            "review": total_review, "control_family_hits_in_posthoc": control_hits,
            "coverage_gaps": coverage_gaps,
            "blind_files_scanned": blind_files,
            "posthoc_files_scanned": posthoc_files}


# --------------------------------------------------------------------------------------
# 4.  Recall: one planted positive per forbidden class.
# --------------------------------------------------------------------------------------

def planted_positives(vocab):
    plants = [
        ("benchmark_contents", "config = json.load(open('%s'))" % BENCHMARK_FILE),
        ("family_id", "TARGET_FAMILY = 'K01'"),
        ("paper_name", "MODE = 'neural/feed-forward'"),
        ("fingerprint_clause",
         "# require " + vocab["fingerprint_clauses"][0][:60]),
        ("target_property_vector",
         "TARGET_PROPERTIES = ['" + vocab["observation_clauses"][0][:40] + "']"),
        ("family_specific_macro", "def attention_macro(x): return x"),
        ("family_cost_bonus", "COST_BONUS = {'K03': -2, 'K04': -1}"),
        ("parent_anchor_in_search", "# after " + vocab["parent_anchors"][0]),
    ]
    out = []
    for name, line in plants:
        v, r, e = scan_text("blind_planted_v1.py", line + "\n", vocab)
        out.append({"class": name, "detected": len(v) > 0,
                    "hit_classes": sorted(set(x["class"] for x in v)),
                    "review_only": len(v) == 0 and len(r) > 0})
    return out


def no_alarm(vocab):
    """The unmodified blind artifacts must raise nothing that gates."""
    res = audit(vocab)
    return {"violations": res["violations"],
            "blind_files_scanned": res["blind_files_scanned"]}


def canonical_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True, separators=(",", ": "))


def main():
    vocab = build_vocabulary()
    res = audit(vocab)
    recall = planted_positives(vocab)
    quiet = no_alarm(vocab)

    failed = []
    if not vocab["blob_matches_pin"]:
        failed.append("GATE_BENCHMARK_BLOB_DRIFT")
    if res["violations"]:
        failed.append("GATE_BLIND_ARTIFACT_VIOLATION")
    if res["control_family_hits_in_posthoc"] == 0:
        failed.append("GATE_SCAN_NOT_PROVEN_TO_WORK")
    missed = [p["class"] for p in recall if not p["detected"]]
    if missed:
        failed.append("GATE_PLANTED_POSITIVE_MISSED:" + ",".join(missed))
    if quiet["violations"]:
        failed.append("GATE_NO_ALARM_VIOLATED")
    if res["blind_files_scanned"] < 3 * len(HOLDOUTS) - 2:
        failed.append("GATE_BLIND_COVERAGE_TOO_LOW")

    receipt = {
        "schema": "GMI833AJ9HoldoutSourceAuditReceiptV1",
        "package": "gmi-833-aj9-holdout-source-audit-v1",
        "issue": 833,
        "section": "AJ9",
        "source_main": SOURCE_MAIN,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "forbidden_input_classes_source":
            "gmi-833-aj9a-known-family-benchmark-v1/HOLDOUT_CONTRACT_V1.json"
            " forbidden_generator_inputs",
        "vocabulary": {"benchmark_blob": vocab["benchmark_blob"],
                       "blob_matches_pin": vocab["blob_matches_pin"],
                       "family_ids": len(vocab["family_ids"]),
                       "paper_names": len(vocab["paper_names"]),
                       "multiword_names": len(vocab["multiword_names"]),
                       "name_tokens": len(vocab["name_tokens"]),
                       "fingerprint_clauses": len(vocab["fingerprint_clauses"]),
                       "exclusion_clauses": len(vocab["exclusion_clauses"]),
                       "observation_clauses": len(vocab["observation_clauses"]),
                       "parent_anchors": len(vocab["parent_anchors"])},
        "holdouts_audited": len(HOLDOUTS),
        "blind_files_scanned": res["blind_files_scanned"],
        "posthoc_files_scanned": res["posthoc_files_scanned"],
        "violations": res["violations"],
        "review_hits": res["review"],
        "control_family_hits_in_posthoc": res["control_family_hits_in_posthoc"],
        "coverage_gaps": res["coverage_gaps"],
        "per_holdout": res["per_holdout"],
        "planted_positive_recall": recall,
        "planted_positives_detected": sum(1 for p in recall if p["detected"]),
        "planted_positives_declared": len(recall),
        "no_alarm": quiet,
        "failed_gates": failed,
        "status": "GREEN" if not failed else "RED",
    }
    return receipt


if __name__ == "__main__":
    r = main()
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        fh.write(canonical_json(r) + "\n")
    print(canonical_json({"status": r["status"], "failed_gates": r["failed_gates"],
                          "violations": r["violations"],
                          "review_hits": r["review_hits"],
                          "control_family_hits_in_posthoc":
                              r["control_family_hits_in_posthoc"],
                          "planted_positives_detected": r["planted_positives_detected"],
                          "coverage_gaps": r["coverage_gaps"]}))
