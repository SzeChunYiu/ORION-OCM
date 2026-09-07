"""Grounded interaction learner (M5 E3; theory batch 3 C6 / MEG-15): communicative outcomes as
discriminating-interaction certificates, never as reward.

KS-T18 says feedback never warrants.  Interaction *can* teach when the outcome of an utterance is
an OBSERVATION about a *registered outcome function* (a sandbox: "the robot's action after the
utterance", "which object the listener picked"): each observed outcome eliminates hypotheses in a
version space over interpretations/constructions (the elimination is sound iff the outcome
function is registered — a hostile is an unregistered "success" bit).  The procedure atom that is
finally admitted keeps a feedback-free warrant: the ⊗ of the outcome observations that pinned it
(they are OBSERVATION evidence about the world, not preference).

Objects: `OutcomeFunction` (registered id + evaluator), `InteractionEpisode` (utterance, hypothesis
predictions, observed outcome, evidence id), `interaction_learn` (version space over a finite class
of hypotheses with per-input warrants, reusing the M2 learner's rules).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

from ocm.kso.warrant import WarrantProfile, meet_all_profiles
from ocm.learning.learner import Experience, ExperienceKind, UpdateKind, UpdateProposal, UpdateStatus, VersionSpaceLearner


@dataclass(frozen=True)
class OutcomeFunction:
    outcome_id: str
    description: str
    evaluate: Callable[[Hashable, str], Hashable]      # (hypothesis, utterance) → predicted outcome
    registered: bool = True


@dataclass(frozen=True)
class InteractionEpisode:
    utterance: str
    observed: Hashable                                   # what the registered outcome function returned in the world
    evidence_id: str                                     # OBSERVATION evidence for that outcome
    outcome_id: str


class UnregisteredOutcome(ValueError):
    pass


def interaction_learn(class_: Mapping[str, Hashable], outcome: OutcomeFunction, episodes: Sequence[InteractionEpisode], query_family: Sequence[str], *, learner_id: str = "interaction") -> UpdateProposal:
    """Version-space elimination by outcome observations.  Each episode is an INTERACTION experience
    whose pairs are (utterance, observed outcome); hypothesis h predicts outcome(h, utterance)."""
    if not outcome.registered:
        raise UnregisteredOutcome(outcome.outcome_id)
    hyps = {name: (lambda u, h=h: outcome.evaluate(h, u)) for name, h in class_.items()}
    lr = VersionSpaceLearner(learner_id, hyps, tuple(query_family))
    for i, ep in enumerate(episodes):
        if ep.outcome_id != outcome.outcome_id:
            raise UnregisteredOutcome(f"episode outcome {ep.outcome_id} ≠ {outcome.outcome_id}")
        lr.observe(Experience(f"ep{i}", ExperienceKind.INTERACTION, ep.evidence_id, learner_id, {"pairs": [(ep.utterance, ep.observed)]}, "world"))
    return lr.propose_updates()[-1]


@dataclass(frozen=True)
class SuccessBit:
    """An unregistered 'it worked' signal (FEEDBACK): admissible for behaviour weights only."""

    utterance: str
    success: bool
    evidence_id: str


def feedback_only(class_: Mapping[str, Hashable], bits: Sequence[SuccessBit], query_family: Sequence[str], *, learner_id: str = "feedback") -> UpdateProposal:
    """Success bits reach the learner as FEEDBACK: the learner may adjust behaviour but never
    admits an object (KS-T18) — returned proposal is BEHAVIOUR or a gap, never OBJECT."""
    hyps = {name: (lambda u, h=h: h) for name, h in class_.items()}
    lr = VersionSpaceLearner(learner_id, hyps, tuple(query_family))
    for i, b in enumerate(bits):
        lr.observe(Experience(f"fb{i}", ExperienceKind.FEEDBACK, b.evidence_id, learner_id, {"pairs": [(b.utterance, b.success)]}, "user"))
    return lr.propose_updates()[-1]


def mutant_success_bit_as_observation(class_: Mapping[str, Hashable], bits: Sequence[SuccessBit], query_family: Sequence[str], predicted_success: Callable[[Hashable, str], bool]) -> UpdateProposal:
    """Planted (M5 §17 / KS-T18): treat an unregistered success bit as if it were a registered
    outcome observation, so preference eliminates hypotheses and warrants an object."""
    fake = OutcomeFunction("success#unregistered", "planted", predicted_success, registered=True)
    eps = [InteractionEpisode(b.utterance, b.success, b.evidence_id, fake.outcome_id) for b in bits]
    return interaction_learn(class_, fake, eps, query_family, learner_id="mutant")
