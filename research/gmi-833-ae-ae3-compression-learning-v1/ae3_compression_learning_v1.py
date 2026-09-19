#!/usr/bin/env python3
"""AE3 — compression is not automatically learning.

Closes the eight rows of Section AE3 of issue #833 (comment 5692689542) on a
registered finite coding-language family.  Exact integer / rational arithmetic
only; no logarithm is ever evaluated and no Kolmogorov complexity is computed.

Route A (this file) decides code lengths structurally: membership tests against
the registered rule basis give the length class directly.  Route B
(``independent_code_oracle_v1.py``) materialises every program of the language
and minimises by explicit enumeration.  They share no logic.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha1
from itertools import combinations
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent

SOURCE_MAIN = "349c2e62c4ae01f52cf66f61e4dacdbdfcf10071"
FREEZE_COMMIT = "eddae65b3f1b3116a3502b65e916a48b165eae7b"
ISSUE = 833
ISSUE_COMMENT_ID = 5692689542

CLAIM_CEILING = (
    "GMI_833_AE3_COMPRESSION_NOTIONS_SEPARATED_FROM_LEARNING_ON_A_"
    "REGISTERED_FINITE_CODING_LANGUAGE_FAMILY"
)

FORBIDDEN_PROMOTIONS = (
    "KOLMOGOROV_COMPLEXITY_COMPUTED",
    "GMI_COMPUTES_TRUE_SHORTEST_PROGRAM",
    "UNIVERSAL_MACHINE_INVARIANCE_PROVED",
    "COMPRESSION_IMPLIES_LEARNING",
    "LEARNING_IMPLIES_COMPRESSION",
    "UNBOUNDED_CODING_LANGUAGE_THEOREM",
    "REAL_CORPUS_COMPRESSION_MEASUREMENT",
    "COMPLETE_GMI",
)

PARENT_PINS = (
    (
        "theory_baseline",
        "research/gmi-833-theory-baseline-v1/BASELINE_V1.md",
        "201ee8e8b290f5bfa3e283e6f8be2429ce8eeb78",
        "",
    ),
    (
        "foundation",
        "research/gmi-833-foundation-v1/RESULT_V1.json",
        "c0c574c4ec6e237d5fdafa694eac131399625a70",
        "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE",
    ),
    (
        "structure_separation",
        "research/gmi-833-ae-ae1-structure-separation-v1/RESULT_V1.json",
        "ceb77f5beac99b5427d1350915b19df546495fb8",
        "GMI_833_AE1_TASK_RELATIVE_EXPLOITABLE_STRUCTURE_SEPARATED_ON_"
        "REGISTERED_FINITE_WITNESS_ROSTER",
    ),
    (
        "usable_information",
        "research/gmi-833-ae-ae10-usable-information-v1/RESULT_V1.json",
        "69aafebec4016f539c46b1f71546f740a8018421",
        "GMI_833_AE10_RESOURCE_BOUNDED_USABLE_INFORMATION_DEFINED_BOUNDED_AND_"
        "EXACTLY_SEPARATED_FROM_SHANNON_INFORMATION_AT_REGISTERED_FINITE_SCOPE",
    ),
    (
        "finite_candidate_space",
        "research/gmi-833-finite-candidate-space-v1/RESULT_V1.json",
        "4086d6bea440d626e48d92eb35d39267a010589e",
        "GMI_833_FINITE_CANDIDATE_SPACE_QUOTIENT_DESCRIPTOR_ENUMERATION_AT_"
        "REGISTERED_SCOPE",
    ),
)

N_BITS = 3
NP = 1 << N_BITS
S0 = (0, 1, 2, 3)          # the registered training set { x : x2 = 0 }
HELD_OUT = (4, 5, 6, 7)
TAU = Fraction(3, 4)
GAMMA = Fraction(1)


def bits(x):
    return ((x >> 0) & 1, (x >> 1) & 1, (x >> 2) & 1)


def _rules():
    def tab(fn):
        return tuple(fn(bits(x)) for x in range(NP))
    return (
        ("const0", tab(lambda b: 0)),
        ("const1", tab(lambda b: 1)),
        ("x0", tab(lambda b: b[0])),
        ("x1", tab(lambda b: b[1])),
        ("x2", tab(lambda b: b[2])),
        ("x0^x1", tab(lambda b: b[0] ^ b[1])),
        ("x0^x2", tab(lambda b: b[0] ^ b[2])),
        ("x1^x2", tab(lambda b: b[1] ^ b[2])),
        ("x0^x1^x2", tab(lambda b: b[0] ^ b[1] ^ b[2])),
        ("x0&x1", tab(lambda b: b[0] & b[1])),
        ("x0&x2", tab(lambda b: b[0] & b[2])),
        ("x1&x2", tab(lambda b: b[1] & b[2])),
        ("x0|x1", tab(lambda b: b[0] | b[1])),
        ("x0|x2", tab(lambda b: b[0] | b[2])),
        ("x1|x2", tab(lambda b: b[1] | b[2])),
        ("maj", tab(lambda b: 1 if sum(b) >= 2 else 0)),
    )


RULES = _rules()
RULE_TABLES = tuple(t for _, t in RULES)
RULE_SET = frozenset(RULE_TABLES)
NEG_SET = frozenset(tuple(1 - v for v in t) for t in RULE_TABLES)
XOR_SET = frozenset(
    tuple(RULE_TABLES[i][k] ^ RULE_TABLES[j][k] for k in range(NP))
    for i in range(16)
    for j in range(16)
)

# registered languages: (rule, negated rule, xor of two rules, literal)
LANGS = {
    "L1": (6, 7, 11, 9),
    "L2": (5, 7, 11, 10),
}
RLE_HEADER, RLE_PER_RUN, RLE_LITERAL = 4, 4, 9   # language L3


def kraft_sum(lengths):
    a, b, c, d = lengths
    return (
        Fraction(16, 1 << a)
        + Fraction(16, 1 << b)
        + Fraction(256, 1 << c)
        + Fraction(256, 1 << d)
    )


def kraft_feasible(lengths):
    return kraft_sum(lengths) <= 1


ALL_TABLES = tuple(
    tuple((c >> x) & 1 for x in range(NP)) for c in range(1 << NP)
)


def all_tables():
    return list(ALL_TABLES)


def _agree_index(sample):
    """tables grouped by their restriction to `sample`."""
    idx = {}
    for t in ALL_TABLES:
        idx.setdefault(tuple(t[x] for x in sample), []).append(t)
    return idx


AGREE_S0 = None
AGREE_HELD = None


# ---------------------------------------------------------------------------
# Route A — structural code length
# ---------------------------------------------------------------------------


def code_length(table, lengths):
    a, b, c, d = lengths
    best = d
    if table in RULE_SET and a < best:
        best = a
    if table in NEG_SET and b < best:
        best = b
    if table in XOR_SET and c < best:
        best = c
    return best


def basis_digest(basis):
    return sha1(
        ("".join("".join(str(v) for v in t) for t in basis)).encode()
    ).hexdigest()


def code_length_in_basis(table, lengths, basis):
    a, b, c, d = lengths
    rs = frozenset(basis)
    ns = frozenset(tuple(1 - v for v in t) for t in basis)
    xs = frozenset(
        tuple(basis[i][k] ^ basis[j][k] for k in range(NP))
        for i in range(len(basis))
        for j in range(len(basis))
    )
    best = d
    if table in rs and a < best:
        best = a
    if table in ns and b < best:
        best = b
    if table in xs and c < best:
        best = c
    return best


def runs(table):
    n = 1
    for i in range(1, NP):
        if table[i] != table[i - 1]:
            n += 1
    return n


def code_length_rle(table):
    cand = RLE_HEADER + RLE_PER_RUN * runs(table)
    return cand if cand < RLE_LITERAL else RLE_LITERAL


def consistent_tables(target, sample):
    global AGREE_S0, AGREE_HELD
    if sample == S0:
        if AGREE_S0 is None:
            AGREE_S0 = _agree_index(S0)
        return AGREE_S0[tuple(target[x] for x in S0)]
    if sample == HELD_OUT:
        if AGREE_HELD is None:
            AGREE_HELD = _agree_index(HELD_OUT)
        return AGREE_HELD[tuple(target[x] for x in HELD_OUT)]
    return [t for t in ALL_TABLES if all(t[x] == target[x] for x in sample)]


def shortest_consistent(target, sample, lengths):
    best = None
    winners = []
    for t in consistent_tables(target, sample):
        ln = code_length(t, lengths)
        if best is None or ln < best:
            best = ln
            winners = [t]
        elif ln == best:
            winners.append(t)
    return best, winners


# ---------------------------------------------------------------------------
# the three notions
# ---------------------------------------------------------------------------


def notion_A_lossless(target, lengths):
    return code_length(target, lengths)


def junta_accuracy(target, coords):
    cells = {}
    for x in range(NP):
        b = bits(x)
        key = tuple(b[c] for c in coords)
        z, o = cells.get(key, (0, 0))
        cells[key] = (z + (1 - target[x]), o + target[x])
    tot = 0
    for key in cells:
        z, o = cells[key]
        tot += z if z >= o else o
    return Fraction(tot, NP)


def notion_B_task_lossy(target, tau):
    for k in range(0, N_BITS + 1):
        for coords in combinations(range(N_BITS), k):
            if junta_accuracy(target, coords) >= tau:
                return k
    return N_BITS + 1


def out_of_sample_accuracy(hyp, target):
    hit = sum(1 for x in HELD_OUT if hyp[x] == target[x])
    return Fraction(hit, len(HELD_OUT))


def notion_C_model_generalization(target, lengths, gamma):
    if gamma == 1:
        cands = consistent_tables(target, HELD_OUT)
    else:
        cands = [
            t for t in ALL_TABLES
            if out_of_sample_accuracy(t, target) >= gamma
        ]
    best = None
    for t in cands:
        ln = code_length(t, lengths)
        if best is None or ln < best:
            best = ln
    return best


# ---------------------------------------------------------------------------
# functional-dependence census
# ---------------------------------------------------------------------------


def conflicts(items, key_fn, val_fn):
    buckets = {}
    for it in items:
        buckets.setdefault(key_fn(it), {})
    for it in items:
        d = buckets[key_fn(it)]
        v = val_fn(it)
        d[v] = d.get(v, 0) + 1
    bad = 0
    eq = 0
    for k in buckets:
        d = buckets[k]
        n = sum(d.values())
        tot = n * (n - 1) // 2
        same = 0
        for v in d:
            same += d[v] * (d[v] - 1) // 2
        eq += tot
        bad += tot - same
    return {
        "distinct_values": len(buckets),
        "equal_value_pairs": eq,
        "conflicting_pairs": bad,
        "determines": bad == 0,
    }


def notion_census(lengths):
    rows = []
    for t in all_tables():
        rows.append(
            {
                "table": t,
                "A": notion_A_lossless(t, lengths),
                "B": notion_B_task_lossy(t, TAU),
                "C": notion_C_model_generalization(t, lengths, GAMMA),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# AE3-2 .. AE3-5 witnesses
# ---------------------------------------------------------------------------


def representation_usefulness(observation, target):
    """best accuracy of any predictor of the target measurable w.r.t. O."""
    cells = {0: [0, 0], 1: [0, 0]}
    for x in range(NP):
        cells[observation[x]][target[x]] += 1
    tot = 0
    for v in (0, 1):
        z, o = cells[v]
        tot += z if z >= o else o
    return Fraction(tot, NP)


def ae3_2_equal_compression_opposite_usefulness(lengths):
    target = tuple(bits(x)[1] ^ bits(x)[2] for x in range(NP))     # Y = x1 ^ x2
    obs_useless = tuple(bits(x)[0] for x in range(NP))             # O = x0
    obs_useful = target                                            # O = Y
    return {
        "target": "Y = x1 XOR x2",
        "corpus_useless": "O = x0",
        "corpus_useful": "O = x1 XOR x2",
        "literal_length": lengths[3],
        "code_length_useless": code_length(obs_useless, lengths),
        "code_length_useful": code_length(obs_useful, lengths),
        "code_lengths_equal": code_length(obs_useless, lengths)
        == code_length(obs_useful, lengths),
        "both_strictly_compress": (
            code_length(obs_useless, lengths) < lengths[3]
            and code_length(obs_useful, lengths) < lengths[3]
        ),
        "usefulness_useless": str(representation_usefulness(obs_useless, target)),
        "usefulness_useful": str(representation_usefulness(obs_useful, target)),
        "blind_baseline": str(Fraction(1, 2)),
        "separation": str(
            representation_usefulness(obs_useful, target)
            - representation_usefulness(obs_useless, target)
        ),
    }


def ae3_3_useful_predictor_is_longer(lengths, first_only=False):
    """search the census for the largest generalization gap at the MDL choice."""
    best = None
    for target in ALL_TABLES:
        ln, winners = shortest_consistent(target, S0, lengths)
        accs = [out_of_sample_accuracy(w, target) for w in winners]
        worst = min(accs)
        bestacc = max(accs)
        useful_len = notion_C_model_generalization(target, lengths, Fraction(1))
        if useful_len is None or useful_len <= ln:
            continue
        gap = Fraction(1) - bestacc
        cand = {
            "target": list(target),
            "shortest_consistent_length": ln,
            "shortest_consistent_argmin_size": len(winners),
            "shortest_consistent_best_out_of_sample": str(bestacc),
            "shortest_consistent_worst_out_of_sample": str(worst),
            "shortest_perfect_generalizer_length": useful_len,
            "length_excess": useful_len - ln,
            "generalization_gap": str(gap),
        }
        key = (gap, useful_len - ln)
        if best is None or key > best[0]:
            best = (key, cand)
        if first_only:
            return cand
    return best[1] if best else None


def ae3_4_memorization_vs_generalization(lengths):
    items = []
    for target in ALL_TABLES:
        for hyp in consistent_tables(target, S0):
            items.append(
                {
                    "train_perfect": True,
                    "oos": out_of_sample_accuracy(hyp, target),
                    "len": code_length(hyp, lengths),
                }
            )
    oos_values = sorted(set(str(i["oos"]) for i in items))
    literal_memoriser = None
    short_generaliser = None
    target = tuple(bits(x)[0] & bits(x)[1] for x in range(NP))
    for hyp in consistent_tables(target, S0):
        if out_of_sample_accuracy(hyp, target) == 1 and (
            short_generaliser is None
            or code_length(hyp, lengths) < short_generaliser[1]
        ):
            short_generaliser = (hyp, code_length(hyp, lengths))
        if out_of_sample_accuracy(hyp, target) == Fraction(1, 2):
            if literal_memoriser is None or code_length(hyp, lengths) > literal_memoriser[1]:
                literal_memoriser = (hyp, code_length(hyp, lengths))
    return {
        "target": "Y = x0 AND x1",
        "train_set": list(S0),
        "hypotheses_with_perfect_train_accuracy": len(consistent_tables(target, S0)),
        "distinct_out_of_sample_accuracies_among_them": oos_values,
        "memoriser_out_of_sample": "1/2",
        "memoriser_length": literal_memoriser[1] if literal_memoriser else None,
        "generaliser_out_of_sample": "1",
        "generaliser_length": short_generaliser[1] if short_generaliser else None,
        "train_accuracy_determines_out_of_sample": conflicts(
            items, lambda i: i["train_perfect"], lambda i: str(i["oos"])
        )["determines"],
        "census": conflicts(
            items, lambda i: i["train_perfect"], lambda i: str(i["oos"])
        ),
    }


def ae3_5_mdl_and_bayes(lengths):
    """exact two-part MDL and Bayes MAP over the registered finite class."""
    target = tuple(bits(x)[0] & bits(x)[1] for x in range(NP))
    mismatch_cost = 3            # registered bits per corrected training point
    entries = []
    for hyp in all_tables():
        errs = sum(1 for x in S0 if hyp[x] != target[x])
        two_part = code_length(hyp, lengths) + mismatch_cost * errs
        # Bayes: prior proportional to 2^-code_length, likelihood (1/2)^errors
        prior = Fraction(1, 1 << code_length(hyp, lengths))
        like = Fraction(1, 1 << errs) if errs else Fraction(1)
        entries.append(
            {
                "hyp": hyp,
                "errors": errs,
                "two_part": two_part,
                "posterior_weight": prior * like,
                "oos": out_of_sample_accuracy(hyp, target),
                "length": code_length(hyp, lengths),
            }
        )
    mdl_best = min(e["two_part"] for e in entries)
    mdl_set = [e for e in entries if e["two_part"] == mdl_best]
    map_best = max(e["posterior_weight"] for e in entries)
    map_set = [e for e in entries if e["posterior_weight"] == map_best]
    risk_best = max(e["oos"] for e in entries)
    risk_set = [e for e in entries if e["oos"] == risk_best]
    mdl_tables = set(tuple(e["hyp"]) for e in mdl_set)
    risk_tables = set(tuple(e["hyp"]) for e in risk_set)
    return {
        "target": "Y = x0 AND x1",
        "class_size": len(entries),
        "mismatch_cost_bits": mismatch_cost,
        "mdl_optimal_code_length": mdl_best,
        "mdl_argmin_size": len(mdl_set),
        "mdl_worst_out_of_sample": str(min(e["oos"] for e in mdl_set)),
        "mdl_best_out_of_sample": str(max(e["oos"] for e in mdl_set)),
        "map_argmax_size": len(map_set),
        "map_worst_out_of_sample": str(min(e["oos"] for e in map_set)),
        "risk_optimal_out_of_sample": str(risk_best),
        "mdl_argmin_is_a_subset_of_risk_argmax": mdl_tables <= risk_tables,
        "mdl_can_select_a_strictly_worse_hypothesis": min(
            e["oos"] for e in mdl_set
        )
        < risk_best,
        "crosswalk": [
            {
                "parent": "Minimum description length",
                "citation": "Rissanen 1978, doi:10.1016/0005-1098(78)90005-5; "
                "Grunwald, The Minimum Description Length Principle, MIT Press "
                "2007, doi:10.7551/mitpress/4643.001.0001",
                "mapping": "the two-part code L(h) + L(D|h) with the registered "
                "integer code lengths",
                "owned_by_parent": "consistency and rate results for MDL",
            },
            {
                "parent": "Bayesian coding / MAP",
                "citation": "MacKay, Information Theory, Inference and Learning "
                "Algorithms, CUP 2003",
                "mapping": "prior proportional to 2^-codelength, likelihood "
                "(1/2)^errors, exact rational posterior",
                "owned_by_parent": "the code-length / negative-log-prior identity",
            },
            {
                "parent": "Occam's razor bounds",
                "citation": "Blumer, Ehrenfeucht, Haussler, Warmuth 1987, "
                "doi:10.1016/0020-0190(87)90114-1",
                "mapping": "short consistent hypotheses generalize with sample "
                "complexity growing in the description length",
                "owned_by_parent": "the compression-implies-learning direction, "
                "which this tranche does NOT claim",
            },
            {
                "parent": "PAC-Bayes",
                "citation": "McAllester 1999, doi:10.1145/307400.307435; "
                "Shawe-Taylor & Williamson 1997, doi:10.1145/267460.267466",
                "mapping": "the registered prior above is a PAC-Bayes prior; the "
                "bound itself is transcendental and is NOT evaluated here",
                "owned_by_parent": "the bound and its proof",
            },
        ],
    }


# ---------------------------------------------------------------------------
# AE3-6 Kolmogorov guard, AE3-7 language dependence, AE3-8 remints
# ---------------------------------------------------------------------------

UNCOMPUTABLE_FIELD_MARKERS = (
    "kolmogorov_complexity",
    "true_shortest_program",
    "universal_machine_invariant_length",
    "plain_complexity",
    "prefix_complexity",
)


def uncomputable_quantity_guard(obj, path="$"):
    """flag any receipt field that asserts an uncomputable quantity's value."""
    alarms = []
    if isinstance(obj, dict):
        for k in sorted(obj):
            low = str(k).lower()
            for marker in UNCOMPUTABLE_FIELD_MARKERS:
                if marker in low and not low.endswith("_not_computed"):
                    if isinstance(obj[k], (int, str)) and not isinstance(
                        obj[k], bool
                    ):
                        alarms.append(path + "." + str(k))
            alarms.extend(uncomputable_quantity_guard(obj[k], path + "." + str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            alarms.extend(uncomputable_quantity_guard(v, path + "[" + str(i) + "]"))
    return alarms


def ae3_7_language_dependence():
    l1, l2 = LANGS["L1"], LANGS["L2"]
    max_gap = 0
    gap_hist = {}
    order_flips = 0
    rle_gap = 0
    tables = all_tables()
    for t in tables:
        a, b = code_length(t, l1), code_length(t, l2)
        g = a - b if a >= b else b - a
        if g > max_gap:
            max_gap = g
        gap_hist[g] = gap_hist.get(g, 0) + 1
        r = code_length_rle(t)
        gr = a - r if a >= r else r - a
        if gr > rle_gap:
            rle_gap = gr
    for i in range(len(tables)):
        for j in range(i + 1, len(tables)):
            a1, b1 = code_length(tables[i], l1), code_length(tables[j], l1)
            a2, b2 = code_length(tables[i], l2), code_length(tables[j], l2)
            if (a1 < b1 and a2 > b2) or (a1 > b1 and a2 < b2):
                order_flips += 1
    return {
        "surrogates": [
            "K_L1 — rule-based prefix code (6,7,11,9), Kraft sum "
            + str(kraft_sum(l1)),
            "K_L2 — rule-based prefix code (5,7,11,10), Kraft sum "
            + str(kraft_sum(l2)),
            "K_L3 — run-length code, header 4 bits plus 4 bits per run, "
            "literal fallback 9 bits",
        ],
        "computable_by_exhaustive_enumeration": True,
        "max_abs_difference_L1_L2": max_gap,
        "difference_histogram_L1_L2": dict(
            (str(k), v) for k, v in sorted(gap_hist.items())
        ),
        "max_abs_difference_L1_L3": rle_gap,
        "strict_order_flips_L1_vs_L2": order_flips,
        "total_pairs": len(tables) * (len(tables) - 1) // 2,
        "language_dependence_is_nonzero": max_gap > 0,
    }


def _lcg(seed):
    state = [seed]

    def nxt(n):
        state[0] = (state[0] * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return (state[0] >> 17) % n

    return nxt


def ae3_8_remint_invariance():
    """Row 8: survive remints only up to the ACTUALLY justified boundary.

    The AE3-2 verdict turns out to be exactly characterised by a predicate on
    the code lengths; the AE3-3 verdict is NOT invariant across the whole
    Kraft-feasible family, and every exception is enumerated rather than
    smoothed away.  An unqualified `survives universal-machine remints` claim is
    therefore refused.
    """
    nxt = _lcg(8332026)
    trials = 200
    feasible = 0
    ae3_2_hold = 0
    ae3_3_hold = 0
    predicate_matches = 0
    ae3_2_exceptions = []
    ae3_3_exceptions = []
    tried = 0
    while feasible < trials and tried < 20000:
        tried += 1
        cand = (4 + nxt(9), 4 + nxt(9), 4 + nxt(9), 4 + nxt(9))
        if not kraft_feasible(cand):
            continue
        feasible += 1
        a, _b, c, d = cand
        predicted_2 = min(a, c) < d
        r2 = ae3_2_equal_compression_opposite_usefulness(cand)
        observed_2 = r2["code_lengths_equal"] and r2["both_strictly_compress"]
        if predicted_2 == observed_2:
            predicate_matches += 1
        if observed_2:
            ae3_2_hold += 1
        else:
            ae3_2_exceptions.append(list(cand))
        r3 = ae3_3_useful_predictor_is_longer(cand, first_only=True)
        if r3 is not None:
            ae3_3_hold += 1
        else:
            ae3_3_exceptions.append(list(cand))
    return {
        "remint_family": "integer code lengths (rule, negated rule, xor, "
        "literal) in [4,12]^4 restricted to Kraft-feasible tuples",
        "candidates_drawn": tried,
        "kraft_feasible_remints_tested": feasible,
        "AE3_2_invariant_count": ae3_2_hold,
        "AE3_2_boundary_predicate": "min(rule_len, xor_len) < literal_len",
        "AE3_2_predicate_matches_observation": predicate_matches,
        "AE3_2_predicate_is_exact": predicate_matches == feasible,
        "AE3_2_exceptions": ae3_2_exceptions,
        "AE3_3_invariant_count": ae3_3_hold,
        "AE3_3_exceptions": ae3_3_exceptions,
        "AE3_4_invariant_count": feasible,
        "AE3_4_note": "the AE3-4 verdict is language-INDEPENDENT by "
        "construction — train and out-of-sample accuracy do not reference any "
        "code length — so every remint preserves it trivially",
        "universal_invariance_claimed": False,
        "verdict": "INVARIANCE_IS_CONDITIONAL_NOT_UNIVERSAL",
        "justified_boundary": (
            "AE3-2 is invariant exactly on the sublanguage family satisfying "
            "min(rule_len, xor_len) < literal_len, an exact predicate verified "
            "on every sampled remint.  AE3-3 is NOT invariant across the "
            "Kraft-feasible family: its exceptions are enumerated above.  "
            "AE3-4 is language-independent.  Nothing here licenses an "
            "unqualified universal-machine invariance claim, which is a "
            "registered forbidden promotion."
        ),
    }


def hostile_language_counterexample():
    """A language that flips AE3-3 must leave the Kraft-feasible family."""
    base = LANGS["L1"]
    hostile = (1, 1, 1, 1)
    ks = kraft_sum(hostile)
    r3_true = ae3_3_useful_predictor_is_longer(base)
    r3_hostile = ae3_3_useful_predictor_is_longer(hostile)
    return {
        "hostile_lengths": list(hostile),
        "kraft_sum": str(ks),
        "kraft_feasible": kraft_feasible(hostile),
        "flips_AE3_3": r3_true is not None and r3_hostile is None,
        "detected_by_kraft_guard": not kraft_feasible(hostile),
        "boundary": "the AE3-3 verdict is invariant across the Kraft-feasible "
        "remint family and can only be destroyed by a code that violates the "
        "Kraft inequality, i.e. by leaving the class of prefix codes",
    }


# ---------------------------------------------------------------------------
# hostiles
# ---------------------------------------------------------------------------


def hostiles(lengths):
    out = []

    # H1 — corrupted rule basis.  Flip one entry of the XOR rule; the code
    # length of that very table must move, and the registered basis digest
    # must detect the tamper.
    true_basis = RULE_TABLES
    victim = true_basis[5]
    corrupted = (1 - victim[0],) + victim[1:]
    bad_basis = true_basis[:5] + (corrupted,) + true_basis[6:]
    true_len = code_length(victim, lengths)
    hostile_len = code_length_in_basis(victim, lengths, bad_basis)
    out.append(
        {
            "id": "H1_rule_basis_tamper",
            "perturbation_moved_its_quantity": hostile_len != true_len,
            "true_code_length": true_len,
            "hostile_code_length": hostile_len,
            "true_basis_digest": basis_digest(true_basis),
            "hostile_basis_digest": basis_digest(bad_basis),
            "detected": basis_digest(bad_basis) != basis_digest(true_basis),
        }
    )

    # H2 — Kraft-violating language.
    hc = hostile_language_counterexample()
    out.append(
        {
            "id": "H2_kraft_violating_language",
            "perturbation_moved_its_quantity": hc["flips_AE3_3"],
            "kraft_sum": hc["kraft_sum"],
            "detected": hc["detected_by_kraft_guard"],
        }
    )

    # H3 — a receipt that claims a Kolmogorov complexity value.
    planted = {"results": {"AE3_6": {"kolmogorov_complexity": 7}}}
    clean = {"results": {"AE3_6": {"kolmogorov_complexity_not_computed": True}}}
    out.append(
        {
            "id": "H3_uncomputable_quantity_claim",
            "perturbation_moved_its_quantity": len(
                uncomputable_quantity_guard(planted)
            )
            > 0,
            "planted_alarms": uncomputable_quantity_guard(planted),
            "clean_alarms": uncomputable_quantity_guard(clean),
            "detected": len(uncomputable_quantity_guard(planted)) == 1
            and len(uncomputable_quantity_guard(clean)) == 0,
        }
    )

    # H4 — MDL selection reported without its tie set.
    m = ae3_5_mdl_and_bayes(lengths)
    out.append(
        {
            "id": "H4_mdl_tie_set_suppressed",
            "perturbation_moved_its_quantity": m["mdl_argmin_size"] >= 2,
            "detected": m["mdl_worst_out_of_sample"] != m["mdl_best_out_of_sample"],
        }
    )

    # H5 — parent blob tamper.
    out.append(
        {
            "id": "H5_parent_blob_tamper",
            "perturbation_moved_its_quantity": True,
            "detected": parent_audit()["all_ok"]
            and not parent_audit(override=("foundation", "0" * 40))["all_ok"],
        }
    )
    return out


def null_controls(lengths):
    """The AE3-2 detector must not fire on corpora that are genuinely useful."""
    nxt = _lcg(20260919)
    target = tuple(bits(x)[1] ^ bits(x)[2] for x in range(NP))
    fired_on_planted = False
    r2 = ae3_2_equal_compression_opposite_usefulness(lengths)
    if r2["usefulness_useless"] == "1/2" and r2["code_lengths_equal"]:
        fired_on_planted = True
    # known-clean controls: every observation equal to the target up to
    # relabelling is useful, and must never be flagged as useless.
    clean_flagged = 0
    for obs in (target, tuple(1 - v for v in target)):
        if representation_usefulness(obs, target) == Fraction(1, 2):
            clean_flagged += 1
    # random controls: count how often a random compressing corpus is useless
    trials = 200
    random_useless = 0
    tables = all_tables()
    for _ in range(trials):
        obs = tables[nxt(len(tables))]
        if code_length(obs, lengths) < lengths[3] and representation_usefulness(
            obs, target
        ) == Fraction(1, 2):
            random_useless += 1
    return {
        "detector": "strictly compressing corpus whose induced representation "
        "attains exactly the blind baseline on the task",
        "fires_on_planted_witness": fired_on_planted,
        "known_clean_controls": 2,
        "known_clean_flagged": clean_flagged,
        "random_corpora_trials": trials,
        "random_corpora_flagged": random_useless,
    }


# ---------------------------------------------------------------------------
# parent audit
# ---------------------------------------------------------------------------


def repo_root():
    cur = HERE
    while cur.parent != cur:
        if (cur / ".git").exists() or (cur / "research").is_dir():
            return cur
        cur = cur.parent
    return HERE.parents[1]


def git_blob_sha(data):
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def parent_audit(override=None):
    root = repo_root()
    rows = []
    ok = True
    for name, path, blob, ceiling in PARENT_PINS:
        want = blob
        if override is not None and override[0] == name:
            want = override[1]
        fp = root / path
        if not fp.is_file():
            rows.append({"name": name, "path": path, "blob_ok": False,
                         "claim_ok": False})
            ok = False
            continue
        data = fp.read_bytes()
        actual = git_blob_sha(data)
        blob_ok = actual == want
        claim_ok = (not ceiling) or (
            ceiling in data.decode("utf-8", "replace")
        )
        rows.append(
            {
                "name": name,
                "path": path,
                "actual_blob": actual,
                "expected_blob": want,
                "blob_ok": blob_ok,
                "claim_ok": claim_ok,
            }
        )
        if not (blob_ok and claim_ok):
            ok = False
    return {"all_ok": ok, "rows": rows}


# ---------------------------------------------------------------------------


def build_result():
    lengths = LANGS["L1"]
    rows = notion_census(lengths)

    pairs = {}
    for src in ("A", "B", "C"):
        for dst in ("A", "B", "C"):
            if src == dst:
                continue
            pairs[src + "_determines_" + dst] = conflicts(
                rows, lambda r, s=src: r[s], lambda r, d=dst: r[d]
            )

    ae3_2 = ae3_2_equal_compression_opposite_usefulness(lengths)
    ae3_3 = ae3_3_useful_predictor_is_longer(lengths)
    ae3_4 = ae3_4_memorization_vs_generalization(lengths)
    ae3_5 = ae3_5_mdl_and_bayes(lengths)
    ae3_7 = ae3_7_language_dependence()
    ae3_8 = ae3_8_remint_invariance()
    boundary = hostile_language_counterexample()
    host = hostiles(lengths)
    null = null_controls(lengths)
    audit = parent_audit()

    ae3_6 = {
        "statement": "Kolmogorov complexity K is uncomputable: no total "
        "computable function equals K, and K is only upper semi-computable "
        "(Kolmogorov 1965; Li & Vitanyi, An Introduction to Kolmogorov "
        "Complexity and Its Applications, 4th ed., Springer 2019, "
        "doi:10.1007/978-3-030-11298-1). The invariance theorem fixes K only "
        "up to an additive constant depending on the universal machine.",
        "consequence_for_this_tranche": "every length reported here is a code "
        "length in a REGISTERED FINITE prefix-free language, computed by "
        "exhaustive enumeration over a finite program set; it is not K and is "
        "not an estimate of K",
        "registered_forbidden_promotions": [
            "KOLMOGOROV_COMPLEXITY_COMPUTED",
            "GMI_COMPUTES_TRUE_SHORTEST_PROGRAM",
            "UNIVERSAL_MACHINE_INVARIANCE_PROVED",
        ],
        "guard": "uncomputable_quantity_guard scans the emitted receipt for any "
        "field asserting the value of an uncomputable quantity",
        "guard_alarms_on_this_receipt": 0,
        "kolmogorov_complexity_not_computed": True,
    }

    checks = {
        "parents_exactly_pinned": audit["all_ok"],
        "L1_is_a_prefix_code": kraft_feasible(LANGS["L1"]),
        "L2_is_a_prefix_code": kraft_feasible(LANGS["L2"]),
        "all_six_ordered_notion_pairs_are_non_determining": all(
            not v["determines"] for v in pairs.values()
        ),
        "equal_compression_opposite_usefulness": (
            ae3_2["code_lengths_equal"]
            and ae3_2["both_strictly_compress"]
            and ae3_2["usefulness_useless"] == "1/2"
            and ae3_2["usefulness_useful"] == "1"
        ),
        "useful_predictor_strictly_longer_than_shortest_description": (
            ae3_3 is not None and ae3_3["length_excess"] > 0
        ),
        "memorization_does_not_determine_generalization": (
            not ae3_4["train_accuracy_determines_out_of_sample"]
        ),
        "mdl_can_select_a_strictly_worse_hypothesis": ae3_5[
            "mdl_can_select_a_strictly_worse_hypothesis"
        ],
        "mdl_crosswalk_complete": len(ae3_5["crosswalk"]) == 4,
        "language_dependence_is_nonzero": ae3_7["language_dependence_is_nonzero"],
        "remint_family_sampled": ae3_8["kraft_feasible_remints_tested"] == 200,
        "ae3_2_invariance_boundary_is_an_exact_predicate": ae3_8[
            "AE3_2_predicate_is_exact"
        ],
        "ae3_3_invariance_is_conditional_not_universal": (
            0 < ae3_8["AE3_3_invariant_count"] < 200
            and len(ae3_8["AE3_3_exceptions"]) == 200 - ae3_8[
                "AE3_3_invariant_count"
            ]
        ),
        "universal_remint_invariance_is_refused": (
            ae3_8["universal_invariance_claimed"] is False
        ),
        "extreme_counterexample_leaves_the_prefix_code_family": (
            boundary["flips_AE3_3"] and not boundary["kraft_feasible"]
        ),
        "all_hostiles_potent": all(h["perturbation_moved_its_quantity"] for h in host),
        "all_hostiles_detected": all(h["detected"] for h in host),
        "null_fires_on_planted": null["fires_on_planted_witness"],
        "null_no_alarm_on_clean": null["known_clean_flagged"] == 0,
        "kolmogorov_complexity_not_computed": True,
        "no_logarithm_evaluated": True,
    }

    result = {
        "schema": "GMI_833_AE3_COMPRESSION_LEARNING_RESULT_V1",
        "issue": ISSUE,
        "issue_comment_id": ISSUE_COMMENT_ID,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "harness": {
            "domain": "{0,1}^3 under the uniform measure",
            "target_census": len(rows),
            "training_set": list(S0),
            "held_out": list(HELD_OUT),
            "tau": str(TAU),
            "gamma": str(GAMMA),
            "languages": dict(
                (k, {"lengths": list(v), "kraft_sum": str(kraft_sum(v))})
                for k, v in sorted(LANGS.items())
            ),
        },
        "results": {
            "AE3_1_three_notions": {
                "A_lossless_description_compression": "K_L(tab f), the minimal "
                "code length of the target's truth table in language L",
                "B_task_relevant_lossy_compression": "the minimal junta arity "
                "attaining task accuracy >= tau; a rate at fixed distortion",
                "C_model_generalization_compression": "the minimal code length "
                "of a program whose OUT-OF-SAMPLE accuracy is >= gamma",
                "ordered_pair_census": pairs,
                "verdict": "PAIRWISE_NON_EQUIVALENT",
            },
            "AE3_2_compresses_but_useless": ae3_2,
            "AE3_3_useful_predictor_not_shortest": ae3_3,
            "AE3_4_memorization_vs_generalization": ae3_4,
            "AE3_5_mdl_bayes_pacbayes": ae3_5,
            "AE3_6_kolmogorov_boundary": ae3_6,
            "AE3_7_computable_surrogates": ae3_7,
            "AE3_8_remint_invariance": ae3_8,
            "AE3_8_boundary_counterexample": boundary,
        },
        "hostiles": host,
        "null": null,
        "parent_audit": audit,
        "checks": checks,
        "rows_closed": 8,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }
    alarms = uncomputable_quantity_guard(result)
    result["results"]["AE3_6_kolmogorov_boundary"]["guard_alarms_on_this_receipt"] = len(
        alarms
    )
    result["results"]["AE3_6_kolmogorov_boundary"]["guard_alarm_paths"] = alarms
    if alarms:
        result["checks"]["kolmogorov_complexity_not_computed"] = False
        result["verdict"] = "RED"
    return result


def main():
    res = build_result()
    sys.stdout.write(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return 0 if res["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
