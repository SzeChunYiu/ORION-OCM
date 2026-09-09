# FNA-4 protocol — library/synthesis learner parent suite for #62 — frozen before execution

**Issue #214 work package FNA-4, target #62 (experience consolidation). Base
`86ddd9bcedfb48de804fbb68d599f00ebd8316ba`. Evidence class E1 / L1: planted task worlds,
one author, one population. No neural arm is run.**

## The question

#62 asks whether solved and failed experience can be consolidated into persistent
epistemically governed structure that makes **future composition cheaper**:

    C_future(T_j | E_t) < C_future(T_j | E_0)

FNA-4's contribution is the **library/synthesis family of parents**: does OCM need anything
beyond the strongest classical library learner for this, and does the learned library pay
back its own acquisition when everything is charged?

The substrate is main's own composition discipline, read from source (not rebuilt):
operators are immutable catalogue entries with typed inputs, executed backends and checkers
(`runtime/solve.py` OperatorSpec/compose_stage/check_stage); candidate selection goes
through the rarest-input inverted index (`runtime/operator_index.py`); candidates carry
warrant profiles bridged by meet (KS-T20); contradictions register as nogoods
(`kso/nogoods.py`). Operators here are **sequence-composed**: solving a task means finding
a chain of catalogue applications whose final atom passes the task's checker.

## Frozen world

Typed data algebra, stdlib only. Types `raw | tokens | scalar`. Surface tags on initial
atoms (`raw:csv`, `raw:jsonl`) are part of atom identity. Primitives:

```
parse:csv|jsonl            raw->tokens
filter:eq:f0|f1|f2         tokens->tokens
sort:asc|desc:f0|f1|f2     tokens->tokens
dedupe:stable              tokens->tokens
merge:2                    tokens x tokens -> tokens   (bag union, associative+commutative)
agg:sum|mean:f0|f1|f2,     tokens->scalar
agg:count                  tokens->scalar
scale:2|3                  scalar->scalar
zip:count                  tokens->scalar   (held-out family only)
```

Task families (the recurring composition patterns #62's E_t would see):

- **F1 PIPE**: parse -> filter -> sort -> agg [-> scale]. Param product ~200.
- **F2 MERGE-AC**: parse x2 -> merge -> dedupe -> agg. `merge` is AC, so variants of the
  same task exist as different orderings — the structure an e-graph canonicalizes and
  anti-unification alone does not.
- **F3 ZIP (held out)**: parse -> zip:count [-> scale]. Shares no contiguous 2-segment with
  F1/F2. Predicted NO transfer; measures harmful transfer and fallback cost.

Fresh tasks are new data payloads + new parameter draws from the same family generators
(deterministic salts, disjoint from any tuning salt). Acquisition stream and test stream
are disjoint.

## Frozen cost model (all integers, one commensurable unit)

Following FNA-1c's discipline: **one unit = one backend simulation, one checker call, one
posting read, or one learner work step** (anti-unification comparison, e-graph rewrite,
usefulness evaluation, nogood probe). No tunable conversion factor exists. A macro never
makes execution free: applying a macro charges one simulation per primitive step inside it
plus one checker call — the physics still runs. What a macro saves is **search**: the
posting reads, the deadend expansions and the checker calls on candidates that a solved
family structure would never have tried. Acquisition (learner work over the corpus),
selection (macro-domain enumeration is charged simulation-by-simulation), maintenance
(revocation revalidation) and specialization (CEGIS refinement) are all charged.

## Frozen arms

1. `NO_LIBRARY` — incumbent: breadth-first composition over the catalogue via the
   production-type inverted index (rarest-input anchor; postings_examined charged), every
   simulation and every goal checker call charged.
2. `CHUNK` — Soar-style exact-difference chunking: each solved composition is stored keyed
   by its exact surface+parameter signature; reuse only on exact match (no abstraction).
3. `AU_PAIR` — Reynolds anti-unification, incremental: anti-unify each new solved trace
   against stored traces; admit a pattern when the same skeleton of length >= 2 recurs.
4. `STITCH` — top-down: repeatedly search for the single abstraction with maximum
   usefulness (compression = uses x (body-1) - definition), rewrite the corpus, repeat to
   budget. No neural guide, by construction.
5. `EGGRAPH` — equality saturation over the trace corpus: union-find over segments,
   saturate under dedup + merge-AC rewrites to a node budget, extract shared classes by
   compression, admit as macros.
6. `NOGOOD_ONLY` — failed-misfire registration only (hard misfires keyed by operator +
   surface-tagged atom), probe charged; no library.
7. `STITCH_NOGOOD_CEGIS` — combined OCM-shaped arm: library + nogoods + CEGIS
   specialization of a macro's hole domains from misfire counterexamples (each refinement
   charged).
8. `ORACLE_TELEPORT` — upper bound, labelled ORACLE: the family's true patterns given at
   zero acquisition cost, one charged structural application each. Never a result.

## Frozen required measurements

- **Fresh-task actual use** (not replay): macro hit counts on test tasks with new payloads
  and new parameters; replayed acquisition tasks do not count.
- **Ablation/revocation**: (a) library removed mid-stream => per-task cost regresses to
  `NO_LIBRARY` (asserted); (b) revoke a primitive's registration evidence => exactly the
  macros whose warrant meets it die (H-EC3: revision cone, stale survivors, collateral);
  independent macros survive and keep working.
- **Parent parity**: identical task streams, identical information (the acquisition traces
  are the only experience any learner sees), identical cost model.
- **Whole payback**: lifetime curve = acquisition + stream cost vs `NO_LIBRARY` over
  stream length; break-even task count; and the **critical repeat rate** r* — the boundary
  below which no horizon pays (the FNA-1d critical-edit-rate analogue, in family-repeat
  rate).
- Warrant semantics: every macro carries `meet` of its constituent primitive warrants
  (KS-T20 bridge rule, same as compose_stage); admission is content-hashed.

## Registered predictions (before any scored run)

- **P1** `CHUNK` scores 0 fresh-task hits (parameters differ) — caching is not
  consolidation; abstraction is load-bearing.
- **P2** `AU_PAIR` and `STITCH` reach finite lifetime break-even on a same-family stream;
  `STITCH` >= `AU_PAIR` (usefulness selection dominates greedy pairwise admission).
- **P3** `EGGRAPH` = `AU_PAIR` on F1 (no AC structure) and > `AU_PAIR` on F2 (merge
  canonicalization merges orderings anti-unification treats as distinct).
- **P4** Held-out F3: zero macro hits for F1/F2 libraries, bounded waste, no capability
  loss (every arm solves every task or the arm is defective).
- **P5** Revocation cone is exactly the dependent macros; zero collateral; unaffected
  macros keep firing.
- **P6** A critical repeat rate r* exists; below it `NO_LIFETIME_PAYBACK` holds on any
  horizon.
- **P7** `NOGOOD_ONLY` saves on streams with repeated hard misfires, loses nothing on F3
  (misfire keys are surface-exact; failure knowledge never becomes impossibility).

## Mandatory harness validation

The type-level selection mirror must reproduce production `SolveOperatorIndex` counts
(postings_examined, selected operators) on constructed catalogues, or the run returns
`CANNOT_CHECK_SELECTION_MIRROR_DISAGREES_WITH_PRODUCTION_INDEX` and no cost number is
interpretable. Every arm must solve every acquisition task from scratch on first exposure
(a learner that cannot re-solve is a cache, and `CHUNK` is the designated cache).

## Stop rule and terminals

Registered #214 section 7 terminals only, from the issue's honest list.
`PARENT_SUFFICIENT_FOR_<function>` is a SUCCESS terminal. Forbidden anywhere:
neural-superiority or neural-necessity claims, `TRANSFORMER_REPLACED`, `LLM_EQUIVALENT`,
general-capability claims. A failing arm gets one-stage attribution -> matching lever ->
re-test (FNA-1b/1c/1d precedent) before any negative is filed; only a proven structural
obstruction stops that chain. Defect runs are preserved and recorded, never edited.

## Declared limitations, before seeing outcomes

Planted worlds, one author: E1/L1, not E3. The catalogue is small and the families are
shallow relative to program-synthesis benchmarks; the claim scope is the mechanism class
on THIS substrate, not a benchmark result. No maintenance-under-edit term beyond
revocation (the catalogue itself is immutable during a run). Human prior enters only
through the frozen family generators, identically for every arm including `NO_LIBRARY`.
