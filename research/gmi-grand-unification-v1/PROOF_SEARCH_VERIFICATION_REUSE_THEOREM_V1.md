# Grand GMI Proof Search, Verification and Reuse Theorem V1

Status: **THEOREM + EXACT FINITE WITNESSES**  
Date: 2026-09-12

## 0. Theorem proving is not one resource

A formal theorem-proving machine may spend resources on at least three different operations:

1. **certificate verification** — check whether a proposed proof is valid;
2. **proof discovery/search** — find a proof among alternatives;
3. **lemma/subproof retention and reuse** — preserve prior derivations so repeated semantic subgoals need not be recomputed.

Grand GMI already has the objects required to type all three:

- verifier channels are semantic cuts/interventions;
- proof discovery is transformation/epistemic search;
- proof state is an obligation-relative semantic state;
- lemma repositories are persistent/external memory channels;
- proof-system and hardware costs live in `rho`.

No theorem-proving primitive is added here.

---

## 1. Binary verifier search law

Let `P={p_1,...,p_N}` be a finite proof-candidate set. A binary verifier query on `p_i` returns whether it is a valid proof. Assume the verifier reveals no other information.

### Truth decision with zero-or-one valid proof

Suppose the admitted ecology contains both:

- worlds with exactly one valid proof candidate;
- a world with no valid proof among the candidates.

The obligation is to decide whether a proof exists.

**PVR-1 — Binary-Verifier Truth-Decision Theorem.** The minimum deterministic worst-case number of verifier queries is

\[
\boxed{Q_{truth}(N)=N.}
\]

**Proof.** Querying all candidates suffices. For necessity, on the no-proof world every query returns `NO`. Before the final unqueried candidate is checked, that transcript is also compatible with a world where the unqueried candidate is the unique valid proof. Therefore truth cannot yet be decided. QED.

Cheap verification of one candidate does not imply cheap proof discovery or theorem decision.

### Promised theorem truth

If the ecology promises exactly one candidate is valid and the obligation is only to identify which candidate, then `N-1` negative queries suffice: after eliminating `N-1`, the last candidate is identified by the promise.

\[
\boxed{Q_{id}(N)=N-1.}
\]

If the delivered certificate itself must also pass the verifier at output time, charge that final verification separately in the resource ledger.

---

## 2. Verification/search separation

Let one proof verification cost `v` physical resource units. Under the zero-or-one black-box candidate ecology,

\[
\rho_{verify\ one}=v,
\qquad
\rho_{decide\ existence}^{worst}=Nv.
\]

Thus the ratio can grow without bound with candidate-space size even though the proof checker is constant-cost per candidate.

**PVR-2 — Certificate/Search Separation.** Verification complexity alone does not determine theorem-proving capability or discovery cost.

This is a proof-specific specialization of the Grand-GMI information–computation separation theorem.

A richer proof assistant that returns type errors, subgoals, earliest failing tactic or other process feedback defines a different information channel. PVR-1 does not apply unchanged to that richer interface.

---

## 3. Semantic proof-state quotient

Let proof-search histories `h,h'` be equivalent when every legal future tactic/continuation induces the same protected proof-obligation response profile:

\[
h\equiv_{proof}h'
\iff
Q_h^{proof}=Q_{h'}^{proof}.
\]

This is exactly the master semantic-state construction specialized to proof search.

**PVR-3 — Proof-State Quotient Theorem.** Any exact proof search may memoize/cache one representative per exact proof-semantic state without changing protected future solvability behavior. Conversely, merging proof histories that are response-distinct is not licensed by semantics alone and can change completeness or cost.

When the quotient is transition-congruent for the legal tactic process, search/dynamic programming can operate on the quotient rather than the raw proof-history tree.

The theorem does not claim that computing the quotient is always easy.

---

## 4. Lemma reuse resource phase

Consider one exact semantic lemma/subgoal class that appears `r>=1` times in a proof workload.

Let

- `C >= 0`: resource cost to derive the lemma/subproof from scratch;
- `S >= 0`: one-time resource cost to store/index/cache the reusable result;
- `U >= 0`: resource cost to retrieve/adapt/verify one subsequent reuse.

Without caching:

\[
C_{fresh}=rC.
\]

With caching after the first derivation:

\[
C_{reuse}=C+S+(r-1)U.
\]

Therefore:

**PVR-4 — Lemma Reuse Phase Theorem.** Caching/reuse is strictly resource-beneficial iff

\[
\boxed{S<(r-1)(C-U).}
\]

If `U>=C`, nonnegative storage cost cannot make caching strictly better. If `U<C`, the strict break-even reuse count is

\[
\boxed{r>1+\frac{S}{C-U}.}
\]

At equality the two morphologies coexist on the resource frontier.

This is not a claim that semantic lemmas are always discoverable or retrievable at the assumed `U`; those are separate transformation/indexing obligations.

---

## 5. Multiple semantic lemma classes

Suppose repeated proof occurrences partition into exact semantic lemma classes `j=1..m`, with reuse multiplicities `r_j` and costs `(C_j,S_j,U_j)`.

Because exact memoization is per semantic class, the independent scalar cost difference is additive:

\[
C_{fresh}-C_{reuse}
=
\sum_j\left[(r_j-1)(C_j-U_j)-S_j\right]
\]

under the declared additive resource coordinate.

If resource coordinates are vector-valued rather than scalar-priced, compare the fresh and reuse profiles by the Grand-GMI Pareto order; do not hide tradeoffs in an undeclared scalar.

**PVR-5 — Proof-DAG Morphology Law.** Tree-like re-derivation and DAG/repository-like proof reuse are resource-conditioned realizations of the same proof semantics. Repeated semantic subgoals create the opportunity for DAG compression; whether caching is frontier-optimal depends on derivation, storage, retrieval, verification and invalidation costs.

---

## 6. Feedback richness is a channel law

A binary verifier gives at most a pass/fail partition of a candidate proof attempt. A process verifier may instead expose structured information such as:

- first failing tactic;
- current proof state/subgoals;
- type mismatch details;
- locally verified proof prefixes.

A richer signal that can simulate the binary verifier but not vice versa refines the proof-search observation channel. By the semantic-cut/data-processing theory, it cannot make the attainable search policy set worse before its added physical costs are charged.

**PVR-6 — Proof Feedback Typing.** Improvements from compiler/verifier feedback are consequences of a richer declared proof-search information channel, not evidence that verification and discovery are the same operation.

This formal typing matches modern verifier-guided theorem-proving systems that feed structured Lean/compiler signals back into search.

---

## 7. Exact finite microscope

`grand_gmi_proof_search_checks_v1.py` checks two independent laws.

### Black-box verifier

For candidate counts `N=1..16`:

- minimax zero-or-one truth decision equals `N` in **16/16** cases;
- promised-exactly-one proof identification equals `N-1` in **16/16** cases.

### Lemma reuse phase

Exact integer grid:

- derivation cost `C=1..8`;
- reuse cost `U=0..8`;
- storage cost `S=0..8`;
- multiplicity `r=1..12`;
- total **7,776** cells.

Direct cost comparison agrees with the analytic inequality `S < (r-1)(C-U)` in **7,776/7,776** cells.

Disposition:

- **3,050** cache-beneficial cells;
- **284** exact ties;
- **4,442** cache-worse cells.

The grid deliberately includes `U>=C` cases where reuse is never strictly beneficial with nonnegative `S`, preventing an automatic “memory always helps” conclusion.

Aggregate terminal:

`GRAND_GMI_PROOF_SEARCH_REUSE_TRANCHE_ALL_GREEN`.

---

## 8. Parent subtraction

Automated theorem proving, proof search, proof assistants, proof certificates, lemma reuse, proof DAGs and memoization are established parent fields. Proof reuse and memoization-based theorem proving have long precedents; modern Lean-based provers explicitly combine planners/search with formal verifiers and increasingly exploit structured verifier feedback.

Grand GMI does not claim those systems or algorithms as inventions.

The residual contribution is the unified resource typing:

\[
\boxed{
\text{proof obligation}
\to
\text{proof semantic state}
\to
\text{verifier information channel}
\to
\text{search transformation cost}
\to
\text{lemma reuse/storage phase}
\to
\text{proof-system morphology frontier}.
}
\]

This makes the verify/search/reuse separation a direct application of the same laws used for planning, retrieval, continual memory and language.

---

## 9. Scope and falsifiers

PVR-1 assumes a finite candidate set, binary equality-style verifier information, deterministic worst-case queries and the zero-or-one proof ecology. Rich feedback, multiple valid proofs, stochastic proposal policies or open-ended proof languages define different search problems.

PVR-4 assumes exact semantic lemma reuse and the declared scalar cost components. Adaptation, invalidation and retrieval failures must be charged when present.

Direct falsifiers:

1. a zero-or-one binary-verifier truth decision using fewer than `N` worst-case candidate queries;
2. a promised-one identification problem requiring a number different from `N-1` under the stated channel;
3. a reuse cell whose direct cost ordering disagrees with `S < (r-1)(C-U)`;
4. semantics-preserving proof memoization that changes protected future proof behavior;
5. a mismatch in the frozen exact receipt.