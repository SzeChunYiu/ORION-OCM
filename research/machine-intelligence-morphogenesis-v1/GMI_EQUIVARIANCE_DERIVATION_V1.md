# Convolution derived from translation symmetry (B5)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/equivariance_witness.py`.
Receipt: `microscopes/results/STAGE_EQUIVARIANCE_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

`GMI_NEURAL_ARCHITECTURE_DERIVATION_V1.md` established that weight sharing is
licensed by a symmetry **in the obligation**, never by a symmetry in the
architecture. This specialises that to **translation** symmetry, which is what
turns sharing into convolution.

## The symmetry descriptor, computed before any architecture

Does the obligation commute with a cyclic shift? A property of the obligation
alone, needing no candidate machine.

| obligation | shift-invariant | counterexample |
|---|---|---|
| `has_11` | ✅ | — |
| `has_101` | ✅ | — |
| `parity_all` | ✅ | — |
| `first_is_1` | **✗** | `010000` |

`first_is_1` fails with an **exhibited** counterexample — the descriptor does
not merely fail to prove invariance, it refutes it.

## The receptive field is read off the obligation

The smallest `w` for which the response is a function of the multiset of
`w`-windows, searched rather than assumed:

| obligation | receptive field |
|---|---|
| `parity_all` | 1 |
| `has_11` | **2** |
| `has_101` | **3** |
| `first_is_1` | **none** |

> Nothing about a kernel size was chosen. **The window that determines the
> response *is* the kernel size.**

`first_is_1` returns *none*: it is not a function of the window multiset at any
width, because the multiset discards position.

## What sharing buys

| obligation | `w` | shared | unshared | table | saving |
|---|---:|---:|---:|---:|---:|
| `has_11` | 2 | **2** | 12 | 64 | **6×** |
| `has_101` | 3 | **3** | 18 | 64 | **6×** |
| `parity_all` | 1 | **1** | 6 | 64 | **6×** |

Sharing is cheaper by exactly the number of positions the rule is reused at.
*Cheaper is not the same as correct* — legality is the descriptor above.

## Neutral recovery, with no `CONV` primitive anywhere

Candidates are `(window, shared or per-position)`. The search is told only
whether the obligation is met and what the shape costs.

| obligation | `w` | shared detector suffices |
|---|---:|---|
| `has_11` | 2 | ✅ |
| `has_101` | 3 | ✅ |
| `parity_all` | 1 | **✗** |

The two pattern obligations are met by **one rule reused at every ring
position** — a small window rule applied everywhere with results combined. That
object is a convolution, selected by cost from a candidate space containing no
such word.

**`parity_all` is the instructive failure.** It *is* shift-invariant and its
receptive field *is* 1, yet a shared detector cannot express it, because results
here are combined by OR and parity needs counting.

> Translation symmetry **licenses** weight sharing. It does not by itself make a
> convolution sufficient — the **combiner** has to match the obligation too, and
> shift-invariance says nothing about that.

## The negative twin

`first_is_1` is the same *kind* of obligation — a local pattern — but anchored
to a position. Everything else held fixed:

| obligation | shift-invariant | receptive field | shared detector works |
|---|---|---|---|
| `has_11` | ✅ | 2 | ✅ |
| `first_is_1` | **✗** | none | **✗** |

> The advantage disappears exactly when the symmetry does, and the descriptor
> predicts it **before any machine is built**.

A machine that shares weights on `first_is_1` is not merely inefficient — it
cannot express the obligation at all, checked by exhausting every window size up
to 3. Sharing *asserts* that position does not matter, and here it does.

## Scope

- Sequences of length 6 over a binary alphabet; cyclic (ring) topology.
- Windows are cyclic, matching the cyclic symmetry tested. *A first version used
  linear windows against a cyclic shift and nothing came out invariant — the
  mismatch was in the witness, not in the obligations.*
- The shared detector combines window results by **OR**. Other combiners would
  change which obligations are expressible; the `parity_all` row is exactly what
  that limitation looks like and is reported rather than hidden.
- The twin's negative is checked to window size 3, not all widths, and the
  document says so.
- Four obligations chosen to span invariant/non-invariant and local/global. They
  are not a sample of any distribution.

**Falsifier.** Exhibit a shift-invariant obligation whose receptive field is
smaller than the sequence and for which no shared detector beats a per-position
machine; or a position-anchored obligation a shared detector expresses exactly.
