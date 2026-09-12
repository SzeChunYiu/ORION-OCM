#!/usr/bin/env python3
"""Signature-space hole census v1 (Track B, issue #377, toward the 'undesigned form' question).

Exploratory E0 theory instrument. It does NOT search, train, or evaluate anything.

It enumerates the finite lattice of label-free morphology signatures S(x) =
(theta_type, update_locality, feedback_dependence, execution_shape, store_discipline)
registered in MORPHOLOGY_SIGNATURES_V2.json, applies the frozen coherence constraints C1-C5,
marks the cells occupied by registered parent morphologies (assignment table below, each with
a rationale), and reports:
  1. coherent cell count, occupied cells, multi-occupant cells (signature-level coincidences);
  2. pairwise-projection holes: value pairs of two observables that no registered parent uses;
  3. 'frontier holes': coherent, unoccupied cells at Hamming distance 1 from an occupied cell
     that close at least two pairwise-projection holes (the cheapest candidate regions for a
     structurally new form that is still adjacent to something known);
  4. the distance-to-nearest-occupant histogram.

Claim ceiling: a hole is a statement about the coordinate system, not about nature. A hole
may be empty because the combination is useless, because the observables are too coarse, or
because nobody built it. Only Stage E (frontier) can say which holes are Pareto-relevant.
Receipt: SIGNATURE_HOLE_CENSUS_V1.json ; narrative: SIGNATURE_HOLE_CENSUS_V1.md
"""
import hashlib
import itertools
import json
import sys
from collections import Counter, defaultdict

THETA = ["DISCRETE_FINITE", "BOUNDED_NUMERIC", "MIXED"]
LOC = ["NONE", "LOCAL_O1", "SPARSE_SUBLINEAR", "DENSE_LINEAR"]
FB_MENU = ["scalar_loss", "exact_counterexample", "query_access", "likelihood_score"]
EXEC = ["ACYCLIC_FIXED_DEPTH", "BOUNDED_LOOP", "STORE_MATCH_CYCLE", "ENUMERATE_TEST_CYCLE", "SAMPLE_SCORE_CYCLE"]
STORE = ["NONE", "INDEXED_EXEMPLARS", "RULE_SET", "TERM_LIBRARY", "TRACE_DISTRIBUTION", "PARAMETER_ARRAY"]
OBS = ["theta_type", "update_locality", "feedback_dependence", "execution_shape", "store_discipline"]


def fb_key(fbs):
    return tuple(sorted(fbs))


def coherent(cell):
    th, lo, fb, ex, st = cell
    if lo == "NONE" and len(fb) > 0:
        return False, "C1"
    if st == "PARAMETER_ARRAY" and th not in ("BOUNDED_NUMERIC", "MIXED"):
        return False, "C2"
    if st == "TRACE_DISTRIBUTION" and th not in ("BOUNDED_NUMERIC", "MIXED"):
        return False, "C3"
    if ex == "ENUMERATE_TEST_CYCLE" and len(fb) == 0:
        return False, "C4"
    if lo == "DENSE_LINEAR" and st not in ("PARAMETER_ARRAY", "NONE"):
        return False, "C5"
    return True, ""


# Registered parent morphologies -> signature cell. Frozen assignment with rationale.
# (name, theta, locality, feedback set, execution, store, rationale, family)
OCCUPANTS = [
    ("M0 finite transducer / DFA / elementary CA", "DISCRETE_FINITE", "NONE", [], "BOUNDED_LOOP", "NONE", "inert automaton; no update law", "M0"),
    ("M1 production system with chunking (Soar-class)", "DISCRETE_FINITE", "LOCAL_O1", ["exact_counterexample"], "STORE_MATCH_CYCLE", "RULE_SET", "match-select-act; one rule added per impasse", "M1"),
    ("TMS / ATMS", "DISCRETE_FINITE", "LOCAL_O1", ["exact_counterexample"], "STORE_MATCH_CYCLE", "RULE_SET", "justification records added per assertion; label propagation", "M1"),
    ("Blackboard (Hearsay-II)", "DISCRETE_FINITE", "LOCAL_O1", ["exact_counterexample"], "STORE_MATCH_CYCLE", "RULE_SET", "knowledge sources fire on blackboard patterns", "M1"),
    ("M2 program synthesis with library (OOPS / CEGIS / DreamCoder-symbolic)", "DISCRETE_FINITE", "SPARSE_SUBLINEAR", ["exact_counterexample", "query_access"], "ENUMERATE_TEST_CYCLE", "TERM_LIBRARY", "enumerate candidates, test against spec/oracle, store solved programs", "M2"),
    ("ILP / Popper (learning from failures)", "DISCRETE_FINITE", "SPARSE_SUBLINEAR", ["exact_counterexample"], "ENUMERATE_TEST_CYCLE", "RULE_SET", "hypothesis space pruned by failures; rules stored", "M2"),
    ("GP / CGP / AutoML-Zero outer search", "DISCRETE_FINITE", "SPARSE_SUBLINEAR", ["scalar_loss"], "ENUMERATE_TEST_CYCLE", "TERM_LIBRARY", "population of programs varied by mutation, selected by scalar fitness", "M2"),
    ("Angluin L* automaton learner", "DISCRETE_FINITE", "SPARSE_SUBLINEAR", ["query_access"], "BOUNDED_LOOP", "INDEXED_EXEMPLARS", "observation table of query answers; hypothesis DFA executed", "M2/M5"),
    ("Decision-tree induction (incremental)", "DISCRETE_FINITE", "SPARSE_SUBLINEAR", ["exact_counterexample"], "ACYCLIC_FIXED_DEPTH", "RULE_SET", "a split changes one subtree", "M1"),
    ("M3 probabilistic program / particle filter / SMC", "MIXED", "SPARSE_SUBLINEAR", ["likelihood_score"], "SAMPLE_SCORE_CYCLE", "TRACE_DISTRIBUTION", "sample traces, score by likelihood, resample", "M3"),
    ("Bayesian program learning (Lake et al.)", "MIXED", "SPARSE_SUBLINEAR", ["likelihood_score"], "SAMPLE_SCORE_CYCLE", "TERM_LIBRARY", "programs as generative models scored by likelihood; library of parts", "M3/M2"),
    ("Markov logic network (weight learning)", "MIXED", "DENSE_LINEAR", ["likelihood_score"], "SAMPLE_SCORE_CYCLE", "PARAMETER_ARRAY", "weights over first-order clauses learned by (pseudo-)likelihood; grounding then sampling", "M3/M1"),
    ("Bayesian network with CPT counting", "BOUNDED_NUMERIC", "SPARSE_SUBLINEAR", ["likelihood_score"], "ACYCLIC_FIXED_DEPTH", "PARAMETER_ARRAY", "counts updated in the CPTs touched by an observation; exact inference bounded", "M3"),
    ("Kalman filter (fixed model)", "BOUNDED_NUMERIC", "DENSE_LINEAR", ["likelihood_score"], "BOUNDED_LOOP", "PARAMETER_ARRAY", "state estimate and covariance updated densely per measurement", "M3"),
    ("Boltzmann machine / EBM (contrastive divergence)", "BOUNDED_NUMERIC", "DENSE_LINEAR", ["likelihood_score"], "SAMPLE_SCORE_CYCLE", "PARAMETER_ARRAY", "all weights moved by a likelihood-gradient estimate from samples", "M3/M4"),
    ("M4 feed-forward net + SGD / MAML / learned optimizers / ES on parameters", "BOUNDED_NUMERIC", "DENSE_LINEAR", ["scalar_loss"], "ACYCLIC_FIXED_DEPTH", "PARAMETER_ARRAY", "every parameter moved per scalar-loss event (gradient or population estimate)", "M4"),
    ("Perceptron (mistake-driven)", "BOUNDED_NUMERIC", "DENSE_LINEAR", ["exact_counterexample"], "ACYCLIC_FIXED_DEPTH", "PARAMETER_ARRAY", "all weights moved on a labelled mistake; no scalar loss needed", "M4"),
    ("RNN / LSTM by BPTT ; NTM / DNC ; neural CA", "BOUNDED_NUMERIC", "DENSE_LINEAR", ["scalar_loss"], "BOUNDED_LOOP", "PARAMETER_ARRAY", "recurrent execution, dense gradient update", "M4"),
    ("Hopfield associative memory", "BOUNDED_NUMERIC", "DENSE_LINEAR", ["exact_counterexample"], "BOUNDED_LOOP", "PARAMETER_ARRAY", "outer-product store touches all weights per pattern", "M4/M5"),
    ("Reservoir computing (fixed reservoir, trained readout)", "BOUNDED_NUMERIC", "SPARSE_SUBLINEAR", ["scalar_loss"], "BOUNDED_LOOP", "PARAMETER_ARRAY", "only the readout is updated", "M4"),
    ("Kohonen SOM / Hebbian self-organization", "BOUNDED_NUMERIC", "SPARSE_SUBLINEAR", [], "ACYCLIC_FIXED_DEPTH", "PARAMETER_ARRAY", "winner and neighbourhood updated; no external feedback", "M4"),
    ("STDP spiking network", "BOUNDED_NUMERIC", "LOCAL_O1", [], "BOUNDED_LOOP", "PARAMETER_ARRAY", "synapse-local timing rule; no external feedback", "M4"),
    ("Naive Bayes / counting classifier", "BOUNDED_NUMERIC", "SPARSE_SUBLINEAR", ["exact_counterexample"], "ACYCLIC_FIXED_DEPTH", "PARAMETER_ARRAY", "counts for the observed features/class updated", "M3/M4"),
    ("SVM (dual, support vectors)", "BOUNDED_NUMERIC", "SPARSE_SUBLINEAR", ["scalar_loss"], "ACYCLIC_FIXED_DEPTH", "INDEXED_EXEMPLARS", "solution stored as weighted exemplars", "M5/M4"),
    ("Tabular Q-learning", "BOUNDED_NUMERIC", "LOCAL_O1", ["scalar_loss"], "STORE_MATCH_CYCLE", "INDEXED_EXEMPLARS", "one table entry updated per reward", "M5"),
    ("GP regression / Bayesian optimization (nonparametric)", "BOUNDED_NUMERIC", "LOCAL_O1", ["scalar_loss"], "ACYCLIC_FIXED_DEPTH", "INDEXED_EXEMPLARS", "append observation; predict by kernel over stored points", "M5/M3"),
    ("M5 kNN / case-based reasoning", "DISCRETE_FINITE", "LOCAL_O1", ["exact_counterexample"], "STORE_MATCH_CYCLE", "INDEXED_EXEMPLARS", "insert exemplar; retrieve by similarity", "M5"),
    ("VSA / HDC associative memory ; transformer in-context learning (frozen weights)", "BOUNDED_NUMERIC", "LOCAL_O1", ["exact_counterexample"], "ACYCLIC_FIXED_DEPTH", "INDEXED_EXEMPLARS", "bundle one new vector / append one demonstration; acyclic read-out", "M5"),
    ("LLM + retrieval store agent (frozen model)", "MIXED", "LOCAL_O1", ["exact_counterexample"], "ACYCLIC_FIXED_DEPTH", "INDEXED_EXEMPLARS", "discrete store grown per interaction; numeric frozen weights", "M6"),
    ("ACT-R (utility learning + declarative chunks)", "MIXED", "LOCAL_O1", ["scalar_loss", "exact_counterexample"], "STORE_MATCH_CYCLE", "RULE_SET", "production utilities updated by reward; chunks added", "M6"),
    ("Sigma graphical architecture", "MIXED", "DENSE_LINEAR", ["scalar_loss", "likelihood_score"], "BOUNDED_LOOP", "PARAMETER_ARRAY", "summary-product message passing; gradient learning over factor functions", "M6"),
    ("DreamCoder (full: neural recognition + library)", "MIXED", "SPARSE_SUBLINEAR", ["scalar_loss", "exact_counterexample", "likelihood_score"], "ENUMERATE_TEST_CYCLE", "TERM_LIBRARY", "enumeration guided by a trained recognition model; library compression by likelihood", "M6"),
    ("Inference compilation (neural proposal + probabilistic program)", "MIXED", "DENSE_LINEAR", ["scalar_loss", "likelihood_score"], "SAMPLE_SCORE_CYCLE", "PARAMETER_ARRAY", "proposal net trained by scalar loss; program scored by likelihood", "M6"),
    ("NEAT / neuroevolution of numeric nets", "BOUNDED_NUMERIC", "SPARSE_SUBLINEAR", ["scalar_loss"], "ENUMERATE_TEST_CYCLE", "PARAMETER_ARRAY", "population of nets varied by structural mutation, selected by fitness", "M4/M2"),
    # --- registration-gap occupants found by the first census pass (structural pairwise holes that
    # turned out to be designed forms missing from the atlas) ---
    ("ProbLog / PRISM / stochastic logic programs", "MIXED", "SPARSE_SUBLINEAR", ["likelihood_score"], "SAMPLE_SCORE_CYCLE", "RULE_SET", "probabilistic clauses; sampling/weighted model counting; parameter learning by EM", "M3/M1"),
    ("Dirichlet-process mixture with Gibbs sampling (Bayesian nonparametrics)", "MIXED", "SPARSE_SUBLINEAR", ["likelihood_score"], "SAMPLE_SCORE_CYCLE", "INDEXED_EXEMPLARS", "exemplars with sampled cluster assignments; scored by likelihood", "M3/M5"),
    ("Kanerva sparse distributed memory", "BOUNDED_NUMERIC", "LOCAL_O1", ["exact_counterexample"], "STORE_MATCH_CYCLE", "PARAMETER_ARRAY", "hard-location counters incremented on write; read by address match", "M5"),
    ("Conjugate exponential-family Bayesian update", "BOUNDED_NUMERIC", "LOCAL_O1", ["likelihood_score"], "ACYCLIC_FIXED_DEPTH", "PARAMETER_ARRAY", "sufficient statistics updated in O(1) per observation", "M3"),
    ("Case-based planning (CHEF-class) / retrieval-augmented synthesis", "DISCRETE_FINITE", "LOCAL_O1", ["exact_counterexample"], "ENUMERATE_TEST_CYCLE", "INDEXED_EXEMPLARS", "retrieve a stored case, adapt by bounded search, store the repaired case", "M5/M2"),
    ("Compiled production / discrimination network (Rete-compiled automaton)", "DISCRETE_FINITE", "LOCAL_O1", ["exact_counterexample"], "BOUNDED_LOOP", "RULE_SET", "rules compiled into a network executed as a bounded-step automaton; rule added per chunk", "M1"),
    ("OCM-like explicit method library with applicability matching (KSO serving)", "DISCRETE_FINITE", "LOCAL_O1", ["exact_counterexample", "query_access"], "STORE_MATCH_CYCLE", "TERM_LIBRARY", "typed methods retrieved by applicability, executed, verified; library grows per admitted method (one candidate morphology, not a privileged substrate: #377 §15)", "M2/M1"),
    ("Batch re-induction per event (retrain-from-scratch rule/tree learner)", "DISCRETE_FINITE", "DENSE_LINEAR", ["exact_counterexample"], "ACYCLIC_FIXED_DEPTH", "NONE", "the whole discrete model is regenerated from all data on each event; degenerate but designed", "M1"),
    ("Sparse distributed / winner-take-all coded memory (Hebbian associative)", "BOUNDED_NUMERIC", "LOCAL_O1", [], "ACYCLIC_FIXED_DEPTH", "PARAMETER_ARRAY", "local Hebbian write, no external feedback", "M4/M5"),
]


def cell_of(o):
    return (o[1], o[2], fb_key(o[3]), o[4], o[5])


def hamming(a, b):
    return sum(1 for i in range(5) if a[i] != b[i])


def main():
    fb_subsets = [fb_key(s) for r in range(len(FB_MENU) + 1) for s in itertools.combinations(FB_MENU, r)]
    all_cells = list(itertools.product(THETA, LOC, fb_subsets, EXEC, STORE))
    coherent_cells, incoherent = [], Counter()
    for c in all_cells:
        ok, why = coherent(c)
        (coherent_cells.append(c) if ok else incoherent.update([why]))
    cohset = set(coherent_cells)
    occ = defaultdict(list)
    bad = []
    for o in OCCUPANTS:
        c = cell_of(o)
        if c not in cohset:
            bad.append((o[0], coherent(c)[1]))
        occ[c].append(o[0])
    if bad:
        print("OCCUPANT VIOLATES COHERENCE:", bad, file=sys.stderr)
        sys.exit(2)
    occupied = set(occ)
    holes = [c for c in coherent_cells if c not in occupied]

    # pairwise projections
    proj_holes = {}
    for i, j in itertools.combinations(range(5), 2):
        used = {(c[i], c[j]) for c in occupied}
        possible = {(c[i], c[j]) for c in coherent_cells}
        proj_holes[f"{OBS[i]}x{OBS[j]}"] = sorted([list(map(lambda v: list(v) if isinstance(v, tuple) else v, p)) for p in (possible - used)])

    # structural projections exclude feedback_dependence (index 2); feedback projections are reported separately
    STRUCT = [0, 1, 3, 4]
    used_pairs = {(i, j): {(c[i], c[j]) for c in occupied} for i, j in itertools.combinations(range(5), 2)}
    struct_holes = {f"{OBS[i]}x{OBS[j]}": sorted(list(p) for p in ({(c[i], c[j]) for c in coherent_cells} - used_pairs[(i, j)]))
                    for i, j in itertools.combinations(STRUCT, 2)}
    # distance histogram + frontier holes (structural criterion)
    occ_list = sorted(occupied)
    dist_hist = Counter()
    frontier = []
    for h in holes:
        d = min(hamming(h, o) for o in occ_list)
        dist_hist[d] += 1
        if d == 1 and len(h[2]) <= 2:
            closes_s = sum(1 for i, j in itertools.combinations(STRUCT, 2) if (h[i], h[j]) not in used_pairs[(i, j)])
            closes_f = sum(1 for i, j in itertools.combinations(range(5), 2) if 2 in (i, j) and (h[i], h[j]) not in used_pairs[(i, j)])
            if closes_s >= 1:
                nearest = sorted(occ[o][0] for o in occ_list if hamming(h, o) == 1)
                frontier.append({"cell": dict(zip(OBS, [list(h[2]) if k == 2 else h[k] for k in range(5)])),
                                 "structural_pairwise_holes_closed": closes_s, "feedback_pairwise_holes_closed": closes_f,
                                 "adjacent_occupants": nearest[:4]})
    frontier.sort(key=lambda r: (-r["structural_pairwise_holes_closed"], -r["feedback_pairwise_holes_closed"], json.dumps(r["cell"], sort_keys=True)))

    multi = {json.dumps(dict(zip(OBS, [list(c[2]) if k == 2 else c[k] for k in range(5)]))): names for c, names in occ.items() if len(names) > 1}

    receipt = {
        "schema": "SignatureHoleCensusV1",
        "status": "EXPLORATORY_E0_THEORY_INSTRUMENT__NOT_EVIDENCE_OF_ANY_MORPHOLOGY",
        "issue": 377,
        "signature_space": {"theta_type": THETA, "update_locality": LOC, "feedback_menu": FB_MENU, "execution_shape": EXEC, "store_discipline": STORE},
        "raw_cells": len(all_cells),
        "coherent_cells": len(coherent_cells),
        "incoherent_by_constraint": dict(incoherent),
        "registered_occupants": len(OCCUPANTS),
        "occupied_cells": len(occupied),
        "hole_cells": len(holes),
        "multi_occupant_cells": multi,
        "pairwise_projection_holes": proj_holes,
        "structural_pairwise_holes_after_atlas_completion": struct_holes,
        "distance_to_nearest_occupant_histogram": dict(sorted(dist_hist.items())),
        "frontier_holes_distance1_closing_structural_projection": frontier,
        "occupant_table": [{"name": o[0], "cell": dict(zip(OBS, [o[1], o[2], list(fb_key(o[3])), o[4], o[5]])), "rationale": o[6], "nearest_signature": o[7]} for o in OCCUPANTS],
        "claim_ceiling": "A hole is a property of the registered coordinate system (MORPHOLOGY_SIGNATURES_V2.json), not of nature: it may be empty because the combination is useless, because the observables are too coarse, or because it was never built. Only a frontier computation (Stage E) can say whether a hole is Pareto-relevant. Multi-occupant cells show which registered parents are indistinguishable at this resolution; that is a statement about resolution, not about equivalence (GMI-T3 requires bounded mutual compilation).",
        "what_this_gives_the_ultimate_question": "A frozen, finite, pre-search list of candidate property vectors for an undesigned morphology (frontier_holes...), each adjacent to a known form and structurally new in at least two pairwise projections; a later neutral search result must be classifiable into one of these cells or into an occupied one — either outcome is a prediction test (#377 §18 criteria still apply).",
    }
    blob = json.dumps(receipt, sort_keys=True, indent=1)
    receipt["receipt_sha256"] = hashlib.sha256(blob.encode()).hexdigest()
    with open("SIGNATURE_HOLE_CENSUS_V1.json", "w") as f:
        json.dump(receipt, f, indent=1, sort_keys=True)
    print(json.dumps({k: receipt[k] for k in ["raw_cells", "coherent_cells", "incoherent_by_constraint", "registered_occupants", "occupied_cells", "hole_cells", "distance_to_nearest_occupant_histogram", "receipt_sha256"]}, indent=1))
    print("multi-occupant cells:", len(multi))
    print("frontier holes (structural, |fb|<=2):", len(frontier))
    for k, v in struct_holes.items():
        print(f"STRUCTURAL projection {k}: {len(v)} unused pairs -> {v}")


if __name__ == "__main__":
    main()
