# FREEZE_V1 — `gmi-833-aj15-flagship-experiment-v1`

Committed **before any implementation, executor, oracle, test, receipt or measurement of
this package exists**. The first commit touching this directory carries only `FREEZE_V1.md`
and `FREEZE_ROWS_V1.json`; `check_freeze_order_v1.py` re-derives that from git in CI with a
negative control, and degrades to a distinct `UNREACHABLE` state (never a pass) if the freeze
commit cannot be reached after a squash.

- **`source_main`** = `f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5`
  (`fix(#833): my gate scoping crashed the harness on an argument position (#1051)`).
- **Claim ceiling** =
  `AJ15_FLAGSHIP_END_TO_END_EXECUTED_WITH_FAMILY_REGISTRY_HIDDEN_AT_REGISTERED_FINITE_B1_AND_B2_SCOPES`.
  It sits strictly under the two ceilings this package may not exceed:
  `AJ9_ALL_11_REGISTERED_FAMILIES_RECOVERED_WITH_FAMILY_LABELS_HIDDEN_AT_DECLARED_FINITE_TASK_AND_BASIS_SCOPES`
  (`gmi-833-aj9h-k07-k11-blind-recovery-v1`) and `FGS-4`
  (`gmi-833-h-family-gate-soundness-v1`: family identity does not follow from operational
  equivalence alone; a scoped, prior-disclosed post-hoc mapping is permitted).
- **Issue-comment fetch** of comment `5693954852` pinned in `FREEZE_ROWS_V1.json` by sha256
  `60b6b8ee34f6c4a1…` (29,631 bytes), with each row's verbatim text and per-row sha256.

## 1. The exact rows this tranche may reconcile

Seven, and only seven: `AJ15_R1` … `AJ15_R7` in `FREEZE_ROWS_V1.json` — the seven unchecked
rows under the anchor `### AJ15 — Flagship end-to-end falsification experiment — OPEN`. They are
the only unchecked rows in the whole comment (83 of 90 rows are checked at `source_main`).

**No neighboring row is earned here.** AJ0–AJ14 are already checked and are cited only as
parents; AJ16 (`NOT EARNED`) is not touched. No row of any other comment or of the issue body is
in scope. This package **never edits any comment or the issue body**; its only issue-facing
artifact is `ISSUE_833_COMMENT_RECONCILIATION_V1.json`.

## 2. One experiment, not seven

Two prior lanes recorded that AJ15 is one experiment and declined to split it. This package
builds it as one run and reports each row as a facet of that run:

> The family-blind enumerative search over the frozen bounded universe **B1**, with the AJ9a
> registry hidden from generation, search and evaluation, under five registered task/resource
> regimes with a prediction per regime frozen here; the `UNKNOWN` channel live for every
> exact solver that matches no registered fingerprint; post-hoc adjudication against the
> registry only after the blind outcome is committed; then the same protocol repeated at a
> larger, **non-enumerated** universe **B2** with two independent search implementations; and
> finally the AJ13 stopping rule and the AJ14 establishment ladder applied to the run.

### 2.1 Universe B1 (bounded, every candidate enumerated)

B1 is the AJ4/AJ11 universe: the 4 memoryless one-bit maps plus all 256 one-bit-state
deterministic step tables over the binary alphabet — 260 presentations, 148 operational
classes, pinned by the AJ11 canonical atlas SHA-256
`09a99f29d2d349d7f28855d3a32776667c65cd1a707ea89129fd77c3328a16ed`. B1 was constructed in
`gmi-833-aj4-process-organizations-v1` at commit `83d79b44` (2026-09-16 11:07:50 +0200),
**before** the AJ9a registry was frozen at `aec01b0e` (2026-09-16 11:59:03 +0200); the
universe therefore was not built from the registry. Both timestamps are re-read from git by
the executor.

Task family `Q` (frozen, identical to AJ11): `identity`, `not`, `delay1`, `toggle`, `const0`,
each a total function on binary words, evaluated exactly on all 31 words of length ≤ 4 from
the seed state. Raw resources: `(state_cells, truth_rows)`. No scalarization.

### 2.2 The registry is hidden; one family is the pre-declared holdout target

The whole registry `KNOWN_FAMILY_BENCHMARK_V1.json` (blob `6b9ac3095c90d74e2717671a70ad7cc18955310c`)
is inaccessible to every blind artifact of this package (`aj15_flagship_v1.py`,
`independent_oracle_v1.py`, `BLIND_OUTCOME_V1.json`, `SEARCH_CONFIG_V1.json`). It is read only
by `posthoc_adjudicate_v1.py`, which refuses to run unless `BLIND_OUTCOME_V1.json` already
exists and records that file's sha256 in its own receipt. The blind artifacts are scanned for
the registry's vocabulary (identifiers, names, name tokens, fingerprint/exclusion/observation
clauses, parent anchors), derived from the pinned blob, not hand-written; a control scan of
the post-hoc artifacts must return hits, and one planted positive per forbidden class must be
detected, before any `0` is reported.

The holdout whose presence/absence the theory predicts is written here in operational
vocabulary only: **the persistent-internal-state organization** — an exact solver whose output
on some input symbol differs between two *reachable* internal states. Which registry entry, if
any, that corresponds to is decided only post hoc, by the frozen fingerprint, and is reported
as a scoped mapping under FGS-4, never as family identity inferred from behaviour.

### 2.3 Regime predictions, frozen now (row `AJ15_R4`)

A specification is **memoryless-realizable** iff it is computed by a map from the current
symbol alone. The registered prediction, derived from operational quantities and nothing else:

| regime | memoryless-realizable | prediction for exact solvers |
|---|---|---|
| `identity` | yes | **none** has a reachable-state-dependent output (holdout organization absent) |
| `not` | yes | absent |
| `const0` | yes | absent |
| `delay1` | no | **every** exact solver has a reachable-state-dependent output (holdout present) |
| `toggle` | no | present |

Justification recorded now so it cannot be re-read later: if no reachable state changes any
output, the machine's input/output behaviour is a memoryless map; conversely a specification
that is not memoryless-realizable cannot be met without a reachable state that changes an
output. The prediction is therefore a consequence of the theory, which is exactly what row
`AJ15_R4` asks: regimes in which the held-out organization is predicted **not** to appear.

**Decision rule (rows R1–R4, R6).** The bounded flagship is `CONFIRMED_AT_B1` iff, on both
routes: (i) every exact solver in each regime is enumerated; (ii) in `identity`, `not`,
`const0` the count of exact solvers with a reachable-state-dependent output is `0`; (iii) in
`delay1`, `toggle` that count equals the count of exact solvers; (iv) every exact solver that
matches no registered fingerprint post hoc is placed in the `UNKNOWN` channel with
`registered_family: null` and survives to strongest-parent review, where it is either
`PARENT_REDUCED_KNOWN` or left `UNKNOWN`; and (v) the post-hoc fingerprint outcome per regime
agrees with the prediction table above. Any failure of (ii), (iii) or (v) is recorded as
`FALSIFIED` (see §5), not explained away.

### 2.4 Universe B2 (larger, non-enumerated; row `AJ15_R5`)

B2 is the 4-state deterministic step-table universe over the binary alphabet: for each of the 8
(state, symbol) pairs a (next state ∈ {0,1,2,3}, output bit) entry — `8^8 = 16,777,216`
presentations. **B2 is not enumerated by this package**; it is searched under a registered
budget by two materially independent implementations:

- `S1` (route A): random-restart mutation hill-climb on the one-entry development graph,
  `random.Random(seed)` with the seed frozen in `SEARCH_CONFIG_V1.json`, exact mismatch count
  over all 127 words of length ≤ 6 as the objective, total budget `300000` evaluations per
  regime, restarts every `2000` non-improving evaluations;
- `S2` (route B): a residual/right-congruence construction from the specification — prefixes
  of length ≤ 6 are merged when their futures agree on every continuation inside the window,
  the quotient is read off as a step table, and the construction returns
  `NOT_RECOVERED_AT_SCOPE` if the quotient needs more than 4 states.

Regimes at B2, with predictions frozen now: `identity` (memoryless-realizable; holdout
organization absent), `delay1` (present), `delay2` — output the symbol two steps back, `0`
before that (present; 4 residual classes), and `delay3` — three steps back (**predicted
`NOT_RECOVERED_AT_SCOPE` on both routes**, because 8 residual classes exceed 4 states). The
fourth regime exercises the honest failure terminal (row `AJ15_R3`) on a live run rather than
only in a hostile. A found solver is confirmed exact for **all** words by an independent
product-state check against the specification's reference transducer.

**Decision rule (row R5).** `REPEATED_AT_B2` iff both implementations return the same terminal
per regime (`RECOVERED` for `identity`/`delay1`/`delay2`, `NOT_RECOVERED_AT_SCOPE` for
`delay3`), every returned solver passes the all-words product check, and the reachable-state
dependence outcome per regime matches the prediction. `INDEPENDENT_TEAM_REPLICATION` is not
claimed: the two implementations are independent code within one programme, and the row is
closed at that scope and no wider.

### 2.5 The UNKNOWN channel (row `AJ15_R6`)

Exact solvers in memoryless-realizable regimes match no registered fingerprint. They enter
`UNKNOWN` with `registered_family: null`, capability and raw resources frozen before taxonomy;
strongest-parent review then runs (expected: reduction to a literal one-symbol Boolean map or
constant — `PARENT_REDUCED_KNOWN`). The same run therefore produces both registered-fingerprint
recovery and non-registered outputs. A `NOVEL_AT_REGISTERED_SCOPE` outcome is not expected and,
if it appeared, would require independent replication before any novelty claim; none is made.

### 2.6 AJ13 and AJ14 applied at the end

After the run, the AJ13 six-conjunct stopping predicate is evaluated on the flagship's base
(assumption tags, no named mechanism in the base, AJ1 loss witnesses consumed by citation,
route-A/route-B presentation invariance, parent ownership, descent boundary) and the AJ14
badge ladder is recomputed from the run's evidence. Expected, recorded now: AJ13 `6/6`;
AJ14 badges 1–4 earned, badge 5 (`GMI_NOVEL_FORM_DISCOVERY_REPLICATED_AT_SCOPE`) **not**
earned because every `UNKNOWN` candidate is parent-reduced, badge 6 **not** earned because
the real-system gate (#903) is open. Because `gmi-833-aj11-bounded-completeness-v1`,
`gmi-833-aj13-stopping-rule-v1` and `gmi-833-aj14-establishment-criterion-v1` carry no
independent oracle, route B of this package re-derives their load-bearing numbers
(260/148/33,670/1,624, frontier `[M000,M001,M002,M043,M169]`, the atlas digest, `6/6`, the
four badges) from independently written code and pins them. `gmi-833-aj9g-k06-blind-recovery-v1`
has no `FREEZE_V1.md` (custody gap recorded by the holdout-source audit); nothing in this
package rests on aj9g, and it is cited only as one member of the AJ9 aggregate ceiling.

## 3. Named results this package may assert

`FX-1` bounded flagship (B1) — enumeration, regime outcomes, two-route agreement.
`FX-2` `UNKNOWN` channel live and parent-reduced; no novel form.
`FX-3` B2 repeat with two independent search implementations; honest failure terminal exercised.
`FX-4` falsifier live — hostile predictions and broken searches produce `FALSIFIED`/`RED`; nulls.
`FX-5` AJ13/AJ14 applied to the run; independent oracle for AJ11/AJ13/AJ14 receipts.
`FX-6` custody — registry read only after the blind outcome; blind-source audit `0` violations
with a validated scanner. No other identifier may appear in the receipt.

## 4. Two routes, hostiles, nulls

Route A `aj15_flagship_v1.py` and route B `independent_oracle_v1.py` share no code. Route A
represents machines as nested tuples and decides equivalence by product-state reachability;
route B represents machines as 8-character strings, decides equivalence by trace comparison on
all words of length ≤ 3 (exact for two 2-state machines: the product has 4 states), builds the
development graph by string edit distance, computes distances and the Pareto set by different
algorithms, and carries search `S2`. Both must agree on every B1 count, every B2 terminal and
the atlas digest.

**Hostiles.** Each carries an `applicable` flag that FAILS the run if the hostile cannot move
the quantity it perturbs.

| id | planted defect | quantity it must move |
|---|---|---|
| `H1` | family name planted into `SEARCH_CONFIG_V1.json` | source-audit violations `0 → ≥1` |
| `H2` | reachable-state clause dropped from the post-hoc fingerprint | `identity` pass count `0 → >0` |
| `H3` | prediction table inverted for `identity` | verdict `CONFIRMED → FALSIFIED` |
| `H4` | `S1` budget set to `1` | `delay2` terminal `RECOVERED → NOT_RECOVERED_AT_SCOPE` |
| `H5` | evaluation window truncated to words of length ≤ 1 | `delay1` exact-solver count `1 → >1`, route disagreement |
| `H6` | one atlas row perturbed | digest mismatch → `RED` |
| `H7` | `novel_replication` asserted `REPLICATED` with no replication receipt | badge 5 refused |
| `H8` | registry read before `BLIND_OUTCOME_V1.json` exists | custody `RED` |

**Nulls.** `N1`: the reachable-state-dependence test applied to 200 uniformly random B1
presentations (`random.Random(20260919)`, no low-bit reads) — the pass rate must lie strictly
between 0 and 1, so the `0/29` and `1/1` outcomes are properties of the regimes, not of a stuck
test. `N2`: exact — of the `C(5,2)=10` two-present/three-absent assignments of the five B1
regimes, exactly `1` matches the observed outcome vector (`1/10`); of the 8 assignments of the
three realizable B2 regimes exactly `1` matches (`1/8`); the frozen prediction is that one.
`N3`: 200 random B2 presentations under the `delay2` specification — the exact-solver rate
must be `0/200`, so a found solver is not a chance hit.

## 5. Failure is a falsifier (row `AJ15_R7`)

The registered claim under test is `SEEN_UNSEEN_REGIME_CONDITIONAL_RECOVERY_AT_SCOPE`: the
theory's regime predictions govern which organization appears. Any of the following is a direct
falsifier and forces the executor to emit `verdict: FALSIFIED` and exit non-zero: a
memoryless-realizable regime whose exact solvers include one with a reachable-state-dependent
output; a non-memoryless regime whose exact solvers include one without such dependence; a B2
`RECOVERED` terminal on one route with `NOT_RECOVERED_AT_SCOPE` on the other within budget;
or a post-hoc fingerprint outcome that contradicts the prediction table. `H3` demonstrates that
the falsifier is live. Nothing in this package may soften a falsification into a scope note.

## 6. Forbidden promotions

`NAMED_FAMILY_RECOVERED` (the historical family as such, beyond the frozen fingerprint at scope),
`FAMILY_IDENTITY_FROM_OPERATIONAL_EQUIVALENCE`, `PREDICTED_SELECTED`,
`PREDICTED_SELECTED_FOR_ALL_FAMILIES`, `REAL_SCALE_VALIDATION`, `INDEPENDENT_TEAM_REPLICATION`,
`M5`, `GMI_NOVEL_FORM_DISCOVERY_REPLICATED_AT_SCOPE`, `FULL_GMI_THEORY_SUPPORTED_AT_DECLARED_SCOPE`,
`NOVEL_MI_DISCOVERED`, `LITERAL_HISTORICAL_IGNORANCE_PROVED`, `FAMILY_INEVITABILITY`,
`ALL_MACHINE_INTELLIGENCES_COMPLETELY_CLASSIFIED`, `AJ16_EARNED`, `COMPLETE_GMI`.

## 7. What is not claimed

No family is recovered as an identity; a frozen fingerprint is satisfied at scope. Nothing here
is real-system evidence. B2 is searched, not enumerated, and its non-enumerated remainder is
not characterized. Task authorship, primitive basis, budgets and evaluators are disclosed
priors (the AJ9h bias ledger applies unchanged). Automata equivalence, right-congruence
construction, hill-climbing and Pareto mathematics are parent-owned; the residual contribution
of this tranche is the single end-to-end execution of the AJ chain's flagship protocol with
its predictions frozen, its failure terminal live, and its custody auditable.
