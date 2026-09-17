"""Design probe 3 (pre-freeze): close the gaps before freezing.

(a) trap1 witness {ab,abab} and trap3 witness {ab}: null ranks under both
    metrics + break-evens.
(b) Affine exchange law asserted exactly on every nesting-family pair with
    differing depth, at rho in {1,2,4}: net(flat_rung,rho) - net(nested_rung,rho)
    == -rho*dDV + dK, with dDV, dK derived from rho=1 and rho=2 and re-checked
    at rho=4.
(c) Identity-tie census: which null combos equal the witness nets (per corpus).
"""
import sys
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "gmi-833-g0-grammar-growth-v1"))
sys.path.insert(0, os.path.join(HERE, "gmi-833-g0-grammar-growth-v2"))

import g0_grammar_growth_v1 as v1  # noqa: E402
import g0_grammar_growth_v2 as v2  # noqa: E402
from probe_execrank_battery import (  # noqa: E402
    KAPPA, flatten, suite_nets, g0_suites, null_ensemble, breakeven,
    nesting_family, fast_burden_dp, fast_exec_burden,
)

fx2 = v2.load_fixtures()
fxv1 = v1.load_fixtures()

out = {}

# (a) trap witnesses
for cid, wit in (("trap1", ["ab", "abab"]), ("trap3", ["ab"])):
    corpus = [tuple(p) for p in fx2["corpora"][cid]["programs"]]
    hp = [tuple(w) for ts in fx2["suites"][cid]["hplus"].values() for w in ts]
    hm = [tuple(w) for w in fx2["suites"][cid]["hminus"]]
    g0 = g0_suites(hp, hm)
    inv = v1.invent(corpus, KAPPA)
    size = len(inv["library_order"])
    names = ["n{}".format(i + 1) for i in range(len(wit))]
    lib = {nm: tuple(w) for nm, w in zip(names, wit)}
    nr = suite_nets(names, lib, hp, hm)
    cnt, ex, P, total = null_ensemble(corpus, size, hp, hm)
    cb = sum(1 for x in cnt if x < nr["count_net"] - g0["g0_count"])
    eb = sum(1 for x in ex if x < nr["exec_net_rho1"] - g0["g0_exec_rho1"])
    ct = sum(1 for x in cnt if x == nr["count_net"] - g0["g0_count"])
    et = sum(1 for x in ex if x == nr["exec_net_rho1"] - g0["g0_exec_rho1"])
    be = breakeven(names, lib, hp, g0["g0_exec_rho1"])
    out.setdefault(cid, {})["witness"] = {
        "lib": wit, "count_net": nr["count_net"] - g0["g0_count"],
        "exec_net": nr["exec_net_rho1"] - g0["g0_exec_rho1"],
        "cb": cb, "eb": eb, "count_ties": ct, "exec_ties": et,
        "breakeven": be, "size": size,
    }
    print(cid, "witness", wit, "cb", cb, "eb", eb, "ties", ct, et, "be", be, flush=True)

# (b) affine law on nesting families, all corpora
for cid in ("v1ref", "c3", "c4", "c5"):
    if cid == "v1ref":
        corpus = [tuple(p) for p in fxv1["training_corpus"]]
        hp = [tuple(w) for w in fxv1["heldout_reuse_positive"]]
    else:
        corpus = [tuple(p) for p in fx2["corpora"][cid]["programs"]]
        hp = [tuple(w) for ts in fx2["suites"][cid]["hplus"].values() for w in ts]
    inv = v1.invent(corpus, KAPPA)
    fam = nesting_family(inv["library"], inv["library_order"])
    rows = []
    for lib, nm in fam:
        nr = suite_nets(nm, lib, hp, hp[:0], rhos=(0, 1, 2, 4))
        rows.append((lib, nm, nr))
    checks = []
    for lib1, nm1, nr1 in rows:
        for lib2, nm2, nr2 in rows:
            if nr1["K"] == nr2["K"] and set(map(str, nm1)) == set(map(str, nm2)):
                pass
    # pair each rung with the fully-flat rung of same macro set
    by_set = {}
    for lib, nm, nr in rows:
        key = tuple(sorted(nm))
        by_set.setdefault(key, []).append((lib, nm, nr))
    law = []
    for key, grp in by_set.items():
        if len(grp) < 2:
            continue
        flatrow = min(grp, key=lambda t: t[2]["K"])  # flat rung has max... K largest
        # flat = max K rung
        flatrow = max(grp, key=lambda t: t[2]["K"])
        for lib, nm, nr in grp:
            if nr is flatrow[2]:
                continue
            dK = flatrow[2]["K"] - nr["K"]
            d1 = (flatrow[2]["exec_net_rho1"] - nr["exec_net_rho1"])
            d2 = (flatrow[2]["exec_net_rho2"] - nr["exec_net_rho2"])
            d4 = (flatrow[2]["exec_net_rho4"] - nr["exec_net_rho4"])
            # d(rho) = -rho*dDV + dK
            dDV = (dK - d1)
            ok = (d2 == -2 * dDV + dK) and (d4 == -4 * dDV + dK) and (d1 == -dDV + dK)
            law.append({"corpus": cid, "rung": {k: "".join(v) for k, v in lib.items()},
                        "dK": dK, "dDV": dDV, "exact": ok,
                        "d1": d1, "d2": d2, "d4": d4})
    out.setdefault(cid, {})["affine_law"] = law
    bad = [x for x in law if not x["exact"]]
    print(cid, "affine law pairs:", len(law), "all exact:", not bad, flush=True)

json.dump(out, open("probe3_out.json", "w"), indent=1, sort_keys=True, default=str)
print("done")
