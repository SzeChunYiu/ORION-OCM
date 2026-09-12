# RV-377-118 — FREEZE: the distributed batch (Billy, old, LUNARC)

Frozen BEFORE any unit runs. `gmi_work.py run` refuses any unit with `frozen: false`, so this
record is what makes the batch executable at all.

Three machines are available beyond this container: **laptop billy**, **laptop old**, and
**LUNARC** (SLURM, account `lu2026-2-51`, partition `lu48`).

## Why these units, given where the theory stands

`RV-377-107`/`109` established that the K4 predictive claim fails **structurally** — 0 of 264,
invariant under 10× budget, discrepancy widening with compute. `RV-377-113` established the
one surviving positive — `G15` step (ii) — but as a **point claim**: one seed, one column, one
budget.

The distributed batch attacks exactly those two facts, and nothing else.

### Lane A — LUNARC: the protected K4 run (`hpc`)

The 264-task array at the frozen `green_rule` budget of ≥ 10⁶ scored candidates, gated on the
one-shot public beacon (`GMI_K4_NULL_AWARE_SUCCESSOR_FREEZE_V5.json`, drand quicknet, first
round ≥ 900 s after the freeze commit, `no_reroll: true`).

This is the only run that can discharge `RV-377-107`'s **Q4** — the frozen prediction that the
protected run reproduces the development verdicts. Development scope has now been tested at
20 000 and 200 000 with **zero** cells moving; 10⁶ is the registered bar.

> **Prediction A1 (already frozen as Q4, restated):** the protected run reproduces
> `THEORY_RED` / `THEORY_RED_NULL_DOMINATES` / `INCONCLUSIVE_GRAMMAR` on the same cells, and
> **0 of 264** recover the target vector.
>
> **Prediction A2:** the grammar axis remains verdict-inert — 88/88 agreement (DG-11).

If A1 is falsified at 10⁶, the structural reading of F1 is wrong and the predictive part is
budget-bound after all. That would be the single most important falsification available to
this programme, and it is why the run is worth a cluster.

### Lane B — laptop billy: multi-seed replication of `G15` step (ii) (`medium`)

`RV-377-113`'s witness is one seed. A point claim cannot support a rate, and `RV-377-108`
showed the corpus has repeatedly mistaken one for the other.

Nine independent seeds of the B1 neutral search on `E_sym5`, each scored under **all six**
registered interventions and against the best constant (0.7917) in fx units.

> **Prediction B1:** the `DENSE` carrier is recovered and clears rule 36 on **≥ 3 of 9** seeds.
> The witness at seed 0 has a margin of only 1.500 fx units, so seed sensitivity is expected.
>
> **Prediction B2:** `half_events` is the binding intervention on the majority of recovered
> seeds (`GMI-DA9`, corroborated by `RV-377-111` at 11/11).
>
> **Prediction B3:** at least one seed recovers `DENSE` under `standard` but **fails** rule 36
> — i.e. the single-intervention reading over-reports, as it has every previous time.

B1 is the prediction that converts the corpus's one positive into a rate, or removes it. If
`DENSE` clears on 0 of 9, `RV-377-113` was a lucky seed and `G15_STEP_TWO_REACHED` must be
withdrawn to `REACHED_AT_ONE_SEED_ONLY`.

### Lane C — laptop old: the CP1 ablation extension (`medium`)

`RV-377-113` recorded a scope reduction: the leave-one-out primitive ablation was cut from 4
ecologies to `E_wit1` alone, because the measured cost was 6.8× the linear projection. The
other three ecologies were declared **owed, not claimed**.

33 kinds × 3 ecologies (`E_smooth1`, `E_smooth3`, `E_sym5`) = **99 units**.

> **Prediction C1:** the irreducible set differs between ecologies — at least one kind is
> IRREDUCIBLE on one ecology and REDUCIBLE on another. If so, "the minimal axiom set" is not
> a single set and CP1's question is ill-posed as asked.
>
> **Prediction C2 (restating `RV-377-110` T3 at the wider scope):** fewer than 10 of 33 kinds
> are irreducible on **every** ecology.

### Lane D — either laptop: DG-12 completion (`tiny`)

The degeneracy audit covered 16 obligations and left **12 modules** unaudited, listed by name.
Cheap, and it closes a gap that is currently open only for want of running it.

> **Prediction D1:** at least one further degenerate or near-degenerate obligation is found
> among the 12. `e1_scdi` regime B was degenerate on 57.7 % of its coefficient space, and
> nothing suggests it is unique.

## Discipline that applies to every unit

* Every receipt path carries `{HOST}`. Host-keying prevents corruption; claims only prevent
  wasted work. A receipt collision has already destroyed two committed receipts in this
  programme.
* `name_key` is popped before any freeze reaches any engine.
* No unit may be marked `done` without its receipt committed.
* Development results are **never** protected evidence; only the beacon-gated LUNARC run is.
* Rule 36, 40, 42 and 45 apply to every adjudication: all six interventions, the best-constant
  control in fx units, both nulls, and a non-degenerate obligation.

## What this batch cannot do

It cannot close DG-13 (two registered instruments are defective and repairing them re-points
historical claims), cannot supply independence (IG-4 and IG-5 remain PENDING — same-author
evaluator, meter and primitives), and cannot address CP6 hostile transfer, which needs
architecture families outside the corpus and is not in this batch.
