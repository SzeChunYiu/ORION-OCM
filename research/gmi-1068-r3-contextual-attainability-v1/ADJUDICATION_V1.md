# R3 post-freeze adjudication

The R3 freeze is unchanged. This successor artifact records defects found after the frozen targets were implemented and the repairs required before merge.

## A1 — optimized checker fail-open

The first implementation used Python `assert` for every load-bearing check while CI deliberately executed a `python -O` route. Optimization removes assertions, so that route could print GREEN without validating the fixture or receipt.

**Disposition:** repaired before merge. All load-bearing checks now use explicit exceptions; normal and optimized outputs must be byte-identical in CI.

## A2 — total evaluator accidentally substituted for R2 partial evaluator

R2 defined `nu_kappa` as partial, while the first R3 finite fixture and Lean definition used total maps.

**Disposition:** repaired before merge. The executable fixture contains an undefined history, and the Lean definition uses `Option W`; only defined values enter attainability.

## A3 — history frontier confused with value frontier

The first finite checker computed Pareto frontiers over history identifiers. That silently identifies “one history” with “one contextual value” and would overcount if two histories had the same evaluation.

**Disposition:** repaired before merge. The fixture now contains two distinct histories with the same value; the attainable image deduplicates them and the frontier is computed over values.

## A4 — bare attainability set was overclaimed as sufficient structure

Capability, resource response, frontier/preference, barrier identity, and cross-context regime change do not follow from an unlabelled set alone.

**Disposition:** claim narrowed. `A_kappa(x)` is the master **carrier relative to inherited/declared context structure**:
- capability needs a success region;
- frontier needs the context preorder;
- resource response needs a resource projection or resource-bearing context;
- barrier claims need a registered relaxation/intervention family, and minimal/causal claims need further structure;
- cross-context comparison needs a common result space/order or explicit transport.

This preserves the two-factor candidate `(C_S,K)`; it does not add a third universal primitive.

## A5 — “barrier” non-uniqueness

Baseline impossibility does not identify which missing process/condition caused it. The finite fixture has three distinct one-step enabling histories.

**Disposition:** R3 records **one-step enabling witnesses**, not a unique causal barrier. Stronger barrier minimality or causality is deferred to an explicitly ordered/causal intervention model.

## A6 — “phase change” terminology was too strong

A change of scalarized argmax across context parameters is a selection-regime switch. It is not automatically a physical/statistical phase transition or a nonanalyticity theorem.

**Disposition:** the fixture now checks the exact switch point `lambda = 3/2`, including the tie there, and forbids promotion beyond an argmax/frontier regime change without extra topology/regularity.

## A7 — budget monotonicity needs nested admissible sets

A scalar budget label does not imply that the induced admissible-history sets are nested.

**Disposition:** the theorem is stated conditionally on actual set inclusion. Any resource family invoking “larger budget” must prove/register the nesting map.

## A8 — old-symbol retirement is not automatic theorem transport

Removing `Gamma/Pref/SEL` from the universal primitive vocabulary does not prove every historical theorem invariant under the new presentation.

**Disposition:** every transport must restate quantifiers, evaluator domain, history-vs-value semantics, inherited order/resource/success structure, and any cross-context transport.

## Merge consequence

R3 may merge only if the successor checker/oracle, optimized-route parity, Lean kernel check, freeze custody, and review-thread closure are green. The surviving claim ceiling is:

`GRAND_GMI_V2_R3_CONTEXTUAL_ATTAINABILITY_MASTER_CARRIER_AT_REGISTERED_SCOPE`
