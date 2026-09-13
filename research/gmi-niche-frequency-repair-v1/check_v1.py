"""Pure-math and retained-record checks; no native evaluator is imported or called."""
from fractions import Fraction as F
from itertools import product
import hashlib
import json
from pathlib import Path
from grid_v1 import full_grid
from joint_law_v1 import achieved, controls, sandwich
from record_audit_v1 import audit, load

HERE = Path(__file__).resolve().parent


def source_check():
    source = json.loads((HERE / "SOURCE_BINDINGS_V1.json").read_text())
    for row in source["files"]:
        data = (HERE / row["path"]).read_bytes()
        if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError("source mismatch: " + row["path"])
    return len(source["files"])


def band_census():
    grid = (F(0), F(1, 2), F(1))
    valid, rejected = 0, 0
    for b0, s0, b1, s1 in product(grid, repeat=4):
        atoms = [(F(1, 2), b0, s0), (F(1, 2), b1, s1)]
        for c, epsilon, gamma, theta in product(grid, (F(0), F(1, 2)), grid, grid):
            error_mass = F((abs(s0 - c) > epsilon) + (abs(s1 - c) > epsilon), 2)
            if error_mass > gamma:
                rejected += 1
                continue
            lo, hi = sandwich(atoms, c, epsilon, gamma, theta, F(1, 2))
            expected = F((s0 >= theta and s0 - b0 >= F(1, 2)) +
                         (s1 >= theta and s1 - b1 >= F(1, 2)), 2)
            if achieved(atoms, theta, F(1, 2)) != expected or not lo <= expected <= hi:
                raise ValueError("finite joint-event band counterexample")
            valid += 1
    return {"valid_approximation_contracts": valid,
            "contracts_outside_stated_assumptions": rejected,
            "complete_atom_score_grid": ["0", "1/2", "1"]}


def late_controls(grid):
    histogram = {int(k): v for k, v in grid["loss_histogram"].items()}
    forbidden = sum(n for loss, n in histogram.items() if 1 - F(loss, 192) > F(23, 24))
    headroom = sum(n for loss, n in histogram.items()
                   if F("0.9653") - F(1, 24) < 1 - F(loss, 192) <= F(23, 24))
    return {"literal_09583_exclusion_counterexample": {"B": "23/24", "S": "1",
                "above_literal_decimal": F(23, 24) > F("0.9583"), "admissible": 1 - F(23, 24) >= F(1, 24)},
            "new_grid_capacity_forbidden_mass": str(F(forbidden, 17 ** 4)),
            "new_grid_hypothetical_headroom_mass": str(F(headroom, 17 ** 4)),
            "descriptor_only_noncarrier_enrichment": str(F(1, 2) / F(1, 10))}


def run():
    grid = full_grid()
    if grid != json.loads((HERE / "raw/EXACT_GRID_V1.json").read_text()):
        raise ValueError("retained full-grid result mismatch")
    return {"schema": "NicheFrequencyRepairV1", "status": "PASS",
            "source_files_checked": source_check(), "late_source_controls": late_controls(grid), "record_audit": audit(load()),
            "joint_event_controls": controls(), "band_census": band_census(),
            "new_exact_analytical_grid": grid, "native_or_campaign_calls": 0,
            "claim_ceiling": "joint-event theorem and conditional CDF bounds; achieved population frequency unmeasured"}
