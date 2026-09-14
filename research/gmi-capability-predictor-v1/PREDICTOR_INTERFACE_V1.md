# Predictor interface — Cap(D,E,R,H) -> capability distributions + abstention

**Issue:** #602 F4. **Ceiling:** G1 spec (no G6 empirical claim). **Authoritative contract:** `CONTRACT_V1.json` + `SCHEMA_V1.json`.

## 1. Signature

```text
Cap : (D, E, R, H) -> ( [Cap_1,...,Cap_27] , meta )
```

- `D : MorphologyDescriptorV1` — 8-field brand-free descriptor (`DESCRIPTOR_V1.md`).
- `E : EcologyExtensionV1` — 15 ecology coords + remint guard (`gmi-ecology-extension-v1`).
- `R = (b, p, rho)` — hard budgets `b`, nonnegative price `p` frozen prospectively, physical map `rho`.
- `H = (H_dev, H_held, lineage)` — which families were seen during derivation/fitting, which are held, and prior morphology transitions.
- `Cap_c` per each of the 27 A4 rows `cap-*` is a **distribution**, not a point scalar. Two frozen forms:

  - **Categorical:** `p = (p0, p1, p2)` over `{fail, marginal, capable}` with `sum=1`, `p_i ≥ 0`. Thresholds `tau_parent, tau_twin` per F1 S0 decide the label if needed.
  - **Continuous:** `Beta(a,b)` over success probability in `[0,1]` with reported mean `a/(a+b)` and credible interval (e.g., 90% equal-tailed). Choice categorical vs Beta is frozen per row before held outcomes.

No architecture-independent scalar "IQ" is implied. A cross-row aggregation `J_p(C)=sum p_j phi_j(C_j)` is only admissible with `p_j ≥ 0` frozen prospectively; default report is componentwise / Pareto.

## 2. Scope and assumptions

1. **Finite declared families only.** No claim across unrestricted ecologies.
2. **Admissibility only (DU-1).** `Cap` bounds what `D` *could* do if reached, not whether development law `D_dev` will reach it. Reachability is separate (#602 E).
3. **Per-row allowed information A0.** Prompt/context store/query distinctions per A4 `allowed_info`; no privileged future/judge leakage.
4. **Negative twin N0 and parent first refusal P0** from `FORMALIZATION_V1.md` apply per row: a claimed capability must beat its preregistered parent `V_c^P(E,B)` at matched information/resource, and must collapse on its matched twin.
5. **Independent units per F1 S0.** Success differences lie in `[-1,1]`; concentration uses `eps(n,alpha)=sqrt(2 ln(3/alpha)/n)`. Dependent rows require a separately registered simultaneous-validity construction (#602 M).

## 3. Loss — strictly proper, held-only, remint-canonicalized

**Primary:** per-row **strictly proper scoring rule** on held families only.

- Categorical: **Brier** `mean((p - one_hot(y))^2)` or **log score** `-log p_y`, where `y` is the realized grade by the A4 `success_metric`.
- Continuous: log score `-log Beta_pdf(y)` or CRPS/Brier on the calibrated probability, against realized 0/1 success or graded label by that row's metric.

**Scope:** `H_dev` (development worlds) is for fitting/deriving the predictor and is excluded from scoring. Only `H_held` contributes. Before scoring, each family's data is canonicalized under its **per-family bijective remint** (bijection on world/task ids, label-leakage-free per `ECOLOGY_EXTENSION_CONTRACT_V1.json` `equivalence_remint_rules`). Held loss is reported per row; no cross-row scalar without a frozen `p`.

**Parent claim:** supremum is over the *registered* parent envelope `Pi_c^P(B)` at matched budgets (F1 P0). Search coverage must be reported when the envelope is open.

## 4. Abstention gate — when not identifiable, withhold

Predictor **must abstain** per row rather than emit an overconfident forecast when the mapping is not identifiable from development support.

### Firing condition (any triggers abstention)

Let thresholds `eta_c, delta_c, d_max` be frozen before held outcomes.

1. **Underspecification:** any required `D` field or `E` coordinate is `NONE/UNDECLARED`, or `|S|` not declared.
2. **Out-of-support:** held ecology/task embedding distance from convex hull of `H_dev` support exceeds `d_max` (remint-invariant metric, e.g., Mahalanobis on ecology one-hot + resource-normalized coordinates), or held family was never represented in `H_dev`.
3. **Non-identifiability:** posterior variance/entropy > `eta_c`, or credible interval width > `delta_c`, or CI straddles both `tau_parent` and `tau_twin` so S0 gate cannot be decided.
4. **Parent-unbounded:** `V_c^P(E,B)` not bounded/enumerated to required precision at this budget.
5. **Remint risk:** proposed remint for the family is not bijective or leaks the label (ecology remint validator rejects).

Operators may **tighten** thresholds; relaxing post-freeze is forbidden.

### Reporting

For each row, decision `{predict, abstain}` with reason code is committed **before** observing that family's outcome. Report per-row abstention rate, **selective risk** (loss conditional on non-abstained rows) and **coverage vs efficiency** tradeoff (`1 - abstention_rate` vs selective risk). Abstained rows are not scored; abstention does not earn capability credit.

### Parent and falsifier

Parent: selective prediction / Chow's reject option; conformal abstention; calibration (Gneiting&Raftery 2007); F1 three-event assay boundary.

Falsifier: any held family built from a world alphabet symbol absent from every development world (e.g., `UNSEEN_SYMBOL` family) where the predictor emits a confident (non-abstained) forecast past a frozen out-of-support threshold.

## 5. Relation to F1 assay

The predictor reuses F1's common assay per row:

```text
S0: mean(d+) - eps(n+,alpha) > tau_parent  and  |mean(d-)| + eps(n-,alpha) <= tau_twin
votes: POSITIVE worlds show candidate-parent gap; TWIN worlds collapse it.
```

F1 provides the statistical gate; F4 provides the *prospective mapping* from morphology to whether that gate will pass on an unseen family. F4 without F1 is unscored; F1 without F4 has no extrapolation.

## 6. Evidence gate

No `G6` predictor claim is earned until: descriptor enumerability check (P1) + interface check (P1) + **per-family frozen predictions** (digest + timestamp < outcome) + **held-family proper-loss scoring** + **abstention audit** + **parent subtraction** + **twin-collapse audit**, all prospective.

## 7. Example shape (informative, not normative)

```json
{
  "family": "held-delay6-v1",
  "remint_seed": "sha256:abc...",
  "D": {"state_carrier": "FINITE_ALPHABET(8)", "...": "..."},
  "E": {"task_distribution_horizon": {"H": 200}, "...": "..."},
  "R": {"b": {"store_bits": 12}, "p": [0.5,0.5], "rho": "host-a"},
  "H": {"dev_families": ["dev-delay1..5"], "held_families": ["held-delay6-v1"]},
  "per_row": {
    "cap-working-memory": {"distribution": {"p": [0.05,0.15,0.80]}, "abstain": false},
    "cap-tool-use": {"abstain": true, "reason": "parent-unbounded"}
  }
}
```
