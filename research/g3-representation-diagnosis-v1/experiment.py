"""Run frozen G3.4 witnesses; timeout-only must not JUMP."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from diagnose import (
    Diagnosis,
    classify,
    features_for,
    frozen_cases,
    parent_always_representation,
    parent_search_more,
    parent_timeout_jump,
)


def main(out: Path) -> dict:
    rows = []
    for case in frozen_cases():
        feat = features_for(case)
        pred = classify(feat)
        truth = Diagnosis(case["truth_reserved"])
        rows.append({
            "id": case["id"],
            "predicted": pred.value,
            "independent_truth": truth.value,
            "correct": pred is truth,
            "features": feat.__dict__,
            "timeout_jump_parent": parent_timeout_jump(feat).value,
            "search_more_parent": parent_search_more(feat).value,
            "repr_parent": parent_always_representation(feat).value,
        })
    timeout = next(r for r in rows if r["id"] == "timeout-only")
    jump_refused = timeout["predicted"] != Diagnosis.JUMP.value
    timeout_parent_jumps = timeout["timeout_jump_parent"] == Diagnosis.JUMP.value
    n_ok = sum(r["correct"] for r in rows)
    parent_more_wrong = sum(parent_search_more(features_for(c)) is not Diagnosis(c["truth_reserved"]) for c in frozen_cases())
    parent_repr_wrong = sum(parent_always_representation(features_for(c)) is not Diagnosis(c["truth_reserved"]) for c in frozen_cases())
    terminal = (
        "REPRESENTATION_CHANNEL_INSUFFICIENT"
        if not jump_refused
        else "PARENT_SUFFICIENT"
        if n_ok == len(rows) and parent_more_wrong == 0
        else "REPRESENTATION_CHANGE_CAUSALLY_USEFUL"
        if n_ok == len(rows) and jump_refused and timeout_parent_jumps
        else "CANNOT_CHECK_DIAGNOSIS_MISMATCH"
        if n_ok < len(rows)
        else "REPRESENTATION_CHANGE_CAUSALLY_USEFUL"
    )
    # Diagnosis utility is identification, not search savings. Prefer a precise terminal.
    if n_ok == len(rows) and jump_refused:
        terminal = "REPRESENTATION_INSUFFICIENCY_DIAGNOSIS_SUPPORTED_AT_SCOPE"
    result = {
        "schema": "ocm.g3.representation-diagnosis.v1",
        "terminal": terminal,
        "n_cases": len(rows),
        "n_correct": n_ok,
        "jump_refused_on_timeout": jump_refused,
        "timeout_parent_emits_jump": timeout_parent_jumps,
        "search_more_parent_errors": parent_more_wrong,
        "repr_parent_errors": parent_repr_wrong,
        "rows": rows,
        "claim_ceiling": "Legal-feature diagnosis on frozen polynomial witnesses. Not a JUMP license.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({"terminal": terminal, "n_correct": n_ok, "n": len(rows), "jump_refused": jump_refused}))
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
