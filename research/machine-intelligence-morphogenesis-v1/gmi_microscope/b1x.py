"""RV-377-087 — B1 with a MECHANISM descriptor: give the partial assembly of a learning rule its own niche.

The standing negative: over the typed IR the coefficient carrier D1 is recovered 0 of 3 on E_smooth1, the ecology where
an admissible witness exists, and 0 of 6 on the two ecologies where none does (RV-377-058, RV-377-081, RV-377-083).

The diagnosis is on record in RV-377-083: over this alphabet the coefficient carrier is a COORDINATED MULTI-NODE
assembly - the registered witness is DENSE, AFFINE, NONLIN, DENSE, LINEAR and TWO GRAD nodes - and the archive gives no
partial credit for building part of it. A genotype halfway to a two-block gradient learner lands in the same cell as a
fully formed memory machine and loses.

This is the SAME SHAPE as the negative that RV-377-057 revived over the expression-tree grammar, where program size was a
parsimony TIE-BREAK that killed partial assemblies and the fix was making size a NICHE COORDINATE. Here the update
structure is invisible to the archive and the fix is the same: make it a coordinate.

THE ONLY CHANGE from b1.py is one added descriptor. Same operator grammar, same charged VM, same ecologies, same theta,
same budget, same seeds. So a difference in outcome is attributable to the descriptor alone.

  d4 UPDATE  the number of UPDATE-class nodes reachable from TARGET, i.e. how much of a learning rule the genotype has
             assembled, bucketed at 0 / 1 / 2 / 3+. Label-free: it reads the typed graph, not any name.

DISCLOSED CALIBRATION (before freezing): on the registered rows this descriptor is 2 for every gradient row and 1 for
every memory, program, store and particle row; over the ten committed admissible E_smooth1 elites its distribution is
{0: 1, 1: 8, 2: 1}. So the archive currently has almost no occupant at the coordinate the coefficient carrier needs.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

from . import b1, morph, morphgen, smooth
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
UPDATE_EDGES = (0, 1, 2)          # buckets 0, 1, 2, 3+
THETA = b1.THETA


def target_fed_updates(g):
    """UPDATE-class nodes reachable from TARGET. Label-free: typed graph only."""
    tgt = [i for i, (k, _) in g["nodes"].items() if k == "TARGET"]
    if not tgt: return 0
    outs = {}
    for a, b_, _ in g["edges"]: outs.setdefault(a, set()).add(b_)
    seen = set(); stack = list(tgt); fed = set()
    while stack:
        i = stack.pop()
        if i in seen: continue
        seen.add(i)
        for j in outs.get(i, ()):
            if j in g["nodes"] and morph.CLASS_OF[g["nodes"][j][0]] == "U": fed.add(j)
            stack.append(j)
    return len(fed)


def evaluate(g, target, n_events=16, criterion="unseen", seed=0):
    """b1.evaluate with the UPDATE coordinate appended to the descriptor. Nothing else differs."""
    r = b1.evaluate(g, target, n_events, criterion, seed)
    if r is None: return None
    cap, desc, R = r
    return cap, desc + (b1._bucket(target_fed_updates(g), UPDATE_EDGES),), R


def search(target, seed=0, evaluations=20000, n_init=400, log_every=5000, log=None):
    rng = random.Random(seed); archive = {}; cache = {}; n = 0; failed = 0; tries = 0; t0 = time.time(); hist = []; last = 0

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
        if n - last >= log_every:
            last = n
            best = max(archive.values(), key=lambda v: v[0])
            rec = {"n_eval": n, "best": best[0], "cells": len(archive), "failed_phenotypes": failed,
                   "sec": round(time.time() - t0, 1),
                   "admissible_carriers": sorted({b1.CARRIERS[k[0]] for k, v in archive.items() if v[0] >= THETA}),
                   "admissible_update_buckets": sorted({k[3] for k, v in archive.items() if v[0] >= THETA})}
            hist.append(rec); print(json.dumps(rec), flush=True)
            if log: open(log, "a").write(json.dumps(rec) + "\n")
    return archive, n, failed, tries, hist


def main(seed=0, evaluations=20000, tag="V37_B1X_MECHANISM", eco_name="E_smooth1", log=None):
    # RV-377-089b / protocol rule 39: the registry is the single source of truth, so every registered ecology can be
    # asked for. The hardcoded three-entry dict this replaces omitted E_sym3 and E_parity.
    target = b1.ecology.target_of(b1.ecology.REGISTRY[eco_name])
    archive, n, failed, tries, hist = search(target, seed, evaluations, log=log)
    by = {}
    for k, (cap, g, R, sz) in archive.items():
        c = b1.CARRIERS[k[0]]
        if c not in by or cap > by[c]["capability"]:
            by[c] = {"capability": cap, "admissible": cap >= THETA, "n_nodes": sz,
                     "mechanism": b1.MECHANISM_OF_CARRIER[c], "target_fed_updates": target_fed_updates(g),
                     "fingerprint": morph.fingerprint(g), "genotype": morph.to_json(g), "R": R,
                     "mechanism_vector": morph.mechanism_vector(g)}
    rec_ = sorted(c for c, v in by.items() if v["admissible"] and c != "NONE")
    receipt = {"schema": "StageB1XMechanismDescriptorV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
               "revival_record": "RV-377-087", "run_tag": tag, "seed": seed, "ecology": eco_name, "theta": THETA,
               "the_only_change_from_b1": "one added archive coordinate: the number of UPDATE-class nodes reachable from TARGET, bucketed at 0/1/2/3+. Same operator grammar, same charged VM, same ecology, same theta, same budget, same seeds.",
               "archive_cells_total": len(b1.CARRIERS) * 6 * 6 * 4, "archive_cells_filled": len(archive),
               "n_evaluations": n, "failed_phenotypes": failed, "proposal_tries_charged": tries,
               "best_by_carrier": by, "mechanism_classes_recovered": rec_, "history": hist,
               "terminal": "NEUTRAL_GRAMMAR_REDISCOVERS_KNOWN_FORMS_AT_SCOPE" if len(rec_) >= 2 else "SEARCH_GRAMMAR_INADEQUATE__UNKNOWN_FORM_TESTS_BLOCKED",
               "claim_ceiling": "one ecology, one seed per receipt, exact charged replay under the standard intervention; carriers here are RAW descriptors and must be re-read after atrophy per protocol rule 23 before any recovery claim"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_B1X_{tag}_{eco_name}_S{seed}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("recovered:", rec_, "| cells", len(archive))
    for c, v in sorted(by.items()):
        print(f"  {c:8s} cap {v['capability']:.4f} adm {v['admissible']} nodes {v['n_nodes']:2d} target_fed_updates {v['target_fed_updates']}")
    return receipt


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 0, int(sys.argv[2]) if len(sys.argv) > 2 else 20000,
         eco_name=sys.argv[3] if len(sys.argv) > 3 else "E_smooth1", log=sys.argv[4] if len(sys.argv) > 4 else None)
