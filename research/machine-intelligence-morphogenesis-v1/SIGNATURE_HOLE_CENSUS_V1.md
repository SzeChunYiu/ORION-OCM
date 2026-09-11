# Signature-space hole census v1 — first instrument aimed at the "undesigned form" question

Status: `EXPLORATORY_E0_THEORY_INSTRUMENT` · receipt `SIGNATURE_HOLE_CENSUS_V1.json` (sha256 inside)
· code `signature_hole_census.py` (stdlib, deterministic, runs in <1 s).
Question served (issue #377 §18, `UNKNOWN_MORPHOLOGY_PROGRAMME_V1.md` §3 "property-first
prediction"): *can the theory say, before any search, what an undesigned morphology would have to
look like?* This instrument answers a necessary sub-question: **at the resolution of the
label-free signature observables, where are the empty cells, and are they empty because nobody
built them or because the coordinate system is too coarse?**

## 1. What was enumerated

The lattice `S = theta_type × update_locality × feedback_dependence × execution_shape ×
store_discipline` from `MORPHOLOGY_SIGNATURES_V2.json`: 3 × 4 × 2⁴ × 5 × 6 = 5 760 raw cells. The
five frozen coherence constraints C1–C5 remove 2 773 (C1 "no update ⇒ no feedback" 1 350; C5
"dense update needs an array or fixed state" 869; C2/C3 numeric stores 245 each; C4
enumerate-test needs a signal 64), leaving **2 987 coherent cells**.

43 registered parent morphologies (the seven signatures `M0…M6` plus the Codex
`MORPHOLOGY_ATLAS_V1.md` families and the registration gaps found in pass 1) were assigned a
cell each, with a one-line rationale per assignment (receipt `occupant_table`). They occupy
**41 cells**. Hole cells: 2 946. Distance-to-nearest-occupant histogram: 703 at Hamming
distance 1, 1 880 at 2, 363 at 3, none at ≥ 4.

## 2. Findings

**F1 — Pass 1 holes were registration gaps, not undesigned forms.** The first run (34
occupants) reported structural pairwise holes such as `SAMPLE_SCORE × RULE_SET`,
`SAMPLE_SCORE × INDEXED_EXEMPLARS`, `STORE_MATCH × PARAMETER_ARRAY`, `LOCAL_O1 × likelihood`,
`ENUMERATE_TEST × INDEXED_EXEMPLARS`, `STORE_MATCH × TERM_LIBRARY`, `DISCRETE × DENSE_LINEAR`.
Each turned out to be occupied by a designed system missing from the atlas: ProbLog/PRISM,
Dirichlet-process mixtures with Gibbs sampling, Kanerva sparse distributed memory, conjugate
exponential-family Bayesian updating, case-based planning (CHEF-class), OCM's own
method-library serving, and batch re-induction. **Consequence:** the census is, first of all, a
completeness check on the parent atlas; every structural hole must be attacked as a possible
registration gap before it is called a candidate region. Nine occupants were added in pass 2.

**F2 — After completion, the remaining structural holes are of three kinds.**
Structural pairwise holes (projections not involving `feedback_dependence`) after pass 2:

| projection | unused pairs | reading |
|---|---|---|
| theta × locality | `BOUNDED_NUMERIC×NONE`, `MIXED×NONE` | inert numeric machines: fixed-function DSP-like circuits; designed but not "learning" — degenerate |
| theta × exec | `DISCRETE×SAMPLE_SCORE` | a purely discrete sample/score cycle with no numeric weights (e.g. uniform-random rewriting with accept/reject on a discrete test) — plausible, cheap, unregistered; **candidate** |
| theta × store | `BOUNDED_NUMERIC×{RULE_SET, TERM_LIBRARY, TRACE_DISTRIBUTION}` | numeric-only systems whose growing store is rules/terms/traces: numeric term libraries exist as *hybrids* (MIXED); pure-numeric versions would be "weighted rule/term stores without discrete structure" — coarse; the MIXED versions are occupied |
| locality × exec | `DENSE×{ENUMERATE_TEST, STORE_MATCH}`, `LOCAL_O1×SAMPLE_SCORE`, `SPARSE×STORE_MATCH`, `NONE×{ACYCLIC, SAMPLE_SCORE, STORE_MATCH}` | dense update inside a search or match cycle = "re-synthesize everything per event" (degenerate); `LOCAL_O1×SAMPLE_SCORE` = a sampler whose per-event update is O(1) (single-particle / streaming MC) — **candidate**; `SPARSE×STORE_MATCH` = a match-cycle store with sublinear structural updates (index rebalancing) — plausible, near-degenerate |
| locality × store | `LOCAL_O1×TRACE_DISTRIBUTION`, `NONE×{…}` | an O(1)-update trace distribution (streaming posterior over executions) — **candidate**; inert stores are degenerate |
| exec × store | `ACYCLIC×{TERM_LIBRARY, TRACE_DISTRIBUTION}`, `BOUNDED_LOOP×{TERM_LIBRARY, TRACE_DISTRIBUTION}`, `ENUMERATE_TEST×{NONE, TRACE_DISTRIBUTION}`, `SAMPLE_SCORE×NONE`, `STORE_MATCH×{NONE, TRACE_DISTRIBUTION}` | libraries/trace-distributions executed without a search or sample cycle (compiled libraries; amortized posteriors) — several are the "compiled" form of an occupied cycle-form and would compile to it cheaply (GMI-T3 band lemma says: same class at small K) |

**F3 — One multi-occupant cell.** `DISCRETE / LOCAL_O1 / {exact_counterexample} / STORE_MATCH /
RULE_SET` holds Soar-class production systems, TMS/ATMS and blackboard systems. At this
resolution they are one class; whether they are one morphology (GMI-T3) is a bounded-compilation
question the census cannot answer — but it is a concrete Stage D pair to test (predicted:
mutual K-bounded, `desc`/`rev` constants differ by the justification records).

**F4 — Coarseness is the main result.** 41 occupied cells out of 2 987 coherent ones means the
five observables are far coarser than the designed landscape is dense in some directions (feedback
subsets: 16 values, most used only in singletons) and about right in others (`update_locality`
and `store_discipline` separate almost every registered family). Two designed pairs land in one
cell that the theory would want to separate — SGD vs. evolution strategies on the same
parameters (both `DENSE / scalar_loss / PARAMETER_ARRAY`), and in-context learning vs.
VSA/HDC memories — because the observables record *where and how much* state changes, not *how
the change is computed*. That is by design (the observables are resource-shape coordinates, GMI-T10-A),
and it fixes the meaning of "undesigned form" for this programme:

> An undesigned morphology must differ from every registered form either (a) in one of the
> registered structural cells that survives F1–F2 as a non-degenerate candidate, or (b) at a
> resolution *finer* than these five observables — i.e. in the charged constants of `Compile_B`
> (Stage D) or in a sixth observable not yet registered. Case (b) is where Codex's phase-hole
> programme and the band lemma (GMI-T3) live; case (a) is what this census pre-registers.

## 3. Pre-registered candidate regions (case (a)), frozen now

From F2, the structural holes that are neither degenerate ("inert", "re-synthesize everything")
nor the compiled twin of an occupied cycle-form:

| id | cell (theta / locality / exec / store) | property vector an instance must show | ecology where it could be favoured (from `ECOLOGY_AXES_V2.json`) |
|---|---|---|---|
| HOLE-A | `DISCRETE / SPARSE or LOCAL_O1 / SAMPLE_SCORE / RULE_SET or TERM_LIBRARY` | stochastic rewriting with discrete accept/reject, no numeric weights, sublinear per-event change | noise present, exact verification available, small data (`PH-3`∩`PH-2`) |
| HOLE-B | `BOUNDED_NUMERIC or MIXED / LOCAL_O1 / SAMPLE_SCORE / TRACE_DISTRIBUTION` | streaming posterior over executions with O(1) per-event update (single-particle / conjugate-trace) | partial observability + frequent revision (`PH-3` × `PH-REV`) |
| HOLE-C | `MIXED / SPARSE_SUBLINEAR / STORE_MATCH / TERM_LIBRARY` with `{likelihood_score, exact_counterexample}` | a method library matched by applicability *and* scored by likelihood, sublinear structural updates | statistical input + exact obligations + heterogeneous verification (`PH-4`) — the region OCM's own morphology sits next to |

These are **not predictions that such forms exist or win**; they are the only regions where a
positive answer to the ultimate question can be *reported* at this resolution without first
refining the observables. A neutral search (D6, not yet authorized) that returns a candidate must
be classified into an occupied cell, one of HOLE-A/B/C, or force a sixth observable — each is a
falsifiable outcome, and only U4+ of `UNKNOWN_MORPHOLOGY_PROGRAMME_V1.md` §7 counts as support.

## 4. Nearest false generalizations (registered)

- "2 946 holes ⇒ 2 946 undiscovered forms": false; F1 shows holes are first registration gaps,
  F2 shows most survivors are degenerate or compiled twins.
- "One cell ⇒ one morphology": false; the cell is a resolution class, morphology identity needs
  GMI-T3's bounded compilation (F3).
- "An occupied cell cannot hold an undesigned form": false; case (b) above.

## 5. What would change the census

Adding a sixth observable (e.g. `update_computation ∈ {derivative, sampling, enumeration,
counting}`) splits several cells and is the next refinement if Stage D constants show that
cell-mates differ by more than the band on `upd`. That decision is deferred to Stage D evidence,
not taken now.
