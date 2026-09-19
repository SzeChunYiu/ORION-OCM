# -*- coding: utf-8 -*-
"""Cross-route and receipt-vs-live check for the AJ15 flagship package.

  * route A (BLIND_OUTCOME_V1.json) and route B (ORACLE_RESULT_V1.json) must agree on
    every B1 count, the atlas digest, every B2 terminal and the nulls they share;
  * route A's post-hoc (POSTHOC_RESULT_V1.json, LADDER_RESULT_V1.json) and route B's
    ladder oracle (LADDER_ORACLE_RESULT_V1.json) must agree;
  * with --live <dir>, receipts re-generated into <dir> must equal the committed ones
    (whole document; `universe_provenance` compared separately because it is read from git).

    python3 -I -B check_receipt_v1.py [--live DIR]
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



def load(path):
    return _load_json(path)


def cross_route(b, o, p, l, lo):
    bad = []
    for t, r in b["B1"]["regimes"].items():
        for k in ("exact_solvers", "with_state_dependent_output", "exact_solver_ids", "state_dependent_ids", "operational_classes_among_solvers"):
            if r[k] != o["B1"]["regimes"][t][k]:
                bad.append("B1.%s.%s" % (t, k))
    for k in ("presentations", "operational_classes", "pair_checks", "equivalent_pairs", "class_size_histogram",
              "development_max_distance", "pareto_front", "atlas_sha256"):
        if b["B1"][k] != o["B1"][k]:
            bad.append("B1.%s" % k)
    for t, r in b["B2"]["regimes"].items():
        if r["terminal"] != o["B2_S2"][t]["terminal"]:
            bad.append("B2.%s.terminal" % t)
        if r["terminal"] == "RECOVERED":
            if o["S1_solvers_certified_by_route_B"][t]["certified"] is not True:
                bad.append("B2.%s.S1_certification" % t)
            if bool(r["state_dependent_output"]) != bool(o["B2_S2"][t]["state_dependent_output"]):
                bad.append("B2.%s.state_dependence" % t)
    if b["nulls"]["N1"]["rate"] != o["nulls"]["N1"]["rate"]:
        bad.append("N1")
    if b["nulls"]["N3"]["rate"] != o["nulls"]["N3"]["rate"]:
        bad.append("N3")
    if b["nulls"]["N2"]["B1"]["chance"] != o["nulls"]["N2_B1"]["chance"]:
        bad.append("N2")
    if b["verdict"] != "CONFIRMED" or o["verdict"] != "CONFIRMED":
        bad.append("verdict")
    for t in p["per_regime"]:
        for k in ("K02_fingerprint_passes", "unknown_channel"):
            if p["per_regime"][t][k] != lo["per_regime"][t][k]:
                bad.append("posthoc.%s.%s" % (t, k))
    if l["aj14_earned_badges"] != lo["aj14_earned_badges"]:
        bad.append("ladder.badges")
    if l["aj13"]["criteria_satisfied"] != lo["aj13_criteria_satisfied"]:
        bad.append("ladder.aj13")
    if p["status"] != "GREEN" or l["status"] != "GREEN" or lo["status"] != "GREEN":
        bad.append("posthoc/ladder status")
    if p["blind_outcome_sha256"] != sha256_of(os.path.join(HERE, "BLIND_OUTCOME_V1.json")):
        bad.append("posthoc pins a different blind outcome")
    return bad


def sha256_of(path):
    import hashlib
    return hashlib.sha256(_read_bytes(path)).hexdigest()


def compare_live(live_dir):
    bad = []
    for name in ("BLIND_OUTCOME_V1.json", "ORACLE_RESULT_V1.json", "POSTHOC_RESULT_V1.json",
                 "LADDER_RESULT_V1.json", "LADDER_ORACLE_RESULT_V1.json"):
        a = load(os.path.join(HERE, name))
        lp = os.path.join(live_dir, name)
        if not os.path.exists(lp):
            bad.append("%s: live receipt missing" % name)
            continue
        c = load(lp)
        if name == "BLIND_OUTCOME_V1.json":
            ua, uc = a.pop("universe_provenance"), c.pop("universe_provenance")
            for k in ua:
                if uc.get(k) is not None and uc[k] != ua[k]:
                    bad.append("%s: universe_provenance.%s" % (name, k))
        if name == "POSTHOC_RESULT_V1.json":
            # the live post-hoc pins the live blind outcome, whose bytes equal the committed one iff the
            # committed blind outcome reproduces; compare everything else strictly
            a.pop("blind_outcome_sha256")
            c.pop("blind_outcome_sha256")
        if a != c:
            bad.append("%s: live differs from committed" % name)
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", default=None)
    args = ap.parse_args(argv)
    b = load(os.path.join(HERE, "BLIND_OUTCOME_V1.json"))
    o = load(os.path.join(HERE, "ORACLE_RESULT_V1.json"))
    p = load(os.path.join(HERE, "POSTHOC_RESULT_V1.json"))
    l = load(os.path.join(HERE, "LADDER_RESULT_V1.json"))
    lo = load(os.path.join(HERE, "LADDER_ORACLE_RESULT_V1.json"))
    bad = cross_route(b, o, p, l, lo)
    if args.live:
        bad += compare_live(args.live)
    if bad:
        sys.stderr.write("RECEIPT CHECK FAILED: %s\n" % bad)
        return 1
    print("receipts agree across routes%s" % (" and match the live rerun" if args.live else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
