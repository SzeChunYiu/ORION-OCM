# Interactive cut scope and exact strategic comparisons

Date: 2026-09-13. Base: `main@2d65cb11d7f4880ff8f3a4fc41511d2f2e626814`.

This additive audit corrects transfers of SC-1 into distributed, strategic and
proof-search interfaces, and propagates the operational theorem's exact-number
assumptions to the strategic frontier. It preserves SC-1 and the original
finite XOR, composition, proof and integer-game receipts.

## 1. The one-way information pattern is a theorem hypothesis

SC-1 proves the exact minimum complete message alphabet for
`c:X -> Z`, `d:Z x Y -> A`. In particular the sender's message is a function of
its registered information `X`, and the downstream side information `Y` does
not reach that sender through undeclared feedback. The old distributed GG26
and strategic GG42 wording transferred the initial one-way hypergraph to
arbitrary exchanged messages and distributed protocols without this condition.

**IC-1 counterexample (classical INDEX).** Alice receives a binary word of
length `n`; Bob receives an index in `{0,...,n-1}` and must return the indexed
bit. Every two distinct words differ at some index, so the original exact
function conflict graph is complete on `2^n` vertices. Its chromatic number is
`2^n`, giving the one-way lower bound of `n` fixed bits; sending the word
attains it. This argument quantifies over every one-way encoder, not a sampled
family of encoders.

An interactive construction lets Bob first transmit the index using
`ceil(log2 n)` bits and Alice reply with the selected bit. For `n=4`, this is
three total bits versus four one-way bits. The eight possible complete
interactive transcripts depend on both inputs; they are not a coloring
`c(x)` of the original 16-word graph. For a fixed received index the remaining
response has just two classes. Its graph is complete bipartite, admits the
two-coloring `x -> x_y`, and has an edge, so the later one-way minimum is
exactly two symbols. Retyping the later cut therefore agrees with SC-1.

The repaired statements retain the exact bound for classical deterministic
one-way interfaces. They require a new information/obligation registration at
a later cut after feedback, or a separate proof for the full interactive
protocol. This does not claim that every task benefits from interaction, or
that the displayed interactive construction is optimal among all protocols.

**IC-2 resource typing.** A binary carrier reused `n` times has a per-use
alphabet of two and a complete fixed-length transcript alphabet of `2^n`.
SC-1 bounds the complete message. It does not require every physical channel
use to carry the entire message alphabet. The corrected GG26 and GP3 make
this distinction explicit; protocol timing/length information must also be
counted if a different variable-length contract makes it observable.

## 2. Finite strategic enumeration needs decidable arithmetic

**IC-3 (propagated FOC arithmetic boundary).** A finite terminating strategy
register and finite ecology/deviation coordinate registers reduce the
strategic calculation to finitely many evaluations and comparisons. Those
evaluations must be effective, and all required equality/order predicates
must be decidable in the declared number representation. Exact rational
profiles meet these conditions. Finiteness alone does not supply them, and an
infinite enumerable strategy set does not supply finite exhaustion.

For a one-player game with constant other capability/resource coordinates,
let the two action losses be `0,x_P`, where `x_P` is
`2^{-t}` if program P first halts at step `t>=1` and zero otherwise. Simulating
P for `m` steps gives an approximation within `2^{-m}`: use the observed exact
value if P halted, otherwise zero. Thus these reals are uniformly computable.
Action 1 has regret vector `(x_P,0)` while action 0 has `(0,-x_P)`. The actions
tie and both have zero regret iff P never halts; otherwise action 1 has
positive regret and is strictly dominated. A uniform exact classifier would
decide nonhalting. This analytic reduction, also used in the finite operational
theorem §7, establishes the boundary; finite simulation cannot prove it.

The corrected strategic GG43 / ledger GG-S5 now states the finite registers,
effective evaluations and total exact comparison procedures. Its finite
algorithm evaluates all profiles and unilateral deviations and removes every
dominated profile by pairwise comparison. No arbitrary computable-real solver
is inferred from the old integer-game census.

## 3. Exact executable evidence

`grand_gmi_interactive_cut_scope_checks_v1.py` prints one JSON receipt with no
arguments, external data or random seed. The frozen result is
`GRAND_GMI_INTERACTIVE_CUT_SCOPE_RECEIPT_V1.json`; its companion test is
`test_grand_gmi_interactive_cut_scope_v1.py`.

- INDEX `n=1..8`: 43,435 original distinct-word pairs all conflict; the
  feedback construction succeeds on all 3,586 input/index pairs. At all 36
  conditioned index cuts, an explicit binary coloring separates every one of
  167,481 checked conflicting pairs and a nonempty edge establishes necessity.
- INDEX `n=1,2`: all 359 encoders over alphabets up to `2^n` are checked by
  independently constructing their decoder cells. Feasibility agrees with
  injectivity; exactly 2 encoders succeed for `n=1`, and 24 for `n=2`.
- 150 two-/three-action rational games: zero-regret and nondominated actions
  agree with the scalar-loss argmin; 40 games retain tied optima. Three tiny
  positive-vs-zero cases, including `2^-2048`, remain strictly positive under
  exact arithmetic; the exact zero case retains both actions.

These are finite checks of the declared constructions and boundary witnesses,
not an exhaustive census of interactive protocols or a new communication
complexity result. The historical receipts remain historical evidence for
their original one-way and integer-arithmetic examples.

## 4. Claim identifier collision

The reference audit found that both the strategic source and
`QUANTUM_PROCESS_INSTANTIATION_THEOREM_V1.md` use historical IDs GG42–GG45.
They do not identify the same claims. Use source-qualified IDs, or the
strategic ledger's existing distinct IDs, when referring across documents:

| Source-qualified ID | Strategic claim | Existing strategic ledger reference |
|---|---|---|
| `strategic:GG42` | one-way strategic cut transfer | GG-S4 |
| `strategic:GG43` | exact finite strategic frontier | GG-S5 |
| `strategic:GG44` | ecology-robust equilibrium can be empty | GG-S6 |
| `strategic:GG45` | cooperative process specialization | source §7 |

The corresponding quantum source IDs concern instantiation, response
quotients, process-relative cut capacity and impossibility transport. This
iteration adds a qualification note to the strategic source and ledger. It
does not renumber historical receipts or claim a global reference migration.

## 5. Source and novelty boundary

The INDEX problem and its one-way/interactive separation are parent
communication-complexity theory. [Tim Roughgarden's Lecture 2, §4
(2015)](https://timroughgarden.org/w15/l/l2.pdf) explicitly describes the
sender's one-way information restriction, the INDEX lower-bound argument and
the feedback construction. Our exact four-bit witness is a finite
specialization with Bob as the designated output party, so his receiving the
one-bit reply is included in the three-bit total.

For the broader distinction, [Briët, Buhrman, Leung, Piovesan and Speelman,
*Round elimination in exact communication complexity*
(2018)](https://arxiv.org/html/1812.09290v1) separates one-round and multiple-round
protocols. Its promise-equality round-elimination result also illustrates why
an interaction advantage must not be asserted for every task. The correction
uses the self-contained INDEX proof above; no quantum conclusion is inferred.

The strategic arithmetic obstruction is the operational theorem's existing
computable-real halting reduction specialized to regret. The residual work
here is correcting theorem-transfer hypotheses and exposing hostile examples
that the previous receipts did not cover. It supplies no empirical gate
closure, unrestricted solver, or claim that all Grand-GMI gaps are closed.
