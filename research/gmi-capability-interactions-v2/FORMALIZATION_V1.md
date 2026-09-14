# Capability interaction laws — tranche 2

Scope: finite exact microscopes for issue #602 F3 rows 5–9. Evidence classes P1/P2. Claim ceiling **G2**.

## Communication × teaching

If the learner begins in at most `P` prior-equivalence classes and the full teaching transcript has at most `K` distinguishable values, then the learner's post-teaching decision state contains at most `P K` prior/transcript cells. This is immediate from Cartesian-product cardinality. Exact teaching of more than `PK` pairwise obligation-distinct lesson states is impossible without extra information; injective coding makes the bound tight when the required cells fit.

## Teaching × cultural accumulation

Let the current repertoire contain `R` distinct useful items. Teaching transmits at most `K` existing items exactly and the learner discovers `B` genuinely novel items. Under itemwise, duplication-free retention,

`R_next = min(R, K) + B`.

Therefore strict accumulation occurs iff

`B > max(0, R-K)`.

Transmission loss must first be repaid by rediscovery before the repertoire can exceed its previous size. Compression and compositional teaching are deliberately outside this itemwise theorem.

## Metacognition × resource allocation

Consider optional computations with registered expected values of computation `e_i`, identical unit costs, additive net gains, and budget for at most `k` operations. Any optimal allocation contains the `k` largest positive `e_i` values, or all positive values when fewer than `k` exist.

Exchange proof: if a selected operation has smaller EVC than an unselected positive one, swapping them strictly increases total EVC. Any nonpositive selected operation can be removed without decreasing value. Scarcity is load-bearing; if every positive operation can be funded, ranking no longer changes the chosen set.

## Causal model × planning

For each latent world `w`, let `A*(w)` be its set of optimal interventions under the exact action-value vector. A registered model representation partitions worlds into classes `C` that the planner cannot distinguish.

**Planning-sufficiency theorem.** A class-conditioned exact planner exists iff for every model class `C`,

`intersection_{w in C} A*(w) != empty`.

Necessity: one action must be chosen for the entire class, so that action must be optimal in every compatible world. Sufficiency: choose any action in the nonempty intersection. This isolates the precise failure mode of observational aliasing: aliasing matters only when it merges worlds whose optimal intervention sets have empty intersection.

## Tool routing × verification

Let the router emit an ordered proposal list and let verification budget `q` inspect only the first `q` proposals. Let `V` be the verifier's accepted inspected proposals and `C` the actually correct proposals.

Guaranteed safe success requires both:

1. soundness on the inspected prefix: `V subseteq C`;
2. verified coverage: `V intersect C` is nonempty.

If either fails, the result is respectively unsafe or unsolved. Proposals routed beyond `q` cannot affect the guarantee unless routing changes the verified prefix. The zero-budget twin therefore yields no safe adoption regardless of router breadth.

## Parent subtraction

The five laws are direct bounded consequences of finite communication complexity, cultural-retention recurrence, equal-cost rational metareasoning, decision-theoretic sufficiency of interventional state, and bounded verification. The contribution at this tranche is their architecture-independent registration with explicit load-bearing assumptions, twins and falsifiers, not a novelty claim over those parent theories.
