# Interface revival result

The 54 frozen `#164` refusals were classified from their retained P1
contracts, then replayed in original ordinal order against the bound
teaching packet. Predecessor sources were not rewritten.

Exclusive first-match subtypes (sum 54):

| Subtype | Count |
|---|---:|
| Extra DV | 0 |
| Extra `$e` | 10 |
| Non-class floats | 14 |
| Missing 3 params (exactly two class, no `$e`) | 22 |
| Other | 8 |

The 22 two-class roots share one missing parameter interface. P1 already
has class syntax (`csymdif`, `cdif`, `cun`, `cin`, `cvv`, `c0`, …). The
successor therefore admits 2- or 3-class packets with empty DV / empty
`$e`, and admits 0-ary P1 syntax constructors the same way the syntax
revival admits 0-ary `wff` constants. `stack[-0:]` is not used.

| Stage | Count |
|---|---:|
| Roots replayed | 54 |
| Still `UNKNOWN_INTERFACE` | 25 |
| Roots newly enumerated | 29 |
| Roots newly with ≥1 `CUT_PROPOSAL` | 25 |
| New `CUT_PROPOSAL` rows | 133 |
| of which 2-class | 88 |
| of which 3-class (0-ary companion) | 45 |
| Native calls | 0 |

The 22 two-class roots all enumerate. Eighteen of them yield 88
proposals (`symdifcom`, `unabs`, `dfun3`, …). Four enumerate without a
proposal: `undm` / `indm` have no two-node edge; `n0i` / `ne0i` are the
whole training proof.

The eight “other” roots are seven three-class proofs that failed the
predecessor at `stack arity` because they use `cvv` or `c0`, plus
four-class `ss2in`. The 0-ary constructor admission unblocks those seven
(45 proposals). `ss2in` stays `UNKNOWN`. Extra `$e` (10) and non-class
floats (14) stay `UNKNOWN`.

Not claimed: alias classification, causal method reuse, native admission,
novelty. Ready traces already have empty DV; the 57 `#164`
`TRACE_UNUSABLE` rows were not replayed.
