# AJ9e — blind recovery of K04 content-dependent routing

The blind task supplies only a context bit `c`, two payload bits `a,b`, and the exact required response `a if c=0 else b`. Search receives generic Boolean NOT/AND/OR only; no selector, routing, attention, softmax, QKV, family label or K04 fingerprint is available.

## Blind result

Size-layered Boolean synthesis first reaches the exact mapping at four operations:

`OR(AND(NOT(c),a), AND(c,b))`.

An independent exact DNF-cover search finds the unique minimum two-cube cover `{c=0,a=1}` and `{c=1,b=1}`. Thus two different representations recover the same context-conditioned two-branch mechanism.

## Post-hoc K04 adjudication

Only after the blind outcome is frozen, the K04 registry entry is read. The recovered mechanism passes the registered fingerprint:

- context-dependent branch/gating quantities are computed for both candidate payloads;
- the causal influence of `a` is present at `c=0` and absent at `c=1`;
- the causal influence of `b` is absent at `c=0` and present at `c=1`;
- payload information from the active branch is aggregated downstream;
- holding payloads fixed while changing context changes which payload dominates.

Terminal: `RECOVERED` at a finite hard-routing scope.

## Boundary

This does not derive Transformer attention, softmax normalization, query/key/value representations, learned attention weights, continuous weighting, or attention optimality. The frozen K04 equivalence scope explicitly permits content-dependent routing/weighting mechanisms not literally implemented as softmax. No pre-search selection prediction was registered, so `PREDICTED_SELECTED` is forbidden.

## Claim ceiling

`AJ9E_K04_BLIND_DYNAMIC_ROUTING_RECOVERY_AT_FROZEN_FINITE_SCOPE`
