# -*- coding: utf-8 -*-
"""AJ15 flagship experiment -- POST-HOC stage (route A).

Runs only after BLIND_OUTCOME_V1.json exists (custody: the registry is read here and
nowhere else in this package).  For every exact solver of the blind run it applies the
frozen AJ9a fingerprints at this scope, keeps the UNKNOWN channel live for solvers that
match no registered fingerprint, runs strongest-parent review afterwards, checks the
post-hoc outcome per regime against the frozen prediction table, and audits the blind
artifacts for registry vocabulary with a scanner validated by a control scan and eight
planted positives (one per forbidden class).  Hostiles H1, H2, H8.

    python3 -I -B posthoc_adjudicate_v1.py [--blind BLIND_OUTCOME_V1.json] [--out POSTHOC_RESULT_V1.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

def _read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_text(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

REPO = os.path.dirname(os.path.dirname(HERE))
REGISTRY = os.path.join(REPO, "research", "gmi-833-aj9a-known-family-benchmark-v1", "KNOWN_FAMILY_BENCHMARK_V1.json")
REGISTRY_BLOB = "6b9ac3095c90d74e2717671a70ad7cc18955310c"
BLIND_FILES = ("aj15_flagship_v1.py", "independent_oracle_v1.py", "SEARCH_CONFIG_V1.json", "BLIND_OUTCOME_V1.json")
POSTHOC_FILES = ("posthoc_adjudicate_v1.py", "apply_aj13_aj14_v1.py", "independent_ladder_oracle_v1.py")
GENERIC_TOKENS = frozenset(("control", "memory", "search", "population", "planning", "local", "shared",
                            "transform", "stateful", "probabilistic", "developmental", "rewrite",
                            "routing", "dynamic", "program", "synthesis", "forward", "feed", "self",
                            "modifying"))
DECLARATION_KEYS = ("forbidden", "registry_access_during_generation_search_evaluation")


def blob_sha(path):
    data = _read_bytes(path)
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\x00")
    h.update(data)
    return h.hexdigest()


def sha256_file(path):
    return hashlib.sha256(_read_bytes(path)).hexdigest()


# --------------------------------------------------------------------------------------
# Machine reconstruction from the blind outcome's ids (B1) and tables (B2).
# --------------------------------------------------------------------------------------


def b1_machine(mid):
    k = int(mid[1:])
    if k < 4:
        o = ((k >> 1) & 1, k & 1)
        return {(0, 0): (0, o[0]), (0, 1): (0, o[1])}, 1
    bits = [int(c) for c in format(k - 4, "08b")]
    t = {}
    for s in (0, 1):
        for x in (0, 1):
            p = 4 * s + 2 * x
            t[(s, x)] = (bits[p], bits[p + 1])
    return t, 2


def b2_machine(rows):
    t = {}
    for s in range(4):
        for x in (0, 1):
            n, o = rows[s * 2 + x]
            t[(s, x)] = (int(n), int(o))
    return t, 4


def reachable(t):
    seen = {0}
    q = [0]
    while q:
        s = q.pop()
        for x in (0, 1):
            n = t[(s, x)][0]
            if n not in seen:
                seen.add(n)
                q.append(n)
    return sorted(seen)


def structural_facts(t, n_states):
    r = reachable(t)
    dep = any(len({t[(s, x)][1] for s in r}) > 1 for x in (0, 1))
    update = any(t[(s, x)][0] != s for s in r for x in (0, 1))
    return {"state_cells": 0 if n_states == 1 else (1 if n_states == 2 else 2),
            "reachable_states": len(r), "reachable_state_dependent_output": dep,
            "reachable_state_update": update}


# --------------------------------------------------------------------------------------
# Frozen fingerprints, instantiated at this scope.
# --------------------------------------------------------------------------------------


def k02_predicate(f, drop_clause_2=False):
    c1 = f["reachable_states"] >= 2          # persistent internal state survives between steps
    c2 = f["reachable_state_dependent_output"]  # prior reachable state changes a later output
    c3 = f["reachable_state_update"] and (c2 or drop_clause_2)  # state updated and fed forward
    if drop_clause_2:
        c2 = True
    excl_pure_map = not f["reachable_state_dependent_output"]  # exclusion: pure symbol map
    excl_write_only = f["reachable_state_update"] and not f["reachable_state_dependent_output"]
    if drop_clause_2:
        excl_pure_map = False
        excl_write_only = False
    return {"required": [c1, c2, c3], "excluded": excl_pure_map or excl_write_only,
            "passes": c1 and c2 and c3 and not (excl_pure_map or excl_write_only)}


NOT_DEFINABLE = {
    "K01": "no internal composition of aggregation sites exists in a step table",
    "K03": "no multiple sites over which a shared transform could be applied",
    "K04": "no multiple candidate sources with content-dependent weighting",
    "K05": "no compositional discrete expression state with rewrite steps",
    "K06": "no normalized probabilistic state object",
    "K07": "a fixed step table evaluates no future consequence before acting",
    "K08": "no multiple stored records selected by a query or content state",
    "K09": "a single step table is not a population of heritable descriptions",
    "K10": "the returned artifact is a step table, not an expression of a declared grammar",
    "K11": "the machine effects no persistent change to its own organization",
}


def adjudicate_solver(fam_ids, f, drop_clause_2=False):
    matches = []
    for fid in fam_ids:
        if fid == "K02":
            if k02_predicate(f, drop_clause_2)["passes"]:
                matches.append(fid)
    if matches:
        return {"registered_taxonomy": "KNOWN_REGISTERED_FAMILY", "registered_family": matches[0],
                "fingerprint_scope_note": "frozen fingerprint satisfied at this finite scope; family identity is not inferred from operational equivalence alone (FGS-4)",
                "strongest_parent_review": "finite deterministic transducer with causally used internal state (automata theory)",
                "novelty": {"implementation": "NOT_ESTABLISHED", "algorithmic_mechanism": "PARENT_REDUCED_KNOWN",
                            "computational_class": "PARENT_REDUCED_KNOWN", "capability_profile": "TASK_SPECIFIC_NOT_NOVEL"}}
    if f["reachable_states"] == 1 or f["state_cells"] == 0:
        parent = "literal one-symbol Boolean map or constant (truth table)"
    else:
        parent = "one-symbol Boolean map with an inert reachable internal state (non-minimal automaton presentation)"
    return {"registered_taxonomy": "UNKNOWN_MORPHOLOGY", "registered_family": None,
            "unknown_channel": True,
            "strongest_parent_review": parent, "post_parent_terminal": "PARENT_REDUCED_KNOWN",
            "novelty": {"implementation": "NOT_ESTABLISHED", "algorithmic_mechanism": "PARENT_REDUCED_KNOWN",
                        "computational_class": "PARENT_REDUCED_KNOWN", "capability_profile": "TASK_SPECIFIC_NOT_NOVEL"}}


# --------------------------------------------------------------------------------------
# Source audit: vocabulary derived from the registry blob, scanner validated first.
# --------------------------------------------------------------------------------------


def build_vocabulary(reg):
    ids, names, tokens, clauses, anchors = [], [], set(), [], []
    for fam in reg["families"]:
        ids.append(fam["family_id"])
        names.append(fam["paper_name"])
        for tok in re.split(r"[^A-Za-z]+", fam["paper_name"]):
            if len(tok) >= 4 and tok.lower() not in GENERIC_TOKENS:
                tokens.add(tok.lower())
        fp = fam["posthoc_fingerprint"]
        clauses.extend(("FINGERPRINT", c) for c in fp.get("required", []))
        if fp.get("learning_extension"):
            clauses.append(("FINGERPRINT", fp["learning_extension"]))
        clauses.extend(("EXCLUSION", c) for c in fam.get("exclusions_near_neighbors", []))
        clauses.extend(("OBSERVATION", c) for c in fam.get("minimum_observation_tests", []))
        anchors.extend(fam.get("parent_anchors", []))
    return {"ids": ids, "names": names, "tokens": sorted(tokens), "clauses": clauses,
            "anchors": anchors, "registry_names": ["KNOWN_FAMILY_BENCHMARK_V1", REGISTRY_BLOB]}


def declaration_lines(name, text):
    spans = set()
    if not name.endswith(".json"):
        return spans
    key_re = re.compile(r'"(' + "|".join(DECLARATION_KEYS) + r')"\s*:')
    inside = False
    for k, line in enumerate(text.split("\n"), 1):
        if key_re.search(line):
            spans.add(k)
            inside = "[" in line and "]" not in line
        elif inside:
            spans.add(k)
            if "]" in line:
                inside = False
    return spans


def scan_text(name, text, vocab):
    hits = []
    decl = declaration_lines(name, text)
    for k, line in enumerate(text.split("\n"), 1):
        if k in decl:
            continue
        low = line.lower()
        for fid in vocab["ids"]:
            if re.search(r"(?<![A-Za-z0-9])" + fid + r"(?![A-Za-z0-9])", line):
                hits.append(("FAMILY_ID", fid, k))
        for nm in vocab["names"]:
            if nm.lower() in low:
                hits.append(("FAMILY_NAME", nm, k))
        for tok in vocab["tokens"]:
            if re.search(r"(?<![a-z])" + re.escape(tok) + r"(?![a-z])", low):
                hits.append(("NAME_TOKEN", tok, k))
        for cls, c in vocab["clauses"]:
            if c.lower() in low:
                hits.append((cls + "_CLAUSE", c, k))
        for a in vocab["anchors"]:
            if a.lower() in low:
                hits.append(("PARENT_ANCHOR", a, k))
        for r in vocab["registry_names"]:
            if r.lower() in low:
                hits.append(("REGISTRY_REFERENCE", r, k))
    return hits


def source_audit(vocab):
    blind = {}
    for f in BLIND_FILES:
        p = os.path.join(HERE, f)
        blind[f] = scan_text(f, _read_text(p), vocab) if os.path.exists(p) else None
    control = {}
    for f in POSTHOC_FILES:
        p = os.path.join(HERE, f)
        control[f] = len(scan_text(f, _read_text(p), vocab)) if os.path.exists(p) else None
    # planted positives, one per forbidden class
    fam = None
    reg = _load_json(REGISTRY)
    for x in reg["families"]:
        if x["family_id"] == "K02":
            fam = x
    plants = {
        "FAMILY_ID": "target = 'K02'",
        "FAMILY_NAME": "label = '%s'" % fam["paper_name"],
        "NAME_TOKEN": "use the %s trick" % vocab["tokens"][0],
        "FINGERPRINT_CLAUSE": "# %s" % fam["posthoc_fingerprint"]["required"][0],
        "EXCLUSION_CLAUSE": "# %s" % fam["exclusions_near_neighbors"][0],
        "OBSERVATION_CLAUSE": "# %s" % fam["minimum_observation_tests"][0],
        "PARENT_ANCHOR": "# see %s" % fam["parent_anchors"][0],
        "REGISTRY_REFERENCE": "path = 'KNOWN_FAMILY_BENCHMARK_V1.json'",
    }
    base = _read_text(os.path.join(HERE, "aj15_flagship_v1.py"))
    recall = {}
    for cls, line in plants.items():
        hits = scan_text("planted.py", base + "\n" + line + "\n", vocab)
        recall[cls] = any(h[0] == cls for h in hits)
    total_blind = sum(len(v) for v in blind.values() if v is not None)
    return {"blind_files": {k: (len(v) if v is not None else None) for k, v in blind.items()},
            "blind_hits_detail": {k: v for k, v in blind.items() if v},
            "violations": total_blind,
            "control_posthoc_hits": control,
            "control_nonempty": sum(v for v in control.values() if v) > 0,
            "planted_positives": recall, "planted_recall": "%d/%d" % (sum(recall.values()), len(recall)),
            "vocabulary_sizes": {"ids": len(vocab["ids"]), "names": len(vocab["names"]),
                                 "tokens": len(vocab["tokens"]), "clauses": len(vocab["clauses"]),
                                 "anchors": len(vocab["anchors"])}}


# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------


def adjudicate(blind_path, drop_clause_2=False):
    if not os.path.exists(blind_path):
        raise RuntimeError("CUSTODY: blind outcome %s does not exist; the registry may not be read" % blind_path)
    blind = _load_json(blind_path)
    blind_sha = sha256_file(blind_path)
    assert blob_sha(REGISTRY) == REGISTRY_BLOB, "registry blob drift"
    reg = _load_json(REGISTRY)
    fam_ids = [f["family_id"] for f in reg["families"]]
    assert len(fam_ids) == 11
    preds = _load_json(os.path.join(HERE, "SEARCH_CONFIG_V1.json"))["regime_predictions_operational_vocabulary"]

    per_regime = {}
    for t, r in blind["B1"]["regimes"].items():
        rows = {}
        for mid in r["exact_solver_ids"]:
            table, n = b1_machine(mid)
            f = structural_facts(table, n)
            rows[mid] = adjudicate_solver(fam_ids, f, drop_clause_2)
            rows[mid]["facts"] = f
        k02 = sum(1 for v in rows.values() if v["registered_family"] == "K02")
        unknown = sum(1 for v in rows.values() if v["registered_family"] is None)
        reduced = sum(1 for v in rows.values() if v.get("post_parent_terminal") == "PARENT_REDUCED_KNOWN")
        want_none = preds["B1"][t]["predicted_exact_solvers_with_state_dependent_output"] == "NONE"
        agree = (k02 == 0) if want_none else (k02 == len(rows) and len(rows) > 0)
        per_regime[t] = {"exact_solvers": len(rows), "K02_fingerprint_passes": k02,
                         "unknown_channel": unknown, "unknown_parent_reduced": reduced,
                         "novel_claimed": 0, "prediction_agreement": agree, "solvers": rows}
    b2 = {}
    for t, r in blind["B2"]["regimes"].items():
        if r["machine"] is None:
            b2[t] = {"terminal": r["terminal"], "adjudication": "NOT_APPLICABLE_NO_SOLVER"}
            continue
        table, n = b2_machine(r["machine"])
        f = structural_facts(table, n)
        a = adjudicate_solver(fam_ids, f, drop_clause_2)
        a["facts"] = f
        want_all = preds["B2"][t]["predicted_state_dependent_output"] == "ALL"
        b2[t] = {"terminal": r["terminal"], "adjudication": a,
                 "prediction_agreement": (a["registered_family"] == "K02") == want_all}
    vocab = build_vocabulary(reg)
    audit = source_audit(vocab)

    # hostiles owned by this stage
    hostiles = {}
    planted_cfg = _read_text(os.path.join(HERE, "SEARCH_CONFIG_V1.json")).replace(
        '"schema": "AJ15_FLAGSHIP_SEARCH_CONFIG_V1"', '"schema": "AJ15_FLAGSHIP_SEARCH_CONFIG_V1", "target_label": "%s"' % vocab["names"][1])
    h1 = scan_text("SEARCH_CONFIG_V1.json", planted_cfg, vocab)
    hostiles["H1"] = {"planted": "family name planted into a copy of SEARCH_CONFIG_V1.json",
                      "applicable": audit["violations"] == 0, "detected": len(h1) >= 1,
                      "violations_under_hostile": len(h1)}
    if not drop_clause_2:
        alt = adjudicate(blind_path, drop_clause_2=True)
        hostiles["H2"] = {"planted": "reachable-state clause dropped from the K02 fingerprint",
                          "applicable": alt["per_regime"]["identity"]["K02_fingerprint_passes"] != per_regime["identity"]["K02_fingerprint_passes"],
                          "detected": alt["per_regime"]["identity"]["K02_fingerprint_passes"] > 0 and not alt["per_regime"]["identity"]["prediction_agreement"],
                          "identity_passes_under_hostile": alt["per_regime"]["identity"]["K02_fingerprint_passes"]}
        try:
            adjudicate(os.path.join(HERE, "DOES_NOT_EXIST.json"))
            refused = False
        except RuntimeError:
            refused = True
        hostiles["H8"] = {"planted": "adjudication requested before any blind outcome exists",
                          "applicable": True, "detected": refused}
    all_agree = all(v["prediction_agreement"] for v in per_regime.values()) and \
        all(v.get("prediction_agreement", True) for v in b2.values())
    problems = []
    if not all_agree:
        problems.append("post-hoc outcome contradicts the frozen prediction table")
    if audit["violations"] != 0:
        problems.append("blind source carries registry vocabulary")
    if not audit["control_nonempty"] or audit["planted_recall"] != "8/8":
        problems.append("scanner not validated")
    for hid, h in hostiles.items():
        if not h["applicable"] or not h["detected"]:
            problems.append("hostile %s vacuous or undetected" % hid)
    return {"schema": "AJ15_POSTHOC_RESULT_V1", "stage": "POSTHOC",
            "adjudication_started_after_blind_outcome": True,
            "blind_outcome_sha256": blind_sha, "registry_blob": REGISTRY_BLOB,
            "registry_role": "POSTHOC_ADJUDICATOR_ONLY", "families_in_registry": fam_ids,
            "fingerprints_definable_at_scope": ["K02"],
            "fingerprints_not_definable_at_scope": NOT_DEFINABLE,
            "per_regime": per_regime, "B2": b2,
            "regime_outcome_vector_B1": {t: v["K02_fingerprint_passes"] > 0 for t, v in per_regime.items()},
            "posthoc_agrees_with_frozen_prediction": all_agree,
            "unknown_channel_exercised": any(v["unknown_channel"] > 0 for v in per_regime.values()),
            "novel_form_claimed": False,
            "novel_replication_gate": "NOT_TRIGGERED_NO_NOVEL_CLAIM",
            "source_audit": audit, "hostiles": hostiles, "problems": problems,
            "status": "GREEN" if not problems else "RED"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind", default=os.path.join(HERE, "BLIND_OUTCOME_V1.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "POSTHOC_RESULT_V1.json"))
    args = ap.parse_args(argv)
    out = adjudicate(args.blind)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"status": out["status"], "problems": out["problems"],
                      "B1": {t: (v["K02_fingerprint_passes"], v["unknown_channel"], v["exact_solvers"]) for t, v in out["per_regime"].items()},
                      "B2": {t: (v["terminal"], (v["adjudication"]["registered_family"] if isinstance(v["adjudication"], dict) else v["adjudication"])) for t, v in out["B2"].items()},
                      "audit": (out["source_audit"]["violations"], out["source_audit"]["planted_recall"], out["source_audit"]["control_posthoc_hits"]),
                      "hostiles": {k: (v["applicable"], v["detected"]) for k, v in out["hostiles"].items()}}, sort_keys=True))
    return 0 if out["status"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
