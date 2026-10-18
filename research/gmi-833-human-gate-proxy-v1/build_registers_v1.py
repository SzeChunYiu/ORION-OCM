#!/usr/bin/env python3
"""Build REOPENED_GATES_V1.json from every proxy verdict in proxies/.

Every `reopen:` line inside a VERDICT_BLOCK is a REOPEN demand.  Each demand is
honoured verbatim: the gate is recorded as reopened, attributed to the proxy that
demanded it, with the proxy's reason and the verdict file's sha256.  Nothing is
filtered, merged or softened; the same gate demanded by several proxies appears
once per demand.  Deterministic (sorted), stdlib only, python3.8.
"""
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LABEL = "HUMAN_GATE_BYPASSED__MODEL_PROXY"


def verdict_block(text):
    m = re.search(r"VERDICT_BLOCK_BEGIN\n(.*?)VERDICT_BLOCK_END", text, re.S)
    if not m:
        return None
    return m.group(1)


def parse_reopens(block):
    out = []
    for line in block.splitlines():
        if not line.startswith("reopen:"):
            continue
        body = line[len("reopen:"):]
        if "| reason:" in body:
            gate, reason = body.split("| reason:", 1)
        else:
            gate, reason = body, ""
        out.append((gate.strip(), reason.strip()))
    return out


def build():
    demands = []
    for path in sorted(glob.glob(os.path.join(HERE, "proxies", "*.verdict.txt"))):
        pid = os.path.basename(path)[: -len(".verdict.txt")]
        raw = open(path, "rb").read()
        block = verdict_block(raw.decode("utf-8"))
        if block is None:
            raise SystemExit("no verdict block in %s" % path)
        sha = hashlib.sha256(raw).hexdigest()
        for gate, reason in parse_reopens(block):
            demands.append({
                "gate": gate,
                "demanded_by": pid,
                "reviewer_kind": LABEL,
                "verdict_file": "proxies/%s.verdict.txt" % pid,
                "verdict_sha256": sha,
                "reason": reason,
                "status": "REOPENED_BY_PROXY_DEMAND",
            })
    demands.sort(key=lambda d: (d["demanded_by"], d["gate"]))
    return {
        "schema": "GMI_833_REOPENED_GATES_V1",
        "package": "gmi-833-human-gate-proxy-v1",
        "rule": "Every REOPEN demand in every proxy verdict block is honoured verbatim. "
                "A reopened gate stays reopened until the owning package lands a numbered "
                "supplement or amendment that answers the recorded reason; this package "
                "closes none of them.",
        "reviewer_authority_source": "rule 5 of every brief under briefs/",
        "count": len(demands),
        "distinct_demanders": sorted({d["demanded_by"] for d in demands}),
        "demands": demands,
    }


def sweep_findings():
    """Every SWEEP-<n> id PX-AA41 named, one record each: the first paragraph
    that carries the id in bold or with its materiality tag is the finding text.
    Completeness is by id set: every id in the report appears here."""
    raw = open(os.path.join(HERE, "proxies", "PX-AA41.verdict.txt"), encoding="utf-8").read()
    paras = [p.strip() for p in raw.split("\n") if p.strip()]
    ids = sorted({int(x) for x in re.findall(r"SWEEP-(\d+)", raw)})
    items = []
    for n in ids:
        pick = None
        for para in paras:
            if re.search(r"\*\*SWEEP-%d\b" % n, para) or re.search(r"SWEEP-%d \(" % n, para):
                pick = para
                break
        if pick is None:
            pick = [para for para in paras if re.search(r"SWEEP-%d\b" % n, para)][0]
        tag = re.search(r"SWEEP-%d\*? \(material(?::\s*(yes|no))?\)" % n, pick)
        material = True if tag is None else (tag.group(1) or "yes") == "yes"
        registered = ("Not registered" not in pick) or ("Registered elsewhere" in pick)
        items.append({"id": "SWEEP-%d" % n, "material": material, "registered_in_artifacts": registered, "text": pick})
    return {"schema": "GMI_833_SWEEP_FINDINGS_V1", "source": "proxies/PX-AA41.verdict.txt",
            "source_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "verdict_AA41": "NOT_SATISFIED", "ids_named_in_report": len(ids), "count": len(items),
            "material": sum(1 for x in items if x["material"]),
            "not_registered_anywhere": sum(1 for x in items if not x["registered_in_artifacts"]),
            "findings": items,
            "rule": "every descendant gap the sweep named is listed; none is closed by this package"}


def hostile_report():
    """Compile the frozen hostile-review report from the verbatim verdict blocks."""
    order = ["PX-Z18-THM", "PX-Z18-EXP", "PX-Z18-LIT", "PX-Z18-STAT", "PX-Z18-COG", "PX-Z18-EDIT",
             "PX-AA41", "PX-AA15", "PX-AG8-A", "PX-AG8-B", "PX-AC02", "PX-AC05-A", "PX-AC05-B", "PX-AC09",
             "PX-Z10", "PX-Z14-SUB", "PX-Z14-COG", "PX-Z9-T1", "PX-Z9-T2", "PX-Z9-P2", "PX-Z9-A1", "PX-Z9-A2"]
    out = ["# HOSTILE_REVIEW_REPORT_V1 — gmi-833-human-gate-proxy-v1", "",
           "Compiled mechanically from the verbatim verdict blocks under `proxies/` (sha256 per file below).",
           "Every reviewer is a fresh-session model proxy labelled `HUMAN_GATE_BYPASSED__MODEL_PROXY`;",
           "this is not an external or human review. The report is frozen by its sha256 in RESULT_V1.json;",
           "the requirement to freeze a hostile-review report re-triggers at any manuscript submission,",
           "and no manuscript submission exists on `main`. Editor dispositions and the authors' responses",
           "are in `RESPONSES_V1.md`, `CLAIM_DOWNGRADES_V1.json`, `REOPENED_GATES_V1.json`.", ""]
    for pid in order:
        path = os.path.join(HERE, "proxies", pid + ".verdict.txt")
        if not os.path.exists(path):
            continue
        raw = open(path, "rb").read()
        block = verdict_block(raw.decode("utf-8"))
        out.append("## %s  (sha256 `%s`)" % (pid, hashlib.sha256(raw).hexdigest()))
        out.append("")
        out.append("```")
        out.extend(block.rstrip("\n").split("\n"))
        out.append("```")
        out.append("")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    reg = build()
    sw = sweep_findings()
    rep = hostile_report()
    sw_dest = os.path.join(HERE, "SWEEP_FINDINGS_V1.json")
    rep_dest = os.path.join(HERE, "HOSTILE_REVIEW_REPORT_V1.md")
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        if json.load(open(sw_dest)) != sw:
            print("SWEEP_FINDINGS_V1.json is stale")
            sys.exit(1)
        if open(rep_dest, encoding="utf-8").read() != rep:
            print("HOSTILE_REVIEW_REPORT_V1.md is stale")
            sys.exit(1)
    else:
        with open(sw_dest, "w", encoding="utf-8") as fh:
            json.dump(sw, fh, indent=1, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
        with open(rep_dest, "w", encoding="utf-8") as fh:
            fh.write(rep)
    dest = os.path.join(HERE, "REOPENED_GATES_V1.json")
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        cur = json.load(open(dest))
        if cur != reg:
            print("REOPENED_GATES_V1.json is stale")
            sys.exit(1)
        print(json.dumps({"reopened_gates": reg["count"], "check": "fresh"}))
        sys.exit(0)
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"reopened_gates": reg["count"], "demanders": len(reg["distinct_demanders"])}))
