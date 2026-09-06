"""The canonical solve loop (M2 §5) over the M1 KSO core.

    Task/Query → atomise/ground → select representation → seed/navigate → warranted + exploratory
    activation → extract reacting subspace → retrieve/compose candidate operators → execute/simulate
    (registered backends only) → check → decide → commitment gate

Every stage returns a structured ``StageResult`` (never a raw string) with status
PASS | FAIL | CANNOT_CHECK | PROPOSAL and a resource delta.  ``CANNOT_CHECK`` propagates: a
downstream stage may not convert it into success, and the commitment gate refuses.  The solver
reads the store and never writes to it (architecture C2); candidates it produces enter the store
only through admission/composition performed by the runtime under its authority boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

from ocm.kso import abstraction as AB
from ocm.kso import admission as AD
from ocm.kso import extraction as EX
from ocm.kso import extraction_indexed as EXI
from ocm.kso.extraction_index import ExtractionIndex
from ocm.kso import firing as FI
from ocm.kso import navigation as N
from ocm.kso import surprise as SP
from ocm.kso.resources import ResourceVector
from ocm.kso.space import KnowledgeSpace, TypedRejection
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import CannotCheck, Liveness, WarrantProfile
from .operator_index import SolveOperatorIndex


class Status(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"
    PROPOSAL = "PROPOSAL"


class Stage(str, Enum):
    TASK = "TASK"
    GROUNDING = "GROUNDING"
    REPRESENTATION = "REPRESENTATION"
    NAVIGATION = "NAVIGATION"
    EXTRACTION = "EXTRACTION"
    COMPOSITION = "COMPOSITION"
    EXECUTION = "EXECUTION"
    CHECK = "CHECK"
    DECISION = "DECISION"
    COMMITMENT = "COMMITMENT"


class Decision(str, Enum):
    ANSWER = "ANSWER"
    ACT = "ACT"
    LEARN = "LEARN"
    CLARIFY = "CLARIFY"
    UNKNOWN = "UNKNOWN"
    JUMP_PROPOSAL = "JUMP_PROPOSAL"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class StageResult:
    stage: Stage
    status: Status
    reason: str
    object_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    payload: Mapping[str, Any] = field(default_factory=dict)
    resources: ResourceVector = field(default_factory=ResourceVector)

    def as_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "status": self.status.value,
            "reason": self.reason,
            "object_ids": list(self.object_ids),
            "evidence_ids": list(self.evidence_ids),
            "payload": {k: (str(v) if isinstance(v, Fraction) else v) for k, v in self.payload.items()},
            "resources": self.resources.as_dict(),
        }


@dataclass(frozen=True)
class QueryPart:
    """One atomised part of a task: typed, bound to existing atoms (contract §28)."""

    text: str
    atom_type: str
    refs: tuple[str, ...]


@dataclass(frozen=True)
class Task:
    task_id: str
    parts: tuple[QueryPart, ...]
    targets: tuple[str, ...] = ()          # atoms the task must reach (empty = open)
    context: str | None = None             # scope context the answer must cover
    required_authority: Authority = field(default_factory=Authority)
    identification_required: bool = False
    at: float | None = None                # evaluation time for epoch-bounded scopes (theory batch 8 H1: an epoch-bounded
                                           # scope may not be read as current on context alone)


@dataclass(frozen=True)
class SolveConfig:
    alpha: Fraction = Fraction(1, 3)
    threshold: Fraction = Fraction(1, 1000)
    budget: N.NavigationBudget = N.NavigationBudget(steps=24, restarts=1, depth=24)
    relevance: N.Relevance = None
    exact_extraction_max_atoms: int = 12
    firing_threshold: Fraction = Fraction(1, 1000)
    surprise_model: SP.SurpriseModel = SP.SurpriseModel.UNIFORM


@dataclass
class SolveTrace:
    task_id: str
    stages: list[StageResult] = field(default_factory=list)

    def add(self, r: StageResult) -> StageResult:
        self.stages.append(r)
        return r

    @property
    def resources(self) -> ResourceVector:
        total = ResourceVector()
        for s in self.stages:
            total = total + s.resources
        return total

    @property
    def worst_status(self) -> Status:
        order = {Status.PASS: 0, Status.PROPOSAL: 1, Status.CANNOT_CHECK: 2, Status.FAIL: 3}
        return max((s.status for s in self.stages), key=lambda s: order[s], default=Status.PASS)

    def as_dict(self) -> dict[str, Any]:
        return {"task_id": self.task_id, "stages": [s.as_dict() for s in self.stages], "resources": self.resources.as_dict(), "worst_status": self.worst_status.value}


# ---------------------------------------------------------------------------------------------
# stages
# ---------------------------------------------------------------------------------------------


def atomise(ks: KnowledgeSpace, task: Task) -> tuple[StageResult, list[Fraction] | None]:
    if not task.parts:
        return StageResult(Stage.GROUNDING, Status.FAIL, "EMPTY_QUESTION"), None
    known = set(ks.ids)
    mass: dict[str, Fraction] = {}
    for i, part in enumerate(task.parts):
        if not part.atom_type.strip() or not part.text.strip():
            return StageResult(Stage.GROUNDING, Status.FAIL, "NON_ATOMIC_INPUT", payload={"part": i}), None
        if not part.refs or any(r not in known for r in part.refs):
            return StageResult(Stage.GROUNDING, Status.FAIL, "UNBOUND_SEED", payload={"part": i, "refs": list(part.refs)}), None
        for r in part.refs:
            mass[r] = mass.get(r, Fraction(0, 1)) + Fraction(1, len(part.refs))
    seed = N.seed_vector(ks, mass)
    support = tuple(sorted(mass))
    return StageResult(Stage.GROUNDING, Status.PASS, "SEEDS_BOUND", object_ids=support, payload={"parts": len(task.parts), "seed_support": list(support)}), seed


def navigate_stage(ks: KnowledgeSpace, seed: Sequence[Fraction], task: Task, cfg: SolveConfig, revoked: Iterable[Hashable]) -> tuple[StageResult, dict[str, Any]]:
    rv = frozenset(revoked)
    try:
        act_w = N.fixed_point(ks, seed, cfg.alpha, revoked=rv, relevance=cfg.relevance)
        act_x = N.fixed_point(ks, seed, cfg.alpha, revoked=rv, relevance=cfg.relevance, mode=N.NavigationMode.EXPLORATORY)
        background = N.fixed_point(ks, N.uniform_seed(ks), cfg.alpha, revoked=rv, relevance=cfg.relevance)
        background_x = N.fixed_point(ks, N.uniform_seed(ks), cfg.alpha, revoked=rv, relevance=cfg.relevance, mode=N.NavigationMode.EXPLORATORY)
    except CannotCheck as exc:
        return StageResult(Stage.NAVIGATION, Status.CANNOT_CHECK, str(exc)), {}
    n = len(ks.ids)
    res = ResourceVector(navigation_work=4 * n * n)
    outcomes: dict[str, N.NavigationResult] = {}
    witness: N.ObstructionWitness | None = None
    worst = Status.PASS
    reason = "ACTIVATION_COMPUTED"
    for t in task.targets:
        try:
            r = N.navigate(ks, seed, t, cfg.budget, alpha=cfg.alpha, threshold=cfg.threshold, revoked=rv, relevance=cfg.relevance)
        except CannotCheck as exc:
            return StageResult(Stage.NAVIGATION, Status.CANNOT_CHECK, str(exc)), {}
        outcomes[t] = r
        res = res + r.resources
        if r.outcome is N.NavigationOutcome.OBSTRUCTION_WITNESSED:
            witness = r.witness
            worst, reason = Status.PROPOSAL, f"OBSTRUCTION:{t}:{r.reason}"
        elif r.outcome is N.NavigationOutcome.GAP_NOT_FOUND and worst is Status.PASS:
            worst, reason = Status.FAIL, f"GAP:{t}:{r.reason}"
    if task.identification_required and worst is Status.PASS:
        for t in task.targets:
            w = N.identification_witness(ks, act_w, t)
            if w is not None:
                witness, worst, reason = w, Status.PROPOSAL, f"NONIDENTIFIABLE:{t}"
                break
    payload = {"outcomes": {t: f"{r.outcome.value}:{r.reason}" for t, r in outcomes.items()}, "live_atoms": len(ks.live_atoms(rv)), "unknown_atoms": len(ks.unknown_atoms(rv))}
    return StageResult(Stage.NAVIGATION, worst, reason, object_ids=tuple(task.targets), payload=payload, resources=res), {"act_w": act_w, "act_x": act_x, "background": background, "background_x": background_x, "witness": witness, "outcomes": outcomes}


def _extraction_index_failure(ks: KnowledgeSpace, index: ExtractionIndex) -> StageResult | None:
    try:
        index.check(ks)
    except CannotCheck as exc:
        return StageResult(Stage.EXTRACTION, Status.CANNOT_CHECK, str(exc),
                           payload={"extraction_path": "INDEXED", "snapshot_valid": False})
    return None


def extract_stage(ks: KnowledgeSpace, seed: Sequence[Fraction], nav: Mapping[str, Any], cfg: SolveConfig, revoked: Iterable[Hashable], *, extraction_index: ExtractionIndex | None = None) -> tuple[StageResult, dict[str, Any]]:
    if extraction_index is not None and (failure := _extraction_index_failure(ks, extraction_index)) is not None:
        return failure, {}
    rv = frozenset(revoked)
    rho_w = SP.surprise(ks, nav["act_w"], nav["background"], seed, cfg.alpha, cfg.surprise_model, revoked=rv)
    rho_x = SP.surprise(ks, nav["act_x"], nav["background_x"], seed, cfg.alpha, cfg.surprise_model, revoked=rv, mode=N.NavigationMode.EXPLORATORY)
    indexed_work = {}
    if extraction_index is None:
        g_w = EX.reacting_subgraph_from_surprise(ks, rho_w, seed, revoked=rv, mode=N.NavigationMode.WARRANTED)
        g_x = EX.reacting_subgraph_from_surprise(ks, rho_x, seed, revoked=rv, mode=N.NavigationMode.EXPLORATORY)
    else:
        g_w, warranted_work = EXI.reacting_subgraph_from_surprise_indexed(
            ks, rho_w, seed, revoked=rv, mode=N.NavigationMode.WARRANTED, index=extraction_index, with_work=True)
        g_x, exploratory_work = EXI.reacting_subgraph_from_surprise_indexed(
            ks, rho_x, seed, revoked=rv, mode=N.NavigationMode.EXPLORATORY, index=extraction_index, with_work=True)
        indexed_work = {"warranted_reaction": warranted_work.as_dict(),
                        "exploratory_reaction": exploratory_work.as_dict()}
    approx = "NONE"
    ties = 0
    prizes = {x: Fraction(max(0.0, rho_w[x])).limit_denominator(10**6) for x in ks.ids}
    support = [x for x, v in zip(ks.ids, seed, strict=True) if v > 0 and ks.atom(x).is_live(rv)]
    optimum: EX.ExtractionResult | None = None
    exact_candidates = 0
    if support:
        try:
            optimum = EX.pcst_exact_bounded(ks, prizes, support, revoked=rv, max_atoms=cfg.exact_extraction_max_atoms)
            approx, ties = optimum.approximation.value, optimum.ties
            exact_candidates = optimum.candidates_considered
        except CannotCheck:
            if extraction_index is None:
                optimum = EX.pcst_greedy(ks, prizes, support, revoked=rv)
            else:
                optimum, greedy_work = EXI.pcst_greedy_indexed(
                    ks, prizes, support, revoked=rv, index=extraction_index, with_work=True)
                indexed_work["greedy_optimizer"] = greedy_work.as_dict()
            approx = optimum.approximation.value
    payload = {"warranted_atoms": sorted(g_w.atoms), "exploratory_only_atoms": sorted(g_x.atoms - g_w.atoms), "optimiser": approx, "optimiser_ties": ties, "surprise_model": cfg.surprise_model.value}
    if extraction_index is not None:
        payload["indexed_extraction"] = {
            "query_work": indexed_work,
            "index_preparation": {"accounting": "CALLER_OWNED", "charged_in_query": False,
                                  "build_work": dict(extraction_index.build_work)},
            "global_preparation": {"total_objects": len(ks.ids), "total_relations": len(ks.hyperedges),
                "surprise_calls": 2, "surprise_scope": "FULL_FIELD", "surprise_internal_work": "NOT_INSTRUMENTED",
                "prize_entries_materialized": len(prizes), "optimizer_seed_entries_examined": len(seed),
                "exact_optimizer_universe_entries_examined": len(ks.ids) if support else 0,
                "exact_optimizer_candidate_subsets": exact_candidates},
            "complete_runtime_scaling": "NOT_ESTABLISHED"}
    status = Status.PASS if g_w.atoms else Status.FAIL
    reason = "REACTING_SUBGRAPH" if g_w.atoms else "NO_WARRANTED_REACTION"
    return StageResult(Stage.EXTRACTION, status, reason, object_ids=tuple(sorted(g_w.atoms)), payload=payload, resources=ResourceVector(composition_work=len(g_w.atoms))), {"g_w": g_w, "g_x": g_x, "optimum": optimum}


Backend = Callable[[KnowledgeSpace, str, Mapping[str, Any]], Mapping[str, Any]]
CallbackGuard = Callable[..., Any]


class CallbackStateChanged(RuntimeError):
    """The host callback changed the runtime state used by this solve."""


@dataclass(frozen=True)
class OperatorSpec:
    """Registered executable operator (M2 §7): controlled backends only at M2."""

    operator_id: str
    version: str
    backend: Backend
    input_atoms: tuple[str, ...]
    output_type: str = "procedure"
    warrant: WarrantProfile = field(default_factory=WarrantProfile.one)
    authority: Authority = field(default_factory=Authority)
    scope: Scope = field(default_factory=Scope.universal)
    checker: Callable[[Mapping[str, Any]], Status] | None = None

    @property
    def fingerprint(self) -> str:
        from ocm.kso.ids import content_hash

        return content_hash({"id": self.operator_id, "version": self.version, "inputs": list(self.input_atoms), "type": self.output_type})


def fire_stage(ks: KnowledgeSpace, nav: Mapping[str, Any], g: EX.ReactingSubgraph, cfg: SolveConfig, revoked: Iterable[Hashable], context: str | None) -> tuple[StageResult, tuple[str, ...]]:
    rv = frozenset(revoked)
    verdicts = [FI.enabling_verdict(ks, e, nav["act_w"], cfg.firing_threshold, rv, context=context) for e in ks.hyperedges if e.edge_id in g.edges]
    enabled = tuple(sorted(v.edge_id for v in verdicts if v.enabling is FI.Enabling.ENABLED))
    unknown = tuple(sorted(v.edge_id for v in verdicts if v.enabling is FI.Enabling.UNKNOWN))
    status = Status.PASS if not unknown else Status.CANNOT_CHECK
    reason = "ENABLED_SET_COMPUTED" if not unknown else "ENABLING_UNKNOWN_FOR_SOME_EDGES"
    return StageResult(Stage.EXECUTION, status, reason, object_ids=enabled, payload={"enabled": list(enabled), "unknown": list(unknown), "disabled": [v.edge_id for v in verdicts if v.enabling is FI.Enabling.DISABLED]}), enabled


def compose_stage(ks: KnowledgeSpace, ops: Sequence[OperatorSpec], g: EX.ReactingSubgraph, revoked: Iterable[Hashable], *, callback_guard: CallbackGuard | None = None) -> tuple[StageResult, list[tuple[OperatorSpec, Mapping[str, Any], WarrantProfile]]]:
    """Retrieve applicable operators (inputs inside the reacting subgraph) and *simulate* them via
    their registered backend; the candidate's warrant is bridge ⊗ inputs (KS-T20).  Nothing is
    written to the store here."""
    rv = frozenset(revoked)
    amap = ks.atom_view
    candidates = []
    res = ResourceVector()
    if isinstance(ops, SolveOperatorIndex):
        selected = ops.select(g.atoms)
        candidate_ops = selected.operators
        selection_work = {"mode": "EXACT_INPUT_INDEX", **selected.work}
    else:
        candidate_ops = ops
        selection_work = {"mode": "FULL_SCAN", "catalogue_operators": len(ops),
                          "operators_considered": len(ops), "index_probes": 0,
                          "postings_examined": 0}
    for op in candidate_ops:
        if not set(op.input_atoms) <= g.atoms:
            continue
        if not op.warrant.is_live(rv) or any(not amap[x].is_live(rv) for x in op.input_atoms):
            continue
        try:
            out = (op.backend(ks, op.operator_id, {"inputs": op.input_atoms}) if callback_guard is None
                   else callback_guard(op.backend, ks, op.operator_id, {"inputs": op.input_atoms}))
        except CallbackStateChanged:
            return StageResult(Stage.COMPOSITION, Status.CANNOT_CHECK, "BACKEND_RUNTIME_STATE_CHANGED",
                               payload={"operator": op.operator_id, "operator_selection": selection_work},
                               resources=res + ResourceVector(composition_work=len(op.input_atoms),
                                                              verification_calls=1)), []
        except Exception as exc:  # noqa: BLE001 — a crashing backend is a failed candidate, never a pass
            candidates.append((op, {"error": f"{type(exc).__name__}: {exc}"}, WarrantProfile.zero()))
            continue
        warrant = AD.meet_all_profiles([op.warrant, *(amap[x].warrant for x in op.input_atoms)])
        candidates.append((op, out, warrant))
        res = res + ResourceVector(composition_work=len(op.input_atoms), verification_calls=1)
    status = Status.PASS if candidates else Status.FAIL
    return StageResult(Stage.COMPOSITION, status, "CANDIDATES_COMPOSED" if candidates else "NO_APPLICABLE_OPERATOR", object_ids=tuple(op.operator_id for op, _, _ in candidates), payload={"candidates": len(candidates), "operator_selection": selection_work}, resources=res), candidates


def check_stage(candidates: Sequence[tuple[OperatorSpec, Mapping[str, Any], WarrantProfile]], revoked: Iterable[Hashable], *, callback_guard: CallbackGuard | None = None) -> tuple[StageResult, list[tuple[OperatorSpec, Mapping[str, Any], WarrantProfile, Status]]]:
    rv = frozenset(revoked)
    checked = []
    worst = Status.PASS
    for op, out, warrant in candidates:
        if "error" in out:
            verdict = Status.FAIL
        elif op.checker is None:
            verdict = Status.CANNOT_CHECK  # a required checker that cannot run never becomes success
        else:
            try:
                verdict = op.checker(out) if callback_guard is None else callback_guard(op.checker, out)
            except CallbackStateChanged:
                # Earlier passes belong to the abandoned state too, not to the changed runtime.
                invalid = [(o, value, w, Status.CANNOT_CHECK) for o, value, w, _ in checked]
                invalid.append((op, out, warrant, Status.CANNOT_CHECK))
                return StageResult(Stage.CHECK, Status.CANNOT_CHECK, "CHECKER_RUNTIME_STATE_CHANGED",
                                   payload={"operator": op.operator_id,
                                            "verdicts": {o.operator_id: v.value for o, _, _, v in invalid}},
                                   resources=ResourceVector(verification_calls=len(invalid))), invalid
            except CannotCheck:
                verdict = Status.CANNOT_CHECK
            except Exception:  # noqa: BLE001
                verdict = Status.FAIL
        if warrant.liveness(rv) is not Liveness.LIVE and verdict is Status.PASS:
            verdict = Status.CANNOT_CHECK if warrant.liveness(rv) is Liveness.UNKNOWN else Status.FAIL
        checked.append((op, out, warrant, verdict))
        if {Status.PASS: 0, Status.PROPOSAL: 1, Status.CANNOT_CHECK: 2, Status.FAIL: 3}[verdict] > {Status.PASS: 0, Status.PROPOSAL: 1, Status.CANNOT_CHECK: 2, Status.FAIL: 3}[worst]:
            worst = verdict
    passed = [c for c in checked if c[3] is Status.PASS]
    status = Status.PASS if passed else (worst if checked else Status.FAIL)
    return StageResult(Stage.CHECK, status, f"{len(passed)}_OF_{len(checked)}_CANDIDATES_PASS", object_ids=tuple(op.operator_id for op, _, _, v in checked if v is Status.PASS), payload={"verdicts": {op.operator_id: v.value for op, _, _, v in checked}}, resources=ResourceVector(verification_calls=len(checked))), checked


# ---------------------------------------------------------------------------------------------
# decision and commitment gate
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SolveOutcome:
    decision: Decision
    trace: SolveTrace
    answer: Mapping[str, Any] | None = None
    candidate: tuple[OperatorSpec, Mapping[str, Any], WarrantProfile] | None = None
    witness: N.ObstructionWitness | None = None
    gap_hook: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"decision": self.decision.value, "trace": self.trace.as_dict(), "answer": self.answer, "gap_hook": self.gap_hook, "witness": None if self.witness is None else self.witness.failed_obligation}


def decide(trace: SolveTrace, nav: Mapping[str, Any], checked: Sequence[tuple[OperatorSpec, Mapping[str, Any], WarrantProfile, Status]], task: Task) -> tuple[StageResult, SolveOutcome]:
    statuses = {s.stage: s for s in trace.stages}
    nav_stage = statuses.get(Stage.NAVIGATION)
    upstream = next((st for st in trace.stages if st.status is Status.CANNOT_CHECK and st.stage is not Stage.DECISION), None)
    if upstream is not None:                                   # CANNOT_CHECK is absorbing along the pipeline (C4 / MEG-11)
        r = StageResult(Stage.DECISION, Status.CANNOT_CHECK, f"UPSTREAM_CANNOT_CHECK:{upstream.stage.value}")
        return r, SolveOutcome(Decision.CANNOT_CHECK, trace)
    if nav.get("witness") is not None:
        r = StageResult(Stage.DECISION, Status.PROPOSAL, "JUMP_PROPOSAL_FROM_OBSTRUCTION")
        return r, SolveOutcome(Decision.JUMP_PROPOSAL, trace, witness=nav["witness"])
    if nav_stage is not None and nav_stage.status is Status.FAIL:
        gaps = [o for o in nav["outcomes"].values() if o.outcome is N.NavigationOutcome.GAP_NOT_FOUND]
        hook = gaps[0].gap_channel_hook if gaps else ""
        reason = gaps[0].reason if gaps else "GAP"
        dec = Decision.CLARIFY if reason.startswith("WARRANT_UNKNOWN") else (Decision.LEARN if hook in ("ACQUISITION_CHANNELS", "ACQUIRE_WARRANT") else Decision.UNKNOWN)
        r = StageResult(Stage.DECISION, Status.FAIL, f"GAP:{reason}")
        return r, SolveOutcome(dec, trace, gap_hook=hook)
    passed = [c for c in checked if c[3] is Status.PASS]
    if passed:
        op, out, warrant, _ = passed[0]
        r = StageResult(Stage.DECISION, Status.PASS, "ANSWER_FROM_CHECKED_CANDIDATE", object_ids=(op.operator_id,))
        return r, SolveOutcome(Decision.ANSWER, trace, answer=dict(out), candidate=(op, out, warrant))
    if any(c[3] is Status.CANNOT_CHECK for c in checked):
        r = StageResult(Stage.DECISION, Status.CANNOT_CHECK, "CANDIDATES_UNCHECKED")
        return r, SolveOutcome(Decision.CANNOT_CHECK, trace)
    ext = statuses.get(Stage.EXTRACTION)
    if ext is not None and ext.status is Status.PASS and not checked:
        r = StageResult(Stage.DECISION, Status.FAIL, "REACTION_WITHOUT_OPERATOR")
        return r, SolveOutcome(Decision.LEARN, trace, gap_hook="ACQUISITION_CHANNELS")
    r = StageResult(Stage.DECISION, Status.FAIL, "UNKNOWN")
    return r, SolveOutcome(Decision.UNKNOWN, trace)


class CommitmentRefused(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def commitment_gate(outcome: SolveOutcome, task: Task, revoked: Iterable[Hashable], *, commit_authority: Authority) -> StageResult:
    """External commitment is allowed only for an ANSWER whose candidate warrant is LIVE, whose
    authority meets the task's requirement under the *external* commit authority, and whose scope
    covers the task context; any CANNOT_CHECK anywhere in the trace refuses (M2 §5)."""
    rv = frozenset(revoked)
    if outcome.trace.worst_status in (Status.CANNOT_CHECK, Status.FAIL) and outcome.decision is Decision.ANSWER:
        return StageResult(Stage.COMMITMENT, Status.FAIL, "REFUSED:TRACE_NOT_CLEAN")
    if outcome.decision is not Decision.ANSWER or outcome.candidate is None:
        return StageResult(Stage.COMMITMENT, Status.FAIL, f"REFUSED:NO_COMMITTABLE_ANSWER:{outcome.decision.value}")
    op, _, warrant = outcome.candidate
    if warrant.liveness(rv) is not Liveness.LIVE:
        return StageResult(Stage.COMMITMENT, Status.FAIL, f"REFUSED:WARRANT_{warrant.liveness(rv).value}")
    if not (task.required_authority <= op.authority.meet(commit_authority)):
        return StageResult(Stage.COMMITMENT, Status.FAIL, "REFUSED:AUTHORITY_INSUFFICIENT")
    if task.context is not None:
        from ocm.kso.types import UNBOUNDED_EPOCH
        if op.scope.epoch != UNBOUNDED_EPOCH and task.at is None:
            # batch 8 H1 (FDX-01): current validity of an epoch-bounded scope needs the evaluation time; without it the
            # certificate is CONDITIONAL_ON_ASSUMPTIONS, not MONITORED_CURRENT — the gate refuses rather than assumes
            return StageResult(Stage.COMMITMENT, Status.FAIL, "REFUSED:SCOPE_EPOCH_UNDECLARED")
        if not op.scope.covers(task.context, task.at):
            return StageResult(Stage.COMMITMENT, Status.FAIL, "REFUSED:OUT_OF_SCOPE")
    return StageResult(Stage.COMMITMENT, Status.PASS, "COMMITTED", object_ids=(op.operator_id,), evidence_ids=tuple(sorted(map(repr, warrant.evidence))))


# ---------------------------------------------------------------------------------------------
# the loop
# ---------------------------------------------------------------------------------------------


def solve(
    ks: KnowledgeSpace,
    task: Task,
    operators: Sequence[OperatorSpec] = (),
    *,
    revoked: Iterable[Hashable] = (),
    config: SolveConfig = SolveConfig(),
    commit_authority: Authority | None = None,
    extraction_index: ExtractionIndex | None = None,
    callback_guard: CallbackGuard | None = None,
) -> SolveOutcome:
    rv = frozenset(revoked)
    trace = SolveTrace(task.task_id)
    trace.add(StageResult(Stage.TASK, Status.PASS, "RECEIVED", payload={"parts": len(task.parts), "targets": list(task.targets)}))
    if extraction_index is not None and (failure := _extraction_index_failure(ks, extraction_index)) is not None:
        trace.add(failure)
        decision, outcome = decide(trace, {}, (), task)
        trace.add(decision)
        trace.add(commitment_gate(outcome, task, rv, commit_authority=commit_authority or Authority()))
        return outcome
    grounding, seed = atomise(ks, task)
    trace.add(grounding)
    if seed is None:
        dec = StageResult(Stage.DECISION, Status.FAIL, f"GAP:{grounding.reason}")
        trace.add(dec)
        out = SolveOutcome(Decision.CLARIFY if grounding.reason != "EMPTY_QUESTION" else Decision.UNKNOWN, trace, gap_hook="RE_ATOMISE")
        trace.add(commitment_gate(out, task, rv, commit_authority=commit_authority or Authority()))
        return out
    trace.add(StageResult(Stage.REPRESENTATION, Status.PASS, "ACTIVE_REPRESENTATION_SELECTED", payload={"representation": "typed_hypergraph_v1", "atoms": len(ks.ids)}))
    nav_res, nav = navigate_stage(ks, seed, task, config, rv)
    trace.add(nav_res)
    checked: list = []
    if nav_res.status is not Status.CANNOT_CHECK:
        ext_res, ext = extract_stage(ks, seed, nav, config, rv, extraction_index=extraction_index)
        trace.add(ext_res)
        if ext_res.status is not Status.CANNOT_CHECK:
            fire_res, enabled = fire_stage(ks, nav, ext["g_w"], config, rv, task.context)
            trace.add(fire_res)
            if fire_res.status is not Status.CANNOT_CHECK:
                # C4 (MEG-11): composition runs only over the *enabled* part of the reacting subgraph;
                # a FIRE-stage CANNOT_CHECK is absorbing (no composition, no check, decision CANNOT_CHECK)
                g_w = ext["g_w"]
                enabled_atoms = {a for e in ks.hyperedges if e.edge_id in enabled for a in (*e.tails, *e.heads)} | set(g_w.seed_support)
                g_enabled = EX.ReactingSubgraph(frozenset(g_w.atoms & enabled_atoms), frozenset(enabled), g_w.mode, g_w.seed_support)
                comp_res, candidates = compose_stage(ks, operators, g_enabled, rv, callback_guard=callback_guard)
                trace.add(comp_res)
                if comp_res.status is not Status.CANNOT_CHECK:
                    chk_res, checked = check_stage(candidates, rv, callback_guard=callback_guard)
                    trace.add(chk_res)
    dec_res, outcome = decide(trace, nav, checked, task)
    trace.add(dec_res)
    trace.add(commitment_gate(outcome, task, rv, commit_authority=commit_authority or Authority()))
    return outcome


def committed(outcome: SolveOutcome) -> bool:
    last = outcome.trace.stages[-1]
    return last.stage is Stage.COMMITMENT and last.status is Status.PASS
