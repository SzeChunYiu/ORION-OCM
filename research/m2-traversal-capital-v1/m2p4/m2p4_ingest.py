#!/usr/bin/env python3
"""Copy an authored package into the repo VERBATIM, with per-file sha256 and a
provenance manifest. Ingest only — it runs no gate and makes no verdict.

The freeze's author_unit.isolation_procedure requires exactly this step: "authored
artifacts copied into the repo verbatim with per-file sha256 and a provenance manifest
(spawn timestamp, spec sha256, isolation note); never edited by this lane after the
session ends". M2-P2 and M2-P3 performed it by hand, leaving no committed tool, so the
most integrity-critical copy in the protocol was the least reproducible step.

Refusals (distinct exit codes, never warnings):
  2  the studio holds anything other than exactly the three required files
  3  a required file is missing or empty
  4  the destination already exists (an ingest never overwrites a package)
  5  the spec does not hash to the frozen sha256
  6  the provenance manifest itself carries taxonomy tokens
  7  the taxonomy scanner could not be loaded, so the manifest is unverifiable
"""
import argparse, hashlib, io, json, os, shutil, sys, time
from pathlib import Path

SPEC_SHA = "382e6152fcdf9569039a14e46eae45fcc8609ab8b70d628e605c688ed71f64ea"
REQUIRED = ("emit_worlds.py", "worlds.jsonl", "AUTHOR_NOTES.md")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", required=True, help="the author's scratch directory")
    ap.add_argument("--into", required=True, help="destination inside the repo (must not exist)")
    ap.add_argument("--spec", required=True, help="the frozen neutral spec")
    ap.add_argument("--session-note", default="", help="isolation note recorded verbatim")
    a = ap.parse_args()

    studio, into, spec = Path(a.studio), Path(a.into), Path(a.spec)

    spec_sha = sha256_file(spec)
    if spec_sha != SPEC_SHA:
        print("REFUSE: spec sha256 %s != frozen %s" % (spec_sha[:16], SPEC_SHA[:16]))
        return 5

    present = sorted(p.name for p in studio.iterdir() if p.is_file())
    extra = [n for n in present if n not in REQUIRED]
    missing = [n for n in REQUIRED if n not in present]
    if extra or missing:
        print(json.dumps({"refuse": "studio contents are not exactly the three required files",
                          "present": present, "missing": missing, "unexpected": extra}, indent=1))
        return 2
    for n in REQUIRED:
        if (studio / n).stat().st_size == 0:
            print("REFUSE: %s is empty" % n)
            return 3
    if into.exists():
        print("REFUSE: destination already exists: %s" % into)
        return 4

    into.mkdir(parents=True)
    digests = {}
    for n in REQUIRED:
        shutil.copy2(studio / n, into / n)                     # verbatim, never edited
        src, dst = sha256_file(studio / n), sha256_file(into / n)
        if src != dst:
            print("REFUSE: copy of %s is not byte-identical" % n)
            return 3
        digests[n] = dst

    manifest = {
        # NO lane identifier here. This manifest is written INTO the authored directory,
        # and the stage-2 orchestrator scans every file in that directory with the 219-token
        # taxonomy hostile. A lane token would void the package as AUTHORSHIP_CONTAMINATED --
        # contamination by the ingest step, not by the author. (M2-P2/M2-P3 manifests also
        # live in authored/ and pass precisely because they carry no T6/T7 token.)
        "schema": "OCM_M2P4_AUTHORED_PACKAGE_PROVENANCE_V1",
        "owner_issue": 165, "hardening_parent": 323,
        "status": "INGEST_ONLY_NOT_A_GATE_AND_NOT_A_SCORED_RUN",
        "ingested_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "studio_directory": str(studio),
        "studio_outside_repository": not studio.resolve().is_relative_to(Path.cwd().resolve()),
        "neutral_spec": {"file": str(spec), "sha256": spec_sha},
        "artifacts_sha256": digests,
        "isolation_note": a.session_note or (
            "fresh model session, no inherited conversation context, given ONLY the frozen "
            "neutral spec verbatim in the spawn prompt; no repository access, no web or search "
            "tool, work confined to the studio directory. Isolation is by instruction, not "
            "enforcement — recorded as such, never claimed as mechanical."),
        "human_gate_label": "HUMAN_GATE_BYPASSED__MODEL_PROXY",
        "independence_scope": (
            "same model family as this lane and as M2-P3; session/context/spec-only isolation. "
            "This package does NOT advance author independence and must never be reported as doing so."),
        "never_edited_after_ingest": (
            "these three files are the artifact of record; any defect re-runs the author unit or "
            "becomes CANNOT_CHECK — they are never patched in place"),
    }
    # self-scan: the manifest joins the authored artifacts in the stage-2 taxonomy scan,
    # so it must itself be clean. Refuse rather than emit a package that voids on ingest.
    blob = json.dumps(manifest, indent=1) + "\n"
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "m2p2"))
        import m2p2_taxa as _taxa
        _tiers = _taxa.build_token_list()
        _hits = _taxa.scan_text(blob, _taxa._patterns(_tiers))
        if _hits:
            shutil.rmtree(into)
            print("REFUSE: the provenance manifest carries taxonomy tokens %s -- writing it "
                  "would void the package as AUTHORSHIP_CONTAMINATED by the ingest step"
                  % [h["token"] for h in _hits])
            return 6
        manifest_scan = "CLEAN (%d tokens checked)" % sum(len(v) for v in _tiers.values())
    except ImportError as e:
        # A could-not-check must NEVER be recorded as a checked-and-fine. If the scanner
        # cannot be loaded we cannot know whether this manifest would void the package,
        # so refuse outright rather than emit an unverified one.
        shutil.rmtree(into)
        print("REFUSE: taxonomy scanner could not be loaded (%s) -- the manifest cannot be "
              "self-checked, so the package is not written" % e)
        return 7
    manifest["manifest_taxonomy_self_scan"] = manifest_scan
    io.open(into / "PROVENANCE.json", "w", encoding="utf-8").write(
        json.dumps(manifest, indent=1) + "\n")

    print(json.dumps({"ingested_into": str(into), "artifacts": digests,
                      "spec_sha256": spec_sha,
                      "next": "run m2p4_check.py --repo . --authored-dir %s --out-dir <stage2>" % into},
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
