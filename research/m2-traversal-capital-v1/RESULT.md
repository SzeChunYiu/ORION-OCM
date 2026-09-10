# M2 traversal-capital probes — RESULT

Pre-freeze measurement for the `DEV-CAL-1` / M1 successor (#323 §5, §6).
Not a scored run; no claim is promoted. Read [CORE.md](CORE.md) first.

## Assay integrity first

The declared grammar is total and small: `sum(4^L, L=0..8) = 87 381` programs over
`("inc","dec","double","square")`, reaching `20 321` distinct normal forms. So
`B_slots` under any enumeration order is an exact lookup.

Two independent controls fired clean **before** any finding was read:

- `min_primitive_length` recomputed from our own enumeration matches the frozen
  `M1_PARTITIONS_V1.json` on **all 288** train+protected rows — zero mismatches.
- The closed-form model reproduces the **committed M1 scored endpoints exactly**:
  RESET/baseline `12/40`, `KNOWN_STRUCTURE_ORACLE` `18/40`.

Reproducing a scored run's endpoints from a closed form is the strongest available
evidence that the model is measuring the same object the harness measured.

<a id="m2-n1"></a>
## M2-N1 `ORACLE_ADVANTAGE_IS_A_CONSTANT_OFFSET`

Of the 8 protected acquisition targets, **7 have `min_primitive_length = 8`**, the
grammar maximum. `methods.solve` enumerates ascending in length, so it pays for all
`1+4+16+64+256+1024+4096+16384 = 21 845` shorter programs first. `oracle_solve`
prunes to the declared length and skips exactly those.

Every oracle saving on a length-8 target is therefore exactly 21 845 slots:

| target | `B` baseline | `B` oracle | delta |
|---|---|---|---|
| `DEG_0_1:SUP_LE2:...:0` | 61 408 | 39 563 | 21 845 |
| `...:1` | 65 280 | 43 435 | 21 845 |
| `...:2` | 65 536 | 43 691 | 21 845 |
| `...:3` | 65 279 | 43 434 | 21 845 |
| `...:5` | 61 440 | 39 595 | 21 845 |
| `...:6` | 65 278 | 43 433 | 21 845 |
| `...:7` | 64 496 | 42 651 | 21 845 |
| `...:4` (true length 6) | 4 088 | 2 723 | 1 365 |

A **constant** predictor that always answers "8" — no features, no history, no
developmental state — reaches ladder `17/18` of the oracle's advantage. A
history-free `DESC` reordering (length 8 first) reaches `15`. Baseline is `12`.

So **94 % of the measured "structural headroom" is a baseline enumeration-order
mismatch**, not transferable structure.

<a id="m2-n2"></a>
## M2-N2 `STRUCTURE_PREDICTABLE_WITHOUT_HISTORY`

The advisor-mandated control. The same explicit modal-length rule was fit twice per
feature set: once on the **dev-phase traversal only** (what history could carry) and
once on the **full reachable ecology** (grammar only, zero developmental outcomes).

Across six feature sets spanning 1 to 1 056 cells, the two fits are
indistinguishable:

| feature set | cells | dev-fit acc | free-fit acc |
|---|---|---|---|
| `FS0_constant` | 1 | 0.444 | 0.444 |
| `FS1_frozen_band` | 18 | 0.486 | 0.486 |
| `FS2_frozen_fine` | 116 | 0.493 | 0.493 |
| `FS3_squares` | 8 | 0.444 | 0.444 |
| `FS4_sq_mag` | 280 | 0.542 | 0.535 |
| `FS5_sq_mag_sup` | 1 056 | 0.583 | 0.576 |

(protected n=144; the full-ecology scope shows the same pattern, free-fit marginally
**ahead** at 0.699 vs 0.698.)

Developmental history contributes no incremental structural information. The
`P_shuffled` control collapses onto `P_constant` exactly, as it must.

There is a mechanism behind this and it is worth stating plainly: the dev phase
enumerated **87 234 of 87 381 slots** while solving its 144 training targets,
observing **20 245 of 20 321 (99.6 %)** distinct normal forms at zero marginal
search cost — and retained 144 solutions plus 16 fragments. The traversal was
discarded. But recovering it would not have helped, because the agent is handed the
complete generative grammar, so every regularity in that traversal is derivable
a priori. **Where the grammar is given, there is no structural prior left to learn.**

<a id="m2-n3"></a>
## M2-N3 `HEADROOM_NOT_SURFACE_IDENTIFIABLE`

At the honest 144-row scope the oracle gap is real and large — baseline ladder 339
vs oracle 443, mean `B` 33 807 vs 22 347 — but **no predictor reaches it**:

| arm | mean `B` | ladder |
|---|---|---|
| ASC baseline | 33 807.5 | 339 |
| best explicit predictor (`FS5`, dev-fit, prune) | 30 156.7 | 344 |
| `KNOWN_STRUCTURE_ORACLE` (true length) | 22 347.0 | 443 |

The best of 1 056 cells captures **5 of the 104-point gap (4.8 %)**, and the free-fit
upper bound does no better. Most predictors score *below* the plain baseline, because
a wrong hard-prune deletes the answer from the space entirely — the value function is
a cliff, not a gradient (`FS1` prune loses 17 of 144 targets outright).

`min_primitive_length` is the length of the *shortest* program for a normal form. It
is of course determined **by** the normal form; what the probes measure is that it is
**not identifiable from the frozen semantic coordinates, nor from four richer explicit
coordinate families** — including the population-optimal (free-fit) rule over 1 056
cells. Motivating intuition, not the claim: shortest-program length is a
grammar-relative Kolmogorov quantity, and such quantities are generically not
recoverable from coarse surface statistics.

**Therefore `KNOWN_STRUCTURE_ORACLE` does not behave as an abstraction oracle at this
scope.** What it supplies is an answer-adjacent fact that none of the tested
coordinate families recovers. Using it as the headroom calibration therefore
**overstates** transferable headroom, and any future "developmental" positive measured
against it would be uninterpretable.

<a id="m2-n4"></a>
## M2-N4 `BASELINE_ENUMERATION_ORDER_IS_MISCALIBRATED` (deliverable, not just diagnosis)

`methods.solve` enumerates ascending in length while **68.1 % of the reachable ecology
(13 846 / 20 321 normal forms) sits at the maximum length 8**. The baseline therefore
pays a large fixed toll before reaching where most answers live. This is a free,
history-free property of the search order, and naming it is what turns M2-N1 from an
observation into a closed defect.

The correction is **not** blanket `DESC`, and the asymmetry is the interesting part:

| scope | ASC baseline ladder | `DESC` ladder |
|---|---|---|
| acquisition targets (n=8) | 12 | **15** |
| protected (n=144) | **339** | 219 |
| full ecology (n=20 321) | **41 122** | 37 960 |

`DESC` wins on the 8-target slice and loses badly on that slice's own parent
distribution. So the M1 protected slice is **unrepresentative of the ecology it is
drawn from** — 7/8 at max length against a 68 % base rate — and any arm tuned on it
inherits that skew. The defensible form of the fix is order-by-predicted-density over
the length distribution, not a fixed direction.

No change is made to `src/ocm/` here. This is registered as a measured finding for the
successor freeze; the runtime selection policy is untouched (#71 respected).

## What this does and does not say

Does say, at this scope: the M1 `NO_NATIVE_EFFECT` terminal stands, and its companion
headroom reading does not. The four byte-identical M1 arms (RESET, `LIBRARY_ONLY`,
`CONTINUED`, `CONTINUED_WITH_LEARNING_STATE_REMOVED`, all `12/40` at mean `B`
26 395.7) mean history never entered search at all; that is a statement about the
admission gate, not about development.

Does **not** say: that OCM cannot develop; that history is worthless; anything about
scopes beyond this frozen length-8 polynomial ecology. `CANNOT_CHECK` is preserved
where it applies — the residual 95 % of the 144-row oracle gap is **not attributed**.

## Consequence for #323

`DEV-CAL-1`'s critical cell — *different surface + same latent structure* — cannot be
tested on an ecology whose generative grammar is handed to the agent, because the
optimal structural prior is then derivable a priori and history is redundant by
construction. This is the `NO_TRANSFERABLE_HEADROOM` branch of #323 §5, reached for a
sharper reason than "the oracle cannot help": the oracle helps, but what it supplies
is neither structural nor learnable.

The constructive requirement that follows is registered separately: an ecology whose
**latent family structure is not derivable from the declared grammar**, so that
history is the only available source of the prior. See
[HIDDEN_FAMILY_DESIGN.md](HIDDEN_FAMILY_DESIGN.md).
