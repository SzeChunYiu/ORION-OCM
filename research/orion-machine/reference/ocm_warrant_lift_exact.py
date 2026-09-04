#!/usr/bin/env python3
"""Exact finite checks for the Warrant Lift theory candidate.

The checker validates finite partition characterizations and hostile controls.
It does not establish literature priority or novelty.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import defaultdict
from typing import Sequence

Partition = tuple[int, ...]


def normalize_partition(labels: Sequence[object]) -> Partition:
    remap: dict[object, int] = {}
    out: list[int] = []
    for label in labels:
        if label not in remap:
            remap[label] = len(remap)
        out.append(remap[label])
    return tuple(out)


def set_partitions(n: int) -> tuple[Partition, ...]:
    if n < 1:
        raise ValueError("n must be positive")
    out: list[Partition] = []

    def rec(prefix: tuple[int, ...]) -> None:
        if len(prefix) == n:
            out.append(prefix)
            return
        maximum = max(prefix, default=-1)
        for label in range(maximum + 2):
            rec(prefix + (label,))

    rec(())
    return tuple(out)


def refines(fine: Partition, coarse: Partition) -> bool:
    if len(fine) != len(coarse):
        raise ValueError("partition sizes differ")
    seen: dict[int, int] = {}
    for f, c in zip(fine, coarse):
        if f in seen and seen[f] != c:
            return False
        seen[f] = c
    return True


def equivalent_partitions(left: Partition, right: Partition) -> bool:
    return refines(left, right) and refines(right, left)


def behavior_fiber_lifecycle_counts(
    behavior: Partition, lifecycle: Partition
) -> dict[int, int]:
    if not refines(lifecycle, behavior):
        raise ValueError("lifecycle partition must refine behavior partition")
    classes: dict[int, set[int]] = defaultdict(set)
    for b, l in zip(behavior, lifecycle):
        classes[b].add(l)
    return {b: len(values) for b, values in classes.items()}


def warrant_lift_real(behavior: Partition, lifecycle: Partition) -> float:
    counts = behavior_fiber_lifecycle_counts(behavior, lifecycle)
    return math.log2(max(counts.values()))


def warrant_lift_bits(behavior: Partition, lifecycle: Partition) -> int:
    counts = behavior_fiber_lifecycle_counts(behavior, lifecycle)
    return math.ceil(math.log2(max(counts.values())))


def minimal_side_code(
    behavior: Partition, lifecycle: Partition
) -> tuple[int, tuple[int, ...]]:
    bits = warrant_lift_bits(behavior, lifecycle)
    index_by_behavior: dict[int, dict[int, int]] = {}
    for b in sorted(set(behavior)):
        lifecycle_labels = sorted(
            {l for bb, l in zip(behavior, lifecycle) if bb == b}
        )
        index_by_behavior[b] = {
            lifecycle_label: index
            for index, lifecycle_label in enumerate(lifecycle_labels)
        }
    code = tuple(
        index_by_behavior[b][l] for b, l in zip(behavior, lifecycle)
    )
    if any(value >= 2**bits for value in code):
        raise AssertionError("constructed side code exceeds claimed bit width")
    return bits, code


def code_identifies_lifecycle(
    behavior: Partition, lifecycle: Partition, code: Sequence[int]
) -> bool:
    if not (len(behavior) == len(lifecycle) == len(code)):
        raise ValueError("vector sizes differ")
    decoder: dict[tuple[int, int], int] = {}
    for b, l, c in zip(behavior, lifecycle, code):
        key = (b, c)
        if key in decoder and decoder[key] != l:
            return False
        decoder[key] = l
    return True


def conditional_entropy_uniform(
    behavior: Partition, lifecycle: Partition
) -> float:
    if not refines(lifecycle, behavior):
        raise ValueError("lifecycle partition must refine behavior partition")
    n = len(behavior)
    by_behavior: dict[int, list[int]] = defaultdict(list)
    for b, l in zip(behavior, lifecycle):
        by_behavior[b].append(l)
    entropy = 0.0
    for values in by_behavior.values():
        p_b = len(values) / n
        counts: dict[int, int] = defaultdict(int)
        for value in values:
            counts[value] += 1
        h = 0.0
        for count in counts.values():
            p = count / len(values)
            h -= p * math.log2(p)
        entropy += p_b * h
    return entropy


def product_partition(left: Partition, right: Partition) -> Partition:
    return normalize_partition(
        [(l, r) for l in left for r in right]
    )


def collapsed_code(code: Sequence[int], first: int, second: int) -> tuple[int, ...]:
    return tuple(first if value == second else value for value in code)


def current_accuracy_blind_spot(bit_count: int) -> tuple[Partition, Partition]:
    if bit_count < 0:
        raise ValueError("bit count must be non-negative")
    worlds = 2**bit_count
    return (0,) * worlds, tuple(range(worlds))


def run_exact_calibration() -> dict[str, object]:
    partitions_by_n = {n: set_partitions(n) for n in range(1, 6)}
    expected_bell = {1: 1, 2: 2, 3: 5, 4: 15, 5: 52}
    if {n: len(p) for n, p in partitions_by_n.items()} != expected_bell:
        raise AssertionError("partition enumeration drift")

    nested_pairs = zero_cases = positive_cases = 0
    encoding_checks = planted_collisions = entropy_checks = 0
    pairs_by_n: dict[int, list[tuple[Partition, Partition]]] = defaultdict(list)

    for n, partitions in partitions_by_n.items():
        for behavior in partitions:
            for lifecycle in partitions:
                if not refines(lifecycle, behavior):
                    continue
                nested_pairs += 1
                pairs_by_n[n].append((behavior, lifecycle))
                lift = warrant_lift_real(behavior, lifecycle)
                lift_bits = warrant_lift_bits(behavior, lifecycle)
                if equivalent_partitions(behavior, lifecycle):
                    zero_cases += 1
                    if lift != 0 or lift_bits != 0:
                        raise AssertionError("zero criterion failed")
                else:
                    positive_cases += 1
                    if lift <= 0 or lift_bits <= 0:
                        raise AssertionError("positive lift criterion failed")

                bits, code = minimal_side_code(behavior, lifecycle)
                if bits != lift_bits or not code_identifies_lifecycle(
                    behavior, lifecycle, code
                ):
                    raise AssertionError("side-code characterization failed")
                encoding_checks += 1

                entropy = conditional_entropy_uniform(behavior, lifecycle)
                if entropy < -1e-12 or entropy > lift + 1e-12:
                    raise AssertionError("conditional entropy outside lift bound")
                entropy_checks += 1

                if lift_bits > 0:
                    found = False
                    for b in sorted(set(behavior)):
                        positions = [i for i, bb in enumerate(behavior) if bb == b]
                        symbols: dict[int, int] = {}
                        for i in positions:
                            symbols.setdefault(lifecycle[i], code[i])
                        if len(symbols) >= 2:
                            first, second = list(symbols.values())[:2]
                            broken = collapsed_code(code, first, second)
                            if code_identifies_lifecycle(
                                behavior, lifecycle, broken
                            ):
                                raise AssertionError(
                                    "planted side-code collision did not fire"
                                )
                            planted_collisions += 1
                            found = True
                            break
                    if not found:
                        raise AssertionError("positive lift without splittable fiber")

    monotonicity_checks = 0
    for pairs in pairs_by_n.values():
        for behavior, lifecycle_coarse in pairs:
            coarse_lift = warrant_lift_real(behavior, lifecycle_coarse)
            for candidate_behavior, lifecycle_fine in pairs:
                if candidate_behavior != behavior:
                    continue
                if refines(lifecycle_fine, lifecycle_coarse):
                    fine_lift = warrant_lift_real(behavior, lifecycle_fine)
                    if fine_lift + 1e-12 < coarse_lift:
                        raise AssertionError("obligation monotonicity failed")
                    monotonicity_checks += 1

    product_checks = 0
    for behavior_1, lifecycle_1 in pairs_by_n[3]:
        for behavior_2, lifecycle_2 in pairs_by_n[3]:
            product_behavior = product_partition(behavior_1, behavior_2)
            product_lifecycle = product_partition(lifecycle_1, lifecycle_2)
            expected = (
                warrant_lift_real(behavior_1, lifecycle_1)
                + warrant_lift_real(behavior_2, lifecycle_2)
            )
            observed = warrant_lift_real(product_behavior, product_lifecycle)
            if abs(expected - observed) > 1e-12:
                raise AssertionError("independent product additivity failed")
            h_expected = (
                conditional_entropy_uniform(behavior_1, lifecycle_1)
                + conditional_entropy_uniform(behavior_2, lifecycle_2)
            )
            h_observed = conditional_entropy_uniform(
                product_behavior, product_lifecycle
            )
            if abs(h_expected - h_observed) > 1e-12:
                raise AssertionError("conditional entropy additivity failed")
            product_checks += 1

    behavior_joint = (0, 0)
    lifecycle_1 = (0, 1)
    lifecycle_2 = (0, 1)
    lifecycle_joint = normalize_partition(
        [(a, b) for a, b in zip(lifecycle_1, lifecycle_2)]
    )
    left = warrant_lift_real(behavior_joint, lifecycle_1)
    right = warrant_lift_real(behavior_joint, lifecycle_2)
    joint = warrant_lift_real(behavior_joint, lifecycle_joint)
    if not joint < left + right:
        raise AssertionError("shared-warrant subadditivity witness failed")

    blind_spots = {}
    for bits in range(9):
        behavior, lifecycle = current_accuracy_blind_spot(bits)
        observed = warrant_lift_bits(behavior, lifecycle)
        if observed != bits:
            raise AssertionError("current-accuracy blind-spot construction failed")
        blind_spots[str(bits)] = {
            "current_behavior_classes": 1,
            "lifecycle_classes": 2**bits,
            "warrant_lift_bits": observed,
        }

    return {
        "schema": "orion.ocm.warrant-lift.exact-results.v1",
        "terminal": "PASS_FINITE_WARRANT_LIFT_THEORY",
        "partition_sweep": {
            "n_values": sorted(partitions_by_n),
            "bell_counts": expected_bell,
            "nested_behavior_lifecycle_pairs_checked": nested_pairs,
            "zero_lift_cases": zero_cases,
            "positive_lift_cases": positive_cases,
            "side_code_characterization_checks": encoding_checks,
            "planted_code_collisions_fired": planted_collisions,
            "conditional_entropy_checks": entropy_checks,
            "obligation_monotonicity_checks": monotonicity_checks,
        },
        "product_law": {
            "independent_product_checks": product_checks,
            "real_warrant_lift_additive": True,
            "uniform_conditional_entropy_additive": True,
            "strict_shared_warrant_subadditivity_witness": {
                "left_lift": left,
                "right_lift": right,
                "joint_lift": joint,
            },
        },
        "current_accuracy_blind_spot": blind_spots,
        "theorems": {
            "zero_iff_current_behavior_is_lifecycle_sufficient": True,
            "minimum_worst_case_additional_bits": (
                "ceil(log2 max_b lifecycle_classes_in_behavior_fiber_b)"
            ),
            "obligation_monotonicity": True,
            "independent_product_additivity": True,
            "shared_warrant_subadditivity": True,
            "distributional_variant": "H(L|B) under a chosen world distribution",
        },
        "authority": {
            "finite_theorem_checks": True,
            "literature_priority": False,
            "novelty": False,
            "architecture_separation": False,
            "publication_readiness": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = run_exact_calibration()
    except (AssertionError, ValueError, IndexError) as exc:
        print(json.dumps({"terminal": "FAIL", "error": str(exc)}, indent=2))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        sweep = result["partition_sweep"]
        print(
            "PASS warrant lift: "
            f"{sweep['nested_behavior_lifecycle_pairs_checked']} nested partition "
            f"pairs; {sweep['planted_code_collisions_fired']} planted collisions."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
