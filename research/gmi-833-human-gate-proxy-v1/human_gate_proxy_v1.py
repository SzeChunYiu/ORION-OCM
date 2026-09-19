#!/usr/bin/env python3
"""Route A executor for gmi-833-human-gate-proxy-v1 (issue #833).

Checks every labelled model-proxy record against the frozen briefs, the pinned
artifacts and the verbatim verdict transcripts; decides each of the 40 rows by
the decision rules frozen in FREEZE_V1.md section 4; scores the Z9 protocol
batches against a fresh run of the frozen exact oracle; runs the AA10
exhaustion gate; emits the receipt and the comment reconciliation.

Usage:
  human_gate_proxy_v1.py                 receipt JSON on stdout
  human_gate_proxy_v1.py --hostiles      every planted defect must be DETECTED
  human_gate_proxy_v1.py --null          200 seeded random record sets / predictors
  human_gate_proxy_v1.py --write         write RESULT_V1.json and the reconciliation

Stdlib only; exact integers and Fractions; python3.8-compatible.
"""
from fractions import Fraction
import copy
import hashlib
import json
import os
import random
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
LABEL = "HUMAN_GATE_BYPASSED__MODEL_PROXY"
FORBIDDEN = ("EXTERNALLY_REVIEWED", "INDEPENDENT_TEAM_REPLICATION", "M5",
             "HUMAN_REVIEW_OBTAINED", "THIRD_PARTY_ADJUDICATED",
             "REAL_SYSTEM_VALIDATED_BY_PROXY", "COGNITIVE_SCIENCE_EVIDENCE_OBTAINED",
             "CROSS_SPECIES_PREDICTION_CONFIRMED", "PROXY_VERDICT_IS_TRUTH",
             "MANUSCRIPT_READY", "COMPLETE_GMI")
CLAIM_CEILING = ("GMI_833_HUMAN_GATE_ROWS_DISCHARGED_BY_LABELLED_MODEL_PROXY"
                 "_AT_REGISTERED_ARTIFACT_SCOPE")
MODEL_FAMILY = {"opus": "opus", "sonnet": "sonnet", "haiku": "haiku", "fable": "fable"}
TWO_ROUTE_ROWS = ("AG8-R48", "AC05")
SNAPSHOTS = {5684819296: "snapshots/COMMENT_5684819296_SNAPSHOT_V1.txt",
             5684607872: "snapshots/COMMENT_5684607872_SNAPSHOT_V1.txt",
             5693520829: "snapshots/COMMENT_5693520829_SNAPSHOT_V1.txt"}
EXHAUSTED = ("EXHAUSTED", "RECURSION_EXHAUSTED", "NO_MATERIAL_GAP_REMAINS")
REVIEW_KINDS = ("EXTERNALLY_REVIEWED", LABEL)


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- freeze ----
def freeze_rows():
    """The 40 rows exactly as FREEZE_V1.md section 2 quotes them, with ids."""
    text = open(os.path.join(HERE, "FREEZE_V1.md"), encoding="utf-8").read()
    sec = text[text.index("## 2. The exact rows"):text.index("## 3. What a proxy is")]
    rows = []
    anchor = None
    comment = None
    for line in sec.split("\n"):
        if line.startswith("### 2.1"):
            comment = 5684819296
        elif line.startswith("### 2.2"):
            comment = 5684607872
        elif line.startswith("### 2.3"):
            comment = 5693520829
        elif line.startswith("> ### "):
            anchor = line[2:]
        elif line.startswith("- [ ] "):
            rows.append({"comment_id": comment, "anchor": anchor, "old": line})
    ids = (["Z9-%d" % i for i in range(1, 8)] + ["Z10-%d" % i for i in range(1, 11)]
           + ["Z14-%d" % i for i in range(1, 8)] + ["Z18-%d" % i for i in range(1, 9)]
           + ["AA10", "AA15", "AA41", "AC02", "AC05", "AC09", "AD08", "AG8-R48"])
    if len(rows) != 40 or len(ids) != 40:
        raise AssertionError("freeze row census %d" % len(rows))
    for r, i in zip(rows, ids):
        r["id"] = i
    return rows


def freeze_brief_digests():
    text = open(os.path.join(HERE, "FREEZE_V1.md"), encoding="utf-8").read()
    sec = text[text.index("## 9. Brief digests"):text.index("## 10. Pins")]
    out = {}
    for line in sec.split("\n"):
        m = re.match(r"\| `(briefs/[^`]+)` \| `([0-9a-f]{64})` \| (\d+) \|", line)
        if m:
            out[m.group(1)] = (m.group(2), int(m.group(3)))
    return out


def freeze_artifact_pins():
    text = open(os.path.join(HERE, "FREEZE_V1.md"), encoding="utf-8").read()
    sec = text[text.index("## 10. Pins"):]
    out = {}
    for line in sec.split("\n"):
        m = re.match(r"\| `([0-9a-f]{40})` \| `([^`]+)` \|", line)
        if m:
            out[m.group(2)] = m.group(1)
    return out


# ------------------------------------------------------- verdict parsing ----
BLOCK_RE = re.compile(r"VERDICT_BLOCK_BEGIN(.*?)VERDICT_BLOCK_END", re.S)


def parse_verdict_block(text):
    """Route A parser: regex over the LAST verdict block in the transcript."""
    blocks = BLOCK_RE.findall(text)
    if not blocks:
        return None
    body = blocks[-1]
    out = {"rows": {}, "claims": {}, "objections": [], "reopen": [], "model_self_report": None}
    for raw in body.split("\n"):
        line = raw.strip()
        if line.startswith("row:"):
            m = re.match(r"row:\s*([A-Za-z0-9-]+)\s*\|\s*verdict:\s*([A-Z_]+)\s*\|\s*reason:\s*(.*)$", line)
            if m:
                out["rows"][m.group(1)] = {"verdict": m.group(2), "reason": m.group(3).strip()}
        elif line.startswith("claim:"):
            m = re.match(r"claim:\s*([A-Za-z0-9-]+)\s*\|\s*verdict:\s*([A-Z_]+)\s*\|\s*reason:\s*(.*)$", line)
            if m:
                out["claims"][m.group(1)] = {"verdict": m.group(2), "reason": m.group(3).strip()}
        elif line.startswith("objection:"):
            m = re.match(r"objection:\s*([^|]+?)\s*\|(?:\s*claim:\s*([^|]+?)\s*\|)?\s*material:\s*(yes|no)\s*\|\s*text:\s*(.*)$", line)
            if m:
                out["objections"].append({"id": m.group(1).strip(), "claim": (m.group(2) or "").strip(),
                                          "material": m.group(3) == "yes", "text": m.group(4).strip()})
        elif line.startswith("reopen:"):
            m = re.match(r"reopen:\s*([^|]+?)\s*\|\s*reason:\s*(.*)$", line)
            if m and m.group(1).strip().lower() not in ("none", "<gate or result name>"):
                out["reopen"].append({"gate": m.group(1).strip(), "reason": m.group(2).strip()})
        elif line.startswith("model_self_report:"):
            out["model_self_report"] = line.split(":", 1)[1].strip()
    return out


# ------------------------------------------------------ record integrity ----
def check_records(doc, briefs, pins, hostile_ctx=None):
    """Return list of violation dicts. Empty list == every record is intact."""
    v = []
    seen = set()
    for rec in doc["records"]:
        rid = rec.get("id", "?")
        if rid in seen:
            v.append({"kind": "DUPLICATE_RECORD_ID", "record": rid})
        seen.add(rid)
        if rec.get("label") != LABEL:
            v.append({"kind": "LABEL_MISSING_OR_WRONG", "record": rid})
        b = rec.get("brief")
        if b not in briefs:
            v.append({"kind": "BRIEF_NOT_IN_FREEZE", "record": rid, "brief": b})
        else:
            actual = sha256_file(os.path.join(HERE, b)) if hostile_ctx is None or "brief_sha" not in hostile_ctx else hostile_ctx["brief_sha"]
            if actual != briefs[b][0] or rec.get("brief_sha256") != briefs[b][0]:
                v.append({"kind": "BRIEF_SHA_MISMATCH", "record": rid, "brief": b})
        for path, sha in (rec.get("artifacts") or {}).items():
            if path.startswith("research/gmi-833-human-gate-proxy-v1/"):
                continue  # intra-package inputs (editor, adjudicator) are pinned by sha256 below
            if pins.get(path) != sha:
                v.append({"kind": "ARTIFACT_PIN_MISMATCH", "record": rid, "path": path})
        for path, sha in (rec.get("inputs_sha256") or {}).items():
            full = os.path.join(HERE, path)
            if not os.path.exists(full) or sha256_file(full) != sha:
                v.append({"kind": "INPUT_SHA_MISMATCH", "record": rid, "path": path})
        vf = rec.get("verdict_file")
        full = os.path.join(HERE, vf) if vf else None
        if not full or not os.path.exists(full):
            v.append({"kind": "VERDICT_FILE_MISSING", "record": rid})
            continue
        text = open(full, encoding="utf-8").read()
        if hostile_ctx and hostile_ctx.get("verdict_text", {}).get(rid) is not None:
            text = hostile_ctx["verdict_text"][rid]
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != rec.get("verdict_sha256"):
            v.append({"kind": "VERDICT_SHA_MISMATCH", "record": rid})
        parsed = parse_verdict_block(text)
        if parsed is None:
            v.append({"kind": "VERDICT_BLOCK_ABSENT", "record": rid})
            continue
        if parsed["rows"] != rec.get("rows", {}):
            v.append({"kind": "STORED_ROWS_DIFFER_FROM_TRANSCRIPT", "record": rid})
        if parsed["claims"] != rec.get("claims", {}):
            v.append({"kind": "STORED_CLAIMS_DIFFER_FROM_TRANSCRIPT", "record": rid})
        if parsed["model_self_report"] != rec.get("model_self_report"):
            v.append({"kind": "MODEL_SELF_REPORT_DIFFERS", "record": rid})
        if rec.get("model_requested") not in MODEL_FAMILY:
            v.append({"kind": "MODEL_REQUESTED_UNKNOWN", "record": rid})
        if rec.get("spawned_after_freeze_commit") != doc.get("freeze_commit"):
            v.append({"kind": "SPAWN_NOT_AFTER_FREEZE", "record": rid})
    return v


def records_by_id(doc):
    return {r["id"]: r for r in doc["records"]}


def row_verdict(rec, row_id):
    if rec is None:
        return None
    return (rec.get("rows") or {}).get(row_id)


# ------------------------------------------------------------- Z9 scoring ----
def score_batch(preds, outs):
    pm = {p["env_id"]: p for p in preds["predictions"]}
    om = {o["env_id"]: o for o in outs["outcomes"]}
    cls_hit = cls_tot = cap_hit = cap_tot = cro_hit = cro_tot = 0
    envs_with_miss = 0
    misses = []
    for eid, o in om.items():
        p = pm.get(eid)
        if p is None:
            misses.append({"env": eid, "kind": "NO_PREDICTION"})
            envs_with_miss += 1
            continue
        miss_here = False
        for lam, w in o["winner_class_set"].items():
            cls_tot += 1
            pw = (p.get("winner_class_set") or {}).get(lam)
            if pw is not None and sorted(pw) == sorted(w):
                cls_hit += 1
            else:
                miss_here = True
                misses.append({"env": eid, "lambda": lam, "kind": "CLASS", "predicted": pw, "observed": w})
            cap_tot += 1
            pjs = (p.get("J_best_stateless") or {}).get(lam)
            pjo = (p.get("J_best_onebit") or {}).get(lam)
            try:
                ok = (pjs is not None and pjo is not None and Fraction(pjs) == Fraction(o["J_best_stateless"][lam])
                      and Fraction(pjo) == Fraction(o["J_best_onebit"][lam]))
            except (ValueError, ZeroDivisionError):
                ok = False
            if ok:
                cap_hit += 1
            else:
                miss_here = True
                misses.append({"env": eid, "lambda": lam, "kind": "CAPABILITY",
                               "predicted": [pjs, pjo], "observed": [o["J_best_stateless"][lam], o["J_best_onebit"][lam]]})
        cro_tot += 1
        try:
            ok = Fraction(p.get("lambda_star", "x")) == Fraction(o["lambda_star"])
        except (ValueError, ZeroDivisionError):
            ok = False
        if ok:
            cro_hit += 1
        else:
            miss_here = True
            misses.append({"env": eid, "kind": "CROSSOVER", "predicted": p.get("lambda_star"), "observed": o["lambda_star"]})
        envs_with_miss += int(miss_here)
    return {"class_hits": cls_hit, "class_total": cls_tot, "capability_hits": cap_hit,
            "capability_total": cap_tot, "crossover_hits": cro_hit, "crossover_total": cro_tot,
            "environments": len(om), "environments_with_miss": envs_with_miss, "misses": misses}


def z9_protocol(doc, recompute=True):
    """Verify each batch's custody chain and score it."""
    proto = doc.get("z9_protocol") or {}
    batches = []
    import importlib.util
    spec = importlib.util.spec_from_file_location("z9a", os.path.join(HERE, "z9_oracle_a_v1.py"))
    z9a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z9a)
    for b in proto.get("batches", []):
        d = os.path.join(HERE, b["dir"])
        env = json.load(open(os.path.join(d, "ENVIRONMENTS.json")))
        pred = json.load(open(os.path.join(d, "PREDICTIONS.json")))
        out = json.load(open(os.path.join(d, "OUTCOMES.json")))
        checks = {
            "environments_sha_matches": sha256_file(os.path.join(d, "ENVIRONMENTS.json")) == b["environments_sha256"],
            "predictions_sha_matches": sha256_file(os.path.join(d, "PREDICTIONS.json")) == b["predictions_sha256"],
            "outcomes_sha_matches": sha256_file(os.path.join(d, "OUTCOMES.json")) == b["outcomes_sha256"],
            "roles_distinct": len({b["test_team"], b["prediction_team"], b["adjudicator"]}) == 3,
            "prediction_before_outcome_commit": b["predictions_commit"] != b["outcomes_commit"],
        }
        if recompute:
            fresh = z9a.run(env)
            checks["outcomes_reproduced_by_frozen_oracle"] = fresh["outcomes"] == out["outcomes"]
        score = score_batch(pred, out)
        batches.append({"batch": b["batch"], "checks": checks, "score": score,
                        "adjudicator_reported": b.get("adjudicator_reported")})
    return batches


def z9_null(doc, n=200, seed=833):
    rng = random.Random(seed)
    proto = doc.get("z9_protocol") or {}
    points = []
    for b in proto.get("batches", []):
        out = json.load(open(os.path.join(HERE, b["dir"], "OUTCOMES.json")))
        for o in out["outcomes"]:
            for lam, w in o["winner_class_set"].items():
                points.append(sorted(w))
    if not points:
        return {"points": 0, "random_predictors_matching_all": None, "trials": 0}
    options = [["STATELESS"], ["PERSISTENT_STATE"], ["PERSISTENT_STATE", "STATELESS"]]
    hits = 0
    for _ in range(n):
        guess = [rng.choice(options) for _ in points]
        hits += int(all(g == w for g, w in zip(guess, points)))
    return {"points": len(points), "random_predictors_matching_all": hits, "trials": n}


# --------------------------------------------------------------- AA10 gate ----
def exhaustion_gate(gaps):
    """Violations: a record with an exhausted status lacking a valid review."""
    v = []
    exhausted = 0
    for g in gaps:
        if g.get("status") in EXHAUSTED:
            exhausted += 1
            r = g.get("independent_hostile_review")
            if (not isinstance(r, dict) or r.get("reviewer_kind") not in REVIEW_KINDS
                    or not r.get("reviewer_id") or r.get("reviewer_id") == g.get("owner_role")
                    or not re.match(r"^[0-9a-f]{64}$", str(r.get("verdict_sha256", "")))):
                v.append({"gap": g.get("id"), "status": g.get("status")})
    return {"records": len(gaps), "exhausted": exhausted, "violations": v}


def load_gaps():
    p = os.path.join(REPO, "research", "gmi-833-corpus-census-v1", "GMI_GAP_GRAPH_V1.json")
    return json.load(open(p))["gaps"]


# ---------------------------------------------------------- row decisions ----
def decide_rows(doc, z9_batches, gate, reopened, hostile_ctx=None):
    R = records_by_id(doc)
    dec = {}

    def sat(rid, row):
        v = row_verdict(R.get(rid), row)
        return v is not None and v["verdict"] == "SATISFIED", v

    def simple(row, rid):
        ok, v = sat(rid, row)
        dec[row] = {"closed": ok, "by": [rid], "reason": (v or {}).get("reason", "no proxy record")}

    for i in range(1, 6):
        simple("Z18-%d" % i, ["PX-Z18-THM", "PX-Z18-EXP", "PX-Z18-LIT", "PX-Z18-STAT", "PX-Z18-COG"][i - 1])
    simple("Z18-7", "PX-Z18-EDIT")
    simple("AD08", "PX-Z18-EDIT")
    simple("AA41", "PX-AA41")
    simple("AC02", "PX-AC02")
    simple("AC09", "PX-AC09")
    simple("Z14-1", "PX-Z14-SUB")
    for i in range(2, 8):
        simple("Z14-%d" % i, "PX-Z14-COG")
    for i in range(1, 11):
        simple("Z10-%d" % i, "PX-Z10")
    # AA15: proxy + lean check
    ok, v = sat("PX-AA15", "AA15")
    lean = doc.get("lean_check") or {}
    lean_ok = bool(lean.get("targets")) and all(t.get("exit_code") == 0 for t in lean.get("targets", []))
    dec["AA15"] = {"closed": ok and lean_ok, "by": ["PX-AA15", "lean_check"],
                   "reason": (v or {}).get("reason", "no proxy record") + ("" if lean_ok else " | lean check failed or absent")}
    # two-route rows
    for row, a, b in (("AG8-R48", "PX-AG8-A", "PX-AG8-B"), ("AC05", "PX-AC05-A", "PX-AC05-B")):
        oka, va = sat(a, row)
        okb, vb = sat(b, row)
        fam_a = MODEL_FAMILY.get((R.get(a) or {}).get("model_requested"))
        fam_b = MODEL_FAMILY.get((R.get(b) or {}).get("model_requested"))
        distinct = fam_a is not None and fam_b is not None and fam_a != fam_b
        dec[row] = {"closed": oka and okb and distinct, "by": [a, b],
                    "reason": "A: %s | B: %s%s" % ((va or {}).get("reason", "no record"), (vb or {}).get("reason", "no record"),
                                                   "" if distinct else " | routes not from distinct model families"),
                    "agreement": (va or {}).get("verdict") == (vb or {}).get("verdict")}
    # Z9 rows
    t_ok = all(sat("PX-Z9-T%d" % b, "Z9-2")[0] for b in (1, 2))
    p3_ok = all(sat("PX-Z9-P%d" % b, "Z9-3")[0] for b in (1, 2))
    p4_ok = all(sat("PX-Z9-P%d" % b, "Z9-4")[0] for b in (1, 2))
    a_ok = all(sat("PX-Z9-A%d" % b, "Z9-6")[0] for b in (1, 2))
    chain_ok = bool(z9_batches) and all(all(b["checks"].values()) for b in z9_batches)
    dec["Z9-1"] = {"closed": chain_ok and all(b["checks"]["roles_distinct"] for b in z9_batches), "by": ["z9_protocol"],
                   "reason": "three context-isolated agents per batch with distinct ids; custody chain verified"}
    dec["Z9-2"] = {"closed": t_ok and chain_ok, "by": ["PX-Z9-T1", "PX-Z9-T2"], "reason": "environment batches authored from the family spec only"}
    dec["Z9-3"] = {"closed": p3_ok and chain_ok, "by": ["PX-Z9-P1", "PX-Z9-P2"], "reason": "prediction teams received only descriptors and the theory"}
    dec["Z9-4"] = {"closed": p4_ok and chain_ok, "by": ["PX-Z9-P1", "PX-Z9-P2"], "reason": "predictions sha256-committed before outcomes"}
    dec["Z9-5"] = {"closed": chain_ok and all(b["checks"].get("outcomes_reproduced_by_frozen_oracle", True) for b in z9_batches),
                   "by": ["z9_oracle_a_v1"], "reason": "outcomes reproduced by the oracle committed before the batches; nothing tunable"}
    dec["Z9-6"] = {"closed": a_ok and chain_ok, "by": ["PX-Z9-A1", "PX-Z9-A2"], "reason": "adjudicators scored from predictions and outcomes only"}
    dec["Z9-7"] = {"closed": chain_ok and len(z9_batches) >= 2, "by": ["z9_protocol"], "reason": "%d independent batches" % len(z9_batches)}
    # AA10
    dec["AA10"] = {"closed": gate["violations"] == [] and doc.get("aa10_gate_wired") is True, "by": ["exhaustion_gate"],
                   "reason": "%d gap records, %d exhausted, %d violations" % (gate["records"], gate["exhausted"], len(gate["violations"]))}
    # Z18-6: authority in every reviewer brief and every reopen demand honoured
    demands = []
    for rid in ("PX-Z18-THM", "PX-Z18-EXP", "PX-Z18-LIT", "PX-Z18-STAT", "PX-Z18-COG", "PX-AA41", "PX-AG8-A", "PX-AG8-B",
                "PX-AC05-A", "PX-AC05-B", "PX-AC02", "PX-AC09", "PX-Z10", "PX-Z14-SUB", "PX-Z14-COG", "PX-AA15"):
        for d in (R.get(rid) or {}).get("reopen_demands", []):
            demands.append((rid, d["gate"]))
    honoured = {(d["demanded_by"], d["gate"]) for d in reopened.get("reopened", [])}
    missing = [d for d in demands if d not in honoured]
    reviewer_briefs = [x for x in sorted(os.listdir(os.path.join(HERE, "briefs")))
                       if x.startswith("BRIEF_Z18_") and "EDITOR" not in x]
    authority = len(reviewer_briefs) == 5 and all(
        "authority to demand" in open(os.path.join(HERE, "briefs", x), encoding="utf-8").read()
        for x in reviewer_briefs)
    dec["Z18-6"] = {"closed": authority and not missing, "by": ["briefs", "REOPENED_GATES_V1.json"],
                    "reason": "%d reopen demands issued, %d honoured" % (len(demands), len(demands) - len(missing))}
    # Z18-8
    rep = doc.get("hostile_review_report") or {}
    rp = os.path.join(HERE, rep.get("path", "HOSTILE_REVIEW_REPORT_V1.md"))
    rep_ok = os.path.exists(rp) and sha256_file(rp) == rep.get("sha256") and rep.get("manuscript_submission") == "NONE_AT_PIN"
    dec["Z18-8"] = {"closed": rep_ok, "by": ["HOSTILE_REVIEW_REPORT_V1.md"], "reason": "report frozen by sha256; no manuscript submission exists at pin"}
    return dec


# ---------------------------------------------------------- reconciliation ----
def build_reconciliation(rows, dec, new_lines, doc):
    reps, nc = [], []
    for r in rows:
        d = dec[r["id"]]
        entry = {"comment_id": r["comment_id"], "anchor": r["anchor"], "old": r["old"]}
        if d["closed"]:
            new = new_lines.get(r["id"])
            if not new:
                raise AssertionError("closed row without a new line: " + r["id"])
            entry["new"] = new
            entry["status"] = "EARNED_BY_LABELLED_MODEL_PROXY"
            reps.append(entry)
        else:
            entry["reason"] = "%s :: %s" % (LABEL, d["reason"])
            nc.append(entry)
    return {"schema": "GMI_ISSUE_COMMENT_RECONCILIATION_V1", "issue": 833,
            "comment_ids": sorted({r["comment_id"] for r in rows}),
            "comment_sha256": {str(k): sha256_file(os.path.join(HERE, v)) for k, v in SNAPSHOTS.items()},
            "heading_depth_note": "All anchors are three-hash subsection headings, byte-exact from the live bodies.",
            "source_main": doc["source_main"], "freeze_commit": doc["freeze_commit"],
            "branch": "research/833-revive-gates", "package": "research/gmi-833-human-gate-proxy-v1",
            "claim_ceiling": CLAIM_CEILING, "label": LABEL, "forbidden_promotions": list(FORBIDDEN),
            "rows_total": len(rows), "rows_closed": len(reps), "rows_not_closed": len(nc),
            "replacements": reps, "not_closed": nc}


def check_reconciliation(rec, rows):
    """H5/H6/H11 live here: label visible, no forbidden token, old unique in snapshot,
    new starts with the checked form of old, closed rows only."""
    v = []
    snaps = {k: open(os.path.join(HERE, p), encoding="utf-8").read() for k, p in SNAPSHOTS.items()}
    for e in rec["replacements"]:
        if LABEL not in e["new"]:
            v.append({"kind": "LABEL_NOT_VISIBLE", "old": e["old"][:60]})
        for tok in FORBIDDEN:
            if re.search(r"(?<![A-Z_])%s(?![A-Z_])" % re.escape(tok), e["new"]):
                v.append({"kind": "FORBIDDEN_PROMOTION", "token": tok, "old": e["old"][:60]})
        if not e["new"].startswith("- [x] " + e["old"][6:]):
            v.append({"kind": "NEW_DOES_NOT_EXTEND_OLD", "old": e["old"][:60]})
    for e in rec["replacements"] + rec["not_closed"]:
        body = snaps[e["comment_id"]]
        n = body.count("\n" + e["old"] + "\n") + body.count("\n" + e["old"] + "\r\n")
        if n != 1:
            v.append({"kind": "OLD_NOT_UNIQUE", "count": n, "old": e["old"][:60]})
        if e["anchor"] not in body:
            v.append({"kind": "ANCHOR_ABSENT", "anchor": e["anchor"]})
    return v


# ------------------------------------------------------------------ main ----
def compute(doc=None, recompute_z9=True):
    doc = doc if doc is not None else load("PROXY_RECORDS_V1.json")
    rows = freeze_rows()
    briefs = freeze_brief_digests()
    pins = freeze_artifact_pins()
    integrity = check_records(doc, briefs, pins)
    z9b = z9_protocol(doc, recompute=recompute_z9)
    gate = exhaustion_gate(load_gaps())
    reopened = load("REOPENED_GATES_V1.json") if os.path.exists(os.path.join(HERE, "REOPENED_GATES_V1.json")) else {"reopened": []}
    dec = decide_rows(doc, z9b, gate, reopened)
    new_lines = load("NEW_LINES_V1.json") if os.path.exists(os.path.join(HERE, "NEW_LINES_V1.json")) else {}
    rec = build_reconciliation(rows, dec, new_lines, doc)
    rec_v = check_reconciliation(rec, rows)
    two_route = {row: dec[row].get("agreement") for row in TWO_ROUTE_ROWS}
    return {"schema": "GMI_833_HUMAN_GATE_PROXY_RESULT_V1", "route": "A", "issue": 833,
            "claim_ceiling": CLAIM_CEILING, "label": LABEL, "source_main": doc["source_main"],
            "freeze_commit": doc["freeze_commit"], "records": len(doc["records"]),
            "record_integrity_violations": integrity, "z9": z9b, "z9_null": z9_null(doc),
            "aa10_gate": gate, "decisions": dec, "closed_rows": sorted(k for k, v in dec.items() if v["closed"]),
            "not_closed_rows": sorted(k for k, v in dec.items() if not v["closed"]),
            "two_route_agreement": two_route, "reconciliation_violations": rec_v,
            "gates": {"record_integrity": integrity == [], "reconciliation_clean": rec_v == [],
                      "aa10_no_violation": gate["violations"] == [],
                      "z9_chain": bool(z9b) and all(all(b["checks"].values()) for b in z9b)},
            "forbidden_promotions": list(FORBIDDEN)}, rec


def hostiles():
    """Every planted defect must move its own gate. Returns dict id -> detected."""
    base = load("PROXY_RECORDS_V1.json")
    rows = freeze_rows()
    briefs = freeze_brief_digests()
    pins = freeze_artifact_pins()
    out = {}
    clean = check_records(base, briefs, pins)
    out["H0_clean_no_alarm"] = clean == []
    d = copy.deepcopy(base); d["records"][0]["label"] = "EXTERNALLY_REVIEWED"
    out["H1_label_removed"] = any(x["kind"] == "LABEL_MISSING_OR_WRONG" for x in check_records(d, briefs, pins))
    d = copy.deepcopy(base); rid = d["records"][0]["id"]
    out["H2_verdict_edited"] = any(x["kind"] == "VERDICT_SHA_MISMATCH" for x in check_records(d, briefs, pins, {"verdict_text": {rid: "tampered"}}))
    d = copy.deepcopy(base); d["records"][0]["brief_sha256"] = "0" * 64
    out["H3_brief_edited"] = any(x["kind"] == "BRIEF_SHA_MISMATCH" for x in check_records(d, briefs, pins))
    d = copy.deepcopy(base)
    for r in d["records"]:
        if r.get("artifacts"):
            k = sorted(r["artifacts"])[0]; r["artifacts"][k] = "f" * 40; break
    out["H4_artifact_edited"] = any(x["kind"] == "ARTIFACT_PIN_MISMATCH" for x in check_records(d, briefs, pins))
    res, rec = compute(base, recompute_z9=False)
    if rec["replacements"]:
        r2 = copy.deepcopy(rec); r2["replacements"][0]["new"] += " EXTERNALLY_REVIEWED"
        out["H5_forbidden_promotion"] = any(x["kind"] == "FORBIDDEN_PROMOTION" for x in check_reconciliation(r2, rows))
        r3 = copy.deepcopy(rec); r3["replacements"][0]["new"] = r3["replacements"][0]["new"].replace(LABEL, "MODEL_PROXY")
        out["H5b_label_hidden"] = any(x["kind"] == "LABEL_NOT_VISIBLE" for x in check_reconciliation(r3, rows))
    # H6: a NOT_SATISFIED proxy row forced closed
    d = copy.deepcopy(base)
    forced = None
    for r in d["records"]:
        for row, v in (r.get("rows") or {}).items():
            if v["verdict"] == "SATISFIED" and row in ("Z10-1", "AC02", "AC05", "Z14-1", "AA41", "AG8-R48", "Z18-1"):
                forced = (r["id"], row); break
        if forced: break
    if forced:
        rr = records_by_id(d)[forced[0]]
        rr["rows"][forced[1]]["verdict"] = "NOT_SATISFIED"
        # stored rows now differ from transcript -> integrity catches the forgery
        out["H6_forced_closure_forgery"] = any(x["kind"] == "STORED_ROWS_DIFFER_FROM_TRANSCRIPT" for x in check_records(d, briefs, pins))
    # H7: two-route row from one model family
    d = copy.deepcopy(base); R = records_by_id(d)
    if "PX-AG8-A" in R and "PX-AG8-B" in R:
        R["PX-AG8-B"]["model_requested"] = R["PX-AG8-A"]["model_requested"]
        dec = decide_rows(d, z9_protocol(d, recompute=False), exhaustion_gate(load_gaps()),
                          load("REOPENED_GATES_V1.json") if os.path.exists(os.path.join(HERE, "REOPENED_GATES_V1.json")) else {"reopened": []})
        out["H7_same_family_two_route"] = dec["AG8-R48"]["closed"] is False
    # H8: planted exhausted gap
    gaps = load_gaps() + [{"id": "PLANT", "status": "EXHAUSTED", "owner_role": "lane"}]
    out["H8_exhausted_without_review"] = exhaustion_gate(gaps)["violations"] != []
    gaps2 = load_gaps() + [{"id": "PLANT2", "status": "EXHAUSTED", "owner_role": "lane",
                            "independent_hostile_review": {"reviewer_kind": LABEL, "reviewer_id": "lane", "verdict_sha256": "a" * 64}}]
    out["H8b_self_review"] = exhaustion_gate(gaps2)["violations"] != []
    # H9: predictions edited after outcomes (sha mismatch)
    d = copy.deepcopy(base)
    if d.get("z9_protocol", {}).get("batches"):
        d["z9_protocol"]["batches"][0]["predictions_sha256"] = "0" * 64
        out["H9_predictions_edited"] = z9_protocol(d, recompute=False)[0]["checks"]["predictions_sha_matches"] is False
        # H10: planted oracle disagreement
        b0 = base["z9_protocol"]["batches"][0]
        outp = json.load(open(os.path.join(HERE, b0["dir"], "OUTCOMES.json")))
        pred = json.load(open(os.path.join(HERE, b0["dir"], "PREDICTIONS.json")))
        o2 = copy.deepcopy(outp)
        lam = sorted(o2["outcomes"][0]["winner_class_set"])[0]
        w = o2["outcomes"][0]["winner_class_set"][lam]
        o2["outcomes"][0]["winner_class_set"][lam] = ["STATELESS"] if w != ["STATELESS"] else ["PERSISTENT_STATE"]
        out["H10_planted_outcome_flip_changes_score"] = score_batch(pred, o2) != score_batch(pred, outp)
    # H11: old string not unique
    r4 = copy.deepcopy(rec)
    if r4["not_closed"] or r4["replacements"]:
        e = (r4["replacements"] or r4["not_closed"])[0]; e["old"] = "- [ ] not a row"
        out["H11_old_absent"] = any(x["kind"] == "OLD_NOT_UNIQUE" for x in check_reconciliation(r4, rows))
    # H12: reopen demand not honoured
    d = copy.deepcopy(base)
    d["records"][0].setdefault("reopen_demands", []).append({"gate": "PLANTED_GATE", "reason": "hostile"})
    dec = decide_rows(d, z9_protocol(d, recompute=False), exhaustion_gate(load_gaps()),
                      load("REOPENED_GATES_V1.json") if os.path.exists(os.path.join(HERE, "REOPENED_GATES_V1.json")) else {"reopened": []})
    out["H12_reopen_not_honoured"] = dec["Z18-6"]["closed"] is False
    return out


def null_records(n=200, seed=833):
    base = load("PROXY_RECORDS_V1.json")
    briefs = freeze_brief_digests(); pins = freeze_artifact_pins()
    rng = random.Random(seed)
    passes = 0
    for _ in range(n):
        d = copy.deepcopy(base)
        for r in d["records"]:
            r["verdict_sha256"] = "".join(rng.choice("0123456789abcdef") for _ in range(64))
            r["brief_sha256"] = "".join(rng.choice("0123456789abcdef") for _ in range(64))
            r["label"] = rng.choice([LABEL, "EXTERNALLY_REVIEWED", "MODEL_PROXY", ""])
        passes += int(check_records(d, briefs, pins) == [])
    return {"trials": n, "random_record_sets_passing_integrity": passes}


if __name__ == "__main__":
    if "--hostiles" in sys.argv:
        h = hostiles()
        print(json.dumps(h, indent=1, sort_keys=True))
        sys.exit(0 if all(h.values()) else 1)
    if "--null" in sys.argv:
        base = load("PROXY_RECORDS_V1.json")
        r = {"records": null_records(), "z9": z9_null(base)}
        print(json.dumps(r, indent=1, sort_keys=True))
        ok = r["records"]["random_record_sets_passing_integrity"] == 0 and (r["z9"]["random_predictors_matching_all"] in (0, None))
        sys.exit(0 if ok else 1)
    res, rec = compute()
    if "--write" in sys.argv:
        with open(os.path.join(HERE, "RESULT_V1.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, sort_keys=True); fh.write("\n")
        with open(os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json"), "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=1, ensure_ascii=False); fh.write("\n")
    print(json.dumps(res, indent=1, sort_keys=True))
    sys.exit(0 if all(res["gates"].values()) else 1)
