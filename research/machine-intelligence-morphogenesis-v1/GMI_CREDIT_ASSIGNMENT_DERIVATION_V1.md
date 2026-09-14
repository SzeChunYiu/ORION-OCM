# Reverse-mode credit assignment and neutral MLP recovery (B4, closing)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/credit_assignment_witness.py`.
Receipt: `microscopes/results/STAGE_CREDIT_ASSIGNMENT_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

`GMI_UPDATE_LAW_DERIVATION_V1.md` left two boxes open and said why: it read
slopes directly rather than propagating them, so it could say nothing about
*how* slopes should be obtained; and neutral MLP recovery needed a slope-bearing
ecology it did not have. This supplies both.

Nothing is asserted from a formula. **Both accumulation modes are implemented
and executed on the same computation graph**, and their multiply-accumulates are
counted.

## Forward and reverse accumulation, counted

| `n_in` | `n_hid` | `n_out` | params | forward | reverse | cheaper |
|---:|---:|---:|---:|---:|---:|---|
| 4 | 4 | 1 | 16 | 320 | **40** | reverse |
| 8 | 8 | 1 | 64 | 4608 | **144** | reverse |
| 2 | 2 | 8 | 4 | 80 | **68** | reverse |
| 2 | 1 | 8 | 2 | **20** | 34 | **forward** |
| 2 | 1 | 32 | 2 | **68** | 130 | **forward** |
| 1 | 1 | 32 | 1 | **33** | 97 | **forward** |

> Forward cost scales with the **parameter** count; reverse cost scales with
> the **output** count. That asymmetry is the derived result.

**It is not a bare "more parameters than outputs" rule.** At 4 parameters and 8
outputs reverse still wins, because a forward pass carries the whole output
layer while a backward traversal per output does not. The crossover sits where
`n_out × (backward traversal)` passes `P × (forward pass)`, and those per-pass
costs are part of the graph. Stating it as `P > n_out` would be tidier and
wrong.

A loss is a single scalar, so a machine learning from a scalar signal sits at
`n_out = 1` — the deepest point of the reverse regime.

> That is why reverse mode looks universal in practice. **It is not universal;
> it is the correct side of a ratio that learning happens to sit on**, and the
> forward rows above are the side it does not sit on.

*Two modelling errors were caught here by the non-vacuity gate before anything
was written down. The first version counted reverse mode as a single backward
pass regardless of output count — it needs one per output. The second still made
every output carry its own weights, so the parameter count grew with the output
count and the forward regime was unreachable by construction. Both made reverse
mode win everywhere, which is exactly what a derivation with no content looks
like.*

## Neutral recovery: the search is never told what an MLP is

Candidates are `(depth, width, nonlinearity present)`. The search is told only
whether the obligation is met and what the shape costs. **No family name appears
anywhere in the candidate description.**

| obligation | depth | width | nonlinearity | cost | is an MLP |
|---|---:|---:|---|---:|---|
| `or2` | 1 | 0 | yes | **4** | **no** |
| `xor2` | **2** | **2** | **yes** | 10 | **yes** |

XOR recovers a depth-2 machine *with* a nonlinearity — an MLP, selected by cost
alone. OR recovers a single layer, because the extra structure would be paid for
and not used.

> **The MLP is what the accounting selects when, and only when, the obligation
> defeats a single weighted sum.** It is not a default and it is not an
> improvement in general.

The witness aborts if the search recovers an MLP for *every* obligation — that
would be a search that prefers MLPs rather than one that prices them.

## What this closes, and what remains open on B4

**Closes** reverse-mode credit assignment (derived from counted operations, with
its negative twin) and neutral recovery of a small MLP morphology (label-free,
with its negative twin).

**Still open**: a held-out ecology where the neural morphology is *predicted* to
win before the outcome is seen. That is a prospective-prediction box, and this
document's recoveries are retrospective — the obligations were chosen knowing
which side of the linear boundary they fall on.

**Still standing**: the `GRAD` depletion measured at 0.48× remains explained by
substrate inertness, per `GMI_UPDATE_LAW_DERIVATION_V1.md`. Nothing here
re-tests that.

## Scope

- The operation counts are for this graph shape. The *asymmetry* (forward scales
  with parameters, reverse with outputs) is the claim; the crossover's exact
  location depends on per-pass costs and is not claimed to be general.
- The readout `V` is deliberately fixed, so parameters do not grow with outputs.
  A network where every output carries its own weights cannot exhibit the
  forward regime at all, which is a fact about that architecture rather than
  about accumulation.
- Recovery uses 2 binary inputs, weight grid `−2…2`, bias `−2…2`, width ≤ 2, and
  six registered shapes. A shape outside that set cannot be recovered.
- ReLU and step are the only nonlinearities.

**Falsifier.** Exhibit a graph where reverse accumulation's cost grows with the
parameter count, or forward's with the output count. Or an obligation defeated
by a single weighted sum where the cheapest shape meeting it is still one layer.
