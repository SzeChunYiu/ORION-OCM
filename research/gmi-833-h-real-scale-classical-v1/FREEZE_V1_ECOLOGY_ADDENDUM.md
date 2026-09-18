# Ecology addendum to `FREEZE_V1.md` — committed before any byte of `D1`–`D3` is read

`FREEZE_V1.md` (commit `0cf9e1e65354b03daf633e36e1dabadb998dcdfa`) named the four
ecologies and left their exact construction to this addendum. This file is
committed **before any executor, extractor, fit, or data read exists**. It adds
no prediction and relaxes nothing: `FREEZE_V1.md` Sections 7–10 stand unchanged.

## A1. `E_H01` — real symbol stream from `D1`

`D1` bytes in source order. Byte to symbol: `a`–`z` -> `0..25`; `A`–`Z` -> the
same `0..25`; every other byte -> `26` (separator). The stream is the full
972,398-symbol image. Row `t` (for `t = 0 .. N-2`) has input the one-hot vector
of `symbol[t]` over the 27 symbols and response `y_t = 1` if `symbol[t+1] == 26`
else `0`. The protected interface is the exact held-out count of decisions
`STEP(OUT_t) != y_t`.

## A2. `E_H02` — real PCM autoregression from `D2`

The nine files in ascending filename order, each decoded as 16-bit signed mono
PCM and concatenated into one stream of 614,266 samples `x_0..x_{N-1}`. Row `t`
(for `t = 32 .. N-1`) has input `ARG_i = x_{t-32+i} / 32768` for `i = 0..31`
(exact rationals, denominator 32768) and response `y_t = x_t / 32768`. The
protected interface is the exact held-out sum of squared errors and the exact
held-out count of `sign` disagreements, both in `Fraction`.

## A3. `E_H03` — real over-dispersed count response from `D3`

The 659 files in ascending path order, decoded `latin-1`, split on `\n`. Rows
are the lines with at least one character, in order. Response `y` is the number
of characters in `0123456789` in the line — a non-negative, heavily
zero-inflated, over-dispersed count. Input is the 12-vector, digits excluded so
no response information enters the design:

`len/64`, `leading spaces/16`, `letters/64`, `spaces/64`, `_ /8`, `= /4`,
`(+) /8`, `[+] /8`, `, /8`, `. /8`, `"+' /8`, `# /4`.

The protected interface is the exact held-out count of rows on which one arm's
rationalised predicted mean is strictly closer to `y` than the other's, and the
exact held-out count of negative predicted means per arm.

## A4. `E_H04` — real future-window energy from `D2`

The same stream as `E_H02`, `W = 32`. Row `t` (for `t = 32 .. N-33`) has input
`ARG_i = x_{t-32+i} / 32768` for `i = 0..31` and response
`y_t = (1/W) * sum_{k=0..W-1} (x_{t+k} / 32768)^2` — the mean energy of the
**next**, unseen window, a non-affine functional of a future segment. The
protected interface is the exact held-out sum of squared errors at charged cost.

## A5. The registered cost model (uniform across all four scopes)

Charged cost of a prediction rule = `ops + storage`, both exact integers.
`ops` counts one unit per `G_R` operation actually evaluated per prediction,
with the fold charged at the real index-set size. `storage` counts one unit per
stored rational parameter or table cell.

The **tabulated alternative at index-set size `m`** is the lookup table over the
sign-quantised first `m` input coordinates: `2^m` cells, `ops = m` (the `m`
quantisation tests), `storage = 2^m`. The **crossover `m*`** reported at every
scope is the smallest `m >= 1` at which the tabulated alternative's charged cost
strictly exceeds the selected compact composed program's charged cost at that
same `m`. It is an exact integer and is computed by exhaustive ascent from
`m = 1`.

`SIGMA_H01` additionally reports the automaton-versus-history-table crossover:
the smallest history length `h` at which `27^h` exceeds the selected machine's
charged cost. `SIGMA_H04` additionally reports `q_b*`, the smallest landmark
count at which the landmark arm's charged cost exceeds the explicit
degree-two basis arm's charged cost on the same design — the kernel-trick
crossover.

## A6. Arms fitted at each scope

| scope | selected arm | registered comparison arm(s) |
|---|---|---|
| `SIGMA_H01` | blind-search winner | best stateless winner; majority-class rule |
| `SIGMA_H02` | blind-search winner | best constant rule; majority-sign rule |
| `SIGMA_H03` | blind-search winner | log-link Poisson arm and identity-link Gaussian arm, same design |
| `SIGMA_H04` | blind-search winner | affine arm on the same design; landmark arm at `q = 1..64`; explicit degree-two basis arm |

The `SIGMA_H04` landmark arm uses the algebraic kernel
`k(x,z) = RECIP(ADD(C1, sum_i MUL(ADD(x_i, NEG(z_i)), ADD(x_i, NEG(z_i)))))`,
built from `G_R` operations only, with landmarks the fit-slice rows at indices
`j * floor(n_fit / q)` for `j = 0..q-1`.

## A7. Supplementary contiguous-tail evaluation (stricter than `FREEZE_V1.md`)

`E_H02` and `E_H04` are sliding-window ecologies, so the `mod 5` held-out slice
of `FREEZE_V1.md` Section 4 interleaves with the fit slice and its windows
overlap fit windows. That is recorded here as a known weakness of the frozen
slice rule. In addition to the frozen protected interface, every claim at every
scope is **also** evaluated on the contiguous final 20% of the source, which no
arm is fitted on and whose windows do not overlap any fit window (the boundary
`W + 32` rows are dropped). A row closes only if the frozen held-out evaluation
and the contiguous-tail evaluation give the same qualitative verdict. This
requirement is strictly stronger than `FREEZE_V1.md`; nothing in it is relaxed.

## A8. Search procedure (frozen, identical at all four scopes, family-blind)

1. Enumerate `BODY` (<= 3 nodes) and `HEAD` (<= 4 nodes) exhaustively per
   `FREEZE_V1.md` Section 5 and quotient each by its exact denotation on the
   registered probe grid. This happens once, before any ecology is loaded.
2. Quotient the resulting pairs by their joint denotation on the scope's own
   **input** domain probe (targets are not read).
3. Screen: fit only two scalars — one `BIAS` and one value shared by all
   `PARAM_i` — over the exact rational grid `{-3,-2,-1,0,1,2,3}^2` on the first
   `n_screen = 300` rows of the search slice; keep the best 40 pairs by exact
   rationalised loss.
4. Search: fit the full parameter vector of each surviving pair by generic
   coordinate descent over the grid `{-4,-3,-2,-1,0,1,2,3,4}` scaled by the
   scope's registered step, 4 sweeps, on `n_search = 20000` rows of the search
   slice; the winner is the pair with the lowest exact rationalised loss, ties
   broken by fewer nodes then by lexicographic expression string.
5. Fit the winner and every registered comparison arm at full real scale on the
   fit slice, rationalise, then evaluate on the held-out slice and on the
   contiguous tail.

No step receives a family name, a family identifier, or a target-specific
candidate list. The structural class is attached after step 4 by a classifier
that reads only the winning expression tree.
