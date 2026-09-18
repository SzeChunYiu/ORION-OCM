# CORE — GMI #833 Section I: admissible update-law space and credit-assignment regimes

Read order: `FREEZE_V1.md` (pre-implementation custody, commit `5c5c36e4`) ->
`PARENT_OWNERSHIP_V1.md` (what is NOT claimed) ->
`UPDATE_LAW_SPACE_THEOREMS_V1.md` (the named results) -> `RESULT_V1.json`.

**Claim ceiling:**
`GMI_833_SECTION_I_UPDATE_LAW_SPACE_AND_CREDIT_ASSIGNMENT_REGIMES_AT_REGISTERED_FINITE_SCOPE`
Evidence EV1 + EV2, maturity M1 + M2. Finite registered scope only.

## What this answers

The direct parent (#870) proved that a useful preference between update laws
requires stated ecological and resource assumptions. It did not say which
assumptions buy which law. This tranche does, by derivation, without naming any
mechanism.

## The three results in one line each

- **IL-1** — the space of admissible update laws over the #837 realization
  contract: decidable at finite scope, closed under mixture and composition, a
  two-sided monoid on kernels, with two earned counterexamples and a mechanical
  name-freedom certificate.
- **IL-2 / IL-3** — evaluative-only updates beat directional ones exactly when
  the price ratio exceeds `rho* = mean_i (d_i+1)/(m_i+1)`, the mean reciprocal
  improving density along the path; the two conditions partition the registered
  space exactly, with no gap and no overlap.
- **IL-4** — the accumulation direction is recovered, not inserted: exact sweep
  counts with necessity, the exact retention-price threshold
  `sigma* = (n-p)E/(N-w)`, an unconditional converse at `p > n`, and an
  exhaustive census over an unnamed elimination-order space whose argmin flips
  with the output-to-input ratio.

## Headline numbers (all reproducible from `RESULT_V1.json`)

| quantity | value |
|---|---|
| IL-1 mixture cases / failures | 686 / 0 |
| IL-1 composition cases / failures at the closure grade | 49 / 0 |
| IL-1 decision bound per law per grade | 1134 exact rational operations |
| IL-1 subassociativity witness | 5 versus 8 at `(r0, h1, (9,9))`, coordinate `c_alpha` |
| IL-2/IL-3 registered paths x price ratios | 75 x 46 = 3450 cases |
| IL-2/IL-3 partition failures | 0 |
| IL-2/IL-3 verdict split | 2047 evaluative-only / 1331 directional / 72 ties |
| IL-2/IL-3 largest registered `rho*` | 7/2 at `d=6, m=1` |
| paths where direction is worthless (`rho* = 1`) | 19 / 75 |
| IL-4 `sigma*` | 21/2, 55/4, 32 on the three threshold graphs |
| IL-4 sweep counts at `p=1` | 1 against `n`, both necessary |
| IL-4 earned boundary | `skip_waist_n2_p2`: a mixed order costs 7 against 10 and 10 |
| two-route agreement | 3450/3450 verdicts, 21/21 probe entries, all IL-4 fields |
| hostiles detected | 14 / 14 |
| nulls | 0/200 shuffled thresholds locate a tie; 0/200 random orders beat reverse-topological on chains |
| A1 lexical screen | 0 denylist hits |
| A2 screen | 5 primitives x 11 signature fields, 0 findings |
| opaque-token remint | 14/14 verdict pairs invariant |
| total checks | 200, all green |

## Reproduce exactly

Standard library only, exact rational arithmetic, Python 3.8 compatible.
Run off this machine per the environment rule; the receipts below were produced
on laptop-billy with `python3` 3.8.10.

```
cd research/gmi-833-update-law-space-v1
python3 -I -B  update_law_space_v1.py            # route A, writes RESULT_V1.json
python3 -I -B  oracle_update_law_space_v1.py     # route B, writes ORACLE_RESULT_V1.json
python3 -I -B  test_update_law_space_v1.py       # 200 checks, prints ALL GREEN

python3 -I -O -B update_law_space_v1.py
python3 -I -O -B oracle_update_law_space_v1.py
python3 -I -O -B test_update_law_space_v1.py
```

`RESULT_V1.json` is byte-identical under both modes; the exact digest is
recorded in `MANIFEST_V1.json` and in the theorem note, which are excluded from
the lexical screen so that quoting the digest cannot perturb the receipt that
produces it. No claim is gated by a bare `assert`, which `-O` would erase.
CI: `.github/workflows/gmi-833-update-law-space-v1.yml`.

## What this does NOT close

Seven of the eleven Section I rows are untouched, and the binding forbidden
promotions are listed in `MANIFEST_V1.json`. The cheap-sensitivity principle,
the adjoint recursion and the elimination view are parent mathematics and are
not claimed here; see `PARENT_OWNERSHIP_V1.md`.
