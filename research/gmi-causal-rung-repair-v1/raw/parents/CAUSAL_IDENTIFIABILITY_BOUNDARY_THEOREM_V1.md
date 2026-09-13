# Causal identifiability boundary — CAU-1–4

Status: **CORRECTED finite SCM scope; exact rational controls.**
This repairs PR570's missing support and model-class premises. The unchanged
original three files and their source hashes are in [the archive](raw/pr570-1277d0e8/SOURCE_BINDINGS_V1.json).

## Primary parents and disposition

[Pearl (2009), §§2–3](https://ftp.cs.ucla.edu/pub/stat_ser/r350.pdf)
supplies the mature SCM/intervention framework, back-door criterion and the
distinction between identification and estimation. His §3.3.2 also supplies
identification routes beyond a single back-door adjustment.
The faithfulness qualification is explicit in §2.1, footnote 1.
These mechanisms are adopted, not renamed as new discovery.

GG29/GG30 supply obligation-relative semantic relevance; LMT's complete-view
lemma supplies the indistinguishability step. A1/A2/A4 supply scoped access,
nonanticipation and charging, while corrected GAC-5 supplies founded composition.
The contribution here is an explicit finite interface and repaired controls,
not a new causal-identification calculus or a physical validation.

## 1. Register and observation interface

Declare finite-valued endogenous variables, a finite **acyclic** causal graph,
deterministic structural equations and a product law of independent root-noise
coordinates. A root coordinate may be shared by several equations; shared hidden
roots must appear in the expanded causal graph. Independence of root noises
alone does not establish causal sufficiency of the *observed* variables.
Acyclic evaluation gives a unique observational law and a unique law after
each surgical replacement of selected equations by constants.

Fix a nonempty admitted model class, observed variables and an observation
protocol. In W1 the protocol returns fresh iid observational (X,Y) draws.
The learner's initial information, private seed law, selection/stopping rules
and decoder are fixed across worlds and contain no hidden world label.
The complete decoder view includes observations, private randomness, actions,
stopping information and every admitted side channel. Restricting only a
marginal transcript is insufficient.

An intervention is mathematically defined by the SCM. Whether the interface
admits *performing* it is a separate operational constraint. A model-defined
query can be meaningful even when its corresponding experiment is unavailable.

## 2. CAU-1 — indistinguishable complete views obstruct identification

There exist two models with identical observational laws but different exact
interventional targets. For any fixed learner under the interface above,
its complete view has the same law in the two models: couple the common seed
and every observational reply, then induct through its actions and stopping.
Its terminal output therefore has a common law. If the two required answers
are distinct, their exact-success events are disjoint, and the two success
probabilities sum to at most one. In particular, worst-world success is at
most 1/2; nontermination does not help. The same conclusion applies to a
decoder of the whole infinite iid stream, whenever that decoder is measurable.

**W1.** U is a fair bit. World 0 has X=U,Y=U; world 1 has X=U,Y=X.
Only X,Y are observed. Both laws put mass 1/2 on (0,0) and (1,1).
Surgical do(X=1) gives P(Y=1)=1/2 and 1 respectively. No amount of
computation or additional draws from that identical stream separates them.
This statement does not prohibit identification in a smaller model class.

## 3. CAU-2 — population identification is a model-class property

For an ideal known compatible observational law P, define its nonempty fiber
C(P)={M in the declared class: P_M restricted to observed variables equals P}.
Require C(P)≠empty; no value is identified by vacuous constancy on an empty set.
A target theta is point-identified at P **iff** theta(M) is constant on C(P).
Necessity follows from indistinguishability; sufficiency defines a unique
set-theoretic population functional. It supplies neither a computable
procedure nor an exact finite-sample estimator.

An arbitrary observation distribution does **not** select one Markov
equivalence class of causal DAGs. Under a declared fully observed acyclic DAG
class, causal Markov and faithfulness assumptions, its exact conditional
independences determine the DAG Markov equivalence class. Without these
premises use the full compatible model fiber instead. For example,
independent fair X,U with Y=X xor U has the same observed independent law
as an empty graph with independent fair X,Y. The first structural graph has
an X→Y edge and is unfaithful, so the two graphs are not Markov equivalent.

Back-door adjustment and randomization below are sufficient routes, not
necessary ones. Other identifying restrictions or do-calculus derivations
may identify a query. Passive data determine GG29/GG30 intervention-dependent
quantities only when those quantities are invariant on the admitted fiber;
no blanket impossibility applies to every restricted class.

## 4. CAU-3 — supported adjustment and surgical randomization

Suppose observed Z meets the back-door criterion for (X,Y) in the declared
acyclic causal model: Z contains no descendant of X and d-separates every
back-door path in the full graph. Also require, for the target x,
P(X=x | Z=z)>0 for every z with P(Z=z)>0. Then
P(Y | do(X=x)) = sum_z P(Y | X=x,Z=z) P(Z=z).
The graphical criterion gives conditional exchangeability; consistency and
the stated support allow replacement by observational conditionals, and
summing over Z gives the formula. Zero-mass Z strata contribute zero;
positive-mass strata with zero treatment support are **not** imputed.

**W2, constructive supported revival.** U is fair, B is an independent bit
with P(B=1)=1/4. The observed root is Z=U; downstream equations are
X=Z xor B and Y=Z in world 0, or Y=X in world 1. Thus the graph has
Z→X,Z→Y in world 0: Z is the root itself, not a proxy child of a hidden parent.
Every (X,Z) stratum has positive mass. Direct observed-table adjustment gives
1/2 and 1 for do(X=1), matching surgical evaluation. In world 0 the unadjusted
P(Y=1 | X=1)=3/4 differs from 1/2.
These are new positive-support models, not a relabeling of W1.

The original W2 used X=Z=U. Its counterfactual strata are unobserved, and its
old helper evaluated structural equations instead of observed conditionals.
The corrected helper refuses this input: back-door graphical structure
without observational support did not identify that numerical formula.

**CAU-3b.** Replace only X's structural equation by an independent random
assignment with known law rho, retaining all other equations and noise laws.
For each x with rho(x)>0, the resulting P(Y | X=x) equals P(Y | do(X=x)).
Conditioning on an independent assignment retains the original noise law,
so the remaining equations are exactly the surgical model at x.
Zero-probability assignments have no such observational conditional.
Independence without the surgical/no-other-mechanism-change premise is insufficient.

**W3, supported bad-control witness.** X is fair; independent noises E,N
have probability 1/4 of one. Let Y=X xor E and Z=Y xor N.
All eight observed (X,Y,Z) cells have positive mass, and Z is a descendant.
At X=1 the Y=1 conditional is 9/10 when Z=1 and 1/2 when Z=0.
Each Z marginal is 1/2, so adjusting yields 7/10.
Surgical do(X=1) yields 3/4. This isolates an unsafe descendant adjustment
without an empty-stratum convention. The old deterministic W3's skipped
unsupported stratum is retained as a rejection control, not as this proof.
Some descendants may be harmless in special models; violation of the
criterion alone does not assert bias in every model.

## 5. CAU-4 — operations and composed claims

Charge the observation, preparation, intervention, identification computation
and other operations actually performed under the declared R contract.
An already admitted causal premise or sufficient adjustment set may identify
an effect without purchasing a new experiment. CAU-1 proves a two-world
information obstruction; it does not prove a positive probe cost in every
causal problem. A physical randomizer's surgical validity remains a premise
requiring its own warrant; no finite rational table certifies hardware.

A derived effect is a local guarantee. Its downstream use requires discharged
interfaces and the bases/well-founded dependencies or initialized invariant
of corrected GAC-5. Experimental access outside the declared interface changes
the operational problem, but does not erase the mathematical SCM query.

## 6. Executable scope

[causal_tables_v1.py](causal_tables_v1.py) builds the finite joint tables;
[test_causal_identifiability_v1.py](test_causal_identifiability_v1.py) derives
observational ratios, independently evaluates surgical targets and rejects
missing support. It also retains W1, private-decoder arithmetic and an
unfaithful-graph control. These are controls, not a general identification solver.

Finite-sample rates, arbitrary graph discovery, transport, learned causal
premises and physical causal validity remain separate obligations.
This unit is outside the grand replay capsule; its scoped repair receipt
does not change any grand checker or aggregate.
