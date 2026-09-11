# GMI Formal Core Proofs v1

Status: **elementary formal deductions from GMI definitions**. These are not claimed as novel mathematics. They exist to make the synthesis internally checkable.

---

# P1 — future developmental equivalence is an equivalence relation

Fix an obligation/development/intervention contract `(O,D,J)` and a common measurable space of protected future traces.

Define

\[
d\sim d'
\]

iff for every registered future intervention/probe programme `j in J` and legal continuation under `D`,

\[
P(Future\mid d,j,D)=P(Future\mid d',j,D).
\]

## Reflexivity

For every `d,j,D`, a probability law equals itself. Therefore `d ~ d`.

## Symmetry

If `P(.|d,j,D)=P(.|d',j,D)`, equality is symmetric, so `P(.|d',j,D)=P(.|d,j,D)`. Therefore `d~d' => d'~d`.

## Transitivity

If `d~d'` and `d'~d''`, then for every `j,D`:

\[
P(.|d,j,D)=P(.|d',j,D)=P(.|d'',j,D).
\]

Therefore `d~d''`.

Hence `~` is an equivalence relation and the quotient

\[
Z_{O,D,J}=\mathcal D/\sim
\]

is well-defined.

**Boundary:** this proof assumes the compared situations are interpreted under the same registered future-trace semantics. Comparing different obligations/protocols requires an explicit translation map and is not covered.

---

# P2 — the quotient is minimal with respect to the chosen equivalence semantics

Let `q:D -> S` be any state representation sufficient to determine the complete registered future law: whenever `q(d)=q(d')`, the registered future laws are equal.

Then

```text
q(d)=q(d') => d~d'.
```

Therefore every cell of the partition induced by `q` is contained inside one `~`-equivalence class. Equivalently, `q` cannot merge two distinct `~` classes without losing sufficiency.

Thus the `~` quotient is the coarsest exact sufficient partition under the registered future semantics.

For finite deterministic automata/transducers this specializes to familiar minimal-state results; uniqueness of a concrete minimal machine is then up to state renaming/isomorphism under the parent theorem.

**Important:** this is minimality of abstract state distinctions, not minimal implementation description length or hardware size.

---

# P3 — morphology realizations are not uniquely determined by the quotient

Suppose two computational systems implement semantics-preserving maps

\[
\kappa_1:X_1\to Z,
\qquad
\kappa_2:X_2\to Z.
\]

If both preserve all registered future transitions/traces under the obligation, then both are valid realizations of the same abstract state process even if `X1` and `X2` have different:

```text
syntax
topology
parameterization
memory layout
locality
execution/update cost
```

Therefore abstract-state minimality does not imply unique computational morphology.

This is why neural, symbolic or programmatic realizations can be semantically equivalent while occupying different resource frontiers.

---

# P4 — pointwise capability/resource dominance is a partial order on frontier points

Fix coordinate semantics so capability coordinates are maximized and resource coordinates minimized.

For points

\[
p=(Q,B),\quad p'=(Q',B'),
\]

define

\[
p\succeq p'
\iff
Q_i\ge Q'_i\ \forall i
\quad\text{and}\quad
B_j\le B'_j\ \forall j.
\]

This relation is:

- reflexive: every coordinate equals itself;
- transitive: coordinate inequalities compose;
- antisymmetric: if both `p >= p'` and `p' >= p`, all coordinates are equal, so `p=p'`.

Hence it is a partial order on points.

---

# P5 — frontier dominance is a preorder on frontiers

For two frontier sets `F1,F2`, define

\[
F_1\succeq_F F_2
\]

iff every point of `F2` is weakly dominated by at least one point of `F1`.

## Reflexivity

Each frontier point dominates itself.

## Transitivity

If every point in `F3` is dominated by some point in `F2`, and that point is dominated by some point in `F1`, pointwise transitivity gives a point in `F1` dominating the original point in `F3`.

Thus frontier dominance is reflexive and transitive.

It is not necessarily antisymmetric as a relation on arbitrary representations/collections because distinct sets can have equivalent downward closures. If frontiers are canonical Pareto antichains over the same coordinate space, mutual dominance implies the same Pareto boundary under ordinary finite exact conditions; in more general continuous/approximate settings use explicit frontier-equivalence rather than assume syntactic equality.

---

# P6 — generality dominance is a preorder on deployed systems

For a registered ecology family `Eset`, deployed system `S=(M,d,D)` has profile

\[
I_S:E\mapsto F_S(E).
\]

Define

\[
S_1\succeq_{Eset}S_2
\]

iff

\[
F_{S_1}(E)\succeq_F F_{S_2}(E)
\]

for every `E in Eset`.

Because frontier dominance is reflexive/transitive, so is this relation.

But two distinct machines can have identical profiles, so antisymmetry on machine identities does not follow.

Therefore:

```text
Generality dominance is a PREORDER on deployed systems.
```

Define profile equivalence

\[
S_1\equiv_I S_2
\iff
S_1\succeq S_2\ \land\ S_2\succeq S_1.
\]

Then dominance induces a partial order on the quotient set of systems by `equiv_I` (subject to the same frontier-equivalence semantics).

This corrects loose wording that called the machine-level relation itself a partial order.

---

# P7 — no scalar ranking is implied by the preorder

If `S1` dominates `S2` on one ecology and `S2` dominates `S1` on another, neither dominates the registered ecology family.

A scalar ranking can still be produced only after choosing an ecology measure `mu` and scalar utility `u`:

\[
G_{\mu,u}(S)
=E_{E\sim\mu}[\sup_{p\in F_S(E)}u(p)].
\]

Changing `mu` or `u` can reverse the ranking of incomparable systems.

The executable GMI reference suite includes an exact reversal fixture.

---

# P8 — lifecycle break-even theorem

For scalarized build cost `A_i` and stationary per-use cost `c_i` over horizon `H`:

\[
C_i(H)=A_i+Hc_i.
\]

Morphology/system `i` costs less than `j` iff

\[
A_i-A_j+H(c_i-c_j)<0.
\]

When `c_i != c_j`, equality occurs at

\[
H^*=\frac{A_j-A_i}{c_i-c_j}.
\]

This is elementary arithmetic, but it establishes the exact condition under which expensive development can be amortized by cheaper future cognition.

For nonstationary costs, replace the stationary term with the registered cumulative expected cost; no one-number horizon formula is implied.

---

# P9 — optional capability expansion cannot hurt an ideal optimizer if truly free

Let strategy/action/development set `A1` contain `A0` and suppose old strategies remain legal with exactly zero new mandatory acquisition/storage/selection/maintenance overhead. For a fixed scalar cost objective:

\[
\inf_{a\in A_1}C(a)\le \inf_{a\in A_0}C(a).
\]

Proof: `A0` is a subset of `A1`, so the old minimizing choice remains available.

This is an ideal dominance statement only. Real inherited state can impose mandatory overhead, routing errors, interference or maintenance, which invalidates the premise. Hence there is no theorem that memory/history always helps an implemented machine.

---

# P10 — exact developmental-state quotient does not imply tractable construction

`Z=D/~` is semantically well-defined by P1/P2, but computing whether two arbitrary Turing-complete developmental situations are equivalent can encode undecidable behavior/reachability questions.

Therefore exact existence of the quotient is not an algorithm for constructing it.

GMI implementations require restricted classes, approximations, learned representations, predictive states or empirical certificates.

---

# Current proof status

```text
P1 future-equivalence relation                 PROVED_FROM_DEFINITION
P2 coarsest exact sufficient partition         PROVED_FROM_DEFINITION
P3 realization non-uniqueness                  DIRECT_CONSEQUENCE
P4 point dominance partial order               PROVED
P5 frontier dominance preorder                 PROVED
P6 system generality dominance preorder        PROVED
P7 scalarization requires extra choice         DIRECT_CONSEQUENCE + exact fixture
P8 lifecycle break-even                        PROVED
P9 free optional expansion ideal dominance     PROVED
P10 quotient construction may be undecidable   PARENT_LIMIT / proof detail delegated
```

These are structural foundations. They do not establish that the GMI abstraction predicts new real-world cognition.