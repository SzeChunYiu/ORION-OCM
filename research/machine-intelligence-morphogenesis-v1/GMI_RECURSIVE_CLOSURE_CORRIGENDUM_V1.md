# Recursive closure corrigendum and proof ledger v1

Date: 2026-09-12. Inspected base: `f211f99a9aaefcfcca05850e1930885701358bcc`.

This is an additive corrigendum. It supersedes only the explicitly identified conclusions below; original claims, predictions and receipts are preserved. No historical failure is converted to a pass. The two programme-wide terminal strings remain FALSE.

## Evidence and review boundary

Executed sources: `run_gmi_developmental_falsification_v1.py`, `run_gmi_primitive_closure_v1.py`, `run_gmi_closure_successor_v1.py`. Primitive source and prediction freeze were committed before execution at `66aa16fbf4f390f4afac56e46d8971768e27f9ea`; successor freeze before its execution at `1e0a57a62af0da5c2faba3e9562c3c48fa3b1ea3`.

Review was separated into formal logic, experimental design, resource accounting and adversarial parent-reduction passes by one author. These are NOT independent human/model reviewers. The scalar witness evaluator differs from the bit-parallel synthesizer, but shares a runtime and author; common-mode implementation errors remain possible. No Lean proof, full repository test suite, independently blinded experiment, learned held-family predictor or real-regime transfer was executed in this tranche.

## RC-01 — original developmental DP-1 is false

Source: `GMI_DEVELOPMENTAL_POTENTIAL_AND_CRITICAL_BURDEN_V1.md`, theorem DP-1. Its premise `L_A <= epsilon_A` is an upper bound. It cannot supply the lower bound used in the purported pure-A impossibility conclusion.

Exact witness: take a singleton pure-A class with `(L_A,L_B)=(0,1/2)`, `epsilon_A=3/4`, `delta_B=1/2`, `epsilon_B=1/8`, `L_star=1`. Every original premise holds: `epsilon_A+delta_B=5/4>1`, while `epsilon_A+epsilon_B=7/8<=1`. A composite preserving `L_A=0` and achieving `L_B=1/8` is available. Nevertheless pure A already has total loss `1/2<=1`. Status of the original conclusion: **FALSIFIED**.

### Corrected theorem

If EVERY pure-A realization has `L_A>=ell_A` and `L_B>=delta_B`, and `ell_A+delta_B>L_star`, none meets the additive-loss threshold. If a legal composite is CONSTRUCTIVELY shown to satisfy `L_A<=u_A`, `L_B<=u_B` with `u_A+u_B<=L_star`, it meets that loss threshold. Other risk, budget and breadth requirements still need separate verification.

Proof: add the two uniform lower bounds for pure A; add the two constructive upper bounds for the composite. The directions must not be interchanged. More generally use a joint lower bound on `inf_M (L_A(M)+L_B(M))`, which can be stronger than adding separate infima. No architectural label enters this argument. The correction changes only the failed bound-direction atom.

Terminal: **CLOSED-FORMAL at the stated additive-loss scope**. Fresh denominator-7 finite checks: 3,136 lower-bound implications and 3,920 upper-bound implications; zero failures. These finite checks calibrate the implementation; the inequality proof covers all real-valued losses satisfying the premises.

## RC-02 — pointwise capability is an outer bound, not joint attainability

Source: the pointwise reachable envelope and breadth definitions in the developmental-potential document; related vector supremum in `GMI_DOMAIN_CAPABILITY_ENVELOPE_V1.md`.

With two equally weighted obligations and reachable fixed-state success vectors `(1,0)` and `(0,1)`, pointwise maximization reports breadth 1 but no single reachable state has breadth above 1/2. This falsifies the JOINT-ATTAINMENT INTERPRETATION, not the pointwise definition itself.

Let `R(b)` be the common set of legally reachable deployed states, including any router, switching policy and its charged development and serving budget. Define

`B_joint(b) = sup_{s in R(b), hard constraints satisfied} sum_e mu_e 1[Q_e(s)>=q_e]`.

For each state and each obligation, success is no greater than the pointwise success supremum. Summing and then maximizing proves `B_joint<=B_pointwise`. Equality requires one feasible state attaining the required coordinates simultaneously, or an explicitly admitted, paid adaptation policy. The attainable capability SET and its Pareto frontier, not the coordinatewise maximum vector, are the correct joint objects.

Terminal: **CLOSED-FORMAL under the common-state/common-budget constitution**. Fresh microscope: all 512 three-state/three-obligation binary success matrices over four nested budgets, 2,048 cases, zero inequality violations, 354 strict pointwise overstatements. Different task-specific development budgets define a different constitution and are not counterexamples to this theorem.

## RC-03 — critical burden need not be attained at its infimum

A reachable adequate-state cost sequence `1+1/n`, with no adequate state of cost at most 1, has critical burden infimum 1. Therefore `B_available=B_dev*` does not imply reachability without an attainment assumption. For any budget strictly greater than a finite infimum of a nonempty feasible cost set, the definition of infimum supplies an adequate state below that budget. Equality requires, for example, a minimum or appropriate compactness and lower-semicontinuity conditions. Also, `B_dev*=0` makes the proposed ratio undefined unless a convention is registered.

Terminal: **CLOSED-FORMAL counterexample and corrected boundary statement**. Capability curves may retain an infimum but must not label the boundary as achieved. This is a mathematical proof, not an empirical scaling result.

## RC-04 — finite semantic state lower bound and causal placement

For histories define equivalence by equality of every registered future response under every legal continuation and intervention. Any exact deterministic state representation must distinguish inequivalent histories: otherwise the same state and future inputs give the same responses, contradicting a distinguishing continuation. If there are K finite equivalence classes, fixed-length state requires at least `ceil(log2 K)` bits. The class label realizes that bound when legal updates induce a right congruence and transition/response lookup is permitted and charged. This is a bound on finite bits, not on the number of arbitrary-precision real coordinates, and not a learning-time bound.

For two independent stored bits and a query arriving AFTER the storage cut, there are four distinguishable records, so one persistent bit is insufficient. Exhaustive enumeration of 256 one-bit encoder/decoder pairs found zero exact solutions, with minimum uniform error 2/8 over 2,048 scored outcomes. Two retained bits suffice. When the query arrives BEFORE the communication cut, sending its one answer bit suffices. Query timing changes the state/communication lower bound even when the final input-output function is identical.

For retain/overwrite streams, one bit stores the current value and zero bits cannot distinguish opposite initial values under a keep continuation. The update `u XOR (g AND (z XOR u))` realizes selective retention; 2,730 histories up to length five passed. All 16 unconditional affine Boolean transitions failed the selector truth table. This derives a conditional state update, NOT LSTM uniqueness or a general recurrent-versus-attention frontier.

Terminal: **CLOSED-FORMAL plus exact finite calibration** at these cuts. Practical quotient identification remains GKF-07/G2-01 OPEN-BLOCKING.

## RC-05 — certified minimum-cost primitive formula synthesis

Scope: finite expression TREES, preloaded Boolean input wires/constants, allowed NOT/AND/OR/XOR or the separate NAND/NOR bases, strictly positive integer primitive prices. No shared-subexpression DAG optimum, physical latency, arbitrary real arithmetic, data acquisition, training, storage or I/O optimum is claimed.

A certificate assigns each semantic truth table f a number d(f) and a formula witness. The checker verifies: terminals have cost zero; each witness computes f on all inputs with exact cost d(f); and every allowed primitive satisfies `d(op(a,b)) <= d(a)+d(b)+price(op)` (the unary version omits b).

Proof of optimality: structural induction bounds d(f) from above by the cost of every formula computing f, using the primitive inequalities. Thus d is a LOWER bound on the optimum. The checked witness supplies an UPPER bound equal to d. This certifies a global optimum within the finite-semantic, unbounded-formula-size grammar. Positive prices ensure a minimum exists; syntax is explicitly whitelisted. The search is an ordinary minimum-cost grammar derivation problem, not a new domain or distinct GMI optimizer.

The independent bounded-layer enumerator for four-input unit-price formulas is complete through cost four: an optimal tree has optimal subtrees, since a cheaper semantically equal replacement would lower its cost. Enumerating every unary predecessor and binary split of k-1, including each unordered pair for commutative operators, therefore enumerates every new behavior at cost k. Absence through layer four is a certified bound within this grammar, not a bound for general circuits.

Results: 2,560 three-input function/price optima across ten basis/price cells, 20,480 scalar witness rows, 1,705,984 Bellman inequalities and 857,344 search relaxations. Four-input layers contain 6, 22, 126, 691 and 3,031 newly reachable functions: 3,876 total, 25,085 relaxations and 62,016 independent witness rows. Eight hostile certificate mutations were rejected, including an architecture macro and illegal prices.

Terminal: **CLOSED-FORMAL certificate argument with EXECUTABLE FINITE MICROSCOPE**. A separate implementation or proof-assistant checker remains a concrete assurance improvement, not an accomplished independent review.

## RC-06 — exact all-positive-price selector crossover

For `select(s,a,b)=a if s else b`, let NOT=AND=OR cost 2 and XOR cost k>0. Then minimum FORMULA cost is `min(2+2k,8)`.

Upper bounds: `b XOR (s AND (a XOR b))` costs `2+2k`; `(NOT s AND b) OR (s AND a)` costs 8.

Lower bound: the RC-05 certificate at k=3 proves every formula costs at least 8. Write any formula cost as A+qk, where q is its XOR count and A is its non-XOR cost, an even integer. The selector is nonaffine (also checked against all 16 affine functions), so a formula needs AND or OR and A>=2. If q=0, the k=3 certificate gives A>=8. If q=1, A+3>=8 and parity give A>=6. If q>=2, A>=2. For 0<k<=3 these three cases each bound cost below by `2+2k`; for k>=3 monotonicity from the certified k=3 value gives the lower bound 8. The constructions attain both bounds.

The eight initial frozen integer-price predictions passed. A successor proof and 80 disjoint rational normalized price cells were frozen before the fresh run: non-XOR prices 22, XOR=m for 1<=m<=88 excluding multiples of 11. All 80 predictions `min(22+2m,88)` passed, certifying 20,480 additional function/price optima, 163,840 scalar witness rows and 15,749,120 Bellman inequalities. These are price holdouts, NOT architecture-family holdouts.

Negative twins always-keep and always-overwrite use zero INTERNAL operators with preloaded wires. They do not cost zero over a complete lifecycle. Interpret KF-17's older phrase 'zero-cost semantic switch' as a semantic identity only; a physical cost-free gate is not derived.

Terminal: **CLOSED-FORMAL at the registered formula grammar**, not Transformer/LSTM/MoE full-family closure.

## RC-07 — a low-order descriptor is not a sufficient cost statistic

Frozen trial descriptor: output one-count and ordered per-coordinate Boolean influence edge counts. It was tested against exact three-input costs and four-input cost<=4 feasibility.

The claim that this descriptor determines a unique label is **FALSIFIED**. Three-input truth-table integers 1 and 128 have descriptor `(1,1,1,1)` but costs 6 and 4 when all primitives cost 2. The descriptor discarded literal polarity relative to the priced carrier. Four-input functions 6 and 24 share descriptor `(2,2,2,2,2)`; 6 has a four-operator witness, while 24 is absent from all layers through four. The result does not falsify every conceivable GMI descriptor.

### Corrected information theorem

For a finite uniformly weighted collection, descriptor Z and target cost label Y, any deterministic Z-only point predictor has at least

`N - sum_z max_y count(z,y)`

errors. Choose the most frequent label within each descriptor cell to attain this lower bound. If exact recovery is required and Z is shared with the decoder, a fixed auxiliary alphabet must have size at least `max_z |Y(z)|`, and cell-specific indices attain that cardinality; the bit bound is its ceiling logarithm. The minimal zero-error set prediction contains all `Y(z)`. This is a reduction to elementary conditional coding, not a method for learning Y(z) without outcome access.

Observed lower bounds: 86 errors among 256 functions across 37 descriptor cells (35 ambiguous); and 2,572 feasibility errors among 65,536 functions across 893 cells (393 ambiguous). Additional worst-case COST-LABEL bits are 2 and 1 respectively; they are not full program-description or developmental-compute bounds.

The successor was frozen before testing all 9,330 binary-descriptor/ternary-label assignments for N=1..5 against all nine descriptor-only predictors: 83,970 predictor evaluations, zero error-identity, code or coverage failures. The original scalar prediction remains FALSIFIED. A cheap pre-outcome estimator of a narrow, useful cost set remains OPEN-BLOCKING with the closure tournament in the companion register.

Terminal: **FALSIFIED-AND-CORRECTED by exact information theorem**; estimator not closed.

## RC-08 — lifecycle selection is conditional on complete costs

For equal-quality admissible alternatives, prefer B over A exactly when

`build_B - build_A + R*(serve_B-serve_A) < 0`.

Division yields a threshold only with the proper inequality direction; handle equal serving costs separately. The microscope checked 67,473 build/serve/reuse tuples, zero discrepancies. This is an accounting identity, not evidence that build cost, reachability, failure risk or serving prices can already be predicted. Acquiring truth tables, discovering dependencies, optimizer trials, failed candidates, I/O, verifier work, communication, provenance and human work must be added before a real frontier claim.

Terminal: **CLOSED-FORMAL conditional accounting**. G2-07 and all practical cost-estimation dependencies remain OPEN-BLOCKING.

## Parent imports and non-novelty

The grammar-search parent is Knuth, *A Generalization of Dijkstra's Algorithm* (1977), with the grammar/hyperpath interpretation also explicit in Ramalingam and Reps, *An Incremental Algorithm for a Generalization of the Shortest-Path Problem* (1996). RC-05 supplies its own scoped certificate proof rather than importing unverified complexity bounds. Finite semantic-state arguments reduce to distinguishability/pigeonhole counting; RC-07 reduces to conditional coding. No distinct GMI gain over an identical, cost-complete ordinary synthesis parent is established: both optimize the identical object.

Original architecture papers are baseline definitions, not uniqueness theorems: Hochreiter and Schmidhuber (1997); Vaswani et al. (2017), arXiv:1706.03762; Hu et al. (2021), arXiv:2106.09685; Cohen and Welling (2016), PMLR 48:2990-2999; Xu et al. (2019), arXiv:1810.00826; Ho et al. (2020), arXiv:2006.11239. Their presence does not constitute a zero-prior derivation or a rerun of their experiments.

## Ledger delta and ceiling

Proof ledger: RC-01 old theorem FALSIFIED; corrected loss theorem closed at scope. RC-02/03 correct capability/development interpretation. RC-04..08 close only their registered algebraic, information and finite-formula atoms.

Closure ledger: G2-01/07/41/42/44/45 gain finite subchecks but remain OPEN-BLOCKING at programme scope. Known-form ledger: GKF-05/07 gain causal-cut and selector results; no full family is promoted to K4/K5/K6 by this tranche. The 24-family companion register makes the remaining derivation obligations explicit.

Domain ledger: all recovered Boolean forms and the compiler/search engine reduce to ordinary symbolic/classical programs. Same-grammar execution is an identity parent comparison; cross-substrate H0-H3 lifecycle separation was not tested. At H4 they belong to the existing classical computability super-domain. Number of new domains established here: zero.

Capability ledger: store jointly attainable capability sets and their Pareto frontiers; retain pointwise envelopes only as outer bounds. Developmental ledger: separate uniform lower bounds, constructive upper bounds, budget attainment and paid composition.

Claim ceiling: finite exact mechanism derivation, certified primitive synthesis, a prospective price law, preserved falsifications and explicit broader blocking experiments. Neither `NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE` nor `KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE` is issued.
