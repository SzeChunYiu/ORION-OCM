"""Recursive root-cause analysis over every negative result in the programme.

Each experiment returned a verdict. A verdict is a symptom, not a cause. This
module asks "why" of each verdict, then "why" of that answer, until the chains
stop producing new answers, then clusters the terminal answers and asks whether
the clusters share a root.

The method is deliberately mechanical so it can be checked: every observation
names the receipt it came from, every why-step is one inferential move, and a
cluster may only be claimed when two or more independent chains terminate on the
same statement. A root supported by a single chain is recorded as a conjecture,
not a root.

What the analysis concludes is uncomfortable and is stated plainly: the
programme has been measuring the supply side of amortization exhaustively and the
demand side not at all. That is a design fault in the experiments, not a property
of the architecture, and it means several of the negatives do not mean what they
appear to mean.
"""

from __future__ import annotations

import json
import pathlib
from collections import Counter

HERE = pathlib.Path(__file__).parent


def O(**kw):
    base = dict(observation_id="", verdict="", source="", why=(), terminates_at="",
                preserved=True)
    base.update(kw)
    return base


#: Every negative in the programme, with its why-chain. The last element of
#: ``why`` is the terminal statement the chain reaches.
OBSERVATIONS = [
O(observation_id="N1-SUPPLIED-KEY-LOOKUP", verdict="PARENT_SUFFICIENT",
  source="results/SCALING_PILOT_V1.json",
  why=(
    "an ordinary index matched k, k/N, query work and correctness exactly at every scale",
    "the index key was the family identity, supplied by the catalogue",
    "so the machine never had to determine relevance; it was told",
    "the task presented a single lookup decision with all relevant information already present",
  ),
  terminates_at="ONE_SHOT_DECISION_WITH_COMPLETE_INFORMATION"),

O(observation_id="N2-FAILURE-MEMORY", verdict="PARENT_SUFFICIENT",
  source="results/FAILURE_PILOT_V1.json",
  why=(
    "a full-strength nogood parent avoided all 640 avoidable work units and tied on four of seven worlds",
    "the residual was confined to worlds where the failure's cause carried no information about correctness",
    "and every arm was handed the correct cause by the world",
    "so each episode was a single classification with all relevant information already present",
  ),
  terminates_at="ONE_SHOT_DECISION_WITH_COMPLETE_INFORMATION"),

O(observation_id="N3-ESCALATION-ADVANTAGE", verdict="GENERATOR_ARTIFACT",
  source="results/ESCALATION_INDEPENDENT_E4_V1.json",
  why=(
    "70/70 on the old generator became 1736/2000 on blindly perturbed worlds",
    "the lead over a fully-resourced repair planner collapsed from 20 points to 0.7",
    "because ground truth had been the generator's intent, and the generator shared the policy's taxonomy",
    "the label and the policy were authored by the same hand",
  ),
  terminates_at="GROUND_TRUTH_SHARED_AN_AUTHOR_WITH_THE_POLICY"),

O(observation_id="N4-LEAVE-ONE-OUT", verdict="STRUCTURALLY_INCOMPLETE",
  source="results/DEPEND_E3_V1.json",
  why=(
    "16 to 25 per cent of methods had support no single-element ablation could see",
    "because where two supports each suffice alone, removing either changes nothing",
    "the probe granularity was fixed at one element by design",
    "so the instrument could not express the structure it was looking for",
  ),
  terminates_at="PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED"),

O(observation_id="N5-LEARNED-RELEVANCE", verdict="INDEX_MAINTENANCE_DOMINATES",
  source="results/SUBSPACE_E1_V1.json",
  why=(
    "with the key withheld, discovery worked but its index bill was not repaid at 30x",
    "the re-index search rescans the whole feature language from scratch on every repair",
    "and the registered query stream was 50 queries, so there was little to amortize against",
    "the structure was rebuilt more often than it was used",
  ),
  terminates_at="STRUCTURE_ACQUIRED_IS_NOT_SUBSEQUENTLY_DEMANDED"),

O(observation_id="N6-UNARY-ACQUISITION", verdict="NO_METHOD_ACQUIRED",
  source="research/math-language-learning-v1/ASSAY-ACQUISITION-DIAGNOSIS.md",
  why=(
    "21 candidates were mined, three were independently checked as sound and essential, all three were singletons",
    "the repeated-support gate then emptied the pool",
    "because flat queried fragments differ across episodes while the intermediate dependency step recurs",
    "the mining operated at a level of abstraction the recurrence does not live at",
  ),
  terminates_at="PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED"),

O(observation_id="N7-CLAUSE-DONOR", verdict="NO_DEVELOPMENT_BENEFIT",
  source="research/math-language-learning-v1/CLAUSE-REVIVAL-RESULT.md",
  why=(
    "with the donor on, the candidate pool went from zero to one, so step-level abstraction fixed discovery",
    "the acquired rule's sixteen development trials then all reported NO_MATCH, at 4425 matching-work units",
    "only four rows were eligible and every one of those targets was a Boolean tautology",
    "no task in the ecology essentially required the method that had been learned",
  ),
  terminates_at="STRUCTURE_ACQUIRED_IS_NOT_SUBSEQUENTLY_DEMANDED"),

O(observation_id="N8-HIDDEN-CAUSE-DIAGNOSIS", verdict="ACCUMULATION_RESIDUAL_CONFINED_TO_PROBE_COST",
  source="results/DIAGNOSIS_E2_V1.json",
  why=(
    "the governed greedy probe rule provably reproduced the hand-authored decision tree's ordering",
    "all three principled arms reached 59/59 against a 0.288 constant baseline",
    "the residual was 42 probe units of 573 and was memoisation of one boolean per checker and scope",
    "probe semantics were authored, so each episode was table inversion under a cost constraint",
  ),
  terminates_at="ONE_SHOT_DECISION_WITH_COMPLETE_INFORMATION"),

O(observation_id="N9-EAGER-DEPENDENCY", verdict="DOMINATED_BY_LAZY_RE_DERIVATION",
  source="results/DEPEND_E3_V1.json, capability-gated re-analysis",
  why=(
    "restricted to arms at precision and recall 1.0, eager discovery lost to lazy re-derivation on work and on stale survivors",
    "eager pays discovery for the whole store up front; lazy pays only for what is actually revoked",
    "the revocation schedule touched a small fraction of what had been discovered",
    "most of the structure the eager arm paid to discover was never queried",
  ),
  terminates_at="STRUCTURE_ACQUIRED_IS_NOT_SUBSEQUENTLY_DEMANDED"),

O(observation_id="N10-SCALAR-FACTORIZATION", verdict="PARENT_SUFFICIENT",
  source="research/independent-factorization-20260908/SESSION_RESULT.md",
  why=(
    "candidate, adaptive parent and global enumeration all attained the exact optimum in every generation case",
    "the adaptive parent ran the same generic algorithm with separate state",
    "so parent sufficiency held by construction rather than by independent implementation",
    "the comparison was built so that the parent shares the mechanism under test",
  ),
  terminates_at="PARENT_SHARES_THE_MECHANISM_UNDER_TEST"),

O(observation_id="N11-SPARSE-METHOD-ACQUISITION", verdict="FAILED_AT_REGISTERED_GRAMMAR",
  source="research/independent-factorization-20260908/SESSION_RESULT.md",
  why=(
    "382 of 384 candidate episodes remained ambiguous and both singleton proposals failed fresh checking",
    "four supplied examples plus four active probes did not separate 1528 candidate functions",
    "the probe budget was fixed in advance against a grammar of that size",
    "the instrument's resolution was set without reference to the hypothesis space it had to separate",
  ),
  terminates_at="PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED"),

O(observation_id="N12-SELF-EVOLUTION", verdict="AUTOML_PARENT_SUFFICIENT_BY_CONSTRUCTION",
  source="SzeChunYiu/ORION-OCM#149",
  why=(
    "the trajectory reached g0 to g1 to g2 to g2; the required third earned transition was not achieved",
    "existing signature-index and lazy-dependency alternatives explained both adopted changes",
    "the changes were selections from a human-authored library under a fixed external host policy",
    "the comparison was built so that the parent shares the mechanism under test",
  ),
  terminates_at="PARENT_SHARES_THE_MECHANISM_UNDER_TEST"),

O(observation_id="N13-INDEPENDENT-FACTORIZATION-PARENT", verdict="INDEPENDENT_PARENT_SUFFICIENT",
  source="results/INDEP_E8_V1.json",
  supersedes="N10-SCALAR-FACTORIZATION",
  why=(
    "a regression parent written from its own standard description, sharing no code path with the arm, "
    "beat it at 564.5 objective calls against 724.4 with both attaining the exact optimum everywhere",
    "steady-state calls were identical to the call and both recovered the same number of parameters, "
    "so the representation was not what separated them",
    "the whole gap was first-generation identification: the arm computed a full 2**n transform while "
    "the parent escalated degree only until the fit stopped improving",
    "the arm paid for every coefficient in the basis and the world only ever demanded the sparse ones",
  ),
  terminates_at="STRUCTURE_ACQUIRED_IS_NOT_SUBSEQUENTLY_DEMANDED"),
]


ROOTS = {
"ONE_SHOT_DECISION_WITH_COMPLETE_INFORMATION": dict(
  statement=(
    "The endpoints chosen were single decisions taken with all relevant information already "
    "present: which item is relevant, which cause holds, which level is required. In that regime "
    "an exact classical procedure is optimal by construction, so there is no room for a residual "
    "and persistence carries nothing forward."),
  why_it_happened=(
    "Single decisions are easy to score exactly against an oracle, which is what made them "
    "attractive for a programme that insists on exact ground truth."),
  consequence=(
    "These are not findings about persistent machinery. They are findings about the regime. A "
    "machine with memory cannot beat a correct one-shot procedure on a one-shot problem."),
  falsifier=(
    "Construct the same decisions inside a sequence where earlier decisions constrain later ones, "
    "and show the parent still ties. That would mean the regime was not the explanation."),
  fixable=True),

"STRUCTURE_ACQUIRED_IS_NOT_SUBSEQUENTLY_DEMANDED": dict(
  statement=(
    "The machine repeatedly paid to acquire structure that later tasks did not require. The clause "
    "donor learned a method that fired zero times because every eligible target was a tautology. "
    "The eager dependency arm discovered a graph most of which was never queried. The relevance "
    "arm rebuilt its index more often than it used it."),
  why_it_happened=(
    "Task ecologies were drawn independently, so the probability that a later task essentially "
    "requires structure acquired earlier was never controlled and, in most lanes, never measured. "
    "It appears to be near zero throughout."),
  consequence=(
    "Amortization has a demand term and the programme has only ever measured the supply term. "
    "Every INDEX_MAINTENANCE_DOMINATES and NO_DEVELOPMENT_BENEFIT verdict is consistent with a "
    "perfectly good mechanism facing no demand."),
  falsifier=(
    "Sweep reuse-opportunity density from zero to one with the mechanism and the parents fixed. If "
    "no density produces a crossover, the mechanism is at fault and this root is wrong."),
  fixable=True),

"PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED": dict(
  statement=(
    "The granularity at which the machine looks for structure was fixed at design time: one "
    "element at a time for dependencies, flat surface fragments for methods, a fixed probe budget "
    "against a grammar of 1528 functions. In each case the structure existed at a level the "
    "instrument could not express."),
  why_it_happened=(
    "Choosing the level is the hard part of the problem, and fixing it makes the experiment "
    "tractable and exactly scorable."),
  consequence=(
    "These are instrument-resolution failures, not learning failures. Leave-one-out cannot see "
    "disjunctive support however good the learner is."),
  falsifier=(
    "Let the machine choose its own probe granularity under a charged budget and show the failures "
    "persist. Experiment E1 did this for relevance and the cost dominated, which is evidence that "
    "adapting the level is expensive when demand is absent, and links this root to the one above."),
  fixable=True),

"PARENT_SHARES_THE_MECHANISM_UNDER_TEST": dict(
  statement=(
    "In two lanes the parent was the same generic algorithm holding separate state, so "
    "PARENT_SUFFICIENT was true by construction and carried no information about the architecture."),
  why_it_happened=(
    "Building a faithful strong parent is most easily done by reusing the arm's own implementation, "
    "and both sessions said so explicitly rather than hiding it."),
  consequence=(
    "These two verdicts should not be counted as evidence that a genuinely independent parent is "
    "sufficient. They are honest, and they are also nearly vacuous."),
  falsifier=(
    "Re-run with an independently implemented parent. If it still ties, the verdict becomes "
    "informative for the first time."),
  falsifier_status=(
    "HALF_FIRED. E8 (results/INDEP_E8_V1.json) supplied independent parents for the factorization "
    "lane. The verdict did not tie: the independent regression parent beat the arm outright, at "
    "0.779 of its objective calls. So N10's PARENT_SUFFICIENT is now informative and its content "
    "is a loss, not a vacuum. N12, the self-evolution lane, has not been re-run against an "
    "independently implemented parent, so this root stays open there and the entry stands."),
  fixable=True),

"GROUND_TRUTH_SHARED_AN_AUTHOR_WITH_THE_POLICY": dict(
  statement=(
    "Benchmark labels were produced by the same taxonomy the policy reasons in, so the policy was "
    "scored against its own categories."),
  why_it_happened="Planting a defect is the obvious way to obtain a labelled world cheaply.",
  consequence=(
    "Already measured and already fixed: authored labels agreed with an independent oracle on 53.4 "
    "per cent of worlds, and the corrected experiment stands."),
  falsifier="Already fired. This root is closed and its correction is in the record.",
  fixable=False),
}


#: Second-order recursion: do the roots themselves share a deeper cause?
DEEP_ROOTS = {
"ECOLOGY_HAS_NO_ACCUMULATION_STRUCTURE": dict(
  subsumes=("ONE_SHOT_DECISION_WITH_COMPLETE_INFORMATION",
            "STRUCTURE_ACQUIRED_IS_NOT_SUBSEQUENTLY_DEMANDED",
            "PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED"),
  statement=(
    "The first two roots are one fact seen from two sides. If tasks are drawn independently and "
    "each carries complete information, then nothing carries forward and nothing acquired is "
    "demanded. The third root sits downstream of the same fact: experiment E1 let the machine "
    "choose its own probe granularity and the maintenance cost dominated, which is what adapting "
    "an instrument costs when there is no demand to amortize it against."),
  the_missing_quantity=(
    "Reuse-opportunity density, rho: the fraction of future tasks whose solution essentially "
    "requires structure acquired earlier. Amortization is benefit = rho * savings-per-reuse * "
    "horizon, minus discovery, maintenance and storage. This programme has measured the subtracted "
    "terms exhaustively and has never measured rho."),
  evidence_that_rho_is_near_zero=(
    "In the clause donor it is exactly zero by construction: every eligible development target was "
    "a Boolean tautology, so no target could require the learned method. In the games, diagnosis "
    "and dependency lanes task instances were drawn independently, and rho was neither controlled "
    "nor reported. The single place a work advantage did appear -- the twelve-generation "
    "factorization study, and the episode-twelve payback in the self-evolution lane -- is the one "
    "place consecutive tasks shared structure, which is rho > 0."),
  consequence=(
    "The programme's central hypothesis is currently UNMEASURABLE rather than refuted. A verdict "
    "of INDEX_MAINTENANCE_DOMINATES or NO_DEVELOPMENT_BENEFIT in an ecology with rho near zero is "
    "the arithmetically expected outcome for a mechanism of any quality, so it discriminates "
    "nothing. Several preserved negatives therefore do not mean what they appear to mean, and this "
    "must be recorded without withdrawing any of them."),
  what_it_does_not_excuse=(
    "It does not rehabilitate the mechanisms. Parent sufficiency on one-shot decisions is still "
    "correct and still final for that regime, and raising rho cannot make an index stop matching a "
    "supplied-key lookup. It changes which experiments were ever capable of answering the "
    "question, not which answers were given."),
  falsifier=(
    "Sweep rho from zero to one with the mechanism, the parents, the budgets and the checker held "
    "fixed. If no density produces a crossover where the machine's cumulative cost falls below the "
    "strongest parent's at matched capability, then demand was not the binding constraint, this "
    "deep root is wrong, and the fault is in the mechanisms after all."),
  falsifier_outcome="PARTIALLY_FIRED",
  outcome=(
    "E7 ran the sweep (results/RHO_E7_V1.json, terminal "
    "CROSSOVER_ONLY_AGAINST_PARENTS_THAT_DO_NOT_SHARE_THE_MECHANISM). The root is CONFIRMED in "
    "part and REFUTED in part, and the refutation is the more useful half.\n\n"
    "Confirmed: density zero reproduced the negatives at both discovery costs, so the knob is the "
    "one the earlier experiments varied and the sweep is valid. Real crossovers appear at density "
    "0.05 against lazy re-derivation and against memoization, and the crossover point rises with "
    "discovery cost as predicted. Demand was therefore a genuine binding constraint for those "
    "comparisons, exactly as this root claimed.\n\n"
    "Refuted: there is no crossover at any density against a deferred-induction parent, which "
    "retains the evidence a derivation produced and defers induction until demand is proven. It is "
    "cheaper than the machine at every density at both discovery costs. So raising demand rescues "
    "PERSISTENCE and does not rescue EAGER ACQUISITION.\n\n"
    "The refined root: absent demand explained why persisting was worthless, but it never explained "
    "why acquiring eagerly was worse than acquiring on demand. That second question is about "
    "acquisition POLICY, not about the ecology and not about architecture, since the parent that "
    "beats the machine shares its mechanism and differs only in trigger. It is also the same shape "
    "as N9, where eager dependency discovery lost to lazy re-derivation, so the two are now one "
    "finding rather than two."),
  fixable=True),

"EAGER_ACQUISITION_IS_DOMINATED_BY_DEFERRED_ACQUISITION": dict(
  subsumes=("STRUCTURE_ACQUIRED_IS_NOT_SUBSEQUENTLY_DEMANDED",
            "PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED"),
  statement=(
    "Across four independent experiments, with four different mechanisms and four different "
    "parent sets, acquiring structure up front loses to deriving it when it is actually needed. "
    "In the first three the winning parent shared the machine's mechanism and differed only in "
    "WHEN it fired, which localised the loss to acquisition policy rather than representation, "
    "instrument resolution, or architecture -- but left open the objection that a parent built "
    "from the arm proves nothing. E8 closes that objection: its winning parent was implemented "
    "independently, from its own standard description, and the loss survived."),
  the_missing_quantity=(
    "A trigger. Every arm in this programme acquires on a schedule -- at admission, at install, at "
    "the end of an episode -- and none acquires on demonstrated demand."),
  evidence_that_rho_is_near_zero=(
    "E3: under the capability gate, eager dependency discovery lost to lazy re-derivation on both "
    "work and stale survivors. E7: no crossover at any reuse density against a deferred-induction "
    "parent that retains evidence and defers induction until demand is proven. E6: at N=850 lazy "
    "re-derivation reached precision and recall 1.0 with 141 interventions and 67350 total work, "
    "against the adaptive arm's 0.941 recall, 1936 interventions and 133525 work -- beating even "
    "the gifted ATMS ceiling that was handed its justifications for free. E8: an independently "
    "implemented regression parent beat the Walsh arm at 564.5 objective calls against 724.4, "
    "with steady-state cost identical to the call and the same parameters recovered, so the whole "
    "gap was the arm computing a full 2**n transform where the parent escalated degree only until "
    "the fit stopped improving. The arm paid for every coefficient in the basis; the world "
    "demanded only the sparse ones."),
  consequence=(
    "This supersedes the demand-density explanation as the primary root. Raising demand was "
    "necessary and turned out not to be sufficient: E7 showed it rescues persistence while leaving "
    "eager acquisition dominated. And E6 shows that letting the instrument choose its own "
    "granularity, which the probe-resolution root prescribed as its fix, does not rescue it "
    "either. Both earlier roots were real and both were upstream of this one. E8 additionally "
    "removes the shared-mechanism confound: the pattern is not an artifact of parents built out "
    "of the arm, because it reproduces against a parent built out of nothing but its own "
    "textbook description."),
  what_it_does_not_excuse=(
    "It is not a licence to call the architecture vindicated. Deferred acquisition is cheap in "
    "these worlds partly because evidence is perfectly retainable, so a derivation can always be "
    "redone later at the same price. Where re-deriving is impossible or the evidence is "
    "perishable, the comparison inverts and eager acquisition may be the only option. Nothing here "
    "measures that regime, and the retainability assumption is doing real work. E10 has since "
    "measured the neighbouring assumption -- that KEEPING is free and unbounded -- and found the "
    "sign reverses when it is dropped, which is why this root now carries a falsifier_status "
    "rather than standing unqualified."),
  falsifier=(
    "Build a world where evidence is perishable or re-derivation is strictly more expensive later, "
    "and show eager acquisition still loses. If it wins there, the finding is scoped to retainable "
    "evidence rather than general, which would be a narrowing and not a refutation."),
  falsifier_status=(
    "FIRED, AND THE ROOT IS NARROWED. E10 (results/RETAIN_E10_V1.json) built the world. It varied "
    "the half of the falsifier about the COST OF KEEPING rather than the half about "
    "perishability: retention was capped in bits and priced, so what to keep became a decision "
    "with an opportunity cost. Above a compressibility threshold the sign of the comparison "
    "reverses -- an online arm that keeps generalizations serves the same demand stream for as "
    "little as 0.379 of the work of a parent shown the entire future and evicting "
    "furthest-in-future, which is optimal over instance policies. The root therefore describes "
    "worlds with UNBOUNDED FREE RETENTION, which is every world this programme had built until "
    "now and which nobody had noticed was a constant. It is scoped, not refuted: at extension "
    "size one, and wherever the budget holds everything, the parents still win exactly as they "
    "did. The perishability half of the falsifier is still unrun."),
  fixable=True),

"COMPARISON_WAS_CONSTRUCTED_FROM_THE_ARM": dict(
  subsumes=("PARENT_SHARES_THE_MECHANISM_UNDER_TEST",),
  statement=(
    "In the factorization and self-evolution lanes the strongest parent was the arm's own generic "
    "algorithm holding separate state. Both sessions said so explicitly. PARENT_SUFFICIENT is then "
    "true by construction and carries no information."),
  the_missing_quantity="an independently implemented parent",
  evidence_that_rho_is_near_zero="not applicable",
  consequence=(
    "Two of the twelve verdicts are honest but nearly vacuous and should not be counted as "
    "evidence that a genuinely independent parent suffices."),
  what_it_does_not_excuse=(
    "It does not weaken the other ten verdicts, several of which used genuinely independent "
    "parents: an ordinary index, a nogood store, a hand-authored decision tree, an exact repair "
    "planner."),
  falsifier="re-run with an independent implementation; a tie then becomes informative",
  falsifier_status=(
    "HALF_FIRED on the factorization lane by E8 (results/INDEP_E8_V1.json), and the outcome was "
    "not a tie. The independent regression parent beat the arm at 0.779 of its objective calls, "
    "so N10's verdict is now informative and what it informs us of is a loss. The self-evolution "
    "lane N12 has not been re-run against an independent parent and this root still holds there, "
    "which is why the entry is not withdrawn."),
  fixable=True),
}


#: The experiment the analysis implies, specified so it cannot be rigged.
DECISIVE_EXPERIMENT = dict(
  name="RHO_SWEEP",
  question=(
    "Does a reuse-opportunity density exist at which persistent acquired structure amortizes "
    "against the strongest independent parent, and where is it?"),
  design=(
    "Hold the mechanism, the parents, the budgets, the checker and the horizon fixed. Vary one "
    "knob: rho, the fraction of tasks in the stream whose solution essentially requires structure "
    "acquired earlier. Sweep the full range including zero and one. Report the entire curve."),
  essential_requirement=(
    "'Essentially requires' must be certified, not assumed: removing the acquired structure must "
    "strictly increase the minimal solution cost for that task. A task solvable by a bypass does "
    "not count toward rho, and the certification is what stops rho from being a synonym for "
    "'tasks we made easy for ourselves'."),
  anti_rigging_controls=(
    "Publication constitution section 11 forbids making every environment one in which explicit "
    "reuse is optimal by construction. Three controls enforce that here. First, rho = 0 is in the "
    "sweep and must REPRODUCE the existing negatives; if it does not, the knob is not the one the "
    "old experiments varied and the whole sweep is void. Second, every parent runs at every rho, "
    "so a crossover must be a crossover against a parent that also benefits. Third, the reported "
    "object is the curve and the crossover point, never a single favourable rho."),
  prediction=(
    "Frozen before execution: the negatives reproduce at rho = 0; the machine's cumulative cost "
    "curve crosses the strongest parent's at some rho* strictly between 0 and 1; and rho* rises "
    "with discovery and maintenance cost."),
  falsifier=(
    "No crossover at any rho up to and including 1.0, at matched capability and with full "
    "accounting. That would refute the deep root and return the fault to the mechanisms."),
  claim_ceiling=(
    "Even a clean crossover would establish only that amortization is achievable in a synthetic "
    "ecology whose reuse density is set by hand. It would not establish that any real task ecology "
    "has that density, and the honest next question would immediately be what rho is in the "
    "domains anyone cares about."),
)


def build() -> dict:
    counts = Counter(o["terminates_at"] for o in OBSERVATIONS)
    return {
        "schema": "orion.root-cause-analysis.v1",
        "programme": "SzeChunYiu/ORION-OCM#143",
        "constitution": "SzeChunYiu/ORION-OCM#144",
        "theory": "SzeChunYiu/ORION-OCM#145, PR #150",
        "method": (
            "Ask why of each verdict, recursively, until the chains stop producing new answers. "
            "Cluster terminal statements. A root needs two or more independent chains; a single "
            "chain is a conjecture. Then recurse once more on the roots."),
        "authority": (
            "This analysis reinterprets evidence; it produces none and withdraws none. Every "
            "negative listed remains preserved exactly as recorded."),
        "observations": [
            {k: (list(v) if isinstance(v, tuple) else v) for k, v in o.items()}
            for o in OBSERVATIONS
        ],
        "first_order_roots": {
            k: dict(v, chains_supporting=counts.get(k, 0),
                    status="ROOT" if counts.get(k, 0) >= 2 else "CONJECTURE_SINGLE_CHAIN")
            for k, v in ROOTS.items()
        },
        "deep_roots": {
            k: dict({kk: (list(vv) if isinstance(vv, tuple) else vv) for kk, vv in v.items()},
                    chains_supporting=sum(counts.get(s, 0) for s in v["subsumes"]))
            for k, v in DEEP_ROOTS.items()
        },
        "decisive_experiment": DECISIVE_EXPERIMENT,
        "headline": (
            f"{sum(counts.get(s, 0) for s in DEEP_ROOTS['ECOLOGY_HAS_NO_ACCUMULATION_STRUCTURE']['subsumes'])} "
            f"of {len(OBSERVATIONS)} why-chains terminate on one deep root: the task ecologies had "
            "no accumulation structure. The programme measured every subtracted term of the "
            "amortization inequality and never measured its demand term. Several preserved "
            "negatives are therefore consistent with a sound mechanism facing no demand, which "
            "makes the central hypothesis unmeasurable in those ecologies rather than refuted."),
    }


def main() -> int:
    doc = build()
    (HERE / "ROOT_CAUSE_ANALYSIS_V1.json").write_text(json.dumps(doc, indent=2) + "\n")
    L = ["# ROOT_CAUSE_ANALYSIS_V1\n",
         "**GENERATED FILE — edit `root_cause.py`, then run `python root_cause.py`.**\n",
         "Recursive why-analysis over every negative result in the programme. This reinterprets "
         "evidence; it produces none and withdraws none.\n",
         f"> {doc['headline']}\n",
         "## Where the chains terminate\n",
         "| terminal statement | chains | status |", "|---|---|---|"]
    for k, v in doc["first_order_roots"].items():
        L.append(f"| {k} | {v['chains_supporting']} | {v['status']} |")
    L += ["", "## Observations and their why-chains\n"]
    for o in doc["observations"]:
        L.append(f"### {o['observation_id']} — `{o['verdict']}`\n")
        L.append(f"Source: `{o['source']}`\n")
        for i, w in enumerate(o["why"], 1):
            L.append(f"{i}. {w}")
        L.append(f"\n→ **{o['terminates_at']}**\n")
    L += ["## First-order roots\n"]
    for k, v in doc["first_order_roots"].items():
        L.append(f"### {k} ({v['status']}, {v['chains_supporting']} chains)\n")
        L.append(f"{v['statement']}\n")
        L.append(f"**Why it happened.** {v['why_it_happened']}\n")
        L.append(f"**Consequence.** {v['consequence']}\n")
        L.append(f"**Falsifier.** {v['falsifier']}\n")
        if v.get("falsifier_status"):
            L.append(f"**Falsifier status.** {v['falsifier_status']}\n")
    L += ["## Deep roots\n"]
    for k, v in doc["deep_roots"].items():
        L.append(f"### {k} ({v['chains_supporting']} chains, subsumes "
                 f"{', '.join(v['subsumes'])})\n")
        L.append(f"{v['statement']}\n")
        L.append(f"**The missing quantity.** {v['the_missing_quantity']}\n")
        if v["evidence_that_rho_is_near_zero"] != "not applicable":
            L.append(f"**Evidence it is near zero.** {v['evidence_that_rho_is_near_zero']}\n")
        L.append(f"**Consequence.** {v['consequence']}\n")
        L.append(f"**What it does not excuse.** {v['what_it_does_not_excuse']}\n")
        L.append(f"**Falsifier.** {v['falsifier']}\n")
        if v.get("falsifier_status"):
            L.append(f"**Falsifier status.** {v['falsifier_status']}\n")
    d = doc["decisive_experiment"]
    L += ["## Decisive experiment implied\n", f"### {d['name']}\n", f"{d['question']}\n",
          f"**Design.** {d['design']}\n",
          f"**What 'essentially requires' must mean.** {d['essential_requirement']}\n",
          f"**Anti-rigging controls.** {d['anti_rigging_controls']}\n",
          f"**Prediction.** {d['prediction']}\n", f"**Falsifier.** {d['falsifier']}\n",
          f"**Claim ceiling.** {d['claim_ceiling']}\n"]
    (HERE / "ROOT_CAUSE_ANALYSIS_V1.md").write_text("\n".join(L))
    print(f"wrote ROOT_CAUSE_ANALYSIS_V1: {len(doc['observations'])} observations, "
          f"{len(doc['first_order_roots'])} first-order roots, {len(doc['deep_roots'])} deep roots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
