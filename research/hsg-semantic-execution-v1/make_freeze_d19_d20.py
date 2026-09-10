"""Build FREEZE_D19_D20_V1.json.

Verifies the five already-frozen HSG-v4 files against FREEZE_V1.json's
manifest_sha256 (so this freeze is a CHECK on the prior freeze, not a claim
standing beside it), pins the base commit, and records its own manifest.

Exit codes: 0 = freeze written and prior manifest verified;
            2 = prior manifest MISMATCH (freeze refused);
            3 = could not check (missing file / missing prior freeze).
Run from research/hsg-semantic-execution-v1/ : python3 make_freeze_d19_d20.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRIOR = ["DEFINITIONS.md", "THEOREM_REGISTRY_V1.json", "PARENT_LEDGER.md",
         "EXPERIMENT_REGISTRY_V1.json", "HOSTILE_REGISTRY_V1.json"]
OWN = ["D19_D20_PROTOCOL_V1.json", "exact/worlds_d19d20.py"]


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    fv1_path = os.path.join(HERE, "FREEZE_V1.json")
    if not os.path.exists(fv1_path):
        print("CANNOT_CHECK: FREEZE_V1.json absent", file=sys.stderr)
        return 3
    with open(fv1_path, encoding="utf-8") as f:
        fv1 = json.load(f)

    # Effective manifest = the V1.0 manifest overlaid, in order, by every
    # recorded amendment's own manifest. FREEZE_V1 keeps the original manifest
    # in place and publishes each amendment's manifest under its own key, so
    # checking V1.0 alone raises a FALSE integrity alarm on any legitimately
    # amended file. Resolve to the newest recorded manifest instead, and record
    # which version was used.
    claimed = dict(fv1["manifest_sha256"])
    manifest_version = "V1.0"
    amendment_touched = set()
    for am in fv1.get("amendments", []):
        keys = sorted(k for k in am if k.startswith("manifest_sha256"))
        for k in keys:
            claimed.update(am[k])
            manifest_version = am.get("id", manifest_version)
        amendment_touched |= set(am.get("changes", {}))

    observed, missing = {}, []
    for name in PRIOR:
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            missing.append(name)
            continue
        observed[name] = sha256(p)
    if missing:
        print("CANNOT_CHECK: missing prior frozen files: %s" % missing,
              file=sys.stderr)
        return 3

    mismatches = {n: {"claimed": claimed.get(n), "observed": observed[n]}
                  for n in PRIOR if claimed.get(n) != observed[n]}
    if mismatches:
        print("PRIOR_MANIFEST_MISMATCH: %s"
              % json.dumps(mismatches, indent=1), file=sys.stderr)
        return 2

    # NO-ALARM ASSERTION: files no amendment claims to have touched must still
    # match the ORIGINAL V1.0 manifest. Without this, an over-broad amendment
    # overlay could silently launder an unrecorded edit.
    untouched_drift = {
        n: {"v1_0": fv1["manifest_sha256"].get(n), "observed": observed[n]}
        for n in PRIOR
        if n not in amendment_touched
        and fv1["manifest_sha256"].get(n) != observed[n]}
    if untouched_drift:
        print("UNRECORDED_DRIFT_ON_UNAMENDED_FILE: %s"
              % json.dumps(untouched_drift, indent=1), file=sys.stderr)
        return 2

    own = {}
    for name in OWN:
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            print("CANNOT_CHECK: own artifact absent: %s" % name,
                  file=sys.stderr)
            return 3
        own[name] = sha256(p)

    head = subprocess.check_output(
        ["/usr/bin/git", "rev-parse", "HEAD"], cwd=HERE).decode().strip()
    base = subprocess.check_output(
        ["/usr/bin/git", "rev-parse", "origin/main"], cwd=HERE).decode().strip()

    out = {
        "freeze": "HSG_V4_SEMANTIC_EXECUTION_D19_D20_FREEZE_V1",
        "created_utc": subprocess.check_output(
            ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip(),
        "tool": "make_freeze_d19_d20.py (this script)",
        "issue": "SzeChunYiu/ORION-OCM#233 (D19 + D20 lanes)",
        "base_branch_origin_main": base,
        "head_at_freeze": head,
        "branch": "hsg/d19-d20-labs",
        "prior_freeze": "FREEZE_V1.json",
        "prior_freeze_created_utc": fv1.get("created_utc"),
        "prior_manifest_verified": True,
        "prior_manifest_version_verified": manifest_version,
        "prior_amendment_touched_files": sorted(amendment_touched),
        "prior_unamended_files_still_match_v1_0": True,
        "prior_manifest_sha256_observed": observed,
        "manifest_sha256": own,
        "worlds_frozen": {
            "OW4": "reused unchanged from exact/worlds.py (clean control population)",
            "OW4N": "8 worlds, 4..7 nodes, >=1 blocker each, key ('OW4N', wi)",
            "OW5S": "30 worlds = n in [8,12,16,20,24] x 6, key ('OW5S', n, wi)",
        },
        "seed": 20260910,
        "result_files_present_at_freeze": [],
        "admissibility": (
            "Frozen and pushed in a commit containing no result file. Results "
            "for D19 and D20 are generated only after this commit exists on "
            "the remote. Any later protocol change requires an explicit "
            "supersession record with cause and a re-run of affected arms."),
        "claim_ceiling": (
            "P2 finite certificate over frozen tiny worlds, exhaustively "
            "enumerated; not a universal proof."),
        "locked_gates": "N2 / N4 / N5 remain LOCKED per FREEZE_V1.",
    }
    with open(os.path.join(HERE, "FREEZE_D19_D20_V1.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print("FREEZE_OK prior_manifest_verified=5/5 against %s (amendment-touched: %s) base=%s"
          % (manifest_version, sorted(amendment_touched) or "none", base[:12]))
    for n in PRIOR:
        print("  prior %-32s %s" % (n, observed[n][:16]))
    for n in OWN:
        print("  own   %-32s %s" % (n, own[n][:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
