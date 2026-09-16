# AJ9d — blind recovery of K03 local/shared-transform structure

The search is deliberately broader than the recovered family. Each of three output sites may be an arbitrary Boolean function of all three global input bits. Generation/search/evaluation receives no locality, sharing, convolution, equivariance, or K03 fingerprint.

## Frozen outcome

Full global truth-table enumeration uniquely fixes each output semantic function. A second solver enumerates dependency subsets by cardinality and then Boolean tables on those subsets. It independently finds that every output requires exactly two inputs, with dependency sets `{0,1}`, `{1,2}`, and `{0,2}`. All three minimum tables are the same semantic rule `(0,1,1,0)` after coordinate alignment.

Thus the exact global response itself removes one remote dependency per output and yields reuse of one two-input transform at all three sites.

## Post-hoc K03 adjudication

Only after the blind outcome is frozen, the K03 fingerprint is read. The candidate passes:

- one common transform is applied at all three positions;
- each application depends only on the registered cyclic local pair `(i,i+1 mod 3)`;
- remote non-neighbor perturbation has no one-step effect;
- the same local two-bit pattern induces the same response at every site;
- cyclic site relabeling transports the output computation consistently.

The full-global enumeration and minimum-dependency synthesis agree on every dependency set. Terminal: `RECOVERED`.

## Claim boundary

This is a finite structural recovery of the registered shared-local mechanism fingerprint. It is not a derivation of convolution as a named operation, CNN training, arbitrary translation groups, infinite grids, or optimality of local/shared mechanisms. No pre-search selection prediction was frozen, so `PREDICTED_SELECTED` is forbidden.

## Claim ceiling

`AJ9D_K03_BLIND_LOCAL_SHARED_TRANSFORM_RECOVERY_AT_FROZEN_FINITE_SCOPE`
