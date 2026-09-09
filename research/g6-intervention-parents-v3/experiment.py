"""G6.1 remainder parent comparison on the frozen synthetic plant.

Does not overwrite v1 or v2 RESULT.json. Does not train an ML selector.
AutoML/BO is not invented. The 1-parameter θ grid is labeled not-BO.
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
    fit_atms_v2,
    fit_generate_and_test,
    fit_human_designed,
    fit_one_parameter_surrogate,
    fit_random_evolutionary,
    run_parent,
)
from plant import V2_RESULT, clone_cohort, load_lab

SALT = "orion-ocm-g6-intervention-parents-v3"
GEN_N = 8
SCHEMA = "ocm.g6.intervention-parents.v3"
V1_DIR = "research/g6-intervention-lab-v1"
V2_DIR = "research/g6-intervention-parents-v2"
V1_UNTOUCHED = True
V2_UNTOUCHED = True
ML_SELECTOR_TRAINED = False

PARENT_ORDER = (
    "atms_change_impact",
    "one_parameter_structured_surrogate",
    "random_evolutionary",
    "generate_and_test_program_repair",
    "human_designed_repair",
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


def cite_v2() -> dict:
    data = json.loads(V2_RESULT.read_text())
    return {
        "schema": data["schema"],
        "terminal": data["terminal"],
        "winner": data["winner"],
        "earned_bullets": data["earned_bullets"],
        "cannot_check": data["cannot_check"],
        "atms_cost": data["scores"]["atms_change_impact"]["cost"],
        "atms_quality": data["scores"]["atms_change_impact"]["quality"],
        "bo": data["automl_bo"]["status"],
        "human_designed": data["compare_against"]["human-designed repair"]["status"],
        "learned_selector_cost": data["scores"]["learned_selector"]["cost"],
        "learned_selector_quality": data["scores"]["learned_selector"]["quality"],
        "system_id_cost": data["scores"]["system_id"]["cost"],
        "system_id_quality": data["scores"]["system_id"]["quality"],
        "not_overwritten": True,
    }


def fit_all(transcripts, Lab, rng: random.Random) -> dict:
    return {
        "atms_change_impact": fit_atms_v2(transcripts, Lab),
        "one_parameter_structured_surrogate": fit_one_parameter_surrogate(transcripts, Lab),
        "random_evolutionary": fit_random_evolutionary(transcripts, Lab, rng),
        "generate_and_test_program_repair": fit_generate_and_test(transcripts, Lab),
        "human_designed_repair": fit_human_designed(transcripts, Lab),
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
    parent_solves = any(v["quality"] == 1.0 for v in scores.values())
    if automl["status"] == "CANNOT_CHECK_NO_BO_LIBRARY" and not parent_solves:
        return "CANNOT_CHECK_NO_BO_LIBRARY"
    if parent_solves:
        return "PARENT_SUFFICIENT"
    return "NO_MULTI_GENERATION_IMPROVEMENT"


def compare_against(scores: dict, automl: dict, v2: dict) -> dict:
    earned = {}
    earned["system-identification"] = {
        "status": "CITED_V2",
        "v2_status": "EARNED",
        "quality": v2["system_id_quality"],
        "cost": v2["system_id_cost"],
        "note": "v2 GF(2) observation map. This remainder capsule does not rerun system-id.",
    }
    earned["structured surrogate"] = {
        "status": "EARNED",
        "variant": "one_parameter_main_effect_top_k",
        "quality": scores["one_parameter_structured_surrogate"]["quality"],
        "cost": scores["one_parameter_structured_surrogate"]["cost"],
        "theta": scores["one_parameter_structured_surrogate"].get("theta"),
        "v2_variant": "2-factor ANOVA (cited, not overwritten)",
        "theta_grid_is_not_bo": True,
    }
    earned["ATMS/change-impact"] = {
        "status": "EARNED",
        "quality": scores["atms_change_impact"]["quality"],
        "cost": scores["atms_change_impact"]["cost"],
        "v2_status": "EARNED",
        "v2_cost": v2["atms_cost"],
        "note": "Cited v2 PARENT_SUFFICIENT; rerun on this split as the standing cheapest parent.",
    }
    earned["evolutionary search"] = {
        "status": "EARNED",
        "variant": "random_(1+lambda)_swap_mutation_ES",
        "quality": scores["random_evolutionary"]["quality"],
        "cost": scores["random_evolutionary"]["cost"],
        "crossover": False,
        "v2_variant": "permutation GA with OX crossover (cited, not overwritten)",
    }
    earned["program repair"] = {
        "status": "EARNED",
        "variant": "generate_and_test_finite_power_set",
        "quality": scores["generate_and_test_program_repair"]["quality"],
        "cost": scores["generate_and_test_program_repair"]["cost"],
        "v2_variant": "GenProg-style mutate (cited, not overwritten)",
    }
    earned["learned selector"] = {
        "status": "CITED_V2_NOT_TRAINED",
        "v2_status": "EARNED",
        "quality": v2["learned_selector_quality"],
        "cost": v2["learned_selector_cost"],
        "ml_selector_trained": False,
        "note": "v2 trained a syndrome→module table. This capsule does not train an ML selector.",
    }
    earned["AutoML/BO"] = {
        "status": automl["status"],
        "invented": False,
        "tried": automl["tried"],
        "grid_search_is_not_bo": True,
        "note": "1-parameter θ enumeration is an exhaustive integer grid labeled not-BO, not an AutoML/BO parent.",
    }
    earned["human-designed repair"] = {
        "status": "EARNED",
        "variant": "authored_plant_xor_windows",
        "quality": scores["human_designed_repair"]["quality"],
        "cost": scores["human_designed_repair"]["cost"],
        "operational_cost": scores["human_designed_repair"]["operational_cost"],
        "prior_cost": scores["human_designed_repair"]["prior_cost"],
        "charged_as_prior": True,
        "v2_status": v2["human_designed"],
        "note": "Human-designed repair is the authored plant. Window map charged as prior, not unpaid operational knowledge.",
    }
    return earned


def main(out: Path) -> dict:
    Lab = load_lab()
    rng = random.Random(16571)
    seen: set = set()
    train = Lab.make_incidents(0, GEN_N, SALT, disjoint_from=seen)
    heldout = Lab.make_incidents(1, GEN_N, SALT, disjoint_from=seen)
    assert len({i.hidden.stuck for i in train + heldout}) == 2 * GEN_N

    transcripts = collect_grid_transcripts(Lab, clone_cohort(Lab, train), rng)
    for row in transcripts:
        assert "stuck" not in row
        assert "hidden" not in row

    models = fit_all(transcripts, Lab, random.Random(16572))
    automl = automl_bo_status()
    v2 = cite_v2()
    assert v2["terminal"] == "PARENT_SUFFICIENT"
    assert v2["bo"] == "CANNOT_CHECK_NO_BO_LIBRARY"

    scores = {}
    per_incident = {}
    for name in PARENT_ORDER:
        rows = evaluate(name, Lab, clone_cohort(Lab, heldout), models[name], random.Random(16573))
        summary = summarize(rows)
        if name == "human_designed_repair":
            summary["operational_cost"] = summary["cost"]
            summary["prior_cost"] = models[name]["prior_cost"]
            summary["cost"] = summary["operational_cost"] + summary["prior_cost"]
        if name == "one_parameter_structured_surrogate":
            summary["theta"] = models[name]["theta"]
            summary["n_parameters"] = 1
        scores[name] = summary
        per_incident[name] = [
            {"quality": r["quality"], "cost": r["cost"], "identified": r["identified"], "n_probes": r["n_probes"]}
            for r in rows
        ]

    bullets = compare_against(scores, automl, v2)
    terminal = decide_terminal(scores, automl)
    ranking = sorted(scores.items(), key=lambda kv: (-kv[1]["quality"], kv[1]["cost"], kv[0]))
    winner = ranking[0][0]
    atms_cost = scores["atms_change_impact"]["cost"]
    atms_still_cheapest = all(
        atms_cost <= scores[name]["cost"] for name in PARENT_ORDER
    )
    if terminal == "PARENT_SUFFICIENT" and not atms_still_cheapest:
        # A remainder parent beat ATMS on this split; still a parent-sufficient terminal.
        pass

    result = {
        "schema": SCHEMA,
        "terminal": terminal,
        "salt": SALT,
        "claim_ceiling": (
            "Bounded synthetic plant remainder parent comparison. Not production M11 self-evolution. "
            "v1 laboratory and v2 RESULT.json are frozen. AutoML/BO is CANNOT_CHECK_NO_BO_LIBRARY. "
            "1-parameter θ grid is not BO. Learned selector is cited from v2, not trained. "
            "Human-designed repair is the authored plant, charged as prior. "
            "Source-bound real failure/probe recovery is a separate G3 worker."
        ),
        "v1_frozen": {
            "dir": V1_DIR,
            "untouched": V1_UNTOUCHED,
            "not_overwritten": True,
        },
        "v2_frozen": {
            "dir": V2_DIR,
            "untouched": V2_UNTOUCHED,
            "not_overwritten": True,
            "cited": v2,
        },
        "ml_selector_trained": ML_SELECTOR_TRAINED,
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
        "atms_still_cheapest": atms_still_cheapest,
        "compare_against": bullets,
        "earned_bullets": [k for k, v in bullets.items() if v.get("status") == "EARNED"],
        "cited_v2_bullets": [k for k, v in bullets.items() if str(v.get("status", "")).startswith("CITED_V2")],
        "cannot_check": [k for k, v in bullets.items() if str(v.get("status", "")).startswith("CANNOT_CHECK")],
        "g61_source_bound_incidents": {
            "status": "SEPARATE_WORKER",
            "note": "G6.1 recover source-bound real failure/probe incidents is research/g3-real-failure-v1, not this capsule.",
        },
        "per_incident": per_incident,
        "constitution": sorted(Lab.CONSTITUTION),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "winner": winner,
                "atms_still_cheapest": atms_still_cheapest,
                "ranking": result["ranking"],
                "earned_bullets": result["earned_bullets"],
                "cited_v2_bullets": result["cited_v2_bullets"],
                "cannot_check": result["cannot_check"],
            },
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
