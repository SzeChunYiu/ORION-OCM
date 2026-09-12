"""RV-377-021 adjudication: compare the executed E_sym(k) frontiers (STAGE_DE_SMOOTH_V6_SYM<k>.json) with the frozen
prediction (STAGE_DE_SYM_PREDICTION.json). Writes microscopes/results/STAGE_DE_SYM_VERDICT.json."""
from __future__ import annotations

import json
import os

from .core import sha256_of
from .predict_sym import ALL_K, BOUNDARY, CANDIDATES_THREE_CLASS, H_GRID, R_GRID

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")


def main():
    pred = json.load(open(os.path.join(RES, "STAGE_DE_SYM_PREDICTION.json")))
    theta = pred["ecology"]["theta"]
    obs = {k: json.load(open(os.path.join(RES, f"STAGE_DE_SMOOTH_V6_SYM{k}.json"))) for k in ALL_K}
    cols = list(obs[ALL_K[0]]["PH_REV"])
    cap = lambda k, row, col: obs[k]["capability_by_cell"][f"{row}|{col}|4"]
    verdict = {"observation_sha256": {str(k): obs[k]["receipt_sha256"] for k in ALL_K}, "prediction_sha256": pred["receipt_sha256"]}
    # C1, C2 closed forms; C7 monotone
    c1 = {str(k): {"predicted": pred["per_k"][str(k)]["predicted_capability"]["S5k"], "observed": sorted({cap(k, "S5k", c) for c in cols})} for k in ALL_K}
    c2 = {str(k): {"predicted": pred["per_k"][str(k)]["predicted_capability"]["S5"], "observed": sorted({cap(k, "S5", c) for c in cols})} for k in ALL_K}
    verdict["C1_S5k_closed_form"] = all(v["observed"] == [v["predicted"]] for v in c1.values()); verdict["C1_detail"] = c1
    verdict["C2_S5_closed_form"] = all(v["observed"] == [v["predicted"]] for v in c2.values()); verdict["C2_detail"] = c2
    s5k_seq = [cap(k, "S5k", cols[0]) for k in sorted(ALL_K)]
    verdict["C7_S5k_strictly_decreasing_in_k"] = all(a > b for a, b in zip(s5k_seq, s5k_seq[1:])); verdict["C7_detail"] = dict(zip(map(str, sorted(ALL_K)), s5k_seq))
    # C3 three-class at the first qualifying candidate; C4 boundary
    adm = {str(k): {row: all(cap(k, row, c) >= theta for c in cols) for row in ("S4", "S2a", "S5k", "S5", "S3")} for k in ALL_K}
    verdict["admissible_by_k"] = adm
    first = next((k for k in CANDIDATES_THREE_CLASS if adm[str(k)]["S4"] and adm[str(k)]["S2a"]), None)
    verdict["C3_first_candidate_with_S4_S2a_admissible"] = first
    verdict["C3_three_classes"] = bool(first is not None and adm[str(first)]["S5k"] and not adm[str(first)]["S5"] and not adm[str(first)]["S3"])
    verdict["three_class_ks"] = [k for k in CANDIDATES_THREE_CLASS if all(adm[str(k)][r] for r in ("S4", "S2a", "S5k")) and not adm[str(k)]["S5"] and not adm[str(k)]["S3"]]
    b = adm[str(BOUNDARY)]
    verdict["C4_boundary"] = bool((not b["S5k"]) and b["S4"] and b["S2a"])
    # C5 called cells, only where the predicted admissible set equals the observed one (else the cell prediction is void by C3/C4)
    wrong = {}; n_called = {}; void = []
    for k in ALL_K:
        obs_adm = sorted(r for r in ("S4", "S2a", "S5k") if adm[str(k)][r])
        if obs_adm != sorted(pred["per_k"][str(k)]["predicted_admissible"]):
            void.append(k); continue
        w = []; n = 0
        for key, cell in pred["per_k"][str(k)]["cells"].items():
            if cell["predicted"] == "ABSTAIN": continue
            n += 1
            if cell["predicted"] not in obs[k]["frontier_H_r"][key]:
                w.append({"cell": key, "predicted": cell["predicted"], "observed": obs[k]["frontier_H_r"][key]})
        wrong[str(k)] = w; n_called[str(k)] = n
    verdict["C5_all_called_cells_correct"] = bool(wrong) and all(not w for w in wrong.values()); verdict["C5_n_called"] = n_called
    verdict["C5_n_wrong"] = {k: len(w) for k, w in wrong.items()}; verdict["C5_wrong_cells"] = {k: w[:10] for k, w in wrong.items()}; verdict["C5_void_k_admissible_set_differs"] = void
    # C6 structure at the three-class ks
    c6 = {}
    for k in verdict["three_class_ks"]:
        for col in cols:
            r0 = all("S2a" in obs[k]["frontier_H_r"][f"{col}|H={Hh}|r=0"] for Hh in H_GRID)
            seq = [obs[k]["frontier_H_r"][f"{col}|H={Hh}|r=8"] for Hh in H_GRID]
            hstar = pred["per_k"][str(k)]["predicted_Hstar_S5k_to_S4_by_r"][col]["8"]
            if hstar is None:
                ok = all("S5k" in s for s in seq); regime = "no crossing: S5k every H"
            elif hstar < 1:
                ok = all("S4" in s for s in seq); regime = "H* < 1: S4 every H"
            elif hstar > 128:
                ok = all("S5k" in s for s in seq); regime = "H* > 128: S5k every H"
            else:
                sw = None
                for i in range(1, len(H_GRID)):
                    if "S5k" in seq[i - 1] and "S4" in seq[i] and "S5k" not in seq[i]: sw = (H_GRID[i - 1], H_GRID[i]); break
                ok = sw is not None and sw[0] <= hstar <= sw[1]; regime = f"switch interval {sw} vs H* {hstar}"
            c6[f"{k}|{col}"] = {"S2a_wins_r0_every_H": r0, "r8_by_H": seq, "regime": regime, "ok": bool(r0 and ok)}
    verdict["C6_structure"] = bool(c6) and all(v["ok"] for v in c6.values()); verdict["C6_detail"] = c6
    keys = ["C1_S5k_closed_form", "C2_S5_closed_form", "C3_three_classes", "C4_boundary", "C5_all_called_cells_correct", "C6_structure", "C7_S5k_strictly_decreasing_in_k"]
    verdict["all_claims_hold"] = all(verdict[x] for x in keys)
    out = {"schema": "StageDESymVerdictV1", "issue": 377, "revival_record": "RV-377-021", "verdict": verdict}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, "STAGE_DE_SYM_VERDICT.json"), "w"), indent=1, sort_keys=True, default=str)
    return out


if __name__ == "__main__":
    o = main(); v = o["verdict"]
    print({k: v[k] for k in v if k.startswith("C") and not k.endswith("detail") and "wrong" not in k and "called" not in k and "void" not in k})
    print("all_claims_hold:", v["all_claims_hold"], "| admissible:", v["admissible_by_k"])
    print("C1:", v["C1_detail"]); print("C2:", v["C2_detail"])
    print("C5 wrong:", v["C5_n_wrong"], "void:", v["C5_void_k_admissible_set_differs"])
    for key, c in v["C6_detail"].items(): print("  C6", key.split("|")[0], key.split("|")[1].split("_")[0], c["regime"], c["ok"], c["r8_by_H"])
