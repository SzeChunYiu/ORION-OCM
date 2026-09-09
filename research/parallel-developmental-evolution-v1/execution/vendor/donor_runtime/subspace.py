"""Discovered indexing: which part of memory is relevant, when nothing says so?

The prior scaling pilot (``scaling.py``, ``scaling_arms.py``) returned
``PARENT_SUFFICIENT`` and it was right to.  An ordinary hash index matched the
machine arm *exactly* on ``k``, on ``k/N`` and on query work, because the index
key was the **family identity** and the catalogue handed that identity to every
arm with the query.  Cheap lookup under a supplied key is a property of the
key.  Nothing about cognition was measured, and the receipt said so.

This module removes the gift.  A query arrives as a set of **observations** --
``(position, label)`` pairs drawn from some subtraction family -- and the family
identity is **not** included.  The store holds ``N`` persistent objects, among
them learned periodic Grundy rules over other families.  The machine has to work
out which stored method, *if any*, applies, and only then answer fresh positions
with it.  Stated without project vocabulary:

    how does a system discover which part of its memory is relevant,
    when nothing tells it?

What is under test, and what is not
-----------------------------------

The treatment is a **discovered indexing feature**.  An arm may index its store
on a feature of a method's own predictions -- the vector of predicted labels at
some set of registered probe positions -- and it must *choose* that set from a
registered, enumerable feature language.  The right feature is not handed to it.
``|F|`` and the bits of prior it represents are computed exactly, by the same
discipline ``methods.py`` applies to method languages: a feature language chosen
after seeing the answer is the first attack a reviewer makes.

The scientifically interesting part is what growth does to a feature.  A feature
that separates eight stored methods will not separate two hundred and forty:
distinct methods start sharing a feature image, buckets grow, and a lookup that
was a single read becomes a scan of a bucket.  The endpoint is therefore not
"is the arm sparse" but **does the arm notice**, and what does noticing cost.
Every re-index is charged as ``index_maintenance_work`` and never folded into
query work.

This is also where the scaling question meets the escalation question.  When no
feature in the registered language separates two stored methods that *disagree*
on a query position, that is an exhibited pair -- the same construction
``escalation.identifiability_witness`` uses -- and the correct report is a
**witnessed obstruction**, not a timeout.  :func:`feature_identifiability_witness`
returns that pair or ``None``, and a third party holding the receipt can
recompute both images and both predictions and check it.

The strongest parent, named before the run
------------------------------------------

``signature_hash_parent`` is an ordinary content-addressed inverted index on a
**hand-specified** prediction prefix, given a prefix exactly as long as the
largest feature the discovering arm is allowed to use, so the comparison is
never about feature size.  It is expected to be **sufficient whenever the
hand-specified prefix happens to be adequate**, and at the small scales it is
expected to *beat* the discovering arm, because it pays no search.  If it
matches the discovering arm on every endpoint the honest terminal is
``PARENT_SUFFICIENT`` and it is the headline, not a caveat.

``oracle_key_parent`` is the ceiling: it is handed the family identity, which is
the old, gifted setting, and it should win on query work.  Its presence is the
standing reminder of how much of the prior pilot's result was the key.

Discipline inherited verbatim
-----------------------------

``TouchLedger``, ``CompetenceStore``, ``ResourceRecord``, ``record_from_ledger``,
``CheckStatus`` and ``fit_loglog`` are imported from ``scaling.py`` rather than
re-implemented.  ``k`` is counted by instrumented touches only; an
uninstrumented accessor poisons its ledger and the resulting record carries
``CANNOT_CHECK`` with ``k = None``; index build and maintenance are charged
separately from query work.  Re-deriving those meters here would let this
module's numbers drift from the previous pilot's, and a receipt that cannot be
read against its predecessor is worth less than one that can.

Correctness is reported beside every ``k``, without exception.  The prior pilot
already produced the cautionary case: ``cache_parent`` was the sparsest arm in
the sweep (``k = 0``) and answered nothing.  An arm that is sparse because it
declines to commit is not better, and the query stream here contains
**absent-family** queries precisely so that "answer nothing" and "answer
everything" are both punished: a query drawn from a family no stored method
serves must be met with ``NO_METHOD_APPLIES``.

Limitations, stated before any number
-------------------------------------

* The observation set handed with a query is exactly identifying **within the
  registered method language**: it covers ``max_preperiod + max_period``
  positions, so two stored rules are observation-indistinguishable if and only
  if they are the same rule.  A shorter observation set would make the retrieval
  problem itself ambiguous.  That harder problem is not run here.
* The families in the store are filtered for extrapolation admissibility
  (CL-D1(b)): a family whose induced rule does not reproduce the true Grundy
  value at every registered query position is rejected from the draw, as
  ``games.eventual_period`` already rejects a family whose period is not
  witnessed.  The count of rejected candidates is reported.
* ``N`` here is a few hundred.  ``PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM`` remains
  the correct terminal for any field claim read out of these numbers.

Parents: content-addressed and inverted indexes; locality-sensitive hashing and
approximate nearest-neighbour retrieval; feature selection for hash keys;
version-space learning for the exact counting.  No novelty is claimed for any of
them.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable, Mapping, Sequence

from games import SubtractionGame
from methods import Admissibility, BitsAccounting, GrundyRule, GrundyRuleLanguage
from prereg import Commitment, canonical_json, commit
from scaling import (
    INDEX_ENTRY_BYTES,
    SHARED_SUPPORT_ID,
    SPARSE_FRACTION,
    CheckStatus,
    CompetenceObject,
    CompetenceStore,
    LogLogFit,
    ResourceRecord,
    TouchLedger,
    certify,
    fit_loglog,
    record_from_ledger,
)

__all__ = [
    "SUBSPACE_PLAN",
    "COMMITMENT",
    "LANGUAGE",
    "OBSERVATION_WINDOW",
    "MAX_BUCKET_SIZE",
    "SIGNATURE_PREFIX",
    "Feature",
    "FeatureLanguage",
    "FeatureAdequacy",
    "RuleSpec",
    "SubspaceCatalogue",
    "Query",
    "QueryOutcome",
    "feature_language",
    "feature_pool",
    "query_positions",
    "admissible_rules",
    "build_catalogue",
    "install_objects",
    "populate_store",
    "grow_store",
    "query_stream",
    "bucket_map",
    "adequacy_of",
    "smallest_adequate_feature",
    "feature_identifiability_witness",
    "feature_bits",
    "rule_admissibility",
    "observations_of",
    "predicted_vector",
    "rule_of",
]


# --------------------------------------------------------------------------
# the frozen plan
# --------------------------------------------------------------------------

#: Frozen before any outcome.  Every draw in this module -- the feature pool,
#: the query positions, the order in which rules enter the store, which
#: families the queries are drawn from -- is a deterministic function of
#: ``sha256`` of this dictionary.  Editing any value changes the commitment and
#: therefore changes the experiment, which is what makes analysis drift
#: mechanically visible rather than a matter of trust (CL-D4).
#:
#: ``hand_specified_prefix_length`` equals ``feature_pool_size`` on purpose: the
#: strongest realistic parent is given a hand-specified prediction prefix of
#: exactly the length of the largest feature the discovering arm may choose, so
#: no part of any separation can be attributed to the parent having been given
#: a smaller budget.
SUBSPACE_PLAN: dict[str, Any] = {
    "protocol": "COGNITIVE_LADDER_PROTOCOL_V1",
    "companion_spec": "COGNITIVE_LADDER_SCALING_V1",
    "rung": "CL-S1 discovered indexing feature under persistent-store growth",
    "experiment": "SUBSPACE_E1",
    "base_methods": 8,
    "multipliers": [1, 3, 10, 30],
    "move_alphabet": 20,
    "move_set_max_size": 4,
    "language": {"max_preperiod": 10, "max_period": 20, "max_value": 12},
    "observation_window": 30,
    "query_position_low": 40,
    "query_position_high": 96,
    "query_positions": 5,
    "in_store_query_families": 6,
    "absent_query_families": 4,
    "held_out_rules": 12,
    "feature_pool_size": 9,
    "feature_language": "every non-empty subset of the registered feature pool",
    "max_bucket_size": 4,
    "hand_specified_prefix_length": 9,
    "arms": [
        "discovering_arm",
        "fixed_feature_arm",
        "oracle_key_parent",
        "exact_scan_parent",
        "signature_hash_parent",
        "nearest_neighbour_parent",
    ],
    "endpoints": [
        "k(N)",
        "k/N",
        "query_work(N)",
        "index_build_work + index_maintenance_work",
        "persistent_bytes(N) = store_bytes + index_bytes",
        "answer correctness, in-store and absent-family separately",
        "collision rate and max bucket size of the chosen feature",
        "number of re-indexes",
        "crossover query count against exact_scan_parent",
    ],
    "sparse_fraction": SPARSE_FRACTION,
    "index_entry_bytes": INDEX_ENTRY_BYTES,
    "loglog_residual_threshold": 0.05,
    "fit_basis": "log10, ordinary least squares, 4 points, 2 free parameters",
}

COMMITMENT: Commitment = commit(SUBSPACE_PLAN)

LANGUAGE = GrundyRuleLanguage(
    max_preperiod=SUBSPACE_PLAN["language"]["max_preperiod"],
    max_period=SUBSPACE_PLAN["language"]["max_period"],
    max_value=SUBSPACE_PLAN["language"]["max_value"],
)

#: The number of observation positions handed with a query, ``0 .. W-1``.  It
#: equals ``max_preperiod + max_period``, so the observations pin every slot of
#: any hypothesis in ``LANGUAGE``: two stored rules are observation-equivalent
#: if and only if they are equal.  Deliberate, and a limitation.
OBSERVATION_WINDOW: int = SUBSPACE_PLAN["observation_window"]

#: A feature is ADEQUATE for a store when no bucket it induces holds more than
#: this many methods.  Declared before any outcome, because a threshold chosen
#: after seeing the buckets is not a threshold.  ``k`` for an arm holding an
#: adequate feature is bounded by this constant independently of ``N``; that
#: bound is the whole sparsity claim and it is the arm's job to keep it true.
MAX_BUCKET_SIZE: int = SUBSPACE_PLAN["max_bucket_size"]

#: The hand-specified feature: the first ``L`` predicted labels.  This is what
#: an ordinary content-addressed index keys on, and position ``0`` is in it
#: because a prefix contains its first element -- every subtraction game has
#: ``G(0) = 0``, so the parent's key wastes one coordinate on a constant.  That
#: is a real property of hand-specified prefixes and it is not corrected for.
SIGNATURE_PREFIX: tuple[int, ...] = tuple(
    range(SUBSPACE_PLAN["hand_specified_prefix_length"])
)


def _stream_rng(label: str) -> random.Random:
    return random.Random(COMMITMENT.stream(label) % (2**63))


# --------------------------------------------------------------------------
# the feature language
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Feature:
    """A set of observation positions to key an index on.

    The image of a method under a feature is the tuple of that method's own
    *predicted* labels at those positions.  Nothing about the query, the family
    identity or the truth enters it: a feature is a function of the stored
    method alone, which is what lets an index be built once and probed many
    times.
    """

    positions: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.positions:
            raise ValueError("a feature needs at least one position")
        if tuple(sorted(set(self.positions))) != self.positions:
            raise ValueError("feature positions must be sorted and distinct")

    @property
    def size(self) -> int:
        return len(self.positions)

    @property
    def feature_id(self) -> str:
        return "F(" + ",".join(str(p) for p in self.positions) + ")"

    def image(self, vector: Sequence[int]) -> tuple[int, ...]:
        """The feature image of a full observation/prediction vector."""
        return tuple(vector[p] for p in self.positions)

    def image_of_rule(self, rule: GrundyRule) -> tuple[int, ...]:
        return tuple(rule.grundy(p) for p in self.positions)

    def as_dict(self) -> dict:
        return {"feature_id": self.feature_id, "positions": list(self.positions)}


@dataclass(frozen=True)
class FeatureLanguage:
    """The registered, enumerable feature language ``FL``.

    A hypothesis is *which* observation positions to key on, and *how many*.
    The language is every non-empty subset of a registered pool of positions,
    enumerated in canonical order -- fewest positions first, then
    lexicographically -- so "the smallest adequate feature" is well defined and
    an arm's choice is deterministic rather than a matter of iteration order.

    ``size()`` is ``2**|pool| - 1`` exactly and ``prior_bits()`` is its base-two
    logarithm.  Both are reported in the receipt, by the same rule
    ``methods.GrundyRuleLanguage`` follows: the size of the space a choice was
    made in is part of the claim, not a footnote to it.
    """

    pool: tuple[int, ...]

    def __post_init__(self) -> None:
        if tuple(sorted(set(self.pool))) != self.pool:
            raise ValueError("the feature pool must be sorted and distinct")

    @property
    def language_id(self) -> str:
        return "FL(subsets of " + ",".join(str(p) for p in self.pool) + ")"

    def size(self) -> int:
        return 2 ** len(self.pool) - 1

    def prior_bits(self) -> float:
        return math.log2(self.size())

    def code_bits(self, feature: Feature) -> float:
        """``bits(F)``: a two-part code, arity then which positions.

        Uniform over arities and then uniform over the subsets of that arity.
        A code tuned to favour small features would make the discovering arm's
        choice look cheaper than it is, so the uniform one is used.
        """
        arities = len(self.pool)
        return math.log2(arities) + math.log2(
            math.comb(len(self.pool), feature.size)
        )

    @lru_cache(maxsize=None)
    def _ordered(self) -> tuple[Feature, ...]:
        out: list[Feature] = []
        for size in range(1, len(self.pool) + 1):
            out.extend(Feature(c) for c in _combinations(self.pool, size))
        return tuple(out)

    def features(self) -> tuple[Feature, ...]:
        """Canonical order: by arity, then lexicographic."""
        return self._ordered()

    def index_of(self, feature: Feature) -> int:
        return self.features().index(feature)

    def contains(self, feature: Feature) -> bool:
        return all(p in self.pool for p in feature.positions)


def _combinations(pool: tuple[int, ...], size: int) -> list[tuple[int, ...]]:
    """Sorted combinations, written out rather than imported.

    ``games.py`` and ``scaling.py`` do the same.  It keeps the enumeration
    order an explicit property of this module instead of an inherited one.
    """
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
def feature_pool() -> tuple[int, ...]:
    """The registered pool of positions a feature may key on.

    Drawn from the protected stream over the whole observation window.  It is
    not chosen: whichever positions the commitment implies are the positions
    the discovering arm has to work with, including the useless ones.  Position
    ``0`` carries ``G(0) = 0`` for every subtraction family, so a pool that
    contains it contains a coordinate with no information, and the arm has to
    discover that for itself.
    """
    rng = _stream_rng("subspace-feature-pool-v1")
    return tuple(
        sorted(rng.sample(range(OBSERVATION_WINDOW), SUBSPACE_PLAN["feature_pool_size"]))
    )


@lru_cache(maxsize=None)
def feature_language() -> FeatureLanguage:
    return FeatureLanguage(feature_pool())


@lru_cache(maxsize=None)
def query_positions() -> tuple[int, ...]:
    """The frozen positions a query asks about.

    Every one lies far above the observation window, so answering requires the
    *rule*: no arm can answer by echoing an observation it was handed.  This is
    CL-D1(b) -- extrapolation beyond training magnitude -- applied to the
    retrieval setting.
    """
    rng = _stream_rng("subspace-query-positions-v1")
    lo = SUBSPACE_PLAN["query_position_low"]
    hi = SUBSPACE_PLAN["query_position_high"]
    return tuple(sorted(rng.sample(range(lo, hi + 1), SUBSPACE_PLAN["query_positions"])))


# --------------------------------------------------------------------------
# the registered rule draw
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class RuleSpec:
    """One learned method and the family it was learned from.

    ``observations`` is the label vector over ``0 .. OBSERVATION_WINDOW-1``.  It
    is simultaneously the evidence the method was induced from, the payload of
    the method's evidence support object, and -- for a query drawn from this
    family -- the observation set the query arrives with.  Holding all three to
    one vector is what makes "identical information for every arm" checkable
    rather than asserted.
    """

    rule_index: int
    moves: tuple[int, ...]
    observations: tuple[int, ...]
    rule: GrundyRule

    @property
    def family_id(self) -> str:
        return "SUB(" + ",".join(str(m) for m in self.moves) + ")"

    @property
    def method_id(self) -> str:
        return f"M:{self.family_id}"

    @property
    def support_id(self) -> str:
        return f"S:{self.family_id}:obs"

    @property
    def support_ids(self) -> tuple[str, ...]:
        return (self.support_id, SHARED_SUPPORT_ID)

    def image(self, feature: Feature) -> tuple[int, ...]:
        return feature.image(self.observations)

    def predicts(self, position: int) -> int:
        return self.rule.grundy(position)


def observations_of(moves: Sequence[int]) -> tuple[int, ...]:
    """The exact Grundy labels of ``SUB(moves)`` over the observation window."""
    table = SubtractionGame(tuple(moves)).grundy_upto(OBSERVATION_WINDOW - 1)
    return tuple(table[: OBSERVATION_WINDOW])


def predicted_vector(rule: GrundyRule) -> tuple[int, ...]:
    """What a stored rule predicts over the observation window."""
    return tuple(rule.grundy(n) for n in range(OBSERVATION_WINDOW))


def rule_of(obj: CompetenceObject) -> GrundyRule:
    """Rebuild a rule from a stored method payload.

    The store persists data, never a live object, exactly as ``scaling_arms``
    does.  Rebuilding here rather than holding a Python reference keeps every
    arm honest about what actually crossed the persistence boundary.
    """
    return GrundyRule(
        preperiod=int(obj.payload["preperiod"]),
        period=int(obj.payload["period"]),
        values=tuple(int(v) for v in obj.payload["values"]),
    )


@dataclass(frozen=True)
class _Draw:
    """The result of the registered family filter, with its rejections."""

    specs: tuple[RuleSpec, ...]
    candidates: int
    rejected_value_out_of_language: int
    rejected_no_hypothesis: int
    rejected_extrapolation: int
    rejected_duplicate_rule: int


@lru_cache(maxsize=None)
def _draw() -> _Draw:
    """Enumerate candidate families and keep the admissible, rule-distinct ones.

    Three filters, all declared, all counted:

    * a family whose Grundy values leave the registered value range is dropped
      -- the language cannot express it and pretending otherwise would put an
      inexpressible method in the store;
    * a family whose induced rule does not reproduce the true Grundy value at
      **every** registered query position is dropped.  This is CL-D1(b)
      admissibility.  Keeping such a family would mean ``exact_scan_parent``
      -- which by construction finds the one consistent method -- could still be
      wrong, and the correctness column would then measure induction quality
      rather than retrieval;
    * a family whose observation vector duplicates one already drawn is dropped,
      so the store holds one method per *distinct rule*.  Many move sets share
      a Grundy sequence; storing all of them would put mutually
      indistinguishable methods in every bucket and the collision rate would
      measure the redundancy of subtraction games rather than the resolving
      power of a feature.

    The rejection counts are reported in the receipt.  A filter that discards
    nine candidates in ten is a fact about the world the experiment runs in, and
    hiding it would misrepresent how much of the draw was selection.
    """
    alphabet = SUBSPACE_PLAN["move_alphabet"]
    max_size = SUBSPACE_PLAN["move_set_max_size"]
    max_value = SUBSPACE_PLAN["language"]["max_value"]
    probes = query_positions()
    top = max(probes)

    candidates: list[tuple[int, ...]] = []
    for size in range(1, max_size + 1):
        candidates.extend(_combinations(tuple(range(1, alphabet + 1)), size))

    seen: set[tuple[int, ...]] = set()
    specs: list[RuleSpec] = []
    bad_value = bad_fit = bad_extrapolation = duplicate = 0
    for moves in candidates:
        table = SubtractionGame(moves).grundy_upto(top)
        observations = tuple(table[:OBSERVATION_WINDOW])
        if any(v >= max_value for v in observations):
            bad_value += 1
            continue
        rule = LANGUAGE.induce(tuple(enumerate(observations)))
        if rule is None:  # pragma: no cover -- the window pins every slot
            bad_fit += 1
            continue
        if any(rule.grundy(p) != table[p] for p in probes):
            bad_extrapolation += 1
            continue
        if observations in seen:
            duplicate += 1
            continue
        seen.add(observations)
        specs.append(
            RuleSpec(
                rule_index=len(specs),
                moves=moves,
                observations=observations,
                rule=rule,
            )
        )
    order = list(specs)
    _stream_rng("subspace-rule-order-v1").shuffle(order)
    ordered = tuple(
        RuleSpec(i, s.moves, s.observations, s.rule) for i, s in enumerate(order)
    )
    return _Draw(
        specs=ordered,
        candidates=len(candidates),
        rejected_value_out_of_language=bad_value,
        rejected_no_hypothesis=bad_fit,
        rejected_extrapolation=bad_extrapolation,
        rejected_duplicate_rule=duplicate,
    )


def admissible_rules() -> _Draw:
    """The frozen, commitment-shuffled draw of admissible distinct rules."""
    return _draw()


def rule_admissibility(spec: RuleSpec) -> Admissibility:
    """CL-D1 admissibility of one stored method, computed not asserted.

    Compression is judged against the cost of simply listing the observation
    window, which is what a verbatim cache of the same information would pay.
    Extrapolation is judged at the registered query positions, all of which lie
    far outside the observation window.  Independence holds because the checker
    (:func:`scaling.certify`) recomputes the Grundy value from the game
    definition and never consults the store.
    """
    max_value = SUBSPACE_PLAN["language"]["max_value"]
    evidence = tuple(enumerate(spec.observations))
    consistent = LANGUAGE.consistent_count(evidence)
    bits_method = LANGUAGE.code_bits(spec.rule)
    bits_data = len(evidence) * math.log2(max_value)
    table = SubtractionGame(spec.moves).grundy_upto(max(query_positions()))
    failures = sum(1 for p in query_positions() if spec.rule.grundy(p) != table[p])
    return Admissibility.build(
        bits_method=bits_method,
        bits_data=bits_data,
        bits_residual=math.log2(consistent),
        extrapolation_probes=len(query_positions()),
        extrapolation_failures=failures,
        independence_ok=True,
    )


# --------------------------------------------------------------------------
# the catalogue and the store
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class SubspaceCatalogue:
    """The frozen contents of the persistent state at one scale.

    ``stored`` is a prefix of one frozen order, so the catalogue at ``3x`` is a
    strict superset of the catalogue at ``1x``.  Nested scales matter for the
    same reason they matter in ``scaling.py``: if each scale drew its own
    methods, a change in ``k`` between scales could be a change of methods
    rather than a change of ``N``.
    """

    scale_id: str
    multiplier: int
    stored: tuple[RuleSpec, ...]
    held_out: tuple[RuleSpec, ...]

    @property
    def n_methods(self) -> int:
        return len(self.stored)

    @property
    def n_objects(self) -> int:
        """``N``: one method plus one evidence support each, plus the lemma."""
        return 2 * len(self.stored) + 1

    def spec_by_method_id(self) -> Mapping[str, RuleSpec]:
        return {s.method_id: s for s in self.stored}


@lru_cache(maxsize=None)
def build_catalogue(multiplier: int) -> SubspaceCatalogue:
    """The catalogue at scale ``multiplier``, nested in the smaller scales."""
    draw = admissible_rules()
    held = SUBSPACE_PLAN["held_out_rules"]
    if held >= len(draw.specs):  # pragma: no cover -- the draw is far larger
        raise AssertionError("the held-out reserve consumes the whole draw")
    pool = draw.specs[:-held]
    held_out = draw.specs[-held:]
    count = SUBSPACE_PLAN["base_methods"] * multiplier
    if count > len(pool):
        raise ValueError(
            f"scale {multiplier}x needs {count} distinct admissible rules but the "
            f"registered draw yields {len(pool)}; the draw is not large enough and "
            "the scale must be reported as unreachable rather than shrunk silently"
        )
    return SubspaceCatalogue(
        scale_id=f"{multiplier}x",
        multiplier=multiplier,
        stored=pool[:count],
        held_out=held_out,
    )


def install_objects(store: CompetenceStore, specs: Sequence[RuleSpec]) -> tuple[str, ...]:
    """Add one evidence support and one method per spec; return the method ids.

    Used both to populate a store and to grow one.  Growth adds objects to the
    *same* store, because the registered growth study is one long-lived machine
    with no reset (``COGNITIVE_LADDER_SCALING_V1`` §2), and an arm that were
    rebuilt at every scale could not exhibit -- or fail to exhibit -- the thing
    this experiment is about.
    """
    added: list[str] = []
    for spec in specs:
        store.add_support(
            spec.support_id,
            spec.family_id,
            {
                "kind": "observation_block",
                "family": spec.family_id,
                "window": OBSERVATION_WINDOW,
                "labels": list(spec.observations),
            },
        )
        added.append(
            store.add_competence(
                spec.family_id, spec.rule, spec.support_ids, relation="stored"
            )
        )
    return tuple(added)


def populate_store(catalogue: SubspaceCatalogue) -> CompetenceStore:
    """Build the store for one catalogue.  Every arm receives one of these.

    ``N``, the byte totals and the dependency graph are produced by this single
    function, so any difference between arms is a difference of retrieval
    architecture and nothing else.
    """
    store = CompetenceStore(f"subspace@{catalogue.scale_id}")
    store.add_support(
        SHARED_SUPPORT_ID,
        "*SHARED*",
        {
            "kind": "lemma",
            "statement": "every finite subtraction game has an eventually periodic Grundy sequence",
            "parent": "Sprague-Grundy theory",
        },
        relation="shared",
    )
    install_objects(store, catalogue.stored)
    return store


def grow_store(
    store: CompetenceStore,
    previous: SubspaceCatalogue,
    nxt: SubspaceCatalogue,
) -> tuple[str, ...]:
    """Grow an installed store from one scale to the next.  Returns new method ids."""
    if nxt.n_methods < previous.n_methods:
        raise ValueError("scales must grow; a shrinking store is a different study")
    if nxt.stored[: previous.n_methods] != previous.stored:
        raise ValueError("scales are not nested; growth would change the methods too")
    return install_objects(store, nxt.stored[previous.n_methods :])


# --------------------------------------------------------------------------
# feature adequacy, collisions and the witnessed obstruction
# --------------------------------------------------------------------------


def bucket_map(
    specs: Sequence[RuleSpec], feature: Feature
) -> dict[tuple[int, ...], list[RuleSpec]]:
    """Group stored methods by their image under ``feature``."""
    out: dict[tuple[int, ...], list[RuleSpec]] = {}
    for spec in specs:
        out.setdefault(spec.image(feature), []).append(spec)
    return out


@dataclass(frozen=True)
class FeatureAdequacy:
    """How well one feature separates the methods currently in the store.

    ``adequate`` is the *declared* criterion -- ``max_bucket <= MAX_BUCKET_SIZE``
    -- and nothing else.  ``collision_rate`` is reported beside it and is a
    different quantity: a feature can be adequate while most of its methods
    share a bucket with somebody, and reading one number without the other is
    how a bucket-size claim gets overstated.
    """

    feature: Feature
    n_methods: int
    n_buckets: int
    max_bucket: int
    colliding_methods: int
    adequate: bool

    @classmethod
    def build(cls, specs: Sequence[RuleSpec], feature: Feature) -> "FeatureAdequacy":
        buckets = bucket_map(specs, feature)
        sizes = [len(v) for v in buckets.values()] or [0]
        return cls(
            feature=feature,
            n_methods=len(specs),
            n_buckets=len(buckets),
            max_bucket=max(sizes),
            colliding_methods=sum(s for s in sizes if s > 1),
            adequate=max(sizes) <= MAX_BUCKET_SIZE,
        )

    @property
    def collision_rate(self) -> float:
        """Fraction of stored methods that share their image with another."""
        if self.n_methods == 0:
            return 0.0
        return self.colliding_methods / self.n_methods

    @property
    def mean_bucket(self) -> float:
        if self.n_buckets == 0:
            return 0.0
        return self.n_methods / self.n_buckets

    def as_dict(self) -> dict:
        return {
            "feature": self.feature.feature_id,
            "feature_size": self.feature.size,
            "n_methods": self.n_methods,
            "n_buckets": self.n_buckets,
            "max_bucket": self.max_bucket,
            "collision_rate": round(self.collision_rate, 6),
            "mean_bucket": round(self.mean_bucket, 4),
            "adequate": self.adequate,
            "max_bucket_size_threshold": MAX_BUCKET_SIZE,
        }


def adequacy_of(specs: Sequence[RuleSpec], feature: Feature) -> FeatureAdequacy:
    return FeatureAdequacy.build(specs, feature)


def smallest_adequate_feature(
    specs: Sequence[RuleSpec], language: FeatureLanguage | None = None
) -> tuple[Feature | None, int]:
    """First adequate feature in canonical order, and how many were tried.

    Returns ``(None, |FL|)`` when the language is exhausted.  This function is
    the *scorer's* view: an arm that wants the same answer has to pay for it,
    and paying for it is the point -- see ``subspace_arms.DiscoveringArm``.
    """
    lang = language if language is not None else feature_language()
    tried = 0
    for feature in lang.features():
        tried += 1
        if FeatureAdequacy.build(specs, feature).adequate:
            return feature, tried
    return None, tried


def feature_identifiability_witness(
    specs: Sequence[RuleSpec], feature: Feature, positions: Sequence[int] | None = None
) -> tuple[str, str, int] | None:
    """Two stored methods with the same feature image and different answers.

    The same construction as ``escalation.identifiability_witness``, applied to
    an index key rather than to a representation, and returned in the same
    exhibited form: a pair plus the position at which they disagree.  A third
    party holding the receipt can recompute both images and both predictions
    and confirm that **no index keyed on this feature can separate them**.

    That is what makes an inadequate feature a *witnessed obstruction* rather
    than a timeout.  A feature that merely produces large buckets is slow; a
    feature under which two methods that disagree are indistinguishable is
    non-identifying, and no amount of further search on that key fixes it.
    """
    probes = tuple(positions) if positions is not None else query_positions()
    by_image: dict[tuple[int, ...], RuleSpec] = {}
    for spec in specs:
        key = spec.image(feature)
        other = by_image.get(key)
        if other is not None:
            for p in probes:
                if other.predicts(p) != spec.predicts(p):
                    return (other.method_id, spec.method_id, p)
        else:
            by_image[key] = spec
    return None


def feature_bits(specs: Sequence[RuleSpec]) -> BitsAccounting | None:
    """CL-D3 accounting for the *feature* choice, not the method choice.

    ``prior_bits`` is ``log2 |FL|``.  ``residual_bits`` is the log of how many
    features in the language are adequate for this store, so ``acquired_bits``
    is exactly the information the store's own contents supplied about where to
    key the index.  ``None`` when no feature is adequate: there is then no
    surviving hypothesis and ``BitsAccounting`` correctly refuses to be built,
    which is the numerical face of the witnessed obstruction.
    """
    lang = feature_language()
    consistent = sum(
        1 for f in lang.features() if FeatureAdequacy.build(specs, f).adequate
    )
    if consistent == 0:
        return None
    return BitsAccounting.build(lang.language_id, lang.size(), consistent)


# --------------------------------------------------------------------------
# the query stream
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Query:
    """One query: observations without a family identity, and a fresh position.

    ``in_store`` and ``truth`` are the **scorer's** fields.  No arm reads them;
    they are kept on the same object only so that the harness cannot lose track
    of which query was which, exactly as ``escalation.py`` keeps a world's
    ``minimum_sufficient_level`` out of ``diagnose`` while storing it on the
    world.
    """

    query_id: str
    family_id: str
    moves: tuple[int, ...]
    observations: tuple[int, ...]
    position: int
    in_store: bool
    truth: bool

    @property
    def expected_outcome(self) -> str:
        return "ANSWERED" if self.in_store else "NO_METHOD_APPLIES"

    def as_dict(self) -> dict:
        return {
            "query_id": self.query_id,
            "position": self.position,
            "in_store": self.in_store,
            "expected_outcome": self.expected_outcome,
        }


@lru_cache(maxsize=None)
def _query_family_indices() -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Which rules the queries are drawn from.  Frozen, and nested-safe.

    The in-store families are drawn from the ``1x`` core, so they are present at
    every scale and a change in ``k`` across scales cannot be a change of query.
    The absent families are drawn from the held-out reserve, which enters no
    store at any scale.
    """
    core = SUBSPACE_PLAN["base_methods"]
    rng = _stream_rng("subspace-query-families-v1")
    in_store = tuple(sorted(rng.sample(range(core), SUBSPACE_PLAN["in_store_query_families"])))
    held = SUBSPACE_PLAN["held_out_rules"]
    absent = tuple(sorted(rng.sample(range(held), SUBSPACE_PLAN["absent_query_families"])))
    return in_store, absent


@lru_cache(maxsize=None)
def query_stream() -> tuple[Query, ...]:
    """The frozen query stream.  Identical at every scale and for every arm.

    Two kinds, and both are load-bearing:

    ``in_store``   observations from a family whose method the store holds.  The
                   arm must find it and answer.  An arm that answers nothing
                   fails here -- the ``cache_parent`` lesson from the prior
                   pilot, where the sparsest arm in the sweep was the one that
                   could not answer.
    ``absent``     observations from a held-out family no stored method serves.
                   The arm must say so.  An arm that always returns its nearest
                   candidate fails here, and that is exactly the failure mode
                   ``nearest_neighbour_parent`` exists to exhibit.

    Every query carries the same number of observations and asks about the same
    registered positions, so no arm can be advantaged by the shape of its input.
    """
    draw = admissible_rules()
    held = SUBSPACE_PLAN["held_out_rules"]
    pool = draw.specs[:-held]
    reserve = draw.specs[-held:]
    in_idx, absent_idx = _query_family_indices()
    out: list[Query] = []
    for kind, specs, idxs in (
        ("in", pool, in_idx),
        ("absent", reserve, absent_idx),
    ):
        for i in idxs:
            spec = specs[i]
            table = SubtractionGame(spec.moves).grundy_upto(max(query_positions()))
            for position in query_positions():
                out.append(
                    Query(
                        query_id=f"Q:{kind}:{spec.family_id}@{position}",
                        family_id=spec.family_id,
                        moves=spec.moves,
                        observations=spec.observations,
                        position=position,
                        in_store=(kind == "in"),
                        truth=table[position] == 0,
                    )
                )
    return tuple(out)


@dataclass(frozen=True)
class QueryOutcome:
    """One answered (or refused) query, scored.

    ``decision_correct`` is the headline correctness coordinate and it is
    stricter than ``record.verdict_correct``.  On an in-store query the arm must
    answer **and** be right; on an absent query it must refuse.  An arm that
    guesses on an absent query and happens to be right about the P-position is
    not correct here, because the thing under test is whether it can tell that
    nothing in its memory applies.
    """

    query: Query
    record: ResourceRecord
    decision_correct: bool
    false_match: bool
    missed_match: bool

    @classmethod
    def build(cls, query: Query, record: ResourceRecord) -> "QueryOutcome":
        answered = record.outcome == "ANSWERED"
        if query.in_store:
            decision = answered and record.verdict_correct is True
        else:
            decision = not answered
        return cls(
            query=query,
            record=record,
            decision_correct=decision,
            false_match=answered and not query.in_store,
            missed_match=(not answered) and query.in_store,
        )

    def as_dict(self) -> dict:
        return {
            **self.query.as_dict(),
            "decision_correct": self.decision_correct,
            "false_match": self.false_match,
            "missed_match": self.missed_match,
            "record": self.record.as_dict(),
        }
