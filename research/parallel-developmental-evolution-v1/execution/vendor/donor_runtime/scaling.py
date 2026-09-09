"""Active-subspace scaling: does query cost track ``k`` or ``N``?

This module is the persistent-state growth harness for endpoints ``S1`` and
``S3`` of ``docs/spec/COGNITIVE_LADDER_PROTOCOL_V1.md``.  The hypothesis under
test is the programme's most load-bearing architectural claim:

    a machine whose persistent state is a set of *scoped* cognitive methods
    answers a query by touching a number of persistent objects ``k`` that is
    governed by the query's scope and not by the size ``N`` of the store, and
    revises after a falsification by touching a dependency cone whose size is
    governed by what actually depended on the falsified support.

Everything interesting about that sentence is in the word *touching*.  A store
that returns a small result set after reading every object it holds is not
sparse; it is a linear scan with a small ``return``.  A store that answers in
``O(1)`` because it rebuilt a global index over all ``N`` objects a moment
earlier has moved the linear term, not removed it.  Both of those are the
failure modes this module exists to make visible, so the discipline is stated
before the mechanism:

* **``k`` is instrumented, never inferred.**  ``k`` is ``len(touched_ids)``
  where every id in that tuple was placed there by :meth:`CompetenceStore.read`
  at the moment the object's payload was handed out.  It is never derived from
  the size of a returned result, a non-zero activation count, or an edge count.
  This is the same rule, and deliberately the same coordinate names, as
  ``research/machine-epistemics-lifetime-v1/lifetime_metrics.py``.
* **An uninstrumented path may not report a number.**  The store exposes one
  deliberately uninstrumented accessor, :meth:`CompetenceStore.unaudited_scan_for_family`.
  It *poisons* the ledger handed to it, and a poisoned ledger can only produce
  a record with ``k_status = CANNOT_CHECK`` and ``k = None``.  A favourable
  number is unreachable on that path by construction rather than by good faith.
* **Index construction and maintenance are charged separately and reported
  alongside query work.**  ``index_build_work`` is the work *this operation*
  triggered; ``lifetime_index_build_work`` and
  ``lifetime_index_maintenance_work`` are the totals the arm has paid since it
  was installed.  Both appear in every record.  This is attack A8 of the
  protocol ("sparse query work hides global indexing"), and the derived
  :attr:`ResourceRecord.sparse_verdict` reports
  ``SPARSE_ONLY_AFTER_GLOBAL_BUILD_SCAN`` when the sparse-looking query was
  bought with a scan of all ``N``.

The strongest parent
--------------------

The parent with first right of refusal here is **not** a strawman linear scan.
It is a plain database-style index: a hash index from family identity to the
method that serves it, maintained incrementally on insert, with no dependency
tracking.  That parent is expected to *match or beat* the OCM arm on ``k(N)``
and on ``query_work(N)``, because scoped lookup keyed on a family identity is
exactly what a database index already does, and the OCM arm additionally pays
to check that each supporting object is still live.  If the sweep reports
``PARENT_SUFFICIENT`` for ``k(N)``, that is the correct report and it is
printed as such.  Any residual has to appear somewhere the parent structurally
cannot reach — here, in ``revision_work`` after a support is revoked, because
the parent holds no dependency edges and must rediscover the cone by scanning.

The falsifier
-------------

The scaling claim is refuted, on this harness, by any of the following:

1. ``k`` for the indexed arm grows with ``N`` (log-log slope distinguishable
   from zero over the frozen scales);
2. ``k`` stays flat only because per-query ``index_build_work`` grew with
   ``N`` --- caught by ``sparse_verdict``;
3. revoking a *globally shared* support produces a small cone.  A dependency
   structure that reports a local cone for a global change is not exact, it is
   broken, and the shared-support revocation is carried in the sweep precisely
   as the control that must **not** look local;
4. the indexed parent matches the OCM arm on every reported coordinate,
   including ``revision_work``.  Then there is no residual and the honest
   report is that a database index explains the effect.

Limitations, stated up front
----------------------------

* The dependency graph the OCM arm walks was authored by this same harness, so
  its revocation is exact **by construction**.  That makes the revision numbers
  evidence about the *cost* of exact revocation, not evidence that dependencies
  can be discovered.  Attack A9 is not answered here and is not claimed to be.
* Four scales and two free parameters leaves two degrees of freedom.  A slope
  fitted on four points is a description of these four points; ``fit_loglog``
  therefore reports a residual and refuses the label ``POWER_LAW_CONSISTENT``
  when the residual is large, instead of assuming the model.
* Bytes are counted as the canonical-JSON serialization length of an object's
  payload plus a declared per-index-entry constant.  That is an exact, arm-
  independent accounting rule, not a claim about any real storage engine.
* ``N`` here is a few thousand.  ``PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM`` from
  the protocol remains available and is the appropriate terminal for any
  attempt to read a field claim out of these numbers.

Parents: relational index structures and query planning; truth maintenance
systems (Doyle) and dependency-directed backtracking for the revocation cone;
active-subspace / sparse-activation accounting as practised in retrieval
systems.  No novelty is claimed for any of them.
"""

from __future__ import annotations

import enum
import math
import random
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Iterator, Mapping, Sequence

from games import SubtractionGame, Work
from methods import GrundyRule, GrundyRuleLanguage
from prereg import Commitment, canonical_json, commit

__all__ = [
    "CheckStatus",
    "TouchLedger",
    "CompetenceObject",
    "CompetenceStore",
    "ResourceRecord",
    "RevisionRecord",
    "FamilySpec",
    "CompetenceCatalogue",
    "LogLogFit",
    "SCALING_PLAN",
    "COMMITMENT",
    "SPARSE_FRACTION",
    "INDEX_ENTRY_BYTES",
    "SHARED_SUPPORT_ID",
    "build_catalogue",
    "populate_store",
    "populate_cache_store",
    "probe_positions",
    "certify",
    "fit_loglog",
    "record_from_ledger",
]


# --------------------------------------------------------------------------
# declared accounting constants
# --------------------------------------------------------------------------

#: An operation is called sparse only if it touched at most this fraction of
#: ``N`` **and** paid at most this fraction of ``N`` in index work that the
#: operation itself triggered.  Declared here, before any outcome, because a
#: threshold chosen after seeing the numbers is not a threshold.
SPARSE_FRACTION = 0.10

#: Declared byte cost of one index entry.  Arm-independent by construction, so
#: an arm cannot look cheap by declaring a smaller entry.
INDEX_ENTRY_BYTES = 24

#: The one support object every induced periodic rule depends on: the theorem
#: that a finite subtraction game has an eventually periodic Grundy sequence.
#: Revoking it is the hostile control -- a genuinely global change that a
#: dependency structure must report as global.
SHARED_SUPPORT_ID = "S:*SHARED*:eventual-periodicity"


class CheckStatus(str, enum.Enum):
    """Whether a coordinate was measured or is structurally unmeasurable.

    Names and values are taken verbatim from ``lifetime_metrics.CheckStatus``
    so that a receipt from this harness and a receipt from the lifetime lane
    can be read against each other without a translation table.
    """

    MEASURED = "MEASURED"
    CANNOT_CHECK = "CANNOT_CHECK"


# --------------------------------------------------------------------------
# the ledger: the only place a touch is recorded
# --------------------------------------------------------------------------


@dataclass
class TouchLedger:
    """Mutable accumulator for one scoped operation.

    Mutable on purpose and in the same style as ``games.Work``: the frozen
    dataclasses in this module are the *records*, and a record is built from a
    finished ledger.  Nothing here reads a clock.

    ``touch`` is the single choke point for ``k``.  Repeated touches of the
    same identity increment ``object_reads`` but do not increase ``k``, which
    is the rule ``lifetime_metrics.TouchMeasure`` enforces: repeated work
    belongs in the resource coordinates, not in the identity count.
    """

    touched_ids: list[str] = field(default_factory=list)
    _touched_set: set[str] = field(default_factory=set, repr=False)
    active_bytes: int = 0
    object_reads: int = 0
    enumerated_items: int = 0
    index_probes: int = 0
    index_build_work: int = 0
    index_maintenance_work: int = 0
    search_expansions: int = 0
    predicate_evaluations: int = 0
    checker_calls: int = 0
    checker_expansions: int = 0
    revision_work: int | None = 0
    status: CheckStatus = CheckStatus.MEASURED
    cannot_check_reason: str | None = None

    def touch(self, object_id: str, byte_cost: int) -> None:
        self.object_reads += 1
        if object_id not in self._touched_set:
            self._touched_set.add(object_id)
            self.touched_ids.append(object_id)
            self.active_bytes += byte_cost

    def probe_index(self, entries: int = 1) -> None:
        self.index_probes += entries
        self.active_bytes += entries * INDEX_ENTRY_BYTES

    def poison(self, reason: str) -> None:
        """Mark this ledger as unable to support a ``k`` claim.

        Called by any accessor that hands out object payloads without a
        per-object touch.  Once poisoned a ledger stays poisoned; the first
        reason is kept, because the first uninstrumented read is the one that
        broke the claim.
        """
        if self.status is CheckStatus.MEASURED:
            self.status = CheckStatus.CANNOT_CHECK
            self.cannot_check_reason = reason

    @property
    def k(self) -> int | None:
        if self.status is CheckStatus.CANNOT_CHECK:
            return None
        return len(self.touched_ids)

    @property
    def query_work(self) -> int:
        """Work spent inside the query path.

        Deliberately excludes ``checker_expansions``.  The checker is an
        independent exact procedure run once per query, identically, by every
        arm; its internal cost is a function of the probe position and not of
        ``N``.  Folding it into ``query_work`` would add the same constant to
        every arm and blur the ``N``-scaling the endpoint is about.  It is
        reported as its own coordinate in every record, never dropped.

        Also excludes ``index_build_work`` and ``index_maintenance_work``:
        those are charged separately and reported alongside, which is the whole
        point of the module.  :attr:`ResourceRecord.charged_total_work` adds
        them back for anyone who wants the single number.
        """
        return (
            self.index_probes
            + self.object_reads
            + self.enumerated_items
            + self.predicate_evaluations
            + self.search_expansions
            + self.checker_calls
        )


# --------------------------------------------------------------------------
# persistent objects
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class CompetenceObject:
    """One persistent, identity-bearing logical object.

    Two classes exist and both count towards ``N``:

    ``method``   an induced per-family Grundy rule -- a reusable cognitive
                 object in the sense of ``MethodRecordV1``.
    ``support``  an evidence block or a shared lemma that a method depends on.
                 Supports are objects, not annotations: they are what a
                 revocation is applied to, so they must be addressable.

    ``revoked`` state deliberately does **not** live here.  The object is
    immutable; the store holds the revoked set.  That keeps the object's byte
    cost and identity stable across a revocation, so ``A_live`` and
    ``A_revoked`` of protocol §6 have identical store shape.
    """

    object_id: str
    object_class: str
    family_id: str
    relation: str
    payload: Mapping[str, Any]
    byte_cost: int
    supports: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {
            "object_id": self.object_id,
            "object_class": self.object_class,
            "family_id": self.family_id,
            "relation": self.relation,
            "byte_cost": self.byte_cost,
            "supports": list(self.supports),
        }


def _payload_bytes(payload: Mapping[str, Any]) -> int:
    return len(canonical_json(dict(payload)).encode("utf-8"))


# --------------------------------------------------------------------------
# the store
# --------------------------------------------------------------------------


class CompetenceStore:
    """``N`` logical competence objects with an instrumented read path.

    The store implements no retrieval policy.  It offers exactly three ways to
    reach a payload, and each has a different epistemic status:

    :meth:`read`
        instrumented single-object access; the only way ``k`` grows.
    :meth:`query`
        the honest un-indexed answer to "which method serves this family": a
        full scan that touches every object and therefore reports ``k = N``.
        This is what an arm without an index actually costs.
    :meth:`unaudited_scan_for_family`
        the same scan without per-object instrumentation.  It poisons the
        ledger.  It exists so that the ``CANNOT_CHECK`` path is exercised by a
        real code path rather than asserted about a hypothetical one.

    ``_objects`` is reachable from Python; no module can prevent that.  The
    discipline enforced here is narrower and checkable: any accessor that does
    not touch per object is named ``unaudited_*`` and poisons its ledger, and
    :func:`record_from_ledger` refuses to emit a number from a poisoned ledger.
    """

    def __init__(self, store_id: str) -> None:
        self.store_id = store_id
        self._objects: dict[str, CompetenceObject] = {}
        self._order: list[str] = []
        self._dependents: dict[str, set[str]] = {}
        self._revoked: set[str] = set()
        self._store_bytes = 0

    # ---- state ----------------------------------------------------------

    @property
    def n_objects(self) -> int:
        """``N``: total persistent logical objects under one object grammar."""
        return len(self._objects)

    @property
    def store_bytes(self) -> int:
        return self._store_bytes

    @property
    def object_grammar(self) -> str:
        return "CompetenceStore.v1(method|support)"

    def counts_by_class(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for obj in self._objects.values():
            out[obj.object_class] = out.get(obj.object_class, 0) + 1
        return out

    def is_revoked(self, object_id: str) -> bool:
        return object_id in self._revoked

    def object_ids(self) -> tuple[str, ...]:
        """Ids in insertion order, for the scorer and for tests.

        Returns no payloads and is not an access path: an arm that used this
        to answer a query would still have to :meth:`read` each object, so no
        touch can escape through it.
        """
        return tuple(self._order)

    # ---- mutation -------------------------------------------------------

    def _add(self, obj: CompetenceObject) -> str:
        if obj.object_id in self._objects:
            raise ValueError(f"duplicate object id {obj.object_id}")
        self._objects[obj.object_id] = obj
        self._order.append(obj.object_id)
        self._store_bytes += obj.byte_cost
        for support_id in obj.supports:
            self._dependents.setdefault(support_id, set()).add(obj.object_id)
        return obj.object_id

    def add_support(
        self,
        object_id: str,
        family_id: str,
        payload: Mapping[str, Any],
        *,
        relation: str = "local",
    ) -> str:
        return self._add(
            CompetenceObject(
                object_id=object_id,
                object_class="support",
                family_id=family_id,
                relation=relation,
                payload=payload,
                byte_cost=_payload_bytes(payload),
            )
        )

    def add_competence(
        self,
        family_id: str,
        rule: GrundyRule,
        support_ids: Sequence[str],
        *,
        relation: str,
    ) -> str:
        """Add one method object depending on ``support_ids``.

        ``relation`` is ``"probe"``, ``"related"`` or ``"distractor"``.  The
        three are structurally identical -- same class, same support arity,
        same byte accounting -- and differ only in family identity.  That is
        deliberate: a distractor that were cheaper or shaped differently would
        make the store's ``N`` a fiction, and the sparse claim would be about
        the shape of the padding rather than about scoping.
        """
        payload = {
            "family": family_id,
            "preperiod": rule.preperiod,
            "period": rule.period,
            "values": list(rule.values),
        }
        return self._add(
            CompetenceObject(
                object_id=f"M:{family_id}",
                object_class="method",
                family_id=family_id,
                relation=relation,
                payload=payload,
                byte_cost=_payload_bytes(payload),
                supports=tuple(support_ids),
            )
        )

    def add_related_competence(
        self, family_id: str, rule: GrundyRule, support_ids: Sequence[str]
    ) -> str:
        """A competence for a family in the probe family's neighbourhood."""
        return self.add_competence(family_id, rule, support_ids, relation="related")

    def add_unrelated_competence(
        self, family_id: str, rule: GrundyRule, support_ids: Sequence[str]
    ) -> str:
        """An unrelated distractor: it inflates ``N`` and is never retrieved.

        Distractors are the entire point of the denominator.  A store whose
        every object is relevant to every query cannot exhibit sparsity, and a
        sparse result over such a store would mean nothing.
        """
        return self.add_competence(family_id, rule, support_ids, relation="distractor")

    def add_cached_position(
        self,
        family_id: str,
        position: int,
        grundy: int,
        support_ids: Sequence[str],
    ) -> str:
        """Add one solved position: the cache parent's unit of persistent state.

        A cached position is an identity-bearing persistent object under the
        same grammar as a method, so it counts towards ``N`` on the same terms.
        That is the whole comparison: the cache and the method arm are given
        identical information and the question is how many objects, and how
        many bytes, that information becomes.
        """
        payload = {
            "family": family_id,
            "position": position,
            "grundy": grundy,
            "is_p": grundy == 0,
        }
        return self._add(
            CompetenceObject(
                object_id=f"C:{family_id}:{position}",
                object_class="cached_position",
                family_id=family_id,
                relation="cache",
                payload=payload,
                byte_cost=_payload_bytes(payload),
                supports=tuple(support_ids),
            )
        )

    def revoke_support(self, support_id: str) -> None:
        """Mark a support revoked.  Computing the cone is the *arm's* job."""
        if support_id not in self._objects:
            raise KeyError(support_id)
        self._revoked.add(support_id)

    def revoke_method(self, method_id: str) -> None:
        self._revoked.add(method_id)

    # ---- ground truth, for the scorer only ------------------------------

    def true_cone(self, support_id: str) -> frozenset[str]:
        """The exact dependency cone of ``support_id``.

        Read **only** by the scorer, in the same way ``escalation.py`` keeps
        ``minimum_sufficient_level`` out of ``diagnose``.  No arm consults this
        method; each arm computes its own observed cone by whatever means its
        architecture actually affords, and the two are compared afterwards.
        """
        if support_id not in self._objects:
            raise KeyError(support_id)
        return frozenset({support_id}) | frozenset(self._dependents.get(support_id, ()))

    # ---- access ---------------------------------------------------------

    def read(self, object_id: str, ledger: TouchLedger) -> CompetenceObject:
        """Instrumented read.  This is the only place ``k`` grows."""
        obj = self._objects[object_id]
        ledger.touch(obj.object_id, obj.byte_cost)
        return obj

    def try_read(self, object_id: str, ledger: TouchLedger) -> CompetenceObject | None:
        if object_id not in self._objects:
            return None
        return self.read(object_id, ledger)

    def scan(self, ledger: TouchLedger) -> Iterator[CompetenceObject]:
        """Instrumented enumeration: every yielded object is enumerated and read.

        This is the honest cost of not having an index, and it is also what an
        index *rebuild* costs.  Nothing in this module can walk the store more
        cheaply than this while still seeing payloads.
        """
        for object_id in self._order:
            ledger.enumerated_items += 1
            yield self.read(object_id, ledger)

    def query(self, family_id: str, ledger: TouchLedger) -> CompetenceObject | None:
        """Un-indexed query for a task family: an instrumented full scan.

        Every object is enumerated and read, so ``k = N``.  The scan does not
        stop at the first match: an early-exit variant would halve the constant
        and leave the slope at one, and a deterministic control is worth more
        here than a constant factor.  Stated so nobody has to guess whether the
        control was weakened or strengthened.
        """
        found: CompetenceObject | None = None
        for obj in self.scan(ledger):
            if (
                obj.object_class == "method"
                and obj.family_id == family_id
                and obj.object_id not in self._revoked
            ):
                found = obj
        return found

    def unaudited_all_objects(self, ledger: TouchLedger) -> Iterator[CompetenceObject]:
        """Enumerate payloads with **no** per-object touch instrumentation.

        Deliberately present, and the only such path.  Any arm that reaches a
        payload this way has, by that act, made its own ``k`` unmeasurable; the
        poisoned ledger forces the resulting record to carry ``CANNOT_CHECK``
        instead of the flattering small number the returned result suggests.
        """
        ledger.poison(
            "payloads reached through unaudited_all_objects: the path walks all N "
            "objects without per-object touch instrumentation, so k cannot be "
            "measured and must not be inferred from the returned result"
        )
        return iter(list(self._objects.values()))

    def unaudited_scan_for_family(
        self, family_id: str, ledger: TouchLedger
    ) -> CompetenceObject | None:
        """The uninstrumented lookup an arm would write if nobody were counting."""
        for obj in self.unaudited_all_objects(ledger):
            if (
                obj.object_class == "method"
                and obj.family_id == family_id
                and obj.object_id not in self._revoked
            ):
                return obj
        return None


# --------------------------------------------------------------------------
# records
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ResourceRecord:
    """The per-operation resource vector.

    Coordinate names follow ``CL-R7`` of the protocol and
    ``lifetime_metrics.ResourceVector`` wherever the two overlap.  Every
    coordinate is reported on every arm; none is ``null`` here, because a
    finite exact harness has no excuse for a missing number.
    """

    arm_id: str
    scale_id: str
    operation: str
    thermal_state: str  # COLD | WARM -- never averaged together (protocol E3)
    n_objects: int
    persistent_bytes: int
    store_bytes: int
    index_bytes: int
    k: int | None
    k_status: CheckStatus
    touched_ids: tuple[str, ...]
    active_bytes: int
    index_probes: int
    index_build_work: int
    index_maintenance_work: int
    lifetime_index_build_work: int
    lifetime_index_maintenance_work: int
    search_expansions: int
    checker_calls: int
    checker_expansions: int
    object_reads: int
    enumerated_items: int
    predicate_evaluations: int
    query_work: int
    outcome: str
    verdict_correct: bool | None = None
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        if self.k_status is CheckStatus.CANNOT_CHECK:
            if self.k is not None:
                raise ValueError("a CANNOT_CHECK record must not report a k value")
            if not self.cannot_check_reason:
                raise ValueError("a CANNOT_CHECK record requires a reason")
            if self.touched_ids:
                raise ValueError(
                    "a CANNOT_CHECK record must not present a partial touch list as k"
                )
        else:
            if self.k is None:
                raise ValueError("a MEASURED record must report k")
            if self.k != len(self.touched_ids):
                raise ValueError("k must equal the instrumented touch count")
            if self.k > self.n_objects:
                raise ValueError("k cannot exceed N under one object grammar")
        if len(set(self.touched_ids)) != len(self.touched_ids):
            raise ValueError("touched ids must be unique; repeats belong in object_reads")
        if self.persistent_bytes != self.store_bytes + self.index_bytes:
            raise ValueError("persistent_bytes must be store_bytes + index_bytes")

    # ---- derived --------------------------------------------------------

    @property
    def k_over_n(self) -> float | None:
        if self.k is None:
            return None
        if self.n_objects == 0:
            return 0.0 if self.k == 0 else None
        return self.k / self.n_objects

    @property
    def triggered_index_work(self) -> int:
        """Index work this operation itself caused, as opposed to amortised."""
        return self.index_build_work + self.index_maintenance_work

    @property
    def charged_total_work(self) -> int:
        """Query work with the index work this operation triggered added back."""
        return self.query_work + self.triggered_index_work

    @property
    def sparse_verdict(self) -> str:
        """The headline check, with the ``N``-sized build made undeniable.

        ``SPARSE_ONLY_AFTER_GLOBAL_BUILD_SCAN`` is the verdict for the hostile
        this module was written to catch: an arm whose ``k`` looks tiny because
        it walked all ``N`` objects to build an index a moment earlier.  Such
        an arm is not sparse, and the record says so without needing a reader
        to notice a second column.
        """
        if self.k_status is CheckStatus.CANNOT_CHECK:
            return "CANNOT_CHECK"
        budget = SPARSE_FRACTION * self.n_objects
        if self.k is not None and self.k > budget:
            return "NOT_SPARSE"
        if self.triggered_index_work > budget:
            return "SPARSE_ONLY_AFTER_GLOBAL_BUILD_SCAN"
        return "SPARSE"

    def as_dict(self) -> dict:
        return {
            "arm_id": self.arm_id,
            "scale_id": self.scale_id,
            "operation": self.operation,
            "thermal_state": self.thermal_state,
            "N_persistent_objects": self.n_objects,
            "k_touched_objects": self.k,
            "k_status": self.k_status.value,
            "k_over_n": None if self.k_over_n is None else round(self.k_over_n, 6),
            "sparse_verdict": self.sparse_verdict,
            "persistent_bytes": self.persistent_bytes,
            "store_bytes": self.store_bytes,
            "index_bytes": self.index_bytes,
            "active_bytes": self.active_bytes,
            "index_probes": self.index_probes,
            "index_build_work": self.index_build_work,
            "index_maintenance_work": self.index_maintenance_work,
            "lifetime_index_build_work": self.lifetime_index_build_work,
            "lifetime_index_maintenance_work": self.lifetime_index_maintenance_work,
            "search_expansions": self.search_expansions,
            "checker_calls": self.checker_calls,
            "checker_expansions": self.checker_expansions,
            "storage_reads": self.object_reads,
            "enumerated_items": self.enumerated_items,
            "predicate_evaluations": self.predicate_evaluations,
            "query_work": self.query_work,
            "charged_total_work": self.charged_total_work,
            "outcome": self.outcome,
            "verdict_correct": self.verdict_correct,
            "cannot_check_reason": self.cannot_check_reason,
            "touched_ids": list(self.touched_ids),
        }


def record_from_ledger(
    ledger: TouchLedger,
    *,
    arm_id: str,
    scale_id: str,
    operation: str,
    thermal_state: str,
    n_objects: int,
    store_bytes: int,
    index_bytes: int,
    lifetime_index_build_work: int,
    lifetime_index_maintenance_work: int,
    outcome: str,
    verdict_correct: bool | None = None,
) -> ResourceRecord:
    """Build a record from a finished ledger, honouring poisoning.

    The only place a ``ResourceRecord`` is constructed.  A poisoned ledger
    yields ``k = None`` and ``CANNOT_CHECK``; there is no argument to override
    it and no code path that supplies ``k`` from anywhere else.
    """
    poisoned = ledger.status is CheckStatus.CANNOT_CHECK
    return ResourceRecord(
        arm_id=arm_id,
        scale_id=scale_id,
        operation=operation,
        thermal_state=thermal_state,
        n_objects=n_objects,
        persistent_bytes=store_bytes + index_bytes,
        store_bytes=store_bytes,
        index_bytes=index_bytes,
        k=None if poisoned else len(ledger.touched_ids),
        k_status=CheckStatus.CANNOT_CHECK if poisoned else CheckStatus.MEASURED,
        touched_ids=() if poisoned else tuple(ledger.touched_ids),
        active_bytes=ledger.active_bytes,
        index_probes=ledger.index_probes,
        index_build_work=ledger.index_build_work,
        index_maintenance_work=ledger.index_maintenance_work,
        lifetime_index_build_work=lifetime_index_build_work,
        lifetime_index_maintenance_work=lifetime_index_maintenance_work,
        search_expansions=ledger.search_expansions,
        checker_calls=ledger.checker_calls,
        checker_expansions=ledger.checker_expansions,
        object_reads=ledger.object_reads,
        enumerated_items=ledger.enumerated_items,
        predicate_evaluations=ledger.predicate_evaluations,
        query_work=ledger.query_work,
        outcome=outcome,
        verdict_correct=verdict_correct,
        cannot_check_reason=ledger.cannot_check_reason,
    )


@dataclass(frozen=True)
class RevisionRecord:
    """One revocation event, scored against the generator's exact cone.

    ``expected_changed_ids`` comes from :meth:`CompetenceStore.true_cone` and
    is the scorer's, not the arm's.  ``observed_changed_ids`` is what the arm
    actually invalidated using only what its own architecture affords.  The
    difference is the endpoint: ``S3`` of the protocol is cone size over store
    size, and ``S4`` is stale survivors and collateral invalidations counted
    exactly.
    """

    arm_id: str
    scale_id: str
    trigger_support_id: str
    trigger_kind: str  # LOCAL | GLOBALLY_SHARED
    n_objects: int
    expected_changed_ids: tuple[str, ...]
    observed_changed_ids: tuple[str, ...]
    touched_ids: tuple[str, ...]
    k: int | None
    k_status: CheckStatus
    #: ``None`` on an uninstrumented path.  A revocation performed through an
    #: unaudited accessor did real work that nothing counted; reporting ``0``
    #: there would be the same lie as reporting ``k = 1``.
    revision_work: int | None
    index_probes: int
    index_maintenance_work: int
    object_reads: int
    enumerated_items: int
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        for name in ("expected_changed_ids", "observed_changed_ids", "touched_ids"):
            xs = getattr(self, name)
            if len(set(xs)) != len(xs):
                raise ValueError(f"{name} must be unique")
        if self.k_status is CheckStatus.CANNOT_CHECK:
            if not self.cannot_check_reason:
                raise ValueError("a CANNOT_CHECK revision record requires a reason")
            if self.k is not None or self.revision_work is not None:
                raise ValueError(
                    "a CANNOT_CHECK revision record must not report k or revision_work"
                )
        elif self.k is None or self.revision_work is None:
            raise ValueError("a MEASURED revision record must report k and revision_work")

    @property
    def cone_size(self) -> int:
        return len(self.observed_changed_ids)

    @property
    def cone_fraction(self) -> float:
        if self.n_objects == 0:
            return 0.0
        return len(self.observed_changed_ids) / self.n_objects

    @property
    def expected_cone_size(self) -> int:
        return len(self.expected_changed_ids)

    @property
    def stale_survivor_ids(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.expected_changed_ids) - set(self.observed_changed_ids)))

    @property
    def collateral_invalidated_ids(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.observed_changed_ids) - set(self.expected_changed_ids)))

    @property
    def dependency_precision(self) -> float:
        expected, observed = set(self.expected_changed_ids), set(self.observed_changed_ids)
        if not observed:
            return 1.0 if not expected else 0.0
        return len(expected & observed) / len(observed)

    @property
    def dependency_recall(self) -> float:
        expected, observed = set(self.expected_changed_ids), set(self.observed_changed_ids)
        if not expected:
            return 1.0
        return len(expected & observed) / len(expected)

    @property
    def exact_revocation(self) -> bool:
        return not self.stale_survivor_ids and not self.collateral_invalidated_ids

    def as_dict(self) -> dict:
        return {
            "arm_id": self.arm_id,
            "scale_id": self.scale_id,
            "trigger_support_id": self.trigger_support_id,
            "trigger_kind": self.trigger_kind,
            "N_persistent_objects": self.n_objects,
            "cone_size": self.cone_size,
            "expected_cone_size": self.expected_cone_size,
            "cone_fraction": round(self.cone_fraction, 6),
            "revision_work": self.revision_work,
            "index_probes": self.index_probes,
            "index_maintenance_work": self.index_maintenance_work,
            "storage_reads": self.object_reads,
            "enumerated_items": self.enumerated_items,
            "k_touched_objects": self.k,
            "k_status": self.k_status.value,
            "dependency_precision": round(self.dependency_precision, 6),
            "dependency_recall": round(self.dependency_recall, 6),
            "stale_survivors": len(self.stale_survivor_ids),
            "collateral_invalidations": len(self.collateral_invalidated_ids),
            "exact_revocation": self.exact_revocation,
        }


# --------------------------------------------------------------------------
# the frozen plan and the commitment-derived draw
# --------------------------------------------------------------------------

#: Frozen before any outcome.  Editing any value here changes the commitment
#: and therefore changes the probe positions and the family order, which is
#: what makes analysis drift mechanically visible (CL-D4).
SCALING_PLAN: dict[str, Any] = {
    "protocol": "COGNITIVE_LADDER_PROTOCOL_V1",
    "rung": "CL-S1/S3 active-subspace scaling",
    "base_families": 20,
    "multipliers": [1, 3, 10, 30],
    "probe_family_moves": [1, 3, 4],
    "evidence_blocks": 2,
    "evidence_block_size": 8,
    "probe_position_low": 40,
    "probe_position_high": 96,
    "probe_positions": 5,
    "move_alphabet": 10,
    "move_set_max_size": 5,
    "language": {"max_preperiod": 6, "max_period": 12, "max_value": 8},
    "arms": [
        "ocm_arm",
        "global_scan_ablation",
        "index_parent",
        "cache_parent",
        "rebuild_index_hostile",
        "unaudited_scan_hostile",
    ],
    "endpoints": [
        "k(N)",
        "query_work(N)",
        "persistent_bytes(N)",
        "revision_work(N) after LOCAL revocation",
        "revision_work(N) after GLOBALLY_SHARED revocation",
    ],
    "sparse_fraction": SPARSE_FRACTION,
    "index_entry_bytes": INDEX_ENTRY_BYTES,
    "loglog_residual_threshold": 0.05,
    "fit_basis": "log10, ordinary least squares, 4 points, 2 free parameters",
}

COMMITMENT: Commitment = commit(SCALING_PLAN)

LANGUAGE = GrundyRuleLanguage(
    max_preperiod=SCALING_PLAN["language"]["max_preperiod"],
    max_period=SCALING_PLAN["language"]["max_period"],
    max_value=SCALING_PLAN["language"]["max_value"],
)


def _stream_rng(label: str) -> random.Random:
    """A deterministic stream derived from the pre-registration commitment."""
    return random.Random(COMMITMENT.stream(label) % (2**63))


@lru_cache(maxsize=None)
def probe_positions() -> tuple[int, ...]:
    """The frozen probe positions, drawn from the protected stream.

    Every position lies strictly above the training support (``0..15``), so a
    verbatim position cache must miss on all of them.  That is CL-D1(b) applied
    to the scaling harness: extrapolation beyond training magnitude is the only
    place a method and a cache can be told apart by behaviour rather than by
    byte count.
    """
    rng = _stream_rng("scaling-probe-positions-v1")
    lo = SCALING_PLAN["probe_position_low"]
    hi = SCALING_PLAN["probe_position_high"]
    return tuple(sorted(rng.sample(range(lo, hi + 1), SCALING_PLAN["probe_positions"])))


@lru_cache(maxsize=None)
def move_set_order() -> tuple[tuple[int, ...], ...]:
    """The frozen family order.  Probe family first, then a committed shuffle.

    Taking the first ``F`` of a single frozen order means the family set at
    scale ``3x`` is a superset of the set at ``1x``.  Nested scales matter: if
    each scale drew its own families, a change in ``k`` between scales could be
    a change of families rather than a change of ``N``.
    """
    alphabet = SCALING_PLAN["move_alphabet"]
    max_size = SCALING_PLAN["move_set_max_size"]
    candidates: list[tuple[int, ...]] = []
    for size in range(1, max_size + 1):
        candidates.extend(_combinations(tuple(range(1, alphabet + 1)), size))
    probe = tuple(SCALING_PLAN["probe_family_moves"])
    rest = [m for m in candidates if m != probe]
    rng = _stream_rng("scaling-family-order-v1")
    rng.shuffle(rest)
    return (probe,) + tuple(rest)


def _combinations(pool: tuple[int, ...], size: int) -> list[tuple[int, ...]]:
    """Sorted combinations without ``itertools``-flavoured surprises."""
    out: list[tuple[int, ...]] = []

    def rec(start: int, acc: tuple[int, ...]) -> None:
        if len(acc) == size:
            out.append(acc)
            return
        for i in range(start, len(pool)):
            rec(i + 1, acc + (pool[i],))

    rec(0, ())
    return out


# --------------------------------------------------------------------------
# the catalogue: identical information for every arm
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class FamilySpec:
    """One family's evidence and the method induced from it.

    ``evidence_blocks`` is the same evidence every arm receives.  The method
    arms turn it into one ``method`` object plus one ``support`` object per
    block; the cache arm turns it into one cached solved position per labelled
    observation.  Same information, different persistent representation --
    which is exactly the comparison protocol §6's ``A_cache`` arm is for.
    """

    family_id: str
    moves: tuple[int, ...]
    relation: str
    evidence_blocks: tuple[tuple[tuple[int, int], ...], ...]
    rule: GrundyRule

    @property
    def support_ids(self) -> tuple[str, ...]:
        return tuple(
            f"S:{self.family_id}:b{i}" for i in range(len(self.evidence_blocks))
        ) + (SHARED_SUPPORT_ID,)

    @property
    def method_id(self) -> str:
        return f"M:{self.family_id}"

    @property
    def evidence(self) -> tuple[tuple[int, int], ...]:
        return tuple(obs for block in self.evidence_blocks for obs in block)


@dataclass(frozen=True)
class CompetenceCatalogue:
    """The frozen contents of the persistent state at one scale."""

    scale_id: str
    multiplier: int
    families: tuple[FamilySpec, ...]
    probe_family_id: str
    probe_moves: tuple[int, ...]

    @property
    def probe(self) -> FamilySpec:
        return self.families[0]


def _family_spec(moves: tuple[int, ...], relation: str) -> FamilySpec:
    game = SubtractionGame(moves)
    blocks = SCALING_PLAN["evidence_blocks"]
    size = SCALING_PLAN["evidence_block_size"]
    table = game.grundy_upto(blocks * size - 1)
    evidence_blocks = tuple(
        tuple((n, table[n]) for n in range(b * size, (b + 1) * size)) for b in range(blocks)
    )
    evidence = tuple(obs for block in evidence_blocks for obs in block)
    rule = LANGUAGE.induce(evidence)
    if rule is None:  # pragma: no cover -- the language always covers 0..15
        raise AssertionError(f"no hypothesis in {LANGUAGE.language_id} fits {moves}")
    return FamilySpec(
        family_id=game.family_id,
        moves=moves,
        relation=relation,
        evidence_blocks=evidence_blocks,
        rule=rule,
    )


@lru_cache(maxsize=None)
def _all_family_specs(count: int) -> tuple[FamilySpec, ...]:
    order = move_set_order()
    if count > len(order):
        raise ValueError(f"only {len(order)} registered families; asked for {count}")
    specs = []
    for i, moves in enumerate(order[:count]):
        if i == 0:
            relation = "probe"
        elif i <= max(1, count // 10):
            relation = "related"
        else:
            relation = "distractor"
        specs.append(_family_spec(moves, relation))
    return tuple(specs)


def build_catalogue(multiplier: int) -> CompetenceCatalogue:
    """The catalogue at scale ``multiplier``; nested in the smaller scales."""
    count = SCALING_PLAN["base_families"] * multiplier
    specs = _all_family_specs(count)
    probe = specs[0]
    return CompetenceCatalogue(
        scale_id=f"{multiplier}x",
        multiplier=multiplier,
        families=specs,
        probe_family_id=probe.family_id,
        probe_moves=probe.moves,
    )


def populate_store(catalogue: CompetenceCatalogue) -> CompetenceStore:
    """Build the method-and-support store for one catalogue.

    Every method-holding arm receives a store built by this one function, so
    ``N``, the byte totals and the dependency graph are identical across arms
    and any difference in the reported numbers is a difference of retrieval
    architecture and nothing else.
    """
    store = CompetenceStore(f"store@{catalogue.scale_id}")
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
    for spec in catalogue.families:
        for i, block in enumerate(spec.evidence_blocks):
            store.add_support(
                f"S:{spec.family_id}:b{i}",
                spec.family_id,
                {"kind": "evidence_block", "family": spec.family_id, "observations": [list(o) for o in block]},
            )
        store.add_competence(
            spec.family_id, spec.rule, spec.support_ids, relation=spec.relation
        )
    return store


def populate_cache_store(catalogue: CompetenceCatalogue) -> CompetenceStore:
    """The same information, stored as solved positions instead of methods.

    The cache parent sees exactly the evidence the method arms see.  It keeps
    the evidence blocks (it must: they are the episodes) and, in addition, one
    ``cached_position`` object per labelled observation.  It induces nothing,
    so it holds no method object and no periodicity lemma -- and that absence
    is not a handicap imposed by this harness, it is what "cache rather than
    method" means.

    Note the consequence for revision, which is genuinely in the cache's
    favour: an exactly solved position does not depend on the periodicity
    lemma, so revoking the lemma correctly invalidates nothing in this store.
    The cache still has to scan every object to discover that, because it holds
    no support-to-dependent index.
    """
    store = CompetenceStore(f"cache@{catalogue.scale_id}")
    # The lemma is part of the information stream and is persisted by both
    # architectures.  The difference is that no cached position *declares* a
    # dependency on it, so its ground-truth cone in this store is itself alone.
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
    for spec in catalogue.families:
        for i, block in enumerate(spec.evidence_blocks):
            support_id = f"S:{spec.family_id}:b{i}"
            store.add_support(
                support_id,
                spec.family_id,
                {"kind": "evidence_block", "family": spec.family_id, "observations": [list(o) for o in block]},
            )
            for position, grundy in block:
                store.add_cached_position(spec.family_id, position, grundy, (support_id,))
    return store


# --------------------------------------------------------------------------
# the independent checker
# --------------------------------------------------------------------------


def certify(moves: Sequence[int], position: int, ledger: TouchLedger) -> bool:
    """Exact verdict from the independent checker.

    The checker recomputes the Grundy value from the game definition.  It does
    not consult the store, any index, or any learned object, which is the
    independence clause CL-D1(c).  Its internal expansions are charged to
    ``checker_expansions`` and are reported in every record; they are excluded
    from ``query_work`` for the reason given on :attr:`TouchLedger.query_work`.
    """
    work = Work()
    game = SubtractionGame(tuple(moves))
    verdict = game.grundy_upto(position, work=work)[position] == 0
    ledger.checker_calls += 1
    ledger.checker_expansions += work.expansions
    return verdict


# --------------------------------------------------------------------------
# log-log fitting, with the model's failure reported rather than assumed
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class LogLogFit:
    """An ordinary least-squares line through ``(log10 N, log10 y)``.

    A slope is only worth reading if the line describes the points.  This
    dataclass therefore always carries the residual, and ``verdict`` refuses
    the power-law label when the residual exceeds the threshold frozen in the
    plan.  Four points and two parameters leave two degrees of freedom; the
    fit is a *description of these four scales*, not an extrapolation licence,
    and ``POWER_LAW_CONSISTENT`` means only "no visible curvature at this
    resolution".
    """

    label: str
    xs: tuple[float, ...]
    ys: tuple[float | None, ...]
    slope: float | None
    intercept: float | None
    rms_log_residual: float | None
    max_log_residual: float | None
    r_squared: float | None
    verdict: str
    note: str = ""

    @property
    def fits(self) -> bool:
        return self.verdict in ("POWER_LAW_CONSISTENT", "CONSTANT_IN_N")

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "slope": None if self.slope is None else round(self.slope, 4),
            "rms_log_residual": None
            if self.rms_log_residual is None
            else round(self.rms_log_residual, 5),
            "max_log_residual": None
            if self.max_log_residual is None
            else round(self.max_log_residual, 5),
            "r_squared": None if self.r_squared is None else round(self.r_squared, 5),
            "verdict": self.verdict,
            "xs": list(self.xs),
            "ys": list(self.ys),
            "note": self.note,
        }


def fit_loglog(
    xs: Sequence[float],
    ys: Sequence[float | None],
    *,
    label: str = "",
    residual_threshold: float | None = None,
) -> LogLogFit:
    """Fit ``log10 y = slope * log10 x + intercept`` and report the residual.

    Four refusals are built in, because each of them is a place where a
    convenient number could otherwise be manufactured:

    * any ``y`` is ``None`` (a ``CANNOT_CHECK`` coordinate) -> ``CANNOT_CHECK``;
      unmeasurability propagates and does not become a zero;
    * any ``x`` or ``y`` is non-positive -> ``UNDEFINED_NONPOSITIVE_VALUES``;
      ``log 0`` is not ``-inf`` for reporting purposes, it is a missing point;
    * every ``y`` identical -> ``CONSTANT_IN_N``, slope exactly ``0``, and
      ``r_squared`` left ``None`` because the total sum of squares is zero and
      a coefficient of determination is undefined, not ``1``;
    * residual above threshold -> ``POWER_LAW_NOT_SUPPORTED``.  The slope is
      still reported, with the explicit statement that the model does not fit,
      so nobody quotes it as an exponent.
    """
    threshold = (
        residual_threshold
        if residual_threshold is not None
        else SCALING_PLAN["loglog_residual_threshold"]
    )
    xs_t = tuple(float(x) for x in xs)
    ys_t = tuple(None if y is None else float(y) for y in ys)
    if len(xs_t) != len(ys_t):
        raise ValueError("xs and ys must have the same length")
    if any(y is None for y in ys_t):
        return LogLogFit(
            label, xs_t, ys_t, None, None, None, None, None, "CANNOT_CHECK",
            "at least one coordinate was CANNOT_CHECK; unmeasurability propagates",
        )
    if len(xs_t) < 3:
        return LogLogFit(
            label, xs_t, ys_t, None, None, None, None, None, "TOO_FEW_POINTS",
            "fewer than three scales; a slope here would be an interpolation, not a fit",
        )
    if any(x <= 0 for x in xs_t) or any(y <= 0 for y in ys_t):  # type: ignore[operator]
        return LogLogFit(
            label, xs_t, ys_t, None, None, None, None, None,
            "UNDEFINED_NONPOSITIVE_VALUES",
            "a non-positive coordinate has no logarithm; the point is missing, not zero",
        )
    lx = [math.log10(x) for x in xs_t]
    ly = [math.log10(y) for y in ys_t]  # type: ignore[arg-type]
    n = len(lx)
    mx = sum(lx) / n
    my = sum(ly) / n
    sxx = sum((x - mx) ** 2 for x in lx)
    if sxx == 0:
        return LogLogFit(
            label, xs_t, ys_t, None, None, None, None, None, "DEGENERATE_X",
            "every scale has the same N; there is no axis to fit along",
        )
    sxy = sum((x - mx) * (y - my) for x, y in zip(lx, ly))
    slope = sxy / sxx
    intercept = my - slope * mx
    residuals = [y - (slope * x + intercept) for x, y in zip(lx, ly)]
    rms = math.sqrt(sum(r * r for r in residuals) / n)
    worst = max(abs(r) for r in residuals)
    sst = sum((y - my) ** 2 for y in ly)
    if sst == 0:
        return LogLogFit(
            label, xs_t, ys_t, 0.0, intercept, 0.0, 0.0, None, "CONSTANT_IN_N",
            "y is identical at every scale; slope is exactly zero and r^2 is undefined",
        )
    r2 = 1.0 - sum(r * r for r in residuals) / sst
    verdict = (
        "POWER_LAW_CONSISTENT" if rms <= threshold else "POWER_LAW_NOT_SUPPORTED"
    )
    note = (
        f"rms log10 residual {rms:.4f} <= threshold {threshold}; no visible curvature "
        f"over {n} scales, which is not evidence of a power law beyond them"
        if verdict == "POWER_LAW_CONSISTENT"
        else (
            f"rms log10 residual {rms:.4f} > threshold {threshold}; a straight line in "
            "log-log does NOT describe these points and the slope must not be quoted "
            "as an exponent"
        )
    )
    return LogLogFit(label, xs_t, ys_t, slope, intercept, rms, worst, r2, verdict, note)
