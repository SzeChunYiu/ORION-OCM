"""Perishable derivation: when postponing stops being free.

This module is experiment ``E12``.  It runs the prediction that ``synthesis.py``
FROZE INTO ITS COMMITMENT DIGEST before this world existed:

    PERISHABLE_EVIDENCE, coordinates rho=True beta=True phi=True, predicted
    MACHINE.  ``beta`` is TRUE even though the store is unbounded, because beta
    is scarcity of the resource the structure economizes, and here that resource
    is the OPPORTUNITY to derive cheaply, which perishes.  If this world returns
    PARENT_SUFFICIENT then beta is specifically about bounded storage, the three
    coordinates are not the right three, and the law is a caching result with an
    inflated name.

That is the whole point of running it.  The prediction is uncomfortable rather
than safe: every instinct built up over E3, E6, E7 and E10 says acquisition
loses, and four receipts say so.  The law says it wins here.  One of them is
wrong and this module finds out which.

The world
---------

E10's world unchanged -- ``R`` rules each generating ``m`` answers -- with two
differences, and only two, so that a reversal cannot be attributed to a redesign:

    THE STORE IS UNBOUNDED.  Bits are free and nothing is ever evicted.  This
    deliberately switches OFF the coordinate E10 switched on, so that E12 cannot
    be read as a repeat of E10 under another name.  Under free unbounded storage
    the folklore answer is to keep everything you derive, and ``memoizer_parent``
    does exactly that; it is the parent to beat.

    DERIVATION PERISHES.  The cost of deriving an answer for the first time is
    ``DERIVE_COST * (1 + lam * t / H)``.  At ``lam = 0`` this is E10's constant
    cost and the earlier negatives must reproduce; the sweep includes it as the
    anti-rigging control and a run in which they do not reproduce is VOID.

What is actually being tested
-----------------------------

With storage free, a memoizer never forgets, so the only thing it can be beaten
on is an answer it has NEVER DERIVED.  That is the whole mechanism:

    a memoizer holds instances of what it has seen;
    a generalizer holds rules that cover what it has not.

When deriving gets more expensive over time, first contact with a novel answer is
the cost that matters, and a rule acquired early pre-pays for its entire
extension at the cheap early price.  The demand stream keeps introducing novel
answers throughout, so this is a live cost for the whole run rather than a
start-up effect.

``clairvoyant_memoizer_parent`` is the strongest instance-shaped parent
available: it is shown the entire future and derives, at ``t = 0`` when
derivation is cheapest, exactly the answers that will be demanded.  No instance
policy can do better, since it buys the right set at the best price.  The
generalizer can still beat it, but only by compression -- ``K_INDUCE``
derivations plus one induction per rule against ``m`` derivations -- which makes
phi's role in the law explicit and checkable rather than asserted.

And the second question, which is not the law's
-----------------------------------------------

``eager_all_rules_parent`` acquires every rule at ``t = 0`` before seeing any
demand.  That is the acquisition schedule that lost in E3, E6, E7 and E10, and it
is here because ``ROOT_CAUSE_ANALYSIS_V1`` attaches this exact falsifier to the
deep root ``EAGER_ACQUISITION_IS_DOMINATED_BY_DEFERRED_ACQUISITION``:

    Build a world where evidence is perishable or re-derivation is strictly more
    expensive later, and show eager acquisition still loses. If it wins there,
    the finding is scoped to retainable evidence rather than general.

So E12 answers two questions with one run, and they can disagree.  The law asks
whether the demand-triggered machine beats the parents.  The deep root asks
whether the untriggered eager parent beats the demand-triggered machine.  Both
verdicts are reported, and if eager wins the deep root is narrowed against the
machine, which is a result this module is required to state plainly rather than
bury under the first one.

Limitations, stated before any number
-------------------------------------

* Perishability is a deterministic ramp in wall-position, not a stochastic decay
  and not an outright loss of the ability to derive. A world where evidence
  becomes UNOBTAINABLE rather than dearer is strictly harsher and is not run.
* Storage being free is an idealisation in the opposite direction from E10's.
  Neither is realistic; the pair of them bracket the real case and neither alone
  should be quoted as it.
* Rules are disjoint, uniform, and induced without error, exactly as in E10, so
  every limitation E10 declared applies here unchanged.
* Nothing here is new machinery. Memoization is folklore; pre-computation under
  a rising price is inventory theory; holding a generator instead of its outputs
  is library learning and MDL model selection. The contribution is the frozen
  prediction and the parent set, not any component.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from prereg import Commitment, commit
from retain import (APPLY_COST, DERIVE_COST, INDUCE_COST, K_INDUCE, LOOKUP_COST,
                    World, build_world, demand_stream)

__all__ = ["PERISH_PLAN", "COMMITMENT", "derive_cost_at", "PerishWorld",
           "build_perish_world", "SYNTHESIS_PREDICTION"]


#: The prediction this module exists to test, copied from synthesis.OUT_OF_SAMPLE
#: so that a test can assert the two have not drifted apart.
SYNTHESIS_PREDICTION = "MACHINE"


def derive_cost_at(step: int, horizon: int, lam: float) -> float:
    """First-contact derivation cost at position ``step``.

    Linear in position so that the ramp has no free shape parameter beyond
    ``lam`` itself, and ``lam = 0`` is exactly E10's constant cost.
    """
    return DERIVE_COST * (1.0 + lam * (step / horizon))


@dataclass(frozen=True)
class PerishWorld:
    base: World
    lam: float
    horizon: int

    def derive(self, step: int) -> float:
        return derive_cost_at(step, self.horizon, self.lam)


def build_perish_world(rule_count: int, extension: int, lam: float,
                       horizon: int) -> PerishWorld:
    return PerishWorld(build_world(rule_count, extension), lam, horizon)


PERISH_PLAN: Mapping[str, Any] = {
    "study_id": "PERISH_E12_V1",
    "programme": "SzeChunYiu/ORION-OCM#143",
    "constitution": "SzeChunYiu/ORION-OCM#144",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "tests_frozen_prediction_from": "SYNTHESIS_V1.json, out_of_sample.PERISHABLE_EVIDENCE",
    "frozen_prediction": SYNTHESIS_PREDICTION,
    "also_runs": (
        "the unrun half of the falsifier attached to the deep root "
        "EAGER_ACQUISITION_IS_DOMINATED_BY_DEFERRED_ACQUISITION in ROOT_CAUSE_ANALYSIS_V1"),
    "scientific_question": (
        "When the store is unbounded and free but the OPPORTUNITY to derive cheaply "
        "perishes, does a demand-triggered generalizer beat a memoizer that never forgets -- "
        "including a clairvoyant memoizer that buys the exact right instances at the "
        "cheapest possible moment?"
    ),
    "evidence_class": "E2",
    "contribution_level": "L1",
    "decisive_causal_question": (
        "lam is the only knob. At lam = 0 the world is E10's with an unbounded store, where "
        "keeping everything is optimal and the prior negatives must reproduce. Any reversal "
        "at lam > 0 is caused by perishability or by nothing."
    ),
    "strongest_parent_attack": (
        "clairvoyant_memoizer_parent sees the entire future and derives exactly the answers "
        "that will be demanded, at step 0, when derivation is cheapest. No instance-shaped "
        "policy can beat it: it buys the right set at the best price. If the generalizer "
        "comes in under it, the difference is compression and not scheduling, because the "
        "parent's schedule is optimal by construction."
    ),
    "prior_information_audit": {
        "generalizing_arm": "past demands only",
        "memoizer_parent": "past demands only; unbounded store, never forgets",
        "clairvoyant_memoizer_parent": "THE ENTIRE FUTURE DEMAND STREAM",
        "eager_all_rules_parent": "no demands at all; acquires before seeing anything",
        "lazy_parent": "nothing retained",
        "oracle_rule_parent": "every rule free, no derivation and no induction charged",
    },
    "capability_gate": (
        "Every arm serves every demand, by deriving when it holds nothing, so correctness is "
        "1.0 everywhere and the work comparison is admissible under section 7. Asserted in "
        "the tests."
    ),
    "pilot_disclosure": (
        "A one-replicate PILOT was run before this plan was frozen, at extension 32 only, "
        "and it FAILED ITS OWN CONTROL: the arm beat the memoizer at lam = 0 by a factor of "
        "two, which the first version of this plan had registered as voiding the run. The "
        "reason was a design error, and it is worth stating because it also corrects the "
        "synthesis law's reasoning. The first plan asserted that with free storage 'keeping "
        "everything is optimal'. That is false. Compression reduces the number of "
        "DERIVATIONS, not merely the number of bits, so at extension 32 a rule buys 32 "
        "answers for 3 derivations and wins whether or not derivation perishes. The world "
        "did not isolate perishability at all. So extension is now a SWEPT AXIS rather than "
        "a fixed setting, the control is an exact arithmetic prediction rather than an "
        "assertion, and the protected sweep runs on a seed disjoint from the pilot. The "
        "pilot's numbers are published under 'pilot' and are not pooled."),
    "analytic_control": (
        "Whether a rule beats memoizing its own extension is exact arithmetic at lam = 0. "
        "Over u demands falling in one rule of extension m, the memoizer pays "
        "m*DERIVE + (u-m)*LOOKUP and the generalizer pays K*DERIVE + INDUCE + (u-K)*APPLY. "
        "Since APPLY exceeds LOOKUP, a rule is cheaper to ACQUIRE and dearer to USE, so the "
        "sign depends on both m and u and flips in both directions across the swept grid. "
        "The lam = 0 row of the sweep is checked against this formula, computed from the "
        "cost constants alone with no reference to the run."),
    "predictions_frozen_before_execution": {
        "P1_control": (
            "At lam = 0 the observed sign of arm-versus-memoizer matches the analytic "
            "break-even at every extension in the grid. This is a control against an exact "
            "formula, not against an intuition, and the previous version of this plan got "
            "the intuition wrong. If the observed and analytic signs disagree, the harness "
            "is not implementing the cost model it declares and the run is VOID."),
        "P2_frozen_prediction": (
            "Perishability SHIFTS THE BOUNDARY: at every extension where the arm loses at "
            "lam = 0, there is a lam at which it wins, and the crossover extension m* is "
            "non-increasing in lam. This is the synthesis law's out-of-sample prediction "
            "made quantitative -- the earlier binary form was untestable here, because the "
            "arm wins at large extension for a compression reason that has nothing to do "
            "with perishability, which is exactly what the pilot exposed."),
        "P3_against_the_clairvoyant": (
            "At sufficiently large lam the arm also beats clairvoyant_memoizer_parent, "
            "because compression buys the extension for K_INDUCE derivations instead of m. "
            "If it never does, the win in P2 is against a weak parent and must be reported "
            "that way."),
        "P4_ceiling": (
            "The arm does not beat oracle_rule_parent, which is handed every rule free. If "
            "it does, the ceiling is wrong and the run is void."),
        "P5_the_deep_roots_question": (
            "eager_all_rules_parent, the schedule that lost in E3, E6, E7 and E10, beats the "
            "demand-triggered arm at large lam. Registered in THAT direction on purpose: it "
            "is the outcome least flattering to the machine, and if it holds, the deep root "
            "is narrowed against the machine and that is the headline."),
    },
    "kill_criterion": (
        "If the crossover extension m* does not fall as lam rises, perishability is not "
        "doing the work and the frozen out-of-sample prediction is REFUTED. beta is then "
        "specifically about bounded storage rather than about scarcity of the economized "
        "resource, the synthesis law's three coordinates are not the right three, and "
        "SYNTHESIS_V1 must be demoted to a caching result. That is to be reported in those "
        "words. Note that a win at large extension alone does NOT confirm anything: the "
        "pilot already produced one and it was an artifact of compression, not of "
        "perishability."
    ),
    "sweep": {
        "rule_count": 16,
        "extensions": [4, 8, 16, 32],
        "horizon": 2000,
        "lams": [0.0, 1.0, 4.0, 16.0],
        "skew": 1.0,
        "reps": 8,
    },
    "why_these_settings": (
        "Extension is swept because it is the axis the pilot showed was confounded with "
        "perishability: the arm wins at large extension for a compression reason alone. The "
        "grid spans both sides of the analytic break-even, so the lam = 0 row contains "
        "losses as well as wins and the control has something to control. The answer space "
        "runs from 64 to 512 against a horizon of 2000, so novel answers keep arriving and "
        "first-contact cost stays live rather than being a start-up effect. lam = 0 is not "
        "optional."
    ),
    "costs": {"derive": DERIVE_COST, "apply": APPLY_COST, "lookup": LOOKUP_COST,
              "induce": INDUCE_COST, "k_induce": K_INDUCE},
    "what_this_does_not_establish": (
        "Perishability is a deterministic ramp, not decay and not an outright loss of the "
        "ability to derive. Storage is free, which is an idealisation in the opposite "
        "direction from E10's bounded store; the two bracket the real case and neither "
        "alone is it. Rules are disjoint, uniform and induced without error. A single "
        "out-of-sample point confirms a law far less than a failure would refute it."
    ),
    "novelty": (
        "NONE CLAIMED. Memoization is folklore, pre-computation under a rising price is "
        "inventory theory, holding a generator rather than its outputs is library learning "
        "and MDL. The contribution is the frozen prediction and the parent set."
    ),
}

COMMITMENT: Commitment = commit(PERISH_PLAN)
