"""G6 three-generation intervention-effect study with raw probe transcripts."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from world import (
    CONSTITUTION,
    N_MODULES,
    World,
    diagnose_and_repair,
    independent_truth,
    learn_selector,
    make_incidents,
    predict_with_structure,
    triad,
)


SALT = "orion-ocm-g6-intervention-lab-v1"
GEN_N = 8


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
    }


def run_generation(incidents, policy, rng):
    rows = []
    transcripts = []
    for incident in incidents:
        rows.append(diagnose_and_repair(incident, policy, rng))
        transcripts.append(incident.transcript)
    return rows, transcripts


def apply_learned(incidents, structure):
    """Learned probe prior plus fail-closed completeness.

    Root cause of v1-style collapse: a 3-bit syndrome is not identifying, so
    replacing only historically associated modules leaves residual faults.
    Conversion: treat the structure as a probe order, then continue probing
    until shadow quality is 1 or the module set is exhausted.
    """
    rows = []
    transcripts = []
    for incident in incidents:
        predicted = predict_with_structure(structure, incident.hidden.syndrome())
        world = World(incident.hidden)
        cost = 0
        order = list(dict.fromkeys(predicted + list(range(N_MODULES))))
        failed = []
        for index in order:
            obs = world.probe(index)
            incident.probes.append(obs)
            cost += obs["cost"]
            if not obs["ok"]:
                rec = world.intervene(index)
                incident.interventions.append({**rec, "phase": "shadow"})
                cost += rec["cost"]
                failed.append(index)
            if all(world.modules):
                break
        restarted = world.restart_clone()
        quality = int(all(restarted.modules))
        incident.adopted = tuple(failed)
        truth = independent_truth(incident.hidden)
        identified = frozenset(failed) == truth
        rows.append({
            "policy": "learned_selector",
            "quality": quality,
            "identified": identified,
            "cost": cost,
            "kappa": len(truth),
            "omega": (1.0 if identified else 0.0) / max(1, len(incident.probes)),
            "chi": max(1, len(order)),
            "prediction": {"replace": failed, "prior": predicted},
        })
        transcripts.append(incident.transcript)
    return rows, transcripts


def main(out: Path) -> dict:
    rng = random.Random(1656)
    seen: set = set()
    g0 = make_incidents(0, GEN_N, SALT, disjoint_from=seen)
    g1 = make_incidents(1, GEN_N, SALT, disjoint_from=seen)
    g2 = make_incidents(2, GEN_N, SALT, disjoint_from=seen)
    assert len({i.hidden.stuck for i in g0 + g1 + g2}) == 3 * GEN_N

    grid0, t0 = run_generation(g0, "grid", rng)
    structure = learn_selector(t0)
    learned1, t1 = apply_learned(g1, structure)
    structure2 = learn_selector(t0 + t1)
    learned2, t2 = apply_learned(g2, structure2)
    evo2, _ = run_generation(make_incidents(2, GEN_N, SALT + "-evo", disjoint_from=set(seen)), "evolutionary", rng)

    s0, s1, s2 = summarize(grid0), summarize(learned1), summarize(learned2)
    t01 = triad(
        {"kappa": s0["kappa"], "omega": s0["omega"], "chi": s0["chi"]},
        {"kappa": s1["kappa"], "omega": s1["omega"], "chi": s1["chi"]},
    )
    t12 = triad(
        {"kappa": s1["kappa"], "omega": s1["omega"], "chi": s1["chi"]},
        {"kappa": s2["kappa"], "omega": s2["omega"], "chi": s2["chi"]},
    )
    three_earned = s0["quality"] == 1 and s1["quality"] == 1 and s2["quality"] == 1
    cost_improved = s2["cost"] < s0["cost"] and s1["cost"] < s0["cost"]
    parent_better = summarize(evo2)["quality"] > s2["quality"] and summarize(evo2)["cost"] < s2["cost"]
    if three_earned and cost_improved:
        terminal = "SELF_EVOLUTION_SUPPORTED_BOUNDED"
    elif parent_better:
        terminal = "AUTOML_PARENT_SUFFICIENT"
    elif three_earned:
        terminal = "MULTI_GENERATION_SELF_CHANGE_SUPPORTED"
    else:
        terminal = "NO_MULTI_GENERATION_IMPROVEMENT"

    result = {
        "schema": "ocm.g6.intervention-lab.v1",
        "terminal": terminal,
        "salt": SALT,
        "constitution": sorted(CONSTITUTION),
        "historical_m11_relabeled": False,
        "raw_traces": True,
        "generations": [s0, s1, s2],
        "triad_0_to_1": t01,
        "triad_1_to_2": t12,
        "structure_keys": list(structure2["syndrome_to_modules"]),
        "evo_gen2": summarize(evo2),
        "transcripts": {
            "g0": [_digest_row(t) for t in t0],
            "g1": [_digest_row(t) for t in t1],
            "g2": [_digest_row(t) for t in t2],
        },
        "claim_ceiling": "Bounded synthetic plant with independent scorer; not a production M11 lineage.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"terminal": terminal, "g0": s0, "g1": s1, "g2": s2}, indent=2, default=str))
    return result


def _digest_row(t: dict) -> dict:
    return {
        "incident_id": t["incident_id"],
        "probe_count": len(t["probes"]),
        "intervention_count": len(t["interventions"]),
        "syndrome": t["syndrome"],
        "adopted": t["adopted"],
    }


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
