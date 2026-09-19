# -*- coding: utf-8 -*-
"""RA-1 tests: two-route agreement, detected hostiles, null, no-alarm case.

    python3 -I -O -B test_agah_map_v1.py
"""

import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import citation_audit_v1 as A   # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    if not cond:
        FAIL.append("%s %s" % (name, detail))
    return cond


def find(table, row_index):
    for i, r in enumerate(table["replacements"]):
        if r["row_index"] == row_index:
            return i
    raise KeyError(row_index)


def main():
    table = json.load(open(os.path.join(HERE, "CITATION_TABLE_V1.json")))
    rows = json.load(open(os.path.join(HERE, "AGAH_ROWS_V1.json")))
    smap = json.load(open(os.path.join(HERE, "AGAH_STRUCTURAL_MAP_V1.json")))
    res = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
    ora = json.load(open(os.path.join(HERE, "ORACLE_RESULT_V1.json")))

    clean = A.audit(table, rows)

    # ---------------- no-alarm case ---------------------------------------
    check("NO_ALARM_ALL_COUNTERS_ZERO", all(x == 0 for x in clean.values()), str(clean))
    check("NO_ALARM_STATUS_GREEN", res["status"] == "GREEN" and res["failed_gates"] == [])
    check("NO_ALARM_75_ROWS", len(smap["rows"]) == 75 and len(rows) == 75)
    check("NO_ALARM_ALL_ROWS_UNIQUE",
          len(set((r["cid"], r["row"]) for r in rows)) == 75)

    # ---------------- two materially independent routes -------------------
    check("ROUTE_REPLACEMENTS", res["citations_audited"] == ora["replacements"] == 40)
    check("ROUTE_FIELDS", res["receipt_fields_verified"] == ora["fields_checked"] == 185)
    check("ROUTE_PACKAGES", res["distinct_parent_packages_cited"] == ora["distinct_packages"],
          str((res["distinct_parent_packages_cited"], ora["distinct_packages"])))
    for a, b in (("pin_failures", "pin_failures"), ("field_failures", "field_failures"),
                 ("value_failures", "value_failures"),
                 ("forbidden_conflicts", "forbidden_conflicts"),
                 ("row_text_failures", "row_text_failures"),
                 ("status_failures", "status_failures")):
        check("ROUTE_%s" % a.upper(), clean[a] == ora[b] == 0)
    check("ROUTE_ROW_SPLIT", ora["rows_closed"] == 55 and ora["rows_open"] == 20)

    # ---------------- hostiles, each with a moved counter -----------------
    detected = {}

    def hostile(name, counter, mutate, repo=REPO, rows_arg=None):
        t = copy.deepcopy(table)
        rr = copy.deepcopy(rows_arg if rows_arg is not None else rows)
        mutate(t, rr)
        v = A.audit(t, rr, repo=repo)
        moved = v[counter] > clean[counter]
        detected[name] = moved
        check("%s_MOVES" % name, moved,
              "%s clean=%d hostile=%d" % (counter, clean[counter], v[counter]))
        return v

    hostile("HA1_CORRUPTED_PIN", "pin_failures",
            lambda t, r: t["replacements"][0]["citations"][0].__setitem__("blob_sha", "0" * 40))
    hostile("HA2_FIELD_ABSENT_FROM_RECEIPT", "field_failures",
            lambda t, r: t["replacements"][0]["citations"][0]["fields"].__setitem__(
                "not_a_real_field", "1"))
    hostile("HA3_TAMPERED_VALUE", "value_failures",
            lambda t, r: t["replacements"][0]["citations"][0]["fields"].__setitem__(
                sorted(t["replacements"][0]["citations"][0]["fields"])[0], '"TAMPERED"'))

    # HA4 is the real case the advisor named: closing AG3's
    # "flagship primitive claims must survive presentation replacement" as a
    # CLEAN positive citing AJ5 would assert COMPILER_MAKES_SEARCH_BIAS_INVARIANT,
    # which AJ5 explicitly forbids.  The auditor must refuse that citation.
    i17 = find(table, 17)
    check("HA4_TOKEN_IS_REALLY_FORBIDDEN",
          "COMPILER_MAKES_SEARCH_BIAS_INVARIANT" in json.load(open(os.path.join(
              REPO, "research/gmi-833-aj5-g0-lowering-v1/RESULT_V1.json")))["forbidden_promotions"])
    hostile("HA4_ROW_MEANING_IS_A_FORBIDDEN_PROMOTION", "forbidden_conflicts",
            lambda t, r: t["replacements"][i17].__setitem__(
                "row_meaning_token", "COMPILER_MAKES_SEARCH_BIAS_INVARIANT"))

    hostile("HA5_NONEXISTENT_PACKAGE", "package_failures",
            lambda t, r: t["replacements"][1]["citations"][0].__setitem__(
                "receipt_path", "research/gmi-833-does-not-exist-v1/RESULT_V1.json"))
    hostile("HA6_DUPLICATE_ROW", "duplicate_rows",
            lambda t, r: t["replacements"].append(copy.deepcopy(t["replacements"][2])))
    def ha7(t, r):
        rep = t["replacements"][3]
        drifted = rep["old"][:-1] + " "          # one trailing character changed
        rep["new"] = rep["new"].replace(rep["old"][len("- [ ] "):], drifted[len("- [ ] "):])
        rep["old"] = drifted
    v7 = hostile("HA7_ROW_TEXT_DRIFT", "row_text_failures", ha7)
    check("HA7_IS_ISOLATED", v7["new_line_failures"] == 0,
          "a one-character row drift must be caught by the row-text gate alone")
    hostile("HA8_ANCHOR_DRIFT", "anchor_failures",
            lambda t, r: t["replacements"][4].__setitem__(
                "anchor", "### AG5 - G0 must be derivable from lower relations/processes"))
    hostile("HA9_NEW_LINE_DROPS_THE_ROW", "new_line_failures",
            lambda t, r: t["replacements"][5].__setitem__(
                "new", "- [x] closed by a merged parent."))
    hostile("HA10_BUCKET_OUTSIDE_VOCABULARY", "bucket_failures",
            lambda t, r: t["replacements"][6].__setitem__("bucket", "PROBABLY_FINE"))

    # HA11 a parent whose own receipt is not GREEN.
    tmp = tempfile.mkdtemp(prefix="agah-ha11-")
    try:
        src_pkg = table["replacements"][0]["citations"][0]["package"]
        dst = os.path.join(tmp, "research", src_pkg)
        os.makedirs(dst)
        doc = json.load(open(os.path.join(REPO, "research", src_pkg, "RESULT_V1.json")))
        doc["status"] = "RED"
        with open(os.path.join(dst, "RESULT_V1.json"), "w") as fh:
            json.dump(doc, fh, indent=1, sort_keys=True)
            fh.write("\n")
        t = copy.deepcopy(table)
        t["replacements"] = [r for r in t["replacements"]
                             if all(c["package"] == src_pkg for c in r["citations"])][:1]
        # the copy's sha will differ; neutralise the pin check so only status moves
        for c in t["replacements"][0]["citations"]:
            c["blob_sha"] = A.blob_sha(os.path.join(dst, "RESULT_V1.json"))
            c["fields"] = {}
        v11 = A.audit(t, rows, repo=tmp)
        detected["HA11_PARENT_RECEIPT_NOT_GREEN"] = v11["status_failures"] > 0
        check("HA11_MOVES", v11["status_failures"] > 0 and v11["pin_failures"] == 0,
              str(v11))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    check("ALL_HOSTILES_DETECTED", all(detected.values()),
          str([k for k in detected if not detected[k]]))
    check("HOSTILE_COUNT", len(detected) == 11, str(len(detected)))

    # ---------------- null: 200 misdirected citations ---------------------
    all_pkgs = sorted(set(c["package"] for r in table["replacements"] for c in r["citations"]))
    seed = 8331120
    admissible = 0
    for _ in range(200):
        t = copy.deepcopy(table)
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        ri = seed % len(t["replacements"])
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        pk = all_pkgs[seed % len(all_pkgs)]
        c = t["replacements"][ri]["citations"][0]
        if c["package"] == pk:
            continue
        c["package"] = pk
        c["receipt_path"] = "research/%s/RESULT_V1.json" % pk
        v = A.audit(t, rows)
        if all(x == 0 for x in v.values()):
            admissible += 1
    check("NULL_ZERO", admissible == 0, "admissible=%d/200" % admissible)

    if FAIL:
        for f in FAIL:
            sys.stderr.write("FAIL %s\n" % f)
        return 1
    summary = {"tests": "PASS", "hostiles_detected": len(detected),
               "null_admissible": admissible, "routes": 2,
               "citations": len(table["replacements"]),
               "fields_verified": res["receipt_fields_verified"],
               "rows_closed": ora["rows_closed"], "rows_open": ora["rows_open"]}
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
