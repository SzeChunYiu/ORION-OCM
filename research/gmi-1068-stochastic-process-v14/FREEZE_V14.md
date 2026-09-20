# V14 freeze: deterministic, stochastic and nondeterministic process instances
Control plane: #1068; historical evidence programme: #833.
Parent: 5c8db6246126d34894a91df70f6628793c9f46d2, PR #1109 pending.
Preserve this preregistration ancestry; merge successful V13 main before publication.
Only eligible original atom: GMI2-R1-008,
"formalize stochastic/nondeterministic optional structure" (FORMAL_OR_FINITE).
Original R1 freeze result4 asks valid process models, not all measure theory.

## Assimilated parents and pre-freeze knowledge
Fritz, Examples2.5–2.6,3.3,10.3:
https://arxiv.org/html/1908.07021v8
Finite stochastic matrices, total relations and deterministic inclusions are
classical parents. The following model and counterexamples were derived
symbolically during planning; their replay is not unseen empirical novelty.
Installed Std4.19 has executable Std.Internal.Rat but no complete rational
algebra-law library. Local mathlib commit
4bbdccd9c5f862bf90ff12f0a9e2c8be032b9a84 targets Lean4.14.
Do not pretend it is a ready Lean4.19 dependency.

## N1: arbitrary finite constructions
Objects are finite state sets, including empty ones.
A stochastic arrow n→m is an n-by-m nonnegative matrix with row sums one.
Composition executes the first arrow and then the second, by matrix product.
Prove closure, identities and associativity from primitive scalar laws.
A nondeterministic arrow is a total relation, each source having a nonempty
set of targets. Composition is existential relational composition.
Prove closure, identities and associativity for arbitrary state types.
Construct faithful deterministic Dirac and singleton embeddings, preserving
identity and composition. Do not assume these conclusions as scalar axioms.

Prove support of composite equals relational composite of supports under
explicit positivity/no-cancellation/no-zero-divisor assumptions sufficient
for finite nonnegative sums and products. Derive finite-sum positivity.
Support is total and preserves identities/composition, but is not faithful.
State exactly which arbitrary rational/real specializations remain paper-only.

## N2: actual closed rational witness
Use the seven arrows I,F,Kp on Bool, with F bit flip and Kp constant rows.
p is probability of true and ranges over {0,1/3,1/2,2/3,1}.
First-then-second: Kp;Kq=Kq, Kp;F=K(1-p), F;Kp=Kp, F;F=I.
Use actual Std.Internal.Rat entries, not unconstrained probability labels.
Kernel-check matrix normalization, actual composition, arrow category laws
and faithful matrix interpretation by exhaustive finite proof.
The four deterministic arrows are I,F,K0,K1.
K(1/3) and K(2/3) have identical full support and different event probabilities.
Prove the latter distinction directly, not by label inequality alone.

## N3: exact independent executable calibration
Use Python Fraction, explicit source/target dimensions, and strict types.
For dimensions 0,1,2, enumerate all stochastic kernels whose entries lie in
{0,1/3,1/2,2/3,1} and sum to one. Enumerate all total relations on the same
dimensions and all deterministic maps. Counts are observed and bound later.
Check every composable pair, every composable triple, identities, support
composition, faithful deterministic embeddings and support probability loss.
Composites are allowed outside the input grid: it is NOT a closed category.
Independent oracle uses its own representation/implementation, no production
composition or normalization helpers. The seven-arrow witness is closed.

Preserve empty source/codomain distinctions: unique empty-domain arrows;
no nonempty-source normalized kernel or total relation into empty codomain.
Malformed dimensions, bool/float aliases, negative/nonnormalized rows, empty
relation rows, mismatched composition dimensions and invalid map targets
must reject explicitly. Tiny positive rational support must never round away.
Test reversed composition using a concrete asymmetric pair.
Demonstrate failure of signed cancellation and modular zero-divisors if
the support theorem's positivity assumptions are removed.

Uniformizing relations is not functorial: one source chooses a or b;
a leads only to x, b leads to y or z. Two-step probabilities are
(1/2,1/4,1/4), while uniformizing the composite gives (1/3,1/3,1/3).
Do not claim that the core assigns a canonical stochastic law.

## Proof and evidence discipline
Pin Lean4.19.0, exact typed theorem registrations, audited axioms and sources.
Separate generic scalar-law proofs, concrete rational kernel proofs and
paper-only standard algebra instantiation. Report any missing component.
Source-valid proof mutants must compile source and fail typed audit.
Every diagnostic must accept actual valid data and reject actual hostile data.
Normal and optimized integrated replays must produce identical receipts.
Missing inputs/tools is CANNOT_CHECK, distinct from checked-invalid.
Bind original checklist/title, R1 freeze and prior V13 scope snapshot.
Modular docs and code under200lines; raw receipts/snapshots may be longer.
A new exact successor contract rejects unrelated closure, scope laundering,
status drift, swapped witnesses, and coupled receipt/manifest edits.

V13 has15closed atoms (8governance,7scientific),207unresolved.
Full success closes only R1-008:16closed,206unresolved.
R1 and overall programme remain OPEN; R0 alone remains whole-EARNED.
This establishes optional process instances, not universal architecture
recovery, probability elimination, primitive minimality or complete GMI.
No empirical novelty claim follows from reconstructing classical parents.
Commit, push and merge this result after all exact-head CI succeeds.
