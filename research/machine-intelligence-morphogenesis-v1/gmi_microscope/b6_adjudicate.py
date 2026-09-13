"""RV-377-180 -- mechanical scoring of the frozen B6 predictions D1a..D5.

Reads the arm receipts written by b6_development.run_arm and scores each frozen
prediction under GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md.
B6_ADJUDICATION_CORRECTION_V1.md records the V2 logical corrections and the
first-recovery evidence boundary; raw receipts and the freeze remain unchanged.

    python3 -m gmi_microscope.b6_adjudicate <host> [seeds]

Readings fixed here (stated so they are auditable, not silently chosen):
  * DISJ has no RESET arm of its own; the freeze shares CROSS's RESET as the baseline
    (same E_b, same seed), exactly as b6_development.summary does.
  * "RESET's seed spread" = max - min of the RESET arm's value over the three seeds,
    computed on B_morph for D3a and on B_dense for D2d.
  * D2d compares DISJ-CONTINUED's B_dense against the RESET B_dense of the SAME seed.
  * A majority requires two of the three frozen seeds. D2b excludes registered
    undetermined comparisons; D2d separately counts its literal "or UNDETERMINED"
    condition. Missing files or unresolved metadata do not satisfy a predicate.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
REVIVAL = "RV-377-180"
CORRECTION = "B6_ADJUDICATION_CORRECTION_V1"
RAW_CARRIERS = {"DENSE", "TABLE", "KVSTORE", "PROGRAM", "NONE"}
MEMORY_CLASSES = {"TABLE", "KVSTORE", "PROGRAM"}
SMOOTH1_OCCUPANTS = {"KVSTORE", "PROGRAM", "TABLE"}


def path(pair, arm, seed, host):
    if pair == "DISJ" and arm == "RESET":
        pair = "CROSS"          # shared baseline, same E_b and seed
    return os.path.join(RES, f"STAGE_B6_DEV_{pair}_{arm}_S{seed}_{host}.json")


def load(pair, arm, seed, host):
    p = path(pair, arm, seed, host)
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    fa = d.get("first_admissible") or {}
    fd = d.get("first_dense_admissible") or {}
    sd = d.get("seeding") or {}
    sc = (d.get("seeding") or {}).get("seed_carriers_raw") or []
    do = fd.get("origin")
    di = do[1] if isinstance(do, (list, tuple)) and len(do) > 1 and do[0] == "seed" else None
    carrier = (sc[di] if isinstance(sc, list) and type(di) is int and 0 <= di < len(sc) else None)
    fps = sd.get("seed_fingerprints")
    population_known = isinstance(fps, list) and bool(fps) and all(isinstance(x, str) and x for x in fps)
    return {
        "dense_root_kind": (do[0] if isinstance(do, (list, tuple)) and do else None),
        "dense_root_carrier": carrier if isinstance(carrier, str) and carrier in RAW_CARRIERS else None,
        "target_ecology": d.get("target_ecology"),
        "source_ecology": d.get("source_ecology"),
        "seed_population_sha256": (hashlib.sha256(json.dumps(fps, sort_keys=True).encode()).hexdigest()
                                   if population_known else None),
        "B_morph": fa.get("B_morph") if fa.get("found") is True else None,
        "found": fa.get("found") if type(fa.get("found")) is bool else None,
        "class": fa.get("carrier_atrophied") if fa.get("found") is True else None,
        "origin": fa.get("origin"),
        "B_dense": fd.get("B_morph") if fd.get("found") is True else None,
        "dense_found": fd.get("found") if type(fd.get("found")) is bool else None,
        "final_best": d.get("final_best_capability_standard"),
        "final_best_dense": (d.get("final_best_by_carrier") or {}).get("DENSE"),
    }


def spread(vals):
    """The registered whole-baseline spread; missing values are not a smaller baseline."""
    return max(vals) - min(vals) if vals and all(x is not None for x in vals) else None


def experiment_identity(row, arm, seed):
    """Identity evidence is valid only within this fixed frozen campaign."""
    target, population = row.get("target_ecology"), row.get("seed_population_sha256")
    if not isinstance(target, str) or not target or population is None:
        return None
    return target, arm, seed, population


def _tally(per_seed):
    """per_seed: seed -> True / False / None(undetermined)."""
    det = {s: v for s, v in per_seed.items() if v is not None}
    return sum(1 for v in det.values() if v), len(det), per_seed


def adjudicate(host, seeds=(0, 1, 2), validation_only=False):
    """validation_only=True runs the scorer on a partial seed set to check the
    instrument against real receipts. The frozen quantifier is ">= 2 of 3 seeds",
    so a run on fewer than three seeds can never be an adjudication: it is written
    to a separate file and stamped, never to the adjudication receipt."""
    if any(type(s) is not int for s in seeds) or len(set(seeds)) != len(seeds):
        raise SystemExit("REFUSED: distinct integer seed identities required")
    if set(seeds) != {0, 1, 2} and not validation_only:
        raise SystemExit("REFUSED: the freeze quantifies over exactly 3 seeds; "
                         "pass validation_only=True to inspect a partial set")
    R = {(p, a, s): load(p, a, s, host) for p in ("SAME", "CROSS", "DISJ")
         for a in ("RESET", "CONTINUED", "TWIN") for s in seeds}
    missing = sorted(f"{p}|{a}|S{s}" for (p, a, s), v in R.items() if v is None)
    out = {"schema": "StageB6AdjudicationV2", "correction": CORRECTION,
           "validation_only": bool(validation_only), "revival_record": REVIVAL, "host": host,
           "seeds": list(seeds), "missing_units": missing,
           "complete": not missing, "rows": {f"{p}|{a}|S{s}": v for (p, a, s), v in R.items() if v},
           "predictions": {}}

    def lt(pair, a, b, s):
        x, y = R[(pair, a, s)], R[(pair, b, s)]
        if not x or not y or x["B_morph"] is None or y["B_morph"] is None:
            return None
        return x["B_morph"] < y["B_morph"]

    def rec(pid, per_seed, rule, detail=None):
        """A ">= 2 of 3" predicate settles when every completion agrees:
        two hits settle it HELD whatever the third seed does, and it is FAILED only
        once two or more seeds are known NOT to satisfy it. Anything in between is
        PENDING, never FAILED -- a missing unit is not a refutation."""
        ok, n, _ = _tally(per_seed)
        n_false = sum(1 for v in per_seed.values() if v is False)
        if validation_only:
            verdict = "NOT_SCORED__PARTIAL_SEED_SET"
        elif ok >= 2:
            verdict = "HELD"
        elif len(per_seed) - n_false < 2:
            verdict = "FAILED"
        elif n < len(per_seed):
            verdict = "PENDING_MORE_UNITS"
        else:
            verdict = "UNDETERMINED" if n == 0 else "FAILED"
        out["predictions"][pid] = {"per_seed": {str(s): per_seed[s] for s in per_seed},
                                   "n_true": ok, "n_determined": n, "verdict": verdict,
                                   "rule": rule}
        if detail:
            out["predictions"][pid]["detail"] = detail

    # D1a / D1b / D1s -- SAME
    rec("D1a", {s: lt("SAME", "CONTINUED", "RESET", s) for s in seeds},
        "SAME: B_morph(CONTINUED) < B_morph(RESET) on >= 2/3 seeds")
    rec("D1b", {s: lt("SAME", "CONTINUED", "TWIN", s) for s in seeds},
        "SAME residual: B_morph(CONTINUED) < B_morph(TWIN) on >= 2/3 seeds [LOAD-BEARING]")
    rec("D1s", {s: (None if lt("SAME", "TWIN", "RESET", s) is None else not lt("SAME", "TWIN", "RESET", s))
                for s in seeds},
        "SAME strong form (reported, predicted to FAIL): TWIN does NOT beat RESET on >= 2/3 seeds")

    # D2a is a conjunction of two majority predicates, not a majority of conjunctions.
    earlier, memory = {}, {}
    for seed in seeds:
        earlier[seed] = lt("CROSS", "CONTINUED", "RESET", seed)
        row = R[("CROSS", "CONTINUED", seed)]
        memory[seed] = None if not row or row["class"] is None else row["class"] in MEMORY_CLASSES
    components = {}
    for name, per in (("earlier", earlier), ("memory", memory)):
        rec("D2a", per, "CROSS: " + name + " on >= 2/3 seeds")
        components[name] = out["predictions"].pop("D2a")
    verdicts = [row["verdict"] for row in components.values()]
    verdict = ("NOT_SCORED__PARTIAL_SEED_SET" if validation_only else
               ("FAILED" if "FAILED" in verdicts else
                ("HELD" if all(v == "HELD" for v in verdicts) else "PENDING_MORE_UNITS")))
    out["predictions"]["D2a"] = {
        "components": components, "verdict": verdict,
        "rule": "CROSS: earlier on >=2/3 seeds AND memory class on >=2/3 seeds; seeds need not coincide"}

    # D2b -- committed sign, determined seeds only
    d2b = {}
    for s in seeds:
        c, r = R[("CROSS", "CONTINUED", s)], R[("CROSS", "RESET", s)]
        if not c or not r or not c["dense_found"] or not r["dense_found"] or c["B_dense"] is None or r["B_dense"] is None:
            d2b[s] = None
        else:
            d2b[s] = c["B_dense"] > r["B_dense"]
    ok, n, _ = _tally(d2b)
    out["predictions"]["D2b"] = {
        "per_seed": {str(s): d2b[s] for s in seeds}, "n_true": ok, "n_determined": n,
        "verdict": "NOT_SCORED__PARTIAL_SEED_SET" if validation_only else
                   ("FAILED" if (n and ok < n) else
                    ("PENDING_MORE_UNITS" if any(R[("CROSS", a, s)] is None for a in ("CONTINUED", "RESET") for s in seeds)
                     else ("UNDETERMINED__NO_DETERMINED_SEED" if n == 0 else "HELD"))),
        "rule": "CROSS: B_dense(CONTINUED) > B_dense(RESET) on EVERY determined seed; undetermined seeds excluded"}

    # D2c -- continuous form, always determined
    d2c = {}
    for s in seeds:
        c, r = R[("CROSS", "CONTINUED", s)], R[("CROSS", "RESET", s)]
        d2c[s] = None if not c or not r or c["final_best_dense"] is None or r["final_best_dense"] is None \
            else c["final_best_dense"] <= r["final_best_dense"]
    rec("D2c", d2c, "CROSS: CONTINUED final best DENSE-cell capability <= RESET's on >= 2/3 seeds",
        {"continued": {str(s): (R[("CROSS", "CONTINUED", s)] or {}).get("final_best_dense") for s in seeds},
         "reset": {str(s): (R[("CROSS", "RESET", s)] or {}).get("final_best_dense") for s in seeds}})

    # D2d accepts registered completed-run censoring, not missing units or metadata.
    baseline = [R[("CROSS", "RESET", seed)] for seed in seeds]
    baseline_pending = any(not row or row["dense_found"] is None
                           or (row["dense_found"] and row["B_dense"] is None) for row in baseline)
    sp_dense = spread([(row or {}).get("B_dense") for row in baseline])
    d2d, condition, registered_undetermined = {}, {}, []
    for seed in seeds:
        c, r = R[("DISJ", "CONTINUED", seed)], R[("CROSS", "RESET", seed)]
        unknown = (baseline_pending or not c or not r or c["dense_found"] is None
                   or (c["dense_found"] and c["B_dense"] is None))
        if unknown:
            d2d[seed] = condition[seed] = None
        elif not c["dense_found"] or not r["dense_found"] or sp_dense is None:
            d2d[seed], condition[seed] = None, True
            registered_undetermined.append(seed)
        else:
            d2d[seed] = condition[seed] = abs(c["B_dense"] - r["B_dense"]) <= sp_dense
    ok, n, _ = _tally(d2d)
    accepted, _, _ = _tally(condition)
    failures = sum(value is False for value in condition.values())
    verdict = ("NOT_SCORED__PARTIAL_SEED_SET" if validation_only else
               ("HELD" if ok >= 2 else
                ("HELD_VACUOUSLY__NO_DETERMINED_SEED" if accepted >= 2 and n == 0 else
                 ("HELD_WITH_REGISTERED_UNDETERMINED_CASES" if accepted >= 2 else
                  ("FAILED" if failures >= 2 else "PENDING_MORE_UNITS")))))
    out["predictions"]["D2d"] = {
        "per_seed": {str(seed): d2d[seed] for seed in seeds},
        "registered_condition_per_seed": {str(seed): condition[seed] for seed in seeds},
        "registered_undetermined_seeds": registered_undetermined,
        "n_true": ok, "n_determined": n, "n_registered_condition_true": accepted,
        "verdict": verdict, "reset_B_dense_spread": sp_dense,
        "rule": "DISJ-CONTINUED B_dense within RESET seed spread, or registered completed-run "
                "UNDETERMINED, on >=2/3 seeds; missing evidence remains pending"}

    # D3a / D3b -- DISJ
    sp_morph = spread([(R[("CROSS", "RESET", s)] or {}).get("B_morph") for s in seeds])
    d3a = {}
    for s in seeds:
        c, t = R[("DISJ", "CONTINUED", s)], R[("DISJ", "TWIN", s)]
        if not c or not t or c["B_morph"] is None or t["B_morph"] is None or sp_morph is None:
            d3a[s] = None
        else:
            d3a[s] = abs(c["B_morph"] - t["B_morph"]) <= sp_morph
    rec("D3a", d3a, "DISJ: |B_morph(CONTINUED) - B_morph(TWIN)| <= RESET seed spread on >= 2/3 seeds",
        {"reset_B_morph_spread": sp_morph})
    rec("D3b", {s: lt("DISJ", "CONTINUED", "RESET", s) for s in seeds},
        "DISJ: B_morph(CONTINUED) < B_morph(RESET) on >= 2/3 seeds (parent's prediction)")

    # D4 -- quality preserved, every pair
    d4pairs = {}
    for p in ("SAME", "CROSS", "DISJ"):
        per = {}
        for s in seeds:
            c, r = R[(p, "CONTINUED", s)], R[(p, "RESET", s)]
            per[s] = None if not c or not r or c["final_best"] is None or r["final_best"] is None \
                else c["final_best"] >= r["final_best"]
        ok, n, _ = _tally(per)
        nf = sum(1 for v in per.values() if v is False)
        if validation_only:
            pv = "NOT_SCORED__PARTIAL_SEED_SET"
        elif ok >= 2:
            pv = "HELD"
        elif len(seeds) - nf < 2:
            pv = "FAILED"
        elif n < len(seeds):
            pv = "PENDING_MORE_UNITS"
        else:
            pv = "UNDETERMINED" if n == 0 else "FAILED"
        d4pairs[p] = {"per_seed": {str(s): per[s] for s in seeds}, "n_true": ok, "n_determined": n,
                      "verdict": pv}
    vs = [v["verdict"] for v in d4pairs.values()]
    # every pair must be HELD; anything else (FAILED, UNDETERMINED, NOT_SCORED) must not roll up to HELD
    if validation_only:
        d4v = "NOT_SCORED__PARTIAL_SEED_SET"
    elif "FAILED" in vs:
        d4v = "FAILED"
    elif "PENDING_MORE_UNITS" in vs:
        d4v = "PENDING_MORE_UNITS"
    elif all(v == "HELD" for v in vs):
        d4v = "HELD"
    else:
        d4v = "UNDETERMINED"
    out["predictions"]["D4"] = {"per_pair": d4pairs, "verdict": d4v,
                                "rule": "CONTINUED final best >= RESET's on >= 2/3 seeds on EVERY pair"}

    # D5 -- SAME: occupant class and lineage root is a seed elite
    d5 = {}
    for s in seeds:
        c = R[("SAME", "CONTINUED", s)]
        if not c or c["class"] is None or c["origin"] is None:
            d5[s] = None
        else:
            root_is_seed = isinstance(c["origin"], (list, tuple)) and len(c["origin"]) >= 1 and c["origin"][0] == "seed"
            d5[s] = (c["class"] in SMOOTH1_OCCUPANTS) and root_is_seed
    rec("D5", d5, "SAME: CONTINUED first admissible class in {KVSTORE,PROGRAM,TABLE} and lineage root is a seed elite, on >= 2/3 seeds",
        {"class_origin": {str(s): [(R[("SAME", "CONTINUED", s)] or {}).get("class"),
                                   (R[("SAME", "CONTINUED", s)] or {}).get("origin")] for s in seeds}})

    # Proven equality permits deduplication; missing provenance never establishes identity.
    groups, path_groups, unknown_paths = {}, {}, set()
    for (pair, arm, seed), row in R.items():
        if not row:
            continue
        label, receipt_path = f"{pair}|{arm}|S{seed}", path(pair, arm, seed, host)
        path_groups.setdefault(receipt_path, []).append(label)
        identity = experiment_identity(row, arm, seed)
        if identity is None:
            unknown_paths.add(receipt_path)
        else:
            groups.setdefault(identity, []).append(label)
    by_design, undisclosed = {}, {}
    for identity, labels in groups.items():
        if len(labels) < 2:
            continue
        keys = [tuple(label.replace("|S", "|").split("|")) for label in labels]
        paths = {path(pair, arm, int(seed), host) for pair, arm, seed in keys}
        record = {"target": identity[0], "arm": identity[1], "seed": identity[2],
                  "seed_population_sha256": identity[3], "n_distinct_receipt_files": len(paths),
                  "identical_B_morph": len({R[(pair, arm, int(seed))]["B_morph"]
                                           for pair, arm, seed in keys}) == 1}
        (by_design if len(paths) == 1 else undisclosed)[" & ".join(sorted(labels))] = record
    for receipt_path, labels in path_groups.items():
        if len(labels) > 1:
            by_design.setdefault(" & ".join(sorted(labels)),
                                 {"n_distinct_receipt_files": 1, "proven_by_shared_path": True})
    after_dedup = len(path_groups) - sum(v["n_distinct_receipt_files"] - 1 for v in undisclosed.values())
    out["duplicate_experiments"] = {
        "shared_baseline_by_design": by_design, "duplicate_computation": undisclosed,
        "n_undisclosed_groups": len(undisclosed), "n_receipt_files": len(path_groups),
        "n_experiments_after_proven_deduplication": after_dedup,
        "n_distinct_experiments": None if unknown_paths else after_dedup,
        "identity_unknown_receipt_files": sorted(unknown_paths),
        "note": ("Equal registered target, arm, seed and known seeded population identify a computation "
                 "within the frozen campaign. Shared file paths identify documented aliases. Unknown "
                 "provenance is not deduplicated and does not certify statistical independence.")}

    # ---- RV-377-180-Z: separate registration on coefficient-carrier reachability.
    # Scored apart from D1a..D5; a Z outcome cannot change any D verdict or the D terminal.
    def dense_hits(pair, arm):
        per = {}
        for s in seeds:
            r = R[(pair, arm, s)]
            per[s] = None if not r else r["dense_found"]
        return per

    Z = {}
    z1, z2, z3 = dense_hits("SAME", "CONTINUED"), dense_hits("SAME", "RESET"), dense_hits("SAME", "TWIN")

    def zrec(zid, per, ok_fn, rule):
        n = sum(1 for v in per.values() if v is not None)
        hits = sum(1 for v in per.values() if v)
        unknown = len(seeds) - n
        # settled early iff the verdict is the same for every way the missing seeds could land
        outcomes = {ok_fn(hits + extra) for extra in range(unknown + 1)}
        verdict = ("NOT_SCORED__PARTIAL_SEED_SET" if validation_only else
                   ("HELD" if outcomes == {True} else
                    ("FAILED" if outcomes == {False} else "PENDING_MORE_UNITS")))
        Z[zid] = {"per_seed": {str(s): per[s] for s in per}, "n_hits": hits,
                  "n_determined": n, "verdict": verdict, "rule": rule}

    # Z5's universal campaign claim is broader than the first-recovery fields supplied.
    recovery_groups = {}
    missing_warm = any(R[(pair, arm, seed)] is None or R[(pair, arm, seed)]["dense_found"] is None
                       for pair in ("SAME", "CROSS", "DISJ")
                       for arm in ("CONTINUED", "TWIN") for seed in seeds)
    for (pair, arm, seed), row in sorted(R.items()):
        if arm == "RESET" or not row or not row["dense_found"]:
            continue
        identity = experiment_identity(row, arm, seed)
        key = ("known", identity) if identity is not None else ("receipt", path(pair, arm, seed, host))
        recovery_groups.setdefault(key, []).append((f"{pair}|{arm}|S{seed}", row))
    z5rows, unknown_roots, dense_roots, nonseed_roots, conflicts = {}, [], [], [], []
    for entries in recovery_groups.values():
        labels = " & ".join(label for label, _ in entries)
        evidence = {(row["dense_root_kind"], row["dense_root_carrier"]) for _, row in entries}
        determinate = {(kind, carrier) for kind, carrier in evidence
                       if kind == "init" or (kind == "seed" and carrier in RAW_CARRIERS)}
        if len(determinate) > 1:
            conflicts.append(labels)
        if any(kind == "seed" and carrier == "DENSE" for kind, carrier in evidence):
            dense_roots.append(labels)
        if any(kind == "init" for kind, _ in evidence):
            nonseed_roots.append(labels)
        known = len(evidence) == 1 and all(kind == "seed" and carrier in RAW_CARRIERS
                                          for kind, carrier in evidence)
        z5rows[labels] = next(iter(evidence))[1] if known else None
        if not known:
            unknown_roots.append(labels)
    first_verdict = ("NOT_SCORED__PARTIAL_SEED_SET" if validation_only else
                     ("UNDETERMINED__CONFLICTING_PROVENANCE" if conflicts else
                      ("FAILED" if dense_roots or nonseed_roots else
                       ("PENDING_MORE_UNITS" if missing_warm else
                        ("UNDETERMINED__UNKNOWN_FOUNDERS" if unknown_roots else
                         ("HELD" if recovery_groups else "UNDETERMINED__NO_RECOVERY"))))))
    universal = ("UNDETERMINED__FIRST_RECOVERY_ONLY" if first_verdict == "HELD" else first_verdict)
    Z["Z5"] = {
        "roots_by_arm": z5rows, "n_distinct_recoveries": len(recovery_groups),
        "n_rooted_in_DENSE": len(dense_roots), "n_nonseed_roots": len(nonseed_roots),
        "unknown_founders": unknown_roots, "conflicting_provenance": conflicts,
        "recorded_first_recovery_verdict": first_verdict, "verdict": universal,
        "evidence_scope": "first admissible atrophied-DENSE recovery per warm arm; RESET excluded",
        "rule": "every recovered atrophied-DENSE machine descends from a non-DENSE seed elite; "
                "first-only receipts cannot certify all later recoveries"}

    zrec("Z1", z1, lambda h: h >= 2, "SAME/CONTINUED reaches atrophied-DENSE on >= 2/3 seeds")
    zrec("Z2", z2, lambda h: h == 0, "SAME/RESET reaches it on 0/3 seeds (within-lane control for the 0-of-43 invariant)")
    zrec("Z3", z3, lambda h: h <= 1, "SAME/TWIN reaches it on <= 1/3 seeds (residual over 'any warm start helps')")
    Z["Z4_reported_only"] = {"note": "CROSS target E_sym5 lists DENSE as a registered occupant; a DENSE "
                                     "recovery there is expected under any arm and is reported, not scored",
                             "cross": {a: {str(s): v for s, v in dense_hits("CROSS", a).items()}
                                       for a in ("RESET", "CONTINUED", "TWIN")}}
    if validation_only:
        Z["terminal"] = "NOT_SCORED__PARTIAL_SEED_SET"
    elif not out["complete"] or any(Z[k]["verdict"] in ("UNDETERMINED", "PENDING_MORE_UNITS")
                                      for k in ("Z1", "Z2", "Z3")):
        Z["terminal"] = "Z_UNDETERMINED__UNITS_MISSING"
    elif Z["Z2"]["verdict"] == "FAILED":
        # F-Z2: the cell is reachable cold, so this is about speed, not reachability
        Z["terminal"] = "COEFFICIENT_CELL_REACHABLE_COLD__NO_CLAIM_ON_THE_INVARIANT"
    elif Z["Z1"]["verdict"] == "HELD" and Z["Z3"]["verdict"] == "FAILED":
        # F-Z3: any developed archive suffices -> the warm-start parents own it
        Z["terminal"] = "COEFFICIENT_LIFT_PARENT_SUFFICIENT_OOPS"
    elif Z["Z1"]["verdict"] == "HELD" and Z["Z3"]["verdict"] == "HELD":
        Z["terminal"] = "COEFFICIENT_CELL_REACHABLE_ONLY_FROM_STRUCTURED_HISTORY_AT_REGISTERED_SCOPE"
    else:
        Z["terminal"] = "COEFFICIENT_LIFT_NOT_OBSERVED"
    Z["adjudication_complete"] = out["complete"] and not validation_only
    out["Z_registration"] = Z

    # terminal
    P = out["predictions"]
    if not out["complete"]:
        out["terminal"] = "ADJUDICATION_INCOMPLETE__UNITS_MISSING"
    elif P["D1a"]["verdict"] == "FAILED":
        out["terminal"] = "DEVELOPMENTAL_MORPHOGENESIS_NOT_OBSERVED_AT_SCOPE"
    elif P["D1a"]["verdict"] == "HELD" and P["D1b"]["verdict"] == "HELD":
        out["terminal"] = "DEVELOPMENTAL_MORPHOGENESIS_OBSERVED_AT_REGISTERED_SCOPE"
    elif P["D1a"]["verdict"] == "HELD" and P["D1b"]["verdict"] == "FAILED":
        out["terminal"] = "PARENT_SUFFICIENT_OOPS"
    else:
        out["terminal"] = "ADJUDICATION_UNDETERMINED__LOAD_BEARING_EVIDENCE"
    out["frozen_all_three_seed_kill_condition"] = (
        not validation_only and P["D1a"]["verdict"] == "FAILED"
        and P["D1a"]["n_true"] == 0 and P["D1a"]["n_determined"] == 3)
    out["residual_over_parents"] = {
        "D1b_load_bearing": P["D1b"]["verdict"],
        "D2b_class_conditioned_sign": P["D2b"]["verdict"],
        "D2d_class_conditioned_control": P["D2d"]["verdict"],
    }
    if validation_only:
        out["terminal"] = "VALIDATION_ONLY__NOT_AN_ADJUDICATION"
        out["note"] = ("scored on %d of 3 seeds; every '>= 2/3' verdict below is therefore "
                       "not the frozen verdict, only an instrument check" % len(seeds))
    p = os.path.join(RES, ("STAGE_B6_DEV_ADJ_VALIDATION_V2_%s.json" % host) if validation_only
                     else ("STAGE_B6_DEV_ADJUDICATION_V2_%s.json" % host))
    json.dump(out, open(p, "w"), indent=1, sort_keys=True, default=str)
    for k in sorted(Z):
        if isinstance(Z[k], dict) and "verdict" in Z[k]:
            print(f"{k:5s} {Z[k]['verdict']:38s} {Z[k].get('per_seed', Z[k].get('roots_by_arm'))}")
    print("Z terminal:", Z["terminal"])
    for k in sorted(P):
        v = P[k]
        print(f"{k:5s} {v['verdict']:38s} {v.get('per_seed', v.get('per_pair', v.get('components')))}")
    DE = out["duplicate_experiments"]
    if DE["n_undisclosed_groups"]:
        print("DUPLICATE COMPUTATION:", DE["n_undisclosed_groups"], "group(s);",
              DE["n_receipt_files"], "receipt files ->", DE["n_experiments_after_proven_deduplication"], "after proven deduplication")
        for g in sorted(DE["duplicate_computation"]):
            print("   ", g)
    if DE["shared_baseline_by_design"]:
        print("shared baseline (by design):", ", ".join(sorted(DE["shared_baseline_by_design"])))
    print("terminal:", out["terminal"], "| missing:", len(missing))
    print("receipt", p)
    return out


if __name__ == "__main__":
    _seeds = tuple(int(x) for x in sys.argv[2].split(",")) if len(sys.argv) > 2 else (0, 1, 2)
    adjudicate(sys.argv[1] if len(sys.argv) > 1 else "billy", _seeds,
               validation_only=(len(sys.argv) > 3 and sys.argv[3] == "validate"))
