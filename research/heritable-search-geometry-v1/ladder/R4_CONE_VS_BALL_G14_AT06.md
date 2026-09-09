# R4 — G14 / A_T06: cone-vs-metric-ball locality mismatch (load-bearing)

Rows: G14 (dependency cone), A_T06 (T06 exact dependency-cone locality, PROVED by lane A:
intervention on S cannot change nodes outside Desc(S); recomputation-skip licensed iff
dependency semantics complete for protected outputs). Rung R4 question: metric-ball
locality vs cone locality mismatch — "the operationally dangerous one".

## Verdict (first sentence)

LIFT_FAILS — metric-ball locality is FALSE in general while cone locality holds: a minimal
3-node DAG witness has an intervention whose metric ball (radius ≥ 1 around S under the
registered edit/Hamming-class metric) contains an unaffected node B and (in the mirrored
witness) misses an affected descendant, witnessed in
`hostiles/witnesses/hostile_cone_ball.json`.

## Minimal counterexample (hostile H3)

DAG: nodes {S, A, B}; single edge S → A; B isolated. Values are functions of declared
ancestors (complete semantics, T06's assumption xi holds). Registered metric: edit
metric on node labels/positions — d(A,B) = 1 (neighbouring slots), d(S,B) = 2,
d(S,A) = 2.

- Intervene on S: A changes (A ∈ Desc(S)); B does not (B ∉ Desc(S)). The metric ball
  B_d(S, 2) ⊇ {A, B} predicts "B affected" — WRONG. Cone locality (T06) gives the exact
  affected set {A}: right.
- Mirrored case: add edge S → B and remove S → A with a metric where d(S,A) = 3 > r:
  every ball of radius r < 3 MISSES the affected node A. Balls are symmetric and
  inclusion-nested; Desc(S) need be neither.

Structural reason (no metric repairs it): Desc(·) is an order-theoretic cone —
asymmetric, not nested in radii, and determined by the edge relation; balls of a metric
are symmetric and monotone in r. On any DAG with an isolated node adjacent in d to a
descendant, every ball mixing the two errs in at least one direction. Locality is a CAUSAL
statement, not a metric one.

## Why this is the operationally dangerous row

The recomputation-skip licence proved by lane A is CONE-licensed: skip outside Desc(S)
iff declared dependency semantics are complete for the protected outputs. An
implementation that uses metric proximity ("cache invalidation radius", embedding
neighbourhoods, "nearby modules") mispredicts in BOTH directions: it recomputes B
(wasted resource) and — worse — skips A (incorrect output, silent). The hostile file
names these two failure modes `over_recompute` and `under_invalidate`.

## The surviving statement (PARENT_SUFFICIENT, exact)

Cone locality itself at R4 reads verbatim: parent Pearl-class causal DAG intervention
locality (d-separation/intervention semantics): an intervention do(S = s) changes the
joint law only on Desc(S) ∪ {S}; outside, the law is invariant. T06 already cites this
parent; HSG adds only the mismatch hostile.

## Assumption passes (A3)

- Remove xi-cone-completeness: lane A's iff-direction covers it (skip licence lost);
  the metric hostile is unaffected — it attacks balls, not completeness.

## Registry note

G14 R4 = LIFT_FAILS (hostile H3); A_T06 R4 = PARENT_SUFFICIENT for the cone statement
(the mismatch is the residual, ours).
