#!/usr/bin/env python3
"""GMI distributed work queue — four machines, one branch, no collisions.

WHY THIS EXISTS, AND WHAT IT IS DEFENDING AGAINST. The available machines are the remote container, two laptops and
LUNARC. They share exactly one coordination medium: the git branch. That is enough, provided two hazards are handled.

HAZARD 1 - RECEIPT COLLISION. This has ALREADY happened once and destroyed committed evidence: `STAGE_B1_{tag}_S{seed}`
did not key on the ecology, so a second ecology's runs silently OVERWROTE two committed receipts of the first (recorded
alongside `RV-377-078`; both were recovered from git history). Four machines writing into one results directory
multiplies that risk by four. The defence here is structural rather than procedural: EVERY unit's receipt path carries
the HOST token, so even a double-claimed unit cannot overwrite another machine's receipt. Claims prevent wasted work;
host-keying prevents corruption. Do not rely on the claim alone.

HAZARD 2 - RUNNING AN UNFROZEN EXPERIMENT. The revival protocol requires the prediction to be committed BEFORE the run.
A queue makes it easy to run something nobody froze. `run` therefore REFUSES any unit whose `frozen` field is false, and
the manifest carries the `revival_id` that must already exist in a ledger. Fail closed.

LEASE MODEL. `claim` writes the claim into the manifest and the operator commits and pushes it. Git rejects a
non-fast-forward push, so two machines cannot both land a claim on the same unit; the loser pulls, sees the claim, and
picks another. This is a cooperative lease, not a lock: a machine that dies holds its claim until someone runs
`release --host <name>`.

USAGE (identical on every machine):

    python3 gmi_work.py status
    python3 gmi_work.py claim --host lunarc --class hpc --n 8
    git add GMI_WORK_MANIFEST_V1.json && git commit -m "claim: lunarc x8" && git push
    python3 gmi_work.py run --host lunarc
    git add -A && git commit -m "receipts: lunarc" && git push

`--dry-run` prints the commands without executing them, which is what the sbatch array uses to build its task list.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import socket
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "GMI_WORK_MANIFEST_V1.json")
CLASSES = ("tiny", "small", "medium", "large", "hpc")


def _load():
    with open(MANIFEST) as f:
        return json.load(f)


def _save(m):
    with open(MANIFEST, "w") as f:
        json.dump(m, f, indent=1, sort_keys=True)


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _host(arg):
    return arg or os.environ.get("GMI_HOST") or socket.gethostname().split(".")[0]


def _subst(unit, host):
    """the HOST token is what makes two machines unable to overwrite each other."""
    return [tok.replace("{HOST}", host) for tok in unit["cmd"]], unit["receipt"].replace("{HOST}", host)


def cmd_status(a):
    m = _load()
    units = m["units"]
    by = {}
    for u in units:
        st = "done" if u.get("done") else ("claimed:" + u["claim"]["host"] if u.get("claim") else
                                           ("FROZEN-PENDING" if not u["frozen"] else "free"))
        by.setdefault(st, []).append(u["unit_id"])
    print(f'{m["schema"]}  {len(units)} units')
    for st in sorted(by):
        print(f'  {st:22s} {len(by[st]):3d}  {",".join(by[st][:10])}{" …" if len(by[st]) > 10 else ""}')
    print()
    print(f'{"class":8s} {"free":>5s} {"claimed":>8s} {"done":>5s}  est core-hours (free)')
    for c in CLASSES:
        cu = [u for u in units if u["class"] == c]
        free = [u for u in cu if not u.get("claim") and not u.get("done") and u["frozen"]]
        print(f'{c:8s} {len(free):5d} {sum(1 for u in cu if u.get("claim")):8d} '
              f'{sum(1 for u in cu if u.get("done")):5d}  {sum(u["est_core_seconds"] for u in free)/3600:.2f}')


def cmd_claim(a):
    host = _host(a.host)
    m = _load()
    want = [u for u in m["units"]
            if u["frozen"] and not u.get("done") and not u.get("claim")
            and (a.klass is None or u["class"] == a.klass)
            and (a.lane is None or u["lane"] == a.lane)]
    if not want:
        print("nothing free matching that filter", file=sys.stderr)
        return 1
    took = want[:a.n]
    for u in took:
        u["claim"] = {"host": host, "at": _now()}
    _save(m)
    print(f"claimed {len(took)} unit(s) for host {host}:")
    for u in took:
        print(f'  {u["unit_id"]:8s} {u["class"]:7s} {u["lane"]:6s} ~{u["est_core_seconds"]}s  {u["title"]}')
    print("\nNow commit and push the manifest, THEN run:")
    print(f"  git add {os.path.basename(MANIFEST)} && git commit -m 'claim: {host} x{len(took)}' && git push")
    print(f"  python3 gmi_work.py run --host {host}")
    return 0


def cmd_release(a):
    host = _host(a.host)
    m = _load()
    n = 0
    for u in m["units"]:
        if u.get("claim") and u["claim"]["host"] == host and not u.get("done"):
            u["claim"] = None
            n += 1
    _save(m)
    print(f"released {n} unclaimed-but-unfinished unit(s) held by {host}")
    return 0


def cmd_run(a):
    host = _host(a.host)
    m = _load()
    mine = [u for u in m["units"]
            if u.get("claim") and u["claim"]["host"] == host and not u.get("done")]
    if a.only:
        mine = [u for u in mine if u["unit_id"] in set(a.only.split(","))]
    if not mine:
        print(f"no claimed, unfinished units for host {host}", file=sys.stderr)
        return 1
    rc_all = 0
    for u in mine:
        if not u["frozen"]:                       # fail closed: never run an unfrozen experiment
            print(f'REFUSING {u["unit_id"]}: frozen=false ({u["revival_id"] or "no revival id"})', file=sys.stderr)
            rc_all = 3
            continue
        cmd, receipt = _subst(u, host)
        print(f'=== {u["unit_id"]} [{u["class"]}] {u["title"]}\n    -> {receipt}\n    $ {" ".join(cmd)}', flush=True)
        if a.dry_run:
            continue
        rc = subprocess.call(cmd, cwd=ROOT)
        if rc == 0 and os.path.exists(os.path.join(ROOT, receipt)):
            u["done"] = {"host": host, "at": _now(), "receipt": receipt}
            _save(m)
        else:
            print(f'  FAILED rc={rc} (receipt present: {os.path.exists(os.path.join(ROOT, receipt))})', file=sys.stderr)
            rc_all = rc or 4
    print("\nCommit the receipts and the manifest:")
    print(f"  git add -A && git commit -m 'receipts: {host}' && git push")
    return rc_all


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="c", required=True)
    sub.add_parser("status").set_defaults(f=cmd_status)
    c = sub.add_parser("claim"); c.add_argument("--host"); c.add_argument("--class", dest="klass", choices=CLASSES)
    c.add_argument("--lane"); c.add_argument("--n", type=int, default=1); c.set_defaults(f=cmd_claim)
    r = sub.add_parser("run"); r.add_argument("--host"); r.add_argument("--dry-run", action="store_true")
    r.add_argument("--only"); r.set_defaults(f=cmd_run)
    x = sub.add_parser("release"); x.add_argument("--host"); x.set_defaults(f=cmd_release)
    a = p.parse_args()
    sys.exit(a.f(a))


if __name__ == "__main__":
    main()
