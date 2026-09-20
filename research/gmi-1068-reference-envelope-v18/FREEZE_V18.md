# V18 / R preregistration — reference families and declared measures

Control plane: #1068; historical evidence programme: #833.
Planning parent: bb5216bbe46c6cde913baad212d7a2376f0278ea (Q, PR #1113).
Import merged Q main ancestry before publication. This freeze precedes all R
outcome code, proofs, tests, receipts and adjudication. Only GMI2-R2-008 is
eligible for original closure: "relate Legg-Hutter and intelligence measures".
Its current Q status is UNKNOWN; original evidence kind is FORMAL_OR_FINITE.
Original R2 freeze target 8, verbatim:
> Parent-subtract Legg-Hutter and decision/resource theory.

## R1 — actual prefix wrapper and shortest-description laws

Fix a partial computable prefix string-output machine U, a fixed injective
assignment i↦c(i) of distinct binary description codes to the environments
under comparison, a target z, and an integer L≥2. A wrapper outputs c(z) on
the exact one-bit programme 0, outputs U(p) on 1^L concatenated with p, and
is undefined otherwise. It outputs a description, not an environment execution.
Prove the exact successful-domain classification, inherited prefix freedom,
compiler simulation and universality when U is a universal prefix machine.
Prove from shortest successful programmes, rather than assume as a K axiom:
K_wrapper(c(z))=1 and K_wrapper(c(i))=L+K_U(c(i)) for every i≠z.
For a nonuniversal base, a nontarget description exists on one side iff it
exists on the other; the displayed finite equality applies when it exists.
A universal base supplies every finite code. Distinct codes, exact singleton
matching, and rejection of wrapper input ε are essential. Prefix freedom alone can hold at L=1; no claim says all such
short padding is invalid. L≥2 supplies the registered concentration margin.

Choose one shortest programme per distinct code. Kraft gives total base
weight at most1. Wrapper target weight is1/2; all other code weights sum to
at most2^-L. Keep these weights unnormalized: they are subprobability weights,
not a probability simplex inferred from process structure. Equal-output
programmes contribute one shortest-output weight, not their programme mass.

## R2 — exact envelope order and an actual policy reversal

For a fixed countable environment index set and arbitrary profiles v,w into
[0,1], define S_U(v)=Σ_i 2^-K_U(c(i))v(i). Prove convergence and
v≤w coordinatewise iff S_U(v)≤S_U(w) for every universal prefix U.
Forward direction uses nonnegative weights. If v(z)-w(z)=δ>0, a wrapper
with 2^-L<δ/2 gives S_wrapper(v)-S_wrapper(w)≥δ/2-2^-L>0.
The machine family must include every required target/padding wrapper;
completeness is not claimed for a finite, natural, or otherwise restricted family.
For 0≤v≤B, prove (1/2)v(z)≤S_wrapper(v)≤(1/2)v(z)+B·2^-L.
Thus padding approximates a half-coordinate uniformly for a common bound.
The envelope order is independent of the fixed injective coding because it
is pointwise order, with the environment class and reward semantics fixed;
individual scores and rankings need not be coding-independent.
No effective enumeration of all computable environments or computable K is
asserted. Countability, semantic environment identity and coding are explicit.

Give actual computable deterministic one-shot environments on two actions.
Honor the LH2007 environment-first timing: initial reward0, reward1 just after
the first action iff it is the designated action, and reward0 forever after.
Their total reward is at most1 for every policy. Two fixed policies taking
opposite initial actions have opposite value profiles in these environments.
Under their respective target wrappers, each policy strictly outranks the
other despite arbitrary bounded performance in every remaining environment.
This is a reward-summable witness, not a forever-reward discounted surrogate.

## R3 — declared expectation and lower-envelope contexts

Construct actual finite expectation contexts with externally supplied weights
w_i≥0, Σw_i=1, and finite nonempty-prior-family lower-envelope contexts
v↦min_{w∈Γ}Σ_i w_i v_i. Prove monotonicity and constant preservation;
singleton Γ returns its expectation. Preserve the caller's P, E, active P∩E,
and illegal/undefined/value tags through the existing Context interface.
State zero-dimensional feasibility: there is no normalized empty weight vector.
No prior, reward, direction of preference or calibration is inferred.

Exhibit a concrete failure of recursive lower-envelope consistency. On states
AC,AD,BC,BD take priors (1/2,0,0,1/2) and (0,1/2,1/2,0), and payoff
(1,0,1,0). Its ex ante lower expectation is1/2 but each branch's conditional
lower expectation is0; a constant1/4 reverses the act preference after
conditioning. The rectangular closure has all four independent branch C/D
choices, branch masses1/2, and restores both values to0. This verifies this
example only; general dynamic consistency requires the parent's rectangularity,
updating and preference assumptions. One-shot aggregation alone does not imply it.

## R4 — free conversion and a complete family of resource contexts

Supply a lawful process category and a free-arrow predicate containing every
identity and closed under actual composition. Define a≽b iff a free arrow
exists from a to b, and derive reflexivity/transitivity from these witnesses.
For each target z construct the actual Bool context M_z(a)=1 iff a≽z.
Prove a≽b implies M_z(a)≥M_z(b), and that all these inequalities imply a≽b
by choosing z=b. This orientation must be explicit when using false≤true.
Equivalent but distinct resources need not be identical; the relation is a
preorder. Free arrows and any tensor are supplied choices. Tensor is unnecessary
for this preorder theorem and is not derived from the bare category.
The complete family is a classical parent result, not one universal scalar,
a unique resource measure, or a derivation of physical admissibility.

## Prospective calibration and falsifiers

All counts below are planning algebra, not outcomes or empirical predictions.
Enumerate binary programmes of lengths0..3, including ε; all prefix-free
subsets and assignments of output labels0/1 yield15,131 finite books on677
domains (F_0=3, F_d=2+F_{d-1}²). Each book×two targets×L∈{2,3,4}
gives90,786 wrappers. These finite books are never called universal.
Check actual parsing, domain prefix freedom, shortest lengths and weights.
Nine two-dimensional profiles over{0,1/2,1} per wrapper give817,074 exact
score-bound checks. Test empty/ε-only books and programmes00/01 sharing one
output: shortest-output weight1/4, not programme mass1/2.

Profiles in dimensions0..3 over{0,1/2,1} give40 profiles and820 ordered
same-dimension pairs. Denominator4 probability weights in dimensions1..3
number1,5,15, yielding11,349 pair-weight checks. All31 nonempty families of
the five two-state weights give279 profile-family values and2,511 pair-family
checks. Exercise the actual nonrectangular example and rectangular repair.
All35 labelled preorders on0..3 resources give278 pairs and816 pair-target
checks, including equivalent-but-distinct states and order-orientation controls.

Mandatory controls: reject nonprefix books, malformed/aliased types, unbounded
profiles, invalid probability vectors and empty prior families; distinguish
undefined output from an output label. Omit a Dirac coordinate to demonstrate
failure of an incomplete separating family. A minimum envelope is nonlinear.
Show that insufficient padding can fail a requested strict margin, without
claiming every L=1 wrapper fails. For base ε→nontarget, L=2 assigns weights
(1/2,1/4): profiles (1/2,0) and (0,1) tie despite a positive target gap;
L=3 makes the first strictly better. Include empty dimensions and P/E tag controls.
Production and oracle must compute independently; no oracle delegates its answer
to production. Exact rational arithmetic must retain tiny positive differences.

## Proof boundary, evidence and immutable successor accounting

Lean4.19 must freshly replay actual List Bool parsing/wrapping and shortest
successful-programme laws, a finite scaled-score separation/tail theorem, actual
free-category convertibility/Bool-family completeness, and registered Context
constructors/laws within their declared scalar model. Machine α=Program→Option α
is a denotation with an executable wrapper; it is not an implemented universal
Turing machine. TM computability/universality, infinite Kraft sums, the full
Real envelope theorem and Real probability semantics remain complete paper
proofs. State this distinction in the formal scope and every adjudication.
No generic Int theorem alone certifies countable Real summation.
Freshly build bound inherited dependencies. Register exact theorem types and
constructor outputs; source-valid proof corruptions must compile changed source
but fail the typed AUDIT. Include wrapper/shortest and separation/resource laws.
Mandatory test inventories/counters, real corruption controls, clean positive
controls and normal/-O receipt equality guard the executable record. Missing
tools/inputs are CANNOT_CHECK exit2; checked invalidity is exit1.

Preserve all222 original IDs/titles and every untouched status/evidence entry.
Only R2-008 may become CLOSED after complete proofs, independent review and
gates. Original fulfillment19/unresolved203 then becomes20/202; R2 remains
OPEN and R0 remains the only whole-EARNED round. R2-006 remains CLOSED;
R2-003/007/009 and R1-006 are not closed by this study.
Carry the two immutable qualified V16 readings separately, deriving200 active
unresolved from202 original unresolved. Never treat replacements as original
fulfillment or historical V16/V17 totals as current. This is an explicit
checkpoint chain, not discovery of an automatically latest amendment ledger.
Dereference inherited receipt inputs, bind current reconciliation to the actual
snapshot, and reject coupled custody/scope mutations. No canonical prior,
complete intelligence theory, architecture recovery or novel mechanism is claimed.

## Primary ownership and planning-parent source bindings

LH2007 §§3.2/3.3/3.5 owns the reward-summable measure and reference-machine
qualification: https://arxiv.org/html/0712.3329v1
Leike–Hutter2015 Lemma1, §4 Corollary14 and §5 Theorem18 own concentration
and the Pareto limitation: https://proceedings.mlr.press/v40/Leike15.pdf
Their discounted LSCCCS model differs from LH2007 reward-summable measures;
this round adapts the concentration argument and gives its own bounded witness.
CFS2014 §3.1 Definition3.3 and §5.1 Proposition5.2 own supplied free processes
and the complete target family: https://arxiv.org/pdf/1409.5531
Epstein–Schneider §3.1/Theorem3.2 owns the dynamic-consistency boundary:
https://people.bu.edu/lepstein/files-research/rectang50.pdf
The envelope theorem is an elementary concentration corollary; no originality
is claimed. Every named result needs premises, dependencies, falsifier and
strongest-parent ownership in the subsequent ledger, not a blanket analogy.

| Source | SHA256 |
| --- | --- |
| research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json | 4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574 |
| research/gmi-1068-r2-context-irreducibility-v1/FREEZE_V1.md | cd3754eb383e2796c3fe06dc7e9fbb7cf17d9d0bca35bea983e43fbc6b6ae320 |
| research/gmi-1068-r2-context-irreducibility-v1/THEORY_V1.md | 09773eab96a80843585154e6211e494b9ca721393542a8cbdd114fe7bae3ab5e |
| research/gmi-1068-context-specializations-v17/FREEZE_V17.md | bbcbc2984380877a96d229d2c3888b604f170cc1f129af48a77efd03daefd848 |
| research/gmi-1068-context-specializations-v17/RESULT_V17.json | 670f7ce0a660e5672f8f58658a0e0e98d7969b5c47e79ba6d341d3e8e628b915 |
| research/gmi-1068-recursive-audit-v17/SCOPE_SNAPSHOT_V17.json | 491cc11bb987a637f3413f53f74fcf0c1c00c0564adc7da24b5f982d583f32d3 |
| research/gmi-1068-recursive-audit-v17/CURRENT_ACCOUNTING_V17.json | 3b834772b0d53a0b7143b3b6deca95d8af768b57a4537fed4a0c9973716af6c1 |
| research/gmi-1068-corrected-targets-v16/TARGET_CONTRACT_V16.json | faa8f83c0af7a2f0a042e84deb7be191b09a281c08f287c5e986397124177902 |
| research/gmi-1068-corrected-targets-v16/RESULT_V16.json | 18bea5c6f85b4fcc91c40c53cbf63df59c38d70e9e839efc4585f6640497ad1a |
| research/gmi-1068-amendment-governance-v16/AMENDMENT_LEDGER_V16.json | e1cc2d2dbc10171407577889f75ac531c30cf09eab224fc3823f3931c5048618 |
| research/gmi-1068-amendment-governance-v16/RESULT_V16.json | ed491fab2cd0b69fb4ee845b82e349c79ff0d70f0dbc1d312ee0755645437de4 |
| research/gmi-1068-partial-context-v15/PartialContextV15.lean | 332dcfb63304d5668800ea21f09795c2d92267989291ffe35d9e38ea2db0edf5 |
| research/gmi-1068-foundation-repair-v5/AdmissibilityV5.lean | e69b53945a50aa20b455b67346a0d01b708443327a0b5fcd18ee2e62f075747b |
| research/gmi-1068-scalarization-v12/ScalarLawsV12.lean | fc6a14981c710647135e2354616db6170fa7c5e483c61ca3a0e9f58de8887f1e |
| research/gmi-1068-scalarization-v12/FiniteSumsV12.lean | efaad21772778c70ab2bfea3aedcf26841f9895da104111ba299e9edd7117638 |
