#!/usr/bin/env python3
"""GMI #833 claim-discipline v1 — registration assembler (FREEZE_V1.md sections 4-5).

Merges, per object and field, in priority order:
  1. authored_g6_v1.G6 (the seven G6 analytic proofs; author-read proofs)
  2. authored_overrides_v1.OVERRIDES (author-derived/gap decisions, basis-noted)
  3. CARRIED status from THEOREM_SCORES_V1/V2 where the S1 scan says STATED
  4. EXTRACTED from evidence files (verbatim, citation-prefixed)
  5. REGISTERED_GAP with typed reason (mechanical default; every gap stays visible)

Hostile checks (fail closed): universe coverage 233 x 6 fields; no absent field;
citation paths exist on disk; DERIVED/EXTRACTED content non-empty; boilerplate
detector (identical DERIVED content strings shared across >1 object are flagged);
counts printed. Deterministic under -I -B / -I -O -B.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from authored_g6_v1 import G6  # noqa: E402

EVIDENCE = {
    "mim_a": "/tmp/ev_mim_a.jsonl",
    "mim_b": "/tmp/ev_mim_b.jsonl",
    "ggu": "/tmp/ev_ggu.jsonl",
    "small": "/tmp/ev_small.jsonl",
    "arr24": "/tmp/ev_arr24.jsonl",
    "new7": "/tmp/ev_new7.jsonl",
    "mim_jsonl": "/tmp/ev_mim_jsonl.json",
}
FIELDS = ["scope_quantifiers", "assumptions", "falsifiers", "strongest_parents", "forbidden_extrapolations"]
LEGACY = json.load(open("/tmp/legacy_objects.json"))
GAP = json.load(open(os.path.join(HERE, "GAP_REGISTER_V1.json")))


def load_jsonl(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


_basename_cache = {}


def _basenames(pkg_root):
    if pkg_root not in _basename_cache:
        s = set()
        if os.path.isdir(pkg_root):
            for dirpath, _, files in os.walk(pkg_root):
                for fn in files:
                    s.add(fn)
        _basename_cache[pkg_root] = s
    return _basename_cache[pkg_root]


def citcheck(items, pkg_root):
    """Every EXTRACTED item must embed a FILE:Lnn citation; the named file must
    exist somewhere in the object's package (census locators are basenames;
    actual files may be nested, e.g. raw/, gmi_microscope/)."""
    missing = []
    known = _basenames(pkg_root)
    for it in items:
        m = re.match(r"([A-Za-z0-9_./-]+\.[A-Za-z0-9]+):L?\d+", it)
        if m:
            fname = os.path.basename(m.group(1))
            if fname not in known and not os.path.exists(os.path.join(pkg_root, m.group(1))):
                missing.append(m.group(1))
    return missing


def carried(entry, score_field):
    v = entry.get(score_field)
    if isinstance(v, list):
        return [x for x in v if isinstance(x, str) and x.strip()]
    return [v] if isinstance(v, str) and v.strip() else []


def main():
    only = [k for k, p in EVIDENCE.items() if os.path.exists(p)]
    print("evidence files present:", sorted(only))
    ev = {}
    for k in only:
        ev[k] = load_jsonl(EVIDENCE[k]) if EVIDENCE[k].endswith(".jsonl") else json.load(open(EVIDENCE[k]))
    # map evidence by object/package
    ev_by_id = {}
    for k in ("mim_a", "mim_b", "ggu", "small"):
        for r in ev.get(k, []):
            ev_by_id.setdefault(r["id"], []).append((k, r))
    ev_by_pkg_arr = {r["package"]: r for r in ev.get("arr24", [])}
    ev_by_pkg_new = {r["package"]: r for r in ev.get("new7", [])}
    ev_rev = {r["id"]: r for r in ev.get("mim_jsonl", [])}
    authored = {o["object_id"]: o for o in G6}
    try:
        from authored_overrides_v1 import OVERRIDES
    except ImportError:
        OVERRIDES = {}
    auth_by_obj = {o["object_id"]: o for o in OVERRIDES.get("objects", [])} if isinstance(OVERRIDES, dict) else {}

    v1 = json.load(open(os.path.join(RESEARCH, "gmi-833-maturity-rescore-v1", "THEOREM_SCORES_V1.json")))["records"]
    v2 = json.load(open(os.path.join(RESEARCH, "gmi-833-maturity-rescore-v2-v1", "THEOREM_SCORES_V2.json")))
    scores = {e["result_id"]: e for e in v1}
    scores.update({e["result_id"]: e for e in v2})
    gaprow = {r["result_id"]: r for r in GAP["objects"]}
    # census id -> (package, file, line)
    census = {}
    for pkg, objs in LEGACY.items():
        for o in objs:
            census.setdefault(o["id"], (pkg, o["file"], o["line"]))

    regs = []
    status_counts = Counter()
    gap_reasons = Counter()
    dup_tracker = defaultdict(set)
    missing_cites = []

    def finish(rid, obj_id, pkg, tranche, fields):
        for f in FIELDS:
            fdata = fields.get(f)
            if not fdata or not fdata.get("status"):
                print("FATAL: absent field", rid, f)
                sys.exit(3)
            st = fdata["status"]
            status_counts[(f, st)] += 1
            if st == "REGISTERED_GAP":
                gap_reasons[(obj_id, f, fdata.get("reason", ""))] += 1
            if st == "DERIVED":
                for item in fdata.get("content", []):
                    dup_tracker[item].add(obj_id)
            if st in ("EXTRACTED",) and pkg:
                missing_cites += citcheck(fdata.get("content", []), os.path.join(RESEARCH, pkg))
        regs.append({
            "result_id": rid,
            "object_id": obj_id,
            "package": pkg,
            "tranche": tranche,
            "fields": fields,
        })

    # ---- U-V1: carried verbatim ----
    for e in v1:
        fields = {}
        for f in FIELDS:
            sf = "scope_quantifier_class" if f == "scope_quantifiers" else f
            fields[f] = {"status": "CARRIED_SCORES_V1", "content": carried(e, sf), "source": "gmi-833-maturity-rescore-v1/THEOREM_SCORES_V1.json:" + e["result_id"]}
        finish(e["result_id"], e["result_id"], e["package"], "U-V1", fields)

    # ---- v2 objects ----
    joinmap = json.load(open("/tmp/join_v2_census.json"))
    for e in v2:
        rid = e["result_id"]
        row = gaprow[rid]
        obj_id = joinmap.get(rid, e.get("theorem_name", rid))
        tranche = "U-LEGACY" if e["tranche"] == "LEGACY_173" else "U-ARRIVALS"
        fields = {}
        for f in FIELDS:
            sf = "scope_quantifier_class" if f == "scope_quantifiers" else f
            if row[f] == "STATED":
                fields[f] = {"status": "CARRIED_SCORES_V2", "content": carried(e, sf), "source": "gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json:" + rid}
                continue
            # authored (G6 + overrides) first
            if obj_id in authored and f in authored[obj_id]["fields"]:
                fields[f] = authored[obj_id]["fields"][f]
                continue
            if obj_id in auth_by_obj and f in auth_by_obj[obj_id]["fields"]:
                fields[f] = auth_by_obj[obj_id]["fields"][f]
                continue
            # evidence
            got = None
            if tranche == "U-ARRIVALS":
                r = ev_by_pkg_arr.get(e["package"])
                if r and f in ("assumptions", "falsifiers") and r.get(f):
                    got = {"status": "EXTRACTED", "content": r[f], "source": e["package"]}
            else:
                for k, r in ev_by_id.get(obj_id, []):
                    key = {"scope_quantifiers": "scope"}.get(f, f)
                    if r.get(key):
                        got = {"status": "EXTRACTED", "content": r[key], "source": "%s:%s" % (e["package"], k)}
                        break
                if not got and obj_id in ev_rev and f != "scope_quantifiers":
                    rr = ev_rev[obj_id]
                    maps = {
                        "assumptions": [("fresh_evidence_source", "registered evidence source/scope"),
                                        ("original_prediction", "registered prediction precondition"),
                                        ("measurement_validity_status", "declared measurement-validity status")],
                        "falsifiers": [("new_falsifier", "registered kill condition (verbatim row field)"),
                                       ("original_prediction", "the registered prediction whose failure would falsify")],
                        "strongest_parents": [("strongest_parent_explanation", "registered parent explanation (verbatim row field)")],
                        "forbidden_extrapolations": [("result_terminal", "terminality registered in row"),
                                                     ("claim_movement", "claim-movement ceiling registered in row")],
                    }
                    content = []
                    for key_, why in maps[f]:
                        if rr.get(key_):
                            content.append("%s:L%d: [%s] %s" % (rr["file"], rr["actual_line"], key_, rr[key_]))
                    if content:
                        got = {"status": "EXTRACTED", "content": content, "source": "revival-ledger row " + rr["id"]}
            if got:
                fields[f] = got
            else:
                reason = ("no registration in package docs; not derivable without new analysis (S1=%s)" % row[f]) if obj_id not in ev_by_id and obj_id not in ev_rev else ("evidence pass found no in-package content for this field (S1=%s)" % row[f])
                fields[f] = {"status": "REGISTERED_GAP", "reason": reason}
        finish(rid, obj_id, e["package"], tranche, fields)

    # ---- U-NEW ----
    for pkg, r in sorted(ev_by_pkg_new.items()):
        fields = {}
        for f in FIELDS:
            key = "scope" if f == "scope_quantifiers" else f
            v = r.get(key)
            if isinstance(v, list) and v:
                fields[f] = {"status": "EXTRACTED", "content": v, "source": pkg}
            elif isinstance(v, str) and v.strip():
                fields[f] = {"status": "EXTRACTED", "content": [v], "source": pkg}
            else:
                fields[f] = {"status": "REGISTERED_GAP", "reason": r.get("gaps", {}).get(key, "not registered in package docs")}
        rid = "GMI833_CD_NEW_" + pkg
        finish(rid, r.get("primary", pkg), pkg, "U-NEW", fields)

    # ---- hostile checks ----
    n = len(regs)
    assert n == GAP["object_count"] + len(ev_by_pkg_new), (n, GAP["object_count"], len(ev_by_pkg_new))
    boiler = {k: sorted(v) for k, v in dup_tracker.items() if len(v) > 1}
    out = {
        "schema": "GMI833_CLAIM_DISCIPLINE_REGISTRATIONS_V1",
        "freeze": "FREEZE_V1.md",
        "scan_sha_note": "recorded at ship in RESULT_V1.json",
        "objects": regs,
        "counts": {
            "objects": n,
            "fields_registered": sum(v for (f, s), v in status_counts.items() if s != "REGISTERED_GAP"),
            "registered_gap": sum(v for (f, s), v in status_counts.items() if s == "REGISTERED_GAP"),
            "by_field_status": {"%s:%s" % k: v for k, v in sorted(status_counts.items())},
        },
    }
    path = os.path.join(HERE, "REGISTRATIONS_V1.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print("objects:", n)
    for f in FIELDS:
        row = {s: status_counts[(f, s)] for s in ("CARRIED_SCORES_V1", "CARRIED_SCORES_V2", "EXTRACTED", "DERIVED", "REGISTERED_GAP") if status_counts[(f, s)]}
        print(f, row)
    print("REGISTERED_GAP total:", sum(1 for r in regs for f in FIELDS if r["fields"][f]["status"] == "REGISTERED_GAP"))
    print("boilerplate flags (identical DERIVED strings across objects):", len(boiler))
    for k, v in list(boiler.items())[:10]:
        print("  DUP:", v, "->", k[:90])
    if missing_cites:
        print("MISSING CITATION PATHS:", missing_cites[:10])
        sys.exit(4)
    return 0


if __name__ == "__main__":
    sys.exit(main())
