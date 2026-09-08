"""Disposition of every negative result: what can be solved, and what cannot.

The instruction to "solve all negative results" needs a distinction the programme
has not yet written down. Some negatives are **correctable design faults**: the
experiment could not have detected the effect it was looking for, so its verdict
is about the instrument. Others are **correct findings**: an ordinary index really
does match a supplied-key lookup, and no amount of engineering changes that.

Treating the second kind as a problem to be solved is how a programme starts
optimising against its own benchmarks. So each negative here gets one of four
dispositions, and the count of each is reported rather than hidden.

``CORRECT_FINDING``        true as stated; not solvable and must not be attacked
``CORRECTABLE``            the experiment could not detect the effect; fix identified
``SUPERSEDED``             a later experiment already replaced it
``NARROW``                 true at its scope; the scope was too small to be interesting

Nothing here withdraws a result. A negative marked CORRECTABLE keeps its verdict
until a replacement experiment reports; the disposition says only that the verdict
does not answer the question it was asked.
"""

from __future__ import annotations

import json
import pathlib
from collections import Counter

HERE = pathlib.Path(__file__).parent

DISPOSITIONS = ("CORRECT_FINDING", "CORRECTABLE", "SUPERSEDED", "NARROW")
FIX_STATUS = ("RUNNING", "NOT_STARTED", "DONE", "NONE_POSSIBLE")


def N(**kw):
    base = dict(negative_id="", verdict="", root="", disposition="", why="",
                what_solved_would_mean="", fix="", fix_status="", outcome="", preserved=True)
    base.update(kw)
    return base


NEGATIVES = [
N(negative_id="N1-SUPPLIED-KEY-LOOKUP", verdict="PARENT_SUFFICIENT",
  root="ONE_SHOT_DECISION_WITH_COMPLETE_INFORMATION",
  disposition="CORRECT_FINDING",
  why="An ordinary index matched k, k/N, query work and correctness exactly at every scale. That "
      "is what an index is for. The key was supplied, so nothing was being asked of the machine.",
  what_solved_would_mean="Nothing. There is no version of this experiment in which a machine with "
                         "memory beats a correct lookup on a supplied key. The only improvement "
                         "available was to stop describing it as cognition, and claim C1 already "
                         "forbids that wording.",
  fix="none; the wording ceiling in CLAIM_LEDGER_V1 is the whole remedy",
  fix_status="NONE_POSSIBLE"),

N(negative_id="N2-FAILURE-MEMORY", verdict="PARENT_SUFFICIENT",
  root="ONE_SHOT_DECISION_WITH_COMPLETE_INFORMATION",
  disposition="NARROW",
  why="A full-strength nogood parent tied on four of seven worlds and avoided all 640 avoidable "
      "work units. True, but every arm was handed the correct cause, so each episode was a single "
      "classification with complete information.",
  what_solved_would_mean="A regime where the cause must be inferred and where a scope repeats, so "
                         "that not re-paying a diagnosis is worth something. E2 tested exactly "
                         "that and the residual came back as memoisation, 42 probe units of 573.",
  fix="E2 diagnosis with the cause hidden", fix_status="DONE"),

N(negative_id="N3-ESCALATION-ARTIFACT", verdict="GENERATOR_ARTIFACT",
  root="GROUND_TRUTH_SHARED_AN_AUTHOR_WITH_THE_POLICY",
  disposition="SUPERSEDED",
  why="Ground truth was the generator's intent and the generator shared the policy's taxonomy. "
      "Authored labels agreed with an independent oracle on 53.4 per cent of worlds.",
  what_solved_would_mean="Blind perturbation with the level recovered by exhaustive repair search, "
                         "which is what E4 did. The corrected number, 1736/2000, stands and the "
                         "lead over the fully-resourced parent is 0.7 points.",
  fix="E4 independent escalation worlds", fix_status="DONE"),

N(negative_id="N4-LEAVE-ONE-OUT", verdict="STRUCTURALLY_INCOMPLETE",
  root="PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED",
  disposition="CORRECTABLE",
  why="16 to 25 per cent of methods carried redundant support, which single-element ablation "
      "cannot see by construction. The instrument could not express the structure it sought.",
  what_solved_would_mean="Discovering the family of MINIMAL SUPPORT SETS rather than one "
                         "dependency set, under a charged intervention budget, at precision and "
                         "recall matching an exhaustive powerset oracle.",
  fix="E6 support-family discovery with adaptive group ablation", fix_status="DONE",
  outcome="INSTRUMENT_FIXED, ARM_STILL_DOMINATED. E6 built the instrument the fix called for and "
          "it works: adaptive group ablation reaches precision 1.0 and recall 1.0 at the "
          "registered scale, against leave-one-out's recall of 0.409 -- 0.00 on ALTERNATIVE_"
          "SUPPORTS, the exact C11 shape, and 0.50 on REDUNDANT_SUPPORTS, where it returns a true "
          "singleton, stops with half the family, and gives no signal that anything is missing. "
          "So N4's diagnosis is confirmed and its instrument is repaired. The arm still lost: "
          "lazy_parent, which discovers nothing and re-derives on demand, reached the same "
          "precision and recall for half the work at every scale, and under the capability gate "
          "the arm is not even admissible at 10x. Recorded as the fourth demonstration that the "
          "fault is the acquisition trigger and not the instrument."),

N(negative_id="N5-LEARNED-RELEVANCE", verdict="INDEX_MAINTENANCE_DOMINATES",
  root="STRUCTURE_ACQUIRED_IS_NOT_SUBSEQUENTLY_DEMANDED",
  disposition="CORRECTABLE",
  why="Two separate causes, and the receipt names both. The re-index search rescans the entire "
      "feature language from scratch on every repair, and the registered stream was 50 queries so "
      "there was almost nothing to amortize against.",
  what_solved_would_mean="Either an incremental re-index that repairs only the colliding buckets, "
                         "or a stream long enough and dense enough in reuse for the rebuild to pay "
                         "back. The receipt already concedes the first: an incremental search "
                         "would cost materially less and was not run.",
  fix="E9 incremental re-index (DONE, terminal solved); E7 rho sweep addresses the demand side",
  fix_status="DONE",
  outcome="INDEX_MAINTENANCE_TERMINAL_SOLVED. Monotone resumption plus early exit cut index work "
          "by 68.2 per cent at 30x with the SAME feature chosen, identical query work and "
          "identical correctness, so capability provably did not move. Payback against exhaustive "
          "scan now arrives at every registered scale: at 30x the crossover falls from 97.9 "
          "queries to 31.1 against a stream of 50. PARENT_SUFFICIENT nonetheless STANDS: the "
          "hand-specified key remains cheaper in total by 10.4x at 30x and 7.3x at 46x. The "
          "machine's query work falls with N while the parent's rises, so a crossover in N is "
          "implied, but it is not reached by 46x and the registered draw is exhausted, so it is "
          "unresolved rather than answered."),

N(negative_id="N6-UNARY-ACQUISITION", verdict="NO_METHOD_ACQUIRED",
  root="PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED",
  disposition="SUPERSEDED",
  why="Three independently checked sound fragments were all singletons because flat fragments "
      "differ while the intermediate dependency step recurs.",
  what_solved_would_mean="Abstraction at the step level. PR #147's clause donor did it and the "
                         "candidate pool went from zero to one, so this negative is solved at the "
                         "discovery level. It was replaced by a different failure, N7.",
  fix="PR #147 clause donor", fix_status="DONE"),

N(negative_id="N7-CLAUSE-DONOR", verdict="NO_DEVELOPMENT_BENEFIT",
  root="STRUCTURE_ACQUIRED_IS_NOT_SUBSEQUENTLY_DEMANDED",
  disposition="CORRECTABLE",
  why="The acquired method fired zero times because every eligible development target was a "
      "Boolean tautology. Reuse opportunity was exactly zero by construction, so the verdict "
      "measures the ecology and not the method.",
  what_solved_would_mean="The same discovered schema run against certified essential-composite "
                         "targets AND against a matched tautological control, with benefit on the "
                         "first and none on the second. Benefit indifferent to the contrast would "
                         "mean the gain was retrieval, not composition.",
  fix="E7 rho sweep (DONE) supplied the density side; E5 (DONE) certified the opportunity "
      "directly",
  fix_status="DONE",
  outcome="E7 partially settles this. With reuse opportunity raised from zero, the machine does "
          "beat lazy re-derivation and memoization from density 0.05 upward, so the clause donor's "
          "zero-opportunity ecology genuinely was masking a working mechanism. But a "
          "deferred-induction parent, which retains evidence and induces only once demand is "
          "proven, is cheaper at every density. Opportunity was necessary and is not sufficient. "
          "E5 then measured opportunity directly instead of varying it: with an essential "
          "composite opportunity CERTIFIED to exist, the acquired schema saves 54 work units, and "
          "on rows where it is certified NOT to exist the same schema costs 235. The two sets are "
          "never pooled. So N7's ecology was the whole of N7: the method was sound and the "
          "ecology had no rows that needed it."),

N(negative_id="N8-DIAGNOSIS-RESIDUAL", verdict="ACCUMULATION_RESIDUAL_CONFINED_TO_PROBE_COST",
  root="ONE_SHOT_DECISION_WITH_COMPLETE_INFORMATION",
  disposition="CORRECT_FINDING",
  why="The governed greedy probe rule PROVABLY reproduces the hand-authored decision tree's "
      "ordering. That is a proof, not a measurement, and no ecology changes it.",
  what_solved_would_mean="Nothing about ordering. The open question is different: probe semantics "
                         "were authored, so this was table inversion under a cost constraint. "
                         "Whether a machine can learn what a probe MEANS is untouched and is a "
                         "separate experiment.",
  fix="none possible inside E2. The result is correct and its residual could not have "
      "been larger: with the probe table authored there was nothing left in that world to "
      "learn. What N8 needs is a SUCCESSOR world, not a repair",
  successor="E11, results/PROBESEM_E11_V1.json",
  fix_status="NONE_POSSIBLE",
  outcome="SUCCESSOR RUN. The standing decision recorded here previously -- that "
          "learning probe semantics was a different experiment rather than a repair -- was "
          "an explanation, not a resolution -- is now discharged, and E11 withdraws "
          "the gift. E2's expected_outcome table is hidden and must be induced from bought "
          "observations plus the cause revealed on resolution; E2's own table is a member "
          "of the world space, so E11 contains E2 rather than replacing it. The semantics "
          "learner reaches the 0.90 accuracy target on 40 of 41 worlds against the mapping "
          "parent's 31, and in 95 resolved cases against 121 on the worlds both solved. It "
          "does not beat the arm handed the true table, which is the ceiling and is not "
          "claimed against. The narrowing is reported beside it: a naive-Bayes parent "
          "holding per-probe frequencies and no table needs 112, so roughly a third of the "
          "gap is available without representing semantics at all."),

N(negative_id="N9-EAGER-DEPENDENCY", verdict="DOMINATED_BY_LAZY_RE_DERIVATION",
  root="STRUCTURE_ACQUIRED_IS_NOT_SUBSEQUENTLY_DEMANDED",
  disposition="CORRECTABLE",
  why="Eager discovery pays for the whole store up front; lazy pays only for what is revoked. The "
      "revocation schedule touched a small fraction of what was discovered, so most of the eager "
      "arm's investment was never queried.",
  what_solved_would_mean="Beating lazy re-derivation on TOTAL work at matched correctness, which "
                         "requires either a revocation density high enough to amortize, or a "
                         "cheaper discovery mechanism. E6 must beat lazy explicitly, not merely "
                         "beat leave-one-out.",
  fix="E6 with lazy_parent as the arm to beat (DONE); E7 for the density side (DONE); E10 "
      "(DONE) found the retention condition the whole finding depends on",
  fix_status="DONE",
  outcome="E7 shows this is not a dependency-specific defect. The same shape appears in method "
          "acquisition: eager loses to deferred at every reuse density, against a parent sharing "
          "the mechanism and differing only in when it fires. N9 and N7 are therefore one finding "
          "about acquisition policy, not two about different subsystems. E10 then found the "
          "condition that finding depends on. Every world behind it gave retention away free and "
          "unbounded, and there retaining nothing is provably optimal, so eager acquisition was "
          "losing to arithmetic rather than to a better policy. Bound the store in bits and price "
          "it, and above a compressibility threshold an ONLINE arm keeping generalizations beats "
          "a parent shown the entire future and keeping instances -- 0.379 of its work at best. "
          "N9 is therefore SCOPED to free unbounded retention, not withdrawn: at extension size "
          "one, and wherever the budget holds everything, it reproduces exactly."),

N(negative_id="N10-SCALAR-FACTORIZATION", verdict="PARENT_SUFFICIENT",
  root="PARENT_SHARES_THE_MECHANISM_UNDER_TEST",
  disposition="CORRECTABLE",
  why="The adaptive parent ran the same generic algorithm with separate state, so parent "
      "sufficiency held by construction and carried no information about the architecture.",
  what_solved_would_mean="An INDEPENDENTLY IMPLEMENTED parent given the same information. If it "
                         "still ties, the verdict becomes informative for the first time; if it "
                         "does not, the original verdict was an artifact of shared code.",
  fix="independent re-implementation of the factorization learner",
  fix_status="DONE",
  outcome="VERDICT_NOW_INFORMATIVE, AND_IT_IS_A_LOSS. E8 supplied parents written from their own "
          "standard descriptions, sharing no code path with the arm; a test walks the import "
          "graph and the string 'walsh' does not occur in the parent module. The independent "
          "regression parent did not tie -- it won, at 564.5 objective calls against 724.4. So "
          "the original PARENT_SUFFICIENT was not an artifact of shared code, and the correction "
          "makes the negative stronger rather than weaker. E8 also localises it: steady-state "
          "calls were identical to the call and the same parameters were recovered, so the gap "
          "was entirely first-generation identification -- a full 2**n transform against "
          "degree-escalating least squares. Under drift the capability gate fires on the arm "
          "itself: it refits a support the world has moved, its own 4-point audit passes anyway, "
          "and its argmax lands 4 per cent low. That audit is not a staleness certificate."),

N(negative_id="N11-SPARSE-ACQUISITION", verdict="FAILED_AT_REGISTERED_GRAMMAR",
  root="PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED",
  disposition="CORRECTABLE",
  why="Four supplied examples plus four active probes did not separate 1528 candidate functions; "
      "382 of 384 episodes stayed ambiguous. The probe budget was set without reference to the "
      "hypothesis space it had to separate.",
  what_solved_would_mean="A probe budget derived from the version space rather than fixed in "
                         "advance, or a discovery level at which the space is smaller. The "
                         "information-theoretic floor is computable here and was never computed.",
  fix="E5 method discovery against DreamCoder and Stitch; the explicit "
      "budget-versus-version-space calculation is still NOT STARTED",
  fix_status="DONE",
  outcome="DIAGNOSIS_SUPERSEDED. N11 blamed the instrument: a probe budget fixed without "
          "reference to the hypothesis space. E5 ran the strongest available discovery parents "
          "and they closed the gap COMPLETELY -- DreamCoder and Stitch found the arm's composite "
          "and three more, so no discovery advantage is claimed against library learning on this "
          "draw. Discovery was therefore not the bottleneck, which means N11's diagnosis, though "
          "reasonable, was aimed at the wrong stage. What separated the arms was admission: "
          "MDL-only acceptance with no support gate keeps macros that pay no rent, leaving both "
          "library learners net-harmful on every set including where the opportunity exists. The "
          "information-theoretic floor on the probe budget is still not computed and that piece "
          "of the fix remains open; it is now a smaller question than N11 assumed."),

N(negative_id="N12-SELF-EVOLUTION", verdict="AUTOML_PARENT_SUFFICIENT_BY_CONSTRUCTION",
  root="PARENT_SHARES_THE_MECHANISM_UNDER_TEST",
  disposition="CORRECTABLE",
  why="Both adopted changes were selections from a human-authored library under a fixed external "
      "host policy, and existing alternatives explained them. The required third earned transition "
      "was not achieved.",
  what_solved_would_mean="Three earned transitions with an independently implemented AutoML parent "
                         "at matched information and lifecycle powers, and at least two materially "
                         "different learned changes surviving ablation.",
  fix="issue #149's own exit obligations; NOT STARTED in this lane",
  fix_status="NOT_STARTED",
  outcome="BLOCKED ON ANOTHER LANE, AND THE BLOCK IS REAL. N12's root is that the parent "
          "shared the mechanism under test. E8 discharged exactly that root for the "
          "factorization lane by supplying independently implemented parents, and the verdict "
          "became informative -- the independent parent won. The same discharge for N12 needs a "
          "real M11 runtime and issue #149's own exit obligations, which are not in this lane "
          "and cannot be simulated here without rebuilding the thing under test. Recorded as "
          "the one negative in the ledger whose fix is identified, feasible, and not available "
          "to the session holding the ledger."),
]


def build() -> dict:
    counts = Counter(n["disposition"] for n in NEGATIVES)
    status = Counter(n["fix_status"] for n in NEGATIVES)
    return {
        "schema": "orion.negative-disposition.v1",
        "programme": "SzeChunYiu/ORION-OCM#143",
        "authority": (
            "This assigns each negative a disposition. It withdraws none of them and produces no "
            "new evidence. A negative marked CORRECTABLE keeps its verdict until a replacement "
            "experiment reports; the disposition says only that the verdict does not answer the "
            "question it was asked."),
        "counts_by_disposition": dict(counts),
        "counts_by_fix_status": dict(status),
        "solvable": sum(v for k, v in counts.items() if k == "CORRECTABLE"),
        "not_solvable": sum(v for k, v in counts.items()
                            if k in ("CORRECT_FINDING", "NARROW")),
        "already_solved": counts.get("SUPERSEDED", 0),
        "negatives": NEGATIVES,
        "headline": (
            f"Of {len(NEGATIVES)} negatives, {counts.get('CORRECTABLE', 0)} are correctable design "
            f"faults with an identified fix, {counts.get('SUPERSEDED', 0)} have already been "
            f"superseded by a later experiment, and "
            f"{counts.get('CORRECT_FINDING', 0) + counts.get('NARROW', 0)} are true as stated and "
            "must not be attacked. Solving the programme's negatives means fixing the first group "
            "and leaving the third alone."),
    }


def main() -> int:
    doc = build()
    (HERE / "NEGATIVE_DISPOSITION_V1.json").write_text(json.dumps(doc, indent=2) + "\n")
    L = ["# NEGATIVE_DISPOSITION_V1\n",
         "**GENERATED FILE — edit `disposition.py`, then run `python disposition.py`.**\n",
         f"> {doc['headline']}\n",
         "Some negatives are correctable design faults: the experiment could not have detected the "
         "effect it was looking for. Others are correct findings. Treating the second kind as a "
         "problem to be solved is how a programme starts optimising against its own benchmarks, so "
         "the two are separated here and the counts are reported rather than hidden.\n",
         "| negative | verdict | disposition | fix status |", "|---|---|---|---|"]
    for n in NEGATIVES:
        L.append(f"| {n['negative_id']} | `{n['verdict']}` | **{n['disposition']}** "
                 f"| {n['fix_status']} |")
    L.append("")
    for n in NEGATIVES:
        L.append(f"## {n['negative_id']} — {n['disposition']}\n")
        L.append(f"**Verdict.** `{n['verdict']}` · **Root.** {n['root']}\n")
        L.append(f"**Why this disposition.** {n['why']}\n")
        L.append(f"**What solved would mean.** {n['what_solved_would_mean']}\n")
        L.append(f"**Fix.** {n['fix']} · **Status.** `{n['fix_status']}`\n")
    (HERE / "NEGATIVE_DISPOSITION_V1.md").write_text("\n".join(L))
    print(f"wrote NEGATIVE_DISPOSITION_V1: {dict(counts_ := Counter(n['disposition'] for n in NEGATIVES))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
