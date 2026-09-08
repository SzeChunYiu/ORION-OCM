from __future__ import annotations

import argparse
import hashlib
import json
import re
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

getcontext().prec = 40

SOURCE_PATH = Path(__file__).resolve().parents[1] / "native-learning-evidence-v1" / "HANDOFF.md"
EXPECTED_SOURCE_GIT_BLOB_SHA1 = "9905090c7f5de3a0f0afb35da65d40701a771b94"


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _decimal_from_cost_row(text: str, label: str) -> Decimal:
    pattern = re.compile(
        rf"^\|\s*{re.escape(label)}\s*\|\s*([0-9]+(?:\.[0-9]+)?)\s*\|",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if match is None:
        raise ValueError(f"missing observed-cost row: {label}")
    return Decimal(match.group(1))


def _attempts_from_arm_row(text: str, label: str) -> int:
    pattern = re.compile(
        rf"^\|\s*{re.escape(label)}\s*\|\s*(?:—|-|[0-9,]+)\s*\|\s*([0-9,]+)\s*\|",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if match is None:
        raise ValueError(f"missing arm row: {label}")
    return int(match.group(1).replace(",", ""))


def strict_break_even_uses(fixed_cost: Decimal, saving_per_use: Decimal) -> int | None:
    """Smallest integer n with n*saving_per_use > fixed_cost."""
    if saving_per_use <= 0:
        return None
    return int(fixed_cost // saving_per_use) + 1


def analyze_text(text: str, *, source_blob_sha1: str | None = None) -> dict[str, Any]:
    attempts = {
        "ordinary_positive": _attempts_from_arm_row(text, "Ordinary baseline"),
        "learned_positive": _attempts_from_arm_row(text, "Learned I enabled"),
        "ordinary_false": _attempts_from_arm_row(text, "False target, ordinary"),
        "learned_false": _attempts_from_arm_row(text, "False target, I enabled"),
    }
    costs = {
        "training_export": _decimal_from_cost_row(text, "Training native export"),
        "producer": _decimal_from_cost_row(text, "Producer A"),
        "projection": _decimal_from_cost_row(text, "Serving projection"),
        "baseline_fresh": _decimal_from_cost_row(text, "Baseline fresh B"),
        "enabled_fresh": _decimal_from_cost_row(text, "Enabled fresh B"),
        "baseline_checker": _decimal_from_cost_row(text, "Baseline native checker"),
        "enabled_checker": _decimal_from_cost_row(text, "Enabled native checker"),
    }

    positive_attempt_saving = attempts["ordinary_positive"] - attempts["learned_positive"]
    false_attempt_penalty = attempts["learned_false"] - attempts["ordinary_false"]
    call_saving = (
        costs["baseline_fresh"]
        + costs["baseline_checker"]
        - costs["enabled_fresh"]
        - costs["enabled_checker"]
    )
    acquisition_all = costs["training_export"] + costs["producer"] + costs["projection"]
    acquisition_post_export = costs["producer"] + costs["projection"]

    if positive_attempt_saving <= 0:
        demand_threshold = None
    elif false_attempt_penalty <= 0:
        demand_threshold = Decimal(0)
    else:
        demand_threshold = Decimal(false_attempt_penalty) / Decimal(
            positive_attempt_saving + false_attempt_penalty
        )

    return {
        "schema": "ocm.general-net-benefit.native-break-even.v1",
        "study": "Native learned-method lifetime break-even bound before matched-parent parity",
        "source": {
            "path": "research/native-learning-evidence-v1/HANDOFF.md",
            "git_blob_sha1": source_blob_sha1,
        },
        "observed": {
            "positive_action_attempt_saving_per_use": positive_attempt_saving,
            "false_target_action_attempt_penalty_per_use": false_attempt_penalty,
            "positive_call_wall_saving_seconds": str(call_saving),
            "acquisition_seconds_including_training_export": str(acquisition_all),
            "acquisition_seconds_after_training_export": str(acquisition_post_export),
        },
        "derived": {
            "strict_break_even_positive_uses_including_training_export": strict_break_even_uses(
                acquisition_all, call_saving
            ),
            "strict_break_even_positive_uses_after_training_export": strict_break_even_uses(
                acquisition_post_export, call_saving
            ),
            "positive_demand_fraction_threshold_for_attempt_count_only": (
                str(demand_threshold) if demand_threshold is not None else None
            ),
        },
        "parent_parity": {
            "same_derived_lemma_parent_executed_in_this_evidence": False,
            "ocm_specific_residual_established": False,
            "reason": (
                "The source control is a method-use ablation. A matched ordinary-derived-lemma "
                "parent with the same checked result must receive equal applicability before "
                "recipe-specific or OCM-specific net benefit can be attributed."
            ),
        },
        "claim_boundary": {
            "wall_time_speedup_claimed": False,
            "observed_break_even_is_replication_claim": False,
            "attempt_threshold_is_complete_lifetime_economics": False,
            "general_ocm_net_benefit_claimed": False,
            "ml_authorized": False,
        },
        "terminal": "NATIVE_BREAK_EVEN_BOUND_ONLY_MATCHED_PARENT_PENDING",
    }


def run(source_path: Path = SOURCE_PATH) -> dict[str, Any]:
    data = source_path.read_bytes()
    actual_blob = git_blob_sha1(data)
    if actual_blob != EXPECTED_SOURCE_GIT_BLOB_SHA1:
        raise RuntimeError(
            f"source custody drift: expected {EXPECTED_SOURCE_GIT_BLOB_SHA1}, got {actual_blob}"
        )
    return analyze_text(data.decode("utf-8"), source_blob_sha1=actual_blob)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    if args.github_notice:
        d = result["derived"]
        print(
            "::notice title=Native lifetime break-even bound::"
            f"observed strict positive-use threshold={d['strict_break_even_positive_uses_including_training_export']} "
            "including training export; matched ordinary-lemma parent still pending"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
