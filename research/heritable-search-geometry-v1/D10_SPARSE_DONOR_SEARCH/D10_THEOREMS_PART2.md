# D10 — Sparse Donor-Search Theorems, part 2 (HSG-T59 … HSG-T64)

---

## HSG-T59 — Hierarchical donor search (parent reconstruction + hostile)

proof_class: P3_PARENT_RECONSTRUCTION | status: PARENT_RECONSTRUCTED | hostile: logged

<statement id="HSG-T59">
Hierarchical donor search (parent: Bubeck–Munos–Stoltz–Szepesvári 2011, HOO / X-armed
bandits). If donor utility f is locally Lipschitz with respect to a dissimilarity ℓ that
is known to the decision maker, and a hierarchical binary covering tree of the donor
space is well behaved with respect to (f, ℓ) (cell diameters shrink along paths so that
near-optimal cells exist at bounded depth), then optimistic hierarchical refinement
(HOO-style: expand cells whose optimism bound is highest) concentrates evaluation mass on
near-optimal donors with expected regret bounded up to a logarithmic factor by √n, with
the constant tied to the local geometry of f around its maxima (near-optimality
dimension). A Higgs-style donor — far under the chosen dissimilarity yet structurally
useful — falsifies the dissimilarity and any router built on it, not the existence of
remote analogy.
</statement>

### Parent reconstruction — exact assumption list

Source: S. Bubeck, R. Munos, G. Stoltz, C. Szepesvári, "X-Armed Bandits", JMLR 12,
2011, jmlr.org/papers/v12/bubeck11a.html. Abstract-level claims verified against the
source page at freeze time (marked [V]); body-level theorem details carry
PARENT_STATEMENT_UNVERIFIED_TEXT (paper body not fetched).

1. Arms form a generic measurable space X (here: the donor universe). [V]
2. Each pull of arm x returns an i.i.d. payoff with mean f(x); only f matters to regret.
3. Local Lipschitz assumption: f is locally Lipschitz with respect to a dissimilarity ℓ
   known to the decision maker. [V — abstract] The parametrized body form (there exist
   ν > 0, ρ ∈ (0,1] with |f(x)−f(y)| ≤ ν ℓ(x,y)^ρ near the maxima) is
   PARENT_STATEMENT_UNVERIFIED_TEXT.
4. Hierarchical partition: a binary tree covers X, each node a cell, children partition
   the parent; the tree is well behaved w.r.t. (f, ℓ): near-optimal cells of shrinking
   diameter exist along some path (near-optimality dimension d defined from the covering
   numbers of near-optimal sets). PARENT_STATEMENT_UNVERIFIED_TEXT (exact Assumption 2).
5. HOO: maintains per-node optimistic upper confidence bounds B computed from cell
   diameter and empirical means; at each round descends the path of maximal B and samples
   a point in that cell.
6. Under 1–5: the expected regret of HOO is bounded up to a logarithmic factor by √n
   (verified, abstract [V]); the growth rate is independent of the ambient dimension; and
   HOO is minimax-optimal when the dissimilarity is a metric [V]. The finer instance-
   dependent form (constants depending on ν, ρ and the near-optimality dimension d of f
   w.r.t. ℓ) is PARENT_STATEMENT_UNVERIFIED_TEXT.

Absorption: donors (or donor regions) = arms; reading/evaluating a candidate = pulling;
f = expected fragment value. HOO-style optimistic refinement over a hierarchical topic
tree is the exact parent for "concentrate donor search where the geometry says near-optima
lie, at regret cost tied to local geometry".

### REQUIRED HOSTILE — decoy dissimilarity with a far optimum (toy instance)

Instance (1-D, fits on one page). Donor space X = [0,1], chosen dissimilarity
ℓ(x,y) = |x−y|, and mean value

  f(x) = 1/2 for x ∈ [0, 1−δ],   f(1) = 1,   linear interpolation on (1−δ, 1),

with δ small. The bulk mode near 0 is a broad shelf of mediocre donors; the unique
optimum is the single arm at x = 1, maximally far (ℓ-distance 1) from the shelf. Fit the
Lipschitz constant to what the shelf reveals: any (ρ=1)-Lipschitz bound valid across the
jump requires ν ≥ (1 − 1/2)/δ = 1/(2δ); with ν that large the optimism bonus on EVERY
cell of diameter ~δ is ≥ 1/2 everywhere, so the tree gives no discrimination — the
regret-bound constant degrades to vacuous. If instead ν is fit to the smooth shelf
(ν ≈ 1/2 · slope of the shelf, small), the bound is simply invalid at x = 1. Either way
HOO's concentration follows ℓ, and ℓ certifies the far arm as the worst candidate: an
ℓ-driven router never refines toward x = 1 while the shelf exists. The structural truth
is that x = 1 IS the remote analogy (e.g. its hidden attribute vector — the donor's
"Higgs-ness": a shared, rarely instantiated structural motif — matches the target atom's
need), but that attribute is not the coordinate ℓ measures.

Kills: the validity of the chosen dissimilarity ℓ (assumption 3) and any router/tree
built on it — NOT the existence of remote analogy, and not the parent theorem (the parent
never claims every ℓ is valid; it conditions on a correct one).

Verdict: LIFT_CONDITIONAL — the lift (optimistic hierarchical concentration at geometry-
tied regret) holds iff the dissimilarity is validated against measured donor values;
the hostile mandates a metric/router-validation step (held-out donor values vs ℓ-neighbors;
dissimilarity learned from observed co-utility, not assumed) before HOO-style routing is
trusted with remote discovery.

Parents: [Bubeck–Munos–Stoltz–Szepesvári 2011, jmlr.org/papers/v12/bubeck11a.html,
assumptions_reconstructed: true].
<!-- end HSG-T59 -->
---

## HSG-T60 — Successive-depth allocation (parent reconstruction + hostile)

proof_class: P3_PARENT_RECONSTRUCTION | status: PARENT_RECONSTRUCTED | hostile: logged

<statement id="HSG-T60">
Successive-depth allocation (parent: Jamieson–Talwalkar 2016, successive halving for
non-stochastic best-arm identification). Model donors as arms whose value estimate
improves monotonically with reading depth, under a total reading budget. Successive
halving evaluates arms in parallel at a common depth, keeps the top fraction by estimated
value, and repeats, thus allocating geometrically larger reading budgets to survivors;
within its registered model (fixed total budget, value estimates that concentrate at the
allocated depths, and a best arm separated from the rest) it identifies the best arm with
a budget within logarithmic factors of the lower bound. A late-blooming donor whose value
appears only at full reconstruction depth is discarded by any halving schedule whose
elimination rounds precede that depth; the required mitigation is a frozen exploration /
late-bloomer lane (issue #221).
</statement>

### Parent reconstruction — exact assumption list

Source: K. Jamieson, A. Talwalkar, "Non-stochastic Best Arm Identification and Hyperband
Applications", ICML 2016, proceedings.mlr.press/v51/jamieson16.html. The page was not
fetched at freeze time; parent-side claims below are reconstructed from standard
presentations of the paper and carry PARENT_STATEMENT_UNVERIFIED_TEXT. (Hyperband's
bracket structure as implemented in the paper is public knowledge; the exact theorem
statements were not verified.)

1. K arms, one designated best by realized value; values are fixed (non-stochastic), no
   stochastic reward noise beyond the finite-sample error of an arm's evaluation at a
   given resource level.
2. A total evaluation budget n is fixed in advance.
3. Resource levels r (here: reading depth) index evaluation fidelity: an arm evaluated at
   resource r yields an estimate whose error is nonincreasing in r (more depth, better
   estimate of the donor's true value).
4. Successive halving (SH): one round = evaluate all surviving arms at a common resource
   level, then discard all but the top ⌈(#survivors)/η⌉ by estimated value (η > 1, the
   paper's canonical η = 2 halves each round); repeat until one arm remains; total budget
   split so survivors' resource grows geometrically across rounds.
5. Registered model guarantee: if the best arm's true value exceeds every other arm's by
   at least Δ at every resource level SH reaches (i.e., no ranking inversions at the
   evaluated depths involving the best arm), then SH outputs the best arm with high
   probability, with total budget within logarithmic factors of the non-stochastic lower
   bound (order (K/Δ²) log K up to log factors). PARENT_STATEMENT_UNVERIFIED_TEXT (exact
   theorem statement, constants, and the log-factor accounting).

Absorption: donors = arms; reading depth = resource r; estimate at r = fragment value
estimated from a depth-r read. This is the exact parent for the programme's
successive-depth donor triage: cheap shallow screen of many donors, geometric deepening
of survivors.

### REQUIRED HOSTILE — late-blooming donor (smallest instance)

Instance. K = 2 donors, A and B*, one elimination round in the schedule. True values:
value(A) = ε (small but positive, visible at ANY depth ≥ 1); value(B*) = 1, but B*'s
signal is present only at depth ≥ d* (full reconstruction): at every depth r < d*, the
depth-r estimate of B* is 0 (its usefulness lives in a construction that only exists once
the donor's content is fully reconstructed — e.g., a proof technique embedded in an
appendix-level corollary reachable only after the full chain is re-derived). Budget
forces round 1 to run at depth d_1 < d* (otherwise the schedule is exhaustive on both
arms and not a halving schedule at all). Round 1 estimates: A = ε, B* = 0. SH keeps the
top ⌈2/η⌉ = 1 arm: A survives, B* is discarded — deterministically, whatever η > 1 and
whatever the budget split, because B* occupies the last rank at every depth SH ever
reaches before eliminating it. The output is A (value ε) while B* (value 1) is lost.

Kills: assumption 5's premise ("best arm separated at every resource level SH reaches") —
the hostile donor is separated the WRONG way at shallow depths (ranked last), so the
registered-model guarantee simply does not apply; within its own model SH remains correct
and near-optimal. The hostile kills the transfer of SH to donor universes containing
late-blooming structure, not the parent theorem.

Verdict: LIFT_CONDITIONAL — successive-depth triage lifts (near-optimal within log
factors) only over the registered model; late-bloomer donors fall outside it. Required
mitigation, registered: a frozen exploration / late-bloomer lane (issue #221) — a fixed
budget share, decided before the campaign and reported with its cost, that carries a
small number of donors to FULL reconstruction depth outside the halving ladder, immune to
early elimination. The frozen share is a structure assumption under T55/T63 accounting,
not a free lunch.

Parents: [Jamieson–Talwalkar 2016, proceedings.mlr.press/v51/jamieson16.html,
assumptions_reconstructed: true].
<!-- end HSG-T60 -->
---

## HSG-T61 — Cross-atom donor amortization (new proof, conditional use)

proof_class: P1_ELEMENTARY | status: PROVED | hostile: none

<statement id="HSG-T61">
Cross-atom donor amortization. Suppose extracting a reusable donor motif from discipline
d costs C_d once, and mapping that motif to atom i costs c_i, i = 1..m. Then the average
cost per atom of read-once-map-many is C_d/m + (1/m)Σ_{i=1}^m c_i, versus
C_d + (1/m)Σ_{i=1}^m c_i under independent per-atom rereading; the saving is
(1 − 1/m) C_d per atom. Amortization dominates exactly when the amortized total
C_d + Σ_{i=1}^m c_i is below the counterfactual cost of obtaining the same m mappings
without reuse, which requires C_d large relative to the mapping costs c_i and actual
reuse by the m atoms (m ≥ 2 realized reusers; failed reuse with m' = 1 realized reusers
leaves C_d as pure overhead). Load-bearing architecture rule: do not reread the same
discipline independently per atom.
</statement>

### Proof

Cost model. One pass over discipline d that extracts the reusable motif (the generalized
technique, stripped of the discipline's local notation) costs C_d; this cost is incurred
once per extraction. Each deployment of the motif onto atom i — recognition that the
motif applies, plus the adaptation — costs c_i. Read-once-map-many total cost:

  T_amort = C_d + Σ_{i=1}^m c_i   ⇒   average per atom = T_amort/m = C_d/m + (1/m) Σ_i c_i.

Independent per-atom rereading (the atom's own pipeline re-derives the extraction from
the raw discipline each time) costs T_reread = Σ_i (C_d + c_i) = m·C_d + Σ_i c_i, i.e.
average per atom = C_d + (1/m) Σ_i c_i. Difference:

  T_reread − T_amort = (m − 1)·C_d,  i.e. per-atom saving (1 − 1/m)·C_d.

Both expressions are arithmetic identities under the stated cost model (single
extraction cost, additive mapping costs). ∎

Dominance condition (the CONDITIONAL part). Amortization dominates its counterfactual
iff T_amort < T_cf, where T_cf is the cost of obtaining the m mappings without reuse.
Under the rereading counterfactual this is (m−1)C_d > 0 — always true for m ≥ 2 and
C_d > 0. But dominance in the stronger, decision-relevant sense requires:

1. C_d large relative to Σ c_i (else the saving (1−1/m)C_d is negligible against
   coordination overheads the identity does not see: motif registry maintenance, version
   drift, validation of each mapping — each of which must itself be registered as a cost
   line, not assumed zero).
2. Realized reuse m' ≥ 2: the identity's m is the number of atoms that ACTUALLY reuse
   the motif. If only m' of the m planned atoms reuse it, the realized average is
   C_d/m' + (1/m')Σ_{i≤m'} c_i; at m' = 1 the extraction cost is carried entire by one
   atom and amortization was a pure loss (the motif-cache risk).

### Architecture consequence (registered rule)

"Do not reread the same discipline independently per atom" is load-bearing: any lane that
re-derives an extraction already available in the motif store pays m·C_d where C_d
suffices. The rule binds the architecture (a shared motif store keyed by discipline, with
per-atom mappings recorded as reuse events so the realized m' is measurable), not any
individual campaign.

### Residual

The identity says nothing about whether a motif EXISTS that transfers to m ≥ 2 atoms —
that is an empirical property of the donor and the atom set, measured by realized reuse
counts (m'), and folded into the T62 donor-value matrix as observed structure.
<!-- end HSG-T61 -->
---

## HSG-T62 — Low-rank donor map as conditional compression hypothesis

proof_class: P5_CONDITIONAL | status: CONDITIONAL | hostile: none

<statement id="HSG-T62">
Low-rank donor map as a conditional compression hypothesis (parents: Candès–Recht 2009
matrix completion; factorization bandits). Let R[a,d] denote the donor-value matrix over
atoms a ∈ A and disciplines d ∈ D. If R is well approximated by rank r ≪ min(|A|,|D|),
then a latent-motif factorization R ≈ U Vᵀ with U ∈ R^{|A|×r}, V ∈ R^{|D|×r} represents
it with O(r(|A|+|D|)) parameters versus O(|A||D|) for the dense map. Recovery of UNSEEN
entries from a sampled subset of observed entries requires — and is not implied by — low
rank plus incoherence of the factors plus sufficient random-like sampling of the observed
entries; absent those conditions no recovery guarantee holds. Status stays CONDITIONAL:
the programme must measure the empirical rank / singular-value decay of observed entries
and the stability of predictions under held-out entries before adopting the factorized
hypothesis; no unconditional recovery claim is made.
</statement>

### Parent reconstruction — exact assumption list

Sources: E. Candès, B. Recht, "Exact Matrix Completion via Convex Optimization",
Foundations of Computational Mathematics 9, 2009, doi:10.1007/s10208-009-9045-5;
factorization bandits (as a registered model class for parameterized value matrices).
The source was not fetched at freeze time; the sampling-complexity exponent below carries
PARENT_STATEMENT_UNVERIFIED_TEXT.

Matrix completion assumptions (Candès–Recht):

1. R ∈ R^{n_1×n_2} has exact rank r (later work relaxes to approximate rank).
2. Incoherence: the singular vectors are spread — no entry of the factors concentrates
   the matrix's mass (bounded coherence parameters for U and V, and for their product);
   without incoherence a low-rank matrix can hide its unobserved entries.
3. Sampling: m entries revealed uniformly at random (or an adequate random-like
   sampler); m on the order of n^{6/5} r log n for the square case n_1 = n_2 = n as
   stated in the 2009 paper (PARENT_STATEMENT_UNVERIFIED_TEXT: exact exponent and
   constants), improved by later work toward near-linear sampling.
4. Under 1–3, nuclear-norm minimization recovers R exactly with high probability. NO
   claim survives dropping 2 or 3: adversarial or structured (e.g. all-of-one-row)
   sampling voids recovery.

Factorization bandits (registered model class): the value matrix is parameterized as a
low-rank factorization and the learner acts/observes entries to both exploit and identify
the factors; its guarantees likewise condition on the low-rank hypothesis holding.

### Why CONDITIONAL in OCM/HSG (and the measurement protocol)

The programme does NOT presuppose that the donor-value matrix is low-rank. Whether a
small set of latent donor motifs explains atom×discipline usefulness is an empirical
question about the world. The hypothesis is registered with its falsification protocol:

- Measure: singular-value decay of the observed R[a,d] entries (empirical rank at a
  registered energy tolerance; fit of a rank-r truncation as a function of r), on the
  programme's accumulated donor-read receipts.
- Measure: held-out stability — predicted vs realized value on held-out (atom, donor)
  pairs; the compression hypothesis is supported only if held-out error tracks the
  in-sample fit, and is REFUTED (for the corpus measured) if apparent rank is high or
  held-out error diverges.
- Register: the sampling pattern of observed entries (which cells of R the programme has
  actually read) — an incoherence/sampling audit is mandatory before any recovery claim;
  a router that reads only predicted-good cells produces structured sampling, which
  violates assumption 3 and can fake low rank or hide it (ties to the T63 exploration
  requirement).
- Decision rule: adopt the factorized representation only while the held-out protocol
  supports it; on divergence, fall back to the dense/observed-only map with T55 costs.

No arbitrary numeric thresholds: tolerances and ranks are read off the measured decay and
held-out error curves and registered per corpus, not fixed here.

Parents: [Candès–Recht 2009, doi:10.1007/s10208-009-9045-5, assumptions_reconstructed:
true; factorization bandits (model class, no single canonical citation registered),
assumptions_reconstructed: true].
<!-- end HSG-T62 -->
---

## HSG-T63 — Exploration mass necessary for unmodelled remote donors (limit + policy)

proof_class: P1_ELEMENTARY | status: PROVED | hostile: none (adversary is the proof)

<statement id="HSG-T63">
Exploration mass necessary for unmodelled remote donors. Any deterministic top-k router
that only ever inspects donors inside its own predicted set of size k < n is defeated by
an adversary who places the only useful donor outside that set: the router inspects
exactly its predicted set, never finds the useful donor, and reports failure with
probability one. Therefore open cross-domain discovery requires (a) a coverage theorem
relative to explicit structure assumptions — guarantees hold only over the assumed
structure class — or (b) nonzero exploration mass over under-modelled or far regions.
This does not make uniform random search efficient: the escape is exploration guided by
novelty, diversity, or uncertainty, with its cost explicitly reported.
</statement>

### Proof

Model. Donor universe D with |D| = n; exactly one donor is useful. A deterministic
top-k router is a map r from the router's information state (history of inspections and
their outcomes) to a predicted set S ⊆ D with |S| = k < n; a pure top-k router inspects
only within S_t at each step t and terminates when S is exhausted or the useful donor is
found.

Adversary argument. Fix the router r. At every step, r's constraint is to inspect only
inside its current predicted set S_t, and |S_t| = k < n at the start, so
D \ S_1 ≠ ∅. Consider the donor configuration u* ∈ D \ S_1 (the useful donor is any
discipline outside the router's FIRST predicted set; the router may adapt S_t later, but
only as a function of inspection outcomes, and by the model every inspection of a
non-useful donor returns only "not useful", carrying no information that identifies u*
among the never-inspected complement). Two cases: (i) the router never expands beyond
predicted sets built from "not useful" feedback — since feedback is uninformative about
the complement, every inspected donor lies in the union of its predicted sets; choose
u* outside the union of all sets the router can ever reach, which is nonempty whenever
the router's total inspected set has size < n. (ii) The router's total inspection
eventually covers all of D — then it is exhaustive and pays the T55 cost, contradicting
the "sub-exhaustive router" premise. Hence for every deterministic top-k router that
inspects fewer than n donors in total, there exists a donor configuration (u* outside its
realizable inspection set) on which the router misses the only useful donor with
probability 1. Randomized routers are convex combinations of deterministic ones: some
deterministic realization has positive weight, so the miss probability of a randomized
pure-router is strictly positive on the corresponding configuration. ∎

Corollary (the fork). Open cross-domain discovery therefore requires one of:

(a) a coverage theorem under EXPLICIT structure assumptions — e.g. "if donor usefulness
is (locally) Lipschitz w.r.t. dissimilarity ℓ (T59) / adaptively submodular (T58) /
reservation-indexed (T57), then policy X attains guarantee Y over that class" — where
the guarantee is conditional on the class, with its hostiles registered; or
(b) nonzero exploration mass over under-modelled / far regions: with probability
bounded away from zero, inspect donors outside the predicted set, chosen by
novelty/diversity/uncertainty signals.

### Policy note (what the theorem does NOT say)

This limit does NOT make uniform random search efficient. By T55, unstructured uniform
inspection over a far region of size n−k hits a specific remote donor with probability
mass 1/(n−k) per draw — the exploration budget is spent at the unstructured rate.
The correct reading: exploration mass is a NECESSARY condition for coverage of
unmodelled regions; its EFFICIENCY must come from guided exploration (novelty, diversity,
uncertainty — i.e., structure learned about the region as it is explored), and the
exploration cost (budget share, expected hits, realized miss rate) must be REPORTED with
the campaign, not buried. Registered accounting: exploration share, donors inspected
outside predicted sets, and useful donors found by exploration vs prediction.

### Residual

The theorem fixes the necessity of exploration mass, not its allocation law. The
allocation law (how to rank under-modelled regions by novelty/diversity/uncertainty) is
empirical machinery registered elsewhere; its cost accounting is mandatory here.
<!-- end HSG-T63 -->
---

## HSG-T64 — Rational metaresearch / VOC stopping (parent reconstruction)

proof_class: P3_PARENT_RECONSTRUCTION | status: PARENT_RECONSTRUCTED | hostile: none

<statement id="HSG-T64">
Rational metaresearch / VOC stopping (parents: Russell–Wefald 1991; Hay–Russell–Tolpin–
Shimony 2012). Treat a research action (reading a donor, mapping a motif, running a
proof attempt) as computation: its expected metalevel value equals the expected
improvement in the quality of the downstream object-level scientific decision minus the
reading/mapping/proof cost it incurs. The rational policy performs the next action while
its expected metalevel value is positive and redirects or stops when it is nonpositive,
evaluated under the frozen metalevel model. This stopping rule is exact only in special
cases with Pandora-type structure (where reservation values solve the stopping problem
exactly, T57); in general it defines an explicit bounded-rational control objective, not
a universal theorem.
</statement>

### Parent reconstruction — exact assumption list

Sources: S. Russell, E. Wefald, "Do the Right Thing: Studies in Limited Rationality"
(precised in "Principles of metareasoning", Artificial Intelligence 49, 1991,
doi:10.1016/0004-3702(91)90015-C); N. Hay, S. Russell, D. Tolpin, S. Shimony,
"Selecting Computations: Theory and Applications" (later titled "Bounded rational
metareasonation..."), arxiv.org/abs/1207.5879. Neither source was fetched at freeze
time; parent-side statements below are reconstructed from standard presentations and
carry PARENT_STATEMENT_UNVERIFIED_TEXT.

Russell–Wefald metareasoning assumptions:

1. An object-level task with a decision (action choice) whose expected utility given the
   current internal state can be estimated; internal computation changes the state and
   hence the decision's expected utility.
2. Computation is itself an action with a cost (time/attention/cash) charged against the
   same utility scale.
3. Value of computation (VOC): E[utility of the decision after the computation] −
   E[utility of the decision before] − cost of the computation.
4. Rational meta-level policy: perform the computation with maximal positive VOC; stop
   computing when no available computation has positive VOC.
5. KEY LIMIT acknowledged by the parents: evaluating VOC exactly is itself a computation
   with its own cost — the full meta-level optimum is generally intractable
   (PARENT_STATEMENT_UNVERIFIED_TEXT: the exact intractability statements as worded in
   the sources); the framework therefore licenses bounded approximations (e.g. myopic VOC:
   evaluate one step of computation ahead, ignoring its knock-on computations).

Hay–Russell–Tolpin–Shimony (registered model): computations as selections under limited
resources; myopic VOC-based selection, with the observation that for certain problem
structures (their analysis includes Pandora-like settings) the myopic policy is optimal
or near-optimal, while in general it is a heuristic with regret relative to the
uncomputable full meta-level optimum. PARENT_STATEMENT_UNVERIFIED_TEXT (the exact
optimality scope).

### Absorption into OCM/HSG

Map: research action = computation (read donor d at depth r; map motif to atom; attempt
lemma); object-level decision = the programme's next scientific commitment (which
donor/atom/proof to spend the next budget unit on, or stop the campaign); frozen
metalevel model = the registered cost lines (reading cost c_d, mapping cost, proof cost)
and the registered value model for downstream improvement. The stopping rule is then:
continue while estimated metalevel VOC > 0; stop/redirect at nonpositive VOC. Exactness:
in Pandora-structured subproblems (independent donors, known priors, scalar max-value —
T57's assumption list) reservation values implement the optimal stop; outside them the
programme's VOC is a myopic estimate under a frozen model and is reported as such.

### Residual

The rule is a control objective, not a guarantee: VOC estimates can be wrong (prior
misspecification), and the theorem-quality of any campaign rests on the frozen model's
own registration. Mandatory reporting: the metalevel model version, the realized VOC
trajectory, and the stop decision's conditioning — so that stop decisions are auditable
rather than folklore. No universal stopping theorem for science follows from the
parents; only the disciplined objective.
<!-- end HSG-T64 -->

---

## D10 census (as landed)

| id | proof_class | status | hostile |
|----|-------------|--------|---------|
| HSG-T55 | P1_ELEMENTARY | PROVED | none (adversary in proof) |
| HSG-T56 | P1_ELEMENTARY | PROVED | none |
| HSG-T57 | P3_PARENT_RECONSTRUCTION | PARENT_RECONSTRUCTED | none |
| HSG-T58 | P3_PARENT_RECONSTRUCTION | PARENT_RECONSTRUCTED | complementary pair, LIFT_CONDITIONAL |
| HSG-T59 | P3_PARENT_RECONSTRUCTION | PARENT_RECONSTRUCTED | decoy dissimilarity, LIFT_CONDITIONAL |
| HSG-T60 | P3_PARENT_RECONSTRUCTION | PARENT_RECONSTRUCTED | late bloomer, LIFT_CONDITIONAL |
| HSG-T61 | P1_ELEMENTARY | PROVED | none |
| HSG-T62 | P5_CONDITIONAL | CONDITIONAL | none |
| HSG-T63 | P1_ELEMENTARY | PROVED | none (adversary in proof) |
| HSG-T64 | P3_PARENT_RECONSTRUCTION | PARENT_RECONSTRUCTED | none |

End of D10.
