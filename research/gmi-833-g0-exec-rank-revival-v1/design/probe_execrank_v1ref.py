"""Design probe (pre-freeze, off-Mac): reachable-admission space on the v1
flagship fixture, both-metric nets, null ranks, frontier.

Uses ONLY the merged v1/v2 modules. No new claims; outputs guide the freeze.
Run: python3 -I -B probe_execrank_v1ref.py
"""
import sys
import json
import itertools

sys.path.insert(0, "v1")
sys.path.insert(0, "v2")

import g0_grammar_growth_v1 as v1  # noqa: E402
import g0_grammar_growth_v2 as v2  # noqa: E402

KAPPA = 1
RHOS = (1, 2, 4)

fx = v1.load_fixtures()
CORPUS = [tuple(p) for p in fx["training_corpus"]]
HP = [tuple(w) for w in fx["heldout_reuse_positive"]]
HM = [tuple(w) for w in fx["heldout_unrelated_control"]]

EXPS0 = v1.symbol_expansions(["a", "b", "c"], {})
G0P = sum(v1.burden_dp(w, ["a", "b", "c"], EXPS0)[0] for w in HP)
G0M = sum(v1.burden_dp(w, ["a", "b", "c"], EXPS0)[0] for w in HM)
EG0P = {r: sum(v2.exec_burden(w, ["a", "b", "c"], {}, r) for w in HP) for r in RHOS}
EG0M = {r: sum(v2.exec_burden(w, ["a", "b", "c"], {}, r) for w in HM) for r in RHOS}


def nets(names, lib):
    order = ["a", "b", "c"] + list(names)
    exps = v1.symbol_expansions(order, lib)
    K = v1.k_total(lib, KAPPA)
    cp = sum(v1.burden_dp(w, order, exps)[0] for w in HP)
    cm = sum(v1.burden_dp(w, order, exps)[0] for w in HM)
    row = {
        "K_total": K,
        "count_net_hplus": cp + K - G0P,
        "count_net_hminus": cm + K - G0M,
    }
    for r in RHOS:
        ep = sum(v2.exec_burden(w, order, lib, r) for w in HP)
        em = sum(v2.exec_burden(w, order, lib, r) for w in HM)
        row["exec_net_hplus_rho%d" % r] = ep + K - EG0P[r]
        row["exec_net_hminus_rho%d" % r] = em + K - EG0M[r]
    return row


def depth_of(lib):
    def d(name, seen=()):
        if name in seen:
            raise ValueError("cycle")
        body = lib[name]
        subs = [d(s, seen + (name,)) for s in body if s in lib]
        return 0 if not subs else 1 + max(subs)

    return max([d(n) for n in lib], default=0)


def flatten(lib):
    return {n: v1.expand_word(b, lib) for n, b in lib.items()}


# ---- sequential closure under positive-count-gain admissions (all sequences)
def closure(corpus, kappa):
    out = {}

    def rec(work, lib, names, hist):
        key = (tuple(tuple(p) for p in work), tuple(names))
        if key in out:
            return
        out[key] = (dict(lib), list(names), list(hist))
        pool = v1.candidate_pool(work, lib)
        for body, (occ, fp, fo) in sorted(pool.items()):
            gain = v1.admission_gain(body, occ, kappa)
            if gain <= 0:
                continue
            name = "m{}".format(len(lib) + 1)
            nlib = dict(lib)
            nlib[name] = body
            nwork = [v1.greedy_rewrite(body, name, p) for p in work]
            rec(nwork, nlib, names + [name], hist + [(name, "".join(body), gain)])

    rec([tuple(p) for p in corpus], {}, [], [])
    return out


def main():
    result = {}

    # 1) reachable sequential libraries (positive count gain)
    cl = closure(CORPUS, KAPPA)
    libs = []
    seen = set()
    for lib, names, hist in cl.values():
        sig = tuple(sorted((n, b) for n, b in lib.items()))
        if sig in seen:
            continue
        seen.add(sig)
        libs.append((lib, names, hist))
    result["n_reachable"] = len(libs)

    # 2) add flattenings
    flats = []
    for lib, names, hist in libs:
        fl = flatten(lib)
        sig = tuple(sorted((n, tuple(b)) for n, b in fl.items()))
        if sig not in seen:
            seen.add(sig)
            flats.append((fl, names, ["flat:" + "".join(h[1]) for h in hist]))
    result["n_flattenings_added"] = len(flats)

    # 3) pool subsets up to size 3
    pool = v1.candidate_pool(CORPUS, {})
    pool_bodies = sorted(pool)
    subsets = []
    for size in (1, 2, 3):
        for combo in itertools.combinations(range(len(pool_bodies)), size):
            bodies = [pool_bodies[i] for i in combo]
            names = ["n{}".format(i + 1) for i in range(size)]
            lib = {nm: tuple(b) for nm, b in zip(names, bodies)}
            sig = tuple(sorted((n, tuple(b)) for n, b in lib.items()))
            if sig not in seen:
                seen.add(sig)
                subsets.append((lib, names, ["pool:" + "".join(b) for b in bodies]))
    result["n_pool_subsets_added"] = len(subsets)

    all_libs = [("seq",) + t for t in libs] + [("flat",) + t for t in flats] + [("pool",) + t for t in subsets]

    rows = []
    for kind, lib, names, hist in all_libs:
        row = {"kind": kind, "origin": hist, "names": names,
               "library": {n: list(b) for n, b in lib.items()},
               "depth": depth_of(lib)}
        row.update(nets(names, lib))
        rows.append(row)
    result["space"] = rows

    # 4) argmins and frontier
    best_count = min(rows, key=lambda r: r["count_net_hplus"])
    best_exec = {r: min(rows, key=lambda x: x["exec_net_hplus_rho%d" % r]) for r in RHOS}
    result["count_argmin"] = {"lib": best_count["library"], "net": best_count["count_net_hplus"]}
    result["exec_argmin"] = {str(r): {"lib": best_exec[r]["library"],
                                      "net": best_exec[r]["exec_net_hplus_rho%d" % r]} for r in RHOS}

    def pareto(rows_):
        keys = [(r["count_net_hplus"], r["exec_net_hplus_rho1"]) for r in rows_]
        keep = []
        for i, (c, e) in enumerate(keys):
            dominated = any(
                (c2 <= c and e2 <= e and (c2 < c or e2 < e)) for c2, e2 in keys
            )
            if not dominated:
                keep.append(i)
        return keep

    pf = pareto(rows)
    result["frontier_rho1"] = [
        {"lib": rows[i]["library"], "depth": rows[i]["depth"],
         "count_net": rows[i]["count_net_hplus"],
         "exec_net": rows[i]["exec_net_hplus_rho1"]}
        for i in sorted(pf, key=lambda i: rows[i]["count_net_hplus"])
    ]

    # 5) null ranks for each size-2 library under both metrics
    def null_ensemble(library_size):
        P = len(pool_bodies)
        total = v1._n_choose_k(P, library_size)
        cnt, ex = [], []
        for seed in range(200):
            ci = (((seed + 1) * 2654435761) % (2 ** 32)) % total
            idxs = v2.unrank_combination(P, library_size, ci)
            bodies = [pool_bodies[i] for i in idxs]
            names = ["n{}".format(i + 1) for i in range(library_size)]
            lib = {nm: tuple(b) for nm, b in zip(names, bodies)}
            nr = nets(names, lib)
            cnt.append(nr["count_net_hplus"])
            ex.append(nr["exec_net_hplus_rho1"])
        return cnt, ex

    ncnt, nex = null_ensemble(2)
    result["null_size2"] = {
        "count_min": min(ncnt), "exec_min": min(nex),
        "count_nets_sorted": sorted(set(ncnt)), "exec_nets_sorted": sorted(set(nex)),
    }
    rank_rows = []
    for kind, lib, names, hist in all_libs:
        if len(lib) != 2:
            continue
        nr = nets(names, lib)
        cb = sum(1 for x in ncnt if x < nr["count_net_hplus"])
        eb = sum(1 for x in nex if x < nr["exec_net_hplus_rho1"])
        rank_rows.append({
            "lib": {n: list(b) for n, b in lib.items()}, "kind": kind,
            "count_net": nr["count_net_hplus"], "exec_net": nr["exec_net_hplus_rho1"],
            "count_nulls_better": cb, "exec_nulls_better": eb,
        })
    result["size2_ranks"] = rank_rows

    print(json.dumps(result, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
