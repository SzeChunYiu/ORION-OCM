# GMI Biosphere Species Equivalence Hardening v1

Status: **FORMAL CORRECTION / SUCCESSOR TO BIOSPHERE §4 SPECIES RELATION**

Status date: 2026-09-12.

Refs:

- `GMI_MACHINE_INTELLIGENCE_BIOSPHERE_V1.md`
- `GMI_RECURSIVE_THEORY_HARDENING_FIXED_POINT_V1.md`

This file records and corrects a logical weakness in the first biosphere species definition.

---

# 1. The problem

`GMI_MACHINE_INTELLIGENCE_BIOSPHERE_V1.md` introduced a tolerance/compiler-budget relation

\[
M_1\equiv_{E,J,\epsilon,c}M_2.
\]

That notation is too strong.

Two independent failures can break transitivity:

1. approximate closeness is not generally transitive:

\[
d(M_1,M_2)\le\epsilon,
\quad d(M_2,M_3)\le\epsilon
\not\Rightarrow
d(M_1,M_3)\le\epsilon;
\]

2. bounded compiler reductions need not compose within the same budget:

\[
C_{12}\le c,
\quad C_{23}\le c
\not\Rightarrow C_{13}\le c.
\]

Therefore tolerance plus bounded-reduction similarity must **not** be called a mathematical equivalence relation without extra assumptions.

This correction is additive; the original text remains part of the research record.

---

# 2. Exact registered developmental equivalence

Fix a registered ecology/intervention family `(E,J)`.

Let a machine's protected developmental response be

\[
\mathcal R_{E,J}(M),
\]

containing its legal semantic traces and state-transition responses under all registered interventions, modulo an allowed exact representation isomorphism.

Define

\[
M_1\sim_{E,J}M_2
\iff
\mathcal R_{E,J}(M_1)=\mathcal R_{E,J}(M_2).
\]

Required equality includes, at the registered scope:

```text
same legal observable semantic behavior
same response to registered development/update interventions
same history/lineage semantics when those are part of E
same verifier/admission semantics when part of E
same morphology-transition semantics when Gamma is under test
```

Pure physical implementation burden is **not** required to be equal for semantic/developmental equivalence; it is recorded separately in `rho_M`.

Under ordinary equality and exact representation isomorphism, `~_{E,J}` is reflexive, symmetric and transitive.

A strict finite-scope **developmental species** is an equivalence class

\[
[M]_{E,J}.
\]

---

# 3. Semantic species vs resource phenotype

Two exact developmental equivalents may have different physical costs.

Therefore distinguish:

```text
semantic/developmental species  [M]_{E,J}
resource phenotype               rho_M(e)
implementation encoding          code/graph/storage/layout
```

Example:

```text
standard dense attention
FlashAttention-style exact attention
```

may be the same registered cognitive/developmental species while having different resource phenotypes on a GPU substrate.

If numeric approximation changes protected behavior, the systems may no longer be exactly equivalent.

---

# 4. Mechanism phenotype

For scientific mechanism classification define an architecture-neutral witness vector

\[
a(M,e)=(a_1,\ldots,a_K).
\]

Machines can be exact developmental equivalents yet implement the behavior through different hidden mechanisms that are not distinguished by the registered intervention set.

If distinguishing those mechanisms matters, enlarge `J` with interventions capable of separating them.

Thus species resolution is explicitly intervention-relative.

---

# 5. Approximate empirical regime: do not use equivalence language

In noisy/continuous real systems exact equality is often unavailable.

Define a registered phenotype distance or discrepancy vector

\[
d_{E,J}(M_1,M_2)
=
(d_{sem},d_{resp},d_{mech},d_{resource},\ldots).
\]

Then define an **epsilon-neighborhood**

\[
\mathcal N_\epsilon(M)
=
\{M':d(M,M')\preceq\epsilon\}.
\]

Do not call this an equivalence class unless transitivity is separately proved.

For practical archive compression one may use clustering, but cluster identity is an analysis convention, not a theorem.

Required robustness checks:

```text
multiple epsilon values
multiple distance weightings / vector thresholds
multiple clustering algorithms where applicable
bootstrap uncertainty
leave-one-ecology-out stability
semantic remint stability
```

---

# 6. Why connected-component closure is dangerous

One tempting repair is to connect all epsilon-neighbors and call connected components species.

Reject this as the default because chaining can collapse distant machines:

\[
M_1\approx M_2\approx\cdots\approx M_n
\]

while `M_1` and `M_n` are scientifically very different.

If graph components are ever used, report component diameter and do not interpret them as exact species.

---

# 7. Compiler/reduction cost is a separate relation

Define directed reduction burden

\[
C(M_1\Rightarrow M_2)
\]

as a **vector** containing, for a frozen reduction protocol:

```text
description/code added
search/tuning
new state
training/development
serve overhead
memory
communication
verification
approximation loss
```

Do not bake a fixed bound `c` into species equivalence.

A parent reduction question becomes:

> how expensive is it for a known parent species to reproduce the candidate phenotype at the registered adequacy level?

This is a novelty/frontier question, not identity.

---

# 8. Symmetric reduction is not identity

Even if

\[
C(M_1\Rightarrow M_2)
\]

and

\[
C(M_2\Rightarrow M_1)
\]

are both small, the systems need not be exact developmental equivalents; the compilers may add side state or change lifecycle behavior.

Therefore reduction tests must explicitly check semantic/developmental preservation.

---

# 9. Species split theorem at registered scope

If there exists a registered ecology `e` and legal intervention `j` such that

\[
\mathcal R(M_1;e,j)\ne\mathcal R(M_2;e,j),
\]

then

\[
M_1\not\sim_{E,J}M_2.
\]

This trivial-looking statement is operationally important: a single protected developmental counterexample is sufficient to split an exact species class at that scope.

Examples include differences in:

```text
rollback after rejected update
as-of historical query
future adaptation after identical present output
response to substrate repricing when morphology adaptation is part of the registered behavior
```

---

# 10. Species merge criterion

A merge is justified only when the registered response objects are equal/indistinguishable under the accepted statistical criterion **across the complete registered intervention set**.

Lack of a separating test is not proof of equality in an open world.

Therefore empirical merge status should be labeled:

```text
UNSEPARATED_AT_CURRENT_TEST_POWER
```

rather than

```text
PROVED_SAME_SPECIES
```

unless exact finite enumeration/proof is available.

---

# 11. Species count is scope-dependent

Let

\[
S(E,J)
=|\mathcal M/\sim_{E,J}|.
\]

Adding ecologies or interventions can only preserve or refine exact equivalence classes; it cannot legitimately merge machines that were previously distinguished by retained tests.

Thus reported species counts must always cite:

```text
E ecology registry version
J intervention registry version
semantic equality/tolerance regime
archive/sample universe
```

There is no context-free count of all possible machine-intelligence species.

---

# 12. Novel-form admission after correction

A candidate supports strong novelty only if:

1. it is separated from registered known parents by protected developmental interventions or frontier behavior;
2. the distinction survives semantic/implementation remints;
3. approximate clustering conclusions are robust to thresholds;
4. parent reduction requires material charged burden or loses protected behavior;
5. independent search encodings recover the same property complex;
6. real-regime transfer survives where required.

This is stronger than the original tolerance-equivalence wording.

---

# 13. Corrected terminology

Use:

```text
exact developmental species       for ~_{E,J} equivalence classes at exact scope
empirical phenotype neighborhood  for approximate epsilon proximity
provisional phenotype cluster     for noisy archive compression
parent-reduction burden           for compilation/reproduction cost
novelty tier                       for evidence of distinction from known parents
```

Do not collapse these concepts.

---

# 14. Claim boundary

This correction narrows the biosphere claim but makes it mathematically cleaner.

The phrase “millions of species” may be used only after a registered exact or robust empirical classification establishes species/cluster counts at a declared scope. Until then use “millions of raw morphology candidates/configurations.”
