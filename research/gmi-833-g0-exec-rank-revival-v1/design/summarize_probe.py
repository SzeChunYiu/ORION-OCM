import json

r = json.load(open("probe_out.json"))
print("reachable:", r["n_reachable"], "flattenings added:", r["n_flattenings_added"],
      "pool subsets added:", r["n_pool_subsets_added"])
print("count_argmin:", r["count_argmin"])
print("exec_argmin:", json.dumps(r["exec_argmin"]))
print("frontier (rho=1):")
for p in r["frontier_rho1"]:
    print("  depth", p["depth"], "count", p["count_net"], "exec", p["exec_net"],
          {k: "".join(v) for k, v in p["lib"].items()})
print("null size2 mins:", r["null_size2"]["count_min"], r["null_size2"]["exec_min"])
print("size2 ranks:")
for x in r["size2_ranks"]:
    print("  ", x["kind"], {k: "".join(v) for k, v in x["lib"].items()},
          "count", x["count_net"], "exec", x["exec_net"],
          "cb", x["count_nulls_better"], "eb", x["exec_nulls_better"])
print("all space rows sorted by count_net:")
for x in sorted(r["space"], key=lambda t: t["count_net_hplus"])[:12]:
    print("  ", x["kind"], {k: "".join(v) for k, v in x["library"].items()},
          "d", x["depth"], "K", x["K_total"],
          "c", x["count_net_hplus"], "e1", x["exec_net_hplus_rho1"],
          "e2", x["exec_net_hplus_rho2"], "e4", x["exec_net_hplus_rho4"])
