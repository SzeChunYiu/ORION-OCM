"""Exact resource metrics of the K05 v5 machine for the lower-bound doc.

Counts per-cell expression sizes, operator/node totals, cost, gate sites,
and the exact census of distinct equality (EQ) subtrees in the frozen basis,
classifying position-position EQ (EQ_T, 12 nodes) vs position-constant EQ
(EQ_C semantics). Output is printed; the numbers are cited verbatim in
K05_LOWER_BOUND_V1.md.
"""
import json, sys
from pathlib import Path
PKG = Path("/home/billy/fdt-k58-revive/k05-wt2/research/gmi-833-family-derivation-symbolic-ssm-retrieval-v1")
sys.path.insert(0, str(PKG))
import machinery_v1 as M

def expr_size(e):
    if e[0] in ("atom", "const"):
        return 1
    if e[0] == "un":
        return 1 + expr_size(e[2])
    return 1 + expr_size(e[1]) + expr_size(e[2])

res = json.load(open(str(PKG / "k05_v5_work" / "k05_v5_result_v1.json")))
m = res["machine"]
ex = m["update"]
sizes = [expr_size(e) for e in ex]
print("work_cells", len(ex), "input", m["input_cells"], "output", m["output_cell"],
      "steps", m["steps"], "rho", m["rho"])
print("per_expr_size", sizes)
print("max_size", max(sizes), "sum_size", sum(sizes))
print("per_expr_ops", [M.expr_ops(e) for e in ex])
print("cost", M.machine_cost(m))
print("gate_sites", M.machine_gate_sites(m))

# collect distinct EQ subtrees: ["un","GE+2",["add", GE0_a, GE0_b]]
eqs = {}
def walk(e):
    if e[0] == "un":
        if e[1] == "GE+2" and e[2][0] == "add":
            a = e[2]
            if (a[1][0] == "un" and a[1][1] == "GE+0" and
                    a[2][0] == "un" and a[2][1] == "GE+0"):
                eqs[json.dumps(e, sort_keys=True)] = e
        walk(e[2])
    elif e[0] == "add":
        walk(e[1]); walk(e[2])
for e in ex:
    walk(e)

def classify(eq):
    return "EQ_C" if "\"const\"" in json.dumps(eq) else "EQ_T"

n_t = sum(1 for e in eqs.values() if classify(e) == "EQ_T")
n_c = sum(1 for e in eqs.values() if classify(e) == "EQ_C")
print("distinct_EQ_subtrees", len(eqs), "EQ_T", n_t, "EQ_C", n_c)
eq_sizes = [expr_size(e) for e in eqs.values()]
print("EQ_size_min", min(eq_sizes), "max", max(eq_sizes),
      "distinct_sizes", sorted(set(eq_sizes)))
tot_eq_nodes = sum(eq_sizes)
tot_eq_ops = sum(M.expr_ops(e) for e in eqs.values())
print("EQ_total_nodes", tot_eq_nodes, "EQ_total_ops", tot_eq_ops,
      "EQ_frac_of_total_nodes", round(tot_eq_nodes / sum(sizes), 3))

# how many distinct EQs are used in >=2 work cells (shared bits)
usage = {}
for ci, e in enumerate(ex):
    seen_c = set()
    def walk2(ee):
        if ee[0] == "un":
            if ee[1] == "GE+2" and ee[2][0] == "add":
                a = ee[2]
                if (a[1][0] == "un" and a[1][1] == "GE+0" and
                        a[2][0] == "un" and a[2][1] == "GE+0"):
                    key = json.dumps(ee, sort_keys=True)
                    if key not in seen_c:
                        seen_c.add(key)
                        usage.setdefault(key, []).append(ci)
            walk2(ee[2])
        elif ee[0] == "add":
            walk2(ee[1]); walk2(ee[2])
    walk2(e)
shared = {k: v for k, v in usage.items() if len(set(v)) >= 2}
print("distinct_EQ_used_in_2plus_cells", len(shared))
for k, v in sorted(shared.items(), key=lambda kv: kv[0]):
    print("  shared", v, classify(json.loads(k)), json.dumps(json.loads(k))[:96])

# EQ instances per cell and total
per_cell = []
for e in ex:
    cnt = [0]
    def w2(ee):
        if ee[0] == "un":
            if ee[1] == "GE+2" and ee[2][0] == "add":
                a = ee[2]
                if (a[1][0] == "un" and a[1][1] == "GE+0" and
                        a[2][0] == "un" and a[2][1] == "GE+0"):
                    cnt[0] += 1
            w2(ee[2])
        elif ee[0] == "add":
            w2(ee[1]); w2(ee[2])
    w2(e)
    per_cell.append(cnt[0])
print("EQ_instances_per_cell", per_cell, "total_instances", sum(per_cell))
