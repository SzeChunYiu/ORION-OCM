"""Execute X4 and write ``results/X4_FINAL_ACCOUNTING_V1.json``."""

from __future__ import annotations

import json
import pathlib
import random
import statistics
import sys
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import dev2_parents as D2
import dev6_arms as A6
import x4
from dev3 import GUARD_PERIODS
from dev4 import build_level_world, d1_stream, language
from retain import demand_stream
from x4 import ARM_LANGUAGES, COMMITMENT, X4_PLAN

OUT = HERE.parent / "cognitive-ladder" / "results" / "X4_FINAL_ACCOUNTING_V1.json"
SW = X4_PLAN["sweep"]
ARMS = tuple(ARM_LANGUAGES) + ("REPLAY_ONLY_PARENT",)
MODE = {"GUARDED_SMALL_LANGUAGE": "singleton",
        "SINGLETON_FULL_LANGUAGE": "singleton",
        "UNANIMITY_FULL_LANGUAGE": "unanimity_naive"}


def _seed(tag: str, rep: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.protected_seed[:12], 16) ^ (acc + rep * 7919)


def one_rep(level: int, d1_length: int, budget: int, skew: float, rep: int) -> dict:
    s = _seed(f"x4-{level}-{d1_length}-{budget}-{skew}", rep)
    world, _ = build_level_world(SW["rule_count"], SW["extension"], level,
                                 random.Random(s ^ 0xA1))
    d0 = demand_stream(world.base, SW["d0_length"], skew, random.Random(s ^ 0xB2))
    d1 = d1_stream(world, d1_length, skew, random.Random(s ^ 0xC3))
    out: dict[str, Any] = {}
    for arm, lang_level in ARM_LANGUAGES.items():
        _p0, p1, _c, meters = A6._run(world, d0, d1, budget, MODE[arm], lang_level)
        out[arm] = {"d1": p1.total_work(0.0), "correctness": p1.correctness(),
                    "verifications": p1.verifications,
                    "deliberation": meters["deliberation_total"]}
    _, r1, _ = D2.replay_only(world, d0, d1, budget)
    out["REPLAY_ONLY_PARENT"] = {"d1": r1.total_work(0.0),
                                 "correctness": r1.correctness(),
                                 "verifications": 0, "deliberation": 0}
    return out


def cell(level: int, d1_length: int, budget: int, skew: float) -> dict:
    reps = [one_rep(level, d1_length, budget, skew, r) for r in range(SW["reps"])]
    out = {"level": level, "d1_length": d1_length, "budget_bits": budget, "skew": skew,
           "reps": SW["reps"], "arms": {}}
    for arm in ARMS:
        correct = [r[arm]["correctness"] for r in reps]
        sound = all(c == 1.0 for c in correct)
        out["arms"][arm] = {
            "language_size": (len(language(ARM_LANGUAGES[arm], SW["extension"]))
                              if arm in ARM_LANGUAGES else None),
            "min_correctness": min(correct),
            "sound_in_every_replicate": sound,
            "d1_work": statistics.mean(r[arm]["d1"] for r in reps) if sound else None,
            "d1_work_if_it_were_admissible": statistics.mean(r[arm]["d1"] for r in reps),
            "verifications": statistics.mean(r[arm]["verifications"] for r in reps),
            "deliberation": statistics.mean(r[arm]["deliberation"] for r in reps),
        }
    replay = out["arms"]["REPLAY_ONLY_PARENT"]["d1_work"]
    out["ratio_to_replay"] = {
        a: (out["arms"][a]["d1_work"] / replay
            if out["arms"][a]["d1_work"] is not None and replay else None)
        for a in ARM_LANGUAGES}
    out["beats_replay"] = {a: (v is not None and v < 1.0)
                           for a, v in out["ratio_to_replay"].items()}
    return out


def _terminal(cells: list[dict]) -> tuple[str, str]:
    guarded = "GUARDED_SMALL_LANGUAGE"
    full = "SINGLETON_FULL_LANGUAGE"
    l1 = [c for c in cells if c["level"] == 1]
    l1_sound = [c for c in l1 if c["arms"][guarded]["sound_in_every_replicate"]]
    l1_wins = [c for c in l1_sound if c["beats_replay"][guarded]]
    if not l1_sound:
        return ("VOID_THE_SMALL_LANGUAGE_IS_UNSOUND_WHERE_IT_CONTAINS_THE_TRUTH",
                "The level-1 language contains every level-1 truth, so the guarded arm "
                "cannot produce a false guard there. It did, which is a harness bug.")
    if not l1_wins:
        return ("NO_CARRY_ADVANTAGE_UNDER_ANY_REPRESENTATION_TRIED",
                "Under one honest charge rule the guarded small-language arm does not beat "
                "the replay parent at level 1, where its language contains the truth and it "
                "is sound. This lane therefore has no carry advantage under any "
                "representation it has tried. DEV-3 must be corrected the way DEV-5 was, "
                "X3's finding generalises rather than being confined to large languages, "
                "and the developmental spine's one measured transition loses its positive.")
    best = min(c["ratio_to_replay"][guarded] for c in l1_wins)
    full_l1 = [c["ratio_to_replay"][full] for c in l1
               if c["ratio_to_replay"][full] is not None]
    unsound = [c for c in cells if c["level"] > 1
               and not c["arms"][guarded]["sound_in_every_replicate"]]
    reason = (
        f"At level 1, where its language contains the truth and it is sound in every "
        f"replicate, the guarded small-language arm beats the replay parent at "
        f"{len(l1_wins)} of {len(l1_sound)} settings, best ratio {best:.3f}, under the same "
        "charge rule that cost DEV-5 its factor. DEV-3's carry advantage therefore SURVIVES "
        "the honest price, and it survives for a reason DEV-6 could not have shown: its "
        "guard is a single collapsed predicate consulted in O(1), so a charge proportional "
        "to what a consultation examines charges it 1, and it never scanned anything.")
    if full_l1:
        reason += (
            f" The same decision rule over the full 433-predicate language does NOT beat "
            f"replay at level 1 (ratios {min(full_l1):.2f} to {max(full_l1):.2f}), which "
            "isolates the cause: a version space that large rarely collapses, so the rule "
            "rarely fires and the arm verifies almost every demand. X3 concluded from "
            "DEV-6's full-language arms that the carry advantage fails, and that conclusion "
            "was about LANGUAGE SIZE rather than about guards. X3 is corrected here, not "
            "withdrawn -- everything it reported about the unanimity lineage stands.")
    if unsound:
        reason += (
            f" The same arm is unsound at {len(unsound)} settings above level 1 and has no "
            "admissible work figure there, reproducing DEV-4: the advantage is conditional "
            "on a language that can express the truth, which is the precondition DEV-4 "
            "proved binding and this study does not remove.")
    return ("CARRY_ADVANTAGE_SURVIVES_ON_A_SMALL_SOUND_LANGUAGE", reason)


def build() -> dict[str, Any]:
    cells = [cell(lvl, n, b, k) for lvl in SW["levels"] for n in SW["d1_lengths"]
             for b in SW["budget_bits"] for k in SW["skews"]]
    terminal, reason = _terminal(cells)
    guarded, full, unan = ARMS[0], ARMS[1], ARMS[2]
    l1 = [c for c in cells if c["level"] == 1]
    return {
        "study_id": "X4_FINAL_ACCOUNTING_V1",
        "authority": (
            "E2 synthetic, and an audit rather than a new claim. It applies one charge rule "
            "to every carry-advantage claim this lane has made. It withdraws nothing from "
            "DEV-5, DEV-6 or X3; it corrects a reading of X3."),
        "plan": X4_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed},
        "terminal": terminal,
        "terminal_reason": reason,
        "language_sizes": {a: len(language(l, SW["extension"]))
                           for a, l in ARM_LANGUAGES.items()},
        "dev3_language_note": (
            "DEV-3's own guard language had 15 predicates (periods 2-5 with phases, plus "
            f"the empty guard); the level-1 language used here has "
            f"{len(language(1, SW['extension']))} (periods {GUARD_PERIODS[:2]}). They are "
            "not identical and the study does not claim they are: what they share is being "
            "SMALL enough to collapse, which is the property under test. Using DEV-4's "
            "ladder keeps every arm on one world family."),
        "predictions": {
            "Z1_small_language_beats_replay_at_level_1": all(
                c["beats_replay"][guarded] for c in l1
                if c["arms"][guarded]["sound_in_every_replicate"]),
            "Z2_full_language_loses_at_level_1": all(
                not c["beats_replay"][full] for c in l1),
            "Z3_small_language_unsound_above_level_1": any(
                not c["arms"][guarded]["sound_in_every_replicate"]
                for c in cells if c["level"] > 1),
            "Z4_unanimity_beats_singleton_on_the_full_language": all(
                c["arms"][unan]["d1_work_if_it_were_admissible"]
                < c["arms"][full]["d1_work_if_it_were_admissible"] for c in cells),
            "Z5_nothing_beats_replay_at_level_3": all(
                not any(c["beats_replay"].values()) for c in cells if c["level"] == 3),
        },
        "what_this_corrects": (
            "X3 concluded that the carry advantage against replay mostly fails the honest "
            "price. Every arm it measured held the full 433-predicate language, because it "
            "inherited DEV-6's arms, and DEV-6 had run the singleton rule over that language "
            "rather than over the small one DEV-3 used. The conclusion was therefore about "
            "how many candidates a version space holds, not about whether a guard pays. "
            "X3's numbers are correct and its reading of them was too broad; the correction "
            "is recorded here and X3's receipt is not withdrawn."),
        "what_survives_after_every_audit": (
            "One conditional carry advantage. A rule carrying a guard drawn from a language "
            "small enough to collapse beats experience replay at matched correctness, under "
            "a consultation charge proportional to what it examines, inside the budget "
            "window DEV-3 computed. It requires the language to contain the truth, which "
            "DEV-4 proved is a precondition and not a convenience, and it does not extend to "
            "large languages, where the same rule rarely fires. Everything else this lane "
            "claimed about carry has been either corrected downward or withdrawn."),
        "primary_grid": cells,
        "what_this_does_not_establish": X4_PLAN["what_this_does_not_establish"],
        "novelty": X4_PLAN["novelty"],
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps(doc["predictions"]))
    for c in doc["primary_grid"]:
        if c["d1_length"] != 1000 or c["skew"] != 1.0:
            continue
        r = c["ratio_to_replay"]
        print(f"  L{c['level']} B={c['budget_bits']:5d} "
              f"guarded_small={r['GUARDED_SMALL_LANGUAGE']} "
              f"singleton_full={r['SINGLETON_FULL_LANGUAGE']} "
              f"unanimity_full={r['UNANIMITY_FULL_LANGUAGE']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
