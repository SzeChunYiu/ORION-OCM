# Decisive corrections and their boundaries

These are short analytic witnesses for the map correction, not a new
algorithm, experiment or theorem suite. Existing parent proofs retain
authority; the old text-pattern tests cannot establish these implications.

## C1 — a declared prior is compatible with the framework

Take two hypotheses with prior (1/2,1/2) and likelihoods (3/4,1/4)
for the acquired event. Formal O3 gives posterior (3/4,1/4), since the
normalizer is 1/2. This is an admitted derived GMI instance.
Thus “every GMI construction is prior-free” is false. A prior is optional
at the core level and load-bearing when that specialization is invoked.
Different priors can produce different decisions; none is supplied for free
by calling the ecology a class.

## C2 — the description-length bridge already exists

For fixed countable hypotheses and pre-data masses p_h>0 with sum at most one,
formal L2 defines

    b_h(n) = min(1, sqrt(log(2 n(n+1)/(delta p_h))/(2n))).

The bounded-loss tail probability at (h,n) is at most
delta p_h/[n(n+1)] when the unclipped radius is below one; radius one is
deterministically safe. Summing over h and n gives simultaneous coverage
at least 1-delta. Later selection within that fixed universe is covered.
A prefix-free code permits p_h=2^-L(h), so its penalty explicitly contains
L(h) log 2. This directly refutes the old map's merely-informal description.
It neither proves a data-selected-prior bound nor supplies the posterior-KL
change-of-measure argument of PAC-Bayes.
An optimizer's effective comparisons and acquisition costs remain separate.

## C3 — identification need not require a newly purchased intervention

Let X be a fair bit and E an independent bit of probability 1/4.
Supply the acyclic no-confounding model class X→Y with Y=X xor E.
Its supported observational conditional satisfies P(Y=1|X=1)=3/4,
equal to P(Y=1|do(X=1)). Under those declared causal restrictions,
the population effect is identified without a new intervention.
This does not make obtaining the observational law or doing inference free.
It distinguishes an identifying premise from a newly performed experiment.

Conversely, corrected CAU-1's two models X=U,Y=U and X=U,Y=X
have the same observational law but do(X=1) targets 1/2 and 1.
Unlimited repetitions of that observational interface cannot resolve them.
Payment and computation alone cannot make a nonidentifying interface identify;
new justified information or a narrower warranted model class can.

## C4 — optimal continuation at a tie is allowed

At state s let the terminal cost be 1. A cognitive edge costing 1 leads
to a terminal action of cost 0. Both the immediate and continued policies
serve with total cost 1. Positive edge cost supplies progress.
Therefore not every optimal policy obeys “continue iff value exceeds charge.”
That iff is correct for the expressly chosen stop-on-ties selector.
On a zero-cost self-loop with an available cost-0 terminal action, serving
value is 0 but the looping minimizing selector never serves.
Rank/properness premises cannot be removed by writing Bellman's equation.

## C5 — a one-shot exact obligation is not a Shannon-capacity claim

A binary symmetric channel with crossover 1/4 has overlapping output supports.
For exact decoding of a fair hidden bit in one use, every output remains
compatible with either bit, so no decoder guarantees correctness.
Yet its mutual information is 1-h_2(1/4)>0.
This inherited example distinguishes the criteria; it does not imply that
the channel has no value for approximate tasks or repeated coding.

## C6 — a conditional infinite-horizon theorem is already present

CMP5 bounds a measurable [0,1]-valued infinite-path functional by
min(1,sum_t e_t) under the common-history/initial-law kernel contract.
For identical pre-transition rewards in [0,1], discount gamma in (0,1)
and uniform TV error e, it bounds value error by the smaller of
1/(1-gamma) and gamma e/(1-gamma)^2.
Thus “no infinite-horizon control-performance guarantee” is too broad.
A zero-hazard model versus independent hazard e>0 has eventual-hazard
probabilities 0 and 1, so constant one-step accuracy does not give sure safety.
No generic physical-control guarantee follows from the discounted statement.

## What changed and what did not

The eight rows now point to conditional results and mature primary mechanisms.
Resource orders, task-relative adequacy and complete-history interfaces specify
the comparison; their presence alone is not technical novelty.
New kernel acquisition, empirical transfers, architecture search and physical
calibration were not executed for this documentation correction.
The unchanged original map, CORE and text-pattern script are archived with
their exact source commit and hashes. The script was retired from active
discovery because passing vocabulary constraints did not validate its premises.
