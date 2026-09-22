"""Coordinator independent verification of k05_v5_result_v1.json (read-only)."""
import json, sys
from pathlib import Path
PKG = Path("/home/billy/fdt-k58-revive/k05-wt2/research/gmi-833-family-derivation-symbolic-ssm-retrieval-v1")
sys.path.insert(0, str(PKG))
import posthoc_adjudicate_v1 as A
import machinery_v1 as M

bc = json.loads((PKG / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())["batteries"]["B_CONTR"]
rows = bc["task_rows"]; lays = bc["task_cell_layouts"]
res = json.loads((PKG / "k05_v5_work" / "k05_v5_result_v1.json").read_text())
m = res["machine"]
assert m["model"] == "M_ITER" and m["input_cells"] == 18
total = m["input_cells"] + len(m["update"])
print("work_cells", len(m["update"]), "total_cells", total,
      "cell_cap", bc["cell_cap"], "step_cap", bc["step_cap"], "steps", m["steps"])
print("cost", M.machine_cost(m), "output_cell", m["output_cell"])
pos_err = fp = illegal = 0
for i in range(len(rows)):
    cells, _, lg = A.run_iter(m, lays[i])
    if not lg:
        illegal += 1
    pred = cells[m["output_cell"]] if lg else None
    if pred != rows[i][3]:
        if rows[i][3] == 1: pos_err += 1
        else: fp += 1
print("FULL pos_err", pos_err, "fp", fp, "illegal", illegal, "of", len(rows))
print("CAPS total<=cap:", total <= bc["cell_cap"], "steps<=cap:", m["steps"] <= bc["step_cap"])
