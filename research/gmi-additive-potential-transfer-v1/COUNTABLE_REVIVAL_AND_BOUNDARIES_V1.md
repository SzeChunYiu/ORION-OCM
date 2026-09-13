# Countable revival and necessary boundaries

These are analytic models and exact arithmetic controls, not empirical records.

## C1. Polynomial-tail proper policies excluded by WTT

On X={1,2,...}, stopped T={0}, charge 1, nominal Q continues n->n+1 with
p_n=n^2/(n+1)^2 and otherwise stops. Starting at 1,

    Pr_Q(tau>t)=product_(n=1)^t n^2/(n+1)^2=1/(t+1)^2,
    E_Q tau=sum_(k>=1)1/k^2<=2.

No finite initial weight w(1) and beta<1 can satisfy a WTT geometric certificate:
its tail bound would require 1/(t+1)^2<=w(1)beta^t for every t, impossible.
This is a single proper countable law, not a problem of finite confidence width.

## C2. Constructive transfer for an entire countable model continuum

Let 0<=e<=1, and K_theta continue with (n^2-theta)/(n+1)^2, theta in [0,e].
The remaining probability reaches 0. All rows are probabilities, including
n=1,theta=1. Set L(n)=V(n)=2n, B(n)=2e, r(n)=2e/(n+1); all potentials
are zero at 0. For every integer n>=1 and real theta in [0,e],

    L-K_theta L = V-K_theta V = 2(n+theta)/(n+1) >=1,
    integral_X V|K_theta-Q| = 2theta/(n+1) <= r(n),
    B-K_theta B-r = 2e(n+theta)/(n+1)^2 >=0.

Thus APT proves E_Ktheta tau<=2n and
|J_Ktheta(n)-J_Q(n)|<=2e. A=e on X and epsilon(n)=e/(n+1)^2 additionally give
A-K_theta A-epsilon=e(2n+theta)/(n+1)^2>=0; all models stop at the same
successful terminal, so their actual eventual-success difference is zero.
The bounds are sufficient, not asserted sharp.

These identities prove all states and the real parameter interval. Finite
rational checks below only validate formula implementation. The supplied
confidence region must warrant these rows even at unobserved n; a finite
sample does not establish the infinite model class or parameter stationarity.

For independent prefix execution from n, survival after H is at most
n^2/(n+H)^2 because each K_theta continuation is <=Q's. APT's work potential
gives a certified interval for the true infinite expected cost:

    prefix_cost_H <= J_Ktheta(n)
       <= prefix_cost_H + survival_H * 2(n+H).

In this particular example that residual tends to zero, at most
2n^2/(n+H). Finite prefix calculations do not replace the all-state proof.

## C3. Nonvanishing envelope remainder is a legitimate no-alarm case

From positive integer n, move to 2n with probability 1/2, otherwise to0;
charge1. Put L=2 and V(n)=n+2. Then KL=L-1 and 1+KV=V for every n.
For K=Q choose B=r=A=epsilon=0. Starting at n, at horizon H,

    Pr(tau>H)=2^-H,
    E[V(X_H)1_alive]=n+2^(1-H) -> n>0,
    prefix_cost_H=2-2^(1-H),   actual_remaining_cost=2^(1-H) ->0.

All APT conclusions hold. Requiring the supplied upper envelope V to vanish
in expectation would wrongly reject this valid model. The proof only drops
its nonnegative remainder; actual finite expected costs give the limit.

## C4. WTT is a constructive special case, not discarded

Given a WTT certificate w,beta,C,eta,zeta, write
h=zeta+C eta/(1-beta). Then set

    L=w/(1-beta), V=Cw/(1-beta),
    r(x,a)=h w(x), B=h w/(1-beta).

WTT drift gives L-KL>=w>=1, V-KV>=Cw>=c_K and B-KB>=h w=r.
Its weighted row bound gives the required immediate-plus-continuation error.
Thus APT reproduces WTT's cost bound. For uniform full-row TV<=epsilon0,
take A=epsilon0 w/(1-beta) and epsilon(x,a)=epsilon0.
The previous geometric certificate remains valid and useful when it exists;
C2 supplies an explicit additional working regime.

## C5. Premises that cannot be dropped

- A zero-cost self-loop obeys c+KV<=V with V=0, and B=r=0, but never stops.
  The separate L progress inequality must reject it.
- A newly possible trap in an empirically unvisited row remains relevant.
  Certificates cover every retained row, not just nominally reachable ones.
- Two models can have identical kernels but different charges; omitting
  |c_K-c_Q| gives a false zero transfer bound.
- Nonnegativity cannot be removed even with the same killed operator.
  In C3's doubling-or-stop chain use signed V(n)=2-n and V(0)=0.
  Then 1+KV(n)=1+(2-2n)/2=2-n=V(n), but from n=2 the false bound
  J<=V(2)=0 contradicts actual J=2. L=2 and B=r=0 remain valid.
  The negative continuation values are precisely the removed premise.
- Swapping two terminal labels preserves the killed kernel but changes success
  probability by1. APT-3 requires full-row TV and its own finite A potential.
- Hidden revealed cost signals can change subsequent decisions despite equal
  expected current costs. Such signals must be inside the common kernel.
- Coverage E can be certain while certification F is empty. Conditioning on F
  can select confidence failures; costs finite for each dataset can still have
  infinite data-averaged expectation. WTT's corresponding restrictions are retained.
- Excluding a cheaper proper policy from Pi_D prevents claiming regret against
  all proper policies. Fees stay in selection and comparator, not just a footnote.

Nonnegative/additive certificates remain sufficient conditions. APT does not
claim they can be synthesized for every true physical policy class or from
arbitrary finite data, or that all countermodels in the repository are solved.
