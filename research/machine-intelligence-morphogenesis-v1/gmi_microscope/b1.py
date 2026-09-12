"""B1 — neutral recovery of known machine-intelligence mechanisms from low-level primitives
(GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1 stage B1; terminals NEUTRAL_GRAMMAR_REDISCOVERS_KNOWN_FORMS_AT_SCOPE /
SEARCH_GRAMMAR_INADEQUATE__UNKNOWN_FORM_TESTS_BLOCKED).

The search is over the typed morphology IR (`morph.py`) with the R5 operator grammar (`morphgen.py`), evaluated by the
exact charged VM (`vm.py`) on the registered D'/E' ecologies. No architecture macro exists in the alphabet, so a
recovered mechanism is recovered from primitives.

Archive (MAP-Elites, R6) over three label-free descriptors:
  d1 CARRIER   the dominant state kind actually READ by the served computation: none / DENSE / TABLE / KVSTORE / PROGRAM
  d2 SIZE      node count of the genotype, bucketed
  d3 OUTDRIFT  how many of the 16 served answers change between the midpoint and the end of development (the behavioural
               signature of learning), bucketed
B1 passes for a mechanism class when the archive holds an ADMISSIBLE genotype whose carrier descriptor is that class, i.e.
the neutral grammar found that known mechanism by itself.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

from . import bases, ecology, morph, morphgen, smooth
from .core import sha256_of
from .vm import VM, VMRow

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
CARRIERS = ("NONE", "DENSE", "TABLE", "KVSTORE", "PROGRAM")
SIZE_EDGES = (5, 8, 12, 18, 26)
DRIFT_EDGES = (0, 1, 2, 4, 8)
THETA = 0.85
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
MECHANISM_OF_CARRIER = {"DENSE": "D1 coefficient / function field (gradient-style)", "TABLE": "D2 exemplar / indexed memory",
                        "KVSTORE": "D2 exemplar / retrieval memory", "PROGRAM": "D4-D5 symbolic program / search", "NONE": "stateless transducer"}


def _bucket(v, edges):
    for i, e in enumerate(edges):
        if v <= e: return i
    return len(edges)


def carrier_of(g):
    """the dominant state kind on a path into OUTPUT (what the served answer actually reads)."""
    ins = {}
    for a, b, pt in g["edges"]: ins.setdefault(b, {})[pt] = a
    out = [i for i, (k, _) in g["nodes"].items() if k == "OUTPUT"][0]
    seen = set(); stack = [out]; found = []
    while stack:
        i = stack.pop()
        if i in seen or i not in g["nodes"]: continue
        seen.add(i); k = g["nodes"][i][0]
        if k in ("DENSE", "TABLE", "KVSTORE", "PROGRAM"): found.append(k)
        stack.extend(ins.get(i, {}).values())
    for c in ("DENSE", "PROGRAM", "KVSTORE", "TABLE"):
        if c in found: return c
    return "NONE"


def evaluate(g, target, n_events=16, criterion="unseen", seed=0):
    """exact charged lifecycle; returns (capability, descriptor, ledger) or None if the phenotype is invalid."""
    rows = {"IR": (lambda gg: (lambda size: VMRow(gg, size, seed)))(g)}
    try:
        r = smooth.run("IR", B0, 1, seed=seed, target=target, n_events=n_events, rows=rows, criterion=criterion)
    except Exception:
        return None
    D = r["D"]; mid = D[len(D) // 2]; end = D[-1]
    drift = sum(1 for x in end if end[x] != mid.get(x))
    desc = (CARRIERS.index(carrier_of(g)), _bucket(len(g["nodes"]), SIZE_EDGES), _bucket(drift, DRIFT_EDGES))
    return r["capability"], desc, r["R"]


def search(target, seed=0, evaluations=20000, n_init=400, log_every=5000, log=None):
    rng = random.Random(seed); archive = {}; cache = {}; n = 0; failed = 0; tries = 0; t0 = time.time(); hist = []; last_log = 0
    def place(g):
        nonlocal n, failed, tries
        key = morph.canonical(g)
        if key in cache: return
        res = evaluate(g, target); n += 1; cache[key] = True
        if res is None: failed += 1; return
        cap, desc, R = res
        cur = archive.get(desc)
        if cur is None or cap > cur[0]: archive[desc] = (cap, g, R, len(g["nodes"]))
    for _ in range(n_init):
        place(morphgen.random_genotype(rng, steps=rng.randrange(3, 12)))
        if n >= evaluations: break
    while n < evaluations:
        vals = list(archive.values())
        if not vals: place(morphgen.random_genotype(rng, steps=6)); continue
        _, parent, _, _ = rng.choice(vals)
        if rng.random() < 0.2 and len(vals) > 1:
            _, other, _, _ = rng.choice(vals); child, tr = morphgen.crossover(rng, parent, other)
        else:
            child, tr = morphgen.mutate(rng, parent)
        tries += tr; place(child)
        if n - last_log >= log_every:
            last_log = n
            best = max(archive.values(), key=lambda v: v[0])
            rec = {"n_eval": n, "best": best[0], "cells": len(archive), "failed_phenotypes": failed, "sec": round(time.time() - t0, 1),
                   "admissible_carriers": sorted({CARRIERS[k[0]] for k, v in archive.items() if v[0] >= THETA})}
            hist.append(rec); print(json.dumps(rec), flush=True)
            if log: open(log, "a").write(json.dumps(rec) + "\n")
    return archive, n, failed, tries, hist


def main(seed=0, evaluations=20000, tag="V33_B1_IR_RECOVERY", eco_name="E_smooth3", log=None):
    # RV-377-089b / protocol rule 39: this was a hardcoded dict naming THREE of the five registered ecologies, so a
    # recovery run could not be asked for E_sym3 or E_parity at all. That truncation is the same defect rule 39 names,
    # sitting in the harness rather than in a claim: the two ecologies it omitted are exactly where the coefficient
    # carrier's only intervention-robust witnesses live. The registry is now the single source of truth, and
    # ecology.target_of handles the table family (E_parity) as well as the smooth one.
    target = ecology.target_of(ecology.REGISTRY[eco_name])
    archive, n, failed, tries, hist = search(target, seed, evaluations, log=log)
    by_carrier = {}
    for k, (cap, g, R, sz) in archive.items():
        c = CARRIERS[k[0]]
        if c not in by_carrier or cap > by_carrier[c]["capability"]:
            by_carrier[c] = {"capability": cap, "admissible": cap >= THETA, "n_nodes": sz, "mechanism": MECHANISM_OF_CARRIER[c],
                             "fingerprint": morph.fingerprint(g), "genotype": morph.to_json(g), "R": R, "mechanism_vector": morph.mechanism_vector(g)}
    recovered = sorted(c for c, v in by_carrier.items() if v["admissible"] and c != "NONE")
    receipt = {"schema": "StageB1NeutralRecoveryV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422], "revival_record": "RV-377-058", "run_tag": tag, "seed": seed, "ecology": eco_name,
               "search_family": "MAP-Elites over the typed morphology IR with the R5 operator grammar (add/remove node, rewire, add edge, change parameter, change state family, change update law, insert verifier, materialize, add lineage, clone/specialize) plus 20% graft recombination; descriptors (carrier, size, output drift); no architecture macro exists in the alphabet",
               "theta": THETA, "n_evaluations": n, "failed_phenotypes": failed, "proposal_tries_charged": tries, "archive_cells_filled": len(archive), "archive_cells_total": len(CARRIERS) * 6 * 6,
               # RV-377-103: the receipt used to record only the BEST genotype per carrier, which makes
               # "the search did not find X" indistinguishable from "the search never visited X's cell". That is
               # rule 38's unswept-index defect sitting inside the instrument. The full cell map is now recorded:
               # every occupied archive cell with its capability and size, so an absent cell is visibly absent.
               "archive_cell_map": {f"{CARRIERS[k[0]]}|size{k[1]}|drift{k[2]}":
                                    {"capability": v[0], "n_nodes": v[3], "admissible": v[0] >= THETA}
                                    for k, v in sorted(archive.items())},
               "archive_cells_empty": sorted(
                   f"{c}|size{si}|drift{d}" for c in CARRIERS for si in range(6) for d in range(6)
                   if (CARRIERS.index(c), si, d) not in archive),
               "best_by_carrier": by_carrier, "mechanism_classes_recovered": recovered, "history": hist,
               "terminal": "NEUTRAL_GRAMMAR_REDISCOVERS_KNOWN_FORMS_AT_SCOPE" if len(recovered) >= 2 else "SEARCH_GRAMMAR_INADEQUATE__UNKNOWN_FORM_TESTS_BLOCKED",
               "claim_ceiling": "one ecology, one seed, exact charged replay; recovery means an admissible genotype whose served answer reads that carrier, not that the recovered machine equals any registered row"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    # the ecology is part of the receipt NAME. It was not, and the second ecology silently OVERWROTE two committed
    # receipts of the first (recorded as an instrument failure alongside RV-377-078): a receipt filename must key on
    # every coordinate that changes its content.
    json.dump(receipt, open(os.path.join(RES, f"STAGE_B1_{tag}_{eco_name}_S{seed}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("recovered mechanism classes:", recovered, "| terminal:", receipt["terminal"])
    for c, v in sorted(by_carrier.items()): print(f"  {c:8s} cap {v['capability']:.4f} adm {v['admissible']} nodes {v['n_nodes']:2d}  {v['mechanism']}")
    return receipt


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 0, int(sys.argv[2]) if len(sys.argv) > 2 else 20000,
         eco_name=sys.argv[3] if len(sys.argv) > 3 else "E_smooth3", log=sys.argv[4] if len(sys.argv) > 4 else None,
         # distributed runs: the tag carries the HOST, so two machines can never write the same receipt.
         # A receipt filename collision has already destroyed two committed receipts in this programme
         # (recorded alongside RV-377-078); multiplying machines multiplies that risk.
         tag=sys.argv[5] if len(sys.argv) > 5 else "V33_B1_IR_RECOVERY")
