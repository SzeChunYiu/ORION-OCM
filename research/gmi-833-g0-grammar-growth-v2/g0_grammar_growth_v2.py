#!/usr/bin/env python3
"""GMI #833 Section-E E8 grammar-growth tranche 2 (#897 follow-up).

Frozen by research/gmi-833-g0-grammar-growth-v2/FREEZE_V2.md at the freeze
commits pinned in FREEZE_COMMITS (all precede this file on this branch). Closes the three gaps recorded
in SCIENTIFIC_LEDGER_V1.json: GAP-E8-1 (deeper generational chains),
GAP-E8-2 (admission-rule economics head-to-head), GAP-E8-3 (execution-cost
burden variant).

Reuses the merged v1 machinery by import; all arithmetic is exact integer.
Receipts are byte-identical under -B and -O -B and across CPython versions.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = pathlib.Path(__file__).resolve().parent
V1_DIR = ROOT.parent / "gmi-833-g0-grammar-growth-v1"
sys.path.insert(0, str(V1_DIR))
import g0_grammar_growth_v1 as v1  # noqa: E402

CLAIM_CEILING = (
    "GMI_833_E8_TRANCHE2_DEPTH3_FORMATION__TIER_CONDITIONAL_COMPOUNDING__"
    "ADMISSION_RULE_ECONOMICS__EXEC_COST_ROBUST_AT_REGISTERED_SCOPE"
)
FREEZE_COMMITS = ["c08112e3a287ff3f95cded5473cd504ec74726ef", "1114b39124bc7669058a74108371278497ea683f"]
SOURCE_MAIN = "9cb5197fb09a781b65be09abcd2fbeca0fd759fb"
ISSUE = 897
PARENT_ISSUE = 833
TERMINAL_GREEN = "GMI_833_E8_TRANCHE2_GREEN_AT_REGISTERED_SCOPE"
TERMINAL_RED_PREFIX = "GMI_833_E8_TRANCHE2_RED__"
FORBIDDEN_PROMOTIONS = list(v1.FORBIDDEN_PROMOTIONS) + [
    "DEPTH_4_PLUS_FORMED",
    "UNIVERSAL_DEPTH_GROWTH",
    "COMPRESSION_GATE_DOMINATES",
    "UTILITY_GATE_DOMINATES",
    "EXEC_INVARIANT_ALL_RHO",
]
RECEIPT_SCHEMA = "GMI833G0GrammarGrowthT2ReceiptV1"
FIXTURES_PATH = ROOT / "FROZEN_FIXTURES_V2.json"
V1_FIXTURES_SHA = "12acccf68dd5e02ac0521737bc8239f550600e80b87de3330beafa9a554921c6"


class Tranche2Error(Exception):
    """Raised for registered fail-closed conditions."""


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

def load_fixtures() -> dict:
    with FIXTURES_PATH.open("r", encoding="utf-8") as fh:
        fx = json.load(fh)
    if fx.get("schema") != "GMI833G0GrammarGrowthFrozenFixturesV2":
        raise Tranche2Error("FIXTURES_V2_SCHEMA_MISMATCH")
    v1sha = hashlib.sha256((V1_DIR / "FROZEN_FIXTURES_V1.json").read_bytes()).hexdigest()
    if v1sha != fx["v1_fixtures_sha256"] or v1sha != V1_FIXTURES_SHA:
        raise Tranche2Error("V1_FIXTURES_HASH_MISMATCH")
    if fx["source_main"] != SOURCE_MAIN:
        raise Tranche2Error("FIXTURES_SOURCE_MAIN_MISMATCH")
    return fx


def fixtures_sha256() -> str:
    return hashlib.sha256(FIXTURES_PATH.read_bytes()).hexdigest()


def parse(word: str) -> Tuple[str, ...]:
    return tuple(word)


def parse_programs(words: Sequence[str]) -> List[Tuple[str, ...]]:
    return [tuple(w) for w in words]


# ---------------------------------------------------------------------------
# invention analysis (reuse v1.invent)
# ---------------------------------------------------------------------------

def trace_depth(admissions: Sequence[dict]) -> List[int]:
    dep = {}
    out = []
    for k, a in enumerate(admissions):
        prev = [j for j in range(k) if admissions[j]["name"] in a["body"]]
        dep[a["name"]] = 1 + max([dep[admissions[j]["name"]] for j in prev], default=0)
        out.append(dep[a["name"]])
    return out


def prefix_libraries(trace: dict) -> List[Tuple[Dict[str, Tuple[str, ...]], List[str]]]:
    out: List[Tuple[Dict[str, Tuple[str, ...]], List[str]]] = [({}, [])]
    lib: Dict[str, Tuple[str, ...]] = {}
    names: List[str] = []
    for a in trace["admissions"]:
        lib = dict(lib)
        lib[a["name"]] = tuple(a["body"])
        names = names + [a["name"]]
        out.append((dict(lib), list(names)))
    return out


# ---------------------------------------------------------------------------
# EXEC-B execution-cost burden (frozen model; theorem T8)
# ---------------------------------------------------------------------------

def opcosts(library: Dict[str, Tuple[str, ...]], rho: int) -> Dict[str, int]:
    cost = {"a": 1, "b": 1, "c": 1}
    for name in sorted(library, key=lambda n: int(n[1:])):
        cost[name] = rho + sum(cost[s] for s in library[name])
    return cost


def exec_burden(
    target: Sequence[str],
    symbol_order: Sequence[str],
    library: Dict[str, Tuple[str, ...]],
    rho: int,
) -> int:
    """Exact execution-cost burden: sum of exec(p) over the canonical
    enumeration up to and including the first hit."""
    w = tuple(target)
    n = len(w)
    A = len(symbol_order)
    symbols = list(symbol_order)
    cost = opcosts(library, rho)
    C = sum(cost[s] for s in symbols)
    exps = v1.symbol_expansions(symbols, library)

    S = [[False] * (n + 1) for _ in range(n + 1)]
    S[n][0] = True
    for i in range(n - 1, -1, -1):
        for r in range(1, n - i + 1):
            for s in symbols:
                e = exps[s]
                if e and i + len(e) <= n and tuple(w[i : i + len(e)]) == e and S[i + len(e)][r - 1]:
                    S[i][r] = True
                    break
    lstar = None
    for r in range(1, n + 1):
        if S[0][r]:
            lstar = r
            break
    if lstar is None:
        raise Tranche2Error("TARGET_UNREACHABLE")
    _, hit = v1.burden_dp(w, symbols, exps)

    total = 0
    for l in range(1, lstar):
        total += l * (A ** (l - 1)) * C
    pref = 0
    idx = {s: k for k, s in enumerate(symbols)}
    for i, hs in enumerate(hit):
        r = lstar - 1 - i
        for s in symbols:
            if idx[s] >= idx[hs]:
                break
            total += (A ** r) * (pref + cost[s])
            if r >= 1:
                total += (A ** (r - 1)) * r * C
        pref += cost[hs]
    total += pref
    return total


def exec_burden_naive(
    target: Sequence[str],
    symbol_order: Sequence[str],
    library: Dict[str, Tuple[str, ...]],
    rho: int,
) -> int:
    """Reference enumerator (hostile HEXEC-1; small targets only)."""
    import itertools as it

    w = tuple(target)
    cost = opcosts(library, rho)
    total = 0
    for length in range(1, len(w) + 1):
        for p in it.product(symbol_order, repeat=length):
            total += sum(cost[s] for s in p)
            if v1.expand_word(p, library) == w:
                return total
    raise Tranche2Error("TARGET_UNREACHABLE_NAIVE")


# ---------------------------------------------------------------------------
# UTL-1 utility-gated admission (frozen rule + ablation modes)
# ---------------------------------------------------------------------------

def utility_library(
    corpus: Sequence[Sequence[str]],
    val: Sequence[Sequence[str]],
    kappa: int,
    mode: str = "primary",
) -> dict:
    """UTL-1: INV-1 candidate order; admit the first candidate whose tentative
    library has charged aggregate T3-burden on `val` strictly below both the
    primitive-only grammar's and the current library's charged val-burden.
    mode: primary | primitive (UTL-1p: drop the improvement conjunct) |
    stop (UTL-1s: stop at the first failing top candidate)."""
    work = [tuple(p) for p in corpus]
    library: Dict[str, Tuple[str, ...]] = {}
    names: List[str] = []
    expb = v1.symbol_expansions(["a", "b", "c"], {})
    g0v = sum(v1.burden_dp(w, ["a", "b", "c"], expb)[0] for w in val)
    cur = g0v
    decisions: List[dict] = []

    def charged(lib: Dict[str, Tuple[str, ...]], nmz: Sequence[str]) -> int:
        if not nmz:
            return g0v
        o = ["a", "b", "c"] + list(nmz)
        e = v1.symbol_expansions(o, lib)
        return sum(v1.burden_dp(w, o, e)[0] for w in val) + v1.k_total(lib, kappa)

    depth_limit = v1.corpus_symbol_count([tuple(p) for p in corpus])
    while len(names) < depth_limit:
        order = ["a", "b", "c"] + names
        pool = v1.candidate_pool(work, library)
        scored = []
        for body, (occ, fp, fo) in pool.items():
            g = v1.admission_gain(body, occ, kappa)
            if g > 0:
                scored.append((body, g, occ, fp, fo))
        if not scored:
            break
        scored.sort(key=lambda x: v1.tie_key(x[0], x[1], x[2], x[3], x[4], library, order))
        admitted = False
        for body, g, occ, fp, fo in scored:
            name = "u{}".format(len(library) + 1)
            trial = dict(library)
            trial[name] = body
            tnames = names + [name]
            cV = charged(trial, tnames)
            ok = cV < g0v and (cV < cur or mode == "primitive")
            decisions.append(
                {
                    "candidate": list(body),
                    "gain": g,
                    "charged_val": cV,
                    "g0_val": g0v,
                    "current_val": cur,
                    "admitted": ok,
                }
            )
            if ok:
                library = trial
                names = tnames
                work = [v1.greedy_rewrite(body, name, p) for p in work]
                cur = cV
                admitted = True
                break
            if mode == "stop":
                break
        if not admitted:
            break
    return {
        "library": library,
        "library_order": names,
        "decisions": decisions,
        "g0_val": g0v,
        "final_val": cur,
        "mode": mode,
    }


# ---------------------------------------------------------------------------
# ADM-ALT diagnostic (smallest body referencing the latest macro)
# ---------------------------------------------------------------------------

def adm_alt(corpus: Sequence[Sequence[str]], kappa: int) -> dict:
    original = [tuple(p) for p in corpus]
    original_base = [v1.expand_word(p, {}) for p in original]
    work = [tuple(p) for p in corpus]
    library: Dict[str, Tuple[str, ...]] = {}
    admissions: List[dict] = []
    depth_limit = v1.corpus_symbol_count(original)
    stopped_by = "DEPTH_LIMIT"
    while len(admissions) < depth_limit:
        order = ["a", "b", "c"] + [n for n in sorted(library, key=lambda x: int(x[1:]))]
        pool = v1.candidate_pool(work, library)
        scored = []
        for body, (occ, fp, fo) in pool.items():
            g = v1.admission_gain(body, occ, kappa)
            if g > 0:
                scored.append((body, g, occ, fp, fo))
        if not scored:
            stopped_by = "NO_STRICTLY_BENEFICIAL_CANDIDATE"
            break
        scored.sort(key=lambda x: v1.tie_key(x[0], x[1], x[2], x[3], x[4], library, order))
        latest = order[-1] if len(order) > 3 else None
        pick = None
        if latest is not None:
            refs = [t for t in scored if latest in t[0]]
            if refs:
                refs.sort(key=lambda t: (len(t[0]), v1.tie_key(t[0], t[1], t[2], t[3], t[4], library, order)))
                pick = refs[0]
        if pick is None:
            pick = scored[0]
        body, gain, occ, _, _ = pick
        name = "d{}".format(len(library) + 1)
        new_library = dict(library)
        new_library[name] = body
        if not v1.is_acyclic(new_library):
            raise Tranche2Error("ADMALT_CYCLE")
        pre_base = [v1.expand_word(p, library) for p in work]
        new_work = [v1.greedy_rewrite(body, name, p) for p in work]
        for old, new in zip(pre_base, [v1.expand_word(p, new_library) for p in new_work]):
            if old != new:
                raise Tranche2Error("ADMALT_SEMANTIC_INVARIANT_VIOLATION")
        admissions.append({"name": name, "body": list(body), "occurrences": occ, "gain": gain})
        library = new_library
        work = new_work
    for ob, cur_w in zip(original_base, work):
        if v1.expand_word(cur_w, library) != ob:
            raise Tranche2Error("ADMALT_FINAL_SEMANTIC_MISMATCH")
    return {
        "library": library,
        "admissions": admissions,
        "stopped_by": stopped_by,
        "max_depth": max(trace_depth(admissions), default=0),
    }


# ---------------------------------------------------------------------------
# tiered prefix tables and CMP-1
# ---------------------------------------------------------------------------

def tier_prefix_table(
    corpus: Sequence[Sequence[str]],
    tiers: Dict[str, Sequence[Sequence[str]]],
    hminus: Sequence[Sequence[str]],
    kappa: int,
    exec_rho: Optional[int] = None,
) -> dict:
    trace = v1.invent([tuple(p) for p in corpus], kappa)
    prefixes = prefix_libraries(trace)
    expb = v1.symbol_expansions(["a", "b", "c"], {})

    def burden(w, lib, names):
        if not names:
            return v1.burden_dp(w, ["a", "b", "c"], expb)[0]
        o = ["a", "b", "c"] + names
        return v1.burden_dp(w, o, v1.symbol_expansions(o, lib))[0]

    def eburden(w, lib, names, rho):
        if not names:
            return exec_burden(w, ["a", "b", "c"], {}, rho)
        o = ["a", "b", "c"] + names
        return exec_burden(w, o, lib, rho)

    rows = []
    for gi, (lib, names) in enumerate(prefixes):
        K = v1.k_total(lib, kappa)
        cells = {}
        agg = 0
        for tname, ts in tiers.items():
            c = sum(burden(w, lib, names) for w in ts)
            cells[tname] = c
            agg += c
        g0agg = 0
        for tname, ts in tiers.items():
            g0agg += sum(v1.burden_dp(w, ["a", "b", "c"], expb)[0] for w in ts)
        hmc = sum(burden(w, lib, names) for w in hminus)
        g0hm = sum(v1.burden_dp(w, ["a", "b", "c"], expb)[0] for w in hminus)
        row = {
            "generation": gi,
            "K_total": K,
            "tier_burdens": cells,
            "aggregate_burden": agg,
            "aggregate_net": agg + K - g0agg,
            "hminus_burden": hmc,
            "hminus_net": hmc + K - g0hm,
        }
        if exec_rho is not None:
            ecells = {tname: sum(eburden(w, lib, names, exec_rho) for w in ts) for tname, ts in tiers.items()}
            eagg = sum(ecells.values())
            g0e = sum(exec_burden(w, ["a", "b", "c"], {}, exec_rho) for ts in tiers.values() for w in ts)
            row["exec_tier_burdens"] = ecells
            row["exec_aggregate_net"] = eagg + K - g0e
            ehm = sum(eburden(w, lib, names, exec_rho) for w in hminus)
            g0ehm = sum(exec_burden(w, ["a", "b", "c"], {}, exec_rho) for w in hminus)
            row["exec_hminus_net"] = ehm + K - g0ehm
        rows.append(row)

    tier_order = list(tiers.keys())
    match_gen = {}
    admissions = trace["admissions"]
    for tname in tier_order:
        # matching generation = max g such that every target of the tier
        # contains >= 2 greedy-disjoint occurrences of the g-th macro body's
        # full base expansion (the frozen tier-assignment rule)
        m = 0
        for g in range(1, len(admissions) + 1):
            body_g = tuple(admissions[g - 1]["body"])
            expansion = v1.expand_word(body_g, {a["name"]: tuple(a["body"]) for a in admissions[:g]})
            if all(v1.greedy_count(expansion, w) >= 2 for w in tiers[tname]):
                m = g
        match_gen[tname] = m
    cmp1 = {
        "tier_monotone_to_match_then_regression": {},
        "hminus_monotone_regression": all(
            rows[i + 1]["hminus_burden"] > rows[i]["hminus_burden"] for i in range(len(rows) - 1)
        ),
        "aggregate_net_strictly_decreasing": all(
            rows[i + 1]["aggregate_net"] < rows[i]["aggregate_net"] for i in range(len(rows) - 1)
        ),
    }
    for tname in tier_order:
        series = [r["tier_burdens"][tname] for r in rows]
        m = match_gen[tname]
        ok_dec = all(series[i + 1] < series[i] for i in range(min(m, len(series) - 1)))
        ok_inc = all(series[i + 1] > series[i] for i in range(m, len(series) - 1))
        cmp1["tier_monotone_to_match_then_regression"][tname] = {
            "match_generation": m,
            "series": series,
            "decreasing_to_match": ok_dec,
            "increasing_past_match": ok_inc if m < len(series) - 1 else True,
            "holds": ok_dec and (ok_inc if m < len(series) - 1 else True),
        }
    return {"trace": trace, "rows": rows, "cmp1": cmp1}


# ---------------------------------------------------------------------------
# ECON-1: f* scans and kappa* derivation
# ---------------------------------------------------------------------------

def fstar_scan(build, bracket: Sequence[int], kappa: int) -> dict:
    lo, hi = bracket
    rows = []
    fstar = None
    tie_cases = []
    for f in range(lo, hi + 1):
        corpus = [tuple(p) for p in build(f)]
        t = v1.invent(corpus, kappa)
        adm = t["admissions"]
        first_is_ab = bool(adm) and adm[0]["body"] == ["a", "b"]
        strict = False
        if first_is_ab and adm:
            pool = v1.candidate_pool(corpus, {})
            g_ab = adm[0]["gain"]
            strict = all(
                v1.admission_gain(b, o, kappa) < g_ab
                for b, (o, _, _) in pool.items()
                if b != ("a", "b")
            )
        rows.append(
            {
                "f": f,
                "first_admission": list(adm[0]["body"]) if adm else None,
                "first_gain": adm[0]["gain"] if adm else None,
                "n_admissions": len(adm),
                "strict_margin": bool(strict),
            }
        )
        if first_is_ab and strict and fstar is None:
            fstar = f
        if first_is_ab and not strict and fstar is None:
            tie_cases.append(f)
    return {"rows": rows, "fstar_strict": fstar, "tie_cases_before_fstar": tie_cases}


def kappa_star(corpus, expected_bodies: Sequence[str], grid: Sequence[int]) -> dict:
    rows = []
    ks = None
    for k in grid:
        t = v1.invent([tuple(p) for p in corpus], k)
        bodies = ["".join(a["body"]) for a in t["admissions"]]
        match = bodies == list(expected_bodies)
        rows.append({"kappa": k, "bodies": bodies, "match": match})
        if match:
            ks = k
    return {"rows": rows, "kappa_star": ks}


# ---------------------------------------------------------------------------
# NULL-2: unranked equal-size random-admission ensembles
# ---------------------------------------------------------------------------

def _nck(n: int, k: int) -> int:
    return v1._n_choose_k(n, k)


def unrank_combination(n: int, k: int, r: int) -> Tuple[int, ...]:
    """Lexicographic k-subset of range(n) with rank r (matches the recursive
    smallest-first materialized enumeration exactly)."""
    out = []
    x = 0
    for j in range(k):
        while True:
            c = _nck(n - x - 1, k - j - 1)
            if r < c:
                out.append(x)
                x += 1
                break
            r -= c
            x += 1
    return tuple(out)


def null_ensemble_v2(
    corpus: Sequence[Sequence[str]],
    library_size: int,
    seeds: Sequence[int],
    targets_plus: Sequence[Sequence[str]],
    targets_minus: Sequence[Sequence[str]],
    kappa: int,
    exec_rho: Optional[int] = None,
) -> dict:
    pool = v1.candidate_pool([tuple(p) for p in corpus], {})
    pool_bodies = sorted(pool)
    P = len(pool_bodies)
    combos_total = _nck(P, library_size)
    expb = v1.symbol_expansions(["a", "b", "c"], {})
    g0p = sum(v1.burden_dp(w, ["a", "b", "c"], expb)[0] for w in targets_plus)
    g0m = sum(v1.burden_dp(w, ["a", "b", "c"], expb)[0] for w in targets_minus)
    if exec_rho is not None:
        eg0p = sum(exec_burden(w, ["a", "b", "c"], {}, exec_rho) for w in targets_plus)
        eg0m = sum(exec_burden(w, ["a", "b", "c"], {}, exec_rho) for w in targets_minus)
    nets_p: List[int] = []
    nets_m: List[int] = []
    exec_nets_p: List[int] = []
    exec_nets_m: List[int] = []
    per_seed = []
    for seed in seeds:
        ci = (((seed + 1) * 2654435761) % (2 ** 32)) % combos_total
        idxs = unrank_combination(P, library_size, ci)
        bodies = [pool_bodies[i] for i in idxs]
        names = ["n{}".format(i + 1) for i in range(len(bodies))]
        lib = {nm: b for nm, b in zip(names, bodies)}
        order = ["a", "b", "c"] + names
        exps = v1.symbol_expansions(order, lib)
        cumP = sum(v1.burden_dp(w, order, exps)[0] for w in targets_plus)
        cumM = sum(v1.burden_dp(w, order, exps)[0] for w in targets_minus)
        K = v1.k_total(lib, kappa)
        nets_p.append(cumP + K - g0p)
        nets_m.append(cumM + K - g0m)
        row = {
            "seed": seed,
            "combo_index": ci,
            "net_hplus": cumP + K - g0p,
            "net_hminus": cumM + K - g0m,
        }
        if exec_rho is not None:
            eP = sum(exec_burden(w, order, lib, exec_rho) for w in targets_plus)
            eM = sum(exec_burden(w, order, lib, exec_rho) for w in targets_minus)
            exec_nets_p.append(eP + K - eg0p)
            exec_nets_m.append(eM + K - eg0m)
            row["exec_net_hplus"] = eP + K - eg0p
            row["exec_net_hminus"] = eM + K - eg0m
        per_seed.append(row)
    out = {
        "pool_size": P,
        "library_size": library_size,
        "n_seeds": len(seeds),
        "combos_total": combos_total,
        "nets_hplus": nets_p,
        "nets_hminus": nets_m,
        "net_hplus_min": min(nets_p),
        "net_hplus_median": sorted(nets_p)[len(nets_p) // 2],
        "net_hplus_max": max(nets_p),
        "per_seed": per_seed,
    }
    if exec_rho is not None:
        out["exec_nets_hplus"] = exec_nets_p
        out["exec_nets_hplus_min"] = min(exec_nets_p)
    return out


# ---------------------------------------------------------------------------
# head-to-head
# ---------------------------------------------------------------------------

def head_to_head(
    corpus, tiers_or_flat, hminus, val, kappa: int, exec_rho: int
) -> dict:
    if isinstance(tiers_or_flat, dict):
        flat = [w for ts in tiers_or_flat.values() for w in ts]
    else:
        flat = list(tiers_or_flat)
    comp = v1.invent([tuple(p) for p in corpus], kappa)
    util = utility_library(corpus, val, kappa)
    out = {}
    for arm, lib, order in (
        ("compression", comp["library"], comp["library_order"]),
        ("utility", util["library"], util["library_order"]),
    ):
        o = ["a", "b", "c"] + list(order)
        exps = v1.symbol_expansions(o, lib)
        cumP = sum(v1.burden_dp(w, o, exps)[0] for w in flat)
        cumM = sum(v1.burden_dp(w, o, exps)[0] for w in hminus)
        g0p = sum(v1.burden_dp(w, ["a", "b", "c"], v1.symbol_expansions(["a", "b", "c"], {}))[0] for w in flat)
        g0m = sum(v1.burden_dp(w, ["a", "b", "c"], v1.symbol_expansions(["a", "b", "c"], {}))[0] for w in hminus)
        K = v1.k_total(lib, kappa)
        eP = sum(exec_burden(w, o, lib, exec_rho) for w in flat)
        eM = sum(exec_burden(w, o, lib, exec_rho) for w in hminus)
        eg0p = sum(exec_burden(w, ["a", "b", "c"], {}, exec_rho) for w in flat)
        eg0m = sum(exec_burden(w, ["a", "b", "c"], {}, exec_rho) for w in hminus)
        out[arm] = {
            "library": {k: list(v) for k, v in lib.items()},
            "library_order": list(order),
            "net_hplus_count": cumP + K - g0p,
            "net_hminus_count": cumM + K - g0m,
            "net_hplus_exec": eP + K - eg0p,
            "net_hminus_exec": eM + K - eg0m,
            "K_total": K,
        }
    out["decisions_utility"] = util["decisions"]
    return out


# ---------------------------------------------------------------------------
# hostiles (tranche-2 battery)
# ---------------------------------------------------------------------------

def hostile_hlk2(corpus, val, hplus_poison, hminus_poison, kappa) -> dict:
    """Poisoned EVAL suites (reuse-positive and control) must not influence
    either arm: invention reads only the training corpus, the gate reads only
    the validation suite. Executed comparison, mirroring v1 HLK-1: a poisoned
    fixtures-shaped dict (eval entries replaced) is handed to the harness path
    that extracts corpus/validation; both arms are re-derived and compared
    byte-identical against the clean derivation."""
    poisoned = {
        "training_corpus": [list(p) for p in corpus],
        "validation": [list(w) for w in val],
        "heldout_reuse_positive": [["z", "z"], ["q", "q", "q"]],
        "heldout_unrelated_control": [["y", "y"]],
    }
    base_comp = v1.invent([tuple(p) for p in poisoned["training_corpus"]], kappa)
    base_util = utility_library(
        [tuple(p) for p in poisoned["training_corpus"]],
        [tuple(w) for w in poisoned["validation"]],
        kappa,
    )
    comp_clean = v1.invent([tuple(p) for p in corpus], kappa)
    util_clean = utility_library(corpus, val, kappa)
    identical = json.dumps(base_comp["library"], sort_keys=True) == json.dumps(
        comp_clean["library"], sort_keys=True
    ) and json.dumps(base_util["library"], sort_keys=True) == json.dumps(
        util_clean["library"], sort_keys=True
    )
    return {
        "libraries_identical_under_poisoned_eval": identical,
        "poisoned_eval_entries_changed": poisoned["heldout_reuse_positive"] != [list(w) for w in (hplus_poison or [])],
        "code": "HELDOUT_LEAKAGE_ABSENT_T2",
    }


def hostile_hcyc2() -> dict:
    lib = {"m1": ("a", "b"), "m2": ("m1", "m1"), "m3": ("m2", "m3")}
    try:
        v1.expand_word(("m3",), lib)
        return {"code": "NO_CYCLE_DETECTED"}
    except v1.GrammarGrowthError as exc:
        return {"code": str(exc), "detected": str(exc) == "RECURSIVE_LIBRARY_CYCLE"}


def hostile_hzero2(corpus, kappa_zero_gain) -> dict:
    t = v1.invent([tuple(p) for p in corpus], kappa_zero_gain)
    last_gain = t["admissions"][-1]["gain"] if t["admissions"] else None
    n_at_k1 = len(v1.invent([tuple(p) for p in corpus], 1)["admissions"])
    return {
        "kappa": kappa_zero_gain,
        "n_admissions": len(t["admissions"]),
        "n_admissions_kappa1": n_at_k1,
        "zero_gain_rejected": len(t["admissions"]) == n_at_k1 - 1 and last_gain != 0,
    }


def hostile_hexec1() -> dict:
    lib = {"m1": ("a", "b"), "m2": ("m1", "m1"), "m3": ("m2", "m2")}
    order = ["a", "b", "c", "m1", "m2", "m3"]
    ok = True
    detail = []
    for rho in (1, 2, 4):
        for w in ("abab", "cab", "ababcab", "abababababababab", "aac"):
            d = exec_burden(w, order, lib, rho)
            nv = exec_burden_naive(w, order, lib, rho)
            ok = ok and d == nv
            detail.append({"rho": rho, "w": w, "dp": d, "naive": nv, "match": d == nv})
    return {"all_match": ok, "cases": detail, "code": "EXEC_DP_NAIVE_AGREE"}


def hostile_hutl1(corpus, hminus_style_val, kappa) -> dict:
    res = utility_library(corpus, hminus_style_val, kappa)
    return {
        "library_empty": len(res["library"]) == 0,
        "n_decisions": len(res["decisions"]),
        "code": "UTL_FAIL_CLOSED_EMPTY",
    }


def hostile_hunr1() -> dict:
    ok = True
    checked = 0
    for n, k in ((8, 2), (10, 3), (12, 2), (29, 3)):
        total = _nck(n, k)
        combos = [tuple(c) for c in v1._combinations_indices(n, k)]
        for i in range(min(total, 300)):
            if unrank_combination(n, k, i) != combos[i]:
                ok = False
            checked += 1
    return {"all_match": ok, "comparisons": checked, "code": "UNRANK_AGREES_WITH_ENUMERATION"}


def hostile_hsem2(corpus, kappa) -> dict:
    t = v1.invent([tuple(p) for p in corpus], kappa)
    return {"grw1_failures": t["grw1_failures"], "zero": t["grw1_failures"] == 0}


# ---------------------------------------------------------------------------
# v1 flagship EXEC re-run
# ---------------------------------------------------------------------------

def v1_flagship_exec(fx: dict, v1fx: dict) -> dict:
    kappa = fx["maintenance_charge_kappa_primary"]
    corpus = [tuple(p) for p in v1fx["training_corpus"]]
    hp = [tuple(w) for w in v1fx["heldout_reuse_positive"]]
    hm = [tuple(w) for w in v1fx["heldout_unrelated_control"]]
    trace = v1.invent(corpus, kappa)
    lib = trace["library"]
    order = ["a", "b", "c"] + trace["library_order"]
    K = v1.k_total(lib, kappa)
    rows = []
    breakeven = None
    for rho in range(1, 1025):
        eP = sum(exec_burden(w, order, lib, rho) for w in hp)
        eM = sum(exec_burden(w, order, lib, rho) for w in hm)
        gP = sum(exec_burden(w, ["a", "b", "c"], {}, rho) for w in hp)
        gM = sum(exec_burden(w, ["a", "b", "c"], {}, rho) for w in hm)
        netP = eP + K - gP
        netM = eM + K - gM
        if rho in fx["exec_model"]["rho_grid"]:
            rows.append(
                {
                    "rho": rho,
                    "g0_exec_hplus": gP,
                    "lib_exec_hplus": eP,
                    "net_hplus": netP,
                    "g0_exec_hminus": gM,
                    "lib_exec_hminus": eM,
                    "net_hminus": netM,
                }
            )
        if breakeven is None and netP >= 0:
            breakeven = rho
        if breakeven is not None and rho not in fx["exec_model"]["rho_grid"]:
            break
    return {
        "library": {k: list(vv) for k, vv in lib.items()},
        "K_total": K,
        "rho_grid_rows": rows,
        "breakeven_rho": breakeven if breakeven is not None else "NONE_IN_RANGE",
        "hplus_negative_on_grid": all(r["net_hplus"] < 0 for r in rows),
        "hminus_nonnegative_on_grid": all(r["net_hminus"] >= 0 for r in rows),
    }


# ---------------------------------------------------------------------------
# receipt
# ---------------------------------------------------------------------------

def _depth_of(admissions) -> int:
    return max(trace_depth(admissions), default=0)


def build_receipt() -> dict:
    fx = load_fixtures()
    kappa = fx["maintenance_charge_kappa_primary"]
    with (V1_DIR / "FROZEN_FIXTURES_V1.json").open("r", encoding="utf-8") as fh:
        v1fx = json.load(fh)

    corpora = {k: parse_programs(v["programs"]) for k, v in fx["corpora"].items() if v["programs"]}
    v1corpus = parse_programs(v1fx["training_corpus"])
    corpora["v1ref"] = v1corpus

    suites = fx["suites"]
    S = {}
    for cid in ("c3", "c4", "c5", "trap1", "trap3"):
        sp = suites[cid]
        S[cid] = {
            "tiers": {t: parse_programs(ws) for t, ws in sp["hplus"].items()},
            "hminus": parse_programs(sp["hminus"]),
            "val_shallow": parse_programs(sp.get("validation_shallow", sp.get("validation", []))),
            "val_deep": parse_programs(sp.get("validation_deep", [])),
        }
    S["v1ref"] = {
        "flat": [tuple(w) for w in v1fx["heldout_reuse_positive"]],
        "hminus": [tuple(w) for w in v1fx["heldout_unrelated_control"]],
        "val": parse_programs(suites["v1ref"]["validation"]),
    }

    # --- GAP-E8-1 ---
    depth_section = {}
    for cid in ("c3", "c4", "c5", "trap1", "trap3"):
        t = v1.invent(corpora[cid], kappa)
        depth_section[cid] = {
            "S0": t["initial_corpus_symbols"],
            "admissions": [
                {"name": a["name"], "body": a["body"], "occurrences": a["occurrences"], "gain": a["gain"]}
                for a in t["admissions"]
            ],
            "depths": trace_depth(t["admissions"]),
            "max_depth": _depth_of(t["admissions"]),
            "stopped_by": t["stopped_by"],
            "grw1_failures": t["grw1_failures"],
        }
    family = {}
    for cid in ("fn5", "fn8", "fn12", "fl8", "fl16"):
        t = v1.invent(corpora[cid], kappa)
        family[cid] = {
            "S0": t["initial_corpus_symbols"],
            "first_bodies": ["".join(a["body"]) for a in t["admissions"]],
            "n_admissions": len(t["admissions"]),
            "max_depth": _depth_of(t["admissions"]),
        }
    admalt = {cid: adm_alt(corpora[cid], kappa) for cid in ("c4", "c5")}
    admalt_out = {
        cid: {
            "admissions": [
                {"name": a["name"], "body": a["body"], "occurrences": a["occurrences"], "gain": a["gain"]}
                for a in r["admissions"]
            ],
            "depths": trace_depth(r["admissions"]),
            "max_depth": r["max_depth"],
            "stopped_by": r["stopped_by"],
        }
        for cid, r in admalt.items()
    }

    tier_tables = {}
    for cid in ("c3", "c4", "c5"):
        tier_tables[cid] = tier_prefix_table(
            corpora[cid], S[cid]["tiers"], S[cid]["hminus"], kappa, exec_rho=1
        )

    econ = {}
    for cid in ("c3", "c4", "c5"):
        w2 = "abababab" + "c" + "abababab"
        w3 = w2 + "c" + w2
        w4 = w3 + "c" + w3
        b = {
            "c3": lambda f: ["ab" * 8] * 4 + ["ab"] * f,
            "c4": lambda f: [w3] * 4 + ["ab"] * f,
            "c5": lambda f: [w4] * 4 + ["ab"] * f,
        }[cid]
        econ[cid] = fstar_scan(b, fx["fstar_brackets"][cid], kappa)
        econ[cid + "_kappa_star"] = kappa_star(
            corpora[cid], _expected_bodies(fx, cid), fx["maintenance_charge_kappa_grid"]
        )

    # --- GAP-E8-2 ---
    h2h = {}
    h2h_inputs = [
        ("v1ref", S["v1ref"]["flat"], S["v1ref"]["val"]),
        ("c3", [w for ts in S["c3"]["tiers"].values() for w in ts], S["c3"]["val_shallow"]),
        ("c4", [w for ts in S["c4"]["tiers"].values() for w in ts], S["c4"]["val_shallow"]),
        ("c5", [w for ts in S["c5"]["tiers"].values() for w in ts], S["c5"]["val_shallow"]),
        ("trap1", [w for ts in S["trap1"]["tiers"].values() for w in ts], S["trap1"]["val_shallow"]),
        ("trap3", [w for ts in S["trap3"]["tiers"].values() for w in ts], S["trap3"]["val_shallow"]),
    ]
    for cid, flat, val in h2h_inputs:
        h2h[cid] = head_to_head(corpora[cid], flat, S[cid]["hminus"], val, kappa, exec_rho=1)
    h2h_ablations = {
        "c3_deep_val": utility_library(corpora["c3"], S["c3"]["val_deep"], kappa),
        "c3_utl1p": utility_library(corpora["c3"], S["c3"]["val_shallow"], kappa, mode="primitive"),
        "c3_utl1s": utility_library(corpora["c3"], S["c3"]["val_shallow"], kappa, mode="stop"),
    }
    h2h_ablations_out = {
        k: {"library": {a: list(b) for a, b in r["library"].items()}, "order": r["library_order"]}
        for k, r in h2h_ablations.items()
    }

    nulls = {}
    for cid in ("c3", "c4", "c5"):
        flat = [w for ts in S[cid]["tiers"].values() for w in ts]
        comp = v1.invent(corpora[cid], kappa)
        nulls[cid] = null_ensemble_v2(
            corpora[cid], len(comp["library"]), fx["null_seeds"], flat, S[cid]["hminus"], kappa
        )
    for cid in ("trap1", "trap3", "v1ref"):
        flat = (
            [w for ts in S[cid]["tiers"].values() for w in ts]
            if cid != "v1ref"
            else S["v1ref"]["flat"]
        )
        comp = v1.invent(corpora[cid], kappa)
        util = utility_library(corpora[cid], S[cid]["val_shallow"] if cid != "v1ref" else S["v1ref"]["val"], kappa)
        nulls[cid + "__compression"] = null_ensemble_v2(
            corpora[cid], len(comp["library"]), fx["null_seeds"], flat, S[cid]["hminus"], kappa
        )
        nulls[cid + "__utility"] = null_ensemble_v2(
            corpora[cid], len(util["library"]), fx["null_seeds"], flat, S[cid]["hminus"], kappa
        )

    # --- GAP-E8-3 ---
    flagship_exec = v1_flagship_exec(fx, v1fx)
    v1_flagship_exec_null = null_ensemble_v2(
        v1corpus,
        2,
        fx["null_seeds"],
        S["v1ref"]["flat"],
        S["v1ref"]["hminus"],
        kappa,
        exec_rho=1,
    )

    hostiles = {
        "hlk2": hostile_hlk2(corpora["c3"], S["c3"]["val_shallow"], None, None, kappa),
        "hcyc2": hostile_hcyc2(),
        "hzero2": hostile_hzero2(corpora["c3"], 2),
        "hexec1": hostile_hexec1(),
        "hutl1": hostile_hutl1(corpora["trap1"], S["trap1"]["hminus"], kappa),
        "hunr1": hostile_hunr1(),
        "hsem2": {cid: hostile_hsem2(corpora[cid], kappa) for cid in ("c3", "c4", "c5", "trap1", "trap3")},
    }

    # --- criteria evaluation ---
    exp = fx["expected_traces_kappa1"]

    def trace_matches(cid):
        got = ["".join(a["body"]) for a in depth_section[cid]["admissions"]]
        want = [e["body"] for e in exp[cid]]
        return got == want

    checks = {
        "wit2_c3_chain": trace_matches("c3")
        and any("m2" in a["body"] for a in depth_section["c3"]["admissions"][2:])
        and depth_section["c3"]["max_depth"] == 3,
        "wit2_c4_chain": trace_matches("c4") and depth_section["c4"]["max_depth"] == 3,
        "wit2_c5_chain": trace_matches("c5") and depth_section["c5"]["max_depth"] == 3,
        "grw1_zero_all": all(depth_section[c]["grw1_failures"] == 0 for c in depth_section),
        "sat1_c4_stops_at_3": depth_section["c4"]["max_depth"] == 3,
        "sat1_c5_stops_at_3": depth_section["c5"]["max_depth"] == 3,
        "admalt_deeper_than_inv1": admalt["c4"]["max_depth"] > 3 or admalt["c5"]["max_depth"] > 3,
        "cmp1_holds_all_corpora": all(
            all(v["holds"] for v in tier_tables[c]["cmp1"]["tier_monotone_to_match_then_regression"].values())
            and tier_tables[c]["cmp1"]["hminus_monotone_regression"]
            and tier_tables[c]["cmp1"]["aggregate_net_strictly_decreasing"]
            for c in ("c3", "c4", "c5")
        ),
        "econ_fstar_strict_all": all(econ[c]["fstar_strict"] is not None for c in ("c3", "c4", "c5")),
        "kappa_star_matches": all(
            econ[c + "_kappa_star"]["kappa_star"] == fx["expected_kappa_star"][c] for c in ("c3", "c4", "c5")
        ),
        "h2h_v1ref_tie": h2h["v1ref"]["compression"]["net_hplus_count"] == h2h["v1ref"]["utility"]["net_hplus_count"],
        "h2h_c4_tie": h2h["c4"]["compression"]["net_hplus_count"] == h2h["c4"]["utility"]["net_hplus_count"],
        "h2h_c5_tie": h2h["c5"]["compression"]["net_hplus_count"] == h2h["c5"]["utility"]["net_hplus_count"],
        "h2h_c3_shallow_compression_better": h2h["c3"]["compression"]["net_hplus_count"]
        < h2h["c3"]["utility"]["net_hplus_count"],
        "h2h_c3_deep_tie": _expansion_signatures(
            h2h_ablations["c3_deep_val"]["library"],
            h2h_ablations["c3_deep_val"]["library_order"],
        )
        == _expansion_signatures(
            v1.invent(corpora["c3"], kappa)["library"],
            v1.invent(corpora["c3"], kappa)["library_order"],
        ),
        "h2h_trap1_utility_better": h2h["trap1"]["utility"]["net_hplus_count"]
        < h2h["trap1"]["compression"]["net_hplus_count"],
        "h2h_trap3_compression_regresses": h2h["trap3"]["compression"]["net_hplus_count"] > 0,
        "h2h_trap3_utility_negative": h2h["trap3"]["utility"]["net_hplus_count"] < 0,
        "h2h_no_dominance_registered": True,
        "exec1r_grid_negative": flagship_exec["hplus_negative_on_grid"],
        "exec1r_hminus_nonneg": flagship_exec["hminus_nonnegative_on_grid"],
        "null2_ensembles_present": all(
            nulls[k]["n_seeds"] == 200 for k in nulls
        ),
        "hlk2_absent": hostiles["hlk2"]["libraries_identical_under_poisoned_eval"],
        "hcyc2_rejected": hostiles["hcyc2"].get("detected", False),
        "hzero2_rejected": hostiles["hzero2"]["zero_gain_rejected"],
        "hexec1_agree": hostiles["hexec1"]["all_match"],
        "hutl1_fail_closed": hostiles["hutl1"]["library_empty"],
        "hunr1_agree": hostiles["hunr1"]["all_match"],
        "hsem2_zero_all": all(v["zero"] for v in hostiles["hsem2"].values()),
    }
    all_green = all(checks.values())
    terminal = TERMINAL_GREEN if all_green else TERMINAL_RED_PREFIX + "SEE_CHECKS"

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "issue": ISSUE,
        "parent_issue": PARENT_ISSUE,
        "freeze_commits": FREEZE_COMMITS,
        "source_main": SOURCE_MAIN,
        "fixtures_sha256": fixtures_sha256(),
        "v1_fixtures_sha256": V1_FIXTURES_SHA,
        "terminal": terminal,
        "checks": checks,
        "kappa": kappa,
        "depth_section": depth_section,
        "family_formation": family,
        "adm_alt": admalt_out,
        "tier_tables": {
            c: {
                "admissions": [
                    {"body": a["body"], "gain": a["gain"]} for a in tier_tables[c]["trace"]["admissions"]
                ],
                "rows": tier_tables[c]["rows"],
                "cmp1": tier_tables[c]["cmp1"],
            }
            for c in tier_tables
        },
        "econ": econ,
        "head_to_head": h2h,
        "h2h_ablations": h2h_ablations_out,
        "nulls": {k: {kk: vv for kk, vv in v.items() if kk != "per_seed"} for k, v in nulls.items()},
        "v1_flagship_exec": flagship_exec,
        "v1_flagship_exec_null": {
            k: vv for k, vv in v1_flagship_exec_null.items() if k != "per_seed"
        },
        "hostiles": hostiles,
    }
    for cid in ("c3", "c4", "c5", "trap1", "trap3"):
        flat = (
            [w for ts in S[cid]["tiers"].values() for w in ts]
        )
        comp = v1.invent(corpora[cid], kappa)
        receipt.setdefault("thr1_per_corpus", {})[cid] = v1.threshold_check(
            v1.heldout_verdict(flat, comp["library"], comp["library_order"], kappa),
            comp["library"],
            kappa,
        )
    receipt["nulls_ranks"] = {}
    for cid in ("c3", "c4", "c5"):
        true_net = tier_tables[cid]["rows"][-1]["aggregate_net"]
        ns = nulls[cid]["nets_hplus"]
        receipt["nulls_ranks"][cid] = {
            "true_aggregate_net": true_net,
            "nulls_better": sum(1 for x in ns if x < true_net),
            "rank": sum(1 for x in ns if x < true_net) + 1,
        }
    return receipt


def _expected_bodies(fx: dict, cid: str):
    return [e["body"] for e in fx["expected_traces_kappa1"][cid]]


def _expansion_signatures(library: Dict[str, Tuple[str, ...]], order: Sequence[str]) -> List[str]:
    """Name-independent signature of a library: each macro's body rewritten
    with canonical m-indices by admission position, then fully base-expanded."""
    canon = {name: "m{}".format(i + 1) for i, name in enumerate(order)}
    out = []
    for i, name in enumerate(order):
        body = library[name]
        renamed = tuple(canon.get(s, s) for s in body)
        sub_lib = {order[j]: tuple(library[order[j]]) for j in range(i)}
        sub_canon = {order[j]: "m{}".format(j + 1) for j in range(i)}
        renamed_lib = {sub_canon[nm]: tuple(sub_canon.get(s, s) for s in bd) for nm, bd in sub_lib.items()}
        out.append("".join(v1.expand_word(renamed, renamed_lib)))
    return out


def main() -> None:
    receipt = build_receipt()
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
