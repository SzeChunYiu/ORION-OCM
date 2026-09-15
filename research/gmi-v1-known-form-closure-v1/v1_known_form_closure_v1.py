"""Executable V1 known-form closure audit (#602 V1/P0)."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LEDGER = HERE / "FAMILY_LEDGER_V1.json"
DISPOSITION = HERE / "V1_BOX_DISPOSITION_V1.json"
REPAIR = HERE / "NEGATIVE_REPAIR_PLAN_V1.json"
P0 = HERE / "P0_ZERO_PRIOR_ROWS_V1.json"
RECEIPT = HERE / "RECEIPT_V1.json"
TERMINAL = "KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE"
Z_ORDER = {"Z0": 0, "Z1": 1, "Z2": 2, "Z3": 3, "Z4": 4}


def z_at_least(z: str, need: str) -> bool:
    return Z_ORDER.get(z, -1) >= Z_ORDER[need]


def run():
    ledger = json.loads(LEDGER.read_text())
    families = ledger["families"]
    missing_ev = []
    for f in families:
        for ev in f.get("evidence") or []:
            if not (REPO / ev).exists() and not Path(ev).exists():
                # paths in ledger are repo-relative
                if not (REPO / ev).exists():
                    missing_ev.append({"family_id": f["family_id"], "path": ev})

    all_ge_z2 = all(z_at_least(f.get("z_earned", "Z0"), "Z2") for f in families)
    frontier_rows = []
    for fid in ledger["frontier_z3_required"]:
        f = next(x for x in families if x["family_id"] == fid)
        z = f.get("z_earned", "Z0")
        typed = f.get("gap") is not None or f.get("negative_twin") is not None
        frontier_rows.append(
            {
                "family_id": fid,
                "z_earned": z,
                "z3_ok": z_at_least(z, "Z3"),
                "typed_open_ok": typed and not z_at_least(z, "Z3"),
            }
        )

    boxes = {
        "V1_1_ledger_complete_for_ml_practice": {
            "tick": len(ledger["ml_practice_checklist"]) >= 20 and len(families) >= 20,
            "detail": {
                "n_checklist": len(ledger["ml_practice_checklist"]),
                "n_families": len(families),
            },
        },
        "V1_2_every_family_ge_Z2": {
            "tick": all_ge_z2 and not missing_ev,
            "detail": {"all_ge_z2": all_ge_z2, "n_missing_evidence": len(missing_ev)},
        },
        "V1_3_frontier_Z3_or_typed": {
            "tick": all(r["z3_ok"] or r["typed_open_ok"] for r in frontier_rows),
            "detail": {"frontier_rows": frontier_rows},
        },
        "V1_4_Z4_claims_typed": {
            "tick": all(
                (f.get("z4_status") is not None) or z_at_least(f.get("z_earned", "Z0"), "Z4")
                for f in families
            ),
            "detail": {"n_families": len(families)},
        },
        "V1_5_no_untyped_blocking_gap": {
            "tick": all(bool(f.get("falsifier")) for f in families),
            "detail": {
                "families_missing_falsifier": [
                    f["family_id"] for f in families if not f.get("falsifier")
                ]
            },
        },
    }
    all_green = all(b["tick"] for b in boxes.values())
    disposition = {
        "schema": "GMIV1BoxDispositionV1",
        "boxes": boxes,
        "all_v1_boxes_green": all_green,
        "terminal": TERMINAL if all_green else "V1_INCOMPLETE",
        "claim_ceiling": ledger["claim_ceiling"],
    }
    DISPOSITION.write_text(json.dumps(disposition, indent=2, sort_keys=True) + "\n")

    repair = []
    for f in families:
        z = f.get("z_earned", "Z0")
        if not z_at_least(z, "Z3"):
            repair.append(
                {
                    "family_id": f["family_id"],
                    "current_z": z,
                    "target_z": "Z3",
                    "gap_type": f.get("gap") or "Z3_NOT_YET_EARNED_AT_REGISTERED_SCOPE",
                    "falsifier": f.get("falsifier"),
                    "next_experiment": f"Neutral remint recovery on {f['family_id']}",
                }
            )
    REPAIR.write_text(
        json.dumps({"schema": "GMINegativeRepairPlanV1", "rows": repair}, indent=2, sort_keys=True)
        + "\n"
    )

    p0_rows = []
    for f in families:
        if f.get("priority") != "P0":
            continue
        exact = any("EXACT" in e and (REPO / e).exists() for e in (f.get("evidence") or []))
        p0_rows.append(
            {
                "family_id": f["family_id"],
                "disposition": "CLOSED_EXACT_LAYER" if exact else "TYPED_OPEN",
                "z_earned": f.get("z_earned"),
                "evidence": f.get("evidence"),
            }
        )
    P0.write_text(
        json.dumps({"schema": "GMIP0ZeroPriorRowsV1", "rows": p0_rows}, indent=2, sort_keys=True)
        + "\n"
    )

    out = {
        "schema": "GMIV1KnownFormClosureReceiptV1",
        "artifact": "GMI_V1_KNOWN_FORM_CLOSURE_V1",
        "issue_refs": ["#602", "#431", "#433"],
        "boxes": boxes,
        "all_v1_boxes_green": all_green,
        "n_families": len(families),
        "n_p0": len(p0_rows),
        "n_repair_rows": len(repair),
        "terminal": disposition["terminal"],
        "claim_ceiling": ledger["claim_ceiling"],
        "forbidden": ["ALL_ML_PRACTICE_DERIVED", "UNIVERSAL_Z4", "LIVING_REGISTRY_FULL_CLOSURE"],
    }
    RECEIPT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
