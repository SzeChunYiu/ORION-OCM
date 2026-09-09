"""Learned probe semantics: the machine is no longer told what its instruments mean.

This module is experiment ``E11``.  It exists to discharge the one negative in
``NEGATIVE_DISPOSITION_V1`` that had been left as a standing decision rather than
a repair, ``N8-DIAGNOSIS-RESIDUAL``, whose why-chain terminates on
``PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED`` and whose receipt says:

    probe semantics were authored, so each episode was table inversion under a
    cost constraint

E2 is precise about where the authoring lives.  ``diagnosis.expected_outcome`` is
a hand-written function from ``(cause, probe)`` to the observation the probe
returns, and every arm in E2 -- the governed policy, the decision tree, the
parents -- consults it.  Given that table, diagnosis is inverting a known matrix
while paying for columns, which is a real problem and is not the problem the
programme claims to be studying.  E2's own residual was 42 probe units of 573,
identified exactly as memoisation of one boolean per checker and scope, and no
amount of better search inside E2 could have made it larger, because there was
nothing left in that world to learn.

E11 withdraws the table.

The world
---------

A hidden semantics matrix ``S[probe][cause] -> bool``, drawn per world, plus the
same latent scope variable E2 had: exactly one probe answers a question about the
``(checker, scope)`` pair rather than about the case, and which probe that is, is
also hidden.  An arm observes only what it buys: it runs a probe on a case and
receives a bit.  After a case is resolved, the true cause is revealed -- that is
the only supervision, it arrives after the diagnosis has been committed, and it
is counted.

E2's registered table is one point in this space and is included in the draw as
``REGISTERED_WORLD``, so E11 contains E2's world rather than replacing it.

What is actually under test
---------------------------

Not "can a machine learn a table" -- of course it can.  The question is whether
representing SEMANTICS pays over representing the input-output MAPPING, which is
the same question the programme has been asking everywhere else in a form where
it can finally be answered cleanly:

    ``semantics_learner``    induces ``S``, one cell at a time, and diagnoses by
                             inverting what it has induced.  Its hypothesis space
                             is ``2 ** (probes * causes)`` but its EVIDENCE is
                             per-cell: one resolved case with a known cause and
                             three bought probes fills three cells.
    ``mapping_parent``       ignores semantics entirely and learns
                             ``P(cause | outcome vector)`` as a lookup table over
                             the ``2 ** probes`` vectors it has actually seen.
                             This is the obvious, strong, standard thing to do
                             and it needs no notion of what a probe means.

Both converge.  If they converge at the same rate, semantics buy nothing, the
terminal is ``PARENT_SUFFICIENT``, and N8's prescribed fix is refuted rather than
completed -- which is a legitimate and reportable outcome, registered here before
the run.

The discriminating coordinate is therefore SAMPLE EFFICIENCY, not accuracy:
resolved cases needed to reach a registered accuracy target.  The prediction that
makes it a causal claim rather than a curve-fit is compositional:

    **PROBE EXTENSION.**  Half way through the lifetime a SIXTH probe is added.
    The semantics learner has to fill one new column, five cells.  The mapping
    parent's table is indexed by outcome vectors, so every row it holds is now a
    prefix of two rows it does not, and it has to re-earn them.  If semantics are
    doing real work, the gap opens at the extension and does not close.

If instead the gap does not open there, then whatever the semantics learner is
doing is not compositional, and saying so is more useful than the headline.

Limitations, stated before any number
-------------------------------------

* Semantics here are DETERMINISTIC and noise-free: a probe's bit is a function of
  the cause and the scope variable.  Real instruments are noisy, and a noisy
  table is a strictly harder induction problem that this module does not attempt.
  The mapping parent is hurt more by noise than the semantics learner in theory,
  so this omission is if anything unfavourable to the parent and is declared.
* The cause is revealed on resolution.  A world where the true cause is never
  revealed is the honest hard case and is not run here; without any supervision
  neither arm learns anything and the comparison is empty.
* The probe set is small (five, then six).  Nothing here says how either arm
  scales to instrument sets where the mapping table is astronomically large,
  which is exactly where the semantics representation should win by more.
* Nothing here is new machinery.  Learning a fault dictionary is digital test
  engineering; learning ``P(cause | evidence)`` directly is a lookup classifier;
  the semantics learner is a version space over a boolean matrix, which is Mitchell
  (1982) with a cheaper update.  The contribution is the COMPARISON and the
  extension test, not any component.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from diagnosis import CAUSE_PRIOR, PROBE_COST, Cause, Probe
from prereg import Commitment, commit

__all__ = ["PROBESEM_PLAN", "COMMITMENT", "CAUSES", "BASE_PROBES", "EXTRA_PROBE",
           "EXTRA_PROBE_COST", "Semantics", "World", "draw_world",
           "REGISTERED_WORLD", "case_stream", "Case"]


#: The five causes a world may carry.  ``CANNOT_IDENTIFY`` is a verdict and never
#: a cause, exactly as in E2, so it is not in this tuple.
CAUSES: tuple[Cause, ...] = tuple(CAUSE_PRIOR)

BASE_PROBES: tuple[Probe, ...] = tuple(PROBE_COST)

#: The probe added half way through the lifetime.  It is a real sixth instrument
#: with its own hidden column, not a relabelling of an existing one.
EXTRA_PROBE: str = "CROSS_SCOPE_REPLAY"
EXTRA_PROBE_COST: int = 4


@dataclass(frozen=True)
class Semantics:
    """The hidden table.  ``table[(probe, cause)]`` is what the probe returns.

    ``scope_probe`` is the one probe that answers a question about the
    (checker, scope) pair rather than about the case: its bit is the latent
    soundness variable and does not depend on the cause at all.  Which probe that
    is, is hidden, and an arm that assumes it knows has assumed the thing E2 was
    given.
    """

    table: Mapping[tuple[str, str], bool]
    scope_probe: str

    def observe(self, probe: str, cause: Cause, checker_sound: bool) -> bool:
        if probe == self.scope_probe:
            return checker_sound
        return self.table[(probe, cause.value)]

    def column(self, probe: str) -> tuple[bool, ...]:
        return tuple(self.table[(probe, c.value)] for c in CAUSES)

    def identifiable(self, probes: Sequence[str]) -> bool:
        """Do these probes separate every pair of causes, at some scope value?"""
        seen = set()
        for cause in CAUSES:
            for sound in (True, False):
                sig = tuple(self.observe(p, cause, sound) for p in probes)
                seen.add((cause, sig))
        by_sig: dict[tuple, set[Cause]] = {}
        for cause, sig in seen:
            by_sig.setdefault(sig, set()).add(cause)
        return all(len(v) == 1 for v in by_sig.values())


def _registered_table() -> dict[tuple[str, str], bool]:
    """E2's own table, so that E11's world space CONTAINS E2's world."""
    from diagnosis import expected_outcome
    out: dict[tuple[str, str], bool] = {}
    for probe in BASE_PROBES:
        for cause in CAUSES:
            out[(probe.value, cause.value)] = expected_outcome(cause, probe, True)
    out[(EXTRA_PROBE, Cause.TRUE_REFUTATION.value)] = False
    for cause in CAUSES:
        out.setdefault((EXTRA_PROBE, cause.value), True)
    return out


REGISTERED_WORLD = Semantics(_registered_table(),
                             Probe.CHECKER_CONTROL_BATTERY.value)


@dataclass(frozen=True)
class World:
    semantics: Semantics
    #: soundness of the (checker, scope) pair; latent, constant within a world
    checker_sound: bool

    def observe(self, probe: str, cause: Cause) -> bool:
        return self.semantics.observe(probe, cause, self.checker_sound)


@dataclass(frozen=True)
class Case:
    cause: Cause


def draw_world(rng: random.Random, require_identifiable: bool = True) -> World:
    """Draw a hidden semantics table, rejecting ones no probe set could crack.

    A world whose probes cannot separate two causes even in principle makes
    ``CANNOT_IDENTIFY`` the correct answer for every arm, which measures nothing
    about learning.  Such worlds are rejected here and the rejection is declared:
    E11 is about learning a table that CAN be learned.
    """
    probes = [p.value for p in BASE_PROBES] + [EXTRA_PROBE]
    for _ in range(2000):
        table = {(p, c.value): rng.random() < 0.5 for p in probes for c in CAUSES}
        scope_probe = rng.choice([p.value for p in BASE_PROBES])
        sem = Semantics(table, scope_probe)
        if not require_identifiable or sem.identifiable(probes):
            return World(sem, rng.random() < 0.5)
    raise RuntimeError("no identifiable world found; the draw is misconfigured")


def case_stream(length: int, rng: random.Random) -> tuple[Case, ...]:
    weights = [CAUSE_PRIOR[c] for c in CAUSES]
    total = sum(weights)
    cum, acc = [], 0.0
    for w in weights:
        acc += w / total
        cum.append(acc)
    out = []
    for _ in range(length):
        u = rng.random()
        i = 0
        while i < len(cum) - 1 and u > cum[i]:
            i += 1
        out.append(Case(CAUSES[i]))
    return tuple(out)


PROBESEM_PLAN: Mapping[str, Any] = {
    "study_id": "PROBESEM_E11_V1",
    "programme": "SzeChunYiu/ORION-OCM#143",
    "constitution": "SzeChunYiu/ORION-OCM#144",
    "discharges": "N8-DIAGNOSIS-RESIDUAL, root PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED",
    "scientific_question": (
        "When probe semantics are withdrawn, does representing WHAT A PROBE MEANS beat "
        "representing WHICH CAUSE AN OUTCOME VECTOR IMPLIES -- and if so, on which "
        "coordinate?"
    ),
    "evidence_class": "E2",
    "contribution_level": "L1",
    "decisive_causal_question": (
        "Sample efficiency at matched accuracy, and its behaviour at a probe extension. "
        "The semantics learner's evidence is per-cell, so a sixth probe costs it five "
        "cells; the mapping parent is indexed by outcome vectors, so a sixth probe "
        "invalidates the index of every row it holds. If semantics are compositional the "
        "gap opens at the extension. If it does not open there, whatever the learner is "
        "doing is not compositional and the receipt says so instead of the headline."
    ),
    "strongest_parent_attack": (
        "mapping_parent, a lookup classifier over outcome vectors. It needs no notion of "
        "what a probe means, it is what any competent engineer would write first, and on a "
        "stationary five-probe world it is expected to converge to the same accuracy. If it "
        "also converges at the same RATE, semantics buy nothing and N8's prescribed fix is "
        "REFUTED rather than completed."
    ),
    "prior_information_audit": {
        "semantics_learner": "nothing; it buys probes and is told the cause on resolution",
        "mapping_parent": "the same observations and the same revelations",
        "naive_bayes_parent": "the same, with an independence assumption imposed",
        "given_semantics_ceiling": "THE TRUE TABLE, free. E2's arm. A ceiling, not a rival",
        "random_probe_parent": "the same revelations, probes chosen at random",
        "fixed_order_parent": "the same revelations, probes in registered cost order",
    },
    "capability_gate": (
        "Arms are compared on cases-to-target-accuracy and on cumulative probe cost, and a "
        "work comparison is quoted only between arms that reached the accuracy target. An "
        "arm that never reaches it has no admissible cost figure and is reported as NOT "
        "REACHED rather than as cheap."
    ),
    "accuracy_target": 0.90,
    "scaling_relevance": (
        "The mapping table grows as 2**probes and the semantics table as probes*causes, so "
        "the predicted gap widens with the instrument set. Only five and six probes are run "
        "here, which is the regime least favourable to the semantics representation, and "
        "the receipt states that any gap found is a lower bound on the gap at scale."
    ),
    "predictions_frozen_before_execution": {
        "R1": "Both learners reach the accuracy target on the five-probe stationary world.",
        "R2": ("semantics_learner reaches it in strictly fewer resolved cases than "
               "mapping_parent."),
        "R3": ("At the probe extension the mapping parent's accuracy drops and the "
               "semantics learner's does not, and the recovery gap is larger than the "
               "pre-extension gap."),
        "R4": ("Neither learner beats given_semantics_ceiling, which is handed the table. "
               "If one does, the ceiling is implemented wrongly and the run is void."),
        "R5": ("random_probe_parent reaches the target eventually and later than both, so "
               "that probe SELECTION and probe SEMANTICS are separated: if random matches "
               "the learner, selection was never the binding constraint."),
    },
    "kill_criterion": (
        "If mapping_parent reaches the accuracy target in no more resolved cases than "
        "semantics_learner, both before and after the probe extension, then learning what a "
        "probe MEANS buys nothing over learning what an outcome IMPLIES. N8's prescribed fix "
        "is then refuted, the terminal is PARENT_SUFFICIENT, and that is reported as the "
        "headline in those words."
    ),
    "sweep": {
        "worlds": 40,
        "lifetime": 400,
        "extension_at": 200,
        "probe_budget_per_case": 3,
        "accuracy_window": 60,
        "include_registered_world": True,
    },
    "world_draw": (
        "Hidden tables are drawn uniformly over booleans and REJECTED unless the full probe "
        "set separates every pair of causes at some scope value. A world no probe set can "
        "crack makes CANNOT_IDENTIFY correct for every arm and measures nothing about "
        "learning. E2's own registered table is included in the draw, so E11's world space "
        "CONTAINS E2's world rather than replacing it."
    ),
    "novelty": (
        "NONE CLAIMED. Fault dictionaries are digital test engineering; a lookup classifier "
        "over evidence vectors is standard; the semantics learner is a version space over a "
        "boolean matrix, Mitchell 1982 with a cheaper update. The contribution is the "
        "comparison and the probe-extension test."
    ),
    "what_this_does_not_establish": (
        "Semantics here are deterministic and noise-free, the true cause is revealed on "
        "resolution, and the probe set is five then six. Noisy instruments, unsupervised "
        "resolution, and large instrument sets are all outside this world, and the first two "
        "are the conditions under which real diagnosis is hard."
    ),
}

COMMITMENT: Commitment = commit(PROBESEM_PLAN)
