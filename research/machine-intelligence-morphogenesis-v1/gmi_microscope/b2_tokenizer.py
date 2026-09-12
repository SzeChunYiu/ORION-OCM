"""B2.1 -- tokenizer granularity: the morphology/resource tradeoff measured as an exact frontier.

Stage B2 row B2.1 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md section 9:
    "Factorial: surface morphology complexity x vocabulary size x sequence length price x embedding/output memory
     price. Endpoints: sample efficiency, serve tokens, memory, cross-remint robustness.
     Prediction: no universal tokenizer size; optimum follows morphology/resource tradeoff."

SYNTHETIC EXACT MICROSCOPE at laptop scope. Every corpus is enumerated in full, every segmentation is deterministic,
every capability and every cost is an exact rational, and there is NO randomness anywhere. It is NOT evidence about a
trained neural network and NOT a claim about any real tokenizer; it measures whether the four declared axes move the
cost-optimal vocabulary size, on obligations whose unit structure is declared. Registry entries TF-001 (tokenization),
TF-002 (vocabulary size), TF-003 (token embeddings), TF-044 (context window, through serve tokens).

Declared ecology
----------------
Surface alphabet Sigma = {0..7} (eight symbols). A MORPHOLOGY m declares eight semantic UNITS, each a string of m
surface symbols, and a value val(U) in {1, 1, -2, -2, 3, 3, 0, 0} (four distinct values, each carried by two units --
the repetition is what makes the remint of the next paragraph semantics-preserving). A corpus string is the
concatenation of THREE units, so every corpus has exactly 8^3 = 512 strings and they differ only in surface length
(3, 6, 9 symbols). The obligation is additive over units:

    q(u) = sum of val(U) over the three units of u.

MORPH1 units are the eight single symbols; MORPH2 units are eight declared digrams; MORPH3 eight declared trigrams.
The digrams and trigrams include surface anagrams with DIFFERENT values ((0,1) at 1 against (1,0) at 3), so a reader
that sees only symbol counts must merge obligation-distinct strings. That is measured, not assumed.

Arms (rows)
-----------
A tokenizer is a frozen merge table: k BPE-style merges learned on the corpus by repeatedly merging the most frequent
adjacent token pair (ties broken lexicographically), applied in learned order. Vocabulary size V = 8 + k. The reader
on top of it is a BAG-OF-TOKENS map: answer(u) = sum over tokens t of seg(u) of w[t].

    CHAR (k = 0) ..... V = 8, longest sequences.
    k = 2 .. 24 ...... progressively coarser frequency-learned merge tables.
    ORACLE_UNIT ...... the declared unit-aligned tokenizer: its vocabulary is the eight symbols plus the eight UNITS,
                       and it segments on unit boundaries. It is the analogue of the ORACLE arm of b2_route.py -- a
                       tokenizer that is handed the morphology instead of learning it -- and it is what makes the
                       SIZE axis separable from the ALIGNMENT axis: it has the same vocabulary size as the k = 8 BPE
                       row and a different segmentation.
    CONSTANT ......... the rule-22 hindsight-optimal constant-answer control row. It reads no developed state and is
                       charged nothing, which rule 21 as narrowed by RV-377-073 permits.

Two capabilities are measured for every row, and they are different things:

    hindsight_optimal_reader ... the best FUNCTION of the token multiset, computed by plurality within each feature
                                 class. This is the PARENT-MAXIMAL reader for this feature map (protocol rule 19): no
                                 bag-of-tokens machine of any kind, linear or not, can beat it.
    linearly_realizable ........ whether the exact linear system Phi w = q is consistent (exact rational rank test).

Endpoints
---------
serve tokens ......... mean tokens per corpus string, exact rational; one charged op per token served.
memory ............... 2*V*d embedding/unembedding scalars at declared d = 4.
sample efficiency .... TWO exact quantities, because the reader class decides which one is meaningful:
                       lookup ... the first prefix of the canonical order that covers every feature class occurring
                                  in the corpus, i.e. what the parent-maximal (table) reader has to have seen.
                       linear ... the first prefix whose design matrix reaches the full design matrix's rank, i.e.
                                  what a bag-of-tokens LINEAR reader has to have seen. Defined only where the exact
                                  linear system is consistent.
cross-remint ......... a declared permutation pi of Sigma renames the surface. Units are respelled, values are
                       carried over, so the obligation is unchanged. The MERGE TABLE IS FROZEN (it is the C component
                       and is not refit); the reader IS refit with hindsight on the reminted world. The endpoint is
                       the refitted capability there.

Run: python3 -m gmi_microscope.b2_tokenizer
"""
from __future__ import annotations

import itertools
import json
import os
from fractions import Fraction as Fr

from . import b2_common as C
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = C.KIND

SIGMA = tuple(range(8))
UNITS_PER_STRING = 3
D_EMBED = 4                       # embedding width, declared
THETA = Fr(1)                     # semantic adequacy = exactness; "burden at fixed adequacy"
VALUES = (1, 1, -2, -2, 3, 3, 0, 0)
REMINT = {0: 1, 1: 2, 2: 0, 3: 4, 4: 5, 5: 3, 6: 7, 7: 6}   # declared surface permutation pi

MORPHOLOGIES = {
    "MORPH1_symbol": [(s,) for s in SIGMA],
    "MORPH2_digram": [(0, 1), (2, 3), (4, 5), (6, 7), (1, 0), (3, 2), (5, 4), (7, 6)],
    "MORPH3_trigram": [(0, 1, 2), (3, 4, 5), (6, 7, 0), (1, 3, 5), (2, 1, 0), (5, 4, 3), (0, 7, 6), (5, 3, 1)],
}
MERGE_LADDER = (0, 2, 4, 8, 12, 16, 20, 24)
PRICES = {                         # (c_mem per embedding scalar, c_len per served token)
    "mem1_len1": (Fr(1), Fr(1)),
    "mem1_len4": (Fr(1), Fr(4)),
    "mem4_len1": (Fr(4), Fr(1)),
    "mem1_len16": (Fr(1), Fr(16)),
}


# ------------------------------------------------------------------------------------------------ corpus
def corpus_of(units):
    """Every concatenation of UNITS_PER_STRING units, in the declared canonical (odometer) order."""
    out = []
    for combo in itertools.product(range(len(units)), repeat=UNITS_PER_STRING):
        surface = tuple(s for i in combo for s in units[i])
        out.append((surface, sum(VALUES[i] for i in combo)))
    return out


# ------------------------------------------------------------------------------------------------ tokenizer
def learn_merges(corpus, k):
    """BPE-style: repeatedly merge the most frequent adjacent token pair over the whole corpus. Deterministic:
    ties are broken by the lexicographically smallest pair. Returns the merge list in learned order."""
    seqs = [[(s,) for s in surf] for surf, _ in corpus]
    merges = []
    for _ in range(k):
        freq = {}
        for seq in seqs:
            for a, b in zip(seq, seq[1:]):
                freq[(a, b)] = freq.get((a, b), 0) + 1
        if not freq:
            break
        best = max(sorted(freq), key=lambda p: freq[p])
        merges.append(best)
        a, b = best
        for i, seq in enumerate(seqs):
            out = []
            j = 0
            while j < len(seq):
                if j + 1 < len(seq) and seq[j] == a and seq[j + 1] == b:
                    out.append(a + b)
                    j += 2
                else:
                    out.append(seq[j])
                    j += 1
            seqs[i] = out
    return merges


def segment(surface, merges):
    """Apply the frozen merge table in learned order. Deterministic, left to right."""
    seq = [(s,) for s in surface]
    for a, b in merges:
        out = []
        j = 0
        while j < len(seq):
            if j + 1 < len(seq) and seq[j] == a and seq[j + 1] == b:
                out.append(a + b)
                j += 2
            else:
                out.append(seq[j])
                j += 1
        seq = out
    return seq


def segment_units(surface, units):
    """The declared unit-aligned segmentation: longest match against the declared unit set, left to right. Every
    corpus string is a concatenation of units, so this always lands on unit boundaries."""
    seq = []
    i = 0
    order = sorted(units, key=lambda u: (-len(u), u))
    while i < len(surface):
        for u in order:
            if surface[i:i + len(u)] == u:
                seq.append(u)
                i += len(u)
                break
        else:
            seq.append((surface[i],))
            i += 1
    return seq


def vocabulary(merges):
    """Single symbols are always in the vocabulary (the tokenizer is total), plus one piece per merge."""
    return sorted(set([(s,) for s in SIGMA] + [a + b for a, b in merges]))


# ------------------------------------------------------------------------------------------------ readers
def unit_aligned_fraction(corpus, segmenter, units):
    """The fraction of corpus strings whose segmentation lands on every declared unit boundary. It separates the SIZE
    of a merge table from its ALIGNMENT with the morphology."""
    us = [tuple(u) for u in units]
    ok = 0
    for surf, _ in corpus:
        cuts = set()
        i = 0
        for t in segmenter(surf):
            i += len(t)
            cuts.add(i)
        need = set()
        i = 0
        j = 0
        while i < len(surf):
            for u in sorted(us, key=lambda u: (-len(u), u)):
                if surf[i:i + len(u)] == u:
                    i += len(u)
                    break
            else:
                i += 1
            need.add(i)
        if need <= cuts:
            ok += 1
    return Fr(ok, len(corpus))


def features(corpus, segmenter, vocab):
    idx = {t: i for i, t in enumerate(vocab)}
    rows = []
    ntok = []
    for surf, _ in corpus:
        seg = segmenter(surf)
        v = [0] * len(vocab)
        for t in seg:
            v[idx[t]] += 1
        rows.append(v)
        ntok.append(len(seg))
    return rows, ntok


def lookup_sample_efficiency(rows):
    """The first prefix of the declared canonical order that covers every feature class occurring in the corpus:
    exactly what the parent-maximal (table) reader must have seen before it is determined everywhere."""
    classes = {tuple(r) for r in rows}
    seen = set()
    for i, r in enumerate(rows):
        seen.add(tuple(r))
        if len(seen) == len(classes):
            return i + 1
    return len(rows)


def hindsight_optimal_reader(rows, targets):
    """The best FUNCTION of the feature vector: plurality within each feature class (protocol rule 19 --
    no bag-of-tokens machine, linear or not, beats it). Returns (capability, n_classes, merged_pairs)."""
    groups = {}
    for r, t in zip(rows, targets):
        groups.setdefault(tuple(r), []).append(t)
    correct = 0
    merged = 0
    for v in groups.values():
        counts = {}
        for t in v:
            counts[t] = counts.get(t, 0) + 1
        correct += max(counts.values())
        merged += sum(1 for i in range(len(v)) for j in range(i + 1, len(v)) if v[i] != v[j])
    return Fr(correct, len(targets)), len(groups), merged


class Basis:
    """Incremental exact row reduction: rank and span membership without re-eliminating the whole matrix."""

    def __init__(self, n):
        self.n = n
        self.piv = {}     # pivot column -> reduced row (list of Fr), last entry is the target

    def reduce(self, row, tgt):
        v = [Fr(x) for x in row] + [Fr(tgt)]
        for c, pr in sorted(self.piv.items()):
            if v[c] != 0:
                f = v[c]
                v = [x - f * y for x, y in zip(v, pr)]
        return v

    def add(self, row, tgt):
        v = self.reduce(row, tgt)
        c = next((i for i in range(self.n) if v[i] != 0), None)
        if c is None:
            return "dependent" if v[self.n] == 0 else "inconsistent"
        inv = Fr(1) / v[c]
        v = [x * inv for x in v]
        for d, pr in list(self.piv.items()):
            if pr[c] != 0:
                f = pr[c]
                self.piv[d] = [x - f * y for x, y in zip(pr, v)]
        self.piv[c] = v
        return "rank+1"

    def rank(self):
        return len(self.piv)

    def solution(self):
        w = [Fr(0)] * self.n
        for c, pr in self.piv.items():
            w[c] = pr[self.n]
        return w


def fit_and_measure(rows, targets):
    """One pass in the declared canonical order: exact rank, consistency, a solution, and the sample-efficiency index
    (the first prefix length at which the design matrix reaches its final rank)."""
    n = len(rows[0])
    B = Basis(n)
    consistent = True
    reach = None
    for i, (r, t) in enumerate(zip(rows, targets)):
        st = B.add(r, t)
        if st == "inconsistent":
            consistent = False
    full_rank = B.rank()
    # second pass for the sample-efficiency index: the first prefix reaching full_rank
    B2 = Basis(n)
    for i, (r, t) in enumerate(zip(rows, targets)):
        B2.add(r, t)
        if B2.rank() == full_rank:
            reach = i + 1
            break
    return {"rank": full_rank, "consistent": consistent, "solution": B.solution() if consistent else None,
            "sample_efficiency_examples": reach}


def apply_reader(rows, w):
    return [sum(Fr(x) * wi for x, wi in zip(r, w)) for r in rows]


# ------------------------------------------------------------------------------------------------ one cell
def _row_record(name, vocab, segmenter, corpus, targets, rcorpus, rtargets, n, merges, units):
    phi, ntok = features(corpus, segmenter, vocab)
    cap, nclasses, merged_pairs = hindsight_optimal_reader(phi, targets)
    fit = fit_and_measure(phi, targets)
    mean_tok = Fr(sum(ntok), n)

    # cross-remint: SAME frozen tokenizer, reader refit with hindsight on the reminted world
    rphi, rntok = features(rcorpus, segmenter, vocab)
    rcap, rclasses, rmerged = hindsight_optimal_reader(rphi, rtargets)
    rfit = fit_and_measure(rphi, rtargets)

    exact = cap == 1
    # the reader's own description is CHARGED (stage B0.3 metering hostility: a table reader may not hide its size in
    # the tokenizer's embedding count). A linearly realizable row stores V weights; a row that is exact only as a
    # TABLE over feature classes stores one answer per class, and that is what it costs.
    reader_params = len(vocab) if fit["consistent"] else nclasses
    return name, {
        "merges": merges, "vocabulary_size_V": len(vocab),
        "merge_table": [list(a) + ["|"] + list(b) for a, b in merges] if isinstance(merges, list) else merges,
        "mean_tokens_per_string": str(mean_tok), "mean_tokens_float": round(float(mean_tok), 6),
        "total_tokens_over_corpus": sum(ntok),
        "embedding_scalars_2Vd": 2 * len(vocab) * D_EMBED,
        "reader_description_scalars": reader_params,
        "reader_class": "linear bag-of-tokens (V weights)" if fit["consistent"] else "table over feature classes",
        "description_scalars_total": 2 * len(vocab) * D_EMBED + reader_params,
        "unit_aligned_segmentation_fraction": str(unit_aligned_fraction(corpus, segmenter, units)),
        "hindsight_optimal_bag_reader_capability": str(cap),
        "hindsight_optimal_bag_reader_capability_float": round(float(cap), 6),
        "distinct_feature_classes": nclasses,
        "obligation_distinct_pairs_merged_by_the_feature_map": merged_pairs,
        "lookup_sample_efficiency_examples": lookup_sample_efficiency(phi),
        "linear_system_rank": fit["rank"], "linear_system_consistent": fit["consistent"],
        "linear_sample_efficiency_examples": fit["sample_efficiency_examples"] if fit["consistent"] else None,
        "exact": exact,
        "admissible_at_theta": exact,
        "serves_developed_state": True,
        "charged_serve_ops_per_query": str(mean_tok),     # one charged op per token served
        "remint_mean_tokens": str(Fr(sum(rntok), n)),
        "remint_hindsight_optimal_capability": str(rcap),
        "remint_hindsight_optimal_capability_float": round(float(rcap), 6),
        "remint_linear_consistent": rfit["consistent"],
        "remint_exact": rcap == 1,
        "remint_robust": rcap == cap,
    }


def run_cell(mname):
    units = MORPHOLOGIES[mname]
    corpus = corpus_of(units)
    targets = [t for _, t in corpus]
    n = len(corpus)

    # rule 22: the hindsight-optimal CONSTANT answer
    ctrl = C.constant_control(corpus, lambda it: it[1])
    void = C.obligation_is_void(ctrl["capability"], THETA)

    # the reminted world: units respelled by pi, values carried over; the obligation is unchanged
    runits = [tuple(REMINT[s] for s in u) for u in units]
    rcorpus = corpus_of(runits)
    rtargets = [t for _, t in rcorpus]

    rows_out = {}
    for k in MERGE_LADDER:
        merges = learn_merges(corpus, k)          # learned on the ORIGINAL world, then FROZEN
        vocab = vocabulary(merges)
        name, rec = _row_record("BPE_k%02d_V%02d" % (k, len(vocab)), vocab,
                                lambda surf, m=merges: segment(surf, m),
                                corpus, targets, rcorpus, rtargets, n, merges, units)
        rows_out[name] = rec

    # the declared unit-aligned arm: same morphology handed to the tokenizer instead of learned from frequencies
    uvocab = sorted(set([(s,) for s in SIGMA] + [tuple(u) for u in units]))
    name, rec = _row_record("ORACLE_UNIT_V%02d" % len(uvocab), uvocab,
                            lambda surf, u=units: segment_units(surf, [tuple(x) for x in u]),
                            corpus, targets, rcorpus, rtargets, n, "declared unit boundaries (not learned)", units)
    rows_out[name] = rec

    # rule 21 audit, with the constant control carried as a row
    audit_rows = {name: {"admissible": r["admissible_at_theta"], "serves_developed_state": True,
                         "charged_serve_ops_per_query": Fr(r["charged_serve_ops_per_query"])}
                  for name, r in rows_out.items()}
    audit_rows["CONSTANT_CONTROL"] = {"admissible": bool(ctrl["capability"] >= THETA),
                                      "serves_developed_state": False, "charged_serve_ops_per_query": 0}
    audit = C.charged_serve_audit(audit_rows)

    # rule 28 frontier: EXACT rows only (burden at fixed semantic adequacy), one context per price vector
    ctxs = {pname: {name: (c_mem * r["description_scalars_total"], c_len * Fr(r["charged_serve_ops_per_query"]))
                    for name, r in rows_out.items() if r["exact"]}
            for pname, (c_mem, c_len) in PRICES.items()}
    minimal_exact_V = min((r["vocabulary_size_V"] for r in rows_out.values() if r["exact"]), default=None)
    return {
        "morphology": mname, "unit_length": len(units[0]), "units": [list(u) for u in units],
        "unit_values": list(VALUES), "corpus_strings": n, "surface_length": len(corpus[0][0]),
        "distinct_obligation_values": len(set(targets)),
        "rule22_constant_control": {"best_constant_answer": ctrl["best_constant_answer"],
                                    "capability": str(ctrl["capability"]),
                                    "capability_float": round(float(ctrl["capability"]), 6),
                                    "theta": str(THETA), "obligation_void": void, "rule": "see protocol_rules_carried.rule_22 at the receipt's top level"},
        "rule21_charged_serve_audit": audit,
        "rows": rows_out,
        "minimal_exact_vocabulary_size": minimal_exact_V,
        "exact_rows": sorted(name for name, r in rows_out.items() if r["exact"]),
        "exact_and_linear_rows": sorted(name for name, r in rows_out.items()
                                        if r["exact"] and r["linear_system_consistent"]),
        "frontier_cost_lines_by_price": {p: {r: [str(a), str(b)] for r, (a, b) in v.items()} for p, v in ctxs.items()},
        "_lines": ctxs,
        "census_of_rows": C.census(len(rows_out), alphabet="the eight-symbol surface alphabet Sigma plus BPE merge "
                                                           "pieces and the declared units over it",
                                   servability_filter="exact under the parent-maximal bag-of-tokens reader at theta = 1",
                                   ecology=mname, what="tokenizer configurations on the declared ladder"),
    }


FRONTIER_NOTE_TEXT = ("rows are EXACT tokenizers only (semantic adequacy held at theta = 1 under the parent-maximal "
                      "bag reader); A = c_mem * (2Vd embedding scalars + the READER's own description scalars), "
                      "E = c_len * mean tokens served per query. Charging the reader is stage B0.3 metering hostility: "
                      "a row exact only as a table over feature classes may not hide that table's size in the "
                      "tokenizer's embedding count.")


def main(path=None):
    cells = {mname: run_cell(mname) for mname in MORPHOLOGIES}
    # ONE shared reuse grid for the whole receipt, built from the crossovers of EVERY (morphology, price) context, so
    # that a single grid maximum is honest for all of them and gmi_microscope/grid_audit.py grades one grid (rule 28).
    ctxs = {f"{m}|{p}": cells[m]["_lines"][p] for m in cells for p in PRICES}
    b2_frontiers, shared_grid = C.frontier_set(ctxs, note=FRONTIER_NOTE_TEXT)
    for m in cells:
        # the cell carries a COMPACT summary; the full auditable block lives once, under b2_frontiers
        cells[m]["frontier_by_price"] = {p: {k: b2_frontiers[f"{m}|{p}"][k] for k in
                                             ("cost_coordinates_A_E", "crossovers_H_star", "largest_crossover",
                                              "grid_max_H", "dg2_grid_covers_twice_every_crossover",
                                              "occupants_on_grid", "occupant_for_all_sufficiently_large_H",
                                              "rows_never_occupying_a_cell", "frontier_runs")} for p in PRICES}
        del cells[m]["_lines"]

    def opt_V(cell, price, H):
        """the cost-minimizing EXACT vocabulary size at this price and reuse horizon."""
        fb = cell["frontier_by_price"][price]
        co = fb["cost_coordinates_A_E"]
        if not co:
            return None
        cost = {r: Fr(v[0]) + Fr(H) * Fr(v[1]) for r, v in co.items()}
        best = min(sorted(cost), key=lambda r: cost[r])
        return cell["rows"][best]["vocabulary_size_V"]

    H_probe = (1, 64, 1024)
    optima = {f"{m}|{p}|H={H}": opt_V(cells[m], p, H) for m in cells for p in PRICES for H in H_probe}

    m1, m2, m3 = "MORPH1_symbol", "MORPH2_digram", "MORPH3_trigram"
    char_rows = {m: cells[m]["rows"]["BPE_k00_V08"] for m in cells}
    oracle = {m: next(r for n, r in cells[m]["rows"].items() if n.startswith("ORACLE_UNIT")) for m in cells}
    bpe_ladder = {m: [cells[m]["rows"][n] for n in sorted(cells[m]["rows"]) if n.startswith("BPE_")] for m in cells}

    def on_frontier_everywhere(m):
        name = next(n for n in cells[m]["rows"] if n.startswith("ORACLE_UNIT"))
        return all(name in occ for fb in cells[m]["frontier_by_price"].values() for _, _, occ in fb["frontier_runs"])

    clauses = {
        "C1_character_level_row_is_exact_only_where_units_are_single_symbols": (
            char_rows[m1]["exact"] and not char_rows[m2]["exact"] and not char_rows[m3]["exact"]),
        "C2_every_morphology_has_at_least_one_exact_row_on_the_declared_ladder": all(
            c["minimal_exact_vocabulary_size"] is not None for c in cells.values()),
        "C3_minimal_exact_vocabulary_size_is_nondecreasing_in_unit_length_and_strictly_larger_at_m3": (
            cells[m1]["minimal_exact_vocabulary_size"] <= cells[m2]["minimal_exact_vocabulary_size"]
            <= cells[m3]["minimal_exact_vocabulary_size"]
            and cells[m1]["minimal_exact_vocabulary_size"] < cells[m3]["minimal_exact_vocabulary_size"]),
        "C4_no_universal_optimum_across_morphologies": any(
            len({optima[f"{m}|{p}|H={H}"] for m in cells}) > 1 for p in PRICES for H in H_probe),
        "C5_no_universal_optimum_across_reuse_horizons": any(
            len({optima[f"{m}|{p}|H={H}"] for H in H_probe}) > 1 for m in cells for p in PRICES),
        "C6_no_universal_optimum_across_price_vectors": any(
            len({optima[f"{m}|{p}|H={H}"] for p in PRICES}) > 1 for m in cells for H in H_probe),
        "C7_linear_sample_efficiency_is_nondecreasing_in_V_along_the_bpe_ladder": all(
            all(a["linear_sample_efficiency_examples"] <= b["linear_sample_efficiency_examples"]
                for a, b in zip(d, d[1:]))
            for d in [[r for r in lad if r["linear_sample_efficiency_examples"] is not None]
                      for lad in bpe_ladder.values()]),
        "C8_charged_serve_tokens_are_nonincreasing_in_V_along_the_bpe_ladder": all(
            all(Fr(a["charged_serve_ops_per_query"]) >= Fr(b["charged_serve_ops_per_query"])
                for a, b in zip(lad, lad[1:])) for lad in bpe_ladder.values()),
        "C9_rule22_constant_control_is_below_theta_in_every_morphology": all(
            not c["rule22_constant_control"]["obligation_void"] for c in cells.values()),
        "C10_rule21_no_admissible_row_serves_developed_state_at_zero_charged_cost": all(
            c["rule21_charged_serve_audit"]["passed"] for c in cells.values()),
        "C11_character_level_capability_is_invariant_under_the_declared_remint": all(
            char_rows[m]["remint_hindsight_optimal_capability"] == char_rows[m]["hindsight_optimal_bag_reader_capability"]
            for m in cells),
        "C12_at_least_one_exact_coarser_row_loses_exactness_under_the_remint": any(
            not c["rows"][name]["remint_exact"] for c in cells.values() for name in c["exact_rows"]),
        "C13_dg2_every_frontier_grid_covers_twice_every_crossover": all(
            fb["dg2_grid_covers_twice_every_crossover"] for c in cells.values() for fb in c["frontier_by_price"].values()),
        "C14_at_equal_V16_the_unit_aligned_row_is_exact_and_linear_where_the_frequency_learned_row_is_neither": all(
            oracle[m]["vocabulary_size_V"] == cells[m]["rows"]["BPE_k08_V16"]["vocabulary_size_V"]
            and oracle[m]["exact"] and oracle[m]["linear_system_consistent"]
            and not (cells[m]["rows"]["BPE_k08_V16"]["exact"] and cells[m]["rows"]["BPE_k08_V16"]["linear_system_consistent"])
            for m in (m2, m3)),
        "C15_frequency_learned_merge_tables_do_not_recover_unit_boundaries_at_k_ge_8": all(
            Fr(r["unit_aligned_segmentation_fraction"]) < 1
            for m in (m2, m3) for n, r in cells[m]["rows"].items() if n.startswith("BPE_k") and r["merges"] and len(r["merges"]) >= 8),
        "C16_lookup_sample_efficiency_is_nondecreasing_in_V_along_the_bpe_ladder": all(
            all(a["lookup_sample_efficiency_examples"] <= b["lookup_sample_efficiency_examples"]
                for a, b in zip(lad, lad[1:])) for lad in bpe_ladder.values()),
        "C17_the_unit_aligned_row_occupies_every_frontier_cell_at_every_price_in_MORPH2_and_MORPH3": (
            on_frontier_everywhere(m2) and on_frontier_everywhere(m3)),
        "C18_at_the_largest_declared_horizon_the_cost_optimal_vocabulary_on_MORPH1_is_not_the_smallest": (
            optima[f"{m1}|mem1_len1|H=1024"] != cells[m1]["minimal_exact_vocabulary_size"]),
    }

    receipt = {
        "schema": "GMI_B2_01_TOKENIZER_V1", "issue": [377, 422], "row": "B2.1 tokenizer granularity",
        "revival_id": "RV-377-090",
        "evidence_kind": KIND,
        "evidence_class": "SYNTHETIC_EXACT_EMPIRICAL (tier S): a measured quantity in a declared synthetic ecology, "
                          "frozen before the run. NOT a closed-form identity and NOT neural evidence.",
        "theorems": ["TM-10 parameter-sharing symmetry principle (the vocabulary/sharing tradeoff)",
                     "TMT-2 finite-window impossibility is NOT invoked here: the merging measured below is a property "
                     "of the FEATURE MAP, not of a context window"],
        "registry_entries": ["TF-001 tokenization / segmentation", "TF-002 vocabulary size", "TF-003 token embeddings",
                             "TF-004 embedding dimension"],
        "declared_instrument": {
            "surface_alphabet": list(SIGMA), "units_per_string": UNITS_PER_STRING, "unit_values": list(VALUES),
            "embedding_width_d": D_EMBED, "theta": str(THETA),
            "merge_ladder": list(MERGE_LADDER), "price_vectors": {k: [str(a), str(b)] for k, (a, b) in PRICES.items()},
            "remint_permutation_pi": {str(k): v for k, v in REMINT.items()},
            "arithmetic": "exact rationals (fractions.Fraction) throughout; ranks by exact row reduction; no tolerance "
                          "anywhere and no floating point in any decided quantity",
            "randomness": "none: corpora are enumerated in full, merges are learned by a deterministic frequency rule "
                          "with lexicographic tie-break, and the remint is a declared permutation",
            "capability_rule": "the hindsight-optimal FUNCTION of the token multiset (plurality within each feature "
                               "class). This is the parent-maximal bag-of-tokens reader (protocol rule 19): no reader "
                               "of that feature map, linear or not, can beat it.",
            "charged_serve": "one charged operation per token served; the constant-answer control reads no developed "
                             "state and is charged nothing",
        },
        "protocol_rules_carried": {"rule_19": "the capability of every row is the PARENT-MAXIMAL reader of its feature "
                                              "map, not a convenient linear one; the linear question is reported "
                                              "separately as linear_system_consistent",
                                   "rule_21": C.RULE_21, "rule_22": C.RULE_22, "rule_28": C.RULE_28, "rule_29": C.RULE_29},
        "pre_freeze_calibration_disclosed_in_full": [
            "A calibration run was executed BEFORE the clauses were frozen, on a row set consisting of the BPE merge "
            "ladder alone, with admissibility defined as consistency of the exact LINEAR bag-of-tokens system. It "
            "showed (a) that no row of the ladder is linearly consistent on MORPH2 or MORPH3, so that definition left "
            "those two ecologies with an EMPTY admissible set and an empty frontier, and (b) that the frequency-learned "
            "merge table crosses unit boundaries even once it contains every unit as a merge.",
            "Three changes were made in consequence, all before the freeze: (i) admissibility was moved to the "
            "PARENT-MAXIMAL reader of the feature map (the best function of the token multiset, protocol rule 19) "
            "rather than the convenient linear one, with linear realizability reported separately; (ii) the declared "
            "unit-aligned arm ORACLE_UNIT was added, so that vocabulary SIZE and merge-table ALIGNMENT are separable "
            "axes; (iii) the reader's own description was CHARGED (stage B0.3 metering hostility), because a row that "
            "is exact only as a table over feature classes would otherwise hide that table in the tokenizer's "
            "embedding count.",
            "The calibration also fixed the numbers behind the predicted verdicts recorded in RV-377-090: the "
            "character-level capabilities (1, 3/8, 3/8), the minimal exact vocabulary sizes (8, 16, 16) and the "
            "mem1_len1 occupant sets. Clause C17 is frozen although the calibration already indicated it FAILS on "
            "MORPH2, because the clause states a quantitative claim worth committing either way.",
        ],
        "dg2_audit": {
            "auditor": "gmi_microscope/grid_audit.py family C, driven by gmi_microscope/b2_audit.py",
            "run_before_commit": True,
            "verdict_recorded_in": "microscopes/results/STAGE_B2_DG2_AUDIT_V1.json",
            "what_the_auditor_does_here": "it recomputes this receipt's own frontier from this receipt's own per-row "
                                          "cost coordinates, cell for cell (the soundness gate), and then checks "
                                          "whether the occupant is constant for every H beyond the grid maximum",
        },
        "dg2_procedure": "every crossover of every price vector is computed FIRST in exact rationals (b2_common."
                         "crossovers), the reuse grid is then built to bracket each one and reach 4x the largest "
                         "(grid_for), and check_dg2 asserts max(grid) >= 2*max(crossover) per context; the per-row "
                         "cost coordinates (A, E) are carried in the receipt so the grid is auditable from its own "
                         "contents (protocol rule 28). gmi_microscope/grid_audit.py was run over this receipt before "
                         "it was committed; see dg2_audit above.",
        "cells": cells,
        "b2_frontiers": b2_frontiers,
        "b2_frontier_schema": C.FRONTIER_SCHEMA,
        "frontier_note": FRONTIER_NOTE_TEXT,
        "shared_reuse_grid_H": shared_grid,
        "optimal_vocabulary_size_by_cell_price_horizon": optima,
        "claims": {k: bool(v) for k, v in clauses.items()},
        "n_claims_hold": sum(bool(v) for v in clauses.values()), "n_claims": len(clauses),
        "status": "GREEN" if all(clauses.values()) else "RED",
        "claim_level": "EMPIRICALLY_SUPPORTED_AT_TIER_S",
        "claim_ceiling": "a measured tokenizer/morphology/price tradeoff on three declared synthetic corpora of 512 "
                         "enumerated strings each, under one declared BPE merge rule, one bag-of-tokens reader class "
                         "and four declared price vectors. It establishes NOTHING about any real tokenizer, any real "
                         "corpus or any trained neural network, and the 'no universal optimum' clause is a statement "
                         "about THESE three morphologies and THESE four price vectors, not a theorem over all of them.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_01_TOKENIZER_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    for m, c in r["cells"].items():
        print("\n%s  units=%d chars, corpus=%d, constant control=%s, minimal exact V=%s" % (
            m, c["unit_length"], c["corpus_strings"], c["rule22_constant_control"]["capability"],
            c["minimal_exact_vocabulary_size"]))
        for name, row in sorted(c["rows"].items()):
            print("   %-18s V=%2d n_tok=%-9s cap=%-9s aligned=%-9s linN=%-5s lookN=%-4s remint=%-9s exact=%s" % (
                name, row["vocabulary_size_V"], row["mean_tokens_per_string"],
                row["hindsight_optimal_bag_reader_capability"], row["unit_aligned_segmentation_fraction"],
                row["linear_sample_efficiency_examples"], row["lookup_sample_efficiency_examples"],
                row["remint_hindsight_optimal_capability"], row["exact"]))
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])
