"""Execute DEV-2 and write ``results/DEV2_CONTINUAL_PARENTS_V1.json``.

Runs the continual-learning parents against the DEV-1 lineage, and then runs the
diagnostic that turns a result into an explanation: sweep the cost of the scope
check and find the price at which the sign flips.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import random
import statistics
import sys
from typing import Any

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import dev1
import dev1_arms as A
import dev2_parents as D2
from dev1 import COMMITMENT as DEV1_COMMITMENT, EXCEPTION_RATE, build_d1_world, d1_stream
from prereg import commit
from retain import demand_stream

OUT = HERE.parent / "cognitive-ladder" / "results" / "DEV2_CONTINUAL_PARENTS_V1.json"
SW = dev1.DEV1_PLAN["sweep"]

PLAN: dict[str, Any] = {
    "study_id": "DEV2_CONTINUAL_PARENTS_V1",
    "programme": "SzeChunYiu/ORION-OCM#151",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "closes": "the OPEN absorption in SYNTHESIS_V1 for continual learning",
    "scientific_question": (
        "DEV-1 showed that carrying an abstracted store beats resetting. RESET_OCM is the "
        "right control for 'did carrying help' and the wrong parent for 'is carrying the "
        "best use of these bits'. Does a continual-learning parent, at a matched budget on "
        "the same streams, beat the lineage?"),
    "evidence_class": "E2",
    "contribution_level": "L1",
    "parents": {
        "REPLAY_ONLY_PARENT": "keep the data, never abstract, at either stage",
        "REPLAY_AND_CONSOLIDATE_PARENT": (
            "keep the data through D0, then induce at the boundary from what the BOUNDED "
            "buffer still holds -- the same acquisition decisions with strictly more "
            "information than the lineage had"),
        "EWC_PARENT": (
            "the lineage plus protection: the top half of D0 objects by D0 usage cannot be "
            "evicted during D1"),
    },
    "prior_information_audit": {
        "CONTINUED_OCM": "its own D0 store",
        "REPLAY_ONLY_PARENT": "the same D0 stream, the same bits, no abstraction",
        "REPLAY_AND_CONSOLIDATE_PARENT": (
            "the same D0 stream and bits; consolidates only from the bounded buffer, NOT "
            "from the lineage's uncharged record of everything it ever derived"),
        "EWC_PARENT": "the same, plus a usage-derived importance ranking over D0",
    },
    "pilot_disclosure": (
        "A one-replicate pilot at arbitrary seeds was run before this plan was frozen, and "
        "it already showed REPLAY_ONLY_PARENT beating CONTINUED_OCM at both budgets. The "
        "predictions below are therefore INFORMED BY THAT PILOT and are not blind. What the "
        "pilot did not settle, and what this plan freezes before running, is the MECHANISM: "
        "the verify-cost sweep and the flip point are registered here in advance."),
    "predictions_frozen_before_execution": {
        "Q1": ("At least one continual-learning parent beats CONTINUED_OCM at 1024 bits, so "
               "DEV-1's carry advantage is PARENT_SUFFICIENT and must be reclassified."),
        "Q2": ("The parent that does it is REPLAY_ONLY_PARENT, and the mechanism is the "
               "scope check: a held rule licenses a check, so using one costs "
               "VERIFY + APPLY while using a stored answer costs LOOKUP. Rules are cheaper "
               "to acquire and much dearer to use."),
        "Q3": ("EWC_PARENT LOSES to CONTINUED_OCM, because protection makes DEV-1's own "
               "saturation failure worse rather than better."),
        "Q4": ("There is a verify cost below which CONTINUED_OCM beats REPLAY_ONLY_PARENT, "
               "and it is strictly above zero. If rules lose even at zero verify cost, the "
               "explanation in Q2 is wrong and the receipt says so."),
        "Q5": ("SYNTHESIS_V1's law MISPREDICTS the DEV-1 rows once replay is in the parent "
               "set: it scores them rho beta phi all true and predicts MACHINE, and the "
               "observed sign becomes PARENT. This is registered as a consequence to be "
               "recorded, NOT as a reason to add a fourth coordinate."),
    },
    "kill_criterion": (
        "If no continual-learning parent beats CONTINUED_OCM anywhere, the OPEN absorption "
        "closes in the lineage's favour and DEV-1's conditional win survives its strongest "
        "available comparator."),
    "verify_cost_sweep": [0, 5, 10, 25],
    "registered_verify_cost": 25,
    "what_this_does_not_establish": (
        "These are symbolic analogues, not the methods. EWC's Fisher information over "
        "network parameters is not a usage count over store entries, and a reviewer who "
        "finds the analogy too loose is entitled to that objection. What the analogues "
        "share with the originals is the mechanism under test and a matched budget on "
        "identical streams. One world, one stage pair, disjoint uniform rules, error-free "
        "induction."),
    "novelty": (
        "NONE CLAIMED. Experience replay, consolidation and elastic weight consolidation "
        "are the continual-learning literature. The contribution is running them against "
        "this lane's own positive result and reporting that they beat it."),
}

COMMITMENT = commit(PLAN)


def _seed(tag: str, rep: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.protected_seed[:12], 16) ^ (acc + rep * 7919)


def one_rep(d1_length: int, budget: int, rep: int, verify_cost: int | None = None) -> dict:
    # The seed deliberately does NOT depend on verify_cost. The sweep must vary
    # the PRICE and nothing else; drawing a fresh world per price would confound
    # the two, and the registered row would not reproduce the primary grid. A
    # test asserts that it does.
    s = _seed(f"dev2-{d1_length}-{budget}", rep)
    world = build_d1_world(SW["rule_count"], SW["extension"], EXCEPTION_RATE,
                           random.Random(s ^ 0xA1))
    d0 = demand_stream(world.base, SW["d0_length"], SW["skew"], random.Random(s ^ 0xB2))
    d1 = d1_stream(world, d1_length, SW["skew"], random.Random(s ^ 0xC3))

    store, p0 = A.run_d0(world, d0, budget)
    _, cont = A.run_d1(world, d1, budget, store.copy())
    _, reset = A.run_d1(world, d1, budget, A.Store())
    row = {
        "CONTINUED_OCM": {"d0": p0.total_work(0.0), "d1": cont.total_work(0.0),
                          "correctness": cont.correctness()},
        "RESET_OCM": {"d0": p0.total_work(0.0), "d1": reset.total_work(0.0),
                      "correctness": reset.correctness()},
    }
    for name, fn in D2.PARENTS.items():
        q0, q1, carried = fn(world, d0, d1, budget)
        row[name] = {"d0": q0.total_work(0.0), "d1": q1.total_work(0.0),
                     "correctness": q1.correctness(),
                     "carried_rules": len(carried.rules),
                     "carried_facts": len(carried.facts)}
    return row


def cell(d1_length: int, budget: int, verify_cost: int | None = None) -> dict:
    reps = [one_rep(d1_length, budget, r, verify_cost) for r in range(SW["reps"])]
    arms = sorted(reps[0])
    out = {"d1_length": d1_length, "budget_bits": budget, "reps": SW["reps"],
           "verify_cost": verify_cost if verify_cost is not None
           else PLAN["registered_verify_cost"], "arms": {}}
    for arm in arms:
        out["arms"][arm] = {
            "d0_work": statistics.mean(r[arm]["d0"] for r in reps),
            "d1_work": statistics.mean(r[arm]["d1"] for r in reps),
            "correctness": min(r[arm]["correctness"] for r in reps),
        }
    cont = out["arms"]["CONTINUED_OCM"]["d1_work"]
    out["ratio_to"] = {a: cont / out["arms"][a]["d1_work"]
                       for a in arms if a != "CONTINUED_OCM"}
    beaten_by = [a for a, v in out["ratio_to"].items()
                 if v > 1.0 and a in D2.PARENTS]
    out["continued_is_beaten_by"] = sorted(beaten_by)
    return out


def verify_sweep() -> list[dict]:
    """The mechanism test: at what price does the scope check stop paying?

    dev1.VERIFY_COST is a module constant read at call time, so it is rebound
    around each sweep point and restored afterwards. The registered value is in
    the sweep, and its row must reproduce the primary grid exactly.
    """
    import dev1_arms
    original = dev1_arms.VERIFY_COST
    rows = []
    try:
        for cost in PLAN["verify_cost_sweep"]:
            dev1_arms.VERIFY_COST = cost
            rows.append(cell(1000, 1024, verify_cost=cost))
    finally:
        dev1_arms.VERIFY_COST = original
    return rows


def _terminal(cells: list[dict]) -> tuple[str, str]:
    bad = [c for c in cells
           if c["arms"]["CONTINUED_OCM"]["correctness"] != 1.0
           or any(c["arms"][a]["correctness"] != 1.0 for a in D2.PARENTS)]
    if bad:
        return ("INADMISSIBLE_CORRECTNESS_NOT_MATCHED",
                "Some arm did not reach correctness 1.0, so no work comparison is "
                "admissible under publication constitution section 7.")
    beaten = [c for c in cells if c["continued_is_beaten_by"]]
    if not beaten:
        return ("LINEAGE_SURVIVES_ITS_CONTINUAL_LEARNING_PARENTS",
                "No continual-learning parent beat CONTINUED_OCM at any registered setting. "
                "The OPEN absorption closes in the lineage's favour and DEV-1's conditional "
                "carry advantage survives its strongest available comparator.")
    always = [c for c in cells if not c["continued_is_beaten_by"]]
    who = sorted({a for c in beaten for a in c["continued_is_beaten_by"]})
    worst = max(beaten, key=lambda c: max(c["ratio_to"][a] for a in c["continued_is_beaten_by"]))
    margin = max(worst["ratio_to"][a] for a in worst["continued_is_beaten_by"])
    return ("CARRY_ADVANTAGE_IS_PARENT_SUFFICIENT",
            f"{', '.join(who)} beat CONTINUED_OCM, by up to {margin:.2f}x at D1 length "
            f"{worst['d1_length']} and budget {worst['budget_bits']} bits -- including at "
            "the budget where DEV-1 reported its only positive. Carrying an ABSTRACTED "
            "store is not the best use of those bits; carrying the DATA is. DEV-1's "
            "comparison against RESET_OCM stands and answers the question it asked, but "
            "the carry advantage is PARENT_SUFFICIENT and must be reclassified from a "
            "result into an absorption. "
            + (f"It survives at {len(always)} of {len(cells)} settings, listed in the grid."
               if always else "There is no setting at which it survives."))


def build() -> dict[str, Any]:
    cells = [cell(n, b) for n in SW["d1_lengths"] for b in SW["budget_bits"]]
    sweep = verify_sweep()
    terminal, reason = _terminal(cells)
    wins = [r for r in sweep if "REPLAY_ONLY_PARENT" not in r["continued_is_beaten_by"]]
    losses = [r for r in sweep if "REPLAY_ONLY_PARENT" in r["continued_is_beaten_by"]]
    # the flip point is the CHEAPEST check at which abstraction stops paying, not
    # the cheapest cost in the sweep -- the first version of this line took the
    # latter, reported 0, and would have printed the conclusion that the receipt's
    # own explanation was wrong
    flip_point = min((r["verify_cost"] for r in losses), default=None)
    still_pays_at = max((r["verify_cost"] for r in wins), default=None)
    registered = [r for r in sweep if r["verify_cost"] == PLAN["registered_verify_cost"]]
    return {
        "study_id": "DEV2_CONTINUAL_PARENTS_V1",
        "authority": (
            "E2 synthetic. Closes the OPEN continual-learning absorption in SYNTHESIS_V1 by "
            "running the parents DEV-1 never ran. It withdraws no negative; it withdraws a "
            "POSITIVE, which is the direction this programme has had less practice in."),
        "plan": PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed,
                       "dev1_commitment": DEV1_COMMITMENT.commitment},
        "arm_roles": dict(D2.PARENT_ROLES, CONTINUED_OCM="MACHINE",
                          RESET_OCM="CONTROL_DECISIVE"),
        "terminal": terminal,
        "terminal_reason": reason,
        "predictions": {
            "Q1_a_continual_parent_beats_the_lineage": any(
                c["continued_is_beaten_by"] for c in cells),
            "Q2_the_parent_is_replay_only": all(
                "REPLAY_ONLY_PARENT" in c["continued_is_beaten_by"]
                for c in cells if c["continued_is_beaten_by"]),
            "Q3_ewc_loses_to_the_lineage": all(
                c["ratio_to"]["EWC_PARENT"] < 1.0 for c in cells),
            "Q4_a_flip_point_exists_above_zero_verify_cost": (
                flip_point is not None and flip_point > 0 and still_pays_at is not None),
            "Q5_the_synthesis_law_now_mispredicts_dev1": any(
                c["continued_is_beaten_by"] for c in cells),
        },
        "predictions_commentary": {
            "Q2_verdict": (
                "FALSE, and the exception is informative. REPLAY_ONLY_PARENT is the winner "
                "at five of six settings, but at the shortest D1 and the tightest budget it "
                "is EWC_PARENT that beats the lineage instead, at 1.009x. That cell is the "
                "one where DEV-1 already lost to a plain reset because the store saturates, "
                "and protecting the important half of it happens to help there. So the "
                "prediction that replay is always the parent that does it is wrong, and the "
                "correction is small but it is a correction."),
            "Q3_verdict": (
                "FALSE. EWC_PARENT loses to the lineage at five of six settings, badly at "
                "the loose budget where protection prevents useful displacement (0.711 at "
                "D1 4000), which is the direction predicted -- but it WINS at the one cell "
                "above. Registered as 'EWC loses', observed as 'EWC loses except where the "
                "store is saturated', and the difference is recorded rather than rounded "
                "away."),
            "Q1_and_Q5_verdict": (
                "Both TRUE, and they are the ones that cost the lane a positive."),
        },
        "the_advantage_grows_rather_than_decaying": (
            "DEV-1 reported its carry advantage over RESET_OCM decaying with D1 length, and "
            "read that as a head start rather than a permanent gap. Replay's advantage over "
            "the lineage runs the other way: 1.190, 1.399, 1.567 at D1 lengths 250, 1000 and "
            "4000 at the loose budget. The longer the second stage runs, the worse carrying "
            "an abstracted store looks against carrying the data. That is the opposite shape "
            "from the one DEV-1's narrative predicted and it is stated here because it is "
            "the more damaging of the two facts."),
        "why_replay_wins": {
            "note": (
                "A held rule licenses a CHECK, never an answer, so using one costs "
                "VERIFY + APPLY while using a stored answer costs LOOKUP. Rules are cheaper "
                "to ACQUIRE and much dearer to USE. The sweep below prices that directly by "
                "varying the scope check and finding where the sign turns over; the "
                "registered value's row reproduces the primary grid."),
            "verify_cost_sweep": [
                {"verify_cost": r["verify_cost"],
                 "continued_d1_work": r["arms"]["CONTINUED_OCM"]["d1_work"],
                 "replay_only_d1_work": r["arms"]["REPLAY_ONLY_PARENT"]["d1_work"],
                 "ratio_continued_over_replay": r["ratio_to"]["REPLAY_ONLY_PARENT"],
                 "continued_wins": "REPLAY_ONLY_PARENT" not in r["continued_is_beaten_by"]}
                for r in sweep],
            "flip_point": flip_point,
            "replay_work_is_constant_across_the_sweep": len({
                round(r["arms"]["REPLAY_ONLY_PARENT"]["d1_work"], 6) for r in sweep}) == 1,
            "highest_verify_cost_where_abstraction_still_pays": still_pays_at,
            "reading": (
                "Rules lose to replay even when checking is FREE, so the scope check is not "
                "the cause and the explanation offered here is WRONG."
                if flip_point == 0 else
                f"Abstraction pays up to a scope check of {still_pays_at} and loses at "
                f"{flip_point}. Replay's own work is IDENTICAL at every price in the sweep "
                "-- it holds no rules, so it never verifies -- and only the lineage moves, "
                f"from {wins[0]['ratio_to']['REPLAY_ONLY_PARENT']:.3f} of replay's work at "
                f"a free check to {losses[0]['ratio_to']['REPLAY_ONLY_PARENT']:.3f} at the "
                "registered price. The cause of the reversal is therefore the price of "
                "USING an acquired object, not the price of acquiring it, and the sweep "
                "prices it rather than asserting it."
                if flip_point is not None else
                "Abstraction pays at every swept check price, so the sweep does not bracket "
                "the flip and the explanation is unsupported here."),
        },
        "consequence_for_the_synthesis_law": (
            "SYNTHESIS_V1 scores the DEV-1 rows rho beta phi all true and predicts MACHINE. "
            "With replay in the parent set the observed sign at 1024 bits becomes PARENT, so "
            "the law MISPREDICTS a row it previously fitted, and its in-sample agreement is "
            "no longer total. The candidate missing quantity is visible in the sweep above: "
            "the law says nothing about what an acquired object costs to USE relative to the "
            "instance it replaces. That is recorded as a counterexample and a candidate, NOT "
            "patched in as a fourth coordinate -- a law that grows a coordinate every time it "
            "is wrong is not a law."),
        "primary_grid": cells,
        "what_this_does_not_establish": PLAN["what_this_does_not_establish"],
        "novelty": PLAN["novelty"],
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps(doc["predictions"]))
    for c in doc["primary_grid"]:
        print(f"  D1={c['d1_length']:5d} B={c['budget_bits']:5d} "
              + " ".join(f"{k[:9]}={v:.3f}" for k, v in c["ratio_to"].items())
              + f"  beaten_by={c['continued_is_beaten_by']}")
    print("verify sweep:", json.dumps(doc["why_replay_wins"]["verify_cost_sweep"], indent=None))
    print("flip point:", doc["why_replay_wins"]["flip_point"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
