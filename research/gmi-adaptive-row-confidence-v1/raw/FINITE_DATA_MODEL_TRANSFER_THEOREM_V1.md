# Finite data transfer for acquisition policies — FMT-1–4

Date: 2026-09-13. Conditional finite-model bridge; no technical novelty claimed.
Read [parent subtraction and charges](FINITE_DATA_PARENTS_AND_COSTS_V1.md) with this theorem.

## 1. Fixed physical and sampling register

Supply finite labelled observed states S, known legal actions U(s), a known
initial state, and known stopped states T with successful subset G. U(s) is
nonempty outside T; inside T the episode has stopped. A success label means an
adequate terminal decision has actually been executed. An unknown stationary
kernel P(s'|s,u) is fixed before sampling and deployment. The observed state is
sufficient for this conditional law. Finite latent state alone does not imply
this premise, nor does a finite sample discover a sufficient state or meaning.

Register a finite integer H>=0. At most H real controls are taken; a finish or
reset is a control and consumes a slot. After stopping, mathematical padding
holds the terminal state fixed and charges zero. At time t before a transition,
known work c_t(s,u) lies in [0,C_t], with finite C_t>=0. A known settlement
d(s) in [0,D] is charged once, at the first stop or at the deadline. Its value
is independent of the stop time, so accounting at padded S_H is equivalent.
Stopping work in c and settlement in d must be distinct charges, never counted
twice. At the deadline a nonterminal state is unsuccessful even if an answer
is ready but its required finish action has not been executed. Thus

    p_P(pi)=Pr_P(S_H in G),
    J_P(pi)=E_P[sum_(t=0)^(H-1) c_t(S_t,U_t)+d(S_H)].

Every legal row is either independently known exactly or sampled. For sampled
row r, supply a nonempty outcome alphabet B_r subseteq S containing its entire
true support, with k_r=|B_r|. Before seeing data fix N>=1 and the row/call
register. Obtain exactly N iid draws from each row, with fresh noise and the
same fixed P. Row access, state preparation, resets, observation, random-bit
supply and recording require a charged generative apparatus. A trajectory of
ordinary deployment is not automatically such an apparatus. Known rows require
their own warrant; an empirical zero is not a known impossible transition.

Samples are private, have distinct registered call identities, and precede
policy selection. Deployment noise is fresh conditional on P and independent
of this data. Cross-row independence is assumed for the exact data census;
the union bound below only needs within-row iidness. Duplicate-call rejection
and complete counts check custody syntax, not physical independence or support
truth. Even rows unreachable in the empirical model must be covered, unless a
separately proved common-model reachability restriction removes them.

## 2. FMT-1 — one confidence event for every subsequently selected policy

Let Phat use empirical rows and unchanged known rows. For 0<alpha<1 and a
fixed rational 0<epsilon<1, put A=sum_r(2^k_r-2). If

    A exp(-2N epsilon^2) <= alpha,

then E={max_r TV(P_r,Phat_r)<=epsilon} has probability at least 1-alpha over
the data, where TV=one half of L1 distance. Equivalently, for A>0, choose
N>=ceil(log(A/alpha)/(2epsilon^2)). For A=0 all rows are exact, including
single-symbol sampled rows, so epsilon=0 is valid. Epsilon=1 is always the
trivial radius. Empty sampling registers require all rows independently known.

**Proof.** For one k-symbol row, TV is the maximum empirical excess over
subsets of its alphabet. The empty and full subsets cannot have positive
excess; a one-sided Bernoulli concentration bound for each other subset gives
(2^k-2) exp(-2N epsilon^2). Sum these bounds across registered rows. This is
the distribution-free consequence of Weissman et al., Theorem 2.1, with their
L1 threshold set to 2epsilon. No independence across rows is needed here.
Single-symbol rows have no error. Known rows have no sampling error. QED.

The confidence set is a continuum of stationary kernels containing the true
kernel on E. It is not identification of a member of UMA's finite hypothesis
list, a Bayesian posterior claim, or a certificate that the supplied alphabets,
costs or adequacy predicate describe reality. Optional stopping, selective row
reporting, dependent reuse of one draw and unregistered drift are not covered.

## 3. FMT-2 — sharp uniform finite-horizon transfer

For any two kernels in the common register with maximum row TV at most epsilon,
let Delta_t=1-(1-epsilon)^t, including Delta_0=0. For every same legal finite
history policy pi, including private randomization,

    |p_P(pi)-p_Phat(pi)| <= Delta_H,
    |J_P(pi)-J_Phat(pi)| <= B_H
         = sum_(t=0)^(H-1) C_t Delta_t + D Delta_H.

Intersect probability intervals with [0,1], and work intervals with
[0,sum C_t+D]. Add any identical policy-seed setup charge outside these
control-work intervals. It cancels in model differences but remains payable.

**Proof.** Couple the initial state and the private policy seed identically.
While the entire observed histories match, the actions match. A maximal
coupling of each next-state row keeps histories equal with conditional
probability at least 1-epsilon. Exact absorbing padding cannot break a match.
Induction gives matching-history probability at least (1-epsilon)^t. Before
the tth transition, stage charges are identical on matching histories and
differ by at most C_t otherwise. At H the success indicators differ by at
most one and settlements by at most D. Take expectations and sum. This proof
is uniform over all legal policies; it never unions over a selected policy
class. Conditioning on any dataset in E therefore permits arbitrary subsequent
data-selected history policies and fresh private randomization. QED.

The successful-policy predicate and legality are common across models. Comparing
different policies, different costs or different initial laws is not licensed.
If a cost depends on the newly observed next state, its corresponding bound is
C_t Delta_(t+1), not C_t Delta_t. Such a charge can instead be explicitly
included in an appropriate common-state/terminal register. Probability-one
statements over data and deployment remain distinct: a certified success lower
bound q on E yields unconditional success at least (1-alpha)q, not certain
success and not a posterior conditional probability that E holds.

## 4. FMT-3 — constructive joint policy transfer and strongest-class comparison

Let Pi contain all legal deterministic history trees at H, or all private
mixtures of them. Their empirical probability/work profiles are obtained by
exhaustive tree enumeration or the common-child recurrence of UMA with one
kernel. At each successor, keep a total legal continuation even at empirical
probability zero. For mixtures take the convex hull. The exact executable
construction assumes rational supplied known rows, costs, target and seed fee;
arbitrary real inputs need an effective representation/comparison oracle. The
analytic transfer inequalities do not require rationality. No scalable algorithm
or bounded physical controller follows.

Define J^sigma(pi)=J(pi)+sigma(pi). Here sigma is zero for pure policies and
one fixed known nonnegative fee for every nontrivial initial mixture, identical
under both kernels; zero fee recovers J. Selection, comparator, regret
and work allowance below all use this augmented objective. For target q in
[0,1], minimize empirical J^sigma among pi with
p_Phat(pi)>=q+Delta_H. A deterministic finite minimum or the best pure/mixture minimum
is attained when feasible. An absent certificate means this sufficient test
failed; it does not prove true infeasibility. On E its selected pi_hat satisfies

    p_P(pi_hat)>=q,
    J^sigma_P(pi_hat)<= min_(pi in Pi: p_P(pi)>=q+2Delta_H) J^sigma_P(pi)+2B_H,

provided the displayed comparator set is nonempty. A control-work allowance w
is certified by J^sigma_Phat(pi_hat)+B_H<=w, using that same policy. Never combine
separate empirical minima. Finite nonnegative allowances are required.

**Proof.** The first result is FMT-2. Every true comparator with the doubled
success margin is feasible for the empirical tightened problem. Its empirical
augmented work is at most its true augmented work plus B_H; optimality adds the
second B_H. Finite policy sets, or compact finite convex hulls, give attainment.
A fixed nonnegative private-seed charge for each nontrivial mixture can be
included on both sides. The optimum is then the best pure policy or two-policy
mixture: with one probability inequality a linear optimum lies on a vertex or
an edge intersection; any degenerate pure profile avoids the surcharge. QED.

This is a uniform transfer certificate, not an exact robust frontier over the
confidence region. It does not replace fixed-model uncertainty with a nature
that selects a new row at each step. Sampling, synthesis and retention charges
are additional setup/lifetime coordinates listed in the companion document.

## 5. FMT-4 — sharpness, impossible upgrade and constructive remedy

Use a clock-labelled chain r_0,...,r_(H-1), then successful stopped g, with
stopped hazard b. Each advance/last-finish costs C_t at slot t. Phat advances
surely; P advances with 1-epsilon and otherwise enters b. All states other
than chain states are absorbing. Set d(g)=D and d(b)=0. Both share the same
stationary row register; the clock states are explicit representation, not
free hidden timing. Then p_Phat-p_P=Delta_H and
J_Phat-J_P=sum C_t Delta_t+D Delta_H. Both bounds are attained together.

Even one unknown finish row can send a call to g with 1-eta and stopped b with
eta>0. N all-safe samples occur with probability (1-eta)^N>0 and are identical
to the deterministic-safe model's data. Empirical success is one; true success
is 1-eta. For eta<=epsilon this happens inside E. Any rule that announces a
zero-error support/sure-success guarantee on this data with positive probability
also falsely announces it under some eta>0. Finite data alone cannot supply
that upgrade uniformly, even though the run always terminates.

The remedy is a clipped probabilistic certificate with charged acquisition and
margin tightening, or an independently certified protective/terminal mechanism
that removes the hazardous support. The receipt includes a nonvacuous fixed-N
certificate, actual chosen-policy execution, exact mixture charges, complete
finite data laws, and common-history policy countercontrols. It is finite
model evidence, not an empirical GMI performance or global completion claim.
