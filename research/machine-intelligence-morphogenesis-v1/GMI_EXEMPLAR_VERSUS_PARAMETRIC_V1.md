# Exemplar memory, retrieval bounds, kNN, and the crossover (B11 remainder)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/exemplar_parametric_witness.py`.
Receipt: `microscopes/results/STAGE_EXEMPLAR_PARAMETRIC_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

Two of B11's boxes were closed by `GMI_K4_SUBSTITUTION_REPAIR_V1.md` — the
index-amortisation threshold, and neutral recovery of memory-indexed solutions.
The four here are about **which** memory, not whether to have one.

Exemplar storage, parametric compression and local (kNN) lookup are not three
designs to choose between on taste. They are three regimes of one comparison,
and each is forced somewhere. The rule class is searched exhaustively for the
shortest description that fits, so *compressible* is measured, not assumed.

## Retrieval bounds

A store answering all `M` inputs with no rule to fall back on needs one slot per
input it cannot infer, so the lower and upper bounds coincide at `M`.

| obligation | shortest rule | rule cost | exemplar cost |
|---|---|---:|---:|
| `constant` | `const1` | 2 | 17 |
| `first_bit` | `bit0` | 3 | 17 |
| `threshold_2` | `thresh>=2` | 4 | 17 |
| `parity` | `parity` | 5 | 17 |
| `incompressible` | **none** | — | 17 |

## The comparison, stated at the right coarseness

With these prices a rule always wins when one exists, so that table decides
**expressible versus not** — which is coarser than a crossover, and saying
otherwise would overclaim. The graded crossover lives in **problem size**.

Holding the obligation fixed at `parity` (rule cost 5) and growing the universe:

| bits | `M` | exemplar | parametric | cheaper |
|---:|---:|---:|---:|---|
| 1 | 2 | 3 | 6 | **exemplar** |
| 2 | 4 | 5 | 6 | **exemplar** |
| 3 | 8 | 9 | 6 | parametric |
| 4 | 16 | 17 | 6 | parametric |
| 6 | 64 | 65 | 6 | parametric |

The winner flips between `M = 4` and `M = 8`, where the cost of storing
everything passes the fixed cost of describing the rule.

> **A rule's cost does not grow with the universe; a table's does.** That is the
> whole of the retrieval-versus-parametric crossover — and it says a
> memory-based machine is not a weaker machine, but the correct one on a small
> or incompressible world.

## kNN is the middle case, and the metric has to earn it

Local lookup stores a **subset** and answers by nearest neighbours. Smallest
subset that answers every query correctly, searched rather than assumed:

| obligation | k=1 subset | kNN cost | beats storing everything |
|---|---:|---:|---|
| `constant` | 1 | 2 | ✅ |
| `first_bit` | 2 | 3 | ✅ |
| `threshold_2` | 4 | 5 | ✅ |
| `parity` | **none ≤ 8** | — | ✗ |
| `incompressible` | **none ≤ 8** | — | ✗ |

> Local lookup is cheaper than full storage **exactly when the obligation is
> smooth in the metric** — when nearby inputs demand nearby responses.

Parity is the sharp negative: flipping *one* bit flips the response, so it is
maximally rough in precisely the metric kNN relies on. A machine can have a
perfectly good store, a perfectly good metric, and still gain nothing, because
the two are not aligned. The witness aborts if local lookup ever beats full
storage on *every* obligation — that would mean the metric was doing no work.

## When an exemplar earns its slot

PVR-3 on a single stored item: keep it iff `S < (r−1)(C−U)`.

| reuse `r` | `C` | `U` | fresh `rC` | retain | keep |
|---:|---:|---:|---:|---:|---|
| 1 | 4 | 1 | 4 | 5 | no |
| 2 | 4 | 1 | 8 | 6 | **yes** |
| 2 | 2 | 1 | 4 | 4 | no |
| 3 | 2 | 1 | 6 | 5 | **yes** |
| 10 | 1 | 1 | 10 | 11 | **no** |

> **No exemplar is ever worth keeping when consulting it costs as much as
> recomputing it**, at any recurrence — including `r = 10`.

Generalization benefit enters as `C`: a strongly generalizing rule makes
recompute cheap, which *raises* the recurrence an exemplar needs before it pays.
That is the answer to "exemplar storage when recurrence exceeds generalization
benefit" — the two are not separate quantities, they are the two sides of one
break-even.

## Scope

- A 4-bit universe (16 inputs) and a deliberately small rule class: constants,
  single-bit reads, thresholds, parity. A class that could express everything
  cheaply would make the comparison vacuous; one that could express nothing
  would make it trivial. The cost numbers are properties of this class.
- The kNN subset search is capped at size 8 and reports `none ≤ 8` rather than
  claiming impossibility — parity may need a larger subset, not no subset.
- `incompressible` is one fixed pseudo-random table, not a random sample over
  tables. It witnesses that the class has gaps; it does not measure how many.
- Slot, description, evaluation and lookup are each priced at 1. The
  *orderings* are the result; the magnitudes are not.

**Falsifier.** Exhibit an obligation with a short rule where exemplar storage is
still cheaper at large `M`; or one that is rough in the metric where kNN beats
full storage; or a case where an exemplar pays with `U ≥ C`.
