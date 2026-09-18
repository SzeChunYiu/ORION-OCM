# -*- coding: utf-8 -*-
"""AH4 hostiles, controls, nulls and the no-alarm case.

No gate depends on a bare `assert`; the file behaves identically under `-O`.

    python3 -I -O -B  test_ah4_organization_ladder_v1.py
"""

import json
import os
import sys
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ah4_organization_ladder_v1 as A   # noqa: E402

FINDINGS = []
HOSTILES = []


def hostile(name, detected, control_clean, detail):
    HOSTILES.append({"hostile": name, "detected": bool(detected),
                     "control_clean": bool(control_clean), "detail": detail})
    if not detected:
        FINDINGS.append("HOSTILE_NOT_DETECTED:" + name)
    if not control_clean:
        FINDINGS.append("CONTROL_NOT_CLEAN:" + name)


ORGS = A.base_organizations()
CELLFREE = set(A.signature(o) for o in ORGS if o.cells == 0)
CLASSES, INDEX = A.equivalence_classes(ORGS)
WORD_INDEX = dict((w, k) for k, w in enumerate(A.WORDS))
BASE_SIGS = set(A.signature(o) for o in ORGS)


def h_motif_key_ignores_state_change():
    def bad_multiplicity(org):
        counts = {}
        sites = ((0, 0), (0, 1)) if org.cells == 0 else ((0, 0), (0, 1), (1, 0), (1, 1))
        for (s, i) in sites:
            _ns, o = org.table[(s, i)]
            counts[o] = counts.get(o, 0) + 1
        return max(counts.values())
    bad = sum(1 for o in ORGS if bad_multiplicity(o) >= 2)
    good = sum(1 for o in ORGS if A.i1(o))
    hostile("motif_key_ignores_state_change", bad != good, good == 234,
            {"perturbed_pass": bad, "control_pass": good})


def h_i2_drops_behaviour_clause():
    bad = sum(1 for o in ORGS if o.cells >= 1)
    good = sum(1 for o in ORGS if all(A.i2_clauses(o, CELLFREE)))
    hostile("i2_drops_behaviour_clause", bad != good, good == 144,
            {"perturbed_pass": bad, "control_pass": good})


def h_composite_parallel_not_series():
    """Parallel wiring ignores A's output and must give a different irreducible count."""
    bad = 0
    total = 0
    for a in ORGS[:40]:
        sa = A.signature(a)
        for b in ORGS[:40]:
            sb = A.signature(b)
            total += 1
            parallel = tuple(sb[WORD_INDEX[w]] for w in A.WORDS)
            if parallel not in BASE_SIGS:
                bad += 1
    good = 0
    for a in ORGS[:40]:
        sa = A.signature(a)
        for b in ORGS[:40]:
            sb = A.signature(b)
            if A.i3_composite_signature(sa, sb, WORD_INDEX) not in BASE_SIGS:
                good += 1
    hostile("composite_parallel_not_series", bad != good, good > 0,
            {"parallel_irreducible": bad, "series_irreducible": good, "pairs": total})


def h_length_bound_too_short():
    short_words = [w for w in A.WORDS if len(w) <= 2]
    part = {}
    for o in ORGS:
        key = tuple(o.run(w) for w in short_words)
        part.setdefault(key, []).append(o.oid)
    hostile("length_bound_too_short", len(part) != len(CLASSES), len(CLASSES) == 148,
            {"short_bound_classes": len(part), "authority_classes": len(CLASSES)})


def h_adaptive_without_experience():
    nd = A.adaptive_witness(False)
    ad = A.adaptive_witness(True)
    hostile("adaptive_without_experience", len(nd.witness_triples()) == 0,
            len(ad.witness_triples()) == 4,
            {"negative_triples": len(nd.witness_triples()),
             "control_triples": len(ad.witness_triples())})


def h_governed_internal_guard():
    neg = A.Governed(False).hidden_channel_divergence()
    pos = A.Governed(True).hidden_channel_divergence()
    hostile("governed_internal_guard", not neg["outcomes_differ"], pos["outcomes_differ"],
            {"internal_guard_differs": neg["outcomes_differ"],
             "external_guard_differs": pos["outcomes_differ"]})


def h_population_without_channel():
    neg = A.Population(False).acquisition()
    pos = A.Population(True).acquisition()
    hostile("population_without_channel", neg["acquired_only_through_channel"] == 0,
            pos["acquired_only_through_channel"] > 0,
            {"without": neg["acquired_only_through_channel"],
             "with": pos["acquired_only_through_channel"]})


def h_grammar_rename_unit():
    neg = A.GrammarUnit((0,))
    pos = A.GrammarUnit((0, 1))
    nd = neg.description_delta(A.CORPUS)
    ns = neg.search_distance_delta(A.TARGET)
    pd = pos.description_delta(A.CORPUS)
    ps = pos.search_distance_delta(A.TARGET)
    hostile("grammar_rename_unit", nd == 0 and ns == 0, pd != 0 and ps != 0,
            {"rename_deltas": [nd, ns], "macro_deltas": [pd, ps]})


def h_prohibition_always_refuses():
    v = A.level_claim_verdict({"asserts": "INTELLIGENT", "capability_evidence": True,
                               "development_evidence": True})
    bad = (v != "ADMITTED_WITH_EVIDENCE")
    w = A.level_claim_verdict({"asserts": "INTELLIGENT", "capability_evidence": False,
                               "development_evidence": False})
    hostile("prohibition_always_refuses", not bad,
            w == "REFUSED__LEVEL_MEMBERSHIP_IS_NOT_INTELLIGENCE",
            {"with_evidence": v, "without_evidence": w})


def h_prohibition_never_refuses():
    w = A.level_claim_verdict({"asserts": "INTELLIGENT", "capability_evidence": True,
                               "development_evidence": False})
    hostile("prohibition_never_refuses",
            w == "REFUSED__LEVEL_MEMBERSHIP_IS_NOT_INTELLIGENCE",
            A.level_claim_verdict({"asserts": "AT_LEVEL_2"}) == "NOT_AN_INTELLIGENCE_CLAIM",
            {"partial_evidence": w})


def h_level_capability_monotone():
    levels = {}
    caps = {}
    for o in ORGS:
        a, b = A.i2_clauses(o, CELLFREE)
        levels[o.oid] = 2 if (a and b) else (1 if A.i1(o) else 0)
        caps[o.oid] = A.capability_vector(o.run)
    inversions = 0
    for x in levels:
        for y in levels:
            if levels[x] > levels[y] and A.dominates(caps[y], caps[x]):
                inversions += 1
    hostile("level_capability_monotone", inversions > 0, inversions == 1914,
            {"inversions": inversions})


def h_nearest_negative_zero_radius():
    seed = None
    for o in ORGS:
        if o.cells == 1 and A.i1(o):
            seed = o
            break
    res = A.nearest_negative(seed.description(), A.org_from_bits, A.i1)
    hostile("nearest_negative_zero_radius", res is not None and res["distance"] >= 1,
            res is not None and A.i1(A.org_from_bits(seed.description())),
            {"distance": None if res is None else res["distance"]})


def h_intermediate_layer_erased():
    counts = {"both": 0, "cell_only": 0}
    for o in ORGS:
        a, b = A.i2_clauses(o, CELLFREE)
        if a and b:
            counts["both"] += 1
        elif a:
            counts["cell_only"] += 1
    hostile("intermediate_layer_erased", counts["cell_only"] > 0,
            counts["both"] == 144 and counts["cell_only"] == 112, counts)


def no_alarm():
    quiet = {
        "behaviour_only_clause_population": sum(
            1 for o in ORGS if (not A.i2_clauses(o, CELLFREE)[0])
            and A.i2_clauses(o, CELLFREE)[1]),
        "i2_classes_split_by_description": sum(
            1 for members in CLASSES
            if len(set(A.i2_clauses(o, CELLFREE)[1] for o in members)) > 1),
        "class_count_mismatch": 0 if len(CLASSES) == 148 else 1,
    }
    bad = [k for k, v in quiet.items() if v != 0]
    if bad:
        FINDINGS.append("NO_ALARM_VIOLATED:" + ",".join(bad))
    return quiet


def main():
    for fn in (h_motif_key_ignores_state_change, h_i2_drops_behaviour_clause,
               h_composite_parallel_not_series, h_length_bound_too_short,
               h_adaptive_without_experience, h_governed_internal_guard,
               h_population_without_channel, h_grammar_rename_unit,
               h_prohibition_always_refuses, h_prohibition_never_refuses,
               h_level_capability_monotone, h_nearest_negative_zero_radius,
               h_intermediate_layer_erased):
        fn()
    quiet = no_alarm()
    m = A.measure()
    nulls = {"class_constancy": A.null_class_constancy(m),
             "level_labels": A.null_level_labels(m)}
    if nulls["level_labels"]["hits"]:
        FINDINGS.append("NULL_LEVEL_LABELS_REPRODUCED")
    if nulls["class_constancy"]["class_constant_hits"] > 20:
        FINDINGS.append("NULL_CLASS_CONSTANCY_NOT_INFORMATIVE")
    out = {"schema": "GMI833AH4OrganizationLadderTestReceiptV1",
           "hostiles": HOSTILES,
           "hostiles_declared": len(HOSTILES),
           "hostiles_detected": sum(1 for h in HOSTILES if h["detected"]),
           "controls_clean": sum(1 for h in HOSTILES if h["control_clean"]),
           "no_alarm": quiet,
           "nulls": nulls,
           "findings": FINDINGS,
           "status": "GREEN" if not FINDINGS else "RED"}
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        fh.write(json.dumps(out, indent=2, sort_keys=True, separators=(",", ": ")) + "\n")
    print(json.dumps({"status": out["status"], "hostiles_declared": out["hostiles_declared"],
                      "hostiles_detected": out["hostiles_detected"],
                      "controls_clean": out["controls_clean"],
                      "findings": FINDINGS}, indent=2, sort_keys=True))
    return 0 if not FINDINGS else 1


if __name__ == "__main__":
    sys.exit(main())
