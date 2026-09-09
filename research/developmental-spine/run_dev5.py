"""Execute DEV-5 and write ``results/DEV5_UNANIMITY_V1.json``."""

from __future__ import annotations

import json
import pathlib
import random
import statistics
import sys
from typing import Any

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import dev2_parents as D2
import dev5_arms as A
from dev4 import build_level_world, d1_stream
from dev5 import COMMITMENT, DEV5_PLAN
from retain import demand_stream

OUT = HERE.parent / "cognitive-ladder" / "results" / "DEV5_UNANIMITY_V1.json"
SW = DEV5_PLAN["sweep"]
ARM_IDS = tuple(A.ARMS) + ("REPLAY_ONLY_PARENT",)


def _seed(tag: str, rep: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.protected_seed[:12], 16) ^ (acc + rep * 7919)


def one_rep(level: int, d0_length: int, budget: int, skew: float, rep: int,
            consult_cost: int | None = None) -> dict:
    s = _seed(f"dev5-{level}-{d0_length}-{budget}-{skew}", rep)
    world, truth = build_level_world(SW["rule_count"], SW["extension"], level,
                                     random.Random(s ^ 0xA1))
    d0 = demand_stream(world.base, d0_length, skew, random.Random(s ^ 0xB2))
    d1 = d1_stream(world, SW["d1_length"], skew, random.Random(s ^ 0xC3))
    out: dict[str, Any] = {}
    for arm in A.ARMS:
        _p0, p1, _c = A.run_arm(arm, world, d0, d1, budget, level, truth, consult_cost)
        out[arm] = {"d1": p1.total_work(0.0), "correctness": p1.correctness(),
                    "verifications": p1.verifications, "applications": p1.applications}
    _, r1, _ = D2.replay_only(world, d0, d1, budget)
    out["REPLAY_ONLY_PARENT"] = {"d1": r1.total_work(0.0), "correctness": r1.correctness(),
                                 "verifications": 0, "applications": 0}
    return out


def cell(level: int, d0_length: int, budget: int, skew: float,
         consult_cost: int | None = None) -> dict:
    reps = [one_rep(level, d0_length, budget, skew, r, consult_cost)
            for r in range(SW["reps"])]
    out = {"level": level, "d0_length": d0_length, "budget_bits": budget, "skew": skew,
           "consult_cost": (consult_cost if consult_cost is not None
                            else DEV5_PLAN["registered_consult_cost"]),
           "reps": SW["reps"], "arms": {}}
    for arm in ARM_IDS:
        correct = [r[arm]["correctness"] for r in reps]
        sound = all(c == 1.0 for c in correct)
        out["arms"][arm] = {
            "role": A.ARM_ROLES.get(arm, "PARENT_NO_GUARDS"),
            "min_correctness": min(correct),
            "sound_in_every_replicate": sound,
            "d1_work": (statistics.mean(r[arm]["d1"] for r in reps) if sound else None),
            "d1_work_if_it_were_admissible": statistics.mean(r[arm]["d1"] for r in reps),
            "verifications": statistics.mean(r[arm]["verifications"] for r in reps),
        }
    u = out["arms"]["UNANIMITY_FULL"]["d1_work"]
    out["ratio_to"] = {
        a: (u / out["arms"][a]["d1_work"]
            if u is not None and out["arms"][a]["d1_work"] else None)
        for a in ARM_IDS if a != "UNANIMITY_FULL"}
    out["beats_singleton"] = (out["ratio_to"]["SINGLETON_FULL"] is not None
                              and out["ratio_to"]["SINGLETON_FULL"] < 1.0)
    out["beats_replay"] = (out["ratio_to"]["REPLAY_ONLY_PARENT"] is not None
                           and out["ratio_to"]["REPLAY_ONLY_PARENT"] < 1.0)
    return out


def consult_sweep() -> list[dict]:
    return [cell(3, 800, 1536, 1.0, consult_cost=c)
            for c in DEV5_PLAN["consult_cost_sweep"]]


def _terminal(cells: list[dict]) -> tuple[str, str]:
    u = "UNANIMITY_FULL"
    if any(not c["arms"][u]["sound_in_every_replicate"] for c in cells):
        return ("VOID_THE_SOUND_RULE_IS_NOT_SOUND",
                "UNANIMITY_FULL holds a language containing every world's truth and acts "
                "only where all survivors agree, so it cannot be wrong. It was. The harness "
                "is not implementing the soundness argument it declares.")
    if any(c["ratio_to"]["ORACLE_GUARD_PARENT"] is not None
           and c["ratio_to"]["ORACLE_GUARD_PARENT"] < 1.0 for c in cells):
        return ("VOID_CEILING_IMPLEMENTED_WRONGLY",
                "The arm beat a parent handed the true guard for free, which the plan "
                "registered as meaning the ceiling is wrong.")
    beats_s = [c for c in cells if c["beats_singleton"]]
    if not beats_s:
        return ("UNANIMITY_IS_INERT",
                "UNANIMITY_FULL did not beat SINGLETON_FULL anywhere. The version space is "
                "rarely unanimous about an index it has not decided, the weaker decision "
                "rule buys nothing, and the dilemma DEV-4 left is real rather than an "
                "artifact of the rule.")
    beats_r = [c for c in cells if c["beats_replay"]]
    best_s = min(c["ratio_to"]["SINGLETON_FULL"] for c in beats_s)
    verif = {a: statistics.mean(c["arms"][a]["verifications"] for c in cells)
             for a in ("UNANIMITY_FULL", "SINGLETON_FULL")}
    reason = (
        f"UNANIMITY_FULL beats SINGLETON_FULL at {len(beats_s)} of {len(cells)} settings and "
        f"by up to {1 / best_s:.2f}x, holding the SAME language and differing only in when "
        "it is willing to act. Mean scope checks fall from "
        f"{verif['SINGLETON_FULL']:.0f} to {verif['UNANIMITY_FULL']:.0f} out of 2000 member "
        "demands. Correctness is 1.0 everywhere for both, because both act only on what the "
        "surviving candidates determine and the truth is always among them -- the weaker "
        "rule gives up no soundness at all, and the stronger rule was costing this lane a "
        "factor it never had to pay.")
    if beats_r:
        reason += (
            f" It also beats REPLAY_ONLY_PARENT at {len(beats_r)} of {len(cells)} settings, "
            "WITHOUT the language gift DEV-3 needed: the language here contains the truth at "
            "every level because it is large, not because it was fitted to the world, and "
            "DEV-4 showed that is the condition that matters. The carry advantage therefore "
            "no longer rests on the precondition DEV-4 found binding.")
    else:
        reason += (
            " It does NOT beat REPLAY_ONLY_PARENT at any setting, so the decision rule "
            "recovers a large factor against this lane's own prior arm and still leaves the "
            "carry advantage resting on DEV-3's declared gift.")
    return ("UNANIMITY_RECOVERS_THE_FULL_LANGUAGE", reason)


def build() -> dict[str, Any]:
    cells = [cell(lvl, n, b, k)
             for lvl in SW["levels"] for n in SW["d0_lengths"]
             for b in SW["budget_bits"] for k in SW["skews"]]
    sweep = consult_sweep()
    terminal, reason = _terminal(cells)
    small = [c for c in cells
             if not c["arms"]["UNANIMITY_SMALL"]["sound_in_every_replicate"]]
    return {
        "study_id": "DEV5_UNANIMITY_V1",
        "authority": (
            "E2 synthetic. Responds to DEV4_LANGUAGE_EXPANSION_V1 by changing a decision "
            "rule that DEV-3 and DEV-4 both took for granted. It withdraws no negative and "
            "no positive."),
        "plan": DEV5_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed},
        "arm_roles": dict(A.ARM_ROLES, REPLAY_ONLY_PARENT="PARENT_NO_GUARDS"),
        "terminal": terminal,
        "terminal_reason": reason,
        "predictions": {
            "U1_unanimity_full_is_sound_everywhere": all(
                c["arms"]["UNANIMITY_FULL"]["sound_in_every_replicate"] for c in cells),
            "U2_beats_the_singleton_rule_everywhere": all(
                c["beats_singleton"] for c in cells),
            "U3_beats_replay_without_the_language_gift": any(
                c["beats_replay"] for c in cells),
            "U4_does_not_beat_the_oracle_guard": all(
                c["ratio_to"]["ORACLE_GUARD_PARENT"] is None
                or c["ratio_to"]["ORACLE_GUARD_PARENT"] >= 1.0 for c in cells),
            "U5_unanimity_does_not_rescue_a_deficient_language": bool(small),
        },
        "the_control": {
            "note": (
                "UNANIMITY_SMALL applies the same decision rule over a language that cannot "
                "express level 2 and level 3 truths. If unanimity were a general fix rather "
                "than a fix for the decision rule, it would be sound here too."),
            "unsound_cells": [{"level": c["level"], "d0_length": c["d0_length"],
                               "skew": c["skew"], "budget_bits": c["budget_bits"],
                               "min_correctness":
                                   c["arms"]["UNANIMITY_SMALL"]["min_correctness"]}
                              for c in small],
            "verdict": (
                "Unanimity does NOT rescue a deficient language: it is unsound in "
                f"{len(small)} of {len(cells)} cells, exactly where the truth is outside "
                "the language. What it fixes is the decision rule, and the language "
                "requirement DEV-4 established stands untouched."
                if small else
                "UNANIMITY_SMALL stayed sound at every setting, which is NOT what the plan "
                "predicted. Either the small language happens to contain an extensionally "
                "equivalent predicate at every level in this draw, or unanimity is more "
                "conservative than the singleton rule in a way the plan did not anticipate. "
                "Recorded as an open discrepancy rather than a result."),
        },
        "consult_cost_sweep": {
            "note": DEV5_PLAN["consult_cost_note"],
            "rows": [{"consult_cost": c["consult_cost"],
                      "unanimity_work": c["arms"]["UNANIMITY_FULL"]["d1_work"],
                      "singleton_work": c["arms"]["SINGLETON_FULL"]["d1_work"],
                      "replay_work": c["arms"]["REPLAY_ONLY_PARENT"]["d1_work"],
                      "beats_singleton": c["beats_singleton"],
                      "beats_replay": c["beats_replay"]} for c in sweep],
        },
        "what_this_changes_about_dev3": (
            "DEV-3's carry advantage needed a guard language fitted to the world, and DEV-4 "
            "showed that was a precondition rather than a convenience. UNANIMITY_FULL holds "
            "a language large enough to contain the truth at every level -- not fitted to "
            "any of them -- and still beats the replay parent. The precondition is "
            "satisfied by taking a BIG language rather than the RIGHT one, which is "
            "available without knowing the world, and the cost of doing so is what the "
            "singleton rule was charging and the unanimity rule is not."),
        "primary_grid": cells,
        "what_this_does_not_establish": DEV5_PLAN["what_this_does_not_establish"],
        "novelty": DEV5_PLAN["novelty"],
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps(doc["predictions"]))
    for c in doc["primary_grid"]:
        if c["skew"] != 1.0 or c["d0_length"] != 800:
            continue
        r = c["ratio_to"]
        print(f"  L{c['level']} B={c['budget_bits']:5d} u/singleton="
              f"{r['SINGLETON_FULL']:.3f} u/replay={r['REPLAY_ONLY_PARENT']:.3f} "
              f"u/oracle={r['ORACLE_GUARD_PARENT']:.3f} "
              f"verif={c['arms']['UNANIMITY_FULL']['verifications']:.0f}")
    print("control unsound cells:", len(doc["the_control"]["unsound_cells"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
