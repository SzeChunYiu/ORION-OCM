# Applicability control — **RETRACTED AS DEPLOYABLE; stands as a calibration ceiling**

> **Leak found by this lane's own audit.** The "v2 mechanism-derived" features below are
> `tile_tokens(canonical_program)` and `baseline_first_index` — properties of the
> **solution**, not the task. Fitting on validation is legitimate (those targets are solved
> history), but *applying* the rule to an unsolved protected target reads its answer. The
> v2 rows are therefore an **oracle-feature ceiling**, not a deployable gate, and the same
> applies to the 670-target LUNARC result and the fit-size sweep, which used them.
>
> The deployable gate is **v1 (observable features)**, which lost to always-serve on two of
> three ecologies. Status: **applicability control 🟢 → 🟡**. The tool now refuses
> answer-derived features unless `--features oracle` is passed explicitly and labels every
> output with its feature mode. Revival launched: a **probe gate** — the "feature" is a
> charged action (run the guided stream alone for β slots; hit → done, miss → RESET),
> observable by construction.
>
> Invariant added to the lane: **a deployment predicate may read the task statement and
> the outcomes of charged actions, never the solution.**


#357 named applicability the missing link: an oracle takes 12/40 → 36/40, while retrieval
timing alone is *exactly* null. This lane's evidence agreed from the other side — the
registered rule is **all-or-nothing**, so one veto-prone target refuses a library that
helps the majority, and OCM then forfeits everything (0 wins / 19 worlds,
[PARENT_REGRET.md](PARENT_REGRET.md)).

The missing object is per-**target** deployment rather than per-**library** admission:

```text
A_a(z) = P( the library helps here | observable context z )
serve iff A_a(z(T)) predicts a positive delta
```

Implemented as an explicit decision list over internally computable features — the first
rung of #71's mandatory parent order. No learned router, no neural component,
`src/ocm/learning/methods.py` untouched. The rule is fitted on the **validation stream
only**; protected targets are never seen during fitting. Correctness is untouched: every
success is still externally verified, and a wrong decision costs at most the bounded 2×
([P1](P1_BOUNDED_REGRET.md)).

## The feature set is the whole result

**v1 — generic surface features** (degree, support, coefficient magnitude): *lost* to
simply always serving on two of three ecologies.

**v2 — mechanism-derived features**: the mechanism says the guided stream wins iff it
reaches the target's composition before the baseline index `b`, so the predictors are

- **tiling token count** — how few library fragments exactly tile the canonical program
  (guided position grows like `T^tokens`, so this dominates);
- **baseline-index band** — the budget the guided stream has to beat.

Both computable without solving the target: tiling is a string match, `b` is a property of
the target's position in the declared enumeration.

| ecology | features | RESET | ALWAYS_SERVE (parent) | **APPLICABILITY** | ORACLE | vs parent |
|---|---|---|---|---|---|---|
| FOREIGN_M1 | v1 surface | 29 387 | **19 992** | 22 558 | 11 965 | +12.8 % ✗ |
| **FOREIGN_M1** | **v2 mechanism** | 29 387 | 19 992 | **13 596** | 11 965 | **−32.0 %** ✓ |
| E7 | v1 surface | 62 935 | **58 636** | 62 788 | 32 731 | +7.1 % ✗ |
| **E7** | **v2 mechanism** | 62 935 | 58 636 | **39 296** | 32 731 | **−33.0 %** ✓ |
| **FV6** (foreign vocabulary) | v1 surface | 3 725 | 4 553 | **3 205** | 2 857 | **−29.6 %** ✓ |
| **FV8** (foreign vocabulary, length 8, 120 targets) | **v2 mechanism** | 56 056 | 81 800 | **50 261** | 47 669 | **−38.6 %** ✓ |

On `FOREIGN_M1` the v2 gate recovers **86 %** of the oracle's advantage (13 596 against an
oracle floor of 11 965) and serves on 60 % of targets.

## Two things this establishes

**Applicability control is a genuine OCM-specific advantage.** It beats the ungated
adaptive parent by 29–39 % on four ecologies, two of them built from the M1 lane's own
vocabulary. On FV8 the library is **harmful** when always served (+46 % over RESET) and
the gate still beats RESET by 10 % — recovering 69 % of the oracle gap by serving on only
26.7 % of targets. The parent serves unconditionally and is
structurally unable to do otherwise, so this is not a configuration artifact — it is the
second win of this kind after [deployment liveness](PLASTICITY.md), and both come from the
same source: separating *is this true* from *is this useful here*.

**It pays exactly when the library's value is heterogeneous.** On FV6 the library is
harmful **on average** (parent 4 553 vs RESET 3 725) yet serving selectively on 31.7 % of
targets beats both. Where the library is uniformly good, always-serve wins and gating only
costs — which is why the v1 surface features lost, and why the honest reading is
conditional rather than universal.

## The transferable lesson

The same correction landed twice in two subsystems this session: [RSI-1](rsi/RSI1_RESULT.md)
found its diagnoser uncalibrated because its likelihoods were **guessed**, and localised
composability as the informative probe; applicability v1 lost because its features were
**guessed** from surface intuition. Both were fixed by deriving from the mechanism.

> Features and likelihoods derived from the mechanism beat features and likelihoods
> derived from intuition — and the failure is not visible until a control that can lose
> is run.

## Claim ceiling

Three ecologies, one decision-list family, fitted per-ecology on its own validation
stream. **Not** established: transfer of a *fitted rule* across ecologies, optimality of
the feature set, or that it closes the remaining 14 % gap to the oracle.
