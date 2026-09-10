# MATH-1 / N4 remaining gates at miniature Hilbert scope

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) MATH-1, owner [#46](https://github.com/SzeChunYiu/ORION-OCM/issues/46).

**This is a bounded MATH-1 microscope, not N4 completion of Metamath, and not
FLT.** Reconstruction of known proofs is still not causal reuse
([disposition](../math-n4-disposition-v1/CORE.md)). The ordinary-goal
[LIBRARY-ARTIFACT](../ordinary-goal-cohort-result-v1/records/qualification-01/LIBRARY-ARTIFACT.json)
is a custody pointer to an off-host prefix; there is no Metamath runtime here.

The consumer is **goal-only MP / intermediate-consuming composition**, not a
one-step successor screen. One-step matching of the held-out suffix against the
acquired PREFIX and SWAP schemas invokes **0** lemmas — the same failure mode as
the Metamath one-step screens (#180). Two independently acquired lemmas compose
on an unseen goal by introducing an intermediate (PREFIX instance) and detaching
with SWAP.

## Domain

Positive implicational Hilbert calculus: axiom schemas K and S, rule MP.
Combinatory SK terms are Hilbert proofs. The kernel checks every selected proof.

| Object | Identity |
|---|---|
| PREFIX / B | `(B → C) → ((A → B) → (A → C))`, witness `S(KS)K` from size-4 search |
| SWAP / C | `(A → (B → C)) → (B → (A → C))`, witness from a frozen SK catalog `{I,B,C}` after size-4 miss |
| Held-out SUFFIX / B' | `(A → B) → ((B → C) → (A → C))` on atoms `{p,q,r}` never used in acquisition |

SWAP catalog admission is **declared prior information**. Size-4 exhaustive
search does not inhabit SWAP; C is the unique catalog hit. Both witnesses are
kernel-checked on training instances and on a further hold-out substitution.

## What is measured

- Lemma invocation in the selected proof of a **fresh** theorem
- Ablation of either lemma: proof lost, MP cost increases
- OS-process restart from a persisted library
- Exact support revocation: withdrawing training-support IDs restores primitive
  (no-lemma) search; restoration returns lemma use
- Composition of two independently acquired lemmas on an unseen goal
- Failed applications retained as **alpha-normalized type shapes**, not task-id
  blacklists; a renamed compatible dead end is skipped; identity remains provable
- Subgoal / intermediate formulas introduced by lemma instantiation
- Representation change: operators `{K,S,MP}` grow by admitted PREFIX and SWAP
- Retrieval parent: bag-of-symbols Jaccard after alpha-normalization
- Neural / Transformer parents: `CANNOT_CHECK_NO_NEURAL_PROVER_IN_THIS_ENVIRONMENT`
- Full search / check / storage / acquisition cost vectors on this microscope

## Terminal

Positive, if and only if every registered causal criterion holds **at this
scope**:

```text
CAUSAL_PROOF_METHOD_REUSE_SUPPORTED_AT_MINIATURE_SCOPE
```

This is **not** `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`. MATH-1 / N4 on Metamath
stays **OPEN**. MATH-2 / N5 and MATH-3 / N6 stay LOCKED. FLT PRs 129–132 are not
touched. PR #203 is not overwritten.

[Result](RESULT.json) · [kernel](kernel.py) · [experiment](experiment.py)
