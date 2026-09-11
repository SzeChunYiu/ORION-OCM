"""Exact finite certificate for the GMI semantic quotient / realization theorem.

The fixture has four implementation states:

u0, u1  duplicate teachable-unlearned states
s       stubborn-unlearned state
l       learned state

Immediate outputs of u0/u1/s are intentionally similar; a future teach/query
continuation separates the teachable and stubborn cases.  The script computes
the exact deterministic Moore-style quotient by partition refinement and then
exhaustively enumerates every set partition of the four implementation states.

This is theorem-semantics calibration only.  It does not establish a universal
machine-intelligence atom or architecture.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, Iterable, Iterator, Mapping, Sequence, Tuple


State = str
Symbol = str
Block = Tuple[State, ...]
Partition = Tuple[Block, ...]

STATES: Tuple[State, ...] = ("u0", "u1", "s", "l")
SYMBOLS: Tuple[Symbol, ...] = ("query", "teach")

# Mealy-style output per (state, symbol).  teach itself returns no learned answer;
# the distinction is visible on the future query after the update.
OUTPUT: Dict[Tuple[State, Symbol], int] = {
    ("u0", "query"): 0,
    ("u0", "teach"): 0,
    ("u1", "query"): 0,
    ("u1", "teach"): 0,
    ("s", "query"): 0,
    ("s", "teach"): 0,
    ("l", "query"): 1,
    ("l", "teach"): 1,
}

TRANSITION: Dict[Tuple[State, Symbol], State] = {
    ("u0", "query"): "u0",
    ("u0", "teach"): "l",
    ("u1", "query"): "u1",
    ("u1", "teach"): "l",
    ("s", "query"): "s",
    ("s", "teach"): "s",
    ("l", "query"): "l",
    ("l", "teach"): "l",
}


@dataclass(frozen=True)
class QuotientReceipt:
    quotient: Partition
    partition_count: int
    exact_encoding_count: int
    minimum_exact_encoded_states: int
    minimum_exact_partitions: Tuple[Partition, ...]
    invalid_coarse_example: Partition
    distinguishing_word_for_teachable_vs_stubborn: Tuple[Symbol, ...]


def canonical_partition(blocks: Iterable[Iterable[State]]) -> Partition:
    normalized = [tuple(sorted(block, key=STATES.index)) for block in blocks]
    return tuple(sorted(normalized, key=lambda b: STATES.index(b[0])))


def block_index(partition: Partition) -> Dict[State, int]:
    out: Dict[State, int] = {}
    for i, block in enumerate(partition):
        for state in block:
            if state in out:
                raise ValueError(f"state appears twice: {state}")
            out[state] = i
    if set(out) != set(STATES):
        raise ValueError("partition does not cover exact fixture state set")
    return out


def refine(partition: Partition) -> Partition:
    """One exact partition-refinement step for future trace equivalence."""

    index = block_index(partition)
    new_blocks = []
    for block in partition:
        groups: Dict[Tuple[Tuple[int, int], ...], list[State]] = {}
        for state in block:
            signature = tuple(
                (OUTPUT[(state, symbol)], index[TRANSITION[(state, symbol)]])
                for symbol in SYMBOLS
            )
            groups.setdefault(signature, []).append(state)
        new_blocks.extend(groups.values())
    return canonical_partition(new_blocks)


def semantic_quotient() -> Partition:
    """Compute the coarsest stable future-trace partition."""

    # Initial grouping by immediate output vector is a safe coarse seed.
    groups: Dict[Tuple[int, ...], list[State]] = {}
    for state in STATES:
        signature = tuple(OUTPUT[(state, symbol)] for symbol in SYMBOLS)
        groups.setdefault(signature, []).append(state)
    partition = canonical_partition(groups.values())
    while True:
        next_partition = refine(partition)
        if next_partition == partition:
            return partition
        partition = next_partition


def run_word(state: State, word: Sequence[Symbol]) -> Tuple[Tuple[int, ...], State]:
    outputs = []
    current = state
    for symbol in word:
        outputs.append(OUTPUT[(current, symbol)])
        current = TRANSITION[(current, symbol)]
    return tuple(outputs), current


def distinguish(state_a: State, state_b: State, max_len: int = 8) -> Tuple[Symbol, ...] | None:
    if state_a == state_b:
        return None
    for length in range(1, max_len + 1):
        for word in product(SYMBOLS, repeat=length):
            if run_word(state_a, word)[0] != run_word(state_b, word)[0]:
                return tuple(word)
    return None


def set_partitions(items: Sequence[State]) -> Iterator[Partition]:
    """Yield every set partition exactly once in canonical order."""

    if not items:
        yield ()
        return
    first = items[0]
    for rest in set_partitions(items[1:]):
        # First may form a new first block.
        yield canonical_partition(((first,),) + rest)
        # Or join any existing block.
        for i in range(len(rest)):
            blocks = [list(block) for block in rest]
            blocks[i].append(first)
            yield canonical_partition(blocks)


def exact_encoding(partition: Partition, quotient: Partition | None = None) -> bool:
    """A partition is exact iff each realization block lies inside one quotient block."""

    quotient = quotient or semantic_quotient()
    q_index = block_index(quotient)
    for block in partition:
        if len({q_index[state] for state in block}) != 1:
            return False
    return True


def factor_map(partition: Partition, quotient: Partition | None = None) -> Dict[int, int]:
    """Return phi from realization blocks to semantic quotient blocks.

    Raises when the realization aliases a required semantic distinction.
    """

    quotient = quotient or semantic_quotient()
    if not exact_encoding(partition, quotient):
        raise ValueError("realization aliases required semantic distinction")
    q_index = block_index(quotient)
    return {i: q_index[block[0]] for i, block in enumerate(partition)}


def census() -> QuotientReceipt:
    quotient = semantic_quotient()
    partitions = tuple(dict.fromkeys(set_partitions(STATES)))
    exact = tuple(p for p in partitions if exact_encoding(p, quotient))
    minimum = min(len(p) for p in exact)
    minima = tuple(p for p in exact if len(p) == minimum)

    invalid = canonical_partition((('u0', 'u1', 's'), ('l',)))
    assert not exact_encoding(invalid, quotient)

    word = distinguish("u0", "s")
    if word is None:
        raise AssertionError("fixture failed: teachable and stubborn states not distinguishable")

    return QuotientReceipt(
        quotient=quotient,
        partition_count=len(partitions),
        exact_encoding_count=len(exact),
        minimum_exact_encoded_states=minimum,
        minimum_exact_partitions=minima,
        invalid_coarse_example=invalid,
        distinguishing_word_for_teachable_vs_stubborn=word,
    )


def as_jsonable() -> dict:
    receipt = census()
    quotient = receipt.quotient
    exact_partitions = tuple(p for p in dict.fromkeys(set_partitions(STATES)) if exact_encoding(p, quotient))

    factorization_checks = []
    for partition in exact_partitions:
        phi = factor_map(partition, quotient)
        # q = phi o e at block level.
        p_index = block_index(partition)
        q_index = block_index(quotient)
        assert all(phi[p_index[state]] == q_index[state] for state in STATES)
        factorization_checks.append({
            "partition": partition,
            "phi": phi,
        })

    return {
        "schema": "GMISemanticQuotientCertificateV1",
        "states": STATES,
        "symbols": SYMBOLS,
        "canonical_semantic_quotient": receipt.quotient,
        "all_set_partitions": receipt.partition_count,
        "exact_encoding_partitions": receipt.exact_encoding_count,
        "minimum_exact_encoded_states": receipt.minimum_exact_encoded_states,
        "minimum_exact_partitions": receipt.minimum_exact_partitions,
        "all_exact_encodings_factor_through_quotient": True,
        "factorization_checks": factorization_checks,
        "invalid_coarse_example": receipt.invalid_coarse_example,
        "distinguishing_word_teachable_vs_stubborn": receipt.distinguishing_word_for_teachable_vs_stubborn,
        "terminal": "GMI_SEMANTIC_QUOTIENT_FINITE_EXACT_GREEN_V1",
        "claim_boundary": (
            "Finite deterministic semantic-state calibration. Parent-owned quotient/minimization mathematics; "
            "no unique local cognitive atom or universal architecture claim."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(as_jsonable(), indent=2, sort_keys=True))
