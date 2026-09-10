# MATH-1 / N4 subgoal discovery and lemma introduction at miniature Hilbert scope

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) MATH-1, owner [#46](https://github.com/SzeChunYiu/ORION-OCM/issues/46).

**Successor** to [`research/math-n4-lemma-reuse-v1/`](../math-n4-lemma-reuse-v1/CORE.md)
(terminal `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED_AT_MINIATURE_SCOPE`). This capsule changes
**mechanism**, not v1 salts. Frozen v1 `RESULT.json` sha256
`cbcae02402fb7f73ec2f5cde25b4f922a141a8266f4ff603fc2d23c71aeb77cc` is custody-checked and must stay
unchanged. FLT PRs 129–132 are not touched. Production `src/` is not edited.

**This is a bounded MATH-1 microscope, not N4 completion of Metamath, and not
FLT.** There is no Metamath runtime here. The LIBRARY-ARTIFACT is an off-host
custody pointer.

## Mechanism change versus v1

v1 independently acquired frozen names `PREFIX` and `SWAP`, then composed them
on a held-out suffix. One-step hits were 0; revoke/ablation worked; neural was
`CANNOT_CHECK`.

v2 does **not** mint or consume `PREFIX`/`SWAP`. A registered kernel:

1. Enumerates primitive SK identities that are not K/S axiom schemas and not
   the goal.
2. Names a new lemma `CUT_*` from a proved identity (alpha-normalized schema).
3. Finishes the training goal by using that named lemma as an intermediate.
4. Reuses the same named lemma on a fresh theorem with held-out atoms.
5. Withdraws exact training-support IDs and restores primitive search.

## Domain

Positive implicational Hilbert calculus: axiom schemas K and S, rule MP.
Combinatory SK terms are Hilbert proofs. The v1 kernel checks every selected
proof. New population salt `orion-ocm-math-n4-subgoal-v2`.

| Object | Identity |
|---|---|
| Invented lemma | `CUT_6bb18bedec08` |
| Invented schema | `((v0 → v1) → ((v2 → v0) → (v2 → v1)))` |
| Witness | `((S (K S)) K)` (kernel-checked) |
| Discovery / reuse goal | `(A → (B → C)) → (A → ((D → B) → (D → C)))` (principal type of B B) |
| Frozen names refused | `PREFIX`, `SWAP` |
| Fresh atoms | `e, f, g, h` |

The invented schema is PREFIX-shaped, but the **lemma identity is not the
frozen name PREFIX**. That is the point of this successor.

## What is measured

- Subgoal discovery: intermediate lemma identity ≠ goal and ≠ frozen training
  lemma name, then the goal is finished
- Representation/lemma introduction: operators `{K,S,MP}` grow by `CUT_6bb18bedec08`
- Fresh-theorem reuse of the introduced lemma
- Exact support revocation and restoration
- OS-process restart from a persisted library
- Retrieval parent: bag-of-symbols Jaccard after alpha-normalization
- Neural / Transformer parents: `CANNOT_CHECK_NO_NN_LIBRARY`
- Windowed search / check / storage / acquisition costs on this microscope

## Terminal

Positive, if and only if every registered causal criterion holds **at this
scope**:

```text
CAUSAL_SUBGOAL_LEMMA_INTRODUCTION_SUPPORTED_AT_MINIATURE_SCOPE
```

This is **not** `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`. MATH-1 / N4 on Metamath
stays **OPEN**. MATH-2 / N5 and MATH-3 / N6 stay LOCKED.

## Issue #165 MATH-1 boxes this honestly supports

Supported **only** on this miniature Hilbert/SK microscope (not Metamath, not
FLT): `subgoal_discovery`, `representation_lemma_introduction`, `exact_support_revocation`, `lemma_reuse`, `unseen_composition`, `fresh_theorem_family_reuse`, `method_ablation`, `restart`, `retrieval_prover`, `symbolic_tactic_search_parent`.

Not supported here: `neural_guided_prover`, `transformer_proof_reference_same_checker`, `full_search_check_storage_acquisition_cost`, `metamath_n4_close`.

## What remains CANNOT_CHECK

- `neural_guided_prover`: CANNOT_CHECK_NO_NN_LIBRARY
- `transformer_proof_reference_same_checker`: CANNOT_CHECK_NO_NN_LIBRARY
- `metamath_n4`: CANNOT_CHECK_NO_METAMATH_RUNTIME; LIBRARY-ARTIFACT is an off-host custody pointer. Unscoped CAUSAL_PROOF_METHOD_REUSE_SUPPORTED is not licensed.
- `full_search_check_storage_acquisition_cost`: CANNOT_CHECK_LIFETIME_ECONOMICS; only windowed microscope cost vectors are recorded.
- `flt_prs_129_132`: CANNOT_CHECK_FLT_BLOCKED; this capsule does not expand FLT.

[Result](RESULT.json) · [kernel](kernel.py) · [experiment](experiment.py)
