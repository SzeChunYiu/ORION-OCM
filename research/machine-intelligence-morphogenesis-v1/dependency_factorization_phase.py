from __future__ import annotations

from fractions import Fraction
from itertools import combinations

ITEMS = (0, 1, 2, 3)
PAIRS = tuple(combinations(ITEMS, 2))


def _partitions(items):
    if not items:
        yield ()
        return
    first = items[0]
    for rest in _partitions(items[1:]):
        yield ((first,),) + rest
        for i in range(len(rest)):
            updated = list(rest)
            updated[i] = tuple(sorted((first,) + rest[i]))
            yield tuple(sorted(updated, key=lambda block: block[0]))


def partitions():
    return tuple(sorted(set(_partitions(ITEMS)), key=lambda p: (len(p), p)))


def internal_edges(partition):
    return sum(len(block) * (len(block) - 1) // 2 for block in partition)


def cut_probability(partition, pair_probability):
    owner = {
        item: block_index
        for block_index, block in enumerate(partition)
        for item in block
    }
    return sum(
        pair_probability[pair]
        for pair in PAIRS
        if owner[pair[0]] != owner[pair[1]]
    )


def lifetime_cost(
    partition,
    pair_probability,
    horizon,
    internal_edge_build_price=Fraction(1, 2),
    cross_factor_surcharge=Fraction(2, 1),
):
    build = internal_edge_build_price * internal_edges(partition)
    per_task = 1 + cross_factor_surcharge * cut_probability(partition, pair_probability)
    return build + horizon * per_task


def structured_pair_ecology(pairing):
    # Two favored dependency edges each receive 0.45; the remaining four
    # edges each receive 0.025, for total probability 1.
    favored = {tuple(sorted(pair)) for pair in pairing}
    return {
        pair: Fraction(9, 20) if pair in favored else Fraction(1, 40)
        for pair in PAIRS
    }


def uniform_ecology():
    return {pair: Fraction(1, 6) for pair in PAIRS}


def winner_rows():
    ecologies = {
        "PAIR_01_23": structured_pair_ecology(((0, 1), (2, 3))),
        "PAIR_02_13": structured_pair_ecology(((0, 2), (1, 3))),
        "UNIFORM": uniform_ecology(),
    }
    horizons = (1, 4, 16)
    all_partitions = partitions()
    rows = []
    for ecology_name, probabilities in ecologies.items():
        for horizon in horizons:
            costs = {
                partition: lifetime_cost(partition, probabilities, horizon)
                for partition in all_partitions
            }
            best = min(costs.values())
            winners = tuple(
                partition for partition, value in costs.items() if value == best
            )
            rows.append(
                {
                    "ecology": ecology_name,
                    "horizon": horizon,
                    "best_cost": str(best),
                    "winners": [repr(winner) for winner in winners],
                }
            )
    return rows


if __name__ == "__main__":
    import json

    print(json.dumps(winner_rows(), indent=2, sort_keys=True))
