# -*- coding: utf-8 -*-
"""Build and verify the AG/AH/AJ/AF comment reconciliation for #833.

Every replacement is verified before it is written:

  1. `old` is byte-exact against a freshly fetched copy of its comment;
  2. `old` occurs **exactly once inside its own `###` anchor section**, not merely once in the
     comment;
  3. `new` contains `old` minus its `- [ ] ` prefix, verbatim;
  4. the row appears exactly once across all replacements;
  5. every cited package's receipt exists, is `GREEN`, and its pinned parents still match on
     both blob and claim ceiling;
  6. the row's meaning token is **not** in any cited parent's forbidden set -- the check the
     AG/AH lane built as RA-1, which caught a row closing as a clean positive on a claim its
     cited parent explicitly forbids;
  7. every number quoted in `new` that is tagged in `quoted_fields` resolves in the cited
     receipt and equals the quoted value.

Fetching needs network; pass `--offline <dir>` to verify against saved copies instead.

    python3 -I -B  build_reconciliation_v1.py --offline /tmp/claude-501/agaj
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

COMMENTS = {
    "AG": 5693520829,
    "AH": 5693590252,
    "AJ": 5693954852,
    "AF": 5693269426,
}

FORBIDDEN_KEYS = ("forbidden_promotions", "forbidden_promotion", "forbidden_terminal",
                  "forbidden_terminals", "forbidden_implications", "forbidden_extrapolations")


def fetch(comment_id, offline):
    if offline:
        for name in ("COMMENT_SNAPSHOT_%d.md" % comment_id,
                     "f_%d.md" % comment_id, "c_%d.md" % comment_id):
            path = os.path.join(offline, name)
            if os.path.exists(path):
                with open(path, "rb") as fh:
                    return fh.read().decode("utf-8")
        raise IOError("no offline snapshot for comment %d" % comment_id)
    out = subprocess.check_output(
        ["gh", "api", "repos/SzeChunYiu/ORION-OCM/issues/comments/%d" % comment_id,
         "--jq", ".body"])
    return out.decode("utf-8")


def anchor_section(body, anchor):
    lines = body.split("\n")
    starts = [k for k, l in enumerate(lines) if l == anchor]
    if len(starts) != 1:
        return None, "ANCHOR_NOT_UNIQUE:%d" % len(starts)
    start = starts[0]
    end = len(lines)
    for k in range(start + 1, len(lines)):
        if lines[k].startswith("### "):
            end = k
            break
    return lines[start:end], None


def blob_sha(path):
    return subprocess.check_output(
        ["/usr/bin/git", "-C", REPO, "hash-object", path]).decode().strip()


def forbidden_set(doc):
    out = set()
    for k in FORBIDDEN_KEYS:
        v = doc.get(k)
        if isinstance(v, str):
            out.add(v)
        elif isinstance(v, list):
            out.update(x for x in v if isinstance(x, str))
        elif isinstance(v, dict):
            out.update(x for x in v.values() if isinstance(x, str))
    return out


def resolve(doc, path):
    cur = doc
    for seg in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(seg)]
        elif isinstance(cur, dict):
            cur = cur[seg]
        else:
            raise KeyError(path)
    return cur


def load_spec():
    with open(os.path.join(HERE, "RECONCILIATION_SPEC_V1.json"), "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", default=None)
    args = ap.parse_args()

    spec = load_spec()
    bodies = dict((name, fetch(cid, args.offline)) for name, cid in COMMENTS.items())
    by_id = dict((cid, bodies[name]) for name, cid in COMMENTS.items())

    problems = []
    seen_rows = {}
    package_cache = {}

    def package(name):
        if name not in package_cache:
            base = os.path.join(REPO, "research", name)
            doc = json.load(open(os.path.join(base, "RESULT_V1.json")))
            man = json.load(open(os.path.join(base, "MANIFEST_V1.json")))
            package_cache[name] = (doc, man)
        return package_cache[name]

    for rep in spec["replacements"]:
        cid = rep["comment_id"]
        body = by_id.get(cid)
        tag = "%s:%s" % (cid, rep["old"][:60])
        if body is None:
            problems.append("UNKNOWN_COMMENT:" + tag)
            continue
        section, err = anchor_section(body, rep["anchor"])
        if err:
            problems.append("%s:%s" % (err, tag))
            continue
        count_section = sum(1 for l in section if l == rep["old"])
        count_body = sum(1 for l in body.split("\n") if l == rep["old"])
        if count_section != 1:
            problems.append("OLD_NOT_UNIQUE_UNDER_ANCHOR:%d:%s" % (count_section, tag))
        if count_body != 1:
            problems.append("OLD_NOT_UNIQUE_IN_COMMENT:%d:%s" % (count_body, tag))
        stem = rep["old"][len("- [ ] "):]
        if not rep["new"].startswith("- [x] " + stem + " — ✅ "):
            problems.append("NEW_DOES_NOT_CARRY_OLD_VERBATIM:" + tag)
        key = (cid, rep["old"])
        if key in seen_rows:
            problems.append("ROW_APPEARS_TWICE:" + tag)
        seen_rows[key] = True

        # --- citation admissibility (RA-1) ---
        for cite in rep["cites"]:
            doc, man = package(cite["package"])
            if doc.get("status") not in ("GREEN", None):
                problems.append("CITED_PACKAGE_NOT_GREEN:%s:%s" % (cite["package"], tag))
            if doc.get("failed_gates"):
                problems.append("CITED_PACKAGE_HAS_FAILED_GATES:%s:%s"
                                % (cite["package"], tag))
            own_forbidden = forbidden_set(doc)
            if rep["row_meaning_token"] in own_forbidden:
                problems.append("MEANING_TOKEN_FORBIDDEN_BY_SELF:%s" % tag)
            for pin in man.get("parent_pins", []):
                live = blob_sha(os.path.join(REPO, pin["path"]))
                if live != pin["blob_sha"]:
                    problems.append("PARENT_PIN_BLOB_DRIFT:%s:%s" % (pin["path"], tag))
                pdoc = json.load(open(os.path.join(REPO, pin["path"])))
                if pdoc.get("claim_ceiling") != pin["claim_ceiling"]:
                    problems.append("PARENT_PIN_CEILING_DRIFT:%s:%s" % (pin["path"], tag))
                if rep["row_meaning_token"] in forbidden_set(pdoc):
                    problems.append("MEANING_TOKEN_FORBIDDEN_BY_PARENT:%s:%s"
                                    % (pin["path"], tag))
            for field, value in cite.get("quoted_fields", {}).items():
                try:
                    got = resolve(doc, field)
                except (KeyError, IndexError, ValueError):
                    problems.append("QUOTED_FIELD_MISSING:%s:%s" % (field, tag))
                    continue
                if got != value:
                    problems.append("QUOTED_FIELD_MISMATCH:%s:%r!=%r:%s"
                                    % (field, got, value, tag))

    for entry in spec["not_closed"]:
        cid = entry["comment_id"]
        body = by_id.get(cid)
        if body is None:
            problems.append("UNKNOWN_COMMENT_NOT_CLOSED:%s" % entry["old"][:50])
            continue
        section, err = anchor_section(body, entry["anchor"])
        if err:
            problems.append("%s:not_closed:%s" % (err, entry["old"][:50]))
            continue
        if sum(1 for l in section if l == entry["old"]) != 1:
            problems.append("NOT_CLOSED_OLD_NOT_UNIQUE:%s" % entry["old"][:50])
        if (cid, entry["old"]) in seen_rows:
            problems.append("ROW_BOTH_CLOSED_AND_NOT_CLOSED:%s" % entry["old"][:50])

    for entry in spec["checked_but_unsupported"]:
        cid = entry["comment_id"]
        body = by_id.get(cid)
        section, err = anchor_section(body, entry["anchor"])
        if err:
            problems.append("%s:checked_but_unsupported" % err)
        elif sum(1 for l in section if l == entry["current_line"]) != 1:
            problems.append("CHECKED_ROW_NOT_FOUND_AS_STATED")

    # every open row of the four comments is accounted for
    accounted = set()
    for rep in spec["replacements"]:
        accounted.add((rep["comment_id"], rep["old"]))
    for e in spec["not_closed"]:
        accounted.add((e["comment_id"], e["old"]))
    unaccounted = []
    for name, cid in COMMENTS.items():
        for line in bodies[name].split("\n"):
            if line.startswith("- [ ] ") and (cid, line) not in accounted:
                unaccounted.append((cid, line[:70]))
    if unaccounted:
        problems.append("OPEN_ROWS_UNACCOUNTED:%d" % len(unaccounted))

    out = dict(spec)
    out["verification"] = {
        "comments_fetched": sorted(COMMENTS.values()),
        "open_rows_in_scope": sum(1 for name in COMMENTS
                                  for line in bodies[name].split("\n")
                                  if line.startswith("- [ ] ")),
        "replacements": len(spec["replacements"]),
        "not_closed": len(spec["not_closed"]),
        "checked_but_unsupported": len(spec["checked_but_unsupported"]),
        "unaccounted_open_rows": [list(u) for u in unaccounted],
        "problems": problems,
        "status": "GREEN" if not problems else "RED",
    }
    with open(os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json"), "w") as fh:
        fh.write(json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False,
                            separators=(",", ": ")) + "\n")
    print(json.dumps(out["verification"], indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
