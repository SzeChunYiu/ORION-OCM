# -*- coding: utf-8 -*-
"""RA-1 route A -- citation admissibility auditor for AG/AH parent reconciliations.

A row closed by citing a merged parent is a *misreport risk*, not a proof.  RA-1
decides, mechanically, whether each citation is admissible.  It does NOT prove
any row's scientific content; that stays owned by the cited parent.

A citation is admissible iff ALL of:

  1. the cited package exists and its RESULT_V1.json git blob sha equals the
     pinned value;
  2. every cited field path resolves in that receipt AND its canonical JSON
     rendering equals the pinned value byte-exactly;
  3. the row's `row_meaning_token` -- what closing the row as a clean positive
     would assert -- is NOT in the cited parent's forbidden set (the union of
     forbidden_promotions / forbidden_promotion / forbidden_terminal /
     forbidden_terminals / forbidden_implications);
  4. the parent's status/verdict field, where present, is GREEN.

And, per replacement:

  5. `old` and `anchor` are byte-exact against the pinned AGAH_ROWS_V1.json;
  6. `new` contains `old` minus its "- [ ] " prefix, verbatim;
  7. the row appears exactly once across all replacements;
  8. `bucket` is in the closed vocabulary.

    python3 -I -B citation_audit_v1.py
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

BUCKETS = ("HARNESS", "EXACT-FORMAL", "DISCIPLINE-CONTRACT", "NEW-SCIENCE", "EXTERNAL-GATE")
FORBIDDEN_KEYS = ("forbidden_promotions", "forbidden_promotion", "forbidden_terminal",
                  "forbidden_terminals", "forbidden_implications", "forbidden_extrapolations")
STATUS_KEYS = ("status", "verdict")


def blob_sha(path):
    with open(path, "rb") as fh:
        data = fh.read()
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\x00")
    h.update(data)
    return h.hexdigest()


def resolve(doc, path):
    cur = doc
    for seg in path.split("."):
        if isinstance(cur, list):
            i = int(seg)
            if i >= len(cur):
                raise KeyError(path)
            cur = cur[i]
        elif isinstance(cur, dict):
            if seg not in cur:
                raise KeyError(path)
            cur = cur[seg]
        else:
            raise KeyError(path)
    return cur


def forbidden_set(doc):
    out = set()
    for k in FORBIDDEN_KEYS:
        v = doc.get(k)
        if isinstance(v, str):
            out.add(v)
        elif isinstance(v, list):
            out.update(x for x in v if isinstance(x, str))
        elif isinstance(v, dict):
            for vv in v.values():
                if isinstance(vv, str):
                    out.add(vv)
                elif isinstance(vv, list):
                    out.update(x for x in vv if isinstance(x, str))
    return out


def audit(table, rows, repo=REPO):
    v = dict((k, 0) for k in (
        "package_failures", "pin_failures", "field_failures", "value_failures",
        "forbidden_conflicts", "status_failures", "row_text_failures",
        "anchor_failures", "new_line_failures", "duplicate_rows",
        "bucket_failures", "status_vocab_failures", "uncheckable"))
    pinned = {}
    for r in rows:
        pinned[(r["cid"], r["row"])] = r["anchor"]

    seen = set()
    for rep in table["replacements"]:
        key = (rep["comment_id"], rep["old"])
        if key in seen:
            v["duplicate_rows"] += 1
        seen.add(key)
        if key not in pinned:
            v["row_text_failures"] += 1
        elif pinned[key] != rep["anchor"]:
            v["anchor_failures"] += 1
        if rep["old"][len("- [ ] "):] not in rep["new"]:
            v["new_line_failures"] += 1
        if not rep["new"].startswith("- [x] "):
            v["new_line_failures"] += 1
        if rep.get("bucket") not in BUCKETS:
            v["bucket_failures"] += 1
        if rep.get("status") not in ("EARNED", "EARNED_BY_COUNTEREXAMPLE"):
            v["status_vocab_failures"] += 1

        for c in rep["citations"]:
            full = os.path.join(repo, c["receipt_path"])
            if not os.path.exists(full):
                v["package_failures"] += 1
                v["uncheckable"] += 1
                continue
            if blob_sha(full) != c["blob_sha"]:
                v["pin_failures"] += 1
            try:
                with open(full) as fh:
                    doc = json.load(fh)
            except Exception:
                v["uncheckable"] += 1
                continue
            for path, pinned_value in sorted(c["fields"].items()):
                try:
                    got = resolve(doc, path)
                except (KeyError, ValueError, IndexError):
                    v["field_failures"] += 1
                    continue
                if json.dumps(got, sort_keys=True) != pinned_value:
                    v["value_failures"] += 1
            if rep["row_meaning_token"] in forbidden_set(doc):
                v["forbidden_conflicts"] += 1
            for sk in STATUS_KEYS:
                if sk in doc and isinstance(doc[sk], str):
                    if doc[sk] != "GREEN":
                        v["status_failures"] += 1
                    break
    return v


def main():
    table = json.load(open(os.path.join(HERE, "CITATION_TABLE_V1.json")))
    smap = json.load(open(os.path.join(HERE, "AGAH_STRUCTURAL_MAP_V1.json")))
    rows = json.load(open(os.path.join(HERE, "AGAH_ROWS_V1.json")))
    v = audit(table, rows)

    reps = table["replacements"]
    pkgs = sorted(set(c["package"] for r in reps for c in r["citations"]))
    fields = sum(len(c["fields"]) for r in reps for c in r["citations"])
    bucket_hist = {}
    disp_hist = {}
    for r in smap["rows"]:
        bucket_hist[r["bucket"]] = bucket_hist.get(r["bucket"], 0) + 1
        disp_hist[r["disposition"]] = disp_hist.get(r["disposition"], 0) + 1

    result = {
        "schema": "AGAH_MAP_RESULT_V1",
        "issue": 833,
        "claim_ceiling": ("AGAH_STRUCTURAL_MAP_AND_PARENT_CITATION_ADMISSIBILITY_AUDITED_AT_"
                          "REGISTERED_MERGED_CORPUS_SCOPE"),
        "results": ["RA-1", "RA-2"],
        "total_open_rows": smap["total_open_rows"],
        "rows_mapped": len(smap["rows"]),
        "bucket_histogram": bucket_hist,
        "disposition_histogram": disp_hist,
        "citations_audited": len(reps),
        "distinct_parent_packages_cited": len(pkgs),
        "parent_packages_cited": pkgs,
        "receipt_fields_verified": fields,
        "violations": v,
        "earned_by_counterexample_rows": sorted(r["row_index"] for r in reps
                                                if r["status"] == "EARNED_BY_COUNTEREXAMPLE"),
        "forbidden_promotions": ["AG_AH_SECTIONS_DISCHARGED", "PARENT_CITATION_PROVES_ROW_CONTENT",
                                 "BUCKET_CLASSIFICATION_IS_A_THEOREM", "COMPLETE_GMI"],
        "scope_note": ("RA-1 decides citation admissibility only. It does not prove the cited "
                       "row's scientific content; that remains owned by the cited parent."),
    }
    gates = [
        ("no_violations", all(x == 0 for x in v.values())),
        ("all_75_rows_mapped", len(smap["rows"]) == 75),
        ("every_bucket_used", len(bucket_hist) == 5),
        ("citations_present", len(reps) == 40),
    ]
    failed = [g for g, ok in gates if not ok]
    result["gates"] = dict(gates)
    result["failed_gates"] = failed
    result["status"] = "GREEN" if not failed else "RED"
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"status": result["status"], "failed_gates": failed, "violations": v,
                      "citations": len(reps), "fields": fields,
                      "buckets": bucket_hist, "dispositions": disp_hist}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
