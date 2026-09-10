# Alignment to the U0–U10 ultimate-goal ladder

Where this lane's measured evidence actually places OCM, including one correction to a
more optimistic reading.

## Correction: U2 is scoped far more narrowly than #356's headline suggests

#356 is cited as evidence for **U2 Development** — "previous experience makes later new
cognition easier". The mechanism is real, but
[HOSTILE_REVIEW_356.md](HOSTILE_REVIEW_356.md) measured its reach:

> **96 of 100** protected targets across E5/E6/E8 are **one motif substitution** from a
> training target; part coverage **1.00**; ~70–77 % of each target's program is a
> contiguous substring of a training program.

So U2 is established as **D1 (reusable objects) at generalisation distance d = 1**, with
the search-order change as its mechanism. `LIBRARY_ONLY ≡ RESET` and the shuffled control
still rule out whole-answer retrieval, and the effect is causal — but "history makes new
cognition easier" currently means **"one substitution from something already solved."**
Distance was never a registered variable, so every prior number is a point estimate at
the most favourable point of an undeclared axis.

**U2 should read 🟡 scoped-at-d=1, not 🟢**, until the matched d=1/d=2 comparison lands.

## Convergence: the λ(z) allocation proposal already has a measured guarantee

The proposal to replace the fixed 50/50 alternation with an applicability-conditioned
allocation `λ(z)`, retaining `ε > 0` for guaranteed primitive fallback and bounding

```text
B_max ≤ ceil(b / ε)
```

is **exactly the regime this lane just measured**. The registered solver *is* the
`ε = 1/2` special case, and [P1_BOUNDED_REGRET.md](P1_BOUNDED_REGRET.md) discharges the
bound empirically at that point:

| | |
|---|---|
| predicted bound at `ε = 1/2` | `B_max ≤ 2b` |
| **max observed ratio**, 410 measurements, 5 adversarial libraries | **2.0000** |
| violations | **0** |
| correctness violations | **0** |

The bound is **attained and never exceeded**, so it is tight rather than loose. That
gives the λ(z) design a measured anchor: the safety argument does not depend on the
allocation being 50/50, only on `ε` being bounded away from zero, and the cost of a
useless learned stream is exactly `1/ε`.

It also supplies the argument for the admission change: since the downside is bounded and
benign at any `ε`, universal non-inferiority is a **dominated policy**, not a safety
property — measured here as 0 wins / 6 ties / 12 losses against the ungated parent, mean
regret +16 506 slots, gate protective in **0 of 19** worlds.

## Convergence: "learn utility, not frequency" is already visible in the data

`learn_generator` selects the top-16 fragments by support **frequency**. The dose-response
shows the predicted pathology directly — benefit is **non-monotone in developmental
depth**, peaking then declining as generic high-support fragments dilute the motifs:

| ecology | peak depth | below the peak |
|---|---|---|
| E6 | 6 | refused at 3–4 |
| E1 | 32 | rises 21.9 → 72.2 % |
| E5 | 35 | **−14.4 %** at depth 6 |
| E8 | 66 | **−82.8 %** at 20 |

Below the recovery threshold an incomplete library is **actively harmful**. So utility-
rather than frequency-based admission is not a refinement; it is the difference between a
prior that helps and one that costs up to 82.8 % extra work.

## U3 is the right next rung, and the parent already owns most of it

#357 measures `STRONG_ADAPTIVE_PARENT` at **+2.794** against `APPL_ORACLE` **+2.902** — a
plain class→fragment decision list recovers ~96 % of the applicability advantage. This
lane's independent evidence agrees: `ORDINARY_ADAPTIVE_PARENT` is identical to
`CONTINUED` wherever OCM admits and strictly better wherever it refuses.

**Assimilate rather than out-invent.** `PARENT_EQUIVALENT` should be an acceptable green
terminal for U3, with OCM's contribution being warrant, provenance, revocation and
deployment lifecycle *around* a parent-owned applicability mechanism.

That contribution is now demonstrated: under an ecology shift, deployment liveness makes
OCM **27 % cheaper than the static parent over a lifetime and 49 % cheaper in the shifted
regime** — the first OCM win over the strongest parent in this programme. Caveat recorded:
the **reactivation** half of the lifecycle never fired.

## The self-diagnosis experiment is well-posed, and its ground truth already exists

Hiding the diagnosis and requiring the self-model to conclude *applicability* from M1's
receipts is the right breakthrough experiment, because #357 has already established the
answer experimentally — applicability dominant, retrieval timing **exactly null**,
integration secondary. That is an unusually clean natural-failure ground truth.

Two design constraints this lane's failures suggest:

1. **The organism cannot use evaluator-side facts.** The admission law
   (`recovered == all motifs ⟺ admitted`) is computed from the hidden motif set and is a
   *diagnostic* law, not an executable rule. Self-diagnosis needs the internally
   computable coverage estimate `Ĉ_t` with `UNKNOWN` distinct from `complete`.
2. **Register the prediction before the run and report it when it fails.** Two registered
   predictions in this lane were falsified (E3's zero-veto prediction; E6's 100 %-veto
   prediction), and each falsification produced more theory than the successes did.

## Ladder position on this lane's evidence

| rung | this lane's reading |
|---|---|
| U0 substrate | 🟢 unchanged |
| U1 learning | 🟢 |
| U2 development | 🟡 **D1 at d = 1**; d ≥ 2 untested, d ≥ 3 not expressible in this grammar |
| U3 conditional cognition | 🟡 parent-owned; OCM adds lifecycle, now measured |
| U4 self-understanding | 🟡 `Ĉ_t` missing — the law is evaluator-side |
| U5 self-repair | 🟡 ground truth now exists (#357); loop not closed |
| U6–U10 | 🔴 — and d ≥ 3 being **empty by counting** in a 4-primitive length-8 grammar is a concrete obstruction to U6/U10, not a resourcing problem |
