# Architecture: attainable designs and conditional selection

Status: construction and impossibility theorems. AX1–AX4 plus behavior alone
do not identify a unique architecture. They support a precise space of
realizations and cost-dependent selection once a substrate is declared.

## ARCH1: behavioral axioms do not identify internal architecture

Call two realizations equivalent when all declared admissible continuation
experiments induce the same protected trace law. REP1/REAL1/REAL2 construct
table, symbolic-rule, circuit and recurrent-neural implementations of the same
finite behavior. Their internal state layouts, operations and graphs differ.
All satisfy AX1–AX4 under their declared faithful interpretation and actual
accounting. Therefore no proposition invariant under this behavioral
equivalence can distinguish these internal architectures.

**Proof by refactoring.** Start from any deterministic implementation.
Insert a second identity register between its update and protected output,
or split one transition into internal stages behind the same external clock
boundary. The protected output/state kernel is unchanged after hiding those
stages. Its architecture graph changes. CMP1 preserves its interface law
in every compatible context. Thus behavior and the core axioms admit both
architectures, contradicting any purported uniquely forced graph. Actual
resource changes remain visible to AX4; refactoring does not preserve costs
unless their equality is separately established. If timing is a protected
coordinate, the implementation must preserve that timing too, or equivalence
is not claimed. Pure renaming always supplies a weaker syntactic ambiguity.

The minimal residual machine is canonical up to isomorphism within its
deterministic interface model. This does not make its table interpreter,
Boolean implementation, neural block or memory layout canonical. No unique
neural substrate, learning rule or physical mechanism follows from REP1.
Useful extra selectors include a fixed instruction set, precision/noise model,
wiring/locality restrictions, workload, development accessibility and resources.

## ARCH2: the full jointly attainable set

Fix an admitted implementation/development family \(\mathcal I\), environments
and obligations. For each executable candidate \(i\), let \(\ell(i)\)
be its declared protected loss/risk profile and \(c(i)\in[0,\infty]^k\)
its fully charged resource profile. Coordinate definitions specify whether
they are pathwise bounds, expectations, quantiles or another fixed statistic;
these notions cannot be exchanged during an optimization argument. Include
acquisition, synthesis, verification and deployment within the chosen boundary.
Define
\[
\mathcal A=\{(\ell(i),c(i)):i\in\mathcal I\},\qquad
\mathcal C_\varepsilon
=\{c(i):i\in\mathcal I,\ \ell(i)\le\varepsilon\}.
\]
All coordinates in one tuple must come from the same candidate and resource
schedule. For alternatives costing \((1,3)\) and \((3,1)\), coordinatewise
infima \((1,1)\) are not an attainable joint design. Independent names for
subtasks likewise do not make their outcome relation or resource sets products.

Given a declared scalar objective \(\phi\), architecture selection is
\(\inf_{c\in\mathcal C_\varepsilon}\phi(c)\), together with an attaining
implementation or an explicit approximation statement. Increasing coordinate
preferences permit Pareto pruning in a finite candidate set. For an infinite
set this requires each candidate to be dominated by a retained Pareto candidate;
the costs \(1+1/n\) have no Pareto minimum. Even when Pareto pruning is valid,
not every Pareto point is obtained by a positive weighted sum. For
\((0,2),(1,1.1),(2,0)\),
all points are nondominated. The middle point could minimize
\(w_1c_1+w_2c_2\), \(w_1,w_2>0\), only if
\(w_1\le0.9w_2\) and \(w_1\ge1.1w_2\), an impossibility.

## ARCH3: optimizer existence is a separate theorem

**Finite theorem.** A nonempty finite feasible candidate family with finite
decidable objective values has an attained computable minimizer: evaluate
each candidate's objective and retain the smallest, breaking ties by a fixed
index. Enumeration and evaluation costs belong in an end-to-end comparison.
Finite candidates with merely computable-real scores may require approximation
and a tolerance because equality of computable reals need not be decidable.

**Compact theorem.** Suppose the feasible parameter set \(F\) is nonempty
compact in a metric space, and the full scalar objective \(J:F\to\mathbb R\)
is lower semicontinuous. Then a minimizer exists. **Proof:** each point has an
open neighborhood where \(J\) exceeds its value minus one. A finite subcover
gives a finite global lower bound. Choose a minimizing sequence; compactness
gives a convergent subsequence with limit \(i_*\in F\).
Lower semicontinuity gives \(J(i_*)\le\liminf J(i_n)=\inf_FJ\), while
the reverse inequality follows from the definition of infimum. This is an
existence argument, not an executable synthesis method. Closed feasibility,
compact parametrization and full-cost lower semicontinuity are extra premises.

**Counterexample and repair.** Let candidate \(i_n\) have the same exact
adequate behavior and scalar cost \(1+1/n\). The infimum is 1 and no
candidate attains it. Every finite search can be improved. Add an actual
candidate costing 1 to attain the bound, or require a positive tolerance
\(\eta\) and choose \(n>1/\eta\) for an \(\eta\)-optimal result.
Naming an optimum without an existence condition would be a false theorem.

## ARCH4: an executable conditional architecture synthesis bridge

Assume SD1's bounded, resettable exact-learning premises. Acquire the minimal
finite transducer; compile it with REAL1/REAL2 into a finite declared family.
Attach each compiler's semantics proof and its actual measured or proven
resource profile. CMP1 transports the common protected behavior through
compatible contexts, and AX4 retains all charges. Under ARCH3's finite-score
premises, enumerate and select a minimum for the registered workload/objective.
Every stage has a construction: observations → table → residual state →
executable candidates → verified composition → charged selection.

This bridge realizes an architecture from acquired behavior; it does not
promise useful cost or identify an unknown general environment without SD1's
premises. Replacing the finite compiler family by a grammar of programs
requires sound compositional rules and an effective search restriction.
Unrestricted program adequacy or termination contains the halting problem,
so enumeration alone does not provide a total exact optimizing algorithm.

## ARCH5: falsifiable architecture predictions and the novelty boundary

For two equally adequate candidates with paid one-off costs \(A_i,A_j\),
per-use costs \(r_i,r_j\) and known horizon \(H\), the full-cost preference
is determined by \(A_i-A_j+H(r_i-r_j)\). If \(A_i>A_j\) and \(r_i<r_j\),
the switch occurs at \(H_*=(A_i-A_j)/(r_j-r_i)\). This follows directly by
subtracting the two total costs. A registered workload and accounting model
make the inequality testable; observed costs can falsify that instantiated
model. A fit after seeing the outcome is not an independent prediction.

Tables may win small finite tasks; compiled circuits may win repeated tasks;
Bayesian state may serve a supplied latent model. These are possibilities,
not unconditional rankings. A theorem of a new architecture must add an
explicit new construction, a matched comparator family, an obligation and a
proved advantage under stated conditions. Empirical superiority additionally
needs held-out measurements including development and execution costs.

REP1, predictive state, finite neural simulation and finite optimization are
established mechanisms. Their GMI assembly does not by itself establish a
historically new machine or general intelligence. The precise achievement is
the conditional construction ARCH4 and the impossibility of an architecture
choice from unspecified realization/cost assumptions. Related bounded-agent
selection is developed in
[Russell, Rationality and Intelligence](https://people.eecs.berkeley.edu/~russell/papers/aij-cnt.pdf);
GMI's declarations must retain the same dependence on environment and machine.
