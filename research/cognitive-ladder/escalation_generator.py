"""Generate escalation worlds whose minimum sufficient level is true by construction.

The nine registered worlds in ``escalation_worlds.py`` were authored alongside
the diagnosis policy.  Scoring the policy on them is design evidence and nothing
more, so it is reported as such.  This generator exists to make a genuine
held-out draw possible: the defect type is sampled first, the world is then
instantiated to carry exactly that defect over a randomly drawn game family, and
the level therefore follows from the construction rather than from a judgement
about the finished world.

Every draw is a pure function of the seed, and the seed comes from the
pre-registration commitment, so the protected draw is reproducible by a third
party holding only the published plan.
"""

from __future__ import annotations

import random
from typing import Callable

from escalation import EscalationWorld, Level, Representation
from escalation_worlds import HEAP_SIZE, HEAP_TUPLE, TOKEN_TOTAL
from games import SubtractionGame, eventual_period

__all__ = ["draw_world", "draw_suite", "MOVE_SETS"]

#: registered subtraction families; each has a witnessed Grundy period
MOVE_SETS = (
    (1, 2), (1, 3), (1, 2, 3), (1, 2, 4), (1, 3, 4), (1, 4, 5),
    (2, 3), (2, 3, 7), (1, 2, 5), (1, 5, 6), (1, 2, 3, 4), (2, 5, 6),
)


def _xor(vs):
    acc = 0
    for v in vs:
        acc ^= v
    return acc


def _residue(period: int, residues: frozenset[int]) -> Callable[[int], bool]:
    return lambda n: (n % period) in residues


def _combiner(fn) -> Callable[[tuple[int, ...]], bool]:
    return lambda p: fn(p) == 0


def _sub_truth(moves: tuple[int, ...], limit: int) -> Callable[[int], bool]:
    table = SubtractionGame(moves).grundy_upto(limit)
    return lambda n: table[n] == 0


def _misere_nim(position) -> bool:
    if all(h <= 1 for h in position):
        return sum(1 for h in position if h == 1) % 2 == 1
    return _xor(position) == 0


def draw_world(rng: random.Random, level: Level, index: int) -> EscalationWorld:
    """Instantiate one world carrying exactly the defect named by ``level``."""
    limit = 96

    if level in (Level.L0_NO_ESCALATION, Level.L1_SEARCH_MORE, Level.L2_MORE_EVIDENCE):
        moves = rng.choice(MOVE_SETS)
        _, period = eventual_period(moves)
        truth = _sub_truth(moves, limit)
        positions = tuple(range(limit + 1))
        true_res = frozenset(r for r in range(period) if truth(r + period))
        # a decoy that agrees with the truth on one residue class and differs on another
        others = [r for r in range(period) if r not in true_res]
        if not others:
            others = [rng.randrange(period)]
        split_res = rng.choice(others)
        decoy = _residue(period, true_res | {split_res})
        hyps = (_residue(period, true_res), decoy)
        agree = [n for n in range(period, limit + 1) if n % period in true_res]
        splitters = [n for n in range(period, limit + 1) if n % period == split_res]
        observed = tuple((n, truth(n)) for n in agree[:4])

        if level is Level.L0_NO_ESCALATION:
            observed = observed + ((splitters[0], truth(splitters[0])),)
            probes, budget = tuple(agree[4:7]), 3
        elif level is Level.L1_SEARCH_MORE:
            probes, budget = (splitters[0],) + tuple(agree[4:6]), 3
        else:  # L2: the permitted channel cannot split, a position outside it can
            probes, budget = tuple(agree[4:8]), 4
        return EscalationWorld(
            world_id=f"G{index:03d}_{level.name}",
            positions=positions,
            truth=truth,
            representation=HEAP_SIZE,
            incumbent_hypotheses=hyps,
            allowed_probes=probes,
            observed=observed,
            probe_budget=budget,
            minimum_sufficient_level=level,
            notes=f"SUB{moves} period {period}",
        )

    if level is Level.L3_LOCAL_REPAIR:
        # choose a family whose true period exceeds the incumbent period bound
        candidates = [m for m in MOVE_SETS if eventual_period(m)[1] >= 5]
        moves = rng.choice(candidates)
        _, period = eventual_period(moves)
        truth = _sub_truth(moves, limit)
        bound = period - 1
        hyps = tuple(
            _residue(p, frozenset({0})) for p in range(2, bound + 1)
        ) + tuple(_residue(p, frozenset({0, 1})) for p in range(2, bound + 1))
        observed = tuple((n, truth(n)) for n in range(0, 2 * period + 2))
        return EscalationWorld(
            world_id=f"G{index:03d}_{level.name}",
            positions=tuple(range(limit + 1)),
            truth=truth,
            representation=HEAP_SIZE,
            incumbent_hypotheses=hyps,
            allowed_probes=tuple(range(2 * period + 2, 2 * period + 12)),
            observed=observed,
            probe_budget=5,
            local_repair_available=True,
            minimum_sufficient_level=level,
            notes=f"SUB{moves} true period {period}, incumbent bound {bound}",
        )

    if level is Level.L4_OPERATOR_INSUFFICIENT:
        heaps = rng.choice((2, 3))
        top = rng.choice((5, 6, 7))
        positions = tuple(
            tuple(rng.randrange(top) for _ in range(heaps)) for _ in range(60)
        )
        positions = tuple(dict.fromkeys(positions))
        truth = lambda p: _xor(p) == 0
        incumbent = (
            _combiner(lambda vs: sum(vs) % 3),
            _combiner(lambda vs: max(vs)),
            _combiner(lambda vs: min(vs)),
            _combiner(lambda vs: sum(vs)),
        )
        widened = incumbent + (_combiner(_xor),)
        # evidence that refutes every incumbent while XOR survives
        observed = tuple((p, truth(p)) for p in positions[:10])
        return EscalationWorld(
            world_id=f"G{index:03d}_{level.name}",
            positions=positions,
            truth=truth,
            representation=HEAP_TUPLE,
            incumbent_hypotheses=incumbent,
            widened_hypotheses=widened,
            allowed_probes=positions,
            observed=observed,
            probe_budget=8,
            minimum_sufficient_level=level,
            notes=f"{heaps}-heap Nim, XOR absent from the incumbent vocabulary",
        )

    if level is Level.L5_REPRESENTATION_CHANGE:
        heaps = 2
        top = rng.choice((5, 6, 7))
        positions = tuple((a, b) for a in range(top) for b in range(top))
        truth = lambda p: _xor(p) == 0
        # find an exhibited colliding pair under the token-total representation
        pair = None
        for p in positions:
            for q in positions:
                if p != q and sum(p) == sum(q) and truth(p) != truth(q):
                    pair = (p, q)
                    break
            if pair:
                break
        assert pair is not None, "token-total must collide on some Nim board"
        hyps = tuple(
            (lambda t: (lambda p: sum(p) % t == 0))(t) for t in range(2, 2 * top)
        )
        return EscalationWorld(
            world_id=f"G{index:03d}_{level.name}",
            positions=positions,
            truth=truth,
            representation=TOKEN_TOTAL,
            incumbent_hypotheses=hyps,
            widened_hypotheses=hyps,
            refined_hypotheses=(_combiner(_xor),),
            allowed_probes=positions,
            observed=((pair[0], truth(pair[0])), (pair[1], truth(pair[1]))),
            probe_budget=8,
            minimum_sufficient_level=level,
            notes=f"token-total collides at {pair}",
        )

    if level is Level.L6_FORMULATION_CHANGE:
        heaps = rng.choice((2, 3))
        top = 4
        positions = tuple(
            tuple(a) for a in _tuples(heaps, top)
        )
        truth = _misere_nim
        normal = (
            _combiner(_xor),
            _combiner(lambda vs: sum(vs) % 2),
            _combiner(lambda vs: max(vs)),
        )
        small = [p for p in positions if all(h <= 1 for h in p)]
        big = [p for p in positions if any(h > 1 for h in p)]
        observed = tuple((p, truth(p)) for p in small[:4] + big[:2])
        return EscalationWorld(
            world_id=f"G{index:03d}_{level.name}",
            positions=positions,
            truth=truth,
            representation=HEAP_TUPLE,
            incumbent_hypotheses=normal,
            widened_hypotheses=normal,
            allowed_probes=positions,
            observed=observed,
            probe_budget=8,
            formulation_defect=True,
            minimum_sufficient_level=level,
            notes=f"misere {heaps}-heap Nim read as normal play",
        )

    raise ValueError(f"no generator registered for {level}")


def _tuples(k: int, top: int):
    if k == 0:
        yield ()
        return
    for rest in _tuples(k - 1, top):
        for v in range(top):
            yield rest + (v,)


LEVELS = (
    Level.L0_NO_ESCALATION,
    Level.L1_SEARCH_MORE,
    Level.L2_MORE_EVIDENCE,
    Level.L3_LOCAL_REPAIR,
    Level.L4_OPERATOR_INSUFFICIENT,
    Level.L5_REPRESENTATION_CHANGE,
    Level.L6_FORMULATION_CHANGE,
)


def draw_suite(seed: str, per_level: int) -> tuple[EscalationWorld, ...]:
    """Draw a balanced suite of ``per_level`` worlds for each registered level."""
    rng = random.Random(int(seed, 16) % (2**63))
    out = []
    i = 0
    for level in LEVELS:
        for _ in range(per_level):
            out.append(draw_world(rng, level, i))
            i += 1
    return tuple(out)
