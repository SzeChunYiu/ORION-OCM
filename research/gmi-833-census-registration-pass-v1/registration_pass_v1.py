#!/usr/bin/env python3
"""Route A - census registration pass (issue #833, section AA feeder).

Populates the five list fields and the two level fields of the frozen corpus
census (`gmi-833-corpus-census-v1`, source 2fffb144) from evidence that is
ALREADY committed on `main`, under the exact-identity rules declared in
FREEZE_V1.md section 4.  Nothing is inferred from prose; every written value
carries a pointer a reviewer can open; every refusal is listed.

Outputs (written next to this file):
  REGISTER_DELTA_V1.json   populated object records only (delta over the census)
  GAP_GRAPH_V2.json        all 1140 gaps with descendants and re-graded materiality
  DECIDABILITY_V1.json     per AA16-AA37 row: discriminator field and evaluable count
  REFUSALS_V1.json         every row / edge / delta refused, with its reason

Stdlib only.  Python 3.8 compatible.  Exact arithmetic only (int / Fraction).
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

CENSUS_INDEX = "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json"
GAP_GRAPH = "research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json"
SCORES_V2 = "research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json"
SCORES_V3_DELTA = "research/gmi-833-maturity-rescore-v3-w4-v1/SCORES_V3_DELTA.json"
REGISTRATIONS = "research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json"
DEPGRAPH = "research/gmi-833-depgraph-adjudication-v1/DEPENDENCY_GRAPH_V2.json"
GAP_SCHEMA = "research/gmi-833-aa-gap-object-v1/OPEN_GAP_SCHEMA_V1.json"

CENSUS_FROZEN_SHA = "2fffb14447193cbfbed3224508a077f2d4f5d2dd"
CLAIM_CEILING = "SOURCED_PROPAGATION_REGISTER_V1"
UNREGISTERED = "UNREGISTERED"
UNKNOWN = "UNKNOWN"
LIST_FIELDS = ("assumptions", "falsifiers", "forbidden_extrapolations", "strongest_parents")
LEGACY_RE = re.compile(r"^GMI833_V2_LEGACY_(\d{3})_(.+)$")
PACKAGE_LEVEL_PREFIXES = ("GMI833_V2_ARRIVAL_", "GMI833_V3_ARRIVAL_", "GMI833_RESCORE_", "GMI833_CD_NEW_")
GAP_KIND_SCOPE = {"DUPID": "PACKAGE", "FIN2UNIV": "FLAGSHIP"}
GRADE_ORDER = ("IMMATERIAL", "MINOR", "MATERIAL", "CRITICAL")
DEP_LAYERS = ("file_local", "pointer_rollup")
NULL_SEED = 8330833
NULL_TRIALS = 200


class PassError(RuntimeError):
    pass


def load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


def canonical(obj):
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def package_of(path):
    parts = path.split("/")
    if len(parts) < 3 or parts[0] != "research":
        raise PassError("census path outside research/<package>/: %r" % path)
    return parts[1]


def key_of(obj):
    return obj["source_path"] + ":" + obj["source_locator"]


# --------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------
class Inputs(object):
    def __init__(self, census=None, gaps=None, scores=None, delta=None, regs=None, depgraph=None, schema=None):
        self.census = census if census is not None else load(CENSUS_INDEX)
        self.gaps = gaps if gaps is not None else load(GAP_GRAPH)
        self.scores = scores if scores is not None else load(SCORES_V2)
        self.delta = delta if delta is not None else load(SCORES_V3_DELTA)
        self.regs = regs if regs is not None else load(REGISTRATIONS)
        self.depgraph = depgraph if depgraph is not None else load(DEPGRAPH)
        self.schema = schema if schema is not None else load(GAP_SCHEMA)
        if self.census.get("frozen_source_sha") != CENSUS_FROZEN_SHA:
            raise PassError("census is not the frozen one: %r" % self.census.get("frozen_source_sha"))
        self.objects = self.census["scientific_objects"]
        self.by_key = {}
        for o in self.objects:
            k = key_of(o)
            if k in self.by_key:
                raise PassError("duplicate register key %s" % k)
            self.by_key[k] = o
        self.by_id = {}
        for o in self.objects:
            self.by_id.setdefault(o["object_id"], []).append(o)
        self.pkg_counts = {}
        for o in self.objects:
            p = package_of(o["source_path"])
            self.pkg_counts[p] = self.pkg_counts.get(p, 0) + 1
        self.scores_by_rid = {}
        for r in self.scores:
            if r["result_id"] in self.scores_by_rid:
                raise PassError("duplicate result_id in scores: %s" % r["result_id"])
            self.scores_by_rid[r["result_id"]] = r
        self.regs_by_rid = {}
        for r in self.regs["objects"]:
            if r["result_id"] in self.regs_by_rid:
                raise PassError("duplicate result_id in registrations: %s" % r["result_id"])
            self.regs_by_rid[r["result_id"]] = r


# --------------------------------------------------------------------------
# 4.2 binding of scored rows to census objects
# --------------------------------------------------------------------------
def _explicit_in_package(inp, oid, package):
    return [o for o in inp.by_id.get(oid, ()) if o["id_kind"] == "EXPLICIT" and package_of(o["source_path"]) == package]


def bind_row(inp, row):
    """Return (rule, object) or (None, reason).  Exact identity only."""
    rid = row["result_id"]
    if rid.startswith(PACKAGE_LEVEL_PREFIXES):
        return None, "PACKAGE_LEVEL_NO_OBJECT_IDENTITY"
    m = LEGACY_RE.match(rid)
    if not m:
        return None, "UNRECOGNISED_RESULT_ID_FORM"
    suffix = m.group(2)
    c1 = _explicit_in_package(inp, suffix, row["package"])
    if len(c1) == 1:
        return "B1_RESULT_ID_SUFFIX_EXACT", c1[0]
    if len(c1) > 1:
        return None, "B1_AMBIGUOUS_%d_OBJECTS" % len(c1)
    name = (row.get("theorem_name") or "").strip()
    c2 = _explicit_in_package(inp, name, row["package"]) if name else []
    if len(c2) == 1:
        return "B2_THEOREM_NAME_ID_EXACT", c2[0]
    if len(c2) > 1:
        return None, "B2_AMBIGUOUS_%d_OBJECTS" % len(c2)
    return None, "NO_EXACT_IDENTITY_IN_PACKAGE"


def bind_all(inp, rows=None):
    rows = inp.scores if rows is None else rows
    bound = {}       # result_id -> (rule, key)
    refusals = []
    package_level = []
    for row in rows:
        rule, res = bind_row(inp, row)
        if rule is None:
            if res == "PACKAGE_LEVEL_NO_OBJECT_IDENTITY":
                package_level.append({"result_id": row["result_id"], "package": row["package"],
                                      "maturity_M": row.get("maturity_M"), "evidence_EV": row.get("evidence_EV"),
                                      "census_objects_under_package": inp.pkg_counts.get(row["package"], 0),
                                      "reason": res})
            else:
                refusals.append({"kind": "SCORED_ROW", "result_id": row["result_id"], "package": row["package"], "reason": res})
            continue
        k = key_of(res)
        if k in [v[1] for v in bound.values()]:
            refusals.append({"kind": "SCORED_ROW", "result_id": row["result_id"], "package": row["package"],
                             "reason": "OBJECT_ALREADY_BOUND_TO_ANOTHER_ROW"})
            continue
        bound[row["result_id"]] = (rule, k)
    return bound, refusals, package_level


def loose_prefix_binding_count(inp, rows):
    """MEASUREMENT ONLY (freeze P4): how many rows a prefix match would bind that B1/B2 do not."""
    explicit = {}
    for o in inp.objects:
        if o["id_kind"] == "EXPLICIT":
            explicit.setdefault(package_of(o["source_path"]), set()).add(o["object_id"])
    extra = 0
    for row in rows:
        m = LEGACY_RE.match(row["result_id"])
        if not m:
            continue
        rule, _ = bind_row(inp, row)
        if rule is not None:
            continue
        suf = m.group(2)
        if any(i.startswith(suf) for i in explicit.get(row["package"], ())):
            extra += 1
    return extra


# --------------------------------------------------------------------------
# 4.4 dependency edges
# --------------------------------------------------------------------------
def parse_citation(cit):
    head = cit.split(" ")[0]
    path, _, loc = head.partition(":")
    return path, loc


def resolve_child(inp, edge):
    cands = inp.by_id.get(edge["child"], [])
    if len(cands) == 1:
        return "UNIQUE_ID", cands[0]
    if not cands:
        return None, "CHILD_ID_NOT_IN_CENSUS"
    path, loc = parse_citation(edge["citation"])
    at_path = [o for o in cands if o["source_path"] == path]
    if len(at_path) == 1:
        return "CITATION_PATH", at_path[0]
    if not at_path:
        return None, "NO_OBJECT_AT_CITATION"
    at_line = [o for o in at_path if o["source_locator"] == loc]
    if len(at_line) == 1:
        return "CITATION_LINE", at_line[0]
    return None, "AMBIGUOUS_CHILD_IDENTITY"


def resolve_edges(inp, depgraph=None):
    depgraph = inp.depgraph if depgraph is None else depgraph
    seen = set()
    resolved = []   # dicts: key, parent, parent_kind, relation, layer, index, citation
    refusals = []
    dup_records = 0
    for layer in DEP_LAYERS:
        for idx, e in enumerate(depgraph["edges"][layer]):
            sig = (layer, e["child"], e["parent"], e["citation"], e["relation"], e.get("parent_kind"))
            if sig in seen:
                dup_records += 1
                continue
            seen.add(sig)
            how, res = resolve_child(inp, e)
            if how is None:
                refusals.append({"kind": "DEPENDENCY_EDGE", "layer": layer, "index": idx, "child": e["child"],
                                 "parent": e["parent"], "citation": e["citation"], "reason": res,
                                 "census_declarations_of_child": len(inp.by_id.get(e["child"], []))})
                continue
            resolved.append({"key": key_of(res), "resolved_by": how, "parent": e["parent"],
                             "parent_kind": e.get("parent_kind"), "relation": e["relation"], "layer": layer,
                             "index": idx, "citation": e["citation"],
                             "pointer": "%s#edges.%s[%d] -> %s" % (DEPGRAPH, layer, idx, e["citation"])})
    return resolved, refusals, dup_records


# --------------------------------------------------------------------------
# 4.5 materiality (AAG-3, reused unchanged) and descendants
# --------------------------------------------------------------------------
def materiality_index(sev, ev, scope, blast, cap=3):
    if blast < 0:
        raise PassError("blast must be >= 0")
    return sev + (3 - ev) + scope + min(blast, cap)


def materiality_grade(index, schema):
    for g in schema["materiality_grades"]:
        if g["lo"] <= index <= g["hi"]:
            return g["grade"]
    raise PassError("index %r outside grade range" % (index,))


def monotonicity_violations(schema, grade_fn=None):
    gfn = grade_fn or (lambda i: materiality_grade(i, schema))
    rank = dict((g, i) for i, g in enumerate(GRADE_ORDER))
    bad = 0
    checked = 0
    for s in range(4):
        for e in range(4):
            for k in range(4):
                for b in range(4):
                    base = rank[gfn(materiality_index(s, e, k, b))]
                    for ds, de, dk, db in ((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)):
                        s2, e2, k2, b2 = s + ds, e + de, k + dk, b + db
                        if not (0 <= s2 < 4 and 0 <= e2 < 4 and 0 <= k2 < 4 and 0 <= b2 < 4):
                            continue
                        checked += 1
                        if rank[gfn(materiality_index(s2, e2, k2, b2))] < base:
                            bad += 1
    return {"domain_points": 256, "comparisons": checked, "violations": bad}


def gap_kind(gap):
    parts = gap["id"].split("-")
    return parts[1] if len(parts) > 1 else ""


def descendants_of(claim_id, children_of_id, by_key):
    """Depth-first transitive closure over object keys; cycle safe."""
    seen = set()
    stack = [claim_id]
    while stack:
        cid = stack.pop()
        for k in children_of_id.get(cid, ()):
            if k not in seen:
                seen.add(k)
                stack.append(by_key[k]["object_id"])
    return seen


# --------------------------------------------------------------------------
# the pass
# --------------------------------------------------------------------------
def run_pass(inp):
    bound, refusals, package_level = bind_all(inp)
    scores_pointer = SCORES_V2 + "#result_id=%s.%s"
    delta_pointer = SCORES_V3_DELTA + "#result_id=%s.%s"
    regs_pointer = REGISTRATIONS + "#result_id=%s.fields.%s.content[%d]"

    records = {}   # key -> populated record

    def rec(key):
        if key not in records:
            o = inp.by_key[key]
            records[key] = {
                "register_key": key, "source_path": o["source_path"], "source_locator": o["source_locator"],
                "object_id": o["object_id"], "id_kind": o["id_kind"], "object_class": o["object_class"],
                "quantifier_class": o["quantifier_class"], "proof_evidence_mode": o["proof_evidence_mode"],
                "maturity_level": UNKNOWN, "evidence_level": UNKNOWN,
                "assumptions": UNREGISTERED, "falsifiers": UNREGISTERED,
                "forbidden_extrapolations": UNREGISTERED, "strongest_parents": UNREGISTERED,
                "claim_dependencies": [], "dependency_parents_by_name": [], "scope_quantifiers": UNREGISTERED,
                "binding": {}, "provenance": {},
            }
        return records[key]

    # ---- 4.2 maturity / evidence
    delta_applied = []
    for rid, (rule, key) in sorted(bound.items()):
        row = inp.scores_by_rid[rid]
        r = rec(key)
        r["maturity_level"] = row["maturity_M"]
        r["evidence_level"] = row["evidence_EV"]
        r["binding"]["scored_row"] = {"result_id": rid, "rule": rule, "package": row["package"],
                                      "source_in_citation_paths": r["source_path"] in row.get("citation_paths", [])}
        r["provenance"]["maturity_level"] = [scores_pointer % (rid, "maturity_M")]
        r["provenance"]["evidence_level"] = [scores_pointer % (rid, "evidence_EV")]
    for d in inp.delta["records"]:
        rid = d["result_id"]
        if rid in bound:
            key = bound[rid][1]
            r = rec(key)
            r["maturity_level"] = d["maturity_M"]
            r["evidence_level"] = d["evidence_EV"]
            r["provenance"]["maturity_level"].append(delta_pointer % (rid, "maturity_M"))
            r["provenance"]["evidence_level"].append(delta_pointer % (rid, "evidence_EV"))
            r["binding"]["v3_delta"] = {"result_id": rid, "delta_kind": d.get("delta_kind"),
                                        "superseded_v2": (inp.scores_by_rid[rid]["maturity_M"], inp.scores_by_rid[rid]["evidence_EV"])}
            delta_applied.append(rid)
        elif rid in inp.scores_by_rid:
            refusals.append({"kind": "V3_DELTA", "result_id": rid, "reason": "V2_ROW_UNBOUND_SO_DELTA_HAS_NO_OBJECT"})
        elif rid.startswith(PACKAGE_LEVEL_PREFIXES):
            package_level.append({"result_id": rid, "package": d["package"], "maturity_M": d["maturity_M"],
                                  "evidence_EV": d["evidence_EV"],
                                  "census_objects_under_package": inp.pkg_counts.get(d["package"], 0),
                                  "reason": "PACKAGE_LEVEL_NO_OBJECT_IDENTITY", "source": "SCORES_V3_DELTA"})
        else:
            refusals.append({"kind": "V3_DELTA", "result_id": rid, "reason": "ORPHAN_DELTA_RESULT_ID_NOT_IN_V2"})

    # ---- 4.3 registrations
    reg_bound = 0
    reg_package_level = 0
    for rid, reg in sorted(inp.regs_by_rid.items()):
        if rid not in bound:
            if rid in inp.scores_by_rid or rid.startswith(PACKAGE_LEVEL_PREFIXES):
                reg_package_level += 1
            else:
                refusals.append({"kind": "REGISTRATION", "result_id": rid, "package": reg["package"],
                                 "reason": "NO_BOUND_SCORED_ROW_WITH_THIS_RESULT_ID"})
            continue
        key = bound[rid][1]
        r = rec(key)
        reg_bound += 1
        for field in LIST_FIELDS + ("scope_quantifiers",):
            f = reg["fields"][field]
            content = list(f["content"])
            r[field] = content
            second_hop = f.get("source") or f.get("derivation") or ""
            r["provenance"][field] = [regs_pointer % (rid, field, i) + " <- " + second_hop for i in range(len(content))]
            r["binding"].setdefault("registration", {})[field] = f["status"]

    # ---- 4.4 edges
    resolved, edge_refusals, dup_records = resolve_edges(inp)
    refusals.extend(edge_refusals)
    children_of_id = {}
    dep_edges = set()
    by_name = 0
    sp_from_edges = 0
    for e in resolved:
        r = rec(e["key"])
        if e["parent_kind"] == "CORPUS_CLAIM":
            if e["parent"] not in r["claim_dependencies"]:
                r["claim_dependencies"].append(e["parent"])
                r["provenance"].setdefault("claim_dependencies", []).append(e["pointer"])
            dep_edges.add((e["key"], e["parent"]))
            children_of_id.setdefault(e["parent"], set()).add(e["key"])
        else:
            by_name += 1
            entry = e["parent"]
            if entry not in r["dependency_parents_by_name"]:
                r["dependency_parents_by_name"].append(entry)
                r["provenance"].setdefault("dependency_parents_by_name", []).append(e["pointer"])
        if e["relation"] == "STRONGEST_PARENT_DECLARED":
            entry = "%s (%s)" % (e["parent"], e["parent_kind"])
            if r["strongest_parents"] == UNREGISTERED:
                r["strongest_parents"] = []
                r["provenance"]["strongest_parents"] = []
            if entry not in r["strongest_parents"]:
                r["strongest_parents"].append(entry)
                r["provenance"]["strongest_parents"].append(e["pointer"])
                sp_from_edges += 1
        r["binding"].setdefault("edges", []).append({"layer": e["layer"], "index": e["index"], "resolved_by": e["resolved_by"]})
    for r in records.values():
        r["claim_dependencies"].sort()
        r["dependency_parents_by_name"].sort()

    # ---- 4.5 gap graph
    schema = inp.schema
    srank, erank, krank = schema["severity_rank"], schema["evidence_mode_rank"], schema["scope_rank"]
    mult = {}
    for g in inp.gaps["gaps"]:
        mult[g["claim_id"]] = mult.get(g["claim_id"], 0) + 1
    gaps_out = []
    grade_counts = dict((g, 0) for g in GRADE_ORDER)
    nonempty_direct = nonempty_trans = 0
    unknown_kind = 0
    for g in inp.gaps["gaps"]:
        kind = gap_kind(g)
        scope = GAP_KIND_SCOPE.get(kind)
        if scope is None:
            unknown_kind += 1
            scope = "LOCAL"
        ev = "ASSERTED" if g.get("status") == "OPEN" else "FINITE_EXACT"
        blast = mult[g["claim_id"]] - 1
        idx = materiality_index(srank[g["severity"]], erank[ev], krank[scope], blast)
        grade = materiality_grade(idx, schema)
        grade_counts[grade] += 1
        direct = sorted(children_of_id.get(g["claim_id"], ()))
        trans = sorted(descendants_of(g["claim_id"], children_of_id, inp.by_key))
        nonempty_direct += bool(direct)
        nonempty_trans += bool(trans)
        g2 = dict(g)
        g2["materiality_v1"] = g["materiality"]
        g2["materiality"] = grade
        g2["materiality_index"] = idx
        g2["materiality_inputs"] = {"severity": g["severity"], "evidence_mode": ev, "scope": scope, "blast": blast,
                                    "rule": GAP_SCHEMA + "#materiality_grades ; gmi-833-aa-gap-object-v1 AAG-3"}
        g2["descendants_direct"] = direct
        g2["descendants"] = trans
        g2["descendants_provenance"] = "claim_dependencies of each listed register key (REGISTER_DELTA_V1.json)"
        gaps_out.append(g2)

    # ---- counts over the full census
    n = len(inp.objects)
    populated_keys = set(records)
    counts = {"objects": n, "populated_records": len(records)}
    for field in ("maturity_level", "evidence_level"):
        pop = sum(1 for r in records.values() if r[field] != UNKNOWN)
        bound_unknown = sum(1 for r in records.values() if r[field] == UNKNOWN and r["provenance"].get(field))
        counts[field] = {"before_populated": 0, "before_unknown": n, "after_populated": pop, "after_unknown": n - pop,
                         "after_bound_but_scored_unknown": bound_unknown, "after_unbound": n - pop - bound_unknown}
    for field in LIST_FIELDS:
        pop = sum(1 for r in records.values() if r[field] != UNREGISTERED)
        counts[field] = {"before_populated": 0, "before_empty": n, "after_populated": pop, "after_unregistered": n - pop,
                         "after_empty_list": sum(1 for r in records.values() if r[field] != UNREGISTERED and not r[field])}
    pop = sum(1 for r in records.values() if r["claim_dependencies"])
    counts["claim_dependencies"] = {"before_populated": 0, "before_empty": n, "after_populated": pop, "after_empty": n - pop,
                                    "edges": len(dep_edges), "distinct_parent_ids": len(children_of_id)}
    counts["dependency_parents_by_name"] = {"after_populated": sum(1 for r in records.values() if r["dependency_parents_by_name"]),
                                            "edge_records": by_name}
    counts["strongest_parents_entries_from_edges"] = sp_from_edges

    binding_counts = {}
    for rule, _ in bound.values():
        binding_counts[rule] = binding_counts.get(rule, 0) + 1
    cit_consistent = sum(1 for r in records.values() if r["binding"].get("scored_row", {}).get("source_in_citation_paths"))

    layer_counts = dict((k, len(v)) for k, v in inp.depgraph["edges"].items())

    result = {
        "schema": "GMI_833_CENSUS_REGISTRATION_PASS_RESULT_V1",
        "package": "gmi-833-census-registration-pass-v1",
        "issue": 833,
        "claim_ceiling": CLAIM_CEILING,
        "census_frozen_source_sha": CENSUS_FROZEN_SHA,
        "route": "A",
        "population": counts,
        "binding": {
            "scored_rows": len(inp.scores), "bound_rows": len(bound), "by_rule": binding_counts,
            "bound_objects": len(set(k for _, k in bound.values())),
            "source_path_in_citation_paths": cit_consistent,
            "package_level_rows": len(package_level), "package_level_rows_with_census_objects":
                sum(1 for p in package_level if p["census_objects_under_package"] > 0),
            "v3_delta_records": len(inp.delta["records"]), "v3_delta_applied": delta_applied,
            "registrations": len(inp.regs["objects"]), "registrations_bound": reg_bound,
            "registrations_package_level": reg_package_level,
            "loose_prefix_variant_extra_bindings": loose_prefix_binding_count(inp, inp.scores),
        },
        "edges": {
            "layers": layer_counts, "layers_scanned": list(DEP_LAYERS),
            "unique_records_scanned": len(resolved) + len(edge_refusals), "duplicate_records_skipped": dup_records,
            "resolved": len(resolved), "refused": len(edge_refusals),
            "resolved_by": dict((h, sum(1 for e in resolved if e["resolved_by"] == h)) for h in ("UNIQUE_ID", "CITATION_PATH", "CITATION_LINE")),
            "refused_by_reason": dict((rs, sum(1 for e in edge_refusals if e["reason"] == rs)) for rs in sorted(set(e["reason"] for e in edge_refusals))),
            "object_to_id_dependency_edges": len(dep_edges), "child_objects_with_dependencies": len(set(k for k, _ in dep_edges)),
        },
        "gap_graph": {
            "gaps": len(gaps_out), "grade_counts": grade_counts, "unknown_kind": unknown_kind,
            "monotonicity": monotonicity_violations(schema),
            "gaps_with_nonempty_descendants_direct": nonempty_direct,
            "gaps_with_nonempty_descendants": nonempty_trans,
            "gaps_isolated": len(gaps_out) - nonempty_trans,
            "descendant_keys_total_direct": sum(len(g["descendants_direct"]) for g in gaps_out),
            "descendant_keys_total": sum(len(g["descendants"]) for g in gaps_out),
            "materiality_v1_distinct": len(set(g["materiality_v1"] for g in gaps_out)),
            "materiality_v2_distinct": len(set(g["materiality"] for g in gaps_out)),
        },
        "refusals": {"total": len(refusals), "by_kind": dict((k, sum(1 for r in refusals if r["kind"] == k)) for k in sorted(set(r["kind"] for r in refusals)))},
    }
    return {"result": result, "records": records, "gaps": gaps_out, "refusals": refusals,
            "package_level": package_level, "bound": bound, "dep_edges": dep_edges, "children_of_id": children_of_id}


# --------------------------------------------------------------------------
# pointer verifier (the check a reviewer would do, mechanised)
# --------------------------------------------------------------------------
_PTR_SCORE = re.compile(r"^(?P<path>[^#]+)#result_id=(?P<rid>.+)\.(?P<attr>maturity_M|evidence_EV)$")
_PTR_REG = re.compile(r"^(?P<path>[^#]+)#result_id=(?P<rid>.+?)\.fields\.(?P<field>[a-z_]+)\.content\[(?P<i>\d+)\](?: <- .*)?$")
_PTR_EDGE = re.compile(r"^(?P<path>[^#]+)#edges\.(?P<layer>[a-z_]+)\[(?P<i>\d+)\] -> (?P<cit>.+)$")
_FIELD_ATTR = {"maturity_level": "maturity_M", "evidence_level": "evidence_EV"}


def verify_pointers(records, inp):
    """Open every pointer and check the pointed value equals the written value."""
    findings = []
    delta_by_rid = dict((d["result_id"], d) for d in inp.delta["records"])
    for key, r in sorted(records.items()):
        for field, ptrs in sorted(r["provenance"].items()):
            value = r[field]
            if field in ("maturity_level", "evidence_level"):
                if not ptrs:
                    findings.append((key, field, "NO_POINTER"))
                    continue
                last = ptrs[-1]
                m = _PTR_SCORE.match(last)
                if not m:
                    findings.append((key, field, "UNPARSEABLE_POINTER"))
                    continue
                src = delta_by_rid if m.group("path") == SCORES_V3_DELTA else inp.scores_by_rid
                row = src.get(m.group("rid"))
                if row is None:
                    findings.append((key, field, "POINTER_TARGET_MISSING"))
                elif row.get(m.group("attr")) != value or _FIELD_ATTR[field] != m.group("attr"):
                    findings.append((key, field, "POINTER_CONTENT_MISMATCH"))
                for p in ptrs[:-1]:
                    m0 = _PTR_SCORE.match(p)
                    if not m0 or m0.group("rid") not in inp.scores_by_rid:
                        findings.append((key, field, "POINTER_TARGET_MISSING"))
            elif field in LIST_FIELDS + ("scope_quantifiers",):
                if value == UNREGISTERED:
                    findings.append((key, field, "POINTER_ON_UNREGISTERED_FIELD"))
                    continue
                if len(ptrs) != len(value):
                    findings.append((key, field, "POINTER_COUNT_MISMATCH"))
                    continue
                for v, p in zip(value, ptrs):
                    m = _PTR_REG.match(p)
                    if m:
                        reg = inp.regs_by_rid.get(m.group("rid"))
                        if reg is None or m.group("field") != field:
                            findings.append((key, field, "POINTER_TARGET_MISSING"))
                            continue
                        content = reg["fields"][field]["content"]
                        i = int(m.group("i"))
                        if i >= len(content) or content[i] != v:
                            findings.append((key, field, "POINTER_CONTENT_MISMATCH"))
                        continue
                    m = _PTR_EDGE.match(p)
                    if m and field == "strongest_parents":
                        e = _edge_at(inp, m.group("layer"), int(m.group("i")))
                        if e is None or e["citation"] != m.group("cit") or e["relation"] != "STRONGEST_PARENT_DECLARED" \
                                or v != "%s (%s)" % (e["parent"], e.get("parent_kind")):
                            findings.append((key, field, "POINTER_CONTENT_MISMATCH"))
                        continue
                    findings.append((key, field, "UNPARSEABLE_POINTER"))
            elif field in ("claim_dependencies", "dependency_parents_by_name"):
                if len(ptrs) != len(value):
                    findings.append((key, field, "POINTER_COUNT_MISMATCH"))
                    continue
                parents = set()
                for p in ptrs:
                    m = _PTR_EDGE.match(p)
                    e = _edge_at(inp, m.group("layer"), int(m.group("i"))) if m else None
                    if e is None or e["citation"] != m.group("cit"):
                        findings.append((key, field, "POINTER_TARGET_MISSING"))
                        continue
                    if resolve_child(inp, e)[1] is not inp.by_key[key] and resolve_child(inp, e)[0] is not None:
                        findings.append((key, field, "POINTER_RESOLVES_TO_OTHER_OBJECT"))
                    parents.add(e["parent"])
                if parents != set(value):
                    findings.append((key, field, "POINTER_CONTENT_MISMATCH"))
            else:
                findings.append((key, field, "UNKNOWN_FIELD_WITH_POINTER"))
    return findings


def _edge_at(inp, layer, i):
    edges = inp.depgraph["edges"].get(layer, [])
    return edges[i] if 0 <= i < len(edges) else None


def verify_descendants(gaps, records):
    """Every listed descendant must reach the gap's claim id through claim_dependencies."""
    findings = []
    for g in gaps:
        for k in g["descendants"]:
            r = records.get(k)
            if r is None:
                findings.append((g["id"], k, "DESCENDANT_NOT_IN_REGISTER"))
                continue
            # walk up: k depends on some id; that id is the claim or is the object_id of another descendant
            ok = g["claim_id"] in r["claim_dependencies"] or any(
                records.get(k2) is not None and records[k2]["object_id"] in r["claim_dependencies"] for k2 in g["descendants"] if k2 != k)
            if not ok:
                findings.append((g["id"], k, "DESCENDANT_DOES_NOT_DEPEND_ON_CLAIM"))
    return findings


# --------------------------------------------------------------------------
# 4.6 decidability
# --------------------------------------------------------------------------
ROW_TEXT = {
    "AA16": "Search for quantifier-order mistakes (`forall/exists` swaps).",
    "AA17": "Search for converse/inverse fallacies.",
    "AA18": "Search for necessity-vs-sufficiency confusion.",
    "AA19": "Search for representability-vs-reachability confusion.",
    "AA20": "Search for optimality-vs-selection confusion.",
    "AA21": "Search for finite-scope-to-universal extrapolation.",
    "AA22": "Search for empirical-correlation-to-causal claims.",
    "AA23": "Search for identifiability failures.",
    "AA24": "Search for hidden dependence/independence assumptions.",
    "AA25": "Search for hidden stationarity/ergodicity assumptions.",
    "AA26": "Search for hidden bounded-horizon assumptions.",
    "AA27": "Search for hidden compactness/finiteness assumptions.",
    "AA28": "Search for encoding-dependent conclusions.",
    "AA29": "Search for arbitrary unit/scalarization dependence.",
    "AA30": "Search for search-algorithm-induced morphology artifacts.",
    "AA31": "Search for grammar-induced morphology artifacts.",
    "AA32": "Search for benchmark/ecology selection bias.",
    "AA33": "Search for post-selection inference / multiple-testing problems.",
    "AA34": "Search for data leakage/remint leakage.",
    "AA35": "Search for underpowered negative results.",
    "AA36": "Search for non-identifiable latent explanations.",
    "AA37": "Search for alternative known-parent reductions after every new-form claim.",
}
ALREADY = {"AA19": "gmi-833-aa-fallacy-detectors-v1 FD-1", "AA21": "gmi-833-aa-finite-universal-harness-v1 FU-1..FU-4",
           "AA31": "gmi-833-aa-fallacy-detectors-v1 FD-2", "AA37": "gmi-833-aa-fallacy-detectors-v1 FD-3"}
STAT_MODES = ("STATISTICAL_EXPERIMENT", "EMPIRICAL_EXPERIMENT")
# ledger vocabulary: MEASUREMENT ONLY (freeze 4.6); never a queue
LEDGER_VOCAB = {
    "AA24": ("independen", "i.i.d", "iid", "exchangeab", "dependen"),
    "AA25": ("stationar", "ergodic", "time-invariant", "time invariant"),
    "AA26": ("horizon", "finite budget", "bounded budget", "step budget"),
    "AA27": ("finite", "compact", "bounded", "closed set"),
}
ASSUMPTION_ROWS = {
    "AA24": ("assumptions", STAT_MODES, "evidence mode is a run experiment (statistical/empirical) AND the registered assumptions ledger does not name a dependence/independence assumption"),
    "AA25": ("assumptions", STAT_MODES, "evidence mode is a run experiment AND the registered assumptions ledger does not name a stationarity/ergodicity assumption"),
    "AA26": ("assumptions", None, "any registered object whose assumptions ledger does not name a horizon/budget bound"),
    "AA27": ("assumptions", None, "any registered object whose assumptions ledger does not name a finiteness/compactness bound"),
}
NO_DISCRIMINATOR = {
    "AA16": "quantifier ORDER of the statement (no register carries a quantifier prefix; quantifier_class is one label)",
    "AA17": "logical form (implication direction) of the statement",
    "AA18": "logical form (necessary vs sufficient condition) of the statement",
    "AA20": "whether the claim asserts optimality vs reports a chosen candidate (claim content, not carried by any register field)",
    "AA22": "whether the claim asserts a causal relation (claim content, not carried by any register field)",
    "AA23": "identifiability of the model from its interface (a property of the model; no register field)",
    "AA28": "outcome of an encoding-equivariance test per claim (no register field; gmi-833-remint-equivariance-v1 supplies a test, not a per-object field)",
    "AA29": "form of the objective / scalarization used (no register field)",
    "AA30": "search budget and algorithm that produced the reported form (no register field)",
    "AA32": "how the benchmark / ecology sample was drawn (no register field; 0 experiment ledgers at the frozen census)",
    "AA34": "leakage ledger per experiment (AA06 artifact class; 0 instances at the frozen census)",
    "AA35": "sample size n per registered negative (no register field carries n as a number)",
    "AA36": "latent structure of the explanation (no register field)",
}


def decidability(records, inp):
    registered = [r for r in records.values() if r["assumptions"] != UNREGISTERED]
    n_reg = len(registered)
    n_obj = len(inp.objects)
    rows = []
    gained = 0
    for row_id in sorted(ROW_TEXT):
        entry = {"row_id": row_id, "row_text": ROW_TEXT[row_id]}
        if row_id in ALREADY:
            entry.update({"verdict": "ALREADY_DECIDED", "decided_by": ALREADY[row_id],
                          "discriminator_field": "quantifier_class + proof_evidence_mode / parent receipt / ledger emission"})
        elif row_id in ASSUMPTION_ROWS:
            field, modes, pred = ASSUMPTION_ROWS[row_id]
            pool = [r for r in registered if modes is None or r["proof_evidence_mode"] in modes]
            vocab = LEDGER_VOCAB[row_id]
            names_it = sum(1 for r in pool if any(w in " ".join(r[field]).lower() for w in vocab))
            entry.update({"verdict": "REGISTERED_DISCRIMINATOR", "discriminator_field": field,
                          "predicate": pred, "trigger_evidence_modes": list(modes) if modes else "ANY",
                          "evaluable_objects_before": 0, "evaluable_objects_after": len(pool),
                          "objects_with_registered_ledger": n_reg,
                          "binding_sparsity": {"field": field, "populated": n_reg, "of": n_obj},
                          "measurement_not_queue": {"ledger_names_the_assumption_class": names_it,
                                                    "ledger_silent_on_it": len(pool) - names_it,
                                                    "vocabulary": list(vocab),
                                                    "note": "a silent ledger is a candidate for the next lane's queue, not a finding here"}})
            gained += 1
        elif row_id == "AA33":
            fam = {}
            for r in registered:
                if r["proof_evidence_mode"] == "STATISTICAL_EXPERIMENT":
                    p = package_of(r["source_path"])
                    fam[p] = fam.get(p, 0) + 1
            fam_all = {}
            for o in inp.objects:
                if o["proof_evidence_mode"] == "STATISTICAL_EXPERIMENT":
                    p = package_of(o["source_path"])
                    fam_all[p] = fam_all.get(p, 0) + 1
            pool = [r for r in registered if r["proof_evidence_mode"] == "STATISTICAL_EXPERIMENT"]
            entry.update({"verdict": "REGISTERED_DISCRIMINATOR", "discriminator_field": "assumptions + package family count of registered STATISTICAL_EXPERIMENT claims",
                          "predicate": "registered statistical claim in a package family of size >= 2 whose assumptions ledger does not name a multiplicity correction",
                          "evaluable_objects_before": 0, "evaluable_objects_after": len(pool),
                          "registered_statistical_families": dict(sorted(fam.items())),
                          "families_of_size_ge_2_registered": sum(1 for v in fam.values() if v >= 2),
                          "census_wide_statistical_families_note": "the census-wide family count (%d families, %d objects) was always computable; only the registered subset carries a ledger to check" % (len(fam_all), sum(fam_all.values())),
                          "binding_sparsity": {"field": "assumptions", "populated": n_reg, "of": n_obj}})
            gained += 1
        else:
            entry.update({"verdict": "NO_REGISTERED_DISCRIMINATOR", "missing_input": NO_DISCRIMINATOR[row_id],
                          "evaluable_objects_before": 0, "evaluable_objects_after": 0})
        rows.append(entry)
    summary = {
        "rows": 22, "already_decided": len(ALREADY),
        "left_undecidable_by_fallacy_lane": 19,
        "of_those_already_decided_elsewhere": 1,
        "gained_registered_discriminator": gained,
        "still_no_registered_discriminator": 22 - len(ALREADY) - gained,
        "binding_field": "assumptions", "binding_field_populated": n_reg, "binding_field_of": n_obj,
        "binding_fraction": str(Fraction(n_reg, n_obj)),
    }
    return {"schema": "GMI_833_AA_DECIDABILITY_V1", "package": "gmi-833-census-registration-pass-v1",
            "issue": 833, "comment_id": 5684607872, "anchor": "### AA. Recursive loophole / logic-gap closure",
            "criterion": "a row has a REGISTERED_DISCRIMINATOR iff a metadata predicate reading only register fields (no statement-prose parse) is evaluable on >= 1 object after the pass",
            "summary": summary, "rows": rows}


# --------------------------------------------------------------------------
# hostiles and null
# --------------------------------------------------------------------------
def hostiles(inp, out):
    records = out["records"]
    res = []
    # H1 pointer to missing result_id
    r = json.loads(json.dumps(next(v for v in records.values() if v["provenance"].get("maturity_level"))))
    r["provenance"]["maturity_level"] = [SCORES_V2 + "#result_id=GMI833_V2_LEGACY_999_NOPE.maturity_M"]
    f = verify_pointers({r["register_key"]: r}, inp)
    res.append({"id": "H1", "perturbation": "pointer names a result_id absent from the scores file",
                "quantity": "pointer findings", "baseline": 0, "perturbed": len(f), "detected": any(x[2] == "POINTER_TARGET_MISSING" for x in f)})
    # H2 pointer to real row, wrong content
    r = json.loads(json.dumps(next(v for v in records.values() if v["provenance"].get("maturity_level") and v["maturity_level"] == "M2" and "v3_delta" not in v["binding"])))
    other = next(rid for rid, row in inp.scores_by_rid.items() if row["maturity_M"] == "M0")
    r["provenance"]["maturity_level"] = [SCORES_V2 + "#result_id=%s.maturity_M" % other]
    f = verify_pointers({r["register_key"]: r}, inp)
    res.append({"id": "H2", "perturbation": "pointer names a real result_id whose stored placement differs",
                "quantity": "pointer findings", "baseline": 0, "perturbed": len(f), "detected": any(x[2] == "POINTER_CONTENT_MISMATCH" for x in f)})
    # H3 similarity plants
    real = next(v for v in sorted(records.values(), key=lambda x: x["register_key"])
                if v["binding"].get("scored_row", {}).get("rule") == "B1_RESULT_ID_SUFFIX_EXACT" and len(v["object_id"]) >= 5 and "-" in v["object_id"])
    pkg = package_of(real["source_path"])
    plant_a = {"result_id": "GMI833_V2_LEGACY_998_" + real["object_id"] + "_V2", "package": pkg, "theorem_name": real["object_id"] + "_V2", "maturity_M": "M4", "evidence_EV": "EV3"}
    plant_b = {"result_id": "GMI833_V2_LEGACY_997_" + real["object_id"][:-1], "package": pkg, "theorem_name": real["object_id"][:-1], "maturity_M": "M4", "evidence_EV": "EV3"}
    ra, _ = bind_row(inp, plant_a)
    rb, _ = bind_row(inp, plant_b)
    res.append({"id": "H3", "perturbation": "synthetic rows whose id is a real id with _V2 appended / a strict prefix of a real id",
                "quantity": "bindings", "baseline": 1, "perturbed": int(ra is not None) + int(rb is not None), "detected": ra is None and rb is None,
                "plants": [plant_a["result_id"], plant_b["result_id"]]})
    # H4 orphan delta
    delta = {"records": inp.delta["records"] + [{"result_id": "GMI833_V2_LEGACY_996_ORPHAN", "package": "nowhere", "maturity_M": "M4", "evidence_EV": "EV3"}]}
    inp2 = Inputs(inp.census, inp.gaps, inp.scores, delta, inp.regs, inp.depgraph, inp.schema)
    o2 = run_pass(inp2)
    orphan = [x for x in o2["refusals"] if x["kind"] == "V3_DELTA" and x["reason"] == "ORPHAN_DELTA_RESULT_ID_NOT_IN_V2"]
    res.append({"id": "H4", "perturbation": "v3 delta record naming a result_id not in v2", "quantity": "orphan-delta refusals",
                "baseline": out["result"]["refusals"]["by_kind"].get("V3_DELTA", 0), "perturbed": len(orphan), "detected": len(orphan) == 1
                and o2["result"]["population"]["maturity_level"]["after_populated"] == out["result"]["population"]["maturity_level"]["after_populated"]})
    # H5 duplicate register key
    census2 = {"frozen_source_sha": inp.census["frozen_source_sha"], "scientific_objects": inp.objects + [inp.objects[0]]}
    try:
        Inputs(census2, inp.gaps, inp.scores, inp.delta, inp.regs, inp.depgraph, inp.schema)
        dup_detected = False
    except PassError:
        dup_detected = True
    res.append({"id": "H5", "perturbation": "one census object duplicated", "quantity": "loader raises", "baseline": 0, "perturbed": int(dup_detected), "detected": dup_detected})
    # H6 ambiguous child edge: the real FAC-CTW edge, plus a fixture forcing two objects at one citation line
    real_amb = [x for x in out["refusals"] if x["kind"] == "DEPENDENCY_EDGE" and x["reason"] == "AMBIGUOUS_CHILD_IDENTITY"]
    dup_id = next(oid for oid, objs in inp.by_id.items() if len(objs) >= 2 and len({o["source_path"] for o in objs}) < len(objs))
    two = [o for o in inp.by_id[dup_id] if sum(1 for x in inp.by_id[dup_id] if x["source_path"] == o["source_path"]) >= 2][0]
    fixture = {"child": dup_id, "parent": "X-1", "parent_kind": "CORPUS_CLAIM", "relation": "USES", "citation": two["source_path"] + ":L0"}
    how, why = resolve_child(inp, fixture)
    res.append({"id": "H6", "perturbation": "child id declared in several places with no unique object at the citation",
                "quantity": "edge refusals", "baseline": 0, "perturbed": len(real_amb) + int(how is None),
                "detected": len(real_amb) >= 1 and how is None and why in ("AMBIGUOUS_CHILD_IDENTITY", "NO_OBJECT_AT_CITATION"),
                "real_refused_children": sorted(set(x["child"] for x in real_amb))})
    # H7 grade-table dip
    def dip(i):
        return "IMMATERIAL" if i == 7 else materiality_grade(i, inp.schema)
    v = monotonicity_violations(inp.schema, grade_fn=dip)["violations"]
    res.append({"id": "H7", "perturbation": "grade table dips to IMMATERIAL at index 7", "quantity": "monotonicity violations", "baseline": 0, "perturbed": v, "detected": v > 0})
    # H8 planted descendant that does not depend on the claim
    gaps2 = json.loads(json.dumps(out["gaps"]))
    g = next(x for x in gaps2 if x["descendants"])
    stranger = next(k for k, r in records.items() if not r["claim_dependencies"])
    g["descendants"].append(stranger)
    f = verify_descendants(gaps2, records)
    res.append({"id": "H8", "perturbation": "a register key with no dependencies planted as a descendant", "quantity": "descendant findings",
                "baseline": 0, "perturbed": len(f), "detected": any(x[2] == "DESCENDANT_DOES_NOT_DEPEND_ON_CLAIM" for x in f)})
    return res


def null_study(inp, out):
    rng = random.Random(NULL_SEED)
    true_count = out["result"]["binding"]["bound_rows"]
    pkgs = [r["package"] for r in inp.scores]
    counts = []
    for _ in range(NULL_TRIALS):
        perm = list(pkgs)
        rng.shuffle(perm)
        rows = [dict(r, package=p) for r, p in zip(inp.scores, perm)]
        b, _, _ = bind_all(inp, rows)
        counts.append(len(b))
    suffix_counts = []
    for t in range(NULL_TRIALS):
        rows = [dict(r, result_id=r["result_id"] + "_%d" % rng.randrange(10 ** 6), theorem_name=(r.get("theorem_name") or "") + "_%d" % t) for r in inp.scores]
        b, _, _ = bind_all(inp, rows)
        suffix_counts.append(len(b))
    return {
        "design": "%d seeded permutations of the package column over the %d scored rows; rows re-bound under B1/B2" % (NULL_TRIALS, len(inp.scores)),
        "seed": NULL_SEED, "true_bound_rows": true_count,
        "permuted_min": min(counts), "permuted_max": max(counts), "permuted_mean": str(Fraction(sum(counts), len(counts))),
        "draws_at_or_above_true": sum(1 for c in counts if c >= true_count),
        "true_beats_every_draw": all(c < true_count for c in counts),
        "suffix_null": {"design": "random suffix appended to every result_id and theorem_name", "bound_max": max(suffix_counts),
                        "must_be": 0, "caveat": "a miss is guaranteed by construction; not evidence of selectivity"},
    }


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def build(inp=None, write=True):
    inp = inp or Inputs()
    out = run_pass(inp)
    pf = verify_pointers(out["records"], inp)
    df = verify_descendants(out["gaps"], out["records"])
    out["result"]["pointer_verification"] = {"pointers_checked": sum(len(v) for r in out["records"].values() for v in r["provenance"].values()),
                                             "findings": len(pf), "no_alarm_on_real_register": len(pf) == 0}
    out["result"]["descendant_verification"] = {"descendant_entries_checked": sum(len(g["descendants"]) for g in out["gaps"]),
                                                "findings": len(df), "no_alarm_on_real_graph": len(df) == 0}
    out["decidability"] = decidability(out["records"], inp)
    out["result"]["decidability_summary"] = out["decidability"]["summary"]
    out["result"]["hostiles"] = hostiles(inp, out)
    out["result"]["null"] = null_study(inp, out)
    out["result"]["forbidden_promotions"] = [
        "CENSUS_FULLY_REGISTERED", "ALL_OBJECTS_SCORED", "ALL_PARENTS_EXHAUSTED", "DEPENDENCY_GRAPH_COMPLETE",
        "GMI_GAP_GRAPH_COMPLETE", "ISOLATED_GAP_IS_LEAF", "UNREGISTERED_MEANS_NONE", "POPULATED_MEANS_VERIFIED",
        "AA_ROW_EARNED", "RECURSION_EXHAUSTED", "ANALYTIC_PROOF", "M4_RESTORED_TO_W4_PARENT"]
    if write:
        delta_doc = {
            "schema": "GMI_833_CENSUS_REGISTER_DELTA_V1", "package": "gmi-833-census-registration-pass-v1",
            "claim_ceiling": CLAIM_CEILING, "supersedes_by_reference": CENSUS_INDEX, "census_frozen_source_sha": CENSUS_FROZEN_SHA,
            "semantics": {
                "delta_only": "only objects with at least one populated field are listed; every other census object carries maturity_level=UNKNOWN, evidence_level=UNKNOWN, the four list ledgers = the string UNREGISTERED, claim_dependencies=[]",
                "UNREGISTERED": "a string sentinel on a list field: no committed register binds to this object; NOT an empty list, NOT a claim that the object has no parents or assumptions",
                "UNKNOWN": "no scored row binds to this object by exact identity",
                "provenance": "one pointer per populated entry, aligned with the field's list; scalar fields carry the v2 pointer then the v3 delta pointer when applied",
                "register_key": "source_path:source_locator, unique over the 22553 census objects; object_id is never a key",
            },
            "population": out["result"]["population"], "binding": out["result"]["binding"], "edges": out["result"]["edges"],
            "records": [out["records"][k] for k in sorted(out["records"])],
            "package_level_results": sorted(out["package_level"], key=lambda p: p["result_id"]),
        }
        (HERE / "REGISTER_DELTA_V1.json").write_text(canonical(delta_doc), encoding="utf-8")
        (HERE / "GAP_GRAPH_V2.json").write_text(canonical({
            "schema": "GMI_GAP_GRAPH_V2", "package": "gmi-833-census-registration-pass-v1", "claim_ceiling": CLAIM_CEILING,
            "supersedes_by_reference": GAP_GRAPH, "frozen_source_sha": CENSUS_FROZEN_SHA,
            "materiality_rule": "gmi-833-aa-gap-object-v1 AAG-3, inputs unchanged; materiality_v1 keeps the census constant",
            "descendant_rule": "FREEZE_V1.md section 4.5; keys are register keys of REGISTER_DELTA_V1.json",
            "summary": out["result"]["gap_graph"], "gaps": out["gaps"]}), encoding="utf-8")
        (HERE / "DECIDABILITY_V1.json").write_text(canonical(out["decidability"]), encoding="utf-8")
        (HERE / "REFUSALS_V1.json").write_text(canonical({
            "schema": "GMI_833_CENSUS_REGISTRATION_REFUSALS_V1", "package": "gmi-833-census-registration-pass-v1",
            "summary": out["result"]["refusals"], "refusals": out["refusals"],
            "package_level_results_not_populating_objects": sorted(out["package_level"], key=lambda p: p["result_id"])}), encoding="utf-8")
    return out


def main(argv):
    out = build(write="--no-write" not in argv)
    sys.stdout.write(canonical(out["result"]))
    ok = (out["result"]["pointer_verification"]["findings"] == 0 and out["result"]["descendant_verification"]["findings"] == 0
          and all(h["detected"] for h in out["result"]["hostiles"]) and out["result"]["null"]["true_beats_every_draw"]
          and out["result"]["gap_graph"]["grade_counts"] == {"IMMATERIAL": 0, "MINOR": 0, "MATERIAL": 847, "CRITICAL": 293})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
