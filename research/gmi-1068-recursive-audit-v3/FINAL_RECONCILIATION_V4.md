# R0–R17 reconciliation after four scoped repair rounds

Issue #1068 remains the control plane. Issue #833 remains historical evidence.
This reconciliation records the work completed in rounds A–D. It does not claim
that GMI is complete, that assumptions have disappeared, or that all machine
intelligence forms have been derived.

`SCOPE_SNAPSHOT_V4.json` is additive. The V3 snapshot and every historical artifact
record remain unchanged. V4 retains the earlier R5 repair and adds the actual
source/result hashes and named witnesses for the R6, R11/R12 and R4 repairs.
Parent digests are recomputed to bind this new evidence consistently. A changed
parent binding does not itself earn a dependent round.

## Claims now supported at their declared scope

| Repair | What is supported | Evidence level | What remains outside the result |
|---|---|---|---|
| A: R5 resource geometry | Identity and triangle bounds from actual minimizing witnesses, nonnegative costs, composition and subadditivity; minimal-element transport under an order-reflecting surjection. Real-infimum and Pareto existence/nonattainment conditions are stated separately. | Three Lean 4.19.0 proofs; paper arguments for the real/infinite extensions; two-route checks over 4,096 finite graphs. | A unique universal metric, physical resource accounting, existence of minima in arbitrary spaces, or complete R4/R5 closure. |
| A: scope gate | Canonical DAG and atomic coverage, file hashes, witness locators, parent bindings, stale descendants, explicit custody mode and rejection of unsupported status promotion. | 25 mutation tests in normal and optimized Python; registered integrity checks. | The truth of a theorem merely because its file and declaration exist; trustless certification of a maliciously changed checker. |
| B: R6 operational genesis | Exact triangular dispatch bound despite a divergent predecessor; all scalar reuse-cost regimes; actual code modification including a modifier of a modifier; a two-state delay lower bound and sufficient construction; stated minimax and countable-uniform obstructions. | Paper proofs; separate operational implementations; 72 scheduler cases, 6,656 cost cases, 24 modification cases and 511 delay words. | Efficient useful discovery, universality of the demonstrated RAM, proof-assistant verification of these general arguments, validated beneficial self-change, or elimination of language/objective/search assumptions. |
| C: R11 control semantics | Finite discounted controlled quotient under reward and action-conditioned transition compatibility; an explicit approximate value/regret bound; perfect latent prediction and noncollapse can coexist with lost control information. | Full paper proofs with explicit premises; 36 fixed-policy checks, 64 direct-return checks, 60 trace checks and malformed-input controls in both interpreter modes. | Measured uniform residuals for a learned world model, new JEPA experiments, general identifiability without source assumptions, or formal verification in Lean. |
| C: R12 findings audit | All 52 frozen registry rows retain source ownership and record the evidence needed for their claimed GMI relationship. Finite proxies do not establish full-family derivations. | Exhaustive audit of that registered row set; exact schema/lineage checks and conservative adjudication. | Rereading every one of the 52 original sources, deriving all 52 findings, reproducing their experiments, or completeness beyond the frozen registry. |
| D: R4 statistical sufficiency | Classical parameter sufficiency and the declared mixture-predictive sufficiency are incomparable. Both predicates are computed from exact joint laws and independently checked by conditional-independence cross-products. | Paper proofs; 7,232 table/statistic comparisons, 18 mechanism/prior cases, 96 relabelings and nine negative controls. | Complete future-test semantics, sufficiency for every prior/intervention/future, inference of exact laws from samples, or full R4 semantic integration. |

The R4 successor's original conditional response-equivalence Lean statements
also passed Lean 4.19.0 with warnings treated as errors. Repair D replaces the
hardcoded statistical verdict evidence through an additive module. It does not
retroactively certify every assertion or hostile-test count in that older receipt.

The R11 source audit found that a nonlinear lower-bound proof step cannot be
imported merely from pointwise minimum Jacobian singular values. The repair
states the additional finite-distance expansion condition needed by its own
argument. This is a scoped proof-step finding, not rejection of the source paper
or its experiments as a whole.

## Current registered requirements and dependency state

There are **205 original R0–R16 atomic requirements plus 17 R17 requirements,
222 in total**. V4 keeps every stable ID, historical initial status, current audit
status and disposition from V3. All 222 remain unresolved at the integrated
round-closure level. This does not mean all historical propositions are false or
that no component has been proved; the local repair records state exactly which
components now have evidence. No new whole-round EARNED status is asserted.

| Rounds | Declared current status | Remaining integrated requirement |
|---|---|---|
| R0–R3 | UNKNOWN in this successor audit | Historical results remain recorded. Independent atom-by-atom reconciliation and the later irreducibility/final-audit requirements have not been completed. R1 erasure witnesses are presentation-relative; R2 non-uniqueness is not a primitive-symbol-count theorem. |
| R4 | OPEN, with repair D locally verified | Complete response/test semantics, observational and resource boundaries, and registered bridge integration remain. |
| R5 | STALE, with repair A locally verified | Corrected conditional geometry does not earn the entire parent chain or all resource claims. |
| R6 | STALE, with repair B locally verified | Corrected operational witnesses do not establish general useful discovery, beneficial self-improvement or all genesis claims. |
| R7–R10 | STALE | Family recovery, architecture leakage, update-law and information/control claims still require their own corrected evidence and earned parents. |
| R11–R12 | STALE, with repair C locally verified | The controlled-state theorem and finite source audit do not establish every physical-AI or registered family claim. |
| R13 | STALE; historical adjudication already merged | Existing evidence adjudication is retained. New performance evidence and corrected parents are still required. |
| R14 | OPEN | Prior and irreducibility audit remains. |
| R15–R16 | NOT_STARTED | Integrated simplification and publication readiness depend on the unfinished chain. |
| R17 | OPEN | Full scope-bound final audit, source ownership, empirical lineage, hostile review and unresolved-region reconciliation remain. |

The canonical DAG is unchanged. The derived stale closure includes R5 through
R17. In particular, later rounds cannot remain earned after a stale ancestor,
and hashes from the historical baseline cannot silently serve as evidence for a
changed parent. Local verification does not remove this dependency boundary.

Literal absence of assumptions is not a supported target: the work explicitly
retains representation, task, observation, objective, comparison and resource
choices. The proved obstructions distinguish assumption-free optimality from
useful learning under declared assumptions. They do not rule out ambitious
architecture-blind research with those assumptions disclosed.

## Review level and reproduction

The mathematical and executable work was cross-reviewed by **internal agents**.
This is not independent external replication, outside peer review or a reproduced
real-scale experiment. Distinct implementations improve error detection but
share the same project environment and declared fixtures.

`check_successors_v4.py` verifies both snapshots, pins the unchanged V3 bytes,
checks that historical artifact records and atomic statuses were preserved,
validates all new file hashes/locators, and applies the baseline transition gate.
Its changed-path list is derived from new registered artifact entries. External
CI must separately bind the target baseline and changed paths to actual git
history; the helper does not authenticate git lineage by itself.

```sh
python3 -I -B research/gmi-1068-recursive-audit-v3/check_successors_v4.py
python3 -I -O -B research/gmi-1068-recursive-audit-v3/check_successors_v4.py
```

CI should also invoke `gate.py` with `--snapshot SCOPE_SNAPSHOT_V4.json`, the
trusted `--baseline SCOPE_SNAPSHOT_V3.json`, and `--changed-files` obtained from
the corresponding git comparison. The full paths are required when running
outside this directory. The expected successful result retains
`overall_closure: OPEN` and `scientific_truth_certified: false`.
