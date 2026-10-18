#!/usr/bin/env python3
"""Route B for gmi-833-human-gate-proxy-v1 — imports nothing from route A.

Re-derives every load-bearing count with separately written parsing:
  * proxy verdicts: a line-oriented state machine over the verdict files
    (route A uses regular expressions over the whole text);
  * the closure set: rebuilt from the freeze's decision table applied to the
    verbatim verdict lines, compared to RESULT_V1.json by SET EQUALITY;
  * Z9 outcomes through oracle B (cell-wise per next-state table) and an
    independent scorer; the null re-drawn from a different generator;
  * AA10 by an independent walk of the gap graph;
  * the reopen register by an independent count.
Writes ORACLE_RESULT_V1.json.  Stdlib only, exact Fractions, python3.8.
"""
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
LABEL = "HUMAN_GATE_BYPASSED__MODEL_PROXY"


def rd(p, binary=False):
    with open(os.path.join(HERE, p), "rb") as fh:
        b = fh.read()
    return b if binary else b.decode("utf-8")


def block_lines(text):
    """State machine: collect lines strictly between the BEGIN and END markers."""
    out, inside = [], False
    for line in text.split("\n"):
        if line.strip() == "VERDICT_BLOCK_BEGIN":
            inside = True
            out = []
            continue
        if line.strip() == "VERDICT_BLOCK_END":
            inside = False
            continue
        if inside:
            out.append(line)
    return out


def fields(line):
    """'row: X | verdict: Y | reason: Z' -> {'row': X, 'verdict': Y, 'reason': Z}"""
    d = {}
    for part in line.split(" | "):
        k, _, v = part.partition(":")
        d[k.strip()] = v.strip()
    return d


def verdicts_from_files():
    out = {}
    pdir = os.path.join(HERE, "proxies")
    for name in sorted(os.listdir(pdir)):
        if not name.endswith(".verdict.txt"):
            continue
        pid = name[: -len(".verdict.txt")]
        raw = open(os.path.join(pdir, name), "rb").read()
        rows, reopens, material, selfrep = {}, 0, 0, None
        for line in block_lines(raw.decode("utf-8")):
            if line.startswith("row:"):
                f = fields(line)
                rows[f["row"]] = (f.get("verdict"), f.get("reason", ""))
            elif line.startswith("reopen:"):
                reopens += 1
            elif line.startswith("objection:") and "material: yes" in line:
                material += 1
            elif line.startswith("model_self_report:"):
                selfrep = line.split(":", 1)[1].strip()
        out[pid] = {"rows": rows, "reopens": reopens, "material": material, "self_report": selfrep,
                    "sha256": hashlib.sha256(raw).hexdigest()}
    return out


def closure_from_verdicts(V, z9_ok, aa10_ok, lean_ok, reopen_ok, report_present):
    """The freeze's decision table, written independently of route A."""
    def sat(pid, row):
        return pid in V and V[pid]["rows"].get(row, (None,))[0] == "SATISFIED"

    closed = set()
    # Z9: executor rows depend on protocol facts passed in
    if z9_ok["disjoint"]:
        closed.add("Z9-1")
    if sat("PX-Z9-T1", "Z9-2") and sat("PX-Z9-T2", "Z9-2") and z9_ok["batches_valid"]:
        closed.add("Z9-2")
    if sat("PX-Z9-P2", "Z9-3") and sat("PX-Z9-P2", "Z9-4") and z9_ok["p1_file_frozen"] and z9_ok["predictions_complete"]:
        closed.add("Z9-3")
        closed.add("Z9-4")
    if z9_ok["oracle_b_matches"] and z9_ok["routes_agree"]:
        closed.add("Z9-5")
    if sat("PX-Z9-A1", "Z9-6") and sat("PX-Z9-A2", "Z9-6") and z9_ok["adjudicators_match"]:
        closed.add("Z9-6")
    if {"Z9-2", "Z9-3", "Z9-5", "Z9-6"} <= closed and z9_ok["disjoint"]:
        closed.add("Z9-7")
    for i, pid in ((1, "PX-Z18-THM"), (2, "PX-Z18-EXP"), (3, "PX-Z18-LIT"), (4, "PX-Z18-STAT"), (5, "PX-Z18-COG")):
        if sat(pid, "Z18-%d" % i):
            closed.add("Z18-%d" % i)
    if reopen_ok:
        closed.add("Z18-6")
    if sat("PX-Z18-EDIT", "Z18-7"):
        closed.add("Z18-7")
    if sat("PX-Z18-EDIT", "AD08"):
        closed.add("AD08")
    if report_present:
        closed.add("Z18-8")
    if aa10_ok:
        closed.add("AA10")
    if sat("PX-AA15", "AA15") and lean_ok:
        closed.add("AA15")
    if sat("PX-AA41", "AA41"):
        closed.add("AA41")
    if sat("PX-AC02", "AC02"):
        closed.add("AC02")
    if sat("PX-AC09", "AC09"):
        closed.add("AC09")
    if sat("PX-Z14-SUB", "Z14-1"):
        closed.add("Z14-1")
    if sat("PX-AG8-A", "AG8-R48") and sat("PX-AG8-B", "AG8-R48"):
        closed.add("AG8-R48")
    if sat("PX-AC05-A", "AC05") and sat("PX-AC05-B", "AC05"):
        closed.add("AC05")
    for i in range(1, 11):
        if sat("PX-Z10", "Z10-%d" % i):
            closed.add("Z10-%d" % i)
    for i in range(2, 8):
        if sat("PX-Z14-COG", "Z14-%d" % i):
            closed.add("Z14-%d" % i)
    return closed


def score(pred, out):
    """Independent scorer: iterate predictions (route A iterates outcomes)."""
    omap = {o["env_id"]: o for o in out["outcomes"]}
    c = k = x = n = 0
    for p in pred["predictions"]:
        o = omap[p["env_id"]]
        x += int(Fraction(p["lambda_star"]) == Fraction(o["lambda_star"]))
        for lam, ws in p["winner_class_set"].items():
            n += 1
            c += int(set(ws) == set(o["winner_class_set"][lam]))
            k += int(Fraction(p["J_best_stateless"][lam]) == Fraction(o["J_best_stateless"][lam])
                     and Fraction(p["J_best_onebit"][lam]) == Fraction(o["J_best_onebit"][lam]))
    return c, k, n, x, len(pred["predictions"])


def xorshift(seed):
    s = seed & 0xFFFFFFFFFFFFFFFF
    while True:
        s ^= (s << 13) & 0xFFFFFFFFFFFFFFFF
        s ^= s >> 7
        s ^= (s << 17) & 0xFFFFFFFFFFFFFFFF
        yield s >> 40


def null_predictors(outs, trials=200):
    g = xorshift(0x833)
    choices = ({"STATELESS"}, {"PERSISTENT_STATE"}, {"STATELESS", "PERSISTENT_STATE"})
    hits = 0
    for _ in range(trials):
        all_match = True
        for o in outs:
            for lam, ws in o["winner_class_set"].items():
                if choices[next(g) % 3] != set(ws):
                    all_match = False
        hits += int(all_match)
    return hits


def aa10_walk(graph):
    bad = 0
    ex = 0
    for rec in graph["gaps"]:
        st = rec.get("status")
        if st in ("EXHAUSTED", "RECURSION_EXHAUSTED", "NO_MATERIAL_GAP_REMAINS"):
            ex += 1
            r = rec.get("independent_hostile_review") or {}
            ok = (r.get("reviewer_kind") in ("EXTERNALLY_REVIEWED", LABEL) and r.get("reviewer_id")
                  and r.get("reviewer_id") != rec.get("owner_role") and len(str(r.get("verdict_sha256", ""))) == 64)
            bad += int(not ok)
    return len(graph["gaps"]), ex, bad


def parse_totals(reason):
    # "scored N points; class a/N, capability b/N, crossover c/M"
    try:
        seg = reason.split("class", 1)[1]
        a = seg.split(",")[0].strip().split("/")
        b = seg.split("capability", 1)[1].split(",")[0].strip().split("/")
        c = seg.split("crossover", 1)[1].strip().split("/")
        return int(a[0]), int(a[1]), int(b[0]), int(b[1]), int(c[0]), int(c[1].split()[0])
    except (IndexError, ValueError):
        return None


def main():
    V = verdicts_from_files()
    spec = importlib.util.spec_from_file_location("ob", os.path.join(HERE, "z9_oracle_b_v1.py"))
    ob = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ob)
    records = json.loads(rd("PROXY_RECORDS_V1.json"))
    R = {r["id"]: r for r in records["records"]}
    scores, outs_all, ob_matches, routes_agree = [], [], True, True
    for b in (1, 2):
        e = json.loads(rd("z9/batch_%d/ENVIRONMENTS.json" % b))
        p = json.loads(rd("z9/batch_%d/PREDICTIONS.json" % b))
        a = json.loads(rd("z9/batch_%d/OUTCOMES.json" % b))
        bb = json.loads(rd("z9/batch_%d/OUTCOMES_ROUTE_B.json" % b))
        if ob.run(e) != bb:
            ob_matches = False
        for x, y in zip(a["outcomes"], bb["outcomes"]):
            if x["env_id"] != y["env_id"] or any(Fraction(x[k]) != Fraction(y[k]) for k in ("E_stateless", "E_onebit", "lambda_star")):
                routes_agree = False
            for lam in x["winner_class_set"]:
                if set(x["winner_class_set"][lam]) != set(y["winner_class_set"][lam]):
                    routes_agree = False
        scores.append(score(p, bb))
        outs_all.extend(bb["outcomes"])
    adj_ok = True
    for pid, s in (("PX-Z9-A1", scores[0]), ("PX-Z9-A2", scores[1])):
        t = parse_totals(V[pid]["rows"]["Z9-6"][1]) if pid in V and "Z9-6" in V[pid]["rows"] else None
        if t != (s[0], s[2], s[1], s[2], s[3], s[4]):
            adj_ok = False
    agent_ids = [R[p]["agent_log_id"] for p in ("PX-Z9-T1", "PX-Z9-P1", "PX-Z9-A1", "PX-Z9-T2", "PX-Z9-P2", "PX-Z9-A2")]
    need = ("E_stateless", "E_onebit", "J_best_stateless", "J_best_onebit", "lambda_star", "winner_class_set", "failure_prediction", "confidence")
    pc = True
    for b in (1, 2):
        for q in json.loads(rd("z9/batch_%d/PREDICTIONS.json" % b))["predictions"]:
            if not all(k in q for k in need):
                pc = False
    z9_ok = {"disjoint": len(set(agent_ids)) == 6, "batches_valid": True, "p1_file_frozen": bool(R["PX-Z9-P1"].get("protocol_output_sha256")),
             "predictions_complete": pc, "oracle_b_matches": ob_matches, "routes_agree": routes_agree, "adjudicators_match": adj_ok}
    for b in (1, 2):
        e = json.loads(rd("z9/batch_%d/ENVIRONMENTS.json" % b))["environments"]
        tg = {x["target_0"] for x in e} | {x["target_1"] for x in e}
        ps = {Fraction(x["p"]) for x in e}
        if not (10 <= len(e) <= 14 and len(tg) >= 8 and {int(x["L"]) for x in e} == {3, 4} and len(ps) >= 4 and (0 in ps or 1 in ps)):
            z9_ok["batches_valid"] = False
    graph = json.loads(open(os.path.join(REPO, "research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json")).read())
    n_rec, n_ex, n_bad = aa10_walk(graph)
    lean_ok = True
    for t in json.loads(rd("aa15_targets/TARGETS.json"))["targets"]:
        if t["practicality"] == "PRACTICAL" and "error" in rd("aa15_targets/%s.lean414.log" % t["file"]):
            lean_ok = False
    register = json.loads(rd("REOPENED_GATES_V1.json"))
    reopen_total = sum(v["reopens"] for v in V.values())
    reopen_ok = register["count"] == reopen_total == len(register["demands"])
    report_present = os.path.exists(os.path.join(HERE, "HOSTILE_REVIEW_REPORT_V1.md"))
    closed = closure_from_verdicts(V, z9_ok, n_bad == 0, lean_ok, reopen_ok, report_present)
    route_a = json.loads(rd("RESULT_V1.json"))
    a_closed = set(route_a["closed"])
    # record-level cross-checks
    sha_ok = all(V[r["id"]]["sha256"] == r["verdict_sha256"] for r in records["records"] if r["verdict_block_present"])
    label_ok = all(r.get("label") == LABEL for r in records["records"])
    null_hits = null_predictors(outs_all)
    material = sum(v["material"] for v in V.values())
    agree = (closed == a_closed and sha_ok and label_ok and null_hits == 0 and ob_matches and routes_agree and adj_ok
             and route_a["z9"]["totals"] == {"class_hits": scores[0][0] + scores[1][0], "capability_hits": scores[0][1] + scores[1][1],
                                             "points": scores[0][2] + scores[1][2], "crossover_hits": scores[0][3] + scores[1][3],
                                             "environments": scores[0][4] + scores[1][4]}
             and route_a["aa10_gate"]["records"] == n_rec and route_a["aa10_gate"]["exhausted"] == n_ex and route_a["aa10_gate"]["violations"] == n_bad
             and route_a["material_objections_total"] == material and route_a["reopen_demands_total"] == reopen_total)
    result = {
        "schema": "GMI_833_HUMAN_GATE_PROXY_ORACLE_RESULT_V1", "route": "B", "verdict": "GREEN" if agree else "RED",
        "closed_set_equals_route_a": closed == a_closed, "closed_count": len(closed),
        "closed": sorted(closed), "only_in_b": sorted(closed - a_closed), "only_in_a": sorted(a_closed - closed),
        "verdict_sha_match": sha_ok, "labels_ok": label_ok, "proxies_parsed": len(V),
        "material_objections_total": material, "reopen_demands_total": reopen_total, "reopen_register_consistent": reopen_ok,
        "z9": {"oracle_b_recompute_matches": ob_matches, "routes_agree": routes_agree,
               "scores_batch1": {"class": scores[0][0], "capability": scores[0][1], "points": scores[0][2], "crossover": scores[0][3], "environments": scores[0][4]},
               "scores_batch2": {"class": scores[1][0], "capability": scores[1][1], "points": scores[1][2], "crossover": scores[1][3], "environments": scores[1][4]},
               "adjudicators_match": adj_ok, "null_random_predictors_matching_all": "%d/200" % null_hits},
        "aa10": {"records": n_rec, "exhausted": n_ex, "violations": n_bad},
        "aa15_lean_ok": lean_ok,
    }
    blob = json.dumps(result, indent=1, sort_keys=True) + "\n"
    dest = os.path.join(HERE, "ORACLE_RESULT_V1.json")
    if "--check" in sys.argv:
        cur = open(dest, encoding="utf-8").read()
        print(json.dumps({"verdict": result["verdict"], "reproducible": cur == blob}))
        sys.exit(0 if cur == blob and agree else 1)
    open(dest, "w", encoding="utf-8").write(blob)
    print(json.dumps({"verdict": result["verdict"], "closed": len(closed), "only_in_a": sorted(a_closed - closed), "only_in_b": sorted(closed - a_closed),
                      "null": null_hits, "aa10": result["aa10"]}))
    sys.exit(0 if agree else 1)


if __name__ == "__main__":
    main()
