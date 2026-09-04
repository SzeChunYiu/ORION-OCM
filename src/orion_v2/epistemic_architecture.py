"""Research-only demarcation and frontier-composition semantics.

This module makes several neighboring "machine-X" concepts explicit without
turning them into a hierarchy or new K0-K6 kernel families.  Its two purposes
are:

1. keep learning mechanisms, cognitive organization, capability evaluation,
   machine-native design, scientific capability, epistemic control and AI-for-
   science application scope from silently collapsing into one concept; and
2. connect ordinary epistemic actions to the existing witnessed-Jump machinery
   for frontier problems without implementing a second escalation controller.

The module is intentionally not re-exported from :mod:`orion_v2.kernel`.
Nothing here grants scientific truth, intelligence superiority, novelty,
architecture authority, field status or publication authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from .jump import JumpLevel


def _ids(values: Iterable[str], *, name: str, allow_empty: bool = False) -> tuple[str, ...]:
    result = tuple(values)
    if not allow_empty and not result:
        raise ValueError(f"{name} must not be empty")
    if any(not value.strip() for value in result):
        raise ValueError(f"{name} may not contain blank identities")
    if len(result) != len(set(result)):
        raise ValueError(f"{name} identities must be unique")
    return result


class MachineConcept(StrEnum):
    MACHINE_LEARNING = "MACHINE_LEARNING"
    MACHINE_REASONING_PLANNING = "MACHINE_REASONING_PLANNING"
    MACHINE_COGNITION = "MACHINE_COGNITION"
    MACHINE_INTELLIGENCE = "MACHINE_INTELLIGENCE"
    MACHINE_NATIVE_INTELLIGENCE = "MACHINE_NATIVE_INTELLIGENCE"
    MACHINE_SCIENTIFIC_INTELLIGENCE = "MACHINE_SCIENTIFIC_INTELLIGENCE"
    MACHINE_EPISTEMICS = "MACHINE_EPISTEMICS"
    AI_FOR_SCIENCE = "AI_FOR_SCIENCE"


class MachineConceptRole(StrEnum):
    LEARNING_MECHANISM = "LEARNING_MECHANISM"
    REASONING_PROCESS = "REASONING_PROCESS"
    COGNITIVE_ARCHITECTURE = "COGNITIVE_ARCHITECTURE"
    CAPABILITY_PROFILE = "CAPABILITY_PROFILE"
    DESIGN_ORIENTATION = "DESIGN_ORIENTATION"
    SCIENTIFIC_CAPABILITY = "SCIENTIFIC_CAPABILITY"
    EPISTEMIC_CONTROL = "EPISTEMIC_CONTROL"
    APPLICATION_ECOSYSTEM = "APPLICATION_ECOSYSTEM"


@dataclass(frozen=True, slots=True)
class MachineConceptDescriptor:
    concept: MachineConcept
    role: MachineConceptRole
    primary_question: str
    scientific_object: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "concept", MachineConcept(self.concept))
        object.__setattr__(self, "role", MachineConceptRole(self.role))
        if not self.primary_question.strip() or not self.scientific_object.strip():
            raise ValueError("concept descriptors require a question and scientific object")


_MACHINE_CONCEPT_DESCRIPTORS = {
    MachineConcept.MACHINE_LEARNING: MachineConceptDescriptor(
        MachineConcept.MACHINE_LEARNING,
        MachineConceptRole.LEARNING_MECHANISM,
        "How does a machine update from data, feedback or experience?",
        "learning and update mechanisms",
    ),
    MachineConcept.MACHINE_REASONING_PLANNING: MachineConceptDescriptor(
        MachineConcept.MACHINE_REASONING_PLANNING,
        MachineConceptRole.REASONING_PROCESS,
        "How does a machine derive, search, predict or choose actions?",
        "reasoning, search and planning processes",
    ),
    MachineConcept.MACHINE_COGNITION: MachineConceptDescriptor(
        MachineConcept.MACHINE_COGNITION,
        MachineConceptRole.COGNITIVE_ARCHITECTURE,
        "How are representation, memory, attention, search and planning organized?",
        "organization of information-processing processes",
    ),
    MachineConcept.MACHINE_INTELLIGENCE: MachineConceptDescriptor(
        MachineConcept.MACHINE_INTELLIGENCE,
        MachineConceptRole.CAPABILITY_PROFILE,
        "How capable is a system under a declared ecology of tasks and constraints?",
        "context-relative capability profile",
    ),
    MachineConcept.MACHINE_NATIVE_INTELLIGENCE: MachineConceptDescriptor(
        MachineConcept.MACHINE_NATIVE_INTELLIGENCE,
        MachineConceptRole.DESIGN_ORIENTATION,
        "Which strategies exploit machine-specific affordances rather than requiring human imitation?",
        "substrate-oriented design hypothesis",
    ),
    MachineConcept.MACHINE_SCIENTIFIC_INTELLIGENCE: MachineConceptDescriptor(
        MachineConcept.MACHINE_SCIENTIFIC_INTELLIGENCE,
        MachineConceptRole.SCIENTIFIC_CAPABILITY,
        "How capable is the system at making progress on scientific problems?",
        "scientific capability profile",
    ),
    MachineConcept.MACHINE_EPISTEMICS: MachineConceptDescriptor(
        MachineConcept.MACHINE_EPISTEMICS,
        MachineConceptRole.EPISTEMIC_CONTROL,
        "When may machine-mediated inquiry change scientific commitments, representations, methods, problems or evidence state?",
        "warranted scientific-transition control",
    ),
    MachineConcept.AI_FOR_SCIENCE: MachineConceptDescriptor(
        MachineConcept.AI_FOR_SCIENCE,
        MachineConceptRole.APPLICATION_ECOSYSTEM,
        "How are AI methods and systems used within scientific research?",
        "scientific application and system ecosystem",
    ),
}


def machine_concept_descriptor(concept: MachineConcept) -> MachineConceptDescriptor:
    """Return the local terminology contract for ``concept``.

    The return value is a categorical descriptor, not an ordering or a claim
    that the external literature uses one universal taxonomy.
    """

    return _MACHINE_CONCEPT_DESCRIPTORS[MachineConcept(concept)]


@dataclass(frozen=True, slots=True)
class CapabilityContext:
    """Declared ecology required for a bounded machine-capability claim."""

    environment_ids: tuple[str, ...]
    task_family_ids: tuple[str, ...]
    resource_regime_ids: tuple[str, ...]
    system_boundary_ids: tuple[str, ...]
    substrate_or_interface_ids: tuple[str, ...]
    timescale_ids: tuple[str, ...]
    criterion_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            object.__setattr__(self, name, _ids(getattr(self, name), name=name))


class EpistemicAction(StrEnum):
    RETRIEVE = "RETRIEVE"
    LEARN = "LEARN"
    REASON = "REASON"
    PROVE = "PROVE"
    SIMULATE = "SIMULATE"
    MEASURE = "MEASURE"
    EXPERIMENT = "EXPERIMENT"
    CHALLENGE = "CHALLENGE"
    CHANGE_MODEL = "CHANGE_MODEL"
    CHANGE_REPRESENTATION = "CHANGE_REPRESENTATION"
    CHANGE_PERSPECTIVE = "CHANGE_PERSPECTIVE"
    REFORMULATE_PROBLEM = "REFORMULATE_PROBLEM"
    BUILD_TOOL = "BUILD_TOOL"
    CHANGE_WORKFLOW = "CHANGE_WORKFLOW"
    TRANSFORM_REGIME = "TRANSFORM_REGIME"
    ABSTAIN = "ABSTAIN"


class RegimeTransformScope(StrEnum):
    MODEL = "MODEL"
    REPRESENTATION = "REPRESENTATION"
    PERSPECTIVE = "PERSPECTIVE"
    PROBLEM = "PROBLEM"
    TOOL_OR_INSTRUMENT = "TOOL_OR_INSTRUMENT"
    WORKFLOW_OR_META_SKILL = "WORKFLOW_OR_META_SKILL"
    FRAMEWORK = "FRAMEWORK"


_SCOPE_JUMP_LEVEL = {
    RegimeTransformScope.MODEL: JumpLevel.MODEL_HYPOTHESIS_EXPANSION,
    RegimeTransformScope.REPRESENTATION: JumpLevel.REPRESENTATION_REGIME_TRANSITION,
    RegimeTransformScope.PERSPECTIVE: JumpLevel.REPRESENTATION_REGIME_TRANSITION,
    RegimeTransformScope.PROBLEM: JumpLevel.PROBLEM_OBJECTIVE_REFORMULATION,
    RegimeTransformScope.TOOL_OR_INSTRUMENT: JumpLevel.METHOD_TOOL_INSTRUMENT_INVENTION,
    RegimeTransformScope.WORKFLOW_OR_META_SKILL: JumpLevel.WORKFLOW_META_SKILL_REVISION,
    RegimeTransformScope.FRAMEWORK: JumpLevel.FRAMEWORK_REVISION,
}

_DIRECT_ACTIONS = frozenset(
    {
        EpistemicAction.RETRIEVE,
        EpistemicAction.LEARN,
        EpistemicAction.REASON,
        EpistemicAction.PROVE,
        EpistemicAction.SIMULATE,
        EpistemicAction.MEASURE,
        EpistemicAction.EXPERIMENT,
        EpistemicAction.CHALLENGE,
    }
)


@dataclass(frozen=True, slots=True)
class FrontierObstruction:
    obstruction_id: str
    problem_id: str
    witness_ids: tuple[str, ...]
    responsibility_hypothesis_ids: tuple[str, ...]
    discriminator_ids: tuple[str, ...]
    lower_level_disposition_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.obstruction_id.strip() or not self.problem_id.strip():
            raise ValueError("frontier obstructions require identities")
        object.__setattr__(self, "witness_ids", _ids(self.witness_ids, name="witness_ids"))
        object.__setattr__(
            self,
            "responsibility_hypothesis_ids",
            _ids(self.responsibility_hypothesis_ids, name="responsibility_hypothesis_ids"),
        )
        object.__setattr__(self, "discriminator_ids", _ids(self.discriminator_ids, name="discriminator_ids"))
        object.__setattr__(
            self,
            "lower_level_disposition_ids",
            _ids(self.lower_level_disposition_ids, name="lower_level_disposition_ids", allow_empty=True),
        )

    @property
    def is_witnessed(self) -> bool:
        return bool(self.witness_ids and self.responsibility_hypothesis_ids and self.discriminator_ids)


@dataclass(frozen=True, slots=True)
class FrontierEpisode:
    episode_id: str
    problem_id: str
    capability_context: CapabilityContext
    obstruction: FrontierObstruction
    admissible_actions: tuple[EpistemicAction, ...]

    def __post_init__(self) -> None:
        if not self.episode_id.strip() or not self.problem_id.strip():
            raise ValueError("frontier episodes require identities")
        if self.obstruction.problem_id != self.problem_id:
            raise ValueError("frontier obstruction must belong to the episode problem")
        actions = tuple(EpistemicAction(action) for action in self.admissible_actions)
        if not actions or len(actions) != len(set(actions)):
            raise ValueError("admissible_actions must be non-empty and unique")
        object.__setattr__(self, "admissible_actions", actions)


class FrontierRouteStatus(StrEnum):
    EXISTING_CONTROL_ACTION = "EXISTING_CONTROL_ACTION"
    JUMP_ASSESSMENT_REQUIRED = "JUMP_ASSESSMENT_REQUIRED"
    BLOCKED_UNWITNESSED_OBSTRUCTION = "BLOCKED_UNWITNESSED_OBSTRUCTION"
    BLOCKED_LOWER_LEVEL_UNRESOLVED = "BLOCKED_LOWER_LEVEL_UNRESOLVED"
    SAFE_ABSTAIN = "SAFE_ABSTAIN"


@dataclass(frozen=True, slots=True)
class FrontierActionRoute:
    action: EpistemicAction
    status: FrontierRouteStatus
    jump_level: JumpLevel | None
    reason: str
    scientific_truth_authorized: bool = False
    superiority_authorized: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", EpistemicAction(self.action))
        object.__setattr__(self, "status", FrontierRouteStatus(self.status))
        if self.jump_level is not None:
            object.__setattr__(self, "jump_level", JumpLevel(self.jump_level))
        if not self.reason.strip():
            raise ValueError("frontier routes require a reason")
        if self.scientific_truth_authorized or self.superiority_authorized:
            raise ValueError("frontier routing is non-authorizing")


def _jump_level_for_action(
    action: EpistemicAction,
    transform_scope: RegimeTransformScope | None,
) -> JumpLevel | None:
    if action in _DIRECT_ACTIONS:
        return None
    if action is EpistemicAction.CHANGE_MODEL:
        return JumpLevel.MODEL_HYPOTHESIS_EXPANSION
    if action in {EpistemicAction.CHANGE_REPRESENTATION, EpistemicAction.CHANGE_PERSPECTIVE}:
        return JumpLevel.REPRESENTATION_REGIME_TRANSITION
    if action is EpistemicAction.REFORMULATE_PROBLEM:
        return JumpLevel.PROBLEM_OBJECTIVE_REFORMULATION
    if action is EpistemicAction.BUILD_TOOL:
        return JumpLevel.METHOD_TOOL_INSTRUMENT_INVENTION
    if action is EpistemicAction.CHANGE_WORKFLOW:
        return JumpLevel.WORKFLOW_META_SKILL_REVISION
    if action is EpistemicAction.TRANSFORM_REGIME:
        if transform_scope is None:
            raise ValueError("TRANSFORM_REGIME requires an explicit transform_scope")
        return _SCOPE_JUMP_LEVEL[RegimeTransformScope(transform_scope)]
    if action is EpistemicAction.ABSTAIN:
        return None
    raise ValueError(f"unhandled epistemic action: {action}")


def route_frontier_action(
    episode: FrontierEpisode,
    action: EpistemicAction,
    *,
    transform_scope: RegimeTransformScope | None = None,
) -> FrontierActionRoute:
    """Route an action to existing control or the witnessed-Jump interface.

    This function does not decide that a Jump is valid.  A route with
    ``JUMP_ASSESSMENT_REQUIRED`` must still be materialized as a
    :class:`orion_v2.jump.JumpTrigger` / :class:`orion_v2.jump.JumpProposal` and
    pass the existing protected assessment machinery.
    """

    action = EpistemicAction(action)
    if action not in episode.admissible_actions:
        raise ValueError("action is not admissible under this frontier episode")
    if action is EpistemicAction.ABSTAIN:
        return FrontierActionRoute(
            action,
            FrontierRouteStatus.SAFE_ABSTAIN,
            None,
            "abstention preserves unresolved frontier obligations without fabricating progress",
        )

    jump_level = _jump_level_for_action(action, transform_scope)
    if jump_level is None:
        return FrontierActionRoute(
            action,
            FrontierRouteStatus.EXISTING_CONTROL_ACTION,
            None,
            "action remains inside the registered repertoire and is handled by existing scientific-control parents",
        )
    if not episode.obstruction.is_witnessed:
        return FrontierActionRoute(
            action,
            FrontierRouteStatus.BLOCKED_UNWITNESSED_OBSTRUCTION,
            jump_level,
            "a frontier-space transformation requires a witnessed obstruction and discriminator",
        )
    if not episode.obstruction.lower_level_disposition_ids:
        return FrontierActionRoute(
            action,
            FrontierRouteStatus.BLOCKED_LOWER_LEVEL_UNRESOLVED,
            jump_level,
            "lower-level repair or expansion has not yet been dispositioned",
        )
    return FrontierActionRoute(
        action,
        FrontierRouteStatus.JUMP_ASSESSMENT_REQUIRED,
        jump_level,
        "route the witnessed transformation through the existing Jump assessment; this route does not authorize adoption",
    )
