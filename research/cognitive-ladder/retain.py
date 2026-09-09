"""Retention under a bit budget: does keeping generalizations beat keeping instances?

This module is experiment ``E10`` of the cognitive-ladder programme.  It exists
to run the falsifier that ``ROOT_CAUSE_ANALYSIS_V1.md`` attaches to the deep root
``EAGER_ACQUISITION_IS_DOMINATED_BY_DEFERRED_ACQUISITION``:

    Build a world where evidence is perishable or re-derivation is strictly more
    expensive later, and show eager acquisition still loses.  If it wins there,
    the finding is scoped to retainable evidence rather than general, which would
    be a narrowing and not a refutation.

Four experiments (E3, E6, E7, E8) have now shown the same thing with four
mechanisms and four parent sets, the last of them against a parent implemented
independently of the arm: acquiring structure up front loses to deriving it when
it is actually needed.  Every one of those worlds shared two properties that were
never varied because nobody had noticed they were constant:

    re-derivation was free to postpone   -- an answer derived at step 900 cost
                                            exactly what it would have cost at
                                            step 9, so waiting was never wrong;
    retention was free                   -- nothing was ever charged for holding
                                            what had been derived, and nothing
                                            ever had to be thrown away.

Under those two conditions the optimal policy is provably to retain nothing and
derive on demand, and that is exactly what the parents did.  The negatives are
correct and this module does not touch them.  What it does is vary the second
condition, because a machine whose whole proposition is persistent structure has
never once been measured in a world where persistence costs anything or is
bounded by anything.

The sharp question
------------------

Bound storage in BITS and charge for holding it.  Now retention is a decision
with a real opportunity cost, and there are two ways to spend the budget:

    keep INSTANCES        the answers themselves, one slot each
    keep GENERALIZATIONS  a rule that regenerates many answers, several slots

The hypothesis under test is representational, not procedural:

    **when the answer population is compressible, a machine that retains
    generalizations beats one that retains instances -- and it beats it even
    when the instance-keeper is allowed to see the future.**

The second half is what makes the result hard to rig.  ``belady_instance_cache``
is handed the entire future demand stream and evicts furthest-in-future, which
for uniform-size uniform-cost items is Belady's rule and is OPTIMAL: no instance
policy, online or offline, can beat it.  So if the online generalizing arm comes
in under it, the difference cannot be policy quality, cannot be luck, and cannot
be information -- the parent had strictly more.  The only remaining explanation
is what is being stored.  That is the one comparison in this programme where
PARENT_SUFFICIENT cannot be won by giving the parent a better schedule, because
the parent has already been given the best schedule that exists.

And the same construction supplies its own negative control.  At extension size
one a rule regenerates exactly one answer while costing more bits than the answer
does, so retaining rules is strictly dominated and the arm MUST lose to Belady.
That is not a hoped-for robustness check, it is arithmetic, and the plan
registers it as a prediction: if the arm wins at extension size one, the
experiment is measuring something other than compression and the whole sweep is
void.

The world
---------

``R`` latent rules, each generating ``m`` answers, disjoint, so ``F = R * m``
answers exist.  A demand stream of length ``H`` draws answers from a Zipf-like
skew over rules and uniform within a rule.  To serve a demand an arm must have
the answer:

============================  ===============================================
in the instance store         ``LOOKUP_COST``
regenerable from a held rule  ``APPLY_COST``
neither                       ``DERIVE_COST``, and derivation reveals which
                              rule the answer belongs to
============================  ===============================================

Holding ``K_INDUCE`` answers of one rule permits induction at ``INDUCE_COST``;
the induced rule then serves that rule's whole extension.  Storage is capped at
``BUDGET_BITS`` and charged at ``sigma`` per bit per step.

Every arm can serve every demand by deriving, so **correctness is 100% for every
arm by construction** and the #144 capability gate is satisfied without
argument.  This is deliberate: it makes work the only coordinate that can move,
which is the only condition under which a work comparison means anything.

What is given away, and why it is still a fair test
---------------------------------------------------

Derivation reveals rule membership.  The arm does not have to LEARN the rule from
features; it has to decide whether to PAY to keep it.  That is a gift and it is
declared rather than buried, for the same reason E6 declared that a method's
candidate evidence set is given: the question here is retention policy under a
budget, and induction difficulty is a separate axis that E5 and E11 own.  The
gift is symmetric -- ``eager_all_rules_parent`` and every instance cache receive
exactly the same revelation on exactly the same derivations -- so it cannot
favour the arm.  What it does do is make the arm's win, if it comes, a claim
about representation ONLY, with induction held at zero difficulty.  A world where
the rule must also be learned can only make the arm's position worse, never
better, and the receipt says so.

The exchange rate problem, and how it is handled rather than assumed
--------------------------------------------------------------------

This experiment must add derivation work to storage work, which the programme's
two-column rule normally forbids.  The rule is not being broken; the exchange
rate is being made into the swept variable.  ``sigma`` is the price of one bit
for one step, every result is reported as a curve over ``sigma``, and no single
``sigma`` is privileged anywhere.  Where a scalar is unavoidable the receipt
carries the whole curve beside it.  A conclusion that survives only at one
``sigma`` is reported as surviving only at one ``sigma``.

Limitations, stated before any number
-------------------------------------

* Rules are DISJOINT and uniform in extension size.  Overlapping rules, partial
  coverage, and heavy-tailed extension sizes are all outside this world, and the
  first of those is where a real library-learning system does its hardest work.
* Induction is free of error.  Nothing here measures a wrong rule, so nothing
  here measures the cost of a wrong rule, which in any real system is where the
  case for eager acquisition actually dies.
* The demand stream is stationary.  Drift is not modelled; E8 already showed
  that an arm's own staleness audit can pass while its answer is 4% low.
* Belady's rule is optimal for uniform-size uniform-cost items.  The MIXED
  clairvoyant, which may hold rules as well as instances, is a greedy heuristic
  and is NOT proven optimal; it is reported as a reference point and never as a
  ceiling, and the receipt says which of the two claims each number supports.
* Nothing here is new machinery.  Caching is Belady (1966); frequency and
  recency policies are folklore; retaining a compressed generator instead of its
  outputs is the whole of library learning (DreamCoder, Stitch) and of MDL model
  selection (Rissanen).  The contribution is the PARENT COMPARISON -- specifically
  running an online generalizer against a clairvoyant instance-optimal parent at
  a matched bit budget -- not any component.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from prereg import Commitment, canonical_json, commit

__all__ = [
    "RETAIN_PLAN",
    "COMMITMENT",
    "World",
    "Store",
    "WorkLedger",
    "build_world",
    "demand_stream",
    "DERIVE_COST",
    "APPLY_COST",
    "LOOKUP_COST",
    "INDUCE_COST",
    "FACT_BITS",
    "RULE_BITS",
    "K_INDUCE",
]


#: Cost to derive one answer from nothing.  Uniform across answers, which is what
#: makes furthest-in-future eviction provably optimal for the instance caches.
DERIVE_COST: int = 100

#: Cost to regenerate one answer from a held rule.
APPLY_COST: int = 10

#: Cost to serve one answer already held as an instance.
LOOKUP_COST: int = 1

#: Cost to induce a rule once ``K_INDUCE`` of its answers have been derived.
INDUCE_COST: int = 40

#: Answers of one rule that must have been derived before it can be induced.
K_INDUCE: int = 3

#: Bits to hold one answer.
FACT_BITS: int = 8

#: Bits to hold one rule.  Four answer-slots: a rule must regenerate more than
#: four answers before it can possibly pay for its own storage, which is the
#: crossover the sweep is looking for and is fixed here BEFORE it is measured.
RULE_BITS: int = 32


RETAIN_PLAN: Mapping[str, Any] = {
    "study_id": "RETAIN_E10_V1",
    "programme": "SzeChunYiu/ORION-OCM#143",
    "constitution": "SzeChunYiu/ORION-OCM#144",
    "scientific_question": (
        "When storage is bounded in bits and charged for, does a machine that retains "
        "GENERALIZATIONS beat one that retains INSTANCES -- including an instance-keeper "
        "that is shown the entire future?"
    ),
    "evidence_class": "E2",
    "contribution_level": "L1",
    "decisive_causal_question": (
        "Is the advantage of persistent acquired structure caused by compressibility of "
        "the answer population, or by anything else? The extension size m is the only "
        "knob that changes compressibility, every other quantity in the world is held "
        "fixed across the sweep, and the prediction is signed at m = 1 and positive above "
        "some m*."
    ),
    "strongest_parent_attack": (
        "belady_instance_cache is handed the whole future demand stream and evicts "
        "furthest-in-future. For uniform-size uniform-cost items that is Belady's rule and "
        "no instance policy can beat it. If the ONLINE arm beats it, the difference is not "
        "policy and not information -- the parent had more of both -- so the only remaining "
        "explanation is representation. If the arm does not beat it, no further parent is "
        "needed to close the question."
    ),
    "prior_information_audit": {
        "arm": "past demands only; rule membership revealed by derivations it paid for",
        "belady_instance_cache": "THE ENTIRE FUTURE DEMAND STREAM, plus the same revelations",
        "belady_mixed_reference": "the entire future stream, and may hold rules as well",
        "oracle_rule_parent": "every rule for free, no derivation and no induction charged",
        "lru_instance_cache / lfu_instance_cache": "past demands only",
        "lazy_parent": "nothing retained, so nothing to know",
        "eager_all_rules_parent": "same revelations, but acquires before demand",
        "random_retention_placebo": "same bit budget, no information used to fill it",
    },
    "scaling_relevance": (
        "Horizon H and rule count R are both swept. The prediction is that m* falls as H "
        "rises, because induction is a fixed cost amortized over demands; if m* is flat in "
        "H the mechanism is not amortization and the explanation offered here is wrong."
    ),
    "predictions_frozen_before_execution": {
        "P1_negative_control": (
            "At m = 1 a rule regenerates one answer for four answer-slots, so the arm MUST "
            "NOT beat belady_instance_cache. If it does, the sweep measures something other "
            "than compression and is VOID."
        ),
        "P2_crossover_exists": (
            "There is an m* > 1 above which the arm's total work is strictly below "
            "belady_instance_cache's at matched correctness."
        ),
        "P3_horizon": "m* is non-increasing in H.",
        "P4_ceiling": (
            "The arm does not beat belady_mixed_reference. If it does, the reference is "
            "implemented wrongly and the run is void rather than a discovery."
        ),
        "P5_placebo": (
            "Delta_purified = work(random_retention_placebo) - work(arm) > 0 wherever the "
            "arm wins, i.e. the win survives CL-D2 structural placebo subtraction."
        ),
    },
    "kill_criterion": (
        "If there is no m in the swept range at which the arm beats belady_instance_cache, "
        "the deep root is NOT narrowed: selective retention has no regime even when storage "
        "is bounded and charged, and that is a stronger negative than any recorded so far. "
        "It is to be reported as the headline in exactly those words."
    ),
    "two_column_rule": (
        "Derivation, application, lookup, induction and storage work are accumulated as "
        "SEPARATE coordinates and every table carries all five. They are summed only under "
        "the declared exchange rate sigma, and sigma is a SWEPT KNOB reported as a curve, "
        "never a fixed assumption. No conclusion is stated at one sigma without the curve."
    ),
    "capability_gate": (
        "Every arm serves every demand by deriving when it holds nothing, so correctness is "
        "1.0 for every arm at every setting. Asserted in the tests rather than assumed. Work "
        "comparison is admissible only because of this."
    ),
    "costs": {
        "derive": DERIVE_COST, "apply": APPLY_COST, "lookup": LOOKUP_COST,
        "induce": INDUCE_COST, "k_induce": K_INDUCE,
        "fact_bits": FACT_BITS, "rule_bits": RULE_BITS,
    },
    "sweep": {
        "rule_count": 16,
        "reps": 8,
        "primary_grid": {
            "extension_sizes": [1, 2, 4, 8, 16, 32], "budget_bits": [64, 256, 1024],
            "horizon": 2000, "skew": 1.0,
        },
        "horizon_slice": {
            "extension_sizes": [1, 2, 4, 8, 16, 32], "horizons": [500, 2000, 8000],
            "budget_bits": 256, "skew": 1.0,
        },
        "skew_slice": {
            "extension_sizes": [1, 2, 4, 8, 16, 32], "skews": [0.0, 1.0],
            "budget_bits": 256, "horizon": 2000,
        },
        "sigmas": [0.0, 0.001, 0.01, 0.1, 1.0],
        "sigma_is_priced_after_the_fact": (
            "Every run accumulates BIT-STEPS, the integral of held bits over the demand "
            "stream, as a raw coordinate. Storage work at any sigma is that integral times "
            "sigma, so the whole sigma curve comes from one run per arm. This is exact and "
            "not an approximation, and it is valid ONLY because no arm is sigma-aware: "
            "policies here respond to the hard bit budget and never to the price. A "
            "sigma-aware arm would hold less as sigma rose and would beat all of these at "
            "high sigma; none is implemented, and the receipt says so rather than letting "
            "the flat curve read as a finding."
        ),
    },
    "pilot_disclosure": (
        "A single-replicate PILOT was run on rng seed 1 BEFORE this plan was frozen, over "
        "extension sizes 1,2,4,8,16,32 at budgets 64,256,1024, horizon 2000, skew 1.0. It "
        "was run to check that the harness worked and that the negative control fired, and "
        "it did both. It also showed a crossover, and it showed it AT THE EDGE of the "
        "extension grid this plan originally registered (1..16), which is why 32 was added. "
        "That is a grid change made after seeing an outcome and it is disclosed here rather "
        "than hidden: it changes the commitment digest, which is the whole point of "
        "deriving the draw from the plan. The pilot numbers are reported in the receipt "
        "under 'pilot' and are NOT pooled with the protected sweep, which runs on "
        "protected_seed and is disjoint from the pilot stream by construction. If the "
        "protected sweep does not reproduce the pilot's crossover, the pilot is the "
        "artifact and the protected sweep is the result."
    ),
    "novelty": (
        "NONE CLAIMED FOR ANY COMPONENT. Belady 1966; LRU/LFU folklore; retaining a "
        "generator rather than its outputs is library learning (DreamCoder, Stitch) and MDL "
        "model selection (Rissanen). The contribution is the parent comparison: an online "
        "generalizer against a clairvoyant instance-optimal parent at a matched bit budget."
    ),
    "what_this_does_not_establish": (
        "Rules are disjoint, uniform, and induced without error, and the stream is "
        "stationary. Real library learning fails at overlap, at partial coverage, and at "
        "wrong rules, and none of those is measured here. A crossover found here is a "
        "statement about a synthetic ecology whose compressibility is set by hand, and the "
        "immediately honest next question is what m is in any domain anyone cares about."
    ),
}

COMMITMENT: Commitment = commit(RETAIN_PLAN)


@dataclass(frozen=True)
class World:
    """A population of answers generated by disjoint rules of equal extension."""

    rule_count: int
    extension: int
    #: ``rule_of[f]`` is the rule that generates answer ``f``.
    rule_of: tuple[int, ...]
    #: ``members[r]`` are the answers rule ``r`` generates.
    members: tuple[tuple[int, ...], ...]

    @property
    def answers(self) -> int:
        return len(self.rule_of)


def build_world(rule_count: int, extension: int) -> World:
    rule_of, members = [], []
    for r in range(rule_count):
        ext = tuple(range(r * extension, (r + 1) * extension))
        members.append(ext)
        rule_of.extend([r] * extension)
    return World(rule_count, extension, tuple(rule_of), tuple(members))


def demand_stream(world: World, horizon: int, skew: float, rng: random.Random) -> tuple[int, ...]:
    """Zipf-like over rules at ``skew``, uniform within a rule.

    ``skew = 0`` is uniform over rules and is the hardest setting for any cache,
    because no policy can concentrate a bounded budget on anything.  It is in the
    sweep for exactly that reason.
    """
    weights = [1.0 / ((r + 1) ** skew) for r in range(world.rule_count)]
    total = sum(weights)
    weights = [w / total for w in weights]
    cum, acc = [], 0.0
    for w in weights:
        acc += w
        cum.append(acc)
    out = []
    for _ in range(horizon):
        u = rng.random()
        r = 0
        while r < len(cum) - 1 and u > cum[r]:
            r += 1
        out.append(rng.choice(world.members[r]))
    return tuple(out)
