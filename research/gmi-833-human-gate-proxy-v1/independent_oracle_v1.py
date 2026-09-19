#!/usr/bin/env python3
"""Route B for gmi-833-human-gate-proxy-v1: an independently written check of
the same claims.  Shares no code with human_gate_proxy_v1.py: line state
machines instead of regexes, chunked hashing, a table-driven row evaluator,
oracle B for Z9 outcomes, and a separate walk of the gap graph.

Usage: independent_oracle_v1.py [--write]     (ORACLE_RESULT_V1.json)
"""
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
LABEL = "HUMAN_GATE_BYPASSED__MODEL_PROXY"
TWO_ROUTE = {"AG8-R48": ("PX-AG8-A", "PX-AG8-B"), "AC05": ("PX-AC05-A", "PX-AC05-B")}
SIMPLE = {"Z18-1": "PX-Z18-THM", "Z18-2": "PX-Z18-EXP", "Z18-3": "PX-Z18-LIT", "Z18-4": "PX-Z18-STAT",
          "Z18-5": "PX-Z18-COG", "Z18-7": "PX-Z18-EDIT", "AD08": "PX-Z18-EDIT", "AA41": "PX-AA41",
          "AC02": "PX-AC02", "AC09": "PX-AC09", "Z14-1": "PX-Z14-SUB"}
for _i in range(2, 8):
    SIMPLE["Z14-%d" % _i] = "PX-Z14-COG"
for _i in range(1, 11):
    SIMPLE["Z10-%d" % _i] = "PX-Z10"


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def read(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as fh:
        return fh.read()


def freeze_tables():
    """Line scan of FREEZE_V1.md: rows, brief digests, artifact pins."""
    rows, briefs, pins = [], {}, {}
    state = None
    comment = anchor = None
    for line in read("FREEZE_V1.md").split("\n"):
        if line.startswith("## "):
            head = line[3:]
            state = ("rows" if head.startswith("2.") else "briefs" if head.startswith("9.")
                     else "pins" if head.startswith("10.") else None)
            continue
        if state == "rows":
            if line.startswith("### 2.1"):
                comment = 5684819296
            elif line.startswith("### 2.2"):
                comment = 5684607872
            elif line.startswith("### 2.3"):
                comment = 5693520829
            elif line.startswith("> ### "):
                anchor = line[2:]
            elif line.startswith("- [ ] "):
                rows.append((comment, anchor, line))
        elif state == "briefs" and line.startswith("| `briefs/"):
            cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
            briefs[cells[0]] = cells[1]
        elif state == "pins" and line.startswith("| `") and len(line) > 50:
            cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
            if len(cells[0]) == 40:
                pins[cells[1]] = cells[0]
    return rows, briefs, pins


def parse_block(text):
    """State machine: collect the last VERDICT block; split fields on '|'."""
    blocks, cur = [], None
    for line in text.split("\n"):
        s = line.strip()
        if s == "VERDICT_BLOCK_BEGIN":
            cur = []
        elif s == "VERDICT_BLOCK_END" and cur is not None:
            blocks.append(cur)
            cur = None
        elif cur is not None:
            cur.append(s)
    if not blocks:
        return None
    rows, claims, self_report, reopen = {}, {}, None, []
    for s in blocks[-1]:
        if s.startswith("model_self_report:"):
            self_report = s[len("model_self_report:"):].strip()
            continue
        parts = [p.strip() for p in s.split("|")]
        kv = {}
        for p in parts:
            if ":" in p:
                k, v = p.split(":", 1)
                kv.setdefault(k.strip(), v.strip())
        if s.startswith("row:") and "verdict" in kv and "reason" in kv:
            rows[kv["row"]] = {"verdict": kv["verdict"], "reason": kv["reason"]}
        elif s.startswith("claim:") and "verdict" in kv and "reason" in kv:
            claims[kv["claim"]] = {"verdict": kv["verdict"], "reason": kv["reason"]}
        elif s.startswith("reopen:") and kv.get("reopen", "").lower() not in ("none", "<gate or result name>", ""):
            reopen.append(kv["reopen"])
    return rows, claims, self_report, reopen


def integrity(doc, briefs, pins):
    bad = 0
    for r in doc["records"]:
        if r.get("label") != LABEL:
            bad += 1
        b = r.get("brief")
        if b not in briefs or briefs[b] != r.get("brief_sha256") or digest(os.path.join(HERE, b)) != briefs[b]:
            bad += 1
        for p, sha in (r.get("artifacts") or {}).items():
            if not p.startswith("research/gmi-833-human-gate-proxy-v1/") and pins.get(p) != sha:
                bad += 1
        for p, sha in (r.get("inputs_sha256") or {}).items():
            if digest(os.path.join(HERE, p)) != sha:
                bad += 1
        vf = os.path.join(HERE, r.get("verdict_file", "missing"))
        if not os.path.exists(vf) or digest(vf) != r.get("verdict_sha256"):
            bad += 1
            continue
        parsed = parse_block(open(vf, encoding="utf-8").read())
        if parsed is None:
            bad += 1
            continue
        rows, claims, self_report, reopen = parsed
        if rows != r.get("rows", {}) or claims != r.get("claims", {}) or self_report != r.get("model_self_report"):
            bad += 1
        if sorted(reopen) != sorted(d["gate"] for d in r.get("reopen_demands", [])):
            bad += 1
        if r.get("spawned_after_freeze_commit") != doc.get("freeze_commit"):
            bad += 1
    return bad


def sat(R, rid, row):
    r = R.get(rid)
    if not r:
        return False
    v = r.get("rows", {}).get(row)
    return bool(v) and v.get("verdict") == "SATISFIED"


def z9(doc):
    import importlib.util
    spec = importlib.util.spec_from_file_location("z9b", os.path.join(HERE, "z9_oracle_b_v1.py"))
    z9b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z9b)
    out = []
    for b in doc.get("z9_protocol", {}).get("batches", []):
        d = os.path.join(HERE, b["dir"])
        env = json.load(open(os.path.join(d, "ENVIRONMENTS.json")))
        pred = json.load(open(os.path.join(d, "PREDICTIONS.json")))
        com = json.load(open(os.path.join(d, "OUTCOMES.json")))
        fresh = z9b.run(env)["outcomes"]
        agree = all(all(f[k] == c[k] for k in ("E_stateless", "E_onebit", "lambda_star", "J_best_stateless",
                                                "J_best_onebit", "winner_class_set"))
                    for f, c in zip(fresh, com["outcomes"])) and len(fresh) == len(com["outcomes"])
        shas_ok = (digest(os.path.join(d, "ENVIRONMENTS.json")) == b["environments_sha256"]
                   and digest(os.path.join(d, "PREDICTIONS.json")) == b["predictions_sha256"]
                   and digest(os.path.join(d, "OUTCOMES.json")) == b["outcomes_sha256"])
        ch = cht = cap = capt = cro = crot = 0
        P = {p["env_id"]: p for p in pred["predictions"]}
        for o in com["outcomes"]:
            p = P.get(o["env_id"], {})
            for lam, w in o["winner_class_set"].items():
                cht += 1
                if sorted(p.get("winner_class_set", {}).get(lam, [])) == sorted(w):
                    ch += 1
                capt += 1
                try:
                    if (Fraction(p["J_best_stateless"][lam]) == Fraction(o["J_best_stateless"][lam])
                            and Fraction(p["J_best_onebit"][lam]) == Fraction(o["J_best_onebit"][lam])):
                        cap += 1
                except (KeyError, ValueError, ZeroDivisionError):
                    pass
            crot += 1
            try:
                if Fraction(p["lambda_star"]) == Fraction(o["lambda_star"]):
                    cro += 1
            except (KeyError, ValueError, ZeroDivisionError):
                pass
        out.append({"batch": b["batch"], "oracle_b_agrees_with_committed_outcomes": agree, "shas_ok": shas_ok,
                    "roles_distinct": len({b["test_team"], b["prediction_team"], b["adjudicator"]}) == 3,
                    "class": [ch, cht], "capability": [cap, capt], "crossover": [cro, crot]})
    return out


def aa10():
    gaps = json.load(open(os.path.join(REPO, "research", "gmi-833-corpus-census-v1", "GMI_GAP_GRAPH_V1.json")))["gaps"]
    ex = [g for g in gaps if str(g.get("status", "")).endswith("EXHAUSTED") or g.get("status") == "NO_MATERIAL_GAP_REMAINS"]
    bad = 0
    for g in ex:
        rv = g.get("independent_hostile_review") or {}
        if rv.get("reviewer_kind") not in ("EXTERNALLY_REVIEWED", LABEL) or rv.get("reviewer_id") in (None, "", g.get("owner_role")) \
                or len(str(rv.get("verdict_sha256", ""))) != 64:
            bad += 1
    return {"records": len(gaps), "exhausted": len(ex), "violations": bad}


def decide(doc, z9r, gate, reopened):
    R = {r["id"]: r for r in doc["records"]}
    closed = {}
    for row, rid in SIMPLE.items():
        closed[row] = sat(R, rid, row)
    lean = doc.get("lean_check") or {}
    closed["AA15"] = sat(R, "PX-AA15", "AA15") and bool(lean.get("targets")) and all(t.get("exit_code") == 0 for t in lean["targets"])
    for row, (a, b) in TWO_ROUTE.items():
        fa, fb = (R.get(a) or {}).get("model_requested"), (R.get(b) or {}).get("model_requested")
        closed[row] = sat(R, a, row) and sat(R, b, row) and fa is not None and fb is not None and fa != fb
    chain = bool(z9r) and all(x["oracle_b_agrees_with_committed_outcomes"] and x["shas_ok"] and x["roles_distinct"] for x in z9r)
    closed["Z9-1"] = chain
    closed["Z9-2"] = chain and sat(R, "PX-Z9-T1", "Z9-2") and sat(R, "PX-Z9-T2", "Z9-2")
    closed["Z9-3"] = chain and sat(R, "PX-Z9-P1", "Z9-3") and sat(R, "PX-Z9-P2", "Z9-3")
    closed["Z9-4"] = chain and sat(R, "PX-Z9-P1", "Z9-4") and sat(R, "PX-Z9-P2", "Z9-4")
    closed["Z9-5"] = chain
    closed["Z9-6"] = chain and sat(R, "PX-Z9-A1", "Z9-6") and sat(R, "PX-Z9-A2", "Z9-6")
    closed["Z9-7"] = chain and len(z9r) >= 2
    closed["AA10"] = gate["violations"] == 0 and doc.get("aa10_gate_wired") is True
    demands = set()
    for rid, r in R.items():
        if rid.startswith("PX-Z9-") or rid == "PX-Z18-EDIT":
            continue
        for d in r.get("reopen_demands", []):
            demands.add((rid, d["gate"]))
    honoured = {(d["demanded_by"], d["gate"]) for d in reopened.get("reopened", [])}
    briefs_dir = os.path.join(HERE, "briefs")
    rb = [x for x in os.listdir(briefs_dir) if x.startswith("BRIEF_Z18_") and "EDITOR" not in x]
    authority = len(rb) == 5 and all("authority to demand" in open(os.path.join(briefs_dir, x), encoding="utf-8").read() for x in rb)
    closed["Z18-6"] = authority and demands <= honoured
    rep = doc.get("hostile_review_report") or {}
    rp = os.path.join(HERE, rep.get("path", "HOSTILE_REVIEW_REPORT_V1.md"))
    closed["Z18-8"] = os.path.exists(rp) and digest(rp) == rep.get("sha256") and rep.get("manuscript_submission") == "NONE_AT_PIN"
    return closed


def main():
    doc = json.load(open(os.path.join(HERE, "PROXY_RECORDS_V1.json")))
    rows, briefs, pins = freeze_tables()
    reopened = {"reopened": []}
    if os.path.exists(os.path.join(HERE, "REOPENED_GATES_V1.json")):
        reopened = json.load(open(os.path.join(HERE, "REOPENED_GATES_V1.json")))
    z9r = z9(doc)
    gate = aa10()
    closed = decide(doc, z9r, gate, reopened)
    res = {"schema": "GMI_833_HUMAN_GATE_PROXY_ORACLE_RESULT_V1", "route": "B", "rows_in_freeze": len(rows),
           "records": len(doc["records"]), "integrity_violations": integrity(doc, briefs, pins),
           "closed_rows": sorted(k for k, v in closed.items() if v), "not_closed_rows": sorted(k for k, v in closed.items() if not v),
           "z9": z9r, "aa10": gate}
    if "--write" in sys.argv:
        with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, sort_keys=True); fh.write("\n")
    print(json.dumps(res, indent=1, sort_keys=True))
    return 0 if res["integrity_violations"] == 0 and len(rows) == 40 else 1


if __name__ == "__main__":
    sys.exit(main())
