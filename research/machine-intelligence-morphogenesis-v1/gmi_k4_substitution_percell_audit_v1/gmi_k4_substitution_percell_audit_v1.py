"""Per-cell audit: which of 159 THEORY_RED cells admit substitution under repaired pricing.

Thin MIM-lane wrapper over research/gmi-k4-substitution-cell-audit-v2/ classification,
adding the repaired-pricing admission predicate (R1/R2/R3 expressed kinds + stage
material_trade). Does not mutate frozen V4/V7 or rewrite frozen verdicts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIM = HERE.parent
REPO = MIM.parent.parent
V2 = REPO / "research" / "gmi-k4-substitution-cell-audit-v2"
SWEEP_PATH = MIM / "GMI_K4_V5_DEV_SWEEP_RV_377_107.json"
LOFO_PATH = MIM / "GMI_K4_LOFO_FREEZE_V1.json"
REPAIR_STAGE_PATH = MIM / "microscopes" / "results" / "STAGE_K4_SUBSTITUTION_REPAIR_V1.json"
OUT_STAGE_PATH = MIM / "microscopes" / "results" / "STAGE_K4_SUBSTITUTION_PERCELL_AUDIT_V1.json"
PACKAGE_STAGE_PATH = HERE / "STAGE_K4_SUBSTITUTION_PERCELL_AUDIT_V1.json"
RECEIPT_PATH = HERE / "RECEIPT_V1.json"
LEDGER_PATH = HERE / "AUDIT_LEDGER_V1.json"

if str(V2) not in sys.path:
    sys.path.insert(0, str(V2))
import cell_audit_v1 as v2  # noqa: E402

SCHEMA = "GMIK4SubstitutionPercellAuditReceiptV1"
AUDIT_ID = "GMI_K4_SUBSTITUTION_PERCELL_AUDIT_V1"
N_THEORY_RED = 159

REPAIR_EXPRESSED_KINDS = frozenset(
    {
        "retention_caching",
        "external_authority",
        "amortisation",
        "parameter_sharing",
    }
)
REPAIR_UNEXPRESSED_KINDS = frozenset(
    {"sparsity_specialisation", "latent_compression"}
)

classify_property_vector = v2.classify_property_vector
substitution_hits = v2.substitution_hits


def repair_expressed_kinds(kinds):
    return [k for k in kinds if k in REPAIR_EXPRESSED_KINDS]


def load_repair_admission(stage_path=None):
    path = Path(stage_path) if stage_path is not None else REPAIR_STAGE_PATH
    stage = json.loads(path.read_text())
    q1 = stage.get("q1") or {}
    repaired = q1.get("R1+R2 repaired") or {}
    frozen = q1.get("frozen v4") or {}
    if repaired.get("material_trade") is not True:
        raise AssertionError("repair stage missing material_trade under R1+R2")
    if frozen.get("material_trade") is not False:
        raise AssertionError("frozen v4 material_trade control drifted")
    return {
        "path": "microscopes/results/STAGE_K4_SUBSTITUTION_REPAIR_V1.json",
        "repaired_material_trade": True,
        "frozen_material_trade": False,
        "repaired_corr": repaired.get("corr"),
        "frozen_corr": frozen.get("corr"),
        "recovery_repaired": (stage.get("recovery") or {}).get("repaired"),
        "recovery_frozen": (stage.get("recovery") or {}).get("frozen"),
    }


def load_theory_red_bundle(sweep_path=None, lofo_path=None):
    sweep_path = Path(sweep_path) if sweep_path is not None else SWEEP_PATH
    lofo_path = Path(lofo_path) if lofo_path is not None else LOFO_PATH
    v2_input = V2 / "AUDIT_INPUT_V1.json"
    if v2_input.is_file():
        obj = json.loads(v2_input.read_text())
        if len(obj.get("cells") or []) != N_THEORY_RED:
            raise AssertionError("v2 AUDIT_INPUT_V1.json cell count != 159")
        return {
            "schema": "GMIK4SubstitutionPercellAuditInputV1",
            "source_sweep": obj.get("source_sweep"),
            "source_freeze": obj.get("source_freeze"),
            "n_theory_red": N_THEORY_RED,
            "cells": obj["cells"],
            "family_property_vectors": obj["family_property_vectors"],
        }
    sweep = json.loads(sweep_path.read_text())
    cells = [
        {
            "family": row["family"],
            "grammar": row["grammar"],
            "cell": row["cell"],
            "verdict": row["verdict"],
            "status": row.get("status"),
            "reason": row.get("reason"),
        }
        for row in sweep
        if row.get("verdict") == "THEORY_RED"
    ]
    if len(cells) != N_THEORY_RED:
        raise AssertionError(
            "expected %d THEORY_RED cells, got %d" % (N_THEORY_RED, len(cells))
        )
    lofo = json.loads(lofo_path.read_text())
    families = lofo.get("families") or {}
    vectors = {
        fam: dict(families[fam]["property_vector"])
        for fam in sorted(set(c["family"] for c in cells))
    }
    return {
        "schema": "GMIK4SubstitutionPercellAuditInputV1",
        "source_sweep": sweep_path.name,
        "source_freeze": lofo_path.name,
        "n_theory_red": len(cells),
        "cells": cells,
        "family_property_vectors": vectors,
    }


def classify_cell(cell, family_vectors, repair_ok):
    family = cell["family"]
    cls = classify_property_vector(family_vectors[family])
    kinds = cls["substitution_kinds"]
    expressed = repair_expressed_kinds(kinds)
    admits = bool(expressed) and bool(repair_ok)
    if admits:
        admit_reason = (
            "targets %s; repaired pricing expresses %s; stage material_trade holds"
            % (kinds, expressed)
        )
    elif cls["targets_substitution"] and not expressed:
        admit_reason = (
            "targets %s but none expressed by R1/R2/R3 (unexpressed=%s)"
            % (kinds, [k for k in kinds if k in REPAIR_UNEXPRESSED_KINDS])
        )
    elif not cls["targets_substitution"]:
        admit_reason = "non-substitution target (%s)" % cls["reason"]
    else:
        admit_reason = "repair material_trade missing"
    return {
        "schema": "GMIK4SubstitutionPercellAuditCellV1",
        "family": family,
        "grammar": cell["grammar"],
        "cell": cell["cell"],
        "frozen_verdict": cell.get("verdict"),
        "frozen_status": cell.get("status"),
        "targets_substitution": cls["targets_substitution"],
        "admits_substitution_under_repaired_pricing": admits,
        "substitution_kinds": kinds,
        "repair_expressed_kinds": expressed,
        "primary_kind": cls["primary_kind"],
        "reason": cls["reason"],
        "admission_reason": admit_reason,
        "claim_label": "admissible",
        "frozen_verdict_rewritten": False,
    }


def run_audit(bundle=None, repair_info=None):
    repair_info = repair_info if repair_info is not None else load_repair_admission()
    repair_ok = repair_info["repaired_material_trade"] is True
    obj = bundle if bundle is not None else load_theory_red_bundle()
    vectors = obj["family_property_vectors"]
    cells_out = [classify_cell(c, vectors, repair_ok) for c in obj["cells"]]

    n_target_yes = sum(1 for c in cells_out if c["targets_substitution"])
    n_target_no = len(cells_out) - n_target_yes
    n_admit_yes = sum(
        1 for c in cells_out if c["admits_substitution_under_repaired_pricing"]
    )
    n_admit_no = len(cells_out) - n_admit_yes
    if n_target_yes + n_target_no != N_THEORY_RED:
        raise AssertionError("target partition broken")
    if n_admit_yes + n_admit_no != N_THEORY_RED:
        raise AssertionError("admission partition broken")

    by_family = {}
    for c in cells_out:
        fam = c["family"]
        slot = by_family.setdefault(
            fam,
            {
                "n_cells": 0,
                "targets_substitution_yes": 0,
                "admits_under_repaired_yes": 0,
                "primary_kind": None,
                "repair_expressed_kinds": [],
            },
        )
        slot["n_cells"] += 1
        if c["targets_substitution"]:
            slot["targets_substitution_yes"] += 1
            slot["primary_kind"] = c["primary_kind"]
        if c["admits_substitution_under_repaired_pricing"]:
            slot["admits_under_repaired_yes"] += 1
            slot["repair_expressed_kinds"] = list(c["repair_expressed_kinds"])

    kind_counts = {}
    for c in cells_out:
        for k in c["substitution_kinds"]:
            kind_counts[k] = kind_counts.get(k, 0) + 1

    families_target_yes = sorted(
        fam for fam, s in by_family.items() if s["targets_substitution_yes"] > 0
    )
    families_admit_yes = sorted(
        fam for fam, s in by_family.items() if s["admits_under_repaired_yes"] > 0
    )
    families_target_yes_admit_no = sorted(
        fam
        for fam, s in by_family.items()
        if s["targets_substitution_yes"] > 0 and s["admits_under_repaired_yes"] == 0
    )

    return {
        "schema": SCHEMA,
        "audit_id": AUDIT_ID,
        "closes": {
            "issues": ["#592", "#602"],
            "checklist_items": ["22", "23", "35"],
            "remaining_clause": "a",
            "clause_text": (
                "per-cell audit of which of the 159 admit a substitution under "
                "the repaired pricing"
            ),
        },
        "source": {
            "sweep": obj.get("source_sweep"),
            "freeze": obj.get("source_freeze"),
            "n_theory_red": obj.get("n_theory_red"),
            "repair_stage": repair_info,
            "classifier": "gmi-k4-substitution-cell-audit-v2/cell_audit_v1.py",
        },
        "cells": cells_out,
        "summary": {
            "n_cells": len(cells_out),
            "targets_substitution_yes": n_target_yes,
            "targets_substitution_no": n_target_no,
            "admits_under_repaired_yes": n_admit_yes,
            "admits_under_repaired_no": n_admit_no,
            "families_targets_yes": families_target_yes,
            "families_admits_yes": families_admit_yes,
            "families_targets_yes_admits_no": families_target_yes_admit_no,
            "kind_cell_hits": kind_counts,
            "repair_expressed_kinds": sorted(REPAIR_EXPRESSED_KINDS),
            "repair_unexpressed_kinds": sorted(REPAIR_UNEXPRESSED_KINDS),
            "by_family": by_family,
        },
        "claim_ceiling": {
            "admissible": (
                "Classifies which of the 159 frozen THEORY_RED cells have a "
                "substitution-defined target that repaired pricing (R1/R2/R3) "
                "makes expressible. NS-1 consequence 2 makes INCONCLUSIVE_GRAMMAR "
                "the admissible reading for those cells."
            ),
            "reachable": (
                "Does NOT claim any cell is reachable/green. Clause (c) "
                "(gmi_k4_repaired_campaign_v1) owns reachability."
            ),
            "parent_subtraction": (
                "Parents with first refusal: COST_STRUCTURE_ROOT_CAUSE, "
                "SUBSTITUTION_REPAIR, NS-1, and sibling cell-audit-v2 "
                "(targets-only). This package adds repaired-pricing admission only."
            ),
            "frozen_verdicts_rewritten": False,
            "frozen_model_mutated": False,
        },
        "frozen_verdicts_rewritten": False,
        "frozen_model_mutated": False,
    }


def compact_cell(cell):
    return {
        "admits_substitution_under_repaired_pricing": cell[
            "admits_substitution_under_repaired_pricing"
        ],
        "cell": cell["cell"],
        "family": cell["family"],
        "grammar": cell["grammar"],
        "primary_kind": cell["primary_kind"],
        "targets_substitution": cell["targets_substitution"],
    }


def write_outputs(receipt, stage_path=None, receipt_path=None):
    stage_path = Path(stage_path) if stage_path is not None else OUT_STAGE_PATH
    receipt_path = Path(receipt_path) if receipt_path is not None else RECEIPT_PATH
    out = dict(receipt)
    out["cells"] = [compact_cell(c) for c in receipt["cells"]]
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(text)
    stage_path.parent.mkdir(parents=True, exist_ok=True)
    stage_path.write_text(text)
    PACKAGE_STAGE_PATH.write_text(
        json.dumps(
            {
                "schema": "GMIK4SubstitutionPercellAuditCellsV1",
                "audit_id": AUDIT_ID,
                "n_cells": len(out["cells"]),
                "summary": {
                    "targets_substitution_yes": receipt["summary"][
                        "targets_substitution_yes"
                    ],
                    "targets_substitution_no": receipt["summary"][
                        "targets_substitution_no"
                    ],
                    "admits_under_repaired_yes": receipt["summary"][
                        "admits_under_repaired_yes"
                    ],
                    "admits_under_repaired_no": receipt["summary"][
                        "admits_under_repaired_no"
                    ],
                },
                "cells": out["cells"],
            },
            indent=1,
            sort_keys=True,
        )
        + "\n"
    )
    return stage_path, receipt_path


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    receipt = run_audit()
    receipt_path = Path(argv[0]) if argv else RECEIPT_PATH
    write_outputs(receipt, receipt_path=receipt_path)
    print(
        json.dumps(
            {
                "audit_id": receipt["audit_id"],
                "n_cells": receipt["summary"]["n_cells"],
                "targets_substitution_yes": receipt["summary"]["targets_substitution_yes"],
                "admits_under_repaired_yes": receipt["summary"]["admits_under_repaired_yes"],
                "families_admits_yes": receipt["summary"]["families_admits_yes"],
                "families_targets_yes_admits_no": receipt["summary"][
                    "families_targets_yes_admits_no"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
