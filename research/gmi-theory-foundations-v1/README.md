# GMI theory foundations v1

Parent programme: #833  
Atomic tranche: #834

## Scientific constitution for this tranche

**Flagship question.** What is the weakest architecture-neutral mathematical language
in which #833 can state behavioral equivalence, minimal exact state, residual priors,
and recursive proof gaps without presupposing a named implementation family?

**Weakest defensible claim.** For deterministic total transition/output systems, future
behavior induces a canonical exact quotient that is minimal among exact deterministic
abstractions; and any unique selector facing an evidence symmetry with no fixed
hypothesis needs a symmetry breaker.

**Strongest eventual target (not established here).** A reproducible cross-domain theory
of machine capability and architecture selection whose assumptions, priors, resource
trade-offs, uncertainty, causal claims, and open gaps remain explicit under recursive
hostile review.

**Forbidden claims at this evidence level.** This package does not establish universal
intelligence, literal prior-free induction, universal grammar completeness, causal
identification, stochastic predictive minimality, open-endedness, G6/G7, empirical
cross-domain superiority, or closure of #833.

**Meaning of obligation.** An obligation is a tuple
`(claim, premises, inference_rule, evidence_required, falsifier, dependencies, status)`.
It is not satisfied by naming an object. A theorem obligation requires a derivation; an
empirical obligation requires a predeclared measurement/decision protocol; a
computation obligation requires replayable code and custody sufficient to reconstruct
the result.

**Behavioral specification.** In this tranche it is the extensional mapping from every
finite admissible action trace to the emitted finite output trace. Legacy "obligation"
objects are therefore evidence/governance records *about* claims, not behavioral
specifications themselves. A complete corpus-wide legacy mapping remains open in #833.

**Architecture-prior-free.** This means no named architecture family is selected by the
admissibility language and architecture relabeling alone cannot change validity, while
all remaining non-evidential restrictions are disclosed in `PRIOR_LEDGER.json`.
It does not mean assumption-free or prior-free; `FORMALIZATION.md` proves the relevant
symmetry obstruction.

## Evidence and maturity scales

Evidence is typed:

| level | meaning |
|---|---|
| E0 | proposal, analogy, or verbal rationale only |
| E1 | exact definitions and scope, no theorem/measurement closure |
| E2 | analytic derivation with explicit premises and falsifier |
| E3 | executable reconstruction plus hostile controls for the declared finite/checkable surface |
| E4 | independent implementation or replication reproduces the claim |
| E5 | preregistered or equivalently frozen real-scale empirical/causal evidence |

Maturity is cumulative:

| maturity | gate |
|---|---|
| M0 | question exists |
| M1 | constitution, scope, and priors frozen |
| M2 | analytic obligations closed in declared scope |
| M3 | executable hostile checks close the locally checkable surface |
| M4 | independent replication closes implementation dependence |
| M5 | real-scale external/causal evidence closes the empirical target |
| M6 | all critical descendants in the programme gap graph meet their required closure level |

`closure != ontological completeness`: a result can be closed at E2/M2 or E3/M3 in a
narrow formal scope while stronger descendants remain open.

## Prior taxonomy

Every restriction must have both a **category** and a **tier**.

Categories:

- `ARCHITECTURE`: preselects an implementation family/topology.
- `REPRESENTATION`: fixes encoding, alphabet, state carrier properties, precision, or
  observability.
- `OPERATOR`: fixes update/composition primitives or a synthesis grammar.
- `SEARCH`: fixes enumeration, optimizer, initialization, ordering, stopping, or
  tie-breaking.
- `ECOLOGICAL`: fixes environment/task/data-generation/resource regime.
- `EVALUATION`: fixes metric, scalarization, equivalence tolerance, benchmark, or
  decision threshold.

Operational tiers:

- `P0`: behavioral/physical problem data only; no preference among behaviorally
  equivalent implementations.
- `P1`: representation/measurement restrictions.
- `P2`: architecture or operator-family restrictions.
- `P3`: search/optimization/resource-ordering restrictions.
- `P4`: ecological or evaluation restrictions that determine what is rewarded,
  observed, or declared successful.

A run may have several categories/tiers. Calling a run `architecture-prior-free` only
asserts absence of an undeclared `ARCHITECTURE` restriction; it does not erase P1/P3/P4.

## Strongest-parent subtraction

This tranche imports rather than reclaims:

- #797: fail-closed theorem typing/counterexample governance for the canonical #602
  theorem corpus.
- #765: dependence-aware uncertainty composition.
- #805: finite lifecycle resource accounting and positive-weight Pareto result.

Those results are parents/evidence dependencies. This package does not count them as new
theorems. Its new claims are S1/S1.1 and B1–B3 plus the deterministic/nondeterministic
boundary counterexample N1.

## Files

- `FORMALIZATION.md` — analytic definitions, proofs, and counterexample.
- `PRIOR_LEDGER.json` — residual-prior disclosure for this tranche.
- `GMI_GAP_GRAPH.json` — recursive machine-readable gaps and closure states.
- `RESULTS.json` — claim metadata and evidence ceiling.
- `GMI_TERMINOLOGY_CROSSWALK.md` — terminology and legacy-boundary map.
- `validate_foundations.py` — schema/gap-closure validator plus finite theorem
  reconstruction.
- `test_foundations.py` — hostile tests, including intentionally invalid mutated
  ledgers/graphs.

## Reproduction

From repository root:

```bash
python research/gmi-theory-foundations-v1/validate_foundations.py
python research/gmi-theory-foundations-v1/test_foundations.py
```

The code uses the Python standard library only. The CI workflow runs both commands and
fails on working-tree mutation.

## Closure rule

`GMI_GAP_GRAPH.json` is fail-closed: any node marked with a closure state
(`LOCALLY_CLOSED`, `HOSTILE_CLOSED`, `REPLICATED_CLOSED`, or `REAL_SCALE_CLOSED`) is
invalid if it has a descendant with severity `CRITICAL` and status `OPEN`. A cycle,
dangling parent/dependency, missing falsifier/evidence field, or unknown closure state
also invalidates the graph.

#833 stays `OPEN`. This tranche must not be used to infer otherwise.
