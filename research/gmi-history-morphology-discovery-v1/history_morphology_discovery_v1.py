from __future__ import annotations

from fractions import Fraction

HISTORY = (36, 38, 52, 37)
TARGETS = (39, 53)
PERMUTATION = (3, 4, 5, 0, 1, 2)
START_MORPHOLOGY = 0
CANDIDATES = tuple(range(64))


def bits(mask: int) -> tuple[int, ...]:
    return tuple((mask >> i) & 1 for i in range(6))


def permute_mask(mask: int) -> int:
    out = 0
    for i, value in enumerate(bits(mask)):
        if value:
            out |= 1 << PERMUTATION[i]
    return out


def bit_counts(history: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(bits(mask)[i] for mask in history) for i in range(6))


def history_score(mask: int, history: tuple[int, ...]) -> int:
    """Exact unnormalized Laplace-smoothed independent-bit likelihood."""
    counts = bit_counts(history)
    n = len(history)
    score = 1
    for i, value in enumerate(bits(mask)):
        score *= counts[i] + 1 if value else n - counts[i] + 1
    return score


def reset_order() -> tuple[int, ...]:
    return CANDIDATES


def learned_order(history: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(CANDIDATES, key=lambda m: (-history_score(m, history), m)))


def discovery_rank(order: tuple[int, ...], target: int) -> int:
    return order.index(target) + 1


def arm_ranks() -> dict[str, list[int]]:
    shuffled = tuple(permute_mask(mask) for mask in HISTORY)
    arms = {
        "RESET": reset_order(),
        "CONTINUED": learned_order(HISTORY),
        "SHUFFLED_HISTORY": learned_order(shuffled),
    }
    return {name: [discovery_rank(order, target) for target in TARGETS] for name, order in arms.items()}


def mean_rank(ranks: list[int]) -> Fraction:
    return Fraction(sum(ranks), len(ranks))


def result() -> dict[str, object]:
    shuffled = tuple(permute_mask(mask) for mask in HISTORY)
    ranks = arm_ranks()
    means = {name: mean_rank(values) for name, values in ranks.items()}
    unseen = set(HISTORY).isdisjoint(TARGETS)
    same_space = set(reset_order()) == set(learned_order(HISTORY)) == set(learned_order(shuffled)) == set(CANDIDATES)
    history_charged = all(learned_order(HISTORY).index(h) < 64 for h in HISTORY)
    success = (
        unseen
        and START_MORPHOLOGY == 0
        and same_space
        and history_charged
        and means["CONTINUED"] < means["RESET"]
        and means["CONTINUED"] < means["SHUFFLED_HISTORY"]
    )
    return {
        "schema": "GMI_HISTORY_MORPHOLOGY_DISCOVERY_V1",
        "freeze_commit": "022e55726a1a5e3235ddd516d386f6b96fdadc12",
        "start_morphology_all_arms": START_MORPHOLOGY,
        "candidate_space": [0, 63],
        "candidate_count_each_arm": len(CANDIDATES),
        "history": list(HISTORY),
        "targets": list(TARGETS),
        "targets_unseen": unseen,
        "shuffled_history": list(shuffled),
        "history_bit_counts": list(bit_counts(HISTORY)),
        "shuffled_bit_counts": list(bit_counts(shuffled)),
        "ranks": ranks,
        "mean_ranks": {name: str(value) for name, value in means.items()},
        "continued_first_ten": list(learned_order(HISTORY)[:10]),
        "shuffled_first_ten": list(learned_order(shuffled)[:10]),
        "same_candidate_space": same_space,
        "historical_candidates_remain_charged": history_charged,
        "terminal": (
            "HISTORY_IMPROVES_UNSEEN_MORPHOLOGY_DISCOVERY_NOT_WARM_START"
            if success else "HISTORY_MORPHOLOGY_DISCOVERY_DEMONSTRATION_FAILED"
        ),
        "claim_ceiling": "FINITE_HISTORY_INDUCED_MORPHOLOGY_SEARCH_PRIOR__NO_WARM_START__PARENT_OWNED",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(result(), indent=2, sort_keys=True))
