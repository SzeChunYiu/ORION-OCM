"""Six arms over one store, and the frozen scale sweep that separates them.

``scaling.py`` supplies the world: ``N`` logical competence objects behind an
instrumented read path, an exact independent checker, a commitment-derived
catalogue and a log-log fitter that refuses to quote an exponent when a
straight line does not describe the points.  This module supplies the arms and
the sweep.

Every arm is handed **identical information**: the same catalogue, the same
evidence blocks, the same probe positions, and one checker call per probe
whether or not it managed to answer.  They differ only in what they persist and
how they reach it.  That is protocol §6's identification strategy applied to the
scaling endpoint: if a difference in ``k(N)`` survives when the information is
held fixed it is a difference of architecture, and if it does not survive there
is nothing to claim.

The arms
--------

``ocm_arm``
    Scoped lookup keyed on family identity, plus a reverse index from a support
    to the methods that declared it.  Invalidation is eager: a revocation marks
    the dependent methods there and then, so the *query* path is a single index
    probe and a single read -- exactly what a plain index does.

``global_scan_ablation``
    The same store with the index removed.  An ablation, not a parent: it shows
    what the same knowledge costs without scoping, and its ``k`` must equal
    ``N`` exactly.  It is also this module's self-check, because a harness in
    which the linear arm does not look linear cannot be believed about the
    sparse one.

``index_parent``
    A plain database-style index, built the same way, with no dependency
    tracking.  **This is the strongest parent and it is expected to tie.**  It
    performs the identical probe-and-read, so its ``k``, its ``k/N`` and its
    query work match the OCM arm at every scale.  The honest report for
    ``k(N)`` is ``PARENT_SUFFICIENT``: answering a query without reading
    everything is what an index is for, the family key was *supplied* by the
    catalogue, and crediting cheap lookup under a supplied key to cognition
    would be laundering.  The only coordinate where the two can separate is
    what happens after a support is withdrawn.

``cache_parent``
    Solved positions instead of methods (protocol §6 ``A_cache``).  Same
    evidence, several times the persistent objects and bytes, and every frozen
    probe position lies above its cached magnitude, so it answers **none** of
    them.  Its ``k`` is ``0``: it touched no persistent object at all.  That is
    this module's own cautionary tale about its headline coordinate -- an arm
    can be maximally sparse and completely useless in the same row, so ``k`` is
    only readable next to whether the arm answered.

``rebuild_index_hostile``
    The headline hostile.  Per-query ``k`` identical to the OCM arm's, because
    it rebuilt its index by scanning all ``N`` objects immediately beforehand
    on a build ledger whose touches never reach the query record.  ``k`` does
    not catch it; the accounting does.  ``index_build_work`` is charged to the
    query that triggered it, ``sparse_verdict`` comes back
    ``SPARSE_ONLY_AFTER_GLOBAL_BUILD_SCAN``, and over the five frozen probes
    its lifetime build work is five times an honest index's.

``unaudited_scan_hostile``
    Reaches payloads through the store's uninstrumented accessor.  It answers
    correctly and would report ``k = 1``.  It reports ``CANNOT_CHECK`` instead,
    with a reason, because the accessor poisons the ledger and
    ``record_from_ledger`` will not emit a number from a poisoned ledger.

Revocation, and what the parents do about it
--------------------------------------------

Two revocations per arm per scale:

* a **LOCAL** support -- one evidence block of the probe family's method.  The
  exact cone is two objects at every scale.
* the **GLOBALLY SHARED** support -- the periodicity lemma every induced rule
  depends on.  This is the hostile control.  Its cone is genuinely most of the
  store, and an arm whose dependency structure reported it as local would be
  broken rather than efficient.  The sweep exists as much to catch that as to
  show the local cone is small.

Only the OCM arm holds support-to-dependent edges, so only it invalidates
anything.  Every other arm observes the **empty set**: it does not respond to a
revocation at all, does no revision work, and silently keeps serving methods
whose support has been withdrawn.  The parent's cost is therefore not work, it
is the entire true cone left standing as stale survivors, counted exactly.

**State this limitation with the result.**  "Observes nothing" is a modelling
choice about default behaviour, not a proof of impossibility.  The store's
objects do carry their declared ``supports``, so a strictly stronger parent
could rediscover the exact cone by scanning all ``N`` at revocation time.  Such
a parent would match the OCM arm on correctness and lose only on work.  The
unaudited hostile happens to demonstrate exactly that -- it recovers both cones
exactly by scanning declared supports -- but it does so through the
uninstrumented path, so its revision work comes back ``CANNOT_CHECK`` and it is
a hostile rather than a parent.  An *audited* version of that parent is not run
here, so the gap reported is about what a plain index does by default, not
about what is achievable.

A second limitation, equally load-bearing: the OCM arm's reverse index is built
from the same declarations that populated the store, so its revocation is exact
**by construction**.  These numbers measure the cost of exact revocation, not
the discovery of dependencies.  Protocol attack A9 is not answered here and is
not claimed to be.

Parents: relational index structures and query planning; truth maintenance
systems (Doyle) and dependency-directed backtracking; cache and memoization
architectures.  No novelty is claimed for any of them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from methods import GrundyRule
from scaling import (
    COMMITMENT,
    INDEX_ENTRY_BYTES,
    SCALING_PLAN,
    SHARED_SUPPORT_ID,
    CheckStatus,
    CompetenceCatalogue,
    CompetenceObject,
    CompetenceStore,
    LogLogFit,
    ResourceRecord,
    RevisionRecord,
    TouchLedger,
    build_catalogue,
    certify,
    fit_loglog,
    populate_cache_store,
    populate_store,
    probe_positions,
    record_from_ledger,
)

__all__ = [
    "FamilyIndex",
    "ScalingArm",
    "OcmArm",
    "GlobalScanAblation",
    "IndexParent",
    "CacheParent",
    "RebuildIndexHostile",
    "UnauditedScanHostile",
    "ocm_arm",
    "global_scan_ablation",
    "index_parent",
    "cache_parent",
    "rebuild_index_hostile",
    "unaudited_scan_hostile",
    "ARMS",
    "ARM_ROLES",
    "ArmResult",
    "SweepRow",
    "ScaleSweep",
    "SWEEP_NOTES",
    "local_support_id",
    "run_arm",
    "sweep",
    "sweep_table",
    "fits_for",
    "run_sweep",
    "format_sweep_table",
    "format_fit_table",
]


def _revision_work(ledger: TouchLedger) -> int:
    """Work spent performing a revocation.

    The same primitive units as ``query_work``, plus index maintenance --
    because maintaining the index *is* the revocation for an indexed arm, and
    excluding it would be exactly the hiding this module refuses.
    """
    return (
        ledger.index_probes
        + ledger.object_reads
        + ledger.enumerated_items
        + ledger.predicate_evaluations
        + ledger.index_maintenance_work
    )


def _rule_of(obj: CompetenceObject) -> GrundyRule:
    """Rebuild the periodic rule from a stored method payload.

    The store persists the rule as plain data, never as a live object, which is
    what a real restart would hand back.  Rebuilding here rather than holding a
    Python reference keeps every arm honest about what actually crossed the
    persistence boundary.
    """
    return GrundyRule(
        preperiod=int(obj.payload["preperiod"]),
        period=int(obj.payload["period"]),
        values=tuple(int(v) for v in obj.payload["values"]),
    )


# --------------------------------------------------------------------------
# the index, with its construction charged
# --------------------------------------------------------------------------


class FamilyIndex:
    """Family identity -> the method that serves it.

    Construction enumerates every object in the store through the instrumented
    scan, and that enumeration is charged to ``build_work``.  Nothing here is
    learned: the key is the family identity the catalogue already supplies.  An
    index is a filing decision, and the cost of filing is reported so that the
    filing cannot be mistaken for cognition.

    ``track_dependencies`` additionally builds the reverse index from a support
    to the methods that declared it.  Those edges are counted in ``entries``
    and therefore in ``bytes``: a dependency map is persistent index state, and
    a module whose whole thesis is "charge the index" cannot leave its own
    index uncharged.  The OCM arm consequently carries strictly more index
    bytes than the plain parent, which is the price of the only thing it can do
    that the parent cannot.
    """

    def __init__(
        self,
        store: CompetenceStore,
        *,
        track_dependencies: bool,
        ledger: TouchLedger,
    ) -> None:
        self.track_dependencies = track_dependencies
        self.build_work = 0
        self.maintenance_work = 0
        self._by_family: dict[str, str] = {}
        self._dependents: dict[str, list[str]] = {}
        for obj in store.scan(ledger):
            self.build_work += 1
            if obj.object_class != "method":
                continue
            self._by_family[obj.family_id] = obj.object_id
            if track_dependencies:
                for support_id in obj.supports:
                    self._dependents.setdefault(support_id, []).append(obj.object_id)
        ledger.index_build_work += self.build_work

    @property
    def entries(self) -> int:
        return len(self._by_family) + sum(len(v) for v in self._dependents.values())

    @property
    def bytes(self) -> int:
        return self.entries * INDEX_ENTRY_BYTES

    def probe(self, family_id: str, ledger: TouchLedger) -> str | None:
        ledger.probe_index()
        return self._by_family.get(family_id)

    def dependents_of(self, support_id: str, ledger: TouchLedger) -> tuple[str, ...]:
        """Methods the index knows depend on ``support_id``.

        One probe of the reverse index, not a scan of it.  Without dependency
        tracking the honest answer is the empty tuple: the arm does not know,
        and it will go on serving a method whose support has been withdrawn.
        """
        if not self.track_dependencies:
            return ()
        ledger.probe_index()
        return tuple(sorted(self._dependents.get(support_id, ())))

    def forget_family(self, family_id: str, ledger: TouchLedger) -> None:
        if self._by_family.pop(family_id, None) is not None:
            self.maintenance_work += 1
            ledger.index_maintenance_work += 1


# --------------------------------------------------------------------------
# base
# --------------------------------------------------------------------------


class ScalingArm:
    """One persistent-state architecture, installed at one scale.

    Subclasses implement ``_install``, ``_answer`` and (optionally)
    ``_invalidate``.  Everything else -- the checker call, the record
    construction, the cold/warm split, the ground-truth cone comparison -- is
    shared, so no arm can differ from another in the bookkeeping rather than in
    the architecture.
    """

    arm_id = "abstract"
    role = "ARM"
    tracks_dependencies = False

    def __init__(self, catalogue: CompetenceCatalogue) -> None:
        self.catalogue = catalogue
        self.scale_id = catalogue.scale_id
        self.store = self._make_store(catalogue)
        self.queries_served = 0
        self.last_build_record: ResourceRecord | None = None
        build_ledger = TouchLedger()
        self._install(build_ledger)
        self.install_record = self._record(
            build_ledger,
            operation="INDEX_BUILD",
            thermal_state="COLD",
            outcome="INSTALL",
            verdict_correct=None,
        )

    # ---- construction ---------------------------------------------------

    def _make_store(self, catalogue: CompetenceCatalogue) -> CompetenceStore:
        return populate_store(catalogue)

    def _install(self, ledger: TouchLedger) -> None:
        raise NotImplementedError

    # ---- reporting surface ----------------------------------------------

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

    def _answer(self, position: int, ledger: TouchLedger) -> tuple[str, bool | None]:
        raise NotImplementedError

    def query(self, position: int) -> ResourceRecord:
        """Answer "is ``position`` a P-position in the probe family?".

        The independent checker is called exactly once per query by every arm,
        including arms that could not answer.  That keeps ``checker_calls`` a
        constant across the comparison and stops an arm looking cheap by
        declining to establish the truth.
        """
        ledger = TouchLedger()
        thermal = "COLD" if self.queries_served == 0 else "WARM"
        outcome, verdict = self._answer(position, ledger)
        truth = certify(self.catalogue.probe_moves, position, ledger)
        correct = None if verdict is None else (verdict == truth)
        self.queries_served += 1
        return self._record(
            ledger,
            operation="QUERY",
            thermal_state=thermal,
            outcome=outcome,
            verdict_correct=correct,
        )

    # ---- the revocation -------------------------------------------------

    def _invalidate(self, support_id: str, ledger: TouchLedger) -> list[str]:
        """Return the objects this arm actually invalidated.

        The default is the empty list: an architecture with no dependency
        record does not respond to a revocation.  That is not a strawman, it is
        what "no truth maintenance" means, and its cost shows up as stale
        survivors rather than as work.
        """
        return []

    def revoke(self, support_id: str, *, trigger_kind: str) -> RevisionRecord:
        """Revoke one support and report the cone the arm actually invalidated.

        ``expected_changed_ids`` comes from the store's ground-truth dependency
        graph, which ``_invalidate`` never consults -- the same separation
        ``escalation.py`` keeps between ``diagnose`` and a world's registered
        ``minimum_sufficient_level``.  The true cone includes the withdrawn
        support itself, so an arm that tracks dependencies at all is credited
        with knowing that the support it just revoked is affected.
        """
        expected = self.store.true_cone(support_id)
        ledger = TouchLedger()
        self.store.revoke_support(support_id)
        observed = self._invalidate(support_id, ledger)
        poisoned = ledger.status is CheckStatus.CANNOT_CHECK
        ledger.revision_work = None if poisoned else _revision_work(ledger)
        return RevisionRecord(
            arm_id=self.arm_id,
            scale_id=self.scale_id,
            trigger_support_id=support_id,
            trigger_kind=trigger_kind,
            n_objects=self.n_objects,
            expected_changed_ids=tuple(sorted(expected)),
            observed_changed_ids=tuple(sorted(set(observed))),
            touched_ids=() if poisoned else tuple(ledger.touched_ids),
            k=None if poisoned else len(ledger.touched_ids),
            k_status=CheckStatus.CANNOT_CHECK if poisoned else CheckStatus.MEASURED,
            revision_work=ledger.revision_work,
            index_probes=ledger.index_probes,
            index_maintenance_work=ledger.index_maintenance_work,
            object_reads=ledger.object_reads,
            enumerated_items=ledger.enumerated_items,
            cannot_check_reason=ledger.cannot_check_reason,
        )


class _IndexedArm(ScalingArm):
    """Shared body of the two arms that answer through a family index.

    They are one class with one flag, on purpose.  The claim under test is that
    the OCM arm and the plain index differ, and the cheapest way to manufacture
    a difference is to write two implementations and let an incidental
    asymmetry creep into the query path.  Here the query path is literally the
    same code, so any difference in the reported numbers has to come from the
    flag.
    """

    def _install(self, ledger: TouchLedger) -> None:
        self.index = FamilyIndex(
            self.store, track_dependencies=self.tracks_dependencies, ledger=ledger
        )

    @property
    def index_bytes(self) -> int:
        return self.index.bytes

    @property
    def lifetime_index_build_work(self) -> int:
        return self.index.build_work

    @property
    def lifetime_index_maintenance_work(self) -> int:
        return self.index.maintenance_work

    def _answer(self, position: int, ledger: TouchLedger) -> tuple[str, bool | None]:
        method_id = self.index.probe(self.catalogue.probe_family_id, ledger)
        if method_id is None:
            return "NO_METHOD_FOR_FAMILY", None
        method = self.store.read(method_id, ledger)
        if self.store.is_revoked(method_id):
            return "METHOD_REVOKED", None
        ledger.predicate_evaluations += 1
        return "ANSWERED", _rule_of(method).is_p_position(position)


class OcmArm(_IndexedArm):
    """Scoped lookup with a reverse index from support to dependent methods.

    Invalidation is eager.  On a revocation the dependent methods are marked
    there and then, which is why the query path can be a single probe and a
    single read: a live method needs no support re-verification, because a
    method whose support was withdrawn is no longer live.  The consequence is
    that this arm's query numbers are *identical* to the plain index parent's,
    and that identity is the honest headline of the sweep rather than something
    to be engineered away.
    """

    arm_id = "ocm_arm"
    role = "OCM"
    tracks_dependencies = True

    def _invalidate(self, support_id: str, ledger: TouchLedger) -> list[str]:
        observed = [support_id]
        self.store.read(support_id, ledger)
        for method_id in self.index.dependents_of(support_id, ledger):
            method = self.store.read(method_id, ledger)
            self.store.revoke_method(method_id)
            self.index.forget_family(method.family_id, ledger)
            observed.append(method_id)
        return observed


class IndexParent(_IndexedArm):
    """A plain database-style index.  The strongest parent, expected to tie.

    Same probe, same read, same rule evaluation, one fewer index structure to
    maintain.  It matches the OCM arm exactly on ``k``, ``k/N`` and query work
    at every scale, which is the correct and reportable ``PARENT_SUFFICIENT``
    outcome for the ``k(N)`` endpoint.

    It holds no dependency edges, so it does nothing at all when a support is
    withdrawn: no work, no invalidation, and the whole true cone left standing.
    That is the default behaviour of an index without truth maintenance.  The
    module docstring records the stronger variant -- rediscover the cone by
    scanning every object's declared supports -- which would close the
    correctness gap at ``O(N)`` cost and is not run here.
    """

    arm_id = "index_parent"
    role = "PARENT"
    tracks_dependencies = False


# --------------------------------------------------------------------------
# the ablation
# --------------------------------------------------------------------------


class GlobalScanAblation(ScalingArm):
    """The same store, no index.  The OCM ablation, not a parent.

    ``k`` must equal ``N`` here at every scale.  If it ever does not, the touch
    instrumentation is broken and nothing else in this module may be believed.
    """

    arm_id = "global_scan_ablation"
    role = "ABLATION"

    def _install(self, ledger: TouchLedger) -> None:
        return None

    def _answer(self, position: int, ledger: TouchLedger) -> tuple[str, bool | None]:
        method = self.store.query(self.catalogue.probe_family_id, ledger)
        if method is None:
            return "NO_METHOD_FOR_FAMILY", None
        ledger.predicate_evaluations += 1
        return "ANSWERED", _rule_of(method).is_p_position(position)


# --------------------------------------------------------------------------
# the cache parent
# --------------------------------------------------------------------------


class CacheParent(ScalingArm):
    """Solved positions rather than methods (protocol §6 ``A_cache``).

    Same evidence, different persistent representation, and a real index over
    ``(family, position)`` so that the comparison is against a competently
    built cache rather than a linear one.  Every frozen probe position lies
    above the cached magnitude by construction, so every probe is a miss and
    this arm answers nothing -- CL-D1(b) with no measurement required.

    Its ``k`` is ``0``.  It is the sparsest arm in the sweep and the only one
    that cannot answer the question, which is exactly why ``k`` is reported
    next to ``answered`` and never alone.
    """

    arm_id = "cache_parent"
    role = "PARENT"

    def _make_store(self, catalogue: CompetenceCatalogue) -> CompetenceStore:
        return populate_cache_store(catalogue)

    def _install(self, ledger: TouchLedger) -> None:
        self._by_position: dict[tuple[str, int], str] = {}
        self._maintenance = 0
        for spec in self.catalogue.families:
            for block in spec.evidence_blocks:
                for position, _ in block:
                    self._by_position[(spec.family_id, position)] = (
                        f"C:{spec.family_id}:{position}"
                    )
                    self._maintenance += 1
        ledger.index_maintenance_work += self._maintenance

    @property
    def index_bytes(self) -> int:
        return len(self._by_position) * INDEX_ENTRY_BYTES

    @property
    def lifetime_index_maintenance_work(self) -> int:
        return self._maintenance

    def _answer(self, position: int, ledger: TouchLedger) -> tuple[str, bool | None]:
        family_id = self.catalogue.probe_family_id
        ledger.probe_index()
        object_id = self._by_position.get((family_id, position))
        if object_id is None or self.store.is_revoked(object_id):
            return "NO_CACHED_POSITION", None
        entry = self.store.read(object_id, ledger)
        return "ANSWERED", bool(entry.payload["is_p"])


# --------------------------------------------------------------------------
# hostiles
# --------------------------------------------------------------------------


class RebuildIndexHostile(ScalingArm):
    """Sparse-looking ``k`` bought with a global scan, on every query.

    The rebuild runs on a *separate* build ledger, so its ``N`` touches never
    appear in the query record and ``k`` comes out identical to the OCM arm's.
    That is precisely the deception a sparse claim is exposed to in real
    systems, and it is why ``k`` alone is not admissible evidence.

    What catches it is the accounting: ``index_build_work`` is charged to the
    query that triggered it, so every query carries ``N`` units of build work
    and ``sparse_verdict`` returns ``SPARSE_ONLY_AFTER_GLOBAL_BUILD_SCAN``.
    Over the five frozen probes its lifetime build work is five times an honest
    index's, and its total work is worse than the un-indexed ablation's -- which
    is what a crossover query count is for.  The discarded build touches remain
    in ``last_build_record``: they are hidden from ``k``, not from the receipt.
    """

    arm_id = "rebuild_index_hostile"
    role = "HOSTILE"

    def _install(self, ledger: TouchLedger) -> None:
        self.index: FamilyIndex | None = None
        self._lifetime_build = 0

    @property
    def index_bytes(self) -> int:
        return 0 if self.index is None else self.index.bytes

    @property
    def lifetime_index_build_work(self) -> int:
        return self._lifetime_build

    def _answer(self, position: int, ledger: TouchLedger) -> tuple[str, bool | None]:
        build_ledger = TouchLedger()
        self.index = FamilyIndex(self.store, track_dependencies=False, ledger=build_ledger)
        self._lifetime_build += self.index.build_work
        ledger.index_build_work += self.index.build_work
        self.last_build_record = self._record(
            build_ledger,
            operation="INDEX_BUILD",
            thermal_state="COLD",
            outcome="GLOBAL_SCAN_REBUILD",
            verdict_correct=None,
        )
        method_id = self.index.probe(self.catalogue.probe_family_id, ledger)
        if method_id is None:
            return "NO_METHOD_FOR_FAMILY", None
        method = self.store.read(method_id, ledger)
        if self.store.is_revoked(method_id):
            return "METHOD_REVOKED", None
        ledger.predicate_evaluations += 1
        return "ANSWERED", _rule_of(method).is_p_position(position)


class UnauditedScanHostile(ScalingArm):
    """An arm whose retrieval path is not instrumented.  Reports CANNOT_CHECK.

    Nothing about its behaviour is unusual: it finds the right method and
    answers correctly, and a naive harness would record ``k = 1``.  The store's
    uninstrumented accessor poisons the ledger, ``record_from_ledger`` will not
    emit a ``k`` from a poisoned ledger, and ``fit_loglog`` propagates the
    ``CANNOT_CHECK`` rather than fitting a slope through a guess.
    """

    arm_id = "unaudited_scan_hostile"
    role = "HOSTILE"

    def _install(self, ledger: TouchLedger) -> None:
        return None

    def _answer(self, position: int, ledger: TouchLedger) -> tuple[str, bool | None]:
        method = self.store.unaudited_scan_for_family(
            self.catalogue.probe_family_id, ledger
        )
        if method is None:
            return "NO_METHOD_FOR_FAMILY", None
        ledger.predicate_evaluations += 1
        return "ANSWERED", _rule_of(method).is_p_position(position)

    def _invalidate(self, support_id: str, ledger: TouchLedger) -> list[str]:
        observed = [support_id]
        for obj in self.store.unaudited_all_objects(ledger):
            if obj.object_class == "method" and support_id in obj.supports:
                self.store.revoke_method(obj.object_id)
                observed.append(obj.object_id)
        return observed


# --------------------------------------------------------------------------
# the registered arm set
# --------------------------------------------------------------------------


def ocm_arm(catalogue: CompetenceCatalogue) -> OcmArm:
    return OcmArm(catalogue)


def global_scan_ablation(catalogue: CompetenceCatalogue) -> GlobalScanAblation:
    return GlobalScanAblation(catalogue)


def index_parent(catalogue: CompetenceCatalogue) -> IndexParent:
    return IndexParent(catalogue)


def cache_parent(catalogue: CompetenceCatalogue) -> CacheParent:
    return CacheParent(catalogue)


def rebuild_index_hostile(catalogue: CompetenceCatalogue) -> RebuildIndexHostile:
    return RebuildIndexHostile(catalogue)


def unaudited_scan_hostile(catalogue: CompetenceCatalogue) -> UnauditedScanHostile:
    return UnauditedScanHostile(catalogue)


ARMS: dict[str, Callable[[CompetenceCatalogue], ScalingArm]] = {
    "ocm_arm": ocm_arm,
    "global_scan_ablation": global_scan_ablation,
    "index_parent": index_parent,
    "cache_parent": cache_parent,
    "rebuild_index_hostile": rebuild_index_hostile,
    "unaudited_scan_hostile": unaudited_scan_hostile,
}

#: Declared before the run.  ``OCM`` is the arm under test, ``PARENT`` gets
#: first right of refusal, ``ABLATION`` removes one mechanism from the OCM arm,
#: and ``HOSTILE`` exists to fail the audit rather than to compete.
ARM_ROLES: dict[str, str] = {
    "ocm_arm": OcmArm.role,
    "global_scan_ablation": GlobalScanAblation.role,
    "index_parent": IndexParent.role,
    "cache_parent": CacheParent.role,
    "rebuild_index_hostile": RebuildIndexHostile.role,
    "unaudited_scan_hostile": UnauditedScanHostile.role,
}


# --------------------------------------------------------------------------
# one cell of the sweep
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ArmResult:
    """Everything one arm did at one scale."""

    arm_id: str
    scale_id: str
    queries: tuple[ResourceRecord, ...]
    local_revision: RevisionRecord | None
    global_revision: RevisionRecord | None
    index_build_work: int
    index_bytes: int
    index_maintenance_work: int = 0
    install_record: ResourceRecord | None = None

    @property
    def n_objects(self) -> int:
        return self.queries[0].n_objects


def local_support_id(catalogue: CompetenceCatalogue) -> str:
    """The LOCAL support: evidence block 0 of the probe family's method."""
    return f"S:{catalogue.probe_family_id}:b0"


def _run_cell(
    factory: Callable[[CompetenceCatalogue], ScalingArm],
    catalogue: CompetenceCatalogue,
) -> ArmResult:
    """Queries at every frozen probe position, then both revocations.

    The revocations run after the queries on the same installed arm, so the
    query numbers are measured on an unrevoked store and both revocations are
    scored against the same ground-truth graph.  The globally shared cone is
    unaffected by the local revocation having happened first, because the
    reverse index still holds every method that declared the lemma.
    """
    arm = factory(catalogue)
    records = tuple(arm.query(p) for p in probe_positions())
    local = arm.revoke(local_support_id(catalogue), trigger_kind="LOCAL")
    shared = arm.revoke(SHARED_SUPPORT_ID, trigger_kind="GLOBALLY_SHARED")
    return ArmResult(
        arm_id=arm.arm_id,
        scale_id=catalogue.scale_id,
        queries=records,
        local_revision=local,
        global_revision=shared,
        index_build_work=arm.lifetime_index_build_work,
        index_bytes=arm.index_bytes,
        index_maintenance_work=arm.lifetime_index_maintenance_work,
        install_record=arm.install_record,
    )


def run_arm(arm_id: str, multiplier: int) -> ArmResult:
    return _run_cell(ARMS[arm_id], build_catalogue(multiplier))


def sweep(arm_ids: Sequence[str] | None = None) -> dict[str, list[ArmResult]]:
    """Every registered arm at every frozen scale, as raw ``ArmResult``s."""
    chosen = list(ARMS) if arm_ids is None else list(arm_ids)
    return {
        arm_id: [
            _run_cell(ARMS[arm_id], build_catalogue(m))
            for m in SCALING_PLAN["multipliers"]
        ]
        for arm_id in chosen
    }


# --------------------------------------------------------------------------
# the flat table and the fits
# --------------------------------------------------------------------------


def _exact(rev: RevisionRecord | None) -> bool | None:
    return None if rev is None else rev.observed_changed_ids == rev.expected_changed_ids


def _cone(rev: RevisionRecord | None) -> int | None:
    return None if rev is None else rev.cone_size


def _true_cone(rev: RevisionRecord | None) -> int | None:
    return None if rev is None else rev.expected_cone_size


def _work(rev: RevisionRecord | None) -> int | None:
    return None if rev is None else rev.revision_work


def _stale(rev: RevisionRecord | None) -> int | None:
    return None if rev is None else len(rev.stale_survivor_ids)


def sweep_table(results: Mapping[str, Sequence[ArmResult]]) -> list[dict]:
    """One flat row per (arm, scale), for the receipt.

    ``k`` and ``query_work`` are means over the frozen probe positions.  ``k``
    is ``None`` whenever any probe was served through an uninstrumented path:
    an unmeasurable coordinate is not averaged away against measurable ones.
    Cone sizes are reported next to the true cone, so an arm that invalidated
    nothing cannot be mistaken for one whose cone happened to be small.
    """
    rows: list[dict] = []
    for arm_id, per_scale in results.items():
        for result in per_scale:
            queries = result.queries
            ks = [q.k for q in queries]
            unmeasured = any(k is None for k in ks)
            n = result.n_objects
            mean_k = None if unmeasured else sum(ks) / len(ks)  # type: ignore[arg-type]
            rows.append(
                {
                    "arm": arm_id,
                    "role": ARM_ROLES.get(arm_id, "ARM"),
                    "scale": result.scale_id,
                    "N": n,
                    "k": mean_k,
                    "k_over_N": None if mean_k is None else mean_k / n,
                    "k_status": "CANNOT_CHECK" if unmeasured else "MEASURED",
                    "query_work": sum(q.query_work for q in queries) / len(queries),
                    "index_build_work": result.index_build_work,
                    "index_maintenance_work": result.index_maintenance_work,
                    "persistent_bytes": queries[0].persistent_bytes,
                    "store_bytes": queries[0].store_bytes,
                    "index_bytes": queries[0].index_bytes,
                    "total_work_including_build": result.index_build_work
                    + sum(q.query_work for q in queries),
                    "answered": sum(1 for q in queries if q.outcome == "ANSWERED"),
                    "correct": sum(1 for q in queries if q.verdict_correct),
                    "sparse_verdict": queries[0].sparse_verdict,
                    "local_cone_exact": _exact(result.local_revision),
                    "global_cone_exact": _exact(result.global_revision),
                    "local_cone_size": _cone(result.local_revision),
                    "global_cone_size": _cone(result.global_revision),
                    "local_true_cone_size": _true_cone(result.local_revision),
                    "global_true_cone_size": _true_cone(result.global_revision),
                    "local_revision_work": _work(result.local_revision),
                    "global_revision_work": _work(result.global_revision),
                    "local_stale_survivors": _stale(result.local_revision),
                    "global_stale_survivors": _stale(result.global_revision),
                }
            )
    return rows


#: Coordinates fitted against ``N`` for every arm.  ``k`` and query work are
#: the ``S1`` endpoint; the cone and revision coordinates are ``S3``.
FITTED_COORDINATES: tuple[tuple[str, str], ...] = (
    ("k(N)", "k"),
    ("query_work(N)", "query_work"),
    ("persistent_bytes(N)", "persistent_bytes"),
    ("total_work(N)", "total_work_including_build"),
    ("revision_work_local(N)", "local_revision_work"),
    ("revision_work_shared(N)", "global_revision_work"),
    ("cone_local(N)", "local_cone_size"),
    ("cone_shared(N)", "global_cone_size"),
)


def fits_for(rows: Sequence[Mapping]) -> dict:
    """Fit each registered relation against ``N``, per arm.

    ``fit_loglog`` refuses to report an exponent when a straight line does not
    describe the points, and refuses to report anything at all when a
    coordinate is ``CANNOT_CHECK`` or non-positive.  A relation that is not a
    power law therefore says so instead of quoting a slope.
    """
    out: dict[str, dict[str, dict]] = {}
    for arm_id in sorted({r["arm"] for r in rows}):
        mine = [r for r in rows if r["arm"] == arm_id]
        ns = [r["N"] for r in mine]
        out[arm_id] = {
            name: fit_loglog(ns, [r[key] for r in mine], label=f"{arm_id}:{name}").as_dict()
            for name, key in FITTED_COORDINATES
        }
    return out


# --------------------------------------------------------------------------
# the rich sweep object
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class SweepRow:
    """One (arm, scale) cell.

    Cold and warm queries are reported separately and never averaged, per
    protocol E3.  ``k`` is the worst case over the frozen probe positions, so
    an arm cannot pass by being sparse on average.
    """

    arm_id: str
    role: str
    scale_id: str
    multiplier: int
    n_objects: int
    k: int | None
    k_status: CheckStatus
    k_over_n: float | None
    query_work_cold: int
    query_work_warm_max: int
    index_build_work_cold: int
    index_build_work_warm_total: int
    lifetime_index_build_work: int
    lifetime_index_maintenance_work: int
    persistent_bytes: int
    store_bytes: int
    index_bytes: int
    active_bytes_cold: int
    search_expansions_cold: int
    checker_calls_total: int
    sparse_verdict: str
    outcome: str
    answered_queries: int
    correct_queries: int
    queries: int
    revision_work_local: int | None
    cone_local: int
    true_cone_local: int
    exact_local: bool
    stale_survivors_local: int
    revision_work_shared: int | None
    cone_shared: int
    true_cone_shared: int
    exact_shared: bool
    stale_survivors_shared: int

    def as_dict(self) -> dict:
        return {
            "arm_id": self.arm_id,
            "role": self.role,
            "scale": self.scale_id,
            "N": self.n_objects,
            "k": self.k,
            "k_status": self.k_status.value,
            "k_over_N": None if self.k_over_n is None else round(self.k_over_n, 6),
            "query_work_cold": self.query_work_cold,
            "query_work_warm_max": self.query_work_warm_max,
            "index_build_work_cold": self.index_build_work_cold,
            "lifetime_index_build_work": self.lifetime_index_build_work,
            "lifetime_index_maintenance_work": self.lifetime_index_maintenance_work,
            "persistent_bytes": self.persistent_bytes,
            "store_bytes": self.store_bytes,
            "index_bytes": self.index_bytes,
            "sparse_verdict": self.sparse_verdict,
            "outcome": self.outcome,
            "answered": f"{self.answered_queries}/{self.queries}",
            "correct": f"{self.correct_queries}/{self.queries}",
            "revision_work_local": self.revision_work_local,
            "cone_local": self.cone_local,
            "true_cone_local": self.true_cone_local,
            "exact_local": self.exact_local,
            "stale_survivors_local": self.stale_survivors_local,
            "revision_work_shared": self.revision_work_shared,
            "cone_shared": self.cone_shared,
            "true_cone_shared": self.true_cone_shared,
            "exact_shared": self.exact_shared,
            "stale_survivors_shared": self.stale_survivors_shared,
        }


@dataclass(frozen=True)
class ScaleSweep:
    """The whole frozen sweep, with slopes and their residuals."""

    commitment: str
    scales: tuple[str, ...]
    probe_family_id: str
    probe_positions: tuple[int, ...]
    rows: tuple[SweepRow, ...]
    fits: Mapping[str, Mapping[str, LogLogFit]]
    results: Mapping[str, tuple[ArmResult, ...]]
    notes: tuple[str, ...]

    def rows_for(self, arm_id: str) -> tuple[SweepRow, ...]:
        return tuple(r for r in self.rows if r.arm_id == arm_id)

    def as_dict(self) -> dict:
        return {
            "commitment_sha256": self.commitment,
            "probe_family": self.probe_family_id,
            "probe_positions": list(self.probe_positions),
            "scales": list(self.scales),
            "rows": [r.as_dict() for r in self.rows],
            "fits": {
                arm: {coord: fit.as_dict() for coord, fit in per_arm.items()}
                for arm, per_arm in self.fits.items()
            },
            "notes": list(self.notes),
        }


def _row_from(result: ArmResult, multiplier: int) -> SweepRow:
    queries = result.queries
    cold, warm = queries[0], queries[1:]
    ks = [q.k for q in queries]
    unmeasured = any(k is None for k in ks)
    k = None if unmeasured else max(ks)  # type: ignore[type-var]
    n = result.n_objects
    local, shared = result.local_revision, result.global_revision
    if local is None or shared is None:  # pragma: no cover -- _run_cell always sets both
        raise ValueError("a sweep row needs both revocations")
    return SweepRow(
        arm_id=result.arm_id,
        role=ARM_ROLES.get(result.arm_id, "ARM"),
        scale_id=result.scale_id,
        multiplier=multiplier,
        n_objects=n,
        k=k,
        k_status=cold.k_status,
        k_over_n=None if k is None or n == 0 else k / n,
        query_work_cold=cold.query_work,
        query_work_warm_max=max((q.query_work for q in warm), default=0),
        index_build_work_cold=cold.index_build_work,
        index_build_work_warm_total=sum(q.index_build_work for q in warm),
        lifetime_index_build_work=result.index_build_work,
        lifetime_index_maintenance_work=result.index_maintenance_work,
        persistent_bytes=cold.persistent_bytes,
        store_bytes=cold.store_bytes,
        index_bytes=cold.index_bytes,
        active_bytes_cold=cold.active_bytes,
        search_expansions_cold=cold.search_expansions,
        checker_calls_total=sum(q.checker_calls for q in queries),
        sparse_verdict=cold.sparse_verdict,
        outcome=cold.outcome,
        answered_queries=sum(1 for q in queries if q.outcome == "ANSWERED"),
        correct_queries=sum(1 for q in queries if q.verdict_correct),
        queries=len(queries),
        revision_work_local=local.revision_work,
        cone_local=local.cone_size,
        true_cone_local=local.expected_cone_size,
        exact_local=local.exact_revocation,
        stale_survivors_local=len(local.stale_survivor_ids),
        revision_work_shared=shared.revision_work,
        cone_shared=shared.cone_size,
        true_cone_shared=shared.expected_cone_size,
        exact_shared=shared.exact_revocation,
        stale_survivors_shared=len(shared.stale_survivor_ids),
    )


SWEEP_NOTES: tuple[str, ...] = (
    "k is the worst case over the frozen probe positions and is counted by "
    "instrumented touches only; it is never inferred from a returned result.",
    "the OCM arm and the plain index parent are identical on k, k/N and query work "
    "at every scale: PARENT_SUFFICIENT on the k(N) endpoint. Sparse lookup under a "
    "family key the catalogue supplies is a property of the key, not a finding "
    "about cognition.",
    "index build and maintenance work are charged separately from query work and "
    "reported in the same row; an arm whose k is small only because it scanned all "
    "N carries sparse_verdict=SPARSE_ONLY_AFTER_GLOBAL_BUILD_SCAN.",
    "an honest index still pays one global build scan; it is charged once at "
    "install and shown as lifetime_index_build_work, while the hostile pays it on "
    "every query. The distinction is amortisation, and the crossover query count "
    "is the number that decides it.",
    "the GLOBALLY_SHARED revocation is a hostile control: its cone SHOULD be large, "
    "and an arm reporting a small cone there is broken rather than local.",
    "every arm except the OCM arm observes the empty cone: without dependency edges "
    "an architecture does no revision work and instead leaves the entire true cone "
    "standing as stale survivors, counted exactly rather than described. A stronger "
    "parent variant could rediscover the cone by scanning every object's declared "
    "supports at O(N): the unaudited hostile does exactly that and gets both cones "
    "exactly right, but through an uninstrumented path, so its revision work is "
    "CANNOT_CHECK. An audited version of that parent is not run here, so the gap "
    "reported is about default behaviour, not about achievability.",
    "the OCM arm's reverse index was built from the same declarations that "
    "populated the store, so its revocation is exact by construction; these numbers "
    "measure the cost of exact revocation, not dependency discovery (protocol "
    "attack A9 is not answered here).",
    "cache_parent answers none of the probes: they lie above its cached magnitude. "
    "It is simultaneously the sparsest arm (k=0) and the only one that cannot "
    "answer, which is why k is never read without 'answered' beside it.",
    "four scales and two free parameters leave two degrees of freedom; a fitted "
    "slope describes these four points and is not an extrapolation licence.",
    "PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM remains the correct terminal for any field "
    "claim read out of an N of a few thousand.",
)


def run_sweep(multipliers: Sequence[int] | None = None) -> ScaleSweep:
    """Run every registered arm at every frozen scale and fit the slopes.

    ``multipliers`` exists so a test can run a cheap subset.  The confirmatory
    sweep is the one frozen in ``SCALING_PLAN``; anything else is a pilot in
    the sense of CL-T6 and must never be reported as confirmatory.
    """
    scales = tuple(multipliers if multipliers is not None else SCALING_PLAN["multipliers"])
    catalogues = [build_catalogue(m) for m in scales]
    results: dict[str, tuple[ArmResult, ...]] = {}
    rows: list[SweepRow] = []
    for arm_id, factory in ARMS.items():
        per_scale = []
        for catalogue in catalogues:
            result = _run_cell(factory, catalogue)
            per_scale.append(result)
            rows.append(_row_from(result, catalogue.multiplier))
        results[arm_id] = tuple(per_scale)

    fits: dict[str, dict[str, LogLogFit]] = {}
    for arm_id in ARMS:
        arm_rows = [r for r in rows if r.arm_id == arm_id]
        xs = [r.n_objects for r in arm_rows]
        fits[arm_id] = {
            "k": fit_loglog(xs, [r.k for r in arm_rows], label=f"{arm_id}:k(N)"),
            "query_work": fit_loglog(
                xs, [r.query_work_cold for r in arm_rows], label=f"{arm_id}:query_work(N)"
            ),
            "persistent_bytes": fit_loglog(
                xs,
                [r.persistent_bytes for r in arm_rows],
                label=f"{arm_id}:persistent_bytes(N)",
            ),
            "revision_work_local": fit_loglog(
                xs,
                [r.revision_work_local for r in arm_rows],
                label=f"{arm_id}:revision_work_local(N)",
            ),
            "revision_work_shared": fit_loglog(
                xs,
                [r.revision_work_shared for r in arm_rows],
                label=f"{arm_id}:revision_work_shared(N)",
            ),
            "cone_shared": fit_loglog(
                xs, [r.cone_shared for r in arm_rows], label=f"{arm_id}:cone_shared(N)"
            ),
        }

    return ScaleSweep(
        commitment=COMMITMENT.commitment,
        scales=tuple(f"{m}x" for m in scales),
        probe_family_id=catalogues[0].probe_family_id,
        probe_positions=tuple(probe_positions()),
        rows=tuple(rows),
        fits=fits,
        results=results,
        notes=SWEEP_NOTES,
    )


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------


def _num(value: int | None) -> str:
    """Render an unmeasurable coordinate as ``CANNOT``, never as a number."""
    return "CANNOT" if value is None else str(value)


_COLUMNS: tuple[tuple[str, int, Callable[[SweepRow], Any]], ...] = (
    ("arm", 24, lambda r: r.arm_id),
    ("scale", 6, lambda r: r.scale_id),
    ("N", 7, lambda r: r.n_objects),
    ("k", 8, lambda r: _num(r.k)),
    ("k/N", 10, lambda r: "n/a" if r.k_over_n is None else f"{r.k_over_n:.6f}"),
    ("qwork", 7, lambda r: r.query_work_cold),
    ("bld/q", 7, lambda r: r.index_build_work_cold),
    ("lifebld", 9, lambda r: r.lifetime_index_build_work),
    ("lifemnt", 9, lambda r: r.lifetime_index_maintenance_work),
    ("bytes", 9, lambda r: r.persistent_bytes),
    ("revLOC", 8, lambda r: _num(r.revision_work_local)),
    ("coneLOC", 9, lambda r: f"{r.cone_local}/{r.true_cone_local}"),
    ("revSHR", 8, lambda r: _num(r.revision_work_shared)),
    ("coneSHR", 10, lambda r: f"{r.cone_shared}/{r.true_cone_shared}"),
    ("ans", 5, lambda r: f"{r.answered_queries}/{r.queries}"),
    ("ok", 5, lambda r: f"{r.correct_queries}/{r.queries}"),
    ("sparse", 38, lambda r: r.sparse_verdict),
)


def format_sweep_table(sweep_result: ScaleSweep) -> str:
    """The scale-sweep table, one row per (arm, scale).

    ``coneLOC`` and ``coneSHR`` print ``observed/true`` so that an arm which
    invalidated nothing is never mistaken for one whose cone was small.
    """
    head = "".join(name.rjust(width) for name, width, _ in _COLUMNS)
    lines = [head, "-" * len(head)]
    for arm_id in ARMS:
        for row in sweep_result.rows_for(arm_id):
            lines.append("".join(str(fn(row)).rjust(w) for _, w, fn in _COLUMNS))
        lines.append("")
    return "\n".join(lines).rstrip()


def format_fit_table(sweep_result: ScaleSweep) -> str:
    """Fitted log-log slopes with residuals and the model's verdict."""
    header = (
        f"{'arm':<24}{'coordinate':<22}{'slope':>9}{'rms resid':>11}"
        f"{'max resid':>11}{'r^2':>9}  verdict"
    )
    lines = [header, "-" * (len(header) + 10)]
    for arm_id, per_arm in sweep_result.fits.items():
        for coord, fit in per_arm.items():
            slope = "     n/a" if fit.slope is None else f"{fit.slope:8.4f}"
            rms = (
                "        n/a"
                if fit.rms_log_residual is None
                else f"{fit.rms_log_residual:11.5f}"
            )
            worst = (
                "        n/a"
                if fit.max_log_residual is None
                else f"{fit.max_log_residual:11.5f}"
            )
            r2 = "      n/a" if fit.r_squared is None else f"{fit.r_squared:9.5f}"
            lines.append(f"{arm_id:<24}{coord:<22}{slope:>9}{rms}{worst}{r2}  {fit.verdict}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main() -> None:  # pragma: no cover -- reporting entry point
    result = run_sweep()
    print(f"commitment  {result.commitment}")
    print(f"probe       {result.probe_family_id} at positions {list(result.probe_positions)}")
    print()
    print(format_sweep_table(result))
    print()
    print(format_fit_table(result))
    print()
    for note in result.notes:
        print(f"* {note}")


if __name__ == "__main__":  # pragma: no cover
    main()
