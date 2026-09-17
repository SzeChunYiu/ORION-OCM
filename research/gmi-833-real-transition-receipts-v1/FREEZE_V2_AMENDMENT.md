# FREEZE V2 AMENDMENT — data-derived stateless floor (registered revival of FREEZE_V1.md)

**Status:** amendment registered under the FREEZE_V1.md Section 7 revival clause, BEFORE any full-scale outcome run. FREEZE_V1.md (commit `cd6196aa5fd0edcdbcfb535ff2aecf7cd0870754`) is never edited and remains the prediction-of-record.

## A1. Failure attribution (V1 smoke finding)

A machinery smoke run (T capped at 8,000, 1 epoch; scratch artifacts only, no receipt outcomes) showed the trained stateless MLP reaching delayed-mode error `0.426` on `R02-alsa-frontcenter` — significantly below the V1-assumed analytic floor `1/2` (3-sigma binomial band at the smoke counts excludes `1/2`).

Root cause (one stage): V1 Section 4 assumed uniformly distributed bits, so any stateless delayed predictor has error exactly `1/2`. Real registered sources have biased and temporally correlated bits, so (i) the marginal majority-bit prediction already beats `1/2`, and (ii) adjacent-bit correlation lets a stateless predictor beat even the marginal `min(P(0),P(1))`. The analytic constant `1/2` is therefore not the stateless floor on real data.

## A2. Lever (single registered change)

Replace the analytic floor constant with the **empirical stateless floor**: `floor_del :=` median (over registered seeds) delayed-mode eval error of the trained `B = 0` candidate of the same system. Everything else in V1 (task family, pools, prices, `lambda_low = lambda*/2`, `lambda_high = 3 lambda*/2` with `lambda* = p/(16H)`, predictions, controls, custody) is unchanged.

## A3. Amended classification rule (blind, numeric-only inputs)

The classifier receives only: the selected candidate's `(B, err_imm, N_imm, err_delay, N_delay)` and the system's `(floor_del, N_delay)`. With `sd = sqrt(0.25/N_delay)` and `sd_diff = sqrt(0.5/N_delay)` (conservative two-proportion bound at worst-case variance):

- trainability gate (unchanged): `ABSTAIN` unless `err_imm <= 1/2 - 3*sqrt(0.25/N_imm)`;
- `STATELESS` iff `B == 0` (the floor-setter itself; its delayed error defines `floor_del` by construction) and `err_delay <= floor_del + 3*sd` (sanity: it must not sit absurdly above its own median);
- `PERSISTENT_STATE` iff `B > 0` and `err_delay <= floor_del - 3*sd_diff` (persistent winner beats the empirical stateless floor beyond noise);
- otherwise `ABSTAIN` (`classification_identified = false`, receipt fails closed).

All thresholds are the standard 2/3-sigma binomial bounds at the measured counts; no tunable constants.

## A4. Derived licensed transition band (exact, replaces the q=1/2 premise)

With `E0 :=` stateless candidate median overall eval error (lambda-independent, measured before any persistent outcome is consulted) and `J_c(lambda) = p*err_c + lambda*B_c`:

- persistent wins at `lambda_low` iff `lambda_low*B_persist + p*err_persist < p*E0`;
- stateless wins at `lambda_high` iff `p*E0 < lambda_high*B_persist + p*err_persist`.

With `B_persist = 4H`, `lambda_low = p/(32H)`, `lambda_high = 3p/(32H)`, `err_persist -> 0`: the transition `PERSISTENT_STATE -> STATELESS` between the frozen endpoints is licensed iff `1/8 < E0 < 3/8`. This band is exact under the frozen grid and contains every source whose stateless overall error is not catastrophically biased. Systems measuring `E0` outside `(1/8, 3/8)` are `UNAVAILABLE_BY_AMENDMENT` and take their pre-registered fallback/spare; predictions apply only to licensed systems.

The V1 predictions for licensed systems are unchanged: `PERSISTENT_STATE` at `lambda_low`, `STATELESS` at `lambda_high`.

## A5. Amended per-system checks

- `stateless_floor_recorded`: `floor_del in (0, 1/2]` and the analytic-uniform expectation `1/2` is recorded but NOT asserted on real data (V1's assertion is retracted by this amendment);
- `persistent_beats_empirical_floor`: persistent candidate median delayed error `<= floor_del - 3*sd_diff` (else the system's persistent form has not demonstrated state use — the receipt fails closed);
- `licensed_band`: `1/8 < E0 < 3/8`;
- transition/prediction match, shifted-law falsification, boundary-tie controls: unchanged from V1.

## A6. Custody

This amendment is committed before the full-scale training run executes (V1 smoke artifacts were scratch-only and are not receipt inputs). The full-scale `REAL_RUNS/` artifacts, `RECEIPTS_V1.json`, and `RESULT_V1.json` are created only in descendant commits of this amendment. CI pins both the V1 freeze commit and this amendment's commit and asserts outcome files exist at neither.
