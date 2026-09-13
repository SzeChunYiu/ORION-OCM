# Complete-view identification and forgetting — LMT-5 / LMT-7

## LMT-5: fix the learner before comparing its experiments

Fix an admitted learner/development policy \(L\). Let \(V\) be its complete
joint terminal decoder view: observations, retained/working state, actions,
context registers, and all private randomness available to its output rule.
Alternatively represent remaining fresh independent terminal randomness by
a common output kernel \(D(du\mid v)\). Its law and timing are part of the
same fixed learner. No hidden state-dependent side channel is omitted.

Suppose the two worlds induce the same **joint** law
\(\mu_0^L=\mu_1^L=\mu\) of \(V\). Let their unique correct outputs be distinct
\(u_0,u_1\), with all other outputs, including abstention, counted as
unsuccessful for this obligation. Then the common output distribution is
\[
\nu(B)=\int D(B\mid v)\,\mu(dv).
\]
Writing \(q_i=\nu(\{u_i\})\), disjointness gives \(q_0+q_1\le1\).
Therefore \(\min(q_0,q_1)\le1/2\). Equality need not hold: abstention or a
third output can reduce both success probabilities. This is the fixed
learner's impossibility result, not a statement that all policies produce
the same experiment.

To conclude impossibility for **every** admitted learner, require the
same-view premise for each such learner \(L\), then apply the displayed
argument separately to each. The common view law may depend on \(L\).
Equivalently, an interface theorem can prove equality of all controlled
observation kernels, joint initial information and allowed continuations
sufficient to establish those complete-view equalities.

## Marginal observations can hide perfect identification

Let the world be \(b\in\{0,1\}\). A fixed learner samples a private fair bit
\(A\), performs action \(A\), receives \(Z=A\mathbin\oplus b\), and outputs
\(A\mathbin\oplus Z\). In both worlds \(Z\) alone is fair. Nevertheless the
complete view \((A,Z)\) is diagonal in world0 and off-diagonal in world1.
The learner succeeds with probability1 in each world. The marginal
observation premise is true and the required joint-view premise is false.
Calling \(A\) private does not remove it from the terminal decoder.

A separate policy-quantifier example uses controlled output zero under
action0 and the world bit under action1. A learner always using action0
has indistinguishable views. Another admitted learner uses action1 and
identifies the world. Impossibility for the former cannot be promoted to
impossibility for all learners.

**Positive repair.** An admitted action revealing the protected bit makes
exact identification possible; charge its access, memory, computation and
any action risk. If such access is absent, retaining an uncertainty set or
an identifiable equivalence class is a legitimate weaker target. Repeated
updates or unchanged marginal frequencies do not supply missing information.

## LMT-7: a collision theorem needs the complete later view

Let \(F(K_0)=F(K_1)=f\), and fix the same admitted complete continuation
protocol, terminal time and common decoder. Include every input the decoder
will actually receive: \(f\), any surviving working state, private seeds,
later observations/actions and external registers. If these complete views
have the same joint law under \(K_0,K_1\), but exact correctness requires
different unique outputs, the LMT-5 proof applies. No common decoder is
exact in both; their minimum success is at most1/2.

For deterministic identical complete views the proof is simply that a common
function receives the same input. For randomized views it is the common
kernel/pushforward argument. The equal-view condition concerns the full
joint view, not equality of each marginal coordinate separately.
An identical input continuation with no extra state-dependent information
is a useful sufficient case.

A collision of \(F\) **alone** does not establish that premise. Set
\(K_b=b\), forget to \(f=0\), and let the common continuation request a fresh
observation \(Z=b\). The common decoder returns \(Z\), exactly repairing
the lost bit. This is compatible with different original required outputs:
the later view now distinguishes them. In contrast, a fresh independent
fair \(Z\) leaves equal views and cannot repair identification.

Thus the exact quotient's obstruction applies to distinctions required by
the declared future interface after all admitted information is accounted
for. Forgetting can be behaviorally safe under restricted obligations, or
made safe by paid reacquisition; neither case is a universal free-memory
theorem. Resource benefit requires a separate comparison of retention with
the complete reacquisition/continuation strategy.

## Parent and claim boundary

Equality of complete experiments followed by a common decision kernel
preserves the output law; the proof above is elementary probability, not a
new statistical-identification theorem. This is the same declared-interface
discipline used by the repository's semantic-state and controlled-acquisition
results. No observational marginal is promoted to an intervention law, no
causal-world parameter is inferred without access, and no new experiment
or empirical capability is reported.
