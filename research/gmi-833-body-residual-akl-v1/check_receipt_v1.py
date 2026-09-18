"""Receipt gate: the committed receipts must match a live re-derivation.

Byte comparison is deliberately NOT used. Two fields are legitimately history
dependent — how many commits exist after the freeze, and when a blob was
introduced — and a squash merge changes both without touching a single claim.
This gate re-derives the STABLE quantities live and requires exact equality.

Usage: python3 -I -B check_receipt_v1.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import body_residual_akl_v1 as A     # noqa: E402

RESULT = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
ORACLE = json.load(open(os.path.join(HERE, "ORACLE_RESULT_V1.json")))


def main():
    failures = []
    tree = A.tracked_tree(A.SOURCE_MAIN)
    live_a = A.row_a(tree)

    for scope in ("S1", "S2", "S3"):
        for key in ("files_scanned", "files_with_hits", "total_hits"):
            live = live_a["RA-1"]["scopes"][scope][key]
            rec = RESULT["ROW_A"]["RA-1"]["scopes"][scope][key]
            orc = ORACLE["ROW_A"][scope][key]
            if not (live == rec == orc):
                failures.append("ROW_A %s.%s live=%r receipt=%r route_b=%r"
                                % (scope, key, live, rec, orc))
    for key in ("required_to_remain_hits", "required_to_remain_files"):
        live = live_a["RA-2"][key]
        rec = RESULT["ROW_A"]["RA-2"][key]
        orc = ORACLE["ROW_A"][key]
        if not (live == rec == orc):
            failures.append("ROW_A %s live=%r receipt=%r route_b=%r"
                            % (key, live, rec, orc))
    for key in ("content_hash_pinned_files", "unpinned_files",
                "bare_basename_pins_rejected"):
        if live_a["RA-3"][key] != RESULT["ROW_A"]["RA-3"][key]:
            failures.append("ROW_A RA-3.%s live=%r receipt=%r"
                            % (key, live_a["RA-3"][key], RESULT["ROW_A"]["RA-3"][key]))
    if live_a["NULLS"]["absent_control_term_hits"] != 0:
        failures.append("ROW_A null control term is no longer absent")

    live_k = A.row_k()
    if live_k["BR-2"]["non_degenerate_total"] != \
            RESULT["ROW_K"]["BR-2"]["non_degenerate_total"]:
        failures.append("ROW_K census drifted")
    if live_k["BR-2"]["inputs_total"] != ORACLE["ROW_K"]["TOTAL"]["inputs"]:
        failures.append("ROW_K input total disagrees with route B")
    if ORACLE["ROW_K"]["TOTAL"]["world_invariant_non_degenerate"] != \
            live_k["BR-2"]["non_degenerate_total"]:
        failures.append("ROW_K route B census disagrees with route A")
    if not live_k["BR-1"]["holds"]:
        failures.append("ROW_K BR-1 no longer holds")
    for name, v in live_k["hostiles"]["HB1_positive_control"].items():
        if v["non_degenerate"] <= 0:
            failures.append("ROW_K positive control %s returns 0" % name)
        if v["non_degenerate"] != ORACLE["ROW_K"][name][
                "fitted_law_positive_control_non_degenerate"]:
            failures.append("ROW_K positive control %s disagrees across routes" % name)
    for name, expected in (("SIGMA_SYN2", 3872), ("SIGMA_ARCH2", 2400)):
        got = live_k["hostiles"]["HB1b_counter_validation"][name]["non_degenerate"]
        if got != expected:
            failures.append("ROW_K counter no longer reproduces the parent's %s "
                            "figure: %d != %d" % (name, got, expected))

    live_l = A.row_l(tree)
    if live_l["FC-2"]["admissible_candidates"] != 0:
        failures.append("ROW_L an in-session candidate became admissible")
    if not live_l["FC-1"]["all_fixtures_agree"]:
        failures.append("ROW_L the criterion fixtures no longer agree")
    if not live_l["FC-2"]["second_route_to_the_absence"]["no_exogenous_posterior_blob"]:
        failures.append("ROW_L an exogenous blob now postdates the freeze")

    recon = json.load(open(os.path.join(
        HERE, "ISSUE_833_RECONCILIATION_BODY_RESIDUAL_V1.json")))
    if recon["replacements"]:
        failures.append("the reconciliation claims a replacement; this package "
                        "closes no row")
    if len(recon["rows_deliberately_left_open"]) != 3:
        failures.append("the reconciliation does not carry exactly 3 open rows")

    if failures:
        sys.stderr.write("RECEIPT MISMATCH:\n")
        for f in failures:
            sys.stderr.write("  " + f + "\n")
        return 1
    print("receipt OK: two routes agree on every stable quantity; census 0 of %d; "
          "S3 residual %d; %d admissible future candidates"
          % (live_k["BR-2"]["inputs_total"],
             live_a["RA-1"]["governing_residual"],
             live_l["FC-2"]["admissible_candidates"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
