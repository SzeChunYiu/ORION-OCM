"""Six arms over one growing store, and the frozen lifetime sweep.

``subspace.py`` supplies the world: a store of learned periodic rules behind
``scaling.py``'s instrumented read path, a query stream that carries
observations and withholds the family identity, a registered feature language,
an exact independent checker and the log-log fitter that refuses to quote an
exponent when a line does not describe the points.  This module supplies the
arms, the growth schedule and the table.

Every arm is handed **identical information**: the same store, the same
observations, the same fifty queries, one checker call per query whether or not
it managed to answer.  They differ only in how they decide which part of the
store to look at.  One arm is handed strictly *more* -- the family identity --
and it is the ceiling, not a competitor.

The arms
--------

``discovering_arm``
    Chooses its index feature from the registered language using only what it
    can see in its own store: it takes the first feature in canonical order
    whose largest bucket is within the declared ``MAX_BUCKET_SIZE``.  When the
    store grows and a bucket outgrows that bound it **detects the inadequacy at
    insertion time and re-indexes** on a richer feature, paying for the search
    and the rebuild in ``index_maintenance_work``.  Its ``k`` is bounded by
    ``MAX_BUCKET_SIZE`` at every scale, and that bound is bought, not given.

``fixed_feature_arm``
    The ablation, and one class with one flag away from the arm above.  It runs
    the identical search at install and then never runs it again.  Everything
    else -- the index, the probe, the verification, the byte accounting -- is
    the same code.  What it loses is visible as ``k``: its 1x feature ends the
    sweep with a bucket two orders of magnitude larger than the bound.  It
    remains **correct**, because it still verifies every bucket member against
    the observations; it is simply no longer sparse.  Correct-but-dense is the
    honest cost of not noticing.

``oracle_key_parent``
    Given the family identity with the query.  This is the prior pilot's gifted
    setting reproduced exactly, and it is the ceiling: one index probe, one
    read, ``k = 1``, right on every query including the absent ones.  It is the
    only arm that overrides ``_answer`` rather than ``_answer_blind``, so the
    gift is structural and a test can check that nobody else took it.

``exact_scan_parent``
    Tests every stored method against the observations.  ``k = N`` exactly, and
    it is always right.  It is the arm every other arm has to beat on work
    without losing to it on correctness, and it is the denominator of the
    crossover query count.

``signature_hash_parent``
    An ordinary content-addressed inverted index on a **hand-specified**
    prediction prefix, of exactly the length of the largest feature the
    discovering arm may choose.  This is the strongest realistic parent.  It is
    expected to be sufficient -- indeed to *win*, since it pays no search --
    wherever its hand-specified prefix happens to be adequate, and the sweep
    reports at which scales that is the case rather than assuming either way.

``nearest_neighbour_parent``
    Ranks every stored method by Hamming distance from the observation vector
    and reads the top one.  A retrieval / approximate-nearest-neighbour stand-in
    with the property such systems actually have: **it always returns
    something**.  On a query drawn from a family the store does not serve it
    returns its nearest miss and answers with it.  Its error rate is measured
    and printed in the same row as its ``k``, not relegated to a note.  Its
    ``k`` is 1 and its query work is linear in ``N``, which is a second reason
    ``k`` is never read alone.

Growth, and where the cost is charged
-------------------------------------

One store, installed at ``1x`` and grown through ``3x``, ``10x`` and ``30x``
without a reset, as the registered growth study requires.  Index construction is
charged to the install, insertion maintenance and any re-index are charged to
the growth event that caused them, and neither is ever folded into query work.
The consequence is that an arm can show a small per-query number while carrying
an enormous lifetime index bill, so the crossover query count against
``exact_scan_parent`` is reported at every scale and is the number that decides
whether the index was worth building.

The feature search is charged conservatively against the arm being tested: a
candidate feature costs one unit per stored method with no early exit, even
though an implementation could abandon a candidate as soon as one bucket
overflowed.  Charging the cheaper number would be the easy direction and it is
not taken.

Limitations, stated with the mechanism
--------------------------------------

* Adequacy and identifiability are different properties and the sweep reports
  both.  A feature can keep every bucket within the declared bound while two
  methods that *disagree* on a query position share an image; correctness is
  then rescued by verifying bucket members against the observations, at the
  price of reading the whole bucket.  ``feature_identifiability_witness``
  exhibits such a pair when one exists, and an exhibited pair is a witnessed
  obstruction rather than a timeout -- the same standard ``escalation.py``
  applies to a representation.
* The discovering arm's search space is a registered language of position
  subsets.  It discovers *which* positions to key on; it does not invent the
  notion of keying on predicted labels, which is authored here.  Attack A1 of
  the protocol is answered only to the extent that ``|FL|`` and the bits of
  prior are reported exactly.
* Nothing here measures dependency discovery, revision, or acquisition.  This
  module is about one question -- finding the relevant part of memory when
  nothing names it -- and every other coordinate of the lifetime vector is
  absent by design.

Parents: inverted indexes and content-addressed storage; locality-sensitive
hashing and approximate nearest neighbour; feature selection for hash keys;
query planning.  No novelty is claimed for any of them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from methods import GrundyRule
from scaling import (
    INDEX_ENTRY_BYTES,
    SPARSE_FRACTION,
    CheckStatus,
    CompetenceStore,
    LogLogFit,
    ResourceRecord,
    TouchLedger,
    certify,
    fit_loglog,
    record_from_ledger,
)
from subspace import (
    COMMITMENT,
    MAX_BUCKET_SIZE,
    OBSERVATION_WINDOW,
    SIGNATURE_PREFIX,
    SUBSPACE_PLAN,
    Feature,
    FeatureAdequacy,
    Query,
    QueryOutcome,
    RuleSpec,
    SubspaceCatalogue,
    adequacy_of,
    build_catalogue,
    feature_bits,
    feature_identifiability_witness,
    feature_language,
    feature_pool,
    grow_store,
    populate_store,
    query_positions,
    query_stream,
    rule_of,
)

__all__ = [
    "FeatureIndex",
    "SubspaceArm",
    "FeatureArm",
    "DiscoveringArm",
    "FixedFeatureArm",
    "OracleKeyParent",
    "ExactScanParent",
    "SignatureHashParent",
    "NearestNeighbourParent",
    "ARMS",
    "ARM_ROLES",
    "ScaleCell",
    "LifetimeResult",
    "SWEEP_NOTES",
    "run_lifetime",
    "sweep",
    "sweep_table",
    "fits_for",
    "crossover_table",
    "unaudited_probe",
    "format_sweep_table",
    "format_feature_table",
    "format_fit_table",
]


# --------------------------------------------------------------------------
# the index, with its construction, its maintenance and its search charged
# --------------------------------------------------------------------------


class FeatureIndex:
    """Feature image -> the methods whose predictions carry that image.

    An inverted index, built by walking the store through the instrumented scan
    so that construction is charged rather than free.  Three costs are tracked
    and never merged:

    ``build_work``        the install scan and the images computed during it;
    ``maintenance_work``  per-insertion upkeep, plus any re-index;
    ``index_probes``      charged on the query ledger, one unit for the key and
                          one for each posting handed back.  A bucket of a
                          hundred postings costs a hundred; charging one would
                          hide exactly the growth this experiment is about.

    ``cache_pool`` decides whether the index also keeps each method's labels at
    the registered feature-pool positions.  That cache is what makes a feature
    *search* possible without re-reading the store, and it is charged in bytes
    on every arm that keeps it.  An arm that never searches does not keep it and
    is correspondingly cheaper in storage, which is the honest trade.
    """

    def __init__(
        self,
        store: CompetenceStore,
        feature: Feature,
        ledger: TouchLedger,
        *,
        cache_pool: tuple[int, ...] | None = None,
    ) -> None:
        self.feature = feature
        self.cache_pool = cache_pool
        self.build_work = 0
        self.maintenance_work = 0
        self.re_index_count = 0
        self.features_evaluated = 0
        self._by_image: dict[tuple[int, ...], list[str]] = {}
        self._pool_vectors: dict[str, tuple[int, ...]] = {}
        for obj in store.scan(ledger):
            self.build_work += 1
            if obj.object_class != "method":
                continue
            rule = rule_of(obj)
            self.build_work += feature.size
            self._by_image.setdefault(feature.image_of_rule(rule), []).append(obj.object_id)
            if cache_pool is not None:
                self.build_work += len(cache_pool)
                self._pool_vectors[obj.object_id] = tuple(
                    rule.grundy(p) for p in cache_pool
                )
        ledger.index_build_work += self.build_work

    # ---- state ----------------------------------------------------------

    @property
    def n_methods(self) -> int:
        return sum(len(v) for v in self._by_image.values())

    @property
    def n_buckets(self) -> int:
        return len(self._by_image)

    @property
    def max_bucket(self) -> int:
        """The arm's own view of its worst bucket.  No ground truth involved."""
        return max((len(v) for v in self._by_image.values()), default=0)

    @property
    def entries(self) -> int:
        return self.n_methods + self.n_buckets + sum(
            len(v) for v in self._pool_vectors.values()
        )

    @property
    def bytes(self) -> int:
        return self.entries * INDEX_ENTRY_BYTES

    # ---- maintenance ----------------------------------------------------

    def insert(self, method_id: str, rule: GrundyRule, ledger: TouchLedger) -> None:
        """Add one method.  Returns nothing; the caller reads ``max_bucket``."""
        self.maintenance_work += 1 + self.feature.size
        self._by_image.setdefault(self.feature.image_of_rule(rule), []).append(method_id)
        if self.cache_pool is not None:
            self.maintenance_work += len(self.cache_pool)
            self._pool_vectors[method_id] = tuple(rule.grundy(p) for p in self.cache_pool)
        ledger.index_maintenance_work += 1 + self.feature.size + (
            0 if self.cache_pool is None else len(self.cache_pool)
        )

    # ---- search ---------------------------------------------------------

    def _image_under(self, method_id: str, feature: Feature) -> tuple[int, ...]:
        assert self.cache_pool is not None
        vec = self._pool_vectors[method_id]
        return tuple(vec[self.cache_pool.index(p)] for p in feature.positions)

    def search_for_feature(
        self, ledger: TouchLedger, *, charge: str
    ) -> tuple[Feature | None, int]:
        """Find the first adequate feature in the registered language.

        Uses only the arm's own cached pool vectors, so no store object is
        touched and ``k`` does not move: the search is index work and is charged
        as index work.  Every candidate costs one unit per stored method, with
        **no early exit** when a bucket overflows -- the conservative direction,
        chosen deliberately.

        Returns ``(None, |FL|)`` when the language is exhausted.  The caller is
        then holding a witnessed obstruction, not a timeout, and must say so.
        """
        language = feature_language()
        ids = list(self._pool_vectors)
        tried = 0
        chosen: Feature | None = None
        for candidate in language.features():
            tried += 1
            buckets: dict[tuple[int, ...], int] = {}
            for method_id in ids:
                key = self._image_under(method_id, candidate)
                buckets[key] = buckets.get(key, 0) + 1
            if max(buckets.values(), default=0) <= MAX_BUCKET_SIZE:
                chosen = candidate
                break
        cost = tried * max(len(ids), 1)
        self.features_evaluated += tried
        if charge == "build":
            self.build_work += cost
            ledger.index_build_work += cost
        else:
            self.maintenance_work += cost
            ledger.index_maintenance_work += cost
        return chosen, tried

    def rebuild_on(self, feature: Feature, ledger: TouchLedger) -> None:
        """Re-key every posting on ``feature``.  Charged as maintenance."""
        ids = list(self._pool_vectors)
        self.feature = feature
        self._by_image = {}
        for method_id in ids:
            self._by_image.setdefault(self._image_under(method_id, feature), []).append(
                method_id
            )
        cost = max(len(ids), 1)
        self.maintenance_work += cost
        self.re_index_count += 1
        ledger.index_maintenance_work += cost

    # ---- query ----------------------------------------------------------

    def probe(self, image: tuple[int, ...], ledger: TouchLedger) -> tuple[str, ...]:
        bucket = tuple(self._by_image.get(image, ()))
        ledger.probe_index(1 + len(bucket))
        return bucket


class FamilyKeyIndex:
    """Family identity -> the method that serves it.  The gifted index.

    Identical in construction and in cost to ``scaling_arms.FamilyIndex``, and
    present for the same reason: it is what the prior pilot measured, and
    reproducing it here keeps the ceiling honest.
    """

    def __init__(self, store: CompetenceStore, ledger: TouchLedger) -> None:
        self.build_work = 0
        self.maintenance_work = 0
        self._by_family: dict[str, str] = {}
        for obj in store.scan(ledger):
            self.build_work += 1
            if obj.object_class == "method":
                self._by_family[obj.family_id] = obj.object_id
        ledger.index_build_work += self.build_work

    @property
    def entries(self) -> int:
        return len(self._by_family)

    @property
    def bytes(self) -> int:
        return self.entries * INDEX_ENTRY_BYTES

    def insert(self, family_id: str, method_id: str, ledger: TouchLedger) -> None:
        self._by_family[family_id] = method_id
        self.maintenance_work += 1
        ledger.index_maintenance_work += 1

    def probe(self, family_id: str, ledger: TouchLedger) -> str | None:
        ledger.probe_index()
        return self._by_family.get(family_id)


class VectorIndex:
    """Every stored method's full prediction vector, for distance ranking.

    The retrieval parent's state.  It holds ``OBSERVATION_WINDOW`` labels per
    method, and pays for all of them in index bytes: a vector store that
    reported one entry per method would be understating its own footprint by a
    factor of thirty.
    """

    def __init__(self, store: CompetenceStore, ledger: TouchLedger) -> None:
        self.build_work = 0
        self.maintenance_work = 0
        self._vectors: list[tuple[str, tuple[int, ...]]] = []
        for obj in store.scan(ledger):
            self.build_work += 1
            if obj.object_class != "method":
                continue
            rule = rule_of(obj)
            self.build_work += OBSERVATION_WINDOW
            self._vectors.append(
                (obj.object_id, tuple(rule.grundy(n) for n in range(OBSERVATION_WINDOW)))
            )
        ledger.index_build_work += self.build_work

    @property
    def entries(self) -> int:
        return len(self._vectors) * OBSERVATION_WINDOW

    @property
    def bytes(self) -> int:
        return self.entries * INDEX_ENTRY_BYTES

    def insert(self, method_id: str, rule: GrundyRule, ledger: TouchLedger) -> None:
        self._vectors.append(
            (method_id, tuple(rule.grundy(n) for n in range(OBSERVATION_WINDOW)))
        )
        self.maintenance_work += OBSERVATION_WINDOW
        ledger.index_maintenance_work += OBSERVATION_WINDOW

    def nearest(
        self, observations: Sequence[int], ledger: TouchLedger
    ) -> tuple[str | None, int]:
        """Top-1 by Hamming distance, ties broken by insertion order.

        Ranking touches every index entry, so it is charged as ``N`` index
        probes and ``N`` predicate evaluations.  The arm's ``k`` stays at one
        because it reads exactly one persistent object; its query work does
        not, and the two coordinates disagreeing is the point.
        """
        best_id: str | None = None
        best_distance = OBSERVATION_WINDOW + 1
        for method_id, vector in self._vectors:
            ledger.predicate_evaluations += 1
            distance = sum(1 for a, b in zip(vector, observations) if a != b)
            if distance < best_distance:
                best_id, best_distance = method_id, distance
        ledger.probe_index(len(self._vectors))
        return best_id, best_distance


# --------------------------------------------------------------------------
# the arms
# --------------------------------------------------------------------------


class SubspaceArm:
    """One retrieval architecture, installed once and grown, never reset.

    Subclasses implement ``_install``, ``_answer_blind`` and
    ``_observe_insertions``.  Everything shared -- the checker call, the record
    construction, the growth bookkeeping, the scoring against the query's
    registered expectation -- lives here, so no arm can differ from another in
    the bookkeeping rather than in the architecture.

    ``_answer`` exists so that exactly one arm, the ceiling, can be handed the
    family identity.  Every other arm implements ``_answer_blind``, which
    receives the observation vector and the position and nothing else.  The gift
    is therefore a visible override rather than a discipline nobody can check.
    """

    arm_id = "abstract"
    role = "ARM"

    def __init__(self, catalogue: SubspaceCatalogue) -> None:
        self.catalogue = catalogue
        self.store = populate_store(catalogue)
        self.queries_served = 0
        ledger = TouchLedger()
        self._install(ledger)
        self.install_record = self._record(
            ledger,
            operation="INDEX_BUILD",
            thermal_state="COLD",
            outcome="INSTALL",
            verdict_correct=None,
        )

    # ---- construction ---------------------------------------------------

    def _install(self, ledger: TouchLedger) -> None:
        raise NotImplementedError

    def _observe_insertions(self, method_ids: Sequence[str], ledger: TouchLedger) -> None:
        """React to new objects.  Default: notice nothing, pay nothing."""
        return None

    def grow(self, nxt: SubspaceCatalogue) -> ResourceRecord:
        """Grow the store to the next scale and let the arm react.

        The arm is not told how many objects arrived or what they are: it is
        handed the ids of the new methods, exactly as an insertion path would
        hand them over, and whatever it wants to know about them it reads
        through the instrumented path and pays for.
        """
        ledger = TouchLedger()
        new_ids = grow_store(self.store, self.catalogue, nxt)
        self.catalogue = nxt
        self._observe_insertions(new_ids, ledger)
        return self._record(
            ledger,
            operation="GROWTH",
            thermal_state="COLD",
            outcome=f"GREW_TO_{nxt.scale_id}",
            verdict_correct=None,
        )

    # ---- reporting surface ----------------------------------------------

    @property
    def scale_id(self) -> str:
        return self.catalogue.scale_id

    @property
    def n_objects(self) -> int:
        return self.store.n_objects

    @property
    def store_bytes(self) -> int:
        return self.store.store_bytes

    @property
    def index_bytes(self) -> int:
        return 0

    @property
    def lifetime_index_build_work(self) -> int:
        return 0

    @property
    def lifetime_index_maintenance_work(self) -> int:
        return 0

    @property
    def re_index_count(self) -> int:
        return 0

    @property
    def features_evaluated(self) -> int:
        return 0

    @property
    def current_feature(self) -> Feature | None:
        return None

    @property
    def obstruction(self) -> tuple[str, str, int] | None:
        """A witnessed non-identifying pair, when the arm has one."""
        return None

    def _record(
        self,
        ledger: TouchLedger,
        *,
        operation: str,
        thermal_state: str,
        outcome: str,
        verdict_correct: bool | None,
    ) -> ResourceRecord:
        return record_from_ledger(
            ledger,
            arm_id=self.arm_id,
            scale_id=self.scale_id,
            operation=operation,
            thermal_state=thermal_state,
            n_objects=self.n_objects,
            store_bytes=self.store_bytes,
            index_bytes=self.index_bytes,
            lifetime_index_build_work=self.lifetime_index_build_work,
            lifetime_index_maintenance_work=self.lifetime_index_maintenance_work,
            outcome=outcome,
            verdict_correct=verdict_correct,
        )

    # ---- the query ------------------------------------------------------

    def _answer_blind(
        self, observations: tuple[int, ...], position: int, ledger: TouchLedger
    ) -> tuple[str, bool | None]:
        raise NotImplementedError

    def _answer(self, query: Query, ledger: TouchLedger) -> tuple[str, bool | None]:
        """Default: the family identity is withheld.  Only the ceiling overrides."""
        return self._answer_blind(query.observations, query.position, ledger)

    def query(self, query: Query) -> QueryOutcome:
        """Answer one query and score it against its registered expectation.

        The independent checker is called exactly once by every arm on every
        query, including arms that declined to answer.  That keeps
        ``checker_calls`` constant across the comparison and stops an arm
        looking cheap by refusing to establish the truth.
        """
        ledger = TouchLedger()
        thermal = "COLD" if self.queries_served == 0 else "WARM"
        outcome, verdict = self._answer(query, ledger)
        truth = certify(query.moves, query.position, ledger)
        correct = None if verdict is None else (verdict == truth)
        self.queries_served += 1
        record = self._record(
            ledger,
            operation="QUERY",
            thermal_state=thermal,
            outcome=outcome,
            verdict_correct=correct,
        )
        return QueryOutcome.build(query, record)

    # ---- shared retrieval primitives ------------------------------------

    def _consistent_with(
        self,
        method_ids: Sequence[str],
        observations: Sequence[int],
        ledger: TouchLedger,
    ) -> list[GrundyRule]:
        """Read each candidate and keep the ones the observations do not refute.

        Every candidate is read -- this is where ``k`` grows -- and every
        candidate is tested, with no early exit.  An early-exit variant would
        halve a constant and leave the growth in bucket size exactly where it
        is; ``scaling.py`` makes the same choice in ``CompetenceStore.query``
        for the same reason.
        """
        out: list[GrundyRule] = []
        for method_id in method_ids:
            obj = self.store.read(method_id, ledger)
            rule = rule_of(obj)
            ledger.predicate_evaluations += 1
            if all(rule.grundy(n) == observations[n] for n in range(len(observations))):
                out.append(rule)
        return out

    @staticmethod
    def _verdict_from(rules: Sequence[GrundyRule], position: int) -> tuple[str, bool | None]:
        """Answer only when the surviving methods agree.

        Within this world the observation set pins every slot of a hypothesis in
        the registered language, so at most one distinct rule can survive and
        the ``AMBIGUOUS_MATCH`` branch is unreachable.  It is written anyway:
        an arm that would answer from a set of mutually disagreeing methods is
        wrong in general, and a branch that exists and is never taken is a
        cheaper way to say so than a comment.
        """
        if not rules:
            return "NO_METHOD_APPLIES", None
        verdicts = {rule.is_p_position(position) for rule in rules}
        if len(verdicts) != 1:
            return "AMBIGUOUS_MATCH", None
        return "ANSWERED", verdicts.pop()


class FeatureArm(SubspaceArm):
    """The two feature-indexed arms and the hand-specified parent, one body.

    Three class flags separate them and nothing else does:

    ``chooses_feature``  search the registered language at install rather than
                         accept a hand-specified feature;
    ``re_indexes``       search again when the store grows a bucket past the
                         declared bound;
    ``hand_feature``     the feature to start from when not choosing.

    Writing them as one class is deliberate.  The claim under test is that
    discovering and re-indexing separate from a hand-specified key, and the
    cheapest way to manufacture that separation would be three implementations
    with an incidental asymmetry in the query path.  Here the query path is
    literally the same code.
    """

    chooses_feature = False
    re_indexes = False
    hand_feature: Feature = Feature(SIGNATURE_PREFIX)

    def _install(self, ledger: TouchLedger) -> None:
        chooses = self.chooses_feature or self.re_indexes
        pool = feature_pool() if chooses else None
        # A choosing arm starts from the first feature in the registered
        # language, not from the parent's hand-specified prefix: seeding the
        # machine arm with the parent's key would make its first choice a
        # correction of somebody else's guess rather than a choice.
        initial = feature_language().features()[0] if chooses else self.hand_feature
        self.index = FeatureIndex(self.store, initial, ledger, cache_pool=pool)
        self._exhausted = False
        if self.chooses_feature:
            chosen, _ = self.index.search_for_feature(ledger, charge="build")
            if chosen is None:
                self._exhausted = True
            else:
                self.index.rebuild_on(chosen, ledger)
                # the install rebuild is construction, not repair: move the
                # charge back onto the build coordinate so that
                # re_index_count means "noticed and fixed after growth".
                self.index.re_index_count = 0

    @property
    def index_bytes(self) -> int:
        return self.index.bytes

    @property
    def lifetime_index_build_work(self) -> int:
        return self.index.build_work

    @property
    def lifetime_index_maintenance_work(self) -> int:
        return self.index.maintenance_work

    @property
    def re_index_count(self) -> int:
        return self.index.re_index_count

    @property
    def features_evaluated(self) -> int:
        return self.index.features_evaluated

    @property
    def current_feature(self) -> Feature | None:
        return self.index.feature

    @property
    def language_exhausted(self) -> bool:
        return self._exhausted

    def _observe_insertions(self, method_ids: Sequence[str], ledger: TouchLedger) -> None:
        for method_id in method_ids:
            obj = self.store.read(method_id, ledger)
            self.index.insert(method_id, rule_of(obj), ledger)
        if not self.re_indexes:
            return
        if self.index.max_bucket <= MAX_BUCKET_SIZE:
            return
        chosen, _ = self.index.search_for_feature(ledger, charge="maintenance")
        if chosen is None:
            self._exhausted = True
            return
        self.index.rebuild_on(chosen, ledger)

    def _answer_blind(
        self, observations: tuple[int, ...], position: int, ledger: TouchLedger
    ) -> tuple[str, bool | None]:
        bucket = self.index.probe(self.index.feature.image(observations), ledger)
        return self._verdict_from(
            self._consistent_with(bucket, observations, ledger), position
        )


class DiscoveringArm(FeatureArm):
    """Chooses its feature, notices when growth breaks it, re-indexes.

    The only arm in the sweep whose index key is not supplied by anybody.  Its
    sparsity claim is exactly: ``k <= MAX_BUCKET_SIZE`` at every scale, bought
    with a search whose cost appears in the same row.
    """

    arm_id = "discovering_arm"
    role = "MACHINE"
    chooses_feature = True
    re_indexes = True

    @property
    def obstruction(self) -> tuple[str, str, int] | None:
        if not self._exhausted:
            return None
        return feature_identifiability_witness(
            self.catalogue.stored, self.index.feature, query_positions()
        )


class FixedFeatureArm(FeatureArm):
    """Chooses once, then never looks again.  The functional-replacement ablation."""

    arm_id = "fixed_feature_arm"
    role = "ABLATION"
    chooses_feature = True
    re_indexes = False


class SignatureHashParent(FeatureArm):
    """An ordinary content-addressed index on a hand-specified prediction prefix.

    The strongest realistic parent.  It pays no search at all, so wherever its
    prefix is adequate it is strictly cheaper than the discovering arm and the
    correct report for that scale is ``PARENT_SUFFICIENT``.  Where the prefix is
    not adequate its buckets grow and its ``k`` grows with them, while it stays
    exactly as correct as before -- which is the distinction between a key that
    is slow and a key that is wrong.
    """

    arm_id = "signature_hash_parent"
    role = "PARENT"
    chooses_feature = False
    re_indexes = False


class OracleKeyParent(SubspaceArm):
    """Given the family identity.  The ceiling, and the prior pilot's setting.

    It should win on query work, and if it did not the harness would be broken.
    It is reported so that every number in the discovering arm's column can be
    read against what the same store costs when nothing has to be discovered.
    """

    arm_id = "oracle_key_parent"
    role = "CEILING"

    def _install(self, ledger: TouchLedger) -> None:
        self.index = FamilyKeyIndex(self.store, ledger)

    @property
    def index_bytes(self) -> int:
        return self.index.bytes

    @property
    def lifetime_index_build_work(self) -> int:
        return self.index.build_work

    @property
    def lifetime_index_maintenance_work(self) -> int:
        return self.index.maintenance_work

    def _observe_insertions(self, method_ids: Sequence[str], ledger: TouchLedger) -> None:
        for method_id in method_ids:
            obj = self.store.read(method_id, ledger)
            self.index.insert(obj.family_id, method_id, ledger)

    def _answer(self, query: Query, ledger: TouchLedger) -> tuple[str, bool | None]:
        """The gift, made structural: this is the only override in the module."""
        method_id = self.index.probe(query.family_id, ledger)
        if method_id is None:
            return "NO_METHOD_APPLIES", None
        obj = self.store.read(method_id, ledger)
        ledger.predicate_evaluations += 1
        return "ANSWERED", rule_of(obj).is_p_position(query.position)

    def _answer_blind(
        self, observations: tuple[int, ...], position: int, ledger: TouchLedger
    ) -> tuple[str, bool | None]:  # pragma: no cover -- never reached
        raise AssertionError("the ceiling answers with the identity it was given")


class ExactScanParent(SubspaceArm):
    """Tests every stored method against the observations.  ``k = N``, always right.

    No index, no build cost, no maintenance, and no scale at which it is wrong.
    Every other arm in the sweep is trying to buy its correctness for less work,
    and the crossover query count is the price list.
    """

    arm_id = "exact_scan_parent"
    role = "PARENT"

    def _install(self, ledger: TouchLedger) -> None:
        return None

    def _answer_blind(
        self, observations: tuple[int, ...], position: int, ledger: TouchLedger
    ) -> tuple[str, bool | None]:
        survivors: list[GrundyRule] = []
        for obj in self.store.scan(ledger):
            if obj.object_class != "method":
                continue
            rule = rule_of(obj)
            ledger.predicate_evaluations += 1
            if all(rule.grundy(n) == observations[n] for n in range(len(observations))):
                survivors.append(rule)
        return self._verdict_from(survivors, position)


class NearestNeighbourParent(SubspaceArm):
    """Ranks by Hamming distance and reads the top one.  It may be wrong.

    The retrieval stand-in, with the property retrieval systems actually have:
    there is no abstention.  Asked about a family the store does not serve, it
    returns its nearest miss and answers from it.  Its decision error rate is
    therefore bounded below by the fraction of absent queries in the stream, and
    the receipt prints that rate rather than burying it.

    A thresholded variant -- refuse when the nearest distance exceeds some
    bound -- would fix this, at the price of a hand-set threshold, which is the
    hand-specified-feature problem again in a different coordinate.  It is not
    run here and no claim is made about it.
    """

    arm_id = "nearest_neighbour_parent"
    role = "PARENT"

    def _install(self, ledger: TouchLedger) -> None:
        self.index = VectorIndex(self.store, ledger)

    @property
    def index_bytes(self) -> int:
        return self.index.bytes

    @property
    def lifetime_index_build_work(self) -> int:
        return self.index.build_work

    @property
    def lifetime_index_maintenance_work(self) -> int:
        return self.index.maintenance_work

    def _observe_insertions(self, method_ids: Sequence[str], ledger: TouchLedger) -> None:
        for method_id in method_ids:
            obj = self.store.read(method_id, ledger)
            self.index.insert(method_id, rule_of(obj), ledger)

    def _answer_blind(
        self, observations: tuple[int, ...], position: int, ledger: TouchLedger
    ) -> tuple[str, bool | None]:
        method_id, _distance = self.index.nearest(observations, ledger)
        if method_id is None:  # pragma: no cover -- the store is never empty
            return "NO_METHOD_APPLIES", None
        obj = self.store.read(method_id, ledger)
        ledger.predicate_evaluations += 1
        return "ANSWERED", rule_of(obj).is_p_position(position)


# --------------------------------------------------------------------------
# the registered arm set
# --------------------------------------------------------------------------

ARMS: dict[str, Callable[[SubspaceCatalogue], SubspaceArm]] = {
    "discovering_arm": DiscoveringArm,
    "fixed_feature_arm": FixedFeatureArm,
    "oracle_key_parent": OracleKeyParent,
    "exact_scan_parent": ExactScanParent,
    "signature_hash_parent": SignatureHashParent,
    "nearest_neighbour_parent": NearestNeighbourParent,
}

#: Declared before the run.  ``MACHINE`` is the arm under test, ``PARENT`` has
#: first right of refusal, ``ABLATION`` removes one mechanism from the machine
#: arm and changes nothing else, and ``CEILING`` is given information no other
#: arm receives and exists to bound the whole table from above.
ARM_ROLES: dict[str, str] = {arm_id: cls.role for arm_id, cls in ARMS.items()}


# --------------------------------------------------------------------------
# one cell of the lifetime sweep
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ScaleCell:
    """Everything one arm did at one scale of one lifetime."""

    arm_id: str
    role: str
    scale_id: str
    multiplier: int
    n_objects: int
    n_methods: int
    outcomes: tuple[QueryOutcome, ...]
    install_record: ResourceRecord | None
    growth_record: ResourceRecord | None
    feature_id: str | None
    feature_size: int | None
    adequacy: FeatureAdequacy | None
    obstruction: tuple[str, str, int] | None
    language_exhausted: bool
    re_index_count: int
    features_evaluated: int
    lifetime_index_build_work: int
    lifetime_index_maintenance_work: int
    index_bytes: int
    store_bytes: int

    # ---- derived, all read next to each other -------------------------

    @property
    def records(self) -> tuple[ResourceRecord, ...]:
        return tuple(o.record for o in self.outcomes)

    @property
    def k_unmeasured(self) -> bool:
        return any(r.k is None for r in self.records)

    @property
    def k_max(self) -> int | None:
        """Worst case over the query stream.  An arm cannot pass on average."""
        if self.k_unmeasured:
            return None
        return max(r.k for r in self.records)  # type: ignore[type-var]

    @property
    def k_mean(self) -> float | None:
        if self.k_unmeasured:
            return None
        return sum(r.k for r in self.records) / len(self.records)  # type: ignore[misc]

    @property
    def query_work_mean(self) -> float:
        return sum(r.query_work for r in self.records) / len(self.records)

    @property
    def query_work_max(self) -> int:
        return max(r.query_work for r in self.records)

    @property
    def answered(self) -> int:
        return sum(1 for r in self.records if r.outcome == "ANSWERED")

    @property
    def decisions_correct(self) -> int:
        return sum(1 for o in self.outcomes if o.decision_correct)

    @property
    def in_store_queries(self) -> int:
        return sum(1 for o in self.outcomes if o.query.in_store)

    @property
    def in_store_correct(self) -> int:
        return sum(1 for o in self.outcomes if o.query.in_store and o.decision_correct)

    @property
    def absent_queries(self) -> int:
        return sum(1 for o in self.outcomes if not o.query.in_store)

    @property
    def absent_correct(self) -> int:
        return sum(
            1 for o in self.outcomes if (not o.query.in_store) and o.decision_correct
        )

    @property
    def false_matches(self) -> int:
        return sum(1 for o in self.outcomes if o.false_match)

    @property
    def missed_matches(self) -> int:
        return sum(1 for o in self.outcomes if o.missed_match)

    @property
    def decision_error_rate(self) -> float:
        return 1.0 - self.decisions_correct / len(self.outcomes)

    @property
    def lifetime_index_work(self) -> int:
        return self.lifetime_index_build_work + self.lifetime_index_maintenance_work

    @property
    def persistent_bytes(self) -> int:
        return self.store_bytes + self.index_bytes

    @property
    def sparse_verdict(self) -> str:
        """Worst sparse verdict over the query stream.  Never the best one."""
        order = {
            "SPARSE": 0,
            "SPARSE_ONLY_AFTER_GLOBAL_BUILD_SCAN": 1,
            "NOT_SPARSE": 2,
            "CANNOT_CHECK": 3,
        }
        return max((r.sparse_verdict for r in self.records), key=lambda v: order[v])

    def as_dict(self) -> dict:
        return {
            "arm_id": self.arm_id,
            "role": self.role,
            "scale": self.scale_id,
            "N": self.n_objects,
            "methods": self.n_methods,
            "k_max": self.k_max,
            "k_mean": None if self.k_mean is None else round(self.k_mean, 4),
            "k_over_N": None if self.k_max is None else round(self.k_max / self.n_objects, 6),
            "k_status": "CANNOT_CHECK" if self.k_unmeasured else "MEASURED",
            "query_work_mean": round(self.query_work_mean, 4),
            "query_work_max": self.query_work_max,
            "lifetime_index_build_work": self.lifetime_index_build_work,
            "lifetime_index_maintenance_work": self.lifetime_index_maintenance_work,
            "lifetime_index_work": self.lifetime_index_work,
            "persistent_bytes": self.persistent_bytes,
            "store_bytes": self.store_bytes,
            "index_bytes": self.index_bytes,
            "answered": f"{self.answered}/{len(self.outcomes)}",
            "decisions_correct": f"{self.decisions_correct}/{len(self.outcomes)}",
            "in_store_correct": f"{self.in_store_correct}/{self.in_store_queries}",
            "absent_correct": f"{self.absent_correct}/{self.absent_queries}",
            "false_matches": self.false_matches,
            "missed_matches": self.missed_matches,
            "decision_error_rate": round(self.decision_error_rate, 6),
            "feature": self.feature_id,
            "feature_size": self.feature_size,
            "feature_adequacy": None if self.adequacy is None else self.adequacy.as_dict(),
            "re_indexes": self.re_index_count,
            "features_evaluated": self.features_evaluated,
            "language_exhausted": self.language_exhausted,
            "obstruction_witness": None
            if self.obstruction is None
            else {
                "method_a": self.obstruction[0],
                "method_b": self.obstruction[1],
                "disagree_at": self.obstruction[2],
            },
            "sparse_verdict": self.sparse_verdict,
        }


@dataclass(frozen=True)
class LifetimeResult:
    """One arm, installed once and carried through every registered scale."""

    arm_id: str
    cells: tuple[ScaleCell, ...]


def run_lifetime(
    arm_id: str, multipliers: Sequence[int] | None = None
) -> LifetimeResult:
    """Install at the smallest scale, then grow.  No reset, ever.

    The whole point of the experiment lives in this function: an arm that were
    rebuilt from scratch at each scale would always hold a freshly chosen
    feature and could not exhibit -- or fail to exhibit -- the detection of an
    index key that growth has broken.
    """
    scales = list(multipliers if multipliers is not None else SUBSPACE_PLAN["multipliers"])
    if not scales:
        raise ValueError("a lifetime needs at least one scale")
    catalogues = [build_catalogue(m) for m in scales]
    arm = ARMS[arm_id](catalogues[0])
    cells: list[ScaleCell] = []
    for i, catalogue in enumerate(catalogues):
        growth = None if i == 0 else arm.grow(catalogue)
        outcomes = tuple(arm.query(q) for q in query_stream())
        feature = arm.current_feature
        cells.append(
            ScaleCell(
                arm_id=arm.arm_id,
                role=arm.role,
                scale_id=catalogue.scale_id,
                multiplier=catalogue.multiplier,
                n_objects=arm.n_objects,
                n_methods=catalogue.n_methods,
                outcomes=outcomes,
                install_record=arm.install_record if i == 0 else None,
                growth_record=growth,
                feature_id=None if feature is None else feature.feature_id,
                feature_size=None if feature is None else feature.size,
                adequacy=None
                if feature is None
                else adequacy_of(catalogue.stored, feature),
                obstruction=arm.obstruction,
                language_exhausted=bool(getattr(arm, "language_exhausted", False)),
                re_index_count=arm.re_index_count,
                features_evaluated=arm.features_evaluated,
                lifetime_index_build_work=arm.lifetime_index_build_work,
                lifetime_index_maintenance_work=arm.lifetime_index_maintenance_work,
                index_bytes=arm.index_bytes,
                store_bytes=arm.store_bytes,
            )
        )
    return LifetimeResult(arm_id=arm_id, cells=tuple(cells))


def sweep(
    arm_ids: Sequence[str] | None = None, multipliers: Sequence[int] | None = None
) -> dict[str, LifetimeResult]:
    """Every registered arm, each through its own lifetime of the same scales."""
    chosen = list(ARMS) if arm_ids is None else list(arm_ids)
    return {arm_id: run_lifetime(arm_id, multipliers) for arm_id in chosen}


# --------------------------------------------------------------------------
# the flat table, the fits and the crossover
# --------------------------------------------------------------------------


def sweep_table(results: Mapping[str, LifetimeResult]) -> list[dict]:
    """One flat row per (arm, scale), for the receipt."""
    return [cell.as_dict() for result in results.values() for cell in result.cells]


#: Coordinates fitted against ``N``.  ``k`` and query work are the ME-SCALE-1
#: endpoint; the index-work coordinate is the hostile that ME-SCALE-1's
#: falsifier is written around.
FITTED_COORDINATES: tuple[tuple[str, str], ...] = (
    ("k(N)", "k_max"),
    ("query_work(N)", "query_work_mean"),
    ("lifetime_index_work(N)", "lifetime_index_work"),
    ("persistent_bytes(N)", "persistent_bytes"),
)


def fits_for(rows: Sequence[Mapping]) -> dict:
    """Fit each registered relation against ``N``, per arm.

    ``fit_loglog`` refuses an exponent when a straight line does not describe
    the points and refuses everything when a coordinate is ``CANNOT_CHECK`` or
    non-positive, so a relation that is not a power law says so.
    """
    out: dict[str, dict[str, dict]] = {}
    for arm_id in sorted({r["arm_id"] for r in rows}):
        mine = [r for r in rows if r["arm_id"] == arm_id]
        ns = [r["N"] for r in mine]
        out[arm_id] = {
            name: fit_loglog(
                ns, [r[key] for r in mine], label=f"{arm_id}:{name}"
            ).as_dict()
            for name, key in FITTED_COORDINATES
        }
    return out


def crossover_table(rows: Sequence[Mapping]) -> dict:
    """``Q*``: queries after which an arm's total work beats the exact scan.

    The direct answer to the index-construction hostile
    (``COGNITIVE_LADDER_SCALING_V1`` §4).  An arm whose per-query work is tiny
    but whose lifetime index bill never repays itself within the registered
    query stream has not demonstrated sparse retrieval; it has moved the cost,
    and ``reached_within_stream`` says so in the same object.

    ``None`` means the arm never saves anything per query against the scan, so
    no number of queries repays its index.
    """
    scan = {r["scale"]: r for r in rows if r["arm_id"] == "exact_scan_parent"}
    out: dict[str, dict[str, Any]] = {}
    stream = len(query_stream())
    for row in rows:
        if row["arm_id"] == "exact_scan_parent":
            continue
        saving = scan[row["scale"]]["query_work_mean"] - row["query_work_mean"]
        if saving <= 0:
            q_star: int | None = None
        else:
            q_star = math.ceil(row["lifetime_index_work"] / saving)
        out.setdefault(row["arm_id"], {})[row["scale"]] = {
            "per_query_saving_vs_exact_scan": round(saving, 4),
            "lifetime_index_work": row["lifetime_index_work"],
            "crossover_queries": q_star,
            "queries_in_registered_stream": stream,
            "reached_within_stream": None if q_star is None else q_star <= stream,
        }
    return out


def unaudited_probe(multiplier: int = 1) -> ResourceRecord:
    """Exercise the uninstrumented path and show it reports ``CANNOT_CHECK``.

    Not an arm.  ``scaling.CompetenceStore`` keeps exactly one accessor that
    hands out payloads without a per-object touch, and it poisons the ledger it
    is given.  This function runs that accessor against a store built by *this*
    module, so the discipline is demonstrated on this harness's own objects
    rather than inherited on faith: the returned record carries ``k = None``,
    ``k_status = CANNOT_CHECK`` and a reason, even though the lookup succeeded
    and a naive harness would have written ``k = 1``.
    """
    catalogue = build_catalogue(multiplier)
    store = populate_store(catalogue)
    ledger = TouchLedger()
    store.unaudited_scan_for_family(catalogue.stored[0].family_id, ledger)
    return record_from_ledger(
        ledger,
        arm_id="unaudited_path_selfcheck",
        scale_id=catalogue.scale_id,
        operation="QUERY",
        thermal_state="COLD",
        n_objects=store.n_objects,
        store_bytes=store.store_bytes,
        index_bytes=0,
        lifetime_index_build_work=0,
        lifetime_index_maintenance_work=0,
        outcome="ANSWERED_THROUGH_UNINSTRUMENTED_PATH",
        verdict_correct=None,
    )


# --------------------------------------------------------------------------
# the notes that travel with the numbers
# --------------------------------------------------------------------------

SWEEP_NOTES: tuple[str, ...] = (
    "k is the worst case over the frozen query stream and is counted by "
    "instrumented touches only; it is never inferred from a returned result. The "
    "uninstrumented accessor is exercised by unaudited_probe() and reports "
    "CANNOT_CHECK on this harness's own store.",
    "the family identity is withheld from every arm except oracle_key_parent, "
    "which overrides _answer rather than _answer_blind. That override is the "
    "prior pilot's entire result: sparse lookup under a supplied key is a "
    "property of the key, and the ceiling is printed so the rest of the table "
    "can be read against it.",
    "signature_hash_parent pays no search. Wherever its hand-specified prefix is "
    "adequate it is strictly cheaper than the discovering arm, and the honest "
    "report at those scales is PARENT_SUFFICIENT. The sweep reports at which "
    "scales the prefix is adequate rather than assuming either way.",
    "adequacy and identifiability are different properties. A feature can keep "
    "every bucket inside the declared bound while two methods that disagree on a "
    "query position share an image; correctness is then rescued by verifying "
    "bucket members against the observations, at the price of reading the whole "
    "bucket. The witness pair is exhibited whenever one exists.",
    "correctness is reported beside every k, split into in-store queries (the "
    "arm must find the method) and absent-family queries (the arm must refuse). "
    "An arm that is sparse because it answers nothing fails the first; an arm "
    "that always returns its nearest candidate fails the second.",
    "nearest_neighbour_parent has k=1 and query work linear in N, and it cannot "
    "abstain, so its decision error rate is bounded below by the absent fraction "
    "of the stream. A thresholded variant would fix that with a hand-set "
    "threshold, which is the hand-specified-feature problem again; it is not run.",
    "the feature search is charged one unit per stored method per candidate with "
    "no early exit, which overstates the discovering arm's cost rather than "
    "understating it.",
    "index build and maintenance are charged to the install and to the growth "
    "event that caused them, never to a query. The crossover query count against "
    "exact_scan_parent is therefore the number that decides whether the index "
    "was worth building, and it is reported at every scale.",
    "the store is grown, never rebuilt: one arm instance is carried through "
    "1x, 3x, 10x and 30x. An arm reset at each scale would always hold a freshly "
    "chosen feature and could not exhibit the failure this experiment is about.",
    "four scales and two free parameters leave two degrees of freedom; a fitted "
    "slope describes these four points and is not an extrapolation licence.",
    "PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM remains the correct terminal for any "
    "field claim read out of an N of a few hundred.",
)


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------


def _num(value: Any) -> str:
    return "CANNOT" if value is None else str(value)


_COLUMNS: tuple[tuple[str, int, Callable[[ScaleCell], Any]], ...] = (
    ("arm", 26, lambda c: c.arm_id),
    ("role", 10, lambda c: c.role),
    ("scale", 6, lambda c: c.scale_id),
    ("N", 6, lambda c: c.n_objects),
    ("k", 7, lambda c: _num(c.k_max)),
    ("k/N", 9, lambda c: "n/a" if c.k_max is None else f"{c.k_max / c.n_objects:.5f}"),
    ("qwork", 9, lambda c: f"{c.query_work_mean:.1f}"),
    ("idxwork", 10, lambda c: c.lifetime_index_work),
    ("bytes", 9, lambda c: c.persistent_bytes),
    ("feature", 22, lambda c: c.feature_id or "-"),
    ("bkt", 5, lambda c: "-" if c.adequacy is None else c.adequacy.max_bucket),
    ("coll", 7, lambda c: "-" if c.adequacy is None else f"{c.adequacy.collision_rate:.2f}"),
    ("adq", 5, lambda c: "-" if c.adequacy is None else ("yes" if c.adequacy.adequate else "NO")),
    ("rix", 5, lambda c: c.re_index_count),
    ("ans", 7, lambda c: f"{c.answered}/{len(c.outcomes)}"),
    ("ok", 7, lambda c: f"{c.decisions_correct}/{len(c.outcomes)}"),
    ("false", 7, lambda c: c.false_matches),
    ("sparse", 14, lambda c: c.sparse_verdict),
)


def format_sweep_table(results: Mapping[str, LifetimeResult]) -> str:
    """The lifetime table, one row per (arm, scale).

    ``k`` sits next to ``ok`` and ``false`` on purpose.  The prior pilot's
    cautionary case was an arm with the best ``k`` in the sweep and no answers;
    this one adds an arm with a good ``k`` and wrong answers.  Neither is
    readable without its neighbours.
    """
    head = "".join(name.rjust(width) for name, width, _ in _COLUMNS)
    lines = [head, "-" * len(head)]
    for arm_id in ARMS:
        if arm_id not in results:
            continue
        for cell in results[arm_id].cells:
            lines.append("".join(str(fn(cell)).rjust(w) for _, w, fn in _COLUMNS))
        lines.append("")
    return "\n".join(lines).rstrip()


def format_feature_table(results: Mapping[str, LifetimeResult]) -> str:
    """Feature choice, collision structure and the exhibited obstruction."""
    header = (
        f"{'arm':<26}{'scale':>6}{'methods':>9}{'feature':>24}{'max_bkt':>9}"
        f"{'collision':>11}{'adequate':>10}{'re-index':>10}{'evaluated':>11}  witness"
    )
    lines = [header, "-" * (len(header) + 12)]
    for arm_id in ARMS:
        if arm_id not in results:
            continue
        if all(cell.adequacy is None for cell in results[arm_id].cells):
            continue
        for cell in results[arm_id].cells:
            if cell.adequacy is None:
                continue
            witness = (
                "-"
                if cell.obstruction is None
                else f"{cell.obstruction[0]} vs {cell.obstruction[1]} @ {cell.obstruction[2]}"
            )
            lines.append(
                f"{cell.arm_id:<26}{cell.scale_id:>6}{cell.n_methods:>9}"
                f"{cell.feature_id or '-':>24}{cell.adequacy.max_bucket:>9}"
                f"{cell.adequacy.collision_rate:>11.4f}"
                f"{('yes' if cell.adequacy.adequate else 'NO'):>10}"
                f"{cell.re_index_count:>10}{cell.features_evaluated:>11}  {witness}"
            )
        lines.append("")
    return "\n".join(lines).rstrip()


def format_fit_table(rows: Sequence[Mapping]) -> str:
    """Fitted log-log slopes with residuals and the model's own verdict."""
    fits = fits_for(rows)
    header = (
        f"{'arm':<26}{'coordinate':<26}{'slope':>9}{'rms resid':>11}{'r^2':>9}  verdict"
    )
    lines = [header, "-" * (len(header) + 10)]
    for arm_id in ARMS:
        if arm_id not in fits:
            continue
        for coord, fit in fits[arm_id].items():
            slope = "     n/a" if fit["slope"] is None else f"{fit['slope']:8.4f}"
            rms = (
                "        n/a"
                if fit["rms_log_residual"] is None
                else f"{fit['rms_log_residual']:11.5f}"
            )
            r2 = "      n/a" if fit["r_squared"] is None else f"{fit['r_squared']:9.5f}"
            lines.append(f"{arm_id:<26}{coord:<26}{slope:>9}{rms}{r2}  {fit['verdict']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main() -> None:  # pragma: no cover -- reporting entry point
    results = sweep()
    rows = sweep_table(results)
    print(f"commitment  {COMMITMENT.commitment}")
    print(f"feature pool {list(feature_pool())}   |FL| {feature_language().size()}")
    print(f"query positions {list(query_positions())}   queries/scale {len(query_stream())}")
    print()
    print(format_sweep_table(results))
    print()
    print(format_feature_table(results))
    print()
    print(format_fit_table(rows))
    print()
    for note in SWEEP_NOTES:
        print(f"* {note}")


if __name__ == "__main__":  # pragma: no cover
    main()
