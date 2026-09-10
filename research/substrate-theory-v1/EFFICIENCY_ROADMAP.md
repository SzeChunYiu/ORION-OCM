# Efficiency Roadmap v1 — better algorithms, not benchmark tricks

Principles: conditional (not fixed) search allocation; learned best-first policies with bounded complete fallback; cost-charged everything; parents before invention (GAP_MATRIX "not gaps").

## F-1 Failure receipts (do first — trivial, gates RSI)
Every failed/vanished candidate emits a receipt with class ∈ {semantic_invalid, inapplicable, bad_routing, insufficient_representation, verifier_rejection, resource_exhaustion, economic_harm}. Wire the dead ResidualKind (11 kinds, runtime/residuals.py) into live receipts; stop silent vanishing of inapplicable operators in compose_stage; ADD the missing economic_harm class. Parent: gradual contracts/blame.

## F-2 Miner score swap (root-cause fix)
Replace (support desc, length desc) ranking with post-application utility (P: Stitch/Babble). Our learnability condition (pairwise substring-disjoint motifs) becomes the degeneracy theorem: where motifs are disjoint, parent ≡ our cheap rank; outside, parent strictly dominates. Also: value-per-charge acquisition ranking (RL 4.2) prices arm creation.

## F-3 Learned serving router (closes NEG-I)
Stage 1: ledger-supervised initiation — train serving on the amortised-return logs that already exist post DEV-CAL-3/4 (RL 1.2; option-critic transposed). Stage 2: contextual bandit with cost-charged regret (EXP4/Thompson), delayed ecological reward, Z-features = fragment-support vector first, PSR probe vectors later (RL 2.1). Stage 3: sleeping-experts structure for the awake-set problem (SYNTH 7.2; KNS impossibility results are the policy-class ceiling — pre-register that ceiling). Bounded fallback: complete search retained at every step; the router reorders/prunes within budget only.

## F-4 Conditional allocation and probes
VoC serve rule (capital-amortised, capability-level; Russell-Wefald + Hay) gating every serve decision; EIG probe selection for discovery (EIG-for-coverage, not parameter precision); sequential-admission stopping (SPRT with ledger-derived asymmetric loss). CEGIS max-discriminating counterexample selection when verification fails.

## F-5 Consolidation and retirement
Wake-sleep: periodically re-mine over the receipt corpus, Ψ-calibration-preserving; retirement by prospective (Ψ-predicted) utility with W-preserving tombstones (Soar excision lesson: cost must include match cost); capital recycling = per-unit retire-and-refund market with conserved capital (the one import whose residue exceeds the economic wrapper); generative replay weighted by ledger return.

## F-6 Complexity remediations (from KSO audit)
- Admission O(n²) per admit → O(n³) cumulative: batch/incremental admission or meet-lattice indexing.
- Dedekind-exhaustive calibration 2^(2^n): cap + sample + register the approximation.
- Grammar search 4^L: pruning by utility estimate before enumeration (F-2 ranking).
- Exact PCST 2^12: fine; register the bound.

## F-7 Scale/vectorization (compute-fungibility)
Every arm must state its vectorizable-evaluation fraction; batch worlds per host; the ledger prices all of it (reuse-first machinery discipline).

## Non-goals
No threshold tuning to move metrics; no per-benchmark special cases; no capability claim without the full-chain ledger (full trade-chain PnL discipline transposed: gross edge > full cost).
