# Population-hereditary carrier, reduction, and information theorem v1

## Carrier and native laws

For a finite genotype set \(G\), a population-hereditary carrier is

\[
P=(n_g,w_g,M(g,g'),\ell)_{g,g'\in G},
\]

where \(n_g\) is genotype multiplicity, \(w_g>0\) fitness, \(M\) a mutation
kernel, and \(\ell\) lineage/custody state. Native operators are
fitness-proportional selection, reproduction/inheritance, mutation, and
birth/death replacement. Population size, genotype and lineage bits, fitness
evaluations, failed offspring, generations, and communication are separately
charged. The machine-readable schema is `POPULATION_CARRIER_SCHEMA_V1.json`.

## Theorem PH-1 — exact D7+D8 reduction

Index every multiset occurrence as one D7 component carrying its genotype and
lineage. Selection is a collective operator over component fitness; reproduction
is component creation; mutation and birth/death are D8 component replacement;
lineage is an ordinary relation over component identifiers. This compiler is
invertible up to permutation of equal multiset members and preserves every
population transition and response exactly.

The state overhead is a component identifier per occurrence and the operator
overhead is polynomial in population size under ordinary enumeration. Therefore
finite population-hereditary cognition reduces to D7 collective state composed
with D8 replacement (and, when candidate discovery is counted separately, D5
search). It is not a new domain at this matched scope.

## Theorem PH-2 — exact selection and heredity information laws

Let \(p_g=n_g/\sum_h n_h\), \(\bar w=\sum_g p_gw_g\), and selection-only
offspring frequency

\[
q_g=\frac{p_gw_g}{\bar w}.
\]

For any numeric trait \(z_g\),

\[
\mathbb E_q[z]-\mathbb E_p[z]
=\frac{\operatorname{Cov}_p(z,w)}{\bar w}.
\]

**Proof.** Substitute \(q_g\):
\(\sum_g p_gw_gz_g/\bar w-\bar z
=(\mathbb E_p[zw]-\bar z\bar w)/\bar w\). ∎

Selection's information displacement is exactly

\[
D_{KL}(q\Vert p)
=\sum_{g:q_g>0}q_g\log_2\frac{q_g}{p_g}
=\sum_{g:q_g>0}q_g\log_2\frac{w_g}{\bar w}.
\]

For a uniform binary parent copied through symmetric mutation probability
\(\mu\), heredity retains

\[
I(parent;offspring)=1-h_2(\mu)
\]

bits: 1 bit at \(\mu=0\), 0 at \(\mu=1/2\). These laws separate selection
information from mutation-channel retention. The executable certificate checks
the Price identity with rational arithmetic in all 2,187 two-genotype
populations through size six, fitness values 1–3, and trait values 0–2.

## Theorem PH-3 — option-value regime

Freeze two equiprobable ecologies \(A,B\) and genotypes specialized one-to-one.
Population support is fixed before ecology reveal; selection is allowed after
reveal; post-reveal mutation/creation is forbidden.

The diverse population \(\{A,B\}\) serves the matching member and has
capability 1. Every support-one carrier is constant across the reveal and succeeds
in exactly one ecology, so its capability is \(1/2\). Homogeneous populations
are matched negative twins and also score \(1/2\). Therefore support size two
is necessary and sufficient for full capability in this timing/resource regime.

This is the predicted regime in which population state is irreducible to one
lineage: future niche uncertainty, pre-reveal diversity, post-reveal selection,
and no post-reveal creation. The D7+D8 compiler reproduces all three possible
size-two multisets exactly, so the result remains parent-absorbed rather than a
domain claim.

## Claim ceiling

Finite multiset populations, finite genotypes, and matched operators only.
Unbounded open-ended heredity and physical population substrates remain open.
