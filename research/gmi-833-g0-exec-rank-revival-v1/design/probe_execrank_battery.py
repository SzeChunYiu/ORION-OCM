"""Design probe 2 (pre-freeze, off-Mac): battery-wide expectations.

Fast burden/exec DPs (precomputed position->symbol matches; identical integer
arithmetic to v1.burden_dp / v2.exec_burden, validated by exact agreement).
Tiered scope: full closure for v1ref/trap1/trap3; capped top-T closure for c3;
deterministic chains + nesting-choice family for c4/c5.
Run: python3 -I -B probe_execrank_battery.py
"""
import sys
import json
import itertools

sys.path.insert(0, "gmi-833-g0-grammar-growth-v1")
sys.path.insert(0, "gmi-833-g0-grammar-growth-v2")

import g0_grammar_growth_v1 as v1  # noqa: E402
import g0_grammar_growth_v2 as v2  # noqa: E402

KAPPA = 1
RHOS = (0, 1, 2, 4)
TOP_T = 10          # frozen for c3 closure reduction
STATE_CAP = 1500    # frozen closure cap
POOL_SUBSET_CAP = 20000

fx2 = v2.load_fixtures()
fxv1 = v1.load_fixtures()


# ---------------- fast DPs (same arithmetic as frozen v1/v2) ----------------

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


def fast_burden_dp(target, symbol_order, expansions):
    w = tuple(target)
    n = len(w)
    A = len(symbol_order)
    symbols = list(symbol_order)
    ms = _matches(w, symbols, expansions)
    S = [[False] * (n + 1) for _ in range(n + 1)]
    S[n][0] = True
    for i in range(n - 1, -1, -1):
        Si = S[i]
        for s, le in ms[i]:
            Sm = S[i + le]
            for r in range(1, n - i + 1):
                if Sm[r - 1]:
                    Si[r] = True
    for r in range(1, n + 1):
        if S[0][r]:
            lstar = r
            break
    else:
        raise ValueError("TARGET_UNREACHABLE")
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
            raise ValueError("SEGMENTATION_INVARIANT_VIOLATION")
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
    for r in range(1, n + 1):
        if S[0][r]:
            lstar = r
            break
    else:
        raise ValueError("TARGET_UNREACHABLE")
    # first-hit program (lexicographic least at lstar) via fast dp
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


# ---------------- shared machinery ----------------

def flatten(lib):
    return {n: v1.expand_word(b, lib) for n, b in lib.items()}


def suite_nets(names, lib, hp, hm, rhos=RHOS):
    order = ["a", "b", "c"] + list(names)
    exps = v1.symbol_expansions(order, lib)
    K = v1.k_total(lib, KAPPA)
    cp = sum(fast_burden_dp(w, order, exps)[0] for w in hp)
    cm = sum(fast_burden_dp(w, order, exps)[0] for w in hm)
    row = {"K": K, "count_net": cp + K, "count_net_m": cm + K}
    for r in rhos:
        ep = sum(fast_exec_burden(w, order, lib, r) for w in hp)
        row["exec_net_rho%d" % r] = ep + K
    return row


def g0_suites(hp, hm):
    exps = v1.symbol_expansions(["a", "b", "c"], {})
    g = {"g0_count": sum(fast_burden_dp(w, ["a", "b", "c"], exps)[0] for w in hp)}
    for r in RHOS:
        g["g0_exec_rho%d" % r] = sum(fast_exec_burden(w, ["a", "b", "c"], {}, r) for w in hp)
    return g


CHARGES = {
    "count": lambda u, cost: len(u) + KAPPA,
    "exec": lambda u, cost: sum(cost.get(s, 1) for s in u) + KAPPA,
    "max": lambda u, cost: max(len(u) + KAPPA, sum(cost.get(s, 1) for s in u) + KAPPA),
    "sum": lambda u, cost: len(u) + KAPPA + sum(cost.get(s, 1) for s in u) + KAPPA,
    "countdisp": lambda u, cost: len(u) + KAPPA + sum(1 for s in u if s in cost),
}


def charge_invent(corpus, phi, rho, kappa):
    work = [tuple(p) for p in corpus]
    lib = {}
    names = []
    for _ in range(v1.corpus_symbol_count([tuple(p) for p in corpus])):
        pool = v1.candidate_pool(work, lib)
        cost = v2.opcosts(lib, rho)
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
        lib[name] = body
        names.append(name)
        work = [v1.greedy_rewrite(body, name, p) for p in work]
    return lib, names


def closure(corpus, top_t=None):
    out = {}

    def rec(work, lib, names):
        key = (tuple(tuple(p) for p in work), tuple(sorted(lib.items())))
        if key in out:
            return
        if len(out) >= STATE_CAP:
            raise RuntimeError("STATE_CAP")
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
            nlib[name] = body
            nwork = [v1.greedy_rewrite(body, name, p) for p in work]
            rec(nwork, nlib, names + [name])

    rec([tuple(p) for p in corpus], {}, [])
    return out


def nesting_family(trace_lib, trace_order):
    """All flat/nested body-choice combinations along the invented trace."""
    fam = []
    prefixes = []
    lib = {}
    for name in trace_order:
        lib = dict(lib)
        lib[name] = trace_lib[name]
        prefixes.append(dict(lib))
    for pref in prefixes:
        for combo in itertools.product((0, 1), repeat=len(pref)):
            # combo[k]=1 -> keep level k+1 body as invented (nested); 0 -> flat
            built = {}
            names = []
            for k, name in enumerate(list(pref)):
                body = pref[name]
                if combo[k] == 0:
                    # flatten this body against the library that defines it
                    sub = {n: pref[n] for n in list(pref)[:k]}
                    body = v1.expand_word(body, sub)
                built[name] = body
                names.append(name)
            fam.append((built, names))
    return fam


def null_ensemble(corpus, size, hp, hm):
    pool = v1.candidate_pool([tuple(p) for p in corpus], {})
    pool_bodies = sorted(pool)
    P = len(pool_bodies)
    total = v1._n_choose_k(P, size)
    cnt, ex = [], []
    g0 = g0_suites(hp, hm)
    for seed in range(200):
        ci = (((seed + 1) * 2654435761) % (2 ** 32)) % total
        idxs = v2.unrank_combination(P, size, ci)
        bodies = [pool_bodies[i] for i in idxs]
        names = ["n{}".format(i + 1) for i in range(size)]
        lib = {nm: tuple(b) for nm, b in zip(names, bodies)}
        nr = suite_nets(names, lib, hp, hm, rhos=(1,))
        cnt.append(nr["count_net"] - g0["g0_count"])
        ex.append(nr["exec_net_rho1"] - g0["g0_exec_rho1"])
    return cnt, ex, P, total


def ranks_vs(cnt, ex, net):
    return (sum(1 for x in cnt if x < net["count_net"]),
            sum(1 for x in ex if x < net["exec_net_rho1"]))


def breakeven(names, lib, hp, g0e):
    order = ["a", "b", "c"] + list(names)
    K = v1.k_total(lib, KAPPA)
    for rho in range(1, 1025):
        ep = sum(fast_exec_burden(w, order, lib, rho) for w in hp)
        if ep + K - g0e >= 0:
            return rho
    return None


def main():
    # validation of fast DPs against frozen implementations
    hpv = [tuple(w) for w in fxv1["heldout_reuse_positive"]]
    invv = v1.invent([tuple(p) for p in fxv1["training_corpus"]], KAPPA)
    ordv = ["a", "b", "c"] + invv["library_order"]
    expsv = v1.symbol_expansions(ordv, invv["library"])
    for w in hpv:
        assert fast_burden_dp(w, ordv, expsv)[0] == v1.burden_dp(w, ordv, expsv)[0]
        assert fast_exec_burden(w, ordv, invv["library"], 1) == v2.exec_burden(w, ordv, invv["library"], 1)
        assert fast_exec_burden(w, ordv, invv["library"], 4) == v2.exec_burden(w, ordv, invv["library"], 4)
    print("fast DP validation: OK", flush=True)

    corpora = {}
    for cid in ("c3", "c4", "c5", "trap1", "trap3"):
        corpora[cid] = {
            "corpus": [tuple(p) for p in fx2["corpora"][cid]["programs"]],
            "hp": [tuple(w) for ts in fx2["suites"][cid]["hplus"].values() for w in ts],
            "hm": [tuple(w) for w in fx2["suites"][cid]["hminus"]],
        }
    corpora["v1ref"] = {
        "corpus": [tuple(p) for p in fxv1["training_corpus"]],
        "hp": [tuple(w) for w in fxv1["heldout_reuse_positive"]],
        "hm": [tuple(w) for w in fxv1["heldout_unrelated_control"]],
    }

    out = {}
    for cid, d in corpora.items():
        corpus, hp, hm = d["corpus"], d["hp"], d["hm"]
        g0 = g0_suites(hp, hm)
        row = {"g0": g0}
        inv = v1.invent(corpus, KAPPA)
        names = inv["library_order"]
        row["inv1"] = {"lib": {k: list(vv) for k, vv in inv["library"].items()}, "names": names}
        row["inv1"].update(suite_nets(names, inv["library"], hp, hm))
        row["inv1"]["breakeven"] = breakeven(names, inv["library"], hp, g0["g0_exec_rho1"])

        # nesting-choice family (includes flat chain and full inv)
        fam = nesting_family(inv["library"], names)
        famrows = []
        for lib, nm in fam:
            nr = suite_nets(nm, lib, hp, hm)
            famrows.append({"lib": {k: list(vv) for k, vv in lib.items()},
                            "K": nr["K"], "count_net": nr["count_net"] - g0["g0_count"],
                            "exec_net": nr["exec_net_rho1"] - g0["g0_exec_rho1"],
                            "exec_net_rho2": nr["exec_net_rho2"] - g0["g0_exec_rho2"],
                            "exec_net_rho4": nr["exec_net_rho4"] - g0["g0_exec_rho4"],
                            "exec0": nr["exec_net_rho0"]})
        row["nesting_family"] = famrows
        flatlib = flatten(inv["library"])
        flat_str = {k: "".join(vv) for k, vv in flatlib.items()}
        row["flat"] = next(f for f in famrows
                           if {k: "".join(vv) for k, vv in f["lib"].items()} == flat_str)
        row["flat"]["breakeven"] = breakeven(names, flatlib, hp, g0["g0_exec_rho1"])

        # closure (tiered, with top-T retry for c3)
        cl = None
        if cid == "c3":
            for t in (TOP_T, 8, 5, 3):
                try:
                    cl = closure(corpus, top_t=t)
                    row["closure_top_t"] = t
                    break
                except RuntimeError:
                    continue
        else:
            try:
                cl = closure(corpus, top_t=None)
            except RuntimeError:
                row["closure_states"] = "CAP_EXCEEDED"
        try:
            if cl is None:
                raise RuntimeError
            row["closure_states"] = len(cl)
            row["closure_states"] = len(cl)
            libs, seen = [], set()
            for lib, nm in cl.values():
                sig = tuple(sorted(lib.items()))
                if sig in seen:
                    continue
                seen.add(sig)
                libs.append((lib, nm))
            for lib, nm in list(libs):
                f = flatten(lib)
                sig = tuple(sorted((n, tuple(b)) for n, b in f.items()))
                if sig not in seen:
                    seen.add(sig)
                    libs.append((f, nm))
            # pool subsets when feasible
            pool = v1.candidate_pool(corpus, {})
            P = len(pool)
            pool_bodies = sorted(pool)
            subset_total = sum(v1._n_choose_k(P, s) for s in range(1, min(P, len(names) + 2)))
            row["pool_size"] = P
            row["subset_total"] = subset_total
            if subset_total <= POOL_SUBSET_CAP:
                for size in range(1, min(P, len(names) + 2)):
                    for combo in itertools.combinations(range(P), size):
                        bodies = [pool_bodies[i] for i in combo]
                        nm = ["n{}".format(i + 1) for i in range(size)]
                        lib = {a: tuple(b) for a, b in zip(nm, bodies)}
                        sig = tuple(sorted(lib.items()))
                        if sig in seen:
                            continue
                        seen.add(sig)
                        libs.append((lib, nm))
            space = []
            for lib, nm in libs:
                nr = suite_nets(nm, lib, hp, hm, rhos=(1,))
                space.append({"lib": {k: list(vv) for k, vv in lib.items()},
                              "count_net": nr["count_net"] - g0["g0_count"],
                              "exec_net": nr["exec_net_rho1"] - g0["g0_exec_rho1"]})
            row["space_size"] = len(space)
            row["count_argmin_net"] = min(x["count_net"] for x in space)
            row["exec_argmin_net"] = min(x["exec_net"] for x in space)
            row["count_argmin_lib"] = min(space, key=lambda x: x["count_net"])["lib"]
            row["exec_argmin_lib"] = min(space, key=lambda x: x["exec_net"])["lib"]
            vals = [(x["count_net"], x["exec_net"], x["lib"]) for x in space]
            fr = [{"lib": lib, "count_net": c, "exec_net": e}
                  for c, e, lib in vals
                  if not any((c2 <= c and e2 <= e and (c2 < c or e2 < e)) for c2, e2, _ in vals)]
            row["frontier"] = sorted(fr, key=lambda x: x["count_net"])
        except RuntimeError:
            row["closure_states"] = "CAP_EXCEEDED"

        # nulls and ranks
        cnt, ex, P, total = null_ensemble(corpus, len(names), hp, hm)
        row["nulls"] = {"count_min": min(cnt), "exec_min": min(ex), "pool": P, "combos": total}
        for label, lib in (("inv1", inv["library"]), ("flat", flatlib)):
            nr = suite_nets(names, lib, hp, hm, rhos=(1,))
            nr["count_net"] -= g0["g0_count"]
            nr["exec_net_rho1"] -= g0["g0_exec_rho1"]
            cb, eb = ranks_vs(cnt, ex, nr)
            row["rank_" + label] = {"count_net": nr["count_net"], "exec_net": nr["exec_net_rho1"],
                                    "cb": cb, "eb": eb}

        # charge-class paths
        paths = {}
        for pname, phi in CHARGES.items():
            lib, nm = charge_invent(corpus, phi, 1, KAPPA)
            entry = {"lib": {k: list(vv) for k, vv in lib.items()}, "names": nm}
            if lib:
                nr = suite_nets(nm, lib, hp, hm, rhos=(1,))
                entry["count_net"] = nr["count_net"] - g0["g0_count"]
                entry["exec_net"] = nr["exec_net_rho1"] - g0["g0_exec_rho1"]
                if len(lib) == len(names):
                    entry["cb"], entry["eb"] = ranks_vs(cnt, ex, {
                        "count_net": nr["count_net"] - g0["g0_count"],
                        "exec_net_rho1": nr["exec_net_rho1"] - g0["g0_exec_rho1"]})
            paths[pname] = entry
        row["charge_paths"] = paths

        # exec-MDL degeneracy over G0 pool
        pool = v1.candidate_pool(corpus, {})
        deg = True
        for body, (occ, _, _) in pool.items():
            for rho in (1, 2, 4):
                if -rho * occ - sum(1 for _ in body) - KAPPA >= 0:
                    deg = False
        row["exec_mdl_degenerate"] = deg

        out[cid] = row
        json.dump(out, open("probe2_out.json", "w"), indent=1, sort_keys=True, default=str)
        print(cid, "done", flush=True)

    print(json.dumps({c: {k: out[c][k] for k in
                          ("inv1", "flat", "nulls", "rank_inv1", "rank_flat",
                           "closure_states", "space_size", "count_argmin_net",
                           "exec_argmin_net", "exec_mdl_degenerate", "pool_size")}
                      for c in out}, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
