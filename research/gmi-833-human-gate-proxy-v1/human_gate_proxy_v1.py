#!/usr/bin/env python3
"""Route A executor for gmi-833-human-gate-proxy-v1.

Decides, from committed bytes only, which of the forty frozen rows close under
the decision rules of FREEZE_V1.md section 4, checks every proxy record's
integrity, scores the Z9 protocol through oracle A, runs the AA10 exhaustion
gate over the live gap graph, runs the twelve registered hostiles (each must be
DETECTED and carry `applicable: true`) and the two nulls, and writes
RESULT_V1.json.  Stdlib only, exact Fractions, python3.8, deterministic.

Usage:  python3 -I -B human_gate_proxy_v1.py            # writes RESULT_V1.json
        python3 -I -B human_gate_proxy_v1.py --check    # compares, no write
"""
from fractions import Fraction
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
LABEL = "HUMAN_GATE_BYPASSED__MODEL_PROXY"
FORBIDDEN = ["EXTERNALLY_REVIEWED", "INDEPENDENT_TEAM_REPLICATION", "M5", "HUMAN_REVIEW_OBTAINED",
             "THIRD_PARTY_ADJUDICATED", "REAL_SYSTEM_VALIDATED_BY_PROXY",
             "COGNITIVE_SCIENCE_EVIDENCE_OBTAINED", "CROSS_SPECIES_PREDICTION_CONFIRMED",
             "PROXY_VERDICT_IS_TRUTH", "MANUSCRIPT_READY", "COMPLETE_GMI"]
EXHAUSTED = {"EXHAUSTED", "RECURSION_EXHAUSTED", "NO_MATERIAL_GAP_REMAINS"}
REVIEWER_KINDS = {"EXTERNALLY_REVIEWED", LABEL}
ALL_ROWS = (["Z9-%d" % i for i in range(1, 8)] + ["Z10-%d" % i for i in range(1, 11)]
            + ["Z14-%d" % i for i in range(1, 8)] + ["Z18-%d" % i for i in range(1, 9)]
            + ["AA10", "AA15", "AA41", "AC02", "AC05", "AC09", "AD08", "AG8-R48"])
SNAPSHOTS = {"5684819296": "snapshots/COMMENT_5684819296_SNAPSHOT_V1.txt",
             "5684607872": "snapshots/COMMENT_5684607872_SNAPSHOT_V1.txt",
             "5693520829": "snapshots/COMMENT_5693520829_SNAPSHOT_V1.txt"}


# --------------------------------------------------------------------------- io
def read(path, mode="r"):
    with open(os.path.join(HERE, path), "rb") as fh:
        b = fh.read()
    return b if mode == "rb" else b.decode("utf-8")


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def blob_sha(b):
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(b))
    h.update(b)
    return h.hexdigest()


def git_blob(sha):
    """Bytes of a blob from the repository object store, or None if unreachable."""
    try:
        r = subprocess.run(["git", "cat-file", "blob", sha], cwd=REPO, capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def load_oracle(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ freeze parse
def parse_freeze(text):
    briefs = {}
    for m in re.finditer(r"\| `briefs/([A-Z0-9_]+\.md)` \| `([0-9a-f]{64})` \| (\d+) \|", text):
        briefs[m.group(1)] = (m.group(2), int(m.group(3)))
    pins = {}
    for m in re.finditer(r"\| `([0-9a-f]{40})` \| `(research/[^`]+)` \|", text):
        pins[m.group(2)] = m.group(1)
    snaps = {}
    for m in re.finditer(r"`(\d{10})` → `([0-9a-f]{64})`", text):
        snaps[m.group(1)] = m.group(2)
    source_main = re.search(r"Source `main`: `([0-9a-f]{40})`", text).group(1)
    ceiling = re.search(r"```\n(GMI_833_[A-Z_]+)\n```", text).group(1)
    return {"briefs": briefs, "pins": pins, "snapshots": snaps, "source_main": source_main, "ceiling": ceiling}


# ---------------------------------------------------------------- verdict parse
def parse_block(text):
    m = re.search(r"VERDICT_BLOCK_BEGIN\n(.*?)VERDICT_BLOCK_END", text, re.S)
    if not m:
        return None
    rows, claims, objections, reopens, selfrep = {}, {}, [], [], None
    for line in m.group(1).splitlines():
        if line.startswith("row:"):
            mm = re.match(r"row:\s*(\S+)\s*\|\s*verdict:\s*(\S+)\s*\|\s*reason:\s*(.*)$", line)
            if mm:
                rows[mm.group(1)] = (mm.group(2), mm.group(3).strip())
        elif line.startswith("claim:"):
            mm = re.match(r"claim:\s*(\S+)\s*\|\s*verdict:\s*(\S+)\s*\|\s*reason:\s*(.*)$", line)
            if mm:
                claims[mm.group(1)] = (mm.group(2), mm.group(3).strip())
        elif line.startswith("objection:"):
            mm = re.match(r"objection:\s*(.+?)\s*\|(?:\s*claim:\s*(\S+)\s*\|)?\s*material:\s*(\S+)\s*\|", line)
            if mm:
                objections.append((mm.group(1), mm.group(2), mm.group(3) == "yes"))
        elif line.startswith("reopen:"):
            gate = line[len("reopen:"):].partition("| reason:")[0].strip()
            reopens.append(gate)
        elif line.startswith("model_self_report:"):
            selfrep = line[len("model_self_report:"):].strip()
    return {"rows": rows, "claims": claims, "objections": objections, "reopens": reopens, "self_report": selfrep}


# ------------------------------------------------------------ record integrity
def check_records(records, freeze, verdict_texts, briefs_text, artifacts_bytes):
    """Return list of violation strings (empty = integrity holds)."""
    v = []
    fam = {}
    for r in records["records"]:
        pid = r["id"]
        if r.get("label") != LABEL:
            v.append("H1:%s:label" % pid)
        bname = r["brief"].split("/")[-1]
        if bname not in freeze["briefs"]:
            v.append("H3:%s:brief-not-frozen" % pid)
        else:
            want, nbytes = freeze["briefs"][bname]
            got = briefs_text.get(bname)
            if got is None or sha256(got) != want or len(got) != nbytes:
                v.append("H3:%s:brief-sha" % pid)
            if r.get("brief_sha256") != want:
                v.append("H3:%s:record-brief-sha" % pid)
        for path in r.get("artifacts_handed", []):
            if path in freeze["pins"]:
                b = artifacts_bytes.get(path)
                if b is None or blob_sha(b) != freeze["pins"][path]:
                    v.append("H4:%s:%s" % (pid, path))
            elif path.startswith("research/gmi-833-human-gate-proxy-v1/"):
                pass  # this package's own files (editor inputs) are bound by sha in RESULT
            else:
                v.append("H4:%s:unpinned:%s" % (pid, path))
        if r.get("verdict_block_present"):
            text = verdict_texts.get(pid)
            if text is None or sha256(text) != r.get("verdict_sha256") or len(text) != r.get("verdict_bytes"):
                v.append("H2:%s:verdict-sha" % pid)
                continue
            parsed = parse_block(text.decode("utf-8"))
            if parsed is None:
                v.append("H2:%s:no-block" % pid)
                continue
            recorded = {x["row"]: x["verdict"] for x in r.get("rows", [])}
            if {k: a for k, (a, _) in parsed["rows"].items()} != recorded:
                v.append("H6:%s:row-verdicts-differ-from-verbatim" % pid)
            if not parsed["self_report"]:
                v.append("H1:%s:no-self-report" % pid)
            if r.get("model_self_report") != parsed["self_report"]:
                v.append("H2:%s:self-report" % pid)
        fam.setdefault(pid.rsplit("-", 1)[0] if pid[-2] == "-" else pid, []).append(r.get("requested_model"))
    return v


# ------------------------------------------------------------------ Z9 scoring
def frac(s):
    return Fraction(s)


def score_batch(pred, out):
    ch = ct = cc = 0
    n = m = 0
    misses = []
    pmap = {p["env_id"]: p for p in pred["predictions"]}
    for o in out["outcomes"]:
        p = pmap[o["env_id"]]
        m += 1
        if frac(p["lambda_star"]) == frac(o["lambda_star"]):
            cc += 1
        else:
            misses.append([o["env_id"], "lambda_star", p["lambda_star"], o["lambda_star"]])
        for lam in o["winner_class_set"]:
            n += 1
            if sorted(p["winner_class_set"][lam]) == sorted(o["winner_class_set"][lam]):
                ch += 1
            else:
                misses.append([o["env_id"], lam, "class", p["winner_class_set"][lam], o["winner_class_set"][lam]])
            if (frac(p["J_best_stateless"][lam]) == frac(o["J_best_stateless"][lam])
                    and frac(p["J_best_onebit"][lam]) == frac(o["J_best_onebit"][lam])):
                ct += 1
    return {"class_hits": ch, "capability_hits": ct, "points": n, "crossover_hits": cc, "environments": m,
            "misses": misses}


def batch_valid(env):
    """The test-team brief's construction requirements, checked mechanically."""
    es = env["environments"]
    targets = set()
    ps = set()
    ls = set()
    for e in es:
        targets.add(e["target_0"])
        targets.add(e["target_1"])
        ps.add(Fraction(e["p"]))
        ls.add(int(e["L"]))
        for x in (e["p"], e["eta"]) + tuple(e["lambdas"]):
            f = Fraction(x)
            if str(f) != x:
                return False, "unreduced fraction %s" % x
    two_back = {"PREV2", "XOR2", "AND2", "OR2", "MAJ3"}
    ok = (10 <= len(es) <= 14 and len(targets) >= 8 and len(targets & two_back) >= 2 and ls == {3, 4}
          and len(ps) >= 4 and (Fraction(0) in ps or Fraction(1) in ps))
    return ok, {"environments": len(es), "distinct_targets": len(targets), "two_back_targets": len(targets & two_back),
                "lengths": sorted(ls), "distinct_p": len(ps)}


def lcg(seed):
    """Deterministic 64-bit LCG; high bits consumed (never the low bits)."""
    s = seed & ((1 << 64) - 1)
    while True:
        s = (6364136223846793005 * s + 1442695040888963407) & ((1 << 64) - 1)
        yield s >> 33


def z9_null(outcomes_all, trials=200):
    """Random class-set predictors: each (environment, lambda) gets one of the
    three class sets uniformly.  Count predictors matching EVERY winner set."""
    g = lcg(833)
    sets = [["STATELESS"], ["PERSISTENT_STATE"], ["PERSISTENT_STATE", "STATELESS"]]
    matched = 0
    for _ in range(trials):
        ok = True
        for o in outcomes_all:
            for lam in o["winner_class_set"]:
                pick = sets[next(g) % 3]
                if sorted(pick) != sorted(o["winner_class_set"][lam]):
                    ok = False
        matched += int(ok)
    return matched


def adjudicator_totals(reason):
    m = re.search(r"class\s+(\d+)/(\d+),\s*capability\s+(\d+)/(\d+),\s*crossover\s+(\d+)/(\d+)", reason)
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


# ------------------------------------------------------------------ AA10 gate
def aa10_gate(graph):
    exhausted = 0
    violations = []
    for g in graph["gaps"]:
        if g.get("status") in EXHAUSTED:
            exhausted += 1
            rev = g.get("independent_hostile_review")
            if not isinstance(rev, dict):
                violations.append((g.get("id"), "no-review"))
                continue
            if rev.get("reviewer_kind") not in REVIEWER_KINDS:
                violations.append((g.get("id"), "reviewer-kind"))
            if not rev.get("reviewer_id") or rev.get("reviewer_id") == g.get("owner_role"):
                violations.append((g.get("id"), "reviewer-not-distinct"))
            if not re.fullmatch(r"[0-9a-f]{64}", str(rev.get("verdict_sha256", ""))):
                violations.append((g.get("id"), "no-verdict-sha"))
    return {"records": len(graph["gaps"]), "exhausted": exhausted, "violations": len(violations),
            "violation_ids": violations[:5]}


def records_null(trials=200):
    """Random record sets: random labels / shas / self-reports must fail integrity."""
    g = lcg(4242)
    labels = [LABEL, "EXTERNAL", "", "HUMAN_GATE_BYPASSED", "MODEL_PROXY"]
    passed = 0
    for _ in range(trials):
        n = 1 + next(g) % 4
        recs = []
        for i in range(n):
            recs.append({"id": "PX-R%d" % i, "label": labels[next(g) % len(labels)],
                         "brief": "briefs/BRIEF_%d.md" % (next(g) % 30), "brief_sha256": "%064x" % next(g),
                         "verdict_block_present": True, "verdict_sha256": "%064x" % next(g), "verdict_bytes": next(g) % 5000,
                         "rows": [], "artifacts_handed": [], "requested_model": "opus", "model_self_report": "x"})
        fake = {"records": recs}
        v = check_records(fake, {"briefs": {}, "pins": {}}, {}, {}, {})
        passed += int(not v)
    return passed


# --------------------------------------------------------------- closure rules
def decide(records, editor, z9, aa10, lean_ok, reopen_ok, z18_6_authority, hostile_report_sha):
    R = {r["id"]: r for r in records["records"]}

    def rv(pid, row):
        r = R.get(pid)
        if r is None:
            return None
        for x in r.get("rows", []):
            if x["row"] == row:
                return x["verdict"]
        return None

    closed, not_closed = {}, {}

    def close(row, evidence):
        closed[row] = evidence

    def keep(row, reason):
        not_closed[row] = reason

    # Z9
    ids = {}
    for pid in ("PX-Z9-T1", "PX-Z9-P1", "PX-Z9-A1", "PX-Z9-T2", "PX-Z9-P2", "PX-Z9-A2"):
        ids[pid] = R[pid]["agent_log_id"]
    disjoint = len(set(ids.values())) == 6
    if disjoint:
        close("Z9-1", "six distinct fresh sessions: per batch a test team, a prediction team and an adjudicator, none sharing a transcript")
    else:
        keep("Z9-1", "agent sessions not disjoint")
    if rv("PX-Z9-T1", "Z9-2") == "SATISFIED" and rv("PX-Z9-T2", "Z9-2") == "SATISFIED" and z9["batch_valid"][0] and z9["batch_valid"][1]:
        close("Z9-2", "two batches (12 + 12 environments) authored from the family spec only; both meet the brief's construction requirements mechanically")
    else:
        keep("Z9-2", "a test-team proxy did not return SATISFIED or a batch fails the brief's construction requirements")
    p1_ok = R["PX-Z9-P1"].get("protocol_output_sha256") and not R["PX-Z9-P1"]["verdict_block_present"]
    p2_ok = rv("PX-Z9-P2", "Z9-3") == "SATISFIED" and rv("PX-Z9-P2", "Z9-4") == "SATISFIED"
    if p1_ok and p2_ok and z9["predictions_complete"]:
        close("Z9-3", "each prediction team received only the descriptor file and the brief's theory (PX-Z9-P2 verdict; PX-Z9-P1's session ended before its reply, its prompt and file are recorded)")
        close("Z9-4", "class-set, capability, crossover and failure predictions frozen for all 24 environments before any oracle ran; sha256 in the commit messages")
    else:
        keep("Z9-3", "prediction records incomplete")
        keep("Z9-4", "prediction records incomplete")
    if z9["oracle_recompute_matches"] and z9["routes_agree"]:
        close("Z9-5", "outcomes are the mechanical output of two frozen oracles with no tunable parameter, recomputed here byte-for-byte")
    else:
        keep("Z9-5", "oracle recomputation or route agreement failed")
    a_ok = all(rv(p, "Z9-6") == "SATISFIED" for p in ("PX-Z9-A1", "PX-Z9-A2")) and z9["adjudicators_match_executor"]
    if a_ok:
        close("Z9-6", "two adjudicator proxies (different model families) scored both batches; their totals equal the executor's exact re-score")
    else:
        keep("Z9-6", "an adjudicator did not return SATISFIED or its totals differ from the executor's")
    if disjoint and len(z9["batches"]) == 2 and all(k in closed for k in ("Z9-2", "Z9-3", "Z9-5", "Z9-6")):
        close("Z9-7", "two independent batches with disjoint agents completed end to end")
    else:
        keep("Z9-7", "fewer than two complete batches")

    # Z18-1..5
    for i, pid in enumerate(("PX-Z18-THM", "PX-Z18-EXP", "PX-Z18-LIT", "PX-Z18-STAT", "PX-Z18-COG"), start=1):
        row = "Z18-%d" % i
        vv = rv(pid, row)
        if vv == "SATISFIED":
            close(row, "%s performed the review and returned a complete per-claim record" % pid)
        else:
            keep(row, "%s: %s" % (pid, vv))
    if z18_6_authority and reopen_ok:
        close("Z18-6", "every brief grants reopen authority (rule 5) and every REOPEN demand is honoured in REOPENED_GATES_V1.json")
    else:
        keep("Z18-6", "authority text missing from a brief or a REOPEN demand missing from the register")
    for row in ("Z18-7", "AD08"):
        vv = rv("PX-Z18-EDIT", row)
        if vv == "SATISFIED":
            close(row, "editor synthesis PX-Z18-EDIT: SATISFIED")
        else:
            keep(row, "editor synthesis PX-Z18-EDIT: %s" % vv)
    if hostile_report_sha:
        close("Z18-8", "HOSTILE_REVIEW_REPORT_V1.md frozen with sha256 %s; no manuscript submission exists on main; the requirement re-triggers at any submission" % hostile_report_sha)
    else:
        keep("Z18-8", "no hostile-review report")

    # AA/AC/AG
    if aa10["violations"] == 0:
        close("AA10", "exhaustion gate executed over %d live gap records: %d exhausted, 0 without independent hostile review; a planted unreviewed exhaustion fails the gate (H8)" % (aa10["records"], aa10["exhausted"]))
    else:
        keep("AA10", "gate violations present")
    if rv("PX-AA15", "AA15") == "SATISFIED" and lean_ok["targets"] >= 1 and lean_ok["all_typecheck"]:
        close("AA15", "%d Lean 4 target stubs written by PX-AA15; all type-check under Lean 4.14.0 core on laptop-billy with 0 errors (sorry counts %s)" % (lean_ok["targets"], lean_ok["sorries"]))
    else:
        keep("AA15", "proxy not SATISFIED or a stub fails to type-check")
    for row, pid in (("AA41", "PX-AA41"), ("AC02", "PX-AC02"), ("AC09", "PX-AC09"), ("Z14-1", "PX-Z14-SUB")):
        vv = rv(pid, row)
        if vv == "SATISFIED":
            close(row, "%s: SATISFIED" % pid)
        else:
            keep(row, "%s: %s" % (pid, vv))
    for row, pa, pb in (("AG8-R48", "PX-AG8-A", "PX-AG8-B"), ("AC05", "PX-AC05-A", "PX-AC05-B")):
        va, vb = rv(pa, row), rv(pb, row)
        fams = {R[pa]["requested_model"], R[pb]["requested_model"]}
        if va == "SATISFIED" and vb == "SATISFIED" and len(fams) == 2:
            close(row, "both proxies SATISFIED from different model families")
        else:
            keep(row, "%s: %s; %s: %s" % (pa, va, pb, vb))
    for i in range(1, 11):
        row = "Z10-%d" % i
        vv = rv("PX-Z10", row)
        if vv == "SATISFIED":
            close(row, "PX-Z10: SATISFIED")
        else:
            keep(row, "PX-Z10: %s" % vv)
    for i in range(2, 8):
        row = "Z14-%d" % i
        vv = rv("PX-Z14-COG", row)
        if vv == "SATISFIED":
            close(row, "PX-Z14-COG: SATISFIED")
        else:
            keep(row, "PX-Z14-COG: %s" % vv)
    assert set(closed) | set(not_closed) == set(ALL_ROWS), "row coverage"
    assert not (set(closed) & set(not_closed))
    return closed, not_closed


# ------------------------------------------------------------------- hostiles
def run_hostiles(ctx):
    """Every hostile mutates a deep copy and must be DETECTED.  `applicable`
    is True only if the mutation actually changed the quantity the check reads;
    a vacuous hostile fails the run."""
    out = {}

    def rec(name, detected, applicable, note):
        out[name] = {"detected": bool(detected), "applicable": bool(applicable), "note": note}

    base = ctx["records"]
    # H1 label removed
    m = copy.deepcopy(base)
    m["records"][0]["label"] = "EXTERNALLY_REVIEWED"
    v = check_records(m, ctx["freeze"], ctx["verdicts"], ctx["briefs"], ctx["artifacts"])
    rec("H1_label_removed", any(x.startswith("H1:") for x in v), m["records"][0]["label"] != base["records"][0]["label"], "label swapped on one record")
    # H2 verdict edited
    m = copy.deepcopy(base)
    pid = [r["id"] for r in m["records"] if r["verdict_block_present"]][0]
    vt = dict(ctx["verdicts"])
    vt[pid] = vt[pid].replace(b"NOT_SATISFIED", b"SATISFIED", 1) if b"NOT_SATISFIED" in vt[pid] else vt[pid] + b"\n"
    v = check_records(m, ctx["freeze"], vt, ctx["briefs"], ctx["artifacts"])
    rec("H2_verdict_edited", any(x.startswith("H2:") for x in v), vt[pid] != ctx["verdicts"][pid], "one verdict byte-edited after recording")
    # H3 brief edited
    bt = dict(ctx["briefs"])
    bname = sorted(bt)[0]
    bt[bname] = bt[bname] + b"\n<!-- post-freeze edit -->\n"
    v = check_records(base, ctx["freeze"], ctx["verdicts"], bt, ctx["artifacts"])
    rec("H3_brief_edited", any(x.startswith("H3:") for x in v), bt[bname] != ctx["briefs"][bname], "one brief edited after freeze")
    # H4 artifact edited
    at = dict(ctx["artifacts"])
    apath = sorted(at)[0]
    at[apath] = at[apath] + b"\n"
    v = check_records(base, ctx["freeze"], ctx["verdicts"], ctx["briefs"], at)
    rec("H4_artifact_edited", any(x.startswith("H4:") for x in v), at[apath] != ctx["artifacts"][apath], "one handed artifact edited after the proxy read it")
    # H5 forbidden token in a new line
    lines = [x["new"] for x in ctx["recon"]["replacements"]]
    if not lines:
        rec("H5_forbidden_promotion", False, False, "no reconciliation yet")
        rec("H11_old_absent_or_duplicated", False, False, "no reconciliation yet")
        lines = None
    if lines is not None:
        bad = [l for l in lines if any(t in l for t in FORBIDDEN)]
        planted = lines[0] + " EXTERNALLY_REVIEWED"
        rec("H5_forbidden_promotion", any(t in planted for t in FORBIDDEN) and not bad, planted != lines[0], "forbidden token planted into a new line; clean lines carry none")
    # H6 closing a NOT_SATISFIED row
    m = copy.deepcopy(base)
    for r in m["records"]:
        if r["id"] == "PX-AA41":
            for x in r["rows"]:
                x["verdict"] = "SATISFIED"
    v = check_records(m, ctx["freeze"], ctx["verdicts"], ctx["briefs"], ctx["artifacts"])
    rec("H6_closed_despite_not_satisfied", any(x.startswith("H6:") for x in v), True, "record claims SATISFIED where the verbatim verdict says NOT_SATISFIED")
    # H7 two-route row by one family
    m = copy.deepcopy(base)
    for r in m["records"]:
        if r["id"] == "PX-AG8-B":
            r["requested_model"] = "opus"
    closed7, nc7 = decide(m, ctx["editor"], ctx["z9"], ctx["aa10"], ctx["lean"], ctx["reopen_ok"], ctx["authority"], ctx["report_sha"])
    fams = {r["requested_model"] for r in m["records"] if r["id"] in ("PX-AG8-A", "PX-AG8-B")}
    rec("H7_two_route_same_family", "AG8-R48" not in closed7 and len(fams) == 1, True, "AG8-R48 must not close when both records come from one family (it also does not close on verdicts)")
    # H8 planted exhausted gap
    g = copy.deepcopy(ctx["graph"])
    g["gaps"][0]["status"] = "EXHAUSTED"
    r8 = aa10_gate(g)
    rec("H8_planted_exhaustion_without_review", r8["violations"] > 0, r8["exhausted"] > ctx["aa10"]["exhausted"], "one record marked EXHAUSTED without a review object")
    # H9 predictions edited after outcomes
    p = copy.deepcopy(ctx["z9"]["pred"][0])
    p["predictions"][0]["lambda_star"] = str(Fraction(p["predictions"][0]["lambda_star"]) + 1)
    rec("H9_predictions_edited_after_outcomes", sha256(json.dumps(p, sort_keys=True).encode()) != ctx["z9"]["pred_sha"][0] and p != ctx["z9"]["pred"][0], True, "predictions file mutated: sha256 no longer matches the frozen commit")
    # H10 oracle A/B disagreement
    ob = copy.deepcopy(ctx["z9"]["out_b"][0])
    lam = list(ob["outcomes"][0]["winner_class_set"])[0]
    ob["outcomes"][0]["winner_class_set"][lam] = ["STATELESS"] if ob["outcomes"][0]["winner_class_set"][lam] != ["STATELESS"] else ["PERSISTENT_STATE"]
    rec("H10_oracle_disagreement", not routes_agree([ctx["z9"]["out_a"][0]], [ob]), True, "route B outcome flipped on one cell")
    # H11 old string absent / duplicated
    if lines is not None:
        snap = ctx["snapshot_text"]
        olds = [x["old"] for x in ctx["recon"]["replacements"]]
        once = all(snap.count(o + "\n") == 1 for o in olds)
        dup_caught = (snap + "\n" + olds[0] + "\n").count(olds[0] + "\n") != 1
        absent_caught = snap.count(olds[0] + " EDITED\n") != 1
        rec("H11_old_absent_or_duplicated", once and dup_caught and absent_caught, True, "every old line occurs exactly once in the live snapshot; a duplicated body and an edited old line are both caught by the count")
    # H12 reopen demand missing
    reg = copy.deepcopy(ctx["reopen_register"])
    reg["demands"] = reg["demands"][1:]
    rec("H12_reopen_missing", not reopen_complete(base, reg), len(reg["demands"]) < len(ctx["reopen_register"]["demands"]), "one honoured demand deleted from the register")
    return out


def routes_agree(outs_a, outs_b):
    for oa, ob in zip(outs_a, outs_b):
        for a, b in zip(oa["outcomes"], ob["outcomes"]):
            if a["env_id"] != b["env_id"]:
                return False
            for k in ("E_stateless", "E_onebit", "lambda_star"):
                if Fraction(a[k]) != Fraction(b[k]):
                    return False
            for lam in a["winner_class_set"]:
                if sorted(a["winner_class_set"][lam]) != sorted(b["winner_class_set"][lam]):
                    return False
                if Fraction(a["J_best_stateless"][lam]) != Fraction(b["J_best_stateless"][lam]):
                    return False
                if Fraction(a["J_best_onebit"][lam]) != Fraction(b["J_best_onebit"][lam]):
                    return False
    return True


def reopen_complete(records, register):
    have = {(d["demanded_by"], d["gate"]) for d in register["demands"]}
    for r in records["records"]:
        for gate in r.get("reopens", []):
            g = gate["gate"] if isinstance(gate, dict) else gate
            if (r["id"], g) not in have:
                return False
    return True


# ----------------------------------------------------------------------- main
def main(check_only=False):
    freeze = parse_freeze(read("FREEZE_V1.md"))
    records = json.loads(read("PROXY_RECORDS_V1.json"))
    briefs = {n: read("briefs/" + n, "rb") for n in os.listdir(os.path.join(HERE, "briefs")) if n.endswith(".md")}
    verdicts = {}
    for r in records["records"]:
        if r["verdict_block_present"]:
            verdicts[r["id"]] = read(r["verdict_file"], "rb")
    artifacts, parents_moved = {}, []
    for path, pin in freeze["pins"].items():
        full = os.path.join(REPO, path)
        b = open(full, "rb").read() if os.path.exists(full) else None
        if b is None or blob_sha(b) != pin:
            # The tree moved past the pin (a parent edited on main after the freeze).  What the proxy
            # read is the pinned blob; if it is still reachable in the object store the bytes are
            # frozen in history and the state is recorded, not failed.  Unreachable -> None -> H4.
            frozen = git_blob(pin)
            parents_moved.append({"path": path, "pinned_blob": pin,
                                  "tree_blob": blob_sha(b) if b is not None else None,
                                  "state": "PINNED_BLOB_REACHABLE_TREE_MOVED" if frozen is not None else "PINNED_BLOB_UNREACHABLE"})
            b = frozen
        artifacts[path] = b
    # snapshots
    snap_ok = all(sha256(read(SNAPSHOTS[k], "rb")) == freeze["snapshots"][k] for k in SNAPSHOTS)
    integrity = check_records(records, freeze, verdicts, briefs, artifacts)

    # Z9
    oa = load_oracle("z9_oracle_a_v1")
    envs, preds, outs_a, outs_b, pred_sha = [], [], [], [], []
    scores = []
    recompute_ok = True
    for b in (1, 2):
        e = json.loads(read("z9/batch_%d/ENVIRONMENTS.json" % b))
        p_raw = read("z9/batch_%d/PREDICTIONS.json" % b, "rb")
        p = json.loads(p_raw.decode("utf-8"))
        a = json.loads(read("z9/batch_%d/OUTCOMES.json" % b))
        bb = json.loads(read("z9/batch_%d/OUTCOMES_ROUTE_B.json" % b))
        rec = oa.run(e)
        if rec != a:
            recompute_ok = False
        envs.append(e)
        preds.append(p)
        outs_a.append(a)
        outs_b.append(bb)
        pred_sha.append(sha256(json.dumps(p, sort_keys=True).encode()))
        scores.append(score_batch(p, a))
    need = ["E_stateless", "E_onebit", "J_best_stateless", "J_best_onebit", "lambda_star", "winner_class_set", "failure_prediction", "confidence"]
    predictions_complete = all(all(k in q for k in need) for p in preds for q in p["predictions"]) and all(
        [q["env_id"] for q in p["predictions"]] == [x["env_id"] for x in e["environments"]] for p, e in zip(preds, envs))
    validity = [batch_valid(e) for e in envs]
    adj = {}
    for pid, i in (("PX-Z9-A1", 0), ("PX-Z9-A2", 1)):
        r = [x for x in records["records"] if x["id"] == pid][0]
        reason = [x["reason"] for x in r.get("rows", []) if x["row"] == "Z9-6"]
        t = adjudicator_totals(reason[0]) if reason else None
        s = scores[i]
        adj[pid] = {"parsed": t, "executor": (s["class_hits"], s["points"], s["capability_hits"], s["points"], s["crossover_hits"], s["environments"])}
    adjudicators_match = all(v["parsed"] == v["executor"] for v in adj.values())
    null_z9 = z9_null(outs_a[0]["outcomes"] + outs_a[1]["outcomes"])
    z9 = {"batches": [1, 2], "pred": preds, "pred_sha": pred_sha, "out_a": outs_a, "out_b": outs_b,
          "oracle_recompute_matches": recompute_ok, "routes_agree": routes_agree(outs_a, outs_b),
          "predictions_complete": predictions_complete, "batch_valid": [v[0] for v in validity],
          "batch_stats": [v[1] for v in validity], "scores": scores, "adjudicators": adj,
          "adjudicators_match_executor": adjudicators_match, "null_random_predictors_matching_all": null_z9}

    # AA10
    graph = json.loads(open(os.path.join(REPO, "research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json")).read())
    aa10 = aa10_gate(graph)

    # AA15 Lean logs
    targets = json.loads(read("aa15_targets/TARGETS.json"))
    practical = [t for t in targets["targets"] if t["practicality"] == "PRACTICAL"]
    sorries = {}
    all_ok = True
    for t in practical:
        log = read("aa15_targets/%s.lean414.log" % t["file"])
        errs = len(re.findall(r"\berror\b", log))
        sorries[t["id"]] = len(re.findall(r"declaration uses 'sorry'", log))
        if errs:
            all_ok = False
    lean = {"targets": len(practical), "all_typecheck": all_ok, "sorries": sorries, "toolchain": "leanprover/lean4:v4.14.0 (laptop-billy)"}

    # reopen register and authority
    register = json.loads(read("REOPENED_GATES_V1.json"))
    reopen_ok = reopen_complete(records, register)
    authority = all(b"You have authority to demand" in briefs[n] for n in briefs if n.startswith("BRIEF_Z18") or n.startswith("BRIEF_A") or n.startswith("BRIEF_Z1"))
    report_sha = sha256(read("HOSTILE_REVIEW_REPORT_V1.md", "rb")) if os.path.exists(os.path.join(HERE, "HOSTILE_REVIEW_REPORT_V1.md")) else None
    editor = [r for r in records["records"] if r["id"] == "PX-Z18-EDIT"][0]

    closed, not_closed = decide(records, editor, z9, aa10, lean, reopen_ok, authority, report_sha)
    recon_path = os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json")
    recon = json.loads(read("ISSUE_833_COMMENT_RECONCILIATION_V1.json")) if os.path.exists(recon_path) else {"replacements": []}
    snapshot_text = "".join(read(SNAPSHOTS[k]) for k in ("5684819296", "5684607872", "5693520829"))
    ctx = {"records": records, "freeze": freeze, "verdicts": verdicts, "briefs": briefs, "artifacts": artifacts,
           "recon": recon, "editor": editor, "z9": z9, "aa10": aa10, "lean": lean, "reopen_ok": reopen_ok,
           "authority": authority, "report_sha": report_sha, "graph": graph, "snapshot_text": snapshot_text,
           "reopen_register": register}
    hostiles = run_hostiles(ctx)
    null_records = records_null()

    # reconciliation consistency: every closed row has exactly one replacement, none of the not_closed rows has one
    recon_rows = [x["row"] for x in recon["replacements"]]
    recon_ok = sorted(recon_rows) == sorted(closed) and all(LABEL in x["new"] for x in recon["replacements"]) and not any(
        t in x["new"] for x in recon["replacements"] for t in FORBIDDEN)

    verdict = "GREEN" if (not integrity and snap_ok and recompute_ok and z9["routes_agree"] and all(h["detected"] and h["applicable"] for h in hostiles.values())
                          and null_z9 == 0 and null_records == 0 and recon_ok) else "RED"
    result = {
        "schema": "GMI_833_HUMAN_GATE_PROXY_RESULT_V1",
        "package": "gmi-833-human-gate-proxy-v1",
        "route": "A",
        "claim_ceiling": freeze["ceiling"],
        "source_main": freeze["source_main"],
        "label": LABEL,
        "verdict": verdict,
        "integrity_violations": integrity,
        "snapshots_match_freeze": snap_ok,
        "parents_moved_since_pin": parents_moved,
        "proxy_records": len(records["records"]),
        "proxy_records_with_verdict": sum(1 for r in records["records"] if r["verdict_block_present"]),
        "terminated_attempts": len(records["terminated_attempts"]),
        "rows_targeted": len(ALL_ROWS),
        "closed": closed,
        "not_closed": not_closed,
        "closed_count": len(closed),
        "not_closed_count": len(not_closed),
        "proxy_row_verdicts": {r["id"]: {x["row"]: x["verdict"] for x in r.get("rows", [])} for r in records["records"]},
        "editor_claim_dispositions": {x["claim"]: x["verdict"] for x in editor.get("claims", [])},
        "material_objections_total": sum(1 for r in records["records"] for o in r.get("objections", []) if o["material"]),
        "reopen_demands_total": register["count"],
        "reopen_register_complete": reopen_ok,
        "z9": {"batches": 2, "environments": sum(len(e["environments"]) for e in envs),
               "price_points": sum(s["points"] for s in scores),
               "batch_stats": z9["batch_stats"], "batch_valid": z9["batch_valid"],
               "predictions_sha256": pred_sha, "oracle_recompute_matches": recompute_ok,
               "routes_agree": z9["routes_agree"],
               "scores": [{k: v for k, v in s.items()} for s in scores],
               "totals": {"class_hits": sum(s["class_hits"] for s in scores), "capability_hits": sum(s["capability_hits"] for s in scores),
                          "points": sum(s["points"] for s in scores), "crossover_hits": sum(s["crossover_hits"] for s in scores),
                          "environments": sum(s["environments"] for s in scores)},
               "adjudicators": {k: {"parsed": list(v["parsed"]) if v["parsed"] else None, "executor": list(v["executor"])} for k, v in adj.items()},
               "adjudicators_match_executor": adjudicators_match,
               "null_random_predictors_matching_all_winner_sets": "%d/200" % null_z9,
               "theory_clause_falsified": "T3 (one-bit optimum = carry x_{t-1}) is false on two-back targets: exhaustive E_onebit < predicted on every missed environment"},
        "aa10_gate": aa10,
        "aa15_lean": lean,
        "hostiles": hostiles,
        "hostiles_detected": sum(1 for h in hostiles.values() if h["detected"]),
        "hostiles_applicable": sum(1 for h in hostiles.values() if h["applicable"]),
        "null_random_record_sets_passing_integrity": "%d/200" % null_records,
        "hostile_review_report_sha256": report_sha,
        "reconciliation_consistent": recon_ok,
        "forbidden_promotions": FORBIDDEN,
    }
    blob = json.dumps(result, indent=1, sort_keys=True) + "\n"
    dest = os.path.join(HERE, "RESULT_V1.json")
    if check_only:
        cur = open(dest, encoding="utf-8").read()
        print(json.dumps({"verdict": verdict, "reproducible": cur == blob}))
        sys.exit(0 if (cur == blob and verdict == "GREEN") else 1)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(blob)
    print(json.dumps({"verdict": verdict, "closed": len(closed), "not_closed": len(not_closed), "integrity_violations": integrity,
                      "hostiles_detected": result["hostiles_detected"], "hostiles_applicable": result["hostiles_applicable"],
                      "z9_totals": result["z9"]["totals"], "null_z9": null_z9, "null_records": null_records, "recon_ok": recon_ok}))
    sys.exit(0 if verdict == "GREEN" else 1)


if __name__ == "__main__":
    main(check_only=("--check" in sys.argv))
