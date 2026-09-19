#!/usr/bin/env python3
"""Assemble PROXY_RECORDS_V1.json from PROXY_META_V1.json (lane-entered spawn
metadata), the verbatim verdict transcripts under proxies/, the artifact lists in
the frozen briefs and the artifact pins in FREEZE_V1.md.  Every stored row/claim
field is parsed from the transcript, so the executor's integrity check
(stored == transcript) holds by construction and any later edit of a transcript
breaks the recorded sha256.  Stdlib only."""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location("hgp", os.path.join(HERE, "human_gate_proxy_v1.py"))
hgp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hgp)

ROOT_PREFIX = "/Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/"


def brief_artifacts(brief_rel):
    text = open(os.path.join(HERE, brief_rel), encoding="utf-8").read()
    paths = re.findall(r"(?:^|\s)-\s+(" + re.escape(ROOT_PREFIX) + r"[^\s`]+)", text)
    extra = re.findall(r"(" + re.escape(ROOT_PREFIX) + r"research/[^\s`,)]+)", text)
    rels = []
    for p in paths + extra:
        r = p[len(ROOT_PREFIX):]
        if r not in rels and os.path.exists(os.path.join(hgp.REPO, r)):
            rels.append(r)
    return rels


def main():
    meta = json.load(open(os.path.join(HERE, "PROXY_META_V1.json")))
    pins = hgp.freeze_artifact_pins()
    briefs = hgp.freeze_brief_digests()
    records = []
    for m in meta["proxies"]:
        vf = "proxies/%s.verdict.txt" % m["id"]
        text = open(os.path.join(HERE, vf), encoding="utf-8").read()
        parsed = hgp.parse_verdict_block(text)
        if parsed is None:
            raise SystemExit("no verdict block in " + vf)
        arts = {}
        inputs = {}
        for rel in brief_artifacts(m["brief"]):
            if rel.startswith("research/gmi-833-human-gate-proxy-v1/"):
                inputs[rel[len("research/gmi-833-human-gate-proxy-v1/"):]] = hgp.sha256_file(os.path.join(hgp.REPO, rel))
            elif rel in pins:
                arts[rel] = pins[rel]
            else:
                raise SystemExit("artifact not pinned in freeze: " + rel)
        for rel in m.get("extra_inputs", []):
            inputs[rel] = hgp.sha256_file(os.path.join(HERE, rel))
        rec = {
            "id": m["id"], "role": m["role"], "brief": m["brief"], "brief_sha256": briefs[m["brief"]][0],
            "artifacts": arts, "inputs_sha256": inputs,
            "model_requested": m["model_requested"], "model_served_per_transcript": m["model_served"],
            "model_self_report": parsed["model_self_report"],
            "agent_tool": "Agent(general-purpose, run_in_background)", "spawned_after_freeze_commit": meta["freeze_commit"],
            "started_utc": m["started_utc"], "finished_utc": m["finished_utc"],
            "verdict_file": vf, "verdict_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "verdict_bytes": len(text.encode("utf-8")),
            "rows": parsed["rows"], "claims": parsed["claims"], "objections": parsed["objections"],
            "reopen_demands": parsed["reopen"], "label": hgp.LABEL,
            "isolation_note": meta["isolation_note"],
        }
        records.append(rec)
    doc = {"schema": "GMI_833_PROXY_RECORDS_V1", "issue": 833, "label": hgp.LABEL,
           "source_main": meta["source_main"], "freeze_commit": meta["freeze_commit"],
           "records": records, "z9_protocol": meta.get("z9_protocol", {"batches": []}),
           "lean_check": meta.get("lean_check", {}), "hostile_review_report": meta.get("hostile_review_report", {}),
           "aa10_gate_wired": True}
    with open(os.path.join(HERE, "PROXY_RECORDS_V1.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False); fh.write("\n")
    print(json.dumps({"records": len(records), "ids": [r["id"] for r in records]}))


if __name__ == "__main__":
    main()
