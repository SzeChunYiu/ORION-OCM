# Section D V6 — finite decision-sufficient complete-coordinate freeze

Date frozen: 2026-09-14.
Owner: #602 Section D. Child tracker: #693.
Base: `2c4b494ad19890afe7cb3c35a221fda6df80e019`.

This is the **pre-outcome authority** for V6. It is committed before the V6 witness, result receipt, tests, or scored atlas output exists.

## 0. Scope and meaning of complete

V6 does not seek a universal ontology. It freezes a finite atlas `W`, a fixed candidate grammar `M`, and an exact Pareto decision map `P(w)`.

A coordinate map `C` is complete/decision-sufficient on the frozen atlas iff

```text
C(w)=C(w') => P(w)=P(w')
```

for every registered pair.

The five frozen coordinate groups are

```text
C_D6 = (S,E,R,V,H)
```

with the exact fields registered in issue #693. No world ID, source path, token spelling, architecture/family name, or candidate label may occur in predictor-visible coordinates.

The exact decision quotient is `w ~P w' iff P(w)=P(w')`. Any sufficient coordinate partition must refine this decision partition. V6 tests an interpretable sufficient refinement and group-wise necessity, not field-wise minimality.

## 1. Candidate grammar and Boolean cost law

Five-bit Boolean candidates reuse the already registered mechanism semantics:

```text
full_map
xor_fold
default_exceptions
count_step
count_step_plus_exceptions
```

All are exhaustively checked for exactness before admission.

For candidate description size `d`, serve cost `c`, verifier cost `v`, horizon `Q`:

```text
lifecycle_ops = d + v + Q*c.
```

Hard persistent-memory cap is applied before Pareto comparison.

Extensional verifier cost is 32 for every admitted Boolean candidate.

The proof-aware verifier is frozen only for a generic affine certificate represented by bias + support. It charges 4 verification operations for an exact affine certificate in world A. Candidates without a registered proof object retain extensional cost 32. The verifier does not relax correctness: every admitted candidate must still be exact on all 32 inputs.

## 2. Boolean obligations

World A:

```text
y = x0 XOR x2 XOR x4
```

Frozen exact candidate data:

```text
xor_fold:          persistent 4, description 4, serve 3
exceptions:        persistent 17, description 17, serve 2
full_map:          persistent 32, description 32, serve 1
```

World B:

```text
y = 1 iff x=10101
```

At cap 8 and Q=16, frozen prediction is unique `default_exceptions`.

## 3. Registered Boolean atlas cells

### S collision

Same E/R/V/H:

```text
A, Q=16, cap=8, extensional, cold -> {xor_fold}
B, Q=16, cap=8, extensional, cold -> {default_exceptions}
```

Dropping S must collide these cells while their frontiers differ.

### E collision

Same S/R/V/H:

```text
A, Q=1,  cap=64, extensional, cold -> {xor_fold}
A, Q=16, cap=64, extensional, cold -> {xor_fold, default_exceptions, full_map}
```

Dropping E must collide them.

### R collision

Same S/E/V/H:

```text
A, Q=16, cap=8,  extensional, cold -> {xor_fold}
A, Q=16, cap=64, extensional, cold -> {xor_fold, default_exceptions, full_map}
```

Dropping R must collide them.

### V collision

Same S/E/R/H:

```text
A, Q=16, cap=64, extensional -> {xor_fold, default_exceptions, full_map}
A, Q=16, cap=64, proof-aware -> {xor_fold}
```

Frozen proof-aware vector for xor is `(persistent=4, lifecycle_ops=56)`:

```text
4 description + 4 proof verification + 16*3 serve = 56.
```

The unchanged alternatives are exceptions `(17,81)` and full map `(32,80)`, so xor must dominate them both.

## 4. History atlas cells

Exact four-pair bidirectional relation, query block 3 forward + 5 reverse, one future block, hard cap 4, exact verifier.

Exact candidates:

```text
key_index:   persistent 4, serve block 23
value_index: persistent 4, serve block 17
```

Changing orientation costs exactly 8 future operations; past construction is sunk.

Frozen cells:

```text
H_key   -> {key_index}   because stay=23 < migrate=8+17=25
H_value -> {value_index} because stay=17 < migrate=8+23=31
```

Common verification cost cancels and may be recorded explicitly without changing the frontier.

Dropping H must collide these cells while their frontiers differ.

## 5. Frozen coordinate fields

### S

```text
obligation_kind
canonical_semantics_digest
algebraic_degree_or_null
algebraic_support_or_null
minority_count_or_null
best_count_step_residual_or_null
relation_cardinality_or_null
bidirectional_or_null
```

The semantics digest is computed from canonical typed semantics after remint normalization, never from specimen labels.

### E

```text
query_horizon_or_blocks
forward_query_count
reverse_query_count
input_or_relation_scale
recurrence_count
query_distribution_numeric_parameters
```

### R

```text
hard_persistent_cap
persistent_accounting_rule
lifecycle_operation_rule
common_workspace_allowance
```

### V

```text
acceptance_semantics
verifier_mode
false_adoption_tolerance
certificate_verification_rule
```

### H

```text
inherited_semantic_state
past_build_cost_sunk
future_conversion_rule
invalidation_reset_state
```

String-valued rule fields are fixed protocol identifiers describing generic accounting semantics; they may not contain candidate/family names.

## 6. Remint twins

Every base atlas cell receives a disjoint remint twin:

- Boolean inputs are permuted by the frozen bit-coordinate permutation `(2,4,1,0,3)` and the semantics is transported accordingly.
- Relation keys and values are independently renamed by opaque permutations.

Prediction: source and remint twin have identical `C_D6` coordinates and identical frontier.

The canonical semantics digest must therefore be remint invariant.

## 7. Sufficiency and group-wise necessity predictions

Frozen predictions:

1. Full `(S,E,R,V,H)` fibers are frontier-constant over the complete source+remint atlas.
2. Dropping S produces at least the A/B collision above.
3. Dropping E produces at least the Q=1/Q=16 collision above.
4. Dropping R produces at least the cap=8/cap=64 collision above.
5. Dropping V produces at least the extensional/proof-aware collision above.
6. Dropping H produces at least the inherited-key/inherited-value collision above.
7. For every drop-one schema, the witness must exhibit an actual pair with equal reduced coordinates and unequal exact frontiers; merely counting fields is insufficient.
8. If any drop-one collision fails, that group's necessity claim fails.

## 8. Quotient theorem

The proof document must show:

Let `C` be sufficient. If `C(w)=C(w')`, sufficiency gives `P(w)=P(w')`; therefore every fiber of `C` is contained in a decision-equivalence class. Hence the partition induced by `C` refines `W/~P`, and `P` factors through `C`.

The decision quotient itself is the coarsest extensional sufficient partition, but is not an explanatory causal coordinate system. V6's grouped schema is tested as an interpretable sufficient refinement.

## 9. Parent boundary

Parents own:

- quotient sets and partition refinement;
- decision/statistical sufficiency;
- abstraction/bisimulation-style state aggregation;
- the individual mechanism/resource/verifier/history phase laws inherited from the prior exact tranches.

Claim ceiling if and only if every frozen condition passes:

```text
FINITE_ATLAS_DECISION_SUFFICIENT_COMPLETE_COORDINATE_SCHEMA_D6
GROUPWISE_NECESSARY_S_E_R_V_H_ON_REGISTERED_ATLAS
PARENT_OWNED_QUOTIENT_SUFFICIENCY_AND_PHASE_MECHANISMS
NO_UNIVERSAL_COMPLETE_COORDINATE_ONTOLOGY_OR_FIELD_MINIMALITY_CLAIM
```
