# RV-377-122 — FREEZE: experimental verification of theorem TI-1 by channel ablation

Frozen BEFORE the full run. **A pilot on one world was run first and is disclosed in §3
below**, so the predictions here are frozen over the remaining 21 worlds.

## Why this is the predictive experiment

`RV-377-121` established that K4's selection principle cannot be predictive: cross-seed
agreement is **0.0 %** at 20 000, 100 000 and 500 000 evaluations, so "the cost-minimal
architecture" does not name an object.

Theorem **TI-1** (Codex lane, merged) does not have that defect. It constrains **information
channels**, not mechanisms:

```
Y = F(P, D, Q, A, R)       with   I(W;P) = 0,   R independent of W
⇒  a realization with no development, no informative query and no informative authority
   succeeds with probability at most 1/M on a uniform M-world exact-identification obligation
```

Three properties make this the right object:

1. **It is predictive** — a quantitative ceiling derivable before any run.
2. **It applies to UNSEEN forms.** It bounds *any* machine `F`, including architectures nobody
   has built, because it constrains what information can reach the answer rather than how the
   answer is computed. A machine class defined by its **channel signature** is a form of
   machine intelligence the theory defines rather than inherits from history.
3. **It does not require the search to converge**, so `RV-377-121` does not touch it.

It has been verified **combinatorially** (`GMI_TARGET_INFORMATION_EXACT_RECEIPT_V1.json`
checks the arithmetic on finite cells) and **never against real machines on real worlds**.
That is the gap this closes.

## Method

For each of the 22 `gmi_k4d_worlds` obligations, one **generic exemplar machine** — nearest
development exemplar by token mismatch — is run under four channel conditions. The machine is
**identical** across arms; only the channels change:

| arm | development | query |
|---|---|---|
| `FULL` | this world's | this world's |
| `NO_DEV` | reminted from an **independent** world of the same shape | this world's |
| `NO_QUERY` | this world's | shuffled against their answers |
| `NEITHER` | independent | shuffled |

The exemplar machine is deliberately the **strongest generic `D+Q` mechanism** available, so a
collapse under ablation cannot be dismissed as a weak learner.

**This is simultaneously a capability test and a leak detector.** A world where `NO_DEV` does
*not* collapse to the chance floor is leaking the protected variable `W` through a channel its
own `target_information_source` declaration does not name.

## 3. Disclosed pilot — one world, run before these predictions were written

`K4-A01` was run to check the harness. It is reported here rather than folded into the
results, and `K4-A01` is **excluded from the prediction counts below**:

```
K4-A01   entropy 6.966 bits   M = 125   chance floor 1/M = 0.008
  FULL 0.5000   NO_DEV 0.3125   NO_QUERY 0.1250   NEITHER 0.1250
```

`NO_DEV = 0.3125` against a floor of `0.008` is **39× the TI-1 bound**. On this world, a
machine whose development came from an entirely different world still answers a third of the
protected queries. Either the bound is wrong or `K4-A01` leaks `W` through `Q`. The bound is a
theorem, so the world leaks — and its declared source is `["DEVELOPMENT","QUERY"]`, which does
name `QUERY`, so the leak may be declared rather than hidden. Distinguishing "declared and
legitimate" from "undeclared leak" is what the full run is for.

## Frozen predictions (over the 21 worlds excluding `K4-A01`)

| id | prediction | falsifier |
|----|-----------|-----------|
| P1 | `FULL` exceeds 0.50 on **≥ 8** of 21 worlds — the generic machine really does learn from development. | < 8 |
| P2 | **`NO_DEV` exceeds its world's `1/M` floor on ≥ 15 of 21 worlds.** Given the pilot, I expect leakage to be the norm, not the exception. | < 15 |
| P3 | **At least 3 worlds show `NO_DEV` ≥ 0.25** — i.e. gross leakage, not marginal. | < 3 |
| P4 | The mean gap `FULL − NO_DEV` exceeds **0.20** — development still contributes real capability even where `Q` leaks. | ≤ 0.20 |
| P5 | **`NEITHER` ≤ `NO_DEV` on every world.** Removing a second channel cannot help. A violation means the harness is measuring noise, not information. | any world where `NEITHER > NO_DEV` |

P2 and P3 are predictions **against the new instrument**, on the base rate of this programme:
two registered instruments were found defective today (`DG-13`: a 50 % leaking intervention and
an ecology that is the identity function). Predicting that a third set of instruments is clean
would be naive.

P5 is the **sanity gate**. If it fails, no number from this run is readable and the harness is
repaired before anything is claimed.

## What a confirmation would and would not license

Confirming P1–P5 would establish that **TI-1's capability ceiling is measurable on real
machines and real worlds**, and that channel ablation is a working instrument for detecting
where protected information actually enters.

It would **not** establish that any particular unseen form achieves a particular capability.
That requires the next step: name a channel signature, derive its ceiling from TI-1/TI-2, build
a machine in that class, and check the measured capability against the derived number on a
world whose `M` is known. That experiment is registered and **not** claimed here.
