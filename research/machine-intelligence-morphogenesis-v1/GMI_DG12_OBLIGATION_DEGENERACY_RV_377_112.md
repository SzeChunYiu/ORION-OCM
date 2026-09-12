# RV-377-112 — DG-12: is the OBLIGATION itself a constant?

Opened by the DG-9 E1/E3 audit. Executed and recorded here.

## The question rule 40 does not ask

Rule 40 asks whether a **constant answer** can clear θ on an ecology, and classifies the
ecology `NON_DISCRIMINATING` if it can. That is one level too shallow.

The DG-9 audit found `e1_scdi`'s boolean serving regime `B` returning the answer `1` on
**all 24** of its registered evaluation queries. The obligation is not merely easy for a
constant — it **is** a constant. A row scoring 1.0000 there has demonstrated nothing
whatsoever, and no capability number computed on it carries any information at all.

Rule 40's control would catch this only incidentally, through a best constant sitting at
the ceiling, and only where a best constant was computed. Nothing in the corpus has ever
asked the question directly.

> **DG-12.** Before any obligation is used to certify anything, it must be shown to take
> more than one value over its own declared evaluation set. An obligation with one
> distinct answer is `DEGENERATE` and every verdict taken on it is void — not weakened,
> void, because a constant emitter scores perfectly.

## Verification of the DG-9 headline, done independently

At `e1_scdi`'s registered coefficients `[(4,8), (12,16), (4,8), (12,16)]`, over
`e1_vlc.EVAL_QUERIES` (24 queries, scopes `(0,1) (0,2) (0,3) (1,2) (1,3) (2,3)`):

| regime | distinct answers | counts | best-constant agreement | |
|---|---|---|---|---|
| A | 5 | `{40:10, 16:6, 24:4, 32:3, 56:1}` | 0.4167 | NON_DEGENERATE |
| **B** | **1** | **`{1: 24}`** | **1.0000** | **DEGENERATE** |
| C | 2 | `{1:13, 0:11}` | 0.5417 | NON_DEGENERATE |
| D | 5 | `{10:10, 4:6, 6:4, 8:3, 14:1}` | 0.4167 | NON_DEGENERATE |

Confirmed exactly as the DG-9 worker reported.

## The degeneracy is structural, not a quirk of the registered point

Sweeping the **entire** coefficient space (`COEFF_VALUES = [4,8,12,16]`, 4 factors × 2
coefficients = 65 536 assignments) and asking how many make each regime constant on the
whole evaluation set:

| regime | degenerate assignments | fraction |
|---|---|---|
| A | 0 / 65 536 | 0.0000 |
| **B** | **37 824 / 65 536** | **0.5771** |
| C | 73 / 65 536 | 0.0011 |
| D | 0 / 65 536 | 0.0000 |

**More than half of regime B's coefficient space is degenerate.** The mechanism is plain
once seen: `B` thresholds a *sum* of factor values against `TAU = 12`, while the factor
values are drawn from `{4, 8, 12, 16}`. Two factors summed almost always exceed 12, so
the threshold almost never separates anything. The registered point is not unlucky — it
is typical.

This also confirms the DG-9 worker's stated reason for regime C **not** joining B:
comparing two factor values to each other stays near-balanced (13/11 at the registered
point, degenerate on 0.11% of the space) exactly where comparing their *sum* to a fixed
threshold degenerates.

## Audit over the registered ecologies

| | |
|---|---|
| obligations scored | **16** |
| `NON_DEGENERATE` | **15** |
| `DEGENERATE__OBLIGATION_IS_A_CONSTANT` | **1** (`e1_scdi` regime B) |
| `NEAR_DEGENERATE` (constant agrees ≥ 85%) | 0 |

All **12** registered smooth/table obligations — the 6 ecologies of `ecology.REGISTRY`
across both declared criteria — are `NON_DEGENERATE`. The corpus's core ecology set is
clean on this axis. The damage is confined to the E1 lane, where it voided 80 verdicts
with zero residual separation.

## What this audit does NOT cover, stated rather than assumed

The audit reaches the registered `smooth`/`table` obligations and the four `e1_scdi`
serving regimes. The following obligation-bearing modules are **NOT covered** and are
listed as uncovered rather than presumed clean:

```
axis_a.py   b1x.py   b2_common.py   b2_depth.py   b2_norm.py   b2_prenorm.py
e1_cp.py    e1_iql.py   e1_lmhm.py   e1_vgsc.py   e1_vlc.py   refine_f.py
```

Extending the audit over these is registered as the next DG-12 step and is **not**
claimed. Until then, `NO_DEGENERATE_OBLIGATION_AT_REGISTERED_SCOPE` is **FALSE**: one
degenerate obligation is known and twelve modules are unaudited.

## Terminal

| terminal | value |
|---|---|
| `NO_DEGENERATE_OBLIGATION_AT_REGISTERED_SCOPE` | **FALSE** |
| `REGISTERED_SMOOTH_TABLE_OBLIGATIONS_NON_DEGENERATE` | **TRUE**, 12 of 12 |
| `DG-12_CLOSED` | **FALSE** — 12 modules unaudited |

## New protocol rule

> **Rule 45.** An obligation must be shown non-degenerate over its own declared
> evaluation set *before* any row is scored against it, and the distinct-answer count
> must appear in the receipt. A capability number computed against a constant obligation
> is not a weak result; it is not a result.

## Completion (appended 2026-09-12, RV-377-118D)

The twelve uncovered modules were audited in `RV-377-118` Lane D (`GMI_DG12_COMPLETION_RV_377_118D_FREEZE.md`,
receipts `microscopes/results/STAGE_DG12_COMPLETION_*_old.json`). D1 held: `axis_a` (`MAXV` at every T, `PARITY` at
T = 4), `e1_cp` (regime B, 21–23 of 24) and `refine_f` (its own regime E, and the re-imported regime B) carry degenerate
or near-degenerate obligations; the other eight auditable modules do not; `b2_common` has no obligation; `b1x` inherits
the registry's. `DG-12_CLOSED` → **TRUE** as an audit; `NO_DEGENERATE_OBLIGATION_AT_REGISTERED_SCOPE` stays **FALSE**.
