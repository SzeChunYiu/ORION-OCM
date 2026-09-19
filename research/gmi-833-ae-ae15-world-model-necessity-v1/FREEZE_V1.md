# GMI #833 Section AE15 — world-model necessity boundary: prospective freeze v1

Source `main`: `0dcdec54fbece041ee2b7cd1f630469ad85d19d3`.

This freeze is committed **before** any executor, oracle, test, fixture,
receipt, theorem note or reconciliation file of this package exists in the
tree. The add-order of the blobs is the custody evidence; this commit
touches exactly one file.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE15 — World-model necessity boundary`

1. `- [ ] Define \`world model\` operationally and distinguish explicit generative model, predictive state, value representation, reactive policy and cached skill.`
2. `- [ ] Construct tasks solvable optimally without an explicit world model.`
3. `- [ ] Construct tasks where a model is provably necessary under the registered interface/resource assumptions.`
4. `- [ ] Derive model-based vs model-free/retrieval/reactive phase boundaries.`
5. `- [ ] Test whether latent variables recovered by a model correspond to identifiable world factors or merely predictive coordinates.`
6. `- [ ] Forbid claims that successful intelligence necessarily reconstructs human-interpretable latent variables.`

**No neighboring row is earned here.** In particular this tranche does not
earn any AE1, AE2, AE3, AE4, AE5, AE6, AE7, AE8, AE9, AE10, AE11, AE12, AE13, AE14, AE16 or AE17 row of issue comment 5692689542, and does not earn any
row of the #833 issue body.

## Registered scope and frozen objects

A **registered task** is a finite POMDP `K = (S, O, A, T, Z, R, gamma, H)` with
`T(s'|s,a)`, `Z(o|s)` and the initial distribution all exact rationals, `R(s,a)` an
exact rational reward, a frozen rational discount `gamma` and a frozen finite
horizon `H`. All optimal values are exact rationals computed by backward induction
over the finite belief set reachable in `H` steps.

Five representation classes are defined as **interfaces**, so that `world model` is
operational rather than rhetorical:

- `REACTIVE_POLICY`: a map `O -> A`; no memory, no model.
- `CACHED_SKILL`: a map from a registered finite context set to a fixed action
  sequence; replay only, no re-planning under a changed reward.
- `VALUE_REPRESENTATION`: a map `O -> Fraction` used greedily with the registered
  one-step lookahead but **without** access to `T` or `Z`.
- `PREDICTIVE_STATE`: a sufficient statistic of history for the distribution of
  future observations, with no reward or action semantics.
- `EXPLICIT_GENERATIVE_MODEL`: the tables `T` and `Z` themselves, usable for
  counterfactual rollout under a **changed** reward without new data.

The distinguishing operational test between the last and the others is the frozen
**reward-swap probe**: the reward table is replaced by a registered alternative and
the representation is re-queried with no further interaction. Only the explicit
generative model can be re-optimized under the probe.

The **phase-boundary family** is a frozen one-parameter family indexed by an exact
rational planning cost `c` and an integer goal count `G`, in which the model-based
value is `V_mb(G) - c` and the best model-free value is `V_mf(G)`; the boundary is
the exact rational `c* (G)` at which the two coincide.

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

- **Row 1.** The five interfaces above, each instantiated on the registered roster,
  plus the reward-swap probe result per class, and a pairwise distinctness table with
  a registered task witnessing each ordered separation.
- **Row 2.** A registered task on which the **exact** optimal value is attained by a
  member of `REACTIVE_POLICY`, with the exact optimum, the exact reactive value and
  their exact difference `0`, verified by exhaustive enumeration of all `|A|^|O|`
  reactive policies in route B.
- **Row 3.** A registered task on which **every** member of `REACTIVE_POLICY`,
  `CACHED_SKILL` and `VALUE_REPRESENTATION` is strictly suboptimal, with the exact
  best value attainable in each class, the exact model-based optimum, and the exact
  gap. `Provably necessary` is claimed only at this registered scope and is
  established by exhaustive enumeration of each finite class, not by an appeal to
  hardness.
- **Row 4.** The exact rational threshold `c*(G)` derived in closed form and verified
  numerically-exactly at every `G` in the frozen range, with the chosen class flipping
  at `c*` and the **strictness** of the flip demonstrated on both sides. The boundary
  record carries the bound-vacuity fields, including a `violated_by` witness drawn
  from an explicitly relaxed class.
- **Row 5.** Two structural causal models with **different** latent factorizations and
  **identical** observational and predictive behaviour, verified by exact equality of
  every observable joint, establishing non-identifiability; and one registered model
  whose latent is exactly recoverable up to relabeling, with the recovery map
  exhibited. The distinction between an identifiable world factor and a merely
  predictive coordinate is thereby machine-checked.
- **Row 6.** The forbidden promotion `LATENTS_ARE_HUMAN_INTERPRETABLE` is registered
  and the row-5 non-identifiability pair is its machine-checked evidence; the
  executor asserts that no artifact of this package asserts the forbidden string.

## Two materially independent routes

Route A is `ae15_world_model_necessity_v1.py`. Route B is `independent_world_model_oracle_v1.py`.
Route B contains no executable import of route A and recomputes every
claimed quantity by a materially different algorithm (exhaustive enumeration of every deterministic memoryless policy, every cached-skill table and every value function over the registered finite POMDPs, and independent exact value iteration on the belief lattice, against route A's closed-form optimal-value recursion and its algebraic phase-boundary derivation).
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

`GMI_833_AE15_WORLD_MODEL_NECESSITY_BOUNDARY_DERIVED_ON_REGISTERED_FINITE_POMDP_ROSTER`

## Forbidden promotions

`INTELLIGENCE_EQUALS_COMPRESSION`, `ALL_LEARNING_IS_COMPRESSION`, `MANIFOLD_HYPOTHESIS_UNIVERSAL`, `MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`, `WORLD_MODEL_ALWAYS_REQUIRED`, `FREE_ENERGY_PRINCIPLE_PROVED`, `THERMODYNAMIC_INTELLIGENCE_LAW`, `GENERAL_REASONING_REDUCED_TO_PREDICTION`, `COMPLETE_GMI`, `ARCHITECTURE_SELECTION_LAW`, `GMI_MORPHOLOGY_PREDICTION`, `ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER`, `REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT`, `WORLD_MODEL_ALWAYS_REQUIRED`, `WORLD_MODEL_NEVER_REQUIRED`, `LATENTS_ARE_HUMAN_INTERPRETABLE`, `MODEL_BASED_DOMINATES_MODEL_FREE`.

## Parent ownership

POMDPs, belief states and sufficient statistics: Astrom (1965), Journal of
Mathematical Analysis and Applications 10(1):174-205,
doi:10.1016/0022-247X(65)90154-X; Smallwood, Sondik (1973), Operations Research
21(5):1071-1088, doi:10.1287/opre.21.5.1071; Kaelbling, Littman, Cassandra (1998),
Artificial Intelligence 101(1-2):99-134, doi:10.1016/S0004-3702(98)00023-X.
Predictive state representations: Littman, Sutton, Singh (2001), NIPS; Singh,
James, Rudary (2004), UAI, arXiv:1207.4167. Model-based versus model-free control
and the arbitration question: Sutton (1991), SIGART Bulletin 2(4):160-163,
doi:10.1145/122344.122377; Daw, Niv, Dayan (2005), Nature Neuroscience
8(12):1704-1711, doi:10.1038/nn1560; Keramati, Dezfouli, Piray (2011), PLoS
Computational Biology 7(5):e1002055, doi:10.1371/journal.pcbi.1002055.
Memoryless-policy suboptimality in partially observed problems: Singh, Jaakkola,
Jordan (1994), ICML, doi:10.1016/B978-1-55860-335-6.50042-8; Littman (1994), ICML.
Latent-variable identifiability: Hyvarinen, Pajunen (1999), Neural Networks
12(3):429-439, doi:10.1016/S0893-6080(98)00140-3; Locatello, Bauer, Lucic,
Ratsch, Gelly, Scholkopf, Bachem (2019), ICML, arXiv:1811.12359; Khemakhem,
Kingma, Monti, Hyvarinen (2020), AISTATS, arXiv:1907.04809.

Nothing in this package is claimed novel against the parent literature. The
named residual contribution of this tranche is stated in
`PARENT_OWNERSHIP_V1.md` and is the exact finite construction and its
machine-checked verification, never the underlying parent theorems.
