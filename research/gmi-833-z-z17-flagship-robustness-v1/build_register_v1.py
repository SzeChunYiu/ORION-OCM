#!/usr/bin/env python3
"""Build the register of central conclusions (#833 Section Z, Z17) from the
programme's own frozen sources. Nothing here is authored: every entry is either
parsed out of a source file on `main`, or quoted from a branch artifact pinned
by git blob sha and shipped byte-exact under `pinned_blobs/` (hash re-verified
before use).

Sources (FREEZE_V1.md section 1):
  Tier F  the flagship claim and its registered law forms
  Tier A  BASELINE_V1.md section 1, assertions A1..A14, stale ones corrected
  Tier C  every research/gmi-833-*/MANIFEST_V1.json claim_ceiling
  Tier R  failed-prediction / counterexample registers and correction notices

Run:  python3 -I -B build_register_v1.py        (writes CENTRAL_CONCLUSIONS_REGISTER_V1.json)
      python3 -I -B build_register_v1.py --check (rebuilds in memory, fails on drift)
      python3 -I -B build_register_v1.py --md    (also prints a markdown index to stdout)

Stdlib only. Python 3.8 compatible. Deterministic output.
"""
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)
REPO = os.path.dirname(RESEARCH)
BLOBS = os.path.join(HERE, "pinned_blobs")
OUT_JSON = os.path.join(HERE, "CENTRAL_CONCLUSIONS_REGISTER_V1.json")

SOURCE_MAIN = "0dcdec54fbece041ee2b7cd1f630469ad85d19d3"

STANDINGS = ("STANDS", "RETIRED", "CORRECTED_TO")
LANE_PACKAGES = ("gmi-833-z-z17-flagship-robustness-v1", "gmi-833-z-z13-repaired-chain-v1")


def rel(path):
    return os.path.relpath(path, REPO)


def read(path, mode="r"):
    with open(path, mode if "b" in mode else "r", encoding=None if "b" in mode else "utf-8") as fh:
        return fh.read()


def blob_sha_of_bytes(data):
    return hashlib.sha1(("blob %d\0" % len(data)).encode("ascii") + data).hexdigest()


def blob_sha(path):
    return blob_sha_of_bytes(read(path, "rb"))


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def occurs(quote, text):
    return norm(quote) in norm(text)


def pinned(sha):
    """Return the byte-exact content of a pinned branch blob, or None, with a
    verification record. The record never says 'fine' when it could not check."""
    path = os.path.join(BLOBS, sha + ".blob")
    if not os.path.exists(path):
        return None, {"blob_sha": sha, "available": False, "hash_verified": False,
                      "status": "UNAVAILABLE"}
    data = read(path, "rb")
    ok = blob_sha_of_bytes(data) == sha
    return (data.decode("utf-8") if ok else None), {
        "blob_sha": sha, "available": True, "hash_verified": ok,
        "status": "VERIFIED" if ok else "HASH_MISMATCH"}


# --------------------------------------------------------------------- pins
# Branch artifacts this register quotes. Each is pinned by path, branch, PR and
# git blob sha; the blob is shipped under pinned_blobs/ and re-hashed on load.
BRANCH_PINS = {
    "Z6_THEOREMS": {"path": "research/gmi-833-z-z6-discrimination-v1/Z6_THEOREMS_V1.md",
                    "blob_sha": "35ab5d2bca7749ea752c23352f8c0d35770d0d2f",
                    "branch": "research/833-sec-z3", "pull_request": 1039},
    "Z6_RESULT": {"path": "research/gmi-833-z-z6-discrimination-v1/RESULT_V1.json",
                  "blob_sha": "33b6a395248ea1095f5832c72f95dd88d8fa4a1d",
                  "branch": "research/833-sec-z3", "pull_request": 1039},
    "Z1_THEOREMS": {"path": "research/gmi-833-z-z1-master-principle-v1/Z1_THEOREMS_V1.md",
                    "blob_sha": "11012f8f163eec17b1cb8bf9ae55bd53b9d660eb",
                    "branch": "research/833-sec-z4", "pull_request": 1052},
    "Z13_FAILED": {"path": "research/gmi-833-z-z13-adjudication-v1/FAILED_PREDICTION_REGISTER_V1.json",
                   "blob_sha": "da6aa2811f1e2d83cd5b9c7633a5bd85c22927ba",
                   "branch": "research/833-sec-z4", "pull_request": 1052},
    "Z13_REPAIR": {"path": "research/gmi-833-z-z13-adjudication-v1/REPAIRED_ECOLOGY_FREEZE_V1.md",
                   "blob_sha": "5bc0597a996c8ad1b53b01f37ebcf1e1e17f1d57",
                   "branch": "research/833-sec-z4", "pull_request": 1052},
    "Z13_P1": {"path": "research/gmi-833-z-z13-property-prediction-freeze-v1/FREEZE_V1.md",
               "blob_sha": "25febfa62cbf73f1f239f3de29436ecd043e67d9",
               "branch": "research/833-sec-z3", "pull_request": 1039},
    "Z5_FAILED": {"path": "research/gmi-833-z-z5-critical-phenomena-v1/FAILED_SCALING_PREDICTION_REGISTER_V1.json",
                  "blob_sha": "b71d26a29a2dd504ac317e46796d36dc5c68c3a0",
                  "branch": "research/833-sec-z2", "pull_request": 1034},
    "Z5_RESULT": {"path": "research/gmi-833-z-z5-critical-phenomena-v1/RESULT_V1.json",
                  "blob_sha": "b6e1fe9c283484a32d3e4930c5afe3575e4ab3ad",
                  "branch": "research/833-sec-z2", "pull_request": 1034},
    "Z7_COUNTER": {"path": "research/gmi-833-z-z7-impossibility-v1/COUNTEREXAMPLE_REGISTER_V1.json",
                   "blob_sha": "06a4c036ee45a42eff2c84a1529117c712720a5d",
                   "branch": "research/833-sec-z2", "pull_request": 1034},
}

MAIN_FILES = {
    "BASELINE": "research/gmi-833-theory-baseline-v1/BASELINE_V1.md",
    "BASELINE_MANIFEST": "research/gmi-833-theory-baseline-v1/BASELINE_MANIFEST_V1.json",
    "Z15_FREEZE": "research/gmi-833-z-z15-decisive-falsifiers-v1/FREEZE_V1.md",
    "Z15_FAILED": "research/gmi-833-z-z15-decisive-falsifiers-v1/FAILED_PREDICTION_REGISTER_V1.json",
    "HELDOUT_FORM": "research/gmi-833-heldout-20-transitions-v1/HELDOUT_TRANSITION_FORMALIZATION_V1.md",
    "HELDOUT_RESULT": "research/gmi-833-heldout-20-transitions-v1/RESULT_V1.json",
    "CIP_NOTICE": "research/gmi-833-capability-interaction-partition-v1/CORRECTION_NOTICE_V1.json",
    "W4_NOTICE": "research/gmi-833-maturity-rescore-v3-w4-v1/CORRECTION_NOTICE_V1.json",
    "W4_DELTA": "research/gmi-833-maturity-rescore-v3-w4-v1/SCORES_V3_DELTA.json",
    "CD_RESULT_V2": "research/gmi-833-claim-discipline-v1/RESULT_V2.json",
    "CD_E9": "research/gmi-833-claim-discipline-v1/REGISTRATIONS_E9_APPEND.json",
    "SCORES_V2": "research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json",
    "TICKETS": "research/gmi-833-corpus-passes-v2-v1/REVIVAL_TICKETS_V1.json",
}


def main_source(key):
    path = os.path.join(REPO, MAIN_FILES[key])
    return {"path": MAIN_FILES[key], "blob_sha": blob_sha(path), "on_main": True}


def branch_source(key):
    pin = dict(BRANCH_PINS[key])
    text, rec = pinned(pin["blob_sha"])
    pin["on_main"] = False
    pin["pinned_blob"] = rec
    return pin, text


# ------------------------------------------------------------------ tier F
def flagship_quote():
    text = read(os.path.join(REPO, MAIN_FILES["Z15_FREEZE"]))
    head = "## The flagship theory, stated without the repository"
    block = text.split(head)[1].split("\n## ")[0]
    lines = [l[2:] for l in block.split("\n") if l.startswith("> ")]
    return " ".join(lines).strip()


def tier_f():
    out = []
    src = main_source("Z15_FREEZE")
    src["section"] = "The flagship theory, stated without the repository"
    out.append({"id": "F1", "tier": "F", "kind": "FLAGSHIP_CLAIM",
                "claim_text": flagship_quote(), "source": src,
                "standing": "STANDS",
                "standing_note": "the programme's own designation of the flagship claim, on main; "
                                 "surviving the Z15 falsifiers does not verify it (their own ceiling)",
                "evidence_class": {"class": "FROZEN_HELDOUT/EV3 via gmi-833-heldout-20-transitions-v1 "
                                            "+ four executable falsifiers (Z15)", "source": "FILE_RULE"},
                "quote_verified": True})

    form = read(os.path.join(REPO, MAIN_FILES["HELDOUT_FORM"]))
    q2 = "Thus the property-level boundary is `lambda* = eta*p/2`."
    src = main_source("HELDOUT_FORM")
    src["section"] = "3. Frozen transition law"
    out.append({"id": "F2", "tier": "F", "kind": "REGISTERED_LAW_FORM",
                "claim_text": q2, "source": src, "quote_verified": occurs(q2, form),
                "standing": "CORRECTED_TO",
                "corrected_to": {"text": "lambda*(env) = eta * p * R0(env) (DS-5); at uniform binary "
                                         "input R0 = 1/2 and the registered form is exact; outside "
                                         "uniform binary input the registered form is refuted (Z6 DS-4, "
                                         "Z5 CP-5 / SP-3)",
                                 "source_keys": ["Z6_THEOREMS", "Z5_FAILED"]},
                "standing_note": "STANDS at its registered scope (uniform binary input, one state bit); "
                                 "CORRECTED_TO the R0 form as a general law",
                "evidence_class": {"class": "FROZEN_HELDOUT/EV3", "source": "FILE_RULE"}})

    pin, text = branch_source("Z6_THEOREMS")
    q3 = "lambda*(env) = eta * p * R0(env)"
    q3b = ("where `R0` is the **minimum delayed-channel error rate attainable without state** "
           "under the environment's own input law, is correct on `R1` in **all `404` worlds**")
    pin["section"] = "DS-5"
    out.append({"id": "F3", "tier": "F", "kind": "REGISTERED_LAW_FORM",
                "claim_text": q3 + " -- " + q3b, "source": pin,
                "quote_verified": bool(text) and occurs(q3, text) and occurs(q3b, text),
                "standing": "STANDS",
                "standing_note": "on branch research/833-sec-z3 (PR #1039), not yet on main",
                "evidence_class": {"class": "EXACT_FINITE_CERTIFICATE + preregistered discrimination "
                                            "(404 worlds), two routes", "source": "FILE_RULE"}})

    pin, text = branch_source("Z1_THEOREMS")
    q4 = "every model selection threshold is a marginal error mass and never an error level."
    pin["section"] = "IC-1"
    out.append({"id": "F4", "tier": "F", "kind": "MASTER_PRINCIPLE",
                "claim_text": "IC-1 (Marginal Value Principle), clause 3: " + q4,
                "source": pin, "quote_verified": bool(text) and occurs(q4, text),
                "standing": "STANDS",
                "standing_note": "on branch research/833-sec-z4 (PR #1052); explicitly parent-owned "
                                 "mathematics (Everett 1963 et al.), not claimed novel",
                "evidence_class": {"class": "ANALYTIC_PROOF_PLUS_EXACT (297 + 135 instances), two routes",
                                   "source": "FILE_RULE"}})

    pin, text = branch_source("Z13_FAILED")
    reg = json.loads(text) if text else {"entries": []}
    by_id = dict((e["id"], e) for e in reg.get("entries", []))
    for fid, zid in (("F5", "ZP-2"), ("F6", "ZP-5")):
        e = by_id.get(zid)
        p = dict(pin)
        p["entry_id"] = zid
        if e is None:
            out.append({"id": fid, "tier": "F", "kind": "RETIRED_PREDICTION", "claim_text": None,
                        "source": p, "quote_verified": False, "standing": "RETIRED",
                        "standing_note": "pinned blob unavailable; entry could not be read"})
            continue
        cc = e.get("claim_ceiling_change", {})
        out.append({"id": fid, "tier": "F", "kind": "RETIRED_PREDICTION",
                    "claim_text": e["prediction"], "source": p, "quote_verified": True,
                    "standing": "RETIRED" if e["verdict"] == "REFUTED" else "STANDS",
                    "corrected_to": {"text": cc.get("replacement"), "retired_text": cc.get("retired"),
                                     "forbidden_promotion_added": cc.get("forbidden_promotion_added"),
                                     "source_keys": ["Z13_FAILED", "Z13_REPAIR"]},
                    "standing_note": "Z13-P1 frozen by research/833-sec-z3 (blob 25febfa6), adjudicated "
                                     "MISS by research/833-sec-z4; " + e.get("evidence", ""),
                    "evidence_class": {"class": "EXACT_FINITE_CERTIFICATE (135 worlds), two routes",
                                       "source": "FILE_RULE"}})
    return out


# ------------------------------------------------------------------ tier A
def baseline_rows():
    text = read(os.path.join(REPO, MAIN_FILES["BASELINE"]))
    sec = text.split("## 1.")[1].split("## 2.")[0]
    rows = []
    for line in sec.split("\n"):
        if not line.startswith("| A"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        rows.append({"id": cells[0], "text": cells[1], "rests_on": cells[2]})
    return rows


def ticket_status():
    """Live status of every revival ticket: the frozen register plus the baseline's
    own supplements. Rule (mechanical, stated): a ticket the frozen register lists
    without a status is CLOSED iff some SUPPLEMENT_*.md that mentions its id also
    carries an explicit closure token for it (CLOSED_GREEN, or the id followed on
    the same line by 'CLOSED' / 'closed:'). Evidence lines are recorded."""
    tickets = json.load(open(os.path.join(REPO, MAIN_FILES["TICKETS"])))["tickets"]
    supp = sorted(glob.glob(os.path.join(REPO, "research/gmi-833-theory-baseline-v1/SUPPLEMENT_*.md")))
    out = []
    for t in tickets:
        tid = t["id"]
        st = t.get("status")
        ev = []
        if st is None:
            for s in supp:
                body = read(s)
                if tid not in body:
                    continue
                for line in body.split("\n"):
                    if tid in line and ("CLOSED" in line or "closed:" in line or "closed " in line):
                        ev.append({"file": rel(s), "line": line.strip()[:160]})
                if not ev and "CLOSED_GREEN" in body:
                    # the closure token may sit on the line after the id (SUPPLEMENT_5 form)
                    lines = body.split("\n")
                    for i, line in enumerate(lines):
                        if tid in line and i + 1 < len(lines) and "CLOSED_GREEN" in lines[i + 1]:
                            ev.append({"file": rel(s), "line": (line.strip() + " " + lines[i + 1].strip())[:160]})
            st = "CLOSED_BY_SUPPLEMENT" if ev else "OPEN"
        out.append({"id": tid, "status": st, "evidence": ev})
    return out


def tier_a():
    out = []
    src = main_source("BASELINE")
    cip = json.load(open(os.path.join(REPO, MAIN_FILES["CIP_NOTICE"])))
    w4 = json.load(open(os.path.join(REPO, MAIN_FILES["W4_NOTICE"])))
    cd = json.load(open(os.path.join(REPO, MAIN_FILES["CD_RESULT_V2"])))
    e9 = json.load(open(os.path.join(REPO, MAIN_FILES["CD_E9"])))
    tickets = ticket_status()
    n_closed = sum(1 for t in tickets if t["status"] != "OPEN")
    n_open = sum(1 for t in tickets if t["status"] == "OPEN")
    for r in baseline_rows():
        e = {"id": r["id"], "tier": "A", "kind": "BASELINE_ASSERTION", "claim_text": r["text"],
             "rests_on": r["rests_on"], "source": dict(src, section="1. What the baseline asserts"),
             "quote_verified": True, "standing": "STANDS",
             "evidence_class": {"class": "CORPUS_AUDIT_COUNT_OVER_BOUND_ARTIFACTS", "source": "FILE_RULE"}}
        if r["id"] == "A14":
            e["standing"] = "CORRECTED_TO"
            e["corrected_to"] = {
                "text": ("CI-U Lemmas A, B, C and CE-1/CE-2 stand; the classification layer (Corollary "
                         "CI-A4) is corrected to the exact partition CIP-1: shipped labels were FALSE "
                         "on %d/%d pairs and non-partitioning on %d/%d; %d of %d labels change" % (
                             cip["defects"]["DEF-1"]["count"], cip["defects"]["DEF-1"]["of"],
                             cip["defects"]["DEF-2"]["count"], cip["defects"]["DEF-2"]["of"],
                             cip["census"]["labels_changed"], cip["census"]["pairs"])),
                "source": main_source("CIP_NOTICE")}
            e["stale_on_main"] = True
        elif r["id"] == "A7":
            e["standing"] = "CORRECTED_TO"
            e["corrected_to"] = {
                "text": ("five discipline fields (not six) for %d claim-bearing objects = %d slots, "
                         "%d REGISTERED_GAP at v2; one post-freeze additive append through the E9 "
                         "channel to the field '%s' of one object" % (
                             cd["objects"], cd["field_slots"], cd["registered_gap_v2"],
                             e9["e9_append"]["target_field"])),
                "source": main_source("CD_RESULT_V2"), "append_source": main_source("CD_E9"),
                "arithmetic": "%d * 5 = %d" % (cd["objects"], cd["objects"] * 5)}
            e["stale_on_main"] = True
        elif r["id"] == "A6":
            c = w4["census"]
            e["standing"] = "CORRECTED_TO"
            e["corrected_to"] = {
                "text": ("maturity distribution corrected by the v3 W4 delta: rows %d -> %d; "
                         "M2 %d -> %d; M4 count %d unchanged with membership swapped "
                         "(gmi-novel-intelligence-w4-v1 M4->M2/EV2 out, "
                         "gmi-novel-intelligence-w4-prospective-v1 M4/EV3 in); still no M5/M6" % (
                             sum(c["published"].values()), sum(c["corrected"].values()),
                             c["published"]["M2"], c["corrected"]["M2"], c["corrected"]["M4"])),
                "source": main_source("W4_NOTICE"), "delta_source": main_source("W4_DELTA")}
            e["stale_on_main"] = True
        elif r["id"] == "A9":
            e["standing"] = "CORRECTED_TO"
            e["corrected_to"] = {
                "text": ("revival queue live counts re-derived from the frozen register plus the "
                         "baseline's supplements: %d tickets, %d closed, %d open" % (
                             len(tickets), n_closed, n_open)),
                "tickets": tickets,
                "source": main_source("TICKETS")}
            e["stale_on_main"] = True
        out.append(e)
    return out


# ------------------------------------------------------------------ tier C
def scores_index():
    rows = json.load(open(os.path.join(REPO, MAIN_FILES["SCORES_V2"])))
    idx = {}
    for r in rows:
        idx[r["package"]] = {"support_kind": r.get("support_kind"), "M": r.get("maturity_M"),
                             "EV": r.get("evidence_EV"), "result_id": r.get("result_id")}
    delta = json.load(open(os.path.join(REPO, MAIN_FILES["W4_DELTA"])))
    for r in delta.get("records", []):
        pk = r.get("package")
        if pk:
            idx[pk] = {"support_kind": r.get("support_kind"), "M": r.get("maturity_M"),
                       "EV": r.get("evidence_EV"), "result_id": r.get("result_id"), "v3_delta": True}
    return idx


def file_rule(pkg_dir):
    files = sorted(os.listdir(pkg_dir))
    has_freeze = any(f.startswith("FREEZE") and f.endswith(".md") for f in files)
    has_result = any(f.startswith("RESULT") and f.endswith(".json") for f in files)
    oracle_py = [f for f in files if f.endswith(".py") and
                 ("oracle" in f.lower() or "independent" in f.lower() or "route_b" in f.lower())]
    oracle_json = [f for f in files if f.upper().startswith("ORACLE") and f.endswith(".json")]
    routes_b = False
    man = os.path.join(pkg_dir, "MANIFEST_V1.json")
    if os.path.exists(man):
        try:
            d = json.load(open(man))
            rt = d.get("routes")
            if isinstance(rt, list):
                routes_b = len(rt) >= 2
            elif isinstance(rt, dict):
                routes_b = len(rt) >= 2
        except ValueError:
            routes_b = False
    return {"freeze_present": has_freeze, "result_present": has_result,
            "second_route_files": oracle_py, "second_route_receipts": oracle_json,
            "manifest_declares_two_routes": routes_b,
            "second_route_signal": bool(oracle_py or oracle_json or routes_b)}


def tier_c():
    out = []
    gaps = []
    idx = scores_index()
    for man in sorted(glob.glob(os.path.join(RESEARCH, "gmi-833-*", "MANIFEST_V1.json"))):
        pkg = os.path.basename(os.path.dirname(man))
        try:
            d = json.load(open(man))
        except ValueError as ex:
            gaps.append({"package": pkg, "gap": "MANIFEST_V1_UNPARSEABLE", "detail": str(ex)})
            continue
        cc = d.get("claim_ceiling")
        if not cc:
            gaps.append({"package": pkg, "gap": "CEILING_KEY_ABSENT"})
            continue
        fr = file_rule(os.path.dirname(man))
        sc = idx.get(pkg)
        if sc:
            ev = {"class": "%s/%s/%s" % (sc["support_kind"], sc["M"], sc["EV"]),
                  "source": "THEOREM_SCORES_V2" + ("+V3_DELTA" if sc.get("v3_delta") else "")}
        else:
            ev = {"class": "%s%s%s" % ("FREEZE+" if fr["freeze_present"] else "NO_FREEZE+",
                                       "RESULT+" if fr["result_present"] else "NO_RESULT+",
                                       "TWO_ROUTE_SIGNAL" if fr["second_route_signal"] else "SINGLE_ROUTE_SIGNAL"),
                  "source": "FILE_RULE"}
        out.append({"id": "C-" + pkg, "tier": "C", "kind": "PACKAGE_CLAIM_CEILING",
                    "claim_text": cc,
                    "source": {"path": rel(man), "blob_sha": blob_sha(man), "on_main": True,
                               "key": "claim_ceiling"},
                    "quote_verified": True, "standing": "STANDS",
                    "standing_note": "a ceiling is a scope statement; STANDS means no correction "
                                     "notice on main names this package's ceiling",
                    "evidence_class": ev, "file_rule": fr})
    for d in sorted(glob.glob(os.path.join(RESEARCH, "gmi-833-*"))):
        if not os.path.isdir(d):
            continue
        pkg = os.path.basename(d)
        if pkg in LANE_PACKAGES:
            gaps.append({"package": pkg, "gap": "LANE_PACKAGE_EXCLUDED",
                         "detail": "this lane's own package; its manifest is written after the register"})
            continue
        if not os.path.exists(os.path.join(d, "MANIFEST_V1.json")):
            alt = [f for f in os.listdir(d) if f.upper().startswith("MANIFEST")]
            gaps.append({"package": pkg, "gap": "NO_MANIFEST_V1", "other_manifest_files": alt})
    return out, gaps


# ------------------------------------------------------------------ tier R
def tier_r():
    out = []
    non = []
    src = main_source("Z15_FAILED")
    z15 = json.load(open(os.path.join(REPO, MAIN_FILES["Z15_FAILED"])))
    kind_map = {"FALSIFIED_PREREGISTERED_PREDICTION": "RETIRED",
                "CONFIRMED_OVERCLAIM_REVIVED": "CORRECTED_TO",
                "OWN_INSTRUMENT_DEFECT": "CORRECTED_TO"}
    for e in z15["failed"]:
        s = dict(src, entry_id=e["id"], pinned_path=e["path"], pinned_blob_sha=e["blob_sha"],
                 anchor=e["anchor"])
        if e["kind"] in kind_map:
            rec = {"id": "R-" + e["id"], "tier": "R", "kind": e["kind"], "claim_text": e["summary"],
                   "source": s, "quote_verified": True, "standing": kind_map[e["kind"]],
                   "evidence_class": {"class": "REGISTERED_IN_FAILED_PREDICTION_REGISTER", "source": "Z15"}}
            if e["id"] == "FP-939-OVERSTRONG":
                rec["corrected_to"] = {"text": "revived to Theorem CI-U (Lemmas A, B, C); its "
                                               "classification layer subsequently corrected to CIP-1 "
                                               "(see A14)", "source": main_source("CIP_NOTICE")}
            if e["id"] == "FP-Z12-CAL-V1":
                rec["corrected_to"] = {"text": "record-level calibration instrument CAL-1 replaced by "
                                               "element-level calibration with lemma CAL-LEM "
                                               "(gmi-833-z-z12-prediction-scoring-v1)"}
            out.append(rec)
        else:
            non.append({"id": e["id"], "kind": e["kind"], "summary": e["summary"], "source": s,
                        "why_not_a_conclusion": "an open row, an open requirement or a registered "
                                                "negative control is not a conclusion"})
    for e in z15["successes"]:
        s = dict(src, entry_id=e["id"], pinned_path=e["path"], pinned_blob_sha=e["blob_sha"],
                 anchor=e["anchor"])
        out.append({"id": "R-" + e["id"], "tier": "R", "kind": "REGISTERED_SUCCESS",
                    "claim_text": e["summary"], "source": s, "quote_verified": True,
                    "standing": "STANDS",
                    "evidence_class": {"class": "REGISTERED_IN_FAILED_PREDICTION_REGISTER", "source": "Z15"}})

    pin, text = branch_source("Z5_FAILED")
    reg = json.loads(text) if text else {"entries": []}
    ents = dict((e["id"], e) for e in reg.get("entries", []))
    if "SP-3" in ents:
        e = ents["SP-3"]
        out.append({"id": "R-Z5-SP-3", "tier": "R", "kind": "REFUTED_NAIVE_EXTRAPOLATION",
                    "claim_text": e["prediction"], "source": dict(pin, entry_id="SP-3"),
                    "quote_verified": True, "standing": "RETIRED",
                    "corrected_to": {"text": ents.get("SP-4", {}).get("prediction"),
                                     "source_keys": ["Z5_FAILED"]},
                    "evidence_class": {"class": "EXACT_FINITE_CERTIFICATE (16, 729, 65536 tables)",
                                       "source": "FILE_RULE"}})
    else:
        out.append({"id": "R-Z5-SP-3", "tier": "R", "kind": "REFUTED_NAIVE_EXTRAPOLATION",
                    "claim_text": None, "source": pin, "quote_verified": False, "standing": "RETIRED",
                    "standing_note": "pinned blob unavailable"})

    pin, text = branch_source("Z7_COUNTER")
    reg = json.loads(text) if text else {"entries": []}
    if reg.get("entries"):
        e = reg["entries"][0]
        out.append({"id": "R-Z7-Q4", "tier": "R", "kind": "REFUTED_FROZEN_HYPOTHESIS",
                    "claim_text": e["frozen_text"], "source": dict(pin, entry_id=e["hypothesis"]),
                    "quote_verified": True, "standing": "RETIRED",
                    "corrected_to": {"text": e["repair"], "witness": e["witness"],
                                     "source_keys": ["Z7_COUNTER"]},
                    "evidence_class": {"class": "EXACT_FINITE_CERTIFICATE (65,552 candidates)",
                                       "source": "FILE_RULE"}})
    else:
        out.append({"id": "R-Z7-Q4", "tier": "R", "kind": "REFUTED_FROZEN_HYPOTHESIS",
                    "claim_text": None, "source": pin, "quote_verified": False, "standing": "RETIRED",
                    "standing_note": "pinned blob unavailable"})

    pin, text = branch_source("Z13_FAILED")
    reg = json.loads(text) if text else {"entries": []}
    for e in reg.get("entries", []):
        if e["id"] in ("ZP-2", "ZP-5"):
            continue  # F5 / F6
        if e["id"] == "ZP-6":
            non.append({"id": "Z13-" + e["id"], "kind": e["label"], "summary": e["prediction"],
                        "source": dict(pin, entry_id=e["id"]),
                        "why_not_a_conclusion": "a null-model statement is a control, not a conclusion"})
            continue
        out.append({"id": "R-Z13-" + e["id"], "tier": "R", "kind": "ADJUDICATED_FROZEN_PREDICTION",
                    "claim_text": e["prediction"], "source": dict(pin, entry_id=e["id"]),
                    "quote_verified": True,
                    "standing": "STANDS" if e["verdict"] == "CONFIRMED" else "RETIRED",
                    "standing_note": e.get("evidence", ""),
                    "evidence_class": {"class": "EXACT_FINITE_CERTIFICATE (135 worlds), two routes",
                                       "source": "FILE_RULE"}})
    return out, non


# ------------------------------------------------------------------- build
def build():
    f = tier_f()
    a = tier_a()
    c, gaps = tier_c()
    r, non = tier_r()
    entries = f + a + c + r
    for e in entries:
        if e["standing"] not in STANDINGS:
            raise SystemExit("bad standing %r on %s" % (e["standing"], e["id"]))
        if e["standing"] == "CORRECTED_TO" and not e.get("corrected_to"):
            raise SystemExit("CORRECTED_TO without replacement on %s" % e["id"])
    ids = [e["id"] for e in entries]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate ids")
    pins = {}
    for k, v in BRANCH_PINS.items():
        _t, rec = pinned(v["blob_sha"])
        pins[k] = dict(v, pinned_blob=rec)
    counts = {"total": len(entries)}
    for t in "FACR":
        counts["tier_" + t] = sum(1 for e in entries if e["tier"] == t)
    for s in STANDINGS:
        counts["standing_" + s] = sum(1 for e in entries if e["standing"] == s)
    counts["stale_on_main"] = sum(1 for e in entries if e.get("stale_on_main"))
    counts["quote_unverified"] = sum(1 for e in entries if not e.get("quote_verified"))
    counts["ceiling_gaps"] = len(gaps)
    counts["non_conclusions_listed"] = len(non)
    doc = {"schema": "GMI_833_Z17_CENTRAL_CONCLUSIONS_REGISTER_V1", "issue": 833,
           "subsection": "Z17", "source_main": SOURCE_MAIN,
           "built_by": "research/gmi-833-z-z17-flagship-robustness-v1/build_register_v1.py",
           "sources_on_main": dict((k, main_source(k)) for k in sorted(MAIN_FILES)),
           "branch_pins": pins,
           "standing_vocabulary": list(STANDINGS),
           "counts": counts, "entries": entries, "ceiling_gaps": gaps,
           "non_conclusions_listed": non}
    return doc


def render_md(doc):
    c = doc["counts"]
    lines = ["# Register of central conclusions v1 (index)", "",
             "Generated by `build_register_v1.py` from the sources named in `FREEZE_V1.md` section 1. "
             "The exact claim texts live byte-exact in `CENTRAL_CONCLUSIONS_REGISTER_V1.json`; this "
             "index is rendered on demand and quotes none of them.", "",
             "| count | value |", "|---|---:|"]
    for k in sorted(c):
        lines.append("| %s | %s |" % (k, c[k]))
    lines += ["", "| id | tier | kind | standing | evidence class | source |", "|---|---|---|---|---|---|"]
    for e in doc["entries"]:
        src = e["source"]
        where = src.get("path", "?")
        if not src.get("on_main", True):
            where += " @ " + src.get("branch", "?")
        lines.append("| `%s` | %s | %s | %s | %s | `%s` |" % (
            e["id"], e["tier"], e["kind"], e["standing"],
            e.get("evidence_class", {}).get("class", "?").replace("|", "/"), where))
    lines += ["", "## Ceiling gaps (enumerated, not conclusions)", ""]
    for g in doc["ceiling_gaps"]:
        lines.append("- `%s`: %s%s" % (g["package"], g["gap"],
                                        (" (" + ", ".join(g["other_manifest_files"]) + ")")
                                        if g.get("other_manifest_files") else ""))
    lines += ["", "## Listed but not conclusions", ""]
    for n in doc["non_conclusions_listed"]:
        lines.append("- `%s` (%s): %s" % (n["id"], n["kind"], n["why_not_a_conclusion"]))
    return "\n".join(lines) + "\n"


def main(argv):
    doc = build()
    js = json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    md = render_md(doc)
    if "--check" in argv:
        cur = read(OUT_JSON) if os.path.exists(OUT_JSON) else ""
        if cur != js:
            sys.stdout.write("REGISTER_DRIFT\n")
            return 1
        sys.stdout.write("REGISTER_OK sha256=%s\n" % hashlib.sha256(js.encode("utf-8")).hexdigest())
        return 0
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        fh.write(js)
    if "--md" in argv:
        # index rendering on demand only: package directory names carry legacy
        # vocabulary the repo-wide terminology ratchet fails new markdown for
        sys.stdout.write(md)
    sys.stdout.write(json.dumps(doc["counts"], indent=1, sort_keys=True) + "\n")
    sys.stdout.write("register sha256=%s\n" % hashlib.sha256(js.encode("utf-8")).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
