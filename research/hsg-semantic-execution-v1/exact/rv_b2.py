"""RV-B2 -- close the T72 oracle targeting defect.

Protocol: RV_B_PROTOCOL_V1.json (frozen at 0918c25 / rebased 994abc1).

PREMISE CORRECTION, recorded in the freeze before this ran. The assignment asks
to re-target D19's revocation to true sources. D19 ALREADY does: exact/d19.py
revokes over w['sources'] in both its comparison loop and its missing-edge arm,
and w['legacy_leaves'] appears only inside the census, which drives no endpoint.
Re-targeting D19 would be a no-op producing a fabricated "no change" finding.
The defect is in the FROZEN T72 ORACLE, which revoked over w['leaves'].

So RV-B2 does the two pieces of work that actually answer the question:
  (i)  recompute EVERY D19 endpoint under BOTH target sets, which is what rules
       the 7% lifecycle margin in or out;
  (ii) repair oracles_d17.py t72() and report the before/after in full.

Python 3.8 compatible, stdlib only.
"""
from __future__ import annotations

import time

from exact.d19 import compare_arms
from exact.worlds_d19d20 import ow4n_worlds, ow4_with_blocker_field
from exact.oracles_d17 import t72

# Frozen BEFORE the numbers were seen (RV_B_PROTOCOL_V1.json).
SAVING_BAND = (0.035, 0.14)
BASELINE_SAVING = 0.07


def legacy_target_set(w):
    """The rule the frozen OW4 generator used to populate its `leaves` field:
    the first premise of every hyperedge, plus node 0."""
    if w.get("legacy_leaves"):
        return sorted(w["legacy_leaves"])
    if not w["edges"]:
        return sorted(w["nodes"][:1])
    return sorted(set(e["premises"][0] for e in w["edges"]) | {w["nodes"][0]})


def with_targets(w, targets):
    """compare_arms() reads the revocation target set from w['sources'], so a
    shallow copy with that field replaced re-runs the IDENTICAL code path over
    a different target set. Nothing else about the world changes."""
    w2 = dict(w)
    w2["sources"] = sorted(targets)
    return w2


def _totals(rows, tot):
    ratio = tot["a2_ops"] / float(max(1, tot["a1_ops"]))
    return {
        "revocation_subsets_exhausted": tot["pairs"],
        "accepted_set_agreement": "%d/%d" % (tot["accept_agree"], tot["pairs"]),
        "reopened_set_agreement": "%d/%d" % (tot["reopen_agree"], tot["pairs"]),
        "accepted_exact": tot["accept_agree"] == tot["pairs"],
        "reopened_exact": tot["reopen_agree"] == tot["pairs"],
        "a1_substitution_ops": tot["a1_ops"],
        "a2_recomputation_ops": tot["a2_ops"],
        "lifecycle_ratio_a2_over_a1": round(ratio, 4),
        "saving": round(ratio - 1.0, 4),
        "touched_state_total": tot["touched"],
        "alt_support_rescues": tot["alt_support_rescues"],
        "nodes_with_multi_support": tot["nodes_multi_support"],
        "worlds_exact": sum(1 for r in rows if r["exact_agreement"]),
        "worlds": len(rows),
    }


def run_rv_b2():
    t0w, t0c = time.time(), time.process_time()
    ctl = ow4_with_blocker_field()
    neg = ow4n_worlds()

    ctl_src = [with_targets(w, w["sources"]) for w in ctl]
    ctl_leg = [with_targets(w, legacy_target_set(w)) for w in ctl]
    neg_src = [with_targets(w, w["sources"]) for w in neg]
    neg_leg = [with_targets(w, legacy_target_set(w)) for w in neg]

    out_rows = {}
    res = {}
    for name, pop in (("control_true_sources", ctl_src),
                      ("control_legacy_leaves", ctl_leg),
                      ("ow4n_true_sources", neg_src),
                      ("ow4n_legacy_leaves", neg_leg)):
        rows, tot = compare_arms(pop, name)
        out_rows[name] = rows
        res[name] = _totals(rows, tot)

    src, leg = res["control_true_sources"], res["control_legacy_leaves"]
    s_src, s_leg = src["saving"], leg["saving"]
    lo, hi = SAVING_BAND
    sign_flip = (s_src > 0) != (s_leg > 0)
    sensitive = bool(sign_flip or s_leg < lo or s_leg > hi)

    # per-world target-set census, to show WHERE the two target sets differ
    census = []
    for w in ctl:
        srcs, legs = set(w["sources"]), set(legacy_target_set(w))
        census.append({"world": w["id"], "true_sources": sorted(srcs),
                       "legacy_targets": sorted(legs),
                       "legacy_only_noops": sorted(legs - srcs),
                       "sources_legacy_misses": sorted(srcs - legs),
                       "subsets_true": 2 ** len(srcs),
                       "subsets_legacy": 2 ** len(legs)})

    # ---- part (ii): the repaired oracle, before and after
    row_fixed = t72()
    row_legacy = t72(target="leaves")
    fixed_ok = (row_fixed["verdict"] == "PROVED_LOCAL"
                and row_fixed["property_green"])
    legacy_ok = (row_legacy["verdict"] == "PROVED_LOCAL"
                 and row_legacy["property_green"])

    def flips(row):
        return sorted((h["id"], bool(h["flipped"])) for h in row["hostiles"])

    oracle = {
        "file": "exact/oracles_d17.py",
        "change": "t72() revokes over TRUE SOURCES (nodes with no incoming "
                  "hyperedge) instead of the world's `leaves` superset; the "
                  "legacy path is retained behind target='leaves' for this "
                  "comparison only and is never the default.",
        "after_fix": {"detail": row_fixed["property_detail"],
                      "revocation_targets": row_fixed["revocation_targets"],
                      "revocation_target_count":
                          row_fixed["revocation_target_count"],
                      "verdict": row_fixed["verdict"],
                      "pass": fixed_ok, "hostiles": flips(row_fixed)},
        "before_fix": {"detail": row_legacy["property_detail"],
                       "revocation_targets": row_legacy["revocation_targets"],
                       "revocation_target_count":
                           row_legacy["revocation_target_count"],
                       "verdict": row_legacy["verdict"],
                       "pass": legacy_ok, "hostiles": flips(row_legacy)},
        "pass_unchanged": fixed_ok == legacy_ok,
        "hostile_flips_unchanged": flips(row_fixed) == flips(row_legacy),
    }

    verdict = ("TARGETING_SENSITIVE" if sensitive else "TARGETING_ROBUST")
    if not fixed_ok:
        verdict = "ORACLE_FIX_REGRESSED"

    out = {
        "experiment": "RV-B2", "protocol": "RV_B_PROTOCOL_V1.json",
        "freeze_commit_as_pushed": "0918c257800c634ba3615a59d152898b255555c0",
        "verdict": verdict,
        "premise_correction": {
            "assignment_assumed": "D19 revokes over the world's `leaves` field "
                                  "and should be re-targeted to true sources",
            "actual": "D19 ALREADY revokes over true sources (exact/d19.py, "
                      "both the comparison loop and the missing-edge arm). "
                      "`legacy_leaves` is read only by the census, which "
                      "drives no endpoint.",
            "consequence": "re-targeting D19 would have been a no-op and would "
                           "have produced a fabricated 'no change' result. The "
                           "defect is in the frozen T72 oracle instead.",
            "what_was_done_instead": "every D19 endpoint recomputed under BOTH "
                                     "target sets, plus a real repair of the "
                                     "T72 oracle."},
        "decision_rule_frozen_before_the_number_was_seen": {
            "baseline_saving_under_true_sources": BASELINE_SAVING,
            "band": list(SAVING_BAND),
            "rule": "TARGETING-SENSITIVE if the legacy-targeting saving falls "
                    "outside [0.035, 0.14] (a factor of two either way) or "
                    "changes sign; otherwise TARGETING-ROBUST."},
        "margin_question": {
            "saving_true_sources": s_src,
            "saving_legacy_leaves": s_leg,
            "sign_flipped": sign_flip,
            "outside_band": bool(s_leg < lo or s_leg > hi),
            "targeting_sensitive": sensitive,
            "conclusion": ("the 7% lifecycle margin is TARGETING-SENSITIVE and "
                           "must not be quoted without the qualifier"
                           if sensitive else
                           "the 7% lifecycle margin is TARGETING-ROBUST: it "
                           "survives the legacy target set and is not an "
                           "artifact of which nodes were revoked")},
        "endpoints_under_both_targetings": res,
        "endpoint_deltas_control": {
            "accepted_agreement": [src["accepted_set_agreement"],
                                   leg["accepted_set_agreement"]],
            "reopened_agreement": [src["reopened_set_agreement"],
                                   leg["reopened_set_agreement"]],
            "both_exact": bool(src["accepted_exact"] and src["reopened_exact"]
                               and leg["accepted_exact"]
                               and leg["reopened_exact"]),
            "alt_support_rescues": [src["alt_support_rescues"],
                                    leg["alt_support_rescues"]],
            "subsets_exhausted": [src["revocation_subsets_exhausted"],
                                  leg["revocation_subsets_exhausted"]],
            "lifecycle_ratio": [src["lifecycle_ratio_a2_over_a1"],
                                leg["lifecycle_ratio_a2_over_a1"]]},
        "target_set_census": census,
        "oracle_fix": oracle,
        "no_change_is_a_result": "a demonstration that corrected targeting "
                                 "changes no agreement endpoint is a genuine "
                                 "negative and is reported as such",
        "claim_ceiling": "P2 finite certificate over frozen tiny worlds; "
                         "revocation subsets exhausted under both target sets.",
        "wall_s": round(time.time() - t0w, 4),
        "cpu_s": round(time.process_time() - t0c, 4)}

    rec = []
    for name in sorted(out_rows):
        for r in out_rows[name]:
            rec.append({"job": "RV-B2", "arm": name, "world_id": r["world"],
                        "revocation_targets":
                            "true_sources" if "true_sources" in name
                            else "legacy_leaves",
                        "obligation_nodes": r["nodes"],
                        "revocation_subsets_exhausted":
                            r["revocation_subsets_exhausted"],
                        "accepted_set_agreement": r["accepted_set_agreement"],
                        "reopened_set_agreement": r["reopened_set_agreement"],
                        "exact_agreement": r["exact_agreement"],
                        "alt_support_rescues": r["alt_support_rescues"],
                        "a1_lifecycle_ops": r["a1_lifecycle_ops"],
                        "a2_lifecycle_ops": r["a2_lifecycle_ops"],
                        "negative_or_cannot_check_status":
                            r["detector"] if r["blockers"] else None,
                        "certificate_ceiling":
                            "P2 finite certificate, not universal proof"})
    return out, rec
