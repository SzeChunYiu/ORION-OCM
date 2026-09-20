# V13 freeze: optional parallelism, symmetry and formal-law adjudication
Control plane:#1068; historical programme:#833.
Parent implementation:8f474c7b35d8f07ebdc8b24e07c3df163fc0fda9, V12
PR#1108 pending at freeze time. Preserve ancestry and merge its successful
main before publishing this result. Freeze precedes outcome-bearing code.

Eligible original requirements, exact titles:
- GMI2-R1-004: adjudicate parallel composition.
- GMI2-R1-005: test symmetry necessity.
- GMI2-R1-010: mechanize universal process claims.

Original R1 freeze result4 asks for valid process models without universal
enrichments; result7 specifies universal category-law consequences in Lean.
The third title does not license claiming that all minimality, physical
adequacy or optional-enrichment claims have already been mechanized.

## Primary assimilation and ownership
Riehl, Category Theory in Context, appendixE.2:
https://emilyriehl.github.io/files/context.pdf.
Baez's Eckmann–Hilton account:
https://math.ucr.edu/home/baez/week258.html.
The category, monoidal, braiding and interchange arguments are parent-owned.
The following symbolic countermodels were derived before this freeze during
primary assimilation. Their validation is not an unseen empirical discovery.

## M1: genuine obstruction to any tensor on an unchanged process category
Use the one-object category with actual bit functions id, reset0, reset1.
Sequential composition executes the first then the second function.
Prove the three maps are distinct, closed, associative, and have unit id.
Prove id is the only invertible arrow. reset0 followed by reset1 differs
from reset1 followed by reset0, so composition is noncommutative.

Every monoidal structure on this unchanged one-object category has its unit
object fixed. Its invertible left/right unitors must therefore both be id.
Naturality yields a common unit for arrow tensor and sequential composition.
Bifunctoriality supplies interchange. Prove the general Eckmann–Hilton
consequence: two unital operations with common unit and interchange coincide
and commute. This contradicts the actual reset-map compositions.

Do not merely omit a tensor field, test one proposed tensor or assume strict
unitors without deriving them. Prove the necessary conditions for a general
monoidal structure, including possibly weak unitors, before invoking the
obstruction. Associator/pentagon conditions may be unused because these
necessary lower-level conditions already contradict noncommutativity.
Adding objects or arrows can allow a monoidal enlargement; that is different.

## M2: lawful monoidal process model with no braiding for its tensor
Use the same noncommutative three-element monoid as objects of a discrete
category, tensor given by monoid multiplication. Prove category and strict
monoidal laws; a braiding requires an arrow a*b→b*a, absent for the reset pair.

Also construct its product with the one-object C2 category: each object has
two actual loop arrows, composed by XOR; tensor arrows by XOR and tensor
objects by the noncommutative monoid product. This supplies nonidentity
processes, lawful functoriality, associativity and units, while the obstructed
cross-object hom-set remains empty. Prove the object-level obstruction.
No claim excludes every alternative tensor on the underlying category.

## M3: original formal-law adjudication
Independently replay the exact V11 path/quotient proof registrations and
inspect the original R1 freeze result7. V11 already constructs arbitrary
typed paths and congruence quotients, and presents every lawful small
category via the kernel of its path evaluator. This is the universal
category-law component of R1-010. Keep all other R1 requirements open.
Bind original IDs, titles, freezes, actual theorem types and source hashes.

## Exact calibration and falsifiers
Implement bit-function composition independently from the three-label table.
Exhaust all three-input associativity/unit/inverse/noncommutativity checks.
Enumerate all19683 binary operations on the three-arrow carrier; exactly81
have the registered common unit. Test interchange on every necessary tuple,
and exhibit a real failed equation for every normalized candidate.
Expected result:no coherent tensor. These counts are symbolic predictions.

No-alarm control:the C2 one-object category admits XOR tensor and valid units.
Exercise nonidentity/invalid unitors explicitly; do not conflate one-sided
inverse with a true isomorphism. Independently verify the discrete and C2
product category's typed composition and monoidal laws. Count actual
equations and exhibit the precise empty hom-set obstructing braiding.
Check label permutations, identities, empty/invalid carriers, malformed
tables, bool/float aliases and corrupted composition/tensor/unit witnesses.
Hostile controls must reject constant pass verdicts, selected-tensor-only
reasoning, missing interchange, erased noncommutativity and domain collapse.

## Evidence, proof scope and closure
Pinned Lean4.19.0, explicit exact statement types and axiom inspection.
Mechanize the general interchange consequence and actual finite obstruction
where feasible; identify any general monoidal extraction or concrete model
construction left paper-only. No assuming the theorem under another name.
Replay actual V11 kernel evidence for R1-010, not just declaration existence.
Independent executables and controls run normal/optimized with identical
receipts. Missing inputs/tooling remain distinct from invalid evidence.
Modular docs/code under200lines each; raw snapshots may be longer.

Preserve every original record except the three eligible new dispositions.
Starting V12 has12closed requirements,210unresolved. Full success yields
15closed (8governance,7scientific),207unresolved; R0 alone remains EARNED.
R1 and overall GMI remain OPEN. A new exact successor contract must prevent
scope, witness, status, source-binding and unrelated-closure drift.
Merge only after all exact-head CI succeeds, using a merge commit.
No absolute primitive minimality, stochasticity elimination, higher-cell
elimination, architecture recovery, empirical novelty or complete GMI claim.
