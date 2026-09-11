"""Registered C1 neural Semantic Proposal Geometry assay.

See GMI_NEURAL_SPG_PROTOCOL_V1.md.  This script intentionally uses only the
frozen finite synthetic grid.  It tests whether gradient-trained developmental
representation history changes *pre-query* semantic target probability on
fresh task heads under the same SPG/K1 meaning used by GMI program/search work.

This is representation-learning / transfer-learning parent territory.  A
positive result is cross-realization measurement evidence, not neural novelty.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean, median
from typing import Dict, Iterable, Mapping, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


SCHEMA = "GMINeuralSPGC1ReceiptV1"
PROTOCOL = "GMI_NEURAL_SPG_PROTOCOL_V1"

D = 20
K = 4
A1_SEED = 17
A2_SEED = 23
DEV_TASK_SEEDS = tuple(range(1000, 1012))
DEV_EXAMPLES_PER_TASK = 512
PRETRAIN_STEPS = 1200
PRETRAIN_BATCH = 64
PRETRAIN_LR = 0.03
REPLICATE_SEEDS = (41, 42, 43, 44)
A1_TARGET_SEEDS = tuple(range(2100, 2112))
A2_TARGET_SEEDS = tuple(range(3100, 3112))
SUPPORT = 16
QUERY = 512
HEAD_STEPS = 300
HEAD_LR = 0.05
HEAD_WEIGHT_DECAY = 1e-4

# Frozen finite-grid acceptance thresholds.
MIN_POSITIVE_ROWS = 40
MIN_MEDIAN_MATCHED_GAIN_BITS = 0.25
MIN_MEDIAN_SPECIFICITY_GAP_BITS = 0.25
MAX_MEDIAN_CROSS_GAIN_BITS = 0.10


@dataclass(frozen=True)
class TaskRow:
    ecology: str
    replicate_seed: int
    target_seed: int
    arm: str
    mean_surprisal_bits: float
    median_surprisal_bits: float
    mean_target_probability: float
    accuracy: float


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def frozen_runtime() -> None:
    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        # May already be fixed by an embedding process; one-thread intra-op and
        # deterministic algorithms remain load-bearing for the reference run.
        pass
    torch.use_deterministic_algorithms(True)


def make_latent_matrix(seed: int) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    raw = torch.randn(K, D, generator=generator)
    q, _ = torch.linalg.qr(raw.T, mode="reduced")
    result = q.T.contiguous()
    # Row orthonormality is part of the task contract.
    eye = result @ result.T
    if not torch.allclose(eye, torch.eye(K), atol=1e-5, rtol=1e-5):
        raise ValueError("latent matrix construction lost row orthonormality")
    return result


def normalized_task_vector(seed: int) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    vector = torch.randn(K, generator=generator)
    norm = torch.linalg.norm(vector)
    if norm <= 0:
        raise ValueError("degenerate task vector")
    return vector / norm


def sample_task(
    latent: torch.Tensor,
    *,
    task_seed: int,
    n: int,
    example_seed: int,
) -> Tuple[torch.Tensor, torch.Tensor]:
    if n <= 0:
        raise ValueError("n must be positive")
    vector = normalized_task_vector(task_seed)
    generator = torch.Generator().manual_seed(example_seed)
    x = torch.randn(n, D, generator=generator)
    hidden = torch.tanh(x @ latent.T)
    logits = hidden @ vector
    y = (logits > 0).float()
    return x, y


class NeuralTrunk(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear = nn.Linear(D, K)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.tanh(self.linear(x))


class IdentityTrunk(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x


class OracleTrunk(nn.Module):
    def __init__(self, latent: torch.Tensor) -> None:
        super().__init__()
        self.register_buffer("latent", latent.clone())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.tanh(x @ self.latent.T)


def random_trunk(seed: int) -> NeuralTrunk:
    set_seed(seed)
    return NeuralTrunk()


def pretrain_trunk(latent: torch.Tensor, *, init_seed: int) -> NeuralTrunk:
    # Resetting to the same init_seed for A1/A2 means MATCHED and CROSS begin
    # from the exact same trunk/head initialization; only developmental labels
    # differ through the latent family.
    set_seed(init_seed)
    trunk = NeuralTrunk()
    heads = nn.ModuleList(nn.Linear(K, 1) for _ in DEV_TASK_SEEDS)
    optimizer = torch.optim.Adam(
        list(trunk.parameters()) + list(heads.parameters()),
        lr=PRETRAIN_LR,
    )

    datasets = []
    for task_seed in DEV_TASK_SEEDS:
        x, y = sample_task(
            latent,
            task_seed=task_seed,
            n=DEV_EXAMPLES_PER_TASK,
            example_seed=700_000 + task_seed,
        )
        datasets.append((x, y))

    for step in range(PRETRAIN_STEPS):
        task_index = step % len(DEV_TASK_SEEDS)
        x, y = datasets[task_index]
        indices = torch.randint(0, len(x), (PRETRAIN_BATCH,))
        logits = heads[task_index](trunk(x[indices])).squeeze(-1)
        loss = F.binary_cross_entropy_with_logits(logits, y[indices])
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return trunk


def fit_target_head(
    trunk: nn.Module,
    x_support: torch.Tensor,
    y_support: torch.Tensor,
    *,
    head_seed: int,
) -> nn.Linear:
    for parameter in trunk.parameters():
        parameter.requires_grad_(False)
    with torch.no_grad():
        feature_dim = int(trunk(x_support[:1]).shape[1])

    set_seed(head_seed)
    head = nn.Linear(feature_dim, 1)
    optimizer = torch.optim.Adam(
        head.parameters(),
        lr=HEAD_LR,
        weight_decay=HEAD_WEIGHT_DECAY,
    )
    with torch.no_grad():
        features = trunk(x_support).detach()

    for _ in range(HEAD_STEPS):
        logits = head(features).squeeze(-1)
        loss = F.binary_cross_entropy_with_logits(logits, y_support)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    return head


def evaluate_query(
    trunk: nn.Module,
    head: nn.Linear,
    x_query: torch.Tensor,
    y_query: torch.Tensor,
) -> Tuple[float, float, float, float]:
    with torch.no_grad():
        logits = head(trunk(x_query)).squeeze(-1)
        p1 = torch.sigmoid(logits)
        target_probability = torch.where(y_query > 0.5, p1, 1 - p1)
        target_probability = torch.clamp(target_probability, min=1e-12, max=1.0)
        surprisal = -torch.log2(target_probability)
        prediction = p1 > 0.5
        accuracy = (prediction == (y_query > 0.5)).float()
    return (
        float(surprisal.mean()),
        float(surprisal.median()),
        float(target_probability.mean()),
        float(accuracy.mean()),
    )


def target_example_seed(ecology: str, target_seed: int) -> int:
    base = 1_100_000 if ecology == "A1" else 1_300_000
    return base + target_seed


def evaluate_ecology(
    *,
    ecology: str,
    latent_target: torch.Tensor,
    target_seeds: Sequence[int],
    matched_trunk: NeuralTrunk,
    cross_trunk: NeuralTrunk,
    reset_trunk: NeuralTrunk,
    replicate_seed: int,
) -> list[TaskRow]:
    rows: list[TaskRow] = []
    trunks: Mapping[str, nn.Module] = {
        "MATCHED_HISTORY_NEURAL": matched_trunk,
        "CROSS_HISTORY_NEURAL": cross_trunk,
        "RESET_NEURAL": reset_trunk,
        "RAW_LINEAR_PARENT": IdentityTrunk(),
        "ORACLE_REPRESENTATION": OracleTrunk(latent_target),
    }

    for target_seed in target_seeds:
        x, y = sample_task(
            latent_target,
            task_seed=target_seed,
            n=SUPPORT + QUERY,
            example_seed=target_example_seed(ecology, target_seed),
        )
        x_support, y_support = x[:SUPPORT], y[:SUPPORT]
        x_query, y_query = x[SUPPORT:], y[SUPPORT:]
        # One target-head seed for all arms in the same replicate/target. Same
        # dimensional neural heads therefore begin with exactly matched state.
        head_seed = 2_000_000 + replicate_seed * 10_000 + target_seed
        for arm, trunk in trunks.items():
            head = fit_target_head(
                trunk,
                x_support,
                y_support,
                head_seed=head_seed,
            )
            mean_i, median_i, mean_p, accuracy = evaluate_query(
                trunk,
                head,
                x_query,
                y_query,
            )
            rows.append(
                TaskRow(
                    ecology=ecology,
                    replicate_seed=replicate_seed,
                    target_seed=target_seed,
                    arm=arm,
                    mean_surprisal_bits=mean_i,
                    median_surprisal_bits=median_i,
                    mean_target_probability=mean_p,
                    accuracy=accuracy,
                )
            )
    return rows


def paired_metrics(rows: Sequence[TaskRow], ecology: str) -> dict:
    relevant = [row for row in rows if row.ecology == ecology]
    by_key: Dict[Tuple[int, int], Dict[str, TaskRow]] = {}
    for row in relevant:
        by_key.setdefault((row.replicate_seed, row.target_seed), {})[row.arm] = row

    required = {
        "MATCHED_HISTORY_NEURAL",
        "CROSS_HISTORY_NEURAL",
        "RESET_NEURAL",
        "RAW_LINEAR_PARENT",
        "ORACLE_REPRESENTATION",
    }
    matched_gains = []
    cross_gains = []
    paired_rows = []
    for key in sorted(by_key):
        arms = by_key[key]
        if set(arms) != required:
            raise ValueError(f"incomplete arm set for {ecology} {key}: {sorted(arms)}")
        reset = arms["RESET_NEURAL"].mean_surprisal_bits
        matched = arms["MATCHED_HISTORY_NEURAL"].mean_surprisal_bits
        cross = arms["CROSS_HISTORY_NEURAL"].mean_surprisal_bits
        matched_gain = reset - matched
        cross_gain = reset - cross
        matched_gains.append(matched_gain)
        cross_gains.append(cross_gain)
        paired_rows.append(
            {
                "replicate_seed": key[0],
                "target_seed": key[1],
                "matched_gain_bits": matched_gain,
                "cross_gain_bits": cross_gain,
            }
        )

    arm_summary = {}
    for arm in sorted(required):
        arm_rows = [row for row in relevant if row.arm == arm]
        arm_summary[arm] = {
            "n": len(arm_rows),
            "mean_task_mean_surprisal_bits": mean(row.mean_surprisal_bits for row in arm_rows),
            "median_task_mean_surprisal_bits": median(row.mean_surprisal_bits for row in arm_rows),
            "mean_accuracy": mean(row.accuracy for row in arm_rows),
            "mean_target_probability": mean(row.mean_target_probability for row in arm_rows),
        }

    positive_count = sum(gain > 0 for gain in matched_gains)
    median_matched = median(matched_gains)
    median_cross = median(cross_gains)
    specificity_gap = median_matched - median_cross
    oracle_headroom = (
        arm_summary["ORACLE_REPRESENTATION"]["mean_task_mean_surprisal_bits"]
        < arm_summary["MATCHED_HISTORY_NEURAL"]["mean_task_mean_surprisal_bits"]
    )

    predictions = {
        "P1_positive_rows": positive_count >= MIN_POSITIVE_ROWS,
        "P1_median_gain": median_matched >= MIN_MEDIAN_MATCHED_GAIN_BITS,
        "P2_specificity_gap": specificity_gap >= MIN_MEDIAN_SPECIFICITY_GAP_BITS,
        "P3_cross_gain_ceiling": median_cross <= MAX_MEDIAN_CROSS_GAIN_BITS,
        "P4_oracle_headroom": oracle_headroom,
    }

    return {
        "paired_rows": paired_rows,
        "positive_matched_rows": positive_count,
        "paired_row_count": len(matched_gains),
        "median_matched_gain_bits": median_matched,
        "median_cross_gain_bits": median_cross,
        "median_specificity_gap_bits": specificity_gap,
        "arm_summary": arm_summary,
        "predictions": predictions,
    }


def parameter_counts() -> dict:
    trunk = NeuralTrunk()
    neural_head = nn.Linear(K, 1)
    raw_head = nn.Linear(D, 1)
    return {
        "neural_trunk": sum(p.numel() for p in trunk.parameters()),
        "neural_target_head": sum(p.numel() for p in neural_head.parameters()),
        "raw_linear_target_head": sum(p.numel() for p in raw_head.parameters()),
        "development_task_heads_total": len(DEV_TASK_SEEDS)
        * sum(p.numel() for p in neural_head.parameters()),
    }


def registered_config() -> dict:
    return {
        "d": D,
        "k": K,
        "latent_matrix_seeds": {"A1": A1_SEED, "A2": A2_SEED},
        "development_task_seeds": DEV_TASK_SEEDS,
        "development_examples_per_task": DEV_EXAMPLES_PER_TASK,
        "pretrain_steps": PRETRAIN_STEPS,
        "pretrain_batch": PRETRAIN_BATCH,
        "pretrain_lr": PRETRAIN_LR,
        "replicate_seeds": REPLICATE_SEEDS,
        "target_task_seeds": {"A1": A1_TARGET_SEEDS, "A2": A2_TARGET_SEEDS},
        "support": SUPPORT,
        "query": QUERY,
        "head_steps": HEAD_STEPS,
        "head_lr": HEAD_LR,
        "head_weight_decay": HEAD_WEIGHT_DECAY,
        "acceptance": {
            "min_positive_rows_each_ecology": MIN_POSITIVE_ROWS,
            "min_median_matched_gain_bits": MIN_MEDIAN_MATCHED_GAIN_BITS,
            "min_median_specificity_gap_bits": MIN_MEDIAN_SPECIFICITY_GAP_BITS,
            "max_median_cross_gain_bits": MAX_MEDIAN_CROSS_GAIN_BITS,
            "oracle_headroom_required": True,
        },
    }


def execute() -> dict:
    frozen_runtime()
    started = time.perf_counter()
    latent_a1 = make_latent_matrix(A1_SEED)
    latent_a2 = make_latent_matrix(A2_SEED)
    rows: list[TaskRow] = []

    for replicate_seed in REPLICATE_SEEDS:
        # Same initial trunk/head RNG state, different developmental latent family.
        trunk_a1 = pretrain_trunk(latent_a1, init_seed=replicate_seed)
        trunk_a2 = pretrain_trunk(latent_a2, init_seed=replicate_seed)
        reset_a1 = random_trunk(replicate_seed)
        reset_a2 = random_trunk(replicate_seed)

        rows.extend(
            evaluate_ecology(
                ecology="A1",
                latent_target=latent_a1,
                target_seeds=A1_TARGET_SEEDS,
                matched_trunk=trunk_a1,
                cross_trunk=trunk_a2,
                reset_trunk=reset_a1,
                replicate_seed=replicate_seed,
            )
        )
        rows.extend(
            evaluate_ecology(
                ecology="A2",
                latent_target=latent_a2,
                target_seeds=A2_TARGET_SEEDS,
                matched_trunk=trunk_a2,
                cross_trunk=trunk_a1,
                reset_trunk=reset_a2,
                replicate_seed=replicate_seed,
            )
        )

    result_a1 = paired_metrics(rows, "A1")
    result_a2 = paired_metrics(rows, "A2")
    all_predictions = {
        f"{ecology}.{key}": value
        for ecology, result in (("A1", result_a1), ("A2", result_a2))
        for key, value in result["predictions"].items()
    }

    p1_hold = all(
        result["predictions"]["P1_positive_rows"]
        and result["predictions"]["P1_median_gain"]
        for result in (result_a1, result_a2)
    )
    p23_hold = all(
        result["predictions"]["P2_specificity_gap"]
        and result["predictions"]["P3_cross_gain_ceiling"]
        for result in (result_a1, result_a2)
    )
    p4_hold = all(
        result["predictions"]["P4_oracle_headroom"]
        for result in (result_a1, result_a2)
    )

    if p1_hold and p23_hold and p4_hold:
        terminal = "NEURAL_K1_SEMANTIC_PROPOSAL_GEOMETRY_SUPPORTED_AT_REGISTERED_SYNTHETIC_SCOPE"
    elif not p1_hold:
        terminal = "NEURAL_K1_NOT_ESTABLISHED_AT_REGISTERED_SCOPE"
    elif not p23_hold:
        terminal = "HISTORY_SPECIFICITY_NOT_ESTABLISHED"
    else:
        terminal = "ORACLE_HEADROOM_ASSAY_DEFECT"

    elapsed = time.perf_counter() - started
    return {
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "registered_config": registered_config(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "device": "cpu",
            "torch_num_threads": torch.get_num_threads(),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
        "resource_receipt": {
            "wall_seconds_observed": elapsed,
            "pretrain_gradient_steps_per_history_trunk": PRETRAIN_STEPS,
            "history_trunks_trained": len(REPLICATE_SEEDS) * 2,
            "target_head_gradient_steps_per_arm_task": HEAD_STEPS,
            "target_task_arm_evaluations": len(rows),
            "parameter_counts": parameter_counts(),
        },
        "results": {"A1": result_a1, "A2": result_a2},
        "prediction_results": all_predictions,
        "terminal": terminal,
        "capital_level": "K1" if terminal.startswith("NEURAL_K1_SEMANTIC_PROPOSAL_GEOMETRY_SUPPORTED") else "NOT_ESTABLISHED",
        "k2_status": "NOT_TESTED",
        "claim_ceiling": (
            "Controlled synthetic neural representation-learning SPG/K1 result only. Parent-owned transfer/representation "
            "learning; no K2, modern deep-network generality, resource dominance, or universal cross-paradigm law."
        ),
        "rows": [asdict(row) for row in rows],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("refusing to overwrite existing receipt")
    receipt = execute()
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "terminal": receipt["terminal"],
        "A1": {
            "positive": receipt["results"]["A1"]["positive_matched_rows"],
            "median_gain": receipt["results"]["A1"]["median_matched_gain_bits"],
            "median_cross": receipt["results"]["A1"]["median_cross_gain_bits"],
        },
        "A2": {
            "positive": receipt["results"]["A2"]["positive_matched_rows"],
            "median_gain": receipt["results"]["A2"]["median_matched_gain_bits"],
            "median_cross": receipt["results"]["A2"]["median_cross_gain_bits"],
        },
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
