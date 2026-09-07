"""SEARCH_MORE versus JUMP: exact escalation-level discrimination.

This module implements the programme's flagship discriminator.  Its whole
purpose is that in a finite exactly-solvable world the **minimum sufficient
escalation level is decidable**, so ``false_jump_rate``,
``missed_jump_rate`` and ``minimum_sufficient_level_accuracy`` are measured
against ground truth rather than against a judgement call.

The machine's diagnosis is computed from *machine-visible* quantities only:
the evidence it has actually seen, the surviving version space, the probes it
is still allowed, and its remaining budget.  It never reads the ground-truth
label of an unprobed position and it never reads the world's own
``minimum_sufficient_level``.  ``diagnose`` and ``ground_truth_level`` are kept
in separate call paths for that reason.

Discipline enforced here, from the programme steering:

* **Saturation is scoped.**  When no allowed probe can split the surviving
  version space the terminal is ``SATURATED_WITHIN_REGISTERED_SPACE``.  It is
  never ``PROBLEM_IMPOSSIBLE``; impossibility needs an independent proof.
* **Saturation does not authorise a Jump.**  It is one input to obstruction
  diagnosis.  A saturated version space that a *larger* language would split is
  an operator-insufficiency witness, not a representation witness.
* **Budget exhaustion is not an obstruction.**  A world where a splitting probe
  exists but the budget ran out must diagnose ``BUDGET_EXHAUSTED`` and must not
  escalate.  This is the single most important hostile in the module, because
  "I tried hard and failed" is exactly the false Jump witness the programme has
  to refuse.
* **Non-identifiability is witnessed, not inferred.**  A representation is
  non-identifying when two positions with the same representational image carry
  different truth values.  That is an exhibited pair, checkable by a third
  party from the receipt.

Parents with first right of refusal: CEGAR (abstraction refinement on a spurious
counterexample), version-space learning and its collapse conditions, active
learning / optimal experimental design (which probe splits the space), program
synthesis with vocabulary extension (CEGIS), and abstract interpretation
(closure certificates).  None of these is claimed as new here.  The claim under
test is only whether an explicit governed escalation policy picks the *minimum
sufficient* level more accurately than those parents' natural policies.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

from games import Work

__all__ = [
    "Level",
    "Diagnosis",
    "Representation",
    "EscalationWorld",
    "diagnose",
    "identifiability_witness",
]


class Level(enum.IntEnum):
    """Minimum sufficient escalation level, ordered.

    The ordering matters: escalating *above* the minimum sufficient level is
    overreach and is counted as a false Jump even when the task is solved,
    because the programme's claim is about minimum-sufficient escalation and a
    machine that always jumps to the top would score perfectly on task success.
    """

    L0_NO_ESCALATION = 0        # the incumbent already identifies; nothing to do
    L1_SEARCH_MORE = 1          # same R, same O, same E-channel: more probes/budget suffice
    L2_MORE_EVIDENCE = 2        # the probe channel must be widened, not the search deepened
    L3_LOCAL_REPAIR = 3         # one bound/parameter of the incumbent language is too tight
    L4_OPERATOR_INSUFFICIENT = 4  # the method vocabulary genuinely lacks a needed operator
    L5_REPRESENTATION_CHANGE = 5  # the representation is non-identifying; no O fixes it
    L6_FORMULATION_CHANGE = 6   # the problem statement itself is wrong (e.g. play convention)


#: Levels at or above this are a Jump in the programme's sense: they change the
#: representation, the operator vocabulary or the problem formulation.  Below it
#: the incumbent formulation is retained and only search, evidence or a bound
#: moves.
JUMP_THRESHOLD = Level.L4_OPERATOR_INSUFFICIENT


@dataclass(frozen=True)
class Representation:
    """A registered representation: positions to observable images.

    ``name`` is part of the pre-registration.  ``image`` must be a pure function
    of the position; a representation that may consult the label is not a
    representation, it is the answer.
    """

    name: str
    image: Callable[[object], object]

    def images(self, positions: Iterable[object]) -> list[object]:
        return [self.image(p) for p in positions]


def identifiability_witness(
    representation: Representation,
    positions: Sequence[object],
    truth: Callable[[object], bool],
) -> tuple[object, object] | None:
    """Return a pair of positions that refutes ``representation``, or ``None``.

    A refuting pair has the same representational image and different truth.
    Its existence is an *exhibited* obstruction: any third party holding the
    receipt can recompute both images and both labels and confirm that no
    method expressible over this representation can separate them.  This is what
    the protocol means by a witnessed obstruction, as opposed to a timeout.
    """
    by_image: dict[object, tuple[object, bool]] = {}
    for p in positions:
        key = representation.image(p)
        label = truth(p)
        if key in by_image:
            other, other_label = by_image[key]
            if other_label != label:
                return (other, p)
        else:
            by_image[key] = (p, label)
    return None


@dataclass(frozen=True)
class Diagnosis:
    """What the machine concluded, and on what visible grounds."""

    level: Level
    terminal: str
    version_space_size: int
    splitting_probe: object | None
    obstruction_witness: tuple[object, object] | None
    budget_remaining: int
    rationale: str
    work: dict

    @property
    def is_jump(self) -> bool:
        return self.level >= JUMP_THRESHOLD

    def as_dict(self) -> dict:
        return {
            "level": self.level.name,
            "terminal": self.terminal,
            "version_space_size": self.version_space_size,
            "splitting_probe": self.splitting_probe,
            "obstruction_witness": list(self.obstruction_witness)
            if self.obstruction_witness
            else None,
            "budget_remaining": self.budget_remaining,
            "is_jump": self.is_jump,
            "rationale": self.rationale,
            "work": self.work,
        }


@dataclass(frozen=True)
class EscalationWorld:
    """One frozen escalation world.

    ``minimum_sufficient_level`` is the ground truth, established by
    construction when the world is registered.  It is read **only** by the
    scorer.  ``diagnose`` never receives this object's truth field.
    """

    world_id: str
    positions: tuple[object, ...]
    truth: Callable[[object], bool]
    representation: Representation
    #: hypotheses expressible over ``representation`` with the incumbent operator
    #: vocabulary; each maps a position to a predicted label
    incumbent_hypotheses: tuple[Callable[[object], bool], ...]
    #: hypotheses that become available if the operator vocabulary is widened by
    #: one registered operator (the L4 repair)
    widened_hypotheses: tuple[Callable[[object], bool], ...] = ()
    #: hypotheses that become available only under a different representation
    #: (the L5 repair)
    refined_hypotheses: tuple[Callable[[object], bool], ...] = ()
    #: positions the machine is still permitted to probe
    allowed_probes: tuple[object, ...] = ()
    #: probes already spent
    observed: tuple[tuple[object, bool], ...] = ()
    probe_budget: int = 0
    minimum_sufficient_level: Level = Level.L0_NO_ESCALATION
    #: set when the incumbent bound is merely one notch too tight (L3)
    local_repair_available: bool = False
    #: set when the play convention / problem statement is wrong (L6)
    formulation_defect: bool = False
    notes: str = ""


def _survivors(
    hypotheses: Sequence[Callable[[object], bool]],
    observed: Sequence[tuple[object, bool]],
    work: Work,
) -> list[Callable[[object], bool]]:
    out = []
    for h in hypotheses:
        work.expansions += 1
        ok = True
        for pos, label in observed:
            work.predicate_evaluations += 1
            if h(pos) != label:
                ok = False
                break
        if ok:
            out.append(h)
    return out


def _find_splitting_probe(
    survivors: Sequence[Callable[[object], bool]],
    probes: Sequence[object],
    work: Work,
) -> object | None:
    """A probe on which two surviving hypotheses disagree.

    Existence of such a probe means the machine is *not* saturated: ordinary
    information gathering still reduces the space.  Absence means saturation
    within the registered ``(R, O, A)`` — and nothing stronger.
    """
    for probe in probes:
        seen: bool | None = None
        for h in survivors:
            work.predicate_evaluations += 1
            v = h(probe)
            if seen is None:
                seen = v
            elif v != seen:
                return probe
    return None


def diagnose(world: EscalationWorld) -> Diagnosis:
    """Diagnose the minimum sufficient escalation level from visible state only.

    The order of tests is the policy under evaluation, and it is deliberately
    conservative: every cheaper explanation must be excluded before a more
    expensive one is proposed.  Read top to bottom, the function *is* the
    escalation contract of the protocol.
    """
    work = Work()
    survivors = _survivors(world.incumbent_hypotheses, world.observed, work)

    # ---- case 1: the incumbent is refuted outright -----------------------
    if not survivors:
        # Before blaming the operator vocabulary, check whether the evidence
        # already exhibits a representational collision.  If two *observed*
        # positions share an image and differ in label, no operator over this
        # representation could have fitted, so the fault is the representation.
        witness = identifiability_witness(
            world.representation,
            [p for p, _ in world.observed],
            dict(world.observed).__getitem__,
        )
        if witness is not None:
            return Diagnosis(
                level=Level.L5_REPRESENTATION_CHANGE,
                terminal="REPRESENTATION_NON_IDENTIFYING_WITNESSED",
                version_space_size=0,
                splitting_probe=None,
                obstruction_witness=witness,
                budget_remaining=world.probe_budget,
                rationale=(
                    "two observed positions share a representational image and "
                    "carry different labels; no method over this representation "
                    "can separate them"
                ),
                work=work.as_dict(),
            )
        # Otherwise: the representation separates the evidence but no incumbent
        # hypothesis fits.  A one-notch bound repair is the cheaper explanation
        # and must be excluded before widening the vocabulary.
        if world.local_repair_available:
            return Diagnosis(
                level=Level.L3_LOCAL_REPAIR,
                terminal="INCUMBENT_BOUND_TOO_TIGHT",
                version_space_size=0,
                splitting_probe=None,
                obstruction_witness=None,
                budget_remaining=world.probe_budget,
                rationale="no incumbent hypothesis fits, but a registered bound relaxation admits one",
                work=work.as_dict(),
            )
        widened = _survivors(world.widened_hypotheses, world.observed, work)
        if widened:
            return Diagnosis(
                level=Level.L4_OPERATOR_INSUFFICIENT,
                terminal="OPERATOR_VOCABULARY_INSUFFICIENT_WITNESSED",
                version_space_size=0,
                splitting_probe=None,
                obstruction_witness=None,
                budget_remaining=world.probe_budget,
                rationale=(
                    "the incumbent vocabulary is refuted by the evidence while a "
                    "single registered operator extension fits it"
                ),
                work=work.as_dict(),
            )
        if world.formulation_defect:
            return Diagnosis(
                level=Level.L6_FORMULATION_CHANGE,
                terminal="PROBLEM_FORMULATION_REFUTED",
                version_space_size=0,
                splitting_probe=None,
                obstruction_witness=None,
                budget_remaining=world.probe_budget,
                rationale="no vocabulary extension over any registered representation fits the evidence",
                work=work.as_dict(),
            )
        return Diagnosis(
            level=Level.L5_REPRESENTATION_CHANGE,
            terminal="REPRESENTATION_CHANGE_REQUIRED",
            version_space_size=0,
            splitting_probe=None,
            obstruction_witness=None,
            budget_remaining=world.probe_budget,
            rationale="incumbent and widened vocabularies are both refuted by the evidence",
            work=work.as_dict(),
        )

    # ---- case 2: the incumbent already identifies ------------------------
    if len(survivors) == 1:
        return Diagnosis(
            level=Level.L0_NO_ESCALATION,
            terminal="IDENTIFIED_WITHIN_INCUMBENT",
            version_space_size=1,
            splitting_probe=None,
            obstruction_witness=None,
            budget_remaining=world.probe_budget,
            rationale="exactly one incumbent hypothesis survives the evidence",
            work=work.as_dict(),
        )

    # ---- case 3: several hypotheses survive ------------------------------
    probe = _find_splitting_probe(survivors, world.allowed_probes, work)
    if probe is not None:
        if world.probe_budget > 0:
            return Diagnosis(
                level=Level.L1_SEARCH_MORE,
                terminal="NOT_SATURATED_SPLITTING_PROBE_AVAILABLE",
                version_space_size=len(survivors),
                splitting_probe=probe,
                obstruction_witness=None,
                budget_remaining=world.probe_budget,
                rationale="an allowed probe separates surviving hypotheses and budget remains",
                work=work.as_dict(),
            )
        # A splitting probe exists but there is no budget to spend on it.
        # This is exhaustion, not obstruction, and it must NOT escalate.
        return Diagnosis(
            level=Level.L1_SEARCH_MORE,
            terminal="BUDGET_EXHAUSTED",
            version_space_size=len(survivors),
            splitting_probe=probe,
            obstruction_witness=None,
            budget_remaining=0,
            rationale=(
                "a splitting probe exists but the registered budget is spent; "
                "exhaustion is not an obstruction witness and does not authorise escalation"
            ),
            work=work.as_dict(),
        )

    # No allowed probe splits the surviving space: saturated within (R, O, A).
    # Saturation alone decides nothing.  Ask what would split it.
    wider_probes = tuple(p for p in world.positions if p not in set(world.allowed_probes))
    if wider_probes and _find_splitting_probe(survivors, wider_probes, work) is not None:
        return Diagnosis(
            level=Level.L2_MORE_EVIDENCE,
            terminal="SATURATED_WITHIN_REGISTERED_SPACE",
            version_space_size=len(survivors),
            splitting_probe=None,
            obstruction_witness=None,
            budget_remaining=world.probe_budget,
            rationale=(
                "no permitted probe splits the space, but a position outside the "
                "registered probe set does; the evidence channel is the binding constraint"
            ),
            work=work.as_dict(),
        )

    witness = identifiability_witness(world.representation, world.positions, world.truth)
    if witness is not None:
        return Diagnosis(
            level=Level.L5_REPRESENTATION_CHANGE,
            terminal="REPRESENTATION_NON_IDENTIFYING_WITNESSED",
            version_space_size=len(survivors),
            splitting_probe=None,
            obstruction_witness=witness,
            budget_remaining=world.probe_budget,
            rationale=(
                "no probe anywhere splits the surviving space and an exhibited pair "
                "shares a representational image with different labels"
            ),
            work=work.as_dict(),
        )

    return Diagnosis(
        level=Level.L4_OPERATOR_INSUFFICIENT,
        terminal="SATURATED_WITHIN_REGISTERED_SPACE",
        version_space_size=len(survivors),
        splitting_probe=None,
        obstruction_witness=None,
        budget_remaining=world.probe_budget,
        rationale=(
            "the space is saturated under every probe and the representation "
            "separates every position, so the operator vocabulary is the binding constraint"
        ),
        work=work.as_dict(),
    )


def score(world: EscalationWorld, diagnosis: Diagnosis) -> dict:
    """Score one diagnosis against the world's registered ground truth.

    ``false_jump`` counts escalation at or above the Jump threshold when the
    minimum sufficient level was below it.  ``missed_jump`` counts the reverse.
    ``overreach`` counts any escalation strictly above the minimum sufficient
    level, including within-threshold overreach, because a policy that always
    picks the highest level would otherwise look perfect.
    """
    truth_level = world.minimum_sufficient_level
    return {
        "world_id": world.world_id,
        "diagnosed": diagnosis.level.name,
        "minimum_sufficient": truth_level.name,
        "exact_match": diagnosis.level == truth_level,
        "false_jump": diagnosis.is_jump and truth_level < JUMP_THRESHOLD,
        "missed_jump": (not diagnosis.is_jump) and truth_level >= JUMP_THRESHOLD,
        "overreach": int(diagnosis.level) > int(truth_level),
        "underreach": int(diagnosis.level) < int(truth_level),
        "terminal": diagnosis.terminal,
        "witnessed": diagnosis.obstruction_witness is not None,
    }
