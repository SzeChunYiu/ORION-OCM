# F4 real-regime replication v1

## Scope

This capsule tests the already-merged development-only capability predictor against four executable task verifiers. The task labels are descriptive only; predictor input remains the same five architecture-name-free signed margins.

## Common rule

For a task requirement `r` and available resource `c`, define the signed margin `m = c-r`. Every registered task is constructed so exact success is equivalent to the relevant registered capability predicate. Therefore a threshold-crossing twin changes one load-bearing margin from `0` to `-1` and leaves the remaining margins unchanged.

This is a bounded realization theorem, not a universal claim about every code, proof, science, or control task.

## R1 — factual/science retrieval

The protected fact set contains four exact entries. The task requires returning all four with no external lookup. With four retained slots (`memory_margin = 0`) all entries are returned exactly. With only three (`memory_margin = -1`) the registered obligation cannot be represented without an unregistered external channel. Thus executable success iff `memory_margin >= 0`, matching `memory_exact`.

## R2 — math/proof chain

The proof certificate is a four-transition equality chain for the finite theorem instance `1+3+5+7 = 4^2`, with two live proof items required during traversal. The verifier checks equality preservation across the full chain. The registered positive case supplies the exact live-state and planning-depth requirements. Reducing planning depth by one makes the final transition unreachable; reducing live state by one also invalidates the proof protocol. Thus the registered positive/twin pair matches the conjunction defining `planning_exact`.

## R3 — code patch verification

Three executable implementations of `clamp` are frozen, together with four tests spanning below-range, in-range, above-range, and degenerate bounds. Exactly one implementation passes all four tests. The task obligation is to certify the unique correct patch, so every candidate must be routed and every frozen test must be checked. The positive case meets both routing and verification requirements. Its twin removes one verification unit and therefore cannot certify the registered obligation. This matches `verified_tool_exact`.

## R4 — sensor/actuator control

A remote actuator must distinguish four hidden plant modes and emit the unique stabilizing command for each. With four communication symbols the encoder/decoder is injective and all modes are controlled exactly. With three symbols, pigeonhole forces two modes to share a message and the receiver cannot emit both distinct required commands. Hence exact control iff `communication_margin >= 0`, matching `coordination_exact`.

## Negative-twin theorem

For each row, the twin changes exactly one load-bearing signed margin from `0` to `-1`. All other registered margins are identical. Because the executable verifier's success condition is exactly the corresponding capability predicate, each positive case must return `1` and each twin `0`. Any disagreement falsifies this capsule at its stated scope.

## Claim boundary

The evidence is P2 executable replication and the claim ceiling is G3. Hidden external memory, uncharged tests, alternative communication channels, compensatory morphology changes, or task-specific shortcuts invalidate the reduction and are explicit out-of-scope counterexamples rather than evidence for a broader G6 claim.
