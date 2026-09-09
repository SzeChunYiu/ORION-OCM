"""Run the R0D short-circuit unanimity parent on DEV-6's frozen sweep."""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import statistics
import sys

HERE = pathlib.Path(__file__).parent
DEV = HERE.parent / "developmental-spine"
COG = HERE.parent / "cognitive-ladder"
sys.path.insert(0, str(DEV))
sys.path.insert(0, str(COG))
sys.path.insert(0, str(HERE))

from donor_custody import require_module_path, verify_inventory
from run_guards import require_zero_maintenance

REPOSITORY_ROOT = HERE.resolve().parents[1]
verify_inventory(REPOSITORY_ROOT)  # before any donor/plan import
import dev6_arms as A
import run_dev6 as D6
import dev6 as D6_CONFIG
require_module_path(A, REPOSITORY_ROOT, "research/developmental-spine/dev6_arms.py")
require_module_path(D6, REPOSITORY_ROOT, "research/developmental-spine/run_dev6.py")
require_module_path(D6_CONFIG, REPOSITORY_ROOT, "research/developmental-spine/dev6.py")
import shortcircuit_parent as S
from dev4 import build_level_world, d1_stream
from retain import demand_stream


SCHEMA = "ocm.paid-decision-region.r0d.shortcircuit.v2"


def _same_nonlookup_semantics(left, right) -> bool:
    return S.phase_semantics(left) == S.phase_semantics(right)


def one_rep(level: int, d1_length: int, budget: int, skew: float, rep: int) -> dict:
    seed = D6._seed(f"dev6-{level}-{d1_length}-{budget}-{skew}", rep)
    world, _truth = build_level_world(
        D6.SW["rule_count"], D6.SW["extension"], level, random.Random(seed ^ 0xA1)
    )
    d0 = demand_stream(world.base, D6.SW["d0_length"], skew, random.Random(seed ^ 0xB2))
    d1 = d1_stream(world, d1_length, skew, random.Random(seed ^ 0xC3))

    _p0, singleton, _c0, singleton_m = A._run(world, d0, d1, budget, "singleton")
    _p1, fullscan, _c1, fullscan_m = A._run(world, d0, d1, budget, "unanimity_naive")
    _p2, short, _c2, short_m = S.run_shortcircuit(world, d0, d1, budget)

    if not _same_nonlookup_semantics(fullscan, short):
        raise AssertionError("short-circuit parent changed a non-deliberation Phase coordinate")
    require_zero_maintenance(fullscan_m["maintenance"], short_m["maintenance"])
    if fullscan_m["consultations"] != short_m["consultations"]:
        raise AssertionError("short-circuit parent changed the number of consultations")
    if short_m["consultation_charge"] > fullscan_m["consultation_charge"]:
        raise AssertionError("short-circuit accounting exceeded full-scan accounting")
    if singleton.correctness() != 1.0 or fullscan.correctness() != 1.0 or short.correctness() != 1.0:
        raise AssertionError("full-language source-control arm lost correctness")

    return {
        "SINGLETON": {
            "work": singleton.total_work(0.0),
            "consultation": singleton_m["consultation_charge"],
            "verifications": singleton.verifications,
        },
        "UNANIMITY_FULLSCAN": {
            "work": fullscan.total_work(0.0),
            "consultation": fullscan_m["consultation_charge"],
            "verifications": fullscan.verifications,
        },
        "UNANIMITY_SHORTCIRCUIT": {
            "work": short.total_work(0.0),
            "consultation": short_m["consultation_charge"],
            "verifications": short.verifications,
        },
        "semantic_identity": _same_nonlookup_semantics(fullscan, short),
    }


def cell(level: int, d1_length: int, budget: int, skew: float) -> dict:
    reps = [one_rep(level, d1_length, budget, skew, rep) for rep in range(D6.SW["reps"])]
    arms = {}
    for arm in ("SINGLETON", "UNANIMITY_FULLSCAN", "UNANIMITY_SHORTCIRCUIT"):
        arms[arm] = {
            "mean_d1_work": statistics.mean(row[arm]["work"] for row in reps),
            "mean_consultation": statistics.mean(row[arm]["consultation"] for row in reps),
            "mean_verifications": statistics.mean(row[arm]["verifications"] for row in reps),
        }
    singleton = arms["SINGLETON"]["mean_d1_work"]
    fullscan = arms["UNANIMITY_FULLSCAN"]["mean_d1_work"]
    short = arms["UNANIMITY_SHORTCIRCUIT"]["mean_d1_work"]
    return {
        "level": level,
        "d1_length": d1_length,
        "budget_bits": budget,
        "skew": skew,
        "reps": D6.SW["reps"],
        "arms": arms,
        "ratio_short_to_singleton": short / singleton,
        "ratio_short_to_fullscan": short / fullscan,
        "consultation_saved_fraction_vs_fullscan": (
            1.0 - arms["UNANIMITY_SHORTCIRCUIT"]["mean_consultation"]
            / arms["UNANIMITY_FULLSCAN"]["mean_consultation"]
            if arms["UNANIMITY_FULLSCAN"]["mean_consultation"] else 0.0
        ),
        "semantic_identity_all_reps": all(row["semantic_identity"] for row in reps),
    }


def build() -> dict:
    cells = [
        cell(level, n, budget, skew)
        for level in D6.SW["levels"]
        for n in D6.SW["d1_lengths"]
        for budget in D6.SW["budget_bits"]
        for skew in D6.SW["skews"]
    ]
    short_ratios = [row["ratio_short_to_singleton"] for row in cells]
    versus_full = [row["ratio_short_to_fullscan"] for row in cells]
    consultation_savings = [row["consultation_saved_fraction_vs_fullscan"] for row in cells]
    semantic_identity = all(row["semantic_identity_all_reps"] for row in cells)
    short_beats_singleton = sum(ratio < 1.0 for ratio in short_ratios)
    fullscan_beats_singleton = sum(
        row["arms"]["UNANIMITY_FULLSCAN"]["mean_d1_work"]
        < row["arms"]["SINGLETON"]["mean_d1_work"]
        for row in cells
    )
    terminal = (
        "SHORTCIRCUIT_UNANIMITY_STRICT_PARENT_R0D"
        if semantic_identity
        and all(ratio <= 1.0 + 1e-12 for ratio in versus_full)
        and any(ratio < 1.0 - 1e-12 for ratio in versus_full)
        else "SHORTCIRCUIT_PARENT_NOT_ESTABLISHED_R0D"
    )
    return {
        "schema": SCHEMA,
        "study": "DEV-6 exact short-circuit decision-region consultation parent",
        "source_custody": S.source_fidelity(),
        "scope": {
            "donor": "DEV6_HONEST_CONSULTATION_PRICE_V1",
            "declared_source_inventory_checked": True,
            "complete_study_requalification": False,
            "decision_rule_changed": False,
            "version_space_changed": False,
            "consultation_calls_changed": False,
            "maintenance_state_added": False,
            "only_accounting_change": "charge exact survivors inspected until first disagreement or full unanimity",
            "ml_used": False,
        },
        "cells": cells,
        "summary": {
            "cells": len(cells),
            "semantic_identity_all_cells": semantic_identity,
            "fullscan_beats_singleton_cells": fullscan_beats_singleton,
            "shortcircuit_beats_singleton_cells": short_beats_singleton,
            "shortcircuit_ratio_to_singleton_range": [min(short_ratios), max(short_ratios)],
            "shortcircuit_ratio_to_fullscan_range": [min(versus_full), max(versus_full)],
            "consultation_saved_fraction_range": [min(consultation_savings), max(consultation_savings)],
            "mean_consultation_saved_fraction": statistics.mean(consultation_savings),
        },
        "claim_boundary": {
            "unanimity_is_novel": False,
            "short_circuit_evaluation_is_novel": False,
            "this_is_a_stronger_exact_parent_before_caching": True,
            "full_paid_drd_bellman_optimum_claimed": False,
            "misspecified_language_solved": False,
            "learned_router_authorized": False,
        },
        "terminal": terminal,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args()
    doc = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, sort_keys=True, indent=2) + "\n")
    notice = {"terminal": doc["terminal"], **doc["summary"]}
    rendered = json.dumps(notice, sort_keys=True, separators=(",", ":"))
    if args.github_notice:
        print(f"::notice title=R0D short-circuit decision-region parent::{rendered}")
    else:
        print(rendered)
    return 0 if doc["terminal"] == "SHORTCIRCUIT_UNANIMITY_STRICT_PARENT_R0D" else 1


if __name__ == "__main__":
    raise SystemExit(main())
