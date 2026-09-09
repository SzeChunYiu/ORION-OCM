# D10 — Sparse Donor-Search Theorems (HSG-T55 … HSG-T64)

Lane: HSG-D10 (ORION-OCM issue #233 work package). Layer: Epistemic Atlas — bounded
cross-domain donor-search programme. This directory ADDS new evidence only; it does not
modify frozen evidence elsewhere in `heritable-search-geometry-v1/`.

Row data: `D10_THEOREM_ROWS_V1.json`; mechanical fold: `REGISTRY_PATCH_D10.json`.
Theorem sections live in `D10_THEOREMS_PART1.md` (T55–T58) and `D10_THEOREMS_PART2.md`
(T59–T64). `statement_sha256` in each row is the sha256 of the exact text between the
`<statement id="HSG-Txx">` and `</statement>` markers below, extracted and hashed
mechanically at build time.

Status vocabulary: PROVED | PARENT_RECONSTRUCTED | CONDITIONAL | REFUTED_BY_HOSTILE | OPEN.
proof_class codes: P1_ELEMENTARY, P3_PARENT_RECONSTRUCTION, P5_CONDITIONAL.
Hostile verdicts: LIFT_SURVIVES | LIFT_CONDITIONAL.

---

## HSG-T55 — Unstructured donor-search lower bound

proof_class: P1_ELEMENTARY | status: PROVED | hostile: none (the adversary is part of the
proof, not a hostile instance)

<statement id="HSG-T55">
Let D be a set of n donor domains containing exactly one useful donor. Suppose (i) domains
are indistinguishable before inspection (the prior over which domain is useful is
exchangeable and no observable feature separates the useful domain), and (ii) inspecting a
domain reveals exactly whether it is useful. Then: (a) every deterministic inspection
strategy has a worst case of n inspections; (b) if the useful domain's location is uniform
over D, every inspection order has expected (n+1)/2 inspections. Consequently, no method
guarantees cheap remote discovery in a totally unstructured donor universe; any
sub-exhaustive advantage requires at least one of: learned prior structure, informative
cheap features, cross-atom reuse, or accepting nonzero miss probability.
</statement>

### Proof

Setting. An inspection strategy observes, one domain at a time, the label
u(d) ∈ {useful, not-useful}. By (ii) an inspection returns the label of the inspected
domain and nothing else; by (i) the labels of uninspected domains remain exchangeable
given everything observed so far. The strategy stops when it finds the useful donor (or
exhausts D).

(a) Worst case n inspections (adversary argument). Fix a deterministic strategy S. Because
labels of uninspected domains are exchangeable whatever S has seen, S's next-choice
function receives no label information that discriminates among uninspected domains; the
realized sequence of inspections of S is therefore a fixed (deterministic) order
d_1, d_2, …, d_n of D. Consider the donor configuration in which the useful donor is
u* = d_n. Running S on this configuration: the adversary (equivalently, nature) answers
"not useful" at d_1, …, d_{n−1}, each answer being the truthful label. S inspects d_n last
and finds u* only on inspection n. No deterministic strategy can avoid this: for any S,
the configuration with u* = d_n (last in S's own realized order) forces n inspections.
Hence worst-case cost = n over configurations, for every deterministic S.

(b) Expected (n+1)/2 under the uniform prior. Let the useful donor's index J in the
realized inspection order of S be random: J = j means the useful donor is d_j. Under the
uniform prior over D, exchangeability of uninspected domains makes J uniform on
{1, …, n} — the answers "not useful" to d_1 … d_{j−1} leave the remaining n−j+1 domains
exchangeable, so the posterior on each remaining candidate is equal. The number of
inspections is J, so E[inspections] = E[J] = (1/n) Σ_{j=1}^n j = (n+1)/2. This holds for
every deterministic order, hence for every deterministic strategy (by the reduction in
(a)), and randomized strategies are convex combinations of orders, so (n+1)/2 is also the
uniform prior expectation of any strategy that stops only upon finding the donor.

### Conclusion and use

- Exhaustive (n) and uniform-prior-average ((n+1)/2) costs are the operative numbers for a
  totally unstructured donor universe; they are costs of the universe's lack of structure,
  not of any particular method. No router, ranking, or heuristic beats them without
  importing one of the four escape channels named in the statement — each of which is a
  (falsifiable) structure assumption, registered elsewhere in the programme (T56 learned
  bridges; T58/T59/T60 structure classes; T61 reuse; T62 measured rank; T63 exploration
  mass at an explicitly reported cost).
- Reading: this is a limit theorem about the unstructured regime. It does not say donor
  search is hopeless; it says every claimed cheap-discovery method implicitly asserts
  structure, and that assertion must be registered and testable.

<!-- end HSG-T55 -->

---

## HSG-T56 — Structural-reminding distance (definition + additivity)

proof_class: P1_ELEMENTARY | status: PROVED | hostile: none

<statement id="HSG-T56">
Let P_t(y|x,c,H_t) be a retrieval kernel (probability that target y is retrieved from
current object x under context c and history H_t) and D = −log P its surprisal. For any
Markov retrieval path x = z_0 → z_1 → … → z_k = y whose probability factorizes over
transitions, the path surprisal is additive: D(path) = Σ_{i=0}^{k−1} D(z_{i+1}|z_i), where
D(z_{i+1}|z_i) = −log P_t(z_{i+1}|z_i,c,H_t). Hence inserting a learned abstract bridge z
yields a strictly cheaper route to a remote donor whenever
−log P_t(z|x,c,H_t) + −log P_t(y|z,c,H_t) < −log P_t(y|x,c,H_t). This is an operational
theorem about retrieval probability, not a claim that human neural distance is literal
metric geometry.
</statement>

### Definition

Retrieval kernel: P_t(y|x,c,H_t) ∈ [0,1] is the probability, at step t, that y is produced
as the next retrieved object given current object x, context c, and retrieved history H_t.
Surprisal distance D := −log P (natural log; base only rescales units). A retrieval path
x = z_0 → … → z_k = y is Markov when its probability factorizes as

  P_t(path) = Π_{i=0}^{k−1} P_t(z_{i+1} | z_i, c, H_t).

### Proof (additivity)

By the Markov factorization and strict monotonicity of −log on (0,1]:

  D(path) = −log P_t(path) = −log Π_i P_t(z_{i+1}|z_i,c,H_t)
          = Σ_i [ −log P_t(z_{i+1}|z_i,c,H_t) ] = Σ_i D(z_{i+1}|z_i).

The middle equality is the logarithm-of-a-product identity applied termwise; each term is
finite and nonnegative because each transition probability lies in (0,1]. ∎

Bridge corollary. Let the direct route x → y have surprisal D_dir = −log P_t(y|x,c,H_t)
and the bridged route x → z → y have surprisal D_br = −log P_t(z|x,c,H_t) +
−log P_t(y|z,c,H_t). Then P_t(bridged path) > P_t(direct hop) iff D_br < D_dir, by
monotonicity of −log. So a learned abstract bridge z that is (i) strongly associated with
x's context (P_t(z|x) high) and (ii) a strong cue for the remote donor y (P_t(y|z) high)
creates a shorter — higher-total-probability — route to y than the direct cue, whenever
the two bridge transitions are jointly more probable than the direct one. Multi-hop
chains and learned hierarchies iterate the same identity: total surprisal is the sum of
edge surprisals along the realized path, so improving any edge, or replacing a
low-probability edge by a chain of higher-probability edges, lowers the cost of reaching
the remote donor under the kernel.

### Scope note (mandatory)

The theorem is operational: it constrains retrieval probability under a stated kernel. It
makes no claim that biological memory implements a metric space, that "distance" in
neural tissue is Euclidean (or any fixed geometry), or that surprisal equals a physical
quantity. Any geometric phrasing elsewhere in the programme is shorthand for the
probabilistic content above. The falsifiable content lives in the kernel: a claimed
bridge is testable by whether measured retrieval of y from x rises once z is learned.

### Residual

Additivity is exact only under Markov factorization; kernels with long-range history
dependence (H_t entering transition probabilities beyond the current object) make edge
costs history-dependent — the identity then holds per realized history but edge costs are
not reusable constants. Registering measured edge surprisals under held-out histories is
the follow-up measurement.
<!-- end HSG-T56 -->
---

## HSG-T57 — Pandora donor search (parent reconstruction)

proof_class: P3_PARENT_RECONSTRUCTION | status: PARENT_RECONSTRUCTED | hostile: none

<statement id="HSG-T57">
Pandora donor search (parent: Weitzman 1979). Assume donor domains d = 1..n with
independent donor values X_d drawn from known prior distributions F_d, inspection cost
c_d > 0 per opened donor, utility = max observed X_d minus total inspection cost, donors
openable at will in any order, and unobserved donors freely left unopened. The parent
optimal policy is the reservation rule: compute reservation values z_d solving
E[(X_d − z_d)^+] = c_d; open donors in decreasing order of z_d; stop when the best
observed value exceeds the reservation value of every unopened donor; take the best
observed value. (PARENT_STATEMENT_UNVERIFIED_TEXT for the exact functional equation and
stopping clause as worded in the source.) OCM/HSG residual: real donors are correlated,
jointly useful, can alter the atom representation, and can create new candidate
disciplines — Pandora is an exact lower-level parent, not the final model.
</statement>

### Parent reconstruction — exact assumption list

Source: M. L. Weitzman, "Optimal Search for the Best Alternative", Econometrica 47(3),
1979, doi:10.2307/1910412 ("Pandora problem": n boxes, box d contains a prize X_d ~ F_d
known, opening costs c_d; open boxes sequentially or stop; payoff = best opened prize
minus total opening costs).

1. n alternatives (donor domains), indexed d, each openable at most once.
2. Prize/value X_d is drawn from a known distribution F_d, independently across d.
3. X_d is revealed exactly and costlessly upon opening; no partial information before.
4. Opening d costs c_d > 0, known, additive; c_d is incurred whether or not the prize is
   eventually used.
5. The searcher may stop at any time; payoff = max(0, max opened X_d) − Σ (opened c_d)
   (unopened boxes neither pay nor cost).
6. Risk neutrality (expected payoff maximization).
7. No recall cost: an opened prize remains available for selection at no further cost.

Reconstructed rule (reservation-value order-and-stop). PARENT_STATEMENT_UNVERIFIED_TEXT —
the source is paywalled; the following is the standard textbook form of Weitzman's
result, which I could not verify against the source text at freeze time:

- Reservation value z_d is the unique solution of c_d = E[(X_d − z_d)^+] =
  ∫_{z_d}^{∞} (1 − F_d(x)) dx (uniqueness by strict monotonicity of the right side in
  z_d). z_d is a fixed cutoff: it depends only on (F_d, c_d), not on other boxes or on
  observations.
- Order rule: open boxes in decreasing reservation value z_d.
- Stopping rule: after each opening, stop and take the best opened prize when it is at
  least the reservation value of every unopened box; otherwise open the unopened box with
  the highest z_d.
- This policy is optimal within the assumption list above (Weitzman's main theorem).

Why the cutoff form is forced (sanity argument, not a re-proof): facing a single box
(value X ~ F, cost c) against an outside option w in hand, opening is weakly optimal iff
E[max(X, w)] − c ≥ w ⇔ E[(X − w)^+] ≥ c; the boundary w = z where equality holds is
exactly the reservation equation. The multi-box optimality of the index order is the
parent's nontrivial content.

### Absorption into OCM/HSG (special case map)

Donor domain = box; inspection/reading of a domain = opening; donor value X_d = realized
usefulness of the extracted fragment; c_d = reading cost. Under assumptions 1–7 the
donor-search stopping problem IS the Pandora problem, so the reservation rule is the
exact optimal policy — this is the lower-level exact parent for "when to stop reading
candidate donors".

### Residual — where OCM/HSG leaves the parent (each residual is a dropped assumption)

- Independence (2) fails: donor values are correlated through shared deep structure;
  one useful donor raises the probability that structurally adjacent donors are useful.
  Correlated Pandora variants are not covered by the parent rule.
- Single-use scalar prize (1,5) fails: donors are jointly useful (complementarities, see
  the T58 hostile), so "max observed" is the wrong value functional — union value, not
  max, is the programme's object.
- Passive values (3) fail: reading a donor can alter the atom representation itself and
  can create new candidate disciplines (state-changing, non-Pandora observation).
- Known F_d (2) fails in cold start: priors over donor usefulness must be learned; the
  reservation values are then estimates with their own error, and the optimality claim
  degrades to "optimal under the frozen prior model".

Parents: [Weitzman 1979, doi:10.2307/1910412, assumptions_reconstructed: true].
<!-- end HSG-T57 -->
---

## HSG-T58 — Adaptive-submodular donor coverage (parent reconstruction + hostile)

proof_class: P3_PARENT_RECONSTRUCTION | status: PARENT_RECONSTRUCTED | hostile: logged

<statement id="HSG-T58">
Adaptive-submodular donor coverage (parents: Golovin–Krause 2011 adaptive submodularity;
Sviridenko 2004 monotone submodular knapsack). If the value of a set of discovered
fragments is adaptive monotone and adaptive submodular (the expected marginal value of any
donor does not increase as the observation state grows), then adaptive greedy achieves
the parent near-optimality guarantees within the registered constraint class: a near
1−1/e approximation for adaptive value maximization under a cardinality-style budget and
a logarithmic competitive ratio for adaptive minimum-cost cover; in the nonadaptive
special case with monotone submodular value under a single knapsack budget, greedy with
partial enumeration achieves 1−1/e exactly (Sviridenko). These guarantees are invalid for
complementary/synergistic donors, where the value of two donors together exceeds the sum
of their individual marginals; under complementarity the guarantee is invalid and joint
(set-level) search is required.
</statement>

### Parent reconstruction — exact assumption list

Sources: D. Golovin, A. Krause, "Adaptive Submodularity: Theory and Applications in Active
Learning and Stochastic Optimization", JAIR 42, 2011, doi:10.1613/JAIR.3278; M.
Sviridenko, "A note on maximizing a submodular set function subject to a knapsack
constraint", Operations Research Letters 32(1), 2004,
doi:10.1016/S0167-6377(03)00062-2. Neither source page was reachable at freeze time
(HTTP 404 both fetch attempts), so ALL parent-side constants below carry
PARENT_STATEMENT_UNVERIFIED_TEXT — reconstructed from standard presentations, not
verified against the sources.

Golovin–Krause setting: items (donors) with stochastic states observed on selection; a
utility f(ψ, A) of selecting item set A under realized observation state ψ; policy π
selects items adaptively.

1. Items are selected sequentially; selecting item reveals its realized state
   (inspection reveals the fragment's actual content).
2. Utility f(ψ, A) is normalized (f(∅) = 0), nonnegative, and nondecreasing in A for
   every ψ (adaptive monotonicity).
3. Adaptive submodularity: for observation states ψ ⊆ ψ′ (ψ′ more informed) and every
   item a, the expected marginal utility Δ(a | ψ) does not increase: Δ(a|ψ′) ≤ Δ(a|ψ).
4. Constraint class for the budgeted guarantee: cardinality-style budget on the number of
   selections (and, for the cost-cover guarantee, item costs with a pointwise bound on
   the probability p_* that a policy attains full value — the competitive ratio involves
   log(1/p_*)).
5. Under 1–4: adaptive greedy (repeatedly pick the item of maximal expected marginal
   utility per unit budget, conditioned on the current observation state) achieves the
   parent near-optimality: a 1−1/e-style approximation for budgeted adaptive
   maximization, and an O(log(1/p_*))-competitive ratio for adaptive minimum-cost cover.
   PARENT_STATEMENT_UNVERIFIED_TEXT (exact theorem numbers and the exact bound forms).
6. Nonadaptive special case (no state revelation; f a set function): monotone +
   submodular (diminishing marginals) under a single knapsack constraint ⇒ Sviridenko's
   greedy with partial enumeration over pairs attains at least 1−1/e of the optimum.
   PARENT_STATEMENT_UNVERIFIED_TEXT (the partial-enumeration construction as worded in
   the source).

Absorption: donors = items, fragment value = adaptive utility, reading = state
revelation. Under assumptions 1–4 the programme's greedy donor-selection inherits the
parent guarantees; this is the exact parent for "read donors greedily by expected
marginal fragment value".

### REQUIRED HOSTILE — complementary donor pair (smallest concrete instance)

Instance. Donor universe {A, B}, one target atom (a lemma). Extracting the lemma's proof
needs BOTH a technique (available only in donor A) and an invariant (available only in
donor B). Realized fragment value: f({A}) = 0 (technique alone proves nothing here),
f({B}) = 0 (invariant alone proves nothing), f({A,B}) = 1 (technique + invariant close
the lemma). Adaptive submodularity demands the expected marginal of B not increase with
more observation state: Δ(B | no reads) = 0 but Δ(B | A read) = 1. 0 → 1 is an
INCREASING marginal: submodularity fails (value of the pair, 1, exceeds the sum of
marginals from the empty state, 0 + 0).

Kills: the adaptive-submodular assumption (3) and, with it, the greedy near-optimality
guarantee in this configuration — greedy from the empty state sees two zero-marginal
donors, picks arbitrarily, and any stopping rule keyed to marginal gains can stop at
value 0; the parent's 1−1/e / log-competitive bounds are INVALID here. (It kills the
guarantee, not the parents: the parents never claimed coverage of complementary items.)

Verdict: LIFT_CONDITIONAL — the lift (greedy near-optimality) holds exactly over the
registered adaptive-submodular class; the hostile marks its boundary. Beyond it, joint
(set-level) search is required: evaluate pairs/sets, or search for a representation under
which the composite motif is itself an item (register the pair as a single derived donor,
which restores submodularity at the coarser granularity at the cost of a combinatorial
item space).

Parents: [Golovin–Krause 2011, doi:10.1613/JAIR.3278, assumptions_reconstructed: true;
Sviridenko 2004, doi:10.1016/S0167-6377(03)00062-2, assumptions_reconstructed: true].
<!-- end HSG-T58 -->
