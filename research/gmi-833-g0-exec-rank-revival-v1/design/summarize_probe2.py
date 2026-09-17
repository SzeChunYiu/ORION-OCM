import json

r = json.load(open("probe2_out.json"))
for cid in ("v1ref", "c3", "c4", "c5", "trap1", "trap3"):
    row = r[cid]
    print("=" * 70)
    print(cid)
    inv = row["inv1"]
    print(" inv1:", {k: "".join(v) for k, v in inv["lib"].items()},
          "K", inv["K"], "count", inv["count_net"] - row["g0"]["g0_count"],
          "exec1", inv["exec_net_rho1"] - row["g0"]["g0_exec_rho1"],
          "breakeven", inv.get("breakeven"))
    fl = row["flat"]
    print(" flat:", {k: "".join(v) for k, v in fl["lib"].items()},
          "K", fl["K"], "count", fl["count_net"], "exec1", fl["exec_net"],
          "exec2", fl["exec_net_rho2"], "exec4", fl["exec_net_rho4"],
          "exec0", fl["exec0"], "breakeven", fl.get("breakeven"))
    print(" nesting family:")
    for f in row["nesting_family"]:
        print("   ", {k: "".join(v) for k, v in f["lib"].items()}, "K", f["K"],
              "c", f["count_net"], "e1", f["exec_net"])
    print(" closure:", row.get("closure_states"), "top_t", row.get("closure_top_t"),
          "space", row.get("space_size"), "pool", row.get("pool_size"))
    if "count_argmin_net" in row:
        print(" count_argmin:", row["count_argmin_net"], row["count_argmin_lib"])
        print(" exec_argmin:", row["exec_argmin_net"], row["exec_argmin_lib"])
        print(" frontier:", [(f["count_net"], f["exec_net"],
                              {k: "".join(v) for k, v in f["lib"].items()}) for f in row["frontier"]])
    print(" nulls:", row["nulls"])
    print(" rank_inv1:", row["rank_inv1"])
    print(" rank_flat:", row["rank_flat"])
    print(" charge paths:")
    for p, e in row["charge_paths"].items():
        print("   ", p, {k: "".join(v) for k, v in e["lib"].items()},
              "c", e.get("count_net"), "e", e.get("exec_net"), "cb", e.get("cb"), "eb", e.get("eb"))
    print(" exec_mdl_degenerate:", row["exec_mdl_degenerate"])
