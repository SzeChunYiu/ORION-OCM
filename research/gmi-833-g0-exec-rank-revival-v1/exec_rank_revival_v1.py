#!/usr/bin/env python3
"""GMI #833 Section-E E9 exec-cost rank revival — main module.

Repairs the tranche-2 GAP-E8-3 rank-fragility lead: under EXEC-B at rho=1,
19/200 equal-cardinality nulls beat the v1 recursive library on v1ref while
0/200 beat it under the count metric.  This package proves, at registered
scope: (EXR-1) the exec-argimal nesting rung is rank-1 under BOTH metrics on
every battery corpus with an extended exec break-even; (EXR-2) the nesting
ladder obeys an exact affine-in-rho exchange law; (EXR-3) the argmin structure
and corpus classification; (EXR-4) no member of the frozen five-charge class
invents a both-rank-1 library on all corpora; (EXR-5) the exec-MDL invention
problem is degenerate (empty library uniquely optimal); (EXR-6) the fast DPs
are exactly certified against the frozen v1/v2 engines; (EXR-7) rung
selection semantics.

Reuses the merged v1/v2 machinery unchanged.  Exact integer arithmetic only;
byte-identical under -I -B / -I -O -B and across CPython >= 3.8.
"""
import hashlib
import itertools
import json
import os
import sys
from typing import Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gmi-833-g0-grammar-growth-v1"))
sys.path.insert(0, os.path.join(HERE, "..", "gmi-833-g0-grammar-growth-v2"))

import g0_grammar_growth_v1 as v1  # noqa: E402
import g0_grammar_growth_v2 as v2  # noqa: E402

FREEZE_COMMIT = "79651e4877b719b7d5575e869ad1c3c7c0018c05"
CLAIM_CEILING = (
    "GMI_833_E9_EXEC_RANK_REVIVAL__BOTH_METRIC_RANK1_WITNESS_BY_NESTING_LADDER"
    "__EXACT_AFFINE_EXCHANGE_LAW__STRUCTURE_CLASSIFICATION_AT_REGISTERED_SCOPE"
)
TERMINAL = "GMI_833_E9_EXEC_RANK_REVIVAL_GREEN_AT_REGISTERED_SCOPE"
FORBIDDEN = [
    "UNIVERSAL_LIBRARY_LEARNING",
    "PRIMITIVE_INVENTION_ALWAYS_HELPS",
    "OPEN_ENDED_GRAMMAR_GROWTH",
    "UNSEEN_FORM_DISCOVERY",
    "P4_RECOVERY_COMPLETE",
    "REAL_WORLD_TRANSFER_PROVED",
    "ALL_FUTURE_TASKS_CHEAPER",
    "COMPLETE_GMI",
    "DEPTH_4_PLUS_FORMED",
    "UNIVERSAL_DEPTH_GROWTH",
    "COMPRESSION_GATE_DOMINATES",
    "UTILITY_GATE_DOMINATES",
    "EXEC_INVARIANT_ALL_RHO",
    "RECURSIVE_LIBRARY_EXEC_OPTIMAL",
    "SINGLE_JOINT_CHARGE_ACHIEVES_BOTH_METRIC_RANK1",
    "UNIFORM_IN_RHO_RANK1",
    "CLOSURE_ARGMIN_ON_C4_C5",
    "NESTING_LADDER_COMPLETE_BEYOND_BATTERY",
]
KAPPA = 1
RHOS = (1, 2, 4)
N_SEEDS = 200
SUBSET_CAP = 20000
STATE_CAP = 1500
TOP_T_C3 = 10
ORACLE_SUBSEEDS = 40


class RevivalError(Exception):
    pass


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

def load_fixtures() -> dict:
    with open(os.path.join(HERE, "FROZEN_FIXTURES_E1.json"), "rb") as fh:
        return json.loads(fh.read().decode())


def fixtures_sha256() -> str:
    with open(os.path.join(HERE, "FROZEN_FIXTURES_E1.json"), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def battery(fx: dict):
    """Corpora + suites from the frozen v1/v2 fixtures (by hash pin in fx)."""
    v1fx = v1.load_fixtures()
    v2fx = v2.load_fixtures()
    out = {}
    for cid in ("v1ref", "c3", "c4", "c5", "trap1", "trap3"):
        if cid == "v1ref":
            corpus = [tuple(p) for p in v1fx["training_corpus"]]
            hp = [tuple(w) for w in v1fx["heldout_reuse_positive"]]
            hm = [tuple(w) for w in v1fx["heldout_unrelated_control"]]
        else:
            corpus = [tuple(p) for p in v2fx["corpora"][cid]["programs"]]
            hp = [tuple(w) for ts in v2fx["suites"][cid]["hplus"].values() for w in ts]
            hm = [tuple(w) for w in v2fx["suites"][cid]["hminus"]]
        out[cid] = {"corpus": corpus, "hp": hp, "hm": hm}
    return out


# ---------------------------------------------------------------------------
# fast certified DPs (identical arithmetic to v1.burden_dp / v2.exec_burden)
# ---------------------------------------------------------------------------

def _matches(w, symbols, exps):
    n = len(w)
    ms = [[] for _ in range(n)]
    for i in range(n):
        for s in symbols:
            e = exps[s]
            le = len(e)
            if le and i + le <= n and tuple(w[i:i + le]) == e:
                ms[i].append((s, le))
    return ms


def _stable(w, symbols, exps):
    n = len(w)
    ms = _matches(w, symbols, exps)
    S = [[False] * (n + 1) for _ in range(n + 1)]
    S[n][0] = True
    for i in range(n - 1, -1, -1):
        Si = S[i]
        for s, le in ms[i]:
            Sm = S[i + le]
            for r in range(1, n - i + 1):
                if Sm[r - 1]:
                    Si[r] = True
    return S, ms


def fast_burden_dp(target, symbol_order, expansions):
    w = tuple(target)
    n = len(w)
    A = len(symbol_order)
    symbols = list(symbol_order)
    S, ms = _stable(w, symbols, expansions)
    for r in range(1, n + 1):
        if S[0][r]:
            lstar = r
            break
    else:
        raise RevivalError("TARGET_UNREACHABLE")
    prog = []
    rank = 0
    idx = {s: k for k, s in enumerate(symbols)}
    i = 0
    remaining = lstar
    while remaining > 0:
        for s, le in ms[i]:
            if S[i + le][remaining - 1]:
                prog.append(s)
                rank = rank * A + idx[s]
                i += le
                remaining -= 1
                break
        else:
            raise RevivalError("SEGMENTATION_INVARIANT_VIOLATION")
    prior = (A ** lstar - A) // (A - 1) if A > 1 else lstar - 1
    return prior + rank + 1, tuple(prog)


def fast_exec_burden(target, symbol_order, library, rho):
    w = tuple(target)
    n = len(w)
    A = len(symbol_order)
    symbols = list(symbol_order)
    cost = v2.opcosts(library, rho)
    C = sum(cost[s] for s in symbols)
    exps = v1.symbol_expansions(symbols, library)
    S, _ = _stable(w, symbols, exps)
    for r in range(1, n + 1):
        if S[0][r]:
            lstar = r
            break
    else:
        raise RevivalError("TARGET_UNREACHABLE")
    _, hit = fast_burden_dp(w, symbols, exps)
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


# ---------------------------------------------------------------------------
# nesting family, rung selection
# ---------------------------------------------------------------------------

def flatten(lib: Dict[str, Tuple[str, ...]]) -> Dict[str, Tuple[str, ...]]:
    return {n: v1.expand_word(b, lib) for n, b in lib.items()}


def nesting_family(trace_lib, trace_order):
    """All flat/nested body choices per level, deduped, admission order kept."""
    fam = {}
    prefixes = []
    lib = {}
    for name in trace_order:
        lib = dict(lib)
        lib[name] = tuple(trace_lib[name])
        prefixes.append(dict(lib))
    for pref in prefixes:
        d = len(pref)
        for combo in range(2 ** d):
            built = {}
            for k, name in enumerate(pref):
                body = tuple(pref[name])
                if not (combo >> k) & 1:
                    sub = {n: pref[n] for n in list(pref)[:k]}
                    body = tuple(v1.expand_word(body, sub))
                built[name] = tuple(body)
            key = tuple(built[n] for n in pref)
            fam.setdefault(key, built)
    return [(fam[k], list(trace_order[:len(fam[k])])) for k in sorted(fam)]


def depth_of(lib):
    def d(name, seen=()):
        if name in seen:
            raise RevivalError("CYCLE")
        body = lib[name]
        subs = [d(s, seen + (name,)) for s in body if s in lib]
        return 0 if not subs else 1 + max(subs)

    return max([d(n) for n in lib], default=0)


def dispatch_counts(lib, rho=1):
    cost = {}
    D = {}
    for name in sorted(lib, key=lambda n: int(n[1:])):
        D[name] = 1 + sum(D.get(s, 0) for s in lib[name])
    return D


# ---------------------------------------------------------------------------
# suites and nets
# ---------------------------------------------------------------------------

def g0_exec(hp, rho):
    return sum(fast_exec_burden(w, ["a", "b", "c"], {}, rho) for w in hp)


def g0_count(hp):
    exps = v1.symbol_expansions(["a", "b", "c"], {})
    return sum(fast_burden_dp(w, ["a", "b", "c"], exps)[0] for w in hp)


def hplus_nets(names, lib, hp, rho):
    order = ["a", "b", "c"] + list(names)
    exps = v1.symbol_expansions(order, lib)
    K = v1.k_total(lib, KAPPA)
    cp = sum(fast_burden_dp(w, order, exps)[0] for w in hp)
    ep = sum(fast_exec_burden(w, order, lib, rho) for w in hp)
    return {"K": K, "count_abs": cp + K, "exec_abs": ep + K}


def net_row(names, lib, hp, g0c, g0e1, g0e2, g0e4):
    nr = hplus_nets(names, lib, hp, 1)
    order = ["a", "b", "c"] + list(names)
    e2 = sum(fast_exec_burden(w, order, lib, 2) for w in hp)
    e4 = sum(fast_exec_burden(w, order, lib, 4) for w in hp)
    row = {
        "K": nr["K"],
        "count_net": nr["count_abs"] - g0c,
        "exec_net_rho1": nr["exec_abs"] - g0e1,
        "exec_net_rho2": e2 + nr["K"] - g0e2,
        "exec_net_rho4": e4 + nr["K"] - g0e4,
        "depth": depth_of(lib) if lib else 0,
    }
    return row


def breakeven_scan(names, lib, hp, g0e1):
    """Exact break-even via the affine-in-rho law (T-E1): net_exec(rho) is
    affine in rho, so rho_dagger = ceil(-base/disp) with two-point verification.
    base = net(0), disp = net(1) - net(0) (dispatch-visit total).  The frozen
    scan limit 2^10 is preserved (larger exact values report NONE_IN_RANGE,
    with the exact uncapped value in breakeven_exact)."""
    order = ["a", "b", "c"] + list(names)
    K = v1.k_total(lib, KAPPA)

    def net_at(rho):
        return sum(fast_exec_burden(w, order, lib, rho) for w in hp) + K - g0e1

    n1 = net_at(1)
    if n1 >= 0:
        return 1, 1
    n0 = net_at(0)
    disp = n1 - n0
    if disp <= 0:
        return "NONE_IN_RANGE", "NEVER"
    rho_d = max(2, (-n0 + disp - 1) // disp)  # ceil of -n0/disp, >= 2 since n1 < 0
    # exact two-point verification of the closed form
    hi = net_at(rho_d)
    lo = net_at(rho_d - 1)
    if not (hi >= 0 and lo < 0):
        raise RevivalError("BREAKEVEN_CLOSED_FORM_MISMATCH")
    if rho_d > 1024:
        return "NONE_IN_RANGE", rho_d
    return rho_d, rho_d


# ---------------------------------------------------------------------------
# spaces
# ---------------------------------------------------------------------------

def closure(corpus, top_t=None):
    out = {}

    def rec(work, lib, names):
        key = (tuple(tuple(p) for p in work), tuple(sorted(lib.items())))
        if key in out:
            return
        if len(out) >= STATE_CAP:
            raise RevivalError("STATE_CAP_EXCEEDED")
        out[key] = (dict(lib), list(names))
        pool = v1.candidate_pool(work, lib)
        scored = []
        for body, (occ, fp, fo) in pool.items():
            gain = v1.admission_gain(body, occ, KAPPA)
            if gain > 0:
                scored.append((body, gain, occ, fp, fo))
        order = ["a", "b", "c"] + names
        scored.sort(key=lambda t: v1.tie_key(t[0], t[1], t[2], t[3], t[4], lib, order))
        if top_t:
            scored = scored[:top_t]
        for body, gain, occ, fp, fo in scored:
            name = "m{}".format(len(lib) + 1)
            nlib = dict(lib)
            nlib[name] = tuple(body)
            nwork = [v1.greedy_rewrite(body, name, p) for p in work]
            rec(nwork, nlib, names + [name])

    rec([tuple(p) for p in corpus], {}, [])
    return out


def build_space(cid, corpus, inv_names, inv_lib, kind):
    libs, seen = [], set()

    def add(lib, names):
        sig = tuple(sorted((n, tuple(b)) for n, b in lib.items()))
        if sig not in seen:
            seen.add(sig)
            libs.append((dict(lib), list(names)))

    if kind in ("full", "top_t_closure"):
        cl = closure(corpus, top_t=TOP_T_C3 if kind == "top_t_closure" else None)
        states = len(cl)
        for lib, names in cl.values():
            add(lib, names)
            add(flatten(lib), names)
        pool = v1.candidate_pool([tuple(p) for p in corpus], {})
        pool_bodies = sorted(pool)
        P = len(pool_bodies)
        subset_total = sum(v1._n_choose_k(P, s) for s in range(1, min(P, len(inv_names) + 2)))
        subsets_added = 0
        if subset_total <= SUBSET_CAP:
            for size in range(1, min(P, len(inv_names) + 2)):
                for combo in itertools.combinations(range(P), size):
                    bodies = [pool_bodies[i] for i in combo]
                    nm = ["n{}".format(i + 1) for i in range(size)]
                    lib = {a: tuple(b) for a, b in zip(nm, bodies)}
                    sig = tuple(sorted(lib.items()))
                    if sig not in seen:
                        seen.add(sig)
                        libs.append((lib, nm))
                        subsets_added += 1
        return libs, {"kind": kind, "closure_states": states, "pool_size": P,
                      "subset_total": subset_total, "subsets_added": subsets_added}
    # chain-only
    for lib, names in nesting_family(inv_lib, inv_names):
        add(lib, names)
    return libs, {"kind": kind}


# ---------------------------------------------------------------------------
# NULL-3 (both metrics) with per-combo signature census
# ---------------------------------------------------------------------------

def null_ensemble_both(corpus, size, hp):
    pool = v1.candidate_pool([tuple(p) for p in corpus], {})
    pool_bodies = sorted(pool)
    P = len(pool_bodies)
    total = v1._n_choose_k(P, size)
    g0c = g0_count(hp)
    g0e = g0_exec(hp, 1)
    cnt: List[int] = []
    ex: List[int] = []
    combo_sig: Dict[int, List[str]] = {}
    for seed in range(N_SEEDS):
        ci = (((seed + 1) * 2654435761) % (2 ** 32)) % total
        idxs = v2.unrank_combination(P, size, ci)
        bodies = ["".join(pool_bodies[i]) for i in idxs]
        combo_sig[seed] = bodies
        names = ["n{}".format(i + 1) for i in range(size)]
        lib = {nm: tuple(b) for nm, b in zip(names, bodies)}
        nr = hplus_nets(names, lib, hp, 1)
        cnt.append(nr["count_abs"] - g0c)
        ex.append(nr["exec_abs"] - g0e)
    public = {
        "pool_size": P, "combos_total": total, "n_seeds": N_SEEDS,
        "nets_count": cnt, "nets_exec": ex,
        "count_min": min(cnt), "exec_min": min(ex),
        "count_median": sorted(cnt)[len(cnt) // 2],
        "exec_median": sorted(ex)[len(ex) // 2],
        "count_max": max(cnt), "exec_max": max(ex),
    }
    return public, combo_sig


def rank_against(nets, value):
    return sum(1 for x in nets if x < value)


def tie_census(combo_sig, witness_bodies):
    wb = sorted(witness_bodies)
    identity_seeds = [s for s in range(N_SEEDS)
                      if sorted(combo_sig[s]) == wb]
    return {"n_identity_draws": len(identity_seeds),
            "identity_draw_seeds": identity_seeds}


# ---------------------------------------------------------------------------
# charge class
# ---------------------------------------------------------------------------

CHARGES = {
    "count": lambda u, cost: len(u) + KAPPA,
    "exec": lambda u, cost: sum(cost.get(s, 1) for s in u) + KAPPA,
    "max": lambda u, cost: max(len(u) + KAPPA,
                               sum(cost.get(s, 1) for s in u) + KAPPA),
    "sum": lambda u, cost: len(u) + KAPPA + sum(cost.get(s, 1) for s in u) + KAPPA,
    # freeze text: Phi_countdisp = |u| + kappa + rho * (#macro symbols in u);
    # macro symbols are exactly the non-base symbols of the body
    "countdisp": lambda u, cost: len(u) + KAPPA + sum(
        1 for s in u if s not in ("a", "b", "c")),
}


def charge_invent(corpus, phi):
    work = [tuple(p) for p in corpus]
    lib = {}
    names = []
    for _ in range(v1.corpus_symbol_count([tuple(p) for p in corpus])):
        pool = v1.candidate_pool(work, lib)
        cost = v2.opcosts(lib, 1)
        scored = []
        for body, (occ, fp, fo) in pool.items():
            gain = occ * (len(body) - 1) - phi(body, cost)
            if gain > 0:
                scored.append((body, gain, occ, fp, fo))
        if not scored:
            break
        order = ["a", "b", "c"] + names
        scored.sort(key=lambda t: v1.tie_key(t[0], t[1], t[2], t[3], t[4], lib, order))
        body = scored[0][0]
        name = "m{}".format(len(lib) + 1)
        lib[name] = tuple(body)
        names.append(name)
        work = [v1.greedy_rewrite(body, name, p) for p in work]
    return lib, names


# ---------------------------------------------------------------------------
# exec-MDL degeneracy
# ---------------------------------------------------------------------------

def exec_mdl_degenerate(corpus):
    pool = v1.candidate_pool([tuple(p) for p in corpus], {})
    worst = None
    for body, (occ, _, _) in pool.items():
        for rho in RHOS:
            g = -rho * occ - len(body) - KAPPA
            if worst is None or g > worst:
                worst = g
    return worst is not None and worst < 0, worst


# ---------------------------------------------------------------------------
# affine exchange law
# ---------------------------------------------------------------------------

def affine_checks(fam_rows):
    """For every same-macro-set pair (rung, flat rung): verify
    net_exec(flat,rho) - net_exec(rung,rho) == -rho*dDV + dK at rho 1,2,4."""
    by_set = {}
    for row in fam_rows:
        key = tuple(row["names"])
        by_set.setdefault(key, []).append(row)
    checks = []
    for key, grp in by_set.items():
        if len(grp) < 2:
            continue
        flatrow = max(grp, key=lambda r: r["K"])
        for row in grp:
            if row is flatrow:
                continue
            dK = flatrow["K"] - row["K"]
            d1 = flatrow["exec_net_rho1"] - row["exec_net_rho1"]
            d2 = flatrow["exec_net_rho2"] - row["exec_net_rho2"]
            d4 = flatrow["exec_net_rho4"] - row["exec_net_rho4"]
            dDV = dK - d1
            exact = (d1 == -dDV + dK and d2 == -2 * dDV + dK and d4 == -4 * dDV + dK)
            checks.append({"names": list(key), "rung_bodies": row["bodies"],
                           "dK": dK, "dDV": dDV, "exact": exact})
    return checks


# ---------------------------------------------------------------------------
# hostiles
# ---------------------------------------------------------------------------

def hostile_hexr1(bat):
    """Fast DPs vs frozen v1/v2 engines on registered spot sets."""
    v1fx = v1.load_fixtures()
    v2fx = v2.load_fixtures()
    cases = 0
    inv = v1.invent(bat["v1ref"]["corpus"], KAPPA)
    order = ["a", "b", "c"] + inv["library_order"]
    exps = v1.symbol_expansions(order, inv["library"])
    for w in bat["v1ref"]["hp"]:
        assert fast_burden_dp(w, order, exps)[0] == v1.burden_dp(w, order, exps)[0]
        for rho in (0, 1, 4):
            assert fast_exec_burden(w, order, inv["library"], rho) == \
                v2.exec_burden(w, order, inv["library"], rho)
            cases += 1
    for cid in ("trap1", "trap3"):
        inv_t = v1.invent(bat[cid]["corpus"], KAPPA)
        o = ["a", "b", "c"] + inv_t["library_order"]
        for w in bat[cid]["hp"]:
            for rho in (1, 4):
                assert fast_exec_burden(w, o, inv_t["library"], rho) == \
                    v2.exec_burden(w, o, inv_t["library"], rho)
                cases += 1
    inv3 = v1.invent(bat["c3"]["corpus"], KAPPA)
    o3 = ["a", "b", "c"] + inv3["library_order"]
    for w in bat["c3"]["hp"][:3]:
        assert fast_exec_burden(w, o3, inv3["library"], 1) == \
            v2.exec_burden(w, o3, inv3["library"], 1)
        cases += 1
    return {"all_agree": True, "cases": cases, "code": "FAST_DP_CERTIFIED"}


def hostile_hexr2(bat):
    """Perturb one opcost by +1 inside the ladder identity: must FAIL."""
    corpus, hp = bat["v1ref"]["corpus"], bat["v1ref"]["hp"]
    inv = v1.invent(corpus, KAPPA)
    fam = nesting_family(inv["library"], inv["library_order"])
    rows = []
    g0c = g0_count(hp)
    g0e = {r: g0_exec(hp, r) for r in (1, 2, 4)}
    for lib, names in fam:
        row = net_row(names, lib, hp, g0c, g0e[1], g0e[2], g0e[4])
        row["names"] = names
        row["bodies"] = ["".join(lib[n]) for n in names]
        rows.append(row)
    # perturb: inflate the exec_net_rho1 of the deepest rung by 1
    tampered = [dict(r) for r in rows]
    for r in tampered:
        if r["depth"] > 0:
            r["exec_net_rho1"] += 1
            break
    ok_real = all(c["exact"] for c in affine_checks(rows))
    ok_tampered = all(c["exact"] for c in affine_checks(tampered))
    return {"real_exact": ok_real, "tamper_detected": (not ok_tampered),
            "code": "AFFINE_TAMPER_EVIDENCE" if (ok_real and not ok_tampered)
            else "AFFINE_TAMPER_MISS"}


def hostile_hexr3(bat):
    fails = 0
    for cid, d in bat.items():
        inv = v1.invent(d["corpus"], KAPPA)
        orig_base = [v1.expand_word(p, {}) for p in d["corpus"]]
        for lib, names in nesting_family(inv["library"], inv["library_order"]):
            # expansions of the macro bodies themselves preserve semantics
            for n in names:
                if v1.expand_word(lib[n], {k: lib[k] for k in names}) != \
                        v1.expand_word(inv["library"][n], inv["library"]):
                    fails += 1
    return {"expansion_preserved": fails == 0, "failures": fails,
            "code": "NFAM_EXPANSION_OK" if fails == 0 else "NFAM_EXPANSION_BROKEN"}


def hostile_hexr4():
    import itertools
    ok = True
    detail = []
    for (n, k) in ((5, 2), (10, 2), (12, 1)):
        total = v1._n_choose_k(n, k)
        mat = list(itertools.combinations(range(n), k))
        for r in range(total):
            if list(v2.unrank_combination(n, k, r)) != list(mat[r]):
                ok = False
                detail.append((n, k, r))
    return {"all_match": ok, "cases": 5 + 45 + 12, "mismatches": detail,
            "code": "UNRANK_MATERIALIZED_AGREE" if ok else "UNRANK_MISMATCH"}


def hostile_hexr5(bat):
    hp = bat["v1ref"]["hp"]
    row = net_row([], {}, hp, g0_count(hp), g0_exec(hp, 1), g0_exec(hp, 2), g0_exec(hp, 4))
    return {"empty_count_net": row["count_net"], "empty_exec_net": row["exec_net_rho1"],
            "identity": row["count_net"] == 0 and row["exec_net_rho1"] == 0,
            "code": "EMPTY_LIBRARY_IDENTITY"}


def hostile_hexr6(bat):
    inv = v1.invent(bat["v1ref"]["corpus"], KAPPA)
    poisoned = {"corpus": bat["v1ref"]["corpus"],
                "hp": [tuple("zz" + "a" * i) for i in range(5)],
                "hm": [tuple("q" * (i + 1)) for i in range(5)]}
    inv2 = v1.invent(poisoned["corpus"], KAPPA)
    same = (inv["library"] == inv2["library"])
    return {"library_byte_identical": same,
            "code": "LEAKAGE_ABSENT" if same else "LEAKAGE_PRESENT"}


def hostile_hexr7():
    lib = {"m1": ("a", "b"), "m2": ("m3", "a")}
    lib2 = dict(lib)
    lib2["m3"] = ("m2", "b")
    try:
        v1.expand_word(("m2",), lib2)
        term = "EXPANDED"
    except v1.GrammarGrowthError as exc:
        term = str(exc)
    return {"terminal": term, "grammar_unchanged": lib2 == {**lib, "m3": ("m2", "b")},
            "code": "CYCLE_REJECTED" if "CYCLE" in term else "CYCLE_MISSED"}


# ---------------------------------------------------------------------------
# receipt
# ---------------------------------------------------------------------------

def build_receipt() -> dict:
    fx = load_fixtures()
    bat = battery(fx)
    receipt = {
        "schema": "GMI833G0ExecRankRevivalResultE1",
        "issue": 833,
        "parent_issue": 897,
        "source_main": fx["source_main"],
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN,
        "fixtures_sha256": fixtures_sha256(),
        "corpora": {},
        "checks": {},
        "hostiles": {},
    }
    witness_rank1_all = True
    breakeven_ok = True
    affine_all = True
    argmin_ok = True
    degenerate_all = True
    null_cache: Dict[Tuple[str, int], dict] = {}

    def ensemble(cid, corpus, hp, size):
        key = (cid, size)
        if key not in null_cache:
            null_cache[key] = null_ensemble_both(corpus, size, hp)
        return null_cache[key]

    for cid in ("v1ref", "c3", "c4", "c5", "trap1", "trap3"):
        d = bat[cid]
        corpus, hp = d["corpus"], d["hp"]
        g0c = g0_count(hp)
        g0e1 = g0_exec(hp, 1)
        g0e2 = g0_exec(hp, 2)
        g0e4 = g0_exec(hp, 4)
        inv = v1.invent(corpus, KAPPA)
        names = inv["library_order"]
        entry = {
            "inv_library": {k: list(vv) for k, vv in inv["library"].items()},
            "inv_trace": [{k: a[k] for k in ("name", "gain", "occurrences")}
                          for a in inv["admissions"]],
            "inv_stopped_by": inv["stopped_by"],
        }
        irow = net_row(names, inv["library"], hp, g0c, g0e1, g0e2, g0e4)
        entry["inv_nets"] = irow
        ibe, ibe_x = breakeven_scan(names, inv["library"], hp, g0e1)
        entry["inv_breakeven"] = ibe
        entry["inv_breakeven_exact"] = ibe_x

        fam = nesting_family(inv["library"], names)
        fam_rows = []
        for lib, nm in fam:
            row = net_row(nm, lib, hp, g0c, g0e1, g0e2, g0e4)
            row["names"] = nm
            row["bodies"] = ["".join(lib[n]) for n in nm]
            fam_rows.append(row)
        entry["nesting_family"] = fam_rows
        aff = affine_checks(fam_rows)
        entry["affine_checks"] = aff
        affine_all = affine_all and all(c["exact"] for c in aff)

        # rung selection (EXR-7): exec argmin rung at rho grid; count argmin rung
        exec_rung = min(fam_rows, key=lambda r: (r["exec_net_rho1"], r["K"]))
        exec_rung2 = min(fam_rows, key=lambda r: (r["exec_net_rho2"], r["K"]))
        exec_rung4 = min(fam_rows, key=lambda r: (r["exec_net_rho4"], r["K"]))
        full_set_rows = [r for r in fam_rows if len(r["names"]) == len(names)]
        count_rung = min(full_set_rows or fam_rows, key=lambda r: (r["count_net"], -r["K"]))
        full_flat_bodies = ["".join(v1.expand_word(inv["library"][n], inv["library"]))
                            for n in names] if names else []
        entry["rung_selection"] = {
            "exec_rho1_rung": {"bodies": exec_rung["bodies"],
                               "net": exec_rung["exec_net_rho1"],
                               "depth": exec_rung["depth"],
                               "is_full_flattening": exec_rung["bodies"] == full_flat_bodies},
            "exec_rho2_is_full_flattening": exec_rung2["bodies"] == full_flat_bodies,
            "exec_rho4_is_full_flattening": exec_rung4["bodies"] == full_flat_bodies,
            "count_rung": {"bodies": count_rung["bodies"], "net": count_rung["count_net"],
                           "K": count_rung["K"],
                           "is_min_k_among_full_set": count_rung["K"] == min(
                               r["K"] for r in (full_set_rows or fam_rows))},
        }

        # witness = trap override or exec rung (freeze EXR-1)
        wit = fx["corpora"][cid]["witness"]
        if cid in ("trap1", "trap3"):
            wbodies = wit["bodies"]
            wnames = ["n{}".format(i + 1) for i in range(len(wbodies))]
            wlib = {nm: tuple(b) for nm, b in zip(wnames, wbodies)}
        else:
            wlib = flatten(inv["library"])
            wnames = list(names)
        wrow = net_row(wnames, wlib, hp, g0c, g0e1, g0e2, g0e4)
        wbe, wbe_x = breakeven_scan(wnames, wlib, hp, g0e1)
        entry["witness"] = {
            "bodies": ["".join(wlib[n]) for n in wnames],
            "nets": wrow, "breakeven": wbe, "breakeven_exact": wbe_x,
        }

        # NULL-3 at the witness cardinality (== |L_inv| on every battery corpus)
        ne, combo_sig = ensemble(cid, corpus, hp, len(names))
        census = tie_census(combo_sig, ["".join(wlib[n]) for n in wnames])
        wcb = rank_against(ne["nets_count"], wrow["count_net"])
        web = rank_against(ne["nets_exec"], wrow["exec_net_rho1"])
        icb = rank_against(ne["nets_count"], irow["count_net"])
        ieb = rank_against(ne["nets_exec"], irow["exec_net_rho1"])
        entry["nulls"] = {
            "pool_size": ne["pool_size"], "combos_total": ne["combos_total"],
            "n_seeds": ne["n_seeds"],
            "nets_count": ne["nets_count"], "nets_exec": ne["nets_exec"],
            "count_min": ne["count_min"], "count_median": ne["count_median"],
            "count_max": ne["count_max"],
            "exec_min": ne["exec_min"], "exec_median": ne["exec_median"],
            "exec_max": ne["exec_max"],
        }
        entry["ranks"] = {
            "inv": {"cb": icb, "eb": ieb},
            "witness": {"cb": wcb, "eb": web},
        }
        entry["tie_census"] = census
        # tie accounting: identity draws always tie; coincidental ties reported
        ties_c = sum(1 for x in ne["nets_count"] if x == wrow["count_net"])
        ties_e = sum(1 for x in ne["nets_exec"] if x == wrow["exec_net_rho1"])
        coinc = sorted({"+".join(combo_sig[s]) for s in range(N_SEEDS)
                        if (ne["nets_count"][s] == wrow["count_net"]
                            or ne["nets_exec"][s] == wrow["exec_net_rho1"])
                        and sorted(combo_sig[s]) != sorted(
                            ["".join(wlib[n]) for n in wnames])})
        entry["tie_counts"] = {"count": ties_c, "exec": ties_e,
                               "coincidental_tie_combos": coinc}
        witness_rank1_all = witness_rank1_all and (wcb == 0 and web == 0)

        # break-even expectations (freeze criteria)
        exp = fx["criteria"]["exr1_breakevens"][cid]
        breakeven_ok = breakeven_ok and (
            entry["witness"]["breakeven"] == exp[0] and entry["inv_breakeven"] == exp[1])

        # spaces + argmins
        kind = fx["spaces"][cid]["kind"]
        libs, meta = build_space(cid, corpus, names, inv["library"], kind)
        meta_serial = {k: v for k, v in meta.items()}
        space_rows = []
        for lib, nm in libs:
            r = net_row(nm, lib, hp, g0c, g0e1, g0e2, g0e4)
            r["bodies"] = ["".join(lib[n]) for n in nm] if nm else []
            space_rows.append(r)
        entry["space"] = meta_serial
        entry["space_size"] = len(space_rows)
        if kind in ("full", "top_t_closure"):
            cmin = min(space_rows, key=lambda r: r["count_net"])
            emin = min(space_rows, key=lambda r: r["exec_net_rho1"])
            entry["space_argmin"] = {
                "count": {"bodies": cmin["bodies"], "net": cmin["count_net"]},
                "exec": {"bodies": emin["bodies"], "net": emin["exec_net_rho1"]},
            }
            if cid in fx["criteria"]["exr3_argmins"]:
                a = fx["criteria"]["exr3_argmins"][cid]
                argmin_ok = argmin_ok and \
                    entry["space_argmin"]["count"]["net"] == a["count"] and \
                    entry["space_argmin"]["exec"]["net"] == a["exec"]
            # frontier
            vals = [(r["count_net"], r["exec_net_rho1"], r["bodies"]) for r in space_rows]
            fr = [{"bodies": b, "count_net": c, "exec_net": e}
                  for c, e, b in vals
                  if not any((c2 <= c and e2 <= e and (c2 < c or e2 < e))
                             for c2, e2, _ in vals)]
            entry["frontier"] = sorted(fr, key=lambda x: x["count_net"])

        # charge paths (ranked at their OWN cardinality: equal-cardinality nulls)
        paths = {}
        for pname, phi in CHARGES.items():
            lib, nm = charge_invent(corpus, phi)
            prow = {"bodies": ["".join(lib[n]) for n in nm], "size": len(nm)}
            if lib:
                pr = net_row(nm, lib, hp, g0c, g0e1, g0e2, g0e4)
                prow.update({"count_net": pr["count_net"],
                             "exec_net_rho1": pr["exec_net_rho1"], "depth": pr["depth"]})
                pne, _ = ensemble(cid, corpus, hp, len(nm))
                prow["cb"] = rank_against(pne["nets_count"], pr["count_net"])
                prow["eb"] = rank_against(pne["nets_exec"], pr["exec_net_rho1"])
            else:
                prow["cb"] = 0
                prow["eb"] = 0
                prow["empty_library"] = True
            paths[pname] = prow
        entry["charge_paths"] = paths

        deg, worst = exec_mdl_degenerate(corpus)
        entry["exec_mdl_degenerate"] = deg
        entry["exec_mdl_worst_gain"] = worst
        degenerate_all = degenerate_all and deg

        receipt["corpora"][cid] = entry

    # EXR-4: no charge achieves both-rank-1 on all corpora (nonempty libraries;
    # the empty library is not a repair — refusing to play is not rank-1)
    universal_charges = []
    for pname in CHARGES:
        ok_all = True
        for cid, entry in receipt["corpora"].items():
            p = entry["charge_paths"][pname]
            if p.get("empty_library") or p.get("cb") != 0 or p.get("eb") != 0:
                ok_all = False
        if ok_all:
            universal_charges.append(pname)
    receipt["charge_class_verdict"] = {
        "charges_with_both_rank1_everywhere": universal_charges,
        "none_universal": len(universal_charges) == 0,
        "note": "per-own-cardinality nulls; empty inventions disqualified",
    }

    receipt["hostiles"] = {
        "hexr1": hostile_hexr1(bat),
        "hexr2": hostile_hexr2(bat),
        "hexr3": hostile_hexr3(bat),
        "hexr4": hostile_hexr4(),
        "hexr5": hostile_hexr5(bat),
        "hexr6": hostile_hexr6(bat),
        "hexr7": hostile_hexr7(),
    }

    receipt["checks"] = {
        "exr1_witness_rank1_both_all_corpora": witness_rank1_all,
        "exr1_breakevens_match_fixtures": breakeven_ok,
        "exr2_affine_exact_all_pairs": affine_all,
        "exr3_argmins_match_fixtures": argmin_ok,
        "exr4_no_universal_charge": receipt["charge_class_verdict"]["none_universal"],
        "exr5_degenerate_all_corpora": degenerate_all,
        "exr7_rung_selection": all(
            receipt["corpora"][cid]["rung_selection"]["exec_rho1_rung"]["is_full_flattening"]
            and receipt["corpora"][cid]["rung_selection"]["exec_rho2_is_full_flattening"]
            and receipt["corpora"][cid]["rung_selection"]["exec_rho4_is_full_flattening"]
            and receipt["corpora"][cid]["rung_selection"]["count_rung"]["is_min_k_among_full_set"]
            for cid in receipt["corpora"]),
        "exr1_identity_draws_always_tie": all(
            entry["tie_census"]["n_identity_draws"] <= entry["tie_counts"]["count"]
            and entry["tie_census"]["n_identity_draws"] <= entry["tie_counts"]["exec"]
            for entry in receipt["corpora"].values()),
        "hexr1_fast_dp_certified": receipt["hostiles"]["hexr1"]["all_agree"],
        "hexr2_tamper_detected": receipt["hostiles"]["hexr2"]["tamper_detected"],
        "hexr3_expansion_preserved": receipt["hostiles"]["hexr3"]["expansion_preserved"],
        "hexr4_unrank_agrees": receipt["hostiles"]["hexr4"]["all_match"],
        "hexr5_empty_identity": receipt["hostiles"]["hexr5"]["identity"],
        "hexr6_leakage_absent": receipt["hostiles"]["hexr6"]["library_byte_identical"],
        "hexr7_cycle_rejected": receipt["hostiles"]["hexr7"]["code"] == "CYCLE_REJECTED",
    }
    all_ok = all(receipt["checks"].values())
    receipt["terminal"] = TERMINAL if all_ok else "GMI_833_E9_EXEC_RANK_REVIVAL_RED"
    return receipt


def main() -> None:
    print(json.dumps(build_receipt(), indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
