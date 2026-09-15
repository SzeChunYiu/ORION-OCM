# Section C box 14 — a held-out prediction for an ecology never enumerated

Every Section C result so far lives in one ecology: 4 states, 2 evidence
symbols, evidence sequences of length `L = 2`, 256 tasks. This box asks whether
the theory predicts a *new* ecology. The target is `L = 3`: 8 sequences, 65536
tasks, a task space 256× larger and a strictly finer instrument, since a
length-3 sequence separates update objects a length-2 sequence cannot.

Six predictions were committed in `a131a9d3` with **no measuring code and
nothing at `L = 3` computed**. `compare_heldout_ecology.py` landed afterwards.

**Four hold, two are falsified — and the split is the result.** Every
*structural* prediction transferred. Both *quantitative extrapolations* failed.

## The theorem that carried

> **For every `L ≥ 1`, `beh_L(state-only) ⊆ beh_L(overwrite)`.**
>
> A `state-only` update ignores evidence, so it is a map `f : S → S` applied once
> per symbol; after any length-`L` sequence the state is `f^L(START)`, regardless
> of the sequence. So every `state-only` behaviour is a constant tuple, and
> `f ≡ c` attains each one: `beh_L(state-only)` is *exactly* the constant tuples.
> An `overwrite` update has `u(s,e) = h(e)`, so for `L ≥ 1` the final state is
> `h(e_L)` — determined by the last symbol. Taking `h(0) = h(1) = c` gives every
> constant tuple. ∎

With box 11's behaviour-containment theorem this makes `state-only` never
uniquely best **at any sequence length** — structural, not an artefact of `L = 2`.
The enumeration confirms it: `|beh(state-only)| = 4` and
`|beh(overwrite)| = 16` at `L = 3`, exactly as registered, and `state-only` is
uniquely best on 0 of 65536 tasks.

## Self-validation before any held-out number

A checker is only trusted on data whose answer is already known. The same code
was first run at `L = 2` and required to reproduce box 12's published receipt
exactly — `additive 14, insertion-monotone 18, idempotent-on-repeat 20`, zero for
the rest. It does, and the run aborts if it does not. Only then is `L = 3`
reported.

## Results

| law | behaviours `L=2` | behaviours `L=3` | uniquely best `L=2` | uniquely best `L=3` |
|---|---|---|---|---|
| `idempotent-on-repeat` | 82 | 142 | 20 | 11182 |
| `additive` | 8 | 16 | 14 | **5722** |
| `insertion-monotone` | 56 | 56 | 18 | **3170** |
| `keep-or-replace` | 52 | 64 | 0 | 0 |
| `overwrite` | 16 | 16 | 0 | 0 |
| `state-only` | 4 | 4 | 0 | 0 |

| prediction | outcome |
|---|---|
| H1 `beh(state-only) ⊆ beh(overwrite)` | HOLDS |
| H2 `state-only` uniquely best on 0 tasks | HOLDS |
| H3 behaviour counts 4 and 16 | HOLDS |
| H4 never-uniquely-best set unchanged | HOLDS |
| H5 order `idempotent > insertion > additive` preserved | **FALSIFIED** |
| H6 unique-best fraction strictly smaller | **FALSIFIED** |

H4 was flagged in advance as the prediction most likely to fail — a longer
sequence can break a containment by probing a distinction a shorter one cannot
reach. It held: the never-uniquely-best set is `{keep-or-replace, overwrite,
state-only}` at both lengths. The containment structure is stable under
refinement of the instrument.

### H5: `additive` and `insertion-monotone` swap

Predicted `idempotent > insertion > additive`; measured
`idempotent (11182) > additive (5722) > insertion (3170)`.

`additive`'s behaviour count doubles from 8 to 16 while `insertion-monotone`'s
stays at 56 — yet `additive` overtakes it. **Uniqueness is not driven by how many
behaviours a law has, but by how little they overlap with other laws'.**
`insertion-monotone` is constrained by bitwise monotonicity, and its 56
behaviours sit largely inside `idempotent-on-repeat`'s 142, so it wins the max
but rarely *alone*. `additive`'s modular shifts are not contained in any other
law, so each of its 16 behaviours converts to sole wins. A behaviour count is a
capability measure; a unique-win count is a *distinctiveness* measure, and the
two diverge.

### H6: uniqueness becomes commoner, not rarer

Predicted the unique-best fraction would shrink because the task space grows 256×
while behaviour sets grow far less. Measured: **20.3% at `L = 2`, 30.6% at
`L = 3`** — it grew.

The reasoning inverted the effect of dimension on ties. A tie requires two laws
to achieve the *same* maximum match. Going from `L = 2` to `L = 3` takes the
score from a max over 4 coordinates to a max over 8: there are more ways for two
laws to differ, so exact ties get *rarer*, and sole winners commoner. Adding
task-space volume does dilute match quality, but adding coordinates sharpens
discrimination, and here discrimination dominates.

This is the same shape of error as box 11's falsified P4 — in both cases I
reasoned about one term of a comparison and neglected that the other moved too.

## What transfers

The honest summary of this box is a boundary, not a victory:

- **Structural claims transfer.** Containments, the never-uniquely-best set, and
  the exact behaviour counts of the evidence-independent laws were all predicted
  correctly from `L = 2` plus a proof, before `L = 3` existed.
- **Ordinal and quantitative claims do not.** Both extrapolations of *magnitude*
  from `L = 2` failed, and each failed because a second quantity moved with the
  first.

A theory that predicts which laws *can* dominate is in better shape than one
predicting *how much* they dominate by. That distinction is now measured rather
than asserted.

## Scope

Exhaustive: 65536 update objects, 6 paradigms, 65536 tasks at `L = 3`, 256 at
`L = 2`. All counts are exact integers over complete enumerations; nothing is
sampled. The `L`-independence theorem is proved for all `L ≥ 1`; every other
claim is about `S = 4`, `E = 2`, `L ∈ {2,3}`.

Receipt: `microscopes/results/STAGE_HELDOUT_ECOLOGY_V1.json`.
