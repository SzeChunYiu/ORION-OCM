# GMI Domain-Equivalence Complexity Hardening v1

Status: **FOUNDATIONAL CORRECTION / CLAIM-BOUNDARY HARDENING**

Status date: 2026-09-12.

Purpose:

> Prevent a universal symbolic/program simulator from trivially collapsing every classical realization into one domain, while also preventing arbitrary implementation differences from being mislabeled as new domains.

---

# 1. The universality loophole

If D4 `symbolic/program` is allowed to mean an unconstrained universal machine, then every ordinary computable classical realization has a D4 simulation. Under mere computability equivalence, neural, memory, search, dynamical, cellular, event, sheaf and constructive machines all collapse.

Therefore **domain identity is meaningless without an accepted simulation-overhead class**.

---

# 2. Registered efficient reduction

For realization families `A,B`, obligation family `O_n`, and resource vector `rho`, define a semantics-preserving compiler

\[
C_{A\to B,n}:A_n\to B_n.
\]

Let the coordinatewise overhead functions be

\[
h^{(j)}_{A\to B}(n)
=
\sup_{M\in A_n}
\frac{1+\rho_j(C(M))}{1+\rho_j(M)}.
\]

Resources may include:

```text
state description
precision
training/development
query time
update time
memory
communication
search
verification
energy
morphogenesis cost
```

For a registered class `H` of admissible overhead functions, write

\[
A\preceq_H B
\]

when every registered resource overhead lies in `H` and semantics are preserved.

Define efficient bi-reducibility

\[
A\equiv_H B
\iff
A\preceq_H B\;\land\;B\preceq_H A.
\]

---

# 3. Composition requirement

`H` must be closed under composition (or the closure explicitly taken), otherwise `equiv_H` may fail transitivity.

Useful registered levels include:

```text
H0 exact/isometric          overhead 1 or registered constant
H1 constant-factor          O(1)
H2 quasilinear              n polylog n relative transform where appropriate
H3 polynomial               poly(n)
H4 computability-only       any finite computable overhead
```

Different levels induce different taxonomies.

This is analogous to biology being classified at several resolutions: a `domain` at H1 may collapse into one broader super-domain at H3.

---

# 4. Domain hierarchy rather than one flat partition

Define

\[
\mathfrak D_H=\mathcal M/\equiv_H.
\]

As the accepted overhead class widens,

\[
\mathfrak D_{H0}\to\mathfrak D_{H1}\to\mathfrak D_{H2}\to\mathfrak D_{H3}\to\mathfrak D_{H4}
\]

can merge previously distinct classes.

Therefore terms should be used with an explicit resolution:

```text
structural kingdom      distinct at tight H0/H1 realization cost
resource domain         distinct at registered lifecycle H1/H2 costs
complexity domain       distinct even under H3 polynomial simulation
computability domain    distinct under H4 computability itself
```

At H4, ordinary classical realizations are expected to collapse heavily.

---

# 5. Consequence for the current D1-D8 taxonomy

The present D1-D8 list should be interpreted as **candidate resource/structural domains**, not yet as pairwise complexity domains.

In particular:

```text
D4 symbolic/program is a universal parent at loose resolution;
D1 neural/coefficient families may approximate/simulate broad classical maps;
D6 dynamical systems can encode computation;
D8 self-rewriting programs can encode many developmental carriers.
```

Thus pairwise domain novelty requires a burden-separation theorem at a declared `H`.

Without that declaration, `NEW_DOMAIN` is forbidden.

---

# 6. Strong-domain theorem target

For candidate `N` and parent union `P`, a complexity-domain separation at overhead class `H` requires proving

\[
N\not\preceq_H P
\]

on a registered obligation family.

A sufficient asymptotic route is to prove one burden coordinate satisfies

\[
r_P(n)=\Omega(f(n)),\qquad r_N(n)=O(g(n))
\]

with `f/g` outside the accepted overhead class.

Examples:

```text
exponential vs polynomial
polynomial-degree separation when H is lower-degree
linear vs exponential update burden
constant communication vs growing communication
bounded local repair vs global rewrite
```

The parent class must be strong enough to prevent syntactic strawman proofs.

---

# 7. Conditional separations

Some domain separations may rely on unresolved complexity assumptions.

Example pattern:

```text
If complexity assumption A holds,
then candidate domain N is not polynomially reducible to classical parent P
for obligation family F.
```

Such results must be labeled `CONDITIONAL_DOMAIN_SEPARATION`, not theorem-level unconditional novelty.

Quantum/classical complexity is an important calibration example: many believed separations are conditional on standard complexity assumptions or oracle models rather than unconditional real-world superiority.

---

# 8. Finite-range material separation

Scientific domain evidence need not wait for asymptotics if the practical scope is finite.

For registered `n in [n_min,n_max]`, define material separation if every strongest-parent reduction exceeds frozen burden threshold `tau` while the candidate remains admissible.

This supports:

```text
RESOURCE_DOMAIN_AT_REGISTERED_SCOPE
```

but not universal complexity-domain language.

---

# 9. Reclassification rule for current novel hypotheses

Following the exact theorem pass:

```text
N10 event/partial-order:
    strong compactness vs naive interleavings,
    but bounded symbolic event-structure/Petri-net reduction exists;
    -> kingdom/phylum candidate unless stronger H-separation found.

N11 invariant/obstruction:
    exact quotient optimality,
    but generic semantic quotient representation already captures it;
    -> mechanism/kingdom, not domain at current scope.

N3 sheaf/local-global:
    exact obstruction theorem,
    but simple registered family compiles to symbolic parity/CSP in O(n);
    -> W2 domain status open.

N8 constructive closure:
    exact developmental-state lower bound,
    but D8 can encode constructor state;
    -> W2 requires an efficiency separation for closure representation/update, not a naming distinction.
```

---

# 10. Revised admission vocabulary

Use the strongest justified label:

```text
MECHANISM
STRUCTURAL_KINGDOM_H0/H1
RESOURCE_DOMAIN_H1/H2
COMPLEXITY_DOMAIN_H3
COMPUTABILITY_DOMAIN_H4
```

Every label must include the registration scope and parent set.

---

# 11. Claim ceiling

This correction intentionally makes new-domain claims harder.

Current allowed statement:

> GMI has exact mechanism-level theorems for several theory-generated carriers, but no new classical complexity domain has yet been proved. Domain identity is now explicitly relative to a closed simulation-overhead class.

This prevents both extremes:

```text
"everything is Turing-equivalent, so there are no meaningful domains"

and

"every clever data structure is a new domain."

The research target is the middle: reproducible, semantics-preserving **efficient-realization separations**.