# Grand GMI Compositional Language Morphology Theorem V1

Status: **THEOREM + EXACT PHASE/RECOMBINATION WITNESSES**  
Date: 2026-09-12

## 0. Language is a semantic-cut morphology

Grand GMI does not take `language`, `word`, `symbolic system` or `compositionality` as a primitive. A communication system is a physical protocol crossing a semantic cut between process components. Its morphology should therefore be derived from:

1. the factorization of obligation-relevant meaning;
2. the exact distinctions that must cross the cut;
3. the resource cost of storing/learning lexical associations;
4. the resource cost of transmitting and processing message positions.

This document derives a finite exact morphology law for a product semantic space.

---

## 1. Product meaning space

Let the exact obligation-relevant meaning be

\[
m=(m_1,\ldots,m_k)\in M_1\times\cdots\times M_k,
\qquad |M_i|=n_i\ge2.
\]

The total number of exact meanings is

\[
N=\prod_{i=1}^k n_i.
\]

A **semantic-role partition** `pi` partitions the role indices `{1,...,k}` into blocks `B`. A block-separable code sends one token for every block. The token emitted for block `B` depends only on the submeaning `m_B`.

This family contains:

- **holistic language**: one block containing all roles;
- **fully compositional language**: `k` singleton blocks;
- **partially compositional/chunked language**: intermediate partitions.

The code class is architecture-neutral: tokens can be implemented by neural activations, discrete strings, gestures, packets or other physical carriers.

---

## 2. Exact lexical-entry theorem

For a block `B`, there are

\[
N_B=\prod_{i\in B}n_i
\]

possible exact block meanings.

If two distinct block meanings receive the same token, choose equal values for every role outside `B`. The two resulting global meanings then produce the same complete block-token sequence but require different exact semantic outputs. Hence exact zero-error communication is impossible.

Therefore every block encoder must be injective.

**CLM-1 — Block Lexicon Theorem.** For a semantic-role partition `pi`, the minimum number of role/block-specific lexical associations required by an exact block-separable code is

\[
\boxed{
A(\pi)=\sum_{B\in\pi}\prod_{i\in B}n_i.
}
\]

The minimum transmitted message length in this code class is

\[
\boxed{L(\pi)=|\pi|.}
\]

Both bounds are attained by assigning one distinct token to each possible block meaning and concatenating one token per block.

Special cases:

\[
A_{hol}=\prod_i n_i,\quad L_{hol}=1,
\]

\[
A_{comp}=\sum_i n_i,\quad L_{comp}=k.
\]

The counted lexical resource is the number of semantic role/block-to-token associations. Surface glyph reuse across positions does not make two role-specific semantic associations free.

---

## 3. Resource-conditioned language phase law

Let

- `lambda > 0` be the counted resource price per lexical association;
- `c > 0` be the counted resource price per transmitted token position.

For partition `pi`, define

\[
\boxed{C_\pi=\lambda A(\pi)+cL(\pi).}
\]

**CLM-2 — Language Partition Morphology Theorem.** Within the declared block-separable exact code class, the resource-optimal language morphology is precisely the partition set

\[
\boxed{
\Pi^*=\arg\min_{\pi} \left[\lambda A(\pi)+c|\pi|\right].
}
\]

Thus compositionality is not universally optimal. It is a resource-conditioned morphology selected by the relative cost of lexical storage/acquisition versus transmission.

For the two extreme forms,

\[
C_{comp}<C_{hol}
\iff
\boxed{
\lambda\left(\prod_i n_i-\sum_i n_i\right)>c(k-1).
}
\]

When the product-minus-sum term is nonpositive, the fully compositional extreme cannot beat the holistic extreme under this scalar resource model. Intermediate partitions can nevertheless define separate phases.

---

## 4. Monotone chunking theorem

Write `r=c/lambda`. Each partition has affine normalized cost

\[
\tilde C_\pi(r)=A(\pi)+r|\pi|.
\]

Let `r_2>r_1`, and let `pi_1` and `pi_2` be any optimal partitions at those respective ratios. Optimality gives

\[
A_1+r_1L_1\le A_2+r_1L_2,
\]

\[
A_2+r_2L_2\le A_1+r_2L_1.
\]

Adding yields

\[
(r_2-r_1)(L_2-L_1)\le0,
\]

so

\[
\boxed{L_2\le L_1.}
\]

**CLM-3 — Monotone Chunking Theorem.** As transmission cost rises relative to lexical-association cost, an optimal block-separable language cannot require *more* compositional blocks. Optimal morphology moves monotonically toward larger chunks/holism, possibly through ties. Conversely, increasing lexical-association pressure relative to transmission pressure favors finer composition.

The phase boundaries are the finitely many intersections

\[
r_{\pi,\pi'}=
\frac{A(\pi')-A(\pi)}{|\pi|-|\pi'|}
\]

for pairs with unequal block counts and physically relevant positive ratio.

This gives a direct GMI morphology phase diagram from semantic factor sizes and resource prices.

---

## 5. Exact three-phase witness

Take three independent semantic roles, each with three values:

\[
(n_1,n_2,n_3)=(3,3,3).
\]

Representative profiles are:

| morphology | lexical associations `A` | tokens `L` |
|---|---:|---:|
| holistic `{123}` | 27 | 1 |
| partial `{12}{3}` | 12 | 2 |
| fully compositional `{1}{2}{3}` | 9 | 3 |

With `lambda=1`:

- `c=1`: fully compositional cost `12` is uniquely optimal by block count;
- `c=5`: a two-block morphology costs `22` and is optimal;
- `c=20`: holistic cost `47` is optimal.

So the theory predicts a genuine sequence

\[
\boxed{
\text{fine composition}\to\text{partial chunking}\to\text{holism}
}
\]

under a single changing resource ratio, without changing the semantic obligation.

---

## 6. Productive recombination theorem

Consider learning a block-separable lookup lexicon from observed complete meanings. Suppose the training set contains, for every block `B`, every block value that will later be required. Then exact global messages are generated by concatenating the learned block tokens; the exact global tuple itself need not have occurred in training.

**CLM-4 — Productive Recombination Theorem.** Once all block-level lexical entries of a partition are available, the code generates the Cartesian product of those block meanings exactly. Generalization to an unseen global combination therefore follows from factorized code structure, not from a new token for the full combination.

### Leave-one-out corollary

Let the full meaning universe be a Cartesian product with every factor size at least two, and train on all global meanings except one held-out tuple.

For any partition with at least two blocks, every held-out block value still occurs in a training meaning: vary a role belonging to another block. Hence every nonholistic block-separable lookup code can reconstruct the held-out global combination from already observed block entries.

A purely holistic empirical lookup has no entry for the held-out full tuple.

This is a theorem about the declared lookup/code classes, **not** a claim that every noncompositional learner lacks other generalization mechanisms.

---

## 7. Why compositionality is not synonymous with generalization

The theorem predicts a resource/recombination advantage under explicit factorization and code-class assumptions. It does not assert

`MORE_COMPOSITIONAL => BETTER_GENERALIZATION`

for arbitrary learners or ecologies.

A noncompositional machine may generalize through geometry, smoothness, learned latent structure, retrieval or other transformations. Conversely a formally compositional code may be hard to learn or physically expensive.

This boundary is important because emergent-language studies report that compositionality and generalization need not correlate universally, while other experiments find learnability/systematic-generalization advantages under structured compositional languages. Grand GMI explains why both outcomes are possible: the verdict depends on the semantic factorization, developmental process and resource vector rather than on a universal architectural virtue.

---

## 8. Relation to the Grand-GMI master objects

Language now has a quantitative reduction:

\[
\boxed{
\text{semantic product structure}
\to
\text{internal/distributed cut}
\to
\text{partition code family}
\to
(A(\pi),L(\pi))
\to
\text{resource phase}\ \Pi^*.
}
\]

The theorem instantiates:

- semantic state/factorization: defines the role product;
- `kappa`: exact messages must preserve obligation-distinct combinations;
- `rho`: prices lexical associations and transmission;
- morphology selection: chooses the nondominated/optimal code partition;
- recursive development: determines whether the corresponding lexicon/code can actually be learned/reached.

No symbol system is privileged in the primitive theory.

---

## 9. Exhaustive exact microscope

`grand_gmi_compositional_language_checks_v1.py` performs exact integer checks with no RNG.

Phase geometry:

- **336** semantic factor configurations (`k=2..4`, each factor size `2..5`);
- **4,192** partition-profile evaluations;
- **43,008** exact scalar resource-phase cells (`lambda=1..8`, `c=1..16`);
- **2,688/2,688** resource sweeps obey monotone chunking.

Recombination:

- **117** factor configurations (`k=2..4`, sizes `2..4`);
- **94,851/94,851** nonholistic partition/held-out cases recover every held-out block from the remaining Cartesian-product training set;
- **7,371/7,371** holistic leave-one-out full-tuple entries are absent.

The ternary three-role witness recovers optimal block counts `3 -> 2 -> 1` at transmission prices `1 -> 5 -> 20` for unit lexical cost.

Aggregate terminal:

`GRAND_GMI_COMPOSITIONAL_LANGUAGE_TRANCHE_ALL_GREEN`.

---

## 10. Parent subtraction

Linguistics, coding theory and emergent-communication research own the ideas that compositional systems reuse parts, support systematic recombination, and trade vocabulary/protocol structure against other costs. Recent work also treats compositionality as a continuum rather than a binary property.

Grand GMI does not relabel those observations as inventions. The residual contribution here is the typed resource theorem connecting an obligation-derived semantic product and its **entire partition lattice** directly to morphology selection:

\[
C_\pi=\lambda\sum_{B\in\pi}\prod_{i\in B}n_i+c|\pi|,
\]

including the monotone chunking law and explicit intermediate phase boundaries.

---

## 11. Scope and falsifiers

The theorem assumes an exact finite product semantic space and a block-separable lookup code class whose lexical associations and token positions are counted as declared resources.

It does not claim natural language is literally a Cartesian product, that human lexical cost equals a constant `lambda`, or that a trained neural system is restricted to lookup coding.

Finite-scope falsifiers are direct:

1. an exact block-separable code using fewer than `A(pi)` role/block associations;
2. an exact code in the declared class transmitting fewer than `|pi|` block tokens without changing the boundary/side information;
3. a resource ratio increase whose optimal partition has strictly more blocks;
4. a leave-one-out Cartesian-product case where a nonholistic partition lacks a held-out block value despite every factor size being at least two;
5. a mismatch in the frozen exact receipt.