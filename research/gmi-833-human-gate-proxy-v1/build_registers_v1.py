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


if __name__ == "__main__":
    reg = build()
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
