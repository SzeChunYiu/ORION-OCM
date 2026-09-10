# MATH-1 remaining family boxes at miniature Hilbert/SK scope

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) MATH-1, owner [#46](https://github.com/SzeChunYiu/ORION-OCM/issues/46).

**Successor** to [`research/math-n4-lemma-reuse-v1/`](../math-n4-lemma-reuse-v1/CORE.md)
and [`research/math-n4-subgoal-v2/`](../math-n4-subgoal-v2/CORE.md). Frozen v1
`RESULT.json` sha256 `cbcae02402fb7f73ec2f5cde25b4f922a141a8266f4ff603fc2d23c71aeb77cc` and frozen
v2 `RESULT.json` sha256 `ae10620c091b1baa9320f34c2a613ba81ef6a7bff9debcd13645ce5122d06144` are
custody-checked and must stay unchanged. FLT PRs 129–132 are not touched.
Production `src/` is not edited. MATH-2 / N5 and MATH-3 / N6 stay **LOCKED**.

**This is a bounded MATH-1 microscope, not N4 completion of Metamath, not N5
exact problem solving, and not FLT.** There is no Metamath runtime here. Family
names below are invented CUT_* identities over Hilbert/SK types.

## Four tiny family worlds

| World | Box | Schema | Acquired lemma | Hold-out |
|---|---|---|---|---|
| successor-arithmetic | arithmetic families | `((B → C) → ((A → B) → (A → C)))` | `CUT_6bb18bedec08` witness `((S (K S)) K)` | held-out PREFIX substitution |
| ring-distrib | algebra families | `((A → (B → C)) → (A → ((D → B) → (D → C))))` | none of its own; served by arithmetic lemma | compose-second on disjoint atoms |
| contraction counting | combinatorics families | `((A → (A → B)) → (A → B))` | `CUT_d583cff6ae97` witness `((S S) (S K))` | held-out contraction |
| even/odd mod-2 | number theory families | `(v0 → v0)` / `((v0 → (v1 → v2)) → (v1 → (v0 → v2)))` | `CUT_4b0a3912d98a` / `CUT_421364dcd906` | even→odd transfer **fails** |

The number-theory world is an even/odd (mod-2) identity, the maximum honest
scale here. It is **not** analytic number theory and **not** FLT.

## What is measured

- Method acquired on family A transfers to held-out A' (arithmetic, combinatorics)
- Arithmetic PREFIX transfers to algebra compose-second; v1 catalog {I,B,C} and
  SK size-4 miss that goal
- Arithmetic method does **not** transfer to combinatorics; even does **not**
  transfer to odd
- Exact symbolic checker (Hilbert kernel / formula identity). Numeric floats
  are rejected
- Windowed resource accounting: proof steps, MP attempts, kernel applications
- Specialized parents on the **same** tasks: Knuth-Bendix-ish v1 SK catalog,
  Hilbert tautology table, primitive SK size 4
- Reference models: those parents. Neural/Transformer: `CANNOT_CHECK_NO_NN_LIBRARY`
- Conjecture testing: PREFIX solves distrib (confirmed); SBI uniquely inhabits
  the iterator type (refuted — I also inhabits it; I ⊭_w SBI)
- Discriminating experiment selection: one-step/library screen vs SK size 4

## Parent dispositions (serving, not MATH-2)

- `arithmetic_successor`: `PARENT_SUFFICIENT_FOR_SERVING`
- `algebra_distrib`: `OCM_LEMMA_SERVES_PARENTS_MISS`
- `combinatorics_counting`: `PARENT_SUFFICIENT_FOR_SERVING`
- `number_theory_even`: `PARENT_SUFFICIENT_FOR_SERVING`
- `number_theory_odd`: `PARENT_SUFFICIENT_FOR_SERVING`

`PARENT_SUFFICIENT_FOR_SERVING` on a family means the specialized parent proves
that hold-out without the acquired lemma. It does not erase the transfer residual
on algebra, and it does not close MATH-2.

## Terminal

Positive, if and only if every registered criterion holds **at this scope**:

```text
MINIATURE_FAMILY_METHOD_TRANSFER_SUPPORTED_AT_HILBERT_SCOPE
```

This is **not** `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`. MATH-1 / N4 on Metamath
stays **OPEN**. MATH-2 / N5 stays **LOCKED**.

## Issue #165 family boxes this honestly supports

Supported **only** on this miniature Hilbert/SK microscope (not Metamath, not
FLT, not N5): `arithmetic_families`, `algebra_families`, `number_theory_families`, `combinatorics_families`, `exact_symbolic_answer_checking`, `method_acquisition`, `method_transfer`, `conjecture_testing`, `discriminating_experiment_selection`, `resource_accounting`, `strongest_specialized_parents`, `reference_model_on_same_tasks`.

Not supported here: `math2_n5_close`, `metamath_n4_close`, `flt`, `neural_guided_prover`, `transformer_proof_reference_same_checker`, `full_lifetime_resource_accounting`.

## What remains CANNOT_CHECK

- `neural_guided_prover`: CANNOT_CHECK_NO_NN_LIBRARY
- `transformer_proof_reference_same_checker`: CANNOT_CHECK_NO_NN_LIBRARY
- `metamath_n4`: CANNOT_CHECK_NO_METAMATH_RUNTIME; LIBRARY-ARTIFACT is an off-host custody pointer.
- `full_search_check_storage_acquisition_cost`: CANNOT_CHECK_LIFETIME_ECONOMICS; only windowed microscope cost vectors are recorded.
- `flt_prs_129_132`: CANNOT_CHECK_FLT_BLOCKED; this capsule does not expand FLT.
- `math2_n5`: CANNOT_CHECK_MATH2_LOCKED; miniature Hilbert/SK family worlds are not N5 exact problem solving.

[Result](RESULT.json) · [kernel](kernel.py) · [experiment](experiment.py)
