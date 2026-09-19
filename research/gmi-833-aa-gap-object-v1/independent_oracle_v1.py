#!/usr/bin/env python3
"""Route B independent oracle for gmi-833-aa-gap-object-v1.

Materially independent of gap_object_v1.py:
  * imports nothing from it;
  * never calls json.load on the gap graph - it walks the raw bytes with a
    hand-written string/escape/depth state machine, so it also sees duplicate
    JSON keys that json.load silently collapses;
  * recomputes impurity as (n^2 - sum c^2)/n^2 reduced by math.gcd instead of
    summing Fractions;
  * recomputes the materiality grade from an explicitly enumerated 256-entry
    lookup table built by boundary comparison, not by the sum-and-bucket path;
  * recomputes the closure chain from re-typed requirement sets over a
    reversed bit ordering.
Only the normative schema JSON is shared - that is the specification, not an
implementation.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
SCHEMA_PATH = os.path.join(HERE, "OPEN_GAP_SCHEMA_V1.json")
GAPS_PATH = os.path.join(REPO, "research", "gmi-833-corpus-census-v1", "GMI_GAP_GRAPH_V1.json")


# ------------------------------------------------- hand-written JSON walker
def _read_string(s, i):
    """s[i] == '"'. Returns (value, next_index)."""
    if s[i] != '"':
        raise ValueError("expected string at %d" % i)
    i += 1
    buf = []
    while True:
        ch = s[i]
        if ch == "\\":
            nxt = s[i + 1]
            mapping = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                       "n": "\n", "r": "\r", "t": "\t"}
            if nxt == "u":
                buf.append(chr(int(s[i + 2:i + 6], 16)))
                i += 6
            else:
                buf.append(mapping.get(nxt, nxt))
                i += 2
            continue
        if ch == '"':
            return "".join(buf), i + 1
        buf.append(ch)
        i += 1


def walk_records(text, array_key="gaps"):
    """Yield (ordered_key_list, {key: raw_string_value_or_None}) per depth-1
    object inside the named array. Duplicate keys are preserved in the list."""
    marker = '"%s"' % array_key
    p = text.index(marker) + len(marker)
    while text[p] != "[":
        p += 1
    p += 1
    out = []
    n = len(text)
    while p < n:
        while p < n and text[p] in " \t\r\n,":
            p += 1
        if p >= n or text[p] == "]":
            break
        if text[p] != "{":
            raise ValueError("unexpected %r at %d" % (text[p], p))
        p += 1
        keys = []
        vals = {}
        depth = 0
        while True:
            while text[p] in " \t\r\n,":
                p += 1
            if text[p] == "}" and depth == 0:
                p += 1
                break
            key, p = _read_string(text, p)
            while text[p] in " \t\r\n":
                p += 1
            if text[p] != ":":
                raise ValueError("expected ':' at %d" % p)
            p += 1
            while text[p] in " \t\r\n":
                p += 1
            c = text[p]
            if c == '"':
                v, p = _read_string(text, p)
            elif c in "[{":
                open_c, close_c = c, ("]" if c == "[" else "}")
                d = 0
                start = p
                while True:
                    ch = text[p]
                    if ch == '"':
                        _, p = _read_string(text, p)
                        continue
                    if ch == open_c:
                        d += 1
                    elif ch == close_c:
                        d -= 1
                        if d == 0:
                            p += 1
                            break
                    p += 1
                v = text[start:p]
            else:
                start = p
                while text[p] not in ",}] \t\r\n":
                    p += 1
                v = text[start:p]
            keys.append(key)
            vals[key] = v
        out.append((keys, vals))
    return out


# ------------------------------------------------- independent recomputation
def impurity_pair(values):
    n = len(values)
    if n == 0:
        return (0, 1)
    tally = {}
    for v in values:
        tally[v] = tally.get(v, 0) + 1
    ssq = 0
    for c in tally.values():
        ssq += c * c
    num = n * n - ssq
    den = n * n
    g = math.gcd(num, den) or 1
    return (num // g, den // g)


def build_grade_table(schema):
    """256-entry lookup table built by explicit boundary comparison."""
    bounds = [(g["grade"], g["lo"], g["hi"]) for g in schema["materiality_grades"]]
    table = {}
    for s in range(4):
        for e in range(4):
            for k in range(4):
                for b in range(4):
                    idx = 0
                    idx += s
                    idx += 3
                    idx -= e
                    idx += k
                    idx += b if b < schema["blast_rank_cap"] else schema["blast_rank_cap"]
                    chosen = None
                    for name, lo, hi in bounds:
                        if idx >= lo and idx <= hi:
                            chosen = name
                            break
                    if chosen is None:
                        raise ValueError("no grade for index %d" % idx)
                    table[(s, e, k, b)] = chosen
    return table


def chain_check(schema):
    order = [g["grade"] for g in schema["closure_grades"]]
    reqs = dict((g["grade"], set(g["requires"])) for g in schema["closure_grades"])
    flags = ["real_scale_run", "independent_replication", "hostiles_detected",
             "independent_route", "local_checks_pass"]
    bad = 0
    for mask in range(32):
        have = set(flags[i] for i in range(5) if mask & (1 << i))
        sat = [g for g in order if reqs[g] <= have]
        if sat != order[:len(sat)]:
            bad += 1
    return {"evidence_points": 32, "violations": bad}


SCOPE_BY_KIND = {"DUPID": 1, "FIN2UNIV": 3}


def run(gaps_path=GAPS_PATH, schema_path=SCHEMA_PATH):
    with open(schema_path, "r") as fh:
        schema = json.load(fh)
    with open(gaps_path, "r") as fh:
        text = fh.read()
    recs = walk_records(text)
    req = [f["key"] for f in schema["open_gap_fields"]]
    dup_key_records = 0
    missing = 0
    empties = 0
    conforming = 0
    for keys, vals in recs:
        if len(keys) != len(set(keys)):
            dup_key_records += 1
        ok = True
        for k in req:
            if k not in vals:
                missing += 1
                ok = False
            elif vals[k].strip() == "":
                empties += 1
                ok = False
        if ok and len(keys) == len(set(keys)):
            conforming += 1
    cols = {}
    for k in req + ["status", "materiality", "descendants"]:
        vals = [v.get(k, "<<ABSENT>>") for _, v in recs]
        num, den = impurity_pair(vals)
        cols[k] = {"distinct": len(set(vals)), "impurity_num": num,
                   "impurity_den": den, "degenerate": num == 0}
    # materiality applied
    table = build_grade_table(schema)
    mult = {}
    for _, v in recs:
        cid = v.get("claim_id", "")
        mult[cid] = mult.get(cid, 0) + 1
    srank = schema["severity_rank"]
    counts = {"IMMATERIAL": 0, "MINOR": 0, "MATERIAL": 0, "CRITICAL": 0}
    unrankable = 0
    kinds = {}
    for _, v in recs:
        bits = v.get("id", "").split("-")
        kind = bits[1] if len(bits) > 1 else ""
        kinds[kind] = kinds.get(kind, 0) + 1
        k = SCOPE_BY_KIND.get(kind, 0)
        e = 0 if v.get("status") == "OPEN" else 1
        b = mult[v.get("claim_id", "")] - 1
        if b > 3:
            b = 3
        sev = srank.get(v.get("severity", ""))
        if sev is None:
            unrankable += 1          # fail closed: never silently graded
            continue
        counts[table[(sev, e, k, b)]] += 1
    nonempty_desc = 0
    for _, v in recs:
        d = v.get("descendants", "[]").strip()
        if d not in ("[]", "", "null"):
            nonempty_desc += 1
    return {
        "schema": "GMI_AA_GAP_OBJECT_RESULT_V1",
        "route": "B",
        "records": len(recs),
        "conforming": conforming,
        "missing_field_events": missing,
        "empty_cell_events": empties,
        "duplicate_key_records": dup_key_records,
        "distinct_claim_id": len(mult),
        "columns": cols,
        "degenerate_columns": sorted([k for k in cols if cols[k]["degenerate"]]),
        "grade_counts": counts,
        "unrankable_severity": unrankable,
        "kind_counts": kinds,
        "closure_chain": chain_check(schema),
        "records_with_nonempty_descendants": nonempty_desc,
    }


def main(argv):
    print(json.dumps(run(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
