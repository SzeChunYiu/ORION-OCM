# GMI mathematical core completion v1

## 1. Imported equivalence boundary

The four parent-equivalence checklist items are already closed by merged PR
#847, whose `gmi-833-parent-equivalence-v1` package supplies the exact
Myhill–Nerode, bisimulation, statistical-sufficiency, and predictive-state
specializations and counterboundaries. This tranche imports that result and
does not claim those boxes again. The local deterministic partition refinement
is retained only to evaluate the finite witness for axiom AX4.

## 2. Morphology and machine species

At registered scope `Omega`, a reduced mechanism signature contains the
protected state/transition/observation relation, registered
intervention-response relation, experiment-indexed raw lifecycle resource
vectors, and resource-labeled developmental relation. Two finite morphologies
are equivalent when a type-preserving carrier bijection commutes with every
transition and preserves every observation, intervention response, experiment
resource vector, and developmental edge/charge. This is typed resource-labeled
relational isomorphism, independent of carrier or syntax names. Behavior-only
equality is insufficient when any other preserved relation differs.

The legacy term **machine species** is defined as the quotient class under this
same relation. Paper-facing text should use **computational-mechanism
equivalence class** unless a biological analogy is explicit; no biological
ontology follows from the quotient.

This is an equivalence relation. Identity is an admissible isomorphism,
inverting a preserving bijection proves symmetry, and composing two preserving
bijections proves transitivity. State/syntax renaming stays in the same class;
altering a resource coordinate, intervention outcome, or developmental edge
provides a negative control outside the class.

## 3. Capability ceilings and impossibility

A capability contract is externally declared by its task/ecology distribution,
utility or acceptance functional, verifier, resource budget, and threshold. A
machine's capability coordinate is 1 exactly when its protected outcomes and
resource observations satisfy that contract; otherwise it is 0. Its capability
region is the set of satisfied contracts. No architecture label is an input.
Consequently realization renaming cannot change the region. Exact morphology
equivalence implies equal regions whenever every contract is measurable from
the relations preserved by the signature.

For an admissible possibility set `U`, coordinate bounds are
`L_j=min_{u in U} C_j(u)` and `H_j=max_{u in U} C_j(u)`. `H_j=0` is an
impossibility region at that scope; `L_j=1` is a guaranteed capability; and
`(L_j,H_j)=(0,1)` is non-identifiable. These are exact finite bounds, not a
claim that a real system's possibility set is known.

The bounds are sharp: because `U` is nonempty and the coordinates are Boolean,
the minimum and maximum are attained. Every admissible realization obeys
`L_j <= C_j <= H_j`; no tighter universal interval can contain all values in
`U`. Hence `H_j=0` proves impossibility relative to exactly the declared
specification, ecology, resource/history conditions, and uncertainty set. It
does not prove an unconditional physical impossibility after those premises are
changed.

For a numeric capability functional `V_c`, the ceiling over an admissible class
`A_Omega` is `sup_{M in A_Omega} V_c(M)` (a maximum in the registered finite
scope). A threshold above it, or an empty admissible class, is an impossibility
region. If a resource budget is relaxed, its admissible class can only expand;
if `A subseteq A'`, then `sup_A V_c <= sup_A' V_c`. Thus ceilings are monotone
under class/budget relaxation and impossibility regions can only shrink.

### Architecture-independent information ceiling

Let latent world `W` be uniform on `{0,1}`, let both worlds emit the same
pre-action observation, and require binary action `A=W` for success. Every
randomized policy is a single number `p=P(A=1)`, so

`P(success) = (1/2)(1-p) + (1/2)p = 1/2`.

Therefore the capability ceiling is exactly `1/2` for every architecture; every
threshold above `1/2` is impossible at this information scope. Revealing `W`
before action admits `A=W` and gives the positive-control ceiling `1`. The
executable P2 control enumerates all 21 policies `p=k/20` with exact rational
arithmetic and obtains `1/2` for every point; that grid is evidence for the
implementation, while the displayed identity proves the continuum theorem.

## 4. Uncertainty, composition, and abstention

Every uncertain object in GMI—machine, ecology, developmental law, verifier,
resource ledger, specification, or derived claim—is a nonempty typed set of
possible worlds, optionally paired with a valid coverage level. Deterministic
maps propagate uncertainty by set image. Joint composition uses the Cartesian
product unless registered dependence removes pairs. These set-image statements
hold for arbitrary sets; the executable witness is finite because that fragment
is decidable by enumeration.

For confidence events `E_i` with marginal coverage `1-alpha_i`, the union bound
gives joint coverage at least `max(0,1-sum alpha_i)` without independence. With
registered mutual independence, product coverage is valid. Multiplying marginal
coverages without that premise is forbidden. These rules apply to any finite
number of registered confidence objects and thus cover the general declared
core scope.

Proof: `P(intersection E_i) = 1-P(union E_i^c)` is at least
`1-sum P(E_i^c)` by subadditivity, clipped at zero. Under mutual independence,
the same intersection probability equals the product of the marginal
probabilities. No pairwise-only or unregistered independence premise licenses
that product. Set image is sound because the true world's image remains in the
image of every set containing that world; Cartesian composition is sound when
all cross-combinations are admissible, and dependence restrictions must be
represented by an explicit subset of that product.

A decision is determinate iff all admissible worlds yield the same value. An
empty set returns `INFEASIBLE`; one distinct value is returned; two or more
return `CANNOT_IDENTIFY`. Abstention is not counted as correctness.

## 5. Compact axioms and consistency

`AXIOMS_V1.json` contains ten typed axioms covering domains, specification,
finite process, equivalence, development, resources, capability, uncertainty,
abstention, and scope tags. The definitions above derive the response quotient,
morphology/species relations, capability profile and bounds, uncertainty
pushforward/composition, and abstention rule from those primitives. Its explicit
two-state/two-action model is checked axiom-by-axiom and satisfies all ten.
Model existence proves syntactic consistency of
this registered finite theory relative to ordinary finite set/arithmetic
semantics: if both a sentence and its negation were derivable in a sound proof
system, no model could satisfy all axioms.

This is not a proof of consistency for arbitrary future extensions, set theory,
real arithmetic, or an unbounded self-referential GMI theory.

The executable checker evaluates ten named predicates, one per axiom, against
the witness. The deterministic receipt requires `axioms_satisfied=10`; deleting
a transition, introducing a negative resource, omitting a type/scope, or making
the two uncertain observations agree falsifies a corresponding check.

## Falsifiers

The tranche fails if partition refinement disagrees with a distinguishing
continuation; a morphology equivalence does not preserve
types/transitions/observations/resources; capability changes under architecture
renaming; a confidence rule exceeds the valid union/product bound; a
determinate value is emitted under disagreement; or the finite witness violates
any registered axiom.
