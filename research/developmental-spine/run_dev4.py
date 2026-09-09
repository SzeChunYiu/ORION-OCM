"""Execute DEV-4 and write ``results/DEV4_LANGUAGE_EXPANSION_V1.json``."""

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
import dev4_arms as A
from dev4 import COMMITMENT, DEV4_PLAN, build_level_world, d1_stream, language
from retain import demand_stream

OUT = HERE.parent / "cognitive-ladder" / "results" / "DEV4_LANGUAGE_EXPANSION_V1.json"
SW = DEV4_PLAN["sweep"]
ARM_IDS = tuple(A.ARMS) + ("REPLAY_ONLY_PARENT",)


def _seed(tag: str, rep: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.protected_seed[:12], 16) ^ (acc + rep * 7919)


def one_rep(level: int, d0_length: int, budget: int, skew: float, rep: int) -> dict:
    s = _seed(f"dev4-{level}-{d0_length}-{budget}-{skew}", rep)
    world, _truth = build_level_world(SW["rule_count"], SW["extension"], level,
                                      random.Random(s ^ 0xA1))
    d0 = demand_stream(world.base, d0_length, skew, random.Random(s ^ 0xB2))
    d1 = d1_stream(world, SW["d1_length"], skew, random.Random(s ^ 0xC3))
    out = {"exception_count": len(world.exceptions)}
    for arm in A.ARMS:
        _p0, p1, carried = A.run_arm(arm, world, d0, d1, budget, level)
        out[arm] = {"d1": p1.total_work(0.0), "correctness": p1.correctness(),
                    "verifications": p1.verifications, "applications": p1.applications,
                    "guards": len(carried.guards), "expansions": carried.expansions}
    _, r1, _ = D2.replay_only(world, d0, d1, budget)
    out["REPLAY_ONLY_PARENT"] = {"d1": r1.total_work(0.0), "correctness": r1.correctness(),
                                 "verifications": 0, "applications": 0, "guards": 0,
                                 "expansions": 0}
    return out


def cell(level: int, d0_length: int, budget: int, skew: float) -> dict:
    reps = [one_rep(level, d0_length, budget, skew, r) for r in range(SW["reps"])]
    out = {"level": level, "d0_length": d0_length, "budget_bits": budget, "skew": skew,
           "reps": SW["reps"],
           "mean_exception_count": statistics.mean(r["exception_count"] for r in reps),
           "arms": {}}
    for arm in ARM_IDS:
        correct = [r[arm]["correctness"] for r in reps]
        sound = all(c == 1.0 for c in correct)
        out["arms"][arm] = {
            "role": A.ARM_ROLES.get(arm, "PARENT_NO_GUARDS"),
            "min_correctness": min(correct),
            "mean_correctness": statistics.mean(correct),
            "sound_in_every_replicate": sound,
            # a work figure is quoted only where the arm is sound; section 7
            "d1_work": (statistics.mean(r[arm]["d1"] for r in reps) if sound else None),
            "d1_work_if_it_were_admissible": statistics.mean(r[arm]["d1"] for r in reps),
            "verifications": statistics.mean(r[arm]["verifications"] for r in reps),
            "applications": statistics.mean(r[arm]["applications"] for r in reps),
            "guards": statistics.mean(r[arm]["guards"] for r in reps),
            "expansions": statistics.mean(r[arm]["expansions"] for r in reps),
        }
    return out


def _terminal(cells: list[dict]) -> tuple[str, str]:
    arm = "EXPANDING_ARM"
    unsound = [c for c in cells if not c["arms"][arm]["sound_in_every_replicate"]]
    sound = [c for c in cells if c["arms"][arm]["sound_in_every_replicate"]]
    full_unsound = [c for c in cells
                    if not c["arms"]["FIXED_FULL_PARENT"]["sound_in_every_replicate"]]
    if full_unsound:
        return ("VOID_THE_SOUND_PARENT_IS_NOT_SOUND",
                "FIXED_FULL_PARENT holds a language that contains the truth at every level, "
                "so it cannot produce a false singleton. It did. The harness is not "
                "implementing the soundness argument it declares and nothing measured under "
                "it means anything.")
    if not unsound:
        wins = [c for c in sound
                if c["arms"][arm]["d1_work"] < c["arms"]["FIXED_FULL_PARENT"]["d1_work"]]
        if wins:
            return ("SELF_EXPANSION_SURVIVES",
                    "The expanding arm held correctness 1.0 at every level and every "
                    "evidence length, and beat FIXED_FULL_PARENT on work. Self-expansion "
                    "survives its first real test and DEV-3's gift was a convenience rather "
                    "than a requirement.")
        return ("SELF_EXPANSION_SOUND_BUT_NOT_CHEAPER",
                "The expanding arm stayed correct everywhere and did not beat the parent "
                "that holds the full language throughout, so expansion costs nothing and "
                "buys nothing.")
    by_level: dict[int, dict[str, list[int]]] = {}
    for c in cells:
        b = by_level.setdefault(c["level"], {"sound": [], "unsound": []})
        key = "sound" if c["arms"][arm]["sound_in_every_replicate"] else "unsound"
        if c["d0_length"] not in b[key]:
            b[key].append(c["d0_length"])
    always_unsound = sorted(l for l, b in by_level.items() if not b["sound"])
    sometimes = sorted(l for l, b in by_level.items() if b["sound"] and b["unsound"])
    always_sound = sorted(l for l, b in by_level.items() if not b["unsound"])
    tracks = all(
        c["arms"][arm]["mean_correctness"]
        == c["arms"]["FIXED_SMALL_PARENT"]["mean_correctness"] for c in cells)
    ratios = [c["arms"]["FIXED_FULL_PARENT"]["d1_work"] / c["arms"][arm]["d1_work"]
              for c in sound]
    best = max(ratios) if ratios else float("nan")

    parts = ["The expanding arm's soundness is GRADED, and the grading is the result."]
    if always_sound:
        parts.append(
            f"At level(s) {always_sound} it is sound at every evidence length -- these are "
            "the levels whose truths its starting language already contains, so expansion "
            "was never required there.")
    if sometimes:
        detail = ", ".join(
            f"level {l} becomes sound only at D0 length "
            f"{min(by_level[l]['sound'])} and above"
            for l in sometimes)
        parts.append(
            f"At level(s) {sometimes} soundness is EARNED BY EVIDENCE rather than by "
            f"language: {detail}. That is a real and unregistered point for the mechanism -- "
            "prediction E5 said the advantage would exist only where expansion was "
            "unnecessary, and it is FALSE, because here expansion reaches a correct guard "
            "for a truth its starting language could not express.")
    if always_unsound:
        parts.append(
            f"At level(s) {always_unsound} it is below correctness 1.0 at EVERY evidence "
            "length in the sweep, including the longest, so the mechanism never becomes "
            "usable there at all.")
    if unsound:
        cells_txt = ", ".join(
            f"level {c['level']} at D0 {c['d0_length']}"
            for c in sorted(unsound, key=lambda c: (c["level"], c["d0_length"]))[:6])
        parts.append(
            f"In {len(unsound)} of {len(cells)} cells it is below correctness 1.0 "
            f"({cells_txt}{', and more' if len(unsound) > 6 else ''}). Under section 7 it "
            "has no admissible work figure in any of them, and the figure it would have "
            "posted is reported under d1_work_if_it_were_admissible so a reader can see "
            "that it is the speed of a wrong answer rather than a cost.")
    parts.append(
        f"Where it is admissible it beats FIXED_FULL_PARENT by up to {best:.2f}x, because a "
        "smaller space collapses to a singleton on fewer observations and it starts "
        "skipping checks sooner.")
    parts.append(
        "The mechanism is visible in the numbers: the expanding arm's correctness equals "
        "the fixed SMALL parent's in every cell, so expansion never fires against the "
        "failure that matters. Expansion triggers on an EMPTY version space; the failure "
        "mode is a wrong SINGLETON, which never empties. Whatever soundness the arm gains "
        "with evidence, it gains as the small parent does and not as an expander."
        if tracks else
        "The expanding arm's correctness differs from the fixed small parent's, so "
        "expansion is doing something on its own; the difference is in the table.")
    return ("SELF_EXPANSION_IS_SOUND_ONLY_BELOW_A_LANGUAGE_LEVEL", " ".join(parts))


def _evidence_verdict(cells: list[dict]) -> str:
    """Computed, because the first version of this text over-claimed.

    It asserted that correctness never reaches 1.0 at any evidence length, which
    was true of the pilot and false of the protected sweep: at the longest
    evidence every cell is sound except level 3 under skewed demand.
    """
    longest = max(c["d0_length"] for c in cells)
    tail = [c for c in cells if c["d0_length"] == longest]
    still = [c for c in tail if not c["arms"]["EXPANDING_ARM"]["sound_in_every_replicate"]]
    head = ("Correctness rises with D0 length: there is more evidence per rule, so fewer "
            "version spaces collapse to a singleton early, and a singleton reached on "
            "complete evidence over a finite extension cannot be extensionally wrong.")
    if not still:
        return (head + f" At the longest evidence length in the sweep ({longest}) every "
                "cell is sound, so in THIS world enough evidence does rescue it. That is a "
                "statement about an extension of sixteen indices and a D0 stream long "
                "enough to cover most of them; it is not a general soundness argument, and "
                "an arm cannot tell from inside whether it has had enough.")
    where = ", ".join(f"level {c['level']} at skew {c['skew']}" for c in still)
    return (head + f" It is not enough everywhere: at the longest evidence length "
            f"({longest}) the arm is still below 1.0 at {where}, so more data makes "
            "premature certainty rarer without making it impossible. The failure survives "
            "exactly where the demand stream is most concentrated and therefore leaves "
            "parts of an extension unobserved, which is the mechanism rather than a "
            "coincidence.")


def build() -> dict[str, Any]:
    cells = [cell(lvl, n, b, k)
             for lvl in SW["levels"] for n in SW["d0_lengths"]
             for b in SW["budget_bits"] for k in SW["skews"]]
    terminal, reason = _terminal(cells)
    arm = "EXPANDING_ARM"
    return {
        "study_id": "DEV4_LANGUAGE_EXPANSION_V1",
        "authority": (
            "E2 synthetic. Withdraws the gift DEV-3 declared -- that the guard language "
            "contains the truth -- and reports what that gift was worth. It withdraws no "
            "negative and no positive: DEV-3's result stands under the gift DEV-3 stated."),
        "plan": DEV4_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed,
                       "pilot_seed": COMMITMENT.pilot_seed},
        "arm_roles": dict(A.ARM_ROLES, REPLAY_ONLY_PARENT="PARENT_NO_GUARDS"),
        "terminal": terminal,
        "terminal_reason": reason,
        "language_sizes": {str(l): len(language(l, SW["extension"])) for l in SW["levels"]},
        "predictions": {
            "E1_all_arms_correct_at_level_1": all(
                c["arms"][a]["sound_in_every_replicate"]
                for c in cells if c["level"] == 1 for a in ARM_IDS),
            "E2_small_languages_are_unsound_above_level_1": any(
                not c["arms"][a]["sound_in_every_replicate"]
                for c in cells if c["level"] > 1
                for a in ("EXPANDING_ARM", "FIXED_SMALL_PARENT")),
            "E3_the_full_language_parent_stays_sound": all(
                c["arms"]["FIXED_FULL_PARENT"]["sound_in_every_replicate"] for c in cells),
            "E4_expansion_beats_the_full_language_where_admissible": all(
                c["arms"][arm]["d1_work"] < c["arms"]["FIXED_FULL_PARENT"]["d1_work"]
                for c in cells if c["arms"][arm]["sound_in_every_replicate"]),
            "E5_advantage_only_where_the_mechanism_is_unnecessary": (
                all(c["level"] == 1 for c in cells
                    if c["arms"][arm]["sound_in_every_replicate"])),
            "E5_verdict": (
                "FALSE, and in the machine's favour. The prediction was registered in the "
                "direction least flattering to self-expansion and it did not hold: at level "
                "2 with enough evidence the arm reaches correctness 1.0 on truths its "
                "starting language cannot express, so it is admissible there and cheaper "
                "than the full-language parent. The advantage is therefore NOT confined to "
                "the levels where expansion was unnecessary. What remains true is the "
                "level-3 boundary and the mechanism note below."),
        },
        "correctness_by_level_and_evidence": [
            {"level": c["level"], "d0_length": c["d0_length"], "skew": c["skew"],
             "expanding": c["arms"][arm]["mean_correctness"],
             "fixed_small": c["arms"]["FIXED_SMALL_PARENT"]["mean_correctness"],
             "fixed_full": c["arms"]["FIXED_FULL_PARENT"]["mean_correctness"],
             "oracle": c["arms"]["ORACLE_LEVEL_PARENT"]["mean_correctness"]}
            for c in cells],
        "what_the_gift_was_worth": (
            "DEV-3 declared that its guard language contained the truth and said a world "
            "where the language must be learned 'can only make the arm's position worse'. "
            "That was an understatement of the right sign. Withdrawing the gift does not "
            "make the arm slower, it makes it WRONG: a version space over a language that "
            "cannot express the truth still collapses to a singleton, and a singleton "
            "reached that way is a false guard the arm cannot distinguish from a true one. "
            "So DEV-3's gift is not a convenience that inflated its result -- it is a "
            "PRECONDITION for the result to be admissible at all, and DEV-3's numbers stand "
            "exactly as far as its stated condition holds and no further."),
        "does_more_evidence_rescue_it": _evidence_verdict(cells),
        "primary_grid": cells,
        "what_this_does_not_establish": DEV4_PLAN["what_this_does_not_establish"],
        "novelty": DEV4_PLAN["novelty"],
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps(doc["predictions"]))
    for r in doc["correctness_by_level_and_evidence"]:
        if r["skew"] != 1.0:
            continue
        print(f"  L{r['level']} d0={r['d0_length']:5d} expanding={r['expanding']:.4f} "
              f"small={r['fixed_small']:.4f} full={r['fixed_full']:.4f} "
              f"oracle={r['oracle']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
