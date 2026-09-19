# R3 — contextual attainability as the master derived carrier

For start configuration (x) and context (kappa), let (mathrm{Hist}_S(x)) be the substrate-admitted finite histories beginning at (x). R2 permits a partial evaluator

[

u_kappa : mathrm{Hist}(C_S) ightharpoonup W_kappa.
]

The contextual attainability set is therefore the image on the evaluator's defined domain:

[
A_kappa(x)
=
{,win W_kappa mid
exists hinmathrm{Hist}_S(x), 
u_kappa(h)=w,}.
]

Undefined evaluations contribute no value. Distinct histories may map to the same value, so (A_kappa(x)) is a value image, not a history set.

For a declared restriction (B), let (mathrm{Hist}^{B}_S(x)subseteqmathrm{Hist}_S(x)) and define (A_kappa^B(x)) by the same image construction.

## R3-1 conditional monotonicity

For any (H_1subseteq H_2),

[

u_kappa(H_1capmathrm{dom},
u_kappa)
subseteq

u_kappa(H_2capmathrm{dom},
u_kappa).
]

Thus attainability is monotone under actual inclusion of admissible histories. A numeric quantity called “budget” does not by itself establish this premise: the budget family must be registered so that larger budget means a nested history set.

## R3-2 order and frontier

The context supplies a preorder (le_kappa). Its strict part is

[
u <_kappa v
quadLongleftrightarrowquad
ule_kappa v land 
eg(vle_kappa u).
]

A finite frontier is the set of attainable values for which no strictly better attainable value exists. Preorder-equivalent values are not artificially ordered.

No existence of maximal elements is asserted for arbitrary infinite preorders without additional conditions such as compactness, chain conditions, well-foundedness, or an appropriate maximality theorem.

## R3-3 what is and is not derived from attainability

(A_kappa(x)) is a master **carrier relative to the rest of the declared context structure**. The bare set alone does not determine all GMI notions.

- **Capability.** Given a context-declared success region (Gsubseteq W_kappa), capability is (A_kappa(x)cap G
eqarnothing).
- **Impossibility.** Relative to a declared target (Tsubseteq W_kappa), impossibility is (A_kappa(x)cap T=arnothing).
- **Frontier / preference shorthand.** These require the inherited context preorder; the bare carrier does not encode which direction is better.
- **Resource response.** This requires a declared resource coordinate/projection (ho:W_kappa	o R), or an equivalent resource-bearing context. It is not recoverable from an unlabelled set of values.
- **Barrier witness.** A baseline attainable set cannot identify a unique causal barrier. A registered one-step enabling witness is defined only relative to a declared admissibility-relaxation/intervention family (Delta): a relaxation (delta) is enabling when the relaxed attainable set intersects the target. Minimal or causal barrier claims need an additional order/cost/causal semantics on (Delta).
- **Context-family regime change.** Comparing frontiers or selected optima across (kappa_	heta) requires either a common result space/order or an explicit transport between result spaces. The finite R3 fixture proves an argmax-regime switch, including its tie boundary. It does **not** promote that switch to a thermodynamic, statistical-mechanical, or nonanalytic “phase transition” without further structure.

These qualifications preserve the candidate two-factor foundation (G_S=(C_S,K)): the extra ingredients above belong to the declared process/context presentation or to explicitly registered comparison/intervention structure; they are not silently manufactured from (A_kappa(x)).

## R3-4 retirement of legacy foundation symbols

(Gamma), (mathrm{Pref}), and (mathrm{SEL}) may remain conservative abbreviations where an old theorem explicitly supplies the required target/order/projection/selector structure. They are removed from the universal primitive list.

No historical theorem transports automatically. Each theorem must be checked for:
1. its original quantifiers;
2. whether its evaluator was total or partial;
3. whether it reasoned over histories or contextual values;
4. which order/resource/success structure it assumed;
5. whether it compared distinct contexts through a legitimate common space or transport.

## R3-5 registered finite hostile results

The executable fixture contains:
- six histories;
- one evaluator-undefined history;
- two distinct histories with the same contextual value;
- four unique attainable contextual values;
- a nested two-history budget restriction;
- a three-point finite Pareto frontier;
- a capability threshold that is impossible under the restricted set and attainable under the full set;
- three distinct one-step enabling witnesses, demonstrating non-uniqueness of a “barrier” absent further minimality semantics;
- a scalar-context family with a switch at (lambda=3/2), where the boundary is a tie rather than a unique winner.

Eight planted hostile interpretations are rejected, and the optimized Python route is required to execute the same fail-closed checks as the normal route.

## Claim ceiling

GRAND_GMI_V2_R3_CONTEXTUAL_ATTAINABILITY_MASTER_CARRIER_AT_REGISTERED_SCOPE
