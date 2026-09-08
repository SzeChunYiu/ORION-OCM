"""X1: does the DEV-5 mechanism transfer to a domain someone else built?

DEV-5 found that this lane had been using a needlessly strong rule for when a
learner may act on an incomplete hypothesis space:

    act only when the space has collapsed to ONE candidate  (singleton)
    act whenever the space DETERMINES the answer to this question  (unanimity)

The second is sound for the same reason as the first and fires far more often,
and switching to it bought a factor of up to 5.1 in DEV-5.  The obvious worry is
that this is a fact about guards over periodic predicates rather than about
learners, so the doctrine's S3 asks for the same computational contract to
survive a change of domain.

It does, and the evidence was already in the repository before DEV-5 existed.

``support_arms._enumerate_minimal`` -- E6's minimal-support enumerator, written by
a different author for a different question, over a subset lattice rather than a
predicate space -- contains this::

    for candidate in subsets_of(universe):
        if determined(candidate):
            continue

``determined`` is the unanimity rule under another name: it skips a subset whose
answer is already implied by what earlier answers established, instead of paying
an intervention to ask.  Same abstract move, different domain, different
implementer, different resource being saved -- interventions rather than scope
checks.

So the transfer test is not a new world, it is an ABLATION.  Delete that rule
from E6's arm and measure what E6 loses.  If it loses a comparable factor, the
contract is domain-neutral in the sense S3 requires; if it loses nothing, then
what DEV-5 found is a property of guards and the cross-domain claim fails.

Fidelity
--------

The ablated enumerator is not re-implemented.  It is E6's own source, retrieved
with ``inspect.getsource`` and transformed by exactly one textual substitution,
then compiled in E6's own module namespace.  A test asserts that the two sources
differ by exactly the declared line, so the comparison cannot drift as E6's
implementation changes and cannot be contaminated by a rewrite of mine.

What this also audits
---------------------

E6's pruning has never been independently checked for soundness.  ``determined``
skips work on the grounds that the answer is implied; if that reasoning were
wrong, E6's arm would be reporting support families it did not establish.  The
ablated arm asks every question rather than inferring any, so its families are
what exhaustive interrogation yields.  If the two disagree, E6's result needs
re-examination -- and that check is registered here as a prediction rather than
offered afterwards as a reassurance.
"""

from __future__ import annotations

import inspect
from typing import Any, Mapping

import support_arms as SA
from scaling import TouchLedger

__all__ = ["ABLATION_SUBSTITUTION", "build_ablated_enumerator", "AblatedAdaptiveArm",
           "source_diff", "X1_PLAN"]


#: The one line the ablation removes, and what it becomes.
ABLATION_SUBSTITUTION = (
    "            if determined(candidate):\n                continue\n",
    "            if USE_DETERMINED and determined(candidate):\n                continue\n",
)


def source_diff() -> tuple[str, str]:
    """The original and ablated sources, for a test to compare line by line."""
    original = inspect.getsource(SA._enumerate_minimal)
    before, after = ABLATION_SUBSTITUTION
    if original.count(before) != 1:
        raise RuntimeError(
            "E6's enumerator no longer contains the pruning line this ablation is defined "
            "against; the transfer test is stale and must not be run as if it were current")
    return original, original.replace(before, after)


def build_ablated_enumerator(use_determined: bool):
    """Compile E6's enumerator with the pruning rule switchable.

    Compiled in E6's own module globals, so every helper it calls is E6's and
    not a copy of mine.
    """
    _original, ablated = source_diff()
    namespace: dict[str, Any] = dict(vars(SA))
    namespace["USE_DETERMINED"] = use_determined
    exec(compile(ablated, "<ablated-enumerate-minimal>", "exec"), namespace)
    return namespace["_enumerate_minimal"]


class AblatedAdaptiveArm(SA.AdaptiveArm):
    """E6's arm with the unanimity rule removed and nothing else changed."""

    arm_id = "adaptive_arm_without_unanimity"
    role = "ABLATION"
    discovery = "adaptive group ablation with the determined-skip removed"

    def _discover(self, ledger: TouchLedger) -> None:
        enumerate_minimal = build_ablated_enumerator(False)
        for method_id in self._methods(ledger):
            candidates = self._candidates(method_id, ledger)

            def breaks(removed, _m=method_id):
                return self._breaks(_m, removed, ledger)

            family, exhausted = enumerate_minimal(breaks, candidates, ledger)
            if exhausted:
                self.budget_exhausted_methods.add(method_id)
            for support_set in family:
                self._file(method_id, support_set)


X1_PLAN: Mapping[str, Any] = {
    "study_id": "X1_UNANIMITY_TRANSFER_V1",
    "programme": "SzeChunYiu/ORION-OCM#143, #145",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md, section S3 cross-domain invariance",
    "responds_to": "results/DEV5_UNANIMITY_V1.json",
    "scientific_question": (
        "Is 'act wherever the hypothesis space already determines this question, rather "
        "than waiting for it to collapse' a fact about guards, or a domain-neutral contract? "
        "E6 contains the same move, written by a different author for support families over "
        "a subset lattice. Ablate it there and measure what is lost."),
    "evidence_class": "E2",
    "contribution_level": "L1",
    "why_this_is_a_transfer_test_and_not_a_restatement": (
        "The domain, the implementer, the represented object and the resource being saved "
        "all differ. DEV-5 saves scope checks against a version space of periodic "
        "predicates; E6 saves interventions against a lattice of evidence subsets. The "
        "mapping between them is a sentence -- 'skip the question whose answer is already "
        "implied' -- and it contains no part of either solution, which is what doctrine S3 "
        "requires of a cross-domain claim."),
    "fidelity": (
        "The ablated enumerator is E6's own source, retrieved with inspect and transformed "
        "by exactly one textual substitution, compiled in E6's module namespace. A test "
        "asserts the two sources differ by exactly that line. Nothing here is a "
        "re-implementation, so the measurement cannot be contaminated by a rewrite."),
    "predictions_frozen_before_execution": {
        "X1": ("The ablated arm returns IDENTICAL support families to E6's arm. The pruning "
               "rule only skips questions whose answers are implied, so it cannot change "
               "the answer. If the families differ, E6's pruning is UNSOUND and E6's result "
               "needs re-examination -- that is the more important outcome and it is "
               "registered here rather than offered afterwards."),
        "X2": ("The ablated arm spends strictly MORE interventions, because every skipped "
               "question becomes a purchased one."),
        "X3": ("The ablated arm spends FEWER predicate evaluations, because `determined` "
               "charges for the reasoning it does. The mechanism trades reasoning for "
               "interventions and E6 already meters both, so this is a real trade and not a "
               "free lunch."),
        "X4": ("Total counted work is HIGHER for the ablated arm: the interventions it buys "
               "cost more than the reasoning it saves. If total work is LOWER, the "
               "mechanism is a loss on E6's own two-column accounting and the cross-domain "
               "claim fails in the direction that matters."),
    },
    "kill_criterion": (
        "If the ablation costs E6 nothing on interventions or on total work, the move is "
        "inert in this domain, DEV-5's factor is a property of guards over periodic "
        "predicates, and the S3 cross-domain claim is REFUTED. That is to be reported in "
        "those words."),
    "two_column_rule": (
        "E6's rule applies unchanged: interventions and total counted operations are "
        "reported side by side and never summed. The mechanism is expected to improve one "
        "and worsen the other, which is exactly the shape E6 was built to expose."),
    "what_this_does_not_establish": (
        "Two domains is not domain-neutrality. Both are synthetic, both are in this "
        "repository, and both were built to study structure discovery, so they are more "
        "alike than a genuine cross-domain test would demand. What the test does have is "
        "independence of implementation: E6's enumerator was written for another question "
        "by another author before DEV-5 existed, so its use of the rule is not evidence "
        "arranged after the fact."),
    "novelty": (
        "NONE CLAIMED. Skipping implied queries is standard lattice pruning and is as old "
        "as version spaces. The contribution is measuring what it is worth, in a domain "
        "where it was already present and never priced."),
}
