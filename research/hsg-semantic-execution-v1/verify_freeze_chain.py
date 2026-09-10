#!/usr/bin/env python3
"""Verify the HSG freeze chain against the working tree.

Exit codes are DISTINCT on purpose -- "could not check" must never be
reported as "checked and fine":

  0  VERIFIED            every recorded file matches a recorded value
  2  UNRECORDED_DRIFT    a file differs from every recorded value for it
  3  CANNOT_CHECK        a freeze file is missing or unparseable
  4  USAGE               bad invocation

Resolution rule (this is the whole point of the checker):
a file's authoritative hash is the one in the NEWEST amendment that names it,
falling back to the freeze's base manifest. Comparing the TOP-LEVEL manifest
against the live tree reports FALSE drift on any file carrying a legitimate
recorded amendment -- that false positive has been hit twice in this repo, so
it is what this script exists to avoid.

Cross-file rule: a freeze may assert that files it did not author are
untouched (`prior_manifest_sha256_observed`). Another lane may legitimately
amend such a file, but only if some freeze in the same directory records an
amendment naming that file with its CURRENT hash. An unrecorded change is
drift, and is reported as such.
"""
import hashlib, json, os, sys

DIR = os.path.dirname(os.path.abspath(__file__))


def sha256(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


def manifests_in(obj):
    """Yield every {file: sha} mapping under a key naming a manifest."""
    for k, v in obj.items():
        # prior_manifest_sha256_observed is an assertion ABOUT OTHER LANES' files,
        # not an authoritative manifest of this freeze's own; it carries its own
        # cross-file supersession rule and is handled separately. Including it here
        # double-counts it and produces a FALSE drift report -- caught on this
        # checker's first real run.
        if str(k) == "prior_manifest_sha256_observed":
            continue
        if "manifest_sha256" in str(k) and isinstance(v, dict):
            if all(isinstance(x, str) for x in v.values()):
                yield k, v


def load_freezes():
    freezes, unreadable = {}, []
    for name in sorted(os.listdir(DIR)):
        if not (name.startswith("FREEZE") and name.endswith(".json")):
            continue
        try:
            with open(os.path.join(DIR, name)) as fh:
                freezes[name] = json.load(fh)
        except (OSError, ValueError) as exc:
            unreadable.append((name, str(exc)))
    return freezes, unreadable


def main():
    freezes, unreadable = load_freezes()
    if unreadable:
        for n, e in unreadable:
            print(f"CANNOT_CHECK unreadable freeze {n}: {e}")
        return 3
    if not freezes:
        print("CANNOT_CHECK no FREEZE*.json found in", DIR)
        return 3

    # every hash ever recorded for a file, anywhere, so cross-file amendments resolve
    recorded_anywhere = {}
    for fname, doc in freezes.items():
        for _, man in manifests_in(doc):
            for f, h in man.items():
                recorded_anywhere.setdefault(f, set()).add(h)
        for am in doc.get("amendments", []):
            if isinstance(am, dict):
                for _, man in manifests_in(am):
                    for f, h in man.items():
                        recorded_anywhere.setdefault(f, set()).add(h)

    drift, checked, notes = [], 0, []

    for fname, doc in freezes.items():
        # authoritative = base manifest, overridden by each amendment in order
        authoritative, origin = {}, {}
        for k, man in manifests_in(doc):
            for f, h in man.items():
                authoritative[f] = h
                origin[f] = f"{fname}:{k}"
        for am in doc.get("amendments", []):
            if not isinstance(am, dict):
                continue
            aid = am.get("id", "?")
            for k, man in manifests_in(am):
                for f, h in man.items():
                    authoritative[f] = h
                    origin[f] = f"{fname}:amendment {aid}"

        for f, expect in authoritative.items():
            got = sha256(os.path.join(DIR, f))
            checked += 1
            if got is None:
                drift.append((fname, f, "FILE MISSING", origin[f]))
            elif got != expect:
                drift.append((fname, f, f"got {got[:12]} want {expect[:12]}", origin[f]))

        # files this freeze asserts were untouched by it
        for f, expect in (doc.get("prior_manifest_sha256_observed") or {}).items():
            got = sha256(os.path.join(DIR, f))
            checked += 1
            if got is None:
                drift.append((fname, f, "FILE MISSING", f"{fname}:prior_manifest"))
            elif got != expect:
                if got in recorded_anywhere.get(f, set()):
                    notes.append(
                        f"{fname}: prior_manifest observation for {f} superseded by a "
                        f"recorded amendment elsewhere (current {got[:12]} is recorded)")
                else:
                    drift.append((fname, f, f"got {got[:12]} want {expect[:12]} "
                                            f"and NO recorded amendment names this hash",
                                  f"{fname}:prior_manifest"))

    for n in notes:
        print("NOTE  " + n)
    if drift:
        for fz, f, why, org in drift:
            print(f"DRIFT {f}  [{why}]  authority={org}")
        print(f"\nUNRECORDED_DRIFT: {len(drift)} of {checked} checks failed "
              f"across {len(freezes)} freeze files")
        return 2
    print(f"VERIFIED: {checked} checks across {len(freezes)} freeze files, "
          f"{len(notes)} recorded supersession(s), zero unrecorded drift")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(__doc__)
        sys.exit(4)
    sys.exit(main())
