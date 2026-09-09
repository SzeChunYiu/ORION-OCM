# HST Limits V1 — T12–T16 (lane C, D4)

Frozen statements: `HST_THEOREM_REGISTRY_V1.json` (not restated verbatim; each section
quotes the frozen content and proves it). Parent statements are given with their
**actual** hypotheses; citation details verified 2026-09-10. Every section ends with the
**non-assumptions**: structured conditions that leave the limit's regime. Claim ceilings
bind #221/#144 wording.

---

## T12 — Finite-state literal open-endedness limit [P5]

### Parent (exact)

**Pigeonhole principle.** If n+1 objects are placed in n boxes, some box contains >= 2 objects.

**Adams, Zenil, Davies & Walker 2017**, "Formal Definitions of Unbounded Evolution and
Innovation Reveal Universal Mechanisms for Open-Ended Evolution in Dynamical Systems",
*Scientific Reports* 7:997 (doi:10.1038/s41598-017-00810-8). Their formal definition:
a system exhibits **unbounded evolution** when it produces patterns that are
**non-repeating within the expected Poincare recurrence time of an equivalent isolated
system**. Note the parent's own escape hatch: the definition is already *relative to a
recurrence baseline* — consistent with, not contradicted by, T12.

**Dolson, Vostarin, Ofria (& Wiser) 2019**, "The MODES Toolbox: Measurements of
Open-ended Dynamics in Evolving Systems", *Artificial Life* 25(1):50-71. MODES is a
*measurement* toolbox (change, novelty, diversity, complexity) over finite observation
windows; it makes no infinite-time claim.

### Frozen assumptions

deterministic closed finite system; state space fixed.

### Theorem (T12) and proof

Let S be a finite set, |S| = n >= 1, and f : S -> S a total map (closed deterministic
system: no inputs, no randomness, no state outside S). For any sigma_0 in S define
sigma_{t+1} = f(sigma_t).

**Claim 1 (recurrence).** There exist 0 <= i < j <= n with sigma_i = sigma_j; the first
repeat occurs within the first n+1 states.

*Proof.* The n+1 states sigma_0, ..., sigma_n lie in S which has n elements; pigeonhole
gives sigma_i = sigma_j for some 0 <= i < j <= n. □

**Claim 2 (eventual periodicity).** With i < j the first such pair, determinism gives
sigma_{t+(j-i)} = sigma_t for all t >= i, so the trajectory is eventually periodic with
period p = j - i <= n. Total distinct states ever visited = i + p <= n; the novelty
count (number of distinct states) **saturates at step j <= n** and never increases again.

*Proof.* Induction: sigma_{i+1} = f(sigma_i) = f(sigma_j) = sigma_{j+1}, and iterating
the same identity shifts by any k >= 0. □

**Corollary (the frozen statement).** A closed deterministic finite-state system must
eventually repeat; literal infinite non-repeating state novelty is impossible for a fixed
finite closed state space. Open-endedness claims must be horizon-scoped, relative to
recurrence baselines, or accompanied by a growing effective state space.

### Scoped HST consequence

For #221 GS campaigns on a frozen morphology grammar, frozen evaluator, frozen hardware
and frozen archive format, the *system state* (lineage state + archive + PRNG stream) is
a fixed finite object, size <= 2^b for the campaign's bit budget b. Any claim of the form
"this run never repeats / novelty is unbounded" is **barred by T12**: the run either
terminates (finite novelty) or repeats within 2^b + 1 steps. The admissible #221 claim
vocabulary is window-scoped MODES-style metrics (novelty/diversity/change/complexity
rates within observation windows) with the recurrence baseline stated — exactly the
operational horizon-scoped OEE vocabulary this row registers.

### Non-assumptions (what escapes T12)

1. **Effective state growth.** If H_t, L_t, or the archive grows without a frozen bit
   bound (an *open* system in the T12 sense: state space not fixed), T12 does not apply
   to the growing system. Escape cost: the growing space is itself the OEE claim, and
   unbounded growth is exactly what T13 bars proving from finite evidence. T12+T13
   jointly leave no unexamined escape.
2. **Exogenous input streams (open-loop ecology).** If E_t injects fresh tasks, novelty
   can be driven by the *input tape*, not the system. The trajectory of the pair
   (state, input) recurs iff the input stream does; T12 then only says: measured
   "novelty" of a driven finite system is an environment property. #221 claims must
   state which side of the boundary the novelty metric reads.
3. **Stochastic transitions.** If sigma_{t+1} ~ P(.|sigma_t) on finite S, the *state
   sequence* need not repeat on any fixed clock; nevertheless the set of reachable
   states saturates into closed communicating classes, and every state-visit frequency
   converges (finite Markov chain theory). Randomness buys non-repetition of the
   *sequence*, not unbounded novelty of the *state set*: still <= n distinct states.
   This escape changes the metric, not the ceiling.
4. **Descriptor-space novelty.** MODES-style metrics computed on descriptors
   (phenotypes, behaviors) that are functions of state inherit the same bound
   (a function of <= 2^b states takes <= 2^b values). Only descriptors computed from
   *unbounded external artifacts* (growing logs, tapes) escape — which is escape 1
   relabelled.


---

## T13 — No finite trajectory proves unbounded future novelty [P5]

### Parent (exact)

**Prefix-extension argument** (classical compactness-flavored observation; here made
constructive — no external citation needed, the construction *is* the proof). Sharpened
by reduction to:

**Turing 1937** (Proc. LMS s2-42:230-265), undecidability of the halting problem: the
set K = {<M, x> : M halts on input x} is not decidable. Assumption: the program class is
all Turing machines (any Turing-complete formalism).

### Frozen assumptions

transition law not fully specified/proved.

### Formal setup

An **observed prefix** is a finite sequence rho = (rho_0, ..., rho_T) of distinct-or-not
state labels. A **transition system** (S, f, s0) extending rho is: a set S containing all
labels of rho, a total map f : S -> S, and s0 = rho_0 in S, whose trajectory satisfies
f(rho_t) = rho_{t+1} for all t < T. The prefix **determines** f on the labels
{rho_0..rho_{T-1}} and is silent on everything else. The prefix itself is *consistent*
iff it contains no contradictory determination: there is no pair i < j < T with
rho_i = rho_j but rho_{i+1} != rho_{j+1}. (A real observation containing such a pair
falsifies determinism outright — then neither continuation below exists, and the claim
"finite observation proves unbounded novelty" is dead for a different reason.)

### Theorem (T13), explicit constructions

Let rho = (rho_0, ..., rho_T) be a consistent observed prefix; m = |{rho_t}| its distinct
states.

**(i) Bounded-continuation system (explicit).** Take S_b := {rho_0, ..., rho_T} (m
states). Define f_b(rho_t) = rho_{t+1} for t < T, and f_b(rho_T) := rho_0 (or rho_T
itself). Consistency of rho makes the first T clauses well defined; the final clause is
free because rho_T has no determined image unless rho_T = rho_i for some i < T — and in
that case consistency already forces f_b(rho_T) = rho_{i+1}, so the trajectory from rho_0
is *already* periodic and we set nothing. In both cases (S_b, f_b, rho_0) is a closed
deterministic finite system consistent with rho whose total novelty is <= m <= T+1
forever: **bounded continuation**. Construction size: m states, T clauses.

**(ii) Continuing-novelty system — two cases.** The observed prefix is either a
**simple path** (all rho_t distinct) or **self-repeating** (rho_T = rho_i for some
i < T; the pair is consistent, so the loop closes).

- **Case A (simple path — the generic observation).** Take
  S_n := {rho_0, ..., rho_T} ∪ {nu_k : k ∈ N} (countably infinite), f_n := f_b on
  {rho_0..rho_{T-1}}, f_n(rho_T) := nu_1, f_n(nu_k) := nu_{k+1}. Deterministic,
  consistent with rho, computable (successor on the nu-chain); its trajectory visits a
  new state at every step t > T: **continuing-novelty continuation**. Construction
  size: m + aleph_0 states, T + 1 nontrivial clauses.
- **Case B (self-repeating prefix).** Then EVERY consistent deterministic extension —
  on ANY state space, however large — replays the observed cycle forever from rho_0:
  the constraints f(rho_i)=rho_{i+1}, ..., f(rho_{T-1})=rho_T=rho_i close a loop, and
  the orbit of rho_0 is trapped in it. A **novelty continuation does not exist at all**;
  the observation itself proves bounded novelty (under determinism). This *strengthens*
  the frozen statement's direction: a prefix that repeats does not merely fail to prove
  unbounded novelty — it refutes it.

**Expansion Lemma (same-universe boundary).** Even in Case A, a continuing-novelty
continuation *inside a fixed universe U* exists iff U contains a state unused by rho
(|{rho_t}| < |U|): the orbit must step to a state outside the prefix set at T+1.
When the prefix exhausts U, novelty requires *enlarging the universe itself* (the T12
escape), not just choosing a different law. Verified exhaustively at finite scope by
`exact/check_t13_v1.py`.

**Conclusion (claim ceiling).** For any finite observed prefix: (i) a
bounded-continuation system always exists (Case A construction S_b; Case B trivially,
since only bounded systems exist); (ii) a continuing-novelty system exists exactly when
the prefix is a simple path (Case A/S_n). Hence no function of a *non-repeating*
observed prefix — any statistic, any trend, any regression on novelty counts — can
entail "novelty continues forever": the same prefix is generated by a system that
saturates at step T+1 (S_b) and by one that never repeats (S_n); and a *repeating*
prefix refutes unbounded novelty outright. Either way, a positive #221 result may
support *scoped* novelty/complexity/evolvability trends over its observed window; it
cannot prove unbounded open-endedness. This is the #221/#144 claim ceiling.

### Sharpening: even the full law does not decide it

One might hope to escape T13 by *specifying* the transition law (the full program).
For arbitrary program classes this fails: define, from (M, x), the machine P that at
step k has simulated M(x) for k steps, carrying a monotonically increasing step counter
(configuration novelty while simulating), and upon M halting enters a 2-cycle. Then:
P's trajectory from its initial configuration visits infinitely many distinct
configurations **iff M(x) does not halt**. So "the future novelty of this fully
specified system is bounded" is at least as hard as the halting problem — undecidable
(Rice/Turing regime; cf. T15). Absent a *proof* of non-recurrence (not mere
specification), the ceiling stands; and for Turing-complete OCM hosts, such proofs are
not generally available. Marked `PARENT_STATEMENT_UNVERIFIED_TEXT` — none: the
reduction above is written out and self-contained; the halting problem's undecidability
is Turing 1937.

### Non-assumptions (what escapes T13)

1. **A proved non-recurrence premise.** If a system *carries a proof* that its effective
   state space grows (e.g., each step appends to an unbounded tape under a verified
   append-only discipline), boundedness of novelty is refuted by construction: T13 bars
   inference *from observation*, not inference from proved premises. The proof burden
   then sits with the premise (and T15 limits which premises are provable).
2. **Probabilistic discrimination (P3, not P5).** With a prior over transition systems,
   a long novelty streak can *raise the posterior* of continuing-novelty laws (Bayes).
   This is a P3 statement about the observer's distribution, never a proof of the
   system's future; the frozen claim ceiling is untouched.
3. **Bounded prediction horizons.** Claims of the form "novelty >= k more steps with
   confidence c" are legitimized by P3 machinery under explicit system distributions —
   horizon-scoped claims are outside what T13 bars (it bars only the unbounded claim).


---

## T14 — No universally best fixed search transformation [P5]

### Parents (exact)

**Wolpert & Macready 1997**, "No Free Lunch Theorems for Optimization", *IEEE Trans.
Evolutionary Computation* 1(1):67-82 (doi:10.1109/4235.585893). Their Theorem 1,
hypotheses stated exactly: X (search space) and Y (cost values) finite; algorithms are
non-revisiting-in-value-sequence procedures producing a length-m value sequence
d_m^y from f; P(d_m^y | f, m, A) the conditional probability of that sequence under
algorithm A on objective f. **Theorem 1**: for any two algorithms A1, A2,

  sum over ALL f : X -> Y of P(d_m^y | f, m, A1) = sum over ALL f : X -> Y of P(d_m^y | f, m, A2),

i.e. summed uniformly over the complete class of all objectives, performance histograms
are algorithm-independent. **Assumption structure**: the average is over the *entire*
function class (uniform weighting over all f), fixed per-run objective, finite X, Y.

**Schumacher, Vose & Whitley 2001** (GECCO 2001, "The No Free Lunch and Problem
Description Length"), the *sharpened NFL*: the NFL identity (equal performance sums over
F under uniform weighting) holds **iff F is closed under permutation (c.u.p.)** —
F = perm(F), i.e. for every permutation pi of X and f ∈ F, f∘pi ∈ F. So c.u.p. is
necessary AND sufficient: no smaller/nicer-than-all-functions uniform class is safe from
NFL, and every non-c.u.p. class admits algorithms that beat others on the uniform
average over it.

**Igel & Toussaint 2005**, "A No-Free-Lunch theorem for non-uniform distributions of
target functions", *J. Math. Modelling and Algorithms* 3(4):313-322
(doi:10.1007/s10852-005-3592-4), their Theorem 5: NFL holds under a (possibly
non-uniform) probability distribution over target functions **iff the distribution is
uniform within each permutation orbit** (f and f∘pi equally probable for every pi).
I.i.d.-random objectives are the canonical orbit-constant case — the "random landscape"
regime is exactly the NFL regime, in expectation.

### Frozen assumptions (exact NFL assumptions)

closed-under-permutation problem class; uniform distribution over problems. The frozen
row additionally *requires* the non-assumptions list — given below, it is the row's
operative content.

### Scoped HST consequence

Under NFL conditions, no search/transformation dominates. Therefore: no HST/OCM claim of
a *permanently superior* mutation/operator/translator/architecture may be stated as
universally best; the forbidden terminal `UNIVERSAL_BEST_SEARCH_ALGORITHM` is enforced
by parent theorem, not by taste. The defensible target is exactly the frozen row's:
conditional bias adaptation (fit Q_t to a registered structured ecology) + regime-change
/ harmful-transfer detection. Any registered-ecology comparison must state its task class
and distribution — because *some* averages over *some* classes DO rank algorithms (all
non-c.u.p., non-orbit-constant ones) — and the comparison claim is scoped to that
registration.

### Non-assumptions — registered-ecology conditions that LEAVE the NFL regime

This is the mandatory row content. Each escape is a condition OCM can *actually satisfy
by registration*, with the registration that carries it:

1. **Non-c.u.p. task class (structure).** Any class of objectives with locality —
   fitness correlated with edit distance / neighborhood structure on the genotype or
   program space (every real OCM morphology grammar with local variation operators) — is
   NOT closed under permutation: a random relabeling of genotypes destroys the
   neighborhood-fitness relation, so perm(F) ⊄ F. Simple certificate: a c.u.p. class
   containing a function with a unique minimum at x0 must contain, for every x ∈ X, a
   function with its unique minimum at x (permutations move x0 anywhere); any registered
   suite whose optima occupy a structured (e.g. reachable-by-gradient) subset violates
   this and is provably non-c.u.p. Registration: the #221 frozen benchmark suite (fixed
   task list, stated operators). On such classes algorithm ranking *is* meaningful.
2. **Non-orbit-constant task distribution (weighting).** OCM samples tasks from a frozen
   campaign mix with unequal weights. Unless that mix happens to weight permuted twins
   equally (it does not: tasks are named, weighted by campaign design), the
   Igel-Toussaint condition fails and NFL does not apply. Registration: the prospectively
   frozen task distribution of each campaign (#144 constitution).
3. **Nonstationary / coevolving objective.** NFL (both 1997 and sharpened forms) is
   stated for a *fixed* objective across the m evaluations. A #217-style ecology where
   E_t changes (curriculum, coevolution, adversarial task generation) is outside the
   parent's hypothesis; the parent theorems make no claim there. (W&M's own extension to
   time-dependent targets requires c.u.p.-type closure *at each time step under the same
   uniform weighting* — an even harder condition for a real ecology to meet.) Escape
   cost: an optimizing-against-moving-target claim needs its own (P4/P3) support; it is
   merely *not barred*, not won.
4. **Sequencing/resource accounting beyond the value sequence.** NFL compares algorithms
   by the histogram of observed cost-value sequences. B (the HST burden vector:
   generation + verification + storage + maintenance) is not a function of the value
   sequence alone; two algorithms with identical NFL-irrelevant value statistics can
   differ unboundedly in verification and memory burden. Burden-dominance claims live
   outside the NFL hypothesis — again not barred, but then they must be *measured*
   (#145/#151), not asserted.
5. **What does NOT escape (the limit side, kept loud).** (a) Any claim averaged over
   "all possible tasks/objectives" or over a c.u.p. closure of the registered suite;
   (b) "our operator mix beats X in general" without the registered distribution named;
   (c) i.i.d.-random-objective evals: expectation-NFL holds there, so random-landscape
   sweeps *cannot* show superiority — they are the null, not the arena. Registered
   comparisons must demonstrate non-c.u.p. structure (escape 1 certificate above) or
   they have proven nothing beyond NFL's flat average.


---

## T15 — No complete general semantic self-improvement verifier [P5]

### Parents (exact, hypotheses stated)

**Rice 1953**, "Classes of Recursively Enumerable Sets and Their Decision Problems",
*Trans. AMS* 74(2):358-366. **Theorem** (Rice's theorem): Let P be a property of
*partial computable functions* that is nontrivial — there is at least one partial
computable function with P and at least one without. Then { e : φ_e has P } is
undecidable. Hypothesis structure: (a) the objects are *extensional* properties of the
computed function (syntax is invisible: two programs computing the same function are
interchangeable); (b) P nontrivial; (c) program class = all partial computable functions.

**Turing 1937**, halting problem: K = { <M, x> : M halts on x } is undecidable (for
Turing-complete program classes). Note: "M halts on x" is a property of (M, x), not a
property of the computed function — Rice does not subsume it; the two are used side by
side.

**Godel 1931** (Monatshefte f. Math. u. Phys. 38:173-198), first incompleteness; Rosser
1936 strengthening. Precise hypotheses: T is **consistent** (Rosser removes Godel's
omega-consistency), **recursively axiomatizable**, and **sufficiently expressive**
(represents all computable functions / contains Robinson arithmetic Q). Conclusion: T is
incomplete — some sentence is undecidable in T. The stronger "true but unprovable"
reading needs T ⊆ true arithmetic (soundness, or at least Sigma_1-soundness). Second
incompleteness: T ⊬ Con(T) (same hypotheses, by Godel 1931/1934 Hilbert-Bernays-Lob
derivability conditions).

**Schmidhuber 2003-2006**, Godel Machines (arXiv:cs/0309048 "Godel Machines:
Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements";
later "Fully Self-Referential Optimal Problem Solvers"). The parent's own claim is
strictly conditional: IF (i) the objective is a frozen, formally encoded utility
functional with all costs charged, (ii) the initial machine's axioms are consistent and
sufficiently expressive, and (iii) the proof searcher *finds* a proof that a candidate
self-rewrite provably increases expected total utility — THEN executing that rewrite is
optimal among the self-changes whose proofs are found, relative to remaining runtime
and the given axioms. Hypothesis (iii) carries no feasibility guarantee: proof search
cost is unbounded and unprovable-but-beneficial rewrites may never be adopted (the
parent says so; incompleteness applies to the machine's own axiom system).

### Scoped HST consequence (limitations ledger)

Frozen statement consequence, decomposed by parent:

1. **Rice**: "is this arbitrary self-change useful/beneficial/capability-preserving" is a
   nontrivial property of the semantics of the changed program/evaluator — undecidable
   over arbitrary program classes. No OCM verifier can certify arbitrary self-changes.
2. **Turing**: even "does this self-change terminate / does the evaluator finish on this
   candidate" is undecidable over Turing-complete hosts.
3. **Godel/Rosser**: any consistent, recursively axiomatized, expressive internal theory
   C of the system leaves true-unprovable statements, including ones encoding beneficial
   self-changes; C cannot certify its own consistency.
4. **Godel Machine**: even the conditional global-optimality route requires finding the
   proof — which (1)-(3) do not supply in general.

Net: *universal complete proof that arbitrary self-change is beneficial is unavailable.*
This is a P5 limit on verifier claims, not on any particular bounded verifier.

### Non-assumptions (what escapes each limit)

1. **Bounded contracts escape Rice/Turing.** "Halts within k steps on input x",
   "output agrees with frozen spec S on the frozen finite test set T", "resource usage
   <= B" are *decidable* (simulate k steps; run T tests; meter). This is precisely the
   OCM design: C exposes **bounded decidable contracts** — syntactic or finite-behavior
   properties — where certification is exact, plus **CANNOT_CHECK** labels elsewhere.
   Rice bars only unbounded semantic properties of arbitrary programs.
2. **Restricted (non-Turing-complete) change languages escape Turing/Godel.** Total
   languages, finite-state or ranked/termination-guaranteed rewrite systems (every legal
   self-change carries a variant/ranking function) make halting decidable by
   construction. Escape cost: expressive power is capped — the language must actually be
   enforced (a "termination-checked" escape that inlines a Turing-complete evaluator
   re-enters the limit).
3. **Weak-but-complete theories escape Godel.** Decidable complete theories exist
   (Presburger arithmetic, real closed fields, propositional/propositional-modal
   contract logics). Godel's hypotheses fail for them: not "sufficiently expressive" in
   his sense. Contracts written in such fragments are fully verifiable — the cost is
   that they cannot quantify over their own programs/proofs, i.e. they verify the
   bounded contract, never "the change is beneficial in general".
4. **Empirical protected validation escapes nothing — it changes the claim class.**
   Running the changed system on held-out protected tasks (#149/#217 discipline) yields
   P4 evidence with confidence statements, not proof. The row's claim ceiling: P1 proof
   where the contract is bounded-decidable; P3/P4 evidence elsewhere; never a universal
   semantic verifier claim.


---

## T16 — No universal fastest solver/self-improver [P5]

### Parent (exact)

**Blum 1967**, "A Machine-Independent Theory of the Complexity of Recursive Functions",
*J. ACM* 14(2):322-336. First the measure axioms, verbatim in content: a **Blum
complexity measure** Φ = (Φ_0, Φ_1, ...) is a sequence of partial functions Φ_i : N -> N
satisfying

  (B1)  Φ_i(x) is defined  <=>  φ_i(x) is defined   (the measure is defined exactly
        where the computed partial function is);
  (B2)  the predicate "Φ_i(x) = y" is (total) decidable.

These two axioms are the *whole* hypothesis on the measure; time and space on any
reasonable machine model satisfy them (Blum's paper proves machine-independence).

**Speedup Theorem** (Blum 1967, same paper): for every **total recursive** function
r (arbitrarily fast-growing, r >= 2 say) there exists a **total recursive** function g
such that: for every program i computing g there is another program j computing g with

  Φ_j(x) <= Φ_i(x) / r(x)     for all but finitely many x.

Hence g has **no asymptotically optimal program**: every solver of g is dominated, on a
co-finite set, by a faster solver of g — for any preassigned recursive speedup factor.
(The theorem also holds with g a 0-1-valued predicate per standard presentations;
the contrived g is built by diagonalization/priority construction.)

### Scoped HST consequence, stated carefully

1. **What it bars**: any HST/OCM claim of convergence to a *final*, *globally fastest*
   cognition/solver/self-improver **over all computable problems**: for some computable
   problems such a final program provably does not exist under any admissible measure.
   "Final architecture" language is barred by parent theorem.
2. **What it supports (scoped)**: for problems in the speedup regime, there is *always*
   further search-transformation pressure — an unbounded chain of improvements — which
   is a structure HST can register as continued burden-reduction pressure, not a
   terminal state.
3. **Scope discipline (mandatory)**: Blum's g is a *contrived* diagonal function, not a
   natural task. The theorem is an existence limit on universal claims. It does NOT say
   OCM's registered tasks lack optimal solvers, and it does NOT predict empirical
   speedup chains in any real campaign. It only makes "we will reach the fastest
   version" unprovable as a universal promise.

### Non-assumptions (what escapes Blum)

1. **Fixed finite domains.** On a finite frozen task set with finite programs there are
   finitely many solvers; a minimizer exists by exhaustion (this is lane B's P2 finite
   microscope regime — Blum's asymptotics do not apply). Escape cost: the claim is then
   "fastest on this finite set at these sizes", nothing asymptotic.
2. **Problems with matching lower bounds.** Many natural problems possess complexity
   lower bounds (hierarchy theorems): for them "no fastest program" is *false* in the
   relevant sense — an optimal-order program exists and Blum speedup does not bite
   beyond constant factors. Blum's theorem does not transfer the speedup regime to them.
3. **Fixed resource floors / finite-precision reality.** The theorem is co-finite and
   asymptotic; on real hardware with overhead floors and bounded precision, "speedup"
   saturates. HST burden claims B are always price-vector, campaign-scoped quantities —
   outside the asymptotic regime, where the theorem is silent.

---

## Machine checks (this lane) and artifact map

- `exact/check_t12_v1.py` — pigeonhole at finite scope: all maps on n = 1..4 states,
  all initial states; verifies first revisit within |S|+1 steps, novelty saturation at
  first revisit, period <= |S|.
- `exact/check_t13_v1.py` — every consistent prefix on n = 3..4 states, all consistent
  transition systems enumerated: >= 1 bounded continuation always; >= 1
  novelty-continuation whenever the universe has a fresh state (and the Expansion-Lemma
  boundary: self-repeating prefixes force same-universe saturation); inconsistent
  prefixes identified as the determinism-falsifying set.
- `proofs/T17_TOY.md` + `exact/check_t17_v1.py` + `hostiles/T17_TAMPER_WITNESS.json` —
  the evaluator-tampering toy (separate file, T17).
- `hostiles/HOSTILES_LIMITS_V1.md` — the two §11 hostiles owned by this lane.

Runners execute on billy-laptop (`ssh billy-laptop`, python 3.8.10); certificates are
P2 witnesses only — no row becomes PROVED because a test passed (README hard rule).

## Sources consulted (2026-09-10)

- Wolpert & Macready 1997, IEEE TEC 1(1):67-82; no-free-lunch.org (WoMa96a.pdf).
- Schumacher, Vose & Whitley, GECCO 2001, "The No Free Lunch and Problem Description
  Length" (sharpened NFL: c.u.p. iff NFL).
- Igel & Toussaint 2005, JMMA 3(4):313-322 (non-uniform NFL iff orbit-constant
  distribution); survey: christian-igel.github.io/paper/NFLTLaPoM.pdf.
- Blum 1967, JACM 14(2):322-336 (Blum axioms B1/B2 + speedup theorem);
  en.wikipedia.org/wiki/Blum%27s_speedup_theorem,
  mathworld.wolfram.com/BlumsSpeed-UpTheorem.html.
- Rice 1953, Trans. AMS 74(2):358-366; Turing 1937, Proc. LMS s2-42:230-265;
  Godel 1931, Monatshefte 38:173-198; Rosser 1936, JSL 1(3):87-91.
- Schmidhuber, arXiv:cs/0309048 (Godel Machines, conditional optimality form).
- Adams, Zenil, Davies & Walker 2017, Sci. Rep. 7:997 (unbounded evolution defined
  against Poincare recurrence baseline).
- Dolson, Vostarin, Ofria (& Wiser) 2019, Artificial Life 25(1):50-71 (MODES toolbox).

No `PARENT_STATEMENT_UNVERIFIED_TEXT` markers were needed: every parent hypothesis above
was verified against the listed sources on 2026-09-10.




