# FREEZE_V1 amendment 2 — `B3′`, the corrected threshold prediction, scored on a new hidden set

Written **before any case of the new hidden set exists and before any score
of `B3′` has been seen**; committed before the revival executor. `FREEZE_V1.md`
and `FREEZE_V1_AMENDMENT_1.md` are not edited. **`B3` stays `MISS`**: nothing
here repairs it, and the register entry this amendment creates supersedes
nothing.

## 1. What missed, attributed to one stage

`FREEZE_V1.md` §6 froze `B3` as "`T_HALF` misses thresholds on **every** `C2`
case with `q ≠ 1/2` and **every** `C3` case with `A ≠ 2`". The receipt counts
`144/162` and `48/54`. The `18 + 6` cases that spoil the universal quantifier
all have `p = (1, 0)`: the delay-1 channel carries no weight, the true
threshold is `η · p_1 · R_0 = 0`, and every registered theory — `T_HALF`
included — predicts `0` there. The failure is in the **wording of the
prediction** (a quantifier that ran over the `p = 0` boundary of the eighths
grid), not in the theory being scored, not in the scorer, not in the case set.
The `p > 0` reading (`144/144`, `48/48`) was derived after the run and is
recorded in `FAILED_PREDICTION_REGISTER_V1.json` as **not scored**.

A corrected sentence scored on the same cases would be post hoc. It is scored
here only on cases that do not yet exist.

## 2. The corrected prediction `B3′`, frozen now

On the new hidden class `C8_HIDDEN_B3PRIME` of §3, with `p_1` the weight of the
delay-1 channel of a two-level case and `p_2` the weight of the delay-2 channel
of a ladder case:

- `B3′(i)` on every two-level binary `IID(q)` case, `T_HALF`'s threshold cell
  is a `MISS` **if and only if** `p_1 > 0` and `q ≠ 1/2`;
- `B3′(ii)` on every two-level alphabet-`A` case, `T_HALF`'s threshold cell is a
  `MISS` **if and only if** `p_1 > 0` and `A ≠ 2`;
- `B3′(iii)` on every ladder case, `T_LEVEL`'s upper threshold cell (`Δ_1`) is a
  `MISS` **if and only if** `p_2 > 0`, and its lower cell (`Δ_2`) is a `HIT` on
  every ladder case;
- `B3′(iv)` `T_LEVEL` is `MISCALIBRATED` on `C8` (its `γ = 1` coverage is below
  `1`) if and only if at least one ladder case has `p_2 > 0`.

The "if and only if" form scores both sides of the `p = 0` boundary: the cases
the old quantifier tripped over are now predicted to be `HIT`s, and a `HIT`
where a `MISS` is predicted, or a `MISS` where a `HIT` is predicted, on any
single case makes `B3′` a `MISS`. **Vacuity**: each of the six sub-populations
(`IID` miss-set and its complement, alphabet miss-set and its complement,
ladder `p_2 > 0` and ladder `p_2 = 0`) must be non-empty; if any is empty the
verdict is `VACUOUS`, which is not a `HIT`.

`B3′` is scored **prospectively**: `HIT`, `MISS` or `VACUOUS` goes into the
register as a new entry `B3_PRIME` with `supersedes: none`.

## 3. The new hidden class `C8_HIDDEN_B3PRIME`, generation rule fixed now

`240` cases drawn by `random.Random(secret_2)` where

```
sha256(secret_2) = e35afc4af6ce3ca4c8d078a7848541020ada4bd3bdc0cfa44fea36b3ebfea20d
```

The preimage is revealed only in the revival executor commit; a wrong
preimage fails the commitment check (`HZ6′`). Per case, draws in this exact
order:

1. `family = rng.randrange(3)`;
2. `η = rng.randrange(1, 5)`;
3. if `family == 0` (**ladder**, `UNIFORM`, alphabet `2`): `p = comps[rng.randrange(153)] / 16`
   where `comps` is the list of the `153` ordered triples `(a, b, c)` of
   non-negative integers with `a + b + c = 16`, ordered with `a` ascending
   then `b` ascending (the executor's `compositions(16, 3)` order);
   if `family == 1` (**two-level binary**, `IID(q)`): `k = rng.randrange(17)`,
   `p = (1 − k/16, k/16)`, then `q = rng.randrange(1, 10) / 10`;
   if `family == 2` (**two-level alphabet**, `UNIFORM`): `k = rng.randrange(17)`,
   `p = (1 − k/16, k/16)`, then `A = rng.randrange(2, 5)`.

Every case carries the full price set `Λ = {j/16 : j = 0..24}`, so that the
discrimination set and the scrambled-truth control have cells to score. The
`p = 0` boundary is deliberately inside the draw (`k = 0`, and `b = 0` triples)
so that both sides of every `B3′` clause are populated. `q = 1/2` and `A = 2`
are inside the draw for the same reason.

Hidden truth, theories, record schema, scoring, the `200`-theory null and the
scrambled pairing are exactly those of `FREEZE_V1.md` §1–§5 and
`FREEZE_V1_AMENDMENT_1.md`; nothing is re-registered. The class-set `sha256`
of `C8` is committed by the executor over the canonical JSON of its `240`
public specifications; route B must reproduce it from this rule and the
revealed preimage.

## 4. Out-of-sample specificity, frozen now

The same run reports, on `C8` alone:

- `S1` `T_DECLARED` disagrees with `T_GMI_IC1` on `0` cases (`NON_DISCRIMINATING`);
- `S2` the scrambled-truth control under the governing clause of
  `FREEZE_V1_AMENDMENT_1.md` (literal form governs unless it alarms on
  `T_GMI_IC1`; then the informative-cell form governs and the switch is
  disclosed): `T_GMI_IC1` at or below the best null, and the planted truth
  reader `T_PEEK` under a leaky harness strictly above the best null (`HZ1′`
  applicable and detected);
- `S3` `C7_DISCRIMINATION` on `C8`: the pair `T_GMI_IC1|T_DECLARED` counts `0`
  and every pair `T_GMI_IC1|T` for `T ∈ {T_HALF, T_LEVEL, T_MDL, T_OCCAM_HARD,
  T_SRM, T_SATISFICE}` counts at least `1`; the full per-pair table is reported.

`S1`–`S3` are scored `HIT`/`MISS` like `B3′` and go to the register the same
way. A `HZ5′` hostile (a tampered `C8` rule — the price set truncated to
`j = 0..23` — changes the `C8` class-set `sha256`) must be applicable and
detected.

## 5. What this amendment does not do

- It does not redraw `C5_HIDDEN`, edit `CASES_V1.json`, `PREDICTIONS_V1.json`,
  `RESULT_V1.json` or `ORACLE_RESULT_V1.json`, or change the case-set `sha256`
  `c8de5c75e4786e4731c19b6aad29eb282eddea8b0b6c95f1b842a57ec723619f`.
  `C8` is a **supplementary** hidden set with its own receipts
  (`CASES_B3PRIME_V1.json`, `PREDICTIONS_B3PRIME_V1.json`,
  `RESULT_B3PRIME_V1.json`, `ORACLE_RESULT_B3PRIME_V1.json`); the forbidden
  promotion `HIDDEN_CASES_REDRAWN_AFTER_A_SCORE_WAS_SEEN` is therefore not
  touched.
- It does not change the verdict of `B3`, the headline table, or any row
  reconciliation. A new forbidden promotion is added:
  `B3_MISS_REPAIRED_BY_B3_PRIME` — `B3′` is a new prediction with its own
  verdict, never a re-scoring of `B3`.
- It does not widen scope: `C8` stays inside `L = 4`, two symbols or alphabet
  `≤ 4`.

Two materially independent routes must agree on every `C8` number: route A
(`b3prime_revival_v1.py`, built on the route-A executor's enumeration) and
route B (`independent_b3prime_oracle_v1.py`, built on the route-B oracle's full
machine enumeration, importing nothing from route A).
