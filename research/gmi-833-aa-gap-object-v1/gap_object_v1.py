#!/usr/bin/env python3
"""Route A executor for gmi-833-aa-gap-object-v1 (issue #833, rows AA01/AA07/AA09/AA39).

Exact, stdlib-only, no floats in any reported quantity. Impurity is an exact
Fraction; every count is an int.

Route A reads the frozen gap universe with json.load and validates it against
OPEN_GAP_SCHEMA_V1.json. Route B (independent_oracle_v1.py) re-derives every
reported quantity from the raw bytes with a hand-written scanner and imports
nothing from this file.
"""
import json
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
SCHEMA_PATH = os.path.join(HERE, "OPEN_GAP_SCHEMA_V1.json")
GAPS_PATH = os.path.join(REPO, "research", "gmi-833-corpus-census-v1", "GMI_GAP_GRAPH_V1.json")


def load_schema(path=SCHEMA_PATH):
    with open(path, "r") as fh:
        return json.load(fh)


def load_gaps(path=GAPS_PATH):
    with open(path, "r") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- AAG-1
def validate_open_gap(records, schema):
    """AAG-1: every record realizes all nine AA01-named fields, non-empty."""
    req = [f["key"] for f in schema["open_gap_fields"]]
    names = [f["aa01_name"] for f in schema["open_gap_fields"]]
    if len(set(req)) != len(req):
        raise ValueError("schema binding is not injective")
    if len(set(names)) != len(names):
        raise ValueError("AA01 names are not distinct")
    conform = 0
    missing_field = 0
    empty_cells = 0
    for r in records:
        ok = True
        for k in req:
            if k not in r:
                missing_field += 1
                ok = False
                continue
            v = r[k]
            if not isinstance(v, str) or v.strip() == "":
                empty_cells += 1
                ok = False
        if ok:
            conform += 1
    return {
        "records": len(records),
        "required_fields": len(req),
        "conforming": conform,
        "missing_field_events": missing_field,
        "empty_cell_events": empty_cells,
        "distinct_claim_id": len(set(r.get("claim_id") for r in records)),
        "verdict": "PASS" if (conform == len(records) and len(records) > 0) else "FAIL",
    }


# ---------------------------------------------------------------- AAG-2
def gini_impurity(values):
    """Exact rational impurity 1 - sum (n_i/n)^2. Zero iff the column is constant."""
    n = len(values)
    if n == 0:
        return Fraction(0, 1)
    counts = {}
    for v in values:
        key = json.dumps(v, sort_keys=True) if not isinstance(v, str) else v
        counts[key] = counts.get(key, 0) + 1
    tot = Fraction(0, 1)
    for c in counts.values():
        tot += Fraction(c * c, n * n)
    return Fraction(1, 1) - tot


def column_report(records, keys):
    out = {}
    for k in keys:
        vals = [r.get(k) for r in records]
        imp = gini_impurity(vals)
        out[k] = {
            "distinct": len(set(json.dumps(v, sort_keys=True) for v in vals)),
            "impurity_num": imp.numerator,
            "impurity_den": imp.denominator,
            "degenerate": imp == 0,
        }
    return out


# ---------------------------------------------------------------- AAG-3
def materiality_index(severity_rank, evidence_mode_rank, scope_rank, blast_count, cap=3):
    if blast_count < 0:
        raise ValueError("blast_count must be >= 0")
    return severity_rank + (3 - evidence_mode_rank) + scope_rank + min(blast_count, cap)


def materiality_grade(index, schema):
    for g in schema["materiality_grades"]:
        if g["lo"] <= index <= g["hi"]:
            return g["grade"]
    raise ValueError("index %r outside declared grade range" % (index,))


GRADE_ORDER = ["IMMATERIAL", "MINOR", "MATERIAL", "CRITICAL"]


def monotonicity_violations(schema, grade_fn=None, index_fn=None):
    """Exhaustive check over the finite 4x4x4x4 domain that the grade is
    non-decreasing in severity and scope and blast, and non-increasing in
    evidence_mode. Returns the exact violation count."""
    gfn = grade_fn or (lambda i: materiality_grade(i, schema))
    ifn = index_fn or materiality_index
    rank = dict((g, i) for i, g in enumerate(GRADE_ORDER))
    bad = 0
    checked = 0
    for s in range(4):
        for e in range(4):
            for k in range(4):
                for b in range(4):
                    base = rank[gfn(ifn(s, e, k, b))]
                    for ds, de, dk, db in ((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)):
                        s2, e2, k2, b2 = s + ds, e + de, k + dk, b + db
                        if not (0 <= s2 < 4 and 0 <= e2 < 4 and 0 <= k2 < 4 and 0 <= b2 < 4):
                            continue
                        checked += 1
                        if rank[gfn(ifn(s2, e2, k2, b2))] < base:
                            bad += 1
    return {"domain_points": 256, "comparisons": checked, "violations": bad}


GAP_KIND_SCOPE = {"DUPID": "PACKAGE", "FIN2UNIV": "FLAGSHIP"}


def grade_real_gaps(records, schema):
    """Apply the declared threshold to the frozen universe.

    severity  <- record 'severity' via schema severity_rank
    evidence  <- ASSERTED for status OPEN (no evidence has been produced yet)
    scope     <- gap kind from the id prefix (DUPID=PACKAGE, FIN2UNIV=FLAGSHIP)
    blast     <- (multiplicity of the record's claim_id) - 1
    """
    srank = schema["severity_rank"]
    erank = schema["evidence_mode_rank"]
    krank = schema["scope_rank"]
    mult = {}
    for r in records:
        mult[r.get("claim_id")] = mult.get(r.get("claim_id"), 0) + 1
    counts = dict((g, 0) for g in GRADE_ORDER)
    kinds = {}
    unknown = 0
    for r in records:
        parts = str(r.get("id", "")).split("-")
        kind = parts[1] if len(parts) > 1 else ""
        kinds[kind] = kinds.get(kind, 0) + 1
        scope = GAP_KIND_SCOPE.get(kind)
        if scope is None:
            unknown += 1
            scope = "LOCAL"
        ev = "ASSERTED" if r.get("status") == "OPEN" else "FINITE_EXACT"
        idx = materiality_index(
            srank[r["severity"]], erank[ev], krank[scope], mult[r.get("claim_id")] - 1
        )
        counts[materiality_grade(idx, schema)] += 1
    above = counts["MATERIAL"] + counts["CRITICAL"]
    return {
        "graded": len(records),
        "grade_counts": counts,
        "kind_counts": kinds,
        "unknown_kind": unknown,
        "at_or_above_threshold": above,
        "below_threshold": len(records) - above,
        "non_degenerate": len([g for g in counts if counts[g] > 0]) >= 2,
    }


# ---------------------------------------------------------------- AAG-4
CLOSURE_EVIDENCE = [
    "local_checks_pass",
    "independent_route",
    "hostiles_detected",
    "independent_replication",
    "real_scale_run",
]


def closure_grades(evidence, schema):
    out = []
    for g in schema["closure_grades"]:
        if all(evidence.get(k, False) for k in g["requires"]):
            out.append(g["grade"])
    return out


def closure_chain_violations(schema):
    """Exhaustive over all 2**5 evidence points: the satisfied-grade set must
    always be an initial segment of the declared 4-grade chain."""
    order = [g["grade"] for g in schema["closure_grades"]]
    bad = 0
    for mask in range(32):
        ev = dict((k, bool(mask & (1 << i))) for i, k in enumerate(CLOSURE_EVIDENCE))
        got = closure_grades(ev, schema)
        prefix = order[: len(got)]
        if got != prefix:
            bad += 1
    return {"evidence_points": 32, "violations": bad, "chain": order}


BARE_CLOSED = re.compile(r"(?<![A-Za-z0-9_])closed\b", re.IGNORECASE)
QUALIFIERS = ("LOCALLY_", "HOSTILE_", "REPLICATED_", "REAL_SCALE_")


def bare_closed_hits(text):
    """A 'closed' token is qualified iff immediately preceded by one of the four
    declared prefixes. Everything else in the line is a bare-closed hit."""
    hits = []
    for i, line in enumerate(text.split("\n")):
        for m in BARE_CLOSED.finditer(line):
            head = line[: m.start()]
            if any(head.endswith(q) for q in QUALIFIERS):
                continue
            hits.append((i + 1, line.strip()[:160]))
    return hits


AUTHORITY_PKGS = ("gmi-833-aa-gap-object-v1", "gmi-833-ab-terminology-harness-v1")


def scan_bare_closed(root, limit_exts=(".md",), exclude=AUTHORITY_PKGS):
    """Measure the corpus, not the instrument: this tranche's own packages
    define the four qualified grades and quote the bare token definitionally
    (one of them carries a byte-exact snapshot of the issue comment that states
    the rule), so they are excluded exactly like the parent terminology gate's
    _authority_doc self-skip. The exclusion set is reported in the result."""
    total = 0
    files = 0
    per_pkg = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git" and d not in exclude]
        for fn in sorted(filenames):
            if not fn.endswith(limit_exts):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, "r", errors="replace") as fh:
                    txt = fh.read()
            except OSError:
                continue
            h = bare_closed_hits(txt)
            files += 1
            if h:
                total += len(h)
                rel = os.path.relpath(p, root)
                pkg = rel.split(os.sep)[0]
                per_pkg[pkg] = per_pkg.get(pkg, 0) + len(h)
    return {"files_scanned": files, "hits": total, "packages_with_hits": len(per_pkg),
            "excluded_packages": sorted(exclude),
            "top": sorted(per_pkg.items(), key=lambda kv: (-kv[1], kv[0]))[:10]}


# ---------------------------------------------------------------- AAG-5
def emit_repair_delta(gap, repair_description, new_assumptions, new_gaps,
                      closure_grade_awarded, schema):
    """AA07: closing a gap MUST emit this successor-interrogation record."""
    if not isinstance(gap, dict) or not str(gap.get("id", "")).strip():
        raise ValueError("gap must carry a non-empty id")
    if not str(repair_description).strip():
        raise ValueError("repair_description must be non-empty")
    valid = [g["grade"] for g in schema["closure_grades"]]
    if closure_grade_awarded not in valid:
        raise ValueError("closure_grade_awarded must be one of %r" % (valid,))
    rec = {
        "closed_gap_id": gap["id"],
        "repair_description": repair_description,
        "new_assumptions": list(new_assumptions),
        "new_gaps": list(new_gaps),
        "interrogation_answered": True,
        "closure_grade_awarded": closure_grade_awarded,
    }
    for f in schema["repair_delta_fields"]:
        if f["key"] not in rec:
            raise ValueError("repair delta missing %s" % f["key"])
    return rec


def repair_delta_totality(records, schema):
    ok = 0
    for r in records:
        try:
            emit_repair_delta(r, "schema-conformance repair", [], [], "LOCALLY_CLOSED", schema)
            ok += 1
        except ValueError:
            pass
    return {"attempted": len(records), "emitted": ok,
            "verdict": "PASS" if ok == len(records) else "FAIL"}


# ---------------------------------------------------------------- driver
def run(gaps_path=GAPS_PATH, schema_path=SCHEMA_PATH, scan_root=None):
    schema = load_schema(schema_path)
    doc = load_gaps(gaps_path)
    records = doc["gaps"]
    aag1 = validate_open_gap(records, schema)
    cols = column_report(records, [f["key"] for f in schema["open_gap_fields"]] +
                         ["status", "materiality", "descendants"])
    degen = sorted([k for k in cols if cols[k]["degenerate"]])
    aag3_mono = monotonicity_violations(schema)
    aag3_real = grade_real_gaps(records, schema)
    aag4 = closure_chain_violations(schema)
    aag5 = repair_delta_totality(records, schema)
    nonempty_desc = len([r for r in records if r.get("descendants")])
    out = {
        "schema": "GMI_AA_GAP_OBJECT_RESULT_V1",
        "route": "A",
        "source_gap_graph": os.path.relpath(gaps_path, REPO),
        "AAG-1": aag1,
        "AAG-2": {"columns": cols, "degenerate_columns": degen,
                  "degenerate_count": len(degen)},
        "AAG-3": {"monotonicity": aag3_mono, "applied": aag3_real},
        "AAG-4": aag4,
        "AAG-5": aag5,
        "AA38_not_earned": {"records": len(records),
                            "records_with_nonempty_descendants": nonempty_desc},
    }
    if scan_root:
        out["bare_closed_scan"] = scan_bare_closed(scan_root)
    return out


def main(argv):
    scan_root = os.path.join(REPO, "research") if "--scan" in argv else None
    res = run(scan_root=scan_root)
    print(json.dumps(res, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
