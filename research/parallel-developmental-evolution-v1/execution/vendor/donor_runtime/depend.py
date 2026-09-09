"""Dependency discovery: which beliefs actually rest on which evidence.

This module is experiment ``E3`` of the cognitive-ladder programme and it
exists because the scaling pilot's revocation result was not a cognitive
finding.  That pilot's own receipt says why:

    the dependency graph was built from the same declarations that populated
    the store, so revocation is exact by construction.  These numbers measure
    the cost of exact revocation, not dependency discovery.

The machine was handed the reverse index.  Here it is not.

The scientific question, stated without project vocabulary:

    how does a system discover which of its beliefs actually rest on which
    evidence, so that withdrawing evidence invalidates exactly the right
    things -- neither leaving a belief standing on support that is gone, nor
    tearing down beliefs that never needed it?

The world
---------

A *method* is a periodic Grundy rule induced by :meth:`GrundyRuleLanguage.induce`
from a set of *evidence blocks*, each block a handful of observed
``(position, grundy)`` pairs.  The store declares which blocks were fed to the
induction -- it must, because otherwise nothing could be induced at all -- but
**nobody declares which of those blocks the induced rule actually depends on**.
That second set is the object under study, and separating the two is the whole
point.  Conflating them is exactly the sin the prior pilot committed.

Ground truth
------------

Operational, decidable, and computed by brute force:

    evidence block ``b`` is a TRUE dependency of method ``m`` iff re-inducing
    ``m`` from the evidence WITHOUT ``b`` yields a different rule (or no rule).

That is leave-one-out re-induction.  It is the oracle, it lives in the "scorer
only" section of this module, and no arm may call it.  A source-inspection test
enforces that in the same way ``test_scaling.py`` enforces the ``true_cone``
separation.

Leave-one-out is also *wrong*, in a specific and important way, and this module
measures its wrongness rather than hiding it.  When two blocks each suffice on
their own, removing either alone changes nothing, so leave-one-out reports that
**neither** is a dependency -- while removing both breaks the rule.  Redundant
support is invisible to leave-one-out by construction.  The second ground truth
in this module, :func:`joint_witnesses`, finds those cases by brute-force subset
search and counts them, and the registered revocation schedule contains a
two-step revocation that walks straight into one.

Discipline
----------

* ``true_cone`` is not the oracle here.  ``CompetenceStore.true_cone`` is the
  *declared* cone, which is the gift being withdrawn; it is what
  ``declared_supports_parent`` is given and it is reported as a ceiling, not as
  ground truth.
* Every re-induction is real work and is charged to the ledger that triggered
  it.  Discovery is not free, and an arm that discovers at acquisition time
  pays for it before it has served a single revocation.
* The two revocation errors are asymmetric and are never summed.  A **stale
  survivor** is a true dependent left live: the machine is now serving a belief
  whose support has been withdrawn.  A **collateral invalidation** is a
  non-dependent torn down: wasteful, recoverable, and not the same kind of
  wrong.
* No wall-clock reads.  Stdlib only.  Frozen dataclasses for records, mutable
  ledgers for accumulation, exactly as in ``scaling.py``.

Limitations, stated before any number
-------------------------------------

* The evidence *candidate* set per method is still declared.  A method's blocks
  are known; which of them matter is not.  A harness in which even the
  candidate set had to be discovered would be a different and larger
  experiment, and this one does not claim to be it.
* Leave-one-out is the oracle AND one arm's discovery procedure.  That arm can
  therefore attain precision and recall of exactly ``1.0`` against the oracle
  without that being evidence of anything except that it ran the same
  procedure.  The endpoints that separate arms are the revocation errors and
  the work, not the graph score of the arm that computes the graph score's
  definition.
* ``N`` here is a few hundred objects.
  ``PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM`` remains the appropriate terminal for
  any attempt to read a field claim out of these numbers.
* The games are finite and exactly solvable.  Nothing here transfers to a
  domain where re-derivation is not cheap; the crossover numbers are about a
  world in which re-induction costs a bounded, known amount.

Parents: truth maintenance systems (Doyle) and justification-based dependency
networks; dependency-directed backtracking; program slicing and dynamic
dependence graphs; delta debugging and leave-one-out ablation as a general
attribution device; database view maintenance.  No novelty is claimed for any
of them, and the redundant-support blind spot recorded here is a known
limitation of leave-one-out attribution, not a discovery.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable, Sequence

from games import SubtractionGame
from methods import GrundyRule, GrundyRuleLanguage
from prereg import Commitment, commit
from scaling import (
    INDEX_ENTRY_BYTES,
    SPARSE_FRACTION,
    CheckStatus,
    CompetenceObject,
    CompetenceStore,
    ResourceRecord,
    RevisionRecord,
    TouchLedger,
    fit_loglog,
    record_from_ledger,
)

__all__ = [
    "DEPEND_PLAN",
    "COMMITMENT",
    "LANGUAGE",
    "EvidenceBlockSpec",
    "DependFamily",
    "DependCatalogue",
    "RevocationStep",
    "DependencyGraphRecord",
    "build_catalogue",
    "populate_store",
    "family_order",
    "induce_from_blocks",
    "loo_dependency_edges",
    "oracle_edges",
    "oracle_changed_methods",
    "joint_witnesses",
    "redundant_support_methods",
    "score_graph",
    "block_observations",
    "INDUCTION_EXPANSIONS",
    "registered_roles",
    "revocation_schedule",
    "declared_edges",
    "all_pairs_edges",
    "block_positions",
    "rule_of_payload",
    "fit_loglog",
    "CheckStatus",
    "CompetenceStore",
    "ResourceRecord",
    "RevisionRecord",
    "TouchLedger",
    "record_from_ledger",
    "INDEX_ENTRY_BYTES",
    "SPARSE_FRACTION",
]


# --------------------------------------------------------------------------
# the frozen plan
# --------------------------------------------------------------------------

#: Frozen before any outcome.  Editing any value changes the commitment and
#: therefore changes the family order, which is what makes analysis drift
#: mechanically visible (CL-D4).  The registered role-selection rules below are
#: deterministic functions of this plan: a third party re-derives the same
#: families from the same hash without trusting anybody's word for it.
DEPEND_PLAN: dict[str, Any] = {
    "protocol": "COGNITIVE_LADDER_PROTOCOL_V1",
    "rung": "CL-D-E3 dependency discovery under evidence withdrawal",
    "base_families": 16,
    "multipliers": [1, 2, 5, 10],
    "probe_family_moves": [1, 3, 4],
    "evidence_blocks": 4,
    "evidence_block_size": 4,
    "move_alphabet": 10,
    "move_set_max_size": 5,
    "language": {"max_preperiod": 6, "max_period": 12, "max_value": 8},
    "ground_truth": (
        "leave-one-out re-induction. Evidence block b is a TRUE dependency of method m "
        "iff inducing m from the live evidence WITHOUT b yields a different rule (or no "
        "rule). Decidable, computed by brute force, never given to any arm."
    ),
    "second_ground_truth": (
        "joint witnesses. A minimal set of blocks whose SIMULTANEOUS removal changes the "
        "rule while no single member's removal does. Every such witness of size >= 2 is a "
        "false negative of the leave-one-out oracle and is reported as a limitation of the "
        "discovery method rather than corrected for."
    ),
    "arms": [
        "learned_dependency_arm",
        "lazy_learner_arm",
        "full_recomputation_parent",
        "declared_supports_parent",
        "co_occurrence_parent",
        "all_evidence_parent",
    ],
    "family_selection_rules": {
        "REDUNDANT": (
            "first family in the committed order whose leave-one-out dependency set is "
            "EMPTY and which has a minimal joint witness of size exactly 2"
        ),
        "GLOBAL": (
            "first remaining family every one of whose blocks is a leave-one-out "
            "dependency: a genuinely global dependency, so locality is not guaranteed "
            "by construction"
        ),
        "ABOVE_SPAN": (
            "first remaining family with a leave-one-out dependency block lying ENTIRELY "
            "above the induced rule's table span (preperiod + period). Positional "
            "co-occurrence cannot see such a block."
        ),
        "INERT": (
            "first remaining family holding both a non-dependency block and a dependency "
            "block. Its non-dependency block is the never-load-bearing revocation."
        ),
    },
    "revocation_schedule": [
        "NEVER_LOAD_BEARING: INERT family, lowest-index non-dependency block. "
        "Every arm should do nothing.",
        "LOAD_BEARING_BELOW_SPAN: GLOBAL family, block 0. Load-bearing and positionally "
        "visible; every arm that links anything should catch it.",
        "LOAD_BEARING_ABOVE_SPAN: ABOVE_SPAN family, its lowest-index dependency block "
        "lying entirely above the rule's table span.",
        "REDUNDANT_FIRST: REDUNDANT family, the HIGHER-index block of its size-2 joint "
        "witness. Individually unnecessary: nothing should change.",
        "REDUNDANT_SECOND: REDUNDANT family, the LOWER-index block of that witness, "
        "revoked after the first. The rule now changes, and any cached leave-one-out "
        "graph says it should not.",
    ],
    "endpoints": [
        "dependency-graph precision and recall against the leave-one-out oracle, per arm",
        "stale survivors (true dependents left live) counted exactly, never summed with",
        "collateral invalidations (non-dependents killed) counted exactly",
        "discovery/build work, revocation work",
        "crossover number of revocations at which learned_dependency_arm total work falls "
        "below lazy_learner_arm and below full_recomputation_parent",
        "redundant-support methods invisible to leave-one-out, counted at every scale",
    ],
    "sparse_fraction": SPARSE_FRACTION,
    "index_entry_bytes": INDEX_ENTRY_BYTES,
    "loglog_residual_threshold": 0.05,
    "fit_basis": "log10, ordinary least squares, 4 points, 2 free parameters",
}

COMMITMENT: Commitment = commit(DEPEND_PLAN)

LANGUAGE = GrundyRuleLanguage(
    max_preperiod=DEPEND_PLAN["language"]["max_preperiod"],
    max_period=DEPEND_PLAN["language"]["max_period"],
    max_value=DEPEND_PLAN["language"]["max_value"],
)

#: Number of expansions one induction costs in this language.  It is a constant
#: because :meth:`GrundyRuleLanguage.induce` visits every ``(q, p)`` shape; it
#: is derived here rather than asserted so that a change to the language grid
#: changes the charge automatically.
INDUCTION_EXPANSIONS = LANGUAGE.max_period * (LANGUAGE.max_preperiod + 1)


# --------------------------------------------------------------------------
# the commitment-derived family order
# --------------------------------------------------------------------------


def _combinations(pool: tuple[int, ...], size: int) -> list[tuple[int, ...]]:
    out: list[tuple[int, ...]] = []

    def rec(start: int, acc: tuple[int, ...]) -> None:
        if len(acc) == size:
            out.append(acc)
            return
        for i in range(start, len(pool)):
            rec(i + 1, acc + (pool[i],))

    rec(0, ())
    return out


@lru_cache(maxsize=None)
def family_order() -> tuple[tuple[int, ...], ...]:
    """The frozen family order: probe family first, then a committed shuffle.

    Taking the first ``F`` of one frozen order makes the family set at each
    scale a superset of the set at the scale below.  Nested scales matter: if
    each scale drew its own families, a change in any endpoint between scales
    could be a change of families rather than a change of ``N``.

    The shuffle is a deterministic function of ``COMMITMENT``.  Because the
    registered roles below are "the first family in this order satisfying
    <property>", the hostile families are not hand-picked; they are whatever
    the plan hash produced, and a reviewer re-derives them from the hash.
    """
    import random

    alphabet = DEPEND_PLAN["move_alphabet"]
    max_size = DEPEND_PLAN["move_set_max_size"]
    candidates: list[tuple[int, ...]] = []
    for size in range(1, max_size + 1):
        candidates.extend(_combinations(tuple(range(1, alphabet + 1)), size))
    probe = tuple(DEPEND_PLAN["probe_family_moves"])
    rest = [m for m in candidates if m != probe]
    rng = random.Random(COMMITMENT.stream("depend-family-order-v1") % (2**63))
    rng.shuffle(rest)
    return (probe,) + tuple(rest)


# --------------------------------------------------------------------------
# the catalogue
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceBlockSpec:
    """One evidence block: an addressable, revocable unit of observation.

    A block is an object, not an annotation.  Revocation is applied to it, so
    it has to have an identity, and its identity is what an arm's dependency
    graph has to be about.
    """

    block_id: str
    family_id: str
    index: int
    observations: tuple[tuple[int, int], ...]

    @property
    def positions(self) -> tuple[int, ...]:
        return tuple(n for n, _ in self.observations)


@dataclass(frozen=True)
class DependFamily:
    """One family: its evidence blocks and the rule induced from all of them.

    ``relation`` is positional only -- ``probe``, ``related`` or ``distractor``
    exactly as in ``scaling.py``.  It deliberately does **not** encode the
    registered role, because the roles are outcomes of the oracle and an arm
    that could read a role off the store would be reading the answer.
    """

    family_id: str
    moves: tuple[int, ...]
    relation: str
    blocks: tuple[EvidenceBlockSpec, ...]
    rule: GrundyRule

    @property
    def method_id(self) -> str:
        return f"M:{self.family_id}"

    @property
    def block_ids(self) -> tuple[str, ...]:
        return tuple(b.block_id for b in self.blocks)

    @property
    def span(self) -> int:
        """The induced rule's table span, ``preperiod + period``.

        The positional heuristic parent uses this and nothing else about the
        rule, so it is named here rather than recomputed in the arm.
        """
        return self.rule.preperiod + self.rule.period


@dataclass(frozen=True)
class DependCatalogue:
    """The frozen contents of the persistent state at one scale."""

    scale_id: str
    multiplier: int
    families: tuple[DependFamily, ...]

    @property
    def probe(self) -> DependFamily:
        return self.families[0]

    @property
    def n_blocks(self) -> int:
        return sum(len(f.blocks) for f in self.families)

    def family_of_method(self, method_id: str) -> DependFamily:
        for family in self.families:
            if family.method_id == method_id:
                return family
        raise KeyError(method_id)

    def family_of_block(self, block_id: str) -> DependFamily:
        for family in self.families:
            if block_id in family.block_ids:
                return family
        raise KeyError(block_id)


def _blocks_for(family_id: str, table: Sequence[int]) -> tuple[EvidenceBlockSpec, ...]:
    count = DEPEND_PLAN["evidence_blocks"]
    size = DEPEND_PLAN["evidence_block_size"]
    return tuple(
        EvidenceBlockSpec(
            block_id=f"S:{family_id}:b{i}",
            family_id=family_id,
            index=i,
            observations=tuple((n, table[n]) for n in range(i * size, (i + 1) * size)),
        )
        for i in range(count)
    )


def _family(moves: tuple[int, ...], relation: str) -> DependFamily:
    game = SubtractionGame(moves)
    width = DEPEND_PLAN["evidence_blocks"] * DEPEND_PLAN["evidence_block_size"]
    table = game.grundy_upto(width - 1)
    blocks = _blocks_for(game.family_id, table)
    rule = induce_from_blocks(blocks)
    if rule is None:  # pragma: no cover -- the language always covers 0..15
        raise AssertionError(f"no hypothesis in {LANGUAGE.language_id} fits {moves}")
    return DependFamily(
        family_id=game.family_id,
        moves=moves,
        relation=relation,
        blocks=blocks,
        rule=rule,
    )


@lru_cache(maxsize=None)
def _all_families(count: int) -> tuple[DependFamily, ...]:
    order = family_order()
    if count > len(order):
        raise ValueError(f"only {len(order)} registered families; asked for {count}")
    out = []
    for i, moves in enumerate(order[:count]):
        if i == 0:
            relation = "probe"
        elif i <= max(1, count // 10):
            relation = "related"
        else:
            relation = "distractor"
        out.append(_family(moves, relation))
    return tuple(out)


@lru_cache(maxsize=None)
def build_catalogue(multiplier: int) -> DependCatalogue:
    """The catalogue at scale ``multiplier``; nested in the smaller scales."""
    count = DEPEND_PLAN["base_families"] * multiplier
    return DependCatalogue(
        scale_id=f"{multiplier}x",
        multiplier=multiplier,
        families=_all_families(count),
    )


def populate_store(catalogue: DependCatalogue) -> CompetenceStore:
    """Build the block-and-method store for one catalogue.

    Every arm receives a store built by this one function, so ``N``, the byte
    totals and the *declared* candidate sets are identical across arms and any
    difference in the reported numbers is a difference of discovery
    architecture and nothing else.

    The declared ``supports`` of a method are its **candidate** evidence blocks
    -- the blocks the induction was actually run over.  They are declared
    because they must be: nothing could be induced without them.  They are NOT
    the dependency set, and the distance between the two is the experiment.
    """
    store = CompetenceStore(f"depend@{catalogue.scale_id}")
    for family in catalogue.families:
        for block in family.blocks:
            store.add_support(
                block.block_id,
                family.family_id,
                {
                    "kind": "evidence_block",
                    "family": family.family_id,
                    "index": block.index,
                    "observations": [list(o) for o in block.observations],
                },
            )
        store.add_competence(
            family.family_id,
            family.rule,
            family.block_ids,
            relation=family.relation,
        )
    return store


def block_positions(obj: CompetenceObject) -> tuple[int, ...]:
    """Positions an evidence block mentions, read off its stored payload."""
    return tuple(int(o[0]) for o in obj.payload["observations"])


def block_observations(obj: CompetenceObject) -> tuple[tuple[int, int], ...]:
    return tuple((int(o[0]), int(o[1])) for o in obj.payload["observations"])


def rule_of_payload(obj: CompetenceObject) -> GrundyRule:
    """Rebuild the periodic rule from a stored method payload.

    The store persists the rule as plain data, never as a live object, which is
    what a real restart would hand back.
    """
    return GrundyRule(
        preperiod=int(obj.payload["preperiod"]),
        period=int(obj.payload["period"]),
        values=tuple(int(v) for v in obj.payload["values"]),
    )


def induce_from_blocks(blocks: Iterable[EvidenceBlockSpec]) -> GrundyRule | None:
    """Induce from a set of blocks.  Deterministic and order-independent."""
    evidence = sorted({obs for b in blocks for obs in b.observations})
    return LANGUAGE.induce(tuple(evidence))


# --------------------------------------------------------------------------
# ground truth, for the scorer only
# --------------------------------------------------------------------------
#
# Everything from here to the end of this section is the oracle.  No arm calls
# any of it; ``test_depend.py`` enforces that by source inspection, the way
# ``test_scaling.py`` enforces the ``true_cone`` separation.  The functions are
# memoised because the scorer runs them many times over nested catalogues; the
# memoisation is a property of the scorer and charges nothing to any arm.


@lru_cache(maxsize=None)
def _induce_cached(evidence: tuple[tuple[int, int], ...]) -> GrundyRule | None:
    return LANGUAGE.induce(evidence)


def _rule_from_ids(family: DependFamily, live: frozenset[str]) -> GrundyRule | None:
    evidence = tuple(
        sorted({obs for b in family.blocks if b.block_id in live for obs in b.observations})
    )
    return _induce_cached(evidence)


@lru_cache(maxsize=None)
def loo_dependency_edges(family: DependFamily) -> frozenset[str]:
    """The true dependency set of ``family``'s method, by leave-one-out.

    Block ``b`` is in the set iff inducing without ``b`` yields a different
    rule (or no rule).  This is the oracle of ``DEPEND_PLAN["ground_truth"]``.
    """
    everything = frozenset(family.block_ids)
    base = _rule_from_ids(family, everything)
    out = set()
    for block_id in family.block_ids:
        if _rule_from_ids(family, everything - {block_id}) != base:
            out.add(block_id)
    return frozenset(out)


@lru_cache(maxsize=None)
def joint_witnesses(family: DependFamily) -> tuple[tuple[str, ...], ...]:
    """Minimal sets of blocks whose SIMULTANEOUS removal changes the rule.

    Brute force over all subsets, keeping only the minimal ones under set
    inclusion.  A witness of size one is just a leave-one-out dependency.  A
    witness of size two or more is a **false negative of the oracle**: the
    method genuinely rests on that set of blocks, and no leave-one-out
    procedure can see it.  Reporting these is not a correction to the
    experiment, it is the experiment's headline limitation.
    """
    ids = family.block_ids
    everything = frozenset(ids)
    base = _rule_from_ids(family, everything)
    minimal: list[tuple[str, ...]] = []
    for size in range(1, len(ids) + 1):
        for combo in _combinations(tuple(range(len(ids))), size):
            candidate = frozenset(ids[i] for i in combo)
            if any(set(w) <= candidate for w in minimal):
                continue
            if _rule_from_ids(family, everything - candidate) != base:
                minimal.append(tuple(sorted(candidate)))
    return tuple(minimal)


def redundant_support_methods(catalogue: DependCatalogue) -> tuple[str, ...]:
    """Methods whose support is invisible to leave-one-out.

    A method qualifies when its leave-one-out dependency set is empty while a
    joint witness of size two or more exists: the rule rests on evidence, and
    the oracle reports that it rests on nothing.
    """
    out = []
    for family in catalogue.families:
        if loo_dependency_edges(family):
            continue
        if any(len(w) >= 2 for w in joint_witnesses(family)):
            out.append(family.method_id)
    return tuple(out)


@lru_cache(maxsize=None)
def oracle_edges(catalogue: DependCatalogue) -> frozenset[tuple[str, str]]:
    """The complete true dependency graph as ``(block_id, method_id)`` edges."""
    return frozenset(
        (block_id, family.method_id)
        for family in catalogue.families
        for block_id in loo_dependency_edges(family)
    )


def oracle_changed_methods(
    catalogue: DependCatalogue,
    live_before: frozenset[str],
    live_after: frozenset[str],
) -> frozenset[str]:
    """Methods whose induced rule genuinely changes when evidence is withdrawn.

    The operational statement of "withdrawing evidence invalidates exactly the
    right things", evaluated against the live evidence rather than against the
    original evidence, so a schedule of successive revocations is scored
    correctly at every step.
    """
    withdrawn = live_before - live_after
    changed = set()
    for family in catalogue.families:
        if not withdrawn & set(family.block_ids):
            continue
        if _rule_from_ids(family, live_after) != _rule_from_ids(family, live_before):
            changed.add(family.method_id)
    return frozenset(changed)


def declared_edges(catalogue: DependCatalogue) -> frozenset[tuple[str, str]]:
    """The DECLARED candidate graph: the gift the prior pilot was given.

    Reported as a ceiling, never as ground truth.  Every true edge is in here
    (a rule cannot depend on evidence it was never shown), so the declared
    graph has recall ``1.0`` for free and its only interesting coordinate is
    precision.
    """
    return frozenset(
        (block_id, family.method_id)
        for family in catalogue.families
        for block_id in family.block_ids
    )


def all_pairs_edges(catalogue: DependCatalogue) -> frozenset[tuple[str, str]]:
    """Every block against every method: the conservative baseline's graph."""
    blocks = [b.block_id for f in catalogue.families for b in f.blocks]
    return frozenset((b, f.method_id) for b in blocks for f in catalogue.families)


# --------------------------------------------------------------------------
# the registered roles and the revocation schedule
# --------------------------------------------------------------------------


@lru_cache(maxsize=None)
def registered_roles(catalogue: DependCatalogue) -> dict[str, str]:
    """Assign the four registered roles by the rules frozen in the plan.

    Each rule is "the first family in the committed order, distinct from those
    already assigned, satisfying <property>".  The properties are facts about
    the world computed by the oracle; the *selection* therefore happens in the
    scorer, before any arm runs, and is a deterministic function of the plan
    hash.  Nothing about an arm's behaviour can influence which families are
    chosen, which is the property that makes the choice pre-registered rather
    than post hoc.
    """
    taken: set[str] = set()
    roles: dict[str, str] = {}

    def claim(role: str, predicate) -> None:
        for family in catalogue.families:
            if family.family_id in taken:
                continue
            if predicate(family):
                roles[role] = family.family_id
                taken.add(family.family_id)
                return
        raise AssertionError(
            f"no family in the {catalogue.scale_id} catalogue fills the registered role "
            f"{role}; the world is too small for the frozen schedule and the rung must "
            "report PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM rather than substitute a family"
        )

    def redundant(f: DependFamily) -> bool:
        return not loo_dependency_edges(f) and any(
            len(w) == 2 for w in joint_witnesses(f)
        )

    def global_dep(f: DependFamily) -> bool:
        return loo_dependency_edges(f) == frozenset(f.block_ids)

    def above_span(f: DependFamily) -> bool:
        deps = loo_dependency_edges(f)
        return any(
            b.block_id in deps and min(b.positions) >= f.span for b in f.blocks
        )

    def inert(f: DependFamily) -> bool:
        deps = loo_dependency_edges(f)
        return bool(deps) and len(deps) < len(f.blocks)

    claim("REDUNDANT", redundant)
    claim("GLOBAL", global_dep)
    claim("ABOVE_SPAN", above_span)
    claim("INERT", inert)
    return roles


@dataclass(frozen=True)
class RevocationStep:
    """One registered revocation, named before the numbers exist."""

    step_id: str
    role: str
    family_id: str
    block_ids: tuple[str, ...]
    intent: str


@lru_cache(maxsize=None)
def revocation_schedule(catalogue: DependCatalogue) -> tuple[RevocationStep, ...]:
    """The five registered revocations, in the order they are applied.

    The order is part of the registration.  The two no-op steps precede the
    breaking step on the same family, so a step's lesson is never contaminated
    by an earlier step having already invalidated the method it is about.  No
    two roles share a family, so no two families interact at all.
    """
    roles = registered_roles(catalogue)
    by_id = {f.family_id: f for f in catalogue.families}

    inert_family = by_id[roles["INERT"]]
    inert_deps = loo_dependency_edges(inert_family)
    inert_block = next(
        b.block_id for b in inert_family.blocks if b.block_id not in inert_deps
    )

    global_family = by_id[roles["GLOBAL"]]

    above_family = by_id[roles["ABOVE_SPAN"]]
    above_deps = loo_dependency_edges(above_family)
    above_block = next(
        b.block_id
        for b in above_family.blocks
        if b.block_id in above_deps and min(b.positions) >= above_family.span
    )

    redundant_family = by_id[roles["REDUNDANT"]]
    witness = next(w for w in joint_witnesses(redundant_family) if len(w) == 2)
    order = {b.block_id: b.index for b in redundant_family.blocks}
    first, second = sorted(witness, key=lambda b: -order[b])

    return (
        RevocationStep(
            step_id="NEVER_LOAD_BEARING",
            role="INERT",
            family_id=inert_family.family_id,
            block_ids=(inert_block,),
            intent=(
                "evidence that was never load-bearing. The rule does not change. Every "
                "arm should do nothing; an arm that invalidates here is wasting work."
            ),
        ),
        RevocationStep(
            step_id="LOAD_BEARING_BELOW_SPAN",
            role="GLOBAL",
            family_id=global_family.family_id,
            block_ids=(global_family.blocks[0].block_id,),
            intent=(
                "a load-bearing block of a method with a GENUINELY GLOBAL dependency: "
                "every one of its blocks is a true dependency, so locality is not "
                "guaranteed by construction. The block is positionally visible."
            ),
        ),
        RevocationStep(
            step_id="LOAD_BEARING_ABOVE_SPAN",
            role="ABOVE_SPAN",
            family_id=above_family.family_id,
            block_ids=(above_block,),
            intent=(
                "a load-bearing block lying entirely above the induced rule's table "
                "span. A positional co-occurrence heuristic cannot see it, and missing "
                "it leaves a stale survivor rather than merely wasting work."
            ),
        ),
        RevocationStep(
            step_id="REDUNDANT_FIRST",
            role="REDUNDANT",
            family_id=redundant_family.family_id,
            block_ids=(first,),
            intent=(
                "the higher-index block of a redundant pair. It is individually "
                "unnecessary: the rule does not change and nothing should be "
                "invalidated."
            ),
        ),
        RevocationStep(
            step_id="REDUNDANT_SECOND",
            role="REDUNDANT",
            family_id=redundant_family.family_id,
            block_ids=(second,),
            intent=(
                "the other half of the redundant pair, withdrawn after the first. The "
                "rule now changes. A dependency graph learned by leave-one-out at "
                "acquisition time says this block has no dependents, because at "
                "acquisition time it did not -- and the belief is left standing."
            ),
        ),
    )


# --------------------------------------------------------------------------
# the dependency-graph record
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class DependencyGraphRecord:
    """One arm's believed dependency graph, scored against the oracle.

    Precision and recall follow the same conventions as
    ``RevisionRecord.dependency_precision`` so a reader can move between the
    graph endpoint and the revocation endpoint without a translation table.

    ``disclosure_work`` is the work the arm spent producing this graph when
    asked for it.  For an arm that stores a graph it is a handful of index
    probes.  For an arm that holds none and re-derives on demand it is the
    whole discovery cost, charged here rather than hidden -- which is exactly
    why "cheap to build" is only true of an arm nobody ever asks.
    """

    arm_id: str
    scale_id: str
    n_true_edges: int
    n_believed_edges: int
    n_correct_edges: int
    disclosure_work: int
    missing_edges: tuple[tuple[str, str], ...]
    extra_edges: tuple[tuple[str, str], ...]
    edge_universe: int

    @property
    def precision(self) -> float:
        if self.n_believed_edges == 0:
            return 1.0 if self.n_true_edges == 0 else 0.0
        return self.n_correct_edges / self.n_believed_edges

    @property
    def recall(self) -> float:
        if self.n_true_edges == 0:
            return 1.0
        return self.n_correct_edges / self.n_true_edges

    @property
    def exact(self) -> bool:
        return not self.missing_edges and not self.extra_edges

    def as_dict(self) -> dict:
        return {
            "arm_id": self.arm_id,
            "scale_id": self.scale_id,
            "true_edges": self.n_true_edges,
            "believed_edges": self.n_believed_edges,
            "correct_edges": self.n_correct_edges,
            "edge_universe": self.edge_universe,
            "precision": round(self.precision, 6),
            "recall": round(self.recall, 6),
            "exact": self.exact,
            "disclosure_work": self.disclosure_work,
            "missed_edges": len(self.missing_edges),
            "spurious_edges": len(self.extra_edges),
            "missed_edge_sample": [list(e) for e in self.missing_edges[:8]],
            "spurious_edge_sample": [list(e) for e in self.extra_edges[:8]],
        }


def score_graph(
    arm_id: str,
    catalogue: DependCatalogue,
    believed: Iterable[tuple[str, str]],
    disclosure_work: int,
    *,
    sample_cap: int = 8,
) -> DependencyGraphRecord:
    """Score a believed graph against the leave-one-out oracle.

    The scorer, and the only place ``oracle_edges`` is consulted for the graph
    endpoint.  ``missing_edges`` are the dangerous direction (a dependency the
    arm does not know about) and ``extra_edges`` the wasteful one; they are
    kept apart here for the same reason stale survivors and collateral
    invalidations are kept apart in the revocation endpoint.
    """
    truth = oracle_edges(catalogue)
    claimed = frozenset(believed)
    missing = tuple(sorted(truth - claimed))
    extra = tuple(sorted(claimed - truth))
    return DependencyGraphRecord(
        arm_id=arm_id,
        scale_id=catalogue.scale_id,
        n_true_edges=len(truth),
        n_believed_edges=len(claimed),
        n_correct_edges=len(truth & claimed),
        disclosure_work=disclosure_work,
        missing_edges=missing[: sample_cap * 4],
        extra_edges=extra[: sample_cap * 4],
        edge_universe=len(all_pairs_edges(catalogue)),
    )
