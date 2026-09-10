"""FORM_ORACLE_PROTOCOL_V1_AMEND_1 — recorded pre-run supersession.

The V1 protocol pinned a sha256 for every oracle/*.py file. Two of those files
were then edited BEFORE any scored run existed, to add a supplementary
reporting view. The freeze discipline says a post-freeze change needs a
recorded supersession with cause, so here it is, minted as its own artefact
rather than by rewriting the frozen protocol.

CAUSE
    Evolvability is computed on a seeded random SUBSAMPLE of T2 survivors, so
    the 4-objective report front covers only that subsample and every retained
    record outside it lands in the CANNOT_CHECK bucket. A determinism smoke run
    made this concrete: 14 retained, 8 with a complete 4-vector, 6 dropped.
    Reporting only the 4-objective front would therefore silently omit a third
    of the map, and an honest map of where each form wins and loses is the
    stated success condition.

CHANGE
    Added COVERAGE_OBJECTIVES = (capability, burden, t3_gen) and its front,
    computed over EVERY retained record.

WHAT DID NOT CHANGE
    No objective definition, no estimator, no admission rule, no hard gate, no
    seed, no rung, no null, no falsifier. Search-time admission is still the
    3-vector (capability, burden, evolvability) and T3 still never enters it.
    The addition is a report, not a redefinition.

TIMING
    Made before any scored run. No result was seen, so nothing needed re-running
    and no outcome could have informed the change.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Digests recorded in FORM_ORACLE_PROTOCOL_V1.json at freeze time.
FROZEN_PROTOCOL_SHA = ("3c956d336793b04c98c8dce19af2137e"
                       "7365c3ef971bd70aefaeed889ecbf833")


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    proto_path = os.path.join(ROOT, "FORM_ORACLE_PROTOCOL_V1.json")
    proto = json.load(open(proto_path))
    frozen = proto.get("code_digests", {})

    current = {}
    for fn in sorted(os.listdir(os.path.join(ROOT, "oracle"))):
        if fn.endswith(".py"):
            current["oracle/" + fn] = _sha256_file(
                os.path.join(ROOT, "oracle", fn))

    changed = {k: {"frozen": frozen.get(k), "current": v}
               for k, v in current.items() if frozen.get(k) != v}
    added = sorted(set(current) - set(frozen))
    removed = sorted(set(frozen) - set(current))

    from oracle import objectives4 as OB
    amend = {
        "amendment_id": "FORM_ORACLE_PROTOCOL_V1_AMEND_1",
        "supersedes_digest": FROZEN_PROTOCOL_SHA,
        "protocol_digest_on_disk": _sha256_file(proto_path),
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "timing": "BEFORE_ANY_SCORED_RUN",
        "cause": (
            "evolvability is computed on a seeded random subsample, so the "
            "4-objective report front covers only that subsample; a smoke run "
            "showed 14 retained, 8 with a complete 4-vector, 6 dropped. "
            "Reporting only that front would omit part of the map."),
        "change": (
            "added COVERAGE_OBJECTIVES = (capability, burden, t3_gen) and its "
            "Pareto front, computed over every retained record"),
        "coverage_objectives": list(OB.COVERAGE_OBJECTIVES),
        "coverage_maximize": list(OB.COVERAGE_MAXIMIZE),
        "unchanged": [
            "search-time admission is still (capability, burden, evolvability)",
            "T3 still never enters admission",
            "every estimator, hard gate, seed, rung, null and falsifier",
        ],
        "rerun_required": False,
        "rerun_rationale": ("no scored result existed when the change was made, "
                            "so no outcome could have informed it and nothing "
                            "needed re-running"),
        "code_digest_drift": {
            "changed": changed, "added": added, "removed": removed,
        },
    }
    out = os.path.join(ROOT, "FORM_ORACLE_PROTOCOL_V1_AMEND_1.json")
    blob = json.dumps(amend, indent=1, sort_keys=True, default=str)
    with open(out, "w") as fh:
        fh.write(blob + "\n")
    sys.stderr.write("amend sha256 %s changed=%d\n"
                     % (hashlib.sha256((blob + "\n").encode()).hexdigest(),
                        len(changed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
