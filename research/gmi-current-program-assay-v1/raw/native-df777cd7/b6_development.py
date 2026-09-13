"""B6 — cross-paradigm developmental morphogenesis (GMI-T12; issue #377 section 19; RV-377-180).

The question (section 19): does developmental history make finding the next useful morphology cheaper?
    B_morph,g = complete resources until the first VERIFIED useful morphology at generation g
    test  B_morph,g+1 < B_morph,g  on fresh ecology shifts, quality preserved, every failed candidate charged.

Developmental history = the MAP-Elites archive produced by the unchanged B1 search (`b1.search`) on a SOURCE ecology E_a.
Three arms on a fresh TARGET ecology E_b, identical charged budget and seed integers:
    RESET      the committed B1 search, fresh random initial population (the default path of b1.search, byte-identical)
    CONTINUED  initial population = the elites of E_a's archive (the developmental arm)
    TWIN       initial population = the elites of the archive of a randomised table ecology with NO bit-linear structure,
               carrier-matched to the CONTINUED seed set (the matched negative twin: "any warm start" without history)
Measurement per run: charged evaluations to the FIRST placement on E_b whose ATROPHIED genotype (rule 23/32) is
admissible under all six registered interventions (rule 36), separates the best constant by >= 1 fx unit (rule 40) and
passes the fixed-function null (rule 42, extractor validated on a known inert row and a known learner before any
candidate is read). B_morph = B_search (search evaluations up to that placement, failed phenotypes included) +
B_verify (every control replay spent on it and on every earlier theta-crossing candidate that failed the controls).

Nothing in the search, the VM, the ecology protocol, theta or the cost model is changed. The only new degree of freedom
is WHICH genotypes the search starts from.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

from . import atrophy_ir, b1, bases, eco_axis, ecology, morph, smooth, zoo
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
THETA = b1.THETA
FX_UNIT = eco_axis.FX_UNIT
REVIVAL = "RV-377-180"
MEMORY = ("TABLE", "KVSTORE")

# the five registered smooth ecologies are the rule-42 probe targets (E_parity excluded: its target is the identity, DG-13)
PROBES = ("E_smooth1", "E_smooth3", "E_sym3", "E_sym5", "E_wit1")
LEARNS_MIN_DISTINCT = 3   # RV-377-103 C4: served answers differ across at least three probe targets

# ---------------------------------------------------------------------------------------------------- ecologies
RANDOM_TABLE_RANGE = (-24, 24)   # the fx range spanned by the registered smooth targets (|sum c_i| <= 1.5, FX_ONE = 16)


def random_table_spec(seed, name):
    """a table ecology with NO bit-linear structure: 16 values drawn uniformly from the fx range of the smooth targets,
    seeded, so the ecology is a deterministic function of its name. Same protocol, criterion and theta as the registry."""
    rng = random.Random(seed)
    return ecology.spec_table([rng.randint(*RANDOM_TABLE_RANGE) for _ in range(16)], name)


# DISJOINT sources and TWIN sources are random tables; seeds are documented here and nowhere else.
RND_SEED_BASE = 4242    # DISJOINT source E_rnd<s>   seed 4242 + s
TWIN_SEED_BASE = 7001   # TWIN source     E_twin<s>  seed 7001 + s


def spec_of(name):
    if name in ecology.REGISTRY: return ecology.REGISTRY[name]
    if name.startswith("E_rnd"): return random_table_spec(RND_SEED_BASE + int(name[5:]), name)
    if name.startswith("E_twin"): return random_table_spec(TWIN_SEED_BASE + int(name[6:]), name)
    raise KeyError(name)


# pairs: (source E_a, target E_b); "<s>" is the seed. Rule (frozen in GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md):
#   E_b must carry a rule-36+40 occupant at 20 000 evaluations in the committed RV-377-113 scan -> E_smooth3 or E_sym5;
#   SAME  memory-occupied -> memory-occupied: the other memory-occupied registered ecology as source
#   CROSS memory-occupied -> the coefficient-witness-bearing ecology
#   DISJ  a structure-free random table -> the coefficient-witness-bearing ecology (shares CROSS's RESET baseline)
PAIRS = {"SAME": ("E_smooth1", "E_smooth3"), "CROSS": ("E_smooth3", "E_sym5"), "DISJ": ("E_rnd<s>", "E_sym5")}
# occupant class of each registered source, from GMI_RV_377_113_INTERVENTION_SCAN.json (all6 == true carriers)
OCCUPANTS = {"E_smooth1": ("KVSTORE", "PROGRAM", "TABLE"), "E_smooth3": ("KVSTORE", "PROGRAM", "TABLE"),
             "E_sym5": ("DENSE", "KVSTORE", "PROGRAM", "TABLE")}


def source_name(pair, seed):
    return PAIRS[pair][0].replace("<s>", str(seed))


def twin_name(seed):
    return f"E_twin{seed}"


# ---------------------------------------------------------------------------------------------------- stage 1: sources
def src_path(eco, seed, host):
    return os.path.join(RES, f"STAGE_B6_DEV_SRC_{eco}_S{seed}_{host}.json")


def run_source(eco, seed, host, evaluations=20000, log=None):
    """the developmental history: the committed B1 search, default path, on the source ecology; the FULL archive is
    saved with every elite's genotype (the committed B1 receipts keep only the best per carrier, which cannot seed)."""
    spec = spec_of(eco); target = ecology.target_of(spec); t0 = time.time()
    archive, n, failed, tries, hist = b1.search(target, seed, evaluations, log=log)
    cells = {}
    for k, (cap, g, R, sz) in sorted(archive.items()):
        cells[f"{b1.CARRIERS[k[0]]}|size{k[1]}|drift{k[2]}"] = {"capability": cap, "n_nodes": sz, "carrier_raw": b1.CARRIERS[k[0]],
                                                                "genotype": morph.to_json(g), "fingerprint": morph.fingerprint(g)}
    bc, c = eco_axis.best_constant(target, smooth.UNSEEN)
    rec = {"schema": "StageB6DevelopmentSourceV1", "revival_record": REVIVAL, "issue": [377], "ecology": eco, "spec": spec,
           "spec_id": ecology.spec_id(spec), "seed": seed, "host": host, "n_evaluations": n, "failed_phenotypes": failed,
           "proposal_tries_charged": tries, "archive_cells_filled": len(cells), "best_constant": bc, "best_constant_value": c,
           "carrier_histogram": _hist(cells), "history": hist, "cells": cells, "seconds": round(time.time() - t0, 1),
           "search_family": "b1.search default path (seed_population=None), byte-identical to the committed B1 search"}
    rec["receipt_sha256"] = sha256_of({k: v for k, v in rec.items() if k != "receipt_sha256"})
    json.dump(rec, open(src_path(eco, seed, host), "w"), indent=1, sort_keys=True, default=str)
    print(f"source {eco} S{seed}: {len(cells)} cells, best {max(v['capability'] for v in cells.values()):.4f}, {rec['seconds']}s", flush=True)
    return rec


def _hist(cells):
    h = {c: 0 for c in b1.CARRIERS}
    for v in cells.values(): h[v["carrier_raw"]] += 1
    return h


# ---------------------------------------------------------------------------------------------------- seed populations
def elites_by_carrier(src):
    """archive elites grouped by RAW carrier (the archive's own descriptor; rule 23 governs recovery CLAIMS, and no claim
    is made about a seed), each group sorted by descending capability then fingerprint (deterministic)."""
    out = {c: [] for c in b1.CARRIERS}
    for key, v in src["cells"].items(): out[v["carrier_raw"]].append(v)
    for c in out: out[c].sort(key=lambda v: (-v["capability"], v["fingerprint"]))
    return out


def matched_populations(src_a, src_twin):
    """CONTINUED and TWIN seed sets with IDENTICAL carrier histograms and sizes: per carrier c, k_c = min(n_a[c], n_twin[c]),
    the top k_c elites of each archive by capability. Placement order: carrier order of b1.CARRIERS, then capability."""
    ea, et = elites_by_carrier(src_a), elites_by_carrier(src_twin)
    cont, twin, k = [], [], {}
    for c in b1.CARRIERS:
        k[c] = min(len(ea[c]), len(et[c]))
        cont += ea[c][:k[c]]; twin += et[c][:k[c]]
    return cont, twin, k, {"a": {c: len(ea[c]) for c in b1.CARRIERS}, "twin": {c: len(et[c]) for c in b1.CARRIERS}}


# ---------------------------------------------------------------------------------------------------- the controls
def six_caps(g, spec):
    out = {}
    for j in ecology.INTERVENTIONS:
        try: out[j] = ecology.run_genotype(spec, g, B0, j)["capability"]
        except Exception: return None
    return out


def final_answers(g, spec):
    return tuple(ecology.run_genotype(spec, g, B0, "standard")["trace"][-1])


def distinct_answers(g):
    """rule 42 extractor: the number of distinct final served-answer vectors over the five probe targets."""
    seen = set()
    for p in PROBES:
        try: seen.add(final_answers(g, ecology.REGISTRY[p]))
        except Exception: seen.add(("ERR", p))
    return len(seen)


def validate_extractor():
    """rule 42: validated on a known inert row and a known learner BEFORE any candidate is read."""
    inert = distinct_answers(zoo.constant_emitter()); learner = distinct_answers(zoo.gradient_net(3, 1))
    return {"known_inert_constant_emitter_distinct": inert, "known_learner_gradient_net_3_1_distinct": learner,
            "valid": inert == 1 and learner >= LEARNS_MIN_DISTINCT}


def verify_candidate(g, spec, bc):
    """all controls on one genotype; returns (verdict dict, replays charged). Order: rule 36 (6 replays) -> rule 40 (free)
    -> rule 42 (5 replays) -> atrophy under all six with the rule-40 line as floor -> rule 42 re-read on the atrophied graph."""
    charged = 0; v = {"pass": False}
    caps = six_caps(g, spec); charged += len(ecology.INTERVENTIONS)
    if caps is None: v["fail"] = "rule36:replay_error"; return v, charged
    mn = min(caps.values()); v["caps"] = caps; v["min_over_six"] = mn; v["binding"] = min(caps, key=caps.get)
    if mn < THETA: v["fail"] = "rule36"; return v, charged
    margin = (mn - bc) / FX_UNIT; v["margin_fx"] = round(margin, 3)
    if margin < 1.0: v["fail"] = "rule40"; return v, charged
    d = distinct_answers(g); charged += len(PROBES); v["distinct_raw"] = d
    if d < LEARNS_MIN_DISTINCT: v["fail"] = "rule42"; return v, charged
    floor = max(THETA, bc + FX_UNIT)   # deletions accepted only if the machine still clears theta AND the rule-40 line
    small, info = atrophy_ir.prune_all_interventions(g, spec, B0, theta=floor)
    charged += info.get("evaluations_charged", len(ecology.INTERVENTIONS))
    v["atrophy"] = {k: val for k, val in info.items() if k not in ("capabilities",)}
    v["atrophied_min_over_six"] = info.get("min_capability"); v["atrophied_margin_fx"] = round((info.get("min_capability", 0) - bc) / FX_UNIT, 3)
    v["carrier_raw"] = b1.carrier_of(g); v["carrier_atrophied"] = b1.carrier_of(small)
    v["n_nodes_raw"] = len(g["nodes"]); v["n_nodes_atrophied"] = len(small["nodes"])
    v["atrophied_genotype"] = morph.to_json(small); v["atrophied_fingerprint"] = morph.fingerprint(small)
    d2 = distinct_answers(small); charged += len(PROBES); v["distinct_atrophied"] = d2
    if d2 < LEARNS_MIN_DISTINCT: v["fail"] = "rule42_atrophied"; return v, charged
    v["pass"] = True
    return v, charged


def first_admissible(trace, spec, bc, max_candidates=None):
    """scan the theta-crossing placements in evaluation order; stop at the first that passes every control."""
    verify_total = 0; failed = {"rule36": 0, "rule40": 0, "rule42": 0, "rule42_atrophied": 0, "rule36:replay_error": 0}; scanned = 0
    for i, rec in enumerate(trace):
        if max_candidates is not None and i >= max_candidates: break
        g = morph.from_json(rec["genotype"]); v, ch = verify_candidate(g, spec, bc); verify_total += ch; scanned += 1
        if v["pass"]:
            return {"found": True, "trace_index": i, "n_eval_search": rec["n_eval"], "n_eval_verify": verify_total,
                    "B_morph": rec["n_eval"] + verify_total, "candidates_scanned": scanned, "candidates_failed_by_rule": failed,
                    "capability_standard": rec["capability"], "origin": rec["origin"], "genotype": rec["genotype"], **v}
        failed[v["fail"]] += 1
    return {"found": False, "n_eval_verify": verify_total, "candidates_scanned": scanned, "candidates_failed_by_rule": failed}


def first_of_class(trace, spec, bc, cls, max_candidates=None):
    """the first placement whose ATROPHIED carrier is in `cls` and which passes every control (for the coefficient-carrier
    delay measurement: cls = ("DENSE",)). Independent scan; charged separately and reported as such."""
    verify_total = 0; scanned = 0
    for i, rec in enumerate(trace):
        if max_candidates is not None and i >= max_candidates: break
        if b1.carrier_of(morph.from_json(rec["genotype"])) not in cls and cls != ("ANY",): continue   # raw pre-filter, free
        g = morph.from_json(rec["genotype"]); v, ch = verify_candidate(g, spec, bc); verify_total += ch; scanned += 1
        if v["pass"] and v["carrier_atrophied"] in cls:
            return {"found": True, "trace_index": i, "n_eval_search": rec["n_eval"], "n_eval_verify": verify_total,
                    "B_morph": rec["n_eval"] + verify_total, "candidates_scanned": scanned, "carrier_atrophied": v["carrier_atrophied"],
                    "capability_standard": rec["capability"], "min_over_six": v["min_over_six"], "origin": rec["origin"]}
    return {"found": False, "n_eval_verify": verify_total, "candidates_scanned": scanned}


# ---------------------------------------------------------------------------------------------------- stage 2: arms
def arm_path(pair, arm, seed, host):
    return os.path.join(RES, f"STAGE_B6_DEV_{pair}_{arm}_S{seed}_{host}.json")


def load_source(eco, seed, host):
    p = src_path(eco, seed, host)
    if not os.path.exists(p): raise FileNotFoundError(p)
    return json.load(open(p))


def run_arm(pair, arm, seed, host, evaluations=20000, log=None, max_candidates=None):
    ea, eb = PAIRS[pair]; ea = ea.replace("<s>", str(seed)); spec = spec_of(eb); target = ecology.target_of(spec)
    bc, cval = eco_axis.best_constant(target, smooth.UNSEEN)
    ext = validate_extractor()
    if not ext["valid"]: raise RuntimeError(f"rule 42 extractor INVALID: {ext}")
    pop = None; seeding = {"arm": arm}
    if arm in ("CONTINUED", "TWIN"):
        src_a = load_source(ea, seed, host); src_t = load_source(twin_name(seed), seed, host)
        cont, twin, k, sizes = matched_populations(src_a, src_t)
        chosen = cont if arm == "CONTINUED" else twin
        pop = [morph.from_json(v["genotype"]) for v in chosen]
        seeding.update({"source_ecology": ea if arm == "CONTINUED" else twin_name(seed), "matched_k_per_carrier": k, "archive_sizes": sizes,
                        "n_seeds": len(pop), "seed_source_capabilities": [v["capability"] for v in chosen],
                        "seed_fingerprints": [v["fingerprint"] for v in chosen], "seed_carriers_raw": [v["carrier_raw"] for v in chosen],
                        "source_receipt_sha256": (src_a if arm == "CONTINUED" else src_t)["receipt_sha256"]})
    elif arm != "RESET":
        raise ValueError(arm)
    trace = []; t0 = time.time()
    archive, n, failed, tries, hist = b1.search(target, seed, evaluations, log=log, seed_population=pop, trace=trace)
    t_search = round(time.time() - t0, 1); t1 = time.time()
    fa = first_admissible(trace, spec, bc, max_candidates)
    fdense = first_of_class(trace, spec, bc, ("DENSE",), max_candidates)
    t_verify = round(time.time() - t1, 1)
    best_by_carrier = {}
    for kk, (cap, g, R, sz) in archive.items():
        c = b1.CARRIERS[kk[0]]
        if c not in best_by_carrier or cap > best_by_carrier[c]["capability"]:
            best_by_carrier[c] = {"capability": cap, "n_nodes": sz, "fingerprint": morph.fingerprint(g), "genotype": morph.to_json(g)}
    # seed-descended fraction of the final archive (lineage bookkeeping; the trace only carries theta-crossers, so this is
    # read from the theta-crossing placements, which is what the measurement is about)
    origins = [r["origin"][0] if r["origin"] else "init" for r in trace]
    rec = {"schema": "StageB6DevelopmentArmV1", "revival_record": REVIVAL, "issue": [377], "pair": pair, "arm": arm, "seed": seed, "host": host,
           "source_ecology": ea, "target_ecology": eb, "target_spec_id": ecology.spec_id(spec), "theta": THETA, "fx_unit": FX_UNIT,
           "best_constant": bc, "best_constant_value": cval, "rule40_line": bc + FX_UNIT, "extractor_validation": ext, "seeding": seeding,
           "n_evaluations": n, "failed_phenotypes": failed, "proposal_tries_charged": tries, "archive_cells_filled": len(archive),
           "n_theta_crossing_placements": len(trace), "theta_crossing_origins": {o: origins.count(o) for o in set(origins)},
           "first_admissible": fa, "first_dense_admissible": fdense,
           "trace_compact": [{"n_eval": r["n_eval"], "capability": r["capability"], "desc": r["desc"], "n_nodes": r["n_nodes"],
                              "origin": r["origin"], "fingerprint": morph.fingerprint(morph.from_json(r["genotype"]))} for r in trace],
           "final_best_capability_standard": max(v["capability"] for v in best_by_carrier.values()) if best_by_carrier else None,
           "final_best_by_carrier": {c: v["capability"] for c, v in best_by_carrier.items()}, "final_best_genotypes": best_by_carrier,
           "history": hist, "seconds_search": t_search, "seconds_verify": t_verify,
           "claim_ceiling": "one target ecology, one seed integer, 20 000 charged evaluations; first-admissible is read on the atrophied "
                            "genotype under all six registered interventions (of which extra_unseen_feedback leaks 50%, DG-13); the "
                            "developmental history's own 20 000 evaluations are generation g's burden and are not charged to g+1"}
    rec["receipt_sha256"] = sha256_of({k: v for k, v in rec.items() if k != "receipt_sha256"})
    json.dump(rec, open(arm_path(pair, arm, seed, host), "w"), indent=1, sort_keys=True, default=str)
    print(f"{pair} {arm} S{seed}: first admissible {fa.get('B_morph')} (search {fa.get('n_eval_search')} + verify {fa.get('n_eval_verify')}) "
          f"class {fa.get('carrier_atrophied')} | first DENSE {fdense.get('B_morph')} | final best {rec['final_best_capability_standard']} | "
          f"{t_search}s + {t_verify}s", flush=True)
    return rec


# ---------------------------------------------------------------------------------------------------- summary
def summary(host, seeds=(0, 1, 2)):
    rows = {}
    for pair in PAIRS:
        for arm in ("RESET", "CONTINUED", "TWIN"):
            for s in seeds:
                p = arm_path(pair, arm, s, host)
                if pair == "DISJ" and arm == "RESET": p = arm_path("CROSS", "RESET", s, host)   # shared baseline, same E_b and seed
                if os.path.exists(p):
                    r = json.load(open(p)); fa = r["first_admissible"]; fd = r["first_dense_admissible"]
                    rows[f"{pair}|{arm}|S{s}"] = {"B_morph": fa.get("B_morph"), "B_search": fa.get("n_eval_search"), "B_verify": fa.get("n_eval_verify"),
                                                  "found": fa["found"], "class": fa.get("carrier_atrophied"), "B_dense": fd.get("B_morph"), "dense_found": fd["found"],
                                                  "final_best": r["final_best_capability_standard"], "final_best_dense": r["final_best_by_carrier"].get("DENSE"),
                                                  "origin": fa.get("origin"), "n_seeds": r["seeding"].get("n_seeds")}
    out = {"schema": "StageB6DevelopmentSummaryV1", "revival_record": REVIVAL, "host": host, "rows": rows}
    json.dump(out, open(os.path.join(RES, f"STAGE_B6_DEV_SUMMARY_{host}.json"), "w"), indent=1, sort_keys=True)
    for k, v in sorted(rows.items()): print(k, json.dumps(v))
    return out


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "source": run_source(sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else 20000)
    elif cmd == "arm": run_arm(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], int(sys.argv[6]) if len(sys.argv) > 6 else 20000)
    elif cmd == "summary": summary(sys.argv[2])
    elif cmd == "validate": print(json.dumps(validate_extractor()))
    else: raise SystemExit(f"unknown command {cmd}")
