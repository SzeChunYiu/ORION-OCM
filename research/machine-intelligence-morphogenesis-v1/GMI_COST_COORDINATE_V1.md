# Section N measured: which cost coordinates the corpus actually meters

Date: 2026-09-15. Addresses checklist section **N** (resource and lifecycle accounting).
Witness: `gmi_microscope/cost_coordinate_audit.py`. Receipt: `microscopes/results/STAGE_COST_COORDINATE_V1.json`.

Section N lists sixteen cost coordinates every claim should meter. This measures how many of the corpus's
**462 receipts** carry each one.

## 1  Why this is measured at key level, not by grepping

The obvious method is to search receipts for words like *cost* and *charge*. A first pass did exactly that
and reported `exec` in 70% of receipts — a figure that counts the word *"executed"* in a prose note as
evidence of metered execution cost. That is the method the B1 audit already showed to be unsound.

So a coordinate counts as metered when a receipt carries a **key** naming it — `charge_resident`, `upd_e`,
`search_compute` — matched on whole key segments. **A key is a commitment by the witness; a word in a note is
not.**

## 2  Result

| coordinate | receipts metering it | |
|---|---:|---|
| revision / unlearning | 5 (1.1%) | **rare** |
| communication | 8 (1.7%) | **rare** |
| energy | 3 (0.6%) | **rare** |
| maintenance | 2 (0.4%) | **rare** |
| human / AI design input | 2 (0.4%) | **rare** |
| verification | 37 (8.0%) | |
| retrieval / index | 59 (12.8%) | |
| precision | 71 (15.4%) | |
| physical counters | 88 (19.0%) | |
| training / development | 116 (25.1%) | |
| failed-candidate | 171 (37.0%) | |
| search / discovery | 238 (51.5%) | **common** |
| update | 247 (53.5%) | **common** |
| serving / execution | 281 (60.8%) | **common** |
| memory / storage | 283 (61.3%) | **common** |
| build / acquisition | 290 (62.8%) | **common** |

**Five of sixteen are commonly metered; five are essentially never.** The corpus charges what it computes —
building, storing, serving, updating, searching — and rarely charges what it does *after*: revising,
communicating, maintaining, and the energy or human input that went in.

## 3  The audit caught two of its own patterns being wrong

**`revision/unlearning` first reported 81.3%** — the highest of any coordinate, which is what made it
obviously wrong: a corpus that charges unlearning more often than it charges execution does not exist. The
pattern `^rev\w*$` was matching **`revival` (311 keys, from `REVIVAL_LEDGER`)** and **`revoke` (92, capability
revocation)**. Genuine revision terms totalled about nine. Corrected: **1.1%**.

**`communication` reported 9.8%** via `^comm\w*$` matching `committed`, `commit` and `commuting`.
Corrected: **1.7%**.

This is the third prefix-pattern blowup in this corpus — after `state` matching *stated* and `production`
matching *reproduction* — and the pattern is consistent enough to state as a rule: **a prefix pattern over
identifiers will find a common unrelated word, and the tell is a number that is implausibly high rather than
implausibly low.**

Both corrected cases are kept as validated ground truth, so a regression is caught rather than re-derived.
A pin also asserts the narrowed patterns still match *something* — narrowing far enough to match nothing
would make the coordinate undetectable rather than rare, which reads the same in a table and is not the same
fact.

## 4  The detector is validated before its counts are believed

Six known-answer cases, **both polarities** — coordinates that must be found and coordinates that must not.
A pin asserts the validation set stays two-sided, because a detector checked only on cases it should accept
is not validated at all.

## 5  Scope

This measures whether a coordinate is metered **anywhere** in a receipt. It does **not** establish that every
claim in that receipt is charged for it, and it does not check that the number is correct. So the common
column is an upper bound on how well section N is satisfied.

Two of section N's eighteen boxes are not coverage questions at all but protocol rules — *no scalarization
without a prospectively frozen price vector*, and *report Pareto frontiers when prices are not fixed*. Those
are auditable in the same style and are **not** addressed here; they remain open.
