# Warrant Blindness: An Oracle Separation from Exact Function Learning

**WLL theorem candidate V1 — exact oracle separation and minimax bounds; priority unresolved**

Date: 2026-09-03  
Scientific umbrella: ORION-V2 #194  
Execution master: ORION-V2 #197  
Focused P0 lane: ORION-V2 #221

## 1. Lifecycle concept class

For every `N>=0`, define concepts `c_z`, one for each `z in {0,1}^N`. Every concept has the identical current function

```text
f_z(x) = x mod 2.
```

Hidden vector `z` describes `N` future warrant challenges: after revoking a registered primary support, challenge `i` requires RETAIN if `z_i=1` and RETRACT if `z_i=0`.

A current-function oracle answers any adaptive query about `f_z`, including exhaustive evaluation. A warrant query asks one challenge bit `z_i`.

## 2. Unlimited current-function oracle blindness

### Theorem WB-1

For every `N`, every adaptive transcript of current-function queries is identical for all `2^N` lifecycle concepts. Exact lifecycle identification is therefore impossible from current-function queries alone, even with unlimited queries, computation and current test coverage.

**Proof.** `f_z=f_z'` for every `z,z'`. Every oracle answer and adaptive query choice is identical, so the transcript has zero information about `z`.

This is stronger than a finite-sample lower bound: exact learning of the current function still leaves arbitrary Warrant Lift.

## 3. Randomized and abstention bounds

Let `Z` be uniform on `{0,1}^N`. After `q` distinct binary warrant queries, `N-q` bits remain independent and uniform conditional on the full transcript.

### Theorem WB-2

The maximum probability of outputting the entire correct lifecycle profile is

```text
2^-(N-q).
```

### Theorem WB-3

If the learner abstains on `a` unqueried coordinates and answers every other coordinate, the minimum expected Hamming error is

```text
(N-q-a)/2.
```

Zero-error partial prediction is possible exactly when

```text
q+a >= N.
```

A closure-certified `N`-bit warrant record is sufficient for zero-query, zero-abstention exact response. It supplies information the current function cannot contain.

## 4. Benchmark impossibility

### Corollary WB-4

No evaluation restricted to current input-output behavior can distinguish any two concepts in the class, even if it exhausts the input domain. Such an evaluation can report perfect accuracy while a system remains wrong on most lifecycle profiles.

A benchmark claiming safe continual reuse must therefore include hidden evidence, scope, authority, policy or verifier changes; current-task accuracy cannot proxy for Warrant Lift.

## 5. Exact finite checks

The checker exhausts `N=0..10`. For every `q<=N`, it verifies the full-profile success formula; for every compatible abstention count it verifies expected Hamming error and the zero-error frontier. It confirms that every current-function transcript within one `N` is identical. A planted false-completion rule that assigns one default warrant profile after perfect current evaluation fails on every non-default lifecycle world.

The registered witness `N=8,q=3,a=2` has

```text
P(exact) = 1/32
E[errors] = 1.5
q+a = 5 < 8, so zero error is impossible.
```

## 6. Strongest-parent subtraction

The proof is an oracle/indistinguishability argument drawing on exact/query learning, sufficient statistics, conditional entropy, version spaces and future-equivalence ideas. Those techniques are parent-owned.

The candidate residual is the target class: learned procedural behavior plus future warrant obligations under evidence/scope/authority/verifier updates. No strengthening of the current-function learner closes the gap because that oracle contains zero information about `z`. Once the comparator receives a warrant interface, the research question becomes the optimal acquisition, compilation, revalidation, recourse, abstention and retention frontier.

This theorem does not establish an architecture separation. A recurrent Transformer with the same warrant oracle can implement the same strategy.

## 7. Novelty relevance

Many apparent OCM gains vanish when the Transformer comparator is recurrent and receives the same tools and memory. WB-1 survives that attack because it is not an expressivity claim: every architecture seeing only the current function is information-theoretically blind to future warrant.

The next theorem must compare alternative warrant interfaces and representations under equal total information, not OCM versus Transformer by name.

## 8. Authority

Supported: exact oracle indistinguishability, randomized success and Hamming bounds, zero-error query/abstention frontier and insufficiency of current-behavior benchmarks for the registered class.

Not supported: literature priority, new architecture status, lower practical cost, natural-language competence, privacy-preserving unlearning, quantum advantage or publication readiness.
