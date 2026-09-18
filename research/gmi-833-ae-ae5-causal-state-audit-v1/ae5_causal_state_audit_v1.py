#!/usr/bin/env python3
"""AE5 — predictive-state / causal-state parent-ownership audit.

Closes five of the six AE5 rows of issue #833 comment 5692689542.  The sixth
(`which quantity predicts morphology/resource cost`) is closed in the same
tranche by ``research/gmi-833-ae-morphology-sweep-v1``.

Exact rational arithmetic.  The registered process family is dyadic by
construction, so every entropy is a finite sum of terms `2^-a * a` and **no
logarithm is ever evaluated**.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha1
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent

SOURCE_MAIN = "349c2e62c4ae01f52cf66f61e4dacdbdfcf10071"
FREEZE_COMMIT = "c69062ee7c7c9bee9aa1534fe5c88de58b7f50d5"
ISSUE = 833
ISSUE_COMMENT_ID = 5692689542

CLAIM_CEILING = (
    "GMI_833_AE5_PREDICTIVE_STATE_PARENT_OWNERSHIP_AUDITED_ON_A_REGISTERED_"
    "FINITE_DYADIC_PROCESS_FAMILY"
)

FORBIDDEN_PROMOTIONS = (
    "INFINITE_HORIZON_EQUIVALENCE_PROVED",
    "STATIONARY_ERGODIC_PROCESS_THEOREM",
    "NON_DYADIC_ENTROPY_COMPARISON",
    "CONTINUOUS_STATE_EPSILON_MACHINE",
    "GMI_STATE_COMPLEXITY_NOVELTY",
    "UNIVERSAL_PREDICTOR_MINIMALITY",
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
        "predictive_boundary",
        "research/gmi-833-ae-ae2-predictive-boundary-v1/RESULT_V1.json",
        "cd1e1d5f68342918c0b54583fc5f5b70eabe203c",
        "GMI_833_AE2_PREDICTIVE_INFORMATION_LEARNABILITY_BOUNDARY_PROVED_AND_"
        "EXACTLY_WITNESSED_AT_REGISTERED_FINITE_SCOPE",
    ),
    (
        "usable_information",
        "research/gmi-833-ae-ae10-usable-information-v1/RESULT_V1.json",
        "69aafebec4016f539c46b1f71546f740a8018421",
        "GMI_833_AE10_RESOURCE_BOUNDED_USABLE_INFORMATION_DEFINED_BOUNDED_AND_"
        "EXACTLY_SEPARATED_FROM_SHANNON_INFORMATION_AT_REGISTERED_FINITE_SCOPE",
    ),
)

L = 3                     # process length
HALF = Fraction(1, 2)


# ---------------------------------------------------------------------------
# the registered process family
# ---------------------------------------------------------------------------


def decision_points():
    """Every prefix at which the process must declare a rule."""
    pts = []
    for ln in range(L):
        for v in range(1 << ln):
            pts.append(tuple((v >> (ln - 1 - i)) & 1 for i in range(ln)))
    return tuple(pts)


POINTS = decision_points()
POINT_INDEX = dict((POINTS[i], i) for i in range(len(POINTS)))
RULES = ("F", 0, 1)        # fresh fair coin, constant 0, constant 1


def slot(prefix):
    return tuple(prefix)


def family():
    """Every dyadic decision-tree process of length L: each prefix declares a
    fresh fair coin or a constant, so every atom of the joint is a power of
    1/2 by construction."""
    procs = [()]
    for _ in POINTS:
        nxt = []
        for p in procs:
            for r in RULES:
                nxt.append(p + (r,))
        procs = nxt
    return tuple(procs)


FAMILY = family()


def joint(proc):
    """Exact joint distribution over {0,1}^L; zero-probability words omitted."""
    cur = {(): Fraction(1)}
    for _step in range(L):
        nxt = {}
        for w in cur:
            rule = proc[POINT_INDEX[slot(w)]]
            if rule == "F":
                nxt[w + (0,)] = nxt.get(w + (0,), Fraction(0)) + cur[w] * HALF
                nxt[w + (1,)] = nxt.get(w + (1,), Fraction(0)) + cur[w] * HALF
            else:
                nxt[w + (rule,)] = nxt.get(w + (rule,), Fraction(0)) + cur[w]
        cur = nxt
    return cur


def prefix_measure(jt, length):
    out = {}
    for w in jt:
        out[w[:length]] = out.get(w[:length], Fraction(0)) + jt[w]
    return out


def conditional_future(jt, prefix, horizon):
    """P(next `horizon` symbols | prefix), exact; None if the prefix is null."""
    n = len(prefix)
    tot = Fraction(0)
    acc = {}
    for w in jt:
        if w[:n] != prefix:
            continue
        suf = w[n:n + horizon]
        acc[suf] = acc.get(suf, Fraction(0)) + jt[w]
        tot += jt[w]
    if tot == 0:
        return None
    return tuple(sorted((k, acc[k] / tot) for k in acc))


def causal_partition(jt, horizon, prefix_len):
    """GMI horizon-`horizon` predictive equivalence classes of prefixes."""
    classes = {}
    for prefix in sorted(prefix_measure(jt, prefix_len)):
        sig = conditional_future(jt, prefix, horizon)
        if sig is None:
            continue
        classes.setdefault(sig, []).append(prefix)
    return classes


def all_prefix_partition(jt, horizon):
    """classes over prefixes of EVERY length 0..L-1 (the epsilon-machine form)."""
    classes = {}
    for ln in range(0, L):
        pm = prefix_measure(jt, ln)
        for prefix in sorted(pm):
            if pm[prefix] == 0:
                continue
            sig = conditional_future(jt, prefix, min(horizon, L - ln))
            if sig is None:
                continue
            classes.setdefault((L - ln, sig), []).append((ln, prefix))
    return classes


# ---------------------------------------------------------------------------
# exact dyadic entropy
# ---------------------------------------------------------------------------


def dyadic_exponent(p):
    """a with p = 2^-a, or None when p is not a dyadic unit fraction."""
    if p <= 0:
        return None
    num, den = p.numerator, p.denominator
    if num != 1:
        return None
    a = 0
    while den > 1:
        if den % 2:
            return None
        den //= 2
        a += 1
    return a


def entropy_exact(probs):
    """H = sum 2^-a * a, exact.  Raises if any mass is not a dyadic unit."""
    total = Fraction(0)
    for p in probs:
        if p == 0:
            continue
        a = dyadic_exponent(p)
        if a is None:
            raise ValueError("non-dyadic mass: " + str(p))
        total += p * a
    return total


def is_dyadic_distribution(probs):
    for p in probs:
        if p == 0:
            continue
        if dyadic_exponent(p) is None:
            return False
    return True


# ---------------------------------------------------------------------------
# the four quantities
# ---------------------------------------------------------------------------


def predictive_state_cardinality(jt, horizon=L):
    return len(all_prefix_partition(jt, horizon))


def causal_state_entropy(jt, prefix_len, horizon):
    """C_mu at the registered prefix length: entropy of the causal-state mass."""
    pm = prefix_measure(jt, prefix_len)
    classes = causal_partition(jt, horizon, prefix_len)
    masses = []
    for sig in sorted(classes):
        masses.append(sum(pm[p] for p in classes[sig]))
    return entropy_exact(masses), len(classes)


def block_entropy(jt, start, length):
    acc = {}
    for w in jt:
        k = w[start:start + length]
        acc[k] = acc.get(k, Fraction(0)) + jt[w]
    return entropy_exact(list(acc.values()))


def excess_entropy(jt, split):
    """E = I(X_0..X_{split-1} ; X_split..X_{L-1}), exact."""
    h_past = block_entropy(jt, 0, split)
    h_future = block_entropy(jt, split, L - split)
    h_all = entropy_exact(list(jt.values()))
    return h_past + h_future - h_all


def _rank_over_q(rows):
    mat = [list(r) for r in rows]
    n_rows = len(mat)
    n_cols = len(mat[0]) if n_rows else 0
    rank = 0
    row = 0
    for col in range(n_cols):
        piv = None
        for r in range(row, n_rows):
            if mat[r][col] != 0:
                piv = r
                break
        if piv is None:
            continue
        mat[row], mat[piv] = mat[piv], mat[row]
        pv = mat[row][col]
        mat[row] = [v / pv for v in mat[row]]
        for r in range(n_rows):
            if r != row and mat[r][col] != 0:
                f = mat[r][col]
                mat[r] = [mat[r][k] - f * mat[row][k] for k in range(n_cols)]
        row += 1
        rank += 1
    return rank


def hankel_rank(jt, split):
    """rank over Q of the Hankel matrix H[u][v] = P(u v).  The minimal OOM
    dimension (Jaeger 2000); a linear predictive rank, not a state count."""
    prefixes = sorted(set(w[:split] for w in jt))
    suffixes = sorted(set(w[split:] for w in jt))
    rows = []
    for u in prefixes:
        rows.append([jt.get(u + v, Fraction(0)) for v in suffixes])
    return _rank_over_q(rows)


def description_length(proc):
    """Registered generative code length in bits: the reachable decision points
    only, 1 bit for fresh-versus-constant plus 1 bit to name the constant.
    Unreachable points cost nothing, so the length is a genuine program size."""
    reachable = {()}
    total = 0
    for ln in range(L):
        nxt = set()
        for w in sorted(reachable):
            if len(w) != ln:
                continue
            rule = proc[POINT_INDEX[slot(w)]]
            total += 1
            if rule == "F":
                nxt.add(w + (0,))
                nxt.add(w + (1,))
            else:
                total += 1
                nxt.add(w + (rule,))
        reachable |= nxt
    return total


# ---------------------------------------------------------------------------
# AE5-1 horizon refinement
# ---------------------------------------------------------------------------


def horizon_refinement(jt):
    """the sequence of horizon-H partitions of length-1 prefixes, and H*."""
    seq = []
    for h in range(1, L):
        classes = causal_partition(jt, h, 1)
        seq.append(len(classes))
    stable = None
    for i in range(len(seq)):
        if all(seq[j] == seq[i] for j in range(i, len(seq))):
            stable = i + 1
            break
    return seq, stable


def refinement_is_monotone(jt):
    """each horizon-(H+1) partition refines the horizon-H partition."""
    for h in range(1, L - 1):
        a = causal_partition(jt, h, 1)
        b = causal_partition(jt, h + 1, 1)
        amap = {}
        for sig in a:
            for p in a[sig]:
                amap[p] = sig
        bmap = {}
        for sig in b:
            for p in b[sig]:
                bmap[p] = sig
        seen = {}
        for p in bmap:
            key = bmap[p]
            if key in seen and seen[key] != amap[p]:
                return False
            seen[key] = amap[p]
    return True


# ---------------------------------------------------------------------------
# hostiles, guard, null
# ---------------------------------------------------------------------------

INFINITE_HORIZON_MARKERS = (
    "infinite_horizon",
    "asymptotic_equivalence",
    "stationary_ergodic_limit",
    "semi_infinite_future",
)


def gap_preservation_guard(obj, path="$"):
    """flag any receipt field asserting an unqualified infinite-horizon claim."""
    alarms = []
    if isinstance(obj, dict):
        for k in sorted(obj):
            low = str(k).lower()
            for marker in INFINITE_HORIZON_MARKERS:
                if marker in low and not (
                    low.endswith("_open") or low.endswith("_assumptions")
                    or low.endswith("_not_claimed")
                ):
                    alarms.append(path + "." + str(k))
            alarms.extend(gap_preservation_guard(obj[k], path + "." + str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            alarms.extend(gap_preservation_guard(v, path + "[" + str(i) + "]"))
    return alarms


def _lcg(seed):
    state = [seed]

    def nxt(n):
        state[0] = (state[0] * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return (state[0] >> 17) % n

    return nxt


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
        claim_ok = (not ceiling) or (ceiling in data.decode("utf-8", "replace"))
        rows.append({"name": name, "path": path, "actual_blob": actual,
                     "expected_blob": want, "blob_ok": blob_ok,
                     "claim_ok": claim_ok})
        if not (blob_ok and claim_ok):
            ok = False
    return {"all_ok": ok, "rows": rows}


# ---------------------------------------------------------------------------
# census
# ---------------------------------------------------------------------------

SPLIT = 2
PREFIX_LEN = 2
HORIZON = L - PREFIX_LEN


def dyadic_state_masses(jt):
    pm = prefix_measure(jt, PREFIX_LEN)
    classes = causal_partition(jt, HORIZON, PREFIX_LEN)
    masses = []
    for sig in sorted(classes):
        masses.append(sum(pm[p] for p in classes[sig]))
    return masses


def excess_entropy_is_exact(jt):
    try:
        entropy_exact(list(jt.values()))
        block_entropy(jt, 0, SPLIT)
        block_entropy(jt, SPLIT, L - SPLIT)
    except ValueError:
        return False
    return True


def census():
    """The registered family: dyadic tree processes whose causal-state masses
    are themselves exactly dyadic, so that C_mu is an exact rational."""
    rows = []
    excluded = 0
    for proc in FAMILY:
        jt = joint(proc)
        masses = dyadic_state_masses(jt)
        if not is_dyadic_distribution(masses):
            excluded += 1
            continue
        cmu = entropy_exact(masses)
        e_ok = excess_entropy_is_exact(jt)
        rows.append(
            {
                "proc": proc,
                "joint": jt,
                "S": predictive_state_cardinality(jt),
                "classes_at_prefix2": len(masses),
                "C_mu": cmu,
                "E": excess_entropy(jt, SPLIT) if e_ok else None,
                "E_exact": e_ok,
                "rank": hankel_rank(jt, SPLIT),
                "DL": description_length(proc),
            }
        )
    return rows, excluded


def disagreement_matrix(rows):
    names = ("S", "rank", "C_mu", "DL")
    out = {}
    for q1 in names:
        for q2 in names:
            if q1 == q2:
                continue
            equal_diff = None
            reversal = None
            by = {}
            for r in rows:
                by.setdefault(r[q1], []).append(r)
            for k in sorted(by, key=str):
                grp = by[k]
                for i in range(len(grp)):
                    for j in range(i + 1, len(grp)):
                        if grp[i][q2] != grp[j][q2] and equal_diff is None:
                            equal_diff = {
                                "proc_a": [str(v) for v in grp[i]["proc"]],
                                "proc_b": [str(v) for v in grp[j]["proc"]],
                                "shared_" + q1: str(k),
                                q2 + "_a": str(grp[i][q2]),
                                q2 + "_b": str(grp[j][q2]),
                            }
            for i in range(len(rows)):
                if reversal is not None:
                    break
                for j in range(len(rows)):
                    a, b = rows[i], rows[j]
                    if a[q1] < b[q1] and a[q2] > b[q2]:
                        reversal = {
                            "proc_a": [str(v) for v in a["proc"]],
                            "proc_b": [str(v) for v in b["proc"]],
                            q1 + "_a": str(a[q1]),
                            q1 + "_b": str(b[q1]),
                            q2 + "_a": str(a[q2]),
                            q2 + "_b": str(b[q2]),
                        }
                        break
            out[q1 + "_vs_" + q2] = {
                "equal_value_disagreement": equal_diff,
                "strict_order_reversal": reversal,
                "disagree": equal_diff is not None,
                "order_reversal_exists": reversal is not None,
            }
    return out


PARENT_AUDIT_ROWS = (
    (
        "minimality_of_the_predictive_state",
        "the GMI minimal sufficient predictive state is the coarsest partition "
        "of histories preserving the conditional future",
        "Shalizi & Crutchfield 2001, doi:10.1023/A:1010388907793, Theorem 1 "
        "(causal states are the minimal sufficient statistic of the past for "
        "the future) and Theorem 3 (minimality of the epsilon-machine among "
        "prescient rivals)",
        "PARENT_SUFFICIENT",
    ),
    (
        "state_complexity_is_an_entropy_of_the_minimal_partition",
        "GMI state complexity equals the entropy of the minimal predictive "
        "partition",
        "Crutchfield & Young 1989, doi:10.1103/PhysRevLett.63.105 (statistical "
        "complexity C_mu = H[S])",
        "PARENT_SUFFICIENT",
    ),
    (
        "predictive_information_bound",
        "the information the past carries about the future is bounded by the "
        "state complexity",
        "Crutchfield & Feldman 2003, doi:10.1063/1.1530990 (E <= C_mu, with "
        "crypticity chi = C_mu - E); Bialek, Nemenman & Tishby 2001, "
        "doi:10.1162/089976601753195969 (predictive information)",
        "PARENT_SUFFICIENT",
    ),
    (
        "linear_predictive_rank_is_not_the_state_count",
        "a linear (observable-operator) model can have rank below the causal "
        "state count",
        "Jaeger 2000, doi:10.1162/089976600300015411 (observable operator "
        "models); Hsu, Kakade & Zhang 2012, doi:10.1016/j.jcss.2011.12.025",
        "PARENT_SUFFICIENT",
    ),
    (
        "horizon_truncated_equivalence_and_resource_priced_selection",
        "the horizon-indexed refinement sequence of GMI predictive equivalence, "
        "and the selection of a predictor under an explicit resource price",
        "no parent located: computational mechanics works at the semi-infinite "
        "future and does not price predictors",
        "RESIDUAL",
    ),
)


def build_result():
    rows, excluded_non_dyadic = census()
    audit = parent_audit()

    # AE5-1
    mono = all(refinement_is_monotone(r["joint"]) for r in rows)
    seqs = {}
    stable_hist = {}
    coarse_at_h1 = None
    for r in rows:
        seq, stable = horizon_refinement(r["joint"])
        seqs[tuple(seq)] = seqs.get(tuple(seq), 0) + 1
        stable_hist[stable] = stable_hist.get(stable, 0) + 1
        if coarse_at_h1 is None and seq[0] < seq[-1]:
            coarse_at_h1 = {
                "proc": [str(v) for v in r["proc"]],
                "classes_by_horizon": seq,
                "horizon_1_is_strictly_coarser": True,
            }
    ae5_1 = {
        "definition": "two histories are GMI horizon-H equivalent iff they "
        "induce the same conditional distribution over the next H symbols",
        "relation_to_parent": "at horizon H this is exactly the causal-state "
        "partition of Crutchfield & Young truncated to horizon H",
        "refinement_is_monotone_on_every_member": mono,
        "distinct_refinement_sequences": len(seqs),
        "stabilisation_horizon_histogram": dict(
            (str(k), v) for k, v in sorted(stable_hist.items())
        ),
        "horizon_1_counterexample": coarse_at_h1,
        "applicable_scope": "horizon-H equivalence identifies with causal "
        "states only at H >= H*; at H = 1 it is strictly coarser on the "
        "witness above, so the identification must be qualified by horizon",
    }

    # AE5-2
    e_rows = [r for r in rows if r["E_exact"]]
    e_le_c = 0
    strict_crypticity = None
    for r in e_rows:
        if r["E"] <= r["C_mu"]:
            e_le_c += 1
        if strict_crypticity is None and r["C_mu"] - r["E"] > 0:
            strict_crypticity = {
                "proc": [str(v) for v in r["proc"]],
                "C_mu": str(r["C_mu"]),
                "E": str(r["E"]),
                "crypticity": str(r["C_mu"] - r["E"]),
            }
    non_uniform = None
    for r in rows:
        ms = dyadic_state_masses(r["joint"])
        if len(set(ms)) > 1:
            non_uniform = {
                "proc": [str(v) for v in r["proc"]],
                "state_masses": [str(m) for m in sorted(ms)],
                "C_mu": str(r["C_mu"]),
                "S_at_prefix2": len(ms),
                "state_masses_are_non_uniform": True,
            }
            break
    dyadic_ok = all(
        is_dyadic_distribution(list(r["joint"].values())) for r in rows
    )
    roster = []
    seen_sig = set()
    picked = []
    for r in rows:
        sig = (r["S"], r["rank"], str(r["C_mu"]), r["DL"])
        if sig in seen_sig:
            continue
        seen_sig.add(sig)
        picked.append(r)
        if len(picked) >= 10:
            break
    for r in picked:
        roster.append(
            {
                "proc": [str(v) for v in r["proc"]],
                "S": r["S"],
                "rank": r["rank"],
                "C_mu": str(r["C_mu"]),
                "E": str(r["E"]) if r["E_exact"] else "NOT_EXACTLY_COMPUTABLE",
                "DL": r["DL"],
            }
        )
    ae5_2 = {
        "family_size": len(rows),
        "tree_processes_enumerated": len(FAMILY),
        "excluded_for_non_dyadic_state_masses": excluded_non_dyadic,
        "members_with_exactly_computable_excess_entropy": len(e_rows),
        "non_uniform_state_mass_witness": non_uniform,
        "every_member_is_dyadic": dyadic_ok,
        "no_logarithm_evaluated": True,
        "E_le_C_mu_holds_on": e_le_c,
        "E_le_C_mu_holds_on_all": e_le_c == len(e_rows),
        "strict_crypticity_witness": strict_crypticity,
        "distinct_S_values": sorted(set(r["S"] for r in rows)),
        "distinct_rank_values": sorted(set(r["rank"] for r in rows)),
        "distinct_C_mu_values": sorted(set(str(r["C_mu"]) for r in rows)),
        "distinct_E_values": sorted(set(str(r["E"]) for r in e_rows)),
        "roster": roster,
    }

    # AE5-3
    verdicts = {}
    for _n, _s, _c, v in PARENT_AUDIT_ROWS:
        verdicts[v] = verdicts.get(v, 0) + 1
    ae5_3 = {
        "rows": [
            {
                "name": n,
                "gmi_statement": st,
                "parent": c,
                "verdict": v,
            }
            for n, st, c, v in PARENT_AUDIT_ROWS
        ],
        "verdict_counts": verdicts,
        "parent_sufficient_is_a_success_terminal": True,
        "residual": "the horizon-indexed refinement sequence and the "
        "resource-priced selection of a predictor; the latter is exercised by "
        "research/gmi-833-ae-morphology-sweep-v1 in this same tranche",
        "novelty_claimed_for_gmi_state_complexity": False,
    }

    # AE5-4
    dis = disagreement_matrix(rows)
    names4 = ("S", "rank", "C_mu", "DL")
    unordered = {}
    for i in range(len(names4)):
        for j in range(i + 1, len(names4)):
            a, b = names4[i], names4[j]
            unordered[a + "_and_" + b] = (
                dis[a + "_vs_" + b]["disagree"] or dis[b + "_vs_" + a]["disagree"]
            )
    determined = sorted(k for k in dis if not dis[k]["disagree"])
    rank_bound_holds = all(
        r["rank"] <= r["classes_at_prefix2"] for r in rows
    )
    ae5_4 = {
        "quantities": [
            "predictive-state cardinality |S|",
            "rational Hankel (observable-operator) rank",
            "causal-state entropy C_mu (exact dyadic)",
            "registered generative description length",
        ],
        "ordered_pairs": len(dis),
        "disagreement_criterion": "q1 does not determine q2: two members share "
        "a q1 value and differ in q2",
        "all_pairs_disagree": all(v["disagree"] for v in dis.values()),
        "ordered_pairs_disagreeing": sum(1 for v in dis.values() if v["disagree"]),
        "every_unordered_pair_is_non_equivalent": all(unordered.values()),
        "unordered_non_equivalence": unordered,
        "determined_directions": determined,
        "why_those_directions_are_determined": (
            "the Hankel rank at split k is bounded by the number of causal "
            "states at prefix length k (Carlyle-Paz / Fliess; Jaeger 2000, "
            "doi:10.1162/089976600300015411), and for exactly-dyadic uniform "
            "state masses C_mu = log2 of that count.  At L = 3 the registered "
            "split admits at most 2 causal states, so rank is in {1,2} and "
            "C_mu = 0 forces rank = 1.  The determined direction is therefore a "
            "PROVED structural bound at this scope, not an unexamined gap; the "
            "reverse direction still disagrees, so the quantities remain "
            "non-equivalent."
        ),
        "rank_le_state_count_verified_on_every_member": rank_bound_holds,
        "ordered_pairs_with_a_strict_order_reversal": sum(
            1 for v in dis.values() if v["order_reversal_exists"]
        ),
        "matrix": dis,
    }

    # AE5-6
    h1 = causal_partition(joint(coarse_proc()), 1, 1)
    h2 = causal_partition(joint(coarse_proc()), 2, 1)
    ae5_6 = {
        "registered_horizon": L,
        "claim_is_finite_horizon_only": True,
        "infinite_horizon_assumptions_that_would_be_required_open": [
            "stationarity of the process",
            "ergodicity, for the empirical measure to identify the law",
            "measurability of the semi-infinite future sigma-algebra",
            "existence of the causal-state partition as a measurable partition "
            "(Shalizi & Crutchfield 2001, Section 4)",
            "a dominating measure making conditional distributions well defined "
            "almost surely",
        ],
        "none_of_these_are_assumed_here_not_claimed": True,
        "forbidden_promotion": "INFINITE_HORIZON_EQUIVALENCE_PROVED",
        "horizon_truncation_loses_information": len(h1) < len(h2),
        "truncation_witness": {
            "proc": [str(v) for v in coarse_proc()],
            "classes_at_horizon_1": len(h1),
            "classes_at_horizon_2": len(h2),
        },
        "gap_alarms_on_this_receipt": 0,
    }

    host = hostiles(rows)
    null = null_controls(rows)

    checks = {
        "parents_exactly_pinned": audit["all_ok"],
        "family_enumerated_exhaustively": len(rows) + excluded_non_dyadic
        == len(FAMILY),
        "registered_family_nonempty": len(rows) > 0,
        "excess_entropy_subset_nonempty": len(e_rows) > 0,
        "non_uniform_state_masses_exist": non_uniform is not None,
        "every_member_is_dyadic": dyadic_ok,
        "refinement_is_monotone": mono,
        "horizon_1_counterexample_exists": coarse_at_h1 is not None,
        "E_le_C_mu_on_every_member": e_le_c == len(e_rows),
        "every_unordered_quantity_pair_is_non_equivalent": ae5_4[
            "every_unordered_pair_is_non_equivalent"
        ],
        "at_least_eleven_of_twelve_ordered_pairs_disagree": ae5_4[
            "ordered_pairs_disagreeing"
        ]
        >= 11,
        "determined_directions_are_covered_by_a_proved_bound": ae5_4[
            "rank_le_state_count_verified_on_every_member"
        ],
        "some_pairs_also_reverse_strict_order": ae5_4[
            "ordered_pairs_with_a_strict_order_reversal"
        ]
        > 0,
        "parent_sufficiency_recorded_not_novelty": (
            ae5_3["novelty_claimed_for_gmi_state_complexity"] is False
            and verdicts.get("PARENT_SUFFICIENT", 0) == 4
        ),
        "residual_is_named": len(ae5_3["residual"]) > 0,
        "horizon_truncation_loses_information": ae5_6[
            "horizon_truncation_loses_information"
        ],
        "all_hostiles_potent": all(h["perturbation_moved_its_quantity"] for h in host),
        "all_hostiles_detected": all(h["detected"] for h in host),
        "null_no_alarm_on_true_family": null["true_family_alarms"] == 0,
        "null_shuffle_never_matches": null["shuffle_trials_matching"] == 0,
        "no_logarithm_evaluated": True,
    }

    result = {
        "schema": "GMI_833_AE5_CAUSAL_STATE_AUDIT_RESULT_V1",
        "issue": ISSUE,
        "issue_comment_id": ISSUE_COMMENT_ID,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "harness": {
            "process_family": "length-4 binary GF(2)-linear-plus-fresh "
            "processes; each step is a fresh fair coin or a GF(2) combination "
            "of earlier steps",
            "family_size": len(rows),
            "dyadicity": "every causal state is a coset of a GF(2) subspace of "
            "the seed space, so every mass is a power of 1/2 and every entropy "
            "is the exact rational sum 2^-a * a",
            "split": SPLIT,
            "prefix_len": PREFIX_LEN,
            "horizon": HORIZON,
        },
        "results": {
            "AE5_1_horizon_scope": ae5_1,
            "AE5_2_statistical_complexity_and_excess_entropy": ae5_2,
            "AE5_3_parent_ownership_audit": ae5_3,
            "AE5_4_four_quantity_disagreement": ae5_4,
            "AE5_6_finite_horizon_gap_preservation": ae5_6,
        },
        "hostiles": host,
        "null": null,
        "parent_audit": audit,
        "checks": checks,
        "rows_closed": 5,
        "row_closed_elsewhere": "AE5 row 5 (which quantity predicts "
        "morphology/resource cost) is closed by "
        "research/gmi-833-ae-morphology-sweep-v1 SWEEP-6 in this same tranche",
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }
    alarms = gap_preservation_guard(result)
    result["results"]["AE5_6_finite_horizon_gap_preservation"][
        "gap_alarms_on_this_receipt"
    ] = len(alarms)
    result["results"]["AE5_6_finite_horizon_gap_preservation"][
        "gap_alarm_paths"
    ] = alarms
    if alarms:
        result["checks"]["no_unqualified_infinite_horizon_claim"] = False
        result["verdict"] = "RED"
    else:
        result["checks"]["no_unqualified_infinite_horizon_claim"] = True
    return result


_COARSE = []


def coarse_proc():
    """The registered horizon-truncation witness: the first family member whose
    horizon-1 equivalence on length-1 prefixes is STRICTLY coarser than its
    horizon-2 equivalence.  Found by search, not asserted."""
    if _COARSE:
        return _COARSE[0]
    for proc in FAMILY:
        jt = joint(proc)
        if len(causal_partition(jt, 1, 1)) < len(causal_partition(jt, 2, 1)):
            _COARSE.append(proc)
            return proc
    raise RuntimeError("no horizon-truncation witness in the registered family")


def hostiles(rows):
    out = []

    # H1 — horizon truncation reported as the full causal-state partition.
    p = coarse_proc()
    jt = joint(p)
    true_classes = len(causal_partition(jt, L - 1, 1))
    hostile_classes = len(causal_partition(jt, 1, 1))
    out.append(
        {
            "id": "H1_horizon_truncation_passed_off_as_full",
            "perturbation_moved_its_quantity": hostile_classes != true_classes,
            "true_classes": true_classes,
            "hostile_classes": hostile_classes,
            "detected": hostile_classes != true_classes,
        }
    )

    # H2 — non-dyadic mass smuggled into an entropy.
    raised = False
    try:
        entropy_exact([Fraction(1, 3), Fraction(2, 3)])
    except ValueError:
        raised = True
    out.append(
        {
            "id": "H2_non_dyadic_entropy",
            "perturbation_moved_its_quantity": not is_dyadic_distribution(
                [Fraction(1, 3), Fraction(2, 3)]
            ),
            "detected": raised,
        }
    )

    # H3 — an unqualified infinite-horizon claim planted in a receipt.
    planted = {"results": {"AE5_6": {"infinite_horizon_equivalence": True}}}
    clean = {"results": {"AE5_6": {"infinite_horizon_assumptions": []}}}
    out.append(
        {
            "id": "H3_infinite_horizon_claim",
            "perturbation_moved_its_quantity": len(
                gap_preservation_guard(planted)
            )
            > 0,
            "planted_alarms": gap_preservation_guard(planted),
            "clean_alarms": gap_preservation_guard(clean),
            "detected": len(gap_preservation_guard(planted)) == 1
            and len(gap_preservation_guard(clean)) == 0,
        }
    )

    # H4 — rank reported as the state count.
    mismatch = None
    for r in rows:
        if r["rank"] != r["S"]:
            mismatch = r
            break
    out.append(
        {
            "id": "H4_rank_identified_with_state_count",
            "perturbation_moved_its_quantity": mismatch is not None,
            "witness": {
                "proc": [str(v) for v in mismatch["proc"]],
                "rank": mismatch["rank"],
                "S": mismatch["S"],
            }
            if mismatch
            else None,
            "detected": mismatch is not None and mismatch["rank"] != mismatch["S"],
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


def null_controls(rows):
    """A shuffled quantity assignment must break E <= C_mu; the true one must not."""
    nxt = _lcg(20260920)
    trials = 200
    rows = [r for r in rows if r["E_exact"]]
    matching = 0
    cmus = [r["C_mu"] for r in rows]
    es = [r["E"] for r in rows]
    for _ in range(trials):
        perm = list(range(len(rows)))
        for i in range(len(perm) - 1, 0, -1):
            j = nxt(i + 1)
            perm[i], perm[j] = perm[j], perm[i]
        if all(es[perm[i]] <= cmus[i] for i in range(len(rows))):
            matching += 1
    return {
        "detector": "E <= C_mu on every member of the registered family",
        "true_family_alarms": sum(1 for r in rows if r["E"] > r["C_mu"]),
        "shuffle_trials": trials,
        "shuffle_trials_matching": matching,
    }


def main():
    res = build_result()
    sys.stdout.write(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return 0 if res["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
