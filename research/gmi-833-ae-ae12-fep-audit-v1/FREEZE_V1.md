# GMI #833 Section AE12 — free-energy / active-inference strongest-parent audit: prospective freeze v1

Source `main`: `0dcdec54fbece041ee2b7cd1f630469ad85d19d3`.

This freeze is committed **before** any executor, oracle, test, fixture,
receipt, theorem note or reconciliation file of this package exists in the
tree. The add-order of the blobs is the custody evidence; this commit
touches exactly one file.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE12 — Free-energy / active-inference strongest-parent audit`

1. `- [ ] Audit Free Energy Principle / active inference as a strongest-parent candidate for perception-learning-action unification.`
2. `- [ ] State exact assumptions needed for any claimed equivalence with Bayesian inference/predictive coding/control.`
3. `- [ ] Include published technical counterexamples/criticisms; do not inherit universal FEP claims uncritically.`
4. `- [ ] Construct finite discriminating tasks where GMI/CPC, rate-distortion control and an active-inference formulation differ.`
5. `- [ ] Compare predictive and control behavior prospectively.`
6. `- [ ] If GMI is reducible to an established FEP/active-inference formulation at a scope, mark parent sufficiency rather than novelty.`

**No neighboring row is earned here.** In particular this tranche does not
earn any AE1, AE2, AE3, AE4, AE5, AE6, AE7, AE8, AE9, AE10, AE11, AE13, AE14, AE15, AE16 or AE17 row of issue comment 5692689542, and does not earn any
row of the #833 issue body.

## Registered scope and frozen objects

A **registered dyadic agent world** is the tuple
`M = (S, O, A, P0, L, T, C, U)` with `S`, `O`, `A` finite ordered label sets;
`P0` a prior on `S`; `L(o | s)` a likelihood; `T(s' | s, a)` a transition
kernel; `C(o)` a preference distribution over outcomes; and `U : A x S -> Fraction`
a utility. Every entry of `P0`, `L`, `T` and `C` is a non-negative integer power
of `1/2` or exactly `0`, and every row sums to `1`; every entry of `U` is an
exact `Fraction`. This dyadic restriction is what makes every entropy, every
Kullback-Leibler divergence and every free energy below an exact rational number
of bits.

The **registered variational family** `Q` is the finite set of dyadic
distributions on `S` whose atoms are integer powers of `1/2` with a frozen
minimum atom `1/2^DMAX`, `DMAX = 4`. `Q_full` is that whole set; `Q_mf` is the
mean-field subfamily of product distributions over a frozen factorization
`S = S1 x S2`.

**Variational free energy** of `q in Q` given an observation `o` is
`F(q, o) = KL(q || P0) - E_q[log2 L(o | s)]`, in bits, exactly rational.
**Expected free energy** of a policy `pi` over a frozen horizon `H = 1` is
`G(pi) = risk(pi) + ambiguity(pi)` with `risk(pi) = KL(Ppi(o) || C)` and
`ambiguity(pi) = E_{s ~ Ppi}[H(L(. | s))]`, both in bits, exactly rational.

The **rate-distortion control** comparator is stated in **cardinality-constrained**
form: minimize expected distortion `E[d]` over all encoders `X -> {1..r}` and all
decoders `{1..r} -> A` at a frozen codebook cardinality `r`; this is log-free and
exactly rational.

The **prospective prediction register** is the file `PROSPECTIVE_REGISTER_V1.json`
of this package: a frozen ordered list of predicted orderings and predicted
disagreement sets. It is committed in the commit immediately following this freeze
and **before any executor, oracle, test or receipt blob of this package exists**, so
that its custody is provable from the git order exactly as this freeze's is. The
executor recomputes the SHA-256 of its canonical serialization, compares it with the
digest the register carries for itself, and refuses to emit a receipt on mismatch.
Each prediction is reported as `CONFIRMED` or `REFUTED` with its exact values; a
refuted prediction is reported as refuted and is never edited after the fact.

## Exact-arithmetic discipline

Every quantity entering a claim is an exact `fractions.Fraction` or a Python
`int`. No float appears in any claim, receipt, test assertion or hostile.
Registered worlds are designed so that each information-theoretic quantity
entering a claim is exactly rational: probabilities that must be logged are
restricted to non-negative integer powers of `1/2`, code lengths are
Kraft-compliant **integers**, rate constraints are stated as **codebook
cardinalities** rather than as real-valued mutual-information budgets, and
Landauer-type statements are carried in units of `k_B T ln 2` with an
**integer** coefficient. Where a comparison genuinely requires the logarithm
of a non-dyadic rational, it is decided only by certified exact rational
bounds: `log2(a/b) >= u/v` is decided by the integer comparison
`a^v >= 2^u * b^v`. Non-separating bounds are reported as `NOT_DECIDED`,
never as equality. Equality of a logarithmic quantity is claimed only in the
exactly dyadic case where the logarithm is an integer.

## Bound-vacuity discipline

Every bound this package states is emitted as a record carrying `kind`
(`upper` or `lower`), `bound_value`, `range_lo` and `range_hi` **derived from
the definition of the bounded quantity, never from the roster's observed
extremes, with the derivation stated in the record**, a `vacuous` flag
(`upper` is vacuous iff `bound_value >= range_hi`; `lower` is vacuous iff
`bound_value <= range_lo`), a separate `attained_by` witness, and a
`violated_by` witness: an object in an explicitly relaxed class that breaks
the bound. A bound with no `violated_by` witness is reported as
`UNFALSIFIED_BOUND` and is not used to close a row. Attainment is recorded
but is **not** accepted as evidence of non-vacuity.

## Required evidence and falsifiers

- **Row 1.** An exact perception audit: on every registered world, with `Q = Q_full`
  and a correctly specified generative model, the minimizer of `F(., o)` must equal
  the exact Bayes posterior `P0(s) L(o|s) / sum_s P0(s) L(o|s)`, checked as exact
  rational equality on every `(world, o)` pair, and the minimizing free energy must
  equal `-log2 P(o)` exactly. A **learning** audit and an **action** audit at the same
  scope. Where the equality holds the receipt emits a `PARENT_SUFFICIENT` terminal
  naming active inference as the owner; no novelty is claimed there.
- **Row 2.** Each assumption needed for the equivalence is named and proved
  **necessary** by an exact counterexample in which dropping it breaks the equality:
  (a) unrestricted `Q` — a world whose exact posterior is outside `Q_mf`, with the
  `Q_mf`-minimizer and its exact free-energy excess reported; (b) correct
  specification — a misspecified likelihood whose `F`-minimizer differs from the
  true posterior, with both distributions reported exactly; (c) the preference
  prior — a utility for which **no** dyadic `C` in the registered family makes the
  expected-free-energy-optimal action equal the expected-utility-optimal action, the
  non-existence proved by exhaustive enumeration over the registered `C` family.
- **Row 3.** A registered criticism table. Each entry carries author, year, venue,
  DOI, the criticism in one sentence, **and** a registered finite predicate that is
  evaluated exactly on a registered object, so that the criticism is machine-checked
  rather than cited. At least one entry must evaluate to a **failure** of a condition
  that a universal reading of the parent claim would require.
- **Row 4.** Finite discriminating tasks on which the CPC compound objective, the
  cardinality-constrained rate-distortion controller and the expected-free-energy
  controller select **different** actions or codebooks, with every objective value
  reported as an exact rational and the argmin ties broken by the frozen total order.
  A world on which all three agree must also be registered, so the discrimination is
  a contrast and not a construction artifact.
- **Row 5.** The prospective register above: the predicted orderings are frozen here
  with their digest, and the executor reports, per prediction, `CONFIRMED` or
  `REFUTED` together with the exact values. A refuted prediction is reported as
  refuted; it is never silently edited.
- **Row 6.** For every scope at which the audit found the parent sufficient, the
  receipt emits `PARENT_SUFFICIENT` with the owning parent and the exact equality
  that establishes it, and the manifest forbids the corresponding novelty claim.

## Two materially independent routes

Route A is `ae12_fep_audit_v1.py`. Route B is `independent_fep_oracle_v1.py`.
Route B contains no executable import of route A and recomputes every
claimed quantity by a materially different algorithm (closed-form posterior algebra and exhaustive enumeration over the registered dyadic variational family and the full policy set, against route A's incremental free-energy minimisation and expected-free-energy decomposition).
The test parses route B's AST and asserts the absence of any import of route A.

## Hostiles, null and no-alarm

Each hostile is a deliberately broken variant of a registered object. Two
assertions are required per hostile, in order: **potency** (the perturbed
quantity differs from the true quantity) and **detection** (the checker flags
the perturbed object). A hostile that cannot move the quantity it perturbs is
a package defect, not a pass. A null of randomized controls drawn from a
registered exact-rational sampler must fail the property the true witnesses
pass, at a reported rate, and the **no-alarm case must be asserted on the
known-clean registered witnesses**.

## Registered constants and prospective predictions

Every constant this package treats as registered — rosters, grids, thresholds,
integer description lengths, predicted orderings and predicted disagreement
sets — is carried in `PROSPECTIVE_REGISTER_V1.json` of this package. That file
is committed in the commit **immediately following this freeze** and before any
executor, oracle, test, fixture or receipt blob of this package exists, so its
custody is provable from the git order exactly as this freeze's is. The
executor recomputes the SHA-256 of the register's canonical serialization,
compares it with the digest the register carries for itself, and refuses to emit
a receipt on mismatch. No registered constant may be introduced or changed after
a result has been seen, and a prediction the evaluation refutes is reported as
`REFUTED` with its exact values rather than edited.

## Determinism

`RESULT_V1.json` is byte-identical under `python3 -I -B` and
`python3 -I -O -B`, and across CPython 3.8 and 3.12. Determinism is
structural: every collection is sorted before serialization, no set is
iterated into output, and serialization is a single
`json.dumps(..., sort_keys=True, indent=2)`. Tests use `unittest` assertion
**methods**, never the bare `assert` statement, so that no check is stripped
by `-O`.

## Claim ceiling

`GMI_833_AE12_FEP_ACTIVE_INFERENCE_PARENT_BOUNDARY_FIXED_ON_REGISTERED_FINITE_DYADIC_ROSTER`

## Forbidden promotions

`INTELLIGENCE_EQUALS_COMPRESSION`, `ALL_LEARNING_IS_COMPRESSION`, `MANIFOLD_HYPOTHESIS_UNIVERSAL`, `MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`, `WORLD_MODEL_ALWAYS_REQUIRED`, `FREE_ENERGY_PRINCIPLE_PROVED`, `THERMODYNAMIC_INTELLIGENCE_LAW`, `GENERAL_REASONING_REDUCED_TO_PREDICTION`, `COMPLETE_GMI`, `ARCHITECTURE_SELECTION_LAW`, `GMI_MORPHOLOGY_PREDICTION`, `ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER`, `REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT`, `FEP_UNIVERSAL_FOR_LIVING_SYSTEMS`, `ACTIVE_INFERENCE_EQUALS_BAYESIAN_INFERENCE_UNCONDITIONALLY`, `MARKOV_BLANKET_EXISTS_FOR_EVERY_SYSTEM`, `GMI_NOVEL_OVER_ACTIVE_INFERENCE`.

## Parent ownership

Free energy principle and active inference: Friston (2010), *The free-energy
principle: a unified brain theory?*, Nature Reviews Neuroscience 11:127-138,
doi:10.1038/nrn2787; Friston, FitzGerald, Rigoli, Schwartenbeck, Pezzulo (2017),
*Active Inference: A Process Theory*, Neural Computation 29(1):1-49,
doi:10.1162/NECO_a_00912; Parr, Pezzulo, Friston (2022), *Active Inference*, MIT
Press, doi:10.7551/mitpress/12441.001.0001. Variational inference and the
evidence lower bound: Jordan, Ghahramani, Jaakkola, Saul (1999), Machine Learning
37:183-233, doi:10.1023/A:1007665907178; Blei, Kucukelbir, McAuliffe (2017),
JASA 112(518):859-877, doi:10.1080/01621459.2017.1285773. Technical criticism:
Biehl, Pollock, Kanai (2021), *A Technical Critique of Some Parts of the Free
Energy Principle*, Entropy 23(3):293, doi:10.3390/e23030293; Aguilera, Millidge,
Tschantz, Buckley (2022), *How particular is the physics of the free energy
principle?*, Physics of Life Reviews 40:24-50,
doi:10.1016/j.plrev.2021.11.001; Bruineberg, Dolega, Dewhurst, Baltieri (2022),
*The Emperor's New Markov Blankets*, Behavioral and Brain Sciences 45:e183,
doi:10.1017/S0140525X21002351. Control as inference and KL control: Todorov
(2009), PNAS 106(28):11478-11483, doi:10.1073/pnas.0710743106; Kappen, Gomez,
Opper (2012), Machine Learning 87:159-182, doi:10.1007/s10994-012-5278-7;
Levine (2018), arXiv:1805.00909. Rate-distortion: Shannon (1959), IRE National
Convention Record 7:142-163; Berger (1971), *Rate Distortion Theory*, Prentice-Hall;
Sims (2003), Journal of Monetary Economics 50(3):665-690,
doi:10.1016/S0304-3932(03)00029-1.

Nothing in this package is claimed novel against the parent literature. The
named residual contribution of this tranche is stated in
`PARENT_OWNERSHIP_V1.md` and is the exact finite construction and its
machine-checked verification, never the underlying parent theorems.
