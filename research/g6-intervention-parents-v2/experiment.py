"""G6.1 remaining parent comparison on the frozen synthetic plant.

Does not overwrite ``research/g6-intervention-lab-v1/``. AutoML/BO is not invented.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from parents import (
    automl_bo_status,
    fit_atms,
    fit_evolutionary,
    fit_learned_selector,
    fit_program_repair,
    fit_structured_surrogate,
    fit_system_id,
    run_parent,
)
from plant import clone_cohort, load_lab

SALT = "orion-ocm-g6-intervention-parents-v2"
GEN_N = 8
SCHEMA = "ocm.g6.intervention-parents.v2"
V1_DIR = "research/g6-intervention-lab-v1"
V1_UNTOUCHED = True

PARENT_ORDER = (
    "learned_selector",
    "system_id",
    "structured_surrogate",
    "atms_change_impact",
    "evolutionary",
    "program_repair",
)


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    return {
        "n": n,
        "quality": sum(r["quality"] for r in rows) / n,
        "identified": sum(r["identified"] for r in rows) / n,
        "cost": sum(r["cost"] for r in rows),
        "kappa": sum(r["kappa"] for r in rows) / n,
        "omega": sum(r["omega"] for r in rows) / n,
        "chi": sum(r["chi"] for r in rows) / n,
        "n_probes": sum(r["n_probes"] for r in rows),
        "n_replaced": sum(r["n_replaced"] for r in rows),
    }


def collect_grid_transcripts(Lab, incidents, rng: random.Random) -> list[dict]:
    transcripts = []
    for incident in incidents:
        Lab.diagnose_and_repair(incident, "grid", rng)
        transcripts.append(incident.transcript)
    return transcripts


def fit_all(transcripts, Lab, rng: random.Random) -> dict:
    return {
        "learned_selector": fit_learned_selector(transcripts, Lab),
        "system_id": fit_system_id(transcripts, Lab),
        "structured_surrogate": fit_structured_surrogate(transcripts, Lab),
        "atms_change_impact": fit_atms(transcripts, Lab),
        "evolutionary": fit_evolutionary(transcripts, Lab, rng),
        "program_repair": fit_program_repair(transcripts, Lab),
    }


def evaluate(name: str, Lab, incidents, model, rng: random.Random) -> list[dict]:
    rows = []
    for incident in incidents:
        rows.append(run_parent(name, Lab, incident, model, rng))
    return rows


def _model_public(models: dict) -> dict:
    out = {}
    for name, model in models.items():
        pub = {k: v for k, v in model.items() if k != "ks"}
        if name == "atms_change_impact":
            pub["n_atoms"] = len(model["ks"].atoms)
        out[name] = pub
    return out


def decide_terminal(scores: dict, automl: dict) -> str:
    ocm = scores["learned_selector"]
    runnable = {k: v for k, v in scores.items() if k != "learned_selector"}
    parent_solves = any(v["quality"] == 1.0 for v in runnable.values())
    parent_beats = any(
        (v["quality"] > ocm["quality"])
        or (v["quality"] == ocm["quality"] and v["cost"] < ocm["cost"])
        for v in runnable.values()
    )
    if automl["status"] == "CANNOT_CHECK_NO_BO_LIBRARY" and not parent_solves:
        return "CANNOT_CHECK_NO_BO_LIBRARY"
    if parent_beats or parent_solves:
        return "PARENT_SUFFICIENT"
    return "NO_MULTI_GENERATION_IMPROVEMENT"


def compare_against(scores: dict, automl: dict) -> dict:
    earned = {}
    mapping = {
        "system-identification": "system_id",
        "structured surrogate": "structured_surrogate",
        "ATMS/change-impact": "atms_change_impact",
        "evolutionary search": "evolutionary",
        "program repair": "program_repair",
        "learned selector": "learned_selector",
    }
    for bullet, key in mapping.items():
        row = scores[key]
        earned[bullet] = {
            "status": "EARNED",
            "quality": row["quality"],
            "cost": row["cost"],
            "identified": row["identified"],
        }
    earned["AutoML/BO"] = {
        "status": automl["status"],
        "invented": False,
        "tried": automl["tried"],
    }
    earned["human-designed repair"] = {
        "status": "NOT_THIS_CAPSULE",
        "note": "Remaining G6.1 compare-against for this successor is the five research parents plus AutoML/BO library gate.",
    }
    return earned


def main(out: Path) -> dict:
    Lab = load_lab()
    rng = random.Random(16561)
    seen: set = set()
    train = Lab.make_incidents(0, GEN_N, SALT, disjoint_from=seen)
    heldout = Lab.make_incidents(1, GEN_N, SALT, disjoint_from=seen)
    assert len({i.hidden.stuck for i in train + heldout}) == 2 * GEN_N

    transcripts = collect_grid_transcripts(Lab, clone_cohort(Lab, train), rng)
    # Fit uses unlabeled transcripts only — no hidden.stuck.
    for row in transcripts:
        assert "stuck" not in row
        assert "hidden" not in row

    models = fit_all(transcripts, Lab, random.Random(16562))
    automl = automl_bo_status()

    scores = {}
    per_incident = {}
    for name in PARENT_ORDER:
        rows = evaluate(name, Lab, clone_cohort(Lab, heldout), models[name], random.Random(16563))
        scores[name] = summarize(rows)
        per_incident[name] = [
            {"quality": r["quality"], "cost": r["cost"], "identified": r["identified"], "n_probes": r["n_probes"]}
            for r in rows
        ]

    bullets = compare_against(scores, automl)
    terminal = decide_terminal(scores, automl)
    ranking = sorted(scores.items(), key=lambda kv: (-kv[1]["quality"], kv[1]["cost"], kv[0]))
    winner = ranking[0][0]

    result = {
        "schema": SCHEMA,
        "terminal": terminal,
        "salt": SALT,
        "claim_ceiling": (
            "Bounded synthetic plant parent comparison. Not production M11 self-evolution. "
            "v1 laboratory is frozen. AutoML/BO is CANNOT_CHECK_NO_BO_LIBRARY."
        ),
        "v1_frozen": {
            "dir": V1_DIR,
            "untouched": V1_UNTOUCHED,
            "not_overwritten": True,
        },
        "historical_m11_relabeled": False,
        "root_cause_labels_supplied": False,
        "train_n": len(train),
        "heldout_n": len(heldout),
        "disjoint": True,
        "automl_bo": automl,
        "models": _model_public(models),
        "scores": scores,
        "ranking": [{"parent": name, **summary} for name, summary in ranking],
        "winner": winner,
        "compare_against": bullets,
        "earned_bullets": [k for k, v in bullets.items() if v.get("status") == "EARNED"],
        "cannot_check": [k for k, v in bullets.items() if str(v.get("status", "")).startswith("CANNOT_CHECK")],
        "per_incident": per_incident,
        "constitution": sorted(Lab.CONSTITUTION),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"terminal": terminal, "ranking": result["ranking"], "cannot_check": result["cannot_check"]}, indent=2))
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
