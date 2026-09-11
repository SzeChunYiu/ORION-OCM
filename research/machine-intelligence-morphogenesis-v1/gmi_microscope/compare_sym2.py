"""RV-377-025 adjudication: compare the executed ROWS_V6 frontiers (STAGE_DE_SMOOTH_V8_SYM<k>_H.json, STAGE_DE_SMOOTH_V8_SMOOTH3_H.json)
with the frozen prediction STAGE_DE_SYM2_PREDICTION.json. Writes microscopes/results/STAGE_DE_SYM2_VERDICT.json."""
from __future__ import annotations

import json
import os

from .core import sha256_of
from .predict_sym import H_GRID, R_GRID

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
FILES = {"SYM3": "STAGE_DE_SMOOTH_V8_SYM3_H.json", "SYM5": "STAGE_DE_SMOOTH_V8_SYM5_H.json", "SYM7": "STAGE_DE_SMOOTH_V8_SYM7_H.json",
         "SYM8": "STAGE_DE_SMOOTH_V8_SYM8_H.json", "SMOOTH3": "STAGE_DE_SMOOTH_V8_SMOOTH3_H.json"}


def main():
    pred = json.load(open(os.path.join(RES, "STAGE_DE_SYM2_PREDICTION.json")))
    theta = pred["theta"]
    obs = {eco: json.load(open(os.path.join(RES, f))) for eco, f in FILES.items()}
    cols = list(obs["SYM3"]["PH_REV"])
    cap = lambda eco, row, col: obs[eco]["capability_by_cell"][f"{row}|{col}|4"]
    v = {"prediction_sha256": pred["receipt_sha256"], "observation_sha256": {e: o["receipt_sha256"] for e, o in obs.items()}}
    # C1 closed form / certificate for S5h
    c1 = {eco: {"predicted": pred["per_ecology"][eco]["certified_capabilities"]["S5h"], "observed": sorted({cap(eco, "S5h", c) for c in cols})} for eco in FILES}
    v["C1_S5h_closed_form"] = all(x["observed"] == [x["predicted"]] for x in c1.values()); v["C1_detail"] = c1
    # C2 admissible sets
    adm = {eco: sorted(r for r in ("S4", "S2a", "S5h", "S5", "S3") if all(cap(eco, r, c) >= theta for c in cols)) for eco in FILES}
    v["C2_admissible_sets_as_predicted"] = all(adm[eco] == sorted(pred["per_ecology"][eco]["predicted_admissible"]) for eco in FILES)
    v["C2_detail"] = {eco: {"predicted": sorted(pred["per_ecology"][eco]["predicted_admissible"]), "observed": adm[eco]} for eco in FILES}
    # C3 called cells (void where the admissible set differs)
    wrong = {}; n_called = {}; void = []
    for eco in FILES:
        if adm[eco] != sorted(pred["per_ecology"][eco]["predicted_admissible"]): void.append(eco); continue
        w = []; n = 0
        for key, cell in pred["per_ecology"][eco]["cells"].items():
            if cell["predicted"] == "ABSTAIN": continue
            n += 1
            if cell["predicted"] not in obs[eco]["frontier_H_r"][key]:
                w.append({"cell": key, "predicted": cell["predicted"], "observed": obs[eco]["frontier_H_r"][key]})
        wrong[eco] = w; n_called[eco] = n
    v["C3_all_called_cells_correct"] = bool(n_called) and all(not w for w in wrong.values()) and not void
    v["C3_n_called"] = n_called; v["C3_n_wrong"] = {e: len(w) for e, w in wrong.items()}; v["C3_wrong_cells"] = {e: w[:10] for e, w in wrong.items()}; v["C3_void"] = void
    # C4 structure in the three-class ecologies
    c4 = {}
    for eco in ("SYM3", "SMOOTH3"):
        if eco in void: continue
        for col in cols:
            r0 = all("S2a" in obs[eco]["frontier_H_r"][f"{col}|H={Hh}|r=0"] for Hh in H_GRID)
            seq = [obs[eco]["frontier_H_r"][f"{col}|H={Hh}|r=8"] for Hh in H_GRID]
            called = [pred["per_ecology"][eco]["cells"][f"{col}|H={Hh}|r=8"]["predicted"] for Hh in H_GRID]
            hstar = pred["per_ecology"][eco]["predicted_Hstar_S5h_to_S4_by_r"][col]["8"]
            if hstar is None or hstar > 128:
                ok = all("S5h" in s for s, c in zip(seq, called) if c != "ABSTAIN"); regime = f"H* {hstar}: S5h at every called H"
            elif hstar < 1:
                ok = all("S4" in s for s, c in zip(seq, called) if c != "ABSTAIN"); regime = f"H* {hstar}: S4 at every called H"
            else:
                sw = None
                for i in range(1, len(H_GRID)):
                    if "S5h" in seq[i - 1] and "S4" in seq[i] and "S5h" not in seq[i]: sw = (H_GRID[i - 1], H_GRID[i]); break
                ok = sw is not None and sw[0] <= hstar <= sw[1]; regime = f"switch {sw} vs H* {hstar}"
            c4[f"{eco}|{col}"] = {"S2a_wins_r0_every_H": r0, "r8_by_H": seq, "regime": regime, "ok": bool(r0 and ok)}
    v["C4_three_class_structure"] = bool(c4) and all(x["ok"] for x in c4.values()); v["C4_detail"] = c4
    # C5 two-class ecologies: S5h every r >= 1
    c5 = {}
    for eco in ("SYM5", "SYM7"):
        if eco in void: continue
        for col in cols:
            ok = all("S5h" in obs[eco]["frontier_H_r"][f"{col}|H={Hh}|r={r}"] for Hh in H_GRID for r in R_GRID[1:])
            ok0 = all("S2a" in obs[eco]["frontier_H_r"][f"{col}|H={Hh}|r=0"] for Hh in H_GRID if pred["per_ecology"][eco]["cells"][f"{col}|H={Hh}|r=0"]["predicted"] == "S2a")
            c5[f"{eco}|{col}"] = bool(ok and ok0)
    v["C5_memory_wins_revision_axis_when_gradient_inadmissible"] = bool(c5) and all(c5.values()); v["C5_detail"] = c5
    v["C6_C2_identical_dev_tables"] = all(all(o["C2"].values()) for o in obs.values())
    keys = ["C1_S5h_closed_form", "C2_admissible_sets_as_predicted", "C3_all_called_cells_correct", "C4_three_class_structure", "C5_memory_wins_revision_axis_when_gradient_inadmissible", "C6_C2_identical_dev_tables"]
    v["all_claims_hold"] = all(v[k] for k in keys)
    out = {"schema": "StageDESym2VerdictV1", "issue": 377, "revival_record": "RV-377-025", "verdict": v}
    out["receipt_sha256"] = sha256_of({k: x for k, x in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, "STAGE_DE_SYM2_VERDICT.json"), "w"), indent=1, sort_keys=True, default=str)
    return out


if __name__ == "__main__":
    o = main(); v = o["verdict"]
    print({k: v[k] for k in v if k[:2] in ("C1", "C2", "C3", "C4", "C5", "C6") and "detail" not in k and "wrong" not in k and "called" not in k and "void" not in k})
    print("all_claims_hold:", v["all_claims_hold"]); print("C1:", v["C1_detail"]); print("C2:", v["C2_detail"])
    print("C3 called:", v["C3_n_called"], "wrong:", v["C3_n_wrong"], "void:", v["C3_void"])
    for key, c in v["C4_detail"].items(): print("  C4", key, c["regime"], c["ok"], c["r8_by_H"])
