# W4 novel-intelligence freeze V1

Frozen **before** family-member search on this branch.

Authority targets: #592 item 39 (earn W4 at registered exact family scope),
#602 P4 residual novelty. Composes after #796 `gmi-unseen-form-prediction-v1`
(V6 exact RQM scope; W2/W3 green; W4 not claimed upstream).

## Freeze seed

```text
sha256("GMI-NOVEL-INTELLIGENCE-W4-V1/RQM-FAMILY-RECURRENCE")
  = 57ddb8d1195e0eba61e0527828882bce1f9e0da24a4474ef3a69b7c6c71789c9
```

(The executable recomputes this digest and refuses to run if it disagrees.)

## Registered parametric family F(k)

For each integer `k ∈ {2,3,4}` construct sparse-alias ecology with
`|S_P|=2`, `max_m=k`, `|S_O|=k+2`:

```text
q_P = (0,)^k + (1,)^k
q_O = (0..k-1) + (k + (i%2) for i in 0..k-1)
```

Property-first family law (stated before search):

```text
max_m(k) = k
C*(k) = 2 + k
flat_table_cost(k) = k + 3
material gap vs flat = 1
needs_residual = true
```

Neutral search remains conditional on registered `q_P` (P fixed; residual
enumerated), as in the upstream V6 capsule.

## Fixed-budget parent (family discriminator)

```text
FIXED_BUDGET_B = 3
```

A residual alphabet capped at fixed `B`, independent of measured `max_m`, is
allowed as a comparison parent only. It is **not** the family residual law:

- `k < B`: recovers but overprovisions (does not track `max_m`)
- `k = B`: locally matches
- `k > B`: fails exact recovery

Family recurrence across distinct `k` therefore leaves a material residual
against this parent.

## Held-out fresh ecology (outside family)

```text
FRESH_K = 5  (not in {2,3,4})
predict before search: max_m=5, C*=7, flat=8, zero-residual impossible
fixed-budget B=3 must fail recovery
```

## Upstream compose gate (frozen requirement)

Upstream V6 receipt must show:

```text
all six V6 boxes green
W2_parent_separation = true
W3_empirical_niche = true
W4_domain_status = false
phase_hole_occupant_claim = false
```

## Explicit non-claims

This freeze does **not** claim:

```text
NEW_DOMAIN / J4
NEW_FORM_OF_INTELLIGENCE_PROVEN
atlas phase-hole occupancy
P4 surviving-unseen-domain (J4 gate)
```

Phase-hole honesty: prior open-niche prediction failed (known parent occupant).
This capsule does not revive that claim.

## Terminals allowed only after all W4 boxes

```text
W4_RESIDUAL_QUOTIENT_STRUCTURAL_DOMAIN_AT_REGISTERED_FINITE_FAMILY_SCOPE
NOVEL_INTEL_LADDER_W2_W3_W4_GREEN_AT_EXACT_RQM_FAMILY_SCOPE
```
