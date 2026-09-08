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

A(parent="curriculum and transfer learning; catastrophic forgetting",
  field="continual learning",
  receipt="../developmental-spine/... DEV1_D0_TO_D1_V1.json", verdict="OPEN",
  teaches="Whether earlier training makes later training cheaper is their question, and the "
          "risk side -- negative transfer -- is theirs too. DEV-1 reproduces both in one "
          "run: the lineage wins at 1024 bits and loses at 256, where its carried structure "
          "cannot be displaced by what the next stage needs.",
  novelty_removed="Any claim that developmental carry-over is a new phenomenon.",
  mapped_to="the beta interval; DEV-1 is the evidence that beta is a band and not a threshold",
  prior_information_charged="the D0 store, earned by paying for every derivation in it",
  next_experiment="OPEN because no continual-learning parent has been run against the "
                  "lineage at all; a replay or EWC parent is the obvious next comparator "
                  "and its absence is a hole in the DEV-1 result, not a detail"),
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
    "outside the experiments that defined them."),
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

LAW_STATUS_AFTER_THE_TEST = (
    "CONJECTURE WITH ONE SURVIVING OUT-OF-SAMPLE PREDICTION. The frozen LAW_STATUS above is "
    "left exactly as written, because it is inside the commitment digest and editing it "
    "would rewrite the prediction after seeing the result. What changed is only this: the "
    "prediction was run and did not fail. That is one point. It is not a validated law, the "
    "in-sample agreement is still worth nothing, and the run that confirmed the prediction "
    "also refuted the argument that motivated it."
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


def build() -> dict:
    rows = check_in_sample()
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
        "what_this_does_not_establish": (
            "Three binary coordinates over ten synthetic rows. Nothing here measures a real "
            "task ecology, none of the coordinates is measured continuously, and the beta "
            "interval rests on a single pair of budgets in one experiment. The law is "
            "falsifiable, which is its only current virtue."),
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
