"""Build ISSUE_833_RECONCILIATION_BODY_RESIDUAL_V1.json from a LIVE body fetch.

This package closes no row, so `replacements` is empty by construction and the
three rows appear under `rows_deliberately_left_open` with the exact quantity
that keeps each open. The live body is re-fetched so that every `old` string is
byte-exact at the moment the artifact is written, and each frozen row is required
to still be present, still unchecked, and still under its frozen anchor.

THIS SCRIPT NEVER EDITS THE ISSUE BODY.

  python3 -I -B build_reconciliation_v1.py               # fetch with gh
  python3 -I -B build_reconciliation_v1.py --body-file F  # use a saved fetch
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = json.load(open(os.path.join(HERE, "FREEZE_ROWS_V1.json")))
RESULT_PATH = os.path.join(HERE, "RESULT_V1.json")
OUT = os.path.join(HERE, "ISSUE_833_RECONCILIATION_BODY_RESIDUAL_V1.json")

FORBIDDEN = json.load(open(os.path.join(HERE, "MANIFEST_V1.json")))["forbidden_promotions"]


def fetch_body():
    proc = subprocess.Popen(
        ["gh", "issue", "view", "833", "--repo", "SzeChunYiu/ORION-OCM",
         "--json", "body", "-q", ".body"], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise SystemExit("gh fetch failed: %s" % err.decode("utf-8", "replace"))
    return out.decode("utf-8")


def locate(body, anchor, old):
    """Assert `old` occurs exactly once, unchecked, after `anchor`."""
    lines = body.split("\n")
    if lines.count(old) != 1:
        raise SystemExit("row not uniquely present (%d occurrences): %r"
                         % (lines.count(old), old))
    if anchor not in lines:
        raise SystemExit("anchor absent: %r" % anchor)
    if lines.index(anchor) > lines.index(old):
        raise SystemExit("row precedes its anchor: %r" % old)
    # the next anchor after this one must come after the row
    after = [i for i, l in enumerate(lines)
             if l.startswith("# ") and i > lines.index(anchor)]
    if after and after[0] < lines.index(old):
        raise SystemExit("row sits under a later anchor: %r" % old)
    return lines.index(old)


def main(argv):
    if "--body-file" in argv:
        body = open(argv[argv.index("--body-file") + 1], encoding="utf-8").read()
    else:
        body = fetch_body()
    result = json.load(open(RESULT_PATH))
    ra = result["ROW_A"]
    rk = result["ROW_K"]
    rl = result["ROW_L"]

    evidence = {
        "ROW_A": ("governing verb `Replace`; the audited term still occurs %d times "
                  "in %d of %d flagship files at source_main (scope S3, the four "
                  "terminology-authority packages excluded because the row's own "
                  "`preserving exact legacy mappings` clause requires their %d "
                  "occurrences to remain). %d of the %d residual files are pinned by "
                  "content hash in another package's manifest, so the repair is the "
                  "migration lane's, not a single tranche's mass edit. RA-1/RA-2/RA-3."
                  % (ra["RA-1"]["governing_residual"],
                     ra["RA-1"]["scopes"]["S3"]["files_with_hits"],
                     ra["RA-1"]["scopes"]["S3"]["files_scanned"],
                     ra["RA-2"]["required_to_remain_hits"],
                     ra["RA-3"]["content_hash_pinned_files"],
                     ra["RA-3"]["residual_files"])),
        "ROW_K": ("obstruction proven structural at this scope. Under the "
                  "protocol-conservative bridge CB-PROTO — truthful by construction, "
                  "so no registration law is fitted — `F` emits %d non-degenerate "
                  "world-invariant point predictions on %d registered inputs across "
                  "all three real populations, both routes agreeing, while the same "
                  "counter returns 1680/3408/3472 under the parent's registered law "
                  "and reproduces the parent's published 3872/2400 on SIGMA_SYN2/"
                  "SIGMA_ARCH2. KE-3's 0-of-161632 is conditioned on truthfulness, "
                  "which held on 73 of 96 systems selected by the measured outcome. "
                  "A fourth fitted law is the terminal FREEZE_V3_ADDENDUM section 6 "
                  "pre-registered and is not attempted. BR-1/BR-2/BR-3."
                  % (rk["BR-2"]["non_degenerate_total"], rk["BR-2"]["inputs_total"])),
        "ROW_L": ("futurity is custody, not sampling. Under the criterion FFA-1 "
                  "(dated, posterior to the frozen prediction, exogenous, "
                  "independently attested), %d of %d candidate families reachable "
                  "in-session are admissible; the checker is validated in both "
                  "directions (a constructed admissible candidate is admitted, three "
                  "clause-failing candidates are rejected) and the absence is "
                  "re-established exhaustively: 0 blobs introduced after the freeze "
                  "outside this package. Anything this lane authors or pins from a "
                  "repo blob is out-of-sample but past. FC-1/FC-2."
                  % (rl["FC-2"]["admissible_candidates"],
                     rl["FC-2"]["candidates_checked"])),
    }

    left_open = []
    for rid in ("ROW_A", "ROW_K", "ROW_L"):
        row = ROWS["rows"][rid]
        locate(body, row["anchor"], row["old"])
        left_open.append({"row": row["old"], "anchor": row["anchor"],
                          "row_id": rid, "reason": evidence[rid]})

    for rid in ("ROW_M1", "ROW_M2", "ROW_M3"):
        text = ROWS["out_of_scope_rows"][rid]
        if body.split("\n").count(text) != 1:
            raise SystemExit("out-of-scope row changed shape: %r" % text)

    doc = {
        "schema": "GMI_ISSUE_RECONCILIATION_V2",
        "issue": 833,
        "package": "gmi-833-body-residual-akl-v1",
        "claim_ceiling":
            "GMI_833_BODY_RESIDUAL_AKL_DISPOSITION_AT_REGISTERED_FINITE_SCOPE",
        "source_main": result["source_main"],
        "freeze_commits": [result["freeze_commit"]],
        "body_fetch_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "body_fetch_bytes": len(body.encode("utf-8")),
        "replacements": [],
        "replacements_empty_because":
            "all three rows in scope are disposed OPEN under rules fixed in "
            "FREEZE_V1.md before any evidence existed. Closing fewer rows honestly "
            "is the outcome this tranche was built to be able to reach.",
        "rows_deliberately_left_open": left_open,
        # Named by id and hash only. The verbatim text of another lane's rows is
        # deliberately NOT reproduced here, so that no body-writing tool can find
        # a row string in this artifact and act on it.
        "rows_not_in_scope": [
            {"row_id": r,
             "row_sha256": hashlib.sha256(
                 ROWS["out_of_scope_rows"][r].encode("utf-8")).hexdigest(),
             "anchor": "# M. Cognitive-function derivation upgrade",
             "reason": "section M; owned by issue #926 and its draft pull request. "
                       "Not closed, not cited, not touched. The row text is given as "
                       "a hash rather than verbatim so this artifact cannot be used "
                       "to edit it."}
            for r in ("ROW_M1", "ROW_M2", "ROW_M3")],
        "forbidden_promotions": FORBIDDEN,
        "disclosed_post_freeze_deviations": [
            {"id": "D1", "materiality": "LOW",
             "what": "FREEZE_V1.md section 2.2 registered the expectation that the "
                     "resolution curve N(k) is 0 for every k < 32.",
             "measured": "N(3) = 1024 in rank-ascending order and N(12) = 352 in "
                         "rank-descending order.",
             "effect": "the expectation was wrong; the DECISION RULE (the row closes "
                       "iff N(0) >= 1) is untouched and N(0) = 0. The global reading "
                       "of BR-1 is withdrawn in the theorem note; the per-input "
                       "statement, which the same freeze registered, is what is "
                       "claimed."},
            {"id": "D2", "materiality": "LOW",
             "what": "FREEZE_V1.md section 5 registered NULL_UNIFORM with the "
                     "expectation that the true census is >= every randomized census.",
             "measured": "the randomized bridges are fully RESOLVED rather than "
                         "coarse, so 14 of 200 seeds emit non-degenerate points, up "
                         "to 3456, while the truthful bridge emits 0.",
             "effect": "the registered inequality direction was wrong. What the null "
                       "establishes is stronger and is what is reported: a census of "
                       "0 is a property of truthfulness, not of an instrument stuck "
                       "at 0."},
        ],
        "issue_body_edited_by_this_package": False,
    }
    with open(OUT, "w") as fh:
        fh.write(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print("wrote %s: %d replacements, %d rows left open, %d out of scope"
          % (os.path.basename(OUT), len(doc["replacements"]),
             len(left_open), len(doc["rows_not_in_scope"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
