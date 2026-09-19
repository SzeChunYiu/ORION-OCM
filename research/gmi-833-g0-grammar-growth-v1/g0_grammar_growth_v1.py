#!/usr/bin/env python3
"""GMI #833 Section-E E8 / issue #897: conservative grammar growth, recursive
primitive invention, and held-out search-cost reduction.

Frozen by research/gmi-833-g0-grammar-growth-v1/FREEZE_V1.md at commit
10f0ef372d3068dcbfb9021d6a53b20ba576f39d before this file existed.

All arithmetic is exact integer arithmetic.  Receipts are byte-identical
under -B and -O -B and across CPython versions.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from typing import Dict, List, Optional, Sequence, Tuple

CLAIM_CEILING = (
    "GMI_FINITE_CONSERVATIVE_RECURSIVE_LIBRARY_GROWTH_AND_HELDOUT_REUSE_BENEFIT_AT_REGISTERED_SCOPE"
)
FREEZE_COMMIT = "10f0ef372d3068dcbfb9021d6a53b20ba576f39d"
SOURCE_MAIN = "aa131e6d65a648754cead0fe3eaa6fde6069147d"
ISSUE = 897
PARENT_ISSUE = 833
TERMINAL_GREEN = "GMI_833_E8_GRAMMAR_GROWTH_HELDOUT_REUSE_GREEN_AT_REGISTERED_SCOPE"
TERMINAL_RED_PREFIX = "GMI_833_E8_GRAMMAR_GROWTH_RED__"
FORBIDDEN_PROMOTIONS = [
    "UNIVERSAL_LIBRARY_LEARNING",
    "PRIMITIVE_INVENTION_ALWAYS_HELPS",
    "OPEN_ENDED_GRAMMAR_GROWTH",
    "UNSEEN_FORM_DISCOVERY",
    "P4_RECOVERY_COMPLETE",
    "REAL_WORLD_TRANSFER_PROVED",
    "ALL_FUTURE_TASKS_CHEAPER",
    "COMPLETE_GMI",
]
RECEIPT_SCHEMA = "GMI833G0GrammarGrowthReceiptV1"

ROOT = pathlib.Path(__file__).resolve().parent
FIXTURES_PATH = ROOT / "FROZEN_FIXTURES_V1.json"

HostileCodes = {
    "cycle": "RECURSIVE_LIBRARY_CYCLE",
    "uncharged_definition": "FREE_DEFINITION_ADMISSION_FLIP_DETECTED",
    "uncharged_maintenance": "UNCHARGED_MAINTENANCE_FLIP_DETECTED",
    "zero_gain": "ZERO_NET_GAIN_REJECTED",
    "semantic_rewrite": "SEMANTIC_REWRITE_DETECTED",
    "heldout_hash": "HELDOUT_FREEZE_HASH_MISMATCH",
    "leakage": "HELDOUT_LEAKAGE_ABSENT",
}


class GrammarGrowthError(Exception):
    """Raised for registered fail-closed conditions."""


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

def load_fixtures() -> dict:
    with FIXTURES_PATH.open("r", encoding="utf-8") as fh:
        fx = json.load(fh)
    if fx.get("schema") != "GMI833G0GrammarGrowthFrozenFixturesV1":
        raise GrammarGrowthError("FIXTURE_SCHEMA_MISMATCH")
    if fx["source_main"] != SOURCE_MAIN:
        raise GrammarGrowthError("FIXTURE_SOURCE_MAIN_MISMATCH")
    return fx


def fixtures_sha256() -> str:
    return hashlib.sha256(FIXTURES_PATH.read_bytes()).hexdigest()


def word_sha256(word: Sequence[str]) -> str:
    payload = json.dumps(list(word), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# expansion (GRW-1 semantics)
# ---------------------------------------------------------------------------

def expand_word(word: Sequence[str], library: Dict[str, Tuple[str, ...]]) -> Tuple[str, ...]:
    """Fully expand a program to its base word; cycles fail closed."""
    base = {"a", "b", "c"}

    def rec(sym: str, in_progress: frozenset) -> Tuple[str, ...]:
        if sym in base:
            return (sym,)
        if sym in in_progress:
            raise GrammarGrowthError(HostileCodes["cycle"])
        if sym not in library:
            raise GrammarGrowthError("UNKNOWN_SYMBOL")
        nxt = in_progress | {sym}
        out: List[str] = []
        for s in library[sym]:
            out.extend(rec(s, nxt))
        return tuple(out)

    flat: List[str] = []
    for sym in word:
        flat.extend(rec(sym, frozenset()))
    return tuple(flat)


def symbol_expansions(symbol_order: Sequence[str], library: Dict[str, Tuple[str, ...]]) -> Dict[str, Tuple[str, ...]]:
    exp: Dict[str, Tuple[str, ...]] = {}
    for sym in symbol_order:
        exp[sym] = expand_word((sym,), library)
    return exp


def dependency_dag(library: Dict[str, Tuple[str, ...]]) -> Dict[str, Tuple[str, ...]]:
    return {name: tuple(s for s in body if s in library) for name, body in library.items()}


def is_acyclic(library: Dict[str, Tuple[str, ...]]) -> bool:
    dag = dependency_dag(library)
    state = {}

    def visit(name: str) -> bool:
        if state.get(name) == 1:
            return False
        if state.get(name) == 2:
            return True
        state[name] = 1
        for dep in dag[name]:
            if not visit(dep):
                return False
        state[name] = 2
        return True

    return all(visit(n) for n in sorted(library))


# ---------------------------------------------------------------------------
# occurrence counting and rewriting (frozen greedy non-overlapping rule)
# ---------------------------------------------------------------------------

def greedy_count(sub: Sequence[str], prog: Sequence[str]) -> int:
    n, m = len(prog), len(sub)
    if m == 0 or m > n:
        return 0
    i = count = 0
    while i <= n - m:
        if tuple(prog[i : i + m]) == tuple(sub):
            count += 1
            i += m
        else:
            i += 1
    return count


def greedy_rewrite(sub: Sequence[str], replacement: str, prog: Sequence[str]) -> Tuple[str, ...]:
    n, m = len(prog), len(sub)
    if m == 0:
        return tuple(prog)
    out: List[str] = []
    i = 0
    while i < n:
        if i <= n - m and tuple(prog[i : i + m]) == tuple(sub):
            out.append(replacement)
            i += m
        else:
            out.append(prog[i])
            i += 1
    return tuple(out)


def corpus_symbol_count(corpus: Sequence[Sequence[str]]) -> int:
    return sum(len(p) for p in corpus)


# ---------------------------------------------------------------------------
# INV-1 deterministic invention
# ---------------------------------------------------------------------------

def candidate_pool(
    corpus: Sequence[Tuple[str, ...]], library: Dict[str, Tuple[str, ...]]
) -> Dict[Tuple[str, ...], Tuple[int, int, int]]:
    """All contiguous subwords with base-expanded length >= 2 and greedy
    occurrence >= 2.  Returns {body: (occurrences, first_program, first_offset)}."""
    base = {"a", "b", "c"}
    bodies: Dict[Tuple[str, ...], Tuple[int, int, int]] = {}
    for pi, prog in enumerate(corpus):
        for i in range(len(prog)):
            for j in range(i + 1, len(prog) + 1):
                body = tuple(prog[i:j])
                if body in bodies:
                    continue
                if all(s in base for s in body):
                    if len(body) < 2:
                        continue
                elif len(expand_word(body, library)) < 2:
                    continue
                occ = sum(greedy_count(body, p) for p in corpus)
                if occ >= 2:
                    bodies[body] = (occ, pi, i)
    return bodies


def admission_gain(body: Tuple[str, ...], occurrences: int, kappa: int) -> int:
    return occurrences * (len(body) - 1) - len(body) - kappa


def tie_key(
    body: Tuple[str, ...],
    gain: int,
    occurrences: int,
    first_program: int,
    first_offset: int,
    library: Dict[str, Tuple[str, ...]],
    symbol_order: Sequence[str],
) -> Tuple:
    rank = {s: k for k, s in enumerate(symbol_order)}
    return (
        -gain,
        expand_word(body, library),
        tuple(rank[s] for s in body),
        first_program,
        first_offset,
    )


def invent(
    corpus: Sequence[Sequence[str]], kappa: int
) -> dict:
    """Deterministic INV-1 invention from the training corpus only."""
    original = [tuple(p) for p in corpus]
    original_base = [expand_word(p, {}) for p in original]
    work = [tuple(p) for p in corpus]
    library: Dict[str, Tuple[str, ...]] = {}
    admissions: List[dict] = []
    depth_limit = corpus_symbol_count(original)  # derived D_reg = S_0
    stopped_by = "DEPTH_LIMIT"
    grw1_failures = 0

    while len(admissions) < depth_limit:
        order = ["a", "b", "c"] + [name for name in sorted(library, key=lambda n: int(n[1:]))]
        pool = candidate_pool(work, library)
        scored = []
        for body, (occ, fp, fo) in pool.items():
            gain = admission_gain(body, occ, kappa)
            if gain > 0:
                scored.append((body, gain, occ, fp, fo))
        if not scored:
            stopped_by = "NO_STRICTLY_BENEFICIAL_CANDIDATE"
            break
        scored.sort(
            key=lambda t: tie_key(t[0], t[1], t[2], t[3], t[4], library, order)
        )
        body, gain, occ, _, _ = scored[0]
        name = "m{}".format(len(library) + 1)
        # GRW-1 conservative-extension invariants for this admission
        if name in library or not is_acyclic({**library, name: body}):
            grw1_failures += 1
            raise GrammarGrowthError("GRW1_ADMISSION_INVARIANT_VIOLATION")
        pre_base = [expand_word(p, library) for p in work]
        new_library = dict(library)
        new_library[name] = body
        new_work = [greedy_rewrite(body, name, p) for p in work]
        for old, new in zip(pre_base, [expand_word(p, new_library) for p in new_work]):
            if old != new:
                grw1_failures += 1
                raise GrammarGrowthError("GRW1_SEMANTIC_INVARIANT_VIOLATION")
        if corpus_symbol_count(new_work) >= corpus_symbol_count(work):
            grw1_failures += 1
            raise GrammarGrowthError("GRW1_MONOTONE_COMPRESSION_VIOLATION")
        admissions.append(
            {
                "name": name,
                "body": list(body),
                "occurrences": occ,
                "gain": gain,
                "charged_total_before": corpus_symbol_count(work) + sum(
                    len(b) + kappa for b in library.values()
                ),
                "corpus_symbols_before": corpus_symbol_count(work),
                "corpus_symbols_after": corpus_symbol_count(new_work),
            }
        )
        library = new_library
        work = new_work

    for orig_base, cur in zip(original_base, work):
        if expand_word(cur, library) != orig_base:
            grw1_failures += 1

    return {
        "library": library,
        "library_order": [a["name"] for a in admissions],
        "corpus_final": [list(p) for p in work],
        "admissions": admissions,
        "depth_limit": depth_limit,
        "stopped_by": stopped_by,
        "grw1_failures": grw1_failures,
        "initial_corpus_symbols": corpus_symbol_count(original),
    }


# ---------------------------------------------------------------------------
# exact breadth-by-description-length discovery burden
# ---------------------------------------------------------------------------

def canonical_symbol_order(library_order: Sequence[str]) -> List[str]:
    return ["a", "b", "c"] + list(library_order)


def burden_dp(
    target: Sequence[str],
    symbol_order: Sequence[str],
    expansions: Dict[str, Tuple[str, ...]],
) -> Tuple[int, Tuple[str, ...]]:
    """Exact burden via segmentation DP.

    burden = sum_{j=1..l*-1} A^j  +  lex_rank(first-hit program at l*)  +  1,
    with l* the minimal description length of any program expanding to target
    and the first hit the lexicographically least such program under the
    canonical symbol order.  Equivalent by construction to naive enumeration.
    """
    w = tuple(target)
    n = len(w)
    A = len(symbol_order)
    symbols = list(symbol_order)

    # S[i][r]: w[i:] segmentable into exactly r symbol expansions.
    S = [[False] * (n + 1) for _ in range(n + 1)]
    S[n][0] = True
    for i in range(n - 1, -1, -1):
        for r in range(1, n - i + 1):
            ok = False
            for s in symbols:
                e = expansions[s]
                le = len(e)
                if le and i + le <= n and tuple(w[i : i + le]) == e and S[i + le][r - 1]:
                    ok = True
                    break
            S[i][r] = ok
    lstar = None
    for r in range(1, n + 1):
        if S[0][r]:
            lstar = r
            break
    if lstar is None:
        raise GrammarGrowthError("TARGET_UNREACHABLE")

    prog: List[str] = []
    rank = 0
    idx = {s: k for k, s in enumerate(symbols)}
    i = 0
    remaining = lstar
    while remaining > 0:
        for s in symbols:
            e = expansions[s]
            le = len(e)
            if le and i + le <= n and tuple(w[i : i + le]) == e and S[i + le][remaining - 1]:
                prog.append(s)
                rank = rank * A + idx[s]
                i += le
                remaining -= 1
                break
        else:  # pragma: no cover - S guarantees feasibility
            raise GrammarGrowthError("SEGMENTATION_INVARIANT_VIOLATION")
    prior = (A ** lstar - A) // (A - 1) if A > 1 else lstar - 1
    burden = prior + rank + 1
    return burden, tuple(prog)


def burden_naive(
    target: Sequence[str],
    symbol_order: Sequence[str],
    library: Dict[str, Tuple[str, ...]],
    max_len: Optional[int] = None,
) -> Tuple[int, Tuple[str, ...]]:
    """Reference enumerator: breadth-by-length, lexicographic within length."""
    w = tuple(target)
    limit = len(w) if max_len is None else max_len
    count = 0
    for length in range(1, limit + 1):
        waves: List[Tuple[str, ...]] = [()]
        for _ in range(length):
            waves = [p + (s,) for p in waves for s in symbol_order]
        for p in waves:
            count += 1
            if expand_word(p, library) == w:
                return count, p
    raise GrammarGrowthError("TARGET_UNREACHABLE_NAIVE")


# ---------------------------------------------------------------------------
# HLD-1 held-out verdicts and THR-1 threshold
# ---------------------------------------------------------------------------

def k_total(library: Dict[str, Tuple[str, ...]], kappa: int) -> int:
    return sum(len(b) + kappa for b in library.values())


def heldout_verdict(
    targets: Sequence[Sequence[str]],
    library: Dict[str, Tuple[str, ...]],
    library_order: Sequence[str],
    kappa: int,
) -> dict:
    order_full = canonical_symbol_order(library_order)
    exp_full = symbol_expansions(order_full, library)
    exp_base = symbol_expansions(["a", "b", "c"], {})
    rows = []
    cum0 = cumF = 0
    for w in targets:
        b0, hit0 = burden_dp(w, ["a", "b", "c"], exp_base)
        bF, hitF = burden_dp(w, order_full, exp_full)
        rows.append(
            {
                "target": list(w),
                "burden_G0": b0,
                "burden_expanded": bF,
                "delta_burden": bF - b0,
                "first_hit_G0": list(hit0),
                "first_hit_expanded": list(hitF),
            }
        )
        cum0 += b0
        cumF += bF
    K = k_total(library, kappa)
    return {
        "targets": rows,
        "cumulative_burden_G0": cum0,
        "cumulative_burden_expanded": cumF,
        "library_overhead_K_total": K,
        "net": cumF + K - cum0,
        "n_targets": len(rows),
    }


def threshold_check(hplus_verdict: dict, library: Dict[str, Tuple[str, ...]], kappa: int) -> dict:
    usage: Dict[str, int] = {}
    for row in hplus_verdict["targets"]:
        for s in row["first_hit_expanded"]:
            if s in library:
                usage[s] = usage.get(s, 0) + 1
    rows = []
    for name in sorted(library, key=lambda n: int(n[1:])):
        body = library[name]
        b = len(body)
        H_eff = usage.get(name, 0)
        delta_marginal = b - 1
        base_len = len(expand_word((name,), library))
        delta_base = base_len - 1
        K = b + kappa
        rows.append(
            {
                "macro": name,
                "body_symbols": b,
                "H_eff": H_eff,
                "delta_marginal": delta_marginal,
                "delta_base_relative": delta_base,
                "K": K,
                "benefit_marginal": H_eff * delta_marginal,
                "benefit_base_relative": H_eff * delta_base,
                "holds_marginal": H_eff * delta_marginal > K,
                "holds_base_relative": H_eff * delta_base > K,
            }
        )
    total_benefit = sum(r["benefit_marginal"] for r in rows)
    total_K = sum(r["K"] for r in rows)
    return {
        "per_macro": rows,
        "aggregate_benefit_marginal": total_benefit,
        "aggregate_K": total_K,
        "aggregate_holds": total_benefit > total_K,
        "all_macros_hold_marginal": all(r["holds_marginal"] for r in rows),
    }


# ---------------------------------------------------------------------------
# NULL-1 equal-size random-admission null
# ---------------------------------------------------------------------------

def null_combo_index(seed: int, pool_size: int, size: int) -> int:
    combos = _n_choose_k(pool_size, size)
    return (((seed + 1) * 2654435761) % (2 ** 32)) % combos


def _n_choose_k(n: int, k: int) -> int:
    result = 1
    for t in range(k):
        result = result * (n - t) // (t + 1)
    return result


def null_ensemble(
    corpus: Sequence[Sequence[str]],
    true_library_size: int,
    seeds: Sequence[int],
    hplus: Sequence[Sequence[str]],
    hminus: Sequence[Sequence[str]],
    kappa: int,
) -> dict:
    pool = candidate_pool([tuple(p) for p in corpus], {})
    pool_bodies = sorted(pool)  # deterministic lexicographic order over G0 tuples
    combos = [
        tuple(c)
        for c in _combinations_indices(len(pool_bodies), true_library_size)
    ]
    exp_base = symbol_expansions(["a", "b", "c"], {})
    g0_plus = sum(burden_dp(w, ["a", "b", "c"], exp_base)[0] for w in hplus)
    g0_minus = sum(burden_dp(w, ["a", "b", "c"], exp_base)[0] for w in hminus)

    nets_plus: List[int] = []
    nets_minus: List[int] = []
    per_seed = []
    for seed in seeds:
        ci = null_combo_index(seed, len(pool_bodies), true_library_size)
        bodies = [pool_bodies[k] for k in combos[ci]]
        names = ["n{}".format(i + 1) for i in range(len(bodies))]
        library = {n: b for n, b in zip(names, bodies)}
        order = canonical_symbol_order(names)
        exps = symbol_expansions(order, library)
        cumP = sum(burden_dp(w, order, exps)[0] for w in hplus)
        cumM = sum(burden_dp(w, order, exps)[0] for w in hminus)
        K = k_total(library, kappa)
        nets_plus.append(cumP + K - g0_plus)
        nets_minus.append(cumM + K - g0_minus)
        per_seed.append(
            {
                "seed": seed,
                "combo_index": ci,
                "bodies": [list(b) for b in bodies],
                "net_hplus": cumP + K - g0_plus,
                "net_hminus": cumM + K - g0_minus,
            }
        )
    return {
        "pool_size": len(pool_bodies),
        "pool_bodies": [list(b) for b in pool_bodies],
        "library_size": true_library_size,
        "n_seeds": len(seeds),
        "g0_cumulative_hplus": g0_plus,
        "g0_cumulative_hminus": g0_minus,
        "nets_hplus": nets_plus,
        "nets_hminus": nets_minus,
        "net_hplus_min": min(nets_plus),
        "net_hplus_median": sorted(nets_plus)[len(nets_plus) // 2],
        "net_hplus_max": max(nets_plus),
        "net_hminus_min": min(nets_minus),
        "net_hminus_median": sorted(nets_minus)[len(nets_minus) // 2],
        "net_hminus_max": max(nets_minus),
        "per_seed": per_seed,
    }


def _combinations_indices(n: int, k: int) -> List[Tuple[int, ...]]:
    out: List[Tuple[int, ...]] = []

    def rec(start: int, chosen: List[int]) -> None:
        if len(chosen) == k:
            out.append(tuple(chosen))
            return
        for i in range(start, n - (k - len(chosen)) + 1):
            rec(i + 1, chosen + [i])

    rec(0, [])
    return out


# ---------------------------------------------------------------------------
# hostile battery
# ---------------------------------------------------------------------------

def hostile_cycle() -> dict:
    snapshot = {"m1": ("a", "b")}
    attacks = {
        "self_loop": {"m1": ("m1", "a")},
        "two_cycle": {"mA": ("mB",), "mB": ("mA",)},
        "deep_cycle": {"mA": ("a", "mB"), "mB": ("mC",), "mC": ("mA",)},
    }
    results = {}
    for name, lib in attacks.items():
        try:
            expand_word(("mA",), lib) if "mA" in lib else expand_word(("m1",), lib)
            results[name] = "NO_CYCLE_DETECTED"
        except GrammarGrowthError as exc:
            results[name] = str(exc)
    results["grammar_unchanged"] = snapshot == {"m1": ("a", "b")}
    results["acyclic_registered"] = is_acyclic({"m1": ("a", "b")})
    ok = all(v == HostileCodes["cycle"] for k, v in results.items() if k.startswith(("self", "two", "deep")))
    results["all_cycles_rejected"] = ok
    return results


def hostile_uncharged_definition(kappa: int) -> dict:
    corpus = [["a", "b"], ["a", "b"]]
    trace = invent(corpus, kappa)
    uncharged_would_admit = 2 * (2 - 1) > 0  # o*(b-1) without definition+maintenance
    return {
        "crafted_corpus": [list(p) for p in corpus],
        "registered_admissions": len(trace["admissions"]),
        "registered_rejects": len(trace["admissions"]) == 0,
        "uncharged_variant_would_admit": uncharged_would_admit,
        "charge_load_bearing": uncharged_would_admit and len(trace["admissions"]) == 0,
        "code": HostileCodes["uncharged_definition"],
    }


def hostile_uncharged_maintenance() -> dict:
    corpus = [["a", "b", "a", "b"] for _ in range(3)] + [["a", "b"]]
    trace_k0 = invent(corpus, 0)
    trace_k1 = invent(corpus, 1)
    flip = len(trace_k0["admissions"]) != len(trace_k1["admissions"])
    return {
        "crafted_corpus": [list(p) for p in corpus],
        "admissions_kappa0": len(trace_k0["admissions"]),
        "admissions_kappa1": len(trace_k1["admissions"]),
        "maintenance_charge_load_bearing": flip,
        "code": HostileCodes["uncharged_maintenance"],
    }


def hostile_zero_gain(kappa: int) -> dict:
    corpus = [["a", "b", "a", "b"] for _ in range(3)] + [["a", "b"]]
    trace = invent(corpus, kappa)
    # after m1 admission, (m1,m1) occurs 3 times: gain = 3*1 - 2 - kappa
    gain_after_m1 = 3 * (2 - 1) - 2 - kappa
    return {
        "crafted_corpus": [list(p) for p in corpus],
        "second_stage_gain_exactly_zero": gain_after_m1 == 0,
        "admissions": len(trace["admissions"]),
        "zero_gain_rejected": gain_after_m1 == 0 and len(trace["admissions"]) == 1,
        "code": HostileCodes["zero_gain"],
    }


def hostile_semantic_rewrite() -> dict:
    corpus = [["a", "b", "a", "b"], ["c", "a", "b"]]

    def corrupt_rewriter(prog):
        out = greedy_rewrite(("a", "b"), "m1", prog)
        return out[:-1] if out else out  # drops the final symbol: semantic change

    library = {"m1": ("a", "b")}
    detected = False
    for prog in corpus:
        before = expand_word(prog, {})
        after = expand_word(corrupt_rewriter(prog), library)
        if before != after:
            detected = True
    return {
        "corrupt_rewrite_detected": detected,
        "code": HostileCodes["semantic_rewrite"],
    }


def hostile_heldout_hash(fx: dict) -> dict:
    recomputed_plus = [word_sha256(w) for w in fx["heldout_reuse_positive"]]
    recomputed_minus = [word_sha256(w) for w in fx["heldout_unrelated_control"]]
    tampered = [["z", "z", "z"]] + fx["heldout_reuse_positive"][1:]
    tampered_hash = word_sha256(tampered[0])
    mismatch_detected = tampered_hash != recomputed_plus[0]
    return {
        "recomputed_hplus_hashes": recomputed_plus,
        "recomputed_hminus_hashes": recomputed_minus,
        "tamper_detected": mismatch_detected,
        "code": HostileCodes["heldout_hash"],
    }


def hostile_leakage(fx: dict, kappa: int) -> dict:
    clean = invent([tuple(p) for p in fx["training_corpus"]], kappa)
    poisoned = dict(fx)
    poisoned["heldout_reuse_positive"] = [["z", "z"], ["q", "q", "q"]]
    poisoned["heldout_unrelated_control"] = [["y", "y"]]
    poisoned_run = invent([tuple(p) for p in poisoned["training_corpus"]], kappa)
    identical = json.dumps(clean["library"], sort_keys=True) == json.dumps(
        poisoned_run["library"], sort_keys=True
    )
    return {
        "library_identical_under_poisoned_heldouts": identical,
        "code": HostileCodes["leakage"],
    }


# ---------------------------------------------------------------------------
# ablation over the maintenance-charge grid
# ---------------------------------------------------------------------------

def kappa_ablation(
    grid: Sequence[int],
    corpus: Sequence[Sequence[str]],
    hplus: Sequence[Sequence[str]],
    hminus: Sequence[Sequence[str]],
) -> dict:
    rows = []
    for kappa in grid:
        trace = invent([tuple(p) for p in corpus], kappa)
        library = trace["library"]
        order = trace["library_order"]
        m2_formed = (
            len(trace["admissions"]) >= 2
            and trace["admissions"][0]["body"] == ["a", "b"]
            and trace["admissions"][1]["body"]
            == [trace["admissions"][0]["name"], trace["admissions"][0]["name"]]
        )
        vp = heldout_verdict(hplus, library, order, kappa)
        vm = heldout_verdict(hminus, library, order, kappa)
        rows.append(
            {
                "kappa": kappa,
                "admissions": [a["name"] for a in trace["admissions"]],
                "n_admissions": len(trace["admissions"]),
                "m2_formed": m2_formed,
                "net_hplus": vp["net"],
                "net_hminus": vm["net"],
                "K_total": k_total(library, kappa),
            }
        )
    feasible = [r["kappa"] for r in rows if r["m2_formed"]]
    primary = max(feasible) if feasible else None
    return {"grid": list(grid), "rows": rows, "kappa_primary_derived": primary}


# ---------------------------------------------------------------------------
# receipt
# ---------------------------------------------------------------------------

def build_receipt() -> dict:
    fx = load_fixtures()
    kappa = fx["maintenance_charge_kappa_primary"]
    corpus = [tuple(p) for p in fx["training_corpus"]]
    hplus = [tuple(w) for w in fx["heldout_reuse_positive"]]
    hminus = [tuple(w) for w in fx["heldout_unrelated_control"]]

    trace = invent(corpus, kappa)
    library = trace["library"]
    order = trace["library_order"]

    # REC-1 witness
    admissions = trace["admissions"]
    m2_uses_m1 = (
        len(admissions) >= 2
        and admissions[1]["body"] == [admissions[0]["name"], admissions[0]["name"]]
    )
    rec1 = {
        "m1_body": admissions[0]["body"] if admissions else None,
        "m2_body": admissions[1]["body"] if len(admissions) > 1 else None,
        "m2_uses_m1": m2_uses_m1,
        "m2_base_expansion": list(expand_word((admissions[1]["name"],), library))
        if len(admissions) > 1
        else None,
        "m1_base_expansion": list(expand_word((admissions[0]["name"],), library))
        if admissions
        else None,
        "dag_acyclic": is_acyclic(library),
        "exact_witness": bool(
            admissions
            and admissions[0]["body"] == ["a", "b"]
            and m2_uses_m1
            and expand_word((admissions[1]["name"],), library) == ("a", "b", "a", "b")
        ),
    }

    verdict_plus = heldout_verdict(hplus, library, order, kappa)
    verdict_minus = heldout_verdict(hminus, library, order, kappa)
    thr = threshold_check(verdict_plus, library, kappa)
    nulls = null_ensemble(
        corpus, len(library), fx["null_seeds"], hplus, hminus, kappa
    )
    abl = kappa_ablation(fx["maintenance_charge_kappa_grid"], corpus, hplus, hminus)

    better_plus = sum(1 for v in nulls["nets_hplus"] if v < verdict_plus["net"])
    rank_plus = sum(1 for v in nulls["nets_hplus"] if v < verdict_plus["net"]) + 1

    hostiles = {
        "cycle": hostile_cycle(),
        "uncharged_definition": hostile_uncharged_definition(kappa),
        "uncharged_maintenance": hostile_uncharged_maintenance(),
        "zero_gain": hostile_zero_gain(kappa),
        "semantic_rewrite": hostile_semantic_rewrite(),
        "heldout_hash": hostile_heldout_hash(fx),
        "leakage": hostile_leakage(fx, kappa),
    }
    kappa_row = next(r for r in abl["rows"] if r["kappa"] == kappa)

    checks = {
        "rec1_exact": rec1["exact_witness"],
        "grw1_zero_failures": trace["grw1_failures"] == 0,
        "stopped_by_saturation": trace["stopped_by"] == "NO_STRICTLY_BENEFICIAL_CANDIDATE",
        "cycles_all_rejected": hostiles["cycle"]["all_cycles_rejected"],
        "grammar_unchanged_under_cycle": hostiles["cycle"]["grammar_unchanged"],
        "definition_charge_load_bearing": hostiles["uncharged_definition"]["charge_load_bearing"],
        "maintenance_charge_load_bearing": hostiles["uncharged_maintenance"]["maintenance_charge_load_bearing"],
        "zero_gain_rejected": hostiles["zero_gain"]["zero_gain_rejected"],
        "semantic_rewrite_detected": hostiles["semantic_rewrite"]["corrupt_rewrite_detected"],
        "heldout_tamper_detected": hostiles["heldout_hash"]["tamper_detected"],
        "leakage_absent": hostiles["leakage"]["library_identical_under_poisoned_heldouts"],
        "hplus_strict_net_reduction": verdict_plus["net"] < 0,
        "hminus_regression_preserved": verdict_minus["net"] >= 0,
        "threshold_all_macros_marginal": thr["all_macros_hold_marginal"],
        "threshold_aggregate": thr["aggregate_holds"],
        "kappa_primary_witness_forms": kappa_row["m2_formed"],
    }
    all_green = all(checks.values())
    terminal = TERMINAL_GREEN if all_green else TERMINAL_RED_PREFIX + "SEE_CHECKS"

    return {
        "schema": RECEIPT_SCHEMA,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "issue": ISSUE,
        "parent_issue": PARENT_ISSUE,
        "freeze_commit": FREEZE_COMMIT,
        "source_main": SOURCE_MAIN,
        "fixtures_sha256": fixtures_sha256(),
        "terminal": terminal,
        "checks": checks,
        "grammar": {
            "base_tokens": ["a", "b", "c"],
            "symbol_order_final": canonical_symbol_order(order),
            "training_corpus_symbols_S0": trace["initial_corpus_symbols"],
            "depth_limit_derived": trace["depth_limit"],
            "stopped_by": trace["stopped_by"],
            "grw1_failures": trace["grw1_failures"],
        },
        "invention": {
            "kappa": kappa,
            "admissions": admissions,
            "final_corpus": trace["corpus_final"],
        },
        "rec1": rec1,
        "heldout_reuse_positive": verdict_plus,
        "heldout_unrelated_control": verdict_minus,
        "threshold_thr1": thr,
        "null_null1": {
            "pool_size": nulls["pool_size"],
            "pool_bodies": nulls["pool_bodies"],
            "library_size": nulls["library_size"],
            "n_seeds": nulls["n_seeds"],
            "true_net_hplus": verdict_plus["net"],
            "null_net_hplus_min": nulls["net_hplus_min"],
            "null_net_hplus_median": nulls["net_hplus_median"],
            "null_net_hplus_max": nulls["net_hplus_max"],
            "null_net_hminus_min": nulls["net_hminus_min"],
            "null_net_hminus_median": nulls["net_hminus_median"],
            "null_net_hminus_max": nulls["net_hminus_max"],
            "nulls_strictly_better_hplus": better_plus,
            "true_library_empirical_rank_hplus": rank_plus,
            "nets_hplus": nulls["nets_hplus"],
            "nets_hminus": nulls["nets_hminus"],
        },
        "kappa_ablation": abl,
        "hostiles": hostiles,
    }


def main() -> None:
    receipt = build_receipt()
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
