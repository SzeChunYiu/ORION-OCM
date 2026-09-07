"""Strongest naive escalation policies: first right of refusal.

A diagnosis policy scored only against worlds its own author designed proves
nothing.  These parents exist so the escalation number is a *comparison*.  Each
is a faithful, non-strawman rendering of a policy that is genuinely used, and
each is given exactly the same visible state as the governed policy.

``timeout_parent``
    Escalate when the budget runs out.  This is the default behaviour of almost
    every practical agent loop, and it is the policy the programme most needs to
    beat, because "I tried hard and failed" is the commonest false Jump witness.

``saturation_parent``
    Escalate when the version space stops collapsing.  This treats cognitive
    saturation as authority for a Jump.  Refusing this inference is precisely
    the programme's stated discipline, so this parent measures what that
    discipline buys.

``cegar_parent``
    Refine the representation whenever the incumbent is refuted by a
    counterexample.  This is counterexample-guided abstraction refinement read
    as an escalation policy.  It is strong and correct in its home setting; here
    it is expected to over-refine when the true defect is a bound or a missing
    operator, which is the honest cost of an always-refine rule.

None of these parents is weakened.  If one of them matches the governed policy
on the protected draw, the correct report is ``PARENT_SUFFICIENT``.
"""

from __future__ import annotations

from typing import Callable

from escalation import Diagnosis, EscalationWorld, Level, _find_splitting_probe, _survivors
from games import Work

__all__ = ["PARENTS", "timeout_parent", "saturation_parent", "cegar_parent"]


def _base(world: EscalationWorld):
    work = Work()
    survivors = _survivors(world.incumbent_hypotheses, world.observed, work)
    probe = _find_splitting_probe(survivors, world.allowed_probes, work)
    return survivors, probe, work


def timeout_parent(world: EscalationWorld) -> Diagnosis:
    survivors, probe, work = _base(world)
    if len(survivors) == 1:
        level, terminal = Level.L0_NO_ESCALATION, "IDENTIFIED_WITHIN_INCUMBENT"
    elif world.probe_budget <= 0 or not survivors:
        level, terminal = Level.L5_REPRESENTATION_CHANGE, "ESCALATED_ON_EXHAUSTION"
    else:
        level, terminal = Level.L1_SEARCH_MORE, "BUDGET_REMAINS"
    return Diagnosis(
        level=level,
        terminal=terminal,
        version_space_size=len(survivors),
        splitting_probe=probe,
        obstruction_witness=None,
        budget_remaining=world.probe_budget,
        rationale="escalate when the budget is spent",
        work=work.as_dict(),
    )


def saturation_parent(world: EscalationWorld) -> Diagnosis:
    survivors, probe, work = _base(world)
    if len(survivors) == 1:
        level, terminal = Level.L0_NO_ESCALATION, "IDENTIFIED_WITHIN_INCUMBENT"
    elif probe is not None:
        level, terminal = Level.L1_SEARCH_MORE, "NOT_SATURATED"
    else:
        level, terminal = Level.L5_REPRESENTATION_CHANGE, "ESCALATED_ON_SATURATION"
    return Diagnosis(
        level=level,
        terminal=terminal,
        version_space_size=len(survivors),
        splitting_probe=probe,
        obstruction_witness=None,
        budget_remaining=world.probe_budget,
        rationale="treat saturation of the version space as authority to change representation",
        work=work.as_dict(),
    )


def cegar_parent(world: EscalationWorld) -> Diagnosis:
    survivors, probe, work = _base(world)
    if not survivors:
        level, terminal = Level.L5_REPRESENTATION_CHANGE, "REFINED_ON_COUNTEREXAMPLE"
    elif len(survivors) == 1:
        level, terminal = Level.L0_NO_ESCALATION, "IDENTIFIED_WITHIN_INCUMBENT"
    elif probe is not None:
        level, terminal = Level.L1_SEARCH_MORE, "NOT_YET_REFUTED"
    else:
        level, terminal = Level.L5_REPRESENTATION_CHANGE, "REFINED_ON_STALL"
    return Diagnosis(
        level=level,
        terminal=terminal,
        version_space_size=len(survivors),
        splitting_probe=probe,
        obstruction_witness=None,
        budget_remaining=world.probe_budget,
        rationale="refine the abstraction whenever the incumbent is refuted or stalls",
        work=work.as_dict(),
    )


PARENTS: dict[str, Callable[[EscalationWorld], Diagnosis]] = {
    "timeout": timeout_parent,
    "saturation": saturation_parent,
    "cegar": cegar_parent,
}


def exact_repair_planner_parent(world: EscalationWorld) -> Diagnosis:
    """The fully-resourced parent: pick the minimum repair that admits a fit.

    This is the analogue, in the exact-game setting, of the parent that has
    already closed the binary Jump decision elsewhere in the programme: a
    verified-regime-revision parent, and the exact finite-horizon planner that
    beat or tied the governed mechanic on minimum-escalation accuracy in the
    prior decisive studies.  It is given the same repairs the governed policy
    may propose and it simply tries them in cost order, taking the first that
    admits a consistent hypothesis.

    It carries no witness requirement.  That is the whole point: it should be
    expected to match the governed policy on *accuracy* wherever the repair
    ladder is a finite decision problem, leaving false-escalation behaviour as
    the only place a residual could survive.  If it matches on both, the honest
    report for this rung is PARENT_SUFFICIENT and the pilot has done its job.
    """
    work = Work()
    survivors = _survivors(world.incumbent_hypotheses, world.observed, work)
    if len(survivors) == 1:
        level, terminal = Level.L0_NO_ESCALATION, "IDENTIFIED_WITHIN_INCUMBENT"
    elif survivors:
        level, terminal = Level.L1_SEARCH_MORE, "INCUMBENT_STILL_VIABLE"
    elif world.local_repair_available:
        level, terminal = Level.L3_LOCAL_REPAIR, "MINIMUM_REPAIR_IS_A_BOUND"
    elif _survivors(world.widened_hypotheses, world.observed, work):
        level, terminal = Level.L4_OPERATOR_INSUFFICIENT, "MINIMUM_REPAIR_IS_A_WIDER_VOCABULARY"
    elif world.formulation_defect:
        level, terminal = Level.L6_FORMULATION_CHANGE, "NO_REPAIR_FITS_ANY_REGISTERED_REPRESENTATION"
    else:
        level, terminal = Level.L5_REPRESENTATION_CHANGE, "MINIMUM_REPAIR_IS_A_REPRESENTATION"
    return Diagnosis(
        level=level,
        terminal=terminal,
        version_space_size=len(survivors),
        splitting_probe=None,
        obstruction_witness=None,
        budget_remaining=world.probe_budget,
        rationale="try each registered repair in cost order; take the first that admits a fit",
        work=work.as_dict(),
    )


PARENTS["exact_repair_planner"] = exact_repair_planner_parent
