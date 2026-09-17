# Finite candidate-space theorems v1

## Definitions

Fix positive finite integers `N,R`. `G0-fin-v1` uses label carrier
`L_n={0,...,n-1}` and register carrier `S_r={0,...,r-1}` for some
`1<=n<=N`, `1<=r<=R`. A program has entry label zero and assigns one typed
instruction instance to every label:

- `READ(s,l)`, `INC(s,l)`, or `EMIT(s,l)` for `(s,l) in S_r x L_n`;
- `DECJZ(s,l+,l0)` for `(s,l+,l0) in S_r x L_n x L_n`;
- `HALT`.

Each instruction contributes resource atom `(1,0)` and each declared register
contributes `(0,1)`. The budget order is coordinatewise. Thus the structural
resource of a program is exactly `(n,r)` and

`M(G0-fin-v1,(N,R))={P : rho(P)<=(N,R)}`.

For a finite interface `I=(W,T)` comprising a duplicate-free ordered tuple of
finite natural-number input words and positive step cap `T`, let

`obs_I(P) = ((status(P,w,T), output(P,w,T)))_{w in W}`,

where status distinguishes halt, blocked input, and exhaustion of the registered
step cap. Define `P ~_I Q` iff `obs_I(P)=obs_I(Q)`.

The registered neutral descriptor is a deterministic function

`D_I(P,d)=F(obs_I(P),rho(P),d)`

for a supplied exact finite developmental distance `d`. `F` returns the
semantic-key hash, status histogram, output-length profile, distinct external
output count, raw structural resource vector, and `d`. It receives no source
tokens, program identity, or architecture-family label.

## FINITE-1 — exact finite cardinality

**Theorem.** For positive finite `N,R`,

```text
|M(G0-fin-v1,(N,R))|
  = sum_{r=1..R} sum_{n=1..N} (1+3rn+rn^2)^n.
```

**Proof.** At fixed `(n,r)`, `READ`, `INC`, and `EMIT` each have `rn`
instances, `DECJZ` has `rn^2`, and `HALT` has one. Hence the finite instruction
alphabet has `q=1+3rn+rn^2` members. A total table independently chooses one of
these at each of `n` labelled positions, giving `q^n` tables. Register and label
counts are encoded in program identity, so strata for distinct `(n,r)` are
disjoint. Summing the finite stratum cardinalities proves the formula and
finiteness. QED.

The additive resource statement follows because summing `n` code atoms and `r`
register atoms gives `(n,r)` exactly; no scalarization is used.

## ENUM-1 — sound, complete, duplicate-free exact enumeration

**Theorem.** The constructive enumerator returns each member of
`M(G0-fin-v1,B)` exactly once at any accepted small budget.

**Proof.** It iterates every admitted `r`, then every admitted `n`, constructs
the complete typed alphabet above, and takes its `n`-fold Cartesian product.
Every emitted operand lies in `S_r` or `L_n`, so emission is sound. Conversely,
every well-typed program in the definition has one admitted `(n,r)` and one
instruction from that complete alphabet at every label, so its unique table
tuple occurs in that Cartesian product; this proves completeness. Program code
is `(r,(instruction_0,...,instruction_{n-1}))`. Product tuples are unique within
a stratum, and `r` plus tuple length separates strata, so no code is emitted
twice. QED.

The independent oracle separately constructs raw tuples without importing the
enumerator, its option builder, candidate classes, validation, or count
function. Exact set equality is checked for `(1,1),(2,1),(1,2),(2,2)`; a fifth
`(3,1)` comparison is held in the unit suite. This is corroboration, not the
analytic proof.

## QUOT-1 — exact declared-interface semantic quotient

**Theorem.** `~_I` is an equivalence relation, its fibers partition the finite
candidate set, and choosing the lexicographically minimum canonical code in
each fiber emits each quotient class exactly once.

**Proof.** `~_I` is equality after the total map `obs_I`; equality is reflexive,
symmetric, and transitive. Preimages of distinct observation tables are
disjoint, and every candidate belongs to the preimage of its own table, so the
nonempty fibers form a partition. A finite nonempty fiber of totally ordered
canonical codes has a unique minimum. Iterating distinct keys therefore emits
one and only one representative per fiber. QED.

On the registered 126-program interface, the exact quotient has 18 classes and
collapses 108 duplicate presentations. This number is interface-relative. The
theorem neither decides equality over all inputs and horizons nor claims that a
step-limited equivalence is universal program equivalence.

## DESC-1 — architecture-name-free factorization and invariance

**Theorem.** If two presentations have equal registered observation tables,
raw resource vectors, and developmental distances, their registered descriptors
are equal. Certified bijective surface reminting and consistent permutation of
the internal register carrier preserve descriptors when those three invariants
are preserved.

**Proof.** The descriptor is defined as the function `F` of exactly the stated
triple. Equal arguments have equal function values. A certified remint changes
only surface tokens and decodes to the identical typed operational table. A
consistent register permutation conjugates every register reference while the
all-zero initial state and external I/O remain unchanged; induction on execution
steps gives the permuted internal state, identical control label, and identical
external output after every step. Neither transformation changes `(n,r)`; with
the same supplied `d`, all inputs to `F` are equal. QED.

Behavioral equivalence alone deliberately does not force descriptor equality:
behaviorally identical programs may use different raw resources or have
different developmental distances. A token map that is not a bijection fails
closed, and an alleged remint that changes operational semantics is exposed by
the complete registered observation table.

## Boundary

All theorems quantify over the stated finite typed slice, exact raw budget,
declared finite interface, and finite developmental-distance input. General
program equivalence remains undecidable in Turing-complete settings; the package
does not weaken that boundary by relabelling a finite observation quotient as a
global semantic quotient. Likewise, descriptor independence from architecture
names is a factorization property at this registered resolution, not proof of a
unique universal species ontology.
