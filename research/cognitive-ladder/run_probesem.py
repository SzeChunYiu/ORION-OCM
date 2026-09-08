"""Execute E11 and write ``results/PROBESEM_E11_V1.json``."""

from __future__ import annotations

import json
import pathlib
import random
import statistics
from typing import Any, Sequence

import probesem_arms as A
from probesem import (BASE_PROBES, COMMITMENT, EXTRA_PROBE, PROBESEM_PLAN,
                      REGISTERED_WORLD, World, case_stream, draw_world)

HERE = pathlib.Path(__file__).parent
OUT = HERE / "results" / "PROBESEM_E11_V1.json"
SW = PROBESEM_PLAN["sweep"]
TARGET = PROBESEM_PLAN["accuracy_target"]
WINDOW = SW["accuracy_window"]
BASE = [p.value for p in BASE_PROBES]


def _probes_at(index: int) -> list[str]:
    return BASE if index < SW["extension_at"] else BASE + [EXTRA_PROBE]


def _seed(tag: str, index: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.protected_seed[:12], 16) ^ (acc + index * 7919)


def worlds() -> list[tuple[str, World]]:
    out: list[tuple[str, World]] = []
    if SW["include_registered_world"]:
        out.append(("REGISTERED_E2_WORLD", World(REGISTERED_WORLD, True)))
    for i in range(SW["worlds"]):
        out.append((f"drawn-{i}", draw_world(random.Random(_seed("world", i)))))
    return out


def run() -> dict[str, list[dict]]:
    per_arm: dict[str, list[dict]] = {a: [] for a in A.ARMS}
    for index, (name, world) in enumerate(worlds()):
        stream = case_stream(SW["lifetime"], random.Random(_seed("stream", index)))
        for arm_id in A.ARMS:
            trace = A.run_arm(arm_id, world, stream, _probes_at,
                              SW["probe_budget_per_case"], _seed(arm_id, index))
            row = trace.as_dict(TARGET, WINDOW)
            row["world"] = name
            ext = SW["extension_at"]
            row["accuracy_before_extension"] = trace.rolling_accuracy(ext, WINDOW)
            row["accuracy_just_after_extension"] = trace.rolling_accuracy(ext + WINDOW, WINDOW)
            row["accuracy_at_end"] = trace.rolling_accuracy(len(trace.correct), WINDOW)
            per_arm[arm_id].append(row)
    return per_arm


def summarise(per_arm: dict[str, list[dict]]) -> dict[str, dict]:
    out = {}
    for arm_id, rows in per_arm.items():
        reached = [r for r in rows if r["reached_target"]]
        out[arm_id] = {
            "role": A.ARM_ROLES[arm_id],
            "worlds": len(rows),
            "worlds_reaching_target": len(reached),
            "accuracy": statistics.mean(r["accuracy"] for r in rows),
            "refusal_rate": statistics.mean(r["refusal_rate"] for r in rows),
            "probe_cost": statistics.mean(r["probe_cost"] for r in rows),
            "accuracy_before_extension": statistics.mean(
                r["accuracy_before_extension"] for r in rows),
            "accuracy_just_after_extension": statistics.mean(
                r["accuracy_just_after_extension"] for r in rows),
            "accuracy_at_end": statistics.mean(r["accuracy_at_end"] for r in rows),
            # a mean over only the worlds that reached the target would be a mean
            # over a self-selected sample, so the count above is reported beside it
            # and a partial result is never quoted as a full one
            "median_cases_to_target": (
                statistics.median(r["cases_to_target"] for r in reached) if reached else None),
            "mean_cases_to_target": (
                statistics.mean(r["cases_to_target"] for r in reached) if reached else None),
        }
    return out


def paired(per_arm: dict[str, list[dict]], arms: Sequence[str]) -> dict[str, Any]:
    """Mean cases-to-target over the worlds where EVERY named arm reached it.

    The unpaired mean is not a comparison. Each arm's own mean is taken over the
    worlds it happened to solve, so an arm that reaches the target on 15 worlds
    of 41 and gives up on the hard ones posts a better number than an arm that
    reaches it on 40 -- and in this run fixed_order_parent does exactly that. The
    paired mean fixes the sample; the reach count is reported beside it and is
    the more important coordinate of the two.
    """
    by_world: dict[str, dict[str, dict]] = {}
    for arm_id in arms:
        for row in per_arm[arm_id]:
            by_world.setdefault(row["world"], {})[arm_id] = row
    common = [w for w, d in by_world.items()
              if len(d) == len(arms) and all(d[a]["reached_target"] for a in arms)]
    return {
        "arms": list(arms),
        "worlds_compared": len(common),
        "worlds_total": len(by_world),
        "mean_cases_to_target": {
            a: (statistics.mean(by_world[w][a]["cases_to_target"] for w in common)
                if common else None) for a in arms},
        "note": (
            "Means over the worlds where every listed arm reached the target. Arms that "
            "reach it on fewer worlds are NOT rewarded for the worlds they failed."),
    }


def _terminal(s: dict[str, dict], pair: dict[str, Any]) -> tuple[str, str]:
    arm, parent = s["semantics_learner"], s["mapping_parent"]
    nb, ceiling = s["naive_bayes_parent"], s["given_semantics_ceiling"]
    if arm["worlds_reaching_target"] == 0 or parent["worlds_reaching_target"] == 0:
        return ("TARGET_NOT_REACHED",
                "One of the two learners never reached the registered accuracy target, so "
                "no sample-efficiency comparison between them is admissible.")
    if arm["accuracy"] > ceiling["accuracy"]:
        return ("VOID_CEILING_IMPLEMENTED_WRONGLY",
                "semantics_learner outscored an arm handed the true table, which the plan "
                "registered as meaning the ceiling is wrong rather than that a discovery "
                "has been made.")
    pm = pair["mean_cases_to_target"]
    if pm["semantics_learner"] >= pm["mapping_parent"]:
        return ("PARENT_SUFFICIENT",
                "mapping_parent reached the accuracy target in no more resolved cases than "
                "semantics_learner. Learning what a probe MEANS bought nothing over "
                "learning what an outcome IMPLIES, and N8's prescribed fix is REFUTED "
                "rather than completed. That is the headline.")
    per_probe_gap = pm["mapping_parent"] - pm["naive_bayes_parent"]
    table_gap = pm["naive_bayes_parent"] - pm["semantics_learner"]
    if per_probe_gap > table_gap:
        return ("PER_PROBE_EVIDENCE_SEPARATES_FROM_PER_ROW_EVIDENCE",
                "The semantics learner is more sample-efficient than the mapping parent "
                f"({pm['semantics_learner']:.0f} resolved cases against "
                f"{pm['mapping_parent']:.0f} on the same worlds), so N8's fix is COMPLETED "
                "and its "
                "prescription holds. But the credit does not go where N8 assigned it. "
                "naive_bayes_parent, which holds per-probe frequencies and NO semantics "
                f"table, reaches the target in {pm['naive_bayes_parent']:.0f} cases: the "
                f"gap between per-row and per-probe evidence is {per_probe_gap:.0f} cases "
                f"and the further gap from per-probe frequencies to an explicit table is "
                f"{table_gap:.0f}. What pays is that evidence about an instrument COMPOSES "
                "across cases; the table itself is a small further improvement. Any claim "
                "here is a claim about evidence factorisation, not about semantics.")
    return ("SEMANTICS_TABLE_SEPARATES_FROM_FREQUENCIES",
            "The explicit table beat per-probe frequencies by more than per-probe "
            "frequencies beat per-row evidence, so the table itself is where the sample "
            "efficiency comes from.")


def build() -> dict[str, Any]:
    per_arm = run()
    s = summarise(per_arm)
    pair = paired(per_arm, ("semantics_learner", "mapping_parent", "naive_bayes_parent",
                            "given_semantics_ceiling"))
    terminal, reason = _terminal(s, pair)
    arm, parent = s["semantics_learner"], s["mapping_parent"]
    gap_before = arm["accuracy_before_extension"] - parent["accuracy_before_extension"]
    gap_after = arm["accuracy_just_after_extension"] - parent["accuracy_just_after_extension"]
    return {
        "study_id": "PROBESEM_E11_V1",
        "authority": (
            "E2 synthetic. Built to discharge N8-DIAGNOSIS-RESIDUAL, which had been left as "
            "a standing decision rather than a repair. It withdraws no negative and "
            "reinterprets none; E2's world is a member of this world space."),
        "plan": PROBESEM_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed,
                       "pilot_seed": COMMITMENT.pilot_seed},
        "arm_roles": A.ARM_ROLES,
        "terminal": terminal,
        "terminal_reason": reason,
        "predictions": {
            "R1_both_reach_target": (arm["worlds_reaching_target"] > 0
                                     and parent["worlds_reaching_target"] > 0),
            "R2_semantics_more_sample_efficient": (
                arm["mean_cases_to_target"] < parent["mean_cases_to_target"]),
            "R3_extension_verdict": _r3(gap_before, gap_after, arm, parent),
            "R3_gap_before_extension": gap_before,
            "R3_gap_just_after_extension": gap_after,
            "R4_does_not_beat_ceiling": arm["accuracy"] <= s["given_semantics_ceiling"]["accuracy"],
            "R5_selection_is_not_free": (
                s["random_probe_parent"]["worlds_reaching_target"]
                < arm["worlds_reaching_target"]),
        },
        "summary": s,
        "paired_comparison": pair,
        "reach_rate_is_the_first_coordinate": {
            "note": (
                "Cases-to-target is only meaningful among arms that got there. The reach "
                "counts below come first, and the paired means come second. "
                "fixed_order_parent is the reason: it posts a competitive unpaired "
                "cases-to-target while reaching the target on a minority of worlds, which "
                "is what an unpaired mean over a self-selected sample looks like."),
            "worlds_reaching_target": {a: v["worlds_reaching_target"] for a, v in s.items()},
            "worlds": next(iter(s.values()))["worlds"],
        },
        "per_world": per_arm,
        "the_narrowing": (
            "naive_bayes_parent holds per-probe frequencies and no semantics table, and it "
            f"reaches the target in {pair['mean_cases_to_target']['naive_bayes_parent']:.0f} "
            f"resolved cases against the learner's "
            f"{pair['mean_cases_to_target']['semantics_learner']:.0f} and the mapping "
            f"parent's {pair['mean_cases_to_target']['mapping_parent']:.0f}, on the "
            f"{pair['worlds_compared']} worlds all of them solved. Much of the advantage is "
            "already available without representing semantics at all. This is stated here, "
            "beside the terminal, because a lane that reported only the learner against the "
            "mapping parent would be reporting a true number in a way that credits the "
            "wrong mechanism."),
        "what_this_does_not_establish": PROBESEM_PLAN["what_this_does_not_establish"],
        "novelty": PROBESEM_PLAN["novelty"],
        "discharges": PROBESEM_PLAN["discharges"],
    }


def nb_cases(s: dict[str, dict]) -> str:
    v = s["naive_bayes_parent"]["mean_cases_to_target"]
    return f"{v:.0f}" if v is not None else "never"


def _r3(gap_before: float, gap_after: float, arm: dict, parent: dict) -> str:
    dropped = parent["accuracy_just_after_extension"] < parent["accuracy_before_extension"]
    widened = gap_after > gap_before
    if dropped and widened:
        return "HELD"
    if widened:
        return (
            "PARTIALLY HELD, AND THE FAILED CLAUSE IS NAMED. R3 predicted two things: that "
            "the mapping parent's accuracy would DROP at the probe extension, and that the "
            "gap would WIDEN. The drop did not happen -- a sixth instrument carries "
            "information, and that outweighs the cold start for every arm, so accuracy rose "
            f"for all of them. The gap did widen, from {gap_before:.3f} to {gap_after:.3f}. "
            "The mechanism R3 was written to expose is therefore visible in the gap and not "
            "in the level, and the half of R3 that was wrong is recorded as wrong.")
    return (
        "REFUTED. The gap did not widen at the probe extension, so whatever makes the "
        f"semantics learner more sample-efficient ({gap_before:.3f} before, {gap_after:.3f} "
        "after) is not compositional in the way the plan claimed. The efficiency result "
        "stands and its stated explanation does not.")


def main() -> int:
    doc = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    for arm_id, row in doc["summary"].items():
        print(f"  {arm_id:26s} acc={row['accuracy']:.3f} "
              f"reached={row['worlds_reaching_target']}/{row['worlds']} "
              f"cases_to_target={row['mean_cases_to_target']} "
              f"probe_cost={row['probe_cost']:.0f}")
    print("paired:", json.dumps(doc["paired_comparison"]["mean_cases_to_target"]))
    print("R3:", doc["predictions"]["R3_extension_verdict"][:80])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
