"""Close revival rows RV-1 and RV-4 in the TTAC living revival backlog.

The backlog belongs to another lane, so this re-reads the file immediately
before writing, applies only the two intended rows, and diffs old against new,
refusing unless EVERY changed line is one this script intended. A count
assertion alone would not protect a shared file from a concurrent edit.
"""
import collections, difflib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "REVIVAL_BACKLOG_V1.json")

CLOSURES = {
 "RV-1": {
  "status": "CLOSED_EARNED_TERMINAL",
  "chain_iteration": 2,
  "outcome": "PARENT_SUFFICIENT_EARNED_AT_A_DEEPER_LEVEL (success terminal)",
  "executed_as": "lane RV-B1, PR #291, merge f403bde",
  "result_anchor": "research/hsg-semantic-execution-v1/exact/results/RV_B1_RESULTS.json",
  "lever_effect": "incremental refinement cut ops to 0.840 of the rebuild arm, removing 16.0% of the construction overhead the attribution named. Equivalence guard 95 checks 0 failures; ceiling held 30/30; refinement counts identical to rebuild on all 30 worlds.",
  "cost_ratio_curve_across_grid": {
    "n_grid": [8, 12, 16, 20, 24],
    "rebuild_over_direct": [3.355, 6.297, 10.769, 12.493, 13.532],
    "incremental_over_direct": [4.316, 6.099, 9.471, 10.101, 10.007],
    "lever_gain_vs_rebuild": [-0.286, 0.031, 0.121, 0.191, 0.26],
    "reading": "the lever FLATTENS the curve: rebuild grows x4.033 across the grid, incremental only x2.319. Incremental has plateaued (10.101 -> 10.007) while rebuild is still climbing (12.493 -> 13.532). At the smallest n the lever is WORSE than rebuild (-28.6%): the predecessor index is a fixed setup surcharge too few refinement rounds cannot amortise. The curve never crosses 1.0."},
  "deeper_attribution": "MEASURED decomposition at the largest n: setup 31.0%, abstract search 24.8%, per-round incremental build 19.9%, counterexample validation 13.2%, verification 11.1%. The largest term is the one the lever cannot touch. The irreducible setup ALONE costs 1.267x the entire direct search and meets or exceeds it on 21 of 30 worlds, so it is a floor sitting above 1.0.",
  "crossing_condition": "crossing 1.0 would require the sound abstraction build to be sublinear in the concrete edge relation. Soundness forbids it: omitting any may-transition is the H-D20b under-approximation already shown to yield false abstraction certificates. Unreachable, not merely unmet, for a single reachability query.",
  "amortisation_probe": "a pre-registered multi-query arm (Q grid 1,2,4,8,16) found NO crossover: ratio falls 8.412 -> 2.493 monotonically and stops. Refinement drives the partition toward discrete (final blocks 81.2% of states, 6 of 30 fully discrete), and after refinement stops the marginal cost per query is 12.966 for the abstraction against 11.738 for direct. Amortisation self-defeats.",
  "grid_not_extended": "the frozen n grid is reported unchanged; extending it would be a new frozen study."},
 "RV-4": {
  "status": "CLOSED_QUESTION_ANSWERED",
  "chain_iteration": 2,
  "outcome": "TARGETING_SENSITIVE - the 7% lifecycle margin does NOT survive the targeting change",
  "executed_as": "lane RV-B2, PR #294, merge 905a720",
  "result_anchor": "research/hsg-semantic-execution-v1/exact/results/RV_B2_RESULTS.json",
  "premise_correction": "the dispatched lever asked to re-target D19 to true sources. D19 ALREADY revoked over true sources (exact/d19.py, both the comparison loop and the missing-edge arm); legacy_leaves was read only by the census, which drives no endpoint. Running the lever literally would have been a no-op producing a fabricated no-change result. The defect was in the frozen T72 ORACLE, which is what was repaired.",
  "margin_answer": "saving 0.0702 under true sources against 0.2487 under legacy targeting - three and a half times larger and far outside the band [0.035, 0.14] frozen before the number was seen. Legacy targeting INFLATES substitution's apparent advantage, because each structurally trivial target still forces a full recomputation on the A2 side while costing the substitution arm almost nothing. The corrected 7% is both the honest figure and the smaller one, so D19 erred conservatively.",
  "what_did_not_move": "every agreement endpoint is exact under BOTH target sets (50/50 and 74/74 on the control) and the control alternate-support rescue count is 40 either way. Targeting moves the COST endpoint only, never correctness. That is the useful negative.",
  "oracle_repaired": "exact/oracles_d17.py t72() now revokes true sources, computed inside the oracle since ow4_worlds() carries no sources field. 140 node checks over 23 targets became 113 over 18; pass and hostile flips unchanged; D17 still 14/14 with all flips OK; D18 untouched at agreement 1.0 over 360 checks."}}


def main():
    before_text = open(P, encoding="utf-8").read()
    before = json.loads(before_text, object_pairs_hook=collections.OrderedDict)
    d = json.loads(before_text, object_pairs_hook=collections.OrderedDict)

    seen = []
    for row in d["revivals"]:
        rid = row.get("revival_id")
        if rid in CLOSURES:
            if row.get("status") != "DISPATCHED":
                print("REFUSED: %s is %s, expected DISPATCHED"
                      % (rid, row.get("status")), file=sys.stderr)
                return 2
            row.update(CLOSURES[rid])
            seen.append(rid)
    if sorted(seen) != sorted(CLOSURES):
        print("REFUSED: expected rows %s, found %s"
              % (sorted(CLOSURES), sorted(seen)), file=sys.stderr)
        return 2

    by = collections.Counter(r.get("status") for r in d["revivals"])
    d["counts"]["by_status"] = dict(sorted(by.items()))
    d["counts"]["closed_by_lane_rv_b"] = sorted(seen)

    # ---- STRUCTURAL guard. A line-based check is fooled by re-indentation and
    # by nested list elements; this compares the PARSED documents instead, so a
    # concurrent edit anywhere outside the two intended rows is refused.
    problems = []
    for k in set(list(before) + list(d)):
        if k in ("revivals", "counts"):
            continue
        if before.get(k) != d.get(k):
            problems.append("top-level key changed: %s" % k)
    if [r.get("revival_id") for r in before["revivals"]] != \
            [r.get("revival_id") for r in d["revivals"]]:
        problems.append("revival row set or order changed")
    for b, a in zip(before["revivals"], d["revivals"]):
        rid = b.get("revival_id")
        if rid not in CLOSURES:
            if b != a:
                problems.append("untouched row modified: %s" % rid)
            continue
        changed_keys = set(k for k in set(list(b) + list(a))
                           if b.get(k) != a.get(k))
        unexpected = changed_keys - set(CLOSURES[rid])
        if unexpected:
            problems.append("row %s changed unintended keys: %s"
                            % (rid, sorted(unexpected)))
    cnt_changed = set(k for k in set(list(before["counts"]) + list(d["counts"]))
                      if before["counts"].get(k) != d["counts"].get(k))
    if cnt_changed - {"by_status", "closed_by_lane_rv_b"}:
        problems.append("counts changed unintended keys: %s"
                        % sorted(cnt_changed - {"by_status",
                                                "closed_by_lane_rv_b"}))
    if problems:
        print("REFUSED, structural guard:", file=sys.stderr)
        for p_ in problems:
            print("   ", p_, file=sys.stderr)
        return 3

    after_text = json.dumps(d, indent=1) + "\n"
    # format fidelity: the builder wrote indent=1, so a rewrite must not
    # reformat the untouched remainder of the file
    if json.dumps(before, indent=1) + "\n" != before_text:
        print("REFUSED: file is not indent=1 canonical; refusing to reformat",
              file=sys.stderr)
        return 3
    diff = [l for l in difflib.unified_diff(before_text.splitlines(),
                                            after_text.splitlines(),
                                            lineterm="", n=0)
            if (l.startswith("+") or l.startswith("-"))
            and not l.startswith(("+++", "---"))]
    open(P, "w", encoding="utf-8").write(after_text)
    print("CLOSED %s | changed lines %d | statuses now %s"
          % (", ".join(sorted(seen)), len(diff), dict(sorted(by.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
