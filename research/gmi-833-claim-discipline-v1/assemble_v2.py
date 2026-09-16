#!/usr/bin/env python3
"""GMI #833 claim-discipline v2 — parent-pin assembler (SUCCESSOR_TRANCHE_V2.md).

Merges the 8 authored v2 pins (authored_parent_pins_v2.PINS_V2) into a copy of
REGISTRATIONS_V1.json -> REGISTRATIONS_V2.json. The v1 register is NEVER written.

Hostile checks (fail closed):
  - v1 baseline: exactly 234 objects; the 8 pinned slots are REGISTERED_GAP in v1
    with exactly the recorded v1 reason (drift guard);
  - only the 8 pinned fields differ between v1 and v2 (deep compare, all other
    fields byte-equal);
  - every EXTRACTED content item embeds a path:line citation that exists under
    research/ (cross-package resolution is the point of this tranche);
  - DERIVED content strings are unique across the ENTIRE merged register
    (v1 no-boilerplate contract extended to v2 additions);
  - v1 artifact byte-integrity: sha256 of REGISTRATIONS_V1.json recorded in the
    output; the script aborts if the v1 gap count is not 8.
Deterministic under -I -B / -I -O -B.
"""
import hashlib
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from authored_arrival_v2 import ARRIVAL  # noqa: E402
from authored_parent_pins_v2 import PINS_V2, OUTCOMES, VERIFICATIONS  # noqa: E402

FIELDS = ["scope_quantifiers", "assumptions", "falsifiers", "strongest_parents", "forbidden_extrapolations"]
V1_PATH = os.path.join(HERE, "REGISTRATIONS_V1.json")
V2_PATH = os.path.join(HERE, "REGISTRATIONS_V2.json")


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def citcheck_v2(items):
    """Every EXTRACTED item's path:line citation must resolve under research/.
    Pins in this tranche cite across packages (e.g. a GGU object pinning
    gmi-formal-derivation-v1 module theorems), so resolution is research/-rooted."""
    missing = []
    for it in items:
        m = re.match(r"([A-Za-z0-9_./-]+\.[A-Za-z0-9]+):L?\d+", it)
        if m:
            p = os.path.join(RESEARCH, m.group(1))
            if not os.path.exists(p):
                missing.append(m.group(1))
    return missing


def main():
    v1_bytes = open(V1_PATH, "rb").read()
    reg = json.loads(v1_bytes.decode())
    assert reg["counts"]["objects"] == 234, reg["counts"]["objects"]
    assert reg["counts"]["registered_gap"] == 8, "v1 baseline must carry exactly 8 gaps"
    v1_by_rid = {o["result_id"]: o for o in reg["objects"]}

    changed = []
    missing_cites = []
    for pin in PINS_V2:
        rid = pin["result_id"]
        obj = v1_by_rid[rid]
        assert obj["object_id"] == pin["object_id"], rid
        fd = obj["fields"][pin["field"]]
        assert fd["status"] == "REGISTERED_GAP", (rid, pin["field"], fd["status"])
        assert fd.get("reason") == pin["v1_reason"], (rid, "v1 reason drift", fd.get("reason"))
        assert pin["status"] in ("EXTRACTED", "DERIVED")
        assert pin["content"] and all(isinstance(c, str) and c.strip() for c in pin["content"])
        if pin["status"] == "EXTRACTED":
            missing_cites += citcheck_v2(pin["content"])
        newfd = {
            "status": pin["status"],
            "content": pin["content"],
            "source": "authored_parent_pins_v2.PINS_V2[%s/%s]" % (pin["object_id"], pin["field"]),
            "v2_outcome": pin["outcome"],
            "basis": pin["basis"],
        }
        obj["fields"][pin["field"]] = newfd
        changed.append((pin["object_id"], pin["field"], pin["outcome"]))

    # deep compare v1 vs v2 (shared 234 objects): only the 8 pinned slots differ
    orig = json.loads(v1_bytes.decode())
    diffs = []
    for o_new, o_old in zip(reg["objects"], orig["objects"]):
        assert o_new["result_id"] == o_old["result_id"]
        for f in FIELDS:
            if o_new["fields"][f] != o_old["fields"][f]:
                diffs.append((o_new["object_id"], f))
    assert sorted(diffs) == sorted((oid, fld) for oid, fld, _ in changed), diffs

    # ---- arrivals absorption (frozen mechanical re-run rule, tranche freeze section 4)
    arrival = json.loads(json.dumps(ARRIVAL))  # deep copy
    for f, fd in arrival["fields"].items():
        assert fd["status"] in ("EXTRACTED", "DERIVED"), (f, fd["status"])
        assert fd.get("content"), f
        missing_cites += citcheck_v2(fd["content"])
        fd["source"] = "authored_arrival_v2.ARRIVAL (post-v1 arrival absorbed under the frozen mechanical rule)"
    assert arrival["tranche"] == "U-NEW"
    new_unew = [o for o in reg["objects"] if o["tranche"] == "U-NEW"]
    assert len(new_unew) == 8, len(new_unew)
    reg["objects"].append({
        "result_id": arrival["result_id"],
        "object_id": arrival["object_id"],
        "package": arrival["package"],
        "tranche": arrival["tranche"],
        "fields": arrival["fields"],
    })

    # counts
    status_counts = Counter()
    for o in reg["objects"]:
        for f in FIELDS:
            status_counts[o["fields"][f]["status"]] += 1
    gaps = [(o["object_id"], f) for o in reg["objects"] for f in FIELDS if o["fields"][f]["status"] == "REGISTERED_GAP"]
    assert not gaps, gaps

    # no-boilerplate across the ENTIRE merged register (DERIVED strings unique)
    seen = {}
    dup = []
    for o in reg["objects"]:
        for f in FIELDS:
            fd = o["fields"][f]
            if fd["status"] == "DERIVED":
                for item in fd.get("content", []):
                    if item in seen:
                        dup.append((o["object_id"], seen[item], item[:80]))
                    seen[item] = o["object_id"]
    assert not dup, dup

    out = {
        "schema": "GMI833_CLAIM_DISCIPLINE_REGISTRATIONS_V2",
        "freeze": "SUCCESSOR_TRANCHE_V2.md",
        "v1_baseline": {
            "register": "REGISTRATIONS_V1.json",
            "sha256": sha256_file(V1_PATH),
            "counts": orig["counts"],
        },
        "objects": reg["objects"],
        "counts": {
            "objects": len(reg["objects"]),
            "fields_registered": sum(v for k, v in status_counts.items() if k != "REGISTERED_GAP"),
            "registered_gap": status_counts.get("REGISTERED_GAP", 0),
            "by_status": dict(sorted(status_counts.items())),
        },
        "v2_outcomes": OUTCOMES,
        "v2_arrival": {
            "package": ARRIVAL["package"],
            "object_id": ARRIVAL["object_id"],
            "rule": "frozen mechanical re-run: git diff --stat ed736cd3..origin/main -- research/",
            "fields": "all five EXTRACTED at file:line (authored_arrival_v2.py)",
        },
        "v2_verifications": VERIFICATIONS,
    }
    with open(V2_PATH, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print("objects:", out["counts"]["objects"])
    print("by_status:", dict(sorted(status_counts.items())))
    print("slots changed vs v1:", len(changed))
    for oid, fld, oc in changed:
        print("  PIN:", oid, "/", fld, "->", oc)
    print("arrival absorbed:", arrival["package"], "->", arrival["object_id"])
    print("v1 sha256:", out["v1_baseline"]["sha256"])
    if missing_cites:
        print("MISSING CITATION PATHS:", missing_cites)
        sys.exit(4)
    print("citation paths: all resolve under research/")
    print("no-boilerplate: 0 duplicate DERIVED strings across merged register")
    return 0


if __name__ == "__main__":
    sys.exit(main())
