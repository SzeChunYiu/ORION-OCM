# THEORY V2 — blind-recovery protocol v2 (GMI #833 / #434)

## Scientific question

Can a family-hidden search recover a known machine-intelligence family's
morphology when EVERY input channel — including the two the audited v1 left
open, task authorship and basis authorship — is closed by a declared neutral
rule? And what does the recovery boundary look like across a complete neutral
battery rather than one authored task?

## Why v2 exists: the two open channels, quantified

The motivation receipt (`MOTIVATION_RECEIPT_V1.json`) reproduces the auditor's
counterfactual with the REAL v1 adjudicator imported unmodified: v1 mechanics
on OR (`[0,1,1,1]`) recover a single-threshold-site construction at cost 2 and
the v1 adjudicator returns NOT_RECOVERED; on XOR (`[0,1,1,0]`, v1's actual
task) the same machinery returns RECOVERED at cost 7. Changing only the task
flips the verdict — the XOR choice carried the family information.

v2 replaces the choice with a class: B_BOOL2 = ALL 16 two-input boolean
functions plus a class-universal machine task; B_DELAY = ALL lags to the
state-domain counting bound; B_LOCAL = ALL 256 elementary local rules; B_BOOL3
= ALL 256 three-input functions. The basis is likewise closed: the unary tier
U_ORD = {NEG} + {GE_c for EVERY cut c in the value domain} — tier-complete
within order-tests, so the family's characteristic gate is present but
unprivileged (v1 had exactly one threshold, under a neutral name).

## The central result (see RESULT_V2.json / POSTHOC_RESULT_V2.json for numbers)

Under the complete neutral battery, per-task minimal constructions split by
linear separability:

- Every linearly-separable function of two inputs (14 of 16) has a
  SINGLE-gate minimal construction and honestly FAILS the frozen K01
  fingerprint — the protocol is not a rubber stamp; the v1 OR counterfactual
  generalizes to the entire separable class.
- The two non-separable functions (XOR, XNOR) have minimal constructions with
  TWO order-test sites on a COMMON skeleton (GE_c(ADD(x0,x1)) at two cut
  parameters, summed with negation) — parameterized aggregation sites +
  reuse-of-construction + non-affine internal response + multi-stage
  composition: the frozen K01 fingerprint is satisfied, RECOVERED, with no
  author having selected the task (the class is complete by rule).

This QUANTIFIES the audit finding: the v1 task choice singled out the 12.5%
of the neutral battery where the morphology is forced. Recovery under v2 is
not "the search produced a network" but "the search's morphology distribution
has a sharp boundary at linear separability, and the fingerprint passes
exactly across it." The family information content of the v1 task channel is
therefore measured, not assumed.

## Why the class-universal machine tranche is reported as bounded, not recovered

The class-universal task (one machine computing all 16 functions selected by
rank bits) requires boolean multiplexing. Under the frozen basis {ADD, NEG,
GE_c} there is no multiplication primitive; a tree-expression mux floor is of
order 100 operator nodes (mux = XOR/AND compositions; AND = GE_1(x+y-1),
XOR = GE_1(x-y)+GE_1(y-x)), far beyond the frozen 16-layer cap. The DP
certifies no-solution within the layers/width completed and reports the bound
(cap_bound / width_bound). Attribution: ONE stage — the tree cost model
prices shared subconstructions at every use, i.e. it structurally underprices
reuse-economy architectures; the revival lever (recorded in OPEN_GAPS, not
executed in v1 of this package) is a counted-once DAG cost model. This is a
structural observation about cost models, not a family failure.

## K02 (recurrent/stateful)

Machine model M_STATE: one integer cell in D, update s'=e_s(s,x), output
y=e_y(s,x), initial state 0; battery = all delayed-copy lags 0..floor(log2|D|)
over a de Bruijn stream of order l_max+1 (every input history occurs). The
minimal machines for lag >= 1 must maintain and read state (the counting
bound makes this necessary, not authored): adjudication executes state
interventions (force alternative reachable state under matched input) and
matched-input/different-state/different-output witnesses. Lag 0 (identity) is
expected to honestly fail the fingerprint (no state dependence) — the battery
contains it by completeness, and the adjudicator reports it as
NOT_RECOVERED_AT_SCOPE, showing the boundary again.

## K03 (local/shared transform)

Per-rule machines: four INDEPENDENTLY searched site expressions over the full
ring atoms — locality and sharing are never enforced by the model, only
measured posthoc. For non-wiring rules the minimal site constructions share a
skeleton (the same local construction instantiated at rotated sites =
parameterized reuse) and satisfy locality (supports within the 3-site
window) + rotation transport + remote-perturbation invariance. Wiring-only
rules (constants, identity, pure shifts) have leaf-only constructions and
honestly fail clause C0 — a shift has no transform to share. The recovery
boundary is again reported as a distribution, not a single verdict.

## K04 (content-dependent routing), secondary

Per-task minimal constructions over all 256 three-input functions; the
routing fingerprint (content-dependent selection between sources) is witnessed
exactly on the selector/mux subclass; distribution reported.

## Robustness (two searches / two presentations), stated precisely

PROC1 = cost-layered DP over the semantic quotient (layer sweeps, per-layer
maps, min-cost representatives); PROC2 = uniform-cost best-first expansion
(heap, closed-on-pop, postfix encoding). Disjoint mechanics, same frozen
objective/budget frame; PROC2 verifies PROC1's costs (recorded per task).
Presentations: TREE_AST and POSTFIX_STACK_ENCODING. Unlike v1's pair (one
algorithm in two encodings), the procedures differ in search mechanics; the
semantic quotient they share is stated openly rather than obscured.

## What this proves / does not prove

PROVES (at the registered finite scopes): family morphology (K01 threshold
networks; K02 state machines; K03 shared local kernels; K04 routing) is
recovered by family-hidden search on coverage-complete neutral batteries
under a tier-complete basis, with every channel's blindness argument stated
in advance and screened (lexical + #855 A2 semantic); the recovery boundaries
(separability for K01, lag>=1 for K02, non-wiring for K03, selector class for
K04) are measured, and the family-information content of v1's open channels
is quantified.

DOES NOT PROVE: all-family recovery (K05-K08, K10, K11 out of scope; K09
untouched); learning/training extensions; PREDICTED_SELECTED (not claimed);
that the order-test tier is the uniquely neutral basis (bounded by the U_ALL3
ablation where feasible); real-scale usefulness.
