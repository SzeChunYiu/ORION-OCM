"""Parent absorption and the phase boundary the negatives actually draw.

Written to the doctrine in PR #150,
``research/evolvability-theory-v0/PARENT_SYNTHESIS_DOCTRINE_V0_2.md``, which
replaces the reading this lane had been operating under:

    PARENT_SUFFICIENT for mechanism X  !=  X is useless to Machine Epistemics

    It means: novelty(X) is parent-owned, X may be absorbed into the generalized
    theory, and any residual claim must move to a higher-order synthesis or a new
    prediction.

Under that doctrine this lane's seven PARENT_SUFFICIENT terminals stop being a
tally of losses and become an absorption backlog with a shape.  This module does
two things with it.

Part one: ABSORPTION.  Every parent that actually beat an arm here is recorded
with the doctrine's own lifecycle verdict -- ADOPT, ADAPT, GENERALIZE, REJECT,
OPEN -- naming the receipt that established it, what it teaches, and what novelty
claim it removes.  No parent in this lane is classified REJECT, and that is worth
saying plainly: every one of them won.

Part two, which is the part that is not bookkeeping.  Eight receipts in this lane
tested acquisition against deferral in eight different mechanisms, and the sign
of the comparison is not random.  Each experiment happens to hold two coordinates
fixed and vary a third, and read together they draw a boundary:

    an acquired structure beats deriving on demand only inside a JOINT REGIME,
    and outside it the parent wins by arithmetic rather than by being cleverer

with three coordinates:

``rho``    DEMAND.  Is the structure required again?  E7 varies this and holds
           the rest.  At rho = 0 nothing can amortize and every negative in this
           programme reproduces.
``beta``   SCARCITY of the resource the structure economizes.  E10 varies this
           for storage bits; E11 varies it for labelled cases.  This is the
           coordinate the programme had never varied: every world before E10 gave
           the economized resource away free and unbounded, and where it is free
           the optimal policy is provably to keep nothing, so the parents were
           winning against arithmetic and not against a mechanism.
``phi``    FACTORISATION of the acquired object's index.  Does evidence about it
           compose across episodes -- per instrument, per component, per rule --
           or is it indexed by whole configurations?  E11 varies this directly
           (a semantics cell against a row keyed by an outcome vector) and E8
           varies it by accident (a full transform against degree-escalating
           least squares).

``beta`` is an INTERVAL and not a threshold, and DEV-1 is what shows it.  Too
little scarcity and holding structure buys nothing because holding costs nothing.
Too much and the carried structure cannot be displaced by what the next stage
needs: at 256 bits DEV-1's lineage arrives with its budget already spent and
loses to a reset arm; at 1024 it wins. So the predicted region is an interior
band, which is the shape doctrine section S5 calls a principled boundary.

What this is and is not
-----------------------

It is a POST HOC law fitted to eight results, and it is labelled that way
everywhere it appears.  A rule that explains the data it was built from explains
nothing.  So the module ends by freezing an OUT-OF-SAMPLE prediction: coordinates
are assigned to an experiment that has not been run, the predicted sign is
committed to the plan digest, and the receipt for that experiment either confirms
it or refutes the law.  Until that runs, the honest status is CONJECTURE and
``LAW_STATUS`` says so.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Any, Mapping

from prereg import Commitment, commit

HERE = pathlib.Path(__file__).parent

__all__ = ["ABSORPTIONS", "CONDITIONS", "OBSERVED", "LAW_STATUS", "predict",
           "OUT_OF_SAMPLE", "COMMITMENT", "build"]

VERDICTS = ("ADOPT", "ADAPT", "GENERALIZE", "REJECT", "OPEN")


def A(**kw):
    base = dict(parent="", field="", receipt="", verdict="", teaches="",
                novelty_removed="", mapped_to="", prior_information_charged="",
                next_experiment="")
    base.update(kw)
    return base


#: Doctrine section 3, applied to every parent that beat an arm in this lane.
ABSORPTIONS = [
A(parent="Independent mathematical review of PR #150 (arrived as PR #153, since "
         "merged as research/evolvability-source-review-v1)", field="theory review",
  receipt="../evolvability-source-review-v1/PR150-MATH-REVIEW.md",
  verdict="GENERALIZE",
  teaches="A calibrated posterior's perplexity does not bound the expected cost of finding "
          "the right answer. With N = 2^m repairs of probability 1/(mN) and one leading "
          "repair of probability 1 - 1/m, chi = 2^H is at most 4 while the expected optimal "
          "guess rank is 1 + (N+1)/(2m) and grows without bound. Effective diversity is a "
          "statistic about a distribution, not about the work of searching it.",
  novelty_removed="Any claim in this lane that a small hypothesis space wins BECAUSE it is "
                  "small. Size is not the operative quantity.",
  mapped_to="The charge rule this lane has used since DEV-6: a consultation costs what it "
            "examines. X5's Y5 tested the review's objection directly on this lane's own "
            "arms and confirmed it -- the same language produces BOTH signs of the carry "
            "advantage, so no function of version-space size predicts the sign, while the "
            "margin rebuilt from the priced events reproduces the measured work difference "
            "to the integer in every one of the thirty-six cells.",
  prior_information_charged="None. The review was written against PR #150's theory without "
                            "reference to this lane, and its counterexample is arithmetic.",
  next_experiment="A world where the version space is LARGE but a consultation is O(1) "
                  "regardless -- a perfect hash or a precompiled decision over the space. "
                  "The size story predicts a loss and the charge story predicts a win, and "
                  "this lane has never built one."),
A(parent="Belady (1966) optimal replacement", field="caching",
  receipt="results/RETAIN_E10_V1.json", verdict="ADOPT",
  teaches="For uniform-size uniform-cost items, furthest-in-future eviction is optimal, "
          "which supplies something rarer than a baseline: a CEILING over an entire "
          "representation class. Beating it cannot be explained by scheduling or luck.",
  novelty_removed="Any claim that OCM's retention policy is a good cache. It is not the "
                  "policy that pays; a clairvoyant policy is available and was used.",
  mapped_to="the eviction half of a bounded persistent store",
  prior_information_charged="the entire future demand stream, handed to the parent free",
  next_experiment="a mixed clairvoyant that may hold generators as well as instances; run "
                  "in E10 as belady_mixed_reference and it still beats the arm"),

A(parent="de Kleer (1986) ATMS; Reiter (1987) minimal hitting sets",
  field="truth maintenance and model-based diagnosis",
  receipt="results/SUPPORT_E6_V1.json, results/DEPEND_E3_V1.json", verdict="ADOPT",
  teaches="Minimal supporting environments are the right object for 'what breaks this', and "
          "leave-one-out ablation cannot express them: it recovers 0.409 of the support "
          "families here and 0.00 on the alternative-support archetype.",
  novelty_removed="Any claim that support-family discovery is new. It is 1986 work.",
  mapped_to="the dependency and revocation layer",
  prior_information_charged="justifications handed free to the gifted variant; the fair "
                            "variant must discover them and is the one reported",
  next_experiment="none needed here; the ATMS won and the arm's only difference from it "
                  "was a degradation mode"),

A(parent="DreamCoder and Stitch", field="library learning",
  receipt="results/LIBDISC_E5_V1.json", verdict="ADAPT",
  teaches="Both close the DISCOVERY gap completely -- they find the arm's composite and "
          "three more -- so no discovery advantage is claimed against library learning. "
          "They then lose on WORK, because MDL-only admission with no support gate keeps "
          "macros that pay no rent, leaving them net-harmful on every set including where "
          "the opportunity exists.",
  novelty_removed="Any claim that OCM discovers reusable abstractions others miss.",
  mapped_to="the acquisition proposer, with admission moved behind a support gate",
  prior_information_charged="the same episodes and the same checker as the arm",
  next_experiment="whether the support gate is itself parent-owned; support-thresholded "
                  "admission is close to standard frequent-pattern mining and the "
                  "comparison has not been run"),

A(parent="ordinary least squares over a monomial basis, degree-escalating",
  field="system identification", receipt="results/INDEP_E8_V1.json", verdict="GENERALIZE",
  teaches="Written from its own standard description, sharing no code path with the arm, it "
          "beat a Walsh-transform arm at 0.779 of its objective calls with identical "
          "steady-state cost and identical recovered parameters. The entire gap was "
          "first-generation identification: escalate the model class on demand rather than "
          "computing the whole basis.",
  novelty_removed="Any claim that learned causal factorization needs a transform "
                  "representation, and any reading of the earlier PARENT_SUFFICIENT as "
                  "vacuous -- with an independent parent it became informative and adverse.",
  mapped_to="the identification stage of any acquisition, generalized to: escalate "
            "representation cost against demonstrated need",
  prior_information_charged="none beyond the arm's; a test walks the import graph",
  next_experiment="the phi coordinate below; this result is one of the two that suggested "
                  "index granularity is the variable"),

A(parent="lookup classifier over evidence vectors; naive Bayes over per-probe likelihoods",
  field="statistical diagnosis", receipt="results/PROBESEM_E11_V1.json", verdict="GENERALIZE",
  teaches="The lookup classifier needs no notion of what an instrument MEANS and converges to "
          "the same accuracy, so semantics are not necessary for the task. What separates "
          "them is sample efficiency and it is not mostly the table: naive Bayes, holding "
          "per-probe frequencies and no table, captures roughly a third of the gap. The "
          "operative property is that evidence about an instrument COMPOSES across episodes.",
  novelty_removed="Any claim that OCM diagnoses better because it represents semantics.",
  mapped_to="the phi coordinate: per-object indexing rather than per-configuration",
  prior_information_charged="identical observations, revelations and exploration bonus",
  next_experiment="noisy instruments, where per-row evidence should degrade faster still"),

A(parent="lazy re-derivation (retain nothing, recompute on demand)",
  field="folklore, and the strongest parent in four of this lane's experiments",
  receipt="results/DEPEND_E3_V1.json, results/SUPPORT_E6_V1.json, results/RHO_E7_V1.json",
  verdict="GENERALIZE",
  teaches="Where the resource an acquired structure economizes is free and unbounded, "
          "retaining nothing is OPTIMAL, not merely competitive. Four PARENT_SUFFICIENT "
          "terminals in this lane are that theorem, not a measurement of OCM.",
  novelty_removed="Any claim that those four negatives were about OCM's architecture.",
  mapped_to="the beta coordinate below; it is the reason beta exists",
  prior_information_charged="none; it holds nothing",
  next_experiment="already run: E10 bounds the resource and the sign reverses"),

A(parent="experience replay; elastic weight consolidation; replay-then-consolidate",
  field="continual learning",
  receipt="results/DEV2_CONTINUAL_PARENTS_V1.json, results/DEV1_D0_TO_D1_V1.json",
  verdict="ADOPT",
  teaches="Plain experience replay -- keep the answers, never abstract -- BEATS the lineage "
          "at five of six settings and by 1.57x at the loose budget where DEV-1 reported "
          "its only positive, and its margin GROWS with the length of the second stage "
          "rather than decaying. The mechanism is priced, not asserted: a held rule "
          "licenses a scope check, so using one costs VERIFY + APPLY where a stored answer "
          "costs LOOKUP, and a sweep over the check price flips the sign between 10 and 25 "
          "with replay's own work constant throughout. EWC is the weaker of the two ideas "
          "here and loses to the lineage except where the store saturates.",
  novelty_removed="Any claim that carrying an ABSTRACTED store across a developmental "
                  "boundary is the best use of a bounded budget. This lane's only "
                  "developmental positive is withdrawn; what survives is DEV-1's comparison "
                  "against RESET_OCM, which answers a different and narrower question.",
  mapped_to="the retention layer of the lineage, which should hold instances until the "
            "cost of verifying an abstraction is known to be low",
  prior_information_charged="the same D0 stream, the same bits, the same D1 stream; "
                            "consolidation reads only the bounded buffer, not the lineage's "
                            "uncharged record of everything it ever derived",
  next_experiment_after_that_2="RUN, in results/DEV5_UNANIMITY_V1.json, and it dissolves "
                  "the dilemma rather than resolving it. DEV-3 and DEV-4 both used a guard "
                  "only when its version space was a SINGLETON, which is sufficient for "
                  "soundness and not necessary. Asking per QUERY whether all survivors "
                  "AGREE about this index is sound for the same reason and fires far more "
                  "often: it beats the singleton rule at every setting by up to 5.1x, with "
                  "mean scope checks falling from about 1700 to about 200 of 2000, at "
                  "correctness 1.0 for both. It then beats the replay parent while holding "
                  "a language large enough to contain every world's truth rather than one "
                  "fitted to the world, so the carry advantage no longer rests on the "
                  "precondition DEV-4 found binding. The control holds: the same rule over "
                  "a language that cannot express the truth is unsound in 17 of 36 cells",
  next_experiment_after_that="RUN, in results/DEV4_LANGUAGE_EXPANSION_V1.json: DEV-3's "
                  "declared gift -- that the guard language contains the truth -- turns out "
                  "to be a PRECONDITION and not a convenience. Withdraw it and the arm is "
                  "not slower, it is WRONG, because a version space over a language that "
                  "cannot express the truth still collapses to a singleton and the arm "
                  "cannot tell a false guard from a true one. Soundness is graded by "
                  "evidence rather than granted by the language, and it is not reached at "
                  "level 3 under skewed demand at any evidence length in the sweep",
  next_experiment="RUN, in results/DEV3_GUARDED_RULES_V1.json, and the prediction held: a "
                  "rule carrying its own precondition, paying bits from the same budget "
                  "instead of a per-use check, beats this same replay parent at all twelve "
                  "settings inside a computable budget window, by up to 3.6x, at "
                  "correctness 1.0 -- with the unstructured-exception control still losing "
                  "to replay, and with rule applications identical between the guarded and "
                  "unguarded arms while checks fall from 3498 to 18"),
]


#: The three coordinates, each isolated by an experiment that varied it alone.
CONDITIONS = {
"rho": dict(
  name="demand",
  question="Is the acquired structure required again?",
  isolated_by="E7 (results/RHO_E7_V1.json), which sweeps reuse-opportunity density and "
              "holds mechanism, parents, budgets, checker and horizon fixed",
  absent_reproduces="every negative in the programme; the density-zero row is the "
                    "anti-rigging control and it reproduces them",
  measurable_as="fraction of tasks whose minimal solution cost strictly increases when the "
                "acquired structure is removed -- certified, not assumed"),
"beta": dict(
  name="scarcity of the economized resource",
  question="Is the resource that holding this structure saves actually scarce?",
  isolated_by="E10 (results/RETAIN_E10_V1.json) for storage bits, E11 "
              "(results/PROBESEM_E11_V1.json) for labelled cases",
  absent_reproduces="lazy re-derivation wins by a theorem rather than by a policy; this is "
                    "the coordinate no experiment before E10 had ever varied",
  measurable_as="whether the resource is bounded or priced. NOT a threshold: DEV-1 shows an "
                "upper edge too, where the store is so tight that carried structure cannot "
                "be displaced by what the next stage needs and the lineage loses"),
"phi": dict(
  name="factorisation of the index",
  question="Does evidence about the acquired object compose across episodes?",
  isolated_by="E11, directly (a semantics cell against a row keyed by an outcome vector); "
              "E8, incidentally (a full transform against degree-escalating least squares)",
  absent_reproduces="each episode's evidence is usable only on episodes that match it "
                    "exactly, so acquisition costs more than it returns",
  measurable_as="whether one episode's evidence updates a per-object cell or a "
                "per-configuration row"),
}


@dataclass(frozen=True)
class Coordinates:
    rho: bool
    beta: bool
    phi: bool


def predict(c: Coordinates) -> str:
    """The law, stated as a rule that can be wrong.

    ``MACHINE`` only in the joint regime; ``PARENT_SUFFICIENT`` whenever any
    coordinate is absent. There is no weighting and no free parameter, which is
    deliberate: a rule with a knob would fit anything.
    """
    return "MACHINE" if (c.rho and c.beta and c.phi) else "PARENT_SUFFICIENT"


def O(**kw):
    base = dict(study="", receipt="", rho=False, beta=False, phi=False, observed="",
                note="")
    base.update(kw)
    return base


#: Every acquisition-versus-deferral comparison this lane has run, scored on the
#: three coordinates and against what actually happened. IN SAMPLE, all of it.
OBSERVED = [
O(study="E1 supplied-key lookup", receipt="results/SCALING_PILOT_V1.json",
  rho=False, beta=False, phi=True, observed="PARENT_SUFFICIENT",
  note="the key was supplied, so nothing was demanded of the machine"),
O(study="E3 eager dependency", receipt="results/DEPEND_E3_V1.json",
  rho=True, beta=False, phi=True, observed="PARENT_SUFFICIENT",
  note="most of what was discovered was never queried and holding it was free"),
O(study="E6 support families", receipt="results/SUPPORT_E6_V1.json",
  rho=True, beta=False, phi=True, observed="PARENT_SUFFICIENT",
  note="lazy re-derivation reached the same capability for half the work"),
O(study="E7 rho sweep", receipt="results/RHO_E7_V1.json",
  rho=True, beta=False, phi=True, observed="PARENT_SUFFICIENT",
  note="crossovers against weak parents, none against the deferred-induction parent"),
O(study="E5 library discovery", receipt="results/LIBDISC_E5_V1.json",
  rho=True, beta=False, phi=True, observed="PARENT_SUFFICIENT",
  note="the arm beat no-library and DreamCoder and Stitch, and tied a parent holding the "
       "identical schema; with holding free, every holder is equal"),
O(study="E8 independent factorization", receipt="results/INDEP_E8_V1.json",
  rho=True, beta=False, phi=False, observed="PARENT_SUFFICIENT",
  note="the arm computed a whole basis where the parent escalated degree on demand"),
O(study="E10 bounded retention", receipt="results/RETAIN_E10_V1.json",
  rho=True, beta=True, phi=True, observed="MACHINE",
  note="online generalizer beats a clairvoyant instance-optimal parent above a "
       "compressibility threshold; at extension size one phi fails and so does the arm"),
O(study="E11 learned probe semantics", receipt="results/PROBESEM_E11_V1.json",
  rho=True, beta=True, phi=True, observed="MACHINE",
  note="labelled cases are the scarce resource; per-cell evidence composes and per-row "
       "evidence does not"),
O(study="DEV-1 D0 to D1, 1024 bits",
  receipt="results/DEV1_D0_TO_D1_V1.json",
  rho=True, beta=True, phi=True, observed="MACHINE",
  note="carried structure makes the next stage cheaper where the store has headroom"),
O(study="DEV-1 D0 to D1, 256 bits",
  receipt="results/DEV1_D0_TO_D1_V1.json",
  rho=True, beta=False, phi=True, observed="PARENT_SUFFICIENT",
  note="beta is scored FALSE at the tight budget on the interval reading: the store is past "
       "the upper edge, saturated by D0's own rules, so carried structure cannot be "
       "displaced. This is the row most at risk of being scored to fit, and it is flagged "
       "as such rather than buried"),
]


LAW_STATUS = (
    "CONJECTURE, FITTED POST HOC. The rule was written after all ten rows above were known "
    "and it reproduces all ten, which is worth exactly nothing on its own -- a rule fitted "
    "to ten points that explains ten points has been fitted, not tested. One row (DEV-1 at "
    "256 bits) requires the interval reading of beta and would score the other way under a "
    "threshold reading, and it is marked. The law becomes evidence only if the frozen "
    "out-of-sample prediction below survives."
)


#: Frozen before the experiment exists. The digest of this plan is the commitment.
OUT_OF_SAMPLE = dict(
  name="PERISHABLE_EVIDENCE",
  why_this_one=(
    "It is the half of the deep root's falsifier that is still unrun, and the three "
    "coordinates assign it a sign that is NOT the sign the rest of this lane would lead "
    "anyone to guess."),
  design=(
    "E10's world, with one change: derived evidence PERISHES. An answer derived at step t "
    "can be re-derived later only at a cost rising with elapsed time, so postponing is no "
    "longer free. Retention budget is left UNBOUNDED and generously large -- beta is "
    "deliberately switched OFF as a storage constraint -- and rho and phi are held at E10's "
    "values."),
  coordinates=dict(rho=True, beta=True, phi=True),
  coordinate_justification=(
    "beta is TRUE even though the store is unbounded, because beta is scarcity of the "
    "resource the structure economizes, and here that resource is the OPPORTUNITY to derive "
    "cheaply, which perishes. This is the load-bearing move: if beta only ever meant 'bits "
    "are capped' then the law is a statement about caches. If it means 'the economized "
    "resource is scarce' then perishability must switch it on, and the prediction below "
    "follows without any further choice."),
  predicted=("MACHINE"),
  predicted_before_the_experiment_exists=True,
  what_refutes_the_law=(
    "PARENT_SUFFICIENT in the perishable world. That would show beta is specifically about "
    "bounded storage rather than about scarcity of the economized resource, the three "
    "coordinates would not be the right three, and the law would be a caching result with "
    "an inflated name."),
  what_confirms_it_weakly=(
    "MACHINE in the perishable world confirms the generalized reading of beta on ONE further "
    "point. That is one out-of-sample point, not a validated law, and the receipt must say "
    "so in those words."),
  registered_in="the commitment digest of this module",
)


#: The outcome of the frozen prediction, and the status the law holds AFTER it.
#: Both live OUTSIDE ``PLAN`` on purpose. ``LAW_STATUS`` and ``OUT_OF_SAMPLE`` are
#: inside the plan and therefore inside the commitment digest, so editing either
#: to record what happened would retroactively rewrite the prediction it was
#: frozen in. The frozen text stays exactly as it was written; what the run
#: produced is recorded beside it and never over it.
OUT_OF_SAMPLE_RESULT = dict(
  ran="results/PERISH_E12_V1.json",
  verdict="SURVIVED_ONE_TEST",
  what_happened=(
    "The crossover extension at which a rule beats a memoizer falls from 16 to 8 as the "
    "perishability ramp rises, so acquisition pays at strictly lower compressibility once "
    "the opportunity to derive cheaply perishes. beta therefore does generalize beyond "
    "bounded storage, which is what the prediction was for."),
  the_correction_it_forced=(
    "The prediction's justification contained an error and E12's pilot found it. This "
    "module argued that with storage free and unbounded, keeping everything you derive is "
    "the folklore-optimal policy. That is false. Compression reduces the number of "
    "DERIVATIONS, not merely the number of bits, so at a large enough extension a rule wins "
    "whether or not derivation perishes -- and the pilot duly produced a confirmation that "
    "was an artifact of compression with perishability doing nothing at all. The corrected "
    "experiment sweeps extension, checks the lam = 0 row against an arithmetic break-even "
    "computed from the cost constants alone, and reports the SHIFT of the boundary rather "
    "than a win. Both the wrong argument and the confirmation it would have bought are on "
    "the record."),
  how_much_this_is_worth=(
    "One out-of-sample point. The law now has one prediction it could have failed and did "
    "not, which moves it from a rule fitted to ten rows to a rule with one surviving "
    "prediction, and no further. Two of its three coordinates have still never been varied "
    "outside the experiments that defined them, and the law has since acquired a known "
    "counterexample: see OBSERVED_REVISIONS."),
  adverse_finding_in_the_same_run=(
    "E12 also ran the unrun half of the deep root's falsifier and it went AGAINST the "
    "machine. eager_all_rules_parent -- which acquires every rule before seeing any demand, "
    "and lost in E3, E6, E7 and E10 -- beats the demand-triggered arm wherever the ramp is "
    "steep, because it buys every derivation at the cheapest price the world will ever "
    "offer. The demand trigger this programme identified as the missing ingredient is "
    "itself a cost once waiting is charged. It is recorded here because it is the finding a "
    "lane reporting its own surviving prediction would be most tempted to leave in the "
    "receipt and out of the summary."),
)

#: Rows whose observed sign changed after a stronger parent was run. Kept OUTSIDE
#: ``PLAN`` for the same reason ``OUT_OF_SAMPLE_RESULT`` is: ``OBSERVED`` is inside
#: the commitment digest, and editing a row to match a later result would rewrite
#: the record the prediction was frozen against.
OBSERVED_REVISIONS = [
dict(study="DEV-1 D0 to D1, 1024 bits",
     was="MACHINE", now="PARENT_SUFFICIENT",
     forced_by="results/DEV2_CONTINUAL_PARENTS_V1.json",
     why=("The row was scored against RESET_OCM, which is the right control for 'did "
          "carrying help' and the wrong parent for 'is carrying the best use of these "
          "bits'. A plain experience-replay parent, never run when the row was written, "
          "beats the lineage by up to 1.57x at this budget."),
     consequence=("The law scores this row rho beta phi all true and predicts MACHINE. It "
                  "is now WRONG on it. In-sample agreement is no longer total and the "
                  "generated document reports both figures.")),
dict(study="DEV-1 D0 to D1, 1024 bits",
     was="PARENT_SUFFICIENT", now="PARENT_SUFFICIENT",
     forced_by="results/DEV5_UNANIMITY_V1.json",
     why=("This row has now changed sign TWICE and that fact is more informative than "
          "either sign. It was MACHINE against a reset control, PARENT_SUFFICIENT once a "
          "replay parent was run, and under the BEST AVAILABLE REPRESENTATION -- a large "
          "guard language with a per-query unanimity rule -- the lineage beats that same "
          "replay parent again. The reading registered before DEV-5 ran says the law "
          "predicts the sign for the best available representation, which would make the "
          "row agree."),
     consequence=("The revised table DELIBERATELY KEEPS THIS ROW AT PARENT_SUFFICIENT, so "
                  "agreement stays 9 of 10 rather than being restored to 10 of 10. A rule "
                  "whose fit is repaired by going and finding a better representation is "
                  "weaker than one that predicted the first attempt, and quietly banking "
                  "the repair would hide exactly that. The best-representation sign is "
                  "recorded in BEST_REPRESENTATION_SIGNS instead, where it can be read "
                  "beside the row it does not overwrite.")),
dict(study="DEV-1 D0 to D1, 256 bits",
     was="PARENT_SUFFICIENT", now="PARENT_SUFFICIENT",
     forced_by="results/DEV2_CONTINUAL_PARENTS_V1.json",
     why=("Unchanged in sign, but for a different reason than recorded: the row was "
          "attributed to the store saturating, and DEV-2 shows EWC_PARENT beating the "
          "lineage at the shortest D1 there, so protection helps in exactly the cell the "
          "saturation story said it should hurt."),
     consequence="No change to the law's agreement; the stated mechanism is less certain."),
]

#: What happened when the candidate below was acted on rather than added to the
#: rule. Outside ``PLAN``, like every other outcome record here.
CANDIDATE_FOLLOW_UP = dict(
  ran="results/DEV3_GUARDED_RULES_V1.json",
  verdict="THE CANDIDATE WAS RIGHT, AND IT IS STILL NOT A COORDINATE",
  what_happened=(
    "The counterexample said the law ignores what an acquired object costs to USE. DEV-3 "
    "changed the representation so that using one costs nothing extra -- a rule carrying its "
    "own scope precondition, charged in bits from the same budget -- and the sign flipped "
    "back: the lineage beats the replay parent at every setting inside a computable budget "
    "window, by up to 3.6x, at correctness 1.0. Rule applications are identical between the "
    "guarded and unguarded arms and checks fall from 3498 to 18, so the guard changes the "
    "PRICE of a use and not the number of uses."),
  what_it_says_about_the_law=(
    "The DEV-1 row was mispredicted because the representation carried a use tax, not "
    "because the world was outside the joint regime. That is a real distinction and it cuts "
    "against a simple reading of the law: the three coordinates describe the world, and "
    "whether the machine wins in a world that satisfies them also depends on the "
    "representation it chose. The law as written predicts the best available "
    "representation's sign, which is a stronger and more falsifiable claim than the one it "
    "was fitted to make, and it is now stated that way rather than quietly assumed."),
  why_it_is_still_not_a_fourth_coordinate=(
    "Adding use-cost would restore a perfect in-sample fit and would be the second time this "
    "module patched itself to match the data. The DEV-1 row STAYS mispredicted in the "
    "revised table. What DEV-3 buys is not a repair of the law but a sharper reading of what "
    "it claims, plus a new falsifier: find a world satisfying rho, beta and phi where NO "
    "representation without a use tax exists, and the law is wrong rather than incomplete."),
)

#: The quantity the counterexample points at. Recorded as a CANDIDATE and
#: deliberately NOT added to ``predict``: a law that grows a coordinate every time
#: it is wrong is not a law, and the honest state is a rule with a known
#: counterexample rather than a rule with four coordinates and no failures.
CANDIDATE_MISSING_QUANTITY = (
    "The USE COST of an acquired object relative to the instance it replaces. All three "
    "coordinates are about acquisition -- is it demanded, is the economized resource scarce, "
    "does its evidence compose -- and none is about what it costs to invoke the thing once "
    "held. DEV-2 prices that directly: at a free scope check the lineage does 0.66 of "
    "replay's work and at the registered price 1.40, on identical worlds, with replay's own "
    "work unchanged. Adding a fourth coordinate would restore a perfect in-sample fit and "
    "would mean nothing. The test it implies instead is a world where verification is cheap "
    "or unnecessary, where this candidate predicts the lineage wins and the current "
    "three-coordinate law predicts nothing different."
)

#: The sign each contested row takes under the best representation anyone has
#: built for it, as opposed to the representation the row's own experiment used.
#: Reported separately and never folded into the revised agreement figure.
BEST_REPRESENTATION_SIGNS = {
"DEV-1 D0 to D1, 1024 bits": dict(
  sign="MACHINE",
  representation="large guard language, per-query unanimity",
  receipt="results/DEV5_UNANIMITY_V1.json",
  caveat=(
    "This is the sign under a representation found AFTER the row was recorded as a "
    "failure. It is reported because the reading of the law registered before DEV-5 ran "
    "says the law predicts the best available representation's sign, and it is kept out "
    "of the agreement figure because a rule that is right once you go and build a better "
    "arm for it has a weaker claim than one that was right the first time. Both readings "
    "are available; neither is hidden behind the other."),
),
}

#: Doctrine S3 asks whether a learned computational contract survives a change of
#: validation semantics. This is the first thing in this lane that answers it,
#: and the answer has a boundary in it. Outside ``PLAN``, like every outcome here.
CROSS_DOMAIN = dict(
  contract="act wherever the hypothesis space already determines this question, rather "
           "than waiting for it to collapse to one candidate",
  first_domain=dict(
    receipt="results/DEV5_UNANIMITY_V1.json",
    object="a version space of periodic predicates guarding a rule",
    resource_saved="scope checks against the world",
    sign="WINS, on both columns; checks falling from about 1700 to about 200. The FACTOR "
         "was first reported as up to 5.1x and is corrected to up to 3.4x by "
         "results/DEV6_HONEST_CONSULTATION_PRICE_V1.json, which re-prices the "
         "consultation in proportion to what it scans -- the accounting standard the "
         "second domain was already using. The ordering survives the correction and the "
         "magnitude does not; the weakest cell becomes nearly a tie at 0.97"),
  second_domain=dict(
    receipt="results/X1_UNANIMITY_TRANSFER_V1.json",
    object="a lattice of evidence subsets, enumerating minimal support families",
    resource_saved="charged interventions",
    sign="WINS on interventions by 2.67x at matched capability and LOSES on total work by "
         "1.63x, because the reasoning that establishes 'already answered' is charged and "
         "here it costs more than the intervention it avoids",
    provenance="the mechanism was already in E6, written by another author for another "
               "question before DEV-5 existed; X1 is an ablation of E6's own source "
               "transformed by one line, not a re-implementation"),
  what_the_pair_identifies=(
    "Neither experiment identifies this alone and together they do: the contract is "
    "domain-neutral and its SIGN is not. It pays when the machine's own reasoning is cheap "
    "relative to querying the world, and it loses when reasoning is dear. DEV-5 measured "
    "that boundary inside its own domain with a consultation-price sweep -- it won up to a "
    "price of 5 and lost at 25 -- and E6 sits on the losing side of the same ratio. So the "
    "quantity to carry forward is a PRICE RATIO between internal deliberation and external "
    "query, and it is the second time this lane has found that what decides a comparison is "
    "the cost of the machine's own operations rather than the structure of the world."),
  relation_to_the_candidate_missing_quantity=(
    "CANDIDATE_MISSING_QUANTITY named the use cost of an acquired object relative to the "
    "instance it replaces. This names the cost of deliberating about an object relative to "
    "asking the world. They are the same shape -- an internal price measured against an "
    "external one -- and neither is in the law's three coordinates, all of which describe "
    "the world. That is now TWO independent pointers at the same gap, which is worth more "
    "than either, and it is still not a reason to bolt a fourth coordinate on."),
  the_audit_this_pair_forced=(
    "Comparing the two domains is what exposed the pricing difference, and the lane that "
    "made the mechanism look free was this one. E6 charged its deliberation in proportion "
    "to the knowledge consulted; DEV-5 charged a flat price whether the arm tested one "
    "predicate or scanned 433. DEV-6 re-ran DEV-5 under the proportional charge and the "
    "conclusion held while the number shrank. It also refuted the fix this lane proposed to "
    "recover the difference -- maintaining per-index vote counts costs more than the "
    "scanning it replaces, at every workload measured -- which was only visible because the "
    "bookkeeping was charged. So the cross-domain comparison paid for itself twice: once as "
    "a boundary, and once as an audit of the result on our side of it."),
  what_it_does_not_establish=(
    "Two domains is not domain-neutrality, and both are synthetic and in this repository. "
    "The strength of the evidence is not its breadth but its independence: E6's use of the "
    "rule was not arranged after the fact."),
)

LAW_STATUS_AFTER_THE_TEST = (
    "CONJECTURE WITH ONE SURVIVING OUT-OF-SAMPLE PREDICTION. The frozen LAW_STATUS above is "
    "left exactly as written, because it is inside the commitment digest and editing it "
    "would rewrite the prediction after seeing the result. What changed is only this: the "
    "prediction was run and did not fail. That is one point. It is not a validated law, the "
    "in-sample agreement is still worth nothing, and the run that confirmed the prediction "
    "also refuted the argument that motivated it. Since then the law has picked up a "
    "COUNTEREXAMPLE from a different direction: running the continual-learning parents "
    "against DEV-1 turned one of the rows it was fitted to from MACHINE into "
    "PARENT_SUFFICIENT, so revised agreement is 9 of 10 rather than 10 of 10. The candidate "
    "missing quantity is named in CANDIDATE_MISSING_QUANTITY and is deliberately NOT added "
    "to the rule. A conjecture with one surviving prediction and one known failure is a "
    "more honest object than a conjecture with four coordinates and none."
)



#: A second lane, a real workload, and the same shape. Recorded OUTSIDE ``PLAN``.
#:
#: PR #153 publishes an eight-call comparison on the actual OCM PROGRAMMATIC
#: dispatcher rather than on synthetic worlds. It is not this lane's evidence and
#: nothing here re-analyses it; what follows quotes its own reported numbers and
#: states what this lane's law predicts about it, so that the prediction is on
#: record before that lane runs the experiment that would settle it.
NATIVE_LANE_CROSS_CHECK = dict(
  source="PR #153 research/native-serving-evidence-v1/HANDOFF.md and "
         "research/native-grounding-review-v1/DECISION.md",
  what_it_reports=(
    "A learned method carried into a proof task is causally used and reduces the positive "
    "rule-tree cost from 3 to 2 and action attempts from 141,792 to 72,579 -- very close to "
    "a halving of the search. OCM nevertheless added cold overhead in every one of the four "
    "pairs, 1.104 to 1.756 seconds, and the handoff states that no cold speedup or lifetime "
    "advantage follows. The grounding review locates why: full ordinary compilation costs "
    "3.689 to 3.931 seconds per arm while search costs 0.256 to 0.442, because compile_parent "
    "grounds the WHOLE bank -- 69,219 instances from 4,191 assertions and 255 formulas -- "
    "before any demand is consulted."),
  why_this_lane_recognises_it=(
    "It is X5's shape in another domain. A carried representation halves the VARIABLE cost "
    "and is charged a FIXED cost that does not shrink with the demand, and the advantage is "
    "invisible because the fixed cost dominates. In this lane the fixed cost is bits: the "
    "guarded arm holds a minority of its guards until the budget is large enough, its work "
    "is nearly flat while that is true, and it wins only in the interval where the fixed "
    "cost is paid and the parent cannot yet memoise. Halving something that is a tenth of "
    "the total cannot be seen, whichever lane you are in."),
  the_prediction=(
    "The grounding review's own next lever -- demand-driven grounding, adapted from "
    "Souffle's magic-set transformation -- is exactly the intervention that makes the fixed "
    "cost proportional to the demand. This lane therefore predicts, before that experiment "
    "exists, that the learned method's already-measured halving of search becomes a "
    "measurable end-to-end advantage only after grounding is made demand-driven, and that "
    "adding indexes or caching the compiled bank will NOT produce one, because neither "
    "changes the proportion of the fixed cost to the demand. This is refutable in that "
    "lane's units, which is the point of writing it down here."),
  what_would_refute_it=(
    "An end-to-end advantage appearing from compiled-bank reuse or indexing alone, or "
    "demand-driven grounding landing without one."),
  boundary=(
    "This lane's receipts are synthetic and this is not evidence about the native lane. It "
    "is a prediction, stated in the other lane's units, with the refutation named."),
)


#: What X6 found when the prediction above was run in this lane's own units.
#: Recorded SEPARATELY and the prediction above is left exactly as it was
#: published, because a prediction edited after its test is not a prediction.
NATIVE_LANE_CROSS_CHECK_ANALOGUE_RESULT = dict(
  receipt="results/X6_COMPILED_CONSULTATION_V1.json",
  what_was_tested=(
    "X6 built both halves of the native lane's lever in this lane: PRECOMPILED_EAGER, which "
    "compiles every index of a rule whenever its version space changes, and "
    "PRECOMPILED_DEMAND, which compiles an index the first time it is demanded. Both hold "
    "the full 433-predicate language and return the unanimity verdict; only the price of a "
    "consultation differs, and a per-replicate control confirmed that no non-deliberation "
    "counter differs anywhere."),
  the_half_that_held=(
    "The ORDERING. Demand-driven compilation costs less deliberation than eager compilation "
    "at every one of the thirty-six settings, and eager wins at no setting demand-driven "
    "does not."),
  the_half_that_did_not=(
    "The claim that compiling the whole bank buys NOTHING. In the analogue it buys almost "
    "everything: eager compilation beats the replay parent at 20 settings against "
    "demand-driven's 21, where the naive scanning rule wins at 8. The prediction as "
    "published is therefore NOT supported in this lane, and is not quietly narrowed."),
  why_the_analogue_cannot_settle_it=(
    "Eager compilation costs the scan times the EXTENSION, which is 16 here, and the "
    "demanded indices already cover about 14 of those 16 -- the measured cache hit rate is "
    "0.78 to 0.86. Compiling everything is therefore barely more than compiling what is "
    "asked for, and the two levers are almost the same lever at this scale. The native lane "
    "grounds 69,219 instances from 4,191 assertions, where a proof's demand cone is a tiny "
    "fraction of the bank, so the gap this lane cannot resolve is exactly the gap that lane "
    "would be measuring."),
  the_prediction_restated=(
    "The publishable form is narrower than what was published and is stated here rather than "
    "substituted for it: the advantage from a carried method appears once the fixed cost of "
    "preparing it is made proportional to the demand, and eager preparation achieves that "
    "only to the extent that the demand already covers the bank. In the native lane it does "
    "not, so eager compiled-bank reuse is predicted to leave most of the advantage on the "
    "table there while capturing nearly all of it here. That is refutable in both lanes and "
    "the earlier, stronger form is refuted in this one."),
)

PLAN: Mapping[str, Any] = {
    "study_id": "SYNTHESIS_V1",
    "doctrine": "PR #150, PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "doctrine_section_addressed": "S5 principled boundary, and S2 new relationship",
    "conditions": CONDITIONS,
    "observed": OBSERVED,
    "law_status": LAW_STATUS,
    "out_of_sample": OUT_OF_SAMPLE,
}

COMMITMENT: Commitment = commit(PLAN)


def check_in_sample() -> list[dict]:
    out = []
    for row in OBSERVED:
        pred = predict(Coordinates(row["rho"], row["beta"], row["phi"]))
        out.append(dict(row, predicted=pred, agrees=pred == row["observed"]))
    return out


def check_after_revision() -> list[dict]:
    """The in-sample table with later parents taken into account.

    ``OBSERVED`` stays frozen; this applies the revisions on top of it, so the
    record of what the law was fitted to and the record of what is now true are
    both available and neither overwrites the other.
    """
    fix = {r["study"]: r["now"] for r in OBSERVED_REVISIONS}
    out = []
    for row in check_in_sample():
        observed = fix.get(row["study"], row["observed"])
        out.append(dict(row, observed=observed, revised=row["study"] in fix,
                        agrees=row["predicted"] == observed))
    return out


def build() -> dict:
    rows = check_in_sample()
    revised = check_after_revision()
    return {
        "schema": "orion.parent-synthesis.v1",
        "programme": "SzeChunYiu/ORION-OCM#143",
        "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
        "authority": (
            "This module produces no evidence. It reclassifies existing receipts under the "
            "absorption doctrine and states a conjecture over them. Every receipt it cites "
            "stands unchanged."),
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed},
        "absorptions": ABSORPTIONS,
        "verdict_counts": {v: sum(1 for a in ABSORPTIONS if a["verdict"] == v)
                           for v in VERDICTS},
        "no_parent_was_rejected": (
            "Not one parent in this lane is classified REJECT, because not one of them lost. "
            "Under the old reading that was seven defeats; under the doctrine it is an "
            "absorption backlog, and the backlog has a shape, which is the next section."),
        "conditions": CONDITIONS,
        "law": (
            "An acquired structure beats deriving on demand only in the JOINT regime "
            "rho AND beta AND phi: the structure is demanded again, the resource it "
            "economizes is scarce, and evidence about it composes across episodes. Outside "
            "that regime the parent wins by arithmetic and not by being cleverer, which is "
            "why seven PARENT_SUFFICIENT terminals in this lane say more about the worlds "
            "than about the machine."),
        "law_status": LAW_STATUS,
        "in_sample": rows,
        "in_sample_agreement": sum(1 for r in rows if r["agrees"]) / len(rows),
        "in_sample_is_not_evidence": (
            "The rule was written knowing all of these rows. Agreement of "
            f"{sum(1 for r in rows if r['agrees'])}/{len(rows)} is a statement about the "
            "rule's construction, not about the world."),
        "out_of_sample": OUT_OF_SAMPLE,
        "out_of_sample_result": OUT_OF_SAMPLE_RESULT,
        "law_status_after_the_test": LAW_STATUS_AFTER_THE_TEST,
        "observed_revisions": OBSERVED_REVISIONS,
        "in_sample_after_revision": revised,
        "in_sample_agreement_after_revision": (
            sum(1 for r in revised if r["agrees"]) / len(revised)),
        "candidate_missing_quantity": CANDIDATE_MISSING_QUANTITY,
        "candidate_follow_up": CANDIDATE_FOLLOW_UP,
        "best_representation_signs": BEST_REPRESENTATION_SIGNS,
        "cross_domain": CROSS_DOMAIN,
        "native_lane_cross_check": NATIVE_LANE_CROSS_CHECK,
        "native_lane_cross_check_analogue_result":
            NATIVE_LANE_CROSS_CHECK_ANALOGUE_RESULT,
        "agreement_note": (
            "Two agreement figures exist and only one is quoted as the law's. Against the "
            "representation each experiment actually used, agreement is "
            f"{sum(1 for r in revised if r['agrees'])} of {len(revised)}. Against the best "
            "representation anyone has since built, the DEV-1 row would also agree, making "
            "it total. The FIRST is the law's figure. The second is in "
            "best_representation_signs and is not banked, because a rule repaired by "
            "building a better arm after the fact is not the same object as a rule that "
            "predicted the first attempt."),
        "what_this_does_not_establish": (
            "Three binary coordinates over ten synthetic rows. Nothing here measures a real "
            "task ecology and none of the coordinates is measured continuously. The beta "
            "interval rested on a single pair of budgets until X5_BUDGET_CROSSING_V1 swept "
            "nine; the interval is now measured rather than assumed, and it is NARROWER "
            "than the one DEV-3 computed -- [1408, 1536] bits at both demand shapes against "
            "a computed window of [768, 2048]. The upper edge DEV-3 computed is confirmed "
            "out of sample; the lower one is necessary and not sufficient. The law is "
            "falsifiable, which remains its main virtue."),
    }


def main() -> int:
    doc = build()
    (HERE / "SYNTHESIS_V1.json").write_text(json.dumps(doc, indent=2) + "\n")
    L = ["# SYNTHESIS_V1 — parent absorption and the phase boundary\n",
         "**GENERATED FILE — edit `synthesis.py`, then run `python synthesis.py`.**\n",
         f"> {doc['law']}\n", f"**Status.** {doc['law_status']}\n",
         "## Absorption register\n",
         "| parent | verdict | receipt | novelty removed |", "|---|---|---|---|"]
    for a in doc["absorptions"]:
        L.append(f"| {a['parent']} | `{a['verdict']}` | `{a['receipt']}` | {a['novelty_removed']} |")
    L += ["", f"{doc['no_parent_was_rejected']}\n", "## The three coordinates\n"]
    for k, v in doc["conditions"].items():
        L += [f"### `{k}` — {v['name']}\n", f"{v['question']}\n",
              f"**Isolated by.** {v['isolated_by']}\n",
              f"**When absent.** {v['absent_reproduces']}\n",
              f"**Measured as.** {v['measurable_as']}\n"]
    L += ["## In sample (all of it)\n",
          "| study | rho | beta | phi | predicted | observed | agrees |",
          "|---|---|---|---|---|---|---|"]
    for r in doc["in_sample"]:
        L.append(f"| {r['study']} | {int(r['rho'])} | {int(r['beta'])} | {int(r['phi'])} "
                 f"| {r['predicted']} | {r['observed']} | {'yes' if r['agrees'] else 'NO'} |")
    o = doc["out_of_sample"]
    L += ["", f"{doc['in_sample_is_not_evidence']}\n",
          "## After a stronger parent was run\n",
          f"In-sample agreement falls from {doc['in_sample_agreement']:.0%} to "
          f"{doc['in_sample_agreement_after_revision']:.0%}. The frozen table above is left "
          "as it was fitted; the revisions are applied on top of it.\n",
          "| study | was | now | forced by |", "|---|---|---|---|"]
    for r in doc["observed_revisions"]:
        L.append(f"| {r['study']} | {r['was']} | {r['now']} | `{r['forced_by']}` |")
    L += ["", "**Candidate missing quantity, deliberately not added to the rule.** "
          f"{doc['candidate_missing_quantity']}\n",
          "**What happened when it was acted on.** "
          f"{doc['candidate_follow_up']['what_happened']}\n",
          f"**What that says about the law.** "
          f"{doc['candidate_follow_up']['what_it_says_about_the_law']}\n",
          f"**Why it is still not a fourth coordinate.** "
          f"{doc['candidate_follow_up']['why_it_is_still_not_a_fourth_coordinate']}\n",
          "## The frozen out-of-sample prediction\n", f"### {o['name']}\n",
          f"**Why this one.** {o['why_this_one']}\n", f"**Design.** {o['design']}\n",
          f"**Coordinates.** {o['coordinates']}\n",
          f"**Why beta is TRUE here.** {o['coordinate_justification']}\n",
          f"**Predicted.** `{o['predicted']}`\n",
          f"**What refutes the law.** {o['what_refutes_the_law']}\n",
          f"**What confirms it, and how weakly.** {o['what_confirms_it_weakly']}\n",
          f"**Commitment.** `{doc['commitment']['commitment']}`\n",
          "## Outcome\n",
          f"**Verdict.** `{doc['out_of_sample_result']['verdict']}` "
          f"— `{doc['out_of_sample_result']['ran']}`\n",
          f"{doc['out_of_sample_result']['what_happened']}\n",
          f"**The correction it forced.** "
          f"{doc['out_of_sample_result']['the_correction_it_forced']}\n",
          f"**How much this is worth.** "
          f"{doc['out_of_sample_result']['how_much_this_is_worth']}\n",
          f"**Adverse finding in the same run.** "
          f"{doc['out_of_sample_result']['adverse_finding_in_the_same_run']}\n",
          f"**Status now.** {doc['law_status_after_the_test']}\n",
          f"## What this does not establish\n\n{doc['what_this_does_not_establish']}\n"]
    (HERE / "SYNTHESIS_V1.md").write_text("\n".join(L))
    print(f"wrote SYNTHESIS_V1: {len(doc['absorptions'])} absorptions, "
          f"{doc['in_sample_agreement']:.0%} in-sample agreement (fitted), "
          f"out-of-sample prediction {o['predicted']} frozen at "
          f"{doc['commitment']['commitment'][:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
