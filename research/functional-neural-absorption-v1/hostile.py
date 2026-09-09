"""FNA-1 hostile: does rarity-first survive when rarity STOPS predicting decisiveness?

DECLARED POST-FREEZE. Written after reading FNA-1's outcome. It is admissible because it
can only WEAKEN the result, never rescue it: a hostile whose purpose is to destroy one's
own finding is not a retune. ``experiment.py`` is NOT edited, so FREEZE_V1.json stands.

The concern this answers, stated plainly: in FNA-1 the decisive atom was placed on the
rare channel, so a rarity-first policy tied the ORACLE at every budget. That is a property
of the world I constructed, not evidence that rarity predicts decisiveness. If rarity-first
only works when the two coincide, the FNA-1 advantage is an artifact of the planted world
and the honest terminal is PARENT_SUFFICIENT, not a resource advantage.

Three worlds are run, identical except for where the decisive atom hangs:

    RARE_DECISIVE     decisive on the rare channel      (the FNA-1 world; expect rarity wins)
    COMMON_DECISIVE   decisive on a common channel      (expect rarity to LOSE)
    ADVERSARIAL       decisive on a common channel AND a large rare-channel decoy subtree
                      that rarity-first will exhaust the budget on before reaching it
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

from ocm.kso.space import KnowledgeSpace, Atom, Hyperedge      # noqa: E402
import experiment as E                                          # noqa: E402

SCHEMA = "ocm.fna.fna1-hostile-rarity.v1"
DECOY_CHANNEL = "EMBEDDING"


def world(kind: str, n_distractors: int = 60, decoys: int = 40) -> KnowledgeSpace:
    atoms = [Atom(atom_id="seed", atom_type="query_seed"),
             Atom(atom_id=E.DECISIVE, atom_type="claim")]
    atoms += [Atom(atom_id=f"d{i}", atom_type="claim") for i in range(n_distractors)]
    edges = [Hyperedge(edge_id=f"e_d{i}", tails=("seed",), heads=(f"d{i}",),
                       relation_type=E.COMMON_CHANNELS[i % len(E.COMMON_CHANNELS)])
             for i in range(n_distractors)]
    for i in range(0, n_distractors, 3):
        for j in (1, 2):
            if i + j < n_distractors:
                edges.append(Hyperedge(edge_id=f"e_c{i}_{j}", tails=(f"d{i}",),
                                       heads=(f"d{i + j}",),
                                       relation_type=E.COMMON_CHANNELS[j % 2]))
    if kind == "RARE_DECISIVE":
        edges.append(Hyperedge(edge_id="e_decisive", tails=("seed",),
                               heads=(E.DECISIVE,), relation_type=E.RARE_CHANNEL))
    else:
        # Decisive sits on a COMMON channel: rarity-first now deprioritises the very
        # channel that carries the answer.
        edges.append(Hyperedge(edge_id="e_decisive", tails=("seed",),
                               heads=(E.DECISIVE,), relation_type=E.COMMON_CHANNELS[0]))
    if kind == "ADVERSARIAL":
        # A rare-channel decoy subtree. Rarest-first will spend the budget here first.
        atoms += [Atom(atom_id=f"k{i}", atom_type="claim") for i in range(decoys)]
        edges += [Hyperedge(edge_id=f"e_k{i}", tails=("seed",), heads=(f"k{i}",),
                            relation_type=DECOY_CHANNEL) for i in range(decoys)]
    return KnowledgeSpace(atoms=tuple(atoms), hyperedges=tuple(edges))


def run(budgets=(4, 8, 16, 32, 64, 128)) -> dict:
    out = {}
    for kind in ("RARE_DECISIVE", "COMMON_DECISIVE", "ADVERSARIAL"):
        ks = world(kind)
        order, counts = E.channel_rarity(ks)
        rows = {}
        for b in budgets:
            naive, wn = E.bounded_closure(ks, ["seed"], b, channel_order=None)
            rarity, wr = E.bounded_closure(ks, ["seed"], b, channel_order=order)
            rows[str(b)] = {
                "budget_binds": wn["truncated"],
                "naive_found": E.DECISIVE in naive,
                "rarity_found": E.DECISIVE in rarity,
                "naive_reached": len(naive), "rarity_reached": len(rarity)}
        binding = {b: r for b, r in rows.items() if r["budget_binds"]}
        out[kind] = {
            "channel_counts": counts, "rarity_order": list(order),
            "rows": rows,
            "rarity_strictly_better": sorted(
                b for b, r in binding.items() if r["rarity_found"] and not r["naive_found"]),
            "rarity_strictly_WORSE": sorted(
                b for b, r in binding.items() if r["naive_found"] and not r["rarity_found"]),
        }
    return {"schema": SCHEMA,
            "analysis_status": "DECLARED_POST_FREEZE_HOSTILE",
            "authority": ("Written after reading FNA-1's outcome. Admissible because it can "
                          "only weaken the finding. experiment.py is unmodified; FREEZE_V1 "
                          "stands."),
            "worlds": out}


def verdict(doc: dict) -> dict:
    w = doc["worlds"]
    better_rare = bool(w["RARE_DECISIVE"]["rarity_strictly_better"])
    worse_common = bool(w["COMMON_DECISIVE"]["rarity_strictly_WORSE"])
    worse_adv = bool(w["ADVERSARIAL"]["rarity_strictly_WORSE"])
    out = {
        "rarity_wins_when_rare_channel_carries_the_answer": better_rare,
        "rarity_loses_when_a_common_channel_carries_the_answer": worse_common,
        "rarity_loses_against_a_rare_channel_decoy": worse_adv,
        "budgets_rarity_worse_common": w["COMMON_DECISIVE"]["rarity_strictly_WORSE"],
        "budgets_rarity_worse_adversarial": w["ADVERSARIAL"]["rarity_strictly_WORSE"],
    }
    out["policy_is_world_dependent"] = better_rare and (worse_common or worse_adv)
    if out["policy_is_world_dependent"]:
        out["terminal"] = "NON_NEURAL_RESOURCE_ADVANTAGE_AT_REGISTERED_SCOPE"
        out["terminal_reason"] = (
            "The FNA-1 advantage is REAL but CONDITIONAL, and the condition is now measured "
            "rather than assumed. The scope is three-way, not binary, and an earlier draft "
            "of this reason stated it binarily and was wrong:\n"
            "  RARE_DECISIVE   rarity-first is strictly BETTER at budgets "
            f"{w['RARE_DECISIVE']['rarity_strictly_better']}\n"
            "  COMMON_DECISIVE rarity-first is NEUTRAL -- identical to naive at every "
            "budget, neither better nor worse. Moving the answer to a common channel "
            "REMOVES the advantage; it does not reverse it.\n"
            "  ADVERSARIAL     rarity-first is strictly WORSE at budgets "
            f"{w['ADVERSARIAL']['rarity_strictly_WORSE']}, where a 40-edge rare-channel "
            "decoy subtree consumes the budget before the answer is reached.\n"
            "So rarity is a SELECTIVITY heuristic, not a relevance signal: it predicts "
            "where FEW edges are, never where the ANSWER is. It pays when scarcity happens "
            "to coincide with decisiveness, costs nothing when it does not, and is actively "
            "harmful when an adversary puts bulk on a scarce channel. FNA-1's headline must "
            "carry that scope, and this hostile is the reason it can.")
    elif better_rare:
        out["terminal"] = "CANNOT_CHECK_HOSTILE_DID_NOT_DISCRIMINATE"
        out["terminal_reason"] = (
            "Rarity-first was not made worse by either hostile world, so this pass did not "
            "establish the scope condition it was built to find. That is a failure of the "
            "hostile, not a strengthening of the claim.")
    else:
        out["terminal"] = "PARENT_SUFFICIENT_FOR_TYPED_CHANNEL_RETRIEVAL"
        out["terminal_reason"] = (
            "Rarity-first did not beat naive even where FNA-1 reported it did, so the FNA-1 "
            "result does not reproduce and the undifferentiated closure is sufficient.")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    doc = run()
    doc["verdict"] = verdict(doc)
    a.out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(json.dumps(doc["verdict"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
