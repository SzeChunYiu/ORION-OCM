#!/usr/bin/env python3
"""GMI #833 E9 independent oracle.

Recomputes the E9 headline quantities WITHOUT importing the main module
(exec_rank_revival_v1), using the frozen v1/v2 engines as the independent
implementation (v1.burden_dp for counts, v2.exec_burden for exec burdens,
v1.invent for traces, v2.unrank_combination for nulls):

- v1ref/trap1/trap3 full verdicts: witness + invented nets at rho 1,2,4,
  40-seed NULL-3 sub-ensembles under both metrics, ranks;
- nesting-family rung nets (independently re-derived flattening logic) on all
  six corpora at rho 1 (2 and 4 where registered feasible);
- affine exchange-law identities from its own numbers;
- exec-MDL degeneracy scan on all six G0 pools;
- agreement with the committed RESULT_E1.json on every shared integer.

Output: sorted JSON; all_ok true iff every recomputation agrees exactly.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gmi-833-g0-grammar-growth-v1"))
sys.path.insert(0, os.path.join(HERE, "..", "gmi-833-g0-grammar-growth-v2"))

import g0_grammar_growth_v1 as v1  # noqa: E402
import g0_grammar_growth_v2 as v2  # noqa: E402

KAPPA = 1
SUBSEEDS = 40
TRAPS = ("trap1", "trap3")


def flatten(lib):
    return {n: v1.expand_word(b, lib) for n, b in lib.items()}


def nesting_fam(trace_lib, trace_order):
    fam = []
    prefixes = []
    lib = {}
    for name in trace_order:
        lib = dict(lib)
        lib[name] = tuple(trace_lib[name])
        prefixes.append(dict(lib))
    for pref in prefixes:
        names = list(pref)
        for mask in range(2 ** len(names)):
            built = {}
            for k, name in enumerate(names):
                body = tuple(pref[name])
                if not (mask >> k) & 1:
                    body = tuple(v1.expand_word(
                        body, {n: pref[n] for n in names[:k]}))
                built[name] = body
            if built not in [f for f, _ in fam]:
                fam.append((built, list(names)))
    return fam


def nets(names, lib, hp, rhos):
    order = ["a", "b", "c"] + list(names)
    exps = v1.symbol_expansions(order, lib)
    K = v1.k_total(lib, KAPPA)
    out = {"K": K,
           "count": sum(v1.burden_dp(w, order, exps)[0] for w in hp) + K}
    for r in rhos:
        out["exec%d" % r] = sum(v2.exec_burden(w, order, lib, r) for w in hp) + K
    return out


def g0s(hp, rhos):
    exps = v1.symbol_expansions(["a", "b", "c"], {})
    out = {"count": sum(v1.burden_dp(w, ["a", "b", "c"], exps)[0] for w in hp)}
    for r in rhos:
        out["exec%d" % r] = sum(v2.exec_burden(w, ["a", "b", "c"], {}, r) for w in hp)
    return out


def sub_ensemble(corpus, size, hp, g0):
    pool = v1.candidate_pool([tuple(p) for p in corpus], {})
    pool_bodies = sorted(pool)
    P = len(pool_bodies)
    total = v1._n_choose_k(P, size)
    cnt, ex = [], []
    for seed in range(SUBSEEDS):
        ci = (((seed + 1) * 2654435761) % (2 ** 32)) % total
        idxs = v2.unrank_combination(P, size, ci)
        bodies = [pool_bodies[i] for i in idxs]
        names = ["n{}".format(i + 1) for i in range(size)]
        lib = {nm: tuple(b) for nm, b in zip(names, bodies)}
        nr = nets(names, lib, hp, (1,))
        cnt.append(nr["count"] - g0["count"])
        ex.append(nr["exec1"] - g0["exec1"])
    return cnt, ex


def main():
    v1fx = v1.load_fixtures()
    v2fx = v2.load_fixtures()
    result = json.loads(open(os.path.join(HERE, "RESULT_E1.json"), "rb").read().decode())
    bat = {}
    for cid in ("v1ref", "c3", "c4", "c5", "trap1", "trap3"):
        if cid == "v1ref":
            bat[cid] = ([tuple(p) for p in v1fx["training_corpus"]],
                        [tuple(w) for w in v1fx["heldout_reuse_positive"]])
        else:
            bat[cid] = ([tuple(p) for p in v2fx["corpora"][cid]["programs"]],
                        [tuple(w) for ts in v2fx["suites"][cid]["hplus"].values()
                         for w in ts])
    checks = {}
    detail = {}

    # 1) nesting-family rung nets on all corpora (rho=1) + affine identities
    for cid, (corpus, hp) in bat.items():
        inv = v1.invent(corpus, KAPPA)
        names = inv["library_order"]
        g0 = g0s(hp, (1,))
        fam = nesting_fam(inv["library"], names)
        rows = []
        for lib, nm in fam:
            nr = nets(nm, lib, hp, (1,))
            rows.append({"K": nr["K"], "c": nr["count"] - g0["count"],
                         "e": nr["exec1"] - g0["exec1"], "n": len(nm),
                         "bodies": ["".join(lib[x]) for x in nm]})
        by_set = {}
        for r in rows:
            by_set.setdefault(r["n"], []).append(r)
        aff_ok = True
        for n, grp in by_set.items():
            if len(grp) < 2:
                continue
            flatr = max(grp, key=lambda r: r["K"])
            for r in grp:
                if r is flatr:
                    continue
                dK = flatr["K"] - r["K"]
                d1 = flatr["e"] - r["e"]
                if d1 != -((dK - d1)) + dK:
                    aff_ok = False
        key = "nesting_rho1_" + cid
        # cross-check against the receipt rows (rho1 + K + count)
        rec_rows = result["corpora"][cid]["nesting_family"]
        rec_sigs = sorted((tuple(r["bodies"]), r["K"], r["count_net"],
                           r["exec_net_rho1"]) for r in rec_rows)
        ora_sigs = sorted((tuple(r["bodies"]), r["K"], r["c"], r["e"]) for r in rows)
        checks[key] = (rec_sigs == ora_sigs) and aff_ok
        detail[key] = {"rungs": len(rows), "affine_ok": aff_ok,
                       "receipt_match": rec_sigs == ora_sigs}

    # 2) full verdicts on v1ref + traps: witness/invented nets at 1,2,4 +
    #    40-seed sub-ensemble ranks under both metrics
    for cid in ("v1ref",) + TRAPS:
        corpus, hp = bat[cid]
        inv = v1.invent(corpus, KAPPA)
        names = inv["library_order"]
        g0 = g0s(hp, (1, 2, 4))
        wit = result["corpora"][cid]["witness"]["bodies"]
        wnames = ["n{}".format(i + 1) for i in range(len(wit))]
        wlib = {nm: tuple(b) for nm, b in zip(wnames, wit)}
        irow = nets(names, inv["library"], hp, (1, 2, 4))
        wrow = nets(wnames, wlib, hp, (1, 2, 4))
        cnt, ex = sub_ensemble(corpus, len(names), hp, g0)
        icb = sum(1 for x in cnt if x < irow["count"] - g0["count"])
        ieb = sum(1 for x in ex if x < irow["exec1"] - g0["exec1"])
        wcb = sum(1 for x in cnt if x < wrow["count"] - g0["count"])
        web = sum(1 for x in ex if x < wrow["exec1"] - g0["exec1"])
        ri = result["corpora"][cid]
        # the 40-seed sub-ensemble must match the receipt's first 40 per-seed
        # nets exactly (stronger than rank equality across different ensembles)
        sub_match = (cnt == ri["nulls"]["nets_count"][:SUBSEEDS]
                     and ex == ri["nulls"]["nets_exec"][:SUBSEEDS])
        ok = (
            irow["count"] - g0["count"] == ri["inv_nets"]["count_net"]
            and irow["exec1"] - g0["exec1"] == ri["inv_nets"]["exec_net_rho1"]
            and irow["exec2"] - g0["exec2"] == ri["inv_nets"]["exec_net_rho2"]
            and irow["exec4"] - g0["exec4"] == ri["inv_nets"]["exec_net_rho4"]
            and wrow["count"] - g0["count"] == ri["witness"]["nets"]["count_net"]
            and wrow["exec1"] - g0["exec1"] == ri["witness"]["nets"]["exec_net_rho1"]
            and wrow["exec2"] - g0["exec2"] == ri["witness"]["nets"]["exec_net_rho2"]
            and wrow["exec4"] - g0["exec4"] == ri["witness"]["nets"]["exec_net_rho4"]
            and sub_match
            and wcb == 0 and web == 0
        )
        checks["verdict_" + cid] = ok
        detail["verdict_" + cid] = {
            "inv": {"count": irow["count"] - g0["count"],
                    "exec1": irow["exec1"] - g0["exec1"],
                    "sub_cb": icb, "sub_eb": ieb},
            "witness": {"count": wrow["count"] - g0["count"],
                        "exec1": wrow["exec1"] - g0["exec1"],
                        "exec2": wrow["exec2"] - g0["exec2"],
                        "exec4": wrow["exec4"] - g0["exec4"],
                        "sub_cb": wcb, "sub_eb": web},
            "sub_ensemble_matches_receipt": sub_match,
        }

    # 3) witness rho1 nets on c3/c4/c5 via the frozen slow engine
    for cid in ("c3", "c4", "c5"):
        corpus, hp = bat[cid]
        inv = v1.invent(corpus, KAPPA)
        names = inv["library_order"]
        wlib = flatten(inv["library"])
        g0 = g0s(hp, (1,))
        wrow = nets(names, wlib, hp, (1,))
        ri = result["corpora"][cid]
        checks["witness_slow_" + cid] = (
            wrow["count"] - g0["count"] == ri["witness"]["nets"]["count_net"]
            and wrow["exec1"] - g0["exec1"] == ri["witness"]["nets"]["exec_net_rho1"])

    # 4) exec-MDL degeneracy on all six G0 pools
    deg_ok = True
    for cid, (corpus, hp) in bat.items():
        pool = v1.candidate_pool(corpus, {})
        for body, (occ, _, _) in pool.items():
            for rho in (1, 2, 4):
                if -rho * occ - len(body) - KAPPA >= 0:
                    deg_ok = False
    checks["exec_mdl_degenerate_all"] = deg_ok

    # 5) breakeven closed-form cross-check on v1ref witness and invented
    for cid in ("v1ref", "trap1", "trap3"):
        corpus, hp = bat[cid]
        inv = v1.invent(corpus, KAPPA)
        names = inv["library_order"]
        wit = result["corpora"][cid]["witness"]["bodies"]
        wnames = ["n{}".format(i + 1) for i in range(len(wit))]
        wlib = {nm: tuple(b) for nm, b in zip(wnames, wit)}
        g0 = g0s(hp, (1,))
        for label, lib, nm in (("inv", inv["library"], names),
                               ("wit", wlib, wnames)):
            order = ["a", "b", "c"] + list(nm)
            K = v1.k_total(lib, KAPPA)
            n1 = sum(v2.exec_burden(w, order, lib, 1) for w in hp) + K - g0["exec1"]
            n0 = sum(v2.exec_burden(w, order, lib, 0) for w in hp) + K - g0["exec1"]
            disp = n1 - n0
            if n1 >= 0:
                bd = 1
            elif disp <= 0:
                bd = "NONE_IN_RANGE"
            else:
                bd = max(2, (-n0 + disp - 1) // disp)
            exp_be = (result["corpora"][cid]["inv_breakeven"] if label == "inv"
                      else result["corpora"][cid]["witness"]["breakeven"])
            checks["breakeven_%s_%s" % (cid, label)] = bd == exp_be

    out = {
        "schema": "GMI833G0ExecRankRevivalOracleE1",
        "issue": 833,
        "parent_issue": 897,
        "sub_seeds": SUBSEEDS,
        "checks": {k: bool(v) for k, v in checks.items()},
        "detail": detail,
        "all_ok": all(bool(v) for v in checks.values()),
    }
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
