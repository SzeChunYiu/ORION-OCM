#!/usr/bin/env python3
import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[1]
DAG_PATH = ROOT / "DEPENDENCY_DAG_V2.json"
STATUS_PATH = ROOT / "ROUND_STATUS_V2.json"
R17_PATH = ROOT / "R17_ATOMIC_ADDENDUM_V2.json"

ALLOWED = {"EARNED","IN_PROGRESS","STALE","NOT_STARTED","UNKNOWN","CANNOT_CHECK"}

def need(cond, msg):
    if not cond:
        raise RuntimeError(msg)

def load(path):
    return json.loads(path.read_text())

def acyclic(nodes, deps):
    temp=set(); perm=set()
    def visit(n):
        if n in perm: return
        if n in temp: raise RuntimeError("CYCLE:"+n)
        temp.add(n)
        for d in deps[n]: visit(d)
        temp.remove(n); perm.add(n)
    for n in nodes: visit(n)

def descendants(nodes, deps):
    out={n:set() for n in nodes}
    changed=True
    while changed:
        changed=False
        for child in nodes:
            for parent in deps[child]:
                before=len(out[parent])
                out[parent].add(child)
                out[parent].update(out[child])
                changed |= len(out[parent]) != before
    return out

def infer_rounds(paths):
    rounds=set()
    rx=re.compile(r"(?:^|/)gmi-1068-r(\d+)(?:-|/)")
    for p in paths:
        m=rx.search(p)
        if m:
            rounds.add("R"+str(int(m.group(1))))
    return rounds

def base_status(base_sha):
    if not base_sha:
        return None
    rel="research/gmi-1068-governance-v2/ROUND_STATUS_V2.json"
    p=subprocess.run(
        ["git","-C",str(REPO),"show",f"{base_sha}:{rel}"],
        capture_output=True,text=True
    )
    if p.returncode != 0:
        return None
    return json.loads(p.stdout)

def validate(dag, stat, add):
    nodes=[f"R{i}" for i in range(18)]
    need(dag["nodes"]==nodes,"NODE_SET")
    deps=dag["dependencies"]
    need(set(deps)==set(nodes),"DEPENDENCY_KEYS")
    for n in nodes:
        need(all(d in nodes for d in deps[n]),"UNKNOWN_DEP:"+n)
        need(n not in deps[n],"SELF_DEP:"+n)
    acyclic(nodes,deps)

    rounds=stat["rounds"]
    need(set(rounds)==set(nodes),"STATUS_KEYS")
    need(set(stat["status_vocabulary"])==ALLOWED,"STATUS_VOCAB")
    for n in nodes:
        s=rounds[n]["status"]
        need(s in ALLOWED,"BAD_STATUS:"+n)
        if s in {"EARNED","IN_PROGRESS"}:
            for d in deps[n]:
                need(rounds[d]["status"]=="EARNED",f"{n}_{s}_WITH_NON_EARNED_DEP_{d}")
        if s=="EARNED":
            need(bool(rounds[n].get("evidence")),"EARNED_WITHOUT_EVIDENCE:"+n)

    rev=descendants(nodes,deps)
    for n in nodes:
        if rounds[n]["status"]=="STALE":
            bad=[d for d in rev[n] if rounds[d]["status"]=="EARNED"]
            need(not bad,f"STALE_{n}_HAS_EARNED_DESCENDANTS:{sorted(bad)}")

    ids=[r["id"] for r in add["rows"]]
    need(ids==[f"GMI2-R17-{i:03d}" for i in range(1,18)],"R17_IDS")
    need(add["row_count"]==17,"R17_COUNT")
    need(all(r["round"]=="R17" and r["status"]=="NOT_STARTED" and not r["closes_by_prose"] for r in add["rows"]),"R17_ROWS")
    return nodes, deps, rounds, rev

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-sha",default="")
    ap.add_argument("--changed-files",default="")
    ap.add_argument("--dag-path",default=str(DAG_PATH))
    ap.add_argument("--status-path",default=str(STATUS_PATH))
    ap.add_argument("--r17-path",default=str(R17_PATH))
    args=ap.parse_args()

    dag=load(pathlib.Path(args.dag_path))
    stat=load(pathlib.Path(args.status_path))
    add=load(pathlib.Path(args.r17_path))
    nodes,deps,rounds,rev=validate(dag,stat,add)
    touched=set()
    if args.changed_files:
        paths=[x.strip() for x in pathlib.Path(args.changed_files).read_text().splitlines() if x.strip()]
        touched=infer_rounds(paths)

    b=base_status(args.base_sha)
    if b is not None and touched:
        brounds=b["rounds"]
        for n in sorted(touched,key=lambda x:int(x[1:])):
            for d in deps[n]:
                need(brounds[d]["status"]=="EARNED",f"PR_TOUCHES_{n}_WITH_BASE_DEP_{d}_{brounds[d]['status']}")
            need(rounds[n]["status"]=="EARNED",f"PR_TOUCHES_{n}_WITHOUT_CURRENT_EARNED_STATUS")

    print(json.dumps({
        "status":"GREEN",
        "nodes":len(nodes),
        "r17_rows":17,
        "earned":sorted(n for n in nodes if rounds[n]["status"]=="EARNED"),
        "in_progress":sorted(n for n in nodes if rounds[n]["status"]=="IN_PROGRESS"),
        "stale":sorted(n for n in nodes if rounds[n]["status"]=="STALE"),
        "touched_rounds":sorted(touched),
        "base_gate_applied":b is not None,
    },sort_keys=True))

if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print("GOVERNANCE_V2_RED:"+repr(exc),file=sys.stderr)
        sys.exit(1)
