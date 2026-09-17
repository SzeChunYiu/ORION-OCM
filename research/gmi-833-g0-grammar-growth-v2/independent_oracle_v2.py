#!/usr/bin/env python3
"""Independent oracle for the tranche-2 receipt.

Imports NEITHER g0_grammar_growth_v1 NOR g0_grammar_growth_v2: every quantity
is recomputed from the frozen fixtures with independently written code
(iterative expansion, top-down memoized burden, recursive prefix-sum exec
burden, independent combinadic unranking). Prints a JSON verdict comparing
against RESULT_V2.json in this directory; exit 0 iff all_ok.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
V1_DIR = ROOT.parent / "gmi-833-g0-grammar-growth-v1"
FIXTURES = ROOT / "FROZEN_FIXTURES_V2.json"
RESULT = ROOT / "RESULT_V2.json"

BASE = ("a", "b", "c")


# ---------------------------------------------------------------------------
# core rewriting machinery (independent)
# ---------------------------------------------------------------------------

def expand(word, library):
    """Iterative stack expansion; cycles fail closed."""
    out = []
    stack = [(s, frozenset()) for s in reversed(list(word))]
    while stack:
        sym, inprog = stack.pop()
        if sym in BASE:
            out.append(sym)
            continue
        if sym in inprog:
            raise ValueError("RECURSIVE_LIBRARY_CYCLE")
        if sym not in library:
            raise ValueError("UNKNOWN_SYMBOL")
        stack.extend((s, inprog | {sym}) for s in reversed(library[sym]))
    return tuple(out)


def gcount(sub, prog):
    n, m = len(prog), len(sub)
    if m == 0 or m > n:
        return 0
    i = c = 0
    while i <= n - m:
        if tuple(prog[i : i + m]) == tuple(sub):
            c += 1
            i += m
        else:
            i += 1
    return c


def grewrite(sub, rep, prog):
    n, m = len(prog), len(sub)
    out = []
    i = 0
    while i < n:
        if i <= n - m and tuple(prog[i : i + m]) == tuple(sub):
            out.append(rep)
            i += m
        else:
            out.append(prog[i])
            i += 1
    return tuple(out)


def pool_of(corpus, library):
    bodies = {}
    for pi, prog in enumerate(corpus):
        for i in range(len(prog)):
            for j in range(i + 1, len(prog) + 1):
                body = tuple(prog[i:j])
                if body in bodies:
                    continue
                if all(s in BASE for s in body):
                    if len(body) < 2:
                        continue
                elif len(expand(body, library)) < 2:
                    continue
                occ = sum(gcount(body, p) for p in corpus)
                if occ >= 2:
                    bodies[body] = (occ, pi, i)
    return bodies


def gain_of(body, occ, kappa):
    return occ * (len(body) - 1) - len(body) - kappa


def symrank(sym, order):
    return order.index(sym)


def inv1(corpus, kappa):
    original = [tuple(p) for p in corpus]
    orig_base = [expand(p, {}) for p in original]
    work = list(original)
    library = {}
    admissions = []
    limit = sum(len(p) for p in original)
    while len(admissions) < limit:
        order = list(BASE) + sorted(library, key=lambda n: int(n[1:]))
        pool = pool_of(work, library)
        scored = [(b, gain_of(b, o, kappa), o, fp, fo) for b, (o, fp, fo) in pool.items()]
        scored = [t for t in scored if t[1] > 0]
        if not scored:
            break

        def key(t):
            b, g, o, fp, fo = t
            return (
                -g,
                expand(b, library),
                tuple(symrank(s, order) for s in b),
                fp,
                fo,
            )

        scored.sort(key=key)
        body, g, o, _, _ = scored[0]
        name = "m{}".format(len(library) + 1)
        pre = [expand(p, library) for p in work]
        library = dict(library)
        library[name] = body
        work = [grewrite(body, name, p) for p in work]
        for a, b2 in zip(pre, [expand(p, library) for p in work]):
            if a != b2:
                raise ValueError("SEMANTIC_MISMATCH")
        admissions.append({"name": name, "body": list(body), "occurrences": o, "gain": g})
    for a, b2 in zip(orig_base, work):
        if expand(b2, library) != a:
            raise ValueError("FINAL_SEMANTIC_MISMATCH")
    return {"library": library, "admissions": admissions}


def utl1(corpus, val, kappa):
    work = [tuple(p) for p in corpus]
    library = {}
    names = []
    g0v = sum(burden(w, list(BASE), {})[0] for w in val)
    cur = g0v

    def charged(lib, nmz):
        if not nmz:
            return g0v
        o = list(BASE) + nmz
        return sum(burden(w, o, lib)[0] for w in val) + sum(len(b) + kappa for b in lib.values())

    while True:
        order = list(BASE) + names
        pool = pool_of(work, library)
        scored = [(b, gain_of(b, o, kappa), o, fp, fo) for b, (o, fp, fo) in pool.items()]
        scored = [t for t in scored if t[1] > 0]
        if not scored:
            break

        def key(t):
            b, g, o, fp, fo = t
            return (-g, expand(b, library), tuple(symrank(s, order) for s in b), fp, fo)

        scored.sort(key=key)
        adm = False
        for body, g, o, _, _ in scored:
            nm = "u{}".format(len(library) + 1)
            trial = dict(library)
            trial[nm] = body
            tn = names + [nm]
            cv = charged(trial, tn)
            if cv < g0v and cv < cur:
                library = trial
                names = tn
                work = [grewrite(body, nm, p) for p in work]
                cur = cv
                adm = True
                break
        if not adm:
            break
    return {"library": library, "order": names}


# ---------------------------------------------------------------------------
# independent burden: top-down memoized feasibility + lex-min reconstruction
# ---------------------------------------------------------------------------

def expansions_of(order, library):
    return {s: expand((s,), library) if s in library else (s,) for s in order}


def burden(w, order, library):
    """(burden, first-hit program) via top-down memoized segmentation."""
    w = tuple(w)
    n = len(w)
    exps = expansions_of(order, library)
    A = len(order)
    # per-position candidate list computed once (independent of the v1 DP)
    cands = []
    for i in range(n + 1):
        row = []
        for k, s in enumerate(order):
            e = exps[s]
            if e and i + len(e) <= n and tuple(w[i : i + len(e)]) == e:
                row.append((k, s, i + len(e)))
        cands.append(row)
    memo = {}

    def feasible(i, r):
        if (i, r) in memo:
            return memo[(i, r)]
        if i == n:
            memo[(i, r)] = r == 0
            return r == 0
        if r == 0:
            memo[(i, r)] = False
            return False
        for _k, _s, j in cands[i]:
            if feasible(j, r - 1):
                memo[(i, r)] = True
                return True
        memo[(i, r)] = False
        return False

    lstar = None
    for r in range(1, n + 1):
        if feasible(0, r):
            lstar = r
            break
    if lstar is None:
        raise ValueError("UNREACHABLE")
    prog = []
    rank = 0
    i = 0
    r = lstar
    while r > 0:
        for k, s, j in cands[i]:
            if feasible(j, r - 1):
                prog.append(s)
                rank = rank * A + k
                i = j
                r -= 1
                break
        else:
            raise ValueError("RECONSTRUCT_FAILED")
    prior = sum(A ** j for j in range(1, lstar))
    return prior + rank + 1, tuple(prog)


# ---------------------------------------------------------------------------
# independent exec burden: recursive prefix-tree summation
# ---------------------------------------------------------------------------

def opcost_of(library, rho):
    cost = {s: 1 for s in BASE}
    for name in sorted(library, key=lambda n: int(n[1:])):
        cost[name] = rho + sum(cost[s] for s in library[name])
    return cost


def exec_burden_oracle(w, order, library, rho):
    w = tuple(w)
    n = len(w)
    exps = expansions_of(order, library)
    cost = opcost_of(library, rho)
    _, hit = burden(w, order, library)
    lstar = len(hit)
    A = len(order)

    def subtree_sum(pos_remaining, fixed_cost):
        """Sum of exec costs over ALL programs with `pos_remaining` free
        symbols, given already-fixed prefix cost `fixed_cost` (per program:
        fixed + suffix costs summed over the A^r suffixes)."""
        r = pos_remaining
        if r == 0:
            return fixed_cost
        csum = sum(cost[s] for s in order)
        # each free position contributes cost[s] * A^(r-1) summed over suffixes
        return (A ** r) * fixed_cost + (A ** (r - 1)) * r * csum

    total = 0
    for l in range(1, lstar):
        csum = sum(cost[s] for s in order)
        total += l * (A ** (l - 1)) * csum
    # walk the length-lstar prefix tree lexicographically, adding subtrees of
    # branches strictly below the hit path
    pref = 0
    for i, hs in enumerate(hit):
        rem = lstar - 1 - i
        for s in order:
            if order.index(s) >= order.index(hs):
                break
            total += subtree_sum(rem, pref + cost[s])
        pref += cost[hs]
    total += pref
    return total


def exec_naive(w, order, library, rho):
    import itertools as it

    w = tuple(w)
    cost = opcost_of(library, rho)
    total = 0
    for length in range(1, len(w) + 1):
        for p in it.product(order, repeat=length):
            total += sum(cost[s] for s in p)
            if expand(p, library) == w:
                return total
    raise ValueError("UNREACHABLE")


# ---------------------------------------------------------------------------
# independent combinadic unranking
# ---------------------------------------------------------------------------

def nck(n, k):
    if k < 0 or k > n:
        return 0
    r = 1
    for t in range(k):
        r = r * (n - t) // (t + 1)
    return r


def unrank_oracle(n, k, r):
    out = []
    x = 0
    for j in range(k):
        while True:
            c = nck(n - x - 1, k - j - 1)
            if r < c:
                out.append(x)
                x += 1
                break
            r -= c
            x += 1
    return tuple(out)


def materialized(n, k):
    out = []

    def rec(start, chosen):
        if len(chosen) == k:
            out.append(tuple(chosen))
            return
        for i in range(start, n - (k - len(chosen)) + 1):
            rec(i + 1, chosen + [i])

    rec(0, [])
    return out


# ---------------------------------------------------------------------------
# oracle run
# ---------------------------------------------------------------------------

def main() -> None:
    fx = json.loads(FIXTURES.read_text())
    v1fx = json.loads((V1_DIR / "FROZEN_FIXTURES_V1.json").read_text())
    result = json.loads(RESULT.read_text())
    kappa = fx["maintenance_charge_kappa_primary"]

    def note(msg):
        print("[oracle] " + msg, file=sys.stderr, flush=True)

    def P(word):
        return tuple(word)

    corpora = {k: [P(w) for w in v2["programs"]] for k, v2 in fx["corpora"].items() if v2["programs"]}
    corpora["v1ref"] = [P(p) for p in v1fx["training_corpus"]]

    checks = {}
    detail = {}

    # traces
    note("traces")
    for cid in ("c3", "c4", "c5", "trap1", "trap3"):
        t = inv1(corpora[cid], kappa)
        got = ["".join(a["body"]) for a in t["admissions"]]
        want = [e["body"] for e in fx["expected_traces_kappa1"][cid]]
        checks["trace_" + cid] = got == want
        detail["trace_" + cid] = {"oracle": got, "receipt": ["".join(a["body"]) for a in result["depth_section"][cid]["admissions"]]}
        same_as_receipt = got == ["".join(a["body"]) for a in result["depth_section"][cid]["admissions"]]
        checks["trace_receipt_" + cid] = same_as_receipt

    note("stage: family")
    # family depths
    for cid in ("fn5", "fn8", "fn12", "fl8", "fl16"):
        t = inv1(corpora[cid], kappa)
        checks["family_" + cid] = len(t["admissions"]) == result["family_formation"][cid]["n_admissions"]

    note("stage: tier")
    # tier burdens (c3 + c4 spot rows) via top-down DP vs receipt rows
    for cid in ("c3", "c4", "c5"):
        sp = fx["suites"][cid]
        tiers = {t: [P(w) for w in ws] for t, ws in sp["hplus"].items()}
        t = inv1(corpora[cid], kappa)
        names = []
        lib = {}
        ok_rows = True
        for gi in range(len(t["admissions"]) + 1):
            if gi > 0:
                a = t["admissions"][gi - 1]
                lib = dict(lib)
                lib[a["name"]] = tuple(a["body"])
                names = names + [a["name"]]
            order = list(BASE) + names
            for tname, ws in tiers.items():
                c = sum(burden(w, order, lib)[0] for w in ws)
                if c != result["tier_tables"][cid]["rows"][gi]["tier_burdens"][tname]:
                    ok_rows = False
                    detail.setdefault("tier_mismatch", []).append(
                        {"corpus": cid, "gen": gi, "tier": tname, "oracle": c,
                         "receipt": result["tier_tables"][cid]["rows"][gi]["tier_burdens"][tname]}
                    )
        checks["tier_rows_" + cid] = ok_rows

    note("stage: head-to-head")
    # head-to-head nets (count) oracle vs receipt
    for cid in ("c3", "trap1", "trap3", "v1ref"):
        sp = fx["suites"][cid]
        if cid == "v1ref":
            flat = [P(w) for w in v1fx["heldout_reuse_positive"]]
            hm = [P(w) for w in v1fx["heldout_unrelated_control"]]
            val = [P(w) for w in sp["validation"]]
        else:
            flat = [P(w) for ws in sp["hplus"].values() for w in ws]
            hm = [P(w) for w in sp["hminus"]]
            val = [P(w) for w in sp.get("validation_shallow", sp.get("validation", []))]
        comp = inv1(corpora[cid], kappa)
        util = utl1(corpora[cid], val, kappa)
        g0p = sum(burden(w, list(BASE), {})[0] for w in flat)
        g0m = sum(burden(w, list(BASE), {})[0] for w in hm)
        ok = True
        for arm, lib, nmz in (
            ("compression", comp["library"], [a["name"] for a in comp["admissions"]]),
            ("utility", util["library"], util["order"]),
        ):
            o = list(BASE) + list(nmz)
            cP = sum(burden(w, o, lib)[0] for w in flat)
            cM = sum(burden(w, o, lib)[0] for w in hm)
            K = sum(len(b) + kappa for b in lib.values())
            netP = cP + K - g0p
            netM = cM + K - g0m
            if netP != result["head_to_head"][cid][arm]["net_hplus_count"]:
                ok = False
                detail.setdefault("h2h_mismatch", []).append(
                    {"corpus": cid, "arm": arm, "oracle_netP": netP,
                     "receipt_netP": result["head_to_head"][cid][arm]["net_hplus_count"]}
                )
            if netM != result["head_to_head"][cid][arm]["net_hminus_count"]:
                ok = False
        checks["h2h_" + cid] = ok

    note("stage: exec")
    # exec flagship grid + breakeven
    hp = [P(w) for w in v1fx["heldout_reuse_positive"]]
    hm = [P(w) for w in v1fx["heldout_unrelated_control"]]
    tr = inv1(corpora["v1ref"], kappa)
    lib = tr["library"]
    order = list(BASE) + [a["name"] for a in tr["admissions"]]
    K = sum(len(b) + kappa for b in lib.values())
    exec_ok = True
    for row in result["v1_flagship_exec"]["rho_grid_rows"]:
        rho = row["rho"]
        eP = sum(exec_burden_oracle(w, order, lib, rho) for w in hp)
        gP = sum(exec_burden_oracle(w, list(BASE), {}, rho) for w in hp)
        if eP + K - gP != row["net_hplus"]:
            exec_ok = False
            detail.setdefault("exec_mismatch", []).append({"rho": rho, "oracle": eP + K - gP, "receipt": row["net_hplus"]})
    checks["exec_flagship_grid"] = exec_ok
    note("stage: naive")
    # naive cross-check on small cases
    naive_ok = True
    for w in ("abab", "cab", "ababcab", "aac"):
        for rho in (1, 2):
            a = exec_burden_oracle(w, order, lib, rho)
            b = exec_naive(w, order, lib, rho)
            naive_ok = naive_ok and a == b
    checks["exec_naive_agree"] = naive_ok

    note("stage: breakeven")
    # breakeven oracle: scan 1..1024
    be = None
    for rho in range(1, 1025):
        eP = sum(exec_burden_oracle(w, order, lib, rho) for w in hp)
        gP = sum(exec_burden_oracle(w, list(BASE), {}, rho) for w in hp)
        if eP + K - gP >= 0:
            be = rho
            break
    checks["exec_breakeven"] = be == result["v1_flagship_exec"]["breakeven_rho"]
    detail["breakeven"] = {"oracle": be, "receipt": result["v1_flagship_exec"]["breakeven_rho"]}

    note("stage: nulls")
    # nulls: c3 40 seeds materialized; v1ref exec 40 seeds materialized
    seeds40 = list(range(40))
    pool = sorted(pool_of(corpora["c3"], {}))
    combos = materialized(len(pool), 3)
    sp3 = fx["suites"]["c3"]
    flat3 = [P(w) for ws in sp3["hplus"].values() for w in ws]
    hm3 = [P(w) for w in sp3["hminus"]]
    g0p3 = sum(burden(w, list(BASE), {})[0] for w in flat3)
    null_ok = True
    for seed in seeds40:
        ci = (((seed + 1) * 2654435761) % (2 ** 32)) % len(combos)
        if unrank_oracle(len(pool), 3, ci) != combos[ci]:
            null_ok = False
        bodies = [pool[i] for i in combos[ci]]
        names = ["n{}".format(i + 1) for i in range(3)]
        libn = dict(zip(names, bodies))
        o = list(BASE) + names
        cP = sum(burden(w, o, libn)[0] for w in flat3)
        K = sum(len(b) + kappa for b in libn.values())
        net = cP + K - g0p3
        if net != result["nulls"]["c3"]["nets_hplus"][seed]:
            null_ok = False
            detail.setdefault("null_mismatch", []).append({"seed": seed, "oracle": net, "receipt": result["nulls"]["c3"]["nets_hplus"][seed]})
    checks["null_c3_40seeds"] = null_ok
    checks["unrank_vs_materialized"] = null_ok

    # kappa star oracle for c3 (full grid) and c4/c5 (derived value + bracketing
    # neighbours + grid endpoints; the receipt carries the full grid)
    def kappa_matches(cid, k):
        want_bodies = [e["body"] for e in fx["expected_traces_kappa1"][cid]]
        t = inv1(corpora[cid], k)
        return ["".join(a["body"]) for a in t["admissions"]] == want_bodies

    note("stage: kappa")
    ks_c3 = max(k for k in fx["maintenance_charge_kappa_grid"] if kappa_matches("c3", k))
    checks["kappa_star_c3"] = ks_c3 == fx["expected_kappa_star"]["c3"] == result["econ"]["c3_kappa_star"]["kappa_star"]
    for cid in ("c4", "c5"):
        ks = fx["expected_kappa_star"][cid]
        grid = fx["maintenance_charge_kappa_grid"]
        probes = sorted({0, ks - 1, ks, ks + 1, grid[-1]} & set(grid))
        ok = kappa_matches(cid, ks) and not kappa_matches(cid, ks + 1)
        # receipt full-grid agreement on every probed kappa
        for k in probes:
            t = inv1(corpora[cid], k)
            row = next(r for r in result["econ"][cid + "_kappa_star"]["rows"] if r["kappa"] == k)
            ok = ok and (["".join(a["body"]) for a in t["admissions"]] == row["bodies"])
        checks["kappa_star_" + cid] = ok and ks == result["econ"][cid + "_kappa_star"]["kappa_star"]

    all_ok = all(checks.values()) and result["terminal"].startswith("GMI_833_E8_TRANCHE2_GREEN")
    out = {
        "schema": "GMI833G0GrammarGrowthT2OracleV1",
        "all_ok": all_ok,
        "checks": checks,
        "detail": detail,
        "receipt_sha256": hashlib.sha256(RESULT.read_bytes()).hexdigest(),
        "fixtures_sha256": hashlib.sha256(FIXTURES.read_bytes()).hexdigest(),
    }
    print(json.dumps(out, sort_keys=True, indent=2))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
