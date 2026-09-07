"""E4: escalation levels from blind perturbation and a policy-independent oracle.

Why this module exists
----------------------
``escalation_generator.py`` picks a defect type first and then instantiates
exactly that defect, so the world's ground-truth level is the *generator's
intent* and the generator shares the diagnosis policy's taxonomy.  That is the
ORION failure-ledger pattern ``STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE``, and
it caps the escalation pilot at evidence class E2 however many worlds are added.
The pilot's own receipt says so.  This module removes exactly that circularity
and nothing else.

The fix has two halves.

**Blind perturbation.**  A world starts from a *fully working* setup: a real
SUBNIM family, the whole registered rule catalogue, the whole registered
operator vocabulary, the identifying representation, the full probe set, a
budget equal to the probe set, the correct play convention, and a sample of
honest evidence.  Zero, one or two perturbations are then drawn independently
and uniformly from a fixed menu.  Nothing anywhere records which escalation
level a perturbation is "supposed" to correspond to, because nothing computes
it: a perturbation is a syntactic edit to the configuration, not a defect
type.

**Ground truth by exhaustive repair search.**  :func:`minimum_sufficient_level`
enumerates the registered repair lattice in increasing cost order and returns
the lowest level at which some repair makes the task identifiable.  It knows
only whether a repair *works*, never why, and it never reads the perturbation
record.  It is used by the scorer alone.

That decoupling is the whole point and it is load-bearing: with two
simultaneous perturbations the true minimum level is routinely **lower** than
either perturbation would "intend" (the evidence already pinned the answer, so
a restricted probe set and a spent budget are both null) and sometimes
**higher** (dropping evidence needs a probe, restricting the channel removes
the probe that would have worked, and only widening the channel repairs both).
``decoupling_audit`` measures both and the tests refuse a draw in which they do
not occur, because a draw without them would mean the generator is still
degenerate.

What is identifiable, exactly
-----------------------------
A configuration *identifies* when the true extension over the world's positions
is realisable in the configuration's hypothesis space, is consistent with the
observed evidence, and every other consistent extension differs from the truth
somewhere the machine is allowed to probe.  At level 0 no probe may be spent at
all, so level 0 means the evidence alone has already pinned the answer.  From
level 1 up, spending probes is what the repair *is*, so the budget cannot
change the ground truth --- which is precisely the programme's stated
discipline that budget exhaustion is not an obstruction, here made a property
of the oracle rather than of the policy under test.

Repair lattice, in cost order.  Each repair only ever enlarges what is
available, so the closure of all repairs at levels at most ``L`` dominates every
combination of repairs costing at most ``L``; the search is therefore exhaustive
even though it walks levels rather than subsets.  ``test_escalation_independent``
verifies that dominance against brute-force enumeration of the whole powerset.

======  =====================================  ==================================
level   repair                                 effect
======  =====================================  ==================================
L1      ``raise_probe_budget``                 spend probes from the allowed set
L2      ``widen_probe_channel``                probe any position
L3      ``relax_period_bound``                 drop one numeric bound of the
        ``relax_preperiod_bound``              incumbent method language
        ``relax_value_bound``
L4      ``widen_operator_vocabulary``          restore every registered combiner
L5      ``add_identifying_representation``     admit the identifying image
L6      ``admit_misere_convention``            admit the other play convention
======  =====================================  ==================================

Arms
----
Every arm is imported, never reimplemented: ``escalation.diagnose`` plus every
entry of ``escalation_parents.PARENTS``, including ``exact_repair_planner``.
They are fed through :func:`to_escalation_world`, which expresses a blindly
perturbed world in the frozen ``EscalationWorld`` vocabulary.  The two boolean
flags that dataclass carries (``local_repair_available``,
``formulation_defect``) are computed from machine-visible state only --- the
observed evidence and the arm's own registered repairs --- never from the
perturbation record and never from the oracle.

Prior expectation, recorded before the numbers
----------------------------------------------
The programme's own evidence warns hard against expecting a win here.  The
binary Jump decision is already closed against a fully-resourced parent with a
protected incremental gap of exactly zero, and in ME-X2 the parent federation
strictly beat the governed mechanic on minimum-escalation accuracy while the
governed one made zero false escalations against the parent's 21.  The
realistic expectation is that ``exact_repair_planner`` matches or beats the
governed policy on accuracy and that the governed policy's advantage, if any,
survives only in the false-escalation rate.  A sharp drop from the old
generator's 70/70 is the *expected* and most valuable outcome, and the receipt
reports it as the headline rather than burying it.
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, replace
from functools import lru_cache
from typing import Callable

from escalation import (
    JUMP_THRESHOLD,
    Diagnosis,
    EscalationWorld,
    Level,
    Representation,
    diagnose,
    score as registered_score,
)
from escalation_generator import draw_suite as old_generator_draw_suite
from escalation_parents import PARENTS
from games import SubtractionGame, eventual_period
from methods import COMBINERS
from prereg import commit
from run_escalation import PLAN as OLD_GENERATOR_PLAN

__all__ = [
    "ARMS",
    "BlindWorld",
    "Config",
    "Family",
    "OracleVerdict",
    "Perturbation",
    "PERTURBATION_KINDS",
    "REPAIR_LATTICE",
    "RuleSpec",
    "FAMILIES",
    "RULES",
    "OPERATORS",
    "COARSENINGS",
    "IDENTIFYING_REPRESENTATION",
    "REPRESENTATION_IMAGES",
    "LEVELS",
    "decoupling_audit",
    "intent_audit",
    "nominal_intent_level",
    "NOMINAL_INTENT",
    "draw_suite",
    "draw_world",
    "build_world",
    "evaluate",
    "extension_bits",
    "family_positions",
    "hypothesis_pool",
    "minimum_sufficient_level",
    "minimum_sufficient_level_by_powerset",
    "old_generator_reference",
    "score_row",
    "single_perturbation_variants",
    "to_escalation_world",
    "truth_bits",
    "well_posedness_screen",
]


# --------------------------------------------------------------------------
# registered constants
# --------------------------------------------------------------------------

LEVELS: tuple[Level, ...] = (
    Level.L0_NO_ESCALATION,
    Level.L1_SEARCH_MORE,
    Level.L2_MORE_EVIDENCE,
    Level.L3_LOCAL_REPAIR,
    Level.L4_OPERATOR_INSUFFICIENT,
    Level.L5_REPRESENTATION_CHANGE,
    Level.L6_FORMULATION_CHANGE,
)

#: the adequate operator vocabulary; ``methods.COMBINERS`` is imported whole so
#: that the vocabulary is the one already registered by the lane, not a fresh
#: one chosen for this experiment.
OPERATORS: tuple[str, ...] = tuple(sorted(COMBINERS))

#: generous bounds: every registered rule satisfies all three, so the
#: unperturbed language is adequate by construction.
MAX_PERIOD = 64
MAX_PREPERIOD = 64
MAX_VALUE = 16

CONVENTIONS = ("normal", "misere")


# --------------------------------------------------------------------------
# the registered per-heap rule catalogue
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class RuleSpec:
    """One eventually periodic per-heap Grundy rule.

    The catalogue is built from real subtraction families, so every rule in it
    is the exact Grundy rule of *some* game.  That matters: the decoys are not
    hand-drawn near-misses, they are other people's correct answers, and they
    collide with the truth on short evidence exactly as often as the arithmetic
    makes them.
    """

    name: str
    preperiod: int
    period: int
    values: tuple[int, ...]

    @property
    def max_value(self) -> int:
        return max(self.values)

    def grundy(self, n: int) -> int:
        if n < self.preperiod:
            return self.values[n]
        return self.values[self.preperiod + (n - self.preperiod) % self.period]


def _rule_for(moves: tuple[int, ...]) -> RuleSpec:
    preperiod, period = eventual_period(moves)
    table = SubtractionGame(moves).grundy_upto(preperiod + period - 1)
    return RuleSpec(
        name="SUB(" + ",".join(str(s) for s in moves) + ")",
        preperiod=preperiod,
        period=period,
        values=tuple(table),
    )


#: move sets that a *world* may be drawn from
FAMILY_MOVE_SETS: tuple[tuple[int, ...], ...] = (
    (1, 2), (1, 3), (1, 2, 3), (1, 3, 4), (1, 4, 5), (2, 3), (1, 2, 3, 4),
    (2, 3, 5), (2, 4, 6), (2, 4, 7), (3, 4, 5), (1, 5, 6), (2, 7, 8), (3, 7, 8),
)

#: move sets whose rules the *machine* may hypothesise; a strict superset, so
#: the language always contains the truth and also contains rivals the world
#: was never drawn from
RULE_MOVE_SETS: tuple[tuple[int, ...], ...] = FAMILY_MOVE_SETS + (
    (1, 2, 4), (1, 2, 5), (1, 3, 5), (2, 5, 6), (1, 2, 6), (3, 5, 9),
    (1, 6, 9), (2, 4, 5, 8),
)

RULES: tuple[RuleSpec, ...] = tuple(_rule_for(m) for m in RULE_MOVE_SETS)


# --------------------------------------------------------------------------
# families and their exact truth
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Family:
    """``SUBNIM(moves, heaps)`` restricted to heaps of size at most ``top``."""

    moves: tuple[int, ...]
    heaps: int
    top: int

    @property
    def family_id(self) -> str:
        return (
            "SUBNIM(" + ",".join(str(s) for s in self.moves)
            + f";k={self.heaps},top={self.top})"
        )


#: (heaps, top) shapes; each keeps the position count at or below 64 so an
#: extension over positions fits one Python int used as a bit set
SHAPES: tuple[tuple[int, int], ...] = ((1, 40), (2, 7), (3, 3))

FAMILIES: tuple[Family, ...] = tuple(
    Family(moves=m, heaps=k, top=t) for m in FAMILY_MOVE_SETS for (k, t) in SHAPES
)


@lru_cache(maxsize=None)
def family_positions(family: Family) -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.product(range(family.top + 1), repeat=family.heaps))


@lru_cache(maxsize=None)
def _position_index(family: Family) -> dict:
    return {p: i for i, p in enumerate(family_positions(family))}


@lru_cache(maxsize=None)
def truth_bits(family: Family, convention: str) -> int:
    """Exact outcome of every position, as a bit set over the position index.

    Backward induction over the joint state space, not Sprague--Grundy, so the
    same routine is exact under both conventions.  Bit ``i`` is set when
    position ``i`` is a P-position: a loss for the player to move.  Under misere
    play a player unable to move *wins*, which is the single line that differs.
    """
    positions = family_positions(family)
    index = _position_index(family)
    terminal_is_p = convention == "normal"
    memo: dict[tuple[int, ...], bool] = {}

    def successors(pos: tuple[int, ...]) -> list[tuple[int, ...]]:
        out = []
        for i, h in enumerate(pos):
            for s in family.moves:
                if s <= h:
                    out.append(pos[:i] + (h - s,) + pos[i + 1:])
        return out

    def is_p(pos: tuple[int, ...]) -> bool:
        cached = memo.get(pos)
        if cached is not None:
            return cached
        succ = successors(pos)
        value = terminal_is_p if not succ else all(not is_p(s) for s in succ)
        memo[pos] = value
        return value

    bits = 0
    for p in positions:
        if is_p(p):
            bits |= 1 << index[p]
    return bits


# --------------------------------------------------------------------------
# representations
# --------------------------------------------------------------------------

#: A representation is a pure function of the position.  A hypothesis must be
#: constant on its fibres, which is enforced by evaluating every hypothesis at
#: the fibre's canonical member rather than at the position itself.  A
#: coarsening that happens not to collide therefore costs nothing, which is the
#: point: ``sorted_heaps`` is a coarsening whose ground-truth level is usually
#: L0, and only the oracle can say so.
REPRESENTATION_IMAGES: dict[str, Callable[[tuple[int, ...]], object]] = {
    "heap_tuple": lambda p: p,
    "sorted_heaps": lambda p: tuple(sorted(p)),
    "token_total": lambda p: sum(p),
    "first_heap": lambda p: p[0],
    "parity_tuple": lambda p: tuple(h % 2 for h in p),
}

IDENTIFYING_REPRESENTATION = "heap_tuple"
COARSENINGS: tuple[str, ...] = ("sorted_heaps", "token_total", "first_heap", "parity_tuple")


@lru_cache(maxsize=None)
def _canonical(family: Family, representation: str) -> tuple[tuple[int, ...], ...]:
    image = REPRESENTATION_IMAGES[representation]
    canon: dict[object, tuple[int, ...]] = {}
    for p in family_positions(family):
        key = image(p)
        if key not in canon or p < canon[key]:
            canon[key] = p
    return tuple(canon[image(p)] for p in family_positions(family))


# --------------------------------------------------------------------------
# hypothesis extensions
# --------------------------------------------------------------------------


@lru_cache(maxsize=None)
def extension_bits(
    family: Family, rule: RuleSpec, operator: str, representation: str, convention: str
) -> int:
    """The full extension of one hypothesis, as a bit set over positions.

    Identifiability is an extensional property, so hypotheses are compared by
    extension and duplicates are collapsed.  Two syntactically distinct
    hypotheses that agree everywhere are the same hypothesis for every purpose
    this experiment measures.
    """
    canon = _canonical(family, representation)
    combine = COMBINERS[operator]
    bits = 0
    for i in range(len(canon)):
        values = [rule.grundy(h) for h in canon[i]]
        if convention == "misere" and all(v <= 1 for v in values):
            predicted = sum(1 for v in values if v == 1) % 2 == 1
        else:
            predicted = combine(values) == 0
        if predicted:
            bits |= 1 << i
    return bits


@lru_cache(maxsize=None)
def hypothesis_pool(
    family: Family,
    period_bound: int,
    preperiod_bound: int,
    value_bound: int,
    operators: tuple[str, ...],
    representations: tuple[str, ...],
    conventions: tuple[str, ...],
) -> tuple[int, ...]:
    """Every distinct extension expressible under these language parameters."""
    seen: set[int] = set()
    out: list[int] = []
    for rule in RULES:
        if rule.period > period_bound:
            continue
        if rule.preperiod > preperiod_bound:
            continue
        if rule.max_value >= value_bound:
            continue
        for operator in operators:
            for representation in representations:
                for convention in conventions:
                    ext = extension_bits(family, rule, operator, representation, convention)
                    if ext not in seen:
                        seen.add(ext)
                        out.append(ext)
    return tuple(out)


def _mask(indices) -> int:
    bits = 0
    for i in indices:
        bits |= 1 << i
    return bits


def consistent(pool: tuple[int, ...], observed_mask: int, truth_ext: int) -> tuple[int, ...]:
    """Extensions in ``pool`` reproducing the truth at every observed position.

    Only ``truth_ext & observed_mask`` is read, so this is machine-visible
    filtering: the labels of unprobed positions never enter.
    """
    target = truth_ext & observed_mask
    return tuple(e for e in pool if (e & observed_mask) == target)


# --------------------------------------------------------------------------
# configurations and the blind perturbation menu
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Config:
    """Everything the task setup fixes, and the only thing perturbations touch.

    ``search_permitted`` is an oracle-lattice coordinate, not a fact about the
    world: it is how the L1 repair "spend probes" is expressed.  A world's own
    config always carries ``False`` and :func:`to_escalation_world` ignores the
    field entirely, so no arm can see it.
    """

    period_bound: int
    preperiod_bound: int
    value_bound: int
    operators: tuple[str, ...]
    representations: tuple[str, ...]
    conventions: tuple[str, ...]
    allowed_probes: tuple[int, ...]
    probe_budget: int
    observed: tuple[int, ...]
    search_permitted: bool = False


@dataclass(frozen=True)
class Perturbation:
    """One syntactic edit to a configuration.

    ``kind`` names the *edit*, never a defect type and never a level.  Nothing
    in this module maps a kind to a level, and the oracle never receives this
    object.  It is carried on the world only so a third party can audit what was
    done to it after the fact.
    """

    kind: str
    params: tuple


PERTURBATION_KINDS: tuple[str, ...] = (
    "shrink_period_bound",
    "shrink_preperiod_bound",
    "shrink_value_bound",
    "remove_operators",
    "coarsen_representation",
    "restrict_probe_set",
    "cut_probe_budget",
    "flip_play_convention",
    "drop_evidence",
)


def _apply_perturbation(
    perturbation: Perturbation, family: Family, config: Config, convention: str
) -> tuple[Config, str]:
    kind, params = perturbation.kind, perturbation.params
    if kind == "shrink_period_bound":
        return replace(config, period_bound=params[0]), convention
    if kind == "shrink_preperiod_bound":
        return replace(config, preperiod_bound=params[0]), convention
    if kind == "shrink_value_bound":
        return replace(config, value_bound=params[0]), convention
    if kind == "remove_operators":
        removed = set(params)
        return replace(config, operators=tuple(o for o in config.operators if o not in removed)), convention
    if kind == "coarsen_representation":
        return replace(config, representations=(params[0],)), convention
    if kind == "restrict_probe_set":
        return replace(config, allowed_probes=tuple(params)), convention
    if kind == "cut_probe_budget":
        return replace(config, probe_budget=params[0]), convention
    if kind == "flip_play_convention":
        return config, "misere"
    if kind == "drop_evidence":
        return replace(config, observed=tuple(params)), convention
    raise KeyError(kind)


@dataclass(frozen=True)
class BlindWorld:
    """One world produced by perturbing a working setup, with no level attached.

    There is deliberately no ``minimum_sufficient_level`` field.  The level is
    not a property the generator knows; it is computed after the fact by
    :func:`minimum_sufficient_level`, which never sees ``perturbations``.
    """

    world_id: str
    family: Family
    baseline_config: Config
    perturbations: tuple[Perturbation, ...]
    config: Config
    actual_convention: str

    @property
    def perturbation_count(self) -> int:
        return len(self.perturbations)

    @property
    def perturbation_kinds(self) -> tuple[str, ...]:
        return tuple(p.kind for p in self.perturbations)


def build_world(
    world_id: str,
    family: Family,
    baseline: Config,
    perturbations: tuple[Perturbation, ...],
) -> BlindWorld:
    """Apply perturbations in a canonical order so the world is order-free."""
    rank = {k: i for i, k in enumerate(PERTURBATION_KINDS)}
    ordered = tuple(sorted(perturbations, key=lambda p: rank[p.kind]))
    config, convention = baseline, "normal"
    for perturbation in ordered:
        config, convention = _apply_perturbation(perturbation, family, config, convention)
    if not any(p.kind == "cut_probe_budget" for p in ordered):
        config = replace(config, probe_budget=len(config.allowed_probes))
    return BlindWorld(
        world_id=world_id,
        family=family,
        baseline_config=baseline,
        perturbations=ordered,
        config=config,
        actual_convention=convention,
    )


def single_perturbation_variants(world: BlindWorld) -> tuple[BlindWorld, ...]:
    """The same baseline carrying each of its perturbations alone.

    Used by :func:`decoupling_audit` to show that the joint level is not a
    function of the individual perturbations.  Not used by any arm.
    """
    return tuple(
        build_world(f"{world.world_id}#{p.kind}", world.family, world.baseline_config, (p,))
        for p in world.perturbations
    )


# --------------------------------------------------------------------------
# THE REPAIR ORACLE.  Used by the scorer only.  No arm may call it.
# --------------------------------------------------------------------------

REPAIR_LATTICE: tuple[tuple[Level, str], ...] = (
    (Level.L1_SEARCH_MORE, "raise_probe_budget"),
    (Level.L2_MORE_EVIDENCE, "widen_probe_channel"),
    (Level.L3_LOCAL_REPAIR, "relax_period_bound"),
    (Level.L3_LOCAL_REPAIR, "relax_preperiod_bound"),
    (Level.L3_LOCAL_REPAIR, "relax_value_bound"),
    (Level.L4_OPERATOR_INSUFFICIENT, "widen_operator_vocabulary"),
    (Level.L5_REPRESENTATION_CHANGE, "add_identifying_representation"),
    (Level.L6_FORMULATION_CHANGE, "admit_misere_convention"),
)


def apply_repair(name: str, family: Family, config: Config) -> Config:
    """Apply one registered repair.  Every repair only ever enlarges."""
    if name == "raise_probe_budget":
        return replace(config, search_permitted=True, probe_budget=len(config.allowed_probes))
    if name == "widen_probe_channel":
        every = tuple(range(len(family_positions(family))))
        return replace(config, search_permitted=True, allowed_probes=every, probe_budget=len(every))
    if name == "relax_period_bound":
        return replace(config, period_bound=MAX_PERIOD)
    if name == "relax_preperiod_bound":
        return replace(config, preperiod_bound=MAX_PREPERIOD)
    if name == "relax_value_bound":
        return replace(config, value_bound=MAX_VALUE)
    if name == "widen_operator_vocabulary":
        return replace(config, operators=OPERATORS)
    if name == "add_identifying_representation":
        reps = tuple(dict.fromkeys(config.representations + (IDENTIFYING_REPRESENTATION,)))
        return replace(config, representations=reps)
    if name == "admit_misere_convention":
        return replace(config, conventions=tuple(dict.fromkeys(config.conventions + ("misere",))))
    raise KeyError(name)


def closure(family: Family, config: Config, level: Level) -> Config:
    """Every registered repair costing at most ``level``, applied together."""
    out = replace(config, search_permitted=False)
    for repair_level, name in REPAIR_LATTICE:
        if repair_level <= level:
            out = apply_repair(name, family, out)
    return out


def identifies(family: Family, config: Config, truth_ext: int) -> bool:
    """Does this configuration pin the truth?

    Three conditions, all extensional: the truth must be expressible, it must
    survive the evidence, and every rival that survives the evidence must differ
    from it somewhere the machine may probe.  When probing is not permitted the
    third condition hardens to "there is no rival at all".
    """
    pool = hypothesis_pool(
        family,
        config.period_bound,
        config.preperiod_bound,
        config.value_bound,
        config.operators,
        config.representations,
        config.conventions,
    )
    survivors = consistent(pool, _mask(config.observed), truth_ext)
    if truth_ext not in survivors:
        return False
    rivals = [e for e in survivors if e != truth_ext]
    if not config.search_permitted:
        return not rivals
    probe_mask = _mask(config.allowed_probes)
    return all(((e ^ truth_ext) & probe_mask) != 0 for e in rivals)


@dataclass(frozen=True)
class OracleVerdict:
    """What the exhaustive repair search found."""

    level: Level
    repair: str

    def as_dict(self) -> dict:
        return {"minimum_sufficient_level": self.level.name, "credited_repair": self.repair}


def minimum_sufficient_level(world: BlindWorld) -> OracleVerdict:
    """Ground truth by exhaustive search over the registered repair lattice.

    Walks levels in increasing cost order and returns the first at which the
    task becomes identifiable, then names the individual repair that did it (or
    the level's closure, when no single repair at that level suffices and the
    combination with everything cheaper was needed).

    This function reads ``world.family``, ``world.actual_convention`` and
    ``world.config``.  It does not read ``world.perturbations`` and cannot: the
    perturbation record is not on any path from here.  That is the property the
    experiment turns on, and ``test_escalation_independent`` asserts it both
    behaviourally and by source inspection.
    """
    family = world.family
    truth_ext = truth_bits(family, world.actual_convention)
    for level in LEVELS:
        if not identifies(family, closure(family, world.config, level), truth_ext):
            continue
        if level is Level.L0_NO_ESCALATION:
            return OracleVerdict(level=level, repair="none")
        below = closure(family, world.config, Level(int(level) - 1))
        credited = "closure_" + level.name
        for repair_level, name in REPAIR_LATTICE:
            if repair_level is not level:
                continue
            if identifies(family, apply_repair(name, family, below), truth_ext):
                credited = name
                break
        return OracleVerdict(level=level, repair=credited)
    raise AssertionError(
        f"{world.world_id} is not repairable within the registered lattice; "
        "the world is ill-posed and must not be scored"
    )


def minimum_sufficient_level_by_powerset(world: BlindWorld) -> Level:
    """Brute-force cross-check: minimise ``max(cost)`` over every repair subset.

    Exponential and used only by the tests, to verify that walking levels is
    genuinely exhaustive over the lattice rather than a convenient shortcut.
    """
    family = world.family
    truth_ext = truth_bits(family, world.actual_convention)
    if identifies(family, replace(world.config, search_permitted=False), truth_ext):
        return Level.L0_NO_ESCALATION
    best: Level | None = None
    for size in range(1, len(REPAIR_LATTICE) + 1):
        for subset in itertools.combinations(REPAIR_LATTICE, size):
            cost = max(lvl for lvl, _ in subset)
            if best is not None and cost >= best:
                continue
            config = replace(world.config, search_permitted=False)
            for _, name in subset:
                config = apply_repair(name, family, config)
            if identifies(family, config, truth_ext):
                best = cost
    if best is None:
        raise AssertionError(f"{world.world_id} is not repairable within the registered lattice")
    return best


# --------------------------------------------------------------------------
# the draw
# --------------------------------------------------------------------------


def _draw_perturbation(rng: random.Random, family: Family, baseline: Config, kind: str) -> Perturbation:
    """Draw one perturbation's parameters.  No level is consulted or produced."""
    positions = len(family_positions(family))
    if kind == "shrink_period_bound":
        return Perturbation(kind, (rng.randint(1, 6),))
    if kind == "shrink_preperiod_bound":
        return Perturbation(kind, (rng.randint(0, 6),))
    if kind == "shrink_value_bound":
        return Perturbation(kind, (rng.randint(2, 4),))
    if kind == "remove_operators":
        # a uniformly random non-empty proper subset of the vocabulary: the
        # blind menu, not a size chosen to make the defect bind
        dropped = rng.sample(OPERATORS, rng.randint(1, len(OPERATORS) - 1))
        return Perturbation(kind, tuple(sorted(dropped)))
    if kind == "coarsen_representation":
        return Perturbation(kind, (rng.choice(COARSENINGS),))
    if kind == "restrict_probe_set":
        keep = max(1, int(positions * rng.choice((0.05, 0.1, 0.2, 0.35))))
        return Perturbation(kind, tuple(sorted(rng.sample(range(positions), keep))))
    if kind == "cut_probe_budget":
        return Perturbation(kind, (rng.choice((0, 1, 2)),))
    if kind == "flip_play_convention":
        return Perturbation(kind, ())
    if kind == "drop_evidence":
        observed = baseline.observed
        return Perturbation(kind, tuple(sorted(rng.sample(observed, rng.randint(0, len(observed) - 1)))))
    raise KeyError(kind)


#: how many perturbations a world carries.  Fixed before any outcome was seen
#: and never revisited: zero is the no-escalation control, two is where the
#: level decouples from the individual edits.
PERTURBATION_COUNT_WEIGHTS: tuple[int, int, int] = (15, 45, 40)


def draw_world(rng: random.Random, index: int) -> BlindWorld:
    """One world: a working setup, then zero, one or two blind perturbations."""
    family = rng.choice(FAMILIES)
    positions = len(family_positions(family))
    every = tuple(range(positions))
    observed = tuple(sorted(rng.sample(every, rng.randint(4, 12))))
    baseline = Config(
        period_bound=MAX_PERIOD,
        preperiod_bound=MAX_PREPERIOD,
        value_bound=MAX_VALUE,
        operators=OPERATORS,
        representations=(IDENTIFYING_REPRESENTATION,),
        conventions=("normal",),
        allowed_probes=every,
        probe_budget=positions,
        observed=observed,
    )
    count = rng.choices((0, 1, 2), weights=PERTURBATION_COUNT_WEIGHTS, k=1)[0]
    kinds = rng.sample(PERTURBATION_KINDS, count)
    perturbations = tuple(_draw_perturbation(rng, family, baseline, k) for k in kinds)
    return build_world(f"E4_{index:04d}", family, baseline, perturbations)


def draw_suite(seed: str, count: int) -> tuple[BlindWorld, ...]:
    """A commitment-derived draw.  Reproducible from the published plan alone."""
    rng = random.Random(int(seed, 16) % (2 ** 63))
    return tuple(draw_world(rng, i) for i in range(count))


# --------------------------------------------------------------------------
# adapting a blind world to the frozen EscalationWorld the arms already speak
# --------------------------------------------------------------------------


def _callables(family: Family, pool: tuple[int, ...]) -> tuple[Callable[[object], bool], ...]:
    index = _position_index(family)

    def build(ext: int) -> Callable[[object], bool]:
        return lambda p: bool((ext >> index[p]) & 1)

    return tuple(build(e) for e in pool)


def to_escalation_world(world: BlindWorld) -> EscalationWorld:
    """Express a blindly perturbed world in the registered ``EscalationWorld``.

    Every arm receives this object and nothing else, so every arm sees exactly
    the same visible state.  Two points of care:

    * ``minimum_sufficient_level`` is left at its default.  No arm reads it and
      the scorer never consults it; the ground truth lives only in the oracle's
      verdict, which is computed on the :class:`BlindWorld`, not on this.
    * ``local_repair_available`` and ``formulation_defect`` are the flags
      ``escalation.diagnose`` and ``exact_repair_planner`` already consult.  Both
      are computed here from the observed evidence and the arm's own registered
      repairs --- "does relaxing my bounds admit a fit to what I have seen", and
      "does no hypothesis over any registered representation fit under my
      assumed convention while one does under the other".  Neither reads the
      perturbation record and neither calls the oracle.
    """
    family = world.family
    positions = family_positions(family)
    index = _position_index(family)
    truth_ext = truth_bits(family, world.actual_convention)
    config = world.config
    observed_mask = _mask(config.observed)

    incumbent = hypothesis_pool(
        family, config.period_bound, config.preperiod_bound, config.value_bound,
        config.operators, config.representations, config.conventions,
    )
    widened = hypothesis_pool(
        family, config.period_bound, config.preperiod_bound, config.value_bound,
        OPERATORS, config.representations, config.conventions,
    )
    relaxed = hypothesis_pool(
        family, MAX_PERIOD, MAX_PREPERIOD, MAX_VALUE,
        config.operators, config.representations, config.conventions,
    )
    refined_reps = tuple(dict.fromkeys(config.representations + (IDENTIFYING_REPRESENTATION,)))
    refined = hypothesis_pool(
        family, MAX_PERIOD, MAX_PREPERIOD, MAX_VALUE, OPERATORS, refined_reps, config.conventions,
    )
    other_convention = tuple(dict.fromkeys(config.conventions + ("misere", "normal")))
    reformulated = hypothesis_pool(
        family, MAX_PERIOD, MAX_PREPERIOD, MAX_VALUE, OPERATORS, refined_reps, other_convention,
    )

    local_repair_available = bool(consistent(relaxed, observed_mask, truth_ext))
    fits_under_assumed_convention = bool(consistent(refined, observed_mask, truth_ext))
    fits_under_some_convention = bool(consistent(reformulated, observed_mask, truth_ext))
    formulation_defect = (not fits_under_assumed_convention) and fits_under_some_convention

    representation = config.representations[0]
    return EscalationWorld(
        world_id=world.world_id,
        positions=positions,
        truth=lambda p: bool((truth_ext >> index[p]) & 1),
        representation=Representation(representation, REPRESENTATION_IMAGES[representation]),
        incumbent_hypotheses=_callables(family, incumbent),
        widened_hypotheses=_callables(family, widened),
        refined_hypotheses=_callables(family, refined),
        allowed_probes=tuple(positions[i] for i in config.allowed_probes),
        observed=tuple((positions[i], bool((truth_ext >> i) & 1)) for i in config.observed),
        probe_budget=config.probe_budget,
        local_repair_available=local_repair_available,
        formulation_defect=formulation_defect,
        notes=family.family_id,
    )


ARMS: dict[str, Callable[[EscalationWorld], Diagnosis]] = {"governed": diagnose, **PARENTS}


# --------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------


def score_row(world: BlindWorld, diagnosis: Diagnosis, verdict: OracleVerdict) -> dict:
    """Score one diagnosis against the oracle's verdict.

    ``false_escalation`` counts a Jump where the minimum sufficient level was
    below the threshold; ``missed_escalation`` the reverse; ``overreach`` and
    ``underreach`` count any deviation in either direction, including within the
    threshold, because a policy that always picks the top level would otherwise
    look perfect on the Jump endpoints.
    """
    truth_level = verdict.level
    return {
        "world_id": world.world_id,
        "diagnosed": diagnosis.level.name,
        "minimum_sufficient": truth_level.name,
        "credited_repair": verdict.repair,
        "exact_match": diagnosis.level == truth_level,
        "false_escalation": diagnosis.is_jump and truth_level < JUMP_THRESHOLD,
        "missed_escalation": (not diagnosis.is_jump) and truth_level >= JUMP_THRESHOLD,
        "overreach": int(diagnosis.level) > int(truth_level),
        "underreach": int(diagnosis.level) < int(truth_level),
        "terminal": diagnosis.terminal,
        "witnessed": diagnosis.obstruction_witness is not None,
        "perturbation_count": world.perturbation_count,
    }


def _summarise(rows: list[dict]) -> dict:
    n = len(rows)
    exact = sum(r["exact_match"] for r in rows)
    confusion: dict[str, dict[str, int]] = {}
    for r in rows:
        confusion.setdefault(r["minimum_sufficient"], {})
        confusion[r["minimum_sufficient"]][r["diagnosed"]] = (
            confusion[r["minimum_sufficient"]].get(r["diagnosed"], 0) + 1
        )
    by_count: dict[str, dict] = {}
    for k in (0, 1, 2):
        sub = [r for r in rows if r["perturbation_count"] == k]
        by_count[str(k)] = {
            "n": len(sub),
            "exact_match": sum(r["exact_match"] for r in sub),
            "accuracy": round(sum(r["exact_match"] for r in sub) / len(sub), 4) if sub else None,
        }
    by_level: dict[str, dict] = {}
    for level in LEVELS:
        sub = [r for r in rows if r["minimum_sufficient"] == level.name]
        by_level[level.name] = {
            "n": len(sub),
            "exact_match": sum(r["exact_match"] for r in sub),
            "accuracy": round(sum(r["exact_match"] for r in sub) / len(sub), 4) if sub else None,
        }
    return {
        "n": n,
        "exact_match": exact,
        "accuracy": round(exact / n, 4) if n else None,
        "false_escalation": sum(r["false_escalation"] for r in rows),
        "missed_escalation": sum(r["missed_escalation"] for r in rows),
        "overreach": sum(r["overreach"] for r in rows),
        "underreach": sum(r["underreach"] for r in rows),
        "witnessed": sum(r["witnessed"] for r in rows),
        "confusion_matrix": {k: dict(sorted(v.items())) for k, v in sorted(confusion.items())},
        "accuracy_by_perturbation_count": by_count,
        "accuracy_by_minimum_sufficient_level": by_level,
    }


def evaluate(worlds, arms: dict | None = None) -> dict:
    """Score every arm on ``worlds``.

    The oracle is called exactly here, once per world, and its verdicts are
    handed only to :func:`score_row`.  No arm receives a verdict.
    """
    arms = ARMS if arms is None else arms
    adapted = [to_escalation_world(w) for w in worlds]
    verdicts = [minimum_sufficient_level(w) for w in worlds]

    levels: dict[str, int] = {}
    counts: dict[str, int] = {}
    repairs: dict[str, int] = {}
    for world, verdict in zip(worlds, verdicts):
        levels[verdict.level.name] = levels.get(verdict.level.name, 0) + 1
        repairs[verdict.repair] = repairs.get(verdict.repair, 0) + 1
        key = str(world.perturbation_count)
        counts[key] = counts.get(key, 0) + 1

    out = {
        "n": len(worlds),
        "minimum_sufficient_level_distribution": dict(sorted(levels.items())),
        "credited_repair_distribution": dict(sorted(repairs.items())),
        "perturbation_count_distribution": dict(sorted(counts.items())),
        "perturbation_kind_distribution": {},
        "arms": {},
    }
    kinds: dict[str, int] = {}
    for world in worlds:
        for kind in world.perturbation_kinds:
            kinds[kind] = kinds.get(kind, 0) + 1
    out["perturbation_kind_distribution"] = dict(sorted(kinds.items()))

    for name, fn in arms.items():
        rows = [
            score_row(world, fn(world_view), verdict)
            for world, world_view, verdict in zip(worlds, adapted, verdicts)
        ]
        out["arms"][name] = _summarise(rows)
    return out


# --------------------------------------------------------------------------
# audits
# --------------------------------------------------------------------------


#: The level the OLD generator's defect taxonomy would have registered for each
#: edit: the repair that undoes it.  This mapping exists for exactly one
#: purpose, to be *checked against* the oracle, and it is the thing this
#: experiment refuses to treat as ground truth.  It is never used to score an
#: arm, never given to an arm, and never read by the oracle;
#: ``test_escalation_independent`` asserts all three by source inspection.
NOMINAL_INTENT: dict[str, Level] = {
    "cut_probe_budget": Level.L1_SEARCH_MORE,
    "drop_evidence": Level.L1_SEARCH_MORE,
    "restrict_probe_set": Level.L2_MORE_EVIDENCE,
    "shrink_period_bound": Level.L3_LOCAL_REPAIR,
    "shrink_preperiod_bound": Level.L3_LOCAL_REPAIR,
    "shrink_value_bound": Level.L3_LOCAL_REPAIR,
    "remove_operators": Level.L4_OPERATOR_INSUFFICIENT,
    "coarsen_representation": Level.L5_REPRESENTATION_CHANGE,
    "flip_play_convention": Level.L6_FORMULATION_CHANGE,
}


def nominal_intent_level(world: BlindWorld) -> Level:
    """What a defect-type generator would have called this world's level.

    The old generator picks the defect first, so its registered level is exactly
    this: the cost of the repair that undoes the edit it made.  With two edits
    the natural extension is the more expensive of the two, since both must be
    undone.  Audit only.
    """
    if not world.perturbations:
        return Level.L0_NO_ESCALATION
    return max(NOMINAL_INTENT[p.kind] for p in world.perturbations)


def intent_audit(worlds) -> dict:
    """How often is the generator's own intent the wrong ground truth?

    This is the experiment's central measurement about *method* rather than
    about any arm.  Every disagreement here is a world the old procedure would
    have mislabelled, and every arm scored against that label would have been
    scored against a wrong answer.
    """
    agree = 0
    intent_too_high = 0
    intent_too_low = 0
    by_count: dict[str, dict[str, int]] = {
        str(k): {"n": 0, "agree": 0, "intent_too_high": 0, "intent_too_low": 0} for k in (0, 1, 2)
    }
    pairs = 0
    pair_below_min = 0
    pair_above_max = 0
    pair_between = 0
    examples: list[dict] = []
    for world in worlds:
        oracle = minimum_sufficient_level(world).level
        intent = nominal_intent_level(world)
        cell = by_count[str(world.perturbation_count)]
        cell["n"] += 1
        if oracle == intent:
            agree += 1
            cell["agree"] += 1
        elif int(oracle) < int(intent):
            intent_too_high += 1
            cell["intent_too_high"] += 1
        else:
            intent_too_low += 1
            cell["intent_too_low"] += 1
        if world.perturbation_count == 2:
            pairs += 1
            intents = [int(NOMINAL_INTENT[p.kind]) for p in world.perturbations]
            if int(oracle) < min(intents):
                pair_below_min += 1
                if len(examples) < 5:
                    examples.append({
                        "world_id": world.world_id,
                        "perturbations": list(world.perturbation_kinds),
                        "nominal_intents": [Level(i).name for i in intents],
                        "oracle_level": oracle.name,
                    })
            elif int(oracle) > max(intents):
                pair_above_max += 1
            else:
                pair_between += 1
    total = len(worlds)
    return {
        "n": total,
        "intent_equals_oracle": agree,
        "intent_agreement_rate": round(agree / total, 4) if total else None,
        "intent_overstates_required_level": intent_too_high,
        "intent_understates_required_level": intent_too_low,
        "by_perturbation_count": by_count,
        "two_perturbation_worlds": pairs,
        "oracle_below_both_intents": pair_below_min,
        "oracle_above_both_intents": pair_above_max,
        "oracle_between_intents": pair_between,
        "examples_oracle_below_both_intents": examples,
    }


def decoupling_audit(worlds) -> dict:
    """Is the joint level a function of the individual perturbations?

    For every two-perturbation world, compare its level against the levels of
    the same baseline carrying each perturbation alone.  ``lower_than_both``
    counts worlds where one repair fixed what two edits did; ``higher_than_both``
    counts worlds where neither edit alone required that level.  If both are
    zero the generator has not actually decoupled intent from ground truth and
    the experiment has failed at its one job.
    """
    lower = 0
    higher = 0
    equal = 0
    examples: dict[str, list] = {"lower_than_both": [], "higher_than_both": []}
    pairs = 0
    for world in worlds:
        if world.perturbation_count != 2:
            continue
        pairs += 1
        joint = minimum_sufficient_level(world).level
        singles = [minimum_sufficient_level(v).level for v in single_perturbation_variants(world)]
        record = {
            "world_id": world.world_id,
            "perturbations": list(world.perturbation_kinds),
            "joint_level": joint.name,
            "levels_alone": [s.name for s in singles],
        }
        if int(joint) < min(int(s) for s in singles):
            lower += 1
            if len(examples["lower_than_both"]) < 5:
                examples["lower_than_both"].append(record)
        elif int(joint) > max(int(s) for s in singles):
            higher += 1
            if len(examples["higher_than_both"]) < 5:
                examples["higher_than_both"].append(record)
        else:
            equal += 1
    return {
        "two_perturbation_worlds": pairs,
        "lower_than_both": lower,
        "higher_than_both": higher,
        "between_or_equal": equal,
        "decoupled": lower > 0 and higher > 0,
        "examples": examples,
    }


def well_posedness_screen() -> dict:
    """Every registered family must be expressible under both conventions.

    The misere hypothesis form used by the language --- flip when every per-heap
    Grundy value is at most one, otherwise combine as usual --- is exact for
    tame games and is not exact in general.  Rather than assume the families are
    tame, check it: if a family failed, worlds drawn from it under a flipped
    convention would be unrepairable at any level and must not be drawn at all.
    """
    failures = []
    for family in FAMILIES:
        full = hypothesis_pool(
            family, MAX_PERIOD, MAX_PREPERIOD, MAX_VALUE, OPERATORS,
            (IDENTIFYING_REPRESENTATION,), CONVENTIONS,
        )
        for convention in CONVENTIONS:
            if truth_bits(family, convention) not in full:
                failures.append({"family": family.family_id, "convention": convention})
    return {
        "families": len(FAMILIES),
        "conventions": list(CONVENTIONS),
        "families_not_expressible": failures,
        "well_posed": not failures,
    }


# --------------------------------------------------------------------------
# the contrast that must not be read past
# --------------------------------------------------------------------------


def old_generator_reference(arms: dict | None = None) -> dict:
    """Re-run the *old* generator's protected draw and score it, arm by arm.

    This is not a quotation of the published 70/70.  It re-derives the old
    pilot's commitment from ``run_escalation.PLAN``, redraws its protected
    suite and rescores it, so the contrast in the receipt is computed rather
    than asserted.
    """
    arms = ARMS if arms is None else arms
    commitment = commit(OLD_GENERATOR_PLAN)
    worlds = old_generator_draw_suite(commitment.protected_seed, OLD_GENERATOR_PLAN["per_level"])
    out = {
        "source": "escalation_generator.draw_suite via run_escalation.PLAN",
        "commitment_sha256": commitment.commitment,
        "n": len(worlds),
        "arms": {},
    }
    for name, fn in arms.items():
        rows = [registered_score(w, fn(w)) for w in worlds]
        out["arms"][name] = {
            "n": len(rows),
            "exact_match": sum(r["exact_match"] for r in rows),
            "accuracy": round(sum(r["exact_match"] for r in rows) / len(rows), 4),
            "false_escalation": sum(r["false_jump"] for r in rows),
            "missed_escalation": sum(r["missed_jump"] for r in rows),
        }
    return out
