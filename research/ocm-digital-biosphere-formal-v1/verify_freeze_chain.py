#!/usr/bin/env python3
"""Verify the EB-F0 biosphere freeze chain against the working tree.

Sibling of research/hsg-semantic-execution-v1/verify_freeze_chain.py. That one
resolves DIR from its own __file__, so the freeze-chain workflow checks the HSG
directory ONLY and never touches this one. This closes that gap (G9) for the
biosphere lane rather than leaving the contract unchecked by any machine.

Exit codes are DISTINCT on purpose -- "could not check" must never be reported
as "checked and fine":

    0 VERIFIED          every recorded file matches its recorded hash
    2 UNRECORDED_DRIFT  a file differs from its authoritative recorded value
    3 CANNOT_CHECK      a freeze file is missing or unparseable
    4 USAGE             bad invocation

Resolution rule, which is the whole point of this checker: a file's
authoritative hash is the one in the NEWEST amendment that names it, falling
back to the base manifest. Comparing a top-level manifest against a live tree
reports FALSE drift on any file carrying a legitimate recorded amendment.

Cross-file rule: a freeze may assert that files it did not author are untouched
(`prior_manifest_sha256_observed`). Those are resolved against the repository
root, not this directory, because they name other lanes' modules.
"""
import hashlib
import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(DIR, "..", ".."))


def sha256(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


def manifests_in(obj):
    """Yield every {file: sha} mapping under a key naming a manifest.

    `prior_manifest_sha256_observed` is an assertion ABOUT OTHER LANES' files,
    not an authoritative manifest of this freeze's own. It carries its own
    cross-file rule and is handled separately. Including it here would
    double-count and produce a FALSE drift report -- the exact false positive
    the HSG checker's docstring records having been hit twice.
    """
    for k, v in obj.items():
        if str(k) == "prior_manifest_sha256_observed":
            continue
        if "manifest_sha256" in str(k) and isinstance(v, dict):
            if v and all(isinstance(x, str) for x in v.values()):
                yield k, v


def main(argv):
    if len(argv) > 1:
        print("usage: verify_freeze_chain.py", file=sys.stderr)
        return 4

    freezes = {}
    for n in sorted(os.listdir(DIR)):
        if n.startswith("FREEZE") and n.endswith(".json"):
            try:
                freezes[n] = json.load(open(os.path.join(DIR, n)))
            except Exception as e:
                print("CANNOT_CHECK unparseable %s: %s" % (n, e))
                return 3
    if not freezes:
        print("CANNOT_CHECK no FREEZE*.json found in", DIR)
        return 3

    drift, checked = [], 0

    for fname, doc in freezes.items():
        # Authoritative = base manifest, overridden by any amendment naming the file.
        authoritative, origin = {}, {}
        for k, man in manifests_in(doc):
            for f, h in man.items():
                authoritative[f] = h
                origin[f] = "%s:%s" % (fname, k)
        for am in doc.get("amendments", []):
            if not isinstance(am, dict):
                continue
            aid = am.get("id", "?")
            for k, man in manifests_in(am):
                for f, h in man.items():
                    authoritative[f] = h
                    origin[f] = "%s:amendment %s" % (fname, aid)

        for f, expect in authoritative.items():
            got = sha256(os.path.join(DIR, f))
            checked += 1
            if got is None:
                drift.append((fname, f, "FILE MISSING", origin[f]))
            elif got != expect:
                drift.append((fname, f, "got %s want %s" % (got[:12], expect[:12]), origin[f]))

        # Files this freeze asserts it did not author and did not touch.
        for f, expect in (doc.get("prior_manifest_sha256_observed") or {}).items():
            got = sha256(os.path.join(REPO, f))
            checked += 1
            if got is None:
                drift.append((fname, f, "FILE MISSING", "%s:prior_manifest" % fname))
            elif got != expect:
                drift.append((fname, f, "got %s want %s" % (got[:12], expect[:12]),
                              "%s:prior_manifest" % fname))

    if drift:
        print("UNRECORDED_DRIFT (%d of %d checked)" % (len(drift), checked))
        for fname, f, what, org in drift:
            print("  %-58s %s   [authoritative: %s]" % (f, what, org))
        print("\nIf a change was legitimate, record it as a NUMBERED amendment naming the")
        print("file and its CURRENT hash. Silent edits are drift by construction.")
        return 2

    print("VERIFIED %d recorded hashes across %d freeze file(s) in %s"
          % (checked, len(freezes), os.path.relpath(DIR, REPO)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
