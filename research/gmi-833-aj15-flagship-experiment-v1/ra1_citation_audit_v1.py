# -*- coding: utf-8 -*-
"""RA-1 -- citation admissibility audit for ISSUE_833_COMMENT_RECONCILIATION_V1.json.

Every replacement cites parent receipts.  A citation is admissible iff ALL of:
  1. the cited receipt exists and its git blob sha equals the pinned value;
  2. every cited field path resolves and its canonical JSON rendering equals the pinned
     value byte-exactly;
  3. the row's `row_meaning_token` is not in the cited receipt's forbidden set (union of
     forbidden_promotions / forbidden_promotion / forbidden_terminal / forbidden_terminals /
     forbidden_implications / forbidden_extrapolations);
  4. the receipt's status/verdict, where present, is GREEN or CONFIRMED.
And per replacement:
  5. `old` occurs exactly once in the fetched comment text under its `###` anchor;
  6. `new` starts with `- [x] ` and contains `old` minus its `- [ ] ` prefix verbatim;
  7. no row appears twice.
RA-1 proves a citation is not a misreport of its parent.  It does not prove the row's
scientific content; that stays owned by the cited receipt.

    python3 -I -B ra1_citation_audit_v1.py [--recon FILE] [--comments DIR] [--self-test]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
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
FORBIDDEN_KEYS = ("forbidden_promotions", "forbidden_promotion", "forbidden_terminal",
                  "forbidden_terminals", "forbidden_implications", "forbidden_extrapolations")


def blob_sha(path):
    data = _read_bytes(path)
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\x00")
    h.update(data)
    return h.hexdigest()


def resolve(doc, path):
    cur = doc
    for seg in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(seg)]
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
    return out


def section_text(comment_text, anchor):
    lines = comment_text.split("\n")
    out = []
    inside = False
    for line in lines:
        if line.startswith("### "):
            inside = line == anchor
            continue
        if inside:
            out.append(line)
    return out


def audit(recon, comments, repo=REPO):
    v = {k: 0 for k in ("package_failures", "pin_failures", "field_failures", "value_failures",
                        "forbidden_conflicts", "status_failures", "row_text_failures",
                        "new_line_failures", "duplicate_rows", "anchor_failures")}
    seen = set()
    fields_checked = 0
    packages = set()
    for rep in recon["replacements"]:
        key = (rep["comment_id"], rep["old"])
        if key in seen:
            v["duplicate_rows"] += 1
        seen.add(key)
        text = comments.get(rep["comment_id"])
        if text is None:
            v["anchor_failures"] += 1
        else:
            sec = section_text(text, rep["anchor"])
            if not sec:
                v["anchor_failures"] += 1
            elif sec.count(rep["old"]) != 1:
                v["row_text_failures"] += 1
        if not rep["new"].startswith("- [x] ") or rep["old"][len("- [ ] "):] not in rep["new"]:
            v["new_line_failures"] += 1
        for c in rep.get("citations", []):
            full = os.path.join(repo, c["receipt_path"])
            packages.add(c["package"])
            if not os.path.exists(full):
                v["package_failures"] += 1
                continue
            if blob_sha(full) != c["blob_sha"]:
                v["pin_failures"] += 1
            doc = _load_json(full)
            for path, pinned in sorted(c.get("fields", {}).items()):
                fields_checked += 1
                try:
                    got = resolve(doc, path)
                except (KeyError, ValueError, IndexError, TypeError):
                    v["field_failures"] += 1
                    continue
                if json.dumps(got, sort_keys=True) != pinned:
                    v["value_failures"] += 1
            if rep.get("row_meaning_token") in forbidden_set(doc):
                v["forbidden_conflicts"] += 1
            st = doc.get("status", doc.get("verdict"))
            if isinstance(st, str) and st not in ("GREEN", "CONFIRMED"):
                v["status_failures"] += 1
    return v, fields_checked, sorted(packages)


def self_test(recon, comments):
    """Each planted defect must move exactly the counter it targets."""
    base, _, _ = audit(recon, comments)
    results = {}

    def planted(mutate, counter):
        r = json.loads(json.dumps(recon))
        mutate(r)
        v, _, _ = audit(r, comments)
        results[counter] = v[counter] > base[counter]

    rep0 = recon["replacements"][0]
    if rep0.get("citations"):
        planted(lambda r: r["replacements"][0]["citations"][0].__setitem__("blob_sha", "0" * 40), "pin_failures")
        planted(lambda r: r["replacements"][0]["citations"][0]["fields"].__setitem__("no.such.field", "1"), "field_failures")
        planted(lambda r: r["replacements"][0]["citations"][0]["fields"].__setitem__(
            sorted(r["replacements"][0]["citations"][0]["fields"])[0], '"PLANTED"'), "value_failures")
        planted(lambda r: r["replacements"][0].__setitem__("row_meaning_token", "COMPLETE_GMI"), "forbidden_conflicts")
        planted(lambda r: r["replacements"][0]["citations"][0].__setitem__("receipt_path", "research/none/RESULT_V1.json"), "package_failures")
    planted(lambda r: r["replacements"][0].__setitem__("old", r["replacements"][0]["old"] + " "), "row_text_failures")
    planted(lambda r: r["replacements"][0].__setitem__("new", "- [ ] planted"), "new_line_failures")
    planted(lambda r: r["replacements"].append(json.loads(json.dumps(r["replacements"][0]))), "duplicate_rows")
    planted(lambda r: r["replacements"][0].__setitem__("anchor", "### nowhere"), "anchor_failures")
    return results


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--recon", default=os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json"))
    ap.add_argument("--comments", default=os.path.join(HERE, "comment_fetches"))
    ap.add_argument("--out", default=os.path.join(HERE, "RA1_AUDIT_RESULT_V1.json"))
    args = ap.parse_args(argv)
    recon = _load_json(args.recon)
    comments = {}
    for fn in os.listdir(args.comments):
        if fn.endswith(".txt"):
            comments[int(fn.split(".")[0])] = _read_text(os.path.join(args.comments, fn))
    v, nfields, pkgs = audit(recon, comments)
    st = self_test(recon, comments)
    ok = all(x == 0 for x in v.values()) and all(st.values())
    out = {"schema": "AJ15_RA1_AUDIT_RESULT_V1", "result": "RA-1", "replacements_audited": len(recon["replacements"]),
           "receipt_fields_verified": nfields, "parent_packages_cited": pkgs, "violations": v,
           "self_test_each_planted_defect_moves_its_counter": st,
           "scope_note": "RA-1 decides citation admissibility only; it does not prove the cited row's scientific content.",
           "status": "GREEN" if ok else "RED"}
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"status": out["status"], "violations": v, "fields": nfields, "self_test": st}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
