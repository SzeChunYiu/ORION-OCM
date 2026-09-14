# Gating derived from variable duration, not long duration (B6)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/gated_recurrence_witness.py`.
Receipt: `microscopes/results/STAGE_GATED_RECURRENCE_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

`GMI_FINITE_STATE_DERIVATION_V1.md` derived the state requirement from the
quotient; `GMI_STATE_SPACE_DERIVATION_V1.md` asked how cheaply the update can be
written. This asks a third question: **when must the update be conditional?**

A gate is conditional retention — hold this or overwrite it, depending on the
input. What follows is the test of what forces one.

## The temporal cut

Streams differing only in the remembered symbol must be told apart at the query,
however far apart the two events sit. The distinction is *created* at one step
and *consumed* at another, so something must carry it across. CSR-1 prices it:
one state per distinction still owed.

## Retention and forgetting are one number, read from two ends

| register length `L` | cells | answers gaps |
|---:|---:|---|
| 1 | 1 | {0} |
| 2 | 2 | {1} |
| 4 | 4 | {3} |
| 7 | 7 | {6} |

Each register answers **exactly** the gap its length matches and no other.

> At fixed capacity, retention and forgetting are not two mechanisms to balance.
> They are one number read from two ends.

## What forces a gate

Two ecologies **matched on the longest delay they contain** — 4 in both. One
holds that delay fixed; the other varies it. Nothing else differs.

| ecology | max gap | ungated register solves it | gated cell |
|---|---:|---|---|
| fixed gap 4 | 4 | **yes** — length 5 | yes |
| variable gap 0/2/4 | **4** | **none at any length ≤ 8** | yes |

> **A gate is not what you reach for when something must be held a *long* time.
> It is what you reach for when the holding time is not known in advance.**
> Long-but-fixed is a register's job.

The witness asserts the two ecologies stay matched on longest delay — without
that, the comparison would be confounded by duration length rather than
duration *variance*.

## The crossover exists even at fixed duration

Where both machines work, the cheaper wins. A register costs one cell per step
of delay; the gated cell costs one cell plus the gate (priced at 2).

| fixed gap | register cells | gated cells | cheaper |
|---:|---:|---:|---|
| 0 | 1 | 3 | **register** |
| 1 | 2 | 3 | **register** |
| 2 | 3 | 3 | tie |
| 3 | 4 | 3 | gated |
| 6 | 7 | 3 | gated |

The winner changes exactly where the register's length passes the gate's price.

> Even with duration fixed and both machines correct, gating is a cost question
> with a threshold — and below it an ungated register is the right machine.

## Neutral recovery, with no LSTM, GRU or gate vocabulary

Candidates are described only by how many cells they carry and whether the write
is **unconditional** or **input-dependent**.

| ecology | cheapest shape | reads as |
|---|---|---|
| fixed gap 1 | unconditional write, 2 cells | **an ungated register** |
| fixed gap 6 | input-dependent write, 1 cell | **a gated cell** |
| variable 0/2/4 | input-dependent write, 1 cell | **a gated cell** |

Both shapes are recovered from the same description by cost alone. The
input-dependent write — what a gate *is* — is selected exactly where an
unconditional one cannot serve the ecology or costs more, and it was never named.

## Scope

- One remembered symbol, one query, delays ≤ 6, registers searched to length 8.
  "No register works" means *none at length ≤ 8*, and the witness reports it that
  way rather than claiming impossibility.
- The gate is priced at 2 cells. The *ordering* and the existence of a threshold
  are the result; the threshold's location moves with that price.
- The gated cell here is a single write-enable. Multiplicative gates, forget
  gates and output gates are not separately derived — what is derived is that the
  write must be **input-dependent**, which is the property all of them share.
- Only two machine shapes are compared. A machine that could index into a
  variable-length buffer is legal in this ledger and is not evaluated.

**Falsifier.** Exhibit a fixed-length register that solves a variable-duration
ecology; or a variable-duration ecology solved by an unconditional write; or a
fixed-delay ecology where the gated cell is cheaper at delay 0.
