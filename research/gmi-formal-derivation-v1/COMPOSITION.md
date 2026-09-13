# Composition under one execution history

Status: analytic conditional theorems. Local correctness must hold under the
actual surrounding execution; isolated marginal validity is insufficient.
Use AX1–AX4 from [AXIOMS](AXIOMS.md).

## CMP1: existence and exact preservation

Assume a finite or countable discrete sequence of kernel invocations. The
scheduler chooses the next component and its input from the global past;
all hidden/shared state needed by the joint law is retained in that law.
For each finite prefix, define its joint law by successive integration of
normalized kernels. Integration of the final kernel gives the shorter-prefix
law, so these finite laws are consistent. The standard countable product-kernel
extension yields a law on infinite trajectories; it does not assert finitely
many invocations per second, termination, or bounded resources.

If two implementations have the same initial law on corresponding configurations
and the same conditional output-and-interface-update
kernel at every reachable global history and corresponding configuration, then
they induce the same protected finite-prefix laws. **Proof:** their initial
laws agree; integration against equal next kernels preserves equality at every
step. Cylinder events generate the path sigma-field, so the infinite laws agree.
Internal state is included in the correspondence or abstracted by a valid
simulation relation; matching isolated marginal outputs does not suffice.

This covers feedback with a one-step delay and predictable interleaving.
Unscheduled concurrency, hidden channels and instantaneous cycles require a
new joint model. Equal protected semantics do not imply equal work/memory.

## CMP2: assume–guarantee safety with countably many calls

Let \(I_t\) mean that every protected invariant has held through step \(t\),
with \(I_0\) certain and \(I_t\subseteq I_{t-1}\). On a good prefix the
scheduler discharges the chosen component's precondition. Let \(q_t\ge0\)
be measurable before its outcome, and assume the local contract
\[
\Pr(I_t^c\mid\mathcal F_{t-1})\,1_{I_{t-1}}
\le q_t1_{I_{t-1}},\qquad \sum_{t\ge1}q_t\le\delta\quad\text{a.s.}
\]
For example, an invariant can be "every output accepted so far has a current
valid certificate and respects the legal action interface."
The precondition implication is a proof obligation, not an assumption that the
entire system already succeeds.

**Theorem.** \(\Pr(\bigcap_{t\ge0}I_t)\ge1-\delta\), without independence.

**Proof.** First-failure events \(D_t=I_{t-1}\cap I_t^c\) are disjoint.
The tower property gives
\(\Pr(D_t)\le\mathbb E[1_{I_{t-1}}q_t]\).
Countable additivity and monotone convergence give
\[
\Pr(\exists t:D_t)\le\mathbb E\sum_t1_{I_{t-1}}q_t
\le\mathbb E\sum_tq_t\le\delta.
\]
Setting every \(q_t=0\) gives almost-sure composition. Safety on *every*
admitted execution instead requires that each compatible transition preserve
the invariant pointwise, including null outcomes; then ordinary pathwise
induction supplies that stronger conclusion. For example, \(U\sim U[0,1]\)
has \(\Pr(U>0)=1\), although the admitted endpoint \(U=0\) fails \(U>0\).
Changing component identities and creating new components causes no difficulty
if these same contracts hold at their actual invocation histories.

Alternatively, a single simultaneous confidence event \(E\) of probability
\(1-\delta\), as in [ADAPTIVE](ADAPTIVE.md), can certify all deterministic
invariant implications on \(E\). Then countable induction gives
\(E\subseteq\bigcap_t I_t\). No extra failure allocation is paid merely for
re-reading the same valid certificate. Its observations may not be recounted
as fresh evidence. Distinct new physical failure risks still require contracts.

## CMP3: dependence and interface counterexamples

Let \(B\) be a fair bit. Modules return \(B\) and \(B\), respectively.
Each output is marginally fair, yet a consumer expecting two independent bits
gets equality probability 1 instead of \(1/2\). Replacing the second module by
a fresh fair bit repairs the product-law conclusion; retaining the common seed
in the joint contract repairs the model without imposing independence.

A producer guarantees a nonnegative integer and a consumer is correct only
on strictly positive integers. Both local specifications can be true when the
producer returns zero and the composed division operation fails. Strengthening
the producer or admitting a zero handler discharges the missing precondition.

Correct assertions from different model versions also need not be jointly
applicable. The invariant must include version and dependency compatibility;
see [MEMORY](MEMORY.md). Local optimality additionally does not imply global
optimality when resources, actions or observations are shared.

## CMP4: safety does not imply termination; a sufficient progress law

A machine that waits forever can satisfy every safety invariant. Add a
nonnegative adapted potential \(V_t\), integer-valued stopping time \(T\), finite
\(\mathbb E V_0\), and a constant \(\eta>0\), with
\[
\mathbb E[V_{(t+1)\wedge T}\mid\mathcal F_t]
\le V_{t\wedge T}-\eta1_{\{T>t\}}.
\]
Assume the displayed expectations are defined and finite at finite times.
Summing expectations through \(n-1\) and using nonnegativity yields
\(\eta\sum_{t<n}\Pr(T>t)\le\mathbb E V_0\).
Monotone convergence gives \(\mathbb ET\le\mathbb E V_0/\eta\); therefore
\(T<\infty\) almost surely. If this progress contract holds globally and
CMP2 holds, termination with safety has probability at least \(1-\delta\).
Drift proved only before a certificate failure instead bounds a stopped
process, not automatically the original machine's unconditional running time.

## CMP5: approximate kernel composition

For finite/countable state interfaces, a common initial law and a common
history policy, suppose
the true and approximate conditional kernels differ in total variation by
at most deterministic \(e_t\) on every equal history at step \(t\).
Couple equal histories with a maximal coupling of the next outcomes.
Conditional probability of first disagreement at step \(t\) is at most
\(e_t\); thus any \([0,1]\)-valued protected prefix functional differs in
expectation by at most \(\min(1,\sum_{t\le H}e_t)\).
For deployment after acquisition, let the simultaneous kernel-coverage event
be measurable with respect to the acquisition history and supply all queried
row bounds. Fix any covered acquisition history and freeze both the selected
common policy and estimated kernels. Apply the coupling to the conditional
deployment laws at that history; the true kernels must retain their stated
conditional-law contract. Do not condition this argument on a coverage event
depending on future deployment outcomes, since doing so can change those
kernels. If acquisition coverage fails with probability at most \(\delta\),
averaging adds at most \(\delta\) to the bounded-functional error above.
Training-data reuse or selection-induced environment changes need their own
conditional-law justification.

For an infinite path, the same proof gives \(\min(1,\sum_{t\ge1}e_t)\)
for every measurable \([0,1]\)-valued protected functional. General bounded
functionals require multiplication by their range width. If the sum is infinite,
the guarantee is vacuous. A model with zero hazard and a true kernel with
independent hazard \(e>0\) each step have one-step distance \(e\), but
eventual hazard probabilities 0 and 1. Discounting or summable errors repairs
the specific inference; an anytime confidence event alone does not.

For identical rewards \(r\in[0,1]\), rewarded before each transition, and
discount \(0<\gamma<1\), a uniform distance \(e\) instead gives
\[
|V^\pi_P-V^\pi_{\widehat P}|
\le\sum_{t\ge0}\gamma^t te
=\frac{\gamma e}{(1-\gamma)^2}.
\]
Taking the better bound with \(1/(1-\gamma)\) is valid. Comparing an
approximate-model optimal policy to a true-model optimal policy adds two such
errors (and any planning suboptimality). This assumes optima or corresponding
approximate witnesses exist; it establishes discounted value, not sure safety.

## Parent ownership

These proofs instantiate product-kernel execution, invariant induction,
conditional union bounds, additive drift and simulation-lemma coupling.
They add a common interface/filtration contract to GMI's existing
[finite-data transfer](../gmi-grand-unification-v1/FINITE_DATA_MODEL_TRANSFER_THEOREM_V1.md)
and [joint relational composition](../gmi-joint-relational-composition-v1/CORE.md).
They do not infer product resources from independent task names.
