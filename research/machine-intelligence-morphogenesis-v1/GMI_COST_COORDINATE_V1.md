# Section N measured: which cost coordinates the corpus actually meters

Date: 2026-09-15. Addresses checklist section **N** (resource and lifecycle accounting).
Witness: `gmi_microscope/cost_coordinate_audit.py`. Receipt: `microscopes/results/STAGE_COST_COORDINATE_V1.json`.

Section N lists sixteen cost coordinates every claim should meter. This measures how many of the corpus's
**459 derivation receipts** carry each one.

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
| maintenance | 1 (0.2%) | **rare** |
| human / AI design input | 1 (0.2%) | **rare** |
| energy | 2 (0.4%) | **rare** |
| revision / unlearning | 4 (0.9%) | **rare** |
| communication | 6 (1.3%) | **rare** |
| verification | 36 (7.8%) | |
| retrieval / index | 58 (12.6%) | |
| precision | 70 (15.3%) | |
| physical counters | 88 (19.2%) | |
| training / development | 115 (25.1%) | |
| failed-candidate | 170 (37.0%) | |
| search / discovery | 237 (51.6%) | **common** |
| update | 246 (53.6%) | **common** |
| serving / execution | 280 (61.0%) | **common** |
| memory / storage | 281 (61.2%) | **common** |
| build / acquisition | 289 (63.0%) | **common** |

**Five of sixteen are commonly metered; five are essentially never.** The corpus charges what it computes —
building, storing, serving, updating, searching — and rarely charges what it does *after*: revising,
communicating, maintaining, and the energy or human input that went in.

## 3  The audit caught two of its own patterns being wrong

**`revision/unlearning` first reported 81%** — the highest of any coordinate, which is what made it
obviously wrong: a corpus that charges unlearning more often than it charges execution does not exist. The
pattern `^rev\w*$` was matching **`revival` (311 keys, from `REVIVAL_LEDGER`)** and **`revoke` (92, capability
revocation)**. Genuine revision terms totalled about nine. Corrected: **0.9%**.

**`communication` reported 9.8%** via `^comm\w*$` matching `committed`, `commit` and `commuting`.
Corrected: **1.3%**.

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

## 4b  An audit must not count its own output

Both audits scan every receipt, so adding the pricing-protocol receipt changed the cost-coordinate audit's
own inputs and broke its reproduction — in CI and on billy-old simultaneously. That is a **structural
coupling**, not a one-off: every future audit would have silently moved these numbers.

Both audits now exclude the four **self-referential** receipts — the outputs of audits that scan the corpus —
so each is a function of the **derivation** receipts alone. The excluded list is recorded in both receipts, so
the exclusion is auditable rather than hidden, and the counts above are stable against adding another audit.

## 5  Scope

This measures whether a coordinate is metered **anywhere** in a receipt. It does **not** establish that every
claim in that receipt is charged for it, and it does not check that the number is correct. So the common
column is an upper bound on how well section N is satisfied.

## 6  The two protocol rules — audited

Section N's other two boxes are **rules**, not coverage questions, and a rule is checkable in a way a count is
not. Witness: `gmi_microscope/pricing_protocol_audit.py`, receipt `STAGE_PRICING_PROTOCOL_V1.json`.

Of 459 derivation receipts, **324 meter two or more cost coordinates** — the population on which either rule can bind.

**R1 — no scalarization without a prospectively frozen price vector: clean.** Two multi-coordinate receipts
scalarize, and **both carry a price-vector key. Zero violations.** A pin asserts that *something* scalarizes,
because a rule satisfied only because nothing ever triggers it demonstrates nothing.

Getting there required reading rather than counting. The audit first flagged **two candidate violations**, both
in log-domain receipts, on a key called `w_scalars`. Reading it showed `w_scalars = 352` — a **count of scalar
weights** in the machine, a size measure, not a cost scalarization at all. R1 restricts scalarizing *costs*;
calling a weight count a pricing breach would have been exactly the over-claim these audits exist to prevent.
The false positive is excluded **by name with its reason recorded**, and pinned, so the next reader does not
re-derive it as a violation.

**R2 — report Pareto frontiers when prices are not fixed: substantially unmet.** Of **289** unpriced
multi-coordinate receipts, **65 (22%) report a frontier** and 224 do not. Pins assert the figure stays
strictly between none and all: all would make R2 trivially met, none would suggest the pattern matches
nothing, and either would be a different claim than the one measured.

So N's two rules split: **one is met, one is met about a fifth of the time.**


