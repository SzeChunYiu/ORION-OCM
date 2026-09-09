"""Exact finite game families for the cognitive ladder (CL-1 .. CL-3).

Every family here is *completely* solvable: the full state space, the optimal
policy, the terminal conditions and an exact checker are all available.  That is
the point.  These games are a microscope, not a benchmark; nothing about a
result here transfers to an interesting domain by itself.

Three families, chosen so that composition is real rather than staged:

``SUB(S)``      one heap, move set ``S``.  Grundy values are eventually periodic
                (Sprague--Grundy).  The learnable object is the periodic rule.

``NIM(k)``      ``k`` heaps, any positive number may be taken.  Per-heap Grundy
                value is the heap size, so the only learnable object is the
                *combiner* (XOR).

``SUBNIM(S,k)`` ``k`` heaps, each with move set ``S``.  Solving it requires the
                per-heap rule from ``SUB(S)`` **and** the combiner from
                ``NIM(k)``.  Neither family alone contains the combined
                solution, which is what makes it an honest CL-2 composition
                probe.

Normal play throughout: a player unable to move loses.  ``P`` denotes a
previous-player win, i.e. a loss for the player to move.

Parents: Sprague--Grundy theory; Bouton's analysis of Nim.  No novelty claimed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Iterable, Sequence

__all__ = [
    "Work",
    "SubtractionGame",
    "MultiHeapGame",
    "grundy_sequence",
    "eventual_period",
]


@dataclass
class Work:
    """Exact work counter.

    Only quantities the machine actually spends are counted here.  There is no
    wall-clock term: wall time belongs in the resource vector, where it is
    reported cold and warm separately.  ``expansions`` is the primitive unit of
    search work and is what the primary efficiency estimand is computed over.
    """

    expansions: int = 0
    move_evaluations: int = 0
    predicate_evaluations: int = 0
    table_reads: int = 0
    table_writes: int = 0

    def add(self, other: "Work") -> "Work":
        return Work(
            expansions=self.expansions + other.expansions,
            move_evaluations=self.move_evaluations + other.move_evaluations,
            predicate_evaluations=self.predicate_evaluations + other.predicate_evaluations,
            table_reads=self.table_reads + other.table_reads,
            table_writes=self.table_writes + other.table_writes,
        )

    def as_dict(self) -> dict:
        return {
            "expansions": self.expansions,
            "move_evaluations": self.move_evaluations,
            "predicate_evaluations": self.predicate_evaluations,
            "table_reads": self.table_reads,
            "table_writes": self.table_writes,
        }

    @property
    def total(self) -> int:
        """Single scalar used only for budget enforcement, never for a claim."""
        return (
            self.expansions
            + self.move_evaluations
            + self.predicate_evaluations
            + self.table_reads
            + self.table_writes
        )


@dataclass(frozen=True)
class SubtractionGame:
    """One-heap subtraction game with move set ``moves``.

    ``moves`` is a sorted tuple of positive integers.  From a heap of ``n`` a
    player may move to ``n - s`` for any ``s`` in ``moves`` with ``s <= n``.
    """

    moves: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.moves:
            raise ValueError("subtraction game needs at least one legal move")
        if any(s <= 0 for s in self.moves):
            raise ValueError("moves must be positive")
        if tuple(sorted(set(self.moves))) != self.moves:
            raise ValueError("moves must be sorted and distinct")

    @property
    def family_id(self) -> str:
        return "SUB(" + ",".join(str(s) for s in self.moves) + ")"

    def successors(self, n: int) -> list[int]:
        return [n - s for s in self.moves if s <= n]

    def grundy_upto(self, limit: int, work: Work | None = None) -> list[int]:
        """Exact Grundy values for ``0..limit`` by dynamic programming.

        This is the ``P0`` parent's own procedure and the oracle used to build
        the checker.  It is never handed to the machine as a policy.
        """
        work = work if work is not None else Work()
        table: list[int] = []
        for n in range(limit + 1):
            work.expansions += 1
            seen = set()
            for s in self.moves:
                if s <= n:
                    work.move_evaluations += 1
                    work.table_reads += 1
                    seen.add(table[n - s])
            g = 0
            while g in seen:
                g += 1
            table.append(g)
            work.table_writes += 1
        return table

    def is_p_position(self, n: int, work: Work | None = None) -> bool:
        """``True`` when ``n`` is a loss for the player to move."""
        return self.grundy_upto(n, work=work)[n] == 0


@dataclass(frozen=True)
class MultiHeapGame:
    """``k`` independent heaps, each played as ``per_heap``.

    ``NIM(k)`` is the special case ``per_heap = SubtractionGame(1..max_heap)``;
    because that lets a player take any amount, its Grundy value is the heap
    size itself.  ``NIM`` is constructed via :meth:`nim` so the move set is
    always wide enough for the heap sizes actually drawn.
    """

    per_heap: SubtractionGame
    heaps: int

    def __post_init__(self) -> None:
        if self.heaps < 1:
            raise ValueError("need at least one heap")

    @classmethod
    def nim(cls, heaps: int, max_heap: int) -> "MultiHeapGame":
        return cls(SubtractionGame(tuple(range(1, max_heap + 1))), heaps)

    @property
    def family_id(self) -> str:
        return f"MULTI[{self.heaps}]{self.per_heap.family_id}"

    def is_p_position(self, position: Sequence[int], work: Work | None = None) -> bool:
        """Exact verdict via Sprague--Grundy.

        Used as the oracle.  The machine does not receive this routine; whether
        it can *acquire* the decomposition-plus-XOR structure from evidence is
        the experimental question, and the bits it needed to do so are counted
        by the bits-of-prior accounting.
        """
        work = work if work is not None else Work()
        if len(position) != self.heaps:
            raise ValueError("position arity does not match the family")
        acc = 0
        table = self.per_heap.grundy_upto(max(position) if position else 0, work=work)
        for h in position:
            work.table_reads += 1
            acc ^= table[h]
        return acc == 0

    def joint_state_count(self, max_heap: int) -> int:
        """Size of the joint state space.

        Reported so that the cost of the position-cache parent is visible: it
        grows as ``(max_heap+1) ** heaps`` while a decomposing method's state is
        constant in ``heaps``.  That contrast is the actual quantitative claim
        at CL-2, and it is a fact about the games, not about OCM.
        """
        return (max_heap + 1) ** self.heaps


def grundy_sequence(game: SubtractionGame, limit: int) -> tuple[int, ...]:
    return tuple(game.grundy_upto(limit))


@lru_cache(maxsize=None)
def eventual_period(moves: tuple[int, ...], search_limit: int = 600) -> tuple[int, int]:
    """Return the least ``(preperiod, period)`` of the Grundy sequence of ``SUB(moves)``.

    Every finite subtraction game has an eventually periodic Grundy sequence.
    The period is **not** bounded by ``max(moves)``: ``SUB(1,3,4)`` has period 7.
    We therefore search up to ``search_limit // 3`` and require the candidate to
    hold over the whole witnessed tail, then assert rather than assume.  A family
    whose period is not witnessed here is rejected from the registered draw; it
    is never silently accepted.
    """
    game = SubtractionGame(moves)
    seq = game.grundy_upto(search_limit)
    for preperiod in range(0, search_limit // 3):
        tail = seq[preperiod:]
        for period in range(1, len(tail) // 3 + 1):
            if all(tail[i] == tail[i % period] for i in range(len(tail))):
                return preperiod, period
    raise AssertionError(
        f"no eventual period witnessed for {moves} within {search_limit}; "
        "raise search_limit or reject the family from the draw"
    )
