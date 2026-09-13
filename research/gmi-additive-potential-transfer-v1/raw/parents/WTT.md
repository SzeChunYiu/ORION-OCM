# Weighted transient transfer — WTT-1–4

Conditional application of weighted transient MDP and simulation arguments.
The general result is primary; finite checks do not establish its quantifiers.
Read [parents and costs](PARENTS_AND_COSTS_V1.md) and
[countermodels and revival](BOUNDARIES_AND_WITNESSES_V1.md).

## 1. Complete common interface

Let S and A be standard Borel spaces, T a measurable absorbing stopped set,
X=S\T, and the common legal-action graph measurable. Supply measurable policy
kernels on complete histories, including any retained private randomness.
Every admitted model has a Borel transition kernel K and a nonnegative
measurable expected pre-transition charge c_K(x,a), zero after stopping.
Conditional on the complete global history and chosen action, the next state
has this K row. Every newly revealed signal used by later decisions, including an observed
random charge, must be included in the next-state observation interface.
Expected charge c_K is not an additional unmodelled observation channel.
The observed state must be sufficient for that conditional law; latent finiteness or a fitted Markov table does not establish it.
All models share labels, legality, stopping/adequacy semantics and initial
law mu. Stop success is a registered property, not inferred from termination.
A finish/reset is a charged action. Transition-dependent charges or terminal
settlements must enter c_K through their conditional expectation, with their
model error included below, or use an explicit additional charged state.
No terminal cost is silently omitted or charged twice.

Data D precedes deployment. For the fixed true model P, a supplied confidence
procedure has a measurable event E={P in C_D} with Pr_D(E)>=1-alpha.
Future deployment obeys P conditional on D; do not condition it on a future
good-trajectory event. Adaptive acquisition needs valid simultaneous coverage,
such as ARC within its finite supplied support contract.
Let F be the measurable event that all following certificates and required
policy choices are supplied; the data-dependent selections must be measurable.
For each D in F, choose a nominal Q in C_D, a measurable retained
action graph A_D, finite measurable w>=1 on X (w=0 on T), beta in [0,1),
and finite C,eta,zeta>=0. Require m=integral w dmu<infinity.
All these objects may depend on D; every inequality below must be verified
for all models and retained rows, including empirically unseen successors.
Define Pi_D as a nonempty supplied class of common measurable history policies
whose actions always lie in A_D at every represented possible history.
Private randomization has the same conditional law in both compared models.

For every K in C_D and (x,a) in A_D, require

    integral_X w(y) K(dy|x,a) <= beta w(x),               (drift)
    0 <= c_K(x,a) <= C w(x),
    integral_X w(y) |K-Q|(dy|x,a) <= eta w(x),           (kernel error)
    |c_K(x,a)-c_Q(x,a)| <= zeta w(x).                    (charge error)

Here |K-Q| is the total-variation MEASURE of the signed row difference,
not half its L1 norm. It is restricted to X because continuation cost is zero
on T. These are deterministic certificates on the supplied confidence set.
The set need not be rectangular: rowwise enforcement is sufficient and can
be conservative. It does not identify a fixed-model optimum with a switching
adversary's optimum. No existence of a measurable optimizer or effective
algorithm for these universal inequalities is asserted.

## 2. WTT-1 — common progress, expected work and tails

Fix any D in F, K in C_D and pi in Pi_D. With
tau=inf{t>=0:X_t in T}, for every integer t,H>=0,

    E_K[w(X_t) 1{tau>t}] <= beta^t m,
    Pr_K(tau>t) <= min(1,beta^t m),
    E_K tau <= m/(1-beta),
    J_K(pi)=E_K sum_(t<tau) c_K(X_t,A_t) <= C m/(1-beta),
    E_K sum_(H<=t<tau) c_K(X_t,A_t) <= C m beta^H/(1-beta).

Use beta^0=1. Thus every such policy is proper with finite expected lifetime;
no deterministic upper bound on realized path length follows in general.

**Proof.** Average the row drift over the common policy kernel conditional
on each complete history. Induction gives the first bound. Since w>=1 before
stopping, it gives the probability bound. Sum survival probabilities for
E tau and sum expected nonnegative charges for the two work bounds, using
Tonelli and the geometric series. In particular, every continuation bounded
by M w has terminal remainder expectation at most M beta^H m, tending to
zero. An additive drift against 1 alone is not substituted for this
transversality statement on an unbounded state space. QED.

## 3. WTT-2 — uniform undiscounted cost and terminal-event transfer

For every common pi in Pi_D and K in C_D,

    |J_K(pi)-J_Q(pi)| <= B
      := m [zeta/(1-beta) + C eta/(1-beta)^2].           (1)

**Proof.** First truncate at H without adding a new settlement. At a complete
history ending in x, Q's remaining truncated cost is at most C w(x)/(1-beta),
by WTT-1 applied to the continuation. A one-step model replacement therefore
changes that continuation expectation by at most
[zeta+C eta/(1-beta)]w(x). Expanding the finite backward recurrence for the
difference under K, then averaging over mu, bounds the H-step difference by
this constant times sum_(t<H) E_K[w(X_t)1{tau>t}], at most B.
This works for every history-dependent randomized policy: the continuation
after a fixed history/action is the same function of the next state in both
models. WTT-1 bounds both omitted tails by C m beta^H/(1-beta).
Let H grow; finite expectations and vanishing tails prove (1). QED.

For a separately registered measurable G subseteq T, additionally require
full-row TV(K,Q)<=epsilon on A_D, where TV is half L1 / supremum over events.
Then

    |Pr_K(X_tau in G)-Pr_Q(X_tau in G)|
        <= d := min(1,epsilon m/(1-beta)).               (2)

**Proof.** Truncate the terminal-event indicator at H. Its continuation is in
[0,1], so each full-row replacement contributes at most epsilon per surviving
step. The same finite recurrence gives epsilon E_K[min(tau,H)].
Both stopping times are almost surely finite; bounded convergence gives (2).
The killed weighted error alone does not distinguish terminal labels. QED.

## 4. WTT-3 — data selection and the exact comparator

All bounds hold simultaneously over Pi_D on E intersect F, without a new
union over data-selected policies, weights or horizons: once D is fixed, the
verified inequalities apply to every model it retains. Coverage of C_D is a
separate premise; checking a selected policy only on its fitted reachable
states is insufficient.

Use the same augmented objective J^sigma=J+sigma(pi) in both models, with
the identical registered finite nonnegative policy setup/seed charge.
If a selected pi_hat is xi-optimal for Q in Pi_D (xi>=0), then on E intersect F

    J_P^sigma(pi_hat) <= inf_(pi in Pi_D) J_P^sigma(pi)+2B+xi.

For a success target q, a xi-optimal selection in the empirical feasible
subset {pi in Pi_D:p_Q(pi)>=q+d} instead gives
p_P(pi_hat)>=q and the same regret bound against
{pi in Pi_D:p_P(pi)>=q+2d}, if this comparator set is nonempty.
This follows by two applications of (1), with (2) making each comparator
empirically feasible. A selected-policy work allowance uses its own
J_Q^sigma(pi_hat)+B; separate policy minima cannot be combined.
These are statements about a supplied xi-optimal witness. Exact attainment,
finite controller representation and synthesis computability need additional
hypotheses. No comparison to proper policies outside Pi_D follows.

## 5. WTT-4 — confidence and cost are not unconditional completion

On E intersect F, the selected policy is proper. Obtaining and executing
such a certified proper policy has probability at least
Pr(E intersect F)>=max(0,Pr(F)-alpha). Coverage E alone does not guarantee F.
Conditioning on F does not preserve coverage 1-alpha: certification can select
the confidence failures. An arbitrary fallback on F^c need not terminate.
Even if F is certain, unconditional expected cost may be infinite on E^c.
A finite global expectation additionally requires an integrable bound over D
on selected/fallback deployment cost, plus integrable acquisition/setup.
Any fallback needs separately warranted termination and cost. Pointwise
finite conditional costs alone need not have a finite data-averaged cost.
Abstention on uncertified data is not successful execution.

Acquisition must itself finish to produce D; ARC does not promise that.
For countable/Borel models, this theorem imports a valid confidence set and
weighted tail restrictions. Finite-alphabet ARC does not establish them.
Ordinary TV convergence does not control unbounded w-weighted row error.
Known law, sufficient state, support, physical access, costs and adequacy
remain empirical/semantic premises. See the explicit accounting register.
