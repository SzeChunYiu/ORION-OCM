#!/usr/bin/env python3
"""Freeze-binding check for an EXISTING GRAND_SEARCH_R1_FREEZE.json
(submit_gs.py gate 5, existing-freeze branch): the freeze binds a code
digest at freeze time; if the capsule code drifted since (pre-score
hardening), refuse HERE with a clear message instead of failing deep
inside a smoke job 15 minutes later.  A drifted pre-score freeze must be
superseded explicitly (GS_R1_FREEZE_SUPERSESSION.jsonl), never silently
rewritten.

Usage: python3 hpc/check_freeze_binding.py <CAPSULE_ROOT>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.abspath(sys.argv[1])


def code_digest(root: str) -> str:
    h = hashlib.sha256()
    for d in ("morphology", "evaluation", "search", "hpc"):
        for fn in sorted(os.listdir(os.path.join(root, d))):
            if fn.endswith(".py"):
                h.update(open(os.path.join(root, d, fn), "rb").read())
    return h.hexdigest()


def main() -> None:
    p = os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json")
    freeze = json.load(open(p))
    cur = code_digest(ROOT)
    frozen = freeze["code_digest"]
    fsha = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if cur != frozen:
        raise SystemExit(
            "REFUSED: CODE DRIFT vs freeze — capsule digest %s != frozen %s "
            "(freeze %s created %s).  No scored GS runs may proceed; "
            "supersede explicitly via GS_R1_FREEZE_SUPERSESSION.jsonl then "
            "refreeze." % (cur[:16], frozen[:16], fsha[:16],
                           freeze["created_utc"]))
    print("FREEZE BINDING OK freeze_sha256=%s code_digest=%s" % (
        fsha, frozen))


if __name__ == "__main__":
    main()
