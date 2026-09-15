# Section D V5 results and proof — boundary uncertainty + held-out scale extrapolation

Authority: issue #689; pre-outcome freeze commit `9d1fa1b0bbfdc8f12638aad7632d1ee6567c67b1`.

## Result

Every frozen V5 prediction passed exactly.

Tiny calibration scales `n=2,3,4` produce the phase walls

```text
x*(2) = 3/2
x*(3) = 2
x*(4) = 9/4.
```

Fitting only `n=2,3` to the preregistered form `alpha + beta/n` gives

```text
alpha = 3
beta  = -3,
```

and the untouched `n=4` calibration check is exact.

The two held-out larger scales then match the frozen prospective predictions without refitting:

```text
x*(7) = 18/7
x*(8) = 21/8.
```

At `n=8`, all `8! = 40,320` bijections are enumerated. Across all four candidates and all 16 directional queries per bijection, the witness executes 2,580,480 exact candidate/query checks. Across the five registered scales it checks 45,392 bijections and 2,863,664 candidate/query obligations.

## Exact phase law

For one 3-forward/5-reverse query block the resource vectors are

```text
key_index   = (n, 3+5n)
value_index = (n, 3n+5)
dual_index  = (2n, 8)
pair_list   = (2n, 8n).
```

For every `n>1`, key indexing is dominated by value indexing and the pair list is dominated by the dual index. Therefore only the latter two can lie on the lower envelope.

With persistent-cell price `x>0` and serve-op price 1, equality solves

```text
n x + (3n+5) = 2n x + 8
              => x*(n) = (3n-3)/n = 3 - 3/n.
```

Hence dual indexing is uniquely selected below the wall, value indexing is uniquely selected above it, and both tie on the wall. Direct all-candidate cost minimization and an independently coded lower-hull selector agree on every registered probe.

## Boundary uncertainty

Only the measured one-block serve totals are uncertain. Each of the value and dual measurements may err by `-1,0,+1`, independently. Therefore their operation difference

```text
Delta_C = 3n-3
```

is perturbed by `e_value-e_dual in {-2,-1,0,1,2}`. Because the memory difference is exactly `n`, every admissible wall is

```text
x_e(n) = (3n-3 + e_value-e_dual)/n.
```

Enumerating all nine error pairs gives the exact robust interval

```text
I_n = [(3n-5)/n, (3n-1)/n].
```

Held out:

```text
I_7 = [16/7, 20/7]
I_8 = [19/8, 23/8].
```

The unperturbed walls `18/7` and `21/8` lie inside their intervals.

The registered robust decisions also pass exactly:

```text
x=2    -> dual_index for every admissible perturbation
x=5/2  -> admissible perturbations disagree (and n=8 includes a tie), so CANNOT_IDENTIFY
x=3    -> value_index for every admissible perturbation.
```

This is the finite exact content of “quantify uncertainty”: not a point estimate with an unregistered error bar, but the complete image of the frozen bounded error set under the phase-wall map.

## Extrapolation and its scope

The `alpha + beta/n` form is not inferred after seeing the held-out worlds. The functional form, calibration scales, fitting rule and held-out scales were frozen first. The larger `n=7,8` walls therefore constitute a prospective finite extrapolation test.

The batching twin changes exactly one primitive accounting law: one scan operation can inspect two records, so scan cost becomes `ceil(n/2)`. Its wall is

```text
x_batch*(n) = (3 ceil(n/2)-3)/n.
```

At the held-out scales,

```text
x_batch*(7) = 9/7
x_batch*(8) = 9/8,
```

which disagrees strongly with the original `18/7` and `21/8`. Thus the successful extrapolation is conditional on the frozen scan primitive; V5 supplies its own non-universality control.

## Remint

Key labels are reversed and value labels are independently cycled. Every candidate remains exact, the resource vectors are unchanged, and therefore the fit, exact walls, uncertainty intervals and robust decisions are unchanged. No token identity carries the result.

## Parent subtraction

The mathematics is parent-owned:

- lower envelopes / normal-fan geometry own the price-wall picture;
- bounded coefficient sensitivity and robust optimization own the uncertainty-set propagation;
- indexing/data-structure theory owns the mechanisms;
- elementary rational asymptotics owns the `3-3/n` finite-size form.

The GMI residual is procedural and scoped: register an architecture-name-free resource family, freeze the scale form and uncertainty set, predict larger unseen phase walls, require robust abstention where the uncertainty set changes the winner, and keep a scope-failure twin beside the extrapolation.

## Box disposition

At this finite exact scope, V5 earns:

- [x] Quantify uncertainty in phase-boundary location.
- [x] Test phase-law extrapolation beyond fitted tiny worlds.

It does **not** earn real-scale empirical uncertainty, universal scaling, nonlinear-price closure, or a complete ecology/resource/verifier/history coordinate schema.

Claim ceiling:

```text
FINITE_EXACT_PROSPECTIVE_PHASE_BOUNDARY_UNCERTAINTY_V5
FINITE_EXACT_HELDOUT_SCALE_EXTRAPOLATION_V5
PARENT_OWNED_POLYHEDRAL_ROBUST_INDEXING_ASYMPTOTICS
NO_REAL_SCALE_UNIVERSAL_SCALING_OR_COMPLETE_COORDINATE_SCHEMA_CLAIM
```
