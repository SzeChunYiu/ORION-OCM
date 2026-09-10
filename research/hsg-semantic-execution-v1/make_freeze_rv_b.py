"""Build FREEZE_RV_B_V1.json.

Re-verifies BOTH prior freezes before recording its own manifest:
  FREEZE_V1.json          (with every recorded amendment, e.g. V1.1, V1.2)
  FREEZE_D19_D20_V1.json  (with amendment S1)

Resolution rule, identical to make_freeze_d19_d20.py: the effective manifest is
the original overlaid, in order, by every recorded amendment's own manifest;
separately, any file NO amendment claims to have touched must still match the
ORIGINAL manifest, so an over-broad overlay cannot launder an unrecorded edit.

Exit 0 = both prior freezes verified and this freeze written.
Exit 2 = a prior manifest MISMATCH (freeze refused).
Exit 3 = could not check (a prior freeze or a listed file is absent).
Run from research/hsg-semantic-execution-v1/ : python3 make_freeze_rv_b.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OWN = ["RV_B_PROTOCOL_V1.json"]


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def resolve(freeze):
    """(effective manifest, amendment-touched files, amendment id chain)."""
    eff = dict(freeze["manifest_sha256"])
    touched, chain = set(), []
    for am in freeze.get("amendments", []):
        for k in sorted(x for x in am if x.startswith("manifest_sha256")):
            eff.update(am[k])
        touched |= set(am.get("changes", {}))
        chain.append(am.get("id", "?"))
    return eff, touched, chain


def verify(freeze_name, report):
    p = os.path.join(HERE, freeze_name)
    if not os.path.exists(p):
        print("CANNOT_CHECK: %s absent" % freeze_name, file=sys.stderr)
        return 3
    with open(p, encoding="utf-8") as f:
        fr = json.load(f)
    eff, touched, chain = resolve(fr)
    observed, missing, bad = {}, [], {}
    for name in sorted(eff):
        fp = os.path.join(HERE, name)
        if not os.path.exists(fp):
            missing.append(name)
            continue
        observed[name] = sha256(fp)
        if observed[name] != eff[name]:
            bad[name] = {"claimed": eff[name], "observed": observed[name]}
    if missing:
        print("CANNOT_CHECK: %s lists missing files %s"
              % (freeze_name, missing), file=sys.stderr)
        return 3
    if bad:
        print("PRIOR_MANIFEST_MISMATCH in %s: %s"
              % (freeze_name, json.dumps(bad, indent=1)), file=sys.stderr)
        return 2
    drift = {n: {"original": fr["manifest_sha256"][n], "observed": observed[n]}
             for n in fr["manifest_sha256"]
             if n not in touched and fr["manifest_sha256"][n] != observed[n]}
    if drift:
        print("UNRECORDED_DRIFT_ON_UNAMENDED_FILE in %s: %s"
              % (freeze_name, json.dumps(drift, indent=1)), file=sys.stderr)
        return 2
    report[freeze_name] = {
        "verified": True,
        "amendment_chain": chain or ["(none)"],
        "manifest_version_verified": chain[-1] if chain else "V1.0",
        "files_verified": len(observed),
        "amendment_touched_files": sorted(touched),
        "unamended_files_still_match_original": True,
        "observed_sha256": observed,
    }
    print("  %-26s OK  %d files, manifest %s"
          % (freeze_name, len(observed), chain[-1] if chain else "V1.0"))
    return 0


def main():
    report = {}
    for fname in ("FREEZE_V1.json", "FREEZE_D19_D20_V1.json"):
        rc = verify(fname, report)
        if rc:
            return rc

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
        "freeze": "HSG_V4_SEMANTIC_EXECUTION_RV_B_FREEZE_V1",
        "created_utc": subprocess.check_output(
            ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip(),
        "tool": "make_freeze_rv_b.py (this script)",
        "issue": "SzeChunYiu/ORION-OCM#233, revival lane RV-B",
        "base_branch_origin_main": base,
        "head_at_freeze": head,
        "branch": "hsg/rv-b1-incremental",
        "prior_freezes_verified": report,
        "manifest_sha256": own,
        "new_seed_key_prefixes": ["RVBQ"],
        "worlds_reused_unchanged": [
            "OW5S: the same frozen 30 worlds, n grid [8,12,16,20,24]",
            "OW4 and OW4N: the same frozen 8 + 8 worlds",
        ],
        "result_files_present_at_freeze": [],
        "declared_source_change": (
            "RV-B2(ii) deliberately repairs exact/oracles_d17.py t72() to "
            "revoke over true sources. Declared here before the run; the "
            "before/after effect on the D17 tranche is reported in full."),
        "admissibility": (
            "Frozen and pushed in a commit containing no result file. Any "
            "later protocol change requires an explicit supersession with "
            "cause and a re-run of affected arms."),
        "claim_ceiling": (
            "P2 finite certificate over frozen tiny worlds, plus one "
            "asymptotic lower-bound ARGUMENT explicitly not a machine-checked "
            "certificate."),
        "locked_gates": "N2 / N4 / N5 remain LOCKED.",
    }
    with open(os.path.join(HERE, "FREEZE_RV_B_V1.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print("FREEZE_RV_B_OK base=%s" % base[:12])
    for n in OWN:
        print("  own   %-28s %s" % (n, own[n][:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
