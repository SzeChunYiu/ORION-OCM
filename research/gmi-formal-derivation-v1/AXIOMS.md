# An economical operational core

Status: proposed classical discrete-time specialization of the existing Grand
GMI declaration, with analytic consistency and indispensable-data witnesses.
This does not replace the substrate-general master with a classical ontology.
The base is `c0344314805b60e7c1c1aec2f5635ee98cfb2951`.

## Primitive signature

Four packages suffice to state the theorems in this supplement:

1. **Process and access** \(\mathsf P\): standard Borel observation, action and
   configuration spaces; legal histories; initial laws; controlled probability
   kernels; an observation map; and admitted interventions/continuations.
2. **Obligation** \(\mathsf O\): measurable protected trace coordinates,
   admissible outcome relations or losses, environments, and error tolerances.
3. **Realization and development** \(\mathsf R\): admitted executable machines,
   initial configurations, legal updates and a declared implementation map to
   process kernels. A machine is allowed to ignore all experience.
4. **Accounting** \(\mathsf C\): resources on actual execution/development
   traces, with explicit aggregation, units and any declared scalarization.

This groups, without deleting, the master's
\((\mathbf P,\mathcal B,\mathcal E,\Omega,\Theta,\rho,\mathcal D,\varepsilon)\).
\(\mathsf P\) groups \(\mathbf P,\mathcal B,\Theta\);
\(\mathsf O\) groups \(\mathcal E,\Omega,\varepsilon\);
\(\mathsf R\) specializes the realization class and \(\mathcal D\);
\(\mathsf C\) specializes \(\rho\). A prior over environments is additional.

## Admissibility axioms

**AX1 (causal execution).** Kernels are measurable, nonnegative and normalized.
At step \(t\), a policy uses only its declared observed history and private
randomness available before that step's outcome. The joint model includes
shared randomness and hidden environment state; it does not assume independent
components or samples. Instantaneous cyclic equations need a separate existence
and uniqueness model; they are not disguised as a sequential kernel.

**AX2 (fixed interpretation).** The observation boundary, protected outcome
interpretation and loss/verification semantics are fixed for a theorem instance.
An adaptive task change is an explicit versioned process transition with its own
contract. A machine's internal score is a protected success criterion only when
the external obligation actually identifies the two.

**AX3 (realization fidelity).** An admitted realization has a specified induced
kernel on the declared interface. Any claimed simulation must preserve the
particular protected law it claims to preserve. Legal development is itself
nonanticipating execution, and its initial information must be declared.
No existence of an adequate, efficient or improving realization is assumed.

**AX4 (resource closure).** Every event inside the declared accounting boundary
is assigned its resource charge. Composition uses the specified aggregation:
work adds, peak memory is a maximum over simultaneous live allocations, and
latency follows the declared schedule. External services retain their resource
coordinates or are explicitly outside the scope; moving work cannot erase an
in-scope charge. Scalar optimization requires an explicit scalar objective.

AX2 and AX4 are rules for well-specified claims, not empirical laws asserting
that every actual instrument is honest. Matching a physical device to AX1/AX3,
verifier validity and measured accounting remain independently testable premises.

## AX-T1: consistency and absence of an assumed solution

Take the two-state parity machine with state \(s\in\{0,1\}\), input bit \(x\),
transition \(s'=s\mathbin\oplus x\), output \(s'\), and one unit of update work.
Finite discrete spaces and deterministic point-mass kernels satisfy AX1.
Fixed parity evaluation satisfies AX2; its transition table supplies AX3;
counting each update and one retained bit supplies AX4. Identity development
is legal. Thus the axioms have a nonempty model.

Now keep AX1–AX4 and require output of an independent fair hidden bit without
any observation of it. For any randomized output \(A\), independence gives
\(\Pr(A=X)=\sum_a\Pr(A=a)\Pr(X=a)=1/2\).
No machine achieves error below \(1/2\). The axioms therefore do not imply
universal adequacy, learning progress, or general intelligence. This is a
countermodel, not a failure to search hard enough. Revealing \(X\) is a
constructive repair that changes the access premise and permits exact success.

## AX-T2: indispensable distinctions, not a uniquely minimal axiom count

Each primitive package carries information the other three cannot recover:

| Omitted datum | Two completions with different answers |
|---|---|
| Process/access | Hidden fair bit versus observed bit: optimal error \(1/2\) versus 0. |
| Obligation | Same constant-output machines, loss for output 0 versus loss for output 1: the winner reverses. |
| Realization/development | Same task/kernel universe, only constant programs reachable versus copy-input reachable: feasibility changes. |
| Accounting | Two adequate implementations, charges \((1,2)\) versus \((2,1)\): the cheaper implementation reverses. |

**Proof.** For every row hold the other declared packages fixed and choose the
two indicated values of the omitted datum. Direct evaluation gives distinct
feasibility or optimization answers. A procedure receiving only the retained
data has the same input in both completions, hence cannot determine that answer.
This proves necessity of those distinctions for the specified questions. It
does not prove logical independence of four sentences: one can encode a tuple
as one object and conjoin all axioms into one sentence. A final absolute
"smallest number of primitives" is not invariant under reformulation.

## What is derived and what is added

Equality of complete protected future profiles defines an equivalence relation;
the quotient, its congruence and realization are proved in
[REPRESENTATION](REPRESENTATION.md). The quotient itself is not an axiom.
Multiple realizations, cost-dependent architecture selection and limits of
universal prediction have constructions/countermodels in
[REALIZATIONS](REALIZATIONS.md) and [ARCHITECTURE](ARCHITECTURE.md).

The learning theorems add bounded loss and an explicit sampling or feedback
contract. Gradient descent adds differentiable parameters and a Euclidean
movement penalty. Bayesian inference adds a prior and likelihood. Agency adds
an objective. None of these additions is hidden in AX1–AX4.

The previous A0–A8 mix constitutive declarations, definitions and consequences:
A0/A1/A5 supply explicit contracts; A2 is a derived quotient definition;
A3/A4 are distinctions realized by examples; A6/A7 define developmental roles;
A8 is supported by countermodels. This supplement separates those logical jobs
without changing the historical records.

## Parent relation

The process/agent/utility distinction follows the declared-agent framework in
[Russell, *Rationality and Intelligence*](https://people.eecs.berkeley.edu/~russell/papers/aij-cnt.pdf).
The present organization adds no theorem of universal intelligence to that
parent. All substantive results below name the extra premises doing the work.
