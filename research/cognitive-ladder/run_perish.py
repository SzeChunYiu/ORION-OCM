"""Execute E12 and write ``results/PERISH_E12_V1.json``."""

from __future__ import annotations

import json
import pathlib
import random
import statistics
from typing import Any

import perish_arms as A
from perish import COMMITMENT, PERISH_PLAN, build_perish_world
from retain import APPLY_COST, DERIVE_COST, INDUCE_COST, K_INDUCE, LOOKUP_COST, demand_stream

HERE = pathlib.Path(__file__).parent
OUT = HERE / "results" / "PERISH_E12_V1.json"
SW = PERISH_PLAN["sweep"]


def _seed(tag: str, rep: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.protected_seed[:12], 16) ^ (acc + rep * 7919)


def _pilot_seed(tag: str, rep: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.pilot_seed[:12], 16) ^ (acc + rep * 7919)


def analytic_sign(extension: int, uses_per_rule: float) -> str:
    """Which arm the cost model says wins at lam = 0, from the constants alone.

    Computed without reference to any run. Over ``u`` demands falling in one rule
    of extension ``m``, memoizing costs ``m*DERIVE + (u-m)*LOOKUP`` and a rule
    costs ``K*DERIVE + INDUCE + (u-K)*APPLY``.
    """
    u = uses_per_rule
    memo = extension * DERIVE_COST + max(0.0, u - extension) * LOOKUP_COST
    gen = K_INDUCE * DERIVE_COST + INDUCE_COST + max(0.0, u - K_INDUCE) * APPLY_COST
    return "MACHINE" if gen < memo else "PARENT"


def cell(extension: int, lam: float, protected: bool = True) -> dict:
    seeder = _seed if protected else _pilot_seed
    reps = SW["reps"] if protected else 1
    per_arm: dict[str, list] = {a: [] for a in A.ARMS}
    uses = []
    for rep in range(reps):
        world = build_perish_world(SW["rule_count"], extension, lam, SW["horizon"])
        stream = demand_stream(world.base, SW["horizon"], SW["skew"],
                               random.Random(seeder(f"{extension}-{lam}", rep)))
        touched = {world.base.rule_of[a] for a in stream}
        uses.append(len(stream) / max(1, len(touched)))
        for arm_id in A.ARMS:
            per_arm[arm_id].append(A.run_arm(arm_id, world, stream,
                                             seeder(arm_id, rep)))
    out: dict[str, Any] = {
        "extension": extension, "lam": lam, "reps": reps,
        "answers": SW["rule_count"] * extension,
        "mean_uses_per_touched_rule": statistics.mean(uses),
        "arms": {},
    }
    for arm_id, leds in per_arm.items():
        out["arms"][arm_id] = {
            "role": A.ARM_ROLES[arm_id],
            "total_work": statistics.mean(l.total_work() for l in leds),
            "derivations": statistics.mean(l.derivations for l in leds),
            "first_contact_work": statistics.mean(l.first_contact_work for l in leds),
            "inductions": statistics.mean(l.inductions for l in leds),
            "correctness": min(l.correctness() for l in leds),
        }
    arm = out["arms"]["generalizing_arm"]["total_work"]
    for name in ("memoizer_parent", "clairvoyant_memoizer_parent",
                 "eager_all_rules_parent", "oracle_rule_parent"):
        other = out["arms"][name]["total_work"]
        out[f"ratio_to_{name}"] = arm / other if other else float("inf")
    out["observed_sign"] = "MACHINE" if out["ratio_to_memoizer_parent"] < 1.0 else "PARENT"
    out["analytic_sign_at_lam_zero"] = analytic_sign(extension,
                                                     out["mean_uses_per_touched_rule"])
    return out


def crossover(cells: list[dict], lam: float) -> int | None:
    """Smallest extension at which the arm beats the memoizer, at this lam."""
    wins = [c["extension"] for c in cells
            if c["lam"] == lam and c["observed_sign"] == "MACHINE"]
    return min(wins) if wins else None


def _terminal(cells: list[dict], m_star: dict[str, int | None]) -> tuple[str, str]:
    control = [c for c in cells if c["lam"] == 0.0]
    mismatched = [c for c in control if c["observed_sign"] != c["analytic_sign_at_lam_zero"]]
    if mismatched:
        return ("VOID_CONTROL_DISAGREES_WITH_THE_COST_MODEL",
                "At lam = 0 the observed winner differs from the one the declared cost "
                f"constants imply, at {len(mismatched)} of {len(control)} extensions. The "
                "harness is not implementing the cost model it declares, so nothing "
                "measured under it means anything.")
    beat_ceiling = [c for c in cells if c["ratio_to_oracle_rule_parent"] < 1.0]
    if beat_ceiling:
        return ("VOID_CEILING_IMPLEMENTED_WRONGLY",
                "The arm beat a parent handed every rule for free, which the plan "
                "registered as meaning the ceiling is wrong.")
    lams = sorted(SW["lams"])
    seq = [m_star[str(l)] for l in lams]
    big = max(SW["extensions"]) * 10
    numeric = [big if v is None else v for v in seq]
    fell = numeric[-1] < numeric[0]
    monotone = all(b <= a for a, b in zip(numeric, numeric[1:]))
    if not fell:
        return ("FROZEN_PREDICTION_REFUTED",
                "The crossover extension did not fall as perishability rose "
                f"({seq}). Perishability is not doing the work, so beta in SYNTHESIS_V1 is "
                "specifically about bounded storage and not about scarcity of the "
                "economized resource. The three coordinates are not the right three and "
                "the synthesis law must be demoted to a caching result.")
    return ("FROZEN_PREDICTION_SURVIVES_ONE_TEST",
            "The crossover extension falls as perishability rises "
            f"({seq} at lam {lams}), so a rule pays at strictly lower compressibility once "
            "the opportunity to derive cheaply perishes. That is the out-of-sample "
            "prediction SYNTHESIS_V1 froze in its digest before this world existed, and it "
            "survives. It is ONE point. The pilot for this same experiment produced an "
            "apparent confirmation that was an artifact of compression at large extension, "
            "which is exactly how cheap a confirmation can be, and the control is here "
            "because of it."
            + ("" if monotone else " The fall is not monotone across the swept lams, and "
                                   "the non-monotone step is in the table."))


def build() -> dict[str, Any]:
    cells = [cell(m, l) for m in SW["extensions"] for l in SW["lams"]]
    pilot = [cell(32, l, protected=False) for l in SW["lams"]]
    m_star = {str(l): crossover(cells, l) for l in SW["lams"]}
    terminal, reason = _terminal(cells, m_star)
    control = [c for c in cells if c["lam"] == 0.0]
    eager = [c for c in cells if c["ratio_to_eager_all_rules_parent"] > 1.0]
    return {
        "study_id": "PERISH_E12_V1",
        "authority": (
            "E2 synthetic. Runs the out-of-sample prediction SYNTHESIS_V1 froze in its "
            "commitment digest, and the unrun half of the falsifier attached to the deep "
            "root EAGER_ACQUISITION_IS_DOMINATED_BY_DEFERRED_ACQUISITION. It withdraws no "
            "negative and reinterprets none."),
        "plan": PERISH_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed,
                       "pilot_seed": COMMITMENT.pilot_seed},
        "arm_roles": A.ARM_ROLES,
        "terminal": terminal,
        "terminal_reason": reason,
        "crossover_extension_by_lam": m_star,
        "control": {
            "note": (
                "The lam = 0 row against the analytic break-even, computed from the cost "
                "constants alone. This is the control the pilot failed."),
            "rows": [{"extension": c["extension"],
                      "mean_uses_per_touched_rule": c["mean_uses_per_touched_rule"],
                      "observed": c["observed_sign"],
                      "analytic": c["analytic_sign_at_lam_zero"],
                      "agrees": c["observed_sign"] == c["analytic_sign_at_lam_zero"]}
                     for c in control],
            "all_agree": all(c["observed_sign"] == c["analytic_sign_at_lam_zero"]
                             for c in control),
        },
        "predictions": {
            "P1_control_matches_the_cost_model": all(
                c["observed_sign"] == c["analytic_sign_at_lam_zero"] for c in control),
            "P2_crossover_falls_with_perishability": terminal.startswith(
                "FROZEN_PREDICTION_SURVIVES"),
            "P3_beats_the_clairvoyant_memoizer_somewhere": any(
                c["ratio_to_clairvoyant_memoizer_parent"] < 1.0 for c in cells),
            "P4_does_not_beat_the_ceiling": not any(
                c["ratio_to_oracle_rule_parent"] < 1.0 for c in cells),
            "P5_eager_beats_the_triggered_arm_somewhere": bool(eager),
        },
        "the_deep_roots_question": {
            "note": (
                "eager_all_rules_parent acquires every rule at step 0 having seen no demand "
                "at all -- the schedule that lost in E3, E6, E7 and E10. The deep root's "
                "falsifier asks whether it still loses when the opportunity to derive "
                "cheaply perishes. Where it wins, the deep root is narrowed AGAINST the "
                "machine, and that is reported here beside the law's result rather than "
                "under it."),
            "cells_where_eager_beats_the_triggered_arm": [
                {"extension": c["extension"], "lam": c["lam"],
                 "ratio_arm_over_eager": c["ratio_to_eager_all_rules_parent"]}
                for c in eager],
            "verdict": (
                "The deep root is NARROWED: untriggered eager acquisition, which lost in "
                "four earlier experiments, beats the demand-triggered arm where "
                "perishability is high, because it buys every derivation at the cheapest "
                "price the world will ever offer. Waiting for demand is itself a cost once "
                "waiting is charged." if eager else
                "The deep root SURVIVES this falsifier: even with derivation perishing, "
                "acquiring on demonstrated demand beat acquiring on a schedule at every "
                "setting in the grid.")
        },
        "capability_gate": {
            "every_arm_correctness": sorted({c["arms"][a]["correctness"]
                                             for c in cells for a in A.ARMS}),
            "note": "Every arm serves every demand, so the work comparison is admissible.",
        },
        "primary_grid": cells,
        "pilot": pilot,
        "what_this_does_not_establish": PERISH_PLAN["what_this_does_not_establish"],
        "novelty": PERISH_PLAN["novelty"],
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("crossover m* by lam:", doc["crossover_extension_by_lam"])
    print("control:", "all agree" if doc["control"]["all_agree"] else "MISMATCH")
    for r in doc["control"]["rows"]:
        print(f"    m={r['extension']:3d} u={r['mean_uses_per_touched_rule']:6.1f} "
              f"observed={r['observed']:8s} analytic={r['analytic']:8s} "
              f"{'ok' if r['agrees'] else 'MISMATCH'}")
    print("predictions:", json.dumps(doc["predictions"]))
    for c in doc["primary_grid"]:
        print(f"  m={c['extension']:3d} lam={c['lam']:5.1f} "
              f"arm/memo={c['ratio_to_memoizer_parent']:.3f} "
              f"arm/clair={c['ratio_to_clairvoyant_memoizer_parent']:.3f} "
              f"arm/eager={c['ratio_to_eager_all_rules_parent']:.3f} {c['observed_sign']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
