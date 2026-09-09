# R4 — A_T03: can a metric separate aliased states? iff-statement and its cost

Row: A_T03 (T03 representation insufficiency by indistinguishability, PROVED), rung R4
ladder question: "can a metric separate aliased states? yes iff — what does that cost".

## Verdict (first sentence)

LIFT_CONDITIONAL — a registered metric d separates the aliased pair (d(s1,s2) > 0) iff
the metric function is itself admitted to the policy's observation; the cost is exactly
T03's "new channel": extending the observation σ-algebra σ(φ) to σ(φ, d), i.e. the metric
must be paid for as an input, not assumed for free — parent: T03's own quotient/aliasing
argument (Mealy-minimization duality), no new geometry needed.

## Exact iff-statement

Read T03 at R4. φ: 𝓢 → Y is the observation channel; aliasing means φ(s1) = φ(s2) while
the contract demands disjoint action sets G(s1) ∩ G(s2) = ∅.

- (Metric fact, trivial:) ANY metric d with d(s1,s2) > 0 separates the pair as points of
  the metric space (𝓢,d). Discrete d does this for free — separation as a space property
  is vacuous.
- (Policy fact, the content:) a policy measurable w.r.t. φ factors through φ, so its
  decision rule is constant on each φ-fibre {s : φ(s) = φ(s1)}; it is therefore blind to
  EVERY registered metric (any d-based rule `s ↦ f(d(s,s1))` must itself be φ-measurable,
  forcing f to be constant on the fibre). Separation is USEFUL iff there is an observation
  extension φ' ⊵ φ (a new channel) with φ'(s1) ≠ φ'(s2); taking φ' = (φ, d) is one such
  channel, and its cost is the cost of computing/measuring d on-line within the resource
  policy R_t.

So: **d separates aliased states for the contract iff d is φ'-measurable-admissible for
some refinement φ' that distinguishes the pair; the price of the metric = the price of
the channel.** (OCM-checkable: register (φ, d, cost of evaluating d); the checker's
witness `witness_aliasing_metric.json` enumerates the fibre-constancy on finite 𝓢.)

## Assumption passes (A3)

- Remove i-decidability: irrelevant to the iff (measurability, not computability, is the
  axis); the conditional names admissibility, which at finite scope is decidable anyway.

## Residual claimed by HSG

The observation that "just add a metric" is not free — the T03 economy (channel cost) is
metric-choice discipline, matching HSG_DEFINITIONS §6 (no canonical metric; choice is a
registered parameter). No curvature vocabulary.
