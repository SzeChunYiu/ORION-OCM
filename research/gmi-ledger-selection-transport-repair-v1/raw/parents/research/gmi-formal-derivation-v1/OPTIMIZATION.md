# Optimization and credit assignment from explicit local decision premises

Status: conditional derivations of established mechanisms; no architecture is selected by the GMI core alone.
Read [learning](LEARNING.md) for the external objective and generalization distinction.

## O0 — the premise that chooses an optimizer

The core admits executable state changes and resource-sensitive comparisons; it does not specify a geometry, differentiability, or a loss function.
Supply a parameterization `theta`, a differentiable objective `F`, local derivative information `g=grad F(theta)`, an admissible update set, and a movement penalty `D`.
The local decision rule is to minimize a linear prediction of objective change plus a movement charge:

    theta^+ in argmin_(u in C) { <g,u-theta> + D(u,theta)/eta }, eta>0.  (O0.1)

This rule is an added, testable local decision premise, not an algebraic consequence of the word intelligence.
An exact objective search, an ordinal comparison or a discrete rule edit is also compatible with the core; different premises select different mechanisms.
The choice of `eta` and geometry is part of the declared resource/accuracy contract, not a universal numeric constant predicted by GMI.

## O1 — Euclidean movement forces the gradient step

Take `C=R^d` and `D(u,theta)=||u-theta||_2^2/2`.
Completing the square in (O0.1) gives

    <g,u-theta> + ||u-theta||^2/(2 eta)
      = ||u-(theta-eta*g)||^2/(2 eta) - eta*||g||^2/2.

The unique minimizer is therefore `theta^+=theta-eta*g`.
For nonempty closed convex `C`, Euclidean projection gives `theta^+=Proj_C(theta-eta*g)` by the same identity.
For a supplied symmetric positive-definite metric `A`, penalty `(u-theta)^T A(u-theta)/2` gives `theta^+=theta-eta*A^-1*g`.
This derives a preconditioned update; it does not identify a Fisher metric or estimate a Hessian for free.

Suppose `F` is lower bounded and has `L`-Lipschitz gradient on `R^d`, `L>0`.
Integrating its directional derivative on the segment from `theta` to `theta+d` yields

    F(theta+d)-F(theta)-<g,d>
      = integral_0^1 <grad F(theta+s*d)-g,d> ds <= L*||d||^2/2.

Substituting `d=-eta*g`, with `0<eta<=1/L`, proves

    F(theta^+) <= F(theta) - eta*(1-L*eta/2)*||g||^2
               <= F(theta) - eta*||g||^2/2.                         (O1.1)

Summing (O1.1) for a fixed such step gives

    min_(t<T) ||grad F(theta_t)||^2 <= 2*(F(theta_0)-inf F)/(eta*T).

This is a stationarity guarantee, not convergence to a global minimizer or a population-risk improvement theorem.
If additionally `F` is `mu`-strongly convex and attains `F*`, its defining quadratic lower bound implies
`F(theta)-F*<=||g||^2/(2*mu)` by minimizing that lower quadratic over all points.
Then (O1.1) gives `F(theta_t)-F* <= (1-eta*mu)^t [F(theta_0)-F*]`.
The derivation covers an exact gradient of the declared objective; stochastic estimates need unbiasedness/noise assumptions and a separate analysis.

## O2 — Bregman movement forces mirror descent and exponentiation

Let `psi` be differentiable and strictly convex on an open convex domain, and define
`D_psi(u,theta)=psi(u)-psi(theta)-<grad psi(theta),u-theta>`.
Assume the minimizer in (O0.1) exists and all gradients below are defined there.
For an interior unconstrained minimizer its first-order equation is

    grad psi(theta^+) = grad psi(theta)-eta*g.

For convex constrained `C`, first-order optimality instead gives, for all `u in C`,

    <eta*g+grad psi(theta^+)-grad psi(theta),u-theta^+> >= 0.

Expanding the three Bregman terms gives the identity

    <grad psi(theta^+)-grad psi(theta),u-theta^+>
      = D_psi(u,theta)-D_psi(u,theta^+)-D_psi(theta^+,theta).

If `psi` is one-strongly convex in norm `||.||`, `D_psi(theta^+,theta)>=||theta^+-theta||^2/2`.
Split `<g,theta-u>` at `theta^+`, use the identity, and use
`eta*||g||_*||theta-theta^+||-||theta-theta^+||^2/2<=eta^2||g||_*^2/2` to obtain

    eta*<g,theta-u> <= D_psi(u,theta)-D_psi(u,theta^+)
                         + eta^2*||g||_*^2/2.                      (O2.1)

For convex losses `F_t`, `F_t(theta_t)-F_t(u)<=<g_t,theta_t-u>`.
Summing (O2.1) with fixed `eta` yields regret at most
`D_psi(u,theta_1)/eta + eta*sum_t ||g_t||_*^2/2`.
No convexity of losses was needed to derive the update itself; convexity is used exactly at this regret step.
These are the established [mirror descent/Bregman mechanisms of Beck and Teboulle](https://www.math.tau.ac.il/~teboulle/recentpub.html), specialized with all inequalities shown.

For positive probability weights `p` on a finite simplex, use negative entropy `psi(p)=sum_j p_j log p_j`, so `D_psi(q,p)=KL(q||p)`.
The Lagrange equation for (O0.1) is `g_j+(log(q_j/p_j)+1)/eta+nu=0`.
Normalization gives the unique minimizer

    q_j = p_j exp(-eta*g_j) / sum_k p_k exp(-eta*g_k).

Boundary competitors follow by continuity; zero initial weights cannot be revived by this finite-KL update and require a separate admission mechanism.
Repeated use with `g_j=ell_(t,j)` is the known Hedge learner proved in [L4](LEARNING.md).
The additive/exponentiated relationship is inherited from [Kivinen and Warmuth](https://doi.org/10.1145/225058.225121); no statistical or computational advantage follows without the appropriate geometry and comparator.

## O3 — Bayesian updating is an exact special case under a likelihood premise

For a finite hypothesis set, positive prior `p_j`, and positive finite likelihoods `L_j=P(e|h_j)`, minimize

    sum_j q_j[-log L_j] + KL(q||p).

Let `Z=sum_j p_j L_j` and `p'_j=p_j L_j/Z`.
Expanding gives the objective `KL(q||p')-log Z`; nonnegativity of KL and equality only at `q=p'` prove the Bayes update is its unique minimizer.
KL nonnegativity follows from `log x<=x-1`, applied to `x=p'_j/q_j` and summed over positive `q_j`; limits cover zero `q_j`.
If some likelihoods vanish, restrict to their nonzero support; if `Z=0`, the conditioning event has no defined posterior in this finite model.
This connects evidence accumulation, entropy geometry and log-loss; likelihood correctness and the prior are supplied model assumptions, not consequences of the GMI core.

## O4 — composition plus the chain rule derives reverse-mode credit assignment

Fix an evaluated finite directed acyclic graph whose scalar nodes satisfy `v_i=f_i((v_j)_(j in pa(i)),theta_i)` and whose scalar output is `F=v_o`.
Every local function is differentiable at the evaluation point; shared parameters are identified as the same variables.
Set the output adjoint `a_o=1`, initialize other adjoints to zero, and process nodes in reverse topological order:

    for each edge j -> i: a_j += a_i * partial f_i / partial v_j,
    for each parameter occurrence theta_r in f_i:
         grad_(theta_r) F += a_i * partial f_i / partial theta_r.

Proof: recursively substitute the total differential
`dv_i=sum_(j in pa(i)) (partial_j f_i) dv_j + sum_r (partial_(theta_r) f_i) dtheta_r`
into `dF=dv_o`. Each directed path contributes the product of its local derivatives.
Reverse topological accumulation sums exactly these path products, since every path begins with one outgoing edge and the remaining path has already been accumulated.
Parameter occurrences contribute additively, so weight sharing is handled by summing all uses. The resulting coefficients of each `dtheta_r` are precisely the gradient.
Thus a differentiable realization plus local decision O1 yields backpropagation followed by a gradient update; `BACKPROP` need not be an opaque primitive.
For bounded-arity operators whose local derivative work is at most a constant multiple of forward work, the reverse pass costs `O(total forward work + explicit adjoint-accumulation work)`.
This becomes `O(number of nodes)` only under a unit-cost elementary-operation model, including bounded parameter incidence and unit-cost derivative multiplication/addition.
Retained intermediate values and adjoints use `O(number of nodes)` scalar slots; scalar bit lengths, precision, graph/parameter storage and operation workspace must also be charged, and are not bounded by the slot count.
Checkpointing exchanges recomputation for retained slots; its precision, scheduling and resource costs remain explicit.
An opaque operation without a supplied derivative/implementation violates the overhead premise; arbitrary differentiation of programs is not made free.
Finite differentiable recurrent execution is covered by unrolling; an unbounded loop, discontinuity or differentiation through discrete branching requires its own semantics and theorem.
The neural-learning application is an established [Rumelhart–Hinton–Williams parent](https://www.nature.com/articles/323533a0), not a priority claim about the invention of reverse-mode differentiation.

## O5 — local block updates and a concrete neural specialization

If, holding other blocks fixed, block `i` obeys the smooth upper bound with constant `L_i>0`, the update
`theta_i^+=theta_i-grad_i F(theta)/L_i` lowers `F` by at least `||grad_i F(theta)||^2/(2L_i)`.
The proof is O1's segment integration restricted to that block.
For finitely many blocks, `L_max=max_i L_i`, choosing a block of largest `||grad_i F||` gives decrease at least `||grad F||^2/(2*d_blocks*L_max)`.
Summing proves the corresponding best-iterate stationarity bound. Finding that block itself may require evaluating all blocks and must be charged.
Arbitrary local updates, stale gradients or independent simultaneous block updates do not inherit this sequential bound.
Example: `F(x,y)=(x+y)^2/2` has each block constant one; simultaneous unit block steps send `(1,1)` to `(-1,-1)`, leaving `F` unchanged although each isolated block update decreases it.

For a supplied layered realization `h^l=sigma(W^l h^(l-1)+b^l)` with elementwise differentiable `sigma`, O4 gives

    delta^L = grad_(h^L) ell * sigma'(z^L),
    delta^l = ((W^(l+1))^T delta^(l+1)) * sigma'(z^l),
    grad_(W^l) ell = delta^l (h^(l-1))^T,     grad_(b^l) ell = delta^l.

Here `*` means componentwise multiplication and `z^l=W^l h^(l-1)+b^l`; parameter tying again adds contributions.
The architecture and smooth parameterization are supplied realizations; these equations derive their optimizer/credit implementation, not neural necessity.
For the globally one-smooth, lower-bounded `F(x)=1+cos(x)`, exact gradient descent initialized at zero remains at a nonoptimal stationary point.
For `F(x)=L*x^2/2`, choosing `eta>2/L` makes nonzero iterates diverge.
These satisfy the relevant smooth local equations and falsify unconditional global-optimality and arbitrary-step claims; revive them by changing initialization/search or supplying a valid step bound.
