#!/usr/bin/env python3
"""Route B for gmi-833-aa1-gap-graph-v1 - an independent validator and oracle.

Imports NOTHING from `gap_graph_v1.py` (route A) and nothing from
`gmi-833-aa-gap-object-v1`. Every rule is re-implemented from FREEZE_V1.md
section 4 and the two JSON schemas, by different means:

  * R2 descendants by fixed-point iteration over REGISTER_DELTA_V1
    claim_dependencies (route A reads the GAP_GRAPH_V2 `descendants` field);
  * strongly connected components by Kosaraju's two passes (route A: Tarjan);
  * reachability by breadth-first queues (route A: depth-first stacks);
  * materiality by a precomputed lookup table over the whole input cube
    (route A: the gap-object sum-and-bucket function);
  * the closure lattice by bitmasks (route A: the gap-object requires lists);
  * the bare-`closed` test by a character scan without regular expressions.

It re-derives the edge sets, closure set, repair records, claim cones, blocked
set and gate verdicts from the raw inputs, compares them with the committed
`GMI_GAP_GRAPH_V3.json`, and validates that file with its own validator.

Exit 0 only if every comparison agrees and the committed graph has no finding.
stdlib only; exact integers only.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))

P_G2 = "research/gmi-833-census-registration-pass-v1/GAP_GRAPH_V2.json"
P_RD = "research/gmi-833-census-registration-pass-v1/REGISTER_DELTA_V1.json"
P_CI = "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json"
P_DA = "research/gmi-833-depgraph-adjudication-v1/DUPLICATE_ADJUDICATION_V1.json"
P_OGS = "research/gmi-833-aa-gap-object-v1/OPEN_GAP_SCHEMA_V1.json"
P_FL = "research/gmi-833-aj0-foundation-scope-v1/FOUNDATION_LAYER_REGISTRY.json"
P_SCHEMA = "research/gmi-833-aa1-gap-graph-v1/GAP_GRAPH_SCHEMA_V1.json"
P_TEMPLATE = "research/gmi-833-aa1-gap-graph-v1/AD_LOOP_TEMPLATE_V1.json"
P_LOOPS = "research/gmi-833-aa1-gap-graph-v1/AD_LOOP_RECORDS_V1.json"
P_RESULTS = "research/gmi-833-aa1-gap-graph-v1/RESULT_RECORDS_V1.json"
P_GRAPH = "research/gmi-833-aa1-gap-graph-v1/GMI_GAP_GRAPH_V3.json"


def jload(rel):
    with open(os.path.join(REPO, *rel.split("/")), "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


SCHEMA = jload(P_SCHEMA)
TEMPLATE = jload(P_TEMPLATE)
OGS = jload(P_OGS)
STATES = list(SCHEMA["closure_states"])
GRADES = [s for s in STATES if s != "OPEN"]
FLAGS = list(SCHEMA["closure_evidence_flags"])
FLAG_BIT = dict((f, 1 << i) for i, f in enumerate(FLAGS))
REQ_MASK = {}
for _g in OGS["closure_grades"]:
    _m = 0
    for _k in _g["requires"]:
        _m |= FLAG_BIT[_k]
    REQ_MASK[_g["grade"]] = _m
CRIT = SCHEMA["blocking_materiality"]


def _table():
    """(severity, evidence, scope, capped blast) -> (index, grade), exhaustively."""
    cap = OGS["blast_rank_cap"]
    bands = []
    for g in OGS["materiality_grades"]:
        bands.append((g["lo"], g["hi"], g["grade"]))
    t = {}
    for s, sr in OGS["severity_rank"].items():
        for e, er in OGS["evidence_mode_rank"].items():
            for k, kr in OGS["scope_rank"].items():
                for b in range(cap + 1):
                    idx = sr + (3 - er) + kr + b
                    name = None
                    for lo, hi, gname in bands:
                        if lo <= idx <= hi:
                            name = gname
                    t[(s, e, k, b)] = (idx, name)
    return t


TABLE = _table()


def mat(inputs):
    """(index, grade) or None when any input is undeclared."""
    if type(inputs) is not dict:
        return None
    b = inputs.get("blast")
    if type(b) is not int or b < 0:
        return None
    key = (inputs.get("severity"), inputs.get("evidence_mode"), inputs.get("scope"),
           b if b < OGS["blast_rank_cap"] else OGS["blast_rank_cap"])
    try:
        return TABLE.get(key)
    except TypeError:
        return None


ASCII_WORD = frozenset("abcdefghijklmnopqrstuvwxyz0123456789_")


def is_bare_closed(text):
    """True if `closed` occurs as a word not immediately preceded by a word
    character (letters, digits, underscore) - the declared bare token."""
    if not isinstance(text, str):
        return False
    low = text.lower()
    n = len("closed")
    i = low.find("closed")
    while i >= 0:
        before = low[i - 1] if i > 0 else ""
        after = low[i + n] if i + n < len(low) else ""
        before_word = before != "" and before in ASCII_WORD
        after_word = after != "" and (after.isalnum() or after == "_")
        if not before_word and not after_word:
            return True
        i = low.find("closed", i + 1)
    return False


def filled_str(x):
    return isinstance(x, str) and len(x.strip()) > 0


# ---------------------------------------------------------------- index
class Index(object):
    def __init__(self, graph):
        self.nodes = {}
        for n in (graph.get("nodes") or []) if isinstance(graph, dict) else []:
            if isinstance(n, dict) and n.get("id") not in self.nodes:
                self.nodes[n.get("id")] = n
        self.fwd = collections.defaultdict(lambda: collections.defaultdict(set))
        self.rev = collections.defaultdict(lambda: collections.defaultdict(set))
        kinds = SCHEMA["edge_kinds"]
        for e in (graph.get("edges") or []) if isinstance(graph, dict) else []:
            if not isinstance(e, list) or len(e) < 3:
                continue
            k, s, d = e[0], e[1], e[2]
            if k not in kinds:
                continue
            if s not in self.nodes or d not in self.nodes:
                continue
            if self.nodes[s].get("kind") in kinds[k]["source"] and \
                    self.nodes[d].get("kind") in kinds[k]["target"]:
                self.fwd[k][s].add(d)
                self.rev[k][d].add(s)
        self.memo = {}

    def reach(self, start):
        if start in self.memo:
            return self.memo[start]
        seen = set()
        q = collections.deque(self.fwd["DESCENDANT"].get(start, ()))
        while q:
            x = q.popleft()
            if x in seen:
                continue
            seen.add(x)
            q.extend(self.fwd["DESCENDANT"].get(x, ()))
        self.memo[start] = seen
        return seen

    def open_gap(self, x):
        n = self.nodes.get(x)
        return n is not None and n.get("kind") == "GAP" and n.get("closure_state") not in GRADES

    def open_critical(self, x):
        return self.open_gap(x) and self.nodes[x].get("materiality") == CRIT

    def parent_cone(self, p):
        cone = set()
        for g in self.fwd["PARENT_OF"].get(p, ()):
            cone.add(g)
            cone.update(self.reach(g))
        return cone

    def claim_open(self, key):
        start = "CLAIM:%s" % (key,)
        down = set([start])
        q = collections.deque([start])
        while q:
            x = q.popleft()
            for child in self.rev["DEPENDS_ON"].get(x, ()):
                if child not in down:
                    down.add(child)
                    q.append(child)
        found = set()
        for c in down:
            for g in self.rev["GAP_ON"].get(c, ()):
                found.add(g)
                found.update(self.reach(g))
        return set(g for g in found if self.open_gap(g))


def kosaraju(adj):
    verts = set(adj)
    for v in list(adj):
        verts.update(adj[v])
    order, seen = [], set()
    for root in sorted(verts):
        if root in seen:
            continue
        seen.add(root)
        stack = [(root, sorted(adj.get(root, ())), 0)]
        while stack:
            v, nbrs, i = stack.pop()
            if i < len(nbrs):
                stack.append((v, nbrs, i + 1))
                w = nbrs[i]
                if w not in seen:
                    seen.add(w)
                    stack.append((w, sorted(adj.get(w, ())), 0))
            else:
                order.append(v)
    radj = collections.defaultdict(set)
    for v in adj:
        for w in adj[v]:
            radj[w].add(v)
    comps, assigned = [], set()
    for root in reversed(order):
        if root in assigned:
            continue
        comp, q = [], [root]
        assigned.add(root)
        while q:
            x = q.pop()
            comp.append(x)
            for y in radj.get(x, ()):
                if y not in assigned:
                    assigned.add(y)
                    q.append(y)
        comps.append(sorted(comp))
    return comps


# ---------------------------------------------------------------- records
def slot_filled(s):
    return (s.get("method_class") in SCHEMA["counterexample_method_classes"]
            and filled_str(s.get("evidence_pointer")) and filled_str(s.get("search_scope"))
            and s.get("outcome") in SCHEMA["slot_outcomes"])


def slot_blank(s):
    for k in ("method_class", "evidence_pointer", "search_scope", "outcome"):
        if s.get(k) is not None:
            return False
    return True


def methods_ok(rec):
    if not isinstance(rec, dict):
        return False
    fl = rec.get("is_flagship")
    if fl is False:
        return True
    slots = rec.get("counterexample_methods")
    if not isinstance(slots, list):
        return False
    classes, found_counterexample = set(), False
    for s in slots:
        if not isinstance(s, dict):
            return False
        if slot_filled(s):
            classes.add(s["method_class"])
            if s["outcome"] == "COUNTEREXAMPLE_FOUND":
                found_counterexample = True
    return (not found_counterexample) and len(classes) >= SCHEMA["min_distinct_methods_for_hostile_closed"]


def record_ok(rec):
    if not isinstance(rec, dict):
        return False
    for f in SCHEMA["result_record_fields"]:
        if f not in rec:
            return False
    if not filled_str(rec["result_id"]) or not filled_str(rec["statement"]):
        return False
    if rec["scope"] not in SCHEMA["scopes"] or type(rec["is_flagship"]) is not bool:
        return False
    if rec["scope"] == "FLAGSHIP" and rec["is_flagship"] is not True:
        return False
    for f in SCHEMA["result_record_list_fields"]:
        v = rec[f]
        if v == SCHEMA["unregistered_sentinel"]:
            continue
        if not isinstance(v, list) or len(v) == 0:
            return False
        for x in v:
            if not filled_str(x):
                return False
    slots = rec["counterexample_methods"]
    if not isinstance(slots, list):
        return False
    if rec["is_flagship"] is True and len(slots) < SCHEMA["min_flagship_slots"]:
        return False
    for pos, s in enumerate(slots, 1):
        if not isinstance(s, dict):
            return False
        for k in SCHEMA["slot_fields"]:
            if k not in s:
                return False
        if s["slot"] != pos:
            return False
        if not slot_blank(s) and not slot_filled(s):
            return False
    pd = rec["prior_disclosure"]
    if not isinstance(pd, dict) or not filled_str(pd.get("freeze_pointer")) \
            or pd.get("outcome_timing") not in SCHEMA["outcome_timing"]:
        return False
    ev = rec["evidence"]
    if not isinstance(ev, dict) or not filled_str(ev.get("evidence_level")) \
            or not filled_str(ev.get("maturity_level")):
        return False
    if rec["closure_state"] not in STATES:
        return False
    ce = rec["closure_evidence"]
    if not isinstance(ce, dict) or set(ce) != set(FLAGS):
        return False
    for k in FLAGS:
        if type(ce[k]) is not bool:
            return False
    return isinstance(rec["provenance"], dict)


# ---------------------------------------------------------------- promotion
def promote(graph, nid, grade, forbidden=None, ix=None):
    forbidden = set(SCHEMA["forbidden_grades_on_real_graph"]) if forbidden is None else set(forbidden)
    ix = ix or Index(graph)
    if grade not in GRADES:
        return {"granted": False, "reasons": ["BARE_CLOSED" if is_bare_closed(grade) else "UNKNOWN_CLOSURE_STATE"]}
    n = ix.nodes.get(nid)
    if n is None:
        return {"granted": False, "reasons": ["MISSING_PARENT"]}
    why = set()
    ce = n.get("closure_evidence")
    mask = 0
    if isinstance(ce, dict):
        for f in FLAGS:
            if ce.get(f) is True:
                mask |= FLAG_BIT[f]
    if mask & REQ_MASK[grade] != REQ_MASK[grade]:
        why.add("LATTICE_EVIDENCE_MISSING")
    if grade in forbidden:
        why.add("FORBIDDEN_GRADE_AWARDED")
    rank = GRADES.index(grade)
    k = n.get("kind")
    if k == "GAP":
        rd = n.get("repair_delta")
        good = isinstance(rd, dict)
        if good:
            for f in OGS["repair_delta_fields"]:
                if f["key"] not in rd:
                    good = False
        good = good and rd.get("closed_gap_id") == nid and filled_str(rd.get("repair_description")) \
            and isinstance(rd.get("new_assumptions"), list) and isinstance(rd.get("new_gaps"), list) \
            and rd.get("interrogation_answered") is True and rd.get("closure_grade_awarded") == grade
        if not good:
            why.add("CLOSED_WITHOUT_REPAIR_DELTA")
        if not (isinstance(rd, dict) and isinstance(rd.get("new_assumptions"), list) and rd["new_assumptions"]):
            why.add("CLOSED_WITHOUT_NEW_ASSUMPTIONS")
        if rank >= 1:
            for x in ix.reach(nid):
                if ix.open_critical(x):
                    why.add("CRITICAL_DESCENDANT_BLOCKS_PROMOTION")
                    break
    elif k == "RESULT":
        if rank >= 1 and not methods_ok(n.get("record")):
            why.add("FLAGSHIP_METHODS_MISSING")
    elif k == "PARENT":
        for x in ix.parent_cone(nid):
            if ix.open_critical(x):
                why.add("PARENT_CLOSED_WITH_CRITICAL_DESCENDANT")
                break
    else:
        why.add("UNKNOWN_KIND")
    return {"granted": len(why) == 0, "reasons": sorted(why)}


def parent_gate(graph, key, ix=None):
    ix = ix or Index(graph)
    p = "PARENT:" + key
    if p not in ix.nodes:
        return {"closure_permitted": False, "unresolved_critical": []}
    bad = sorted(x for x in ix.parent_cone(p) if ix.open_critical(x))
    return {"closure_permitted": len(bad) == 0, "unresolved_critical": bad}


# ---------------------------------------------------------------- validator
def validate(graph, forbidden=None):
    out = set()
    raw_nodes = (graph.get("nodes") or []) if isinstance(graph, dict) else []
    raw_edges = (graph.get("edges") or []) if isinstance(graph, dict) else []
    tally = collections.Counter((n.get("id") if isinstance(n, dict) else None) for n in raw_nodes)
    for k, c in tally.items():
        if c >= 2:
            out.add(("DUPLICATE_NODE_ID", str(k)))
    ix = Index(graph if isinstance(graph, dict) else {})
    kinds = SCHEMA["edge_kinds"]
    for nid, n in ix.nodes.items():
        if n.get("kind") not in SCHEMA["node_kinds"]:
            out.add(("UNKNOWN_KIND", str(nid)))
    for e in raw_edges:
        if not isinstance(e, list) or len(e) < 3:
            out.add(("UNKNOWN_KIND", "edge:MALFORMED"))
            continue
        tag = "edge:%s|%s|%s" % (e[0], e[1], e[2])
        if e[0] not in kinds:
            out.add(("UNKNOWN_KIND", tag))
        elif e[1] not in ix.nodes or e[2] not in ix.nodes:
            out.add(("MISSING_PARENT", tag))
        elif ix.nodes[e[1]].get("kind") not in kinds[e[0]]["source"] or \
                ix.nodes[e[2]].get("kind") not in kinds[e[0]]["target"]:
            out.add(("EDGE_ENDPOINT_KIND", tag))
    for nid, n in ix.nodes.items():
        k = n.get("kind")
        if k == "GAP":
            parent = "PARENT:%s" % (n.get("parent_result"),)
            if parent not in ix.nodes:
                out.add(("MISSING_PARENT", "%s|parent_result" % nid))
            if nid not in ix.fwd["PARENT_OF"].get(parent, set()):
                out.add(("ORPHAN_GAP", nid))
            if ("CLAIM:%s" % (n.get("claim_id"),)) not in ix.nodes:
                out.add(("MISSING_PARENT", "%s|claim_id" % nid))
            m = mat(n.get("materiality_inputs"))
            if m is None or m[0] != n.get("materiality_index") or m[1] != n.get("materiality"):
                out.add(("MATERIALITY_MISMATCH", nid))
            if "descendant_gaps" in n and n["descendant_gaps"] != sorted(ix.reach(nid)):
                out.add(("DESCENDANT_RECORD_MISMATCH", nid))
        elif k == "ASSUMPTION":
            if len(ix.rev["INTRODUCES"].get(nid, ())) == 0:
                out.add(("ORPHAN_ASSUMPTION", nid))
        elif k == "CLAIM":
            touched = False
            for ek in kinds:
                if ix.fwd[ek].get(nid) or ix.rev[ek].get(nid):
                    touched = True
            if not touched:
                out.add(("ORPHAN_CLAIM", nid))
            if "unresolved_descendant_gaps" in n and \
                    n["unresolved_descendant_gaps"] != sorted(ix.claim_open(n.get("key"))):
                out.add(("DESCENDANT_RECORD_MISMATCH", nid))
        elif k == "RESULT":
            rec = n.get("record")
            if not record_ok(rec) or rec.get("closure_state") != n.get("closure_state") \
                    or rec.get("result_id") != n.get("key"):
                out.add(("RESULT_RECORD_INVALID", nid))
        if k not in ("GAP", "RESULT", "PARENT"):
            continue
        st = n.get("closure_state")
        if st not in STATES:
            out.add(("BARE_CLOSED" if is_bare_closed(st) else "UNKNOWN_CLOSURE_STATE", nid))
            continue
        if st == "OPEN":
            continue
        for r in promote(graph, nid, st, forbidden, ix)["reasons"]:
            out.add((r, nid))
        if k == "GAP" and isinstance(n.get("repair_delta"), dict):
            rd = n["repair_delta"]
            for a in rd.get("new_assumptions") or []:
                an = "ASSUMPTION:%s" % (a,)
                if an not in ix.nodes:
                    out.add(("MISSING_PARENT", "%s|assumption:%s" % (nid, a)))
                elif an not in ix.fwd["INTRODUCES"].get(nid, set()):
                    out.add(("DESCENDANT_RECORD_MISMATCH", nid))
            ng = rd.get("new_gaps")
            if not isinstance(ng, list) or sorted(ng) != sorted(ix.fwd["DESCENDANT"].get(nid, set())):
                out.add(("DESCENDANT_RECORD_MISMATCH", nid))
    for ek in ("DESCENDANT", "DEPENDS_ON"):
        adj = dict((v, set(ws)) for v, ws in ix.fwd[ek].items())
        for v in sorted(adj):
            if v in adj[v]:
                out.add(("SELF_LOOP", "%s:%s" % (ek, v)))
        for comp in kosaraju(adj):
            if len(comp) >= 2:
                out.add(("CYCLE", "%s:%s" % (ek, "|".join(comp))))
    return sorted([list(x) for x in out])


# ---------------------------------------------------------------- AD loop
def validate_loops(doc):
    out = set()
    if not isinstance(doc, dict) or not isinstance(doc.get("loops"), list) or len(doc["loops"]) == 0:
        return [["L_SCHEMA", "document"]]
    order = [s["id"] for s in TEMPLATE["steps"]]
    need = ["id"] + [f["key"] for f in OGS["open_gap_fields"]]
    seen_ids = set()
    for li, loop in enumerate(doc["loops"]):
        ok = isinstance(loop, dict) and all(f in loop for f in TEMPLATE["loop_fields"]) \
            and isinstance(loop.get("iterations"), list) and len(loop["iterations"]) > 0
        if not ok:
            out.add(("L_SCHEMA", "loop[%d]" % li))
            continue
        name = str(loop["loop_id"])
        carried, halted = None, False
        for pos, it in enumerate(loop["iterations"], 1):
            tag = "%s#%d" % (name, pos)
            if not isinstance(it, dict) or not all(f in it for f in TEMPLATE["iteration_fields"]):
                out.add(("L_SCHEMA", tag))
                continue
            if halted or it.get("iteration") != pos:
                out.add(("L_ITERATION_CONTINUITY", tag))
            steps = it["steps"] if isinstance(it["steps"], list) else []
            names = []
            for s in steps:
                names.append(s.get("step") if isinstance(s, dict) else None)
            if names != order:
                out.add(("L_STEP_MISSING_OR_ORDER", tag))
            last = None
            for s in steps:
                if not isinstance(s, dict):
                    continue
                if s.get("step") == "S12_NEW_GAP_EXTRACTION" and last is None:
                    last = s
                status = s.get("status")
                if status == "DONE":
                    good = filled_str(s.get("evidence"))
                elif status in ("NOT_RUN", "NOT_APPLICABLE"):
                    good = filled_str(s.get("reason"))
                else:
                    good = False
                if not good:
                    out.add(("L_STEP_STATUS", "%s:%s" % (tag, s.get("step"))))
            ex = it["extracted_gaps"]
            if last is None or last.get("status") != "DONE" or not isinstance(ex, list) or len(ex) == 0:
                out.add(("L_NO_GAP_EXTRACTION", tag))
            local_ids, top = set(), None
            for gi, g in enumerate(ex if isinstance(ex, list) else []):
                gtag = "%s:gap[%d]" % (tag, gi)
                if not isinstance(g, dict):
                    out.add(("L_GAP_RECORD_INVALID", gtag))
                    continue
                bad = "materiality_inputs" not in g or g.get("source_rule") not in TEMPLATE["source_rules"]
                for f in need:
                    if not filled_str(g.get(f)):
                        bad = True
                if bad:
                    out.add(("L_GAP_RECORD_INVALID", gtag))
                mi = g.get("materiality_inputs")
                m = mat(mi)
                if m is None or not isinstance(mi, dict) or g.get("severity") != mi.get("severity"):
                    out.add(("L_MATERIALITY_INPUTS", gtag))
                    top = 99
                else:
                    top = m[0] if top is None else max(top, m[0])
                if g.get("id") in seen_ids:
                    out.add(("L_DUPLICATE_GAP_ID", str(g.get("id"))))
                seen_ids.add(g.get("id"))
                local_ids.add(g.get("id"))
            b, a = it["assumptions_before"], it["assumptions_after"]
            lists_ok = isinstance(b, list) and isinstance(a, list)
            if lists_ok:
                for x in b + a:
                    if not filled_str(x):
                        lists_ok = False
            if not lists_ok:
                out.add(("L_SCHEMA", tag))
            else:
                if carried is not None and b != carried:
                    out.add(("L_ITERATION_CONTINUITY", tag))
                plus, minus = set(a).difference(b), set(b).difference(a)
                ch = it["assumption_changes"]
                said_plus, said_minus, broken = set(), set(), not isinstance(ch, list)
                for c in (ch if isinstance(ch, list) else []):
                    if not isinstance(c, dict) or not filled_str(c.get("assumption")) \
                            or c.get("gap_ref") not in local_ids:
                        broken = True
                    elif c.get("change") == "ADDED":
                        said_plus.add(c["assumption"])
                    elif c.get("change") == "REMOVED":
                        said_minus.add(c["assumption"])
                    else:
                        broken = True
                if broken or said_plus != plus or said_minus != minus:
                    out.add(("L_SILENT_ASSUMPTION_EDIT", tag))
                carried = a
            d, why = it["decision"], it["stop_reason"]
            if d == "STOP":
                halted = True
                if why not in TEMPLATE["stop_reasons"]:
                    out.add(("L_STOP_REASON", tag))
                elif why == "NO_MATERIAL_GAP_AT_THRESHOLD":
                    if top is None or top >= TEMPLATE["material_threshold_index"]:
                        out.add(("L_STOP_UNJUSTIFIED", tag))
            elif d == "REPEAT":
                if why is not None:
                    out.add(("L_STOP_REASON", tag))
            else:
                out.add(("L_STOP_REASON", tag))
    return sorted([list(x) for x in out])


# ---------------------------------------------------------------- oracle
def derive():
    """Re-derive the edge sets, closure set, repair records and gate inputs
    from the raw inputs, without reading the GAP_GRAPH_V2 `descendants` field."""
    g2 = jload(P_G2)["gaps"]
    ci = jload(P_CI)["scientific_objects"]
    rd = jload(P_RD)["records"]
    da = jload(P_DA)["dupid_gaps"]["adjudications"]
    loops = jload(P_LOOPS)
    by_obj = collections.defaultdict(list)
    for o in ci:
        by_obj[o["object_id"]].append(o)
    verdict = {}
    for a in da:
        verdict[a["gap_id"]] = (a["verdict"], a["reason"])
    rules = SCHEMA["repair_rule_assumptions"]

    ids, seen = [], collections.Counter()
    for g in g2:
        seen[g["id"]] += 1
        ids.append("GAP:%s#%d" % (g["id"], seen[g["id"]]))

    def rule_of(decls):
        if len(decls) < 2:
            return None
        texts = [d.get("statement") for d in decls]
        first = texts[0]
        if all(t == first for t in texts):
            return "B1_VERBATIM_REDECLARATION"
        canon = [" ".join((t or "").split()).lower() for t in texts]
        if all(c == canon[0] for c in canon):
            return "B2_CANONICAL_REDECLARATION"
        for x in range(len(decls)):
            for y in range(len(decls)):
                if x != y and decls[y]["source_path"].rsplit("/", 1)[-1] in (decls[x].get("statement") or ""):
                    return "B3_POINTER_TO_SAME_CONTENT"
        return "B4_ID_COLLISION_CONTENT_DIFFERS"

    closed = {}
    for i, g in enumerate(g2):
        if not g["id"].startswith("GAP-DUPID-"):
            continue
        v = verdict.get(g["id"])
        if v and v[0] == "DUPLICATE" and v[1] in rules and rule_of(by_obj.get(g["claim_id"], [])) == v[1]:
            closed[ids[i]] = v[1]

    edges = set()
    groups = collections.defaultdict(list)
    for i, g in enumerate(g2):
        groups[g["claim_id"]].append(i)
    for c, members in groups.items():
        for x in members:
            for y in members:
                if g2[x]["id"].startswith("GAP-DUPID-") and g2[y]["id"].startswith("GAP-FIN2UNIV-"):
                    edges.add(("DESCENDANT", ids[x], ids[y], "R1_ID_PRECEDENCE"))
    children = collections.defaultdict(set)
    for r in rd:
        deps = r.get("claim_dependencies")
        if isinstance(deps, list):
            for p in deps:
                children[p].add(r["object_id"])
    for i, g in enumerate(g2):
        down = set(children.get(g["claim_id"], ()))
        while True:
            grown = set(down)
            for x in down:
                grown |= children.get(x, set())
            if grown == down:
                break
            down = grown
        for oid in down:
            for j in groups.get(oid, ()):
                if j != i:
                    edges.add(("DESCENDANT", ids[i], ids[j], "R2_DEPENDENCY_PROPAGATION"))

    def pkg(path):
        parts = path.split("/")
        return parts[1] if len(parts) > 1 and parts[0] == "research" else parts[0]

    sources = {"NONE": []}
    sources["B1_CROSS_PACKAGE"] = sorted(
        n for n, r in closed.items() if r == "B1_VERBATIM_REDECLARATION"
        and len(set(pkg(d["source_path"]) for d in by_obj.get(g2[ids.index(n)]["claim_id"], []))) > 1)
    sources["B3_ALL"] = sorted(n for n, r in closed.items() if r == "B3_POINTER_TO_SAME_CONTENT")
    extracted = []
    for loop in loops["loops"]:
        for it in loop["iterations"]:
            for e in it["extracted_gaps"]:
                seen[e["id"]] += 1
                nid = "GAP:%s#%d" % (e["id"], seen[e["id"]])
                extracted.append(nid)
                for s in sources[e["source_rule"]]:
                    edges.add(("DESCENDANT", s, nid, "R3_REPAIR_SUCCESSOR"))
    for r in rd:
        deps = r.get("claim_dependencies")
        if isinstance(deps, list):
            for p in deps:
                edges.add(("DEPENDS_ON", "CLAIM:" + r["object_id"], "CLAIM:" + p,
                           "REGISTER_DELTA_CLAIM_DEPENDENCIES"))
    new_gaps = {}
    for n in closed:
        new_gaps[n] = sorted(set(e[2] for e in edges if e[0] == "DESCENDANT" and e[1] == n))
    return {"closed": closed, "descendant_and_dependency_edges": edges, "new_gaps": new_gaps,
            "extracted": extracted, "sources": sources}


def run():
    graph = jload(P_GRAPH)
    d = derive()
    ix = Index(graph)
    nodes = ix.nodes
    disagreements = []
    committed = set(tuple(e) for e in graph["edges"] if e[0] in ("DESCENDANT", "DEPENDS_ON"))
    if committed != d["descendant_and_dependency_edges"]:
        disagreements.append("edge sets differ: %d only in graph, %d only in route B"
                             % (len(committed - d["descendant_and_dependency_edges"]),
                                len(d["descendant_and_dependency_edges"] - committed)))
    closed_graph = dict((k, v.get("closure_rule")) for k, v in nodes.items()
                        if v.get("kind") == "GAP" and v.get("closure_state") == "LOCALLY_CLOSED")
    if closed_graph != d["closed"]:
        disagreements.append("closure sets differ")
    for n, ng in d["new_gaps"].items():
        rdl = (nodes.get(n) or {}).get("repair_delta") or {}
        if rdl.get("new_gaps") != ng:
            disagreements.append("repair new_gaps differ at %s" % n)
            break
    blocked = sorted(n for n in d["closed"] if any(ix.open_critical(x) for x in ix.reach(n)))
    corpus_edges = collections.defaultdict(set)
    for e in d["descendant_and_dependency_edges"]:
        if e[0] == "DESCENDANT" and e[3] in ("R1_ID_PRECEDENCE", "R2_DEPENDENCY_PROPAGATION"):
            corpus_edges[e[1]].add(e[2])
    rule_counts = collections.Counter(e[3] for e in d["descendant_and_dependency_edges"])
    parents = sorted(v["key"] for v in nodes.values() if v.get("kind") == "PARENT")
    gates = dict((p, parent_gate(graph, p, ix)) for p in parents)
    flagship = sorted(k for k, v in nodes.items() if v.get("kind") == "RESULT"
                      and isinstance(v.get("record"), dict) and v["record"].get("is_flagship") is True)
    hostile = dict((k, promote(graph, k, "HOSTILE_CLOSED", None, ix)) for k in flagship)
    claims = [v for v in nodes.values() if v.get("kind") == "CLAIM"]
    claim_sets_agree = all(v.get("unresolved_descendant_gaps") == sorted(ix.claim_open(v["key"]))
                           for v in claims)
    if not claim_sets_agree:
        disagreements.append("claim unresolved-descendant sets differ")
    findings = validate(graph)
    loop_findings = validate_loops(jload(P_LOOPS))
    own = jload(P_RESULTS).get("records", [])
    corpus_nodes = [k for k, v in nodes.items() if v.get("kind") == "GAP" and v.get("origin") == "CORPUS"]
    return {
        "schema": "GMI_833_AA1_GAP_GRAPH_ROUTE_B_V1",
        "route": "B",
        "descendant_edges_by_rule": dict((r, rule_counts[r]) for r in sorted(rule_counts)
                                         if len(r) > 1 and r[0] == "R" and r[1] in "123456789"),
        "depends_on_edges": rule_counts["REGISTER_DELTA_CLAIM_DEPENDENCIES"],
        "corpus_records_gaining_gap_descendants_by_R1_R2": len(corpus_edges),
        "locally_closed": len(d["closed"]),
        "locally_closed_by_rule": dict(collections.Counter(d["closed"].values())),
        "closed_blocked_beyond_local": len(blocked),
        "unresolved_critical_corpus": sum(1 for k in corpus_nodes if ix.open_critical(k)),
        "parent_closure": dict((p, {"closure_permitted": gates[p]["closure_permitted"],
                                    "unresolved_critical": len(gates[p]["unresolved_critical"])})
                               for p in parents),
        "flagship_hostile_closed_refused": sum(1 for v in hostile.values() if not v["granted"]),
        "flagship_refused_for_missing_methods": sum(
            1 for v in hostile.values() if "FLAGSHIP_METHODS_MISSING" in v["reasons"]),
        "claims_with_unresolved_descendants": sum(1 for v in claims if v.get("unresolved_descendant_gaps")),
        "own_records_valid": sum(1 for r in own if record_ok(r)),
        "own_records": len(own),
        "validation_findings": findings,
        "loop_findings": loop_findings,
        "disagreements": disagreements,
    }


def main():
    res = run()
    print(json.dumps(res, indent=1, sort_keys=True))
    bad = res["disagreements"] or res["validation_findings"] or res["loop_findings"] \
        or res["own_records_valid"] != res["own_records"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
