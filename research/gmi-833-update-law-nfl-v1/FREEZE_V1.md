# GMI #833 update-law no-free-lunch boundary — freeze v1

**Child issue:** #870  
**Parent:** #833 Section I  
**Frozen from main:** `497977a071f33a824628332caf1ccc44e077f924`  
**Claim ceiling:** `GMI_FINITE_UPDATE_LAW_NO_FREE_LUNCH_BOUNDARY_AT_UNIFORM_COMPLETION_SCOPE`

This is the pre-implementation scientific custody record. Executor, tests, result receipt, theorem note, manifest, reconciliation spec and workflow must postdate this freeze.

## Exact target row

This tranche may reconcile only:

`Prove no-free-lunch boundaries: no universal best update law without ecological assumptions.`

No neighboring selector/recovery/held-out/real-system row is earned here.

## Parent theorem ownership

This tranche does not claim novelty for no-free-lunch or inductive-bias mathematics.

- Wolpert & Macready (1997), *No Free Lunch Theorems for Optimization*, IEEE Transactions on Evolutionary Computation 1(1):67–82, DOI `10.1109/4235.585893`: under the theorem's symmetric averaging conditions, improved performance on one problem class is offset elsewhere; useful algorithm preference requires structure/restriction in the problem distribution.
- Mitchell (1980), *The Need for Biases in Learning Generalizations*: nontrivial generalization requires a bias/assumption beyond mere consistency with observed examples.
- Supervised-learning NFL formulations under uniform target-function averaging are treated as parent specializations, not as a statement that all algorithms are equal under real-world, nonuniform, structured task distributions.

The residual #833 contribution is the architecture-neutral update-law/ecology contract, exact finite specialization, and claim-language boundary.

## Registered finite object

Let:

- `X={0,...,n-1}` be a finite context set;
- `Y={0,...,k-1}` with `k>=2` be the finite prediction/action alphabet;
- `O subset X` be observed contexts;
- `U=X\O` be a **nonempty** held-out set;
- `h:O->Y` be the registered observed history;
- `A` be any update law that, after receiving `h`, produces for each `x in U` a normalized probability vector `q_A(.|h,x)` over `Y`.

The law may be deterministic or randomized. Its internal architecture, optimizer, representation and update implementation are not part of the theorem.

A target/ecology completion is a total function `f:X->Y` satisfying `f|O=h`.

## NFL-I1 — uniform-completion equality

Let `F_h` be the `k^|U|` completions consistent with `h`, with the uniform distribution. For every update law `A` and every `x in U`,

`E_{f~Unif(F_h)} q_A(f(x)|h,x) = 1/k`.

Hence expected mean held-out accuracy is exactly `1/k` and expected mean 0–1 error is exactly `1-1/k` for every deterministic or randomized update law.

### Frozen proof

For fixed `x in U`, each label `y in Y` occurs at `x` in exactly `k^(|U|-1)` completions. Therefore

`E q_A(f(x)|h,x)`
`= (1/k) * sum_{y in Y} q_A(y|h,x)`
`= 1/k`

because the law's predictive probabilities normalize. Averaging the same value over `x in U` preserves `1/k`. QED.

Observed labels do not alter the argument: they merely restrict `F_h`; each still-unconstrained held-out coordinate remains uniform under uniform completion.

## NFL-I2 — ecology dependence and preference reversal

The theorem must include a same-space nonuniform control showing that algorithm preference is conditional on ecology.

Frozen binary one-heldout witness:

- update law `A0` predicts label `0` with probability 1;
- update law `A1` predicts label `1` with probability 1;
- ecology `P0(f(x)=0)=3/4`, `P0(f(x)=1)=1/4` makes `A0` accuracy `3/4` and `A1` accuracy `1/4`;
- ecology `P1(f(x)=0)=1/4`, `P1(f(x)=1)=3/4` reverses those scores.

Thus there is no ecology-independent strict ordering even for this pair. This does not prove that every pair of algorithms reverses under some ecology; the claim is only that selecting a unique best law requires ecological/model/resource assumptions beyond the symmetric NFL average.

## NFL-I3 — randomized-law control

Frozen ternary one-heldout law `q=(1/7,2/7,4/7)` must have uniform-completion accuracy exactly

`(1/3)*(1/7+2/7+4/7)=1/3`.

Randomization cannot evade NFL-I1.

## NFL-I4 — exact exhaustive finite certificates

Post-freeze code must exhaustively verify the analytic theorem on small finite universes including at least:

- binary labels with 1, 2, and 3 held-out coordinates;
- ternary labels with 1 and 2 held-out coordinates;
- multiple different observed histories;
- all deterministic held-out prediction vectors for each registered small case;
- several exact-rational randomized laws.

The executable certificate is supporting evidence only. NFL-I1 remains an analytic theorem for arbitrary finite `k>=2` and nonempty finite `U` under its stated uniform-completion premise.

## Fail-closed hostiles

The implementation must reject or distinguish:

1. `U=empty` -> `NOT_APPLICABLE_NO_HELDOUT`, not a vacuous learning-success certificate;
2. `k<2` -> invalid theorem instance;
3. predictive vector not normalized -> reject;
4. negative predictive probability -> reject;
5. target completion inconsistent with observed history -> reject;
6. ecology weights not normalized -> reject;
7. a nonuniform ecology falsely declared `UNIFORM` -> reject by exact equality of weights over the completion support;
8. incomplete completion support declared `UNIFORM` -> reject;
9. float probability/weight evidence -> reject; exact rational only.

## Evidence semantics

Required terminal vocabulary includes:

- `UNIFORM_COMPLETION_NFL_EQUALITY`
- `NONUNIFORM_ECOLOGY_PREFERENCE`
- `NOT_APPLICABLE_NO_HELDOUT`
- `CANNOT_CHECK_INVALID_DISTRIBUTION`

No executor branch may infer `ALL_ALGORITHMS_EQUAL_IN_REAL_WORLD` from a uniform finite certificate.

## Historical branch boundary

The old unmerged branch `gmi/learning-law-selection` is non-authoritative context only. It conditionally maps registered premises/prices to five learning laws and explicitly refuses premise-free selection. This tranche does not import its artifacts as proof authority or merge it wholesale.

## Forbidden promotions

This tranche alone cannot support:

- `ALL_ALGORITHMS_EQUAL_IN_REAL_WORLD`
- `UNIVERSAL_UNIFORM_ECOLOGY`
- `NO_ALGORITHM_CAN_OUTPERFORM_ANOTHER`
- `NO_USEFUL_LEARNING_LAW_SELECTION`
- `ALL_LEARNING_LAWS_COVERED`
- `PROSPECTIVE_SELECTOR_BUILT`
- `P3_RECOVERY_COMPLETE`
- `COMPLETE_GMI`
