# Grammar-growth theorems, tranche 2 (E8 / #897 follow-up)

Scope: the additions frozen by `FREEZE_V2.md` (commits `65df05af`, `74d0a24e`),
on top of the v1 theorem note (`GRAMMAR_GROWTH_THEOREMS_V1.md`, T1–T6).
Every quantity is an exact integer recomputed by `independent_oracle_v2.py`.

## T7 (formation saturation at generational depth 3 under INV-1)

**Separator-pair dominance.** Let the corpus contain `P` programs, each
consisting of `n ≥ 2` copies of a current-alphabet unit `u` (`|u| = b ≥ 2`)
separated by single non-`u` symbols (separator form). Both `u` and `u c u`
are pool candidates with greedy occurrence counts `o(u) = P·n` and
`o(u c u) = P·⌊n/2⌋`. Then the charged gains satisfy

```text
gain(u c u) − gain(u) = P·n − b − 1        (for even n; κ cancels)
```

so the pair-with-separator strictly dominates the unit whenever
`P·n > b + 1` — e.g. `P = 4, n = 4, b = 4`: `16 > 5`, margin `11`
(measured: c4 level 2 admits `(m1)^4 c (m1)^4`, gain 54 vs unit gain 43).

**Run-internal dominance.** Within a maximal run of `X ≥ 3` copies of `u` per
program, the candidate `u^k` has `gain(k) = P·⌊X/k⌋(k−1) − k − κ`; for
`P ≥ 4, X ≥ 4` the maximizer is `k ∈ {X/2, X}` (never `k = 2`): at the frozen
c3 shape (`X = 8, P = 4`) `gain(4) = gain(8) = 19 > gain(2) = 13`, and the
frozen expand-order tie-break selects `k = 4`, leaving runs of exactly two
units — which is why the pure-run depth-3 witness terminates in the *pair*
body `m3 = (m2, m2)` (gain 1, the strict-positivity floor).

**Corollary (depth-3 ceiling, rule-attributable).** Under INV-1 every frozen
attempt at depth ≥ 4 collapses in exactly three admissions
(symbol → maximal repeated unit/pair → whole program), because at each level
the dominance inequality holds for the current unit: separator corpora
(`c4`, `c5` — designed for depth 4/5) stop at depth 3 with single-symbol
programs, and pure-run corpora can never exceed depth 3 (a single-symbol
program admits no positive-gain candidate: `b = 1 ⇒ gain = −1 − κ < 0`).
The ceiling is attributable to the frozen greedy gain order, not the
language: the registered ADM-ALT diagnostic (smallest body referencing the
latest macro, same charges) forms depth **7** on `c4` and depth **9** on `c5`
(`RESULT_V2.json:adm_alt`), with GRW-1 semantics preserved throughout.

## T8 (EXEC-B execution-cost burden, exact closed form)

With per-symbol op costs `cost(s)` (`cost(base) = 1`, `cost(m) = ρ + Σ body`),
`C = Σ_s cost(s)` over the alphabet `A`, first-hit length `ℓ*` and lex-min
hit program `h`:

```text
exec-burden = Σ_{l=1..ℓ*−1} l·A^(l−1)·C                    (full lengths)
            + Σ_{i, s < h_i} [ A^r·(prefix_i + cost(s)) + A^(r−1)·r·C ]   (lex prefix)
            + exec(h),        r = ℓ*−1−i
```

**Proof.** Each symbol occupies each position of the length-`l` class exactly
`A^(l−1)` times (additivity of exec over symbols); within the hit length,
programs lexicographically before `h` split into free-tail blocks whose count
and cost sums are closed forms; the identity is verified against naive
enumeration on the HEXEC-1 battery (all cases match, `ρ ∈ {1,2,4}`, including
misses and deep chains) and independently by the oracle's recursive
prefix-tree summation. ∎

**Flagship consequence (EXEC-1R).** Under EXEC-B the v1 headline survives with
margin: H+ exec net `−395484 / −393054 / −388194` at `ρ = 1/2/4`
(count metric: `−48739`), H− regression preserved (`+10304 / +13592 / +20168`),
exact break-even `ρ† = 164` (net(ρ) is monotone increasing in ρ; `ρ† ≤ 1024`).
**Cost-model fragility, reported not hidden:** under EXEC-B(ρ=1), `19/200`
equal-size random-admission nulls beat the true recursive library
(exec-null min `−396644 < −395484`; count metric: `0/200`, v1 rank 1
preserved). Mechanism: the flat `abab` macro (op cost `ρ+4 = 5`) is cheaper to
execute than the recursive `m2 = (m1,m1)` (op cost `3ρ+4 = 7`) at the same
description length, so execution-cost accounting de-ranks recursion relative
to flat encodings — the v1 *net* claim is cost-robust, the v1 *rank* claim is
cost-relative.

## T9 (tier-conditional compounding; the T4 question resolved at scope)

A depth-`g` macro shortens the minimal description length `ℓ*` of a target
only if the target segments through the macro's expansion (≥ 2 greedy-disjoint
occurrences for aggregate effect), while every admission widens the alphabet
(`3 → 3+g`), multiplying the enumerated volume at every length below the hit
(v1 T4). Therefore, per tier of target reuse depth `t`:

- for `g ≤ t`: burden strictly decreases (compounding through the match);
- for `g > t`: burden strictly increases (pure widening + charges);
- the unrelated control strictly increases at every `g`.

Measured (c3, κ=1, charged): T1 `1712 → 732 → 1296 → 2098`;
T2 `1.97e9 → 7.68e6 → 4130 → 7652`; T3 `3.15e16 → 1.22e11 → 20616 → 1350`;
H− `429 → 771 → 1257 → 1911`. Aggregate charged nets strictly decrease
(net −3.15e16 at full depth; per-macro THR-1 marginal identities hold:
`8 > 3`, `24 > 5`, `8 > 3`; aggregate `40 > 11`). The same pattern holds on
c4 (T3sep `… → 5360 → 10215`; T4 `… → 2061996 → 6474`) and c5
(T4sep `… → 2718 → 5270`; T5 `… → 1671370 → 5177`). Compounding is real but
**tier-conditional**: it is not a blanket "deeper is cheaper".

## T10 (registered tranche-2 run facts)

- Formation: c3 `m1=ab (o=51,g=48)`, `m2=(m1)^4 (8,19)`, `m3=(m2,m2) (4,1)`,
  saturation, depth 3, S_0=102; c4/c5 separator chains
  `m2=(m1)^4c(m1)^4`, `m3=(m2,c,m2)`, depth 3 (not 4/5), S_0=240/518;
  family ceiling fn5/8/12 depth 1, fl8/fl16 depth 2; ADM-ALT depth 7/9.
- Economics: f* = 19/50/115 (strict; tie cases 18/49/—), κ* = 1/4/4;
  S_0-per-depth 23 (d2, v1) → 102 (d3) → 240, 518 (attempts, still d3).
- Head-to-head (count, charged): v1ref/c4/c5 exact ties; c3+shallow-V
  compression better by 14939 (utility gate rejects m3); c3+deep-V tie;
  trap1 utility better (−19433 vs −12892; 0/200 nulls beat the utility arm,
  52/200 beat the compression arm); trap3 compression regresses
  (`+43897 > 0`, worse than primitive) while utility wins (−17348 = the best
  single macro in the pool; the null-ensemble min equals it exactly).
  Exec verdicts agree in sign everywhere.
- Nulls (count): c3/c4/c5 all rank 1 (0/200 better); v1ref reproduced 0/200.
