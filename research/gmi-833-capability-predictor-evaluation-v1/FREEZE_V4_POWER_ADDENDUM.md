# FREEZE_V4_POWER_ADDENDUM — power revival of the held-out rows

Committed **before the `SIGMA_SYN2` / `SIGMA_ARCH2` outcomes were computed**.
Every earlier freeze document, universe module and frozen prediction file is left
byte-identical.

## 1. The defect, found prediction-side

On `SIGMA_SYN` and `SIGMA_ARCH` every point `F` emits takes one of exactly two
degenerate values: `UNSATISFIED` (936 of 1,534 identified inputs per threshold on
`SIGMA_SYN`) or `0` (598). The soundness census over those points is true — 0
violations on 45,800 and 121,920 pairs — but it is weak evidence, because a
predictor that only ever identifies a degenerate value is barely being asked a
question.

This is a **power defect in the registered universe/grid, not a prediction miss**,
and it is visible entirely prediction-side: the point-value census is a function of
`F`'s emissions alone and consults no outcome oracle. Diagnosing and fixing it
before freezing V4 is therefore legitimate; after this freeze it is fixed.

## 2. Single-stage attribution and the lever

The failing stage is the **observation coordinate**. `obs = (1+w, m mod 2)` cannot
pin a survivor set down to machines that share a *nonzero* capability, so every
non-degenerate image is multi-valued and `F` correctly abstains — the abstention was
right, the instrument was blunt.

Lever: a finer registered observation `obs = (1+w, m mod 2, h mod 4)`, with three
registered observation values chosen so that a survivor set can consist entirely of
machines solving the same task.

## 3. New machines, so the outcomes are new

`SIGMA_SYN2` (128 machines) adds a `g` gate on head 2; `SIGMA_ARCH2` (160 machines)
adds the parameters `FF 3`, `REC 6` and `CTR 3`. No machine of either population had
its capability measured before this commit. Both are disjoint from all six earlier
populations (`rho[3] = 12/13` and `14/15` versus `0`, `{1,2}`, `{3,4}`, `{5,6}`,
`{7,8}`, `{9,10}`), with 0 descriptor collisions on every pairwise comparison.

## 4. What this freeze can and cannot claim about custody

It **can** claim: the predictions below were committed before their outcomes were
computed, and `git log` proves it.

It **cannot** claim what `FREEZE_V1.md` claims — that no outcome oracle existed. The
external evaluator was written for the V1 freeze and is reused unchanged. That is a
strength of a different kind: the simulator was not written with these machines in
mind, and the closed-form registered law for the new parameters must agree with it.
The distinction is stated here rather than blurred.

## 5. Frozen figures

| | `SIGMA_SYN2` | `SIGMA_ARCH2` |
|---|---:|---:|
| machines | 128 | 160 |
| grid | 51,840 | 51,840 |
| point emissions | 7,200 | 9,488 |
| **non-degenerate points** | **3,872** | **2,400** |
| distinct non-degenerate values | 4/11, 5/11, 9/11 | 4/13, 7/13, 11/13 |
| abstentions | 3,552 | 6,640 |
| inconsistent | 41,088 | 35,712 |
| stream sha256 | `14b8127f1e242fc2…` | `e24e90d7849d716e…` |

Every registered threshold is non-degenerate in both universes.

## 6. Falsifiers

- the closed-form capability law disagreeing with brute-force simulation on any
  machine of either new population;
- any point emission differing from the externally evaluated capability of a
  consistent realization — now testable on 6,272 non-degenerate emissions rather
  than on degenerate ones only;
- a replayed stream whose sha256 differs from the two pinned above.
