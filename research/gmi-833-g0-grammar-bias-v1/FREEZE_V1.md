# GMI #833 Section-E2 finite grammar-bias freeze v1

**Parent:** #833 Section E  
**Child:** #875  
**Depends on:** merged #868 / PR #873  
**Source main:** `367e14e9296cf79924ce56d89fad34b3769acb5d`  
**Pinned #868 manifest blob:** `cfe890b276cef0bdb2424877de878b9173547cf2`  
**Pinned #868 receipt blob:** `5d2948b9c04c84a46f6625e043753a489895478f`  
**Status:** pre-implementation theorem/evidence freeze

This file freezes the finite presentation universe, semantic test suite, code-length metric, mutation graph, remint definitions, hostile pair, expected structural counts, parent subtraction and claim ceiling before any #875 executor, tests, result receipt, reconciliation spec or dedicated workflow exists on this branch.

## 1. Scientific boundary

A grammar/search representation is an inductive bias. This tranche measures that bias exactly on one bounded slice of the already-merged `G0-reg-v1` operational grammar. It does **not** establish a universal algorithmic prior, universal search neutrality, Kolmogorov-neutral finite description lengths, or morphology invariance under arbitrary grammar changes.

The formal object is a finite grammar/search presentation

`G=(P,M,sigma,ell,E,S0)`

with finite nonempty syntax presentations `P`, finite semantic classes `M`, surjective semantics `sigma:P->M`, exact nonnegative description length `ell:P->N`, directed mutation/search relation `E`, and nonempty start set `S0`.

## 2. Frozen bounded `G0-reg-v1` slice

Import the five #868 instruction classes and executor semantics unchanged.

Use exactly one register `r`, start label `L0`, and two label-count strata:

### One-label stratum

Labels `{L0}`. Because every successor must be `L0`, the legal instruction choices at `L0` are exactly:

- `HALT`
- `READ(r,L0)`
- `INC(r,L0)`
- `EMIT(r,L0)`
- `DECJZ(r,L0,L0)`

Hence exactly **5** presentations.

### Two-label stratum

Labels `{L0,L1}`. At each label there are exactly:

- one `HALT`;
- two `READ` successors;
- two `INC` successors;
- two `EMIT` successors;
- four `DECJZ` successor pairs;

for **11** instruction choices per label and `11^2 = 121` programs.

Total frozen syntax presentations:

`|P| = 5 + 121 = 126`.

Program identity is a canonical tuple `(label_count, instruction_at_L0 [, instruction_at_L1])`; surface node names introduced later by a remint are not semantic.

## 3. Frozen semantic equivalence

For every presentation `p`, execute the imported #868 semantics on exactly these protected inputs:

```text
()
(0,)
(1,)
```

with exact step budget `6`.

The semantic signature is the ordered triple

```text
sigma(p) = ((terminal_0, output_0),
            (terminal_1, output_1),
            (terminal_2, output_2)).
```

Register contents, label names and internal traces are deliberately excluded from this protected semantic signature. Thus this is a bounded behavioral equivalence, not universal program equivalence.

The number and multiplicities of resulting semantic classes are **not frozen as outcomes**; they must be computed after activation.

## 4. Frozen description metric and exact bias quantities

Description length is instruction count:

```text
ell(p)=1  for one-label programs
ell(p)=2  for two-label programs.
```

For semantic class `m`, define:

```text
L_G(m)   = min{ell(p): sigma(p)=m}
N_G(B,m) = |{p: sigma(p)=m and ell(p)<=B}|
Q_G(B,m) = N_G(B,m) / |{p:ell(p)<=B}|
```

when the denominator is nonzero.

`L_G` is grammar-relative shortest registered description. `Q_G` is syntax-count mass under uniform sampling of the bounded syntax slice; it is not a Bayesian posterior or universal prior.

## 5. Frozen mutation/search graph

Let `E` be the undirected relation represented as two directed edges for each allowed move.

### Mutation move

At fixed label count, replace exactly one labelled instruction by any other legal instruction for that label set.

### Add/delete-label move

From a one-label program, add `L1` while preserving its existing `L0` instruction and choose any legal two-label instruction for `L1`.

The inverse delete move exists exactly when deleting `L1` leaves the `L0` instruction well typed in the one-label grammar, i.e. the `L0` instruction references no `L1` successor.

Start set:

```text
S0 = { one-label HALT presentation }.
```

Every edge has unit cost.

For presentation `p`, let `dist_G(p)` be shortest-path distance from `S0`, or infinity. For class `m`:

```text
d_G(m)   = min{dist_G(p):sigma(p)=m}
A_G(k,m) = |{p:sigma(p)=m and dist_G(p)<=k}|
R_G(k)   = {m:d_G(m)<=k}.
```

These are exact reachability-bias quantities under the frozen mutation graph, not a claim about every search algorithm.

## 6. BIAS-1 target — finite description bias

Analytic target: `L,N,Q` are exactly computable because `P` is finite and `ell,sigma` are decidable on every presentation.

Machine evidence must enumerate all 126 presentations exactly once and record:

- number of semantic classes;
- complete class multiplicity histogram;
- histogram of `L_G`;
- per-budget (`B=1,2`) class counts and exact rational syntax masses;
- no silent class dropping.

No asymptotic or universal coding claim follows.

## 7. BIAS-2 target — finite reachability bias

Analytic target: `dist_G` and therefore `d,A,R` are exactly computable by finite graph shortest paths.

Require two independent implementations:

1. ordinary breadth-first search from `S0`;
2. monotone fixed-point wave expansion `W_0=S0`, `W_{k+1}=W_k union Succ(W_k)` until stable.

They must agree presentation-by-presentation and class-by-class.

The exact number of semantic classes at each distance is an outcome and is not frozen here.

## 8. REMINT-1 — isometric grammar-remint theorem target

An **isometric semantic remint** from `G` to `G'` is a bijection `phi:P->P'` satisfying for every `p,q`:

```text
sigma'(phi(p)) = sigma(p)
ell'(phi(p))    = ell(p)
(p,q) in E      iff (phi(p),phi(q)) in E'
p in S0         iff phi(p) in S0'.
```

### Target theorem

For every class `m`, budget `B` and search radius `k`:

```text
L_G(m)   = L_G'(m)
N_G(B,m) = N_G'(B,m)
Q_G(B,m) = Q_G'(B,m)
d_G(m)   = d_G'(m)
A_G(k,m) = A_G'(k,m)
R_G(k)   = R_G'(k).
```

Proof target: bijection transports each defining set exactly; graph-isomorphism plus start-set preservation transports paths length-for-length.

### Frozen executable fixture

Use a four-presentation finite grammar fixture with four surface node names. Exhaust every `4! = 24` syntax-name permutations as remints. Every certified isometric remint must preserve all bias quantities and a frozen grammar-relative selection functional.

This fixture is independent of #864's machine-state remint: it remints **program presentation nodes/search graph**.

## 9. Grammar-relative morphology selection boundary

For a finite candidate semantic set `C subseteq M`, freeze the demonstration selection functional

```text
Sel_G(C) = lexicographic argmin over m in C of
           (L_G(m), d_G(m), canonical_semantic_key(m)).
```

This is a diagnostic grammar-relative selector, not a normative intelligence objective.

Under REMINT-1, the tuple is invariant for every `m`, hence `Sel_G(C)` is invariant.

## 10. REMINT-2 frozen hostile — same semantics, changed grammar bias

Construct two tiny grammars with the same semantic image `{ROOT,A,B}` but different syntax geometry.

### Grammar GA

Presentations `{root,a,b}`:

```text
sigma(root)=ROOT, ell(root)=0
sigma(a)=A,       ell(a)=1
sigma(b)=B,       ell(b)=2
S0={root}
edges: root <-> a <-> b
```

For candidate set `{A,B}`:

```text
(L,d)(A)=(1,1)
(L,d)(B)=(2,2)
Sel_GA={A}.
```

### Grammar GB

Presentations `{root2,a2,b2}` with the **same semantic image**:

```text
sigma(root2)=ROOT, ell(root2)=0
sigma(a2)=A,       ell(a2)=2
sigma(b2)=B,       ell(b2)=1
S0={root2}
edges: root2 <-> b2 <-> a2
```

Then

```text
(L,d)(A)=(2,2)
(L,d)(B)=(1,1)
Sel_GB={B}.
```

Thus the same semantic coverage does not imply the same description bias, reachability bias, or grammar-relative selected morphology. GA and GB are semantically equivalent by image but not isometric semantic remints.

## 11. Frozen remint hostiles

Certification must fail closed for:

- non-bijective node map;
- semantic-map corruption;
- description-length corruption;
- missing/added edge not transported by `phi`;
- start-set corruption;
- arbitrary semantic-only map presented as an isometric remint.

Each failure must identify its violated condition.

## 12. KOL-BOUND — invariance-theorem boundary

Classical Kolmogorov/algorithmic-complexity invariance says that suitable universal description systems differ by at most a description-system-dependent additive constant. This tranche neither reproves nor strengthens that parent theorem.

Frozen non-inference:

```text
additive-constant asymptotic invariance
!= equality of finite L_G
!= equality of bounded syntax mass Q_G
!= equality of mutation distance d_G.
```

The GA/GB hostile already witnesses finite inequality without contradicting the classical theorem.

## 13. Strongest-parent subtraction

- SyGuS: grammar is explicit syntactic candidate-space restriction.
- Whigham / grammar-based GP: language and search bias depend on grammar; same semantic language can have different connectivity/search landscape.
- McKay et al. survey: grammar restrictions and representation/search connectivity are parent observations.
- Kolmogorov/Solomonoff/Chaitin invariance: only additive-constant universal-description boundary, not finite equality.
- #863: generic robustness requirement for alternate encodings/search algorithms/scalarizations.
- #864: semantic machine-state remint equivariance; explicitly not search invariance.
- #868: operational G0 semantics and manifest/receipt authority pinned above.

## 14. Reconciliation ceiling

After green dedicated CI, this tranche may reconcile only these #833 Section-E rows at the declared bounded scope:

- Quantify description-length bias induced by `G0`.
- Quantify reachability bias induced by `G0`.
- Construct multiple semantically equivalent grammars with different syntax.
- Test whether morphology conclusions survive grammar reminting — disposition must explicitly say **invariant under certified isometric grammar remints, not invariant under arbitrary same-semantics grammar changes**.

## 15. Claim ceiling

`GMI_FINITE_GRAMMAR_BIAS_AND_REMINT_BOUNDARY_AT_REGISTERED_G0_SCOPE`

Forbidden promotions:

- `UNBIASED_G0`
- `UNIVERSAL_ALGORITHMIC_PRIOR`
- `KOLMOGOROV_NEUTRALITY`
- `GRAMMAR_REPRESENTATION_INVARIANT_UNIVERSALLY`
- `SEARCH_REACHABILITY_INVARIANT_UNIVERSALLY`
- `MORPHOLOGY_SELECTION_INVARIANT_UNDER_ARBITRARY_GRAMMAR`
- `ALL_GRAMMARS_EQUIVALENT`
- `COMPLETE_GMI`
