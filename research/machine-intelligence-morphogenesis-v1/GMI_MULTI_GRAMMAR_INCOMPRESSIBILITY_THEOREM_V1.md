# GMI Multi-Grammar Incompressibility Theorem v1

Status: **FORMAL SUCCESSOR TO GRAMMAR-BIAS FALSIFICATION / ZERO-PRIOR COMPRESSION HARDENING**

Status date: 2026-09-12.

Purpose:

> Replace handpicked “hard” label vectors with a family-level incompressibility theorem that is valid for any preregistered finite set of description languages. This supplies a principled negative twin for shared-law compression versus explicit memory.

---

# 1. Finite exact target family

Let the registered query domain contain `N` distinguishable points and the exact output alphabet have size `q>=2`.

The unrestricted exact target family is

\[
\mathcal F=[q]^N,
\qquad
|\mathcal F|=q^N.
\]

Let a description language / grammar `G` assign binary descriptions to exact target functions. Write

\[
K_G(f)
\]

for the length in bits of the shortest valid description of `f` under `G`, including every grammar-specific token/compiler convention required by the preregistration.

No computability assumption beyond finite exact decoding is needed for the counting theorem below.

---

# 2. Single-grammar incompressibility bound

## Theorem MG-1 — few functions have short exact descriptions

For any fixed binary description language `G` and any integer `L>=0`, the number of distinct exact functions with a description shorter than `L` bits is at most

\[
2^L-1.
\]

Therefore for a uniformly random target

\[
F\sim\operatorname{Unif}([q]^N),
\]

\[
\Pr[K_G(F)<L]
\le
\frac{2^L-1}{q^N}
<
\frac{2^L}{q^N}.
\]

### Proof

There are exactly

\[
\sum_{j=0}^{L-1}2^j=2^L-1
\]

binary strings shorter than `L`. Even if every such string is a valid program and every program denotes a different target, no more than `2^L-1` functions can receive such a short description. QED.

---

# 3. Near-table-length incompressibility

Assume for simplicity that `q^N` is compared in bits through

\[
B_{table}=N\log_2q.
\]

Set

\[
L=B_{table}-s
\]

for compression saving `s>0` bits (with integer rounding where needed).

## Corollary MG-1.1

A uniformly random exact labeling admits an exact description saving at least `s` bits relative to unrestricted target identity with probability at most approximately

\[
2^{-s}.
\]

More exactly,

\[
\Pr[K_G(F)<N\log_2q-s]
<2^{-s}.
\]

Thus **most exact independent labelings are incompressible by a large margin in every fixed language**.

This is a counting statement, not an appeal to a specific polynomial degree or surface pattern.

---

# 4. Multiple preregistered grammars

Let

\[
\mathcal G=\{G_1,\ldots,G_m\}
\]

be `m` distinct frozen grammars/search encodings.

Define best registered description length

\[
K_{\mathcal G}(f)=\min_jK_{G_j}(f).
\]

## Theorem MG-2 — multi-grammar union bound

For uniform random target `F`,

\[
\Pr[K_{\mathcal G}(F)<L]
\le
m\frac{2^L-1}{q^N}
<
m\frac{2^L}{q^N}.
\]

### Proof

Apply MG-1 to each grammar and union-bound the events that at least one grammar provides a description shorter than `L`. QED.

## Corollary MG-2.1

To make the probability of an accidental `s`-bit compression across any of `m` grammars at most `delta`, it is sufficient to choose

\[
s\ge\log_2\frac{m}{\delta}.
\]

Equivalently, with probability at least `1-delta`,

\[
K_{\mathcal G}(F)
\ge
N\log_2q-\log_2\frac{m}{\delta}
\]

up to integer rounding.

---

# 5. Grammar/compiler cost must be charged

A pathological “grammar” could contain the protected target itself as a one-token primitive. That does not invalidate the theorem; it means the grammar/compiler description has encoded the world identifier outside the measured program.

Therefore GMI requires the total description/lifecycle accounting

\[
K(\text{grammar/compiler})
+
K_G(f)
+
B_{search/eval/update}.
\]

A target-specific macro introduced after seeing protected data is contamination and fails the D/V/P firewall.

For a frozen reusable grammar, grammar cost may be amortized over registered worlds according to the declared horizon.

---

# 6. Correct negative twin for coefficient/shared-law compression

The architecture-neutral negative twin is no longer one vector such as

```text
[0,0,0,0,1]
```

which turned out to be easy in a richer equality grammar.

Instead use a **protected independent-label generator**:

\[
F(x_i)\overset{iid}{\sim}\operatorname{Unif}([q]).
\]

Freeze grammars and description/resource budgets before drawing the protected target.

Then MG-2 gives a preregistered upper bound on the chance that an unrelated short exact shared law exists across those grammars.

This is the right negative control for “there is no reusable exact semantic structure here” at finite scope.

---

# 7. Positive twin

Choose a protected structured family with known small generative description, for example

\[
f_\theta(x)
\]

where parameter identity requires `B_struct << N log2 q` bits and the legal family is frozen before target draw.

Then compare total lifecycle burden of:

```text
shared-law realization
shared-law + residual realization
explicit memory/table realization
```

under equal exact semantics.

The positive/negative pair now differs in **target-family entropy/description structure**, not a handpicked surface pattern.

---

# 8. Connection to developmental data burden

For a finite structured family of size `M`, earlier finite-class learning bounds scale with `log M`.

For unrestricted independent labels,

\[
M=q^N,
\qquad
\log_2M=N\log_2q.
\]

Thus the same family-size variable controls both:

```text
retained exact target-state information
identification/data burden in finite realizable settings
```

This strengthens the GMI bridge between compression, memory and learning.

---

# 9. What remains language-dependent

The theorem does **not** provide an absolute Kolmogorov complexity for a particular real target. It says:

1. for each frozen finite grammar, most targets require nearly full target-identity information;
2. the statement survives any finite preregistered grammar ensemble with a logarithmic union-bound penalty;
3. grammar/compiler/search costs must be charged;
4. specific structured real tasks still require measurable evidence that they belong to a compressible family.

---

# 10. Zero-prior successor protocol

For coefficient/basis/model versus memory:

1. preregister at least three materially different low-level description/search languages;
2. preregister compiler and search budgets;
3. use structured positive target generators;
4. use uniform/random-independent protected negative generators;
5. freeze exact/approximate semantic tolerance;
6. predict shared-law/residual/memory frontier before protected target draw;
7. semantic-remint both families;
8. require independent search encodings to recover the predicted structural phase;
9. preserve every grammar-specific failure.

---

# 11. Revised evidence status

```text
old polynomial negative vector:
    RED as cross-grammar control

single richer DSL exhaustive hostile:
    GREEN / predecessor falsified

family-level multi-grammar incompressibility theorem:
    PROVED-EXACT

multi-grammar protected rediscovery:
    OPEN-BLOCKING
```

Desired successor terminal:

`ZERO_PRIOR_COMPRESSION_MULTI_GRAMMAR_GREEN`.
