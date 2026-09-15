# Body–environment sufficient-state and reduction theorem v1

## Scope and boundary

An extended system is

\[
Z=A\times W,qquad
o_t=O(W_t),quad a_t=\pi(A_t,o_t),quad
(A_{t+1},W_{t+1})=T(A_t,W_t,a_t,i_t).
\]

Here \(A\) is agent-owned state, \(W\) environment-owned state, \(O\) the
allowed observation/read channel, \(T\) the joint agent/world transition, and
\(i_t\) a registered future intervention. Custody/reset authority and internal
bits, external bits, reads, writes, world operations, latency, and energy are
separate coordinates. This explicit boundary is machine-readable in
`STATE_BOUNDARY_SCHEMA_V1.json`.

Two joint states are future-trace equivalent when every registered future
intervention sequence produces the same protected output trace. The minimal
sufficient cognitive carrier is the quotient by this equivalence—not whatever
the evaluator happens to call “inside.”

## Theorem EC-1 — exact external-state necessity condition

External state is necessary relative to the projection \(p(A,W)=A\) iff there
exist reachable \((A,W_0),(A,W_1)\) with the same currently admitted ordinary
observation but different protected future traces under some common future
intervention.

**Proof.** If such a pair exists, every function of \(A\) (and the equal current
observation) maps them to one carrier value, yet obligation-sufficient state must
distinguish their different future traces: contradiction. Conversely, if no such
pair exists, future trace is constant on each fiber of the projection, so it
factors through \(A\); the agent projection is sufficient. ∎

This is a necessary-and-sufficient, boundary-relative statement. Merely being
physically outside the body is neither necessary nor sufficient.

## Theorem EC-2 — finite reduction to memory and dynamics

When \(W\) is finite/effectively encodable and the parent receives matched
read/write and transition primitives, compile

\[
(A,W)\mapsto A'=A\times W.
\]

External read/write becomes ordinary D2 read/write on the second component and
the joint transition becomes one D6 transition. Induction on time gives identical
protected traces. Total state information is unchanged (only location/custody is
relabeled); with matched primitives read/write counts are unchanged. Thus the
finite system reduces exactly to D2/D6 under the registered total-state burden.

This is CR-7 from
`GMI_CLASSICAL_DOMAIN_REDUCTION_COMPLETION_V3.md` made executable. If a parent
is denied environmental bandwidth, storage, or world dynamics available to the
candidate, any separation is a primitive/resource mismatch and must be reported
on that coordinate—not as semantic domain novelty.

## Exact predicted ecology

The frozen `DELAYED_EXTERNAL_BIT` ecology has two histories. At STORE, input
bit \(b\) is written to one environmental mark; the agent has zero internal
bits. DISTRACT makes the agent state and ordinary observation identical. At
QUERY, the extended arm may read the mark and must output \(b\).

Predictions:

1. extended arm: capability 1;
2. any deterministic zero-bit agent-only arm: capability at most \(1/2\);
3. erase-write negative twin: capability \(1/2\);
4. matched one-bit D2 memory parent: capability 1 with the same two answers.

The two stored histories collide under the agent-only projection and separate in
future response, so EC-1 makes the environmental bit irreducible **within the
frozen zero-internal-bit boundary**. Exhausting both deterministic functions on a
singleton carrier proves the \(1/2\) bound. Moving the bit inside constructs the
exact D2/D6 reduction of EC-2.

## Disposition

The ecology prediction is fully positive, including its negative twin, while the
domain-novelty result is negative: the external carrier is necessary relative to
the restricted body boundary but absorbed by ordinary memory/dynamics under a
matched comparison. Analog, unbounded, or physically advantaged substrates
remain open.
