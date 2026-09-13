# Why a quantitative common transience certificate is needed

These are analytic countermodels and exact arithmetic controls, not new
ecology, timing, training, measurement or learned-capability records.

## B1. Empirical properness does not transfer, even on a covered dataset

Use nonterminals s,b and absorbing g, one action, cost 1 per nonterminal
step. The fitted Q sends s to g; true P sends s to b with probability e and
to g otherwise, where 0<e<1. Both models keep b at b forever.
The maximum row TV is e. N all-safe samples have probability (1-e)^N>0,
so this fitted/true pair can lie inside a valid radius-e confidence event.

From s, Q is proper and J_Q=1; P never stops with probability e and J_P=infinity.
A fitted viability analysis can omit b only because b is fitted-unreachable.
It cannot omit b from a confidence set admitting the true transition.
A confidence set containing the b self-loop cannot pass WTT drift at b:
w(b)<=beta w(b) contradicts beta<1.

**Constructive revival.** Supply an independently justified legal rescue at b
that costs kappa>0 and reaches g surely. The policy takes the original action
at s and rescue at b. It is proper with path length at most 2 and
J_P=1+e kappa. For e<=e_max<1, w(s)=w(b)=1 and beta=e_max certify every
retained row, including the previously unseen b branch. Availability, safety,
adequacy and charge of rescue are premises, never created by changing labels.

## B2. Properness in both models does not yield a uniform error modulus

Replace the b self-loop in both models by b->g with probability p>0 and
b->b otherwise. Both models are proper from every state, but

    J_Q(s)=1,    J_P(s)=1+e/p.

Taking p=e^2 gives cost error 1/e while maximum row TV e tends to zero.
The missing quantity is a common transience margin, not a Boolean proper flag.
The finite control uses e=1/4,p=1/16: values 1 and 5.
WTT remains valid with beta=max(e,1-p)=15/16 and w=1, though its bound is
conservative. It does not promise a small bound when the margin degenerates.

## B3. A real countable-state sufficient regime

Let X={1,2,...}, T={0}. At n, move down with p, up with q, otherwise hold;
at n=1 a down move stops. Every admitted row/action, including unobserved
states, obeys p>=1/2, q<=1/8 and p+q<=1. The laws may vary with state.
For w(n)=2^n, w(0)=0,

    K w(n)/w(n) <= p/2+2q+1-p-q
                 =1-p/2+q <=7/8.

The n=1 downward term is smaller. WTT applies to arbitrary admitted history
policies and initial laws with E[2^X0]<infinity. This is an infinite state
regime with a genuine geometric certificate, not a finite truncation proof.
Its uniform row restrictions require external warrant or valid confidence
construction; a finite sample cannot certify unrestricted unseen rows.
The executable checks verify representative arithmetic only. The displayed
inequality proves every n and every row in the stated region.

## B4. Positive sampling probability and infinite global expectation

Coverage also does not ensure certification: let C_D always equal the known
zero-cost self-loop model, so E is certain, but no beta<1 drift certificate
exists and F is empty. A fallback using that loop never stops. Thus the
covered-and-certified event is E intersect F, not E alone.

A confidence procedure can fail with positive probability. If its resulting
policy then enters B1's trap, its unconditional expected work is infinite.
Multiplying an on-event finite bound by 1-alpha does not fix this.
Even E=F=certain does not imply integrability across data: take
Pr(D=n)=2^-n for n>=1 and a selected immediate stopping action costing 2^n.
Each conditional lifetime is 1 and cost finite, but total expected cost is
sum_(n>=1) 1=infinity. An integrable data-averaged cost envelope is separate. Conditional
coverage and an independently safe finite-cost fallback are distinct inputs.

## B5. Joint selection, fees and terminal identity

The comparator is the same certified policy class and the same augmented
objective. Two exact policies with control costs 0 and 1 but setup fees 10
and 0 must be selected by total 10 versus 1. No zero-error model transfer
claim permits removing the fee after optimization. The finite selector control
also chooses different certified actions from different nominal data models;
both obey the same confidence region's uniform certificate.

With two absorbing outcomes g and f, kernels reaching g surely versus f
surely have identical zero killed kernels and zero continuation cost, yet
their terminal-success probabilities differ by 1. Hence WTT-2 separately
uses full-row TV for terminal-event transfer.

## B6. The adjacent parent boundary is explicit

ARC-2 (lines 76–100 in the pinned parent) transfers every data-selected
finite horizon and explicitly excludes infinite-horizon risk. FMT-2 is
finite-horizon; CMP5 supplies summable-error or discounted bounds.
SPS assumes the exact known kernel. None states the false inference in B1.
WTT supplies their missing quantitative undiscounted transfer interface.
Weighted geometric drift is sufficient, not asserted necessary for every
proper policy. It does not supersede SPS's larger exact-model proper class.

## B7. Expected cost is not an unmodelled observation channel

Suppose an initial stage reveals charge Z and reaches an unchanged next-state
label. Q has Z=1 surely; P has Z=0 or 2 equally likely. Both expected stage
charges are 1. A common learner pays 10 at the next stage only after Z=1,
otherwise stops freely. If Z is omitted from the kernel's observed state,
eta=zeta=0 falsely predicts equal cost: Q costs 11, P costs 1.
The repaired interface includes the revealed Z in the successor state.
Then the full row laws differ (TV=1), and the weighted certificate correctly
accounts for the policy-relevant difference. This is an exact two-stage
countermodel, not random charge measurements.

## B8. Properness need not admit this geometric certificate

On X={1,2,...}, move from n to n+1 with probability (n/(n+1))^2 and
otherwise stop; charge 1. Starting at 1, telescoping products give
Pr(tau>t)=1/(t+1)^2. Hence E tau=sum_(k>=1)1/k^2<=2 is finite.
If a WTT certificate with finite w(1) and beta<1 existed, WTT-1 would give
1/(t+1)^2<=w(1) beta^t for every t, impossible since geometric decay is faster
than polynomial decay. Thus the sufficient weighted geometric regime excludes
some proper countable-state policies. No claim of necessary geometric drift
or full coverage of all proper policies is made.
