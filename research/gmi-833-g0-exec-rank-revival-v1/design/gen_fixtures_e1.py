"""Generate FROZEN_FIXTURES_E1.json from the archived probe outputs.

Run on the design host: python3 -I -B gen_fixtures_e1.py
Reads probe2_out.json + probe3_out.json (design probes) and emits the frozen
machine fixtures for the E9 package.
"""
import json
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))

p2 = json.load(open("probe2_out.json"))
p3 = json.load(open("probe3_out.json"))


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


CORPORA = ["v1ref", "c3", "c4", "c5", "trap1", "trap3"]

fx = {
    "schema": "GMI833G0ExecRankRevivalFrozenFixturesE1",
    "issue": 833,
    "parent_issue": 897,
    "source_main": "636a53fb9fdae949aad85131f44e5c78389839c3",
    "v1_package": "research/gmi-833-g0-grammar-growth-v1",
    "v2_package": "research/gmi-833-g0-grammar-growth-v2",
    "v1_fixtures_sha256": sha(os.path.join(
        HERE, "gmi-833-g0-grammar-growth-v1/FROZEN_FIXTURES_V1.json")),
    "v2_fixtures_sha256": sha(os.path.join(
        HERE, "gmi-833-g0-grammar-growth-v2/FROZEN_FIXTURES_V2.json")),
    "maintenance_charge_kappa_primary": 1,
    "exec_model": {
        "rho_grid": [1, 2, 4],
        "rho_primary": 1,
        "breakeven_scan_limit": 1024,
        "k_charge_accounting": "count-symbols (frozen v2 convention)",
    },
    "null3": {
        "n_seeds": 200,
        "selection_hash": "((s+1)*2654435761 mod 2^32) mod C(pool,size)",
        "library_size_rule": "|L_inv| per corpus",
        "metrics": ["count", "exec_rho1"],
    },
    "spaces": {
        "v1ref": {"kind": "full", "subset_cap": 20000},
        "trap1": {"kind": "full", "subset_cap": 20000},
        "trap3": {"kind": "full", "subset_cap": 20000},
        "c3": {"kind": "top_t_closure", "top_t": 10, "state_cap": 1500,
               "subset_cap": 20000},
        "c4": {"kind": "chain_only", "state_cap": 1500},
        "c5": {"kind": "chain_only", "state_cap": 1500},
    },
    "charge_class": ["count", "exec", "max", "sum", "countdisp"],
    "corpora": {},
}

WITNESS_OVERRIDE = {
    "trap1": ["ab", "abab"],
    "trap3": ["ab"],
}

for cid in CORPORA:
    row = p2[cid]
    inv = row["inv1"]
    fl = row["flat"]
    entry = {
        "inv_library": {k: "".join(v) for k, v in inv["lib"].items()},
        "inv_names": inv["names"],
        "inv_breakeven": inv.get("breakeven"),
        "flat_breakeven": fl.get("breakeven"),
        "rank_inv": {"cb": row["rank_inv1"]["cb"], "eb": row["rank_inv1"]["eb"],
                     "count_net": row["rank_inv1"]["count_net"],
                     "exec_net": row["rank_inv1"]["exec_net"]},
        "rank_flat": {"cb": row["rank_flat"]["cb"], "eb": row["rank_flat"]["eb"],
                      "count_net": row["rank_flat"]["count_net"],
                      "exec_net": row["rank_flat"]["exec_net"]},
        "nulls": row["nulls"],
        "exec_mdl_degenerate": row["exec_mdl_degenerate"],
        "charge_paths": {p: {"lib": {k: "".join(v) for k, v in e["lib"].items()},
                             "count_net": e.get("count_net"),
                             "exec_net": e.get("exec_net")}
                         for p, e in row["charge_paths"].items()},
    }
    if cid in ("trap1", "trap3"):
        entry["witness"] = {
            "lib": WITNESS_OVERRIDE[cid],
            **p3[cid]["witness"],
        }
        entry["witness"].pop("lib", None)
        entry["witness"]["bodies"] = WITNESS_OVERRIDE[cid]
    else:
        entry["witness"] = {
            "bodies": ["".join(v) for v in fl["lib"].values()],
            "lib": {k: "".join(v) for k, v in fl["lib"].items()},
            "cb": row["rank_flat"]["cb"], "eb": row["rank_flat"]["eb"],
            "count_net": row["rank_flat"]["count_net"],
            "exec_net": row["rank_flat"]["exec_net"],
            "breakeven": fl.get("breakeven"),
        }
    if "count_argmin_net" in row:
        entry["space_size"] = row["space_size"]
        entry["closure_states"] = row["closure_states"]
        entry["count_argmin_net"] = row["count_argmin_net"]
        entry["count_argmin_lib"] = {k: "".join(v) for k, v in row["count_argmin_lib"].items()}
        entry["exec_argmin_net"] = row["exec_argmin_net"]
        entry["exec_argmin_lib"] = {k: "".join(v) for k, v in row["exec_argmin_lib"].items()}
        entry["frontier"] = [{**f, "lib": {k: "".join(v) for k, v in f["lib"].items()}}
                             for f in row["frontier"]]
    if cid in p3 and "affine_law" in p3.get(cid, {}):
        entry["affine_law_pairs"] = len(p3[cid]["affine_law"])
        entry["affine_law_all_exact"] = all(x["exact"] for x in p3[cid]["affine_law"])
    fx["corpora"][cid] = entry

# nesting family nets registered per corpus (probe rows)
for cid in CORPORA:
    fam = p2[cid]["nesting_family"]
    fx["corpora"][cid]["nesting_family_nets"] = [
        {"lib": {k: "".join(v) for k, v in f["lib"].items()}, "K": f["K"],
         "count_net": f["count_net"], "exec_net": f["exec_net"],
         "exec_net_rho2": f["exec_net_rho2"], "exec_net_rho4": f["exec_net_rho4"]}
        for f in fam]

fx["criteria"] = {
    "exr1_both_metric_rank1": "witness cb==0 and eb==0 on all six corpora",
    "exr1_breakevens": {"v1ref": [314, 164], "trap1": [53, 5], "trap3": [41, 1],
                        "c3": ["NONE_IN_RANGE", "NONE_IN_RANGE"],
                        "c4": ["NONE_IN_RANGE", "NONE_IN_RANGE"],
                        "c5": ["NONE_IN_RANGE", "NONE_IN_RANGE"]},
    "exr2_affine_exact_all_pairs": True,
    "exr3_argmins": {
        "v1ref": {"count": -48739, "exec": -396644},
        "c3": {"count": -31501345179969635, "exec": -1036301575840176630},
    },
    "exr4_no_universal_charge": True,
    "exr5_degenerate_all": True,
    "exr7_rung_selection": "flat rung at rho in {1,2,4} on v1ref/c3/c4/c5; identity on traps",
    "honest_failure": "any frozen expectation failing is reported as the result; fixtures are not retuned",
}

out = json.dumps(fx, indent=1, sort_keys=True)
open("FROZEN_FIXTURES_E1.json", "w").write(out + "\n")
print("fixtures written", len(out), "bytes")
print("sha256:", hashlib.sha256((out + "\n").encode()).hexdigest())
