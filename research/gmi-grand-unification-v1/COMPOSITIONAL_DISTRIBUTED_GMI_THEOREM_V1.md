# Grand GMI Compositional and Distributed Theorem V1

Status: **THEOREM WITH FACTORIZATION CONDITIONS + EXACT HOSTILE WITNESSES**  
Date: 2026-09-12

## 1. Multi-agent systems are not a new semantic primitive

A finite distributed machine consists of local process states, local observations/actions, and communication channels. Let

\[
M_{team}=(M_1,\ldots,M_n, C_1,\ldots,C_k).
\]

The product of local states plus channel/buffer state is itself one legal process state. Therefore the distributed network can be unfolded into a single centralized process `Cent(M_team)` that reproduces the same external intervention/observation trace.

**GG25 — team-centralization theorem.** Every finite synchronous distributed GMI machine has an externally trace-equivalent centralized realization obtained by product-state compilation.

The converse is not resource-neutral: a centralized realization may use communication or shared state unavailable to the distributed team. Thus "multi-agent intelligence" is semantically ordinary GMI plus explicit internal cut/resource constraints.

## 2. Internal communication is a semantic cut

Partition a team into subsystems `A | B` and register their information at the
boundary. A classical deterministic one-way interface has the SC-1 form
`c:X -> Z`, `d:Z x Y -> A_out`: the complete forward message depends only on
the registered sender information `X`, and the receiver uses that message and
its registered side information `Y`. Under these hypotheses the minimum
zero-error message alphabet is the obligation-relative hypergraph chromatic
number `chi(H_C)`.

**GG26 — distributed one-way semantic-cut theorem.** A distributed interface
with this registered one-way information pattern inherits SC-1 exactly.
The alphabet counts the **complete encoded message**, or the full forward
transcript when several transmissions implement that one-way message. It does
not count just the carrier alphabet of one use of a reusable channel.

Feedback can change the sender's information, so the hypergraph constructed
before feedback does not automatically lower-bound an interactive protocol.
At a later one-way boundary, register the actual sender/receiver information,
compatible states and remaining obligation again. Apply SC-1 only if the
resulting interface satisfies its one-way factorization. A lower bound on a
whole interactive protocol needs a proof for that protocol class; adding up
unconditioned one-way bounds does not supply one.

**Exact feedback counterexample.** Alice holds `x in {0,1}^4`, Bob holds
`y in {0,1,2,3}`, and Bob must return `x_y`. Before communication any two
distinct words conflict at an index where they differ. The one-way graph is
`K_16`, so Alice's one-way message needs 16 symbols, or four fixed bits.
Instead Bob can send his two-bit index, then Alice can reply with the selected
bit. All 64 input pairs succeed using three total bits and two forward reply
symbols. The reply is now `c(x,y)`, not `c(x)`. Conditional on the received
index, the remaining binary response has a two-class cut, in agreement with
SC-1. The classical INDEX separation is reviewed in [Roughgarden, Lecture 2,
§4](https://timroughgarden.org/w15/l/l2.pdf); the bounded witness and correction
scope are in `INTERACTIVE_CUT_SCOPE_CORRECTION_V1.md`.

Witness: Alice sees `x`, Bob sees `y`, and Bob must output `x XOR y`. Exhaustive deterministic one-way enumeration finds:

- one message symbol: 4 decoder protocols, 0 succeed;
- two message symbols: 64 encoder/decoder protocols, 2 succeed.

Hence exactly one communicated bit is necessary and sufficient.

## 3. Product-obligation tensorization

Suppose two GMI problems are genuinely independent:

- ecology `E = E1 x E2`;
- state/input/action/output spaces factor;
- obligation is the conjunction/product `Omega = Omega1 x Omega2`;
- feasible machines are exactly products `M1 x M2` (no cross-coupling channel);
- registered capability/resource coordinates are retained as separate component coordinates.

Then the attainable set factorizes:

\[
\mathcal A_{12}=\mathcal A_1\times\mathcal A_2.
\]

Because dominance is coordinatewise on the concatenated coordinates,

\[
\boxed{\operatorname{Pareto}(\mathcal A_1\times\mathcal A_2)
=\operatorname{Pareto}(\mathcal A_1)\times\operatorname{Pareto}(\mathcal A_2).}
\]

**GG27 — frontier tensorization theorem.** Independent obligations with independent feasible process classes and separately retained resource coordinates have an exactly factorized frontier.

The exact checker exhausts every pair of nonempty subsets of the binary two-coordinate grid: 225/225 set pairs satisfy the identity.

## 4. Semantic width tensorization for exact independent outputs

For a no-side-information exact function obligation `f_i:X_i -> A_i`, the minimum cut message alphabet is the number of distinct required outputs `|im f_i|`. For the product obligation `(f1,f2)`, distinct output pairs form the Cartesian product, so

\[
\boxed{m_{12}=m_1m_2.}
\]

Therefore required log-alphabet width adds:

\[
\log m_{12}=\log m_1+\log m_2.
\]

The checker exhausts all 27 ternary functions on a three-element domain against all 27 partners: 729/729 product pairs obey exact multiplicativity.

**GG28 — independent semantic-width tensorization.** Independent exact output obligations multiply message alphabets and add log-width.

## 5. Coupled obligations break tensorization

The factorization hypotheses are load-bearing. With two hidden bits, requiring the pair `(x1,x2)` needs four exact messages across a no-side-information cut. Replacing that product obligation by the coupled obligation `x1 XOR x2` needs only two messages.

Thus the ontology cannot infer modularity from variable decomposition alone. Modularity is derived only when **ecology, obligation, feasible process coupling and resource coordinates all factor at the declared level**.

## 6. Centralization witness

A two-agent finite process with one-bit local states and a one-bit message is compiled into one product-state machine. Across all four initial local states and every binary external-input sequence through length six, distributed and centralized machines have identical states and external outputs: 508 exact trace checks.

This demonstrates the theorem's semantic part while leaving communication/resource accounting explicit.

## 7. Architectural consequences

Under exact factorization, separate modules can be frontier-optimal without any architecture prior. Under coupled obligations, shared representations, messages, attention, global memory or joint computation can become necessary or resource-improving. Therefore Grand GMI predicts **when modularity is licensed and when cross-module integration is structurally required**.

A society of agents, MoE routing system, distributed controller, multi-robot team, federated learner or modular neural system is not a separate intelligence category. Each is a process network whose internal cuts and local transformations carry obligation-relative lower bounds.

## 8. Boundaries

This tranche does not claim:

- that arbitrary interacting frontiers tensorize;
- that communication complexity is always additive;
- that centralization preserves physical cost/privacy/latency;
- that every multi-agent equilibrium is globally optimal;
- that social goals reduce to individual goals.

Those require the coupling structure to be declared, not guessed.
