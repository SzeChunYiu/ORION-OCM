# SCOPE_V1 — what is measured, and how each number is defined

## 1. The external capability, defined without reference to `F`

For a machine `x`, a contract `E ∈ {E_full, E_v0}` and a registered resource
pair `R = (budget, charge)`:

```
extcap(x, E, R) = UNSATISFIED                        if rho(x) exceeds budget-charge
                = sum_{j verified by E} mu_j * [ x answers task j correctly
                                                 on EVERY protected item ]   otherwise
```

"Answers correctly on every protected item" is decided by **running the
machine** over the whole protected battery and comparing exactly — never by
consulting a registered table. This is the definition of "externally evaluated
capability" used by every row below. The `UNSATISFIED` branch is the external
counterpart of the parent's load-bearing decision: an over-budget machine is
*scored* `UNSATISFIED`, it is not deleted from the population.

## 2. Row-by-row definitions

### Held-out synthetic species / held-out known architectures

For each of the 51,840 registered inputs, `F` emits `IDENTIFIED(v)`,
`CANNOT_IDENTIFY(S)`, `INCONSISTENT_REGISTERED_ASSUMPTIONS` or `CANNOT_CHECK`.
Scoring, over (input, consistent-realization) pairs:

- **hit** — `IDENTIFIED(v)` and `extcap` of the realization equals `v`;
- **miss (soundness violation)** — `IDENTIFIED(v)` and `extcap` differs;
- **abstention** — `CANNOT_IDENTIFY`; scored neither hit nor miss, and reported
  with the power figures so it cannot be mistaken for success;
- **coverage hit** — `extcap` lies in the emitted identified set (applies to
  both dispositions).

Power is reported as the exact rationals `point_rate`, `abstention_rate` and
`abstention_rate_among_answerable`, plus the per-threshold count of
*non-degenerate* inputs (inputs where the survivors genuinely disagree about
meeting `tau`), because a threshold on which every survivor agrees cannot
discriminate failure modes.

### Predict qualitative failure before evaluation

The frozen prediction carries, per input, the single live mode of the ten-mode
KP-2 taxonomy. The outcome is the *externally attributed* mode, recomputed from
`extcap` by the independent evaluator. The confusion matrix is reported
separately on the `ORDER_FREE` stratum (a unique binding cut exists) and on the
`CONJUNCTIVE` stratum (KP-2D: no order-free attribution exists, so a mismatch
there measures the ambiguity, not the predictor).

### Predict quantitative resource/capability curves before evaluation

Per registered curve case, the resource coordinate `R.budget` is swept over all
three registered budgets and the predicted disposition/point is frozen at every
swept point. The outcome is the exact externally evaluated curve. Reported as
per-point exact agreement counts — never a fitted summary, never an error norm.

### Measure calibration error

Coverage is measured against the U-2B premise the emission actually carries:
`L = max(0, 1 - alpha - sum(beta))` with `beta = (1/100, 1/200, 1/500, 1/50)`,
so `L = 913/1000` at `alpha = 1/20` and `863/1000` at `alpha = 1/10`.

The parent proved exact coverage at finite scope with all registered relations
assumed good; that is coverage 1 and says nothing about calibration. This row
therefore measures coverage under the **registered fault law**, which is the
event structure the `beta`s are premises about: each of the four relations
`M`, `D`, `B`, `H` independently fails with exactly its registered probability,
and on failure the true realization need only satisfy the surviving cuts. The
resulting coverage is an exact rational obtained by enumerating all 16 fault
patterns against the whole universe with exact weights.

```
calibration_error(stratum) = empirical_coverage - L      (exact, signed)
violation                  = empirical_coverage < L
```

Every calibration figure is reported together with the abstention rate on the
same stratum, and separately for point emissions only (the harsh test, where
coverage is `P(extcap == point)`), because a predictor that abstains whenever
unsure is trivially well covered.

### Measure out-of-distribution failure

OOD is defined **structurally**, not by intuition: a world is out-of-universe
iff its registered realization is not a member of the installed universe. Two
strata are reported and never merged:

- **in-universe** — the true realization is in the survivor set. KP-1B predicts
  0 soundness violations; the verified region's exact size is reported.
- **out-of-universe** — the true realization is drawn from `SIGMA_OOD`,
  constructed by relaxing each registered generator coordinate one at a time.
  Here a wrong point is *not* a new finding: it is the parent's declared
  boundary KP-1D restated, attributable to registration. The scientifically
  interesting quantity is the size of the OOD region over which `F` nonetheless
  abstains, and the exact boundary between the two.

## 3. Two materially independent routes

Route A is the closed-form registered law plus the parent's bitmask machinery.
Route B (`oracle_route_b_v1.py`) does not import `capability_predictor_v1` or
`heldout_universes_v1` at all: it re-declares the populations as explicit tuples,
represents survivor sets as Python `frozenset`s of realization records rather
than integer bitmasks, computes the contract image by direct set comprehension,
and simulates every machine from its own independently written simulator. Route B
must reproduce disposition, identified set, failure mode and composed budget on
every input of every universe.
