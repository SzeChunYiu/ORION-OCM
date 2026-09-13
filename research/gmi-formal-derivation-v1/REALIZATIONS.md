# Constructive realizations and computational boundaries

Status: exact finite compilation results, plus a computability boundary.
The input is a learned or supplied finite behavior from REP1/SD1. Additional
operations and encodings are explicit members of AX3's realization class.

## REAL1: tables, branching programs, trees and symbolic machines

Let a total Mealy machine have \(n\ge1\) states, \(a\ge1\) input symbols,
\(b\ge1\) output symbols, root \(q_0\), transition \(d(i,j)\), and output
\(o(i,j)\). Its complete behavior is specified by \(na\) table entries.
A table interpreter reads the entry indexed by its retained state and current
input, emits \(o(i,j)\), and stores \(d(i,j)\). Induction proves its state
and output coincide with the abstract machine at every step.

With fixed-width codes, the table data need
\(na(\lceil\log_2n\rceil+\lceil\log_2b\rceil)\) bits, retained state
\(\lceil\log_2n\rceil\) bits, and input code \(\lceil\log_2a\rceil\)
bits. A singleton coordinate can use zero bits because its only value is
implicit. Interpreter, addressing, allocation and interface overhead are extra;
constant-time random access is a machine assumption, not a theorem of GMI.

A branching program instead tests the state and input code, with a leaf for
each pair returning the same next state/output. A full binary decision tree
on \(k=\lceil\log_2n\rceil+\lceil\log_2a\rceil\) bits has at most
\(2^k\) leaves and \(2^k-1\) internal tests; unused codes get an explicit
default/error leaf. Reuse this finite tree every step with a state register.
For a fixed horizon \(H\), unroll into an input tree with
\(\sum_{t=0}^{H-1}a^t\) internal nodes and \(a^H\) leaves, attaching the
machine's output to each edge. Induction on depth proves exact agreement
through \(H\). A finite unrolled tree is not an infinite-horizon machine.

Symbolic rules \((q=i,x=j)\Rightarrow(y=o(i,j),q'=d(i,j))\), with an
exact rule interpreter and exactly one matching rule, are another realization.
Binary Boolean circuits follow by equality tests for each encoded pair,
AND gates for pair indicators and OR gates for each output/next-state bit.
Every realization needs an admitted storage and execution substrate. These
constructions derive implementations from a finite transition law; they do not
derive a unique representational syntax from probability normalization.

## REAL2: explicit threshold and ReLU recurrent neural embedding

Encode state \(i\) as one-hot \(s=e_i\in\{0,1\}^n\), input \(j\) as
one-hot \(x=e_j\in\{0,1\}^a\), and output as \(y=e_{o(i,j)}\).
For every state/input pair create one hidden ReLU unit
\[
z_{ij}=\operatorname{ReLU}(s_i+x_j-1).
\]
Then use a linear readout
\[
s'_k=\sum_{(i,j):d(i,j)=k}z_{ij},\qquad
y_\ell=\sum_{(i,j):o(i,j)=\ell}z_{ij}.                 \tag{NN}
\]
**Theorem.** Starting at \(s=e_{q_0}\), this recurrent block produces
exactly the Mealy machine's output stream on every encoded input stream.
**Proof.** For one-hot \(s,x\), exactly one pair has sum two; its unit is
one. Every other sum is at most one and its unit is zero. Each readout
therefore selects exactly the indicated next-state and output basis vector.
The state remains one-hot. Induction repeats the argument at every step,
establishing exact equality of all finite prefixes and thus infinite streams.

Counts for this sparse two-layer block: \(na\) hidden units, \(n+b\)
readout coordinates, \(2na\) input-to-hidden weighted edges, \(na\)
hidden biases, and \(2na\) hidden-to-readout weighted edges. All nonzero
edge weights are one and every hidden bias is minus one. There are \(n\)
retained state coordinates. Counts include neither input encoding/output
decoding, readout accumulation work, registers nor scheduling. If a uniform
activation convention requires ReLU on readouts, adding it changes nothing on
this nonnegative domain. Unrolling \(H\) recurrent steps gives \(H\) copies
of the block; weight sharing and stored parameters are different resource
coordinates. The threshold variant uses
\(z_{ij}=1\{s_i+x_j\ge3/2\}\) with the same readouts.

This is exact on the finite one-hot domain, including the invariant generated
by the recurrent block; no claim is made for arbitrary real inputs, floating
perturbations, continuous physical dynamics, efficient training, or desirable
generalization. It requires exact enough arithmetic for these finite integer
operations. Noise robustness needs a separate margin and propagation proof.
The construction compiles a known table, so backpropagation is not part of its
proof. Acquiring that table through SD1 yields an actual learned network
behavior, while all acquisition and compilation costs remain charged.

## REAL3: stochastic tables and Bayesian filtering

For finite controlled state, a supplied rational kernel
\(K(y,s'\mid s,a)\) has a finite exact stochastic-table implementation if
independent unbiased random bits and terminating rational sampling are admitted.
For a row choose integer denominator \(D\); use
\(k=\lceil\log_2D\rceil\) bits to draw \(J\in\{0,\ldots,2^k-1\}\),
reject \(J\ge D\), and partition accepted integers into numerator-sized
outcome intervals. Acceptance probability exceeds \(1/2\) unless \(D=1\),
which needs no draw. Independent retries terminate almost surely, with fewer
than two expected trials. Draw count is unbounded, so this is not a fixed
worst-case-time sampler. Arbitrary real probabilities require an additional
effective sampling representation and may not be computable.

For Bayesian state, add a supplied finite hidden-state model: prior \(b_0\),
controlled transition \(T_a(j\mid i)\), and emission \(O_a(y\mid j)\)
after the transition. Define
\[
\bar b_j=\sum_i b_iT_a(j\mid i),\quad
Z=\sum_jO_a(y\mid j)\bar b_j,\quad
b'_j=O_a(y\mid j)\bar b_j/Z \quad(Z>0).
\]
**Derivation.** Conditional total probability gives \(\bar b_j\).
The observation/state joint probability is \(O_a(y\mid j)\bar b_j\);
normalizing by its sum gives the conditional hidden-state law. Induction
maintains the posterior. Integrating the next controlled law against this
posterior shows that it is a predictive sufficient state as in REP3.
For a zero-probability observation, the posterior is unspecified by the model;
an operational fallback or model revision is additional behavior.

Bayesian filtering is therefore a valid realization under prior/likelihood and
hidden-Markov assumptions, not a unique consequence of AX1–AX4. Even finite
hidden-state models generally have infinitely many reachable beliefs. Exact
rational arithmetic may grow in bit length indefinitely; storing a vector of
\(n\) reals does not establish a bounded-memory executable filter.

## REAL4: countable machines need effective syntax

Suppose states, inputs and outputs have effective finite-string encodings;
the initial state is computable; and next-state/output maps are total
computable functions on admitted encodings. A symbolic program stores the
current encoding, evaluates the maps, emits the result and repeats. Each
finite input prefix takes finitely many steps by totality. State length and
transition time may grow without a uniform bound. The behavioral residual
quotient need not be computable: the full encoded history remains an available
state when its next-output function is computable, even if minimization is not.

Countability alone does not supply this premise. With \(A=\{a\}\), let
output number \(t\) be the indicator that Turing machine \(t\) halts on its
own code. This is a total causal deterministic probability law on countable
histories, hence satisfies the process axioms. Any total digital program
emitting each next output would decide the halting set by running until its
\(t\)-th output, a contradiction. AX3 can consistently admit only
computable machines, making this obligation unrealizable. Restricting the
target to effectively computable laws repairs this specific obstruction.

Neural Turing simulation requires equally explicit precision and execution
assumptions. [Siegelmann and Sontag (1995)](https://www.sciencedirect.com/science/article/pii/S0022000085710136)
prove rational recurrent-net simulation under their exact dynamical model.
It does not make finite-precision bounded-memory hardware a universal exact
realizer of arbitrary laws. REAL2 instead proves the finite special case
directly with concrete weights, unit counts and a state-domain invariant.
