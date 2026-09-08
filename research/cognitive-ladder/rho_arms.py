"""E7 arms: six persistence policies over one stream, and the rho sweep.

``rho.py`` supplies the ecology: a commitment-derived task stream, an exact
independent checker, the registered procedure set and the certificate that says
which tasks **essentially require** structure acquired earlier.  This module
supplies the arms and the sweep.

Every arm is handed **identical information**: the same stream, the same tasks in
the same order, the same checker, the same registered procedures and the same
budget.  They differ in exactly one thing --- what they persist and when they
decide to acquire it --- and the query path is literally the same code for all of
them, because the cheapest way to manufacture a difference is to write two
implementations and let an incidental asymmetry creep in.

The arms
--------

``persistent_arm``  (ARM, the machine)
    Acquires a method from every task it had to solve by dynamic programming,
    persists it, indexes it, and reuses it.  Eager: it pays discovery the first
    time it meets a family, whether or not that family is ever demanded again.
    It also maintains support-to-method dependency edges.

``reset_arm``  (ABLATION)
    Persists nothing.  Solves every task from scratch with the best method-free
    procedure.  This is protocol ``P0`` with no memory, and it supplies the
    ``displaced_work`` coordinate of every ``ReuseEventV1``.

``lazy_parent``  (PARENT)
    Acquires nothing eagerly and retains no evidence.  It counts demand: the
    second time a family forces a dynamic programme it induces the rule *from the
    table that dynamic programme just produced* and reuses it thereafter.  It
    therefore pays discovery only for structure that was actually demanded, and
    pays one extra derivation per demanded family.  This is the arm that
    dominated eager discovery in the E3 capability-gated re-analysis.

``index_parent``  (PARENT)
    The persistent arm with a plain family index and no dependency edges.  It is
    expected to match the machine exactly on every work coordinate and to hold
    strictly fewer index bytes, reproducing ``C1-SPARSE-LOOKUP``.

``cache_parent``  (PARENT)
    Solved instances rather than methods (protocol §6 ``A_cache``, and ``P1``
    persistent memoization).  It answers an exact repeat for one unit and must
    re-solve everything else, so it generalises at chance beyond its cached
    instances.  Its ``cache_extrapolation_accuracy`` coordinate measures that
    rather than asserting it.

``deferred_induction_parent``  (PARENT, added beyond the registered five)
    Retains the evidence a solve produced but defers *induction* until a family
    is demanded a second time, at which point it induces from the retained
    evidence and never pays the second dynamic programme at all.  It is the
    strongest parent this domain admits and it was added because protocol §7
    gives the strongest plausible alternative first right of refusal; leaving it
    out would have been the rigging the constitution's §11 forbids.  It shares
    the machine's mechanism entirely --- same store, same rules, same reuse ---
    and differs only in its acquisition trigger, so a loss to it is a result
    about *policy*, not about architecture, and is labelled as such.

Which parents share the mechanism
---------------------------------

``ROOT_CAUSE_ANALYSIS_V1``'s second deep root is
``COMPARISON_WAS_CONSTRUCTED_FROM_THE_ARM``: a parent that is the arm's own
algorithm holding separate state makes ``PARENT_SUFFICIENT`` true by construction
and carries no information.  Three of the parents here are in exactly that
position and say so before the run: ``index_parent``, ``lazy_parent`` and
``deferred_induction_parent`` all hold periodic rules in a persistent store and
differ from the machine only in retrieval structure or acquisition trigger.  The
independently-implemented parents are ``cache_parent`` (memoization, a different
architecture) and the ``reset_arm`` ablation.  Both crossovers are reported: one
against the strongest parent of any kind, one against the strongest independent
parent.

Accounting
----------

``rho.py`` and ``scaling.py`` share a ledger.  ``k`` is instrumented and never
inferred: it counts persistent objects a path actually touched through
``CompetenceStore.read``.  An uninstrumented path poisons the ledger, and
``record_from_ledger`` refuses to emit a number from a poisoned ledger, so a
favourable ``k`` is unreachable on that path by construction.

Four charged coordinates, reported separately and never weighted into a scalar
(CL-S-T4):

``discovery``    ``index_build_work``: induction plus the CL-D1(b) extrapolation
                 certification.
``maintenance``  ``index_maintenance_work``: store upkeep per method per task,
                 plus memo inserts.
``query``        ``query_work``: index probes, object reads, predicate
                 evaluations, search expansions and checker calls.
``checker``      ``checker_expansions``: the scorer's one call per task per arm.
                 It is identical across arms by construction and the sweep
                 asserts it, so the crossover is reported both with and without.

Parents: relational index structures; truth-maintenance systems (Doyle);
memoization and cache architectures; version-space induction (Mitchell); MDL
(Rissanen).  No novelty is claimed for any of them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from games import SubtractionGame
from methods import GrundyRule
from rho import (
    COMMITMENT,
    LANGUAGE,
    MAINTENANCE_PER_METHOD_PER_TASK,
    MEMO_INSERT_WORK,
    RHO_PLAN,
    Acquisition,
    StreamTask,
    Task,
    TaskStream,
    acquire_method,
    available_procedures,
    build_stream,
    check_verdict,
    procedure_cost,
    solve_by_closed_form,
    solve_by_dp,
    solve_by_rule,
)
from scaling import (
    INDEX_ENTRY_BYTES,
    SHARED_SUPPORT_ID,
    CheckStatus,
    CompetenceStore,
    ResourceRecord,
    TouchLedger,
    record_from_ledger,
)

__all__ = [
    "MethodIndex",
    "ArmSpec",
    "ARM_SPECS",
    "ARM_ROLES",
    "ReuseEvent",
    "RhoArm",
    "ArmRun",
    "run_arm",
    "run_cell",
    "sweep",
    "sweep_table",
    "crossovers",
    "SWEEP_NOTES",
]


# --------------------------------------------------------------------------
# the index, charged on insert
# --------------------------------------------------------------------------


class MethodIndex:
    """Family identity -> method object id, plus optional dependency edges.

    Built incrementally: nothing here scans the store, so no arm can look sparse
    by rebuilding a global index a moment before a query.  Every entry is charged
    once on insert as maintenance work and forever as index bytes.

    ``track_dependencies`` additionally records support -> dependent-method edges.
    They are counted in ``entries`` and therefore in ``bytes``, because a
    dependency map is persistent index state and a lane whose thesis is "charge
    the index" cannot leave its own index uncharged.  No revocation is exercised
    in E7, so those edges buy the machine nothing here and cost it bytes; that
    asymmetry is reported rather than removed.
    """

    def __init__(self, *, track_dependencies: bool) -> None:
        self.track_dependencies = track_dependencies
        self._by_family: dict[str, str] = {}
        self._memo: dict[tuple[str, tuple[int, ...]], str] = {}
        self._dependents: dict[str, list[str]] = {}

    # ---- methods --------------------------------------------------------

    def insert_method(
        self, family_id: str, object_id: str, supports: Sequence[str], ledger: TouchLedger
    ) -> None:
        self._by_family[family_id] = object_id
        ledger.index_maintenance_work += 1
        if self.track_dependencies:
            # The reverse edges are written by the same insert operation, so they
            # add index BYTES and no additional work.  This is deliberate and it
            # is what makes the index parent tie the machine exactly on every work
            # coordinate, reproducing C1-SPARSE-LOOKUP instead of manufacturing a
            # difference out of the machine's own bookkeeping.
            for support_id in supports:
                self._dependents.setdefault(support_id, []).append(object_id)

    def probe_method(self, family_id: str, ledger: TouchLedger) -> str | None:
        ledger.probe_index()
        return self._by_family.get(family_id)

    # ---- memo -----------------------------------------------------------

    def insert_memo(
        self, key: tuple[str, tuple[int, ...]], object_id: str, ledger: TouchLedger
    ) -> None:
        self._memo[key] = object_id
        ledger.index_maintenance_work += MEMO_INSERT_WORK

    def probe_memo(
        self, key: tuple[str, tuple[int, ...]], ledger: TouchLedger
    ) -> str | None:
        ledger.probe_index()
        return self._memo.get(key)

    # ---- reporting ------------------------------------------------------

    @property
    def method_entries(self) -> int:
        return len(self._by_family)

    @property
    def entries(self) -> int:
        return (
            len(self._by_family)
            + len(self._memo)
            + sum(len(v) for v in self._dependents.values())
        )

    @property
    def bytes(self) -> int:
        return self.entries * INDEX_ENTRY_BYTES


# --------------------------------------------------------------------------
# arm configuration
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ArmSpec:
    """One persistence policy, declared before the run.

    ``acquisition_trigger`` is the only field that separates the machine from two
    of its parents, which is the point: E7 varies the ecology, and the arms vary
    *when* structure is acquired, so the sweep answers "at what reuse density
    does eager acquisition pay" rather than "is persistence good".
    """

    arm_id: str
    role: str
    shares_mechanism: bool
    holds_methods: bool
    holds_memo: bool
    retains_evidence: bool
    tracks_dependencies: bool
    #: NONE | FIRST_DP_SOLVE | SECOND_DEMAND | SECOND_DEMAND_FROM_RETAINED_EVIDENCE
    acquisition_trigger: str
    note: str

    @property
    def persists(self) -> bool:
        return self.holds_methods or self.holds_memo or self.retains_evidence


ARM_SPECS: dict[str, ArmSpec] = {
    "persistent_arm": ArmSpec(
        arm_id="persistent_arm",
        role="ARM",
        shares_mechanism=False,
        holds_methods=True,
        holds_memo=True,
        retains_evidence=True,
        tracks_dependencies=True,
        acquisition_trigger="FIRST_DP_SOLVE",
        note="eager: acquires from every task it had to derive, demanded or not",
    ),
    "reset_arm": ArmSpec(
        arm_id="reset_arm",
        role="ABLATION",
        shares_mechanism=False,
        holds_methods=False,
        holds_memo=False,
        retains_evidence=False,
        tracks_dependencies=False,
        acquisition_trigger="NONE",
        note="persists nothing; supplies displaced_work for every reuse event",
    ),
    "lazy_parent": ArmSpec(
        arm_id="lazy_parent",
        role="PARENT",
        shares_mechanism=True,
        holds_methods=True,
        holds_memo=True,
        retains_evidence=False,
        tracks_dependencies=False,
        acquisition_trigger="SECOND_DEMAND",
        note="acquires nothing eagerly; re-derives on demand and induces only "
             "when a family has demanded derivation twice",
    ),
    "index_parent": ArmSpec(
        arm_id="index_parent",
        role="PARENT",
        shares_mechanism=True,
        holds_methods=True,
        holds_memo=True,
        retains_evidence=True,
        tracks_dependencies=False,
        acquisition_trigger="FIRST_DP_SOLVE",
        note="an ordinary index over acquired methods, no dependency tracking",
    ),
    "cache_parent": ArmSpec(
        arm_id="cache_parent",
        role="PARENT",
        shares_mechanism=False,
        holds_methods=False,
        holds_memo=True,
        retains_evidence=False,
        tracks_dependencies=False,
        acquisition_trigger="NONE",
        note="stores solved instances rather than methods; chance beyond them",
    ),
    "deferred_induction_parent": ArmSpec(
        arm_id="deferred_induction_parent",
        role="PARENT_STRONGEST_KNOWN",
        shares_mechanism=True,
        holds_methods=True,
        holds_memo=True,
        retains_evidence=True,
        tracks_dependencies=False,
        acquisition_trigger="SECOND_DEMAND_FROM_RETAINED_EVIDENCE",
        note="retains evidence eagerly, defers induction until demand is proven, "
             "and therefore never pays a second derivation",
    ),
}

ARM_ROLES: dict[str, str] = {k: v.role for k, v in ARM_SPECS.items()}

#: Parents whose comparison is informative because they do not hold the
#: machine's own mechanism.  Declared before the run.
INDEPENDENT_PARENTS: tuple[str, ...] = tuple(
    k for k, v in ARM_SPECS.items() if v.role.startswith("PARENT") and not v.shares_mechanism
)
ALL_PARENTS: tuple[str, ...] = tuple(
    k for k, v in ARM_SPECS.items() if v.role.startswith("PARENT")
)


# --------------------------------------------------------------------------
# CL-R3: the only admissible witness of causal use
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ReuseEvent:
    """One witnessed invocation of an acquired method.

    Presence in memory is not use and similarity is not reuse.  An endpoint may
    cite a method only when a record like this exists with a non-empty
    ``execution_trace``.  ``displaced_work`` is measured, not estimated: it is the
    work the matched ablation actually spent on the same ``task_id``.
    """

    reuse_id: str
    method_id: str
    task_id: str
    arm_id: str
    applicability_witness: str
    execution_trace: tuple[str, ...]
    work_with: int
    displaced_work: int
    certified_essential: bool

    def __post_init__(self) -> None:
        if not self.execution_trace:
            raise ValueError("a reuse event without an execution trace is inadmissible")

    def as_dict(self) -> dict:
        return {
            "reuse_id": self.reuse_id,
            "method_id": self.method_id,
            "task_id": self.task_id,
            "arm_id": self.arm_id,
            "applicability_witness": self.applicability_witness,
            "execution_trace": list(self.execution_trace),
            "work_with": self.work_with,
            "displaced_work": self.displaced_work,
            "certified_essential": self.certified_essential,
        }


# --------------------------------------------------------------------------
# one arm over one stream
# --------------------------------------------------------------------------


class RhoArm:
    """One persistence policy, installed once and run over the whole stream.

    Subclassing is deliberately avoided.  Every arm is this class configured by an
    :class:`ArmSpec`, so the retrieval path, the charging, the checker call and
    the record construction are shared byte for byte and any difference in the
    reported numbers has to come from the declared policy flags.
    """

    def __init__(
        self,
        spec: ArmSpec,
        *,
        discovery_multiplier: int = 1,
        displaced: Mapping[str, int] | None = None,
    ) -> None:
        self.spec = spec
        self.arm_id = spec.arm_id
        self.discovery_multiplier = discovery_multiplier
        self.displaced = dict(displaced or {})
        self.store = CompetenceStore(f"rho:{spec.arm_id}")
        self.index = MethodIndex(track_dependencies=spec.tracks_dependencies)
        self.rules: dict[str, GrundyRule] = {}
        self.acquisitions: dict[str, Acquisition] = {}
        self.evidence_supports: dict[str, str] = {}
        self.derivations: dict[str, int] = {}
        self.reuse_events: list[ReuseEvent] = []
        self.records: list[ResourceRecord] = []
        self.procedure_counts: dict[str, int] = {}
        self.answered = 0
        self.correct = 0
        self.cache_extrapolation_attempts = 0
        self.cache_extrapolation_correct = 0
        self.cache_extrapolation_p_positions = 0
        if spec.holds_methods or spec.retains_evidence:
            self.store.add_support(
                SHARED_SUPPORT_ID,
                "*SHARED*",
                {
                    "kind": "lemma",
                    "statement": "every finite subtraction game has an eventually "
                                 "periodic Grundy sequence",
                    "parent": "Sprague-Grundy theory",
                },
                relation="shared",
            )

    # ---- reporting surface ---------------------------------------------

    @property
    def index_bytes(self) -> int:
        return self.index.bytes

    @property
    def persistent_bytes(self) -> int:
        return self.store.store_bytes + self.index_bytes

    def _record(self, ledger: TouchLedger, *, operation: str, thermal: str,
                outcome: str, correct: bool | None) -> ResourceRecord:
        return record_from_ledger(
            ledger,
            arm_id=self.arm_id,
            scale_id=f"rho-stream",
            operation=operation,
            thermal_state=thermal,
            n_objects=self.store.n_objects,
            store_bytes=self.store.store_bytes,
            index_bytes=self.index_bytes,
            lifetime_index_build_work=0,
            lifetime_index_maintenance_work=0,
            outcome=outcome,
            verdict_correct=correct,
        )

    # ---- persistence primitives ----------------------------------------

    def _retain_evidence(self, task: Task, ledger: TouchLedger) -> str:
        """Persist the Grundy observations a derivation produced.

        Charged in bytes always and in maintenance once.  An arm that retains
        evidence has acquired *something* eagerly, and the receipt says so.
        """
        support_id = f"S:{task.family_id}:b0"
        if task.family_id in self.evidence_supports:
            return support_id
        table, _ = _evidence_table(task.moves)
        self.store.add_support(
            support_id,
            task.family_id,
            {
                "kind": "evidence_block",
                "family": task.family_id,
                "observations": [[n, g] for n, g in table],
            },
        )
        self.evidence_supports[task.family_id] = support_id
        ledger.index_maintenance_work += 1
        return support_id

    def _acquire(self, task: Task, ledger: TouchLedger) -> bool:
        """Induce, certify and persist a rule for ``task``'s family.

        Returns whether an admissible method was stored.  An inadmissible method
        may be stored but is never counted and never reused (CL-D1).
        """
        if task.family_id in self.rules:
            return True
        acquisition = acquire_method(
            task.moves, ledger, discovery_multiplier=self.discovery_multiplier
        )
        support_id = self._retain_evidence(task, ledger)
        supports = (support_id, SHARED_SUPPORT_ID)
        if not acquisition.admissible:  # pragma: no cover -- filter guarantees it
            return False
        method_id = self.store.add_competence(
            task.family_id, acquisition.rule, supports, relation="probe"
        )
        self.index.insert_method(task.family_id, method_id, supports, ledger)
        self.rules[task.family_id] = acquisition.rule
        self.acquisitions[task.family_id] = acquisition
        return True

    def _memo_id(self, task: Task) -> str:
        return "MEMO:" + task.family_id + ":" + ",".join(str(p) for p in task.positions)

    def _insert_memo(self, task: Task, verdict: bool, ledger: TouchLedger) -> None:
        """Persist one solved instance.  Every persisting arm does this identically.

        The memo is the reason a repeated task is never certified essential: it is
        the registered ``P_MEMO`` bypass made real, and because all four persisting
        arms hold the same memo it contributes an identical term to each of them
        and cancels out of every comparison between them.
        """
        object_id = self._memo_id(task)
        if task.key in self.index._memo:
            return
        self.store.add_support(
            object_id,
            task.family_id,
            {
                "kind": "solved_instance",
                "family": task.family_id,
                "positions": list(task.positions),
                "is_p": verdict,
            },
            relation="memo",
        )
        self.index.insert_memo(task.key, object_id, ledger)

    # ---- the task loop --------------------------------------------------

    def _needs_derivation(self, task: Task) -> bool:
        """True when nothing this arm holds can answer ``task`` except ``P_DP``."""
        if task.modulus is not None:
            return False
        if self.spec.holds_memo and task.key in self.index._memo:
            return False
        if self.spec.holds_methods and task.family_id in self.rules:
            return False
        return True

    def _choose(self, task: Task) -> str:
        """The cheapest available registered procedure, frozen tie-break.

        The choice is made on *certified* procedure cost, identical for every arm,
        so an arm cannot manufacture a reuse event by preferring its own machinery
        when something cheaper was available to it.
        """
        method_available = self.spec.holds_methods and task.family_id in self.rules
        memo_available = self.spec.holds_memo and task.key in self.index._memo
        order = {name: i for i, name in enumerate(RHO_PLAN["procedure_preference"])}
        best: tuple[int, int, str] | None = None
        for name in available_procedures(
            task, method_available=method_available, memo_available=memo_available
        ):
            candidate = (procedure_cost(task, name), order[name], name)
            if best is None or candidate < best:
                best = candidate
        assert best is not None
        return best[2]

    def handle(self, stream_task: StreamTask) -> ResourceRecord:
        """Answer one task, acquire whatever the policy says, pay for all of it."""
        task = stream_task.task
        ledger = TouchLedger()
        thermal = "COLD" if not self.records else "WARM"

        # deferred induction fires BEFORE the answer: an arm that retained the
        # evidence can induce now and skip the second derivation entirely.
        if (
            self.spec.acquisition_trigger == "SECOND_DEMAND_FROM_RETAINED_EVIDENCE"
            and self._needs_derivation(task)
            and task.family_id in self.evidence_supports
        ):
            self._acquire(task, ledger)

        procedure = self._choose(task)
        self.procedure_counts[procedure] = self.procedure_counts.get(procedure, 0) + 1

        if procedure == "P_CLOSED_FORM":
            verdict = solve_by_closed_form(task, ledger)
            outcome = "ANSWERED_CLOSED_FORM"
        elif procedure == "P_MEMO":
            object_id = self.index.probe_memo(task.key, ledger)
            assert object_id is not None
            entry = self.store.read(object_id, ledger)
            ledger.predicate_evaluations += 1
            verdict = bool(entry.payload["is_p"])
            outcome = "ANSWERED_MEMO"
        elif procedure == "P_RULE":
            method_id = self.index.probe_method(task.family_id, ledger)
            assert method_id is not None
            method = self.store.read(method_id, ledger)
            rule = _rule_of(method)
            verdict, trace = solve_by_rule(task, rule, ledger)
            outcome = "ANSWERED_REUSE"
            self.reuse_events.append(
                ReuseEvent(
                    reuse_id=f"{self.arm_id}:{task.task_id}",
                    method_id=method_id,
                    task_id=task.task_id,
                    arm_id=self.arm_id,
                    applicability_witness=(
                        f"index probe on family {task.family_id} returned {method_id}; "
                        f"scope covers positions {list(task.positions)}"
                    ),
                    execution_trace=trace,
                    work_with=ledger.query_work,
                    displaced_work=self.displaced.get(task.task_id, 0),
                    certified_essential=stream_task.certified_essential,
                )
            )
        else:
            verdict = solve_by_dp(task, ledger)
            outcome = "ANSWERED_DERIVED"
            self.derivations[task.family_id] = self.derivations.get(task.family_id, 0) + 1
            if task.modulus is None:
                if self.spec.acquisition_trigger == "FIRST_DP_SOLVE":
                    self._acquire(task, ledger)
                elif self.spec.acquisition_trigger == "SECOND_DEMAND" and (
                    self.derivations[task.family_id] >= 2
                ):
                    self._acquire(task, ledger)
                elif (
                    self.spec.acquisition_trigger
                    == "SECOND_DEMAND_FROM_RETAINED_EVIDENCE"
                ):
                    # evidence is retained eagerly, induction is not
                    self._retain_evidence(task, ledger)

        # The cache diagnostic is taken BEFORE this task enters the memo.  Taking
        # it afterwards would let the guess find the task's own answer at distance
        # zero and score a perfect one, which is not generalisation, it is reading
        # the row that was written a line earlier.
        cache_guess = (
            self._nearest_cached_guess(task)
            if self.spec.arm_id == "cache_parent" and procedure != "P_MEMO"
            else None
        )

        if self.spec.holds_memo:
            self._insert_memo(task, verdict, ledger)

        # store upkeep, charged every task on every arm that holds methods
        if self.spec.holds_methods and self.rules:
            ledger.index_maintenance_work += (
                MAINTENANCE_PER_METHOD_PER_TASK * len(self.rules)
            )

        truth = check_verdict(task, ledger)
        correct = verdict == truth
        self.answered += 1
        self.correct += int(correct)

        # cache_parent's generalisation diagnostic: what a nearest-cached-instance
        # guess WOULD have said on a miss.  Measured, never used to answer.
        if cache_guess is not None:
            self.cache_extrapolation_attempts += 1
            self.cache_extrapolation_correct += int(cache_guess == truth)
            self.cache_extrapolation_p_positions += int(truth)

        record = self._record(
            ledger, operation="TASK", thermal=thermal, outcome=outcome, correct=correct
        )
        self.records.append(record)
        return record

    def _nearest_cached_guess(self, task: Task) -> bool | None:
        """The verdict a nearest-cached-instance heuristic would return.

        Diagnostic only: it never answers a task and never enters the ledger.  It
        exists so that "a cache generalises at chance beyond its cached instances"
        is a measured number in the receipt rather than a claim in a docstring.
        """
        best: tuple[int, bool] | None = None
        for (family_id, positions), object_id in self.index._memo.items():
            if family_id != task.family_id or len(positions) != len(task.positions):
                continue
            distance = sum(abs(a - b) for a, b in zip(positions, task.positions))
            payload = self.store._objects[object_id].payload
            candidate = (distance, bool(payload["is_p"]))
            if best is None or candidate < best:
                best = candidate
        return None if best is None else best[1]


def _rule_of(obj) -> GrundyRule:
    """Rebuild a periodic rule from a stored payload.

    The store persists rules as plain data, never as live objects, which is what a
    real restart hands back.  Rebuilding here rather than holding a Python
    reference keeps every arm honest about what crossed the persistence boundary.
    """
    return GrundyRule(
        preperiod=int(obj.payload["preperiod"]),
        period=int(obj.payload["period"]),
        values=tuple(int(v) for v in obj.payload["values"]),
    )


def _evidence_table(moves: tuple[int, ...]) -> tuple[tuple[tuple[int, int], ...], int]:
    """The frozen evidence window ``[(n, G(n))]`` for one family.

    It is the by-product of the derivation that produced it, so retaining it costs
    bytes and one maintenance unit but no search: an arm that has just run the
    dynamic programme already holds these numbers.
    """
    from rho import EVIDENCE_WINDOW, grundy_table

    table, work = grundy_table(moves, EVIDENCE_WINDOW - 1)
    return tuple((n, table[n]) for n in range(EVIDENCE_WINDOW)), work


# --------------------------------------------------------------------------
# one cell of the sweep
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ArmRun:
    """Everything one arm did over one stream at one discovery cost."""

    arm_id: str
    role: str
    shares_mechanism: bool
    requested_rho: float
    realised_rho: float
    discovery_multiplier: int
    tasks: int
    answered: int
    correct: int
    discovery_work: int
    maintenance_work: int
    query_work: int
    checker_expansions: int
    persistent_bytes: int
    store_bytes: int
    index_bytes: int
    n_objects: int
    methods_acquired: int
    max_k: int | None
    total_k: int | None
    k_status: str
    reuse_invocations: int
    essential_reuse_invocations: int
    reuse_displaced_work: int
    procedure_counts: Mapping[str, int]
    cache_extrapolation_attempts: int
    cache_extrapolation_correct: int
    cache_extrapolation_p_positions: int

    @property
    def capability(self) -> float:
        return self.correct / self.tasks if self.tasks else 0.0

    @property
    def charged_total_work(self) -> int:
        """Discovery + maintenance + query.  The headline cumulative cost.

        The scorer's checker call is excluded here and reported beside it, for the
        reason ``scaling.py`` gives: it is an identical constant on every arm, so
        including it adds the same number to every row and compresses the very
        contrast the sweep is about.  The sweep asserts that it really is
        identical, and the crossover is computed both ways.
        """
        return self.discovery_work + self.maintenance_work + self.query_work

    @property
    def charged_total_with_checker(self) -> int:
        return self.charged_total_work + self.checker_expansions

    @property
    def cache_extrapolation_accuracy(self) -> float | None:
        if not self.cache_extrapolation_attempts:
            return None
        return self.cache_extrapolation_correct / self.cache_extrapolation_attempts

    @property
    def cache_extrapolation_majority_baseline(self) -> float | None:
        """The accuracy of always answering the commoner class.

        "Generalises at chance" is meaningless against 0.5 when P-positions are
        rare, and a cache that answers "not a P-position" every time would score
        well against the wrong yardstick.  The honest comparison is the
        majority-class baseline on the very tasks the cache missed, so it is
        computed and reported next to the accuracy rather than left implicit.
        """
        n = self.cache_extrapolation_attempts
        if not n:
            return None
        p = self.cache_extrapolation_p_positions
        return max(p, n - p) / n

    @property
    def cache_extrapolation_lift(self) -> float | None:
        """Accuracy minus the majority baseline.  Zero or below means chance."""
        if self.cache_extrapolation_accuracy is None:
            return None
        return self.cache_extrapolation_accuracy - self.cache_extrapolation_majority_baseline

    def as_row(self) -> dict:
        return {
            "arm": self.arm_id,
            "role": self.role,
            "shares_mechanism": self.shares_mechanism,
            "requested_rho": self.requested_rho,
            "realised_rho": round(self.realised_rho, 6),
            "discovery_multiplier": self.discovery_multiplier,
            "tasks": self.tasks,
            "capability": round(self.capability, 6),
            "discovery_work": self.discovery_work,
            "maintenance_work": self.maintenance_work,
            "query_work": self.query_work,
            "charged_total_work": self.charged_total_work,
            "scoring_checker_expansions": self.checker_expansions,
            "charged_total_with_checker": self.charged_total_with_checker,
            "persistent_bytes": self.persistent_bytes,
            "store_bytes": self.store_bytes,
            "index_bytes": self.index_bytes,
            "N_persistent_objects": self.n_objects,
            "methods_acquired": self.methods_acquired,
            "max_k": self.max_k,
            "k_status": self.k_status,
            "reuse_invocations": self.reuse_invocations,
            "essential_reuse_invocations": self.essential_reuse_invocations,
            "reuse_displaced_work": self.reuse_displaced_work,
            "procedure_counts": dict(sorted(self.procedure_counts.items())),
            "cache_extrapolation_attempts": self.cache_extrapolation_attempts,
            "cache_extrapolation_accuracy": (
                None
                if self.cache_extrapolation_accuracy is None
                else round(self.cache_extrapolation_accuracy, 6)
            ),
            "cache_extrapolation_majority_baseline": (
                None
                if self.cache_extrapolation_majority_baseline is None
                else round(self.cache_extrapolation_majority_baseline, 6)
            ),
            "cache_extrapolation_lift_over_majority": (
                None
                if self.cache_extrapolation_lift is None
                else round(self.cache_extrapolation_lift, 6)
            ),
        }


def run_arm(
    arm_id: str,
    stream: TaskStream,
    *,
    discovery_multiplier: int = 1,
    displaced: Mapping[str, int] | None = None,
) -> tuple[ArmRun, RhoArm]:
    """Run one arm over the whole stream and aggregate its per-task records."""
    spec = ARM_SPECS[arm_id]
    arm = RhoArm(spec, discovery_multiplier=discovery_multiplier, displaced=displaced)
    for stream_task in stream.tasks:
        arm.handle(stream_task)

    poisoned = any(r.k_status is CheckStatus.CANNOT_CHECK for r in arm.records)
    ks = [r.k for r in arm.records if r.k is not None]
    run = ArmRun(
        arm_id=arm_id,
        role=spec.role,
        shares_mechanism=spec.shares_mechanism,
        requested_rho=stream.requested_rho,
        realised_rho=stream.realised_rho,
        discovery_multiplier=discovery_multiplier,
        tasks=len(stream.tasks),
        answered=arm.answered,
        correct=arm.correct,
        discovery_work=sum(r.index_build_work for r in arm.records),
        maintenance_work=sum(r.index_maintenance_work for r in arm.records),
        query_work=sum(r.query_work for r in arm.records),
        checker_expansions=sum(r.checker_expansions for r in arm.records),
        persistent_bytes=arm.persistent_bytes,
        store_bytes=arm.store.store_bytes,
        index_bytes=arm.index_bytes,
        n_objects=arm.store.n_objects,
        methods_acquired=len(arm.rules),
        max_k=None if poisoned else (max(ks) if ks else 0),
        total_k=None if poisoned else sum(ks),
        k_status="CANNOT_CHECK" if poisoned else "MEASURED",
        reuse_invocations=len(arm.reuse_events),
        essential_reuse_invocations=sum(
            1 for e in arm.reuse_events if e.certified_essential
        ),
        reuse_displaced_work=sum(e.displaced_work for e in arm.reuse_events),
        procedure_counts=dict(arm.procedure_counts),
        cache_extrapolation_attempts=arm.cache_extrapolation_attempts,
        cache_extrapolation_correct=arm.cache_extrapolation_correct,
        cache_extrapolation_p_positions=arm.cache_extrapolation_p_positions,
    )
    return run, arm


def run_cell(
    requested_rho: float, *, discovery_multiplier: int = 1
) -> dict[str, tuple[ArmRun, RhoArm]]:
    """Every arm over one stream.  Anti-rigging control 2 lives here.

    Every parent runs at every ``rho`` on the identical stream, because a parent
    that was denied the reuse opportunity the machine was given is not a parent,
    it is a handicap.  The ablation runs first so that every ``ReuseEventV1`` can
    carry a ``displaced_work`` that was measured on the same ``task_id`` rather
    than estimated.
    """
    stream = build_stream(requested_rho)
    ablation, ablation_arm = run_arm(
        "reset_arm", stream, discovery_multiplier=discovery_multiplier
    )
    displaced = {
        st.task.task_id: rec.query_work
        for st, rec in zip(stream.tasks, ablation_arm.records)
    }
    out: dict[str, tuple[ArmRun, RhoArm]] = {"reset_arm": (ablation, ablation_arm)}
    for arm_id in RHO_PLAN["arms"]:
        if arm_id == "reset_arm":
            continue
        out[arm_id] = run_arm(
            arm_id,
            stream,
            discovery_multiplier=discovery_multiplier,
            displaced=displaced,
        )
    return out


def sweep(
    rho_grid: Sequence[float] | None = None,
    multipliers: Sequence[int] | None = None,
) -> dict[tuple[int, float], dict[str, tuple[ArmRun, RhoArm]]]:
    """The whole registered sweep: every arm at every rho at every discovery cost."""
    grid = list(rho_grid if rho_grid is not None else RHO_PLAN["rho_grid"])
    mults = list(
        multipliers if multipliers is not None else RHO_PLAN["discovery_cost_multipliers"]
    )
    return {
        (m, r): run_cell(r, discovery_multiplier=m) for m in mults for r in grid
    }


def sweep_table(
    results: Mapping[tuple[int, float], Mapping[str, tuple[ArmRun, RhoArm]]]
) -> list[dict]:
    """The reported object: the entire curve, never a single favourable rho."""
    rows: list[dict] = []
    for (multiplier, requested), cell in sorted(results.items()):
        for arm_id in RHO_PLAN["arms"]:
            rows.append(cell[arm_id][0].as_row())
    return rows


# --------------------------------------------------------------------------
# the crossover: the second half of the reported object
# --------------------------------------------------------------------------


def _totals(rows: Sequence[Mapping], multiplier: int, key: str) -> dict[float, dict[str, int]]:
    out: dict[float, dict[str, int]] = {}
    for row in rows:
        if row["discovery_multiplier"] != multiplier:
            continue
        out.setdefault(row["requested_rho"], {})[row["arm"]] = row[key]
    return out


def crossovers(
    rows: Sequence[Mapping], *, key: str = "charged_total_work"
) -> dict[str, Any]:
    """Where the machine's cumulative cost falls below each parent's, if anywhere.

    Reported for every parent separately, for the envelope of all parents, and for
    the envelope of the *independent* parents.  The envelope is the honest object:
    a crossover against one chosen parent while another parent still wins is not a
    crossover, it is parent shopping.

    ``first_rho_below`` is the smallest grid point where the machine is strictly
    cheaper; ``stays_below`` says whether it remains so at every larger grid point.
    A crossover that does not persist is reported as not persisting rather than
    quietly headlined.
    """
    out: dict[str, Any] = {}
    for multiplier in sorted({row["discovery_multiplier"] for row in rows}):
        totals = _totals(rows, multiplier, key)
        grid = sorted(totals)
        per_parent: dict[str, Any] = {}
        targets: dict[str, Callable[[dict[str, int]], int]] = {
            **{p: (lambda t, p=p: t[p]) for p in ALL_PARENTS},
            "STRONGEST_PARENT_ENVELOPE": lambda t: min(t[p] for p in ALL_PARENTS),
            "STRONGEST_INDEPENDENT_PARENT_ENVELOPE": lambda t: min(
                t[p] for p in INDEPENDENT_PARENTS
            ),
        }
        for name, pick in targets.items():
            below = [r for r in grid if totals[r]["persistent_arm"] < pick(totals[r])]
            first = below[0] if below else None
            stays = bool(
                first is not None
                and all(
                    totals[r]["persistent_arm"] < pick(totals[r])
                    for r in grid
                    if r >= first
                )
            )
            per_parent[name] = {
                "first_rho_below": first,
                "stays_below_at_every_larger_rho": stays,
                "machine_minus_target_by_rho": {
                    str(r): totals[r]["persistent_arm"] - pick(totals[r]) for r in grid
                },
            }
        out[str(multiplier)] = per_parent
    return out


def rho_zero_reproduces_negatives(rows: Sequence[Mapping]) -> dict[str, Any]:
    """Anti-rigging control 1, evaluated exactly.

    At ``rho = 0`` the machine must show no advantage and the index and lazy
    parents must match or beat it, consistent with ``SCALING_PILOT_V1.json`` and
    the E3 capability-gated re-analysis.  If they do not, the knob is not the one
    the old experiments varied and the whole sweep is void.
    """
    out: dict[str, Any] = {}
    for multiplier in sorted({row["discovery_multiplier"] for row in rows}):
        at_zero = {
            row["arm"]: row
            for row in rows
            if row["discovery_multiplier"] == multiplier and row["requested_rho"] == 0.0
        }
        if not at_zero:
            out[str(multiplier)] = {"reproduced": False, "reason": "rho=0 not in the grid"}
            continue
        machine = at_zero["persistent_arm"]["charged_total_work"]
        checks = {
            "lazy_parent_matches_or_beats_machine": at_zero["lazy_parent"][
                "charged_total_work"
            ]
            <= machine,
            "index_parent_matches_or_beats_machine": at_zero["index_parent"][
                "charged_total_work"
            ]
            <= machine,
            "machine_has_no_advantage_over_any_parent": all(
                at_zero[p]["charged_total_work"] <= machine for p in ALL_PARENTS
            ),
            "no_essential_reuse_at_rho_zero": at_zero["persistent_arm"][
                "essential_reuse_invocations"
            ]
            == 0,
            "realised_rho_is_zero": at_zero["persistent_arm"]["realised_rho"] == 0.0,
        }
        out[str(multiplier)] = {
            "reproduced": all(checks.values()),
            "checks": checks,
            "machine_charged_total_work": machine,
            "parent_charged_total_work": {
                p: at_zero[p]["charged_total_work"] for p in ALL_PARENTS
            },
        }
    return out


def controls(rows: Sequence[Mapping]) -> dict[str, Any]:
    """The three anti-rigging controls plus the capability gate, all computed."""
    grid = sorted({row["requested_rho"] for row in rows})
    mults = sorted({row["discovery_multiplier"] for row in rows})
    ran = {
        (row["discovery_multiplier"], row["requested_rho"], row["arm"]) for row in rows
    }
    every_parent_everywhere = all(
        (m, r, arm) in ran for m in mults for r in grid for arm in RHO_PLAN["arms"]
    )
    checker_constant = True
    for m in mults:
        for r in grid:
            vals = {
                row["scoring_checker_expansions"]
                for row in rows
                if row["discovery_multiplier"] == m and row["requested_rho"] == r
            }
            checker_constant = checker_constant and len(vals) == 1
    return {
        "control_1_rho_zero_reproduces_negatives": rho_zero_reproduces_negatives(rows),
        "control_2_every_parent_ran_at_every_rho": every_parent_everywhere,
        "control_3_reported_object_is_the_whole_curve": {
            "rho_grid": grid,
            "rows": len(rows),
            "single_favourable_rho_reported": False,
        },
        "capability_gate_passed": all(row["capability"] == 1.0 for row in rows),
        "capability_by_arm": {
            arm: sorted({row["capability"] for row in rows if row["arm"] == arm})
            for arm in RHO_PLAN["arms"]
        },
        "scoring_checker_identical_across_arms": checker_constant,
    }


SWEEP_NOTES: tuple[str, ...] = (
    "rho is the ONLY knob. The family pool, the eight donor tasks, the horizon of "
    "64 tasks, the position band, the checker, the budgets and every arm's policy "
    "are identical at every point of the sweep, so discovery cost is a constant "
    "across the curve and all variation is in the demand term.",
    "REALISED rho is always below REQUESTED rho, and the gap is not noise: the "
    "donor tasks that make any structure acquirable at all can never themselves "
    "be essential, so a 64-task stream with 8 donors cannot exceed a realised rho "
    "of 0.875 however the knob is set. The receipt reports both.",
    "A BYPASS_REPEAT task sits on an irregular family hundreds of positions beyond "
    "the training support, where the dynamic programme costs thousands of units "
    "and the acquired rule costs one. It is still certified NOT essential, because "
    "a solved-instance store answers it for the same one unit. That exclusion is "
    "the whole reason rho is not a synonym for 'tasks we made easy for ourselves'.",
    "Every arm that persists anything holds the identical solved-instance memo, so "
    "the memo contributes the same term to each of them and cancels out of every "
    "comparison between them. No arm's advantage can come from the bypass.",
    "The persistent arm and the index parent are expected to TIE on every work "
    "coordinate and to differ only in index bytes, reproducing C1-SPARSE-LOOKUP. "
    "A tie with a parent that holds the machine's own mechanism carries no "
    "information about the architecture and is not read as a result.",
    "deferred_induction_parent is a sixth arm, added beyond the five the decisive "
    "experiment registered, because protocol section 7 gives the strongest "
    "plausible alternative first right of refusal. Omitting a parent that was "
    "obviously available would have been the rigging that constitution section 11 "
    "forbids. It shares the machine's mechanism and its comparison is labelled.",
    "No revocation is exercised in E7, so the machine's dependency edges buy it "
    "nothing here and cost it index bytes. That is charged, not hidden, and it is "
    "why persistent_bytes is reported next to every work coordinate.",
    "Work coordinates are never weighted into a scalar (CL-S-T4). Bytes are "
    "reported separately and are never converted into work.",
)
