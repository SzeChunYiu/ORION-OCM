# FMT parent assimilation, acquisition and limits

## Primary sources actually read

| Parent | Faithful mechanism | Adaptation and omitted claims |
|---|---|---|
| [Weissman et al., HPL-2003-97R1 (2003), Theorem 2.1, pp. 2–6](https://shiftleft.com/mirrors/www.hpl.hp.com/techreports/2003/HPL-2003-97R1.pdf) | Finite iid empirical-row L1 concentration; their distribution-free consequence becomes a TV bound with exponent -2N epsilon². This is a mirror of the original HP report, not a secondary summary. | Union over supplied row alphabets; no claim to the sharper unknown-distribution-dependent exponent or sample optimality. |
| [Lobel and Parr (2024), arXiv v1, §3.2–3.5 and Appendix B](https://arxiv.org/html/2406.16249v1) | Overlap survives multiplicatively; their finite-horizon formula already improves the linearized simulation bound. | Couple full histories/private seeds, add actual stopped-state success and once-only terminal settlement, then combine with one data-confidence event. No new simulation lemma is claimed. |
| [Kearns and Singh (2002), §5.2, Lemmas 4–5](https://www.cis.upenn.edu/~mkearns/papers/reinforcement.pdf) | Model estimation feeds uniform policy-value control. | We do not import their exploration/mixing-time/sample-complexity guarantees. |
| [Kearns, Mansour and Ng (2002), §1–2](https://www.cis.upenn.edu/~mkearns/papers/sparsesampling-journal.pdf) | Generative access samples a requested state/action row and provides more access than one uncontrolled trajectory. | Our explicit complete fixed-N register is not their sparse-sampling planner. Row setup/reset is a supplied and charged apparatus. |

The direct internal parents are [PCA](https://github.com/SzeChunYiu/ORION-OCM/blob/8138e5c19e76205180bd8a8b71ad2160d13f54f2/research/gmi-grand-unification-v1/PROBABILISTIC_CONTROLLED_ACQUISITION_THEOREM_V1.md)
and [UMA](https://github.com/SzeChunYiu/ORION-OCM/blob/8138e5c19e76205180bd8a8b71ad2160d13f54f2/research/gmi-grand-unification-v1/FIXED_UNKNOWN_MODEL_ACQUISITION_THEOREM_V1.md).
FMT is their finite-data conditional bridge using established statistical and
control parents. It does not infer physical meaning, sufficient state or exact
support from finite observations. Learned confidence regions and supplied finite
hypothesis registers are different objects.

## Complete charge contract

Let R be the sampled row register. A fixed per-call bound a_r must cover state
preparation/reset, random-noise generation, the probe, sensing, recording and
any return/cleanup needed before the next independent call. If such a bound or
row access is unavailable, the sampling premise is undischarged. A reset must
preserve the fixed kernel and restore the registered row; reusing one noisy
reading N times is not N samples. Exact stopped or other known rows still need
an independently supplied support/kernel certificate and its verification cost.

Keep these setup quantities explicit, in actual native units or proved bounds:

    A_total = A_apparatus + A_support_and_cost_verification
            + N sum_(r in R) a_r + A_model(D)
            + A_synthesis(D) + A_compile(pi_D).

Counted acquisition is N|R| row calls. A raw outcome payload uses
N sum_r ceil(log2 k_r) bits with ordered call identities implicit only under
that registered encoding. A support-indexed count table uses
sum_r k_r ceil(log2(N+1)) bits; this checker instead maintains |S| count slots
per sampled row. Row labels, support dictionaries, headers,
source/model programs, costs, terminal predicates and raw-record custody are
additional stored objects. Storage is not identified with a terminal-action cut.

Synthesis counts visited subproblems, generated child-profile combinations and
weighted transition terms. All are separate from deployment J. Arithmetic bit
work, allocation, controller/model representation and compilation remain
additional measured or bounded terms; these finite operation counts are not
CPU time. Full history-tree enumeration may grow very rapidly. For m empirical
profiles the implemented mixture search examines m² ordered pairs, including
rejected/identical pairs, plus pure-policy candidates.

For L deployments, a declared lifetime coordinate is

    A_total + storage_rental(L) + sum_(ell=1)^L [J_P(pi_D)+sigma(pi_D)],

where sigma includes each fresh private policy-seed setup. In the finite
mixture checker sigma is a supplied nonnegative fixed charge for a nontrivial
initial mixture; pure trees have zero in that coordinate. It is not a universal
random-bit cost law. Other policy-dependent physical costs need their own
register before an architecture or lifetime superiority claim is licensed.

A synthetic charge example uses N=768 draws from one binary-outcome finish
row, 4 units per draw (prepare, draw, record, private randomness: one each),
and 12 setup units, totaling 3,084 acquisition/setup units in that declared
coordinate. With epsilon=1/16 and alpha=1/20, the exact confidence upper bound
is below alpha. The observed row is 720 successes and 48 failures. Risky finish
costs 1, known-safe finish costs 3, and failure settlement costs 4. At target
q=7/8 the certificate selects risky finish, with success interval [7/8,1] and
work upper bound 3/2. This is an arithmetic witness, not executed apparatus,
measured setup cost, or proof that 3,084 includes all physical resources.

## Finite falsification design

The policy oracle builds complete action/observation syntax without consulting
kernels or costs, then executes stochastic terminal paths. The sampling oracle
enumerates ordered sequences before aggregating counts; a separate multinomial
implementation gives the count law. The report compares every registered pair
of models and every complete finite policy, not separately optimized controls.

Controls expose half-L1 normalization, horizon indexing, post-transition costs,
missing terminal charges, policy changes, legal/cost-register changes, omitted
rows, false observed-support restriction, repeated correlated draws, model
drift and selection optimism. Singleton rows and absent sampling registers
have explicit no-error cases. No random trial or timing is used for evidence.

The exponential confidence certificate is evaluated with rational arithmetic:
exp(x) >= sum_(j=0)^m x^j/j!, hence A divided by that finite sum is a rigorous
upper bound on A exp(-x), clipped at one. This may be conservative; it never
rounds a floating-point estimate into a confidence certificate. The finite data
census tests the derived tail against exact event probabilities independently.

Remaining Q1 premises are real row access and independence, closed sufficient
state, verified action/terminal semantics, supplied support coverage and cost
bounds. Online adaptive sampling, learned alphabets, generic belief spaces,
infinite-horizon guarantees and unrestricted physical profiles remain open.
