#!/usr/bin/env python3
"""Route B - independent oracle for the census registration pass.

Imports NOTHING from registration_pass_v1.py.  Re-derives every set the
receipt reports from the same frozen inputs by different mechanics:
  * identity tables built in one linear pass keyed by (package, object_id),
    rather than per-row candidate filtering;
  * result-id forms recognised by splitting on '_' rather than by prefix tuples;
  * citations parsed by a regular expression rather than partition();
  * descendants closed by fixed-point iteration rather than depth-first search;
  * materiality graded through a 256-entry lookup table rather than
    sum-and-bucket.
Agreement with route A is checked by SET EQUALITY in check_receipt_v1.py and
the tests.  Stdlib only; Python 3.8 compatible; int / Fraction only.
"""
from __future__ import annotations

import json
import re
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
P_CENSUS = REPO / "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json"
P_GAPS = REPO / "research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json"
P_SCORES = REPO / "research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json"
P_DELTA = REPO / "research/gmi-833-maturity-rescore-v3-w4-v1/SCORES_V3_DELTA.json"
P_REGS = REPO / "research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json"
P_DEP = REPO / "research/gmi-833-depgraph-adjudication-v1/DEPENDENCY_GRAPH_V2.json"
P_SCHEMA = REPO / "research/gmi-833-aa-gap-object-v1/OPEN_GAP_SCHEMA_V1.json"

LEGACY = re.compile(r"^GMI833_V2_LEGACY_[0-9]{3}_(.*)$")
CIT = re.compile(r"^(\S+?):(L[0-9]+)")
LEDGERS = ("assumptions", "falsifiers", "forbidden_extrapolations", "strongest_parents")
STAT = frozenset(["STATISTICAL_EXPERIMENT", "EMPIRICAL_EXPERIMENT"])


def rd(p):
    with open(str(p), encoding="utf-8") as fh:
        return json.load(fh)


def is_package_level(rid):
    parts = rid.split("_")
    if len(parts) < 3 or parts[0] != "GMI833":
        return False
    if parts[1] in ("V2", "V3") and parts[2] == "ARRIVAL":
        return True
    if parts[1] == "RESCORE":
        return True
    if parts[1] == "CD" and parts[2] == "NEW":
        return True
    return False


def derive(census=None, gaps=None, scores=None, delta=None, regs=None, dep=None, schema=None):
    census = rd(P_CENSUS) if census is None else census
    gaps = rd(P_GAPS) if gaps is None else gaps
    scores = rd(P_SCORES) if scores is None else scores
    delta = rd(P_DELTA) if delta is None else delta
    regs = rd(P_REGS) if regs is None else regs
    dep = rd(P_DEP) if dep is None else dep
    schema = rd(P_SCHEMA) if schema is None else schema

    # ---- identity tables, one linear pass
    expl = {}          # (package, oid) -> [key]
    by_id = {}         # oid -> [(key, path, loc)]
    meta = {}          # key -> (oid, mode, cls, path)
    n = 0
    for o in census["scientific_objects"]:
        n += 1
        key = o["source_path"] + ":" + o["source_locator"]
        if key in meta:
            raise RuntimeError("duplicate key " + key)
        pkg = o["source_path"].split("/")[1]
        meta[key] = (o["object_id"], o["proof_evidence_mode"], o["object_class"], o["source_path"])
        by_id.setdefault(o["object_id"], []).append((key, o["source_path"], o["source_locator"]))
        if o["id_kind"] == "EXPLICIT":
            expl.setdefault((pkg, o["object_id"]), []).append(key)

    # ---- binding
    bound = {}
    rules = {}
    refused_rows = []
    pkg_level = []
    used = set()
    for r in scores:
        rid = r["result_id"]
        if is_package_level(rid):
            pkg_level.append(rid)
            continue
        m = LEGACY.match(rid)
        if not m:
            refused_rows.append((rid, "FORM"))
            continue
        c = expl.get((r["package"], m.group(1)), [])
        rule = "B1_RESULT_ID_SUFFIX_EXACT"
        if len(c) != 1:
            if len(c) > 1:
                refused_rows.append((rid, "B1_AMBIGUOUS"))
                continue
            name = (r.get("theorem_name") or "").strip()
            c = expl.get((r["package"], name), []) if name else []
            rule = "B2_THEOREM_NAME_ID_EXACT"
            if len(c) != 1:
                refused_rows.append((rid, "NONE" if not c else "B2_AMBIGUOUS"))
                continue
        if c[0] in used:
            refused_rows.append((rid, "ALREADY_BOUND"))
            continue
        used.add(c[0])
        bound[rid] = c[0]
        rules[rid] = rule
    level = {}   # key -> (M, EV)
    for r in scores:
        if r["result_id"] in bound:
            level[bound[r["result_id"]]] = (r["maturity_M"], r["evidence_EV"])
    v2_ids = set(r["result_id"] for r in scores)
    delta_applied = []
    delta_refused = []
    for d in delta["records"]:
        if d["result_id"] in bound:
            level[bound[d["result_id"]]] = (d["maturity_M"], d["evidence_EV"])
            delta_applied.append(d["result_id"])
        elif d["result_id"] not in v2_ids and not is_package_level(d["result_id"]):
            delta_refused.append(d["result_id"])

    # ---- registrations
    ledger = {}   # (key, field) -> tuple(content)
    regs_bound = 0
    for r in regs["objects"]:
        k = bound.get(r["result_id"])
        if k is None:
            continue
        regs_bound += 1
        for f in LEDGERS + ("scope_quantifiers",):
            ledger[(k, f)] = tuple(r["fields"][f]["content"])

    # ---- edges
    seen = set()
    dep_edges = set()      # (key, parent_id)
    byname = set()         # (key, parent_name)
    sp_edges = set()       # (key, "parent (kind)")
    refused_edges = []
    dups = 0
    for layer in ("file_local", "pointer_rollup"):
        for i, e in enumerate(dep["edges"][layer]):
            sig = json.dumps([layer, e["child"], e["parent"], e["citation"], e["relation"], e.get("parent_kind")])
            if sig in seen:
                dups += 1
                continue
            seen.add(sig)
            cands = by_id.get(e["child"], [])
            key = None
            if len(cands) == 1:
                key = cands[0][0]
            elif cands:
                mm = CIT.match(e["citation"])
                path, loc = (mm.group(1), mm.group(2)) if mm else ("", "")
                at = [c for c in cands if c[1] == path]
                if len(at) == 1:
                    key = at[0][0]
                elif at:
                    atl = [c for c in at if c[2] == loc]
                    if len(atl) == 1:
                        key = atl[0][0]
                    else:
                        refused_edges.append((layer, i, "AMBIGUOUS_CHILD_IDENTITY"))
                else:
                    refused_edges.append((layer, i, "NO_OBJECT_AT_CITATION"))
            else:
                refused_edges.append((layer, i, "CHILD_ID_NOT_IN_CENSUS"))
            if key is None:
                continue
            if e.get("parent_kind") == "CORPUS_CLAIM":
                dep_edges.add((key, e["parent"]))
            else:
                byname.add((key, e["parent"]))
            if e["relation"] == "STRONGEST_PARENT_DECLARED":
                sp_edges.add((key, "%s (%s)" % (e["parent"], e.get("parent_kind"))))

    # ---- descendants by fixed point
    kids = {}
    for k, p in dep_edges:
        kids.setdefault(p, set()).add(k)
    desc = {}
    desc_direct = {}
    for g in gaps["gaps"]:
        c = g["claim_id"]
        direct = set(kids.get(c, ()))
        closed = set(direct)
        frontier_ids = set(meta[k][0] for k in direct)
        while True:
            new = set()
            for oid in frontier_ids:
                new |= kids.get(oid, set())
            new -= closed
            if not new:
                break
            closed |= new
            frontier_ids = set(meta[k][0] for k in new)
        desc[g["id"]] = sorted(closed)
        desc_direct[g["id"]] = sorted(direct)

    # ---- grading via lookup table
    grades = schema["materiality_grades"]
    table = {}
    for s in range(4):
        for e_ in range(4):
            for k in range(4):
                for b in range(4):
                    idx = s + (3 - e_) + k + b
                    table[(s, e_, k, b)] = [g["grade"] for g in grades if g["lo"] <= idx <= g["hi"]][0]
    mult = {}
    for g in gaps["gaps"]:
        mult[g["claim_id"]] = mult.get(g["claim_id"], 0) + 1
    grade_of = {}
    counts = {}
    for g in gaps["gaps"]:
        kind = g["id"].split("-")[1]
        scope = {"DUPID": "PACKAGE", "FIN2UNIV": "FLAGSHIP"}.get(kind, "LOCAL")
        ev = "ASSERTED" if g["status"] == "OPEN" else "FINITE_EXACT"
        b = mult[g["claim_id"]] - 1
        gr = table[(schema["severity_rank"][g["severity"]], schema["evidence_mode_rank"][ev], schema["scope_rank"][scope], b if b < 3 else 3)]
        grade_of[g["id"]] = gr
        counts[gr] = counts.get(gr, 0) + 1

    # ---- decidability evaluable counts
    reg_keys = sorted(set(k for (k, f) in ledger if f == "assumptions"))
    stat_keys = [k for k in reg_keys if meta[k][1] in STAT]
    fam = {}
    for k in reg_keys:
        if meta[k][1] == "STATISTICAL_EXPERIMENT":
            p = meta[k][3].split("/")[1]
            fam[p] = fam.get(p, 0) + 1

    populated_keys = set(bound.values()) | set(k for k, _ in dep_edges) | set(k for k, _ in byname) | set(k for k, _ in sp_edges)
    return {
        "route": "B",
        "objects": n,
        "bound": dict(sorted(bound.items())),
        "rules": dict(sorted(rules.items())),
        "by_rule": {"B1_RESULT_ID_SUFFIX_EXACT": sum(1 for v in rules.values() if v.startswith("B1")),
                    "B2_THEOREM_NAME_ID_EXACT": sum(1 for v in rules.values() if v.startswith("B2"))},
        "refused_rows": sorted(refused_rows),
        "package_level_rows": sorted(pkg_level),
        "delta_applied": sorted(delta_applied),
        "delta_refused": sorted(delta_refused),
        "levels": dict((k, list(v)) for k, v in sorted(level.items())),
        "maturity_populated": sum(1 for v in level.values() if v[0] != "UNKNOWN"),
        "evidence_populated": sum(1 for v in level.values() if v[1] != "UNKNOWN"),
        "registrations_bound": regs_bound,
        "ledger_keys": dict((f, sorted(k for (k, ff) in ledger if ff == f)) for f in LEDGERS),
        "ledger_content": dict(("%s|%s" % (k, f), list(v)) for (k, f), v in sorted(ledger.items())),
        "dep_edges": sorted(dep_edges),
        "byname_edges": sorted(byname),
        "sp_edges": sorted(sp_edges),
        "refused_edges": sorted(refused_edges),
        "duplicate_edge_records": dups,
        "descendants": desc,
        "descendants_direct": desc_direct,
        "gaps_with_descendants": sum(1 for v in desc.values() if v),
        "gaps_with_direct": sum(1 for v in desc_direct.values() if v),
        "grade_of": grade_of,
        "grade_counts": counts,
        "populated_records": len(populated_keys),
        "decidability": {"assumptions_populated": len(reg_keys), "stat_or_empirical_registered": len(stat_keys),
                         "statistical_registered": sum(1 for k in reg_keys if meta[k][1] == "STATISTICAL_EXPERIMENT"),
                         "registered_statistical_families": dict(sorted(fam.items())),
                         "binding_fraction": str(Fraction(len(reg_keys), n))},
    }


def summary(b):
    return {
        "objects": b["objects"], "bound_rows": len(b["bound"]), "by_rule": b["by_rule"],
        "refused_rows": len(b["refused_rows"]), "package_level_rows": len(b["package_level_rows"]),
        "delta_applied": b["delta_applied"], "delta_refused": b["delta_refused"],
        "maturity_populated": b["maturity_populated"], "evidence_populated": b["evidence_populated"],
        "registrations_bound": b["registrations_bound"],
        "ledger_populated": dict((f, len(v)) for f, v in b["ledger_keys"].items()),
        "dep_edges": len(b["dep_edges"]), "byname_edges": len(b["byname_edges"]), "sp_edges": len(b["sp_edges"]),
        "refused_edges": len(b["refused_edges"]), "duplicate_edge_records": b["duplicate_edge_records"],
        "gaps_with_descendants": b["gaps_with_descendants"], "gaps_with_direct": b["gaps_with_direct"],
        "descendant_keys_total": sum(len(v) for v in b["descendants"].values()),
        "grade_counts": b["grade_counts"], "populated_records": b["populated_records"],
        "decidability": b["decidability"],
    }


if __name__ == "__main__":
    sys.stdout.write(json.dumps(summary(derive()), indent=1, sort_keys=True) + "\n")
