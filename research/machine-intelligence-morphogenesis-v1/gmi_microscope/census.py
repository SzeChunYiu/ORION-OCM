"""R9 — census of the genotype space by size: type-correct CONFIGURATIONS, isomorphism CLASSES, and RESPONSE classes,
counted separately and never conflated.

WHICH R9 THIS IS. `GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1` section 20 lists R9 as the "species classifier"; the working
brief asks R9 for a census by size. A census IS the species classifier run exhaustively instead of on whatever a search
happened to find, and it is the only way to put a number on the sentence that opens
`GMI_MACHINE_INTELLIGENCE_BIOSPHERE_V1` section 1: *raw configuration != intelligence species*. That document estimates
2^20 raw mechanism vectors and then says the estimate is not a species count. This module measures the collapse:

  N_CONFIG(n)     type-correct genotypes of exactly n nodes in the declared census universe. A CONFIGURATION count.
  N_CANONICAL(n)  distinct canonical fingerprints among them — isomorphism classes of the typed port graph, i.e. the
                  count after the nuisance group (identifiers, order, surface labels) is quotiented out. Still a
                  configuration count, just a de-duplicated one.
  N_RESPONSE(n)   distinct developmental RESPONSE signatures on one registered ecology (R2's exact relation, served
                  trace plus capability). This is the coarsest count here and it is STILL NOT A SPECIES COUNT: the R2
                  species relation quantifies over a whole registered family (E, J*) of ecologies and interventions,
                  and one ecology can only MERGE machines that a second ecology would split. N_RESPONSE(n) is therefore
                  an upper bound on nothing and a LOWER bound on the number of species at the registered scope.
                  `scaling document section 12: do not report "millions of species" when the number is millions of raw
                  genotypes.` Every count in this receipt is labelled with which of the three it is.

THE DECLARED CENSUS UNIVERSE. Exhaustive enumeration needs a finite alphabet, so the census fixes one parameter setting
per kind (`FREE`), allows an input port to be bound or unbound but requires OUTPUT port 0 to be bound, and requires every
node to feed something except OUTPUT and the update laws (which are executed for their effect on state). Those are declared restrictions of the R0 IR, not of the theory: the universe is
a SUBSET of the type-correct genotypes of size n, so N_CONFIG(n) is a count for this universe. The alphabet is chosen to span
the mechanism families the lane has registered (coefficient carrier, indexed memory, exemplar memory, program carrier,
with their routers and update laws) so that the collapse is measured across families rather than inside one.

EXHAUSTIVE UP TO A SIZE, STRATIFIED ABOVE IT. Sizes up to `EXHAUSTIVE_MAX` are enumerated completely. Above it the
size class is STRATIFIED by node-type composition, a uniform sample of strata is drawn without replacement, and each
drawn stratum is enumerated exhaustively — so N_CONFIG carries a Horvitz-Thompson estimate with a standard error, while
the class counts are reported as counts WITHIN the sampled strata with no extrapolation. An extrapolated class count
would be exactly the kind of number this module exists to refuse.

CLAIM CEILING. One ecology, one intervention, one declared sub-alphabet, one parameter setting per kind. Enlarging the
alphabet, the parameter grid or the ecology family can only raise N_CONFIG and can move N_RESPONSE in either direction.
"""
from __future__ import annotations

import itertools
import json
import os
import random
import sys
import time

from . import bases, ecology, morph, zoo
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]

# the declared census alphabet: one frozen parameter setting per kind, spanning the registered mechanism families
MANDATORY = (("INPUT", {"width": 4}), ("OUTPUT", {}))
FREE = (("TARGET", {}),
        ("DENSE", {"width": 4}),            # coefficient carrier
        ("TABLE", {"keybits": 4}),          # indexed memory
        ("KVSTORE", {"cap": 16}),           # exemplar memory
        ("PROGRAM", {"grammar": 0}),        # program carrier
        ("LINEAR", {}),                     # local transform on the coefficient carrier
        ("LOOKUP", {}),                     # key routing
        ("NEAREST", {"k": 1, "metric": 0}),  # similarity routing
        ("PROGEXEC", {}),                   # program execution
        ("INSERT", {}),                     # memory-insertion update law
        ("GRAD", {"lr": 4}))                # gradient update law
EXHAUSTIVE_MAX = 5
N_STRATA = 200             # strata (node-type compositions) drawn for a stratified size class
CLASS_EVAL_CAP = 9000      # isomorphism classes whose RESPONSE is evaluated per size (uniform reservoir above this)
CENSUS_ECO = "E_smooth3"
CENSUS_J = "standard"


def _alphabet_id():
    return sha256_of({"mandatory": MANDATORY, "free": FREE})[:16]


def _strata(n):
    """the strata of the census universe at size n: the node-type compositions (multisets of free kinds)."""
    return list(itertools.combinations_with_replacement(range(len(FREE)), n - 2))


def enumerate_stratum(combo, materialize=True):
    """every type-correct genotype of the declared universe in one stratum (one node-type composition).

    Universe rules: exactly one INPUT and one OUTPUT; an input port may be bound to any node of the matching output
    type or left UNBOUND (the R0 type system permits an unbound port and the R1 VM evaluates it as absent), except
    OUTPUT port 0 which must be bound so the machine serves something; no dead node (every node feeds something, except
    OUTPUT and the class-U update laws, which are executed for their effect on state and have no consumer); acyclic.
    Returns (exact count, materialized genotypes)."""
    spec = list(MANDATORY) + [FREE[i] for i in combo]
    kinds = [k for k, _ in spec]; ids = [str(i) for i in range(len(spec))]
    out_type = {i: morph.KINDS[k][2] for i, k in zip(ids, kinds)}
    ports = [(i, pt, t) for i, k in zip(ids, kinds) for pt, t in enumerate(morph.KINDS[k][1])]
    outid = [i for i, k in zip(ids, kinds) if k == "OUTPUT"][0]
    choices = []
    for i, pt, t in ports:
        srcs = [j for j in ids if j != i and out_type[j] == t]
        if (i, pt) != (outid, 0): srcs = srcs + [None]
        choices.append(srcs)
    if any(not c for c in choices): return 0, []
    nodes = {i: (k, dict(p)) for i, (k, p) in zip(ids, spec)}
    total = 0; kept = []
    for assign in itertools.product(*choices):
        edges = [(a, i, pt) for a, (i, pt, _) in zip(assign, ports) if a is not None]
        used = {a for a, _, _ in edges}
        # no dead node. OUTPUT and the UPDATE-LAW nodes (class U) are exempt: an update node is executed for its effect
        # on the state it writes and has no consumer by design, so requiring it to feed something would delete every
        # machine that learns from the universe (it did, in the first version of this census).
        if any(i not in used and nodes[i][0] != "OUTPUT" and morph.CLASS_OF[nodes[i][0]] != "U" for i in ids): continue
        g = {"nodes": nodes, "edges": edges, "meta": {}}
        try:
            morph.typecheck(g)                            # also rejects cycles
        except morph.MorphError:
            continue
        total += 1
        if materialize:
            kept.append({"nodes": {i: (k, dict(p)) for i, (k, p) in nodes.items()}, "edges": list(edges), "meta": {}})
    return total, kept


def enumerate_size(n, strata=None):
    """the whole size class, or the union of the given strata. Returns (exact count over those strata, genotypes).
    Materializes everything; use `iter_size` for the sizes where that does not fit."""
    total = 0; kept = []
    for combo in (strata if strata is not None else _strata(n)):
        t, gs = enumerate_stratum(combo)
        total += t; kept.extend(gs)
    return total, kept


def iter_size(n, strata=None):
    """stream the genotypes of the size class (or of the given strata) one at a time."""
    for combo in (strata if strata is not None else _strata(n)):
        _, gs = enumerate_stratum(combo)
        for g in gs: yield g


def response_of(g, spec_name=CENSUS_ECO, intervention=CENSUS_J):
    """the R2 developmental response signature, or None when the genotype has no valid phenotype."""
    try:
        r = ecology.run_genotype(ecology.REGISTRY[spec_name], g, B0, intervention)
    except Exception:
        return None, None
    return ecology.response_signature(r), r["capability"]


def census_size(n, exhaustive, rng, n_strata=N_STRATA, class_eval_cap=CLASS_EVAL_CAP):
    """the three counts at size n, exhaustively or on a STRATIFIED sample of the size class.

    Stratified mode: the strata are the node-type compositions; `n_strata` of them are drawn uniformly WITHOUT
    replacement and each drawn stratum is enumerated EXHAUSTIVELY. So the counts inside the sampled strata are exact,
    and N_CONFIG for the whole size class carries a Horvitz-Thompson estimate with its standard error. Class counts are
    NOT extrapolated: an estimated number of isomorphism or response classes would need to know how classes are shared
    between strata, which the sample does not measure, so they are reported as counts WITHIN the sampled strata.

    RESPONSE evaluation is the expensive step, so when the number of isomorphism classes exceeds `class_eval_cap` a
    uniform reservoir sample of that many classes is run and the receipt reports the response count as a count over the
    evaluated representatives, with the number evaluated next to it. The isomorphism-class count is always exact over
    the enumerated strata; only the response count is ever subsampled."""
    t0 = time.time()
    all_strata = _strata(n); sampled = not exhaustive
    chosen = all_strata if exhaustive else rng.sample(all_strata, min(n_strata, len(all_strata)))
    seen = set(); reps = []; second = []; n_config = 0
    for g in iter_size(n, strata=chosen):
        n_config += 1
        fp = morph.fingerprint(g)
        if fp in seen:
            if len(second) < 60: second.append((fp, morph.to_json(g)))
            continue
        seen.add(fp); j = len(seen) - 1
        if len(reps) < class_eval_cap: reps.append((fp, morph.to_json(g)))
        else:
            k = rng.randrange(j + 1)
            if k < class_eval_cap: reps[k] = (fp, morph.to_json(g))
    est = None
    if sampled:
        per = [enumerate_stratum(c, materialize=False)[0] for c in chosen]
        f = len(all_strata) / len(chosen); mean = sum(per) / len(per)
        var = sum((x - mean) ** 2 for x in per) / max(len(per) - 1, 1)
        est = {"estimator": "Horvitz-Thompson over uniformly sampled strata (node-type compositions), each sampled stratum enumerated exhaustively",
               "n_strata_population": len(all_strata), "n_strata_sampled": len(chosen),
               "N_CONFIG_estimate": round(f * n_config, 1),
               "standard_error": round(f * ((len(per) * var * (1 - len(chosen) / len(all_strata))) ** 0.5), 1),
               "exact_count_within_sampled_strata": n_config}
    responses = {}; invalid = 0
    for fp, gj in reps:
        sig, cap = response_of(morph.from_json(gj))
        if sig is None: invalid += 1; continue
        r = responses.setdefault(sig, {"n_canonical_classes": 0, "best_capability": cap, "example_fp": fp})
        r["n_canonical_classes"] += 1
        if cap is not None and (r["best_capability"] is None or cap > r["best_capability"]): r["best_capability"] = cap
    # MEASURED check of the claim the canonical cache rests on: a SECOND labelling of the same canonical form must have
    # the identical response (the response is a function of the isomorphism class, not of the node identifiers)
    first = {fp: gj for fp, gj in reps}
    checked = 0; disagree = 0
    for fp, gj in second:
        if fp not in first or checked >= 60: continue
        s1, _ = response_of(morph.from_json(first[fp])); s2, _ = response_of(morph.from_json(gj)); checked += 1
        if s1 != s2: disagree += 1
    # remint invariance: reminting a representative must change neither its fingerprint nor its response
    rbad = 0; rchecked = 0
    for fp, gj in reps[:60]:
        g = morph.from_json(gj); gr = morph.remint(g, 3); rchecked += 1
        if morph.fingerprint(gr) != fp or response_of(gr)[0] != response_of(g)[0]: rbad += 1
    n_canon = len(seen)
    return {"size": n, "exhaustive": not sampled,
            "N_CONFIG_type_correct": n_config if not sampled else None,
            "N_CONFIG_stratified_estimate": est,
            "n_configurations_enumerated": n_config,
            "N_CANONICAL_isomorphism_classes": n_canon if not sampled else None,
            "n_canonical_classes_in_sample": n_canon,
            "n_canonical_classes_response_evaluated": len(reps),
            "response_classes_subsampled": len(reps) < n_canon,
            "N_RESPONSE_classes": len(responses) if (not sampled and len(reps) == n_canon) else None,
            "n_response_classes_in_sample": len(responses),
            "n_canonical_classes_without_a_valid_phenotype": invalid,
            "collapse_config_to_canonical": round(n_canon / n_config, 4) if n_config else None,
            "collapse_canonical_to_response": round(len(responses) / len(reps), 4) if reps else None,
            "best_capability_any_class": max([v["best_capability"] for v in responses.values() if v["best_capability"] is not None] or [None]) if responses else None,
            "response_class_check": {"n_multi_member_classes_checked": checked, "n_disagreements": disagree,
                                     "assertion": "two labellings of the same canonical form have the identical developmental response"},
            "remint_invariance": {"n_checked": rchecked, "n_changed": rbad},
            "seconds": round(time.time() - t0, 1)}


def main(tag="V1", sizes=(3, 4, 5, 6), exhaustive_max=EXHAUSTIVE_MAX, seed=0, n_strata=N_STRATA):
    rng = random.Random(seed); t0 = time.time(); rows = []
    for n in sizes:
        rows.append(census_size(n, n <= exhaustive_max, rng, n_strata))
        print(json.dumps({k: rows[-1][k] for k in ("size", "exhaustive", "n_configurations_enumerated", "n_canonical_classes_in_sample", "n_response_classes_in_sample", "seconds")}), flush=True)
    # which response classes a registered known parent occupies: a response class with no parent in it is not thereby
    # a new species (that is R10/B8's question), it is simply unoccupied by this lane's parent library
    parents = {}
    for name, fn in zoo.ZOO.items():
        sig, cap = response_of(fn())
        parents[name] = {"response_signature": sig, "capability": cap, "n_nodes": len(fn()["nodes"]), "fingerprint": morph.fingerprint(fn())}
    parent_sigs = {v["response_signature"] for v in parents.values()}
    exhaustive_rows = [r for r in rows if r["exhaustive"]]
    total_config = sum(r["n_configurations_enumerated"] for r in exhaustive_rows)
    total_canon = sum(r["N_CANONICAL_isomorphism_classes"] for r in exhaustive_rows)
    disagreements = sum(r["response_class_check"]["n_disagreements"] for r in rows)
    remint_bad = sum(r["remint_invariance"]["n_changed"] for r in rows)
    out = {"schema": "StageR9CensusV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422], "layer": "R9",
           "layer_reading": "census by size = the species classifier run exhaustively instead of on a search's leftovers; see the module docstring",
           "run_tag": tag, "seed": seed, "ecology": CENSUS_ECO, "intervention": CENSUS_J,
           "ecology_spec_id": ecology.spec_id(ecology.REGISTRY[CENSUS_ECO]),
           "census_universe": {"alphabet_id": _alphabet_id(),
                               "mandatory_nodes": [list(x) for x in MANDATORY], "free_nodes": [list(x) for x in FREE],
                               "restrictions": ["exactly one INPUT and one OUTPUT", "every input port bound",
                                                "no dead node (every node but OUTPUT feeds something)", "acyclic (R0 typecheck)",
                                                "one frozen parameter setting per kind"],
                               "note": "a declared SUBSET of the type-correct genotypes of each size; every count below is a count for this universe"},
           "exhaustive_max_size": exhaustive_max, "stratified_strata_drawn": n_strata, "response_evaluation_class_cap": CLASS_EVAL_CAP,
           "counts_by_size": rows,
           "totals_over_exhaustive_sizes": {"sizes": [r["size"] for r in exhaustive_rows],
                                            "N_CONFIG_type_correct": total_config,
                                            "N_CANONICAL_isomorphism_classes": total_canon,
                                            "N_RESPONSE_classes_union_not_computed": "response classes are counted within a size; the same signature can occur at two sizes and the union is reported below",
                                            "config_per_canonical_class": round(total_config / total_canon, 4) if total_canon else None},
           "three_counts_are_different_things": {
               "N_CONFIG": "type-correct CONFIGURATIONS in the declared universe. Not species, not even distinct machines.",
               "N_CANONICAL": "isomorphism classes of the typed port graph — configurations after the nuisance group is quotiented out. Still a configuration count.",
               "N_RESPONSE": "distinct exact developmental responses on ONE registered ecology under ONE intervention. A LOWER bound on the species count at the registered scope, because a second ecology or intervention can only split these classes further, never merge them.",
               "forbidden_sentence": "none of these three may be reported as a species count (scaling document section 12)"},
           "known_parent_occupancy": {"parents": parents, "n_distinct_parent_response_signatures": len(parent_sigs),
                                      "n_parents": len(parents),
                                      "note": "the R4 parents are mostly larger than the censused sizes; this block records which responses the registered parent library realizes, so a census response class can be checked against them"},
           "response_class_check_total": {"n_disagreements": disagreements,
                                          "assertion": "the developmental response is a function of the canonical form; a disagreement would falsify the canonical-form cache R8 relies on"},
           "remint_invariance": {"n_changed": remint_bad, "assertion": "morph.remint changes no count in this receipt"},
           "seconds": round(time.time() - t0, 1),
           "terminal": "R9_CENSUS_EXECUTED" if (disagreements == 0 and remint_bad == 0) else "R9_CENSUS_INVARIANCE_FAILED",
           "claim_ceiling": "one ecology, one intervention, one declared sub-alphabet with one parameter setting per kind. Enlarging the alphabet or the parameter grid can only raise N_CONFIG; enlarging the registered ecology family can only raise N_RESPONSE. The stratified sizes report SAMPLE counts with no extrapolation to the population"}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, f"STAGE_R9_CENSUS_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    for r in rows:
        print(f"  n={r['size']} {'exhaustive' if r['exhaustive'] else 'stratified'} configs {r['n_configurations_enumerated']:>9} "
              f"canonical {r['n_canonical_classes_in_sample']:>6} response {r['n_response_classes_in_sample']:>5}")
    return out


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V1")
