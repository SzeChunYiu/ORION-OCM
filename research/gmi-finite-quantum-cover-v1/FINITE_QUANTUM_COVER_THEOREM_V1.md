# Finite relational quantum coverage — FQC-1–4

Status: constructive corollary of established quantum and real-algebraic parents.
Date: 2026-09-13. Read [parent subtraction and costs](PARENTS_AND_COSTS_V1.md).

## 1. Registered protocol class

Fix finite nonempty sets X,Y,A and a nonempty promise D⊆X×Y. Each promised
pair has an explicitly supplied nonempty acceptable set Γ(x,y)⊆A.
Remove unused sender inputs if desired; write n=|X|≥1.

Alice receives x, Bob receives y. Alice sends exactly one noiseless
d-dimensional quantum system, with positive integer d. There is no
pre-shared entanglement, input-dependent side channel, communication of y to
Alice, abort or postselection. All promised pairs must succeed with probability
one. Local preparation, private randomness, ancillas and measurements are
arbitrary finite-dimensional quantum operations. Only transmitted dimension
is optimized. Optional input-independent shared classical randomness is allowed
with the same fixed transmitted dimension d on every seed. It does not improve
feasibility: for each promised pair the conditional failure probability is zero
for almost every seed. Finitely many such probability-one seed events have a
probability-one intersection. Fix a seed in that intersection, retaining exact
success for every pair. This derandomizes feasibility, not response distributions
or variable-length expected resource costs. Independently averaging Alice's and
Bob's objects would instead lose their correlation and is not the argument.
This is the ideal interface of the existing quantum theorem §4.4.

Local work and storage do not become free in other cost coordinates merely
because this dimension optimization leaves them unconstrained.
The input is the finite relation, not a program whose termination defines Γ.
An empty promise has the separately decidable trivial solution d=1; a promised
empty acceptable set is infeasible. Neither is admitted to the main statement.

## 2. FQC-1 — complete protocol coverage and quadratic normal form

After fixing any shared seed as above, every admitted protocol induces states
ρ_x≥0, Trρ_x=1, and effects E_a^y≥0
with Σ_a E_a^y=I. Private ancillas and randomness are absorbed into the transmitted
density state and Bob's POVM. These objects depend only on their owner's input.
Zero error is equivalent to Tr(ρ_x E_a^y)=0 whenever a∉Γ(x,y).

For positive operators this zero trace implies suppρ_x⊆ker E_a^y:
Tr(ρE)=||E^(1/2)ρ^(1/2)||_HS², so the product vanishes.
Choose any unit vector v_x in suppρ_x. It satisfies every forbidden-output
constraint at every compatible y simultaneously. Thus pure transmitted states
suffice for feasibility and minimum dimension for these exact relational tasks.
This preserves adequacy, not the complete response distribution or other costs.

Factor each effect E_a^y=B_a^y(B_a^y)† with a square d×d factor. Hence the entire
admitted protocol class is feasibility-equivalent to

    v_x†v_x=1                       for every x,
    Σ_a B_a^y(B_a^y)†=I_d            for every y,
    (B_a^y)†v_x=0                   for each forbidden promised (x,y,a).

Conversely these constraints give normalized pure states and a complete POVM.
The forbidden probabilities are ||(B_a^y)†v_x||²=0, and completeness makes the
total outcome probability one. Therefore all outcomes are acceptable.

Split every complex variable into real and imaginary parts. Every equation
above is quadratic with integer coefficients. There are
N_d=2dn+2d²|Y||A| real scalar variables before optional simplification.
For the matrix equation it suffices to impose the d real diagonal equations
and real/imaginary parts of the upper-triangular off-diagonal equations.
Each forbidden vector gives 2d real equations. The resulting finite system
covers all admitted mixed states and general POVMs; it is not a finite sample
of quantum devices, a convex program, or a restriction to real quantum theory.

## 3. FQC-2 — an effective attained dimension optimum

For each fixed d, real-closed-field decision and algebraic sample-point
construction decide the polynomial system and return a real-algebraic solution
when it is feasible. This is the established parent mechanism, not a new
quantifier-elimination algorithm. Integer coefficients make the real-algebraic
field sufficient even if the original feasible device used transcendental entries.

There is always a feasible protocol with d=n. Send basis state |x⟩. For each y,
choose an action a(x,y)∈Γ(x,y) on promised pairs and any action otherwise.
Bob's effects are diagonal projectors onto the x values assigned each action.
They form a complete measurement and satisfy every promised constraint.

Thus the effective finite search

    for d=1,...,n:
        decide the complete FQC-1 system;
        return the first feasible d and an algebraic witness

terminates, and its returned d is the exact minimum over the entire registered
protocol class. A hypothetical smaller-dimensional protocol would satisfy an
earlier system, contradicting its exact rejection. The witness attains the
minimum. This uses the explicit finite upper bound, not an undecidable search
over arbitrary unbounded dimensions, histories, gate programs or physical laws.

The result yields q_min=ceil(log2 d_min) if transmitted systems are padded to
qubit registers with unused subspace. A d-dimensional protocol embeds into any
larger dimension by extending states with zero and assigning the orthogonal
complement to one action. The logical d value and padded qubit dimension differ.

No efficient complexity guarantee follows. The executable evidence in this
unit verifies supplied rational witnesses and exact lower certificates. It
does not execute a general quantifier eliminator or claim that its finite
census is that algorithm.

## 4. FQC-3 — constructive legal operations in the ideal interface

For each y define V_y:C^d→C^A⊗C^d by

    V_y ψ = Σ_a |a⟩ ⊗ (B_a^y)†ψ.

Then V_y†V_y=Σ_a B_a^y(B_a^y)†=I. Measuring the first output register in the
standard basis gives exactly the required POVM probabilities. This is the
Naimark-isometry construction. It accounts for an outcome register of dimension
|A| and a receiver composite space of dimension d|A|.

A finite algebraic isometry extends to an algebraic unitary: process the standard
basis in fixed order, subtract projections onto columns already retained, omit
zero residuals, and normalize each nonzero residual. Algebraic arithmetic,
zero tests and positive square roots are effective. Finite dimension guarantees
completion. Applying the same construction to each unit vector v_x supplies
an algebraic unitary with that vector as its first column. A controlled choice
of that preparation for x, the transmitted system, V_y and the outcome readout
therefore provide legal operations in this ideal quantum interface.

An exact unitary over algebraic numbers need not have a finite exact circuit
over a selected finite gate alphabet. No gate synthesis, hardware precision,
noise robustness, timing, energy or calibration theorem is implied.
The isometry's ancillary dimension is a construction cost, not a minimal
receiver-memory theorem. Classical descriptions of the x/y-controlled maps
and their selection interfaces also require resources.

## 5. FQC-4 — decisive relational census and matched parents

Take |X|=|A|=3, one receiver context, and arbitrary nonempty Γ(x).
There are 7³=343 tasks. Their exact unassisted quantum dimensions are:

- 169 tasks with a common acceptable action: d_min=1.
- 6 permutations of the three distinct singleton sets: d_min=3.
- The other 168 tasks: d_min=2.

For d=1 Bob's output distribution is independent of x. Its nonempty support
must lie in the intersection of all Γ(x), proving the first criterion.
Three distinct forced outputs require three mutually orthogonal nonzero
state supports, proving the second lower bound.
Otherwise any empty common intersection requires d≥2. A two-action hitting
set exists: if every pair of the three actions missed some Γ(x), the three
singleton sets would all have to occur. The exceptional six tasks are already
removed. Encoding one chosen acceptable hitting-set action in two orthogonal
states attains d=2. Inclusion–exclusion counts the first class as
3·4³−3·2³+1=169. Hence the census is analytically complete.

The three pairwise-intersecting sets {0,1},{0,2},{1,2} are a load-bearing
d_min=2 case: a graph that only marks disjoint pairs incorrectly permits d=1.
The matched classical encoder/decoder search independently finds all 343
optima. This census claims no quantum advantage.

For a nonclassical positive control, the archived augmented Yu–Oh edge-promise
witness (the 13-ray graph plus one universal apex: 14 rays, 37 edges) has classical
alphabet 5 and exact quantum dimension 4. An independent graph
color search, four-clique bound, full Born checks and compiled isometries verify
that inherited separation. Two-bit random access supplies a timing-of-information
control: d_min=4 when only Bob knows the requested index; d=2 is possible if
Alice also receives it. These are different declared interfaces.

## 6. Remaining obligations

This discharges complete dimension coverage, attainment and effective
construction for one infinite continuous protocol class. It narrows Q4 and
the ideal-operation part of Q9; arbitrary physical universes and hardware
claims remain open. MSC property claims still require complete optimal fibers.
Q2 representation/synthesis/platform costs, Q3 lifetime reuse, Q1 model learning
and Q10 changed query interfaces are not closed by this result.
