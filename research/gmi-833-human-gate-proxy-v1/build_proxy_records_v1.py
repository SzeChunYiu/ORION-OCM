#!/usr/bin/env python3
"""Assemble PROXY_RECORDS_V1.json — one record per model proxy spawned under
FREEZE_V1.md section 4, plus every terminated attempt.

Inputs (all on the lane machine; the harness transcripts never enter git):
  argv[1]  recovered_records.json — per-proxy facts extracted from the harness
           transcripts (agent log id, requested and served model, timestamps,
           files written, whether the reply carried a VERDICT_BLOCK).
The verdict text itself is read from proxies/<ID>.verdict.txt, byte-exact, and
never edited.  Stdlib only, python3.8, deterministic output.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LABEL = "HUMAN_GATE_BYPASSED__MODEL_PROXY"

# proxy id -> (brief, rows the freeze table assigns, model family requested)
TABLE = {
    "PX-Z18-THM": ("BRIEF_Z18_THEOREM_REVIEWER.md", ["Z18-1"], "opus"),
    "PX-Z18-EXP": ("BRIEF_Z18_EXPERIMENTAL_METHOD_REVIEWER.md", ["Z18-2"], "opus"),
    "PX-Z18-LIT": ("BRIEF_Z18_PARENT_LITERATURE_REVIEWER.md", ["Z18-3"], "opus"),
    "PX-Z18-STAT": ("BRIEF_Z18_STATISTICS_CAUSAL_REVIEWER.md", ["Z18-4"], "opus"),
    "PX-Z18-COG": ("BRIEF_Z18_COGNITIVE_SCIENCE_REVIEWER.md", ["Z18-5"], "opus"),
    "PX-Z18-EDIT": ("BRIEF_Z18_EDITOR_SYNTHESIS.md", ["Z18-7", "AD08"], "opus"),
    "PX-AA41": ("BRIEF_AA41_RECURSIVE_HOSTILE_SWEEP.md", ["AA41"], "opus"),
    "PX-AA15": ("BRIEF_AA15_FORMAL_TARGETS.md", ["AA15"], "opus"),
    "PX-AG8-A": ("BRIEF_AG8_R48_FOUNDATIONS_REVIEW.md", ["AG8-R48"], "opus"),
    "PX-AG8-B": ("BRIEF_AG8_R48_FOUNDATIONS_REVIEW.md", ["AG8-R48"], "sonnet"),
    "PX-AC05-A": ("BRIEF_AC05_CITATION_VERIFICATION.md", ["AC05"], "opus"),
    "PX-AC05-B": ("BRIEF_AC05_CITATION_VERIFICATION.md", ["AC05"], "sonnet"),
    "PX-AC02": ("BRIEF_AC02_PARENT_LITERATURE_COLLECTION.md", ["AC02"], "opus"),
    "PX-AC09": ("BRIEF_AC09_LITERATURE_RERUN.md", ["AC09"], "opus"),
    "PX-Z10": ("BRIEF_Z10_REAL_SYSTEM_REVIEW.md", ["Z10-%d" % i for i in range(1, 11)], "opus"),
    "PX-Z14-SUB": ("BRIEF_Z14_CROSS_SUBSTRATE_REVIEW.md", ["Z14-1"], "opus"),
    "PX-Z14-COG": ("BRIEF_Z14_NATURAL_COGNITION_REVIEW.md", ["Z14-%d" % i for i in range(2, 8)], "opus"),
    "PX-Z9-T1": ("BRIEF_Z9_TEST_TEAM.md", ["Z9-2"], "sonnet"),
    "PX-Z9-T2": ("BRIEF_Z9_TEST_TEAM.md", ["Z9-2"], "opus"),
    "PX-Z9-P1": ("BRIEF_Z9_PREDICTION_TEAM.md", ["Z9-3", "Z9-4"], "opus"),
    "PX-Z9-P2": ("BRIEF_Z9_PREDICTION_TEAM.md", ["Z9-3", "Z9-4"], "sonnet"),
    "PX-Z9-A1": ("BRIEF_Z9_ADJUDICATOR.md", ["Z9-6"], "sonnet"),
    "PX-Z9-A2": ("BRIEF_Z9_ADJUDICATOR.md", ["Z9-6"], "opus"),
}
Z9_BATCH = {"PX-Z9-T1": 1, "PX-Z9-P1": 1, "PX-Z9-A1": 1, "PX-Z9-T2": 2, "PX-Z9-P2": 2, "PX-Z9-A2": 2}
Z9_OUTPUT = {"PX-Z9-T1": "z9/batch_1/ENVIRONMENTS.json", "PX-Z9-T2": "z9/batch_2/ENVIRONMENTS.json",
             "PX-Z9-P1": "z9/batch_1/PREDICTIONS.json", "PX-Z9-P2": "z9/batch_2/PREDICTIONS.json"}

# harness attempts that ended before a reply (session limit); recorded, never hidden
TERMINATED = [
    {"proxy": "PX-Z9-P1", "agent_log_id": "ac205a3e75b90a8bf", "requested_model": "opus",
     "served_models": ["claude-opus-5"], "what_happened":
     "wrote z9/batch_1/PREDICTIONS.json in full, then the harness ended the session before the reply; "
     "the file is used verbatim as the frozen prediction and the VERDICT_BLOCK is absent",
     "resolution": "not re-run (a second prediction set for the same batch would let the lane choose); "
                   "rows Z9-3/Z9-4 for batch 1 are decided by the executor from the file and the git order"},
    {"proxy": "PX-AC05-A", "agent_log_id": "a8a3fd6cb3eb17059", "requested_model": "opus",
     "served_models": ["claude-opus-5"], "what_happened": "session ended after 30 tool calls, no reply",
     "resolution": "a fresh session was spawned against the same brief; the first attempt produced no verdict"},
    {"proxy": "PX-Z9-P2", "agent_log_id": "aed9821dbe1ebb953", "requested_model": "sonnet",
     "served_models": [], "what_happened": "session ended before any tool call",
     "resolution": "a fresh session was spawned against the same brief; the first attempt produced nothing"},
]


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def parse_block(text):
    m = re.search(r"VERDICT_BLOCK_BEGIN\n(.*?)VERDICT_BLOCK_END", text, re.S)
    if not m:
        return None
    rows, claims, objections, reopens, selfrep = [], [], [], [], None
    for line in m.group(1).splitlines():
        if line.startswith("row:"):
            mm = re.match(r"row:\s*(\S+)\s*\|\s*verdict:\s*(\S+)\s*\|\s*reason:\s*(.*)$", line)
            if mm:
                rows.append({"row": mm.group(1), "verdict": mm.group(2), "reason": mm.group(3).strip()})
        elif line.startswith("claim:"):
            mm = re.match(r"claim:\s*(\S+)\s*\|\s*verdict:\s*(\S+)\s*\|\s*reason:\s*(.*)$", line)
            if mm:
                claims.append({"claim": mm.group(1), "verdict": mm.group(2), "reason": mm.group(3).strip()})
        elif line.startswith("objection:"):
            mm = re.match(r"objection:\s*(.+?)\s*\|(?:\s*claim:\s*(\S+)\s*\|)?\s*material:\s*(\S+)\s*\|\s*text:\s*(.*)$", line)
            if mm:
                objections.append({"id": mm.group(1), "claim": mm.group(2), "material": mm.group(3) == "yes",
                                   "text": mm.group(4).strip()})
        elif line.startswith("reopen:"):
            body = line[len("reopen:"):]
            gate, _, reason = body.partition("| reason:")
            reopens.append({"gate": gate.strip(), "reason": reason.strip()})
        elif line.startswith("model_self_report:"):
            selfrep = line[len("model_self_report:"):].strip()
    return {"rows": rows, "claims": claims, "objections": objections, "reopens": reopens,
            "model_self_report": selfrep}


def brief_artifacts(brief_path):
    out = []
    for line in open(brief_path, encoding="utf-8"):
        for m in re.finditer(r"/Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/(research/[A-Za-z0-9_./-]+)", line):
            p = m.group(1)
            if p not in out:
                out.append(p)
    return out


def main(recovered_path):
    rec = json.load(open(recovered_path))
    records = []
    for pid in sorted(TABLE):
        brief, rows, family = TABLE[pid]
        r = rec.get(pid)
        if r is None:
            raise SystemExit("no recovered facts for %s" % pid)
        entry = {
            "id": pid,
            "label": LABEL,
            "brief": "briefs/" + brief,
            "brief_sha256": sha256_file(os.path.join(HERE, "briefs", brief)),
            "rows_assigned": rows,
            "requested_model": family,
            "served_models": r["served_models"],
            "agent_log_id": r["agent_log_id"],
            "first_ts": r["first_ts"],
            "last_ts": r["last_ts"],
            "tool_calls": r["tool_calls"],
            "artifacts_handed": brief_artifacts(os.path.join(HERE, "briefs", brief)),
            "isolation": "fresh session; instructed to read only the brief and the artifacts it lists; "
                         "received no lane reasoning, no freeze, no checklist",
        }
        if pid in Z9_BATCH:
            entry["z9_batch"] = Z9_BATCH[pid]
        if pid in Z9_OUTPUT:
            entry["protocol_output"] = Z9_OUTPUT[pid]
            entry["protocol_output_sha256"] = sha256_file(os.path.join(HERE, Z9_OUTPUT[pid]))
        vf = os.path.join(HERE, "proxies", pid + ".verdict.txt")
        if os.path.exists(vf):
            text = open(vf, "rb").read()
            parsed = parse_block(text.decode("utf-8"))
            if parsed is None:
                raise SystemExit("verdict file without block: %s" % vf)
            entry["verdict_file"] = "proxies/%s.verdict.txt" % pid
            entry["verdict_sha256"] = hashlib.sha256(text).hexdigest()
            entry["verdict_bytes"] = len(text)
            entry["verdict_block_present"] = True
            entry.update(parsed)
        else:
            entry["verdict_block_present"] = False
            entry["rows"] = []
            entry["claims"] = []
            entry["objections"] = []
            entry["reopens"] = []
            entry["model_self_report"] = None
            entry["harness_synthetic_termination"] = bool(r.get("harness_synthetic_termination"))
        records.append(entry)
    out = {
        "schema": "GMI_833_PROXY_RECORDS_V1",
        "package": "gmi-833-human-gate-proxy-v1",
        "label": LABEL,
        "label_meaning": "every record is a fresh-session model proxy standing in for a human/external gate; "
                         "none is an external, human, third-party or independent-team outcome",
        "records": records,
        "terminated_attempts": TERMINATED,
    }
    dest = os.path.join(HERE, "PROXY_RECORDS_V1.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"records": len(records), "with_verdict": sum(1 for x in records if x["verdict_block_present"]),
                      "terminated_attempts": len(TERMINATED)}))


if __name__ == "__main__":
    main(sys.argv[1])
