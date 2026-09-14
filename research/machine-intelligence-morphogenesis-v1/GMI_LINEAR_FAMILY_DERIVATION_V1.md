# Linear, GLM, basis and kernel systems, derived (B3)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/linear_family_witness.py`.
Receipt: `microscopes/results/STAGE_LINEAR_FAMILY_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

`GMI_EXEMPLAR_VERSUS_PARAMETRIC_V1.md` showed a rule's cost does not grow with
the universe while a table's does. This asks what happens when the rule is
specifically a **weighted sum**, and derives the coefficient family from that.

Identification is decided by **enumerating every candidate weight vector**, and
representability by **exact Gaussian elimination over Fractions** — so the
formulas are confirmed rather than restated.

## 1–2. The coefficient vector, and the exact sample bound

True coefficients `(2, −1, 1)` over 3 binary features. A table needs 8 entries;
the coefficient vector needs 3 numbers.

| observations | consistent `w` | identified |
|---:|---:|---|
| 0 | 125 | no |
| 1 | 25 | no |
| 2 | **5** | no |
| **3** | **1** | **yes** |

Identification happens at `n = d` exactly. With `d − 1` observations **five**
weight vectors remain consistent, so no machine can answer correctly on every
continuation — the sample lower bound **exhibited**, not argued from rank.

Counting is not sufficient. Three *dependent* observations (`100 100 010`)
leave 5 candidates:

> The bound is `d` **independent** observations, which is what the
> dimensionality bound actually says.

## 3–4. Regression, and what a link costs

The same obligation through two response channels — the exact value, or a
binary threshold of it. The threshold is a GLM link: it discards magnitude.

| channel | identifies after |
|---|---:|
| real value (regression) | **3** = `d` |
| threshold (GLM link) | **7** |

> **A link does not destroy identifiability here — it delays it**, from `d = 3`
> to 7. A link buys a bounded response range and pays in samples: every
> thresholded observation carries strictly less than the value it replaced, so
> more are needed to reach the same conclusion.

*My first version of this section asserted the threshold could never identify.
It was false — with all 8 inputs it does. The delay is the robust claim.*

**Scope.** This alphabet is finite and the weight grid coarse, which is why the
threshold eventually becomes unique. Over an unbounded weight space a threshold
channel would fix the weights only up to positive scaling — a direction, not a
vector. Eventual uniqueness is an artefact of the grid and is **not** asserted
beyond it.

## 5. Linearity belongs to the pair, not the obligation

XOR of the first two features is not a weighted sum of them. Add one product
feature and it is — `w = (1, 1, 0, −2)`. Nothing about the obligation changed.

> Linearity is a property of the **pair** (obligation, basis), never of the
> obligation alone. A kernel machine is a coefficient machine whose basis was
> chosen so the obligation became compressible in it — **the choosing is where
> the work went**, and it is charged there rather than to the weighted sum.

## 6. What the basis costs, and why a rich enough kernel *is* a table

*A first version compared `d` coefficients against `2^d` table slots and found
coefficients cheaper at every `d`. That is not a crossover; it is the
observation that `d < 2^d`.* The real trade is the basis.

Monomial bases over `d = 3`, minimal degree found by exact solve:

| obligation | true degree | min basis degree | basis size |
|---|---:|---:|---:|
| constant | 0 | 0 | 1 |
| single bit | 1 | 1 | 4 |
| AND of two | 2 | 2 | 7 |
| XOR of two | 2 | 2 | 7 |
| 3-way parity | 3 | 3 | **8** |

Each obligation needs **exactly** its true degree. The full monomial basis has
`8` features; the universe has `8` inputs.

> **A kernel machine is not a way to avoid paying for a table.** It is a way to
> pay for only the part of the table the obligation needs — and at full
> expressiveness the two costs coincide *exactly*.

So the coefficient-versus-exemplar crossover is a statement about the basis:
coefficients win when a low-degree basis suffices, and the advantage disappears
continuously as the required degree rises.

*An earlier attempt at this table searched a ±2 weight grid and reported 3-way
parity as unrepresentable. That was a grid artefact — parity needs a
coefficient of 4. Replacing the search with an exact solve removed it. "Not
representable" and "not representable with these coefficients" are different
claims.*

## 7. A quantitative prediction, frozen then measured

Prediction, computed before the measurement: a coefficient machine over `d`
features identifies after exactly `d` independent observations — not `d − 1`,
and not more.

| `d` | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| predicted | 1 | 2 | 3 | 4 |
| measured | **1** | **2** | **3** | **4** |

Holds at every dimension tested. A derived consequence, not a fit — nothing was
tuned to make it land.

## Scope

- Binary features, `d ≤ 4`, integer weight grid `−2…2` for the identification
  counts. The grid bounds *how many* candidates are counted; it does not affect
  where identification occurs, which is checked at `d` for every `d`.
- Representability uses exact rational solving with no grid at all.
- Five structured obligations of known degree. They exhibit the ladder; they
  are not a sample of any natural distribution.
- Least-squares fitting under noise is not modelled. Everything here is exact
  identification under noiseless observation.

**Falsifier.** Exhibit a coefficient machine identified by fewer than `d`
independent observations; or an obligation whose minimal monomial degree
differs from its true degree; or a full monomial basis whose size differs from
the number of inputs.
