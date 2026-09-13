"""Audit all retained aggregate cells as printed decimals, not invented native traces."""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import json
from grid_v1 import baseline

HERE = Path(__file__).resolve().parent
ROWS = ("compiled_search", "constant_emitter", "exemplar_table", "gradient_net_h2",
        "gradient_net_h4", "hamming_knn_k3", "particles_p4", "program_search", "soft_retrieval")
V1 = ("standard", "no_revoke", "double_revoke", "half_events",
      "shuffled_events", "extra_unseen_feedback")


def load():
    return json.loads((HERE / "raw/upstream/STAGE_NICHE_FREQUENCY_V1.json").read_text(), parse_float=F)


def audit(packet):
    names = {"E_niche" + str(i) for i in range(1, 13)}
    if set(packet["ecologies"]) != names or set(packet["results"]) != names:
        raise ValueError("missing/extra ecology")
    if tuple(packet["interventions"]) != V1:
        raise ValueError("historical record must retain exact V1 label scope")
    if packet["seed"] != int(hashlib.sha256(b"GMI-NICHE-FREQ-V1").hexdigest()[:8], 16):
        raise ValueError("declared seed mismatch")
    counts, threshold_counts = dict.fromkeys(ROWS, 0), dict.fromkeys(ROWS, 0)
    cells, exact_baselines, sensitivity = [], {}, []
    lattice_changes = []
    lattice_counts = dict.fromkeys(ROWS, 0)
    for task in sorted(names, key=lambda x: int(x[7:])):
        coeffs = packet["ecologies"][task]
        k = [c * 16 for c in coeffs]
        if any(x.denominator != 1 for x in k):
            raise ValueError("coefficient off declared grid")
        exact = baseline(tuple(int(x) for x in k))
        rowset = packet["results"][task]
        b = rowset["best_constant"]
        if round(exact, 4) != b or set(rowset["rows"]) != set(ROWS):
            raise ValueError("baseline or row membership mismatch")
        exact_baselines[task] = str(exact)
        for name in ROWS:
            row = rowset["rows"][name]
            s, margin = row["min_over_six"], row["margin_fx"]
            if not 0 <= s <= 1 or round(24 * (s - b), 3) != margin:
                raise ValueError("printed margin disagreement")
            decision = s >= F(17, 20) and margin >= 1
            if type(row["admissible"]) is not bool or row["admissible"] != decision:
                raise ValueError("printed decision disagreement")
            counts[name] += decision
            threshold_counts[name] += s >= F(17, 20)
            # Four-decimal score intervals; exact baseline is independently derived.
            lo, hi = max(F(0), s - F(1, 20000)), min(F(1), s + F(1, 20000))
            possible = hi >= F(17, 20) and hi - exact >= F(1, 24)
            guaranteed = lo >= F(17, 20) and lo - exact >= F(1, 24)
            if possible != guaranteed:
                sensitivity.append([task, name])
            compatible = [F(k, 192) for k in range(193) if round(F(k, 192), 4) == s]
            if len(compatible) != 1:
                raise ValueError("display incompatible with conditional native eight-input lattice")
            exact_score = compatible[0]
            exact_decision = exact_score >= F(17, 20) and exact_score - exact >= F(1, 24)
            lattice_counts[name] += exact_decision
            if decision != exact_decision:
                lattice_changes.append([task, name, decision, exact_decision, str(exact_score - exact)])
            cells.append({"task": task, "row": name, "score": str(s), "printed_baseline": str(b),
                          "margin": str(margin), "printed_admissible": decision,
                          "conditional_eight_input_unrounded_score": str(exact_score),
                          "rounding_interval_possible": possible, "rounding_interval_guaranteed": guaranteed})
    scores = {name: [packet["results"][t]["rows"][name]["min_over_six"] for t in names] for name in ROWS}
    return {"tasks": 12, "cells": cells, "cell_count": len(cells), "counts": counts,
            "threshold_only_counts": threshold_counts, "exact_baselines": exact_baselines,
            "frequencies_on_record": {k: str(F(v, 12)) for k, v in counts.items()},
            "mean_printed_baseline": str(sum(packet["results"][t]["best_constant"] for t in names) / 12),
            "score_ranges": {k: [str(min(v)), str(max(v))] for k, v in scores.items()},
            "N4_strict": counts["program_search"] > counts["hamming_knn_k3"] > counts["soft_retrieval"] > counts["gradient_net_h2"],
            "N4_noninversion": counts["program_search"] >= counts["hamming_knn_k3"] >= counts["soft_retrieval"] >= counts["gradient_net_h2"],
            "precision_sensitive_cells": sensitivity,
            "conditional_unrounded_gate_counts": lattice_counts,
            "conditional_unrounded_changes": lattice_changes, "distinct_coefficient_tuples": len({tuple(v) for v in packet["ecologies"].values()}),
            "scope": "108 internally checked printed aggregate records under named V1; population law unverified"}
