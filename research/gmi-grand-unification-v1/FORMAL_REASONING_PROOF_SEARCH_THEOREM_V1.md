# Grand GMI Formal Reasoning / Proof-Search Theorem V1

Status: **FORMAL REDUCTION + EXACT FINITE SECTOR**  
Date: 2026-09-13  
Base: `main@d48207f10867eee5f9d00f2185565701b15b32ce`

## 0. Purpose

Formal reasoning, theorem proving and program proof search should not be separate primitive kinds of intelligence. In Grand GMI they are process instances with a declared proof system/verifier, an obligation to emit an accepted certificate or action, semantic state induced by future proof continuations, and ordinary information/computation/resource constraints.

The proof system itself is part of the declared process/ecology. Grand GMI does not manufacture soundness or truth from an arbitrary checker.

## 1. Proof-search problem

A finite proof-search problem is

\[
\mathfrak P=(X,\Pi,\mathcal G,V,\Omega,\rho,B),
\]

where:

- `X` is the theorem/problem instance;
- `Pi` is the proof/certificate space;
- `G` is the legal partial-proof transition grammar;
- `V(X,pi)` is the declared verifier;
- `Omega` requires an accepted proof/certificate or a declared theorem-level outcome;
- `rho` charges search, memory, communication and verification resources;
- `B` is any declared budget.

This is an ordinary Grand-GMI process: partial proofs are histories/states, tactic choices are actions, verifier outcomes are observations, and accepted proof production is the obligation.

## 2. GP1 — semantic proof-state quotient

For partial proof histories `h,h'`, define

\[
h\equiv_{proof}h'
\]

when every admitted legal continuation has the same obligation-relevant verifier/acceptance response from `h` and `h'` at the declared tolerance/budget.

Then the quotient

\[
S^*_{proof}=H_{proof}/\!\equiv_{proof}
\]

is the canonical exact proof-search state at that operational scope.

Any representation preserving **every registered continuation response** must
refine this quotient. Merely finding one accepted certificate can require less:
partial histories with acceptable completions `{a,b}` and `{a,c}` have different
full response rows but can both use completion `a`. Task-success necessity is
therefore governed by the compatibility/cut condition in GP3, not by full
response cardinality alone; see `SEMANTIC_ADEQUACY_CORRECTION_V1.md`.
If the proof grammar respects class-consistent legal actions and is
right-congruent with respect to the response equivalence, quotient search
preserves the registered acceptance behavior. Dynamic programming for any
additional objective or resource coordinate also requires that coordinate's
transition/output costs to be preserved; acceptance equivalence alone does
not identify a cost-optimal proof search.

Thus symbolic proof states, learned proof embeddings and search nodes are candidate realizations of the same obligation-relative quotient.

## 3. GP2 — verifier/search separation

A certificate verifier and a certificate finder solve different transformations.

Suppose one valid proof is hidden among `N` candidate certificates and the only proof-specific information available during search is an exact equality verifier:

\[
V(i)=1\iff i=i^*.
\]

Checking a supplied candidate costs one verifier call. Finding the hidden valid certificate in the worst case requires eliminating `N-1` candidates before the last candidate is forced, or equivalently `N` trials if a positive verifier response is required before output.

Therefore low verification complexity does not imply low proof-search complexity.

This is the theorem-proving specialization of the Grand-GMI information/computation separation: the accepted output may have small semantic width while the transformation needed to find it is large.

## 4. GP3 — proof communication is a semantic cut

Whenever one module/agent produces a proof state, lemma, certificate, tactic hint or verifier response consumed by another module, that interface is an ordinary semantic cut.

For a classical deterministic **one-way** interface `c:X -> Z`, `d:Z x Y -> A`,
if downstream behavior must distinguish `m` mutually conflicting proof
situations under its registered local side information, the complete zero-error
message alphabet needs at least `m` symbols, with SC-1's full hypergraph for
general set-valued proof obligations. A reusable channel's per-use alphabet
does not count its whole transmitted message. In interactive proof search,
requests or verifier feedback may change the sender's information; apply the
bound to the actual later one-way cut after re-registering its information and
remaining obligation. The original unconditioned bound is not automatically
a bound on an interactive transcript; see `INTERACTIVE_CUT_SCOPE_CORRECTION_V1.md`.

Hence proof traces, chain-of-thought-like scratch state, retrieved lemmas and tactic messages are not special ontological objects; they are communication/memory realizations whose necessity depends on the proof obligation and cut geometry.

## 5. GP4 — exact verifier-search law is conditional on the verifier interface

The black-box search law is not universal. Extra process information can collapse search:

- a proof grammar may expose constraints before a complete proof is proposed;
- a differentiable/heuristic score may rank candidates;
- lemmas may factor the proof state;
- an oracle may reveal a semantic quotient class;
- structure may permit dynamic programming rather than enumeration.

Therefore the proof-search spectrum is an instance of `tau`, not a universal exponent attached to the word "reasoning".

## 6. GP5 — soundness is an external process premise

Let the true theorem predicate be `T(X,pi)` while the machine only observes declared verifier `V(X,pi)`.

If `V` is unsound, there can exist `pi_bad` with

\[
V(X,\pi_{bad})=1,\qquad T(X,\pi_{bad})=0.
\]

A machine satisfying the obligation "make V accept" may then return `pi_bad` perfectly. Grand GMI cannot infer truth from verifier acceptance unless soundness (or an equivalent protected relationship) is part of the declared process/evidence.

This is a foundational anti-Goodhart boundary for verifier-based reasoning.

## 7. GP6 — completeness is also typed, not assumed

If a true theorem has no admitted proof inside the declared proof system/budget, failure to find a certificate does not imply theorem falsity. The possible terminals must distinguish at least:

- `PROVED`;
- `REFUTED` when a sound refutation system is declared;
- `NO_PROOF_IN_DECLARED_SEARCH_SCOPE`;
- `UNKNOWN_FROM_CURRENT_PROCESS`.

This is the formal-reasoning analogue of Grand GMI abstention under unresolved identifiability/resource bounds.

## 8. GP7 — learned theorem provers are realization families, not new theory

A neural prover, symbolic searcher, proof assistant tactic engine, retrieval-augmented prover, verifier-guided sampler or hybrid system differs in realization and resource profile. They share the same proof obligation when judged against the same protected proof process.

Family choice is therefore made by the existing reachable morphology/resource frontier once representation adequacy, search capability, verifier access and development cost are accounted for.

## 9. Exact finite evidence

`grand_gmi_proof_reasoning_checks_v1.py` checks:

1. unique-proof equality-verifier search for `N=1..8`: exhaustive query orders have worst-case `N-1` negative verifier calls before the remaining proof is forced, while checking a supplied proof needs one call;
2. a finite proof DAG with response-equivalent partial states: dynamic programming on the semantic quotient exactly matches state-level optimal values/actions;
3. all binary proof-response tables in a finite witness family: quotient cardinality equals the number of distinct future acceptance-response rows;
4. an unsound verifier witness accepts a false certificate exactly, demonstrating that verifier satisfaction and theorem truth are distinct predicates;
5. a sound-but-incomplete bounded proof system yields `UNKNOWN/NO_PROOF_IN_SCOPE`, not a false refutation.

## 10. Parent boundary

Proof complexity, automated theorem proving, SAT/SMT, formal verification and interactive proof theory supply mature parent results. Grand GMI's contribution is the architecture-free reduction into the common semantic-state/cut/transformation/morphology framework and the typed boundary between proof obligation, verifier contract and physical realization.

## 11. Claim ceiling

This theorem does not claim:

- a universal efficient theorem prover;
- `P=NP` or any new complexity-class collapse;
- soundness of arbitrary external verifiers;
- decidability of unrestricted mathematics;
- that neural or symbolic proof search is universally preferred.

It closes formal reasoning/theorem proving as a Grand-GMI process sector while preserving the existing undecidability and resource boundaries.
