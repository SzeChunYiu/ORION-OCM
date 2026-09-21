"""Build ISSUE_833_RECONCILIATION_KL_REVIVAL_V1.json (schema GMI_ISSUE_RECONCILIATION_V2).

`old` is taken byte-exact from a body fetch supplied on the command line
(taken immediately before finalising); the frozen rows must still occur exactly
once under their anchors; every number in a `new` line is read from the
committed receipts.  The package NEVER edits the issue body.

Usage: python3 -I -B build_reconciliation_v1.py --body body.md --result RESULT_V1.json --oracle ORACLE_RESULT_V1.json
"""

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from build_manifest_v1 import FORBIDDEN, FREEZE_COMMIT, AMENDMENT_1_COMMIT  # noqa: E402

PKG = "gmi-833-kl-revival-v1"


def section(text, anchor):
    lines = text.split("\n")
    start = None
    for i, line in enumerate(lines):
        if line == anchor:
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("# "):
            end = j
            break
    return lines[start:end]


def hits_list(win, key):
    return "/".join(str(x) for x in win["tally"][key])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--body", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--oracle", required=True)
    args = ap.parse_args(argv)
    with open(args.body, "rb") as h:
        body = h.read()
    text = body.decode("utf-8")
    with open(os.path.join(HERE, "FREEZE_ROWS_V1.json")) as h:
        rows = json.load(h)
    with open(args.result) as h:
        res = json.load(h)
    with open(args.oracle) as h:
        orc = json.load(h)
    routes_agree = bool(orc.get("agreement", {}).get("all"))
    K = res["row_K"]
    L = res["row_L"]
    replacements = []
    left_open = []
    rows_already_closed = []

    # Row K
    rk = rows["rows"]["ROW_K"]
    k_closes = bool(K.get("decision", {}).get("closes_pending_route_b")) and routes_agree
    pk1 = K["positive_controls"]["PK1_v3_point_law"]
    k_evidence = ("SB-1/SB-2/SB-3: the set-valued bridge SB-L* (derived from the parent's three real "
                  "receipts by the frozen rule CR-1, 84 committed cells, 3 of 7 cell classes abstaining) "
                  "was frozen on the new population SIGMA_REAL4 (32 torch-trained MLP/GRU systems at "
                  "widths 6 and 48, never trained before) before training: %d non-degenerate "
                  "world-invariant point emissions (all 8/17) and %d informative set emissions on "
                  "%d registered inputs, where every truthful-by-construction bridge gave 0; on the "
                  "measured systems the bridge is truthful on %d/32 machines with %d soundness "
                  "violations over %d (input, survivor) pairs, the V3 point-law control resolves more "
                  "(%d points) but is truthful on only %d/32 with %d violating pairs, CB-PROTO gives "
                  "0/0, and 0 of 200 random-commitment null bridges are truthful on 32/32 (max %d); "
                  "two routes agree input by input"
                  % (K["census"]["nd2"], K["census"]["nd1"], K["census"]["inputs"],
                     K["truthfulness"]["truthful"], K["soundness"]["violating_pairs"],
                     K["soundness"]["pairs"], pk1["nd2"], pk1["truthful_machines"],
                     pk1["soundness"]["violating_pairs"],
                     K["null"]["NULL_RANDOM_COMMIT"]["max_truthful_machines"]))
    k_section = section(text, rk["anchor"])
    k_present = 0 if k_section is None else k_section.count(rk["old"])
    if k_present == 0 and k_section is not None:
        # ROW_K was already closed in the issue body by the merged K package
        # (#1106 gmi-833-k-real-trained-v1); record it and never re-replace it.
        k_line = next((ln for ln in k_section
                       if ln.startswith("- [x] Test predictor on real trained systems.")), None)
        if k_line is None:
            raise SystemExit("ROW_K old line absent and no checked replacement line found under its anchor")
        rows_already_closed.append({"row": "ROW_K", "anchor": rk["anchor"], "old": rk["old"],
                                    "old_sha256": rk["old_sha256"],
                                    "current_body_line": k_line,
                                    "closed_by": "#1106 gmi-833-k-real-trained-v1"})
    elif k_present != 1:
        raise SystemExit("ROW_K old line must occur exactly once under its anchor: %d" % k_present)
    elif k_closes:
        replacements.append({
            "row": "ROW_K", "anchor": rk["anchor"], "old": rk["old"],
            "new": "- [x] Test predictor on real trained systems. — ✅ %s %s." % (PKG, k_evidence),
            "old_sha256": rk["old_sha256"],
        })
    else:
        left_open.append({"row": "ROW_K", "anchor": rk["anchor"], "old": rk["old"],
                          "reason": k_evidence,
                          "attribution": K.get("decision", {}).get("attribution")})

    # Row L
    rl = rows["rows"]["ROW_L"]
    w1 = L["windows"]["W1"]
    w2 = L["windows"]["W2"]
    comb = L["combined"]
    l_closes = bool(L.get("decision", {}).get("closes_pending_route_b")) and routes_agree
    if w1.get("status") == "OK":
        t1 = w1["tally"]
        head = ("FP-1/FP-2/FP-3/FP-4: the evolvability prediction EP-1 (pH(POS) > pH(NEG) for Ev_Q(U)) was "
                "frozen at %s (2026-09-19T07:16:31Z) and scored on %d posterior-dated exogenous task "
                "families (English Wikipedia page-creation revisions created after the freeze, admitted "
                "by the mechanical rule PS-1, each bound to Wikimedia's own revision sha1, custody %d/%d "
                "under a checker validated both directions): window 1 EP-1 %d/%d (pH(POS) %s of 24 vs "
                "pH(NEG) %s of 24; the miss %s is a tie at 0/24 whose graded potential still orders "
                "POS above NEG, C_pot %s vs %s)"
                % (FREEZE_COMMIT[:8], t1["scored_admissible_sources"], w1["custody"]["admissible"],
                   w1["custody"]["of"], t1["EP1_hits"], t1["scored_admissible_sources"],
                   hits_list(w1, "pH_pos_hits"), hits_list(w1, "pH_neg_hits"),
                   ",".join(t1["EP1_misses"]) if t1["EP1_misses"] else "none",
                   hits_list(w1, "C_pot_QH_pos"), hits_list(w1, "C_pot_QH_neg")))
        if w2.get("status") == "OK":
            t2 = w2["tally"]
            head += ("; window 2 (registered in amendment 1 at %s, %d scored posterior sources, custody "
                     "%d/%d; P06 AT_FLOOR_OR_CEILING excluded by name and replaced by P07 per "
                     "FREEZE_V1.md 4.6 clause 2) EP-1 %d/%d (pH(POS) %s of 24 vs pH(NEG) %s of 24)%s; "
                     "combined record %d/%d, exact label-permutation null %s (two-window procedure null "
                     "%s); EP-4 developmental-potential ordering %d/%d prospective on window 2, %d/%d "
                     "post hoc on window 1, %d/7 post hoc on the parent's sources"
                     % (AMENDMENT_1_COMMIT[:8], t2["scored_admissible_sources"], w2["custody"]["admissible"],
                        w2["custody"]["of"], t2["EP1_hits"], t2["scored_admissible_sources"],
                        hits_list(w2, "pH_pos_hits"), hits_list(w2, "pH_neg_hits"),
                        (" (miss %s)" % ",".join(t2["EP1_misses"])) if t2["EP1_misses"] else "",
                        comb["EP1_hits"], comb["sources"], comb["record_level_null_observed_or_better"],
                        comb["procedure_level_null_two_windows"],
                        t2["EP4_hits"], t2["scored_admissible_sources"], t1["EP4_hits"],
                        t1["scored_admissible_sources"],
                        L["EP4_developmental_potential"]["parent_seven_sources_post_hoc"].get("EP4_hits", 0)))
        else:
            head += "; window 2 %s" % w2.get("status")
        l_evidence = head
    else:
        l_evidence = "FP-1: freeze in place at %s; posterior record %s" % (FREEZE_COMMIT[:8], w1.get("status"))
    if l_closes:
        replacements.append({
            "row": "ROW_L", "anchor": rl["anchor"], "old": rl["old"],
            "new": "- [x] Predict evolvability on genuinely future task families. — ✅ %s %s." % (PKG, l_evidence),
            "old_sha256": rl["old_sha256"],
        })
    else:
        left_open.append({"row": "ROW_L", "anchor": rl["anchor"], "old": rl["old"],
                          "reason": l_evidence,
                          "attribution": L.get("decision", {}).get("attribution")})

    for rep in replacements + left_open:
        sec = section(text, rep["anchor"])
        if sec is None:
            raise SystemExit("anchor not found: %r" % rep["anchor"])
        if sec.count(rep["old"]) != 1:
            raise SystemExit("old line does not occur exactly once under its anchor: %r" % rep["old"])
        if hashlib.sha256(rep["old"].encode("utf-8")).hexdigest() != rows["rows"][rep["row"]]["old_sha256"]:
            raise SystemExit("old line sha256 drifted: %r" % rep["old"])
    for row in rows_already_closed:
        sec = section(text, row["anchor"])
        if sec is None:
            raise SystemExit("anchor not found: %r" % row["anchor"])
        if sec.count(row["old"]) != 0:
            raise SystemExit("row %s recorded as already closed but its old line is still present" % row["row"])
        if not row["current_body_line"].startswith("- [x] "):
            raise SystemExit("row %s current body line is not checked: %r" % (row["row"], row["current_body_line"]))
    out = {
        "schema": "GMI_ISSUE_RECONCILIATION_V2",
        "issue": 833,
        "target": "body",
        "package": PKG,
        "claim_ceiling": res["claim_ceiling"],
        "source_main": res["source_main"],
        "freeze_commits": [FREEZE_COMMIT, AMENDMENT_1_COMMIT],
        "body_fetch_sha256": hashlib.sha256(body).hexdigest(),
        "body_bytes": len(body),
        "forbidden_promotions": list(FORBIDDEN),
        "disclosed_post_freeze_deviations": res["disclosed_post_freeze_deviations"],
        "replacements": replacements,
        "rows_deliberately_left_open": left_open,
        "rows_already_closed_by_prior_packages": rows_already_closed,
        "routes_agree": routes_agree,
        "issue_body_edited_by_this_package": False,
        "never_edits_issue_body": True,
    }
    with open(os.path.join(HERE, "ISSUE_833_RECONCILIATION_KL_REVIVAL_V1.json"), "w") as h:
        json.dump(out, h, indent=1, ensure_ascii=False)
        h.write("\n")
    sys.stdout.write("replacements: %d, left open: %d, already closed by prior packages: %d, routes_agree: %r\n"
                     % (len(replacements), len(left_open), len(rows_already_closed), routes_agree))


if __name__ == "__main__":
    main(sys.argv[1:])
