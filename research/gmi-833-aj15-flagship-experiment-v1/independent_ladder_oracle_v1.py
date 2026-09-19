# -*- coding: utf-8 -*-
"""AJ15 -- route B for the post-hoc stage.  Imports nothing from route A.

Re-derives, from the committed receipts and its own code:
  * the AJ13 six-conjunct stopping predicate as a flat table of tests over the
    flagship base recorded in LADDER_RESULT_V1.json#aj13_input;
  * the AJ14 badge ladder as a left fold over ordered gates;
  * the post-hoc per-regime fingerprint outcome, recomputed from the blind outcome ids
    with a second implementation of the persistent-state predicate (string machines);
and requires equality with route A's LADDER_RESULT_V1.json and POSTHOC_RESULT_V1.json.

    python3 -I -B independent_ladder_oracle_v1.py [--out LADDER_ORACLE_RESULT_V1.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

def _read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_text(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

REPO = os.path.dirname(os.path.dirname(HERE))

TAGS = {"MATHEMATICAL_FOUNDATION", "LOGIC/METATHEORY", "PHYSICAL_SUBSTRATE_LAW", "RESOURCE_MODEL", "VALUE/REQUIREMENT_INPUT"}
MECH = {"NEURON", "LAYER", "ATTENTION", "MEMORY", "PLANNER", "SEARCHER", "WORLD_MODEL", "BACKPROP", "TRANSFORMER", "SYMBOLIC_REASONER"}
ROLES = {"TYPE", "SEQUENCE", "PARALLEL", "NO_CHANGE", "SUBSTRATE_ADMISSIBILITY", "OPERATIONAL_OBSERVATION"}
LADDER = [
    ("GMI_CORE_FORMALIZED_AT_SCOPE", lambda e: all(e[k] == "SATISFIED_REGISTERED_SCOPE" for k in ("FOUNDATION", "GENERATION", "DEVELOPMENT", "RELEVANCE_CAPABILITY")) and e["BOUNDARIES"] == "EXPLICIT"),
    ("GMI_BOUNDED_ATLAS_COMPLETE_AT_SCOPE", lambda e: e["BOUNDED_ATLAS"]["status"] == "COMPLETE_REGISTERED_BOUND" and e["BOUNDED_ATLAS"]["terminal"] == "COMPLETE_GMI_ATLAS_AT_BOUND_B"),
    ("GMI_KNOWN_FAMILIES_BLINDLY_RECOVERED_AT_SCOPE", lambda e: e["RECOVERY"]["status"].startswith("ALL_11_REGISTERED_FAMILIES_RECOVERED") and e["RECOVERY"]["flagship_holdout_confirmed"] is True),
    ("GMI_SELECTION_LAWS_PROSPECTIVELY_VALIDATED_AT_SCOPE", lambda e: e["SELECTION"] == "PROSPECTIVE_FINITE_SYNTHETIC_SCOPE"),
    ("GMI_NOVEL_FORM_DISCOVERY_REPLICATED_AT_SCOPE", lambda e: e["DISCOVERY"]["novel_replication"] == "REPLICATED" and e["DISCOVERY"]["novel_form_claimed"] is True and bool(e["DISCOVERY"]["replication_receipt"])),
    ("FULL_GMI_THEORY_SUPPORTED_AT_DECLARED_SCOPE", lambda e: e["EVIDENCE"]["real_system_gate"] == "SATISFIED"),
]


def fold_ladder(e):
    earned = []
    for name, gate in LADDER:
        if not gate(e):
            break
        earned.append(name)
    return earned


def aj13_table(x):
    tests = [
        ("1_tagged", lambda: len(x["remaining_assumptions"]) > 0 and all(a["tag"] in TAGS for a in x["remaining_assumptions"])),
        ("2_no_named_mechanism_in_base", lambda: not any(b in MECH for b in x["operational_base"])),
        ("3_removal_has_loss_witness", lambda: set(x["aj1_loss_witnesses"].values()) == ROLES),
        ("4_survives_alternative_presentations", lambda: sum(1 for p in ("AJ5_", "AJ12_", "AJ15_") if any(s.startswith(p) for s in x["presentation_invariance_evidence"])) == 3),
        ("5_parent_ownership", lambda: x["parent_ownership_registered"] is True),
        ("6_descent_changes_domain", lambda: 0 < len(set(x["further_descent_classification"])) and set(x["further_descent_classification"]) <= (TAGS - {"RESOURCE_MODEL"})),
    ]
    res = {n: bool(f()) for n, f in tests}
    ok = all(res.values()) and x["requested_terminal"] != "ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN"
    return res, sum(res.values()), ("FOUNDATION_RELATIVE_GMI_CORE_STABLE_AT_REGISTERED_SCOPE" if ok else "STOPPING_RULE_NOT_SATISFIED")


# second implementation of the persistent-state predicate on B1 ids


def machine_string(mid):
    k = int(mid[1:])
    return "S" + format(k, "02b") if k < 4 else format(k - 4, "08b")


def step(m, s, x):
    if m[0] == "S":
        return 0, m[1 + x]
    p = 4 * s + 2 * x
    return int(m[p]), m[p + 1]


def facts(m):
    reach = {0}
    frontier = [0]
    while frontier:
        nxt = []
        for s in frontier:
            for x in (0, 1):
                n, _ = step(m, s, x)
                if n not in reach:
                    reach.add(n)
                    nxt.append(n)
        frontier = nxt
    dep = any(len({step(m, s, x)[1] for s in reach}) > 1 for x in (0, 1))
    upd = any(step(m, s, x)[0] != s for s in reach for x in (0, 1))
    return len(reach), dep, upd


def k02_at_scope(n_reach, dep, upd):
    return n_reach >= 2 and dep and upd


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "LADDER_ORACLE_RESULT_V1.json"))
    args = ap.parse_args(argv)
    blind = _load_json(os.path.join(HERE, "BLIND_OUTCOME_V1.json"))
    posthoc = _load_json(os.path.join(HERE, "POSTHOC_RESULT_V1.json"))
    ladder_a = _load_json(os.path.join(HERE, "LADDER_RESULT_V1.json"))

    res, n_ok, terminal = aj13_table(ladder_a["aj13_input"])
    earned = fold_ladder(ladder_a["aj14_evidence"])
    per_regime = {}
    for t, r in blind["B1"]["regimes"].items():
        passes = 0
        for mid in r["exact_solver_ids"]:
            n_reach, dep, upd = facts(machine_string(mid))
            if k02_at_scope(n_reach, dep, upd):
                passes += 1
        per_regime[t] = {"exact_solvers": len(r["exact_solver_ids"]), "K02_fingerprint_passes": passes,
                         "unknown_channel": len(r["exact_solver_ids"]) - passes}
    agree = {
        "aj13_criteria": n_ok == ladder_a["aj13"]["criteria_satisfied"] == 6,
        "aj13_terminal": terminal == ladder_a["aj13"]["terminal"],
        "aj14_badges": earned == ladder_a["aj14_earned_badges"],
        "posthoc_per_regime": all(per_regime[t]["K02_fingerprint_passes"] == posthoc["per_regime"][t]["K02_fingerprint_passes"]
                                  and per_regime[t]["unknown_channel"] == posthoc["per_regime"][t]["unknown_channel"]
                                  for t in per_regime),
        "posthoc_status_green": posthoc["status"] == "GREEN",
    }
    failures = [k for k, v in agree.items() if not v]
    out = {"schema": "AJ15_LADDER_ORACLE_RESULT_V1", "route": "B", "aj13_conjuncts": res,
           "aj13_criteria_satisfied": n_ok, "aj13_terminal": terminal, "aj14_earned_badges": earned,
           "per_regime": per_regime, "agreement": agree, "failures": failures,
           "status": "GREEN" if not failures else "RED"}
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"status": out["status"], "aj13": n_ok, "badges": len(earned), "failures": failures}, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
