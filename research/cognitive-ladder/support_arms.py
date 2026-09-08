"""Seven ways to answer "what is the whole set of ways to break this belief?".

``support.py`` supplies the world: eleven authored support archetypes, a
charged intervention channel, a declared per-method budget, and a powerset
oracle nobody may call.  This module supplies the arms and the sweep.

Every arm is handed **identical information**: the same store, the same
declared candidate evidence per method, the same public metadata, the same
intervention budget and the same registered revocation schedule.  They differ
only in which groups they choose to ablate, when, and what they keep.

The arms
--------

``adaptive_arm``
    Chooses which GROUP ablations to run.  Starts by asking whether ANYTHING is
    load-bearing (one intervention answers ``NO_LOAD_BEARING`` outright, where
    leave-one-out needs ``B``), then shrinks a known breaking set to a minimal
    one and enumerates the rest of the family by seeding into the part of the
    subset lattice its previous answers have not already determined.  This is
    MARCO/CAMUS-style MUS enumeration with a QuickXplain shrink; **no novelty is
    claimed for it**, it is parent-owned machinery and has also been
    independently implemented in a sibling lane of this programme.  What is
    measured is interventions spent AND total counted operations, side by side.

``leave_one_out_parent``
    The E3 mechanism, ported unchanged in spirit: ``B`` interventions, one per
    candidate block, and every block whose solo removal breaks the method is
    reported as a minimal support set of size one.  It must fail, exactly, on
    every archetype whose family contains a set of size two or more, and it must
    fail *silently* on ``REDUNDANT_SUPPORTS``, where it finds a real singleton,
    reports it, and stops with half the answer.  ``test_support.py`` asserts
    both.

``lazy_parent``
    Discovers nothing.  Zero interventions at acquisition, zero stored support
    family.  At revocation time it re-derives on demand: one charged ablation
    per candidate-affected method against the cumulative revoked set.  **This is
    the arm that DOMINATED the eager arm in the #144 capability-gated
    re-analysis of E3** -- 1317 against 7033 total work at N=80, 9237 against
    70249 at N=800, with zero stale survivors against the eager arm's one -- and
    it is the arm to beat here.  It is included and reported honestly.  Asking
    it for a support family costs it the whole enumeration it skipped; that cost
    is reported separately and never folded into total work, because serving a
    revocation does not require publishing a family.

``atms_gifted_parent``
    **THE GIFTED CEILING, labelled as such.**  Handed the justifications and
    told to compute the label: minimal supporting environments by fixpoint
    propagation, then minimal support sets as their minimal transversals.  Zero
    interventions, exactly correct.  Computing minimal supporting environments
    is what an ATMS has done since de Kleer (1986) and no novelty whatsoever is
    claimed for the machinery; the point of running it is that a ceiling you
    refuse to run is not a ceiling.

``atms_discovering_parent``
    The same ATMS, required to DISCOVER its justifications by intervention.  It
    recovers the label directly -- probing which evidence subsets SUFFICE rather
    than which BREAK -- then hitting-sets to the support family.  This is the
    fair comparison and the one the terminal rule reads.  Reporting only the
    gifted row would be reporting a ceiling as a result.

``exhaustive_powerset_parent``
    Ablates every one of the ``2**B - 1`` non-empty subsets.  Exactly correct,
    exponential, and DECLARED BUDGET EXEMPT, because a truncated exhaustive
    enumeration is a different arm and not a ceiling.  The correctness ceiling
    and the cost ceiling in the same row.

``random_group_ablation_parent``
    Samples random subsets under the same budget from a commitment-derived
    stream and reports the minimal breaking sets among those it happened to
    test.  The floor.  Without it, "adaptive selection works" would mean only
    "group ablation works", and those are different claims.

What separates them
-------------------

Not the support-family score of an arm that runs the oracle's own procedure:
``exhaustive_powerset_parent`` scores 1.0 on precision and recall for the
uninteresting reason that it enumerates the powerset, exactly as E3's learned
arm scored 1.0 by running leave-one-out.  The separating coordinates are:

* **interventions spent** to reach a given precision and recall;
* **total counted operations**, reported in the column beside it and never
  summed with it;
* **stale survivors**, the dangerous revocation error;
* **collateral invalidations**, the wasteful one;
* **total work against lazy_parent, including discovery**.

Parents: assumption-based truth maintenance (de Kleer); minimal hitting sets
and model-based diagnosis (Reiter); QuickXplain (Junker); MUS enumeration
(Liffiton & Sakallah, CAMUS; Liffiton et al., MARCO); delta debugging (Zeller
& Hildebrandt).  No novelty is claimed for any of them.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

from support import (
    COMMITMENT,
    EVIDENCE_PER_METHOD,
    INTERVENTION_BUDGET,
    SUPPORT_PLAN,
    BudgetExhausted,
    CheckStatus,
    INDEX_ENTRY_BYTES,
    InterventionMeter,
    ResourceRecord,
    RevisionRecord,
    RevocationStep,
    SupportCatalogue,
    SupportFamilyRecord,
    SupportWorld,
    TouchLedger,
    build_catalogue,
    build_world,
    fit_loglog,
    hitting_sets,
    minimal_sets,
    oracle_changed_methods,
    populate_store,
    powerset_bound,
    record_from_ledger,
    revocation_schedule,
    score_family,
    subsets_of,
)

__all__ = [
    "ARMS",
    "ARM_ROLES",
    "SWEEP_NOTES",
    "SupportArm",
    "AdaptiveArm",
    "LeaveOneOutParent",
    "LazyParent",
    "AtmsGiftedParent",
    "AtmsDiscoveringParent",
    "ExhaustivePowersetParent",
    "RandomGroupAblationParent",
    "ArmResult",
    "charged_work",
    "run_arm",
    "sweep",
    "sweep_table",
    "step_table",
    "archetype_table",
    "fits_for",
    "budget_curve",
    "summarise",
    "lazy_comparison",
    "capability_gated_comparison",
    "format_summary",
]


def charged_work(ledger: TouchLedger) -> int:
    """Every counted operation an arm actually spent.

    Deliberately INCLUDES index build and maintenance, as ``depend_arms``
    does.  The question here is whether choosing groups adaptively is worth it,
    and an accounting that left out the search an arm ran to choose its next
    group would answer that question by omission -- which is exactly the shape
    the sibling lane reported and this module has to be able to detect.
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


# --------------------------------------------------------------------------
# base
# --------------------------------------------------------------------------


class SupportArm:
    """One support-discovery architecture, installed over one catalogue.

    Subclasses implement ``_discover`` and may override ``_disclose``,
    ``_invalidate`` and ``_answer``.  Everything else -- the ledgers, the
    meter, the record construction, the comparison against the oracle -- is
    shared, so no arm can differ from another in the bookkeeping rather than in
    the architecture.
    """

    arm_id = "abstract"
    role = "ARM"
    discovery = "unspecified"
    budget_exempt = False
    disclosure_exempt = False

    def __init__(self, catalogue: SupportCatalogue, *, budget: int | None = None) -> None:
        self.catalogue = catalogue
        self.scale_id = catalogue.scale_id
        self.store = populate_store(catalogue)
        self.world: SupportWorld = build_world(catalogue)
        self.index_entries = 0
        #: what the arm believes: method id -> set of minimal support sets
        self.believed: dict[str, set[frozenset[str]]] = {}
        #: methods whose discovery ran out of budget, reported not hidden
        self.budget_exhausted_methods: set[str] = set()
        #: the arm's own memory of interventions it has already performed.
        #: Re-asking a question it already asked is free; asking a new one is
        #: not.  Shared by every arm so that "remembers its own experiments" is
        #: not an accidental advantage of one implementation.
        self._probe_cache: dict[tuple[str, frozenset[str]], bool] = {}
        self.budget_per_method = INTERVENTION_BUDGET if budget is None else budget
        self.meter = InterventionMeter(
            budget_per_method=self.budget_per_method, exempt=self.budget_exempt
        )
        self.revoked_evidence: set[str] = set()
        self.invalidated: set[str] = set()

        ledger = TouchLedger()
        self.meter.phase = "DISCOVERY"
        self._discover(ledger)
        self.discovery_ledger = ledger
        self.discovery_work = charged_work(ledger)
        self.discovery_interventions = self.meter.phase_total("DISCOVERY")
        self.discovery_record = self._record(ledger, operation="DISCOVERY")

    # ---- the charged channel --------------------------------------------

    def _ablate(
        self, method_id: str, removed: frozenset[str], ledger: TouchLedger
    ) -> bool:
        """Ask the world whether ``method_id`` survives losing ``removed``."""
        key = (method_id, removed)
        if key in self._probe_cache:
            ledger.probe_index()
            return self._probe_cache[key]
        answer = self.world.ablate(method_id, removed, ledger, self.meter)
        self._probe_cache[key] = answer
        return answer

    def _breaks(
        self, method_id: str, removed: frozenset[str], ledger: TouchLedger
    ) -> bool:
        return not self._ablate(method_id, removed, ledger)

    # ---- public metadata ------------------------------------------------

    def _methods(self, ledger: TouchLedger) -> list[str]:
        """Enumerate the methods by scanning the store.  Charged, never free."""
        out = []
        for obj in self.store.scan(ledger):
            ledger.index_build_work += 1
            if obj.object_class == "method":
                out.append(obj.object_id)
        return out

    def _candidates(self, method_id: str, ledger: TouchLedger) -> tuple[str, ...]:
        """A method's DECLARED candidate evidence, read off the stored object."""
        return self.store.read(method_id, ledger).candidates

    def _file(self, method_id: str, support_set: frozenset[str]) -> None:
        self.believed.setdefault(method_id, set()).add(support_set)
        self.index_entries += 1

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

    # ---- discovery ------------------------------------------------------

    def _discover(self, ledger: TouchLedger) -> None:
        raise NotImplementedError

    # ---- disclosure -----------------------------------------------------

    def _disclose(self, ledger: TouchLedger) -> dict[str, set[frozenset[str]]]:
        """Answer "what do you believe rests on what", and be charged for it.

        The default is an index probe per stored entry: an arm that holds a
        family answers from what it holds.  An arm that holds none has to
        derive one, and that derivation is charged here in full.
        """
        for method_id, sets in self.believed.items():
            for _ in sets:
                ledger.probe_index()
        return {k: set(v) for k, v in self.believed.items()}

    def disclose_family(self) -> SupportFamilyRecord:
        ledger = TouchLedger()
        previous = self.meter.phase
        self.meter.phase = "DISCLOSURE"
        exempt_before = self.meter.exempt
        self.meter.exempt = exempt_before or self.disclosure_exempt
        try:
            believed = self._disclose(ledger)
        finally:
            self.meter.exempt = exempt_before
            self.meter.phase = previous
        self.disclosure_ledger = ledger
        self.disclosure_work = charged_work(ledger)
        self.disclosure_interventions = self.meter.phase_total("DISCLOSURE")
        return score_family(
            self.arm_id,
            self.catalogue,
            believed,
            interventions=self.discovery_interventions,
            disclosure_work=self.disclosure_work,
            budget_exhausted_methods=len(self.budget_exhausted_methods),
        )

    # ---- revocation -----------------------------------------------------

    def _affected(self, method_id: str, revoked: frozenset[str], ledger: TouchLedger) -> bool:
        return bool(set(self._candidates(method_id, ledger)) & revoked)

    def _invalidate(
        self, cumulative_revoked: frozenset[str], newly: frozenset[str], ledger: TouchLedger
    ) -> list[str]:
        """The shared revocation rule: kill a method when a believed set is gone.

        Uniform across every arm that holds a support family, so the difference
        between those arms is entirely the family they discovered and not the
        policy they apply to it.  ``lazy_parent`` overrides this, because
        re-deriving instead of remembering IS its architecture.
        """
        observed: list[str] = []
        for method_id in self._methods(ledger):
            if method_id in self.invalidated:
                continue
            if not self._affected(method_id, newly, ledger):
                continue
            ledger.probe_index()
            for support_set in self.believed.get(method_id, ()):
                ledger.predicate_evaluations += 1
                if support_set <= cumulative_revoked:
                    self.store.revoke_method(method_id)
                    ledger.index_maintenance_work += 1
                    self.invalidated.add(method_id)
                    observed.append(method_id)
                    break
        return observed

    def revoke(self, step: RevocationStep) -> RevisionRecord:
        """Apply one registered revocation and score the arm's response.

        ``expected_changed_ids`` comes from :func:`oracle_changed_methods`,
        which ``_invalidate`` never consults -- the same separation
        ``depend_arms.DependencyArm.revoke`` keeps around the leave-one-out
        oracle.  The expectation includes the withdrawn evidence itself so that
        precision does not degenerate on the no-op steps.
        """
        live_before = self.store.live_evidence()
        live_after = live_before - set(step.evidence_ids)
        expected = frozenset(step.evidence_ids) | oracle_changed_methods(
            self.catalogue, live_before, live_after
        )
        ledger = TouchLedger()
        previous = self.meter.phase
        self.meter.phase = "REVOCATION"
        try:
            for evidence_id in step.evidence_ids:
                self.store.revoke_evidence(evidence_id)
                self.revoked_evidence.add(evidence_id)
            observed = set(step.evidence_ids) | set(
                self._invalidate(
                    frozenset(self.revoked_evidence),
                    frozenset(step.evidence_ids),
                    ledger,
                )
            )
        finally:
            self.meter.phase = previous
        poisoned = ledger.status is CheckStatus.CANNOT_CHECK
        return RevisionRecord(
            arm_id=self.arm_id,
            scale_id=self.scale_id,
            trigger_support_id=step.evidence_ids[0],
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

    # ---- the registered query stream ------------------------------------

    def _answer(self, method_id: str, ledger: TouchLedger) -> bool:
        """"Is this method still supported?", answered from what the arm holds."""
        ledger.probe_index()
        for support_set in self.believed.get(method_id, ()):
            ledger.predicate_evaluations += 1
            if support_set <= frozenset(self.revoked_evidence):
                return False
        return True

    def answer_queries(self) -> tuple[ResourceRecord, int, int]:
        """Ask every method "are you still supported?" after the schedule.

        The capability gate of protocol section 8: an efficiency number from an
        arm that answers wrongly is not admissible.  Correctness is scored
        against the world's own derivability, which is the same relation the
        charged channel exposes, so an arm cannot be wrong here for a reason
        that is not about what it discovered.
        """
        ledger = TouchLedger()
        previous = self.meter.phase
        self.meter.phase = "QUERY"
        correct = 0
        total = 0
        live = self.store.live_evidence()
        try:
            for method_id in self._methods(ledger):
                total += 1
                believed_live = self._answer(method_id, ledger)
                if believed_live == self.world.holds(method_id, live):
                    correct += 1
        finally:
            self.meter.phase = previous
        self.query_ledger = ledger
        self.query_work = charged_work(ledger)
        self.query_interventions = self.meter.phase_total("QUERY")
        return (
            self._record(ledger, operation="QUERY_STREAM"),
            correct,
            total,
        )


# --------------------------------------------------------------------------
# the shared group-ablation enumerator
# --------------------------------------------------------------------------


def _enumerate_minimal(
    predicate: Callable[[frozenset[str]], bool],
    universe: Sequence[str],
    ledger: TouchLedger,
) -> tuple[frozenset[frozenset[str]], bool]:
    """Enumerate the minimal subsets satisfying a MONOTONE ``predicate``.

    ``predicate`` is upward closed: if it holds of ``S`` it holds of every
    superset of ``S``.  Both objects this module needs are of that shape --
    "removing ``S`` breaks the method" and "``S`` alone suffices to derive the
    method" -- so one enumerator serves the adaptive arm and the discovering
    ATMS, and any difference between those two arms is a difference of which
    question they ask rather than of how well the answer was implemented.

    The procedure is MARCO/CAMUS-style and is parent-owned in every part:

    1. probe the whole universe once.  If it does not satisfy the predicate
       there is nothing to find and the answer is the empty family, at a cost
       of ONE intervention -- which is the whole reason group ablation exists,
       because leave-one-out needs ``B`` interventions to reach a weaker
       version of the same conclusion.
    2. shrink that satisfying seed to a minimal one, one element at a time
       (QuickXplain, Junker 2004).
    3. walk the subset lattice smallest-first, skipping every subset already
       determined by what earlier answers imply, probing the rest, shrinking a
       satisfying seed and growing a non-satisfying one to a maximal
       non-satisfying set so that everything below it is determined too.

    Every ``predicate`` call is a charged intervention.  Every lattice
    bookkeeping step is charged to ``ledger`` as a predicate evaluation, which
    is what stops "few interventions" from being bought with unbounded free
    search -- and is exactly the accounting a sibling lane's result says will
    decide this experiment.

    ``up`` holds sets known to satisfy the predicate and ``down`` sets known
    not to; both are used only to prune.  ``up`` is written to only by paths
    that also record a minimal subset, which is what makes the enumeration
    complete: a minimal satisfying set is never pruned by a fact that did not
    already account for it.

    Returns ``(minimal sets, exhausted)``.  ``exhausted`` is ``True`` when the
    budget ran out, and the partial family is returned rather than discarded:
    an arm that ran out of budget has a partial answer and the receipt says so.
    """
    universe = tuple(universe)
    full = frozenset(universe)
    up: list[frozenset[str]] = []
    down: list[frozenset[str]] = []
    minimal: list[frozenset[str]] = []

    def determined(candidate: frozenset[str]) -> bool:
        ledger.predicate_evaluations += len(up) + len(down)
        return any(u <= candidate for u in up) or any(candidate <= d for d in down)

    def shrink(seed: frozenset[str]) -> frozenset[str]:
        current = seed
        for element in sorted(seed):
            smaller = current - {element}
            if predicate(smaller):
                current = smaller
            else:
                down.append(smaller)
        return current

    def grow(seed: frozenset[str]) -> frozenset[str]:
        current = seed
        for element in sorted(full - seed):
            bigger = current | {element}
            if not predicate(bigger):
                current = bigger
        return current

    def record_satisfying(seed: frozenset[str]) -> None:
        ledger.predicate_evaluations += len(minimal)
        up.append(seed)
        if any(m <= seed for m in minimal):
            return
        minimal.append(shrink(seed))

    try:
        if not predicate(full):
            return frozenset(), False
        record_satisfying(full)
        for candidate in subsets_of(universe):
            if determined(candidate):
                continue
            if predicate(candidate):
                record_satisfying(candidate)
            else:
                down.append(candidate)
                down.append(grow(candidate))
    except BudgetExhausted:
        return minimal_sets(minimal), True
    return minimal_sets(minimal), False


# --------------------------------------------------------------------------
# the arm under test
# --------------------------------------------------------------------------


class AdaptiveArm(SupportArm):
    """Chooses which GROUP to ablate next, under the charged budget.

    Its first intervention on every method asks whether removing ALL the
    candidate evidence breaks it.  That single question settles the
    ``NO_LOAD_BEARING`` archetype outright, where leave-one-out spends ``B``
    interventions to conclude the same thing less reliably, and it hands the
    shrink step a breaking set to work down from.

    No novelty is claimed.  This is MUS enumeration with a QuickXplain shrink
    and it is parent-owned; a sibling lane of this programme has independently
    implemented the same object.  The reason it is here is to be compared
    against the parents on TWO columns at once -- interventions spent and total
    counted operations -- because the hypothesis under test is precisely that
    the first column improves while the second gets worse.
    """

    arm_id = "adaptive_arm"
    role = "ARM"
    discovery = "adaptive group ablation: whole-set probe, QuickXplain shrink, MARCO seeds"

    def _discover(self, ledger: TouchLedger) -> None:
        for method_id in self._methods(ledger):
            candidates = self._candidates(method_id, ledger)

            def breaks(removed: frozenset[str], _m=method_id) -> bool:
                return self._breaks(_m, removed, ledger)

            family, exhausted = _enumerate_minimal(breaks, candidates, ledger)
            if exhausted:
                self.budget_exhausted_methods.add(method_id)
            for support_set in family:
                self._file(method_id, support_set)


# --------------------------------------------------------------------------
# the parent this experiment exists to replace
# --------------------------------------------------------------------------


class LeaveOneOutParent(SupportArm):
    """The E3 mechanism.  ``B`` interventions, singletons only.

    Its probe granularity is fixed at one element by design, which is the root
    ``PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED`` restated as code.  It
    reports every block whose solo removal breaks the method as a minimal
    support set of size one, and it can express nothing else.

    It is therefore exactly right on ``SINGLE_SUPPORT``, ``DEEP_CHAIN`` and
    ``SHARED_GLOBAL``; blind on ``ALTERNATIVE_SUPPORTS``, ``TWO_OF_THREE``,
    ``CONDITIONAL_SUPPORT``, ``HIGHER_ORDER_INTERACTION``, ``CYCLIC`` and
    ``REPRESENTATION_DEPENDENT``, where it reports an empty family and calls it
    an answer; and half right on ``REDUNDANT_SUPPORTS``, which is the worst
    case, because there it returns a true singleton and no indication that
    anything is missing.  ``test_support.py`` asserts the partition, which is
    claim C11 reproduced exactly rather than cited.
    """

    arm_id = "leave_one_out_parent"
    role = "PARENT"
    discovery = "single-element ablation at acquisition time, cached (the E3 mechanism)"

    def _discover(self, ledger: TouchLedger) -> None:
        for method_id in self._methods(ledger):
            candidates = self._candidates(method_id, ledger)
            for evidence_id in candidates:
                try:
                    if self._breaks(method_id, frozenset({evidence_id}), ledger):
                        self._file(method_id, frozenset({evidence_id}))
                except BudgetExhausted:  # pragma: no cover -- B is below the budget
                    self.budget_exhausted_methods.add(method_id)
                    break


# --------------------------------------------------------------------------
# the arm to beat
# --------------------------------------------------------------------------


class LazyParent(SupportArm):
    """Discovers nothing.  Re-derives on demand at revocation time.

    Zero interventions and zero work at acquisition.  On each revocation it
    walks the store, finds the methods whose candidate evidence lost a block,
    and spends ONE charged ablation per such method against the cumulative
    revoked set.  Exactly correct at every step, including every archetype the
    other arms need a family to survive, because it never relies on a snapshot
    of which evidence mattered.

    This arm is not a strawman.  In the #144 capability-gated re-analysis of E3
    -- where a work comparison is admissible only between arms at precision and
    recall 1.0 -- it DOMINATED the eager learned-dependency arm: 1317 against
    7033 total work at N=80, 9237 against 70249 at N=800, and it left zero
    stale survivors where the eager arm left one.  Correctness by
    re-derivation is the oldest trick in the book, it is not a finding, and the
    burden is entirely on any discovering arm to beat it on total work.

    Asking it for a support family costs it the enumeration it skipped.  That
    disclosure is declared budget exempt and is reported in its own column,
    never folded into total work, because serving a revocation does not require
    publishing a family.
    """

    arm_id = "lazy_parent"
    role = "PARENT"
    discovery = "none; one charged re-derivation per affected method at revocation time"
    disclosure_exempt = True

    def _discover(self, ledger: TouchLedger) -> None:
        return None

    def _invalidate(
        self, cumulative_revoked: frozenset[str], newly: frozenset[str], ledger: TouchLedger
    ) -> list[str]:
        observed: list[str] = []
        for method_id in self._methods(ledger):
            if method_id in self.invalidated:
                continue
            ledger.predicate_evaluations += 1
            if not self._affected(method_id, newly, ledger):
                continue
            if self._breaks(method_id, cumulative_revoked, ledger):
                self.store.revoke_method(method_id)
                ledger.index_maintenance_work += 1
                self.invalidated.add(method_id)
                observed.append(method_id)
        return observed

    def _answer(self, method_id: str, ledger: TouchLedger) -> bool:
        return not self._breaks(method_id, frozenset(self.revoked_evidence), ledger)

    def _disclose(self, ledger: TouchLedger) -> dict[str, set[frozenset[str]]]:
        """The receipt for "cheap to build".

        Charged in full and metered in full: the interventions appear in the
        DISCLOSURE column, where a reader can see that an arm nobody asks is
        cheap and an arm somebody asks is not.
        """
        return _exhaustive_families(self, ledger)


def _exhaustive_families(
    arm: SupportArm, ledger: TouchLedger
) -> dict[str, set[frozenset[str]]]:
    """Powerset enumeration through the charged channel, run by an arm.

    Shared by ``lazy_parent``'s disclosure path and by
    ``exhaustive_powerset_parent``'s discovery.  It is the oracle's own
    procedure paid for at the arm's own till: ``2**B - 1`` interventions per
    method.  Putting it in one function keeps the difference between those two
    arms -- WHEN they pay, not WHAT they compute -- from being an
    implementation accident.
    """
    out: dict[str, set[frozenset[str]]] = {}
    for method_id in arm._methods(ledger):
        candidates = arm._candidates(method_id, ledger)
        breaking = []
        for candidate in subsets_of(candidates):
            if not candidate:
                continue
            if arm._breaks(method_id, candidate, ledger):
                breaking.append(candidate)
        family = minimal_sets(breaking)
        if family:
            out[method_id] = set(family)
    return out


# --------------------------------------------------------------------------
# the ATMS, run both ways
# --------------------------------------------------------------------------


class AtmsGiftedParent(SupportArm):
    """THE GIFTED CEILING.  Handed the justifications, computes the label.

    Label propagation to a least fixpoint over the assumption lattice gives the
    minimal supporting ENVIRONMENTS of each method; the minimal support sets
    are their minimal transversals.  Zero interventions, exactly correct.

    **Computing minimal supporting environments is what an ATMS has done since
    de Kleer (1986), and no novelty is claimed for any of this machinery.**  The
    dual step is Reiter (1987).  This arm is here for the same reason
    ``depend_arms.DeclaredSupportsParent`` was: it is given something the
    experiment exists to take away, it is labelled accordingly, and a ceiling
    you refuse to run is not a ceiling.

    Its label computation enumerates the assumption lattice rather than
    propagating incrementally.  That costs it counted operations and buys it
    nothing in interventions, and it is stated rather than optimised because
    the arm's role is the correctness ceiling, not the cost ceiling.
    """

    arm_id = "atms_gifted_parent"
    role = "PARENT_GIFTED_CEILING"
    discovery = "given the justifications; ATMS label to minimal environments, then transversals"

    def _label(self, instance, method_id: str, ledger: TouchLedger) -> frozenset[frozenset[str]]:
        inside_cache: dict[frozenset[str], bool] = {}
        for environment in subsets_of(instance.evidence_ids):
            inside = set(instance.axiom_ids) | set(environment)
            changed = True
            while changed:
                changed = False
                ledger.search_expansions += 1
                for justification in instance.justifications:
                    if justification.consequent in inside:
                        continue
                    ledger.predicate_evaluations += len(justification.antecedents)
                    if all(a in inside for a in justification.antecedents):
                        inside.add(justification.consequent)
                        changed = True
            inside_cache[environment] = method_id in inside
        return minimal_sets(e for e, ok in inside_cache.items() if ok)

    def _discover(self, ledger: TouchLedger) -> None:
        for instance in self.catalogue.instances:
            ledger.index_build_work += 1
            for method_id in instance.method_ids:
                self.store.read(method_id, ledger)
                environments = self._label(instance, method_id, ledger)
                ledger.predicate_evaluations += len(environments)
                for support_set in hitting_sets(environments):
                    self._file(method_id, support_set)


class AtmsDiscoveringParent(SupportArm):
    """The same ATMS, required to discover its label by intervention.

    It asks the dual question to the adaptive arm's.  Where the adaptive arm
    probes which groups BREAK the method and reads the minimal support sets off
    directly, this one probes which groups SUFFICE -- an ablation that removes
    everything except the candidate environment -- recovers the minimal
    environments, and hitting-sets them into the support family.

    **This is the fair configuration and it is the one the terminal rule
    reads.**  The gifted row above is a ceiling; reporting only that row would
    be reporting a gift as a result.  Both rows appear in the receipt.
    """

    arm_id = "atms_discovering_parent"
    role = "PARENT"
    discovery = "ATMS label discovered by intervention: minimal environments, then transversals"

    def _discover(self, ledger: TouchLedger) -> None:
        for method_id in self._methods(ledger):
            candidates = self._candidates(method_id, ledger)
            everything = frozenset(candidates)

            def sufficient(environment: frozenset[str], _m=method_id) -> bool:
                return self._ablate(_m, everything - environment, ledger)

            environments, exhausted = _enumerate_minimal(sufficient, candidates, ledger)
            if exhausted:
                self.budget_exhausted_methods.add(method_id)
            ledger.predicate_evaluations += len(environments)
            for support_set in hitting_sets(environments):
                self._file(method_id, support_set)


# --------------------------------------------------------------------------
# the ceiling and the floor
# --------------------------------------------------------------------------


class ExhaustivePowersetParent(SupportArm):
    """Ablates every non-empty subset.  Exactly correct, exponential.

    ``2**B - 1`` interventions per method, which at the frozen width is 63
    against a declared budget of 24.  It is **DECLARED BUDGET EXEMPT**, with
    the exemption printed in the receipt, because truncating an exhaustive
    enumeration produces a different arm rather than a weakened ceiling.

    Its precision and recall of 1.0 against the powerset oracle is arithmetic
    and not evidence: it runs the oracle's own procedure, exactly as E3's
    learned arm ran leave-one-out's.  The row exists so the interventions
    column has a top.
    """

    arm_id = "exhaustive_powerset_parent"
    role = "PARENT_CORRECTNESS_CEILING"
    discovery = "every non-empty subset of the candidate evidence is ablated"
    budget_exempt = True

    def _discover(self, ledger: TouchLedger) -> None:
        for method_id, family in _exhaustive_families(self, ledger).items():
            for support_set in family:
                self._file(method_id, support_set)


class RandomGroupAblationParent(SupportArm):
    """Samples random subsets under the same budget.  The floor.

    Without it, a result showing that the adaptive arm beats leave-one-out
    would establish only that GROUP ablation beats SINGLE-element ablation,
    which is not in doubt and is not the claim.  This arm has the same
    granularity freedom and the same budget as the adaptive arm and spends it
    without direction.

    Its sample stream is drawn from the pre-registration commitment, so the
    floor is not re-rolled if it happens to land badly, and a third party
    re-derives the identical stream from the plan hash.  It reports the minimal
    breaking sets among the subsets it happened to test, which is why it is
    wrong in both directions: it misses families it never sampled and it
    reports non-minimal sets as minimal when it never sampled the smaller
    subset that would have refuted them.
    """

    arm_id = "random_group_ablation_parent"
    role = "PARENT_FLOOR"
    discovery = "random subsets under the same budget, from the committed stream"

    def _discover(self, ledger: TouchLedger) -> None:
        rng = random.Random(
            COMMITMENT.stream(f"support-random-ablation-v1::{self.scale_id}") % (2**63)
        )
        for method_id in self._methods(ledger):
            candidates = self._candidates(method_id, ledger)
            pool = [s for s in subsets_of(candidates) if s]
            rng.shuffle(pool)
            breaking: list[frozenset[str]] = []
            for candidate in pool[: self.budget_per_method]:
                try:
                    if self._breaks(method_id, candidate, ledger):
                        breaking.append(candidate)
                except BudgetExhausted:  # pragma: no cover -- the slice is the budget
                    self.budget_exhausted_methods.add(method_id)
                    break
            for support_set in minimal_sets(breaking):
                self._file(method_id, support_set)


# --------------------------------------------------------------------------
# the registry
# --------------------------------------------------------------------------

ARMS: dict[str, Callable[[SupportCatalogue], SupportArm]] = {
    "adaptive_arm": AdaptiveArm,
    "leave_one_out_parent": LeaveOneOutParent,
    "lazy_parent": LazyParent,
    "atms_gifted_parent": AtmsGiftedParent,
    "atms_discovering_parent": AtmsDiscoveringParent,
    "exhaustive_powerset_parent": ExhaustivePowersetParent,
    "random_group_ablation_parent": RandomGroupAblationParent,
}

#: Declared before the run.  ``ARM`` is under test; the rest get first right of
#: refusal, and the two ceilings carry the reason they are only ceilings.
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
    n_evidence: int
    discovery_record: ResourceRecord
    discovery_work: int
    discovery_interventions: int
    disclosure_work: int
    disclosure_interventions: int
    query_record: ResourceRecord
    query_work: int
    query_interventions: int
    queries_correct: int
    queries_total: int
    revocation_interventions: int
    index_bytes: int
    budget_exempt: bool
    revisions: tuple[RevisionRecord, ...]
    family: SupportFamilyRecord

    @property
    def revocation_work(self) -> int:
        return sum(r.revision_work or 0 for r in self.revisions)

    @property
    def update_work(self) -> int:
        """Index maintenance triggered by the world changing under the arm."""
        return sum(r.index_maintenance_work for r in self.revisions)

    @property
    def stale_survivors(self) -> int:
        return sum(len(r.stale_survivor_ids) for r in self.revisions)

    @property
    def collateral_invalidations(self) -> int:
        return sum(len(r.collateral_invalidated_ids) for r in self.revisions)

    @property
    def total_work(self) -> int:
        """Discovery plus revocation plus query.

        Disclosure is NOT included, on the convention ``depend_arms`` set: an
        arm is not obliged to publish its support family in order to serve a
        revocation, and folding a disclosure into the total would charge
        ``lazy_parent`` for a service it does not offer.
        """
        return self.discovery_work + self.revocation_work + self.query_work

    @property
    def total_interventions(self) -> int:
        return (
            self.discovery_interventions
            + self.revocation_interventions
            + self.query_interventions
        )

    @property
    def capability_gate(self) -> bool:
        """Protocol section 8: no efficiency number is read from a wrong arm."""
        return self.queries_correct == self.queries_total


def _run_cell(factory, catalogue: SupportCatalogue) -> ArmResult:
    """Install the arm, disclose its family, run the schedule, then query.

    Disclosure happens BEFORE any revocation so the family endpoint is about
    what the arm knew at acquisition, which is the coordinate the experiment is
    about.  The query stream runs AFTER the schedule so the capability gate is
    evaluated on a world that has actually changed.
    """
    arm = factory(catalogue)
    family = arm.disclose_family()
    revisions = tuple(arm.revoke(step) for step in revocation_schedule(catalogue))
    revocation_interventions = arm.meter.phase_total("REVOCATION")
    query_record, correct, total = arm.answer_queries()
    return ArmResult(
        arm_id=arm.arm_id,
        role=arm.role,
        scale_id=catalogue.scale_id,
        multiplier=catalogue.multiplier,
        n_objects=arm.n_objects,
        n_methods=catalogue.n_methods,
        n_evidence=catalogue.n_evidence,
        discovery_record=arm.discovery_record,
        discovery_work=arm.discovery_work,
        discovery_interventions=arm.discovery_interventions,
        disclosure_work=arm.disclosure_work,
        disclosure_interventions=arm.disclosure_interventions,
        query_record=query_record,
        query_work=arm.query_work,
        query_interventions=arm.query_interventions,
        queries_correct=correct,
        queries_total=total,
        revocation_interventions=revocation_interventions,
        index_bytes=arm.index_bytes,
        budget_exempt=arm.budget_exempt or arm.disclosure_exempt,
        revisions=revisions,
        family=family,
    )


def run_arm(arm_id: str, multiplier: int) -> ArmResult:
    return _run_cell(ARMS[arm_id], build_catalogue(multiplier))


def sweep(arm_ids: Sequence[str] | None = None) -> dict[str, list[ArmResult]]:
    """Every registered arm at every frozen scale."""
    chosen = list(ARMS) if arm_ids is None else list(arm_ids)
    return {
        arm_id: [
            _run_cell(ARMS[arm_id], build_catalogue(m))
            for m in SUPPORT_PLAN["multipliers"]
        ]
        for arm_id in chosen
    }


# --------------------------------------------------------------------------
# tables
# --------------------------------------------------------------------------


def sweep_table(results: Mapping[str, Sequence[ArmResult]]) -> list[dict]:
    """One flat row per (arm, scale).

    ``interventions`` and ``total_work`` are two columns and there is
    deliberately no column that combines them, for the same reason there is no
    column that adds stale survivors to collateral invalidations.  An arm that
    spends fewer interventions and more operations has moved cost between two
    coordinates; anybody who wants to call that an improvement has to say which
    coordinate they are buying with the other, and that decision does not
    belong in this table.
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
                    "evidence_blocks": result.n_evidence,
                    "budget_exempt": result.budget_exempt,
                    "family_precision": result.family.precision,
                    "family_recall": result.family.recall,
                    "family_exact": result.family.exact,
                    "true_support_sets": result.family.n_true_sets,
                    "believed_support_sets": result.family.n_believed_sets,
                    "missed_sets": len(result.family.missing),
                    "spurious_sets": len(result.family.extra),
                    "budget_exhausted_methods": result.family.budget_exhausted_methods,
                    "discovery_interventions": result.discovery_interventions,
                    "disclosure_interventions": result.disclosure_interventions,
                    "revocation_interventions": result.revocation_interventions,
                    "query_interventions": result.query_interventions,
                    "total_interventions": result.total_interventions,
                    "discovery_work": result.discovery_work,
                    "disclosure_work": result.disclosure_work,
                    "revocation_work": result.revocation_work,
                    "query_work": result.query_work,
                    "update_work": result.update_work,
                    "total_work": result.total_work,
                    "index_bytes": result.index_bytes,
                    "persistent_bytes": result.discovery_record.persistent_bytes,
                    "stale_survivors": result.stale_survivors,
                    "collateral_invalidations": result.collateral_invalidations,
                    "exact_revocations": sum(
                        1 for r in result.revisions if r.exact_revocation
                    ),
                    "revocations": len(result.revisions),
                    "queries_correct": result.queries_correct,
                    "queries_total": result.queries_total,
                    "capability_gate": result.capability_gate,
                }
            )
    return rows


def archetype_table(results: Mapping[str, Sequence[ArmResult]]) -> list[dict]:
    """One row per (arm, scale, archetype): where the blindness is legible.

    An aggregate can hide a family an arm cannot see among ten it can, and the
    family it cannot see is the finding.
    """
    rows: list[dict] = []
    for arm_id, per_scale in results.items():
        for result in per_scale:
            for archetype_id, scores in result.family.per_archetype.items():
                rows.append(
                    {
                        "arm": arm_id,
                        "scale": result.scale_id,
                        "archetype": archetype_id,
                        **{k: v for k, v in scores.items()},
                    }
                )
    return rows


def step_table(results: Mapping[str, Sequence[ArmResult]]) -> list[dict]:
    """One row per (arm, scale, registered revocation step)."""
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
                        "stale_survivor_ids": list(record.stale_survivor_ids[:4]),
                        "collateral_invalidations": len(record.collateral_invalidated_ids),
                        "exact": record.exact_revocation,
                        "revision_work": record.revision_work,
                        "k": record.k,
                    }
                )
    return rows


#: Coordinates fitted against ``N`` for every arm.
FITTED_COORDINATES: tuple[tuple[str, str], ...] = (
    ("discovery_interventions(N)", "discovery_interventions"),
    ("discovery_work(N)", "discovery_work"),
    ("revocation_work(N)", "revocation_work"),
    ("total_work(N)", "total_work"),
    ("believed_support_sets(N)", "believed_support_sets"),
    ("persistent_bytes(N)", "persistent_bytes"),
)


def fits_for(rows: Sequence[Mapping]) -> dict:
    """Fit each registered relation against ``N``, per arm.

    ``fit_loglog`` refuses an exponent when a straight line does not describe
    the points and refuses anything at all on a non-positive coordinate, so an
    arm whose discovery interventions are zero at every scale gets
    ``UNDEFINED_NONPOSITIVE_VALUES`` rather than a fabricated slope.
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
# the declared residual coordinate, measured as a curve
# --------------------------------------------------------------------------


def budget_curve(
    multiplier: int, budgets: Sequence[int] | None = None
) -> list[dict]:
    """Precision, recall, interventions and work at each declared budget.

    The declared residual coordinate is "interventions spent to reach a given
    support-family precision and recall".  One budget reports one point on that
    curve.  This reports the curve, which is what
    ``ROOT_CAUSE_ANALYSIS_V1.md`` demands of any knob a result depends on: the
    reported object is the curve, never a single favourable setting.

    Both columns appear at every point.  An arm that reaches a given recall at
    fewer interventions and more counted operations has moved cost between two
    coordinates and the curve says so at every budget, rather than at the one
    budget somebody chose.
    """
    points = list(SUPPORT_PLAN["budget_curve_points"]) if budgets is None else list(budgets)
    catalogue = build_catalogue(multiplier)
    rows: list[dict] = []
    for arm_id, factory in ARMS.items():
        for budget in points:
            arm = factory(catalogue, budget=budget)
            record = arm.disclose_family()
            rows.append(
                {
                    "arm": arm_id,
                    "role": arm.role,
                    "scale": catalogue.scale_id,
                    "budget_per_method": budget,
                    "budget_exempt": arm.budget_exempt or arm.disclosure_exempt,
                    "precision": round(record.precision, 6),
                    "recall": round(record.recall, 6),
                    "exact": record.exact,
                    "discovery_interventions": arm.discovery_interventions,
                    "discovery_work": arm.discovery_work,
                    "budget_exhausted_methods": record.budget_exhausted_methods,
                }
            )
    return rows


# --------------------------------------------------------------------------
# the summary the terminal rule reads
# --------------------------------------------------------------------------


def summarise(rows: Sequence[Mapping]) -> dict:
    """Per-arm coordinates aggregated over the frozen scales.

    Precision and recall are reported as the exact list of values seen across
    scales, never as a mean, on the convention ``depend_arms.summarise`` set:
    an arm perfect at three scales and blind at the fourth has a blindness, and
    an average describes an arm that does not exist.
    """
    out: dict[str, dict] = {}
    for arm_id in sorted({r["arm"] for r in rows}):
        mine = [r for r in rows if r["arm"] == arm_id]
        out[arm_id] = {
            "role": mine[0]["role"],
            "discovery": mine[0]["discovery"],
            "budget_exempt": mine[0]["budget_exempt"],
            "precision_by_scale": [round(r["family_precision"], 6) for r in mine],
            "recall_by_scale": [round(r["family_recall"], 6) for r in mine],
            "exact_by_scale": [r["family_exact"] for r in mine],
            "discovery_interventions_by_scale": [
                r["discovery_interventions"] for r in mine
            ],
            "disclosure_interventions_by_scale": [
                r["disclosure_interventions"] for r in mine
            ],
            "total_interventions_by_scale": [r["total_interventions"] for r in mine],
            "discovery_work_by_scale": [r["discovery_work"] for r in mine],
            "revocation_work_by_scale": [r["revocation_work"] for r in mine],
            "query_work_by_scale": [r["query_work"] for r in mine],
            "update_work_by_scale": [r["update_work"] for r in mine],
            "total_work_by_scale": [r["total_work"] for r in mine],
            "persistent_bytes_by_scale": [r["persistent_bytes"] for r in mine],
            "stale_survivors_by_scale": [r["stale_survivors"] for r in mine],
            "collateral_by_scale": [r["collateral_invalidations"] for r in mine],
            "capability_gate_by_scale": [r["capability_gate"] for r in mine],
            "budget_exhausted_by_scale": [r["budget_exhausted_methods"] for r in mine],
            "total_stale_survivors": sum(r["stale_survivors"] for r in mine),
            "total_collateral": sum(r["collateral_invalidations"] for r in mine),
            "total_work": sum(r["total_work"] for r in mine),
            "total_discovery_interventions": sum(
                r["discovery_interventions"] for r in mine
            ),
        }
    return out


def lazy_comparison(summary: Mapping[str, Mapping]) -> dict:
    """Every arm against ``lazy_parent``, on the two columns, side by side.

    The comparison the brief demands and the one the sibling lane's result
    predicts will go badly: fewer interventions, more total work.  Both ratios
    are reported and neither is combined with the other.
    """
    lazy = summary["lazy_parent"]
    out: dict[str, dict] = {}
    for arm_id, row in summary.items():
        if arm_id == "lazy_parent":
            continue
        out[arm_id] = {
            "total_work_by_scale": list(row["total_work_by_scale"]),
            "lazy_total_work_by_scale": list(lazy["total_work_by_scale"]),
            "work_ratio_by_scale": [
                round(a / b, 4) if b else None
                for a, b in zip(row["total_work_by_scale"], lazy["total_work_by_scale"])
            ],
            "beats_lazy_on_total_work_at_every_scale": all(
                a < b
                for a, b in zip(row["total_work_by_scale"], lazy["total_work_by_scale"])
            ),
            "discovery_interventions_by_scale": list(
                row["discovery_interventions_by_scale"]
            ),
            "lazy_discovery_interventions_by_scale": list(
                lazy["discovery_interventions_by_scale"]
            ),
            "stale_survivors_by_scale": list(row["stale_survivors_by_scale"]),
            "lazy_stale_survivors_by_scale": list(lazy["stale_survivors_by_scale"]),
        }
    return out


def capability_gated_comparison(summary: Mapping[str, Mapping]) -> dict:
    """The #144 gate, applied here as it was applied to E3.

    A work comparison is admissible only between arms at support-family
    precision AND recall of 1.0 at every registered scale.  An arm that is
    cheaper because it stopped early has not been shown to be cheaper; it has
    been shown to have answered a smaller question.  That gate is what turned
    E3's eager-discovery result around, and it is applied here before any
    total-work number is read.

    Reports the admitted arms, the arms excluded and why, and -- for the
    admitted set only -- total work and interventions side by side, never
    summed.
    """
    admitted: list[str] = []
    excluded: dict[str, str] = {}
    for arm_id, row in summary.items():
        if all(p == 1.0 for p in row["precision_by_scale"]) and all(
            r == 1.0 for r in row["recall_by_scale"]
        ):
            admitted.append(arm_id)
        else:
            excluded[arm_id] = (
                f"precision {row['precision_by_scale']}, recall {row['recall_by_scale']}: "
                "not at 1.0 at every scale, so its work is not comparable"
            )
    ranked = sorted(admitted, key=lambda a: summary[a]["total_work_by_scale"])
    return {
        "gate": (
            "support-family precision AND recall of 1.0 at every registered scale, "
            "the #144 rule under which the eager arm of E3 was found to be dominated"
        ),
        "admitted": sorted(admitted),
        "excluded": excluded,
        "total_work_by_scale": {
            arm_id: list(summary[arm_id]["total_work_by_scale"]) for arm_id in admitted
        },
        "discovery_interventions_by_scale": {
            arm_id: list(summary[arm_id]["discovery_interventions_by_scale"])
            for arm_id in admitted
        },
        "stale_survivors_by_scale": {
            arm_id: list(summary[arm_id]["stale_survivors_by_scale"])
            for arm_id in admitted
        },
        "cheapest_admitted_arm_by_total_work": ranked[0] if ranked else None,
        "note": (
            "the two columns are reported side by side and are NEVER summed. An arm "
            "cheaper on interventions and dearer on counted operations has moved cost "
            "between coordinates, and this table refuses to decide on the reader's "
            "behalf which of the two they are buying with the other."
        ),
    }


SWEEP_NOTES: tuple[str, ...] = (
    "the powerset oracle is computed by brute force in the scorer and is handed to no "
    "arm; a source-inspection test refuses any arm class that mentions it.",
    "exhaustive_powerset_parent attains precision and recall 1.0 for the uninteresting "
    "reason that it runs the oracle's own procedure. That is arithmetic, not evidence, "
    "and it is reported as a ceiling rather than as a result.",
    "INTERVENTIONS AND TOTAL COUNTED OPERATIONS ARE TWO COLUMNS AND ARE NEVER SUMMED. A "
    "sibling lane of this programme (research/epistemic-structure-discovery-20260908) "
    "reported that active model enumeration lowers queries but costs more, and "
    "results/REINDEX_E9_V1.json found the same shape in a different place. If the "
    "adaptive arm reproduces it here that is an independent replication and is the "
    "headline, not a caveat.",
    "NO NOVELTY IS CLAIMED FOR THE LEARNER. Minimal-support / antichain discovery is "
    "parent-owned -- de Kleer 1986 for minimal environments, Reiter 1987 for the hitting-"
    "set dual, Junker 2004 for the shrink, the CAMUS/MARCO line for the enumeration -- "
    "and has been independently implemented elsewhere in this programme. What this "
    "experiment contributes is the parent comparison and the family taxonomy.",
    "leave_one_out_parent is the E3 mechanism. It is exactly right on the archetypes "
    "whose support family is all singletons, blind on the ones whose family has no "
    "singleton, and HALF right on REDUNDANT_SUPPORTS, where it returns a true singleton "
    "and no indication that a pair is missing. That partition is claim C11 reproduced "
    "rather than cited.",
    "lazy_parent is the arm to beat. In the #144 capability-gated re-analysis of E3 it "
    "dominated the eager arm on total work at every scale and left zero stale survivors. "
    "Any discovering arm here carries the whole burden of beating it.",
    "atms_gifted_parent is a CEILING: it is handed the justifications and needs zero "
    "interventions. atms_discovering_parent is the fair comparison and is the row the "
    "terminal rule reads. Both are reported.",
    "stale survivors and collateral invalidations are asymmetric and are never summed.",
    "the archetypes are AUTHORED. Their support families are the ones the experiment "
    "wanted to see, so no RATE quoted here transfers anywhere; E3's 16-25% came from a "
    "world that produced the shapes on its own and this one does not pretend to.",
    "B = 6 candidate blocks per method, so the powerset oracle enumerates 63 non-empty "
    "subsets per method and is exactly computable. Every intervention count here is a "
    "count for a six-element candidate set.",
)


def format_summary(rows: Sequence[Mapping]) -> str:  # pragma: no cover -- reporting
    head = (
        f"{'arm':30s} {'role':26s} {'scale':>5s} {'N':>5s} {'prec':>6s} {'rec':>6s} "
        f"{'d_intv':>7s} {'d_work':>9s} {'total_w':>9s} {'stale':>6s} {'collat':>7s}"
    )
    lines = [head, "-" * len(head)]
    for row in rows:
        lines.append(
            f"{row['arm']:30s} {row['role']:26s} {row['scale']:>5s} {row['N']:>5d} "
            f"{row['family_precision']:>6.3f} {row['family_recall']:>6.3f} "
            f"{row['discovery_interventions']:>7d} {row['discovery_work']:>9d} "
            f"{row['total_work']:>9d} {row['stale_survivors']:>6d} "
            f"{row['collateral_invalidations']:>7d}"
        )
    return "\n".join(lines)


def main() -> None:  # pragma: no cover -- reporting entry point
    results = sweep()
    rows = sweep_table(results)
    print(format_summary(rows))


if __name__ == "__main__":  # pragma: no cover
    main()
