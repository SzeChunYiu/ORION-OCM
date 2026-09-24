#!/usr/bin/env python3
"""Route A for gmi-833-aa1-gap-graph-v1 (issue #839; #833 addendum AA/AD).

Builds `GMI_GAP_GRAPH_V3.json` from pinned corpus records, validates it, and
exposes the promotion evaluator, the parent-closure predicate, the result-record
validator and the AD research-loop validator. Every rule is fixed in
`FREEZE_V1.md` section 4; nothing here is tuned to an outcome.

Reuse, not re-derivation: materiality, the four-grade lattice, the bare-`closed`
detector and the REPAIR_DELTA emitter are imported from
`research/gmi-833-aa-gap-object-v1/gap_object_v1.py`. Route B
(`independent_gap_graph_oracle_v1.py`) imports nothing from this file or from
that module.

stdlib only; exact integers only; Python 3.8-compatible.

Usage:
  gap_graph_v1.py                       build and write GMI_GAP_GRAPH_V3.json, print the summary
  gap_graph_v1.py --check               rebuild in memory; exit 1 unless byte-identical to the file
  gap_graph_v1.py --validate [PATH]     validate a graph file; exit 1 on any finding
  gap_graph_v1.py --parent-closure-gate KEY   exit 1 when closing PARENT:KEY is refused
  gap_graph_v1.py --promote NODE_ID GRADE     exit 1 when the promotion is refused
  gap_graph_v1.py --validate-loop PATH  validate an AD loop document; exit 1 on any finding
  gap_graph_v1.py --validate-records PATH     validate a result-record document
"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
GAP_OBJECT_DIR = os.path.join(REPO, "research", "gmi-833-aa-gap-object-v1")


def _load_gap_object():
    """Load the gap-object module by file path. sys.path is left untouched: that
    package ships its own check_receipt_v1.py, which must never shadow ours."""
    if "gap_object_v1" in sys.modules:
        return sys.modules["gap_object_v1"]
    spec = importlib.util.spec_from_file_location(
        "gap_object_v1", os.path.join(GAP_OBJECT_DIR, "gap_object_v1.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gap_object_v1"] = mod
    spec.loader.exec_module(mod)
    return mod


GO = _load_gap_object()

PKG = "gmi-833-aa1-gap-graph-v1"
PKG_REL = "research/" + PKG
CLAIM_CEILING = "GMI_833_RECURSIVE_GAP_GOVERNANCE_V1_AT_DECLARED_SCOPE"
SOURCE_MAIN = "cc36a3096031f871c430c79d6fbd64890388c772"

INPUTS = {
    "gap_graph_v2": "research/gmi-833-census-registration-pass-v1/GAP_GRAPH_V2.json",
    "register_delta": "research/gmi-833-census-registration-pass-v1/REGISTER_DELTA_V1.json",
    "corpus_index": "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json",
    "gap_graph_v1": "research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json",
    "duplicate_adjudication": "research/gmi-833-depgraph-adjudication-v1/DUPLICATE_ADJUDICATION_V1.json",
    "overstrong_adjudication": "research/gmi-833-depgraph-adjudication-v1/OVERSTRONG_ADJUDICATION_V1.json",
    "open_gap_schema": "research/gmi-833-aa-gap-object-v1/OPEN_GAP_SCHEMA_V1.json",
    "gap_object_module": "research/gmi-833-aa-gap-object-v1/gap_object_v1.py",
    "flagship_registry": "research/gmi-833-aj0-foundation-scope-v1/FOUNDATION_LAYER_REGISTRY.json",
    "registrations": "research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json",
}
PINS = {
    "gap_graph_v2": "20cd106f10f65e25a527a1695f1113c96cf8ac41",
    "register_delta": "be84eb34ff9fa03dbeb21f33a4df4e41c2d44f70",
    "corpus_index": "709159c53c6284366aaf1f05380f5fada8d81a98",
    "gap_graph_v1": "61006b756721c748f8dcc797c755abd25cc42956",
    "duplicate_adjudication": "ac6b41b4cce62f71081ede53c9c5d2ca399d5687",
    "overstrong_adjudication": "f56e1245d216c6ad93090ea2f73156c9ec0623b4",
    "open_gap_schema": "9050c2e01e44347aa2b19710286890be1a5eb21d",
    "gap_object_module": "4d39fbacd2acb79d8f170d844abcb8103b4bd195",
    "flagship_registry": "5caefcd3a0b812a1f2557dcc228f88de04db5cee",
    "registrations": "66c3b7e4ef91e096f0ece2720af4645bebe75238",
}
OWN = {
    "schema": PKG_REL + "/GAP_GRAPH_SCHEMA_V1.json",
    "template": PKG_REL + "/AD_LOOP_TEMPLATE_V1.json",
    "loops": PKG_REL + "/AD_LOOP_RECORDS_V1.json",
    "results": PKG_REL + "/RESULT_RECORDS_V1.json",
}
GRAPH_REL = PKG_REL + "/GMI_GAP_GRAPH_V3.json"
GRADES = ["LOCALLY_CLOSED", "HOSTILE_CLOSED", "REPLICATED_CLOSED", "REAL_SCALE_CLOSED"]
CLOSURE_FLAGS = ["local_checks_pass", "independent_route", "hostiles_detected",
                 "independent_replication", "real_scale_run"]


def rp(rel):
    return os.path.join(REPO, *rel.split("/"))


def read_bytes(rel):
    with open(rp(rel), "rb") as fh:
        return fh.read()


def load_json(rel):
    return json.loads(read_bytes(rel).decode("utf-8"))


def git_blob_sha(rel):
    data = read_bytes(rel)
    h = hashlib.sha1()
    h.update(b"blob %d\x00" % len(data))
    h.update(data)
    return h.hexdigest()


def load_schema():
    return load_json(OWN["schema"])


def load_template():
    return load_json(OWN["template"])


def load_open_gap_schema():
    return GO.load_schema(rp(INPUTS["open_gap_schema"]))


def pin_report():
    """Blob sha of every pinned input, and whether it matches the freeze pin."""
    out = {}
    for k in sorted(INPUTS):
        live = git_blob_sha(INPUTS[k])
        out[k] = {"path": INPUTS[k], "pinned": PINS[k], "live": live, "match": live == PINS[k]}
    return out


def load_inputs():
    return {
        "g2": load_json(INPUTS["gap_graph_v2"]),
        "rd": load_json(INPUTS["register_delta"]),
        "ci": load_json(INPUTS["corpus_index"]),
        "v1": load_json(INPUTS["gap_graph_v1"]),
        "da": load_json(INPUTS["duplicate_adjudication"]),
        "oa": load_json(INPUTS["overstrong_adjudication"]),
        "fl": load_json(INPUTS["flagship_registry"]),
        "rg": load_json(INPUTS["registrations"]),
        "schema": load_schema(),
        "template": load_template(),
        "ogs": load_open_gap_schema(),
        "loops": load_json(OWN["loops"]),
        "results": load_json(OWN["results"]),
    }


# ------------------------------------------------------------------ helpers
def nonempty_str(x):
    return isinstance(x, str) and x.strip() != ""


def package_of(path):
    parts = str(path).split("/")
    if len(parts) >= 2 and parts[0] == "research":
        return parts[1]
    return parts[0]


def empty_evidence():
    return dict((k, False) for k in CLOSURE_FLAGS)


def materiality_of(inputs, ogs):
    """(index, grade) by the AAG-3 function of gmi-833-aa-gap-object-v1; raises
    ValueError on any undeclared input."""
    if not isinstance(inputs, dict):
        raise ValueError("materiality inputs missing")
    sev, ev, sc, bl = (inputs.get("severity"), inputs.get("evidence_mode"),
                       inputs.get("scope"), inputs.get("blast"))
    if sev not in ogs["severity_rank"] or ev not in ogs["evidence_mode_rank"] \
            or sc not in ogs["scope_rank"]:
        raise ValueError("undeclared materiality input")
    if isinstance(bl, bool) or not isinstance(bl, int) or bl < 0:
        raise ValueError("blast must be a non-negative integer")
    idx = GO.materiality_index(ogs["severity_rank"][sev], ogs["evidence_mode_rank"][ev],
                               ogs["scope_rank"][sc], bl, ogs["blast_rank_cap"])
    return idx, GO.materiality_grade(idx, ogs)


def rederive_rule(decls):
    """The DUPID adjudication rule whose predicate the declarations satisfy,
    first match in the adjudication's own order (FREEZE 4.3)."""
    if len(decls) < 2:
        return None
    stmts = [d.get("statement") for d in decls]
    if len(set(stmts)) == 1:
        return "B1_VERBATIM_REDECLARATION"
    if len(set(" ".join((s or "").split()).lower() for s in stmts)) == 1:
        return "B2_CANONICAL_REDECLARATION"
    for i, a in enumerate(decls):
        for j, b in enumerate(decls):
            if i == j:
                continue
            if b["source_path"].split("/")[-1] in (a.get("statement") or ""):
                return "B3_POINTER_TO_SAME_CONTENT"
    return "B4_ID_COLLISION_CONTENT_DIFFERS"


# ------------------------------------------------------------ result records
def slot_is_blank(s):
    return all(s.get(k) is None for k in ("method_class", "evidence_pointer", "search_scope", "outcome"))


def slot_is_filled(s, schema):
    return (s.get("method_class") in schema["counterexample_method_classes"]
            and nonempty_str(s.get("evidence_pointer"))
            and nonempty_str(s.get("search_scope"))
            and s.get("outcome") in schema["slot_outcomes"])


def flagship_slots_ok(rec, schema):
    """FREEZE 4.7. Returns (ok, detail). Fail-closed on every malformed input."""
    if not isinstance(rec, dict):
        return False, "RECORD_MALFORMED"
    flag = rec.get("is_flagship")
    is_flagship = flag if isinstance(flag, bool) else True
    if not is_flagship:
        return True, "NOT_FLAGSHIP"
    slots = rec.get("counterexample_methods")
    if not isinstance(slots, list):
        return False, "SLOT_DATA_MALFORMED"
    filled = []
    for s in slots:
        if not isinstance(s, dict):
            return False, "SLOT_DATA_MALFORMED"
        if slot_is_filled(s, schema):
            filled.append(s)
    if any(s.get("outcome") == "COUNTEREXAMPLE_FOUND" for s in filled):
        return False, "COUNTEREXAMPLE_ON_RECORD"
    classes = set(s["method_class"] for s in filled)
    if len(classes) < schema["min_distinct_methods_for_hostile_closed"]:
        return False, "FEWER_THAN_TWO_DISTINCT_METHODS"
    return True, "TWO_DISTINCT_METHODS"


def validate_result_record(rec, schema):
    """FREEZE 4.10. Returns a sorted list of problem strings (empty = valid)."""
    probs = []
    if not isinstance(rec, dict):
        return ["not an object"]
    for f in schema["result_record_fields"]:
        if f not in rec:
            probs.append("missing:" + f)
    if probs:
        return sorted(probs)
    if not nonempty_str(rec["result_id"]):
        probs.append("result_id")
    if not nonempty_str(rec["statement"]):
        probs.append("statement")
    if rec["scope"] not in schema["scopes"]:
        probs.append("scope")
    if not isinstance(rec["is_flagship"], bool):
        probs.append("is_flagship")
    elif rec["scope"] == "FLAGSHIP" and not rec["is_flagship"]:
        probs.append("is_flagship_vs_scope")
    sent = schema["unregistered_sentinel"]
    for f in schema["result_record_list_fields"]:
        v = rec[f]
        if v == sent:
            continue
        if not isinstance(v, list) or not v or not all(nonempty_str(x) for x in v):
            probs.append("list:" + f)
    slots = rec["counterexample_methods"]
    if not isinstance(slots, list):
        probs.append("counterexample_methods")
    else:
        if rec.get("is_flagship") is True and len(slots) < schema["min_flagship_slots"]:
            probs.append("flagship_slots")
        for i, s in enumerate(slots):
            if not isinstance(s, dict) or any(k not in s for k in schema["slot_fields"]):
                probs.append("slot:%d" % i)
            elif s.get("slot") != i + 1:
                probs.append("slot_index:%d" % i)
            elif not (slot_is_blank(s) or slot_is_filled(s, schema)):
                probs.append("slot_partial:%d" % i)
    pd = rec["prior_disclosure"]
    if not isinstance(pd, dict) or not nonempty_str(pd.get("freeze_pointer")) \
            or pd.get("outcome_timing") not in schema["outcome_timing"]:
        probs.append("prior_disclosure")
    ev = rec["evidence"]
    if not isinstance(ev, dict) or not nonempty_str(ev.get("evidence_level")) \
            or not nonempty_str(ev.get("maturity_level")):
        probs.append("evidence")
    if rec["closure_state"] not in schema["closure_states"]:
        probs.append("closure_state")
    ce = rec["closure_evidence"]
    if not isinstance(ce, dict) or sorted(ce.keys()) != sorted(CLOSURE_FLAGS) \
            or not all(isinstance(ce[k], bool) for k in CLOSURE_FLAGS):
        probs.append("closure_evidence")
    if not isinstance(rec["provenance"], dict):
        probs.append("provenance")
    return sorted(probs)


def flagship_records(fl, rg):
    """FREEZE 4.10: one record per AJ0 flagship result, copied by exact package
    equality with a pointer per field; UNREGISTERED where no source exists."""
    reg_path = INPUTS["registrations"]
    fl_path = INPUTS["flagship_registry"]
    objs = rg["objects"]
    out = []
    for i, f in enumerate(fl["flagship_results"]):
        rid = f["id"]
        pkg = rid.split("/", 1)[1] if "/" in rid else rid
        rows = [o for o in objs if o.get("package") == pkg]
        prov = {}

        def take(field):
            if len(rows) != 1:
                return "UNREGISTERED"
            c = (rows[0].get("fields") or {}).get(field, {}).get("content")
            if isinstance(c, list) and c and all(nonempty_str(x) for x in c):
                prov[field] = "%s#%s.fields.%s" % (reg_path, rows[0]["result_id"], field)
                return list(c)
            return "UNREGISTERED"

        assumptions = take("assumptions")
        falsifiers = take("falsifiers")
        parents = take("strongest_parents")
        fe = take("forbidden_extrapolations")
        deps = f.get("dependencies")
        if isinstance(deps, list) and deps and all(nonempty_str(x) for x in deps):
            deps = list(deps)
            prov["dependencies"] = "%s#flagship_results[%d].dependencies" % (fl_path, i)
        else:
            deps = "UNREGISTERED"
        fp = f.get("forbidden_promotions")
        if isinstance(fp, list) and fp and all(nonempty_str(x) for x in fp):
            base = fe if isinstance(fe, list) else []
            fe = base + [x for x in fp if x not in base]
            ptr = "%s#flagship_results[%d].forbidden_promotions" % (fl_path, i)
            prov["forbidden_extrapolations"] = (prov["forbidden_extrapolations"] + " ; " + ptr
                                                if "forbidden_extrapolations" in prov else ptr)
        freeze_rel = "research/%s/FREEZE_V1.md" % pkg
        freeze = freeze_rel if os.path.isfile(rp(freeze_rel)) else "UNREGISTERED"
        prov["statement"] = "%s#flagship_results[%d]" % (fl_path, i)
        rec = {
            "result_id": rid,
            "statement": "flagship result %s: registry status %s, primary layer %s"
                         % (rid, f.get("status"), f.get("primary_layer")),
            "scope": "FLAGSHIP",
            "is_flagship": True,
            "assumptions": assumptions,
            "dependencies": deps,
            "falsifiers": falsifiers,
            "counterexample_methods": [
                {"slot": 1, "method_class": None, "evidence_pointer": None,
                 "search_scope": None, "outcome": None},
                {"slot": 2, "method_class": None, "evidence_pointer": None,
                 "search_scope": None, "outcome": None},
            ],
            "strongest_parents": parents,
            "prior_disclosure": {"freeze_pointer": freeze, "outcome_timing": "UNVERIFIED"},
            "evidence": {"evidence_level": "UNREGISTERED", "maturity_level": "UNREGISTERED"},
            "forbidden_extrapolations": fe,
            "closure_state": "OPEN",
            "closure_evidence": empty_evidence(),
            "provenance": prov,
        }
        out.append(rec)
    return out


# ------------------------------------------------------------------ builder
def build(inputs=None):
    I = inputs if inputs is not None else load_inputs()
    S, OGS = I["schema"], I["ogs"]
    gaps = I["g2"]["gaps"]
    decl = {}
    key2oid = {}
    for o in I["ci"]["scientific_objects"]:
        decl.setdefault(o["object_id"], []).append(o)
        key2oid[o["source_path"] + ":" + o["source_locator"]] = o["object_id"]
    da = dict((a["gap_id"], a) for a in I["da"]["dupid_gaps"]["adjudications"])
    oa = {}
    for a in I["oa"]["adjudications"]:
        oa.setdefault((a["gap_id"], a["claim_id"]), []).append(a)
    repair_rules = S["repair_rule_assumptions"]

    nodes = {}
    edges = set()
    occ = {}
    by_claim = {}
    corpus_ids = []
    unmapped_descendant_keys = 0

    # corpus gap nodes (FREEZE 4.1) and closure (4.3)
    for i, g in enumerate(gaps):
        occ[g["id"]] = occ.get(g["id"], 0) + 1
        k = occ[g["id"]]
        nid = "GAP:%s#%d" % (g["id"], k)
        mi = g["materiality_inputs"]
        node = {
            "id": nid, "kind": "GAP", "key": g["id"], "occurrence": k, "origin": "CORPUS",
            "pointer": "%s#gaps[%d]" % (INPUTS["gap_graph_v2"], i),
            "gap_kind": g["id"].split("-")[1],
            "claim_id": g["claim_id"], "parent_result": g["parent_result"],
            "materiality": g["materiality"], "materiality_index": g["materiality_index"],
            "materiality_inputs": dict((x, mi[x]) for x in ("severity", "evidence_mode", "scope", "blast")),
            "closure_state": "OPEN", "closure_evidence": empty_evidence(),
        }
        if node["gap_kind"] == "DUPID":
            a = da.get(g["id"])
            rr = rederive_rule(decl.get(g["claim_id"], []))
            if a is not None:
                node["adjudication"] = {"source": INPUTS["duplicate_adjudication"],
                                        "verdict": a["verdict"], "reason": a["reason"],
                                        "rederived_reason": rr}
                if a["verdict"] == "DUPLICATE" and a["reason"] in repair_rules and rr == a["reason"]:
                    node["closure_state"] = "LOCALLY_CLOSED"
                    node["closure_rule"] = a["reason"]
                    node["closure_evidence"]["local_checks_pass"] = True
                    node["closure_evidence"]["independent_route"] = True
        elif node["gap_kind"] == "FIN2UNIV":
            lst = oa.get((g["id"], g["claim_id"]), [])
            if len(lst) >= k:
                a = lst[k - 1]
                node["adjudication"] = {"source": INPUTS["overstrong_adjudication"],
                                        "verdict": a["verdict"], "reason": a["reason"],
                                        "basis": a["basis"], "object_source": a.get("source")}
        nodes[nid] = node
        corpus_ids.append(nid)
        by_claim.setdefault(g["claim_id"], []).append(nid)

    # R1 ID_PRECEDENCE
    for cid in sorted(by_claim):
        members = by_claim[cid]
        for d in members:
            if nodes[d]["gap_kind"] != "DUPID":
                continue
            for f in members:
                if nodes[f]["gap_kind"] == "FIN2UNIV":
                    edges.add(("DESCENDANT", d, f, "R1_ID_PRECEDENCE"))
    # R2 DEPENDENCY_PROPAGATION (reads GAP_GRAPH_V2 descendants)
    for i, g in enumerate(gaps):
        src = corpus_ids[i]
        for key in g.get("descendants") or []:
            oid = key2oid.get(key)
            if oid is None:
                unmapped_descendant_keys += 1
                continue
            for dst in by_claim.get(oid, []):
                if dst != src:
                    edges.add(("DESCENDANT", src, dst, "R2_DEPENDENCY_PROPAGATION"))

    # AD-loop extracted gaps (FREEZE 4.9) and R3 REPAIR_SUCCESSOR
    closed_b1_cross = sorted(
        n for n in corpus_ids
        if nodes[n].get("closure_rule") == "B1_VERBATIM_REDECLARATION"
        and len(set(package_of(d["source_path"]) for d in decl.get(nodes[n]["claim_id"], []))) >= 2)
    closed_b3 = sorted(n for n in corpus_ids
                       if nodes[n].get("closure_rule") == "B3_POINTER_TO_SAME_CONTENT")
    source_sets = {"B1_CROSS_PACKAGE": closed_b1_cross, "B3_ALL": closed_b3, "NONE": []}
    extracted_ids = []
    for li, loop in enumerate(I["loops"].get("loops", [])):
        for ii, it in enumerate(loop.get("iterations", [])):
            for gi, e in enumerate(it.get("extracted_gaps", [])):
                occ[e["id"]] = occ.get(e["id"], 0) + 1
                k = occ[e["id"]]
                nid = "GAP:%s#%d" % (e["id"], k)
                mi = e["materiality_inputs"]
                idx, grade = materiality_of(mi, OGS)
                nodes[nid] = {
                    "id": nid, "kind": "GAP", "key": e["id"], "occurrence": k, "origin": "AD_LOOP",
                    "pointer": "%s#loops[%d].iterations[%d].extracted_gaps[%d]" % (OWN["loops"], li, ii, gi),
                    "gap_kind": "AD", "claim_id": e["claim_id"], "parent_result": e["parent_result"],
                    "materiality": grade, "materiality_index": idx,
                    "materiality_inputs": dict((x, mi[x]) for x in ("severity", "evidence_mode", "scope", "blast")),
                    "closure_state": "OPEN", "closure_evidence": empty_evidence(),
                    "source_rule": e["source_rule"],
                }
                extracted_ids.append(nid)
                for s in source_sets.get(e["source_rule"], []):
                    edges.add(("DESCENDANT", s, nid, "R3_REPAIR_SUCCESSOR"))

    gap_ids = corpus_ids + extracted_ids

    # claims, dependencies, parents
    claim_keys = set(nodes[n]["claim_id"] for n in gap_ids)
    for r in I["rd"]["records"]:
        deps = r.get("claim_dependencies")
        if isinstance(deps, list) and deps:
            claim_keys.add(r["object_id"])
            for p in deps:
                claim_keys.add(p)
                edges.add(("DEPENDS_ON", "CLAIM:" + r["object_id"], "CLAIM:" + p,
                           "REGISTER_DELTA_CLAIM_DEPENDENCIES"))
    for c in claim_keys:
        nodes["CLAIM:" + c] = {"id": "CLAIM:" + c, "kind": "CLAIM", "key": c}
    for n in gap_ids:
        edges.add(("GAP_ON", n, "CLAIM:" + nodes[n]["claim_id"], "CLAIM_ID_FIELD"))
        pid = "PARENT:" + nodes[n]["parent_result"]
        if pid not in nodes:
            nodes[pid] = {"id": pid, "kind": "PARENT", "key": nodes[n]["parent_result"],
                          "closure_state": "OPEN", "closure_evidence": empty_evidence()}
        edges.add(("PARENT_OF", pid, n, "PARENT_RESULT_FIELD"))

    # repair records of closed gaps (FREEZE 4.4), via the gap-object emitter
    succ = {}
    for (k, s, d, _r) in edges:
        if k == "DESCENDANT":
            succ.setdefault(s, set()).add(d)
    for n in corpus_ids:
        node = nodes[n]
        if node["closure_state"] != "LOCALLY_CLOSED":
            continue
        rule = repair_rules[node["closure_rule"]]
        aid = "ASSUMPTION:" + rule["id"]
        if aid not in nodes:
            nodes[aid] = {"id": aid, "kind": "ASSUMPTION", "key": rule["id"], "text": rule["text"],
                          "introduced_by_rule": node["closure_rule"]}
        edges.add(("INTRODUCES", n, aid, "REPAIR_DELTA_NEW_ASSUMPTIONS"))
        node["repair_delta"] = GO.emit_repair_delta(
            {"id": n},
            "adjudicated DUPLICATE (%s) by gmi-833-depgraph-adjudication-v1; predicate re-derived "
            "from CORPUS_INDEX_V1 declarations of claim %s" % (node["closure_rule"], node["claim_id"]),
            [rule["id"]], sorted(succ.get(n, ())), "LOCALLY_CLOSED", OGS)

    # result records
    for rec in flagship_records(I["fl"], I["rg"]) + list(I["results"].get("records", [])):
        rid = "RESULT:" + rec["result_id"]
        nodes[rid] = {"id": rid, "kind": "RESULT", "key": rec["result_id"],
                      "closure_state": rec["closure_state"],
                      "closure_evidence": dict(rec["closure_evidence"]), "record": rec}

    graph = {
        "schema": S["graph_schema"],
        "package": PKG,
        "issue": 839,
        "claim_ceiling": CLAIM_CEILING,
        "source_main": SOURCE_MAIN,
        "inputs": dict((k, {"path": INPUTS[k], "blob": PINS[k]}) for k in sorted(INPUTS)),
        "rules": "FREEZE_V1.md section 4; GAP_GRAPH_SCHEMA_V1.json",
        "nodes": [nodes[k] for k in sorted(nodes)],
        "edges": [list(e) for e in sorted(edges)],
    }
    ctx = Context(graph, S, OGS)
    for n in gap_ids:
        nodes[n]["descendant_gaps"] = sorted(ctx.closure(n))
    for c in sorted(claim_keys):
        nodes["CLAIM:" + c]["unresolved_descendant_gaps"] = sorted(ctx.claim_unresolved(c))
    graph["build_notes"] = {"unmapped_descendant_register_keys": unmapped_descendant_keys}
    return graph


def dumps_graph(graph):
    """Fixed byte order: header keys sorted, one node / one edge per line."""
    head = dict((k, v) for k, v in graph.items() if k not in ("nodes", "edges"))
    lines = ["{"]
    for k in sorted(head):
        lines.append(" %s: %s," % (json.dumps(k), json.dumps(head[k], sort_keys=True)))
    lines.append(' "nodes": [')
    lines.append(",\n".join("  " + json.dumps(n, sort_keys=True) for n in graph["nodes"]))
    lines.append(" ],")
    lines.append(' "edges": [')
    lines.append(",\n".join("  " + json.dumps(e) for e in graph["edges"]))
    lines.append(" ]")
    lines.append("}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- analysis
class Context(object):
    """Indexes a graph once: nodes by id (first occurrence), valid adjacency,
    transitive DESCENDANT closure, unresolved-CRITICAL set."""

    def __init__(self, graph, schema, ogs):
        self.S, self.OGS = schema, ogs
        self.N = {}
        for n in graph.get("nodes", []):
            if isinstance(n, dict) and n.get("id") not in self.N:
                self.N[n.get("id")] = n
        self.out, self.inc = {}, {}
        ek = schema["edge_kinds"]
        for e in graph.get("edges", []):
            if not (isinstance(e, list) and len(e) >= 3):
                continue
            k, s, d = e[0], e[1], e[2]
            if k not in ek or s not in self.N or d not in self.N:
                continue
            if self.N[s].get("kind") not in ek[k]["source"] or self.N[d].get("kind") not in ek[k]["target"]:
                continue
            self.out.setdefault(k, {}).setdefault(s, set()).add(d)
            self.inc.setdefault(k, {}).setdefault(d, set()).add(s)
        self._closure = {}

    def succ(self, kind, n):
        return self.out.get(kind, {}).get(n, set())

    def pred(self, kind, n):
        return self.inc.get(kind, {}).get(n, set())

    def closure(self, n):
        if n in self._closure:
            return self._closure[n]
        seen, stack = set(), [n]
        while stack:
            u = stack.pop()
            for v in self.succ("DESCENDANT", u):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        self._closure[n] = seen
        return seen

    def unresolved(self, n):
        node = self.N.get(n)
        return node is not None and node.get("kind") == "GAP" and node.get("closure_state") not in GRADES

    def unresolved_critical(self, n):
        return self.unresolved(n) and self.N[n].get("materiality") == self.S["blocking_materiality"]

    def blocking_descendants(self, n):
        return sorted(x for x in self.closure(n) if self.unresolved_critical(x))

    def cone(self, parent):
        out = set()
        for g in self.succ("PARENT_OF", parent):
            out.add(g)
            out |= self.closure(g)
        return out

    def claim_unresolved(self, c):
        cid = "CLAIM:%s" % (c,)
        down, stack = set([cid]), [cid]
        while stack:
            u = stack.pop()
            for v in self.pred("DEPENDS_ON", u):
                if v not in down:
                    down.add(v)
                    stack.append(v)
        gaps = set()
        for x in down:
            for g in self.pred("GAP_ON", x):
                gaps.add(g)
                gaps |= self.closure(g)
        return set(g for g in gaps if self.unresolved(g))


def evaluate_promotion(graph, node_id, requested, schema=None, ogs=None, forbidden=None, ctx=None):
    """Would holding `requested` at `node_id` be legitimate? Fail-closed."""
    S = schema or load_schema()
    OGS = ogs or load_open_gap_schema()
    forbidden = set(S["forbidden_grades_on_real_graph"]) if forbidden is None else set(forbidden)
    ctx = ctx or Context(graph, S, OGS)
    reasons = set()
    if requested not in GRADES:
        bare = isinstance(requested, str) and bool(GO.bare_closed_hits(requested))
        return {"granted": False, "reasons": ["BARE_CLOSED" if bare else "UNKNOWN_CLOSURE_STATE"]}
    n = ctx.N.get(node_id)
    if n is None:
        return {"granted": False, "reasons": ["MISSING_PARENT"]}
    ev = n.get("closure_evidence") if isinstance(n.get("closure_evidence"), dict) else {}
    req = [g["requires"] for g in OGS["closure_grades"] if g["grade"] == requested][0]
    if any(ev.get(k) is not True for k in req):
        reasons.add("LATTICE_EVIDENCE_MISSING")
    if requested in forbidden:
        reasons.add("FORBIDDEN_GRADE_AWARDED")
    above_local = GRADES.index(requested) > 0
    kind = n.get("kind")
    if kind == "GAP":
        rd = n.get("repair_delta")
        fields = [f["key"] for f in OGS["repair_delta_fields"]]
        rd_ok = (isinstance(rd, dict) and all(f in rd for f in fields)
                 and rd.get("closed_gap_id") == node_id
                 and nonempty_str(rd.get("repair_description"))
                 and isinstance(rd.get("new_assumptions"), list)
                 and isinstance(rd.get("new_gaps"), list)
                 and rd.get("interrogation_answered") is True
                 and rd.get("closure_grade_awarded") == requested)
        if not rd_ok:
            reasons.add("CLOSED_WITHOUT_REPAIR_DELTA")
        if not (isinstance(rd, dict) and isinstance(rd.get("new_assumptions"), list)
                and len(rd["new_assumptions"]) > 0):
            reasons.add("CLOSED_WITHOUT_NEW_ASSUMPTIONS")
        if above_local and ctx.blocking_descendants(node_id):
            reasons.add("CRITICAL_DESCENDANT_BLOCKS_PROMOTION")
    elif kind == "RESULT":
        if above_local and not flagship_slots_ok(n.get("record"), S)[0]:
            reasons.add("FLAGSHIP_METHODS_MISSING")
    elif kind == "PARENT":
        if any(ctx.unresolved_critical(x) for x in ctx.cone(node_id)):
            reasons.add("PARENT_CLOSED_WITH_CRITICAL_DESCENDANT")
    else:
        reasons.add("UNKNOWN_KIND")
    return {"granted": not reasons, "reasons": sorted(reasons)}


def parent_closure_gate(graph, parent_key, schema=None, ogs=None, ctx=None):
    """FREEZE 4.5: may PARENT:<key> leave OPEN?"""
    S = schema or load_schema()
    OGS = ogs or load_open_gap_schema()
    ctx = ctx or Context(graph, S, OGS)
    pid = "PARENT:" + parent_key
    if pid not in ctx.N:
        return {"parent": pid, "closure_permitted": False, "reason": "MISSING_PARENT",
                "unresolved_critical": []}
    bad = sorted(x for x in ctx.cone(pid) if ctx.unresolved_critical(x))
    return {"parent": pid, "closure_permitted": not bad,
            "reason": "PARENT_CLOSED_WITH_CRITICAL_DESCENDANT" if bad else "NONE",
            "unresolved_critical": bad}


def tarjan_scc(adj):
    """Iterative Tarjan. Returns the list of SCCs (each a sorted list)."""
    index, low, on, stack, out = {}, {}, set(), [], []
    counter = [0]
    for root in sorted(adj):
        if root in index:
            continue
        work = [(root, iter(sorted(adj.get(root, ()))))]
        index[root] = low[root] = counter[0]
        counter[0] += 1
        stack.append(root)
        on.add(root)
        while work:
            v, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter[0]
                    counter[0] += 1
                    stack.append(w)
                    on.add(w)
                    work.append((w, iter(sorted(adj.get(w, ())))))
                    advanced = True
                    break
                elif w in on:
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                out.append(sorted(comp))
    return out


def cycle_report(ctx):
    rep = {}
    for k in ("DESCENDANT", "DEPENDS_ON"):
        adj = ctx.out.get(k, {})
        rep[k] = {"cycles": sorted(c for c in tarjan_scc(adj) if len(c) > 1),
                  "self_loops": sorted(v for v in adj if v in adj[v])}
    return rep


def validate(graph, schema=None, ogs=None, forbidden=None):
    """FREEZE 4.8. Sorted list of [code, subject]; empty means valid."""
    S = schema or load_schema()
    OGS = ogs or load_open_gap_schema()
    forb = set(S["forbidden_grades_on_real_graph"]) if forbidden is None else set(forbidden)
    F = set()
    nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
    edges = graph.get("edges", []) if isinstance(graph, dict) else []
    count = {}
    for n in nodes:
        nid = n.get("id") if isinstance(n, dict) else None
        count[nid] = count.get(nid, 0) + 1
    for nid in count:
        if count[nid] > 1:
            F.add(("DUPLICATE_NODE_ID", str(nid)))
    ctx = Context(graph if isinstance(graph, dict) else {}, S, OGS)
    N = ctx.N
    for nid, n in N.items():
        if n.get("kind") not in S["node_kinds"]:
            F.add(("UNKNOWN_KIND", str(nid)))
    ek = S["edge_kinds"]
    for e in edges:
        if not (isinstance(e, list) and len(e) >= 3):
            F.add(("UNKNOWN_KIND", "edge:MALFORMED"))
            continue
        k, s, d = e[0], e[1], e[2]
        sub = "edge:%s|%s|%s" % (k, s, d)
        if k not in ek:
            F.add(("UNKNOWN_KIND", sub))
        elif s not in N or d not in N:
            F.add(("MISSING_PARENT", sub))
        elif N[s].get("kind") not in ek[k]["source"] or N[d].get("kind") not in ek[k]["target"]:
            F.add(("EDGE_ENDPOINT_KIND", sub))
    for nid, n in N.items():
        kind = n.get("kind")
        if kind == "GAP":
            pid = "PARENT:%s" % (n.get("parent_result"),)
            if pid not in N:
                F.add(("MISSING_PARENT", nid + "|parent_result"))
            if nid not in ctx.succ("PARENT_OF", pid):
                F.add(("ORPHAN_GAP", nid))
            if "CLAIM:%s" % (n.get("claim_id"),) not in N:
                F.add(("MISSING_PARENT", nid + "|claim_id"))
            try:
                idx, grade = materiality_of(n.get("materiality_inputs"), OGS)
                if idx != n.get("materiality_index") or grade != n.get("materiality"):
                    F.add(("MATERIALITY_MISMATCH", nid))
            except ValueError:
                F.add(("MATERIALITY_MISMATCH", nid))
            if "descendant_gaps" in n and n.get("descendant_gaps") != sorted(ctx.closure(nid)):
                F.add(("DESCENDANT_RECORD_MISMATCH", nid))
        elif kind == "ASSUMPTION":
            if not ctx.pred("INTRODUCES", nid):
                F.add(("ORPHAN_ASSUMPTION", nid))
        elif kind == "CLAIM":
            if not any(ctx.succ(k, nid) or ctx.pred(k, nid) for k in ek):
                F.add(("ORPHAN_CLAIM", nid))
            if "unresolved_descendant_gaps" in n and \
                    n.get("unresolved_descendant_gaps") != sorted(ctx.claim_unresolved(n.get("key"))):
                F.add(("DESCENDANT_RECORD_MISMATCH", nid))
        elif kind == "RESULT":
            rec = n.get("record")
            if not isinstance(rec, dict) or validate_result_record(rec, S) \
                    or rec.get("closure_state") != n.get("closure_state") \
                    or rec.get("result_id") != n.get("key"):
                F.add(("RESULT_RECORD_INVALID", nid))
        if kind in ("GAP", "RESULT", "PARENT"):
            st = n.get("closure_state")
            if st not in S["closure_states"]:
                bare = isinstance(st, str) and bool(GO.bare_closed_hits(st))
                F.add(("BARE_CLOSED" if bare else "UNKNOWN_CLOSURE_STATE", nid))
                continue
            if st == "OPEN":
                continue
            for r in evaluate_promotion(graph, nid, st, S, OGS, forb, ctx)["reasons"]:
                F.add((r, nid))
            if kind == "GAP":
                rd = n.get("repair_delta")
                if isinstance(rd, dict):
                    for a in rd.get("new_assumptions") or []:
                        aid = "ASSUMPTION:%s" % (a,)
                        if aid not in N:
                            F.add(("MISSING_PARENT", nid + "|assumption:" + str(a)))
                        elif aid not in ctx.succ("INTRODUCES", nid):
                            F.add(("DESCENDANT_RECORD_MISMATCH", nid))
                    ng = rd.get("new_gaps")
                    if not isinstance(ng, list) or sorted(ng) != sorted(ctx.succ("DESCENDANT", nid)):
                        F.add(("DESCENDANT_RECORD_MISMATCH", nid))
    rep = cycle_report(ctx)
    for k in rep:
        for c in rep[k]["cycles"]:
            F.add(("CYCLE", "%s:%s" % (k, "|".join(c))))
        for v in rep[k]["self_loops"]:
            F.add(("SELF_LOOP", "%s:%s" % (k, v)))
    return [list(x) for x in sorted(F)]


# ------------------------------------------------------------ AD loop
def validate_loops(doc, template=None, ogs=None):
    """FREEZE 4.9. Sorted list of [code, subject]; empty means valid."""
    T = template or load_template()
    OGS = ogs or load_open_gap_schema()
    F = set()
    if not isinstance(doc, dict) or not isinstance(doc.get("loops"), list) or not doc["loops"]:
        return [["L_SCHEMA", "document"]]
    step_ids = [s["id"] for s in T["steps"]]
    gap_keys = [f["key"] for f in OGS["open_gap_fields"]]
    seen = set()
    for li, loop in enumerate(doc["loops"]):
        if not isinstance(loop, dict) or any(f not in loop for f in T["loop_fields"]) \
                or not isinstance(loop.get("iterations"), list) or not loop["iterations"]:
            F.add(("L_SCHEMA", "loop[%d]" % li))
            continue
        lid = str(loop["loop_id"])
        prev_after, stopped = None, False
        for ii, it in enumerate(loop["iterations"]):
            subj = "%s#%d" % (lid, ii + 1)
            if not isinstance(it, dict) or any(f not in it for f in T["iteration_fields"]):
                F.add(("L_SCHEMA", subj))
                continue
            if it.get("iteration") != ii + 1 or stopped:
                F.add(("L_ITERATION_CONTINUITY", subj))
            steps = it["steps"] if isinstance(it["steps"], list) else []
            got = [s.get("step") if isinstance(s, dict) else None for s in steps]
            if got != step_ids:
                F.add(("L_STEP_MISSING_OR_ORDER", subj))
            for s in steps:
                if not isinstance(s, dict):
                    continue
                stt = s.get("status")
                ok = (stt == "DONE" and nonempty_str(s.get("evidence"))) or \
                     (stt in ("NOT_RUN", "NOT_APPLICABLE") and nonempty_str(s.get("reason")))
                if not ok:
                    F.add(("L_STEP_STATUS", "%s:%s" % (subj, s.get("step"))))
            s12 = [s for s in steps if isinstance(s, dict) and s.get("step") == "S12_NEW_GAP_EXTRACTION"]
            gaps = it["extracted_gaps"]
            if not s12 or s12[0].get("status") != "DONE" or not isinstance(gaps, list) or not gaps:
                F.add(("L_NO_GAP_EXTRACTION", subj))
            ids_here = set()
            max_index = None
            for gi, g in enumerate(gaps if isinstance(gaps, list) else []):
                gsub = "%s:gap[%d]" % (subj, gi)
                if not isinstance(g, dict):
                    F.add(("L_GAP_RECORD_INVALID", gsub))
                    continue
                strs = ["id"] + gap_keys
                if any(not nonempty_str(g.get(k)) for k in strs) or "materiality_inputs" not in g \
                        or g.get("source_rule") not in T["source_rules"]:
                    F.add(("L_GAP_RECORD_INVALID", gsub))
                try:
                    idx, _grade = materiality_of(g.get("materiality_inputs"), OGS)
                    if g.get("severity") != g["materiality_inputs"].get("severity"):
                        raise ValueError("severity field disagrees with materiality inputs")
                    max_index = idx if max_index is None else max(max_index, idx)
                except (ValueError, AttributeError, TypeError):
                    F.add(("L_MATERIALITY_INPUTS", gsub))
                    max_index = 99
                gid = g.get("id")
                if gid in seen:
                    F.add(("L_DUPLICATE_GAP_ID", str(gid)))
                seen.add(gid)
                ids_here.add(gid)
            before, after = it["assumptions_before"], it["assumptions_after"]
            if not (isinstance(before, list) and isinstance(after, list)
                    and all(nonempty_str(x) for x in before + after)):
                F.add(("L_SCHEMA", subj))
            else:
                if prev_after is not None and before != prev_after:
                    F.add(("L_ITERATION_CONTINUITY", subj))
                added, removed = set(after) - set(before), set(before) - set(after)
                ch = it["assumption_changes"]
                dec_add, dec_rem, bad = set(), set(), not isinstance(ch, list)
                for c in ch if isinstance(ch, list) else []:
                    if not isinstance(c, dict) or not nonempty_str(c.get("assumption")) \
                            or c.get("change") not in T["assumption_change_kinds"] \
                            or c.get("gap_ref") not in ids_here:
                        bad = True
                        continue
                    (dec_add if c["change"] == "ADDED" else dec_rem).add(c["assumption"])
                if bad or dec_add != added or dec_rem != removed:
                    F.add(("L_SILENT_ASSUMPTION_EDIT", subj))
                prev_after = after
            dec, sr = it["decision"], it["stop_reason"]
            if dec not in T["decisions"]:
                F.add(("L_STOP_REASON", subj))
            elif dec == "STOP":
                stopped = True
                if sr not in T["stop_reasons"]:
                    F.add(("L_STOP_REASON", subj))
                elif sr == "NO_MATERIAL_GAP_AT_THRESHOLD" and \
                        (max_index is None or max_index >= T["material_threshold_index"]):
                    F.add(("L_STOP_UNJUSTIFIED", subj))
            elif sr is not None:
                F.add(("L_STOP_REASON", subj))
    return [list(x) for x in sorted(F)]


# ---------------------------------------------------------------- summary
def summarize(graph, inputs=None, schema=None, ogs=None):
    I = inputs if inputs is not None else load_inputs()
    S = schema or I["schema"]
    OGS = ogs or I["ogs"]
    ctx = Context(graph, S, OGS)
    N = ctx.N
    gaps = [n for n in graph["nodes"] if n["kind"] == "GAP"]
    corpus = [n for n in gaps if n["origin"] == "CORPUS"]
    extracted = [n for n in gaps if n["origin"] == "AD_LOOP"]
    rule_edges = {}
    for e in graph["edges"]:
        if e[0] == "DESCENDANT":
            rule_edges.setdefault(e[3], []).append(e)
    corpus_rule_src = set(e[1] for r in ("R1_ID_PRECEDENCE", "R2_DEPENDENCY_PROPAGATION")
                          for e in rule_edges.get(r, []))
    any_src = set(e[1] for r in rule_edges for e in rule_edges[r])
    closed = [n for n in corpus if n["closure_state"] == "LOCALLY_CLOSED"]
    by_rule = {}
    for n in closed:
        by_rule[n["closure_rule"]] = by_rule.get(n["closure_rule"], 0) + 1
    blocked = sorted(n["id"] for n in closed if ctx.blocking_descendants(n["id"]))

    def corpus_blocking(nid):
        seen, stack = set(), [nid]
        adj = {}
        for e in rule_edges.get("R1_ID_PRECEDENCE", []) + rule_edges.get("R2_DEPENDENCY_PROPAGATION", []):
            adj.setdefault(e[1], set()).add(e[2])
        while stack:
            u = stack.pop()
            for v in adj.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        return [x for x in seen if ctx.unresolved_critical(x)]

    blocked_corpus_only = sorted(n["id"] for n in closed if corpus_blocking(n["id"]))
    distinct_ids = set(n["key"] for n in corpus)
    shared = dict((k, sum(1 for n in corpus if n["key"] == k)) for k in distinct_ids)
    shared = dict((k, v) for k, v in shared.items() if v > 1)
    parents = sorted(n["key"] for n in graph["nodes"] if n["kind"] == "PARENT")
    gates = dict((p, parent_closure_gate(graph, p, S, OGS, ctx)) for p in parents)
    results = [n for n in graph["nodes"] if n["kind"] == "RESULT"]
    flagship = [n for n in results if n["record"].get("is_flagship") is True]
    hostile_eval = dict((n["key"], evaluate_promotion(graph, n["id"], "HOSTILE_CLOSED", S, OGS, None, ctx))
                        for n in flagship)
    own = [n for n in results if n["record"].get("is_flagship") is not True]
    claims = [n for n in graph["nodes"] if n["kind"] == "CLAIM"]
    gap_claim_ids = set(n["claim_id"] for n in corpus)
    v1 = I["v1"]["gaps"]
    kinds = {}
    for n in graph["nodes"]:
        kinds[n["kind"]] = kinds.get(n["kind"], 0) + 1
    ekinds = {}
    for e in graph["edges"]:
        ekinds[e[0]] = ekinds.get(e[0], 0) + 1
    unres_crit_corpus = sorted(n["id"] for n in corpus if ctx.unresolved_critical(n["id"]))
    unres_crit_ex = sorted(n["id"] for n in extracted if ctx.unresolved_critical(n["id"]))
    findings = validate(graph, S, OGS)
    return {
        "nodes_by_kind": kinds,
        "edges_by_kind": ekinds,
        "descendant_edges_by_rule": dict((r, len(v)) for r, v in sorted(rule_edges.items())),
        "gap_records": {
            "corpus": len(corpus), "extracted_ad_loop": len(extracted),
            "corpus_distinct_ids": len(distinct_ids),
            "ids_shared_by_several_records": len(shared),
            "records_under_shared_ids": sum(shared.values()),
        },
        "descendants": {
            "v1_records_with_nonempty_descendants": sum(1 for g in v1 if g.get("descendants")),
            "v2_records_with_nonempty_object_descendants":
                sum(1 for g in I["g2"]["gaps"] if g.get("descendants")),
            "corpus_records_gaining_gap_descendants_by_R1_R2": sum(1 for n in corpus if n["id"] in corpus_rule_src),
            "corpus_records_gaining_gap_descendants_any_rule": sum(1 for n in corpus if n["id"] in any_src),
            "corpus_records_with_nonempty_transitive_descendants":
                sum(1 for n in corpus if n["descendant_gaps"]),
            "corpus_records_with_gap_or_object_descendants":
                sum(1 for n in corpus if n["id"] in any_src
                    or I["g2"]["gaps"][record_index(n)].get("descendants")),
            "unmapped_descendant_register_keys": graph["build_notes"]["unmapped_descendant_register_keys"],
        },
        "closure": {
            "locally_closed": len(closed),
            "locally_closed_by_rule": dict(sorted(by_rule.items())),
            "closed_with_nonempty_new_assumptions": sum(
                1 for n in closed if n.get("repair_delta", {}).get("new_assumptions")),
            "closed_with_nonempty_new_gaps": sum(1 for n in closed if n.get("repair_delta", {}).get("new_gaps")),
            "adjudicated_duplicate_not_closed": sum(
                1 for n in corpus if n.get("adjudication", {}).get("verdict") == "DUPLICATE"
                and n["closure_state"] == "OPEN"),
            "higher_grades_awarded": sum(1 for n in graph["nodes"]
                                         if n.get("closure_state") in GRADES[1:]),
        },
        "materiality": {
            "unresolved_critical_corpus": len(unres_crit_corpus),
            "unresolved_critical_extracted": len(unres_crit_ex),
            "closed_blocked_beyond_local": len(blocked),
            "closed_blocked_by_corpus_rules_only": len(blocked_corpus_only),
            "closed_not_blocked": len(closed) - len(blocked),
        },
        "parent_closure": dict((p, {"closure_permitted": gates[p]["closure_permitted"],
                                    "unresolved_critical": len(gates[p]["unresolved_critical"])})
                               for p in parents),
        "flagship": {
            "results": len(flagship),
            "hostile_closed_refused": sum(1 for v in hostile_eval.values() if not v["granted"]),
            "refusal_reasons": sorted(set(r for v in hostile_eval.values() for r in v["reasons"])),
            "refused_for_missing_methods": sum(
                1 for v in hostile_eval.values() if "FLAGSHIP_METHODS_MISSING" in v["reasons"]),
            "slots_filled_total": sum(
                1 for n in flagship for s in n["record"]["counterexample_methods"]
                if isinstance(s, dict) and slot_is_filled(s, S)),
            "evidence_level_unregistered": sum(
                1 for n in flagship if n["record"]["evidence"]["evidence_level"] == "UNREGISTERED"),
            "freeze_pointer_registered": sum(
                1 for n in flagship if n["record"]["prior_disclosure"]["freeze_pointer"] != "UNREGISTERED"),
            "unregistered_fields": dict(
                (f, sum(1 for n in flagship if n["record"][f] == "UNREGISTERED"))
                for f in S["result_record_list_fields"]),
        },
        "own_results": {
            "records": len(own),
            "with_two_distinct_filled_methods": sum(
                1 for n in own if len(set(s["method_class"] for s in n["record"]["counterexample_methods"]
                                          if isinstance(s, dict) and slot_is_filled(s, S))) >= 2),
        },
        "claims": {
            "claim_nodes": len(claims),
            "gap_claim_ids": len(gap_claim_ids),
            "claims_with_unresolved_descendants": sum(1 for n in claims if n["unresolved_descendant_gaps"]),
            "claims_without_unresolved_descendants": sum(1 for n in claims if not n["unresolved_descendant_gaps"]),
        },
        "cycles": cycle_report(ctx),
        "validation_findings": findings,
        "loop_findings": validate_loops(I["loops"], I["template"], OGS),
        "record_findings": dict((r.get("result_id"), validate_result_record(r, S))
                                for r in I["results"].get("records", [])
                                if validate_result_record(r, S)),
    }


def record_index(node):
    """Index into GAP_GRAPH_V2 gaps of a corpus gap node, from its pointer."""
    return int(node["pointer"].rsplit("[", 1)[1].rstrip("]"))


def run(write=False):
    I = load_inputs()
    graph = build(I)
    text = dumps_graph(graph)
    if write:
        with open(rp(GRAPH_REL), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    summ = summarize(graph, I)
    return {
        "schema": "GMI_833_AA1_GAP_GRAPH_ROUTE_A_V1",
        "route": "A",
        "graph_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "pins": pin_report(),
        "summary": summ,
    }


def main(argv):
    if "--check" in argv:
        text = dumps_graph(build())
        with open(rp(GRAPH_REL), "r", encoding="utf-8") as fh:
            same = fh.read() == text
        print("graph byte-identical to committed file: %s" % same)
        return 0 if same else 1
    if "--validate" in argv:
        i = argv.index("--validate")
        path = argv[i + 1] if len(argv) > i + 1 else rp(GRAPH_REL)
        with open(path, "r", encoding="utf-8") as fh:
            g = json.load(fh)
        f = validate(g)
        print(json.dumps({"findings": f, "count": len(f)}, indent=1, sort_keys=True))
        return 1 if f else 0
    if "--parent-closure-gate" in argv:
        key = argv[argv.index("--parent-closure-gate") + 1]
        with open(rp(GRAPH_REL), "r", encoding="utf-8") as fh:
            g = json.load(fh)
        r = parent_closure_gate(g, key)
        print(json.dumps({"parent": r["parent"], "closure_permitted": r["closure_permitted"],
                          "reason": r["reason"], "unresolved_critical_count": len(r["unresolved_critical"]),
                          "first_unresolved_critical": r["unresolved_critical"][:10]}, indent=1))
        return 0 if r["closure_permitted"] else 1
    if "--promote" in argv:
        i = argv.index("--promote")
        with open(rp(GRAPH_REL), "r", encoding="utf-8") as fh:
            g = json.load(fh)
        r = evaluate_promotion(g, argv[i + 1], argv[i + 2])
        print(json.dumps(r, indent=1, sort_keys=True))
        return 0 if r["granted"] else 1
    if "--validate-loop" in argv:
        with open(argv[argv.index("--validate-loop") + 1], "r", encoding="utf-8") as fh:
            f = validate_loops(json.load(fh))
        print(json.dumps({"findings": f, "count": len(f)}, indent=1))
        return 1 if f else 0
    if "--validate-records" in argv:
        with open(argv[argv.index("--validate-records") + 1], "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        S = load_schema()
        bad = dict((r.get("result_id") if isinstance(r, dict) else str(i), validate_result_record(r, S))
                   for i, r in enumerate(doc.get("records", [])))
        bad = dict((k, v) for k, v in bad.items() if v)
        print(json.dumps({"invalid": bad, "count": len(bad)}, indent=1, sort_keys=True))
        return 1 if bad else 0
    res = run(write=True)
    print(json.dumps(res, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
