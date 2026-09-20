# R2 — context/value irreducibility

## Context

Given a substrate-relative process category C_S, a context kappa supplies an externally declared observation/evaluation map

nu_kappa : Hist(C_S) -> W_kappa

(partial where evaluation is not defined), with W_kappa carrying at least a preorder <=_kappa.

Utility, pass/fail acceptance, viability, vector resource burden, confidence objects and Pareto coordinates are special choices of W_kappa and its order. They are not separate universal GMI primitives.

## Theorem R2-1 — process law does not determine value/context

Take one state *, two actions a0,a1, and identical deterministic self-loop transition dynamics for both actions.

Define contexts
k0(a0)=1, k0(a1)=0
k1(a0)=0, k1(a1)=1.

The process reduct is byte-for-byte the same while the selected action reverses. Therefore no theorem of the process reduct alone can define a unique context/value ordering across both valid expansions.

This is the general model-theoretic form of the finite #929/AJ7 witness.

## Theorem R2-2 — context does not determine process possibility

Hold a context fixed. Let C0 contain only identity reachability on {0,1}. Let C1 additionally admit 0->1. The context values states identically in both models, yet attainability differs. Hence context alone cannot reconstruct the substrate-admitted process sets.

## Corollary — two independent axes

At the declared scope, process possibility and contextual evaluation are mutually non-derivable without extra assumptions.

This is a non-uniqueness theorem, not a claim that physics and values can never be correlated in a richer scientific model.

## Scalarization boundary

Let result vectors be ordered coordinatewise. Any positive-weight linear scalarization is monotone on already-dominating pairs, but it does not preserve the incomparability relation: p=(1,0) and q=(0,1) are incomparable, while weights (2,1) prefer p and weights (1,2) prefer q.

Thus a scalar preference over an entire Pareto set imports extra contextual information.

## Universal intelligence scalar boundary

Any aggregation of performance across multiple contexts requires a measure/weighting over those contexts. That measure is not supplied by process law. Legg-Hutter universal intelligence is therefore a comparison specialization that supplies an algorithmic environment weighting; it is not a uniquely forced scalar of the minimal GMI core.

## Parent ownership

Decision theory, utility theory, Pareto order, reward ambiguity and Legg-Hutter environment-weighted intelligence remain parent mathematics. GMI's residual is the explicit placement of their assumptions on the context branch of the fixed-point candidate and the process/context non-derivability theorem schema.

## Claim ceiling

GRAND_GMI_V2_R2_PROCESS_CONTEXT_MUTUAL_NONDERIVABILITY_AND_CONTEXT_FORMALIZATION_AT_REGISTERED_SCOPE
