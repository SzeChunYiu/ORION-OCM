"""Six ways to answer "what rests on this evidence?", and what each one costs.

``depend.py`` supplies the world: methods induced from evidence blocks, a
leave-one-out oracle nobody may call, a joint-witness oracle that names the
oracle's own blind spot, and a registered five-step revocation schedule chosen
by rules frozen in the plan hash.  This module supplies the arms and the sweep.

Every arm is handed **identical information**: the same store, the same
evidence, the same public metadata, and the same revocation schedule.  They
differ only in what they discover, when they discover it, and what they keep.

The arms
--------

``learned_dependency_arm``
    Discovers dependencies by leave-one-out re-induction at ACQUISITION time,
    stores the learned graph, uses it at revocation.  Its discovery cost is
    charged in full: every re-induction is real work and appears in its build
    record before it has served a single revocation.  At revocation it is a
    single index probe.  It attains precision and recall of ``1.0`` against the
    oracle for the uninteresting reason that it runs the oracle's own
    procedure; the endpoint that matters for this arm is what its **cached**
    graph does when evidence is withdrawn in a pattern acquisition never saw.

``lazy_learner_arm``
    Discovers nothing up front.  On each revocation it scans, re-induces the
    methods whose evidence was touched, and compares against the rule it
    currently believes.  Cheap to build, expensive per revocation, and exactly
    correct at every step because it re-derives rather than remembers.  This is
    the arm that makes the crossover meaningful, and it is also the arm that
    shows "cheap to build" is a claim about an arm nobody ever asks for its
    graph: disclosing one costs it the whole discovery.

``full_recomputation_parent``
    On revocation, re-induces EVERY method from the live evidence.  Always
    exactly correct.  The correctness ceiling and the cost ceiling in the same
    row, which is what a ceiling should look like.

``declared_supports_parent``
    **The gifted ceiling, labelled as such.**  It is handed the declared
    ``supports`` of every method -- the same declarations that populated the
    store -- and treats them as the dependency set.  This is the arm from the
    prior scaling pilot and it is cheating relative to this experiment's
    question.  It is included because a ceiling you refuse to run is not a
    ceiling.  Note honestly: in this world a method's declared supports are
    exactly its family's blocks, so the gift buys no more than family-grouped
    closure would.  The gift is not a bigger candidate set, it is the licence
    to call the candidate set a dependency set.

``co_occurrence_parent``
    The strongest cheap heuristic: link a method to every evidence block that
    shares its family identity and mentions a position inside the method's own
    range, taken as the induced rule's table span ``preperiod + period``.  It
    reads family identity -- public store metadata, the key an ordinary
    database index already uses -- and never reads ``supports``.  It costs no
    inductions at all.  It has precision AND recall errors and both are
    measured: a block lying entirely above the table span is invisible to it,
    and a block below the span that the rule does not actually need is a false
    positive.

``all_evidence_parent``
    Assumes every method depends on every block.  Recall ``1.0`` by
    construction; it can never leave a stale survivor.  It invalidates the
    entire store on every revocation, so its collateral is the whole store
    minus the true cone.  The conservative baseline, and the reason stale
    survivors and collateral invalidations are never summed: an arm that is
    perfect on one and catastrophic on the other would score respectably on
    any total.

What separates them
-------------------

Not the graph score of the arm that computes the graph score's definition.
The separating coordinates are:

* **stale survivors**, the dangerous error -- a belief left standing on
  withdrawn support;
* **collateral invalidations**, the wasteful error -- a belief torn down that
  never needed the evidence;
* **work**, split into discovery/build and per-revocation, and the crossover
  revocation count where paying up front starts to pay off.

The result this module was built to expose
------------------------------------------

``learned_dependency_arm`` is exact against the oracle and still leaves a stale
survivor, on the registered ``REDUNDANT_SECOND`` step.  Two blocks each
sufficed on their own, so at acquisition time leave-one-out correctly found
neither individually necessary and stored no edge for either.  When both are
withdrawn in sequence the rule changes and the cached graph says nothing
should.  ``co_occurrence_parent`` -- a cruder method with no notion of
dependency at all -- happens to catch it, because over-linking is safe in the
direction that matters.  That is not a point in the heuristic's favour so much
as a demonstration that a *sound* discovery procedure and a *cheap* one fail in
opposite directions, and that only the direction of failure is worth arguing
about.

Parents: truth maintenance systems and justification networks; dynamic
dependence graphs and program slicing; delta debugging; database view
maintenance and incremental recomputation.  No novelty is claimed for any of
them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

from games import Work
from methods import GrundyRule
from depend import (
    DEPEND_PLAN,
    INDEX_ENTRY_BYTES,
    LANGUAGE,
    CheckStatus,
    CompetenceObject,
    DependCatalogue,
    DependencyGraphRecord,
    ResourceRecord,
    RevisionRecord,
    RevocationStep,
    TouchLedger,
    block_observations,
    block_positions,
    build_catalogue,
    fit_loglog,
    oracle_changed_methods,
    populate_store,
    record_from_ledger,
    revocation_schedule,
    rule_of_payload,
    score_graph,
)

__all__ = [
    "ARMS",
    "ARM_ROLES",
    "SWEEP_NOTES",
    "DependencyArm",
    "LearnedDependencyArm",
    "LazyLearnerArm",
    "FullRecomputationParent",
    "DeclaredSupportsParent",
    "CoOccurrenceParent",
    "AllEvidenceParent",
    "ArmResult",
    "charged_work",
    "run_arm",
    "sweep",
    "sweep_table",
    "step_table",
    "fits_for",
    "crossover_revocations",
    "crossovers_for",
    "summarise",
    "format_summary",
]

#: Sentinel for "this arm has not formed a belief about this method yet".
#: ``None`` cannot be used: ``None`` is a legitimate induction result meaning
#: "no rule in the language fits the surviving evidence", and conflating the
#: two would let an arm score a change it never detected.
_UNSET = object()


def charged_work(ledger: TouchLedger) -> int:
    """Every unit of work an operation actually spent.

    Unlike ``TouchLedger.query_work`` this deliberately **includes** index
    build and maintenance.  The whole question here is whether paying to
    discover dependencies up front is worth it, and an accounting that left the
    build out of the total would answer that question by omission.
    """
    return (
        ledger.index_probes
        + ledger.object_reads
        + ledger.enumerated_items
        + ledger.predicate_evaluations
        + ledger.search_expansions
        + ledger.index_build_work
        + ledger.index_maintenance_work
    )


def _induce(groups: Iterable[Sequence[tuple[int, int]]], ledger: TouchLedger):
    """Induce from observation groups and charge the search to ``ledger``.

    This is the arms' own induction path.  It is not the oracle: it is the same
    public :meth:`GrundyRuleLanguage.induce` the catalogue used, and every
    expansion it costs is charged to the caller.  An arm that wants to know
    whether a rule changed has to pay for finding out.
    """
    evidence = tuple(sorted({obs for g in groups for obs in g}))
    work = Work()
    rule = LANGUAGE.induce(evidence, work=work)
    ledger.search_expansions += work.expansions
    return rule


# --------------------------------------------------------------------------
# base
# --------------------------------------------------------------------------


class DependencyArm:
    """One dependency-discovery architecture, installed over one catalogue.

    Subclasses implement ``_build``, ``_invalidate`` and ``_disclose``.
    Everything else -- the ledgers, the record construction, the comparison
    against the oracle -- is shared, so no arm can differ from another in the
    bookkeeping rather than in the architecture.
    """

    arm_id = "abstract"
    role = "ARM"
    discovery = "unspecified"

    def __init__(self, catalogue: DependCatalogue) -> None:
        self.catalogue = catalogue
        self.scale_id = catalogue.scale_id
        self.store = populate_store(catalogue)
        self.index_entries = 0
        self._belief: dict[str, object] = {}
        ledger = TouchLedger()
        self._build(ledger)
        self.build_ledger = ledger
        self.build_work = charged_work(ledger)
        self.build_record = self._record(ledger, operation="DISCOVERY_BUILD")

    # ---- construction ---------------------------------------------------

    def _build(self, ledger: TouchLedger) -> None:
        raise NotImplementedError

    # ---- reporting surface ----------------------------------------------

    @property
    def n_objects(self) -> int:
        return self.store.n_objects

    @property
    def index_bytes(self) -> int:
        return self.index_entries * INDEX_ENTRY_BYTES

    def _record(self, ledger: TouchLedger, *, operation: str) -> ResourceRecord:
        return record_from_ledger(
            ledger,
            arm_id=self.arm_id,
            scale_id=self.scale_id,
            operation=operation,
            thermal_state="COLD",
            n_objects=self.n_objects,
            store_bytes=self.store.store_bytes,
            index_bytes=self.index_bytes,
            lifetime_index_build_work=ledger.index_build_work,
            lifetime_index_maintenance_work=ledger.index_maintenance_work,
            outcome=operation,
            verdict_correct=None,
        )

    # ---- shared re-induction helpers ------------------------------------
    #
    # These read a method's candidate evidence through the *family identity*
    # carried on every stored object.  Family identity is public metadata --
    # the key an ordinary database index already uses -- and is not the
    # dependency declaration.  Exactly one arm reads ``supports``, and it is
    # labelled the gifted ceiling.

    def _family_blocks(self, family_id: str, ledger: TouchLedger) -> list[str]:
        return [b.block_id for b in self.catalogue.family_of_method(f"M:{family_id}").blocks]

    def _live_observations(
        self, block_ids: Sequence[str], ledger: TouchLedger
    ) -> list[tuple[tuple[int, int], ...]]:
        out = []
        for block_id in block_ids:
            if self.store.is_revoked(block_id):
                continue
            out.append(block_observations(self.store.read(block_id, ledger)))
        return out

    def _believed_rule(self, obj: CompetenceObject) -> GrundyRule | None:
        """The rule this arm currently thinks the method carries.

        Seeded from the stored payload, which is what actually crossed the
        persistence boundary, and updated whenever the arm detects a change.
        Seeding costs no induction: the store persisted the rule as data.
        """
        held = self._belief.get(obj.object_id, _UNSET)
        if held is _UNSET:
            held = rule_of_payload(obj)
            self._belief[obj.object_id] = held
        return held  # type: ignore[return-value]

    # ---- revocation -----------------------------------------------------

    def _invalidate(self, block_ids: Sequence[str], ledger: TouchLedger) -> list[str]:
        """Return the method ids this arm actually invalidated."""
        raise NotImplementedError

    def _live_block_ids(self) -> frozenset[str]:
        """Scaffolding bookkeeping, not an arm access path.

        Returns identities only, never a payload, and is charged to nobody
        because it is the scorer establishing what the world looks like before
        and after the step.  An arm that used this would still have to
        ``read`` every block to learn anything from it.
        """
        return frozenset(
            b.block_id
            for f in self.catalogue.families
            for b in f.blocks
            if not self.store.is_revoked(b.block_id)
        )

    def revoke(self, step: RevocationStep) -> RevisionRecord:
        """Apply one registered revocation and score the arm's response.

        ``expected_changed_ids`` comes from :func:`oracle_changed_methods`,
        which ``_invalidate`` never consults -- the same separation
        ``scaling_arms.ScalingArm.revoke`` keeps around ``true_cone``.  The
        expectation includes the withdrawn blocks themselves, so an arm is
        credited with knowing that the evidence it just revoked is affected and
        precision does not degenerate on the no-op steps.
        """
        live_before = self._live_block_ids()
        live_after = live_before - set(step.block_ids)
        expected = frozenset(step.block_ids) | oracle_changed_methods(
            self.catalogue, live_before, live_after
        )
        ledger = TouchLedger()
        for block_id in step.block_ids:
            self.store.revoke_support(block_id)
        observed = set(step.block_ids) | set(self._invalidate(step.block_ids, ledger))
        poisoned = ledger.status is CheckStatus.CANNOT_CHECK
        return RevisionRecord(
            arm_id=self.arm_id,
            scale_id=self.scale_id,
            trigger_support_id=step.block_ids[0],
            trigger_kind=step.step_id,
            n_objects=self.n_objects,
            expected_changed_ids=tuple(sorted(expected)),
            observed_changed_ids=tuple(sorted(observed)),
            touched_ids=() if poisoned else tuple(ledger.touched_ids),
            k=None if poisoned else len(ledger.touched_ids),
            k_status=CheckStatus.CANNOT_CHECK if poisoned else CheckStatus.MEASURED,
            revision_work=None if poisoned else charged_work(ledger),
            index_probes=ledger.index_probes,
            index_maintenance_work=ledger.index_maintenance_work,
            object_reads=ledger.object_reads,
            enumerated_items=ledger.enumerated_items,
            cannot_check_reason=ledger.cannot_check_reason,
        )

    # ---- graph disclosure -----------------------------------------------

    def _disclose(self, ledger: TouchLedger) -> set[tuple[str, str]]:
        raise NotImplementedError

    def disclose_graph(self) -> DependencyGraphRecord:
        """Ask the arm what it believes depends on what, and charge it.

        An arm that stores a graph answers with index probes.  An arm that
        stores none has to derive one, and the derivation is charged here in
        full.  Nothing is free because nobody happened to ask earlier.
        """
        ledger = TouchLedger()
        edges = self._disclose(ledger)
        return score_graph(self.arm_id, self.catalogue, edges, charged_work(ledger))


class _ReverseIndexArm(DependencyArm):
    """Shared body of the three arms that keep a support-to-method index.

    They are one class with three ``_build`` methods on purpose.  The claim
    under test is that *discovering* a dependency graph differs from *being
    handed* one, and the cheapest way to manufacture a difference is to write
    three implementations and let an incidental asymmetry creep into the
    revocation path.  Here the revocation path and the disclosure path are
    literally the same code, so any difference in the reported numbers has to
    come from what ``_build`` put in the index.
    """

    def _file(self, block_id: str, method_id: str) -> None:
        self._dependents.setdefault(block_id, []).append(method_id)
        self.index_entries += 1

    def _build(self, ledger: TouchLedger) -> None:
        self._dependents: dict[str, list[str]] = {}
        self._discover(ledger)

    def _discover(self, ledger: TouchLedger) -> None:
        raise NotImplementedError

    def _invalidate(self, block_ids: Sequence[str], ledger: TouchLedger) -> list[str]:
        observed: list[str] = []
        for block_id in block_ids:
            ledger.probe_index()
            for method_id in sorted(self._dependents.get(block_id, ())):
                self.store.read(method_id, ledger)
                self.store.revoke_method(method_id)
                ledger.index_maintenance_work += 1
                observed.append(method_id)
        return observed

    def _disclose(self, ledger: TouchLedger) -> set[tuple[str, str]]:
        edges = set()
        for family in self.catalogue.families:
            for block in family.blocks:
                ledger.probe_index()
                for method_id in self._dependents.get(block.block_id, ()):
                    edges.add((block.block_id, method_id))
        return edges


# --------------------------------------------------------------------------
# the arm under test
# --------------------------------------------------------------------------


class LearnedDependencyArm(_ReverseIndexArm):
    """Discovers the graph by leave-one-out re-induction, then caches it.

    Discovery is ``B + 1`` inductions per method: one for the rule as
    acquired, and one per candidate block with that block withheld.  Every one
    of them is charged to the build ledger.  Nothing about this is free and
    nothing about it is declared.

    The cached graph is exact against the oracle **at acquisition time**.  What
    it cannot represent is support that was redundant when it was learned: two
    blocks that each sufficed alone produce no edge for either, because at that
    moment neither was individually necessary.  Withdraw both and the belief
    falls over while the graph still says nothing depends on them.  That is not
    a bug in this implementation; it is what leave-one-out means, and the
    registered ``REDUNDANT_SECOND`` step exists to make it a number.
    """

    arm_id = "learned_dependency_arm"
    role = "ARM"
    discovery = "leave-one-out re-induction at acquisition time, cached"

    def _discover(self, ledger: TouchLedger) -> None:
        for obj in self.store.scan(ledger):
            ledger.index_build_work += 1
            if obj.object_class != "method":
                continue
            candidates = self._family_blocks(obj.family_id, ledger)
            observations = {
                block_id: block_observations(self.store.read(block_id, ledger))
                for block_id in candidates
            }
            base = _induce(observations.values(), ledger)
            for block_id in candidates:
                without = [v for k, v in observations.items() if k != block_id]
                if _induce(without, ledger) != base:
                    self._file(block_id, obj.object_id)
            self.index_entries += 1


# --------------------------------------------------------------------------
# the arm that discovers nothing until it has to
# --------------------------------------------------------------------------


class LazyLearnerArm(DependencyArm):
    """Keeps no graph.  Re-induces on revocation to find what changed.

    Build cost is zero: it does not even scan.  On each revocation it walks the
    store, finds the methods whose family owns a withdrawn block, re-induces
    each from the surviving evidence, and compares against the rule it
    currently believes -- updating that belief when it changes, so a sequence
    of revocations is scored against what the arm actually holds rather than
    against the original acquisition.

    Exactly correct at every step, including the redundant-pair step, because
    it never relies on a snapshot of which evidence mattered.  Correctness by
    re-derivation is the oldest trick in the book and it is not a finding; the
    finding, if there is one, is what it costs.
    """

    arm_id = "lazy_learner_arm"
    role = "ARM"
    discovery = "none at acquisition; re-induction on every revocation"

    def _build(self, ledger: TouchLedger) -> None:
        return None

    def _reinduce(self, obj: CompetenceObject, ledger: TouchLedger):
        blocks = self._family_blocks(obj.family_id, ledger)
        return _induce(self._live_observations(blocks, ledger), ledger)

    def _affected(self, block_ids: Sequence[str], obj: CompetenceObject) -> bool:
        """Whether this method's own family lost a block in this revocation."""
        return any(
            self.catalogue.family_of_block(b).method_id == obj.object_id
            for b in block_ids
        )

    def _invalidate(self, block_ids: Sequence[str], ledger: TouchLedger) -> list[str]:
        observed: list[str] = []
        for obj in self.store.scan(ledger):
            if obj.object_class != "method":
                continue
            ledger.predicate_evaluations += 1
            if not self._affected(block_ids, obj):
                continue
            before = self._believed_rule(obj)
            after = self._reinduce(obj, ledger)
            if after != before:
                self._belief[obj.object_id] = after
                self.store.revoke_method(obj.object_id)
                ledger.index_maintenance_work += 1
                observed.append(obj.object_id)
        return observed

    def _disclose(self, ledger: TouchLedger) -> set[tuple[str, str]]:
        """Deriving the graph costs this arm the whole discovery it skipped.

        Charged here in full.  "Cheap to build" is a true statement about an
        arm nobody asks, and this method is the receipt for that qualifier.
        """
        return _rederive_edges(self, ledger)


class FullRecomputationParent(DependencyArm):
    """Re-induces EVERY method on every revocation.  The correctness ceiling.

    It does not ask which methods could possibly be affected, because asking
    that question is already a dependency assumption.  It pays ``F``
    inductions per revocation and is never wrong.  Both facts belong in the
    same row: this arm is what correctness costs when nothing is remembered
    and nothing is scoped.
    """

    arm_id = "full_recomputation_parent"
    role = "PARENT"
    discovery = "none; full re-induction of every method on every revocation"

    def _build(self, ledger: TouchLedger) -> None:
        return None

    def _reinduce(self, obj: CompetenceObject, ledger: TouchLedger):
        blocks = self._family_blocks(obj.family_id, ledger)
        return _induce(self._live_observations(blocks, ledger), ledger)

    def _invalidate(self, block_ids: Sequence[str], ledger: TouchLedger) -> list[str]:
        observed: list[str] = []
        for obj in self.store.scan(ledger):
            if obj.object_class != "method":
                continue
            before = self._believed_rule(obj)
            after = self._reinduce(obj, ledger)
            if after != before:
                self._belief[obj.object_id] = after
                self.store.revoke_method(obj.object_id)
                ledger.index_maintenance_work += 1
                observed.append(obj.object_id)
        return observed

    def _disclose(self, ledger: TouchLedger) -> set[tuple[str, str]]:
        return _rederive_edges(self, ledger)


def _rederive_edges(arm: DependencyArm, ledger: TouchLedger) -> set[tuple[str, str]]:
    """Leave-one-out discovery run on demand, charged to the caller.

    Shared by the two arms that hold no graph.  It is the same procedure
    ``LearnedDependencyArm`` runs at acquisition; running it here rather than
    at build time is the entire difference between those arms, and putting it
    in one function keeps that difference from being an implementation
    accident.
    """
    edges: set[tuple[str, str]] = set()
    for obj in arm.store.scan(ledger):
        ledger.index_build_work += 1
        if obj.object_class != "method":
            continue
        candidates = arm._family_blocks(obj.family_id, ledger)
        observations = {
            block_id: block_observations(arm.store.read(block_id, ledger))
            for block_id in candidates
        }
        base = _induce(observations.values(), ledger)
        for block_id in candidates:
            without = [v for k, v in observations.items() if k != block_id]
            if _induce(without, ledger) != base:
                edges.add((block_id, obj.object_id))
    return edges


# --------------------------------------------------------------------------
# the parents
# --------------------------------------------------------------------------


class DeclaredSupportsParent(_ReverseIndexArm):
    """THE GIFTED CEILING.  Handed the declarations and told they are the truth.

    This is the arm from the prior scaling pilot.  It reads ``supports`` --
    the very declarations that populated the store -- and files each one as a
    dependency edge.  It pays no inductions, so its build is the cheapest of
    any arm that holds a graph, and its revocation is a single index probe.

    It is cheating relative to this experiment's question and is included with
    that label attached.  Its recall is ``1.0`` for free: a rule cannot depend
    on evidence it was never shown, so the declared set contains every true
    dependency.  Its precision is the interesting number, and the gap between
    ``1.0`` and that number is exactly the fiction the prior pilot's exactness
    was built on.
    """

    arm_id = "declared_supports_parent"
    role = "PARENT_GIFTED_CEILING"
    discovery = "none; the declared supports are taken to be the dependency set"

    def _discover(self, ledger: TouchLedger) -> None:
        for obj in self.store.scan(ledger):
            ledger.index_build_work += 1
            if obj.object_class != "method":
                continue
            for block_id in obj.supports:
                self._file(block_id, obj.object_id)
            self.index_entries += 1


class CoOccurrenceParent(_ReverseIndexArm):
    """A positional heuristic: same family, and mentions a position in range.

    "In range" means inside the induced rule's table span, ``preperiod +
    period`` -- the slots the rule actually has.  The heuristic is cheap
    (no inductions, one predicate per candidate pair), it is the strongest
    thing available without re-deriving anything, and it is wrong in both
    directions:

    * a block whose positions all lie **above** the span is unlinked even when
      the rule genuinely needs it, because the rule's table wraps and the
      block is the only witness to a slot -- a stale survivor;
    * a block below the span that the rule does not actually need is linked
      anyway -- a collateral invalidation.

    Both are measured.  Neither is hidden, and the arm is not tuned to make
    either go away, because a heuristic tuned against the oracle would be the
    oracle wearing a hat.
    """

    arm_id = "co_occurrence_parent"
    role = "PARENT"
    discovery = "positional co-occurrence within the induced rule's table span"

    def _discover(self, ledger: TouchLedger) -> None:
        blocks_by_family: dict[str, list[tuple[str, tuple[int, ...]]]] = {}
        methods: list[tuple[str, str, int]] = []
        for obj in self.store.scan(ledger):
            ledger.index_build_work += 1
            if obj.object_class == "support":
                blocks_by_family.setdefault(obj.family_id, []).append(
                    (obj.object_id, block_positions(obj))
                )
            elif obj.object_class == "method":
                rule = rule_of_payload(obj)
                methods.append(
                    (obj.object_id, obj.family_id, rule.preperiod + rule.period)
                )
        for method_id, family_id, span in methods:
            for block_id, positions in blocks_by_family.get(family_id, ()):
                ledger.predicate_evaluations += 1
                if any(position < span for position in positions):
                    self._file(block_id, method_id)
            self.index_entries += 1


class AllEvidenceParent(DependencyArm):
    """Every method depends on every block.  The conservative baseline.

    It can never leave a stale survivor: recall is ``1.0`` by construction and
    stays ``1.0`` under any revocation pattern, redundant support included.
    It pays for that by invalidating the whole store every time anything is
    withdrawn, which is a collateral invalidation count equal to the number of
    methods that did not change.

    This arm is the reason the two error kinds are reported separately and
    never summed.  On any total that added them it would look like a
    reasonable middle option, and it is not: it is the option that throws away
    all accumulated competence whenever one observation is retracted.
    """

    arm_id = "all_evidence_parent"
    role = "PARENT"
    discovery = "none; every method is assumed to depend on every block"

    def _build(self, ledger: TouchLedger) -> None:
        self._method_ids: list[str] = []
        self._block_ids: list[str] = []
        for obj in self.store.scan(ledger):
            ledger.index_build_work += 1
            if obj.object_class == "method":
                self._method_ids.append(obj.object_id)
                self.index_entries += 1
            else:
                self._block_ids.append(obj.object_id)

    def _invalidate(self, block_ids: Sequence[str], ledger: TouchLedger) -> list[str]:
        observed: list[str] = []
        for method_id in self._method_ids:
            self.store.read(method_id, ledger)
            self.store.revoke_method(method_id)
            ledger.index_maintenance_work += 1
            observed.append(method_id)
        return observed

    def _disclose(self, ledger: TouchLedger) -> set[tuple[str, str]]:
        for _ in self._block_ids:
            ledger.probe_index()
        return {(b, m) for b in self._block_ids for m in self._method_ids}


# --------------------------------------------------------------------------
# the registry
# --------------------------------------------------------------------------

ARMS: dict[str, Callable[[DependCatalogue], DependencyArm]] = {
    "learned_dependency_arm": LearnedDependencyArm,
    "lazy_learner_arm": LazyLearnerArm,
    "full_recomputation_parent": FullRecomputationParent,
    "declared_supports_parent": DeclaredSupportsParent,
    "co_occurrence_parent": CoOccurrenceParent,
    "all_evidence_parent": AllEvidenceParent,
}

#: Declared before the run.  ``ARM`` is under test, ``PARENT`` gets first right
#: of refusal, and ``PARENT_GIFTED_CEILING`` is a parent that is only allowed
#: to be a ceiling because it is given something this experiment exists to take
#: away.
ARM_ROLES: dict[str, str] = {name: cls.role for name, cls in ARMS.items()}


# --------------------------------------------------------------------------
# one cell of the sweep
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ArmResult:
    """Everything one arm did at one scale."""

    arm_id: str
    role: str
    scale_id: str
    multiplier: int
    n_objects: int
    n_methods: int
    n_blocks: int
    build_record: ResourceRecord
    build_work: int
    index_bytes: int
    revisions: tuple[RevisionRecord, ...]
    graph: DependencyGraphRecord

    @property
    def revocation_work(self) -> int:
        return sum(r.revision_work or 0 for r in self.revisions)

    @property
    def mean_revocation_work(self) -> float:
        return self.revocation_work / len(self.revisions)

    @property
    def stale_survivors(self) -> int:
        return sum(len(r.stale_survivor_ids) for r in self.revisions)

    @property
    def collateral_invalidations(self) -> int:
        return sum(len(r.collateral_invalidated_ids) for r in self.revisions)

    @property
    def total_work(self) -> int:
        return self.build_work + self.revocation_work


def _run_cell(factory, catalogue: DependCatalogue) -> ArmResult:
    """Install the arm, disclose its graph, then run the registered schedule.

    Disclosure happens **before** any revocation so the graph endpoint is about
    what the arm knew at acquisition, which is the coordinate the experiment is
    about.  Its cost is reported separately and is never folded into the
    crossover accounting, because an arm is not obliged to publish its graph in
    order to serve a revocation.
    """
    arm = factory(catalogue)
    graph = arm.disclose_graph()
    revisions = tuple(arm.revoke(step) for step in revocation_schedule(catalogue))
    return ArmResult(
        arm_id=arm.arm_id,
        role=arm.role,
        scale_id=catalogue.scale_id,
        multiplier=catalogue.multiplier,
        n_objects=arm.n_objects,
        n_methods=len(catalogue.families),
        n_blocks=catalogue.n_blocks,
        build_record=arm.build_record,
        build_work=arm.build_work,
        index_bytes=arm.index_bytes,
        revisions=revisions,
        graph=graph,
    )


def run_arm(arm_id: str, multiplier: int) -> ArmResult:
    return _run_cell(ARMS[arm_id], build_catalogue(multiplier))


def sweep(arm_ids: Sequence[str] | None = None) -> dict[str, list[ArmResult]]:
    """Every registered arm at every frozen scale."""
    chosen = list(ARMS) if arm_ids is None else list(arm_ids)
    return {
        arm_id: [
            _run_cell(ARMS[arm_id], build_catalogue(m))
            for m in DEPEND_PLAN["multipliers"]
        ]
        for arm_id in chosen
    }


# --------------------------------------------------------------------------
# tables
# --------------------------------------------------------------------------


def sweep_table(results: Mapping[str, Sequence[ArmResult]]) -> list[dict]:
    """One flat row per (arm, scale).

    Stale survivors and collateral invalidations appear as two columns and
    there is deliberately no column that adds them.  Anyone who wants a single
    number has to decide for themselves which error they are willing to buy
    with the other, and that decision does not belong in this table.
    """
    rows: list[dict] = []
    for arm_id, per_scale in results.items():
        for result in per_scale:
            rows.append(
                {
                    "arm": arm_id,
                    "role": result.role,
                    "discovery": ARMS[arm_id].discovery,
                    "scale": result.scale_id,
                    "N": result.n_objects,
                    "methods": result.n_methods,
                    "blocks": result.n_blocks,
                    "graph_precision": result.graph.precision,
                    "graph_recall": result.graph.recall,
                    "graph_exact": result.graph.exact,
                    "true_edges": result.graph.n_true_edges,
                    "believed_edges": result.graph.n_believed_edges,
                    "missed_edges": len(result.graph.missing_edges),
                    "spurious_edges": len(result.graph.extra_edges),
                    "graph_disclosure_work": result.graph.disclosure_work,
                    "build_work": result.build_work,
                    "revocation_work": result.revocation_work,
                    "mean_revocation_work": result.mean_revocation_work,
                    "total_work": result.total_work,
                    "index_bytes": result.index_bytes,
                    "persistent_bytes": result.build_record.persistent_bytes,
                    "stale_survivors": result.stale_survivors,
                    "collateral_invalidations": result.collateral_invalidations,
                    "exact_revocations": sum(
                        1 for r in result.revisions if r.exact_revocation
                    ),
                    "revocations": len(result.revisions),
                }
            )
    return rows


def step_table(results: Mapping[str, Sequence[ArmResult]]) -> list[dict]:
    """One row per (arm, scale, registered revocation step).

    The step-level view is where the hostiles are legible.  A summed row can
    hide a single stale survivor among four exact steps, and the single stale
    survivor is the finding.
    """
    rows: list[dict] = []
    for arm_id, per_scale in results.items():
        for result in per_scale:
            for record in result.revisions:
                rows.append(
                    {
                        "arm": arm_id,
                        "scale": result.scale_id,
                        "N": result.n_objects,
                        "step": record.trigger_kind,
                        "revoked": record.trigger_support_id,
                        "expected_cone": record.expected_cone_size,
                        "observed_cone": record.cone_size,
                        "precision": record.dependency_precision,
                        "recall": record.dependency_recall,
                        "stale_survivors": len(record.stale_survivor_ids),
                        "stale_survivor_ids": list(record.stale_survivor_ids),
                        "collateral_invalidations": len(record.collateral_invalidated_ids),
                        "exact": record.exact_revocation,
                        "revision_work": record.revision_work,
                        "k": record.k,
                    }
                )
    return rows


#: Coordinates fitted against ``N`` for every arm.
FITTED_COORDINATES: tuple[tuple[str, str], ...] = (
    ("build_work(N)", "build_work"),
    ("revocation_work(N)", "revocation_work"),
    ("total_work(N)", "total_work"),
    ("graph_disclosure_work(N)", "graph_disclosure_work"),
    ("believed_edges(N)", "believed_edges"),
    ("persistent_bytes(N)", "persistent_bytes"),
)


def fits_for(rows: Sequence[Mapping]) -> dict:
    """Fit each registered relation against ``N``, per arm.

    ``fit_loglog`` refuses an exponent when a straight line does not describe
    the points and refuses anything at all on a non-positive or unmeasurable
    coordinate.  An arm whose build work is zero at every scale therefore gets
    ``UNDEFINED_NONPOSITIVE_VALUES`` rather than a fabricated slope, which is
    the correct report for an arm that genuinely does nothing at build time.
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
# the crossover
# --------------------------------------------------------------------------

#: How far ahead the crossover search looks before giving up.  Declared rather
#: than open-ended: "never, within a hundred thousand revocations" is a
#: reportable answer and an unbounded search is not.
CROSSOVER_HORIZON = 100_000


def crossover_revocations(
    build_a: float,
    per_revocation_a: float,
    build_b: float,
    per_revocation_b: float,
    *,
    horizon: int = CROSSOVER_HORIZON,
) -> int | None:
    """Least ``R >= 1`` with ``build_a + R*rev_a < build_b + R*rev_b``.

    Linear extrapolation from the mean per-revocation work measured over the
    registered schedule.  That assumption is stated here rather than buried:
    the registered steps are not a random sample of revocations, so the
    crossover is "how many revocations *like these*", and a workload of only
    no-op revocations would move it.  ``None`` means the arm never catches up
    within the declared horizon, which is a result and not a missing value.
    """
    for r in range(1, horizon + 1):
        if build_a + r * per_revocation_a < build_b + r * per_revocation_b:
            return r
    return None


def crossovers_for(rows: Sequence[Mapping]) -> dict:
    """Crossovers for ``learned_dependency_arm`` against every other arm."""
    out: dict[str, dict[str, int | None]] = {}
    by_scale: dict[str, dict[str, Mapping]] = {}
    for row in rows:
        by_scale.setdefault(row["scale"], {})[row["arm"]] = row
    for scale, arms in by_scale.items():
        learned = arms["learned_dependency_arm"]
        out[scale] = {
            other: crossover_revocations(
                learned["build_work"],
                learned["mean_revocation_work"],
                arms[other]["build_work"],
                arms[other]["mean_revocation_work"],
            )
            for other in arms
            if other != "learned_dependency_arm"
        }
    return out


# --------------------------------------------------------------------------
# the summary the terminal rule reads
# --------------------------------------------------------------------------


def summarise(rows: Sequence[Mapping]) -> dict:
    """Per-arm coordinates aggregated over the frozen scales.

    Precision and recall are reported as the exact set of values seen across
    scales, not as a mean.  An arm whose recall is ``1.0`` at three scales and
    ``0.5`` at the fourth has a recall problem, and averaging it to ``0.875``
    would describe an arm that does not exist.
    """
    out: dict[str, dict] = {}
    for arm_id in sorted({r["arm"] for r in rows}):
        mine = [r for r in rows if r["arm"] == arm_id]
        out[arm_id] = {
            "role": mine[0]["role"],
            "discovery": mine[0]["discovery"],
            "precision_by_scale": [round(r["graph_precision"], 6) for r in mine],
            "recall_by_scale": [round(r["graph_recall"], 6) for r in mine],
            "stale_survivors_by_scale": [r["stale_survivors"] for r in mine],
            "collateral_by_scale": [r["collateral_invalidations"] for r in mine],
            "build_work_by_scale": [r["build_work"] for r in mine],
            "revocation_work_by_scale": [r["revocation_work"] for r in mine],
            "total_work_by_scale": [r["total_work"] for r in mine],
            "total_stale_survivors": sum(r["stale_survivors"] for r in mine),
            "total_collateral": sum(r["collateral_invalidations"] for r in mine),
            "total_work": sum(r["total_work"] for r in mine),
        }
    return out


SWEEP_NOTES: tuple[str, ...] = (
    "the leave-one-out oracle is computed by brute force in the scorer and is handed to "
    "no arm; a source-inspection test refuses any arm class that mentions it.",
    "learned_dependency_arm attains precision and recall 1.0 against the oracle for the "
    "uninteresting reason that it runs the oracle's own procedure. That is not evidence "
    "of anything and is not reported as a result.",
    "REDUNDANT SUPPORT IS INVISIBLE TO LEAVE-ONE-OUT. Where two blocks each suffice "
    "alone, the oracle finds neither individually necessary, so a graph learned at "
    "acquisition stores no edge for either. Withdrawing both leaves the belief standing. "
    "This is a limitation of the discovery method, it is counted at every scale as "
    "redundant_support_methods, and it is the reason the terminal is what it is.",
    "stale survivors and collateral invalidations are asymmetric and are never summed. "
    "all_evidence_parent has recall 1.0 and destroys the store on every revocation; a "
    "combined error count would rank it as moderate.",
    "declared_supports_parent is the GIFTED CEILING. It is handed the declarations that "
    "populated the store and calls them dependencies. Its recall is 1.0 for free and it "
    "is cheating relative to this experiment's question, which is why it is labelled "
    "rather than excluded.",
    "co_occurrence_parent costs no inductions and is wrong in both directions: it cannot "
    "see a load-bearing block lying above the induced rule's table span, and it links "
    "below-span blocks the rule does not need.",
    "the crossover is linear extrapolation from the mean per-revocation work of the five "
    "registered steps. Those steps are not a random sample of revocations; a different "
    "workload moves the crossover and the number should be read as 'revocations like "
    "these'.",
    "graph disclosure work is charged to the arm that has to derive a graph on demand and "
    "is reported separately from the crossover accounting, because serving a revocation "
    "does not require publishing a graph.",
)


def format_summary(rows: Sequence[Mapping]) -> str:  # pragma: no cover -- reporting
    head = (
        f"{'arm':28s} {'role':22s} {'scale':>6s} {'N':>5s} {'prec':>6s} {'rec':>6s} "
        f"{'stale':>6s} {'collat':>7s} {'build':>9s} {'revoc':>9s} {'total':>9s}"
    )
    lines = [head, "-" * len(head)]
    for row in rows:
        lines.append(
            f"{row['arm']:28s} {row['role']:22s} {row['scale']:>6s} {row['N']:>5d} "
            f"{row['graph_precision']:>6.3f} {row['graph_recall']:>6.3f} "
            f"{row['stale_survivors']:>6d} {row['collateral_invalidations']:>7d} "
            f"{row['build_work']:>9d} {row['revocation_work']:>9d} {row['total_work']:>9d}"
        )
    return "\n".join(lines)


def main() -> None:  # pragma: no cover -- reporting entry point
    results = sweep()
    rows = sweep_table(results)
    print(format_summary(rows))
    print()
    print("crossover revocations for learned_dependency_arm:")
    for scale, others in crossovers_for(rows).items():
        print(f"  {scale}: {others}")


if __name__ == "__main__":  # pragma: no cover
    main()
