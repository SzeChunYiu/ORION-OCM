# GMI #859/#833-D execution controls — freeze v1

**Child issue:** #859 (`T833-D-execution-controls`)
**Parent:** #833 Section D (execution) + the four exact open rows listed below
**Frozen from main:** `f4d9d7d5` (`research(#833): terminology migration v2 … (#947)`)
**Claim ceiling:** `GMI_DERIVATION_ROBUSTNESS_CONTROLS_ENFORCED_AT_REGISTERED_FINITE_SCOPE`

This is the pre-implementation custody record. Executor code, fixtures, tests,
receipt, theorem note, manifest, reconciliation spec, and workflow must postdate
this freeze. There is no RNG anywhere in this tranche; the deterministic "seed"
is the frozen case grid plus this freeze commit.

## What this tranche is, and is not

Sibling #863 (`gmi-833-robustness-controls-v1`) formalized the four Section-D
controls as detector contracts on toy fixtures. This tranche is **not another
detector-only package**: it (a) hardens the control definitions where the
2026-09-16 audit found a hole (two alleged search replicas that were one
algorithm in two encodings), (b) wraps them in a fail-closed, machine-readable
`DerivationRobustnessRecord` admission schema reusable by Section H/J derivation
packages, and (c) **executes every control end-to-end on one registered result
family from main**, with exact finite positive/negative witnesses and one
targeted hostile per control plus cross-control combinations.

## Registered execution substrate (frozen, reused, not rebuilt)

The result family is the merged #901 `gmi-833-heldout-20-transitions-v1`
package: binary sequential candidate universe

- `U` = 16 stateless candidates (4-bit output tables) + 65,536 stateful
  candidates (8-bit next-state table × 8-bit output table over 1-bit state),
  evaluated on 8 binary input sequences of length 3 in two modes
  (now-prediction `mode=0`, delay-prediction `mode=1`), exact integer error
  counts `(error_now, error_delay)` each in `0..16`;
- registered objective `eta*((1-p)*en/16 + p*ed/16) + lambda*s` with exact
  rational parameters; registered phase law `lambda* = eta*p/2` predicting
  `PERSISTENT_STATE -> STATELESS` (20 frozen held-out transition cases, 40
  endpoint worlds, 20 boundary worlds);
- semantic projection `rho(c) = (s, en, ed)` with the frozen 146-point risk
  histogram and candidate-ID remint machinery.

Registered mechanism `K` = **data-dependent internal state**: the semantic
fingerprint of `K` on a candidate is `state_data_dependent(c)` (the next-state
table is not state/input-constant in the registered encoding). Registered
K-dependent target property: `ed(c) < 8`. Frozen substrate facts (proved by
#901 receipts): every stateless candidate has `ed >= 8` (floor attained), and
stateful candidates attain `(en, ed) = (0, 0)`. So `ed < 8` is realizable by
`K`-carrying candidates only.

## D-X1 — matched mechanism-removal twin gate (hardened)

For a twin pair `(G+, G-)` over the substrate, define the non-K capacity
descriptor vector

```
D(G) = (candidate_count, primitive_envelope, non_k_operator_inventory,
       evaluator_id, sequence_set, budget, tie_rule, stopping_rule,
       representable_k_free_behaviour_set)
```

`G-` is a **matched mechanism-removal twin** iff

1. `D(G-) = D(G+)` on every coordinate (exact equality; `candidate_count`
   equal — removal is by disabling the mechanism in place, not by deleting
   candidates);
2. no candidate in `G-` carries the K fingerprint, and the K-dependent target
   property `ed < 8` is unrealizable in `G-`;
3. no operator or macro absent from `G+`'s inventory appears in `G-`
   (no compensating target-equivalent macro);
4. multiplicity reweighting inside the K-free behaviour family is **reported,
   never disguised** (in-place disabling reweights K-free behaviour
   multiplicities; that is a declared consequence of ablation, not a capacity
   change);
5. the #855 semantic no-smuggling auditor runs on **both** twins with clean or
   evaluable terminals.

Registered construction: `G-` = state-register ablation — every stateful
candidate keeps its full table slots (same count, same primitive envelope,
same evaluator, same budget) but the next-state table is replaced by the
constant-0 table, so the state register is inert; behaviour collapses exactly
onto the 16-candidate K-free behaviour family.

Hostiles (must fire):

- **H1a capacity-hostile:** delete all stateful candidates (`G-` = 16
  stateless only). Performance falls, but `candidate_count` differs →
  `UNMATCHED_MECHANISM_TWIN`, **not** evidence that `K` is necessary.
- **H1b macro-hostile:** ablate state but introduce a `PREV` primitive
  (hard-wired previous-input output with `ed = 0`) → operator inventory
  differs → `UNMATCHED_MECHANISM_TWIN` (compensating macro).
- **H1c stopping-hostile:** ablate state and quietly halve the evaluation
  sequence set → `sequence_set` differs → `UNMATCHED_MECHANISM_TWIN`.

Interpretation rule: the K-dependence of the phase law may be claimed only by
running the identical frozen case grid on the **matched** twin (where the
persistent-state regime must vanish because `K` is disabled at equal capacity),
never on an unmatched twin.

## D-X1E — matched positive/negative ecology twins (#833 Section G row)

Ecology descriptors `Ec(E) = (sequence_set, mode_count, scoring_events,
mixing_parameter_p, evaluator_id, tie_rule, budget)`. The registered pair:

- `E+` = the frozen #901 ecology: both modes present, delay mode carrying the
  memory demand, mixing weight `p`;
- `E-` = the matched negative ecology twin: the delay-mode evaluation is
  replaced by a second now-mode evaluation with the same sequence set, same 16
  scoring events, same evaluator/budget/tie rules — only the K-relevant task
  property (prediction target requires previous input) is removed.

`E-` is matched iff all descriptor coordinates except the registered
mode-target vector are equal. Hostile: an ecology twin that also halves the
sequence set → `ECOLOGY_TWIN_UNMATCHED`. Hostile: an ecology twin that rescales
`eta` → `ECOLOGY_TWIN_UNMATCHED`.

## D-X2 — alternate semantic encoding / remint gate (mechanical invariance)

Two encodings `E1, E2` of the same finite candidate set are **semantic
remints** iff a registered bijection `phi: E1 -> E2` exists and an independent
`E2` evaluator reproduces, for **every** candidate, the exact `rho` value and
objective-resource fingerprint of `E1` (full 65,552-candidate exact census,
not a sample). All claim comparison happens after canonical semantic
projection `rho`; raw program strings and surface names are never compared.

Registered pair:

- `E1` = the #901 table encoding (integer tables, `q%05d` surface ids);
- `E2` = a syntactically disjoint rule-list encoding: symbolic
  state/mode/input/output alphabet (disjoint from `E1`'s), rules enumerated in
  Gray-code table order, `W…` base-26 surface ids, independently written
  evaluator.

Invariance is proved by construction for every `rho`-functional conclusion
(bijection + per-candidate `rho` equality ⇒ equal multiset statistics and
equal `rho`-projected optima), then tested empirically on the full frozen
world grid (winner value, winner state property, 146-point histogram,
threshold law) — the *mechanical* content #859 demands.

Hostiles (must fire):

- **H2a deletion:** an alleged remint whose map silently deletes one candidate
  → non-bijective → `ENCODING_NOT_SEMANTICALLY_EQUIVALENT`.
- **H2b cost-mutation:** an `E2` evaluator that scales delay error by `15/16`
  → resource fingerprint mismatch → `ENCODING_NOT_SEMANTICALLY_EQUIVALENT`.
- **H2c surface-tie:** a decision rule that tie-breaks on lexicographic
  surface ids changes its canonical conclusion under a pure remint →
  `ENCODING_SENSITIVE` (this is the registered identification witness for the
  #833 Section-B row "claims sensitive to arbitrary encoding choices",
  together with the merged #875 `GA/GB` same-semantics non-isometric
  selection reversal already on main).

## D-X3 — alternate search algorithm gate (materially different procedures)

At least two **materially distinct** registered search procedures over the
same frozen candidate semantics, objective, tie policy, and budget frame.
Material distinctness is **certified mechanically, not by declared signatures
alone** — this hardens #863 against the one-algorithm-two-encodings failure:

> Two registered searchers are materially distinct iff (i) their declared
> difference tables differ on at least two declared axes, and (ii) their
> canonical evaluation traces (the ordered tuple of `rho`-semantics of each
> evaluated candidate) differ, and (iii) neither is a re-encoding of the
> other: a re-encoding pair has identical canonical traces (up to the
> registered bijection) and identical acceptance decisions on every probe, and
> must be rejected as `SEARCHERS_NOT_MATERIALLY_DISTINCT`.

Registered replicas (difference table frozen):

| axis | S1 exhaustive enumeration | S2 risk-frontier branch&bound | S3 best-first certificate |
|---|---|---|---|
| representation | raw 65,552 candidates | compressed 146 risk points | compressed 146 risk points |
| exploration order | enumeration order | price-sorted order | min-heap by admissible lower bound |
| pruning | none | admissible lower bound (strict) | none (early stop by certificate) |
| acceptance/termination | full-scan exact argmin + tie set | incumbent update + tie set | accept-on-optimality-certificate + mandatory tie sweep |
| completeness proof | construction (evaluates all) | admissibility theorem | dominance certificate + tie sweep theorem |
| search cost | 65,552 evaluations | evaluated points (pruned reported) | evaluations until certificate |

S1/S2 are reused from #901 (source-separated); S3 is new. Required outputs per
procedure: selected semantic optimum/set, coverage certificate or explicit
incompleteness, **search cost reported separately from candidate resource
cost**, and pairwise distinctness certificates.

Hostile (must fire): **H3a early-stop heuristic** — first-accept in
price-sorted order without certificate returns the wrong winner on the
registered grid → `SEARCH_SENSITIVE`, surfaced, never averaged.
Hostile: **H3b re-encoding masquerade** — S2 with reminted point ids
registered as an alleged third replica → identical canonical trace and
acceptance decisions → `SEARCHERS_NOT_MATERIALLY_DISTINCT` (the #932-failure
detector). This is the registered identification witness for the #833
Section-B row "claims sensitive to search algorithm rather than scientific
structure" (search-dependent conclusions exist and are caught; the frozen
law's conclusions are search-invariant at registered scope).

## D-X4 — alternate scalarization / Pareto gate + metric perturbations

Resources are raw vectors `r(c) = (en, ed, s)`; the Pareto relation is primary.
Required outputs: full exact Pareto set over the 146 risk points (with
multiplicities), winner under each registered scalarization, and the split of
invariant vs price-conditional claim language.

Registered scalarizations (preregistered, frozen): the 30 strictly positive
endpoint weight vectors of frozen cases 1–15, plus the 20 boundary weight
vectors of cases 1–20 as declared boundary probes (cases 17–20 have `p = 1`
and are boundary probes by declaration, not positive scalarizations).

Frozen theorems to re-verify on the substrate: strictly positive weighted-sum
scalarization never selects a Pareto-dominated candidate; Pareto-incomparable
candidates reverse under suitable positive weights.

Hostile (must fire): **H4a winner-reversal** — a registered Pareto-incomparable
pair from the exact census reverses under positive weights (the `(1,4)` vs
`(4,1)` pattern realized on real census points) → any universal-winner
wording fails with `SCALARIZATION_SENSITIVE`; price-conditional language
survives. Robust morphology language survives only for properties shared by
the entire Pareto frontier (e.g. every frontier point with `ed < 8` has `s=1`).

Metric perturbation control (#833 Section-F row content): for every registered
endpoint world, perturb the weight vector within the **derived** exact
stability bound (half the exact margin between the world's price and the
phase boundary `eta*p/2`, and coordinatewise error-weight perturbations bounded
by the same derived margin) — the winner-state partition and the 146-point
clustering must be stable inside the bound and must flip exactly at the
boundary; grammar remints (ID remint and the full `E2` structural remint)
must preserve the clustering and partition at every perturbed world. No
arbitrary perturbation constants: every epsilon is derived from the exact
phase-cell margin of the world it perturbs.

## Cross-control admission schema

A machine-readable `DerivationRobustnessRecord` (schema
`GMI833DerivationRobustnessRecordV1`, stdlib-only validator in this package,
reusable by later Section H/J derivation packages). A claim may receive

`ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE`

only if all five conditions hold (else fail closed to
`CANNOT_ESTABLISH_D_ROBUSTNESS_<CONTROL>`, or to the matching sensitivity
terminal, never silently clean):

1. matched mechanism-removal twin valid and outcome interpreted against it;
2. at least two semantic-equivalent encodings agree after canonical
   projection (full exact census);
3. at least two materially distinct registered search procedures support the
   same scoped conclusion (or an exhaustive theorem removes search
   dependence);
4. raw Pareto analysis plus at least two preregistered positive
   scalarizations do not contradict the claim's universality wording;
5. the #855 no-smuggling audit is clean/evaluable for every compared arm.

Fail-closed census requirement: every single-control deletion, plus the
cross-control combination hostiles (twin valid + encoding census broken;
search re-encodings only; empty scalarization set; unclean no-smuggling on
the negative arm) must produce the exact typed failure terminal.

## Exact target rows (#833)

This tranche may reconcile only these four open rows, at the registered
scope stated in each replacement:

1. `Identify claims sensitive to arbitrary encoding choices.` (Section B)
2. `Identify claims sensitive to search algorithm rather than scientific structure.` (Section B)
3. `Validate clustering stability under grammar remints and metric perturbations.` (Section F)
4. `Construct matched positive/negative ecology twins.` (Section G)

Rows 1–2 are closed by the registered identification witnesses (H2c/H3b plus
the corpus examples #875 `GA/GB` and the #863 budget-one forward/reverse
search hostile, with the #901 family audited robust at registered scope) —
identification at registered scope, not a corpus-wide RED/AMBER/GREEN table.
Rows 3–4 are closed at the #901-family scope exactly as constructed above.

## Parent authority / literature boundary

Consumes, does not re-claim: #837 foundation and P3/P4 wording; #855/#856
no-smuggling audit terminals; #848/#850 raw capability/resource definitions;
#863 control requirement contracts; #901 substrate universe, searchers, and
phase law. No novelty is claimed for negative controls, metamorphic
invariance testing, Pareto order, or multiobjective scalarization. The
residual contribution is the hardened, mechanically-certified execution
controls plus the fail-closed admission record.

## Forbidden promotions (from #859, verbatim)

`ALL_GMI_DERIVATIONS_ROBUST`, `ARCHITECTURE_PRIOR_FREE_UNIVERSALLY`,
`REPRESENTATION_INDEPENDENT_UNIVERSALLY`, `SEARCH_INDEPENDENT_UNIVERSALLY`,
`RESOURCE_PRICE_INDEPENDENT_UNIVERSALLY`, `KNOWN_FAMILY_RECOVERY_COMPLETE`,
`COMPLETE_GMI`.

## Evidence commitments

Post-freeze artifacts must include: stdlib-only exact finite executor with
exact rational arithmetic; the four controls executed on the #901 family;
one targeted hostile per control plus cross-control combinations; the
fail-closed admission census; deterministic normal and `python -O`
byte-identical receipt; machine-readable record schema/validator; PR
check-only / main-push apply-only reconciliation for the four exact rows;
validator self-test on the no-alarm case (validate-the-checker-first).
