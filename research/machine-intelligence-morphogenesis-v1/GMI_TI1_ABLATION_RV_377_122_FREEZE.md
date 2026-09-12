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

---

# RV-377-122 — ADJUDICATION: the sanity gate failed, so no capability number is claimed

22 worlds, 0 errors.

## P5 — the sanity gate — FAILED

| id | prediction | outcome |
|----|-----------|---------|
| **P5** | `NEITHER ≤ NO_DEV` on every world | **FALSIFIED** — violated on `K4-A03` (0.250 > 0.125) and `K4-A11` (0.100 > 0.000) |
| P1 | `FULL > 0.50` on ≥ 8 of 21 | 5/21 — **not read** |
| P2 | `NO_DEV > 1/M` on ≥ 15 of 21 | 7/21 — **not read** |
| P3 | `NO_DEV ≥ 0.25` on ≥ 3 | 6/21 — **not read** |
| P4 | mean gap > 0.20 | 0.054 — **not read** |

The freeze said, before the run:

> *"P5 is the **sanity gate**. If it fails, no number from this run is readable and the harness
> is repaired before anything is claimed."*

It failed. Removing a **second** channel cannot increase the information available, so a world
where `NEITHER > NO_DEV` is reporting sampling noise, not information. **P1–P4 are recorded as
measured and explicitly not claimed.** TI-1 is neither confirmed nor challenged by this run.

## Why the harness is inadequate — diagnosed, not guessed

Two independent defects, both mine:

**1. The generic machine cannot read most of these worlds.** `FULL = 0.000` on **10 of 22**
worlds. Where the machine scores zero with full access, ablating its channels tells you
nothing — 0 versus 0 is not a collapse. The answer-extraction heuristic
(`for k in ("y","answer","expected","out","label","x")`) is a guess at heterogeneous world
shapes and is simply wrong for most of them. A per-world adapter is required.

**2. The query counts are far too small for the resolution claimed.** Worlds carry 10–28
protected queries, so one query is 4–10 percentage points. Both P5 violations are a **single
query** (`K4-A11`: 0.100 vs 0.000 on n=10). The differences I was scoring are at or below the
noise floor of the measurement.

## A real finding the run did expose — four degenerate worlds

Four of the 22 worlds have `entropy_bits_lower_bound = 0.00`, i.e. **M = 1**:

```
K4-A05, K4-A06, K4-A14, K4-A17     M = 1,  chance floor 1/M = 1.000
```

TI-1's own text names this case:

> *"a benchmark that grants such a fixed realization perfect semantic score has leaked
> protected target information **or has defined a degenerate one-world obligation**."*

A one-world obligation has nothing to identify. `K4-A05` and `K4-A17` duly score `FULL = 1.000`
and `NEITHER = 1.000` — a machine with every channel destroyed still scores perfectly, because
there is only one possible world.

This is **DG-12 applied to the successor instrument**: the degeneracy audit that found
`e1_scdi` regime B constant now finds four constant obligations in the new world set, before
any result was built on them. Reported to the Codex lane's design rather than worked around.

> **`K4D_WORLDS_NON_DEGENERATE` = FALSE — 4 of 22 have M = 1.**

## Registered repairs, not claimed

1. **Per-world answer adapters**, so the machine reads each obligation's actual structure.
   Success criterion: `FULL` substantially above zero on the worlds that are not degenerate.
2. **Raise the query count** until one query is worth well under one percentage point —
   at least a few hundred protected queries per world.
3. **Repair or retire the four `M = 1` worlds.** A one-world obligation cannot test
   acquisition.
4. Re-run P1–P5 only after 1–3. **TI-1 remains experimentally untested against real machines.**

## Status

`TI_1_EXPERIMENTALLY_VERIFIED_ON_REAL_MACHINES` = **FALSE — instrument not yet adequate.**

The theorem itself is untouched: it is proved, and verified combinatorially. What failed here
is my apparatus for measuring it, and it failed a gate I set for exactly this purpose before
looking at any result.
