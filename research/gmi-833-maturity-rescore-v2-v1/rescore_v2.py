#!/usr/bin/env python3
"""GMI #833 maturity rescore v2 — tranche 2 scorer (legacy corpus + arrivals).

Frozen by FREEZE_V2.md (commit f1b6ea7d, source authority d624c617).
Stdlib-only, deterministic, fails closed on every FREEZE_V2 §7 control.
Judgment tables live in judgments_v2.py (human-adjudicated, validated here).
"""
import hashlib
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)  # .../research
REPO = os.path.dirname(RESEARCH)  # worktree root
CENSUS_PATH = os.path.join(RESEARCH, "gmi-833-corpus-census-v1", "CORPUS_INDEX_V1.json")

CLAIM_CLASSES = {"THEOREM", "LAW", "CLAIM", "COROLLARY", "PROPOSITION", "LEMMA", "AXIOM"}

ARRIVALS = [
    "gmi-833-ai0-convergence-spine-v1",
    "gmi-833-aj0-foundation-scope-v1",
    "gmi-833-aj1-operational-process-base-v1",
    "gmi-833-aj2-operational-equivalence-v1",
    "gmi-833-aj3-distinguishability-v1",
    "gmi-833-aj4-process-organizations-v1",
    "gmi-833-aj5-g0-compilation-v1",
    "gmi-833-aj5-g0-lowering-v1",
    "gmi-833-aj6-aj8-development-value-intelligence-v1",
    "gmi-833-aj6-hst-layer-map-v1",
    "gmi-833-aj7-objective-provenance-v1",
    "gmi-833-aj8-intelligence-boundary-v1",
    "gmi-833-aj9a-known-family-benchmark-v1",
    "gmi-833-aj9b-k01-blind-recovery-v1",
    "gmi-833-aj9c-k02-blind-recovery-v1",
    "gmi-833-aj9d-k03-blind-recovery-v1",
    "gmi-833-aj9e-k04-blind-recovery-v1",
    "gmi-833-aj9f-k05-blind-recovery-v1",
    "gmi-833-aj9g-k06-blind-recovery-v1",
    "gmi-833-capability-abstention-v1",
    "gmi-833-capability-bounds-interactions-v1",
    "gmi-833-cognitive-reaudit-v1",
    "gmi-833-developmental-potential-evolvability-v1",
    "gmi-833-g0-grammar-growth-v1",
]

TYPED_EXCLUSIONS = {
    "gmi-833-corpus-audit-close-v1": "NO PRIMARY THEOREM — adjudication child, freeze-only audit object at the v2 frozen SHA (same typed reason as gmi-833-corpus-census-v1 in v1)",
    "gmi-833-maturity-rescore-v1": "NO PRIMARY THEOREM — tranche-1 score records; this programme's own audit object",
    "gmi-833-terminology-migration-v1": "NO PRIMARY THEOREM — terminology authority (same typed reason as gmi-833-tranche-ab-ac-lit in v1)",
    "gmi-833-corpus-census-v1": "NO PRIMARY THEOREM — corpus/provenance audit object (v1 typed exclusion, unchanged)",
    "gmi-833-tranche-ab-ac-lit": "NO PRIMARY THEOREM — terminology authority/crosswalk (v1 typed exclusion, unchanged)",
}

FROZEN_SOURCE_SHA = "d624c617d7a7c12f28e21c59a6ccca0e75bf34c0"
FREEZE_COMMIT = "f1b6ea7d"

# Frozen protocol map (FREEZE_V2 §4). support_kind -> (evidence_EV, maturity_M)
# M3_OVERRIDE is only legal when prior_free_recovery is True (v1 carve-out).
CEILING = {"EV0": 1, "EV1": 2, "EV2": 3, "EV3": 4, "EV4": 5, "EV5": 6}
MLEVEL = {"M0": 0, "M1": 1, "M2": 2, "M3": 3, "M4": 4, "M5": 5, "M6": 6}

REQUIRED_LIST_FIELDS = (
    "assumptions",
    "falsifiers",
    "strongest_parents",
    "forbidden_extrapolations",
    "citation_paths",
)
ABSENCE_MARKER = "UNREGISTERED_IN_LEGACY_SOURCE"


class FailClosed(Exception):
    pass


def die(msg):
    raise FailClosed(msg)


def git_blob(path):
    data = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def load_census_green_claims():
    idx = json.load(open(CENSUS_PATH))
    objs = idx["scientific_objects"]
    green = [
        o
        for o in objs
        if o.get("audit_disposition") == "GREEN"
        and o.get("id_kind") == "EXPLICIT"
        and o.get("object_class") in CLAIM_CLASSES
    ]
    return idx, green


def validate_legacy_blob(obj):
    p = os.path.normpath(os.path.join(REPO, obj["source_path"]))
    if not os.path.isfile(p):
        die("FAIL_CLOSED missing source file %s (object %s)" % (p, obj["object_id"]))
    if git_blob(p) != obj["source_blob"]:
        die("FAIL_CLOSED census blob mismatch for %s at %s" % (obj["object_id"], p))
    return p


def apply_protocol(j):
    """Frozen §4 map. Returns (evidence_EV, maturity_M). Fails closed on
    M-above-ceiling and on unsupported M3."""
    sk = j["support_kind"]
    m = j["maturity_M"]
    ev = j["evidence_EV"]
    if m != "UNKNOWN" and ev != "UNKNOWN":
        if MLEVEL[m] > CEILING[ev]:
            die("MATURITY_EVIDENCE_MISMATCH %s: %s above %s ceiling" % (j["result_id"], m, ev))
    if m == "M3" and not j.get("prior_free_recovery", False):
        die("M3_WITHOUT_P3_RELATIVE_EVIDENCE %s" % j["result_id"])
    if m == "M3" and sk not in ("EXACT_FINITE_CERTIFICATE", "FROZEN_HELDOUT"):
        die("M3_ON_UNGROUNDED_SUPPORT %s (%s)" % (j["result_id"], sk))
    if m == "M4" and sk != "FROZEN_HELDOUT":
        die("M4_WITHOUT_FROZEN_HELDOUT %s" % j["result_id"])
    if m in ("M5", "M6"):
        die("M5_M6_NOT_AVAILABLE_IN_TRANCHE2 %s (no EV4/EV5 receipts admitted by protocol)" % j["result_id"])
    return ev, m


def validate_record(j, census_obj=None):
    for c in j.get("citation_paths", []):
        if not os.path.exists(os.path.join(REPO, c)):
            die("FAIL_CLOSED citation path missing %s (%s)" % (c, j.get("result_id", "?")))
    for f in REQUIRED_LIST_FIELDS:
        v = j.get(f)
        if not isinstance(v, list) or not v:
            die("MISSING_REQUIRED_FIELD %s.%s" % (j.get("result_id", "?"), f))
    if census_obj is not None:
        for f in ("statement_excerpt", "scope_quantifier_class", "justification"):
            if not j.get(f):
                die("MISSING_REQUIRED_FIELD %s.%s" % (j["result_id"], f))
    apply_protocol(j)


def main():
    sys.path.insert(0, HERE)
    from judgments_v2 import JUDGMENTS_LEGACY, JUDGMENTS_ARRIVALS

    idx, green = load_census_green_claims()
    if len(green) != 173:
        die("FROZEN_LIST_DRIFT green claim census != 173: %d" % len(green))

    census_by_key = {}
    for o in green:
        pkg = o["source_path"].split("/")[1]
        census_by_key[(pkg, o["object_id"])] = o

    # --- Gap 1: legacy per-object ---
    rows = []
    jkeys = set(JUDGMENTS_LEGACY.keys())
    ckeys = set(census_by_key.keys())
    if jkeys - ckeys:
        die("UNKNOWN_OBJECT judgment for non-census object: %s" % sorted(jkeys - ckeys)[:3])
    if ckeys - jkeys:
        die("OMITTED_OBJECT census objects without judgment: %s" % sorted(ckeys - jkeys)[:3])

    n = 0
    for key in sorted(census_by_key.keys()):
        o = census_by_key[key]
        j = JUDGMENTS_LEGACY[key]
        validate_legacy_blob(o)
        n += 1
        rec = dict(j)
        rec.update(
            {
                "result_id": "GMI833_V2_LEGACY_%03d_%s" % (n, o["object_id"][:24].replace(" ", "_").replace("/", "_")),
                "package": key[0],
                "tranche": "LEGACY_173",
                "census_object_id": o["object_id"],
                "census_class": o["object_class"],
                "census_quantifier_class": o["quantifier_class"],
                "census_proof_mode": o["proof_evidence_mode"],
                "source_path": o["source_path"],
                "source_locator": o["source_locator"],
            }
        )
        validate_record(rec, census_obj=o)
        rows.append(rec)

    # --- Gap 2: arrivals, one primary per package ---
    if sorted(JUDGMENTS_ARRIVALS.keys()) != sorted(ARRIVALS):
        missing = set(ARRIVALS) - set(JUDGMENTS_ARRIVALS.keys())
        extra = set(JUDGMENTS_ARRIVALS.keys()) - set(ARRIVALS)
        die("ARRIVAL_LIST_MISMATCH missing=%s extra=%s" % (sorted(missing), sorted(extra)))
    n2 = 0
    for pkg in sorted(ARRIVALS):
        d = os.path.join(RESEARCH, pkg)
        if not os.path.isdir(d):
            die("FAIL_CLOSED missing arrival package dir %s" % pkg)
        j = JUDGMENTS_ARRIVALS[pkg]
        n2 += 1
        rec = dict(j)
        rec.update(
            {
                "result_id": "GMI833_V2_ARRIVAL_%02d_%s" % (n2, pkg.replace("gmi-833-", "")),
                "package": pkg,
                "tranche": "ARRIVALS_24",
            }
        )
        validate_record(rec, census_obj="arrival")
        rows.append(rec)

    rows.sort(key=lambda r: r["result_id"])

    # --- distributions / deltas (computed, never hand-entered) ---
    dist_m = Counter(r["maturity_M"] for r in rows)
    dist_ev = Counter(r["evidence_EV"] for r in rows)
    dist_delta = Counter(r["delta_kind"] for r in rows)
    dist_support = Counter(r["support_kind"] for r in rows)
    legacy = [r for r in rows if r["tranche"] == "LEGACY_173"]
    arrivals = [r for r in rows if r["tranche"] == "ARRIVALS_24"]
    downs = [r for r in rows if r["delta_kind"] == "DOWN_GENERATING"]
    for r in rows:
        if r["delta_kind"] not in ("MAINTAINS", "DOWN_GENERATING", "UNSCORED_WITH_REASON", "NEW_SCORE"):
            die("UNKNOWN_DELTA_KIND %s" % r["delta_kind"])
        if r["delta_kind"] == "UNSCORED_WITH_REASON" and not (r["maturity_M"] == "UNKNOWN" and r["evidence_EV"] == "UNKNOWN"):
            die("UNSCORED_WITH_REASON_MUST_BE_UNKNOWN %s" % r["result_id"])
    for r in downs:
        if not r.get("individually_verified"):
            die("DOWN_GENERATING_NOT_VERIFIED %s" % r["result_id"])
    overreach = [r["result_id"] for r in legacy if r.get("claim_evidence_gap") == "QUANTIFIER_EXCEEDS_EVIDENCE"]
    disagreement = [
        (r["result_id"], r["census_proof_mode"], r["support_kind"])
        for r in legacy
        if r["support_kind"] not in CENSUS_MODE_MAP.get(r["census_proof_mode"], {r["support_kind"]})
    ]
    maintains = [r for r in rows if r["delta_kind"] == "MAINTAINS"]
    n_spot = sum(1 for r in maintains if r.get("spot_verified"))
    spot_rate = (n_spot / len(maintains)) if maintains else 0.0
    if spot_rate < 0.10:
        die("SPOT_CHECK_RATE_BELOW_FROZEN_MINIMUM %.3f" % spot_rate)

    result = {
        "claim": "GMI_MATURITY_RESCORE_V2_AT_FROZEN_MAIN_SCOPE",
        "frozen_source_sha": FROZEN_SOURCE_SHA,
        "freeze_commit": FREEZE_COMMIT,
        "census_authority": "research/gmi-833-corpus-census-v1 (2fffb144 / result 861b1ba1)",
        "pre_existing_status": "all 173 legacy objects pre-date the 833 programme (census 2fffb144); all 24 arrival packages merged on main before the v2 freeze; this tranche labels pre-existing evidence, asserts no new result",
        "counts": {
            "legacy_objects_scored": len(legacy),
            "legacy_target": 173,
            "arrival_packages_scored": len(arrivals),
            "arrival_target": 24,
            "unscored_with_reason": sum(1 for r in rows if r["maturity_M"] == "UNKNOWN"),
            "typed_exclusions": len(TYPED_EXCLUSIONS),
        },
        "distribution_maturity": dict(sorted(dist_m.items())),
        "distribution_evidence": dict(sorted(dist_ev.items())),
        "distribution_delta": dict(sorted(dist_delta.items())),
        "distribution_support": dict(sorted(dist_support.items())),
        "down_generating_count": len(downs),
        "down_generating_ids": [r["result_id"] for r in downs],
        "quantifier_overreach_ids": overreach,
        "census_mode_disagreements": disagreement,
        "spot_check": {
            "maintains_cluster_size": len(maintains),
            "spot_verified": n_spot,
            "rate": round(spot_rate, 4),
            "frozen_minimum": 0.10,
        },
        "forbidden_promotions": [
            "M3_THROUGH_UNSUPPLIED_PRIORS",
            "ONTO_COMPLETENESS_IMPLIED_BY_MATURITY",
            "MATURITY_PROMOTED_BY_EXISTENCE_OF_SCORE_RECORD",
            "CORPUS_WIDE_MATURITY_CLOSURE",
            "RESCORED_THEOREMS_REPROVEN",
            "COMPLETE_GMI",
            "LEGACY_GREEN_PROMOTED_BEYOND_EVIDENCE",
        ],
    }

    with open(os.path.join(HERE, "THEOREM_SCORES_V2.json"), "w") as f:
        json.dump(rows, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(os.path.join(HERE, "RESULT_V2.json"), "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")

    print("legacy_scored=%d arrivals_scored=%d rows=%d" % (len(legacy), len(arrivals), len(rows)))
    print("maturity:", dict(sorted(dist_m.items())))
    print("evidence:", dict(sorted(dist_ev.items())))
    print("delta:", dict(sorted(dist_delta.items())))
    print("down_generating=%d overreach=%d mode_disagreements=%d" % (len(downs), len(overreach), len(disagreement)))
    print("spot_rate=%.3f (%d/%d)" % (spot_rate, n_spot, len(maintains)))
    print("OK")


CENSUS_MODE_MAP = {
    # census mechanical guess -> set of support kinds consistent with it
    "ANALYTIC_DEDUCTIVE": {"ANALYTIC_PROOF", "MECHANIZED_PROOF", "PROTOCOL_ONLY", "LEDGER_ENTRY"},
    "COMPUTER_ASSISTED_EXHAUSTIVE": {"EXACT_FINITE_CERTIFICATE"},
    "FINITE_EXECUTABLE_CERTIFICATE": {"EXACT_FINITE_CERTIFICATE"},
    "MECHANIZED_PROOF": {"MECHANIZED_PROOF", "ANALYTIC_PROOF"},
    "STATISTICAL_EXPERIMENT": {"SAMPLED_STATISTICAL", "FROZEN_HELDOUT", "EMPIRICAL_UNFROZEN"},
    "EMPIRICAL_EXPERIMENT": {"SAMPLED_STATISTICAL", "FROZEN_HELDOUT", "EMPIRICAL_UNFROZEN"},
    "PROTOCOL_ONLY": {"PROTOCOL_ONLY", "LEDGER_ENTRY", "NONE_FOUND"},
}


if __name__ == "__main__":
    try:
        main()
    except FailClosed as e:
        print("FAIL_CLOSED:", e, file=sys.stderr)
        sys.exit(2)
