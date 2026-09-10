"""RV-8 submit feeder: keep the cell array flowing under LUNARC's MaxSubmitJobs=300.

Scheduling only -- it selects WHICH frozen cell to submit next and never touches a
frozen constant, an arm, a stream or a cost term.

lu48 caps this association at 300 submitted (pending + running) jobs, and array tasks
count individually, so a single `--array=0-983` submission is rejected with
AssocMaxSubmitJobLimit. This loops: count my own lu48 jobs, submit the next chunk of
unfinished cells if there is room, sleep, repeat. It self-heals across submit failures
rather than aborting on one.

MY_CAP is deliberately below the 300 limit: a sibling lane (EB-F0, issue #296) shares
this association, and taking the whole allowance would starve it.

Order is high-mix-first, so the part of the surface that carries the crossover claim
completes first.

    setsid python3 rv8_feeder.py <out_dir> &

Run with --once to submit a single top-up and exit.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rv8_horizon as H  # noqa: E402

BASE = "/projects/hep/fs12/scratch/scyiu-rv8"
BODY = BASE + "/rv8_array_body.sb"
ACCOUNT = "lu2026-2-51"
PARTITION = "lu48"
MY_CAP = 240              # of the association's 300; the rest is left for the sibling lane
CHUNK = 40                # array tasks per sbatch call
POLL_SEC = 120

#: --time per cost class, sized from probe_cost.py's measured worst-cell projection
#: (RV8_COSTPROBE.json) with margin. Measured worst cell, hours:
#:   full     NOGOOD_ONLY_per_batch 37.8, NO_LIBRARY 32.9, STITCH 28.4, CEGIS 2.5
#:   null     SHUFFLE_NULL#1 217.8, #2 172.3, NC#0 139.2  -- two exceed lu48's 7-day
#:            ceiling, so those cells will run as far as they get and be compared with
#:            their learned counterpart on the prefix BOTH reached. Shortening the
#:            null's horizon instead would make it non-comparable at the horizon where
#:            the crossover claim is made.
#:   reduced  EGGRAPH 6.9, AU_PAIR 5.8, CHUNK 1.2
HOURS = {"full": 96, "null": 167, "reduced": 24}

#: A cell that times out is retried once; after that its recorded prefix stands. Without
#: this a cell too long for the ceiling would be resubmitted forever.
MAX_ATTEMPTS = 2


def my_jobs():
    r = subprocess.run(["squeue", "-u", "scyiu", "-p", PARTITION, "-h", "-o", "%i"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return len([x for x in r.stdout.split("\n") if x.strip()])


def cell_done(out, idx):
    p = out / "cells" / ("cell_%05d.json.gz" % idx)
    if not p.exists():
        return False
    import gzip
    try:
        with gzip.open(str(p), "rt") as fh:
            return bool(json.load(fh).get("complete"))
    except Exception:
        return False


def cell_class(c):
    if c["arm"] in H.NULL_ARMS:
        return "null"
    return "reduced" if c["arm"] in H.REDUCED_ARMS else "full"


def ordered_cells():
    """High mix first; within a mix, the arms that can cross before the ones that
    cannot, and the nulls with them."""
    cells = list(enumerate(H.cell_inventory()))
    def key(item):
        i, c = item
        cls = 0 if c["arm"] in H.FULL_ARMS else (1 if c["arm"] in H.NULL_ARMS else 2)
        return (-c["mix_idx"], cls, i)
    return [i for i, _c in sorted(cells, key=key)]


def main(out, once=False):
    order = ordered_cells()
    log = out.parent / "logs" / "feeder.log"
    log.parent.mkdir(parents=True, exist_ok=True)

    def say(msg):
        with open(str(log), "a") as fh:
            fh.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), msg))

    say("feeder start, %d cells, cap %d" % (len(order), MY_CAP))
    inflight = set()
    attempts = {}
    while True:
        todo = [i for i in order if i not in inflight and not cell_done(out, i)
                and attempts.get(i, 0) < MAX_ATTEMPTS]
        if not todo:
            say("all cells complete or in flight; exiting")
            return 0
        n = my_jobs()
        if n is None:
            say("squeue failed; retrying")
            time.sleep(POLL_SEC)
            continue
        room = MY_CAP - n
        if room < CHUNK:
            if once:
                say("no room (%d in flight); once-mode exit" % n)
                return 0
            time.sleep(POLL_SEC)
            continue
        inv = H.cell_inventory()
        cls = cell_class(inv[todo[0]])
        batch = [i for i in todo if cell_class(inv[i]) == cls][:min(CHUNK, room)]
        arr = ",".join(str(i) for i in batch)
        cmd = ["sbatch", "-A", ACCOUNT, "-p", PARTITION, "-n", "1", "-c", "1",
               "--mem-per-cpu=4000", "-t", "%d:00:00" % HOURS[cls],
               "-J", "rv8cell", "--array=" + arr + "%%%d" % CHUNK, BODY]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            inflight.update(batch)
            for i in batch:
                attempts[i] = attempts.get(i, 0) + 1
            say("submitted %d %s cells (-t %dh): %s" % (len(batch), cls, HOURS[cls],
                                                        r.stdout.strip()))
        else:
            say("submit failed (%s); backing off" % r.stderr.strip()[:200])
            time.sleep(POLL_SEC)
            continue
        # cells that finish leave inflight so a crashed/timed-out cell is retried
        inflight = set(i for i in inflight if not cell_done(out, i))
        if once:
            return 0
        time.sleep(15)


if __name__ == "__main__":
    o = Path([a for a in sys.argv[1:] if not a.startswith("--")][0]).resolve()
    sys.exit(main(o, once="--once" in sys.argv))
