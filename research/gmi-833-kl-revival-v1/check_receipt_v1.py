"""Receipt gate: the committed RESULT_V1.json / ORACLE_RESULT_V1.json must be
reproduced by a fresh run on the stable quantities, the two routes must agree,
every applicable hostile must be detected, and the nulls must be beaten.
Host-dependent fields (byte re-verification of off-repository sources, the
commit-chain timestamps, hostile HK6's process exits) are compared only where
both runs carry them.  Corpus-wide totals are never gated.

Usage: python3 -I -B check_receipt_v1.py --route-a A.json --route-b B.json
Exit 0 pass, 1 fail, 2 UNREACHABLE (a committed receipt is missing).
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

STABLE_K = ("census", "census_matches_frozen", "resolved_machines", "committed_cells",
            "positive_controls", "frozen_stream", "truthfulness", "soundness", "decision", "bridge",
            "receipt", "parent_code_unchanged", "parent_file_blob_sha")
STABLE_L = ("custody", "tally", "scores", "decision", "record", "ps1_replay",
            "freeze_committer_time_utc", "checker_validation")
STABLE_B_K = ("census", "truthful", "soundness", "resolved_machines", "committed_cells", "proto_census",
              "PK1_v3_point_law", "PK2_cb_proto", "bridge_summary", "stream_sha256_route_a_format",
              "untruthful_machines")
STABLE_B_L = ("admissible", "EP1_hits", "scored", "scores", "custody", "ps1_replay", "freeze_time_utc",
              "all_pilots_ok", "all_sources_ok")
DROP = ("hostiles", "null", "bytes_reverification", "commit_chain", "first_violation")


def load(path):
    with open(path) as h:
        return json.load(h)


def strip(obj):
    if isinstance(obj, dict):
        return dict((k, strip(v)) for k, v in obj.items() if k not in DROP)
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--route-a", required=True)
    ap.add_argument("--route-b", required=True)
    args = ap.parse_args(argv)
    ok = True
    committed_a = os.path.join(HERE, "RESULT_V1.json")
    committed_b = os.path.join(HERE, "ORACLE_RESULT_V1.json")
    if not (os.path.exists(committed_a) and os.path.exists(committed_b)):
        print("UNREACHABLE: committed receipts missing")
        return 2
    a_new, a_old = load(args.route_a), load(committed_a)
    b_new, b_old = load(args.route_b), load(committed_b)
    for key in STABLE_K:
        if strip(a_new["row_K"].get(key)) != strip(a_old["row_K"].get(key)):
            print("FAIL: route A row_K.%s differs from committed receipt" % key)
            ok = False
    for key in STABLE_L:
        if strip(a_new["row_L"].get(key)) != strip(a_old["row_L"].get(key)):
            print("FAIL: route A row_L.%s differs from committed receipt" % key)
            ok = False
    for key in STABLE_B_K:
        if strip(b_new["row_K"].get(key)) != strip(b_old["row_K"].get(key)):
            print("FAIL: route B row_K.%s differs from committed receipt" % key)
            ok = False
    for key in STABLE_B_L:
        if strip(b_new["row_L"].get(key)) != strip(b_old["row_L"].get(key)):
            print("FAIL: route B row_L.%s differs from committed receipt" % key)
            ok = False
    # Hostiles and nulls: the live run must detect / beat them, and the
    # committed run must have recorded the same verdicts (process exits aside).
    for row in ("row_K", "row_L"):
        for name, h in (a_new[row].get("hostiles") or {}).items():
            old = (a_old[row].get("hostiles") or {}).get(name)
            if old is None or old.get("detected") != h.get("detected") or old.get("applicable") != h.get("applicable"):
                print("FAIL: hostile %s.%s verdict differs from the committed receipt" % (row, name))
                ok = False
    agreement = b_new.get("agreement", {})
    if not agreement.get("all", False):
        print("FAIL: routes disagree: %r" % agreement)
        ok = False
    if not b_old.get("agreement", {}).get("all", False):
        print("FAIL: committed route B receipt records disagreement")
        ok = False
    print("routes agree on %d row-K and %d row-L quantities; HK5 decided by route B: %r"
          % (len(agreement.get("row_K", {})), len(agreement.get("row_L", {})),
             agreement.get("HK5_route_disagreement_detected")))

    ck = a_new["row_K"]
    if ck.get("status") != "OK":
        print("FAIL: row K status %r" % ck.get("status"))
        ok = False
    else:
        if ck["census"]["nd2"] < 1:
            print("FAIL: ND-2 census is 0 -- the row-K quantity was not produced")
            ok = False
        if not ck["positive_controls"]["PK1_v3_point_law"]["exceeds_sb"]:
            print("FAIL: positive control PK-1 did not exceed SB-L*")
            ok = False
        if not ck["positive_controls"]["PK2_cb_proto"]["both_zero"]:
            print("FAIL: positive control PK-2 not zero")
            ok = False
        if not ck["frozen_stream"]["reproduced"]:
            print("FAIL: frozen stream not reproduced")
            ok = False
        for name, h in ck["hostiles"].items():
            if h["detected"] is None:
                continue
            if not (h["detected"] or (not h["applicable"] and name.startswith("HK3"))):
                print("FAIL: hostile %s not detected and not inapplicable-by-result" % name)
                ok = False
        if not ck["null"]["NULL_RANDOM_COMMIT"]["beaten"]:
            print("FAIL: row-K null not beaten")
            ok = False
        print("row K: ND-2 %d, ND-1 %d, truthful %d/%d, violating pairs %d, closes=%r"
              % (ck["census"]["nd2"], ck["census"]["nd1"], ck["truthfulness"]["truthful"],
                 ck["truthfulness"]["machines"], ck["soundness"]["violating_pairs"],
                 ck["decision"]["closes_pending_route_b"]))
    cl = a_new["row_L"]
    if cl.get("status") == "OK":
        if not cl["checker_validation"]["validated_both_directions"]:
            print("FAIL: custody checker not validated in both directions")
            ok = False
        if not cl["ps1_replay"]["ok"]:
            print("FAIL: PS-1 replay failed: %r" % cl["ps1_replay"]["checks"])
            ok = False
        for name, h in cl.get("hostiles", {}).items():
            if not (h["detected"] or not h["applicable"]):
                print("FAIL: hostile %s not detected" % name)
                ok = False
        if cl["null"]["NULL_RANDOM_SIGN"] is not None and not cl["null"]["NULL_RANDOM_SIGN"]["beaten"]:
            print("FAIL: row-L null not beaten")
            ok = False
        br = cl.get("bytes_reverification") or {}
        if br.get("bytes_available") and not br.get("all_consistent"):
            print("FAIL: off-repository bytes inconsistent with the record")
            ok = False
        print("row L: admissible %d/%d, EP-1 %d/%d, closes=%r"
              % (cl["custody"]["admissible"], cl["custody"]["of"], cl["tally"]["EP1_hits"],
                 cl["tally"]["scored_admissible_sources"], cl["decision"]["closes_pending_route_b"]))
    else:
        print("row L status %r (freeze in place)" % cl.get("status"))
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
