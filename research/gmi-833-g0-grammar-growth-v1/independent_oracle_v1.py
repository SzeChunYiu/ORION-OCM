#!/usr/bin/env python3
"""Independent oracle for research/gmi-833-g0-grammar-growth-v1.

Recomputes expansions, the full invention trace, every held-out burden
(naive enumeration for the registered grammars, independent top-down
segmentation search for the null ensemble), the THR-1 identities and the
kappa ablation WITHOUT importing the main module, then compares against the
committed RESULT_V1.json.  Prints ORACLE_RESULT_V1.json to stdout.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
BASE = ("a", "b", "c")


def _fail(code: str):
    raise SystemExit("ORACLE_FAIL:" + code)


# ---- expansion via joined strings -------------------------------------------

def expand_str(prog, library):
    """Expand with ','-joined strings; cycles return the sentinel CYCLE."""
    def go(sym, active):
        if sym in BASE:
            return sym
        if sym not in library:
            _fail("UNKNOWN_SYMBOL")
        if sym in active:
            return "CYCLE"
        body = library[sym]
        parts = []
        for s in body:
            r = go(s, active | frozenset((sym,)))
            if r == "CYCLE":
                return "CYCLE"
            parts.append(r)
        return "".join(parts)

    pieces = []
    for s in prog:
        r = go(s, frozenset())
        if r == "CYCLE":
            return "CYCLE"
        pieces.append(r)
    return "".join(pieces)


def base_word(prog):
    return "".join(prog)


# ---- mining, implemented independently --------------------------------------

def occurrences(sub, prog):
    """Greedy non-overlapping count on ','-joined form."""
    s = ",".join(sub)
    p = ",".join(prog)
    out = 0
    i = 0
    while True:
        j = p.find(s, i)
        if j < 0:
            return out
        out += 1
        i = j + len(s)


def rewrite(sub, name, prog):
    s = ",".join(sub)
    p = ",".join(prog)
    while True:
        j = p.find(s)
        if j < 0:
            break
        p = p[:j] + name + p[j + len(s):]
    return tuple(x for x in p.split(","))


def mine(corpus, kappa):
    cur = [tuple(p) for p in corpus]
    lib = {}
    trace = []
    while True:
        # gather candidate bodies with all-alphabet subwords
        cands = {}
        for prog in cur:
            for i in range(len(prog)):
                for j in range(i + 1, len(prog) + 1):
                    body = prog[i:j]
                    key = ",".join(body)
                    if key in cands:
                        continue
                    if len(expand_str(body, lib)) < 2:
                        continue
                    occ = sum(occurrences(body, p) for p in cur)
                    if occ >= 2:
                        cands[key] = (body, occ, len(body))
        best = None
        for key, (body, occ, ln) in sorted(cands.items()):
            gain = occ * (ln - 1) - ln - kappa
            if gain <= 0:
                continue
            # syntax-independent tie key: (-gain, base expansion, body)
            k = (-gain, expand_str(body, lib), key)
            if best is None or k < best[0]:
                best = (k, body, gain, occ)
        if best is None:
            return lib, cur, trace, "NO_STRICTLY_BENEFICIAL_CANDIDATE"
        _, body, gain, occ = best
        name = "m{}".format(len(lib) + 1)
        trace.append(
            {
                "name": name,
                "body": list(body),
                "occurrences": occ,
                "gain": gain,
                "corpus_symbols_before": sum(len(p) for p in cur),
            }
        )
        lib[name] = body
        cur = [rewrite(body, name, p) for p in cur]


# ---- burden: naive enumeration ------------------------------------------------

def burden_naive(target, symbols, library):
    w = base_word(target)
    exp = {s: expand_str((s,), library) for s in symbols}
    count = 0
    ln = 1
    frontier = [""]
    while ln <= len(target):
        for combo in _lex_products(symbols, ln):
            count += 1
            if "".join(exp[s] for s in combo) == w:
                return count, list(combo)
        ln += 1
    _fail("TARGET_UNREACHABLE")


def _lex_products(symbols, ln):
    if ln == 0:
        yield ()
        return
    for head in symbols:
        for tail in _lex_products(symbols, ln - 1):
            yield (head,) + tail


# ---- burden: independent top-down segmentation search -------------------------

def burden_search(target, symbols, library):
    """Minimal description length + lexicographically first program + burden,
    via memoized top-down search.  Different structure from the main DP."""
    w = base_word(target)
    exp = [expand_str((s,), library) for s in symbols]
    A = len(symbols)
    memo = {}

    def seg(i, r):
        if (i, r) in memo:
            return memo[(i, r)]
        if i == len(w) and r == 0:
            memo[(i, r)] = True
            return True
        if r == 0 or i >= len(w):
            memo[(i, r)] = False
            return False
        ok = False
        for e in exp:
            if e and w.startswith(e, i) and seg(i + len(e), r - 1):
                ok = True
                break
        memo[(i, r)] = ok
        return ok

    lstar = None
    for r in range(1, len(w) + 1):
        if seg(0, r):
            lstar = r
            break
    if lstar is None:
        _fail("TARGET_UNREACHABLE")
    prog = []
    i = 0
    for k in range(lstar):
        for s, e in zip(symbols, exp):
            if e and w.startswith(e, i) and seg(i + len(e), lstar - k - 1):
                prog.append(s)
                i += len(e)
                break
    rank = 0
    for s in prog:
        rank = rank * A + symbols.index(s)
    prior = sum(A ** j for j in range(1, lstar))
    return prior + rank + 1, prog


# ---- main ----------------------------------------------------------------------

def main():
    fx = json.loads((ROOT / "FROZEN_FIXTURES_V1.json").read_text())
    result = json.loads((ROOT / "RESULT_V1.json").read_text())
    kappa = fx["maintenance_charge_kappa_primary"]
    corpus = [tuple(p) for p in fx["training_corpus"]]
    hplus = [tuple(w) for w in fx["heldout_reuse_positive"]]
    hminus = [tuple(w) for w in fx["heldout_unrelated_control"]]

    mismatches = []
    agreement = {}

    def check(label, ok):
        agreement[label] = bool(ok)
        if not ok:
            mismatches.append(label)

    # expansion + invention trace
    lib, final_corpus, trace, stopped = mine(corpus, kappa)
    check("invention_admissions", [t["name"] for t in trace] ==
          [a["name"] for a in result["invention"]["admissions"]])
    check("invention_bodies", [t["body"] for t in trace] ==
          [a["body"] for a in result["invention"]["admissions"]])
    check("invention_gains", [t["gain"] for t in trace] ==
          [a["gain"] for a in result["invention"]["admissions"]])
    check("invention_occurrences", [t["occurrences"] for t in trace] ==
          [a["occurrences"] for a in result["invention"]["admissions"]])
    check("final_corpus", [list(p) for p in final_corpus] == result["invention"]["final_corpus"])
    check("stopped_by", stopped == result["grammar"]["stopped_by"])
    check("rec1_m2_expansion", expand_str(("m2",), lib) == "abab")
    check("rec1_m1_expansion", expand_str(("m1",), lib) == "ab")

    # corpus semantic preservation (HSEM) recheck on every program
    sem_ok = all(expand_str(p, lib) == base_word(p) for p in corpus)
    check("corpus_semantics_preserved", sem_ok)

    order = list(BASE) + [t["name"] for t in trace]

    # held-out burdens: naive enumeration AND search, both must equal receipt
    naive_checks = 0
    search_checks = 0
    for section, targets in (("heldout_reuse_positive", hplus),
                             ("heldout_unrelated_control", hminus)):
        for row, w in zip(result[section]["targets"], targets):
            b0n, _ = burden_naive(w, list(BASE), {})
            bFn, _ = burden_naive(w, order, lib)
            b0s, _ = burden_search(w, list(BASE), {})
            bFs, hit = burden_search(w, order, lib)
            naive_checks += 2
            search_checks += 2
            if (b0n, bFn) != (row["burden_G0"], row["burden_expanded"]):
                mismatches.append(section + ":" + base_word(w))
            if (b0s, bFs) != (row["burden_G0"], row["burden_expanded"]):
                mismatches.append(section + ":search:" + base_word(w))
            if hit != row["first_hit_expanded"]:
                mismatches.append(section + ":hit:" + base_word(w))
    agreement["naive_burden_checks"] = naive_checks
    agreement["search_burden_checks"] = search_checks

    # nets
    for section, targets in (("heldout_reuse_positive", hplus),
                             ("heldout_unrelated_control", hminus)):
        cum0 = sum(burden_search(w, list(BASE), {})[0] for w in targets)
        cumF = sum(burden_search(w, order, lib)[0] for w in targets)
        K = sum(len(b) + kappa for b in lib.values())
        check(section + "_net", cumF + K - cum0 == result[section]["net"])
        check(section + "_K_total", K == result[section]["library_overhead_K_total"])

    # THR-1
    usage = {}
    for row in result["heldout_reuse_positive"]["targets"]:
        for s in row["first_hit_expanded"]:
            if s in lib:
                usage[s] = usage.get(s, 0) + 1
    for r in result["threshold_thr1"]["per_macro"]:
        n = r["macro"]
        H = usage.get(n, 0)
        b = len(lib[n])
        check("thr_" + n + "_Heff", H == r["H_eff"])
        check("thr_" + n + "_holds", (H * (b - 1) > b + kappa) == r["holds_marginal"])

    # null ensemble recomputation
    pool = set()
    for prog in corpus:
        for i in range(len(prog)):
            for j in range(i + 1, len(prog) + 1):
                body = prog[i:j]
                if len(body) >= 2 and sum(occurrences(body, p) for p in corpus) >= 2:
                    pool.add(tuple(body))
    pool_sorted = sorted(pool)
    check("null_pool", [list(b) for b in pool_sorted] == result["null_null1"]["pool_bodies"])
    n_choose = 1
    for t in range(result["null_null1"]["library_size"]):
        n_choose = n_choose * (len(pool_sorted) - t) // (t + 1)
    from itertools import combinations as _comb
    combos = list(_comb(range(len(pool_sorted)), result["null_null1"]["library_size"]))
    g0p = sum(burden_search(w, list(BASE), {})[0] for w in hplus)
    g0m = sum(burden_search(w, list(BASE), {})[0] for w in hminus)
    nets_p = []
    nets_m = []
    for seed in fx["null_seeds"]:
        ci = (((seed + 1) * 2654435761) % (2 ** 32)) % n_choose
        bodies = [pool_sorted[k] for k in combos[ci]]
        names = ["n{}".format(i + 1) for i in range(len(bodies))]
        nlib = dict(zip(names, bodies))
        norder = list(BASE) + names
        cumP = sum(burden_search(w, norder, nlib)[0] for w in hplus)
        cumM = sum(burden_search(w, norder, nlib)[0] for w in hminus)
        K = sum(len(b) + kappa for b in nlib.values())
        nets_p.append(cumP + K - g0p)
        nets_m.append(cumM + K - g0m)
    check("null_nets_hplus", nets_p == result["null_null1"]["nets_hplus"])
    check("null_nets_hminus", nets_m == result["null_null1"]["nets_hminus"])

    # kappa ablation recomputation (admission counts + m2 formation)
    for row in result["kappa_ablation"]["rows"]:
        _, _, tr, _ = mine(corpus, row["kappa"])
        m2 = (len(tr) >= 2 and tr[1]["body"] == [tr[0]["name"], tr[0]["name"]])
        check("abl_kappa{}_admissions".format(row["kappa"]), len(tr) == row["n_admissions"])
        check("abl_kappa{}_m2".format(row["kappa"]), m2 == row["m2_formed"])

    # cycle hostiles
    check("cycle_self", expand_str(("mX",), {"mX": ("mX", "a")}) == "CYCLE")
    check("cycle_two", expand_str(("mA",), {"mA": ("mB",), "mB": ("mA",)}) == "CYCLE")

    all_ok = len(mismatches) == 0
    out = {
        "schema": "GMI833G0GrammarGrowthOracleV1",
        "claim_ceiling": result["claim_ceiling"],
        "freeze_commit": result["freeze_commit"],
        "fixtures_sha256": hashlib.sha256((ROOT / "FROZEN_FIXTURES_V1.json").read_bytes()).hexdigest(),
        "all_ok": all_ok,
        "mismatches": mismatches,
        "agreement": agreement,
        "terminal": "ORACLE_GREEN" if all_ok else "ORACLE_RED",
    }
    print(json.dumps(out, sort_keys=True, indent=2))
    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
