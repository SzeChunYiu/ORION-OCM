# R6 successor: operational genesis, disclosed assumptions, and limits

This additive repair follows the committed
[`FREEZE_V3.md`](../gmi-1068-recursive-audit-v3/FREEZE_V3.md), Round B.
The old R6 receipt remains historical. The current R6 round remains **OPEN**:
these results repair specified propositions and operational evidence, while R5
parent semantics and broader genesis/representation/learning claims are not
re-earned by a successful local checker. Proofs below are mathematical proofs;
they have not been verified by Lean. Finite checks do not replace their universal
quantifiers.

## 1. Effective search that survives a nonhalting candidate

Fix an effective enumeration of finite machine descriptions `e(0),e(1),...`, a
total computable **single-step** transition, finite initial configurations, and
independent resumable configurations. Initializing any one candidate must finish.
The scheduler's stage `m=0,1,...` initializes candidate `m`, then allocates one
step to every non-stopped candidate `k<=m`. A scheduled slot is counted even when
a previously stopped machine requires no execution. Evaluation must itself be
encoded in the candidate execution for this result to establish evaluation
coverage. Finite generation/dispatch overhead is not a constant-time claim.

**Theorem S (exact dispatch bound).** If candidate `k` halts after exactly `t>=1`
of its own transitions, it first halts at stage `k+t-1`. The number of scheduled
slots through stage `m` is `(m+1)(m+2)/2`. Nontermination of another candidate
does not alter either statement.

**Proof.** Candidate `k` receives no steps before stage `k`. After stage
`k+j`, it has received `j+1` steps, unless it stopped earlier. Induction on
`j=0,...,t-1` therefore gives its `t`-th step at `k+t-1`, with no earlier halt.
Stage `i` has `i+1` slots, whose sum for `i=0,...,m` is the stated triangular
number. Only a single total transition is requested in each slot, so a looping
candidate cannot block subsequent slots. QED.

The checker instantiates a looping first candidate and later halting machines.
The adversary `k=3,t=4` completes at stage 6, after 28 scheduled slots. It rejects
the false bound `max(k,t-1)=3`, serial execution and a scheduler that visits only
the newest candidate. The independent oracle restarts and replays each allotted
prefix using a separate dense-memory interpreter; it does not call the candidate
interpreter or scheduler.

This is conditional eventual coverage, not efficient search, discovery of a
useful candidate, proof of global nondominance, or successful evaluation of every
program. With an infinite registry, completed finite evaluations need not reveal
whether a better unevaluated program exists. Frontier admission additionally
requires a fixed comparison semantics and a declared tie/archive policy. None
of those conclusions is inferred from the finite scheduler fixture.

## 2. Every abstraction-cost regime

Let setup cost `D>=0`, inline cost `L>=0`, per-call cost `c>=0`, and integer
repetition count `n>=0` be measured in the same scalar units. Inlining costs
`nL`; reuse costs `D+nc`. This model presupposes equal task behavior and excludes
undeclared conversion, memory and execution costs.

**Theorem A.** Saving is `n(L-c)-D`. If `L>c`, reuse strictly wins exactly when
`n>D/(L-c)`, with first positive winning integer
`floor(D/(L-c))+1`. If `L=c`, reuse ties exactly when `D=0`, otherwise loses.
If `L<c`, reuse never strictly wins; it ties only at `n=0,D=0`.

**Proof.** Subtract the two costs. Division preserves the strict inequality
only when `L-c>0`; the floor formula is the smallest integer exceeding the
nonnegative quotient. For zero slope, saving is `-D`. For negative slope,
`n(L-c)<=0`, and equality requires `n=0`, then also `D=0`. QED.

In particular, `D=0,n=0` always ties. Reuse with `D=0,n>0` wins iff `L>c`.
The checker compares exact rational arithmetic against separately accumulated
inline/call costs across all three slope regimes, setup/repetition zero, and
ties. This scalar model does not prove R5's general multi-resource geometry.

## 3. Code modification with an actual interpreter

The declared RAM has unbounded integer-valued cells at nonnegative addresses,
initially zero outside its finite loaded description. Instructions are triples
`(opcode,a,b)`. Opcodes are HALT, STORE-immediate, COPY, ADD-immediate,
JNZ and OUT; the program counter advances by three unless a jump is taken.
An invalid opcode/address produces FAULT. A finite budget ending before HALT or
FAULT produces BUDGET_EXHAUSTED, never a conclusion about general divergence.
Code and data share memory. Fetch reads current memory on every step.

For depth `d>=1`, put `d` STORE instructions at positions `3j`, `0<=j<d`.
Each targets the immediate cell `3(j+1)+2` of the next instruction. The first
immediate is `v`; other initial immediates are arbitrary sentinels. At position
`3d`, STORE writes its immediate to a separate data cell beyond all code. OUT
reads that cell, followed by HALT. No primitive “meta” or “self-modify” opcode is
introduced.

**Theorem M (finite encoded modification towers).** For every finite `d>=1`
and integer `v`, this program halts in `d+3` transitions and emits exactly `v`.
When `d>=2`, an executed STORE modifies the instruction that subsequently
modifies another instruction.

**Proof.** At the start of step 1, the immediate of the first STORE is `v`.
If the STORE at position `3j` has immediate `v`, it writes `v` into the next
STORE's immediate and advances the counter to that instruction. It changes no
opcode or destination address. Induction gives immediate `v` for the STORE at
`3d`, which writes `v` to the non-code data cell. The next two instructions emit
that value and halt. There are `d+1` stores, one output, and one halt. The
first two code writes for `d>=2` establish the modifier-of-modifier claim. QED.

The operational receipt contains the complete depth-two trace. Independent
execution must match every fetched instruction and edit. A mutant interpreter
that fetches immutable initial code fails; changing the first modifier's literal
changes the final output. Thus this evidence goes beyond the V1 function
composition lemma. The theorem is about this encoded family. Arbitrary reflective
process closure additionally requires a semantics-preserving encoding/evaluator
for every proposed code transformer, well-formed outputs, and termination where
claimed. It does not follow from this fixture. Universality of the RAM,
automatic synthesis of modifiers, beneficial changes, validation of self-changes,
and open-ended capability improvement are not proved here.

## 4. Memory necessity without a finite-word extrapolation

The delay task demands output `0` at the first step and previous input thereafter
for **every finite binary input word**, with the output produced after receiving
the current input. The task definition and sequential interface are assumptions.

**Theorem D.** A deterministic zero-state map `f(current_input)` cannot solve the
task. A two-state transducer can; hence two distinguishable internal states are
necessary and sufficient in this deterministic sequential model.

**Proof.** Following histories `(0)` and `(1)`, append the same current input
`0`. Required next outputs are respectively `0` and `1`; a zero-state map
receives identical current input in both cases and cannot produce both. More
generally, the two histories cannot lead to the same internal state in a correct
deterministic transducer. For sufficiency, initialize state `q=0`, output `q`,
then assign `q=current_input`. Induction shows the state before every output
equals the preceding input, with the prescribed initial value. QED.

The 511 words of lengths 0 through 8 and all four stateless Boolean maps are
sanity checks. The proof does not infer all-length correctness from these words.
State names may be permuted; a unique named Mealy table is not a unique physical
architecture. Exhausting a supplied Mealy family is not architecture-blind
discovery. This successor supplies a task-dependent memory lower bound, not a
derivation of all learning systems.

## 5. What “prior-free” can and cannot mean

**Theorem P1 (binary indistinguishability).** Fix any finite history `h`. Let a
possibly randomized predictor output 1 with probability `p`. If the admissible
environment class contains deterministic computable extensions of `h` whose
next bits are respectively 0 and 1, its zero-one risks in these environments
are `p` and `1-p`. Its worst-case next-bit risk is at least `1/2`.

**Proof.** The environments produce the identical observed history, hence the
same predictor distribution. The two error probabilities sum to one; their
maximum is at least half. Fair random guessing attains this bound. For any fixed
finite `h`, both constant-tail extensions have finite program descriptions. QED.

This is a one-step result for the declared unrestricted extension class. It does
not prohibit useful generalization on structured task classes or statistical
guarantees under explicit distribution assumptions.

**Theorem P2 (no countable uniform probability).** No countably additive
probability on a countably infinite set of distinct candidates is invariant
under every permutation. **Proof.** Transpositions force every singleton to
have the same mass `c`. If `c=0`, their countable union has mass zero. If `c>0`,
a sufficiently large finite union has mass greater than one. Both contradict
normalization. QED.

**Theorem P3 (finite selection breaks full permutation symmetry).** A nonempty
finite selected subset of a countably infinite candidate set cannot be invariant
under every permutation. **Proof.** Transpose a selected and an unselected
candidate. The subset changes. QED.

These elementary proofs establish the stated obstructions directly; they are
not claimed as new theorems. A viable blank-machine programme can remove
pretraining and known-family templates while **disclosing** the language,
encoding, primitives, scheduler, task distribution, objective, feedback,
comparison/tie convention and resource budget. This implementation's synthetic
program generator is deliberately a test fixture, not evidence that every
architecture-specific prior has been eliminated from a learned search system.
The machine-readable ledger records the remaining assumptions.

Universal encodability alone cannot select a unique architecture: for example,
adding an unused register preserves behavior while changing structure. A unique
design requires additional equivalence, cost and tie assumptions. The minimax
obstruction also does not disappear when the predictor is called “GMI”.

## 6. Primary literature and exact import boundaries

All links below were checked against the primary document for this repair.
These are literature constraints and parent results, not GMI empirical findings.

| Primary source | Scoped finding used |
|---|---|
| [Wolpert & Macready (1997), No Free Lunch Theorems for Optimization](https://www.cs.ubc.ca/~hutter/earg/papers07/00585893.pdf) | Theorem 1 concerns finite search/output spaces and performance from distinct evaluations, averaged uniformly over all objective functions. It does not imply every real task is equally hard, or forbid useful restricted classes. |
| [Solomonoff (1964), A Formal Theory of Inductive Inference, Part I](https://raysolomonoff.com/publications/1964pt1.pdf) | Algorithmic induction uses a chosen description language/machine. Universal programme weighting is not a uniform probability on all hypotheses. |
| [Hutter (2005), Universal Artificial Intelligence, author's exposition](https://hutter1.net/ai/uaibook.htm) | AIXI combines sequential reward maximization with algorithmic environment weighting. Its displayed construction fixes action/percept spaces, machine and lifetime; this is not absence of assumptions. |
| [Legg & Hutter (2007), Universal Intelligence](https://arxiv.org/pdf/0712.3329) | The intelligence measure aggregates reward over computable environments weighted by description complexity. Such representation breadth does not derive the internals of each machine family. |
| [Leike & Hutter (2015), Bad Universal Priors and Notions of Optimality](https://arxiv.org/pdf/1510.04931) | Under finite actions/percepts, rewards in [0,1], and summable nonnegative discounting, Theorem 7 constructs dogmatic universal mixtures favoring a given computable policy under its stated positive-value condition. Theorem 18 shows Pareto optimality is non-discriminating for the broad environment class considered. UTM dependence cannot simply be dropped. |
| [Lattimore & Hutter (2011), Asymptotically Optimal Agents](https://arxiv.org/pdf/1107.5537) | Theorem 8, for all deterministic computable environments and computable discounting, excludes strong asymptotic optimality and deterministic computable weak optimality. Its second part explicitly does not exclude stochastic computable policies. We do not extend its no-go beyond these hypotheses. |
| [Schmidhuber (2006 version), Gödel Machines](https://arxiv.org/pdf/cs/0309048) | Theorem 4.1 is relative to encoded utility, formal system and the alternative of continuing proof search. Its code-rewrite framework imports hardware/environment axioms. Our encoded store examples prove neither that theorem nor that every beneficial change is discoverable. |
| [Tarski (1955), A lattice-theoretical fixpoint theorem and its applications](https://msp.org/pjm/1955/5-2/pjm-v5-n2-p11-s.pdf) | Theorem 1 gives a complete lattice of fixed points for a monotone map on a complete lattice. It does not supply finite termination, semantic truth, or a complete intelligence theory. |

For a frozen finite universe `U`, an inflationary monotone map on its powerset
stabilizes after at most `|U|-|S0|` strict additions from `S0`; this follows by
counting newly added elements. The limit is closure relative to `U` and that map.
For contrast, `F(S)=S union {0} union {n+1:n in S}` on subsets of the natural numbers is
monotone and inflationary, and its iteration from the empty set is `S_m={0,...,m-1}`: no finite
stage is fixed. Thus no fixed-point terminology permits promotion from a finite
R0–R17 registry audit to absence of unknown gaps or explanation of all AI.

## 7. Reproduction and evidence level

Run `python3 -I -B check_r6_v2.py` (or supply its full path). Imports resolve
explicitly to reviewed sibling files. Default mode recomputes all operational evidence,
checks historical parent hashes, and rejects any mismatch with `RESULT_V2.json`.
`--write` is the explicit receipt-generation operation. The receipt hashes the
actual source/ledger/theory inputs, excluding itself. It does not self-embed a
commit hash; an external merge receipt should bind its bytes to a git head.

Remaining obligations include proof-assistant verification of the paper proofs,
independent re-earning of R4/R5 and descendant dependencies, full cost accounting,
task-distribution and evaluator validity, finite-resource useful discovery,
validated beneficial self-modification, and empirical evidence beyond fixtures.
